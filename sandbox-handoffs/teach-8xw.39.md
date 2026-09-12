# teach-8xw.39 — survey: writing and foreign-language domains

## What was asked

Survey (not build) two of the epic's four claimed domains — writing and
foreign language — that have no `ConceptGraph`/`SourceAdapter` at all today
(confirmed by re-running the bead's own `ls teach/*.py` check: still only
`va_math_sol_graph.py`, `dummit_foote_graph.py`, `va_reading_sol_graph.py`).
Per teach-8xw.2's precedent (survey before build), document what
standards/frameworks exist, whether any are already published in an
AI-consumable graph format, and a recommended starting scope — without
committing to implementation.

## Method — fetch the raw bytes, not a summary

Per sandbox-prompt.md's rule on trusting your own tool calls: every claim
below was checked by curling a real API/feed and parsing the JSON myself,
not by asking a summarizer. WebSearch was not used (teach-8xw.1 and
teach-8xw.2 both found it non-functional/fabricating in this sandbox);
`curl` was used against the HuggingFace datasets API, the GitHub repo-search
API, and the Learning Commons `nodes.jsonl` export directly.

## Finding 1 — Writing: real curriculum-scale source already sitting in
the repo's existing pipeline

teach-8xw.29 built `teach/va_reading_sol_graph.py` from
`cdn.learningcommons.org/knowledge-graph/v1.13.0/exports/nodes.jsonl`,
filtering Virginia English-Language-Arts nodes for the `RI`/`RL` reading
strands. I streamed that same 300MB+ feed again (via
`curl -sN URL | grep -m N pattern`, letting `grep` kill the pipe early
rather than downloading the whole file where not needed) and confirmed:

- Virginia's ELA slice (1580 nodes total — same count teach-8xw.29
  reported, re-verified independently) contains a **`W` (Writing) strand
  present at every grade K–12**, structurally identical to `RI`/`RL`:
  236 nodes, `Standard Grouping` headings (e.g. `10.W` "The student will
  write in a variety of forms for diverse audiences and purposes...",
  `7.W.1` "Modes and Purposes for Writing") over real leaf `Standard` text
  (e.g. `12.W.3.A` "Revise writing for clarity of content, accuracy, and
  depth of information.", `8.W.1.C` "Write persuasively, supporting
  well-defined points of view effectively with relevant evidence.").
- Full strand inventory for VA ELA in this feed, for context: `C`
  (Communication/oral), `DSR`, `FFR`/`FFW` (K-5 foundational reading/
  writing skills), `LU` (Language Usage), `R`, `RI`, `RL`, `RV`, `W` — `W`
  spans the complete K-12 grid with no gaps, same shape as `RI`/`RL`.
- This is the **same source, same license (CC BY-4.0), same provenance
  chain** (VDOE attribution URL, Wayback-archivable, direct VDOE fetch
  403s the same way) that teach-8xw.2 and teach-8xw.29 already vetted for
  math and reading. Building `teach/va_writing_sol_graph.py` would be a
  near-mechanical repeat of `va_reading_sol_graph.py`'s pattern (strand
  node -> two `hasChild` hops -> leaf `Standard` text, K→1→...→12
  grade-chain edges) — the survey step this bead exists to do is now done;
  what's left is genuinely just implementation, which is why I filed it as
  a build bead below rather than doing it inside a survey bead.
- Data snapshot saved this session at `/tmp/va_ela_nodes.jsonl` (1580
  lines, not committed to the repo — ephemeral scratch, re-fetchable from
  the same URL) for whoever picks up the build bead, so they don't have to
  re-stream 300MB+ to re-derive this.

## Finding 2 — Foreign language: negative result across every channel
checked, including the repo's own established source

- **Learning Commons (the repo's own established source):** streamed the
  *entire* `nodes.jsonl` feed (all jurisdictions, not just Virginia) and
  grepped every node whose `academicSubject` contains "Language", "World",
  "Foreign", or a specific language name. Result: **zero** matches outside
  "English Language Arts" (94,206 ELA nodes total, across every
  jurisdiction in the dataset, none of them world/foreign language). This
  is a stronger and more relevant negative than a generic web search: it's
  the exact pipeline this repo already trusts and has twice verified
  end-to-end, and it simply does not carry foreign-language content for
  *any* state, not just Virginia.
- **HuggingFace dataset search API** (direct `curl`, not WebSearch): 8
  queries — "CEFR can do graph", "language proficiency DAG", "foreign
  language curriculum graph", "ACTFL proficiency", "curriculum DAG",
  "skill graph education", "NCSSFL", plus an initial CEFR query. Only real
  hits were CEFR *sentence-level readability classification* datasets
  (e.g. `astrideducation/cefr-combined-no-cefr-test` — 3.3M sentences
  each tagged with a CEFR difficulty level via lexical frequency). These
  are text-difficulty classifiers, not prerequisite-DAG-shaped
  skill-sequence graphs — wrong shape for this repo's `ConceptGraph`
  model, not a match.
- **GitHub repo search API** (direct `curl`, confirmed past an initial
  rate-limit by re-running after it cleared and checking `total_count`
  rather than trusting empty output): "ACTFL can-do" → 0, "CEFR
  proficiency levels prerequisite" → 0, "world language standards
  knowledge graph" → 1 hit, irrelevant (an unrelated W3C report repo).
- **VDOE/Wayback direct check** (the method teach-8xw.2/.29 used to
  cross-verify math and reading against the actual VDOE PDF): Internet
  Archive's CDX API was intermittently returning a literal "Temporarily
  Offline" outage page during this session for broader domain-scoped
  queries (confirmed against a known-good narrow query — the exact
  reading-SOL attribution URL from teach-8xw.29 still resolved fine, so
  this is IA flakiness on wide queries, not a systemic block). **This
  channel is inconclusive, not negative** — stated honestly rather than
  folded into the "no results" finding above. Virginia almost certainly
  does publish a World Languages SOL as a PDF (every VDOE subject does);
  the open question this leaves is only whether it's published anywhere
  in graph/structured form, which is what actually matters for this
  survey.
- **What does exist, unstructured:** ACTFL (actfl.org, reachable, HTTP
  200) and NCSSFL jointly publish "Can-Do Statements" — a real,
  widely-used ordinal proficiency framework (Novice→Intermediate→
  Advanced→Superior→Distinguished, each with Low/Mid/High sub-bands),
  and the Council of Europe publishes CEFR (A1–C2) with its own can-do
  descriptors. Both are inherently chainable the same low-risk way
  math/reading grade-strands are (`Novice-Low -> Novice-Mid -> ... ->
  Distinguished`). Neither was found published as machine-readable
  nodes+edges anywhere searched — building from either would mean
  transcribing PDF/HTML text by hand, the same category of effort
  va_math_sol_graph.py and va_reading_sol_graph.py avoided by finding an
  existing structured feed. This is also where the bead's own text flags
  real scope ambiguity ("which language?") that a survey shouldn't
  resolve by picking one.

## Recommended starting scope (not committed to — per bead's own ask)

Split into two follow-up beads, since the two domains turned out to need
completely different next steps — exactly the situation the bead
anticipated ("may reasonably split... once the survey clarifies how
different the two efforts are"):

1. **Writing** — low-risk, high-confidence build bead: reuse the existing
   Learning Commons pipeline, mirror `va_reading_sol_graph.py` exactly.
   Filed as `teach-5aj` (child of `teach-8xw`).
2. **Foreign language** — genuinely unresolved seed choice: no existing
   AI-consumable prerequisite graph found anywhere checked; smallest real
   seed candidate is ACTFL/NCSSFL Can-Do Statements (freely published,
   ordinal, ~5-10 top-level proficiency nodes), but the source would need
   to be hand-transcribed rather than fetched structured, and "which
   target language" is a real open decision this survey deliberately did
   not make. Filed as `teach-cr8` (child of `teach-8xw`), scoped as
   "decide + hand-transcribe a minimal seed" rather than "build," since
   the survey step for this one genuinely didn't find a shortcut the way
   it did for writing.

## Evidence

```
$ ls teach/*.py
teach/__init__.py  teach/biblical_nt_source.py  teach/biblical_ot_source.py
teach/boundary.py  teach/cbt_primitives.py  teach/cialdini.py
teach/cialdini_integration_check.py  teach/concept_graph.py
teach/concept_recovery.py  teach/dnf_bond_integration.py
teach/dnf_bond_lesson.py  teach/dummit_foote_graph.py  teach/fact_checker.py
teach/honesty_rubric.py  teach/math_facts.py  teach/persona.py
teach/potential_checker.py  teach/producer_state.py  teach/publish_graph.py
teach/va_math_sol_graph.py  teach/va_reading_sol_graph.py
# still no writing_*.py / *language*.py — confirms the bead's premise held

$ wc -l /tmp/va_ela_nodes.jsonl
1580 /tmp/va_ela_nodes.jsonl   # matches teach-8xw.29's reported VA ELA count

# W-strand node count within that file: 236, K-12 complete grid (script-verified, not eyeballed)

$ uv run pytest -q
(unchanged — no code touched this session, survey only)
```

No code was written or modified this session. This bead is scoped as
survey-only per its own "What would close this" section, and closes on
the survey write-up plus the two follow-up beads it names.

## Known limitations, stated not hidden

- The GitHub and HuggingFace searches are keyword-based, same as
  teach-8xw.2's "not exhaustive" caveat — a differently-worded existing
  resource could still exist and not have been found.
- The Wayback/VDOE direct-source check for foreign language is genuinely
  inconclusive (IA outage during this session), not a verified negative.
  Whoever picks up teach-8xw.42 should re-attempt it rather than treat
  this survey's silence as confirmation nothing exists.
- "Writing" here means Virginia's K-12 Writing SOL specifically — the
  same VA-only, K-12-only scope math and reading already carry in this
  repo. Extending beyond VA or beyond K-12 (e.g. undergraduate
  composition) is unexamined and out of scope for this survey.
