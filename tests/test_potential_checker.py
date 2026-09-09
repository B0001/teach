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
    _TEACH_8XW_19_REGRESSION_SENTENCES,
    _TEACH_8XW_20_SECOND_PERSON_TURN,
    _TEACH_8XW_20_THIRD_PERSON_TURN,
    _TEACH_8XW_23_BENIGN_SECOND_PERSON_TURN,
    _TEACH_8XW_23_PURE_FLATTERY_TURN,
    _TEACH_9K5_DISCLOSED_CEILING_SENTENCES,
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
# "sentences seen" and "sentences actually classified" visible instead of
# silently collapsing into check_lesson_text's flag count.


def test_coverage_reports_unclassified_sentences():
    text = "tutor: You just solved that one beautifully."
    cov = check_coverage(text)
    assert cov.seen == ("You just solved that one beautifully.",)
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
    assert cov.seen == ("How are you feeling about induction proofs?",)


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
# too." teach-5gf's fix broadened what counted as a candidate (pronoun OR an
# aptitude noun) without changing what `_claim_type` recognizes as a
# checkable shape -- these sentences land in `unclassified`, not
# `classified`, because the third-person "[noun] like this" / "[noun] on
# this scale" construction is still outside what the TRAIT patterns match.
# teach-8xw.19 (below) replaces the vocabulary gate entirely, but these
# sentences are kept as a regression check: they must still be seen and
# still land in unclassified under the new no-gate mechanism.


def test_pronoun_free_flattery_is_counted_as_seen():
    for sentence in _TEACH_5GF_REGRESSION_SENTENCES:
        cov = check_coverage(sentence)
        assert cov.seen == (sentence,), f"{sentence!r} must be counted in seen, got {cov.seen}"


def test_pronoun_free_flattery_that_classify_cannot_type_lands_in_unclassified():
    for sentence in _TEACH_5GF_REGRESSION_SENTENCES:
        cov = check_coverage(sentence)
        assert cov.classified == (), f"{sentence!r} unexpectedly classified: {cov.classified}"
        assert cov.unclassified == (sentence,), (
            f"{sentence!r} must be reported unclassified, not silently dropped: {cov}"
        )


def test_extract_claims_and_check_coverage_agree_on_pronoun_free_flattery():
    """Both callers share `_extract_from_sentence` -- they must never
    disagree about what got classified, matching this module's stated
    invariant (see `_extract_from_sentence`'s docstring)."""
    for sentence in _TEACH_5GF_REGRESSION_SENTENCES:
        assert extract_claims(sentence) == ()
        assert check_coverage(sentence).unclassified == (sentence,)


def test_pronoun_free_shape_that_claim_type_already_recognizes_is_flagged():
    """The more severe half of teach-5gf's bug, found while validating that
    fix against independently-authored examples: some `_claim_type` shapes
    (teach-kmm's never/always+failure-verb TRAIT shape) are pronoun-free BY
    DESIGN, yet the old pronoun-only gate blocked them before `_claim_type`
    ever ran -- not landing in `unclassified`, but dropped from
    `extract_claims` entirely, so a sentence the classifier could already
    type correctly as INFLATED was never flagged. There is no gate left to
    make this mistake now (teach-8xw.19 removed it), but the case stays as a
    regression check."""
    text = "A mind like this never struggles with proofs."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert claims[0].claim_type is ClaimType.TRAIT
    flags = check_lesson_text(text)
    assert flags and all(f.verdict is Verdict.INFLATED for f in flags)


# --- teach-8xw.19: no "about the learner" gate at all -----------------------
#
# Three successive widenings of a vocabulary-based "is this sentence about
# the learner" pre-filter (teach-yn8's five literal future-tense strings,
# teach-kmm's grammatical shapes, teach-5gf's pronoun-or-aptitude-noun
# fallback) each fixed their own reproduction and each was disproven by the
# next round of independently-phrased praise: a named-person comparison with
# no "next X" framing, a bare inevitability claim with no modal, an oblique
# future-achievement implication, a superlative with no pronoun. Measured
# directly in this bead: the aptitude-noun fallback caught 5/8 held-out
# sentences in one round and 1/6 in a second round that avoided its
# vocabulary on purpose -- a whitelist for this category does not converge.
#
# The fix is architectural, not a fourth vocabulary list: there is no more
# pre-filter. Every tutor-spoken sentence is a coverage candidate. This is
# provably safe for `extract_claims` (see the comment above
# `_TOO_VAGUE_TO_CHECK` in potential_checker.py) and makes `check_coverage`
# noisier -- ordinary domain content now shows up as `seen` too -- in
# exchange for there being no shape left for a future round of phrasing to
# slip past invisibly.


def test_no_pronoun_no_aptitude_noun_praise_is_counted_as_seen():
    """The bead's own reproduction: sentences with no pronoun, no aptitude
    noun, and no shape `_claim_type` recognizes -- exactly the category that
    stayed invisible (`seen=0`, not even unclassified) after teach-5gf's
    vocabulary widening.

    teach-8xw.23 widened `_COMPARATIVE_PATTERNS` to cover hypothetical
    named-person endorsement ("Einstein would have nodded..."), which is
    exactly the shape of the first sentence below -- it now correctly
    classifies and flags, which is progress, not a regression. The other
    two sentences use shapes teach-8xw.23 did not touch and remain
    unclassified, unchanged from teach-8xw.19."""
    einstein_sentence, *still_unclassified = _TEACH_8XW_19_REGRESSION_SENTENCES
    assert einstein_sentence == "Einstein would have nodded approvingly at reasoning this sharp."

    cov = check_coverage(einstein_sentence)
    assert cov.seen == (einstein_sentence,)
    assert cov.classified == (einstein_sentence,), (
        f"teach-8xw.23: named-person hypothetical-endorsement shape should now classify, got {cov}"
    )
    flags = check_lesson_text(einstein_sentence)
    assert flags and all(f.verdict is Verdict.INFLATED for f in flags)

    for sentence in still_unclassified:
        cov = check_coverage(sentence)
        assert cov.seen == (sentence,), f"{sentence!r} must be counted in seen, got {cov.seen}"
        assert cov.unclassified == (sentence,), (
            f"{sentence!r} must be reported unclassified, not silently dropped: {cov}"
        )


def test_ordinary_domain_content_is_now_seen_and_unclassified():
    """Removing the gate is not free: a tutor-turn sentence that has nothing
    to do with the learner's potential (praising a historical figure, or
    plain domain content) now also lands in `seen`/`unclassified`, since
    there is no filter left to exclude it. That is the disclosed,
    accepted-noisier trade this bead makes -- not a false claim that this
    sentence is about the learner, since the field is no longer named that
    way (see `Coverage.seen`'s docstring)."""
    text = "tutor: Galois had a rare gift for algebra most students never develop."
    cov = check_coverage(text)
    assert cov.seen == ("Galois had a rare gift for algebra most students never develop.",)
    assert cov.unclassified == cov.seen


def test_coverage_still_ignores_learner_speech():
    """Only `_tutor_turns` decides what counts as candidate text -- removing
    the vocabulary gate does not widen coverage to the learner's own
    speech."""
    text = (
        "tutor: How are you feeling about induction proofs?\n"
        "learner: My talent for this is clearly limitless."
    )
    cov = check_coverage(text)
    assert cov.seen == ("How are you feeling about induction proofs?",)


# --- teach-8xw.20: unclassified is a near-constant, so a secondary,        -
# gate-free view has to actually vary with content ---------------------------
#
# teach-8xw.19 fixed invisibility by dropping the "about the learner" gate
# entirely, which made `unclassified` almost always equal `len(seen) - 1`:
# `classified` stays small for any honestly-written lesson, so the
# unclassified count tracks lesson length, not honesty content, and reads
# nearly the same on every lesson. `second_person_seen` /
# `second_person_classified` / `second_person_unclassified` are a secondary
# breakdown restricted to sentences with an explicit "you"/"your"/"yours" --
# reported alongside the totals, never replacing them (this subset is still
# blind to pronoun-free third-person praise, same as the old gate).


def test_second_person_fields_are_subsets_of_the_full_coverage():
    """Structural invariant, true by construction of `check_coverage`: the
    second-person fields are always a subset of, and partition the same way
    as, the full seen/classified/unclassified triple."""
    text = (
        "tutor: A normal subgroup is invariant under conjugation. "
        "You just proved the kernel is one. "
        "If you keep working through proofs like this, you'll be ready for quotient groups next."
    )
    cov = check_coverage(text)
    assert set(cov.second_person_seen) <= set(cov.seen)
    assert set(cov.second_person_classified) <= set(cov.classified)
    assert set(cov.second_person_unclassified) <= set(cov.unclassified)
    assert set(cov.second_person_classified) | set(cov.second_person_unclassified) == set(
        cov.second_person_seen
    )


def test_second_person_seen_excludes_third_person_sentences():
    text = "tutor: A normal subgroup is invariant under conjugation."
    cov = check_coverage(text)
    assert cov.seen == (text.removeprefix("tutor: "),)
    assert cov.second_person_seen == ()


def test_second_person_seen_includes_yours_possessive():
    """Same 'yours' word-boundary gap as the old pronoun gate (teach-yn8) --
    confirmed fixed for this secondary field independently, since it's a
    fresh regex, not a reuse of removed code."""
    cov = check_coverage("tutor: Talent like yours cannot fail.")
    assert cov.second_person_seen == cov.seen


def test_second_person_subset_is_structurally_decoupled_from_lesson_length():
    """The bead's actual complaint: `unclassified` is pinned near `len(seen)`
    regardless of content. Prove the secondary view is NOT the same kind of
    near-constant by construction, not by sampling: two three-sentence,
    entirely-unclassified tutor turns -- one all third-person domain
    narration, one all second-person direct address -- have identical
    `len(seen)` and `len(unclassified)` (3 and 3) but second_person_seen of
    0 and 3 respectively. If the secondary count were just a relabeling of
    the primary one, these would match."""
    third = check_coverage(_TEACH_8XW_20_THIRD_PERSON_TURN)
    second = check_coverage(_TEACH_8XW_20_SECOND_PERSON_TURN)
    assert len(third.seen) == len(second.seen) == 3
    assert third.unclassified == third.seen
    assert second.unclassified == second.seen
    assert third.second_person_seen == ()
    assert second.second_person_seen == second.seen


def test_dnf_bond_lesson_second_person_subset_is_smaller_than_full_unclassified():
    """Mechanism check against the real lesson this bead was filed against:
    the secondary line must be a strictly smaller, more targeted list than
    the raw 31-of-32 unclassified total -- otherwise it's not buying a
    reviewer anything."""
    from teach.dnf_bond_lesson import build_lesson

    cov = check_coverage(build_lesson().text)
    assert 0 < len(cov.second_person_unclassified) < len(cov.unclassified)


def test_benign_second_person_turn_stays_unflagged():
    """teach-8xw.23's turn A: every sentence is second-person procedural
    address (finished/wrote/feeling/notes), none of it a potential-claim.
    A widening aimed at catching pure flattery must not also catch this --
    that would trade a false negative for a false positive, which the bead
    is explicit is not obviously the better trade."""
    assert check_lesson_text(_TEACH_8XW_23_BENIGN_SECOND_PERSON_TURN) == ()


def test_pure_flattery_turn_is_no_longer_invisible():
    """teach-8xw.23's actual bug: turn B is nothing but flattery built from
    five shapes `_claim_type` could not type (inherent-capacity, rarity-as-
    praise, named-person comparison, bare inevitability, negated-
    ordinariness) -- pre-fix, `check_lesson_text(B) == ()`, identical to
    the all-clean turn A. Every sentence must now classify and flag
    INFLATED; this is the bead's literal reproduction floor, not a claim
    that every pronoun-free or pronoun-bearing flattery sentence in English
    is now caught (see the blind-agent generalization check below, and the
    handoff, for what's still measured-but-open)."""
    cov = check_coverage(_TEACH_8XW_23_PURE_FLATTERY_TURN)
    assert len(cov.seen) == 5
    assert cov.classified == cov.seen, f"expected every sentence in turn B to classify, got {cov}"

    flags = check_lesson_text(_TEACH_8XW_23_PURE_FLATTERY_TURN)
    assert len(flags) == 5
    assert all(f.verdict is Verdict.INFLATED for f in flags)


def test_turn_a_and_turn_b_are_no_longer_indistinguishable():
    """The bead's precise complaint: pre-fix, `check_coverage(A)` and
    `check_coverage(B)` were identical on all six fields (5/0/5, 2p 5/0/5)
    even though A is benign and B is pure overpromise -- and
    `check_lesson_text` produced zero flags for both. Post-fix the coverage
    shape is still allowed to look similar (this bead doesn't touch
    `_SECOND_PERSON_REFERENCE` or `check_coverage` itself), but
    `check_lesson_text` must now tell them apart."""
    assert check_lesson_text(_TEACH_8XW_23_BENIGN_SECOND_PERSON_TURN) == ()
    assert len(check_lesson_text(_TEACH_8XW_23_PURE_FLATTERY_TURN)) == 5


# --- teach-9k5: disclosed ceiling, not a fifth widening ---------------------
#
# teach-8xw.23's fix typed the five shapes in ITS OWN reproduction. Measured
# against two independent blind-agent-authored held-out rounds (18
# sentences, no repo access, the second round explicitly steered away from
# teach-8xw.23's new vocabulary), `_claim_type` types 0/18. This is the
# fourth bead in the teach-yn8 -> teach-kmm -> teach-5gf -> teach-8xw.19 ->
# teach-8xw.23 lineage to hit the same wall, and teach-9k5 is closed as a
# disclosed limitation rather than a fifth vocabulary round (see the comment
# above `_TEACH_9K5_DISCLOSED_CEILING_SENTENCES` in potential_checker.py for
# why). These tests hold the disclosure honest, not the classification: the
# bar is seen+unclassified, never invisible and never falsely flagged clean.


def test_teach_9k5_disclosed_ceiling_sentences_are_seen():
    for sentence in _TEACH_9K5_DISCLOSED_CEILING_SENTENCES:
        cov = check_coverage(sentence)
        assert cov.seen == (sentence,), f"{sentence!r} must be counted as seen, got {cov.seen}"


def test_teach_9k5_disclosed_ceiling_sentences_land_in_unclassified_not_classified():
    for sentence in _TEACH_9K5_DISCLOSED_CEILING_SENTENCES:
        cov = check_coverage(sentence)
        assert cov.classified == (), f"{sentence!r} unexpectedly classified: {cov.classified}"
        assert cov.unclassified == (sentence,), f"{sentence!r} must be reported unclassified, got {cov}"


def test_teach_9k5_disclosed_ceiling_sentences_are_not_falsely_flagged_clean():
    """Unclassified must never be silently reported as zero flags without
    the accompanying coverage disclosure -- confirms check_lesson_text and
    check_coverage still agree on these, per _extract_from_sentence's
    single-source-of-truth invariant."""
    for sentence in _TEACH_9K5_DISCLOSED_CEILING_SENTENCES:
        assert check_lesson_text(sentence) == ()
        assert check_coverage(sentence).unclassified == (sentence,)
