"""teach-ysm.1: the foundational logic nodes extracted from Levin DMOI 3rd ed.

The licensing tests are not ceremony. This text was chosen over the one the
plan named (Hammack, CC BY-NC-ND, PDF-only) specifically because the 3rd
edition is CC BY-SA 4.0 -- and the same repository's master branch is the 4th
edition under CC BY-NC-SA. Everything that makes this half of the graph
publishable is a property of one pinned commit, so it is asserted, not
assumed.
"""
import pytest

from teach.concept_graph import ConceptNode
from teach.levin_foundations_graph import (
    DOMAIN,
    LEVIN_SOURCE,
    load_levin_foundation_nodes,
    load_levin_foundations_data,
)
from teach.pretext_parser import LEVIN_SRC, iter_blocks

needs_levin = pytest.mark.skipif(
    not LEVIN_SRC.is_dir(), reason=f"pinned Levin source not cached at {LEVIN_SRC}"
)


@pytest.fixture(scope="module")
def nodes():
    return load_levin_foundation_nodes()


@pytest.fixture(scope="module")
def by_id(nodes):
    return {n.id: n for n in nodes}


def test_twelve_unique_foundational_nodes(nodes):
    assert len(nodes) == 12
    assert len({n.id for n in nodes}) == 12
    assert all(isinstance(n, ConceptNode) for n in nodes)
    assert all(n.domain == DOMAIN for n in nodes)
    assert all(n.id.startswith("levin-dmoi:") for n in nodes)
    assert all(n.standard_ref for n in nodes)


def test_source_is_the_by_sa_third_edition_commit_not_master():
    """The tripwire for the one mistake that would silently relicense this
    half of the graph: re-extracting from master, which is the 4th edition
    and carries a NonCommercial clause."""
    assert LEVIN_SOURCE["license"] == "https://creativecommons.org/licenses/by-sa/4.0/"
    assert LEVIN_SOURCE["commit"] == "a8e4949bc45daf100930c1182983778f56ab689f"
    assert LEVIN_SOURCE["git_tag"] == "3rd-ed"
    assert "NC" in LEVIN_SOURCE["license_note"]
    assert "by-nc" not in LEVIN_SOURCE["license"]


def test_every_node_carries_its_license_and_attribution(nodes):
    """Per-node, not per-dataset. Levin is CC BY-SA and Judson is GFDL 1.3+ --
    two different copyleft licenses that do not merge, so teach-j4n.1 has to
    emit each node's own terms."""
    for n in nodes:
        assert n.facts["license"] == "https://creativecommons.org/licenses/by-sa/4.0/"
        assert "Oscar Levin" in n.facts["attribution"]
        assert "ShareAlike" in n.facts["attribution"]


@pytest.mark.parametrize(
    "node_id,needles",
    [
        ("levin-dmoi:sets", ("set", "unordered collection")),
        ("levin-dmoi:set-operations", ("union", "intersection", "Cartesian product")),
        ("levin-dmoi:statements", ("statement", "atomic", "molecular")),
        ("levin-dmoi:predicates-and-quantifiers", ("predicate", "quantifier", "free variable")),
        ("levin-dmoi:propositional-logic", ("tautology", "logically equivalent", "truth table")),
        ("levin-dmoi:deduction-rules", ("deduction rule", "modus ponens", "valid")),
        ("levin-dmoi:functions", ("function", "domain", "codomain")),
        ("levin-dmoi:function-properties", ("injective", "surjective", "bijection")),
        ("levin-dmoi:direct-proof", ("direct proof",)),
        ("levin-dmoi:proof-by-contrapositive", ("contrapositive", "logically equivalent")),
        ("levin-dmoi:proof-by-contradiction", ("contradiction",)),
        ("levin-dmoi:mathematical-induction", ("base case", "inductive case")),
    ],
)
def test_each_node_actually_defines_what_it_is_named_for(by_id, node_id, needles):
    """A node whose text does not contain its own subject is this repo's
    characteristic failure: it reads fluently and teaches nothing."""
    text = by_id[node_id].facts["definition"]
    for needle in needles:
        assert needle in text, f"{node_id} is missing {needle!r}"


def test_deduction_rules_node_is_not_the_sherlock_holmes_puzzle(by_id):
    """Regression. Levin's "Deductions" subsection opens with an
    `<investigation>` posing a Holmes dress-code puzzle. Harvested naively,
    the node explaining what a deduction rule is began "Holmes owns two
    suits: one black and one tweed." Investigations are activities, not
    exposition, and the parser skips them."""
    text = by_id["levin-dmoi:deduction-rules"].facts["definition"]
    assert "Holmes" not in text
    assert "sandals" not in text
    assert "modus ponens" in text


def test_direct_proof_node_states_the_proof_skeleton(by_id):
    """Regression. Levin states the shape of a direct proof in a 57-character
    `<blockquote>` carrying no `<term>`. A "short prose is filler" rule
    deleted exactly that sentence, leaving the node ending on "The general
    format to prove P => Q is this:" and never saying what the format is."""
    text = by_id["levin-dmoi:direct-proof"].facts["definition"]
    assert "Assume $P$" in text
    assert "Therefore $Q$" in text


def test_every_node_is_traceable_to_pinned_source_blocks():
    for n in load_levin_foundations_data()["nodes"]:
        assert n["provenance"], f"{n['id']} has no provenance"
        for p in n["provenance"]:
            assert p["source_file"].endswith(".ptx")
            assert len(p["file_sha256"]) == 64
            assert p["kind"] in ("term-definition", "assemblage", "prose")


@needs_levin
def test_extract_still_matches_the_live_pinned_source():
    """Drift guard: the committed extract is a derived artifact, so every
    block it claims to have taken from the source must still be there, with
    text that is still a substring of the node it fed. Catches a hand-edited
    extract as readily as an upstream that moved."""
    import hashlib

    cache: dict[str, list] = {}
    for n in load_levin_foundations_data()["nodes"]:
        for p in n["provenance"]:
            fname = p["source_file"]
            if fname not in cache:
                cache[fname] = list(iter_blocks(LEVIN_SRC / fname, include_prose=True))
                digest = hashlib.sha256((LEVIN_SRC / fname).read_bytes()).hexdigest()
                assert digest == p["file_sha256"], f"{fname} changed on disk"
            match = [
                b for b in cache[fname]
                if b.kind == p["kind"]
                and b.xml_id == p["xml_id"]
                and b.subsection_title == p["subsection_title"]
            ]
            assert match, f"{n['id']}: no live block for {p}"
            assert any(b.text in n["definition"] for b in match), (
                f"{n['id']}: live text for {p['kind']} in {fname} is no longer "
                "a substring of the extracted definition"
            )


# --------------------------------------------------------------------------
# teach-ysm.2: the foundational layer as an ordered DAG.

from teach.concept_graph import GraphError  # noqa: E402
from teach.levin_foundations_graph import (  # noqa: E402
    REFUSED_EDGES,
    load_levin_foundations_graph,
)


@pytest.fixture(scope="module")
def graph():
    return load_levin_foundations_graph()


def test_graph_is_a_valid_dag_over_all_twelve_nodes(graph):
    graph.validate()
    order = graph.topological_order()
    assert len(order) == 12
    for e in graph.edges:
        assert order.index(e.src) < order.index(e.dst)


def test_sets_and_statements_are_the_only_roots(graph):
    """These are the roots of the WHOLE unified graph -- everything in
    teach.judson_algebra_graph is downstream of them -- so a third root
    appearing means something was left unordered, and a missing one means a
    cycle or a spurious dependency crept in."""
    has_incoming = {e.dst for e in graph.edges}
    roots = {n.id for n in graph.nodes if n.id not in has_incoming}
    assert roots == {"levin-dmoi:sets", "levin-dmoi:statements"}


def test_deduction_rules_is_not_a_root(graph):
    """Regression on an overruled refutation. A skeptic refused
    statements -> deduction-rules after counting occurrences of the word
    "statement" in the node (exactly one, in an aside), which would have made
    a rule of inference a root of the graph -- preceding the notion of a
    statement. The argument form that IS the definition is written in
    propositional variables joined by the conditional connective, both of
    which `statements` defines."""
    incoming = {e.src for e in graph.edges if e.dst == "levin-dmoi:deduction-rules"}
    assert "levin-dmoi:statements" in incoming


def test_contrapositive_depends_on_direct_proof(graph):
    """The other overruled refutation. Levin's statement of what the technique
    is reads "It gives a direct proof of the contrapositive of the
    implication" -- the definiens is src's only term."""
    incoming = {e.src for e in graph.edges if e.dst == "levin-dmoi:proof-by-contrapositive"}
    assert incoming == {"levin-dmoi:direct-proof", "levin-dmoi:propositional-logic"}


def test_refused_edges_stay_refused(graph):
    """An absent edge is invisible. Without this, a later worker cannot tell a
    dependency that was considered and rejected from one that was missed."""
    asserted = {(e.src, e.dst) for e in graph.edges}
    assert REFUSED_EDGES
    for src, dst, why in REFUSED_EDGES:
        assert (src, dst) not in asserted
        assert why.strip(), f"{src} -> {dst} refused with no stated ground"


def test_edges_only_connect_known_nodes(graph):
    ids = {n.id for n in graph.nodes}
    for e in graph.edges:
        assert e.src in ids and e.dst in ids
        assert e.type == "precedes"


def test_a_cycle_would_be_rejected_loudly(graph):
    """The engine's guarantee, exercised on this graph's real nodes: a bad
    edge set fails rather than producing an arbitrary order."""
    from teach.concept_graph import ConceptGraph, PrerequisiteEdge

    bad = ConceptGraph(
        nodes=graph.nodes,
        edges=graph.edges + (
            PrerequisiteEdge(src="levin-dmoi:function-properties", dst="levin-dmoi:sets"),
        ),
    )
    with pytest.raises(GraphError):
        bad.topological_order()
