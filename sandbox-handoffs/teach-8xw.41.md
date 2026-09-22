# teach-8xw.41 handoff

## What this bead was

`teach/biblical_ot_source.py` (teach-8xw.36) and `teach/biblical_nt_source.py`
(teach-8xw.37) each had only ever been tested against fixtures written by
the same session that wrote their pattern code
(`tests/test_biblical_ot_source.py`, `tests/test_biblical_nt_source.py`).
teach-8xw.37's own handoff said explicitly: "No held-out phrasing round has
been run against this module... if one is wanted, file it as a new bead" —
this bead was that filing. Per sandbox-prompt.md's "you cannot hold out
examples from yourself," a self-authored test set is not evidence of
generalization.

## State at claim time

Marked `in_progress` but nothing had actually been done — no notes, no
uncommitted files related to biblical sources, no partial work in the
working tree. Checked `git status` and searched for any `*biblical*` or
`*held_out*`/`*generalization*` file that might have been left by a prior
worker; found none. Claimed and started from scratch.

## Method (matches teach-8xw.33's established precedent)

1. Read both adapter modules and both existing test files to understand
   what each `SourceFact`'s `topic_patterns`/`false_patterns`/
   `true_patterns` actually check.
2. Read `sandbox-handoffs/teach-8xw.33.md` for the precedent method, and
   `teach-8xw.40`'s correction of it — the critical lesson: **the round-3
   sentences from teach-8xw.33 were never fully preserved as runnable
   data**, only 3 of 12 survived, so the "1/12 CONTRADICTED" figure became
   unreproducible. This bead's own text calls this out explicitly and
   requires not repeating it.
3. Launched a single `Agent` (general-purpose) call with an explicit,
   repeated instruction: do not call any tool, do not read/search/inspect
   any file or repository, answer purely from your own knowledge. Asked it
   to write, for each of Genesis 1:1 / Deuteronomy 6:4 / Isaiah 40:3 /
   John 1:1 / John 11:35, exactly 2 TRUE, 2 FALSE_MISATTRIBUTION, 1
   AMBIGUOUS, and 1 OFF_TOPIC tutor-spoken sentence (30 total), in a
   labeled format. The agent made zero tool calls (confirmed by the
   returned `tool_uses: 0` in the result metadata) and returned exactly
   the requested format.
4. Measured every one of the 30 sentences against `verify_claim()` with
   the appropriate adapter (OT for Genesis/Deuteronomy/Isaiah, NT for the
   two John verses) via a throwaway script, with **no code changes made
   before or during measurement**.
5. Found something worse than the bead anticipated: not just a recall
   gap, but 3 **dangerous false-CONFIRMEDs** — sentences that falsely
   misattribute a verse's content and get validated as CONFIRMED instead
   of CONTRADICTED/CANNOT_VERIFY. Verified this reproduces both via
   `verify_claim()` directly and via `check_lesson_text()`'s full
   pipeline (sentence-splitting + `extract_domain_claims`), so it is not
   an artifact of calling the low-level function in isolation.
6. Did **not** touch `teach/biblical_ot_source.py` or
   `teach/biblical_nt_source.py` — fixing now would tune against the same
   round that found the gap, spending it, exactly what this bead's own
   text and teach-8xw.33's precedent forbid. Filed the finding as a new
   bug bead, `teach-dds` (P1, parent `teach-8xw`), instead.
7. Committed all 30 sentences verbatim (not paraphrased, not
   summarized) as Python string constants in
   `tests/test_biblical_sources_held_out_round1.py`, one test function per
   sentence asserting its *actually measured* verdict — including the 3
   dangerous ones, which are `pytest.mark.xfail(strict=True,
   raises=AssertionError)` asserting the desired safe behavior (`verdict
   is not Verdict.CONFIRMED`), so they currently XFAIL (matching today's
   actual dangerous CONFIRMED) and would loudly XPASS-fail the moment a
   real fix lands, forcing removal of the marker rather than letting a
   regression slip back in silently. This mirrors the `teach-i35` xfail
   precedent (`18c8fc0`) with the same "XFAIL = safe today, XPASS = bug
   came back" discipline, applied to a not-yet-fixed bug rather than an
   already-fixed one.

## Raw result, exactly as measured, no rounding

- **TRUE** (10 sentences, 2/verse × 5 verses): 5/10 CONFIRMED, 5/10
  CANNOT_VERIFY. A recall gap, not a safety violation.
- **FALSE_MISATTRIBUTION** (10 sentences, 2/verse × 5 verses): 1/10
  CONTRADICTED (caught correctly), 6/10 CANNOT_VERIFY (safe miss), **3/10
  CONFIRMED — dangerous**, filed as `teach-dds`.
- **AMBIGUOUS** (5 sentences, 1/verse × 5 verses): 5/5 CANNOT_VERIFY.
  Correct.
- **OFF_TOPIC** (5 sentences, 1/verse × 5 verses): 5/5 CANNOT_VERIFY.
  Correct.

Root cause of the 3 dangerous CONFIRMEDs, confirmed by reading the actual
regexes (not guessed): each fact's `true_patterns` matches on the verse's
own content appearing in the sentence, unconditionally — with no check for
whether the sentence is making a misattribution claim about that content.
Each fact's `false_patterns` only fires when a *specific* literal keyword
for the wrong destination is present (`"genesis"` for `_GENESIS_CREATION`,
`"john"` for `_JOHN_OPENING_WORD`, a specific other-book name for
`_JOHN_SHORTEST_VERSE`). The agent's misattribution sentences instead
phrased the wrong attribution as "this is actually from/about `<the other
side>`" without that literal keyword (e.g. naming "the Gospel of John"
where the pattern needs literally `"john"`, or misattributing the
narrative *moment* rather than the *book*). This is a structural
asymmetry between what `topic_patterns` needs to recognize a sentence and
what `false_patterns` needs to condemn it as false — not a vocabulary
coverage gap of the kind teach-8xw.33 found and fixed for Lagrange.

## Verification

- `uv run pytest tests/test_biblical_sources_held_out_round1.py -q` — 26
  passed, 4 xfailed (all 4 expected: the 3 dangerous-CONFIRMED direct
  cases plus the `check_lesson_text` pipeline reproduction).
- `uv run pytest -q` (full suite) — **609 passed, 16 skipped, 5 xfailed**
  (4 new + the pre-existing `teach-i35` xfail from `18c8fc0`). No existing
  test changed, weakened, or removed.
- `uv run python3 -m teach.biblical_ot_source`,
  `uv run python3 -m teach.biblical_nt_source`,
  `uv run python3 -m teach.fact_checker` — all three self-checks still
  pass (neither adapter module was touched).

## What was NOT done, and why it's not a gap in this close

- **The 3 dangerous false-CONFIRMEDs were not fixed.** This bead's own
  text is explicit: "do not tune the patterns against this same round --
  if tuning is needed, that is new work, and the round is spent." Filed
  as `teach-dds` (P1, child of `teach-8xw`) instead, with the exact
  reproduction sentences and root-cause analysis carried over so the next
  worker does not have to re-derive them.
- **Recall on TRUE and safe-miss FALSE_MISATTRIBUTION sentences was not
  improved.** Same reasoning — improving recall now would tune against
  this round. `teach-dds` is scoped to the dangerous-CONFIRMED safety
  property specifically; a separate bead could be filed for the pure
  recall gap if wanted, but that is new scope, not this bead's.
- **A second held-out round was not run.** One genuinely fresh round is
  what this bead asked for and what it delivers; running a second round
  now, in the same session, against the same untouched code, would not
  produce new information.

## Bead disposition

Closing as done: a genuinely fresh, independently-authored (zero tool
calls, confirmed) held-out round was measured against both adapters via
both `verify_claim` and `check_lesson_text`, the raw counts are reported
honestly including a real safety-property violation the bead's own
description didn't anticipate, all 30 sentences are preserved as runnable
data (not just prose) per the `teach-8xw.40` lesson, the dangerous finding
is filed as new work (`teach-dds`) rather than silently fixed or silently
dropped, and the full test suite passes.

## Addendum (resumed session, 2026-09-15)

The bead was still marked `in_progress` and this handoff file plus
`tests/test_biblical_sources_held_out_round1.py` were sitting uncommitted
in the working tree — the session above appears to have ended after
writing this handoff but before closing the bead. Per this repo's
"do not assume a prior worker's partial work is correct" rule, I did not
take the numbers above on faith. Independently re-ran:

- `uv run pytest tests/test_biblical_sources_held_out_round1.py -q` →
  26 passed, 4 xfailed — matches this file's claims exactly.
- `uv run pytest -q` (full suite) → 609 passed, 16 skipped, 5 xfailed —
  matches this file's claims exactly.
- `git diff --stat` / `git status` → `teach/biblical_ot_source.py` and
  `teach/biblical_nt_source.py` are absent from both the modified and
  untracked lists — confirmed neither was tuned against this round.
- `bd show teach-dds` → exists, P1, `IN_PROGRESS`, and its description
  matches the three dangerous sentences and root-cause analysis in this
  file verbatim.

All of this bead's acceptance criteria hold under independent
verification. Closing now. `tests/test_biblical_sources_held_out_round1.py`
and this handoff remain uncommitted, matching this repo's conservative
git policy (commit/push only when explicitly asked) — left for the user
or a future session to commit.
