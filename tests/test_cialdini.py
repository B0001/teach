"""Enforce the Cialdini/Pre-Suasion motivation layer defined in
teach/cialdini.py (teach-8xw.31).

Mirrors tests/test_cbt_primitives.py exactly, plus the one invariant that
distinguishes generation logic from a single hand-authored sentence per
principle: two requested variants of the same move must actually differ.
"""
import pytest

from teach.cialdini import (
    FAKE_CONTEXTS,
    MOVES,
    MotivationMoment,
    PrincipleName,
    is_on_topic,
    render_authority,
    render_commitment_consistency,
    render_liking,
    render_reciprocity,
    render_scarcity,
    render_social_proof,
    render_unity,
)


def test_exactly_the_seven_principles_the_epic_names():
    assert {m.name for m in MOVES} == set(PrincipleName)
    assert len(PrincipleName) == 7


def test_every_principle_has_a_nonempty_when_to_use():
    for move in MOVES:
        assert move.when_to_use.strip()


@pytest.mark.parametrize("move", MOVES, ids=lambda m: m.name.value)
def test_principle_renders_nonempty_on_topic_output_from_fake_context(move):
    moment = FAKE_CONTEXTS[move.name]
    output = move.render(moment, 0)
    assert output.strip()
    assert is_on_topic(output, moment.concept_name)


@pytest.mark.parametrize("move", MOVES, ids=lambda m: m.name.value)
def test_principle_variants_actually_differ(move):
    """Proof this is generation logic, not one hand-authored string per
    principle -- the exact gap this bead was filed to close."""
    moment = FAKE_CONTEXTS[move.name]
    variant_0 = move.render(moment, 0)
    variant_1 = move.render(moment, 1)
    assert variant_0 != variant_1
    assert is_on_topic(variant_1, moment.concept_name)


def test_reciprocity_states_the_gift_before_the_ask():
    moment = MotivationMoment(
        concept_name="cosets", given_first="a worked example", next_ask="try the next one"
    )
    output = render_reciprocity(moment, 0)
    assert "a worked example" in output
    assert "try the next one" in output
    assert output.index("a worked example") < output.index("try the next one")


def test_reciprocity_requires_both_fields():
    with pytest.raises(ValueError):
        render_reciprocity(MotivationMoment(concept_name="cosets", next_ask="x"))
    with pytest.raises(ValueError):
        render_reciprocity(MotivationMoment(concept_name="cosets", given_first="y"))


def test_commitment_consistency_surfaces_the_learners_own_words():
    moment = MotivationMoment(
        concept_name="cosets",
        prior_commitment="I want to understand this properly",
        consistent_next_step="working the harder example",
    )
    output = render_commitment_consistency(moment, 0)
    assert "I want to understand this properly" in output
    assert "working the harder example" in output


def test_commitment_consistency_requires_both_fields():
    with pytest.raises(ValueError):
        render_commitment_consistency(MotivationMoment(concept_name="cosets", prior_commitment="x"))
    with pytest.raises(ValueError):
        render_commitment_consistency(
            MotivationMoment(concept_name="cosets", consistent_next_step="y")
        )


def test_liking_requires_shared_frame():
    with pytest.raises(ValueError):
        render_liking(MotivationMoment(concept_name="cosets"))


def test_authority_cites_the_named_source_and_the_fact():
    moment = MotivationMoment(
        concept_name="cosets",
        cited_source="Dummit and Foote's Abstract Algebra",
        authority_fact="cosets partition the group",
    )
    output = render_authority(moment, 0)
    assert "Dummit and Foote's Abstract Algebra" in output
    assert "cosets partition the group" in output


def test_authority_requires_both_fields():
    with pytest.raises(ValueError):
        render_authority(MotivationMoment(concept_name="cosets", cited_source="x"))
    with pytest.raises(ValueError):
        render_authority(MotivationMoment(concept_name="cosets", authority_fact="y"))


def test_scarcity_requires_scarce_detail():
    with pytest.raises(ValueError):
        render_scarcity(MotivationMoment(concept_name="cosets"))


def test_unity_requires_shared_identity():
    with pytest.raises(ValueError):
        render_unity(MotivationMoment(concept_name="cosets"))


def test_social_proof_names_the_difficulty_not_an_outcome():
    """The deliberate honesty boundary this module's docstring states:
    social proof normalizes struggle, it never promises a future result."""
    moment = MotivationMoment(concept_name="cosets", peer_difficulty="mixing up left and right cosets")
    output = render_social_proof(moment, 0)
    assert "mixing up left and right cosets" in output
    assert "goes on to" not in output.lower()
    assert "everyone who" not in output.lower()


def test_social_proof_requires_peer_difficulty():
    with pytest.raises(ValueError):
        render_social_proof(MotivationMoment(concept_name="cosets"))
