"""Run the Cialdini/Pre-Suasion motivation layer (teach-8xw.31) through the
existing blind checkers for real, and report the actual result.

teach-8xw.31's acceptance criteria, stated directly in the bead: build the
generation layer, then "it must be run through teach/potential_checker.py
and teach/honesty_rubric.py (the existing blind checker) and the actual
flag/pass results reported, since that is the real test the epic describes
as the point of building the checker in the first place." This module is
that run.

Mirrors the existing `dnf_bond_lesson.py` / `dnf_bond_integration.py` split:
`teach.cialdini` is the pure generation module (no checker imports, same as
`teach.cbt_primitives`); this module is the one that crosses the boundary,
building a real lesson transcript out of `teach.cialdini`'s moves and
feeding it to `teach.potential_checker` exactly the way a learner-facing
transcript would reach it -- flattened text, nothing else.

`teach.honesty_rubric.classify` is exercised here only indirectly, through
`teach.potential_checker.check_lesson_text` (which calls `classify` on
every claim it extracts) -- there is no separate raw-text entry point into
`honesty_rubric` itself, since by its own module docstring it operates on
already-extracted `PotentialClaim`s, and extraction from text is
`potential_checker`'s job. Running the generated text through
`check_lesson_text` is therefore the full, real exercise of both modules
this bead's acceptance criteria ask for.

TWO THINGS THIS RUN REPORTS, NOT ONE

  1. The demonstration lesson built from `teach.cialdini`'s seven honestly-
     bounded moves (see that module's docstring for why SOCIAL_PROOF and
     AUTHORITY are shaped the way they are) -- what actually gets
     extracted, classified, and (not) flagged.
  2. Side by side with (1): teach-8xw.32's own confirmed-blind sentence
     (`_TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES[0]`, imported verbatim,
     not re-authored here) -- the exact shape a NAIVE social-proof
     rendering of this same principle would have produced. This is not a
     new measurement of that gap (teach-8xw.32 already measured and closed
     it); it is here so the contrast between "this module's actual output"
     and "the known-blind naive alternative" is visible in one report,
     answering the bead's own warning that a naive build "would
     immediately trigger" that gap.

WHAT THIS RUN DOES NOT ESTABLISH

Per sandbox-prompt.md's rule on self-authored examples: the demonstration
lesson below is written in this same session, by the same process that
wrote `teach.cialdini`'s templates. A clean `check_lesson_text` result on
it is evidence that THIS text, run through the REAL unmodified checker,
produced no flags -- it is not evidence that the seven templates
generalize to phrasings nobody here wrote. That is exactly the caveat this
repo's `teach-9k5`/`teach-8xw.32` lineage insists on stating plainly rather
than rounding into "the layer is honest." What IS new here, and wasn't true
before this bead: the checker has now been run against text a real
persuasion-generation mechanism produced, for the first time -- previously
it had only ever seen one hand-authored sentence and the module's own
worked examples.
"""
from __future__ import annotations

import dataclasses

from teach.boundary import LessonArtifact, Turn
from teach.cialdini import MotivationMoment, MOVES, PrincipleName
from teach.potential_checker import (
    Coverage,
    Flag,
    check_coverage,
    check_lesson_text,
)
from teach.potential_checker import _TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES  # noqa: F401 -- see module docstring


# A single demonstration lesson moment: the shared D&F/Bond content this
# session's `teach.dnf_bond_lesson` already teaches (cosets and normal
# subgroups, on the way to Lagrange's Theorem), reused here as the concrete
# substance each Cialdini move renders from -- not a fresh, unrelated
# example invented just for this check.
_DEMO_MOMENT = MotivationMoment(
    concept_name="normal subgroups",
    given_first="a fully worked check that a specific subgroup of a small finite group is normal",
    next_ask="check whether a second, different subgroup satisfies the same condition",
    prior_commitment="I want to actually understand why cosets have to be the same size, not just accept it",
    consistent_next_step="working through why every left coset of H has exactly |H| elements, instead of skipping to the statement of Lagrange's Theorem",
    shared_frame="the Bond briefing",
    cited_source="Dummit and Foote's Abstract Algebra, section 3.1",
    authority_fact="a subgroup is normal exactly when its left and right cosets coincide for every element",
    scarce_detail="the condition has to hold for every element of the group, not just the ones already checked",
    shared_identity="the two of us working this problem set",
    peer_difficulty="mixing up 'closed under conjugation' with 'closed under the group operation'",
)


def build_demo_lesson() -> LessonArtifact:
    """One tutor turn per Cialdini principle (variant 0), rendered from
    `_DEMO_MOMENT`, plus the plain domain content those turns refer to --
    a small but real transcript, not a bag of sentences with no shared
    context."""
    turns: list[Turn] = [
        Turn(
            speaker="tutor",
            text=(
                "Cosets and Normal Subgroups is the payoff of vetting Q Branch: "
                "a subgroup H of G is normal exactly when every left coset of H "
                "equals the corresponding right coset."
            ),
        ),
    ]
    for move in MOVES:
        turns.append(Turn(speaker="tutor", text=move.render(_DEMO_MOMENT, 0)))
    turns.append(
        Turn(
            speaker="learner",
            text="Okay -- I can see why the left and right cosets have to match up for every element.",
        )
    )
    return LessonArtifact(turns=tuple(turns))


@dataclasses.dataclass(frozen=True)
class CialdiniCheckReport:
    """What the real, unmodified checker actually did with the generated
    lesson -- reported in full, never collapsed to a bare pass/fail."""

    per_principle_flags: dict[PrincipleName, tuple[Flag, ...]]
    lesson_flags: tuple[Flag, ...]
    lesson_coverage: Coverage
    naive_social_proof_sentence: str
    naive_social_proof_flags: tuple[Flag, ...]
    naive_social_proof_coverage: Coverage

    def render(self) -> str:
        lines: list[str] = []
        lines.append("=== per-principle: check_lesson_text on each move's own rendered turn ===")
        for name, flags in self.per_principle_flags.items():
            verdicts = ", ".join(f"{f.verdict.value}: {f.reason}" for f in flags) or "(no flags)"
            lines.append(f"  {name.value}: {verdicts}")

        lines.append("=== full demonstration lesson ===")
        cov = self.lesson_coverage
        lines.append(
            f"tutor-spoken sentences: {len(cov.seen)} seen, "
            f"{len(cov.classified)} classified, {len(cov.unclassified)} unclassified"
        )
        if cov.unclassified:
            lines.append("unclassified (seen but not run through the honesty rubric):")
            lines.extend(f"  - {s}" for s in cov.unclassified)
        if self.lesson_flags:
            for flag in self.lesson_flags:
                lines.append(f"  [{flag.verdict.value}] {flag.reason}: {flag.claim.text!r}")
        else:
            lines.append(
                f"(no flags among the {len(cov.classified)} classified claim(s) in this lesson)"
            )

        lines.append("=== contrast: teach-8xw.32's confirmed-blind naive social-proof shape ===")
        lines.append(f"sentence (verbatim from teach-8xw.32's fixtures): {self.naive_social_proof_sentence!r}")
        lines.append(
            f"check_lesson_text -> {len(self.naive_social_proof_flags)} flag(s); "
            f"check_coverage -> seen={len(self.naive_social_proof_coverage.seen)} "
            f"classified={len(self.naive_social_proof_coverage.classified)} "
            f"unclassified={len(self.naive_social_proof_coverage.unclassified)}"
        )
        lines.append(
            "this sentence is the shape teach.cialdini.render_social_proof was deliberately "
            "built NOT to produce -- see teach/cialdini.py's module docstring"
        )
        return "\n".join(lines)


def run_check() -> CialdiniCheckReport:
    per_principle_flags: dict[PrincipleName, tuple[Flag, ...]] = {}
    for move in MOVES:
        turn_text = f"tutor: {move.render(_DEMO_MOMENT, 0)}"
        per_principle_flags[move.name] = check_lesson_text(turn_text)

    artifact = build_demo_lesson()
    lesson_flags = check_lesson_text(artifact.text)
    lesson_coverage = check_coverage(artifact.text)

    naive_sentence = _TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES[0]
    naive_flags = check_lesson_text(naive_sentence)
    naive_coverage = check_coverage(naive_sentence)

    return CialdiniCheckReport(
        per_principle_flags=per_principle_flags,
        lesson_flags=lesson_flags,
        lesson_coverage=lesson_coverage,
        naive_social_proof_sentence=naive_sentence,
        naive_social_proof_flags=naive_flags,
        naive_social_proof_coverage=naive_coverage,
    )


def _self_check() -> None:
    report = run_check()

    # Boundary: the artifact built here is the same LessonArtifact shape
    # every other producer module crosses with -- no forbidden fields.
    from teach.boundary import check_no_forbidden_fields

    artifact = build_demo_lesson()
    violations = check_no_forbidden_fields(type(artifact))
    assert violations == [], f"build_demo_lesson leaked planner fields: {violations}"

    # The measured, actual result of running this bead's generated text
    # through the real checker -- asserted against what was observed
    # running this module, not against what was hoped for going in.
    assert report.lesson_flags == (), (
        f"expected the honestly-bounded demonstration lesson to pass clean, got {report.lesson_flags}"
    )
    assert len(report.lesson_coverage.seen) > 0
    assert len(report.lesson_coverage.classified) > 0, (
        "expected at least one sentence in the demonstration lesson to actually reach the "
        "honesty rubric (not just be seen) -- a clean result over zero classified claims would "
        "be the teach-yn8 failure mode (silence mistaken for a passed check)"
    )

    # The contrast this run exists to show: the same social-proof principle,
    # rendered the naive way (teach-8xw.32's own fixture, not re-authored
    # here), produces zero flags for a different reason -- it isn't even
    # classified, confirming the already-measured gap rather than papering
    # over it.
    assert report.naive_social_proof_flags == ()
    assert report.naive_social_proof_coverage.classified == ()
    assert report.naive_social_proof_coverage.unclassified == (report.naive_social_proof_sentence,)

    print(report.render())
    print()
    print(
        "OK: all 7 Cialdini/Pre-Suasion principles rendered real text and were run through "
        "teach.potential_checker's actual extract_claims/classify pipeline; the demonstration "
        "lesson passed clean with at least one claim actually classified (not vacuously empty); "
        "the naive social-proof alternative this layer was deliberately NOT built to produce is "
        "shown side by side, still slipping past unclassified exactly as teach-8xw.32 measured. "
        "Caveat, stated per sandbox-prompt.md, not hidden: this demonstration text is "
        "self-authored in this session -- a clean result here is not evidence the seven "
        "templates generalize to independently-written phrasing."
    )


if __name__ == "__main__":
    _self_check()
