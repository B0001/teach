"""Enforce the producer/checker boundary defined in teach/boundary.py.

teach-8xw.9's acceptance criteria: a runnable check that fails if any field
reachable from the checker-facing artifact contains planner-only fields
(target node id, traversal, answer key). These tests are that check, plus
proof that the check itself actually fires rather than passing vacuously.
"""
import dataclasses

from teach.boundary import (
    LessonArtifact,
    Turn,
    check_no_forbidden_fields,
)
from teach.producer_state import PlannerState, emit_lesson_artifact


def test_lesson_artifact_has_no_forbidden_fields():
    """The actual boundary type must be clean. This is the enforcement."""
    violations = check_no_forbidden_fields(LessonArtifact)
    assert violations == []


def test_turn_has_no_forbidden_fields():
    violations = check_no_forbidden_fields(Turn)
    assert violations == []


def test_check_fires_on_a_directly_leaky_type():
    """Prove the detector isn't vacuous: it must catch an obvious leak."""

    @dataclasses.dataclass(frozen=True)
    class LeakyArtifact:
        turns: tuple[Turn, ...]
        target_node_id: str

    violations = check_no_forbidden_fields(LeakyArtifact)
    assert len(violations) == 1
    assert violations[0].field_name == "target_node_id"


def test_check_fires_on_a_leak_nested_inside_a_container():
    """A forbidden field hiding inside tuple[SomeDataclass, ...] must also
    be caught -- the leak doesn't have to be a top-level field."""

    @dataclasses.dataclass(frozen=True)
    class TurnWithAnswerKey:
        speaker: str
        text: str
        answer_key: str

    @dataclasses.dataclass(frozen=True)
    class NestedLeakArtifact:
        turns: tuple[TurnWithAnswerKey, ...]

    violations = check_no_forbidden_fields(NestedLeakArtifact)
    matched_fields = {v.field_name for v in violations}
    assert "answer_key" in matched_fields


def test_planner_state_itself_is_correctly_flagged_as_unfit_to_cross():
    """PlannerState is the producer's real internal state -- it SHOULD be
    full of forbidden fields. This documents why it must never be handed to
    a checker directly, and proves the check isn't tuned to only ever pass."""
    violations = check_no_forbidden_fields(PlannerState)
    matched_fields = {v.field_name for v in violations}
    assert {"target_node_id", "traversal", "answer_key"} <= matched_fields


def test_emit_lesson_artifact_carries_only_turns():
    state = PlannerState(
        target_node_id="dummit-foote-3.1-normal-subgroups",
        traversal=("groups", "subgroups", "normal-subgroups"),
        answer_key={"q1": "the kernel of a homomorphism is normal"},
        turns=(
            Turn(speaker="tutor", text="M says the mission needs a subgroup that stays fixed under conjugation."),
            Turn(speaker="learner", text="Like cover stays intact no matter who's watching?"),
        ),
    )

    artifact = emit_lesson_artifact(state)

    assert isinstance(artifact, LessonArtifact)
    assert artifact.turns == state.turns
    assert check_no_forbidden_fields(type(artifact)) == []
    # The planner-only values must not be reachable from the artifact at all
    # -- not just absent as field names, but absent as an attribute.
    assert not hasattr(artifact, "target_node_id")
    assert not hasattr(artifact, "traversal")
    assert not hasattr(artifact, "answer_key")


def test_lesson_artifact_text_is_learner_visible_only():
    artifact = LessonArtifact(
        turns=(
            Turn(speaker="tutor", text="Bond needed backup that wouldn't crack."),
            Turn(speaker="learner", text="A subgroup that's normal, so it survives any conjugation M throws at it."),
        )
    )
    assert artifact.text == (
        "tutor: Bond needed backup that wouldn't crack.\n"
        "learner: A subgroup that's normal, so it survives any conjugation M throws at it."
    )
