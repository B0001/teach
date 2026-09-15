"""Producer stage: the foundational logic layer (teach-ysm.1).

The root nodes of the unified graph -- sets, functions, statements,
propositional and predicate logic, the three proof techniques, and induction.
Everything in `teach.judson_algebra_graph` is downstream of these.

WHY LEVIN AND NOT HAMMACK (teach-9ug, decided by the repo owner 2026-09-13)

The plan this graph belongs to named Richard Hammack's *Book of Proof* as the
foundational text. It cannot be used, for two independent reasons, both
verified by fetching the bytes rather than by recalling anything:

  - No machine-readable source exists. Hammack publishes `Main.pdf` and
    nothing else: no PreTeXt, no LaTeX, no source repository (his only GitHub
    repo is his web page). The book's canonical home at
    `www.people.vcu.edu/~rhammack/BookOfProof/` no longer resolves -- it
    redirects to the VCU front page -- and the live mirror at
    `richardhammack.github.io/BookOfProof/` links only the PDF. So the
    structural-tag extraction this graph is built on has nothing to read.
  - The license forbids the result. That mirror's own copyright line reads:
    "(c) 2018 by Richard Hammack; Licensed under a Creative Commons
    Attribution-NonCommercial-NoDerivative 4.0 License". A knowledge graph
    carrying its definitions and their dependency structure is an adaptation,
    which NoDerivatives does not permit. This is the same objection that
    already moved this repo off Dummit & Foote (see
    `teach.judson_algebra_graph`'s docstring, teach-8xw.56).

The replacement is Oscar Levin's *Discrete Mathematics: An Open Introduction*,
**3rd edition**, which is real PreTeXt and covers the same foundational
ground: sets and set operations, functions and their properties, statements
and connectives, truth tables and logical equivalence, predicates and
quantifiers, deduction rules, direct proof, contrapositive, contradiction,
and induction.

THE EDITION IS THE LICENSE, AND THE PIN IS WHAT MAKES IT TRUE

`LICENSE` at the pinned commit reads, verbatim:

    This work is licensed under the Creative Commons Attribution-ShareAlike
    4.0 International License.

That is the 3rd edition. The repository's `master` branch is the **4th**
edition and is CC BY-**NC**-SA 4.0 -- the NonCommercial clause this project
cannot accept. So what makes this source usable is the commit
(`a8e4949bc45daf100930c1182983778f56ab689f`, tag `3rd-ed`), not the
repository, and a future worker who re-clones `master` to "update" this
extract would silently relicense the whole foundational half. The pin is
recorded in `teach/data/textbook_provenance.json` with a sha256 per source
file, and `LEVIN_SOURCE["license_note"]` repeats the warning where anyone
reading the data will see it.

CC BY-SA is copyleft, and so is Judson's GFDL 1.3+. They are *different*
copyleft licenses and they do not merge. A node's license travels with the
node: `teach-j4n.1` must emit per-node license and attribution rather than
stamping one license across the combined dataset.

WHERE THE NODE TEXT COMES FROM

Each node's `definition` is text this repo's `teach.pretext_parser` pulled out
of the pinned `ptx/*.ptx` files -- Levin's own words, not a paraphrase -- and
`teach/data/levin_dmoi_foundations.json` records, per node, every
`(source_file, xml_id, kind)` block the text was assembled from plus that
file's sha256. So any claim this graph makes about what Levin says is
re-derivable from the source with the parser alone.

Neither Levin nor Judson contains a single `<definition>` element (measured,
not assumed -- see `teach.pretext_parser`'s docstring). Definitions here are
recovered from `<term>`-bearing prose, and the provenance records that with
`kind: "term-definition"` so a consumer never mistakes a recovered definition
for one the author tagged.

Two selection rules were needed to keep node text on topic, and both exist
because the naive version produced something confidently wrong:

  - `<investigation>` subtrees are skipped by the parser. Levin opens many
    subsections with a puzzle for the reader; "Deductions" opens with a
    Sherlock Holmes dress-code puzzle. Harvested naively, the node explaining
    what a deduction rule is began "Holmes owns two suits: one black and one
    tweed."
  - `<example>` blocks are excluded from node text. They illustrate; they do
    not define. They are NOT treated as terminating a section, because Levin
    interleaves definitions and examples -- an earlier "stop at the first
    example" rule cost the `statements` node five of its six blocks and
    dropped the definition of a tautology, which follows an example.
"""
from __future__ import annotations

import json
from pathlib import Path

from teach.concept_graph import ConceptGraph, ConceptNode, PrerequisiteEdge

DOMAIN = "math"

_DATA_PATH = Path(__file__).parent / "data" / "levin_dmoi_foundations.json"


def load_levin_foundations_data() -> dict:
    """Raw parsed JSON -- exposed so a caller (or a test) can inspect
    provenance (`data["source"]`, and per-node `provenance`) without also
    building nodes."""
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


LEVIN_SOURCE = load_levin_foundations_data()["source"]


def load_levin_foundation_nodes() -> tuple[ConceptNode, ...]:
    """The foundational concepts, as `teach.concept_graph.ConceptNode`s.

    No edges: ordering them is teach-ysm.2's job, and it is a separate claim
    from "these concepts are in this book". A node's `facts` carries the terms
    Levin introduces, his definition text, and the blocks it came from.
    """
    data = load_levin_foundations_data()
    return tuple(
        ConceptNode(
            id=n["id"],
            domain=DOMAIN,
            label=n["label"],
            standard_ref=n["standard_ref"],
            facts={
                "terms": tuple(n["terms"]),
                "definition": n["definition"],
                "source_files": tuple(
                    sorted({p["source_file"] for p in n["provenance"]})
                ),
                "blocks": tuple(
                    (p["kind"], p["xml_id"], p["subsection_title"])
                    for p in n["provenance"]
                ),
                "license": LEVIN_SOURCE["license"],
                "attribution": LEVIN_SOURCE["attribution"],
            },
        )
        for n in data["nodes"]
    )


# --------------------------------------------------------------------------
# teach-ysm.2: ordering the foundational concepts.
#
# THE RULE, the same one teach.judson_algebra_graph applies, and it is narrow
# on purpose:
#
#     An edge src -> dst exists only when dst's definition cannot be stated
#     without using a term src defines.
#
# That is a content dependency readable off the definitions. It is NOT "the
# book prints src first", NOT "src is a standard example of dst", and NOT "a
# student would probably learn src first".
#
# HOW THESE EDGES WERE DECIDED, and why the process is worth recording
#
# Twelve independent adjudicators (one per destination node, each considering
# all 11 candidate sources) proposed edges against the rule above, quoting the
# phrase in dst's own definition that uses the required term. Twelve
# independent skeptics then tried to REFUTE each proposed edge -- checking the
# quote was verbatim, that the term was genuinely src's and not dst's own, and
# trying to restate dst without src's vocabulary. 16 edges were proposed and 7
# were refuted.
#
# The skeptics were not treated as the final word, because a refutation can be
# wrong in the same way an assertion can. Two refusals were overruled after
# reading the source text, and both were refuted on narrow grounds:
#
#   statements -> deduction-rules   The skeptic counted occurrences of the
#         word "statement" in dst (exactly one, in the aside "Let's look at
#         the form of the statements") and concluded it was not load-bearing.
#         But the argument form that IS the definition is written as P, Q
#         joined by the conditional connective -- propositional variables and
#         "if..., then..." are both defined in `statements`, and the word
#         count never looked at them. Refusing this edge also made
#         deduction-rules a root of the graph, which is plainly wrong: a rule
#         of inference does not precede the notion of a statement.
#   direct-proof -> proof-by-contrapositive   The skeptic argued dst spells
#         its skeleton out inline ("Assume not-Q ... Therefore not-P") so it
#         does not need src. But Levin's statement of what the technique IS
#         reads "This is all that proof by contrapositive does. It gives a
#         direct proof of the contrapositive of the implication." The
#         definiens is src's only term. The inline skeleton is the form; this
#         sentence is the definition, and it cannot be stated without it.
#
# A third refutation was factually wrong but harmless in its conclusion, and
# is recorded here so nobody re-derives it: the skeptic killed
# sets -> function-properties claiming every occurrence of "set" in dst sat
# inside a "duplicated summary block that is byte-identical" to earlier text.
# There is no duplicated text in that node (checked: zero repeated sentences);
# the block it meant is Levin's own <assemblage> summary box. The edge stays
# refused anyway, on the better ground that `sets` already reaches
# function-properties through `functions`.
_EDGES = (
    # from sets
    PrerequisiteEdge(src="levin-dmoi:sets", dst="levin-dmoi:set-operations"),
    PrerequisiteEdge(src="levin-dmoi:sets", dst="levin-dmoi:functions"),
    PrerequisiteEdge(src="levin-dmoi:functions", dst="levin-dmoi:function-properties"),
    # from statements
    PrerequisiteEdge(src="levin-dmoi:statements", dst="levin-dmoi:predicates-and-quantifiers"),
    PrerequisiteEdge(src="levin-dmoi:statements", dst="levin-dmoi:propositional-logic"),
    PrerequisiteEdge(src="levin-dmoi:statements", dst="levin-dmoi:deduction-rules"),
    PrerequisiteEdge(src="levin-dmoi:statements", dst="levin-dmoi:direct-proof"),
    PrerequisiteEdge(src="levin-dmoi:statements", dst="levin-dmoi:proof-by-contradiction"),
    PrerequisiteEdge(src="levin-dmoi:statements", dst="levin-dmoi:mathematical-induction"),
    # proof techniques
    PrerequisiteEdge(src="levin-dmoi:propositional-logic", dst="levin-dmoi:proof-by-contrapositive"),
    PrerequisiteEdge(src="levin-dmoi:direct-proof", dst="levin-dmoi:proof-by-contrapositive"),
)

# Edges proposed and then refused, with the ground for refusing. Recorded the
# way judson_algebra_graph records its NON_EDGES: an absent edge is invisible,
# so without this a later worker "fixes" the graph by adding one back and
# nobody can tell whether it was considered and rejected or simply missed.
REFUSED_EDGES = (
    ("levin-dmoi:propositional-logic", "levin-dmoi:predicates-and-quantifiers",
     "propositional-logic's own definition opens 'A proposition is simply a "
     "statement' -- an explicit synonym that adds nothing of its own, so what "
     "predicates-and-quantifiers actually leans on is `statements`, which it "
     "already has an edge from."),
    ("levin-dmoi:propositional-logic", "levin-dmoi:deduction-rules",
     "The truth table is how Levin CHECKS modus ponens, not what a deduction "
     "rule is: the definition is 'an argument form which is always valid', and "
     "the table arrives behind 'Are you convinced? If not, consider the "
     "following truth table' -- the author's own framing of it as optional."),
    ("levin-dmoi:sets", "levin-dmoi:function-properties",
     "Reachable through `functions`, which does depend on sets. Asserting the "
     "transitive edge separately would double-count the same dependency."),
    ("levin-dmoi:predicates-and-quantifiers", "levin-dmoi:direct-proof",
     "Direct proof is defined for an implication P => Q and needs no "
     "quantifier to state. Levin's universally-quantified case is an extension "
     "of the technique, and dst never uses the words predicate or quantifier."),
    ("levin-dmoi:statements", "levin-dmoi:proof-by-contrapositive",
     "'statement' appears in dst only in a motivational aside about where the "
     "technique is useful. Reached transitively through propositional-logic."),
)


def load_levin_foundations_graph() -> ConceptGraph:
    """The foundational layer as a validated DAG. `sets` and `statements` are
    its only roots -- everything else in this repo's unified graph, including
    all of `teach.judson_algebra_graph`, sits downstream of these."""
    graph = ConceptGraph(nodes=load_levin_foundation_nodes(), edges=_EDGES)
    graph.validate()
    return graph


def _self_check() -> None:
    data = load_levin_foundations_data()
    nodes = load_levin_foundation_nodes()

    assert len(nodes) == 12, len(nodes)
    assert len({n.id for n in nodes}) == len(nodes), "duplicate node id"
    assert all(n.domain == DOMAIN for n in nodes)
    assert all(n.id.startswith("levin-dmoi:") for n in nodes)

    # The license claim this whole choice of text rests on. If someone
    # re-extracts from master (the 4th edition), this is the tripwire.
    assert LEVIN_SOURCE["license"] == "https://creativecommons.org/licenses/by-sa/4.0/"
    assert LEVIN_SOURCE["commit"] == "a8e4949bc45daf100930c1182983778f56ab689f"
    assert LEVIN_SOURCE["git_tag"] == "3rd-ed"
    assert "NC" in LEVIN_SOURCE["license_note"], (
        "the note warning that master is the NonCommercial 4th edition is gone"
    )

    by_id = {n.id: n for n in nodes}

    # Content spot-checks: each node must actually define what it is named
    # for, in Levin's words. A node whose text does not contain its own
    # subject is the failure mode this repo cares about -- it reads fluently
    # and teaches nothing.
    expected = {
        "levin-dmoi:sets": ("set", "unordered collection"),
        "levin-dmoi:set-operations": ("union", "intersection"),
        "levin-dmoi:statements": ("statement", "atomic"),
        "levin-dmoi:predicates-and-quantifiers": ("predicate", "quantifier"),
        "levin-dmoi:propositional-logic": ("tautology", "logically equivalent"),
        "levin-dmoi:deduction-rules": ("deduction rule", "modus ponens"),
        "levin-dmoi:functions": ("function", "codomain"),
        "levin-dmoi:function-properties": ("injective", "surjective"),
        "levin-dmoi:direct-proof": ("direct proof", "Assume $P$"),
        "levin-dmoi:proof-by-contrapositive": ("contrapositive", "logically equivalent"),
        "levin-dmoi:proof-by-contradiction": ("contradiction", r"\neg P"),
        "levin-dmoi:mathematical-induction": ("base case", "inductive case"),
    }
    for node_id, needles in expected.items():
        text = by_id[node_id].facts["definition"]
        for needle in needles:
            assert needle in text, f"{node_id} text is missing {needle!r}"

    # The Holmes regression: the deduction-rules node must explain deduction,
    # not open with the <investigation> puzzle that shares its subsection.
    assert "Holmes owns two suits" not in by_id["levin-dmoi:deduction-rules"].facts["definition"]

    # Every node is traceable to specific blocks in specific pinned files.
    for n in data["nodes"]:
        assert n["provenance"], f"{n['id']} has no provenance"
        for p in n["provenance"]:
            assert p["source_file"].endswith(".ptx")
            assert len(p["file_sha256"]) == 64
            assert p["kind"] in ("term-definition", "assemblage", "prose")

    # teach-ysm.2: the graph is a valid DAG with exactly the two roots the
    # content implies, and every refused edge stays refused.
    graph = load_levin_foundations_graph()
    order = graph.topological_order()
    assert len(order) == 12

    has_incoming = {e.dst for e in graph.edges}
    roots = tuple(n.id for n in graph.nodes if n.id not in has_incoming)
    assert set(roots) == {"levin-dmoi:sets", "levin-dmoi:statements"}, roots

    for src, dst in ((e.src, e.dst) for e in graph.edges):
        assert order.index(src) < order.index(dst)

    asserted = {(e.src, e.dst) for e in graph.edges}
    for src, dst, _why in REFUSED_EDGES:
        assert (src, dst) not in asserted, f"refused edge re-asserted: {src} -> {dst}"

    # The two overruled refutations are load-bearing structure, not taste: one
    # of them is the only thing keeping deduction-rules off the root set.
    assert ("levin-dmoi:statements", "levin-dmoi:deduction-rules") in asserted
    assert ("levin-dmoi:direct-proof", "levin-dmoi:proof-by-contrapositive") in asserted

    print(f"OK: {len(nodes)} foundational nodes from Levin DMOI 3rd ed "
          f"(CC BY-SA 4.0, commit {LEVIN_SOURCE['commit'][:7]}), "
          "each traceable to the pinned blocks it was extracted from")
    print(f"    {len(graph.edges)} edges, {len(REFUSED_EDGES)} refused and recorded; "
          f"roots: {', '.join(sorted(roots))}")


if __name__ == "__main__":
    _self_check()
