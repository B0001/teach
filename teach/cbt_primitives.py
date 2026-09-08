"""CBT-derived pedagogical primitives -- the producer's building blocks.

sandbox-prompt.md and the epic (`bd show teach-8xw`) both name cognitive
behavioural therapy primitives as the pedagogical building blocks, but
nothing in the repo said what that meant concretely until this module: no
enumerable list, no definition of when each one fires, nothing the
persona-rendering stage (teach-8xw.6) could call into. This module is that
list.

Scope of this bead (teach-8xw.7): define the primitives and prove each one,
given a minimal fake lesson moment, produces non-empty, on-topic output. It
does NOT decide *when* in a real traversal each primitive should fire, and
it does NOT do narrative/persona styling -- both are teach-8xw.6's job, once
it exists. A move here returns plain, unstyled tutor-facing text; the
persona layer is expected to re-voice it, not consume it verbatim.

THE FOUR PRIMITIVES

These are exactly the four the epic names, no more invented here:

  - IDENTIFY_STUCK_BELIEF: surface a self-limiting belief the learner just
    voiced ("I'm bad at math") as a hypothesis to test against evidence,
    not as an accepted fact. Applies when the learner's own words assert a
    fixed, negative self-judgment tied to the concept being taught.
  - GRADED_EXPOSURE: pose the next problem as a small, controlled step up
    in difficulty from what the learner just handled -- not a jump to the
    hardest form of the concept. Applies right after the learner succeeds
    at an easier instance and is ready for a harder-but-manageable one.
  - BEHAVIORAL_ACTIVATION: hand the learner one small, concrete, doable-now
    action tied to the concept. Applies when the learner is stalled or
    avoidant and needs re-engagement through action, not more explanation.
  - SPACED_RETRIEVAL: ask the learner to recall and use a concept taught
    earlier in the lesson, before moving on to new material. Applies once
    enough lesson has elapsed since a prior concept that recalling it (not
    re-exposure to it) is what strengthens retention.

Each primitive requires specific fields on `LessonMoment` to fire (see each
render function's docstring) and raises `ValueError` if the field it needs
is missing, rather than silently rendering empty or generic filler --
producing plausible-sounding output from context that isn't there would be
exactly the kind of unverified confidence sandbox-prompt.md warns against.
"""
from __future__ import annotations

import dataclasses
import enum
from typing import Callable


@dataclasses.dataclass(frozen=True)
class LessonMoment:
    """A minimal, fake stand-in for whatever real lesson state
    teach-8xw.6's persona layer will eventually carry. Just enough fields
    for each primitive below to have something concrete to render from.
    """

    concept_name: str
    learner_statement: str | None = None
    prior_concept_name: str | None = None
    next_action: str | None = None
    easier_problem: str | None = None
    harder_problem: str | None = None


def _require(moment: LessonMoment, field: str) -> str:
    value = getattr(moment, field)
    if not value:
        raise ValueError(
            f"LessonMoment.{field} is required to render this primitive, got {value!r}"
        )
    return value


def render_identify_stuck_belief(moment: LessonMoment) -> str:
    """Requires `learner_statement`: what the learner said that reads as a
    fixed, negative self-judgment. Reflects it back as a hypothesis to test
    against what the lesson actually shows, rather than agreeing with it or
    brushing past it."""
    belief = _require(moment, "learner_statement")
    return (
        f'You just said "{belief}." Let\'s treat that as a guess rather than '
        f"a fact for a moment -- what would count as evidence, one way or "
        f"the other, about whether that's true for {moment.concept_name}?"
    )


def render_graded_exposure(moment: LessonMoment) -> str:
    """Requires `easier_problem` (what the learner just handled) and
    `harder_problem` (the small step up). Frames the harder one explicitly
    as a small step from the easier one, not a jump."""
    easier = _require(moment, "easier_problem")
    harder = _require(moment, "harder_problem")
    return (
        f"You just handled {easier} on {moment.concept_name}. Here's one "
        f"small step harder: {harder}. Same idea, just less scaffolding."
    )


def render_behavioral_activation(moment: LessonMoment) -> str:
    """Requires `next_action`: one small, concrete, doable-right-now step.
    Deliberately sized down -- the point is re-engagement through a
    completed action, not covering more ground."""
    action = _require(moment, "next_action")
    return (
        f"Let's not solve the whole thing yet. Just do this one small "
        f"piece on {moment.concept_name}: {action}. That's the whole ask "
        f"for right now."
    )


def render_spaced_retrieval(moment: LessonMoment) -> str:
    """Requires `prior_concept_name`: something taught earlier in this
    lesson. Asks the learner to recall and use it, rather than re-explaining
    it -- retrieval is the mechanism, not re-exposure."""
    prior = _require(moment, "prior_concept_name")
    return (
        f"Before we go on to {moment.concept_name} -- without looking back "
        f"at how we did it -- what was the key move we used for {prior}? "
        f"We're going to need it again in a second."
    )


class PrimitiveName(enum.Enum):
    IDENTIFY_STUCK_BELIEF = "identify_stuck_belief"
    GRADED_EXPOSURE = "graded_exposure"
    BEHAVIORAL_ACTIVATION = "behavioral_activation"
    SPACED_RETRIEVAL = "spaced_retrieval"


@dataclasses.dataclass(frozen=True)
class PedagogicalMove:
    """One named CBT-derived primitive: when it applies, and how to render
    it from a `LessonMoment`. This is the thing teach-8xw.6 is expected to
    call into once it exists."""

    name: PrimitiveName
    when_to_use: str  # one-line definition, per this bead's acceptance criteria
    render: Callable[[LessonMoment], str]


MOVES: tuple[PedagogicalMove, ...] = (
    PedagogicalMove(
        name=PrimitiveName.IDENTIFY_STUCK_BELIEF,
        when_to_use=(
            "The learner's own words just asserted a fixed, negative "
            "self-judgment about their ability tied to the concept at hand."
        ),
        render=render_identify_stuck_belief,
    ),
    PedagogicalMove(
        name=PrimitiveName.GRADED_EXPOSURE,
        when_to_use=(
            "The learner just succeeded at an easier instance of the "
            "concept and is ready for a harder-but-manageable next one."
        ),
        render=render_graded_exposure,
    ),
    PedagogicalMove(
        name=PrimitiveName.BEHAVIORAL_ACTIVATION,
        when_to_use=(
            "The learner is stalled or avoidant and needs re-engagement "
            "through one small completed action, not more explanation."
        ),
        render=render_behavioral_activation,
    ),
    PedagogicalMove(
        name=PrimitiveName.SPACED_RETRIEVAL,
        when_to_use=(
            "Enough lesson has elapsed since a prior concept that recalling "
            "it unprompted -- not re-explaining it -- will strengthen "
            "retention before moving on to new material."
        ),
        render=render_spaced_retrieval,
    ),
)


# --- fake lesson contexts for the runnable check ---------------------------
# One minimal LessonMoment per primitive, populated with only the fields
# that primitive needs. These double as the fixtures both the self-check
# below and tests/test_cbt_primitives.py exercise, so both stay checking
# the same ground truth.

FAKE_CONTEXTS: dict[PrimitiveName, LessonMoment] = {
    PrimitiveName.IDENTIFY_STUCK_BELIEF: LessonMoment(
        concept_name="normal subgroups",
        learner_statement="I'm just bad at math",
    ),
    PrimitiveName.GRADED_EXPOSURE: LessonMoment(
        concept_name="normal subgroups",
        easier_problem="checking that a given subgroup is normal in a small finite group",
        harder_problem="finding all normal subgroups of a group with no worked example given",
    ),
    PrimitiveName.BEHAVIORAL_ACTIVATION: LessonMoment(
        concept_name="normal subgroups",
        next_action="write down the definition of a normal subgroup in your own words",
    ),
    PrimitiveName.SPACED_RETRIEVAL: LessonMoment(
        concept_name="normal subgroups",
        prior_concept_name="cosets",
    ),
}


def is_on_topic(text: str, concept_name: str) -> bool:
    """Mechanical proxy for 'on-topic': the rendered text must actually
    mention the concept it was rendered for, not just be generic
    encouragement filler that would read the same for any concept."""
    return concept_name.lower() in text.lower()


if __name__ == "__main__":
    assert len(MOVES) == 4, f"expected exactly 4 named primitives, got {len(MOVES)}"
    for move in MOVES:
        assert move.when_to_use.strip(), f"{move.name}: when_to_use must not be empty"
        moment = FAKE_CONTEXTS[move.name]
        output = move.render(moment)
        assert output.strip(), f"{move.name}: render produced empty output"
        assert is_on_topic(output, moment.concept_name), (
            f"{move.name}: output does not mention concept {moment.concept_name!r}: {output!r}"
        )
    print(f"OK: {len(MOVES)} CBT primitives all render non-empty, on-topic output from a fake lesson moment")
