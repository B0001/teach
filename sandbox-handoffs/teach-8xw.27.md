# teach-8xw.27 — concept_recovery: a prerequisite announced across two sentences was wrongly reported as unsignposted

## What was wrong

`concept_recovery.recover_assumed_prerequisites` required an "already-known"
signal phrase (e.g. "you already know", "recall") and a prerequisite node's
distinctive vocabulary to appear in the *same sentence*. An ordinary teaching
pattern — announce, then elaborate in the next sentence, possibly with a
short acknowledgment in between ("Remember X from last year? Great. Now
we'll build on it, using Y...") — routinely splits the cue from the content
across sentence boundaries, so this text was wrongly classified as
UNSIGNPOSTED (silently assumed) even though it explicitly announced the
prerequisite.

Reproducing the bead's exact repro turned up a second, distinct problem: the
literal example text, `"Remember polygons from last year?"`, did not match
*any* existing `_ASSUMED_KNOWN_PATTERNS` regex at all — `remember (when|how|
that)` requires one of those three words immediately after "remember", and
`last (year|grade|time) you` requires "you" directly after "last year",
neither of which this phrasing has. So the same-sentence rule was not
actually the proximate cause of the bug in the bead's literal repro command;
no cue fired anywhere in the text, at any window size. I verified this by
testing a window-only fix (same regex, wider co-occurrence check) against
the exact repro command — it still returned `unsignposted: ('va-math-sol:
3.MG',)`. Both a regex gap and a same-sentence-only window needed fixing to
close this bead; fixing only one would not reproduce the bead's stated
"assumed: ('va-math-sol:3.MG',)" expectation.

## What was built

Two changes in `teach/concept_recovery.py`, both narrowly scoped:

1. **New cue pattern**: `\bremember\b(?!\s+to\b)` — a bare "remember
   &lt;noun phrase&gt;" (as in "Remember polygons?") is now recognized as an
   already-known signal, same as `remember (when|how|that)`. Excludes
   "remember to &lt;verb&gt;" (e.g. "remember to bring your homework"),
   which is a forward-looking instruction, not a recall-of-prior-content
   cue. Confirmed no existing fixture anywhere in `teach/` or `tests/` used
   the word "remember" before this change (`grep -rniE remember`), so this
   addition could not silently change any other test's outcome.

2. **Widened co-occurrence window**: `recover_assumed_prerequisites` now
   checks vocabulary overlap against the cue sentence *plus the next
   `_ASSUMED_KNOWN_WINDOW_SENTENCES` (=2) sentences*, not just the cue's own
   sentence. The window is forward-only (cue, then elaboration) — that
   matches ordinary teaching dialogue and deliberately does not look
   backward, so a prerequisite's vocabulary appearing *before* an unrelated
   cue elsewhere in the text is not swept in.

Module docstring's prerequisite-recovery section and the new constant both
document the reasoning; see `teach/concept_recovery.py` lines ~85-97 and
~145-158.

## Evidence this fixes the actual bug (not just the literal repro)

`tests/test_concept_recovery.py::test_two_sentence_announcement_recovered_against_the_real_graph`
runs the bead's exact repro command against the real VA Math SOL graph and
asserts `assumed_prerequisite_ids == ("va-math-sol:3.MG",)`,
`unsignposted_prerequisite_ids == ()`.

Per the bead's explicit ask ("verify the fix doesn't just patch this exact
two-sentence example... check it against a few independently-phrased
multi-sentence announcement patterns"):

`test_assumed_prerequisite_recognized_across_a_short_discourse_gap` — one
synthetic 2-node graph, five *different* cue phrasings (`"You already know
this."`, `"Recall what we did before."`, `"You've already learned plenty."`,
`"Last year you covered a lot."`, `"Remember what we did?"`), each followed
by a filler sentence then the sentence carrying the prerequisite's
vocabulary — all five must recover the prerequisite as assumed, not
unsignposted. This is not just the "remember" phrasing the bug was filed
against; four of the five cues already matched the pre-existing regex set
and only failed before this fix because of the same-sentence restriction.

Per the bead's explicit ask that the fix "not just make the flag fire less
often across the board" and that the true-unsignposted case still fires:

`test_window_does_not_rescue_a_prerequisite_with_no_nearby_cue` — a graph
with *two* direct prerequisites of the taught node. One ("a") is properly
announced within the cue's window and must be `assumed`. The other ("c") is
used later in the same lesson, outside any cue's window, even though a real
cue phrase exists elsewhere in the text (announcing "a", not "c") — "c" must
still be `unsignposted`, proving the window doesn't degenerate into "any cue
anywhere covers everything."

All pre-existing tests are unmodified and pass unchanged, including the ones
that specifically guard against over-triggering:
`test_assumed_prerequisite_requires_signal_phrase_not_just_overlap` (no cue
anywhere → empty, unaffected by window since there's no signaled sentence to
window from), `test_unsignposted_and_assumed_are_mutually_exclusive`,
`test_unsignposted_detection_only_considers_direct_prerequisites`,
`test_only_direct_prerequisite_edges_are_considered`.

## Verification

```
uv run pytest -q                       # 243 passed (was 240; +3 new tests)
uv run pytest tests/test_concept_recovery.py -v   # 20/20 passed
uv run python -m teach.concept_recovery            # OK, same recover/abstain pair as before
```

Manually re-ran the bead's exact repro command:
```
taught: va-math-sol:4.MG
assumed: ('va-math-sol:3.MG',)
unsignposted: ()
```

## Files touched

- `teach/concept_recovery.py` — new `_ASSUMED_KNOWN_WINDOW_SENTENCES`
  constant, one new regex in `_ASSUMED_KNOWN_PATTERNS`,
  `recover_assumed_prerequisites` rewritten to build a word-window per
  signaled sentence instead of checking that sentence alone. Docstring
  updated (prerequisite-recovery section + new function docstring).
- `tests/test_concept_recovery.py` — 3 new tests (see above).
- `bd remember teach-8xw-10-concept-recovery-design` updated in place: point
  (4) revised to describe the window instead of strict same-sentence
  co-location; new point (5) documents the bare-"remember" cue addition.

Nothing committed — conservative git policy, not asked to commit.

## Follow-up

None filed. The window size (2 sentences forward) is a judgment call, not
derived from a corpus — if a future worker finds a real lesson where the
elaboration is more than 2 sentences past the cue, that's a new, separate
bead with its own repro, not something to guess at now.
