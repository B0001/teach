"""teach-dds: third independently-authored held-out phrasing round against
teach/biblical_ot_source.py and teach/biblical_nt_source.py.

METHOD (same as round1/teach-8xw.41 and round2's precedent): a fresh `Agent`
call was made with an explicit instruction not to call any tool, read any
file, or inspect this or any repository -- only to use its own knowledge of
these five Bible verses and of natural tutor-speak phrasing. It was told
nothing about the patterns, vocabulary, or code in this repo, and nothing
about round1's or round2's findings or about Fix #2's mechanism
(attribution-anchored other-book coverage). It was additionally asked to
produce at least one FALSE_MISATTRIBUTION sentence per verse with no
reassignment-framing language ("actually", "in fact", "really", "originates",
"comes from", a trailing ", not ..." clause) and to use rival books not
reused from round1/round2, to directly stress-test Fix #2's core mechanism.
It produced exactly 30 sentences: for each of Genesis 1:1, Deuteronomy 6:4,
Isaiah 40:3, John 1:1, and John 11:35 -- 2 TRUE, 2 FALSE_MISATTRIBUTION, 1
AMBIGUOUS, and 1 OFF_TOPIC sentence. The 30 sentences below are reproduced
VERBATIM from that agent's output.

WHY THIS ROUND EXISTS, AND ITS HONEST EVIDENTIARY STATUS (READ THIS BEFORE
CITING IT AS EVIDENCE FOR ANYTHING)

Unlike round2 (tuning data for Fix #2, because Fix #2 was written in direct
response to round2's own JOHN1_FALSE_1 finding -- see
tests/test_biblical_sources_held_out_round2.py's docstring), this round was
generated AFTER Fix #2 already existed, by an agent with no knowledge of
Fix #2's mechanism, round1's findings, or round2's findings. It is genuine
held-out evidence for Fix #2, the same way round2 was genuine held-out
evidence for Fix #1.

At first measurement (against Fix #2 alone, before the fix this round's own
findings prompted), 26/30 sentences behaved safely and FOUR did not -- all
four FALSE_MISATTRIBUTION, all four landing a dangerous false CONFIRMED:

  DEUT_FALSE_2  = "The declaration 'Hear, O Israel: The LORD our God, the
  LORD is one' was written down in the book of 1 Samuel."
  JOHN1_FALSE_2 = "The famous 'In the beginning was the Word' opening is
  the first verse of Titus, not of any Gospel."
  JOHN11_FALSE_1 = "'Jesus wept' is a verse in the book of Job."
  JOHN11_FALSE_2 = "You'll find those two words, 'Jesus wept,' in
  Zephaniah, which is where the Bible's shortest verse sits."

Each slipped past Fix #2's `_other_book_attribution` false_pattern not
because the rival book was unanticipated (Fix #2's book list is exhaustive
-- all 66 canonical books), but because the ATTRIBUTION VERB wasn't in
`_ATTRIBUTION_VERBS`'s hand-curated list, or fell outside the short word
window that pattern requires: "written down in" (not "written in"),
"is a verse in" (not "is in"), "is the first verse of" (no listed verb at
all), "is where ... sits" (book and verb separated by too many words). This
is the SAME structural problem the original bug was, one level down --
enumerating attribution verbs is just as closed-world as enumerating rival
book names was. Patching `_ATTRIBUTION_VERBS` with "written", "book of",
"verse of", "sits" for these four specific sentences would repeat exactly
the anti-pattern this bead exists to fix.

So this bead's fix was extended a second time: `caution_patterns`, a new
field on `fact_checker.SourceFact` (see its docstring), wired into every
vulnerable fact in both source modules using blind, unanchored other-book
co-occurrence (no verb, no window). A true_patterns hit that also matches a
caution_pattern abstains (CANNOT_VERIFY) instead of confirming -- weaker
than false_patterns' CONTRADICTED, but structurally unable to produce a
dangerous CONFIRMED regardless of what attribution phrasing, or lack of
one, a misattribution sentence uses. This did cost recall on TWO existing
tests whose true claims legitimately mention another book in passing
without attributing content to it (see
tests/test_biblical_ot_source.py::test_isaiah_claim_mentioning_another_book_in_passing_now_abstains
and
tests/test_biblical_nt_source.py::test_true_claim_mentioning_another_book_in_passing_now_abstains)
-- an accepted trade-off in the safe direction, the same one Fix #1 already
made for reassignment-framing language.

The per-sentence tests below assert the CURRENT (post-caution_patterns)
measured behavior, honest and reproducible. Because this round's own
findings drove this third fix, THIS round is no longer evidence that the
caution_patterns mechanism itself generalizes beyond what it already
covers by construction (it is total over "any of the 66 canonical books,
anywhere in the sentence" by design, not by pattern-matching a phrasing) --
but that totality is exactly why no further held-out round is expected to
find a new gap of this same shape. Any future gap would have to be a
misattribution that does NOT co-occur with a rival book's name in the
sentence at all (e.g. reassigning to an unnamed "another Gospel" or a
pronoun-only reference) -- a different, out-of-scope failure mode not
addressed here; if a future round finds one, it should be filed as a new
bead per this bead's own "do not patch just the sentences that found it"
precedent, not folded into this fix silently.

RAW RESULT, honestly reported, measured AFTER the caution_patterns fix (the
state this file's tests assert):

  TRUE                  (10 sentences, 2/verse x 5 verses):
    8/10 CONFIRMED, 2/10 CANNOT_VERIFY (GENESIS_TRUE_2, JOHN1_TRUE_2 --
    recall gaps: the exact content keywords true_patterns keys on aren't
    all present in these two paraphrases, unrelated to caution_patterns).

  FALSE_MISATTRIBUTION  (10 sentences, 2/verse x 5 verses):
    4/10 CONTRADICTED (caught precisely by the attribution-anchored
    false_pattern -- GENESIS_FALSE_1, DEUT_FALSE_1, ISAIAH_FALSE_1,
    JOHN1_FALSE_1), 6/10 CANNOT_VERIFY (caught only by the weaker
    caution_patterns safety net -- GENESIS_FALSE_2, DEUT_FALSE_2,
    ISAIAH_FALSE_2, JOHN1_FALSE_2, JOHN11_FALSE_1, JOHN11_FALSE_2, all four
    of which were the dangerous false-CONFIRMEDs before this round's fix),
    0/10 CONFIRMED. Zero dangerous false-CONFIRMEDs.

  AMBIGUOUS   (5 sentences, 1/verse x 5 verses): 5/5 CANNOT_VERIFY. Correct.

  OFF_TOPIC   (5 sentences, 1/verse x 5 verses): 4/5 CANNOT_VERIFY, 1/5
    CONFIRMED (DEUT_OFF_TOPIC -- "Right after the Shema, Deuteronomy 6
    commands loving the LORD with all your heart, soul, and might."). Not
    dangerous: this sentence happens to also contain "Shema" and
    "Deuteronomy" together, which correctly and truthfully confirms the
    Shema-is-in-Deuteronomy fact even though the round's author intended it
    as an off-topic distractor about the following verse's content, not a
    claim about the Shema's location. A true incidental assertion getting
    correctly confirmed, not a false one slipping through.

TOTAL: 30 sentences, 9/30 CONFIRMED (all correct), 4/30 CONTRADICTED (all
correct), 17/30 CANNOT_VERIFY (all safe). Zero dangerous false-CONFIRMEDs.
"""
from teach.biblical_nt_source import BIBLICAL_NT_SOURCE
from teach.biblical_ot_source import BIBLICAL_OT_SOURCE
from teach.fact_checker import Verdict, verify_claim

# --- the 30 sentences, verbatim from the no-repo-access agent's output ------

GENESIS_TRUE_1 = (
    "Let's start with the very first line of the Bible: Genesis 1:1 tells "
    "us, 'In the beginning God created the heavens and the earth.'"
)
GENESIS_TRUE_2 = (
    "Notice how the opening verse of Genesis places God's creative act at "
    "the very start of everything — the heavens and the earth both "
    "come from him."
)
GENESIS_FALSE_1 = (
    "The book of Habakkuk opens with the words 'In the beginning God "
    "created the heavens and the earth.'"
)
GENESIS_FALSE_2 = (
    "That line about God creating the heavens and the earth in the "
    "beginning actually comes from the first chapter of Ezra."
)
GENESIS_AMBIGUOUS = (
    "Genesis 1:1 is one of those verses people have thought about for a "
    "very long time."
)
GENESIS_OFF_TOPIC = (
    "A little further into Genesis 1, God says 'Let there be light,' and "
    "there was light."
)

DEUT_TRUE_1 = (
    "Deuteronomy 6:4, the Shema, says, 'Hear, O Israel: The LORD our God, "
    "the LORD is one.'"
)
DEUT_TRUE_2 = (
    "When a student asks where Israel's central confession of one God is "
    "stated, point them to the Shema in the sixth chapter of Deuteronomy."
)
DEUT_FALSE_1 = (
    "Colossians 6:4 gives us the Shema: 'Hear, O Israel: The LORD our God, "
    "the LORD is one.'"
)
DEUT_FALSE_2 = (
    "The declaration 'Hear, O Israel: The LORD our God, the LORD is one' "
    "was written down in the book of 1 Samuel."
)
DEUT_AMBIGUOUS = (
    "We'll spend some time on the Shema later in the unit, since it comes "
    "up more than once."
)
DEUT_OFF_TOPIC = (
    "Right after the Shema, Deuteronomy 6 commands loving the LORD with "
    "all your heart, soul, and might."
)

ISAIAH_TRUE_1 = (
    "Isaiah 40:3 reads, 'A voice cries: In the wilderness prepare the way "
    "of the LORD.'"
)
ISAIAH_TRUE_2 = (
    "The image of a voice calling out in the wilderness to prepare the "
    "LORD's way comes early in Isaiah 40."
)
ISAIAH_FALSE_1 = (
    "Nahum is where we read, 'A voice cries: In the wilderness prepare the "
    "way of the LORD.'"
)
ISAIAH_FALSE_2 = (
    "That 'voice crying in the wilderness, prepare the way of the LORD' "
    "line originates in the book of Esther."
)
ISAIAH_AMBIGUOUS = (
    "Isaiah 40:3 is a verse worth sitting with before we move on to the "
    "next passage."
)
ISAIAH_OFF_TOPIC = (
    "Later in that same chapter, Isaiah says those who wait for the LORD "
    "shall mount up with wings like eagles."
)

JOHN1_TRUE_1 = (
    "John opens his Gospel with, 'In the beginning was the Word, and the "
    "Word was with God, and the Word was God.'"
)
JOHN1_TRUE_2 = (
    "In John 1:1, the Word is described as both being with God and being "
    "God, right at the beginning."
)
JOHN1_FALSE_1 = (
    "Hebrews begins, 'In the beginning was the Word, and the Word was "
    "with God, and the Word was God.'"
)
JOHN1_FALSE_2 = (
    "The famous 'In the beginning was the Word' opening is the first "
    "verse of Titus, not of any Gospel."
)
JOHN1_AMBIGUOUS = "Students often have a lot to say about the first verse of John's Gospel."
JOHN1_OFF_TOPIC = (
    "A few verses on, John 1:14 tells us the Word became flesh and dwelt "
    "among us."
)

JOHN11_TRUE_1 = "The shortest verse in most English Bibles is John 11:35: 'Jesus wept.'"
JOHN11_TRUE_2 = (
    "When Jesus came to Lazarus's tomb, the text gives us just two words "
    "— 'Jesus wept.'"
)
JOHN11_FALSE_1 = "'Jesus wept' is a verse in the book of Job."
JOHN11_FALSE_2 = (
    "You'll find those two words, 'Jesus wept,' in Zephaniah, which is "
    "where the Bible's shortest verse sits."
)
JOHN11_AMBIGUOUS = (
    "We'll come back to John 11:35 when we talk about how brevity works "
    "in narrative."
)
JOHN11_OFF_TOPIC = (
    "Earlier in John 11, Jesus tells Martha, 'I am the resurrection and "
    "the life.'"
)


# --- TRUE: safe hits (8/10) ----------------------------------------------

def test_genesis_true_1_confirmed():
    assert verify_claim(GENESIS_TRUE_1, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_deut_true_1_confirmed():
    assert verify_claim(DEUT_TRUE_1, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_deut_true_2_confirmed():
    assert verify_claim(DEUT_TRUE_2, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_isaiah_true_1_confirmed():
    assert verify_claim(ISAIAH_TRUE_1, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_isaiah_true_2_confirmed():
    assert verify_claim(ISAIAH_TRUE_2, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_john1_true_1_confirmed():
    assert verify_claim(JOHN1_TRUE_1, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


def test_john11_true_1_confirmed():
    assert verify_claim(JOHN11_TRUE_1, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


def test_john11_true_2_confirmed():
    assert verify_claim(JOHN11_TRUE_2, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


# --- TRUE: safe misses (2/10) -- recall gap, not a safety violation ------

def test_genesis_true_2_recall_gap_abstains():
    assert verify_claim(GENESIS_TRUE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john1_true_2_recall_gap_abstains():
    assert verify_claim(JOHN1_TRUE_2, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


# --- FALSE_MISATTRIBUTION: correct, precise catches via false_patterns (4/10) --

def test_genesis_false_1_correctly_contradicted():
    assert verify_claim(GENESIS_FALSE_1, BIBLICAL_OT_SOURCE) is Verdict.CONTRADICTED


def test_deut_false_1_correctly_contradicted():
    assert verify_claim(DEUT_FALSE_1, BIBLICAL_OT_SOURCE) is Verdict.CONTRADICTED


def test_isaiah_false_1_correctly_contradicted():
    assert verify_claim(ISAIAH_FALSE_1, BIBLICAL_OT_SOURCE) is Verdict.CONTRADICTED


def test_john1_false_1_correctly_contradicted():
    assert verify_claim(JOHN1_FALSE_1, BIBLICAL_NT_SOURCE) is Verdict.CONTRADICTED


# --- FALSE_MISATTRIBUTION: caught only by the caution_patterns safety net (6/10) --
# Each of these four sentences was a dangerous false CONFIRMED before the
# caution_patterns fix this round's own findings prompted -- see module
# docstring. They now abstain (CANNOT_VERIFY) rather than confirm.

def test_genesis_false_2_safe_miss_abstains():
    assert verify_claim(GENESIS_FALSE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_deut_false_2_previously_dangerous_now_abstains():
    """Was CONFIRMED before this round's caution_patterns fix -- "written
    down in" isn't "written in", so the attribution-anchored false_pattern
    didn't fire; blind other-book co-occurrence (caution_patterns) now
    withholds CONFIRMED regardless."""
    assert verify_claim(DEUT_FALSE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_isaiah_false_2_safe_miss_abstains():
    assert verify_claim(ISAIAH_FALSE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john1_false_2_previously_dangerous_now_abstains():
    """Was CONFIRMED before this round's caution_patterns fix -- "is the
    first verse of" has no listed attribution verb at all."""
    assert verify_claim(JOHN1_FALSE_2, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john11_false_1_previously_dangerous_now_abstains():
    """Was CONFIRMED before this round's caution_patterns fix -- "is a
    verse in" isn't "is in" (the extra words "a verse" break the literal
    match)."""
    assert verify_claim(JOHN11_FALSE_1, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john11_false_2_previously_dangerous_now_abstains():
    """Was CONFIRMED before this round's caution_patterns fix -- the rival
    book (Zephaniah) and the eventual verb ("sits") are separated by too
    many words for the attribution-anchored pattern's window."""
    assert verify_claim(JOHN11_FALSE_2, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


# --- FALSE_MISATTRIBUTION: zero dangerous CONFIRMEDs (0/10) --------------
# The property this whole round exists to check. Explicit per-sentence
# "not CONFIRMED" assertions above, plus this aggregate, so a future
# regression on any one of these ten fails loudly and specifically.

def test_no_false_misattribution_sentence_is_dangerously_confirmed():
    for name, claim, source in (
        ("GENESIS_FALSE_1", GENESIS_FALSE_1, BIBLICAL_OT_SOURCE),
        ("GENESIS_FALSE_2", GENESIS_FALSE_2, BIBLICAL_OT_SOURCE),
        ("DEUT_FALSE_1", DEUT_FALSE_1, BIBLICAL_OT_SOURCE),
        ("DEUT_FALSE_2", DEUT_FALSE_2, BIBLICAL_OT_SOURCE),
        ("ISAIAH_FALSE_1", ISAIAH_FALSE_1, BIBLICAL_OT_SOURCE),
        ("ISAIAH_FALSE_2", ISAIAH_FALSE_2, BIBLICAL_OT_SOURCE),
        ("JOHN1_FALSE_1", JOHN1_FALSE_1, BIBLICAL_NT_SOURCE),
        ("JOHN1_FALSE_2", JOHN1_FALSE_2, BIBLICAL_NT_SOURCE),
        ("JOHN11_FALSE_1", JOHN11_FALSE_1, BIBLICAL_NT_SOURCE),
        ("JOHN11_FALSE_2", JOHN11_FALSE_2, BIBLICAL_NT_SOURCE),
    ):
        verdict = verify_claim(claim, source)
        assert verdict is not Verdict.CONFIRMED, (
            f"dangerous false-CONFIRMED: {name} -> {verdict}"
        )


# --- AMBIGUOUS: 5/5 CANNOT_VERIFY ----------------------------------------

def test_genesis_ambiguous_abstains():
    assert verify_claim(GENESIS_AMBIGUOUS, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_deut_ambiguous_abstains():
    assert verify_claim(DEUT_AMBIGUOUS, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_isaiah_ambiguous_abstains():
    assert verify_claim(ISAIAH_AMBIGUOUS, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john1_ambiguous_abstains():
    assert verify_claim(JOHN1_AMBIGUOUS, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john11_ambiguous_abstains():
    assert verify_claim(JOHN11_AMBIGUOUS, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


# --- OFF_TOPIC: 4/5 CANNOT_VERIFY, 1/5 benign CONFIRMED -------------------

def test_genesis_off_topic_abstains():
    assert verify_claim(GENESIS_OFF_TOPIC, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_deut_off_topic_benign_confirm_not_dangerous():
    """This distractor sentence happens to also contain "Shema" and
    "Deuteronomy" together, which correctly confirms the (true)
    Shema-is-in-Deuteronomy fact -- a true incidental assertion getting
    correctly confirmed, not a misattribution slipping through. See module
    docstring."""
    assert verify_claim(DEUT_OFF_TOPIC, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_isaiah_off_topic_abstains():
    assert verify_claim(ISAIAH_OFF_TOPIC, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john1_off_topic_abstains():
    assert verify_claim(JOHN1_OFF_TOPIC, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john11_off_topic_abstains():
    assert verify_claim(JOHN11_OFF_TOPIC, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY
