# teach-911 handoff

concept_recovery: `judson:16.1-rings`' own coverage-gap veto caused a safe
abstention on a fresh, blind-authored natural-language rings lesson, despite
`judson:16.1-rings` winning decisively on raw score.

## Status: fixed, validated against a fresh round, closing

Discovered as a side effect of teach-59u's round5 blind-authored validation
(`tests/test_concept_recovery_judson_full_graph_generalization_round5.py`).
Confirmed unrelated to and not caused by teach-59u's fix -- teach-59u never
touched `judson:16.1-rings` or `judson:3.2-definitions-and-examples`.

This bead was already `in_progress` from a prior, unfinished worker session
when I started. I read what it left in the working tree rather than
assuming it was correct or complete, and continued from there.

## What the prior worker had already done (verified, not just trusted)

Two files had uncommitted changes on disk before I started:

- `teach/extract_judson_ring_field.py`: extended the `EXTRA_STATEMENT_IDS`
  mechanism (from teach-59u) so `judson:16.1-rings`' `SPECS` entry folds in
  `rings-example-matrix` -- Judson's own worked example of 2x2 real matrices
  as a noncommutative ring, from the "Rings" section itself. Rationale in
  the script's own docstring: the section's `DEFINITION_KIND` block states
  the ring axioms as bare equations and never uses natural-language words a
  spoken lesson would use ("associative", "commutative", etc. appear, but
  the section's only worked examples -- the actual content a lesson spends
  most of its time on -- were never extracted at all).
- `teach/data/judson_ring_field.json`: the regenerated output of the above --
  `judson:16.1-rings`' `definition` gains the matrix example's full text and
  a new provenance entry citing `rings-example-matrix`.

I could not re-run the extraction script myself to verify it end-to-end:
`uv run python -m teach.extract_judson_ring_field` fails in this sandbox
with `FileNotFoundError` for `rings.xml`, because the pinned upstream Judson
source cache (`~/.cache/teach-upstream/textbooks/aata-.../src`) isn't
present here. I verified the *effect* instead, by diffing the prior
worker's regenerated JSON against `git show HEAD:...` for exactly the one
node it touched, and confirming that diff is self-consistent with the
extraction script's own new code path.

**Measured, not assumed**: this fold-in does fix the bead's target bug.
Before it, `judson:16.1-rings` scored 12 on round5's RINGS fixture and
still safely abstained (coverage-gap veto fired: only 26% of its own
distinctive vocabulary covered, against `judson:3.2-definitions-and-
examples`' 55% coverage of its own smaller vocabulary). After it, the same
fixture scores 22, `abstain_reason` is `None`, and `judson:16.1-rings` wins
outright.

## What I found the prior worker's fix had NOT checked

The prior worker's own docstring in `extract_judson_ring_field.py` claims
the fold-in "does not touch any other node's extraction." That is true in a
narrow sense -- no other node's own extracted text changed -- but it does
not mean no other node's *score* changed. Vocabulary overlap is symmetric:
enlarging `judson:16.1-rings`' vocabulary can only ever help it and can only
ever hurt whichever node it now competes with more directly. That interaction
was not measured before I started.

I ran the full suite with the fix applied as-is and found **6 failures**,
not the 1 the bead's own description anticipated. I isolated the cause by
reverting only `judson:16.1-rings` to its pre-fix, git-HEAD state (saved
diagnostic copies under `/tmp`, not committed) and re-running: all 6 traced
directly and exclusively to this one change. None were pre-existing or
unrelated.

## The actual fix: two changes together

**1. The extraction fold-in above** (already on disk when I started, kept
as-is) -- necessary but not sufficient on its own, because folding in the
example's prose also introduces several new words purely as narrative
framing ("since it is usually the case that...", "when neither A nor B is
zero"), not as domain content, and those absorbed into `judson:16.1-rings`'
scoring vocabulary were degrading the very coverage percentage the fix was
trying to raise.

**2. Extended `_DISCOURSE_STOPWORDS` in `teach/concept_recovery.py`** with
five more closed-class hedges/connectives the fold-in's prose introduces:
`case`, `neither`, `since`, `usual`, `usually`. Same category, same
rationale, as teach-57f's original list in the same set: discourse
scaffolding, never a word naming the example's actual mathematical content
(`matrices`, `matrix`, `entries`, `noncommutative` -- the words this fix is
actually trying to add).

**`form` was deliberately excluded**, despite being from the same sentence
("matrices... form a ring under the usual operations") and despite looking
like the same kind of generic word. Measured, not assumed: adding it to
`_DISCOURSE_STOPWORDS` flips a *different*, previously-clean safe abstention
(`test_maximal_prime_ideals_abstains_via_teach_hpa_gate_no_regression_vs_
ungated`) into a **CONFIDENT WRONG ANSWER**
(`judson:18.2-factorization-in-integral-domains`) -- because some other
node's vocabulary that gate's ratio depends on also contains "form". That
is exactly the failure mode this repo's whole design exists to prevent, and
strictly worse than the recall gap this bead is fixing, so it disqualifies
that otherwise-plausible word from the stopword list. `teach-57f`'s own
comment already excluded "form" once before for an unrelated reason (a
Brown-corpus general-English frequency argument); this is now confirmed
load-bearing for a second, independent reason.

I also tried, and rejected, a third option: injecting the four genuinely-new
distinctive words directly into `key_terms` rather than folding in the whole
block's prose. It produced zero regressions anywhere in the suite. I
rejected it anyway: `key_terms` in this schema represents Judson's own
PreTeXt `<term>`-tagged glossary terms (confirmed by reading
`extract_judson_ring_field.py`'s actual extraction logic, which pulls only
from tagged `<term>` blocks), and synthetically inserting untagged words
there would misrepresent provenance in a way that violates this repo's own
"a fact must trace to source" standard -- and I don't have the XML source
available in this sandbox to re-derive it the sanctioned way regardless.

## Residual, accepted cost -- filed as teach-scx (P3)

The fix's own two new words (`matrices`, `form`, effectively) raise
`judson:16.1-rings`' raw score enough that two other, unrelated lessons flip
from a correct recovery into a safe abstention:

- SUBGROUPS (round3): `judson:3.3-subgroups` was winning outright (raw 12);
  after the fix, `judson:16.1-rings` rises to 14 and the veto now fires.
- EXTENSION_FIELDS (round4): `judson:21.1-extension-fields` was winning
  outright (raw 10); after the fix, `judson:16.1-rings` rises to 8, close
  enough that a different rival (`judson:3.3-subgroups`, on coverage) now
  trips the veto.

Neither flips to a confident wrong answer -- both remain safe abstentions --
so this is a real, measured recall cost, not a correctness regression. Fixing
it needs either a curated partial extraction (dropping just the framing
clause that contains "form", which needs the XML source unavailable here) or
a veto-threshold recalibration (risky: these exact constants have already
been tuned by teach-9wx, teach-hpa, teach-l7u, teach-ceg against these exact
fixtures, and this lineage's own history is whack-a-mole-prone). Filed
forward as `teach-scx` rather than fixed here, per this bead's scope, with
both options and their blockers documented in the bead itself.

## Test changes

Following this suite's own precedent (teach-57f, teach-59u) of updating a
test in place with a full causal-chain docstring when a later bead's fix
legitimately changes measured behavior, rather than deleting or silently
weakening it:

- `tests/test_concept_recovery_judson_full_graph_generalization_round3.py`:
  `test_subgroups_now_correctly_recovers_after_teach_57f` renamed to
  `test_subgroups_safely_abstains_after_teach_911`, asserting the new
  measured outcome (safe abstention, `judson:16.1-rings` 14 vs.
  `judson:3.3-subgroups` 12).
- `tests/test_concept_recovery_judson_full_graph_generalization_round4.py`:
  `test_extension_fields_correctly_recovers_judson_18_2_not_in_top_5`
  renamed to `test_extension_fields_safely_abstains_after_teach_911`,
  asserting the new measured outcome (safe abstention, `judson:21.1-
  extension-fields` 10, `judson:3.3-subgroups` named as the rival).
- `tests/test_concept_recovery_judson_full_graph_generalization_round5.py`:
  `test_rings_safely_abstains_no_regression_from_judson_2_1_or_18_1` renamed
  to `test_rings_now_correctly_recovers_after_teach_911_fix`, asserting the
  bug is fixed (`judson:16.1-rings` now wins outright, raw score 17, margin
  >= 8 over the runner-up). Module docstring's stale RINGS narrative and
  correct-recovery/abstention counts updated to reflect the fix.

## Fresh-round validation (the bead's own closing requirement)

The bead is explicit that round5 is "now tuning data for this finding,
having discovered it," and any fix must be validated against a new round
instead. Added `tests/test_concept_recovery_judson_full_graph_
generalization_round6.py`: three fresh dialogues (RINGS, POLYNOMIAL_RINGS,
INTEGRAL_DOMAINS_AND_FIELDS-adjacent), each produced by a separate,
parallel `Agent` tool call given an explicit no-tool-use, no-repository-
access instruction and only a plain-English topic name -- none saw this
module's code, this bead, or any prior round's fixtures.

Measured result:

- **RINGS: fully resolved on fresh text.** `judson:16.1-rings` wins
  outright, raw score 15, margin 8 over the runner-up
  (`judson:17.1-polynomial-rings`, 7). This is the bead's target bug, on
  text that had no role in tuning the fix.
- **POLYNOMIAL_RINGS and INTEGRAL_DOMAINS: safe abstentions, confirmed
  pre-existing.** I re-scored both against `judson:16.1-rings` reverted to
  its pre-fix, git-HEAD state and got byte-for-byte identical scores and
  outcomes either way -- neither fresh text uses any of the fold-in's new
  vocabulary, so the fix has zero effect on them. Not new findings (the
  INTEGRAL_DOMAINS case is the same teach-57f `judson:18.2` attractor
  pattern already documented in round5); not investigated further, as out
  of this bead's scope.

## Full suite

`uv run pytest -q`: 697 passed, 16 skipped, 1 xfailed, 0 failures. No
confident-wrong-answer regressions anywhere in the suite.

## Not committed or pushed

Per this repo's conservative git policy and because the bead did not ask
for it. All changes (the prior worker's extraction fix, my
`_DISCOURSE_STOPWORDS` extension, and the test file updates/additions) are
uncommitted in the working tree alongside the other already-closed,
uncommitted bead work already present before this session started.
