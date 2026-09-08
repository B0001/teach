# teach-8xw.9 — Checker: define the blind interface boundary

## What was built

Nothing existed in the repo before this session (scaffold only, one
placeholder test). This session created:

- `teach/boundary.py` — the artifact format that is the boundary itself:
  - `Turn` (speaker, text) and `LessonArtifact` (a tuple of `Turn`, plus a
    `.text` flattening property) are the *only* type allowed to cross from
    producer to checker. It carries nothing but rendered dialogue.
  - `FORBIDDEN_FIELD_SUBSTRINGS` — a list of substrings (`target_node`,
    `traversal`, `planner`, `answer_key`, `answer`, `solution`,
    `prerequisite`, `prereq`, `graph`, `node_id`, `dag`, `target_concept`)
    that mark a field as planner-only.
  - `check_no_forbidden_fields(cls)` — walks a dataclass's fields via
    `dataclasses.fields()` + `typing.get_type_hints()` (needed because
    `boundary.py` uses `from __future__ import annotations`, so raw
    `field.type` is a string, not a type object), recurses into nested
    dataclasses and into dataclasses hiding inside `tuple[X, ...]` /
    `list[X]` containers, and returns every field whose name matches a
    forbidden substring. Empty list = clean.
  - `python -m teach.boundary` self-check: asserts `LessonArtifact` is
    clean and prints an OK line, per this repo's "every module
    self-checks standalone" convention.

- `teach/producer_state.py` — a stand-in for the real planner (which
  doesn't exist yet; that's teach-8xw.4/.5/.6's job). `PlannerState` is a
  dataclass that genuinely carries `target_node_id`, `traversal`,
  `answer_key`, and `turns` — i.e. it's deliberately built to be *unfit*
  to hand to a checker, so the boundary has something real to be tested
  against instead of a strawman. `emit_lesson_artifact(state)` is the one
  function that reaches across the line, and it only reads `state.turns`.
  `python -m teach.producer_state` self-check: builds a `PlannerState`
  with real planner-only values, runs it through `emit_lesson_artifact`,
  and asserts the result carries none of them (`check_no_forbidden_fields`
  passes, `hasattr(artifact, "target_node_id")` is False).

- `tests/test_boundary.py` — 7 tests, all passing (`uv run pytest -q`):
  1. `LessonArtifact` itself is clean.
  2. `Turn` itself is clean.
  3. **The detector fires on an obvious leak** — a locally-defined
     `LeakyArtifact` with a `target_node_id` field is caught. This is the
     "make it fail first" check: proof the detector isn't vacuously
     passing everything.
  4. **The detector fires on a leak nested inside a container** —
     `tuple[TurnWithAnswerKey, ...]` where the nested dataclass (not the
     top-level one) carries `answer_key`. Proves recursion into
     tuple/list-wrapped dataclasses actually works, not just top-level
     fields.
  5. `PlannerState` (the producer's real internal state) is correctly
     flagged as unfit to cross — documents *why* it must never be handed
     directly to a checker, and is a second proof the check isn't tuned
     to always pass.
  6. `emit_lesson_artifact` output carries only `turns`; the planner-only
     values are unreachable as attributes, not just absent as field
     names.
  7. `LessonArtifact.text` renders as plain `"speaker: text"` lines — the
     form a checker would actually read.

- `conftest.py` at repo root (previously absent) — makes `teach` importable
  from `tests/` without a build backend or editable install; pytest
  inserts a `conftest.py`'s directory onto `sys.path` in prepend import
  mode. `pyproject.toml` has no `[build-system]` section, so this was
  needed for the import to resolve at all — worth knowing if a real
  package structure gets built later, since at that point this shim
  should probably be replaced by `uv pip install -e .` with an actual
  build backend.

- Deleted `tests/test_scaffold.py`, per its own docstring instruction
  ("Delete this once the first real test exists").

## What this does NOT do

- It does not build any part of the actual checker (concept recovery,
  domain-fact verification, potential-inflation detection — those are
  teach-8xw.10/.11/.13). This bead was scoped to the *interface*, not the
  checker logic.
- It does not build any part of the actual producer/planner. `PlannerState`
  is explicitly a stand-in built for this bead's test fixtures, not a
  claim about what the real planner will look like structurally. Whoever
  picks up the producer-side beads should feel free to replace it, as
  long as whatever replaces it still only crosses the line through
  something that satisfies `check_no_forbidden_fields`.
- The forbidden-field detector is name-based (substring match on field
  names), not a proof of non-leakage. It cannot, for example, catch a
  planner sneaking `target_node_id`'s *value* into `Turn.text` as prose —
  that's a content-inspection problem, not a schema problem, and is out of
  scope for a static interface check. It also cannot stop a human from
  writing a checker module that directly `import teach.producer_state` and
  reads `PlannerState` instead of receiving a `LessonArtifact` — there is
  no import-time enforcement for that in Python. The boundary is real at
  the *data* level (nothing on `LessonArtifact` can carry planner state
  without the test suite catching it) but not enforced at the *code
  access* level. If that turns out to matter, a follow-up could add a
  static check that scans checker-package source for imports of
  `teach.producer_state` or any future producer-internal module and fails
  the build if found — flagging as a possible future bead, not doing it
  now since nothing calls itself "the checker package" yet.

## Verification

```
uv run pytest -q          # 7 passed
uv run python -m teach.boundary          # OK: LessonArtifact is clean (1 fields, no planner leaks)
uv run python -m teach.producer_state    # OK: emit_lesson_artifact strips all planner-only state
```

## Files touched

- `teach/__init__.py` (new, empty)
- `teach/boundary.py` (new)
- `teach/producer_state.py` (new)
- `tests/test_boundary.py` (new)
- `tests/test_scaffold.py` (deleted)
- `conftest.py` (new, repo root)

Nothing committed — conservative git policy, bead did not say to commit.
