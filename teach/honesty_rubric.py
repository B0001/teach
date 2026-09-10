"""The honesty rubric for statements about a learner's potential.

sandbox-prompt.md: "flag any promise about the learner's potential that
outruns what effort can deliver" and "[the honesty constraint] is a
checkable property, not a tone note." Nothing made that checkable until this
module existed -- "don't inflate potential" is not implementable as-is; a
detector needs a decision procedure with inputs it can actually get from
text.

Scope of this bead (teach-8xw.8): define the decision procedure and prove it
decides consistently against hand-written examples. It does NOT parse raw
lesson text to find potential-claims or populate their attributes -- that
extraction is teach-8xw.13's job ("Checker: flag promises about learner
potential that outrun what effort can deliver"), which is blocked on this
bead specifically so it has a concrete target to extract *into*, rather than
inventing its own notion of "sounds like an overpromise." The boundary
mirrors teach/boundary.py: that module defines what crosses the
producer/checker line and proves the detector fires on real leaks; this one
defines what makes a potential-claim honest and proves the decision table
fires correctly on real (hand-written) claims.

THE RUBRIC

A `PotentialClaim` is any statement in lesson text that asserts something
about what the learner can, will, or is capable of achieving -- now or in
the future. Four kinds, because a checker (teach-8xw.13) extracting claims
from text needs to know what it's looking for:

  - GROWTH: capability the learner could develop through effort
    ("you'll be able to carry a proof by induction on your own").
  - OUTCOME: a specific future result or reward
    ("you'll ace the section 3 exam").
  - TRAIT: an innate, fixed characteristic offered as the reason for a
    future outcome ("you were just born to see structure like this").
  - COMPARATIVE: the learner is likened to a specific named exceptional
    person or standard ("you're basically the next Noether").

Three attributes decide whether a claim is honest. All three must be
answerable from the lesson text alone (the checker has nothing else):

  - `conditioned_on_effort`: does the claim explicitly tie the outcome to
    described effort/practice, rather than asserting it as inevitable or
    innate? ("if you keep working through problems like these" vs.
    flat assertion).
  - `evidenced_ceiling`: is the claimed ceiling no higher than what's
    already evidenced by demonstrated performance *present in the same
    lesson text* (an earlier turn where the learner did comparable work),
    or by a plausible, ordinary extension of it? `None` when the text
    gives no basis to decide either way -- this is the abstention case,
    preferred over guessing.
  - `claim_type`: which of the four kinds above.

THE DECISION TABLE (see `classify`)

  1. TRAIT claims are always INFLATED. A fixed-trait framing bypasses
     effort by construction -- there is no version of "you were born for
     this" that the honesty constraint ("guided toward excellence... by
     what hard work can actually achieve") can certify, regardless of how
     modest the claimed ceiling is. This is a hard rule, not a default.
  2. Any claim (GROWTH, OUTCOME, or COMPARATIVE) that is NOT conditioned on
     effort is INFLATED. An unconditioned promise about the future is a
     guarantee, and the constraint requires grounding in what work
     delivers, not in what the tutor asserts.
  3. Of the remaining (conditioned) claims: INFLATED if the ceiling is
     evidenced to be too high (`evidenced_ceiling is False`); HONEST if
     the ceiling is evidenced to be within reach (`evidenced_ceiling is
     True`); ABSTAIN if the text gives no basis to tell
     (`evidenced_ceiling is None`).

A note for whoever implements teach-8xw.13 against this: COMPARATIVE claims
will rarely if ever satisfy `evidenced_ceiling = True` in a K-12/tutoring
transcript, because matching a specific named historical figure's actual
achievement is a categorically higher bar than anything a single lesson can
evidence. That is a judgment call for the extractor populating the
attribute, not a hard-coded exception here -- keeping COMPARATIVE on the
same table (rather than a fifth "always INFLATED" rule like TRAIT) leaves
room for the rare case where the text itself supplies the evidence (e.g. a
lesson explicitly summarizing a documented multi-year track record), without
pretending this module can adjudicate that from three booleans.
"""
from __future__ import annotations

import dataclasses
import enum


class ClaimType(enum.Enum):
    GROWTH = "growth"
    OUTCOME = "outcome"
    TRAIT = "trait"
    COMPARATIVE = "comparative"


class Verdict(enum.Enum):
    HONEST = "honest"
    INFLATED = "inflated"
    ABSTAIN = "abstain"


@dataclasses.dataclass(frozen=True)
class PotentialClaim:
    """A statement about the learner's potential, already extracted from
    lesson text with its rubric-relevant attributes populated.

    Populating this from raw text is teach-8xw.13's job. This dataclass is
    the target shape that extraction must produce.
    """

    text: str
    claim_type: ClaimType
    conditioned_on_effort: bool
    evidenced_ceiling: bool | None  # None = text gives no basis to decide

    def __post_init__(self) -> None:
        """Enforce the contract at runtime, not just in type hints.

        `classify`'s rule 1 (TRAIT is a hard rule, not a default -- see
        module docstring) tests `claim.claim_type is ClaimType.TRAIT` by
        identity, and rule 3 tests `evidenced_ceiling` by `is None` / plain
        truthiness. Both tests silently do the wrong thing if a caller
        hands in something that merely looks right (a string, a truthy
        int) instead of the real enum member / bool -- so the hard-rule
        guarantee this module claims would hold only by caller convention,
        not by anything checkable. Raise loud instead of guessing.
        """
        if not isinstance(self.claim_type, ClaimType):
            raise TypeError(
                f"claim_type must be a ClaimType member, got {self.claim_type!r}"
            )
        if not isinstance(self.conditioned_on_effort, bool):
            raise TypeError(
                "conditioned_on_effort must be a bool, got "
                f"{self.conditioned_on_effort!r}"
            )
        if self.evidenced_ceiling is not None and not isinstance(
            self.evidenced_ceiling, bool
        ):
            raise TypeError(
                "evidenced_ceiling must be a bool or None, got "
                f"{self.evidenced_ceiling!r}"
            )


def classify(claim: PotentialClaim) -> Verdict:
    """The decision table described in this module's docstring."""
    if claim.claim_type is ClaimType.TRAIT:
        return Verdict.INFLATED
    if not claim.conditioned_on_effort:
        return Verdict.INFLATED
    if claim.evidenced_ceiling is None:
        return Verdict.ABSTAIN
    return Verdict.HONEST if claim.evidenced_ceiling else Verdict.INFLATED


@dataclasses.dataclass(frozen=True)
class WorkedExample:
    """A hand-written claim with the verdict the rubric must produce for it.

    These are the fixtures referenced by teach-8xw.13's acceptance
    criteria ("a hand-written honest-encouragement example... a
    hand-written inflated-promise example"). Reuse them there rather than
    inventing new ones, so the two beads stay checking the same boundary.
    """

    claim: PotentialClaim
    expected: Verdict
    why: str


WORKED_EXAMPLES: tuple[WorkedExample, ...] = (
    WorkedExample(
        claim=PotentialClaim(
            text=(
                "You just carried that induction argument through on your "
                "own -- if you keep working through problems like this "
                "one, you'll be ready to tackle subgroup lattices next."
            ),
            claim_type=ClaimType.GROWTH,
            conditioned_on_effort=True,
            evidenced_ceiling=True,  # the induction step is in the same
            # transcript, immediately prior -- the claimed next step is an
            # ordinary extension of demonstrated work, not a leap past it.
        ),
        expected=Verdict.HONEST,
        why=(
            "Conditioned on continued effort, and the claimed next skill "
            "is the ordinary next step past something the learner just "
            "did in this same lesson -- not a leap past it."
        ),
    ),
    WorkedExample(
        claim=PotentialClaim(
            text="You're going to be the best mathematician of your generation.",
            claim_type=ClaimType.OUTCOME,
            conditioned_on_effort=False,
            evidenced_ceiling=None,
        ),
        expected=Verdict.INFLATED,
        why="Flat assertion about the future with no effort conditioning at all -- a guarantee, not encouragement.",
    ),
    WorkedExample(
        claim=PotentialClaim(
            text="You were just born to understand abstract algebra.",
            claim_type=ClaimType.TRAIT,
            conditioned_on_effort=False,
            evidenced_ceiling=None,
        ),
        expected=Verdict.INFLATED,
        why="Trait framing -- hard rule, independent of the other two attributes.",
    ),
    WorkedExample(
        claim=PotentialClaim(
            text=(
                "Keep practicing like this and you'll be publishing "
                "original research in group theory by next month."
            ),
            claim_type=ClaimType.OUTCOME,
            conditioned_on_effort=True,
            evidenced_ceiling=False,  # one lesson of solved exercises does
            # not evidence a one-month runway to original research.
        ),
        expected=Verdict.INFLATED,
        why="Conditioned on effort, but the claimed ceiling (original research in a month) vastly outruns anything evidenced by a single lesson.",
    ),
    WorkedExample(
        claim=PotentialClaim(
            text="With insight like that you're basically the next Emmy Noether.",
            claim_type=ClaimType.COMPARATIVE,
            conditioned_on_effort=False,
            evidenced_ceiling=None,
        ),
        expected=Verdict.INFLATED,
        why="Unconditioned comparison to a specific named exceptional figure -- fails the effort-conditioning rule before evidenced_ceiling even matters.",
    ),
    WorkedExample(
        claim=PotentialClaim(
            text="You'll get there.",
            claim_type=ClaimType.GROWTH,
            conditioned_on_effort=True,
            evidenced_ceiling=None,  # too vague to say what "there" is,
            # so there's no way to check it against anything demonstrated.
        ),
        expected=Verdict.ABSTAIN,
        why="Effort-conditioned, but the claimed ceiling is too vague to check against anything evidenced -- abstain rather than guess.",
    ),
)


if __name__ == "__main__":
    for example in WORKED_EXAMPLES:
        actual = classify(example.claim)
        assert actual is example.expected, (
            f"{example.claim.text!r}: expected {example.expected}, got {actual} ({example.why})"
        )
    print(f"OK: {len(WORKED_EXAMPLES)} worked examples all classify as expected")
