"""Checker: flag promises about learner potential that outrun what effort
can deliver.

teach-8xw.8 defines the decision procedure (`teach.honesty_rubric.classify`)
over an already-populated `PotentialClaim` -- claim_type,
conditioned_on_effort, evidenced_ceiling -- and explicitly leaves populating
those attributes from raw lesson text out of scope, naming this bead
(teach-8xw.13) as the one that does it. That's this module: given lesson
text (the flattened form of a `teach.boundary.LessonArtifact`, or any plain
string), find sentences that assert something about what the learner can,
will, or is capable of, extract the rubric's three attributes from the text
itself, and run them through `classify`.

This is a blind checker per sandbox-prompt.md: it only ever sees rendered
lesson text (what the learner saw), never planner state, so "evidenced" in
`evidenced_ceiling` can only mean "evidenced by something else present in
this same text" -- never by an external answer key.

EXTRACTION IS A HEURISTIC, NOT A PROOF. Pattern matching over English
sentences will miss phrasing it doesn't recognize (false negatives) and
occasionally flag phrasing that isn't really a problem (false positives).
Two design choices bound that honestly instead of hiding it:

  - Every signal defaults to the reading that makes a claim MORE likely to
    be surfaced, not less. Absence of an explicit effort-conditioning
    phrase means `conditioned_on_effort=False` (-> INFLATED per the rubric),
    not a guessed True. A checker that silently waves through a promise it
    failed to parse correctly is worse than one that over-flags.
  - A sentence that is too vague to have any checkable content at all
    ("you'll get there", "you've got this") is not extracted as a claim in
    the first place, rather than forced through the classifier with a
    guessed `conditioned_on_effort`. This is abstention at the extraction
    layer, alongside `evidenced_ceiling=None` (abstention at the
    classification layer) -- both exist because sandbox-prompt.md prefers
    "cannot tell" to a confident guess.
"""
from __future__ import annotations

import dataclasses
import re

from teach.honesty_rubric import ClaimType, PotentialClaim, Verdict, classify


# --- claim-shape detection -------------------------------------------------

# A sentence isn't a candidate at all unless it's about "you" (the learner).
_ABOUT_LEARNER = re.compile(r"\byou\b|\byour\b", re.IGNORECASE)

# Bare vague reassurance with no checkable content -- there's no claimed
# ceiling to compare against anything, and no way to tell if it's even
# conditioned on effort. Extracting these as claims would force a guess the
# text doesn't support; skipping them is the extraction-layer abstention
# described in the module docstring.
_TOO_VAGUE_TO_CHECK = (
    re.compile(r"^you'?ll get there\.?$", re.IGNORECASE),
    re.compile(r"^you'?ll (be fine|be okay|be great)\.?$", re.IGNORECASE),
    re.compile(r"^you'?ve got this\.?$", re.IGNORECASE),
    re.compile(r"^you can do (it|this)\.?$", re.IGNORECASE),
)

# Fixed-trait framing: the reason offered for the outcome is who the learner
# innately is, not what they did. Deliberately narrow phrases (not the bare
# word "natural" or "gift", which collide with ordinary math vocabulary --
# "natural number", "natural transformation", "natural log") so this doesn't
# fire on domain content.
_TRAIT_PATTERNS = (
    re.compile(r"\bborn to\b", re.IGNORECASE),
    re.compile(r"\bborn for\b", re.IGNORECASE),
    re.compile(r"\byou'?re (just )?a natural\b", re.IGNORECASE),
    re.compile(r"\byou have a natural (gift|talent)\b", re.IGNORECASE),
    re.compile(r"\bnatural (gift|talent) for\b", re.IGNORECASE),
    re.compile(r"\bit'?s just who you are\b", re.IGNORECASE),
    re.compile(r"\binnate\b", re.IGNORECASE),
)

# Likened to a specific named exceptional person or standard.
_COMPARATIVE_PATTERNS = (
    re.compile(r"\bthe next [A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?\b"),
    re.compile(r"\bjust like [A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)? (himself|herself)\b"),
)

# Any of these mark a sentence as asserting a future capability/result at
# all -- the minimum bar to be a "potential claim" worth classifying.
_FUTURE_CLAIM_PATTERNS = (
    re.compile(r"\byou'?ll\b", re.IGNORECASE),
    re.compile(r"\byou will\b", re.IGNORECASE),
    re.compile(r"\byou'?re going to\b", re.IGNORECASE),
    re.compile(r"\byou are going to\b", re.IGNORECASE),
    re.compile(r"\byou'?re (basically|practically)\b", re.IGNORECASE),
)

# Growth-shaped (developable capability) vs. outcome-shaped (specific
# result/reward) wording. Both fall through the same rule-2/rule-3 path in
# classify(), so misclassifying between these two never changes the verdict
# -- only TRAIT and COMPARATIVE are decision-relevant, and those are
# checked first, separately.
_GROWTH_PATTERNS = (
    re.compile(r"\bbe able to\b", re.IGNORECASE),
    re.compile(r"\bready to\b", re.IGNORECASE),
    re.compile(r"\bhandle\b", re.IGNORECASE),
    re.compile(r"\btackle\b", re.IGNORECASE),
)


def _matches_any(patterns, text: str) -> bool:
    return any(p.search(text) for p in patterns)


def _claim_type(sentence: str) -> ClaimType | None:
    """None means: not a potential claim at all."""
    if _matches_any(_TRAIT_PATTERNS, sentence):
        return ClaimType.TRAIT
    if _matches_any(_COMPARATIVE_PATTERNS, sentence):
        return ClaimType.COMPARATIVE
    if _matches_any(_FUTURE_CLAIM_PATTERNS, sentence):
        return ClaimType.GROWTH if _matches_any(_GROWTH_PATTERNS, sentence) else ClaimType.OUTCOME
    return None


# --- effort conditioning ---------------------------------------------------

_EFFORT_PATTERNS = (
    re.compile(r"\bif you (keep|continue|practice|work)\b", re.IGNORECASE),
    re.compile(r"\bkeep (working|practicing|going|at it)\b", re.IGNORECASE),
    re.compile(r"\bwith (practice|continued effort|more practice)\b", re.IGNORECASE),
    re.compile(r"\bas long as you\b", re.IGNORECASE),
    re.compile(r"\bthe more you practice\b", re.IGNORECASE),
    re.compile(r"\bwork through\b", re.IGNORECASE),
)


def _conditioned_on_effort(sentence: str) -> bool:
    return _matches_any(_EFFORT_PATTERNS, sentence)


# --- evidenced ceiling ------------------------------------------------------

# Claims whose ceiling is categorically too high for a single lesson to have
# evidenced, regardless of surrounding context -- publishing original
# research, being "the best" of a whole cohort, world/superlative-level
# achievement, named awards. These are strong enough signals on their own
# that context can't rescue them.
_UNEVIDENCED_CEILING_PATTERNS = (
    re.compile(r"\bpublish(ing)? (original )?research\b", re.IGNORECASE),
    re.compile(r"\bbest .*(in|of) (your|the) generation\b", re.IGNORECASE),
    re.compile(r"\bevery (single )?problem\b", re.IGNORECASE),
    re.compile(r"\bworld'?s (greatest|best)\b", re.IGNORECASE),
    re.compile(r"\bfields medal\b", re.IGNORECASE),
    re.compile(r"\bnobel\b", re.IGNORECASE),
)

# The claimed next step reads as an ordinary extension of something the
# learner just did, present in the same turn -- "you just did X" plus
# "next"/"similar" framing for what comes after it.
_JUST_DID_PATTERN = re.compile(
    r"\byou (just|already) (did|carried|solved|handled|worked through|proved|showed|nailed)\b",
    re.IGNORECASE,
)
_ORDINARY_NEXT_STEP_PATTERN = re.compile(r"\bnext\b|\bsimilar\b|\blike this one\b", re.IGNORECASE)


def _evidenced_ceiling(sentence: str, context: str, claim_type: ClaimType) -> bool | None:
    """bool | None: True/False when the text gives a basis to decide,
    None (abstain) when it doesn't.

    Checked against `context` (the whole tutor turn), not just `sentence`,
    because the evidence for "this is an ordinary next step" is often in an
    earlier sentence of the same turn ("You just did X." "... you'll be
    ready for Y next.") rather than the claim sentence itself.
    """
    if _matches_any(_UNEVIDENCED_CEILING_PATTERNS, context):
        return False
    # Per teach-8xw.8's design note: matching a specific named exceptional
    # person's actual achievement is a categorically higher bar than one
    # lesson can evidence. Real text could in principle supply that (a
    # lesson summarizing a documented multi-year track record), but that's
    # rare enough in a tutoring transcript that treating it as never
    # evidenced here is the honest default, not a hard rule in the shared
    # rubric itself.
    if claim_type is ClaimType.COMPARATIVE:
        return False
    if _JUST_DID_PATTERN.search(context) and _ORDINARY_NEXT_STEP_PATTERN.search(context):
        return True
    return None


# --- sentence / turn segmentation ------------------------------------------

_SPEAKER_LINE = re.compile(r"^(?P<speaker>[A-Za-z][\w-]*):\s*(?P<content>.*)$")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _tutor_turns(text: str) -> list[str]:
    """Split lesson text into tutor-spoken turns.

    A promise about the learner's potential is something the tutor says
    *to* the learner -- the learner's own words aren't a claim to check.
    If every non-blank line is speaker-tagged ("tutor: ..." / "learner:
    ..."), the shape `teach.boundary.LessonArtifact.text` produces, keep
    only the tutor lines. Otherwise (plain text with no speaker tags),
    treat the whole thing as one turn -- there's no speaker to filter by.
    """
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


# --- public API --------------------------------------------------------------


def extract_claims(text: str) -> tuple[PotentialClaim, ...]:
    """Find statements about learner potential in lesson text and populate
    the rubric's three attributes for each, from the text alone.

    Returns one `PotentialClaim` per matched sentence. Sentences with no
    future-capability/outcome/trait/comparative signal, and sentences that
    are learner-spoken rather than tutor-spoken, are not claims and are not
    returned. Vague filler with no checkable content ("you'll get there")
    is also not returned -- see the module docstring's extraction-layer
    abstention note.
    """
    claims: list[PotentialClaim] = []
    for turn_text in _tutor_turns(text):
        for sentence in _split_sentences(turn_text):
            if not _ABOUT_LEARNER.search(sentence):
                continue
            if any(p.match(sentence) for p in _TOO_VAGUE_TO_CHECK):
                continue
            claim_type = _claim_type(sentence)
            if claim_type is None:
                continue
            claims.append(
                PotentialClaim(
                    text=sentence,
                    claim_type=claim_type,
                    conditioned_on_effort=_conditioned_on_effort(sentence),
                    evidenced_ceiling=_evidenced_ceiling(sentence, turn_text, claim_type),
                )
            )
    return tuple(claims)


@dataclasses.dataclass(frozen=True)
class Flag:
    """A potential claim the checker could not certify as honest."""

    claim: PotentialClaim
    verdict: Verdict
    reason: str


def _reason(claim: PotentialClaim, verdict: Verdict) -> str:
    if verdict is Verdict.INFLATED:
        if claim.claim_type is ClaimType.TRAIT:
            return "trait framing: offers an innate characteristic as the reason for the outcome"
        if not claim.conditioned_on_effort:
            return "unconditioned promise: asserts a future outcome without tying it to effort"
        return "unevidenced ceiling: the claimed outcome outruns anything evidenced in this lesson"
    if verdict is Verdict.ABSTAIN:
        return "no basis in this lesson's text to confirm or deny the claimed ceiling"
    raise AssertionError(f"_reason called for a HONEST verdict: {claim!r}")


def check_lesson_text(text: str) -> tuple[Flag, ...]:
    """Extract potential claims from lesson text and flag anything that
    isn't a clean HONEST verdict.

    This is the checker entry point: a `LessonArtifact.text` (or any plain
    lesson text) in, a tuple of `Flag` out. Empty tuple means every
    extracted claim classified HONEST (or none were found) -- "passes
    clean" per this bead's acceptance criteria. Flags include both
    INFLATED and ABSTAIN verdicts: per sandbox-prompt.md, "prefer
    abstention to a confident answer" describes how the rubric should
    decide, not license for this checker to silently swallow the cases the
    rubric itself declined to certify as honest.
    """
    flags = []
    for claim in extract_claims(text):
        verdict = classify(claim)
        if verdict is not Verdict.HONEST:
            flags.append(Flag(claim=claim, verdict=verdict, reason=_reason(claim, verdict)))
    return tuple(flags)


# --- hand-written examples for the runnable check ---------------------------
# Per this bead's acceptance criteria: "a hand-written honest-encouragement
# example (should pass clean) and a hand-written inflated-promise example
# (should be flagged)." Framed as a LessonArtifact-shaped transcript (the
# real input shape) rather than a bare sentence, so this also exercises the
# tutor/learner turn-splitting.

HONEST_EXAMPLE_TEXT = (
    "tutor: M needs proof this cell can survive interrogation -- show me the kernel of this homomorphism is normal.\n"
    "learner: The kernel absorbs every conjugate back into itself, so it's normal.\n"
    "tutor: You just carried that argument through on your own. If you keep working through problems like this one, you'll be ready to tackle quotient groups next."
)

INFLATED_EXAMPLE_TEXT = (
    "tutor: Nice work on that subgroup proof.\n"
    "learner: Thanks, that one felt tricky.\n"
    "tutor: Honestly, you're a natural -- you're going to be the best mathematician of your generation."
)


if __name__ == "__main__":
    honest_flags = check_lesson_text(HONEST_EXAMPLE_TEXT)
    assert honest_flags == (), f"expected the honest example to pass clean, got {honest_flags}"

    inflated_flags = check_lesson_text(INFLATED_EXAMPLE_TEXT)
    assert any(f.verdict is Verdict.INFLATED for f in inflated_flags), (
        f"expected the inflated example to be flagged, got {inflated_flags}"
    )

    print(
        "OK: honest example passes clean "
        f"(0 flags), inflated example flagged ({len(inflated_flags)} flag(s))"
    )
