# teach-8xw.55 -- one shared HuggingFace dataset repo for all graphs

## What the bead asked for

`publish_graph.py`'s `_cli()` hardcoded `load_va_math_sol_graph`, and
`publish()` wrote `nodes.jsonl` / `associations.jsonl` / `manifest.json` /
`README.md` at the repo root -- so only one graph could ever live in the
now-shared `lego573402/teach-concept-graphs` repo. The bead asked for a
per-graph path prefix under that one repo, a top-level index (counts +
source per graph), and a CLI graph selector, while keeping: one atomic
`create_commit` per publish (teach-8xw.24), no blanket license in the root
card (teach-8xw.57), and no blending of per-graph provenance (interacts with
the still-open teach-8xw.54, not this bead's job).

## The bead's graph count was stale -- corrected against the actual code

The bead's "six graphs, five never published" list still named
`dummit_foote_graph.py`, which teach-8xw.56 replaced with
`judson_algebra_graph.py`. Enumerating what actually exists today: **10**
publishable graphs across 7 modules (ACTFL's Can-Do statements are 4
independent mode-graphs, not one; `va_math_sol_hs` is a function inside
`va_math_sol_graph.py`, not a separate published file):

```
va-math-sol-k8              va_math_sol_graph.load_va_math_sol_graph
va-math-sol-hs               "        "     .load_va_math_sol_hs_graph
va-reading-sol-k8            va_reading_sol_graph.load_va_reading_sol_graph
va-writing-sol-k12           va_writing_sol_graph.load_va_writing_sol_graph
va-world-language-sol        va_world_language_sol_graph.load_...
actfl-can-do-interpersonal   actfl_can_do_graph.load_actfl_can_do_graph("interpersonal")
actfl-can-do-interpretive     "        "                    (...)("interpretive")
actfl-can-do-presentational   "        "                    (...)("presentational")
actfl-can-do-intercultural    "        "                    (...)("intercultural")
judson-algebra               judson_algebra_graph.load_judson_algebra_graph
```

`load_va_math_sol_full_graph()` (the K-8+HS union used for traversal
convenience) is deliberately **not** registered -- its two source halves
have genuinely different shapes, so publishing the union under one manifest
would blend provenance the bead explicitly forbids. Documented inline in
`_graph_registry()`'s docstring.

## What was built

`teach/publish_graph.py` now has two parallel APIs. The old one is untouched
byte-for-byte in its outputs:

- `build_dataset_files(graph, *, source, repo_id=None)` / `publish(...)` --
  single graph, root-level `nodes.jsonl`/`associations.jsonl`/`manifest.json`/
  `README.md`. Existing callers and tests see no behavior change (it now
  shares a `_graph_core_files` helper with the multi-graph path, and
  `manifest.json` gained a `"license"` key alongside the existing ones --
  additive, not tested by existing tests to omit it).

New, for this bead:

- `GraphSpec(key, loader, source, description)` -- a frozen dataclass
  bundling one graph's loader and its own `source` block, so nothing about
  publishing N graphs can accidentally reach into another graph's data.
- `build_multi_graph_dataset_files(specs, *, repo_id=None)` -- for each
  spec, writes `{key}/nodes.jsonl`, `{key}/associations.jsonl`,
  `{key}/manifest.json` (calls `graph.validate()` per graph); at the root,
  writes `index.json` (schema `teach-concept-graph-index-v1`, one entry per
  graph: key, path, description, node/edge counts, domains, license,
  full source block) and `README.md`. Rejects duplicate keys and an empty
  selection with `ValueError`.
- `_root_index_card(...)` -- the root `README.md`. Front matter carries tags
  only, **no** `license:` field (teach-8xw.57's decision: licenses vary by
  directory). Body states that explicitly, then lists every graph's
  license/counts/domains/source as its own JSON block.
- `publish_many(specs, repo_id, *, token=None, dry_run=None, private=False)`
  -- same dry-run-with-no-`$HF_TOKEN` default as `publish()`. Live path:
  resolves the canonical repo id, rebuilds files against it, and pushes
  every file in **one** `create_commit` call. In that same commit it deletes
  whichever of the legacy root files (`nodes.jsonl`, `associations.jsonl`,
  `manifest.json`) `api.list_repo_files` reports actually present remotely
  and aren't already among the new files being written -- so a first
  migration run cleans up the old root layout, a repeat run on an
  already-migrated repo deletes nothing, and it's still exactly one commit
  either way. `list_repo_files` is wrapped in try/except so a brand-new repo
  (nothing to list yet) doesn't fail the publish.
- `_graph_registry() -> dict[str, GraphSpec]` -- the 10 graphs above, built
  with function-local imports so importing `publish_graph` doesn't eagerly
  import every graph module.
- `_cli()` reworked: `--graph KEY` (repeatable, `choices` from the registry,
  default = every graph) replaces the hardcoded loader; `--list` prints the
  registry and exits, no network. `--repo-id` is still required to actually
  publish, but see the bug fix below -- it must *not* be required for
  `--list`.

## A bug this session found in its own work, and fixed

Manual CLI verification (`uv run python -m teach.publish_graph --list`)
failed with an argparse usage error demanding `--repo-id`, even though
`--list`'s own help text says "No network, no data I/O." Cause: `--repo-id`
was declared `required=True` in argparse, so argparse rejects the invocation
before `_cli()`'s `if args.list:` branch ever runs -- the `required=True`
and the "works standalone" promise contradicted each other.

Fixed by dropping `required=True` from `--repo-id` and instead checking
`if not args.repo_id: parser.error(...)` after the `--list` early-return, so
`--list` truly needs nothing else and a real publish still fails fast (exit
2, clear message) without a `--repo-id`. Added two regression tests calling
`_cli()` directly with a patched `sys.argv`
(`test_cli_list_works_without_repo_id`,
`test_cli_requires_repo_id_when_not_listing`) -- this repo's `_cli()` had no
tests at all before this session; these are new coverage for it, not
replacements.

## Provenance requirement (teach-8xw.54 interaction)

The bead requires that a shared root index not imply one provenance across
graphs, and that a graph with unrecorded provenance not inherit another's
record. `teach/upstream_provenance.py`'s `upstream_state_for()` is not
called anywhere in `publish_graph.py` -- wiring it in is teach-8xw.54's job,
still open, not this bead's. What this bead's implementation guarantees in
the meantime: every graph's manifest and index entry carries only its own
`source` dict, verbatim, with no shared/merged fields at the multi-graph
level (`test_real_graph_registry_builds_offline_with_independent_licenses`
asserts `va-math-sol-k8`'s source `!=` `va-math-sol-hs`'s). There is nothing
to blend because nothing provenance-shaped exists above the per-graph
level -- this bead does not solve teach-8xw.54, it just doesn't make it
harder to solve later.

## A licensing gap found and filed separately, not fixed here

Two of the registered graphs have license problems, discovered while wiring
them in:

- `actfl_can_do_graph.py`'s `SOURCE` has no `"license"` key at all, but does
  have a `"usage_terms"` string: *"FREE FOR EDUCATIONAL AND NON-PROFIT USE
  ONLY. COMMERCIAL USE OR SALE IS PROHIBITED."* -- a real restriction with no
  HuggingFace license identifier that means the same thing. `_hf_license_id`
  correctly reports `"unknown"` for it (abstains rather than guessing), but
  an "unknown" license and an actively non-commercial-only license are not
  the same fact, and nothing currently surfaces the second one.
- `va_world_language_sol_graph.py`'s `SOURCE` also has no `"license"` key
  (plausibly CC BY 4.0 like the other three Learning Commons exports, but
  that's a guess, not a verified fact).

Per this repo's precedent (teach-8xw.57: licensing is the repo owner's
decision, not a worker's to make unilaterally), this was **not** resolved
here. Filed as **teach-8xw.58** (discovered-from this bead), with inline
comments in `_graph_registry()` pointing at it above the affected specs.
**All four `actfl-can-do-*` graphs remain registered** -- excluding them
would be a unilateral scope decision too, just in the other direction -- but
`--live` publishing any of them should not happen until teach-8xw.58 is
answered. They are only ever exercised offline/dry-run by this session's
tests.

## Evidence

- `uv run pytest -q` -- **447 passed** (was 434 before this session; +13:
  11 covering the multi-graph machinery, 2 covering the `--list`/`--repo-id`
  CLI bug fix above).
- `uv run python -m teach.publish_graph --list` -- now exits 0, no
  `--repo-id` needed, prints all 10 keys with descriptions.
- `uv run python -m teach.publish_graph` (no args) -- self-check path,
  prints OK including the new multi-graph and real-registry assertions.
- `uv run python -m teach.publish_graph --repo-id lego573402/teach-concept-graphs`
  -- dry run (no `$HF_TOKEN` in this sandbox), correctly reports it would
  publish all 10 graphs as 32 files (30 per-graph + root `index.json` +
  root `README.md`) with no network call made.
- `PYTHONPATH=. uv run python teach/<module>.py` self-check passed for every
  touched/related module: `publish_graph.py`, `judson_algebra_graph.py`,
  `va_math_sol_graph.py`, `va_reading_sol_graph.py`,
  `va_writing_sol_graph.py`, `va_world_language_sol_graph.py`,
  `actfl_can_do_graph.py`.
- No `--live` publish was run against the real Hub repo in this session --
  everything above is dry-run/offline, matching the sandbox's `$HF_TOKEN`-gated
  convention.

## Files touched

- `teach/publish_graph.py` -- multi-graph build/publish API, registry, CLI
  rework, `--list`/`--repo-id` bug fix (596 lines added net across edits).
- `tests/test_publish_graph.py` -- 13 new tests (268 lines added).

No other files were modified for this bead. `teach/judson_algebra_graph.py`,
`teach/upstream_provenance.py`, and the VA/ACTFL graph modules were read for
reference only.

## What this session deliberately did not do

- Did not wire `upstream_provenance.upstream_state_for()` into
  `publish_graph.py` -- that's teach-8xw.54, still open.
- Did not resolve the ACTFL / va-world-language-sol license questions --
  filed as teach-8xw.58, repo owner's call.
- Did not run a live publish against the real Hub repo, migrated or
  otherwise -- no `$HF_TOKEN` in this sandbox, and doing so wasn't asked for.
- Did not touch `_hf_license_id`, `_HF_LICENSE_IDS`, or anything from
  teach-8xw.57 -- already correct, verified rather than re-done.

## Next steps (not this bead)

- teach-8xw.54: wire `upstream_state_for()` into the per-graph manifest/index
  entries so "unrecorded" is a fact a consumer of the published data can
  actually see, not just something this codebase knows internally.
- teach-8xw.58: repo owner decides what to do about ACTFL's non-commercial
  usage terms and va-world-language-sol's missing license field before
  `--live` publishing those five keys.
- Whoever runs the first real `--live` publish against
  `lego573402/teach-concept-graphs` should expect it to delete the existing
  root-level `nodes.jsonl`/`associations.jsonl`/`manifest.json` (the
  currently-published `va-math-sol-k8` graph) in the same commit that adds
  the new per-graph layout -- this is intentional (the bead's own "moving
  them is a breaking change for anyone who already fetched them -- which
  right now is nobody, so do it now" instruction), not a bug.
