# teach-8xw.8 — Producer: define a checkable honesty constraint

## What was built

The epic requires motivation to be "guided by Cialdini... bounded by a hard
honesty constraint," and sandbox-prompt.md says that constraint is "a
checkable property, not a tone note." Nothing existed yet. This bead is
scoped as design-only (its own acceptance criteria: "a concrete rubric...
recorded via `bd update --design`... specific enough that teach-8xw.13 can be
implemented directly against it, not against a vague restatement of 'don't
lie'"), so the deliverable is the rubric itself, encoded as real, tested code
rather than prose alone — same pattern teach-8xw.9 used for the boundary
definition.

- `teach/honesty_rubric.py`:
  - `ClaimType` — four kinds of potential-claim a checker must distinguish
    when extracting from lesson text: GROWTH (developable capability),
    OUTCOME (specific future result/reward), TRAIT (innate fixed
    characteristic offered as the reason for an outcome), COMPARATIVE
    (likened to a named exceptional person/standard).
  - `PotentialClaim` — the target shape extraction must produce: `text`,
    `claim_type`, `conditioned_on_effort: bool`, `evidenced_ceiling: bool |
    None` (`None` = text gives no basis to decide — the abstention case).
  - `classify(claim) -> Verdict` — the decision table:
    1. `TRAIT` → always `INFLATED` (hard rule, independent of the other two
       attributes — trait framing bypasses effort by construction).
    2. not `conditioned_on_effort` → `INFLATED` (an unconditioned promise is
       a guarantee).
    3. Otherwise: `evidenced_ceiling is None` → `ABSTAIN`; `False` →
       `INFLATED`; `True` → `HONEST`.
  - `WORKED_EXAMPLES` — 6 hand-written `PotentialClaim`s with expected
    verdicts, covering all three branches of the table (one HONEST, three
    INFLATED via different routes — trait, unconditioned, conditioned-but-
    unevidenced — one INFLATED comparative, one ABSTAIN). These are the
    fixtures teach-8xw.13's own acceptance criteria ask for ("a hand-written
    honest-encouragement example... a hand-written inflated-promise
    example") — reuse them there rather than writing new ones.
  - `python -m teach.honesty_rubric` self-check: asserts every worked
    example classifies as expected, per this repo's "every module
    self-checks standalone" convention.

- `tests/test_honesty_rubric.py` — 9 tests, all passing:
  - worked examples all classify as expected
  - at least one worked example is HONEST / INFLATED / ABSTAIN each
    (proof the table isn't tuned to always pass, always flag, or never
    abstain)
  - TRAIT claims are inflated even when marked effort-conditioned and
    ceiling-evidenced (proves the hard rule actually overrides the other
    two attributes, not just happens to agree with them on the worked
    example)
  - unconditioned claim is inflated even with an evidenced ceiling (proves
    conditioning is checked before, and independent of, ceiling evidence)
  - conditioned+evidenced → HONEST, conditioned+unevidenced → INFLATED,
    conditioned+unknown → ABSTAIN (the three-way branch on
    `evidenced_ceiling`, tested directly rather than only via worked
    examples)

- `bd update teach-8xw.8 --design` — the full rubric recorded on the bead
  itself (claim shape, the three attributes, the decision table, the six
  worked examples, and an explicit note for teach-8xw.13 about scope — see
  below), per this bead's own "what would close this."

Full test suite: `uv run pytest -q` → 16 passed (7 pre-existing from
teach-8xw.9 + 9 new).

## What this does NOT do

- It does not parse raw lesson text to find potential-claims or populate
  their attributes. `classify()` operates on an already-extracted
  `PotentialClaim` — turning free text into that shape (finding the
  sentences, deciding whether they're effort-conditioned, deciding whether
  the claimed ceiling is evidenced by anything earlier in the same
  transcript) is teach-8xw.13's job, which is *why* .13 was filed separately
  and blocked on this bead: it needs a concrete target to extract into,
  rather than inventing its own notion of "sounds like an overpromise."
- It does not implement the full checker (teach-8xw.13) or wire it into
  teach/boundary.py's `LessonArtifact`. No code here reads a `LessonArtifact`
  at all.
- COMPARATIVE claims are on the same decision table as GROWTH/OUTCOME
  (not a hard-INFLATED rule like TRAIT), on the theory that a rare,
  extraordinarily well-evidenced comparison shouldn't be structurally
  unreachable. But the design note flags explicitly that in practice this
  will almost never resolve to `evidenced_ceiling=True` in a real tutoring
  transcript, since matching a specific named historical figure's actual
  achievement is a categorically higher bar than a single lesson can
  evidence — that's a judgment call left to teach-8xw.13's extractor, not
  hard-coded here.
- `evidenced_ceiling` is defined against "the same lesson text" (the
  `LessonArtifact` transcript), not against any producer-side ground truth
  the checker isn't allowed to see — this keeps the rubric compatible with
  the blind-checker boundary from teach-8xw.9, but it does mean the rubric
  can only ever verify internal consistency of a lesson (does the promise
  match what the transcript itself shows), not whether the transcript's own
  claims of demonstrated performance are truthful. That's arguably a gap
  worth a bead of its own if it turns out to matter once teach-8xw.13 is
  built against real generated lesson text — not filing it now since it's
  speculative until there's a real producer to observe.

## Verification

```
uv run python -m teach.honesty_rubric   # OK: 6 worked examples all classify as expected
uv run pytest -q                        # 16 passed
```

## Files touched

- `teach/honesty_rubric.py` (new)
- `tests/test_honesty_rubric.py` (new)
- bead `--design` field updated with the rubric text

Nothing committed — conservative git policy, bead did not say to commit.
