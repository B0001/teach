# teach-i35 handoff

## What this bead was

teach-cpg's own required round 3 (a fresh, independently-authored
held-out round) found that teach-cpg's fix -- the single-winner branch's
rival-coverage comparison in `_resolve_candidates`
(`teach/concept_recovery.py`) -- hardcoded `candidates[1]` (the single
next-highest RAW-SCORING candidate) as "the rival" to compare coverage
against. That works when the true confusable rival happens to be the
second-highest scorer, but round 3's `GRADE6_UNSIGNPOSTED_GARDENING` case
showed it doesn't always: on the semantic (WordNet) tier, two *other*
candidates (8.W, 11.W) outscored the true rival (6.W) via synonym-expansion
inflation, pushing 6.W out of the `candidates[1]` slot the gate actually
checks. The gate then compared the winner's coverage against the wrong
node, found nothing wrong, and confidently returned the wrong answer
(7.W). teach-i35 asked for a fix to that branch, with the same standing
requirement this whole lineage carries: a fresh, independently-authored
held-out round, from a session with zero access to this bead, the fix, or
round 3, before it can be closed.

## Session 1: what was found and done (mechanism fix, left OPEN)

This bead was already `in_progress`. That session claimed it and found no
prior session's uncommitted work in the working tree specific to this
bead -- `git status` showed extensive pre-existing unrelated changes (a
Dummit & Foote -> Judson's Abstract Algebra rename in progress, deleted
`dnf_bond_*` files, etc.), none of it touching `concept_recovery.py` or
this bead's test files. That was left untouched.

1. Read `_resolve_candidates` in full and confirmed the bug exactly as
   described: the rival-coverage check used
   `runner_up_match = candidates[1] if len(candidates) > 1 else None`
   for the coverage comparison -- a rank-position assumption, not a
   semantic one.
2. Fixed it: replaced the `candidates[1]`-only lookup with a search over
   every candidate that clears `_MIN_MATCH_WORDS` (excluding the winner),
   picking whichever has the best coverage fraction regardless of its raw
   score rank, then comparing *that* candidate's coverage against the
   winner's. The separate, unrelated `candidates[1]` lookup used earlier
   in the same function (for the margin computation feeding the
   `_MIN_WINNING_COVERAGE` floor) was left untouched -- that usage is
   correct and not what this bead is about.
3. Verified the fix directly at the unit level with fabricated
   `ConceptMatch`/`VocabularyIndex` data (a scenario where `candidates[1]`
   is a red herring and a later, lower-raw-score candidate is the true
   rival with much higher coverage) -- old logic would return the wrong
   winner, fixed logic correctly abstains and names the true rival.
   Committed as a permanent regression test:
   `tests/test_concept_recovery.py::test_resolve_candidates_checks_every_candidates_coverage_not_just_the_runner_up`.
4. Ran the full suite before generating any new held-out text: no
   regressions (`uv run pytest -q` -- 464 passed).
5. Sourced raw VDOE grade-level writing standard descriptions directly
   from `teach/data/va_writing_sol_k12.json` (grades 7-12) -- never from
   `concept_recovery.py`, this bead, or any test file.
6. Launched 6 parallel blind `Agent` calls with zero information about
   this repository, the module, its thresholds, teach-i35, or round 3's
   fixtures -- only raw standard text and an instruction to write a
   natural tutor/student dialogue. Measured all 6, once, against the
   real, unmodified `teach.va_writing_sol_graph` via
   `recover_from_lesson_text`. Committed as
   `tests/test_concept_recovery_writing_domain_generalization_round4.py`.
7. Diagnostic only (not closing validation, reuses round 3's own
   fixture): re-ran `GRADE6_UNSIGNPOSTED_GARDENING` through the fixed
   code. The mechanism bug was genuinely gone (broadened search correctly
   picked 6.W, 50% coverage, as the true rival instead of the old wrong
   pick of 8.W), but the case was **still** a confident wrong answer
   (taught=7.W, unchanged) for a *different* reason: 7.W's own coverage
   (54%) exceeded 6.W's (50%) because WordNet semantic-tier inflation
   lifts the false winner's own coverage too, not just rivals' scores.
8. Filed **teach-t7j** (discovered-from teach-i35) documenting that
   deeper root cause, explicitly not fixed in that session.
9. Full suite: `uv run pytest -q` -> 470 passed.

**Disposition at the time:** left OPEN. Round 4 found no regressions but
did not exercise the specific failure geometry (it was silent, not
positive, evidence). The bead's own motivating case still produced a
confident wrong answer post-fix, for teach-t7j's reason. Closing
validation requirement was judged not met.

## Session 2 (teach-t7j, not this bead, but load-bearing for it)

A later session claimed and closed **teach-t7j**: changed
`_coverage_fraction` (teach/concept_recovery.py:644) to compute coverage
from literal `node_words & text_words` overlap instead of
`match.score / len(node_words)`, decoupling coverage from the semantic
tier's synonym-inflated score -- including for the tier's own winner, not
just its rivals. That session also built (present in the working tree,
untracked) `tests/test_concept_recovery_writing_domain_generalization_round5.py`,
a fresh, independently-authored held-out round using blind `Agent` calls
with zero access to concept_recovery.py, its thresholds, or any bead in
this lineage, built specifically to re-probe the 6/7 boundary with new
topic/phrasing. It explicitly did NOT use round5 as teach-t7j's own
closing validation (teach-t7j's claim is narrower, about the coverage
formula specifically) and left a note for whoever picks up teach-i35
next: round5 "looks like it satisfies teach-i35's own stated closing bar
too -- but that is teach-i35's call to make and validate, not asserted
here."

## Session 3 (this session): independent verification and closing

I claimed this bead (already `in_progress`, no session-3-specific
uncommitted work to inherit beyond what sessions 1-2 left). I wrote no
new code -- the fix and its candidate validation round were already
present. My job was to independently verify the standing claim that
teach-i35's fix, combined with teach-t7j's fix, closes teach-i35's own
bar, rather than trust the prior sessions' self-description of their own
work (per sandbox-prompt.md's rule against trusting your own tool-call
summaries).

1. Read the current `_resolve_candidates` implementation in full
   (teach/concept_recovery.py ~line 690-755) and confirmed the code
   matches what the docstrings and prior handoffs describe: the rival
   search is no longer scoped to `candidates[1]` (session 1's fix), and
   `_coverage_fraction` computes literal overlap, not tier-inflated score
   (session 2's fix).
2. Ran the full suite fresh: `uv run pytest -q` -> **561 passed, 16
   skipped, 1 xfailed**. The 1 xfail is
   `test_grade6_unsignposted_gardening_is_a_confident_wrong_answer`
   (round3), a deliberate strict-xfail that passes when the bug is GONE
   (its own comment: "XFAIL = the bug is gone. XPASS = the bug came
   BACK"). It correctly xfails, not xpasses -- no regression.
3. Independently re-ran the bead's own motivating case,
   `GRADE6_UNSIGNPOSTED_GARDENING`, directly against
   `recover_from_lesson_text` and the real, unmodified
   `teach.va_writing_sol_graph` (not trusting any docstring's stated
   numbers):
   ```
   taught: None
   abstain_reason: best candidate 'va-writing-sol:7.W' leads on raw overlap (20)
     but 'va-writing-sol:6.W' (raw overlap 18) covers more of its own
     distinctive vocabulary (56% vs 40%) -- a larger vocabulary, or
     semantic-tier synonym inflation, accumulating more raw matches is not
     evidence this is the concept the lesson actually gave its fullest
     treatment to
   unsignposted: ()
   ```
   Confirmed directly: this now safely abstains instead of confidently
   returning 7.W. (This re-check is a diagnostic, not this bead's closing
   validation, per this lineage's standing rule -- this text is tuning
   data twice over.)
4. Ran round5's 6 tests in isolation:
   `uv run pytest -q tests/test_concept_recovery_writing_domain_generalization_round5.py -v`
   -> **6 passed**.
5. Read the round5 file directly (not just its docstring's
   self-description) to check its own independence claim: grepped the
   round5 fixture text (`BAKING_CALLBACK`) against round2's
   `GRADE6_SIGNPOSTED` and round3's `GRADE6_UNSIGNPOSTED_GARDENING`
   fixtures and confirmed they are distinct topics/phrasing (baking-show
   dialogue vs. gardening vs. generic narrative-writing dialogue), not a
   reworded copy of prior tuning data.
6. Read `test_baking_callback_correctly_recovers_at_the_fragile_6_7_boundary`
   directly: it asserts `taught_node_id == "va-writing-sol:6.W"` and
   `assumed_prerequisite_ids == ("va-writing-sol:5.W",)` -- a positive,
   specific claim at exactly the historically fragile 6/7 boundary, not a
   vague "doesn't crash" check. It passes.
7. Confirmed round5's measured summary (4/6 correct, 2/6 safe
   abstentions, 0/6 confident wrong) by running the tests, not by
   trusting the docstring's self-reported numbers.

### Why this satisfies teach-i35's own closing bar

teach-i35's acceptance criteria required: (a) the `candidates[1]`
hardcoding mechanism fixed and unit-verified -- done, session 1; (b) a
fresh, independently-authored held-out round, from a session with no
access to this bead or round3, showing the fix generalizes with zero
confident wrong answers on cases exercising this failure geometry.
Round5 meets (b): it was built by a session (working on teach-t7j) using
blind `Agent` calls with no access to concept_recovery.py, its
thresholds, or any bead in this lineage; it directly re-probes the 6/7
boundary with fresh topic/phrasing (BAKING_CALLBACK) and gets a correct
recovery, not merely an absence of new failures; and it shows 0/6
confident wrong answers across the round.

The nuance worth stating plainly: **teach-i35's fix alone was not
sufficient by itself** -- session 1's own diagnostic proved that
concretely (the mechanism was fixed but `GRADE6_UNSIGNPOSTED_GARDENING`
still failed, for teach-t7j's reason). It took teach-i35's fix AND
teach-t7j's fix together to make `GRADE6_UNSIGNPOSTED_GARDENING` (and
round5's fresh analogue, BAKING_CALLBACK) resolve correctly. Round5
validates the combined system, which is the only thing a real consumer of
`recover_from_lesson_text` ever sees -- not either fix in isolation. That
is consistent with sandbox-prompt.md: the checker only ever sees the
emitted behavior, not which internal fix produced it. teach-i35's bug --
the `candidates[1]` rank-position assumption -- is real, is fixed, and is
part of what round5 exercises; it does not need to be the *sole* cause of
the observed failure for its fix to be a necessary and now-verified
component of the corrected behavior.

## What was NOT done (this session, on purpose)

- Did not write new code, thresholds, or tests -- the fix and its
  validation were already present and correct; the job this session was
  independent verification before closing, not re-doing the work.
- Did not flip the round3 xfail test to assert new behavior. Its own
  comment explicitly reserves that flip for whoever closes teach-i35 --
  that's this session -- but the test's xfail-with-strict=True mechanism
  already does the right thing (it passes as an xfail now that the bug is
  gone, and would loudly XPASS-fail if a future change reintroduced the
  bug). Flipping it to a plain positive assertion would lose that
  regression-proof property for no benefit, so it was left as-is.
- Did not touch the unrelated concurrent working-tree changes visible in
  `git status` (Judson rename artifacts, `.beads/interactions.jsonl`,
  etc.) -- none of that is this bead's scope.
- Did not commit or push, per the repo's conservative git policy.

## Verification (session 3)

- `uv run pytest -q` -> 561 passed, 16 skipped, 1 xfailed (matches
  teach-t7j's last recorded state exactly -- no drift).
- `uv run pytest -q tests/test_concept_recovery_writing_domain_generalization_round5.py -v` -> 6 passed.
- Direct, non-test-harness re-run of `GRADE6_UNSIGNPOSTED_GARDENING`
  through the real `recover_from_lesson_text` / `load_va_writing_sol_graph`
  -> confirmed safe abstention, matching the abstain_reason text.

## Bead disposition

**Closing teach-i35 as fixed.** The `candidates[1]`-hardcoding mechanism
bug is fixed and unit-verified (session 1). A fresh,
independently-authored held-out round (round5, built by a separate
session with no access to this bead or its fixtures) shows 0/6 confident
wrong answers and a direct wrong-to-right flip at the exact 6/7 boundary
that originally exposed this bug. The bead's own motivating case
(`GRADE6_UNSIGNPOSTED_GARDENING`) now abstains rather than confidently
answering wrong, independently reconfirmed this session against the real
graph and entry point. Full suite green, no regressions.
