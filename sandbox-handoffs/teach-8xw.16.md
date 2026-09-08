# teach-8xw.16 — Extend VA Math SOL graph to the high school course sequence

## Bottom line

Found a genuine, sourced VA-specific course-sequence document (satisfies
acceptance criterion (a); the negative-result path (b) was not needed) and
used it to add high-school course-level `PrerequisiteEdge`s to the graph,
with the source quoted in code:

- `teach/data/va_math_sol_hs.json` — 33 (course, strand) groupings across
  all 9 VA HS math courses, plus a `course_prerequisites` list of 7
  relations, each carrying the exact sentence it was read from.
- `teach/va_math_sol_graph.py` — extended with `load_va_math_sol_hs_data`,
  `load_va_math_sol_hs_graph`, `load_va_math_sol_full_graph` (unions K-8 +
  HS), a new module-docstring section explaining the sourcing and the
  bipartite-edge-expansion design decision, and an extended `__main__`
  self-check.
- `tests/test_va_math_sol_hs_graph.py` — 13 new pytest tests (DAG validity,
  no dangling edges, exact edge set matches the bipartite-product rule,
  topological order respects every sourced relation, every relation carries
  a real quote, abstention on the 3 courses with no sourced prerequisite,
  provenance recorded, cycle rejection, and the K-8/HS union is clean).

`uv run pytest -q`: **154 passed**, no pre-existing test touched or broken.
`uv run python3 -m teach.va_math_sol_graph`: both K-8 and HS self-checks OK.

## Why this shape (read this before changing the data or the edge rule)

### The prior "unreachable" finding was real but incomplete — and I didn't take it on faith

teach-8xw.2 and teach-8xw.5 each tried and failed to reach a VDOE
course-sequence document, and both are correct about what they actually
checked: `doe.virginia.gov` 403s all direct bot traffic (Akamai; I
reconfirmed this live, still true), and a Wayback Machine check against
`testing/sol/resources/crosswalks.html` (a *guessed* URL) found zero
snapshots. That guessed URL was never real — per teach-8xw.2's own handoff,
it came from a WebSearch result, not a fetched, read page.

Per sandbox-prompt.md's rule about not trusting a summarizer on an
existence/content question, I didn't stop at "prior sessions said this is
unreachable" — I went back to the Learning Commons dataset (the same one
teach-8xw.5 already streamed for K-8) and read its own
`attributionStatement` field for the VA HS math nodes, which cites a real
VDOE URL: `doe.virginia.gov/home/showpublisheddocument/48908/<id>`. I ran
the Wayback CDX API (`web.archive.org/cdx/search/cdx`, not the flakier
`availability` endpoint) against that exact URL family and got multiple
live snapshots, 2023 through 2026-04-16. The most recent one
(`https://web.archive.org/web/20260416041407/https://www.doe.virginia.gov/home/showpublisheddocument/48908/638741650017470000`)
is "Mathematics Standards of Learning for Virginia Public Schools,"
adopted August 2023 by the Virginia Board of Education — 115 pages,
1,254,006 bytes, fetched and read via `pypdf` text extraction, not summarized
by a tool. This corrects, rather than contradicts, the prior finding: it was
accurate for the URL those sessions tried, not for the document itself.

### What the source actually says, and what I chose not to assert

Most HS course intro paragraphs in that PDF explicitly name a prerequisite
by stating what students are assumed to have completed. I extracted 7 such
sentences and used them, verbatim, as the only source for
`course_prerequisites`:

| src | dst | quote (verbatim from the PDF) |
|---|---|---|
| A | G | "Geometry is a course designed for students who have successfully completed the Standards for Algebra 1." |
| A | AFDA | "Algebra, Functions, and Data Analysis is a course designed for students who have successfully completed the Standards for Algebra 1 and may benefit from additional support in their transition to Algebra 2." |
| A | A2 | "Students enrolled in Algebra 2 are assumed to have mastered the concepts outlined in the Algebra 1 Standards." |
| A | CM | "Students enrolled in Computer Mathematics are assumed to have studied the concepts and skills in Algebra 1 and beginning Geometry." |
| G | CM | (same sentence as above — Geometry is also named, with the weaker phrase "beginning Geometry") |
| G | MA | "Students enrolled in Mathematical Analysis are assumed to have mastered Geometry and Algebra 2 concepts." |
| A2 | MA | (same sentence as above) |

Three courses — Trigonometry, Probability and Statistics, Discrete
Mathematics — have no such sentence in their intros. I did not invent a
"well-known" ordering for them (e.g. "Trigonometry usually comes after
Geometry"); they get zero incoming edges, and a test
(`test_courses_without_a_sourced_prerequisite_sentence_get_no_incoming_edge`)
locks that in as a regression guard, not just an observation.

I also did not add a K-8 → Algebra 1 edge. The document's Algebra 1 section
says algebraic thinking "begins in kindergarten," but never cites a specific
K-8 grouping as Algebra 1's prerequisite the way the HS-to-HS sentences do —
same abstention rule applied.

### Node/edge granularity mismatch, and why the resolution is a full bipartite product

Nodes are (course, strand) groupings (`G.RLT`, `A.EO`, ...) — same level as
the K-8 data, for the same reason (individual numbered standards within a
grouping carry no documented order). But the sourced relation is at
*course* granularity ("completed Algebra 1"), and a course's strand codes
don't line up across courses the way K-8 grade-groupings do (Geometry has
DF/PC/RLT/TR; Algebra 1 has EI/EO/F/ST — no shared code to chain on, unlike
K-8's shared 5-strand grid). A single edge from one Algebra 1 grouping to
one Geometry grouping would not actually force "all of Algebra 1 before all
of Geometry" under `topological_order()` — Kahn's algorithm would still
accept an ordering with an unconnected Algebra 1 grouping after a Geometry
one. So `load_va_math_sol_hs_graph()` builds the full bipartite product:
every grouping of the prerequisite course to every grouping of the
dependent course (96 edges from 7 sourced relations). This is generated
mechanically from `course_prerequisites`, not hand-typed, and is the
minimum edge set that actually gives the topological-sort guarantee. A test
(`test_edges_are_exactly_the_bipartite_product_of_sourced_course_pairs`)
checks the produced edge set against an independently-recomputed expected
set, not just a count.

### Also found, and deliberately not used: a 2020 VDOE policy shift away from a single track

While searching, I also found VDOE's "Virginia Mathematics Pathways
Initiative" (VMPI) slide deck (`vmpi.pptx`, fetched via Wayback, not kept),
which documents VA's 2020 move *away* from a single canonical Algebra 1 →
Geometry → Algebra 2 track toward multiple locally-chosen pathways. This is
real and worth knowing as context for anyone building a persona/curriculum
layer on top of this graph — the 7 edges here are real prerequisite
statements from the current (August 2023) standards document, not a claim
that every VA student follows one fixed sequence — but it doesn't
contradict or block what's implemented: the sourced sentences are still
literally true prerequisite requirements for those specific courses,
regardless of how many alternate pathways a district offers around them.
Not filed as a follow-up bead — it's scope/caveat context for graph
consumers, not a defect in this graph.

## What I actually did (so this is reproducible, not just asserted)

1. Streamed `nodes.jsonl`/`relationships.jsonl` from the same Learning
   Commons CDN URLs teach-8xw.5 used, filtered to VA HS math `Standard
   Grouping` nodes (33, across 9 courses) and their `hasChild` edges to real
   numbered standards (114 leaf standards) — same method as K-8, extended to
   the HS subset.
2. Read each grouping's `attributionStatement` to find the real VDOE
   publication URL (`showpublisheddocument/48908/...`), confirmed
   `doe.virginia.gov` still 403s live bot traffic today, then queried the
   Wayback CDX API directly against that URL family and got real snapshot
   timestamps back (not a guess, not a tool's summary of "probably exists").
3. Fetched the 2026-04-16 snapshot, extracted text with `pypdf`
   (`uv run --with pypdf python3 -c "..."`), whitespace-normalized it, and
   located each course's intro paragraph by searching for its course name;
   copied the prerequisite-naming sentence verbatim into
   `course_prerequisites[].source_quote`.
4. Wrote `teach/data/va_math_sol_hs.json`, extended
   `teach/va_math_sol_graph.py` with the loader functions and docstring
   section above, extended the `__main__` self-check, and wrote
   `tests/test_va_math_sol_hs_graph.py`.
5. Deleted all large intermediate downloads from `/tmp`
   (`lc_nodes.jsonl` 327MB, `lc_relationships.jsonl` 545MB, several PDFs,
   the VMPI pptx, ~900MB total) — reproducible from the cited URLs, not
   worth keeping, matching teach-8xw.5's precedent.

## Verification

```
uv run pytest -q                            # 154 passed
uv run python3 -m teach.va_math_sol_graph   # both K-8 and HS self-checks print OK
```

## Follow-up filed

None. This bead's acceptance criteria are fully satisfied by the sourced
edges above; no scope was found that needed a new bead.

## Files touched

- `teach/data/va_math_sol_hs.json` (new)
- `teach/va_math_sol_graph.py` (modified — new docstring section, 3 new
  loader functions, extended self-check)
- `tests/test_va_math_sol_hs_graph.py` (new)
- `sandbox-handoffs/teach-8xw.16.md` (this file)

Nothing committed — conservative git policy, bead did not say to commit.
