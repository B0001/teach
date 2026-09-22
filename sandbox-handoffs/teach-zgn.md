# teach-zgn handoff

## Status: FIXED. Bead closed.

## The bug

A fresh, blind, tool-less held-out fixture (`GROUP_HOMOMORPHISMS_BLIND`,
authored while validating teach-jkx) — a full tutor/student dialogue clearly
about GROUP homomorphisms (`f(a*b) = f(a)*f(b)`, kernel, image,
injective/surjective, worked examples using `Z -> Z/nZ` reduction mod n, the
determinant map on invertible matrices) — was recovered via
`recover_from_lesson_text()` as `judson:16.3-ring-homomorphisms-and-ideals`
(raw score 20) instead of the correct `judson:11.1-group-homomorphisms` (raw
score 6, not even runner-up). This fires at the RAW word-overlap tier, before
semantic scoring ever runs — structurally different from teach-jkx (no
WordNet inflation involved).

## Root cause

`judson:16.3-ring-homomorphisms-and-ideals`'s own node text is long and
explicitly explains ring homomorphisms BY ANALOGY to group homomorphisms
("Similarly, a homomorphism between rings preserves...", "Just as with group
homomorphisms and normal subgroups..."), so its distinctive vocabulary
legitimately contains a lot of genuinely group-homomorphism-flavored language
(`homomorphism`, `kernel`, `isomorphism`, `normal subgroup`, `structure
preserving`). `judson:11.1-group-homomorphisms`'s own hand-authored node text
was comparatively thin — 7 distinctive words after document-frequency
filtering: `homomorphism, homomorphisms, kernel, mapped, normal, preserving,
structure`. It had never been given credit for `injective` or `image`, both
of which are real, core Judson ch. 11 vocabulary (the chapter states the
Z_7→Z_12-has-no-injective-homomorphism example and defines the image of a
homomorphism directly).

Measured baseline (verified by temporarily reverting the node to its
pre-fix content and re-running `score_candidates`/`_resolve_candidates`
diagnostics directly, not guessed):
- `judson:11.1-group-homomorphisms`: raw score 6, 85.7% coverage of its own
  (then 7-word) vocabulary.
- `judson:16.3-ring-homomorphisms-and-ideals`: raw score 20, ~37% coverage
  of its own (large, auto-extracted) vocabulary.
- The decisive-margin veto's credibility gate
  (`_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO=0.35`) requires a rival to score
  at least `0.35 * 20 = 7.0` to be considered a credible enough rival to
  trigger the coverage-gap veto against the raw-score leader.
  `judson:11.1`'s score of 6 fell just short of that bar (ratio ~0.30), so
  it was never even considered — the raw tier returned a confident,
  uncontested wrong answer (`judson:16.3`) instead of abstaining.

## The fix

Added genuine, real-textbook-sourced vocabulary to
`judson:11.1-group-homomorphisms` in `teach/judson_algebra_graph.py`: added
`"injective"` and `"image"` to `key_terms`, and added two sentences to
`definition` — the Z_7→Z_12 injective-homomorphism-doesn't-exist example, and
the image-of-phi definition — both drawn from the real Judson `homomorph.xml`
source (fetched directly from the pinned GitHub commit
`3069910e3ded72ff5e18837a97a0e810c92790e2`, not recalled from memory, per
sandbox-prompt.md's "fetch raw bytes yourself" discipline).

This grows the node's distinctive vocabulary from 7 words to 10
(`divide, image, injective` added). After the fix:
- `judson:11.1-group-homomorphisms`: raw score 8, 80.0% coverage of its own
  (now 10-word) vocabulary. Ratio against the winner: `8/20 = 0.40`, clears
  the 7.0 / 0.35 credibility bar.
- With `judson:11.1` now a credible rival, the coverage-gap veto fires (its
  80.0% coverage vs. `judson:16.3`'s ~37% coverage is a large gap), and
  `recover_from_lesson_text(GROUP_HOMOMORPHISMS_BLIND, GRAPH)` now safely
  **abstains** (`taught_node_id=None`, non-`None` `abstain_reason`) instead
  of confidently returning the wrong ring-homomorphisms node.

`judson:16.3` itself was not touched — it is correctly, extensively
vocabularied auto-extracted content, and the pre-existing calibration case
`RING_HOMOMORPHISMS` (a genuine ring-homomorphisms lesson) was confirmed
still correctly recovers `judson:16.3-ring-homomorphisms-and-ideals` with
`abstain_reason is None`, unaffected by this change.

## Why a threshold change was ruled out

The pre-compaction portion of this session found the new bug case's
credibility ratio (~0.30, just under the 0.35 bar) sits uncomfortably close
to a pre-existing, must-not-veto calibration case's ratio (~0.294, correctly
excluded by the same bar). Moving `_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO`
down far enough to admit the bug case as a credible rival risks also
admitting that calibration case, which would falsely trigger a veto where
none should fire. This repo's own documented history in this exact module
(teach-9wx, teach-hpa, teach-ceg, teach-i35, teach-l7u, teach-scx, teach-911,
teach-jkx) is a long, repeated pattern of pure threshold-moves getting
falsified by fresh held-out fixtures. Consistent with that pattern and with
teach-59u/teach-911's precedent, this fix instead adds genuine vocabulary
content to the thin node, which is what was actually missing.

## Iteration (what didn't work)

1. **"homomorphic image" as a key term + reworded definition sentence** —
   fixed the target bug, but caused 7 test failures. Diagnosis found that
   `test_signposted_prerequisites_are_recovered`'s fixture text
   (`SIGNPOSTED_LESSON`) already abstains at the raw tier for unrelated
   reasons and falls through to the SEMANTIC tier, whose result is
   sensitive to `judson:11.1`'s vocabulary in ways not visible from raw-tier
   inspection alone — this larger vocabulary addition tipped that semantic
   fallback the wrong way. (General lesson: testing `_resolve_candidates`
   directly on raw-tier `score_candidates()` output does NOT reflect
   `recover_from_lesson_text()`'s true behavior whenever the raw tier
   abstains for that text — must always test through the public entry
   point.)
2. **"surjective" + "determinant" instead of "image"** — tried to sidestep
   a suspected vocabulary collision with `judson:1.2-sets-and-equivalence-
   relations` (which uses "image" in a deliberate 3-way-ambiguity test).
   Made things worse: 10 failures, including new regressions in ring/group-
   axioms round5/round6/round7 tests not present with the "image" version.
3. **Settled: "injective" + "image" only** — 5 failures remained, all
   legitimate and expected (see below), none of them new regressions
   unrelated to this vocabulary change.

## Test updates made

- `tests/test_concept_recovery_judson_full_graph_generalization_round10.py`:
  `test_group_homomorphisms_confident_wrong_answer_is_teach_zgn_not_teach_jkx`
  and `test_group_homomorphisms_bug_is_raw_tier_not_semantic_tier` — both
  rewritten to assert the new safe-abstention outcome (previously asserted
  the confident-wrong-answer bug as a documented-bug baseline), with
  measured-not-guessed before/after numbers in the docstrings.
- `tests/test_concept_recovery_judson_full_graph_generalization_round8.py`:
  one pinned raw-score assertion for `judson:11.1-group-homomorphisms`
  updated from `== 4` to `== 5` on an unrelated fixture
  (`GROUP_HOMOMORPHISMS_FRESH`) — the node's vocabulary grew, so its score
  on this fixture grew too, but the fixture's actual abstention outcome
  (`taught_node_id is None`) is unchanged. Confirmed via diff this is the
  only behavioral difference.
- `tests/test_concept_recovery.py`:
  `test_semantic_tier_abstains_on_a_genuinely_ambiguous_math_paraphrase` —
  this test's premise was itself invalidated by the fix. Its fixture spends
  most of its length on homomorphism/kernel/image content with one aside
  sentence on isomorphism; before the fix, `judson:11.1` had no "image" in
  its vocabulary so this looked ambiguous. After the fix it decisively and
  correctly recovers `judson:11.1-group-homomorphisms` (raw tier: score 5 vs
  runner-up 3). Assertions flipped from expecting abstention to expecting
  this correct, decisive recovery, with the reasoning documented in the
  docstring. (See that docstring for the still-genuinely-ambiguous sibling
  test that continues to correctly abstain, confirming this wasn't an
  across-the-board loosening.)
- `teach/data/learning_commons_export/nodes.jsonl` — regenerated via
  `teach/learning_commons_export.py`'s own `main()`/`--write` mechanism
  (invoked as `uv run python -c "from teach import learning_commons_export
  as lce; lce.main()"` since running the file directly as a script breaks
  its internal package-relative imports). This resolved the
  `test_written_dataset_matches_what_the_builder_produces` drift-guard
  failure caused by `judson:11.1`'s vocabulary change rippling into the
  exported dataset.

## Final verification

`uv run pytest -q`: **712 passed, 16 skipped, 1 xfailed, 0 failed** — run
against the full, live shared working tree (see note below).

- Target bug fixture (`GROUP_HOMOMORPHISMS_BLIND`) confirmed safely abstains,
  not a confident wrong answer.
- Pre-existing calibration case (`RING_HOMOMORPHISMS`) confirmed unaffected,
  still correctly recovers `judson:16.3-ring-homomorphisms-and-ideals`.

## Note: shared/concurrent sandbox

This working tree has many other concurrent agent sessions' uncommitted
changes present (other beads' modified/untracked files — e.g.
`teach/biblical_nt_source.py`, `teach/fact_checker.py`,
`teach/extract_judson_ring_field.py`, various `tests/test_biblical_*.py`,
other `sandbox-handoffs/teach-*.md` files, and an unrelated hunk in
`judson_algebra_graph.py` touching `judson:2.1-the-division-algorithm`
explicitly commented as belonging to bead teach-59u). None of that is part
of this work; it's flagged here only so a future reader isn't confused by
`git status` looking larger than this bead's actual diff. This session's own
diff footprint is precisely: the `judson:11.1-group-homomorphisms` node in
`teach/judson_algebra_graph.py`, the four test files listed above, and the
regenerated export artifact.

No commit/push/sync was performed (conservative git policy, not asked to).
