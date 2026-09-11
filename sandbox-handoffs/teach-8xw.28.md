# teach-8xw.28 — concept_recovery: opaque UUID identifiers leak into extracted vocabulary

## Outcome: duplicate, already fixed

This bead describes the exact same defect as `teach-klm` (also filed against
`teach/concept_recovery.py`'s `_flatten_strings`/`_node_vocabulary`, same
root cause: `va_math_sol_graph.py`'s `case_identifier_uuid` field, a raw
UUID4 string, has its hex-letter runs pulled out by the word regex and
counted as vocabulary). `teach-klm` was closed in the immediately preceding
commit (`3d5ca5d`, "Cialdini layer, reading-SOL graph, non-math recovery
evidence (9 beads)"), which landed the fix before this session started.

Full detail of the fix (root cause, design rationale, evidence, files
touched) is in `sandbox-handoffs/teach-klm.md` — not duplicated here.

## Verification performed this session

Did not trust the prior close message — re-ran the fix against this bead's
own reproduction and re-read the diff:

```
uv run python3 -c "
from teach.concept_recovery import _node_vocabulary, build_vocabulary_index
from teach.va_math_sol_graph import load_va_math_sol_graph
g = load_va_math_sol_graph()
nodes = {n.id: n for n in g.nodes}
n = nodes['va-math-sol:4.MG']
words = _node_vocabulary(n)
print('UUID field:', n.facts.get('case_identifier_uuid'))
print('suspicious:', [w for w in words if 'ded' in w or len(w) > 15])
"
```
→ `UUID field: 5184644f-d652-4ed4-8bdc-6ededf2a6965`, `suspicious: []`. The
hex fragment `ededf` this bead's reproduction predicted does not appear.

- `teach/concept_recovery.py` (lines 169–181, `_words` at line 262) has the
  `_UUID` regex and strip-before-tokenize logic teach-klm added. It filters
  by **string shape** (a UUID4 pattern), not by the field name
  `case_identifier_uuid` — satisfies this bead's explicit requirement that
  the fix stay generic and not keyed to the literal key name.
- `tests/test_concept_recovery.py::test_uuid_bookkeeping_field_does_not_leak_hex_fragments_into_vocabulary`
  exists and asserts, directly: `"ededf" not in vocab` and `"baca" not in
  vocab` (the second real node this bead's own text doesn't mention but
  teach-klm's reproduction found independently), plus a positive check that
  real content words (`perimeter`, `quadrilaterals`) survive the strip —
  guards against over-stripping, not just under-stripping.
- `uv run pytest -q` → 262 passed (whole suite, not just this file).

No code changes made this session — there was nothing left to do. Filing a
new fix here would have been redundant with, and riskier than, the existing
one (two competing UUID-strip implementations is worse than one).

## Recommendation

Close as duplicate of `teach-klm`. No follow-up bead needed — teach-klm's
own handoff already answers this bead's "check whether
`dummit_foote_graph.py` has a similar field" question (no).
