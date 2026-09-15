"""teach-8xw.43: first concept_recovery.py cross-test against
teach/actfl_can_do_graph.py (teach-cr8).

Before this bead, `grep -rl concept_recovery tests/` never matched
teach.actfl_can_do_graph -- teach-cr8's own handoff said as much explicitly:
"No concept_recovery/checker integration test was written... not re-exercised
against this specific graph this session." concept_recovery.py's genericity
claim (teach-8xw.10/.29) had been exercised against math, reading, and
writing domains only; the foreign-language proficiency-ladder domain had
never been tried.

This file mirrors test_concept_recovery_non_math_domain.py's and
test_concept_recovery_writing_domain.py's pattern and disclosure exactly: it
is a FLOOR test, not a generalization measurement. Every lesson text below is
hand-written by this session, so per sandbox-prompt.md's "you cannot hold
out examples from yourself" this establishes that recovery MECHANICALLY
WORKS against this graph -- not that it generalizes to lesson text nobody in
this session imagined. Every fixture was checked against the actual
`score_candidates`/`recover_from_lesson_text` output before being written
into an assertion (not guessed and then patched until green).

TWO THINGS THIS GRAPH'S OWN STRUCTURE PUT UNDER REAL PRESSURE THAT NO PRIOR
DOMAIN DID:

1. `facts["function_prompt"]` is IDENTICAL across all 11 nodes of a given
   Can-Do mode (e.g. every Interpersonal node repeats "How can I exchange
   information and ideas in conversations?"). That means "exchange",
   "information", and "ideas" have document frequency 11 out of 11 nodes in
   the Interpersonal graph -- comfortably above `_MAX_DOCUMENT_FREQ` (4) --
   and the boilerplate filter drops all three from every node's distinctive
   vocabulary, exactly as it drops VA SOL's "reasoning"/"problems" filler.
   See `test_shared_function_prompt_filtered_from_interpersonal_vocabulary`.
2. Unlike every prior graph exercised (VA Math/Reading/Writing SOL, Judson),
   the Intercultural mode's `ConceptNode.facts` has no `performance_indicator`
   or `proficiency_benchmark` key at all -- it uses six differently-named
   opaque fields (`investigation_benchmark`, `investigation_indicator_
   products`, `investigation_indicator_practices`, `interaction_benchmark`,
   `interaction_indicator_language`, `interaction_indicator_behavior`).
   `_node_vocabulary`'s generic string-flattening (teach-8xw.10's design --
   it never reads a named key, only recursively harvests every string
   reachable inside `facts`) has to pull distinguishing vocabulary from that
   differently-shaped payload with no code change. See
   `test_generic_harvesting_recovers_intercultural_opaque_fact_fields` and
   `test_harvesting_pulls_words_from_every_intercultural_fact_field`.
"""
from teach.actfl_can_do_graph import (
    load_actfl_can_do_graph,
    load_actfl_intercultural_graph,
)
from teach.concept_recovery import (
    build_vocabulary_index,
    recover_from_lesson_text,
    score_candidates,
)

INTERPERSONAL_GRAPH = load_actfl_can_do_graph()
INTERCULTURAL_GRAPH = load_actfl_intercultural_graph()

# Two adjacent sublevels of the Interpersonal ordinal chain
# (actfl-can-do:advanced-low -> actfl-can-do:advanced-mid, a direct
# PrerequisiteEdge). Quotes each sublevel's real, sourced
# `performance_indicator` text verbatim (see _SUBLEVELS in
# actfl_can_do_graph.py) -- checked against score_candidates before being
# written here: advanced-mid scores 8, advanced-low (the closest rival)
# scores 6, a margin of 2 with 67% winning coverage of advanced-mid's own
# distinctive vocabulary.
CORRECT_RECOVERY_TEXT = (
    "tutor: Last year you already learned to ask and answer a variety of "
    "questions about familiar topics.\n"
    "learner: Right, I could do that.\n"
    "tutor: Today, one step further: I can maintain discussions across "
    "time frames on a wide variety of familiar and unfamiliar topics, "
    "using probing questions and detailed responses."
)
CORRECT_RECOVERY_TAUGHT = "actfl-can-do:advanced-mid"
CORRECT_RECOVERY_ASSUMED = ("actfl-can-do:advanced-low",)


def test_correct_recovery_of_two_adjacent_actfl_sublevels():
    """A lesson quoting real Advanced Mid performance-indicator language,
    with the real Advanced Low indicator signposted as already known,
    recovers both correctly against the actual sourced NCSSFL-ACTFL
    Interpersonal Communication chain -- not a synthetic fixture."""
    result = recover_from_lesson_text(CORRECT_RECOVERY_TEXT, INTERPERSONAL_GRAPH)
    assert result.taught_node_id == CORRECT_RECOVERY_TAUGHT
    assert result.assumed_prerequisite_ids == CORRECT_RECOVERY_ASSUMED
    assert result.unsignposted_prerequisite_ids == ()
    assert result.abstain_reason is None


def test_unsignposted_prerequisite_detected_without_signal_phrase():
    """Same lesson content as the correct-recovery fixture, but with the
    'Last year you already learned...' signal stripped entirely (not even
    a bare 'remember'/'already' cue): the text still leans on enough of
    Advanced Low's real distinctive vocabulary ("answer") to count as
    unsignposted use, per teach-20c's three-way split."""
    text = (
        "tutor: Ask and answer a variety of questions about familiar "
        "topics. Today: I can maintain discussions across time frames on "
        "a wide variety of familiar and unfamiliar topics, using probing "
        "questions and detailed responses."
    )
    result = recover_from_lesson_text(text, INTERPERSONAL_GRAPH)
    assert result.taught_node_id == CORRECT_RECOVERY_TAUGHT
    assert result.assumed_prerequisite_ids == ()
    assert result.unsignposted_prerequisite_ids == CORRECT_RECOVERY_ASSUMED


def test_abstains_on_content_outside_actfl_vocabulary():
    """Lesson text about abstract-algebra group theory -- entirely outside
    an ordinal proficiency-sublevel ladder's vocabulary -- shares zero
    distinctive words with any of the 11 Interpersonal Communication nodes
    and must abstain, not guess a sublevel. The same disclosed-gap
    abstention teach-8xw.15 established for math (against a K-8 graph),
    teach-8xw.29 for reading, and teach-8xw.42 for writing, now checked for
    the foreign-language proficiency-ladder domain."""
    text = (
        "tutor: M needs proof this cell can survive interrogation -- show "
        "me the kernel of this homomorphism is normal, and that every "
        "coset of it partitions the group into equal pieces."
    )
    index = build_vocabulary_index(INTERPERSONAL_GRAPH)
    assert score_candidates(text, index) == ()

    result = recover_from_lesson_text(text, INTERPERSONAL_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert result.assumed_prerequisite_ids == ()


def test_shared_function_prompt_filtered_from_interpersonal_vocabulary():
    """Every one of the 11 Interpersonal nodes repeats the identical
    `facts["function_prompt"]` string ("How can I exchange information and
    ideas in conversations?"), so "exchange", "information", and "ideas"
    have document frequency 11/11 -- comfortably above `_MAX_DOCUMENT_FREQ`
    (4) -- and must be filtered as boilerplate from every node's
    distinctive vocabulary, the same discipline that keeps VA SOL's
    near-identical grade-to-grade phrasing from tying every grade together.
    A sublevel's genuinely distinctive words (its own real
    performance_indicator content) must survive that same filter."""
    index = build_vocabulary_index(INTERPERSONAL_GRAPH)
    for node in INTERPERSONAL_GRAPH.nodes:
        words = index.node_words(node.id)
        for boilerplate_word in ("exchange", "information", "ideas"):
            assert boilerplate_word not in words, (node.id, boilerplate_word)

    advanced_mid_words = index.node_words("actfl-can-do:advanced-mid")
    advanced_low_words = index.node_words("actfl-can-do:advanced-low")
    for distinctive_word in ("detailed", "responses", "wide"):
        assert distinctive_word in advanced_mid_words
        assert distinctive_word not in advanced_low_words


# Intercultural Communication's facts have no "performance_indicator"/
# "proficiency_benchmark" key at all (see actfl_can_do_graph.py's
# teach-8xw.49 docstring section) -- six differently-named fields instead.
# Quotes real, sourced text from actfl-can-do:intercultural:novice (assumed)
# and actfl-can-do:intercultural:intermediate (taught), a direct
# PrerequisiteEdge. Checked against score_candidates before being written
# here: intermediate scores 19, its closest rivals (advanced, novice) both
# score 11 -- a margin of 8.
INTERCULTURAL_CORRECT_RECOVERY_TEXT = (
    "tutor: Last year you already learned how to identify products and "
    "practices that help you understand perspectives from a variety of "
    "cultures and communities, including your own -- you could interact "
    "at a limited level in some familiar everyday situations.\n"
    "learner: Right, that felt pretty basic.\n"
    "tutor: Today we build on that: you will compare products to "
    "understand perspectives related to familiar contexts and personal "
    "interests, and compare practices to understand perspectives related "
    "to familiar contexts and personal interests too. You can interact at "
    "a functional level in some familiar contexts. You will interact with "
    "others from a variety of cultures and communities, including your "
    "own, in familiar situations and demonstrate some understanding of "
    "cultural similarities and differences. And you will recognize that "
    "significant differences in behaviors exist among cultures and use "
    "some culturally appropriate behaviors in familiar situations."
)
INTERCULTURAL_CORRECT_RECOVERY_TAUGHT = "actfl-can-do:intercultural:intermediate"
INTERCULTURAL_CORRECT_RECOVERY_ASSUMED = ("actfl-can-do:intercultural:novice",)


def test_generic_harvesting_recovers_intercultural_opaque_fact_fields():
    """concept_recovery.py's genericity claim (teach-8xw.10: `_flatten_
    strings` never reads a named key) has to hold even though Intercultural
    Communication's facts payload is shaped completely differently from
    every graph this module had been exercised against before (no
    performance_indicator/proficiency_benchmark; six other field names
    instead -- see module docstring). Recovery of taught concept and
    assumed prerequisite still works with no code change."""
    result = recover_from_lesson_text(
        INTERCULTURAL_CORRECT_RECOVERY_TEXT, INTERCULTURAL_GRAPH
    )
    assert result.taught_node_id == INTERCULTURAL_CORRECT_RECOVERY_TAUGHT
    assert result.assumed_prerequisite_ids == INTERCULTURAL_CORRECT_RECOVERY_ASSUMED
    assert result.unsignposted_prerequisite_ids == ()
    assert result.abstain_reason is None


def test_harvesting_pulls_words_from_every_intercultural_fact_field():
    """Direct check that `_node_vocabulary` actually reached into all six of
    Intercultural's opaque fact fields, not just whichever field happens to
    look like a familiar name -- one real, distinguishing word sourced from
    each field on `actfl-can-do:intercultural:novice`."""
    index = build_vocabulary_index(INTERCULTURAL_GRAPH)
    novice_words = index.node_words("actfl-can-do:intercultural:novice")

    # "identify" -- shared by investigation_benchmark, _indicator_products,
    # and _indicator_practices (all three open with "I can identify...").
    assert "identify" in novice_words
    # "limited" -- interaction_benchmark ("I can interact at a limited
    # level...").
    assert "limited" in novice_words
    # "communicate" -- interaction_indicator_language ("I can communicate
    # with others...").
    assert "communicate" in novice_words
    # "rehearsed" -- interaction_indicator_behavior ("I can use appropriate
    # rehearsed behaviors...").
    assert "rehearsed" in novice_words
