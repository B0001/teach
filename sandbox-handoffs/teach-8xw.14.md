# teach-8xw.14 — HuggingFace publish pipeline for built knowledge graphs

## Bottom line

Built `teach/publish_graph.py`: a domain-agnostic pipeline that turns any
`ConceptGraph` (not just the VA Math SOL one from teach-8xw.5) into a
HuggingFace dataset, with a dry-run mode that needs no network and no live
`HF_TOKEN`. Added `huggingface_hub` as a real dependency (was previously
forwarded via `[tool.sandbox.forward-env]` but unused by any code — this
bead is what actually uses it).

- `teach/publish_graph.py` — `build_dataset_files()` (pure, offline,
  deterministic file-building) and `publish()` (dry-run by default,
  live push behind an explicit `dry_run=False` + a real token), plus a CLI
  (`python3 -m teach.publish_graph --repo-id ... [--live]`).
- `tests/test_publish_graph.py` — 11 pytest tests, all exercising the
  offline path (file shape, determinism, dry-run default, dry-run explicit,
  live-without-token error, graph-validation rejection).
- `pyproject.toml` / `uv.lock` — added `huggingface-hub>=1.30.0` via
  `uv add huggingface_hub` (network to PyPI confirmed live this session,
  `curl -sS https://pypi.org/simple/huggingface-hub/` → 200 before adding).

`env -u HF_TOKEN uv run pytest -q`: **90 passed** (79 pre-existing + 11 new).
No pre-existing test touched or broken. `env -u HF_TOKEN uv run python3 -m
teach.publish_graph` (no args) runs the module's own offline self-check and
prints `OK: ...`.

## Design decisions (read before changing the export shape)

### Two functions, split so the testable path never touches the network

`build_dataset_files(graph, source=...) -> {path: bytes}` is pure: no I/O,
no `huggingface_hub` import reachable from it at all. `publish(graph,
repo_id, source=..., token=None, dry_run=None)` wraps it: `dry_run` defaults
to `True` whenever no token is available (arg or `$HF_TOKEN`), and the
dry-run branch returns a `PublishResult` built entirely from
`build_dataset_files()`'s output — it never imports `huggingface_hub.HfApi`.
The live branch imports `HfApi` *inside* the function body, not at module
scope, so a broken or absent `huggingface_hub` install would only break the
live-push path, never the offline one. This is what makes the bead's "dry-run
mode that doesn't require a live HF_TOKEN (so it's testable without live
credentials)" criterion actually true rather than aspirational — the test
suite runs with `HF_TOKEN` explicitly unset (`monkeypatch.delenv` /
`env -u HF_TOKEN`) and every dry-run test passes.

I did not stub or mock `HfApi` to fake-test the live path — per
sandbox-prompt.md, a mocked live-push test would prove nothing about whether
a real push works, only that this module calls a mock the way I wrote the
mock to expect. **The live path (`dry_run=False`) is untested by this repo's
suite.** That is a real gap, not hidden: it needs a live `HF_TOKEN` and a
disposable HF dataset repo to actually verify against, which this sandbox
session does not have (checked: `$HF_TOKEN` is unset here). Filed as
teach-8xw.17 (see below) rather than claimed as covered.

### Export shape: modeled on CASE, not a conformance claim

teach-8xw.3 (this project's registry survey) confirmed live against
`opensalt.net`'s CASE API that `precedes` is CASE's own vocabulary token for
"origin comes before destination in time or order" — exactly
`concept_graph.py`'s `PrerequisiteEdge` direction — and recommended modeling
this bead's export on CASE's `CFItem`/`CFAssociation` shape for ecosystem
interop. `_item_record()`/`_association_record()` do that: `identifier`,
`fullStatement`, `humanCodingScheme`, `CFItemType` for nodes;
`associationType`/`originNodeURI`/`destinationNodeURI` for edges. The
dataset card explicitly says "modeled on ... not a CASE-conformance claim" —
fields CASE's real schema has that this module has no data for (a minted
CFDocument GUID, a publishing authority) are not fabricated to look more
conformant than the underlying data actually is.

### Stayed domain-agnostic, on purpose

`concept_graph.py`'s docstring is explicit that per-domain shape must not
leak into engine code. `publish_graph.py` takes `graph: ConceptGraph` and a
caller-supplied `source: dict` — it never imports `va_math_sol_graph` at
module scope (only inside `_cli()`, which is VA-math-specific *by design*
since it's the one concrete CLI entry point this session had a real graph
to publish). The self-check (`_selfcheck()`, run via `python3 -m
teach.publish_graph` with no args) deliberately builds a tiny synthetic
two-node graph rather than importing the VA Math SOL data, so this module's
own correctness check doesn't depend on that domain's data shape.

### `facts` forwarded unread, `identifier` deterministic

Per `concept_graph.py`, `ConceptNode.facts` is opaque engine-side payload —
`_item_record()` forwards it verbatim into the `facts` key rather than
picking known sub-fields out of it (which would silently assume every
domain's facts have the same shape). Association `identifier` is
`f"{src}::{type}::{dst}"`, not a random UUID — same graph, same publish,
same identifiers every time, so a re-publish of unchanged data produces a
byte-identical diff (checked by `test_build_dataset_files_is_deterministic_
across_calls`).

## What I did NOT do (filed as follow-ups, not done here)

- **Did not verify a live push actually lands on huggingface.co.** No
  `HF_TOKEN` in this sandbox session (confirmed: `echo $HF_TOKEN` empty).
  Filed **teach-8xw.17**: "Verify `teach/publish_graph.py`'s live push path
  against a real (disposable) HF dataset repo once `HF_TOKEN` is available
  in a session" — this is a real, not hypothetical, gap: the dry-run tests
  prove the *files* are right, not that `HfApi.create_repo`/`upload_file`
  are called with arguments that actually work against the live API.
- **Did not publish anything.** This bead is the pipeline, not a publish
  run. `bd show teach-8xw` (the epic) still needs someone to actually invoke
  `--live` once a target org/repo-id and token exist — that's a product
  decision (what HF org/namespace to publish under), not a code task, so I
  didn't guess one.
- **Did not add a `--output-dir` local-write flag to the CLI.** Not asked
  for by the bead's acceptance criteria (dry-run mode + a runnable check
  covering it); would be easy to add later if a worker wants to inspect
  the built files without HF credentials at all, but adding it now would be
  scope the bead didn't ask for.

## Verification

```
env -u HF_TOKEN uv run pytest -q                    # 90 passed
env -u HF_TOKEN uv run python3 -m teach.publish_graph   # module self-check, no HF_TOKEN needed
env -u HF_TOKEN uv run python3 -m teach.publish_graph --repo-id someorg/va-math-sol-k8
  # -> "DRY RUN: would publish 45 nodes / 40 edges to 'someorg/va-math-sol-k8'
  #     as 4 files (52410 bytes): README.md, associations.jsonl, manifest.json, nodes.jsonl"
env -u HF_TOKEN uv run python3 -m teach.publish_graph --repo-id someorg/va-math-sol-k8 --live
  # -> raises ValueError: "publish(dry_run=False) requires a token: pass
  #     token=... or set $HF_TOKEN" -- confirms --live doesn't silently
  #     downgrade to dry-run or crash some other way when no token exists
```

## Files touched

- `teach/publish_graph.py` (new)
- `tests/test_publish_graph.py` (new)
- `pyproject.toml`, `uv.lock` (added `huggingface-hub` dependency via
  `uv add huggingface_hub`)

Nothing committed — conservative git policy, bead did not say to commit.
