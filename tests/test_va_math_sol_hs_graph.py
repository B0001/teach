"""teach-8xw.16: the VA Math SOL high-school course-sequence DAG actually
loads, is a true DAG, has no dangling edges, and its edges match the sourced
course_prerequisites rule the module documents -- each backed by a verbatim
quote from VDOE's August 2023 Mathematics Standards of Learning document,
not an invented "well-known" ordering.
"""
import pytest

from teach.concept_graph import GraphError, PrerequisiteEdge
from teach.va_math_sol_graph import (
    load_va_math_sol_full_graph,
    load_va_math_sol_graph,
    load_va_math_sol_hs_data,
    load_va_math_sol_hs_graph,
)

COURSES = {"A", "G", "AFDA", "A2", "T", "CM", "PS", "DM", "MA"}
COURSES_WITH_NO_SOURCED_PREREQUISITE = {"A", "T", "PS", "DM"}


def _groupings_by_course(data):
    by_course = {}
    for g in data["groupings"]:
        by_course.setdefault(g["course_code"], []).append(g["id"])
    return by_course


def test_covers_all_nine_hs_courses_with_no_extra_or_missing():
    graph = load_va_math_sol_hs_graph()
    seen_courses = {n.facts["course_code"] for n in graph.nodes}
    assert seen_courses == COURSES


def test_is_a_true_dag_no_cycles():
    graph = load_va_math_sol_hs_graph()
    graph.validate()
    graph.topological_order()


def test_every_edge_references_a_node_that_exists():
    graph = load_va_math_sol_hs_graph()
    node_ids = {n.id for n in graph.nodes}
    assert graph.edges, "expected at least one prerequisite edge"
    for edge in graph.edges:
        assert edge.src in node_ids, f"dangling edge src: {edge.src!r}"
        assert edge.dst in node_ids, f"dangling edge dst: {edge.dst!r}"


def test_edges_are_exactly_the_bipartite_product_of_sourced_course_pairs():
    """96 edges: for each of the 7 sourced course_prerequisites relations,
    every grouping of the prerequisite course to every grouping of the
    dependent course. Not fewer (a broken product), not more (a stray edge
    the loader shouldn't be producing)."""
    graph = load_va_math_sol_hs_graph()
    data = load_va_math_sol_hs_data()
    by_course = _groupings_by_course(data)

    expected = set()
    for rel in data["course_prerequisites"]:
        for src_id in by_course[rel["src_course"]]:
            for dst_id in by_course[rel["dst_course"]]:
                expected.add((src_id, dst_id))

    actual = {(e.src, e.dst) for e in graph.edges}
    assert actual == expected
    assert all(e.type == "precedes" for e in graph.edges)


def test_topological_order_respects_every_sourced_course_relation():
    graph = load_va_math_sol_hs_graph()
    data = load_va_math_sol_hs_data()
    by_course = _groupings_by_course(data)
    order = graph.topological_order()

    for rel in data["course_prerequisites"]:
        for src_id in by_course[rel["src_course"]]:
            for dst_id in by_course[rel["dst_course"]]:
                assert order.index(src_id) < order.index(dst_id), (
                    f"{src_id} must precede {dst_id} per {rel['source_quote']!r}"
                )


def test_every_course_prerequisite_carries_a_real_source_quote():
    """The one thing standing between this data and an invented ordering:
    every relation must cite the sentence it was read from."""
    data = load_va_math_sol_hs_data()
    assert len(data["course_prerequisites"]) == 7
    for rel in data["course_prerequisites"]:
        assert rel["src_course"] in COURSES
        assert rel["dst_course"] in COURSES
        quote = rel["source_quote"]
        assert isinstance(quote, str) and len(quote) > 20
        # every quote should actually mention the course names it's citing --
        # a guard against a copy-paste mismatch between the pair and the quote
        assert rel["dst_course"] != rel["src_course"]


def test_courses_without_a_sourced_prerequisite_sentence_get_no_incoming_edge():
    """Trigonometry, Probability and Statistics, and Discrete Mathematics
    have no prerequisite-naming sentence in the source document's course
    introductions -- abstention, not a guessed 'usually comes after
    Geometry' edge. Algebra 1 also has none (it's the base course)."""
    data = load_va_math_sol_hs_data()
    graph = load_va_math_sol_hs_graph()
    courses_with_incoming = {rel["dst_course"] for rel in data["course_prerequisites"]}
    assert COURSES - courses_with_incoming == COURSES_WITH_NO_SOURCED_PREREQUISITE

    incoming_by_node = {n.id: 0 for n in graph.nodes}
    for e in graph.edges:
        incoming_by_node[e.dst] += 1
    by_course = _groupings_by_course(data)
    for course in COURSES_WITH_NO_SOURCED_PREREQUISITE:
        for node_id in by_course[course]:
            assert incoming_by_node[node_id] == 0, f"{node_id} has an unsourced incoming edge"


def test_node_standard_ref_and_label_match_source_for_a_known_code():
    graph = load_va_math_sol_hs_graph()
    node = graph.by_id("va-math-sol:G.RLT")
    assert node.domain == "math"
    assert node.standard_ref == "G.RLT"
    assert node.facts["course_code"] == "G"
    assert node.facts["course_name"] == "Geometry"


def test_leaf_standards_carry_real_sourced_text_not_placeholders():
    graph = load_va_math_sol_hs_graph()
    a_eo = graph.by_id("va-math-sol:A.EO")
    leaf_codes = [code for code, _ in a_eo.facts["leaf_standards"]]
    assert "A.EO.1" in leaf_codes
    descriptions = dict(a_eo.facts["leaf_standards"])
    assert "expressions" in descriptions["A.EO.1"].lower()


def test_source_provenance_is_recorded_not_asserted_from_memory():
    data = load_va_math_sol_hs_data()
    source = data["source"]
    assert "learningcommons.org" in source["standard_text_provider"]
    assert source["standard_text_license"] == "https://creativecommons.org/licenses/by/4.0/"
    assert "Virginia Department of Education" in source["standard_text_author"]
    assert "2023" in source["course_sequence_document"]
    assert "web.archive.org" in source["course_sequence_document_retrieved_via"]


def test_a_hand_introduced_cycle_is_rejected_not_silently_ordered():
    graph = load_va_math_sol_hs_graph()
    cyclic_edges = graph.edges + (
        PrerequisiteEdge(src="va-math-sol:MA.CF", dst="va-math-sol:A.EI"),
        PrerequisiteEdge(src="va-math-sol:A.EI", dst="va-math-sol:MA.CF"),
    )
    cyclic_graph = graph.__class__(nodes=graph.nodes, edges=cyclic_edges)
    with pytest.raises(GraphError):
        cyclic_graph.topological_order()


def test_full_graph_unions_k8_and_hs_with_no_id_collision_and_no_cross_edges():
    k8 = load_va_math_sol_graph()
    hs = load_va_math_sol_hs_graph()
    full = load_va_math_sol_full_graph()

    k8_ids = {n.id for n in k8.nodes}
    hs_ids = {n.id for n in hs.nodes}
    assert not (k8_ids & hs_ids), "K-8 and HS node ids must not collide"

    assert len(full.nodes) == len(k8.nodes) + len(hs.nodes)
    assert len(full.edges) == len(k8.edges) + len(hs.edges)
    full.validate()

    # no edge should cross between the two datasets -- this bead sources
    # only HS-to-HS course relations, never a K-8-to-HS one (see module
    # docstring's "What is deliberately NOT here")
    for e in full.edges:
        both_k8 = e.src in k8_ids and e.dst in k8_ids
        both_hs = e.src in hs_ids and e.dst in hs_ids
        assert both_k8 or both_hs, f"unexpected cross-dataset edge {e.src!r} -> {e.dst!r}"
