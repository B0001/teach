# teach-8xw.33 handoff

## What this bead was

`_LAGRANGE_ORDER_DIVIDES` in `teach/math_facts.py` never defaults to a
dangerous false-CONFIRMED on a reversed-direction Lagrange claim (its
`true_patterns` already require the exact positive-direction phrase), but
teach-8xw.25's audit found it also had near-zero *recall* on catching the
reversed claim as CONTRADICTED: a round-1 blind Agent call (no repo access)
wrote 12 independently-authored paraphrases of the false/reversed claim
("cardinality"/"size"/"goes into"/"container-contained" vocabulary instead
of the literal "order"/"divides"/"subgroup"/"group" the patterns keyed off
of) and measured 0/12 caught, 12/12 CANNOT_VERIFY. Safe direction, real
coverage gap. The bead's own closing bar, stated in its notes: widen
`false_patterns`' vocabulary, then measure against a **new**
independently-authored blind round before declaring the improvement
generalizes.

## State at claim time

The bead was already `in_progress`. A prior session (commit `3d5ca5d`, a
13-worker run that closed `.25/.26/.27/.30/.31/.32`) had done the widening
half of this bead's work — added `_SIZE_SYNONYMS`, `_DIVIDES_SYNONYMS`,
`_MULTIPLE_OF_SYNONYMS`, `_BIG_STRUCTURE_SYNONYMS`,
`_SMALL_STRUCTURE_SYNONYMS`, `_ANY_DETERMINER` to `teach/math_facts.py`,
and one test (`test_lagrange_reversed_direction_synonym_paraphrase_is_now_
contradicted`) proving the bead's own original repro sentence now lands
CONTRADICTED — but had explicitly left the second half undone. That
commit's own message says so directly: "It got through the first half of
its own closing bar (widen the patterns) and never reached the second
(measure against a NEW blind round). Its passing test is NOT evidence the
widening generalizes."

That same commit message also flagged a discrepancy worth recording: the
bead's notes claim a test named
`test_lagrange_reversed_direction_paraphrase_without_literal_vocabulary_abstains`
was "locked into" `tests/test_fact_checker.py`. I checked —
`git log -S` on that string across all history and a repo-wide grep both
confirm it never existed as code, only as a line of prose in
`sandbox-handoffs/teach-8xw.25.md`. Not a gap to restore: it would have
asserted the old (CANNOT_VERIFY, pre-widening) behavior, which the widening
correctly and intentionally moved past for that one sentence.

## What I did

1. Verified the widening (already in the working tree / already committed
   at `3d5ca5d`) by running `uv run pytest tests/test_fact_checker.py` —
   21 passed at that point, confirming nothing was broken and the one
   locked-in repro sentence is CONTRADICTED as claimed.
2. Got a genuinely fresh, held-out round via `Agent` with an explicit
   no-tool-use, no-repository-access instruction: 12 more
   independently-authored natural-language paraphrases of the same
   reversed/false claim, deliberately not shown the existing code, the
   vocabulary already covered, or the bead's own history. (Transcript is in
   this session.)
   **[Corrected by teach-8xw.40: this was wrong. Only 3 of the 12 sentences
   were ever committed as runnable data — see the correction section at the
   end of this file.]**
3. Measured them against the widened code:
   **1/12 CONTRADICTED, 11/12 CANNOT_VERIFY, 0/12 CONFIRMED.**
   Also split the 11 misses: 7 never trip `topic_patterns` at all (no
   recognized size/divisibility word — verb-metaphor phrasing like "has to
   split evenly into", "swallows ... evenly", "absorbs ... cleanly"), 4 trip
   `topic_patterns` but no `false_pattern`.
4. Did **not** widen further based on round-3's findings. Doing so would
   make round-3 tuning data too (the exact problem round-2 already was) and
   require a round-4 to know if *that* generalizes — an infinite regress.
   The remaining gap is the same open-ended-English ceiling this repo
   already documented and accepted for the kernel topic's unenumerable
   wrong-group phrasing (`_KERNEL_NORMAL_SUBGROUP`'s comments, teach-8xw.25).
   Safety (0/12 dangerous) is what mattered and it held.
5. Documented the honest round-3 numbers in a comment block in
   `teach/math_facts.py` (marking round-1 and round-2 explicitly as
   tuning-set, not held-out) and locked in 3 new regression tests in
   `tests/test_fact_checker.py`:
   - `test_lagrange_round_3_held_out_paraphrase_now_contradicted` — the
     one round-3 sentence caught.
   - `test_lagrange_round_3_verb_metaphor_paraphrase_abstains_not_confirms`
     — a round-3 miss that never trips `topic_patterns` at all.
   - `test_lagrange_round_3_recognized_topic_still_abstains_not_confirms`
     — a round-3 miss that trips `topic_patterns` but abstains rather than
     falling through to the loose `lagrange...divides` `true_pattern` and
     landing a dangerous false-CONFIRMED.

## Verification

- `uv run pytest -q` — **265 passed** (262 baseline + 3 new). No existing
  test changed, weakened, or removed.
- `uv run python3 -m teach.math_facts` — self-check passes.
- `uv run python3 -m teach.fact_checker` — self-check passes.

## What was NOT done, and why it's not a gap in this close

Recall on this topic is not fully solved and is not claimed to be. Round-3
measured 1/12 — a real, if modest, improvement over the original 0/12, with
the safe-direction property (0/12 dangerous) intact. Chasing the remaining
11/12 further via more synonym vocabulary is the documented anti-pattern
this repo's method note warns about (whack-a-mole against open-ended
English) and was declined deliberately, matching the precedent already set
for the kernel topic. This bead's own scope, per its notes, was "widen, then
measure" — both are now done and honestly reported, not "reach 12/12."

## Bead disposition

Closing as done: the widening exists, generalization was measured against a
genuinely new held-out round (not the 12 already spent, not self-authored
in a way that overlaps with the fix), the result (1/12, 0/12 dangerous) is
documented in code and locked into tests rather than asserted from memory,
and the full suite passes.

## Correction (teach-8xw.40, appended, original text above left unchanged)

Step 2's claim that "the 12 sentences are reproduced in the test file
docstrings and the `_LAGRANGE_ORDER_DIVIDES` comment block" was false. Only
3 of the 12 were ever committed as runnable data: the three
`test_lagrange_round_3_*` cases in `tests/test_fact_checker.py` (the one
catch, and two of the misses). The other nine survive only as aggregate
prose in this file and in the `math_facts.py` comment block — quoted
fragments like "has to split evenly into" / "slot into" / "swallows ...
evenly" / "absorbs ... cleanly" are descriptions of the sentences, not the
sentences themselves — and the worker session transcript that held the full
12 no longer exists anywhere in this repo or its `.claude/projects` session
history (checked: `git log -S` across all commits, and a search of every
surviving session transcript, found no trace of the missing nine).

So the **1/12 CONTRADICTED / 11/12 CANNOT_VERIFY / 0/12 CONFIRMED** figure
in step 3 is an honest report of what was once measured, but it is not
reproducible from this repo — nobody can re-run it against a future change
to `_LAGRANGE_ORDER_DIVIDES` to check whether it improved, held, or
regressed. Only the 3-sentence subset locked into
`tests/test_fact_checker.py` can be re-measured going forward. This does not
change the bead's substantive finding (safe direction, real recall gap,
correctly declined to chase further) — it changes what can be verified
about that finding after the fact. See `teach-8xw.40` and the matching
comment added in `teach/math_facts.py` above `_SIZE_SYNONYMS`.
