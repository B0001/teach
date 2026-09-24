"""teach-dds: second independently-authored held-out phrasing round against
teach/biblical_ot_source.py and teach/biblical_nt_source.py.

METHOD (same as round1/teach-8xw.41 and teach-8xw.33's precedent): a fresh
`Agent` call was made with an explicit instruction not to call any tool,
read any file, or inspect this or any repository -- only to use its own
knowledge of these five Bible verses and of natural tutor-speak phrasing.
It was told nothing about the patterns, vocabulary, or code in this repo,
and nothing about round1's three dangerous sentences. It produced exactly
30 sentences: for each of Genesis 1:1, Deuteronomy 6:4, Isaiah 40:3, John
1:1, and John 11:35 -- 2 TRUE, 2 FALSE_MISATTRIBUTION, 1 AMBIGUOUS, and 1
OFF_TOPIC sentence. The 30 sentences below are reproduced VERBATIM from
that agent's output.

WHY THIS ROUND EXISTS, AND ITS HONEST EVIDENTIARY STATUS (READ THIS BEFORE
CITING IT AS EVIDENCE FOR ANYTHING)

This round was generated and FIRST MEASURED against teach-dds's Fix #1
only (the domain-agnostic `_REASSIGNMENT_FRAMING` guard in
teach.fact_checker.verify_claim, written in response to round1's three
dangerous sentences). At that first measurement, 29/30 sentences behaved
safely and exactly one did not:

  JOHN1_FALSE_1 = "The Gospel of Mark opens with 'In the beginning was the
  Word, and the Word was with God, and the Word was God.'"

landed a dangerous false CONFIRMED. It carries no reassignment-framing
language at all ("actually", "in fact", "originates", "comes from", a
trailing ", not ..." clause) -- it is a flat, bare misattribution to an
unanticipated book (Mark, not one of the specific rivals any fact's
false_patterns had been keyed to). This is exactly the class of gap the
bead's acceptance criteria warned against: a fix that only closes the
literal sentences a round happened to find.

So teach-dds wrote Fix #2: `_other_book_attribution()` in both
biblical_ot_source.py and biblical_nt_source.py, which broadens each
vulnerable fact's false_patterns to recognize the verse's content
attributed to ANY canonical Bible book other than its own -- anchored to
an attribution verb near the book name (not blind co-occurrence, which was
tried first and immediately broke three existing CONFIRMED tests whose
true claims mention another book only in passing, e.g. "...unlike
Genesis", "...quoted by all four Gospels about John the Baptist"; see
`_other_book_attribution`'s docstring comment in both source modules).

Because Fix #2 was designed specifically in response to what THIS round
found, this round is TUNING DATA for Fix #2, not held-out evidence of it
-- the same "you cannot hold out examples from yourself" problem
sandbox-prompt.md warns about, now applying recursively to a fix instead
of to the original code. The per-sentence tests below assert the CURRENT
(post-Fix-#2) measured behavior, which is honest and reproducible, but
this file alone does not prove Fix #2 generalizes to a misattribution
phrasing neither this round nor round1 happened to produce. A third,
genuinely fresh held-out round (generated after Fix #2 was already
written, with the same no-repo-access discipline) is what would establish
that -- see tests/test_biblical_sources_held_out_round3.py.

RAW RESULT, honestly reported, measured AFTER Fix #2 (the state this file's
tests assert):

  TRUE                  (10 sentences, 2/verse x 5 verses):
    4/10 CONFIRMED, 6/10 CANNOT_VERIFY.
    A recall gap, not a safety violation -- some of these miss because the
    exact content keywords true_patterns keys on aren't all present
    (paraphrase), and GENESIS_TRUE_2 specifically trips
    `_REASSIGNMENT_FRAMING` ("actually begins with") and abstains rather
    than confirms -- the same accepted recall/safety trade-off Fix #1
    already makes on round1.

  FALSE_MISATTRIBUTION  (10 sentences, 2/verse x 5 verses):
    3/10 CONTRADICTED (caught correctly -- DEUT_FALSE_1, JOHN1_FALSE_1,
    JOHN11_FALSE_1), 7/10 CANNOT_VERIFY (safe miss), 0/10 CONFIRMED.
    Zero dangerous false-CONFIRMEDs, including JOHN1_FALSE_1, the one
    sentence that WAS dangerous before Fix #2.

  AMBIGUOUS   (5 sentences, 1/verse x 5 verses): 5/5 CANNOT_VERIFY. Correct.

  OFF_TOPIC   (5 sentences, 1/verse x 5 verses): 5/5 CANNOT_VERIFY. Correct.

TOTAL: 30 sentences, 7/30 CONFIRMED (all correct), 3/30 CONTRADICTED (all
correct), 20/30 CANNOT_VERIFY (all safe). Zero dangerous false-CONFIRMEDs.
"""
from teach.biblical_nt_source import BIBLICAL_NT_SOURCE
from teach.biblical_ot_source import BIBLICAL_OT_SOURCE
from teach.fact_checker import Verdict, verify_claim

# --- the 30 sentences, verbatim from the no-repo-access agent's output ------

GENESIS_TRUE_1 = (
    "This line opens the book of Genesis, describing God's creation of the "
    "heavens and the earth."
)
GENESIS_TRUE_2 = (
    "Genesis actually begins with this majestic statement about God "
    "creating the heavens and the earth."
)
GENESIS_FALSE_1 = (
    "This famous line about God creating the heavens and the earth "
    "actually comes from the opening of the book of Exodus."
)
GENESIS_FALSE_2 = (
    "The book of Psalms opens by declaring that God created the heavens "
    "and the earth."
)
GENESIS_AMBIGUOUS = "This verse really sets an important tone for the whole Bible, wouldn't you say?"
GENESIS_OFF_TOPIC = (
    "Later in Genesis chapter one, God separates the light from the "
    "darkness on the first day."
)

DEUT_TRUE_1 = (
    "This is the Shema, found in Deuteronomy chapter six, declaring that "
    "the LORD our God is one."
)
DEUT_TRUE_2 = (
    "Moses delivers this call to Israel in the book of Deuteronomy, "
    "affirming the LORD's oneness."
)
DEUT_FALSE_1 = (
    "The Shema is in fact drawn from the book of Exodus, during Moses's "
    "time on Mount Sinai."
)
DEUT_FALSE_2 = "Leviticus records the priests declaring that the LORD our God is one."
DEUT_AMBIGUOUS = "This verse is really central to Jewish tradition, in a pretty significant way."
DEUT_OFF_TOPIC = (
    "The verses that follow in Deuteronomy six instruct the Israelites to "
    "love the LORD with all their heart, soul, and strength."
)

ISAIAH_TRUE_1 = (
    "This verse from Isaiah announces a voice crying out to prepare the "
    "way of the LORD in the wilderness."
)
ISAIAH_TRUE_2 = (
    "Isaiah chapter forty opens with this call to prepare the way of the "
    "LORD, later echoed in the Gospels."
)
ISAIAH_FALSE_1 = (
    'The phrase "prepare the way of the LORD" originates from the book of '
    "Malachi, near the end of the Old Testament."
)
ISAIAH_FALSE_2 = (
    "John the Baptist speaks these exact words for the first time in the "
    "Gospel of Luke."
)
ISAIAH_AMBIGUOUS = "This passage really carries a lot of weight for how we think about preparation."
ISAIAH_OFF_TOPIC = (
    "Isaiah chapter forty goes on to compare the nations to a drop in a "
    "bucket before God's greatness."
)

JOHN1_TRUE_1 = (
    "John's Gospel opens with this statement that the Word was with God "
    "and the Word was God."
)
JOHN1_TRUE_2 = (
    "This is the famous prologue of John, which echoes the opening of "
    'Genesis with "In the beginning."'
)
JOHN1_FALSE_1 = (
    'The Gospel of Mark opens with "In the beginning was the Word, and '
    'the Word was with God, and the Word was God."'
)
JOHN1_FALSE_2 = (
    "This line about the Word being with God is actually part of Paul's "
    "letter to the Colossians."
)
JOHN1_AMBIGUOUS = "This verse is really one of the deepest in the whole New Testament."
JOHN1_OFF_TOPIC = (
    "A few verses later, John writes that the Word became flesh and dwelt "
    "among us."
)

JOHN11_TRUE_1 = (
    'At just two words, "Jesus wept" is the shortest verse in the Bible, '
    "found in John chapter eleven."
)
JOHN11_TRUE_2 = "This verse records Jesus weeping at the tomb of his friend Lazarus."
JOHN11_FALSE_1 = (
    '"Jesus wept" appears in the Gospel of Luke, right after the raising '
    "of Lazarus."
)
JOHN11_FALSE_2 = (
    "This is really Peter's reaction recorded after the crucifixion, not "
    "Jesus's own response."
)
JOHN11_AMBIGUOUS = "This little verse really packs an emotional punch, don't you think?"
JOHN11_OFF_TOPIC = (
    "Right before this, Martha tells Jesus that if he had been there, her "
    "brother would not have died."
)


# --- TRUE: safe hits (4/10) ---------------------------------------------

def test_deut_true_1_confirmed():
    assert verify_claim(DEUT_TRUE_1, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_isaiah_true_1_confirmed():
    assert verify_claim(ISAIAH_TRUE_1, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_isaiah_true_2_confirmed():
    assert verify_claim(ISAIAH_TRUE_2, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_john11_true_1_confirmed():
    assert verify_claim(JOHN11_TRUE_1, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


# --- TRUE: safe misses (6/10) -- recall gap, not a safety violation -----

def test_genesis_true_1_recall_gap_abstains():
    assert verify_claim(GENESIS_TRUE_1, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_genesis_true_2_recall_gap_abstains():
    """Trips _REASSIGNMENT_FRAMING ("actually begins with") -- Fix #1's
    accepted recall/safety trade-off, not a new gap."""
    assert verify_claim(GENESIS_TRUE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_deut_true_2_recall_gap_abstains():
    assert verify_claim(DEUT_TRUE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john1_true_1_recall_gap_abstains():
    assert verify_claim(JOHN1_TRUE_1, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john1_true_2_recall_gap_abstains():
    assert verify_claim(JOHN1_TRUE_2, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john11_true_2_recall_gap_abstains():
    assert verify_claim(JOHN11_TRUE_2, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


# --- FALSE_MISATTRIBUTION: correct catches (3/10) ------------------------

def test_deut_false_1_correctly_contradicted():
    assert verify_claim(DEUT_FALSE_1, BIBLICAL_OT_SOURCE) is Verdict.CONTRADICTED


def test_john1_false_1_correctly_contradicted():
    """This is the sentence that was dangerously CONFIRMED before Fix #2
    (see module docstring) -- now correctly CONTRADICTED via
    `_other_book_attribution` in biblical_nt_source.py's
    `_JOHN_OPENING_WORD`."""
    assert verify_claim(JOHN1_FALSE_1, BIBLICAL_NT_SOURCE) is Verdict.CONTRADICTED


def test_john11_false_1_correctly_contradicted():
    assert verify_claim(JOHN11_FALSE_1, BIBLICAL_NT_SOURCE) is Verdict.CONTRADICTED


# --- FALSE_MISATTRIBUTION: safe misses (7/10) -----------------------------

def test_genesis_false_1_safe_miss_abstains():
    assert verify_claim(GENESIS_FALSE_1, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_genesis_false_2_safe_miss_abstains():
    assert verify_claim(GENESIS_FALSE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_deut_false_2_safe_miss_abstains():
    assert verify_claim(DEUT_FALSE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_isaiah_false_1_safe_miss_abstains():
    assert verify_claim(ISAIAH_FALSE_1, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_isaiah_false_2_safe_miss_abstains():
    assert verify_claim(ISAIAH_FALSE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john1_false_2_safe_miss_abstains():
    assert verify_claim(JOHN1_FALSE_2, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john11_false_2_safe_miss_abstains():
    assert verify_claim(JOHN11_FALSE_2, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


# --- FALSE_MISATTRIBUTION: zero dangerous CONFIRMEDs (0/10) --------------
# The property this whole round exists to check. Explicit per-sentence
# "not CONFIRMED" assertions, not just an aggregate count, so a future
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


# --- OFF_TOPIC: 5/5 CANNOT_VERIFY ----------------------------------------

def test_genesis_off_topic_abstains():
    assert verify_claim(GENESIS_OFF_TOPIC, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_deut_off_topic_abstains():
    assert verify_claim(DEUT_OFF_TOPIC, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_isaiah_off_topic_abstains():
    assert verify_claim(ISAIAH_OFF_TOPIC, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john1_off_topic_abstains():
    assert verify_claim(JOHN1_OFF_TOPIC, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john11_off_topic_abstains():
    assert verify_claim(JOHN11_OFF_TOPIC, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY
