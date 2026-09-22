# teach-9wx handoff

## Bead

teach-9wx (P2 bug): "concept_recovery: decisive raw-score margin bypasses the
coverage check entirely, letting a long verbatim node beat a correct terse
rival." Full text in `bd show teach-9wx`. discovered-from teach-ngy.

## Status: CLOSED

The bead's named mechanism is fixed, unit-verified in isolation, does not
regress the full suite (553 passed, 16 skipped, 1 xfailed, up from 548 before
this session), and a genuinely fresh, independently-authored held-out round
(zero access to this bead, its file, or the module's thresholds) produced
zero confident wrong answers. That fresh round also surfaced a real,
disclosed recall cost of the fix -- filed forward as teach-hpa rather than
chased in this session, per this lineage's rule against tuning a fix against
the same round that measured it.

## What I did

1. **Reproduced the bug independently.** Loaded `load_judson_full_graph()`
   (20 nodes), ran the HOMOMORPHISMS lesson (semantic tier) through
   `recover_from_lesson_text`. Confirmed the bead's exact reproduction:
   `judson:16.3-ring-homomorphisms-and-ideals` scores 17, decisively beating
   the runner-up (margin 7, well past `_SEMANTIC_MIN_MARGIN`'s 3), while
   covering only 17.5% of its own distinctive vocabulary. The true answer,
   `judson:11.1-group-homomorphisms`, scores 7 (third place by raw count)
   but covers 57.1% of its own vocabulary -- a 39.6-point coverage gap the
   old code never looked at, because the decisive-margin path of
   `_resolve_candidates`'s single-close-candidate branch returned the
   raw-score leader unconditionally, with no coverage check of any kind.

2. **First fix attempt failed and was reverted.** Tried pulling
   `_MIN_WINNING_COVERAGE` (the existing near-margin self-floor check) out
   so it applied unconditionally, regardless of margin. This broke two
   legitimate, previously-passing tests
   (`test_two_sentence_announcement_recovered_against_the_real_graph`,
   `test_faithful_paraphrase_recovers_via_semantic_fallback_tier`) whose
   correct winners had genuinely low absolute coverage (16.2% and 8.1%) from
   large vocabularies matched via paraphrase/semantic credit -- one of them
   numerically *lower* than the bug's own 17.5%, so an absolute floor cannot
   tell the legitimate low-coverage wins from the bug's illegitimate one.
   Reverted.

3. **Actual fix**: added `_DECISIVE_MARGIN_COVERAGE_GAP = 0.25` and a new
   `else:` branch in `_resolve_candidates` (attached to the existing
   `margin <= min_margin` branch, so it only runs on the OTHER side --
   `margin > min_margin`, the decisive case). It searches every candidate
   clearing `_MIN_MATCH_WORDS` (excluding the winner) for the best-covered
   rival, and abstains only if that rival's coverage exceeds the winner's own
   by >= 0.25. A *relative gap*, not an absolute floor, because the
   discriminating signal is "is some rival covered so much better that the
   winner looks like incidental overlap by comparison" -- not "is the
   winner's absolute coverage low," which the first attempt's failure showed
   is not by itself evidence of anything. Calibrated on three measured gaps:
   `SIGNPOSTED_LESSON` (a real decisive win that must NOT be vetoed, 7.9-point
   gap), a real correctly-recovered VA Math SOL paraphrase (1.9-point gap,
   also must not be vetoed), and the bug's own HOMOMORPHISMS case
   (39.6-point gap, must be caught). The three numbers cluster with a wide
   (~0.24) empty gap in the middle; 0.25 sits in it. Full rationale is in the
   code comment directly above the new branch in `teach/concept_recovery.py`.

4. **Added two permanent unit tests**
   (`tests/test_concept_recovery.py::test_decisive_margin_still_abstains_when_a_rival_is_covered_far_better`,
   `::test_decisive_margin_not_second_guessed_when_the_rival_gap_is_narrow`),
   fabricating `ConceptMatch`/`VocabularyIndex` objects directly, in the
   file's established style, proving the new gap check both fires and does
   NOT over-fire, in isolation from lesson-text/graph machinery.

5. **Diagnostically re-checked** (NOT as validation -- the bead explicitly
   forbids using this exact case to validate the fix) that
   `tests/test_concept_recovery_judson_full_graph_generalization.py`'s
   HOMOMORPHISMS case, renamed
   `test_homomorphisms_no_longer_a_confident_wrong_answer`, now safely
   abstains instead of confidently misnaming the concept. Appended a
   "TEACH-9WX" section to that file's module docstring (not rewritten --
   this repo's established pattern is to append updates, preserving
   teach-ngy's original narrative).

6. **Ran the bead's mandatory fresh held-out round.** Selected five topics
   from `load_judson_full_graph()`'s 20 nodes not covered by round1's six
   fixtures: ring homomorphisms and ideals, group isomorphisms, cyclic
   subgroups, integral domains vs. fields, and permutation groups. One
   topic -- ring homomorphisms and ideals -- was deliberately chosen to be
   the exact node that was the original bug's false winner
   (`judson:16.3-ring-homomorphisms-and-ideals`), but here as the TRUE
   target, to check the fix doesn't overcorrect against that node when it's
   genuinely what's being taught. Launched five separate, fully blind
   `Agent` calls (no tool access, zero repo/bug/threshold context, told only
   a plain-English topic name), each writing an independent tutor/student
   dialogue from its own general knowledge. None saw another's output, this
   module's code, or round1's fixtures. Measured all five against the
   unmodified `load_judson_full_graph()`, once, honestly, no tuning:

   - **2/5 correct**: cyclic_subgroups -> `judson:4.1-cyclic-subgroups`,
     permutation_groups -> `judson:5.1-definitions-and-notation`. Both
     decisive wins that are also well-covered, so the new gap check passes
     them through cleanly.
   - **3/5 safe abstentions, 0/5 confident wrong answers**:
     - `RING_HOMOMORPHISMS` -- the one case teach-9wx's new code actually
       decides. Leads decisively on raw score (17 vs runner-up 11) and,
       pre-fix, would have recovered *correctly*. But its own coverage is
       only 30% (generic homomorphism/kernel vocabulary shared with
       `judson:11.1-group-homomorphisms`, which covers 71% of its own here)
       -- a 41-point gap past the 0.25 threshold, so it now abstains instead
       of correctly answering. **This is the fix's real, disclosed cost**:
       it can turn a genuinely correct decisive win into a false abstention
       when a rival is much better covered by incidental/shared vocabulary,
       not just prevent false wins. Filed as teach-hpa rather than tuned
       away in this same round.
     - `ISOMORPHISMS` -- abstains through teach-ngy's pre-existing
       multi-candidate-tie branch (ties three ring-flavored candidates, none
       of which is the correct `judson:9.1-definition-and-examples`),
       confirmed by checking the abstain-reason text against source, unrelated
       to this bead.
     - `INTEGRAL_DOMAINS_FIELDS` -- abstains through the pre-existing
       near-margin self-floor check (teach-l7u/teach-i35's code), also
       confirmed unrelated to this bead.

7. **Converted the held-out round into a permanent test file**:
   `tests/test_concept_recovery_judson_full_graph_generalization_round2.py`
   -- all five fixtures, honest result narrative including the disclosed
   recall cost, one test per case, in the same style as round1.

8. **Filed teach-hpa** ("concept_recovery: decisive-margin coverage-gap
   check can turn a correct win into a false abstention"), discovered-from
   teach-9wx, documenting the RING_HOMOMORPHISMS finding, why it's not a
   regression against this bead's own bar (zero confident wrong answers),
   what's not attempted and why, and the same held-out-round discipline
   applied forward.

9. Ran the full suite one final time after adding the round2 file:
   **553 passed, 16 skipped, 1 xfailed** -- clean, no regressions.

## Files changed

- `teach/concept_recovery.py` -- new `_DECISIVE_MARGIN_COVERAGE_GAP`
  constant and the new `else:` branch in `_resolve_candidates`'s
  single-close-candidate case, applying a rival-coverage gap check when the
  margin is decisive.
- `tests/test_concept_recovery.py` -- two new unit tests proving the
  mechanism in isolation (fires on a wide gap, does not fire on a narrow
  one).
- `tests/test_concept_recovery_judson_full_graph_generalization.py` --
  renamed/rewrote the HOMOMORPHISMS test to check safe abstention instead of
  pinning the old wrong answer; appended a TEACH-9WX section to the module
  docstring (original teach-ngy narrative preserved, not deleted).
- `tests/test_concept_recovery_judson_full_graph_generalization_round2.py`
  -- new file, the permanent record of this bead's required fresh held-out
  round.

Note: this session's working tree also already contained an uncommitted,
in-progress fix for teach-ngy's multi-candidate-tie branch (the "search all
tied candidates for best coverage, not just the raw-score leader" change) --
left completely untouched, not authored by me, not part of this bead's
scope.

Nothing committed (conservative git policy; no explicit request to commit
this session). Suggested next commands, if/when asked to commit:

```
git status
git diff --stat
git add teach/concept_recovery.py tests/test_concept_recovery.py \
  tests/test_concept_recovery_judson_full_graph_generalization.py \
  tests/test_concept_recovery_judson_full_graph_generalization_round2.py \
  sandbox-handoffs/teach-9wx.md
git commit -m "..."
```
(This leaves teach-ngy's own uncommitted multi-candidate-tie fix out of the
commit, since it isn't this bead's work -- worth flagging to whoever
actually runs the commit, in case teach-ngy wants it bundled separately or
together.)

## What's NOT done / left for whoever picks this up

- **teach-hpa** (filed this session): the decisive-margin gap check cannot
  currently distinguish "rival is better covered because the winner is a
  wrong answer" from "rival is better covered because both nodes
  genuinely share a lot of vocabulary but the winner is still the correct,
  decisively-signaled answer." Needs its own design (e.g. checking whether
  the rival's high-coverage words are also part of the winner's own
  vocabulary) and its own fresh held-out validation round -- do not use
  RING_HOMOMORPHISMS or any fixture in this bead's round2 file to validate
  it, per this repo's standing rule.
- teach-t7j (semantic-tier gap, filed by teach-i35) is still open and
  untouched by this session.
- `load_judson_algebra_graph()` (11-node) remains the default for all
  production consumers (`judson_bond_lesson.py`, `judson_bond_integration.py`);
  `load_judson_full_graph()` (20-node) is still not used by any production
  consumer. This bead, like teach-ngy before it, is about what happens if/when
  a consumer is switched to the full graph.

## Lineage

teach-cpg -> teach-i35 (fixed single-close-candidate branch's positional
rival-search bug; found and filed teach-t7j) -> teach-ngy (fixed the same
class of positional bug in the multi-candidate-tie branch; found and filed
teach-9wx) -> **teach-9wx (this bead)**: fixed the decisive-margin branch's
total bypass of coverage checking; found and filed teach-hpa for the
resulting gap-check's own recall cost. Each fix in this chain is real and
verified; each held-out round has found the next-deepest layer of the same
underlying problem (a growing graph's vocabulary-size and vocabulary-overlap
dynamics undermining a bag-of-words scorer's assumptions). teach-t7j and
teach-hpa are both still open.
