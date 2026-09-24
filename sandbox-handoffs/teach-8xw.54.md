# teach-8xw.54 -- wire upstream provenance into the published manifest

## What the bead asked for

`manifest.json`'s `source` block carried `provider`/`author`/`license`/
`attribution`/`retrieved_via` but no retrieval date and no content hash. The
only version anchor was the string `"v1.13.0"` in a CDN path -- verified
mutable (an unauthenticated HEAD on the CDN returns 200 from S3, nothing
pins the bytes behind that path) -- so a published graph could not say which
upstream bytes it was actually built from. The bead asked to add, at build
time, `retrieved_at`/`sha256`/`content_length`/upstream `last-modified` to
the source block for each upstream export actually read, with two hard
constraints: (1) never hash a fresh download and present it as the
provenance of the four extracts already committed to `teach/data/` -- their
original downloads are gone (teach-8xw.2), so record their upstream state as
honestly unknown; (2) `publish()` must not silently omit the field when
absent -- it must read `"unrecorded"`, not just not be there.

## Starting state: half-done and committed

A previous session (`eb81cd8`, "Record what upstream bytes an extract came
from (teach-8xw.54, partial)") had already built
`teach/upstream_provenance.py` and `teach/data/upstream_provenance.json`:
`load_record()`, `verify_local()` (offline hash check against the
`~/.cache/teach-upstream/` cache, outside the repo by design), `check_upstream()`
(network HEAD against the CDN, reports "nothing detected" not "verified" --
a HEAD match isn't proof of identical bytes), and `upstream_state_for(name)`,
which returns the literal string `"unrecorded"` for the four pre-record
extracts (`UNRECORDED_EXTRACTS`) and the full record dict for anything else.
Its own docstring said explicitly: *"Partial: wiring this into publish() so
the published manifest carries it is the rest of teach-8xw.54."* That
wiring -- and only that -- is what this session did. Nothing in
`upstream_provenance.py` was changed.

## What was built

`teach/publish_graph.py`:

- `_with_upstream_state(source_fn, extract_filename)` -- wraps a
  `GraphSpec.source` callable so the dict it returns also carries
  `upstream_state`, resolved via `upstream_provenance.upstream_state_for`.
  The import is function-local (inside the wrapper), matching this module's
  existing convention of not touching provenance/network machinery unless
  the wrapped spec is actually selected.
- `_graph_registry()`'s four Learning-Commons-derived specs
  (`va-math-sol-k8`, `va-math-sol-hs`, `va-reading-sol-k8`,
  `va-writing-sol-k12`) now wrap their `source` lambda in
  `_with_upstream_state(..., "<extract>.json")`, one call per graph, each
  naming its own extract file. The other six specs (Judson, the four ACTFL
  Can-Do modes, world-language) are **not** wrapped -- their source
  documents have nothing to do with the Learning Commons CDN export, and
  giving them an `upstream_state` key would assert a provenance question
  was asked and came back unknown, when the question never applied. Absent
  key = "not applicable"; `"unrecorded"` = "applies, unknown" -- the bead's
  own distinction, now enforced by which specs get wrapped.
- Module docstring gained an "UPSTREAM PROVENANCE (teach-8xw.54)" section
  explaining the mechanism and why the four graphs currently all read
  `"unrecorded"`.
- `_selfcheck()` (the `python3 -m teach.publish_graph` no-args path) now
  asserts, against the real registry, that the four Learning-Commons graphs'
  manifests carry `upstream_state == "unrecorded"` and that
  judson-algebra/va-world-language-sol/actfl-can-do-interpersonal carry no
  `upstream_state` key at all.

`tests/test_publish_graph.py` -- three new tests:

- `test_learning_commons_graphs_report_unrecorded_upstream_state` -- checks
  all four graphs' manifest `source["upstream_state"] == "unrecorded"`
  (against the real registry, not a fixture) and that the string survives
  verbatim into the dataset card (`README.md` embeds `source` as JSON).
  Pins the exact `UNRECORDED_EXTRACTS` set this test assumes, so if
  `upstream_provenance.py` ever changes that set, this test fails loudly
  instead of silently testing the wrong four keys.
- `test_non_learning_commons_graphs_carry_no_upstream_state_key` -- the
  negative case: Judson, world-language, and all four ACTFL modes get no
  `upstream_state` key.
- `test_with_upstream_state_surfaces_the_full_record_for_a_recorded_extract`
  -- calls `_with_upstream_state` directly with a filename NOT in
  `UNRECORDED_EXTRACTS`, so the test actually exercises the other branch of
  `upstream_state_for` (the four registry graphs, being all-unrecorded right
  now, can't distinguish "always returns the literal string" from "correctly
  delegates"). Asserts the result equals `upstream_provenance.load_record()`
  verbatim, that other keys in the wrapped source dict are preserved, and
  that the original source dict passed in isn't mutated in place (a shared
  fixture across tests would otherwise leak state).

## Why the wiring lives in `_graph_registry()`, not in each graph loader

`publish_graph.py`'s own docstring states it is "deliberately engine-level,
not VA-math-specific" -- `build_dataset_files`/`build_multi_graph_dataset_files`
take an opaque `source` dict and never know or care where it came from.
Putting Learning-Commons-CDN-specific logic there would violate that
boundary. `_graph_registry()` already is the layer that knows
graph-specific facts (which loader, which description, which license
caveats per teach-8xw.58) -- it is where the fact "these four extracts came
from this CDN, these six didn't" already lives implicitly in which modules
get imported. Wrapping the four `source` lambdas there keeps the general
`build_dataset_files`/`publish()` path (used directly by callers who supply
their own `source` dict, not through the registry) completely unaffected --
verified: no caller in this repo invokes `publish()`/`build_dataset_files`
directly with a VA-math loader's source outside the registry path, so there
was nothing else needing this wiring.

## Evidence

- `uv run pytest -q` -- **451 passed** (was 448 before this session's edits;
  +3, the new tests above). Full suite, not just this module.
- `uv run python -m teach.publish_graph` (no args, self-check) -- OK,
  including the new upstream-state assertions against the real registry.
- `uv run python -m teach.upstream_provenance` -- OK, unchanged, confirms
  this session didn't touch that module's own behavior.
- Manual check of the actual manifest bytes `build_multi_graph_dataset_files`
  would produce for `va-math-sol-k8`:
  ```json
  {
    "attribution": "Knowledge Graph is provided by Learning Commons under the CC BY-4.0 license. ...",
    "author": "Virginia Department of Education",
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "provider": "Learning Commons (learningcommons.org), Knowledge Graph v1.13.0",
    "retrieved_via": "https://cdn.learningcommons.org/knowledge-graph/v1.13.0/exports/{nodes,relationships}.jsonl",
    "upstream_state": "unrecorded"
  }
  ```
  and confirmed `judson-algebra`'s manifest `source` has no `upstream_state`
  key at all.

## What this session deliberately did not do

- Did not touch `teach/upstream_provenance.py` or
  `teach/data/upstream_provenance.json` -- both were already correct and
  complete from the prior session; this bead's remaining scope was the
  wiring only.
- Did not attempt to recover provenance for the four pre-record extracts.
  Per the bead's own constraint, that is impossible honestly -- their
  original downloads are gone -- and "unrecorded" is the correct, final
  answer for them, not a placeholder waiting to be filled in.
- Did not run `check_upstream()` (the live CDN HEAD check) -- no network
  need in this session, and it wasn't part of the wiring gap.
- Did not touch the many other uncommitted files sitting in this working
  tree from other in-progress/other-bead sessions (`git status` shows
  substantial unrelated modified/untracked state -- e.g.
  `teach/judson_algebra_graph.py`, `teach/actfl_can_do_graph.py`, staged
  `dnf_bond_*` deletions). None of that was read or written by this session
  beyond what's listed under "Files touched" below.

## Files touched

- `teach/publish_graph.py` -- `_with_upstream_state` helper, four
  `_graph_registry()` specs wrapped, module docstring section,
  `_selfcheck()` assertions.
- `tests/test_publish_graph.py` -- 3 new tests (~65 lines).

## Next steps (not this bead)

- If/when this repo re-fetches the Learning Commons export with
  `upstream_provenance.py`'s recording path and regenerates
  `va_math_sol_k8.json` etc. from that fresh download, the extract's
  filename should be added to a *new* record (or the existing one updated)
  and removed from `UNRECORDED_EXTRACTS` -- at that point
  `upstream_state_for` will return the full record automatically, and no
  change to `publish_graph.py` is needed; the wiring here already reads
  whatever `upstream_state_for` says.
- teach-8xw.58 (ACTFL/world-language license gap) and the "one repo per
  graph vs. shared repo" question are unrelated, already tracked
  separately.
