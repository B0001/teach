# teach-8xw.45 — evidenced_ceiling gets a real (narrow) fabrication cross-reference

## Decision: (b), not (a)

The bead offered two honest closes: (a) document that the transcript-
self-consistency-only gap is fundamental, or (b) implement a verifiable
signal reachable within the blind-checker boundary, with a concrete case
proving it's reachable from a real producer's output, not a hypothetical.

This session found and implemented (b): a genuine cross-reference is
available without crossing the producer/checker boundary, and it caught two
real bugs in this repo's own producers on first use — not fixture text
written to make the new check look good.

## What was built

`teach/potential_checker.py`:

- `_tutor_turns_with_precedent(text)` — same tutor/learner turn split as the
  existing `_tutor_turns`, but paired with whether each tutor turn is
  IMMEDIATELY preceded, in the transcript's own turn order, by a
  learner-spoken turn. Returns `[(text, None)]` for plain, non-speaker-tagged
  text (no turn structure to check at all — preserves old behavior exactly).
- `_evidenced_ceiling` gained a `preceded_by_learner: bool | None` parameter.
  When `_JUST_DID_PATTERN` ("you just carried/solved/handled/...") and
  `_ORDINARY_NEXT_STEP_PATTERN` both match the turn's context, the claim used
  to be unconditionally evidenced (`True`). Now: if `preceded_by_learner is
  False` (a learner turn was checked for, in this same transcript, and
  genuinely isn't there), it returns `False` — unevidenced. Otherwise
  (`True` or `None`, i.e. adjacent-learner-turn or no-turn-structure-to-check)
  it stays `True`, same as before.
- `_extract_from_sentence`, `extract_claims`, and `check_coverage` all thread
  `preceded_by_learner` through from `_tutor_turns_with_precedent`.
- New module-docstring section, "WHAT 'EVIDENCED' CANNOT MEAN, AND THE ONE
  NARROW THING IT CAN (teach-8xw.45)": states plainly that confirming a
  performance claim's *content* actually happened is fundamental and out of
  reach (would require producer-side ground truth the boundary forbids), and
  scopes exactly what the new turn-adjacency signal does and does not catch
  (does not confirm an adjacent learner turn's *content* matches the claim;
  does not catch performance disguised as the learner's own work inside a
  tutor turn).
- New fixtures: `_TEACH_8XW_45_CLAIM_SENTENCE`,
  `_TEACH_8XW_45_LEARNER_TURN_ADJACENT_TEXT` (learner turn immediately
  before the claim → stays HONEST),
  `_TEACH_8XW_45_NO_LEARNER_TURN_TEXT` (identical claim, all-tutor turns
  before it → now INFLATED) — a minimal pair proving the signal fires on the
  turn-order difference alone, not on the claim text.

`tests/test_potential_checker.py`: 3 new tests exercising the minimal pair
and confirming plain untagged text keeps its old (`True`) behavior
unchanged.

## The concrete reproduction (not hypothetical)

Ran the real `teach.dnf_bond_lesson.build_lesson()` and inspected
`artifact.text` directly (`.text.splitlines()`, not source-reading alone).
Its closing line —

> "You just carried that coset argument through to Lagrange's Theorem on
> your own. If you keep working through subgroup problems like this one,
> you'll be ready to tackle the isomorphism theorems next."

— follows eight consecutive tutor-only turns with no learner contribution
about cosets or Lagrange anywhere in them (the last learner turn before it
is an unrelated "I'm not sure I'm cut out for this kind of maths"). Before
this bead, `evidenced_ceiling` returned `True` for the second sentence
(text-only pattern match); after this bead it returns `False`, and
`classify` correctly flags it `INFLATED`.

Separately, `teach.cialdini_integration_check.build_demo_lesson()` renders
all seven Cialdini principles as consecutive tutor turns with the single
learner turn appended only at the very end — `render_commitment_consistency`
("the same kind of move you just handled a moment ago") has no learner turn
anywhere near it there either, and is now correctly flagged INFLATED too.

Both are real, previously-undetected instances of exactly the fabrication
shape the bead describes ("you just correctly solved 10 problems in a row"
— never happened in this transcript) slipping through as HONEST solely
because the text was internally consistent.

## What this does NOT close (still true, restated precisely)

- Whether a claimed action's *content* really matches an adjacent learner
  turn — "learner speaks, tutor immediately claims a match to whatever the
  learner just said" still always reads as evidenced, real match or not.
- Performance disguised as the learner's own work — the producer solving a
  problem inside a tutor turn and crediting the learner — has no learner
  turn to check against at all, and looks identical to ordinary narration.
- Confirming a performance claim's content actually occurred in reality (as
  opposed to in this transcript's own turn-taking shape) remains fundamental
  and out of reach without producer-side ground truth the boundary forbids.

This is stated in `teach/potential_checker.py`'s module docstring so a
future reader doesn't mistake this bead for having solved fabrication
detection in general.

## Tests updated to reflect the corrected (more honest) checker

The fix surfaced 4 previously-passing tests that were passing *because* of
the gap this bead closed, not despite it. Per this repo's rule against
reverting or weakening a checker fix to keep old assertions green, these
were updated to describe the corrected behavior, not reverted:

- `tests/test_dnf_bond_integration.py::test_checker_flags_no_dishonest_potential_claims`
  → renamed `test_checker_flags_the_one_unevidenced_closing_claim`, now
  asserts exactly the one known flag.
- `teach/dnf_bond_integration.py::_self_check()` — same change (was
  asserting `potential_flags == ()`), plus updated docstring/print text.
- `tests/test_cialdini_integration_check.py::test_demo_lesson_passes_the_real_honesty_checker_clean`
  → renamed `test_demo_lesson_flags_the_one_context_free_commitment_claim`.
- `tests/test_cialdini_integration_check.py::test_every_principle_individually_passes_the_real_checker_clean`
  → renamed `..._except_commitment_consistency`: checking a single
  principle in complete isolation (`check_lesson_text("tutor: <move>")`, one
  turn, nothing before it) means COMMITMENT_CONSISTENCY's "you just did X a
  moment ago" premise structurally can never show a preceding learner turn,
  regardless of how the move is used in a real lesson. This is not itself a
  producer bug (see `test_honesty_rubric_verdicts_reachable_from_generated_text`
  below, where the real `dnf_bond_lesson` usage of the same move IS
  evidenced) — it's an inherent limit of checking a context-dependent move
  completely out of context, now correctly disclosed instead of silently
  certified.
- `tests/test_cialdini_integration_check.py::test_honesty_rubric_verdicts_reachable_from_generated_text`
  → `build_demo_lesson()` alone no longer reaches Verdict.HONEST (its only
  classified claim is now the correctly-caught INFLATED one), so this test
  now also exercises `teach.dnf_bond_lesson.build_lesson()`, which genuinely
  does have a learner turn before its equivalent commitment_consistency
  move and reaches HONEST. The test now proves both verdicts are reachable
  from real generated text, from two different real producers — a stronger
  check than either alone.
- `teach/cialdini_integration_check.py::_self_check()` — same
  `lesson_flags == ()` → `len(lesson_flags) == 1` change, plus updated
  docstring/print text and the module docstring's "WHAT THIS RUN DOES NOT
  ESTABLISH" section.

No pre-existing assertion was deleted to make a test pass; every changed
assertion now describes what the corrected checker actually, verifiably
does.

## Follow-up bead filed (out of this bead's scope)

**teach-8xw.51** — the two producer-side bugs this bead's fix exposed:
1. `teach/dnf_bond_lesson.py`'s closing line fabricates a performance the
   learner never demonstrated in this transcript.
2. `teach/cialdini_integration_check.py`'s `build_demo_lesson()` (and/or
   `teach/cialdini.py`'s `render_commitment_consistency` template) renders
   "you just handled a moment ago" with no learner turn anywhere near it.

Not fixed here — this bead's scope is the checker, not the producers, per
its own working rule ("if you discover work outside this bead's scope, file
it as a new bead, do not do it now").

## Verification

- `uv run pytest -q` — 354 passed (351 baseline, 4 updated to describe
  corrected behavior instead of a false "clean", 3 new regression tests for
  the turn-adjacency signal itself).
- `uv run python -m teach.potential_checker` — self-check passes.
- `uv run python -m teach.dnf_bond_integration` — self-check passes, prints
  the one known INFLATED flag (closing line) alongside the recovered
  concept/prerequisite/Lagrange verdicts and disclosed coverage gaps.
- `uv run python -m teach.cialdini_integration_check` — self-check passes,
  prints the one known INFLATED flag (commitment_consistency) alongside the
  teach-8xw.32 contrast and the teach-8xw.44/50 blind-round measurements
  (unchanged by this bead: still 3/25 flagged, 42/45 unclassified).

## Caveat for whoever reads this next

This bead narrows a real, previously undetected gap by exactly one
structural signal (turn-adjacency within the same transcript) — it does not
make `evidenced_ceiling` a truthfulness oracle, and the module docstring
says so in the same terms as this handoff. If a future bead wants to close
the two still-open gaps (adjacent-learner-turn content verification;
performance disguised as learner work), that requires either a different
kind of producer-side instrumentation than this repo currently emits across
the boundary, or accepting those as permanently out of a blind checker's
reach — same shape of decision this repo's teach-9k5/teach-8xw.32/
teach-8xw.50 lineage has already made for the pattern-classification side of
this module.
