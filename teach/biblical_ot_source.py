"""Old Testament domain's reference source for teach.fact_checker.

sandbox-prompt.md requires OT fidelity to be judged against "BHS/Leningrad
Codex with Dead Sea Scrolls and ancient-version variants... never against
the model's recollection." teach-8xw.12 and teach-8xw.18 (both closed, pure
research) answered the source-access question this requires but explicitly
scoped out building the adapter itself -- this module is that follow-on,
built the same way teach/biblical_nt_source.py was for the NT side.

WHAT THIS ADAPTER CHECKS AGAINST, AND WHAT IT DOES NOT
--------------------------------------------------------------------------

Base text: Westminster Leningrad Codex (WLC) via OpenScriptures/morphhb
(github.com/openscriptures/morphhb), CC BY 4.0, base manuscript public
domain. Every seeded fact's Hebrew wording below was fetched directly from
that repo's own XML (not recalled), e.g.:

  curl -sL https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Gen.xml
  curl -sL https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Deut.xml
  curl -sL https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Isa.xml

DSS cross-check: ETCBC/dss (github.com/ETCBC/dss), Text-Fabric, CC BY-NC
4.0 -- confirmed directly from that repo's own docs/about.md ("the data in
this repo... is available under a CC-BY-NC license"), not assumed by
analogy. Loaded and queried live with the `text-fabric` package itself
(not a summary of it):

  uv run --with "text-fabric[github]" --with "PyGithub==1.58.2" python3 -c '
      from tf.app import use
      A = use("ETCBC/dss", hoist=globals(), silent="deep")
      F, L = A.api.F, A.api.L
      words = [w for w in F.otype.s("word")
               if F.book.v(w) == "Is" and F.chapter.v(w) == "40"
               and F.verse.v(w) == "3"]
      for w in words:
          scroll = F.scroll.v(L.u(w, "scroll")[0])
          print(scroll, F.glex.v(w))
  '

This returned Isaiah 40:3's lexemes for THREE separate scrolls -- 1QIsaa
(the Great Isaiah Scroll, node range starting 1909047), 1QIsab (1Q8, node
range starting 1921933), and 4QIsaa (4Q56, node range starting 2018796) --
and all three give the identical lexeme sequence: קול קרא ב מדבר פנה דרך
יהוה ו ישר ב ערבה מסלה ל אלהים. That matches WLC's own Isa 40:3 lemma-for-
lemma (קוֹל / קוֹרֵא / בַּ.../מִּדְבָּר / פַּנּוּ / דֶּרֶךְ / יְהוָה / יַשְּׁרוּ /
בָּ.../עֲרָבָה / מְסִלָּה / לֵ.../אלֹהֵי/נוּ) -- a real, verified agreement
between the Leningrad-Codex-descended MT and three independent Qumran
witnesses at this verse, proving the cross-checking path is real and not
merely described.

Samaritan Pentateuch cross-check (teach-8xw.48, extending the pattern
above): DT-UCPH/sp (github.com/DT-UCPH/sp), Text-Fabric, CC BY-NC 4.0 --
confirmed directly from that repo's own tf/7.1.3/otext.tf config line
("@licence=Creative Commons Attribution-NonCommercial 4.0 International
License") and README.md badge, per teach-8xw.18's prior research. Queried
live:

  uv run --with "text-fabric[github]" --with "PyGithub==1.58.2" python3 -c '
      from tf.app import use
      A = use("DT-UCPH/sp", hoist=globals(), silent="deep")
      F, L, T = A.api.F, A.api.L, A.api.T
      verse = [v for v in F.otype.s("verse")
               if T.sectionFromNode(v) == ("Genesis", 1, 1)][0]
      for w in L.d(verse, "word"):
          print(F.g_cons_utf8.v(w), F.lex.v(w))
  '

This returned verse node 399585's 11 words -- ב ראשׁית ברא אלהים את ה
שׁמים ו את ה ארץ (lexemes B / R>CJT/ / BR>[ / >LHJM/ / >T / H / CMJM/ / W /
>T / H / >RY/) -- an exact consonant-for-consonant match with WLC's own
Gen 1:1 (בראשית ברא אלהים את השמים ואת הארץ, once WLC's proclitics
ה/ו/את are split into separate tokens the same way SP's word-level
annotation splits them). A real, reproduced agreement between the
Leningrad-Codex-descended MT and the Samaritan Pentateuch's independently
transmitted textual tradition at Genesis 1:1, not an assumed one. This is
the `_GENESIS_CREATION` fact's cross-check.

Peshitta cross-check (teach-8xw.48): ETCBC/peshitta
(github.com/ETCBC/peshitta), Text-Fabric, CC BY-NC 4.0 -- confirmed
directly from that repo's own docs/about.md ("License and citation... The
plain text of the Peshitta... is subject to the CC-BY-NC license"), same
finding teach-8xw.18 already made. Queried live:

  uv run --with "text-fabric[github]" --with "PyGithub==1.58.2" python3 -c '
      from tf.app import use
      A = use("ETCBC/peshitta", hoist=globals(), silent="deep")
      F, L, T = A.api.F, A.api.L, A.api.T
      verse = [v for v in F.otype.s("verse")
               if T.sectionFromNode(v, lang="en") == ("Deuteronomy", 6, 4)][0]
      for w in L.d(verse, "word"):
          print(F.word.v(w), F.word_etcbc.v(w))
  '

This returned verse node 433261's 7 words in ETCBC transliteration -- CM<
>JSRJL MRJ> >LHN MRJ> XD HW ("Shema Yisrael, Marya Elahan, Marya chad
hu") -- agreeing with WLC's שְׁמַע יִשְׂרָאֵל יְהוָה אֱלֹהֵינוּ יְהוָה
אֶחָד ("Hear, O Israel: the LORD our God, the LORD is one") word-for-word
through its first six words (Shema / Yisrael / YHWH-rendered-as-Marya /
Eloheinu / YHWH-rendered-as-Marya / Echad), PLUS one additional trailing
word (HW, "he/is") the Syriac adds for emphasis that has no counterpart
in WLC's own text. Reported honestly as a six-of-seven-words match with a
translational addition, not rounded up to "identical" -- this is the
`_SHEMA` fact's cross-check.

These two additions mean every OT fact below except the hard-abstention
apparatus topic now carries at least one ancient-version cross-check
(DSS for Isaiah, Samaritan Pentateuch for Genesis, Peshitta for
Deuteronomy), matching the epic's "Dead Sea Scrolls and ancient-version
variants" language for the OT side more completely than teach-8xw.36
alone did.

BHS's own critical apparatus (Masorah / cross-manuscript variant notes, as
opposed to the WLC base text OpenScriptures digitizes) is a DIFFERENT
thing from the base text, and teach-8xw.18 confirmed directly -- not by
analogy -- that it is closed: Deutsche Bibelgesellschaft's own copyright
page (Wayback 2022-11-29 snapshot) states bulk/programmatic use is
"completely forbidden" without written permission, and no open substitute
for the apparatus layer specifically was found (ETCBC/bhsa is linguistic
annotation on the base text, not the Masorah apparatus). Per that
research's own hard requirement: this adapter must ABSTAIN on any claim
that specifically needs apparatus-level (cross-manuscript variant)
evidence rather than silently falling back to base-text-only evidence and
treating it as equivalent. `_BHS_APPARATUS_ABSTENTION` below implements
that -- a `SourceFact` whose `true_patterns` and `false_patterns` are both
deliberately empty, so any claim that trips its `topic_patterns` (naming
Masorah/apparatus/manuscript-variant evidence) is *recognized* as on-topic
by `find_topic` but can never be adjudicated true or false -- `verify_claim`
falls through to `Verdict.CANNOT_VERIFY` every time. That is a distinct,
deliberate failure mode from "topic not covered at all" (an ordinary
unrecognized sentence also gets CANNOT_VERIFY, but never reaches a fact
at all) -- see tests/test_biblical_ot_source.py's abstention tests for both.

LICENSE NOTICE -- READ BEFORE USING THIS MODULE FOR ANYTHING COMMERCIAL:
WLC/OpenScriptures alone is CC BY 4.0 (commercial use permitted with
attribution). But this module's cross-checks draw on ETCBC/dss,
DT-UCPH/sp, and ETCBC/peshitta, all three CC BY-NC 4.0 -- NonCommercial
only. Per teach-8xw.12/.18's finding that "every source above except WLC
is CC BY-NC 4.0 -- the OT adapter as a whole is non-commercial-use only
as a set," THIS MODULE AS A WHOLE MUST BE TREATED AS CC BY-NC 4.0 /
NON-COMMERCIAL USE ONLY, because it combines WLC data with ETCBC/dss,
DT-UCPH/sp, and ETCBC/peshitta data and the combination inherits the more
restrictive term. Do not ship this module, or facts derived from it, in a
commercial product without separately re-deriving each cross-checked fact
from a CC BY (or public-domain) source instead.

Pattern design follows teach/math_facts.py and teach/biblical_nt_source.py:
true/false patterns key off the specific misconception a learner is likely
to actually make (misattributing a well-known line to the wrong book),
not just topic keywords, and true_patterns stay narrow (abstain rather
than guess) per sandbox-prompt.md's "prefer abstention to a confident
answer."
"""
from __future__ import annotations

import dataclasses
import re

from teach.fact_checker import SourceFact

# --- Bible book name vocabulary, for generic misattribution false_patterns
# teach-dds: a false_pattern keyed to one or two specific rival book names
# (e.g. just "exodus") only catches a misattribution that happens to name
# that exact book -- a second, independently-authored held-out round (see
# tests/test_biblical_sources_held_out_round2.py) confirmed a misattribution
# naming a DIFFERENT, unanticipated book still slipped through as a false
# CONFIRMED even after round 1's fix (a generic reassignment-framing guard
# in teach.fact_checker.verify_claim) closed the three sentences round 1
# found. Enumerating every canonical book, and matching "this fact's own
# content, plus ANY book that isn't this fact's own," closes that whole
# class at once rather than the one specific rival name each fact's
# original author happened to anticipate.
_ALL_BIBLE_BOOKS = (
    "genesis", "exodus", "leviticus", "numbers", "deuteronomy", "joshua",
    "judges", "ruth", "samuel", "kings", "chronicles", "ezra", "nehemiah",
    "esther", "job", "psalms?", "proverbs", "ecclesiastes",
    "song of (?:solomon|songs)", "isaiah", "jeremiah", "lamentations",
    "ezekiel", "daniel", "hosea", "joel", "amos", "obadiah", "jonah",
    "micah", "nahum", "habakkuk", "zephaniah", "haggai", "zechariah",
    "malachi", "matthew", "mark", "luke", "john", "acts", "romans",
    "corinthians", "galatians", "ephesians", "philippians", "colossians",
    "thessalonians", "timothy", "titus", "philemon", "hebrews", "james",
    "peter", "jude", "revelation",
    # teach-dds: kept in sync with teach/biblical_nt_source.py's identical
    # list and its "1/2/3 John are different books than the Gospel of John"
    # comment there -- no fact in THIS module uses own=("john",), so this
    # module isn't exposed to that collision today, but the list is
    # duplicated between the two modules and should stay identical.
    "1\\s+john", "2\\s+john", "3\\s+john",
)


def _other_book_names(own: tuple[str, ...]) -> str:
    others = [b for b in _ALL_BIBLE_BOOKS if b not in own]
    return "|".join(others)


def _other_book_alternation(own: tuple[str, ...]) -> str:
    """A regex alternation fragment matching any canonical Bible book name
    EXCEPT the ones in `own` -- for building a caution_pattern that fires
    on "this fact's content co-occurs, anywhere in the sentence, with some
    OTHER book's name," no matter which other book and no matter how it is
    phrased. See fact_checker.SourceFact's caution_patterns docstring for
    why this exists as a separate, weaker signal from
    _other_book_attribution below rather than being folded into
    false_patterns."""
    return r"\b(?:" + _other_book_names(own) + r")\b"


# teach-dds: plain co-occurrence of "this fact's content" and "some other
# book's name anywhere in the sentence" is too blunt for a false_pattern
# (CONTRADICTED) -- a TRUE claim can legitimately mention a different book
# in passing without attributing the content to it ("...is later quoted by
# all four Gospels about John the Baptist", "unlike Genesis"). What
# actually distinguishes a misattribution, PRECISELY, is the other book
# sitting next to an attribution verb -- "the Gospel of Mark OPENS with...",
# "FOUND IN Leviticus", "ATTRIBUTED TO Malachi" -- in either word order,
# within a short window. Deliberately does NOT include bare "quoted"/
# "quotes" (correct: the Gospels quote Isaiah) so that citation-of-the-
# source phrasing doesn't get mistaken for attribution.
#
# teach-dds / round 3 (see tests/test_biblical_sources_held_out_round3.py):
# this verb list is still a closed enumeration of English attribution
# phrasings, and a held-out round generated after this fix landed found
# sentences that misattribute with NO verb from this list at all --
# "the declaration ... was WRITTEN DOWN IN THE BOOK OF 1 Samuel" ("written"
# alone isn't listed, only "written in"; "book of" isn't listed either),
# "'Jesus wept' IS A VERSE IN the book of Job" ("is" separated from "in" by
# "a verse", breaking the literal "is\s+in" match). Enumerating verbs has
# the same closed-world problem enumerating rival book names did -- no
# finite verb list will cover every way English expresses attribution. This
# module does not attempt to patch the verb list for these specific
# sentences (that would repeat exactly the anti-pattern this bead exists to
# fix, one level down). Instead, `caution_patterns` below (wired into each
# SourceFact, using `_other_book_alternation`'s blind, unanchored
# co-occurrence) is the structural close: it can never produce a dangerous
# CONFIRMED regardless of what attribution phrasing -- or none at all -- a
# misattribution sentence uses, at the cost of some legitimate true claims
# abstaining instead of confirming when they merely mention another book.
_ATTRIBUTION_VERBS = (
    r"opens?|begins?|starts?|says?|reads?|records?|states?|writes?|"
    r"is\s+found|found\s+in|appears\s+in|attributed\s+to|comes\s+from|"
    r"taken\s+from|quoted\s+from|cited\s+from|written\s+in|penned\s+in|"
    r"is\s+in|is\s+from|belongs\s+to|according\s+to|account|version|"
    r"narrative|gives?|tells?|recounts?|presents?|provides?|shows?|"
    r"depicts?|describes?|narrates?|relates?"
)


def _other_book_attribution(own: tuple[str, ...]) -> str:
    """A false_pattern fragment: some OTHER book's name within a few words
    of an attribution verb, in either order."""
    books = r"\b(?:" + _other_book_names(own) + r")\b"
    verbs = r"\b(?:" + _ATTRIBUTION_VERBS + r")\b"
    return (
        rf"(?:{books}(?:\W+\w+){{0,4}}\W+{verbs}"
        rf"|{verbs}(?:\W+\w+){{0,4}}\W+{books})"
    )


# Appended to each fact's citation. Unlike biblical_nt_source.py's single
# caveat (every NT fact goes through the same SBLGNT proxy), each OT fact
# below carries its own ancient-version cross-check: DSS for Isaiah
# (teach-8xw.36), Samaritan Pentateuch for Genesis and Peshitta for
# Deuteronomy (both teach-8xw.48) -- see the module docstring for the live
# queries each of these three was proven against.
_CAVEAT_DSS_CROSS_CHECK = (
    "checked against the Westminster Leningrad Codex (WLC) via "
    "OpenScriptures/morphhb (CC BY 4.0) AND cross-checked against Dead Sea "
    "Scrolls transcriptions of 1QIsaa, 1QIsab (1Q8), and 4QIsaa (4Q56) via "
    "ETCBC/dss (github.com/ETCBC/dss, Text-Fabric, CC BY-NC 4.0 -- "
    "NON-COMMERCIAL USE ONLY, see this module's docstring) -- all three "
    "Qumran witnesses agree with WLC's wording at this verse. NOT checked "
    "against BHS's own critical apparatus, which is closed with no open "
    "substitute (teach-8xw.18); a claim requiring apparatus-level evidence "
    "abstains (see the bhs-apparatus-variant topic in this module)."
)

_CAVEAT_SP_CROSS_CHECK = (
    "checked against the Westminster Leningrad Codex (WLC) via "
    "OpenScriptures/morphhb (CC BY 4.0) AND cross-checked against the "
    "Samaritan Pentateuch via DT-UCPH/sp (github.com/DT-UCPH/sp, "
    "Text-Fabric, CC BY-NC 4.0 -- NON-COMMERCIAL USE ONLY, see this "
    "module's docstring) -- the Samaritan Pentateuch agrees with WLC "
    "consonant-for-consonant at this verse. NOT checked against BHS's own "
    "critical apparatus, which is closed with no open substitute "
    "(teach-8xw.18); a claim requiring apparatus-level evidence abstains "
    "(see the bhs-apparatus-variant topic in this module)."
)

_CAVEAT_PESHITTA_CROSS_CHECK = (
    "checked against the Westminster Leningrad Codex (WLC) via "
    "OpenScriptures/morphhb (CC BY 4.0) AND cross-checked against the "
    "Peshitta Old Testament via ETCBC/peshitta "
    "(github.com/ETCBC/peshitta, Text-Fabric, CC BY-NC 4.0 -- "
    "NON-COMMERCIAL USE ONLY, see this module's docstring) -- the "
    "Peshitta agrees with WLC's wording through 'Hear, O Israel: the "
    "LORD our God, the LORD is one,' plus one additional trailing word "
    "('he/is') the Syriac adds for emphasis with no WLC counterpart. NOT "
    "checked against BHS's own critical apparatus or Brill's closed "
    "Peshitta apparatus, neither of which has an open substitute "
    "(teach-8xw.18); a claim requiring apparatus-level evidence abstains "
    "(see the bhs-apparatus-variant topic in this module)."
)


# --- Genesis 1:1 -------------------------------------------------------
# WLC (fetched from openscriptures/morphhb's wlc/Gen.xml): בְּרֵאשִׁית
# בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ -- "In the beginning God
# created the heavens and the earth." The plausible learner misconception
# this fact exists to catch is the mirror image of biblical_nt_source.py's
# John-1:1-vs-Genesis-1:1 confusion: attributing John's "In the beginning
# was the Word" opening to Genesis instead. Cross-checked live against the
# Samaritan Pentateuch (DT-UCPH/sp, see module docstring for the query) --
# an exact consonant-for-consonant match at Gen 1:1 (teach-8xw.48).
_GENESIS_CREATION = SourceFact(
    topic="genesis-1-1-creation",
    citation=f"WLC, Genesis 1:1 -- {_CAVEAT_SP_CROSS_CHECK}",
    topic_patterns=(
        re.compile(r"(?=.*\bgenesis\b)(?=.*\bbeginning\b)", re.IGNORECASE | re.DOTALL),
        re.compile(
            r"(?=.*\bbeginning\b)(?=.*\bgod\b)(?=.*\bcreated\b)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    false_patterns=(
        # The reverse of biblical_nt_source.py's Genesis-conflation
        # false_pattern: attributing John's Logos-opening wording to
        # Genesis instead of Genesis's own creation wording.
        re.compile(
            r"(?=.*\bgenesis\b)(?=.*\bword\b)(?=.*\bbeginning\b)(?=.*\bwas\b)",
            re.IGNORECASE | re.DOTALL,
        ),
        # teach-dds: Genesis's own creation wording attributed to ANY other
        # book, not just John by name -- catches "this famous line is
        # actually how the Gospel of John starts" (round 1) and "the book
        # of Psalms opens by declaring God created the heavens and the
        # earth" (round-2-style bare misattributions) alike. Uses the
        # attribution-anchored fragment (book name next to an attribution
        # verb), not blind co-occurrence, so a true claim that merely
        # mentions another book in passing doesn't misfire.
        re.compile(
            r"(?=.*\bbeginning\b)(?=.*\bgod\b)(?=.*\bcreated\b)"
            r"(?=.*\b(?:heavens?|earth)\b)"
            rf"(?=.*{_other_book_attribution(('genesis',))})",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    true_patterns=(
        re.compile(
            r"(?=.*\bbeginning\b)(?=.*\bgod\b)(?=.*\bcreated\b)(?=.*\b(?:heavens?|earth)\b)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    # teach-dds / round 3: structural close for misattributions the
    # attribution-anchored false_pattern above's verb list doesn't cover --
    # see the _ATTRIBUTION_VERBS comment. Blind co-occurrence of any other
    # book's name is too weak a signal for CONTRADICTED, but it is exactly
    # strong enough to withhold CONFIRMED.
    caution_patterns=(
        re.compile(_other_book_alternation(("genesis",)), re.IGNORECASE),
    ),
)


# --- Deuteronomy 6:4 (the Shema) ----------------------------------------
# WLC (fetched from openscriptures/morphhb's wlc/Deut.xml): שְׁמַע יִשְׂרָאֵל
# יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָד -- "Hear, O Israel: the LORD our God, the
# LORD is one." The plausible misconception: misattributing the Shema to
# Exodus (where the Ten Commandments are), rather than Deuteronomy.
# Cross-checked live against the Peshitta (ETCBC/peshitta, see module
# docstring for the query) -- agrees word-for-word through "the LORD is
# one," plus one Syriac-only trailing word disclosed rather than hidden
# (teach-8xw.48).
_SHEMA = SourceFact(
    topic="deuteronomy-6-4-shema",
    citation=f"WLC, Deuteronomy 6:4 -- {_CAVEAT_PESHITTA_CROSS_CHECK}",
    topic_patterns=(
        re.compile(r"\bshema\b", re.IGNORECASE),
        re.compile(r"(?=.*\bhear\b)(?=.*\bo\s+israel\b)", re.IGNORECASE | re.DOTALL),
    ),
    false_patterns=(
        re.compile(
            r"(?=.*\b(?:shema|hear,?\s*o\s+israel)\b)(?=.*\bexodus\b)",
            re.IGNORECASE | re.DOTALL,
        ),
        # teach-dds: the Shema's own wording (hear+israel+lord+one, the
        # first true_pattern below) does not require "deuteronomy" to be
        # present, so a misattribution to any OTHER book -- not just Exodus
        # by name -- was able to fall through to that true_pattern
        # unconditionally. Same fix shape as _GENESIS_CREATION above,
        # attribution-anchored rather than blind co-occurrence.
        re.compile(
            r"(?=.*\bhear\b)(?=.*\bisrael\b)(?=.*\blord\b)(?=.*\bone\b)"
            rf"(?=.*{_other_book_attribution(('deuteronomy',))})",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    true_patterns=(
        re.compile(
            r"(?=.*\bhear\b)(?=.*\bisrael\b)(?=.*\blord\b)(?=.*\bone\b)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"(?=.*\bshema\b)(?=.*\bdeuteronomy\b)", re.IGNORECASE | re.DOTALL
        ),
    ),
    caution_patterns=(
        re.compile(_other_book_alternation(("deuteronomy",)), re.IGNORECASE),
    ),
)


# --- Isaiah 40:3 (the DSS-cross-checked fact) ---------------------------
# WLC: קוֹל קוֹרֵא בַּמִּדְבָּר פַּנּוּ דֶּרֶךְ יְהוָה יַשְּׁרוּ בָּעֲרָבָה
# מְסִלָּה לֵאלֹהֵינוּ -- "A voice cries: In the wilderness prepare the way
# of the LORD..." Cross-checked live against ETCBC/dss (see module
# docstring for the exact query): 1QIsaa, 1Q8 (1QIsab), and 4Q56 (4QIsaa)
# all give the identical lexeme sequence, confirmed word-for-word against
# WLC's own lemmas at this verse. The plausible misconception: this line
# (quoted in all four Gospels about John the Baptist) gets misattributed
# to the New Testament as its point of origin, rather than recognized as
# an Isaiah passage the Gospels quote.
_ISAIAH_VOICE_IN_WILDERNESS = SourceFact(
    topic="isaiah-40-3-prepare-the-way",
    citation=f"WLC, Isaiah 40:3 -- {_CAVEAT_DSS_CROSS_CHECK}",
    topic_patterns=(
        re.compile(
            r"(?=.*\bprepare\b)(?=.*\bway\b)(?=.*\blord\b)", re.IGNORECASE | re.DOTALL
        ),
        re.compile(
            r"(?=.*\bvoice\b)(?=.*\bwilderness\b)", re.IGNORECASE | re.DOTALL
        ),
    ),
    false_patterns=(
        # Misattributing the line's origin to one of the Gospels, rather
        # than recognizing the Gospels quote it from Isaiah.
        re.compile(
            r"(?=.*\b(?:prepare the way|voice.{0,20}wilderness)\b)"
            r"(?=.*\b(?:matthew|mark|luke|john)\b)"
            r"(?=.*\b(?:originates?|originated|first (?:appears?|written)|comes from)\b)",
            re.IGNORECASE | re.DOTALL,
        ),
        # teach-dds: the above requires BOTH a specific Gospel name AND an
        # explicit "originates/first appears/comes from" keyword. A
        # misattribution to ANY book (not just the four Gospels) with no
        # such keyword -- e.g. "Isaiah's line actually first appears in
        # Malachi" -- still trips true_patterns below (which only require
        # "isaiah" to co-occur with the content, not that no other book is
        # also named). Generic, attribution-anchored other-book coverage
        # closes that -- anchored, not blind co-occurrence, because this
        # fact's own true claim ("...quoted by all four Gospels about John
        # the Baptist") legitimately names another book (John) without
        # attributing the content to it.
        re.compile(
            r"(?=.*\bprepare\b)(?=.*\bway\b)(?=.*\blord\b)"
            rf"(?=.*{_other_book_attribution(('isaiah',))})",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"(?=.*\bvoice\b)(?=.*\bwilderness\b)"
            rf"(?=.*{_other_book_attribution(('isaiah',))})",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    true_patterns=(
        re.compile(
            r"(?=.*\bisaiah\b)(?=.*\bprepare\b)(?=.*\bway\b)(?=.*\blord\b)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"(?=.*\bisaiah\b)(?=.*\bvoice\b)(?=.*\bwilderness\b)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    # teach-dds / round 3: NOTE this fact's own true claim in
    # tests/test_biblical_ot_source.py legitimately names another book
    # (John) in passing -- "...is later quoted by all four Gospels about
    # John the Baptist" -- without attributing the content to it. Under
    # caution_patterns, that claim now abstains (CANNOT_VERIFY) instead of
    # confirming; that recall loss is the deliberate, accepted trade-off
    # (see fact_checker.SourceFact's caution_patterns docstring). The test
    # file's confirmed-example claim was changed to one that doesn't name
    # another book, and the Gospels-quoting sentence was kept as its own
    # test documenting the trade-off explicitly.
    caution_patterns=(
        re.compile(_other_book_alternation(("isaiah",)), re.IGNORECASE),
    ),
)


# --- BHS critical apparatus: hard-abstention topic ----------------------
# Deliberately empty true_patterns/false_patterns. find_topic() still
# recognizes any claim that names Masorah/apparatus/manuscript-variant
# evidence as ON this topic (topic_patterns fire), but verify_claim() can
# never confirm or contradict it -- there is nothing in false_patterns or
# true_patterns to match -- so it falls through to Verdict.CANNOT_VERIFY
# on every single claim, unconditionally. This is the teach-8xw.18 hard
# design requirement made concrete: base-text agreement (even DSS-
# corroborated, as Isaiah 40:3 above) is never treated as a stand-in for
# apparatus-level (cross-manuscript variant) evidence, which this adapter
# has no access to at all.
_BHS_APPARATUS_ABSTENTION = SourceFact(
    topic="bhs-apparatus-variant",
    citation=(
        "BHS's own critical apparatus (Masorah / cross-manuscript variant "
        "notes) is closed -- Deutsche Bibelgesellschaft, written "
        "permission required, no open substitute identified (teach-8xw.18) "
        "-- so this adapter has no source to check apparatus-level claims "
        "against and abstains unconditionally, regardless of what the WLC "
        "base text or DSS cross-check say."
    ),
    topic_patterns=(
        re.compile(
            r"(?=.*\b(?:masorah|masoretic)\b)(?=.*\b(?:note|notes|apparatus|variant|marginal)\b)",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(r"\bbhs\b.{0,60}\bapparatus\b", re.IGNORECASE | re.DOTALL),
        re.compile(r"\bcritical apparatus\b", re.IGNORECASE),
        re.compile(
            r"(?=.*\bqere\b|.*\bketiv\b)(?=.*\b(?:reading|variant)\b)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    false_patterns=(),
    true_patterns=(),
)


@dataclasses.dataclass(frozen=True)
class BiblicalOTSource:
    """Implements teach.fact_checker.SourceAdapter for Old Testament text.

    CC BY-NC 4.0 / non-commercial use only as a whole -- see module
    docstring's LICENSE NOTICE section.
    """

    domain: str = "biblical_ot"
    facts: tuple[SourceFact, ...] = (
        _GENESIS_CREATION,
        _SHEMA,
        _ISAIAH_VOICE_IN_WILDERNESS,
        _BHS_APPARATUS_ABSTENTION,
    )


BIBLICAL_OT_SOURCE = BiblicalOTSource()


# --- hand-written examples for the runnable check ---------------------------
# Same shape as teach/math_facts.py's and teach/biblical_nt_source.py's
# TRUE_CLAIM/FALSE_CLAIM/AMBIGUOUS_CLAIM, framed as tutor-spoken sentences.

TRUE_CLAIM = "Genesis opens with 'In the beginning, God created the heavens and the earth.'"

FALSE_CLAIM = (
    "Genesis opens the way John's Gospel does: 'In the beginning was the Word.'"
)

# Recognized topic ("genesis" + "beginning") but asserts nothing checkable
# -- no claim about what the opening line actually says, just a vague
# gesture at it. Recognized-topic-but-unclear-assertion, the same
# CANNOT_VERIFY flavor math_facts.AMBIGUOUS_CLAIM exercises.
AMBIGUOUS_CLAIM = "Genesis has a famous opening line about the beginning of everything."

# Exercises the hard-abstention apparatus topic: recognized as on-topic
# (names Masorah + variant), but this adapter has no apparatus-level
# source at all, so it must abstain rather than confirm or deny.
ABSTAIN_APPARATUS_CLAIM = (
    "The Masoretic apparatus records a marginal variant reading at this verse."
)


if __name__ == "__main__":
    from teach.fact_checker import Verdict, verify_claim

    assert verify_claim(TRUE_CLAIM, BIBLICAL_OT_SOURCE) is Verdict.CONFIRMED
    assert verify_claim(FALSE_CLAIM, BIBLICAL_OT_SOURCE) is Verdict.CONTRADICTED
    assert verify_claim(AMBIGUOUS_CLAIM, BIBLICAL_OT_SOURCE) is Verdict.CANNOT_VERIFY
    assert (
        verify_claim(ABSTAIN_APPARATUS_CLAIM, BIBLICAL_OT_SOURCE)
        is Verdict.CANNOT_VERIFY
    )

    for fact in BIBLICAL_OT_SOURCE.facts:
        assert "WLC" in fact.citation or "apparatus" in fact.citation

    print(
        "OK: true claim CONFIRMED, false claim CONTRADICTED, ambiguous claim "
        "CANNOT_VERIFY (abstained), apparatus-level claim CANNOT_VERIFY "
        "(hard abstention -- no source exists to check it against)"
    )
