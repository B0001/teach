"""teach-8xw.29: exercises concept_recovery.py against a REAL, curriculum-scale
non-math ConceptGraph (VA Reading SOL K-8, teach/va_reading_sol_graph.py) --
not a synthetic fixture built to make the checker look good.

Before this bead, every data-backed ConceptGraph exercised anywhere in this
repo's tests (teach/va_math_sol_graph.py, teach/dummit_foote_graph.py) was
math. concept_recovery.py's module docstring and the design memory (`bd
memories teach-8xw-10-concept-recovery-design`) both claim domain-agnostic
genericity, but that claim had never been run against a real non-math
curriculum with real boilerplate structure -- only a 2-node synthetic
fixture (test_concept_recovery.py's
test_domain_agnostic_vocabulary_extraction_ignores_key_names), which only
proves the code doesn't hardcode a key name, not that recovery actually
works at curriculum scale.

The lesson texts below are still hand-written by this session, same as
every fixture in test_concept_recovery.py -- that is a real limit on what
this file proves (per sandbox-prompt.md, "you cannot hold out examples from
yourself" applies most sharply to a *generalization* claim, and hand-written
lesson text is not a held-out generalization set). What this file adds that
the prior 2-node fixture did not: the GRAPH itself is real, sourced,
curriculum-scale data with the actual boilerplate density and per-grade
vocabulary overlap a real domain has (VA Reading SOL's 3rd/4th/5th grade RI
strands share the bulk of their raw vocabulary -- "cause", "effect",
"comparison", "problem", "solution", "sequence", "search", "tools" all
appear in multiple adjacent grades' leaf standards), so the document-
frequency boilerplate filter and the margin/coverage abstention gates are
exercised under real, not invented, ambiguity pressure. See the module
docstring's design-memory point 2 about why this calibration matters.
"""
from teach.concept_recovery import (
    build_vocabulary_index,
    recover_from_lesson_text,
    score_candidates,
)
from teach.va_reading_sol_graph import load_va_reading_sol_graph

READING_GRAPH = load_va_reading_sol_graph()

# Drawn from the real, sourced leaf standards: 3.RI.1.C + 3.RI.2.A (assumed
# prerequisite) and 4.RI.1.C + 4.RI.2.A (taught) -- see
# teach/data/va_reading_sol_k8.json. Phrasing quotes the actual standard
# text, the same convention teach/concept_recovery.py's own
# CORRECT_RECOVERY_TEXT uses for VA Math SOL.
CORRECT_RECOVERY_TEXT = (
    "tutor: Last year you already learned to identify and explain how an "
    "author uses reasons and evidence to support specific points in texts, "
    "and how informational texts differ in their organizational patterns "
    "-- cause and effect, comparison and contrast, problem and solution, "
    "description, and sequence.\n"
    "learner: Right, we looked at how authors organize things.\n"
    "tutor: Today we build on that: you'll explain how authors select an "
    "organizational pattern and use transitional words and phrases to "
    "support their purpose, and you'll distinguish between fact and "
    "opinion, explaining how an author uses reasons and evidence to "
    "support opinions within texts."
)
CORRECT_RECOVERY_TAUGHT = "va-reading-sol:4.RI"
CORRECT_RECOVERY_ASSUMED = ("va-reading-sol:3.RI",)


def test_correct_recovery_against_real_reading_graph():
    """A lesson quoting real 4.RI leaf-standard language, with a real 3.RI
    leaf-standard signposted as already known, recovers both correctly
    against the actual sourced VA Reading SOL K-8 graph -- not a synthetic
    2-node fixture."""
    result = recover_from_lesson_text(CORRECT_RECOVERY_TEXT, READING_GRAPH)
    assert result.taught_node_id == CORRECT_RECOVERY_TAUGHT
    assert result.assumed_prerequisite_ids == CORRECT_RECOVERY_ASSUMED
    assert result.unsignposted_prerequisite_ids == ()
    assert result.abstain_reason is None


def test_abstains_on_content_outside_reading_sol_vocabulary():
    """Lesson text about literary-theory content (unreliable narrators,
    focalization, metafiction) that this K-8 graph's vocabulary has nothing
    on must abstain, not guess a K-8 node -- the same disclosed-gap
    abstention teach-8xw.15 established for math (group theory vs. K-8 VA
    Math SOL), now checked for the reading domain."""
    text = (
        "tutor: M needs a full deconstruction of this dossier's unreliable "
        "narrator before she'll trust a word of it -- walk me through the "
        "focalization shifts and the metafictional frame first."
    )
    result = recover_from_lesson_text(text, READING_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert result.assumed_prerequisite_ids == ()


def test_unsignposted_prerequisite_detected_without_signal_phrase():
    """Same lesson content as the correct-recovery fixture, but with the
    'Last year you already learned...' signal stripped: the text still
    leans on enough of 3.RI's real distinctive vocabulary to count as
    unsignposted use, per teach-20c's three-way split -- checked against
    the real graph, not a synthetic one."""
    text = (
        "tutor: Informational texts differ in their organizational "
        "patterns -- cause and effect, comparison and contrast, problem "
        "and solution, description, and sequence. Today you'll explain "
        "how authors select an organizational pattern and use "
        "transitional words and phrases to support their purpose, and "
        "you'll distinguish between fact and opinion, explaining how an "
        "author uses reasons and evidence to support opinions within "
        "texts."
    )
    result = recover_from_lesson_text(text, READING_GRAPH)
    assert result.taught_node_id == "va-reading-sol:4.RI"
    assert result.assumed_prerequisite_ids == ()
    assert result.unsignposted_prerequisite_ids == ("va-reading-sol:3.RI",)


def test_adjacent_grades_real_vocabulary_overlap_forces_honest_abstention():
    """VA Reading SOL's 3rd/4th/5th grade RI strands genuinely share most
    of their raw vocabulary (real boilerplate pressure, not invented) --
    text drawing on only the words common to grades 3-5 (not 4th grade's
    OWN distinctive words like 'distinguish'/'fact'/'opinion') must abstain
    as ambiguous rather than guess one grade, because a human reader given
    only this generic text genuinely could not tell which grade it was
    either."""
    text = (
        "tutor: Texts have organizational patterns -- cause and effect, "
        "comparison and contrast, problem and solution, description, and "
        "sequence -- and readers use search tools to locate information "
        "efficiently from multiple sources."
    )
    index = build_vocabulary_index(READING_GRAPH)
    candidates = score_candidates(text, index)
    top_three_ids = {c.node_id for c in candidates[:3]}
    assert top_three_ids == {
        "va-reading-sol:3.RI",
        "va-reading-sol:4.RI",
        "va-reading-sol:5.RI",
    }, candidates[:5]

    result = recover_from_lesson_text(text, READING_GRAPH)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()


def test_boilerplate_document_frequency_filter_survives_real_data():
    """The design memory's own calibration concern (point 2): a real
    domain's near-identical grade-to-grade phrasing must not tie every
    grade of a strand together. Among the 18 grade/strand groupings'
    leaf-standard text, 'texts' appears in 15, 'including' in 16, and
    'author' in 13 -- all comfortably above `_MAX_DOCUMENT_FREQ` (4) -- so
    all three must be filtered out of every node's distinctive vocabulary,
    while each grade's genuinely distinctive content words survive."""
    index = build_vocabulary_index(READING_GRAPH)
    k_ri_words = index.node_words("va-reading-sol:K.RI")
    eighth_ri_words = index.node_words("va-reading-sol:8.RI")

    for boilerplate_word in ("texts", "including", "author"):
        assert boilerplate_word not in k_ri_words
        assert boilerplate_word not in eighth_ri_words

    # K.RI's own distinctive vocabulary (from its real leaf standards, e.g.
    # "With prompting and support, identify the purpose of common text
    # features...") survives filtering.
    assert "prompting" in k_ri_words
    # 8.RI's own distinctive vocabulary (e.g. "Analyze how an author
    # establishes and conveys a perspective...") survives filtering, and is
    # not shared with kindergarten's.
    assert "perspective" in eighth_ri_words
    assert "perspective" not in k_ri_words
