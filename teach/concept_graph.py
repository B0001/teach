"""Domain-agnostic prerequisite graph -- the shared engine core decided by
teach-8xw.4.

The epic drives reading, writing, foreign language, and arithmetic-through-
undergraduate-mathematics off *one* traversal engine. The risk this bead was
filed against: if the first real graph code is written against the VA Math
SOL data (the most fleshed-out domain), it is easy to let math-specific shape
leak into what should be domain-agnostic -- e.g. one node = one SOL standard
code, or an edge that only ever means "strict algebraic prerequisite."

The fix is the split below. Everything in this module is shared engine code
and must stay ignorant of which domain it is traversing: it only ever touches
`ConceptNode.id` / `.domain` (an opaque tag, not a discriminant it branches
on) and `PrerequisiteEdge.src/.dst/.type`. What a node's `facts` payload
means, what its `standard_ref` refers to, and how to check a claim about a
node's content against source (teach-8xw.11's job) are per-domain data and
code that live *outside* this module and are never imported by it.

Node/edge schema, and why each field is shaped the way it is:

  ConceptNode.id            globally unique string. A domain owns its own
                             namespacing convention (e.g. "va-math-sol:8.1",
                             "dummit-foote:3.1-normal-subgroups",
                             "va-reading-sol:3.4-main-idea"); the engine
                             never parses it, only compares it for equality.
  ConceptNode.domain         opaque tag ("math", "reading", "writing",
                             "foreign-language", ...). Carried through so a
                             consumer *can* group or filter by it, but this
                             module never switches behavior on its value --
                             the day traversal_order() or validate() gains an
                             `if node.domain == "math":` branch, the boundary
                             this bead exists to fix has been violated.
  ConceptNode.standard_ref   optional opaque string pointing at wherever the
                             domain's own standards document names this
                             concept (a SOL code, a textbook section number,
                             a CASE CFItem identifier). Meaning belongs to the
                             domain, not the engine.
  ConceptNode.facts          opaque per-domain payload (fact text, answer
                             key, proof sketch, target reading level --
                             whatever that domain's producer/checker pair
                             needs). The engine stores and forwards it
                             unread; it is data, not code.

  PrerequisiteEdge.src/dst   src must be established before dst. Same
                             direction as CASE's `precedes` association
                             ("the origin comes before the destination in
                             time or order") -- see sandbox-handoffs/
                             teach-8xw.3.md, confirmed live against
                             opensalt.net's CASE API this session. Do NOT
                             copy edge direction from mathgraph's graph.py
                             `depends_on` uninspected: there, `b.uses`/
                             `b.refs` point from a claim to the lemmas *it*
                             needs, i.e. src depends on dst -- the opposite
                             direction from `precedes`. A domain ingesting
                             depends_on-shaped source data must invert src/
                             dst when constructing a PrerequisiteEdge.
  PrerequisiteEdge.type      defaults to "precedes" (strict prerequisite,
                             the only relation this bead's traversal needs)
                             but is an open string, not an enum, so a future
                             domain that needs CASE's other relation types
                             (e.g. "isPartOf" for a reading passage
                             decomposed into sub-skills) is not forced to
                             misuse "precedes" to express something else.

Domain-plugin boundary -- what is shared engine code vs. per-domain data:

  SHARED ENGINE (this module, and boundary.py / cbt_primitives.py /
  honesty_rubric.py / potential_checker.py already built this way):
    - ConceptNode / PrerequisiteEdge / ConceptGraph types
    - graph validation (duplicate ids, dangling edges, cycles)
    - traversal (topological order)
    - the LessonArtifact boundary and CBT primitive rendering, which already
      operate on plain strings (`concept_name`) rather than a math-typed
      object -- teach-8xw.7/.9 got this right before this bead was filed

  PER-DOMAIN DATA/CONFIG (not this module; owned by each domain, e.g.
  teach-8xw.5 for VA Math SOL):
    - the actual ConceptNode/PrerequisiteEdge instances for that domain,
      built from that domain's standards source
    - the shape of `facts` for that domain (a math node's facts might carry
      a theorem statement + proof sketch; a reading node's might carry a
      passage + comprehension target) -- the engine never validates this
      shape, only the domain's own producer and checker agree on it

  PER-DOMAIN CODE, BEHIND A NARROW INTERFACE (not written by this bead --
  flagged so teach-8xw.11 doesn't accidentally grow it inside this module):
    verifying a domain fact claim (e.g. "is this group-theory statement
    correct") is genuine domain logic, not data. It must sit behind a
    function signature the checker calls through (claim text in, verdict
    out) so concept_graph.py and the traversal engine never import anything
    domain-specific. Designing that interface is teach-8xw.11's job; this
    bead only reserves the seam by keeping ConceptNode.facts opaque.
"""
from __future__ import annotations

import dataclasses
from typing import Mapping


@dataclasses.dataclass(frozen=True)
class ConceptNode:
    """One concept in some domain's standards. See module docstring for why
    each field is opaque to the engine."""

    id: str
    domain: str
    label: str
    standard_ref: str | None = None
    facts: Mapping[str, object] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class PrerequisiteEdge:
    """src must be established before dst. See module docstring for the
    direction convention and why it matches CASE's `precedes`, not
    mathgraph's `depends_on`."""

    src: str
    dst: str
    type: str = "precedes"


class GraphError(ValueError):
    """Raised by validate()/topological_order() on a structurally invalid
    graph (duplicate id, dangling edge endpoint, or cycle). A caller gets a
    loud failure, never a silently wrong traversal order -- this is the
    'prefer abstention to a confident answer' rule applied to graph data."""


@dataclasses.dataclass(frozen=True)
class ConceptGraph:
    """A domain-agnostic prerequisite graph: any mix of domains' nodes and
    edges, indistinguishable to every method here."""

    nodes: tuple[ConceptNode, ...]
    edges: tuple[PrerequisiteEdge, ...]

    def by_id(self, node_id: str) -> ConceptNode:
        for node in self.nodes:
            if node.id == node_id:
                return node
        raise KeyError(node_id)

    def validate(self) -> None:
        """Raise GraphError on the first structural problem found: a
        duplicate node id, an edge pointing at a node id that doesn't exist,
        or a cycle. Called by topological_order() before it trusts the graph
        enough to produce an order from it.
        """
        seen_ids: set[str] = set()
        for node in self.nodes:
            if node.id in seen_ids:
                raise GraphError(f"duplicate node id: {node.id!r}")
            seen_ids.add(node.id)

        for edge in self.edges:
            if edge.src not in seen_ids:
                raise GraphError(
                    f"edge {edge.src!r} -> {edge.dst!r} references unknown src node {edge.src!r}"
                )
            if edge.dst not in seen_ids:
                raise GraphError(
                    f"edge {edge.src!r} -> {edge.dst!r} references unknown dst node {edge.dst!r}"
                )

        self._check_acyclic(seen_ids)

    def _check_acyclic(self, node_ids: set[str]) -> None:
        # Kahn's algorithm: repeatedly remove nodes with in-degree zero. If
        # nodes remain once no more can be removed, whatever's left is on a
        # cycle -- report a member of it rather than just "graph has a
        # cycle somewhere", per the "prefer abstention... but abstain
        # informatively" spirit.
        remaining = set(node_ids)
        indegree = {n: 0 for n in remaining}
        for edge in self.edges:
            indegree[edge.dst] += 1

        ready = [n for n in remaining if indegree[n] == 0]
        while ready:
            n = ready.pop()
            remaining.discard(n)
            for edge in self.edges:
                if edge.src == n and edge.dst in remaining:
                    indegree[edge.dst] -= 1
                    if indegree[edge.dst] == 0:
                        ready.append(edge.dst)

        if remaining:
            raise GraphError(
                f"cycle detected involving node(s): {sorted(remaining)}"
            )

    def topological_order(self) -> tuple[str, ...]:
        """A valid learning order: every PrerequisiteEdge(src, dst) puts src
        before dst. Raises GraphError if the graph is invalid (see
        validate()) rather than returning a partial or arbitrary order.
        """
        self.validate()

        node_ids = [n.id for n in self.nodes]
        indegree = {n: 0 for n in node_ids}
        for edge in self.edges:
            indegree[edge.dst] += 1

        # Stable order: process ready nodes in the order they first appear
        # in self.nodes, not set-iteration order, so the same graph always
        # produces the same traversal.
        ready = [n for n in node_ids if indegree[n] == 0]
        order: list[str] = []
        while ready:
            n = ready.pop(0)
            order.append(n)
            for edge in self.edges:
                if edge.src == n:
                    indegree[edge.dst] -= 1
                    if indegree[edge.dst] == 0:
                        ready.append(edge.dst)

        return tuple(order)


if __name__ == "__main__":
    # Two domains that share nothing but the schema: a math node named after
    # a Dummit & Foote section, a reading node named after a VA reading SOL
    # code. If this module needed a single math-specific field or branch to
    # handle both, this check would be the place that would fail.
    math_cosets = ConceptNode(
        id="dummit-foote:3.1-cosets", domain="math", label="Cosets",
        standard_ref="D&F 3.1",
    )
    math_normal_subgroups = ConceptNode(
        id="dummit-foote:3.1-normal-subgroups", domain="math",
        label="Normal subgroups", standard_ref="D&F 3.1",
    )
    reading_main_idea = ConceptNode(
        id="va-reading-sol:3.4-main-idea", domain="reading",
        label="Identify the main idea", standard_ref="VA RDG 3.4",
    )
    reading_summarize = ConceptNode(
        id="va-reading-sol:3.5-summarize", domain="reading",
        label="Summarize a text", standard_ref="VA RDG 3.5",
    )

    graph = ConceptGraph(
        nodes=(math_cosets, math_normal_subgroups, reading_main_idea, reading_summarize),
        edges=(
            PrerequisiteEdge(src=math_cosets.id, dst=math_normal_subgroups.id),
            PrerequisiteEdge(src=reading_main_idea.id, dst=reading_summarize.id),
        ),
    )
    order = graph.topological_order()
    assert order.index(math_cosets.id) < order.index(math_normal_subgroups.id)
    assert order.index(reading_main_idea.id) < order.index(reading_summarize.id)

    cyclic = ConceptGraph(
        nodes=(math_cosets, math_normal_subgroups),
        edges=(
            PrerequisiteEdge(src=math_cosets.id, dst=math_normal_subgroups.id),
            PrerequisiteEdge(src=math_normal_subgroups.id, dst=math_cosets.id),
        ),
    )
    try:
        cyclic.topological_order()
        raise AssertionError("expected GraphError on a two-node cycle")
    except GraphError:
        pass

    print(
        "OK: one ConceptGraph traverses two unrelated domains (math, reading) "
        "correctly, and a cycle is rejected loudly rather than silently ordered"
    )
