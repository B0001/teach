# teach-cpg handoff

## What this bead was

teach-8xw.53's held-out round 2 found a genuine confident-wrong-answer
failure in `teach/concept_recovery.py`'s `_resolve_candidates`:
GRADE6_SIGNPOSTED recovered taught=7.W instead of the intended 6.W. Root
cause: the single-winner branch (teach-l7u's fix) only checked the
winner's own coverage against a fixed floor, never against the coverage
of the rival that put it in the "close" group. teach-cpg asked for a fix
to that branch, but explicitly required its own **fourth**
independently-authored held-out round before it could be closed. Per
sandbox-prompt.md, "you cannot hold out examples from yourself."

A prior session (see the git history of this file, or
`.beads/interactions.jsonl`) ran that fourth round
(`tests/test_concept_recovery_writing_domain_generalization_round3.py`)
and found 1/6 confident wrong answers (GRADE6_UNSIGNPOSTED_GARDENING:
taught=7.W instead of 6.W), root-caused it precisely, and filed
**teach-i35** (discovered-from teach-cpg) rather than fix it in the same
session that measured it. That session left teach-cpg's own explicit
closing bar as: *"stay open until teach-i35 (or an equivalent broader fix
to the rival-selection logic) is addressed and a FIFTH fresh held-out
round shows 0 confident wrong answers -- or until someone judges the
residual teach-i35 gap acceptable and closes this with an explicit
`--reason`."*

## What I found on arrival

teach-cpg was already `in_progress`. I claimed it and read the prior
session's handoff (this file, before I overwrote it) plus teach-i35's and
teach-t7j's own bead descriptions/notes to reconstruct the lineage:

- **teach-i35**'s fix was already present, uncommitted, in
  `teach/concept_recovery.py`: the single-winner branch's rival search no
  longer hardcodes `candidates[1]` as "the rival" -- it now searches every
  candidate clearing `_MIN_MATCH_WORDS` for whichever has the best
  coverage fraction, regardless of raw-score rank. Verified against
  `tests/test_concept_recovery.py::test_resolve_candidates_checks_every_candidates_coverage_not_just_the_runner_up`
  (present, passing).
- **teach-t7j**'s fix was also already present, uncommitted:
  `_coverage_fraction` now computes coverage from literal exact-word
  overlap against the raw lesson text (`node_words & text_words`), not
  `match.score / len(node_words)` -- decoupling coverage from
  tier-specific WordNet synonym-credit inflation, which teach-t7j found
  was inflating the *false winner's own* coverage, not just rivals'.
  Confirmed via
  `grep -n "COVERAGE IS MEASURED ON EXACT WORDS ONLY" teach/concept_recovery.py`.
- Two further, later-lineage fixes were also present and passing their own
  tests, unrelated to teach-cpg/teach-i35/teach-t7j directly but part of
  the same `_resolve_candidates` function: teach-ngy's multi-candidate-tie
  rewrite (picks `best_covered` among all `close` candidates, not
  necessarily `top`) and teach-9wx/teach-hpa's decisive-margin credible-rival
  check. I did not audit these in depth -- they are other beads' scope --
  only confirmed they don't conflict with anything teach-cpg needs.
- `git status` showed a large amount of unrelated pre-existing uncommitted
  work (a Dummit & Foote -> Judson's Abstract Algebra rename in progress,
  deleted `dnf_bond_*` files, changes to `.beads/interactions.jsonl`,
  several other sandbox-handoffs and test files from the teach-i35/teach-t7j/
  teach-ngy/teach-9wx lineage). I left all of it untouched -- none of it is
  this bead's scope.
- Diagnostically (not as closing evidence -- both are tuning data for the
  fixes that produced them), I re-ran round 2's `GRADE6_SIGNPOSTED` and
  round 3's `GRADE6_UNSIGNPOSTED_GARDENING` through the current code: both
  now **safely abstain**, citing the true rival (6.W) as more proportionally
  covered than the false winner (7.W) that used to win confidently. This
  confirmed the fixes address their own motivating cases, but per this
  lineage's own repeated rule, this is not validation -- it is exactly the
  data that produced the fixes.

## What I did

1. Confirmed the full suite passed before generating any new text
   (`uv run pytest -q` -- 554 passed, 16 skipped, 1 xfailed; the 1 xfail is
   round 3's own strict-xfail pinning test, correctly xfailing now that the
   bug it pins is gone at the code level).
2. Sourced raw VDOE grade-level writing standard descriptions directly from
   `teach/data/va_writing_sol_k12.json` (grades 3-7) -- never from
   `concept_recovery.py`, any fix, or any test file.
3. Launched 6 parallel `Agent` calls, each explicitly told not to use any
   tools and given zero information about this repository, the module, its
   thresholds, or any bead history -- only the raw standard text and a
   student-interest framing, with an instruction to write a natural
   tutor/student dialogue. Scenarios chosen specifically to (a) cover fresh
   grade territory rounds 1-4 hadn't touched (grades 3, 4), (b) directly
   re-probe the historically fragile 6/7 boundary with an entirely new
   topic and phrasing (baking, grade 6, WITH a signposted callback to grade
   5 -- the exact zone that produced both teach-cpg's and teach-i35's
   confident-wrong-answer bugs), (c) add a fresh signposted-callback probe
   one grade band lower (grade 5, callback to grade 4) to check the fix
   isn't a fluke specific to the 6/7 boundary, (d) a fresh grade-7
   no-signpost case, and (e) an off-domain history control (the Space Race,
   Sputnik through Apollo 11).
4. Measured all 6, once, against the real, unmodified
   `teach.va_writing_sol_graph` via `recover_from_lesson_text` -- the
   public entry point only. No threshold was changed in response to seeing
   the results.
5. Committed the full 6-text set, verbatim, with per-case docstrings and
   assertions matching the actually-measured outcome, in
   `tests/test_concept_recovery_writing_domain_generalization_round5.py`.
6. Ran the full suite again: `uv run pytest -q` -> **560 passed, 16
   skipped, 1 xfailed** (554 baseline + 6 new round5 tests).

## Honest result

6 held-out texts, measured once, thresholds untouched afterward:

| correct recoveries | safe abstentions | CONFIDENT WRONG ANSWERS |
|---|---|---|
| 4 / 6 | 2 / 6 | **0 / 6** |

- **DINOSAUR** (intended taught=3.W, no signposting): **safe abstention**.
  Top three candidates (2.W score=6, 3.W score=6, 4.W score=5) are within
  one point of each other; the checker correctly declines rather than
  guessing among close grade-2/3/4 neighbors.
- **BASKETBALL** (intended taught=4.W, no signposting): **correct**,
  taught=4.W exactly.
- **MUSIC_CALLBACK** (intended taught=5.W, signposted callback to grade 4):
  **correct**, taught=5.W exactly, AND `assumed_prerequisite_ids ==
  ("va-writing-sol:4.W",)` exactly -- the signposted callback was correctly
  recovered too.
- **BAKING_CALLBACK** (intended taught=6.W, signposted callback to grade
  5) -- **the load-bearing result**: this text was built specifically to
  re-probe the exact 6/7 confusability zone that produced both
  GRADE6_SIGNPOSTED (teach-cpg's own bug) and GRADE6_UNSIGNPOSTED_GARDENING
  (teach-i35's bug), using an entirely new topic (baking shows) and
  phrasing. It **correctly recovers taught=6.W** (not the historically
  attractive wrong neighbor 7.W) **and** `assumed_prerequisite_ids ==
  ("va-writing-sol:5.W",)` exactly.
- **VIDEOGAME** (intended taught=7.W, no signposting): **correct**,
  taught=7.W exactly.
- **SPACE_RACE_HISTORY** (off-domain control, no writing-domain
  vocabulary): **safe abstention** (true negative). Candidate scores are
  far lower than any on-domain text in this round and tie across eight of
  the graph's twelve grade nodes.

This round does not have the gap round 4 had. Round 4 (teach-i35's own
closing round) measured 0/6 confident wrong but, by its own admission, did
not happen to produce a case in the specific failure geometry that
motivated teach-i35's fix, so it could not show the fix flipping a wrong
answer to a right one. This round's BAKING_CALLBACK and MUSIC_CALLBACK
were deliberately built to land in that geometry (signposted callback +
6/7-adjacent content), and both resolve correctly, with correctly-recovered
prerequisites.

This is not a claim that `concept_recovery.py` is bug-free in general --
only that, on this fresh round, the specific failure mode this bead's
lineage tracked (a confident wrong answer at the 6/7 grade boundary, driven
by WordNet semantic-tier coverage inflation misdirecting the rival search)
did not reproduce, at the boundary itself, with a genuinely fresh topic.

## What was NOT done (on purpose)

- Did not touch `_resolve_candidates`, `_coverage_fraction`, or any
  threshold in response to this round's results -- that would make this
  round tuning data too, exactly the mistake this lineage exists to avoid.
- Did not audit or attempt to close teach-i35 or teach-t7j themselves in
  this session -- both are separate beads with their own closing bars
  (teach-i35 wants a round exercising its specific failure geometry;
  teach-t7j wants a round probing the own-coverage-inflation gap
  specifically). This round's BAKING_CALLBACK/MUSIC_CALLBACK results are
  relevant evidence for both, but deciding their disposition is outside
  teach-cpg's scope -- left for whoever picks those up next, noted here so
  the evidence isn't lost.
- Did not audit teach-ngy's or teach-9wx's/teach-hpa's mechanisms in depth
  -- present in the working tree, passing their own tests, not this bead's
  concern.
- Did not touch the unrelated concurrent working-tree changes (the Judson
  Abstract Algebra rename, deleted `dnf_bond_*` files, etc.) -- none of
  that is this bead's scope and none of it was made by this session.
- Did not commit or push anything, per the repo's conservative git policy.
  A substantial amount of uncommitted work now sits in the tree across
  several beads' worth of fixes (teach-i35, teach-t7j, teach-ngy, teach-9wx,
  teach-hpa, and now this round's teach-cpg closing evidence) -- committing
  it is a decision for whoever is asked to, not implied by closing this
  bead.

## Verification

- `uv run pytest -q` -- **560 passed, 16 skipped, 1 xfailed** (the xfail is
  round 3's own strict pinning test, expected: it asserts the old buggy
  outcome and correctly fails to reproduce it).
- `git status` shows, relevant to this bead: `teach/concept_recovery.py`
  and `tests/test_concept_recovery.py` modified (pre-existing, from the
  teach-i35/teach-t7j/teach-ngy/teach-9wx/teach-hpa lineage, left as
  found), plus one new file added by this session,
  `tests/test_concept_recovery_writing_domain_generalization_round5.py`.

## Bead disposition

**Closing teach-cpg.** Its own explicit closing bar --
*"teach-i35 (or an equivalent broader fix to the rival-selection logic) is
addressed and a FIFTH fresh held-out round shows 0 confident wrong
answers"* -- is met: teach-i35's mechanism fix and teach-t7j's coverage
fix are both present and unit-verified, and this fresh, independently-
authored, blind round 5 -- deliberately re-probing the exact 6/7 boundary
that produced this bead's own bug -- measured 0/6 confident wrong answers,
including a direct correct recovery (not merely a non-regression) at that
boundary with a brand-new topic. teach-i35 and teach-t7j remain open as
their own beads with narrower, distinct closing bars; this round's results
are noted in their sections above as relevant evidence but are not this
bead's call to act on.
