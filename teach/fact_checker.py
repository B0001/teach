"""Checker: verify domain facts asserted in lesson text against source.

sandbox-prompt.md and the epic both require the checker to "verify the
domain facts... against source" -- not just check tone or structure. This
is the general mechanism teach-8xw.11 asks for: different domains have
different notions of "source" (a math claim checked against a textbook
theorem, a historical claim checked against a citation, a biblical-text
claim checked against a critical edition -- that last one is its own bead,
teach-8xw.12, because its sourcing requirement is far more specific). What
they share is one shape: a claim in, a reference source to check it
against, a verdict out. This module is that shared shape; per-domain
reference data (teach/math_facts.py for the math case this bead's
acceptance criteria asks for) plugs into it without this module importing
anything domain-specific, mirroring the domain-plugin boundary
teach-8xw.4 decided and the seam it explicitly reserved for this bead:
"verifying a domain fact claim... must sit behind a claim-in/verdict-out
function signature."

This is a blind checker per sandbox-prompt.md: it only ever sees rendered
lesson text (what the learner saw, via teach.boundary.LessonArtifact.text
or any plain string) and a reference source supplied by the domain --
never the producer's planner state.

THREE-WAY VERDICT, NOT TWO

  - CONFIRMED: the claim matches a source fact and restates it correctly.
  - CONTRADICTED: the claim matches a source fact and asserts something
    that fact rules out (a negation, a wrong direction, a known
    misconception).
  - CANNOT_VERIFY: either the source has nothing on this claim's topic, or
    it recognizes the topic but the claim's specific wording doesn't match
    a phrasing this checker's pattern set can adjudicate either way.

Collapsing the second case into "assume confirmed" would violate "prefer
abstention to a confident answer" -- recognizing a topic is not the same
as being able to certify a specific sentence about it. Both CANNOT_VERIFY
paths are one verdict because a consumer of this checker's output needs to
know the same thing either way: this checker did not establish that this
sentence is true.

EXTRACTION IS A HEURISTIC, NOT A PROOF, same caveat as
teach/potential_checker.py: pattern matching over English will miss
phrasing it doesn't recognize (undercoverage, surfaced as CANNOT_VERIFY --
the safe failure mode) and can occasionally mismatch phrasing that only
superficially resembles a known pattern. Every SourceFact's patterns are
checked in the order false-then-true, so a sentence that happens to trip
both a false and a true pattern is reported CONTRADICTED, not CONFIRMED --
the same "default toward surfacing, not toward silence" bias
potential_checker uses for effort-conditioning.
"""
from __future__ import annotations

import dataclasses
import enum
import re
from typing import Pattern, Protocol


class Verdict(enum.Enum):
    CONFIRMED = "confirmed"
    CONTRADICTED = "contradicted"
    CANNOT_VERIFY = "cannot_verify"


@dataclasses.dataclass(frozen=True)
class SourceFact:
    """One fact a domain's reference source can adjudicate claims against.

    topic_patterns decide *aboutness*: does this claim even touch what this
    fact covers? A claim matching no fact's topic_patterns is CANNOT_VERIFY
    by construction -- the source has nothing to say about it, which is a
    different (and more honest) outcome than guessing it's fine.

    false_patterns are checked before true_patterns by `verify_claim`, so a
    known misconception or negation wins even if it also contains the
    fact's true-statement keywords.
    """

    topic: str
    citation: str
    topic_patterns: tuple[Pattern[str], ...]
    true_patterns: tuple[Pattern[str], ...]
    false_patterns: tuple[Pattern[str], ...]


class SourceAdapter(Protocol):
    """The per-domain plugin boundary. `verify_claim` only ever touches
    `.facts` on whatever is passed to it -- never anything domain-specific
    -- so a new domain (history, foreign language, ...) plugs in by
    providing an object with this shape, not by this module growing a
    branch."""

    domain: str
    facts: tuple[SourceFact, ...]


def _matches_any(patterns: tuple[Pattern[str], ...], text: str) -> bool:
    return any(p.search(text) for p in patterns)


def find_topic(claim_text: str, source: SourceAdapter) -> SourceFact | None:
    """Which source fact (if any) this claim is about. None means the
    source has nothing on this topic at all."""
    for fact in source.facts:
        if _matches_any(fact.topic_patterns, claim_text):
            return fact
    return None


def verify_claim(claim_text: str, source: SourceAdapter) -> Verdict:
    """claim-in/verdict-out: the interface teach-8xw.4 reserved for this
    bead. Domain-ignorant -- all domain knowledge lives in `source`."""
    fact = find_topic(claim_text, source)
    if fact is None:
        return Verdict.CANNOT_VERIFY
    if _matches_any(fact.false_patterns, claim_text):
        return Verdict.CONTRADICTED
    if _matches_any(fact.true_patterns, claim_text):
        return Verdict.CONFIRMED
    return Verdict.CANNOT_VERIFY


@dataclasses.dataclass(frozen=True)
class FactCheck:
    """One sentence from lesson text that touched a source fact's topic,
    and what this checker could establish about it."""

    sentence: str
    topic: str
    citation: str
    verdict: Verdict


# --- sentence / turn segmentation -------------------------------------------
# Same speaker-turn convention as teach.potential_checker: a domain fact is
# something asserted *to* the learner, so only tutor-spoken lines are
# scanned when the text is speaker-tagged the way
# teach.boundary.LessonArtifact.text renders it. Duplicated rather than
# imported because potential_checker's helpers are private to that module
# and this is a handful of lines, not a shared abstraction worth extracting
# on this bead's scope.

_SPEAKER_LINE = re.compile(r"^(?P<speaker>[A-Za-z][\w-]*):\s*(?P<content>.*)$")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _tutor_turns(text: str) -> list[str]:
    lines = [line for line in text.splitlines() if line.strip()]
    if lines and all(_SPEAKER_LINE.match(line) for line in lines):
        return [
            m.group("content")
            for line in lines
            if (m := _SPEAKER_LINE.match(line)) and m.group("speaker").lower() == "tutor"
        ]
    return [text]


def _split_sentences(turn_text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(turn_text.strip()) if s.strip()]


def extract_domain_claims(text: str, source: SourceAdapter) -> tuple[str, ...]:
    """Sentences (tutor-spoken, per the turn convention above) whose topic
    this source recognizes at all. Sentences with no recognized topic are
    not domain-fact claims as far as this source is concerned and are not
    returned -- this is the "aboutness" filter, distinct from the
    CANNOT_VERIFY verdict a recognized-topic-but-unclear-assertion sentence
    still gets once it reaches `verify_claim`. A question is never an
    assertion regardless of what keywords it contains ("is the kernel
    normal in the codomain?" is the tutor prompting the learner, not the
    tutor claiming something) -- skip it here rather than let it reach
    `verify_claim` and be judged as if it had asserted an answer.
    """
    claims = []
    for turn_text in _tutor_turns(text):
        for sentence in _split_sentences(turn_text):
            if sentence.endswith("?"):
                continue
            if find_topic(sentence, source) is not None:
                claims.append(sentence)
    return tuple(claims)


def check_lesson_text(text: str, source: SourceAdapter) -> tuple[FactCheck, ...]:
    """The checker entry point: lesson text and a reference source in, one
    FactCheck per sentence whose topic the source recognizes. Coverage
    accounting per sandbox-prompt.md -- "state the scope you actually
    covered" -- means every recognized-topic sentence gets a result,
    including CANNOT_VERIFY ones, rather than only reporting the sentences
    this checker felt confident about.
    """
    checks = []
    for sentence in extract_domain_claims(text, source):
        fact = find_topic(sentence, source)
        assert fact is not None  # extract_domain_claims already filtered to this
        checks.append(
            FactCheck(
                sentence=sentence,
                topic=fact.topic,
                citation=fact.citation,
                verdict=verify_claim(sentence, source),
            )
        )
    return tuple(checks)


if __name__ == "__main__":
    from teach.math_facts import (
        AMBIGUOUS_CLAIM,
        FALSE_CLAIM,
        MATH_SOURCE,
        TRUE_CLAIM,
    )

    assert verify_claim(TRUE_CLAIM, MATH_SOURCE) is Verdict.CONFIRMED
    assert verify_claim(FALSE_CLAIM, MATH_SOURCE) is Verdict.CONTRADICTED
    assert verify_claim(AMBIGUOUS_CLAIM, MATH_SOURCE) is Verdict.CANNOT_VERIFY

    print(
        "OK: true claim CONFIRMED, false claim CONTRADICTED, "
        "ambiguous claim CANNOT_VERIFY (abstained)"
    )
