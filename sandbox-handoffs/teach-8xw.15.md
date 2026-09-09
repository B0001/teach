# teach-8xw.15 — Integration: the D&F / James Bond test case, end-to-end

## What was built

The epic's acceptance test, actually run, for the first time. Two new
modules and one new test file:

- `teach/dnf_bond_lesson.py` — the producer side. Builds a real
  `teach.producer_state.PlannerState` targeting
  `dummit-foote:3.2-lagrange-theorem`, traversing exactly the graph's own
  `prerequisite_closure(TARGET) + [TARGET]` (0.1 sets-and-functions -> 1.1
  groups -> 2.1 subgroups -> 3.1 cosets -> 3.2 Lagrange's theorem — verified
  against the graph, not assumed). Each beat is narrated in a Bond/MI6
  frame by a hand-authored `BondNarrationBackend` (conforms to
  `teach.persona.Backend`, checked via `persona.conforms` — a real
  ocean_ollama/ocean_fable-shaped backend is a drop-in swap of this one
  class, no other module needs to change). The four `teach.cbt_primitives`
  are invoked for real against `LessonMoment`s built from this lesson's own
  content (not `FAKE_CONTEXTS`) and re-voiced into the handler's frame,
  including an inserted learner "I'm not cut out for this" turn so
  `render_identify_stuck_belief` has a real belief to respond to. The
  closing line is a bounded encouragement modeled on
  `teach.potential_checker.HONEST_EXAMPLE_TEXT`'s own shape (effort-
  conditioned, points at the ordinary next graph node, not an invented
  reach). `build_lesson()` is the only exported entry point and returns a
  `LessonArtifact` via `emit_lesson_artifact` — nothing else in this module
  should be imported by a checker.

- `teach/dnf_bond_integration.py` — the checker side. `run_integration_check`
  takes a `LessonArtifact` and nothing producer-shaped (does not import
  `PlannerState`, does not import anything from `dnf_bond_lesson` except
  `build_lesson`, which only its own self-check calls). Runs all three
  existing blind checkers against `artifact.text` alone —
  `concept_recovery.recover_from_lesson_text`, `fact_checker.check_lesson_text`
  (against `math_facts.MATH_SOURCE`), `potential_checker.check_lesson_text`
  — and assembles an `IntegrationReport` with an explicit
  `out_of_scope_facts` field so a coverage gap is a field on the report,
  not something a reader has to infer from absence.

- `tests/test_dnf_bond_integration.py` — 5 tests, all passing, asserting on
  the real structured output of the real run (not on `dnf_bond_lesson`'s
  internals): boundary is clean, taught concept and its one direct
  prerequisite are both recovered correctly with correct signposted/
  unsignposted classification, Lagrange's theorem is CONFIRMED and nothing
  is CONTRADICTED, no potential-claim is flagged, and the disclosed
  out-of-scope fact list is exactly `("kernel-normal-subgroup",)`.

## The actual checker report (captured, not summarized)

```
=== concept_recovery ===
taught_node_id: dummit-foote:3.2-lagrange-theorem
assumed_prerequisite_ids: ('dummit-foote:3.1-cosets',)
unsignposted_prerequisite_ids: ()
=== fact_checker ===
[confirmed] (lagrange-order-divides, Dummit & Foote, Abstract Algebra, 3rd ed., section 3.2, Theorem 8 (Lagrange's Theorem)) "This is Lagrange's Theorem, and the proof behind it is the whole reason the roster count was never going to be an accident: for a finite group G with subgroup H, the order of the subgroup divides the order of the finite group."
[cannot_verify] (lagrange-order-divides, Dummit & Foote, Abstract Algebra, 3rd ed., section 3.2, Theorem 8 (Lagrange's Theorem)) "You just carried that coset argument through to Lagrange's Theorem on your own."
out-of-scope for this run (not exercised, not claimed): ('kernel-normal-subgroup',)
=== potential_checker ===
(no claims flagged -- every extracted potential claim classified HONEST, or none were found)
```

Reproduce with `uv run python -m teach.dnf_bond_integration`.

## What this run covered, and what it did not (read this before treating it as a blanket pass)

**Covered:**
- The taught concept (Lagrange's theorem) was correctly named by the
  checker from lesson text alone — no target node, no traversal, no answer
  key on the wire, enforced by `check_no_forbidden_fields` and by
  `dnf_bond_integration.py` importing nothing producer-internal.
- The lesson's one direct prerequisite (cosets) was correctly recovered as
  *signposted/assumed* (the "Recall that the left coset gH..." sentence),
  and correctly NOT double-counted as unsignposted — teach-20c's
  three-way split exercised for real, not just against its own fixtures.
- The mathematical content of Lagrange's theorem itself, as stated in the
  lesson, is CONFIRMED against `teach.math_facts`' source-cited fact
  (D&F 3rd ed., §3.2, Theorem 8) with zero CONTRADICTED verdicts anywhere
  in the text.
- The closing encouragement line passed the honesty rubric clean — zero
  flags, meaning the bounded-Cialdini layer (effort-conditioned promise,
  ceiling evidenced by what the learner had just done in this same lesson)
  held up against real narrative text, not only against
  `potential_checker.py`'s own worked examples.

**NOT covered by this run — disclosed, not silently absent:**
- `teach.math_facts.MATH_SOURCE` has two `SourceFact`s. The second,
  `kernel-normal-subgroup` (D&F §3.2 Prop 7), is topically attached to
  `dummit-foote:3.3-isomorphism-theorems` (teach-25o), which is off this
  lesson's traversal — Lagrange's own `prerequisite_closure` does not
  include it. `dnf_bond_integration.IntegrationReport.out_of_scope_facts`
  reports this explicitly; it is not a bug, it's this run's actual scope
  boundary. A second lesson targeting `3.3-isomorphism-theorems` would be
  needed to exercise that fact, and is out of scope for this bead.
- `potential_checker`'s `evidenced_ceiling` check can only compare a
  claim's promised ceiling against what THIS SAME lesson's text evidences
  — there is no independent producer-side ground truth crossing the
  boundary for it to check against instead. This was already flagged as a
  standing design limitation in `sandbox-handoffs/teach-8xw.8.md`; this run
  confirms it's still true with real lesson text, not new information.
- This exercises exactly one traversal through the D&F graph (the
  5-node Lagrange chain). It says nothing about lessons targeting other
  nodes, other traversal orders, or lessons that get the mathematics
  wrong on purpose (no adversarial/negative-case lesson text was run
  through this integration — the existing negative-case fixtures in
  `tests/test_fact_checker.py`, `tests/test_concept_recovery.py`, and
  `tests/test_potential_checker.py` already cover that at the unit level,
  and continue to pass).
- No live LLM backend was used. `BondNarrationBackend` is deterministic and
  offline, per this repo's established self-check philosophy — consistent
  with `teach.persona`'s own module docstring, which named wiring a real
  backend in as optional future work, not this bead's requirement.

## A real finding, filed separately: **teach-ed3**

Building this lesson surfaced a genuine fragility in
`teach.concept_recovery`'s taught-concept scoring, not specific to this
lesson's content: a lesson that fully and correctly teaches an entire
prerequisite chain (rather than lightly touching prerequisites while
mostly narrating the target) can score its target and its immediate
prerequisite very close together, because both get real definitional
vocabulary. This lesson's first draft scored Lagrange 13 vs. cosets 12 —
under `_MIN_MARGIN=2` — and the checker correctly abstained on a lesson
that had no actual ambiguity a human reader would have had. The fix used
here was legitimate (the target node's own facts already say "the proof
is..."; the narration simply hadn't used the word "proof" yet), not a
threshold change or a content shortcut, and raised the margin to exactly
2. But it was one word away from failing, which is a fragile margin for a
scoring design, not a robust one. Filed as **teach-ed3** rather than fixed
here — this bead's job was to run the acceptance test honestly and report
what happened, including a checker abstaining on a genuinely correct
lesson, not to redesign `concept_recovery`'s scoring algorithm.

## Verification

```
uv run pytest -q                          # 159 passed
uv run python -m teach.dnf_bond_lesson       # OK: 14-turn lesson, boundary clean
uv run python -m teach.dnf_bond_integration  # OK: full report above, all self-check assertions pass
```

Every other module's own `python -m teach.<module>` self-check was also
re-run and still passes clean (no regressions from the new imports).

## Files touched

- `teach/dnf_bond_lesson.py` (new)
- `teach/dnf_bond_integration.py` (new)
- `tests/test_dnf_bond_integration.py` (new)

Nothing committed — conservative git policy, not asked to commit.

## Follow-up filed

- **teach-ed3** — concept_recovery's taught-concept margin is fragile for
  full-prerequisite-chain lessons (see above).
