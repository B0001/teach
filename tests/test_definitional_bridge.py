"""teach-b5k.4: the definitional bridge and the unified graph.

The bridge exists because the LLM one (teach-b5k.2/.3) produced 127 proposals
and survived none of them. So the thing most worth testing is not that six
edges exist -- it is that the pun which would have produced eleven wrong ones
stays rejected, and that nothing here is reported as LLM-derived.
"""
import pytest

from teach.definitional_bridge import (
    BRIDGE_EDGES,
    EVIDENCE,
    REFUSED_BRIDGE_EDGES,
    TRANSITIVELY_REDUNDANT,
    bridge_edge_records,
    load_unified_graph,
)
from teach.semantic_bridge import redundant_against


@pytest.fixture(scope="module")
def graph():
    return load_unified_graph()


def test_unified_graph_is_a_valid_dag(graph):
    graph.validate()
    order = graph.topological_order()
    assert len(order) == 32
    assert len(graph.edges) == 40
    for e in graph.edges:
        assert order.index(e.src) < order.index(e.dst)


def test_the_two_halves_are_actually_joined(graph):
    """The property the LLM bridge failed to deliver at all: some algebraic
    node is reachable from a foundational one."""
    assert redundant_against(
        "levin-dmoi:sets", "judson:6.2-lagranges-theorem", graph.edges
    ), "Lagrange's Theorem is not reachable from the foundational layer"
    assert redundant_against(
        "levin-dmoi:functions", "judson:9.1-definition-and-examples", graph.edges
    )


def test_roots_are_the_four_the_texts_imply(graph):
    """Levin's two roots, plus Judson's own preliminaries -- which stay roots
    because Judson DEFINES sets, functions and the division algorithm himself
    rather than importing them."""
    has_incoming = {e.dst for e in graph.edges}
    roots = {n.id for n in graph.nodes if n.id not in has_incoming}
    assert roots == {
        "levin-dmoi:sets",
        "levin-dmoi:statements",
        "judson:1.2-sets-and-equivalence-relations",
        "judson:2.1-the-division-algorithm",
    }


def test_the_integral_domain_pun_stays_rejected(graph):
    """The trap a term match cannot see. Levin's `functions` node defines a
    function's DOMAIN; Judson's ring chapters say "integral domain", a
    commutative ring with no zero divisors. Same string, unrelated concepts.
    Taking the mechanical scan at face value would have wired function theory
    into four ring-theory nodes on a pun."""
    asserted = {(e.src, e.dst) for e in graph.edges}
    for dst in (
        "judson:16.1-rings",
        "judson:16.2-integral-domains-and-fields",
        "judson:18.1-fields-of-fractions",
    ):
        assert ("levin-dmoi:functions", dst) not in asserted
        assert ("levin-dmoi:function-properties", dst) not in asserted

    polysemy = [r for r in REFUSED_BRIDGE_EDGES if r[2].startswith("POLYSEMY")]
    assert len(polysemy) == 6


def test_judson_defines_its_own_preliminaries_so_does_not_import_them(graph):
    """Judson's ch.1 lists "function", "one-to-one" and "onto" in its OWN
    key_terms. Two books defining the same notion independently is not a
    dependency, however well the words match."""
    asserted = {(e.src, e.dst) for e in graph.edges}
    assert ("levin-dmoi:functions",
            "judson:1.2-sets-and-equivalence-relations") not in asserted
    assert ("levin-dmoi:function-properties",
            "judson:1.2-sets-and-equivalence-relations") not in asserted

    by_id = {n.id: n for n in graph.nodes}
    judson_prelim = by_id["judson:1.2-sets-and-equivalence-relations"]
    assert "function" in judson_prelim.facts["key_terms"]
    assert "one-to-one" in judson_prelim.facts["key_terms"]


def test_every_refused_edge_stays_refused_with_a_stated_ground(graph):
    asserted = {(e.src, e.dst) for e in graph.edges}
    assert len(REFUSED_BRIDGE_EDGES) == 11
    for src, dst, why in REFUSED_BRIDGE_EDGES:
        assert (src, dst) not in asserted, f"{src} -> {dst}"
        assert why.strip(), f"{src} -> {dst} refused with no ground"


def test_transitively_dropped_edges_really_are_redundant(graph):
    """"True but redundant" is a different fact from "rejected". If one of
    these is NOT reachable without its edge, dropping it removed a real
    dependency from the graph."""
    asserted = {(e.src, e.dst) for e in graph.edges}
    assert len(TRANSITIVELY_REDUNDANT) == 5
    for src, dst, _term in TRANSITIVELY_REDUNDANT:
        assert (src, dst) not in asserted
        assert redundant_against(src, dst, graph.edges), (
            f"{src} -> {dst} was dropped as transitive but dst is NOT "
            "reachable from src without it"
        )


def test_only_sets_and_function_nodes_bridge():
    """Nine of twelve foundational nodes have no bridge edge, and that is the
    honest answer rather than a gap. Judson's DEFINITIONS do not use
    propositional logic or proof technique -- a group is a set with an
    operation, stated without a quantifier symbol or a word about
    contradiction. Logic and proof method are how one WORKS with the
    definitions; this repo's edge rule is definitional on purpose."""
    sources = {src for src, _d, _t, _q in BRIDGE_EDGES}
    assert sources == {
        "levin-dmoi:sets", "levin-dmoi:functions", "levin-dmoi:function-properties"
    }
    for absent in ("levin-dmoi:propositional-logic", "levin-dmoi:direct-proof",
                   "levin-dmoi:mathematical-induction", "levin-dmoi:deduction-rules"):
        assert absent not in sources


def test_bridge_edges_are_labelled_definitional_not_llm_inferred():
    """These must never be reported as though a language model established
    them -- it proposed none of them, and the five it came closest on were
    refuted."""
    records = bridge_edge_records()
    assert len(records) == len(BRIDGE_EDGES) == 6
    for r in records:
        assert r["evidence"] == EVIDENCE == "definitional-rule-adjudicated"
        assert "llm" not in r["evidence"].lower()
        assert r["required_term"]
        assert r["quote"]


def test_each_bridge_edge_quotes_a_term_that_is_really_in_the_destination(graph):
    """The quote is the evidence. If the required term is not in the
    destination's own definition text, the edge rests on nothing."""
    by_id = {n.id: n for n in graph.nodes}
    for src, dst, term, _quote in BRIDGE_EDGES:
        text = str(by_id[dst].facts["definition"]).lower()
        needles = [t.strip().lower() for t in term.split("/")]
        assert any(n in text for n in needles), (
            f"{src} -> {dst}: required term {term!r} not present in dst's definition"
        )
