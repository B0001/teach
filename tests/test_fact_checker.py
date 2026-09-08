"""Enforce the checker defined in teach/fact_checker.py against the math
domain source in teach/math_facts.py.

teach-8xw.11's acceptance criteria: a fact-checking pass that takes an
asserted claim from lesson text and a reference source and returns
confirmed / contradicted / cannot-verify, proven with a hand-written true
claim, a hand-written false claim, and an ambiguous claim that should
abstain.
"""
from teach.fact_checker import (
    Verdict,
    check_lesson_text,
    extract_domain_claims,
    verify_claim,
)
from teach.math_facts import (
    AMBIGUOUS_CLAIM,
    FALSE_CLAIM,
    MATH_SOURCE,
    TRUE_CLAIM,
)


def test_true_claim_is_confirmed():
    assert verify_claim(TRUE_CLAIM, MATH_SOURCE) is Verdict.CONFIRMED


def test_false_claim_is_contradicted():
    assert verify_claim(FALSE_CLAIM, MATH_SOURCE) is Verdict.CONTRADICTED


def test_ambiguous_claim_abstains():
    assert verify_claim(AMBIGUOUS_CLAIM, MATH_SOURCE) is Verdict.CANNOT_VERIFY


def test_off_topic_claim_cannot_verify_not_confirmed():
    """A sentence the source has nothing on at all must abstain, not be
    silently treated as fine. This is the "topic not covered" flavor of
    CANNOT_VERIFY, distinct from the "topic covered, wording unclear"
    flavor AMBIGUOUS_CLAIM exercises."""
    assert (
        verify_claim("Cosets partition a group into equal-sized pieces.", MATH_SOURCE)
        is Verdict.CANNOT_VERIFY
    )


def test_false_beats_true_when_a_sentence_matches_both():
    """A sentence that trips both a true- and a false-pattern must resolve
    CONTRADICTED, not CONFIRMED -- false_patterns are checked first by
    design, biasing toward surfacing a problem rather than silently
    clearing it."""
    sentence = (
        "The kernel of a homomorphism is always a normal subgroup, "
        "but it is not a normal subgroup of the codomain."
    )
    assert verify_claim(sentence, MATH_SOURCE) is Verdict.CONTRADICTED


def test_lagrange_true_claim_confirmed():
    claim = "In a finite group, the order of any subgroup divides the order of the group."
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONFIRMED


def test_lagrange_reversed_direction_is_contradicted():
    """The converse-direction misstatement (order of the group dividing the
    order of the subgroup, backwards from what Lagrange's theorem says) is
    a specific, catchable false claim -- not the same as the converse-of-
    Lagrange claim (subgroup order dividing group order implies a subgroup
    of that order exists), which this source does not cover at all."""
    claim = "The order of the finite group divides the order of the subgroup."
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONTRADICTED


def test_converse_of_lagrange_is_a_different_uncovered_topic():
    """This source states only the forward direction of Lagrange's theorem.
    A converse-shaped claim (order divides implies a subgroup of that order
    exists -- famously false, e.g. A4 has no subgroup of order 6) is not
    something this fact's patterns were built to adjudicate, so it must
    abstain rather than accidentally matching as confirmed or contradicted."""
    claim = "Since 6 divides 12, a group of order 12 must have a subgroup of order 6."
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CANNOT_VERIFY


def test_check_lesson_text_only_reports_recognized_topics():
    text = (
        "tutor: Let's warm up -- how was your day?\n"
        "learner: Pretty good, thanks.\n"
        "tutor: The kernel of a homomorphism is always a normal subgroup of the domain."
    )
    checks = check_lesson_text(text, MATH_SOURCE)
    assert len(checks) == 1
    assert checks[0].verdict is Verdict.CONFIRMED
    assert checks[0].topic == "kernel-normal-subgroup"


def test_check_lesson_text_ignores_learner_speech():
    """A domain fact is something the tutor asserts to the learner; a wrong
    claim in the learner's own words (e.g. a guess being tested) is not the
    system making a factual claim and shouldn't be checked the same way."""
    text = (
        "tutor: What do you think -- is the kernel normal in the codomain?\n"
        "learner: The kernel of a homomorphism is a normal subgroup of the codomain."
    )
    checks = check_lesson_text(text, MATH_SOURCE)
    assert checks == ()


def test_check_lesson_text_reports_cannot_verify_sentences_too():
    """Coverage accounting: a recognized-topic sentence the checker can't
    adjudicate must still show up in the results as CANNOT_VERIFY, not be
    dropped -- dropping it would make "0 flags" indistinguishable from
    "nothing to check.\""""
    text = f"tutor: {AMBIGUOUS_CLAIM}"
    checks = check_lesson_text(text, MATH_SOURCE)
    assert len(checks) == 1
    assert checks[0].verdict is Verdict.CANNOT_VERIFY


def test_plain_text_with_no_speaker_tags_is_still_scanned():
    checks = check_lesson_text(TRUE_CLAIM, MATH_SOURCE)
    assert len(checks) == 1
    assert checks[0].verdict is Verdict.CONFIRMED


def test_extract_domain_claims_filters_to_recognized_topics():
    text = (
        "tutor: Nice work today. The kernel of a homomorphism is always a "
        "normal subgroup of the domain. Let's take a break."
    )
    claims = extract_domain_claims(text, MATH_SOURCE)
    assert len(claims) == 1
    assert "kernel" in claims[0].lower()


def test_extract_domain_claims_empty_when_nothing_recognized():
    text = "tutor: Great session -- see you next time!"
    assert extract_domain_claims(text, MATH_SOURCE) == ()
