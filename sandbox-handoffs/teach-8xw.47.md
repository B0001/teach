# teach-8xw.47 handoff

## What this bead was

teach-8xw.40 found that teach-8xw.33's closing claim -- a held-out round-3
measurement of 1/12 CONTRADICTED, 11/12 CANNOT_VERIFY, 0/12 CONFIRMED against
12 independently-authored reversed-direction Lagrange paraphrases -- was only
3/12 reproducible. The other 9 sentences existed only as prose fragments in
`sandbox-handoffs/teach-8xw.33.md` and a comment in `teach/math_facts.py`;
the worker session that held the full 12 no longer exists anywhere in the
repo or surviving session history. teach-8xw.40 corrected the false
preservation claim (documented 3/12, not 12/12) but explicitly declined to
generate a replacement round in the same bead, filing that as this bead
instead.

This bead's job: get a genuinely fresh held-out round using the same method
as round-3, measure it against the current (unwidened) `_LAGRANGE_ORDER_DIVIDES`
patterns, and this time commit **all 12** sentences as runnable test data
from the start -- not just aggregate prose. Explicitly out of scope: widening
the patterns based on what this round finds (that would make this round
tuning data too, the same regress round-3's own handoff already declined).

## What I did

1. Read `bd show teach-8xw.40` and `sandbox-handoffs/teach-8xw.33.md` in full
   to confirm the gap and recover the exact method round-3 used.
2. Read `teach/math_facts.py`'s `_LAGRANGE_ORDER_DIVIDES` fact and comment
   block, and `tests/test_fact_checker.py`'s existing Lagrange tests, to
   understand the current (post-teach-8xw.34) pattern state I was measuring
   against.
3. Spawned an `Agent` (subagent_type: general-purpose) with an explicit
   instruction to use **zero tools** -- no file reads, no bash, no grep, no
   web search -- and to answer purely from its own general knowledge of
   group theory and English paraphrase, with no repository access at all.
   Confirmed after the fact that the call recorded `tool_uses: 0`. Asked for
   12 independently-invented English sentences stating the reversed/false
   direction of Lagrange's theorem (group's order divides subgroup's order,
   backwards), steered toward aggressive vocabulary and structural variety,
   with an explicit requirement that no two of the 12 share a template and
   none are hedged into ambiguity. The prompt did not show the agent any
   existing code, vocabulary, or bead history (same method as round-3, per
   teach-8xw.33's own description of how it obtained its round).
4. Measured all 12 against the current `MATH_SOURCE` via `verify_claim`
   directly (a short throwaway script, not committed):
   **2/12 CONTRADICTED, 10/12 CANNOT_VERIFY, 0/12 CONFIRMED.** No sentence
   landed the dangerous false-CONFIRMED verdict -- the safe-direction
   property held again.
5. Did **not** widen `_LAGRANGE_ORDER_DIVIDES` in response to this
   measurement. Per this bead's explicit instruction, that is a different
   (future) bead's job, to be measured against its own fresh round.
6. Committed all 12 sentences verbatim, each paired with its measured
   verdict, as a module-level tuple `LAGRANGE_ROUND_4_HELD_OUT` in
   `tests/test_fact_checker.py`, exercised by a single
   `@pytest.mark.parametrize`d test (`test_lagrange_round_4_held_out_paraphrase`)
   -- all 12, not a 3-sentence sample, so the full figure is reproducible
   with one command (`uv run pytest -k round_4`) against any future change
   to the patterns.
7. Added a comment block in `teach/math_facts.py` immediately after the
   existing round-3/teach-8xw.40 correction comment, recording round-4's
   method, result, and the full-preservation fact, and naming "round 5" as
   the bead that would need its own fresh round if it wants to widen and
   re-measure.

## Verification

- `uv run pytest -q` -- **395 passed** (383 baseline + 12 new
  `test_lagrange_round_4_held_out_paraphrase` cases). No existing test
  changed, weakened, or removed.
- `uv run python3 -m teach.math_facts` -- self-check passes.
- `uv run python3 -m teach.fact_checker` -- self-check passes.
- Manually re-ran `verify_claim` over the 12 committed sentences from a
  fresh Python process against the values in `LAGRANGE_ROUND_4_HELD_OUT`
  to confirm the tuple's expected verdicts match what the code actually
  produces (not hand-typed guesses) before committing them.

## What was NOT done, and why it's not a gap in this close

- The patterns were not widened. This bead is bookkeeping/measurement, and
  its own text says so explicitly ("do not widen the patterns in the same
  pass"). The 10/12 miss rate is a real, disclosed recall gap, of the same
  open-ended-English-ceiling species already documented for round 3 and for
  the kernel topic's unenumerable wrong-group phrasing -- not something this
  bead was asked to fix.
- I did not attempt to recover round-3's missing 9 sentences (teach-8xw.40
  already exhausted that search: no later commit, no earlier commit, no
  surviving transcript). This bead measures a new round rather than
  resurrecting the old one, which is what teach-8xw.40 asked for.
- Round-4's 2/12 is not compared against round-3's 1/12 as if it were an
  improvement or regression -- they are different, non-comparable samples of
  the same open-ended space (this is the same reasoning teach-8xw.33 and
  teach-8xw.40 both apply to round-1/round-2/round-3 relative to each other).

## Bead disposition

Closing as done: a genuinely fresh, independently-authored held-out round was
obtained via a verified-zero-tool-access Agent call, measured against the
current unwidened patterns (2/12 CONTRADICTED, 10/12 CANNOT_VERIFY, 0/12
CONFIRMED -- safe direction held), and all 12 sentences are committed as
runnable parametrized test data in `tests/test_fact_checker.py` from the
start, closing the exact reproducibility gap teach-8xw.40 identified. Full
suite passes (395).
