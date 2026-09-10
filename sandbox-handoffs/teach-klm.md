# teach-klm — concept_recovery: case_identifier_uuid leaks hex-fragment noise words into node vocabulary

## What was wrong

`teach/va_math_sol_graph.py` stores a bookkeeping `case_identifier_uuid`
field (a raw UUID4 string) in every node's `facts`. `_flatten_strings` in
`teach/concept_recovery.py` recursively harvests every string reachable in
`facts` by design (concept_graph.py's opacity rule, teach-8xw.10/teach-8xw.4
— the module must not know a domain's key names), and `_words`'s regex
`[a-z]+` pulled hex-letter runs out of those UUIDs as if they were real
words: `5184644f-d652-4ed4-8bdc-6ededf2a6965` → `ededf`,
`43064722-68cf-4828-baca-b35714aa2275` → `baca`. Both sat in the same
vocabulary set as real distinctive words like `quadrilaterals` and
`perimeter`. Every node in `va_math_sol_graph.py` has one of these, so it was
systemic. `va-math-sol:3.PS`'s real distinctive vocabulary is tiny after
document-frequency filtering (just `pictographs`), so the UUID fragment
(`baca`) was proportionally significant noise for that node specifically —
this is what teach-8xw.26's generalization measurement noticed as a side
effect.

## What was built

Since `_flatten_strings` can't be taught the key name `case_identifier_uuid`
without breaking the opacity rule (a reading or foreign-language domain's
graph would still need the same protection, without concept_recovery.py
knowing anything about their fields either), the fix is shape-based, not
name-based, and lives at `_words` — the single shared tokenization point
already used for both node vocabulary (`_node_vocabulary`) and lesson text
(every call site in `recover_taught_concept`,
`recover_assumed_prerequisites`, `recover_unsignposted_prerequisites`):

```python
_UUID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)

def _words(text: str) -> set[str]:
    text = _UUID.sub(" ", text)
    return {w for w in _WORD.findall(text.lower()) if len(w) >= 4 and w not in _STOPWORDS}
```

The regex matches a UUID-shaped substring anywhere in a string (not just a
whole-string match), so a future domain that embeds an id inside a longer
sentence rather than as its own dict value is still covered, and it's
applied uniformly to lesson text too (harmless there — lesson text is not
expected to contain UUIDs, and if it somehow did, stripping it is still
correct).

Considered and rejected: filtering by key name in `va_math_sol_graph.py`'s
node-construction code, or a `_flatten_strings` special case for that key —
both would leak domain-specific knowledge into either the graph-agnostic
`concept_recovery.py` or would require the loader to know which fields are
"safe," neither of which is the actual invariant (bookkeeping fields aren't
defined by their key name, they're defined by not being natural-language
prose, and a UUID is the shape that's actually opaque).

## Evidence

Bead's own reproduction, re-run after the fix:

```
uv run python3 -c "
from teach.concept_recovery import _node_vocabulary
from teach.va_math_sol_graph import load_va_math_sol_graph
g = load_va_math_sol_graph()
nodes = {n.id: n for n in g.nodes}
n = nodes['va-math-sol:4.MG']
print(n.facts['case_identifier_uuid'])
print(sorted(_node_vocabulary(n)))
"
```
→ `ededf` no longer appears; `quadrilaterals`, `perimeter`, etc. unaffected.
Same check against `va-math-sol:3.PS` confirms `baca` is gone too.

Swept every node in both real graphs (`va_math_sol_graph.py` and
`dummit_foote_graph.py`) for any remaining hex-looking leftover token
(`^[0-9a-f]{3,}$` with at least one a-f letter, not a real word) — zero
found. `dummit_foote_graph.py`'s facts have no UUID or similar bookkeeping
field (checked directly, not inferred) — the bead's "check whether
dummit_foote_graph.py has any similar field" is answered: no, this fix is
currently only load-bearing for `va_math_sol_graph.py`, but is generic
enough to cover a future one without changes.

New regression test,
`tests/test_concept_recovery.py::test_uuid_bookkeeping_field_does_not_leak_hex_fragments_into_vocabulary`:
a synthetic node with a UUID field alongside real content (proves the fix
doesn't over-strip — `perimeter`/`quadrilaterals` still recovered) plus the
bead's exact two real-graph nodes (`va-math-sol:4.MG`, `va-math-sol:3.PS`)
asserted directly against `_node_vocabulary`.

```
uv run pytest -q                    # 247 passed (was 246; +1 new test)
uv run pytest tests/test_concept_recovery.py -q   # 24 passed
uv run python3 -m teach.concept_recovery          # OK, same abstain/recover pair as before
```

## Files touched

- `teach/concept_recovery.py` — added `_UUID` pattern (with rationale
  comment) and one line in `_words` to strip UUID-shaped substrings before
  tokenizing.
- `tests/test_concept_recovery.py` — one new test, one new import
  (`_node_vocabulary`, module-private but imported directly because the bug
  is specifically about vocabulary extraction, one level below the public
  `recover_from_lesson_text` entry point — asserting on the public API alone
  wouldn't pin down which specific words got excluded).

Nothing committed — conservative git policy, not asked to commit. The
working tree already had substantial uncommitted changes from other, unrelated
bead sessions (`teach/honesty_rubric.py`, `teach/math_facts.py`,
`teach/potential_checker.py`, `teach/cialdini.py` and others) present before
this session started; none of those were touched, and `git diff` on this
bead's two files only (`git diff -- teach/concept_recovery.py
tests/test_concept_recovery.py`) confirms the change is scoped to the
`_UUID`/`_words` addition and the one new test.

## Follow-up

None filed. The bead's "check whether dummit_foote_graph.py has any similar
non-content bookkeeping field" is answered above (no).
