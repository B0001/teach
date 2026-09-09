# teach-8xw.19 — potential_checker: pronoun-free praise outside the aptitude-noun vocabulary is still invisible to coverage

## What was wrong

`teach/potential_checker.py`'s `_about_learner` (teach-5gf's fix: pronoun OR
`_claim_type` OR a bounded aptitude-noun list) was still a vocabulary
whitelist gating candidacy for both `extract_claims` and `check_coverage`.
teach-5gf's own two rounds of held-out testing (see
`sandbox-handoffs/teach-5gf.md`) already showed it cratering as
independently-authored sentences avoided its vocabulary on purpose:

```
round 1 (8 sentences, varied vocabulary encouraged): 5/8 caught
round 2 (6 sentences, explicitly avoiding gift/talent/genius/instinct/brilliance): 1/6 caught
```

Sentences like "Einstein would have nodded approvingly at reasoning this
sharp." or "Few students ever produce work this polished on a first
attempt." produced `about_learner=0` — not `unclassified`, absent — the
exact bug class teach-yn8, teach-kmm, and teach-5gf had each already fixed
once, reopened one register at a time.

## Why this bead does not widen the vocabulary a fourth time

The bead's own METHOD NOTE forecloses the pattern every prior bead in this
lineage used to close itself: "do not close this bead against a held-out set
written in the same session that does the widening." That's not a
formality here — it's the diagnosis. Every previous fix (teach-yn8 →
teach-kmm → teach-5gf) *did* validate against a fresh, blind subagent's
held-out sentences, and every one still broke on the next round, including
teach-5gf's own two rounds, run in the same session that produced the fix,
before this bead even existed. A same-session "held-out" set, blind agent or
not, keeps sharing the fix-author's implicit model of what pronoun-free
praise looks like — that's exactly what a whitelist can't escape by getting
one generation wider.

So instead of a fourth vocabulary round, this bead changes the mechanism:
**there is no more "is this about the learner" pre-filter.** Every
tutor-spoken sentence (from `_tutor_turns`, unchanged) is now a coverage
candidate. `_about_learner`, `_ABOUT_LEARNER_PRONOUN`, `_ABOUT_LEARNER_APTITUDE`,
and `_APTITUDE_NOUN` are deleted, not widened.

## Why this is safe, not just noisier

Two separate claims, both checked, not asserted:

1. **`extract_claims`'s output does not change.** teach-5gf's gate was
   deliberately engineered as a *superset* of what `_claim_type` can type
   (pronoun OR `_claim_type(sentence) is not None` OR aptitude noun) — the
   middle clause exists specifically so a classifiable sentence could never
   be blocked before classification ran. Since `extract_claims` only ever
   returns sentences `_claim_type` actually typed, and every such sentence
   already passed the old gate, removing the gate cannot add or remove a
   single flagged claim. Verified: `uv run pytest -q` — every
   flag-producing test (yn8/kmm regression and generalization sets, the
   honest/inflated hand-written examples) still passes unchanged.
2. **`check_coverage` gets noisier, not wrong.** With no gate, ordinary
   domain content and Bond narration now show up in `seen` too, alongside
   learner-directed praise. The real D&F/Bond integration lesson
   (`teach/dnf_bond_lesson.py`) went from `about_learner=6` (the sentences
   the old gate happened to recognize as learner-directed) to `seen=32`
   (every tutor-spoken sentence in the lesson) — `classified` stayed at 1,
   `unclassified` grew from 5 to 31. This is the bead's own suggested
   alternative, taken literally: "treating every tutor-turn sentence as a
   candidate and leaning entirely on `_claim_type`'s unclassified bucket for
   disclosure, accepting much noisier coverage stats in exchange for no
   silent gate."

## Field rename: `Coverage.about_learner` → `Coverage.seen`

The old field name asserted the module had identified learner-directed
content — the exact claim that kept turning out false across three beads.
Once the gate is gone, keeping the name `about_learner` would make the
report actively misleading (a sentence like "MI6 keeps a roster of assets
and a separate roster of handlers." is not about the learner, but would now
appear under that name). Renamed to `seen` — a plain count of tutor-spoken
sentences, no claim about their content — and updated every call site:

- `teach/potential_checker.py`: `Coverage` dataclass, `check_coverage`,
  the module's `__main__` self-check.
- `teach/dnf_bond_integration.py`: `IntegrationReport.render()`'s summary
  line ("tutor-spoken sentences: N seen..." instead of "sentences about the
  learner: N seen..."), and the same wording in the no-flags branch and the
  final printed summary. `_self_check()`'s assertions updated to the real,
  re-measured counts (`seen == 32`, `classified == 1`, `unclassified == 31`).
- `tests/test_potential_checker.py`, `tests/test_dnf_bond_integration.py`:
  every `.about_learner` reference renamed to `.seen`; tests whose docstrings
  specifically described the old pronoun-vs-aptitude-noun gate mechanism
  (`test_third_person_aptitude_sentence_about_someone_else_is_still_seen`,
  `test_coverage_still_ignores_learner_speech_for_aptitude_nouns`) rewritten
  to describe the current no-gate mechanism instead of a mechanism that no
  longer exists.

## Regression sentences added

`_TEACH_8XW_19_REGRESSION_SENTENCES` in `teach/potential_checker.py`: the
bead's own reproduction, verbatim, limited to the three sentences quoted as
*complete* sentences ("Einstein would have nodded approvingly at reasoning
this sharp.", "Future textbooks might well cite work that starts exactly
like this.", "Few students ever produce work this polished on a first
attempt."). The bead also quotes four more as trailing-ellipsis fragments
(e.g. "...reminiscent of a young Feynman...") — not reproduced as literal
test fixtures since they aren't standalone sentences as written, and
reconstructing them into full sentences would mean inventing wording this
bead didn't actually specify.

These are a regression check on the bead's own stated reproduction, not a
generalization test — there's no widened pattern here for a generalization
claim to be made about. The architectural fix (no gate at all) makes *every*
sentence, including ones nobody has written yet, land in `seen`; the three
regression sentences just confirm the specific reproduction this bead names
is no longer invisible.

## What was NOT done

- Did not touch `teach/honesty_rubric.py`'s decision table, `_claim_type`'s
  shape patterns, `_TRAIT_PATTERNS`, `_COMPARATIVE_PATTERNS`,
  `_FUTURE_CLAIM_PATTERNS`, `_EFFORT_PATTERNS`, or `_evidenced_ceiling` — the
  claim-shape *classifier* is unchanged; only sentence *candidacy* for
  coverage changed.
- Did not attempt to add new `_claim_type` shapes for the bead's four
  residual categories (named-person comparison without "next X" framing,
  bare inevitability without a modal, oblique future-achievement
  implication, guarantee-of-outcome without "guaranteed to"). Those
  sentences are now `seen`/`unclassified`, which is this bead's actual bar —
  turning them into `classified`/`INFLATED` is a different, optional
  follow-on (teaching `_claim_type` new shapes) that would need its own
  held-out verification round and is out of this bead's scope.
- Did not spawn a fresh agent to write a new held-out set to validate this
  fix, on purpose — see "Why this bead does not widen the vocabulary a
  fourth time" above. The safety argument here is a proof about
  `extract_claims`'s output (point 1, above), not a sampling argument, so
  there is nothing a held-out sampling round would add.

## Verification

- `uv run python -m teach.potential_checker` — self-check passes, now also
  asserting all three teach-8xw.19 regression sentences produce
  `seen=(sentence,)` and `unclassified=(sentence,)`.
- `uv run python -m teach.dnf_bond_integration` — real D&F/Bond lesson:
  `seen=32, classified=1, unclassified=31`, zero flags, report text says
  "tutor-spoken sentences" throughout (no stray "about the learner" left in
  any f-string — grepped for it after editing).
- `uv run pytest -q` — **180 passed** (179 after teach-5gf per its handoff;
  +1 net in `tests/test_potential_checker.py`, confirmed via
  `grep -c "^def test_"` before/after: 32 → 33 — removed 2 tests whose
  docstrings described the now-deleted pronoun/aptitude-noun gate mechanism
  (`test_third_person_aptitude_sentence_about_someone_else_is_still_seen`,
  `test_coverage_still_ignores_learner_speech_for_aptitude_nouns`), added 3
  (`test_no_pronoun_no_aptitude_noun_praise_is_counted_as_seen` for the
  teach-8xw.19 regression sentences, plus
  `test_ordinary_domain_content_is_now_seen_and_unclassified` and
  `test_coverage_still_ignores_learner_speech` covering what those two
  removed tests covered under the new mechanism). `tests/test_dnf_bond_integration.py`
  kept its 6 test functions, only assertion values changed.
- Grepped the whole repo for `about_learner` / `_about_learner` after the
  change: the only remaining hits are prose in comments describing past
  (pre-teach-8xw.19) behavior for historical context, no live code or test
  references to the removed field name or function.

## Follow-up filed

None. This bead's stated alternative ("look at a different mechanism
entirely") is what was implemented, and it closes the specific bug class
(gate-driven invisibility in coverage) structurally rather than
statistically — there is no more gate for a next round of phrasing to slip
past. The `_claim_type` classifier itself remains a bounded whitelist (as
documented in its own module docstring, unchanged by this bead) — that is a
pre-existing, disclosed limitation of `classified` vs `unclassified`, not a
new gap this bead introduces or leaves silently unaddressed. If a future
worker wants `_claim_type` itself to recognize more shapes (turning some of
today's `unclassified` sentences into `classified`/`INFLATED`), that's a new
bead, with its own held-out verification problem to solve honestly.
