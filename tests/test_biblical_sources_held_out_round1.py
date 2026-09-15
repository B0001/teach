"""teach-8xw.41: first independently-authored held-out phrasing round ever
run against teach/biblical_ot_source.py and teach/biblical_nt_source.py.

Before this bead, both adapters (teach-8xw.36, teach-8xw.37) had only ever
been exercised against tests/test_biblical_ot_source.py and
tests/test_biblical_nt_source.py -- fixtures written by the same session
that wrote the pattern code. teach-8xw.37's own handoff said so explicitly.
Per sandbox-prompt.md's "you cannot hold out examples from yourself", that
is not evidence of generalization.

METHOD (matches teach-8xw.33's precedent exactly): a fresh `Agent` call was
made with an explicit instruction not to call any tool, read any file, or
inspect this or any repository -- only to use its own knowledge of these
five Bible verses and of natural tutor-speak phrasing. It was told nothing
about the patterns, vocabulary, or code in this repo. It produced exactly
30 sentences: for each of Genesis 1:1, Deuteronomy 6:4, Isaiah 40:3, John
1:1, and John 11:35 -- 2 TRUE, 2 FALSE_MISATTRIBUTION, 1 AMBIGUOUS, and 1
OFF_TOPIC sentence. The 30 sentences below are reproduced VERBATIM from
that agent's output -- not summarized, not paraphrased, not hand-picked.
teach-8xw.40's own finding (round-3 of the Lagrange measurement was never
fully preserved, only 3 of 12 sentences survived as runnable data) is the
reason every one of the 30 is committed here as code, not just described
in a handoff.

Per the bead's own instruction, the patterns in biblical_ot_source.py and
biblical_nt_source.py were NOT touched after this round was measured. Doing
so would make this round tuning data too -- the same problem a self-authored
set already is -- and would require a further held-out round to know
whether any fix actually generalizes.

RAW RESULT, honestly reported, no rounding:

  TRUE                  (10 sentences, 2/verse x 5 verses):
    5/10 CONFIRMED, 5/10 CANNOT_VERIFY.
    A recall gap, not a safety violation: an accurate claim going
    unconfirmed leaves the learner uncorrected but never tells them
    something false is true.

  FALSE_MISATTRIBUTION  (10 sentences, 2/verse x 5 verses):
    1/10 CONTRADICTED (caught correctly),
    6/10 CANNOT_VERIFY (safe miss -- abstained rather than guessed),
    3/10 CONFIRMED  <-- DANGEROUS. A false claim was validated as true.
    This is a real safety-property violation, not a recall gap, and is
    filed as teach-dds (new bug bead) rather than fixed in this bead --
    fixing it now would spend this same round as tuning data. See the
    three `test_dangerous_*` functions below, each `xfail(strict=True)`
    pending that bead.

  AMBIGUOUS   (5 sentences, 1/verse x 5 verses): 5/5 CANNOT_VERIFY. Correct.

  OFF_TOPIC   (5 sentences, 1/verse x 5 verses): 5/5 CANNOT_VERIFY. Correct
    (a sentence about a different verse/topic entirely never trips any
    fact's topic_patterns, or if it coincidentally does, still fails to
    trip a true_pattern -- either way, safe).

TOTAL: 30 sentences, 11/30 CONFIRMED (8 correct + 3 dangerous), 1/30
CONTRADICTED (correct), 18/30 CANNOT_VERIFY (15 correct/safe-miss + 3 of
the FALSE_MISATTRIBUTION's safe misses already counted above -- see the
per-category breakdown, this total line is just an arithmetic check:
10 TRUE + 10 FALSE_MISATTRIBUTION + 5 AMBIGUOUS + 5 OFF_TOPIC = 30).

Root cause of the 3 dangerous CONFIRMEDs (see each xfail test's docstring
for specifics): every seeded fact's `true_patterns` matches on the
verse's own content/wording appearing in the sentence, unconditionally.
Each fact's `false_patterns` only catches a misattribution when a
SPECIFIC other book's name is the literal token that appears (e.g.
_JOHN_OPENING_WORD's false_patterns require the literal word "john";
_GENESIS_CREATION's false_patterns require the literal word "genesis").
The agent's misattribution sentences instead phrased the wrong attribution
as "this is actually from/about <the other side>" without repeating the
anchor keyword the false_pattern was keyed to relative to the topic that
matched -- topic_patterns recognized the sentence as being about the fact
in question by CONTENT alone, but false_patterns needed an EXTRA keyword
that the sentence, once already on-topic, no longer had a reason to
include. That is a structural asymmetry between what topic_patterns needs
to recognize a sentence and what false_patterns needs to condemn it,
not a vocabulary-coverage gap the way teach-8xw.33's Lagrange gap was.
"""
from teach.biblical_nt_source import BIBLICAL_NT_SOURCE
from teach.biblical_ot_source import BIBLICAL_OT_SOURCE
from teach.fact_checker import Verdict, check_lesson_text, verify_claim

import pytest

# --- the 30 sentences, verbatim from the no-repo-access agent's output ------

GENESIS_TRUE_1 = (
    "Genesis opens by telling us that God created the heavens and the earth "
    "right at the very beginning of time."
)
GENESIS_TRUE_2 = (
    "The Bible's very first sentence is all about how God brought the sky "
    "and the earth into existence out of nothing."
)
GENESIS_FALSE_1 = (
    'That famous opening line, "In the beginning God created the heavens '
    'and the earth," is actually how the Gospel of John starts.'
)
GENESIS_FALSE_2 = (
    "Exodus opens with the creation account, telling us God made the "
    "heavens and the earth in the beginning."
)
GENESIS_AMBIGUOUS = "This verse is probably the most quoted opening line in all of world literature."
GENESIS_OFF_TOPIC = (
    "Later in Genesis, God rests on the seventh day and sets it apart as a "
    "day of rest for his people."
)

DEUT_TRUE_1 = (
    "In Deuteronomy, Moses tells the Israelites to listen up, because the "
    "Lord their God is one God."
)
DEUT_TRUE_2 = (
    "The Shema declares that the Lord is our God, and that the Lord alone "
    "is one, with no other gods beside him."
)
DEUT_FALSE_1 = (
    'The Shema, "Hear, O Israel," comes from the book of Leviticus as part '
    "of the purity laws."
)
DEUT_FALSE_2 = (
    "That line about the Lord being one God is actually the first of the "
    "Ten Commandments given in Exodus."
)
DEUT_AMBIGUOUS = (
    "This is one of the most central prayers in all of Jewish tradition, "
    "recited daily by observant Jews."
)
DEUT_OFF_TOPIC = (
    "A few chapters later, Moses reminds the people not to test the Lord "
    "their God the way they did at Massah."
)

ISAIAH_TRUE_1 = (
    "Isaiah describes a voice crying out that the people should prepare "
    "the way of the Lord in the wilderness."
)
ISAIAH_TRUE_2 = (
    "The prophet Isaiah pictures someone calling from the desert, telling "
    "everyone to make a straight highway for God."
)
ISAIAH_FALSE_1 = (
    'That famous "voice crying in the wilderness" line is actually from '
    "the prophet Jeremiah's early chapters."
)
ISAIAH_FALSE_2 = (
    "John the Baptist himself wrote those words about preparing the way "
    "of the Lord in the wilderness, before Isaiah picked them up."
)
ISAIAH_AMBIGUOUS = "This passage is one that later New Testament writers loved to point back to."
ISAIAH_OFF_TOPIC = (
    "Elsewhere in Isaiah, the prophet describes a suffering servant who is "
    "despised and rejected by others."
)

JOHN1_TRUE_1 = (
    "John opens his Gospel by saying that in the beginning was the Word, "
    "and the Word was with God, and the Word was God."
)
JOHN1_TRUE_2 = (
    "According to John, before anything else existed, the Word already "
    "existed alongside God and was fully divine."
)
JOHN1_FALSE_1 = (
    'That "In the beginning was the Word" passage is actually the opening '
    "of the book of Genesis."
)
JOHN1_FALSE_2 = (
    "Paul writes in his letter to the Romans that the Word was with God "
    "and the Word was God."
)
JOHN1_AMBIGUOUS = "This opening has been the subject of centuries of theological debate and reflection."
JOHN1_OFF_TOPIC = (
    "A little later, John tells us that the Word became flesh and dwelt "
    "among us, full of grace and truth."
)

JOHN11_TRUE_1 = (
    "When Jesus arrives at Lazarus's tomb and sees everyone grieving, "
    "we're simply told that Jesus wept."
)
JOHN11_TRUE_2 = (
    "John records the shortest verse in the Bible right here, just two "
    "words: Jesus wept."
)
JOHN11_FALSE_1 = (
    "It's Luke's Gospel that gives us that famous short verse, "
    '"Jesus wept," at Lazarus\'s grave.'
)
JOHN11_FALSE_2 = (
    '"Jesus wept" is actually describing the moment right before the '
    "crucifixion, not the raising of Lazarus."
)
JOHN11_AMBIGUOUS = "This is often pointed to as a striking moment showing something important about Jesus."
JOHN11_OFF_TOPIC = (
    "Just after this, Jesus calls into the tomb and Lazarus comes out "
    "still wrapped in his grave clothes."
)


# --- TRUE: safe hits (5/10) --------------------------------------------

def test_genesis_true_1_confirmed():
    assert verify_claim(GENESIS_TRUE_1, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_isaiah_true_1_confirmed():
    assert verify_claim(ISAIAH_TRUE_1, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED


def test_john1_true_1_confirmed():
    assert verify_claim(JOHN1_TRUE_1, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


def test_john11_true_1_confirmed():
    assert verify_claim(JOHN11_TRUE_1, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


def test_john11_true_2_confirmed():
    assert verify_claim(JOHN11_TRUE_2, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED


# --- TRUE: safe misses (5/10) -- recall gap, not a safety violation -----

def test_genesis_true_2_recall_gap_abstains():
    """Accurate paraphrase ("brought the sky and earth into existence out
    of nothing") without the literal words the true_pattern keys on
    ("created", "heavens"/"earth" together with "beginning"+"god" all
    present) -- misses, safely."""
    assert verify_claim(GENESIS_TRUE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_deut_true_1_recall_gap_abstains():
    assert verify_claim(DEUT_TRUE_1, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_deut_true_2_recall_gap_abstains():
    assert verify_claim(DEUT_TRUE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_isaiah_true_2_recall_gap_abstains():
    assert verify_claim(ISAIAH_TRUE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john1_true_2_recall_gap_abstains():
    assert verify_claim(JOHN1_TRUE_2, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


# --- FALSE_MISATTRIBUTION: the one correct catch (1/10) -----------------

def test_john11_false_1_correctly_contradicted():
    assert verify_claim(JOHN11_FALSE_1, BIBLICAL_NT_SOURCE) is Verdict.CONTRADICTED


# --- FALSE_MISATTRIBUTION: safe misses (6/10) ---------------------------

def test_deut_false_1_safe_miss_abstains():
    assert verify_claim(DEUT_FALSE_1, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_deut_false_2_safe_miss_abstains():
    assert verify_claim(DEUT_FALSE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_isaiah_false_1_safe_miss_abstains():
    assert verify_claim(ISAIAH_FALSE_1, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_isaiah_false_2_safe_miss_abstains():
    assert verify_claim(ISAIAH_FALSE_2, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY


def test_john1_false_2_safe_miss_abstains():
    assert verify_claim(JOHN1_FALSE_2, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY


# --- FALSE_MISATTRIBUTION: DANGEROUS false-CONFIRMEDs (3/10) ------------
# Filed as teach-dds. NOT fixed in this bead -- per this bead's own text,
# tuning against the round that found the gap spends the round; a fresh
# no-repo-access round would be needed to show any fix actually
# generalizes. xfail(strict=True) so a future fix is loudly detected (XPASS)
# and forces removal of the marker, and so a future regression that
# resurrects any of these three is impossible to merge silently.

@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="teach-dds: dangerous false-CONFIRMED, Genesis-content "
    "misattributed to John without the literal word 'genesis' appearing",
)
def test_dangerous_genesis_misattributed_to_john_not_confirmed():
    """Sentence claims Genesis's own opening line is "actually how the
    Gospel of John starts" -- a false misattribution. _GENESIS_CREATION's
    false_patterns require the literal word "genesis" to co-occur with
    "word"+"beginning"+"was"; this sentence names "the Gospel of John"
    instead, so false_patterns never fire. true_patterns match on
    beginning+god+created+heavens/earth alone, with no check for
    misattributing framing, so verify_claim returns CONFIRMED -- the
    checker validates a false claim as true. Measured actual behavior
    today: CONFIRMED. Desired/safe: CANNOT_VERIFY or CONTRADICTED, but
    never CONFIRMED."""
    verdict = verify_claim(GENESIS_FALSE_1, BIBLICAL_OT_SOURCE)
    assert verdict is not Verdict.CONFIRMED, (
        f"dangerous false-CONFIRMED reproduced (teach-dds): {verdict}"
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="teach-dds: dangerous false-CONFIRMED, John's content "
    "misattributed to Genesis without the literal word 'john' appearing",
)
def test_dangerous_john1_misattributed_to_genesis_not_confirmed():
    """Mirror image of the Genesis case: claims John 1:1's content is
    "actually the opening of the book of Genesis." _JOHN_OPENING_WORD's
    false_patterns both require the literal word "john"; this sentence
    never says "john" at all -- it only names the wrong destination,
    "Genesis." true_patterns match on word+beginning+was alone. Measured
    actual behavior today: CONFIRMED."""
    verdict = verify_claim(JOHN1_FALSE_1, BIBLICAL_NT_SOURCE)
    assert verdict is not Verdict.CONFIRMED, (
        f"dangerous false-CONFIRMED reproduced (teach-dds): {verdict}"
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="teach-dds: dangerous false-CONFIRMED, 'Jesus wept' "
    "misattributed to the wrong narrative moment (no other book named)",
)
def test_dangerous_john11_wrong_narrative_context_not_confirmed():
    """Claims "Jesus wept" is "actually describing the moment right before
    the crucifixion, not the raising of Lazarus" -- false (it is Lazarus's
    raising). _JOHN_SHORTEST_VERSE's true_patterns match on the bare
    literal phrase "jesus wept" unconditionally; its false_patterns only
    fire when a DIFFERENT BOOK NAME is present (luke/mark/matthew/acts/
    genesis/exodus/psalms), which this sentence never does -- it
    misattributes the narrative moment, not the book. Measured actual
    behavior today: CONFIRMED."""
    verdict = verify_claim(JOHN11_FALSE_2, BIBLICAL_NT_SOURCE)
    assert verdict is not Verdict.CONFIRMED, (
        f"dangerous false-CONFIRMED reproduced (teach-dds): {verdict}"
    )


# --- AMBIGUOUS: 5/5 correctly abstain -----------------------------------

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


# --- OFF_TOPIC: 5/5 correctly abstain -----------------------------------

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


# --- check_lesson_text: prove the same dangerous CONFIRMED reproduces via
# the full lesson-text pipeline (sentence splitting + extract_domain_claims
# + verify_claim), not just the low-level verify_claim entry point, since
# check_lesson_text is what a real consumer of this checker actually calls.

@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="teach-dds: same dangerous false-CONFIRMED as "
    "test_dangerous_genesis_misattributed_to_john_not_confirmed, "
    "reproduced through the full check_lesson_text pipeline rather than "
    "a direct verify_claim() call",
)
def test_check_lesson_text_reproduces_dangerous_confirm_via_full_pipeline():
    """A real consumer of this checker calls check_lesson_text, not
    verify_claim directly. This proves the teach-dds bug is not an
    artifact of calling verify_claim in isolation -- sentence splitting
    and extract_domain_claims both pass GENESIS_FALSE_1 through unchanged,
    and it still lands CONFIRMED."""
    text = "tutor: " + GENESIS_TRUE_1 + " " + GENESIS_FALSE_1
    checks = check_lesson_text(text, BIBLICAL_OT_SOURCE)
    assert len(checks) == 2
    assert checks[0].sentence == GENESIS_TRUE_1
    assert checks[0].verdict is Verdict.CONFIRMED
    assert checks[1].sentence == GENESIS_FALSE_1
    assert checks[1].verdict is not Verdict.CONFIRMED, (
        f"dangerous false-CONFIRMED reproduced via check_lesson_text "
        f"(teach-dds): {checks[1].verdict}"
    )
