"""Enforce the CBT primitive library defined in teach/cbt_primitives.py.

teach-8xw.7's acceptance criteria: a named, enumerable set of CBT-derived
pedagogical primitives with a one-line definition of when each applies,
plus a runnable check that each primitive, given a minimal fake lesson
context, produces non-empty, on-topic output. These tests are that check,
plus proof that each primitive actually requires the context it claims to
need rather than rendering plausible-looking filler from nothing.
"""
import pytest

from teach.cbt_primitives import (
    FAKE_CONTEXTS,
    MOVES,
    LessonMoment,
    PrimitiveName,
    is_on_topic,
    render_behavioral_activation,
    render_graded_exposure,
    render_identify_stuck_belief,
    render_spaced_retrieval,
)


def test_exactly_the_four_primitives_the_epic_names():
    assert {m.name for m in MOVES} == {
        PrimitiveName.IDENTIFY_STUCK_BELIEF,
        PrimitiveName.GRADED_EXPOSURE,
        PrimitiveName.BEHAVIORAL_ACTIVATION,
        PrimitiveName.SPACED_RETRIEVAL,
    }


def test_every_primitive_has_a_nonempty_when_to_use():
    for move in MOVES:
        assert move.when_to_use.strip()


@pytest.mark.parametrize("move", MOVES, ids=lambda m: m.name.value)
def test_primitive_renders_nonempty_on_topic_output_from_fake_context(move):
    moment = FAKE_CONTEXTS[move.name]
    output = move.render(moment)
    assert output.strip()
    assert is_on_topic(output, moment.concept_name)


def test_identify_stuck_belief_surfaces_the_actual_belief_text():
    """Not just on-topic -- the specific belief the learner voiced must
    show up in the output, or this is generic encouragement wearing the
    primitive's name."""
    moment = LessonMoment(concept_name="groups", learner_statement="I'm just bad at math")
    output = render_identify_stuck_belief(moment)
    assert "I'm just bad at math" in output


def test_identify_stuck_belief_requires_learner_statement():
    moment = LessonMoment(concept_name="groups")
    with pytest.raises(ValueError):
        render_identify_stuck_belief(moment)


def test_graded_exposure_references_both_easier_and_harder_problem():
    moment = LessonMoment(
        concept_name="groups",
        easier_problem="verify closure for a 3-element set",
        harder_problem="verify closure for a group given only its multiplication table",
    )
    output = render_graded_exposure(moment)
    assert "verify closure for a 3-element set" in output
    assert "verify closure for a group given only its multiplication table" in output


def test_graded_exposure_requires_both_problems():
    with pytest.raises(ValueError):
        render_graded_exposure(LessonMoment(concept_name="groups", easier_problem="x"))
    with pytest.raises(ValueError):
        render_graded_exposure(LessonMoment(concept_name="groups", harder_problem="y"))


def test_behavioral_activation_references_the_concrete_action():
    moment = LessonMoment(concept_name="groups", next_action="list the elements of Z/4Z")
    output = render_behavioral_activation(moment)
    assert "list the elements of Z/4Z" in output


def test_behavioral_activation_requires_next_action():
    with pytest.raises(ValueError):
        render_behavioral_activation(LessonMoment(concept_name="groups"))


def test_spaced_retrieval_references_the_prior_concept():
    moment = LessonMoment(concept_name="normal subgroups", prior_concept_name="cosets")
    output = render_spaced_retrieval(moment)
    assert "cosets" in output


def test_spaced_retrieval_requires_prior_concept_name():
    with pytest.raises(ValueError):
        render_spaced_retrieval(LessonMoment(concept_name="normal subgroups"))
