# teach-8xw.36 — Build the OT biblical SourceAdapter for fact_checker.py

## What was done

Built `teach/biblical_ot_source.py`, a `SourceAdapter` (per
`teach/fact_checker.py`'s Protocol) for Old Testament text, following the
same pattern `teach/biblical_nt_source.py` (teach-8xw.37) already
established for the New Testament side. Four `SourceFact`s:

1. **Genesis 1:1** (`genesis-1-1-creation`) — checked against WLC only.
   Catches the mirror image of the NT source's John/Genesis conflation:
   attributing John's "In the beginning was the Word" opening to Genesis.
2. **Deuteronomy 6:4, the Shema** (`deuteronomy-6-4-shema`) — checked
   against WLC only. Catches misattribution to Exodus.
3. **Isaiah 40:3** (`isaiah-40-3-prepare-the-way`) — checked against WLC
   **and cross-checked against DSS variant data via ETCBC/dss**, per this
   bead's specific requirement to prove the cross-checking path is real.
   Catches misattributing "prepare the way of the Lord" 's origin to one
   of the Gospels instead of recognizing they quote Isaiah.
4. **`bhs-apparatus-variant`** — a hard-abstention topic. `topic_patterns`
   recognizes claims naming Masorah/critical-apparatus/manuscript-variant
   evidence; `true_patterns` and `false_patterns` are both deliberately
   `()`, so `verify_claim` can never confirm or contradict it — every
   claim on this topic falls through to `CANNOT_VERIFY`, unconditionally,
   even when it names a verse (Isaiah 40:3) this adapter otherwise
   confirmed against WLC+DSS. This implements teach-8xw.18's hard design
   requirement: base-text (even DSS-corroborated) agreement must never be
   treated as a stand-in for apparatus-level (cross-manuscript variant)
   evidence, which this adapter has no access to at all.

`tests/test_biblical_ot_source.py`: 22 tests, all passing. Covers the
standard true/false/ambiguous triad per fact, the false-beats-true
ordering bias, both abstention flavors (off-topic vs. recognized-but-
apparatus-required), and that `check_lesson_text` — the real consumer-
facing entry point, not just `verify_claim` — carries the DSS/CC BY-NC
disclosure and the abstention through to a `FactCheck` record.

`uv run pytest -q`: **316 passed** (was 294 before this bead; +22 new).

## Verification — fetched raw bytes myself, not recalled

Per sandbox-prompt.md's rule ("fetch the raw bytes and read them
yourself... be most suspicious when the answer confirms exactly what you
were hoping to find"), every Hebrew wording and every license claim below
was checked against the actual source, not memory of what the verse says:

**Base text (WLC/OpenScriptures)**, fetched directly:
```
curl -sL https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Gen.xml
curl -sL https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Deut.xml
curl -sL https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Isa.xml
curl -sL https://raw.githubusercontent.com/openscriptures/morphhb/master/LICENSE.md
```
Confirmed CC BY 4.0, and confirmed the exact Hebrew word sequence at
Gen 1:1, Deut 6:4, and Isa 40:3 by grepping the verse's `<verse
osisID="...">` block directly (not from memory of "what Genesis 1:1 says
in English").

**DSS cross-check (ETCBC/dss)** — this is the part this bead specifically
required to be *proven real*, not just described. The repo is
Text-Fabric format, not plain grep-able text, so I installed and ran the
`text-fabric` package itself (pinning `PyGithub==1.58.2`; the current
PyGithub release breaks text-fabric's GitHub-backend rate-limit check —
`'RateLimitOverview' object has no attribute 'core'` — a real, reproducible
compatibility bug worth knowing about for whoever touches this next) and
queried the live corpus:

```
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
```
Returned Isaiah 40:3's lexemes for three independent scrolls — 1Qisaa (the
Great Isaiah Scroll), 1Q8 (1QIsab), and 4Q56 (4QIsaa) — all three
identical to each other and lemma-for-lemma identical to WLC's own Isa
40:3 reading. This is a genuine, reproduced agreement between the MT and
three Qumran witnesses, not an assumed one. Also fetched
`docs/about.md` directly to confirm ETCBC/dss's data license is CC BY-NC
4.0 in the repo's own words (not the MIT badge GitHub's top-level API
field reports — that covers the conversion code only, same caveat
teach-8xw.18 already flagged for ETCBC/peshitta).

**BHS apparatus closure** — not re-verified this session; teach-8xw.18
already confirmed directly (Wayback snapshot of Deutsche
Bibelgesellschaft's own copyright page) that it's closed with no open
substitute. Carried forward as-is per "prior research already done, do
not re-research."

## Design decisions worth flagging for the next worker

- **License scope**: WLC alone is CC BY 4.0 (commercial-safe), but this
  module as a whole is CC BY-NC 4.0 because the Isaiah fact's citation
  depends on ETCBC/dss data. The module docstring states this plainly
  under "LICENSE NOTICE" and the citation-level caveat text itself
  includes "NON-COMMERCIAL USE ONLY" so it survives being read out of
  context of the docstring. Genesis and Deuteronomy's own facts are
  WLC-only (no DSS dependency) and could in principle be extracted into a
  CC-BY-only module later if the NC constraint ever becomes a blocker —
  not done here, out of this bead's scope.
- **Apparatus abstention as an empty-pattern-set fact, not a special-cased
  branch in `verify_claim`**: this keeps `fact_checker.py` itself
  domain-ignorant (it never learns "OT" or "apparatus" as special
  concepts) while still getting hard, structural abstention — enforced by
  `find_topic`/`verify_claim`'s existing generic logic, not new logic in
  this bead. `tests/test_biblical_ot_source.py::test_apparatus_fact_has_no_true_or_false_patterns`
  locks in that this stays true patterns-empty rather than accidentally
  growing a matcher later.
- Only Isaiah's fact carries the DSS cross-check; Genesis and Deuteronomy
  are WLC-only. DSS transcriptions for Genesis/Deuteronomy exist in the
  same corpus in principle but doing all three would have been scope
  creep beyond "cross-check **at least one** fact" — filed nothing further
  since this was a known, deliberate scope boundary, not a gap I noticed
  and dropped.

## What this does NOT do

- Does not touch the NT adapter (`teach/biblical_nt_source.py`) — already
  built (teach-8xw.37).
- Does not implement Samaritan Pentateuch or Peshitta cross-checking —
  teach-8xw.18 researched their access terms (both CC BY-NC, Text-Fabric)
  but this bead's acceptance criteria only asked for WLC + DSS. Not filed
  as a new bead since the epic's "ancient-version variants" language is
  satisfied by the DSS cross-check already present; a future worker adding
  more OT facts could add Samaritan Pentateuch/Peshitta cross-checks to
  existing facts without new infrastructure.
- Does not wire `BIBLICAL_OT_SOURCE` into any lesson-generation or
  producer-side code — this bead is checker-side infrastructure only, same
  scope boundary as teach-8xw.37 before it.

## Files touched

- `teach/biblical_ot_source.py` (new)
- `tests/test_biblical_ot_source.py` (new, 22 tests)

Nothing committed — conservative git policy, not asked to commit.

## Next step

Closing teach-8xw.36: its acceptance criteria (SourceAdapter built,
seeded with WLC-verified facts, at least one DSS cross-check proven real
via a live query rather than described, apparatus-abstention as a tested
case, CC BY-NC license notice stated plainly) are all met, and the full
suite passes at 316/316.
