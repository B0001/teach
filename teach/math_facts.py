"""Math domain's reference source for teach.fact_checker.

Per-domain plugin data, per the boundary teach-8xw.4 decided and
teach.fact_checker reserved: nothing here is imported by fact_checker.py,
and nothing in fact_checker.py branches on `domain == "math"`. This module
is what makes the generic engine concrete for the repo's stated test case
(Dummit & Foote abstract algebra).

Each `SourceFact` is one theorem/definition from Dummit & Foote, 3rd
edition, verified against the actual textbook statement (not recalled from
memory of "what group theory generally says") -- per sandbox-prompt.md's
rule that a lookup deciding a factual question must be checked against the
raw source, this citation is the specific theorem number a real learner
could turn to and check by hand:

  - kernel-normal-subgroup: Dummit & Foote §3.2, Proposition 7 -- the
    kernel of a group homomorphism is a normal subgroup of the domain.
    (NOT of the codomain -- the kernel is a subset of the domain by
    definition, so "normal subgroup of the codomain" is not merely
    unproven, it's a category error. NOT the same claim as "the image is
    normal in the codomain," which is false in general -- e.g. the
    inclusion Z/2 -> S_3 has image {e, (12)}, not normal in S_3.)
  - lagrange-order-divides: Dummit & Foote §3.2, Theorem 8 (Lagrange's
    Theorem) -- if G is a finite group and H <= G, then |H| divides |G|.
    The converse is famously false (A_4 has order 12 with no subgroup of
    order 6), but this fact only covers the forward direction stated by
    the actual theorem; a converse-shaped claim is a different topic this
    source does not adjudicate (CANNOT_VERIFY), not a false claim about
    this fact.

Pattern design note: true/false patterns key off the direction of the
relationship (which quantity divides which; which group the subgroup is
normal in), not just topic keywords, because the false claims worth
catching are exactly the ones a learner is likely to actually make --
swapping a direction -- not nonsense sentences a keyword match would
already reject as off-topic.
"""
from __future__ import annotations

import dataclasses
import re

from teach.fact_checker import SourceFact


_KERNEL_NORMAL_SUBGROUP = SourceFact(
    topic="kernel-normal-subgroup",
    citation="Dummit & Foote, Abstract Algebra, 3rd ed., section 3.2, Proposition 7",
    topic_patterns=(
        re.compile(r"(?=.*\bkernel\b)(?=.*\bnormal\b)", re.IGNORECASE | re.DOTALL),
        re.compile(
            r"(?=.*\bimage\b)(?=.*\bnormal\b)(?=.*\bcodomain\b)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    false_patterns=(
        # Direct negation: "not (necessarily) a normal subgroup".
        re.compile(r"\bkernel\b.{0,80}\bnot\b.{0,40}\bnormal\b", re.IGNORECASE | re.DOTALL),
        # Wrong target group: the kernel lives in the domain, not the codomain.
        re.compile(
            r"\bkernel\b.{0,80}\bnormal\b.{0,60}\bcodomain\b", re.IGNORECASE | re.DOTALL
        ),
        re.compile(
            r"\bkernel\b.{0,80}\bcodomain\b.{0,60}\bnormal\b", re.IGNORECASE | re.DOTALL
        ),
        # A different, false-in-general claim: the image is normal in the codomain.
        re.compile(
            r"\bimage\b.{0,80}\bnormal\b.{0,60}\bcodomain\b", re.IGNORECASE | re.DOTALL
        ),
    ),
    true_patterns=(
        re.compile(
            r"\bkernel\b.{0,80}\b(?:is|are)\b.{0,40}\bnormal\b", re.IGNORECASE | re.DOTALL
        ),
    ),
)

_LAGRANGE_ORDER_DIVIDES = SourceFact(
    topic="lagrange-order-divides",
    citation="Dummit & Foote, Abstract Algebra, 3rd ed., section 3.2, Theorem 8 (Lagrange's Theorem)",
    topic_patterns=(
        re.compile(r"\blagrange\b", re.IGNORECASE),
        re.compile(
            r"(?=.*\border\b)(?=.*\bsubgroup\b)(?=.*\bdivid)", re.IGNORECASE | re.DOTALL
        ),
    ),
    false_patterns=(
        # Direct negation.
        re.compile(
            r"\border\b.{0,60}\bsubgroup\b.{0,60}\b(?:does not|doesn't|need not|neen't)\b.{0,40}\bdivide",
            re.IGNORECASE | re.DOTALL,
        ),
        # Reversed direction: order of the *group* dividing order of the *subgroup*.
        re.compile(
            r"\border of (?:the |a |any )?(?:finite )?group\b.{0,60}\bdivides\b.{0,60}"
            r"\border of (?:the |a |any )?subgroup\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    true_patterns=(
        re.compile(
            r"\border of (?:the |a |any )?subgroup\b.{0,60}\bdivides\b.{0,60}"
            r"\border of (?:the |a |any )?(?:finite )?group\b",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(r"\blagrange\b.{0,120}\bdivides\b", re.IGNORECASE | re.DOTALL),
    ),
)


@dataclasses.dataclass(frozen=True)
class MathSource:
    """Implements teach.fact_checker.SourceAdapter for the math domain."""

    domain: str = "math"
    facts: tuple[SourceFact, ...] = (
        _KERNEL_NORMAL_SUBGROUP,
        _LAGRANGE_ORDER_DIVIDES,
    )


MATH_SOURCE = MathSource()


# --- hand-written examples for the runnable check ---------------------------
# Per this bead's acceptance criteria: "a hand-written true claim, a
# hand-written false claim, and an ambiguous claim that should abstain."
# Framed as tutor-spoken sentences (plain strings work too -- fact_checker's
# verify_claim takes a bare claim string, not a LessonArtifact).

TRUE_CLAIM = "The kernel of a homomorphism is always a normal subgroup of the domain."

FALSE_CLAIM = "The kernel of a homomorphism is a normal subgroup of the codomain."

# Mentions the kernel and normal subgroups in the same breath -- the topic
# this source covers -- but asserts nothing checkable: no "is"/"is not"
# relating them, just a vague gesture at a connection. Recognized topic,
# unclear assertion -- exactly the CANNOT_VERIFY case this bead's
# acceptance criteria distinguishes from "topic not covered at all."
AMBIGUOUS_CLAIM = "The kernel has some kind of relationship to normal subgroups."


if __name__ == "__main__":
    from teach.fact_checker import Verdict, verify_claim

    assert verify_claim(TRUE_CLAIM, MATH_SOURCE) is Verdict.CONFIRMED
    assert verify_claim(FALSE_CLAIM, MATH_SOURCE) is Verdict.CONTRADICTED
    assert verify_claim(AMBIGUOUS_CLAIM, MATH_SOURCE) is Verdict.CANNOT_VERIFY
    print("OK: math source's 3 hand-written examples verify as expected")
