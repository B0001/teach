# teach-8xw.25 — fact_checker: synonym for 'codomain' makes a false kernel-normality claim verify CONFIRMED instead of CONTRADICTED

## Decision: closed. Literal repro fixed; a structural fix (not just synonym
widening) eliminated the dangerous direction across two independent blind
generalization rounds; the Lagrange audit found the same disease absent
there, plus a real but *safe*-direction coverage gap, disclosed and filed
separately as teach-8xw.33.

## Reproduced first

Ran the bead's exact repro against `main` before touching anything:

```
verify_claim("... normal subgroup of the target group.", MATH_SOURCE)   -> CONFIRMED  (should be CONTRADICTED)
verify_claim("... normal subgroup of the range of the map.", MATH_SOURCE) -> CONFIRMED  (should be CONTRADICTED)
verify_claim("... normal subgroup of the codomain.", MATH_SOURCE)       -> CONTRADICTED (correct — literal fixture word)
verify_claim("Kernels are always normal subgroups of the domain.", MATH_SOURCE) -> CANNOT_VERIFY (should be CONFIRMED)
```

Confirmed exactly as described: `\bkernel\b` never matches inside "kernels"
(no word boundary between "l" and "s"), and `_KERNEL_NORMAL_SUBGROUP`'s
`false_patterns` were keyed to the literal word "codomain" only.

## What was built

### 1. Literal-repro fix (`teach/math_facts.py`)

- `topic_patterns`/`false_patterns`/`true_patterns` for
  `_KERNEL_NORMAL_SUBGROUP` now match `\bkernels?\b` instead of `\bkernel\b`,
  fixing the plural-miss.
- Added `_CODOMAIN_SYNONYMS`, an alternation covering `codomain`, `target`/
  `target group`, `range`/`range of the {map,homomorphism,function}`, used
  everywhere `false_patterns` previously hard-coded the bare word
  `codomain`.

This alone fixes the bead's four literal reproduction lines.

### 2. Measured generalization, round 1 (blind Agent, no repo access)

Per this repo's standing method note (a same-session self-authored set is
never held-out evidence), spawned an `Agent` with no filesystem access,
told only the mathematical content of the false claim, asked to paraphrase
it in 12 varied, independently-worded sentences.

**Before adding `_CODOMAIN_SYNONYMS`'s wider set** (codomain/target/range
only): 5/12 CONTRADICTED, 5/12 CANNOT_VERIFY, **2/12 CONFIRMED — the
dangerous failure, on new synonyms** ("receiving group", "receiving end of
the map").

Widened `_CODOMAIN_SYNONYMS` to add `receiving (group|end [of the
{map,homomorphism,function}])` and `output group`, found by reading what
the blind agent actually wrote — not guessed in advance. Re-ran the same
12 sentences: 8/12 CONTRADICTED, 4/12 CANNOT_VERIFY, **0/12 CONFIRMED**.

### 3. Measured generalization, round 2 (second blind Agent, forbidden vocabulary)

Widening the synonym list only proves it covers what round 1 happened to
say — the exact failure mode documented across the `potential_checker`
lineage (teach-yn8 → teach-kmm → teach-5gf → teach-8xw.19/20/23 → teach-9k5).
So a **second** blind Agent call, explicitly forbidden from using any word
already added (`codomain`, `target`, `range`, `receiving`, `output`), was
asked to paraphrase the identical false claim using structural/naming
tricks instead (`H` as a stand-in name for the codomain, "where the arrows
point to", "the group being mapped into").

Against the **synonym-widened** checker (before the fix in step 4 below):
0/12 CONTRADICTED, 10/12 CANNOT_VERIFY, **2/12 CONFIRMED — dangerous, and
unfixable by adding two more synonyms without repeating the same failure
next round.**

### 4. Structural fix: default-to-abstain instead of default-to-confirm

The actual bug is not "missing synonyms," it's the polarity of the
fallback. `true_patterns` for the kernel topic used to be
`kernel ... is/are ... normal` with **no constraint on which group at
all** — so any sentence that dodged the (necessarily incomplete)
`false_patterns` enumeration fell through to CONFIRMED by default. That is
backwards from sandbox-prompt.md's "prefer abstention to a confident
answer," and it's why widening synonyms can reduce but never zero out the
dangerous direction: English has unboundedly many ways to name "the wrong
group" and only the enumerated ones get caught.

Fixed the default instead of the enumeration: `true_patterns` now requires
an **explicit "domain" mention** to confirm. Anything that names some
other/ambiguous group — enumerated synonym or not — no longer defaults to
CONFIRMED; it abstains (CANNOT_VERIFY) unless a `false_pattern` already
caught it as a known wrong-group phrasing.

Re-ran **both** blind rounds against this fix:

- Round 1 (12 sentences): unchanged, 8/12 CONTRADICTED, 4/12 CANNOT_VERIFY,
  **0/12 CONFIRMED**.
- Round 2 (12 sentences, forbidden vocabulary): 0/12 CONTRADICTED, **12/12
  CANNOT_VERIFY, 0/12 CONFIRMED** — the two dangerous cases from step 3
  ("H is the group being mapped into...", "...lives where the arrows point
  to...") now abstain instead of confirming.

Net, across 24 independently-authored sentences from two separate blind
agents (neither of which saw this session's code, patterns, or each
other's output): **0/24 dangerous false-CONFIRMED**, both before and after
the exact vocabulary each round happened to use. That's the property this
bead actually needed — not "catches every paraphrase" (it still doesn't:
round 2's catch rate is 0/12), but "never certifies a false claim as
CONFIRMED just because its phrasing wasn't anticipated."

### 5. Audited the other topic (Lagrange) for the same disease

`_LAGRANGE_ORDER_DIVIDES`'s `true_patterns` already require the exact
positive-direction phrase structure (`order of subgroup ... divides ...
order of group`, in that order) — it does **not** default-confirm on bare
topic match the way the kernel topic used to. So a blind-agent round of 12
independently-authored paraphrases of the reversed-direction false claim
(using "cardinality," "size," "goes into," "container/contained" instead
of the literal "order"/"divides subgroup/group" phrasing) landed **0/12
CONTRADICTED, 12/12 CANNOT_VERIFY, 0/12 CONFIRMED**. Real coverage gap,
safe direction — not the bug this bead is about. Filed as **teach-8xw.33**
(P2) rather than fixed here, since fixing it means the same
widen-then-blind-verify cycle as the kernel topic and this bead's scope is
the kernel/codomain bug specifically.

## Test changes

`tests/test_fact_checker.py` — 8 new tests, all passing, none removed or
weakened:

- `test_kernel_normal_in_target_group_synonym_is_contradicted` — bead's
  literal repro (target group).
- `test_kernel_normal_in_range_of_the_map_synonym_is_contradicted` — bead's
  literal repro (range of the map).
- `test_kernel_plural_true_claim_is_confirmed_not_missed` — bead's
  secondary finding (plural "Kernels").
- `test_kernel_normal_in_receiving_group_synonym_is_contradicted` — a third
  synonym the round-1 blind agent actually used.
- `test_kernel_normal_in_unenumerated_wrong_group_phrasing_abstains_not_confirms`
  — round-2 blind sentence ("H is the group being mapped into..."), locking
  in abstain-not-confirm.
- `test_kernel_normal_structural_wrong_group_description_abstains_not_confirms`
  — round-2 blind sentence ("...lives where the arrows point to..."), same
  lock.
- `test_lagrange_reversed_direction_paraphrase_without_literal_vocabulary_abstains`
  — Lagrange audit finding, locking in the safe-direction disclosure so a
  future change can't silently make it CONFIRMED.

`teach/math_facts.py` — inline comments at `_CODOMAIN_SYNONYMS` and the
kernel topic's `true_patterns` document *why* (not just what), per repo
convention, including the specific blind-round numbers that motivated each
change, so the next worker doesn't have to re-derive them from git blame.

## Verification

- `uv run pytest -q` — 199 passed (191 baseline + 8 new). No existing test
  changed or removed.
- `uv run python3 -m teach.math_facts` — self-check passes.
- `uv run python3 -m teach.fact_checker` — self-check passes.
- Bead's exact repro re-run against the fixed code: all four lines now give
  the correct verdict (CONTRADICTED/CONTRADICTED/CONTRADICTED/CONFIRMED).

## What was NOT done, and why it's not a gap in this close

- Did not attempt to make the kernel topic's *recall* on unenumerated
  false phrasing better than round 2's 0/12 — that would mean either (a)
  another synonym-widening cycle fitted to round 2's specific wording,
  which is exactly the self-defeating pattern this method note exists to
  block, or (b) a genuinely different mechanism (semantic role labeling:
  "which group does this claim assign the kernel to, and is it the
  domain") that's a real design decision, not a bug-fix-bead-sized change.
  The bead's danger-direction requirement is met (0/24 dangerous across
  both rounds); residual under-recall is the safe, disclosed failure mode
  sandbox-prompt.md explicitly prefers over guessing.
- Did not fix the Lagrange coverage gap — filed as teach-8xw.33 instead,
  since it's the same widen-then-reverify cycle and out of this bead's
  named scope (the codomain-synonym bug).
- Did not change `false_patterns` structure or the false-before-true
  ordering in `fact_checker.py` itself — the fix lives entirely in
  `math_facts.py`'s per-topic pattern data, consistent with the
  domain-plugin boundary the module's docstring describes.

## Caveat for whoever reads this next

The two blind-agent rounds are real held-out evidence, but it is still
only two rounds from one session. "0/24 dangerous" is what was measured,
not a proof that no phrasing exists that would still slip through
`true_patterns`' `domain`-mention requirement while asserting something
false (e.g., a sentence that mentions the word "domain" in an unrelated
clause while actually asserting the wrong-group claim elsewhere — not
tested here, and plausible). If a future session finds such a case,
that's a new, narrower bug in the `true_patterns` regex, not a reason to
reopen this bead's broader claim: the *default-to-abstain* structural
change is what generalized across two rounds where *synonym-widening*
plateaued after one, and that mechanism argument holds independent of
whether every possible edge case has been found yet.
