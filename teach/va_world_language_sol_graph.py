"""Producer stage: an optional, VA-specific World Language SOL seed graph for
the foreign-language domain (teach-8xw.52).

teach-8xw.39 found no structured (JSON/CASE-shaped) foreign-language source
for any jurisdiction, so teach-cr8 built the foreign-language domain's seed
graph (`actfl_can_do_graph.py`) from ACTFL/NCSSFL's national, language-
agnostic Can-Do Statements instead. teach-8xw.46 then confirmed, live against
the Wayback CDX API, that Virginia's VDOE *does* publish its own World
Language Standards of Learning as a real PDF -- just not in a structured
feed, so it offers no shortcut over hand-transcription. teach-8xw.52 is the
bead that picked up that optional, explicitly-not-blocking option: a second,
VA/course-specific graph, mirroring `va_writing_sol_graph.py`'s precedent of
building from a state-adopted document, sitting alongside (not replacing)
the language-agnostic ACTFL graph -- exactly as teach-8xw.52's own bead text
specifies.

PROVENANCE -- fetched live this session, not recalled (sandbox-prompt.md's
"fetch the raw bytes and read them yourself" rule):

  VDOE's own site 403s direct fetches (same Akamai block already documented
  for math/reading/writing/the World Language listing page), so the Wayback
  Machine was used, as teach-8xw.46 already verified live: the CDX API
  (`web.archive.org/cdx/search/cdx?url=doe.virginia.gov/home/showpublisheddocument/
  17824/638048064740900000&output=json`) was queried fresh this session and
  returned 8 snapshots of that exact URL, `application/pdf`, `statuscode 200`,
  spanning 2025-02-08 through 2025-10-07 -- the same 2025-10-07 snapshot
  teach-8xw.46 cited (`20251007191057`) confirmed still present, not assumed
  from the prior bead's notes. That snapshot's PDF bytes were then fetched
  (`web.archive.org/web/20251007191057if_/https://www.doe.virginia.gov/
  home/showpublisheddocument/17824/638048064740900000`), confirmed to start
  with the real `%PDF-1.6` magic bytes (not an HTML error page -- the failure
  mode sandbox-prompt.md's PyPI/narrator incident warns about), and text-
  extracted with `pypdf` (`uv run --with pypdf python3 ...`) -- no summarizer
  in the loop. Document title (from the PDF's own first page): "VIRGINIA
  WORLD LANGUAGE STANDARDS OF LEARNING 2021, Novice-Advanced". 28 pages
  total; only page 1 (the "STRANDS and BENCHMARKS" overview grid) is used
  here -- see NODE GRANULARITY below for why.

  Every benchmark string embedded in `_STRAND_DATA` below was checked
  programmatically against that same page's extracted text: both sides
  lowercased and whitespace-collapsed (`re.sub(r"\\s+", " ", ...)`, matching
  `va_writing_sol_graph.py`'s and `actfl_can_do_graph.py`'s own normalization
  discipline for PDF line-wrap artifacts), then required to be an exact
  substring. The run against this module's actual data (not a separately
  retyped copy) reported 38 checks / 0 mismatches (25 numbered benchmark
  statements + 5 strand-name labels, +5 more statements from the
  three-bullet Communicative Literacy strand's third level of repetition --
  see the strand table for the exact count). The check script itself was
  ephemeral (matching teach-cr8's and teach-5aj's own method) and is not part
  of this repo.

NODE GRANULARITY -- one node per (strand, level) pair, not the finer-grained
per-sublevel or per-standard-code tables the later pages of the same PDF
contain (e.g. page 2's "INTERPRETIVE COMMUNICATION STANDARDS" table, which
subdivides Novice/Intermediate/Advanced into Low/Mid/High columns the way
ACTFL's own Can-Do sublevels do). That finer table exists in the source and
is a natural next step for a future bead, but was deliberately left
untranscribed here to keep this bead's slice the small, quickly-verifiable
one its own scope note asked for ("hand-transcribe a small real slice...
e.g. the Novice-level row across all four communication modes") --
transcribing all five strands' full Low/Mid/High/Advanced-High breakdown
across 28 pages would be a much larger effort than this bead's text
describes, and each additional page transcribed is another surface for a
silent transcription error this session's `_verify_provenance` check
wouldn't catch (it only checks page 1). A future bead that wants that
granularity should extend this module, not replace it.

  The overview grid (PDF page 1, 0-indexed page 0) is a 5 (strand) x 3
  (level) table, each cell holding 2 or 3 numbered benchmark sentences:
    - INTERCULTURAL Communication and Connections
    - INTERPRETIVE Communication
    - INTERPERSONAL Communication
    - PRESENTATIONAL Communication
    - Communicative LITERACY (a cross-cutting fifth strand integrating the
      other four -- present in the source's own grid, so kept rather than
      dropped to force a round "four modes" the bead's summary mentioned but
      the source itself does not limit itself to)
  All five strand labels are transcribed exactly as printed (including the
  source's own inconsistent capitalization, e.g. "Communicative LITERACY"
  vs. "INTERCULTURAL Communication and Connections" -- not normalized to a
  uniform style, since sandbox-prompt.md's fidelity rule applies to
  formatting quirks too, not just content).

EDGE PROVENANCE -- ordinal, and the source states the ordering claim
explicitly (unlike VDOE's math/reading/writing grade-chains, which this repo's
own docs flag as an *inference* VDOE never states outright): the document's
own title is "Novice--Advanced", and ACTFL's Can-Do framework (which this
grid's Novice/Intermediate/Advanced terms are drawn directly from -- see
`actfl_can_do_graph.py`'s own DECISION section on the same ordinal ladder)
states "Each sublevel includes the abilities of the prior sublevels." VA's
own grid presents the three levels left-to-right in exactly that order in
every one of its five strand rows. So each strand gets a 3-node chain,
Novice -> Intermediate -> Advanced, one edge per consecutive pair -- no
skip-edges, no cross-strand edges (the source presents the five strands as
independent axes of the same learner, the same "independent modes" framing
`actfl_can_do_graph.py`'s SOURCE["independent_modes_quote"] already
documents for ACTFL's parallel Interpretive/Interpersonal/Presentational
modes).

DECISION -- domain and target language, same reasoning `actfl_can_do_graph.py`
already recorded and still binding here: this grid is language-agnostic in
the source itself (every benchmark says "using the target language", never
naming one), so this module keeps that framing and does not invent a target
language. `domain` is "foreign-language", the same tag `actfl_can_do_graph.py`
uses -- this is a second, VA-specific seed graph *within* that domain, not a
new domain. Node ids are namespaced `va-world-language-sol:...` so the two
graphs' ids cannot collide (checked by
`test_no_node_id_collisions_with_actfl_graph`).
"""
from __future__ import annotations

from teach.concept_graph import ConceptGraph, ConceptNode, PrerequisiteEdge

DOMAIN = "foreign-language"

SOURCE = {
    "title": "Virginia World Language Standards of Learning 2021, Novice-Advanced",
    "publisher": "Virginia Department of Education (VDOE)",
    "adopted": "2021",
    "listing_page": (
        "https://www.doe.virginia.gov/teaching-learning-assessment/k-12-"
        "standards-instruction/world-language/standards-of-learning"
    ),
    "document_url": (
        "https://www.doe.virginia.gov/home/showpublisheddocument/17824/"
        "638048064740900000"
    ),
    "retrieved_via": (
        "Wayback Machine (VDOE's own site 403s direct fetches -- same Akamai "
        "block documented for math/reading/writing)"
    ),
    "wayback_snapshot": "20251007191057",
    "wayback_url": (
        "https://web.archive.org/web/20251007191057if_/https://www.doe."
        "virginia.gov/home/showpublisheddocument/17824/638048064740900000"
    ),
    "retrieved": "2026-09-12",
    "extracted_with": "pypdf",
    "source_page": (
        "PDF page 1 (0-indexed page 0), the 'STRANDS and BENCHMARKS' "
        "Novice/Intermediate/Advanced overview grid"
    ),
    "ordering_note": (
        "The document's own title states the range 'Novice-Advanced'; the "
        "three levels are presented left-to-right in that order in every "
        "strand row of the overview grid."
    ),
}

# (strand_id_suffix, strand_name_as_printed, {level: [benchmark statements, verbatim]})
_STRAND_DATA = (
    (
        "intercultural",
        "INTERCULTURAL Communication and Connections",
        {
            "Novice": (
                "Identify typical products and practices to help make "
                "connections to and understand perspectives in native and "
                "other cultures using the target language.",
                "Interact at a survival level in everyday contexts with "
                "people in and from other cultures using the target "
                "language and appropriate rehearsed behaviors.",
            ),
            "Intermediate": (
                "Make comparisons between products and practices to help "
                "make connections to and understand perspectives in native "
                "and other cultures using the target language.",
                "Interact at a functional level in familiar contexts with "
                "people in and from other cultures using the target "
                "language and appropriate learned behaviors.",
            ),
            "Advanced": (
                "Explain some diversity among products and practices and "
                "how it relates to perspectives in native and other "
                "cultures using the target language.",
                "Interact at a competent level in familiar and some "
                "unfamiliar contexts with people in and from other cultures "
                "using the target language and adjusting behaviors as "
                "needed.",
            ),
        },
    ),
    (
        "interpretive",
        "INTERPRETIVE Communication",
        {
            "Novice": (
                "Comprehend spoken, written or signed information in very "
                "familiar, everyday contexts from authentic texts presented "
                "through a variety of media and based on familiar topics.",
                "Identify the general topic and basic information from "
                "words, phrases and simple sentences in authentic "
                "informational and fictional texts and overheard or "
                "observed conversations.",
            ),
            "Intermediate": (
                "Comprehend information in a variety of familiar contexts "
                "from authentic texts that are spoken, written or signed.",
                "Understand the main idea and related information from "
                "connected sentences and short paragraphs in authentic "
                "informational and fictional texts and overheard or "
                "observed conversations.",
            ),
            "Advanced": (
                "Comprehend information in a wide variety of familiar and "
                "general interest contexts from authentic texts that are "
                "spoken, written or signed.",
                "Understand the main message and supporting details from "
                "paragraphs across various time frames in complex, "
                "organized authentic texts and overheard or observed "
                "conversations.",
            ),
        },
    ),
    (
        "interpersonal",
        "INTERPERSONAL Communication",
        {
            "Novice": (
                "Communicate in spontaneous spoken, written or signed "
                "conversations on very familiar, everyday topics.",
                "Request and provide information using a variety of "
                "practiced or familiar words, phrases, simple sentences and "
                "questions.",
            ),
            "Intermediate": (
                "Communicate in spontaneous spoken, written or signed "
                "conversations on familiar topics.",
                "Exchange information using connected sentences and a "
                "variety of questions.",
            ),
            "Advanced": (
                "Sustain spontaneous spoken, written or signed "
                "conversations and discussions on familiar and unfamiliar "
                "concrete topics.",
                "Discuss and explain information, incorporating various "
                "time frames, series of connected sentences, paragraphs "
                "and probing questions.",
            ),
        },
    ),
    (
        "presentational",
        "PRESENTATIONAL Communication",
        {
            "Novice": (
                "Present prepared or spontaneous information on very "
                "familiar, everyday topics through written, spoken or "
                "signed language.",
                "Inform, narrate and express preferences and opinions "
                "using a variety of practiced or familiar words, phrases "
                "and simple sentences.",
            ),
            "Intermediate": (
                "Present prepared or spontaneous information on familiar "
                "topics through written, spoken or signed language.",
                "Explain, narrate and express viewpoints using sentences "
                "and series of connected sentences.",
            ),
            "Advanced": (
                "Present detailed and organized presentations on familiar "
                "as well as unfamiliar concrete researched topics.",
                "Analyze, narrate and convey persuasive arguments using "
                "various time frames and paragraphs.",
            ),
        },
    ),
    (
        "literacy",
        "Communicative LITERACY",
        {
            "Novice": (
                "Use literacy skills to comprehend authentic texts that "
                "are spoken, written or signed.",
                "Use interpersonal skills to interact, negotiate meaning "
                "and communicate effectively.",
                "Use presentational skills to communicate effectively.",
            ),
            "Intermediate": (
                "Use literacy skills to deepen understanding of authentic "
                "texts that are spoken, written or signed.",
                "Use interpersonal skills to interact, negotiate meaning "
                "and communicate effectively.",
                "Use presentational skills to communicate effectively.",
            ),
            "Advanced": (
                "Use literacy skills to integrate understanding of "
                "authentic texts that are spoken, written or signed.",
                "Use interpersonal skills to interact, negotiate meaning "
                "and communicate effectively.",
                "Use presentational skills to communicate effectively.",
            ),
        },
    ),
)

LEVEL_ORDER = ("Novice", "Intermediate", "Advanced")

STRAND_IDS = tuple(suffix for suffix, _, _ in _STRAND_DATA)


def _node_id(strand_suffix: str, level: str) -> str:
    return f"va-world-language-sol:{strand_suffix}:{level.lower()}"


def load_va_world_language_sol_graph() -> ConceptGraph:
    """The five-strand x three-level VA World Language SOL overview grid as
    a validated ConceptGraph: 15 nodes, one strict Novice -> Intermediate ->
    Advanced ordinal chain per strand (10 edges total), no cross-strand
    edges. Raises GraphError (via ConceptGraph.validate) if the strand table
    above were ever hand-edited into an inconsistent state.
    """
    nodes = []
    edges = []
    for suffix, strand_name, levels in _STRAND_DATA:
        level_ids = [_node_id(suffix, level) for level in LEVEL_ORDER]
        for level, node_id in zip(LEVEL_ORDER, level_ids):
            nodes.append(
                ConceptNode(
                    id=node_id,
                    domain=DOMAIN,
                    label=f"{strand_name} ({level})",
                    standard_ref=f"VA World Language SOL 2021, {strand_name} -- {level}",
                    facts={
                        "strand_name": strand_name,
                        "level": level,
                        "benchmark_statements": levels[level],
                    },
                )
            )
        for earlier, later in zip(level_ids, level_ids[1:]):
            edges.append(PrerequisiteEdge(src=earlier, dst=later))

    graph = ConceptGraph(nodes=tuple(nodes), edges=tuple(edges))
    graph.validate()
    return graph


def _verify_provenance() -> None:
    """Re-derive every transcribed string's presence in the actual source
    PDF, fetched fresh via the same Wayback snapshot SOURCE records, rather
    than trusting the hand-transcription in `_STRAND_DATA` on faith. Network-
    dependent, so it is not part of `_self_check()` (which must run offline
    like every other domain's `python3 <module>.py` self-check) -- run it
    directly (`uv run --with pypdf python3 -c "import
    teach.va_world_language_sol_graph as m; m._verify_provenance()"`) when
    re-verifying provenance rather than as part of the standard self-check
    or test suite.
    """
    import re
    import urllib.request

    from pypdf import PdfReader

    req = urllib.request.Request(
        SOURCE["wayback_url"], headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        pdf_bytes = resp.read()
    assert pdf_bytes[:5] == b"%PDF-", "fetched bytes are not a real PDF"

    import io

    reader = PdfReader(io.BytesIO(pdf_bytes))
    page_text = reader.pages[0].extract_text()

    def norm(s: str) -> str:
        s = s.replace("-\n", "")
        s = re.sub(r"\s+", " ", s)
        return s.strip().lower()

    haystack = norm(page_text)

    checked = 0
    for _, strand_name, levels in _STRAND_DATA:
        assert norm(strand_name) in haystack, strand_name
        checked += 1
        for level, statements in levels.items():
            for statement in statements:
                assert norm(statement) in haystack, (strand_name, level, statement)
                checked += 1

    print(f"OK: {checked} transcribed strings all verified verbatim in the live-fetched source PDF")


def _self_check() -> None:
    graph = load_va_world_language_sol_graph()
    assert len(graph.nodes) == 15, len(graph.nodes)
    assert len(graph.edges) == 10, len(graph.edges)

    order = graph.topological_order()
    for suffix in STRAND_IDS:
        ids = [_node_id(suffix, level) for level in LEVEL_ORDER]
        positions = [order.index(i) for i in ids]
        assert positions == sorted(positions), suffix

    # Real content escalation, not just three level labels in a row: Novice
    # interpersonal leans on "practiced or familiar words, phrases" and
    # "simple sentences"; Advanced names neither and adds "discussions" and
    # "probing questions" instead.
    novice = graph.by_id("va-world-language-sol:interpersonal:novice")
    advanced = graph.by_id("va-world-language-sol:interpersonal:advanced")
    novice_text = " ".join(novice.facts["benchmark_statements"]).lower()
    advanced_text = " ".join(advanced.facts["benchmark_statements"]).lower()
    assert "simple sentences" in novice_text
    assert "probing questions" in advanced_text
    assert "probing questions" not in novice_text

    # No target language is asserted anywhere -- see the DECISION section.
    for node in graph.nodes:
        assert node.domain == "foreign-language"
        blob = " ".join(
            str(v) for v in node.facts.values() if not isinstance(v, tuple)
        ) + " ".join(
            " ".join(v) for v in node.facts.values() if isinstance(v, tuple)
        )
        blob = blob.lower()
        for language in ("spanish", "french", "japanese", "mandarin", "german"):
            assert language not in blob, (node.id, language)

    print(
        f"OK: {len(graph.nodes)} VA World Language SOL 2021 (strand, level) nodes "
        f"across {len(STRAND_IDS)} strands load as a valid DAG ({len(graph.edges)} "
        "strict Novice->Intermediate->Advanced chain edges, no cross-strand edges); "
        "content escalates from simple-sentence Novice exchanges to probing-question "
        "Advanced discussions, not just three level labels in a row."
    )


if __name__ == "__main__":
    _self_check()
