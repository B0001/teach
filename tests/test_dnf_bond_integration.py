"""teach-8xw.15: the epic's actual acceptance test, run for real.

A real producer (teach.dnf_bond_lesson) builds a Bond-framed Dummit & Foote
lesson ending at Lagrange's Theorem; a real blind checker
(teach.dnf_bond_integration) consumes only the resulting LessonArtifact and
must independently recover the taught concept, confirm the mathematics, and
confirm the encouragement is honest -- with the coverage gaps this
particular run does not exercise disclosed, not hidden.
"""
from teach.boundary import check_no_forbidden_fields
from teach.dnf_bond_integration import run_integration_check
from teach.dnf_bond_lesson import build_lesson
from teach.dummit_foote_graph import TARGET_NODE_ID
from teach.fact_checker import Verdict as FactVerdict


def test_lesson_crosses_the_boundary_clean():
    artifact = build_lesson()
    assert check_no_forbidden_fields(type(artifact)) == []
    assert not hasattr(artifact, "target_node_id")
    assert not hasattr(artifact, "traversal")
    assert not hasattr(artifact, "answer_key")


def test_checker_recovers_the_taught_concept_and_its_prerequisite():
    report = run_integration_check(build_lesson())
    assert report.recovery.taught_node_id == TARGET_NODE_ID
    assert report.recovery.assumed_prerequisite_ids == ("dummit-foote:3.1-cosets",)
    assert report.recovery.unsignposted_prerequisite_ids == ()


def test_checker_confirms_lagrange_and_finds_no_contradictions():
    report = run_integration_check(build_lesson())
    lagrange_checks = [fc for fc in report.fact_checks if fc.topic == "lagrange-order-divides"]
    assert any(fc.verdict is FactVerdict.CONFIRMED for fc in lagrange_checks)
    assert not any(fc.verdict is FactVerdict.CONTRADICTED for fc in report.fact_checks)


def test_checker_flags_no_dishonest_potential_claims():
    report = run_integration_check(build_lesson())
    assert report.potential_flags == ()


def test_potential_checker_coverage_gap_is_disclosed_not_hidden():
    """teach-yn8: 'zero flags' from the potential_checker must never be
    reported as 'no overpromises' on its own -- most of this lesson's
    tutor-spoken sentences (domain content and Bond narration, plus
    retrospective/procedural framing like 'you just handled...') are not
    potential claims the extractor's recognized-shape whitelist classifies
    at all. The report must say so explicitly, exactly like the
    fact_checker's out-of-scope disclosure above, rather than let an
    unqualified 'no claims flagged' imply every sentence was checked.

    teach-8xw.19 removed the vocabulary-gated 'is this about the learner'
    pre-filter that used to keep this count small (and, worse, that three
    successive widenings of -- teach-yn8, teach-kmm, teach-5gf -- each still
    left some phrasing of learner-directed praise invisible rather than
    unclassified). `seen` is now every tutor-spoken sentence in the lesson,
    not a heuristically-selected subset -- noisier, but nothing is invisible.

    teach-8xw.21: the exact sentence count is lesson prose length, not an
    honesty signal, so it is not pinned here -- it would break on any edit
    to the lesson text (a reworded definition, more Bond narration) that has
    nothing to do with potential claims. What's checked instead is the
    invariant this test is actually named for: every seen sentence lands in
    exactly one of classified/unclassified (nothing vanishes), coverage is
    non-empty (the teach-yn8 vacuous-pass failure mode), and exactly the one
    real potential claim in this lesson is classified.

    teach-8xw.20: with the gate gone, `unclassified` on this lesson is 31 of
    32 -- a number that would read almost the same on any lesson of similar
    length, regardless of content (see teach/potential_checker.py's
    `Coverage` docstring). The secondary `second_person_*` breakdown is
    checked here too: same subset invariant, and it must actually be a
    proper subset of `seen` on this real lesson (there IS third-person
    domain/Bond content this lesson contains that isn't second-person
    address), not a value that just mirrors `unclassified`."""
    report = run_integration_check(build_lesson())
    cov = report.potential_coverage
    assert len(cov.seen) > 0
    assert len(cov.seen) == len(cov.classified) + len(cov.unclassified)
    assert len(cov.classified) == 1
    assert len(cov.unclassified) > 0
    assert "unclassified" in report.render()
    assert len(cov.second_person_seen) == len(cov.second_person_classified) + len(
        cov.second_person_unclassified
    )
    assert 0 < len(cov.second_person_seen) < len(cov.seen), (
        "expected the second-person subset to be smaller than the full lesson on this "
        f"real lesson (second_person_seen={len(cov.second_person_seen)}, seen={len(cov.seen)})"
    )
    assert len(cov.second_person_unclassified) < len(cov.unclassified), (
        "the whole point of teach-8xw.20's secondary line: it must be a strictly smaller, "
        "more targeted list than the raw unclassified total"
    )
    assert "address the learner directly" in report.render()


def test_out_of_scope_coverage_is_disclosed_not_hidden():
    """teach-25o's kernel-normal-subgroup fact lives on 3.3, off this
    lesson's traversal to Lagrange -- the report must say so explicitly
    rather than silently reporting a clean pass that implies full coverage
    of teach.math_facts.MATH_SOURCE."""
    report = run_integration_check(build_lesson())
    assert report.out_of_scope_facts == ("kernel-normal-subgroup",)
