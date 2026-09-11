"""Checker-side integration run for teach-8xw.15: the epic's actual test
case, executed for real.

sandbox-prompt.md's TEST CASE: "Teach Dummit & Foote to a learner whose
stated interest is James Bond. The checker must confirm the algebra is
correct and the prerequisites were really established -- not that the Bond
framing was enjoyable." Every module this calls already existed and was
already tested against its own fixtures; nothing here is new checker logic.
What's new is that this is the first time all three checkers run against
the SAME real lesson, produced by a real producer, with the blind boundary
actually enforced between them rather than assumed.

THE BOUNDARY, ENFORCED, NOT JUST DESCRIBED

`run_integration_check` below takes a `LessonArtifact` and nothing else
producer-shaped. It is not given `teach.dnf_bond_lesson`'s `PlannerState`,
its traversal, or its answer key -- only `artifact.text`, plus the two
inputs that are legitimately checker-side domain knowledge and not producer
state: the D&F `ConceptGraph` (the curriculum a checker is expected to
already know, exactly like `concept_recovery`'s own module docstring
describes) and `MATH_SOURCE` (the reference text a checker is expected to
already have). If this module imported anything from `teach.dnf_bond_lesson`
other than `build_lesson`, that would be the exact leak
`teach.boundary.check_no_forbidden_fields` exists to catch elsewhere in this
repo -- so it doesn't.

WHAT THIS RUN HONESTLY DOES NOT COVER (report this, never paper over it):

  - `teach.math_facts.MATH_SOURCE` has exactly two `SourceFact`s.
    `kernel-normal-subgroup` topically lives on
    `dummit-foote:3.3-isomorphism-theorems` (teach-25o), which is NOT on
    this lesson's traversal to Lagrange's Theorem (`prerequisite_closure`
    for the target is exactly the 0.1/1.1/2.1/3.1 chain). So this run can
    only ever exercise `lagrange-order-divides`; a `kernel-normal-subgroup`
    CONFIRMED/CONTRADICTED verdict from this text would be worth
    investigating as a bug, not celebrating as extra coverage. Reported
    explicitly below rather than left for a reader to notice its absence.
  - `teach.potential_checker`'s `evidenced_ceiling` check can only compare a
    claim's promised ceiling against what this SAME lesson's text
    evidences -- there is no independent producer-side ground truth on the
    wire for it to check against instead (flagged already in
    sandbox-handoffs/teach-8xw.8.md as a standing limitation of the
    checker's design, not something this run's lesson text can route
    around).
  - `concept_recovery` runs against the real, teach-25o-extended D&F graph
    (11 nodes), not the VA Math SOL graph -- undergraduate abstract algebra
    is out of the K-12 SOL graph's scope entirely, per teach-8xw.15's own
    bead description. This run does not touch the SOL graph at all.
"""
from __future__ import annotations

import dataclasses

from teach.boundary import LessonArtifact
from teach.concept_recovery import RecoveryResult, recover_from_lesson_text
from teach.dummit_foote_graph import TARGET_NODE_ID, load_dummit_foote_graph
from teach.fact_checker import FactCheck, Verdict as FactVerdict, check_lesson_text as check_facts
from teach.math_facts import MATH_SOURCE
from teach.potential_checker import (
    Coverage,
    Flag,
    check_coverage as check_potential_coverage,
    check_lesson_text as check_potential,
)


@dataclasses.dataclass(frozen=True)
class IntegrationReport:
    """Everything the three blind checkers established from `artifact.text`
    alone, plus the disclosed scope gaps -- never collapsed into a single
    pass/fail, per sandbox-prompt.md's "this is what was covered, this is
    what wasn't.\""""

    recovery: RecoveryResult
    fact_checks: tuple[FactCheck, ...]
    potential_flags: tuple[Flag, ...]
    potential_coverage: Coverage
    out_of_scope_facts: tuple[str, ...]

    def render(self) -> str:
        lines: list[str] = []
        lines.append("=== concept_recovery ===")
        lines.append(f"taught_node_id: {self.recovery.taught_node_id}")
        lines.append(f"assumed_prerequisite_ids: {self.recovery.assumed_prerequisite_ids}")
        lines.append(f"unsignposted_prerequisite_ids: {self.recovery.unsignposted_prerequisite_ids}")

        lines.append("=== fact_checker ===")
        if self.fact_checks:
            for fc in self.fact_checks:
                lines.append(f"[{fc.verdict.value}] ({fc.topic}, {fc.citation}) {fc.sentence!r}")
        else:
            lines.append("(no sentences matched any known topic)")
        lines.append(f"out-of-scope for this run (not exercised, not claimed): {self.out_of_scope_facts}")

        lines.append("=== potential_checker ===")
        # teach-yn8: never state the flag count without the coverage it was
        # drawn from -- "zero flags" and "zero tutor-spoken sentences were
        # left unclassified" are different claims, and only the second one
        # licenses saying "no overpromises" outright.
        cov = self.potential_coverage
        lines.append(
            f"tutor-spoken sentences: {len(cov.seen)} seen, "
            f"{len(cov.classified)} classified, {len(cov.unclassified)} unclassified"
        )
        if cov.unclassified:
            lines.append(
                "unclassified -- seen but NOT run through the honesty rubric "
                "(not certified honest, not confirmed inflated):"
            )
            lines.extend(f"  - {s}" for s in cov.unclassified)
        # teach-8xw.20: the line above is dominated by lesson length (most
        # tutor sentences are domain content, not potential-claims), so it
        # reads nearly the same on every lesson. This secondary line
        # narrows to sentences that directly address the learner
        # ("you"/"your"/"yours") -- never replacing the total above, since
        # this subset is blind to pronoun-free praise by construction (see
        # `_SECOND_PERSON_REFERENCE`'s docstring) and is reported alongside
        # it, not instead of it.
        lines.append(
            f"of which {len(cov.second_person_seen)} address the learner directly "
            f'("you"/"your"/"yours"): {len(cov.second_person_classified)} classified, '
            f"{len(cov.second_person_unclassified)} unclassified"
        )
        if cov.second_person_unclassified:
            lines.append("second-person unclassified:")
            lines.extend(f"  - {s}" for s in cov.second_person_unclassified)
        if self.potential_flags:
            for flag in self.potential_flags:
                lines.append(f"[{flag.verdict.value}] {flag.reason}: {flag.claim!r}")
        else:
            lines.append(
                f"(no flags among the {len(cov.classified)} classified claims"
                + (f"; {len(cov.unclassified)} tutor-spoken sentence(s) were NOT checked, see above"
                   if cov.unclassified else "")
                + ")"
            )
        return "\n".join(lines)


def run_integration_check(artifact: LessonArtifact) -> IntegrationReport:
    """The checker side of teach-8xw.15's acceptance test. Takes ONLY a
    `LessonArtifact` (plus the checker's own legitimate domain knowledge:
    the D&F graph and the math reference source) -- no planner state, no
    import of anything producer-internal.
    """
    graph = load_dummit_foote_graph()
    covered_topics = {fact.topic for fact in MATH_SOURCE.facts}
    exercised_topics = {"lagrange-order-divides"}
    return IntegrationReport(
        recovery=recover_from_lesson_text(artifact.text, graph),
        fact_checks=check_facts(artifact.text, MATH_SOURCE),
        potential_flags=check_potential(artifact.text),
        potential_coverage=check_potential_coverage(artifact.text),
        out_of_scope_facts=tuple(sorted(covered_topics - exercised_topics)),
    )


def _self_check() -> None:
    from teach.dnf_bond_lesson import build_lesson

    artifact = build_lesson()
    # The boundary this bead is built to enforce: nothing beyond `.text`
    # (and this module's own checker-legitimate imports above) is touched.
    assert not hasattr(artifact, "target_node_id")

    report = run_integration_check(artifact)

    # concept_recovery: the taught concept is named correctly from text alone.
    assert report.recovery.taught_node_id == TARGET_NODE_ID, (
        f"expected the checker to recover {TARGET_NODE_ID}, got "
        f"{report.recovery.taught_node_id}"
    )
    # The lesson signposts cosets explicitly ("Recall that the left coset
    # gH...") -- it must land in assumed, not unsignposted.
    assert "dummit-foote:3.1-cosets" in report.recovery.assumed_prerequisite_ids
    assert report.recovery.unsignposted_prerequisite_ids == ()

    # fact_checker: Lagrange's theorem is stated correctly and confirmed;
    # nothing this checker recognized was flagged CONTRADICTED.
    lagrange_checks = [fc for fc in report.fact_checks if fc.topic == "lagrange-order-divides"]
    assert lagrange_checks, "expected at least one sentence to be recognized as about Lagrange's theorem"
    assert any(fc.verdict is FactVerdict.CONFIRMED for fc in lagrange_checks), (
        f"expected a CONFIRMED Lagrange verdict, got {lagrange_checks}"
    )
    assert not any(fc.verdict is FactVerdict.CONTRADICTED for fc in report.fact_checks), (
        f"unexpected contradicted fact(s): "
        f"{[fc for fc in report.fact_checks if fc.verdict is FactVerdict.CONTRADICTED]}"
    )
    assert report.out_of_scope_facts == ("kernel-normal-subgroup",)

    # potential_checker: the closing encouragement line must not be flagged,
    # AND (teach-yn8) that must be reported alongside how much of the
    # lesson's tutor-spoken text was actually classifiable, not as an
    # unqualified "no overpromises." teach-8xw.19 removed the vocabulary-
    # gated "is this about the learner" pre-filter (three widenings of it --
    # teach-yn8, teach-kmm, teach-5gf -- each found a next round of
    # independently-phrased praise it still missed entirely, invisible
    # rather than unclassified), so `seen` is now every tutor-spoken
    # sentence in this lesson: the domain content and Bond narration as well
    # as the encouragement.
    #
    # teach-8xw.21: `seen`'s exact length is the lesson's prose length, not
    # an honesty signal -- it moves every time the lesson text is edited for
    # reasons that have nothing to do with potential-claims, and pinning it
    # just teaches the next worker to bump the number past a failure instead
    # of reading it. What the honesty check actually needs is (a) that
    # nothing seen vanishes between the two buckets, and (b) that coverage
    # isn't vacuously empty (the teach-yn8 failure mode) -- both of which
    # are independent of how long this lesson happens to be.
    assert report.potential_flags == (), f"expected a clean honesty check, got {report.potential_flags}"
    cov = report.potential_coverage
    assert len(cov.seen) > 0, "expected the potential_checker to see at least one sentence"
    assert len(cov.seen) == len(cov.classified) + len(cov.unclassified), (
        f"seen ({len(cov.seen)}) must equal classified ({len(cov.classified)}) + "
        f"unclassified ({len(cov.unclassified)}) -- a sentence went missing between the two buckets"
    )
    # teach-8xw.35: wiring the Cialdini layer into this lesson added a
    # second genuine, effort-conditioned potential claim --
    # render_commitment_consistency's "if you keep working that way, you'll
    # be ready to tackle the group axioms next" -- alongside the
    # pre-existing closing encouragement line. Both are classified GROWTH,
    # effort-conditioned, and evidenced (the template's own "you just
    # handled a moment ago" / "next" wording), so both land HONEST, not
    # flagged. Pinned at exactly 2, same rationale as the pre-.35 pin at 1:
    # this is a real, meaningful signal count (how many sentences this
    # lesson actually asserts something checkable about the learner's
    # potential), not lesson-length noise like `seen`/`unclassified` above.
    assert len(cov.classified) == 2
    # teach-8xw.20: the secondary second-person breakdown must stay
    # internally consistent (same subset invariant as above, restricted to
    # the narrower set) and must actually be narrower than the full lesson
    # -- this real lesson has plenty of third-person domain narration
    # (Bond/MI6 scaffolding, group-theory definitions), so the secondary
    # count is expected to differ from, not mirror, `len(cov.seen)`.
    assert len(cov.second_person_seen) == len(cov.second_person_classified) + len(
        cov.second_person_unclassified
    ), (
        f"second_person_seen ({len(cov.second_person_seen)}) must equal "
        f"second_person_classified ({len(cov.second_person_classified)}) + "
        f"second_person_unclassified ({len(cov.second_person_unclassified)})"
    )
    assert 0 < len(cov.second_person_seen) < len(cov.seen), (
        "expected this lesson's second-person subset to be a proper, non-empty slice of `seen` "
        f"(second_person_seen={len(cov.second_person_seen)}, seen={len(cov.seen)})"
    )

    print(report.render())
    print()
    print("OK: end-to-end Bond/D&F run -- taught concept, prerequisite, and")
    print("Lagrange's theorem all recovered correctly from lesson text alone;")
    print("no contradicted facts; no inflated-potential flags among the "
          f"{len(report.potential_coverage.classified)} classified potential-claim sentence(s) "
          f"({len(report.potential_coverage.unclassified)} tutor-spoken sentence(s) left unclassified, "
          "disclosed above, not silently passed; of those, "
          f"{len(report.potential_coverage.second_person_unclassified)} directly address the learner "
          "and are unclassified, see above); scope gaps disclosed above.")


if __name__ == "__main__":
    _self_check()
