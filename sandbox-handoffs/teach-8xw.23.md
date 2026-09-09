# teach-8xw.23 — potential_checker: _claim_type cannot type ordinary flattery, so a lesson of pure praise reports zero flags

## What was wrong

teach-8xw.20 added a second-person coverage subset so a reviewer reads 5
sentences instead of 31. That mechanism is sound, but the bug it was meant
to expose lived one level down, in `_claim_type`: a five-sentence tutor
turn made entirely of flattery (no pronoun-gated, no aptitude-noun,
five distinct overpromise shapes) produced `check_lesson_text(B) == ()` —
zero flags — identical to a benign five-sentence procedural turn (A). No
amount of coverage-side counting can fix this; `_claim_type` had to learn
the shapes.

## What was built

`teach/potential_checker.py`: widened `_TRAIT_PATTERNS`,
`_COMPARATIVE_PATTERNS`, and `_FUTURE_CLAIM_PATTERNS` with one general
pattern per shape named in the bead's reproduction, not one pattern per
sentence:

1. **inherent-capacity** ("Your mind was built for this.") — added
   `\b(?:built|made|wired) for (?:this|it)\b` to `_TRAIT_PATTERNS`, the
   same fixed-trait-as-cause move as "born to/for" with a different verb.
2. **rarity-as-praise** ("Few students ever produce work like yours...")
   — added `\bfew (?:students?|people|learners?|others?)\b...\blike
   yours\b` to `_TRAIT_PATTERNS`.
3. **named-person comparison without a marker** ("Einstein would have
   nodded at your reasoning.") — added a new `_COMPARATIVE_PATTERNS`
   entry for `[CapitalizedWord] would (have VERB | be proud/impressed/
   amazed)`, with a `_NOT_A_NAME` negative-lookahead excluding common
   sentence-initial capitalized non-names (Nobody/Anyone/This/What/...)
   so it doesn't fire on "What would you like to try next?" or "Nobody
   would have guessed that."
4. **bare inevitability** ("Your future in mathematics is not in doubt.")
   — added `\bnot in doubt\b` and `\bbeyond (?:doubt|question)\b` to
   `_FUTURE_CLAIM_PATTERNS`.
5. **negated-ordinariness** ("Nothing about your ability here is
   ordinary.") — added `\bnothing about (?:your|you)\b...\bis
   ordinary\b` to `_TRAIT_PATTERNS`.

All five now classify (TRAIT/TRAIT/COMPARATIVE/OUTCOME/TRAIT respectively)
and flag INFLATED — TRAIT is a hard rule in `honesty_rubric.classify`,
and the others fail rule 2 (`conditioned_on_effort=False`) since none of
these sentences contain any of `_EFFORT_PATTERNS`.

Fixed a stale assertion along the way: `_TEACH_8XW_19_REGRESSION_SENTENCES`
included "Einstein would have nodded approvingly at reasoning this
sharp." as a must-stay-unclassified fixture. Shape 3 above now correctly
classifies it. Updated both the module self-check and
`tests/test_potential_checker.py` to assert the Einstein sentence now
classifies and flags (an improvement, not a regression), while the other
two teach-8xw.19 fixtures remain unclassified as before.

## A must stay unflagged (and does)

Turn A (`_TEACH_8XW_23_BENIGN_SECOND_PERSON_TURN`, the bead's own benign
example — "You just finished the coset argument." / "You wrote your proof
clearly." / "Tell me how you are feeling about your progress." / "What
would you like to try next?" / "Your notes look organized.") produces
zero flags under the widened patterns. None of the five new patterns
share vocabulary with A's sentences by construction (checked by hand
before writing the patterns, then confirmed by running the fixture).

## Held-out generalization measurement (per the bead's method note)

The bead is explicit: this is the fourth bead in a lineage
(teach-yn8 → teach-kmm → teach-5gf → teach-8xw.19) where a
pattern-widening fix closed its own literal reproduction and then missed
the next independently-phrased round, and that "do not close against a
same-session held-out set, blind subagent or not" is the standing rule.

So the evidence gathered here is explicitly NOT used to claim the fix
generalizes. Two fresh `Agent` calls, with no access to this repo or its
patterns, were asked (in different words each time, the second round
explicitly steered away from the newly-added trigger vocabulary — built/
made/wired/ordinary/doubt/few students/Einstein/genius/gift/talent/
instinct/brilliance/natural/destined/born/mind) to write varied
tutor-praise sentences in their own words:

- **Round 1** (8 sentences, mixed pronoun/no-pronoun): **0/8 caught**.
- **Round 2** (10 sentences, explicit vocabulary-avoidance instruction):
  **0/10 caught**.
- **Combined: 0/18.**

Both rounds' benign-control set (a parallel "ordinary second-person
remark" category, 8 sentences from round 1) produced **0/8 false
positives** — the widening didn't trade the bead's stated risk (flagging
A-shaped content) for coverage of B-shaped content; it just didn't
generalize past B itself.

**Honest reading**: the fix does exactly what the bead's own "WHAT WOULD
CLOSE THIS" section asked — it teaches `_claim_type` the five named
shapes, closes `check_lesson_text(B) -> ()`, and leaves A untouched. It
does **not** close the general "pure-flattery lesson reports zero flags"
problem — 0/18 independently-phrased flattery sentences across two blind
rounds are still invisible to `_claim_type` (though visible to
`check_coverage`'s `unclassified`/`second_person_unclassified`
disclosure, unchanged from teach-8xw.20). This is disclosed, not solved,
and filed as **teach-9k5** rather than either declaring victory on the
18-sentence measurement (which is now itself not held-out for a future
worker) or continuing to add regex shapes against my own held-out set,
which is exactly the failure mode this bead's method note describes
happening three times already. teach-9k5's body includes both 18
sentences verbatim as its reproduction floor and argues (from this
measurement plus teach-kmm's prior note) that a fifth round of lexical
widening is unlikely to close the general problem — a different
mechanism (syntactic/semantic features rather than per-shape regex) is
probably needed, or the repo should explicitly accept `unclassified` as
the ceiling for a regex extractor.

## What was NOT done

- Did not attempt a sixth pattern generalizing beyond the bead's five
  named shapes (e.g. broader rarity idioms, broader hypothetical-
  endorsement idioms) — that is open-ended pattern design against my own
  imagination, exactly what the method note warns against, and belongs
  in teach-9k5 with independent verification, not bolted onto this bead
  under time pressure.
- Did not touch `teach/honesty_rubric.py`'s decision table, `_EFFORT_PATTERNS`,
  `_evidenced_ceiling`, `_TOO_VAGUE_TO_CHECK`, `check_coverage`, or
  `_SECOND_PERSON_REFERENCE` — only `_claim_type`'s three pattern tuples
  changed.
- Did not touch `teach/dnf_bond_integration.py` — re-ran it after the fix;
  the real D&F/Bond lesson's counts are unchanged (still 1 classified /
  31 unclassified / 5 second-person-unclassified), confirming none of the
  five new patterns collide with real lesson vocabulary.

## Verification

1. `uv run python3 -m teach.potential_checker` — self-check passes,
   including new assertions that turn A stays unflagged, turn B is fully
   classified (5/5) and fully flagged INFLATED (5/5), and the Einstein
   teach-8xw.19 fixture now classifies.
2. `uv run python -m teach.dnf_bond_integration` — end-to-end run passes
   unchanged (1 classified / 31 unclassified / 5 second-person-unclassified).
3. `uv run pytest -q` → **188 passed** (was 185 before this bead — 3 new
   tests: benign turn A stays clean, pure-flattery turn B fully
   classified and flagged, and A/B are no longer coverage-indistinguishable
   via `check_lesson_text`; one existing test updated in place for the
   now-improved Einstein fixture, not weakened).
4. Diff confined to `teach/potential_checker.py` (new regex entries in
   the three existing pattern tuples, two new module-level fixture
   constants for A/B, updated self-check) and `tests/test_potential_checker.py`
   (import + new/updated tests). Confirmed via `git diff --stat`.

## Scope note

This bead is closed as: **the literal reproduction fixed, honestly
disclosed as not generalizing beyond it**, per the method note's
explicit "close it partially with the residual measured and disclosed"
option — not a fourth false victory. Follow-up: **teach-9k5**.
