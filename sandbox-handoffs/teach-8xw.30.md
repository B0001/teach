# teach-8xw.30 — honesty_rubric: runtime validation for PotentialClaim

## What was wrong

`teach/honesty_rubric.py`'s decision table itself was correct (proven by
`WORKED_EXAMPLES` and the exhaustive-sweep claim in the bead), but the
module's stated guarantee — "TRAIT is a hard rule, not a default" — only
held by caller convention. `PotentialClaim` was a frozen dataclass with type
hints (`claim_type: ClaimType`, `evidenced_ceiling: bool | None`) and no
`__post_init__`, and `classify()` tests `claim_type is ClaimType.TRAIT` by
identity and `evidenced_ceiling` by `is None` / plain truthiness. Anything
that merely looked right — the string `"trait"` instead of the enum member,
a truthy string or falsy int instead of a real bool — silently defeated the
hard rule instead of erroring.

## What was built

Added `PotentialClaim.__post_init__` (same pattern as
`teach/persona.py`'s `Ocean.__post_init__` — the repo's established
"raise loud rather than guess" convention for dataclass invariants):

- `claim_type` must be `isinstance(..., ClaimType)` — rejects the
  string-that-looks-like-an-enum-value case from the bead's first repro.
- `evidenced_ceiling` must be `None` or `isinstance(..., bool)` — rejects
  both the truthy-non-bool (`"no"`) and falsy-non-bool (`0`) cases from the
  bead's second repro. `isinstance(x, bool)` correctly excludes plain ints
  (`isinstance(0, bool)` is `False` in Python even though `bool` subclasses
  `int`), so this doesn't accidentally accept `0`/`1` as `False`/`True`.
- Also validated `conditioned_on_effort` the same way (`isinstance(...,
  bool)`). This wasn't in the bead's explicit "what would close this" list,
  but it's the identical root cause on the same dataclass — `classify`'s
  rule 2 tests it by truthiness too, and it's typed as a plain `bool` with
  no `__post_init__` enforcement, so leaving it out would have left one
  more instance of the exact gap this bead exists to close. Judgment call,
  not scope creep into a different module or a different guarantee.

All three raise `TypeError` (matching `teach/persona.py`'s style of raising
close to the point of construction; `ValueError` would also fit the repo's
convention — `TypeError` was chosen because these are all "wrong kind of
value" contract violations on typed fields, not "right type, bad value"
cases like `persona.py`'s trait-range check).

Five new regression tests in `tests/test_honesty_rubric.py`, one per case:
malformed `claim_type` (string `"trait"`), truthy-non-bool
`evidenced_ceiling` (`"no"`), falsy-non-bool `evidenced_ceiling` (`0`), and
non-bool `conditioned_on_effort` (`"yes"`) — each asserts `pytest.raises
(TypeError)`.

## Verification

```
uv run pytest tests/test_honesty_rubric.py -v    # 13 passed (was 9; +4 new)
uv run pytest                                     # 240 passed, full suite, no regressions
uv run python3 teach/honesty_rubric.py            # OK: 6 worked examples all classify as expected
```

Also re-ran the bead's exact repro snippets directly (not through pytest) to
confirm the reported `Verdict.HONEST` / `Verdict.INFLATED` misclassifications
are gone and replaced with a raised `TypeError`:

```
$ uv run python3 -c "... claim_type='trait' ..."
OK raised: claim_type must be a ClaimType member, got 'trait'

$ uv run python3 -c "... evidenced_ceiling='no' ..."
OK raised: evidenced_ceiling must be a bool or None, got 'no'

$ uv run python3 -c "... evidenced_ceiling=0 ..."
OK raised: evidenced_ceiling must be a bool or None, got 0
```

`tests/test_potential_checker.py` (the only real constructor of
`PotentialClaim` on main today, per the bead's "not currently exploitable"
note) passes unchanged — confirms the new validation doesn't reject
anything the live pipeline actually produces.

## Scope note

This bead was explicitly about closing the *runtime enforcement* gap, not
re-auditing the decision table (already proven correct and out of scope
here) or building the extractor (`teach-8xw.13`, already done). Nothing
else in the module changed.

## Files touched

- `teach/honesty_rubric.py` — added `PotentialClaim.__post_init__`
- `tests/test_honesty_rubric.py` — added 5 regression tests + updated
  module docstring to note why they exist

Nothing committed — conservative git policy, not asked to commit.

## Follow-up filed

None. This closes the gap the bead identified; no new scope was discovered.
