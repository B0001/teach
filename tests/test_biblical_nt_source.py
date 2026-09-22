"""Enforce teach.fact_checker against the New Testament source in
teach/biblical_nt_source.py.

teach-8xw.37's acceptance criteria mirrors teach-8xw.11's for math: a
hand-written true claim, a hand-written false claim, and an ambiguous
claim that should abstain -- plus this bead's own requirement that every
verdict this adapter produces discloses it is checked against SBLGNT, not
directly against NA27/28/UBS4/5.
"""
from teach.biblical_nt_source import (
    AMBIGUOUS_CLAIM,
    BIBLICAL_NT_SOURCE,
    FALSE_CLAIM,
    TRUE_CLAIM,
    TRUE_CLAIM_MENTIONS_ANOTHER_BOOK_IN_PASSING,
)
from teach.fact_checker import Verdict, check_lesson_text, verify_claim


def test_true_claim_is_confirmed():
    assert verify_claim(TRUE_CLAIM, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


def test_false_claim_is_contradicted():
    assert verify_claim(FALSE_CLAIM, BIBLICAL_NT_SOURCE) is Verdict.CONTRADICTED


def test_ambiguous_claim_abstains():
    assert verify_claim(AMBIGUOUS_CLAIM, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


def test_off_topic_claim_cannot_verify_not_confirmed():
    """A sentence the source has nothing on at all must abstain -- the
    "topic not covered" flavor of CANNOT_VERIFY, distinct from the
    "topic covered, wording unclear" flavor AMBIGUOUS_CLAIM exercises."""
    assert (
        verify_claim("Paul wrote several letters to churches he had founded.", BIBLICAL_NT_SOURCE)
        is Verdict.CANNOT_VERIFY
    )


def test_jesus_wept_quoted_alone_is_confirmed():
    """The bare quotation, unattributed to any Gospel, is still an accurate
    claim -- true_patterns must not require naming John explicitly."""
    claim = "Jesus wept."
    assert verify_claim(claim, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


def test_jesus_wept_misattributed_to_luke_is_contradicted():
    """The plausible misattribution error: "Jesus wept" is only in John,
    not Luke."""
    claim = "In Luke's account, Jesus wept at the tomb of Lazarus."
    assert verify_claim(claim, BIBLICAL_NT_SOURCE) is Verdict.CONTRADICTED


def test_shortest_verse_correctly_attributed_to_john_is_confirmed():
    claim = "The shortest verse in the New Testament is found in John."
    assert verify_claim(claim, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


def test_shortest_verse_misattributed_to_mark_is_contradicted():
    claim = "The shortest verse in the New Testament is in Mark's Gospel."
    assert verify_claim(claim, BIBLICAL_NT_SOURCE) is Verdict.CONTRADICTED


def test_false_beats_true_when_a_sentence_matches_both():
    """Same bias as teach.fact_checker's math-source test: a sentence
    tripping both a true- and a false-pattern must resolve CONTRADICTED,
    not CONFIRMED."""
    sentence = (
        "Jesus wept, as John's Gospel says -- though some people mistakenly "
        "think that line is from Luke."
    )
    assert verify_claim(sentence, BIBLICAL_NT_SOURCE) is Verdict.CONTRADICTED


def test_genesis_conflation_is_contradicted():
    """The specific misconception this fact exists to catch: conflating
    John 1:1's opening with Genesis 1:1's, both of which start "In the
    beginning" but say different things."""
    claim = (
        "John's Gospel begins the same way Genesis does: in the beginning, "
        "God created the heavens and the earth."
    )
    assert verify_claim(claim, BIBLICAL_NT_SOURCE) is Verdict.CONTRADICTED


def test_true_claim_mentioning_another_book_in_passing_now_abstains():
    """teach-dds / round 3: a true claim that legitimately names another
    book (Genesis) without attributing John's content to it used to
    confirm -- the attribution-anchored false_pattern correctly didn't fire
    (no attribution verb next to "Genesis" here). But round 3 found
    misattribution sentences whose verbs weren't in that pattern's
    hand-curated list either ("...is the first verse of Titus, not of any
    Gospel"), so a second, weaker `caution_patterns` signal was added:
    blind co-occurrence of any other book's name, no verb required. That
    signal can't distinguish this passing mention from a real
    misattribution, so it abstains rather than confirms -- a deliberate
    recall loss in the safe direction (see
    teach.fact_checker.SourceFact's caution_patterns docstring)."""
    assert (
        verify_claim(TRUE_CLAIM_MENTIONS_ANOTHER_BOOK_IN_PASSING, BIBLICAL_NT_SOURCE)
        is Verdict.CANNOT_VERIFY
    )


def test_shortest_verse_misattributed_to_2_john_is_not_dangerously_confirmed():
    """teach-dds: found by code review (not a held-out round), while
    checking _ALL_BIBLE_BOOKS' coverage after round 3's fix. Both John
    facts use own=("john",), and _other_book_names excluded that string
    from the "other book" alternation -- but the bare "john" regex also
    matches inside "1 John"/"2 John"/"3 John", which ARE different
    canonical books from the Gospel of John. So a misattribution naming an
    epistle slipped past both false_patterns and caution_patterns entirely
    and landed a dangerous CONFIRMED, the same failure class this whole
    bead exists to close. Fixed by listing "1 john"/"2 john"/"3 john" as
    distinct entries in _ALL_BIBLE_BOOKS so they survive the own=("john",)
    exclusion."""
    claim = "'Jesus wept' is found in 2 John, the shortest of the epistles."
    assert verify_claim(claim, BIBLICAL_NT_SOURCE) is not Verdict.CONFIRMED


def test_opening_word_misattributed_to_3_john_is_not_dangerously_confirmed():
    claim = (
        "The opening line 'In the beginning was the Word, and the Word was "
        "with God, and the Word was God' can also be found in 3 John."
    )
    assert verify_claim(claim, BIBLICAL_NT_SOURCE) is not Verdict.CONFIRMED


def test_word_was_with_god_paraphrase_is_confirmed():
    """A paraphrase that doesn't name John explicitly but does state the
    actual content of John 1:1."""
    claim = "In the beginning, the Word already was, and the Word was with God."
    assert verify_claim(claim, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


# --- the 540-variation-unit caveat --------------------------------------
# This bead's acceptance criteria requires every verdict from this adapter
# to disclose that it's checked against SBLGNT, not NA27/28/UBS4/5 directly.
# teach.fact_checker.FactCheck copies fact.citation onto every FactCheck it
# emits regardless of verdict, so asserting the caveat is present on
# fact.citation for every seeded fact -- and exercising it through the real
# check_lesson_text entry point, not just verify_claim -- is what actually
# proves the disclosure reaches a consumer of this checker's output.


def test_every_fact_citation_discloses_the_sblgnt_caveat():
    for fact in BIBLICAL_NT_SOURCE.facts:
        assert "SBLGNT" in fact.citation
        assert "NA27/28" in fact.citation
        assert "UBS4/5" in fact.citation
        assert "540" in fact.citation


def test_check_lesson_text_carries_the_caveat_on_a_confirmed_verdict():
    text = f"Tutor: {TRUE_CLAIM}"
    checks = check_lesson_text(text, BIBLICAL_NT_SOURCE)
    assert len(checks) == 1
    assert checks[0].verdict is Verdict.CONFIRMED
    assert "SBLGNT" in checks[0].citation
    assert "NA27/28" in checks[0].citation


def test_check_lesson_text_carries_the_caveat_on_a_contradicted_verdict():
    text = f"Tutor: {FALSE_CLAIM}"
    checks = check_lesson_text(text, BIBLICAL_NT_SOURCE)
    assert len(checks) == 1
    assert checks[0].verdict is Verdict.CONTRADICTED
    assert "SBLGNT" in checks[0].citation


def test_a_question_about_the_topic_is_not_extracted_as_a_claim():
    """Same convention teach.fact_checker documents for math: a question is
    never an assertion, even about a recognized topic."""
    text = "Tutor: Does John's Gospel open the same way Genesis does?"
    checks = check_lesson_text(text, BIBLICAL_NT_SOURCE)
    assert checks == ()
