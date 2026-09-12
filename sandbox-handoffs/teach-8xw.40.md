# teach-8xw.40 handoff

## What this bead was

teach-8xw.33's handoff (`sandbox-handoffs/teach-8xw.33.md`) claimed "the 12
[round-3 held-out] sentences are reproduced in the test file docstrings and
the `_LAGRANGE_ORDER_DIVIDES` comment block." They were not. Only 3 of the
12 were ever committed as runnable data — the three
`test_lagrange_round_3_*` cases in `tests/test_fact_checker.py`. The other
nine survived only as prose fragments quoted in the comment block ("has to
split evenly into", "slot into", "swallows ... evenly", "absorbs ...
cleanly"), which are not runnable sentences, and the worker session that
held the full 12 no longer exists. This bead's ask: either recover the nine
and preserve all 12 as data (option a), or say plainly, where the claim is
made, that only 3/12 are preserved and the 1/12 figure is not reproducible
(option b). Explicitly out of scope: generating a fresh round of 12 and
presenting it as a recovery of this one.

## What I did

1. Confirmed the gap is real by reading `tests/test_fact_checker.py` (only
   3 `test_lagrange_round_3_*` cases exist) and the `_LAGRANGE_ORDER_DIVIDES`
   comment block in `teach/math_facts.py` (aggregate prose only, no full
   sentence list for the other 9).
2. Searched for any surviving record of the missing nine before concluding
   they were unrecoverable, per option (a):
   - `find /home/node/.claude/projects -type d` — only one session directory
     exists on this machine, `083e80d2-...` (the current session). No prior
     session transcripts survive anywhere.
   - `git log --oneline --all` and `git show ce3300f -- teach/math_facts.py
     tests/test_fact_checker.py` — `ce3300f` is the commit that introduced
     both the round-3 comment block and the three tests, and its own commit
     message already states the same finding this bead was filed over
     ("Filed teach-8xw.40: ... Three are [preserved]. The other nine survive
     as prose fragments"). No earlier or later commit contains more than
     those three sentences.
   - A grep for round-3 fragment text ("swallows ... evenly" etc.) against
     the current session transcript did match — but only because the bead's
     own description (fetched via `bd show`) quotes those same fragments.
     Not a recovered transcript; a false positive I ruled out before relying
     on it.
   - Conclusion: the nine are genuinely gone. No repo history, no session
     transcript, no other file anywhere in the working tree contains them.
     Option (a) is not available.
3. Did option (b): corrected the claim at the place it was made.
   - `teach/math_facts.py`: appended a new paragraph to the comment block
     above `_SIZE_SYNONYMS` (right after the existing "Deliberately NOT
     chased further here..." paragraph) stating that only 3/12 were
     committed, that the 1/12 figure is accurate as a historical report but
     not reproducible from this repo, and that a future change can only
     honestly claim to hold or improve on the 3 committed sentences (or
     measure a new, differently-numbered round of its own).
   - `sandbox-handoffs/teach-8xw.33.md`: left the original text in place
     (this repo's handoffs are a record, not something to silently rewrite)
     but (a) inline-flagged the false claim in step 2 with a pointer to the
     correction, and (b) appended a dated "Correction (teach-8xw.40)" section
     at the end spelling out exactly what was false, what's actually true,
     and that the substantive finding (safe direction, real recall gap,
     correctly declined to chase further) is unaffected — only its
     reproducibility is.
4. Did NOT touch `_LAGRANGE_ORDER_DIVIDES`'s patterns, `_SIZE_SYNONYMS`, or
   any other widening logic. This bead is bookkeeping only, per its own
   explicit instruction ("Note for whoever takes this: the fix is
   bookkeeping, not pattern work. Do not widen `_LAGRANGE_ORDER_DIVIDES`
   here.").

## Verification

- `uv run pytest -q` — **316 passed**, same as before this bead's edits
  (comment/doc-only change, no code path touched — no test count change, no
  test content change).
- `uv run python3 -m teach.math_facts` — self-check passes.
- `uv run python3 -m teach.fact_checker` — self-check passes.

## Bead disposition

Closing as done via option (b): the false preservation claim is corrected
both where it originated (`sandbox-handoffs/teach-8xw.33.md`) and where it
was repeated (`teach/math_facts.py`'s comment block), the honest smaller
claim (3/12 reproducible, 1/12 is a historical report only) now stands in
place of the false larger one, and nothing about `_LAGRANGE_ORDER_DIVIDES`'s
behavior or tests changed.
