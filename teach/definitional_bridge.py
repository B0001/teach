"""The bridge between the foundational layer and the algebraic one
(teach-b5k.4), and the unified graph it completes.

WHY THIS EXISTS INSTEAD OF THE LLM BRIDGE

teach-b5k.2 asked a local model to propose these edges. It produced 127
relations over 240 pairs, and teach-b5k.3's independent checker refused all
127 -- zero survived. So the unified graph had no edges at all between its two
halves: "the bridged dataset" would have been two disconnected components.

That zero was a fact about the producer, not about the mathematics. The model
never proposed the edges that are actually there, and the five it came closest
on were wrong: it asserted "Sets generalizes Lagrange's Theorem" and returned
my own prompt rubric back as its reasoning. Full measurement in
`teach/data/semantic_bridge_candidates.json` and
`teach/data/bridge_verdicts.json`; both are kept, because a producer that
failed is evidence, and deleting it would leave the graph looking as though
this bridge had always been derived this way.

These edges are DEFINITIONAL, derived by the same rule every other edge in
this repo is held to and adjudicated the same way -- NOT LLM-inferred. Anything
emitting this graph must say so per edge rather than let a reader assume a
language model established them. `EVIDENCE` is the field that carries it.

HOW THEY WERE DERIVED

1. A mechanical scan proposed candidates: 22 of the 240 foundation/algebra
   pairs in which a term the foundational node defines occurs as a whole word
   in the algebraic node's definition. Inflected forms were tried too, since
   "truth table" vs the term "truth tables" had already cost a real match
   elsewhere in this repo.
2. Twelve independent adjudicators (one per algebraic destination) ruled on
   every candidate against the definitional rule, each required to quote the
   sentence and to state what the matched word MEANS there.
3. Independent skeptics then tried to refute every accepted edge.
4. Survivors were transitively reduced against the edges the graph already
   had, so no bridge edge asserts a dependency a traversal already gets.

22 candidates -> 7 rejected at adjudication -> 4 refuted by skeptics -> 11
accepted -> 5 dropped as transitive -> 6 edges.

THE TRAP THE SCAN COULD NOT SEE, AND THE ADJUDICATION CAUGHT EVERY TIME

Six of the seven rejections are one word: "domain". Levin's `functions` node
defines a function's domain; Judson's ring chapters say "integral domain",
a commutative ring with no zero divisors. Same string, unrelated concepts. A
term match cannot tell them apart, and taking the scan at face value would
have wired function theory into four ring-theory nodes on a pun. Every
adjudicator flagged it as polysemy unprompted-by-the-answer, having been
warned the trap existed.

The four skeptic refutations are subtler and worth keeping visible: Judson's
own Preliminaries chapter DEFINES "function", "one-to-one" and "onto" (they
are in its own key_terms), so it does not depend on Levin's nodes for them --
the two books simply define the same notions independently. And "set" occurs
in Judson's polynomial-ring section exactly once, inside a naming convention
("we will denote the set of all polynomials ... by R[x]"), which is not
load-bearing.

WHAT DOES NOT BRIDGE, AND WHY THAT IS THE HONEST ANSWER

Nine of the twelve foundational nodes have no bridge edge at all: statements,
propositional-logic, predicates-and-quantifiers, deduction-rules,
set-operations, direct-proof, proof-by-contrapositive, proof-by-contradiction,
mathematical-induction. Only `sets`, `functions` and `function-properties`
reach the algebra.

That is not a gap to be filled in later by relaxing the rule. Judson's
DEFINITIONS do not use propositional logic or proof technique -- a group is a
set with an operation, stated without a single quantifier symbol or a word
about contradiction. Logic and proof method are how one WORKS with those
definitions, not vocabulary the definitions are built from, and this repo's
edge rule is definitional on purpose. A methodological prerequisite is a real
relationship and this graph does not currently have a relation type for it;
inventing one by overloading `precedes` would be exactly the silent
reinterpretation the rule exists to prevent.

Judson's own ch. 1-2 (`sets-and-equivalence-relations`, `the-division-
algorithm`) also stay roots, for the same reason: Judson defines that material
himself rather than importing it.
"""
from __future__ import annotations

from teach.concept_graph import ConceptGraph, PrerequisiteEdge
from teach.judson_algebra_graph import load_judson_full_graph
from teach.levin_foundations_graph import load_levin_foundations_graph

#: How every edge in this module was established. Emitters must carry this
#: rather than let a consumer assume the LLM stage produced them.
EVIDENCE = "definitional-rule-adjudicated"

#: (src, dst, required_term, the sentence in dst's definition that uses it)
BRIDGE_EDGES = (
    ("levin-dmoi:sets", "judson:3.2-definitions-and-examples", "set",
     "A group (G, .) is a set G together with a binary operation satisfying: "
     "the operation is associative; there is an identity element e..."),
    ("levin-dmoi:functions", "judson:5.1-definitions-and-notation", "bijection",
     "A permutation of a set S is a bijection from S to itself."),
    ("levin-dmoi:function-properties", "judson:5.1-definitions-and-notation",
     "bijection", "A permutation of a set S is a bijection from S to itself."),
    ("levin-dmoi:function-properties", "judson:9.1-definition-and-examples",
     "bijective",
     "Two groups (G, .) and (H, *) are isomorphic if there exists a bijective "
     "map phi: G -> H such that phi(g1 . g2) = phi(g1) * phi(g2)..."),
    ("levin-dmoi:functions", "judson:16.3-ring-homomorphisms-and-ideals",
     "one-to-one / onto",
     "If phi : R -> S is a one-to-one and onto homomorphism, then phi is "
     "called an isomorphism of rings."),
    ("levin-dmoi:function-properties", "judson:16.3-ring-homomorphisms-and-ideals",
     "one-to-one / onto",
     "If phi : R -> S is a one-to-one and onto homomorphism, then phi is "
     "called an isomorphism of rings."),
)

#: Accepted by adjudication AND by the skeptic, then dropped because the graph
#: already reaches dst from src. Kept because "true but redundant" is a
#: different fact from "rejected", and a later worker re-deriving the bridge
#: should not have to re-litigate them.
TRANSITIVELY_REDUNDANT = (
    ("levin-dmoi:sets", "judson:5.1-definitions-and-notation", "set"),
    ("levin-dmoi:sets", "judson:11.1-group-homomorphisms", "set"),
    ("levin-dmoi:sets", "judson:16.1-rings", "set"),
    ("levin-dmoi:sets", "judson:16.3-ring-homomorphisms-and-ideals", "set"),
    ("levin-dmoi:functions", "judson:18.2-factorization-in-integral-domains",
     "function"),
)

#: (src, dst, ground). An absent edge is invisible; without this a later worker
#: cannot tell a dependency that was considered and rejected from one missed.
REFUSED_BRIDGE_EDGES = (
    # -- the "domain" polysemy, six times over --
    ("levin-dmoi:functions", "judson:16.1-rings",
     "POLYSEMY. The only lexical match is 'domain', which in Judson occurs "
     "solely inside the compound 'integral domain' -- a commutative ring with "
     "no zero divisors, not the input set of a function. Judson defines a ring "
     "via two binary operations and axioms on elements, never via a function."),
    ("levin-dmoi:function-properties", "judson:16.1-rings",
     "POLYSEMY, same 'integral domain' match. Not one injectivity, surjectivity "
     "or bijectivity term occurs in Judson's ring definition."),
    ("levin-dmoi:functions", "judson:16.2-integral-domains-and-fields",
     "POLYSEMY. 'domain' appears only as the second half of 'integral domain', "
     "naming a species of commutative ring."),
    ("levin-dmoi:function-properties", "judson:16.2-integral-domains-and-fields",
     "POLYSEMY, and incidental: the only shared word is 'domain' bound inside "
     "'integral domain'."),
    ("levin-dmoi:functions", "judson:18.1-fields-of-fractions",
     "POLYSEMY. 'the integral domain D' is an algebraic structure, not a "
     "function's domain."),
    ("levin-dmoi:function-properties", "judson:18.1-fields-of-fractions",
     "POLYSEMY, same 'integral domain D' match."),
    ("levin-dmoi:function-properties",
     "judson:18.2-factorization-in-integral-domains",
     "None of the terms this node introduces -- injective, surjective, "
     "bijection, image, codomain -- occurs in dst's definition at all."),
    # -- refuted by the skeptics --
    ("levin-dmoi:functions", "judson:1.2-sets-and-equivalence-relations",
     "'function' is not vocabulary judson:1.2 BORROWS, it is that node's own "
     "definiendum -- it appears in its own key_terms. Judson defines the notion "
     "himself ('A function f from X to Y assigns to each element of X exactly "
     "one element of Y'). The two books define the same thing independently; "
     "that is not a dependency."),
    ("levin-dmoi:function-properties", "judson:1.2-sets-and-equivalence-relations",
     "Same shape, more sharply: 'one-to-one' and 'onto' are both in "
     "judson:1.2's OWN key_terms and are defined in its own sentence."),
    ("levin-dmoi:sets", "judson:4.1-cyclic-subgroups",
     "'set' occurs in the collection sense, but is not load-bearing: the "
     "definition of a cyclic subgroup restates without any of Levin's "
     "vocabulary, given the group notion it already depends on."),
    ("levin-dmoi:sets", "judson:17.1-polynomial-rings",
     "'set' occurs exactly once in the whole node, inside a naming convention "
     "('we will denote the set of all polynomials with coefficients in a ring "
     "R by R[x]'). Every actual definition in the node -- polynomial, "
     "coefficient, degree, leading coefficient -- is stated with no set "
     "vocabulary at all."),
)


def load_unified_graph() -> ConceptGraph:
    """Levin's foundations + Judson's algebra + the definitional bridge.

    32 nodes, 40 edges. Roots are `levin-dmoi:sets`, `levin-dmoi:statements`,
    and Judson's own two preliminaries chapters, which he defines himself
    rather than importing -- see the module docstring.
    """
    foundations = load_levin_foundations_graph()
    algebra = load_judson_full_graph()
    graph = ConceptGraph(
        nodes=foundations.nodes + algebra.nodes,
        edges=foundations.edges + algebra.edges + tuple(
            PrerequisiteEdge(src=src, dst=dst) for src, dst, _t, _q in BRIDGE_EDGES
        ),
    )
    graph.validate()
    return graph


def bridge_edge_records() -> tuple[dict, ...]:
    """The bridge edges with their evidence, for an emitter to serialize."""
    return tuple(
        {"src": src, "dst": dst, "required_term": term, "quote": quote,
         "evidence": EVIDENCE}
        for src, dst, term, quote in BRIDGE_EDGES
    )


def _self_check() -> None:
    graph = load_unified_graph()
    assert len(graph.nodes) == 32, len(graph.nodes)
    assert len(graph.edges) == 40, len(graph.edges)

    order = graph.topological_order()
    for e in graph.edges:
        assert order.index(e.src) < order.index(e.dst)

    has_incoming = {e.dst for e in graph.edges}
    roots = {n.id for n in graph.nodes if n.id not in has_incoming}
    assert roots == {
        "levin-dmoi:sets", "levin-dmoi:statements",
        "judson:1.2-sets-and-equivalence-relations",
        "judson:2.1-the-division-algorithm",
    }, roots

    # The two halves are genuinely joined: some algebraic node is reachable
    # from a foundational one. This is the property the LLM bridge failed to
    # deliver at all.
    asserted = {(e.src, e.dst) for e in graph.edges}
    assert ("levin-dmoi:sets", "judson:3.2-definitions-and-examples") in asserted

    # Refused and transitively-dropped edges must not be asserted.
    for src, dst, _why in REFUSED_BRIDGE_EDGES:
        assert (src, dst) not in asserted, f"refused edge re-asserted: {src} -> {dst}"
    for src, dst, _t in TRANSITIVELY_REDUNDANT:
        assert (src, dst) not in asserted, f"redundant edge asserted: {src} -> {dst}"

    # Every transitively-dropped edge really is redundant: dst reachable from
    # src without it. If this fails, dropping it removed a real dependency.
    from teach.semantic_bridge import redundant_against

    for src, dst, _t in TRANSITIVELY_REDUNDANT:
        assert redundant_against(src, dst, graph.edges), (src, dst)

    # Six of the eleven refusals are the same pun; keep that visible.
    polysemy = [r for r in REFUSED_BRIDGE_EDGES if r[2].startswith("POLYSEMY")]
    assert len(polysemy) == 6, len(polysemy)

    # No foundational logic/proof node bridges, and that is deliberate.
    bridged_sources = {src for src, _d, _t, _q in BRIDGE_EDGES}
    assert bridged_sources == {
        "levin-dmoi:sets", "levin-dmoi:functions", "levin-dmoi:function-properties"
    }, bridged_sources

    print(f"OK: unified graph {len(graph.nodes)} nodes, {len(graph.edges)} edges, "
          f"{len(BRIDGE_EDGES)} definitional bridge edges")
    print(f"    {len(REFUSED_BRIDGE_EDGES)} refused (6 of them the "
          f"'integral domain' pun), {len(TRANSITIVELY_REDUNDANT)} true but redundant")
    print(f"    roots: {', '.join(sorted(roots))}")


if __name__ == "__main__":
    _self_check()
