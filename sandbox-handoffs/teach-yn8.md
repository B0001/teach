# teach-yn8 — potential_checker: overpromises outside the 5 future-tense patterns pass silently

## What was wrong

`teach/potential_checker.py`'s `_claim_type` used a hard whitelist gate,
`_FUTURE_CLAIM_PATTERNS`, of exactly five literal constructions ("you'll" /
"you will" / "you're going to" / "you are going to" / "you're
basically|practically"). A sentence had to match one of those five before
`classify()` ever saw it. Anything else — including blatant overpromises —
produced zero flags, and `check_lesson_text`'s empty tuple was reported
unqualified as "no claims flagged." Three sentences from the bead's
reproduction (a deliberately corrupted lesson) demonstrated the gap:

- "Keep this up and you are guaranteed to become one of the greatest
  mathematicians who has ever lived."
- "Talent like yours cannot fail."
- "You have the potential to be the best mathematician in the world."

The second one had a compounding bug: `_ABOUT_LEARNER = re.compile(r"\byou\b|
\byour\b")` doesn't match "yours" at all — `\byour\b` requires a word
boundary right after "r", and "yours" continues with "s", so that sentence
was falling out at the very first gate, before extraction logic ever ran.

The bead explicitly forbade closing this by adding three more literal
regexes — natural language for overpromising is unbounded, so any fixed
whitelist has an outside, and the real defect was conflating "no flags among
sentences my gate admitted" with "no overpromises in this lesson."

## What was built

Two changes, per the bead's stated (b)-then-(a) escalation:

**1. Broadened the claim-shape gate (`teach/potential_checker.py`)**

- Fixed the `\byours\b` gap in `_ABOUT_LEARNER`.
- Widened `_FUTURE_CLAIM_PATTERNS` from 5 literal future-tense phrases to a
  set organized by grammatical *shape* rather than exact string: certainty/
  inevitability modals (`guaranteed to`, `bound to`, `certain to`, `sure to`,
  `destined to`, `meant to be`), negated-failure (`cannot fail`, `won't
  fail`), and present-tense potential/capability assertions (`have the
  potential to`, `have what it takes`, `capable of`). This is still
  enumerable — a heuristic regex extractor cannot stop being one — but it
  closes the specific gap class the bead reproduced (present-tense and
  certainty-modal overpromises, not just five future-tense forms), not just
  the three literal sentences.
- Extended `_UNEVIDENCED_CEILING_PATTERNS` to catch "best ... in the world"
  and "greatest ... (who has) ever lived / of all time" (previously only
  "world's greatest/best" and "best ... of your/the generation" were
  recognized).
- Added "keep this up" to `_EFFORT_PATTERNS` (accurate classification, not
  required for the regression bar since an unconditioned claim is INFLATED
  either way).

All three bead sentences now classify OUTCOME, unconditioned-on-effort (no
explicit effort phrase present) → INFLATED under the existing, unchanged
`teach/honesty_rubric.py` decision table. No change to the rubric itself.

**2. Coverage transparency (the structural fix, addresses "will always have
an outside")**

Added `Coverage` (dataclass: `about_learner`, `classified`, `unclassified` —
all tuples of sentence text) and `check_coverage(text) -> Coverage` to
`teach/potential_checker.py`. Refactored the shared per-sentence decision
into `_extract_from_sentence(sentence, turn_text)` so `extract_claims` and
`check_coverage` cannot silently diverge on what counts as classified.

`check_coverage` reports, for every tutor-spoken sentence that is about the
learner and not filtered as vague-filler-with-no-checkable-content: how many
were seen, how many the extractor could type into a `PotentialClaim`, and —
critically — the literal text of the ones it could not. This makes "this
sentence was seen but never reached the rubric" visible and inspectable
instead of indistinguishable from "this sentence contains no promise."
Widening the pattern set (change 1) narrows what falls into `unclassified`;
it does not and cannot make that set empty, and this is now measured, not
assumed.

`teach/dnf_bond_integration.py`'s `IntegrationReport` gained a
`potential_coverage: Coverage` field. `render()` and the module's
`_self_check()` print/assert this explicitly now — the summary line changed
from the old unqualified "no inflated-potential flags" to "no inflated-
potential flags among the N classified potential-claim sentence(s) (M
about-learner sentence(s) left unclassified, disclosed above, not silently
passed)". Running it against the real `dnf_bond_lesson` output: 6 sentences
about the learner, 1 classified (the effort-conditioned "you'll be ready to
tackle the isomorphism theorems next" — HONEST), 5 unclassified
(retrospective/procedural framing like "you just handled..." and "in your
own words..." — read manually and confirmed none are potential claims, but
that confirmation is this handoff's, not the checker's, and is reported as
such rather than folded into the flag count).

## What was NOT done

- Did not implement full grammatical inversion (bead's option (a) taken
  literally: "any sentence about the learner making an evaluative or
  predictive statement is a claim, period, no shape-matching at all").
  Attempted design work during this session concluded that without shape
  detection, `classify()` has no `ClaimType`/`conditioned_on_effort`/
  `evidenced_ceiling` to populate, and defaulting all of those pessimistically
  for every about-learner sentence (including retrospective feedback like
  "you got that right" or plain encouragement like "you're doing great
  work") would flag ordinary tutor dialogue as INFLATED — a regression in
  the other direction. The combination actually shipped (broadened
  shape-detection + explicit, measured coverage-of-the-gap reporting) is the
  bead's stated minimum (b) plus a partial (a) that stays inside what a
  regex heuristic can responsibly claim; it does not close the gap, it
  measures it. A future worker with a real NLP capability-assertion
  classifier could go further; noting this rather than pretending broader
  regexes are the "real fix" the bead asked not to settle for.
- Did not touch `teach/honesty_rubric.py` (the decision table) — unaffected,
  no changes needed there.

## Verification

- `uv run python -m teach.potential_checker` — self-check now also asserts
  all 3 reproduction sentences from the bead are flagged INFLATED (previously
  0 flags on all three; reproduced this before fixing, confirmed FAIL on the
  pre-fix code, then confirmed PASS after).
- `uv run python -m teach.dnf_bond_integration` — real end-to-end run, prints
  the qualified coverage line, all assertions pass.
- `uv run pytest -q` — 170 passed (was 162 before this bead; 8 new tests:
  3 for the exact regression sentences, 1 for the `yours` gate fix, 4 for
  `check_coverage`/`Coverage`, plus 1 new integration-level coverage
  disclosure test). All pre-existing tests pass unmodified — the broadened
  patterns and the coverage addition are additive to the public API
  (`extract_claims`, `check_lesson_text` signatures unchanged).

## Regression bar (from the bead)

> the three sentences above must not pass silently

Confirmed: all three now produce `check_lesson_text(...)` output with
`len(flags) >= 1` and every flag's verdict is `INFLATED`. Enforced as an
assertion in `teach/potential_checker.py`'s own `__main__` self-check
(`_TEACH_YN8_REGRESSION_SENTENCES`) and as three individual pytest cases in
`tests/test_potential_checker.py`, so a future regression on this specific
reproduction fails loudly in two independent places.
