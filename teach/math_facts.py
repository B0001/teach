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


# "codomain" is the Dummit & Foote term, but a lesson (or a learner echoing
# one back) is not obliged to use it -- "target group"/"target" and "range
# of the {map,homomorphism,function}"/"range" are the ordinary synonyms for
# the same wrong group, and teach-8xw.25's reproduction is exactly this: the
# identical false claim phrased with "target group" and "range of the map"
# both slipped past a false_patterns set keyed to the literal word
# "codomain". Every codomain-shaped false_pattern below must use this
# alternation, not the bare word, or the same bug reopens at the next
# synonym.
_CODOMAIN_SYNONYMS = (
    r"(?:codomain"
    r"|target(?:\s+group)?"
    r"|range(?:\s+of\s+the\s+(?:map|homomorphism|function))?"
    r"|receiving\s+(?:group|end(?:\s+of\s+the\s+(?:map|homomorphism|function))?)"
    r"|output\s+group)"
)

_KERNEL_NORMAL_SUBGROUP = SourceFact(
    topic="kernel-normal-subgroup",
    citation="Dummit & Foote, Abstract Algebra, 3rd ed., section 3.2, Proposition 7",
    topic_patterns=(
        # kernels? -- \bkernel\b alone never matches inside "kernels" because
        # no word boundary sits between "l" and "s"; a true claim phrased in
        # the plural was falling all the way through to CANNOT_VERIFY.
        re.compile(r"(?=.*\bkernels?\b)(?=.*\bnormal\b)", re.IGNORECASE | re.DOTALL),
        re.compile(
            rf"(?=.*\bimage\b)(?=.*\bnormal\b)(?=.*{_CODOMAIN_SYNONYMS}\b)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    false_patterns=(
        # Direct negation: "not (necessarily) a normal subgroup".
        re.compile(r"\bkernels?\b.{0,80}\bnot\b.{0,40}\bnormal\b", re.IGNORECASE | re.DOTALL),
        # Wrong target group: the kernel lives in the domain, not the codomain
        # (or any of its ordinary synonyms -- see _CODOMAIN_SYNONYMS above).
        re.compile(
            rf"\bkernels?\b.{{0,80}}\bnormal\b.{{0,60}}{_CODOMAIN_SYNONYMS}\b",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            rf"\bkernels?\b.{{0,80}}{_CODOMAIN_SYNONYMS}\b.{{0,60}}\bnormal\b",
            re.IGNORECASE | re.DOTALL,
        ),
        # A different, false-in-general claim: the image is normal in the codomain.
        re.compile(
            rf"\bimage\b.{{0,80}}\bnormal\b.{{0,60}}{_CODOMAIN_SYNONYMS}\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    # This used to be "kernel ... is/are ... normal" with NO constraint on
    # which group -- so any claim not caught by false_patterns' enumerated
    # synonym list defaulted to CONFIRMED. That default is exactly backwards
    # per sandbox-prompt.md's "prefer abstention to a confident answer": a
    # blind round of independently-authored paraphrases (teach-8xw.25) found
    # false claims naming the wrong group structurally -- "a normal subgroup
    # that lives where the arrows point to", "H is the group being mapped
    # into, [and] the kernel is simply one of H's normal subgroups" -- that
    # no false_patterns synonym list will ever fully enumerate (open-ended
    # English, the same ceiling documented for teach/potential_checker.py's
    # lineage). Rather than keep chasing synonyms, true_patterns now only
    # confirms when the claim explicitly names the domain -- anything else
    # (unqualified, or naming some other/ambiguous group) abstains instead
    # of guessing confirmed. This trades recall on rare unqualified-true
    # phrasing for eliminating the dangerous direction on unenumerated wrong-
    # group phrasing.
    true_patterns=(
        re.compile(
            r"\bkernels?\b.{0,80}\b(?:is|are)\b.{0,40}\bnormal\b.{0,60}\bdomain\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
)

# teach-8xw.33's finding: a blind round-1 of 12 independently-authored
# paraphrases of the reversed/false Lagrange claim -- using "cardinality",
# "size", "goes into", "is a multiple of", and a container/contained
# metaphor instead of the literal "order"/"divides"/"group"/"subgroup"
# wording above -- measured 0/12 caught. Landing on CANNOT_VERIFY was the
# safe direction (true_patterns' exact-phrase requirement meant no reversed
# paraphrase was ever wrongly CONFIRMED), but it's still a real recall gap,
# so -- same move as _CODOMAIN_SYNONYMS above -- these widen false_patterns'
# vocabulary. true_patterns is deliberately NOT widened the same way: per
# the kernel topic's precedent, false-catching is safe to broaden
# aggressively (worst case is an extra CANNOT_VERIFY->CONTRADICTED that was
# already a false claim), but confirming is kept narrow on purpose so a
# loose synonym match never manufactures a false CONFIRMED.
#
# Round-1 and a round-2 (referenced piecemeal above: the "every"-quantifier
# gap, "must be a factor of") were both spent TUNING this widening in the
# same session that wrote it, so neither is evidence the fix generalizes --
# per sandbox-prompt.md's rule that a generalization set authored in the
# same session as the rule is not held out, whatever it's labelled. A third,
# genuinely fresh blind round (12 more independently-authored paraphrases,
# generated by an Agent call with no repository access, after this widening
# was already committed) is the actual held-out measurement:
#
#   1/12 CONTRADICTED, 11/12 CANNOT_VERIFY, 0/12 CONFIRMED.
#
# Real, if modest, improvement over the original 0/12 -- and critically the
# safe-direction property still holds under fresh paraphrase (0/12
# dangerous, same as round 1). The 11 misses split further: 7/12 don't even
# trip topic_patterns (verb-phrase metaphors like "has to split evenly
# into", "slot into", "swallows ... evenly", "absorbs ... cleanly" -- no
# recognized size- or divisibility-word at all), and the other 4 trip
# topic_patterns but no false_pattern. Both are the same open-ended-English
# ceiling already documented and accepted for the kernel topic's
# unenumerable wrong-group phrasing above -- not a bug, a disclosed limit.
# Deliberately NOT chased further here: doing so would just widen again
# against round-3 (making it tuning data too) and require yet another fresh
# round to know if *that* generalizes -- the same infinite regress this
# comment exists to avoid. One round-3 catch and two round-3 misses are
# locked into tests/test_fact_checker.py as regression evidence for both
# halves of this measurement.
_SIZE_SYNONYMS = r"(?:order|cardinality|size|count)"

# A bare determiner list ("the"/"a"/"any") missed quantifiers like "every"
# subgroup / "each" subgroup / "all" subgroups -- teach-8xw.33's second blind
# round (round 2, used to tune this fix) found a sentence using "every"
# that fell through the literal false_pattern below straight to the loose
# `lagrange...divides` true_pattern, landing the DANGEROUS false-CONFIRMED
# verdict this repo's whole checker design exists to avoid, not just the
# disclosed-safe CANNOT_VERIFY this bead was filed for. Any determiner list
# used to recognize a structure phrase needs every ordinary English
# quantifier, not just the three that happened to be in the first example.
#
# teach-8xw.34's finding: this quantifier list still missed possessive
# determiners ("its subgroups", "their subgroups") and the compound
# quantifier+possessive form ("any of its subgroups"). Unlike the round-2
# "every" gap, this one was dangerous, not just a recall gap: the reversed
# claim "the order of the group divides the order of its subgroups" slipped
# past every false_pattern (none of which recognized "its") straight through
# to true_patterns' loose `lagrange...divides` fallback and landed the
# dangerous false-CONFIRMED verdict this whole checker design exists to
# prevent. Built as (quantifier [of possessive])? | possessive rather than
# enumerating "any of its"/"any of their"/"each of its"/... as separate
# alternatives, so a new quantifier added to the first group automatically
# gets the possessive-compound form too.
#
# Per this repo's working rule, self-authored examples from the same
# session that wrote the fix are not evidence it generalizes. A held-out
# round -- 12 fresh reversed-Lagrange paraphrases from a no-repo-access
# Agent call, steered specifically at possessive/determiner-adjacent
# phrasing -- measured 3/12 CONTRADICTED, 9/12 CANNOT_VERIFY, 0/12
# CONFIRMED after this fix landed. The safety property (no dangerous
# false-CONFIRMED) held on every sentence; the 9 misses are the same
# open-ended-English ceiling already disclosed elsewhere in this file (verb
# phrases and symbolic notation the synonym lists don't cover), not a
# recurrence of the possessive-determiner gap this fix targeted. One catch
# and one miss from this round are locked into tests/test_fact_checker.py.
_POSSESSIVE_DETERMINER = r"(?:its|their)"
_ANY_DETERMINER = (
    rf"(?:(?:the|a|any|every|each|all)\s+(?:of\s+{_POSSESSIVE_DETERMINER}\s+)?"
    rf"|{_POSSESSIVE_DETERMINER}\s+)?"
)

_BIG_ADJ = r"(?:whole|entire|big|bigger|larger|large|outer|ambient|parent|enclosing|finite)"
_SMALL_ADJ = r"(?:small|smaller|little|child|inner|enclosed)"

_BIG_STRUCTURE_SYNONYMS = rf"(?:(?:{_BIG_ADJ}\s+)?(?:groups?|containers?|boxes?))"

_SMALL_STRUCTURE_SYNONYMS = (
    rf"(?:(?:{_SMALL_ADJ}\s+)?(?:subgroups?|boxes?)"
    r"|contained (?:groups?|structures?|sets?)"
    r"|things?(?:\s+that)? it contains"
    r"|what it contains)"
)

# "goes into"/"fits into" and "a factor/divisor of" are ordinary-English
# synonyms for "divides" that keep the same grammatical direction (A divides
# B / A goes into B / A fits into B / A is a factor of B all put the smaller
# quantity first). The verb before "a factor/divisor of" ("is", "must be",
# "will always be", ...) is deliberately not anchored -- round 2 found
# "must be a factor of" -- so only the noun phrase itself is matched.
_DIVIDES_SYNONYMS = (
    r"(?:divides|go(?:es)?\s+into|fits?\s+(?:evenly\s+)?into|(?:a\s+)?(?:divisor|factor)\s+of)"
)

# "is a multiple of" states the identical relation with the operands
# swapped (B is a multiple of A <=> A divides B), so it needs its own
# patterns rather than folding into _DIVIDES_SYNONYMS above.
_MULTIPLE_OF_SYNONYMS = r"(?:(?:is\s+)?an?(?:\s+integer)? multiple of)"


def _size_phrase(structure: str) -> str:
    """Any of three grammatical forms for naming a structure's size:
    "order of the group", "the group's order", or "number of elements in
    the group" (each with the cardinality/size/count synonyms, and every
    ordinary-English quantifier, not just "the/a/any")."""
    return (
        rf"(?:{_SIZE_SYNONYMS}s? of {_ANY_DETERMINER}{structure}"
        rf"|{_ANY_DETERMINER}{structure}'?s?\s+{_SIZE_SYNONYMS}s?"
        rf"|number of elements (?:in|of) {_ANY_DETERMINER}{structure})"
    )


_BIG_SIZE = _size_phrase(_BIG_STRUCTURE_SYNONYMS)
_SMALL_SIZE = _size_phrase(_SMALL_STRUCTURE_SYNONYMS)


_LAGRANGE_ORDER_DIVIDES = SourceFact(
    topic="lagrange-order-divides",
    citation="Dummit & Foote, Abstract Algebra, 3rd ed., section 3.2, Theorem 8 (Lagrange's Theorem)",
    topic_patterns=(
        re.compile(r"\blagrange\b", re.IGNORECASE),
        re.compile(
            r"(?=.*\border\b)(?=.*\bsubgroup\b)(?=.*\bdivid)", re.IGNORECASE | re.DOTALL
        ),
        # Synonym-vocabulary aboutness gate: a sentence naming a size word,
        # a big-or-small structure word, and a divisibility relation (in any
        # order) is about this topic even without the literal "order" /
        # "subgroup" / "divid-" words above.
        re.compile(
            rf"(?=.*\b{_SIZE_SYNONYMS}\b)"
            rf"(?=.*\b(?:{_BIG_STRUCTURE_SYNONYMS}|{_SMALL_STRUCTURE_SYNONYMS})\b)"
            rf"(?=.*(?:\b{_DIVIDES_SYNONYMS}\b|{_MULTIPLE_OF_SYNONYMS}))",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    false_patterns=(
        # Direct negation.
        re.compile(
            r"\border\b.{0,60}\bsubgroup\b.{0,60}\b(?:does not|doesn't|need not|neen't)\b.{0,40}\bdivide",
            re.IGNORECASE | re.DOTALL,
        ),
        # Reversed direction: order of the *group* dividing order of the
        # *subgroup*. Routed through _ANY_DETERMINER (rather than its own
        # competing "the|a|any" list) so it inherits every quantifier and
        # possessive form _ANY_DETERMINER recognizes -- teach-8xw.34 found
        # this pattern's own inline list didn't cover "its"/"any of its",
        # letting a reversed possessive claim slip through to the loose
        # true_patterns fallback below and land a false CONFIRMED.
        re.compile(
            rf"\border of {_ANY_DETERMINER}(?:finite )?groups?\b.{{0,60}}\bdivides\b.{{0,60}}"
            rf"\border of {_ANY_DETERMINER}subgroups?\b",
            re.IGNORECASE | re.DOTALL,
        ),
        # Same reversed direction, synonym vocabulary: big-structure's size
        # divides small-structure's size (either grammatical form of "size").
        re.compile(
            rf"{_BIG_SIZE}\b.{{0,80}}\b{_DIVIDES_SYNONYMS}\b.{{0,100}}{_SMALL_SIZE}",
            re.IGNORECASE | re.DOTALL,
        ),
        # Same reversed direction stated with "multiple of": small's size is
        # a multiple of big's size (subgroup's size a multiple of the
        # group's -- backwards; the true relation is the other way).
        re.compile(
            rf"{_SMALL_SIZE}\b.{{0,80}}{_MULTIPLE_OF_SYNONYMS}\b.{{0,100}}{_BIG_SIZE}",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    true_patterns=(
        re.compile(
            rf"\border of {_ANY_DETERMINER}subgroups?\b.{{0,60}}\bdivides\b.{{0,60}}"
            rf"\border of {_ANY_DETERMINER}(?:finite )?groups?\b",
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
