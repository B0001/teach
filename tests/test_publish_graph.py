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


def test_publish_live_pushes_all_files_in_a_single_commit(monkeypatch):
    """teach-8xw.24: a failed publish must not leave a partially-populated
    public dataset -- so the live path has to be one `create_commit` call
    carrying every file, not one `upload_file` (== one commit) per file.
    This mocks `HfApi` so the regression is caught offline, without a live
    $HF_TOKEN; the real network behaviour was verified separately against an
    actual scratch HF dataset repo, per the bead's acceptance criteria.
    """
    import huggingface_hub

    create_commit_calls = []
    upload_file_calls = []

    class _FakeRepoUrl:
        repo_id = "canonical-org/repo"

        def __str__(self):
            return "https://huggingface.co/datasets/canonical-org/repo"

    class _FakeHfApi:
        def __init__(self, token=None):
            self.token = token

        def create_repo(self, repo_id, *, repo_type, private, exist_ok):
            return _FakeRepoUrl()

        def upload_file(self, **kwargs):
            upload_file_calls.append(kwargs)

        def create_commit(self, *, repo_id, repo_type, operations, commit_message):
            create_commit_calls.append(
                {
                    "repo_id": repo_id,
                    "repo_type": repo_type,
                    "operations": list(operations),
                    "commit_message": commit_message,
                }
            )

    monkeypatch.setattr(huggingface_hub, "HfApi", _FakeHfApi)

    graph = _two_node_graph()
    result = publish(graph, "org/repo", source=SOURCE, token="fake-token", dry_run=False)

    assert upload_file_calls == [], "must not fall back to one-commit-per-file uploads"
    assert len(create_commit_calls) == 1, "all files must land in exactly one commit"
    call = create_commit_calls[0]
    assert call["repo_id"] == "canonical-org/repo"
    assert call["repo_type"] == "dataset"
    paths = {op.path_in_repo for op in call["operations"]}
    assert paths == {"nodes.jsonl", "associations.jsonl", "manifest.json", "README.md"}
    assert result.repo_id == "canonical-org/repo"
    assert result.dry_run is False
