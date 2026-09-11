"""New Testament domain's reference source for teach.fact_checker.

sandbox-prompt.md requires NT fidelity to be judged against "Nestle-Aland
27/28 and UBS 4/5... never against the model's recollection." teach-8xw.12
(closed) confirmed both are closed texts: Deutsche Bibelgesellschaft's own
copyright pages state bulk/programmatic use is "completely forbidden"
without written permission, and no legal digital substitute for the
critical text itself exists. This module cannot check against NA/UBS
directly and does not pretend to.

teach-8xw.12 identified one open proxy: the SBL Greek New Testament
(SBLGNT, sblgnt.com and github.com/Faithlife/SBLGNT), CC BY 4.0, confirmed
by fetching the repo's own LICENSE metadata
(`curl -s https://api.github.com/repos/Faithlife/SBLGNT` -> license.key
"cc-by-4.0") and https://sblgnt.com/about/ directly. That same about page
states, in SBL's own words: "the SBLGNT differs from the standard text
[NA/UBS] in more than 540 variation units." That is not a rounding error --
per sandbox-prompt.md's rule that a checker verdict must not misrepresent
its own grounding, a verdict from this adapter is a claim about the SBLGNT
reading, not a certified claim about the NA27/28/UBS4/5 reading, unless
separately shown the two agree at that exact point.

HOW THE 540-VARIATION-UNIT CAVEAT IS HANDLED HERE (bead's option (a) + (b))

(b) -- disclosed on every verdict, unconditionally: `_CAVEAT` below is
    appended to every SourceFact's `citation`. teach.fact_checker.FactCheck
    copies `fact.citation` onto every FactCheck record it emits --
    including CANNOT_VERIFY ones -- so every verdict this adapter ever
    produces carries the "checked against SBLGNT, not NA/UBS directly, 540+
    known divergence points exist" disclosure. This is the unconditional
    floor: even if a future fact is added to this module without doing (a)
    below, the caveat still ships.

(a) -- verified per-fact, not assumed: every seeded fact's verse was
    checked against Faithlife/SBLGNT's OWN comparative apparatus
    (`data/sblgntapp/text/<Book>.txt` in that same repo), which records,
    verse by verse, every point where SBLGNT's printed text differs from
    Westcott-Hort, Tregelles, NA27/28, or the Robinson-Pierpont Byzantine
    text -- i.e. it is the primary source the "540 variation units" figure
    itself is drawn from, not a summary of it. Fetched directly:

      curl -sL https://raw.githubusercontent.com/Faithlife/SBLGNT/master/data/sblgntapp/text/John.txt

    Both verses seeded below (John 1:1, John 11:35) have NO entry at all in
    that apparatus file -- confirmed by exact-line grep against the raw
    file, not recalled -- meaning SBLGNT, WH, Tregelles, NA27/28, and RP all
    agree on the wording at those two verses. Neither is one of the known
    540 divergence points.

    For contrast (documented, not used as fact data -- do NOT seed a fact
    on any of these without re-verifying the surrounding words fall outside
    the flagged span), real SBLGNT-vs-NA28 divergences this same apparatus
    surfaced on a sweep of every NT book's apparatus file:

      Matthew 6:25, Matthew 27:40, John 5:11, Acts 8:33, Hebrews 12:9,
      James 2:4

    e.g. John 5:11's healed man says "he who [ὃς δὲ, SBLGNT/WH/Treg] made me
    well" where NA28 reads "the one [ὁ δὲ]" instead -- a real, if minor,
    textual difference this adapter must not paper over by treating SBLGNT
    and NA28 as interchangeable at that verse.

WHY THESE TWO VERSES: both are widely taught, low-ambiguity content facts
(not doctrinal interpretation) that a lesson can misstate in a
well-documented, plausible way -- conflating John 1:1's "In the beginning
was the Word" with Genesis 1:1's "In the beginning God created," and
misattributing "Jesus wept" (John 11:35, the shortest verse in most English
New Testaments) to a different Gospel. Pattern design otherwise follows
teach/math_facts.py: true/false patterns key off the specific misconception
a learner is likely to actually make, not just topic keywords, and
true_patterns stay narrow (abstain rather than guess) per sandbox-prompt.md's
"prefer abstention to a confident answer."
"""
from __future__ import annotations

import dataclasses
import re

from teach.fact_checker import SourceFact

# Appended to every fact's citation below so every FactCheck this adapter
# produces -- CONFIRMED, CONTRADICTED, or CANNOT_VERIFY alike, since
# teach.fact_checker.check_lesson_text copies fact.citation onto all three
# -- discloses that the verdict is grounded in SBLGNT, not NA27/28/UBS4/5
# directly. See module docstring for how this is verified per-fact, not
# just asserted.
_CAVEAT = (
    "checked against SBLGNT (sblgnt.com / github.com/Faithlife/SBLGNT, "
    "CC BY 4.0), an open proxy for the closed NA27/28 and UBS4/5 critical "
    "editions -- NOT a direct check against NA27/28/UBS4/5, which have no "
    "legal bulk-access substitute (teach-8xw.12). SBLGNT differs from "
    "NA/UBS at 540+ known variation units; this verse was checked against "
    "Faithlife/SBLGNT's own comparative apparatus and confirmed NOT to be "
    "one of them (see teach/biblical_nt_source.py docstring)."
)


_JOHN_OPENING_WORD = SourceFact(
    topic="john-1-1-opening-word",
    citation=f"SBLGNT, John 1:1 -- {_CAVEAT}",
    topic_patterns=(
        # "John['s Gospel] ... begin[s/ning] ..." -- aboutness anchored to
        # John specifically, not "the beginning" in the abstract (which
        # would also match Genesis-only sentences that aren't a claim
        # about John at all).
        re.compile(
            r"(?=.*\bjohn\b)(?=.*\bgospel\b|.*\b1:1\b)(?=.*\bbegin)",
            re.IGNORECASE | re.DOTALL,
        ),
        # Direct quotation/paraphrase without naming John explicitly --
        # "word" + "beginning" together is distinctive enough (teach-8xw.10's
        # document-frequency reasoning: this pairing doesn't occur in
        # ordinary sentences about other topics).
        re.compile(
            r"(?=.*\b(?:word|logos)\b)(?=.*\bbeginning\b)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    false_patterns=(
        # The Genesis-conflation misconception: claiming John's Gospel
        # opens the way Genesis does. This is the single most common
        # mix-up a learner makes here -- both open "In the beginning," and
        # it is easy to elide the fact that they say different things
        # after that.
        re.compile(
            r"(?=.*\bjohn\b)(?=.*\bbeginning\b)(?=.*\bcreated\b)"
            r"(?=.*\b(?:heavens?|earth)\b)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"(?=.*\bjohn\b)(?=.*\b(?:begins|opens)\b)"
            r"(?=.*\b(?:same as|identical to|just like)\b)(?=.*\bgenesis\b)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    true_patterns=(
        re.compile(
            r"(?=.*\bword\b)(?=.*\bbeginning\b)(?=.*\bwas\b)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
)


_JOHN_SHORTEST_VERSE = SourceFact(
    topic="john-11-35-shortest-verse",
    citation=f"SBLGNT, John 11:35 -- {_CAVEAT}",
    topic_patterns=(
        re.compile(r"(?=.*\bshortest\b)(?=.*\bverse\b)", re.IGNORECASE | re.DOTALL),
        re.compile(r"\bjesus wept\b", re.IGNORECASE),
    ),
    false_patterns=(
        # Misattributing "Jesus wept" (or "the shortest verse") to a
        # different Gospel/book -- the plausible learner error, not a
        # nonsense sentence a keyword match would already reject.
        re.compile(
            r"(?=.*\b(?:shortest verse|jesus wept)\b)"
            r"(?=.*\b(?:luke|mark|matthew|acts|genesis|exodus|psalms?)\b)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    true_patterns=(
        re.compile(r"\bjesus wept\b", re.IGNORECASE),
        re.compile(
            r"(?=.*\bshortest verse\b)(?=.*\bjohn\b)", re.IGNORECASE | re.DOTALL
        ),
    ),
)


@dataclasses.dataclass(frozen=True)
class BiblicalNTSource:
    """Implements teach.fact_checker.SourceAdapter for New Testament text."""

    domain: str = "biblical_nt"
    facts: tuple[SourceFact, ...] = (_JOHN_OPENING_WORD, _JOHN_SHORTEST_VERSE)


BIBLICAL_NT_SOURCE = BiblicalNTSource()


# --- hand-written examples for the runnable check ---------------------------
# Same shape as teach/math_facts.py's TRUE_CLAIM/FALSE_CLAIM/AMBIGUOUS_CLAIM,
# framed as tutor-spoken sentences.

TRUE_CLAIM = "John's Gospel opens with 'In the beginning was the Word,' unlike Genesis."

FALSE_CLAIM = (
    "John's Gospel begins the same way Genesis does: in the beginning, "
    "God created the heavens and the earth."
)

# Recognized topic (mentions "shortest verse" and names a Gospel) but
# asserts nothing checkable -- no claim about which Gospel it's actually
# in, just a vague gesture. Recognized-topic-but-unclear-assertion, the
# same CANNOT_VERIFY flavor math_facts.AMBIGUOUS_CLAIM exercises.
AMBIGUOUS_CLAIM = "The New Testament has a shortest verse that people like to bring up."


if __name__ == "__main__":
    from teach.fact_checker import Verdict, verify_claim

    assert verify_claim(TRUE_CLAIM, BIBLICAL_NT_SOURCE) is Verdict.CONFIRMED
    assert verify_claim(FALSE_CLAIM, BIBLICAL_NT_SOURCE) is Verdict.CONTRADICTED
    assert verify_claim(AMBIGUOUS_CLAIM, BIBLICAL_NT_SOURCE) is Verdict.CANNOT_VERIFY

    for fact in BIBLICAL_NT_SOURCE.facts:
        assert "SBLGNT" in fact.citation and "NA27/28" in fact.citation

    print(
        "OK: true claim CONFIRMED, false claim CONTRADICTED, "
        "ambiguous claim CANNOT_VERIFY (abstained); every fact's citation "
        "carries the SBLGNT-vs-NA/UBS caveat"
    )
