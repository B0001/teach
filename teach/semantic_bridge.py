"""Reading side of the LLM-proposed bridge between the foundational layer and
the algebraic one (teach-b5k.2).

`teach/extract_semantic_bridge.py` writes the candidates by asking a local
model; this module reads them back and is the only thing downstream code
should import. It exists mainly to make one thing hard to get wrong:

    NOTHING IN THIS FILE IS AN EDGE UNTIL THE CHECKER HAS PASSED ON IT.

`load_bridge_candidates()` returns records carrying `status: "unverified"`.
There is deliberately no function here that turns them into
`PrerequisiteEdge`s -- that conversion belongs after `teach-b5k.3`'s
independent check, so no caller can accidentally traverse a graph containing
edges a language model guessed. `sandbox-prompt.md`: a result is a candidate
until something measured says otherwise, and the consumer of an output cannot
tell which mode it is in unless the code makes the distinction for them.

TRANSITIVE REDUNDANCY is removed mechanically rather than by not asking. Every
one of the 12 x 20 foundation/algebra pairs was put to the model; a proposed
bridge whose destination is already reachable from the same source through
another asserted edge adds nothing to a traversal, and `redundant_against()`
identifies those so the assembly step can drop them with a reason recorded,
instead of the pair silently never having been considered.
"""
from __future__ import annotations

import json
from pathlib import Path

_DATA_PATH = Path(__file__).parent / "data" / "semantic_bridge_candidates.json"

#: Relations the producer was allowed to return, plus the error sentinel.
RELATIONS = ("is-prerequisite-for", "generalizes", "is-example-of", "none")


def load_bridge_data() -> dict:
    """The whole file, including the producer block (model, prompt hash) and
    the honesty banner. Exposed so a caller can report provenance."""
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_bridge_candidates(include_none: bool = False) -> tuple[dict, ...]:
    """Candidate records. By default only those where the model proposed some
    relation; pass `include_none=True` to see the full asked-pair space, which
    is what makes the base rate visible.

    A high proportion of non-"none" answers is not a good sign: the pairs were
    not pre-filtered, so most of them genuinely are unrelated, and a model that
    finds a relation everywhere is agreeing with the question.
    """
    records = load_bridge_data()["candidates"]
    if include_none:
        return tuple(records)
    return tuple(r for r in records if r["relation"] not in ("none", "ERROR"))


def relation_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in load_bridge_data()["candidates"]:
        counts[r["relation"]] = counts.get(r["relation"], 0) + 1
    return counts


def redundant_against(src: str, dst: str, edges) -> bool:
    """Is `dst` already reachable from `src` through `edges`?

    Used to drop bridge proposals that a traversal would get for free. Plain
    forward reachability, not a claim about the mathematics.
    """
    outgoing: dict[str, list[str]] = {}
    for e in edges:
        outgoing.setdefault(e.src, []).append(e.dst)

    seen: set[str] = set()
    stack = list(outgoing.get(src, ()))
    while stack:
        node = stack.pop()
        if node == dst:
            return True
        if node in seen:
            continue
        seen.add(node)
        stack.extend(outgoing.get(node, ()))
    return False


def _self_check() -> None:
    data = load_bridge_data()
    assert data["schema"] == "semantic-bridge-candidates-v1"
    assert data["status"].startswith("UNVERIFIED"), (
        "the honesty banner was removed from the candidates file"
    )
    assert data["producer"]["model"]
    assert data["producer"]["temperature"] == 0

    everything = load_bridge_candidates(include_none=True)
    asked = data["pair_space"]["pairs_asked"]
    assert len(everything) == asked, (len(everything), asked)

    for r in everything:
        assert r["status"] == "unverified", r
        assert r["relation"] in RELATIONS + ("ERROR",), r["relation"]
        assert len(r["prompt_sha256"]) == 64

    proposed = load_bridge_candidates()
    assert all(r["relation"] not in ("none", "ERROR") for r in proposed)

    counts = relation_counts()
    # MEASURED, 240 pairs, llama3:latest at temperature 0:
    #   generalizes 125, none 112, is-prerequisite-for 2, ERROR 1
    # "none" is NOT the plurality, on a pair space where most pairs genuinely
    # are unrelated -- the producer over-reports "generalizes" and almost never
    # uses the one relation this repo's edge rule can test. It is agreeing with
    # the question rather than reading the definitions, which is the thing the
    # checker exists for. Recorded here rather than asserted as a target; the
    # shape of the finding is pinned in tests/test_semantic_bridge.py.
    assert counts.get("none", 0) > 0, counts

    # Reachability helper, on a graph small enough to check by eye.
    from teach.concept_graph import PrerequisiteEdge

    edges = (PrerequisiteEdge(src="a", dst="b"), PrerequisiteEdge(src="b", dst="c"))
    assert redundant_against("a", "c", edges)
    assert not redundant_against("c", "a", edges)
    assert not redundant_against("a", "d", edges)

    print(f"OK: {len(everything)} pairs asked, {len(proposed)} relations proposed, "
          f"counts={counts}")
    print(f"    ALL UNVERIFIED -- producer output from {data['producer']['model']}; "
          "teach-b5k.3 has to pass on these before any of them is an edge")


if __name__ == "__main__":
    _self_check()
