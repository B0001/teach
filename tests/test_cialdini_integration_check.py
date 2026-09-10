"""teach-8xw.31's own acceptance test: the Cialdini/Pre-Suasion layer, run
for real through teach.potential_checker (which itself calls
teach.honesty_rubric.classify on everything it extracts), and the actual
result checked -- not assumed.
"""
from teach.boundary import check_no_forbidden_fields
from teach.cialdini_integration_check import (
    _TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES,
    build_demo_lesson,
    run_check,
)
from teach.honesty_rubric import Verdict


def test_demo_lesson_crosses_the_boundary_clean():
    artifact = build_demo_lesson()
    assert check_no_forbidden_fields(type(artifact)) == []


def test_demo_lesson_passes_the_real_honesty_checker_clean():
    report = run_check()
    assert report.lesson_flags == ()


def test_demo_lesson_coverage_is_not_vacuous():
    """The teach-yn8 failure mode: a clean result over zero classified
    claims is silence, not a passed check. At least one of the seven
    principle-rendered turns must actually reach the honesty rubric."""
    report = run_check()
    cov = report.lesson_coverage
    assert len(cov.seen) == len(cov.classified) + len(cov.unclassified)
    assert len(cov.classified) > 0


def test_every_principle_individually_passes_the_real_checker_clean():
    report = run_check()
    for name, flags in report.per_principle_flags.items():
        assert flags == (), f"{name}: expected no flags, got {flags}"


def test_naive_social_proof_contrast_is_the_confirmed_teach_8xw_32_gap():
    """Side-by-side measurement: teach-8xw.32's own confirmed-blind
    sentence (imported verbatim, not re-authored) is the shape
    teach.cialdini.render_social_proof was deliberately built not to
    produce. This does not re-measure teach-8xw.32's finding -- it
    confirms the contrast still holds against the real, unmodified checker."""
    report = run_check()
    assert report.naive_social_proof_sentence == _TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES[0]
    assert report.naive_social_proof_flags == ()
    assert report.naive_social_proof_coverage.classified == ()
    assert report.naive_social_proof_coverage.unclassified == (report.naive_social_proof_sentence,)


def test_honesty_rubric_verdicts_reachable_from_generated_text():
    """Confirms teach.honesty_rubric.classify (via potential_checker) is
    actually exercised against this bead's generated text, not just its own
    worked examples -- the specific gap the bead names as never having
    happened before this bead."""
    from teach.potential_checker import extract_claims

    report = run_check()
    claims = extract_claims(build_demo_lesson().text)
    assert len(claims) > 0
    from teach.honesty_rubric import classify

    verdicts = {classify(c) for c in claims}
    assert verdicts <= {Verdict.HONEST, Verdict.ABSTAIN, Verdict.INFLATED}
    assert Verdict.HONEST in verdicts
