# teach-cia handoff

## Status: NOT FIXED. Bead left open (P4). No code changes in the working tree.

This is a continuation of two prior investigations on this same bead (see the
bead's own notes, dated 2026-09-22 and 2026-09-23, which already falsified a
global `_DISCOURSE_STOPWORDS` extension and a direct vocabulary enrichment of
`judson:11.1-group-homomorphisms`, the latter with measured 11-test-suite
regressions from `build_vocabulary_index()`'s global per-word document-frequency
ripple). This session independently reproduced the recall gap from scratch
(not trusting the prior session's numbers), then tried the specific
combination the prior handoff named as the one remaining untried,
lower-blast-radius direction: a per-node-scoped edit to `judson:16.3`'s text
(instead of a global stopword) paired with a document-frequency-safe
enrichment of `judson:11.1` (choosing only new words whose pre-edit document
frequency was comfortably under `_MAX_DOCUMENT_FREQ=4`, to sidestep the exact
ripple mechanism that broke 11 tests last time). All experiments were done
**in-memory** against `dataclasses.replace`-copied graph objects — nothing on
disk was ever edited. `git status`/`git diff --stat` are clean except for
`.beads/interactions.jsonl` (bd's own bookkeeping from `--claim`) and this
handoff file.

## Independent reproduction

Confirmed directly via `score_candidates()` against
`tests/test_concept_recovery_judson_full_graph_generalization_round11.py`'s
`GROUP_HOMOMORPHISMS_BLIND`, on `load_judson_full_graph()` (unmodified):

```
judson:16.3-ring-homomorphisms-and-ideals  11  [addition, between, first, homomorphism,
                                                  homomorphisms, kernel, multiplication,
                                                  nice, normal, operation, preserves]
judson:16.1-rings                          10  [addition, closed, condition, first, last,
                                                  matrices, multiplication, nonzero,
                                                  operation, under]
judson:11.1-group-homomorphisms             5  [homomorphism, homomorphisms, injective,
                                                  kernel, normal]
```

Matches the bead description exactly (16.3=11, 16.1=10, 11.1=5; abstains only
because 16.3/16.1 tie within `_MIN_MARGIN=2`).

## What this session tried, with hard numbers

### Step 1: elide 16.3's group-analogy sentences (not a global stopword)

`judson:16.3`'s own text explains ring homomorphisms largely BY ANALOGY to
groups ("Similarly, a homomorphism between rings preserves...", "Just as with
group homomorphisms and normal subgroups...", "These subgroups have nice
characteristics..."). Stripped those specific analogy clauses from the
node's `definition` text in memory (not the genuine ring-content sentences
that define kernel/ideal/homomorphism for rings, which stayed untouched):

```
judson:16.3-ring-homomorphisms-and-ideals   7  [between, homomorphism, homomorphisms,
                                                  kernel, normal, operation, preserves]
```

Score drops 11 → 7 (slightly better than the prior session's global-stopword
estimate of 11 → 8, because this also removes "addition"/"multiplication"
that the pure discourse-word cut couldn't touch, since the whole analogy
*sentence* went, not just 3 connective words).

**But this does not fix anything by itself — it hands the win to a
different wrong node.** `judson:16.1-rings` (untouched, still 10) becomes
the outright raw-score leader with a decisive margin (10 vs runner-up 7 >
`_MIN_MARGIN`). The full pipeline still abstains here, but only because the
decisive-margin coverage-gap veto (`_DECISIVE_MARGIN_COVERAGE_GAP`) happens
to catch it: 16.1's coverage of its own vocabulary (19%) is far below
`judson:3.3-subgroups`'s (50%), a gap wide enough to trigger the veto. That
this particular substitution still lands on the safe side is fragile luck in
the specific numbers, not a property anyone designed — it is exactly the
kind of knock-on effect the bead's own notes already warned about (teach-911,
teach-scx: editing one node's score on one lesson measurably shifts which
OTHER node wins on that same lesson).

### Step 2: add step-1's edit + document-frequency-safe enrichment of 11.1

Checked every candidate new word's PRE-EDIT document frequency before adding
it, specifically to dodge the ripple mechanism that broke round3/round7/
round8/round10/round11 last time (adding a word already at
document-frequency 4 pushes it to 5, dropping it from every node's
vocabulary, including nodes that already depended on it). Confirmed this
mechanism live: an early draft of the enrichment used "nonzero reals" for
the determinant-map example — "nonzero" was ALREADY at document-frequency 4
(the exact ceiling), so adding it to an enrichment on `11.1` silently deleted
it from `judson:16.1-rings`'s and `judson:18.2`'s vocabularies too (a visible
score change on 16.1 from 10 to 9 with zero edits to 16.1's own text).
Swapped to "invertible" (pre-edit document frequency 0) instead and
re-verified no other node's score moved for the wrong reason.

With both edits applied together:

```
judson:11.1-group-homomorphisms  10  [determinant, homomorphism, homomorphisms, injective,
                                        inverses, kernel, matrices, normal, reals, sends]
judson:16.1-rings                 9  [addition, closed, condition, first, last, matrices,
                                        multiplication, operation, under]
judson:16.3-ring-homomorphisms     7  [between, homomorphism, homomorphisms, kernel,
                                        normal, operation, preserves]
```

`judson:11.1` now leads outright — genuine progress, and every added word
(determinant/GL_2 map, identity/inverse preservation, image) is grounded in
Judson's real "Group Homomorphisms" section (`homomorph.xml`), the same
source teach-zgn and the 2026-09-23 session already used, not reverse-derived
from this fixture's own wording.

**Still not a correct recovery.** Margin is 10−9=1, which does not clear
`_MIN_MARGIN=2`, so `_resolve_candidates` falls to the coverage tiebreak —
and that requires the winner to cover `_MIN_COVERAGE_FRACTION=0.85` of its
OWN vocabulary. Measured: `judson:11.1`'s coverage on this text is 55.6% (10
of 18 words) — a wide, decisive margin over `judson:16.1`'s 17.6% (comfortably
clears the *margin* requirement, `_MIN_COVERAGE_MARGIN=0.15`) but nowhere
near the *floor* requirement (0.85). Result: `recover_from_lesson_text`
still abstains — "ambiguous match... too close to call" — one step closer
than the prior session's finding (which only reached a 3-way tie), but the
same non-outcome: a safe abstention, not the bead's actual acceptance bar
(correctly recover `judson:11.1`).

Closing that last gap by raw-score margin needs `judson:16.1` to drop by 1
more point or `judson:11.1` to gain 1 more point of real (non-fixture-fit)
overlap. Closing it via the coverage floor instead needs `judson:11.1`'s own
vocabulary to be ~85% present in the text — i.e. trimming existing, real
words from its vocabulary that this particular lesson doesn't happen to use
("divide", "mapped", "structure", "preserving" — all pre-existing, unrelated
to this session's edits), which would just move the same problem to whatever
OTHER lesson those words currently serve. Either route from here is
indistinguishable from tuning against this one held-out fixture rather than
adding genuine source content — the thing sandbox-prompt.md's "you cannot
hold out examples from yourself" already warns against, and round11 is this
lineage's own held-out check, not a scratch fixture to fit.

## Why this still isn't a fix worth committing

1. It does not clear the bead's own acceptance bar (correct recovery of
   `judson:11.1`) — it produces a *better-quality* abstention (unanimous
   near-win instead of a 3-way muddle), not a win.
2. Step 1 alone (before any 11.1 enrichment) already demonstrated that
   knocking down `judson:16.3` can silently make `judson:16.1-rings` the new
   raw-score leader on this fixture — this particular case is still caught by
   the coverage-gap veto, but that is a property of these specific numbers,
   not a guarantee, and the bead's own history (teach-911/teach-scx) already
   shows single-node text edits routinely move OTHER lessons' outcomes in the
   same graph. A real attempt would still need the full generalization suite
   (round3/6/7/8/9/10/11, `test_concept_recovery_judson_full_graph_
   generalization.py`, `test_judson_algebra_graph.py`) re-run against it, on
   top of physically implementing the edit (see below) — this session did not
   do that, because step 2's result did not clear the acceptance bar and so
   there was nothing yet worth that validation cost.
3. Physically implementing step 1 still requires the addressing-scheme fix
   the 2026-09-23 session already flagged and left undone: `EXCERPT_EDITS` in
   `extract_judson_ring_field.py` is keyed by `(node_id, xml_id)`, and all of
   `judson:16.3`'s term-definition blocks have `xml_id=None` (ordinary `<p>`
   tags), so today's mechanism cannot address "this specific sentence in this
   specific block" the way it already does for `judson:16.1`'s single
   `xml_id`-tagged example. That is a real code change to the extractor
   (index- or substring-keyed addressing), untried this session because
   step 2 showed the result wouldn't clear the bar even with it.

## What this leaves for a future worker

The three-times-measured picture is now: raw-margin fix, coverage-floor fix,
and (this session) the combination of a scoped node edit with a
document-frequency-safe enrichment ALL stop just short of the acceptance bar,
each for a structurally different reason (respectively: not enough headroom
without breaking other fixtures; the 0.85 floor is calibrated for a different
failure mode entirely and is nowhere close to reachable by a small
prerequisite node; a 1-point margin gap that would need either more real
source content than the section actually contains, or fixture-fitting to
close). None of the three failure modes is a threshold-tuning problem — no
single constant in `concept_recovery.py` moves this outcome without
reopening a different, already-fixed bug (the file's own long comment blocks
document that pattern for nearly every constant in it). The remaining honest
paths are the same two the 2026-09-23 handoff already named:

1. Real score normalization at the winner-selection stage (explicitly
   flagged there as having "repo-wide blast radius" — this session's step 1
   is a small, concrete illustration of exactly that blast radius: a
   one-node text edit measurably reshuffled a different node into the raw
   leader on the very fixture it was meant to fix).
2. Accept this as a known, safe, non-hazardous recall gap and leave it open
   at low priority — the system has never, across three sessions'
   independent attempts, produced a confident WRONG answer on this fixture;
   every attempt's failure mode was "still abstains," which is this module's
   own documented preferred failure mode (sandbox-prompt.md: "prefer
   abstention to a confident answer").

## Verification

`uv run pytest -q`: **721 passed, 16 skipped, 1 xfailed, 0 failed** — baseline,
unchanged by this session (all experiments ran against in-memory
`dataclasses.replace` copies of the graph, never against the files pytest
actually loads). `git status --short` / `git diff --stat`: clean except
`.beads/interactions.jsonl` (bd's own `--claim` bookkeeping) and this file.

No commit/push/sync performed (conservative git policy; not asked to).

## Bead disposition

Left OPEN at P4. This session made real, quantified progress narrowing the
gap (single ambiguous near-win vs. the prior session's 3-way muddle) and
newly confirmed a live example of the cross-node ripple risk with a concrete
number (the "nonzero" collision), but the bead's stated acceptance bar
(correctly recover `judson:11.1`, not just abstain) is still not met, and
nothing in the working tree changed. Closing this P4 bug now would
misrepresent "narrowed, not closed" as "done."
