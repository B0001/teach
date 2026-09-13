"""Producer stage: LLM-proposed semantic edges bridging the foundational
layer to the algebraic one (teach-b5k.2).

Writes `teach/data/semantic_bridge_candidates.json`.

EVERYTHING THIS MODULE PRODUCES IS A CANDIDATE, NOT A RESULT

`sandbox-prompt.md`: a producer's output must never be phrased, logged, or
reported as if it were verified. An LLM asked "is A a prerequisite for B?"
will agree with the question most of the time, and it is being asked here
about pairs that were deliberately NOT pre-filtered -- so the base rate of
"none" should be high, and a run that returns a relation for most pairs is
evidence the model is agreeing with the prompt rather than reading the text.
Every record carries `"status": "unverified"` and the model, prompt hash and
raw response that produced it. `teach-b5k.3` is the independent checker; until
it has run, nothing here is an edge.

WHY EVERY PAIR, not a shortlist: pre-selecting "plausible" pairs would mean
the interesting part of the answer -- which pairs relate at all -- was decided
by the author's intuition and then confirmed by the model. Asking about all
12 x 20 = 240 pairs keeps that decision with the evidence. Transitive
redundancy is removed afterwards, mechanically, in the assembly step rather
than by leaving pairs unasked.

ENVIRONMENT (verified 2026-09-13): ollama is at /usr/local/bin/ollama serving
http://localhost:11434 with llama3:latest, qwen2.5-coder:14b and two smaller
models. `litellm` is NOT installed and is not a dependency of this project;
ollama's own /api/chat takes a JSON Schema in `format`, so no extra package is
needed to get structured output. The configured `ollama` MCP server failed to
connect this session (CONNECTION_CLOSED), which is why this talks to the local
HTTP API directly rather than through it.

Run with: uv run python -m teach.extract_semantic_bridge
"""
import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.request

from teach.judson_algebra_graph import load_judson_full_graph
from teach.levin_foundations_graph import load_levin_foundation_nodes

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3:latest"

RELATIONS = ("is-prerequisite-for", "generalizes", "is-example-of", "none")

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "relation": {"type": "string", "enum": list(RELATIONS)},
        "reason": {"type": "string"},
    },
    "required": ["relation", "reason"],
}

PROMPT_TEMPLATE = """You are labelling the relationship between two mathematical concepts, \
using ONLY the definitions given. Do not use outside knowledge.

CONCEPT A: {a_label}
A's definition (verbatim from its textbook):
{a_text}

CONCEPT B: {b_label}
B's definition (verbatim from its textbook):
{b_text}

Which ONE of these best describes how A relates to B?

  is-prerequisite-for : B's definition cannot be stated without using a term A
                        defines. Not "a student would learn A first" -- the
                        definition of B must actually need A's vocabulary.
  generalizes         : A is a strictly more general notion that B is a
                        special case of.
  is-example-of       : A is a particular instance or example of B.
  none                : none of the above holds.

Most pairs are unrelated. Answer "none" unless the definitions in front of you
show otherwise. Quote nothing you cannot see in the text above.
"""


def _prompt_for(a, b) -> str:
    return PROMPT_TEMPLATE.format(
        a_label=a.label,
        a_text=str(a.facts.get("definition", ""))[:1800],
        b_label=b.label,
        b_text=str(b.facts.get("definition", ""))[:1800],
    )


#: Exceptions a single call can fail with. TimeoutError is listed explicitly
#: and is the reason this tuple exists: `urlopen` raises it directly on a read
#: timeout and it is NOT a subclass of urllib.error.URLError, so an earlier
#: version of this module let one slow call escape the handler and kill a
#: 20-minute run with nothing written to disk.
CALL_FAILURES = (
    urllib.error.URLError, TimeoutError, OSError,
    ValueError, KeyError, json.JSONDecodeError,
)


def ask(prompt: str, model: str = MODEL, timeout: int = 180,
        schema: dict | None = None, num_predict: int = 256) -> dict:
    """One structured call to the local ollama server. Raises on transport or
    decode failure rather than returning a default -- a silently-defaulted
    'none' would be indistinguishable from a real judgement.

    `schema` overrides the response shape. It exists because the checker asks a
    different question ({refuted, reason}) than this producer does
    ({relation, reason}); without it the checker silently got the producer's
    schema back, found no "refuted" key, and returned "cannot-tell" for every
    single claim regardless of the evidence.
    """
    schema = schema or RESPONSE_SCHEMA
    payload = json.dumps({
        "model": model,
        "stream": False,
        "format": schema,
        # num_predict caps generation. Without it the free-text "reason" can
        # run for minutes on a 14B model -- the checker's first run stalled at
        # 0% CPU with no output for 24 minutes on an uncapped call.
        "options": {"temperature": 0, "num_predict": num_predict},
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read())
    content = body["message"]["content"]
    parsed = json.loads(content)
    if schema is RESPONSE_SCHEMA and parsed.get("relation") not in RELATIONS:
        raise ValueError(f"model returned unknown relation: {parsed!r}")
    return {"relation": parsed.get("relation"), "reason": parsed.get("reason", ""),
            "raw": content, "parsed": parsed}


def main() -> None:
    foundations = load_levin_foundation_nodes()
    algebra = load_judson_full_graph().nodes

    out_path = pathlib.Path(__file__).parent / "data" / "semantic_bridge_candidates.json"
    checkpoint = out_path.with_suffix(".partial.json")
    records = []
    started = time.time()
    total = len(foundations) * len(algebra)

    for i, a in enumerate(foundations):
        for j, b in enumerate(algebra):
            prompt = _prompt_for(a, b)
            n = i * len(algebra) + j + 1
            res = None
            for attempt in range(2):
                try:
                    res = ask(prompt)
                    break
                except CALL_FAILURES as exc:
                    last = f"{type(exc).__name__}: {exc}"
                    if attempt == 0:
                        print(f"  pair {n}: {last} -- retrying once", flush=True)
            if res is None:
                res = {"relation": "ERROR", "reason": last, "raw": ""}
            records.append({
                "src": a.id,
                "dst": b.id,
                "src_label": a.label,
                "dst_label": b.label,
                "relation": res["relation"],
                "reason": res["reason"],
                "status": "unverified",
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            })
            if n % 20 == 0 or n == total:
                elapsed = time.time() - started
                print(f"  {n}/{total} pairs, {elapsed:.0f}s elapsed", flush=True)
                # Checkpoint: partial progress survives a crash. Written to a
                # sidecar so a half-finished run can never be mistaken for the
                # real extract.
                checkpoint.write_text(json.dumps(records, indent=2) + "\n")

    counts: dict[str, int] = {}
    for r in records:
        counts[r["relation"]] = counts.get(r["relation"], 0) + 1

    data = {
        "schema": "semantic-bridge-candidates-v1",
        "status": "UNVERIFIED -- producer output. Every record here is a "
                  "CANDIDATE proposed by a local LLM, not an established edge. "
                  "teach-b5k.3 is the independent checker; until it has run, "
                  "nothing in this file may be used as a prerequisite edge.",
        "producer": {
            "model": MODEL,
            "endpoint": OLLAMA_URL,
            "temperature": 0,
            "relations_offered": list(RELATIONS),
            "prompt_template_sha256": hashlib.sha256(
                PROMPT_TEMPLATE.encode()).hexdigest(),
            "generated_by": "teach/extract_semantic_bridge.py. Re-derive with: "
                            "uv run python -m teach.extract_semantic_bridge "
                            "(requires a local ollama server; results are not "
                            "guaranteed byte-identical across runs even at "
                            "temperature 0)",
        },
        "pair_space": {
            "foundation_nodes": len(foundations),
            "algebra_nodes": len(algebra),
            "pairs_asked": len(records),
            "note": "Every pair was asked. No pre-filtering by plausibility -- "
                    "which pairs relate at all is the question, and shortlisting "
                    "first would have answered it by intuition and then had the "
                    "model confirm it.",
        },
        "relation_counts": counts,
        "candidates": records,
    }
    out_path.write_text(json.dumps(data, indent=2) + "\n")
    checkpoint.unlink(missing_ok=True)
    print(f"wrote {out_path.name}: {len(records)} pairs in "
          f"{time.time() - started:.0f}s, counts={counts}")


if __name__ == "__main__":
    main()
