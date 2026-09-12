"""teach-8xw.52: the VA World Language SOL 2021 overview-grid seed graph
loads, is a true DAG, matches the documented per-strand Novice->Intermediate
->Advanced chain, carries real sourced benchmark text (not placeholders),
and asserts no target language and no id collision with the existing
language-agnostic ACTFL graph -- same structural discipline
test_actfl_can_do_graph.py and test_va_writing_sol_graph.py apply to their
own graphs.
"""
import pytest

from teach.concept_graph import GraphError, PrerequisiteEdge
from teach.actfl_can_do_graph import (
    load_actfl_can_do_graph,
    load_actfl_interpretive_graph,
    load_actfl_presentational_graph,
    load_actfl_intercultural_graph,
)
from teach.va_world_language_sol_graph import (
    DOMAIN,
    LEVEL_ORDER,
    SOURCE,
    STRAND_IDS,
    _node_id,
    _self_check,
    load_va_world_language_sol_graph,
)


def test_self_check_passes():
    _self_check()


def test_has_exactly_the_documented_fifteen_nodes():
    graph = load_va_world_language_sol_graph()
    expected_ids = {
        _node_id(suffix, level) for suffix in STRAND_IDS for level in LEVEL_ORDER
    }
    assert {n.id for n in graph.nodes} == expected_ids
    assert len(graph.nodes) == 15


def test_is_a_true_dag_no_cycles():
    graph = load_va_world_language_sol_graph()
    graph.validate()  # raises GraphError on a cycle; must not raise here
    graph.topological_order()


def test_every_edge_references_a_node_that_exists():
    graph = load_va_world_language_sol_graph()
    node_ids = {n.id for n in graph.nodes}
    assert graph.edges, "expected at least one prerequisite edge"
    for edge in graph.edges:
        assert edge.src in node_ids, f"dangling edge src: {edge.src!r}"
        assert edge.dst in node_ids, f"dangling edge dst: {edge.dst!r}"


def test_edges_are_exactly_the_documented_per_strand_chain():
    """10 edges: 5 strands x 2 consecutive-level gaps (Novice-Intermediate,
    Intermediate-Advanced). Not fewer (a broken chain), not more (a stray
    cross-strand edge implying a dependency the source never states)."""
    graph = load_va_world_language_sol_graph()
    actual = {(e.src, e.dst) for e in graph.edges}
    expected = {
        (_node_id(suffix, earlier), _node_id(suffix, later))
        for suffix in STRAND_IDS
        for earlier, later in zip(LEVEL_ORDER, LEVEL_ORDER[1:])
    }
    assert actual == expected
    assert all(e.type == "precedes" for e in graph.edges)


def test_topological_order_respects_level_sequence_within_each_strand():
    graph = load_va_world_language_sol_graph()
    order = graph.topological_order()
    for suffix in STRAND_IDS:
        ids = [_node_id(suffix, level) for level in LEVEL_ORDER]
        positions = [order.index(i) for i in ids]
        assert positions == sorted(positions), suffix


def test_no_cross_strand_edges():
    """Each strand's 3-node chain is independent -- the source presents the
    five strands as separate axes of the same learner, not a dependency
    chain into each other (same 'independent modes' framing
    actfl_can_do_graph.py documents for its own parallel modes)."""
    graph = load_va_world_language_sol_graph()
    for edge in graph.edges:
        src_strand = edge.src.split(":")[1]
        dst_strand = edge.dst.split(":")[1]
        assert src_strand == dst_strand


def test_node_facts_carry_real_sourced_text_not_placeholders():
    graph = load_va_world_language_sol_graph()
    node = graph.by_id("va-world-language-sol:interpretive:novice")
    assert node.domain == DOMAIN
    assert node.facts["strand_name"] == "INTERPRETIVE Communication"
    assert node.facts["level"] == "Novice"
    joined = " ".join(node.facts["benchmark_statements"]).lower()
    assert "authentic texts" in joined
    assert "overheard or observed conversations" in joined


def test_content_actually_escalates_not_just_labels():
    """Guards against a data error that shuffled labels without shuffling
    text: Novice interpersonal leans on practiced/familiar words and simple
    sentences; Advanced names neither and adds probing questions instead."""
    graph = load_va_world_language_sol_graph()
    novice = graph.by_id("va-world-language-sol:interpersonal:novice")
    advanced = graph.by_id("va-world-language-sol:interpersonal:advanced")
    novice_text = " ".join(novice.facts["benchmark_statements"]).lower()
    advanced_text = " ".join(advanced.facts["benchmark_statements"]).lower()
    assert "simple sentences" in novice_text
    assert "probing questions" not in novice_text
    assert "probing questions" in advanced_text


def test_communicative_literacy_strand_has_three_benchmarks_not_two():
    """Four of the five strands print 2 numbered benchmarks per level;
    Communicative Literacy prints 3 (literacy, interpersonal, presentational
    skills). Pins the real source asymmetry rather than assuming every
    strand is shaped alike."""
    graph = load_va_world_language_sol_graph()
    for level in LEVEL_ORDER:
        literacy = graph.by_id(_node_id("literacy", level))
        assert len(literacy.facts["benchmark_statements"]) == 3
    for suffix in ("intercultural", "interpretive", "interpersonal", "presentational"):
        for level in LEVEL_ORDER:
            node = graph.by_id(_node_id(suffix, level))
            assert len(node.facts["benchmark_statements"]) == 2


def test_no_target_language_is_asserted_anywhere():
    """Same language-agnostic commitment actfl_can_do_graph.py's DECISION
    section records, applied to this second graph -- see this module's own
    DECISION section. Fails loudly if a later edit quietly bolts a language
    name onto the data instead of filing a new bead for it."""
    graph = load_va_world_language_sol_graph()
    for node in graph.nodes:
        assert node.domain == "foreign-language"
        blob = " ".join(node.facts["benchmark_statements"]).lower()
        for language in ("spanish", "french", "japanese", "mandarin", "german"):
            assert language not in blob


def test_source_provenance_is_recorded_not_asserted_from_memory():
    assert "doe.virginia.gov" in SOURCE["document_url"]
    assert "web.archive.org" in SOURCE["wayback_url"]
    assert SOURCE["wayback_snapshot"] in SOURCE["wayback_url"]
    assert "2021" in SOURCE["adopted"]


def test_a_hand_introduced_cycle_is_rejected_not_silently_ordered():
    """Not a property of the shipped data (already tested acyclic above) --
    a regression guard that this domain's loader output still goes through
    concept_graph's real cycle check, not a stub."""
    graph = load_va_world_language_sol_graph()
    cyclic_edges = graph.edges + (
        PrerequisiteEdge(
            src=_node_id("interpretive", "Advanced"),
            dst=_node_id("interpretive", "Novice"),
        ),
    )
    cyclic_graph = graph.__class__(nodes=graph.nodes, edges=cyclic_edges)
    with pytest.raises(GraphError):
        cyclic_graph.topological_order()


def test_no_node_id_collisions_with_actfl_graph():
    """This is a second, VA-specific seed graph within the same
    'foreign-language' domain the existing ACTFL graph already occupies --
    the two must never share a node id."""
    va_ids = {n.id for n in load_va_world_language_sol_graph().nodes}
    actfl_ids = {
        n.id
        for graph in (
            load_actfl_can_do_graph(),
            load_actfl_interpretive_graph(),
            load_actfl_presentational_graph(),
            load_actfl_intercultural_graph(),
        )
        for n in graph.nodes
    }
    assert va_ids.isdisjoint(actfl_ids)
