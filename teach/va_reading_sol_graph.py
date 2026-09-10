"""Producer stage: a real, curriculum-scale non-math ConceptGraph (teach-8xw.29).

concept_recovery.py's module docstring and the design memory
(`bd memories teach-8xw-10-concept-recovery-design`) both claim vocabulary
extraction is domain-agnostic by construction. That claim had never been
exercised against a real non-math `ConceptGraph` -- every data-backed graph
in this repo before this module was VA Math SOL or Dummit & Foote, both math.
This module is the non-math counterpart: the Virginia English SOL reading
strands, grades K-8, loaded the same way teach-8xw.5 loaded VA Math SOL --
from the same real source, not synthetic filler written to make a checker
look good (see sandbox-prompt.md's "you cannot hold out examples from
yourself").

Where the data comes from (checked, not recalled -- see sandbox-prompt.md's
"fetch the raw bytes and read them yourself" rule):

  The same source teach-8xw.5 used for math --
  https://cdn.learningcommons.org/knowledge-graph/v1.13.0/exports/{nodes,
  relationships}.jsonl -- also carries Virginia's English Language Arts
  standards (`academicSubject == "English Language Arts"`, 1580 Virginia
  nodes), correctly coded and attributed to VDOE. Filtering those nodes for
  `statementType == "Strand"` and `statementCode` matching `<grade>.RI` or
  `<grade>.RL` for grades K-8 gives exactly 18 nodes -- a complete 9-grade x
  2-strand grid with no gaps (RI = "Reading: Informational Texts", RL =
  "Reading: Fiction"; both are present at every K-8 grade in this dataset,
  unlike some of the other ELA strands, e.g. RV, which stops after grade 5).
  Each strand node's real leaf standards were recovered by following two
  levels of `hasChild` edges (Strand -> Sub-Strand -> Standard, one level
  deeper than VA Math SOL's single Strand -> Standard hop -- ELA's data has
  an extra Sub-Strand layer, e.g. "1.RI.1" "Key Ideas and Confirming
  Details", that math's data doesn't), keeping only the leaf `Standard`-type
  nodes' `description` text (e.g. "1.RI.1.A", the actual numbered
  requirement) -- never a Sub-Strand's short label, which is a heading, not
  content. 150 leaf standards across the 18 groupings.

  VDOE's own site blocks direct fetches (403, same Akamai block teach-8xw.2
  found for the math document), so two independent checks stood in for a
  direct fetch: (1) the Wayback Machine CDX API (not the unreliable
  `availability` endpoint) shows live snapshots of the exact
  `doe.virginia.gov/home/showpublisheddocument/53643/638499760936600000`
  attribution URL from 2024-05 through 2025-11, confirming this is a real
  published VDOE document, not a guessed or fabricated URL; (2) the
  2025-10-07 snapshot was fetched and text-extracted (pypdf), and two leaf
  standard descriptions pulled from the Learning Commons data
  ("ask and answer literal (who, what, when, where) or inferential (why,
  how) questions about what is read" and "Trace and evaluate the argument
  and specific claims in a text, assessing whether the reasoning and
  evidence are relevant and sufficient to support the claims") were found
  verbatim in the extracted PDF text -- confirming Learning Commons'
  transcription matches VDOE's actual March 2024 "English Standards of
  Learning for Virginia Public Schools" document, not just trusting the
  intermediary.

Node granularity and edge derivation follow va_math_sol_graph.py's precedent
exactly: one ConceptNode per (grade, strand) grouping;
`PrerequisiteEdge(src=<grade N>.<strand>, dst=<grade N+1>.<strand>)` chaining
K -> 1 -> ... -> 8 within each strand, the same low-risk, VDOE-organizes-it-
this-way-on-purpose inference math made, not a claim copied from a published
progression document (none was found, same as math). The self-check below
spot-checks this against actual content, not just grade labels: K.RI's
leaves ask literal recall questions "with prompting and support"; 8.RI's
leaves require analyzing how an author "establishes and conveys a
perspective... and acknowledges and responds to conflicting evidence" --
a genuine content escalation, not just nine grade numbers in order.

Boilerplate warning, on purpose: like VA Math SOL, ELA's strand-level
descriptions are near-identical across grades ("The student will use
textual evidence to demonstrate comprehension and build knowledge from a
variety of [fiction/informational] texts read, viewed, and/or heard" recurs
at every RI and every RL grade with only small wording drift) -- this is
exactly the boilerplate-heavy structure concept_recovery.py's document-
frequency filtering exists to see through, and this graph was deliberately
not curated to avoid that property, since a graph specifically shaped to make
the checker look good would reproduce the self-authored-test-set failure
this bead exists to avoid.
"""
from __future__ import annotations

import json
from pathlib import Path

from teach.concept_graph import ConceptGraph, ConceptNode, PrerequisiteEdge

_DATA_PATH = Path(__file__).parent / "data" / "va_reading_sol_k8.json"


def load_va_reading_sol_data() -> dict:
    """Raw parsed JSON -- exposed so a caller (or a test) can inspect
    provenance (`data["source"]`) without also building a ConceptGraph."""
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_va_reading_sol_graph() -> ConceptGraph:
    """Build the ConceptGraph: one node per (grade, strand) grouping, edges
    chaining consecutive grades within each strand (RI, RL). Raises
    GraphError (via ConceptGraph.validate, called by anyone who traverses
    it) if the data file were ever hand-edited into an inconsistent state.
    """
    data = load_va_reading_sol_data()
    grade_order: list[str] = data["grade_order"]
    grade_index = {g: i for i, g in enumerate(grade_order)}

    nodes = tuple(
        ConceptNode(
            id=g["id"],
            domain="reading",
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
    graph = load_va_reading_sol_graph()

    assert len(graph.nodes) == 18, f"expected 18 K-8 (grade, RI/RL) groupings, got {len(graph.nodes)}"
    assert len(graph.edges) == 16, f"expected 16 grade-chain edges (2 strands x 8 gaps), got {len(graph.edges)}"

    order = graph.topological_order()

    ri_grades = ["K", "1", "2", "3", "4", "5", "6", "7", "8"]
    ri_ids = [f"va-reading-sol:{g}.RI" for g in ri_grades]
    for earlier, later in zip(ri_ids, ri_ids[1:]):
        assert order.index(earlier) < order.index(later), f"{earlier} must precede {later}"

    k_ri = graph.by_id("va-reading-sol:K.RI")
    eighth_ri = graph.by_id("va-reading-sol:8.RI")
    k_text = " ".join(desc for _, desc in k_ri.facts["leaf_standards"]).lower()
    eighth_text = " ".join(desc for _, desc in eighth_ri.facts["leaf_standards"]).lower()
    assert "with prompting and support" in k_text
    assert "with prompting and support" not in eighth_text
    assert "perspective" in eighth_text

    strands = {"RI", "RL"}
    seen = {(n.facts["strand_code"], n.facts["grade"]) for n in graph.nodes}
    expected = {(s, g) for s in strands for g in ri_grades}
    assert seen == expected, f"missing (strand, grade) pairs: {expected - seen}"

    total_leaves = sum(len(n.facts["leaf_standards"]) for n in graph.nodes)
    assert total_leaves == 150, f"expected 150 sourced leaf standards, got {total_leaves}"

    print(
        f"OK: {len(graph.nodes)} VA Reading SOL K-8 grade-strand groupings ({total_leaves} "
        f"sourced leaf standards) load as a valid DAG ({len(graph.edges)} grade-chain edges "
        "across 2 strands); K.RI..8.RI orders correctly and its endpoints' sourced standard "
        "text actually escalates in content (prompted literal recall -> independent analysis "
        "of authorial perspective), not just grade number"
    )
