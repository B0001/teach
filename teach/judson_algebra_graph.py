"""Producer stage: the Judson prerequisite chain (teach-8xw.56).

Formerly `teach/dummit_foote_graph.py`. DECISION (repo owner, 2026-09-12): the
abstract-algebra test case moved from Dummit & Foote to Thomas W. Judson's
*Abstract Algebra: Theory and Applications* -- D&F is a copyrighted commercial
textbook, so a learner cannot open a cited page without buying it, and a graph
derived from its structure cannot be published. Judson covers the same group
theory and is licensed GNU FDL 1.3 or later (Copyright (C) 1997-2015 Thomas W.
Judson, Robert A. Beezer; no Invariant Sections, no Cover Texts -- read from
`COPYING` at github.com/twjudson/aata, not from the GitHub API's incorrect
NOASSERTION label). Source of record is `src/*.xml` (PreTeXt) in that
repository; the book's own rendered domains do not resolve from this sandbox.

Why this exists separately from `va_math_sol_graph`: the epic's acceptance
test (teach-8xw.15) is "teach [the abstract-algebra text] to a learner
interested in James Bond." The SOL graph is K-8; undergraduate group theory is
nowhere in it, and stretching grade-band nodes to cover cosets would have been
the silent reinterpretation teach-8xw.15's own description warns against. So
this is a second, small, hand-authored graph in the same domain-agnostic
engine (`teach.concept_graph`) -- no new types, no parallel traversal code.

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
without "group", so groups -> subgroups. "A coset is the set gH for a
subgroup H" cannot be stated without "subgroup", so subgroups -> cosets.

THE STRUCTURE GENUINELY CHANGES FROM THE D&F VERSION OF THIS GRAPH

teach-8xw.56 re-derived every edge from Judson's own PreTeXt source
(`src/*.xml`) rather than porting and relabeling the old D&F edge list --
porting would have asserted D&F's dependency structure while citing Judson, a
silent reinterpretation undetectable from node labels alone. Judson's own
chapter organization differs from D&F's in exactly the two ways that make this
non-trivial:

  - D&F bundles homomorphisms and isomorphisms into one section (1.6). Judson
    splits them into separate chapters, and -- unlike a same-book split that
    just separates adjacent material -- puts Isomorphisms (ch. 9) BEFORE
    Homomorphisms (ch. 11). Reading isomorph.xml directly confirms Judson's
    isomorphism definition never uses the word "homomorphism": an isomorphism
    is defined as its own bijective structure-preserving map, not as a
    special case of a homomorphism already on the page. So this graph has NO
    edge between them in either direction (see EDGES DELIBERATELY NOT
    ASSERTED) -- they are independent chains that happen to share the group
    axioms as a common ancestor.
  - D&F bundles cosets and normal subgroups into one section (3.1). Judson
    has Cosets in ch. 6 and Normal Subgroups in ch. 10, three chapters apart.
    Reading normal.xml directly confirms Judson's normal-subgroup definition
    (gH = Hg for every g) is stated in terms of cosets, so cosets ->
    normal-subgroups is a real content edge, not a printing-order artifact.

The one content dependency this restructuring changes at the target's
downstream neighbor: `teach.math_facts`'s kernel-normal-subgroup fact is cited
from Judson's Homomorphisms chapter ("the kernel of phi is a normal subgroup
of G"), and *that* statement needs "normal subgroup" -- Judson's own term for
it, defined in ch. 10 -- not Lagrange's theorem and not isomorphisms. So in
this graph homomorphisms depends on normal-subgroups (via cosets), not on
Lagrange's theorem and not on isomorphisms, which is a different dependency
shape than D&F's bundled-section version had any occasion to distinguish.

EDGES DELIBERATELY NOT ASSERTED

Printing order is not dependency, and this is where a plausible-looking graph
would quietly start lying:

  sets-and-functions -> integers        Judson's Preliminaries chapter covers
              set/function/equivalence-relation language (ch 1) before The
              Integers (ch 2), and the integers chapter's induction proofs
              are typically phrased using set language. But "an integer a
              divides b when b = ac for some integer c" needs no set or
              function language to state. Omitted, same as the D&F version
              of this graph omitted the analogous 0.1 -> 0.2 edge.
  cyclic-groups -> lagranges-theorem     Judson proves Lagrange's Theorem (ch
              6) after Cyclic Groups (ch 4) and cyclic groups are a standard
              source of examples for it. Lagrange's statement ("the number of
              elements in H must divide the number of elements in G") needs
              subgroups and cosets, not generators or element order. Omitted
              -- this is the edge most likely to be wrongly asserted from
              memory of the chapter order.
  permutation-groups -> lagranges-theorem   Same shape: permutation groups
              (ch 5) print immediately before cosets/Lagrange (ch 6) and
              symmetric groups are the standard example, but Lagrange's
              statement doesn't mention permutations. Omitted.
  isomorphisms -> homomorphisms          Judson prints Isomorphisms (ch 9)
              before Homomorphisms (ch 11), which reads as an ordering claim.
              But isomorph.xml's definition of an isomorphism never uses the
              word "homomorphism" (it is defined directly, as its own
              bijective structure-preserving map) -- a reader who has never
              seen a homomorphism can still state what an isomorphism is.
              Omitted; this is the direct analogue of the D&F version's
              1.6 -> 2.1 omission (a later-numbered dependency that chapter
              order suggests and the definitions don't support), except here
              it runs in the *opposite* print direction, which is exactly why
              it has to be checked from the source and not inferred from "the
              D&F graph didn't have this edge either."
  lagranges-theorem -> homomorphisms     Both are reachable from cosets, and
              Lagrange (ch 6) prints well before Homomorphisms (ch 11), but
              the theorem this graph's target node states ("|H| divides
              |G|") never appears in homomorph.xml's kernel-is-normal
              theorem or its proof. Omitted.
  homomorphisms -> isomorphisms          The converse of the omitted
              isomorphisms -> homomorphisms edge above, checked separately
              for the same reason: homomorph.xml's own definitions never cite
              isomorph.xml's. Neither direction holds; they are independent
              chains sharing only the group axioms as a common ancestor.

The self-check below asserts these six stay absent, so a later well-meaning
edit that "completes" the chain fails loudly instead of silently widening
what this graph claims.

Target node is Lagrange's Theorem (ch. 6, "Lagrange's Theorem" section),
chosen to line up with `teach.math_facts`, whose lagrange-order-divides
SourceFact is cited from exactly that section (`xml:id="cosets-theorem-
lagrange"`). Homomorphisms is included past that target so
kernel-normal-subgroup (the other verified SourceFact) is reachable from a
traversal; Normal Subgroups and Isomorphisms are included because
Homomorphisms' own re-derived dependency chain runs through them. Lagrange's
Theorem remains the target used by teach-8xw.15's acceptance test.
"""
from __future__ import annotations

import json
from pathlib import Path

from teach.concept_graph import ConceptGraph, ConceptNode, PrerequisiteEdge

DOMAIN = "math"
TARGET_NODE_ID = "judson:6.2-lagranges-theorem"

# teach-8xw.57: the `source` block a future publish of this graph must carry.
# Unlike va_math_sol_graph's CC BY 4.0 source, GFDL is copyleft -- the license
# and the copyright notice have to travel with the derivative, not just an
# identifier, so `attribution` below is the verbatim text of `COPYING` at
# github.com/twjudson/aata (fetched and read directly, not recalled), and
# `license` is the exact GNU FDL 1.3 URL that `publish_graph._hf_license_id`
# maps to HF's "gfdl" identifier -- confirmed by this module's self-check.
# `publish_graph.py`'s "## Source" block and `manifest.json` both serialize
# this dict verbatim, so the notice ships wherever this dict does.
#
# This is metadata only: nothing in this repo publishes the Judson graph yet
# (teach-8xw.55's per-graph repo layout does not exist), and teach-8xw.57
# says not to until it does. Defining the source block now means .55 has no
# further licensing decision left to make when it wires this graph in.
JUDSON_SOURCE = {
    "provider": "Thomas W. Judson and Robert A. Beezer, "
    "Abstract Algebra: Theory and Applications",
    "author": "Thomas W. Judson, Robert A. Beezer",
    "license": "https://www.gnu.org/licenses/fdl-1.3.html",
    "attribution": (
        "Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer. "
        "Permission is granted to copy, distribute and/or modify this "
        "document under the terms of the GNU Free Documentation License, "
        "Version 1.3 or any later version published by the Free Software "
        "Foundation; with no Invariant Sections, no Front-Cover Texts, and "
        "no Back-Cover Texts. A copy of the license is included in the "
        "section entitled \"GNU Free Documentation License\"."
    ),
    "retrieved_via": "https://github.com/twjudson/aata (src/*.xml PreTeXt "
    "source; COPYING for the license notice above)",
}

_NODES = (
    ConceptNode(
        id="judson:1.2-sets-and-equivalence-relations",
        domain=DOMAIN,
        label="Sets and Equivalence Relations",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, ch. "Preliminaries", '
                     'sec. "Sets and Equivalence Relations"',
        facts={
            "chapter": 1,
            "section": "Sets and Equivalence Relations",
            "key_terms": ("set", "function", "domain", "range", "one-to-one",
                          "onto", "bijective", "image", "cartesian product",
                          "equivalence relation", "equivalence class",
                          "partition", "reflexive", "symmetric", "transitive"),
            "definition": (
                "A function f from X to Y assigns to each element of X "
                "exactly one element of Y. It is one-to-one when distinct "
                "inputs have distinct outputs, onto when every element of Y "
                "is an output. An equivalence relation on a set X is a "
                "relation that is reflexive, symmetric, and transitive; its "
                "equivalence classes partition X."
            ),
        },
    ),
    ConceptNode(
        id="judson:2.1-the-division-algorithm",
        domain=DOMAIN,
        label="The Division Algorithm",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, ch. "The Integers", '
                     'sec. "The Division Algorithm"',
        facts={
            "chapter": 2,
            "section": "The Division Algorithm",
            "key_terms": ("divides", "divisor", "division algorithm",
                          "greatest common divisor", "relatively prime",
                          "Euclidean algorithm", "prime", "quotient",
                          "remainder", "existence", "uniqueness"),
            # teach-59u: the previous text ("writes any integer b as b = aq +
            # r ... which is what makes the Euclidean algorithm ... terminate")
            # dropped the theorem's own defining property -- Judson states
            # the division algorithm as an EXISTENCE-AND-UNIQUENESS theorem
            # ("there exist unique integers q and r"; the proof itself is
            # titled "This is a perfect example of the existence-and-
            # uniqueness type of proof", integers.xml). Phrased below as
            # "uniquely determined" rather than the bare word "unique" on
            # purpose: "unique" already sits at document-frequency 3 across
            # this graph (judson:16.1, judson:18.2, judson:21.1) before this
            # edit, and judson:18.1's own teach-59u extraction fix
            # legitimately adds a 4th (still <= _MAX_DOCUMENT_FREQ); adding
            # a 5th use here would push "unique" over that threshold and
            # silently strip it from all five nodes' distinctive vocabulary
            # -- confirmed by measurement (a previously-passing generalization
            # test broke) before landing on this phrasing. "Uniquely" and
            # "uniqueness" are unclaimed elsewhere in the graph and carry the
            # same meaning without that collision.
            "definition": (
                "An integer a divides an integer b if there is an integer c "
                "such that b = ac. The division algorithm states that for "
                "integers a and b with b > 0, there is a quotient q and a "
                "remainder r, uniquely determined, such that a = bq + r "
                "with 0 <= r < b -- an existence-and-uniqueness theorem: "
                "both that such q and r exist, and that they are the only "
                "ones that work, are what make the Euclidean algorithm for "
                "the greatest common divisor of two integers terminate with "
                "a single, well-defined answer. Two integers are relatively "
                "prime when their greatest common divisor is 1, and a prime "
                "is an integer greater than 1 with no positive divisor "
                "other than 1 and itself."
            ),
        },
    ),
    ConceptNode(
        id="judson:3.2-definitions-and-examples",
        domain=DOMAIN,
        label="Definitions and Examples of Groups",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, ch. "Groups", '
                     'sec. "Definitions and Examples"',
        facts={
            "chapter": 3,
            "section": "Definitions and Examples",
            "key_terms": ("binary operation", "group", "associative",
                          "identity", "inverse", "abelian", "commutative",
                          "order of a group"),
            "definition": (
                "A group (G, .) is a set G together with a binary operation "
                "satisfying: the operation is associative; there is an "
                "identity element e with eg = ge = g for all g; and every "
                "element g has an inverse g^-1 with g g^-1 = g^-1 g = e. The "
                "group is abelian when the operation commutes."
            ),
        },
    ),
    ConceptNode(
        id="judson:3.3-subgroups",
        domain=DOMAIN,
        label="Subgroups",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, ch. "Groups", '
                     'sec. "Subgroups"',
        facts={
            "chapter": 3,
            "section": "Subgroups",
            "key_terms": ("subgroup", "subgroup criterion", "trivial subgroup",
                          "proper subgroup", "closed under inverses",
                          "nonempty subset"),
            "definition": (
                "A subgroup H of a group G is a subset of G that is itself a "
                "group under G's operation. A nonempty subset H of G is a "
                "subgroup exactly when H is closed under the operation and "
                "under taking inverses."
            ),
        },
    ),
    ConceptNode(
        id="judson:4.1-cyclic-subgroups",
        domain=DOMAIN,
        label="Cyclic Subgroups",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, ch. "Cyclic Groups", '
                     'sec. "Cyclic Subgroups"',
        facts={
            "chapter": 4,
            "section": "Cyclic Subgroups",
            "key_terms": ("cyclic group", "generator", "generated by",
                          "order of an element", "infinite cyclic"),
            "definition": (
                "A group G is cyclic if there is an element g in G such that "
                "G is the set of all powers of g; such a g is a generator of "
                "G. The order of an element g is the smallest positive n "
                "with g^n = e, and equals the size of the cyclic subgroup g "
                "generates."
            ),
        },
    ),
    ConceptNode(
        id="judson:5.1-definitions-and-notation",
        domain=DOMAIN,
        label="Permutation Groups: Definitions and Notation",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, ch. "Permutation Groups", '
                     'sec. "Definitions and Notation"',
        facts={
            "chapter": 5,
            "section": "Definitions and Notation",
            "key_terms": ("permutation", "symmetric group", "cycle",
                          "cycle notation", "transposition", "composition",
                          "disjoint cycles", "permutation group"),
            "definition": (
                "A permutation of a set S is a bijection from S to itself. "
                "The symmetric group S_n is the group of all permutations of "
                "{1, ..., n} under composition; a permutation group is a "
                "subgroup of some symmetric group."
            ),
        },
    ),
    ConceptNode(
        id="judson:6.1-cosets",
        domain=DOMAIN,
        label="Cosets",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, '
                     'ch. "Cosets and Lagrange\'s Theorem", sec. "Cosets"',
        facts={
            "chapter": 6,
            "section": "Cosets",
            "key_terms": ("coset", "left coset", "right coset",
                          "index of a subgroup"),
            "definition": (
                "Let G be a group and H a subgroup of G. Suppose g is in G. "
                "Then gH = {gh : h in H} is a left coset of H in G, and "
                "Hg = {hg : h in H} is a right coset of H in G."
            ),
        },
    ),
    ConceptNode(
        id=TARGET_NODE_ID,
        domain=DOMAIN,
        label="Lagrange's Theorem",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, '
                     'ch. "Cosets and Lagrange\'s Theorem", sec. "Lagrange\'s Theorem" '
                     '(xml:id="cosets-theorem-lagrange")',
        facts={
            "chapter": 6,
            "section": "Lagrange's Theorem",
            "key_terms": ("Lagrange", "index", "order divides",
                          "partition into cosets", "finite group",
                          "equal size cosets"),
            "definition": (
                "Lagrange's Theorem: let G be a finite group and let H be a "
                "subgroup of G. Then the number of elements in H must divide "
                "the number of elements in G, i.e. |H| divides |G|. The proof "
                "is that the left cosets of H partition G into blocks all of "
                "size |H|."
            ),
            "fact_topics": ("lagrange-order-divides",),
        },
    ),
    ConceptNode(
        id="judson:9.1-definition-and-examples",
        domain=DOMAIN,
        label="Isomorphisms: Definition and Examples",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, ch. "Isomorphisms", '
                     'sec. "Definition and Examples"',
        facts={
            "chapter": 9,
            "section": "Definition and Examples",
            "key_terms": ("isomorphism", "isomorphic", "structure preserving",
                          "bijective map"),
            "definition": (
                "Two groups (G, .) and (H, *) are isomorphic if there exists "
                "a bijective map phi: G -> H such that phi(g1 . g2) = "
                "phi(g1) * phi(g2) for all g1, g2 in G. Such a phi is called "
                "an isomorphism."
            ),
        },
    ),
    ConceptNode(
        id="judson:10.1-factor-groups-and-normal-subgroups",
        domain=DOMAIN,
        label="Normal Subgroups",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, '
                     'ch. "Normal Subgroups and Factor Groups", '
                     'sec. "Factor Groups and Normal Subgroups"',
        facts={
            "chapter": 10,
            "section": "Factor Groups and Normal Subgroups",
            "key_terms": ("normal subgroup", "conjugate", "factor group",
                          "quotient group"),
            "definition": (
                "A subgroup H of a group G is normal in G if gH = Hg for all "
                "g in G, that is, the left and right cosets of H agree."
            ),
        },
    ),
    ConceptNode(
        id="judson:11.1-group-homomorphisms",
        domain=DOMAIN,
        label="Group Homomorphisms",
        standard_ref='Judson, Abstract Algebra: Theory and Applications, ch. "Homomorphisms", '
                     'sec. "Group Homomorphisms"',
        facts={
            "chapter": 11,
            "section": "Group Homomorphisms",
            "key_terms": ("homomorphism", "kernel", "structure preserving",
                          "normal subgroup", "injective", "image"),
            "definition": (
                "Let G and H be groups. A map phi: G -> H is a homomorphism "
                "if phi(g1 g2) = phi(g1) phi(g2) for all g1, g2 in G. The "
                "kernel of phi is the set of elements of G mapped to the "
                "identity of H. Theorem: the kernel of phi is a normal "
                "subgroup of G. There is no injective homomorphism from "
                "Z_7 to Z_12, since 7 does not divide 12. The image of phi "
                "is the set of all phi(g) for g in G."
            ),
            "fact_topics": ("kernel-normal-subgroup",),
        },
    ),
)

# Content dependencies only -- see EDGE PROVENANCE. Kept as a transitive
# reduction: e.g. groups -> subgroups -> cosets is recorded, groups -> cosets
# is not, because the engine's topological_order already respects the
# composite.
_EDGES = (
    PrerequisiteEdge("judson:1.2-sets-and-equivalence-relations",
                     "judson:3.2-definitions-and-examples"),
    PrerequisiteEdge("judson:1.2-sets-and-equivalence-relations",
                     "judson:5.1-definitions-and-notation"),
    PrerequisiteEdge("judson:3.2-definitions-and-examples",
                     "judson:5.1-definitions-and-notation"),
    PrerequisiteEdge("judson:3.2-definitions-and-examples",
                     "judson:3.3-subgroups"),
    PrerequisiteEdge("judson:3.3-subgroups",
                     "judson:4.1-cyclic-subgroups"),
    PrerequisiteEdge("judson:3.3-subgroups",
                     "judson:6.1-cosets"),
    PrerequisiteEdge("judson:6.1-cosets",
                     TARGET_NODE_ID),
    PrerequisiteEdge("judson:3.2-definitions-and-examples",
                     "judson:9.1-definition-and-examples"),
    PrerequisiteEdge("judson:6.1-cosets",
                     "judson:10.1-factor-groups-and-normal-subgroups"),
    PrerequisiteEdge("judson:3.2-definitions-and-examples",
                     "judson:11.1-group-homomorphisms"),
    PrerequisiteEdge("judson:10.1-factor-groups-and-normal-subgroups",
                     "judson:11.1-group-homomorphisms"),
)

# Asserted absent by the self-check and by tests. See EDGES DELIBERATELY NOT
# ASSERTED -- each is a plausible edge that chapter order suggests and the
# definitions do not support.
NON_EDGES = (
    ("judson:1.2-sets-and-equivalence-relations", "judson:2.1-the-division-algorithm"),
    ("judson:4.1-cyclic-subgroups", TARGET_NODE_ID),
    ("judson:5.1-definitions-and-notation", TARGET_NODE_ID),
    # teach-8xw.56: Judson prints Isomorphisms (ch 9) before Homomorphisms
    # (ch 11), which reads as an ordering claim. isomorph.xml's definition of
    # an isomorphism never uses the word "homomorphism" -- it is defined
    # directly as its own bijective structure-preserving map. A reader who
    # has never seen a homomorphism can still state what an isomorphism is.
    ("judson:9.1-definition-and-examples", "judson:11.1-group-homomorphisms"),
    # teach-8xw.56: both are reachable from cosets and Lagrange (ch 6) prints
    # well before Homomorphisms (ch 11), but homomorph.xml's kernel-is-normal
    # theorem and its proof never state or use "|H| divides |G|".
    (TARGET_NODE_ID, "judson:11.1-group-homomorphisms"),
    # teach-8xw.56: the converse of the omitted isomorphisms -> homomorphisms
    # edge above, checked separately -- homomorph.xml's own definitions never
    # cite isomorph.xml's. Neither direction holds.
    ("judson:11.1-group-homomorphisms", "judson:9.1-definition-and-examples"),
)


# --------------------------------------------------------------------------
# teach-b5k.1: the ring and field half.
#
# The nodes above are hand-authored group theory (teach-8xw.56). The ring and
# field nodes are read out of the PreTeXt source by
# `teach/extract_judson_ring_field.py` into `teach/data/judson_ring_field.json`
# instead, so their text is Judson's verbatim rather than retyped, and each
# carries the (source_file, xml_id, section, file sha256) it came from.
#
# WHY THE TWO HALVES HAVE DIFFERENT PROVENANCE, rather than re-extracting
# everything: `teach.concept_recovery` builds a node's vocabulary by flattening
# every string reachable in `ConceptNode.facts`, so rewriting the existing
# nodes' hand-authored `facts` would change that vocabulary, and with it the
# recovery and abstention outcomes that existing tests pin against this graph.
# That is a real behavioural change wearing the clothes of a refactor. The
# facts SHAPE is identical across both halves (chapter, section, key_terms,
# definition), so nothing downstream can tell them apart; only the provenance
# differs, and this comment is where that is recorded.
_RING_FIELD_DATA_PATH = Path(__file__).parent / "data" / "judson_ring_field.json"


def load_judson_ring_field_data() -> dict:
    """Raw parsed JSON, for callers that want provenance without nodes."""
    with _RING_FIELD_DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _ring_field_nodes() -> tuple[ConceptNode, ...]:
    return tuple(
        ConceptNode(
            id=n["id"],
            domain=DOMAIN,
            label=n["label"],
            standard_ref=n["standard_ref"],
            facts={
                "chapter": n["chapter"],
                "section": n["section"],
                "key_terms": tuple(n["terms"]),
                "definition": n["definition"],
            },
        )
        for n in load_judson_ring_field_data()["nodes"]
    )


# Same rule as the group-theory edges above: src -> dst only when dst's
# definition cannot be stated without a term src defines. Each edge names the
# term and the clause of Judson's own text that carries it.
_RING_FIELD_EDGES = (
    # "A nonempty set R is a ring if it has two closed binary operations" --
    # "binary operation" is defined in the Groups chapter (3.2), so ring
    # theory attaches to group theory here, and on that term. NOT on "abelian
    # group": Judson's remark that the first four axioms make a ring an
    # abelian group under addition is an observation ABOUT the definition, and
    # the definition itself lists the four axioms outright.
    PrerequisiteEdge(src="judson:3.2-definitions-and-examples", dst="judson:16.1-rings"),
    # "If R is a commutative ring and r is a nonzero element in R..."
    PrerequisiteEdge(src="judson:16.1-rings", dst="judson:16.2-integral-domains-and-fields"),
    # "if R and S are rings, then a ring homomorphism is a map phi : R -> S"
    PrerequisiteEdge(src="judson:16.1-rings", dst="judson:16.3-ring-homomorphisms-and-ideals"),
    # "Throughout this chapter we shall assume that R is a commutative ring
    # with identity... is called a polynomial over R"
    PrerequisiteEdge(src="judson:16.1-rings", dst="judson:17.1-polynomial-rings"),
    # "A proper ideal M of a ring R is a maximal ideal of R if..."
    PrerequisiteEdge(src="judson:16.3-ring-homomorphisms-and-ideals",
                     dst="judson:16.4-maximal-and-prime-ideals"),
    # "The field F_D is called the field of fractions... of the integral domain D"
    PrerequisiteEdge(src="judson:16.2-integral-domains-and-fields",
                     dst="judson:18.1-fields-of-fractions"),
    # "Let D be an integral domain. A nonzero element p in D that is not a
    # unit is said to be irreducible..."
    PrerequisiteEdge(src="judson:16.2-integral-domains-and-fields",
                     dst="judson:18.2-factorization-in-integral-domains"),
    # "An integral domain in which every ideal is principal is called a
    # principal ideal domain" -- "ideal" and "principal ideal" are 16.3's.
    PrerequisiteEdge(src="judson:16.3-ring-homomorphisms-and-ideals",
                     dst="judson:18.2-factorization-in-integral-domains"),
    # "A field E is an extension field of a field F if F is a subfield of E."
    PrerequisiteEdge(src="judson:16.2-integral-domains-and-fields",
                     dst="judson:21.1-extension-fields"),
    # "alpha ... is algebraic over F if f(alpha)=0 for some nonzero polynomial
    # f(x) in F[x]"
    PrerequisiteEdge(src="judson:17.1-polynomial-rings", dst="judson:21.1-extension-fields"),
    # "An extension field E of F is a splitting field of p(x) if..."
    PrerequisiteEdge(src="judson:21.1-extension-fields", dst="judson:21.2-splitting-fields"),
    # "let p(x) = a_0 + a_1 x + ... be a nonconstant polynomial in F[x]"
    PrerequisiteEdge(src="judson:17.1-polynomial-rings", dst="judson:21.2-splitting-fields"),
)

# Ring/field edges considered and refused, in the same spirit as NON_EDGES.
RING_FIELD_NON_EDGES = (
    ("judson:11.1-group-homomorphisms", "judson:16.3-ring-homomorphisms-and-ideals",
     "Judson opens the section with 'In the study of groups, a homomorphism is "
     "a map that preserves the operation of the group. Similarly, a "
     "homomorphism between rings preserves...' -- that is an ANALOGY drawn for "
     "the reader, and the definition that follows is self-contained: 'a ring "
     "homomorphism is a map phi : R -> S satisfying phi(a+b) = phi(a) + phi(b) "
     "and phi(ab) = phi(a)phi(b)'. Nothing in it needs the group-homomorphism "
     "definition. This is the edge most likely to be wrongly asserted here, "
     "because the prose invites it."),
    ("judson:1.2-sets-and-equivalence-relations", "judson:16.1-rings",
     "'A nonempty set R is a ring...' does use 'set', but 1.2 already reaches "
     "16.1 through 3.2. Asserting the transitive edge separately would "
     "double-count one dependency."),
    ("judson:6.2-lagranges-theorem", "judson:16.1-rings",
     "Lagrange prints well before the Rings chapter and is the target node of "
     "this graph's acceptance test, but no clause of the ring axioms mentions "
     "subgroup order or index. Print order is not dependency."),
    ("judson:16.4-maximal-and-prime-ideals", "judson:21.1-extension-fields",
     "Maximal ideals are how one CONSTRUCTS extension fields later in Judson, "
     "but the definition of an extension field ('a field E is an extension "
     "field of a field F if F is a subfield of E') never mentions ideals."),
)


def load_judson_algebra_graph() -> ConceptGraph:
    """The hand-authored group-theory chain (11 nodes) as a validated
    ConceptGraph. Raises GraphError if the node/edge tables above were edited
    into an inconsistent state.

    WHY THIS IS STILL GROUP THEORY ONLY, when teach-b5k.1 added ring and field
    nodes: making the 20-node graph the default measurably degraded
    `teach.concept_recovery`. Measured, not predicted -- three tests flipped,
    including the epic's own acceptance case. On the Bond/Lagrange lesson the
    checker stopped recovering Lagrange's Theorem at all and abstained, with
    `judson:18.2-factorization-in-integral-domains` ranking ABOVE the correct
    node. The ring/field sections carry a lot of generic mathematical
    vocabulary ("divides", "unit", "prime", "element", "identity") that
    overlaps ordinary lesson prose, so adding them dilutes the per-node
    distinctiveness recovery depends on.

    That is a real finding about the checker, filed separately -- not something
    to tune away by editing the test. It fails toward abstention rather than a
    confident wrong answer, which is the safe direction, but the capability is
    genuinely reduced. So the historical contract is preserved here and the
    combined graph is `load_judson_full_graph()`, which is what the Learning
    Commons export (teach-j4n) is built from.
    """
    graph = ConceptGraph(nodes=_NODES, edges=_EDGES)
    graph.validate()
    return graph


def load_judson_full_graph() -> ConceptGraph:
    """Group, ring AND field theory: 20 nodes, 23 edges (teach-b5k.1).

    The ring/field nodes are downstream of the group-theory ones and outside
    the target node's closure, so `prerequisite_closure(graph,
    TARGET_NODE_ID)` is identical to the group-only graph's -- Lagrange's
    Theorem does not acquire ring theory as a prerequisite just because the
    book contains it. The self-check asserts that.

    Read `load_judson_algebra_graph`'s docstring before switching a consumer
    to this: it costs concept_recovery accuracy on this domain.
    """
    graph = ConceptGraph(
        nodes=_NODES + _ring_field_nodes(),
        edges=_EDGES + _RING_FIELD_EDGES,
    )
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
    # The default graph is still the hand-authored group-theory chain; see
    # load_judson_algebra_graph's docstring for why.
    graph = load_judson_algebra_graph()
    assert len(graph.nodes) == 11, len(graph.nodes)
    assert len(graph.edges) == 11, len(graph.edges)

    # 11 group-theory nodes (teach-8xw.56) + 9 extracted ring/field nodes.
    full = load_judson_full_graph()
    assert len(full.nodes) == 20, len(full.nodes)
    assert len(full.edges) == 23, len(full.edges)

    # Adding ring and field theory must NOT change what the acceptance
    # test's target node depends on: Lagrange's Theorem does not acquire ring
    # theory as a prerequisite just because the book contains it.
    assert prerequisite_closure(full, TARGET_NODE_ID) == prerequisite_closure(
        graph, TARGET_NODE_ID
    ), "ring/field nodes leaked into the target node's prerequisite closure"

    # Ring/field structure, read off Judson's own definitions.
    ring_field_ids = {n["id"] for n in load_judson_ring_field_data()["nodes"]}
    assert len(ring_field_ids) == 9, len(ring_field_ids)
    assert "judson:16.1-rings" in ring_field_ids
    assert "judson:21.2-splitting-fields" in ring_field_ids

    by_id = {n.id: n for n in full.nodes}
    # Each ring/field node must actually define its own subject.
    for node_id, needle in (
        ("judson:16.1-rings", "is a ring if it has two closed binary operations"),
        ("judson:16.2-integral-domains-and-fields", "no zero divisors"),
        ("judson:16.3-ring-homomorphisms-and-ideals", "ring homomorphism is a map"),
        ("judson:16.4-maximal-and-prime-ideals", "is a maximal ideal"),
        ("judson:17.1-polynomial-rings", "is called a polynomial over"),
        ("judson:18.1-fields-of-fractions", "field of fractions"),
        ("judson:18.2-factorization-in-integral-domains", "is said to be irreducible"),
        ("judson:21.1-extension-fields", "is an extension field of a field"),
        ("judson:21.2-splitting-fields", "is a splitting field of"),
    ):
        assert needle in by_id[node_id].facts["definition"], node_id

    # Ring theory attaches to group theory on "binary operation", the term the
    # ring definition's first clause actually uses.
    asserted = {(e.src, e.dst) for e in full.edges}
    assert ("judson:3.2-definitions-and-examples", "judson:16.1-rings") in asserted
    assert "binary operation" in by_id["judson:3.2-definitions-and-examples"].facts["key_terms"]

    # Refused ring/field edges stay refused.
    for src, dst, why in RING_FIELD_NON_EDGES:
        assert (src, dst) not in asserted, f"refused edge re-asserted: {src} -> {dst}"
        assert why.strip()

    # Structure: validate() already ran inside the loader, so a cycle or a
    # dangling endpoint would have raised before reaching here.
    assert len(full.topological_order()) == 20
    order = graph.topological_order()
    assert len(order) == 11

    # The chain actually orders the way the mathematics does.
    position = {node_id: i for i, node_id in enumerate(order)}
    for earlier, later in (
        ("judson:1.2-sets-and-equivalence-relations", "judson:3.2-definitions-and-examples"),
        ("judson:3.2-definitions-and-examples", "judson:3.3-subgroups"),
        ("judson:3.3-subgroups", "judson:6.1-cosets"),
        ("judson:6.1-cosets", TARGET_NODE_ID),
        ("judson:3.2-definitions-and-examples", "judson:9.1-definition-and-examples"),
        ("judson:6.1-cosets", "judson:10.1-factor-groups-and-normal-subgroups"),
        ("judson:10.1-factor-groups-and-normal-subgroups", "judson:11.1-group-homomorphisms"),
        ("judson:3.2-definitions-and-examples", "judson:11.1-group-homomorphisms"),
    ):
        assert position[earlier] < position[later], (earlier, later)

    # Ring and field theory order after the group theory they attach to.
    full_position = {node_id: i for i, node_id in enumerate(full.topological_order())}
    for earlier, later in (
        ("judson:3.2-definitions-and-examples", "judson:16.1-rings"),
        ("judson:16.1-rings", "judson:16.2-integral-domains-and-fields"),
        ("judson:16.1-rings", "judson:16.3-ring-homomorphisms-and-ideals"),
        ("judson:16.3-ring-homomorphisms-and-ideals", "judson:16.4-maximal-and-prime-ideals"),
        ("judson:16.1-rings", "judson:17.1-polynomial-rings"),
        ("judson:16.2-integral-domains-and-fields", "judson:18.1-fields-of-fractions"),
        ("judson:16.3-ring-homomorphisms-and-ideals",
         "judson:18.2-factorization-in-integral-domains"),
        ("judson:16.2-integral-domains-and-fields", "judson:21.1-extension-fields"),
        ("judson:17.1-polynomial-rings", "judson:21.1-extension-fields"),
        ("judson:21.1-extension-fields", "judson:21.2-splitting-fields"),
    ):
        assert full_position[earlier] < full_position[later], (earlier, later)

    # Lagrange depends on exactly the definitions its statement uses.
    closure = prerequisite_closure(graph, TARGET_NODE_ID)
    assert closure == {
        "judson:6.1-cosets",
        "judson:3.3-subgroups",
        "judson:3.2-definitions-and-examples",
        "judson:1.2-sets-and-equivalence-relations",
    }, sorted(closure)

    # Homomorphisms depends on normal subgroups (via cosets) and on the group
    # axioms -- not on Lagrange, and not on isomorphisms or the cyclic/
    # permutation-group side branches. This is the shape teach-8xw.56 exists
    # to get right: it is genuinely different from the D&F version, where the
    # analogous node (bundled cosets+normal-subgroups) sat one hop from
    # homomorphisms with no intervening chapter.
    hom_closure = prerequisite_closure(graph, "judson:11.1-group-homomorphisms")
    assert hom_closure == {
        "judson:10.1-factor-groups-and-normal-subgroups",
        "judson:6.1-cosets",
        "judson:3.3-subgroups",
        "judson:3.2-definitions-and-examples",
        "judson:1.2-sets-and-equivalence-relations",
    }, sorted(hom_closure)
    assert TARGET_NODE_ID not in hom_closure
    assert "judson:9.1-definition-and-examples" not in hom_closure

    # Isomorphisms depends only on the group axioms -- confirmed independent
    # of homomorphisms, cosets, and Lagrange (see EDGE PROVENANCE).
    iso_closure = prerequisite_closure(graph, "judson:9.1-definition-and-examples")
    assert iso_closure == {
        "judson:3.2-definitions-and-examples",
        "judson:1.2-sets-and-equivalence-relations",
    }, sorted(iso_closure)

    # The deliberate omissions stay omitted. This is the assertion that fails
    # if someone later "completes" the graph from chapter order.
    present = {(e.src, e.dst) for e in graph.edges}
    for non_edge in NON_EDGES:
        assert non_edge not in present, f"non-edge asserted: {non_edge}"
    # Cyclic groups and permutation groups are genuinely off the Lagrange path.
    assert "judson:4.1-cyclic-subgroups" not in closure
    assert "judson:5.1-definitions-and-notation" not in closure

    # kernel-normal-subgroup is reachable from homomorphisms -- it requires
    # normal-subgroups (via cosets), and homomorphisms is where the graph
    # states it.
    assert "judson:10.1-factor-groups-and-normal-subgroups" in hom_closure

    # The two nodes carrying fact_topics match teach.math_facts' real topics.
    topics = {t for n in graph.nodes for t in n.facts.get("fact_topics", ())}
    assert topics == {"kernel-normal-subgroup", "lagrange-order-divides"}, topics

    # teach-8xw.57: JUDSON_SOURCE's license must resolve to HF's exact "gfdl"
    # identifier, not degrade to "other", and its GFDL notice + copyright must
    # actually survive into a published artifact's text -- a license id alone
    # does not satisfy GFDL's copyleft requirement. Imported here rather than
    # at module scope, matching publish_graph.py's own late-import convention.
    from teach.publish_graph import _hf_license_id, build_dataset_files

    assert _hf_license_id(JUDSON_SOURCE["license"]) == "gfdl", (
        "Judson's GFDL license must map to HF's exact identifier, not 'other'"
    )
    assert "Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer" in (
        JUDSON_SOURCE["attribution"]
    )
    files = build_dataset_files(graph, source=JUDSON_SOURCE, repo_id="example/judson")
    readme = files["README.md"].decode()
    assert "license: gfdl" in readme
    assert "Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer" in readme
    assert "GNU Free Documentation License" in readme

    print("judson_algebra_graph self-check OK "
          f"(group-theory graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges; "
          f"full graph: {len(full.nodes)} nodes, {len(full.edges)} edges, "
          f"+{len(ring_field_ids)} ring/field)")


if __name__ == "__main__":
    _self_check()
