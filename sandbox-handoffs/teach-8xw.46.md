# teach-8xw.46 — re-attempt the VDOE/Wayback World Languages SOL check left inconclusive by an IA outage

## What was asked

teach-8xw.39's survey found a real negative for foreign-language structured
sources across Learning Commons, HuggingFace, and GitHub, but its
VDOE/Wayback direct-source check specifically was inconclusive — Internet
Archive's CDX API was intermittently returning a "Temporarily Offline" page
for broad domain-scoped queries during that session (a narrow known-good
query still worked, so this was IA flakiness on wide queries, not a
systemic block). That handoff named a follow-up bead ("teach-8xw.42") that
was never actually filed — a dangling reference. This bead is that filing,
re-running the check for real.

## Method — fetch the raw bytes, not a summary

Every claim below comes from a real `curl` against the Internet Archive CDX
API and the resulting PDFs, extracted with `pypdf` and read directly — no
WebFetch/WebSearch summarizer used, per sandbox-prompt.md's rule on
trusting your own tool calls over a summary that might mirror what you
were hoping to find.

## Finding 1 — Internet Archive is not down this session

Ran the same broad domain-scoped query style teach-8xw.39 described as
failing (`url=doe.virginia.gov&matchType=domain&filter=original:...`,
`limit=200`). Two separate broad queries both returned real JSON (HTTP 200,
71KB and 42KB respectively) with no "Temporarily Offline" page — one took
48s, one took 37s (CDX is just slow on wide domain queries, not broken).
The narrow known-good query from teach-8xw.29 (the exact reading-SOL
attribution URL) also still resolves instantly, consistent with both
sessions. **This channel is no longer inconclusive.**

## Finding 2 — Virginia DOES publish a World Language SOL (as anticipated), but it is unstructured, same category as math/reading's VDOE originals

Broad CDX queries for `doe.virginia.gov` filtered on "language"/"world
language" surfaced:

- `https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/world-language/standards-of-learning`
  — live in Wayback with ~45 snapshots from 2022 through 2026-08. Fetched
  the 2026-08-06 snapshot directly and confirmed by reading the extracted
  page text (not a summary): "The Virginia Board of Education adopted
  revised World Language Standards of Learning on March 18, 2021,"
  followed by "Standards of Learning Documents for World Language –
  Adopted 2021" (a single "World Language" course, Accessible Text /
  Grid View, Word+PDF) and a second, older "Adopted 2014" section split
  per language: All World Language, American Sign Language, Modern: Roman
  Alphabet Languages, Modern: Non-Roman Alphabet Languages, French,
  German, Latin, Spanish (each its own Word/PDF pair, Curriculum Framework
  column all "NA").
- Fetched the 2021 "Grid View" PDF itself
  (`doe.virginia.gov/home/showpublisheddocument/17824/638048064740900000`,
  Wayback snapshot 2025-10-07, `application/pdf` magic bytes confirmed,
  not an HTML error page) and extracted its text with `pypdf`: real
  standards prose, a Novice/Intermediate/Advanced ×
  Interpretive/Interpersonal/Presentational/Communicative-Literacy grid
  ("Comprehend spoken, written or signed information in very familiar,
  everyday contexts from authentic texts...", "Sustain spontaneous
  spoken, written or signed conversations and discussions on familiar and
  unfamiliar concrete topics...").
- Direct VDOE fetch (both the standards-of-learning page and the PDF
  itself) still 403s live, right now — same Akamai block already
  documented for math/reading/writing, not a new finding, just confirming
  the pattern holds for this domain too.

**This is a genuine, real document — but it is PDF/Word prose, not
graph/JSON/CASE-shaped.** It is exactly the category of source
`va_math_sol_graph.py` and `va_reading_sol_graph.py` had *before* Learning
Commons did the transcription work — and teach-8xw.39 already indepedently
re-verified, by streaming Learning Commons' entire `nodes.jsonl` across
every jurisdiction, that zero foreign-language nodes exist there for any
state. This VDOE PDF was never going to show up in that feed, and finding
it doesn't change that.

## Conclusion — the check is now genuinely negative, not inconclusive

- The IA outage is over; broad domain queries work.
- A real, structured-in-the-*document*-sense but not
  structured-in-the-*machine-readable* sense VA World Language SOL exists,
  confirmed by direct PDF fetch and text extraction — exactly what
  teach-8xw.39 predicted ("Virginia almost certainly does publish a World
  Languages SOL as a PDF").
- No graph/JSON/CASE-shaped structured source was found. The negative
  result stands: **teach-8xw.39's conclusion does not change**, and
  **teach-cr8's ACTFL/NCSSFL Can-Do seed choice does not need
  revisiting** — the VDOE document offers no shortcut over hand-
  transcription (the same effort ACTFL's PDFs already required), and its
  2014 per-language split reintroduces exactly the "which language"
  ambiguity teach-cr8 deliberately avoided by picking a language-agnostic
  source.

This closes the dangling "teach-8xw.42" reference from teach-8xw.39's
handoff for good.

## New bead filed (work outside this bead's scope)

`teach-8xw.52` — optional, low-priority: if a future worker wants a
*second*, VA-specific foreign-language `ConceptGraph` (mirroring
`teach-5aj`'s writing-SOL precedent — building from a real state-adopted
document rather than a national language-agnostic one), the 2021 Grid
View PDF found this session is a real, fetchable, spot-verified starting
point. Explicitly not a replacement for `teach/actfl_can_do_graph.py`, and
explicitly not a gap — the domain already has a working seed graph.

## Evidence

```
$ curl -sG "http://web.archive.org/cdx/search/cdx" \
    --data-urlencode "url=doe.virginia.gov" \
    --data-urlencode "matchType=domain" \
    --data-urlencode "filter=original:.*[Ww]orld.[Ll]anguage.*" \
    --data-urlencode "output=json" -m 90
HTTP:200 SIZE:42439 TIME:36.9s   # broad domain query succeeds, no outage page

$ curl -s "https://web.archive.org/web/20251007170841/.../showpublisheddocument/17824/638048064740900000" \
    -o /tmp/wl_sol_grid.pdf
$ head -c 10 /tmp/wl_sol_grid.pdf
%PDF-1.6%   # real PDF, not an HTML error page

$ uv run --with pypdf python3 -c "from pypdf import PdfReader; ..."
# extracted text confirmed real World Language SOL prose (Novice/
# Intermediate/Advanced x communication-mode grid)

$ curl -s -o /dev/null -w "HTTP:%{http_code}\n" \
    "https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/world-language/standards-of-learning"
HTTP:403   # direct VDOE fetch still blocked live, consistent with prior sessions

$ uv run pytest -q
395 passed   # no code touched this session; sanity check only
```

No code was written or modified this session — this bead was scoped as a
re-verification of a specific inconclusive check, and closes on that
verification plus the one follow-up bead it produced.

## Known limitations, stated not hidden

- The CDX filter/keyword approach is still keyword-based (same caveat
  teach-8xw.39 already flagged for its other channels) — a differently
  named VA page could in principle exist and not have matched these
  filters. But the specific dangling question this bead existed to close
  (was the IA outage hiding a structured source?) is now answered: no,
  and IA itself is not down.
- Did not attempt to fully diff every course of the 2014 per-language PDFs
  against the 2021 Grid View version — only confirmed the 2021 document's
  content is genuine prose standards, which was sufficient to answer the
  "structured or not" question this bead was scoped to.
