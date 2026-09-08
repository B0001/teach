# teach-20c — Checker: detect UNSIGNPOSTED prerequisite use, not just 'recall'-style phrases

## The gap this closes

`recover_assumed_prerequisites()` (teach-8xw.10) only ever fired on lessons
that explicitly signpost ("recall", "you already know", "last year you...").
A lesson that leans on a prerequisite's vocabulary throughout with no such
phrase — `tests/test_dummit_foote_graph.py`'s `BOND_LESSON`, which uses
subgroup/coset language for the entire Lagrange lesson without ever saying
"recall" — returned `assumed_prerequisite_ids == ()`. That's the *correct*
abstention when there's genuinely no textual signal. The bug was that a
lesson silently assuming a prerequisite and a lesson assuming none at all
produced the exact same empty result — indistinguishable, even though (b) is
the case that actually strands a learner.

The bead was explicit: do not close this by widening
`_ASSUMED_KNOWN_PATTERNS`. More signal phrases still only catch lessons that
signpost; they don't touch the silent case, and make the vacuous-pass
problem harder to see (looks like more coverage, isn't).

## What was built

`teach/concept_recovery.py`:

- New `RecoveryResult.unsignposted_prerequisite_ids: tuple[str, ...]` field —
  a third, distinct outcome alongside `assumed_prerequisite_ids` and "no
  signal at all" (both empty). Docstring on `RecoveryResult` spells out the
  three-way split explicitly so a future reader doesn't have to reconstruct
  it from the code.
- New `recover_unsignposted_prerequisites(text, index, taught_node_id,
  assumed_prerequisite_ids)`: for each **direct** prerequisite of the taught
  node not already in `assumed_prerequisite_ids`, scores whole-text overlap
  against that node's distinctive vocabulary (the same
  `VocabularyIndex.node_words` used everywhere else in this module) and
  reports it if the overlap clears `_MIN_UNSIGNPOSTED_MATCH_WORDS` (=
  `_MIN_MATCH_WORDS` = 3, deliberately the same bar concept identification
  itself uses — "this text is meaningfully about that node's content" should
  take the same evidence whether the node is the one being taught or one
  being leaned on silently).
- Wired into `recover_from_lesson_text`: computed after `assumed`, passed
  `assumed` so the two fields are mutually exclusive by construction (a
  signposted prerequisite is never also reported as unsignposted).
- Deliberately does **not** touch `_ASSUMED_KNOWN_PATTERNS` or
  `recover_assumed_prerequisites` at all — the two detectors are additive,
  not a rewrite of the existing one, per the bead's explicit constraint.

## Why whole-text overlap, not per-sentence

`recover_assumed_prerequisites` anchors to a *signaled sentence* because it
needs to tie an explicit "already known" phrase to a specific candidate.
There is no such anchor for the unsignposted case — that's exactly what
makes it silent. So the overlap is scored against the entire lesson text,
same granularity `score_candidates` uses for the taught concept itself. This
is why the threshold reuses `_MIN_MATCH_WORDS` rather than a new, weaker
number: scoring against a bigger haystack (the whole lesson vs. one
sentence) needs at least the same bar to avoid false positives from
incidental word reuse, not a lower one.

## Tests

`tests/test_dummit_foote_graph.py` — the bead named this file specifically
(`test_unsignposted_prerequisites_abstain_rather_than_guess` "pins the
current behaviour and should be updated, not deleted"):

- Renamed to `test_unsignposted_prerequisites_flagged_as_own_category`,
  updated to assert `assumed_prerequisite_ids == ()` **and**
  `unsignposted_prerequisite_ids == ("dummit-foote:3.1-cosets",)` against
  the real `BOND_LESSON` fixture (verified by hand: it shares 5 distinctive
  words with the cosets node's vocabulary — `subgroup, cosets, products,
  coset, left` — well past the threshold).
- New `test_no_signal_at_all_is_still_distinct_from_unsignposted_use`: a
  hand-written Lagrange lesson using only the target node's own vocabulary
  (order, index, divides, finite, blocks — deliberately avoiding
  subgroup/coset/left, the words that overlap the cosets prerequisite)
  recovers the taught concept correctly with **both** fields empty — proving
  case (a) "assumes nothing detectable" still exists and is distinct from
  case (b).
- `test_signposted_prerequisites_are_recovered` gained an assertion that
  `unsignposted_prerequisite_ids == ()` when the prerequisite is signposted
  — mutual exclusivity, from the real graph, not just synthetic.

`tests/test_concept_recovery.py` — 4 new synthetic-graph tests, isolated
from real-graph vocabulary drift:

- `test_unsignposted_prerequisite_use_is_flagged_without_a_signal_phrase` —
  the core positive case.
- `test_unsignposted_and_assumed_are_mutually_exclusive` — a signposted
  prerequisite never double-counts into the new field.
- `test_unsignposted_detection_only_considers_direct_prerequisites` — same
  direct-edges-only discipline as `recover_assumed_prerequisites`; a
  grandparent node sharing plenty of vocabulary still must not be flagged.
- `test_unsignposted_detection_requires_the_same_overlap_bar_as_recovery` —
  a stray word or two (below `_MIN_UNSIGNPOSTED_MATCH_WORDS`) stays silent,
  same abstention discipline as the rest of the module.

`uv run pytest`: 138 passed (134 pre-existing/unaffected + 4 new in
`test_concept_recovery.py`; `test_dummit_foote_graph.py` net +1 test file
count, 13 total there now, all passing).

`uv run python -m teach.concept_recovery` (module self-check): still passes
unchanged — the bead's fixed correct-recovery/abstain examples don't exercise
this new field, so no ground-truth constant needed updating there.

Note: `python3 teach/concept_recovery.py` (the invocation CLAUDE.md's Build &
Test section literally shows) fails with `ModuleNotFoundError: No module
named 'teach'` — reproduced this as **pre-existing**, identical failure on
the unmodified `teach/dummit_foote_graph.py` too, nothing this session
touched or introduced. `uv run python -m teach.<module>` is the invocation
that actually works from repo root; not fixed here, out of this bead's
scope.

## What this does NOT do

- **No stemming**, same disclosed limitation as teach-8xw.10 — "subgroup"
  vs. "subgroups" are different words for document-frequency/overlap
  purposes (though both actually appear in the real D&F node vocab, so this
  didn't bite the fixtures here).
- **No severity/confidence gradient.** A node either clears
  `_MIN_UNSIGNPOSTED_MATCH_WORDS` or it doesn't — there's no "mild" vs.
  "heavy" unsignposted use distinguished, just presence in the tuple.
- **Still bag-of-words, still no negation-awareness** — inherited limitation
  from teach-8xw.10, not addressed or worsened here.
- **Does not change what a consumer of `RecoveryResult` is required to do**
  with the new field — no caller in this repo currently reads
  `unsignposted_prerequisite_ids` yet (there is no acceptance-test harness
  wired up that fails a lesson on it). Surfacing it as an actual pass/fail
  gate in whatever consumes `RecoveryResult` is follow-up work, not scoped
  to this bead (which asked only for the checker to be able to *report* the
  distinction).

## Verification

```
uv run pytest -q                      # 138 passed
uv run python -m teach.concept_recovery
# OK: correct-recovery example identifies va-math-sol:4.MG with assumed
# prerequisite(s) ('va-math-sol:3.MG',); out-of-graph (group theory) lesson
# text abstains (...)
```

## Files touched

- `teach/concept_recovery.py` (modified: new field, new function, wired into
  `recover_from_lesson_text`, docstring updates)
- `tests/test_dummit_foote_graph.py` (modified: renamed/updated the pinned
  test per the bead's instruction, added one new test, one new assertion)
- `tests/test_concept_recovery.py` (modified: 4 new tests)

Nothing committed — conservative git policy, bead did not say to commit.
