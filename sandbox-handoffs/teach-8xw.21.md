# teach-8xw.21 handoff

## What was wrong

`teach/dnf_bond_integration.py::_self_check()` and
`tests/test_dnf_bond_integration.py::test_potential_checker_coverage_gap_is_disclosed_not_hidden`
both asserted `len(cov.seen) == 32` (and `unclassified == 31`). Before
teach-8xw.19, `seen` was gated to about-learner sentences, so that number
tracked the lesson's *claims*. teach-8xw.19 removed the gate -- `seen` is now
every tutor-spoken sentence in the lesson, domain content and Bond narration
included -- so 32 became a measurement of lesson *prose length*, not of
anything to do with honesty. Any edit to the lesson text (reword a
definition, add a paragraph of Bond narration, split a sentence) would flip
this count and fail both checks with a message about a count, for a change
that has nothing to do with the honesty picture. The cheapest fix available
to a worker hitting that failure is to bump the number to whatever the code
now prints, which is exactly how an assertion stops checking anything.

## What changed

`teach/dnf_bond_integration.py::_self_check()`:
- Dropped `assert len(report.potential_coverage.seen) == 32` and
  `assert len(report.potential_coverage.unclassified) == 31`.
- Replaced with two invariant assertions that are independent of lesson
  length:
  - `len(cov.seen) > 0` -- catches the teach-yn8 vacuous-coverage failure
    mode (an empty coverage set would make "no flags" trivially true and
    worthless).
  - `len(cov.seen) == len(cov.classified) + len(cov.unclassified)` -- the
    actual invariant that matters post-teach-8xw.19: nothing seen silently
    disappears between the two buckets.
- Kept `assert len(cov.classified) == 1` unchanged, per the bead: this
  tracks a claim, not prose volume, and legitimately should break if the
  lesson's one potential-claim sentence stops being recognized.

`tests/test_dnf_bond_integration.py::test_potential_checker_coverage_gap_is_disclosed_not_hidden`:
- Same replacement: `len(cov.seen) > 0`,
  `len(cov.seen) == len(cov.classified) + len(cov.unclassified)`,
  `len(cov.classified) == 1`, `len(cov.unclassified) > 0` (kept as an
  existence check, not a pinned count, since the docstring/rendered-report
  assertion right below it depends on there being at least one unclassified
  sentence to disclose).
- Updated the docstring to explain why the exact count isn't pinned anymore.

Both files already had unrelated uncommitted changes from teach-8xw.19
(`about_learner` -> `seen` rename, comment updates) sitting in the working
tree when I started; I left those alone and only touched the two count
assertions plus their surrounding comments/docstrings.

`teach/potential_checker.py` and `tests/test_potential_checker.py` are also
modified in the working tree (pre-existing, from teach-8xw.19) -- out of
scope for this bead, untouched by this session.

## Verification

1. Ran the self-check as-is (with the fix applied): passes, prints
   "32 seen, 1 classified, 31 unclassified" -- the code path is unchanged,
   only the assertions are.
2. To confirm the fix actually solves the described problem (not just that
   it passes today), I temporarily added a sentence to the first tutor turn
   in `teach/dnf_bond_lesson.py` ("Q has already laid the files on the
   desk."), reran `python -m teach.dnf_bond_integration`: exit 0, report
   now shows "32 tutor-spoken sentence(s) were NOT checked" (33 seen, one
   more than before). Confirmed this would have failed both assertions
   before the fix. Reverted the lesson edit immediately after.
3. Full suite: `uv run pytest -q` -> 180 passed.

## Scope note

This bead's diff is intentionally narrow: two assertions and their
surrounding prose in two files. `classified == 1` was explicitly left as an
exact-count assertion per the bead's instruction, since it tracks a claim
count, not prose volume.
