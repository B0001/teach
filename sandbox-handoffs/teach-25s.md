# teach-25s: va_writing_sol_graph concept_recovery generalization (held-out round 1)

## What the bead asked for

teach-8xw.42's floor test (`tests/test_concept_recovery_writing_domain.py`)
proved `concept_recovery.py` mechanically runs against the real VA Writing
SOL graph, but every fixture in it was self-authored by the session that
wrote the assertions -- per sandbox-prompt.md's "you cannot hold out examples
from yourself", that is not a generalization measurement. teach-25s asked for
lesson text authored by an agent with no repository access (teach-8xw.33's
precedent), kept in its own file, with the recovered fraction stated plainly.

## What I found on claiming this bead

The deliverable already existed and was already committed:
`tests/test_concept_recovery_writing_domain_generalization.py`, added in
commit `b5e1f4d` (2026-09-11, "Writing, foreign-language and biblical domains
..."). Its docstring documents 8 lesson dialogues, each independently
produced by a separate no-repo-access `Agent` call, transcripts reproduced
verbatim, method matching teach-8xw.33's precedent. The bead itself was never
closed and no handoff was ever written for it -- the commit message that
introduced the file says so explicitly: "Also still claimed, work included
here, no handoffs yet: ... teach-25s ... Neither should be read as
finished."

In the time since that commit, a later session (teach-l7u, closed) found and
fixed two real bugs using exactly this round's fixtures: the raw+semantic
tiers were giving *confident wrong answers* on 3 of the 8 held-out cases
(GRADE10_UNSIGNPOSTED, READING_THEME_ABSTAIN, REVISING_AMBIGUOUS) instead of
abstaining. teach-l7u's close rewrote this file's test *assertions* to match
the post-fix behavior (all three now correctly abstain) but did not update
the module docstring's "HONEST RESULT" narrative, which still described the
old wrong-answer behavior verbatim. That left the file self-contradictory:
prose says "WRONG, not abstained" for a test that asserts `taught_node_id is
None` two pages below.

## What I did

1. Verified current behavior directly: ran
   `pytest tests/test_concept_recovery_writing_domain_generalization.py -v`
   -- all 8 pass, matching what the test bodies (not the stale prose) assert.
2. Fixed the docstring in place, per teach-8xw.40's precedent (correct in
   place, leave the original text standing, append a dated correction rather
   than silently rewriting history). Added an "UPDATE (teach-25s, after
   teach-l7u's fix)" section stating the current honest result: 2/8 full
   correct recoveries, 0/8 confident wrong answers, 6/8 safe abstentions (2
   genuinely out-of-domain, 1 deliberately ungraded/no-correct-answer, 3
   safe misses on real targets that tied within margin). Also stated plainly
   that re-running this exact text against the now-fixed module is
   diagnostic of the fix, not a fresh generalization measurement (this
   round's own bugs became the fix's tuning data) -- the actual
   post-fix generalization evidence is rounds 2 onward
   (`test_concept_recovery_writing_domain_generalization_round2.py` /
   teach-8xw.53, and rounds 3-5 under teach-cpg / teach-i35), which this
   bead does not need to duplicate.
3. Confirmed the floor test (`test_concept_recovery_writing_domain.py`, 5
   tests) and this generalization file (8 tests) remain in separate files,
   per teach-8xw.42's own closing note.
4. Ran the full suite: `uv run pytest -q` -> 703 passed, 16 skipped, 1
   xfailed. No regressions from the docstring edit (it only touches a
   module-level string, no assertions changed).

## Evidence

- `uv run pytest tests/test_concept_recovery_writing_domain_generalization.py -v`
  -> 8 passed.
- `uv run pytest tests/test_concept_recovery_writing_domain.py tests/test_concept_recovery_writing_domain_generalization.py -q`
  -> 13 passed (floor + generalization, still separate files).
- `uv run pytest -q` (full suite) -> 703 passed, 16 skipped, 1 xfailed.

## Scope note

I did not touch the round 2-5 files (teach-8xw.53 / teach-cpg / teach-i35 --
those beads are closed already and are not this bead's concern) or the
unrelated in-flight changes I found in the working tree at claim time
(`teach/biblical_nt_source.py`, `teach/biblical_ot_source.py`,
`teach/fact_checker.py`, `teach/judson_algebra_graph.py`, various held-out
round files for the Judson graph and biblical sources, etc. -- these belong
to other in-progress beads, teach-8xw.58 and teach-jkx, per `bd list
--status in_progress` at session start). I left those files exactly as I
found them.

## Why closing rather than leaving open

The bead's acceptance bar -- a held-out round, authored by no-repo-access
agents, kept separate from the floor test, with the recovered fraction
stated plainly -- was already met by the existing file; the only real defect
was that its narrative had gone stale relative to a later fix and needed
correcting, which I did. There is no further work this bead's own text
asks for (a second, post-fix generalization round is a distinct concern
already covered by later beads' own rounds, not a gap in this one).
