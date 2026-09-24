# teach-59u handoff

concept_recovery: `judson:2.1-the-division-algorithm` and
`judson:18.1-fields-of-fractions` scored too low or didn't appear at all
against ring/field-family sibling nodes on fresh natural-language dialogue
text -- a recall gap (a correct node scoring too LOW), the mirror image of
teach-57f's precision problem (a wrong node scoring too HIGH).

## Status: fixed (division algorithm fully, fields of fractions measurably
but not fully) and closing with a follow-up bead filed

Filed forward from teach-57f's round4 (see `sandbox-handoffs/teach-57f.md`),
which found both gaps as a side effect of its own fresh validation round but
explicitly left them unfixed, correctly diagnosing them as a different
problem needing a different fix ("enriching thin nodes' vocabulary, not
filtering rich ones").

## Root cause, per node

**judson:2.1-the-division-algorithm**: the node's hand-authored
`key_terms`/`definition` in `teach/judson_algebra_graph.py` stated the
division algorithm without ever naming what makes it a *theorem* rather than
a mere fact -- existence and uniqueness of the quotient/remainder pair. A
natural dialogue about the division algorithm uses exactly that vocabulary
("there exists...", "unique", "uniquely determined") and the old node text
gave the checker none of it to match against, so sibling nodes with more
generic ring-family vocabulary (judson:17.1-polynomial-rings,
judson:18.2-factorization-in-integral-domains) outscored the correct node
outright.

**judson:18.1-fields-of-fractions**: mechanical, not wording. The Judson
source's "Fields of Fractions" section has exactly one `<term>`-bearing
paragraph, and it is a bare cross-reference ("The field $F_D$ in [xref] is
called the field of fractions...") rather than a self-contained definition
-- it names the term but states nothing of what $F_D$ actually is. The
extractor (`teach/extract_judson_ring_field.py`) only ever pulled
`DEFINITION_KIND` blocks, so it never saw the lemma/theorem blocks
(`domains-lemma-field-of-fractions`, `domains-theorem-field-of-quotients`)
that spell out the actual content (equivalence classes, defined operations,
the field property, the embedding of $D$ in $F_D$). Measured before the fix:
judson:18.1's distinctive vocabulary was 3 words -- "fractions", "integral",
"quotients" -- the smallest node in the graph, unable to compete with any
larger sibling on a lesson that didn't happen to reuse those exact three
words verbatim.

## Fixes applied

**judson:2.1** (`teach/judson_algebra_graph.py`): added `"existence"`,
`"uniqueness"` to `key_terms`; reworded `definition` to state the theorem as
an existence-and-uniqueness result explicitly: "...there is a quotient q and
a remainder r, uniquely determined, such that a = bq + r ... -- an
existence-and-uniqueness theorem: both that such q and r exist, and that
they are the only ones that work, are what make the Euclidean algorithm ...
terminate with a single, well-defined answer."

Final `key_terms`: `("divides", "divisor", "division algorithm", "greatest
common divisor", "relatively prime", "Euclidean algorithm", "prime",
"quotient", "remainder", "existence", "uniqueness")`.

**judson:18.1** (`teach/extract_judson_ring_field.py`): added an
`extra_statement_ids` mechanism to `SPECS` -- a 6th tuple element naming
theorem/lemma blocks (by `xml:id`, so a later source edit that moves or
retitles a section can't silently swap in the wrong one) whose `<statement>`
text is folded into the node's `definition` and `terms`, alongside the
`DEFINITION_KIND` blocks every other node already uses. judson:18.1's spec
now names `("domains-lemma-field-of-fractions",
"domains-theorem-field-of-quotients")`. Proof text is deliberately excluded
-- a block's *statement* is what defines the term; its *proof* is how you'd
verify the definition holds; the vocabulary that identifies which concept a
lesson is about lives in the former. This is a general mechanism (any future
node with the same "bare cross-reference" problem can use it), not a
judson:18.1-specific hack, and touches no other node's already-working
extraction (`extra_statement_ids` defaults to `()` everywhere else).

Regenerated `teach/data/judson_ring_field.json` via
`uv run python -m teach.extract_judson_ring_field`.

## Derived-artifact trap discovered mid-session

`teach/data/learning_commons_export/{nodes.jsonl,relationships.jsonl,
manifest.json}` is a committed, derived dataset that combines BOTH the Levin
foundational graph (CC BY-SA 4.0) and the Judson graph (GFDL 1.3+) into one
"Learning Commons"-schema export -- any change to Judson node text changes
these files' bytes, so they go stale whenever the Judson graph changes.
`test_learning_commons_export.py`'s drift-guard test caught this
immediately.

**Trap**: `uv run python -m teach.learning_commons_export` (no flag) prints
a success-looking `"OK: 32 LearningComponent nodes..."` message but writes
**nothing** to disk -- confirmed via `git status --short` (no changes) and
file mtimes (unchanged). Reading the module's `if __name__ == "__main__":`
block shows why: without `--write` it calls `_self_check()`, a read-only
validator, not `main()`, the actual writer. Correct regeneration command:
`uv run python -m teach.learning_commons_export --write`. Worth a docstring
note in that module for the next person who hits this; not fixed here
(out of scope for this bead, and the module's own behavior is arguably
correct/intentional -- just easy to trip over).

## A regression this fix introduced, found and fixed mid-session

My first attempt at the judson:2.1 wording added the bare word `"unique"` to
both `key_terms` and `definition`. `concept_recovery.py` filters any word
appearing in **more than** `_MAX_DOCUMENT_FREQ = 4` nodes graph-wide as
boilerplate, for *all* nodes, not just the over-represented ones -- a
cross-cutting, shared-resource mechanism (this is the same mechanism
teach-57f's handoff describes hitting from the other direction). `"unique"`
was already at document-frequency 3 (judson:16.1, judson:18.2, judson:21.1)
before this bead; judson:18.1's own extraction fix legitimately added a 4th
use (via the folded-in theorem statement) -- still within threshold. Adding
a 5th, hand-authored use in judson:2.1 pushed it over, silently stripping
`"unique"` from **all five** nodes that used it. Caught by the full suite:
`test_isomorphisms_abstains_via_preexisting_multi_candidate_tie_not_teach_9wx`
in round2 unexpectedly failed, despite that test's text having nothing to do
with the division algorithm -- root-caused via a throwaway document-
frequency diagnostic script (not committed) and confirmed by reproducibly
reverting/reapplying the patch (`git diff -- <files> > patch; git apply -R
patch; git apply patch` -- `git stash` fails with a "dubious ownership"
error in this sandbox that I did not work around, per the standing "never
update git config" rule).

**Fix**: reworded to `"uniquely determined"` (word: `"uniquely"`, doc_freq
0 before this bead) instead of the bare `"unique"`, and removed `"unique"`
from judson:2.1's `key_terms` (kept `"existence"`, `"uniqueness"`, both also
unclaimed elsewhere and carrying the same meaning without collision).
Re-verified via the same diagnostic that `"unique"` is back to
document-frequency 4 (exactly at, not over, threshold) and the round2 test
passes again.

## Fresh held-out validation round (round5)

Per this bead's own explicit requirement (round4, round3, round2, and
teach-443's fixture edits are all tuning data and must not be reused): five
fresh dialogues authored via five separate, parallel, blind `Agent` tool
calls (no repo/tool access, no knowledge of this bead, concept_recovery.py
internals, or any prior round's fixtures -- only a plain-English topic name
and a request for a natural 300-400 word tutor/student dialogue).
Persisted as
`tests/test_concept_recovery_judson_full_graph_generalization_round5.py`.
Topics: the division algorithm, fields of fractions, rings, integral
domains and fields, polynomial rings (this bead's two target topics plus
the sibling nodes the fix must not regress).

**Honest measured result**, against the real, unmodified
`load_judson_full_graph()`, no threshold or word list changed in response to
seeing these numbers:

- correct recoveries: 2/5 (DIVISION_ALGORITHM, POLYNOMIAL_RINGS)
- safe abstentions: 3/5 (FIELDS_OF_FRACTIONS, RINGS,
  INTEGRAL_DOMAINS_AND_FIELDS)
- confident wrong answers: 0/5

**DIVISION_ALGORITHM: fully resolved.** judson:2.1 now wins decisively --
raw score 11, margin >=4 over the runner-up, correct `taught_node_id`, no
abstention. This is the fresh-data confirmation that the vocabulary fix
(not just this file's own re-worded tuning text) actually closes the gap.

**FIELDS_OF_FRACTIONS: measurably improved, not fully resolved.**
judson:18.1 went from invisible pre-fix (below the match floor on
comparable text) to a genuine contender: raw score 9, present in the top 5,
named in the final "too close to call" abstain set -- but still ties with
judson:16.1-rings at score 10 rather than winning outright, so the result is
a safe abstention, never a confident wrong answer. The extraction fix
narrows the gap (3-word vocabulary -> a real, competitive vocabulary) but a
lesson that emphasizes the field-of-fractions construction in different
words than the Judson source's lemma/theorem statements can still tie with
a larger sibling node. This is an honest partial result, consistent with
teach-57f's own precedent of accepting a "no longer inflated/no longer
invisible, but not perfectly disambiguated" outcome as real progress rather
than full closure.

**Sibling topics (RINGS, INTEGRAL_DOMAINS_AND_FIELDS, POLYNOMIAL_RINGS):
no new false-positive attractor introduced.** Neither judson:2.1 nor
judson:18.1 wins outright or is named as a contender in any of these
topically-unrelated abstain reasons:

- RINGS top6: judson:16.1-rings 12, judson:17.1-polynomial-rings 9,
  judson:18.2-factorization-in-integral-domains 8,
  judson:16.3-ring-homomorphisms-and-ideals 7,
  judson:3.2-definitions-and-examples 6, judson:16.2-integral-domains-
  and-fields 5. judson:2.1/18.1 don't appear at all in the top 6. **This
  text safely abstains too**, but for a reason unrelated to this bead --
  see "Follow-up bead filed" below.
- INTEGRAL_DOMAINS_AND_FIELDS top6: judson:18.2 11, judson:16.2 10,
  judson:16.1 9, judson:16.3 6, judson:2.1 6 (tied 5th, low score, not
  named as a contender), judson:18.1 4 (tied 6th, low score, not named).
  This is the already-known teach-57f judson:18.2 attractor pattern
  recurring, not a new problem.
- POLYNOMIAL_RINGS: correct recovery (judson:17.1, score 14), neither
  judson:2.1 nor judson:18.1 in the top 6.

## Follow-up bead filed

**teach-911** (P2, discovered from round5, out of scope for teach-59u):
the RINGS dialogue -- squarely about judson:16.1-rings -- safely abstains
despite judson:16.1 leading its own raw-score ranking by a wide margin (12
vs. runner-up 9), because the final abstain logic's decisive-margin
coverage-gap veto fires: judson:16.1's own distinctive vocabulary is covered
too thinly by this lesson relative to how much of *its own* vocabulary a
lower-scoring rival covers. Confirmed unrelated to and not caused by this
bead's fix (judson:16.1 and judson:3.2 were not touched). Likely the same
family of root cause as this bead (a node's own extracted vocabulary too
thin or mismatched relative to how a natural lesson on that exact topic
would phrase things, even while winning on raw score) -- filed forward
rather than fixed here, since it needs its own fresh held-out round once
attempted (round5 is now tuning data for this specific finding, having
discovered it).

## Test suite impact

Baseline before this session's fixes (from the working tree at claim time,
which already carried other unrelated uncommitted changes from
already-completed teach-57f/teach-443 work): 2 failed (both round4 tests
whose measured scores this fix legitimately shifted), rest passing.

Both round4 failures were diagnosed by directly querying
`recover_from_lesson_text`/`score_candidates` for the actual post-fix
scores and abstain branch, confirmed as legitimate traceable consequences
of the fix (not new wrong-confident-answer regressions), and updated per
this repo's established precedent (teach-57f's and teach-443's own
handoffs) of renaming/redocumenting a test when a correctness fix
legitimately shifts which outcome results, rather than reverting the fix or
force-patching the assertion:

1. `test_division_algorithm_safely_abstains_with_judson_18_2_still_a_close_rival`
   -> renamed `test_division_algorithm_now_correctly_recovers_after_teach_59u_fix`.
   Score went from safe-abstention to a decisive correct recovery (raw
   score 16, margin >=7 over runner-up on this file's text). Full rewrite,
   docstring explicitly flags this file's text as now-superseded tuning
   data and points to round5 for real validation.
2. `test_fields_of_fractions_safely_abstains_judson_18_2_present_but_not_named`
   -> renamed `test_fields_of_fractions_measurably_improved_after_teach_59u_fix`.
   judson:18.1 went from absent from the raw top 5 (score 2) to present and
   named in the abstain reason (score 7, tied with judson:18.2 among five
   candidates) -- still a safe abstention on this text, same "measurably
   improved, not fully resolved" story as round5's fresh measurement.
   Docstring updated, assertions inverted to match (was asserting
   judson:18.1 absent; now asserts it's present and named).

An "UPDATE (teach-59u)" paragraph was appended to round4's module-level
historical docstring summarizing both changes and reiterating that this
file's text remains tuning data, not validation evidence, for this fix.

Full suite after these two fixture updates plus the new round5 file:
**624 passed, 16 skipped, 5 xfailed, 0 failures.**

## Files touched

- `teach/judson_algebra_graph.py` -- judson:2.1's `key_terms` and
  `definition` reworded (existence/uniqueness vocabulary added, without the
  bare word "unique" -- see the document-frequency regression above).
- `teach/extract_judson_ring_field.py` -- new `extra_statement_ids`
  mechanism in `SPECS`; judson:18.1's spec updated to fold in
  `domains-lemma-field-of-fractions` and
  `domains-theorem-field-of-quotients`.
- `teach/data/judson_ring_field.json` -- regenerated
  (`uv run python -m teach.extract_judson_ring_field`).
- `teach/data/learning_commons_export/{nodes.jsonl,relationships.jsonl,
  manifest.json}` -- regenerated
  (`uv run python -m teach.learning_commons_export --write`), a derived
  dataset embedding Judson node text that would otherwise silently drift
  stale.
- `tests/test_concept_recovery_judson_full_graph_generalization_round4.py`
  -- two tests renamed/rewritten reflecting shifted (now-correct / now-
  improved) outcomes; one UPDATE paragraph appended to the module's
  historical docstring.
- `tests/test_concept_recovery_judson_full_graph_generalization_round5.py`
  -- new file, the fresh held-out validation round required to close this
  bead.

## Git

Not committed or pushed -- conservative git policy, not asked to do so this
session. `git status --short` will show the files above as modified/new,
plus this handoff file, `.beads/` sync state, and untracked
`sandbox-handoffs/*.md`/other in-flight files from prior, already-completed
but uncommitted sessions (teach-57f's `_DISCOURSE_STOPWORDS`/
`_LATEX_COMMAND` work, round2/round3 fixture edits) that predate and are
unrelated to this session's changes.

## Full suite

Final run: `uv run pytest -q` -> **624 passed, 16 skipped, 5 xfailed, 0
failures**.
