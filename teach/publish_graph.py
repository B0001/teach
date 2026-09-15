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

ONE SHARED DATASET REPO FOR ALL GRAPHS (teach-8xw.55)

The repo owner decided all graphs share one HuggingFace dataset repo
(`lego573402/teach-concept-graphs`) rather than one repo per graph. A single
graph is still `build_dataset_files`/`publish` below, writing at the repo
ROOT -- that pair is unchanged and is what the pre-multi-graph repo actually
has live today. Multiple graphs sharing one repo are
`build_multi_graph_dataset_files`/`publish_many`: each graph gets its own
`{key}/nodes.jsonl`, `{key}/associations.jsonl`, `{key}/manifest.json`
(own counts, own license, own `source` block -- nothing blended across
graphs, per teach-8xw.55's provenance requirement), and the repo root gets
`README.md` (a card listing every graph, explicit that licenses vary by
directory -- never a single blanket license) plus `index.json` (the same
listing, machine-readable). `_graph_registry()` is the map from CLI-facing
graph key to loader + source; `_cli()`'s `--graph` selects a subset of it
(default: all), replacing the old hardcoded-to-VA-math-K-8 CLI.

Two paths per shape, split so dataset-file construction is testable without
a network or a token at all:

  build_dataset_files(graph, source=...) / build_multi_graph_dataset_files(specs)
      -- pure, offline, deterministic. Returns {path: bytes} for every file
      that would land in the HF dataset repo. No I/O, no huggingface_hub
      import touched (multi-graph loaders do read this repo's own local
      `teach/data/*.json` files -- that's local disk, not network).

  publish(graph, repo_id, source=..., ...) / publish_many(specs, repo_id, ...)
      -- the network path. dry_run=True (the default whenever no token is
      available) never imports huggingface_hub's networking, never touches
      the network, and returns a PublishResult describing exactly what
      *would* have been created/uploaded -- so it's exercisable in CI or
      this sandbox with no live HF_TOKEN, per the bead's acceptance
      criteria. dry_run=False needs a real token (arg or $HF_TOKEN) and
      actually calls the HF Hub API; nothing in this repo's test suite
      exercises that path with live credentials, because doing so would
      require this module to manufacture them.

UPSTREAM PROVENANCE (teach-8xw.54)

`source["retrieved_via"]` alone names a CDN path whose only version anchor is
a mutable string ("v1.13.0") -- nothing stops the same version being
republished with different bytes, so a published graph couldn't say which
upstream bytes it actually came from. `teach/upstream_provenance.py` now
keeps a record (retrieval timestamp, sha256, content-length, upstream
ETag/last-modified) of the Learning Commons export a *future* extract is
built from; `_with_upstream_state` below merges that record's key,
`upstream_state`, into the `source` block for the four graphs actually
derived from it (`va-math-sol-k8`/`-hs`, `va-reading-sol-k8`,
`va-writing-sol-k12`). For those four, `upstream_state` reads the literal
string `"unrecorded"` right now -- the extracts committed in `teach/data/`
predate the provenance record, and the downloads they were built from are
gone, so hashing a fresh download and calling it their provenance would be a
fabricated audit trail. Graphs with unrelated source documents (Judson,
ACTFL, world-language) get no `upstream_state` key at all -- the question
doesn't apply to them, which is a different, and differently-spelled,
statement than "applies and is unknown".
"""
from __future__ import annotations

import dataclasses
import json
import os
from typing import Callable, Sequence

from teach.concept_graph import ConceptGraph

DATASET_SCHEMA_NAME = "teach-concept-graph-v1"

# The pre-multi-graph layout published these three files at the repo ROOT
# (see `publish()` below). `publish_many` moves them under a per-graph
# directory and must delete the orphans from a repo that still has them --
# see the "existing published files are at the root" constraint in
# teach-8xw.55.
LEGACY_ROOT_FILES = ("nodes.jsonl", "associations.jsonl", "manifest.json")


def _with_upstream_state(
    source_fn: Callable[[], dict], extract_filename: str
) -> Callable[[], dict]:
    """Wrap a `GraphSpec.source` callable so the published source block also
    carries `upstream_state` (teach-8xw.54): the record
    `teach/upstream_provenance.py` keeps for the Learning Commons export
    `extract_filename` was built from -- or the literal string `"unrecorded"`
    for the extracts that predate that record (`va_math_sol_k8.json` and its
    hs/reading/writing siblings; see `upstream_provenance.UNRECORDED_EXTRACTS`).

    Only for graphs actually derived from a Learning Commons CDN export --
    `_graph_registry()` below applies this to exactly those four. Judson,
    ACTFL and the world-language graph have their own, unrelated source
    documents and get no `upstream_state` key at all: an absent key here
    means "this provenance question doesn't apply to this graph", which is
    different from -- and must not be confused with -- `"unrecorded"`
    meaning "it applies, and the answer is unknown" (the bead's own
    constraint: a manifest must not silently omit a field that IS relevant,
    but must also not invent one that isn't).

    Offline: `upstream_state_for` only reads the local
    `teach/data/upstream_provenance.json` record, no network.
    """

    def wrapped() -> dict:
        from teach.upstream_provenance import upstream_state_for

        source = dict(source_fn())
        source["upstream_state"] = upstream_state_for(extract_filename)
        return source

    return wrapped


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
# Keys are stored WITHOUT a trailing slash and matched that way (see
# `_hf_license_id`). The earlier version appended one to any http URL, which
# happened to suit canonical Creative Commons URLs and silently broke every
# license whose URL ends in a filename -- GFDL's does (fdl-1.3.html), so
# Judson's book would have degraded to "other" despite having an exact HF
# identifier (teach-8xw.57).
_HF_LICENSE_IDS = {
    "https://creativecommons.org/licenses/by/4.0": "cc-by-4.0",
    "https://creativecommons.org/licenses/by-sa/4.0": "cc-by-sa-4.0",
    "https://creativecommons.org/licenses/by-nc/4.0": "cc-by-nc-4.0",
    "https://creativecommons.org/publicdomain/zero/1.0": "cc0-1.0",
    # GNU FDL, the license of Judson's Abstract Algebra: Theory and
    # Applications. HF's accepted vocabulary has no version-specific GFDL
    # identifier -- just "gfdl" -- so 1.3 and the unversioned copyleft URL
    # both map to it, and the *version* stays where it is stated exactly: in
    # the source block's own license text, which ships verbatim in the card.
    "https://www.gnu.org/licenses/fdl-1.3.html": "gfdl",
    "https://www.gnu.org/licenses/fdl.html": "gfdl",
    "http://www.gnu.org/copyleft/fdl.html": "gfdl",
    "gnu fdl 1.3": "gfdl",
    "gfdl-1.3": "gfdl",
    "gfdl": "gfdl",
}


def _hf_license_id(raw: object) -> str:
    """The front-matter `license` value for a source's stated license.

    Unrecognized input is "other", never a guess: publishing a specific
    identifier the source did not actually state would be this repo asserting
    a license on someone else's material on the strength of a string match.
    """
    if raw is None:
        return "unknown"
    key = str(raw).strip().lower().rstrip("/")
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


def _manifest(graph: ConceptGraph, source: dict) -> dict:
    return {
        "schema": DATASET_SCHEMA_NAME,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "domains": sorted({n.domain for n in graph.nodes}),
        # Resolved here (not just left inside `source`) so a consumer who
        # only fetches one graph's directory -- not the root card -- can
        # still tell its HF-recognized license without reimplementing
        # `_hf_license_id`'s mapping themselves.
        "license": _hf_license_id(source.get("license")),
        "source": source,
    }


def _graph_core_files(
    graph: ConceptGraph, *, source: dict, path_prefix: str = ""
) -> dict[str, bytes]:
    """{path_prefix}nodes.jsonl / associations.jsonl / manifest.json for one
    graph -- everything `build_dataset_files` writes except the dataset
    card. Shared by the single-graph and multi-graph builders so the record
    shapes (and the license-in-manifest rule above) can't drift between the
    two.

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

    manifest = _manifest(graph, source)

    return {
        f"{path_prefix}nodes.jsonl": nodes_jsonl.encode("utf-8"),
        f"{path_prefix}associations.jsonl": associations_jsonl.encode("utf-8"),
        f"{path_prefix}manifest.json": (
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8"),
    }


def _root_index_card(*, repo_id: str | None, index_entries: list[dict]) -> str:
    lines = [
        "---",
        "tags:",
        "  - knowledge-graph",
        "  - prerequisite-graph",
        "  - education",
        "---",
        "",
        f"# {repo_id or '<unpublished>'}",
        "",
        "Prerequisite knowledge graphs exported from the `teach` engine's "
        f"`ConceptGraph`s (schema `{DATASET_SCHEMA_NAME}`). This repo holds "
        f"{len(index_entries)} independent graph(s), one per directory "
        "below. Item/association shape is modeled on 1EdTech CASE's "
        "`CFItem`/`CFAssociation` (`precedes` = origin established before "
        "destination); this is a shape reference, not a CASE-conformance "
        "claim.",
        "",
        "**Licenses vary by directory.** This card's front matter "
        "deliberately carries no repo-wide `license` field -- do not assume "
        "one license covers everything published here. Each graph below "
        "states its own.",
        "",
        "## Graphs",
        "",
    ]
    for entry in index_entries:
        lines += [
            f"### `{entry['path']}` -- {entry['description']}",
            "",
            f"- License: {entry['license']}",
            f"- Nodes: {entry['node_count']}",
            f"- Edges: {entry['edge_count']}",
            f"- Domains: {', '.join(entry['domains']) if entry['domains'] else '(none)'}",
            "",
            "```json",
            json.dumps(entry["source"], indent=2, sort_keys=True),
            "```",
            "",
        ]
    lines += [
        "## Files",
        "",
        "Each graph directory above contains `nodes.jsonl` (one "
        "`CFItem`-shaped record per `ConceptNode`), `associations.jsonl` "
        "(one `CFAssociation`-shaped record per `PrerequisiteEdge`), and its "
        "own `manifest.json` (schema, counts, license, and that graph's "
        "`source` block -- nothing here is inherited from another graph). "
        "`index.json` at the repo root is the machine-readable form of the "
        "listing above.",
        "",
    ]
    return "\n".join(lines)


def build_dataset_files(
    graph: ConceptGraph, *, source: dict, repo_id: str | None = None
) -> dict[str, bytes]:
    """Pure, offline, deterministic: the exact set of files `publish()`
    would upload at the repo ROOT, as {path_in_repo: bytes}. No network, no
    huggingface_hub call -- this is the function the dry-run path and the
    tests build on. For a repo that shares many graphs, see
    `build_multi_graph_dataset_files` instead.
    """
    files = dict(_graph_core_files(graph, source=source))
    files["README.md"] = _dataset_card(graph=graph, source=source, repo_id=repo_id).encode(
        "utf-8"
    )
    return files


@dataclasses.dataclass(frozen=True)
class GraphSpec:
    """One entry in the shared repo: `key` is both the CLI selector and the
    directory the graph is published under. `loader`/`source` are zero-arg
    callables (not values) so `_graph_registry()` can list every known graph
    without eagerly importing and I/O-loading all of them -- only the ones a
    given publish actually selects get loaded.

    `blocked_reason` (teach-8xw.58): set when this graph's own stated terms
    are a real usage restriction with no resolvable HF license id -- not
    merely an unverified license, a *confirmed* one this repo cannot honor
    by guessing. Building and dry-running a blocked graph is still allowed
    (that is how a reviewer inspects what *would* ship); `publish_many` with
    `dry_run=False` refuses outright. This is a worker-level engineering
    guard, not the licensing decision itself -- clearing it requires a
    recorded repo-owner decision (see teach-8xw.58's notes), at which point
    a future session removes this field for that key, the same way
    teach-8xw.57's GFDL decision was landed by editing code only after the
    decision existed, never by a CLI override flag.
    """

    key: str
    loader: Callable[[], ConceptGraph]
    source: Callable[[], dict]
    description: str
    blocked_reason: str | None = None


def build_multi_graph_dataset_files(
    specs: Sequence[GraphSpec], *, repo_id: str | None = None
) -> dict[str, bytes]:
    """Pure, offline, deterministic: every file a `publish_many` call for
    `specs` would upload -- `{key}/nodes.jsonl`, `{key}/associations.jsonl`,
    `{key}/manifest.json` per graph, plus a root `README.md` and `index.json`
    listing all of them. Each graph's `source`/`license` is computed and
    carried independently; the root files only ever read what the per-graph
    manifests already computed, never re-derive or blend them (teach-8xw.55's
    provenance requirement: no graph inherits another's record).
    """
    if not specs:
        raise ValueError("build_multi_graph_dataset_files: no graphs selected")
    keys = [s.key for s in specs]
    if len(set(keys)) != len(keys):
        dupes = sorted({k for k in keys if keys.count(k) > 1})
        raise ValueError(f"duplicate graph keys: {dupes}")

    files: dict[str, bytes] = {}
    index_entries = []
    for spec in specs:
        graph = spec.loader()
        source = spec.source()
        graph_files = _graph_core_files(graph, source=source, path_prefix=f"{spec.key}/")
        files.update(graph_files)
        manifest = json.loads(graph_files[f"{spec.key}/manifest.json"])
        index_entries.append(
            {
                "key": spec.key,
                "path": f"{spec.key}/",
                "description": spec.description,
                "node_count": manifest["node_count"],
                "edge_count": manifest["edge_count"],
                "domains": manifest["domains"],
                "license": manifest["license"],
                "source": source,
            }
        )

    index = {"schema": "teach-concept-graph-index-v1", "graphs": index_entries}
    files["index.json"] = (json.dumps(index, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    files["README.md"] = _root_index_card(
        repo_id=repo_id, index_entries=index_entries
    ).encode("utf-8")
    return files


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
    from huggingface_hub import CommitOperationAdd, HfApi

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
    # One commit for all four files, not one commit per file: a mid-loop
    # failure (e.g. teach-8xw.17's dataset-card license rejection) must not
    # be able to leave the public repo holding data files with no README --
    # no provenance, no license, no attribution -- until a retry lands
    # (teach-8xw.24). `upload_file` above is itself a `create_commit`
    # wrapper around a single `CommitOperationAdd`; this is that same call
    # made explicitly, with all operations in one list.
    operations = [
        CommitOperationAdd(path_in_repo=path_in_repo, path_or_fileobj=content)
        for path_in_repo, content in files.items()
    ]
    api.create_commit(
        repo_id=repo_id,
        repo_type="dataset",
        operations=operations,
        commit_message=f"teach: publish {DATASET_SCHEMA_NAME} ({len(graph.nodes)} nodes, {len(graph.edges)} edges)",
    )

    return PublishResult(
        repo_id=repo_id,
        dry_run=False,
        files=tuple(sorted(files)),
        total_bytes=total_bytes,
        repo_url=str(repo_url),
    )


def publish_many(
    specs: Sequence[GraphSpec],
    repo_id: str,
    *,
    token: str | None = None,
    dry_run: bool | None = None,
    private: bool = False,
) -> PublishResult:
    """Like `publish()`, but for teach-8xw.55's shared multi-graph repo:
    builds every graph in `specs` under its own `{key}/` directory plus a
    root `README.md`/`index.json`, and pushes all of it in ONE commit -- the
    same atomicity guarantee `publish()` has for a single graph (teach-8xw.24),
    extended to many. A multi-graph publish staying one commit rather than
    one-per-graph is deliberate here, not an oversight: nothing downstream
    (the root index) is valid until every selected graph's files have landed,
    so a partial commit would leave the index claiming graphs whose data
    isn't actually there yet.
    """
    token = token or os.environ.get("HF_TOKEN") or None

    if dry_run is None:
        dry_run = token is None

    # teach-8xw.58: a dry run is how a reviewer inspects what *would* ship
    # (still permitted for a blocked graph, on purpose), but an actual push
    # must refuse outright -- "remember not to select this key" is exactly
    # the kind of manual discipline this repo's own standard says not to
    # rely on.
    if not dry_run:
        blocked = [s for s in specs if s.blocked_reason]
        if blocked:
            raise ValueError(
                "publish_many(dry_run=False) refused: the following graph(s) "
                "are blocked pending a repo-owner licensing decision and "
                "must not be pushed live -- " + "; ".join(
                    f"{s.key}: {s.blocked_reason}" for s in blocked
                )
            )

    files = build_multi_graph_dataset_files(specs, repo_id=repo_id)
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
            "publish_many(dry_run=False) requires a token: pass token=... or set $HF_TOKEN"
        )

    from huggingface_hub import CommitOperationAdd, CommitOperationDelete, HfApi

    api = HfApi(token=token)
    repo_url = api.create_repo(
        repo_id, repo_type="dataset", private=private, exist_ok=True
    )
    repo_id = repo_url.repo_id
    files = build_multi_graph_dataset_files(specs, repo_id=repo_id)
    total_bytes = sum(len(content) for content in files.values())

    operations = [
        CommitOperationAdd(path_in_repo=path_in_repo, path_or_fileobj=content)
        for path_in_repo, content in files.items()
    ]

    # teach-8xw.55: the pre-multi-graph layout published LEGACY_ROOT_FILES at
    # the repo root (see `publish()` above); the new layout moves that data
    # under a per-graph directory. An Add-only commit would leave those
    # orphans live alongside the new directories, silently doubling what a
    # naive root listing looks like. Checked against what the repo actually
    # has (not assumed) so a brand-new repo, or one already migrated, doesn't
    # get a delete-of-something-that-was-never-there error.
    try:
        existing = set(api.list_repo_files(repo_id, repo_type="dataset"))
    except Exception:
        existing = set()
    for legacy_path in LEGACY_ROOT_FILES:
        if legacy_path in existing and legacy_path not in files:
            operations.append(CommitOperationDelete(path_in_repo=legacy_path))

    api.create_commit(
        repo_id=repo_id,
        repo_type="dataset",
        operations=operations,
        commit_message=f"teach: publish {len(specs)} graph(s) under {DATASET_SCHEMA_NAME}",
    )

    return PublishResult(
        repo_id=repo_id,
        dry_run=False,
        files=tuple(sorted(files)),
        total_bytes=total_bytes,
        repo_url=str(repo_url),
    )


def _graph_registry() -> dict[str, GraphSpec]:
    """Every graph this repo knows how to publish, keyed by the directory it
    is published under in the shared repo. Imports are local to this
    function, not module scope: listing the registry (e.g. `--list`) must
    not require importing -- and I/O-loading the data behind -- every
    domain module whether or not it was selected.

    NOT included: `load_va_math_sol_full_graph` (K-8 union high-school) --
    it is a traversal convenience, not a separate provenance-bearing
    artifact, and its two halves have differently-shaped `source` dicts
    (see va-math-sol-hs below); publishing the union would blend them under
    one manifest, which is exactly what teach-8xw.55's provenance
    requirement rules out. A consumer who wants both fetches both
    directories.
    """
    from teach.actfl_can_do_graph import SOURCE as _ACTFL_SOURCE
    from teach.actfl_can_do_graph import (
        load_actfl_can_do_graph,
        load_actfl_intercultural_graph,
        load_actfl_interpretive_graph,
        load_actfl_presentational_graph,
    )
    from teach.judson_algebra_graph import JUDSON_SOURCE, load_judson_algebra_graph
    from teach.va_math_sol_graph import (
        load_va_math_sol_data,
        load_va_math_sol_graph,
        load_va_math_sol_hs_data,
        load_va_math_sol_hs_graph,
    )
    from teach.va_reading_sol_graph import load_va_reading_sol_data, load_va_reading_sol_graph
    from teach.va_world_language_sol_graph import SOURCE as _WORLD_LANG_SOURCE
    from teach.va_world_language_sol_graph import load_va_world_language_sol_graph
    from teach.va_writing_sol_graph import load_va_writing_sol_data, load_va_writing_sol_graph

    specs = (
        GraphSpec(
            key="va-math-sol-k8",
            loader=load_va_math_sol_graph,
            source=_with_upstream_state(
                lambda: load_va_math_sol_data()["source"], "va_math_sol_k8.json"
            ),
            description="Virginia Math SOL, grades K-8 (groupings chained by grade within strand)",
        ),
        GraphSpec(
            key="va-math-sol-hs",
            loader=load_va_math_sol_hs_graph,
            source=_with_upstream_state(
                lambda: load_va_math_sol_hs_data()["source"], "va_math_sol_hs.json"
            ),
            description="Virginia Math SOL, high-school course sequence",
        ),
        GraphSpec(
            key="va-reading-sol-k8",
            loader=load_va_reading_sol_graph,
            source=_with_upstream_state(
                lambda: load_va_reading_sol_data()["source"], "va_reading_sol_k8.json"
            ),
            description="Virginia Reading SOL, grades K-8",
        ),
        GraphSpec(
            key="va-writing-sol-k12",
            loader=load_va_writing_sol_graph,
            source=_with_upstream_state(
                lambda: load_va_writing_sol_data()["source"], "va_writing_sol_k12.json"
            ),
            description="Virginia Writing SOL, grades K-12",
        ),
        # teach-8xw.58: this source has no "license" key. UPDATE -- this was
        # originally registered on the theory that VDOE's terms were merely
        # *unverified*, plausibly CC BY 4.0 like the other VA SOL graphs by
        # publisher association. That guess was checked directly against
        # VDOE's own stated terms (the document itself, plus VDOE's
        # web-policies page) and turned out to be wrong: VDOE's terms are an
        # explicit all-rights-reserved, non-commercial-use, permission-
        # required notice (see `SOURCE["usage_terms"]` in
        # va_world_language_sol_graph.py) -- structurally the same kind of
        # confirmed restriction as ACTFL's below, not just an open question.
        # `blocked_reason` below makes that real now, the same as ACTFL.
        GraphSpec(
            key="va-world-language-sol",
            loader=load_va_world_language_sol_graph,
            source=lambda: _WORLD_LANG_SOURCE,
            description="Virginia World Language SOL, Novice-Advanced",
            blocked_reason=(
                "VDOE's own stated terms for this document (see "
                "SOURCE['usage_terms']) are a confirmed non-commercial-use, "
                "permission-required notice with no resolvable HF license "
                "id -- same shape of question as ACTFL's below. Needs a "
                "recorded repo-owner decision (teach-8xw.58) before a live "
                "publish, not a guessed license."
            ),
        ),
        # teach-8xw.58: ACTFL's SOURCE has no "license" key either -- its own
        # stated usage_terms restrict to "educational and non-profit use
        # only, commercial use or sale is prohibited", which does not map
        # onto any HF license identifier `_hf_license_id` knows (correctly
        # reports "unknown" rather than guessing "cc-by-nc" or similar).
        # Same shape of question GFDL vs CC-BY was for Judson (teach-8xw.57)
        # -- the repo owner's call, not a worker's. Registered here
        # (buildable, dry-run-able, tested) because excluding them from the
        # registry entirely would be this worker making that same call
        # unilaterally in the other direction; `blocked_reason` below is
        # what actually stops a LIVE publish, not just a comment asking
        # nicely.
        GraphSpec(
            key="actfl-can-do-interpersonal",
            loader=load_actfl_can_do_graph,
            source=lambda: _ACTFL_SOURCE,
            description="NCSSFL-ACTFL Can-Do Statements, Interpersonal Communication (11 sublevels)",
            blocked_reason=(
                "ACTFL's own stated usage_terms restrict to educational/"
                "non-profit use only, commercial use or sale prohibited -- "
                "no resolvable HF license id. Needs a recorded repo-owner "
                "decision (teach-8xw.58) before a live publish."
            ),
        ),
        GraphSpec(
            key="actfl-can-do-interpretive",
            loader=load_actfl_interpretive_graph,
            source=lambda: _ACTFL_SOURCE,
            description="NCSSFL-ACTFL Can-Do Statements, Interpretive Communication (11 sublevels)",
            blocked_reason=(
                "ACTFL's own stated usage_terms restrict to educational/"
                "non-profit use only, commercial use or sale prohibited -- "
                "no resolvable HF license id. Needs a recorded repo-owner "
                "decision (teach-8xw.58) before a live publish."
            ),
        ),
        GraphSpec(
            key="actfl-can-do-presentational",
            loader=load_actfl_presentational_graph,
            source=lambda: _ACTFL_SOURCE,
            description="NCSSFL-ACTFL Can-Do Statements, Presentational Communication (11 sublevels)",
            blocked_reason=(
                "ACTFL's own stated usage_terms restrict to educational/"
                "non-profit use only, commercial use or sale prohibited -- "
                "no resolvable HF license id. Needs a recorded repo-owner "
                "decision (teach-8xw.58) before a live publish."
            ),
        ),
        GraphSpec(
            key="actfl-can-do-intercultural",
            loader=load_actfl_intercultural_graph,
            source=lambda: _ACTFL_SOURCE,
            blocked_reason=(
                "ACTFL's own stated usage_terms restrict to educational/"
                "non-profit use only, commercial use or sale prohibited -- "
                "no resolvable HF license id. Needs a recorded repo-owner "
                "decision (teach-8xw.58) before a live publish."
            ),
            description="NCSSFL-ACTFL Can-Do Statements, Intercultural Communication (5 major levels)",
        ),
        GraphSpec(
            key="judson-algebra",
            loader=load_judson_algebra_graph,
            source=lambda: JUDSON_SOURCE,
            description="Judson, Abstract Algebra: Theory and Applications -- "
            "group theory prerequisite chain to Lagrange's theorem (GFDL 1.3+)",
        ),
    )
    return {spec.key: spec for spec in specs}


def _cli() -> None:
    import argparse

    registry = _graph_registry()

    parser = argparse.ArgumentParser(
        description="Publish teach ConceptGraph(s) to the shared HuggingFace "
        "dataset repo (teach-8xw.55)."
    )
    parser.add_argument(
        "--repo-id",
        help="HuggingFace dataset repo id, e.g. 'lego573402/teach-concept-graphs'. "
        "Required unless --list.",
    )
    parser.add_argument(
        "--graph",
        action="append",
        choices=sorted(registry),
        metavar="KEY",
        help="Graph key to publish (repeatable). Default: every registered "
        "graph. See --list for the available keys.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List registered graph keys and exit. No network, no data I/O.",
    )
    parser.add_argument("--private", action="store_true")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually push (default is dry-run; requires $HF_TOKEN or --token)",
    )
    parser.add_argument("--token", default=None)
    args = parser.parse_args()

    if args.list:
        for key in sorted(registry):
            print(f"{key}: {registry[key].description}")
        return

    if not args.repo_id:
        parser.error("--repo-id is required unless --list is given")

    keys = args.graph or sorted(registry)
    specs = [registry[key] for key in keys]

    result = publish_many(
        specs,
        args.repo_id,
        token=args.token,
        dry_run=not args.live,
        private=args.private,
    )
    if result.dry_run:
        print(
            f"DRY RUN: would publish {len(specs)} graph(s) ({', '.join(keys)}) "
            f"to '{result.repo_id}' as {len(result.files)} files "
            f"({result.total_bytes} bytes): {', '.join(result.files)}"
        )
    else:
        print(
            f"Published {len(specs)} graph(s) to {result.repo_url}: "
            f"{', '.join(result.files)}"
        )


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
    # teach-8xw.57: GFDL's URL ends in a filename, which the old trailing-slash
    # normalization mangled. Both spellings and the bare identifier must land
    # on HF's exact id rather than degrading to "other".
    assert _hf_license_id("https://www.gnu.org/licenses/fdl-1.3.html") == "gfdl"
    assert _hf_license_id("http://www.gnu.org/copyleft/fdl.html") == "gfdl"
    assert _hf_license_id("GNU FDL 1.3") == "gfdl"
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

    # manifest.json now also resolves the HF license id itself (teach-8xw.55:
    # a consumer of just one graph's directory shouldn't have to reimplement
    # _hf_license_id against the raw source.license string).
    assert manifest["license"] == "other", manifest  # source["license"] == "n/a", unrecognized

    print(
        "OK: build_dataset_files is offline/deterministic and publish() "
        "defaults to a no-network dry run when no HF_TOKEN is available"
    )

    # teach-8xw.55: the multi-graph builder, on the same domain-agnostic
    # synthetic fixtures -- two graphs, two different licenses, so a blend
    # would be caught immediately.
    c = ConceptNode(id="dom2:c", domain="test2", label="C")
    graph2 = ConceptGraph(nodes=(c,), edges=())
    source2 = {"provider": "self-check-2", "license": "https://creativecommons.org/licenses/by/4.0/"}
    specs = (
        GraphSpec(key="g1", loader=lambda: graph, source=lambda: source, description="first"),
        GraphSpec(key="g2", loader=lambda: graph2, source=lambda: source2, description="second"),
    )

    multi_files = build_multi_graph_dataset_files(specs, repo_id="example/multi")
    assert set(multi_files) == {
        "g1/nodes.jsonl", "g1/associations.jsonl", "g1/manifest.json",
        "g2/nodes.jsonl", "g2/associations.jsonl", "g2/manifest.json",
        "index.json", "README.md",
    }
    g1_manifest = json.loads(multi_files["g1/manifest.json"])
    g2_manifest = json.loads(multi_files["g2/manifest.json"])
    assert g1_manifest["license"] == "other" and g1_manifest["source"] == source
    assert g2_manifest["license"] == "cc-by-4.0" and g2_manifest["source"] == source2
    # Neither per-graph manifest picked up the other's license or source --
    # the concrete failure mode the provenance requirement rules out.
    assert g1_manifest["source"] != g2_manifest["source"]

    index = json.loads(multi_files["index.json"])
    by_key = {g["key"]: g for g in index["graphs"]}
    assert set(by_key) == {"g1", "g2"}
    assert by_key["g1"]["license"] == "other"
    assert by_key["g2"]["license"] == "cc-by-4.0"

    readme = multi_files["README.md"].decode()
    assert "license:" not in readme.split("---", 2)[1], (
        "root card front matter must not declare a single blanket license"
    )
    assert "Licenses vary by directory" in readme
    assert "g1/" in readme and "g2/" in readme

    # Duplicate keys and an empty selection are both refused, not silently
    # merged/no-op'd -- either would make the index misdescribe the commit.
    try:
        build_multi_graph_dataset_files(
            (specs[0], dataclasses.replace(specs[1], key="g1")), repo_id="example/multi"
        )
        raise AssertionError("duplicate graph keys must be rejected")
    except ValueError:
        pass
    try:
        build_multi_graph_dataset_files((), repo_id="example/multi")
        raise AssertionError("an empty graph selection must be rejected")
    except ValueError:
        pass

    saved = os.environ.pop("HF_TOKEN", None)
    try:
        multi_result = publish_many(specs, "example/multi-dry-run")
    finally:
        if saved is not None:
            os.environ["HF_TOKEN"] = saved
    assert multi_result.dry_run is True and multi_result.repo_url is None
    assert set(multi_result.files) == set(multi_files)

    print("OK: build_multi_graph_dataset_files/publish_many keep every graph's "
          "license and source independent, and reject duplicate/empty selections")

    # teach-8xw.55: the REAL registry -- every graph this repo actually
    # ships -- builds offline (local teach/data/*.json reads, no network)
    # without error, with unique keys, and Judson's GFDL notice survives
    # into both its own manifest and the root card.
    registry = _graph_registry()
    assert len(registry) >= 10, (
        f"expected at least 10 registered graphs, got {len(registry)}: {sorted(registry)}"
    )
    all_files = build_multi_graph_dataset_files(list(registry.values()), repo_id="example/all")
    real_index = json.loads(all_files["index.json"])
    licenses = {g["key"]: g["license"] for g in real_index["graphs"]}
    assert licenses["va-math-sol-k8"] == "cc-by-4.0"
    assert licenses["judson-algebra"] == "gfdl"
    judson_manifest = json.loads(all_files["judson-algebra/manifest.json"])
    assert "Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer" in (
        judson_manifest["source"]["attribution"]
    )
    real_readme = all_files["README.md"].decode()
    assert "Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer" in real_readme
    assert "license: gfdl" not in real_readme.split("---", 2)[1]  # not in front matter

    # teach-8xw.54: the four Learning-Commons-derived graphs predate
    # upstream_provenance.py's record, so their published source block must
    # say "unrecorded" -- honestly, not silently omitted (that would read as
    # "not applicable") and not a freshly-hashed download passed off as
    # theirs (that would be a fabricated audit trail).
    for key in (
        "va-math-sol-k8", "va-math-sol-hs", "va-reading-sol-k8", "va-writing-sol-k12",
    ):
        manifest = json.loads(all_files[f"{key}/manifest.json"])
        assert manifest["source"]["upstream_state"] == "unrecorded", (key, manifest["source"])
    # Graphs with unrelated source documents get no upstream_state key at
    # all -- the question doesn't apply to them.
    for key in ("judson-algebra", "va-world-language-sol", "actfl-can-do-interpersonal"):
        manifest = json.loads(all_files[f"{key}/manifest.json"])
        assert "upstream_state" not in manifest["source"], (key, manifest["source"])

    print(
        f"OK: the real graph registry ({len(registry)} graphs, keys: "
        f"{', '.join(sorted(registry))}) builds offline with independent "
        "per-graph licenses, and Judson's GFDL notice survives into the "
        "published artifact"
    )

    # teach-8xw.58: the five graphs with a confirmed, non-mappable usage
    # restriction (ACTFL's four Can-Do graphs plus va-world-language-sol)
    # must dry-run cleanly (a reviewer can still inspect what would ship)
    # but refuse outright on an actual live push -- pending a repo-owner
    # decision this self-check cannot make for them.
    blocked_keys = {
        "va-world-language-sol",
        "actfl-can-do-interpersonal",
        "actfl-can-do-interpretive",
        "actfl-can-do-presentational",
        "actfl-can-do-intercultural",
    }
    blocked_specs = [registry[k] for k in blocked_keys]
    assert all(s.blocked_reason for s in blocked_specs), (
        "every graph with a confirmed non-mappable usage restriction must "
        "carry a blocked_reason -- an unblocked one here would silently "
        "re-open the gap teach-8xw.58 closed"
    )
    unblocked = [k for k, s in registry.items() if k not in blocked_keys and s.blocked_reason]
    assert not unblocked, (
        f"unexpected blocked_reason on graph(s) not part of teach-8xw.58's "
        f"known restricted set: {unblocked}"
    )

    dry = publish_many(blocked_specs, "example/blocked-dry-run", dry_run=True)
    assert dry.dry_run is True  # inspection must still work

    try:
        publish_many(blocked_specs, "example/blocked-live", token="fake-token", dry_run=False)
        raise AssertionError("a blocked graph must refuse a live publish")
    except ValueError as exc:
        assert "actfl-can-do-interpersonal" in str(exc)
        assert "va-world-language-sol" in str(exc)

    # A live selection that mixes one blocked graph into an otherwise-clear
    # batch must refuse the WHOLE batch, not silently drop the blocked one --
    # silently dropping it would publish something other than what was asked
    # for without saying so.
    mixed = [registry["judson-algebra"], registry["actfl-can-do-interpersonal"]]
    try:
        publish_many(mixed, "example/mixed-live", token="fake-token", dry_run=False)
        raise AssertionError("a live publish must refuse if ANY selected graph is blocked")
    except ValueError as exc:
        assert "actfl-can-do-interpersonal" in str(exc)

    print(
        "OK: graphs with a confirmed non-mappable usage restriction "
        "(va-world-language-sol, the four actfl-can-do-* graphs) dry-run "
        "cleanly but refuse a live publish, individually or mixed into a "
        "larger batch, until a repo-owner licensing decision is recorded"
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
