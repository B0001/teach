"""Emit the unified graph in the Learning Commons Knowledge Graph record shape
(teach-j4n.1).

Pure, offline and deterministic: `build_export()` returns the exact bytes a
write would produce, so it can be diffed and tested without touching a
network or a filesystem.

THE SCHEMA DOES NOT HAVE A PLACE FOR WHAT THIS GRAPH ASSERTS

This is the central fact about this mapping and it is not a complaint about
Learning Commons -- their schema models US academic standards, and a textbook
prerequisite graph is not that. Verified against docs.learningcommons.org
(fetched, not recalled) on 2026-09-13:

  - `LearningComponent` is the entity our concepts genuinely are: "a single,
    well-defined skill or concept that students are expected to learn". Every
    one of its required properties (academicSubject, attributionStatement,
    author, description, identifier, inLanguage, license, provider) is
    something we legitimately have. BUT its only defined relationship is
    `supports`, pointing at a `StandardsFrameworkItem`. There is NO
    LearningComponent -> LearningComponent relationship in the schema at all.
  - `buildsTowards` is the schema's nearest thing to a prerequisite. It runs
    `StandardsFrameworkItem` -> `StandardsFrameworkItem`, and its own
    definition says it captures "a directional progression WITHOUT requiring
    strict prerequisite order" -- strictly weaker than
    `PrerequisiteEdge`, which means src must be established before dst.
  - Modelling our concepts as `StandardsFrameworkItem` to reach
    `buildsTowards` would require `caseIdentifierURI` and `caseIdentifierUUID`
    (cardinality 1 -- identifiers in 1EdTech's CASE Network, which these
    concepts do not have) and `jurisdiction` (cardinality 1, and
    `JurisdictionENUM` is the 50 US states plus Washington, D.C. -- there is
    no non-US value, and a textbook has no jurisdiction at all).

So there are three honest options and one dishonest one. The dishonest one is
inventing a CASE UUID and calling Judson's group theory a Virginia standard;
that is not on the table. What this module does instead:

  * nodes are `LearningComponent`, fully conformant;
  * relationships are LearningComponent -> LearningComponent carrying
    `relationshipType: "buildsTowards"`, which is an EXTENSION beyond the
    published schema, declared as such in the manifest rather than left for a
    consumer to discover;
  * every record additionally carries `x_teach*` fields preserving what the
    edge actually claims and what established it.

`MANIFEST["schema_conformance"]` states all of this in the emitted bytes, so
the caveat travels with the data instead of living only in this docstring.

WHY THE `x_teach*` FIELDS EXIST (repo owner's decision, 2026-09-13)

"Map to the nearest LC relationshipType AND keep the original alongside."
`buildsTowards` loses two distinctions that matter:

  - strictness. Our edges mean "must be established before"; buildsTowards
    explicitly does not. `x_teachRelation: "precedes"` records what was meant.
  - evidence. An edge read off a definition and an edge guessed by a language
    model are different claims. `x_teachEvidence` separates them. In this
    dataset every edge is definitional -- the LLM stage (teach-b5k.2)
    proposed 127 relations and the independent checker (teach-b5k.3) refused
    all 127, so not one LLM-inferred edge is present. That is recorded in the
    manifest rather than silently showing up as an absence.

LICENSES DO NOT MERGE

Levin is CC BY-SA 4.0 and Judson is GFDL 1.3+ -- both copyleft, and different.
There is no single license for this dataset, so there is no dataset-level
license field: every record carries its own `license`, `attributionStatement`
and `author`, and a bridge relationship spanning both carries both notices.
`provider` names the textbook author, never Learning Commons -- emitting
"provider: Learning Commons" on records Learning Commons never published would
be a fabricated attribution.
"""
from __future__ import annotations

import json
import pathlib
import uuid

from teach.definitional_bridge import (
    BRIDGE_EDGES,
    EVIDENCE as BRIDGE_EVIDENCE,
    load_unified_graph,
)
from teach.methodological_bridge import (
    EDGE_TYPE as METHODOLOGICAL_TYPE,
    METHODOLOGICAL_EDGES,
    PROOFS_IN_MODELLED_SECTIONS,
    REFUSED_METHODS,
    TOTAL_PROOFS,
    load_graph_with_methodological_edges,
)
from teach.judson_algebra_graph import JUDSON_SOURCE
from teach.levin_foundations_graph import LEVIN_SOURCE

#: Fixed namespace for deterministic identifiers. LC identifiers are UUIDs;
#: ours are uuid5 over this namespace and our own node id, so the same graph
#: always emits the same identifiers and a diff between two exports is
#: meaningful rather than noise.
NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/teach/unified-concept-graph")

LC_ENTITY = "LearningComponent"
LC_RELATIONSHIP_TYPE = "buildsTowards"
ACADEMIC_SUBJECT = "Mathematics"  # AcademicSubjectENUM
IN_LANGUAGE = "en-US"  # LanguageENUM

#: Our own relation, preserved alongside the LC one.
TEACH_RELATION = "precedes"

_LEVIN_PREFIX = "levin-dmoi:"
_JUDSON_PREFIX = "judson:"


def identifier_for(node_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE, node_id))


def _source_for(node_id: str) -> dict:
    """Which textbook a node came from. Its license travels with it."""
    if node_id.startswith(_LEVIN_PREFIX):
        return {
            "author": LEVIN_SOURCE["author"],
            "provider": LEVIN_SOURCE["provider"],
            "license": LEVIN_SOURCE["license"],
            "attributionStatement": LEVIN_SOURCE["attribution"],
        }
    if node_id.startswith(_JUDSON_PREFIX):
        return {
            "author": JUDSON_SOURCE["author"],
            "provider": JUDSON_SOURCE["provider"],
            "license": JUDSON_SOURCE["license"],
            "attributionStatement": JUDSON_SOURCE["attribution"],
        }
    raise KeyError(f"no source known for node id {node_id!r}")


def node_record(node) -> dict:
    """One LearningComponent record. Conformant: every required property is
    present and legitimately ours."""
    src = _source_for(node.id)
    facts = node.facts
    terms = facts.get("terms") or facts.get("key_terms") or ()
    return {
        "type": "node",
        "identifier": identifier_for(node.id),
        "labels": [LC_ENTITY],
        "properties": {
            "academicSubject": ACADEMIC_SUBJECT,
            "attributionStatement": src["attributionStatement"],
            "author": src["author"],
            "description": str(facts.get("definition", "")),
            "identifier": identifier_for(node.id),
            "inLanguage": IN_LANGUAGE,
            "license": src["license"],
            "provider": src["provider"],
            "name": node.label,
            # -- extensions: what LC has no field for --
            "x_teachNodeId": node.id,
            "x_teachStandardRef": node.standard_ref,
            "x_teachTerms": list(terms),
            "x_teachDomain": node.domain,
        },
    }


def _bridge_lookup() -> dict:
    return {(src, dst): (term, quote) for src, dst, term, quote in BRIDGE_EDGES}


def _methodological_lookup() -> dict:
    return {(src, dst): (n, quote) for src, dst, n, quote in METHODOLOGICAL_EDGES}


def relationship_record(edge, bridge: dict) -> dict:
    """One relationship record.

    EXTENSION, declared: `buildsTowards` between two LearningComponents is not
    in the published schema (there it runs StandardsFrameworkItem ->
    StandardsFrameworkItem). See the module docstring for why the conformant
    route is not available without fabricating a CASE identifier and a US
    jurisdiction.
    """
    key = (edge.src, edge.dst)
    is_bridge = key in bridge
    methodological = _methodological_lookup()
    is_methodological = edge.type == METHODOLOGICAL_TYPE
    src_source, dst_source = _source_for(edge.src), _source_for(edge.dst)

    if src_source["license"] == dst_source["license"]:
        license_ = src_source["license"]
        attribution = src_source["attributionStatement"]
        author = src_source["author"]
        provider = src_source["provider"]
    else:
        # A bridge edge spans two different copyleft licenses. They do not
        # merge, so both notices travel with the edge.
        license_ = f"{src_source['license']} AND {dst_source['license']}"
        attribution = (
            f"This relationship connects two independently licensed works. "
            f"Source: {src_source['attributionStatement']} "
            f"Target: {dst_source['attributionStatement']}"
        )
        author = f"{src_source['author']}; {dst_source['author']}"
        provider = f"{src_source['provider']}; {dst_source['provider']}"

    rel_id = str(uuid.uuid5(NAMESPACE, f"{edge.src}->{edge.dst}"))
    props = {
        "attributionStatement": attribution,
        "author": author,
        "description": (
            "The target's PROOFS invoke the method the source defines. This is a "
            "methodological prerequisite, not a definitional one: the target's "
            "definition does not use the source's vocabulary."
            if is_methodological else
            "The source concept must be established before the target concept: "
            "the target's definition cannot be stated without a term the source "
            "defines."
        ),
        "identifier": rel_id,
        "license": license_,
        "provider": provider,
        "relationshipType": LC_RELATIONSHIP_TYPE,
        "sourceEntity": LC_ENTITY,
        "sourceEntityKey": "identifier",
        "targetEntity": LC_ENTITY,
        "targetEntityKey": "identifier",
        # -- extensions: what buildsTowards cannot say --
        "x_teachRelation": METHODOLOGICAL_TYPE if is_methodological else TEACH_RELATION,
        "x_teachRelationNote": (
            "buildsTowards is documented as a directional progression WITHOUT "
            "requiring strict prerequisite order. That is a closer fit for this "
            "edge than for the definitional ones: a methodological prerequisite "
            "genuinely is a progression rather than a strict ordering."
            if is_methodological else
            "buildsTowards is documented as a directional progression WITHOUT "
            "requiring strict prerequisite order. This edge is strictly "
            "stronger: the source must be established before the target."
        ),
        "x_teachEvidence": (
            "named-method-in-proof-body" if is_methodological
            else BRIDGE_EVIDENCE if is_bridge else "read-off-definition"
        ),
        "x_teachIsBridge": is_bridge or is_methodological,
    }
    if is_methodological:
        n_proofs, quote = methodological[key]
        props["x_teachProofsMatched"] = n_proofs
        props["x_teachQuote"] = quote
    elif is_bridge:
        term, quote = bridge[key]
        props["x_teachRequiredTerm"] = term
        props["x_teachQuote"] = quote

    return {
        "type": "relationship",
        "identifier": rel_id,
        "label": LC_RELATIONSHIP_TYPE,
        "properties": props,
        "source_identifier": identifier_for(edge.src),
        "source_labels": [LC_ENTITY],
        "target_identifier": identifier_for(edge.dst),
        "target_labels": [LC_ENTITY],
    }


def _upstream_bytes() -> dict:
    """What upstream bytes the extracts were built from (teach-8xw.54's rule):
    a pinned commit and a sha256 per source file, so "which graph was this
    planned from" has an answer after the fact."""
    path = pathlib.Path(__file__).parent / "data" / "textbook_provenance.json"
    record = json.loads(path.read_text())
    return {
        key: {
            "repo": src["repo"],
            "commit": src["commit"],
            "tarball_sha256": src["tarball_sha256"],
            "license": src["license"],
            "source_files": len(src.get("files", {})),
            "per_file_sha256": "teach/data/textbook_provenance.json",
        }
        for key, src in record["sources"].items()
    }


def _checker_verdicts() -> dict:
    """The LLM bridge's measured outcome. Carried into the manifest because a
    dataset that simply contains no LLM edges is indistinguishable from one
    where the stage was never run."""
    path = pathlib.Path(__file__).parent / "data" / "bridge_verdicts.json"
    if not path.is_file():
        return {"status": "not run"}
    v = json.loads(path.read_text())
    return {
        "producer_model": json.loads(
            (pathlib.Path(__file__).parent / "data"
             / "semantic_bridge_candidates.json").read_text()
        )["producer"]["model"],
        "checker_model": v["checker"]["model"],
        "pairs_asked": 240,
        "relations_proposed": v["checked"],
        "verdicts": v["counts"],
        "confirmed": v["counts"].get("confirmed", 0),
        "checker_independence": v["checker"]["does_not_see"],
        "note": (
            "Every proposed relation was refused. The zero is a fact about the "
            "producer, not the mathematics: a mechanical scan finds real "
            "textual evidence on 22 of the 240 pairs, and the model proposed "
            "none of them. The bridge in this dataset is definitional instead."
        ),
    }


def build_manifest(graph, bridge: dict) -> dict:
    n_bridge = sum(1 for e in graph.edges if (e.src, e.dst) in bridge)
    n_method = sum(1 for e in graph.edges if e.type == METHODOLOGICAL_TYPE)
    return {
        "schema": "learning-commons-knowledge-graph-record-shape",
        "generated_by": "teach/learning_commons_export.py (teach-j4n.1)",
        "counts": {
            "nodes": len(graph.nodes),
            "relationships": len(graph.edges),
            "definitional_relationships": len(graph.edges) - n_method,
            "methodological_relationships": n_method,
            "bridge_relationships": n_bridge,
            "llm_inferred_relationships": 0,
        },
        "relation_types": {
            "note": (
                "Two distinct claims share one Learning Commons relationshipType "
                "because Learning Commons has vocabulary for neither. They are kept "
                "apart by x_teachRelation, never merged."
            ),
            TEACH_RELATION: {
                "claim": "The target's DEFINITION cannot be stated without a term "
                         "the source defines.",
                "evidence": "Read off the definition text in the pinned PreTeXt "
                            "source, adjudicated.",
                "count": len(graph.edges) - n_method,
                "vs_buildsTowards": "STRICTLY STRONGER than buildsTowards, which "
                                    "explicitly does not require prerequisite order.",
            },
            METHODOLOGICAL_TYPE: {
                "claim": "The target's PROOFS invoke the inference method the "
                         "source defines. The target's definition does NOT use the "
                         "source's vocabulary -- this is why the definitional rule "
                         "could never find these edges.",
                "evidence": "The method is NAMED in a <proof> element inside the "
                            "target's section (e.g. 'We will use mathematical "
                            "induction on the degree of p(x)'). Each edge carries "
                            "the proof count and a verbatim excerpt.",
                "count": n_method,
                "vs_buildsTowards": "A CLOSER fit for buildsTowards than the "
                                    "definitional edges are: a methodological "
                                    "prerequisite genuinely is a directional "
                                    "progression rather than a strict ordering.",
                "coverage": (
                    f"Derived from {PROOFS_IN_MODELLED_SECTIONS} of Judson's "
                    f"{TOTAL_PROOFS} <proof> elements -- the other "
                    f"{TOTAL_PROOFS - PROOFS_IN_MODELLED_SECTIONS} are in chapters "
                    "this graph models no node for (galois, algcodes, boolean, "
                    "finite, sylow, actions, struct, ...). NOT exhaustive."
                ),
                "refused": {node_id: why for node_id, why in REFUSED_METHODS},
            },
        },
        "schema_conformance": {
            "nodes": (
                "CONFORMANT. Every record is a LearningComponent and carries all "
                "eight required properties (academicSubject, attributionStatement, "
                "author, description, identifier, inLanguage, license, provider)."
            ),
            "relationships": (
                "EXTENSION, NOT CONFORMANT. These are LearningComponent -> "
                "LearningComponent edges carrying relationshipType "
                "'buildsTowards'. The published schema defines no "
                "LearningComponent -> LearningComponent relationship at all: "
                "LearningComponent's only relationship is 'supports', which "
                "points at a StandardsFrameworkItem, and 'buildsTowards' runs "
                "between StandardsFrameworkItems."
            ),
            "why_not_standardsframeworkitem": (
                "StandardsFrameworkItem requires caseIdentifierURI and "
                "caseIdentifierUUID (identifiers in 1EdTech's CASE Network, which "
                "these textbook concepts do not have) and jurisdiction, whose "
                "enum is the 50 US states plus Washington, D.C. A textbook has no "
                "jurisdiction. Emitting these would be fabricated identifiers and "
                "a fabricated jurisdiction, so the extension above was preferred "
                "over false conformance."
            ),
            "semantic_gap": (
                "buildsTowards is documented as a directional progression "
                "WITHOUT requiring strict prerequisite order. Every edge here is "
                "strictly stronger than that -- src must be established before "
                "dst -- so x_teachRelation records the real claim."
            ),
            "unrepresentable_relations": (
                "The plan also asked for 'generalizes' and 'is example of'. "
                "Learning Commons has no vocabulary for either, and no edge of "
                "those kinds survived verification, so none is emitted. Had any "
                "survived, it would have carried x_teachRelation rather than "
                "being flattened into buildsTowards."
            ),
        },
        "provenance": {
            "foundational_half": {
                "text": LEVIN_SOURCE["provider"],
                "license": LEVIN_SOURCE["license"],
                "commit": LEVIN_SOURCE["commit"],
                "note": LEVIN_SOURCE["license_note"],
            },
            "algebraic_half": {
                "text": JUDSON_SOURCE["provider"],
                "license": JUDSON_SOURCE["license"],
                "retrieved_via": JUDSON_SOURCE["retrieved_via"],
            },
            "licenses_do_not_merge": (
                "CC BY-SA 4.0 and GFDL 1.3+ are different copyleft licenses. "
                "There is no dataset-level license: each record carries its own, "
                "and a bridge relationship spanning both carries both notices."
            ),
        },
        "upstream_bytes": _upstream_bytes(),
        "llm_bridge_attempt": _checker_verdicts(),
        "edge_evidence": {
            "read-off-definition": (
                "Asserted only where the target's definition cannot be stated "
                "without a term the source defines, read from the pinned PreTeXt "
                "source."
            ),
            BRIDGE_EVIDENCE: (
                "Same rule, applied across the two textbooks, with independent "
                "adjudication and an independent refutation pass."
            ),
            "llm-inferred": (
                "NONE PRESENT. teach-b5k.2 had a local model propose 127 "
                "relations over all 240 foundation/algebra pairs; teach-b5k.3's "
                "independent checker refused all 127, so no LLM-inferred edge "
                "reached this dataset. Recorded here because an absence is "
                "invisible otherwise."
            ),
        },
    }


def build_export() -> dict[str, bytes]:
    """The exact files an export writes. Pure, offline, deterministic."""
    graph = load_graph_with_methodological_edges()
    bridge = _bridge_lookup()

    nodes = [node_record(n) for n in graph.nodes]
    rels = [relationship_record(e, bridge) for e in graph.edges]

    def jsonl(records: list[dict]) -> bytes:
        return ("\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n").encode()

    return {
        "nodes.jsonl": jsonl(nodes),
        "relationships.jsonl": jsonl(rels),
        "manifest.json": (
            json.dumps(build_manifest(graph, bridge), indent=2, sort_keys=True) + "\n"
        ).encode(),
    }


OUTPUT_DIR = pathlib.Path(__file__).parent / "data" / "learning_commons_export"


def main() -> None:
    """Write the final bridged dataset (teach-j4n.2).

    Writes files only. Publishing is NOT in scope: teach-8xw.57 says the
    Judson graph is not to be published until teach-8xw.55's per-graph repo
    layout exists, and nothing here pushes anywhere.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = build_export()
    for name, payload in sorted(files.items()):
        (OUTPUT_DIR / name).write_bytes(payload)
        print(f"  wrote {OUTPUT_DIR.relative_to(pathlib.Path(__file__).parent.parent)}/"
              f"{name}  {len(payload):,} bytes")
    manifest = json.loads(files["manifest.json"])
    print(f"counts: {manifest['counts']}")


def _self_check() -> None:
    files = build_export()
    assert set(files) == {"nodes.jsonl", "relationships.jsonl", "manifest.json"}

    nodes = [json.loads(l) for l in files["nodes.jsonl"].decode().splitlines()]
    rels = [json.loads(l) for l in files["relationships.jsonl"].decode().splitlines()]
    manifest = json.loads(files["manifest.json"])

    assert len(nodes) == 32, len(nodes)
    assert len(rels) == 48, len(rels)
    method = [r for r in rels
              if r["properties"]["x_teachRelation"] == METHODOLOGICAL_TYPE]
    assert len(method) == 8, len(method)

    required = ("academicSubject", "attributionStatement", "author", "description",
                "identifier", "inLanguage", "license", "provider")
    ids = set()
    for n in nodes:
        assert n["type"] == "node"
        assert n["labels"] == [LC_ENTITY]
        for prop in required:
            assert n["properties"].get(prop), (n["identifier"], prop)
        assert n["properties"]["academicSubject"] == "Mathematics"
        # never claim Learning Commons published this
        assert "Learning Commons" not in n["properties"]["provider"]
        # identifiers are UUIDs and unique
        uuid.UUID(n["identifier"])
        assert n["identifier"] not in ids
        ids.add(n["identifier"])
        # no fabricated standards identity
        assert "caseIdentifierUUID" not in n["properties"]
        assert "jurisdiction" not in n["properties"]

    by_uuid = {n["identifier"]: n for n in nodes}
    for r in rels:
        assert r["type"] == "relationship"
        assert r["label"] == LC_RELATIONSHIP_TYPE
        assert r["source_identifier"] in by_uuid
        assert r["target_identifier"] in by_uuid
        p = r["properties"]
        assert p["relationshipType"] == LC_RELATIONSHIP_TYPE
        assert p["sourceEntity"] == p["targetEntity"] == LC_ENTITY
        assert p["x_teachRelation"] in (TEACH_RELATION, METHODOLOGICAL_TYPE)
        assert p["x_teachEvidence"] in (
            "read-off-definition", BRIDGE_EVIDENCE, "named-method-in-proof-body"
        )
        assert "llm" not in p["x_teachEvidence"].lower()

    # Methodological edges carry their proof evidence.
    for r in method:
        assert r["properties"]["x_teachProofsMatched"] >= 1
        assert r["properties"]["x_teachQuote"]
        assert r["properties"]["x_teachEvidence"] == "named-method-in-proof-body"
        assert "PROOFS" in r["properties"]["description"]

    # Licenses travel per record. Every cross-book edge -- definitional bridge
    # or methodological -- spans CC BY-SA and GFDL, so both notices ride along.
    bridges = [r for r in rels if r["properties"]["x_teachIsBridge"]]
    assert len(bridges) == 6 + 8, len(bridges)
    for r in bridges:
        assert " AND " in r["properties"]["license"]
        assert "by-sa" in r["properties"]["license"]
        assert "fdl" in r["properties"]["license"]

    definitional_bridges = [r for r in bridges
                            if r["properties"]["x_teachRelation"] == TEACH_RELATION]
    assert len(definitional_bridges) == 6, len(definitional_bridges)
    for r in definitional_bridges:
        assert r["properties"]["x_teachRequiredTerm"]

    levin_nodes = [n for n in nodes if n["properties"]["x_teachNodeId"].startswith("levin-")]
    judson_nodes = [n for n in nodes if n["properties"]["x_teachNodeId"].startswith("judson:")]
    assert len(levin_nodes) == 12 and len(judson_nodes) == 20
    assert all("by-sa" in n["properties"]["license"] for n in levin_nodes)
    assert all("fdl" in n["properties"]["license"] for n in judson_nodes)

    assert manifest["counts"]["llm_inferred_relationships"] == 0
    assert manifest["counts"]["methodological_relationships"] == 8
    assert METHODOLOGICAL_TYPE in manifest["relation_types"]
    assert TEACH_RELATION in manifest["relation_types"]
    assert manifest["relation_types"][METHODOLOGICAL_TYPE]["refused"]
    assert "EXTENSION" in manifest["schema_conformance"]["relationships"]
    assert "NONE PRESENT" in manifest["edge_evidence"]["llm-inferred"]

    # Deterministic: same graph, same bytes.
    assert build_export() == files

    print(f"OK: {len(nodes)} LearningComponent nodes, {len(rels)} relationships "
          f"({len(rels) - len(method)} definitional + {len(method)} "
          f"{METHODOLOGICAL_TYPE}), deterministic")
    print("    nodes conformant; relationships declared as an EXTENSION "
          "(LC has no LearningComponent -> LearningComponent relation)")


if __name__ == "__main__":
    import sys

    if "--write" in sys.argv:
        main()
    else:
        _self_check()
