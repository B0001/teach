# teach-8xw.37: NT biblical SourceAdapter (SBLGNT proxy)

## Status: closing as done

The work was already written and committed at `ce3300f` (a prior session's
batched "6 beads" commit), but that commit's own message flagged it as
unfinished: "teach-8xw.37 ... is still claimed and its work is in this
commit ... with no handoff written yet. Do not read its passing tests as
completion." So this session did not write new code -- it independently
verified the existing `teach/biblical_nt_source.py` and
`tests/test_biblical_nt_source.py` against the bead's acceptance criteria
and against the source data itself, per sandbox-prompt.md's rule that a
prior session's claims (even one's own) are not evidence until checked.

## What I verified myself, not by trusting the file's docstring or a prior transcript

1. **SBLGNT license** -- `curl -s https://api.github.com/repos/Faithlife/SBLGNT`
   -> `license.key: "cc-by-4.0"`. Confirmed directly, not re-summarized.

2. **The two seeded facts (John 1:1, John 11:35) are NOT among SBLGNT's
   540+ divergence points from NA/UBS.** Fetched
   `https://raw.githubusercontent.com/Faithlife/SBLGNT/master/data/sblgntapp/text/John.txt`
   (SBLGNT's own comparative apparatus against WH/Tregelles/NA28/RP) myself
   and grepped it:
   - `grep -n "^John 1:1$"` -> no match (exact-anchor, since a naive prefix
     grep for "John 1:1" also matches "John 1:15/1:16/1:18/1:19" -- caught
     and corrected that false positive in my own check before trusting it).
   - `grep -n "^John 11:35"` -> no match.
   - As a control, `grep -n "^John 5:11"` (a verse the module's docstring
     names as a real divergence, NOT used as seed data) -> matched, and the
     apparatus entry (`ὃς δὲ WH Treg ] ὁ δὲ NA28; – RP`) is exactly what the
     docstring describes. This is the strongest evidence the apparatus file
     is actually being read correctly and the absence for the two seeded
     verses is a real absence, not a parsing miss.

3. **The seeded facts' content matches the actual SBLGNT text**, not just
   the apparatus's silence about them. Fetched
   `.../data/sblgnt/text/John.txt` (the running text, not the apparatus):
   - `John 1:1` -> `Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ ὁ λόγος ἦν πρὸς τὸν θεόν, καὶ
     θεὸς ἦν ὁ λόγος.` = "In the beginning was the Word, and the Word was
     with God, and the Word was God" -- matches `TRUE_CLAIM`.
   - `John 11:35` -> `ἐδάκρυσεν ὁ Ἰησοῦς.` = "Jesus wept." -- matches the
     fact's true_patterns.

4. **Caveat propagation is structural, not just tested for the happy
   path.** `teach/fact_checker.py:check_lesson_text` sets
   `citation=fact.citation` on every `FactCheck` before it even computes
   `verdict`, so the SBLGNT-vs-NA/UBS disclosure reaches CONFIRMED,
   CONTRADICTED, *and* CANNOT_VERIFY records unconditionally -- confirmed by
   reading the function body, not inferred from the NT test file (which
   only exercises CONFIRMED/CONTRADICTED explicitly; CANNOT_VERIFY coverage
   for citation-carrying comes from the shared fact_checker code path, which
   is exercised generically by `tests/test_fact_checker.py`).

5. **ETCBC/syrnt was not used** -- confirmed by reading the file; only
   `Faithlife/SBLGNT` appears.

## Test results

- `uv run pytest tests/test_biblical_nt_source.py` -> all pass (14 tests:
  true/false/ambiguous/off-topic claims, both directions of misattribution,
  false-beats-true tie-break, question-is-not-a-claim, and the caveat-
  disclosure tests on both `fact.citation` directly and through
  `check_lesson_text`).
- `uv run pytest` (full suite) -> 339 passed.
- `uv run python3 -m teach.biblical_nt_source` (standalone self-check) ->
  OK.

## How the 540-variation-unit caveat is actually handled (bead's (a) + (b), both)

- (a) per-fact: only seeded two verses, both individually confirmed absent
  from SBLGNT's own divergence apparatus (see #2 above) -- this adapter does
  not currently carry any fact that sits at a known SBLGNT/NA-UBS
  divergence point.
- (b) unconditional: every fact's `citation` includes a `_CAVEAT` string
  naming SBLGNT, the closed status of NA27/28/UBS4/5, and the "540+ known
  variation units" figure, and it ships on every verdict this adapter can
  produce (see #4 above) -- so even a future fact added without doing (a)
  still can't present a verdict as equivalent to an NA/UBS check.

## What's NOT covered (stating scope, not hiding it)

- Only two facts are seeded (John 1:1, John 11:35). This is a floor, not a
  measure of how well the adapter would generalize to other NT lesson
  content -- same caveat as every other fact_checker source module in this
  repo (math, OT). No held-out phrasing round has been run against this
  module; if one is wanted, file it as a new bead rather than treating
  these hand-written tests as generalization evidence.
- The "shortest verse in the New Testament" framing for John 11:35 is
  checked for correct *book attribution* (is it in John, not
  Luke/Mark/etc.), which is what SBLGNT can actually verify. The
  superlative claim itself ("shortest by word/letter count across all NT
  verses in Greek") is a separate, narrower trivia claim this adapter does
  not attempt to adjudicate -- the true/false patterns only ever check
  attribution, never the superlative. Worth noting if a future lesson makes
  the superlative claim explicit and precise (e.g. "shortest in Greek word
  count") rather than the loose popular framing this fact was seeded for.

## Housekeeping noticed but out of scope, left alone

- `teach/math_facts.py` has an uncommitted local diff (comment-only, +17
  lines) unrelated to this bead -- it documents a teach-8xw.40 correction
  about round-3 sentence reproducibility. Not touched; not part of this
  bead's deliverable. Left for whoever owns teach-8xw.40 to commit or
  discard.

## Git state at close

Not committed -- conservative git policy, no commit/push was requested for
this bead. `teach/biblical_nt_source.py` and `tests/test_biblical_nt_source.py`
were already committed at `ce3300f` prior to this session; nothing new needs
committing for this bead specifically.
