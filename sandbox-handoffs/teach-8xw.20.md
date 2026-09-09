# teach-8xw.20 handoff

## What was wrong

teach-8xw.19 correctly removed the vocabulary-gated "is this about the
learner" pre-filter from `teach/potential_checker.py` -- three widenings of
it (teach-yn8, teach-kmm, teach-5gf) each left a next round of
independently-phrased praise invisible, and a whitelist has no last round.
But the fix left `Coverage.unclassified` structurally pinned near
`len(seen)`: `unclassified = len(seen) - len(classified)`, and `classified`
is small and roughly constant for any honestly-written lesson (0-2 true
potential-claims). `len(seen)` is now every tutor-spoken sentence, dominated
by ordinary domain content and narration that was never a candidate for a
potential-claim in the first place. Result: every lesson reports "N seen, ~1
classified, ~N-1 unclassified" regardless of what it actually says. On the
real D&F/Bond lesson that's 31 of 32. The number stopped being a signal a
reviewer could act on -- both the 32-sentence lesson A) (mostly ordinary
content) and a hypothetical 32-sentence lesson B) (20 sentences of
pronoun-free flattery `_claim_type` can't type) render identically.

The bead is explicit that the fix must not reintroduce a gate under a new
name -- no sentence may become invisible again -- and that the closing
evidence must be a mechanism argument, not "I wrote some lessons and the
number varied" (that exact same-session-sampling method failed three times
across teach-yn8/teach-kmm/teach-5gf).

## What changed

`teach/potential_checker.py`:

- Added `_SECOND_PERSON_REFERENCE` (`\byou\b|\byour\b|\byours\b`), explicitly
  documented as NOT a candidacy gate -- it is only ever used to compute a
  secondary, reported-alongside-not-instead-of breakdown.
- `Coverage` gained three new fields: `second_person_seen`,
  `second_person_classified`, `second_person_unclassified` -- the same three
  buckets, restricted to sentences containing an explicit second-person
  reference. `check_coverage` computes them in the same pass as the existing
  fields, off the same `_extract_from_sentence` call, so the two views can
  never disagree about what got classified.
- Nothing about `extract_claims` or the primary `seen`/`classified`/
  `unclassified` fields changed -- this is purely an additional, narrower
  view computed alongside the untouched ungated total.

`teach/dnf_bond_integration.py`:

- `IntegrationReport.render()` now prints a secondary line: "of which N
  address the learner directly ('you'/'your'/'yours'): M classified, K
  unclassified", plus the actual list of second-person-unclassified
  sentences when non-empty. The primary "N seen, M classified, K
  unclassified" line is unchanged and printed first -- the secondary line is
  additive, never a replacement.
- `_self_check()` gained invariant assertions: the second-person triple
  sums correctly, and on this real lesson it is a proper, non-empty subset
  of `seen` (there is genuine third-person Bond/domain content that
  contributes nothing to it).
- Closing print statement now also reports the second-person-unclassified
  count.

## Why this satisfies the "mechanism, not sampling" bar

The bead's complaint is that `unclassified` is *structurally* pinned near
`len(seen)` -- a consequence of `classified` staying small, not of anything
about the specific lesson. The fix has to show the new number is NOT the
same kind of near-constant, and it has to show this by construction rather
than by writing lessons in this session and checking the figure moved
(exactly the method that failed three times in this lineage).

`teach/potential_checker.py` now includes (as module constants exercised by
both the `__main__` self-check and `tests/test_potential_checker.py`) two
three-sentence, entirely-unclassified tutor turns:
`_TEACH_8XW_20_THIRD_PERSON_TURN` (ordinary third-person domain exposition,
e.g. "A normal subgroup is one that's invariant under conjugation.") and
`_TEACH_8XW_20_SECOND_PERSON_TURN` (direct-address chit-chat with no
potential-claim shape in it, e.g. "Take a moment and tell me how you're
feeling about this material."). Both have `len(seen) == len(unclassified)
== 3` -- identical on the exact axis the bug is about. Their
`second_person_seen` comes out `0` and `3` respectively. This is a minimal
constructed pair proving the two counts are driven by different textual
properties (sentence count vs. presence of second-person address), not two
views of the same underlying number -- a structural argument, not a sampling
one. `test_second_person_subset_is_structurally_decoupled_from_lesson_length`
in `tests/test_potential_checker.py` pins this down as a regression check.

Separately, `test_dnf_bond_lesson_second_person_subset_is_smaller_than_full_unclassified`
confirms the real lesson this bead was filed against gets a strictly
smaller, more targeted secondary list: 5 second-person-unclassified
sentences instead of the full 31-sentence unclassified list. A reviewer can
now read 5 sentences instead of 31 and still see the disclosure the primary
total already made (nothing is hidden -- both numbers are printed).

## What this does NOT solve (disclosed, not papered over)

- The secondary subset is blind to pronoun-free third-person praise by
  construction -- exactly the category teach-8xw.19's own reproduction
  sentences fall into ("Einstein would have nodded approvingly...",
  "Future textbooks might well cite work that starts exactly like this.").
  Those sentences show `second_person_seen` contribution of zero, same as
  before. This is not a regression: the primary, ungated `seen`/
  `unclassified` totals still catch them (see the existing
  `_TEACH_8XW_19_REGRESSION_SENTENCES` test, unchanged), and the module
  docstring and this handoff both say so explicitly rather than let the new
  field imply broader coverage than it has.
- This does not close the general "coverage number is uninformative on an
  adversarial lesson built entirely of pronoun-free flattery" case -- that
  lesson would still show a small `second_person_unclassified` alongside a
  large primary `unclassified`, and a reviewer has to read both lines, not
  just the smaller one. The bead's own candidate list flagged all three
  options as "none obviously right"; this implements the second candidate
  (second-person subset, reported alongside, never replacing) because it is
  the one that stays gate-free while being provably decoupled from lesson
  length by construction, not because it fully solves the discrimination
  problem for every possible lesson.
- The corpus-level outlier candidate (option 3) was not attempted -- this
  repo currently has exactly one real integration lesson
  (`teach.dnf_bond_lesson`) plus hand-written test fixtures, not a body of
  independently-produced lessons to compute an outlier baseline against.
  That would need real infrastructure (a corpus, a baseline-fitting
  procedure) this bead's scope doesn't cover; noting it here in case a
  future bead wants to revisit it once more real lessons exist.

## Verification

1. `uv run python3 -m teach.potential_checker` -- self-check passes,
   including the new structural-decoupling assertions (0/3 vs 3/3
   second-person sentences on two equal-length, equally-unclassified
   fixture turns).
2. `uv run python -m teach.dnf_bond_integration` -- end-to-end run passes;
   report now shows both "32 seen, 1 classified, 31 unclassified" AND "of
   which 6 address the learner directly: 1 classified, 5 unclassified",
   with the 5 actual second-person-unclassified sentences listed.
3. `uv run pytest -q` -> **185 passed** (was 180 before this bead; 5 new
   tests added: subset invariant, third-person-exclusion, `yours`-possessive
   coverage for the new regex, the structural-decoupling proof, and the
   real-lesson smaller-subset check).
4. No other module constructs `Coverage` directly or reads its fields
   (`grep -rn "Coverage("` and a repo-wide search for `potential_checker`/
   `check_coverage` consumers) -- `teach/dnf_bond_integration.py` is the
   only caller outside the module's own tests, and it's updated above.

## Scope note

Diff is confined to `teach/potential_checker.py` (new regex, three new
`Coverage` fields, `check_coverage` computing them, module-level fixture
constants + self-check assertions), `teach/dnf_bond_integration.py` (render
+ self-check + closing print), and both test files. `extract_claims`,
`check_lesson_text`, and every existing field/behavior are untouched --
confirmed by the full pre-existing test suite passing unchanged.
