"""teach-5aj: the VA Writing SOL K-12 prerequisite DAG actually loads, is a
true DAG, has no dangling edges, and its edges match the grade-chain rule
the module documents -- same structural discipline
test_va_reading_sol_graph.py applies to the reading graph.
"""
import pytest

from teach.concept_graph import GraphError, PrerequisiteEdge
from teach.va_writing_sol_graph import load_va_writing_sol_data, load_va_writing_sol_graph

GRADES = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]


def test_covers_every_k12_grade_with_no_gaps():
    graph = load_va_writing_sol_graph()
    seen = {(n.facts["strand_code"], n.facts["grade"]) for n in graph.nodes}
    expected = {("W", g) for g in GRADES}
    assert seen == expected


def test_is_a_true_dag_no_cycles():
    graph = load_va_writing_sol_graph()
    graph.validate()  # raises GraphError on a cycle; must not raise here
    graph.topological_order()


def test_every_edge_references_a_node_that_exists():
    graph = load_va_writing_sol_graph()
    node_ids = {n.id for n in graph.nodes}
    assert graph.edges, "expected at least one prerequisite edge"
    for edge in graph.edges:
        assert edge.src in node_ids, f"dangling edge src: {edge.src!r}"
        assert edge.dst in node_ids, f"dangling edge dst: {edge.dst!r}"


def test_edges_are_exactly_the_documented_grade_chain():
    """12 edges: 1 strand x 12 consecutive-grade gaps (K-1, 1-2, ..., 11-12).
    Not fewer (a broken chain), not more (a stray cross-grade edge the
    loader shouldn't be producing)."""
    graph = load_va_writing_sol_graph()
    actual = {(e.src, e.dst) for e in graph.edges}
    expected = {
        (f"va-writing-sol:{earlier}.W", f"va-writing-sol:{later}.W")
        for earlier, later in zip(GRADES, GRADES[1:])
    }
    assert actual == expected
    assert all(e.type == "precedes" for e in graph.edges)


def test_topological_order_respects_grade_sequence():
    graph = load_va_writing_sol_graph()
    order = graph.topological_order()
    ids = [f"va-writing-sol:{g}.W" for g in GRADES]
    positions = [order.index(i) for i in ids]
    assert positions == sorted(positions)


def test_node_standard_ref_and_label_match_source_for_a_known_code():
    graph = load_va_writing_sol_graph()
    node = graph.by_id("va-writing-sol:7.W")
    assert node.domain == "writing"
    assert node.standard_ref == "7.W"
    assert node.facts["strand_name"] == "Writing"
    assert node.facts["grade"] == "7"


def test_leaf_standards_carry_real_sourced_text_not_placeholders():
    graph = load_va_writing_sol_graph()
    k_w = graph.by_id("va-writing-sol:K.W")
    leaf_codes = [code for code, _ in k_w.facts["leaf_standards"]]
    assert "K.W.1.A" in leaf_codes
    descriptions = dict(k_w.facts["leaf_standards"])
    assert "drawing" in descriptions["K.W.1.A"].lower()


def test_grade_progression_is_a_real_content_escalation_not_just_labels():
    """The K->12 chain isn't just thirteen grade numbers in order -- the
    actual standard text should escalate in what it asks of a student.
    Guards against the loader chaining groupings whose *text* doesn't
    actually build on each other (e.g. a data error that shuffled labels)."""
    graph = load_va_writing_sol_graph()
    k_w = graph.by_id("va-writing-sol:K.W")
    twelfth_w = graph.by_id("va-writing-sol:12.W")
    k_text = " ".join(desc for _, desc in k_w.facts["leaf_standards"]).lower()
    twelfth_text = " ".join(desc for _, desc in twelfth_w.facts["leaf_standards"]).lower()
    assert "guidance and support" in k_text
    assert "guidance and support" not in twelfth_text
    assert "postsecondary" in twelfth_text
    assert "postsecondary" not in k_text


def test_source_provenance_is_recorded_not_asserted_from_memory():
    data = load_va_writing_sol_data()
    source = data["source"]
    assert "learningcommons.org" in source["provider"]
    assert source["license"] == "https://creativecommons.org/licenses/by/4.0/"
    assert "Virginia Department of Education" in source["author"]


def test_a_hand_introduced_cycle_is_rejected_not_silently_ordered():
    """Not a property of the shipped data (which is already tested acyclic
    above) -- a regression guard that this domain's loader output still goes
    through concept_graph's real cycle check, not a stub."""
    graph = load_va_writing_sol_graph()
    cyclic_edges = graph.edges + (
        PrerequisiteEdge(src="va-writing-sol:12.W", dst="va-writing-sol:K.W"),
    )
    cyclic_graph = graph.__class__(nodes=graph.nodes, edges=cyclic_edges)
    with pytest.raises(GraphError):
        cyclic_graph.topological_order()


def test_grade_12_duplicate_statement_code_is_a_documented_source_quirk():
    """Known upstream data anomaly (see module docstring): two distinct
    source nodes at grade 12 both carry statement_code "12.W.3.A" with
    different description text. leaf_standards is a tuple of (code, text)
    pairs specifically so both survive rather than one silently overwriting
    the other in a dict -- this test pins that behavior."""
    graph = load_va_writing_sol_graph()
    twelfth_w = graph.by_id("va-writing-sol:12.W")
    codes = [code for code, _ in twelfth_w.facts["leaf_standards"]]
    assert codes.count("12.W.3.A") == 2
