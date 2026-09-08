# teach-8xw.7 — Producer: CBT primitives as pedagogical building blocks

## What was built

Nothing existed in the repo defining what "CBT primitives are the
pedagogical building blocks" meant concretely. This session built
`teach/cbt_primitives.py`:

- `LessonMoment` — a minimal, deliberately fake stand-in for whatever real
  lesson state teach-8xw.6's persona layer will eventually carry
  (`concept_name` plus a handful of optional fields each primitive needs:
  `learner_statement`, `prior_concept_name`, `next_action`,
  `easier_problem`, `harder_problem`).

- Exactly the four primitives the epic itself names in `bd show teach-8xw`
  — no others invented, to avoid scope creep beyond what was specified:
  - `IDENTIFY_STUCK_BELIEF` — reflects a self-limiting statement the
    learner just made back as a hypothesis to test, not an accepted fact.
    Requires `learner_statement`.
  - `GRADED_EXPOSURE` — frames the next problem as a small step up from
    one the learner just handled. Requires both `easier_problem` and
    `harder_problem`.
  - `BEHAVIORAL_ACTIVATION` — hands the learner one small, concrete,
    doable-right-now action. Requires `next_action`.
  - `SPACED_RETRIEVAL` — asks the learner to recall (not re-read) a
    concept taught earlier in the same lesson before moving on. Requires
    `prior_concept_name`.

  Each is a `PedagogicalMove(name, when_to_use, render)` — `when_to_use` is
  the one-line applicability definition the bead's acceptance criteria
  asks for; `render` is a `LessonMoment -> str` function. `render` raises
  `ValueError` if the field it needs is missing, rather than emitting
  generic filler from context that isn't there — producing plausible
  output from absent input is exactly the failure mode sandbox-prompt.md
  is about.

- `FAKE_CONTEXTS` — one minimal `LessonMoment` per primitive, populated
  with only the fields that primitive needs. Shared between the module's
  own self-check and the test file so both check the same ground truth
  rather than drifting apart.

- `is_on_topic(text, concept_name)` — the mechanical proxy for "on-topic":
  the rendered text must actually mention the concept it was rendered for.
  Deliberately crude (substring match) but real: it would fail on generic
  encouragement that never names the concept, which is the failure mode
  worth catching here.

- `python3 teach/cbt_primitives.py` self-check: asserts there are exactly
  4 primitives, each has a non-empty `when_to_use`, and each renders
  non-empty on-topic output from its fake context. This is the "runnable
  check" the bead's acceptance criteria asks for.

- `tests/test_cbt_primitives.py` — 12 tests, all passing:
  - Exactly the four named primitives are present (`test_exactly_the_four_primitives_the_epic_names`).
  - Every primitive has a non-empty `when_to_use`.
  - Parametrized non-empty/on-topic check across all four (mirrors the
    module self-check, run under pytest).
  - Per-primitive: the *specific* input content (the belief text, both
    problem descriptions, the action, the prior concept name) actually
    appears in the rendered output — not just "on-topic" by the crude
    concept-name substring check, but genuinely reflecting what was passed
    in. This is what would catch a `render_*` function that ignores its
    argument and returns boilerplate.
  - Per-primitive: rendering without the required field raises
    `ValueError` rather than silently succeeding with placeholder text.

Full suite: `uv run pytest tests/ -q` → 46 passed (34 pre-existing + 12
new), 0 failures.

## Design decisions and why

- **Exactly the epic's four primitives, not a longer CBT-inspired list.**
  The epic text explicitly names identify-stuck-belief, graded exposure,
  behavioral activation, and spaced retrieval as *the* examples. Standard
  CBT also has adjacent techniques (cognitive restructuring/challenging
  the belief once surfaced, behavioral experiments, thought records) that
  would be a natural next step after "identify," but adding them wasn't
  asked for by this bead and would be scope creep past what's specified.
  If teach-8xw.6's integration finds it needs a restructuring step as a
  distinct move from identification, that's a new bead, not a retrofit
  here.
- **`render` takes a fake, made-up `LessonMoment`, not any real lesson
  type.** teach-8xw.6 (persona rendering) doesn't exist yet, so there is
  no real lesson-context type to bind against. Building one here would be
  guessing at teach-8xw.6's eventual data model instead of it deciding
  its own shape. `LessonMoment` is explicitly documented as a stand-in.
- **Required-field-missing raises, doesn't default.** A primitive that
  renders something plausible-sounding when the context it needs isn't
  there would be indistinguishable from one that used real context — the
  exact "fluency reads as correctness" failure mode this repo is about,
  just at the producer's building-block layer instead of the checker's.
- **Plain `str` output, not a `teach.boundary.Turn`.** These are content
  templates the persona layer is expected to re-voice into its own
  narrative style (Bond-framed dialogue, etc.), not finished dialogue
  turns. Wrapping them in `Turn` now would presume persona styling
  happens *after* concatenation rather than *during* rendering, which is
  teach-8xw.6's decision to make, not this bead's.

## What this does NOT do (explicitly out of scope for this bead)

- Does not decide *when*, in a real graph traversal, each primitive should
  fire (e.g., "fire GRADED_EXPOSURE after N consecutive correct answers").
  That's sequencing logic that belongs to teach-8xw.6 once it exists.
- Does not do narrative/persona styling (no Bond framing, no fluid-persona
  voice). Deliberately plain, tutor-register text.
- Does not integrate with `teach.boundary` / `LessonArtifact` — these
  primitives don't cross the producer/checker line themselves; whatever
  calls them (teach-8xw.6) is responsible for assembling `Turn`s that
  eventually do.

## Verification performed

- `uv run python3 teach/cbt_primitives.py` — self-check passes.
- `uv run pytest tests/ -q` — 46 passed, 0 failed (ran the full suite, not
  just the new file, to confirm nothing existing broke).
- Manually inspected each `render_*` output for the fake contexts to
  confirm they read as sensible pedagogical moves, not just
  pattern-satisfying strings (see the module's `FAKE_CONTEXTS` for exact
  inputs used).

## Files changed

- `teach/cbt_primitives.py` (new)
- `tests/test_cbt_primitives.py` (new)
- `sandbox-handoffs/teach-8xw.7.md` (new, this file)

## Git / bd status

Not committed — repo policy (`CLAUDE.md`, `sandbox-prompt.md`) is to not
commit or push without being asked, and this bead didn't ask for it.
`bd close teach-8xw.7` will be run after this handoff is written, per the
session's write-before-close instruction. `teach-8xw.15` (integration) was
already blocked on this bead in the tracker; check `bd ready` / `bd
blocked` after close to see what else that unblocks (only teach-8xw.6,
which is itself still open, actually depends on this content).
