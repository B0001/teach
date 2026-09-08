"""Producer stage: the VA Math SOL prerequisite knowledge graph (teach-8xw.5).

Loads `teach/data/va_math_sol_k8.json` into a `teach.concept_graph.ConceptGraph`
-- the mathgraph-style DAG the epic asks planning to traverse, scoped to
Virginia Mathematics SOL, grades K-8.

Where the data comes from (checked, not recalled -- see sandbox-prompt.md's
"fetch the raw bytes and read them yourself" rule):

  teach-8xw.2 (this bead's dependency) surveyed HuggingFace, GitHub, arXiv,
  and VDOE-via-Wayback and found no existing VA SOL *prerequisite* graph
  anywhere, but did find that github.com/learning-commons-org/knowledge-graph
  (CC BY-4.0) carries the actual VA Math SOL standard *text*, correctly coded
  and attributed to VDOE source documents. This module re-derives that
  finding directly rather than trusting the prior session's summary of it:
  `nodes.jsonl` was streamed from
  https://cdn.learningcommons.org/knowledge-graph/v1.13.0/exports/nodes.jsonl
  and filtered for `jurisdiction == "Virginia"`, `academicSubject ==
  "Mathematics"` -- 1758 nodes, of which 45 have `normalizedStatementType ==
  "Standard Grouping"` with a `statementCode` of the form `<grade>.<strand>`
  (e.g. `2.NS`) for grades K-8 across exactly the 5 core strands (Number and
  Number Sense, Computation and Estimation, Measurement and Geometry,
  Patterns/Functions and Algebra, Probability and Statistics) -- a complete
  9-grade x 5-strand grid with no gaps. `relationships.jsonl` was streamed
  the same way for `hasChild` edges whose source is one of those 45
  groupings, giving each grouping its real, VDOE-sourced numbered standards
  (e.g. `2.NS.3`, kept as `facts["leaf_standards"]` -- opaque payload, not
  graph structure, per teach-8xw.4's schema). VDOE's own site blocks direct
  fetches (403 from Akamai, confirmed live and via empty Wayback CDX -- see
  teach-8xw.2's handoff), so the attribution URL in the data is cited but not
  independently re-fetched; the standard *text* was cross-checked against
  the grade-to-grade content itself (see below), not against VDOE's PDF.

Node granularity: one ConceptNode per (grade, strand) *grouping*, not per
individual numbered standard. This is a deliberate scope decision, not
laziness: the individual numbered standards under a grouping (e.g. `2.NS.1`
through `2.NS.4`) don't carry a documented order relative to each other in
this dataset, and asserting one would be inventing a prerequisite claim this
module can't source. The (grade, strand) grouping *does* carry a real,
checkable order: it is the grade sequence itself.

Edge derivation -- the one substantive judgment call this module makes:

  PrerequisiteEdge(src=<grade N>.<strand>, dst=<grade N+1>.<strand>) for
  every strand, chaining K -> 1 -> 2 -> ... -> 8. This is NOT copied from a
  VDOE-published progression document -- no such document was reachable
  (teach-8xw.2 confirmed VDOE blocks bot traffic, and Wayback has no
  crosswalk/progression page archived). It is a mechanical rule: within one
  state's own strand taxonomy, the grade N+1 bucket is assumed to build on
  the grade N bucket of the *same* strand. This is about as low-risk an
  inference as a prerequisite claim can be (grade order is definitional, and
  VA organizes every grade's standards into these same 5 strands precisely
  so they read as a spiral progression) -- but it is still an inference this
  module makes, not a fact copied from source, and the self-check below
  spot-checks it against the actual standard text rather than asserting it
  blind: K.NS ("counting quantities up to 100") textually precedes 1.NS
  ("counting quantities up to 120") precedes 2.NS ("ten-to-one base-10
  relationships") precedes 8.NS ("the real number system and its subsets"),
  which is a genuine, content-level escalation, not just five grade labels
  in numeric order.

  High school (grades 9-12) is organized by *course* (Algebra 1, Geometry,
  Algebra II, ...), not a single linear grade number, so the K-8 grade-chain
  rule above does not apply to it -- see the next section.

High school course sequence (teach-8xw.16) -- what's sourced and what isn't:

  teach-8xw.2 and teach-8xw.5 (this bead's dependencies) each tried and
  failed to reach a VDOE course-sequence document: doe.virginia.gov 403s all
  direct bot traffic (Akamai block, reconfirmed live this session), and both
  sessions' Wayback Machine checks against a *guessed* crosswalk URL
  (testing/sol/resources/crosswalks.html) found zero snapshots -- correctly,
  since that URL was never real. This session found the real document by a
  different route: the Learning Commons node data for VA's HS math standards
  (see below) carries an `attributionStatement` citing VDOE's actual
  publication URL, `doe.virginia.gov/home/showpublisheddocument/48908/<id>`.
  Wayback DOES hold live snapshots of that exact URL family across several
  capture dates from 2023 through 2026-04-16 (verified via the CDX API this
  session, not the unreliable `availability` API endpoint) -- it was never
  actually unreachable, only unguessed. The 2026-04-16 capture
  (https://web.archive.org/web/20260416041407/https://www.doe.virginia.gov/home/showpublisheddocument/48908/638741650017470000)
  is "Mathematics Standards of Learning for Virginia Public Schools,"
  adopted August 2023 by the Virginia Board of Education -- the actual
  current SOL document, not a secondary summary of it.

  That PDF gives each high-school course a short introductory paragraph, and
  most of them explicitly name a prerequisite course by stating what
  students are assumed to have already completed. Those sentences are the
  *only* source for the `course_prerequisites` list in
  `data/va_math_sol_hs.json` -- each entry there carries the exact quoted
  sentence it was read from, verbatim (pypdf-extracted, whitespace-
  normalized), so this is checkable against the PDF rather than asserted.
  Courses with no such sentence (Trigonometry, Probability and Statistics,
  Discrete Mathematics) get no incoming prerequisite edge here -- the
  document simply doesn't say, and inventing "well-known" ordering for them
  (e.g. that Trigonometry is usually taken after Geometry) would be exactly
  the kind of unsourced claim sandbox-prompt.md rules out. The 7 sourced
  relations: Algebra 1 -> Geometry, Algebra 1 -> AFDA, Algebra 1 -> Algebra
  2, Algebra 1 -> Computer Mathematics, Geometry -> Computer Mathematics
  (the source's exact phrase is "beginning Geometry," weaker than "completed
  Geometry" for the other edges -- flagged, not softened away), Geometry ->
  Mathematical Analysis, Algebra 2 -> Mathematical Analysis.

  Node/edge granularity mismatch and how it's resolved: like the K-8 data,
  each HS node is a (course, strand) grouping (e.g. `G.RLT`, `A.EO`) -- the
  same `Standard Grouping` level Learning Commons uses, for the same reason
  (the individual numbered standards within one grouping carry no documented
  order). But the *sourced* prerequisite relation is at course granularity
  ("completed Algebra 1"), not grouping granularity, and a course's strand
  groupings don't line up 1:1 across courses the way K-8 grade-groupings do
  (Geometry's strands are DF/PC/RLT/TR; Algebra 1's are EI/EO/F/ST -- no
  shared strand code to chain within). Asserting a `PrerequisiteEdge` from
  just one Algebra 1 grouping to just one Geometry grouping would not
  actually force every Algebra 1 grouping before every Geometry grouping in
  `topological_order()` -- a valid topological sort could still place an
  unconnected Algebra 1 grouping after a Geometry one. So `_hs_course_edges`
  below builds the full bipartite product: every grouping of the
  prerequisite course gets an edge to every grouping of the dependent
  course. This is mechanical (generated from `course_prerequisites`, not
  hand-typed) and is the minimum edge set that actually guarantees "all of
  course X before any of course Y" under Kahn's-algorithm topological sort.

  What is deliberately NOT here: an edge from any K-8 grouping into Algebra
  1. The 2023 document's Algebra 1 section says algebraic thinking "begins
  in kindergarten," but never cites a specific K-8 standard grouping as
  Algebra 1's prerequisite the way the HS-to-HS sentences do -- so, per the
  same rule, no edge is asserted there either.
"""
from __future__ import annotations

import json
from pathlib import Path

from teach.concept_graph import ConceptGraph, ConceptNode, PrerequisiteEdge

_DATA_PATH = Path(__file__).parent / "data" / "va_math_sol_k8.json"
_HS_DATA_PATH = Path(__file__).parent / "data" / "va_math_sol_hs.json"


def load_va_math_sol_data() -> dict:
    """Raw parsed JSON -- exposed mainly so a caller (or a test) can inspect
    provenance (`data["source"]`) without also building a ConceptGraph."""
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_va_math_sol_graph() -> ConceptGraph:
    """Build the ConceptGraph: one node per (grade, strand) grouping, edges
    chaining consecutive grades within each strand. Raises GraphError (via
    ConceptGraph.validate, called by anyone who traverses it) if the data
    file were ever hand-edited into an inconsistent state.
    """
    data = load_va_math_sol_data()
    grade_order: list[str] = data["grade_order"]
    grade_index = {g: i for i, g in enumerate(grade_order)}

    nodes = tuple(
        ConceptNode(
            id=g["id"],
            domain="math",
            label=f"{g['strand_name']} (Grade {g['grade']})",
            standard_ref=g["statement_code"],
            facts={
                "strand_code": g["strand_code"],
                "strand_name": g["strand_name"],
                "grade": g["grade"],
                "case_identifier_uuid": g["case_identifier_uuid"],
                "leaf_standards": tuple(
                    (leaf["statement_code"], leaf["description"])
                    for leaf in g["leaf_standards"]
                ),
            },
        )
        for g in data["groupings"]
    )

    by_strand: dict[str, list[dict]] = {}
    for g in data["groupings"]:
        by_strand.setdefault(g["strand_code"], []).append(g)

    edges: list[PrerequisiteEdge] = []
    for strand_groupings in by_strand.values():
        strand_groupings.sort(key=lambda g: grade_index[g["grade"]])
        for earlier, later in zip(strand_groupings, strand_groupings[1:]):
            edges.append(PrerequisiteEdge(src=earlier["id"], dst=later["id"]))

    return ConceptGraph(nodes=nodes, edges=tuple(edges))


def load_va_math_sol_hs_data() -> dict:
    """Raw parsed JSON for the high-school course-grouping data -- exposed so
    a caller (or a test) can inspect `data["course_prerequisites"]` (each
    entry's sourced quote) without also building a ConceptGraph."""
    with _HS_DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_va_math_sol_hs_graph() -> ConceptGraph:
    """Build the high-school ConceptGraph: one node per (course, strand)
    grouping, edges built from `course_prerequisites`' sourced course-level
    relations as the full bipartite product of (every grouping of the
    prerequisite course) x (every grouping of the dependent course). See the
    module docstring's "High school course sequence" section for why this
    shape, and why it's the minimum edge set that actually orders correctly.
    """
    data = load_va_math_sol_hs_data()

    nodes = tuple(
        ConceptNode(
            id=g["id"],
            domain="math",
            label=f"{g['strand_description']} ({g['course_name']})",
            standard_ref=g["statement_code"],
            facts={
                "course_code": g["course_code"],
                "course_name": g["course_name"],
                "strand_description": g["strand_description"],
                "case_identifier_uuid": g["case_identifier_uuid"],
                "leaf_standards": tuple(
                    (leaf["statement_code"], leaf["description"])
                    for leaf in g["leaf_standards"]
                ),
            },
        )
        for g in data["groupings"]
    )

    groupings_by_course: dict[str, list[str]] = {}
    for g in data["groupings"]:
        groupings_by_course.setdefault(g["course_code"], []).append(g["id"])

    edges: list[PrerequisiteEdge] = []
    for rel in data["course_prerequisites"]:
        src_ids = groupings_by_course[rel["src_course"]]
        dst_ids = groupings_by_course[rel["dst_course"]]
        for src_id in src_ids:
            for dst_id in dst_ids:
                edges.append(PrerequisiteEdge(src=src_id, dst=dst_id))

    return ConceptGraph(nodes=nodes, edges=tuple(edges))


def load_va_math_sol_full_graph() -> ConceptGraph:
    """K-8 and high-school combined into one ConceptGraph. Safe to union
    directly (no shared node ids -- K-8 ids key on a digit/'K' grade, HS ids
    key on a course letter code) and no edges cross the two, since no K-8
    grouping is asserted as an HS course's prerequisite (see module
    docstring)."""
    k8 = load_va_math_sol_graph()
    hs = load_va_math_sol_hs_graph()
    return ConceptGraph(nodes=k8.nodes + hs.nodes, edges=k8.edges + hs.edges)


if __name__ == "__main__":
    graph = load_va_math_sol_graph()

    assert len(graph.nodes) == 45, f"expected 45 K-8 groupings, got {len(graph.nodes)}"
    assert len(graph.edges) == 40, f"expected 40 grade-chain edges (5 strands x 8 gaps), got {len(graph.edges)}"

    order = graph.topological_order()

    # Content-level spot check for the NS strand, not just label ordering --
    # see module docstring's "Edge derivation" section for why this matters.
    ns_grades = ["K", "1", "2", "3", "4", "5", "6", "7", "8"]
    ns_ids = [f"va-math-sol:{g}.NS" for g in ns_grades]
    for earlier, later in zip(ns_ids, ns_ids[1:]):
        assert order.index(earlier) < order.index(later), f"{earlier} must precede {later}"

    k_ns = graph.by_id("va-math-sol:K.NS")
    eighth_ns = graph.by_id("va-math-sol:8.NS")
    assert "100" in k_ns.facts["leaf_standards"][0][1]
    assert "real number" in eighth_ns.facts["leaf_standards"][0][1].lower()

    # Every strand code appears at every grade -- the "no gaps" claim this
    # module's docstring makes about the source data, checked here rather
    # than just asserted.
    strands = {"NS", "CE", "MG", "PFA", "PS"}
    seen = {(n.facts["strand_code"], n.facts["grade"]) for n in graph.nodes}
    expected = {(s, g) for s in strands for g in ns_grades}
    assert seen == expected, f"missing (strand, grade) pairs: {expected - seen}"

    print(
        f"OK: {len(graph.nodes)} VA Math SOL K-8 grade-strand groupings load as a "
        f"valid DAG ({len(graph.edges)} grade-chain edges across {len(strands)} "
        "strands); K.NS..8.NS orders correctly and its endpoints' sourced "
        "standard text actually escalates in content, not just grade number"
    )

    hs_graph = load_va_math_sol_hs_graph()

    assert len(hs_graph.nodes) == 33, f"expected 33 HS course-strand groupings, got {len(hs_graph.nodes)}"
    assert len(hs_graph.edges) == 96, f"expected 96 bipartite prerequisite edges, got {len(hs_graph.edges)}"

    hs_order = hs_graph.topological_order()

    # Content-level check, same spirit as the K-8 one above: every Algebra 1
    # grouping actually precedes every Geometry grouping (and the other 6
    # sourced course relations) in the computed order -- not just "some edge
    # exists somewhere", which is what the bipartite-product edge
    # construction exists to guarantee. A bug that only wired one grouping
    # per course (instead of the full product) would leave some pairs
    # unordered and this loop would catch it.
    hs_data = load_va_math_sol_hs_data()
    groupings_by_course: dict[str, list[str]] = {}
    for g in hs_data["groupings"]:
        groupings_by_course.setdefault(g["course_code"], []).append(g["id"])
    for rel in hs_data["course_prerequisites"]:
        for src_id in groupings_by_course[rel["src_course"]]:
            for dst_id in groupings_by_course[rel["dst_course"]]:
                assert hs_order.index(src_id) < hs_order.index(dst_id), (
                    f"{src_id} ({rel['src_course']}) must precede {dst_id} ({rel['dst_course']}) "
                    f"per source quote: {rel['source_quote']!r}"
                )

    # Every course_prerequisites entry must carry a real, non-empty quote --
    # this is what stops the edge list from silently degrading into an
    # unsourced assertion if someone edits the data file later.
    for rel in hs_data["course_prerequisites"]:
        assert rel.get("source_quote"), f"missing source_quote for {rel['src_course']} -> {rel['dst_course']}"
        assert rel["src_course"] in hs_data["courses"]
        assert rel["dst_course"] in hs_data["courses"]

    # Courses the source document gives no prerequisite sentence for must
    # have zero incoming course_prerequisites edges -- abstention, not a
    # guessed ordering (see module docstring).
    courses_with_incoming = {rel["dst_course"] for rel in hs_data["course_prerequisites"]}
    no_sourced_prereq = set(hs_data["courses"]) - courses_with_incoming - {"A"}
    assert no_sourced_prereq == {"T", "PS", "DM"}, (
        f"expected exactly Trigonometry/Probability-and-Statistics/Discrete-Mathematics "
        f"to have no sourced prerequisite, got {no_sourced_prereq}"
    )

    full_graph = load_va_math_sol_full_graph()
    assert len(full_graph.nodes) == len(graph.nodes) + len(hs_graph.nodes)
    assert len(full_graph.edges) == len(graph.edges) + len(hs_graph.edges)
    full_graph.validate()  # union must still be a single valid DAG, no cross-contamination

    print(
        f"OK: {len(hs_graph.nodes)} VA Math SOL high-school course-strand groupings "
        f"(9 courses: {', '.join(sorted(hs_data['courses']))}) load as a valid DAG "
        f"({len(hs_graph.edges)} edges from {len(hs_data['course_prerequisites'])} sourced "
        "course-level prerequisite sentences in VDOE's August 2023 Mathematics SOL "
        "document, expanded to the full bipartite product); every sourced relation "
        "orders correctly; courses with no sourced prerequisite sentence "
        "(Trigonometry, Probability and Statistics, Discrete Mathematics) correctly "
        "have none asserted"
    )
