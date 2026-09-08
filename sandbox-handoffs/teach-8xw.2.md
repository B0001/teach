# teach-8xw.2 — Survey existing VA Math SOL prerequisite knowledge graphs before building one

## Bottom line

**No existing graph is seeded from, or directly usable as, a VA Math SOL
prerequisite DAG.** But the survey found a near-miss worth recording in
detail, because it changes what "build one from scratch" should mean for
teach-8xw.5: the actual VA SOL Math standard text already exists in a
well-licensed public graph dataset, correctly coded — it just has zero
prerequisite edges and zero crosswalk to the one dataset that does have
prerequisite edges for K-12 math. Building teach-8xw.5 from *nothing* would
be wrong; building it by re-typing 400+ standards from PDFs would be wasted
effort. The gap is specifically the edges, not the nodes.

A prior session's shallow pass (see the bead's own description) checked only
three HuggingFace dataset-search queries and found nothing. This session
widened the search to HuggingFace (broader queries), GitHub repo search,
arXiv, direct inspection of the most promising GitHub projects' actual data
files, and Wayback-Machine-mediated checks of VDOE's own site (VDOE blocks
direct `curl`/bot traffic with a 403, including on the bare root domain, so
it had to be approached this way). Every conclusion below is grounded in a
command run this session, not recollection — full commands and outputs are
in this session's transcript, not reproduced verbatim here for length.

## What exists: Learning Commons Knowledge Graph (closest candidate)

- Repo: `github.com/learning-commons-org/knowledge-graph` (151 stars, active,
  latest data release v1.13.0 dated 2026-08-27, confirmed current against
  its own `.release-please-manifest.json`).
- Data: two JSONL exports, `nodes.jsonl` (343MB, 290,718 nodes) and
  `relationships.jsonl` (571MB, 499,498 edges), CC BY-4.0, downloadable
  without auth from `cdn.learningcommons.org`.
- **It has real Virginia Math SOL content**: 1,759 `StandardsFrameworkItem`
  nodes with `jurisdiction: "Virginia"`, `academicSubject: "Mathematics"`,
  correct SOL-style `statementCode`s (e.g. `2.NS.3f`), sourced and attributed
  directly to VDOE-published documents (URLs on `doe.virginia.gov` cited in
  each node's `attributionStatement`).
- **It has zero prerequisite structure for Virginia.** I built an id→edge
  index over the full downloaded files (not a sample) and checked every
  edge label that touches any of the 1,759 VA Math node ids:
  - `buildsTowards` (the prerequisite/progression edge type) touches **0**
    Virginia nodes. All 757 `buildsTowards` edges in the entire dataset
    connect only `Multi-State Mathematics` nodes (i.e. Common Core) to each
    other — this 757 figure is not a coincidence, see next section.
  - `hasStandardAlignment` (the state-standard → Common-Core crosswalk edge
    type used for 40+ other states) touches **0** Virginia nodes, of *any*
    subject, not just math. I listed every source jurisdiction with at
    least one `hasStandardAlignment` edge (42 states plus DC) — Virginia is
    conspicuously absent, consistent with the well-known fact that Virginia
    never adopted Common Core and uses SOL independently.
  - `supports`, `relatesTo`, `hasEducationalAlignment`, `hasReference`: all
    **0** for Virginia math nodes.
  - The only edge type touching Virginia math nodes at all is `hasChild`
    (1,759/1,759 — the strand→sub-strand→standard outline hierarchy, not a
    prerequisite/dependency relation).
  - Two more edge types exist (`hasDependency`, 209 edges; `mutuallyExclusiveWith`,
    192 edges) but both are entirely internal to Illustrative Mathematics
    curriculum objects (`LessonGrouping`, `Assessment`), not standards, and
    touch zero VA nodes.

**Conclusion on this dataset**: it is the right place to source verified VA
SOL Math standard *text* and codes (real content, permissively licensed,
attributed to VDOE), but it currently contributes nothing toward the
prerequisite *edges* teach-8xw.5 needs. Worth flagging to whoever builds
teach-8xw.5 as a starting node-list, not a starting graph.

## What exists: the underlying Common Core prerequisite dataset

The 757 `buildsTowards` edges above are the *same* dataset independently
findable at `github.com/markpaik/coherence-map-explorer` (created 2026-07-16,
CC0-licensed code, data vendored from Student Achieve the Core's now-
unmaintained "Coherence Map" tool, itself CC0 per achievethecore.org's
permissions page): **480 Common Core K-12 math standards, 757 directed
prerequisite edges**, DAG-verified, built by Student Achievement Partners
(Jason Zimba, a lead CCSS math author). This is a real, substantial,
permissively-licensed prerequisite graph for K-12 math — just for Common
Core, not SOL, and Virginia has no official crosswalk connecting the two
(see below). Reusing it for VA would require building and defending a VA
SOL ↔ CCSS crosswalk first, which is itself nontrivial: SOL and CCSS place
some topics at different grades, so borrowing CCSS's prerequisite structure
wholesale risks asserting a sequencing VA's own standards don't actually
follow. That tradeoff is a decision for teach-8xw.5, not this bead — flagging
it so it isn't rediscovered from scratch there.

## What was checked and found genuinely absent or inconclusive

- **VDOE's own site**: `doe.virginia.gov` blocks direct HTTP requests from
  this sandbox with a 403 (confirmed on the bare root domain too, so it's
  bot-blocking, not a dead site — Wayback Machine has a live snapshot of the
  root from 2026-08-14). A WebSearch-tool-suggested URL,
  `doe.virginia.gov/testing/sol/resources/crosswalks.html` (an SOL↔Common-Core
  crosswalk document), **has zero Wayback Machine snapshots ever** — strong
  evidence it doesn't exist and was hallucinated by the tool (see tooling
  note below). I then searched the Wayback CDX index for every URL ever
  archived under `doe.virginia.gov` containing any of `crosswalk`,
  `comparison`, `commoncore`, `common_core`, `vertical`, `progression` —
  zero hits on all six terms. This doesn't prove VDOE has never published a
  SOL/CCSS comparison document (it could be un-crawled, e.g. a PDF behind a
  search portal), but nothing findable through this channel exists.
- **HuggingFace datasets**: 11 search queries beyond the prior session's 3
  (`SOL math`, `virginia standards`, `K-12 math knowledge graph`,
  `curriculum graph`, `learning progression math`, `math curriculum dag`,
  `standards of learning`, `learning map math`, `prerequisite math`,
  `achieve the core`, `common core coherence`). Only two non-noise hits:
  `Borisz42/CTNSG-Graph-Curriculum` and `akumch/graph-reasoning-foundational-curriculum`
  (both ML-curriculum-learning datasets, i.e. "curriculum" in the ML training
  sense, not education-curriculum sense — checked and ruled out) and
  `allenai/achieve-the-core` (a *hierarchical standards taxonomy*, not a
  prerequisite graph — CCSS-only, no dependency edges, built for an LM
  math-standard-tagging benchmark, arXiv:2408.04226 "Mathfish").
- **GitHub repo search**: 7 query strings. Beyond the two real hits above
  (`coherence-map-explorer`, `learning-commons-org/knowledge-graph`), also
  found `haojing8312/cn-k12-math-knowledge-graph` — a genuine, well-built,
  DAG-validated prerequisite graph (1,327 topics, 1,204 edges) for
  **Chinese** compulsory-education math (grades 1–9). Not usable as VA SOL
  content (wrong curriculum, wrong language), but worth a structural note:
  it explicitly leaves 438 zero-in-degree topics marked "unresolved" after
  AI-assisted review rather than asserting "confirmed no prerequisite" —
  the same abstain-over-guess posture this repo's own standard asks for.
  Also found `Chiiicky/curriculum-aligned-math-solution-generation`, which
  turned out on inspection to be an RL-reward-modeling paper (curriculum in
  the training-difficulty sense) — ruled out.
- **arXiv**: spot-checked one paper via the export API; two keyword-phrase
  queries against the search API returned zero results, but the query
  encoding may have been malformed (no `all:"..."` quoting) — treat this
  channel as under-tested, not exhausted, if anyone wants to push further.

## Tooling note for future sessions (not a repo bug, but costs time if unknown)

`WebSearch` in this sandbox does not perform a search. On every query this
session, it returned a canned "here's how you'd search" non-answer, once
with a fabricated-looking URL presented as a real result (the VDOE crosswalk
URL above, which Wayback shows was never archived). This matches a prior
session's finding on `teach-8xw.1` about `WebFetch` hallucinating package
metadata that exactly confirmed the search terms it was given. Pattern:
tools that summarize/search on this sandbox's behalf are not trustworthy for
existence claims — always drop to raw `curl` against a real API (HF
datasets API, GitHub API, Wayback CDX/`availability` API, arXiv export API)
and inspect the actual bytes.

## What this does NOT do

- Does not build anything. teach-8xw.5 is still fully open.
- Does not decide the crosswalk-vs-scratch question for teach-8xw.5 — that's
  a real design tradeoff (documented above) for whoever picks that bead up.
- Does not touch `teach-8xw.3` (common reference site for AI-consumable
  graphs) even though Learning Commons is an extremely relevant find for it
  (it explicitly positions itself as exactly that: a multi-state,
  multi-subject, graph-native, publicly-downloadable education standards
  graph). Flagging the connection here for whoever picks up .3; not doing
  that bead's work in this one.

## Verification

```
uv run pytest -q     # 16 passed — unchanged, no code was touched by this bead
```

No source files were created or modified. Large downloaded artifacts
(`/tmp/lc_kg/nodes.jsonl`, `relationships.jsonl`, ~900MB total) were deleted
at the end of the session — they're a public CDN download, trivially
reproducible from the URLs above, not worth keeping in a temp dir.

## Files touched

None in the repo tree besides this handoff and the bead's own notes/status.

Nothing committed — conservative git policy, bead did not say to commit.
