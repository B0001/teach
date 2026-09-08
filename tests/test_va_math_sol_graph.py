"""teach-8xw.5: the VA Math SOL K-8 prerequisite DAG actually loads, is a
true DAG, has no dangling edges, and its edges match the grade-chain-within-
strand rule the module documents -- not some other order it silently drifted
into.
"""
import pytest

from teach.concept_graph import GraphError, PrerequisiteEdge
from teach.va_math_sol_graph import load_va_math_sol_data, load_va_math_sol_graph

GRADES = ["K", "1", "2", "3", "4", "5", "6", "7", "8"]
STRANDS = ["NS", "CE", "MG", "PFA", "PS"]


def test_covers_every_strand_at_every_k8_grade_with_no_gaps():
    graph = load_va_math_sol_graph()
    seen = {(n.facts["strand_code"], n.facts["grade"]) for n in graph.nodes}
    expected = {(s, g) for s in STRANDS for g in GRADES}
    assert seen == expected


def test_is_a_true_dag_no_cycles():
    graph = load_va_math_sol_graph()
    graph.validate()  # raises GraphError on a cycle; must not raise here
    graph.topological_order()


def test_every_edge_references_a_node_that_exists():
    graph = load_va_math_sol_graph()
    node_ids = {n.id for n in graph.nodes}
    assert graph.edges, "expected at least one prerequisite edge"
    for edge in graph.edges:
        assert edge.src in node_ids, f"dangling edge src: {edge.src!r}"
        assert edge.dst in node_ids, f"dangling edge dst: {edge.dst!r}"


def test_edges_are_exactly_the_documented_grade_chain_per_strand():
    """40 edges: 5 strands x 8 consecutive-grade gaps (K-1, 1-2, ..., 7-8).
    Not fewer (a broken chain), not more (a stray cross-strand or
    cross-grade edge the loader shouldn't be producing)."""
    graph = load_va_math_sol_graph()
    actual = {(e.src, e.dst) for e in graph.edges}
    expected = set()
    for strand in STRANDS:
        for earlier, later in zip(GRADES, GRADES[1:]):
            expected.add((f"va-math-sol:{earlier}.{strand}", f"va-math-sol:{later}.{strand}"))
    assert actual == expected
    assert all(e.type == "precedes" for e in graph.edges)


def test_topological_order_respects_grade_sequence_within_every_strand():
    graph = load_va_math_sol_graph()
    order = graph.topological_order()
    for strand in STRANDS:
        ids = [f"va-math-sol:{g}.{strand}" for g in GRADES]
        positions = [order.index(i) for i in ids]
        assert positions == sorted(positions), f"strand {strand} out of grade order"


def test_node_standard_ref_and_label_match_source_for_a_known_code():
    graph = load_va_math_sol_graph()
    node = graph.by_id("va-math-sol:2.NS")
    assert node.domain == "math"
    assert node.standard_ref == "2.NS"
    assert node.facts["strand_name"] == "Number and Number Sense"
    assert node.facts["grade"] == "2"


def test_leaf_standards_carry_real_sourced_text_not_placeholders():
    graph = load_va_math_sol_graph()
    k_ns = graph.by_id("va-math-sol:K.NS")
    leaf_codes = [code for code, _ in k_ns.facts["leaf_standards"]]
    assert "K.NS.1" in leaf_codes
    descriptions = dict(k_ns.facts["leaf_standards"])
    assert "counting" in descriptions["K.NS.1"].lower()
    assert "100" in descriptions["K.NS.1"]


def test_grade_progression_is_a_real_content_escalation_not_just_labels():
    """The K->8 chain within NS isn't just five grade numbers in order --
    the actual standard text should escalate in what it asks of a student.
    Guards against the loader chaining groupings whose *text* doesn't
    actually build on each other (e.g. a data error that shuffled labels)."""
    graph = load_va_math_sol_graph()
    k_ns = graph.by_id("va-math-sol:K.NS")
    eighth_ns = graph.by_id("va-math-sol:8.NS")
    k_text = " ".join(desc for _, desc in k_ns.facts["leaf_standards"]).lower()
    eighth_text = " ".join(desc for _, desc in eighth_ns.facts["leaf_standards"]).lower()
    assert "100" in k_text or "30" in k_text
    assert "real number" in eighth_text


def test_source_provenance_is_recorded_not_asserted_from_memory():
    data = load_va_math_sol_data()
    source = data["source"]
    assert "learningcommons.org" in source["provider"]
    assert source["license"] == "https://creativecommons.org/licenses/by/4.0/"
    assert "Virginia Department of Education" in source["author"]


def test_a_hand_introduced_cycle_is_rejected_not_silently_ordered():
    """Not a property of the shipped data (which is already tested acyclic
    above) -- a regression guard that this domain's loader output still goes
    through concept_graph's real cycle check, not a stub."""
    graph = load_va_math_sol_graph()
    cyclic_edges = graph.edges + (
        PrerequisiteEdge(src="va-math-sol:8.NS", dst="va-math-sol:K.NS"),
    )
    cyclic_graph = graph.__class__(nodes=graph.nodes, edges=cyclic_edges)
    with pytest.raises(GraphError):
        cyclic_graph.topological_order()
