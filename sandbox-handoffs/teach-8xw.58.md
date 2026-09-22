# teach-8xw.58 -- ACTFL Can-Do license question / va-world-language-sol license gap

Status: **left OPEN**. This is a third same-day re-verification pass
(2026-09-20). Zero code changes. Following this repo's rule of not trusting
a prior handoff's narrative, I independently re-grepped the two source
files, re-ran the targeted tests and self-check, and searched for any
recorded repo-owner decision, before writing anything below.

## What I independently confirmed this session

- `grep -n '"license"\|usage_terms' teach/actfl_can_do_graph.py` -> still
  only `usage_terms` at line 190, no `"license"` key.
- `teach/va_world_language_sol_graph.py` -> still deliberately no
  `"license"` key; docstring still cites the VDOE all-rights-reserved,
  non-commercial, permission-required notice.
- `grep -n "blocked_reason=" teach/publish_graph.py` -> still 5 hits
  (`va-world-language-sol` + all four `actfl-can-do-*` keys); every other
  graph is unblocked.
- `uv run pytest tests/test_publish_graph.py tests/test_va_world_language_sol_graph.py -q`
  -> **48 passed**.
- `uv run python -m teach.publish_graph` -> all 4 self-check sections `OK`.
- Searched for a recorded repo-owner decision: `bd memories license`,
  `bd memories actfl`, `bd memories teach-8xw.58`, `bd memories teach-8xw.57`,
  `grep -rn DECIDED .beads/ teach/`, and searched the tree for a
  `DECISIONS`-style file. **None found.** Only the `teach-8xw-58-status`
  memory exists, and it already correctly (as of the last session's
  correction) does not cite `.57` as precedent.

## Conclusion (unchanged from every prior session)

Item 1 -- whether publishing the ACTFL Can-Do graphs and
`va-world-language-sol` to a public HF dataset repo is consistent with
their stated non-commercial / all-rights-reserved terms, and if so under
what license id -- is a repo-owner policy question with **no worker-side
path to close it**. There is no HF-mappable identifier a worker could add
(unlike `teach-8xw.57`/GFDL, which had a real SPDX-style identifier
waiting to be found). Item 2 (verify VDOE's actual terms) was already done
in a prior session via a live fetch of VDOE's web-policies page, cited in
the module docstring. Item 3 (block live publish until item 1 is answered)
is implemented and enforced by `publish_graph.py`'s `blocked_reason` /
`publish_many()` refusal, and re-confirmed working this session.

No code changed. `bd update teach-8xw.58 --notes=...` records this pass.
Working tree also has unrelated uncommitted changes from other concurrent
bead sessions (e.g. `teach/biblical_nt_source.py`, `teach/concept_recovery.py`)
-- untouched, not part of this bead's scope.

## For the next worker or the repo owner

Unchanged from the prior handoff: if you're the repo owner, record a
`DECIDED (repo owner, <date>): ...` note on this bead once item 1 is
answered, and a future session can wire `_graph_registry()` accordingly. If
you're a worker landing here with no such decision recorded, a quick grep
of the two SOURCE dicts plus `blocked_reason` in `publish_graph.py` is
sufficient to confirm nothing has drifted -- there is no need to re-run the
full suite/self-check every single session absent a code diff touching
these files, and there is nothing to build. Leave it open.
