"""Methodological prerequisites: proof technique -> algebra (teach-6xi).

WHY A SECOND RELATION TYPE, AND WHY THE DEFINITIONAL ONE COULD NEVER FIND THESE

`teach.definitional_bridge` asserts an edge only when dst's DEFINITION cannot
be stated without a term src defines. That rule bridged sets and functions into
the algebra and left nine foundational nodes -- the whole logic and proof
half -- connected to nothing. Measured, not assumed: Judson's entire definition
corpus (14,716 characters across all 20 nodes) contains zero occurrences of
"contradiction", "induction", "contrapositive", "tautology", "truth table" or
"converse". Ernst's *An Inquiry-Based Approach to Abstract Algebra* is the
same -- 47 `\\begin{definition}` blocks, 13,119 characters, zero of the first
three. So this is not a defect in either book and not a symptom of picking the
wrong foundational text.

Definitions state invariant properties of algebraic objects. Proof methods are
inference operators applied inside a demonstration. They live in different
elements, so the evidence rule has to look where the operator is actually
used:

    src ->(methodological_prerequisite) dst  when a `<proof>` inside dst's
    section explicitly invokes the method src defines.

`PrerequisiteEdge.type` is an open string precisely so a domain needing a
second relation is not forced to misuse "precedes" (see
`teach.concept_graph`'s docstring). This uses that seam rather than widening
the definitional rule, so a consumer can always tell the two claims apart:
`precedes` means dst's definition needs src; `methodological_prerequisite`
means dst's proofs use src.

WHAT COUNTS AS EVIDENCE, AND WHAT DELIBERATELY DOES NOT

Only methods Judson NAMES in the proof body: "We will prove this theorem by
contradiction", "We will use mathematical induction on the degree of p(x)",
"we will show that the contrapositive of the statement is true". Every match
was read before being trusted; the sampled matches contained no false
positives, and each edge records the proof count and a verbatim excerpt.

Refused, and recorded in `REFUSED_METHODS` rather than left as a silent
absence:

  - quantifier language ("for all" in 29 proofs, "there exists" in 49) and
    "if and only if" (3). These are logical VOCABULARY, not method operators.
    Counting them would repeat the exact error this bead exists to correct --
    matching a word instead of the thing the word does -- and "for all" is
    ubiquitous in mathematical prose.
  - direct proof. There is no positive textual marker for it; its signature is
    the ABSENCE of a named method. Inferring "this proof is a direct proof
    because it does not say otherwise" would manufacture an edge out of
    silence, so `levin-dmoi:direct-proof` gets no edge even though Judson's
    proofs plainly use it constantly. This is the honest gap, not an oversight.
  - deduction-rules, propositional-logic, statements, predicates-and-
    quantifiers, set-operations: no named-method marker exists for any of them.

COVERAGE IS PARTIAL AND THE NUMBER MATTERS

Judson has 207 `<proof>` elements. Only 88 sit in a section this graph models
as a ConceptNode; the other 119 are in chapters with no node (galois 18,
algcodes 12, boolean 12, finite 11, poly's later sections 10, actions 8, sylow
8, struct 6, ...). So these edges are derived from 88 proofs, not 207, and a
method used only in an unmodelled chapter produces no edge at all. That is
exactly what happened to `proof-by-contrapositive`: Judson names it in two
proofs, both in sections this graph does not model (finite.xml "Structure of a
Finite Field" and isomorph.xml "Direct Products"), so it has ZERO edges here
despite genuinely being used in the book.
"""
from __future__ import annotations

import collections
import re

from teach.concept_graph import ConceptGraph, PrerequisiteEdge
from teach.definitional_bridge import load_unified_graph
from teach.judson_algebra_graph import load_judson_full_graph

#: The relation this module asserts. Distinct from "precedes" on purpose.
EDGE_TYPE = "methodological_prerequisite"

#: Chapter number -> source file, read off the `<xi:include>` order in
#: `src/aata.xml` (sets=1 ... galois=23), not recalled. Consistent with the
#: numbering the hand-authored nodes already use (isomorph=9, normal=10,
#: homomorph=11).
CHAPTER_TO_FILE = {
    1: "sets.xml", 2: "integers.xml", 3: "groups.xml", 4: "cyclic.xml",
    5: "permute.xml", 6: "cosets.xml", 7: "crypt.xml", 8: "algcodes.xml",
    9: "isomorph.xml", 10: "normal.xml", 11: "homomorph.xml", 12: "matrix.xml",
    13: "struct.xml", 14: "actions.xml", 15: "sylow.xml", 16: "rings.xml",
    17: "poly.xml", 18: "domains.xml", 19: "boolean.xml", 20: "vect.xml",
    21: "fields.xml", 22: "finite.xml", 23: "galois.xml",
}

#: Foundational node -> the marker that shows its method being invoked.
#: Deliberately narrow: the author naming the technique.
PROOF_METHOD_PATTERNS = {
    "levin-dmoi:proof-by-contradiction": r"contradict",
    "levin-dmoi:mathematical-induction": r"\binduction\b",
    "levin-dmoi:proof-by-contrapositive": r"contrapositive",
}

#: (src, dst, proofs_matched, verbatim excerpt from one of them)
METHODOLOGICAL_EDGES = (
    ('levin-dmoi:mathematical-induction', 'judson:2.1-the-division-algorithm', 1,
     'Uniqueness To show uniqueness we will use induction on $n$. The theorem is certainly true for $n = 2$ since in this case $n$ is prime. Now assume that the'),
    ('levin-dmoi:mathematical-induction', 'judson:21.2-splitting-fields', 2,
     'We will use mathematical induction on the degree of $p(x)$. If $\\deg p(x) = 1$, then $p(x)$ is a linear polynomial and $E = F$. Assume that'),
    ('levin-dmoi:mathematical-induction', 'judson:5.1-definitions-and-notation', 1,
     'We will employ induction on $r$. A transposition cannot be the identity; hence, $r \\gt 1$. If $r=2$, then we are done. Suppose'),
    ('levin-dmoi:proof-by-contradiction', 'judson:16.2-integral-domains-and-fields', 1,
     'either $a1 =0$ or $b1=0$. Hence, the characteristic of $D$ must be less than $n$, which is a contradiction. Therefore, $n$ must be prime.'),
    ('levin-dmoi:proof-by-contradiction', 'judson:18.2-factorization-in-integral-domains', 1,
     '\\rangle$; otherwise, $a$ and $a_1$ would be associates and $b_1$ would be a unit, which would contradict our assumption. Now suppose that $a_1 = a_2 b_2$, where neither $a_2$ nor $b_2$ is a unit. By the same'),
    ('levin-dmoi:proof-by-contradiction', 'judson:2.1-the-division-algorithm', 4,
     'we would have $a - b(q + 1)$ in the set $S$. But then $a - b(q + 1) \\lt a - bq$, which would contradict the fact that $r = a - bq$ is the smallest member of $S$. So $r \\leq b$. Since $0 \\notin S$, $r \\neq b$'),
    ('levin-dmoi:proof-by-contradiction', 'judson:21.1-extension-fields', 1,
     '\\alpha ) s( \\alpha ) = 0$; consequently, either $r( \\alpha )=0$ or $s( \\alpha ) = 0$, which contradicts the fact that $p$ is of minimal degree. Therefore, $p(x)$ must be irreducible.'),
    ('levin-dmoi:proof-by-contradiction', 'judson:9.1-definition-and-examples', 1,
     'the contrary; that is, $a^m = a^n$. In this case $a^{m - n} = e$, where $m - n \\gt 0$, which contradicts the fact that $a$ has infinite order. Our map is onto since any element in $G$ can be written as $a^n$'),
)

#: Foundational nodes that get no methodological edge, and why. An absence is
#: invisible without this.
REFUSED_METHODS = (
    ("levin-dmoi:direct-proof",
     "No positive textual marker exists. Its signature is the ABSENCE of a named "
     "method, and inferring 'this is a direct proof because it does not say "
     "otherwise' would manufacture an edge out of silence. Judson's proofs plainly "
     "use direct proof constantly; this graph cannot evidence it, and says so "
     "rather than asserting it."),
    ("levin-dmoi:proof-by-contrapositive",
     "Judson NAMES this method in exactly 2 proofs, and both are in sections this "
     "graph does not model as nodes (finite.xml 'Structure of a Finite Field' and "
     "isomorph.xml 'Direct Products'). So it has zero edges here despite genuinely "
     "being used in the book -- a coverage limit, not a claim that Judson avoids "
     "contrapositive arguments."),
    ("levin-dmoi:predicates-and-quantifiers",
     "Quantifier language is everywhere in the proofs ('for all' in 29, 'there "
     "exists' in 49) but it is logical VOCABULARY, not a method operator. Counting "
     "it would repeat the error this bead exists to correct: matching a word "
     "instead of the thing the word does."),
    ("levin-dmoi:propositional-logic",
     "'if and only if' appears in 3 proofs; it is a statement form, not an "
     "inference operator invoked by name."),
    ("levin-dmoi:deduction-rules",
     "No named-method marker. Judson never writes 'by modus ponens'."),
    ("levin-dmoi:statements",
     "No named-method marker; it is foundational vocabulary, not a technique."),
    ("levin-dmoi:set-operations",
     "No named-method marker; it is subject matter, not a proof technique."),
)

#: Measured coverage. Recorded so the edges are never read as exhaustive.
TOTAL_PROOFS = 207
PROOFS_IN_MODELLED_SECTIONS = 88


def _node_section_key() -> dict:
    """(source_file, section_title) -> node id, for the 20 Judson nodes."""
    keys = {}
    for node in load_judson_full_graph().nodes:
        path = CHAPTER_TO_FILE.get(node.facts.get("chapter"))
        section = node.facts.get("section")
        if path and section:
            keys[(path, section)] = node.id
    return keys


def derive_from_source() -> dict:
    """Re-derive the edges by scanning Judson's `<proof>` elements.

    Needs the pinned source cache. Used by the tests as a drift guard against
    the hardcoded `METHODOLOGICAL_EDGES` above, so the table cannot quietly
    stop matching the book.
    """
    from teach.pretext_parser import JUDSON_GLOB, JUDSON_SRC, iter_book

    keys = _node_section_key()
    found: dict = collections.defaultdict(int)
    total = in_scope = 0
    for block in iter_book(JUDSON_SRC, JUDSON_GLOB):
        if block.kind != "proof":
            continue
        total += 1
        node_id = keys.get((block.source_file, block.section_title))
        if node_id is None:
            continue
        in_scope += 1
        for src, pattern in PROOF_METHOD_PATTERNS.items():
            if re.search(pattern, block.text, re.IGNORECASE):
                found[(src, node_id)] += 1
    return {"edges": dict(found), "total_proofs": total,
            "proofs_in_modelled_sections": in_scope}


def methodological_edges() -> tuple[PrerequisiteEdge, ...]:
    return tuple(
        PrerequisiteEdge(src=src, dst=dst, type=EDGE_TYPE)
        for src, dst, _n, _q in METHODOLOGICAL_EDGES
    )


def edge_records() -> tuple[dict, ...]:
    """The edges with their evidence, for an emitter to serialize."""
    return tuple(
        {"src": src, "dst": dst, "relation": EDGE_TYPE, "proofs_matched": n,
         "quote": quote, "evidence": "named-method-in-proof-body"}
        for src, dst, n, quote in METHODOLOGICAL_EDGES
    )


def load_graph_with_methodological_edges() -> ConceptGraph:
    """The definitional unified graph plus the methodological edges.

    32 nodes, 48 edges: 40 `precedes` and 8 `methodological_prerequisite`.
    """
    base = load_unified_graph()
    graph = ConceptGraph(nodes=base.nodes, edges=base.edges + methodological_edges())
    graph.validate()
    return graph


def _self_check() -> None:
    graph = load_graph_with_methodological_edges()
    assert len(graph.nodes) == 32, len(graph.nodes)
    assert len(graph.edges) == 48, len(graph.edges)

    typed = [e for e in graph.edges if e.type == EDGE_TYPE]
    assert len(typed) == 8, len(typed)
    assert all(e.type == "precedes" for e in graph.edges if e not in typed)

    # Still a DAG, and every methodological edge respects the order.
    order = graph.topological_order()
    for e in graph.edges:
        assert order.index(e.src) < order.index(e.dst), (e.src, e.dst)

    # The two claims stay distinguishable -- that is the whole point of the
    # second type.
    definitional = {(e.src, e.dst) for e in graph.edges if e.type == "precedes"}
    methodological = {(e.src, e.dst) for e in typed}
    assert not (definitional & methodological), "an edge is asserted under both types"

    # Every methodological source is a proof-technique node that the
    # definitional rule left with no outgoing edge at all.
    for src, _dst, n, quote in METHODOLOGICAL_EDGES:
        assert src in PROOF_METHOD_PATTERNS, src
        assert n >= 1
        assert quote.strip()
        assert src not in {e.src for e in graph.edges if e.type == "precedes"}, (
            f"{src} already had a definitional edge; the two rules overlap"
        )

    # This connects one of the two nodes the definitional bridge stranded.
    base_incoming = {e.dst for e in load_unified_graph().edges}
    stranded = {n.id for n in graph.nodes
                if n.id.startswith("judson:") and n.id not in base_incoming}
    assert "judson:2.1-the-division-algorithm" in stranded
    assert ("levin-dmoi:proof-by-contradiction",
            "judson:2.1-the-division-algorithm") in methodological

    for node_id, why in REFUSED_METHODS:
        assert node_id not in {s for s, _d in methodological}, node_id
        assert why.strip()

    print(f"OK: {len(graph.nodes)} nodes, {len(graph.edges)} edges "
          f"({len(graph.edges) - len(typed)} precedes + {len(typed)} {EDGE_TYPE})")
    print(f"    derived from {PROOFS_IN_MODELLED_SECTIONS} of {TOTAL_PROOFS} proofs "
          f"(the rest are in chapters this graph models no node for)")
    print(f"    {len(REFUSED_METHODS)} foundational nodes still have no "
          "methodological edge, each with a recorded ground")


if __name__ == "__main__":
    _self_check()
