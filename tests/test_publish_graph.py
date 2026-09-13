"""teach-8xw.14: the HuggingFace publish pipeline builds the right dataset
files from a ConceptGraph, and its dry-run path never requires (or reaches
for) a live HF_TOKEN. This is the "runnable check covering at least the
dry-run path" the bead asks for.
"""
import dataclasses
import json

import pytest

from teach.concept_graph import ConceptGraph, ConceptNode, GraphError, PrerequisiteEdge
from teach.publish_graph import (
    GraphSpec,
    LEGACY_ROOT_FILES,
    build_dataset_files,
    build_multi_graph_dataset_files,
    publish,
    publish_many,
)

SOURCE = {"provider": "test-fixture", "license": "n/a"}
SOURCE_CC_BY = {"provider": "test-fixture-2", "license": "https://creativecommons.org/licenses/by/4.0/"}


def _two_node_graph() -> ConceptGraph:
    a = ConceptNode(
        id="dom:a", domain="test", label="A", standard_ref="A.1", facts={"k": "v"}
    )
    b = ConceptNode(id="dom:b", domain="test", label="B")
    return ConceptGraph(nodes=(a, b), edges=(PrerequisiteEdge(src="dom:a", dst="dom:b"),))


def _one_node_graph(id_: str, domain: str) -> ConceptGraph:
    return ConceptGraph(nodes=(ConceptNode(id=id_, domain=domain, label=id_),), edges=())


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


# teach-8xw.55: one shared repo for many graphs, each in its own directory
# with its own manifest/license/source, plus a root index. See
# `publish_graph.py`'s module docstring for the layout.


def _two_specs():
    return (
        GraphSpec(
            key="g1",
            loader=_two_node_graph,
            source=lambda: SOURCE,
            description="first graph",
        ),
        GraphSpec(
            key="g2",
            loader=lambda: _one_node_graph("dom2:c", "test2"),
            source=lambda: SOURCE_CC_BY,
            description="second graph",
        ),
    )


def test_build_multi_graph_dataset_files_namespaces_paths_per_graph():
    files = build_multi_graph_dataset_files(_two_specs(), repo_id="org/repo")
    assert set(files) == {
        "g1/nodes.jsonl", "g1/associations.jsonl", "g1/manifest.json",
        "g2/nodes.jsonl", "g2/associations.jsonl", "g2/manifest.json",
        "index.json", "README.md",
    }


def test_multi_graph_manifest_carries_its_own_license_and_source_only():
    files = build_multi_graph_dataset_files(_two_specs(), repo_id="org/repo")
    g1 = json.loads(files["g1/manifest.json"])
    g2 = json.loads(files["g2/manifest.json"])
    assert g1["source"] == SOURCE and g1["license"] == "other"
    assert g2["source"] == SOURCE_CC_BY and g2["license"] == "cc-by-4.0"
    # The concrete failure mode teach-8xw.55 warns against: one graph's
    # manifest quietly reflecting another's provenance.
    assert g1["source"] != g2["source"]
    assert g1["license"] != g2["license"]


def test_root_index_lists_every_graph_with_counts_and_source():
    files = build_multi_graph_dataset_files(_two_specs(), repo_id="org/repo")
    index = json.loads(files["index.json"])
    by_key = {g["key"]: g for g in index["graphs"]}
    assert set(by_key) == {"g1", "g2"}
    assert by_key["g1"]["node_count"] == 2 and by_key["g1"]["edge_count"] == 1
    assert by_key["g2"]["node_count"] == 1 and by_key["g2"]["edge_count"] == 0
    assert by_key["g1"]["source"] == SOURCE
    assert by_key["g2"]["source"] == SOURCE_CC_BY


def test_root_card_declares_no_blanket_license_and_names_each_directory():
    files = build_multi_graph_dataset_files(_two_specs(), repo_id="org/repo")
    readme = files["README.md"].decode()
    front_matter = readme.split("---", 2)[1]
    assert "license:" not in front_matter, (
        "root card must not declare one license covering a repo whose graphs "
        "have different licenses"
    )
    assert "Licenses vary by directory" in readme
    assert "g1/" in readme and "g2/" in readme


def test_build_multi_graph_dataset_files_rejects_duplicate_keys():
    a, b = _two_specs()
    with pytest.raises(ValueError):
        build_multi_graph_dataset_files((a, dataclasses.replace(b, key=a.key)))


def test_build_multi_graph_dataset_files_rejects_empty_selection():
    with pytest.raises(ValueError):
        build_multi_graph_dataset_files(())


def test_build_multi_graph_dataset_files_is_deterministic():
    specs = _two_specs()
    assert build_multi_graph_dataset_files(specs, repo_id="org/repo") == (
        build_multi_graph_dataset_files(specs, repo_id="org/repo")
    )


def test_publish_many_defaults_to_dry_run_with_no_token(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    result = publish_many(_two_specs(), "org/repo")
    assert result.dry_run is True
    assert result.repo_url is None
    expected = build_multi_graph_dataset_files(_two_specs(), repo_id="org/repo")
    assert set(result.files) == set(expected)
    assert result.total_bytes == sum(len(c) for c in expected.values())


def test_publish_many_live_pushes_everything_in_one_commit_and_deletes_legacy_root_files(
    monkeypatch,
):
    """teach-8xw.55: the pre-multi-graph repo has nodes.jsonl/associations.jsonl/
    manifest.json at the ROOT. Moving to per-graph directories must not leave
    those orphaned -- a live publish has to delete them, in the SAME commit
    that adds the new layout, not a separate one (teach-8xw.24's atomicity
    guarantee extended to the migration itself)."""
    import huggingface_hub

    create_commit_calls = []

    class _FakeRepoUrl:
        repo_id = "canonical-org/repo"

        def __str__(self):
            return "https://huggingface.co/datasets/canonical-org/repo"

    class _FakeHfApi:
        def __init__(self, token=None):
            self.token = token

        def create_repo(self, repo_id, *, repo_type, private, exist_ok):
            return _FakeRepoUrl()

        def list_repo_files(self, repo_id, *, repo_type):
            return list(LEGACY_ROOT_FILES) + ["some-other-file.txt"]

        def create_commit(self, *, repo_id, repo_type, operations, commit_message):
            create_commit_calls.append(
                {"repo_id": repo_id, "repo_type": repo_type, "operations": list(operations)}
            )

    monkeypatch.setattr(huggingface_hub, "HfApi", _FakeHfApi)

    result = publish_many(_two_specs(), "org/repo", token="fake-token", dry_run=False)

    assert len(create_commit_calls) == 1, "everything must land in exactly one commit"
    call = create_commit_calls[0]
    add_paths = {
        op.path_in_repo for op in call["operations"]
        if type(op).__name__ == "CommitOperationAdd"
    }
    delete_paths = {
        op.path_in_repo for op in call["operations"]
        if type(op).__name__ == "CommitOperationDelete"
    }
    assert delete_paths == set(LEGACY_ROOT_FILES), (
        "every legacy root file must be deleted in the migration commit"
    )
    assert "some-other-file.txt" not in delete_paths, (
        "must only delete the specific legacy paths it knows about, not "
        "everything unfamiliar in the repo"
    )
    assert add_paths == {
        "g1/nodes.jsonl", "g1/associations.jsonl", "g1/manifest.json",
        "g2/nodes.jsonl", "g2/associations.jsonl", "g2/manifest.json",
        "index.json", "README.md",
    }
    assert result.repo_id == "canonical-org/repo"
    assert result.dry_run is False


def test_publish_many_live_omits_deletes_when_no_legacy_files_present(monkeypatch):
    """A fresh repo (or one already migrated) has none of the legacy root
    files -- the commit must not try to delete paths that were never there."""
    import huggingface_hub

    create_commit_calls = []

    class _FakeRepoUrl:
        repo_id = "canonical-org/repo"

        def __str__(self):
            return "https://huggingface.co/datasets/canonical-org/repo"

    class _FakeHfApi:
        def __init__(self, token=None):
            pass

        def create_repo(self, repo_id, *, repo_type, private, exist_ok):
            return _FakeRepoUrl()

        def list_repo_files(self, repo_id, *, repo_type):
            return []

        def create_commit(self, *, repo_id, repo_type, operations, commit_message):
            create_commit_calls.append({"operations": list(operations)})

    monkeypatch.setattr(huggingface_hub, "HfApi", _FakeHfApi)

    publish_many(_two_specs(), "org/repo", token="fake-token", dry_run=False)

    delete_ops = [
        op for op in create_commit_calls[0]["operations"]
        if type(op).__name__ == "CommitOperationDelete"
    ]
    assert delete_ops == []


def test_real_graph_registry_builds_offline_with_independent_licenses():
    """Not a fixture -- the actual registry this repo ships, exercised the
    way the CLI's default (`--graph` omitted, publish everything) would.
    Offline: these are local teach/data/*.json reads, no network."""
    from teach.publish_graph import _graph_registry

    registry = _graph_registry()
    assert len(registry) >= 10, sorted(registry)

    files = build_multi_graph_dataset_files(list(registry.values()), repo_id="lego573402/teach-concept-graphs")
    index = json.loads(files["index.json"])
    by_key = {g["key"]: g for g in index["graphs"]}

    assert by_key["va-math-sol-k8"]["node_count"] == 45
    assert by_key["va-math-sol-k8"]["edge_count"] == 40
    assert by_key["va-math-sol-k8"]["license"] == "cc-by-4.0"

    # GFDL's copyleft requirement: the notice and copyright must actually be
    # in the published bytes, not just an identifier.
    assert by_key["judson-algebra"]["license"] == "gfdl"
    judson_manifest = json.loads(files["judson-algebra/manifest.json"])
    assert "Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer" in (
        judson_manifest["source"]["attribution"]
    )
    readme = files["README.md"].decode()
    assert "Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer" in readme

    # No two graphs collide on directory path, and none of the pre-existing
    # "unrecorded" Learning-Commons-derived graphs' source blocks leak into
    # each other (spot check: k8 and hs really do carry different data).
    assert by_key["va-math-sol-k8"]["source"] != by_key["va-math-sol-hs"]["source"]


def test_learning_commons_graphs_report_unrecorded_upstream_state():
    """teach-8xw.54: the four graphs built from Learning Commons extracts
    that predate teach/upstream_provenance.py's record must say so honestly
    -- "unrecorded", not a fresh hash presented as if it dated back to the
    extract, and not silently absent either (an absent key reads as "this
    question doesn't apply", which would be false here)."""
    from teach.publish_graph import _graph_registry
    from teach.upstream_provenance import UNRECORDED_EXTRACTS

    assert {
        "va_math_sol_k8.json", "va_math_sol_hs.json",
        "va_reading_sol_k8.json", "va_writing_sol_k12.json",
    } == set(UNRECORDED_EXTRACTS), (
        "this test's graph keys below assume this exact set of pre-record "
        "extracts -- update both together if upstream_provenance.py changes"
    )

    registry = _graph_registry()
    files = build_multi_graph_dataset_files(list(registry.values()), repo_id="org/repo")
    for key in (
        "va-math-sol-k8", "va-math-sol-hs", "va-reading-sol-k8", "va-writing-sol-k12",
    ):
        manifest = json.loads(files[f"{key}/manifest.json"])
        assert manifest["source"]["upstream_state"] == "unrecorded", (
            key, manifest["source"]
        )
    # The dataset card embeds the source block verbatim -- a consumer reading
    # only README.md (not manifest.json) must see the same honesty.
    readme = files["README.md"].decode()
    assert '"upstream_state": "unrecorded"' in readme


def test_non_learning_commons_graphs_carry_no_upstream_state_key():
    """Judson, ACTFL and the world-language graphs have their own source
    documents, unrelated to the Learning Commons CDN export. They must not
    pick up an `upstream_state` key at all -- that would assert a provenance
    question was asked and came back unknown, when really the question never
    applied to this graph in the first place."""
    from teach.publish_graph import _graph_registry

    registry = _graph_registry()
    files = build_multi_graph_dataset_files(list(registry.values()), repo_id="org/repo")
    for key in (
        "judson-algebra", "va-world-language-sol",
        "actfl-can-do-interpersonal", "actfl-can-do-interpretive",
        "actfl-can-do-presentational", "actfl-can-do-intercultural",
    ):
        manifest = json.loads(files[f"{key}/manifest.json"])
        assert "upstream_state" not in manifest["source"], (key, manifest["source"])


def test_with_upstream_state_surfaces_the_full_record_for_a_recorded_extract():
    """`_with_upstream_state` is exercised above only against the four
    pre-record extracts, where every path returns the same literal string --
    that alone couldn't tell "always returns 'unrecorded'" apart from
    "correctly delegates to upstream_state_for". Call it directly with a
    filename NOT in UNRECORDED_EXTRACTS and check the other branch: the real
    provenance record, verbatim."""
    from teach.publish_graph import _with_upstream_state
    from teach.upstream_provenance import load_record

    wrapped = _with_upstream_state(lambda: dict(SOURCE), "some_future_extract.json")
    result = wrapped()
    assert result["upstream_state"] == load_record()
    # The wrapped source still carries everything the original callable
    # returned -- merging in upstream_state must not drop or overwrite other
    # keys.
    assert result["provider"] == SOURCE["provider"]
    assert result["license"] == SOURCE["license"]
    # And the original dict handed to _with_upstream_state is untouched --
    # mutating a shared SOURCE fixture in place would corrupt other tests.
    assert "upstream_state" not in SOURCE


def test_cli_list_works_without_repo_id(monkeypatch, capsys):
    """Regression: --repo-id was `required=True` in argparse, so --list --
    documented as "No network, no data I/O" -- failed with a usage error
    before _cli()'s own `if args.list` branch ever ran. --list must stand on
    its own."""
    import sys

    from teach.publish_graph import _cli

    monkeypatch.setattr(sys, "argv", ["publish_graph.py", "--list"])
    _cli()
    out = capsys.readouterr().out
    assert "va-math-sol-k8" in out
    assert "judson-algebra" in out


def test_cli_requires_repo_id_when_not_listing(monkeypatch):
    import sys

    from teach.publish_graph import _cli

    monkeypatch.setattr(sys, "argv", ["publish_graph.py"])
    with pytest.raises(SystemExit):
        _cli()
