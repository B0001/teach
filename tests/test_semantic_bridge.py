"""teach-b5k.2: LLM-proposed bridge candidates between the two halves.

These tests are mostly about honesty plumbing rather than mathematics, and
that is the point. The failure this bead is exposed to is not "the model got a
pair wrong" -- it will -- it is a guessed relation reaching a traversal while
looking like an established one. So what is asserted here is that every record
is marked unverified, that the file keeps its banner, that no helper exists to
turn candidates into edges before the checker has run, and that the base rate
looks like something a model reading definitions would produce rather than one
agreeing with its prompt.
"""
import pytest

from teach.semantic_bridge import (
    RELATIONS,
    load_bridge_candidates,
    load_bridge_data,
    redundant_against,
    relation_counts,
)


@pytest.fixture(scope="module")
def data():
    return load_bridge_data()


def test_file_keeps_its_unverified_banner(data):
    assert data["status"].startswith("UNVERIFIED")
    assert "teach-b5k.3" in data["status"], (
        "the banner must keep naming the checker that has to pass on these"
    )


def test_producer_provenance_is_recorded(data):
    p = data["producer"]
    assert p["model"]
    assert p["temperature"] == 0
    assert p["endpoint"].startswith("http://localhost:11434")
    assert len(p["prompt_template_sha256"]) == 64


def test_every_record_is_marked_unverified_and_traceable():
    for r in load_bridge_candidates(include_none=True):
        assert r["status"] == "unverified"
        assert r["relation"] in RELATIONS + ("ERROR",)
        assert len(r["prompt_sha256"]) == 64
        assert r["src"].startswith("levin-dmoi:")
        assert r["dst"].startswith("judson:")


def test_the_whole_pair_space_was_asked_not_a_shortlist(data):
    """Pre-selecting plausible pairs would decide the interesting part of the
    answer -- which pairs relate at all -- by intuition, then have the model
    confirm it."""
    space = data["pair_space"]
    assert space["pairs_asked"] == space["foundation_nodes"] * space["algebra_nodes"]
    assert len(load_bridge_candidates(include_none=True)) == space["pairs_asked"]


def test_no_helper_converts_candidates_into_edges():
    """The conversion belongs after the checker. If someone adds it here, a
    caller can traverse a graph containing edges a language model guessed."""
    import teach.semantic_bridge as mod

    exported = [n for n in dir(mod) if not n.startswith("_")]
    for name in exported:
        assert "edge" not in name.lower() or name == "redundant_against", name


def test_transport_errors_are_rare_and_recorded_as_errors():
    """A failed call must stay distinguishable from a real judgement. A
    silently-defaulted "none" would be indistinguishable from the model
    actually deciding the pair is unrelated."""
    counts = relation_counts()
    total = sum(counts.values())
    assert counts.get("ERROR", 0) * 10 < total, f"too many transport errors: {counts}"


def test_the_producer_is_measurably_degenerate():
    """This pins a MEASUREMENT, not a target.

    The first version of this test asserted that "none" would be the most
    common answer, on the reasoning that an unfiltered pair space is mostly
    unrelated pairs. That is a reasonable expectation about the mathematics
    and it turned out to be false about the model, so the assertion was
    wrong to make: it encoded what I wanted the producer to do rather than
    what it does. Measured over all 240 pairs (llama3:latest, temperature 0):

        generalizes 125, none 112, is-prerequisite-for 2, ERROR 1

    "generalizes" is the plurality answer on a pair space where most pairs
    are genuinely unrelated, and only 2 of 240 use the one relation this
    repo's edge rule can actually test. Both of those two are wrong on their
    face, and their "reason" fields are the prompt's own rubric text copied
    back -- the model is echoing the question rather than reading the
    definitions.

    So this asserts the shape of that finding. If a re-run changes it, the
    change is worth looking at rather than silently absorbing -- exact counts
    are not pinned because the producer is not deterministic in practice even
    at temperature 0.
    """
    counts = relation_counts()
    assert counts.get("generalizes", 0) > counts.get("none", 0), (
        f"producer no longer over-reports 'generalizes' -- re-measure: {counts}"
    )
    assert counts.get("is-prerequisite-for", 0) < 10, (
        f"producer now proposes real prerequisite claims -- re-measure: {counts}"
    )


def test_redundant_against_is_plain_reachability():
    from teach.concept_graph import PrerequisiteEdge

    edges = (
        PrerequisiteEdge(src="a", dst="b"),
        PrerequisiteEdge(src="b", dst="c"),
        PrerequisiteEdge(src="x", dst="y"),
    )
    assert redundant_against("a", "c", edges)
    assert redundant_against("a", "b", edges)
    assert not redundant_against("c", "a", edges)
    assert not redundant_against("a", "y", edges)
    assert not redundant_against("nonexistent", "a", edges)
