# teach-8xw.26 — concept_recovery: faithful paraphrase of real graph content causes total abstention

## What was wrong

`concept_recovery.recover_taught_concept` matches lesson text against a
graph node's distinctive vocabulary by raw exact-word overlap only — no
stemming, no synonyms (a known, disclosed limitation per bd memory
`teach-8xw-10-concept-recovery-design`). The bead's reproduction showed this
was not just a theoretical gap: a faithful, no-invention paraphrase of
`va-math-sol:4.MG`'s real leaf standards ("rules" for formulas, "space
covered" for area, "four-sided shapes with square corners" for
rectangles/squares, "tell apart... by properties" for classify, "crossing"
for intersecting) shared almost no literal vocabulary with 4.MG, so its raw
score (3) collapsed to a near-tie with two unrelated nodes (7.MG=2, 8.MG=2)
and the checker abstained with "ambiguous match" — on text a real
persona-rendering pass is likely to produce, per teach-8xw.6's whole
purpose.

I also found, while investigating, that even the *exact* source words
"area", "perimeter", and "squares" would not have saved this: their
document frequency across the VA Math SOL graph is 6, 5, and 6 respectively
(> `_MAX_DOCUMENT_FREQ` = 4), because those topics legitimately recur across
several grades in a spiraling curriculum. The boilerplate filter that keeps
grade-to-grade phrasing from tying nodes together also strips genuinely
distinctive-to-this-lesson words that happen to recur across grades. That's
a real, separate tension worth someone's attention eventually, but I did not
touch `_MAX_DOCUMENT_FREQ` or the document-frequency mechanism — it's out of
this bead's scope and changing it risks the exact regressions
`test_build_vocabulary_index_filters_boilerplate_words` and the coverage-
tiebreak tests guard against.

## What was built

A new **semantic fallback tier** in `teach/concept_recovery.py`, added
strictly as a second chance after raw exact-word scoring, never as a
replacement for it:

- `score_candidates_semantic(text, index)` — same shape and ranking as
  `score_candidates`, but a node's distinctive word counts as matched if
  the text contains that exact word, its WordNet lemma (`_lemma`, via
  `nltk.stem.WordNetLemmatizer`), or a word in its WordNet synonym
  neighborhood (`_synonym_lemmas`, built generically from `wordnet.synsets`
  across all parts of speech — the same mechanism for every word in every
  domain, not a table curated to this bead's specific wording, per
  sandbox-prompt.md's "you cannot hold out examples from yourself").
- `recover_taught_concept` now: runs raw `score_candidates` first; if and
  only if that abstains (no candidate clears `_MIN_MATCH_WORDS`, or the
  margin/coverage-tiebreak logic can't resolve it), it re-scores with
  `score_candidates_semantic` and applies the **same** abstention machinery
  — refactored out of the old inline body into `_resolve_candidates`, now
  shared by both tiers — before giving up. A lesson the raw tier already
  resolves is untouched: this cannot change the outcome for any
  already-working case (verified — see below).
- `_SEMANTIC_MIN_MARGIN = 3`, stricter than the raw tier's `_MIN_MARGIN =
  2`. This constant exists because of a real false positive the
  generalization measurement caught (below) — WordNet synonym links
  include ordinary-English pairs with zero domain content ("want"/
  "require", "answer"/"solution"), so the semantic tier's raw margin-2 bar
  let a wrong node win once. Margin 3 rejects that case while still
  resolving both this bead's own reproduction (margin 3 exactly) and every
  genuine recovery the generalization set needed the semantic tier for
  (margin >= 5).
- Graceful degradation: `_wordnet_lemmatizer()` tries to load the corpus,
  attempts a one-time `nltk.download("wordnet", quiet=True)` if missing,
  and returns `None` on any failure — every caller then treats a word as
  its own lemma with no synonym expansion (i.e. the semantic tier
  contributes nothing, never crashes, never guesses). Added `nltk` as a
  project dependency (`pyproject.toml`); the wordnet corpus itself is not
  vendored and downloads on first use if not already cached locally in
  this environment (confirmed present at `/home/node/nltk_data` in this
  sandbox from earlier exploration this session).

## Generalization measurement (per sandbox-prompt.md)

This bead's method note is explicit: a fix measured only against the bead's
own reproduction, or against examples this session wrote, is not evidence
it generalizes (`teach-yn8`/`teach-kmm` already broke this way twice). So
before considering this closeable I had a **separate Agent instance, given
only raw node content (topic descriptions, no algorithm details, no bead
text, no hint this was a bug-fix task) and no visibility into this session's
implementation**, write one faithful tutoring-paraphrase paragraph per
assigned topic, for 8 real nodes it did not choose: 5 from
`va_math_sol_graph.py` (`5.NS`, `6.PFA`, `3.PS`, `7.CE`, `2.MG` — none of
them the bead's own `4.MG`) and 3 from `dummit_foote_graph.py`
(`1.1-groups`, `2.1-subgroups`, `1.6-homomorphisms`).

Results, raw tier vs. raw+semantic tier, n=8:

| topic | target | raw tier | with semantic tier |
|---|---|---|---|
| 1 | 5.NS | CORRECT | CORRECT |
| 2 | 6.PFA | CORRECT | CORRECT |
| 3 | 3.PS | ABSTAIN | ABSTAIN (see below) |
| 4 | 7.CE | ABSTAIN | ABSTAIN |
| 5 | 2.MG | CORRECT | CORRECT |
| 6 | 1.1-groups | CORRECT | CORRECT |
| 7 | 2.1-subgroups | CORRECT | CORRECT |
| 8 | 1.6-homomorphisms | ABSTAIN | **CORRECT** |

**Raw tier: 5/8 correct, 3/8 abstain, 0/8 wrong.**
**With semantic tier: 6/8 correct, 2/8 abstain, 0/8 wrong.**

Topic 8 (homomorphisms) is the one case in this set the semantic tier
actually rescued from an honest abstention. Topics 3 and 4 stayed abstained
under both tiers — topic 3's real cause turned out to be unrelated to
paraphrase at all: `va-math-sol:3.PS`'s own distinctive vocabulary is just
`{"pictographs"}` after document-frequency filtering, because its `facts`
payload is almost entirely a `case_identifier_uuid` bookkeeping string that
`_flatten_strings` also harvests as vocabulary (filed separately as
`teach-klm` — out of this bead's scope). No amount of synonym matching can
recover a node whose real vocabulary is one word.

**The false positive this measurement caught, before `_SEMANTIC_MIN_MARGIN`
existed:** with the semantic tier's margin bar at the same value as the raw
tier's (2), topic 3's paraphrase ("...we want an answer to..." /
"...pulling it from somewhere it's already been recorded...") spuriously
out-scored every real candidate for `va-math-sol:8.PFA` (raw semantic score
7, next rival 5 — margin exactly 2) via ordinary-English WordNet pairs
("want"→"require", "answer"→"solution") that carry no domain signal
whatsoever. That would have turned a safe abstention into a **wrong**
confident answer — exactly what sandbox-prompt.md's "prefer abstention to a
confident answer" exists to prevent. Raising the semantic tier's margin
requirement to 3 (`_SEMANTIC_MIN_MARGIN`) closed this specific false
positive without cost to any of the 8 topics (verified by re-running the
full set after the change — see table above). This is a calibration
against one 8-item held-out set, not a proof no false positive can occur at
margin 3 with a larger set; I'm reporting it as exactly that.

Both new regression tests
(`test_semantic_tier_still_abstains_on_a_thin_coincidental_margin`,
`test_semantic_tier_recovers_dummit_foote_paraphrase_raw_tier_missed`) use
the literal text from this generalization set, not text I wrote for this
bead — so they lock in both the rescue and the near-miss false positive
against regression, without pretending either one is "coverage" beyond
these two texts.

## Honest scope of what this closes and what it doesn't

- The bead's literal reproduction (`va-math-sol:4.MG` paraphrase) now
  recovers correctly — `test_faithful_paraphrase_recovers_via_semantic_fallback_tier`.
- On an 8-item blind, independently-authored generalization set spanning
  both graphs in this repo, the semantic tier improved abstain→correct by
  1/8 net (6/8 vs 5/8 correct) with **zero** wrong answers in either
  configuration after the margin fix — but this was only possible to
  confirm because I found and fixed one wrong-answer regression the tier
  introduced along the way (documented above). That is 8 examples, not a
  general property: WordNet's synonym coverage is real but partial (it does
  not, for instance, link "area" and "space" — they share no synset — so
  not every paraphrase gets rescued), and it has almost nothing for
  graduate-level technical vocabulary. Generalization beyond this
  particular 8-item set is unmeasured.
- I did not touch the document-frequency boilerplate filter, despite
  finding that it independently strips some genuinely-distinctive words
  that recur across VA SOL grades (e.g. "area"/"perimeter"/"squares" all
  exceed `_MAX_DOCUMENT_FREQ`). That's a distinct tension from this bead's
  synonym/paraphrase problem and changing it risks the existing coverage-
  tiebreak tests; noted here for visibility, not filed as a bead since it's
  not blocking anything right now and I have no concrete fix in mind.
- Filed `teach-klm` for the `case_identifier_uuid`-vocabulary-pollution bug
  discovered while building the generalization set (out of this bead's
  scope, a data-quality issue in `_node_vocabulary`/`_flatten_strings`
  unrelated to paraphrase matching).

## Files touched

- `teach/concept_recovery.py` — module docstring section "A FAITHFUL
  PARAPHRASE CAN STILL LOOK LIKE NOTHING MATCHED (teach-8xw.26)"; new
  `_wordnet_lemmatizer`, `_lemma`, `_synonym_lemmas`, `_semantic_match`,
  `score_candidates_semantic`; `_resolve_candidates` extracted from the old
  inline body of `recover_taught_concept` and parameterized on
  `min_margin`; `_SEMANTIC_MIN_MARGIN` constant; `recover_taught_concept`
  rewritten to try the semantic tier only on raw-tier abstention.
- `tests/test_concept_recovery.py` — 3 new tests: the bead's literal
  reproduction, the calibration false-positive-turned-abstention, and one
  dummit-foote paraphrase the raw tier missed but the semantic tier
  recovers (all texts are either the bead's own repro text or the blind
  agent's output, not newly invented for this file).
- `pyproject.toml` / `uv.lock` — added `nltk` dependency.

## Validation

- `uv run pytest -q` — 246 passed (was 243 before this bead; 3 new tests
  added, zero regressions in the pre-existing suite).
- `uv run python3 -m teach.concept_recovery` — module self-check passes
  (note: `python3 teach/concept_recovery.py` directly fails with
  `ModuleNotFoundError: No module named 'teach'` on `main` too, before any
  change in this bead — pre-existing, confirmed via `git stash`, not
  something this bead introduced or should fix).
- Bead's exact reproduction command re-run after the fix: `taught:
  va-math-sol:4.MG`, `abstain_reason: None`.

## Note on uncommitted state

The working tree already had uncommitted changes from other closed beads
(`teach-8xw.27`, `.30`, `.31`, `.32` and others) when this session started,
per this repo's conservative git policy (no commit/push without being
asked). I did not commit anything, including my own changes — `git status`
shows everything from this session alongside the pre-existing uncommitted
work. Not committing or pushing per standing instructions.
