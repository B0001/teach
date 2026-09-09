# teach-5gf — potential_checker: the _ABOUT_LEARNER pronoun gate silently excludes sentences from coverage accounting

## What was wrong

`teach/potential_checker.py`'s `_ABOUT_LEARNER` (a single regex requiring a
literal `you`/`your`/`yours`) gated both `extract_claims` and
`check_coverage` before a sentence was even considered a candidate. A
sentence that praised the learner without a pronoun was invisible to both —
not `unclassified`, just absent:

```
check_coverage("Genius like this comes along once in a generation.")
  -> about_learner=0  classified=0  unclassified=0
```

This re-opens the exact vacuous-pass shape teach-yn8 closed, one level up:
`check_coverage`'s "N seen" figure was itself silently gated, so a lesson
that flattered the learner entirely in this register would report "0 seen,
0 classified, 0 unclassified" — reading as "no claims about the learner"
rather than "the counting mechanism missed this register."

## What was found while fixing it (not in the bead's reproduction)

Tracing `_ABOUT_LEARNER`'s two call sites turned up a **more severe**
instance of the same bug. Some of `_claim_type`'s own patterns are already
pronoun-free by design — teach-kmm's "never/always ... struggles/fails/..."
TRAIT shape explicitly claims an invariant outcome without needing "you":

```python
>>> _claim_type("A mind like this never struggles with proofs.")
ClaimType.TRAIT
```

Under the old gate, this sentence was blocked from ever reaching
`_claim_type` — not landing in `unclassified`, but dropped from
`extract_claims` entirely. A sentence the classifier could already type
correctly as INFLATED was never flagged. That's worse than the bead's own
reproduction (which, even if let through, still wouldn't classify).

## What was built

`_ABOUT_LEARNER` was renamed `_ABOUT_LEARNER_PRONOUN` and a new
`_about_learner(sentence)` function (used identically by both
`extract_claims` and `check_coverage`, so they can never disagree) accepts a
sentence as a candidate via any of three independent paths:

1. **Pronoun** (`_ABOUT_LEARNER_PRONOUN`) — unchanged from before.
2. **`_claim_type(sentence) is not None`** — if the classifier can already
   type the sentence on the text alone, it must never be gated out first.
   This closes the more severe gap above using the existing pattern set,
   no new vocabulary.
3. **`_ABOUT_LEARNER_APTITUDE`** — a new, explicitly bounded fallback: an
   inherent-quality noun (`gift(s)`, `talent(s)`, `mind(s)`, `brain(s)`,
   `intellect(s)`, `instinct(s)`, `abilit(y|ies)`, `genius(es)`,
   `brilliance`), singular or plural. This is what makes the bead's own two
   reproduction sentences visible: they don't match any `_claim_type`
   shape even given the chance (no "like yours", no absolute adjective, no
   failure verb — they use "like this" / "on this scale," not a claim shape
   this module recognizes), so they land in `unclassified`, which is the
   correct, disclosed outcome, not a silent drop.

`teach/potential_checker.py`'s module comments at the new code explain the
"why" (see the block above `_APTITUDE_NOUN`) rather than restating this here.

## Held-out generalization testing (per the bead's method note)

The bead is explicit that teach-yn8 and teach-kmm were **both** closed
against self-authored generalization sets, and both broke on the first
independently-authored phrasings — teach-kmm's gap is what produced this
very bead. So before treating this as closed, I ran two rounds of
genuinely-blind testing: a fresh `Agent` call, given no access to this
repo's code, asked only to write flattering-tutor sentences with no
`you`/`your`/`yours`, in its own words.

**Round 1** (8 sentences, agent asked for varied vocabulary and structure):

| sentence | seen? |
|---|---|
| "Genius of this kind surfaces maybe once in a decade." | yes |
| "Some minds simply arrive wired for numbers, and this is clearly one of them." | yes |
| "Einstein would have nodded approvingly at reasoning this sharp." | **no** |
| "There's an inevitability to the success ahead here — the only question is how far it goes." | **no** |
| "A gift like this can't be taught; it can only be recognized." | yes |
| "Few people are born with this kind of mathematical instinct." | yes |
| "Future textbooks might well cite work that starts exactly like this." | **no** |
| "Raw, natural brilliance of this caliber tends to write its own destiny." | yes |

5/8 caught. ("Some minds..." only started passing after a plural-form bug
fix — the first version of `_APTITUDE_NOUN` matched `mind` but not `minds`.)

**Round 2** (6 sentences, a *second* fresh agent, explicitly told to avoid
"genius"/"gift"/"talent"/"instinct"/"brilliance" to probe past-vocabulary):

| sentence | seen? |
|---|---|
| "Rarely does a mind take to abstract structure this naturally..." | yes |
| "Such quick command of the material practically guarantees a spot among the top scorers..." | **no** |
| "Few students ever produce work this polished on a first attempt." | **no** |
| "...reminiscent of a young Feynman working through a problem..." | **no** |
| "Mastery like this doesn't fade — it compounds..." | **no** |
| "Once in a great while a tutor gets to work with someone whose understanding simply outpaces the lesson plan..." | **no** |

1/6 caught.

**Honest reading of this evidence**: the fix demonstrably closes the bug's
literal reproduction and a real, more-severe variant found along the way. It
does **not** close the general problem — 8 of 14 independently-authored
pronoun-free praise sentences across both rounds are *still* invisible to
`check_coverage` (`about_learner=0`, indistinguishable from "no claims about
the learner"), for the same structural reason the original bug existed: any
finite whitelist has an outside, and English's ways of implying "you" without
saying it are unbounded. This is disclosed, not fixed, and I filed it as a
new bead rather than either (a) quietly declaring victory on the two rounds
above, which are now themselves not held-out for a future worker, or (b)
chasing more literal patterns against my own held-out set, which is exactly
the failure this bead's method note describes happening twice already.

Filed: **teach-8xw.19** — "potential_checker: pronoun-free praise outside
the aptitude-noun vocabulary is still invisible to coverage" — with the
specific missed sentences from both rounds as its reproduction floor, and
the same method note repeated (don't close it against a same-session
held-out set).

## What was NOT done

- Did not attempt to regex-match the four residual categories found
  (named-person comparison without "next X"/"just like X himself";
  bare inevitability without a future-tense modal; oblique
  future-achievement implication; guarantee-of-outcome framing without
  "guaranteed to") — that's genuinely open-ended pattern design, not a
  bounded fix, and belongs in teach-8xw.19 with its own held-out
  verification, not bolted onto this bead's closure under time pressure.
- Did not change `teach/honesty_rubric.py`'s decision table, `_claim_type`'s
  existing shape patterns, `_EFFORT_PATTERNS`, or `_evidenced_ceiling` —
  only the candidacy gate (`_ABOUT_LEARNER` → `_about_learner`) changed.
- Did not touch `teach/dnf_bond_integration.py` — its hardcoded
  `about_learner == 6` / `classified == 1` / `unclassified == 5` assertions
  against the real D&F/Bond lesson text were re-verified unchanged (grepped
  the lesson text for the new aptitude vocabulary first — no collisions,
  then ran the module directly to confirm the counts).

## Verification

- `uv run python -m teach.potential_checker` — self-check now also asserts
  both bead reproduction sentences produce `about_learner=(sentence,)` and
  `unclassified=(sentence,)` via `check_coverage`.
- `uv run python -m teach.dnf_bond_integration` — real D&F/Bond lesson
  still reports 6 seen / 1 classified / 5 unclassified, unchanged.
- `uv run pytest -q` — 179 passed (was 173 before this bead). 6 new tests in
  `tests/test_potential_checker.py`: seen-not-dropped and
  unclassified-not-silently-classified for the bead's reproduction,
  `extract_claims`/`check_coverage` agreement, a third-person-about-someone-
  else sentence still landing in the seen set (proving the gate isn't
  learner-specific — it can't be, without solving coreference), tutor/
  learner-turn scoping still holding for the new aptitude-noun path, and
  the more-severe `_claim_type`-without-pronoun regression
  ("A mind like this never struggles with proofs." now flags INFLATED).
- All pre-existing tests pass unmodified; the only public-surface change is
  `_ABOUT_LEARNER` (private, unused outside this module and its tests) being
  renamed to `_ABOUT_LEARNER_PRONOUN` plus the addition of `_about_learner`,
  `_APTITUDE_NOUN`, and `_ABOUT_LEARNER_APTITUDE`.

## Regression bar (from the bead, reproduced before fixing)

```
check_coverage("Genius like this comes along once in a generation.")
  -> about_learner=0  classified=0  unclassified=0   (pre-fix, confirmed)
  -> about_learner=1  classified=0  unclassified=1   (post-fix)

check_coverage("Talent on this scale is simply rare.")
  -> about_learner=0  classified=0  unclassified=0   (pre-fix, confirmed)
  -> about_learner=1  classified=0  unclassified=1   (post-fix)
```

Both now match the bead's third example's behavior
("Your genius comes along once in a generation." → seen, unclassified),
which is the bead's stated bar for what would close it. Enforced as an
assertion in `teach/potential_checker.py`'s own `__main__` self-check
(`_TEACH_5GF_REGRESSION_SENTENCES`) and in `tests/test_potential_checker.py`.

## Follow-up filed

- **teach-8xw.19** (P2): the residual, measured-but-unclosed generalization
  gap described above. Not a blocker for this bead — the specific coupling
  bug this bead names (coverage denominator depending on the same narrow
  gate as classification) is fixed and the bead's literal reproduction
  passes — but the underlying safety property ("an unclassified sentence is
  visibly unchecked, never silently invisible") is only partially restored,
  and a future worker should not read this handoff as "the invisibility
  problem is solved."
