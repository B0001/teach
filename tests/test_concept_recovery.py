"""Enforce the checker defined in teach/concept_recovery.py.

teach-8xw.10's acceptance criteria: given a small fixed set of hand-written
lesson texts with known ground truth (concept + prerequisite set), recovery
either identifies them correctly or explicitly abstains -- proven with a
runnable check exercising at least one correct-recovery path and one
abstention path. This file exercises both, plus the specific failure modes
the module docstring calls out (ambiguous match, no-overlap-at-all, and
genuine domain-agnosticism of the vocabulary extractor).
"""
from teach.boundary import LessonArtifact, Turn
from teach.concept_graph import ConceptGraph, ConceptNode, PrerequisiteEdge
from teach.concept_recovery import (
    ABSTAIN_TEXT,
    CORRECT_RECOVERY_ASSUMED,
    CORRECT_RECOVERY_TAUGHT,
    CORRECT_RECOVERY_TEXT,
    build_vocabulary_index,
    recover_assumed_prerequisites,
    recover_from_lesson_text,
    recover_unsignposted_prerequisites,
    score_candidates,
)
from teach.va_math_sol_graph import load_va_math_sol_graph

VA_GRAPH = load_va_math_sol_graph()


def test_correct_recovery_example_identifies_node_and_prerequisite():
    """The bead's required correct-recovery fixture: a hand-written lesson
    text, checked against the real teach-8xw.5 VA Math SOL graph, recovers
    the right taught node and the right assumed prerequisite."""
    result = recover_from_lesson_text(CORRECT_RECOVERY_TEXT, VA_GRAPH)
    assert result.taught_node_id == CORRECT_RECOVERY_TAUGHT
    assert result.assumed_prerequisite_ids == CORRECT_RECOVERY_ASSUMED
    assert result.abstain_reason is None


def test_abstain_example_out_of_graph_vocabulary():
    """The bead's required abstention fixture: lesson text about content the
    graph's vocabulary has nothing on (group theory, checked against a K-8
    VA Math SOL graph -- the actual, disclosed gap teach-8xw.15 flags for
    the Dummit & Foote test case) must abstain, not guess a K-8 node."""
    result = recover_from_lesson_text(ABSTAIN_TEXT, VA_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert result.assumed_prerequisite_ids == ()


def test_no_vocabulary_overlap_abstains_with_its_own_reason():
    """Distinct from the ambiguous-match abstention below: this text shares
    *no* distinctive words with any node at all, and the reason string must
    say so rather than reusing the "too close to call" reason."""
    text = "tutor: Good morning! How are you feeling today?"
    result = recover_from_lesson_text(text, VA_GRAPH)
    assert result.taught_node_id is None
    assert "overlaps this text at all" in result.abstain_reason


def test_plain_text_with_no_speaker_tags_still_recovers():
    """Bag-of-words scoring doesn't depend on the tutor:/learner: speaker
    convention -- bare text (not a LessonArtifact-shaped transcript) must
    still recover, since the bead says 'lesson text', not specifically a
    LessonArtifact."""
    text = CORRECT_RECOVERY_TEXT.replace("tutor: ", "").replace("learner: ", "")
    result = recover_from_lesson_text(text, VA_GRAPH)
    assert result.taught_node_id == CORRECT_RECOVERY_TAUGHT


def test_recovers_from_a_real_lessonartifact():
    """Interoperates with the actual boundary type a checker receives, not
    just a bare string built to look like one."""
    artifact = LessonArtifact(
        turns=(
            Turn("tutor", "Last year you already learned how to combine and "
                           "subdivide polygons using grids and simple tools."),
            Turn("learner", "Right, we cut some polygons into equal pieces."),
            Turn("tutor", "Today we go one step further: instead of just "
                           "combining shapes by eye, you'll develop and use "
                           "actual formulas for rectangles, parallelograms, "
                           "rhombi, and trapezoids -- and draw the "
                           "intersecting and perpendicular lines that make "
                           "up their angles."),
        )
    )
    result = recover_from_lesson_text(artifact.text, VA_GRAPH)
    assert result.taught_node_id == "va-math-sol:4.MG"
    assert result.assumed_prerequisite_ids == ("va-math-sol:3.MG",)


def test_ambiguous_candidates_abstain_rather_than_guess():
    """Two candidates tied on score -- 'too close to call' must abstain
    instead of picking one arbitrarily. Built as a small synthetic graph
    (rather than hunting for a real tie in the 45-node VA graph) so the tie
    is exact and the test doesn't depend on graph internals shifting."""
    graph = ConceptGraph(
        nodes=(
            ConceptNode(id="a", domain="math", label="Alpha topic",
                        facts={"detail": "zebras xylophones quicksand mongoose"}),
            ConceptNode(id="b", domain="math", label="Beta topic",
                        facts={"detail": "walruses yardsticks umbrellas trombone"}),
        ),
        edges=(),
    )
    text = (
        "Today we cover zebras, xylophones, and quicksand, also walruses, "
        "yardsticks, and umbrellas."
    )
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()


def test_domain_agnostic_vocabulary_extraction_ignores_key_names():
    """concept_graph.py's docstring: ConceptNode.facts is opaque per-domain
    payload, and the engine must never assume a domain-specific key name.
    This is the same discipline applied to concept_recovery: a reading
    domain whose facts don't use the math domain's 'leaf_standards' key
    (arbitrary nested shape instead) must still be recoverable, or this
    module has quietly hardcoded a math-only assumption."""
    reading_main_idea = ConceptNode(
        id="reading:main-idea", domain="reading", label="Identify the main idea",
        facts={"skill_notes": {"summary": "readers extract the central idea from dense unfamiliar paragraphs"}},
    )
    reading_summarize = ConceptNode(
        id="reading:summarize", domain="reading", label="Summarize a text",
        facts={"skill_notes": {"summary": "readers compress paragraphs into fewer sentences without losing meaning"}},
    )
    graph = ConceptGraph(
        nodes=(reading_main_idea, reading_summarize),
        edges=(PrerequisiteEdge(src=reading_main_idea.id, dst=reading_summarize.id),),
    )
    text = (
        "Since you can already extract the central idea from a dense "
        "unfamiliar paragraph, let's summarize that same paragraph: "
        "compress it into fewer short sentences without losing its meaning "
        "or its overall text."
    )
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id == "reading:summarize"
    assert result.assumed_prerequisite_ids == ("reading:main-idea",)


def test_assumed_prerequisite_requires_signal_phrase_not_just_overlap():
    """Vocabulary overlap with a prerequisite node alone isn't evidence the
    lesson assumed it -- the text also has to actually signal that
    something is being treated as already known. A lesson that mentions
    prerequisite-adjacent words in passing, with no 'you already...'-style
    phrase anywhere, must report no assumed prerequisites."""
    index = build_vocabulary_index(VA_GRAPH)
    text = (
        "Today we'll develop and use actual formulas for rectangles, "
        "parallelograms, rhombi, and trapezoids, and we'll also mention "
        "polygons and subdividing shapes along the way."
    )
    assumed = recover_assumed_prerequisites(text, index, "va-math-sol:4.MG")
    assert assumed == ()


def test_only_direct_prerequisite_edges_are_considered():
    """A grandparent node (two edges away) must never be reported as an
    assumed prerequisite even if the text happens to signal it -- only
    direct PrerequisiteEdge sources of the taught node are candidates."""
    graph = ConceptGraph(
        nodes=(
            ConceptNode(id="a", domain="math", label="Node A", facts={"detail": "quicksand xylophones"}),
            ConceptNode(id="b", domain="math", label="Node B", facts={"detail": "walruses yardsticks"}),
            ConceptNode(id="c", domain="math", label="Node C",
                        facts={"detail": "umbrellas trombones bicycles accordions"}),
        ),
        edges=(
            PrerequisiteEdge(src="a", dst="b"),
            PrerequisiteEdge(src="b", dst="c"),
        ),
    )
    index = build_vocabulary_index(graph)
    text = (
        "You already learned about quicksand and xylophones. "
        "Today we cover umbrellas, trombones, bicycles, and accordions."
    )
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id == "c"
    # "a" is only a prerequisite of "b", not of "c" -- must not appear here.
    assert result.assumed_prerequisite_ids == ()


def test_unsignposted_prerequisite_use_is_flagged_without_a_signal_phrase():
    """teach-20c: a lesson that leans on enough of a direct prerequisite's
    distinctive vocabulary to be leaning on it, with no 'you already
    know'-style phrase anywhere, must be reported as unsignposted use --
    not silently collapsed into the same empty result as a lesson that
    assumes nothing."""
    graph = ConceptGraph(
        nodes=(
            ConceptNode(id="a", domain="math", label="Node A",
                        facts={"detail": "zebras xylophones quicksand mongoose"}),
            ConceptNode(id="b", domain="math", label="Node B",
                        facts={"detail": "walruses yardsticks umbrellas trombones bicycles"}),
        ),
        edges=(PrerequisiteEdge(src="a", dst="b"),),
    )
    # "b" (taught) matches all 5 of its own words; "a" (direct prerequisite)
    # matches only 3 of its 4 -- enough to clear both the unsignposted bar
    # (>= 3) and the taught-concept margin bar (5 - 3 >= 2) without a tie.
    text = (
        "Today we cover walruses, yardsticks, umbrellas, trombones, and "
        "bicycles, plus some zebras, xylophones, and quicksand along the "
        "way for flavor."
    )
    index = build_vocabulary_index(graph)
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id == "b"
    assert result.assumed_prerequisite_ids == ()
    assert result.unsignposted_prerequisite_ids == ("a",)
    # And the underlying function agrees when called directly.
    assert recover_unsignposted_prerequisites(text, index, "b", ()) == ("a",)


def test_unsignposted_and_assumed_are_mutually_exclusive():
    """A prerequisite the text explicitly signposts must not ALSO show up
    as unsignposted -- the two fields partition the direct prerequisites,
    they don't overlap."""
    graph = ConceptGraph(
        nodes=(
            ConceptNode(id="a", domain="math", label="Node A",
                        facts={"detail": "zebras xylophones quicksand mongoose"}),
            ConceptNode(id="b", domain="math", label="Node B",
                        facts={"detail": "walruses yardsticks umbrellas trombones bicycles"}),
        ),
        edges=(PrerequisiteEdge(src="a", dst="b"),),
    )
    text = (
        "You already know about zebras, xylophones, and quicksand. Today we "
        "cover walruses, yardsticks, umbrellas, trombones, and bicycles."
    )
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id == "b"
    assert result.assumed_prerequisite_ids == ("a",)
    assert result.unsignposted_prerequisite_ids == ()


def test_unsignposted_detection_only_considers_direct_prerequisites():
    """Same discipline as `recover_assumed_prerequisites`: a grandparent
    node (two edges away) must never be flagged as unsignposted, even if
    the text happens to share plenty of its distinctive vocabulary."""
    graph = ConceptGraph(
        nodes=(
            ConceptNode(id="a", domain="math", label="Node A",
                        facts={"detail": "zebras xylophones quicksand mongoose"}),
            ConceptNode(id="b", domain="math", label="Node B",
                        facts={"detail": "walruses yardsticks"}),
            ConceptNode(id="c", domain="math", label="Node C",
                        facts={"detail": "umbrellas trombones bicycles accordions saxophones"}),
        ),
        edges=(
            PrerequisiteEdge(src="a", dst="b"),
            PrerequisiteEdge(src="b", dst="c"),
        ),
    )
    # "c" (taught) matches all 5 of its own words; "a" (grandparent, not a
    # direct prerequisite of "c") matches only 3 of its 4 -- enough to clear
    # the unsignposted overlap bar on its own, and enough margin (5 - 3 >= 2)
    # that concept identification isn't itself ambiguous.
    text = (
        "Today we cover umbrellas, trombones, bicycles, accordions, and "
        "saxophones -- plus zebras, xylophones, and quicksand for good "
        "measure."
    )
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id == "c"
    # "a" is a grandparent of "c", not a direct prerequisite -- must not
    # appear even though the text shares 3 of its 4 distinctive words.
    assert result.unsignposted_prerequisite_ids == ()


def test_unsignposted_detection_requires_the_same_overlap_bar_as_recovery():
    """A stray word or two from a prerequisite's vocabulary is not enough
    to call it unsignposted use -- same abstention discipline as everywhere
    else in this module. Below the match-word threshold, silence."""
    graph = ConceptGraph(
        nodes=(
            ConceptNode(id="a", domain="math", label="Node A",
                        facts={"detail": "zebras xylophones quicksand mongoose"}),
            ConceptNode(id="b", domain="math", label="Node B",
                        facts={"detail": "walruses yardsticks umbrellas trombones bicycles"}),
        ),
        edges=(PrerequisiteEdge(src="a", dst="b"),),
    )
    text = (
        "Today we cover walruses, yardsticks, umbrellas, trombones, and "
        "bicycles. A zebra wandered by once, too."
    )
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id == "b"
    assert result.unsignposted_prerequisite_ids == ()


def test_build_vocabulary_index_filters_boilerplate_words():
    """A word shared across most nodes (boilerplate curriculum phrasing) is
    excluded from every node's distinctive vocabulary, even though it's a
    real word in the node's text -- this is the mechanism that keeps
    generic SOL phrasing from tying every grade of a strand together."""
    unique_words = ["zebra", "walrus", "trombone", "accordion", "mongoose", "yardstick"]
    graph = ConceptGraph(
        nodes=tuple(
            ConceptNode(
                id=f"n{i}", domain="math", label=f"Node {i}",
                facts={"detail": f"reasoning justification {unique_words[i]}"},
            )
            for i in range(6)
        ),
        edges=(),
    )
    index = build_vocabulary_index(graph)
    # "reasoning"/"justification" appear in all 6 nodes -- boilerplate, filtered out.
    assert "reasoning" not in index.node_words("n0")
    assert "justification" not in index.node_words("n0")
    # each node's own distinct word survives.
    assert "zebra" in index.node_words("n0")
    assert "accordion" in index.node_words("n3")


def test_coverage_tiebreak_resolves_a_full_chain_lessons_margin_of_one():
    """teach-ed3: a lesson that walks a full prerequisite chain with real
    content at every step can give an earlier, bigger-vocabulary scaffolding
    node a raw-overlap score close enough to the actual target's that the
    old raw-margin-only rule would abstain (this is exactly what happened to
    teach-8xw.15's Bond/Lagrange lesson: margin of 1, cosets 12 vs Lagrange
    13). Here "a" is the earlier node with a 6-word vocabulary, "b" is the
    target with a 5-word vocabulary that the text covers *completely* --
    raw scores are b=5, a=4 (margin 1, below _MIN_MARGIN), but b's coverage
    (5/5 = 1.0) decisively beats a's (4/6 = 0.667), so this must recover b,
    not abstain."""
    graph = ConceptGraph(
        nodes=(
            # Single-letter labels so the label itself contributes no words
            # to vocabulary (words under 4 letters are dropped by `_words`)
            # -- this test is about the facts vocabulary's coverage math,
            # not incidental overlap from a "Node A"/"Node B"-style label.
            ConceptNode(id="a", domain="math", label="A",
                        facts={"detail": "zebras xylophones quicksand mongoose addax bison"}),
            ConceptNode(id="b", domain="math", label="B",
                        facts={"detail": "walruses yardsticks umbrellas trombones bicycles"}),
        ),
        edges=(PrerequisiteEdge(src="a", dst="b"),),
    )
    text = (
        "Today we cover walruses, yardsticks, umbrellas, trombones, and "
        "bicycles -- building on zebras, xylophones, quicksand, and "
        "mongoose from before."
    )
    index = build_vocabulary_index(graph)
    candidates = score_candidates(text, index)
    scores = {c.node_id: c.score for c in candidates}
    assert scores == {"b": 5, "a": 4}, scores  # raw margin is exactly 1

    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id == "b"
    assert result.abstain_reason is None


def test_coverage_tiebreak_does_not_rescue_similarly_partial_coverage():
    """The tiebreak requires the winner's coverage to be both near-total
    (>= _MIN_COVERAGE_FRACTION) and decisively ahead of every close rival
    (>= _MIN_COVERAGE_MARGIN) -- two candidates that are each partially and
    similarly covered is a real ambiguous match, not a case the tiebreak
    should paper over. Same graph shape as the rescue test above, but the
    text only partially covers "b" (3 of 5 words) at a fraction (0.6) far
    below the 0.85 coverage bar, so this must still abstain."""
    graph = ConceptGraph(
        nodes=(
            ConceptNode(id="a", domain="math", label="A",
                        facts={"detail": "zebras xylophones quicksand mongoose addax bison"}),
            ConceptNode(id="b", domain="math", label="B",
                        facts={"detail": "walruses yardsticks umbrellas trombones bicycles"}),
        ),
        edges=(PrerequisiteEdge(src="a", dst="b"),),
    )
    text = (
        "Today we mostly cover walruses, yardsticks, and umbrellas -- "
        "building on zebras, xylophones, quicksand, and mongoose from "
        "before."
    )
    index = build_vocabulary_index(graph)
    candidates = score_candidates(text, index)
    scores = {c.node_id: c.score for c in candidates}
    assert scores == {"b": 3, "a": 4}

    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()


def test_dnf_bond_lesson_recovers_lagrange_without_a_single_word_margin():
    """teach-ed3's actual trigger: teach-8xw.15's real Bond/Lagrange lesson
    (teach/dnf_bond_lesson.py) once had a raw-score margin of exactly 1
    (Lagrange 13 vs cosets 12) before a single word ("proof") was added to
    push it to the _MIN_MARGIN=2 floor -- a single point of margin, not a
    robust property. This test removes that same word from the real,
    already-built lesson text and confirms the coverage tiebreak recovers
    Lagrange's theorem anyway, so the correctness of this lesson's recovery
    no longer hinges on one word."""
    from teach.dnf_bond_lesson import build_lesson
    from teach.dummit_foote_graph import TARGET_NODE_ID, load_dummit_foote_graph

    graph = load_dummit_foote_graph()
    artifact = build_lesson()
    assert "the proof behind it is" in artifact.text  # guards the fixture itself
    text_without_proof = artifact.text.replace("the proof behind it is", "it is")

    index = build_vocabulary_index(graph)
    candidates = score_candidates(text_without_proof, index)
    by_id = {c.node_id: c.score for c in candidates}
    assert by_id[TARGET_NODE_ID] - by_id["dummit-foote:3.1-cosets"] == 1  # reproduces the fragile margin

    result = recover_from_lesson_text(text_without_proof, graph)
    assert result.taught_node_id == TARGET_NODE_ID
    assert result.abstain_reason is None
