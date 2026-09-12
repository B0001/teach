# teach-8xw.52 — VA-specific World Language SOL graph (optional, picked up)

## What was asked

teach-8xw.46 confirmed live (Wayback CDX API) that VDOE really does publish a
World Language Standards of Learning document — the 2021-adopted "Grid View"
PDF at `doe.virginia.gov/home/showpublisheddocument/17824/638048064740900000`
— but flagged this as an *optional future option*, not a gap: the
foreign-language domain already has a working seed graph
(`teach/actfl_can_do_graph.py`, closed by teach-cr8), and this VA document is
PDF prose, not a structured feed, so it offers no shortcut. The bead's scope,
if picked up: hand-transcribe a small real slice (it suggested "the
Novice-level row across all four communication modes") into a second
ConceptGraph the same way teach-cr8 did for ACTFL — not a replacement for the
existing language-agnostic graph.

This session picked it up and built it.

## What was verified before building

- Re-ran the CDX API query fresh (not trusted from teach-8xw.46's notes):
  `web.archive.org/cdx/search/cdx?url=doe.virginia.gov/home/showpublisheddocument/17824/638048064740900000&output=json`
  returned 8 snapshots, all `application/pdf` / `statuscode 200`, spanning
  2025-02-08 through 2025-10-07. The Internet Archive was actually briefly
  down mid-session ("Temporarily Offline" page, same failure mode
  teach-8xw.39 hit) — waited ~20s and retried rather than treating the first
  failure as a negative result.
- Fetched the exact 2025-10-07 snapshot's PDF bytes
  (`web.archive.org/web/20251007191057if_/...`), confirmed real `%PDF-1.6`
  magic bytes (not an HTML error page), and extracted text with `pypdf`
  directly — no summarizer in the loop.
- Real document: "VIRGINIA WORLD LANGUAGE STANDARDS OF LEARNING 2021,
  Novice—Advanced", 28 pages. Page 1 (0-indexed page 0) is a "STRANDS and
  BENCHMARKS" overview grid: 5 strands (Intercultural, Interpretive,
  Interpersonal, Presentational, Communicative Literacy) × 3 levels (Novice,
  Intermediate, Advanced), each cell holding 2-3 numbered benchmark
  sentences.

## Scope decision — which slice, and why

Chose the page-1 overview grid over the finer per-sublevel tables later in
the same PDF (e.g. page 2's "INTERPRETIVE COMMUNICATION STANDARDS" table,
which further splits Novice/Intermediate/Advanced into Low/Mid/High columns
the way ACTFL's own sublevels do). Two reasons:

1. It matches the bead's own scope note ("a small real slice") — the
   overview grid is one page, cleanly quotable, and gives a real 3-level
   ordinal chain per strand without hand-transcribing 28 pages.
2. The bead's own summary undercounted the source's actual strands — it
   said "Interpretive/Interpersonal/Presentational... modes" but the real
   grid has five: those three, plus Intercultural (which VA's own document
   groups the same way) and Communicative Literacy (a cross-cutting fifth
   strand). Built from what the source actually contains, not the bead's
   summary of it — the bead itself says "where a design document and a bead
   disagree, the bead wins; where the code and a bead disagree, say so",
   and here it's the bead's *own prose summary* vs. the source document, so
   the source document wins and the discrepancy is stated in the module
   docstring rather than silently rounding to "four".

Kept all 5 real strands, including the finer sublevel breakdown as an
explicitly disclosed *unclaimed* next step for a future bead — flagged in
the module docstring so nobody assumes this graph already covers it.

## What was built

- `teach/va_world_language_sol_graph.py` — `load_va_world_language_sol_graph()`
  returns a 15-node ConceptGraph (5 strands × 3 levels), 10 edges (one strict
  Novice→Intermediate→Advanced chain per strand, no cross-strand edges — the
  source presents the five strands as independent axes of one learner, the
  same framing `actfl_can_do_graph.py` already documents for its four
  modes). `domain = "foreign-language"`, same tag the ACTFL graph uses (this
  is a second seed graph *within* that domain, not a new domain). Node ids
  namespaced `va-world-language-sol:<strand>:<level>` so they cannot collide
  with `actfl-can-do:*` ids (`test_no_node_id_collisions_with_actfl_graph`
  checks this).
- `_verify_provenance()` — a network-dependent function (not part of
  `_self_check()`, which must stay offline like every other domain's
  standalone self-check) that re-fetches the live Wayback snapshot and
  re-checks every transcribed string against the actual PDF bytes, rather
  than trusting the hand-transcription on faith. Run this session against
  the module's real data (not a separately retyped copy): 38 checks (25
  numbered benchmark statements across 5 strands × 3 levels, plus 5 strand
  labels — Communicative Literacy has 3 benchmarks per level, the other four
  strands have 2), 0 mismatches.
- `tests/test_va_world_language_sol_graph.py` — 14 tests: node/edge counts,
  true-DAG + no-dangling-edges, exact documented edge set, per-strand
  topological ordering, no-cross-strand-edges, real sourced text (not
  placeholders), content-escalation (Novice "simple sentences" →
  Advanced "probing questions", not just relabeled), the Communicative
  Literacy 3-vs-2 benchmark-count asymmetry, no-target-language, source
  provenance recorded, hand-introduced-cycle rejection, and no id collision
  with the ACTFL graph.

Followed `va_writing_sol_graph.py`'s doc-comment discipline (exact CDX
query, exact snapshot timestamp, exact fetch URL, magic-byte check) and
`actfl_can_do_graph.py`'s hand-transcription discipline (data embedded
directly in the module as quoted tuples, not a JSON data file — this is a
small hand-transcribed PDF slice, not a big streamed Learning-Commons feed).

## Verification run

```
$ uv run python3 -m teach.va_world_language_sol_graph
OK: 15 VA World Language SOL 2021 (strand, level) nodes across 5 strands
load as a valid DAG (10 strict Novice->Intermediate->Advanced chain edges,
no cross-strand edges); content escalates from simple-sentence Novice
exchanges to probing-question Advanced discussions, not just three level
labels in a row.

$ uv run --with pypdf python3 -c "import teach.va_world_language_sol_graph as m; m._verify_provenance()"
OK: 38 transcribed strings all verified verbatim in the live-fetched source PDF

$ uv run pytest tests/test_va_world_language_sol_graph.py -v
14 passed

$ uv run pytest -q
409 passed
```

## Known limitations, stated not hidden

- Only the page-1 overview grid is transcribed — the finer per-sublevel
  (Low/Mid/High) tables on later pages of the same 28-page PDF are real,
  fetchable, and not yet in this repo. A future bead that wants that
  granularity extends this module; it does not need to re-fetch anything,
  the same snapshot already covers it.
- `_verify_provenance()` is network-dependent and therefore not run by the
  test suite or `_self_check()` — it was run once manually this session (see
  above) and is available for a future worker to re-run rather than trust
  this handoff's numbers on faith.
- Same DECISION as `actfl_can_do_graph.py`: no target language is asserted
  anywhere (VA's own document says "using the target language" throughout,
  never naming one). This graph does not teach vocabulary or grammar for any
  specific language — only the ordinal benchmark ladder.
- No `concept_recovery`/checker integration test was written, matching
  teach-8xw.49's stated scope boundary for the same reason:
  `concept_recovery.py` claims domain-agnosticism by construction, and
  nothing about this graph's shape should require new checker code, but
  that claim was not re-exercised against this specific graph this session.

## Status

Closing as done: a second, VA-specific ConceptGraph was built from the real
2021-adopted VDOE document (fetched via Wayback, verified via magic bytes
and live substring re-check against the actual PDF, not recalled), sitting
alongside the existing language-agnostic ACTFL graph without replacing it,
with a full test suite (14 new tests) and the whole repo's 409 tests green.
