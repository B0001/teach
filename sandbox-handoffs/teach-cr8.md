# teach-cr8 — Foreign-language domain: decide target language(s) and
hand-transcribe a minimal ACTFL/NCSSFL Can-Do seed graph

## What was asked

teach-8xw.39's survey found no existing AI-consumable prerequisite-DAG-shaped
source for foreign language anywhere (Learning Commons, HuggingFace, GitHub,
VDOE/Wayback). This bead was scoped as "decide + hand-transcribe a minimal
seed," not "build a full domain": (a) decide which target language(s) the
graph should model, recording the reasoning explicitly rather than defaulting
silently, and (b) hand-transcribe a small real seed graph — the ~10 top-level
ACTFL proficiency sublevels as ConceptNodes with ordinal PrerequisiteEdges,
sourced from ACTFL's actual published Can-Do document (fetch and quote the
real text, don't paraphrase from training-data recall).

## Decision — no target language committed

Recorded in `teach/actfl_can_do_graph.py`'s module docstring (DECISION
section) and enforced by a test
(`test_no_target_language_is_asserted_anywhere`). Reasoning, in short:

1. The NCSSFL-ACTFL Can-Do Statements are themselves published
   language-agnostic — every "I can..." descriptor names a communicative
   function, never a language, by design.
2. teach-8xw.39's negative result is total across every language, not just
   Virginia's SOL: there is no structured source yet to build a real
   per-language vocabulary/grammar layer from. Inventing one now would be
   exactly the self-authored-material risk sandbox-prompt.md's "you cannot
   hold out examples from yourself" section warns about.
3. Keeps the seed honest about its own size — an ordinal proficiency-level
   skeleton, not a language curriculum. A future bead that wants to actually
   teach one language would hang a second, language-specific content layer
   off these sublevel nodes; that is out of scope here and is flagged in the
   module so the next worker doesn't assume this graph is closer to "done"
   than it is.

`domain` is `"foreign-language"`, not e.g. `"spanish"`.

## What was built

`teach/actfl_can_do_graph.py` — an 11-node, 10-edge strictly ordinal
`ConceptGraph`: Novice Low/Mid/High → Intermediate Low/Mid/High → Advanced
Low/Mid/High → Superior → Distinguished. Modeled as hand-authored embedded
data (like `dummit_foote_graph.py`), not a JSON feed (like
`va_reading_sol_graph.py`/`va_writing_sol_graph.py`), because there is no
structured feed here to load from — hand-transcription was the whole point
of this bead.

All eleven nodes are drawn from the *same* communication mode and function —
Interpersonal Communication, "How can I exchange information and ideas in
conversations?" — the first function listed under Interpersonal
Communication in every one of ACTFL's four level-specific PDFs. This keeps
the chain reading as one coherent ladder instead of stitching together
unrelated skills across levels.

`tests/test_actfl_can_do_graph.py` — 12 tests: structural (DAG, no dangling
edges, exact edge set, sole root/leaf), content-escalation (Novice Low leans
on gesture/visual support and memorized language; Distinguished names
neither and adds culturally nuanced complex discourse), the no-target-
-language guard, source-provenance fields, and a hand-introduced-cycle
regression guard matching the existing graphs' test pattern.

## Method — fetch the raw bytes, not a summary

Per sandbox-prompt.md's rule: WebSearch was tried once and (as prior surveys
found) came back as a canned "I can't search the web" non-answer rather than
real results — not used further. Instead:

1. `curl`'d ACTFL's own Can-Do Statements listing page
   (`https://www.actfl.org/educator-resources/ncssfl-actfl-can-do-statements`,
   HTTP 200) and grepped its HTML for real `.pdf` links, rather than
   guessing a URL (a guessed URL for a different ACTFL PDF failed earlier in
   this session, returning an HTML 404 page instead of a PDF — caught by
   checking the first bytes, not by trusting the HTTP 200 curl gave for the
   redirect target).
2. Fetched all 5 linked PDFs directly with `curl`, confirmed each starts
   with the `%PDF-1.4` magic bytes (not an HTML error page — the same class
   of check that would have caught the fabricated `narrator` PyPI summary
   sandbox-prompt.md describes).
3. Extracted text with `pypdf` (`uv run --with pypdf python3 ...` — pypdf is
   not a project dependency, installed ephemerally the same way the prior
   `va_reading_sol_graph.py` session apparently did) and read the extracted
   text myself.
4. Verified programmatically, not just by eye: every `proficiency_benchmark`
   and `performance_indicator` string in the module is an exact
   whitespace-normalized substring of the corresponding source PDF's
   extracted text (script run and shown passing — "ALL MATCH" — before
   writing this handoff).

Real PDFs fetched this session (all still on ACTFL's live site as of
2026-09-11):
```
https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Novice.pdf
https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Intermediate.pdf
https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Advanced.pdf
https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Superior-Distinguished.pdf
https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Benchmarks-Indicators-11x17_2026-02-10-011907_btgx.pdf
```

The ordering claim (src precedes dst) is not this session's inference the
way VA Math/Reading's grade-chain is — the Benchmarks-Indicators PDF states
it directly: "Can-Do Statements describe what learners can independently do
at each sublevel and help pave the way to higher levels... Each sublevel
includes the abilities of the prior sublevels." Quoted verbatim in
`SOURCE["ordering_quote"]`.

## Evidence

```
$ uv run python3 -m teach.actfl_can_do_graph
OK: 11 NCSSFL-ACTFL Can-Do proficiency sublevels (Novice Low..Distinguished)
load as a valid, strictly ordinal DAG (10 edges), sourced from ACTFL's real
2026 Can-Do Statements PDFs with no target language asserted.

$ uv run pytest tests/test_actfl_can_do_graph.py -v
12 passed

$ uv run pytest -q
339 passed
```

(Full suite was already green with a number of other beads' uncommitted work
present in the tree — teach-5aj/writing, biblical_ot_source, etc. Nothing in
this bead's scope touched those files; `git status` shows them as pre-
existing untracked/modified state, not something this session produced.)

## Known limitations, stated not hidden

- This is a proficiency-level skeleton, not a language curriculum. It has no
  content a producer could use to actually teach vocabulary or grammar in
  any language — only the ordinal "what can a learner do" ladder. Teaching
  a real target language off this graph is explicitly out-of-scope future
  work (see DECISION section), not implied to be covered.
- Only one communication mode/function (Interpersonal — exchanging
  information and ideas) is represented per sublevel. ACTFL's real Can-Do
  Statements also cover Interpretive Communication, Presentational
  Communication, and Intercultural Communication at every sublevel; this
  seed deliberately picked one function for coherence rather than trying to
  represent all four in a first pass. A follow-up could add parallel node
  sets for the other modes.
- No `concept_recovery`/checker integration test was written (unlike
  `test_dummit_foote_graph.py`'s Bond-lesson recovery test) — out of scope
  for "hand-transcribe a minimal seed"; `concept_recovery.py`'s own design
  claims domain-agnosticism by construction, and nothing about this graph's
  shape (opaque `facts`, standard node/edge types) should require new code
  there, but that claim was not re-exercised against this specific graph
  this session.

## Status

Closing as done: the bead's own "what would close this" section names
option (a) — a documented decision plus a small real seed graph sourced with
va_reading_sol_graph.py-level provenance rigor — and that is what exists
now, verified against the source text programmatically, not just by
eyeball, with the full test suite green.
