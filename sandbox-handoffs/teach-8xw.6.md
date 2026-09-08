# teach-8xw.6: Producer: persona/narrative rendering of a graph traversal

## What this bead asked for

Given a traversal (sequence of graph nodes) and a persona config, produce
lesson narrative text, reusing narrator's story-generation machinery
("motive graph, personality as data structure") rather than reimplementing
it from scratch -- with a runnable check that feeds a small fixed traversal
and asserts the output actually mentions each node's concept.

Blocked on teach-8xw.1 (locate narrator), teach-8xw.4 (domain-plugin
boundary), teach-8xw.5 (a real graph). All three were closed before this
session started.

## What was built

`teach/persona.py` (new) + `tests/test_persona.py` (new, 21 tests). No
other files touched. Working tree had no partial work for this bead when
claimed -- `teach/persona.py` did not exist yet.

- **`Persona`** -- vendored from `narrator/ocean.py`'s `Ocean`: five OCEAN
  traits in `[-1.0, 1.0]`, range-validated in `__post_init__`,
  `system_prompt()`/`options()` compile the vector into a tone description
  and sampling knobs, `save`/`load` round-trip through JSON with the same
  reject-unknown/missing/out-of-range/wrong-type checks the original has.
  Deliberately did NOT vendor `CultureMatrix`/`transform` -- nothing in this
  bead's acceptance criteria needs cross-cultural trait reweighting, and it's
  a whole extra correctness surface (narrator treats an uncited matrix as a
  values violation) this bead doesn't need to take on. Renamed from `Ocean`
  because this module isn't murder-mystery flavored; the shape is identical.
- **`Backend` protocol + `conforms()`** -- vendored from
  `narrator/backends/base.py`: `generate(profile, prompt, model=...) -> str`.
  This is the seam a real LLM backend (narrator's `ocean_ollama.py` /
  `ocean_fable.py`-shaped) drops into later without touching
  `render_traversal`.
- **`TemplateBackend`** (the default) -- deterministic, offline, no network,
  no model. Wraps `profile.system_prompt()` around the prompt verbatim. This
  is NOT a mock of an LLM call standing in for a test -- it's the module's
  actual reference implementation, following the same offline-deterministic
  precedent every other producer/checker module in this repo already set
  (`concept_recovery.py`, `potential_checker.py`,
  `cbt_primitives.py`'s `render_*` functions). narrator's own `motive.py`
  draws exactly this line: `describe()` (pure, self-checked) is separate from
  `prose()` (LLM call, deliberately NOT covered by `motive.py`'s own
  self-check because it needs a live model). `beats()`/`TemplateBackend`
  mirror that split.
- **`beats(graph, traversal)`** -- pure, domain-agnostic: turns a sequence of
  node ids into `Beat(node_id, label, facts_text)`, flattening
  `ConceptNode.facts` (opaque per teach-8xw.4) via a local
  `_flatten_strings` that mirrors `concept_recovery.py`'s harvesting logic
  without importing checker code into the producer. Raises `ValueError` on
  an empty traversal, `KeyError` (via `ConceptGraph.by_id`) on an unknown
  node id -- fails loud rather than rendering nothing.
- **`render_traversal(graph, traversal, persona, backend=DEFAULT_BACKEND,
  model=...)`** -- the bead's actual ask: one tutor `Turn` per node, in
  traversal order, each built by calling `backend(persona, prompt_for_beat,
  model=model)`. Returns a `LessonArtifact` (`teach.boundary`) -- the only
  type allowed to cross to the checker. Nothing about `graph` or `traversal`
  is attached to the result beyond what made it into the rendered text.

## Why the narrative reliably mentions each concept

The per-beat prompt (`_beat_prompt`) explicitly includes the node's `label`
and flattened `facts_text` and instructs "use the exact phrase `<label>` at
least once." `TemplateBackend` echoes its input verbatim, so this holds by
construction for the reference backend. This also matters downstream: the
`bd remember` note on `teach-8xw-10-concept-recovery-design` says the
checker does bag-of-words matching with **no stemming** -- "formula" and
"formulas" are different words to it. Keeping the node's exact label/fact
vocabulary intact in the narrative (rather than letting a persona rewrite
paraphrase it away) is what keeps this bead's producer output actually
recoverable by that checker later, not just self-consistent with its own
proxy check. A real LLM backend is not guaranteed to honor that instruction
as reliably -- that's an integration-time question for teach-8xw.15, not
something this bead's offline self-check can promise on.

## Verification

```
uv run python3 -m teach.persona    # -> OK: rendered a 3-node traversal ...
uv run pytest -q                   # -> 121 passed (100 pre-existing + 21 new)
```

The module self-check (`__main__`) does exactly what the bead's acceptance
criteria describes: builds a small fixed 3-node traversal (Dummit & Foote
cosets -> normal subgroups -> quotient groups, the epic's actual test-case
domain), renders it with a non-neutral persona, and asserts (a) every node's
label appears in the output text, (b) the labels appear in traversal order
(not just present-somewhere), (c) `check_no_forbidden_fields` on the
produced artifact's type is still `[]`, (d) an empty traversal and an
unknown node id both fail loud. `tests/test_persona.py` covers the same
ground plus `Persona`'s validation/round-trip behavior, the `Backend`
protocol, and a custom (non-default) backend actually getting used.

## What this bead deliberately did NOT do (in scope for later beads, not filed as new ones -- already covered by existing beads/notes)

- **No live LLM call anywhere**, by design -- see "why" above. Wiring a real
  narrator-shaped backend (`ocean_ollama`/`ocean_fable`) into an actual
  Dummit & Foote / James Bond run is teach-8xw.15's job (it's already
  blocked on this bead and now unblocked).
- **No CBT-primitive integration.** `cbt_primitives.py`'s own docstring says
  it "does NOT decide *when* in a real traversal each primitive should
  fire" and expects the persona layer to "re-voice it, not consume it
  verbatim." Deciding when a `PedagogicalMove` fires during a traversal is a
  real design decision with its own failure modes (e.g. firing
  `SPACED_RETRIEVAL` before anything has actually been taught yet) -- it
  isn't in this bead's acceptance criteria, and bolting it on without
  thinking through the trigger conditions would be exactly the kind of
  scope creep the working rules warn against. Left as an open seam:
  `render_traversal` takes any `Backend`, so a future version could route
  through `cbt_primitives.MOVES` before calling the backend without changing
  this module's public shape.
- **No `CultureMatrix`.** See above.

## Files changed

- `teach/persona.py` (new)
- `tests/test_persona.py` (new)

Not committed -- repo's conservative git policy, no commit/push requested.
