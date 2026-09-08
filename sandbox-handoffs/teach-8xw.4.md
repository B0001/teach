# teach-8xw.4 — Decide the domain-plugin architecture before writing math-specific graph code

## Bottom line

**Decided and recorded via `bd update teach-8xw.4 --design=...` on this bead** (full text there, not duplicated as a separate doc file per the bead's own instruction). Summary:

- **Node/edge schema**: `ConceptNode(id, domain, label, standard_ref=None, facts={})` and `PrerequisiteEdge(src, dst, type="precedes")`. `id`/`domain`/`standard_ref`/`facts` are opaque to the engine — a globally-unique string a domain namespaces itself, a tag never branched on, and an unread payload, respectively. Edge direction (`src` before `dst`) matches CASE's `precedes` semantics, confirmed live against `opensalt.net` in `teach-8xw.3` — and is explicitly the *opposite* direction from mathgraph's own `depends_on` edges, which is exactly the kind of math-tool-shaped assumption this bead was filed to catch before teach-8xw.5 copies it uninspected.
- **Domain-plugin boundary**: the graph type + validation (duplicate ids, dangling edges, cycle detection) + topological traversal are shared engine code, kept domain-ignorant by construction (no field or branch anywhere reads `.domain` to decide behavior). Per-domain node/edge *instances* and the shape of `.facts` are data, owned by each domain. Domain fact-verification (real logic, e.g. "is this group theory correct") is deliberately *not* built here — flagged as a reserved seam (claim-in/verdict-out interface) for `teach-8xw.11`, so that bead doesn't accidentally grow domain-specific imports into the graph core.

## What's in the repo now

- `teach/concept_graph.py` — `ConceptNode`, `PrerequisiteEdge`, `ConceptGraph` (`by_id`, `validate`, `topological_order`), `GraphError`. Self-check (`python3 -m teach.concept_graph` / `if __name__ == "__main__"`) builds one graph mixing a Dummit & Foote-named math node and a VA-reading-SOL-named node, traverses both with the same call, and proves a 2-node cycle is rejected rather than silently ordered.
- `tests/test_concept_graph.py` — 9 tests: single-domain chain order, cross-domain traversal with no special-casing, opaque `facts`/`standard_ref` payload, `by_id` lookup + `KeyError` on miss, duplicate-id rejection, dangling-edge rejection, cycle rejection, open (non-enum) edge `type` string, and a diamond-shaped (non-chain) DAG to prove the traversal isn't just handling straight lines.

This is intentionally *not* the VA Math SOL graph itself, and not a `DomainPlugin` class with speculative verification methods — both are explicitly out of scope (the former is `teach-8xw.5`'s job, the latter `teach-8xw.11`'s). Building either here would have been exactly the kind of half-finished, un-asked-for scope this repo's working rules warn against.

## Why this shape, concretely

Two design choices were the ones actually at risk of baking in math assumptions, so they got the most attention:

1. **`facts`/`standard_ref` as opaque payload, not typed fields.** A node for "one SOL standard code" and a node for "one Dummit & Foote theorem" and a node for "one reading-comprehension skill" all fit the exact same dataclass, because neither field means anything to `ConceptNode` itself — proven by `test_facts_and_standard_ref_are_opaque_payload` and the self-check's two-domain graph, not just asserted in a comment.
2. **Edge direction matching CASE, not mathgraph.** This was verified against real data, not recalled: `curl https://opensalt.net/ims/case/v1p0/CFPackages/aa7ab56a-276b-11ef-8aff-0242ac140003` this session (same package `teach-8xw.3` used) confirms `CFAssociation.originNodeURI`/`destinationNodeURI` shape, and 1EdTech's own spec text (already fetched raw in `teach-8xw.3`) defines `precedes` as "origin before destination in time or order." Cross-checked against `/workspace-mathgraph/mathgraph/graph.py:48-54`, which builds `depends_on` edges from `b.uses`/`b.refs` — a claim pointing at the lemmas *it* needs, i.e. the reverse direction. Recording this explicitly in the design decision (not just picking one silently) means a future worker copying data shaped like mathgraph's output into this repo's `PrerequisiteEdge` gets a documented invert-direction warning instead of a silently backwards prerequisite graph.

## Verification

```
uv run python3 -m teach.concept_graph   # OK: two domains, one traversal call, cycle rejected
uv run pytest -q                        # 55 passed (46 pre-existing + 9 new)
```

No existing file was modified — `teach/producer_state.py`'s `PlannerState.traversal: tuple[str, ...]` was already domain-agnostic (plain node-id strings) before this bead, which is consistent with, not contradicted by, the schema decided here: those strings are meant to be `ConceptNode.id` values in `ConceptGraph.topological_order()` order.

## What this does NOT do

- Does not build the VA Math SOL graph (`teach-8xw.5`, now unblocked) or any real domain's node/edge data.
- Does not implement domain fact verification or a `DomainPlugin` protocol/class — reserved as a seam for `teach-8xw.11`, not built speculatively here.
- Does not touch `teach/boundary.py`, `teach/producer_state.py`, `teach/cbt_primitives.py`, `teach/honesty_rubric.py`, or `teach/potential_checker.py` — all already independently domain-agnostic (operate on plain strings/text), confirmed by reading them, not assumed.

## Files touched

- Added: `teach/concept_graph.py`, `tests/test_concept_graph.py`, `sandbox-handoffs/teach-8xw.4.md`.
- Bead: `bd update teach-8xw.4 --design=...` (see bead for full text).
- Nothing committed — conservative git policy, bead did not say to commit.
