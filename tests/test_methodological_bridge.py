"""teach-6xi: methodological prerequisites, derived from <proof> not <definition>.

The point of this bead is that two different claims were being forced through
one relation. So the tests that matter are the ones asserting they stay
separable, that the evidence rule really is "a proof names the method", and
that what could NOT be evidenced is reported rather than guessed.
"""
import pytest

from teach.definitional_bridge import load_unified_graph
from teach.methodological_bridge import (
    EDGE_TYPE,
    METHODOLOGICAL_EDGES,
    PROOFS_IN_MODELLED_SECTIONS,
    PROOF_METHOD_PATTERNS,
    REFUSED_METHODS,
    TOTAL_PROOFS,
    derive_from_source,
    edge_records,
    load_graph_with_methodological_edges,
)
from teach.pretext_parser import JUDSON_SRC

needs_judson = pytest.mark.skipif(
    not JUDSON_SRC.is_dir(), reason=f"pinned Judson source not cached at {JUDSON_SRC}"
)


@pytest.fixture(scope="module")
def graph():
    return load_graph_with_methodological_edges()


def test_graph_gains_eight_methodological_edges_and_stays_a_dag(graph):
    graph.validate()
    assert len(graph.nodes) == 32
    assert len(graph.edges) == 48
    typed = [e for e in graph.edges if e.type == EDGE_TYPE]
    assert len(typed) == 8
    order = graph.topological_order()
    for e in graph.edges:
        assert order.index(e.src) < order.index(e.dst)


def test_the_two_claims_never_collapse_into_one_edge(graph):
    """"dst's definition needs src" and "dst's proofs use src" are different
    assertions. If the same pair appeared under both types a consumer could
    not tell which was meant."""
    definitional = {(e.src, e.dst) for e in graph.edges if e.type == "precedes"}
    methodological = {(e.src, e.dst) for e in graph.edges if e.type == EDGE_TYPE}
    assert not (definitional & methodological)
    assert len(definitional) == 40 and len(methodological) == 8


def test_methodological_sources_are_exactly_the_nodes_the_definitional_rule_stranded(graph):
    """These nodes had no outgoing edge at all under the definitional rule --
    that is the gap this bead was filed for."""
    definitional_sources = {e.src for e in graph.edges if e.type == "precedes"}
    for src, _dst, _n, _q in METHODOLOGICAL_EDGES:
        assert src in PROOF_METHOD_PATTERNS
        assert src not in definitional_sources


def test_it_connects_a_node_the_definitional_bridge_left_stranded(graph):
    """judson:2.1-the-division-algorithm had no incoming edge of any kind: its
    definitions are self-contained, so nothing could reach it definitionally.
    Its proofs use contradiction and induction."""
    base_incoming = {e.dst for e in load_unified_graph().edges}
    assert "judson:2.1-the-division-algorithm" not in base_incoming

    incoming = {(e.src, e.type) for e in graph.edges
                if e.dst == "judson:2.1-the-division-algorithm"}
    assert ("levin-dmoi:proof-by-contradiction", EDGE_TYPE) in incoming
    assert ("levin-dmoi:mathematical-induction", EDGE_TYPE) in incoming


def test_every_edge_carries_proof_count_and_a_verbatim_excerpt():
    records = edge_records()
    assert len(records) == 8
    for r in records:
        assert r["relation"] == EDGE_TYPE
        assert r["evidence"] == "named-method-in-proof-body"
        assert r["proofs_matched"] >= 1
        assert len(r["quote"]) > 40


def test_direct_proof_gets_no_edge_and_the_reason_is_recorded():
    """Its signature is the ABSENCE of a named method. Inferring "this is a
    direct proof because it does not say otherwise" would manufacture an edge
    out of silence -- so it gets none, and the manifest says why."""
    refused = dict(REFUSED_METHODS)
    assert "levin-dmoi:direct-proof" in refused
    assert "silence" in refused["levin-dmoi:direct-proof"]
    sources = {src for src, _d, _n, _q in METHODOLOGICAL_EDGES}
    assert "levin-dmoi:direct-proof" not in sources


def test_quantifier_vocabulary_is_refused_as_a_method():
    """"for all" appears in 29 proofs and "there exists" in 49, but they are
    logical vocabulary, not inference operators. Counting them would repeat
    the word-matching error this bead exists to correct."""
    refused = dict(REFUSED_METHODS)
    assert "levin-dmoi:predicates-and-quantifiers" in refused
    assert "vocabulary" in refused["levin-dmoi:predicates-and-quantifiers"].lower()
    sources = {src for src, _d, _n, _q in METHODOLOGICAL_EDGES}
    assert "levin-dmoi:predicates-and-quantifiers" not in sources


def test_contrapositive_has_no_edge_because_of_coverage_not_absence():
    """Judson genuinely uses contrapositive -- twice, by name -- but both
    proofs are in sections this graph models no node for. Reporting that as
    "Judson does not use contrapositive" would be false."""
    refused = dict(REFUSED_METHODS)
    why = refused["levin-dmoi:proof-by-contrapositive"]
    assert "2 proofs" in why
    assert "coverage limit" in why


@needs_judson
def test_hardcoded_edges_still_match_a_fresh_scan_of_the_source():
    """Drift guard. The table is a derived artifact; if the book or the parser
    changes, the table must not quietly stop matching."""
    derived = derive_from_source()
    assert derived["total_proofs"] == TOTAL_PROOFS
    assert derived["proofs_in_modelled_sections"] == PROOFS_IN_MODELLED_SECTIONS

    hardcoded = {(src, dst): n for src, dst, n, _q in METHODOLOGICAL_EDGES}
    assert derived["edges"] == hardcoded, (
        f"scan and table disagree:\n  only in scan: "
        f"{set(derived['edges']) - set(hardcoded)}\n  only in table: "
        f"{set(hardcoded) - set(derived['edges'])}"
    )


@needs_judson
def test_coverage_is_partial_and_the_numbers_are_honest():
    """88 of 207 proofs are in modelled sections. These edges are a floor, not
    a census, and the manifest has to say so."""
    derived = derive_from_source()
    assert derived["proofs_in_modelled_sections"] < derived["total_proofs"]
    assert derived["proofs_in_modelled_sections"] == 88
    assert derived["total_proofs"] == 207


@needs_judson
def test_every_quoted_excerpt_really_appears_in_a_judson_proof():
    """The quote is the evidence. A quote that is not in the book is a
    fabricated citation."""
    import re

    from teach.pretext_parser import JUDSON_GLOB, iter_book

    proofs = " ".join(
        re.sub(r"\s+", " ", b.text)
        for b in iter_book(JUDSON_SRC, JUDSON_GLOB) if b.kind == "proof"
    )
    for _src, dst, _n, quote in METHODOLOGICAL_EDGES:
        needle = re.sub(r"\s+", " ", quote).strip()
        assert needle in proofs, f"{dst}: quoted excerpt not found in any proof"
