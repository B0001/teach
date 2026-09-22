# teach-8xw.53 handoff

## What this bead was

teach-l7u fixed two confident-wrong-answer failures in
`teach/concept_recovery.py`'s `_resolve_candidates`, validated only against
the three reproduction cases that motivated the fix (its own "floor, not a
measurement"). Per sandbox-prompt.md ("a generalization set you generated in
the same session that wrote the rule is not held out, whatever it is
labelled"), teach-l7u could not produce its own validation and filed this
bead for a fresh session — one that did not write the fix — to measure it
against genuinely held-out writing-domain lesson text, using the
teach-8xw.33 method (agents with no repository access, not shown the code,
thresholds, or bead history), report three counts separately (correct
recoveries / safe abstentions / confident wrong answers), and preserve the
set as committed runnable data rather than a prose summary.

Explicitly forbidden: closing this against the three original teach-l7u
texts (guaranteed to pass — they're the tuning data), and tuning
`_MIN_WINNING_COVERAGE` or any other threshold in response to this round's
results.

I am a fresh session with no part in writing teach-l7u's fix, so I qualify
to run this measurement.

## What I did

1. Read `teach/concept_recovery.py` in full (777 lines) and
   `teach/va_writing_sol_graph.py` in full, to understand
   `recover_from_lesson_text`'s public contract and the real VA Writing SOL
   K-12 graph's 13 nodes — without letting that reading influence the lesson
   texts I asked for (all text content given to the generating agents was
   independently paraphrased from the raw source JSON
   `teach/data/va_writing_sol_k12.json`, not from anything in
   `concept_recovery.py`).
2. Confirmed the existing suite passes before touching anything:
   `uv run pytest tests/test_concept_recovery.py
   tests/test_concept_recovery_writing_domain.py
   tests/test_concept_recovery_writing_domain_generalization.py -q` → 37
   passed.
3. Read `tests/test_concept_recovery_writing_domain_generalization.py` (the
   existing teach-25s held-out round) to see which grades and scenarios it
   already covered (K, 4, 7, 10, 12), so this round could deliberately avoid
   re-measuring the same ground.
4. Launched 8 independent `Agent` tool calls in parallel, each told
   explicitly not to use any tools and not given any information about this
   repository, `concept_recovery.py`, its thresholds, or any bead history —
   only plain-English paraphrased VA Writing SOL content and a request to
   render it as natural tutor/student dialogue. Grades chosen (1, 2, 6, 9,
   11) deliberately do not overlap teach-25s's (K, 4, 7, 10, 12) or
   teach-l7u's three originals. Also generated: one off-domain math lesson,
   one off-domain reading-inference lesson (both on different topics than
   teach-25s's water-cycle/theme-analysis off-domain cases), and one
   deliberately grade-neutral generic writing-process lesson with no
   escalation language.
5. Measured all 8 texts against the real, unmodified
   `teach.va_writing_sol_graph` via `recover_from_lesson_text` — the public
   entry point only, no internals inspected to choose or adjust the texts.
6. Found one genuine confident wrong answer (GRADE6_SIGNPOSTED: recovers
   taught=7.W instead of the intended 6.W, with a consistently-wrong
   prerequisite claim of assumed=(6.W,) instead of (5.W,) — 6.W is a real
   direct prerequisite of the wrongly-recovered 7.W, so the error is
   internally consistent, not just topically off). Wrote a follow-up
   diagnostic script computing `_coverage_fraction` and matched-word counts
   for the top candidates to root-cause it exactly: 7.W scores 18 (36.0%
   coverage of its own 50-word vocabulary) vs. 6.W's 16 (50.0% coverage of
   its own 32-word vocabulary) — 6.W is proportionally the better match but
   loses on raw count because it has a smaller vocabulary. Margin is exactly
   2 (`_MIN_MARGIN`), which is NOT less than `_MIN_MARGIN`, so
   `_resolve_candidates` takes the single-winner branch (teach-l7u's fix)
   and only checks 7.W's own coverage against the fixed 20% floor — it
   clears that floor easily, so the gate never fires, and 6.W's (higher)
   coverage is never consulted at all. This is a distinct structural gap
   from what teach-l7u fixed, not a regression of it: the coverage-tiebreak
   branch that DOES compare rival candidates against each other only runs
   when the winning margin is small enough to put multiple candidates in a
   "close" group together — here it wasn't, because 7.W's margin over its
   single largest rival is exactly `_MIN_MARGIN`, not under it.
7. Committed the full 8-text set, verbatim, plus per-case docstrings and
   assertions matching the actually-measured outcome, in
   `tests/test_concept_recovery_writing_domain_generalization_round2.py` —
   including asserting the GRADE6_SIGNPOSTED confident-wrong-answer as
   *current* behavior, explicitly flagged as a known bug with a pointer to
   its own bead, not silently accepted as correct.
8. Filed **teach-cpg** documenting the coverage-tiebreak gap in full
   technical detail (root cause, exact numbers, why it's distinct from
   teach-l7u's fix, explicit instruction not to validate any future fix
   against this same round). Linked `teach-cpg` `discovered-from`
   `teach-8xw.53`. Did NOT touch `_resolve_candidates`, `_MIN_MARGIN`,
   `_MIN_WINNING_COVERAGE`, or any other threshold — per this bead's
   explicit instruction not to tune anything in response to this
   measurement.
9. Updated the `teach-8xw-10-concept-recovery-design` bd memory with the
   full lineage (teach-25s → teach-l7u → teach-8xw.53 → teach-cpg) so a
   future worker touching `_resolve_candidates` sees the coverage-tiebreak
   gap without having to re-discover it.
10. Ran the full suite: `uv run pytest -q` → **431 passed** (423 pre-existing
    + 8 new). Ran both modules' standalone self-checks
    (`uv run python -m teach.concept_recovery`,
    `uv run python -m teach.va_writing_sol_graph`) — both pass. (Note:
    `uv run python teach/concept_recovery.py` as a bare script fails with
    `ModuleNotFoundError: No module named 'teach'` because the script's own
    directory, not the repo root, lands on `sys.path` that way — this is a
    property of how the package is laid out, not something this session
    changed, and `-m` invocation is the correct/working form.)

## Honest result

8 held-out texts, measured once, thresholds untouched afterward:

| correct recoveries | safe abstentions | CONFIDENT WRONG ANSWERS |
|---|---|---|
| 0 / 8 | 7 / 8 | **1 / 8** |

Before teach-l7u's fix (teach-25s's original round): 2 of 8 confident wrong
answers. This round, on a fresh set the fix was never tuned against: 1 of 8.
The fix reduced the failure mode; it did not close it. This is reported as a
measurement of these 8 texts, not extrapolated into "the fix works" or "the
fix is broken."

Two of the 8 safe abstentions are themselves worth flagging honestly rather
than filed away as pure successes:
- GRADE1_STANDALONE actually had the correct top scorer (1.W) but the module
  abstained anyway because that win's own coverage (16%) falls below
  `_MIN_WINNING_COVERAGE` (20%) — a false negative, not a false positive.
  Costs recall, not correctness; consistent with this module's documented
  bias toward declining over guessing.
- GRADE9_UNSIGNPOSTED and GRADE11_STANDALONE both abstained correctly, but
  in both cases the raw top-scoring candidates were not even the intended
  grade — the module got lucky into a safe outcome via ambiguity rather than
  "almost got it right." Reported as-is; not spun as stronger evidence than
  it is.

Full texts, per-case reasoning, and exact assertions are in
`tests/test_concept_recovery_writing_domain_generalization_round2.py`
(module docstring has the complete accounting, including the root-cause
explanation for GRADE6_SIGNPOSTED).

## What was NOT done (on purpose)

- Did not touch `_resolve_candidates`, `_MIN_WINNING_COVERAGE`,
  `_MIN_MARGIN`, or any other threshold in `concept_recovery.py`. The
  GRADE6_SIGNPOSTED finding is reported, not fixed, per this bead's explicit
  instruction — fixing it here would make this round's set into tuning data
  too, the exact mistake this lineage (teach-8xw.33/40, teach-9k5, teach-l7u)
  keeps disclosing and correcting.
- Did not re-run or rely on the three original teach-l7u reproduction texts
  as part of this measurement (they still pass, per the pre-existing
  `tests/test_concept_recovery_writing_domain_generalization.py`, but that
  is not this bead's evidence).
- Did not touch any of the unrelated concurrent working-tree changes visible
  in `git status` (a Dummit & Foote → Judson's Abstract Algebra rename
  across several files, `.beads/interactions.jsonl`, other new/deleted
  files) — none of that is this bead's scope, and none of it was made by
  this session.
- Did not commit or push anything, per the repo's conservative git policy.

## Verification

- `uv run pytest -q` — **431 passed**.
- `uv run python -m teach.concept_recovery` — self-check passes.
- `uv run python -m teach.va_writing_sol_graph` — self-check passes.
- `git status` shows exactly one new file from this session:
  `tests/test_concept_recovery_writing_domain_generalization_round2.py`
  (plus this handoff and the bd database write for `teach-cpg` and the
  updated memory, which are not git-tracked working-tree edits).

## Bead disposition

Closing as done: the bead's own "WHAT WOULD CLOSE THIS" section asks for a
fresh held-out measurement with an honest three-count report and a
preserved, runnable set — not a fix. That measurement is complete, the set
is committed as runnable test data with per-case expected outcomes, the
three counts are reported honestly (including the one that matters: 1
confident wrong answer, down from 2 but not zero), and the newly-found
structural gap is filed as its own bead (`teach-cpg`) rather than patched
here.
