# teach-8xw.1 — Locate the 'narrator' story-generation package

## What was done

Two prior sessions searched every index this sandbox could reach (GitHub,
PyPI, grep.app, Sourcegraph, DuckDuckGo) and correctly found nothing, then
correctly routed the question to a human via `bd human` rather than guessing.
The human answered on the bead: `narrator` is local, was never on any index,
and is now bind-mounted read-only at `/workspace-narrator` (mathgraph the
same way at `/workspace-mathgraph`). The human named six files to read:
`motive.py`, `motive_graph.json`, `ocean.py`, `admissibility.py`,
`evidence_ledger.py` in narrator; `graph.py` and `align.py` in mathgraph.
Closing instruction: "confirm what is actually reusable vs what teach must
build."

This session:

1. Verified the mounts are real (`ls /workspace-narrator`, `/workspace-mathgraph`
   — both populated, both genuinely `:ro` — no write attempted).
2. Read all six named files plus `backends/base.py`, `backends/ocean_ollama.py`,
   `pyproject.toml`, and `prd.md` for context on what narrator actually is.
3. **Did not stop at reading.** Per sandbox-prompt.md's rule that a summarizer
   (including my own reading-and-concluding) is a producer too: I executed
   narrator's own embedded self-checks rather than trusting that the code
   does what its docstrings say.
   - `narrator`'s own `.venv` points at a host-machine path
     (`/Users/benjaminhess/miniconda/...`) that doesn't exist in this
     container, so its checked-in venv can't run here as-is.
   - Worked around with `uv run --with networkx --no-project python3 motive.py`
     (run from inside `/workspace-narrator` so its relative
     `motive_graph.json` load resolves) — **read-only**, no files written
     into the mount.
   - Results: `motive.py` → `ok — 18 nodes, 31 edges`; `ocean.py` → `ok`;
     `evidence_ledger.py` → `ok`; `admissibility.py` → `ok`. All four
     self-checks the human pointed at actually pass, not just read plausibly.
4. Read `narrator/prd.md`, which corrects a load-bearing assumption in the
   epic. Narrator is not a general-purpose "story generation" library with a
   callable public API — it's itself a *teaching project* (code-generation +
   psychology, audience: three teenagers) whose artifact happens to be a
   murder-mystery motive simulator. There is no `render(traversal) -> prose`
   entry point to import. "Reuse narrator's story-generation machinery" has
   to mean *reuse specific pieces / imitate specific patterns*, not
   `import narrator`.

## Confirmed reusable vs must-build (posted to the bead's notes in full)

**Reusable as-is (vendor into teach):**
- `ocean.py` — OCEAN 5-vector → system prompt + sampling params. Zero
  coupling to the mystery domain, stdlib + dataclasses only. This *is*
  "personality as data structure." Its `CultureMatrix` citation-required gate
  is a policy worth keeping, not just code worth copying.
- `backends/base.py` (the `Backend` protocol) + `backends/ocean_ollama.py` —
  the profile-in/text-out seam for calling a model.

**Pattern to imitate, not code to call:**
- `motive.py`'s traversal engine (seeded weighted random walk, entry→terminal,
  no-revisit, load-time JSON validation, Mermaid render with the walked path
  highlighted). The algorithm shape is reusable; `motive_graph.json`'s
  content (murder-motive vocabulary) is not. Teach needs its own
  traversal-to-narrative-beats function over mathgraph's DAG, which has
  different edge semantics (`depends_on`/authored vs `aligns_to`/inferred,
  see `mathgraph/graph.py`) than motive.py's escalation-weight edges.
- `admissibility.py` + `evidence_ledger.py`'s grounding pattern
  (provenance-tagged claims, DIRECT vs DERIVED, recursive blind-grounding
  check) is the closest existing analog to what teach's blind checker must do
  for lesson claims vs assumed prerequisites — architecture to replicate for
  lesson content, not a module to import.
- `mathgraph/align.py`'s three-valued MATCHED/AMBIGUOUS/UNMATCHED abstention
  (thresholds fit to a target precision, not hand-picked) is the abstention
  shape teach-8xw.10/.11 should copy.

**Not reusable, not deeply inspected:** `mystery.py`, `clue_partition.py`,
`hypothesis_board.py`, `question_selector.py`, `panel.py`, `chapters.py`,
`turn.py`, `discussion.py`, `agents.py`, `moves.py`, `metrics.py` — all
murder-mystery-gameplay-specific (suspects, clues, interrogation turns).
Named in the bead notes only so a future session doesn't have to re-derive
that these are out of scope.

## What this does NOT do

- Does not implement anything in teach. This bead is confirmation only;
  teach-8xw.6 (persona/narrative rendering) is the bead that builds against
  this confirmation.
- Does not touch `/workspace-narrator` or `/workspace-mathgraph` — both
  mounts are `:ro` and nothing was written to either, including during the
  self-check runs (verified no stray files: `git status` inside neither repo
  was checked since they're foreign repos, but the self-checks used are
  documented as read-only / tempdir-only in their own source).

## Verification

```
(cd /workspace-narrator && uv run --with networkx --no-project python3 motive.py)
# ok — 18 nodes, 31 edges
(cd /workspace-narrator && uv run --no-project python3 ocean.py)               # ok
(cd /workspace-narrator && uv run --no-project python3 evidence_ledger.py)     # ok
(cd /workspace-narrator && uv run --no-project python3 admissibility.py)       # ok
uv run pytest -q     # 16 passed — unchanged, no teach source was touched
bd human list         # No human-needed beads found (already resolved before this session)
```

## Files touched

None in `/workspace` (teach) source. `/workspace-narrator` and
`/workspace-mathgraph` were read and their self-checks executed, never
written to. The only state change is on the bead itself (`--claim`,
`--notes` with the full reusable/build-new breakdown).

Nothing committed — conservative git policy, bead did not say to commit, and
there is nothing in `/workspace` to commit.

## Next step

Closing this bead with `bd close teach-8xw.1`. This should unblock
teach-8xw.6, which still separately depends on teach-8xw.4 (domain-plugin
architecture) and teach-8xw.5 (VA Math SOL graph) before real work can start
there.
