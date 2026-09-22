# teach-9ba handoff

## Status: closing, diagnostic question answered, no code fix (out of scope)

This bead was diagnostic, not a fix request. Its own text poses the
question directly: is the coverage-veto abstention on genuine
rings/subgroups lessons a rings-specific vocabulary-curation problem, or a
general property of the 85%-coverage-floor design? The bead explicitly
flags that retuning `_MIN_COVERAGE_FRACTION` / `_DECISIVE_MARGIN_*` would
need "much more careful, whack-a-mole-aware calibration" given this
lineage's tuning history (teach-9wx/teach-hpa/teach-l7u/teach-ceg) and asks
only that the next worker "determine whether" before anyone attempts a fix.

I picked this bead up already `in_progress` with substantial notes left by
a prior session (visible in `bd show teach-9ba`). I did not repeat that
work; I verified it instead, since the standing rule here is that a
previous worker's partial work is a candidate until checked, not a given.

## What I verified (this session)

1. **Re-ran the new evidence file** the prior session added,
   `tests/test_concept_recovery_judson_full_graph_generalization_round7.py`
   (3 tests) against the current, unmodified tree. All 3 pass, and the
   asserted raw scores/coverage fractions in the test bodies
   (`CYCLIC_SUBGROUPS_BLIND` score 9/11 coverage; `GROUP_AXIOMS_BLIND` raw
   tier 13/52 vs 6/11, gap ≥ 0.18; semantic tier 18 vs 6) match what the
   code actually returns — not just what the docstring narrates.
2. **Ran the full suite**: 703 passed, 16 skipped, 1 xfailed. (The prior
   session's notes reported 700/16/1 as their own before/after delta;
   the extra 3 passing here are accounted for by other beads' untracked
   test files already present in this shared, uncommitted working tree at
   session start — e.g. round8 fixtures for teach-jkx, round2/round3 for
   the biblical sources. Nothing regressed.)
3. **Read the full diff of `teach/concept_recovery.py`** against HEAD to
   confirm the prior session's claim of "no code change to
   concept_recovery.py's thresholds/logic in this session" — true. The
   diff present in the working tree is the accumulated, uncommitted history
   of several *other* beads (teach-443, teach-57f, teach-911, teach-scx,
   teach-jkx investigation notes) already narrated inline as code comments;
   nothing in it originates from this session or is attributed to teach-9ba.

## Conclusion (confirmed, not just inherited)

CONFIRMED as a general property of `judson:16.1-rings`' vocabulary breadth,
not a rings/subgroups-specific paraphrase gap. Evidence:

- `CYCLIC_SUBGROUPS_BLIND` (fresh, blind, tool-less fixture on a different,
  well-covered node) recovers correctly — proves this class of genuine
  on-topic blind lesson does not *always* abstain, i.e. rules out "the
  mechanism is broken for all blind fixtures."
- `GROUP_AXIOMS_BLIND` (fresh, blind, tool-less fixture that never mentions
  rings) hits the identical decisive-margin coverage-gap veto that the
  bead's original subgroups/rings fixtures hit. `judson:16.1-rings`' curated
  vocabulary (binary, operation, satisfying, together, abelian, addition,
  conditions, notice, first, last, …) is broad/generic enough to
  out-raw-score group-theory-adjacent topics generally, independent of
  paraphrase choice — so the bead's "add paraphrase-common synonyms to
  rings' vocabulary" suggested fix direction is rejected: it would widen an
  already-too-broad vocabulary and likely make the veto trigger *more*
  often, not less.

So: the coverage-gap veto (teach-9wx/teach-hpa) is doing its job here —
this is the abstain-when-uncertain behavior working as designed on a
lesson that genuinely can't be told apart from rings by raw overlap alone.
Retuning thresholds is explicitly out of this bead's scope (its own text
says so), and would need the whack-a-mole-aware process the bead names,
not a one-session tweak.

## Byproduct found, filed forward, NOT fixed here

While exercising `GROUP_AXIOMS_BLIND` through the *full*
`recover_from_lesson_text()` pipeline (not just the raw tier in isolation),
the prior session found a second, more severe bug: the raw tier's safe
abstention is overridden by the semantic (WordNet) fallback tier, whose
`credible_rivals` filter compares semantically-inflated scores rather than
literal coverage. `judson:3.2-definitions-and-examples` (55% literal
coverage, genuinely the best) gets excluded from the rival set because its
*semantic* score (6) doesn't clear 0.35× rings' *semantically-inflated*
score (18), even though nothing about its literal coverage changed. Net
effect: a **confident wrong answer** (`judson:16.1-rings`,
`abstain_reason=None`), not a safe abstention. This is a different failure
mode (wrong answer vs. over-caution) with a distinct root cause from what
teach-9ba describes, so it was filed as **teach-jkx** (P2, currently
in_progress with two rejected fix attempts already documented in
`concept_recovery.py`'s own comments above `_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO`)
rather than fixed under this bead. I did not touch teach-jkx this session —
it is out of scope here per this lineage's standing rule against fixing in
the same session that found the bug.

## Evidence left behind

- `tests/test_concept_recovery_judson_full_graph_generalization_round7.py`
  — 3 tests, all passing, asserting the exact scores/coverage fractions
  above against the current, unmodified `load_judson_full_graph()`. This is
  the runnable check for this bead's finding; it does not need a fix to
  keep passing because the bead's ask was diagnostic, not corrective.
- No changes to `teach/concept_recovery.py`, `teach/judson_algebra_graph.py`,
  or any threshold constant were made under this bead, this session or the
  prior one.

## Why closing rather than leaving open

The bead's own text frames its ask as a diagnostic question ("determine
whether... rings-specific... or a general property") with an explicit
scope boundary against retuning thresholds. That question now has a
directly-measured, fresh-fixture answer (general property), backed by a
passing, reviewable test file, and a distinct downstream bug it surfaced
has been filed forward with its own bead rather than swept under this one.
There is no remaining acceptance criterion this bead's text asks for that
is still open. Full suite: 703 passed, 16 skipped, 1 xfailed.
