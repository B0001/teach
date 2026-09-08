"""Enforce the domain-agnostic schema and traversal decided in teach-8xw.4.

The bead's risk: math-specific assumptions leaking into what should be a
domain-agnostic core. These tests are the check that the core actually is
domain-agnostic (one graph, two unrelated domains, no branching) and that
invalid graphs fail loudly rather than producing a silently wrong order.
"""
import pytest

from teach.concept_graph import ConceptGraph, ConceptNode, GraphError, PrerequisiteEdge


def _node(node_id: str, domain: str) -> ConceptNode:
    return ConceptNode(id=node_id, domain=domain, label=node_id)


def test_topological_order_respects_a_single_domains_edges():
    graph = ConceptGraph(
        nodes=(_node("a", "math"), _node("b", "math"), _node("c", "math")),
        edges=(
            PrerequisiteEdge(src="a", dst="b"),
            PrerequisiteEdge(src="b", dst="c"),
        ),
    )
    order = graph.topological_order()
    assert order.index("a") < order.index("b") < order.index("c")


def test_one_graph_traverses_two_unrelated_domains_without_special_casing():
    """The engine must not need to know 'math' from 'reading' to order
    either one correctly -- both are handled by the exact same call."""
    math_a, math_b = _node("math:a", "math"), _node("math:b", "math")
    reading_a, reading_b = _node("reading:a", "reading"), _node("reading:b", "reading")
    graph = ConceptGraph(
        nodes=(math_a, math_b, reading_a, reading_b),
        edges=(
            PrerequisiteEdge(src=math_a.id, dst=math_b.id),
            PrerequisiteEdge(src=reading_a.id, dst=reading_b.id),
        ),
    )
    order = graph.topological_order()
    assert order.index(math_a.id) < order.index(math_b.id)
    assert order.index(reading_a.id) < order.index(reading_b.id)


def test_facts_and_standard_ref_are_opaque_payload():
    """The engine must accept any per-domain facts shape without inspecting
    it -- a math fact payload and a reading fact payload look nothing alike
    and neither should mean anything special to ConceptNode itself."""
    math_node = ConceptNode(
        id="m", domain="math", label="Normal subgroups", standard_ref="D&F 3.1",
        facts={"theorem": "the kernel of a homomorphism is normal"},
    )
    reading_node = ConceptNode(
        id="r", domain="reading", label="Main idea", standard_ref="VA RDG 3.4",
        facts={"passage_id": "p12", "target_level": "grade 3"},
    )
    assert math_node.facts != reading_node.facts
    assert math_node.standard_ref != reading_node.standard_ref


def test_by_id_looks_up_a_node():
    a = _node("a", "math")
    graph = ConceptGraph(nodes=(a,), edges=())
    assert graph.by_id("a") is a
    with pytest.raises(KeyError):
        graph.by_id("missing")


def test_duplicate_node_id_is_rejected():
    graph = ConceptGraph(nodes=(_node("a", "math"), _node("a", "math")), edges=())
    with pytest.raises(GraphError):
        graph.validate()


def test_edge_to_unknown_node_is_rejected():
    graph = ConceptGraph(
        nodes=(_node("a", "math"),),
        edges=(PrerequisiteEdge(src="a", dst="does-not-exist"),),
    )
    with pytest.raises(GraphError):
        graph.validate()


def test_cycle_is_rejected_rather_than_silently_ordered():
    """A two-node cycle must raise, not return some arbitrary order --
    silently ordering an inconsistent prerequisite graph would tell a
    learner concept A requires B and B requires A with a straight face."""
    graph = ConceptGraph(
        nodes=(_node("a", "math"), _node("b", "math")),
        edges=(
            PrerequisiteEdge(src="a", dst="b"),
            PrerequisiteEdge(src="b", dst="a"),
        ),
    )
    with pytest.raises(GraphError):
        graph.topological_order()


def test_edge_type_defaults_to_precedes_but_is_an_open_string():
    default_edge = PrerequisiteEdge(src="a", dst="b")
    assert default_edge.type == "precedes"
    other_edge = PrerequisiteEdge(src="a", dst="b", type="isPartOf")
    assert other_edge.type == "isPartOf"


def test_diamond_shaped_prerequisites_produce_a_valid_order():
    """a -> b, a -> c, b -> d, c -> d: a valid DAG that isn't a simple
    chain, to prove topological_order handles branching, not just lines."""
    graph = ConceptGraph(
        nodes=(_node("a", "math"), _node("b", "math"), _node("c", "math"), _node("d", "math")),
        edges=(
            PrerequisiteEdge(src="a", dst="b"),
            PrerequisiteEdge(src="a", dst="c"),
            PrerequisiteEdge(src="b", dst="d"),
            PrerequisiteEdge(src="c", dst="d"),
        ),
    )
    order = graph.topological_order()
    assert order.index("a") < order.index("b")
    assert order.index("a") < order.index("c")
    assert order.index("b") < order.index("d")
    assert order.index("c") < order.index("d")
