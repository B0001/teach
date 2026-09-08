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
Recall that a subgroup H is a nonempty subset closed under the operation and
under inverses. Bond takes any agent g and forms the left coset gH. The
cosets partition the roster into equal blocks, so the order of H divides the
order of G. That is Lagrange theorem, with the index counting the blocks.
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


def test_unsignposted_prerequisites_abstain_rather_than_guess():
    """BOND_LESSON leans on subgroup/coset with no 'recall'-style phrase.
    The checker reports nothing rather than inferring -- and that is the
    known limitation tracked by teach-20c: a lesson that silently assumes
    a prerequisite is indistinguishable here from one that assumes none."""
    result = recover_from_lesson_text(BOND_LESSON, load_dummit_foote_graph())
    assert result.assumed_prerequisite_ids == ()


def test_signposted_prerequisites_are_recovered():
    result = recover_from_lesson_text(SIGNPOSTED_LESSON, load_dummit_foote_graph())
    assert result.taught_node_id == TARGET_NODE_ID
    assert "dummit-foote:3.1-cosets" in result.assumed_prerequisite_ids
