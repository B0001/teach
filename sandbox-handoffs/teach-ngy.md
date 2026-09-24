# teach-ngy handoff

## UPDATE (this session): CLOSED

The prior session below left this bead open because its own required
held-out round (round1) found a confident-wrong-answer case
(HOMOMORPHISMS) that its fix didn't reach, and filed that residual forward
as teach-9wx. teach-9wx has since been fixed and closed by a later session,
with its own real mechanism fix (`_DECISIVE_MARGIN_COVERAGE_GAP`), two unit
tests, and its own genuinely fresh, independently blind held-out round
(round2, 5 fixtures) showing 0/5 confident wrong answers.

This session's job was specifically teach-ngy, not teach-9wx or teach-hpa.
What I did:

1. Read this bead's notes and `bd show teach-9wx` / `bd show teach-hpa` to
   understand what had happened since this bead was left open.
2. Confirmed both fixes (teach-ngy's multi-candidate-tie fix, teach-9wx's
   decisive-margin coverage-gap fix) are present, uncommitted, in the
   current working tree -- nothing needed re-doing.
3. Independently re-ran (did not just trust the notes) both held-out round
   files against the current code:
   `tests/test_concept_recovery_judson_full_graph_generalization.py`
   (round1, 6 fixtures) and
   `tests/test_concept_recovery_judson_full_graph_generalization_round2.py`
   (round2, 5 fixtures). All 11 pass. Combined: 6/11 correct, 5/11 safe
   abstain, **0/11 confident wrong answers**, against the full 20-node
   graph.
4. Ran the full suite: 554 passed, 16 skipped, 1 xfailed -- no regressions.
5. Verified `judson_bond_integration.py` (the only production consumer of
   `concept_recovery`) still uses the 11-node `load_judson_algebra_graph()`,
   not the full graph -- consistent with both prior sessions' notes; this
   lineage remains about a not-yet-made consumer switch.

**Closing rationale**: this bead's own standing rule for closure was "a
real, unit-verified mechanism fix is not sufficient to close when a genuine
held-out round shows a confident wrong answer." That confident-wrong-answer
case (HOMOMORPHISMS) is the one and only thing that kept this bead open.
It's now fixed, and refixed by two rounds of genuinely fresh held-out
evidence (11 fixtures total, 0 confident wrong answers). The remaining known
gap, teach-hpa (false abstention on a genuinely-correct decisive win), is
the SAFE failure direction this bead's own description explicitly names as
acceptable ("DIRECTION OF FAILURE: abstention... that is the safe
direction"), so it does not block closing this bead. teach-hpa stays open,
tracked separately, correctly scoped P3 (below this lineage's P1/P2
confident-wrong-answer bugs).

I did not author a third held-out round specifically for this bead's
closure -- the two rounds already run (one by the session that wrote this
bead's own fix, one by teach-9wx's session, neither self-tuned against by
this session) are real, independent, fresh evidence directly on point, and
a third round with no new question to answer would be redundant work
outside this bead's scope.

Nothing further changed in `teach/concept_recovery.py` or the tests this
session -- this was a verification-and-closure session, not a fix session.
Nothing committed (conservative git policy; no explicit request to commit).

---

## Original handoff (prior session, left bead open)

### Bead

teach-ngy (P1 bug): "concept_recovery discrimination degrades as the graph
grows: 9 more Judson nodes make the Bond/Lagrange acceptance lesson
unrecoverable." Full text in `bd show teach-ngy`.

### Status: left OPEN, not closed

A real, verified mechanism fix was made and does fix the bead's own named
reproduction. But this bead's own required fresh held-out round found a
DIFFERENT confident-wrong-answer case the fix does not touch, so the bead's
named problem ("discrimination degrades as the graph grows") is not fully
resolved. Per this repo's standing rule (see teach-i35's precedent, below), a
mechanism fix that is real and unit-verified is not sufficient to close a
bead in this lineage when a genuine held-out round shows a confident wrong
answer. `bd update teach-ngy --notes=...` records this; the bead stays open
for whoever wants to take on the residual gap (or decide it's out of scope
for this bead's remaining life and close it anyway with `--reason`, pointing
at the new bead as where the residual lives -- that is also a defensible
call, and I left it to whoever picks this up next rather than making it
unilaterally).

### What I did

1. **Reproduced the bug independently.** Loaded `load_judson_full_graph()`
   (20 nodes) and ran the Bond/Lagrange lesson text through
   `score_candidates`/`recover_from_lesson_text` directly. Confirmed exactly
   what the bead describes: raw scores `judson:18.2-factorization-in-integral-domains`=14,
   `judson:16.1-rings`=13, `judson:6.2-lagranges-theorem`=13 (all within
   `_MIN_MARGIN`), `taught_node_id=None`.

2. **Root-caused the mechanism.** `_resolve_candidates` (teach/concept_recovery.py)
   has a multi-candidate-tie branch (`len(close) > 1`, reached when the raw-score
   margin doesn't clear `_MIN_MARGIN`) that tries a coverage tiebreak before
   abstaining. The OLD code only ever checked whether `top` -- the raw-score
   leader -- had decisive coverage dominance over the tied group. It never
   asked whether some OTHER tied candidate was actually the best-covered one.
   This is the exact same class of positional-assumption bug teach-i35 fixed
   one branch up (the single-close-candidate case's rival search), left
   unfixed here.

   In the Bond/Lagrange reproduction: `judson:18.2-factorization-in-integral-domains`
   is a long, verbatim, ring-theory node whose sheer vocabulary size racks up
   incidental raw-count hits from ordinary textbook narration ("recall",
   "write", "definition") that the terse, hand-authored `judson:6.2-lagranges-theorem`
   node never had a chance to contain -- so it leads on raw count while
   covering only a sliver of its OWN vocabulary. `judson:6.2-lagranges-theorem`
   is the one actually well-covered by the lesson text, but the old code
   never checked it because it isn't `top`.

3. **Fixed it** (`teach/concept_recovery.py`, the multi-candidate-tie
   branch): search every candidate in `close` that clears `_MIN_MATCH_WORDS`
   for whichever has the highest coverage fraction, and apply the existing
   `_MIN_COVERAGE_FRACTION`/`_MIN_COVERAGE_MARGIN` test to THAT candidate
   instead of always to `top`. See the `teach-ngy:`-tagged comment in the
   code for the full rationale.

4. **Added a permanent unit test**
   (`tests/test_concept_recovery.py::test_multi_candidate_tie_coverage_winner_need_not_be_the_raw_score_leader`)
   that calls `_resolve_candidates` directly with fabricated `ConceptMatch`/
   `VocabularyIndex` objects, proving the mechanism in isolation (a
   raw-score non-leader wins the multi-way tie on coverage). Full suite:
   539 -> 540 passed, zero regressions, before the held-out round file was
   added.

5. **Diagnostically re-checked** (NOT as validation -- the bead explicitly
   says the Bond/Lagrange lesson is now tuning data) that the fixed code
   recovers `judson:6.2-lagranges-theorem` correctly on that exact lesson
   against the full graph. It does.

6. **Ran the mandatory fresh held-out round.** Sourced real definition text
   for three ring/field nodes directly from `teach/data/judson_ring_field.json`
   (never from concept_recovery.py or any test file), then launched 6
   parallel, fully blind `Agent` calls -- no tool access, zero repo/bug/
   threshold context -- to write natural tutor/student dialogues for: rings,
   factorization-in-integral-domains, splitting-fields, cosets-and-Lagrange
   (deliberately Bond-framing-free, a fresh instance of the bead's own named
   shape), group-homomorphisms (deliberately marked "NOT ring theory" to
   stress the newest, sharpest possible collision this graph addition
   creates), and an off-topic bicycle-gears control case. Measured the fixed
   code against all six, once, honestly, with no tuning:

   - **4/6 correct**: rings -> `judson:16.1-rings`, factorization ->
     `judson:18.2-factorization-in-integral-domains`, lagrange ->
     `judson:6.2-lagranges-theorem`, bicycle_control -> `None` (correct
     abstain, off-domain).
   - **1/6 safe abstention on an expected-correct case**: splitting_fields
     (expected `judson:21.2-splitting-fields`) ties exactly with
     `judson:21.1-extension-fields` at raw score 9 each -- a genuinely close
     confusability (a splitting field IS an extension field with an extra
     condition), so declining is defensible, not a fix failure.
   - **1/6 CONFIDENT WRONG ANSWER**: homomorphisms (expected
     `judson:11.1-group-homomorphisms`) resolved to
     `judson:16.3-ring-homomorphisms-and-ideals` instead. Scores: 16.3=17,
     16.1-rings=10, 11.1-group-homomorphisms=7 (correct answer, third
     place).

7. **Diagnosed the confident-wrong-answer case precisely** (not tuned
   against -- no code changed in response). The raw margin between the
   leader (17) and runner-up (10) is 7, decisively larger than `_MIN_MARGIN`
   (2). That means this case resolves in `_resolve_candidates`'s
   SINGLE-close-candidate branch under its `margin > min_margin` path, which
   by design returns the raw-score leader with **no coverage check
   whatsoever** -- this is a completely different branch from the one
   teach-ngy's fix touches. That short-circuit is deliberate, not an
   oversight: the code comment right above it cites
   `judson_algebra_graph.py`'s `SIGNPOSTED_LESSON` fixture as a real case
   where a decisive raw-score win must NOT be second-guessed against a
   smaller-vocabulary rival's proportionally higher coverage, or a correct
   decisive win gets thrown away as an abstention. Loosening that
   short-circuit risks breaking
   `test_judson_algebra_graph.py::test_signposted_prerequisites_are_recovered`.
   Untangling that tension is real, separate design work, not a one-line
   extension of this bead's fix.

8. **Converted the held-out round into a permanent test file**:
   `tests/test_concept_recovery_judson_full_graph_generalization.py` --
   all six fixtures, honest result narrative, and the diagnosis above, in
   the same style as `tests/test_concept_recovery_writing_domain_generalization_round4.py`
   (teach-i35's own precedent file). One test per case, including a test
   that PINS the wrong answer (`test_homomorphisms_is_a_confident_wrong_answer_not_yet_fixed`)
   so a future fix's effect on this exact case is measured, not assumed.

9. **Filed teach-9wx** ("concept_recovery: decisive raw-score margin
   bypasses the coverage check entirely, letting a long verbatim node beat a
   correct terse rival"), discovered-from teach-ngy, documenting this exact
   residual gap with full reproduction, root cause, what's NOT attempted and
   why, and the same "don't validate against your own tuning data" rule
   applied forward to whoever picks it up next.

10. Ran the full suite one final time after adding the held-out round file:
    **546 passed, 16 skipped, 1 xfailed** -- clean.

### Files changed

- `teach/concept_recovery.py` -- multi-candidate-tie branch of
  `_resolve_candidates`, generalizing teach-i35's rival-search fix to this
  branch.
- `tests/test_concept_recovery.py` -- one new unit test proving the
  mechanism in isolation.
- `tests/test_concept_recovery_judson_full_graph_generalization.py` -- new
  file, the permanent record of this bead's required held-out round.

Nothing committed (conservative git policy; no explicit request to commit
this session).

### What's NOT done / left for whoever picks this up

- The confident-wrong-answer gap (`judson:16.3-ring-homomorphisms-and-ideals`
  vs `judson:11.1-group-homomorphisms`) is real and unresolved. See teach-9wx
  for full detail on what might fix it and the validation discipline
  required.
- `load_judson_algebra_graph()` (11-node) remains the default for all
  existing consumers, unchanged. `load_judson_full_graph()` (20-node) is
  still not used by any production consumer (`judson_bond_lesson.py`,
  `judson_bond_integration.py` both still use the 11-node graph) -- so the
  epic's actual acceptance test remains unaffected by any of this in the
  currently-committed state. This bead and teach-9wx are both about what
  happens if/when a consumer is switched to the full graph, which is where
  the real product risk lives (e.g. any future Learning Commons export or
  full-textbook traversal).
- Splitting_fields' safe-abstention-on-expected-correct case
  (`judson:21.1-extension-fields` vs `judson:21.2-splitting-fields` tied at
  9) was not investigated further -- it's a safe failure direction
  (abstention), consistent with this bead's stated design intent, and is
  recorded honestly in the permanent test file rather than treated as a bug.

### Lineage

teach-cpg (rival-coverage check added) -> teach-i35 (fixed the
single-close-candidate branch's positional rival-search bug; found and
filed teach-t7j for a deeper semantic-tier gap) -> teach-ngy (this bead:
fixed the same class of positional bug in the multi-candidate-tie branch;
found and filed teach-9wx for a deeper decisive-margin-bypasses-coverage
gap). Each fix in this chain is real and verified; each held-out round has
found the next-deepest layer of the same underlying problem (a growing
graph's vocabulary-size and vocabulary-overlap dynamics undermining a
bag-of-words scorer's assumptions). teach-t7j and teach-9wx are both still
open.
