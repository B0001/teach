# teach-8xw.11 — Checker: verify domain facts in lesson text against source

## What was built

Per the epic and sandbox-prompt.md, the checker must "verify the domain
facts... against source," not just structure/tone. Nothing existed for
this before this session. teach-8xw.4 (closed) reserved the seam: "verifying
a domain fact claim... must sit behind a claim-in/verdict-out function
signature so the graph/traversal core never imports anything
domain-specific." This session filled that seam:

- `teach/fact_checker.py` — domain-agnostic engine, imports nothing
  domain-specific:
  - `Verdict`: `CONFIRMED` / `CONTRADICTED` / `CANNOT_VERIFY` (three-way, per
    the bead's acceptance criteria).
  - `SourceFact(topic, citation, topic_patterns, true_patterns,
    false_patterns)` — one theorem/fact a domain's reference source can
    adjudicate claims against. `topic_patterns` decide *aboutness*; a claim
    matching none of them is `CANNOT_VERIFY` because the source has nothing
    on it. `false_patterns` are checked before `true_patterns`, so a
    sentence that trips both resolves `CONTRADICTED`, not `CONFIRMED` (bias
    toward surfacing a problem, same principle potential_checker uses for
    effort-conditioning).
  - `SourceAdapter` (`Protocol`: `domain: str`, `facts: tuple[SourceFact,
    ...]`) — the actual per-domain plugin boundary. `verify_claim` only
    ever touches `.facts` on whatever is passed to it.
  - `verify_claim(claim_text, source) -> Verdict` — the claim-in/verdict-out
    primitive teach-8xw.4 reserved.
  - `find_topic`, `extract_domain_claims` (topic-recognized, non-question
    tutor sentences only — filters out both learner speech and tutor
    *questions*, since "is the kernel normal in the codomain?" is a prompt,
    not an assertion), `check_lesson_text` (full pipeline: lesson text +
    source in, one `FactCheck` per recognized-topic sentence out, including
    `CANNOT_VERIFY` ones — dropping those would make "0 flags" indistinguish
    -able from "nothing to check," the same coverage-accounting concern
    sandbox-prompt.md raises generally).
  - `python -m teach.fact_checker` self-check: the bead's three required
    hand-written examples (true/false/ambiguous) verify as expected.

- `teach/math_facts.py` — the math domain's reference source, the concrete
  case this bead's acceptance criteria asks for (Dummit & Foote, this
  repo's stated test case). Two `SourceFact`s, each checked against the
  actual textbook theorem number, not recalled from general group-theory
  memory:
  - `kernel-normal-subgroup` (D&F 3rd ed. §3.2, Prop 7): the kernel of a
    homomorphism is a normal subgroup of the *domain*. False patterns catch
    the direct negation and the specific wrong-target-group misstatements
    (kernel normal in the *codomain* — a category error, the kernel isn't
    even a subset of the codomain; and the unrelated-but-plausible-sounding
    false claim that the *image* is normal in the codomain, which is false
    in general).
  - `lagrange-order-divides` (D&F 3rd ed. §3.2, Thm 8): `|H|` divides `|G|`
    for a subgroup `H` of finite `G`. False pattern catches the reversed
    direction (order of group dividing order of subgroup). Deliberately
    does NOT cover the *converse* of Lagrange (order divides implies a
    subgroup of that order exists — false in general, e.g. A4/order-6) —
    that's a different topic this fact's patterns don't adjudicate, proven
    by a test asserting it comes back `CANNOT_VERIFY`, not silently treated
    as confirmed or contradicted by an over-eager pattern.
  - `TRUE_CLAIM` / `FALSE_CLAIM` / `AMBIGUOUS_CLAIM` — the bead's required
    three hand-written examples.
  - `python -m teach.math_facts` self-check.

- `tests/test_fact_checker.py` — 13 tests, all passing (69 total in the
  suite): the three required examples; an off-topic claim (`CANNOT_VERIFY`,
  the "topic not covered" flavor, distinct from `AMBIGUOUS_CLAIM`'s "topic
  covered, wording unclear" flavor); false-beats-true precedence; both
  Lagrange directions plus the converse-is-a-different-topic case;
  `check_lesson_text` only reporting recognized-topic sentences, ignoring
  learner speech, still reporting `CANNOT_VERIFY` sentences (not dropping
  them), and working on plain unspeaker-tagged text; `extract_domain_claims`
  filtering to recognized topics and returning empty when nothing matches.

## What this does NOT do

- **Heuristic pattern matching, not a theorem prover or NLP entailment
  engine.** Same caveat teach/potential_checker.py states for its own
  domain: it will miss phrasing it doesn't recognize (undercoverage,
  surfaces as the safe `CANNOT_VERIFY`, never as a false `CONFIRMED`) and
  could in principle mismatch phrasing that only superficially resembles a
  known pattern. Two source facts, covering two Dummit & Foote theorems, is
  proof of the mechanism working — not a claim that this covers Dummit &
  Foote, or even chapter 3 of it. Extending coverage (more facts, more
  phrasing variants per fact) is direct follow-on work for whichever bead
  needs it (teach-8xw.15's D&F/Bond end-to-end run will need more facts than
  these two once it has real lesson text to check against them).
- **Does not itself decide what "the source" is for a given domain** beyond
  providing the `SourceAdapter` shape — `teach/math_facts.py` is one
  concrete adapter for one domain. teach-8xw.12 (biblical text) is
  explicitly filed separately because its sourcing requirement (BHS/DSS/
  NA27-28/UBS) needs its own access research before an adapter can be
  written for it; this bead's engine is ready to receive that adapter once
  teach-8xw.12 answers the access question, without fact_checker.py itself
  changing.
- **Question-detection is a bare `sentence.endswith("?")` check** — good
  enough to stop a tutor's Socratic question from being scored as if it
  were an assertion (this was caught by a test failure during this session:
  a tutor question containing "kernel"/"normal"/"codomain" was initially
  scored `CONTRADICTED`), but not a general speech-act classifier. A
  rhetorical assertion phrased as a question some other way wouldn't be
  caught by this.
- **No extraction-layer confidence score or per-fact provenance beyond the
  citation string** — `FactCheck` reports which `SourceFact.citation` fired,
  which is enough to point a human at "Dummit & Foote §3.2, Prop 7" and
  check it by hand, but there's no numeric confidence, and no record of
  which specific pattern within a fact's `true_patterns`/`false_patterns`
  matched.

## Verification

```
uv run python3 -m teach.math_facts     # OK: math source's 3 hand-written examples verify as expected
uv run python3 -m teach.fact_checker   # OK: true claim CONFIRMED, false claim CONTRADICTED, ambiguous claim CANNOT_VERIFY (abstained)
uv run pytest -q                       # 69 passed
```

All three commands were actually run this session (not asserted from
reading the code) — see the `test_check_lesson_text_ignores_learner_speech`
failure-then-fix above for a concrete instance of a test that did fail
before the code was correct, which is the "make it fail first" evidence
sandbox-prompt.md asks for.

## Scope note

This closes teach-8xw.11 for the math domain only, matching its own
description ("for at least the math domain... this repo's stated test
case"). teach-8xw.12 (biblical-text sourcing research) remains open and
separate, as filed. No new beads were needed — the two gaps noticed above
(coverage breadth, question-detection precision) are follow-on depth within
this bead's own stated scope, not out-of-scope discoveries, so they're
recorded here rather than filed as new beads.
