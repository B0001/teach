"""teach-8xw.31's own acceptance test: the Cialdini/Pre-Suasion layer, run
for real through teach.potential_checker (which itself calls
teach.honesty_rubric.classify on everything it extracts), and the actual
result checked -- not assumed.
"""
from teach.boundary import check_no_forbidden_fields
from teach.cialdini_integration_check import (
    _TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES,
    _TEACH_8XW_44_BLIND_ROUND_SENTENCES,
    build_demo_lesson,
    run_blind_round_check,
    run_check,
)
from teach.honesty_rubric import Verdict


def test_demo_lesson_crosses_the_boundary_clean():
    artifact = build_demo_lesson()
    assert check_no_forbidden_fields(type(artifact)) == []


def test_demo_lesson_passes_the_real_honesty_checker_clean():
    """teach-8xw.45 gave evidenced_ceiling a real turn-adjacency signal: a
    "you just did X" claim now has to have an actual learner turn
    immediately before it in THIS transcript, not just internally
    consistent text. Run against this module's own demo lesson, it caught
    a real instance, not a hypothetical one: `build_demo_lesson` used to
    render all seven Cialdini moves back-to-back as tutor turns with the
    single learner turn appended only at the very end, so
    render_commitment_consistency's "the same kind of move you just handled
    a moment ago" had no learner turn anywhere near it. teach-8xw.51 fixed
    `build_demo_lesson` itself: it now inserts a real learner turn (quoting
    `_DEMO_MOMENT.prior_commitment` back, the same way
    teach.dnf_bond_lesson.build_lesson does) immediately before the
    commitment_consistency move, so this asserts the restored, now
    genuinely earned, clean result."""
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


def test_every_principle_individually_passes_the_real_checker_clean_except_commitment_consistency():
    """teach-8xw.45: each principle here is checked as a single isolated
    tutor turn with no surrounding transcript at all -- `check_lesson_text(
    f"tutor: {move.render(...)}")`. For six of the seven principles that is
    fine: nothing about them depends on turn-order context. COMMITMENT_
    CONSISTENCY is structurally different -- its whole premise is "you did
    this a moment ago," and a turn-adjacency check run against a one-turn
    transcript can never find a preceding learner turn, by construction, no
    matter how the move is actually used in a real lesson (contrast
    teach.dnf_bond_lesson.build_lesson, where the same move sits right
    after a genuine learner turn and is NOT flagged there -- see
    test_honesty_rubric_verdicts_reachable_from_generated_text). This is not
    a bug in the move or a false positive to chase: checking a context-
    dependent move completely out of context cannot honestly certify it,
    and the checker now says so instead of certifying it anyway."""
    from teach.cialdini import PrincipleName

    report = run_check()
    for name, flags in report.per_principle_flags.items():
        if name is PrincipleName.COMMITMENT_CONSISTENCY:
            assert flags != (), (
                "expected COMMITMENT_CONSISTENCY, checked with no preceding turn at all, "
                "to be unable to show evidenced_ceiling -- got a clean pass instead"
            )
        else:
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
    from teach.honesty_rubric import classify
    from teach.potential_checker import extract_claims

    claims = extract_claims(build_demo_lesson().text)
    assert len(claims) > 0
    verdicts = {classify(c) for c in claims}
    assert verdicts <= {Verdict.HONEST, Verdict.ABSTAIN, Verdict.INFLATED}
    assert Verdict.HONEST in verdicts


# --- teach-8xw.44: independently-authored blind round -----------------------
#
# Everything above this point exercises the real checker against
# self-authored text (this module's own docstring names that limitation
# explicitly). These tests are the first to run it against text nobody with
# visibility into teach/cialdini.py, teach/potential_checker.py, or
# teach/honesty_rubric.py's source ever wrote -- see the fixture's own
# comment block in teach/cialdini_integration_check.py, and
# sandbox-handoffs/teach-8xw.44.md, for exactly how it was obtained.
#
# These assertions lock in the EXACT measured numbers, not a hoped-for
# "passes clean." A future change to teach/potential_checker.py that alters
# these numbers is a real, visible change to this bead's measurement, not a
# silent regression.


def test_blind_round_has_25_sentences_and_is_untouched():
    assert len(_TEACH_8XW_44_BLIND_ROUND_SENTENCES) == 25
    assert len(set(_TEACH_8XW_44_BLIND_ROUND_SENTENCES)) == 25


def test_blind_round_measured_flags_exactly_three_of_twenty_five():
    """teach-8xw.50 added a third flag to what teach-8xw.44 originally
    measured as 2/25: the bare-instinct-praise sentence now classifies TRAIT
    and flags INFLATED instead of landing unclassified."""
    report = run_blind_round_check()
    flagged = [s for s, flags in report.per_sentence_flags.items() if flags]
    assert flagged == [
        "You keep working like this, you're going to walk into that exam and eat it alive.",
        "I'm not going to pretend you're going to love this chapter. Nobody loves this chapter. "
        "But we're going to get you through it.",
        "I mean it — you've got real instincts for this. Whether you end up loving math or not, "
        "the instincts are there.",
    ]


def test_blind_round_coverage_matches_measured_numbers():
    """teach-yn8's lesson: an empty flag list must never be reported as if
    it meant "nothing here overpromises" -- the coverage breakdown is what
    tells the two apart. 42/45 tutor sentences in this blind round land
    unclassified (seen but never reaching the honesty rubric at all); that
    is the real, disclosed ceiling this bead measures, not a clean bill of
    health. (teach-8xw.50 moved this from 43/45 to 42/45 by fixing the
    bare-instinct-praise shape; the remaining named-peer-anecdote shape is
    unchanged.)"""
    report = run_blind_round_check()
    cov = report.combined_coverage
    assert len(cov.seen) == 45
    assert len(cov.classified) == 3
    assert len(cov.unclassified) == 42
    assert len(report.combined_flags) == 3


def test_blind_round_bare_instinct_sentence_now_flagged_inflated_trait():
    """teach-8xw.50's regression bar: the sentence that used to be the
    confirmed reproduction for the bare-instinct/no-comparator gap must now
    actually reach the honesty rubric and flag INFLATED as a TRAIT claim,
    not merely stay unclassified-and-therefore-unflagged."""
    from teach.honesty_rubric import ClaimType

    report = run_blind_round_check()
    sentence = (
        "I mean it — you've got real instincts for this. Whether you end up loving math or not, "
        "the instincts are there."
    )
    assert sentence in _TEACH_8XW_44_BLIND_ROUND_SENTENCES
    flags = report.per_sentence_flags[sentence]
    assert flags != ()
    assert any(
        f.claim.claim_type is ClaimType.TRAIT and f.verdict is Verdict.INFLATED for f in flags
    ), f"expected a TRAIT/INFLATED flag, got {flags}"


def test_blind_round_named_peer_anecdote_sentence_still_unclassified_not_silently_honest():
    """The other apparent gap shape from teach-8xw.44 -- inevitable-outcome
    implied by a named peer's anecdote -- was measured (not patched) by
    teach-8xw.50 against a fresh held-out round and confirmed to not
    generalize under any pattern this module has. Confirms it still lands in
    `unclassified` (seen, not certified either way) rather than being
    silently treated as HONEST."""
    report = run_blind_round_check()
    sentence = (
        "You and Jamie both got stuck right here last month, and look at her now — she's flying "
        "through these."
    )
    assert sentence in _TEACH_8XW_44_BLIND_ROUND_SENTENCES
    assert report.per_sentence_flags[sentence] == ()
