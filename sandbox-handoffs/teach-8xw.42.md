# teach-8xw.42 — va_writing_sol_graph x concept_recovery floor test

## What was asked

`teach/va_writing_sol_graph.py` (teach-5aj) had zero cross-test with
`teach/concept_recovery.py` -- not even a self-authored floor test, unlike
the reading domain (teach-8xw.29). `grep -rl concept_recovery tests/`
confirmed this before starting: it returned only `test_concept_recovery.py`
(math), `test_concept_recovery_non_math_domain.py` (reading only), and
`test_dummit_foote_graph.py`.

## What was done

Wrote `tests/test_concept_recovery_writing_domain.py`, mirroring
`test_concept_recovery_non_math_domain.py`'s structure exactly (same four
test shapes: correct recovery, out-of-vocabulary abstention, unsignposted-
prerequisite detection, adjacent-grade ambiguity forcing abstention) plus a
fifth test for the boilerplate document-frequency filter, since that one is
present in the design memory's own calibration concern but the reading file
folds it implicitly into other assertions rather than isolating it -- this
file isolates it, same as the reading file's own docstring says the module's
design memory calls out as point 2.

Every fixture was built by first querying the real module
(`build_vocabulary_index`, `score_candidates`) against the real loaded
`teach.va_writing_sol_graph` graph, reading the actual scores it produced,
and only then writing the assertion -- not guessed and patched until green:

1. **Correct recovery**: assumed-prior = grade 6.W, taught = grade 7.W.
   Lesson text quotes real 6.W.1.B/6.W.1.C and 7.W.1.A/7.W.1.B/7.W.1.C leaf-
   standard text verbatim from `teach/data/va_writing_sol_k12.json`.
   Deliberately preserves a real upstream transcription quirk: 6.W.1.C's
   source text spells it `"welldefined"` (no hyphen) while 7.W.1.C's spells
   it `"well-defined"` (hyphenated) -- confirmed both spellings are the
   *source's own*, not typos introduced here, and confirmed the hyphenated
   form tokenizes to `"defined"` while the unhyphenated form tokenizes to
   `"welldefined"` as a single distinct vocabulary word, so the fixture
   actually needed both exact spellings to hit each grade's real vocabulary.
   Checked before writing the assertion: raw score for 7.W is 45 against
   8.W's 34 (closest rival) -- a comfortable, checked margin, not assumed.
2. **Abstention**: screenwriting-craft lesson text (inciting incidents,
   midpoint reversals, hero's-journey beats) -- checked that the best
   candidate shares exactly 1 word ("draft") with the text, below
   `_MIN_MATCH_WORDS` (3).
3. **Unsignposted prerequisite**: same content as (1) with the "Last year
   you already learned" cue stripped -- checked assumed becomes `()` and
   unsignposted becomes `("va-writing-sol:6.W",)`.
4. **Adjacent-grade ambiguity**: computed the actual 3-way vocabulary
   intersection of grades 6/7/8 (`{variety, structure, description,
   existing, among, concept, transition, comparison, multi, alter,
   persuasively, structures, paragraph}` -- 13 words, real overlap after the
   document-frequency filter, not invented) and wrote a sentence using only
   those words, checked to produce an *exact* three-way score tie (13/13/13)
   before writing the assertion -- stronger than the reading file's version,
   which only asserts "top three set", not an exact tie.
5. **Boilerplate filter**: confirmed by direct document-frequency count over
   `_node_vocabulary` (not assumed by analogy to reading) that "writing"
   (df=13), "texts" (df=11), and "topic" (df=9) all exceed
   `_MAX_DOCUMENT_FREQ` (4) and are filtered from both K.W and 12.W, while
   each grade's real distinctive words ("drawing", "prewriting" for K;
   "postsecondary", "workplace" for 12) survive.

Filed `teach-25s` as a separate, explicitly-scoped follow-up for the
generalization measurement this bead does NOT provide: every fixture above
is hand-written by this session, so per sandbox-prompt.md's "you cannot hold
out examples from yourself" this is floor evidence only (mechanism runs
against a third real non-math curriculum-scale graph), not a generalization
claim. teach-25s asks for lesson text from an agent with no repo access, per
teach-8xw.33's precedent, and asks that whoever closes it keep the two
measurements in separate files rather than folding a generalization result
into this floor test.

## Evidence

```
$ uv run pytest tests/test_concept_recovery_writing_domain.py -v
5 passed

$ uv run pytest -q
414 passed   # full suite, unchanged elsewhere -- no regressions
```

## Scope note: what this bead did NOT do

Did not touch `teach/concept_recovery.py` itself, `teach/va_writing_sol_graph.py`
itself, or attempt any generalization measurement (see teach-25s). Did not
re-derive or re-verify the writing SOL source data -- that provenance is
teach-5aj's, unchanged and untouched here.
