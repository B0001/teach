# teach-ceg handoff

## Bead

teach-ceg (P2 bug): "concept_recovery: `_DECISIVE_MARGIN_COVERAGE_GAP`
near-miss lets a confident wrong answer through (SETS_EQUIVALENCE, gap 24pt
vs 25pt bar)." Full text in `bd show teach-ceg`. discovered-from teach-hpa.

## Status: CLOSED

The bead's named fix (`_DECISIVE_MARGIN_COVERAGE_GAP` recalibrated from 0.25
to 0.18) and its full reasoning were already implemented and documented in
`teach/concept_recovery.py`, and `tests/test_concept_recovery_judson_full_graph_generalization_round3.py`
already contained a passing test confirming SETS_EQUIVALENCE now abstains
instead of confidently misnaming `judson:18.2-factorization-in-integral-domains`
-- all of that was done in a prior, uncommitted session that claimed this
bead (`started_at` was set) and then stopped without leaving `bd` notes, a
handoff, or closing the bead. I found this working tree in that state at the
start of this session (see "What I found already done" below), read it
carefully, confirmed it was sound, then supplied the one thing genuinely
still missing per the bead's own explicit closing requirement: **a fresh
held-out round dedicated to this bead**, since none of the several
downstream beads that had since built on top of the 0.18 fix (teach-57f,
teach-443, teach-59u, teach-911, teach-scx, teach-9ba, teach-jkx) had run one
in this bead's own name.

## What I found already done (not authored by me this session)

`teach/concept_recovery.py`:

- `_DECISIVE_MARGIN_COVERAGE_GAP = 0.18` (was 0.25). The in-code comment
  (search `teach-ceg` in that file, ~line 396-425) derives 0.18 from the
  PRE-EXISTING calibration pair this constant already had (a 7.9-point "must
  not veto" case and a 39.6-point "must veto" case, both from teach-9wx/
  teach-hpa's own work) using an asymmetry argument already established
  elsewhere in the same file (a false abstention is cheaper than a confident
  wrong answer, so the veto threshold should sit closer to the safe boundary
  than the danger boundary): roughly one third of the way from 7.9 to 39.6
  gives 0.18. This is real, principled recalibration -- it was NOT derived
  by taking SETS_EQUIVALENCE's 24-point gap and picking a number just below
  it, which would have been overfitting to the one case that found the bug.
  I re-derived the arithmetic by hand (7.9 + (39.6-7.9)/3 ≈ 18.47, rounds to
  18) and confirm it matches what the comment claims.
- `tests/test_concept_recovery_judson_full_graph_generalization_round3.py`'s
  `test_sets_equivalence_now_abstains_instead_of_a_confident_wrong_answer`
  already asserted the fixed behavior and already passed.

I made no changes to the `_DECISIVE_MARGIN_COVERAGE_GAP` value itself, or to
round3's test, this session -- both were already correct. (I did fix two
unrelated stale-documentation numbers in `tests/test_concept_recovery.py` --
see "What I did," item 1.)

What was missing, and is why the bead was still open: the bead's own
explicit closing requirement --

> Any fix must not use this bead's own SETS_EQUIVALENCE fixture ... to
> validate -- it is now tuning data -- and needs its own fresh held-out
> round before closing.

-- had not been satisfied by a round run *in this bead's name*. Several
later, unrelated beads (teach-57f's round4, teach-59u's round5, teach-911's
round6, teach-9ba/teach-jkx's round7) all incidentally ran fresh dialogues
against the current tree (which already had 0.18) and found zero
regressions traceable to that threshold -- real evidence, and I cite it
below -- but none of them was authored to test `_DECISIVE_MARGIN_COVERAGE_GAP`
specifically, and round7's GROUP_AXIOMS_BLIND case (29.5-point gap) clears
0.18 by such a wide margin it says little about whether 0.18 itself has a
near-miss failure in the same direction as the bug this bead fixed.

## What I did

1. **Fixed two stale numeric references** in `tests/test_concept_recovery.py`
   (`test_decisive_margin_still_abstains_when_a_rival_is_covered_far_better`
   and `test_decisive_margin_not_second_guessed_when_the_rival_gap_is_narrow`):
   both docstrings stated `_DECISIVE_MARGIN_COVERAGE_GAP` was "(0.25)" as a
   *current* fact, which stopped being true the moment this bead's fix
   landed (the assertions themselves were unaffected either way, since 62.5pt
   and 7.9pt both sit on the same side of 0.18 as they did of 0.25 -- this
   was a documentation staleness, not a logic bug). Updated both to name the
   actual current value (0.18) and note the teach-ceg change, per this
   repo's "a number in a document must match the code, or say where it came
   from" standard. Full suite re-run after this edit: still 700 passed, 16
   skipped, 1 xfailed -- confirmed no behavior change.

2. **Ran this bead's own fresh held-out round**, deliberately dedicated to
   `_DECISIVE_MARGIN_COVERAGE_GAP`, not borrowed from a sibling bead's
   round. Every one of the 20 nodes in `load_judson_full_graph()` already
   has a fixture somewhere in rounds 1-7 (checked directly: grepped every
   round file's fixture names against the graph's node list), so there is
   no genuinely untouched topic left -- "fresh" here means what round4
   already established it means once the graph runs out of unused nodes:
   newly, independently authored dialogue text on a topic already in the
   graph, produced blind and measured once. I picked three topics
   deliberately chosen to stress the mechanism, not to make it easy to
   pass: `judson:6.1-cosets` (paired against `judson:6.2-lagranges-theorem`,
   the exact rival pair `_DECISIVE_MARGIN_COVERAGE_GAP` was calibrated never
   to break -- see the SIGNPOSTED_LESSON comment in concept_recovery.py),
   `judson:9.1-definition-and-examples` (isomorphisms), and
   `judson:11.1-group-homomorphisms` (the exact topic of teach-9wx's
   original bug).

3. **Ran three separate, fully blind `Agent` calls** (no tool access, no
   repository access, told only a plain-English topic name and asked to
   write a 300-500 word tutor/student dialogue from general knowledge alone,
   with no reference to a specific textbook and no mention of this repo,
   concept_recovery.py, or any threshold/mechanism in it). None of the three
   agents saw another's output, this bead, or any prior round's fixtures.

4. **Measured all three once, honestly**, against the real, unmodified,
   current-tree `load_judson_full_graph()`, via the public
   `recover_from_lesson_text` / `score_candidates` / `_resolve_candidates`
   entry points only -- no internals read to choose or adjust the texts, no
   threshold or word list changed in response to seeing the results:

   - **0/3 correct recoveries. 3/3 safe abstentions. 0/3 confident wrong
     answers.**
   - **COSETS_FRESH** is the one directly on point: `judson:6.2-lagranges-
     theorem` leads raw overlap decisively (score 12, margin 7 -- the exact
     shape of case this bead's mechanism gates) but covers only 80% of its
     own vocabulary, while the correct answer `judson:6.1-cosets` covers
     100% of its own -- a **20-point gap**, 2 points clear of the new 0.18
     threshold and squarely inside the [18, 25) zone the old 0.25 threshold
     would NOT have caught. Under the pre-teach-ceg code this fresh,
     independently-authored dialogue would have been a confident wrong
     answer (Lagrange's theorem instead of cosets) -- the same failure
     shape as the bead's own named bug, on a different rival pair, never
     seen or tuned against before this measurement. This is the closest
     thing to a direct, dedicated confirmation that 0.18 does not carry its
     own near-miss failure in the same direction as the 0.25 bug it
     replaced. It is one data point, not proof the boundary is safe
     everywhere -- see "What's NOT done" below.
   - **ISOMORPHISMS_FRESH** and **GROUP_HOMOMORPHISMS_FRESH** both abstain
     via a different branch entirely (the bare-minimum-margin "too close to
     call" path -- top score 7 vs runner-up 6, margin 1, below
     `_MIN_MARGIN`), not the decisive-margin path this bead touched. Their
     correct answers (`judson:9.1`, `judson:11.1`) each clear
     `_MIN_MATCH_WORDS` (score 4) but are not competitive (3 points behind
     the leader) -- an honest recall gap, not a confident-wrong-answer
     failure, and out of this bead's scope. Recorded because
     isomorphisms/homomorphisms are this lineage's historically most
     fragile topics (teach-9wx's original bug was HOMOMORPHISMS); a null
     result here is worth having on record even though it doesn't
     specifically test `_DECISIVE_MARGIN_COVERAGE_GAP`.

5. **Wrote the permanent record**:
   `tests/test_concept_recovery_judson_full_graph_generalization_round8.py`
   (new file) -- module docstring covering methodology and the full honest
   result tally, three tests (one per topic), each asserting the actually
   measured outcome. `test_cosets_fresh_hits_decisive_margin_coverage_gap_veto`
   explicitly asserts the gap lands in `[0.18, 0.25)` so the test would fail
   loudly (rather than silently stop meaning anything) if a future change
   moved this case out of the zone that makes it a real test of this bead's
   fix.

6. **Re-ran the full suite** after the new round and the docstring fix:
   `uv run pytest -q` → **703 passed, 16 skipped, 1 xfailed** (up from 700
   passed at session start; the 3 new round8 tests, zero regressions
   elsewhere). Also re-ran `teach/concept_recovery.py`'s own standalone
   self-check (`python3 concept_recovery.py`, per this repo's `uv run
   pytest` + module-self-check convention) -- exits 0, same OK message as
   before.

## Test suite status

- `uv run pytest -q`: **703 passed, 16 skipped, 1 xfailed**.
- `uv run pytest tests/test_concept_recovery_judson_full_graph_generalization_round8.py -v`:
  all 3 new tests pass individually.
- `uv run pytest tests/test_concept_recovery.py -q`: passes, including the
  two docstring-corrected tests (logic unchanged, numbers now accurate).
- `PYTHONPATH=/workspace uv run python3 teach/concept_recovery.py`: exits 0.

## Files changed this session

- `tests/test_concept_recovery.py` -- two docstring corrections (0.25 →
  0.18, with attribution to teach-ceg), no assertion/logic changes.
- `tests/test_concept_recovery_judson_full_graph_generalization_round8.py`
  -- new file, this bead's own required fresh held-out round.
- `sandbox-handoffs/teach-ceg.md` -- this file.

`teach/concept_recovery.py` itself (the `_DECISIVE_MARGIN_COVERAGE_GAP`
fix and its comment) and
`tests/test_concept_recovery_judson_full_graph_generalization_round3.py`
(the SETS_EQUIVALENCE test) were inspected and verified but NOT modified
this session -- their content was already complete and correct from the
prior uncommitted session that claimed this bead.

Nothing committed (conservative git policy; no explicit request to commit
this session). The working tree also contains substantial uncommitted work
from many other beads (visible in `git status`: `teach/biblical_nt_source.py`,
`teach/biblical_ot_source.py`, `teach/fact_checker.py`,
`teach/extract_judson_ring_field.py`, `teach/judson_algebra_graph.py`,
`teach/data/judson_ring_field.json`, several `tests/test_biblical_*` and
`tests/test_concept_recovery_judson_full_graph_generalization_round{2,3,4,5,6,7}.py`
files, and numerous untracked handoff/test files from sessions on other
beads) -- all left untouched, out of this bead's scope. Suggested next
commands, if/when asked to commit just this bead's work:

```
git status
git diff tests/test_concept_recovery.py
git add tests/test_concept_recovery.py \
  tests/test_concept_recovery_judson_full_graph_generalization_round8.py \
  sandbox-handoffs/teach-ceg.md
# teach/concept_recovery.py and round3's test file were changed by a prior
# (uncommitted) session, not this one -- confirm with whoever owns that
# work, and everything else currently dirty in the tree, before bundling
# into the same commit.
git commit -m "..."
```

## What's NOT done / left for whoever picks this up

- This round found exactly one case (COSETS_FRESH) that lands in the
  `[18pt, 25pt)` zone that distinguishes the new threshold from the old one.
  One case is evidence, not proof -- a future round that happens to produce
  a gap sitting *just under* 18 (the same shape of near-miss as the
  original bug, one layer down) would be the sharper test, and this round
  didn't happen to produce one. Nothing suggests such a case exists; nothing
  rules it out either.
- Per this lineage's own established pattern (teach-hpa, teach-jkx), this
  round's three fixtures are now tuning data for `_DECISIVE_MARGIN_COVERAGE_GAP`
  and must not be reused to validate any future change to that constant.
- **teach-jkx** (discovered from a downstream bead, still open, P2): a
  structurally different bug in the same neighborhood -- the semantic
  (WordNet) fallback tier's `credible_rivals` filter compares tier-native
  (synonym-inflated) scores, which can silently drop the true best-covered
  rival when its score doesn't inflate as much as the winner's, producing a
  confident wrong answer at the semantic tier even when the raw tier
  correctly abstains. Not this bead's mechanism (a different check, a
  different tier) and not fixed here -- left exactly as I found it.
- **teach-443** (already closed) and the still-open **teach-57f** (P3):
  `judson:18.2-factorization-in-integral-domains`'s generic-vocabulary-
  attractor behavior. Unrelated to this bead's mechanism; also unaffected by
  anything done this session.
- `load_judson_algebra_graph()` (11-node) remains the production default;
  `load_judson_full_graph()` (20-node) is still not used by any production
  consumer -- this whole lineage continues to be about what happens if/when
  a consumer is switched to the full graph.

## Lineage

teach-cpg -> teach-i35 -> teach-ngy -> teach-9wx (added
`_DECISIVE_MARGIN_COVERAGE_GAP`, found and filed teach-hpa) -> teach-hpa
(added the rival-credibility ratio gate, found and filed teach-ceg and
teach-443) -> **teach-ceg (this bead)**: recalibrated
`_DECISIVE_MARGIN_COVERAGE_GAP` from 0.25 to 0.18 to close the near-miss on
SETS_EQUIVALENCE, verified with its own dedicated fresh held-out round
(round8) rather than borrowed validation from the several sibling beads
(teach-57f, teach-443, teach-59u, teach-911, teach-scx, teach-9ba, teach-jkx)
that had since built on top of the same fix. teach-jkx (found downstream,
still open) shows this general shape of problem -- a bag-of-words scorer's
score inflation defeating a coverage-based safety gate -- recurs in a third,
structurally distinct place (the semantic tier's credibility filter), not
just the two this bead and teach-hpa already closed.
