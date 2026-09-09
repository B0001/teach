# teach-kmm — potential_checker: classify claims by shape instead of a (now wider) pattern whitelist

## What was wrong

teach-yn8 widened `teach/potential_checker.py`'s pattern lists and shipped the
coverage-transparency fix ((b)): an unclassified sentence is now visibly
unchecked rather than silently clean. It explicitly did not ship (a), "the
real fix" — classification by claim shape rather than by matching one more
listed construction. teach-kmm measured the gap left behind by running the
post-yn8 checker against five phrasings that were NOT in yn8's reproduction
set:

- "Nothing can stop you from mastering Galois theory." — MISS (unclassified)
- "You are destined for a Fields Medal." — MISS
- "Your gift for algebra is limitless." — MISS
- "A mind like yours never struggles with proofs." — MISS
- "There is no doubt whatsoever that you will surpass your professors." — FLAG
  (already worked, via the existing `you will` pattern)

4 of 5 fell through as unclassified, not wrongly-classified — thanks to (b)
this was disclosed via `check_coverage`, not silently passed, which is why
this bead was P2 rather than P1.

The bead was explicit that adding these four sentences as new literal
patterns would score 0 on its actual measure: generalization to phrasing
nobody wrote a pattern for.

## What was built

`teach/potential_checker.py`'s `_claim_type` still has to assign one of four
concrete `ClaimType`s to run `honesty_rubric.classify`'s decision table — a
regex-only extractor cannot escape being a pattern matcher over *something*.
What changed is what the patterns are organized around: each of the four
missed sentences was traced to a distinct **grammatical shape**, and each
shape got one general pattern rather than one pattern per sentence:

1. **Negated-obstacle idiom** ("nothing/no one/nobody can/will/could stop
   you", "there's/there is no stopping you", "you can't be stopped", bare
   "unstoppable") — added to `_FUTURE_CLAIM_PATTERNS`. This asserts the same
   inevitable-success claim as "you will succeed" by denying any obstacle
   could prevent it, rather than asserting the success directly. Covers
   "Nothing can stop you from mastering Galois theory."

2. **`destined for` as well as `destined to`** — the old pattern
   (`\bdestined to\b`, from teach-yn8) only matched the verb-phrase
   continuation ("destined to become..."); "destined for a Fields Medal" is
   the same inevitability modal with a noun phrase after it. One-character
   change to the alternation (`destined (?:to|for)`) closes both.

3. **Innate-quality-noun framing**, three sub-shapes added to
   `_TRAIT_PATTERNS`, built on a shared `_INNATE_QUALITY_NOUN` group
   (gift/talent/mind/brain/intellect/instincts/ability) instead of hard-coding
   "talent" as teach-yn8's `\byours\b` fix implicitly had:
   - `"[noun] like yours"` — generalizes the already-known "talent like
     yours cannot fail" case to any noun naming an inherent quality. Covers
     "A mind like yours never struggles with proofs" (which also matches
     shape 4 below — either is sufficient).
   - `"your [noun] is/are [absolute adjective]"` (limitless / boundless /
     infinite / unmatched / unparalleled / unrivaled) — an innate quality
     described as having no ceiling at all. Covers "Your gift for algebra
     is limitless."
   - `"never/always ... [failure verb]"` (struggles/falters/fails/
     stumbles/hesitates/doubts) — quantifies over every instance rather
     than describing this one, so the claimed success is invariant rather
     than earned; same fixed-characteristic-as-cause move as the other two,
     wearing a verb instead of a noun. Covers "A mind like yours never
     struggles with proofs" independently of the "like yours" match.

All five bead sentences now classify and flag INFLATED under the unchanged
`teach/honesty_rubric.py` decision table (four via the new patterns, the
fifth — "you will surpass" — was already working and is included as a
non-regression check).

## Held-out generalization set (the actual measure of success)

Per the bead: "the measure of success is the unclassified count falling on
held-out phrasings nobody wrote a pattern for." Reusing the bead's own five
sentences as the only fixture would not demonstrate that — those five are
exactly what the patterns above were designed to catch. So a second set,
`_TEACH_KMM_HELD_OUT_GENERALIZATION_SENTENCES`, was written using different
vocabulary and a different named reward/person for the same five shapes,
none of which appears literally in any new regex:

- "No one can stop you from acing the final." (obstacle-negation, different
  verb than "stop"/"mastering")
- "You are destined for a spot on the Putnam team." ("destined for", named
  reward not in `_UNEVIDENCED_CEILING_PATTERNS` or anywhere else)
- "Your talent for proofs is boundless." (innate-noun + absolute adjective,
  different noun+adjective pairing than the bead's "gift"/"limitless")
- "A brain like yours never falters on hard problems." ("[noun] like
  yours", different noun ("brain") and different failure verb ("falters")
  than the bead's "mind"/"struggles")
- "Your instincts for this are unrivaled." (innate-noun + absolute
  adjective again, "instincts"/"unrivaled" — neither word is the bead's)

All five flag INFLATED. `test_teach_kmm_regression_and_generalization_sets_are_disjoint`
asserts the two sets share no sentence, so this can't silently degrade into
one list wearing two names.

**Honest limit on what this proves**: both sets were written by the same
session that wrote the patterns, so this is not independent held-out data in
the strict ML sense — it's evidence the fix generalizes across *shape*
variation (different noun, different verb, different named reward) rather
than being five more literal strings, which is the specific failure mode the
bead called out. It is not evidence against every phrasing English offers;
`check_coverage`'s `unclassified` count (unchanged from teach-yn8, still
wired through `dnf_bond_integration`) remains the honest disclosure
mechanism for whatever this still misses. A future worker wanting a stronger
generalization proof would need phrasings from a source that never saw this
session's regex choices — e.g. a fresh worker session given only the rubric
and asked to write adversarial examples blind to this diff.

## What was NOT done

- No NLP/POS-tagging dependency was added (checked: no `spacy`/`nltk` in the
  environment, and `pyproject.toml` has no NLP dependency). A genuinely
  syntax-driven classifier (detect modal auxiliaries, absolute quantifiers,
  and superlative adjectives via POS tags rather than lexical alternation)
  would generalize further than regex families can, but that's a dependency
  and design decision beyond this bead's scope — filing as a candidate
  follow-up thought, not a new bead, since no concrete requirement forces it
  yet.
- Did not touch `teach/honesty_rubric.py` (the decision table) or
  `_EFFORT_PATTERNS` — unaffected, no gap found there.
- Did not touch `_COMPARATIVE_PATTERNS` (named-person comparison) — none of
  the five reproduction sentences exercised that claim type, so no gap was
  measured there this session.

## Verification

- `uv run python -m teach.potential_checker` — self-check now also asserts
  all 5 teach-kmm regression sentences and all 5 held-out generalization
  sentences flag INFLATED (previously 4/5 regression sentences unclassified,
  reproduced this before fixing — confirmed FAIL on pre-fix code via a
  scratch script, then confirmed PASS after).
- Manually re-checked the honest-encouragement fixtures and
  `dnf_bond_lesson`'s real lesson text (via the full pytest run, which
  includes `tests/test_dnf_bond_integration.py`) for new false positives
  from the widened patterns — none observed.
- `uv run pytest -q` — 173 passed (was 170 before this bead; 3 new tests:
  regression-set flagged, generalization-set flagged, and the
  sets-are-disjoint guard). All pre-existing tests pass unmodified — changes
  are additive to `_TRAIT_PATTERNS`/`_FUTURE_CLAIM_PATTERNS` plus two new
  module-level fixture tuples; no public function signature changed.

## Regression bar (from the bead)

> MISS "Nothing can stop you from mastering Galois theory."
> MISS "You are destined for a Fields Medal."
> MISS "Your gift for algebra is limitless."
> MISS "A mind like yours never struggles with proofs."
> FLAG "There is no doubt whatsoever that you will surpass your professors."

Confirmed: all five now produce `check_lesson_text(...)` output with
`len(flags) >= 1` and every flag's verdict is `INFLATED`. Enforced as an
assertion in `teach/potential_checker.py`'s own `__main__` self-check
(`_TEACH_KMM_REGRESSION_SENTENCES`) and as a pytest case in
`tests/test_potential_checker.py`, plus the independently-worded
generalization set in both places, so a future regression on either the
bead's exact reproduction or the shape-variation check fails loudly.
