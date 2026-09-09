"""Publishing stage: push a built `ConceptGraph` to HuggingFace as a dataset
(teach-8xw.14, epic PUBLISHING goal in `bd show teach-8xw`).

`pyproject.toml` already forwards `HF_TOKEN` into the sandbox
(`[tool.sandbox.forward-env]`), but until this module nothing in the repo
used it -- no `huggingface_hub` dependency, no publish code. This module is
that code. It is deliberately engine-level, not VA-math-specific: it takes
any `ConceptGraph` (see `concept_graph.py`'s domain-agnostic contract -- a
node's `facts` payload is opaque here too, forwarded unread) plus a
`source` metadata dict the caller supplies, and turns it into dataset files.

Export shape is modeled on 1EdTech CASE's `CFItem` / `CFAssociation`, per
teach-8xw.3's recommendation (confirmed live against opensalt.net's CASE API:
`precedes` is CASE's own token for "origin comes before destination in time
or order", which is exactly `concept_graph.py`'s edge direction). This is
*modeled on* CASE, not a conformance claim -- fields not backed by this
module's own data (e.g. CASE's full CFDocument wrapper, GUIDs minted by a
CASE authority) are not fabricated just to look more conformant.

Two paths, split so the dataset-file construction is testable without a
network or a token at all:

  build_dataset_files(graph, source=...)  -- pure, offline, deterministic.
      Returns {path: bytes} for every file that would land in the HF dataset
      repo: nodes.jsonl, associations.jsonl, manifest.json, README.md (the
      dataset card). No I/O, no huggingface_hub import touched.

  publish(graph, repo_id, source=..., token=..., dry_run=...) -- the network
      path. dry_run=True (the default whenever no token is available) never
      imports huggingface_hub's networking, never touches the network, and
      returns a PublishResult describing exactly what *would* have been
      created/uploaded -- so it's exercisable in CI or this sandbox with no
      live HF_TOKEN, per the bead's acceptance criteria. dry_run=False needs
      a real token (arg or $HF_TOKEN) and actually calls the HF Hub API;
      nothing in this repo's test suite exercises that path, because doing so
      would require live credentials this module cannot manufacture.
"""
from __future__ import annotations

import dataclasses
import json
import os

from teach.concept_graph import ConceptGraph

DATASET_SCHEMA_NAME = "teach-concept-graph-v1"


def _item_record(node) -> dict:
    return {
        "identifier": node.id,
        "fullStatement": node.label,
        "humanCodingScheme": node.standard_ref,
        "CFItemType": "Concept",
        "domain": node.domain,
        "facts": node.facts,
    }


def _association_record(edge) -> dict:
    return {
        # Deterministic, not random/minted -- same graph always produces the
        # same identifier, so a re-publish of unchanged data diffs as empty.
        "identifier": f"{edge.src}::{edge.type}::{edge.dst}",
        "associationType": edge.type,
        "originNodeURI": edge.src,
        "destinationNodeURI": edge.dst,
    }


# teach-8xw.17: HF validates the dataset card's front-matter `license` against
# a fixed vocabulary of identifiers and rejects the ENTIRE upload when it does
# not match -- and the VA SOL source states its license as the CC BY 4.0 URL,
# which is not one of them. Map only the spellings we can recognize exactly;
# anything else becomes "other", which the Hub accepts and which, unlike
# guessing at the nearest identifier, asserts nothing about a license this code
# did not recognize. The source's own license string is published verbatim in
# the "## Source" block below regardless, so nothing is lost by being vague in
# the front matter.
_HF_LICENSE_IDS = {
    "https://creativecommons.org/licenses/by/4.0/": "cc-by-4.0",
    "https://creativecommons.org/licenses/by-sa/4.0/": "cc-by-sa-4.0",
    "https://creativecommons.org/licenses/by-nc/4.0/": "cc-by-nc-4.0",
    "https://creativecommons.org/publicdomain/zero/1.0/": "cc0-1.0",
}


def _hf_license_id(raw: object) -> str:
    """The front-matter `license` value for a source's stated license.

    Unrecognized input is "other", never a guess: publishing a specific
    identifier the source did not actually state would be this repo asserting
    a license on someone else's material on the strength of a string match.
    """
    if raw is None:
        return "unknown"
    key = str(raw).strip().lower()
    if not key.endswith("/") and key.startswith("http"):
        key += "/"
    return _HF_LICENSE_IDS.get(key, "other")


def _dataset_card(*, graph: ConceptGraph, source: dict, repo_id: str | None) -> str:
    domains = sorted({n.domain for n in graph.nodes})
    lines = [
        "---",
        "license: " + _hf_license_id(source.get("license")),
        "tags:",
        "  - knowledge-graph",
        "  - prerequisite-graph",
        "  - education",
        "---",
        "",
        f"# {repo_id or '<unpublished>'}",
        "",
        "Prerequisite knowledge graph exported from the `teach` engine's "
        f"`ConceptGraph` (schema `{DATASET_SCHEMA_NAME}`). Item/association "
        "shape is modeled on 1EdTech CASE's `CFItem`/`CFAssociation` "
        "(`precedes` = origin established before destination); this is a "
        "shape reference, not a CASE-conformance claim.",
        "",
        f"- Nodes: {len(graph.nodes)}",
        f"- Edges: {len(graph.edges)}",
        f"- Domains: {', '.join(domains) if domains else '(none)'}",
        "",
        "## Source",
        "",
        "```json",
        json.dumps(source, indent=2, sort_keys=True),
        "```",
        "",
        "## Files",
        "",
        "- `nodes.jsonl` -- one `CFItem`-shaped record per `ConceptNode`",
        "- `associations.jsonl` -- one `CFAssociation`-shaped record per "
        "`PrerequisiteEdge`",
        "- `manifest.json` -- schema name, counts, and the `source` block "
        "above as structured data",
        "",
    ]
    return "\n".join(lines)


def build_dataset_files(
    graph: ConceptGraph, *, source: dict, repo_id: str | None = None
) -> dict[str, bytes]:
    """Pure, offline, deterministic: the exact set of files `publish()`
    would upload, as {path_in_repo: bytes}. No network, no huggingface_hub
    call -- this is the function the dry-run path and the tests build on.

    Raises `GraphError` (via `graph.validate()`) rather than exporting a
    structurally broken graph -- the same "prefer abstention" rule
    `concept_graph.py` applies to traversal.
    """
    graph.validate()

    nodes_jsonl = "\n".join(
        json.dumps(_item_record(n), sort_keys=True) for n in graph.nodes
    )
    if graph.nodes:
        nodes_jsonl += "\n"

    associations_jsonl = "\n".join(
        json.dumps(_association_record(e), sort_keys=True) for e in graph.edges
    )
    if graph.edges:
        associations_jsonl += "\n"

    manifest = {
        "schema": DATASET_SCHEMA_NAME,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "domains": sorted({n.domain for n in graph.nodes}),
        "source": source,
    }

    return {
        "nodes.jsonl": nodes_jsonl.encode("utf-8"),
        "associations.jsonl": associations_jsonl.encode("utf-8"),
        "manifest.json": (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        ),
        "README.md": _dataset_card(graph=graph, source=source, repo_id=repo_id).encode(
            "utf-8"
        ),
    }


@dataclasses.dataclass(frozen=True)
class PublishResult:
    """What happened (or, in dry-run, what *would* happen). `dry_run=True`
    means `files` was computed but nothing crossed the network -- a caller
    (or test) can tell the two modes apart without guessing from side
    effects."""

    repo_id: str
    dry_run: bool
    files: tuple[str, ...]
    total_bytes: int
    repo_url: str | None = None


def publish(
    graph: ConceptGraph,
    repo_id: str,
    *,
    source: dict,
    token: str | None = None,
    dry_run: bool | None = None,
    private: bool = False,
) -> PublishResult:
    """Build the dataset files for `graph` and push them to the HuggingFace
    dataset repo `repo_id`.

    `token` defaults to `$HF_TOKEN` (the env var `pyproject.toml` already
    forwards into this sandbox). `dry_run` defaults to True whenever no
    token is available (arg or env) -- so calling this with no arguments
    beyond a graph and repo_id never accidentally hits the network. Pass
    `dry_run=False` explicitly to force a live push (raises if no token is
    available either way).
    """
    token = token or os.environ.get("HF_TOKEN") or None

    if dry_run is None:
        dry_run = token is None

    files = build_dataset_files(graph, source=source, repo_id=repo_id)
    total_bytes = sum(len(content) for content in files.values())

    if dry_run:
        return PublishResult(
            repo_id=repo_id,
            dry_run=True,
            files=tuple(sorted(files)),
            total_bytes=total_bytes,
            repo_url=None,
        )

    if not token:
        raise ValueError(
            "publish(dry_run=False) requires a token: pass token=... or set $HF_TOKEN"
        )

    # Imported here, not at module scope: a dry-run caller (the only path
    # exercised by this repo's test suite, per this module's docstring)
    # should not need huggingface_hub's networking machinery to import
    # cleanly, and a missing/broken install of it should only break the
    # live-push path, not offline file-building.
    from huggingface_hub import HfApi

    api = HfApi(token=token)
    repo_url = api.create_repo(
        repo_id, repo_type="dataset", private=private, exist_ok=True
    )
    # teach-8xw.17: `create_repo` resolves a namespace-less repo id against the
    # token owner and returns the canonical "owner/name"; `upload_file` does
    # NOT -- it looks up the literal string and 404s. Passing the caller's
    # `repo_id` to both therefore creates one repo and uploads to a different,
    # nonexistent one, and the failure reads as "Repository Not Found" for a
    # repo that was just successfully created one line above. Take the
    # canonical id back from `create_repo` and use it from here on.
    repo_id = repo_url.repo_id
    # Rebuilt, not reused: `files` above was built from the caller's spelling,
    # and the dataset card embeds it as the README title -- publishing the
    # pre-canonical build would ship a card headed "mathgraph-00" to a repo
    # actually named "owner/mathgraph-00".
    files = build_dataset_files(graph, source=source, repo_id=repo_id)
    total_bytes = sum(len(content) for content in files.values())
    for path_in_repo, content in files.items():
        api.upload_file(
            path_or_fileobj=content,
            path_in_repo=path_in_repo,
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"teach: publish {DATASET_SCHEMA_NAME} ({len(graph.nodes)} nodes, {len(graph.edges)} edges)",
        )

    return PublishResult(
        repo_id=repo_id,
        dry_run=False,
        files=tuple(sorted(files)),
        total_bytes=total_bytes,
        repo_url=str(repo_url),
    )


def _cli() -> None:
    import argparse

    from teach.va_math_sol_graph import load_va_math_sol_data, load_va_math_sol_graph

    parser = argparse.ArgumentParser(
        description="Publish a teach ConceptGraph to a HuggingFace dataset repo."
    )
    parser.add_argument(
        "--repo-id",
        required=True,
        help="HuggingFace dataset repo id, e.g. 'someorg/va-math-sol-k8'",
    )
    parser.add_argument("--private", action="store_true")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually push (default is dry-run; requires $HF_TOKEN or --token)",
    )
    parser.add_argument("--token", default=None)
    args = parser.parse_args()

    data = load_va_math_sol_data()
    graph = load_va_math_sol_graph()
    result = publish(
        graph,
        args.repo_id,
        source=data["source"],
        token=args.token,
        dry_run=not args.live,
        private=args.private,
    )
    if result.dry_run:
        print(
            f"DRY RUN: would publish {len(graph.nodes)} nodes / {len(graph.edges)} "
            f"edges to '{result.repo_id}' as {len(result.files)} files "
            f"({result.total_bytes} bytes): {', '.join(result.files)}"
        )
    else:
        print(f"Published to {result.repo_url}: {', '.join(result.files)}")


def _selfcheck() -> None:
    from teach.concept_graph import ConceptNode, PrerequisiteEdge

    # Self-check: build_dataset_files is fully offline and deterministic --
    # no $HF_TOKEN needed to verify this module's own logic. Uses a small
    # synthetic graph so this check doesn't depend on va_math_sol_graph.py's
    # data shape (this module must stay domain-agnostic, per
    # concept_graph.py's boundary).
    a = ConceptNode(id="dom:a", domain="test", label="A")
    b = ConceptNode(id="dom:b", domain="test", label="B")
    graph = ConceptGraph(nodes=(a, b), edges=(PrerequisiteEdge(src="dom:a", dst="dom:b"),))
    source = {"provider": "self-check", "license": "n/a"}

    assert _hf_license_id("https://creativecommons.org/licenses/by/4.0/") == "cc-by-4.0"
    assert _hf_license_id("https://creativecommons.org/licenses/by/4.0") == "cc-by-4.0"
    assert _hf_license_id("Some Bespoke Institutional License") == "other", (
        "an unrecognized license must degrade to 'other', never to a guessed identifier"
    )
    assert _hf_license_id(None) == "unknown"

    files = build_dataset_files(graph, source=source, repo_id="example/repo")
    assert set(files) == {"nodes.jsonl", "associations.jsonl", "manifest.json", "README.md"}
    assert len(files["nodes.jsonl"].decode().strip().splitlines()) == 2
    assert len(files["associations.jsonl"].decode().strip().splitlines()) == 1
    manifest = json.loads(files["manifest.json"])
    assert manifest["node_count"] == 2 and manifest["edge_count"] == 1

    # publish() with no token must default to dry-run and must not raise
    # even though $HF_TOKEN is (almost certainly) unset in this sandbox --
    # that's the acceptance criterion this bead is built around.
    saved = os.environ.pop("HF_TOKEN", None)
    try:
        result = publish(graph, "example/dry-run-repo", source=source)
    finally:
        if saved is not None:
            os.environ["HF_TOKEN"] = saved
    assert result.dry_run is True
    assert result.repo_url is None
    assert set(result.files) == set(files)
    expected_files = build_dataset_files(graph, source=source, repo_id="example/dry-run-repo")
    assert result.total_bytes == sum(len(c) for c in expected_files.values())

    print(
        "OK: build_dataset_files is offline/deterministic and publish() "
        "defaults to a no-network dry run when no HF_TOKEN is available"
    )


if __name__ == "__main__":
    import sys

    # No args: `python3 -m teach.publish_graph` runs the offline self-check,
    # matching this repo's convention (see module docstrings elsewhere).
    # With args, it's the real CLI (`--repo-id ...`) -- so the one entry
    # point serves both without one shadowing the other.
    if len(sys.argv) > 1:
        _cli()
    else:
        _selfcheck()
