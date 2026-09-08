"""teach-dye: the D&F chain, and that the blind checker can consume it."""
import pytest

from teach.concept_graph import GraphError
from teach.concept_recovery import recover_from_lesson_text
from teach.dummit_foote_graph import (
    NON_EDGES,
    TARGET_NODE_ID,
    load_dummit_foote_graph,
    prerequisite_closure,
    _self_check,
)

# A lesson in the epic's actual test framing, written to use the prerequisite
# vocabulary WITHOUT signposting it -- the harder case for the checker.
BOND_LESSON = """
Bond has been handed a finite roster of MI6 field agents. Call that whole
roster G, a group under the operation of composing assignments. Inside it
sits a smaller unit, Q Branch: a nonempty subset closed under the operation
and under taking inverses, which makes it a subgroup H of G.

Pick any agent g. The left coset gH is the set of products gh for h in Q
Branch. Every one of these cosets has the same size as Q Branch itself, and
no agent belongs to two of them, so the cosets partition the roster into
equal blocks.

If the roster has order |G| and Q Branch has order |H|, the number of blocks
is the index. That forces |H| to divide |G|. This is Lagrange theorem: the
order of a subgroup divides the order of a finite group.
"""

SIGNPOSTED_LESSON = """
Recall that the left coset gH is the set of products gh, and these cosets
partition the group into equal blocks. Bond takes Q Branch as the subgroup H
and any agent g, and forms the left coset gH the same way. The order of H
divides the order of G, so this is Lagrange theorem, with the index counting
the blocks.
"""


def test_self_check_passes():
    _self_check()


def test_graph_validates_and_orders():
    graph = load_dummit_foote_graph()
    graph.validate()
    order = graph.topological_order()
    position = {n: i for i, n in enumerate(order)}
    assert position["dummit-foote:1.1-groups"] < position["dummit-foote:2.1-subgroups"]
    assert position["dummit-foote:3.1-cosets"] < position[TARGET_NODE_ID]


def test_lagrange_closure_is_exactly_the_definitional_chain():
    graph = load_dummit_foote_graph()
    assert prerequisite_closure(graph, TARGET_NODE_ID) == {
        "dummit-foote:3.1-cosets",
        "dummit-foote:2.1-subgroups",
        "dummit-foote:1.1-groups",
        "dummit-foote:0.1-sets-and-functions",
    }


def test_isomorphism_theorems_closure_excludes_lagrange():
    """teach-25o: the First Isomorphism Theorem needs homomorphisms/kernels
    (1.6) and quotient groups (reached through cosets, 3.1) -- not Lagrange's
    theorem, even though 3.2 prints immediately before 3.3 in the book."""
    graph = load_dummit_foote_graph()
    assert prerequisite_closure(graph, "dummit-foote:3.3-isomorphism-theorems") == {
        "dummit-foote:1.6-homomorphisms",
        "dummit-foote:3.1-cosets",
        "dummit-foote:2.1-subgroups",
        "dummit-foote:1.1-groups",
        "dummit-foote:0.1-sets-and-functions",
    }


def test_kernel_normal_subgroup_fact_is_reachable():
    """teach-25o's whole point: teach.math_facts' kernel-normal-subgroup
    SourceFact (D&F 3.2 Prop 7) must attach to some node in this graph, not
    sit unreferenced. Before this bead there was no homomorphism node for it
    to attach to at all."""
    graph = load_dummit_foote_graph()
    carriers = [
        n.id for n in graph.nodes if "kernel-normal-subgroup" in n.facts.get("fact_topics", ())
    ]
    assert carriers == ["dummit-foote:3.3-isomorphism-theorems"]


@pytest.mark.parametrize("src,dst", NON_EDGES)
def test_chapter_order_edges_stay_unasserted(src, dst):
    """These are the edges D&F's printing order suggests and its definitions
    do not support. Fails loudly if someone 'completes' the chain."""
    graph = load_dummit_foote_graph()
    assert (src, dst) not in {(e.src, e.dst) for e in graph.edges}


def test_roots_have_no_prerequisites():
    graph = load_dummit_foote_graph()
    for root in ("dummit-foote:0.1-sets-and-functions", "dummit-foote:0.2-integers"):
        assert prerequisite_closure(graph, root) == frozenset()


def test_cycle_is_rejected_not_silently_ordered():
    """The detector has to actually fire -- an assertion never seen failing
    is not verified."""
    from teach.concept_graph import ConceptGraph, PrerequisiteEdge

    graph = load_dummit_foote_graph()
    looped = ConceptGraph(
        nodes=graph.nodes,
        edges=graph.edges + (PrerequisiteEdge(TARGET_NODE_ID, "dummit-foote:1.1-groups"),),
    )
    with pytest.raises(GraphError):
        looped.validate()


def test_checker_recovers_lagrange_from_bond_framing():
    """The acceptance-test shape: the checker sees only lesson text -- no
    target node, no traversal -- and must name the concept itself."""
    result = recover_from_lesson_text(BOND_LESSON, load_dummit_foote_graph())
    assert result.taught_node_id == TARGET_NODE_ID


def test_unsignposted_prerequisites_flagged_as_own_category():
    """BOND_LESSON leans on subgroup/coset vocabulary throughout with no
    'recall'-style phrase anywhere. teach-20c: this must not land in
    assumed_prerequisite_ids (no signpost -- that field requires one), but
    it must also not collapse into the same empty result a lesson that
    assumes nothing would produce. It is a third, distinct outcome:
    unsignposted use of a direct prerequisite's distinctive vocabulary."""
    result = recover_from_lesson_text(BOND_LESSON, load_dummit_foote_graph())
    assert result.assumed_prerequisite_ids == ()
    assert result.unsignposted_prerequisite_ids == ("dummit-foote:3.1-cosets",)


def test_no_signal_at_all_is_still_distinct_from_unsignposted_use():
    """The other half of teach-20c's split: a lesson that teaches Lagrange
    using the theorem's own vocabulary (order, index, divides, finite,
    blocks) without leaning on coset-specific words at all gets empty
    results on *both* fields -- genuinely no recoverable signal, not
    silent-but-detectable use of the prerequisite. Contrast with
    test_unsignposted_prerequisites_flagged_as_own_category, whose BOND_LESSON
    fixture actually uses coset vocabulary and must NOT abstain the same
    way."""
    text = (
        "This is Lagrange theorem. For any finite group, the order of a "
        "certain part always divides the total order of the group. That "
        "part cuts the group into blocks of equal size, and the number of "
        "blocks is called the index. This is what the proof establishes."
    )
    result = recover_from_lesson_text(text, load_dummit_foote_graph())
    assert result.taught_node_id == TARGET_NODE_ID
    assert result.assumed_prerequisite_ids == ()
    assert result.unsignposted_prerequisite_ids == ()


def test_signposted_prerequisites_are_recovered():
    result = recover_from_lesson_text(SIGNPOSTED_LESSON, load_dummit_foote_graph())
    assert result.taught_node_id == TARGET_NODE_ID
    assert "dummit-foote:3.1-cosets" in result.assumed_prerequisite_ids
    # Signposted, so it must not also be reported as unsignposted -- the two
    # categories are mutually exclusive per node (teach-20c).
    assert result.unsignposted_prerequisite_ids == ()
