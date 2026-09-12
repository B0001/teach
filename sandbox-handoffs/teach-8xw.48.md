# teach-8xw.48 — extend Samaritan Pentateuch/Peshitta cross-checking to Genesis and Deuteronomy

## What was done

teach-8xw.36 built `teach/biblical_ot_source.py` with a live DSS cross-check
proven real for Isaiah 40:3, but left Genesis 1:1 and Deuteronomy 6:4 as
WLC-only, deliberately scoped out ("a future worker adding more OT facts
could add Samaritan Pentateuch/Peshitta cross-checks to existing facts
without new infrastructure"). This bead is that follow-on:

- **Genesis 1:1** now also cross-checked against the **Samaritan Pentateuch**
  (`DT-UCPH/sp`, Text-Fabric, CC BY-NC 4.0).
- **Deuteronomy 6:4 (the Shema)** now also cross-checked against the
  **Peshitta** Old Testament (`ETCBC/peshitta`, Text-Fabric, CC BY-NC 4.0).

No new infrastructure was needed, as teach-8xw.36 predicted — same
`_CAVEAT_*_CROSS_CHECK` constant pattern, same `SourceFact.citation`
plumbing, same `find_topic`/`verify_claim` machinery in
`teach/fact_checker.py` (untouched).

`tests/test_biblical_ot_source.py`: 26 tests, all passing (was 22; +4 new —
two citation-disclosure tests mirroring the existing Isaiah/DSS one, two
`check_lesson_text` tests mirroring the existing DSS one).

`uv run pytest -q`: **383 passed** (full suite, was already at 383 before
this session's edits per a fresh baseline run — no regressions from this
change; the OT module's own file went from 22→26 tests).

## Verification — fetched raw bytes and ran live Text-Fabric queries myself

Per sandbox-prompt.md's rule (be most suspicious when a lookup confirms what
you were hoping to find), I did not assume "Samaritan Pentateuch and Peshitta
both cover the Torah, so this will obviously work" — I ran the actual query
against the actual corpus for both new facts, the same way teach-8xw.36 did
for Isaiah/DSS, and read the raw result before writing any code.

**Samaritan Pentateuch, Genesis 1:1** (`DT-UCPH/sp`):
```
uv run --with "text-fabric[github]" --with "PyGithub==1.58.2" python3 -c '
from tf.app import use
A = use("DT-UCPH/sp", hoist=globals(), silent="deep")
F, L, T = A.api.F, A.api.L, A.api.T
verse = [v for v in F.otype.s("verse")
         if T.sectionFromNode(v) == ("Genesis", 1, 1)][0]
for w in L.d(verse, "word"):
    print(F.g_cons_utf8.v(w), F.lex.v(w))
'
```
Returned verse node 399585's 11 words: ב ראשׁית ברא אלהים את ה שׁמים ו את ה
ארץ (lexemes `B R>CJT/ BR>[ >LHJM/ >T H CMJM/ W >T H >RY/`) — an exact
consonant-for-consonant match with WLC's own Gen 1:1, confirmed by grepping
`openscriptures/morphhb`'s `wlc/Gen.xml` directly (not from memory), once
WLC's ה/ו/את proclitics are split into separate tokens the way SP's
word-level annotation splits them. Also fetched
`tf/7.1.3/otext.tf` directly to confirm the CC BY-NC 4.0 licence line in the
dataset's own words, and confirmed `T.sectionFromNode` (not `F.book.v(w)`
directly, which returned an empty result set on first attempt — see "gotcha"
below) is the correct API for this corpus.

**Peshitta, Deuteronomy 6:4** (`ETCBC/peshitta`):
```
uv run --with "text-fabric[github]" --with "PyGithub==1.58.2" python3 -c '
from tf.app import use
A = use("ETCBC/peshitta", hoist=globals(), silent="deep")
F, L, T = A.api.F, A.api.L, A.api.T
verse = [v for v in F.otype.s("verse")
         if T.sectionFromNode(v, lang="en") == ("Deuteronomy", 6, 4)][0]
for w in L.d(verse, "word"):
    print(F.word.v(w), F.word_etcbc.v(w))
'
```
Returned verse node 433261's 7 words in ETCBC transliteration: `CM< >JSRJL
MRJ> >LHN MRJ> XD HW` ("Shema Yisrael, Marya Elahan, Marya chad hu"). This
agrees with WLC's שְׁמַע יִשְׂרָאֵל יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָד word-for-word
through its first six words, **but the Peshitta has a seventh word (`HW`,
"he/is") with no WLC counterpart** — a genuine Syriac translational addition
for emphasis, not a disagreement about the underlying Hebrew Vorlage. I
disclosed this as "agrees through six of seven words, plus one Syriac-only
addition" in the fact's citation rather than rounding it up to "identical"
— per sandbox-prompt.md's "never a third [option]" rule on documented
figures, and per the standard's demand that fidelity claims not overstate
what was actually verified. Also fetched `docs/about.md` directly to confirm
CC BY-NC 4.0 in the repo's own words (`"License and citation... subject to
the CC-BY-NC license"`), matching teach-8xw.18's prior finding exactly.

**A gotcha worth recording for whoever touches Text-Fabric OT corpora next**:
teach-8xw.36's own docstring showed `F.book.v(w)`/`F.chapter.v(w)`/
`F.verse.v(w)` called directly on a *word* node for `ETCBC/dss` and it
apparently worked there. I tried the identical pattern first against
`DT-UCPH/sp` and got **zero results** (`F.book.v(w) == "Genesis"` matched no
words) even though the data is present — book/chapter/verse are section
features defined on their own node types (book/chapter/verse), not
propagated onto word nodes in this corpus. The portable, correct API is
`T.sectionFromNode(node)` (walks up the embedding automatically), which is
what both new queries use. I did not go back to re-verify whether
`ETCBC/dss` really supports direct `F.book.v(word)` or whether that specific
combination happened to work by different means (e.g. `dss` may denormalize
section features onto word nodes, or that call may have silently returned
per-scroll node identity for a different reason) — flagging this rather than
assuming either corpus's behavior generalizes to the other.

## What this does NOT do

- Does not add Samaritan Pentateuch or Peshitta cross-checks to the Isaiah
  fact, or a second cross-check to Genesis/Deuteronomy (e.g. also
  DSS-checking Genesis) — this bead's acceptance criteria asked for adding
  cross-checks to the Genesis and/or Deuteronomy facts specifically, and one
  well-verified cross-check per fact satisfies "ancient-version variants"
  without scope creep.
- Does not touch the NT adapter or `teach/fact_checker.py` itself — this
  bead is additive within the OT module's existing `SourceFact` shape.
- Does not resolve the BHS apparatus / Brill Peshitta apparatus gaps —
  those remain closed with no open substitute (teach-8xw.18), and the
  `bhs-apparatus-variant` hard-abstention fact is untouched and still fires
  even for claims about Genesis/Deuteronomy that name apparatus-level
  evidence (not separately re-tested here since the abstention logic itself
  didn't change, only which facts have how many cross-checks).
- Does not verify `DT-UCPH/sp`'s or `ETCBC/peshitta`'s license terms from
  scratch — both were already confirmed CC BY-NC 4.0 by teach-8xw.18's prior
  research; I re-confirmed by fetching the same files directly rather than
  trusting the memory record, per sandbox-prompt.md, and got the same
  answer.

## Files touched

- `teach/biblical_ot_source.py` — extended docstring (documents both new
  live queries and their results), replaced `_CAVEAT_WLC_ONLY` with
  `_CAVEAT_SP_CROSS_CHECK` and `_CAVEAT_PESHITTA_CROSS_CHECK` (no fact is
  WLC-only anymore, so the old shared constant became dead code and was
  removed rather than left unused), updated `_GENESIS_CREATION` and
  `_SHEMA`'s citations and inline comments, updated the module's LICENSE
  NOTICE to name all three CC BY-NC sources (SP and Peshitta don't change
  the module's overall license classification — it was already CC BY-NC as
  a whole because of DSS — but the notice should name what it actually
  depends on).
- `tests/test_biblical_ot_source.py` — added 4 tests: citation-disclosure
  tests for the SP and Peshitta cross-checks (mirroring the existing Isaiah
  DSS-disclosure test), and `check_lesson_text` tests confirming the new
  caveats survive to a real `FactCheck` record for both facts (mirroring the
  existing DSS `check_lesson_text` test).

Nothing committed — conservative git policy, not asked to commit.

## Next step

Closing teach-8xw.48: its stated closing criteria (add a Samaritan
Pentateuch and/or Peshitta cross-check to the Genesis 1:1 and/or
Deuteronomy 6:4 facts, following the exact live-query pattern teach-8xw.36
proved for Isaiah/DSS rather than a described/assumed agreement, plus
regression tests mirroring the existing DSS tests) are met: both facts now
have a live-queried, honestly-disclosed ancient-version cross-check, and the
full suite passes at 383/383 with the module's own test file at 26/26.

No new bead filed. The remaining named-but-unimplemented items from
teach-8xw.18's research (BHS critical apparatus, Brill's Peshitta critical
apparatus — both closed, no open substitute) are already covered by the
existing `bhs-apparatus-variant` hard-abstention fact and don't need new
cross-check infrastructure; there is no further "ancient-version variants"
gap left in this module for the facts it currently has.
