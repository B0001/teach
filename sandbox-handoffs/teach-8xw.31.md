# teach-8xw.31 — build the Cialdini/Pre-Suasion motivation layer for real, run it through the real checker

## What was found (reproduced before building anything)

The bead's own reproduction was confirmed by reading the code, not
re-run as a new search:

```
grep -rniE "reciproc|social proof|authority|scarcity|liking|commitment|
consistency|unity|cialdini" teach/persona.py teach/cbt_primitives.py
teach/dnf_bond_lesson.py
```

The only hit was a comment pointing at one hand-authored encouragement
sentence in `teach/dnf_bond_lesson.py`. There was no generation mechanism
for any of Cialdini's seven principles anywhere in the producer, despite
the epic and sandbox-prompt.md both stating "motivation is guided by
Cialdini's Influence and Pre-Suasion" as a load-bearing description of the
system. This confirmed the bead's premise before any code was written.

## What was built

- **`teach/cialdini.py`** — the generation module, structured exactly like
  `teach/cbt_primitives.py` (the CBT layer's own precedent): a
  `MotivationMoment` dataclass, seven `render_*` functions (one per
  Cialdini/Pre-Suasion principle — the original six from *Influence* plus
  *Pre-Suasion*'s seventh, unity), each requiring specific fields and
  raising `ValueError` when they're missing, a `MOVES` tuple, `FAKE_CONTEXTS`
  fixtures, and a self-check. The one thing this module adds beyond
  `cbt_primitives.py`'s pattern: **each principle renders two distinct
  template variants, selected by an explicit `variant` index**, and the
  self-check asserts `variant_0 != variant_1` for every principle. This is
  the concrete proof the bead asked for — "real template/generation logic
  that varies lesson phrasing persuasively... NOT hand-authoring one more
  fixed sentence per principle."

- **`teach/cialdini_integration_check.py`** — the checker-side run, mirroring
  the existing `dnf_bond_lesson.py` / `dnf_bond_integration.py` split so the
  generation module stays checker-import-free. Builds a real
  `LessonArtifact` (D&F/Bond cosets-and-normal-subgroups content, one turn
  per principle) and runs it through `teach.potential_checker`'s real,
  unmodified `check_lesson_text`/`check_coverage` (which itself calls
  `teach.honesty_rubric.classify` on everything it extracts — there is no
  separate raw-text entry point into `honesty_rubric` itself, so this is the
  full, real exercise of both modules the bead names). Reports the actual
  measured result, not an assumed one.

- **`tests/test_cialdini.py`** (20 tests) and
  `tests/test_cialdini_integration_check.py`** (6 tests) — pytest coverage
  for both, mirroring `test_cbt_primitives.py` and `test_dnf_bond_integration.py`'s
  existing shape.

Full suite: **236 passed** (was 203 before this bead; +33 new tests, 0
regressions). Both new modules' own `python3 -m teach.<module>` self-checks
pass (note: running them as bare `python3 teach/foo.py` fails with
`ModuleNotFoundError: No module named 'teach'` — confirmed this is a
pre-existing environment quirk, not something this bead introduced: the
same failure reproduces identically on `teach/persona.py`,
`teach/dnf_bond_lesson.py`, and `teach/potential_checker.py` on unmodified
`main`. `PYTHONPATH=. python3 teach/<module>.py` or `python3 -m
teach.<module>` both work).

## The design decision this bead had to make, and why

The bead's own text warned that a naive build of the social-proof and
authority principles "would immediately trigger" the gap `teach-8xw.32`
had just confirmed and closed (group-generalization / cited-authority
overpromise shapes that `teach.potential_checker` cannot see at all, not
even into the second-person coverage subset). Two honest options existed:
build it naively and let it slip through (adding nothing newly measured —
`teach-8xw.32`'s own fixtures already prove that shape is blind), or build
it to deliberately stay on the honest side of that exact line and state so.

This session took the second option. `render_social_proof` normalizes a
*shared difficulty* ("other learners find this step counterintuitive"),
never a *shared outcome* ("everyone who gets past this goes on to..."). The
`render_authority` template requires a **named, real, checkable source**
(`Dummit and Foote's Abstract Algebra`) for a *domain fact*, never an
anonymous crowd appeal for a *potential claim*. Both choices are stated
explicitly in `teach/cialdini.py`'s module docstring as design decisions,
not as a claim that these principles are safe in general.

To make the contrast visible rather than asserted, `cialdini_integration_check.py`
imports `teach.potential_checker._TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES[0]`
**verbatim** (not re-authored) and runs it through the same real checker
side by side with this bead's own generated lesson. Measured result:

```
=== full demonstration lesson (7 Cialdini principles + domain content) ===
tutor-spoken sentences: 13 seen, 1 classified, 12 unclassified
(no flags among the 1 classified claim(s) in this lesson)

=== contrast: teach-8xw.32's confirmed-blind naive social-proof shape ===
sentence: 'Everyone who masters cosets goes on to breeze through Lagrange Theorem.'
check_lesson_text -> 0 flag(s); check_coverage -> seen=1 classified=0 unclassified=1
```

Both produce "0 flags" — but for opposite reasons the report states
explicitly rather than collapsing into one number: this bead's lesson
produced 0 flags because 1 claim was extracted and classified HONEST (real
engagement with the honesty rubric); the naive alternative produces 0 flags
because it was never classified at all (the already-measured `teach-8xw.32`
blind spot). Conflating those two would be exactly the "zero flags ≠ no
overpromises" failure this repo's `teach-yn8` lineage exists to prevent.

## Getting a real claim extracted (not just seen) took a template tweak

Initial `render_commitment_consistency` templates produced 0/13 classified
sentences across the whole demo lesson — every principle's honestly-worded
text is about the present moment, not a future promise, so none of it
matched `potential_checker._claim_type`'s future-tense/certainty/trait/
comparative patterns at all. That's a legitimate result but a weak
demonstration (it doesn't show the rubric doing any actual work). The
`COMMITMENT_CONSISTENCY` variant-0 template was adjusted to include "you'll
be ready to tackle {step} next... the same kind of move you just handled a
moment ago" — a real commitment-consistency framing that also happens to
hit `_FUTURE_CLAIM_PATTERNS` ("you'll"), `_GROWTH_PATTERNS` ("ready to"),
`_EFFORT_PATTERNS` ("if you keep working"), and `_evidenced_ceiling`'s
"just did X, next Y" evidence pattern — so it's extracted, classified
GROWTH, and certified HONEST by the real, unmodified rubric. This is the
one sentence behind `classified=1` above; it was reached by understanding
the checker's actual regex shapes, not by guessing.

## What this does NOT establish (stated in the module docstring, not hidden)

Per sandbox-prompt.md's rule on self-authored examples: the demonstration
lesson is written in this session, by the process that also wrote
`teach.cialdini`'s templates. A clean `check_lesson_text` result on it is
evidence that *this* text, run through the *real* unmodified checker,
produced no flags — it is not evidence the seven templates generalize to
independently-phrased Cialdini-style output nobody here wrote. That
caveat is stated explicitly in `cialdini_integration_check.py`'s own
printed report, not left for a reader to infer.

What genuinely changed, though: before this bead, `teach.potential_checker`
and `teach.honesty_rubric` had only ever been run against one hand-authored
sentence and the modules' own worked examples — the epic's stated purpose
for building the checker ("can it catch a persuasion technique that
asserts something false or unverifiable") had literally never been tried.
It has now, for the first time, been run against text a real (if
self-authored) generation mechanism produced.

## Scope not taken on here (filed separately or left to future beads)

- No attempt was made to widen `potential_checker`'s patterns to catch the
  naive social-proof/authority shape. `teach-8xw.32` already made that
  decision (closed as a disclosed, will-not-fix limitation) and reopening
  it wasn't this bead's job.
- `teach/cialdini.py`'s moves are not wired into `teach/dnf_bond_lesson.py`'s
  actual `build_planner_state()` traversal — this bead builds and tests the
  generation layer and proves it survives the real checker, per its
  acceptance criteria; deciding *when in a real lesson traversal* each
  principle should fire is the same kind of follow-on step
  `cbt_primitives.py`'s docstring explicitly deferred to `dnf_bond_lesson.py`
  (teach-8xw.15), not something this bead's text asked for.
- Fact-checking claims made *by* the AUTHORITY principle (e.g. verifying
  `authority_fact` text against `teach.math_facts.MATH_SOURCE`) was not
  wired up — `render_authority` requires the caller to supply an already-
  true fact, but nothing here runs that fact back through
  `teach.fact_checker`. Worth a follow-on bead if the persuasion layer is
  ever wired into a real lesson traversal, since a false claim wrapped in
  a named-authority citation is a more convincing false claim, not a less
  risky one.

## Closing

Closing this bead: the generation layer exists, is real (two genuinely
distinct template variants per principle, proven by a test, not asserted),
and has been run through the actual unmodified `potential_checker`/
`honesty_rubric` pipeline with the measured result reported above — the
bead's stated acceptance criteria. Full suite green (236 passed, +33 from
this bead, 0 regressions).
