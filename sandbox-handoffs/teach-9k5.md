# teach-9k5 — potential_checker: regex-shape widening plateaus at 0/18 on blind-agent flattery

## Decision: closed as (b), a disclosed limitation, not a fifth widening

The bead itself named two honest ways to close: (a) a fundamentally different
classification mechanism, proven against held-out evidence from an agent
call that did not also write the mechanism, or (b) an explicit decision that
the regex-based extractor's ceiling has been reached and is already
disclosed, closed "will not fix" rather than left open indefinitely.

This session took (b). Reasoning:

- teach-9k5 is the **fourth** bead in a row (teach-yn8 → teach-kmm →
  teach-5gf → teach-8xw.19 → teach-8xw.23) to hit exactly this wall: widen
  `_claim_type`'s patterns to cover a reproduction, measure against a fresh
  independently-authored round, watch it fail almost completely. The measured
  scores across the lineage: teach-kmm 5/8 then 1/6; this bead 0/8 then 0/10.
  There is no visible trend toward convergence — if anything the ceiling is
  getting more visible, not less.
- The only concrete mechanism the lineage has floated for (a) — POS-tagging /
  syntactic feature detection instead of lexical regex — is not available in
  this environment (`spacy`/`nltk` are not installed, `pyproject.toml` has no
  NLP dependency; teach-kmm's handoff already checked and noted this). Adding
  a new dependency and building a genuinely different classifier is a real
  design decision, not something to bolt on inside a bug-fix bead.
- The bead's own instruction for closing via (a) is "get the generalization
  evidence from an agent call in a DIFFERENT session than the one that wrote
  the mechanism." A single work session cannot produce that: if this session
  wrote a new mechanism and then also generated its own held-out test data
  (even via a blind `Agent` call), the mechanism's author is still the one
  choosing when to stop iterating and what to ask the blind agent to avoid —
  the same feedback loop that let regex-widening look like progress three
  times before failing on the next round. Structurally satisfying "different
  session" requires a worker who does not know this session's mechanism,
  which this session cannot arrange for itself.
- Given that, attempting a fifth regex/keyword round now — even organized as
  "syntactic features" rather than "shapes" — would just be a differently-
  labeled instance of the same failure mode this lineage exists to document:
  patterns fitted by reading a known failing set are not evidence they
  generalize to the next one.

## What was verified before deciding

Reproduced the bead's own measurement rather than trusting the bead text:
ran all 18 sentences (8 from round 1, 10 from round 2) through
`check_coverage`/`check_lesson_text` on current `main`. Confirmed exactly as
reported: all 18 land as `seen=1, classified=0, unclassified=1, flags=0` —
genuinely unclassified (disclosed), not silently dropped and not falsely
counted as clean-and-classified.

## What was built

Not a new pattern — a permanent regression check that the *disclosure*
mechanism (`Coverage.unclassified`, wired through `dnf_bond_integration`'s
`render()`) continues to do its job on this exact known-failing set, so a
future change can't accidentally make these 18 sentences invisible again
(silently dropped) while still not classifying them.

`teach/potential_checker.py`:
- Added `_TEACH_9K5_DISCLOSED_CEILING_SENTENCES` (the 18 sentences, verbatim
  from the bead), with a comment documenting the lineage and the decision not
  to widen further.
- Extended the module's `__main__` self-check to assert all 18 are
  `seen`+`unclassified` and produce zero flags from `check_lesson_text`.
- Updated the self-check's summary print line.

`tests/test_potential_checker.py`:
- `test_teach_9k5_disclosed_ceiling_sentences_are_seen`
- `test_teach_9k5_disclosed_ceiling_sentences_land_in_unclassified_not_classified`
- `test_teach_9k5_disclosed_ceiling_sentences_are_not_falsely_flagged_clean`

No change to any pattern list (`_TRAIT_PATTERNS`, `_COMPARATIVE_PATTERNS`,
`_FUTURE_CLAIM_PATTERNS`, `_GROWTH_PATTERNS`, `_EFFORT_PATTERNS`), to
`_claim_type`, to `check_coverage`, or to `honesty_rubric.py`. This bead
changes disclosure test coverage, not classification behavior.

## What was NOT done, and why it's not a new bead

- No POS-tagging/semantic mechanism was attempted (see "Decision" above —
  this needs a dependency decision plus a different-session generalization
  proof neither of which fits inside this bead).
- Not filing a new bead for "build a syntactic/semantic potential-claim
  classifier" — teach-kmm already noted this as a candidate future direction
  and declined to file it as a formal bead absent a concrete requirement
  forcing it; that reasoning still holds. If a future session wants to
  attempt (a), the requirement is unchanged from what this bead already
  states: a fundamentally different mechanism, verified against held-out
  data from an agent call in a session that did not write the mechanism.

## Verification

- `uv run python -m teach.potential_checker` — self-check passes, including
  the new 18-sentence assertion block.
- `uv run pytest -q` — 191 passed (188 baseline + 3 new tests). No existing
  test changed or removed.

## Caveat for whoever reads this next

Closing (b) here is a statement about *this extraction mechanism's* ceiling,
not about the underlying honesty property. The real lesson text this system
emits is still checked by `dnf_bond_integration`'s `render()`, which reports
`unclassified`/`second_person_unclassified` counts alongside
`check_lesson_text`'s flags — a reviewer reading that output already sees
"N sentences seen, M classified" and knows not to read an empty flag list as
"nothing here overpromises." That disclosure was true before this bead and
remains true after it; this bead's contribution is only proving, with a
concrete held-out set, that the gap it discloses is real and currently
non-trivial (0/18), not closing that gap.
