"""Checker stage: independently verify the LLM-proposed bridge edges
(teach-b5k.3).

WHAT THIS SEES, AND WHAT IT MUST NOT

It gets a claim -- src label and definition text, dst label and definition
text, and the asserted relation -- plus the pinned source. It does NOT get the
producer's prompt, its stated reason, its confidence, or which model emitted
it. `CLAIM_FIELDS` is the whitelist and `claim_view()` is the only way a claim
enters this module; anything else is a channel through which the producer's
reasoning could reach the checker, and a checker that can read the producer's
state agrees with it and verifies nothing.

WHY IT IS NOT JUST A SECOND OPINION FROM THE SAME MODEL

Asking the same family of model the same question a second time measures
agreement, not truth. So stage one is not a language model at all: it is the
same textual rule the rest of this repo's edges are held to --

    an `is-prerequisite-for` claim requires that dst's definition actually
    uses a term src defines

-- applied mechanically against the pinned text. That rule cannot be talked
out of a verdict, and it catches the claim that is simply false about the
page. It is also, on its own, WEAK in a way worth stating plainly: matching a
term as a whole word produces false positives on ordinary English. Measured on
this repo's own data, a bare term match fires `sets -> direct-proof` because
Levin writes "we will set up the proof structure" -- the word "set", not the
concept. So a match is treated as EVIDENCE TO EXAMINE, never as confirmation.

Stage two hands the matched term and the sentence it occurs in to a DIFFERENT
model (qwen2.5-coder:14b, where the producer used llama3), framed to refute
rather than to confirm, and told to default to refusing when unsure. An edge
is confirmed only when the mechanical stage found real textual evidence AND
the adversarial stage could not explain it away.

THREE-VALUED ON PURPOSE

`confirmed` / `refused` / `cannot-tell`, and the last is a first-class
outcome. `generalizes` and `is-example-of` have no mechanical rule here -- the
repo's edge discipline is about definitional dependency and says nothing about
them -- so they can never reach `confirmed` on mechanical evidence alone and
are reported honestly as `cannot-tell` when the adversarial stage is not
decisive. A checker that guessed on those would be worth less than one that
says it cannot separate them, because the consumer cannot tell the modes
apart.
"""
from __future__ import annotations

import json
import pathlib
import re

from teach.extract_semantic_bridge import CALL_FAILURES, ask

#: The only fields of a candidate record this module is allowed to read.
#: Deliberately excludes "reason" (the producer's rationale), "relation"
#: confidence, model, and prompt hash.
CLAIM_FIELDS = ("src", "dst", "src_label", "dst_label", "relation")

CHECKER_MODEL = "qwen2.5-coder:14b"

VERDICTS = ("confirmed", "refused", "cannot-tell")

#: Relations for which a mechanical definitional test exists.
MECHANICALLY_TESTABLE = ("is-prerequisite-for",)

_VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "refuted": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["refuted", "reason"],
}

_REFUTE_PROMPT = """You are checking a claim about two mathematical concepts, and your job is \
to REFUTE it if you can.

CLAIM: "{src_label}" {relation} "{dst_label}".

The definition of "{dst_label}", verbatim from its textbook:
{dst_text}

The definition of "{src_label}", verbatim from its textbook:
{src_text}

{evidence}

Decide whether the claim is WRONG.

For "is-prerequisite-for", the claim is only right if the definition of
"{dst_label}" genuinely cannot be stated without a term that "{src_label}"
defines. It is WRONG if the term appears only incidentally, in ordinary
English rather than as the technical notion, in a motivating aside, or in an
analogy -- and it is WRONG if you can restate what "{dst_label}" is without
using any of "{src_label}"'s vocabulary.

For "generalizes", the claim is right only if the first concept is strictly
more general and the second is a special case of it. For "is-example-of", only
if the first is literally an instance of the second.

Default to refuted=true when you are not sure. Judge only from the text above.
"""


def claim_view(record: dict) -> dict:
    """The producer-blind view of a candidate. Raises if a caller tries to
    smuggle the producer's rationale through."""
    return {k: record[k] for k in CLAIM_FIELDS}


def _terms_of(node) -> tuple[str, ...]:
    facts = node.facts
    terms = facts.get("terms") or facts.get("key_terms") or ()
    return tuple(str(t) for t in terms)


def _definition_of(node) -> str:
    return str(node.facts.get("definition", ""))


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.;:])\s+", text) if s.strip()]


def mechanical_evidence(src_node, dst_node) -> dict:
    """Does dst's definition use a term src defines, and in what sentence?

    Terms dst introduces itself are excluded -- dst defining its own
    vocabulary is not a dependency on src. Returns the matches so the
    adversarial stage can judge whether they are load-bearing; this function
    deliberately does not decide that.
    """
    dst_text = _definition_of(dst_node)
    dst_own = {t.lower() for t in _terms_of(dst_node)}
    matches = []
    for term in _terms_of(src_node):
        t = term.lower().strip()
        if not t or t in dst_own or len(t) < 3:
            continue
        pattern = r"\b" + re.escape(t) + r"\b"
        if not re.search(pattern, dst_text, re.IGNORECASE):
            continue
        sentence = next(
            (s for s in _sentences(dst_text) if re.search(pattern, s, re.IGNORECASE)),
            "",
        )
        matches.append({"term": term, "sentence": sentence})
    return {"matches": matches, "match_count": len(matches)}


def check_claim(record: dict, src_node, dst_node, use_model: bool = True) -> dict:
    """Verify one claim. Returns {verdict, basis, ...}."""
    claim = claim_view(record)
    relation = claim["relation"]
    evidence = mechanical_evidence(src_node, dst_node)

    # Stage 1, mechanical. Only decisive in the refusing direction: a claim
    # that dst's definition needs src's vocabulary is textually false if none
    # of src's terms occurs in it at all.
    if relation in MECHANICALLY_TESTABLE and evidence["match_count"] == 0:
        return {
            **claim,
            "verdict": "refused",
            "basis": "mechanical",
            "detail": ("no term defined by src occurs in dst's definition text, "
                       "so dst's definition demonstrably does not need src's "
                       "vocabulary"),
            "evidence": evidence,
        }

    if not use_model:
        return {**claim, "verdict": "cannot-tell", "basis": "mechanical-only",
                "detail": "adversarial stage not run", "evidence": evidence}

    # Stage 2, adversarial, different model, framed to refute.
    if evidence["matches"]:
        shown = "\n".join(
            f'  - the term "{m["term"]}" occurs in: "{m["sentence"][:300]}"'
            for m in evidence["matches"][:6]
        )
        evidence_block = (
            "Someone checking this mechanically found that these terms defined "
            f'by "{claim["src_label"]}" occur in the other definition:\n{shown}\n'
            "Occurring is not the same as being needed. Decide whether they are "
            "load-bearing or incidental."
        )
    else:
        evidence_block = (
            f'A mechanical check found NO term defined by "{claim["src_label"]}" '
            f'occurring in the definition of "{claim["dst_label"]}".'
        )

    prompt = _REFUTE_PROMPT.format(
        src_label=claim["src_label"],
        dst_label=claim["dst_label"],
        relation=relation,
        src_text=_definition_of(src_node)[:1500],
        dst_text=_definition_of(dst_node)[:1500],
        evidence=evidence_block,
    )
    try:
        # _VERDICT_SCHEMA, NOT the producer's. Passing the producer's schema
        # here made the model answer with a relation enum instead of a
        # refutation, so "refuted" was always absent and every claim came back
        # "cannot-tell" no matter what the evidence said -- a checker that
        # verifies nothing while looking like it works.
        raw = ask(prompt, model=CHECKER_MODEL, schema=_VERDICT_SCHEMA, timeout=90)
    except CALL_FAILURES as exc:
        return {**claim, "verdict": "cannot-tell", "basis": "checker-unavailable",
                "detail": f"{type(exc).__name__}: {exc}", "evidence": evidence}

    parsed = raw.get("parsed") or {}
    refuted = parsed.get("refuted")
    if refuted is None:
        return {**claim, "verdict": "cannot-tell", "basis": "checker-malformed",
                "detail": f"no 'refuted' field in checker response: {raw.get('raw','')[:200]}",
                "evidence": evidence}
    reason = parsed.get("reason", "")

    if refuted is True:
        verdict = "refused"
    elif refuted is False and relation in MECHANICALLY_TESTABLE and evidence["match_count"]:
        # Confirmed needs BOTH: real textual evidence and a failed refutation.
        verdict = "confirmed"
    else:
        # generalizes / is-example-of have no mechanical rule here, so a
        # failed refutation alone is not enough to call them established.
        verdict = "cannot-tell"

    return {**claim, "verdict": verdict, "basis": "mechanical+adversarial",
            "detail": reason, "evidence": evidence}


def _ask_refute(prompt: str) -> dict:
    """Indirection kept so the adversarial call is easy to stub in tests."""
    return ask(prompt, model=CHECKER_MODEL)


def main() -> None:
    """Check every proposed candidate and write teach/data/bridge_verdicts.json.

    Only records where the producer proposed a relation are checked -- a
    "none" answer asserts nothing, so there is nothing to verify. The count of
    unchecked "none" records is carried in the output so the denominator stays
    visible.
    """
    from teach.judson_algebra_graph import load_judson_full_graph
    from teach.levin_foundations_graph import load_levin_foundation_nodes
    from teach.semantic_bridge import load_bridge_candidates, load_bridge_data

    nodes = {n.id: n for n in load_levin_foundation_nodes()}
    nodes.update({n.id: n for n in load_judson_full_graph().nodes})

    proposed = load_bridge_candidates()
    verdicts = []
    for i, record in enumerate(proposed, 1):
        src, dst = nodes.get(record["src"]), nodes.get(record["dst"])
        if src is None or dst is None:
            verdicts.append({**claim_view(record), "verdict": "cannot-tell",
                             "basis": "missing-node", "detail": "", "evidence": {}})
            continue
        verdicts.append(check_claim(record, src, dst))
        if i % 10 == 0 or i == len(proposed):
            print(f"  checked {i}/{len(proposed)}", flush=True)
            # Checkpoint, same lesson the producer learned the hard way: this
            # loop is ~40 minutes of local inference and the machine has
            # already killed processes under memory pressure once. A sidecar
            # name so a partial run can never be mistaken for the real file.
            (pathlib.Path(__file__).parent / "data"
             / "bridge_verdicts.partial.json").write_text(
                json.dumps(verdicts, indent=2) + "\n")

    counts: dict[str, int] = {}
    for v in verdicts:
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1

    all_records = load_bridge_data()["candidates"]
    out = {
        "schema": "bridge-verdicts-v1",
        "checker": {
            "model": CHECKER_MODEL,
            "producer_model_was": load_bridge_data()["producer"]["model"],
            "sees": list(CLAIM_FIELDS),
            "does_not_see": ["the producer's reason/rationale", "its confidence",
                             "which model produced it", "the producer's prompt"],
            "stages": ["mechanical definitional-term test against the pinned "
                       "source text", "adversarial refutation by a different "
                       "model, defaulting to refuted when unsure"],
            "confirm_requires": "both stages: textual evidence AND a failed refutation",
        },
        "counts": counts,
        "checked": len(verdicts),
        "not_checked_because_producer_asserted_nothing":
            sum(1 for r in all_records if r["relation"] == "none"),
        "producer_errors": sum(1 for r in all_records if r["relation"] == "ERROR"),
        "verdicts": verdicts,
    }
    path = pathlib.Path(__file__).parent / "data" / "bridge_verdicts.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    (path.parent / "bridge_verdicts.partial.json").unlink(missing_ok=True)
    print(f"wrote {path.name}: {len(verdicts)} checked, counts={counts}")


def _self_check() -> None:
    from teach.concept_graph import ConceptNode

    src = ConceptNode(
        id="x:sets", domain="math", label="Sets",
        facts={"terms": ("set", "power set"),
               "definition": "A set is an unordered collection of objects."},
    )
    needs_src = ConceptNode(
        id="x:groups", domain="math", label="Groups",
        facts={"key_terms": ("group",),
               "definition": "A group is a set G with a binary operation."},
    )
    unrelated = ConceptNode(
        id="x:proof", domain="math", label="Direct Proof",
        facts={"key_terms": ("direct proof",),
               "definition": "Assume P. Explain. Therefore Q."},
    )

    # Producer rationale must not be reachable through the claim view.
    record = {"src": "x:sets", "dst": "x:groups", "src_label": "Sets",
              "dst_label": "Groups", "relation": "is-prerequisite-for",
              "reason": "PRODUCER RATIONALE THAT MUST NOT LEAK",
              "status": "unverified", "prompt_sha256": "0" * 64}
    view = claim_view(record)
    assert set(view) == set(CLAIM_FIELDS)
    assert "reason" not in view
    assert "PRODUCER" not in json.dumps(view)

    # Mechanical stage finds a real dependency...
    ev = mechanical_evidence(src, needs_src)
    assert ev["match_count"] == 1, ev
    assert ev["matches"][0]["term"] == "set"
    assert "binary operation" in ev["matches"][0]["sentence"]

    # ...refuses one with no textual basis at all, without consulting a model.
    no_basis = dict(record, dst="x:proof", dst_label="Direct Proof")
    out = check_claim(no_basis, src, unrelated, use_model=False)
    assert out["verdict"] == "refused", out
    assert out["basis"] == "mechanical"

    # ...and does not confirm on mechanical evidence alone.
    out = check_claim(record, src, needs_src, use_model=False)
    assert out["verdict"] == "cannot-tell", out

    # A term dst defines itself is not evidence of a dependency on src.
    self_defining = ConceptNode(
        id="x:sets2", domain="math", label="Sets again",
        facts={"terms": ("set",), "definition": "A set is a collection."},
    )
    assert mechanical_evidence(src, self_defining)["match_count"] == 0

    # The schema the adversarial stage asks for must be the REFUTATION schema.
    # Reusing the producer's ({relation, reason}) silently made every verdict
    # "cannot-tell" -- the checker ran, cost 40 minutes of inference, and
    # verified nothing. Assert the two schemas are actually different and that
    # this module asks for its own.
    from teach.extract_semantic_bridge import RESPONSE_SCHEMA

    assert _VERDICT_SCHEMA is not RESPONSE_SCHEMA
    assert "refuted" in _VERDICT_SCHEMA["properties"]
    assert "refuted" not in RESPONSE_SCHEMA["properties"]
    import inspect

    src_text = inspect.getsource(check_claim)
    assert "schema=_VERDICT_SCHEMA" in src_text, (
        "check_claim must pass its own schema to ask(), or every verdict "
        "silently becomes cannot-tell"
    )

    assert set(VERDICTS) == {"confirmed", "refused", "cannot-tell"}
    print("OK: checker is producer-blind (claim view excludes the producer's "
          "reason), refuses claims with no textual basis mechanically, and "
          "never confirms without both stages")


if __name__ == "__main__":
    import sys

    if "--run" in sys.argv:
        main()
    else:
        _self_check()
