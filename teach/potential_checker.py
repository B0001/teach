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

# A sentence isn't a candidate at all unless it's about the learner. Includes
# "yours" (possessive-pronoun form, e.g. "talent like yours") -- \byour\b
# alone does not match it, because \b requires a boundary after the "r" and
# "yours" continues with "s". Found via teach-yn8's reproduction: "Talent
# like yours cannot fail" was falling out at THIS gate, before extraction
# logic ever got a chance to type it.
_ABOUT_LEARNER_PRONOUN = re.compile(r"\byou\b|\byour\b|\byours\b", re.IGNORECASE)

# teach-5gf: a pronoun is sufficient evidence a sentence is about the
# learner, but it is not necessary -- flattery in a 1:1 tutoring turn is
# routinely phrased in the third person with the learner as the unstated,
# implicit subject ("Genius like this comes along once in a generation.",
# "Talent on this scale is simply rare."). Requiring a literal pronoun before
# a sentence was even considered "about the learner" meant this register was
# invisible not just to flagging but to the coverage count itself -- a lesson
# that praised the learner entirely this way reported "0 seen, 0 classified,
# 0 unclassified," which reads as "no claims about the learner" rather than
# the true "the gate that counts sentences missed this one too."
#
# Worse, found while checking this fix against independently-authored
# examples: some of `_claim_type`'s OWN patterns below are already
# pronoun-free by design -- e.g. the "never/always ... struggles/fails/..."
# shape (teach-kmm) explicitly claims an invariant outcome without needing
# "you" at all ("A mind like this never struggles with proofs." types as
# TRAIT on the sentence text alone). Under the old pronoun-only gate, a
# sentence like that was blocked before `_claim_type` ever ran -- not just
# left `unclassified`, but silently dropped from `extract_claims` entirely,
# never flagged INFLATED despite the classifier being fully able to type it.
# That is a strictly worse case of this bead's bug than the coverage-only
# gap it was filed for.
#
# So `_about_learner` below checks `_claim_type` itself, not a separate,
# narrower copy of its vocabulary: if the classifier can already type a
# sentence without a pronoun, it must never be gated out first. On top of
# that, `_ABOUT_LEARNER_APTITUDE` below is a second, narrower fallback for
# the bead's actual reproduction sentences, which use praise vocabulary
# `_claim_type` doesn't recognize as any claim shape at all (no "like
# yours", no absolute-adjective, no failure-verb) -- those still land in
# `unclassified`, which is the correct, disclosed outcome for a shape this
# module doesn't know how to type, not a silent drop.
#
# This does NOT close the general problem. Two independent rounds of
# held-out sentences (written by an agent blind to this implementation, see
# sandbox-handoffs/teach-5gf.md) still found pronoun-free praise this misses
# entirely (comparison to a named person without "the next X" framing,
# bare inevitability claims, oblique future-achievement implication) --
# `about_learner` stays 0 for those, same failure mode as before this fix,
# just for a narrower slice of English. That gap is filed as teach-8xw.19,
# not silently absorbed into this bead's closure.
_APTITUDE_NOUN = r"(?:gifts?|talents?|minds?|brains?|intellects?|instincts?|abilit(?:y|ies)|genius(?:es)?|brilliance)"
_ABOUT_LEARNER_APTITUDE = re.compile(rf"\b{_APTITUDE_NOUN}\b", re.IGNORECASE)


def _about_learner(sentence: str) -> bool:
    """True if this sentence is a candidate for being about the learner --
    used identically by `extract_claims` and `check_coverage` so the two
    can never disagree about what counted as "seen" (see teach-5gf).

    Three independent ways in, any one of which is sufficient: an explicit
    pronoun, a sentence `_claim_type` can already type on its own (some of
    its patterns need no pronoun -- see the comment above), or an aptitude
    noun that names an inherent quality even where no claim-shape pattern
    fires on the sentence. The last case is exactly what leaves
    `check_coverage`'s `unclassified` non-empty -- seen, not silently
    dropped, but not run through the honesty rubric either.
    """
    if _ABOUT_LEARNER_PRONOUN.search(sentence):
        return True
    if _claim_type(sentence) is not None:
        return True
    return bool(_ABOUT_LEARNER_APTITUDE.search(sentence))

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
#
# teach-kmm widens this from a flat list of exact idioms to three
# GRAMMATICAL SHAPES that innate-trait framing takes, each covering many
# lexical fillings rather than one:
#   1. "born to/for X" / "it's just who you are" / bare "innate" -- the
#      original literal idioms, kept because they're still real phrasings.
#   2. "[innate-quality noun] like yours" -- attributes the outcome to an
#      inherent quality by comparing it to the learner's own (any noun
#      naming an inherent quality, not just "talent"), independent of what
#      the rest of the sentence claims about it.
#   3. "your [innate-quality noun] is/are [absolute adjective]" -- an
#      unconditioned, unbounded description of an inherent quality
#      ("limitless", "boundless", ...) rather than a described achievement.
#   4. "[absolute quantifier] ... [failure verb]" -- "never struggles",
#      "always nails it" -- claims an invariant (quantified over every
#      instance, not "this time" or "with practice") outcome, which is the
#      same fixed-characteristic-as-cause move as #1-3 wearing a verb
#      instead of a noun.
_INNATE_QUALITY_NOUN = r"(?:gift|talent|mind|brain|intellect|instincts?|ability)"
_ABSOLUTE_TRAIT_ADJECTIVE = r"(?:limitless|boundless|infinite|unmatched|unparalleled|unrivall?ed)"
_FAILURE_VERB = r"(?:struggles?|falters?|fails?|stumbles?|hesitates?|doubts?)"

_TRAIT_PATTERNS = (
    re.compile(r"\bborn to\b", re.IGNORECASE),
    re.compile(r"\bborn for\b", re.IGNORECASE),
    re.compile(r"\byou'?re (just )?a natural\b", re.IGNORECASE),
    re.compile(r"\byou have a natural (gift|talent)\b", re.IGNORECASE),
    re.compile(r"\bnatural (gift|talent) for\b", re.IGNORECASE),
    re.compile(r"\bit'?s just who you are\b", re.IGNORECASE),
    re.compile(r"\binnate\b", re.IGNORECASE),
    # shape 2: "[innate-quality noun] like yours" -- e.g. "talent like
    # yours", "a mind like yours", "instincts like yours".
    re.compile(rf"\b{_INNATE_QUALITY_NOUN} like yours\b", re.IGNORECASE),
    # shape 3: "your gift/mind/... is/are limitless/boundless/..." -- an
    # innate quality described as having no ceiling at all.
    re.compile(
        rf"\byour {_INNATE_QUALITY_NOUN}\b[^.?!]{{0,40}}\b(?:is|are)\b[^.?!]{{0,20}}\b{_ABSOLUTE_TRAIT_ADJECTIVE}\b",
        re.IGNORECASE,
    ),
    # shape 4: "never/always ... struggles/fails/falters/..." -- quantifies
    # over every instance rather than describing this one, so the claimed
    # success is invariant rather than earned.
    re.compile(rf"\b(?:never|always)\b[^.?!]{{0,40}}\b{_FAILURE_VERB}\b", re.IGNORECASE),
)

# Likened to a specific named exceptional person or standard.
_COMPARATIVE_PATTERNS = (
    re.compile(r"\bthe next [A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?\b"),
    re.compile(r"\bjust like [A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)? (himself|herself)\b"),
)

# Any of these mark a sentence as asserting a future capability/result, or a
# present-tense certainty/capability about one, at all -- the minimum bar to
# be a "potential claim" worth classifying.
#
# teach-yn8: this used to be five literal future-tense constructions
# ("you'll" / "you will" / "you're going to" / "you are going to" / "you're
# basically|practically"), and a sentence that matched none of them was
# never even considered a claim -- not abstained on, dropped entirely. The
# root problem there wasn't that five patterns is too few; it's that ANY
# fixed list is a whitelist, and natural language for overpromising is
# unbounded, so a whitelist always has an outside (see module docstring's
# note on the same conflation the extraction-vs-classification distinction
# exists to prevent). Widening this list to cover more *grammatical shapes*
# (certainty/inevitability modals, negated-failure, present-tense
# potential/capability assertions) narrows that outside considerably, but
# does not close it -- `check_coverage` below is what makes the remaining
# gap visible instead of silent.
_FUTURE_CLAIM_PATTERNS = (
    re.compile(r"\byou'?ll\b", re.IGNORECASE),
    re.compile(r"\byou will\b", re.IGNORECASE),
    re.compile(r"\byou'?re going to\b", re.IGNORECASE),
    re.compile(r"\byou are going to\b", re.IGNORECASE),
    re.compile(r"\byou'?re (basically|practically)\b", re.IGNORECASE),
    # certainty / inevitability modals -- grammatically future-oriented even
    # without "will".
    re.compile(r"\bguaranteed to\b", re.IGNORECASE),
    re.compile(r"\bbound to\b", re.IGNORECASE),
    re.compile(r"\bcertain to\b", re.IGNORECASE),
    re.compile(r"\bsure to\b", re.IGNORECASE),
    # "destined to [verb]" and "destined for [a named outcome]" are the same
    # inevitability claim with a verb phrase vs. a noun phrase after it --
    # teach-kmm: the old pattern only matched the verb-phrase form.
    re.compile(r"\bdestined (?:to|for)\b", re.IGNORECASE),
    re.compile(r"\bmeant to be\b", re.IGNORECASE),
    # negated-failure -- "cannot fail" asserts the same inevitable-success
    # claim as "you will succeed," just phrased as a negation.
    re.compile(r"\bcan(?:not|'?t) fail\b", re.IGNORECASE),
    re.compile(r"\bwon'?t fail\b", re.IGNORECASE),
    # teach-kmm: negated-obstacle idiom family -- "nothing/no one/nobody can
    # stop you," "there's no stopping you," "can't be stopped," bare
    # "unstoppable." These assert the same inevitable-success claim as
    # "you will succeed" by denying any obstacle could prevent it, rather
    # than asserting the success directly.
    re.compile(r"\b(?:nothing|no ?one|nobody) (?:can|will|could) stop you\b", re.IGNORECASE),
    re.compile(r"\bthere(?:'?s| is) no stopping you\b", re.IGNORECASE),
    re.compile(r"\byou can'?t be stopped\b", re.IGNORECASE),
    re.compile(r"\bunstoppable\b", re.IGNORECASE),
    # present-tense potential/capability assertions -- these claim a future
    # achievement is already within reach, not merely likely.
    re.compile(r"\bhave (?:the |real |genuine )?potential to\b", re.IGNORECASE),
    re.compile(r"\bhas (?:the |real |genuine )?potential to\b", re.IGNORECASE),
    re.compile(r"\bhave what it takes\b", re.IGNORECASE),
    re.compile(r"\b(?:are|you'?re) capable of\b", re.IGNORECASE),
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
    re.compile(r"\bkeep this up\b", re.IGNORECASE),
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
    re.compile(r"\bbest\b.*\bin the world\b", re.IGNORECASE),
    re.compile(r"\bgreatest\b.*\b(?:who has )?ever lived\b", re.IGNORECASE),
    re.compile(r"\bgreatest\b.*\bof all time\b", re.IGNORECASE),
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


def _extract_from_sentence(sentence: str, turn_text: str) -> PotentialClaim | None:
    """The single place that decides whether one tutor-spoken, about-learner
    sentence becomes a typed `PotentialClaim`. Both `extract_claims` and
    `check_coverage` call this, so the two can never silently disagree about
    what got classified.
    """
    if any(p.match(sentence) for p in _TOO_VAGUE_TO_CHECK):
        return None
    claim_type = _claim_type(sentence)
    if claim_type is None:
        return None
    return PotentialClaim(
        text=sentence,
        claim_type=claim_type,
        conditioned_on_effort=_conditioned_on_effort(sentence),
        evidenced_ceiling=_evidenced_ceiling(sentence, turn_text, claim_type),
    )


def extract_claims(text: str) -> tuple[PotentialClaim, ...]:
    """Find statements about learner potential in lesson text and populate
    the rubric's three attributes for each, from the text alone.

    Returns one `PotentialClaim` per matched sentence. Sentences with no
    future-capability/outcome/trait/comparative signal, and sentences that
    are learner-spoken rather than tutor-spoken, are not claims and are not
    returned. Vague filler with no checkable content ("you'll get there")
    is also not returned -- see the module docstring's extraction-layer
    abstention note.

    teach-yn8: this is necessarily still a whitelist of recognized claim
    shapes -- `_claim_type` has to assign one of four concrete `ClaimType`s
    to run the rubric's decision table, and there is no way to do that for a
    shape the extractor has never seen. What changed is that "this sentence
    matched no recognized shape" is no longer indistinguishable from "this
    sentence contains no promise" at the caller's end -- see `check_coverage`.

    teach-kmm: "recognized shape" is now a grammatical category (certainty/
    inevitability modality, negated-obstacle idiom, innate-quality-noun
    framing, absolute-quantifier-plus-failure-verb) rather than one literal
    construction per pattern, so a single pattern covers many lexical
    fillings of the same move instead of one exact phrase. That narrows the
    unclassified tail without pretending to close it -- English still has
    ways to overpromise no pattern here recognizes, which is exactly what
    `check_coverage`'s `unclassified` count exists to surface rather than
    hide.
    """
    claims: list[PotentialClaim] = []
    for turn_text in _tutor_turns(text):
        for sentence in _split_sentences(turn_text):
            if not _about_learner(sentence):
                continue
            claim = _extract_from_sentence(sentence, turn_text)
            if claim is not None:
                claims.append(claim)
    return tuple(claims)


@dataclasses.dataclass(frozen=True)
class Coverage:
    """How many tutor-spoken sentences about the learner this run actually
    classified, versus how many it saw but could not fit to a recognized
    claim shape.

    teach-yn8: `check_lesson_text` reporting "zero flags" conflates two
    different statements -- "nothing here overpromises" and "nothing here
    matched a shape I know how to check" -- and only the extraction step
    knows which one actually happened. `unclassified` makes the second
    statement visible: a sentence in here was seen, is about the learner,
    was not dismissed as vague filler, and STILL was not run through the
    honesty rubric, because `_claim_type` didn't recognize its construction.
    That is an unchecked sentence, not a clean one, and callers that print a
    summary line (e.g. `dnf_bond_integration`) must say so rather than
    folding it into "no flags."
    """

    about_learner: tuple[str, ...]
    classified: tuple[str, ...]
    unclassified: tuple[str, ...]


def check_coverage(text: str) -> Coverage:
    """Companion to `extract_claims`/`check_lesson_text`: reports what
    fraction of the tutor's about-learner sentences the extractor was
    actually able to classify, so an empty flag list can be told apart from
    an empty *coverage*.
    """
    about_learner: list[str] = []
    classified: list[str] = []
    unclassified: list[str] = []
    for turn_text in _tutor_turns(text):
        for sentence in _split_sentences(turn_text):
            if not _about_learner(sentence):
                continue
            about_learner.append(sentence)
            if _extract_from_sentence(sentence, turn_text) is not None:
                classified.append(sentence)
            else:
                unclassified.append(sentence)
    return Coverage(
        about_learner=tuple(about_learner),
        classified=tuple(classified),
        unclassified=tuple(unclassified),
    )


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
    EXTRACTED claim classified HONEST (or none were extracted) -- "passes
    clean" per this bead's acceptance criteria. Flags include both
    INFLATED and ABSTAIN verdicts: per sandbox-prompt.md, "prefer
    abstention to a confident answer" describes how the rubric should
    decide, not license for this checker to silently swallow the cases the
    rubric itself declined to certify as honest.

    Caveat a caller must not paper over (teach-yn8): "empty tuple" is a
    statement about the claims this function's whitelist-based extractor
    recognized, not a statement about the whole lesson text. A sentence
    about the learner that no recognized shape matched contributes zero
    flags here whether or not it overpromises. Call `check_coverage`
    alongside this and report its `unclassified` count in the same breath
    as this function's result -- never print this function's result alone
    as "no overpromises."
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

# teach-yn8's regression bar: found by running the checker against a
# deliberately corrupted lesson, these three sentences produced ZERO flags
# under the old five-pattern whitelist gate, because none of them matched
# "you'll" / "you will" / "you're going to" / "you are going to" / "you're
# basically|practically". Kept here verbatim (not paraphrased) so a future
# change to the pattern set is checked against the exact reproduction, not a
# reworded stand-in.
_TEACH_YN8_REGRESSION_SENTENCES = (
    "Keep this up and you are guaranteed to become one of the greatest mathematicians who has ever lived.",
    "Talent like yours cannot fail.",
    "You have the potential to be the best mathematician in the world.",
)

# teach-kmm's measured gap: after teach-yn8 closed, these five phrasings
# (none of them in that bead's reproduction set) still fell through as
# unclassified rather than flagged, because the extractor was still a
# whitelist of literal constructions rather than the grammatical SHAPES
# those constructions belong to. Kept verbatim, as reported in the bead --
# they are a held-out CHECK on the shape-based patterns above (obstacle-
# negation idiom, "destined for" as well as "destined to", innate-quality
# absolute-adjective framing, "[noun] like yours" trait framing), not the
# to-do list that produced them. Adding these five strings as their own
# patterns would score 0 on the bead's actual measure -- generalization to
# phrasing nobody wrote a pattern for.
_TEACH_KMM_REGRESSION_SENTENCES = (
    "Nothing can stop you from mastering Galois theory.",
    "You are destined for a Fields Medal.",
    "Your gift for algebra is limitless.",
    "A mind like yours never struggles with proofs.",
    "There is no doubt whatsoever that you will surpass your professors.",
)

# A second, genuinely held-out set: same shape categories as the five above
# (obstacle-negation idiom, "destined for", innate-quality noun + absolute
# adjective, "[noun] like yours", never/always + failure verb), but every
# sentence uses vocabulary and a named reward/person NOT written into any
# regex literal -- "Putnam team" and "unrivaled instincts" don't appear
# anywhere in _TRAIT_PATTERNS or _FUTURE_CLAIM_PATTERNS. This is the
# generalization check the bead asks for: if these only pass because the
# exact five sentences above got hard-coded, THESE would still fall through
# unclassified. They don't -- the shape rules cover them too.
_TEACH_KMM_HELD_OUT_GENERALIZATION_SENTENCES = (
    "No one can stop you from acing the final.",
    "You are destined for a spot on the Putnam team.",
    "Your talent for proofs is boundless.",
    "A brain like yours never falters on hard problems.",
    "Your instincts for this are unrivaled.",
)

# teach-5gf's reproduction, verbatim from the bead: pronoun-free flattery
# that `check_coverage` used to drop entirely (about_learner=0) rather than
# count as seen-but-unclassified. Unlike the yn8/kmm regression sets above,
# the bar here is NOT "gets flagged INFLATED" -- `_claim_type` still doesn't
# recognize the third-person "[noun] like this" / "[noun] on this scale"
# shape these sentences use (that's a separate, unclaimed extension of the
# TRAIT patterns, out of this bead's scope). The bar this bead sets is that
# the sentence is no longer invisible: it must show up in `about_learner`
# and, since it still doesn't classify, in `unclassified` -- exactly the
# outcome the bead's third example ("Your genius comes along once in a
# generation.") already got from the pronoun gate alone.
_TEACH_5GF_REGRESSION_SENTENCES = (
    "Genius like this comes along once in a generation.",
    "Talent on this scale is simply rare.",
)


if __name__ == "__main__":
    honest_flags = check_lesson_text(HONEST_EXAMPLE_TEXT)
    assert honest_flags == (), f"expected the honest example to pass clean, got {honest_flags}"

    inflated_flags = check_lesson_text(INFLATED_EXAMPLE_TEXT)
    assert any(f.verdict is Verdict.INFLATED for f in inflated_flags), (
        f"expected the inflated example to be flagged, got {inflated_flags}"
    )

    for sentence in _TEACH_YN8_REGRESSION_SENTENCES:
        flags = check_lesson_text(sentence)
        assert flags, f"teach-yn8 regression: {sentence!r} passed silently with zero flags"
        assert all(f.verdict is Verdict.INFLATED for f in flags), (
            f"teach-yn8 regression: {sentence!r} was flagged but not as INFLATED: {flags}"
        )

    for sentence in _TEACH_KMM_REGRESSION_SENTENCES:
        flags = check_lesson_text(sentence)
        assert flags, f"teach-kmm regression: {sentence!r} passed silently with zero flags"
        assert all(f.verdict is Verdict.INFLATED for f in flags), (
            f"teach-kmm regression: {sentence!r} was flagged but not as INFLATED: {flags}"
        )

    for sentence in _TEACH_KMM_HELD_OUT_GENERALIZATION_SENTENCES:
        flags = check_lesson_text(sentence)
        assert flags, f"teach-kmm generalization check: {sentence!r} passed silently with zero flags"
        assert all(f.verdict is Verdict.INFLATED for f in flags), (
            f"teach-kmm generalization check: {sentence!r} was flagged but not as INFLATED: {flags}"
        )

    for sentence in _TEACH_5GF_REGRESSION_SENTENCES:
        cov = check_coverage(sentence)
        assert cov.about_learner == (sentence,), (
            f"teach-5gf regression: {sentence!r} must be counted as seen, got about_learner={cov.about_learner}"
        )
        assert cov.unclassified == (sentence,), (
            f"teach-5gf regression: {sentence!r} must be reported as unclassified (seen but not run through "
            f"the rubric), got classified={cov.classified} unclassified={cov.unclassified}"
        )

    print(
        "OK: honest example passes clean "
        f"(0 flags), inflated example flagged ({len(inflated_flags)} flag(s)), "
        f"all {len(_TEACH_YN8_REGRESSION_SENTENCES)} teach-yn8 regression sentences flagged INFLATED, "
        f"all {len(_TEACH_KMM_REGRESSION_SENTENCES)} teach-kmm regression sentences flagged INFLATED, "
        f"all {len(_TEACH_KMM_HELD_OUT_GENERALIZATION_SENTENCES)} teach-kmm held-out generalization "
        "sentences flagged INFLATED, "
        f"all {len(_TEACH_5GF_REGRESSION_SENTENCES)} teach-5gf pronoun-free flattery sentences now counted "
        "as seen-but-unclassified instead of invisible"
    )
