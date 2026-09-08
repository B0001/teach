# teach-8xw.5 — Build the VA Math SOL prerequisite knowledge graph

## Bottom line

Built a loadable `ConceptGraph` covering Virginia Mathematics SOL, grades
K-8, all 5 core strands (Number and Number Sense, Computation and
Estimation, Measurement and Geometry, Patterns/Functions and Algebra,
Probability and Statistics): 45 nodes, 40 `precedes` edges, a true DAG, no
dangling edges. High school (course-based, not grade-linear) is explicitly
out of scope and filed as `teach-8xw.16`.

- `teach/data/va_math_sol_k8.json` — the data: 45 grade x strand groupings,
  each carrying its real numbered VA SOL standards as sourced text.
- `teach/va_math_sol_graph.py` — the loader: builds a `ConceptGraph` per
  teach-8xw.4's schema, plus a `python3 -m teach.va_math_sol_graph`
  self-check.
- `tests/test_va_math_sol_graph.py` — 10 pytest tests (DAG validity, no
  dangling edges, exact edge set matches the documented rule, grade order
  respected within every strand, provenance recorded, cycle rejection).

`uv run pytest -q`: **79 passed** (69 pre-existing + 10 new). No pre-existing
test touched or broken.

## Why this shape (read this before changing the data or the edge rule)

teach-8xw.2 (blocking dependency) already established: **no existing graph
anywhere is seeded from, or usable as, a VA Math SOL prerequisite DAG.**
It also found the one thing that *is* real and reusable: the actual VA SOL
standard text lives in `github.com/learning-commons-org/knowledge-graph`
(CC BY-4.0), attributed to VDOE, but with **zero prerequisite edges** for
Virginia. This bead had to build from that node text; the edges are new.

I did not trust that finding secondhand — re-derived it this session by
streaming the same CDN files myself (see "What I actually did" below),
per sandbox-prompt.md's rule about not trusting a summarizer (even a prior
session's own handoff) on an existence/content question.

### Node granularity: (grade, strand) grouping, not individual standard

The source data has three levels: `Standard Grouping` (e.g. `2.NS` =
"Number and Number Sense", grade 2) → `Standard` (e.g. `2.NS.3`) →
lettered sub-bullets (e.g. `2.NS.3f`). I made the **groupings** the graph
nodes, and attached their child `Standard` records as opaque `facts`
payload rather than as separate graph nodes.

Why: the grouping level has a real, checkable order (grade sequence). The
individual numbered standards within one grouping (`2.NS.1` vs `2.NS.2` vs
`2.NS.3`) do **not** carry a documented order relative to each other
anywhere in this dataset — asserting `2.NS.1 precedes 2.NS.2` would be
inventing a prerequisite claim with no source. Keeping them as `facts`
means a domain consumer (teach-8xw.6's persona renderer, teach-8xw.11's
fact checker) still sees the real numbered-standard text, but the graph
structure only asserts what's actually justified.

### Edge derivation: the one substantive judgment call in this bead

`PrerequisiteEdge(K.NS, 1.NS)`, `PrerequisiteEdge(1.NS, 2.NS)`, ... chained
per strand. **This is not copied from a VDOE progression document** — none
was reachable (see below). It's a disclosed, mechanical rule: grade N+1's
bucket of a strand is assumed to build on grade N's bucket of the *same*
strand. This is about as low-risk an inference as a prerequisite claim
gets (grade order is definitional; VA organizes every grade into these
same 5 strands specifically so they read as a spiral progression) — but
it's still my inference, not a fact I have a citation for, and I've said so
in the module docstring rather than presenting it as sourced.

I did not stop at "this is probably fine" — the self-check and one pytest
test (`test_grade_progression_is_a_real_content_escalation_not_just_labels`)
verify the claim against actual content, not just grade numbers: K.NS's
text is about counting to 100, 1.NS to 120, and 8.NS is about the real
number system and its subsets. If the chain were wrong (e.g. if grouping
labels had been mismatched during extraction), this check would have a
real chance of catching it — a check on "is order.index(K) < order.index(8)"
alone would not, since that's true of any acyclic chain by construction.

### What's deliberately NOT here

- **High school (grades 9-12).** VA's HS math standards are organized by
  *course* (`A` = Algebra I, `G` = Geometry, `A2` = Algebra II, `AFDA`,
  plus electives `CM`/`DM`), all tagged `gradeLevel: ["9","10","11","12"]`
  with no finer grade signal to chain on. A real course sequence exists in
  VA (Algebra I → Geometry → Algebra II is the well-known default path) but
  I could not find a VDOE-published document to cite for it this session —
  see "What I checked and couldn't reach" below. Rather than assert it from
  general knowledge (exactly the thing sandbox-prompt.md warns against),
  I filed **teach-8xw.16** to either find a real source or document that
  none is reachable. The Learning Commons dataset does have the real HS
  course-strand node text already, ready for whoever picks that bead up.
- **Individual leaf-standard-to-leaf-standard edges** — see "node
  granularity" above.

## What I actually did (so this is reproducible, not just asserted)

1. `curl -sL "https://cdn.learningcommons.org/knowledge-graph/v1.13.0/exports/nodes.jsonl?ref=gh_curl"`
   streamed (not saved whole — piped straight into a filter) through a small
   Python script (`jq` is **not installed** in this sandbox — used
   `urllib.request` + line-by-line `json.loads` instead) filtering
   `labels contains StandardsFrameworkItem`, `jurisdiction == "Virginia"`,
   `academicSubject == "Mathematics"` → 1758 matches out of 290,718 total
   nodes (one fewer than teach-8xw.2's reported 1759 — consistent with a
   minor data-version drift between sessions, not a filtering bug; not
   investigated further since it doesn't affect the K-8 subset used here).
2. Of those 1758, exactly 45 have `normalizedStatementType == "Standard
   Grouping"` with a `statementCode` matching `<K|1-8>.<NS|CE|MG|PFA|PS>` —
   a complete 9-grade × 5-strand grid, verified with no gaps (printed and
   eyeballed the full 45-row list before trusting it).
3. Streamed `relationships.jsonl` the same way (499,498 total relationships)
   filtering `label == "hasChild"` with both endpoints in the 1758-node id
   set → 1756 edges. Filtered further to edges whose *source* is one of the
   45 groupings → their real numbered `Standard` children (118 total, e.g.
   `K.PS` has 1 child, `5.PS` has 3), each carrying real VDOE-sourced
   description text.
4. Wrote the curated result to `teach/data/va_math_sol_k8.json` (52 KB) and
   deleted the large intermediate downloads (`/tmp/lc_kg/*.jsonl`,
   ~900 MB) — reproducible from the CDN URLs, not worth keeping.

## What I checked and couldn't reach

- `doe.virginia.gov` and `www.doe.virginia.gov`: both return `403` from
  Akamai bot protection on every path tried (root, math instruction pages,
  the specific `showpublisheddocument` URL cited in the dataset's own
  `attributionStatement`) — confirmed live this session, matching
  teach-8xw.2's finding.
- Wayback Machine `availability` API on the exact `showpublisheddocument`
  URL: zero archived snapshots.
- No independent re-verification of VDOE's PDF text was possible; the
  standard text is sourced to Learning Commons's CC BY-4.0 export, which
  itself attributes to VDOE, and cross-checked internally via the content-
  escalation check described above rather than against the original PDF.

## Also checked: mathgraph is not reusable here

`pyproject.toml`'s `[tool.sandbox]` mounts a sibling repo at
`/workspace-mathgraph` (read-only). Given the epic explicitly invokes "the
mathgraph idea," I looked before assuming teach-8xw.4's design doc already
settled this. It has: `mathgraph` (per its own README) takes a LaTeX paper,
recovers its dependency graph, and aligns statements against `mathlib4` —
a research-level formal-math alignment tool, unrelated to K-12 curriculum
sequencing, and explicitly reports its own alignment layer as untrustworthy
at any operating point it measured. Nothing in it is reusable for this
bead beyond the `depends_on`-vs-`precedes` direction note teach-8xw.4
already flagged. Not touched, not imported.

## Verification

```
uv run pytest -q                      # 79 passed
uv run python3 -m teach.va_math_sol_graph   # self-check, prints OK line
```

## Follow-up filed

`teach-8xw.16` — extend to the HS course sequence (Algebra I / Geometry /
Algebra II / ...), blocked on finding a citable VA-specific course-sequence
source (or documenting that none is reachable).

## Files touched

- `teach/data/va_math_sol_k8.json` (new)
- `teach/va_math_sol_graph.py` (new)
- `tests/test_va_math_sol_graph.py` (new)
- `sandbox-handoffs/teach-8xw.5.md` (this file)

Nothing committed — conservative git policy, bead did not say to commit.
