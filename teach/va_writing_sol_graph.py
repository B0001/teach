"""Producer stage: the VA Writing SOL K-12 prerequisite graph (teach-5aj).

teach-8xw.39's survey found the writing domain has a real, curriculum-scale
source already sitting in the same pipeline this repo already trusts and has
verified twice (math: teach-8xw.5, reading: teach-8xw.29):
`cdn.learningcommons.org/knowledge-graph/v1.13.0/exports/nodes.jsonl` carries
a complete K-12 Virginia ELA "W" (Writing) strand, same Strand -> Sub-Strand
-> leaf Standard shape as `va_reading_sol_graph.py`'s RI/RL strands, same CC
BY-4.0 license, same VDOE attribution/provenance chain. This module is the
near-mechanical repeat of that pattern the survey predicted it would be.

Where the data comes from (checked, not recalled -- see sandbox-prompt.md's
"fetch the raw bytes and read them yourself" rule):

  `nodes.jsonl` (342MB, streamed this session, not trusted from the prior
  session's scratch snapshot which no longer existed on disk) was filtered
  for `jurisdiction == "Virginia"`, `academicSubject == "English Language
  Arts"`, `statementCode` matching `<grade>.W(.*)?` for grades K-12 -- 236
  nodes, a complete 13-grade grid with no gaps. `relationships.jsonl`
  (570MB, streamed the same session) was filtered for `hasChild` edges whose
  `source_identifier`/`target_identifier` (the node's top-level `identifier`
  field -- NOT `caseIdentifierUUID`, despite `sourceEntityKey`/
  `targetEntityKey` in the relationship's own properties claiming that; the
  UUID-keyed join produced zero matches and was rejected before the
  identifier-keyed one was tried) are both within that 236-node set: exactly
  223 edges, i.e. 236 - 13, confirming the 236 nodes form 13 disjoint trees
  (one per grade) with no orphans and no cross-grade edges.

  BFS from each of the 13 `Strand` roots (`K.W`, `1.W`, ..., `12.W`) shows a
  perfectly uniform 4-level hierarchy in every grade: `Strand` (depth 0) ->
  `Sub-Strand` (depth 1, e.g. `7.W.1` "Modes and Purposes for Writing") ->
  `Standard` (depth 2, e.g. `12.W.3.A`, the real numbered requirement) ->
  `Component` (depth 3, e.g. `7.W.2.A.iii`, template-fragment bullets like
  "*Write arguments that* develop a thesis..." that read as sentence
  fragments, not standalone requirements). This module keeps only the depth-
  2 `Standard`-type leaves, one level deeper than `va_reading_sol_graph.py`
  needed to go (RI/RL has no Component layer) but the same stopping rule:
  the leaf is the type named "Standard", not whatever is deepest in the
  tree. 93 leaf standards across the 13 groupings.

  VDOE's own site blocks direct fetches (403, same Akamai block teach-8xw.2
  found for math and teach-8xw.29 found for reading), so the same two-check
  substitute was used: (1) the Wayback Machine CDX API shows live snapshots
  of the exact `doe.virginia.gov/home/showpublisheddocument/53643/
  638499760936600000` attribution URL from 2024-05 through 2025-09 -- the
  same document reading's provenance already established, since VA's
  "English Standards of Learning" PDF covers RI/RL/W/etc. together, not one
  PDF per strand; (2) the 2025-09-06 snapshot was fetched and text-extracted
  (pypdf), and three leaf standard descriptions spanning the grade range --
  K.W.1.A ("Use a combination of drawing, dictating, and writing to compose
  narrative stories in sequential order..."), 12.W.3.A ("Revise writing for
  clarity of content, accuracy, and depth of information."), and 12.W.3.D
  ("Write and revise to a standard acceptable both in the workplace and in
  postsecondary education.") -- were found verbatim in the extracted PDF
  text, confirming Learning Commons' transcription matches VDOE's actual
  document for this strand too, not just the RI/RL strands reading already
  checked.

  Known source quirk, stated not hidden: grade 12 has two distinct source
  nodes (different `caseIdentifierUUID`s, different `description` text) both
  coded `statementCode == "12.W.3.A"` -- "Plan and organize writing to
  address a specific audience and purpose..." and "Revise writing for
  clarity of content, accuracy, and depth of information." This is upstream
  data, not a bug in this loader (confirmed by reading both raw node lines
  directly from `nodes.jsonl`); `leaf_standards` is a tuple of (code, text)
  pairs, same as reading, so both entries survive rather than one silently
  overwriting the other in a dict -- but a caller that expects
  `statement_code` to be unique within a grouping should not assume that
  here.

Node granularity and edge derivation follow `va_reading_sol_graph.py`'s
precedent exactly: one ConceptNode per (grade, strand) grouping (here,
strand is always "W");
`PrerequisiteEdge(src=<grade N>.W, dst=<grade N+1>.W)` chaining K -> 1 ->
... -> 12, the same low-risk, VDOE-organizes-it-this-way-on-purpose
inference math and reading both made, not a claim copied from a published
progression document (none was found, same as math and reading). The self-
check below spot-checks this against actual content, not just grade labels:
every grouping K-5 contains the phrase "guidance and support" (e.g. K.W.2.A
"With guidance and support, use prewriting activities..."); it is absent
from every grouping grade 6 and up. Conversely, "postsecondary" appears only
in 12.W (12.W.3.D, above) and nowhere K-11 -- a genuine two-sided content
escalation, not just thirteen grade numbers in order.
"""
from __future__ import annotations

import json
from pathlib import Path

from teach.concept_graph import ConceptGraph, ConceptNode, PrerequisiteEdge

_DATA_PATH = Path(__file__).parent / "data" / "va_writing_sol_k12.json"


def load_va_writing_sol_data() -> dict:
    """Raw parsed JSON -- exposed so a caller (or a test) can inspect
    provenance (`data["source"]`) without also building a ConceptGraph."""
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_va_writing_sol_graph() -> ConceptGraph:
    """Build the ConceptGraph: one node per (grade, strand) grouping (strand
    is always "W" here), edges chaining consecutive grades K -> 1 -> ... ->
    12. Raises GraphError (via ConceptGraph.validate, called by anyone who
    traverses it) if the data file were ever hand-edited into an
    inconsistent state.
    """
    data = load_va_writing_sol_data()
    grade_order: list[str] = data["grade_order"]
    grade_index = {g: i for i, g in enumerate(grade_order)}

    nodes = tuple(
        ConceptNode(
            id=g["id"],
            domain="writing",
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


if __name__ == "__main__":
    graph = load_va_writing_sol_graph()

    assert len(graph.nodes) == 13, f"expected 13 K-12 (grade, W) groupings, got {len(graph.nodes)}"
    assert len(graph.edges) == 12, f"expected 12 grade-chain edges (1 strand x 12 gaps), got {len(graph.edges)}"

    order = graph.topological_order()

    grades = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    w_ids = [f"va-writing-sol:{g}.W" for g in grades]
    for earlier, later in zip(w_ids, w_ids[1:]):
        assert order.index(earlier) < order.index(later), f"{earlier} must precede {later}"

    k_w = graph.by_id("va-writing-sol:K.W")
    twelfth_w = graph.by_id("va-writing-sol:12.W")
    k_text = " ".join(desc for _, desc in k_w.facts["leaf_standards"]).lower()
    twelfth_text = " ".join(desc for _, desc in twelfth_w.facts["leaf_standards"]).lower()
    assert "guidance and support" in k_text
    assert "guidance and support" not in twelfth_text
    assert "postsecondary" in twelfth_text
    assert "postsecondary" not in k_text

    seen = {(n.facts["strand_code"], n.facts["grade"]) for n in graph.nodes}
    expected = {("W", g) for g in grades}
    assert seen == expected, f"missing (strand, grade) pairs: {expected - seen}"

    total_leaves = sum(len(n.facts["leaf_standards"]) for n in graph.nodes)
    assert total_leaves == 93, f"expected 93 sourced leaf standards, got {total_leaves}"

    print(
        f"OK: {len(graph.nodes)} VA Writing SOL K-12 grade-strand groupings ({total_leaves} "
        f"sourced leaf standards) load as a valid DAG ({len(graph.edges)} grade-chain edges); "
        "K.W..12.W orders correctly and its endpoints' sourced standard text actually escalates "
        "in content (guided drawing/dictating -> independent postsecondary/workplace-standard "
        "writing), not just grade number"
    )
