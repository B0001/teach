# teach-8xw.34 handoff

## What this bead was

A dangerous false-CONFIRMED bug in `_LAGRANGE_ORDER_DIVIDES`
(`teach/math_facts.py`), distinct from teach-8xw.33's recall-gap finding.
`true_patterns[1]` is a loose, direction-agnostic fallback
(`\blagrange\b.{0,120}\bdivides\b`) that fires on *any* sentence containing
both words, with no direction check. The only thing standing between that
and a false CONFIRMED on a reversed (false) claim is `false_patterns`
catching the reversed direction first (`verify_claim` checks
`false_patterns` before `true_patterns`). But the two literal reversed-
direction patterns (`false_patterns[1]` and `true_patterns[0]`) each had
their own inline `(?:the |a |any )?` determiner list instead of sharing
`_ANY_DETERMINER` — so a claim phrased with a possessive ("its subgroups",
"their subgroups", "any of its subgroups") slipped past both, fell through
to the loose fallback, and landed `Verdict.CONFIRMED` on a **false** claim.

## Root-cause detail

`_ANY_DETERMINER` (extended in teach-8xw.33 to add "every"/"each"/"all")
was itself never the problem for the *synonym-based* false_patterns
(`false_patterns[2]`/`[3]`, built from `_BIG_SIZE`/`_SMALL_SIZE` via
`_size_phrase()`) — those already route through `_ANY_DETERMINER`. The bug
was specifically that `false_patterns[1]` (the literal "order of the group
... divides ... order of the subgroup" pattern) and `true_patterns[0]` (the
literal correct-direction pattern) had their own separate, un-synced
`(?:the |a |any )?` list, so any fix to `_ANY_DETERMINER` alone would not
have reached them. The bead explicitly called this out: route them through
`_ANY_DETERMINER` "so the fix isn't a second competing determiner list."

## Fix

1. Extended `_ANY_DETERMINER` in `teach/math_facts.py` to recognize
   possessive determiners (`its`, `their`) and the compound
   quantifier+possessive form (`any of its`, `each of their`, ...), built
   generatively as `(quantifier (of possessive)?) | possessive` rather than
   enumerating every quantifier×possessive pair by hand — so a future
   quantifier added to the first group automatically gets the possessive-
   compound form too, and there's one determiner vocabulary, not several.
2. Rewired `false_patterns[1]` and `true_patterns[0]` (the two literal
   patterns) to use `_ANY_DETERMINER` instead of their own inline list, and
   made `group`/`subgroup` accept the plural form (`groups?`/`subgroups?`)
   they were silently missing too (`subgroup\b` doesn't match inside
   "subgroups" — no word boundary after "subgroup" when followed by "s").
3. Did **not** touch `true_patterns[1]`'s loose fallback itself. The bead's
   own "what would close this" section scoped the fix to the determiner gap,
   not to removing the fallback — and with the determiner gap closed, every
   reported reproduction case is now caught by `false_patterns` before ever
   reaching that fallback, per `verify_claim`'s false-before-true ordering.
   The fallback remains a residual landmine for as-yet-unenumerated reversed
   phrasings; that's the same disclosed open-ended-English ceiling already
   accepted elsewhere in this file, not something this bead's scope covers.

## Verification

- Reproduced the exact bug first, against unmodified code:
  `"Lagrange's theorem: the order of the group divides the order of its
  subgroups."` → `Verdict.CONFIRMED` (wrong — should be CONTRADICTED).
  `"...divides the order of any of its subgroups."` → also `CONFIRMED`.
  Also reproduced through `teach/cialdini.py`'s `render_authority` AUTHORITY
  move exactly as the bead's repro showed, confirming this is reachable
  from a real producer code path.
- After the fix, both reproduction sentences and the `render_authority`
  path all return `Verdict.CONTRADICTED`. A control possessive sentence in
  the *correct* direction (`"the order of its subgroups divides the order
  of the group"`) still returns `Verdict.CONFIRMED` — the fix only rejects
  the reversed direction, it doesn't make the checker abstain on correct
  possessive phrasing.
- Full suite: `uv run pytest -q` → 271 passed (was 265 before; +6 new
  regression tests). Module self-checks (`python3 -m teach.math_facts`,
  `teach.fact_checker`, `teach.cialdini`) all still pass.
- **Held-out measurement, not self-authored tuning data**: per this repo's
  working rule, spawned an Agent with no repository access and asked it to
  write 12 independently-authored paraphrases of the reversed/false
  Lagrange claim, steered specifically at possessive and determiner-
  adjacent phrasing (the exact failure category this bug was about — not
  the general open-ended-English ceiling teach-8xw.33 already measured).
  Ran all 12 against the fixed code:

  **3/12 CONTRADICTED, 9/12 CANNOT_VERIFY, 0/12 CONFIRMED.**

  The property that matters — zero dangerous false-CONFIRMED — held on
  every sentence in this fresh round. The 9 misses are not possessive-
  determiner gaps recurring; they're the already-disclosed ceiling: verb-
  phrase metaphors ("goes evenly into" breaks `_DIVIDES_SYNONYMS`' adjacency
  requirement because "evenly" sits between "goes" and "into"), symbolic
  notation (`|G| divides |H|`), and sentence structures topic_patterns
  doesn't recognize at all. One catch and one representative miss from this
  round are locked into `tests/test_fact_checker.py` as regression evidence
  for both halves of the measurement, matching teach-8xw.33's precedent.
  This is **not** a claim that possessive phrasing in general is now fully
  covered — 9/12 still abstain rather than catch — only that the specific
  dangerous failure mode (false CONFIRMED) this bead was filed against did
  not recur in an independently-authored round targeting exactly that
  phrasing family.

## Files changed

- `teach/math_facts.py` — `_ANY_DETERMINER` extended with possessive
  support; `false_patterns[1]` and `true_patterns[0]` in
  `_LAGRANGE_ORDER_DIVIDES` rewired to use it instead of their own inline
  determiner list, plus plural `group`/`subgroup` support.
- `tests/test_fact_checker.py` — 6 new regression tests: the exact bug
  sentence, the "any of its" compound form, a "their" variant, a possessive
  correct-direction control (must stay CONFIRMED), and one catch + one miss
  from the held-out blind round.

## What's still open (not this bead's scope, filed separately if pursued)

- `true_patterns[1]`'s loose `lagrange...divides` fallback is still
  direction-agnostic in principle. It's now unreachable for every known
  reproduction, but the underlying design — a catch-all true_pattern that
  trusts false_patterns to have caught every reversed phrasing first — is
  structurally an arms race against open-ended English. Not touched here
  because the bead scoped the fix to the determiner gap specifically, and
  narrowing/removing the fallback is a separate design decision with its
  own tradeoffs (recall loss) that deserves its own bead if someone wants
  to pursue it.
- The 9/12 misses in the held-out round (verb-phrase metaphors, symbolic
  notation) are the same disclosed ceiling already accepted for
  teach-8xw.33 and the kernel topic. Not chased further, for the same
  infinite-regress reason teach-8xw.33's comment gives: widening against
  this round's misses would just make them tuning data too.

## Commands to reproduce

```bash
uv run pytest -q                          # 271 passed
uv run python3 -m teach.math_facts        # OK: ...
uv run python3 -m teach.fact_checker      # OK: ...
git diff teach/math_facts.py tests/test_fact_checker.py
```
