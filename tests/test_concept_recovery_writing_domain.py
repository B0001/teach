"""teach-8xw.42: floor-level cross-test of concept_recovery.py against the VA
Writing SOL K-12 ConceptGraph (teach/va_writing_sol_graph.py, teach-5aj).

Before this bead, `grep -rl concept_recovery tests/` returned exactly three
files -- test_concept_recovery.py (math), test_concept_recovery_non_math_
domain.py (reading, va_reading_sol_graph only), and
test_dummit_foote_graph.py -- and none of them imported
teach.va_writing_sol_graph. teach-5aj's own handoff said as much explicitly:
"Whether this graph's vocabulary is recoverable from real lesson text is
unmeasured." Unlike the reading domain (teach-8xw.29), writing had never even
had a self-authored smoke test.

This file mirrors test_concept_recovery_non_math_domain.py's pattern and
disclosure exactly: it is a FLOOR test, not a generalization measurement. All
lesson text below is hand-written by this session (same limit that file's own
docstring names), so per sandbox-prompt.md's "you cannot hold out examples
from yourself" this establishes that recovery MECHANICALLY WORKS against a
third real, curriculum-scale, non-math ConceptGraph with its own real
boilerplate density -- not that it generalizes to lesson text nobody in this
session imagined. A genuine generalization measurement (lesson text authored
by an agent with no repo access, per teach-8xw.33's precedent) is out of this
bead's scope and is filed separately.

Every fixture below was checked against the actual `score_candidates` output
before being written into an assertion (not guessed and then patched until
green) -- see the fixture comments for which real leaf-standard text each one
quotes and why the chosen grades separate or tie.
"""
from teach.concept_recovery import (
    build_vocabulary_index,
    recover_from_lesson_text,
    score_candidates,
)
from teach.va_writing_sol_graph import load_va_writing_sol_graph

WRITING_GRAPH = load_va_writing_sol_graph()

# Assumed-prior content quotes real 6.W.1.B/6.W.1.C leaf-standard text
# (including the source's own "welldefined" -- no hyphen -- which is a real
# transcription quirk of that leaf, not a typo introduced here; 7.W.1.C's
# leaf text does hyphenate "well-defined", so the two grades' fixtures
# deliberately use the source's own two different spellings). Taught content
# quotes real 7.W.1.A/7.W.1.B/7.W.1.C leaf-standard text verbatim. See
# teach/data/va_writing_sol_k12.json for the source strings.
CORRECT_RECOVERY_TEXT = (
    "tutor: Last year you already learned to write persuasively about "
    "topics or texts, including media messages, supporting welldefined "
    "claims with clear reasons and evidence that are logically grouped, "
    "and how to write expository texts that logically convey ideas using "
    "text structures such as description, comparison, or cause-effect to "
    "create cohesion.\n"
    "learner: Right, we worked on structuring persuasive paragraphs like "
    "that.\n"
    "tutor: Today we build on that: you'll write narratives to develop "
    "real or imagined experiences or to alter an existing text, using a "
    "variety of precise words and phrases and transitional words to "
    "develop the characters, convey sequence, and signal shifts from one "
    "timeframe or setting to another. You'll also write expository texts "
    "to examine a topic or concept that develops the focus with relevant "
    "facts, definitions, concrete details, or other information from "
    "multiple credible sources, using structures and patterns such as "
    "description, enumeration, classification, comparison, "
    "problem-solution, or cause-effect to clarify relationships among "
    "ideas, and you'll write persuasively supporting a well-defined point "
    "of view with appropriate claims, relevant evidence, and clear "
    "reasoning that are logically grouped."
)
CORRECT_RECOVERY_TAUGHT = "va-writing-sol:7.W"
CORRECT_RECOVERY_ASSUMED = ("va-writing-sol:6.W",)


def test_correct_recovery_against_real_writing_graph():
    """A lesson quoting real 7.W leaf-standard language, with real 6.W
    leaf-standard content signposted as already known, recovers both
    correctly against the actual sourced VA Writing SOL K-12 graph -- not a
    synthetic fixture. Checked (not assumed) that 7.W's raw score (45) beats
    the closest rival, 8.W (34), by a comfortable margin before this
    assertion was written."""
    result = recover_from_lesson_text(CORRECT_RECOVERY_TEXT, WRITING_GRAPH)
    assert result.taught_node_id == CORRECT_RECOVERY_TAUGHT
    assert result.assumed_prerequisite_ids == CORRECT_RECOVERY_ASSUMED
    assert result.unsignposted_prerequisite_ids == ()
    assert result.abstain_reason is None


def test_abstains_on_content_outside_writing_sol_vocabulary():
    """Lesson text about screenwriting craft (inciting incidents, midpoint
    reversals, hero's-journey beats) that this K-12 expository/narrative/
    persuasive-writing graph has no vocabulary for must abstain, not guess a
    K-12 node -- the same disclosed-gap abstention teach-8xw.15 established
    for math and teach-8xw.29 established for reading, now checked for
    writing. The best-scoring candidate shares exactly one word ("draft")
    with the text, below `_MIN_MATCH_WORDS` (3)."""
    text = (
        "tutor: Before Bond signs off on this screenplay draft, walk me "
        "through the inciting incident, the midpoint reversal, and how the "
        "hero's journey beats land in act three -- and make sure the "
        "antagonist's arc mirrors his."
    )
    result = recover_from_lesson_text(text, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert result.assumed_prerequisite_ids == ()


def test_unsignposted_prerequisite_detected_without_signal_phrase():
    """Same lesson content as the correct-recovery fixture, but with the
    'Last year you already learned...' signal stripped: the text still
    leans on enough of 6.W's real distinctive vocabulary to count as
    unsignposted use, per teach-20c's three-way split -- checked against the
    real graph."""
    text = (
        "tutor: Writing persuasively about topics or texts, including "
        "media messages, means supporting welldefined claims with clear "
        "reasons and evidence that are logically grouped, and expository "
        "texts logically convey ideas using text structures such as "
        "description, comparison, or cause-effect to create cohesion. "
        "Today you'll write narratives to develop real or imagined "
        "experiences or to alter an existing text, using a variety of "
        "precise words and phrases and transitional words to develop the "
        "characters, convey sequence, and signal shifts from one "
        "timeframe or setting to another. You'll also write expository "
        "texts to examine a topic or concept that develops the focus with "
        "relevant facts, definitions, concrete details, or other "
        "information from multiple credible sources, using structures and "
        "patterns such as description, enumeration, classification, "
        "comparison, problem-solution, or cause-effect to clarify "
        "relationships among ideas, and you'll write persuasively "
        "supporting a well-defined point of view with appropriate claims, "
        "relevant evidence, and clear reasoning that are logically "
        "grouped."
    )
    result = recover_from_lesson_text(text, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:7.W"
    assert result.assumed_prerequisite_ids == ()
    assert result.unsignposted_prerequisite_ids == ("va-writing-sol:6.W",)


def test_adjacent_grades_real_vocabulary_overlap_forces_honest_abstention():
    """VA Writing SOL's 6th/7th/8th grade strands genuinely share most of
    their raw distinctive vocabulary once boilerplate is filtered out --
    "structure", "description", "comparison", "concept", "persuasively",
    "transition", "alter", "paragraph", "multi", "variety", "existing",
    "among" all survive the document-frequency filter in all three grades
    (real overlap, not invented). Text drawing on only those 13 shared
    words -- deliberately avoiding any grade's OWN distinctive vocabulary
    (7th's "shifts"/"focus", 8th's "quotations"/"clarify", 6th's "media"/
    "cohesion") -- ties all three candidates at an identical raw score, so
    a human reader given only this generic text genuinely could not tell
    which grade it was either."""
    text = (
        "tutor: A strong multi-paragraph piece comes down to structure: "
        "use description and comparison to develop your concept, add a "
        "variety of structures, and alter the transition among paragraphs "
        "so you write persuasively throughout, even in an existing "
        "paragraph you're revising."
    )
    index = build_vocabulary_index(WRITING_GRAPH)
    candidates = score_candidates(text, index)
    top_three_ids = {c.node_id for c in candidates[:3]}
    top_three_scores = {c.score for c in candidates[:3]}
    assert top_three_ids == {
        "va-writing-sol:6.W",
        "va-writing-sol:7.W",
        "va-writing-sol:8.W",
    }, candidates[:5]
    assert len(top_three_scores) == 1, (
        "expected an exact three-way tie",
        candidates[:5],
    )

    result = recover_from_lesson_text(text, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()


def test_boilerplate_document_frequency_filter_survives_real_data():
    """The design memory's calibration concern (point 2 of `bd memories
    teach-8xw-10-concept-recovery-design`): a real domain's near-identical
    grade-to-grade phrasing must not tie every grade of a strand together.
    Among the 13 grade groupings' leaf-standard text, 'writing' appears in
    13, 'texts' in 11, and 'topic' in 9 -- all comfortably above
    `_MAX_DOCUMENT_FREQ` (4) -- so all three must be filtered out of every
    node's distinctive vocabulary, while each grade's genuinely distinctive
    content words survive."""
    index = build_vocabulary_index(WRITING_GRAPH)
    k_w_words = index.node_words("va-writing-sol:K.W")
    twelfth_w_words = index.node_words("va-writing-sol:12.W")

    for boilerplate_word in ("writing", "texts", "topic"):
        assert boilerplate_word not in k_w_words
        assert boilerplate_word not in twelfth_w_words

    # K.W's own distinctive vocabulary survives filtering (from "Use a
    # combination of drawing, dictating, and writing to compose narrative
    # stories..." and "...use prewriting activities...").
    assert "drawing" in k_w_words
    assert "prewriting" in k_w_words
    # 12.W's own distinctive vocabulary survives filtering (from "Write and
    # revise to a standard acceptable both in the workplace and in
    # postsecondary education."), and is not shared with kindergarten's.
    assert "postsecondary" in twelfth_w_words
    assert "workplace" in twelfth_w_words
    assert "postsecondary" not in k_w_words
