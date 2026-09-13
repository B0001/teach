"""teach-b5k.1: the ring and field half of the Judson graph.

Two things are under test here, and the second is easy to lose sight of:
that the new nodes say what Judson says, and that adding them did not quietly
change anything that already worked. The 20-node graph measurably degrades
`teach.concept_recovery` (filed as teach-ngy), so the default loader still
returns the group-theory chain and that contract is asserted, not assumed.
"""
import hashlib

import pytest

from teach.judson_algebra_graph import (
    RING_FIELD_NON_EDGES,
    TARGET_NODE_ID,
    load_judson_algebra_graph,
    load_judson_full_graph,
    load_judson_ring_field_data,
    prerequisite_closure,
)
from teach.pretext_parser import DEFINITION_KIND, JUDSON_SRC, iter_blocks

needs_judson = pytest.mark.skipif(
    not JUDSON_SRC.is_dir(), reason=f"pinned Judson source not cached at {JUDSON_SRC}"
)

RING_FIELD_IDS = (
    "judson:16.1-rings",
    "judson:16.2-integral-domains-and-fields",
    "judson:16.3-ring-homomorphisms-and-ideals",
    "judson:16.4-maximal-and-prime-ideals",
    "judson:17.1-polynomial-rings",
    "judson:18.1-fields-of-fractions",
    "judson:18.2-factorization-in-integral-domains",
    "judson:21.1-extension-fields",
    "judson:21.2-splitting-fields",
)


@pytest.fixture(scope="module")
def full():
    return load_judson_full_graph()


def test_full_graph_is_a_valid_dag_of_twenty_nodes(full):
    full.validate()
    order = full.topological_order()
    assert len(order) == 20
    assert len(full.edges) == 23
    for e in full.edges:
        assert order.index(e.src) < order.index(e.dst)


def test_all_nine_ring_and_field_nodes_are_present(full):
    ids = {n.id for n in full.nodes}
    for node_id in RING_FIELD_IDS:
        assert node_id in ids


def test_default_loader_is_still_the_group_theory_chain():
    """Contract preservation. Making the 20-node graph the default broke three
    tests including the epic's acceptance case -- see teach-ngy. The default
    stays group-only until that is understood, and this is the tripwire."""
    graph = load_judson_algebra_graph()
    assert len(graph.nodes) == 11
    assert len(graph.edges) == 11
    assert not {n.id for n in graph.nodes} & set(RING_FIELD_IDS)


def test_ring_and_field_nodes_stay_out_of_the_targets_prerequisite_closure(full):
    """Lagrange's Theorem must not acquire ring theory as a prerequisite just
    because the book contains it. This is the property that makes adding the
    ring/field half safe for the acceptance test's planning side."""
    assert prerequisite_closure(full, TARGET_NODE_ID) == prerequisite_closure(
        load_judson_algebra_graph(), TARGET_NODE_ID
    )


@pytest.mark.parametrize(
    "node_id,needle",
    [
        ("judson:16.1-rings", "is a ring if it has two closed binary operations"),
        ("judson:16.2-integral-domains-and-fields", "no zero divisors"),
        ("judson:16.3-ring-homomorphisms-and-ideals", "ring homomorphism is a map"),
        ("judson:16.4-maximal-and-prime-ideals", "is a maximal ideal"),
        ("judson:17.1-polynomial-rings", "is called a polynomial over"),
        ("judson:18.1-fields-of-fractions", "field of fractions"),
        ("judson:18.2-factorization-in-integral-domains", "is said to be irreducible"),
        ("judson:21.1-extension-fields", "is an extension field of a field"),
        ("judson:21.2-splitting-fields", "is a splitting field of"),
    ],
)
def test_each_ring_field_node_defines_its_own_subject(full, node_id, needle):
    by_id = {n.id: n for n in full.nodes}
    assert needle in by_id[node_id].facts["definition"], node_id


def test_ring_theory_attaches_to_group_theory_on_binary_operation(full):
    """Judson's ring definition opens "A nonempty set R is a ring if it has two
    closed binary operations" -- and "binary operation" is defined in the
    Groups chapter. The edge rests on that term, NOT on Judson's later remark
    that the first four axioms make a ring an abelian group under addition:
    that is an observation about the definition, which lists the four axioms
    outright and needs no group to state them."""
    by_id = {n.id: n for n in full.nodes}
    asserted = {(e.src, e.dst) for e in full.edges}
    assert ("judson:3.2-definitions-and-examples", "judson:16.1-rings") in asserted
    assert "binary operation" in by_id["judson:3.2-definitions-and-examples"].facts["key_terms"]
    assert "two closed binary operations" in by_id["judson:16.1-rings"].facts["definition"]


def test_ring_homomorphisms_do_not_depend_on_group_homomorphisms(full):
    """The edge the prose most invites and the text does not support. Judson
    opens with "In the study of groups, a homomorphism is a map that preserves
    the operation of the group. Similarly..." -- an analogy for the reader.
    The definition that follows is self-contained."""
    asserted = {(e.src, e.dst) for e in full.edges}
    assert ("judson:11.1-group-homomorphisms",
            "judson:16.3-ring-homomorphisms-and-ideals") not in asserted


def test_refused_ring_field_edges_stay_refused(full):
    asserted = {(e.src, e.dst) for e in full.edges}
    assert RING_FIELD_NON_EDGES
    for src, dst, why in RING_FIELD_NON_EDGES:
        assert (src, dst) not in asserted, f"{src} -> {dst}"
        assert why.strip(), f"{src} -> {dst} refused with no stated ground"


def test_extract_records_gfdl_and_does_not_claim_levins_license():
    """Judson is GFDL 1.3+ and Levin is CC BY-SA 4.0. Two different copyleft
    licenses that do not merge -- teach-j4n.1 emits per-node terms."""
    source = load_judson_ring_field_data()["source"]
    assert source["license"] == "https://www.gnu.org/licenses/fdl-1.3.html"
    assert source["commit"] == "3069910e3ded72ff5e18837a97a0e810c92790e2"
    assert "creativecommons" not in source["license"]


@needs_judson
def test_extract_still_matches_the_live_pinned_source():
    """Drift guard, same as the Levin half: every block the extract claims to
    have taken must still be there, in a file that still hashes the same."""
    cache: dict[str, list] = {}
    for n in load_judson_ring_field_data()["nodes"]:
        for p in n["provenance"]:
            fname = p["source_file"]
            if fname not in cache:
                cache[fname] = list(iter_blocks(JUDSON_SRC / fname))
                digest = hashlib.sha256((JUDSON_SRC / fname).read_bytes()).hexdigest()
                assert digest == p["file_sha256"], f"{fname} changed on disk"
            match = [
                b for b in cache[fname]
                if b.kind == DEFINITION_KIND
                and b.xml_id == p["xml_id"]
                and b.section_title == p["section_title"]
            ]
            assert match, f"{n['id']}: no live block for {p}"
            assert any(b.text in n["definition"] for b in match), (
                f"{n['id']}: live text in {fname} is no longer a substring of "
                "the extracted definition"
            )


@needs_judson
def test_sage_sections_are_never_harvested():
    """Every Judson chapter ends with a Sage section: executable code, not
    exposition. No node may draw text from one."""
    for n in load_judson_ring_field_data()["nodes"]:
        for p in n["provenance"]:
            assert p["section_title"] != "Sage", n["id"]
