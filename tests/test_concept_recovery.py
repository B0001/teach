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
    _node_vocabulary,
    build_vocabulary_index,
    recover_assumed_prerequisites,
    recover_from_lesson_text,
    recover_unsignposted_prerequisites,
    score_candidates,
)
from teach.dummit_foote_graph import load_dummit_foote_graph
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


def test_uuid_bookkeeping_field_does_not_leak_hex_fragments_into_vocabulary():
    """teach-klm: va_math_sol_graph.py's case_identifier_uuid is bookkeeping,
    not curriculum content, but _flatten_strings must stay ignorant of that
    key name (the same opacity rule the test above enforces) -- so the fix
    has to recognize the UUID by its *shape*, not its field name. Reproduces
    the bead's two flagged nodes directly against the real graph."""
    node = ConceptNode(
        id="synthetic:uuid-in-facts", domain="math", label="Synthetic node",
        facts={"case_identifier_uuid": "5184644f-d652-4ed4-8bdc-6ededf2a6965",
               "notes": "perimeter and area formulas for quadrilaterals"},
    )
    vocab = _node_vocabulary(node)
    assert "ededf" not in vocab
    assert "perimeter" in vocab and "quadrilaterals" in vocab

    graph = load_va_math_sol_graph()
    nodes = {n.id: n for n in graph.nodes}
    assert "ededf" not in _node_vocabulary(nodes["va-math-sol:4.MG"])
    assert "baca" not in _node_vocabulary(nodes["va-math-sol:3.PS"])


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


def test_two_sentence_announcement_recovered_against_the_real_graph():
    """teach-8xw.27's exact reproduction: a lesson that announces a
    prerequisite with 'Remember X from last year?' and then elaborates on X
    in a *following* sentence (a short 'Great.' acknowledgment in between)
    must be recovered as signposted, not silently miscategorized as
    unsignposted -- checked against the real teach-8xw.5 VA Math SOL graph,
    not a synthetic fixture."""
    text = (
        "Tutor: Remember polygons from last year? Great. We will now "
        "combine and subdivide several of them using grids. Today we "
        "develop and use actual formulas for the perimeter and area of "
        "rectangles, parallelograms, rhombi, and trapezoids."
    )
    result = recover_from_lesson_text(text, VA_GRAPH)
    assert result.taught_node_id == "va-math-sol:4.MG"
    assert result.assumed_prerequisite_ids == ("va-math-sol:3.MG",)
    assert result.unsignposted_prerequisite_ids == ()


def test_assumed_prerequisite_recognized_across_a_short_discourse_gap():
    """teach-8xw.27: an ordinary teaching announcement often splits the
    already-known cue from the sentence that actually names the
    prerequisite's content ('Cue. Good. <content>.') rather than packing
    both into one sentence. This must still count as signposted. Checked
    against several independently phrased cues -- not just the literal
    'remember' phrasing the bug was filed against -- so the fix is a real
    widening of the co-occurrence window, not a patch for one phrasing."""
    graph = ConceptGraph(
        nodes=(
            ConceptNode(id="a", domain="math", label="A",
                        facts={"detail": "zebras xylophones quicksand mongoose"}),
            ConceptNode(id="b", domain="math", label="B",
                        facts={"detail": "walruses yardsticks umbrellas trombones bicycles"}),
        ),
        edges=(PrerequisiteEdge(src="a", dst="b"),),
    )
    cues = [
        "You already know this.",
        "Recall what we did before.",
        "You've already learned plenty.",
        "Last year you covered a lot.",
        "Remember what we did?",
    ]
    for cue in cues:
        text = (
            f"{cue} Good. That covered zebras, xylophones, and quicksand "
            "along the way. Today we cover walruses, yardsticks, "
            "umbrellas, trombones, and bicycles."
        )
        result = recover_from_lesson_text(text, graph)
        assert result.taught_node_id == "b", (cue, result.candidates)
        assert result.assumed_prerequisite_ids == ("a",), (cue, result.assumed_prerequisite_ids)
        assert result.unsignposted_prerequisite_ids == ()


def test_window_does_not_rescue_a_prerequisite_with_no_nearby_cue():
    """The window widening must not degrade into 'any cue anywhere in the
    text covers every prerequisite' -- that would just make the
    unsignposted flag fire less often across the board, the exact failure
    mode this bead's method note warns against. A second, genuinely
    unannounced prerequisite ('c') that shares no sentence within the
    window of the text's one cue must still be reported as unsignposted,
    even though a real 'you already know' cue exists elsewhere in the same
    lesson (announcing a different prerequisite, 'a')."""
    graph = ConceptGraph(
        nodes=(
            ConceptNode(id="a", domain="math", label="A",
                        facts={"detail": "zebras xylophones quicksand mongoose"}),
            ConceptNode(id="b", domain="math", label="B",
                        facts={"detail": "walruses yardsticks umbrellas trombones bicycles"}),
            ConceptNode(id="c", domain="math", label="C",
                        facts={"detail": "addax bison caribou dingo"}),
        ),
        edges=(
            PrerequisiteEdge(src="a", dst="b"),
            PrerequisiteEdge(src="c", dst="b"),
        ),
    )
    text = (
        "You already know this. Good. That covered zebras, xylophones, "
        "and quicksand along the way. Today we cover walruses, "
        "yardsticks, umbrellas, trombones, and bicycles. By the way we "
        "will also touch addax, bison, and caribou without calling much "
        "attention to it."
    )
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id == "b", result.candidates
    assert result.assumed_prerequisite_ids == ("a",)
    assert result.unsignposted_prerequisite_ids == ("c",)


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


def test_faithful_paraphrase_recovers_via_semantic_fallback_tier():
    """teach-8xw.26's exact reproduction: a faithful, no-invention paraphrase
    of va-math-sol:4.MG's real leaf standards ("rules" for formulas, "space
    covered" for area, "four-sided shapes with square corners" for
    rectangles/squares, "tell apart... by properties" for classify,
    "crossing" for intersecting) shares almost none of 4.MG's literal
    distinctive vocabulary, and raw exact-word scoring alone abstains
    (ambiguous against 7.MG/8.MG). The semantic fallback tier (WordNet
    lemma/synonym matching) must recover it correctly rather than leaving
    this reproduction abstained."""
    graph = load_va_math_sol_graph()
    text = (
        "Tutor: Today we will work out rules for finding the perimeter and "
        "the space covered by four-sided shapes with square corners. We "
        "will also learn to tell apart different four-sided shapes -- ones "
        "with two pairs of matching sides, ones where all sides match, and "
        "slanted ones -- by their properties. We will also draw crossing, "
        "side-by-side, and square-cornered straight lines."
    )
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id == "va-math-sol:4.MG", result.candidates
    assert result.abstain_reason is None


def test_semantic_tier_still_abstains_on_a_thin_coincidental_margin():
    """teach-8xw.26's generalization measurement (see the bead's handoff)
    found the semantic fallback tier can turn an honest abstention into a
    WRONG confident answer: a faithful, independently-written paraphrase of
    va-math-sol:3.PS ("we're walking through the full process of working
    with data... coming up with a good question we actually want an answer
    to...") spuriously out-scored every real candidate for va-math-sol:8.PFA
    via ordinary-English WordNet synonym pairs with no domain content at
    all ("want"/"require", "answer"/"solution") at a raw margin of only 2 --
    the same margin the raw exact-word tier already tolerates. This is
    exactly the case sandbox-prompt.md's "prefer abstention to a confident
    answer" warns about: a wrong guess is worse than admitting the text is
    unclear. `_SEMANTIC_MIN_MARGIN` (stricter than the raw tier's
    `_MIN_MARGIN`) exists to keep this a silent abstention, not a wrong
    node id -- this test locks that in against the exact text that
    surfaced it, since it came from a fresh agent with no visibility into
    this module's algorithm or thresholds, not from this session's own
    idea of what a paraphrase looks like."""
    graph = load_va_math_sol_graph()
    text = (
        "Tutor: Today we're walking through the full process of working "
        "with data, starting with coming up with a good question we "
        "actually want an answer to. Next we gather the information, "
        "either by collecting it ourselves or pulling it from somewhere "
        "it's already been recorded. Then we organize what we've gathered "
        "and display it visually -- specifically using pictographs, where "
        "pictures or symbols stand for amounts, and bar graphs, where bar "
        "heights or lengths show the amounts. The last step is looking "
        "closely at what the display tells us and explaining our findings "
        "in words."
    )
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id is None, (
        f"expected abstention, got {result.taught_node_id!r} -- the "
        "semantic tier's margin guard regressed"
    )
    assert result.abstain_reason is not None


def test_semantic_tier_recovers_dummit_foote_paraphrase_raw_tier_missed():
    """Same fallback mechanism, checked against the OTHER domain in this
    repo (dummit_foote_graph.py, undergraduate abstract algebra) with an
    independently-written paraphrase of dummit-foote:1.6-homomorphisms
    (from teach-8xw.26's blind generalization set) that raw exact-word
    scoring leaves ambiguous against 3.3-isomorphism-theorems, since both
    nodes' vocabularies revolve around "isomorphic"/"isomorphism". WordNet
    lemma/synonym matching (mapping this paraphrase's "map", "matchup", and
    "structure" language onto the source's own vocabulary) gives
    homomorphisms a decisive lead once the exact wording is normalized."""
    graph = load_dummit_foote_graph()
    text = (
        "Tutor: A homomorphism is a map from one group to another that "
        "respects the way things combine -- if you combine two elements "
        "first and then map the result, you get the same thing as mapping "
        "each one separately and then combining those. When a map like "
        "that is also a perfect one-to-one, onto matchup between the two "
        "groups, we upgrade its name to an isomorphism, and we say the two "
        "groups are isomorphic, meaning they're really the same structure "
        "wearing different labels. The kernel of the map is the collection "
        "of everything in the starting group that gets sent all the way to "
        "the unchanging special element on the other side. We also talk "
        "about the image, which is everything the map actually lands on in "
        "the second group."
    )
    result = recover_from_lesson_text(text, graph)
    assert result.taught_node_id == "dummit-foote:1.6-homomorphisms", result.candidates
    assert result.abstain_reason is None
