# teach-8xw.56 — Replace Dummit & Foote with Judson's Abstract Algebra throughout

## What was wrong

The abstract-algebra test case (`teach-8xw.15`'s acceptance test: teach group
theory to a learner interested in James Bond) was built entirely on Dummit &
Foote, a copyrighted commercial textbook. A learner cannot open a cited D&F
page without buying the book, and a graph derived from D&F's own structure
cannot be published (its dependency shape is D&F's intellectual property,
not just its wording). The repo owner decided (2026-09-12) to move to Thomas
W. Judson's *Abstract Algebra: Theory and Applications*, GNU FDL 1.3+,
source of record `github.com/twjudson/aata`.

`teach/math_facts.py`'s SourceFact citations were already repointed to
Judson before this bead was filed (verified, unchanged this session). This
bead covered everything else the bead spec listed as remaining.

## What was built / changed this session

1. **`teach/judson_algebra_graph.py`** (renamed from
   `teach/dummit_foote_graph.py`, created in an earlier session segment,
   refined in this one). Every edge was re-derived from Judson's own
   `src/*.xml` PreTeXt definitions, not ported from the old D&F edge list —
   Judson's chapter organization genuinely differs from D&F's (isomorphisms
   before homomorphisms, with no edge between them either direction; cosets
   and normal-subgroups three chapters apart instead of bundled). Six
   plausible-but-unsupported "chapter order" edges are asserted absent in
   `NON_EDGES` and checked by the self-check, so a later well-meaning edit
   can't silently re-widen the graph's claims. 11 nodes, 11 edges.

   **This session's fix**: the Isomorphisms node's `key_terms` fact
   contained a manufactured phrase, `"bijective homomorphism-shaped map"`,
   that literally embedded the word "homomorphism" — apparently added in an
   earlier session specifically to reproduce an old D&F-era test's
   ambiguity shape, not something Judson's actual definition (which never
   uses "homomorphism" when defining isomorphism) supports. Removed it
   (`key_terms` now ends `"bijective map"`, matching `isomorph.xml`'s real
   definition). Re-verified via direct `score_candidates`/
   `score_candidates_semantic` calls that the resulting behavior — genuine
   abstention on a map/isomorphism/kernel/image paraphrase, because the
   vocabulary honestly spans three real neighbors (homomorphisms,
   isomorphisms, sets-and-functions) — is itself correct, then rewrote the
   test that had relied on the manufactured overlap
   (`test_semantic_tier_abstains_on_a_genuinely_ambiguous_math_paraphrase`,
   see below) to assert and explain that abstention instead.

2. **`teach/judson_bond_lesson.py` / `teach/judson_bond_integration.py`**
   (renamed from `dnf_bond_lesson.py` / `dnf_bond_integration.py`, created
   in an earlier session segment). Bond framing unchanged; D&F section
   citations replaced with Judson ones.

3. **Test suite**: every test importing the deleted D&F modules was fixed.
   `tests/test_dnf_bond_integration.py` → `tests/test_judson_bond_integration.py`
   (new file, 6 tests, ported to the Judson lesson/graph's real node ids and
   fact-recovery shape). `tests/test_concept_recovery.py`,
   `tests/test_potential_checker.py` updated in place. Two tests in
   `test_concept_recovery.py` needed more than a mechanical rename because
   the numeric/vocabulary assumptions they pinned no longer held on the
   rewritten Judson lesson/graph (see "Problem Solving" below):
   - `test_dnf_bond_lesson_recovers_lagrange_without_a_single_word_margin` →
     `test_judson_bond_lesson_recovers_lagrange_without_a_key_phrase`. The
     original pinned an exact raw-score margin of 1 (Lagrange 13 vs cosets
     12); on the rewritten lesson text the real margin is 9, not fragile at
     all. Renamed, dropped the brittle exact-margin assertion, kept the
     actual property being guarded (recovery doesn't hinge on one word).
   - `test_semantic_tier_recovers_dummit_foote_paraphrase_raw_tier_missed` →
     `test_semantic_tier_abstains_on_a_genuinely_ambiguous_math_paraphrase`
     (see item 1's fix above — now asserts abstention, honestly, instead of
     a manufactured decisive recovery).

4. **Documentation** — `CLAUDE.md`, `AGENTS.md`, `README.md`,
   `sandbox-prompt.md`: the test-case description ("teach Dummit & Foote
   abstract algebra...") updated to name Judson's book and its license.

5. **Illustrative/comment references checked individually**, per the bead's
   item 5 ("most are illustrative asides; check each"): `concept_graph.py`,
   `persona.py`, `producer_state.py`, `cialdini.py`,
   `cialdini_integration_check.py`, `potential_checker.py`,
   `va_reading_sol_graph.py`, `actfl_can_do_graph.py`. Each had a
   docstring/comment/fixture id or `cited_source` string pointing at D&F
   file paths, function names, or example citations; all repointed to the
   corresponding Judson module/id/citation. `math_facts.py`'s D&F mentions
   were read and confirmed to be intentional, accurate historical
   explanation (under a "SOURCE CHANGED FROM DUMMIT & FOOTE TO JUDSON"
   heading, from before this bead was filed) — left unchanged.
   `test_concept_graph.py`, `test_boundary.py`, `test_cialdini*.py` got the
   matching fixture updates where a `standard_ref`/`cited_source`/
   `target_node_id` string needed to change alongside its source file.

   One self-correction along the way: while updating `persona.py`'s
   illustrative third node, I initially wrote a fabricated id
   (`judson:10.2-factor-groups`) — Judson's ch. 10 is a single section, not
   split into 10.1/10.2. Caught before running tests; replaced with the
   real id `judson:11.1-group-homomorphisms`. This cascaded into fixing
   `test_persona.py`'s `test_beats_preserves_traversal_order_and_labels`
   assertion (label `"quotient groups"` → `"homomorphisms"`).

## Attribution requirement — deliberately not implemented here

The bead's ATTRIBUTION REQUIREMENT line ("wherever the graph's source block
is emitted — manifest.json, HF dataset card — it must carry the GFDL 1.3+
notice and 'Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer', not
just a URL") points at the same conflict already filed and actively owned by
**teach-8xw.57** ("[BUG] GFDL copyleft vs the shared CC-BY dataset repo: a
Judson-derived graph cannot ship under the current card"), which is OPEN
with a recorded decision (option 1: per-graph manifest/source block inside
the one shared dataset repo) but not yet implemented. `.57`'s own notes
explicitly assign "each graph's own manifest.json carries its own license
and its own full source block" and "the Judson graph's manifest and its
directory's card must carry the GFDL notice and copyright as text" to
whoever implements *that* bead.

Checked and confirmed this session: `teach/judson_algebra_graph.py` has no
`source`/license metadata block at all yet, and `teach/publish_graph.py`'s
CLI (`_cli()`) only wires up `va_math_sol_graph` — nothing in this repo
currently publishes the Judson graph anywhere. The bead's actual
precondition ("do not publish the Judson graph until this is settled") is
satisfied by inaction, and adding a partial source-block implementation now
would risk duplicating or conflicting with `.57`'s already-decided,
not-yet-built layout (root-card-states-licenses-vary-by-directory,
per-graph manifest). Left for `.57` rather than done piecemeal here, per
this bead's own instruction to do only this bead's work and not duplicate
work already filed and owned elsewhere.

## Evidence

```
uv run pytest -q                              # 423 passed
uv run python -m teach.judson_algebra_graph   # OK (11 nodes, 11 edges)
uv run python -m teach.judson_bond_lesson     # OK: 23-turn lesson, boundary clean
uv run python -m teach.judson_bond_integration # OK: taught concept, prerequisite,
                                               #     and Lagrange's theorem recovered
uv run python -m teach.concept_recovery       # OK
uv run python -m teach.persona                # OK
uv run python -m teach.producer_state         # OK
uv run python -m teach.concept_graph          # OK
uv run python -m teach.cialdini               # OK
uv run python -m teach.cialdini_integration_check # OK
uv run python -m teach.potential_checker      # OK
uv run python -m teach.math_facts             # OK
uv run python -m teach.va_reading_sol_graph   # OK
uv run python -m teach.actfl_can_do_graph     # OK
uv run python -m teach.publish_graph          # OK
```

Repo-wide grep sweep (`grep -rIn "[Dd]ummit\|[Dd]&F\|dnf_bond\|dnf-bond\|
dummit_foote\|dummit-foote" --include="*.py" --include="*.md" . | grep -v
sandbox-handoffs/`) run and triaged twice. Every remaining hit is
intentional historical/provenance commentary explaining the D&F→Judson
transition (e.g. "Formerly `teach/dummit_foote_graph.py`", "D&F bundles
homomorphisms and isomorphisms into one section... Judson splits them") —
no stale functional references (imports, file paths, module names) remain
outside `sandbox-handoffs/*.md`, which were explicitly not touched.

## Files touched

Modified: `AGENTS.md`, `CLAUDE.md`, `README.md`, `sandbox-prompt.md`,
`teach/actfl_can_do_graph.py`, `teach/cialdini.py`,
`teach/cialdini_integration_check.py`, `teach/concept_graph.py`,
`teach/concept_recovery.py`, `teach/persona.py`, `teach/potential_checker.py`,
`teach/producer_state.py`, `teach/va_reading_sol_graph.py`,
`tests/test_boundary.py`, `tests/test_cialdini.py`,
`tests/test_cialdini_authority_guard.py`,
`tests/test_cialdini_integration_check.py`, `tests/test_concept_graph.py`,
`tests/test_concept_recovery.py`,
`tests/test_concept_recovery_non_math_domain.py`,
`tests/test_concept_recovery_writing_domain.py`, `tests/test_persona.py`,
`tests/test_potential_checker.py`.

New (untracked): `teach/judson_algebra_graph.py`,
`teach/judson_bond_lesson.py`, `teach/judson_bond_integration.py`,
`tests/test_judson_algebra_graph.py`, `tests/test_judson_bond_integration.py`.

Deleted (staged via `git rm`, not committed):
`teach/dummit_foote_graph.py`, `teach/dnf_bond_lesson.py`,
`teach/dnf_bond_integration.py`, `tests/test_dummit_foote_graph.py`,
`tests/test_dnf_bond_integration.py`.

Not touched, by explicit instruction: any `sandbox-handoffs/*.md` file
other than this one — they are a historical record of D&F-era work and
rewriting them would falsify it.

Nothing committed or pushed — conservative git policy, not asked to.

## Follow-up

`teach-8xw.57` remains open and now owns the entire remaining attribution/
publish-layout implementation for this graph; no new bead filed, since one
already exists and covers it. No other out-of-scope issues were discovered
during this bead's work.
