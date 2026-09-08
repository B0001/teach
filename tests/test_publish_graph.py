"""teach-8xw.14: the HuggingFace publish pipeline builds the right dataset
files from a ConceptGraph, and its dry-run path never requires (or reaches
for) a live HF_TOKEN. This is the "runnable check covering at least the
dry-run path" the bead asks for.
"""
import json

import pytest

from teach.concept_graph import ConceptGraph, ConceptNode, GraphError, PrerequisiteEdge
from teach.publish_graph import build_dataset_files, publish

SOURCE = {"provider": "test-fixture", "license": "n/a"}


def _two_node_graph() -> ConceptGraph:
    a = ConceptNode(
        id="dom:a", domain="test", label="A", standard_ref="A.1", facts={"k": "v"}
    )
    b = ConceptNode(id="dom:b", domain="test", label="B")
    return ConceptGraph(nodes=(a, b), edges=(PrerequisiteEdge(src="dom:a", dst="dom:b"),))


def test_build_dataset_files_is_offline_and_returns_expected_paths():
    files = build_dataset_files(_two_node_graph(), source=SOURCE, repo_id="org/repo")
    assert set(files) == {"nodes.jsonl", "associations.jsonl", "manifest.json", "README.md"}
    assert all(isinstance(content, bytes) for content in files.values())


def test_nodes_jsonl_has_one_record_per_node_with_facts_forwarded_unread():
    files = build_dataset_files(_two_node_graph(), source=SOURCE)
    records = [json.loads(line) for line in files["nodes.jsonl"].decode().splitlines()]
    assert len(records) == 2
    by_id = {r["identifier"]: r for r in records}
    assert by_id["dom:a"]["fullStatement"] == "A"
    assert by_id["dom:a"]["humanCodingScheme"] == "A.1"
    assert by_id["dom:a"]["facts"] == {"k": "v"}
    assert by_id["dom:b"]["humanCodingScheme"] is None


def test_associations_jsonl_uses_case_precedes_direction():
    files = build_dataset_files(_two_node_graph(), source=SOURCE)
    records = [
        json.loads(line) for line in files["associations.jsonl"].decode().splitlines()
    ]
    assert len(records) == 1
    assert records[0]["associationType"] == "precedes"
    assert records[0]["originNodeURI"] == "dom:a"
    assert records[0]["destinationNodeURI"] == "dom:b"


def test_manifest_records_schema_counts_and_source_verbatim():
    files = build_dataset_files(_two_node_graph(), source=SOURCE)
    manifest = json.loads(files["manifest.json"])
    assert manifest["node_count"] == 2
    assert manifest["edge_count"] == 1
    assert manifest["domains"] == ["test"]
    assert manifest["source"] == SOURCE


def test_readme_dataset_card_names_repo_and_counts():
    files = build_dataset_files(_two_node_graph(), source=SOURCE, repo_id="org/repo")
    readme = files["README.md"].decode()
    assert readme.startswith("---\n")  # YAML front matter for the HF dataset card
    assert "org/repo" in readme
    assert "Nodes: 2" in readme
    assert "Edges: 1" in readme


def test_build_dataset_files_is_deterministic_across_calls():
    graph = _two_node_graph()
    first = build_dataset_files(graph, source=SOURCE, repo_id="org/repo")
    second = build_dataset_files(graph, source=SOURCE, repo_id="org/repo")
    assert first == second


def test_build_dataset_files_rejects_a_structurally_invalid_graph():
    cyclic = ConceptGraph(
        nodes=(ConceptNode(id="a", domain="test", label="A"),),
        edges=(PrerequisiteEdge(src="a", dst="missing"),),
    )
    with pytest.raises(GraphError):
        build_dataset_files(cyclic, source=SOURCE)


def test_publish_defaults_to_dry_run_with_no_token_and_touches_no_network(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    result = publish(_two_node_graph(), "org/repo", source=SOURCE)
    assert result.dry_run is True
    assert result.repo_url is None
    assert result.repo_id == "org/repo"
    assert set(result.files) == {"nodes.jsonl", "associations.jsonl", "manifest.json", "README.md"}
    assert result.total_bytes > 0


def test_publish_dry_run_explicit_true_ignores_a_present_token(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "not-a-real-token")
    result = publish(_two_node_graph(), "org/repo", source=SOURCE, dry_run=True)
    assert result.dry_run is True
    assert result.repo_url is None


def test_publish_live_without_any_token_raises_instead_of_silently_downgrading(
    monkeypatch,
):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with pytest.raises(ValueError):
        publish(_two_node_graph(), "org/repo", source=SOURCE, dry_run=False)


def test_publish_dry_run_file_bytes_match_build_dataset_files_directly(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    graph = _two_node_graph()
    result = publish(graph, "org/repo", source=SOURCE)
    direct = build_dataset_files(graph, source=SOURCE, repo_id="org/repo")
    assert result.total_bytes == sum(len(c) for c in direct.values())
