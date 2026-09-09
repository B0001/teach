# teach-ed3 — concept_recovery: taught-concept margin is fragile for full prerequisite-chain lessons

## What was wrong

`concept_recovery.recover_taught_concept` picked the highest-scoring node by
raw distinctive-word overlap and abstained unless it beat the runner-up by
`_MIN_MARGIN=2`. That raw-count rule is biased toward whichever candidate
happens to have the *larger* vocabulary, not whichever candidate the lesson
actually gave its deepest treatment to. A lesson that walks a full
prerequisite chain with real definitional content at every step (not just
lightly touching prerequisites while mostly narrating the target — the shape
`teach/dnf_bond_lesson.py` uses) routinely gives an earlier scaffolding node
(e.g. cosets, on the way to Lagrange's theorem) a large raw overlap too,
purely because that node's own vocabulary list is longer. teach-8xw.15's
first draft of that lesson scored Lagrange 13 vs. cosets 12 — a margin of 1,
below the bar — and the checker abstained on a lesson that was correctly and
fully teaching Lagrange's theorem. The fix applied there (adding the word
"proof", already present in the target node's own facts) got the margin to
exactly 2, but that was one word of margin, not a robust property: any other
full-chain lesson author who didn't happen to reach for every one of the
target's distinctive words risked the same incorrect abstention.

## What was built

A second, independent signal — coverage — that gets a chance to resolve the
match ONLY when the raw-score margin doesn't clear `_MIN_MARGIN`, in
`teach/concept_recovery.py`:

- `_coverage_fraction(match, index)`: what fraction of a candidate node's own
  distinctive vocabulary appears in the text at all
  (`match.score / len(node's distinctive vocabulary)`).
- In `recover_taught_concept`, when the top candidate's raw margin over one
  or more close rivals falls under `_MIN_MARGIN`, the tiebreak fires only if
  **both**:
  - the top candidate's coverage fraction is >= `_MIN_COVERAGE_FRACTION`
    (0.85) — near-total coverage of its own vocabulary, i.e. this is the
    node the lesson's climactic, most detailed passage is actually about, and
  - that fraction beats **every** other close-on-raw-score rival's own
    coverage fraction by >= `_MIN_COVERAGE_MARGIN` (0.15) — a decisive gap,
    not just a marginally higher one.

  Both conditions are required so two candidates that are each partially and
  similarly covered (a genuinely ambiguous match) still abstain — this is
  chosen deliberately over the "direction 2" tiebreaker suggested in the
  bead (last node in a recoverable topological chain), because that
  tiebreaker would have used graph edge structure the checker has no
  business leaning on for concept *identification* (edges only enter
  *after* the taught concept is known, for prerequisite recovery) and would
  have resolved on structure rather than on what the text actually says.

This is direction 1 from the bead ("weight a node's score by how much of the
lesson's content is about it") implemented at the per-candidate level
(fraction of *that node's* vocabulary covered) rather than per-lesson
(fraction of *turns/sentences* devoted to it) — cheaper to compute
correctly from the same `ConceptMatch` data already produced by
`score_candidates`, and it does not require sentence-to-node attribution
that nothing else in this module currently does.

Full write-up of the design and its reasoning is in the module docstring's
new "COVERAGE TIEBREAK (teach-ed3)" section and the constants' comments in
`teach/concept_recovery.py`.

## Evidence this fixes the actual fragility (not just passes new tests written to fit the fix)

`tests/test_concept_recovery.py::test_dnf_bond_lesson_recovers_lagrange_without_a_single_word_margin`
takes the REAL, already-built `teach/dnf_bond_lesson.py` lesson text,
mechanically removes the word "proof" (undoing the exact one-word fix
teach-8xw.15 applied), reproduces the fragile margin-of-1
(`Lagrange 13 → 12, cosets stays 12` — asserted explicitly, not assumed),
and confirms `recover_from_lesson_text` still recovers
`dummit-foote:3.2-lagrange-theorem`, not abstention. This is the concrete
regression check for the bug as reported, not a synthetic stand-in for it.

Two more targeted tests, using single-letter node labels so the label
contributes no extra vocabulary and the coverage arithmetic is exact:

- `test_coverage_tiebreak_resolves_a_full_chain_lessons_margin_of_one` —
  a synthetic 2-node chain reproducing the shape of the bug generically
  (raw scores 5 vs 4, margin 1, target's coverage 5/5=1.0 vs. rival's
  4/6=0.667) — must recover, not abstain.
- `test_coverage_tiebreak_does_not_rescue_similarly_partial_coverage` — same
  graph, but the text only partially covers the target (3/5 = 0.6, below
  the 0.85 coverage bar) — must still abstain. This is the "do not silently
  soften abstention" guard the bead required: proof the tiebreak only fires
  on near-total, decisive coverage, not on any coverage edge at all.

## Abstention behavior preserved

All pre-existing abstention fixtures still abstain, unchanged:

- `tests/test_concept_recovery.py::test_ambiguous_candidates_abstain_rather_than_guess`
  — exact raw-score tie (3 vs 3), coverage tie too (0.75 vs 0.75, same
  vocab-size-4 nodes) — the tiebreak's `_MIN_COVERAGE_FRACTION=0.85` bar
  isn't even cleared, so this abstains exactly as before.
- `tests/test_concept_recovery.py::test_abstain_example_out_of_graph_vocabulary`,
  `test_no_vocabulary_overlap_abstains_with_its_own_reason` — these hit the
  earlier `_MIN_MATCH_WORDS` gate, upstream of the tiebreak entirely,
  unaffected.
- `tests/test_dummit_foote_graph.py` — all 8 tests pass unchanged (BOND_LESSON,
  SIGNPOSTED_LESSON, isomorphism-theorems closure, unsignposted/assumed
  split). None of these needed the tiebreak — their raw margins already
  cleared `_MIN_MARGIN` on their own (verified: they were passing before
  this change and are unmodified now).

## Verification

```
uv run pytest -q                              # 162 passed (was 159; +3 new tests)
uv run python -m teach.concept_recovery       # OK, same abstain/recover pair as before
uv run python -m teach.dnf_bond_lesson        # OK: 14-turn lesson, boundary clean (unchanged)
uv run python -m teach.dummit_foote_graph     # OK: 11 nodes, 13 edges (unchanged)
```

## Files touched

- `teach/concept_recovery.py` — `_coverage_fraction`, `_MIN_COVERAGE_FRACTION`,
  `_MIN_COVERAGE_MARGIN`, and the tiebreak logic in `recover_taught_concept`;
  module docstring gained a "COVERAGE TIEBREAK (teach-ed3)" section.
- `tests/test_concept_recovery.py` — 3 new tests (see above); one new import
  (`score_candidates`, already public, used to assert on raw scores directly
  so the tests document the exact margin they're exercising rather than
  asserting only on the final recovered/abstained outcome).

Nothing committed — conservative git policy, not asked to commit.
Pre-existing untracked files from other beads (`teach/dnf_bond_lesson.py`,
`teach/dnf_bond_integration.py`, `tests/test_dnf_bond_integration.py`,
`sandbox-handoffs/teach-8xw.15.md`) were left exactly as found; this bead
did not touch them (`dnf_bond_lesson.py`'s "proof" word fix is untouched —
still legitimate content, it's just no longer the only thing standing
between this lesson and an incorrect abstention).

## Follow-up

None filed. The bead's three possible directions were: (1) content-weighted
scoring — done, as coverage-of-own-vocabulary; (2) topological
last-node tiebreak — considered and deliberately not used, see rationale
above; (3) just document the sensitivity — insufficient on its own per the
bead's "any fix must keep or improve abstention," which asked for behavior,
not just documentation, though the documentation half is also done (module
docstring).
