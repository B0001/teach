# teach-443 handoff

concept_recovery: judson:18.2-factorization-in-integral-domains acts as a
generic-vocabulary attractor node, topping raw score across unrelated topics.

## Status: fixed (partially) and closing with a follow-up bead filed

teach-443 asked specifically: is judson:18.2's outsized raw-score attraction
a vocabulary-extraction defect, or a more general property of long verbatim
nodes -- and it asked for someone to actually inspect
`build_vocabulary_index` output for that node before proposing a fix. That
investigation is done. It found two independent, layered causes. One is a
narrow, unambiguous bug and is fixed here. The other is a real, harder
problem, deliberately left open and filed forward as **teach-57f**.

## Investigation

Built `_node_vocabulary`-equivalent output directly (via `uv run python -c`,
importing the module's actual `_WORD`/`_STOPWORDS`/`_UUID`/`_flatten_strings`
helpers rather than re-deriving them by hand) and compared judson:18.2's
distinctive-word count and content against the rest of the 20-node
`load_judson_full_graph()` graph.

**Finding 1 -- size**: judson:18.2 had 75 distinctive words pre-fix, vs. a
graph median around 15-18. Next highest was judson:16.3 at 57; smallest was
judson:18.1 at just 3. This ~3-5x outlier size is exactly the kind of raw
"more distinctive words = more raw score" advantage that lets 18.2 win
against dialogues on entirely unrelated topics, per the bead's hypothesis.

**Finding 2 -- content-bundling asymmetry (root structural cause, not
fixed)**: `teach/extract_judson_ring_field.py`'s `build()` concatenates
*every* `<definition>` block matching a PreTeXt section title into one
node's `definition` field (`" ".join(b.text for b in blocks)`). Judson's own
"Factorization in Integral Domains" section legitimately bundles ~9-10
separate formal definitions (irreducible, prime element, unit, associates,
UFD, ..., in the same expository section), so this one node's `definition`
text is structurally ~9-10x longer than a single-definition node like
judson:18.1 ("Fields of Fractions", which only has one definition in its
section). This is real Judson content, correctly extracted -- not a bug --
but it produces exactly the vocabulary-size skew described above.

**Finding 3 -- LaTeX markup leakage (fixed)**: the verbatim `definition`
text still carries raw PreTeXt/LaTeX inline math source, e.g.
`$\nu(a) \leq \nu(ab)$` or `$D \setminus \{0\} \to \mathbb N_0$`.
`_WORD = re.compile(r"[a-z]+")` tokenizes text *after* lowercasing without
first stripping backslash-command markup, so `\mathbb` becomes the bare
"word" `mathbb`, `\setminus` becomes `setminus`, etc. Confirmed systemic
across the whole ring/field data file:

```
grep -o '\\[a-zA-Z]*' teach/data/judson_ring_field.json | sort | uniq -c
```

showed repeated hits for `\mathbb`, `\setminus`, `\langle`, `\rangle`,
`\cdots`, `\ldots` and others, across multiple nodes, not just judson:18.2.

**Finding 4 -- generic-discourse contamination (real, NOT fixed, filed as
teach-57f)**: of judson:18.2's 75 pre-fix distinctive words, roughly 36 are
ordinary academic-discourse/connective English -- "recall", "suppose",
"written", "satisfy", "question", "necessarily", "furthermore", "extend",
"numbers", "positive", "common", "distinct", "exist", "form", "function",
"either", "know", "possible", "provided", "result", "said", "states",
"unique", "whenever", "whether", "write", "condition", "conditions",
"order" -- not domain-specific factorization vocabulary. These pass the
`_MAX_DOCUMENT_FREQ=4` filter (most have document-frequency 1 among these 20
nodes) purely because every *other* node in this graph is short, formal,
single-definition prose that never contains ordinary sentence connectives at
all. The document-frequency filter can only catch a word that recurs across
nodes; it has no mechanism for catching a word that's rare in this graph
only because the graph's other nodes are too terse to ever use it. This is
the deeper, harder half of the bead's root-cause question and is
**intentionally not fixed in this session** -- see teach-57f.

## Fix applied (Finding 3 only)

`teach/concept_recovery.py`: added a `_LATEX_COMMAND` regex
(`re.compile(r"\\[a-zA-Z]+")`) and strip it in `_words()` immediately after
the existing `_UUID` stripping, before word-tokenization:

```python
_LATEX_COMMAND = re.compile(r"\\[a-zA-Z]+")
...
def _words(text: str) -> set[str]:
    text = _UUID.sub(" ", text)
    text = _LATEX_COMMAND.sub(" ", text)
    return {w for w in _WORD.findall(text.lower()) if len(w) >= 4 and w not in _STOPWORDS}
```

This is a narrow, unambiguous correctness fix (a LaTeX macro name is never
an English content word) that needs no threshold calibration or held-out
validation the way `_resolve_candidates` tuning constants do. Effect:
judson:18.2's distinctive vocabulary shrank from 75 -> 69 words (removed:
`cdots`, `langle`, `ldots`, `mathbb`, `rangle`, `setminus`; nothing else
changed). It also corrected document-frequency counts for other ring/field
nodes that had markup-only occurrences of ordinary words -- notably "subset"
appeared via literal `\subset` commands in some nodes and via real prose in
others; once markup occurrences are excluded, "subset"'s document frequency
dropped from 5 to 3, newly qualifying it as distinctive vocabulary for
judson:16.1-rings.

## Test suite impact

Baseline before fix: 614 passed, 16 skipped, 5 xfailed.
Immediately after the fix (before updating fixtures): 612 passed, 2 failed.

Both failures were diagnosed precisely and are legitimate, traceable
consequences of the fix, not regressions:

1. **`test_splitting_fields_safely_abstains`** (in
   `tests/test_concept_recovery_judson_full_graph_generalization.py`) --
   SPLITTING_FIELDS used to tie exactly at raw score 9 between
   judson:21.2-splitting-fields and judson:21.1-extension-fields, neither
   clearing the multi-candidate coverage-tiebreak margin, so the module
   correctly abstained on a genuinely close pair. Both of those nodes' own
   `definition` text contains `\cdots`/`\ldots`. Stripping that markup
   shrinks both nodes' vocabularies to their real prose, which breaks the
   tie decisively in judson:21.2's favor (88.9% self-coverage vs. 21.1's
   24.2%) -- this is a side effect of a correctness fix, not a retuned
   threshold, and it flips a stale abstention into a **correct recovery**.
   Renamed to `test_splitting_fields_now_correctly_recovers_after_teach_443`
   with a docstring explaining the mechanism and asserting
   `result.taught_node_id == "judson:21.2-splitting-fields"`.

2. **`test_subgroups_abstains_via_preexisting_near_margin_floor_not_teach_hpa`**
   (in `tests/test_concept_recovery_judson_full_graph_generalization_round3.py`)
   -- SUBGROUPS used to abstain because judson:18.2 won by exactly 2 words
   over runner-up judson:16.1-rings (single-candidate near-margin floor).
   The "subset" document-frequency change above (Finding 3's side effect)
   raises judson:16.1-rings' own score by one, from 12 to 13, pulling both
   candidates into the multi-candidate coverage-tie branch instead. Neither
   clears `_MIN_COVERAGE_FRACTION` there (18.2: 20%, rings: 26%), so the
   **outcome is still the same safe abstention**, just via a different
   code path. Renamed to
   `test_subgroups_abstains_via_multi_candidate_coverage_tie_after_teach_443`
   with a docstring explaining the mechanism; assertions unchanged
   (`taught_node_id is None`, abstain reason mentions "too close to call").

Both renamed tests retain their original historical docstring content where
relevant and clearly separate "what was originally measured" from "what
changed and why," per this repo's existing teach-ceg annotation precedent in
the same round3 file. An "UPDATE (teach-443, later session)" paragraph was
also appended to the round3 module's frozen historical docstring, directly
under the paragraph that originally flagged this bug, summarizing the fix
and pointing at teach-57f -- the original historical percentages/counts in
that paragraph were left untouched.

Final full suite run after all fixture updates:
**614 passed, 16 skipped, 5 xfailed, 0 failures, 0 warnings.**

## Follow-up bead filed

**teach-57f** (P3, `discovered-from` teach-443): the generic-academic-
discourse-vocabulary contamination (Finding 4 above) is real and unfixed.
Two candidate directions are sketched in that bead (a general-English
frequency reference independent of this graph's own document-frequency
stats, or splitting judson:18.2 into finer-grained per-definition nodes to
address the content-bundling asymmetry directly). Neither is attempted here
-- both need their own design and a **fresh** held-out validation round,
per this repo's standing methodology (round3's five dialogues, and every
fixture touched in this session, are now tuning data and must not be reused
to validate a future fix).

## Files touched

- `teach/concept_recovery.py` -- the fix (13 lines added, no lines removed).
- `tests/test_concept_recovery_judson_full_graph_generalization.py` --
  renamed/rewrote one test to reflect a corrected recovery.
- `tests/test_concept_recovery_judson_full_graph_generalization_round3.py`
  -- renamed/rewrote one test to reflect the same safe abstention via a
  different path; appended an UPDATE paragraph to the module's historical
  docstring.

## Git

Not committed or pushed -- conservative git policy, not asked to do so this
session. `git status --short` shows the three modified files above plus the
pre-existing unrelated modification to `.beads/interactions.jsonl` (bd's own
bookkeeping) and the untracked `sandbox-handoffs/*.md` files from prior
sessions.

## Not touched

`teach-ceg` (separate, still `in_progress` P2 bead) -- its fix already
appears to exist in the code; left entirely alone per scope.
