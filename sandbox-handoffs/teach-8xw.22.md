# teach-8xw.22: unclassified disclosure was an unreadable one-line tuple repr

## What was wrong

`IntegrationReport.render()` in `teach/dnf_bond_integration.py` interpolated
`cov.unclassified` (a tuple of sentence strings) directly into an f-string,
so the entire disclosure — the block that licenses the report's "no
overpromises" line — rendered as a single Python `repr()` line. At the
current sentence count (31, post teach-8xw.19's removal of the vocabulary
pre-filter) this was thousands of characters wide with repr-escaped quotes,
i.e. unreadable by any human reviewer.

## What I found in the working tree

teach-8xw.19, .20, and .21 had already landed (uncommitted, in the working
tree) before I started. Their diffs to `dnf_bond_integration.py` introduced
a **second** instance of the exact same bug: teach-8xw.20 added a
`second_person_unclassified` breakdown line (`lines.append(f"second-person
unclassified: {cov.second_person_unclassified}")`) with the identical
tuple-repr-on-one-line defect. Since this is the same disclosure pattern in
the same render() method, immediately adjacent to the line the bead names, I
fixed both rather than leaving one readable and one not — fixing only the
bead's literal quoted line would have left the report inconsistent within
itself.

## Fix

Both blocks now do:

```python
lines.append("<header text>:")
lines.extend(f"  - {s}" for s in <tuple>)
```

instead of interpolating the tuple. Applied to:
- `cov.unclassified` block (teach/dnf_bond_integration.py, ~line 105)
- `cov.second_person_unclassified` block (~line 123)

No behavior change: `Coverage` fields, `IntegrationReport` fields, and all
assertions are untouched. Only the string returned by `.render()` changed
shape (newlines instead of a tuple repr).

## Verification

- `uv run python -m teach.dnf_bond_integration` — read the output directly:
  the 31-sentence unclassified block and the 5-sentence second-person block
  now print one sentence per line, indented with `  - `, plain text (no
  repr quote-escaping), instead of a single wrapped line.
- `uv run pytest -q` — 185 passed (no assertions reference rendered text,
  per the bead's own note, so this suite doesn't independently prove the
  rendering fix, only that nothing broke).
- `uv run python -m teach.potential_checker` — self-check still passes,
  unrelated to this change but confirms nothing else regressed.

## Scope notes

- Left `out_of_scope_facts` (line 93, `fact_checker` section) untouched —
  it's a 1-element tuple in the current fixture and not what this bug
  report is about (the bead's title and body are specifically about the
  potential_checker "unclassified" disclosure). If it grows, it would need
  the same fix, but that's speculative and out of scope here.
- teach-8xw.20's question ("should all 31 be printed, or a ranked subset?")
  is untouched — this bead was explicitly compatible with either resolution
  order and I did not attempt to reduce the count, only to make whatever
  count is printed readable.
- I did not commit. Per repo policy (conservative git, only commit when
  asked) and this bead's instructions, the fix is left in the working tree
  alongside the already-uncommitted teach-8xw.19/.20/.21 work.
