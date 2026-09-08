# teach-8xw.17 — Verify publish_graph.py live push against a real HF dataset repo

## Status: BLOCKED, left open

Cannot be completed in this session. No `HF_TOKEN` (or `HUGGING_FACE_HUB_TOKEN`)
was present in the environment.

## What I checked (not assumed)

1. `env | grep -i hf` / `grep -i hugging` — empty. `HF_TOKEN` and
   `HUGGING_FACE_HUB_TOKEN` both unset.
2. `pyproject.toml`'s `[tool.sandbox.forward-env]` documents that `HF_TOKEN`
   is *supposed* to be forwarded into the sandbox, with the comment
   "publishing built knowledge graphs to HuggingFace will fail" as the
   consequence of it being absent — i.e. this is a known, named precondition
   of the repo's own tooling, not a fluke of this session.
3. Live network check, not a config check: ran
   `huggingface_hub.HfApi().whoami()` under `uv run`. It raised
   `LocalTokenNotFoundError` — an actual call against the HF API confirming
   no usable credential exists, not just an absent env var (belt-and-braces
   per the "fetch the raw bytes yourself" rule in sandbox-prompt.md).
4. `find` for `~/.huggingface/token` / any `.netrc` with HF creds — none
   found.
5. Confirmed no prior worker had left in-progress artifacts for this bead:
   `git status` showed only unrelated in-flight diffs from other beads
   (concept_recovery.py, dummit_foote_graph.py, etc.) and no
   `sandbox-handoffs/teach-8xw.17.md` existed yet.
6. Confirmed the bead's prerequisite (teach-8xw.14's dry-run path) is still
   intact and passing: `uv run pytest tests/ -k publish -q` → 11 passed. So
   there is no regression to fix here either — the code this bead needs to
   exercise is ready and waiting; only the credential is missing.

## What is needed to close this bead

A session with:
- A real `HF_TOKEN` with write access to a HuggingFace account/org.
- A disposable/test namespace to publish into (so a throwaway dataset repo
  doesn't pollute a real org's dataset list). Suggest something like
  `<your-hf-username>/teach-concept-graph-smoke-test`.

Then, per the acceptance criteria, run either:

```bash
uv run python3 -m teach.publish_graph --repo-id <namespace>/<repo> --live
```

(check `teach/publish_graph.py`'s `__main__`/CLI section for the actual flag
names before relying on this invocation — I did not modify that file this
session, so verify current signature rather than trusting this snippet) or
call `publish(graph, repo_id=..., token=..., dry_run=False)` directly from a
script, using a real `ConceptGraph` (e.g. the VA SOL graph or the Dummit &
Foote graph already in the repo).

That session must then:
- Confirm on huggingface.co that the repo was created with `repo_type="dataset"`.
- Confirm `nodes.jsonl`, `associations.jsonl`, `manifest.json`, `README.md`
  are present in the repo with content matching what
  `build_dataset_files(graph, source=...)` produces locally for the same
  graph (diff, don't eyeball).
- Optionally push a second time to confirm `exist_ok=True` doesn't clobber
  unexpectedly (per this bead's description).
- Record the exact `repo_id` used, and the push result, in this file's
  successor handoff (or an update here) so a future session knows what
  exists on huggingface.co and can clean it up.

## Bead state left as: OPEN, claimed by this session, notes added

Did not close. No credential was available to fabricate a result, and this
repo's standard explicitly forbids reporting an unmeasured result as
verified.
