# teach-8xw.24: publish_graph atomic commit

## What was wrong

`publish()`'s live path called `api.upload_file(...)` once per output file
(nodes.jsonl, associations.jsonl, manifest.json, README.md). Each
`upload_file` call is its own `create_commit` under the hood, so a failure
partway through the loop (e.g. teach-8xw.17's dataset-card license
rejection) left whatever had already uploaded sitting in the public repo —
data files with no README, and therefore no provenance/license/attribution
block, until a retry succeeded.

## Fix

`teach/publish_graph.py`, `publish()`: replaced the `for path, content in
files.items(): api.upload_file(...)` loop with a single
`api.create_commit(repo_id=..., repo_type="dataset", operations=[...],
commit_message=...)` call, where `operations` is a list of
`CommitOperationAdd` — one per file, built from the same `files` dict as
before. `CommitOperationAdd` is imported alongside `HfApi` in the existing
function-local `huggingface_hub` import (still not imported at module
scope, so the dry-run/offline path is unaffected).

All four files now land in exactly one commit, or none reach the Hub at
all if the commit fails validation.

## Verification

**Offline (existing suite + one new test):**
- `uv run pytest` — 192 passed (full repo suite, no regressions).
- Added `test_publish_live_pushes_all_files_in_a_single_commit` to
  `tests/test_publish_graph.py`: monkeypatches `huggingface_hub.HfApi` with
  a fake that records `create_commit`/`upload_file` calls separately, then
  asserts `upload_file` was never called and `create_commit` was called
  exactly once with all four `path_in_repo` values as operations. This is
  the "runnable check behind non-trivial logic" per the working rules —
  it'll fail if a future edit reverts to per-file uploads, without needing
  a live token in CI.

**Live, against a real HF repo (per the bead's explicit "verify against a
real repo, not a dry run" instruction — this bug class is invisible
offline):**
- `$HF_TOKEN` was present in this sandbox (account `lego573402`, confirmed
  via `HfApi().whoami()` — not assumed).
- Ran `uv run python3 -m teach.publish_graph --repo-id
  lego573402/teach-publish-scratch-20260909-223941 --live --private`
  against the real VA Math SOL graph (45 nodes, 40 edges). Succeeded.
- Queried `HfApi().list_repo_commits(repo_id, repo_type="dataset")`
  directly (not a summarized/agent report of it): two commits total — the
  Hub's own empty "initial commit" from `create_repo`, and exactly one
  `teach: publish teach-concept-graph-v1 (45 nodes, 40 edges)` commit.
- Queried `HfApi().dataset_info(repo_id, revision=<that commit's sha>,
  files_metadata=True)` and confirmed all four files
  (README.md, associations.jsonl, manifest.json, nodes.jsonl, plus the
  Hub's auto-generated .gitattributes) are present at that single commit.
- Deleted the scratch repo afterward (`api.delete_repo(...)`) — it existed
  only for this verification.

This confirms the acceptance criterion literally: one commit in the
history holding all four files, on a real repo, not a dry run.

## Scope note

`git status` at the start of this session showed unrelated uncommitted
changes to `teach/potential_checker.py` and
`tests/test_potential_checker.py` (and untracked
`sandbox-handoffs/teach-8xw.23.md`, `sandbox-handoffs/teach-9k5.md`) left
by other sessions. Not touched — outside this bead's scope.

## Files changed

- `teach/publish_graph.py` — `publish()`'s live-push loop replaced with one
  `create_commit` call.
- `tests/test_publish_graph.py` — added the mocked-`HfApi` atomicity
  regression test.

## Status

Closing as done. Tests pass (192/192), live verification performed and
matches the bead's acceptance criteria exactly.
