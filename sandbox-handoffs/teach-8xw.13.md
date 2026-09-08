# teach-8xw.13 — Checker: flag promises about learner potential that outrun what effort can deliver

## What was built

teach-8xw.8 (closed) defined `teach/honesty_rubric.py`: a decision procedure
(`classify`) over an already-populated `PotentialClaim`
(claim_type/conditioned_on_effort/evidenced_ceiling), explicitly scoping
*extraction from raw text* out of itself and naming this bead as the one
that does it. Nothing existed for that extraction before this session. This
session built it:

- `teach/potential_checker.py`:
  - `extract_claims(text)` — heuristic, regex-based extraction. Splits
    lesson text into tutor-only turns (filters out `learner:` lines when
    the text is speaker-tagged the way `teach.boundary.LessonArtifact.text`
    renders it; treats the whole string as one turn otherwise), then
    sentences within each turn. A sentence becomes a `PotentialClaim` only
    if it's about "you"/"your" and matches a TRAIT, COMPARATIVE, or
    future-tense GROWTH/OUTCOME pattern. `conditioned_on_effort` is decided
    by an explicit effort-phrase list ("if you keep...", "with practice",
    etc.) — absence defaults to `False`, not a guessed `True`, per the
    stated bias: absence of a signal should make a claim MORE likely to be
    surfaced, not less. `evidenced_ceiling` is `False` for a fixed list of
    categorically-too-high claims (publishing original research, "best of
    your generation", Fields Medal, etc.) and for all COMPARATIVE claims
    (matching teach-8xw.8's own design note that a named figure's actual
    achievement is a categorically higher bar than one lesson can
    evidence); `True` when the turn contains both a "you just did X"
    self-reference and an "next/similar" framing for what comes after;
    `None` (abstain) otherwise.
  - Extraction-layer abstention: a short stoplist of vague filler with no
    checkable content ("you'll get there", "you've got this") is not
    extracted as a claim at all, rather than forced through the classifier
    with a guessed `conditioned_on_effort` (that attribute is a plain
    `bool` with no abstain option in teach-8xw.8's dataclass — the
    extractor's only way to abstain on genuinely underdetermined input is
    to not manufacture the claim in the first place). This is deliberate
    and documented in the module docstring, not an oversight.
  - `Flag` (claim, verdict, reason) and `check_lesson_text(text) ->
    tuple[Flag, ...]` — the actual checker entry point. Surfaces both
    INFLATED and ABSTAIN verdicts (not just INFLATED) — abstention in the
    rubric means "the text doesn't support certifying this as honest," not
    license for this checker to swallow it silently.
  - `HONEST_EXAMPLE_TEXT` / `INFLATED_EXAMPLE_TEXT` — the bead's required
    hand-written examples, framed as `LessonArtifact`-shaped
    tutor/learner transcripts (the real input shape) rather than bare
    sentences.
  - `python -m teach.potential_checker` self-check: asserts the honest
    example produces zero flags and the inflated example produces at least
    one INFLATED flag.

- `tests/test_potential_checker.py` — 16 tests, all passing:
  - The two required hand-written examples (honest passes clean, inflated
    is flagged as INFLATED).
  - Not-vacuous checks: ordinary lesson text with no potential-claims
    produces zero flags; learner-spoken text isn't extracted (a promise is
    something the *tutor* makes); plain text with no speaker tags is still
    scanned (the bead says "given lesson text," not "given a
    LessonArtifact").
  - **Fidelity to the teach-8xw.8 worked examples**: ran `extract_claims`
    against the raw `.text` of 5 of the 6 `WORKED_EXAMPLES` fixtures in
    `honesty_rubric.py` and asserted the extracted claim classifies to the
    same `.expected` verdict the hand-authored fixture declares. This is
    the check that proves the extractor targets teach-8xw.8's actual
    boundary rather than an independent guess at "sounds like an
    overpromise" — which is exactly what teach-8xw.8's own design note
    asked for.
  - The 6th worked example ("You'll get there.") is deliberately excluded
    from that fidelity check — see "What this does NOT do" below — with a
    test proving it's excluded for the stated reason (extraction-layer
    abstention), not silently dropped.
  - Individual attribute-extraction tests: TRAIT detection, COMPARATIVE
    detection, effort-conditioning detection (present and absent),
    categorical unevidenced-ceiling detection, ordinary-extension
    evidenced-ceiling detection, and the ABSTAIN path when ceiling
    evidence is absent either way.

## What this does NOT do

- **It is a heuristic, not a proof.** Regex-over-English will miss
  phrasing it doesn't recognize (false negatives — an inflated claim
  phrased in a way not in these pattern lists passes through unflagged)
  and could occasionally misfire on phrasing that happens to match a
  pattern for an unrelated reason (false positives). This is stated
  plainly in the module docstring rather than implied to be more reliable
  than it is. A real deployment would need either a much larger corpus of
  adversarial test phrasings, or a second extraction path (e.g. an LLM
  call) cross-checked against this one — out of scope here.
- **It does not resolve `WORKED_EXAMPLES[5]` ("You'll get there.")
  end-to-end.** That fixture's `conditioned_on_effort=True` is a generous
  reading of context (implied prior effort) that the bare sentence, taken
  alone, does not contain — and `conditioned_on_effort` is a plain `bool`
  with no abstain option in teach-8xw.8's `PotentialClaim`, so a text-only
  extractor is forced to a binary call the fixture's own hand-authored
  label doesn't obviously follow from the text. Rather than special-casing
  that exact string to fake agreement (which would be gaming the test, not
  passing it), this extractor abstains a different way: vague filler with
  no checkable content is never extracted as a claim, so it produces zero
  flags for that input instead of an ABSTAIN-tagged flag. Documented in
  both the module docstring and a dedicated test
  (`test_vague_reassurance_is_not_extracted_as_a_claim`). If a future bead
  wants exact parity here, it would need to either give
  `conditioned_on_effort` a `None` state in teach-8xw.8's dataclass (a
  change to the closed bead's rubric) or accept that this one fixture is a
  genuinely underdetermined boundary case.
- **It does not verify domain facts** (teach-8xw.11) or **recover the
  taught concept/prerequisites** (teach-8xw.10) — those are separate
  checker components. This module only looks at potential-claims.
- **It has not been run against real producer output**, because no
  producer exists yet (teach-8xw.6/.7 are open). The two hand-written
  examples and the worked-example fidelity check are the only evidence of
  correctness that exists right now. teach-8xw.15 (integration, blocked on
  this bead among others) is where this gets tested against a real
  end-to-end lesson.

## Verification

```
uv run pytest -q                        # 32 passed (16 new + 9 honesty_rubric + 7 boundary)
uv run python -m teach.potential_checker  # OK: honest example passes clean (0 flags), inflated example flagged (1 flag(s))
```

## Files touched

- `teach/potential_checker.py` (new)
- `tests/test_potential_checker.py` (new)

Nothing committed — conservative git policy, bead did not say to commit.
(Note: `sandbox-handoffs/teach-8xw.1.md` shows as modified in `git status`
from before this session started; not touched here, out of scope.)
