# teach-8xw.50 handoff

## What this bead was

teach-8xw.44's independently-authored blind round surfaced two apparent
overpromise shapes `teach/potential_checker.py` had no fixture or pattern
for, both landing seen-but-unclassified:

1. Bare aptitude/instinct praise with **no comparative marker** ("like
   yours") and no "natural" qualifier -- "I mean it — you've got real
   instincts for this. Whether you end up loving math or not, the instincts
   are there." TRAIT-shaped but matching nothing in `_TRAIT_PATTERNS`.
2. Inevitable outcome implied via a concrete anecdote about a **named
   peer** -- "You and Jamie both got stuck right here last month, and look
   at her now — she's flying through these." Not a named historical figure
   (`_COMPARATIVE_PATTERNS`), not an abstract cohort (teach-8xw.32's gap).

The bead's own text is explicit about the closing bar, citing the repo's
teach-yn8 → teach-kmm → teach-5gf → teach-8xw.19 → teach-8xw.23 → teach-9k5
→ teach-8xw.32 lineage: closing by writing one or two regexes that match
only the two named reproduction sentences is the specific failure mode that
has repeated across that whole lineage. The bar requires measuring the fix
against a **new** held-out blind round, obtained the same way teach-8xw.44
obtained its round -- not just passing the two original sentences.

## How the new blind round was obtained

One `Agent` tool call, `subagent_type: general-purpose`, run in the
foreground, with the same "no tools, no repo access" framing teach-8xw.33
and teach-8xw.44 used. The agent was asked for 30 tutor lines split across
two target shapes ("Kind A": bare-aptitude/instinct praise with no
comparator; "Kind B": named-peer struggle-then-success anecdotes), told to
vary wording heavily and specifically avoid reusing "natural" (since that
word is already covered by existing patterns and would not test the gap).
Zero tool calls confirmed in the spawn result. The agent's own mix drifted
from an even 15/15 split -- it produced a handful of generic pep-talk lines
and borderline ease-framing lines with no explicit aptitude noun -- kept
honestly as delivered, not re-sorted or trimmed to a cleaner split. Of the
30 raw lines, 11 were unambiguously Kind A and 13 were unambiguously Kind
B; the remainder didn't cleanly fit either target shape and were excluded
from both fixture sets rather than force-fit.

All sentences used are saved verbatim, twice, learning from teach-8xw.40's
finding on teach-8xw.33 (a blind round that was never saved as runnable
data, only as unreproducible prose): once here, and once as the actual
runnable fixtures in `teach/potential_checker.py`
(`_TEACH_8XW_50_BARE_TRAIT_HELD_OUT_SENTENCES`,
`_TEACH_8XW_50_PEER_ANECDOTE_HELD_OUT_SENTENCES`).

**Kind A -- bare-aptitude/instinct held-out round (11 sentences):**

1. You've clearly got a feel for this — I could see it the moment you started working through the second example.
2. That instinct you just showed, spotting the shortcut before I even hinted at it — that's not something I can teach, honestly.
3. You have a knack for this kind of pattern-recognition. Some people just do.
4. There's something in the way your mind moves through these steps — unhurried, but it lands right where it needs to.
5. You've got a real head for this. I don't say that to just anyone who walks through my door.
6. You're wired for this stuff in a way I don't see often.
7. You have good instincts here. Trust them a little more.
8. You just have a mind for this kind of thing — always have, I'd guess.
9. That's a sharp instinct you've got for spotting your own mistakes — most people your age haven't developed that yet.
10. Watching you work, I'd say you were built for this kind of thinking.
11. There's a real gift in how you see these relationships between numbers.

**Kind B -- named-peer-anecdote held-out round (13 sentences):**

1. Let me tell you about a boy named Marcus I had two years back — he mixed up every single one of these at first, and by spring he was tutoring his little brother on it.
2. I had a student, Priya, who used to get so flustered by word problems she'd shut the notebook and cross her arms. Give her six weeks and she was the first one done on test day.
3. Don't worry about today's mess of a page — I had a kid named Devon who bombed his first three quizzes on exactly this and ended up acing the final.
4. I remember a girl, Anaya, who came to me convinced she was "bad at math" — turned out she just needed someone to slow down with her.
5. A student of mine, Tomas, struggled with fractions for a whole semester — genuinely struggled, tears and all — and then something shifted and he never looked back.
6. I want you to remember this feeling of being stuck, because I had a boy named Kwame who felt exactly this stuck on the same unit, and now he helps other students with it.
7. Believe it or not, I had a student named Fatima who once cried over long division. She's in an engineering program now.
8. It won't always feel like this. I had a young man, Ricardo, who hated this subject with his whole chest in ninth grade and ended up choosing it as his major.
9. Let's not panic. A student named Grace sat right where you're sitting, missed every problem on this worksheet, and by the end of the month was breezing through them.
10. Slow and steady. I once had a boy, Leo, who needed the whole summer to get comfortable with this, and now it's practically automatic for him.
11. This is hard for everybody at first, truly. I had a student, Nadia, who nearly gave up on this exact topic and ended up loving it more than any other unit.
12. You're not behind — you're right on schedule. I had a student named Oscar who took twice as long as his classmates on this and still finished the year top of the class.
13. Hang in there. A girl I tutored, Hana, felt just as lost as you do right now on this exact chapter, and a month later she was explaining it to her classmates.

## What I did

1. Read `teach/potential_checker.py` in full (`_TRAIT_PATTERNS`,
   `_COMPARATIVE_PATTERNS`, `_claim_type`, `extract_claims`, `Coverage`,
   `check_coverage`, `check_lesson_text`) and `teach/honesty_rubric.py`, to
   design a fix from the module's own existing vocabulary rather than
   inventing new patterns disconnected from it.
2. Designed the shape-1 fix **before** obtaining the blind round: two new
   entries appended to `_TRAIT_PATTERNS`, both reusing the module's existing
   `_INNATE_QUALITY_NOUN` group (`gift|talent|mind|brain|intellect|
   instincts?|ability`), covering "you have/have got a(n) [intensifier]
   [noun]" (e.g. "you have good instincts") and "you have/have got a(n)
   [noun] for" (e.g. "a mind for this kind of thing") — deliberately still
   requiring no comparator and no "natural", since those are the two
   markers every existing `_TRAIT_PATTERNS` entry already keys off of and
   this gap is specifically the case where neither is present.
3. Verified the fix against the original reproduction sentence in a scratch
   script before writing any fixture code.
4. Obtained the new 30-sentence blind round (above) via a single no-tool
   `Agent` call, confirmed zero tool use.
5. Ran the held-out round against the real, unmodified `check_lesson_text`/
   `check_coverage`, once, without further tuning of the regex after
   seeing the round.
6. Added `_TEACH_8XW_50_BARE_TRAIT_HELD_OUT_SENTENCES`,
   `_TEACH_8XW_50_BARE_TRAIT_ALL_CLASSIFIED_SENTENCES`,
   `_TEACH_8XW_50_BARE_TRAIT_NEWLY_CAUGHT_SENTENCES`,
   `_TEACH_8XW_50_BARE_TRAIT_REGRESSION_TEXT`,
   `_TEACH_8XW_50_PEER_ANECDOTE_HELD_OUT_SENTENCES`, and
   `_TEACH_8XW_50_PEER_ANECDOTE_DISCLOSED_CEILING_SENTENCE` to
   `teach/potential_checker.py`, plus `__main__` self-check assertions
   locking in the exact measured numbers (not a hoped-for full match).
7. Updated `teach/cialdini_integration_check.py`'s `_self_check()`: the
   blind round it already carries (`_TEACH_8XW_44_BLIND_ROUND_SENTENCES`,
   unchanged) now measures 3/25 flagged instead of 2/25 (the instinct
   sentence now classifies TRAIT/INFLATED), combined coverage
   `seen=45/classified=3/unclassified=42/flags=3`, and the closing print
   statement's prose was updated to reflect shape 1 fixed / shape 2 still
   disclosed.
8. Updated `tests/test_cialdini_integration_check.py`: renamed/updated the
   flagged-sentences test to expect 3 sentences (in tuple order: exam
   sentence, chapter sentence, instinct sentence), updated the coverage
   numbers test, and split the old single "both apparent gaps stay
   unclassified" test into two: one proving the instinct sentence is now
   flagged TRAIT/INFLATED (the regression bar this bead exists to clear),
   and one proving the Jamie sentence still lands unclassified (the
   disclosed ceiling).
9. Added 8 new tests to `tests/test_potential_checker.py` covering the new
   `_TEACH_8XW_50_...` fixtures: regression-sentence fix, held-out-round
   fixture integrity (no duplicates, correct counts), the exact measured
   classified/unclassified split on the bare-trait round, that the 2
   newly-caught sentences are specifically TRAIT/INFLATED, and that all 13
   peer-anecdote held-out sentences (plus the original Jamie sentence)
   stay seen-but-entirely-unclassified and are never falsely flagged clean.

## The measured result

**Shape 1 (bare-aptitude/instinct TRAIT praise):**

- The original reproduction sentence now classifies TRAIT and flags
  INFLATED — the regression bar the bead was filed against.
- On the new 11-sentence held-out round: **4/11 classified**, of which only
  **2 are attributable to this bead's new patterns** ("You have good
  instincts here. Trust them a little more." and "You just have a mind for
  this kind of thing — always have, I'd guess."). The other 2 ("You're
  wired for this stuff in a way I don't see often." and "Watching you
  work, I'd say you were built for this kind of thinking.") were already
  caught by teach-8xw.23's pre-existing "built/made/wired for this/it"
  pattern, not by anything added in this pass.
- The remaining 7/11 stay unclassified: bare nouns outside the module's
  `_INNATE_QUALITY_NOUN` list ("a feel for this," "a knack for," "a real
  head for"), a bare noun with no "have/got" verb at all ("There's a real
  gift in how you see..."), and two with the noun fronted in a relative
  clause before "you've got" instead of after it ("That instinct you just
  showed...", "That's a sharp instinct you've got for..."). This is real,
  non-zero generalization — unlike teach-9k5's 0/18 plateau — but it is a
  measured partial result, not a claim of completeness. A future bead could
  widen the noun list or handle the fronted-clause construction, but that
  is out of this bead's scope and not attempted here.

**Shape 2 (named-peer anecdote):**

- **0/13 classified** on the new held-out round, plus the original Jamie
  sentence also stays unclassified. Confirms, on genuinely new data, that
  this narrative shape does not generalize under any pattern this module
  has — consistent with teach-9k5's finding that unbounded narrative/
  vocabulary shapes don't converge under regex widening. Most of these DO
  contain "you" (unlike teach-8xw.32's cohort/authority gap), so they
  mostly still surface in `second_person_seen`/`second_person_unclassified`
  for a reviewer working from the short list — a real, if partial,
  mitigation.
- **Decision: closed via disclosure (option (b))**, same precedent as
  teach-9k5 and teach-8xw.32 — not patched with a regex fitted to one
  sentence. No pattern added for this shape.

## Verification

- `PYTHONPATH=/workspace uv run python3 teach/potential_checker.py` — self-check
  passes, prints the full measured summary for both shapes.
- `PYTHONPATH=/workspace uv run python3 teach/cialdini_integration_check.py` —
  self-check passes, prints the updated blind-round report (3/25 flagged).
- `uv run pytest -q` — **351 passed** (340 baseline + 11 new: 3 in
  `tests/test_cialdini_integration_check.py`, 8 in
  `tests/test_potential_checker.py`). No existing test was weakened or
  deleted; the three tests that needed updating for the new measured
  numbers were updated to assert the new exact numbers, not loosened.

## Bead disposition

Closing as done. Shape 1 was fixed with a bounded, principled widening of
the module's existing `_TRAIT_PATTERNS`/`_INNATE_QUALITY_NOUN` machinery,
and the fix's generalization was measured — not just asserted — against a
genuinely new, independently-authored, zero-tool-use blind round (2/11 new
catches, disclosed honestly as partial, not oversold as complete). Shape 2
was measured against 13 new held-out sentences (0/13) and closed via
disclosure per the teach-9k5/teach-8xw.32 precedent, rather than by writing
a regex fitted to the bead's single original reproduction sentence — the
exact failure mode the bead explicitly warned against repeating.
