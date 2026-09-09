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
    reported as 'no overpromises' on its own -- this lesson has five
    about-learner sentences (retrospective/procedural framing, e.g. 'you
    just handled...') that the extractor's recognized-shape whitelist does
    not classify as potential claims at all. The report must say so
    explicitly, exactly like the fact_checker's out-of-scope disclosure
    above, rather than let an unqualified 'no claims flagged' imply every
    about-learner sentence was checked."""
    report = run_integration_check(build_lesson())
    cov = report.potential_coverage
    assert len(cov.about_learner) == 6
    assert len(cov.classified) == 1
    assert len(cov.unclassified) == 5
    assert "unclassified" in report.render()


def test_out_of_scope_coverage_is_disclosed_not_hidden():
    """teach-25o's kernel-normal-subgroup fact lives on 3.3, off this
    lesson's traversal to Lagrange -- the report must say so explicitly
    rather than silently reporting a clean pass that implies full coverage
    of teach.math_facts.MATH_SOURCE."""
    report = run_integration_check(build_lesson())
    assert report.out_of_scope_facts == ("kernel-normal-subgroup",)
