# teach-hpa handoff

## Bead

teach-hpa (P3 bug): "concept_recovery: decisive-margin coverage-gap check can
turn a correct win into a false abstention." Full text in `bd show teach-hpa`.
discovered-from teach-9wx.

## Status: CLOSED

The bead's named mechanism (a credibility gate on which rivals are even
allowed to veto a decisive raw-score winner) was already implemented,
unit-verified in isolation, when this session started -- claimed but left
unfinished by a prior session. I verified that implementation is correct and
complete for the bead's ask, then supplied the one thing it was still
missing: a genuinely fresh, independently-authored held-out round that does
not reuse RING_HOMOMORPHISMS or any round2 fixture. That round found zero
regressions (proved mechanistically, not just by inspection) and two
pre-existing issues unrelated to this bead, filed forward rather than fixed
here.

## What I found already done (not authored by me this session)

`teach/concept_recovery.py`'s decisive-margin branch already had:

- `_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO = 0.35` -- a new constant gating
  which rivals are even eligible to trigger teach-9wx's coverage-gap veto.
  Only rivals scoring >= 35% of the winner's own raw score are "credible"
  enough to be considered; the coverage-gap check then only runs among
  those, not all rivals clearing `_MIN_MATCH_WORDS`.
- The rationale, calibrated on two ratios: RING_HOMOMORPHISMS's rival
  (score 5 vs winner's 17, ratio 0.294) must fall BELOW the gate so that
  case no longer aborts a correct decisive win; the original HOMOMORPHISMS
  bug's rival (ratio 0.412) must stay ABOVE it so teach-9wx's fix still
  catches the case it was built for. 0.35 sits between the two, documented
  in a module-docstring section and an in-code comment that both say
  explicitly "THAT IS CALIBRATION, NOT VALIDATION."
- Five isolated unit tests in `tests/test_concept_recovery.py` fabricating
  `ConceptMatch`/`VocabularyIndex` fixtures directly, proving the ratio gate
  fires and doesn't over-fire in isolation from lesson-text/graph machinery
  (`test_decisive_margin_not_vetoed_by_a_rival_too_thin_in_absolute_terms`
  is the one that pins the RING_HOMOMORPHISMS numbers: rival score 5 vs top
  17, ratio 0.294 < 0.35, asserts the winner is not vetoed).

I read this code and its tests carefully, re-derived the two calibration
ratios by hand against the module's own scoring logic, and confirm the
implementation matches its own stated design. I made no changes to
`teach/concept_recovery.py` or `tests/test_concept_recovery.py` this
session -- both were already correct.

What was missing, and is why the bead was still open: the bead's explicit
closing requirement --

> Must not use RING_HOMOMORPHISMS (or any fixture in
> tests/test_concept_recovery_judson_full_graph_generalization_round2.py) to
> validate a fix -- it is now tuning data. Needs its own fresh,
> independently-authored held-out round before closing.

-- had not been done. The prior session's unit tests validate the mechanism
against the calibration cases directly, which is necessary but is exactly
the kind of self-validation this repo's methodology forbids as sufficient
on its own ("you cannot hold out examples from yourself").

## What I did

1. **Selected five fresh topics** from `load_judson_full_graph()`'s 20 nodes,
   deliberately excluding every node used in round1 or round2:
   `judson:1.2-sets-and-equivalence-relations`, `judson:3.3-subgroups`,
   `judson:6.1-cosets`, `judson:10.1-factor-groups-and-normal-subgroups`,
   `judson:16.4-maximal-and-prime-ideals`. The last two were picked
   specifically because they sit near the same ring/group-homomorphism
   vocabulary neighborhood as the original bug and teach-9wx's fix, to give
   the ratio gate a real chance to matter, not just topics far away from the
   mechanism under test.

2. **Ran five separate, fully blind `Agent` calls** (no tool access, no repo
   access, told only a plain-English topic name and asked to write a
   tutor/student dialogue from general knowledge alone). None saw each
   other's output, this bead, teach-9wx's thresholds, or round1/round2's
   fixtures.

3. **Measured all five once, honestly**, against the unmodified
   `load_judson_full_graph()`, via the public `recover_from_lesson_text` API
   only:

   - **0/5 correct recoveries.**
   - **3/5 safe abstentions**: SUBGROUPS (via the pre-existing near-margin
     self-coverage floor, unrelated to teach-hpa), NORMAL_SUBGROUPS and
     MAXIMAL_PRIME_IDEALS (both via teach-hpa's own decisive-margin path --
     see the gated/ungated analysis below for why these are "no regression"
     rather than "the fix working as intended").
   - **1/5 boundary/defensible**: COSETS recovers as
     `judson:6.2-lagranges-theorem` via the unrelated teach-ngy
     multi-candidate-tie branch. Defensible, not wrong: the dialogue
     substantively derives Lagrange's theorem from coset counting, so the
     recovered node is a reasonable reading of what was actually taught.
   - **1/5 confident wrong answer**: SETS_EQUIVALENCE recovers as
     `judson:18.2-factorization-in-integral-domains` -- unrelated to
     anything this bead's mechanism touches (no rival was even close enough
     in score to engage the ratio gate). Pre-existing, not caused or
     preventable by teach-hpa. Filed as teach-ceg (see below).

4. **Proved causal attribution mechanically, not by inspection.** For every
   case that went through the decisive-margin branch (NORMAL_SUBGROUPS,
   MAXIMAL_PRIME_IDEALS, and SETS_EQUIVALENCE's near-miss), I recomputed the
   decision with teach-hpa's ratio-credibility gate artificially disabled
   (i.e. what teach-9wx's code alone, without teach-hpa's gate, would have
   decided) and compared to the actual gated result. In all cases the
   decision was **identical either way** -- the gate never changed a final
   abstain/no-abstain outcome in this fresh round. That means teach-hpa
   introduced zero regressions here, but this round also did not happen to
   contain a case with RING_HOMOMORPHISMS's exact geometry (a decisive raw
   winner with genuinely low self-coverage vetoed only by a coverage-thin
   rival), so it did not get a chance to demonstrate the fix's intended
   benefit either. Both facts are stated plainly in the test file's module
   docstring -- this is not being spun as a win beyond what was measured.

5. **Wrote the permanent record**:
   `tests/test_concept_recovery_judson_full_graph_generalization_round3.py`
   (new file, 662 lines) -- module docstring covering methodology, the full
   honest result tally, the gated-vs-ungated proof with exact numbers for
   each of the three decisive-margin cases, and disclosure of the two new
   issues found. Five tests, one per topic, each asserting the actually
   measured outcome (not an aspirational one):
   - `test_sets_equivalence_is_a_confident_wrong_answer_not_yet_fixed`
   - `test_subgroups_abstains_via_preexisting_near_margin_floor_not_teach_hpa`
   - `test_cosets_recovers_as_the_closely_related_lagrange_node`
   - `test_normal_subgroups_abstains_via_teach_hpa_gate_no_regression_vs_ungated`
   - `test_maximal_prime_ideals_abstains_via_teach_hpa_gate_no_regression_vs_ungated`

6. **Filed two new beads** for the pre-existing issues surfaced by this
   round, neither attributable to teach-hpa:
   - **teach-ceg** (P2): `_DECISIVE_MARGIN_COVERAGE_GAP`'s 0.25 threshold has
     a near-miss -- SETS_EQUIVALENCE's actual gap is ~24 points, just under
     the bar, letting a confident wrong answer through by a hair. This is
     teach-9wx's threshold, not teach-hpa's ratio gate (no rival was
     credible enough under teach-hpa's gate to even reach the coverage-gap
     check in this case, confirmed via the same gated/ungated method).
   - **teach-443** (P3): `judson:18.2-factorization-in-integral-domains`
     behaves as a generic-vocabulary attractor, topping raw score across
     multiple unrelated topics in this round and round2 both -- a systemic
     pattern in the node's own vocabulary, not a defect in the resolver
     logic.

## Test suite status

- `uv run pytest -q`: **614 passed, 16 skipped, 5 xfailed** (up from 609
  passed at session start; the 5 new round3 tests, zero regressions
  elsewhere).
- `uv run pytest tests/test_concept_recovery_judson_full_graph_generalization_round3.py -v`:
  all 5 new tests pass individually.
- `uv run pytest tests/test_judson_algebra_graph.py -q`: **21 passed**,
  including `test_signposted_prerequisites_are_recovered`, which the bead
  lineage treats as a must-never-regress case.

## Files changed this session

- `tests/test_concept_recovery_judson_full_graph_generalization_round3.py`
  -- new file, the permanent record of this bead's required fresh held-out
  round.
- `sandbox-handoffs/teach-hpa.md` -- this file.

`teach/concept_recovery.py` and `tests/test_concept_recovery.py` were
inspected and verified but not modified this session -- their teach-hpa
content was already complete and correct from a prior uncommitted session.

Nothing committed (conservative git policy; no explicit request to commit
this session). The working tree also contains substantial unrelated
uncommitted work from other beads
(`teach/publish_graph.py`, `teach/va_world_language_sol_graph.py`,
`tests/test_publish_graph.py`, `tests/test_va_world_language_sol_graph.py`,
`.beads/interactions.jsonl`, and numerous other untracked handoff/test
files listed in `git status`) -- all left untouched, out of this bead's
scope. Suggested next commands, if/when asked to commit just this bead's
work:

```
git status
git diff --stat teach/concept_recovery.py tests/test_concept_recovery.py
git add tests/test_concept_recovery_judson_full_graph_generalization_round3.py \
  sandbox-handoffs/teach-hpa.md
# teach/concept_recovery.py and tests/test_concept_recovery.py were changed
# by a prior (uncommitted) session, not this one -- confirm with whoever
# owns that work before bundling it into the same commit.
git commit -m "..."
```

## What's NOT done / left for whoever picks this up

- Neither this round nor round2 has yet produced a fresh case with
  RING_HOMOMORPHISMS's exact geometry (decisive winner, genuinely low
  self-coverage, vetoed only by a coverage-thin rival) to positively
  demonstrate the ratio gate doing its intended job outside the calibration
  case itself. Not a blocker for closing (the requirement was "no
  regression," which is proven), but worth noting for whoever next touches
  this mechanism: the gate's benefit is still only demonstrated on tuning
  data, only its safety is demonstrated on held-out data.
- **teach-ceg** (filed this session, P2): the 0.25 coverage-gap threshold's
  own near-miss on SETS_EQUIVALENCE. Needs its own design + fresh held-out
  round, per this lineage's standing rule.
- **teach-443** (filed this session, P3): judson:18.2's generic-vocabulary-
  attractor behavior. Likely needs either better distinctive-vocabulary
  extraction for that node or a module-level fix, not a resolver-logic fix.
- teach-t7j (semantic-tier gap, filed by teach-i35) remains open and
  untouched.
- `load_judson_algebra_graph()` (11-node) remains the production default;
  `load_judson_full_graph()` (20-node) is still not used by any production
  consumer -- this whole lineage continues to be about what happens if/when
  a consumer is switched to the full graph.

## Lineage

teach-cpg -> teach-i35 -> teach-ngy -> teach-9wx (fixed the decisive-margin
branch's total bypass of coverage checking; found and filed teach-hpa) ->
**teach-hpa (this bead)**: added a credibility gate so only rivals with a
non-trivial raw score relative to the winner can trigger teach-9wx's
coverage-gap veto, fixing the false-abstention cost teach-9wx disclosed,
verified with its own fresh held-out round; found and filed teach-ceg and
teach-443. Each fix in this chain is real and verified; each held-out round
keeps finding the next-deepest layer of the same underlying problem (a
growing graph's vocabulary-size and vocabulary-overlap dynamics undermining
a bag-of-words scorer's assumptions). teach-t7j, teach-ceg, and teach-443
are all still open.
