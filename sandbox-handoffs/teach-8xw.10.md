# teach-8xw.10 — Checker: recover taught concept and assumed prerequisites from lesson text alone

## What was built

Nothing existed in the repo for this bead before this session. This session
created:

- `teach/concept_recovery.py` — the recovery step. Given lesson text (any
  plain string, or `teach.boundary.LessonArtifact.text`) and a domain's
  `teach.concept_graph.ConceptGraph`, it:
  - Builds a per-node **distinctive vocabulary** (`build_vocabulary_index`):
    harvests every string reachable inside `ConceptNode.label` and
    `ConceptNode.facts` — generically, via `_flatten_strings`, which
    recurses through dict/list/tuple without ever reading a named key like
    `"leaf_standards"`, so a non-math domain whose `facts` payload is
    shaped completely differently still works (proven by
    `test_domain_agnostic_vocabulary_extraction_ignores_key_names`). Words
    that appear in more than `_MAX_DOCUMENT_FREQ` (4) nodes are dropped as
    curriculum boilerplate before scoring ever runs — this is the part that
    keeps "The student will use mathematical reasoning and justification
    to solve contextual problems..." (near-verbatim across most VA SOL
    grade groupings) from tying every grade of a strand together.
  - Scores every node by word-overlap count against the lesson text
    (`score_candidates`), then `recover_taught_concept` accepts the top
    candidate only if it clears an absolute floor (`_MIN_MATCH_WORDS = 3`
    distinctive words) **and** beats the runner-up by a margin
    (`_MIN_MARGIN = 2`) — both are abstention gates, not just the first
    one. Failing either produces `taught_node_id=None` with a
    machine-readable `abstain_reason` string (two different reasons for
    "nothing matched" vs. "too many things matched too closely" — a test
    checks the reason text differs, not just that it abstained).
  - `recover_assumed_prerequisites` only considers **direct**
    `PrerequisiteEdge` sources of the recovered taught node (never
    transitive/grandparent nodes — proven by
    `test_only_direct_prerequisite_edges_are_considered`), and only reports
    one as assumed if the text both (a) contains an "already
    know"/"recall"/"last year you..."-shaped phrase *and* (b) that
    sentence's words overlap that specific candidate's distinctive
    vocabulary. Vocabulary overlap alone, with no such phrase anywhere in
    the text, reports zero assumed prerequisites rather than guessing
    (`test_assumed_prerequisite_requires_signal_phrase_not_just_overlap`).
  - `python -m teach.concept_recovery` self-check: runs the bead's two
    required example texts (below) and asserts one recovers correctly and
    the other abstains.

- `tests/test_concept_recovery.py` — 10 tests, all passing:
  1. `test_correct_recovery_example_identifies_node_and_prerequisite` — the
     bead's required correct-recovery fixture, checked against the real
     teach-8xw.5 VA Math SOL graph (not a synthetic stand-in).
  2. `test_abstain_example_out_of_graph_vocabulary` — the bead's required
     abstention fixture: a group-theory (Bond/D&F-flavored) lesson text
     checked against the K-8 VA Math SOL graph abstains rather than
     guessing a K-8 node. This is the exact, disclosed gap teach-8xw.15
     names ("undergraduate abstract algebra is beyond the VA K-12 SOL the
     graph is seeded from") — reproduced here as a passing abstention, not
     asserted from memory.
  3. `test_no_vocabulary_overlap_abstains_with_its_own_reason` — the "zero
     overlap" abstention path is distinct from the "ambiguous" path.
  4. `test_plain_text_with_no_speaker_tags_still_recovers` — works on bare
     text, not just a speaker-tagged transcript.
  5. `test_recovers_from_a_real_lessonartifact` — exercises the actual
     `teach.boundary.LessonArtifact`/`Turn` types a real checker receives,
     not a hand-rolled string built to look like one.
  6. `test_ambiguous_candidates_abstain_rather_than_guess` — an exact score
     tie between two synthetic nodes abstains instead of picking
     arbitrarily.
  7. `test_domain_agnostic_vocabulary_extraction_ignores_key_names` — a
     reading-domain graph with a `facts` shape that has nothing to do with
     the math domain's `leaf_standards` key still recovers correctly.
  8. `test_assumed_prerequisite_requires_signal_phrase_not_just_overlap` —
     see above.
  9. `test_only_direct_prerequisite_edges_are_considered` — see above.
  10. `test_build_vocabulary_index_filters_boilerplate_words` — the
      document-frequency filter itself, isolated from the recovery logic
      that depends on it.

  `uv run pytest -q`: 100 passed (90 pre-existing + 10 new).

## Design choices and why

- **The graph is fixed vocabulary, not the traversal.** teach-8xw.10
  depends on teach-8xw.5 "for evaluation... needs real graph nodes to
  check recovered concepts against" — this module takes that literally:
  `recover_from_lesson_text(text, graph)` receives the *whole* domain
  graph (every node this domain could ever teach), the same way a human
  checker who already knows the curriculum would. It never receives which
  node the planner actually traversed to for *this* lesson — that's
  exactly the traversal teach-8xw.9's boundary keeps off the wire. This
  mirrors teach-8xw.11's `fact_checker.py`/`math_facts.py` split (a
  domain-agnostic engine plus a domain's own reference data plugged in),
  not a new pattern.
- **Bag-of-words overlap with document-frequency filtering, not embeddings
  or an LLM call.** Consistent with every other checker built so far
  (`potential_checker.py`, `fact_checker.py`) — cheap, inspectable,
  deterministic, and its failure mode (misses phrasing it doesn't
  recognize) fails toward abstention, not toward a wrong confident answer.
  A future bead could swap in embedding similarity for better recall; this
  session did not do that because nothing in the bead's acceptance
  criteria asked for state-of-the-art recall, only "identifies them
  correctly, or explicitly abstains rather than guessing wrong."
- **No stemming.** "formula" and "formulas" are treated as different
  words. This is a real, disclosed limitation (see below), traded off
  against not wanting to hand-roll a stemmer or add a dependency for a
  heuristic module that already has to state its coverage honestly either
  way.
- **Two independent abstention gates for the taught concept**
  (`_MIN_MATCH_WORDS`, `_MIN_MARGIN`), not one. A single "top score >
  threshold" rule would still confidently pick a winner in a tie; a single
  "margin > 0" rule would accept a barely-there match (score 1 vs. score
  0) as if it meant something. Both are needed and both are tested
  separately.
- **Assumed-prerequisite recovery requires a phrase signal, not just
  vocabulary co-occurrence**, because a lesson that merely *mentions*
  prerequisite-adjacent vocabulary while introducing new content (e.g.
  contrasting old and new) is not textual evidence that the prerequisite
  was assumed already-known — that's a substantive design decision, tested
  explicitly (`test_assumed_prerequisite_requires_signal_phrase_not_just_overlap`).

## What this does NOT do

- **No stemming/lemmatization.** A lesson using "formula" where the source
  standard says "formulas" loses that word as a signal. This showed up
  directly while building the correct-recovery fixture (see
  `sandbox-handoffs/` note below) and was worked around by choosing
  fixture vocabulary that matches the source's exact word forms, not
  fixed at the module level. If a future bead needs this on messier
  real producer output (not hand-picked fixture text), plurals/verb forms
  not matching their vocabulary counterpart is a real, silent recall loss
  — it fails toward abstention (fewer matched words → more likely to hit
  the `_MIN_MATCH_WORDS` floor and abstain) rather than toward a wrong
  answer, but it is undercoverage worth flagging, not fixed here.
- **No confidence score is exposed as a probability.** `ConceptMatch.score`
  is a raw integer word-overlap count, useful for comparison between
  candidates for the *same* text, not calibrated across different texts or
  graphs. Don't read "score=11" as "91% confident" — nothing here computes
  that.
- **Does not attempt concept recovery against the actual Dummit & Foote /
  James Bond narrative content the epic's test case describes**, beyond
  proving that such text correctly triggers abstention against the
  *current* (K-8 math only) graph. Building an actual undergraduate-algebra
  ConceptGraph for that traversal is teach-8xw.15's / a future graph bead's
  job, flagged, not silently assumed, by teach-8xw.15's own description
  ("this may also require extending the graph beyond SOL scope").
- **Single-pass scoring, no iterative refinement or negation-awareness.**
  If a lesson text explicitly says "this is NOT about area and perimeter,"
  the module would still score toward whichever node's vocabulary
  literally appears, because it counts word overlap, not assertion
  polarity. `fact_checker.py`'s false/true-pattern split solves a related
  problem for individual domain-fact claims; concept identification here
  has no equivalent, and this is a known blind spot rather than a
  guaranteed non-issue.

## Verification

```
uv run pytest -q                      # 100 passed
uv run python -m teach.concept_recovery
# OK: correct-recovery example identifies va-math-sol:4.MG with assumed
# prerequisite(s) ('va-math-sol:3.MG',); out-of-graph (group theory) lesson
# text abstains ("best candidate 'va-math-sol:1.NS' shares only 1
# distinctive word(s) with the text (need >= 3)")
```

## Files touched

- `teach/concept_recovery.py` (new)
- `tests/test_concept_recovery.py` (new)

Nothing committed — conservative git policy, bead did not say to commit.
