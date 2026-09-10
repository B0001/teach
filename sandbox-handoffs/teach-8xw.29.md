# teach-8xw.29 — concept_recovery: claimed genericity to non-math domains had zero test evidence

## What was wrong

`teach/concept_recovery.py`'s module docstring and the design memory
(`teach-8xw-10-concept-recovery-design`) both asserted domain-agnostic
genericity ("no hardcoded key names, so non-math domains work") as if it
were a measured fact. It was a design intent only: every `ConceptGraph`
this module had ever actually been run against — in tests, in the
`if __name__` self-check, everywhere — was math (`va_math_sol_graph.py`,
`dummit_foote_graph.py`). The only non-math graphs anywhere in the repo were
a 2-node illustrative fixture in `concept_graph.py`'s own self-check and a
hand-built 2-node synthetic graph in one test
(`test_domain_agnostic_vocabulary_extraction_ignores_key_names`), which only
proves the code doesn't read a `"leaf_standards"`-shaped key name — not that
recovery actually works at curriculum scale against a real domain with real
boilerplate density and real grade-to-grade vocabulary overlap, the thing
the design memory's own point 2 says the document-frequency calibration
exists to handle.

The bead's own text was explicit that closing it by writing a *synthetic*
non-math graph shaped to make the checker look good would reproduce the
exact self-authored-test-set failure this repo's method note exists to
prevent (`teach-yn8`/`teach-kmm`/`teach-5gf`). So option (a) — a real graph,
sourced the same way math was — was the only path that actually closes the
gap rather than papering over it.

## What was built

**1. `teach/data/va_reading_sol_k8.json` + `teach/va_reading_sol_graph.py`** —
a real, curriculum-scale non-math `ConceptGraph`: Virginia English SOL
reading strands (RI = Reading: Informational Texts, RL = Reading: Fiction),
grades K-8. Sourced from the exact same feed `va_math_sol_graph.py` used for
math (`cdn.learningcommons.org/knowledge-graph/v1.13.0/exports/{nodes,
relationships}.jsonl`), which also carries Virginia's English Language Arts
standards (1580 VA nodes) — confirmed by fetching and grepping the raw
`.jsonl` myself, not by trusting a prior session's summary of what the feed
contains.

- 18 `ConceptNode`s (9 grades x 2 strands, a complete grid, no gaps), 16
  grade-chain `PrerequisiteEdge`s (K→1→…→8 within each strand — same
  low-risk "VA's own strand taxonomy IS the progression" inference math
  made, not a claim copied from a published document; none exists for K-8
  ELA either).
- 150 real leaf standards recovered by following `hasChild` two levels deep
  (Strand → Sub-Strand → Standard — ELA's data has an extra Sub-Strand
  layer math's doesn't, e.g. "1.RI.1" "Key Ideas and Confirming Details" is
  itself a heading, not content; only the leaf `Standard`-type nodes'
  `description` text was kept).
- Provenance double-checked, not just cited: VDOE 403s direct fetches (same
  Akamai block teach-8xw.2 found for math), so (a) the Wayback CDX API
  (not the unreliable `availability` endpoint) was queried directly and
  shows live snapshots of the exact attribution URL
  (`doe.virginia.gov/home/showpublisheddocument/53643/638499760936600000`)
  from 2024-05 through 2025-11 — a real document, not a guessed URL; (b) the
  2025-10-07 snapshot was fetched and text-extracted with `pypdf`
  (`uv run --with pypdf` — ephemeral, not added to `pyproject.toml`/
  `uv.lock`), and two leaf-standard descriptions pulled from the Learning
  Commons JSON were found **verbatim** in the extracted PDF text, confirming
  Learning Commons' transcription matches VDOE's actual March 2024 "English
  Standards of Learning for Virginia Public Schools" document.
- Content-escalation spot check (same discipline `va_math_sol_graph.py`'s
  self-check applies to K.NS→8.NS): K.RI's leaves ask literal recall
  questions "with prompting and support"; 8.RI's leaves require analyzing
  how an author "establishes and conveys a perspective... and acknowledges
  and responds to conflicting evidence" — a genuine escalation, not just
  nine grade numbers in a row.
- Deliberately NOT curated to avoid boilerplate: grades 3/4/5's RI leaf
  standards share the bulk of their raw vocabulary ("cause", "effect",
  "comparison", "problem", "solution", "sequence", "search", "tools" all
  recur), exactly the real grade-to-grade overlap pressure VA Math SOL has.

**2. `tests/test_va_reading_sol_graph.py`** — structural tests for the new
loader, mirroring `test_va_math_sol_graph.py`'s coverage exactly (DAG
validity, no dangling edges, exact documented edge set, grade-order
topological sort, provenance recorded not asserted, cycle rejection). 10
tests, all real assertions against the loaded graph, no mocking.

**3. `tests/test_concept_recovery_non_math_domain.py`** — the bead's actual
target: `concept_recovery.recover_from_lesson_text` exercised against the
real VA Reading SOL K-8 graph, covering every outcome the math test suite
covers:

- correct recovery + signposted assumed-prerequisite (`va-reading-sol:4.RI`
  taught, `3.RI` assumed known, via a lesson quoting real 3.RI/4.RI leaf
  standard language),
- abstention on out-of-graph vocabulary (literary-theory text — unreliable
  narrator, focalization, metafiction — checked against a K-8 graph that
  has none of that vocabulary),
- unsignposted-prerequisite detection (same lesson content as the correct-
  recovery fixture with the "already learned" cue stripped),
- the ambiguous-match abstention gate under **real**, not invented,
  ambiguity pressure: a text built only from words VA Reading SOL grades
  3/4/5's RI strands genuinely share (not 4th grade's own distinctive
  words) scores top-3 = {3.RI, 4.RI, 5.RI} and correctly abstains rather
  than guessing one,
- the document-frequency boilerplate filter surviving real data: "texts"
  (doc freq 15/18), "including" (16/18), and "author" (13/18) are
  confirmed filtered out of K.RI's and 8.RI's distinctive vocabulary, while
  each grade's own distinctive words ("prompting" for K, "perspective" for
  8) survive.

All 5 tests pass on first correct attempt after one test-writing mistake
(see Known limitation below) was caught and fixed by actually running the
assertion, not assumed.

**4. Docstring + design-memory update, scoped honestly.** `concept_recovery
.py`'s module docstring gained a new "GENERICITY: MEASURED, NOT JUST
DESIGNED-FOR" section stating plainly what is now measured (recovery works
against one real non-math graph, this specific lesson-text set) and what
is NOT (generalization to arbitrary reading/writing/foreign-language text —
the lesson text is still hand-written by this session, not held out). The
`teach-8xw-10-concept-recovery-design` memory was updated the same way via
`bd remember --key`, replacing the unqualified "so non-math domains work"
line with a "GENERICITY CLAIM STATUS (teach-8xw.29)" paragraph making the
same measured/unmeasured distinction explicit for future readers.

## Evidence

```
$ uv run pytest -q
262 passed in 1.41s   # was 252 before this bead; +10 new tests, 0 regressions

$ PYTHONPATH=/workspace uv run python3 teach/va_reading_sol_graph.py
OK: 18 VA Reading SOL K-8 grade-strand groupings (150 sourced leaf standards)
load as a valid DAG (16 grade-chain edges across 2 strands); K.RI..8.RI
orders correctly and its endpoints' sourced standard text actually escalates
in content (prompted literal recall -> independent analysis of authorial
perspective), not just grade number
```

## Known limitation (stated, not hidden)

The lesson text in `test_concept_recovery_non_math_domain.py` is hand-
written by this session, exactly like every existing fixture in
`test_concept_recovery.py` (`CORRECT_RECOVERY_TEXT`, the `teach-8xw.26`
paraphrase fixtures, etc.) — this was never a "gather a held-out set"
bead, and the bead text itself only asked for real graph data, not a
blind lesson-text set. So this closes the *graph-genericity* gap
specifically: recovery has now been run against real non-math curriculum
data, with real boilerplate/overlap structure, and works. It does NOT
establish that recovery generalizes to arbitrary reading-domain lesson
text a persona might actually produce — that would need an independently
authored generalization set, the same kind of measurement `teach-8xw.26`
did for the semantic fallback tier's math false-positive risk. If a future
bead wants that measurement for the reading domain specifically, it should
be filed separately rather than assumed from this one; I did not file it
myself since it's new scope beyond what teach-8xw.29 asked for.

## Files touched

- `teach/data/va_reading_sol_k8.json` (new) — sourced data
- `teach/va_reading_sol_graph.py` (new) — loader + self-check
- `tests/test_va_reading_sol_graph.py` (new) — 10 structural tests
- `tests/test_concept_recovery_non_math_domain.py` (new) — 5 recovery tests
- `teach/concept_recovery.py` — docstring addition only (no logic changed)
- `bd remember --key teach-8xw-10-concept-recovery-design` — updated

No other in-progress uncommitted work in the tree (concept_recovery.py's
larger uncommitted diff, cialdini.py, etc. — left over from other beads
worked earlier this session) was touched or reverted.
