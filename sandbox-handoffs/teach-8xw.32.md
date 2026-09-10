# teach-8xw.32 — group-generalization / cited-authority shapes are invisible to _claim_type, and miss the second-person short-list too

## Decision: closed via option (b), following teach-9k5's precedent

The bead named two honest closes: (a) a fundamentally different
classification mechanism, proven against held-out evidence from an agent
call in a DIFFERENT session than the one that wrote the mechanism, or (b) an
explicit decision to extend the disclosed-ceiling regression fixture to
cover this shape family too, closed as a documented additional ceiling.

This session took (b), for the same structural reason teach-9k5 did:

- The bead's own four reproduction sentences were written by whoever filed
  the bead, in this same lineage of sessions — not held-out evidence from an
  agent call blind to this repo's patterns. Writing four regexes to match
  exactly those four sentences would score 4/4 against a same-session set
  and prove nothing about the next independently-phrased round of
  cohort/authority claims. That is precisely the failure mode this repo's
  lineage (teach-yn8 → teach-kmm → teach-5gf → teach-8xw.19 → teach-8xw.23)
  has already repeated four times, most recently measured at 0/18 in
  teach-9k5.
- teach-9k5 already established, and this session did not find reason to
  revisit, that option (a)'s own requirement — generalization evidence from
  an agent call in a session that did not write the mechanism — is
  structurally unreachable from a single work session: whoever writes the
  mechanism is also the one who would have to arrange the blind held-out
  test, which breaks the "different session" requirement by construction.
- The bead's own text names (b) as "probably the more honest default unless
  someone has a concrete non-lexical mechanism in mind." No such mechanism
  was available (same `spacy`/`nltk`-absent constraint teach-9k5 already
  checked; `pyproject.toml` still has no NLP dependency), so this session
  did not attempt one.

## What was verified before deciding

Reproduced the bead's own measurement against current `main` before touching
anything:

```
uv run python3 -c "
from teach.potential_checker import check_lesson_text, check_coverage
sentences = [
    'Everyone who masters cosets goes on to breeze through Lagrange Theorem.',
    'Mathematicians agree that a student who reasons like this is on track for real results.',
    'Students who reach this point almost always go on to master group theory with ease.',
    'Only a handful of students each year make it this far in the material.',
]
for s in sentences:
    print(s[:50], '->', check_lesson_text(s))
    c = check_coverage(s)
    print('  seen=%d classified=%d unclassified=%d second_person_seen=%d' %
          (len(c.seen), len(c.classified), len(c.unclassified), len(c.second_person_seen)))
"
```

Confirmed exactly as the bead states: all four sentences land
`seen=1, classified=0, unclassified=1, second_person_seen=0`. `check_lesson_text`
returns `()` for each. This also confirmed the bead's sharper claim: these
sentences aren't silently dropped by the *general* disclosure mechanism
(`dnf_bond_integration.py`'s `render()` does print the full `cov.unclassified`
list, including these) — the specific, worse gap is that they are 0/4 on
`second_person_seen`, so a reviewer following the teach-8xw.20 short-list
workflow (reading only `second_person_unclassified`) would never see them,
unlike (part of) teach-9k5's mixed pronoun/no-pronoun set.

## What was built

Not a new pattern — a permanent regression fixture and tests proving the
disclosure holds for this shape family too, and proving the specific new
finding (0/4 on `second_person_seen`, not just 0/4 classified).

`teach/potential_checker.py`:
- Added `_TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES` (the bead's four
  sentences, verbatim), with a comment documenting why this is a distinct
  shape family from teach-9k5's (cohort-generalization / third-party
  authority attribution, never naming or addressing the learner directly,
  vs. teach-9k5's direct-to-learner praise) and why (b) was chosen over (a).
- Extended the `__main__` self-check with an assertion block: all four are
  seen, unclassified, absent from `second_person_seen`, and produce zero
  flags from `check_lesson_text`.
- Updated the self-check's summary print line.
- Added a caveat to `Coverage`'s docstring noting this second blind spot in
  `second_person_seen` alongside the one teach-8xw.19/teach-8xw.20 already
  documented there.

`tests/test_potential_checker.py`:
- `test_teach_8xw_32_disclosed_ceiling_sentences_are_seen`
- `test_teach_8xw_32_disclosed_ceiling_sentences_land_in_unclassified_not_classified`
- `test_teach_8xw_32_disclosed_ceiling_sentences_are_not_falsely_flagged_clean`
- `test_teach_8xw_32_disclosed_ceiling_sentences_miss_second_person_subset` —
  the test that locks in this bead's specific new finding, not just a repeat
  of teach-9k5's coverage of "seen+unclassified."

No change to any pattern list (`_TRAIT_PATTERNS`, `_COMPARATIVE_PATTERNS`,
`_FUTURE_CLAIM_PATTERNS`, `_GROWTH_PATTERNS`, `_EFFORT_PATTERNS`,
`_SECOND_PERSON_REFERENCE`), to `_claim_type`, to `check_coverage`'s logic,
or to `honesty_rubric.py`. `dnf_bond_integration.py` was not touched — it
already prints the full `cov.unclassified` list unconditionally, so these
four sentences were already reaching a reviewer who reads that far; this
bead's contribution is proving that concretely and proving the
second-person short-list specifically misses them, not fixing a silent-drop
bug (there wasn't one at that layer).

## What was NOT done, and why it's not a new bead

- No cohort-quantifier / third-party-attribution pattern list was added to
  `_claim_type` or to a new `Coverage` subset. Per the bead's own explicit
  instruction, four sentences is not evidence such patterns generalize, and
  this repo's lineage has measured that exact failure mode four times
  already.
- No POS-tagging/semantic mechanism was attempted — same reasoning as
  teach-9k5: no NLP dependency is available, and adding one plus building a
  genuinely different classifier is a design decision outside a single
  bug-fix bead, especially one whose own bead text recommends (b) as the
  default.
- Not filing a new bead for "build a syntactic/semantic potential-claim
  classifier" — teach-kmm and teach-9k5 already noted this as candidate
  future work and declined to file it absent a concrete requirement forcing
  it. That reasoning still holds; if a future session attempts it, the
  requirement is unchanged: a fundamentally different mechanism, verified
  against held-out data from an agent call in a session that did not write
  the mechanism.

## Verification

- `uv run python -m teach.potential_checker` — self-check passes, including
  the new teach-8xw.32 assertion block.
- `uv run pytest -q` — 203 passed (199 baseline for this file's suite plus
  the 4 new tests; full repo suite, no test removed or changed elsewhere).
- `uv run pytest -q -k teach_8xw_32 -v` — all 4 new tests pass in isolation.

## Caveat for whoever reads this next

Closing (b) here, like teach-9k5, is a statement about *this extraction
mechanism's* ceiling for a second shape family, not about the underlying
honesty property. `dnf_bond_integration.py`'s `render()` still reports the
full `unclassified` count alongside the narrower second-person subset, so a
reviewer reading the whole render output (not just the short list) already
sees these four sentences disclosed as unchecked. What this bead adds to the
record is that the short-list workflow specifically — which teach-8xw.20
built as the thing "a reviewer is meant to read" per this bead's own
framing — has a real, now-measured blind spot for claims that generalize
over a cohort or cite an authority instead of addressing the learner
directly. If the Cialdini social-proof/authority layer named in teach-8xw.31
is ever built into the producer, this is exactly the shape it would emit,
and it would currently pass the short-list review clean while still showing
up (correctly, just not prominently) in the full unclassified total.
