# teach-8xw.49 — ACTFL Can-Do graph: add Interpretive, Presentational, and
Intercultural Communication (teach-cr8 only covered Interpersonal)

## What was asked

`teach/actfl_can_do_graph.py` (built in teach-cr8) models 11 ordinal
ACTFL/NCSSFL proficiency sublevels, but every node's facts are drawn only
from Interpersonal Communication — a disclosed, deliberate first-pass scope
choice in `sandbox-handoffs/teach-cr8.md`. Real ACTFL Can-Do Statements also
cover Interpretive Communication, Presentational Communication, and
Intercultural Communication at every sublevel. This bead asked for those
three added, sourced from the same PDFs teach-cr8 used, preserving its
verbatim-substring verification method and its no-target-language guarantee,
with the "additional facts vs. parallel node sets" design choice left to
whoever picked this up — provided the reasoning is stated either way.

## Design choice — parallel node sets, not bolted-on facts

Recorded in the module docstring's `TEACH-8XW.49` section. Two independently
sufficient reasons:

1. **Interpretive and Presentational Communication share Interpersonal's
   exact 11-sublevel granularity** in the source (Novice Low/Mid/High ...
   Distinguished), so they get their own 11-node ordinal chains —
   `actfl-can-do:interpretive:<sublevel>` and
   `actfl-can-do:presentational:<sublevel>` — mirroring the existing
   Interpersonal chain's shape exactly.
2. **Intercultural Communication is not broken into sublevels anywhere in
   the source.** All four level-specific PDFs present Intercultural Can-Do
   Statements once per *major* level only (Novice, Intermediate, Advanced,
   Superior, Distinguished — 5, not 11), organized around two dimensions,
   Investigation and Interaction, not the single function-based
   `performance_indicator` the other three modes use. Forcing an 11-sublevel
   split or a single `performance_indicator` field onto Intercultural would
   assert structure the source doesn't contain — the same "a number is only
   allowed to exist in a document if the code produces it" principle
   `sandbox-prompt.md` states for numeric claims, applied here to graph
   structure. So Intercultural gets its own 5-node chain,
   `actfl-can-do:intercultural:<major-level>`, with `investigation_*` and
   `interaction_*` fact fields instead of `performance_indicator`.

Each mode is returned by its own loader function
(`load_actfl_can_do_graph` unchanged for Interpersonal;
`load_actfl_interpretive_graph`, `load_actfl_presentational_graph`,
`load_actfl_intercultural_graph` new) rather than one merged graph, and there
are **no edges between modes**: the source states outright that the modes
are independent axes of the same learner —
"Learners may be at different levels for different modes (Interpretive,
Interpersonal, Presentational) or skills (reading, listening, writing,
speaking, viewing, signing)" (`Can-Do-Novice.pdf`, quoted verbatim in
`SOURCE["independent_modes_quote"]`). Inventing a cross-mode edge would
assert an ordering claim the source explicitly denies.

## What was built

- `_INTERPRETIVE_SUBLEVELS` / `_PRESENTATIONAL_SUBLEVELS` — 11-entry tuples,
  same shape as teach-cr8's `_SUBLEVELS` (suffix, label, major_level,
  proficiency_benchmark, performance_indicator).
- `_INTERCULTURAL_LEVELS` — 5-entry tuple with a different shape (suffix,
  label, investigation_benchmark, investigation_indicator_products,
  investigation_indicator_practices, interaction_benchmark,
  interaction_indicator_language, interaction_indicator_behavior).
- `INTERPRETIVE_SUBLEVEL_ORDER`, `PRESENTATIONAL_SUBLEVEL_ORDER`,
  `INTERCULTURAL_LEVEL_ORDER` — analogous to `SUBLEVEL_ORDER`.
- `load_actfl_interpretive_graph()`, `load_actfl_presentational_graph()`,
  `load_actfl_intercultural_graph()` — each builds, validates, and returns
  its own `ConceptGraph` with a strict ordinal chain of `PrerequisiteEdge`s,
  following `load_actfl_can_do_graph()`'s exact pattern.
- `SOURCE["other_modes_and_functions"]` and `SOURCE["independent_modes_quote"]`
  — the new modes' function prompts and the independence quote, recorded as
  provenance the same way `SOURCE["ordering_quote"]` already was.
- Self-checks: `_self_check_interpretive()`, `_self_check_presentational()`,
  `_self_check_intercultural()` (structural + content-escalation +
  no-target-language, per mode), and
  `_self_check_no_cross_mode_collisions()` (the four graphs' node ids are
  disjoint — genuinely parallel, not accidentally merged). `__main__` now
  runs all five self-checks.
- `tests/test_actfl_can_do_graph.py` — 25 new tests (12 → 37 total):
  parametrized structural tests (DAG validity, exact edge set, sole
  root/leaf, topological order, mode/function-prompt consistency,
  no-target-language) shared across Interpretive and Presentational since
  they're structurally identical; separate tests for Intercultural's
  different shape (5-node chain, dimension-prompt constancy across levels);
  content-escalation tests per mode; and a cross-mode node-id-collision test.

## Method — fetch the raw bytes, re-verify against the live module, not a
remembered summary

The same five PDFs teach-cr8 used were re-fetched this session
(2026-09-11), same URLs, same `%PDF-1.4` magic-byte check, same `pypdf`
extraction (`uv run --with pypdf python3 ...`), text read directly with no
summarizer in the loop:

```
https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Novice.pdf
https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Intermediate.pdf
https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Advanced.pdf
https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Superior-Distinguished.pdf
https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Benchmarks-Indicators-11x17_2026-02-10-011907_btgx.pdf
```

Every new fact string was checked programmatically as an exact substring of
the corresponding source PDF's extracted text, normalized (lowercased,
whitespace-collapsed) with two artifact-specific fixes:

1. **Ligature glyphs**: `pypdf` renders "fl"/"fi"/"ff" as single Unicode
   ligature characters, sometimes followed by a stray space from kerning
   (e.g. `"reﬂ  ect"` for "reflect"). The fix substitutes the ligature and
   strips trailing whitespace at the same substitution site, before general
   whitespace collapsing — collapsing first would leave a spurious single
   space still splitting the word.
2. **Line-wrap hyphenation**: caught late, and worth flagging explicitly
   since it's exactly the kind of "confirms what I hoped to find" trap
   `sandbox-prompt.md` warns about. My first check of
   `SOURCE["independent_modes_quote"]` against the module's *stored* string
   reported a mismatch. The raw PDF text has
   `"...or skills (reading, listen-\ning, writing..."` — `pypdf` preserves
   the source PDF's line-wrap hyphen literally where the justified layout
   broke "listening" across two lines. That's a print-layout artifact, not
   a real hyphen in the word, so the normalizer now also strips a bare
   `-\n` before collapsing whitespace. Re-running the check after that fix
   passed. This was **not** caught by the module's own self-check (which
   only asserts structural properties, not the `SOURCE` dict's quote
   fidelity) — it was caught by a targeted re-verification pass run
   specifically to double-check every claim on the way to writing this
   handoff, not by the original check I ran while writing the module. Doing
   that re-check is what this repo's standard asks for; skipping it would
   have shipped a quote silently drifted from the source it cites.

Final verification, run against the actual data as loaded from the live
module (not a separately-retyped copy of the strings) — script is ephemeral
and not part of this repo, matching teach-cr8's own precedent:

```
$ uv run --with pypdf python3 /tmp/verify_module_against_pdfs.py
81 checks run against live module data
ALL MATCH
```

(76 node-fact strings across the three new loaders — `proficiency_benchmark`
+ `performance_indicator` × 11 sublevels × 2 modes, plus 6 fields × 5 levels
for Intercultural — and 5 `SOURCE`-dict quote fragments, including the two
literal quoted fragments inside the composite Intercultural
`other_modes_and_functions` entry.)

## Evidence

```
$ uv run python3 -m teach.actfl_can_do_graph
OK: 11 NCSSFL-ACTFL Can-Do proficiency sublevels (Novice Low..Distinguished)
load as a valid, strictly ordinal DAG (10 edges), sourced from ACTFL's real
2026 Can-Do Statements PDFs with no target language asserted.
OK: 11 NCSSFL-ACTFL Interpretive Communication sublevels load as a valid,
strictly ordinal DAG (10 edges).
OK: 11 NCSSFL-ACTFL Presentational Communication sublevels load as a valid,
strictly ordinal DAG (10 edges).
OK: 5 NCSSFL-ACTFL Intercultural Communication levels load as a valid,
strictly ordinal DAG (4 edges) -- 5 major levels, not 11 sublevels, matching
the source's own granularity.
OK: all 38 node ids across the four Can-Do mode graphs (Interpersonal,
Interpretive, Presentational, Intercultural) are unique -- the graphs are
genuinely parallel, not accidentally overlapping.

$ uv run pytest tests/test_actfl_can_do_graph.py -v
37 passed

$ uv run pytest -q
379 passed
```

(Full suite was already green with other beads' uncommitted work present in
the tree — sandbox-handoffs for teach-8xw.36/.37/.40/.44/.45/.50/.51,
teach-5aj, biblical_ot_source, va_writing_sol_graph, etc. Nothing in this
bead's scope touched those files.)

## Known limitations, stated not hidden

- This still has no content a producer could use to teach actual vocabulary
  or grammar — only the ordinal "what can a learner do" ladder, now covering
  four communication modes instead of one. teach-cr8's DECISION (no target
  language committed) is unchanged and still applies to all four graphs.
- The four mode graphs are entirely independent — no edges connect a
  sublevel in one mode to a sublevel in another, by design (the source says
  modes are independent axes, not a dependency chain). A consumer that wants
  "the whole Can-Do domain for one learner" must call and combine all four
  loaders itself; nothing here does that for them.
- No `concept_recovery`/checker integration test was written for the three
  new graphs, matching teach-cr8's own stated scope boundary for the same
  reason: `concept_recovery.py` claims domain-agnosticism by construction
  and nothing about these graphs' shape should require new code there, but
  that claim was not re-exercised against these specific graphs this
  session.
- The Intercultural `other_modes_and_functions` SOURCE entry is a composite
  string (my own "Investigation --"/"Interaction --" labels wrapped around
  two literal quoted fragments), not a single verbatim source sentence like
  the Interpretive/Presentational entries. Each quoted fragment was verified
  independently against the source; the labels and semicolon joining them
  are structural framing, not asserted as the source's own prose.

## Status

Closing as done: the bead's "what closes this" criterion — Interpretive,
Presentational, and Intercultural content added with teach-cr8's
verbatim-substring method preserved, the no-target-language guarantee
intact, and the design choice stated with reasoning — is met, verified
against the live module's actual data (not a remembered or separately
retyped copy) after catching and fixing a real hyphenation-artifact bug in
that verification, with the full test suite green.
