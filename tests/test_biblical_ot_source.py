"""Enforce teach.fact_checker against the Old Testament source in
teach/biblical_ot_source.py.

teach-8xw.36's acceptance criteria mirrors teach-8xw.11's for math and
teach-8xw.37's for the New Testament: a hand-written true claim, a
hand-written false claim, and an ambiguous claim that should abstain --
plus this bead's own requirements that (1) at least one fact is
cross-checked against DSS variant data via ETCBC/dss, proving that path is
real rather than merely described, and (2) a claim needing BHS
apparatus-level (cross-manuscript variant) evidence must abstain rather
than silently fall back to base-text-only evidence.
"""
from teach.biblical_ot_source import (
    ABSTAIN_APPARATUS_CLAIM,
    AMBIGUOUS_CLAIM,
    BIBLICAL_OT_SOURCE,
    FALSE_CLAIM,
    TRUE_CLAIM,
)
from teach.fact_checker import Verdict, check_lesson_text, verify_claim


def test_true_claim_is_confirmed():
    assert verify_claim(TRUE_CLAIM, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_false_claim_is_contradicted():
    assert verify_claim(FALSE_CLAIM, BIBLICAL_OT_SOURCE) is Verdict.CONTRADICTED


def test_ambiguous_claim_abstains():
    assert verify_claim(AMBIGUOUS_CLAIM, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_off_topic_claim_cannot_verify_not_confirmed():
    """A sentence the source has nothing on at all must abstain -- the
    "topic not covered" flavor of CANNOT_VERIFY, distinct from the
    "topic covered, wording unclear" flavor AMBIGUOUS_CLAIM exercises."""
    assert (
        verify_claim("Paul wrote several letters to churches he had founded.", BIBLICAL_OT_SOURCE)
        is Verdict.CANNOT_VERIFY
    )


# --- Genesis 1:1 ---------------------------------------------------------


def test_genesis_bare_claim_without_naming_the_book_is_confirmed():
    claim = "In the beginning, God created the heavens and the earth."
    assert verify_claim(claim, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_genesis_conflated_with_john_is_contradicted():
    """The mirror image of biblical_nt_source.py's Genesis-conflation
    check: attributing John's Logos-opening wording to Genesis."""
    claim = "Genesis opens by saying, 'In the beginning was the Word, and the Word was with God.'"
    assert verify_claim(claim, BIBLICAL_OT_SOURCE) is Verdict.CONTRADICTED


# --- Deuteronomy 6:4 (the Shema) -----------------------------------------


def test_shema_correctly_attributed_to_deuteronomy_is_confirmed():
    claim = "The Shema appears in Deuteronomy: 'Hear, O Israel, the LORD our God, the LORD is one.'"
    assert verify_claim(claim, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_shema_misattributed_to_exodus_is_contradicted():
    claim = "The Shema -- 'Hear, O Israel, the LORD is one' -- is found in the book of Exodus."
    assert verify_claim(claim, BIBLICAL_OT_SOURCE) is Verdict.CONTRADICTED


def test_genesis_fact_citation_discloses_the_sp_cross_check_and_nc_license():
    """teach-8xw.48: Genesis 1:1 now carries a Samaritan Pentateuch
    cross-check, mirroring the disclosure Isaiah's DSS cross-check
    already carries."""
    fact = next(f for f in BIBLICAL_OT_SOURCE.facts if f.topic == "genesis-1-1-creation")
    assert "DT-UCPH/sp" in fact.citation
    assert "Samaritan Pentateuch" in fact.citation
    assert "CC BY-NC" in fact.citation


def test_shema_named_alone_is_cannot_verify():
    """Recognized topic (the word "Shema" alone), but no checkable
    assertion -- recognized-topic-but-unclear-assertion."""
    claim = "The Shema is one of the most important lines in the Torah."
    assert verify_claim(claim, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_shema_fact_citation_discloses_the_peshitta_cross_check_and_nc_license():
    """teach-8xw.48: Deuteronomy 6:4 now carries a Peshitta cross-check,
    including the honest disclosure that the Peshitta adds one word with
    no WLC counterpart rather than being rounded up to "identical"."""
    fact = next(f for f in BIBLICAL_OT_SOURCE.facts if f.topic == "deuteronomy-6-4-shema")
    assert "ETCBC/peshitta" in fact.citation
    assert "Peshitta" in fact.citation
    assert "CC BY-NC" in fact.citation
    assert "additional trailing word" in fact.citation


# --- Isaiah 40:3, the DSS-cross-checked fact ------------------------------


def test_isaiah_voice_in_wilderness_correctly_attributed_is_confirmed():
    claim = (
        "Isaiah's 'A voice cries: prepare the way of the LORD' is later "
        "quoted by all four Gospels about John the Baptist."
    )
    assert verify_claim(claim, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_isaiah_line_misattributed_to_matthew_is_contradicted():
    """The plausible misconception this fact exists to catch: treating the
    Gospel citation of the line as its point of origin."""
    claim = (
        "The line 'prepare the way of the Lord' originates in the Gospel "
        "of Matthew, which John the Baptist later fulfills."
    )
    assert verify_claim(claim, BIBLICAL_OT_SOURCE) is Verdict.CONTRADICTED


def test_isaiah_topic_recognized_but_unattributed_is_cannot_verify():
    claim = "There's a famous 'voice in the wilderness' passage that shows up in both testaments."
    assert verify_claim(claim, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_isaiah_fact_citation_discloses_the_dss_cross_check_and_nc_license():
    fact = next(
        f for f in BIBLICAL_OT_SOURCE.facts if f.topic == "isaiah-40-3-prepare-the-way"
    )
    assert "1QIsaa" in fact.citation or "ETCBC/dss" in fact.citation
    assert "CC BY-NC" in fact.citation


# --- BHS apparatus: hard abstention on every claim ------------------------
# teach-8xw.18's hard design requirement: a claim needing cross-manuscript
# (Masorah) apparatus-level evidence must abstain, never silently fall
# back to base-text-only evidence as if it were equivalent.


def test_apparatus_level_claim_abstains():
    assert verify_claim(ABSTAIN_APPARATUS_CLAIM, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_apparatus_topic_is_recognized_not_merely_unmatched():
    """Distinguish this from ordinary off-topic CANNOT_VERIFY: the
    apparatus fact's topic_patterns DO fire (find_topic returns the fact),
    it is verify_claim's empty true/false pattern sets that force the
    abstention -- a deliberate hard-abstention topic, not an accidental
    recall gap."""
    from teach.fact_checker import find_topic

    fact = find_topic(ABSTAIN_APPARATUS_CLAIM, BIBLICAL_OT_SOURCE)
    assert fact is not None
    assert fact.topic == "bhs-apparatus-variant"


def test_apparatus_abstention_holds_even_when_a_dss_confirmed_verse_is_named():
    """The dangerous failure mode this fact exists to prevent: a claim
    that names a verse this adapter DID verify against WLC+DSS (Isaiah
    40:3) but asks specifically about Masoretic apparatus-level variant
    evidence must still abstain, not borrow confidence from the
    base-text/DSS agreement."""
    claim = (
        "The critical apparatus in BHS notes a Masoretic variant at "
        "Isaiah 40:3 concerning the word division."
    )
    assert verify_claim(claim, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_apparatus_fact_has_no_true_or_false_patterns():
    """Structural guarantee, not just behavioral: this topic can never
    produce CONFIRMED or CONTRADICTED because there is nothing to match."""
    fact = next(
        f for f in BIBLICAL_OT_SOURCE.facts if f.topic == "bhs-apparatus-variant"
    )
    assert fact.true_patterns == ()
    assert fact.false_patterns == ()


# --- false beats true when a sentence matches both ------------------------


def test_false_beats_true_when_a_sentence_matches_both():
    """Same bias as teach.fact_checker's math-source and NT-source tests:
    a sentence tripping both a true- and a false-pattern must resolve
    CONTRADICTED, not CONFIRMED."""
    sentence = (
        "Genesis says 'In the beginning, God created the heavens and the "
        "earth,' though some people confuse it with the Gospel of John's "
        "'In the beginning was the Word.'"
    )
    assert verify_claim(sentence, BIBLICAL_OT_SOURCE) is Verdict.CONTRADICTED


# --- citations reach a real consumer via check_lesson_text -----------------


def test_every_fact_citation_names_wlc_or_the_apparatus_gap():
    for fact in BIBLICAL_OT_SOURCE.facts:
        assert "WLC" in fact.citation or "apparatus" in fact.citation


def test_check_lesson_text_carries_the_dss_caveat_on_a_confirmed_verdict():
    text = (
        "Tutor: Isaiah's 'A voice cries: prepare the way of the LORD' is "
        "later quoted by all four Gospels about John the Baptist."
    )
    checks = check_lesson_text(text, BIBLICAL_OT_SOURCE)
    assert len(checks) == 1
    assert checks[0].verdict is Verdict.CONFIRMED
    assert "ETCBC/dss" in checks[0].citation
    assert "CC BY-NC" in checks[0].citation


def test_check_lesson_text_carries_the_sp_caveat_on_a_confirmed_genesis_verdict():
    text = "Tutor: In the beginning, God created the heavens and the earth."
    checks = check_lesson_text(text, BIBLICAL_OT_SOURCE)
    assert len(checks) == 1
    assert checks[0].verdict is Verdict.CONFIRMED
    assert "DT-UCPH/sp" in checks[0].citation
    assert "CC BY-NC" in checks[0].citation


def test_check_lesson_text_carries_the_peshitta_caveat_on_a_confirmed_shema_verdict():
    text = "Tutor: The Shema appears in Deuteronomy: 'Hear, O Israel, the LORD our God, the LORD is one.'"
    checks = check_lesson_text(text, BIBLICAL_OT_SOURCE)
    assert len(checks) == 1
    assert checks[0].verdict is Verdict.CONFIRMED
    assert "ETCBC/peshitta" in checks[0].citation
    assert "CC BY-NC" in checks[0].citation


def test_check_lesson_text_carries_abstention_on_apparatus_claim():
    text = f"Tutor: {ABSTAIN_APPARATUS_CLAIM}"
    checks = check_lesson_text(text, BIBLICAL_OT_SOURCE)
    assert len(checks) == 1
    assert checks[0].verdict is Verdict.CANNOT_VERIFY


def test_a_question_about_the_topic_is_not_extracted_as_a_claim():
    """Same convention teach.fact_checker documents for math and NT: a
    question is never an assertion, even about a recognized topic."""
    text = "Tutor: Does Genesis open the same way John's Gospel does?"
    checks = check_lesson_text(text, BIBLICAL_OT_SOURCE)
    assert checks == ()
