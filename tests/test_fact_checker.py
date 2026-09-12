"""Enforce the checker defined in teach/fact_checker.py against the math
domain source in teach/math_facts.py.

teach-8xw.11's acceptance criteria: a fact-checking pass that takes an
asserted claim from lesson text and a reference source and returns
confirmed / contradicted / cannot-verify, proven with a hand-written true
claim, a hand-written false claim, and an ambiguous claim that should
abstain.
"""
import pytest

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


def test_kernel_normal_in_target_group_synonym_is_contradicted():
    """teach-8xw.25 repro: the identical false claim phrased with the
    ordinary synonym "target group" instead of the literal word "codomain"
    must still be caught -- it was previously falling through to
    false_patterns finding no match and true_patterns' unqualified
    "kernel ... is ... normal" matching instead, i.e. CONFIRMED on a false
    claim."""
    claim = "The kernel of a homomorphism is a normal subgroup of the target group."
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONTRADICTED


def test_kernel_normal_in_range_of_the_map_synonym_is_contradicted():
    """Same false claim, the other ordinary synonym named in teach-8xw.25."""
    claim = "The kernel of a homomorphism is a normal subgroup of the range of the map."
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONTRADICTED


def test_kernel_plural_true_claim_is_confirmed_not_missed():
    """teach-8xw.25 secondary finding: \\bkernel\\b never matches inside
    "kernels" (no word boundary between "l" and "s"), so a true claim
    phrased in the plural was falling through to CANNOT_VERIFY as if the
    source had nothing to say about it at all."""
    claim = "Kernels are always normal subgroups of the domain."
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONFIRMED


def test_kernel_normal_in_receiving_group_synonym_is_contradicted():
    """A third codomain synonym surfaced by the round-1 blind-agent
    generalization measurement (teach-8xw.25 handoff) -- widening the
    synonym list is what took that round from 2/12 dangerous false-CONFIRMED
    down to 0/12."""
    claim = "The kernel is that special normal subgroup carved out of the receiving group."
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONTRADICTED


def test_kernel_normal_in_unenumerated_wrong_group_phrasing_abstains_not_confirms():
    """The round-2 blind-agent measurement (deliberately steered away from
    every synonym already in the false_patterns list) found false claims
    naming the wrong group in ways no enumerable synonym list will ever
    fully cover -- "H" as a stand-in name, or a structural description like
    "the group being mapped into". No false_pattern will catch these. What
    must not happen is the old failure mode: true_patterns defaulting to
    CONFIRMED because no false_pattern fired. Per sandbox-prompt.md's
    "prefer abstention to a confident answer", true_patterns now requires
    an explicit domain mention to confirm, so this abstains instead."""
    claim = (
        "If H is the group being mapped into, the kernel is simply one of "
        "H's normal subgroups."
    )
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CANNOT_VERIFY


def test_kernel_normal_structural_wrong_group_description_abstains_not_confirms():
    """Same round-2 finding, a different unenumerable phrasing (a relative
    clause naming the wrong group instead of a noun synonym) -- also must
    abstain, not confirm."""
    claim = (
        "The kernel is a normal subgroup that lives where the arrows point "
        "to, not where they start."
    )
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CANNOT_VERIFY


def test_lagrange_reversed_direction_synonym_paraphrase_is_now_contradicted():
    """teach-8xw.33: this exact sentence was the documented residual from
    teach-8xw.25's audit -- a reversed-direction (false) Lagrange claim
    phrased with "cardinality"/"container"/"contains" synonyms instead of
    the literal "order"/"subgroup"/"group" vocabulary false_patterns keyed
    off of, landing CANNOT_VERIFY (0/12 across an independently-authored
    blind round) instead of CONTRADICTED. That was always the SAFE failure
    direction -- true_patterns' exact-phrase requirement meant no reversed
    paraphrase was ever wrongly CONFIRMED -- but still a real recall gap.
    teach-8xw.33 widened _LAGRANGE_ORDER_DIVIDES's false_patterns with a
    synonym vocabulary (cardinality/size, container/contained, goes
    into/is a multiple of), the same move teach-8xw.25 made for the kernel
    topic's codomain synonyms, so this specific phrase is now caught.
    Locked in here so a future change can't quietly regress it back to
    CANNOT_VERIFY -- or worse, all the way to CONFIRMED."""
    claim = "Containment works like this: the container's cardinality divides the cardinality of what it contains."
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONTRADICTED


def test_lagrange_round_3_held_out_paraphrase_now_contradicted():
    """teach-8xw.33's held-out measurement: round-1 and round-2 blind
    paraphrases were both spent TUNING _LAGRANGE_ORDER_DIVIDES's widened
    false_patterns in the same session that wrote them, so neither counted
    as evidence the fix generalizes (sandbox-prompt.md: a generalization
    set authored in the same session as the rule is not held out). This
    sentence is from a genuinely fresh round-3 -- 12 more independently-
    authored paraphrases from a no-repo-access Agent call made AFTER the
    widening was already committed -- and is the one round-3 sentence the
    widened false_patterns actually caught (1/12)."""
    claim = (
        "It's kind of counterintuitive, but the outer group's order is a "
        "divisor of the inner subgroup's order, not the other way round."
    )
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONTRADICTED


def test_lagrange_round_3_verb_metaphor_paraphrase_abstains_not_confirms():
    """Same round-3 measurement, one of the 11/12 misses: a verb-phrase
    metaphor ("fit into that box a whole number of times") that never trips
    _LAGRANGE_ORDER_DIVIDES's topic_patterns at all -- no recognized size-
    or divisibility-word -- so it falls all the way through to CANNOT_VERIFY
    without the fact ever being looked up. Locked in as the disclosed
    ceiling: open-ended verb-phrase paraphrase is not enumerable by a
    synonym list, same as the kernel topic's unenumerable wrong-group
    phrasing above. What must not happen is this drifting to CONFIRMED."""
    claim = (
        "Picture the little subgroup as a box — the whole group's size "
        "needs to fit into that box a whole number of times."
    )
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CANNOT_VERIFY


def test_lagrange_round_3_recognized_topic_still_abstains_not_confirms():
    """Same round-3 measurement, the other miss flavor: a sentence that DOES
    trip topic_patterns (names "order" and "group"/"subgroup" and a
    divides-synonym) but whose structure ("gets divided out of ... with
    nothing left over") doesn't match either false_patterns or the narrow
    true_patterns -- so it correctly abstains rather than falling through to
    true_patterns' loose lagrange+divides pattern and landing the dangerous
    false-CONFIRMED verdict."""
    claim = (
        "The overall group order gets divided out of the subgroup order "
        "with nothing left over — that's the rule."
    )
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CANNOT_VERIFY


# --- round 4: fresh held-out measurement, all 12 preserved as data --------
#
# teach-8xw.47: round-3's held-out measurement above was real, but only 3 of
# its 12 sentences were ever committed as runnable data -- the other 9
# survived only as prose in a handoff and a comment in teach/math_facts.py,
# and the session that held the full 12 no longer exists, so the 1/12
# figure could never be re-checked against a future change to
# _LAGRANGE_ORDER_DIVIDES. This round repeats round-3's method (an Agent
# call given zero tool access -- no file reads, no repo, no code, no
# history -- asked to invent 12 independently-authored English paraphrases
# of the reversed/false Lagrange claim) but this time commits every
# sentence up front, verdict and all, as a parametrized test over a
# module-level tuple instead of prose. Measured against the current,
# unwidened-by-this-bead _LAGRANGE_ORDER_DIVIDES patterns:
# 2/12 CONTRADICTED, 10/12 CANNOT_VERIFY, 0/12 CONFIRMED. The safety
# property (no dangerous false-CONFIRMED) held on all 12. Per this bead's
# explicit instruction the patterns are NOT widened in response to this
# measurement -- doing so would make round-4 tuning data too, the same
# regress round-3's handoff already declined. A future widening attempt
# should measure against a round-5, not this one.
LAGRANGE_ROUND_4_HELD_OUT = (
    (
        "In this (incorrect) framing, the number of elements in the whole "
        "group is said to be a factor of the number of elements sitting in "
        "the subgroup.",
        Verdict.CANNOT_VERIFY,
    ),
    (
        "Notice that the subgroup's cardinality ends up being a multiple of "
        "the parent group's cardinality — or so the flawed reasoning goes.",
        Verdict.CONTRADICTED,
    ),
    (
        "Remember how big G is? Well, that count is supposed to go into the "
        "size of H evenly, according to this backwards claim.",
        Verdict.CANNOT_VERIFY,
    ),
    (
        "The outer structure's order evenly divides the order of the inner "
        "structure it sits inside.",
        Verdict.CANNOT_VERIFY,
    ),
    (
        "Think of it like tiling: the ambient group's size tiles evenly "
        "into the size of the subset contained within it.",
        Verdict.CANNOT_VERIFY,
    ),
    (
        "Is the number of elements in the child structure always a "
        "multiple of how many elements are in the parent? This mistaken "
        "account says yes.",
        Verdict.CANNOT_VERIFY,
    ),
    (
        "However many elements the whole group has, that number is claimed "
        "to fit neatly inside the count of elements belonging to the "
        "piece.",
        Verdict.CANNOT_VERIFY,
    ),
    (
        "The bigger structure's element-count is a divisor of the smaller "
        "structure's element-count — at least according to this reversed "
        "statement.",
        Verdict.CANNOT_VERIFY,
    ),
    (
        "Here's the (wrong) rule: take how many elements are in G, and "
        "that quantity splits evenly into however many elements are in H.",
        Verdict.CANNOT_VERIFY,
    ),
    (
        "Compare the two: the containing group's order is treated as a "
        "factor that packs neatly into the contained subgroup's order.",
        Verdict.CANNOT_VERIFY,
    ),
    (
        "Every subgroup, under this false description, has an element "
        "count that is some whole-number multiple of the outer group's "
        "element count.",
        Verdict.CANNOT_VERIFY,
    ),
    (
        "So the story goes, the size of the whole never exceeds being a "
        "clean divisor of the size of its own piece — the group's order "
        "goes into the subgroup's order without remainder.",
        Verdict.CONTRADICTED,
    ),
)


@pytest.mark.parametrize("claim,expected", LAGRANGE_ROUND_4_HELD_OUT)
def test_lagrange_round_4_held_out_paraphrase(claim, expected):
    """teach-8xw.47: every one of the 12 round-4 held-out sentences,
    preserved verbatim with its measured verdict, so this 2/12 CONTRADICTED
    / 10/12 CANNOT_VERIFY / 0/12 CONFIRMED figure -- unlike round-3's -- can
    be re-run with one command against any future change to
    _LAGRANGE_ORDER_DIVIDES. None of the 12 land CONFIRMED, i.e. the safety
    property held on this round too; a future assert flipping to CONFIRMED
    here would mean a widening introduced a dangerous regression."""
    assert verify_claim(claim, MATH_SOURCE) is expected


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


def test_lagrange_reversed_possessive_is_contradicted_not_confirmed():
    """teach-8xw.34: false_patterns' reversed-direction patterns had their
    own inline "(?:the |a |any )?" determiner list instead of sharing
    _ANY_DETERMINER, so "its" was never recognized as a determiner. That let
    this exact sentence slip past every false_pattern and fall through to
    true_patterns' loose `lagrange...divides` fallback, landing a dangerous
    false CONFIRMED on a reversed (false) claim -- not merely the disclosed-
    safe CANNOT_VERIFY recall gap teach-8xw.33 measured. Must be
    CONTRADICTED, the same as the "the/a/any/each subgroup" phrasings
    already covered."""
    claim = (
        "Lagrange's theorem: the order of the group divides the order of "
        "its subgroups."
    )
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONTRADICTED


def test_lagrange_reversed_quantifier_plus_possessive_is_contradicted():
    """Same teach-8xw.34 gap, compound quantifier+possessive form ("any of
    its subgroups") -- the sentence from the bead's own reproduction of the
    bug through teach/cialdini.py's render_authority AUTHORITY move, proving
    this is reachable from a real producer code path and not just a
    hand-crafted verify_claim call."""
    claim = (
        "Lagrange's theorem: the order of the group divides the order of "
        "any of its subgroups."
    )
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONTRADICTED


def test_lagrange_reversed_their_possessive_is_contradicted():
    """Same gap, "their" rather than "its" -- _POSSESSIVE_DETERMINER covers
    both, and this locks in the second pronoun so a future edit narrowing it
    back to "its" alone fails loudly."""
    claim = (
        "Lagrange's theorem: the order of the group divides the order of "
        "their subgroups."
    )
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONTRADICTED


def test_lagrange_true_claim_with_possessive_determiner_is_confirmed():
    """_ANY_DETERMINER is shared between the reversed (false_patterns) and
    correct-direction (true_patterns) literal patterns, so the possessive
    fix must not make the checker abstain on a CORRECT claim phrased with
    "its" -- only reject the reversed direction."""
    claim = "In a finite group, the order of its subgroups divides the order of the group."
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONFIRMED


def test_lagrange_possessive_held_out_paraphrase_caught_as_contradicted():
    """teach-8xw.34's held-out measurement, after the _ANY_DETERMINER
    possessive fix landed: 12 fresh reversed-Lagrange paraphrases from a
    no-repo-access Agent call, deliberately steered toward possessive and
    determiner-adjacent phrasing ("its", "their", "any of its", "the
    group's own", ...) -- the exact failure mode this bug was about, not
    the general open-ended-English ceiling teach-8xw.33 already measured.
    Result: 3/12 CONTRADICTED, 9/12 CANNOT_VERIFY, 0/12 CONFIRMED -- the
    safety property (no dangerous false-CONFIRMED) held on every sentence
    in this round. This is one of the 3 catches."""
    claim = (
        "Lagrange's theorem tells us that a group's order is always a "
        "factor of the order of each of its subgroups."
    )
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CONTRADICTED


def test_lagrange_possessive_held_out_paraphrase_abstains_not_confirms():
    """Same teach-8xw.34 held-out round, one of the 9/12 misses: "the size
    of the whole group goes evenly into the size of any of its subgroups"
    breaks _DIVIDES_SYNONYMS' "go(?:es)?\\s+into" match because "evenly"
    sits between "goes" and "into" -- an open-ended-English gap in the verb
    phrase, not the possessive-determiner gap this bead fixed. Locked in as
    the disclosed ceiling: what must not happen is this landing CONFIRMED."""
    claim = (
        "Per Lagrange, the size of the whole group goes evenly into the "
        "size of any of its subgroups."
    )
    assert verify_claim(claim, MATH_SOURCE) is Verdict.CANNOT_VERIFY


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
