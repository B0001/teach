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

WHAT "EVIDENCED" CANNOT MEAN, AND THE ONE NARROW THING IT CAN (teach-8xw.45)

A lesson can say "you just solved 10 problems in a row" whether or not the
learner did -- self-consistency (does a later ceiling-claim match an
earlier performance-claim in the SAME text) is strictly weaker than
truthfulness (did the earlier performance-claim itself really happen), and
nothing in this module can close that gap in general. Confirming a
performance claim's content actually occurred would require exactly the
producer-side ground truth (planner state, an answer key, a transcript the
learner didn't see) the blind-checker boundary forbids this module from
reading. That limitation is fundamental, not a to-do.

One narrow cross-reference IS available without crossing the boundary,
because it stays entirely inside the same transcript: `_JUST_DID_PATTERN`
("you just carried/solved/handled/...") asserts the LEARNER acted a moment
ago, and this transcript's own turn order either has a learner turn
adjacent to that claim or it doesn't. `_tutor_turns_with_precedent` /
`_evidenced_ceiling` use exactly that -- when no learner turn immediately
precedes a "you just did X" claim, the transcript itself contradicts the
claim's premise, and `evidenced_ceiling` reports `False` rather than the
`True` a text-only pattern match would have handed out. This caught real
cases, not a hypothetical one: `teach.dnf_bond_lesson`'s closing line ("You
just carried that coset argument through to Lagrange's Theorem on your
own") follows eight consecutive tutor-only turns with no learner
contribution about cosets or Lagrange anywhere in them, and
`teach.cialdini_integration_check`'s demo lesson renders all seven
Cialdini moves as consecutive tutor turns with the one learner turn
appended only at the end -- see `tests/test_dnf_bond_integration.py`,
`tests/test_cialdini_integration_check.py`, and
`sandbox-handoffs/teach-8xw.45.md` for the reproductions, and teach-8xw.51
for the follow-up bead fixing those two producers.

This is still a narrow, structural check, not a truthfulness oracle. Two
things it explicitly does NOT catch, so a caller never mistakes silence
here for a clean bill of health:

  - When a learner turn IS adjacent, this module has no way to confirm
    that turn's *content* actually is the claimed action -- only that the
    turn-taking shape is consistent with it. "Learner speaks, tutor
    immediately claims a match to whatever the learner just said" always
    reads as evidenced here, whether or not the match is real.
  - Performance disguised as the learner's own work -- the producer
    solving the problem within a tutor turn and then crediting the
    learner for it -- has a learner turn nowhere in sight to check against
    at all, and looks identical to ordinary tutor narration.
"""
from __future__ import annotations

import dataclasses
import re

from teach.honesty_rubric import ClaimType, PotentialClaim, Verdict, classify


# --- claim-shape detection -------------------------------------------------

# teach-yn8 gated candidacy on five literal future-tense strings; teach-kmm
# widened that to grammatical shapes; teach-5gf found the gate applied a
# SECOND time, one level up, as a "does this sentence even count as being
# about the learner" pre-filter (pronoun-or-aptitude-noun) that had to run
# before a sentence was even considered for classification. Each widening
# fixed its own reproduction and was checked against held-out sentences a
# fresh agent wrote -- and each time, a next round of independently-phrased
# praise (comparison to a named person with no "next X" framing, bare
# inevitability with no modal, oblique future-achievement implication,
# guarantee-of-outcome with no "guaranteed to", bare superlatives) fell
# through the same hole again. teach-8xw.19 measured this directly: the
# aptitude-noun fallback caught 5/8 held-out sentences in one round and
# 1/6 in a second round that avoided its vocabulary on purpose. A vocabulary
# whitelist for "is this about the learner" cannot converge -- praise that
# implies the learner as an unstated third-person subject is not a bounded
# set of nouns, and every fix in this lineage was disproven by the next
# round of phrasing nobody happened to write a pattern for.
#
# teach-8xw.19's fix is not a fourth widening. There is no more "about the
# learner" pre-filter: every tutor-spoken sentence (see `_tutor_turns`) is a
# coverage candidate, full stop. This cannot silently drop a sentence,
# because there is no gate left to fail. Two things make this safe rather
# than just noisier:
#
#   1. `extract_claims`'s actual output is UNCHANGED by removing the gate.
#      The old gate was engineered to be a superset of what `_claim_type`
#      can classify (pronoun OR `_claim_type(sentence) is not None` OR
#      aptitude noun) specifically so a classifiable sentence could never be
#      blocked before classification ran. Any sentence `_claim_type` types
#      already passed the old gate, so `extract_claims` (which only ever
#      returns typed claims) returns exactly the same claims either way.
#      Nothing that used to flag stops flagging, and nothing new starts
#      flagging just because the gate is gone.
#   2. What changes is `check_coverage`: every tutor sentence a real lesson
#      contains -- ordinary domain content and procedural remarks included,
#      not just learner-directed praise -- now shows up as `seen`, and
#      lands in `unclassified` unless `_claim_type` recognizes it. That is
#      the noisier-but-honest trade the bead names as the alternative to
#      another vocabulary round: `about_learner` is no longer a claim that
#      the heuristic identified learner-directed content (a claim that kept
#      turning out to be false), it is a plain count of what the tutor said,
#      with disclosure of how much of that this module can actually type
#      pushed entirely onto `unclassified` -- which was already the
#      module's designated place for "seen but not certified either way."
#
# This is why the field below is `seen`, not `about_learner`: the old name
# asserted a filter this module can no longer honestly claim to perform.
#
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

# teach-8xw.23: pure flattery with no checkable claim shape still produced
# zero flags because these five shapes -- all present in the bead's own
# reproduction (turn B) -- weren't typed by anything above. Each is a
# distinct move, not a paraphrase of an existing pattern:
#   - "built/made/wired for this" -- the same fixed-trait-as-cause move as
#     "born to/for", spelled with a different verb.
#   - "few [people-noun] ever ... like yours" -- rarity offered as evidence
#     of an innate exceptional quality, rather than of anything the learner
#     did.
#   - "nothing about your [X] is ordinary" -- innate exceptionality stated
#     by negating the mundane, rather than asserting the extraordinary
#     directly.
# Kept narrow (bounded noun/verb lists, not bare "natural"/"gift") for the
# same reason the original shapes were: collision with ordinary domain
# vocabulary ("natural number") and with A-shaped benign second-person
# address (see `_TEACH_8XW_23_BENIGN_SECOND_PERSON_TURN` below) is the
# failure mode a widening must not trade into.
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
    # teach-8xw.23 shape 5: "built/made/wired for this|it" -- inherent-
    # capacity framing, the same move as "born to/for" with a different verb.
    re.compile(r"\b(?:built|made|wired) for (?:this|it)\b", re.IGNORECASE),
    # teach-8xw.23 shape 6: "few students/people/... ever ... like yours" --
    # rarity-as-praise: the outcome is explained by how few others could
    # match it, not by what the learner did.
    re.compile(r"\bfew (?:students?|people|learners?|others?)\b[^.?!]{0,60}\blike yours\b", re.IGNORECASE),
    # teach-8xw.23 shape 7: "nothing about your [X] is ordinary" --
    # negated-ordinariness: exceptionality asserted by ruling out the
    # mundane rather than describing the extraordinary directly.
    re.compile(r"\bnothing about (?:your|you)\b[^.?!]{0,60}\bis ordinary\b", re.IGNORECASE),
    # teach-8xw.50 shape 8: bare aptitude/instinct possession with NO
    # comparative marker ("like yours") and no "natural" qualifier -- just a
    # flat "you have/have got a(n) [innate-quality noun]" declarative. Two
    # variants because natural phrasing splits here: an intensifying
    # adjective (real/genuine/true/good/great/such) makes the noun read as
    # trait-praise even with no object at all ("you have good instincts");
    # without an intensifier, an explicit "for X" object is what marks it as
    # praise rather than a neutral capability reference ("you have the
    # ability to do this with practice" is ordinary effort-conditioned
    # growth phrasing on its own, and must not become TRAIT just because
    # "ability" is in the noun list).
    re.compile(
        rf"\byou(?:'ve|(?: (?:just|really|simply|definitely))? have) (?:got )?(?:a |an )?"
        rf"(?:real|genuine|true|good|great|such) {_INNATE_QUALITY_NOUN}\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\byou(?:'ve|(?: (?:just|really|simply|definitely))? have) (?:got )?(?:a |an )?"
        rf"{_INNATE_QUALITY_NOUN} for\b",
        re.IGNORECASE,
    ),
)

# Likened to a specific named exceptional person or standard.
#
# teach-8xw.23: the existing two idioms both require an explicit comparison
# marker ("the next X", "just like X himself") -- they miss a hypothetical
# endorsement from a named figure with no marker at all ("Einstein would
# have nodded at your reasoning"). `_NOT_A_NAME` excludes the common
# capitalized words that start a sentence without naming a person (bare
# pronouns, determiners), so this doesn't fire on "What would you like to
# try next?" or "Nobody would have guessed that."
_NOT_A_NAME = (
    r"Nobody|Anybody|Everybody|Someone|Anyone|Everyone|"
    r"Something|Nothing|Anything|Everything|"
    r"This|That|These|Those|It|They|We|You|I|What|Who|Which"
)
_COMPARATIVE_PATTERNS = (
    re.compile(r"\bthe next [A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?\b"),
    re.compile(r"\bjust like [A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)? (himself|herself)\b"),
    # teach-8xw.23 shape: "[Named person] would have nodded/been proud/..."
    # -- a hypothetical endorsement from a specific named exceptional
    # figure, with no "next X"/"just like X" marker required.
    re.compile(
        rf"\b(?!(?:{_NOT_A_NAME})\b)[A-Z][a-zA-Z]+ would (?:have \w+|be (?:proud|impressed|amazed))\b"
    ),
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
    # teach-8xw.23: bare inevitability with no modal at all -- "is not in
    # doubt" / "beyond doubt|question" assert the same certain-future-
    # success claim as "you will succeed," just phrased as ruling out
    # uncertainty rather than asserting the outcome.
    re.compile(r"\bnot in doubt\b", re.IGNORECASE),
    re.compile(r"\bbeyond (?:doubt|question)\b", re.IGNORECASE),
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


# --- second-person disclosure (teach-8xw.20) -------------------------------
#
# NOT a candidacy gate. teach-yn8/teach-kmm/teach-5gf spent three rounds
# widening a pronoun-anchored "is this about the learner" pre-filter and
# teach-8xw.19 removed it for good, because pronoun-free third-person praise
# ("Einstein would have nodded...") is real English and any gate built on
# this pattern makes exactly that praise invisible again. This regex must
# never be used to decide whether a sentence is extracted or counted in
# `seen` -- only to compute a secondary, reported-alongside-not-instead-of
# breakdown of `seen`/`classified`/`unclassified` (see `Coverage` below).
#
# Why this is worth reporting even though it can't see pronoun-free praise:
# `unclassified = len(seen) - len(classified)`, and in a lesson with the
# usual handful (0-2) of true potential-claims, `classified` is small and
# roughly constant, so `unclassified` is structurally pinned near
# `len(seen)` -- it moves in lockstep with how long the lesson is, not with
# how much of it is about the learner at all. `len(seen)` includes every
# tutor-spoken sentence: domain definitions, historical narration, plot
# scaffolding, none of which is a candidate for a potential-claim in the
# first place. A subset restricted to sentences carrying an explicit
# second-person address ("you"/"your"/"yours") is NOT pinned to `len(seen)`
# the same way: ordinary domain exposition ("A normal subgroup is one
# that's invariant under conjugation.") is almost always third-person by
# construction of the genre, so it contributes zero to this subset no
# matter how many such sentences the lesson has, while direct
# encouragement or procedural remarks to the learner almost always use
# "you." Rewriting the domain content of a lesson to be longer or shorter
# changes `len(seen)` without necessarily changing the size of this subset
# at all -- the two counts measure genuinely different properties of the
# text, which is what makes the second one informative where the first has
# become a near-constant.
#
# This does not solve pronoun-free third-person praise -- that content
# still shows up only in the ungated `seen`/`unclassified` totals, which
# remain the authoritative, un-narrowed disclosure. This subset is reported
# ALONGSIDE that total, never in place of it (see `Coverage`'s docstring).
_SECOND_PERSON_REFERENCE = re.compile(r"\byou\b|\byour\b|\byours\b", re.IGNORECASE)


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


def _evidenced_ceiling(
    sentence: str,
    context: str,
    claim_type: ClaimType,
    preceded_by_learner: bool | None,
) -> bool | None:
    """bool | None: True/False when the text gives a basis to decide,
    None (abstain) when it doesn't.

    Checked against `context` (the whole tutor turn), not just `sentence`,
    because the evidence for "this is an ordinary next step" is often in an
    earlier sentence of the same turn ("You just did X." "... you'll be
    ready for Y next.") rather than the claim sentence itself.

    teach-8xw.45: `_JUST_DID_PATTERN` matching `context` only proves the
    TUTOR *said* "you just did X" -- it cannot, on its own, distinguish a
    real demonstrated performance from a narrated one, which is exactly the
    gap teach-8xw.8's own design note flagged as a standing limitation
    ("this rubric can only ever verify internal consistency of a lesson...
    not whether the transcript's own claims of demonstrated performance are
    truthful"). `preceded_by_learner` (see `_tutor_turns_with_precedent`)
    is the one cross-reference available without crossing the producer/
    checker boundary: does THIS SAME transcript's own turn order show a
    learner turn immediately before the claim, for "just" to be referring
    to? `preceded_by_learner is False` means the transcript itself
    contradicts the claim's premise -- nothing the learner did appears
    adjacent to "you just did X" -- so this is treated as UNevidenced
    (`False`), not merely abstained on. This is a narrow, structural check,
    not a truthfulness oracle: it cannot confirm the learner turn (when one
    IS adjacent) actually contains the claimed action, only that the turn-
    taking shape is at least consistent with it, and it says nothing at all
    about performance disguised as the learner's own work (the producer
    solving it and attributing it to the learner) -- see this module's
    docstring for the disclosed scope of what this can and can't catch.
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
        if preceded_by_learner is False:
            return False
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


def _tutor_turns_with_precedent(text: str) -> list[tuple[str, bool | None]]:
    """Same split as `_tutor_turns`, paired with whether each tutor turn is
    IMMEDIATELY preceded, in the original transcript's own turn order, by a
    learner-spoken turn.

    This is teach-8xw.45's cross-reference signal: `_evidenced_ceiling`'s
    "you just did X" evidence (`_JUST_DID_PATTERN`) is a claim that the
    LEARNER performed some action a moment ago. A blind checker can never
    confirm the claimed action's *content* happened -- that would require
    the producer-side ground truth the boundary forbids -- but it can check
    whether this same transcript's own turn-taking has any learner turn at
    all adjacent to the claim for "just" to be referring to. If the
    immediately preceding turn is tutor-only, the transcript itself shows
    nothing the learner did there, independent of what the claim says.

    `None` (not `False`) when the text has no turn structure to check at
    all (see `_tutor_turns`'s own plain-text fallback) -- an unstructured
    string was never going to let this check run, and that absence of
    signal must not be conflated with the structured, turn-tagged case
    where a learner turn was checked for and genuinely wasn't there.
    """
    lines = [line for line in text.splitlines() if line.strip()]
    if not (lines and all(_SPEAKER_LINE.match(line) for line in lines)):
        return [(text, None)]
    parsed = [
        (m.group("speaker").lower(), m.group("content"))
        for line in lines
        if (m := _SPEAKER_LINE.match(line))
    ]
    return [
        (content, i > 0 and parsed[i - 1][0] == "learner")
        for i, (speaker, content) in enumerate(parsed)
        if speaker == "tutor"
    ]


def _split_sentences(turn_text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(turn_text.strip()) if s.strip()]


# --- public API --------------------------------------------------------------


def _extract_from_sentence(
    sentence: str, turn_text: str, preceded_by_learner: bool | None = None
) -> PotentialClaim | None:
    """The single place that decides whether one tutor-spoken, about-learner
    sentence becomes a typed `PotentialClaim`. Both `extract_claims` and
    `check_coverage` call this, so the two can never silently disagree about
    what got classified.

    `preceded_by_learner` (teach-8xw.45, see `_tutor_turns_with_precedent`):
    whether the tutor turn this sentence came from is immediately preceded,
    in the full transcript's own turn order, by a learner turn. Defaults to
    `None` (unknown/not checked) for direct callers (e.g. tests exercising
    a single sentence in isolation) that don't have turn-sequence context to
    offer -- see `_evidenced_ceiling`'s docstring for what this does and
    does not let it verify.
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
        evidenced_ceiling=_evidenced_ceiling(sentence, turn_text, claim_type, preceded_by_learner),
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

    teach-8xw.19: there used to be an "is this even about the learner"
    pre-filter here (`_about_learner`) before a sentence reached
    `_claim_type` at all. It is gone -- every tutor-spoken sentence reaches
    `_extract_from_sentence` now (see the comment above `_TOO_VAGUE_TO_CHECK`
    for why removing it changes nothing about which claims get extracted).
    """
    claims: list[PotentialClaim] = []
    for turn_text, preceded_by_learner in _tutor_turns_with_precedent(text):
        for sentence in _split_sentences(turn_text):
            claim = _extract_from_sentence(sentence, turn_text, preceded_by_learner)
            if claim is not None:
                claims.append(claim)
    return tuple(claims)


@dataclasses.dataclass(frozen=True)
class Coverage:
    """How many tutor-spoken sentences this run actually classified, versus
    how many it saw but could not fit to a recognized claim shape.

    teach-yn8: `check_lesson_text` reporting "zero flags" conflates two
    different statements -- "nothing here overpromises" and "nothing here
    matched a shape I know how to check" -- and only the extraction step
    knows which one actually happened. `unclassified` makes the second
    statement visible: a sentence in here was seen, was not dismissed as
    vague filler, and STILL was not run through the honesty rubric, because
    `_claim_type` didn't recognize its construction. That is an unchecked
    sentence, not a clean one, and callers that print a summary line (e.g.
    `dnf_bond_integration`) must say so rather than folding it into "no
    flags."

    teach-8xw.19: `seen` (formerly `about_learner`) is every tutor-spoken
    sentence, not a heuristically-filtered subset. Three rounds of trying to
    widen a vocabulary-based "is this about the learner" filter (teach-yn8,
    teach-kmm, teach-5gf) each found a next round of independently-phrased
    praise the filter still missed -- not `unclassified`, invisible,
    `about_learner=0`. Renaming the field is part of the fix: `about_learner`
    asserted the module had identified learner-directed content, which is
    exactly the claim that kept turning out false. `seen` makes no such
    claim -- it is a plain count of tutor sentences, with `unclassified`
    doing all of the honest-disclosure work.

    teach-8xw.20: removing that gate fixed the invisibility bug but created
    a new problem -- `unclassified` is `len(seen) - len(classified)`, and
    `classified` is small and roughly constant for any honestly-written
    lesson (0-2 true potential-claims), so `unclassified` is structurally
    pinned near `len(seen)` regardless of what the lesson actually says.
    Every lesson reports "~N-1 unclassified" and the figure stops carrying
    information a reviewer can act on.

    `second_person_seen`/`second_person_classified`/`second_person_unclassified`
    are the same three buckets restricted to sentences containing an
    explicit "you"/"your"/"yours" (see `_SECOND_PERSON_REFERENCE`) -- a
    SECONDARY, narrower view reported alongside the totals above, never
    replacing them. This is not another candidacy gate: nothing is extracted
    or excluded from `seen` based on it, it only re-slices numbers already
    computed. It is not a general solution either -- pronoun-free
    third-person praise (teach-8xw.19's own reproduction) is invisible to
    THIS subset by construction, exactly as it was to the old vocabulary
    gate. teach-8xw.32 found a second, distinct family with the same blind
    spot: group-generalization ("everyone who masters X goes on to...") and
    cited-authority ("mathematicians agree that...") claims never address the
    learner with a pronoun either, so they too are only ever visible in the
    full `seen`/`unclassified` totals, never in this narrower subset. What it
    buys is a count that isn't pinned to lesson length the way
    `unclassified` is: ordinary domain exposition is almost always
    third-person by genre convention, so it contributes nothing to this
    subset no matter how long the lesson runs, while direct address to the
    learner does. A caller must report both views, never one alone -- see
    `dnf_bond_integration.py`'s render().
    """

    seen: tuple[str, ...]
    classified: tuple[str, ...]
    unclassified: tuple[str, ...]
    second_person_seen: tuple[str, ...]
    second_person_classified: tuple[str, ...]
    second_person_unclassified: tuple[str, ...]


def check_coverage(text: str) -> Coverage:
    """Companion to `extract_claims`/`check_lesson_text`: reports what
    fraction of the tutor's sentences the extractor was actually able to
    classify, so an empty flag list can be told apart from an empty
    *coverage*.
    """
    seen: list[str] = []
    classified: list[str] = []
    unclassified: list[str] = []
    second_person_seen: list[str] = []
    second_person_classified: list[str] = []
    second_person_unclassified: list[str] = []
    for turn_text, preceded_by_learner in _tutor_turns_with_precedent(text):
        for sentence in _split_sentences(turn_text):
            seen.append(sentence)
            is_classified = _extract_from_sentence(sentence, turn_text, preceded_by_learner) is not None
            (classified if is_classified else unclassified).append(sentence)
            if _SECOND_PERSON_REFERENCE.search(sentence):
                second_person_seen.append(sentence)
                (second_person_classified if is_classified else second_person_unclassified).append(sentence)
    return Coverage(
        seen=tuple(seen),
        classified=tuple(classified),
        unclassified=tuple(unclassified),
        second_person_seen=tuple(second_person_seen),
        second_person_classified=tuple(second_person_classified),
        second_person_unclassified=tuple(second_person_unclassified),
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

# teach-8xw.45's own regression bar: two transcripts with the exact same
# "you just did X ... you'll be ready for Y next" claim text, differing only
# in whether a learner turn sits immediately before it. Kept side by side so
# a future change to `_tutor_turns_with_precedent`/`_evidenced_ceiling` is
# checked against a real minimal-pair reproduction, not just the full
# dnf_bond_lesson/cialdini_integration_check fixtures those functions were
# actually found and fixed against (see this module's own docstring and
# sandbox-handoffs/teach-8xw.45.md).
_TEACH_8XW_45_CLAIM_SENTENCE = (
    "You just carried that argument through on your own. If you keep "
    "working through problems like this one, you'll be ready to tackle "
    "quotient groups next."
)

_TEACH_8XW_45_LEARNER_TURN_ADJACENT_TEXT = (
    "tutor: Show me the kernel of this homomorphism is normal.\n"
    "learner: The kernel absorbs every conjugate back into itself, so it's normal.\n"
    f"tutor: {_TEACH_8XW_45_CLAIM_SENTENCE}"
)

_TEACH_8XW_45_NO_LEARNER_TURN_TEXT = (
    "tutor: Show me the kernel of this homomorphism is normal.\n"
    "tutor: A subgroup is normal exactly when every left coset equals the corresponding right coset.\n"
    f"tutor: {_TEACH_8XW_45_CLAIM_SENTENCE}"
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
# the sentence is no longer invisible: it must show up in `seen` (named
# `about_learner` at the time this bead was written; renamed by teach-8xw.19)
# and, since it still doesn't classify, in `unclassified` -- exactly the
# outcome the bead's third example ("Your genius comes along once in a
# generation.") already got from the pronoun gate alone.
_TEACH_5GF_REGRESSION_SENTENCES = (
    "Genius like this comes along once in a generation.",
    "Talent on this scale is simply rare.",
)

# teach-8xw.19's reproduction, verbatim from the bead (its three complete
# sentences -- the bead also quotes four more as trailing-ellipsis
# fragments, e.g. "...reminiscent of a young Feynman...", which aren't
# standalone sentences as written and so aren't reproduced here). These are
# exactly the phrasings that stayed invisible after teach-5gf's aptitude-noun
# widening: no pronoun, no aptitude noun, no shape `_claim_type` recognizes.
# The bar is the same as teach-5gf's -- seen and unclassified, not flagged
# INFLATED -- but the mechanism is different. teach-5gf closed its gap with
# a fourth vocabulary list; this bead's fix removes the vocabulary-gated
# pre-filter entirely, so there is no shape left for a fifth round of
# phrasing to slip past. These three sentences aren't a generalization test
# of a widened pattern (there is no pattern to generalize) -- they're proof
# that the specific reproduction this bead was filed against is now seen.
_TEACH_8XW_19_REGRESSION_SENTENCES = (
    "Einstein would have nodded approvingly at reasoning this sharp.",
    "Future textbooks might well cite work that starts exactly like this.",
    "Few students ever produce work this polished on a first attempt.",
)

# teach-8xw.20's structural proof that `second_person_seen` is not just
# `seen` wearing a smaller number -- two three-sentence, all-unclassified
# tutor turns, one entirely third-person (ordinary domain narration) and
# one entirely second-person (direct-address chit-chat, still no
# potential-claim shape in it), matched sentence-for-sentence in length and
# claim content. `len(seen)` and `len(unclassified)` come out identical for
# both (3 and 3) -- the exact near-constant this bead is about -- while
# `len(second_person_seen)` comes out 0 and 3. This is not a sampling claim
# ("I tried some lessons and the number varied"); it is a minimal
# constructed pair showing the two counts are driven by different textual
# properties (sentence count vs. second-person address), so the second
# cannot be a disguised copy of the first.
_TEACH_8XW_20_THIRD_PERSON_TURN = (
    "tutor: A normal subgroup is one that's invariant under conjugation.\n"
    "A homomorphism's kernel is always normal in its domain.\n"
    "The quotient group collects the cosets of that kernel into a single group."
)
_TEACH_8XW_20_SECOND_PERSON_TURN = (
    "tutor: Take a moment and tell me how you're feeling about this material.\n"
    "Is your pace here comfortable, or would you like to slow down?\n"
    "Let me know if you want to revisit anything before we move on."
)

# teach-8xw.23's own reproduction, verbatim from the bead. Turn A is benign
# second-person procedural address -- every sentence carries an explicit
# "you"/"your" but none is a potential-claim of any kind, so it must stay
# entirely unflagged; a widening that flags it has traded a false negative
# for a false positive. Turn B is pure flattery built entirely from the five
# shapes `_claim_type` could not type before this bead (inherent-capacity,
# rarity-as-praise, named-person comparison, bare inevitability,
# negated-ordinariness) -- before this bead's fix, `check_lesson_text(B) ==
# ()`, zero flags on a turn that is nothing but overpromise. Kept verbatim,
# as the bead's own literal reproduction, not a to-do list -- this is the
# floor this bead's fix must clear, not the measure of how far it
# generalizes (see the module docstring's note on why self-authored sets
# can't be that measure).
_TEACH_8XW_23_BENIGN_SECOND_PERSON_TURN = (
    "tutor: You just finished the coset argument. You wrote your proof "
    "clearly. Tell me how you are feeling about your progress. What would "
    "you like to try next? Your notes look organized."
)
_TEACH_8XW_23_PURE_FLATTERY_TURN = (
    "tutor: Your mind was built for this. Few students ever produce work "
    "like yours on a first attempt. Einstein would have nodded at your "
    "reasoning. Your future in mathematics is not in doubt. Nothing about "
    "your ability here is ordinary."
)

# teach-9k5: two independently-authored, blind-agent-generated held-out
# rounds (18 sentences total -- agents given no access to this repo or its
# patterns, asked only to write varied flattery in their own words, and for
# the second round explicitly steered away from the vocabulary teach-8xw.23
# had just added) measured this module's actual generalization after that
# fix: 0/18 typed by `_claim_type`. This is the fourth bead in the
# teach-yn8 -> teach-kmm -> teach-5gf -> teach-8xw.19 -> teach-8xw.23
# lineage to hit this same wall -- each vocabulary/shape widening closes its
# own literal reproduction and is disproven by the next independently-
# phrased round almost entirely.
#
# DECISION (teach-9k5, per its own stated closing condition (b)): no further
# regex/keyword widening is attempted against this measurement. A fifth
# round of "read the failing sentences, write patterns that match them"
# would repeat exactly the failure this lineage exists to document --
# patterns fitted to a known failing set are not evidence they generalize to
# the NEXT round, which is the only thing that has ever mattered here. This
# closes the bead the honest way it names as acceptable: the regex-based
# extractor has a real ceiling, and that ceiling is disclosed rather than
# hidden -- `check_coverage` puts every one of these 18 sentences in `seen`
# and `unclassified` (never silently dropped, never miscounted as
# `classified`), which is this module's designated place for "seen but not
# certified either way" (see `Coverage`'s docstring). A fundamentally
# different mechanism (POS-tagging/syntactic features over lexical
# alternation, per teach-kmm's original note) remains open future work, but
# proving it generalizes needs held-out evidence from an agent call that did
# not also write the mechanism -- out of reach for a single work session,
# per teach-9k5's own closing condition, and not attempted here.
#
# Kept verbatim as a permanent regression check that the DISCLOSURE stays
# honest even though the classifier's ceiling does not move: these must
# always land in seen+unclassified -- never silently invisible, and never a
# false negative dressed up as a clean lesson (zero flags).
_TEACH_9K5_DISCLOSED_CEILING_SENTENCES = (
    "You're clearly operating several levels above everyone else in this room.",
    "A mind like this comes along maybe once in a generation.",
    "Honestly, you just solved that the way a young Newton might have.",
    "There's an extraordinary intellect at work here, one most people spend a lifetime chasing.",
    "Something in the way this student sees problems marks them as exceptional, full stop.",
    "Your answer just now wasn't the product of study — it was simply who you are.",
    "It's rare to meet someone whose mind works this far ahead of the curve.",
    "This kind of understanding can't be taught; it was already there, waiting to be noticed.",
    "There's a version of Newton sitting in that answer.",
    "Some people just arrive already ahead of everyone else.",
    "It's rare to watch someone solve a problem like that without even trying.",
    "This is the kind of answer that shows up once in a classroom's lifetime.",
    "She reasons the way Curie must have — effortlessly, as if the answer were already there waiting.",
    "The rest of the class will spend years catching up to where he already stands.",
    "You're simply operating on a different level than everyone else in this room.",
    "Honestly, you remind me of a young Feynman before he even opened his mouth.",
    "What you just did in thirty seconds, most people never manage in a lifetime.",
    "There's no explaining it — you just see things other people can't.",
)

# teach-8xw.32: a DISTINCT shape family from teach-9k5's, not covered by its
# fixture set. teach-9k5's 18 sentences are all direct second-person praise
# of the individual learner ("you're...", "your mind...") -- pronoun-free by
# accident of phrasing in a few cases, but still about the learner as the
# subject. These four are structurally different: a claim about a COHORT the
# learner is implicitly a member of ("everyone who masters cosets...",
# "students who reach this point...") or a claim attributed to a third-party
# AUTHORITY ("mathematicians agree that..."), never naming or addressing the
# learner directly at all. `_claim_type` has no pattern for either shape, so
# all four land unclassified exactly like teach-9k5's set -- but because none
# contains "you"/"your"/"yours", ALL FOUR also miss `second_person_seen`
# entirely (0/4, not some fraction the way teach-9k5's mixed set does), so
# they are invisible to teach-8xw.20's short-list disclosure and visible only
# in the full seen/unclassified totals. That is the concrete, worse-than-
# teach-9k5 gap this bead measures and this fixture set locks in as disclosed.
#
# DECISION (teach-8xw.32, following teach-9k5's own precedent): closed via
# the bead's option (b), not (a). The bead's own reproduction sentences were
# written by whoever filed the bead, in the same lineage of sessions that
# maintains this module -- not held-out evidence from an agent call in a
# session that never saw this mechanism, which is what the bead's option (a)
# requires and which teach-9k5 already established is structurally
# unreachable from a single work session (see teach-9k5's own comment block
# and sandbox-handoffs/teach-9k5.md). Writing four regexes that match exactly
# these four sentences would score a self-congratulated 4/4 and prove nothing
# about the next independently-phrased round of cohort/authority claims --
# precisely the failure this repo's lineage (teach-yn8, teach-kmm, teach-5gf,
# teach-8xw.19, teach-8xw.23) has already repeated four times. No pattern
# list below is touched by this bead.
#
# Kept verbatim as a permanent regression check that the disclosure stays
# honest for this shape family too: these four sentences must always land in
# seen+unclassified (never silently invisible, never falsely flagged clean),
# AND must always be absent from second_person_seen (proving, rather than
# merely asserting, that this shape bypasses the short-list subset -- if a
# future change to `_SECOND_PERSON_REFERENCE` or `_claim_type` ever made that
# false, this test catches it).
_TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES = (
    "Everyone who masters cosets goes on to breeze through Lagrange Theorem.",
    "Mathematicians agree that a student who reasons like this is on track for real results.",
    "Students who reach this point almost always go on to master group theory with ease.",
    "Only a handful of students each year make it this far in the material.",
)

# teach-8xw.50: two more apparent overpromise shapes surfaced by hand-reading
# teach-8xw.44's own 25-sentence blind round -- neither is a paraphrase of
# anything above:
#
#   1. Bare aptitude/instinct possession with NO comparative marker ("like
#      yours") and no "natural" qualifier at all -- just "you have/have got
#      a(n) [innate-quality noun]", e.g. "you've got real instincts for
#      this." Every existing TRAIT shape requires either an idiom ("born
#      to/for", "innate"), a comparator ("[noun] like yours"), an absolute
#      adjective ("your gift is limitless"), or a quantified failure-verb
#      ("never struggles") -- a flat declarative possession claim matches
#      none of them.
#   2. Inevitable outcome implied via a concrete anecdote about one specific
#      named PEER ("You and Jamie both got stuck right here last month, and
#      look at her now -- she's flying through these.") -- not a named
#      exceptional historical figure (`_COMPARATIVE_PATTERNS`) and not an
#      abstract cohort (teach-8xw.32's "everyone/students who..." gap). No
#      pattern anywhere in this module types an anecdote structure at all.
#
# teach-8xw.50's fix, and the reason it's split into two different
# outcomes: shape 1 is a bounded, principled widening of the SAME
# grammatical family `_TRAIT_PATTERNS` already covers (bare possession of an
# `_INNATE_QUALITY_NOUN`, the version with neither "natural" nor a "like
# yours" comparator) -- see the two new patterns appended to
# `_TRAIT_PATTERNS` above. Shape 2 is a narrative anecdote structure (an
# arbitrary struggle description, an arbitrary success description, and an
# arbitrary way of introducing a named third party, in unbounded
# combination) -- structurally the same kind of unbounded-vocabulary problem
# that plateaued at 0/18 in teach-9k5 and that teach-9k5's own closing
# decision says not to re-attempt with another regex list. No pattern for
# shape 2 is added here.
#
# Per this bead's own explicit instruction, closing on the original two
# reproduction sentences alone (or worse, two regexes fitted only to them)
# would repeat exactly the failure this repo's teach-yn8 -> ... ->
# teach-8xw.32 lineage exists to document. So shape 1's fix was designed
# from the reproduction sentence plus the module's EXISTING noun list (not
# from reading the round below), then measured -- once, without further
# tuning -- against a genuinely independent, blind round: one `Agent` call,
# `subagent_type: general-purpose`, zero tool use (confirmed in the spawn
# result), given no access to this repo, asked to write 30 tutor lines
# split into the two shapes above (15 aiming for bare-aptitude praise, 15
# aiming for named-peer anecdotes) with instructions to vary wording heavily
# and not reuse "natural". The agent's own mix drifted from an even 15/15
# (it produced a few generic pep-talk lines that are neither shape, and a
# few borderline ease-framing lines with no explicit aptitude noun) -- kept
# honestly as delivered, not re-sorted or trimmed to a cleaner split.
#
# MEASURED RESULT, shape 1 (11 sentences unambiguously bare-aptitude-noun
# praise, no comparator, no named peer): 4/11 classified, of which only 2
# are attributable to THIS bead's new patterns ("you have good instincts
# here", "you just have a mind for this kind of thing") -- the other 2
# ("wired for this stuff", "built for this kind of thinking") were already
# caught by teach-8xw.23's pre-existing "built/made/wired for" pattern, not
# by anything added here. The remaining 7/11 stay unclassified: bare nouns
# outside this module's list ("a feel for this," "a knack for," "a real
# head for"), a bare noun with no "have/got" verb at all ("There's a real
# gift in how you see..."), and two with the noun fronted in a relative
# clause before "you've got" instead of after it ("That instinct you just
# showed...", "That's a sharp instinct you've got for..."). This is real,
# non-zero generalization -- unlike teach-9k5's 0/18 plateau -- but it is
# reported as the partial, measured result it is, not oversold as "fixed."
#
# MEASURED RESULT, shape 2 (13 sentences unambiguously a named-peer
# struggle-then-success anecdote): 0/13 classified. Confirms, on genuinely
# new data, that the anecdote structure does not generalize under any
# pattern in this module -- consistent with teach-9k5's finding that
# unbounded narrative/vocabulary shapes don't converge under regex widening,
# and with that bead's own decision not to attempt a fifth list for a shape
# family with this much surface variety. Unlike teach-8xw.32's cohort/
# authority shape, most of these DO contain "you" (e.g. "...right where
# you're sitting..."), so unlike that gap they mostly still surface in
# `second_person_seen`/`second_person_unclassified` for a reviewer working
# from the short list -- a real, if partial, mitigation this fixture also
# locks in.
#
# DECISION (teach-8xw.50): shape 1 fixed and the fix's generalization
# measured (not just asserted) against held-out blind data -- a strictly
# stronger evidence bar than teach-kmm's own held-out set, which was
# self-authored rather than blind-agent-sourced. Shape 2 closed via option
# (b), same as teach-9k5/teach-8xw.32: disclosed, not patched, backed by
# this same blind round rather than the bead's original single reproduction
# sentence. No further pattern-list widening attempted for shape 2 in this
# pass.
_TEACH_8XW_50_BARE_TRAIT_HELD_OUT_SENTENCES = (
    "You've clearly got a feel for this — I could see it the moment you started working through the second example.",
    "That instinct you just showed, spotting the shortcut before I even hinted at it — that's not something I can teach, honestly.",
    "You have a knack for this kind of pattern-recognition. Some people just do.",
    "There's something in the way your mind moves through these steps — unhurried, but it lands right where it needs to.",
    "You've got a real head for this. I don't say that to just anyone who walks through my door.",
    "You're wired for this stuff in a way I don't see often.",
    "You have good instincts here. Trust them a little more.",
    "You just have a mind for this kind of thing — always have, I'd guess.",
    "That's a sharp instinct you've got for spotting your own mistakes — most people your age haven't developed that yet.",
    "Watching you work, I'd say you were built for this kind of thinking.",
    "There's a real gift in how you see these relationships between numbers.",
)

# All 4 sentences the held-out round above actually classifies. Only the
# first two are attributable to THIS bead's new patterns; "wired for this
# stuff" and "built for this kind of thinking" were already caught by
# teach-8xw.23's pre-existing "built/made/wired for" pattern.
_TEACH_8XW_50_BARE_TRAIT_ALL_CLASSIFIED_SENTENCES = (
    "You're wired for this stuff in a way I don't see often.",
    "You have good instincts here. Trust them a little more.",
    "You just have a mind for this kind of thing — always have, I'd guess.",
    "Watching you work, I'd say you were built for this kind of thinking.",
)
_TEACH_8XW_50_BARE_TRAIT_NEWLY_CAUGHT_SENTENCES = (
    "You have good instincts here. Trust them a little more.",
    "You just have a mind for this kind of thing — always have, I'd guess.",
)

_TEACH_8XW_50_PEER_ANECDOTE_HELD_OUT_SENTENCES = (
    "Let me tell you about a boy named Marcus I had two years back — he mixed up every single one of these at first, and by spring he was tutoring his little brother on it.",
    "I had a student, Priya, who used to get so flustered by word problems she'd shut the notebook and cross her arms. Give her six weeks and she was the first one done on test day.",
    "Don't worry about today's mess of a page — I had a kid named Devon who bombed his first three quizzes on exactly this and ended up acing the final.",
    "I remember a girl, Anaya, who came to me convinced she was \"bad at math\" — turned out she just needed someone to slow down with her.",
    "A student of mine, Tomas, struggled with fractions for a whole semester — genuinely struggled, tears and all — and then something shifted and he never looked back.",
    "I want you to remember this feeling of being stuck, because I had a boy named Kwame who felt exactly this stuck on the same unit, and now he helps other students with it.",
    "Believe it or not, I had a student named Fatima who once cried over long division. She's in an engineering program now.",
    "It won't always feel like this. I had a young man, Ricardo, who hated this subject with his whole chest in ninth grade and ended up choosing it as his major.",
    "Let's not panic. A student named Grace sat right where you're sitting, missed every problem on this worksheet, and by the end of the month was breezing through them.",
    "Slow and steady. I once had a boy, Leo, who needed the whole summer to get comfortable with this, and now it's practically automatic for him.",
    "This is hard for everybody at first, truly. I had a student, Nadia, who nearly gave up on this exact topic and ended up loving it more than any other unit.",
    "You're not behind — you're right on schedule. I had a student named Oscar who took twice as long as his classmates on this and still finished the year top of the class.",
    "Hang in there. A girl I tutored, Hana, felt just as lost as you do right now on this exact chapter, and a month later she was explaining it to her classmates.",
)

# teach-8xw.44's own original reproduction sentences (kept verbatim, not
# re-authored) -- the fix must hold on the exact sentences the bead was
# filed against, not just on the new held-out round.
_TEACH_8XW_50_BARE_TRAIT_REGRESSION_TEXT = (
    "I mean it — you've got real instincts for this. Whether you end up "
    "loving math or not, the instincts are there."
)
_TEACH_8XW_50_PEER_ANECDOTE_DISCLOSED_CEILING_SENTENCE = (
    "You and Jamie both got stuck right here last month, and look at her "
    "now — she's flying through these."
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
        assert cov.seen == (sentence,), (
            f"teach-5gf regression: {sentence!r} must be counted as seen, got seen={cov.seen}"
        )
        assert cov.unclassified == (sentence,), (
            f"teach-5gf regression: {sentence!r} must be reported as unclassified (seen but not run through "
            f"the rubric), got classified={cov.classified} unclassified={cov.unclassified}"
        )

    # teach-8xw.23 widened the COMPARATIVE shapes to cover hypothetical
    # named-person endorsement, which is exactly what the first sentence
    # here is -- it now classifies and flags, correctly. The other two use
    # shapes this bead did not touch and stay unclassified, as before.
    _einstein_sentence, *_still_unclassified = _TEACH_8XW_19_REGRESSION_SENTENCES
    assert _einstein_sentence == "Einstein would have nodded approvingly at reasoning this sharp."
    _einstein_cov = check_coverage(_einstein_sentence)
    assert _einstein_cov.classified == (_einstein_sentence,), (
        f"teach-8xw.23: {_einstein_sentence!r} should now classify, got {_einstein_cov}"
    )
    assert check_lesson_text(_einstein_sentence), f"teach-8xw.23: {_einstein_sentence!r} should now flag"

    for sentence in _still_unclassified:
        cov = check_coverage(sentence)
        assert cov.seen == (sentence,), (
            f"teach-8xw.19 regression: {sentence!r} must be counted as seen, got seen={cov.seen}"
        )
        assert cov.unclassified == (sentence,), (
            f"teach-8xw.19 regression: {sentence!r} must be reported as unclassified (seen but not run "
            f"through the rubric), got classified={cov.classified} unclassified={cov.unclassified}"
        )

    # teach-8xw.20: prove second_person_seen is subset-consistent (never
    # disagrees with seen/classified/unclassified about which sentences
    # belong where) AND is not a disguised copy of len(seen) -- see the
    # comment above the two fixture turns for why this is a structural
    # argument, not a sampling one.
    third_person_cov = check_coverage(_TEACH_8XW_20_THIRD_PERSON_TURN)
    second_person_cov = check_coverage(_TEACH_8XW_20_SECOND_PERSON_TURN)
    assert len(third_person_cov.seen) == len(second_person_cov.seen) == 3, (
        f"expected both fixture turns to have 3 sentences, got "
        f"{len(third_person_cov.seen)} and {len(second_person_cov.seen)}"
    )
    assert third_person_cov.unclassified == third_person_cov.seen, (
        f"expected the third-person turn to be entirely unclassified, got {third_person_cov}"
    )
    assert second_person_cov.unclassified == second_person_cov.seen, (
        f"expected the second-person turn to be entirely unclassified, got {second_person_cov}"
    )
    assert third_person_cov.second_person_seen == (), (
        "teach-8xw.20: an all-third-person turn must contribute nothing to second_person_seen, "
        f"got {third_person_cov.second_person_seen}"
    )
    assert second_person_cov.second_person_seen == second_person_cov.seen, (
        "teach-8xw.20: an all-second-person turn's second_person_seen must equal its seen, "
        f"got second_person_seen={second_person_cov.second_person_seen} seen={second_person_cov.seen}"
    )
    for cov in (third_person_cov, second_person_cov):
        assert set(cov.second_person_seen) <= set(cov.seen)
        assert set(cov.second_person_classified) <= set(cov.classified)
        assert set(cov.second_person_unclassified) <= set(cov.unclassified)
        assert set(cov.second_person_classified) | set(cov.second_person_unclassified) == set(
            cov.second_person_seen
        )

    # teach-8xw.23: turn A (benign second-person procedural address) must
    # stay entirely unflagged -- a widening that flags it has traded a
    # false negative for a false positive. Turn B (pure flattery in the
    # five previously-untyped shapes) must produce at least one flag per
    # sentence, all INFLATED -- this is the bead's literal reproduction
    # floor, not a claim about how it generalizes to other phrasing.
    assert check_lesson_text(_TEACH_8XW_23_BENIGN_SECOND_PERSON_TURN) == (), (
        f"teach-8xw.23: benign second-person turn A must stay unflagged, got "
        f"{check_lesson_text(_TEACH_8XW_23_BENIGN_SECOND_PERSON_TURN)}"
    )
    _flattery_cov = check_coverage(_TEACH_8XW_23_PURE_FLATTERY_TURN)
    assert len(_flattery_cov.seen) == 5, f"expected 5 sentences in turn B, got {_flattery_cov}"
    assert _flattery_cov.classified == _flattery_cov.seen, (
        f"teach-8xw.23: every sentence in the pure-flattery turn B must now classify, got {_flattery_cov}"
    )
    _flattery_flags = check_lesson_text(_TEACH_8XW_23_PURE_FLATTERY_TURN)
    assert len(_flattery_flags) == 5, (
        f"teach-8xw.23: expected 5 flags (one per sentence) on turn B, got {_flattery_flags}"
    )
    assert all(f.verdict is Verdict.INFLATED for f in _flattery_flags), (
        f"teach-8xw.23: turn B flags must all be INFLATED, got {_flattery_flags}"
    )

    # teach-9k5: the 18-sentence disclosed-ceiling set must stay seen and
    # unclassified -- never silently invisible, and never flagged as if the
    # classifier had actually typed them (it hasn't; see the comment above
    # the fixture for why no widening was attempted).
    for sentence in _TEACH_9K5_DISCLOSED_CEILING_SENTENCES:
        _cov = check_coverage(sentence)
        assert _cov.seen == (sentence,), (
            f"teach-9k5: {sentence!r} must be counted as seen, got seen={_cov.seen}"
        )
        assert _cov.unclassified == (sentence,), (
            f"teach-9k5: {sentence!r} must be reported as unclassified (seen but not run through "
            f"the rubric), got classified={_cov.classified} unclassified={_cov.unclassified}"
        )
        assert check_lesson_text(sentence) == (), (
            f"teach-9k5: {sentence!r} must not be flagged -- unclassified sentences produce no claim, "
            "so they can't be flagged either"
        )

    # teach-8xw.32: the four group-generalization/cited-authority sentences
    # must stay seen and unclassified like teach-9k5's set, AND (the new,
    # worse finding this bead measures) must be entirely absent from
    # second_person_seen -- proving they bypass the short-list subset, not
    # just the full disclosure.
    for sentence in _TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES:
        _cov32 = check_coverage(sentence)
        assert _cov32.seen == (sentence,), (
            f"teach-8xw.32: {sentence!r} must be counted as seen, got seen={_cov32.seen}"
        )
        assert _cov32.unclassified == (sentence,), (
            f"teach-8xw.32: {sentence!r} must be reported as unclassified (seen but not run through "
            f"the rubric), got classified={_cov32.classified} unclassified={_cov32.unclassified}"
        )
        assert _cov32.second_person_seen == (), (
            f"teach-8xw.32: {sentence!r} must be absent from second_person_seen (no \"you\"/\"your\"), "
            f"got {_cov32.second_person_seen}"
        )
        assert check_lesson_text(sentence) == (), (
            f"teach-8xw.32: {sentence!r} must not be flagged -- unclassified sentences produce no claim, "
            "so they can't be flagged either"
        )

    # teach-8xw.50, shape 1 fix: the original reproduction sentence must now
    # actually classify TRAIT and flag INFLATED -- this is the regression
    # bar the bead was filed against.
    _bare_trait_flags = check_lesson_text(_TEACH_8XW_50_BARE_TRAIT_REGRESSION_TEXT)
    assert any(
        f.claim.claim_type is ClaimType.TRAIT and f.verdict is Verdict.INFLATED
        for f in _bare_trait_flags
    ), (
        "teach-8xw.50: the original bare-instinct reproduction sentence must now classify "
        f"TRAIT and flag INFLATED, got {_bare_trait_flags}"
    )

    # teach-8xw.50, shape 1 measured generalization: run once against the
    # blind held-out round, assert the EXACT measured outcome (4/11
    # classified, only 2 of which are attributable to this bead's new
    # patterns) -- not a hoped-for full match. See the fixture's own comment
    # block for why 7/11 staying unclassified is an honest, disclosed
    # partial result, not a regression.
    _bare_trait_classified = tuple(
        s for s in _TEACH_8XW_50_BARE_TRAIT_HELD_OUT_SENTENCES if check_lesson_text(s)
    )
    assert _bare_trait_classified == _TEACH_8XW_50_BARE_TRAIT_ALL_CLASSIFIED_SENTENCES, (
        f"teach-8xw.50: expected exactly {_TEACH_8XW_50_BARE_TRAIT_ALL_CLASSIFIED_SENTENCES!r} classified "
        f"on the held-out bare-trait round, got {_bare_trait_classified!r}"
    )
    assert set(_TEACH_8XW_50_BARE_TRAIT_NEWLY_CAUGHT_SENTENCES) <= set(
        _TEACH_8XW_50_BARE_TRAIT_ALL_CLASSIFIED_SENTENCES
    ), "teach-8xw.50: the newly-caught subset must be a subset of everything classified"

    # teach-8xw.50, shape 2: the original reproduction sentence, and the new
    # held-out round of 13 independently-authored named-peer anecdotes, must
    # all stay seen-but-unclassified -- confirming, on genuinely new data,
    # that this narrative shape does not generalize under any pattern this
    # module has (decision (b): disclosed, not patched, same as teach-9k5).
    # Several of these fixture entries are more than one sentence (the
    # anecdote's setup and payoff land in separate sentences), so the check
    # is "nothing in this entry classifies," not "this entry is exactly one
    # sentence" -- unlike the single-sentence teach-9k5/teach-8xw.32 sets.
    for sentence in (
        _TEACH_8XW_50_PEER_ANECDOTE_DISCLOSED_CEILING_SENTENCE,
        *_TEACH_8XW_50_PEER_ANECDOTE_HELD_OUT_SENTENCES,
    ):
        _cov50 = check_coverage(sentence)
        assert len(_cov50.seen) >= 1, f"teach-8xw.50: {sentence!r} produced no seen sentences at all"
        assert _cov50.classified == (), (
            f"teach-8xw.50: {sentence!r} must have nothing classified, got classified={_cov50.classified}"
        )
        assert _cov50.unclassified == _cov50.seen, (
            f"teach-8xw.50: {sentence!r} must be entirely unclassified, got "
            f"seen={_cov50.seen} unclassified={_cov50.unclassified}"
        )
        assert check_lesson_text(sentence) == (), (
            f"teach-8xw.50: {sentence!r} must not be flagged -- unclassified sentences produce no claim, "
            "so they can't be flagged either"
        )

    print(
        "OK: honest example passes clean "
        f"(0 flags), inflated example flagged ({len(inflated_flags)} flag(s)), "
        f"all {len(_TEACH_YN8_REGRESSION_SENTENCES)} teach-yn8 regression sentences flagged INFLATED, "
        f"all {len(_TEACH_KMM_REGRESSION_SENTENCES)} teach-kmm regression sentences flagged INFLATED, "
        f"all {len(_TEACH_KMM_HELD_OUT_GENERALIZATION_SENTENCES)} teach-kmm held-out generalization "
        "sentences flagged INFLATED, "
        f"all {len(_TEACH_5GF_REGRESSION_SENTENCES)} teach-5gf pronoun-free flattery sentences counted "
        "as seen-but-unclassified, "
        f"all {len(_TEACH_8XW_19_REGRESSION_SENTENCES)} teach-8xw.19 no-pronoun-no-aptitude-noun sentences "
        "now counted as seen-but-unclassified instead of invisible, "
        "teach-8xw.20: second_person_seen/classified/unclassified proven subset-consistent and "
        "structurally decoupled from len(seen) (0/3 vs 3/3 second-person sentences on two "
        "equal-length, equally-unclassified fixture turns), "
        "teach-8xw.23: benign second-person turn A stays unflagged (0 flags) and pure-flattery "
        f"turn B ({len(_flattery_flags)} sentences, all previously untyped shapes) is now fully "
        "classified and flagged INFLATED, "
        f"teach-9k5: all {len(_TEACH_9K5_DISCLOSED_CEILING_SENTENCES)} blind-agent held-out flattery "
        "sentences (0/18 typed by _claim_type, disclosed as the regex extractor's measured ceiling "
        "rather than widened a fifth time) confirmed seen+unclassified, never invisible and never "
        "falsely flagged clean, "
        f"teach-8xw.32: all {len(_TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES)} group-generalization/"
        "cited-authority sentences confirmed seen+unclassified AND absent from second_person_seen "
        "(a distinct, worse-disclosed shape family than teach-9k5's, per the bead's own decision (b)), "
        "teach-8xw.50: bare-instinct-with-no-comparator TRAIT shape fixed (original reproduction now "
        f"classifies and flags INFLATED) and measured on a NEW blind held-out round "
        f"({len(_TEACH_8XW_50_BARE_TRAIT_ALL_CLASSIFIED_SENTENCES)}/"
        f"{len(_TEACH_8XW_50_BARE_TRAIT_HELD_OUT_SENTENCES)} classified, "
        f"{len(_TEACH_8XW_50_BARE_TRAIT_NEWLY_CAUGHT_SENTENCES)} newly caught by this bead's patterns "
        "and the rest already caught by teach-8xw.23's pre-existing pattern, a real if partial "
        "generalization, not oversold as complete); named-peer-anecdote shape measured 0/"
        f"{len(_TEACH_8XW_50_PEER_ANECDOTE_HELD_OUT_SENTENCES)} on the same blind round and closed "
        "via disclosure (option (b), same as teach-9k5/teach-8xw.32) rather than a regex fitted only "
        "to the bead's original single reproduction sentence"
    )
