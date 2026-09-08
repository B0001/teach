"""Producer stage: the Dummit & Foote prerequisite chain (teach-dye).

Why this exists separately from `va_math_sol_graph`: the epic's acceptance
test (teach-8xw.15) is "teach Dummit & Foote to a learner interested in James
Bond." The SOL graph is K-8; undergraduate group theory is nowhere in it, and
stretching grade-band nodes to cover cosets would have been the silent
reinterpretation teach-8xw.15's own description warns against. So this is a
second, small, hand-authored graph in the same domain-agnostic engine
(`teach.concept_graph`) -- no new types, no parallel traversal code.

EDGE PROVENANCE -- the important difference from va_math_sol_graph

`va_math_sol_graph` derives its 40 edges from a mechanical rule (grade N
precedes grade N+1 within a strand) and says so, because VDOE publishes no
reachable progression document. Its edges are an *inference about ordering*.

The edges here are a different and stronger kind of claim, and the rule is
narrow enough to be checked by hand:

    An edge src -> dst exists only when dst's definition cannot be stated
    without using a term src defines.

That is a content dependency readable off the definitions themselves, not an
ordering read off a table of contents. Concretely: "a subgroup is a subset of
a group that is itself a group under the same operation" cannot be stated
without "group", so 1.1 -> 2.1. "A coset is the set gH for a subgroup H"
cannot be stated without "subgroup", so 2.1 -> 3.1.

EDGES DELIBERATELY NOT ASSERTED

Printing order is not dependency, and this is where a plausible-looking graph
would quietly start lying:

  0.3 -> 1.1  D&F introduces Z/nZ (0.3) before groups (1.1) and uses it as a
              motivating example. But the *definition* of a group does not
              mention Z/nZ; a reader who never saw 0.3 can still state the
              group axioms. Example-of is not prerequisite-for. Omitted.
  0.1 -> 0.2  Divisibility ("a divides b if b = ac for some c") needs no set
              or function language. 0.2 is a root here, which looks odd next
              to a section numbered 0.2 and is nonetheless correct.
  2.3 -> 3.2  D&F proves Lagrange after cyclic groups, and cyclic groups are
              the standard source of examples for it. Lagrange's statement
              (|H| divides |G|) needs subgroups and cosets, not generators.
              Omitted -- this is the edge most likely to be wrongly asserted
              from memory of the chapter order.
  1.6 -> 2.1  teach-25o: chapter 1 (homomorphisms, 1.6) prints before chapter
              2 (subgroups, 2.1). The subgroup criterion never mentions a map
              between groups; a reader who has never seen a homomorphism can
              still state it. Omitted.
  3.2 -> 3.3  teach-25o: 3.2 (Lagrange) immediately precedes 3.3 (isomorphism
              theorems) and some courses use Lagrange to prove corollaries of
              the isomorphism theorems. But the First Isomorphism Theorem's
              own statement needs a homomorphism, its kernel, and a quotient
              group -- not "|H| divides |G|". Omitted for the same reason as
              2.3 -> 3.2: proof order is not definitional need.

The self-check below asserts these six stay absent, so a later well-meaning
edit that "completes" the chain fails loudly instead of silently widening
what this graph claims.

Target node is 3.2 (Lagrange), chosen to line up with `teach.math_facts`,
whose two verified SourceFacts are D&F 3.2 Proposition 7 and 3.2 Theorem 8.
teach-25o added 1.6 (homomorphisms) and 3.3 (isomorphism theorems) past that
target so Proposition 7 (kernel of a homomorphism is normal in the domain) is
reachable from a traversal; 3.2 remains the target used by teach-8xw.15's
acceptance test.
"""
from __future__ import annotations

from teach.concept_graph import ConceptGraph, ConceptNode, PrerequisiteEdge

DOMAIN = "math"
TARGET_NODE_ID = "dummit-foote:3.2-lagrange-theorem"

_NODES = (
    ConceptNode(
        id="dummit-foote:0.1-sets-and-functions",
        domain=DOMAIN,
        label="Sets and Functions",
        standard_ref="Dummit & Foote, 3rd ed., section 0.1",
        facts={
            "section": "0.1",
            "key_terms": ("set", "function", "domain", "codomain", "injective",
                          "surjective", "bijective", "image", "fiber",
                          "cartesian product", "equivalence relation",
                          "equivalence class", "partition"),
            "definition": (
                "A function f from A to B assigns to each element of the "
                "domain A exactly one element of the codomain B. It is "
                "injective when distinct inputs have distinct images, "
                "surjective when every element of B is an image, and "
                "bijective when both."
            ),
        },
    ),
    ConceptNode(
        id="dummit-foote:0.2-integers",
        domain=DOMAIN,
        label="Properties of the Integers",
        standard_ref="Dummit & Foote, 3rd ed., section 0.2",
        facts={
            "section": "0.2",
            "key_terms": ("divisibility", "divides", "division algorithm",
                          "greatest common divisor", "relatively prime",
                          "Euclidean algorithm", "prime", "quotient",
                          "remainder"),
            "definition": (
                "An integer a divides b when b = ac for some integer c. The "
                "division algorithm writes any b as qa + r with remainder r "
                "smaller than a, which is what makes the Euclidean algorithm "
                "for the greatest common divisor terminate."
            ),
        },
    ),
    ConceptNode(
        id="dummit-foote:0.3-integers-mod-n",
        domain=DOMAIN,
        label="Z/nZ: The Integers Modulo n",
        standard_ref="Dummit & Foote, 3rd ed., section 0.3",
        facts={
            "section": "0.3",
            "key_terms": ("congruence", "congruent modulo", "residue class",
                          "congruence class", "modular arithmetic",
                          "well defined", "representative"),
            "definition": (
                "Congruence modulo n is an equivalence relation on the "
                "integers; its equivalence classes are the congruence "
                "classes, and Z/nZ is the set of those classes with addition "
                "and multiplication induced from the integers."
            ),
        },
    ),
    ConceptNode(
        id="dummit-foote:1.1-groups",
        domain=DOMAIN,
        label="Binary Operations and the Group Axioms",
        standard_ref="Dummit & Foote, 3rd ed., section 1.1",
        facts={
            "section": "1.1",
            "key_terms": ("binary operation", "group", "associative",
                          "identity", "inverse", "abelian", "commutative",
                          "closure", "order of a group"),
            "definition": (
                "A binary operation on a set G is a function from G cross G "
                "to G. A group is a set with an associative binary operation "
                "having an identity element, in which every element has an "
                "inverse. The group is abelian when the operation commutes."
            ),
        },
    ),
    ConceptNode(
        id="dummit-foote:1.3-symmetric-groups",
        domain=DOMAIN,
        label="Symmetric Groups",
        standard_ref="Dummit & Foote, 3rd ed., section 1.3",
        facts={
            "section": "1.3",
            "key_terms": ("permutation", "symmetric group", "cycle",
                          "cycle decomposition", "transposition",
                          "composition", "disjoint cycles"),
            "definition": (
                "A permutation of a set is a bijection from that set to "
                "itself. The symmetric group S_n is the group of all "
                "permutations of n symbols under composition, written in "
                "cycle notation."
            ),
        },
    ),
    ConceptNode(
        id="dummit-foote:1.6-homomorphisms",
        domain=DOMAIN,
        label="Group Homomorphisms and Isomorphisms",
        standard_ref="Dummit & Foote, 3rd ed., section 1.6",
        facts={
            "section": "1.6",
            "key_terms": ("homomorphism", "isomorphism", "isomorphic",
                          "kernel", "image", "structure preserving",
                          "well defined map"),
            "definition": (
                "A homomorphism phi from a group G to a group G prime is a "
                "map satisfying phi(xy) = phi(x)phi(y) for all x, y in G. "
                "It is an isomorphism when phi is also a bijection, in which "
                "case G and G prime are called isomorphic. The kernel of "
                "phi is the set of elements of G mapped to the identity of "
                "G prime."
            ),
        },
    ),
    ConceptNode(
        id="dummit-foote:2.1-subgroups",
        domain=DOMAIN,
        label="Subgroups and the Subgroup Criterion",
        standard_ref="Dummit & Foote, 3rd ed., section 2.1",
        facts={
            "section": "2.1",
            "key_terms": ("subgroup", "subgroup criterion", "trivial subgroup",
                          "proper subgroup", "closed under inverses",
                          "nonempty subset"),
            "definition": (
                "A subgroup is a subset of a group that is itself a group "
                "under the same operation. The subgroup criterion: a "
                "nonempty subset H is a subgroup exactly when it is closed "
                "under the operation and under taking inverses."
            ),
        },
    ),
    ConceptNode(
        id="dummit-foote:2.3-cyclic-groups",
        domain=DOMAIN,
        label="Cyclic Groups and Cyclic Subgroups",
        standard_ref="Dummit & Foote, 3rd ed., section 2.3",
        facts={
            "section": "2.3",
            "key_terms": ("cyclic", "generator", "generated by",
                          "order of an element", "infinite cyclic"),
            "definition": (
                "A cyclic group is one generated by a single element; the "
                "order of an element is the least positive power of it "
                "equal to the identity, and equals the size of the cyclic "
                "subgroup it generates."
            ),
        },
    ),
    ConceptNode(
        id="dummit-foote:3.1-cosets",
        domain=DOMAIN,
        label="Cosets and Normal Subgroups",
        standard_ref="Dummit & Foote, 3rd ed., section 3.1",
        facts={
            "section": "3.1",
            "key_terms": ("coset", "left coset", "right coset",
                          "normal subgroup", "conjugation", "conjugate",
                          "quotient group", "factor group"),
            "definition": (
                "For a subgroup H of G and g in G, the left coset gH is the "
                "set of products gh. H is normal when every conjugate gHg "
                "inverse equals H, which is exactly the condition making the "
                "cosets into a quotient group."
            ),
        },
    ),
    ConceptNode(
        id=TARGET_NODE_ID,
        domain=DOMAIN,
        label="Lagrange's Theorem",
        standard_ref="Dummit & Foote, 3rd ed., section 3.2, Theorem 8",
        facts={
            "section": "3.2",
            "key_terms": ("Lagrange", "index", "order divides",
                          "partition into cosets", "finite group",
                          "equal size cosets"),
            "definition": (
                "Lagrange's Theorem: if G is a finite group and H is a "
                "subgroup, then the order of H divides the order of G, and "
                "the index is the number of left cosets. The proof is that "
                "the cosets partition G into blocks of equal size."
            ),
            "fact_topics": ("lagrange-order-divides",),
        },
    ),
    ConceptNode(
        id="dummit-foote:3.3-isomorphism-theorems",
        domain=DOMAIN,
        label="The Isomorphism Theorems",
        standard_ref="Dummit & Foote, 3rd ed., section 3.3",
        facts={
            "section": "3.3",
            "key_terms": ("isomorphism theorem", "first isomorphism theorem",
                          "natural map", "correspondence", "kernel", "image"),
            "definition": (
                "The First Isomorphism Theorem: if phi is a homomorphism "
                "from G to G prime, then the kernel of phi is normal in G, "
                "and the quotient group G modulo the kernel is isomorphic "
                "to the image of phi."
            ),
            "fact_topics": ("kernel-normal-subgroup",),
        },
    ),
)

# Content dependencies only -- see EDGE PROVENANCE. Kept as a transitive
# reduction: 1.1 -> 2.1 -> 2.3 is recorded, 1.1 -> 2.3 is not, because the
# engine's topological_order already respects the composite.
_EDGES = (
    PrerequisiteEdge("dummit-foote:0.1-sets-and-functions",
                     "dummit-foote:0.3-integers-mod-n"),
    PrerequisiteEdge("dummit-foote:0.2-integers",
                     "dummit-foote:0.3-integers-mod-n"),
    PrerequisiteEdge("dummit-foote:0.1-sets-and-functions",
                     "dummit-foote:1.1-groups"),
    PrerequisiteEdge("dummit-foote:0.1-sets-and-functions",
                     "dummit-foote:1.3-symmetric-groups"),
    PrerequisiteEdge("dummit-foote:1.1-groups",
                     "dummit-foote:1.3-symmetric-groups"),
    PrerequisiteEdge("dummit-foote:0.1-sets-and-functions",
                     "dummit-foote:1.6-homomorphisms"),
    PrerequisiteEdge("dummit-foote:1.1-groups",
                     "dummit-foote:1.6-homomorphisms"),
    PrerequisiteEdge("dummit-foote:1.1-groups",
                     "dummit-foote:2.1-subgroups"),
    PrerequisiteEdge("dummit-foote:2.1-subgroups",
                     "dummit-foote:2.3-cyclic-groups"),
    PrerequisiteEdge("dummit-foote:2.1-subgroups",
                     "dummit-foote:3.1-cosets"),
    PrerequisiteEdge("dummit-foote:3.1-cosets",
                     TARGET_NODE_ID),
    PrerequisiteEdge("dummit-foote:1.6-homomorphisms",
                     "dummit-foote:3.3-isomorphism-theorems"),
    PrerequisiteEdge("dummit-foote:3.1-cosets",
                     "dummit-foote:3.3-isomorphism-theorems"),
)

# Asserted absent by the self-check and by tests. See EDGES DELIBERATELY NOT
# ASSERTED -- each is a plausible edge that chapter order suggests and the
# definitions do not support.
NON_EDGES = (
    ("dummit-foote:0.3-integers-mod-n", "dummit-foote:1.1-groups"),
    ("dummit-foote:0.1-sets-and-functions", "dummit-foote:0.2-integers"),
    ("dummit-foote:2.3-cyclic-groups", TARGET_NODE_ID),
    ("dummit-foote:1.3-symmetric-groups", TARGET_NODE_ID),
    # teach-25o: 1.6 (chapter 1) prints before 2.1 (chapter 2), which reads
    # as an ordering claim. But the subgroup criterion ("a nonempty subset
    # closed under the operation and inverses") never mentions a map between
    # groups; a reader who has never seen a homomorphism can still state it.
    ("dummit-foote:1.6-homomorphisms", "dummit-foote:2.1-subgroups"),
    # teach-25o: 3.2 immediately precedes 3.3 in the book and Lagrange is
    # used to prove corollaries of the isomorphism theorems in some courses,
    # but the First Isomorphism Theorem's own statement (G/ker(phi) is
    # isomorphic to the image) needs a homomorphism, its kernel, and a
    # quotient group -- not "|H| divides |G|". Omitted for the same reason
    # 2.3 -> 3.2 is omitted above: proof order is not definitional need.
    (TARGET_NODE_ID, "dummit-foote:3.3-isomorphism-theorems"),
)


def load_dummit_foote_graph() -> ConceptGraph:
    """The D&F chain as a validated ConceptGraph. Raises GraphError if the
    node/edge tables above were edited into an inconsistent state."""
    graph = ConceptGraph(nodes=_NODES, edges=_EDGES)
    graph.validate()
    return graph


def prerequisite_closure(graph: ConceptGraph, node_id: str) -> frozenset[str]:
    """Every node that must be established before `node_id`, transitively.

    This is what the acceptance test needs to ask "were the prerequisites
    really established?" without the checker having to walk edges itself.
    """
    incoming: dict[str, list[str]] = {}
    for edge in graph.edges:
        incoming.setdefault(edge.dst, []).append(edge.src)

    seen: set[str] = set()
    stack = list(incoming.get(node_id, ()))
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(incoming.get(current, ()))
    return frozenset(seen)


def _self_check() -> None:
    graph = load_dummit_foote_graph()
    assert len(graph.nodes) == 11, len(graph.nodes)
    assert len(graph.edges) == 13, len(graph.edges)

    # Structure: validate() already ran inside the loader, so a cycle or a
    # dangling endpoint would have raised before reaching here.
    order = graph.topological_order()
    assert len(order) == 11

    # The chain actually orders the way the mathematics does.
    position = {node_id: i for i, node_id in enumerate(order)}
    for earlier, later in (
        ("dummit-foote:0.1-sets-and-functions", "dummit-foote:1.1-groups"),
        ("dummit-foote:1.1-groups", "dummit-foote:2.1-subgroups"),
        ("dummit-foote:2.1-subgroups", "dummit-foote:3.1-cosets"),
        ("dummit-foote:3.1-cosets", TARGET_NODE_ID),
        ("dummit-foote:0.1-sets-and-functions", "dummit-foote:1.6-homomorphisms"),
        ("dummit-foote:1.1-groups", "dummit-foote:1.6-homomorphisms"),
        ("dummit-foote:1.6-homomorphisms", "dummit-foote:3.3-isomorphism-theorems"),
        ("dummit-foote:3.1-cosets", "dummit-foote:3.3-isomorphism-theorems"),
    ):
        assert position[earlier] < position[later], (earlier, later)

    # Lagrange depends on exactly the definitions its statement uses.
    closure = prerequisite_closure(graph, TARGET_NODE_ID)
    assert closure == {
        "dummit-foote:3.1-cosets",
        "dummit-foote:2.1-subgroups",
        "dummit-foote:1.1-groups",
        "dummit-foote:0.1-sets-and-functions",
    }, sorted(closure)

    # The isomorphism theorems depend on homomorphisms/kernels and on
    # quotient groups (via cosets/normal subgroups) -- not on Lagrange, and
    # not on the cyclic/symmetric-group side branches.
    iso_closure = prerequisite_closure(graph, "dummit-foote:3.3-isomorphism-theorems")
    assert iso_closure == {
        "dummit-foote:1.6-homomorphisms",
        "dummit-foote:3.1-cosets",
        "dummit-foote:2.1-subgroups",
        "dummit-foote:1.1-groups",
        "dummit-foote:0.1-sets-and-functions",
    }, sorted(iso_closure)
    assert TARGET_NODE_ID not in iso_closure

    # The deliberate omissions stay omitted. This is the assertion that fails
    # if someone later "completes" the graph from chapter order.
    present = {(e.src, e.dst) for e in graph.edges}
    for non_edge in NON_EDGES:
        assert non_edge not in present, f"non-edge asserted: {non_edge}"
    # Cyclic groups and symmetric groups are genuinely off the Lagrange path.
    assert "dummit-foote:2.3-cyclic-groups" not in closure
    assert "dummit-foote:1.3-symmetric-groups" not in closure

    # teach-25o: Proposition 7 (kernel of a homomorphism is normal in the
    # domain) is now reachable -- it requires both 1.6 (kernel) and 3.1
    # (normal subgroup), and 3.3 is where the graph states it.
    assert "dummit-foote:1.6-homomorphisms" in iso_closure
    assert "dummit-foote:3.1-cosets" in iso_closure

    # The two nodes carrying fact_topics match teach.math_facts' real topics.
    topics = {t for n in graph.nodes for t in n.facts.get("fact_topics", ())}
    assert topics == {"kernel-normal-subgroup", "lagrange-order-divides"}, topics

    print("dummit_foote_graph self-check OK "
          f"({len(graph.nodes)} nodes, {len(graph.edges)} edges)")


if __name__ == "__main__":
    _self_check()
