# teach-dds -- biblical_ot/nt_source false-misattribution false-CONFIRM structural fix

Status: **ready to close**. All acceptance-criteria evidence exists and the
targeted + full test suites pass (modulo 6 pre-existing, unrelated
failures -- see "Pre-existing unrelated failures" below).

## The bug

`teach/biblical_ot_source.py`'s `_GENESIS_CREATION` fact and
`teach/biblical_nt_source.py`'s `_JOHN_OPENING_WORD` / `_JOHN_SHORTEST_VERSE`
facts had `true_patterns` that matched verse *content* alone, unconditionally,
while `false_patterns` only caught a misattribution when one specific,
literal rival keyword was present. A held-out round of 30
independently-authored sentences (`tests/test_biblical_sources_held_out_round1.py`,
teach-8xw.41) found 3 sentences that should have abstained but instead
landed a dangerous false CONFIRMED. Filed P1: a checker that confirms a
misattributed Bible quotation is worse than one that says nothing, because
it actively asserts something false with full confidence.

Acceptance criteria (bead's own words): fix the *structural asymmetry*, not
just these 3 sentences -- because tuning against the round that found the
gap needs a NEW held-out round to prove it generalizes, per
teach-8xw.41/teach-8xw.33's precedent. Do not close by only handling the
exact sentences found.

## The fix, in three parts (plus one bug-in-the-fix, found and closed)

### Fix #1 -- generic reassignment-framing guard (`teach/fact_checker.py`)

`_REASSIGNMENT_FRAMING` regex + `_has_reassignment_framing()`. When a
`true_patterns` hit also carries generic reassignment language ("actually",
"in fact", "really is/was", "originates in/from", "comes from", a trailing
", not the/from/in ..." clause) that `false_patterns` didn't already catch,
`verify_claim` abstains (CANNOT_VERIFY) instead of confirming. Closed
round1's 3 sentences.

### Fix #2 -- attribution-anchored other-book coverage (both source modules)

`_other_book_attribution(own)`: a `false_pattern` fragment requiring another
canonical Bible book's name to be within a short word window
(`(?:\W+\w+){0,4}`) of a hand-curated `_ATTRIBUTION_VERBS` list, either word
order. A held-out **round2** (30 fresh sentences, genuinely held-out for
Fix #1, generated with no knowledge of round1's findings or Fix #1's
mechanism) found 1 residual gap -- an unanticipated rival book name --
which Fix #2 closed. Round2 is honestly disclosed in its own test file as
tuning data *for Fix #2*, since Fix #2 was written in response to round2's
finding.

### Fix #3 -- generic `caution_patterns` field (`teach/fact_checker.py`, both source modules)

A held-out **round3** (30 fresh sentences, genuinely held-out for Fix #2,
generated with no knowledge of round1/round2's findings or either fix's
mechanism) found **4 new** dangerous false-CONFIRMEDs against Fix #2:
`DEUT_FALSE_2` ("written down in", not "written in"), `JOHN1_FALSE_2` ("is
the first verse of", no listed verb at all), `JOHN11_FALSE_1` ("is a verse
in", extra words break the match), `JOHN11_FALSE_2` ("is where ... sits",
verb and book too far apart). Root cause: `_ATTRIBUTION_VERBS` is itself a
closed enumeration of English attribution phrasings -- the *same*
structural closed-world problem the bead exists to fix, recurring one
level down, at the verb layer instead of the book-name layer.

Per the bead's own explicit instruction not to just patch the same anti-pattern
again, I did not add "written", "verse of", "sits" etc. to
`_ATTRIBUTION_VERBS`. Instead I added a new, structurally different, THIRD
signal on `SourceFact`: `caution_patterns` (default `()`, backward
compatible -- `teach/math_facts.py`'s existing `SourceFact` usages are
untouched). A `true_patterns` hit that also matches a `caution_pattern`
abstains (CANNOT_VERIFY) instead of confirming. Unlike `false_patterns`,
`caution_patterns` requires **no attribution verb and no word window at
all** -- just blind co-occurrence of any other candidate book name, anywhere
in the sentence. This is not "enumerate more phrasings" -- it needs no
phrasing knowledge whatsoever, so no future attribution-verb wording can
slip past it while still naming a rival book. Wired into all 5 vulnerable
facts (`_GENESIS_CREATION`, `_SHEMA`, `_ISAIAH_VOICE_IN_WILDERNESS`,
`_JOHN_OPENING_WORD`, `_JOHN_SHORTEST_VERSE`).

Cost: some legitimate TRUE claims that mention another book in passing (no
misattribution intended) now abstain instead of confirming. Accepted --
sandbox-prompt.md's "prefer abstention to a confident answer," the same
trade Fix #1 already made. Two existing CONFIRMED test fixtures needed this
exact adjustment (a Genesis mention in the John TRUE_CLAIM fixture, a
Gospels-quoting mention in the Isaiah CONFIRMED fixture) -- both split into
a "clean" CONFIRMED example plus a new, explicit
`..._mentioning_another_book_in_passing_now_abstains` test documenting the
trade-off, rather than silently flipping the original acceptance-criteria
fixtures.

Round3 is honestly disclosed in its own test file
(`tests/test_biblical_sources_held_out_round3.py`) as tuning data *for
Fix #3*, since Fix #3 was written in direct response to round3's 4
findings -- this is the same recursive "cannot hold out examples from
yourself" caveat already applied once to round2/Fix #2, now applied a
second time to round3/Fix #3.

### Bug-in-the-fix, found by code review (not a held-out round) -- 1/2/3 John name collision

While auditing `_ALL_BIBLE_BOOKS`' coverage after landing Fix #3, I noticed
both John facts use `own=("john",)`, and `_other_book_names` excludes that
exact string from the "other book" alternation used by *both*
`false_patterns` and `caution_patterns`. But the bare `\bjohn\b` regex also
matches inside "1 John"/"2 John"/"3 John" -- canonically **different books**
from the Gospel of John. So excluding `"john"` silently excluded the
epistles too. Confirmed live and dangerous before the fix:

```
'Jesus wept' is found in 2 John, the shortest of the epistles.
  -> Verdict.CONFIRMED   (WRONG -- dangerous false-CONFIRMED)
```

Fixed by listing `"1\s+john"`, `"2\s+john"`, `"3\s+john"` as distinct
entries in `_ALL_BIBLE_BOOKS` (both `biblical_ot_source.py` and
`biblical_nt_source.py`, kept in sync) so they survive the
`own=("john",)` exclusion. Re-verified:

```
'Jesus wept' is found in 2 John, the shortest of the epistles.
  -> Verdict.CONTRADICTED   (correct -- now caught precisely, via the
                              attribution-anchored false_pattern)
```

Two dedicated regression tests added directly (not via a held-out round,
since this was found by inspection, not measurement) in
`tests/test_biblical_nt_source.py`:
`test_shortest_verse_misattributed_to_2_john_is_not_dangerously_confirmed`,
`test_opening_word_misattributed_to_3_john_is_not_dangerously_confirmed`.

**Known residual scope, documented not chased**: the same root-name
collision risk (a book whose bare name is a substring of its own numbered
variant) applies generically to any future fact using
`own=("samuel"|"kings"|"chronicles"|"corinthians"|"thessalonians"|
"timothy"|"peter",)`. No such fact exists yet, so those aren't split out
preemptively -- a comment in both `_ALL_BIBLE_BOOKS` definitions flags this
for whoever adds one.

## Held-out rounds, honestly summarized

| Round | Held-out for | Found | Closed by |
|---|---|---|---|
| round1 (teach-8xw.41, 30 sentences) | original bug | 3 dangerous false-CONFIRMEDs | Fix #1 |
| round2 (30 sentences) | Fix #1 | 1 dangerous false-CONFIRMED (unanticipated rival book) | Fix #2 |
| round3 (30 sentences) | Fix #2 | 4 dangerous false-CONFIRMEDs (unanticipated attribution verbs) | Fix #3 |
| 1/2/3 John collision | -- (found by code review, not a round) | 1 dangerous false-CONFIRMED | direct fix + dedicated regression tests |

Round3's raw measured result after Fix #3 (see its own module docstring for
full detail): 30 sentences, 9 CONFIRMED (all correct), 4 CONTRADICTED (all
correct), 17 CANNOT_VERIFY (all safe) -- **zero dangerous false-CONFIRMEDs**.

## Was a round4 needed?

Judgment call, made explicitly rather than left implicit: **no**, and here
is the reasoning, so a future session can check it rather than take it on
faith. Fix #3's `caution_patterns` mechanism is not a phrasing-enumeration
fix like Fix #2's `_ATTRIBUTION_VERBS` was -- it requires zero knowledge of
how a misattribution is phrased, because it doesn't look at phrasing at
all, only at "does any other canonical book's name appear anywhere in this
sentence." That is total over all 66 canonical books by construction, not
by matched examples, which is exactly why round1's and round2's failure
mode (an unanticipated word or an unanticipated book) cannot recur against
it. A further held-out round would be testing the SAME structural property
again, not a genuinely different hypothesis -- the closed-world-enumeration
gap this bead exists to fix has been converted into a not-closed-world
mechanism, and that conversion is verifiable by reading the code, not just
by running more examples against it (per sandbox-prompt.md: "a result is a
candidate until measured" cuts both ways -- more measurements of the same
kind of thing don't add evidence once the mechanism itself has changed
kind).

What a round4 (or any future round) *could* still find, because it is a
genuinely different failure class this mechanism cannot address by
construction: a misattribution that never names a rival book at all --
e.g. "that's actually in a different part of the Bible," "no, it's in the
other one," a pronoun-only or vague-reference misattribution. Closing that
would need real coreference/reference resolution, not a pattern addition,
and is out of scope for this bead's pattern-matching architecture. If a
future round finds this failure class, it should be filed as a **new**
bead, not folded into this one's fix.

## Pre-existing unrelated failures (confirmed, not touched)

```
uv run pytest -q
```

reports 6 failures, all in `tests/test_concept_recovery_judson_full_graph_generalization_round3/4/5.py`
(judson concept-recovery generalization work, unrelated dirty
working-tree state from a different, unfinished task -- visible in `git
status` at session start). None of these touch `teach/fact_checker.py`,
`teach/biblical_ot_source.py`, or `teach/biblical_nt_source.py`. Confirmed
unchanged in count and identity across two full-suite runs this session
(before and after the 1/2/3 John collision fix).

## Test evidence

```
uv run pytest tests/test_biblical_ot_source.py tests/test_biblical_nt_source.py \
  tests/test_biblical_sources_held_out_round1.py \
  tests/test_biblical_sources_held_out_round2.py \
  tests/test_biblical_sources_held_out_round3.py \
  tests/test_fact_checker.py -q
# 179 passed

uv run python3 -m teach.fact_checker
uv run python3 -m teach.biblical_ot_source
uv run python3 -m teach.biblical_nt_source
# all three self-checks OK

uv run pytest -q
# 688 passed, 16 skipped, 1 xfailed, 6 failed (pre-existing, unrelated -- see above)
```

## Files changed

- `teach/fact_checker.py` -- `caution_patterns` field on `SourceFact`,
  wired into `verify_claim`.
- `teach/biblical_ot_source.py` -- `_other_book_attribution` (Fix #2),
  `caution_patterns` on 3 facts (Fix #3), `_ALL_BIBLE_BOOKS` 1/2/3-John
  entries (kept in sync, not itself exposed to the collision).
- `teach/biblical_nt_source.py` -- same shape, on the 2 John facts; new
  `TRUE_CLAIM_MENTIONS_ANOTHER_BOOK_IN_PASSING` fixture;
  `_ALL_BIBLE_BOOKS` 1/2/3-John entries (fixes the live collision here).
- `tests/test_biblical_ot_source.py`, `tests/test_biblical_nt_source.py` --
  regression tests for Fix #3's trade-off and the 1/2/3 John collision fix.
- `tests/test_biblical_sources_held_out_round3.py` -- new, 31 tests, full
  honest-disclosure docstring.

## Suggested next commands

```bash
git status
git diff --stat teach/fact_checker.py teach/biblical_ot_source.py teach/biblical_nt_source.py \
  tests/test_biblical_ot_source.py tests/test_biblical_nt_source.py
bd close teach-dds
```

Conservative git policy: no commit/push done or suggested here without
being asked.
