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
wrote `teach.cialdini`'s templates. Whatever `check_lesson_text` reports on
it -- flagged or not -- is evidence about THIS text, run through the REAL
unmodified checker; it is not evidence that the seven templates generalize
to phrasings nobody here wrote. That is exactly the caveat this repo's
`teach-9k5`/`teach-8xw.32` lineage insists on stating plainly rather than
rounding into "the layer is honest." What IS new here, and wasn't true
before this bead: the checker has now been run against text a real
persuasion-generation mechanism produced, for the first time -- previously
it had only ever seen one hand-authored sentence and the module's own
worked examples. teach-8xw.45 then used exactly that real generated text to
find a real gap in it: `build_demo_lesson` has no learner turn near the
COMMITMENT_CONSISTENCY move, so this run correctly flags it INFLATED
(teach-8xw.51 tracks fixing the demo lesson itself) instead of the false
"clean" it reported before that bead.
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
        if move.name is PrincipleName.COMMITMENT_CONSISTENCY:
            # teach-8xw.51: render_commitment_consistency's template
            # unconditionally says "the same kind of move you just handled
            # a moment ago" -- true only when a learner turn actually
            # precedes it. Give it one, quoting back the exact
            # `prior_commitment` text the move itself references, the same
            # way `teach.dnf_bond_lesson.build_lesson` does for its own
            # commitment_consistency turn.
            turns.append(Turn(speaker="learner", text=_DEMO_MOMENT.prior_commitment))
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


# --- teach-8xw.44: independently-authored blind round ----------------------
#
# Everything above this point (`build_demo_lesson`, `run_check`) exercises
# the real, unmodified `teach.potential_checker.check_lesson_text` /
# `check_coverage` -- but only ever against text this module's own docstring
# already flags as self-authored: written in the same session, by the same
# process that wrote `teach.cialdini`'s templates. teach-8xw.44 is the bead
# that closes that gap for the first time: a round of persuasive/
# motivational tutor-turn phrasing written by a process with zero visibility
# into `teach/cialdini.py`, `teach/potential_checker.py`, or
# `teach/honesty_rubric.py`'s source, run through the exact same real,
# unmodified checker entry points.
#
# Source, in full, per this bead's own acceptance criteria and per
# sandbox-prompt.md's rule that self-authored examples cannot stand in for a
# generalization claim: a single `Agent` tool call (general-purpose
# subagent, no file/tool access used, briefed only on "write 25 things a
# tutor might say to encourage/motivate/persuade a struggling student,"
# explicitly told to include a realistic unsanitized mix of hedged
# encouragement and outright overpromising) -- the same shape of brief
# teach-8xw.33's precedent used for its own blind round. See
# `sandbox-handoffs/teach-8xw.44.md` for the exact prompt text and the full
# raw agent transcript, kept there verbatim so this measurement is
# reproducible from the repo alone -- teach-8xw.40 found that teach-8xw.33's
# equivalent transcript was NOT saved anywhere durable and only 3 of its 12
# sentences ever became runnable data; all 25 sentences here are locked in
# below as runnable fixture data specifically so that mistake isn't repeated.
#
# Kept verbatim below, never edited, pruned, or reordered after seeing what
# the checker did with them -- per this bead's own explicit instruction, a
# gap this round reveals is new bead-worthy work, not something to quietly
# patch and re-measure in the same pass. Neither `teach/potential_checker.py`
# nor `teach/cialdini.py` was touched to produce the results recorded below.
_TEACH_8XW_44_BLIND_ROUND_SENTENCES: tuple[str, ...] = (
    "Look, nobody gets this on the first pass — I didn't either, and I took two years of this stuff in grad school.",
    "Hang on, back up — remember on Tuesday you told me you actually wanted to understand why this works, not just get the answer? That's exactly what we're doing right now.",
    "Okay, that right there, that little minus sign you almost dropped — that's the exact spot where ninety percent of people trip. You caught it.",
    "We're gonna get through this together, you and me, one line at a time.",
    "That's good work. Genuinely — that's a cleaner way to set it up than I expected.",
    "You keep working like this, you're going to walk into that exam and eat it alive.",
    "I won't lie to you, this one's a slog. It's a slog for everybody. Doesn't mean you're bad at it.",
    "My old professor used to say if you're not confused at some point, you're not paying attention. So congratulations, you're paying attention.",
    "Take a breath. We've got the whole hour. Nothing's on fire.",
    "You know, this is the exact same kind of problem that trips people up in the Sharma textbook — you're in good company.",
    "I want you to notice — you just did that whole step without looking at your notes once.",
    "Alright, one more time, slower. I promise it clicks, it just hasn't clicked yet.",
    "You and Jamie both got stuck right here last month, and look at her now — she's flying through these.",
    "I'm not going to pretend you're going to love this chapter. Nobody loves this chapter. But we're going to get you through it.",
    "That's the kind of mistake smart kids make, honestly — the sloppy-but-almost-right kind. Easy fix.",
    "Hey, remember you said you wanted to actually get into that engineering program? This is one of those unglamorous bricks in that wall.",
    "Let's just get through this one problem. Don't think about the whole chapter, just this one.",
    "I've taught this for fifteen years and I still think this particular proof is mean. It's not you.",
    "You're closer than you think — look, you had the right idea two steps ago, we just need to walk it forward.",
    "Slow and steady, that's all this is. You don't have to be fast, you have to be careful.",
    "I mean it — you've got real instincts for this. Whether you end up loving math or not, the instincts are there.",
    "Okay, deep breath, and let's try it your way this time — I want to see how you're thinking about it.",
    "This is the hard part. Once we're through this part, the rest gets a lot easier, I promise.",
    "You didn't get it wrong, you got it not-yet-right. Big difference.",
    "Look at where you started this semester and look at what you just did without help. That's not nothing — that's real progress.",
)


@dataclasses.dataclass(frozen=True)
class BlindRoundReport:
    """The measured, actual result of running the teach-8xw.44 blind round
    through the real, unmodified checker -- reported in full, same
    no-collapsing-to-pass/fail discipline as `CialdiniCheckReport`."""

    per_sentence_flags: dict[str, tuple[Flag, ...]]
    combined_flags: tuple[Flag, ...]
    combined_coverage: Coverage

    def render(self) -> str:
        lines: list[str] = []
        lines.append("=== teach-8xw.44 blind round: check_lesson_text per sentence, as its own tutor turn ===")
        n_flagged = sum(1 for f in self.per_sentence_flags.values() if f)
        lines.append(f"{n_flagged}/{len(self.per_sentence_flags)} sentences flagged individually")
        for sentence, flags in self.per_sentence_flags.items():
            if flags:
                verdicts = ", ".join(f"{f.verdict.value}: {f.reason}" for f in flags)
                lines.append(f"  [FLAGGED] {verdicts}: {sentence!r}")
        lines.append("=== combined into one 25-turn lesson ===")
        cov = self.combined_coverage
        lines.append(
            f"seen={len(cov.seen)} classified={len(cov.classified)} unclassified={len(cov.unclassified)} "
            f"flags={len(self.combined_flags)}"
        )
        lines.append(
            f"second_person: seen={len(cov.second_person_seen)} "
            f"classified={len(cov.second_person_classified)} unclassified={len(cov.second_person_unclassified)}"
        )
        return "\n".join(lines)


def run_blind_round_check() -> BlindRoundReport:
    per_sentence_flags: dict[str, tuple[Flag, ...]] = {}
    for sentence in _TEACH_8XW_44_BLIND_ROUND_SENTENCES:
        turn_text = f"tutor: {sentence}"
        per_sentence_flags[sentence] = check_lesson_text(turn_text)

    combined_text = "\n".join(f"tutor: {s}" for s in _TEACH_8XW_44_BLIND_ROUND_SENTENCES)
    combined_flags = check_lesson_text(combined_text)
    combined_coverage = check_coverage(combined_text)

    return BlindRoundReport(
        per_sentence_flags=per_sentence_flags,
        combined_flags=combined_flags,
        combined_coverage=combined_coverage,
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
    #
    # teach-8xw.45 gave evidenced_ceiling a turn-adjacency cross-reference,
    # and run against this module's own demo lesson it correctly caught a
    # real gap: `build_demo_lesson` used to render all seven principles as
    # consecutive tutor turns with the one learner turn appended only at
    # the very end, so render_commitment_consistency's "you just handled a
    # moment ago" had no learner turn anywhere near it in that transcript.
    # teach-8xw.51 fixed the demo lesson itself -- it now gives the learner
    # a real turn (quoting `_DEMO_MOMENT.prior_commitment` back, the same
    # way `teach.dnf_bond_lesson.build_lesson` does) immediately before the
    # commitment_consistency move -- so this asserts the corrected, honest
    # "clean" result, not a blindness the checker used to have.
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
        "lesson passed clean with at least one claim actually classified (not vacuously empty), "
        "including the commitment_consistency move now that (teach-8xw.51) it sits right after "
        "a real learner turn instead of eight consecutive tutor turns; "
        "the naive social-proof alternative this layer was deliberately NOT built to produce is "
        "shown side by side, still slipping past unclassified exactly as teach-8xw.32 measured. "
        "Caveat, stated per sandbox-prompt.md, not hidden: this demonstration text is "
        "self-authored in this session -- a clean result here is not evidence the seven "
        "templates generalize to independently-written phrasing."
    )

    # teach-8xw.44: the measured, actual result of running the blind round
    # (see the fixture's own comment block for sourcing) through the real,
    # unmodified checker -- locked in as a regression on the EXACT observed
    # numbers, not on a hoped-for "passes clean" or "catches everything."
    # A change to this assertion block means the checker's behavior on this
    # exact fixture changed; it is not a bar this fixture is expected to
    # clear.
    blind_report = run_blind_round_check()
    _flagged_sentences = tuple(
        sentence for sentence, flags in blind_report.per_sentence_flags.items() if flags
    )
    assert _flagged_sentences == (
        "You keep working like this, you're going to walk into that exam and eat it alive.",
        "I'm not going to pretend you're going to love this chapter. Nobody loves this chapter. "
        "But we're going to get you through it.",
        "I mean it — you've got real instincts for this. Whether you end up loving math or not, "
        "the instincts are there.",
    ), f"teach-8xw.44: expected exactly these 3/25 sentences flagged, got {_flagged_sentences}"

    cov = blind_report.combined_coverage
    assert (len(cov.seen), len(cov.classified), len(cov.unclassified)) == (45, 3, 42), (
        f"teach-8xw.44: expected seen=45 classified=3 unclassified=42, got "
        f"seen={len(cov.seen)} classified={len(cov.classified)} unclassified={len(cov.unclassified)}"
    )
    assert len(blind_report.combined_flags) == 3, (
        f"teach-8xw.44: expected 3 flags on the combined 25-turn lesson, got {len(blind_report.combined_flags)}"
    )

    print()
    print(blind_report.render())
    print()
    print(
        "OK (teach-8xw.44/teach-8xw.50): 25 independently-authored tutor motivational lines (blind Agent "
        "call, no repo access -- see sandbox-handoffs/teach-8xw.44.md), run through the real, unmodified "
        "check_lesson_text/check_coverage -- 3/25 flagged (one ABSTAIN on a vague-ceiling overpromise, "
        "one INFLATED on an unconditioned future claim, and, as of teach-8xw.50, one INFLATED TRAIT on "
        "the bare-instinct-praise sentence that used to land unclassified), 42/45 tutor-spoken sentences "
        "in the combined lesson landed unclassified (seen but not run through the honesty rubric at "
        "all). This is a REAL measurement, not a clean bill of health: reading the unclassified set by "
        "hand still surfaces one apparent gap shape this checker has no fixture for -- inevitable-"
        "outcome-by-named-peer-anecdote ('You and Jamie both got stuck right here... look at her now'). "
        "teach-8xw.50 measured that shape against a NEW independent blind round (13 held-out sentences, "
        "0/13 classified) and closed it via disclosure rather than a regex fitted to this one sentence -- "
        "see sandbox-handoffs/teach-8xw.50.md."
    )


if __name__ == "__main__":
    _self_check()
