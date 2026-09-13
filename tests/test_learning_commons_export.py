"""teach-j4n.1: the Learning Commons record-shape export.

Most of these guard against a specific dishonest output rather than a broken
one. The schema has no place for a textbook prerequisite -- reaching
conformance would mean inventing a CASE identifier and declaring Judson's
group theory a US state standard -- so the tests that matter assert the
fabrications are absent and the caveat travels in the emitted bytes.
"""
import json
import uuid

import pytest

from teach.learning_commons_export import (
    LC_ENTITY,
    LC_RELATIONSHIP_TYPE,
    TEACH_RELATION,
    build_export,
    identifier_for,
)
from teach.methodological_bridge import EDGE_TYPE as METHODOLOGICAL_TYPE

REQUIRED_LEARNING_COMPONENT_PROPERTIES = (
    "academicSubject", "attributionStatement", "author", "description",
    "identifier", "inLanguage", "license", "provider",
)


@pytest.fixture(scope="module")
def files():
    return build_export()


@pytest.fixture(scope="module")
def nodes(files):
    return [json.loads(l) for l in files["nodes.jsonl"].decode().splitlines()]


@pytest.fixture(scope="module")
def rels(files):
    return [json.loads(l) for l in files["relationships.jsonl"].decode().splitlines()]


@pytest.fixture(scope="module")
def manifest(files):
    return json.loads(files["manifest.json"])


def test_export_is_the_three_learning_commons_files(files):
    assert set(files) == {"nodes.jsonl", "relationships.jsonl", "manifest.json"}


def test_node_records_are_conformant_learning_components(nodes):
    assert len(nodes) == 32
    for n in nodes:
        assert n["type"] == "node"
        assert n["labels"] == [LC_ENTITY]
        for prop in REQUIRED_LEARNING_COMPONENT_PROPERTIES:
            assert n["properties"].get(prop), (n["identifier"], prop)
        assert n["properties"]["academicSubject"] == "Mathematics"
        assert n["properties"]["inLanguage"] == "en-US"


def test_no_fabricated_standards_identity(nodes):
    """The dishonest route to conformance. StandardsFrameworkItem would reach
    the schema's real prerequisite relation, but it requires a CASE Network
    UUID these concepts do not have and a jurisdiction whose enum is the 50 US
    states plus D.C. A textbook has neither."""
    for n in nodes:
        props = n["properties"]
        assert "caseIdentifierUUID" not in props
        assert "caseIdentifierURI" not in props
        assert "jurisdiction" not in props
        assert "adoptionStatus" not in props


def test_provider_never_claims_learning_commons_published_this(nodes, rels):
    """Emitting "provider: Learning Commons" on records Learning Commons never
    published would be a fabricated attribution."""
    for n in nodes:
        assert "Learning Commons" not in n["properties"]["provider"]
        assert "Learning Commons" not in n["properties"]["author"]
    for r in rels:
        assert "Learning Commons" not in r["properties"]["provider"]


def test_identifiers_are_deterministic_uuids(nodes):
    ids = set()
    for n in nodes:
        uuid.UUID(n["identifier"])
        assert n["identifier"] == n["properties"]["identifier"]
        assert n["identifier"] not in ids
        ids.add(n["identifier"])
    assert identifier_for("levin-dmoi:sets") == identifier_for("levin-dmoi:sets")
    assert identifier_for("levin-dmoi:sets") != identifier_for("levin-dmoi:statements")


def test_export_is_byte_for_byte_deterministic(files):
    """So a diff between two exports means a real change, not noise."""
    assert build_export() == files


def test_relationships_reference_only_emitted_nodes(nodes, rels):
    known = {n["identifier"] for n in nodes}
    assert len(rels) == 48
    for r in rels:
        assert r["source_identifier"] in known
        assert r["target_identifier"] in known
        assert r["source_labels"] == r["target_labels"] == [LC_ENTITY]


def test_two_distinct_claims_share_one_lc_type_but_stay_distinguishable(rels):
    """Learning Commons has vocabulary for neither claim, so both land on
    buildsTowards. x_teachRelation is what keeps them apart -- "precedes"
    (dst's DEFINITION needs src) versus "methodological_prerequisite" (dst's
    PROOFS invoke src). Merging them would lose the distinction that made a
    second relation type necessary."""
    kinds = {}
    for r in rels:
        p = r["properties"]
        assert p["relationshipType"] == LC_RELATIONSHIP_TYPE
        assert p["x_teachRelation"] in (TEACH_RELATION, METHODOLOGICAL_TYPE)
        assert "WITHOUT requiring strict prerequisite order" in p["x_teachRelationNote"]
        kinds[p["x_teachRelation"]] = kinds.get(p["x_teachRelation"], 0) + 1
    assert kinds == {"precedes": 40, METHODOLOGICAL_TYPE: 8}, kinds


def test_methodological_edges_carry_their_proof_evidence(rels):
    """The evidence rule is "a <proof> in dst's section NAMES the method src
    defines", so the proof count and a verbatim excerpt must ship with it."""
    method = [r for r in rels
              if r["properties"]["x_teachRelation"] == METHODOLOGICAL_TYPE]
    assert len(method) == 8
    for r in method:
        p = r["properties"]
        assert p["x_teachEvidence"] == "named-method-in-proof-body"
        assert p["x_teachProofsMatched"] >= 1
        assert p["x_teachQuote"].strip()
        assert "PROOFS" in p["description"]
        # never a definitional claim
        assert "x_teachRequiredTerm" not in p


def test_no_llm_inferred_edge_is_present_and_the_absence_is_stated(rels, manifest):
    """127 LLM proposals, 127 refused. An absence is invisible, so the
    manifest has to say it happened rather than let the dataset look as
    though the bridge had always been definitional."""
    for r in rels:
        assert r["properties"]["x_teachEvidence"] in (
            "read-off-definition", "definitional-rule-adjudicated",
            "named-method-in-proof-body",
        )
        assert "llm" not in r["properties"]["x_teachEvidence"].lower()
    assert manifest["counts"]["llm_inferred_relationships"] == 0
    assert "NONE PRESENT" in manifest["edge_evidence"]["llm-inferred"]
    assert "127" in manifest["edge_evidence"]["llm-inferred"]


def test_manifest_declares_both_relation_types_and_the_coverage_limit(manifest):
    """teach-6xi: the second relation type has to be declared, not inferred
    from x_ fields a consumer may ignore."""
    rt = manifest["relation_types"]
    assert TEACH_RELATION in rt and METHODOLOGICAL_TYPE in rt
    assert rt[TEACH_RELATION]["count"] == 40
    assert rt[METHODOLOGICAL_TYPE]["count"] == 8
    assert "PROOFS" in rt[METHODOLOGICAL_TYPE]["claim"]
    # the coverage limit must ship: these edges are NOT exhaustive
    coverage = rt[METHODOLOGICAL_TYPE]["coverage"]
    assert "88" in coverage and "207" in coverage
    assert "NOT exhaustive" in coverage
    # and the refusals, including direct-proof
    assert "levin-dmoi:direct-proof" in rt[METHODOLOGICAL_TYPE]["refused"]


def test_licenses_travel_per_record_and_do_not_merge(nodes, rels):
    """Levin is CC BY-SA 4.0, Judson is GFDL 1.3+. Both copyleft, different.
    A dataset-level license would have to misstate one of them."""
    levin = [n for n in nodes if n["properties"]["x_teachNodeId"].startswith("levin-")]
    judson = [n for n in nodes if n["properties"]["x_teachNodeId"].startswith("judson:")]
    assert len(levin) == 12 and len(judson) == 20
    for n in levin:
        assert "by-sa" in n["properties"]["license"]
        assert "Oscar Levin" in n["properties"]["attributionStatement"]
    for n in judson:
        assert "fdl" in n["properties"]["license"]
        assert "Judson" in n["properties"]["attributionStatement"]


def test_cross_book_relationships_carry_both_copyleft_notices(rels):
    """An edge spanning two differently-licensed works cannot pick one. Applies
    to both kinds of cross-book edge: 6 definitional bridges + 8
    methodological."""
    bridges = [r for r in rels if r["properties"]["x_teachIsBridge"]]
    assert len(bridges) == 14
    for r in bridges:
        lic = r["properties"]["license"]
        assert "by-sa" in lic and "fdl" in lic
        assert r["properties"]["x_teachQuote"]
        attribution = r["properties"]["attributionStatement"]
        assert "Oscar Levin" in attribution and "Judson" in attribution

    definitional = [r for r in bridges
                    if r["properties"]["x_teachRelation"] == TEACH_RELATION]
    assert len(definitional) == 6
    for r in definitional:
        assert r["properties"]["x_teachRequiredTerm"]


def test_manifest_declares_the_relationship_extension_rather_than_hiding_it(manifest):
    """A consumer must not have to discover that these edges are outside the
    published schema."""
    conformance = manifest["schema_conformance"]
    assert "CONFORMANT" in conformance["nodes"]
    assert "EXTENSION, NOT CONFORMANT" in conformance["relationships"]
    assert "LearningComponent -> LearningComponent" in conformance["relationships"]
    assert "caseIdentifier" in conformance["why_not_standardsframeworkitem"]
    assert "jurisdiction" in conformance["why_not_standardsframeworkitem"]
    assert "generalizes" in conformance["unrepresentable_relations"]


def test_manifest_records_both_licenses_and_the_levin_edition_trap(manifest):
    prov = manifest["provenance"]
    assert "by-sa" in prov["foundational_half"]["license"]
    assert "fdl" in prov["algebraic_half"]["license"]
    assert prov["foundational_half"]["commit"] == "a8e4949bc45daf100930c1182983778f56ab689f"
    assert "NC" in prov["foundational_half"]["note"]
    assert "do not merge" in prov["licenses_do_not_merge"].lower() or \
        "different copyleft" in prov["licenses_do_not_merge"]


# --------------------------------------------------------------------------
# teach-j4n.2: the dataset actually written to disk.

from teach.learning_commons_export import OUTPUT_DIR  # noqa: E402

needs_written = pytest.mark.skipif(
    not OUTPUT_DIR.is_dir(), reason=f"dataset not written to {OUTPUT_DIR}"
)


@needs_written
def test_written_dataset_matches_what_the_builder_produces(files):
    """Drift guard. The committed dataset is a derived artifact; if it and the
    builder disagree, one of them is stale and a consumer cannot tell which."""
    for name, payload in files.items():
        on_disk = (OUTPUT_DIR / name).read_bytes()
        assert on_disk == payload, f"{name} on disk differs from build_export()"


@needs_written
def test_manifest_records_the_upstream_bytes_each_half_came_from():
    """teach-8xw.54's rule: "which graph was this planned from" must have an
    answer after the fact, so the pinned commit and per-file hashes ship with
    the dataset."""
    manifest = json.loads((OUTPUT_DIR / "manifest.json").read_bytes())
    upstream = manifest["upstream_bytes"]
    assert upstream["judson-aata"]["commit"] == "3069910e3ded72ff5e18837a97a0e810c92790e2"
    assert upstream["levin-dmoi"]["commit"] == "a8e4949bc45daf100930c1182983778f56ab689f"
    for half in upstream.values():
        assert len(half["tarball_sha256"]) == 64
        assert half["source_files"] > 0


@needs_written
def test_manifest_carries_the_failed_llm_bridge_measurement():
    """A dataset that simply contains no LLM edges is indistinguishable from
    one where the stage was never run. The numbers have to ship."""
    manifest = json.loads((OUTPUT_DIR / "manifest.json").read_bytes())
    attempt = manifest["llm_bridge_attempt"]
    assert attempt["pairs_asked"] == 240
    assert attempt["relations_proposed"] == 127
    assert attempt["confirmed"] == 0
    assert attempt["verdicts"] == {"refused": 127}
    assert attempt["producer_model"] != attempt["checker_model"], (
        "producer and checker must not be the same model"
    )
    assert attempt["checker_independence"]
