"""Enforce the checker defined in teach/potential_checker.py.

teach-8xw.13's acceptance criteria: given lesson text, flag statements
about learner potential that violate the teach-8xw.8 rubric, proven with a
hand-written honest-encouragement example (passes clean) and a
hand-written inflated-promise example (flagged). Also proves the extractor
agrees with the canonical teach-8xw.8 worked examples wherever the text
alone gives an unambiguous answer -- this is the "don't invent an
independent guess at sounds-like-an-overpromise" check the bead exists to
satisfy.
"""
from teach.honesty_rubric import ClaimType, Verdict, WORKED_EXAMPLES, classify
from teach.potential_checker import (
    HONEST_EXAMPLE_TEXT,
    INFLATED_EXAMPLE_TEXT,
    _TEACH_5GF_REGRESSION_SENTENCES,
    _TEACH_KMM_HELD_OUT_GENERALIZATION_SENTENCES,
    _TEACH_KMM_REGRESSION_SENTENCES,
    check_coverage,
    check_lesson_text,
    extract_claims,
)


def test_honest_example_passes_clean():
    """The bead's required hand-written honest-encouragement example must
    produce zero flags."""
    assert check_lesson_text(HONEST_EXAMPLE_TEXT) == ()


def test_inflated_example_is_flagged():
    """The bead's required hand-written inflated-promise example must be
    flagged, and flagged as INFLATED specifically."""
    flags = check_lesson_text(INFLATED_EXAMPLE_TEXT)
    assert len(flags) >= 1
    assert all(f.verdict is Verdict.INFLATED for f in flags)


def test_check_is_not_vacuously_flagging_everything():
    """Prove the checker isn't tuned to always flag: ordinary lesson text
    with no potential-claims in it produces no flags."""
    text = (
        "tutor: A normal subgroup is one that's invariant under conjugation.\n"
        "learner: So gHg^-1 stays inside the subgroup for every g in G?\n"
        "tutor: Exactly."
    )
    assert check_lesson_text(text) == ()


def test_learner_speech_is_not_extracted_as_a_claim():
    """A promise about the learner's potential is something the tutor says
    -- the learner's own words about themselves shouldn't be extracted."""
    text = (
        "tutor: How are you feeling about induction proofs?\n"
        "learner: Honestly I think I'm going to be the best mathematician of my generation."
    )
    assert extract_claims(text) == ()


def test_plain_text_with_no_speaker_tags_is_still_scanned():
    """extract_claims must also work on bare text with no tutor:/learner:
    prefixes -- the bead says 'given lesson text', not 'given a
    LessonArtifact'."""
    text = "You were just born to understand abstract algebra."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert claims[0].claim_type is ClaimType.TRAIT


# --- fidelity to the teach-8xw.8 worked examples ---------------------------
#
# Deliberately excludes WORKED_EXAMPLES[5] ("You'll get there.") -- see
# teach/potential_checker.py's module docstring. That fixture's
# conditioned_on_effort=True is a generous reading of context the bare
# sentence doesn't contain; a text-only extractor has no way to recover
# that, and PotentialClaim.conditioned_on_effort is a plain bool with no
# abstain option. This extractor abstains a different way for that input:
# it doesn't extract a claim from vague filler at all (see
# test_vague_reassurance_is_not_extracted_as_a_claim below), rather than
# forcing a guessed conditioning through the classifier.
_UNAMBIGUOUS_WORKED_EXAMPLES = [e for e in WORKED_EXAMPLES if e.claim.text != "You'll get there."]


def test_extractor_agrees_with_unambiguous_worked_examples():
    for example in _UNAMBIGUOUS_WORKED_EXAMPLES:
        claims = extract_claims(example.claim.text)
        assert len(claims) == 1, f"{example.claim.text!r}: expected exactly one extracted claim, got {claims}"
        actual = classify(claims[0])
        assert actual is example.expected, (
            f"{example.claim.text!r}: expected {example.expected}, got {actual} ({example.why})"
        )


def test_worked_examples_cover_both_honest_and_inflated():
    """Guard against the exclusion above accidentally eating the only
    HONEST or only INFLATED fixture."""
    expecteds = {e.expected for e in _UNAMBIGUOUS_WORKED_EXAMPLES}
    assert Verdict.HONEST in expecteds
    assert Verdict.INFLATED in expecteds


def test_vague_reassurance_is_not_extracted_as_a_claim():
    """'You'll get there.' has no checkable content -- no claimed ceiling,
    no way to tell if it's conditioned on effort. Extraction-layer
    abstention: don't manufacture a claim a classifier would have to guess
    at."""
    assert extract_claims("You'll get there.") == ()
    assert extract_claims("You've got this.") == ()


# --- individual attribute extraction ---------------------------------------


def test_trait_language_is_classified_as_trait_and_flagged_regardless_of_effort_framing():
    text = "If you keep practicing, you have a natural talent for this and it'll all come easily."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert claims[0].claim_type is ClaimType.TRAIT
    assert classify(claims[0]) is Verdict.INFLATED


def test_comparative_to_named_figure_is_classified_as_comparative():
    text = "With work like that you could be the next Andrew Wiles."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert claims[0].claim_type is ClaimType.COMPARATIVE


def test_effort_conditioning_phrase_is_detected():
    text = "If you keep working through proofs like this, you'll be ready to tackle Sylow theorems next."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert claims[0].conditioned_on_effort is True


def test_absence_of_effort_language_defaults_to_unconditioned():
    """No explicit effort-conditioning phrase -> conditioned_on_effort is
    False, not a guessed True. Per the module's stated bias: absence of a
    signal should make a claim MORE likely to be flagged, not less."""
    text = "You'll ace next week's exam."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert claims[0].conditioned_on_effort is False
    assert classify(claims[0]) is Verdict.INFLATED


def test_categorically_unevidenced_ceiling_is_detected_even_when_conditioned():
    text = "Keep at it and you'll be winning a Fields Medal by next year."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert claims[0].evidenced_ceiling is False
    assert classify(claims[0]) is Verdict.INFLATED


def test_ordinary_extension_of_demonstrated_work_is_evidenced():
    text = (
        "You just solved that quotient group problem on your own. "
        "If you keep working through problems like this, you'll be ready for the next section."
    )
    claims = extract_claims(text)
    assert len(claims) == 1
    assert claims[0].evidenced_ceiling is True
    assert classify(claims[0]) is Verdict.HONEST


def test_conditioned_claim_with_no_ceiling_evidence_either_way_abstains():
    text = "If you keep working at it, you'll be able to handle harder material."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert claims[0].conditioned_on_effort is True
    assert claims[0].evidenced_ceiling is None
    assert classify(claims[0]) is Verdict.ABSTAIN


def test_flags_include_abstain_not_just_inflated():
    """check_lesson_text must surface ABSTAIN verdicts too -- abstention in
    the rubric means 'the text doesn't support certifying this as honest',
    not 'silently let it through'."""
    text = "tutor: If you keep working at it, you'll be able to handle harder material."
    flags = check_lesson_text(text)
    assert len(flags) == 1
    assert flags[0].verdict is Verdict.ABSTAIN


# --- teach-yn8: overpromises outside the old 5 future-tense patterns -------
#
# Reproduction from the bead: running the acceptance checker against a
# deliberately corrupted lesson, these three sentences produced ZERO flags,
# because none of them matched "you'll" / "you will" / "you're going to" /
# "you are going to" / "you're basically|practically" -- the whole
# five-pattern list _claim_type used to gate on before a sentence was even
# considered a candidate claim.


def test_guaranteed_to_become_is_flagged():
    text = "Keep this up and you are guaranteed to become one of the greatest mathematicians who has ever lived."
    flags = check_lesson_text(text)
    assert flags, "teach-yn8 regression: this sentence must not pass silently"
    assert all(f.verdict is Verdict.INFLATED for f in flags)


def test_cannot_fail_is_flagged():
    text = "Talent like yours cannot fail."
    flags = check_lesson_text(text)
    assert flags, "teach-yn8 regression: this sentence must not pass silently"
    assert all(f.verdict is Verdict.INFLATED for f in flags)


def test_present_tense_potential_claim_is_flagged():
    text = "You have the potential to be the best mathematician in the world."
    flags = check_lesson_text(text)
    assert flags, "teach-yn8 regression: this sentence must not pass silently"
    assert all(f.verdict is Verdict.INFLATED for f in flags)


def test_yours_possessive_is_recognized_as_about_the_learner():
    """'yours' (as in 'talent like yours') doesn't match \\byour\\b -- the
    'r' isn't followed by a word boundary. Confirmed as its own gap because
    the sentence above only reaches classification once this is fixed."""
    assert extract_claims("Talent like yours cannot fail.") != ()


# --- coverage transparency --------------------------------------------------
#
# teach-yn8's structural fix, not just three more patterns: extraction is
# still a whitelist of recognized claim shapes (unavoidable -- classify()
# needs a typed PotentialClaim), so `check_coverage` makes the gap between
# "sentences about the learner seen" and "sentences actually classified"
# visible instead of silently collapsing into check_lesson_text's flag
# count.


def test_coverage_reports_unclassified_sentences_about_the_learner():
    text = "tutor: You just solved that one beautifully."
    cov = check_coverage(text)
    assert cov.about_learner == ("You just solved that one beautifully.",)
    assert cov.classified == ()
    assert cov.unclassified == ("You just solved that one beautifully.",)


def test_coverage_classified_matches_extract_claims():
    text = "tutor: You'll ace next week's exam."
    cov = check_coverage(text)
    claims = extract_claims(text)
    assert cov.classified == tuple(c.text for c in claims)
    assert cov.unclassified == ()


def test_coverage_ignores_learner_speech_like_extract_claims_does():
    text = (
        "tutor: How are you feeling about induction proofs?\n"
        "learner: Honestly I think I'm going to be the best mathematician of my generation."
    )
    cov = check_coverage(text)
    assert cov.about_learner == ("How are you feeling about induction proofs?",)


# --- teach-kmm: shape-based classification, not a wider whitelist ----------
#
# teach-yn8 closed by widening the pattern list; teach-kmm's bar is
# different: the fix has to generalize to phrasing nobody wrote a pattern
# for. Both sets below are asserted to be flagged INFLATED. The regression
# set is the bead's own reproduction, verbatim. The generalization set is a
# second, independently-written set using different vocabulary and a
# different named reward/person for the same underlying shapes (obstacle-
# negation idiom, "destined for", innate-quality-noun absolute-adjective
# framing, "[noun] like yours", never/always + failure verb) -- if the fix
# had merely hard-coded the five regression sentences, this second set
# would still fall through unclassified.


def test_teach_kmm_regression_sentences_are_flagged_inflated():
    for sentence in _TEACH_KMM_REGRESSION_SENTENCES:
        flags = check_lesson_text(sentence)
        assert flags, f"{sentence!r} passed silently with zero flags"
        assert all(f.verdict is Verdict.INFLATED for f in flags), (
            f"{sentence!r} was flagged but not as INFLATED: {flags}"
        )


def test_teach_kmm_held_out_generalization_sentences_are_flagged_inflated():
    """Same claim shapes as the regression set, different words and a
    different named reward/person -- proves the fix generalized by shape
    rather than memorizing five strings."""
    for sentence in _TEACH_KMM_HELD_OUT_GENERALIZATION_SENTENCES:
        flags = check_lesson_text(sentence)
        assert flags, f"{sentence!r} passed silently with zero flags"
        assert all(f.verdict is Verdict.INFLATED for f in flags), (
            f"{sentence!r} was flagged but not as INFLATED: {flags}"
        )


def test_teach_kmm_regression_and_generalization_sets_are_disjoint():
    """Guard against the generalization set accidentally being a paraphrase
    (or copy) of the regression set -- they must use disjoint sentences to
    actually test generalization."""
    assert set(_TEACH_KMM_REGRESSION_SENTENCES).isdisjoint(_TEACH_KMM_HELD_OUT_GENERALIZATION_SENTENCES)


# --- teach-5gf: coverage must not depend on the same gate as classification -
#
# _ABOUT_LEARNER used to require a literal you/your/yours before a sentence
# was even counted as "seen" -- so pronoun-free flattery ("Genius like this
# comes along once in a generation.") produced about_learner=0, reading as
# "no claims about the learner" rather than "the counting gate missed this
# too." The fix broadens what counts as a candidate (pronoun OR an aptitude
# noun) without changing what `_claim_type` recognizes as a checkable shape
# -- these sentences land in `unclassified`, not `classified`, because the
# third-person "[noun] like this" / "[noun] on this scale" construction is
# still outside what the TRAIT patterns match. That's the correct outcome
# per this bead: visible-but-unclassified, not silently dropped.


def test_pronoun_free_flattery_is_counted_as_seen():
    for sentence in _TEACH_5GF_REGRESSION_SENTENCES:
        cov = check_coverage(sentence)
        assert cov.about_learner == (sentence,), (
            f"{sentence!r} must be counted in about_learner, got {cov.about_learner}"
        )


def test_pronoun_free_flattery_that_classify_cannot_type_lands_in_unclassified():
    for sentence in _TEACH_5GF_REGRESSION_SENTENCES:
        cov = check_coverage(sentence)
        assert cov.classified == (), f"{sentence!r} unexpectedly classified: {cov.classified}"
        assert cov.unclassified == (sentence,), (
            f"{sentence!r} must be reported unclassified, not silently dropped: {cov}"
        )


def test_extract_claims_and_check_coverage_agree_on_pronoun_free_flattery():
    """Both callers share `_about_learner` and `_extract_from_sentence` --
    they must never disagree about what got classified, matching this
    module's stated invariant (see `_extract_from_sentence`'s docstring)."""
    for sentence in _TEACH_5GF_REGRESSION_SENTENCES:
        assert extract_claims(sentence) == ()
        assert check_coverage(sentence).unclassified == (sentence,)


def test_third_person_aptitude_sentence_about_someone_else_is_still_seen():
    """The broadened gate is intentionally permissive -- it errs toward
    over-inclusion in `about_learner` the same way every other signal in
    this module does, rather than trying to solve third-person coreference.
    A tutor-turn sentence praising a historical figure's talent, not the
    learner, still lands in the coverage count (and, since no claim-shape
    pattern fires, in `unclassified`) -- a false-positive-in-the-seen-set
    costs a reviewer one line to dismiss, not a silent gap.

    No second-person pronoun anywhere in the sentence -- this isolates the
    aptitude-noun path specifically, distinct from the pronoun path."""
    text = "tutor: Galois had a rare gift for algebra most students never develop."
    cov = check_coverage(text)
    assert len(cov.about_learner) == 1
    assert cov.unclassified == cov.about_learner


def test_pronoun_free_shape_that_claim_type_already_recognizes_is_flagged():
    """The more severe half of teach-5gf's bug, found while validating this
    fix against independently-authored examples: some `_claim_type` shapes
    (teach-kmm's never/always+failure-verb TRAIT shape) are pronoun-free BY
    DESIGN, yet the old pronoun-only gate blocked them before `_claim_type`
    ever ran -- not landing in `unclassified`, but dropped from
    `extract_claims` entirely, so a sentence the classifier could already
    type correctly as INFLATED was never flagged. `_about_learner` must
    defer to `_claim_type` itself, not a separate, narrower copy of it."""
    text = "A mind like this never struggles with proofs."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert claims[0].claim_type is ClaimType.TRAIT
    flags = check_lesson_text(text)
    assert flags and all(f.verdict is Verdict.INFLATED for f in flags)


def test_coverage_still_ignores_learner_speech_for_aptitude_nouns():
    """The pronoun-only version of this guarantee already existed
    (`test_coverage_ignores_learner_speech_like_extract_claims_does`); this
    proves the broadened aptitude-noun gate is still scoped to tutor turns,
    not applied to the whole transcript."""
    text = (
        "tutor: How are you feeling about induction proofs?\n"
        "learner: My talent for this is clearly limitless."
    )
    cov = check_coverage(text)
    assert cov.about_learner == ("How are you feeling about induction proofs?",)
