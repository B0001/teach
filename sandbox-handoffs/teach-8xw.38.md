# teach-8xw.38 — cialdini.render_authority had no runtime check that authority_fact is a domain fact, not an overpromise

## What was wrong

`teach/cialdini.py`'s `render_authority` docstring stated `authority_fact`
is "deliberately narrow: this backs a checkable domain claim... not a
promise about the learner" — a documentation convention, not an enforced
invariant. `_require` (the only gate on `MotivationMoment` fields) only
checked that the value was a non-empty string. Nothing stopped a caller
from populating `authority_fact` with an overpromise claim instead of a
domain fact, e.g.:

```python
moment = MotivationMoment(
    concept_name="Lagrange theorem",
    cited_source="Dummit and Foote",
    authority_fact="every student who masters this theorem goes on to prove new results with ease",
)
render_authority(moment, 0)  # rendered without complaint
```

The rendered text lands in `teach.potential_checker`'s already-disclosed
blind spot (teach-8xw.32's group-generalization/cited-authority shape):
confirmed `extract_claims("every student who masters this theorem goes on
to prove new results with ease")` returns `()` both bare and wrapped in
`"tutor: "` — the same pre-existing gap, not a new detection failure. So
this citation-framed overpromise would sail through the checker unflagged,
and worse, read as MORE credible for being dressed as a citation — exactly
the risk sandbox-prompt.md names for the whole persuasion layer.

## What was built

`teach/cialdini.py`:

- Added `_AUTHORITY_COHORT_GENERALIZATION_PATTERN`: a narrow regex matching
  a cohort-of-people noun phrase ("everyone who...", "students who...",
  "mathematicians", etc.) within ~80 chars of a future-outcome verb phrase
  ("goes on to", "will", "almost always", "with ease", "agree that").
  Deliberately bounded vocabulary (not bare "everyone"/"will") so it
  doesn't collide with ordinary domain exposition ("every element", "the
  group will act transitively").
- Added `_looks_like_overpromise(fact) -> bool`: True if EITHER (a)
  `potential_checker.extract_claims(fact)` recognizes any potential-claim
  shape at all (TRAIT/COMPARATIVE/GROWTH/OUTCOME), regardless of what
  `honesty_rubric.classify` would say about it — an honestly-conditioned
  promise is still a promise, not a domain fact — OR (b) the cohort-
  generalization pattern above matches.
- Added `_require_domain_fact(moment, field)`: same gate as `_require`,
  plus the overpromise check, raising `ValueError` in the same style.
- `render_authority` now calls `_require_domain_fact(moment,
  "authority_fact")` instead of `_require`.
- Updated the module docstring's "what this module does and does not do"
  section, which previously stated (accurately, until now) that
  `teach/cialdini.py` "does not import anything checker-side." That's now
  false for one field, so the docstring explains what changed and why it
  doesn't undermine the checker/producer blind-eval split from
  sandbox-prompt.md: the split forbids the *checker* reading the
  *producer's* internals so it can't grade itself; this is the reverse
  direction — the producer calling the checker's already-independently-
  built, public `extract_claims` as an input filter on one field, before
  any text exists for a learner to read. The checker, when it later runs
  over whatever this module emits, still does so with zero knowledge this
  guard ran.

`tests/test_cialdini_authority_guard.py` (new file):

- `test_repro_authority_fact_is_unclassified_by_the_general_checker` —
  confirms the premise: the bead's repro sentence is genuinely unclassified
  by `potential_checker.extract_claims`, both bare and `"tutor: "`-wrapped.
- `test_render_authority_rejects_the_teach_8xw_38_repro_fact` — the bead's
  exact repro sentence now raises `ValueError` at render time.
- `test_render_authority_rejects_overpromise_shapes` (parametrized, 3
  cases) — the repro's cohort+outcome shape, a cited-authority-framed
  variant, and a plain `_claim_type`-classified OUTCOME sentence with no
  cohort wording at all (proves condition (a) above fires independently of
  condition (b)).
- `test_render_authority_still_accepts_ordinary_domain_facts` (parametrized,
  3 cases) — the exact domain facts already used in this module's own
  `FAKE_CONTEXTS`/`cialdini_integration_check.py`'s demo moment and the
  pre-existing `tests/test_cialdini.py` fixture, proving the guard doesn't
  reject the plain content this field exists to carry.

## What was NOT done

- Did not modify `teach/potential_checker.py` at all. teach-8xw.32 already
  measured this exact shape family as a general-extractor blind spot and
  deliberately declined to widen that module's pattern list a further
  round, for good reason (documented lineage: teach-yn8 → teach-kmm →
  teach-5gf → teach-8xw.19 → teach-8xw.23 → teach-9k5 → teach-8xw.32, each
  widening round disproven by the next independently-phrased case). This
  bead's guard is scoped to one field in the persuasion layer, not a
  reopening of that decision — it doesn't touch `potential_checker`'s
  patterns or its general blindness to this shape in arbitrary lesson text.
- Did not add an equivalent guard to any other `MotivationMoment` field.
  `render_social_proof`'s `peer_difficulty` doesn't need one: its fixed
  templates only ever slot the value into difficulty-shaped sentences (the
  module docstring already explains this design choice), so there's no
  free-text embedding point for an overpromise to hide in the way
  `authority_fact` has. If a future bead adds a field with the same
  unconstrained-embedding shape, it would need its own guard — this is not
  a general mechanism applied to all seven principles.
- Did not claim this generalizes beyond the shape family named in the bead
  (cohort-generalization / cited-authority-attribution). The regex is
  narrow by construction and, like every pattern list in this repo, will
  miss phrasing neither check recognizes. `_looks_like_overpromise`'s
  docstring states this plainly rather than rounding it into "detects
  overpromises."

## Verification

- `uv run pytest -q` — 279 passed (was 271 before; 8 new tests, all in the
  new file). No pre-existing test changed or removed.
- `uv run pytest tests/test_cialdini.py tests/test_cialdini_integration_check.py -q`
  — 33 passed, unmodified from before this bead (the guard doesn't change
  behavior for any existing fixture's `authority_fact`, all of which are
  plain domain facts).
- `PYTHONPATH=. uv run python3 teach/cialdini.py` — self-check passes (same
  pre-existing requirement for standalone execution as
  `teach/potential_checker.py` itself; `python3 teach/cialdini.py` alone
  fails with `ModuleNotFoundError` on both files equally — not a
  regression this bead introduced).
- `PYTHONPATH=. uv run python3 teach/cialdini_integration_check.py` and
  `PYTHONPATH=. uv run python3 teach/dnf_bond_lesson.py` — both self-checks
  still pass clean; the two real `authority_fact` values in
  `dnf_bond_lesson.py` and the demo moment in
  `cialdini_integration_check.py` are all plain domain facts and are
  unaffected by the new guard.
- Manually re-ran the bead's exact repro against the fixed code: raises
  `ValueError: MotivationMoment.authority_fact must be a checkable domain
  fact attributable to the cited source, not a promise about the learner's
  (or a cohort's) potential -- got '...'` instead of rendering silently.

## Regression bar (from the bead)

> Add a test proving the exact repro sentence above is now rejected at
> render time, not silently passed through to a checker that (correctly,
> and by design) won't catch it downstream.

Confirmed: `test_render_authority_rejects_the_teach_8xw_38_repro_fact` in
`tests/test_cialdini_authority_guard.py` uses the bead's sentence verbatim
and asserts `pytest.raises(ValueError)`.
