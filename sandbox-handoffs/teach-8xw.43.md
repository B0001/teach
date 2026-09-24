# teach-8xw.43 — actfl_can_do_graph: zero concept_recovery integration test exists

## What was asked

`teach/actfl_can_do_graph.py` (teach-cr8) had no cross-test with
`teach/concept_recovery.py`. `grep -rl 'concept_recovery' tests/` returned only
`test_concept_recovery.py`, `test_concept_recovery_non_math_domain.py`, and
`test_dummit_foote_graph.py` — none referenced `teach.actfl_can_do_graph`.
`concept_recovery.py`'s genericity claim (teach-8xw.10/.29) had been exercised
against math, reading, and writing domains, but never against the
foreign-language proficiency-ladder domain, despite that graph existing since
teach-cr8 closed. What would close it: a floor-level test recovering at least
two adjacent ACTFL sublevels plus a deliberate abstention case, and specific
confirmation that generic string-flattening harvests vocabulary from this
graph's opaque `facts` fields (`proficiency_benchmark`, `performance_
indicator`, and — added later by teach-8xw.49 — the differently-shaped
`investigation_*`/`interaction_*` fields), since ACTFL's imperative "I
can..." can-do statements are structurally different prose from the SOL
standards' style everything else was tuned against.

## What was built

`tests/test_actfl_can_do_graph_concept_recovery.py` — 6 tests, all
hand-written fixtures checked against actual `score_candidates`/
`recover_from_lesson_text` output before being written into assertions (not
guessed and patched until green):

1. `test_correct_recovery_of_two_adjacent_actfl_sublevels` — lesson text
   quoting real Advanced Mid `performance_indicator` text, with the real
   Advanced Low indicator signposted as already known ("Last year you
   already learned..."), recovers `actfl-can-do:advanced-mid` with assumed
   prerequisite `actfl-can-do:advanced-low` (a direct `PrerequisiteEdge`)
   against the 11-node Interpersonal Communication chain.
2. `test_unsignposted_prerequisite_detected_without_signal_phrase` — same
   content with the recall cue stripped entirely; Advanced Low correctly
   moves to `unsignposted_prerequisite_ids` instead of `assumed_prerequisite
   _ids` (teach-20c's three-way split).
3. `test_abstains_on_content_outside_actfl_vocabulary` — group-theory lesson
   text scores zero overlap against every one of the 11 Interpersonal nodes
   (`score_candidates(...) == ()`) and abstains cleanly — the same
   disclosed-gap abstention pattern teach-8xw.15/.29/.42 established for
   math/reading/writing.
4. `test_shared_function_prompt_filtered_from_interpersonal_vocabulary` — a
   finding this bead surfaced, not something known going in:
   `facts["function_prompt"]` is byte-identical across all 11 Interpersonal
   nodes ("How can I exchange information and ideas in conversations?"), so
   "exchange"/"information"/"ideas" have document frequency 11/11 —
   comfortably above `_MAX_DOCUMENT_FREQ` (4) — and the existing boilerplate
   filter correctly drops all three from every node's vocabulary. Confirmed
   this doesn't collaterally strip a sublevel's own genuinely distinctive
   words (`detailed`/`responses`/`wide` survive on Advanced Mid and are
   absent from Advanced Low).
5. `test_generic_harvesting_recovers_intercultural_opaque_fact_fields` —
   the bead's central genericity concern: Intercultural Communication's
   `facts` has no `performance_indicator`/`proficiency_benchmark` key at
   all, only six differently-named fields
   (`investigation_benchmark`/`investigation_indicator_products`/
   `investigation_indicator_practices`/`interaction_benchmark`/
   `interaction_indicator_language`/`interaction_indicator_behavior`).
   Recovery of taught concept (`actfl-can-do:intercultural:intermediate`)
   and assumed prerequisite (`actfl-can-do:intercultural:novice`, a direct
   edge) works against that shape with zero code change to
   `concept_recovery.py`.
6. `test_harvesting_pulls_words_from_every_intercultural_fact_field` —
   direct confirmation that `_node_vocabulary` reached all six of those
   fields, not just the ones with familiar-looking names: one real,
   distinguishing word sourced from each field on
   `actfl-can-do:intercultural:novice` ("identify",
   "limited", "communicate", "rehearsed").

## Method

Every fixture was built by first computing real `score_candidates` output in
a scratch script (not written into the test file), then locking in the
lesson text and expected result once the margin/coverage numbers were
checked by eye. This surfaced two non-obvious things worth recording for
future workers on this graph:

- **Quoting a sublevel's shared `proficiency_benchmark` text ties adjacent
  sublevels within the same major level.** `proficiency_benchmark` is
  identical across all three sublevels of one major level (e.g. Advanced
  Low/Mid/High all share one benchmark paragraph) — a lesson quoting that
  paragraph verbatim scores all three sublevels equally and forces
  abstention (correctly — a human reader given only the shared benchmark
  text genuinely couldn't tell which sublevel it was either). Recovering a
  *specific* sublevel requires leaning on its own `performance_indicator`
  text, which is genuinely sublevel-distinct.
- **`function_prompt` is boilerplate at the whole-graph level, not just the
  per-strand level VA SOL exercised.** VA Math/Reading/Writing SOL's
  boilerplate was grade-to-grade near-duplication; here it's a single
  literal repeated string across all 11 nodes of a mode. Same filter, same
  threshold, first time confirmed against a graph whose boilerplate is a
  single constant field rather than merely similar prose.

## Evidence

```
$ uv run pytest tests/test_actfl_can_do_graph_concept_recovery.py -v
6 passed

$ uv run pytest -q
457 passed

$ uv run python3 -m teach.actfl_can_do_graph
OK: 11 NCSSFL-ACTFL Can-Do proficiency sublevels ... (and 4 more OK lines for
interpretive/presentational/intercultural/no-cross-mode-collision checks)

$ uv run python3 -m teach.concept_recovery
OK: correct-recovery example identifies va-math-sol:4.MG ... (unchanged,
math self-check untouched)
```

No production code was changed — this bead was scoped as test-only.

## Known limitations, stated not hidden

- Same floor-vs-generalization limit every prior `concept_recovery`
  cross-test names: all lesson text is hand-written by this session, not a
  held-out generalization set. This measures "recovery mechanically works
  against this graph given these specific texts," not "recovery generalizes
  to arbitrary foreign-language lesson text." Per sandbox-prompt.md, that
  is not something a self-authored fixture can ever establish.
- Only the Interpersonal and Intercultural mode graphs are exercised.
  Interpretive and Presentational (also added by teach-8xw.49, same
  11-sublevel shape as Interpersonal) were not separately tested — a quick
  survey script (see the session's scratch exploration, not kept) showed
  their sublevels are recoverable via indicator-only text with margins
  similar to Interpersonal's, but no assertion locks that in. Filing this
  as follow-up scope, not doing it now.
- The abstention case checked is only "content entirely outside the whole
  domain" (group theory). No test exercises within-graph ambiguity for this
  domain the way `test_adjacent_grades_real_vocabulary_overlap_forces_
  honest_abstention` does for reading/writing (e.g. two adjacent sublevels
  whose real indicator text is close enough to force a genuine tie) — the
  Advanced Low/Mid pair used for the correct-recovery fixture was
  specifically chosen because it does NOT tie; a from-scratch search for a
  genuinely-tied adjacent pair was not done. Also out of this bead's scope.

## Status

Closing as done: the bead's "what would close this" section asked for a
test mirroring the reading/writing domain pattern, recovering at least two
adjacent ACTFL sublevels plus one abstention case, with specific confirmation
that generic harvesting pulls vocabulary from this graph's opaque fact
fields — all of which now exists, passing, with the full suite green.
