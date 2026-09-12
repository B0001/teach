# teach-8xw.51 — fix the two real "you just did X" fabrications teach-8xw.45 caught

## What was wrong (recap)

teach-8xw.45 gave `teach/potential_checker.py`'s `evidenced_ceiling` a real,
narrow cross-reference: a tutor turn claiming "you just carried/solved/
handled/..." something is only evidenced if THIS SAME transcript's own turn
order shows a learner turn immediately before it. Run against this repo's
two real (non-fixture) producers, it found two genuine instances of the
fabricated-performance pattern:

1. `teach/dnf_bond_lesson.py`'s closing line — "You just carried that coset
   argument through to Lagrange's Theorem on your own" — followed eight
   consecutive tutor-only turns with zero learner contribution about cosets
   or Lagrange anywhere in them.
2. `teach/cialdini_integration_check.py`'s `build_demo_lesson()` — every
   Cialdini principle rendered back-to-back as tutor turns, with the single
   learner turn appended only at the very end, so
   `render_commitment_consistency`'s "the same kind of move you just handled
   a moment ago" had no learner turn anywhere near it.

teach-8xw.45 deliberately did not fix these — it pinned them as known,
unfixed fabrications (`len(flags) == 1` in both integration self-checks and
the corresponding tests) and filed this bead to fix the producers.

## What this bead did: fixed both producers, not the checker

Per the bead's explicit instruction, the checker signal was not touched.
Both producers were fixed so the claim is actually earned:

### 1. `teach/dnf_bond_lesson.py`

Inserted a real learner turn immediately before the closing line, giving
the learner an actual chance to carry the coset-counting argument through
before being credited for it:

- New tutor turn: asks what the equal-size, non-overlapping coset blocks
  force about how Q Branch's roster size relates to headquarters' size.
- New learner turn: "If the blocks are all the same size and together they
  cover everyone with no overlap, then headquarters' count has to be some
  whole number of those blocks -- so Q Branch's size has to divide
  headquarters' size." (domain-correct: this is exactly Lagrange's theorem's
  counting argument, in the learner's own words, matching the answer key's
  `"the order of a finite group's subgroup divides the order of the
  group"`.)
- The closing "You just carried..." tutor turn now immediately follows this
  learner turn, no other tutor turn in between.

Lesson grew from 21 to 23 turns. `_self_check()` in
`teach/dnf_bond_lesson.py` still passes (it doesn't assert turn count).

### 2. `teach/cialdini_integration_check.py`

`build_demo_lesson()` now inserts a learner turn — quoting
`_DEMO_MOMENT.prior_commitment` back verbatim, the same pattern
`teach.dnf_bond_lesson.build_lesson` already used correctly for its own
commitment_consistency turn — immediately before the
`COMMITMENT_CONSISTENCY` move's rendered turn, instead of only appending one
learner turn at the very end after all seven principles. `render_
commitment_consistency`'s template (`teach/cialdini.py`) was NOT touched —
the fix is in how the demo lesson assembles its turns, per the bead's
"and/or" acceptance criterion.

## Downstream assertions updated to describe the corrected, honest behavior

Per the bead's explicit instruction ("update their assertions to match the
corrected... behavior... once the producers themselves stop making the
unevidenced claim") — not a reversion, an update to reflect the new,
verified-clean measurement:

- `teach/dnf_bond_integration.py::_self_check` — `potential_flags` pinned at
  1 (with an "isomorphism theorems next" claim-text check) reverted to the
  original `== ()` shape, since that flag is now genuinely gone, not
  suppressed. `classified == 2` count unchanged (both claims still land, now
  both HONEST). Comments/print rewritten to state history without pinning a
  now-fixed number in prose.
- `teach/cialdini_integration_check.py::_self_check` — `lesson_flags`
  assertion reverted to `== ()`. Comments/print updated the same way. The
  `teach-8xw.44` blind-round block (unrelated to this bead) was left
  untouched.
- `tests/test_dnf_bond_integration.py::test_checker_flags_no_dishonest_potential_claims`
  (renamed back from `test_checker_flags_the_one_unevidenced_closing_claim`)
  — asserts `potential_flags == ()` again.
- `tests/test_cialdini_integration_check.py::test_demo_lesson_passes_the_real_honesty_checker_clean`
  (renamed back from `test_demo_lesson_flags_the_one_context_free_commitment_claim`)
  — asserts `lesson_flags == ()` again.
- `tests/test_cialdini_integration_check.py::test_honesty_rubric_verdicts_reachable_from_generated_text`
  — reverted to checking `build_demo_lesson()`'s own claims land HONEST
  (the teach-8xw.45-era version had to route around the demo's own bug by
  checking `teach.dnf_bond_lesson.build_lesson` instead; that workaround is
  no longer needed since the demo lesson is fixed). Removed the
  now-unused `ClaimType` import this left behind.
- `test_every_principle_individually_passes_the_real_checker_clean_except_commitment_consistency`
  was left unchanged — it checks `COMMITMENT_CONSISTENCY` rendered as a
  single isolated tutor turn with no surrounding transcript at all
  (`run_check()`'s `per_principle_flags`), which is a structurally
  different, unfixable case (a one-turn transcript can never have a
  preceding learner turn by construction) — not the `build_demo_lesson`
  bug this bead targets. That test's own docstring already states this
  correctly; nothing here needed to change.

## What this does NOT claim

- This does not touch or weaken `teach-8xw.45`'s checker signal in any way
  — `teach/potential_checker.py` is unmodified by this bead.
- This does not claim `evidenced_ceiling`'s turn-adjacency check is a
  general fabrication detector. It remains exactly what teach-8xw.45's
  docstring says: a narrow structural check that a learner turn exists
  adjacent to the claim, not that its content matches. Both fixes here
  happen to also make the content genuinely match (the learner really did
  articulate the argument / really did state the prior commitment), but
  that is because these are real fixes, not just checker-satisfying ones —
  it is not something a future producer bug of this shape would be
  guaranteed to get right by construction.
- `test_every_principle_individually_passes_the_real_checker_clean_except_commitment_consistency`
  is intentionally still not "clean" — checking a context-dependent move
  completely out of its transcript context cannot honestly certify it, and
  that is not this bead's gap to close.

## Verification

- `PYTHONPATH=/workspace uv run python3 teach/dnf_bond_lesson.py` — self-check
  passes, 23-turn lesson.
- `PYTHONPATH=/workspace uv run python3 teach/dnf_bond_integration.py` —
  self-check passes, 0 potential flags, 2 classified claims both HONEST.
- `PYTHONPATH=/workspace uv run python3 teach/cialdini_integration_check.py`
  — self-check passes, 0 lesson flags; teach-8xw.44 blind-round block
  (unrelated) still measures the same 3/25.
- `uv run pytest -q` — **354 passed** (same count as before this bead; no
  tests added or removed, four existing tests' assertions/names corrected
  to describe the fixed, honest behavior).

## Files touched

- `teach/dnf_bond_lesson.py` (producer fix)
- `teach/cialdini_integration_check.py` (producer fix + self-check assertion
  update)
- `teach/dnf_bond_integration.py` (self-check assertion update)
- `tests/test_dnf_bond_integration.py` (assertion update)
- `tests/test_cialdini_integration_check.py` (assertion update)

Not committed, per this repo's conservative git policy — left for the user
to review and commit.
