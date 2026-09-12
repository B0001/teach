"""Producer stage: a minimal ACTFL/NCSSFL Can-Do proficiency-sublevel seed
graph for the foreign-language domain (teach-cr8).

teach-8xw.39 surveyed this domain and found no shortcut: unlike math, reading,
and writing (all built from the same structured Learning Commons/VDOE feed),
Learning Commons carries zero foreign-language content for any jurisdiction,
and no dataset or repo search turned up an existing prerequisite-DAG-shaped
source (see sandbox-handoffs/teach-8xw.39.md). What does exist, unstructured,
is ACTFL/NCSSFL's jointly published "Can-Do Statements" -- so this module
hand-transcribes a small real seed from that source, the same category of
effort dummit_foote_graph.py used for Dummit & Foote (embedded, quoted data,
not a fetched JSON feed), rather than the Learning-Commons-pipeline pattern
va_reading_sol_graph.py/va_writing_sol_graph.py used.

DECISION -- which target language(s), recorded explicitly per the bead's own
instruction not to default silently:

  This graph does not commit to a target language. The NCSSFL-ACTFL Can-Do
  Statements are themselves published language-agnostic -- every "I can..."
  descriptor names a communicative function ("exchange information...",
  "discuss and debate...") and never a language, precisely so the same
  ladder can self-assess a learner of Spanish, Japanese, or ASL alike. Three
  reasons this seed keeps that framing rather than picking one language:

    1. Fidelity to the source: inventing "Spanish for X" content bolted onto
       these nodes would be asserting curriculum the cited document does not
       contain -- exactly the kind of claim sandbox-prompt.md's "a number is
       only allowed to exist in a document if the code produces it" rule
       exists to block, applied to prose rather than a number.
    2. teach-8xw.39's negative result is total, not Virginia-specific: zero
       AI-consumable structured source was found for *any* language, so
       there is nothing to build a real per-language vocabulary/grammar
       layer from yet. Picking "Spanish" today would mean hand-authoring
       that content from memory, the exact self-authored-material risk
       sandbox-prompt.md's "you cannot hold out examples from yourself"
       section warns against.
    3. It keeps the seed honest about its own size: this is an ordinal
       proficiency-level skeleton (Novice-Low..Distinguished), not a
       language curriculum. A future bead that wants to actually teach one
       language would hang a second, language-specific content layer off
       these sublevel nodes (e.g., PrerequisiteEdge from a sublevel into a
       "Spanish: ordering food" node) -- out of scope here, and flagged so
       the next worker doesn't assume this graph is closer to "done" than
       it is.

  domain is therefore "foreign-language", not "spanish" or similar.

PROVENANCE -- fetched live this session, not recalled (sandbox-prompt.md's
"fetch the raw bytes and read them yourself" rule):

  ACTFL's own Can-Do Statements listing page --
  https://www.actfl.org/educator-resources/ncssfl-actfl-can-do-statements
  (fetched 2026-09-11, HTTP 200, real page, not a guessed URL) -- links
  five real PDFs, each fetched directly and confirmed to start with the
  `%PDF-1.4` magic bytes (not an HTML error page, the failure mode
  sandbox-prompt.md's PyPI/narrator incident warns about):

    https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Novice.pdf
    https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Intermediate.pdf
    https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Advanced.pdf
    https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Superior-Distinguished.pdf
    https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Benchmarks-Indicators-11x17_2026-02-10-011907_btgx.pdf

  Text was extracted with `pypdf` (`uv run --with pypdf python3 ...`) and
  read directly -- no summarizer in the loop. Document title (from the PDF's
  own first page): "NCSSFL-ACTFL Can-Do Statements", (c) 2026, a joint
  publication of ACTFL (American Council on the Teaching of Foreign
  Languages) and NCSSFL (National Council of State Supervisors for
  Languages). Usage terms printed on every page: "FREE FOR EDUCATIONAL AND
  NON-PROFIT USE ONLY. COMMERCIAL USE OR SALE IS PROHIBITED." -- recorded
  verbatim in SOURCE below rather than assumed to be CC-licensed like the
  Learning Commons feed math/reading/writing use.

NODE GRANULARITY AND CONTENT -- one node per ACTFL proficiency sublevel
(Novice Low/Mid/High, Intermediate Low/Mid/High, Advanced Low/Mid/High,
Superior, Distinguished -- 11 sublevels, matching the bead's "~10"), all
drawn from the *same* communication mode and function so the chain reads as
one coherent ladder rather than stitched-together unrelated skills:
Interpersonal Communication, function "How can I exchange information and
ideas in conversations?" -- the first function listed under Interpersonal
Communication in every one of the four level-specific PDFs. Each node's
`facts["performance_indicator"]` is that sublevel's real, quoted "I can..."
statement for that exact function (Novice/Intermediate/Advanced sublevels
each get their own distinct statement; Superior and Distinguished are not
further divided into sublevels in the source, so each gets one). Each node
also carries `facts["proficiency_benchmark"]`, the broader paragraph the
source prints once per major level (shared across that level's sublevels) --
kept as a separate field so a node's headline claim (benchmark) and its
concrete evidence (performance indicator) aren't conflated into one string.

EDGE PROVENANCE -- ordinal, and the source states the ordering claim
explicitly rather than leaving it to be inferred from table position (unlike
va_math_sol_graph.py and va_reading_sol_graph.py's grade-chain, which VDOE
never states as a claim and this repo's own docs flag as an *inference*):
the Benchmarks-Indicators overview PDF states outright, "Can-Do Statements
describe what learners can independently do at each sublevel and help pave
the way to higher levels... Each sublevel includes the abilities of the
prior sublevels." That sentence is exactly PrerequisiteEdge's "src must be
established before dst" semantics, applied by the source to its own eleven
sublevels in the order it defines them. So the chain here is a straight line,
Novice Low -> ... -> Distinguished, one edge per consecutive pair -- no
skip-edges, no NON_EDGES list the way dummit_foote_graph.py needs one,
because there is no branching structure or plausible-but-wrong shortcut edge
to guard against in a strictly ordinal, source-asserted sequence.

TEACH-8XW.49 -- Interpretive, Presentational, and Intercultural Communication
node sets added (this module originally shipped with only Interpersonal,
disclosed as a deliberate first-pass scope choice in
sandbox-handoffs/teach-cr8.md):

  PROVENANCE -- same five PDFs re-fetched live this session (2026-09-11,
  same URLs as above, same `%PDF-1.4` magic-byte check, same `pypdf`
  extraction method, no summarizer in the loop). Every new
  `performance_indicator`/`proficiency_benchmark`/`investigation_*`/
  `interaction_*` string below, plus the two new SOURCE entries
  (`other_modes_and_functions`, `independent_modes_quote`), was checked
  programmatically against the corresponding extracted PDF text: lowercased,
  ligature-normalized (pypdf renders "fl"/"fi"/"ff" ligature glyphs as a
  single character, sometimes followed by a stray space from kerning -- e.g.
  "reﬂ  ect" for "reflect" -- so the check strips whitespace immediately
  after a ligature substitution before collapsing the rest), and
  de-hyphenated across line-wraps (pypdf preserves the source PDF's
  line-wrap hyphens literally, e.g. "listen-\ning" for "listening" -- a
  layout artifact of justified text, not a real hyphen, so a bare `-\n` is
  removed before collapsing whitespace), then required to be an exact
  substring of the same-processed source text. The final run, against the
  actual data as loaded from this module (not a separately-retyped copy),
  reported 81 checks / "ALL MATCH" (76 node facts across the three new
  loaders, plus 5 SOURCE-dict quote fragments including the two composite
  Intercultural prompt strings, checked as their individual quoted
  fragments). The check script itself was ephemeral (matching teach-cr8's
  own method) and is not part of this repo.

  DESIGN CHOICE -- parallel node sets, each at the granularity the source
  actually provides for that mode, not additional facts bolted onto the
  existing 11 Interpersonal nodes. Two reasons:

    1. Interpretive and Presentational Communication *are* broken into the
       same 11 sublevels (Novice Low/Mid/High ... Distinguished) as
       Interpersonal in the source -- so those two get their own 11-node
       ordinal chains, `actfl-can-do:interpretive:<sublevel>` and
       `actfl-can-do:presentational:<sublevel>`, mirroring Interpersonal's
       shape exactly.
    2. Intercultural Communication is NOT broken into sublevels anywhere in
       the source: every one of the four level PDFs presents Intercultural
       Can-Do Statements once per *major* level only (Novice, Intermediate,
       Advanced, Superior, Distinguished -- 5, not 11), each with two
       dimensions, Investigation and Interaction, rather than the
       function-based statements the other three modes use. Bolting a
       fabricated Low/Mid/High split onto Intercultural nodes, or forcing
       its two-dimension shape into the single `performance_indicator`
       field the other modes use, would assert structure the source does
       not contain -- exactly what sandbox-prompt.md's "a number is only
       allowed to exist in a document if the code produces it" rule (applied
       here to graph structure, not a number) exists to block. So
       Intercultural gets its own 5-node chain,
       `actfl-can-do:intercultural:<major-level>`, with `investigation_*`
       and `interaction_*` fact fields instead of `performance_indicator`.

  Each of the four modes is returned by its own loader
  (`load_actfl_can_do_graph` for Interpersonal, unchanged;
  `load_actfl_interpretive_graph`, `load_actfl_presentational_graph`,
  `load_actfl_intercultural_graph` new) rather than one graph merging all
  four. There are no edges between modes: the source states outright that
  the modes are independent axes of the same learner, not a dependency
  chain into each other -- "Learners may be at different levels for
  different modes (Interpretive, Interpersonal, Presentational) or skills
  (reading, listening, writing, speaking, viewing, signing)" (Can-Do-
  Novice.pdf p.5, quoted in full in SOURCE["independent_modes_quote"]).
  Inventing an edge from, say, `interpretive:novice-low` into
  `interpersonal:novice-low` would assert an ordering claim the source
  explicitly denies. `test_no_node_id_collisions_across_the_four_mode_graphs`
  checks the four graphs stay disjoint. A consumer that wants "the whole
  domain" combines the four loaders' output itself; nothing here merges
  them.
"""
from __future__ import annotations

from teach.concept_graph import ConceptGraph, ConceptNode, PrerequisiteEdge

DOMAIN = "foreign-language"

SOURCE = {
    "title": "NCSSFL-ACTFL Can-Do Statements",
    "year": "2026",
    "publisher": (
        "American Council on the Teaching of Foreign Languages (ACTFL) and "
        "the National Council of State Supervisors for Languages (NCSSFL)"
    ),
    "usage_terms": (
        "FREE FOR EDUCATIONAL AND NON-PROFIT USE ONLY. COMMERCIAL USE OR "
        "SALE IS PROHIBITED."
    ),
    "listing_page": "https://www.actfl.org/educator-resources/ncssfl-actfl-can-do-statements",
    "pdfs_fetched": (
        "https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Novice.pdf",
        "https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Intermediate.pdf",
        "https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Advanced.pdf",
        "https://www.actfl.org/uploads/files/general/Resources-Publications/Can-Do-Superior-Distinguished.pdf",
        "https://www.actfl.org/uploads/files/general/Resources-Publications/"
        "Can-Do-Benchmarks-Indicators-11x17_2026-02-10-011907_btgx.pdf",
    ),
    "retrieved": "2026-09-11",
    "mode_and_function": (
        "Interpersonal Communication -- "
        '"How can I exchange information and ideas in conversations?"'
    ),
    "ordering_quote": (
        "Can-Do Statements describe what learners can independently do at "
        "each sublevel and help pave the way to higher levels... Each "
        "sublevel includes the abilities of the prior sublevels."
    ),
    # teach-8xw.49: the three modes added after the first pass, and which
    # function/prompt each one's node set was drawn from -- same convention
    # as mode_and_function above (first function listed under that mode in
    # every level PDF), except Intercultural, which has no "functions" in
    # the source, only two constant dimension prompts.
    "other_modes_and_functions": {
        "Interpretive Communication": (
            '"What can I understand, interpret, or analyze in authentic '
            'informational texts and media?"'
        ),
        "Presentational Communication": (
            '"How can I present information to inform and explain?"'
        ),
        "Intercultural Communication": (
            'Investigation -- "How does my investigation of products and '
            'practices help me understand perspectives?"; Interaction -- '
            '"How can I use my language and behavior to interact across '
            'cultures and communities?"'
        ),
    },
    "independent_modes_quote": (
        "Learners may be at different levels for different modes "
        "(Interpretive, Interpersonal, Presentational) or skills (reading, "
        "listening, writing, speaking, viewing, signing)."
    ),
}

# (sublevel_id_suffix, label, major_level, proficiency_benchmark, performance_indicator)
_SUBLEVELS = (
    (
        "novice-low", "Novice Low", "Novice",
        "I can participate in spontaneous spoken, written, or signed "
        "conversations on both very familiar and everyday topics, using "
        "words, phrases, simple sentences, and questions.",
        "I can provide information by answering a few simple questions on "
        "very familiar topics, using practiced or memorized words and "
        "phrases with the help of gestures, facial expressions, or visuals.",
    ),
    (
        "novice-mid", "Novice Mid", "Novice",
        "I can participate in spontaneous spoken, written, or signed "
        "conversations on both very familiar and everyday topics, using "
        "words, phrases, simple sentences, and questions.",
        "I can request and provide information by asking and answering "
        "simple questions on both very familiar and everyday topics, using "
        "a mix of practiced or memorized words, phrases, and simple "
        "sentences.",
    ),
    (
        "novice-high", "Novice High", "Novice",
        "I can participate in spontaneous spoken, written, or signed "
        "conversations on both very familiar and everyday topics, using "
        "words, phrases, simple sentences, and questions.",
        "I can request and provide information by asking and answering "
        "practiced and some original questions on familiar and everyday "
        "topics, using simple sentences most of the time.",
    ),
    (
        "intermediate-low", "Intermediate Low", "Intermediate",
        "I can interact in spontaneous spoken, written, or signed "
        "conversations on familiar topics, creating sentences and series "
        "of sentences to ask and answer a variety of questions.",
        "I can exchange information on familiar topics and topics of "
        "interest, creating simple sentences and appropriate follow-up "
        "questions.",
    ),
    (
        "intermediate-mid", "Intermediate Mid", "Intermediate",
        "I can interact in spontaneous spoken, written, or signed "
        "conversations on familiar topics, creating sentences and series "
        "of sentences to ask and answer a variety of questions.",
        "I can exchange information on familiar topics and some researched "
        "topics, creating sentences and some series of sentences to ask "
        "and answer a variety of follow-up questions.",
    ),
    (
        "intermediate-high", "Intermediate High", "Intermediate",
        "I can interact in spontaneous spoken, written, or signed "
        "conversations on familiar topics, creating sentences and series "
        "of sentences to ask and answer a variety of questions.",
        "I can exchange information, often across various time frames, on "
        "a variety of familiar and researched topics, creating series of "
        "sentences to ask and answer a variety of questions.",
    ),
    (
        "advanced-low", "Advanced Low", "Advanced",
        "I can maintain spontaneous spoken, written, or signed "
        "conversations and discussions across various time frames on "
        "familiar and concrete unfamiliar topics using series of connected "
        "sentences and probing questions.",
        "I can exchange and discuss information and ideas across various "
        "time frames on a variety of familiar and some unfamiliar topics, "
        "using series of connected sentences to ask and answer a variety "
        "of questions.",
    ),
    (
        "advanced-mid", "Advanced Mid", "Advanced",
        "I can maintain spontaneous spoken, written, or signed "
        "conversations and discussions across various time frames on "
        "familiar and concrete unfamiliar topics using series of connected "
        "sentences and probing questions.",
        "I can maintain discussions across time frames on a wide variety "
        "of familiar and unfamiliar topics, using probing questions and "
        "detailed responses.",
    ),
    (
        "advanced-high", "Advanced High", "Advanced",
        "I can maintain spontaneous spoken, written, or signed "
        "conversations and discussions across various time frames on "
        "familiar and concrete unfamiliar topics using series of connected "
        "sentences and probing questions.",
        "I can discuss and debate on a variety of complex concrete topics, "
        "often addressing hypothetical or abstract issues, using probing "
        "questions and explanations.",
    ),
    (
        "superior", "Superior", "Superior",
        "I can engage in extended spoken, written, or signed discussions "
        "and debates on concrete and abstract issues and ideas and some "
        "areas of specialized expertise, using complex discourse with "
        "supporting arguments and exploring hypotheses.",
        "I can discuss and debate at length on a variety of hypothetical "
        "or abstract issues, including general social interests and some "
        "areas of personal and professional expertise, using complex "
        "discourse with supporting arguments and exploring hypotheses.",
    ),
    (
        "distinguished", "Distinguished", "Distinguished",
        "I can engage in conceptually and linguistically complex spoken, "
        "written, or signed discussions and debates on a wide range of "
        "global issues and abstract concepts, using complex discourse and "
        "adapting to the cultural context of the conversation.",
        "I can discuss and debate at length on global issues and abstract "
        "concepts, using complex discourse and adapting language in "
        "culturally nuanced ways to the context of the conversation.",
    ),
)

SUBLEVEL_ORDER = tuple(f"actfl-can-do:{suffix}" for suffix, *_ in _SUBLEVELS)


def load_actfl_can_do_graph() -> ConceptGraph:
    """The 11-sublevel ordinal Can-Do chain as a validated ConceptGraph.
    Raises GraphError if the sublevel table above were edited into an
    inconsistent state."""
    nodes = tuple(
        ConceptNode(
            id=f"actfl-can-do:{suffix}",
            domain=DOMAIN,
            label=label,
            standard_ref=f"NCSSFL-ACTFL Can-Do Statements (2026), {label} -- "
                          "Interpersonal Communication",
            facts={
                "major_level": major_level,
                "sublevel": label,
                "mode": "Interpersonal Communication",
                "function_prompt": "How can I exchange information and ideas in conversations?",
                "proficiency_benchmark": benchmark,
                "performance_indicator": indicator,
            },
        )
        for suffix, label, major_level, benchmark, indicator in _SUBLEVELS
    )

    edges = tuple(
        PrerequisiteEdge(src=earlier, dst=later)
        for earlier, later in zip(SUBLEVEL_ORDER, SUBLEVEL_ORDER[1:])
    )

    graph = ConceptGraph(nodes=nodes, edges=edges)
    graph.validate()
    return graph


# teach-8xw.49 -- Interpretive Communication, same 11-sublevel granularity as
# Interpersonal above. First function listed under Interpretive Communication
# in every level PDF: "What can I understand, interpret, or analyze in
# authentic informational texts and media?"
# (sublevel_id_suffix, label, major_level, proficiency_benchmark, performance_indicator)
_INTERPRETIVE_SUBLEVELS = (
    (
        "novice-low", "Novice Low", "Novice",
        "I can identify the general topic and some basic information in "
        "both very familiar and everyday contexts from words, phrases, and "
        "simple sentences in texts that are spoken, written, or signed.",
        "I can identify memorized or familiar words in short, "
        "straightforward informational texts and media that are supported "
        "by gestures, facial expressions, or visuals.",
    ),
    (
        "novice-mid", "Novice Mid", "Novice",
        "I can identify the general topic and some basic information in "
        "both very familiar and everyday contexts from words, phrases, and "
        "simple sentences in texts that are spoken, written, or signed.",
        "I can identify some basic facts from memorized or familiar words "
        "and phrases in short, straightforward informational texts and "
        "media that are supported by gestures, facial expressions, or "
        "visuals.",
    ),
    (
        "novice-high", "Novice High", "Novice",
        "I can identify the general topic and some basic information in "
        "both very familiar and everyday contexts from words, phrases, and "
        "simple sentences in texts that are spoken, written, or signed.",
        "I can identify the topic and some isolated facts from simple "
        "sentences in short, straightforward informational texts and "
        "media.",
    ),
    (
        "intermediate-low", "Intermediate Low", "Intermediate",
        "I can understand the main idea and some related pieces of "
        "information on familiar topics from sentences and series of "
        "connected sentences in texts that are spoken, written, or signed.",
        "I can identify the topic and related information from simple "
        "sentences in descriptive informational texts and media.",
    ),
    (
        "intermediate-mid", "Intermediate Mid", "Intermediate",
        "I can understand the main idea and some related pieces of "
        "information on familiar topics from sentences and series of "
        "connected sentences in texts that are spoken, written, or signed.",
        "I can understand the main idea and key information from connected "
        "sentences in descriptive informational texts and media.",
    ),
    (
        "intermediate-high", "Intermediate High", "Intermediate",
        "I can understand the main idea and some related pieces of "
        "information on familiar topics from sentences and series of "
        "connected sentences in texts that are spoken, written, or signed.",
        "I can follow the main message in various time frames, from "
        "series of sentences and paragraphs in informational texts and "
        "media involving familiar and some concrete unfamiliar topics or "
        "genres.",
    ),
    (
        "advanced-low", "Advanced Low", "Advanced",
        "I can understand the main message, the author's purpose, and "
        "supporting details on a wide variety of familiar and general "
        "interest topics in longer texts that are spoken, written, or "
        "signed.",
        "I can identify the underlying message and some supporting "
        "details across various time frames, from multiple paragraphs in "
        "informational texts and media involving familiar and some "
        "concrete unfamiliar topics or genres.",
    ),
    (
        "advanced-mid", "Advanced Mid", "Advanced",
        "I can understand the main message, the author's purpose, and "
        "supporting details on a wide variety of familiar and general "
        "interest topics in longer texts that are spoken, written, or "
        "signed.",
        "I can understand the underlying message and most supporting "
        "details across time frames, from multiple paragraphs in "
        "informational texts and media involving familiar and some "
        "unfamiliar topics or genres.",
    ),
    (
        "advanced-high", "Advanced High", "Advanced",
        "I can understand the main message, the author's purpose, and "
        "supporting details on a wide variety of familiar and general "
        "interest topics in longer texts that are spoken, written, or "
        "signed.",
        "I can follow the flow of ideas and infer meaning from multiple "
        "paragraphs in informational texts and media involving a variety "
        "of unfamiliar, abstract topics or genres, and different "
        "viewpoints.",
    ),
    (
        "superior", "Superior", "Superior",
        "I can interpret and infer meaning on a range of unfamiliar, "
        "abstract, and specialized issues or themes in academic, "
        "technical, and professional texts that are spoken, written, or "
        "signed",
        "I can follow the flow of ideas and infer meaning from complex "
        "language in extended informational texts and media involving "
        "unfamiliar and abstract professional, technical, and academic "
        "content",
    ),
    (
        "distinguished", "Distinguished", "Distinguished",
        "I can interpret and infer meaning on a wide range of global "
        "issues or themes and highly abstract concepts, with deeply "
        "embedded cultural references, colloquialisms, and language "
        "varieties from dense, structurally sophisticated texts that are "
        "spoken, written, or signed",
        "I can easily understand sophisticated language, regardless of "
        "the cultural context or complexity, in extended informational "
        "texts and media in almost any genre and almost any professional, "
        "technical, and academic content",
    ),
)

INTERPRETIVE_SUBLEVEL_ORDER = tuple(
    f"actfl-can-do:interpretive:{suffix}" for suffix, *_ in _INTERPRETIVE_SUBLEVELS
)


def load_actfl_interpretive_graph() -> ConceptGraph:
    """The 11-sublevel ordinal Interpretive Communication chain, parallel to
    load_actfl_can_do_graph()'s Interpersonal chain but a separate graph --
    see the module docstring's teach-8xw.49 section for why the four modes
    are not merged into one graph."""
    nodes = tuple(
        ConceptNode(
            id=f"actfl-can-do:interpretive:{suffix}",
            domain=DOMAIN,
            label=label,
            standard_ref=f"NCSSFL-ACTFL Can-Do Statements (2026), {label} -- "
                          "Interpretive Communication",
            facts={
                "major_level": major_level,
                "sublevel": label,
                "mode": "Interpretive Communication",
                "function_prompt": "What can I understand, interpret, or "
                                    "analyze in authentic informational "
                                    "texts and media?",
                "proficiency_benchmark": benchmark,
                "performance_indicator": indicator,
            },
        )
        for suffix, label, major_level, benchmark, indicator in _INTERPRETIVE_SUBLEVELS
    )

    edges = tuple(
        PrerequisiteEdge(src=earlier, dst=later)
        for earlier, later in zip(INTERPRETIVE_SUBLEVEL_ORDER, INTERPRETIVE_SUBLEVEL_ORDER[1:])
    )

    graph = ConceptGraph(nodes=nodes, edges=edges)
    graph.validate()
    return graph


# teach-8xw.49 -- Presentational Communication, same 11-sublevel granularity.
# First function listed under Presentational Communication in every level
# PDF: "How can I present information to inform and explain?"
# (sublevel_id_suffix, label, major_level, proficiency_benchmark, performance_indicator)
_PRESENTATIONAL_SUBLEVELS = (
    (
        "novice-low", "Novice Low", "Novice",
        "I can share information on both very familiar and everyday "
        "topics, using a variety of practiced or memorized words, "
        "phrases, and simple sentences through spoken, written, or signed "
        "language.",
        "I can name very familiar people, places and objects, using "
        "practiced or memorized words and phrases with the help of "
        "gestures, facial expressions, or visuals.",
    ),
    (
        "novice-mid", "Novice Mid", "Novice",
        "I can share information on both very familiar and everyday "
        "topics, using a variety of practiced or memorized words, "
        "phrases, and simple sentences through spoken, written, or signed "
        "language.",
        "I can share information on both very familiar and everyday "
        "topics, using a mix of practiced or memorized words, phrases, "
        "and simple sentences.",
    ),
    (
        "novice-high", "Novice High", "Novice",
        "I can share information on both very familiar and everyday "
        "topics, using a variety of practiced or memorized words, "
        "phrases, and simple sentences through spoken, written, or signed "
        "language.",
        "I can share information on both familiar and everyday topics, "
        "using simple sentences most of the time.",
    ),
    (
        "intermediate-low", "Intermediate Low", "Intermediate",
        "I can provide information and express my thoughts about familiar "
        "topics, creating sentences and series of connected sentences "
        "through spoken, written, or signed language.",
        "I can describe aspects of familiar topics and topics of "
        "interest, creating simple sentences.",
    ),
    (
        "intermediate-mid", "Intermediate Mid", "Intermediate",
        "I can provide information and express my thoughts about familiar "
        "topics, creating sentences and series of connected sentences "
        "through spoken, written, or signed language.",
        "I can explain aspects of familiar topics and some researched "
        "topics, creating sentences and strings of connected sentences.",
    ),
    (
        "intermediate-high", "Intermediate High", "Intermediate",
        "I can provide information and express my thoughts about familiar "
        "topics, creating sentences and series of connected sentences "
        "through spoken, written, or signed language.",
        "I can give detailed explanations, often across various time "
        "frames, on a variety of familiar and researched topics, creating "
        "short paragraphs.",
    ),
    (
        "advanced-low", "Advanced Low", "Advanced",
        "I can organize, express, and present information to an audience "
        "in a detailed way on concrete unfamiliar topics, using "
        "paragraphs across various time frames through spoken, written, "
        "or signed language.",
        "I can give detailed explanations across various time frames on a "
        "variety of familiar and some unfamiliar topics, using "
        "paragraphs.",
    ),
    (
        "advanced-mid", "Advanced Mid", "Advanced",
        "I can organize, express, and present information to an audience "
        "in a detailed way on concrete unfamiliar topics, using "
        "paragraphs across various time frames through spoken, written, "
        "or signed language.",
        "I can give detailed explanations across time frames on a wide "
        "variety of familiar and unfamiliar topics, using organized "
        "paragraphs.",
    ),
    (
        "advanced-high", "Advanced High", "Advanced",
        "I can organize, express, and present information to an audience "
        "in a detailed way on concrete unfamiliar topics, using "
        "paragraphs across various time frames through spoken, written, "
        "or signed language.",
        "I can give detailed explanations on a variety of complex, "
        "concrete topics and some hypothetical or abstract issues, using "
        "organized paragraphs.",
    ),
    (
        "superior", "Superior", "Superior",
        "I can present to a wide variety of audiences on hypothetical or "
        "abstract issues and ideas ranging from broad general interests "
        "to my areas of specialized expertise, producing extended "
        "discourse with precision of expression, using spoken, written, "
        "or signed language",
        "I can deliver clearly articulated, well-structured presentations "
        "to various audiences on a variety of hypothetical or abstract "
        "issues, including general social interests and some areas of "
        "personal and professional expertise, producing extended and "
        "precise discourse",
    ),
    (
        "distinguished", "Distinguished", "Distinguished",
        "I can present on a wide range of global issues and highly "
        "abstract concepts, producing conceptually and linguistically "
        "complex discourse and adapting to the cultural context of the "
        "audience using spoken, written, or signed language",
        "I can adapt my language to the characteristics of the audience "
        "and embed cultural perspectives while presenting on global "
        "issues and abstract concepts, using complex, culturally nuanced "
        "discourse with accuracy, efficiency, and effectiveness",
    ),
)

PRESENTATIONAL_SUBLEVEL_ORDER = tuple(
    f"actfl-can-do:presentational:{suffix}" for suffix, *_ in _PRESENTATIONAL_SUBLEVELS
)


def load_actfl_presentational_graph() -> ConceptGraph:
    """The 11-sublevel ordinal Presentational Communication chain, parallel
    to load_actfl_can_do_graph()'s Interpersonal chain but a separate
    graph."""
    nodes = tuple(
        ConceptNode(
            id=f"actfl-can-do:presentational:{suffix}",
            domain=DOMAIN,
            label=label,
            standard_ref=f"NCSSFL-ACTFL Can-Do Statements (2026), {label} -- "
                          "Presentational Communication",
            facts={
                "major_level": major_level,
                "sublevel": label,
                "mode": "Presentational Communication",
                "function_prompt": "How can I present information to "
                                    "inform and explain?",
                "proficiency_benchmark": benchmark,
                "performance_indicator": indicator,
            },
        )
        for suffix, label, major_level, benchmark, indicator in _PRESENTATIONAL_SUBLEVELS
    )

    edges = tuple(
        PrerequisiteEdge(src=earlier, dst=later)
        for earlier, later in zip(PRESENTATIONAL_SUBLEVEL_ORDER, PRESENTATIONAL_SUBLEVEL_ORDER[1:])
    )

    graph = ConceptGraph(nodes=nodes, edges=edges)
    graph.validate()
    return graph


# teach-8xw.49 -- Intercultural Communication. Unlike the three modes above,
# the source defines this only per MAJOR level (5, not 11) -- see the module
# docstring's teach-8xw.49 section. Two constant dimension prompts apply at
# every level rather than a per-sublevel function.
_INTERCULTURAL_INVESTIGATION_PROMPT = (
    "How does my investigation of products and practices help me "
    "understand perspectives?"
)
_INTERCULTURAL_INTERACTION_PROMPT = (
    "How can I use my language and behavior to interact across cultures "
    "and communities?"
)

# (level_id_suffix, label,
#  investigation_benchmark, investigation_indicator_products, investigation_indicator_practices,
#  interaction_benchmark, interaction_indicator_language, interaction_indicator_behavior)
_INTERCULTURAL_LEVELS = (
    (
        "novice", "Novice",
        "I can identify products and practices that help me understand "
        "perspectives from a variety of cultures and communities, "
        "including my own.",
        "I can identify some products to help me understand perspectives "
        "in familiar everyday contexts.",
        "I can identify some practices to help me understand perspectives "
        "in familiar everyday contexts.",
        "I can interact at a limited level in some familiar everyday "
        "contexts.",
        "I can communicate with others from a variety of cultures and "
        "communities, including my own, in familiar everyday situations, "
        "using memorized language and basic cultural awareness.",
        "I can use appropriate rehearsed behaviors and recognize some "
        "obviously inappropriate behaviors in familiar everyday "
        "situations.",
    ),
    (
        "intermediate", "Intermediate",
        "I can compare products and practices to understand perspectives "
        "from a variety of cultures and communities, including my own.",
        "I can compare products to understand perspectives related to "
        "familiar contexts and personal interests.",
        "I can compare practices to understand perspectives related to "
        "familiar contexts and personal interests.",
        "I can interact at a functional level in some familiar contexts.",
        "I can interact with others from a variety of cultures and "
        "communities, including my own, in familiar situations and "
        "demonstrate some understanding of cultural similarities and "
        "differences.",
        "I can recognize that significant differences in behaviors exist "
        "among cultures and use some culturally appropriate behaviors in "
        "familiar situations.",
    ),
    (
        "advanced", "Advanced",
        "I can explain how products and practices reflect perspectives "
        "from a variety of cultures and communities, including my own.",
        "I can explain how a variety of products are related to "
        "perspectives in familiar and some unfamiliar contexts.",
        "I can explain how a variety of practices are related to "
        "perspectives in familiar and some unfamiliar contexts.",
        "I can interact competently in familiar and some unfamiliar "
        "contexts.",
        "I can interact with others from a variety of cultures and "
        "communities, including my own, in familiar and some unfamiliar "
        "situations and apply my understanding of cultural similarities "
        "and differences.",
        "I can demonstrate awareness of subtle differences among cultural "
        "behaviors and integrate culturally appropriate behaviors in "
        "familiar and some unfamiliar situations.",
    ),
    (
        "superior", "Superior",
        "I can analyze products, practices, and perspectives from a "
        "variety of cultures and communities, including my own",
        "I can analyze how a wide range of concrete and abstract products "
        "are related to perspectives in various contexts",
        "I can analyze how a wide range of concrete and abstract "
        "practices are related to perspectives in various contexts",
        "I can interact in complex situations to ensure a shared "
        "understanding of culture",
        "I can suspend judgment, adapt my language and use a depth of "
        "cultural knowledge to interact with others from a variety of "
        "cultures and communities, including my own, in various "
        "situations",
        "I can adapt to cultural norms and etiquette, read nonverbal "
        "cues, and adjust my behavior in various situations",
    ),
    (
        "distinguished", "Distinguished",
        "I can objectively evaluate products, practices, and perspectives "
        "from a variety of cultures and communities, including my own",
        "I can evaluate how a wide range of concrete and abstract "
        "products reflect perspectives",
        "I can evaluate how a wide range of concrete and abstract "
        "practices reflect perspectives",
        "I can mediate and bridge cultural and pluricultural perspectives "
        "with ease",
        "I can engage with empathy and cultural nuance when interacting "
        "with others from a variety of cultures and communities, "
        "including my own, in almost any situation",
        "I can adjust my formal and informal styles of behavior, respond "
        "effectively to nonverbal cues, and mediate smoothly and "
        "respectfully in almost any situation",
    ),
)

INTERCULTURAL_LEVEL_ORDER = tuple(
    f"actfl-can-do:intercultural:{suffix}" for suffix, *_ in _INTERCULTURAL_LEVELS
)


def load_actfl_intercultural_graph() -> ConceptGraph:
    """The 5-major-level ordinal Intercultural Communication chain -- 5
    nodes, not 11, because the source itself never subdivides Intercultural
    Communication by sublevel (see the module docstring's teach-8xw.49
    section)."""
    nodes = tuple(
        ConceptNode(
            id=f"actfl-can-do:intercultural:{suffix}",
            domain=DOMAIN,
            label=label,
            standard_ref=f"NCSSFL-ACTFL Can-Do Statements (2026), {label} -- "
                          "Intercultural Communication",
            facts={
                "major_level": label,
                "mode": "Intercultural Communication",
                "investigation_prompt": _INTERCULTURAL_INVESTIGATION_PROMPT,
                "interaction_prompt": _INTERCULTURAL_INTERACTION_PROMPT,
                "investigation_benchmark": investigation_benchmark,
                "investigation_indicator_products": investigation_products,
                "investigation_indicator_practices": investigation_practices,
                "interaction_benchmark": interaction_benchmark,
                "interaction_indicator_language": interaction_language,
                "interaction_indicator_behavior": interaction_behavior,
            },
        )
        for (
            suffix, label,
            investigation_benchmark, investigation_products, investigation_practices,
            interaction_benchmark, interaction_language, interaction_behavior,
        ) in _INTERCULTURAL_LEVELS
    )

    edges = tuple(
        PrerequisiteEdge(src=earlier, dst=later)
        for earlier, later in zip(INTERCULTURAL_LEVEL_ORDER, INTERCULTURAL_LEVEL_ORDER[1:])
    )

    graph = ConceptGraph(nodes=nodes, edges=edges)
    graph.validate()
    return graph


def _self_check() -> None:
    graph = load_actfl_can_do_graph()
    assert len(graph.nodes) == 11, len(graph.nodes)
    assert len(graph.edges) == 10, len(graph.edges)

    order = graph.topological_order()
    assert order == SUBLEVEL_ORDER, order

    # Real content escalation, not just eleven labels in a row: the Novice
    # Low statement leans on gesture/visual support and memorized language;
    # Distinguished names none of that and adds culturally nuanced complex
    # discourse instead.
    novice_low = graph.by_id("actfl-can-do:novice-low").facts["performance_indicator"]
    distinguished = graph.by_id("actfl-can-do:distinguished").facts["performance_indicator"]
    assert "gestures" in novice_low
    assert "memorized" in novice_low
    assert "gestures" not in distinguished
    assert "culturally nuanced" in distinguished

    # No target language is asserted anywhere in the data -- see the DECISION
    # section. A later edit that quietly bolts on a language name would
    # violate the documented decision; this assertion is what makes that
    # violation fail loudly instead of silently.
    for node in graph.nodes:
        assert node.domain == "foreign-language"
        blob = " ".join(str(v) for v in node.facts.values()).lower()
        for language in ("spanish", "french", "japanese", "mandarin", "german"):
            assert language not in blob, (node.id, language)

    print(
        f"OK: {len(graph.nodes)} NCSSFL-ACTFL Can-Do proficiency sublevels "
        f"(Novice Low..Distinguished) load as a valid, strictly ordinal DAG "
        f"({len(graph.edges)} edges), sourced from ACTFL's real 2026 "
        "Can-Do Statements PDFs with no target language asserted."
    )


def _assert_no_target_language(graph: ConceptGraph) -> None:
    for node in graph.nodes:
        assert node.domain == "foreign-language"
        blob = " ".join(str(v) for v in node.facts.values()).lower()
        for language in ("spanish", "french", "japanese", "mandarin", "german"):
            assert language not in blob, (node.id, language)


def _self_check_interpretive() -> None:
    graph = load_actfl_interpretive_graph()
    assert len(graph.nodes) == 11, len(graph.nodes)
    assert len(graph.edges) == 10, len(graph.edges)

    order = graph.topological_order()
    assert order == INTERPRETIVE_SUBLEVEL_ORDER, order

    novice_low = graph.by_id("actfl-can-do:interpretive:novice-low").facts["performance_indicator"]
    distinguished = graph.by_id("actfl-can-do:interpretive:distinguished").facts["performance_indicator"]
    assert "gestures" in novice_low
    assert "memorized" in novice_low
    assert "gestures" not in distinguished
    assert "sophisticated" in distinguished

    _assert_no_target_language(graph)

    print(
        f"OK: {len(graph.nodes)} NCSSFL-ACTFL Interpretive Communication "
        f"sublevels load as a valid, strictly ordinal DAG "
        f"({len(graph.edges)} edges)."
    )


def _self_check_presentational() -> None:
    graph = load_actfl_presentational_graph()
    assert len(graph.nodes) == 11, len(graph.nodes)
    assert len(graph.edges) == 10, len(graph.edges)

    order = graph.topological_order()
    assert order == PRESENTATIONAL_SUBLEVEL_ORDER, order

    novice_low = graph.by_id("actfl-can-do:presentational:novice-low").facts["performance_indicator"]
    distinguished = graph.by_id("actfl-can-do:presentational:distinguished").facts["performance_indicator"]
    assert "gestures" in novice_low
    assert "memorized" in novice_low
    assert "culturally nuanced" in distinguished

    _assert_no_target_language(graph)

    print(
        f"OK: {len(graph.nodes)} NCSSFL-ACTFL Presentational Communication "
        f"sublevels load as a valid, strictly ordinal DAG "
        f"({len(graph.edges)} edges)."
    )


def _self_check_intercultural() -> None:
    graph = load_actfl_intercultural_graph()
    assert len(graph.nodes) == 5, len(graph.nodes)
    assert len(graph.edges) == 4, len(graph.edges)

    order = graph.topological_order()
    assert order == INTERCULTURAL_LEVEL_ORDER, order

    novice = graph.by_id("actfl-can-do:intercultural:novice")
    distinguished = graph.by_id("actfl-can-do:intercultural:distinguished")
    assert "limited level" in novice.facts["interaction_benchmark"]
    assert "familiar everyday" in novice.facts["investigation_indicator_products"]
    assert "objectively evaluate" in distinguished.facts["investigation_benchmark"]
    assert "mediate and bridge" in distinguished.facts["interaction_benchmark"]

    # Both dimension prompts are constant across levels -- confirm they are
    # actually identical strings, not five independently-transcribed copies
    # that happen to look similar.
    for node in graph.nodes:
        assert node.facts["investigation_prompt"] == _INTERCULTURAL_INVESTIGATION_PROMPT
        assert node.facts["interaction_prompt"] == _INTERCULTURAL_INTERACTION_PROMPT

    _assert_no_target_language(graph)

    print(
        f"OK: {len(graph.nodes)} NCSSFL-ACTFL Intercultural Communication "
        f"levels load as a valid, strictly ordinal DAG "
        f"({len(graph.edges)} edges) -- 5 major levels, not 11 sublevels, "
        "matching the source's own granularity."
    )


def _self_check_no_cross_mode_collisions() -> None:
    interpersonal = load_actfl_can_do_graph()
    interpretive = load_actfl_interpretive_graph()
    presentational = load_actfl_presentational_graph()
    intercultural = load_actfl_intercultural_graph()

    all_ids = [
        node.id
        for graph in (interpersonal, interpretive, presentational, intercultural)
        for node in graph.nodes
    ]
    assert len(all_ids) == len(set(all_ids)), "cross-mode node id collision"

    print(
        f"OK: all {len(all_ids)} node ids across the four Can-Do mode "
        "graphs (Interpersonal, Interpretive, Presentational, "
        "Intercultural) are unique -- the graphs are genuinely parallel, "
        "not accidentally overlapping."
    )


if __name__ == "__main__":
    _self_check()
    _self_check_interpretive()
    _self_check_presentational()
    _self_check_intercultural()
    _self_check_no_cross_mode_collisions()
