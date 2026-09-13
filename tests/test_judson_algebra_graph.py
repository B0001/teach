"""teach-8xw.56: the Judson chain, and that the blind checker can consume it."""
import pytest

from teach.concept_graph import GraphError
from teach.concept_recovery import recover_from_lesson_text
from teach.judson_algebra_graph import (
    JUDSON_SOURCE,
    NON_EDGES,
    TARGET_NODE_ID,
    load_judson_algebra_graph,
    prerequisite_closure,
    _self_check,
)
from teach.publish_graph import _hf_license_id, build_dataset_files

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
    graph = load_judson_algebra_graph()
    graph.validate()
    order = graph.topological_order()
    position = {n: i for i, n in enumerate(order)}
    assert position["judson:3.2-definitions-and-examples"] < position["judson:3.3-subgroups"]
    assert position["judson:6.1-cosets"] < position[TARGET_NODE_ID]


def test_lagrange_closure_is_exactly_the_definitional_chain():
    graph = load_judson_algebra_graph()
    assert prerequisite_closure(graph, TARGET_NODE_ID) == {
        "judson:6.1-cosets",
        "judson:3.3-subgroups",
        "judson:3.2-definitions-and-examples",
        "judson:1.2-sets-and-equivalence-relations",
    }


def test_homomorphisms_closure_excludes_lagrange_and_isomorphisms():
    """teach-8xw.56: Judson's kernel-is-normal theorem needs normal subgroups
    (ch. 10, reached through cosets, ch. 6) -- not Lagrange's theorem, and
    not isomorphisms (ch. 9), even though Judson prints isomorphisms before
    homomorphisms. See judson_algebra_graph.py's EDGE PROVENANCE section for
    why neither omission is a printing-order artifact left unchecked."""
    graph = load_judson_algebra_graph()
    assert prerequisite_closure(graph, "judson:11.1-group-homomorphisms") == {
        "judson:10.1-factor-groups-and-normal-subgroups",
        "judson:6.1-cosets",
        "judson:3.3-subgroups",
        "judson:3.2-definitions-and-examples",
        "judson:1.2-sets-and-equivalence-relations",
    }


def test_isomorphisms_closure_is_independent_of_homomorphisms_and_cosets():
    """Judson defines an isomorphism directly (its own bijective
    structure-preserving map), never in terms of a homomorphism already on
    the page -- so isomorphisms' closure is just the group axioms."""
    graph = load_judson_algebra_graph()
    assert prerequisite_closure(graph, "judson:9.1-definition-and-examples") == {
        "judson:3.2-definitions-and-examples",
        "judson:1.2-sets-and-equivalence-relations",
    }


def test_kernel_normal_subgroup_fact_is_reachable():
    """teach-8xw.56: teach.math_facts' kernel-normal-subgroup SourceFact
    (Judson, ch. "Homomorphisms", sec. "Group Homomorphisms") must attach to
    some node in this graph, not sit unreferenced."""
    graph = load_judson_algebra_graph()
    carriers = [
        n.id for n in graph.nodes if "kernel-normal-subgroup" in n.facts.get("fact_topics", ())
    ]
    assert carriers == ["judson:11.1-group-homomorphisms"]


@pytest.mark.parametrize("src,dst", NON_EDGES)
def test_chapter_order_edges_stay_unasserted(src, dst):
    """These are the edges Judson's printing order suggests and its
    definitions do not support. Fails loudly if someone 'completes' the
    chain."""
    graph = load_judson_algebra_graph()
    assert (src, dst) not in {(e.src, e.dst) for e in graph.edges}


def test_roots_have_no_prerequisites():
    graph = load_judson_algebra_graph()
    for root in ("judson:1.2-sets-and-equivalence-relations", "judson:2.1-the-division-algorithm"):
        assert prerequisite_closure(graph, root) == frozenset()


def test_cycle_is_rejected_not_silently_ordered():
    """The detector has to actually fire -- an assertion never seen failing
    is not verified."""
    from teach.concept_graph import ConceptGraph, PrerequisiteEdge

    graph = load_judson_algebra_graph()
    looped = ConceptGraph(
        nodes=graph.nodes,
        edges=graph.edges + (PrerequisiteEdge(TARGET_NODE_ID, "judson:3.2-definitions-and-examples"),),
    )
    with pytest.raises(GraphError):
        looped.validate()


def test_checker_recovers_lagrange_from_bond_framing():
    """The acceptance-test shape: the checker sees only lesson text -- no
    target node, no traversal -- and must name the concept itself."""
    result = recover_from_lesson_text(BOND_LESSON, load_judson_algebra_graph())
    assert result.taught_node_id == TARGET_NODE_ID


def test_unsignposted_prerequisites_flagged_as_own_category():
    """BOND_LESSON leans on subgroup/coset vocabulary throughout with no
    'recall'-style phrase anywhere. teach-20c: this must not land in
    assumed_prerequisite_ids (no signpost -- that field requires one), but
    it must also not collapse into the same empty result a lesson that
    assumes nothing would produce. It is a third, distinct outcome:
    unsignposted use of a direct prerequisite's distinctive vocabulary."""
    result = recover_from_lesson_text(BOND_LESSON, load_judson_algebra_graph())
    assert result.assumed_prerequisite_ids == ()
    assert result.unsignposted_prerequisite_ids == ("judson:6.1-cosets",)


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
    result = recover_from_lesson_text(text, load_judson_algebra_graph())
    assert result.taught_node_id == TARGET_NODE_ID
    assert result.assumed_prerequisite_ids == ()
    assert result.unsignposted_prerequisite_ids == ()


def test_signposted_prerequisites_are_recovered():
    result = recover_from_lesson_text(SIGNPOSTED_LESSON, load_judson_algebra_graph())
    assert result.taught_node_id == TARGET_NODE_ID
    assert "judson:6.1-cosets" in result.assumed_prerequisite_ids
    # Signposted, so it must not also be reported as unsignposted -- the two
    # categories are mutually exclusive per node (teach-20c).
    assert result.unsignposted_prerequisite_ids == ()


# teach-8xw.57: GFDL is copyleft. A derivative of Judson's book must carry the
# license identifier AND the notice/copyright as text -- an identifier alone
# does not satisfy it. These pin JUDSON_SOURCE to both requirements so a
# future publish (blocked on teach-8xw.55's per-graph repo layout) inherits
# correct metadata rather than a fresh licensing decision.


def test_judson_source_license_resolves_to_hf_gfdl_not_other():
    assert _hf_license_id(JUDSON_SOURCE["license"]) == "gfdl"


def test_judson_source_attribution_carries_the_gfdl_notice_and_copyright():
    assert "Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer" in (
        JUDSON_SOURCE["attribution"]
    )
    assert "GNU Free Documentation License" in JUDSON_SOURCE["attribution"]


def test_judson_source_notice_survives_into_the_published_dataset_card():
    """Not just a license id in the front matter -- the notice and copyright
    text itself must appear in the artifact a consumer actually reads."""
    files = build_dataset_files(
        load_judson_algebra_graph(), source=JUDSON_SOURCE, repo_id="example/judson"
    )
    readme = files["README.md"].decode()
    assert "license: gfdl" in readme
    assert "Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer" in readme
    manifest_source = files["manifest.json"].decode()
    assert "Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer" in (
        manifest_source
    )
