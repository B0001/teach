# teach-5aj — build teach/va_writing_sol_graph.py from the VA ELA Writing (W) strand

## What was asked

Build the writing-domain counterpart to `va_reading_sol_graph.py`, per
teach-8xw.39's survey finding: the same Learning Commons pipeline that
carries VA Math SOL (teach-8xw.5) and VA Reading SOL RI/RL (teach-8xw.29)
also carries a complete K-12 Virginia ELA "W" (Writing) strand, same shape,
same license, same provenance chain.

## What was done

The prior session's scratch snapshot (`/tmp/va_ela_nodes.jsonl`, 1580
lines) no longer existed on disk (confirmed by `ls` before trusting it) --
per sandbox-prompt.md's rule on not trusting a prior session's summary of
its own tool calls, the whole thing was re-derived from the live source
this session, not resumed from a note:

1. Streamed `nodes.jsonl` (342MB) and `relationships.jsonl` (570MB) fresh
   from `cdn.learningcommons.org/knowledge-graph/v1.13.0/exports/` via
   `curl`, downloaded to `/tmp` and filtered with plain Python/grep (no
   summarizer in the loop).
2. Filtered for `jurisdiction=="Virginia"`, `academicSubject=="English
   Language Arts"`, `statementCode` matching `<grade>.W(.*)?` for K-12:
   **236 nodes**, matching the survey's reported count independently.
3. Discovered and worked around a real gotcha the survey didn't hit: the
   `hasChild` relationship's own `properties.sourceEntityKey`/
   `targetEntityKey` claim `"caseIdentifierUUID"`, but joining
   `source_identifier`/`target_identifier` against nodes' `caseIdentifierUUID`
   produced **zero** matches. Joining against the node's top-level
   `identifier` field instead produced 223 edges (= 236 - 13, i.e. exactly
   a 13-tree forest with no orphans) -- confirmed against a live sample
   before trusting it at scale.
4. BFS from each of the 13 `Strand` roots showed a perfectly uniform
   4-level hierarchy: `Strand` -> `Sub-Strand` -> `Standard` -> `Component`.
   Writing has one more layer than reading (`Component`: template-fragment
   bullets like `7.W.2.A.iii` "*Write arguments that* develop a thesis...")
   -- this module deliberately stops at the `Standard`-type leaf, same
   stopping rule as `va_reading_sol_graph.py` (leaf = the type literally
   named "Standard", not whatever is deepest), not a new judgment call.
5. Cross-checked against the actual VDOE PDF (same document reading already
   verified, since VA's ELA SOL covers all strands in one PDF): fetched the
   2025-09-06 Wayback snapshot of the same attribution URL teach-8xw.29
   used, text-extracted with `pypdf`, and confirmed three leaf standards
   spanning the grade range (K.W.1.A, 12.W.3.A, 12.W.3.D) appear verbatim.
6. Found and documented (not hidden or silently deduped) a real upstream
   data quirk: grade 12 has two distinct source nodes, different
   `caseIdentifierUUID`s and different description text, both coded
   `statementCode == "12.W.3.A"`. `leaf_standards` stores `(code, text)`
   tuples (same as reading), so both survive; a dedicated test
   (`test_grade_12_duplicate_statement_code_is_a_documented_source_quirk`)
   pins this rather than letting a future refactor to a dict silently drop
   one.
7. Wrote `teach/data/va_writing_sol_k12.json` (13 groupings, 93 sourced
   leaf standards), `teach/va_writing_sol_graph.py` (mirrors
   `va_reading_sol_graph.py`'s loader shape exactly: one `ConceptNode` per
   `(grade, "W")` grouping, `PrerequisiteEdge` chaining K -> 1 -> ... -> 12),
   and `tests/test_va_writing_sol_graph.py` (11 tests, mirrors
   `test_va_reading_sol_graph.py`'s coverage plus the grade-12-duplicate
   regression test above).

## Content-escalation self-check

Reading's self-check used "with prompting and support" (K) vs. its absence
(grade 8). Writing's actual source text uses a different idiom
("guidance and support", not "prompting and support"), verified directly
rather than assumed by analogy:

- `"guidance and support"` appears in every grouping K-5, absent from every
  grouping grade 6-12.
- `"postsecondary"` appears only in `12.W` (12.W.3.D: "Write and revise to
  a standard acceptable both in the workplace and in postsecondary
  education."), nowhere K-11.

Both directions are asserted in the module's `__main__` self-check and in
`test_grade_progression_is_a_real_content_escalation_not_just_labels`, so a
future data-shuffling bug would fail loudly in both directions, not just
one.

## Evidence

```
$ uv run python -m teach.va_writing_sol_graph
OK: 13 VA Writing SOL K-12 grade-strand groupings (93 sourced leaf
standards) load as a valid DAG (12 grade-chain edges); K.W..12.W orders
correctly and its endpoints' sourced standard text actually escalates in
content (guided drawing/dictating -> independent postsecondary/workplace-
standard writing), not just grade number

$ uv run pytest tests/test_va_writing_sol_graph.py -v
11 passed

$ uv run pytest -q
327 passed   # full suite, unchanged elsewhere -- no regressions
```

## Scope note: what this bead did NOT do

Per the bead's own explicit instruction, `concept_recovery.py`'s
`recover_from_lesson_text` genericity was **not** re-run against this new
graph in this session -- no real (non-self-authored) writing-domain lesson
text was available, and doing so with self-written fixtures would repeat
exactly the self-authored-test-set failure sandbox-prompt.md documents for
teach-yn8/teach-kmm/teach-5gf. Whether this graph's vocabulary is
recoverable from real lesson text is unmeasured and should be a separate
bead, gated on real (not session-authored) lesson text becoming available.

## Files changed

- `teach/data/va_writing_sol_k12.json` (new)
- `teach/va_writing_sol_graph.py` (new)
- `tests/test_va_writing_sol_graph.py` (new)

Not committed -- conservative git policy, bead did not ask for a commit.
Other unrelated uncommitted/untracked changes present in the working tree
(`.beads/interactions.jsonl`, `sandbox-handoffs/teach-8xw.33.md`,
`teach/math_facts.py`, `teach/biblical_ot_source.py`, two other
`sandbox-handoffs/*.md` files, `tests/test_biblical_ot_source.py`) predate
this session and were left untouched.
