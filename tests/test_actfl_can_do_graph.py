"""teach-cr8: the ACTFL/NCSSFL Can-Do proficiency-sublevel seed graph for the
foreign-language domain loads, is a true DAG, matches the documented strict
ordinal chain, and asserts no target language -- per the bead's own decision
recorded in teach/actfl_can_do_graph.py's DECISION section.

teach-8xw.49 extends coverage to the other three Can-Do communication modes
(Interpretive, Presentational, Intercultural) that teach-cr8 disclosed as
out of scope -- see that section of the module docstring for the parallel
node sets vs merged graph design choice.
"""
import pytest

from teach.concept_graph import GraphError, PrerequisiteEdge
from teach.actfl_can_do_graph import (
    SOURCE,
    SUBLEVEL_ORDER,
    INTERPRETIVE_SUBLEVEL_ORDER,
    PRESENTATIONAL_SUBLEVEL_ORDER,
    INTERCULTURAL_LEVEL_ORDER,
    load_actfl_can_do_graph,
    load_actfl_interpretive_graph,
    load_actfl_presentational_graph,
    load_actfl_intercultural_graph,
    _self_check,
    _self_check_interpretive,
    _self_check_presentational,
    _self_check_intercultural,
    _self_check_no_cross_mode_collisions,
)


def test_self_check_passes():
    _self_check()


def test_has_exactly_the_eleven_documented_sublevels():
    graph = load_actfl_can_do_graph()
    ids = {n.id for n in graph.nodes}
    assert ids == set(SUBLEVEL_ORDER)
    assert len(graph.nodes) == 11


def test_is_a_true_dag_no_cycles():
    graph = load_actfl_can_do_graph()
    graph.validate()  # raises GraphError on a cycle; must not raise here
    graph.topological_order()


def test_every_edge_references_a_node_that_exists():
    graph = load_actfl_can_do_graph()
    node_ids = {n.id for n in graph.nodes}
    assert graph.edges, "expected at least one prerequisite edge"
    for edge in graph.edges:
        assert edge.src in node_ids, f"dangling edge src: {edge.src!r}"
        assert edge.dst in node_ids, f"dangling edge dst: {edge.dst!r}"


def test_edges_are_exactly_the_strict_ordinal_chain():
    """10 edges: one per consecutive sublevel pair, in the source's own
    stated order (novice-low -> ... -> distinguished). Not fewer (a broken
    chain) and not more (a stray skip-edge implying a shortcut the source
    never claims)."""
    graph = load_actfl_can_do_graph()
    actual = {(e.src, e.dst) for e in graph.edges}
    expected = set(zip(SUBLEVEL_ORDER, SUBLEVEL_ORDER[1:]))
    assert actual == expected
    assert all(e.type == "precedes" for e in graph.edges)


def test_topological_order_matches_the_documented_sequence():
    graph = load_actfl_can_do_graph()
    assert graph.topological_order() == SUBLEVEL_ORDER


def test_novice_low_is_the_sole_root_and_distinguished_the_sole_leaf():
    graph = load_actfl_can_do_graph()
    dsts = {e.dst for e in graph.edges}
    srcs = {e.src for e in graph.edges}
    node_ids = {n.id for n in graph.nodes}
    roots = node_ids - dsts
    leaves = node_ids - srcs
    assert roots == {"actfl-can-do:novice-low"}
    assert leaves == {"actfl-can-do:distinguished"}


def test_content_actually_escalates_not_just_labels():
    """Guards against a data error that shuffled labels without shuffling
    text: Novice Low leans on gesture/visual support and memorized language;
    Distinguished names neither and adds culturally nuanced complex
    discourse instead."""
    graph = load_actfl_can_do_graph()
    novice_low = graph.by_id("actfl-can-do:novice-low").facts["performance_indicator"]
    distinguished = graph.by_id("actfl-can-do:distinguished").facts["performance_indicator"]
    assert "gestures" in novice_low
    assert "memorized" in novice_low
    assert "gestures" not in distinguished
    assert "memorized" not in distinguished
    assert "culturally nuanced" in distinguished


def test_every_node_shares_the_same_mode_and_function():
    """All eleven nodes are drawn from one communication function so the
    chain reads as one coherent ladder, not stitched-together unrelated
    skills -- see the module's NODE GRANULARITY section."""
    graph = load_actfl_can_do_graph()
    for node in graph.nodes:
        assert node.facts["mode"] == "Interpersonal Communication"
        assert node.facts["function_prompt"] == (
            "How can I exchange information and ideas in conversations?"
        )


def test_no_target_language_is_asserted_anywhere():
    """The DECISION section commits to a language-agnostic seed. This is
    the assertion that fails loudly if a later edit quietly bolts a
    language name onto the data instead of filing a new bead for it."""
    graph = load_actfl_can_do_graph()
    for node in graph.nodes:
        assert node.domain == "foreign-language"
        blob = " ".join(str(v) for v in node.facts.values()).lower()
        for language in ("spanish", "french", "japanese", "mandarin", "german"):
            assert language not in blob


def test_source_provenance_is_recorded_not_asserted_from_memory():
    assert "actfl.org" in SOURCE["listing_page"]
    assert len(SOURCE["pdfs_fetched"]) == 5
    assert all(url.startswith("https://www.actfl.org/") for url in SOURCE["pdfs_fetched"])
    assert "2026" in SOURCE["year"]
    assert "NON-PROFIT USE ONLY" in SOURCE["usage_terms"]


def test_a_hand_introduced_cycle_is_rejected_not_silently_ordered():
    """Not a property of the shipped data (already tested acyclic above) --
    a regression guard that this domain's loader output still goes through
    concept_graph's real cycle check, not a stub."""
    graph = load_actfl_can_do_graph()
    cyclic_edges = graph.edges + (
        PrerequisiteEdge(src="actfl-can-do:distinguished", dst="actfl-can-do:novice-low"),
    )
    cyclic_graph = graph.__class__(nodes=graph.nodes, edges=cyclic_edges)
    with pytest.raises(GraphError):
        cyclic_graph.topological_order()


# ---------------------------------------------------------------------------
# teach-8xw.49: Interpretive and Presentational Communication -- same
# 11-sublevel shape as Interpersonal above, but separate graphs (parallel
# node sets, per the module docstring's teach-8xw.49 DESIGN CHOICE section).
# ---------------------------------------------------------------------------

_MODE_CASES = (
    (
        load_actfl_interpretive_graph,
        INTERPRETIVE_SUBLEVEL_ORDER,
        "actfl-can-do:interpretive:novice-low",
        "actfl-can-do:interpretive:distinguished",
        "Interpretive Communication",
        "What can I understand, interpret, or analyze in authentic "
        "informational texts and media?",
    ),
    (
        load_actfl_presentational_graph,
        PRESENTATIONAL_SUBLEVEL_ORDER,
        "actfl-can-do:presentational:novice-low",
        "actfl-can-do:presentational:distinguished",
        "Presentational Communication",
        "How can I present information to inform and explain?",
    ),
)


@pytest.mark.parametrize(
    "loader, order, root_id, leaf_id, mode, function_prompt", _MODE_CASES
)
def test_mode_graph_has_exactly_the_eleven_documented_sublevels(
    loader, order, root_id, leaf_id, mode, function_prompt
):
    graph = loader()
    ids = {n.id for n in graph.nodes}
    assert ids == set(order)
    assert len(graph.nodes) == 11


@pytest.mark.parametrize(
    "loader, order, root_id, leaf_id, mode, function_prompt", _MODE_CASES
)
def test_mode_graph_is_a_true_dag_no_cycles(
    loader, order, root_id, leaf_id, mode, function_prompt
):
    graph = loader()
    graph.validate()
    graph.topological_order()


@pytest.mark.parametrize(
    "loader, order, root_id, leaf_id, mode, function_prompt", _MODE_CASES
)
def test_mode_graph_edges_are_exactly_the_strict_ordinal_chain(
    loader, order, root_id, leaf_id, mode, function_prompt
):
    graph = loader()
    actual = {(e.src, e.dst) for e in graph.edges}
    expected = set(zip(order, order[1:]))
    assert actual == expected
    assert all(e.type == "precedes" for e in graph.edges)


@pytest.mark.parametrize(
    "loader, order, root_id, leaf_id, mode, function_prompt", _MODE_CASES
)
def test_mode_graph_topological_order_matches_documented_sequence(
    loader, order, root_id, leaf_id, mode, function_prompt
):
    graph = loader()
    assert graph.topological_order() == order


@pytest.mark.parametrize(
    "loader, order, root_id, leaf_id, mode, function_prompt", _MODE_CASES
)
def test_mode_graph_root_and_leaf(
    loader, order, root_id, leaf_id, mode, function_prompt
):
    graph = loader()
    dsts = {e.dst for e in graph.edges}
    srcs = {e.src for e in graph.edges}
    node_ids = {n.id for n in graph.nodes}
    assert node_ids - dsts == {root_id}
    assert node_ids - srcs == {leaf_id}


@pytest.mark.parametrize(
    "loader, order, root_id, leaf_id, mode, function_prompt", _MODE_CASES
)
def test_mode_graph_every_node_shares_the_same_mode_and_function(
    loader, order, root_id, leaf_id, mode, function_prompt
):
    graph = loader()
    for node in graph.nodes:
        assert node.facts["mode"] == mode
        assert node.facts["function_prompt"] == function_prompt


@pytest.mark.parametrize(
    "loader, order, root_id, leaf_id, mode, function_prompt", _MODE_CASES
)
def test_mode_graph_no_target_language_is_asserted_anywhere(
    loader, order, root_id, leaf_id, mode, function_prompt
):
    graph = loader()
    for node in graph.nodes:
        assert node.domain == "foreign-language"
        blob = " ".join(str(v) for v in node.facts.values()).lower()
        for language in ("spanish", "french", "japanese", "mandarin", "german"):
            assert language not in blob


def test_interpretive_content_actually_escalates_not_just_labels():
    graph = load_actfl_interpretive_graph()
    novice_low = graph.by_id("actfl-can-do:interpretive:novice-low").facts["performance_indicator"]
    distinguished = graph.by_id("actfl-can-do:interpretive:distinguished").facts["performance_indicator"]
    assert "gestures" in novice_low
    assert "memorized" in novice_low
    assert "gestures" not in distinguished
    assert "sophisticated" in distinguished


def test_presentational_content_actually_escalates_not_just_labels():
    graph = load_actfl_presentational_graph()
    novice_low = graph.by_id("actfl-can-do:presentational:novice-low").facts["performance_indicator"]
    distinguished = graph.by_id("actfl-can-do:presentational:distinguished").facts["performance_indicator"]
    assert "gestures" in novice_low
    assert "memorized" in novice_low
    assert "culturally nuanced" in distinguished


# ---------------------------------------------------------------------------
# teach-8xw.49: Intercultural Communication -- only 5 major levels in the
# source (not 11 sublevels), two dimensions (Investigation/Interaction).
# ---------------------------------------------------------------------------

def test_intercultural_has_exactly_the_five_documented_levels():
    graph = load_actfl_intercultural_graph()
    ids = {n.id for n in graph.nodes}
    assert ids == set(INTERCULTURAL_LEVEL_ORDER)
    assert len(graph.nodes) == 5


def test_intercultural_is_a_true_dag_no_cycles():
    graph = load_actfl_intercultural_graph()
    graph.validate()
    graph.topological_order()


def test_intercultural_edges_are_exactly_the_strict_ordinal_chain():
    graph = load_actfl_intercultural_graph()
    actual = {(e.src, e.dst) for e in graph.edges}
    expected = set(zip(INTERCULTURAL_LEVEL_ORDER, INTERCULTURAL_LEVEL_ORDER[1:]))
    assert actual == expected
    assert all(e.type == "precedes" for e in graph.edges)
    assert len(graph.edges) == 4


def test_intercultural_novice_is_the_sole_root_and_distinguished_the_sole_leaf():
    graph = load_actfl_intercultural_graph()
    dsts = {e.dst for e in graph.edges}
    srcs = {e.src for e in graph.edges}
    node_ids = {n.id for n in graph.nodes}
    assert node_ids - dsts == {"actfl-can-do:intercultural:novice"}
    assert node_ids - srcs == {"actfl-can-do:intercultural:distinguished"}


def test_intercultural_dimension_prompts_are_constant_across_levels():
    """Investigation and Interaction each have one function prompt that
    applies at every level -- confirm all five nodes carry the identical
    string, not five independently-transcribed near-duplicates."""
    graph = load_actfl_intercultural_graph()
    investigation_prompts = {n.facts["investigation_prompt"] for n in graph.nodes}
    interaction_prompts = {n.facts["interaction_prompt"] for n in graph.nodes}
    assert len(investigation_prompts) == 1
    assert len(interaction_prompts) == 1


def test_intercultural_content_actually_escalates_not_just_labels():
    graph = load_actfl_intercultural_graph()
    novice = graph.by_id("actfl-can-do:intercultural:novice")
    distinguished = graph.by_id("actfl-can-do:intercultural:distinguished")
    assert "limited level" in novice.facts["interaction_benchmark"]
    assert "objectively evaluate" in distinguished.facts["investigation_benchmark"]
    assert "mediate and bridge" in distinguished.facts["interaction_benchmark"]


def test_intercultural_no_target_language_is_asserted_anywhere():
    graph = load_actfl_intercultural_graph()
    for node in graph.nodes:
        assert node.domain == "foreign-language"
        blob = " ".join(str(v) for v in node.facts.values()).lower()
        for language in ("spanish", "french", "japanese", "mandarin", "german"):
            assert language not in blob


# ---------------------------------------------------------------------------
# teach-8xw.49: cross-mode independence -- the four graphs are genuinely
# parallel (disjoint node ids), not accidentally merged or overlapping.
# ---------------------------------------------------------------------------

def test_no_node_id_collisions_across_the_four_mode_graphs():
    interpersonal = load_actfl_can_do_graph()
    interpretive = load_actfl_interpretive_graph()
    presentational = load_actfl_presentational_graph()
    intercultural = load_actfl_intercultural_graph()

    all_ids = [
        node.id
        for graph in (interpersonal, interpretive, presentational, intercultural)
        for node in graph.nodes
    ]
    assert len(all_ids) == len(set(all_ids))
    assert len(all_ids) == 11 + 11 + 11 + 5


def test_new_mode_self_checks_pass():
    _self_check_interpretive()
    _self_check_presentational()
    _self_check_intercultural()
    _self_check_no_cross_mode_collisions()
