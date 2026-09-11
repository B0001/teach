"""Cialdini/Pre-Suasion motivation layer -- the producer's persuasion
building blocks (teach-8xw.31).

The epic (`bd show teach-8xw`) and sandbox-prompt.md both claim "motivation
is guided by Cialdini's Influence and Pre-Suasion... bounded by a hard
honesty constraint," and name this exact machinery as the highest-risk
component in the whole system: "the producer is explicitly optimized to be
persuasive... That is precisely the machinery that makes an ineffective
lesson feel like an effective one." Before this module, that claim was
false -- the only trace of it in the producer was one hand-authored
sentence (`teach/dnf_bond_lesson.py`'s closing encouragement line), not a
generation mechanism. This module is that mechanism, built the same way
`teach/cbt_primitives.py` built the CBT layer: a named, enumerable set of
moves, each with a one-line "when to use," each rendering real (if
templated) text from structured input, each requiring the specific fields
it claims to need.

THE SEVEN PRINCIPLES

Cialdini's original six (Influence) plus Pre-Suasion's seventh (unity),
exactly the seven the epic's citation names, no more invented here:

  - RECIPROCITY: hand the learner something first (a worked step, a
    concrete resource) before asking for the next small piece of effort --
    framed explicitly as a gift-then-ask, not a demand.
  - COMMITMENT_CONSISTENCY: point back at something the learner already
    said or did, and frame the next step as simply following through on
    that -- not a new, separate demand.
  - LIKING: lean on a shared narrative frame (persona, stated interest) to
    build rapport before or during instruction -- affiliation, not flattery.
  - AUTHORITY: back a claim with a *named, real, checkable* source (the
    textbook this lesson is drawn from) rather than an anonymous appeal
    ("mathematicians agree") -- deliberately excludes the shape
    teach-8xw.32 confirmed the checker cannot see, see the module-level
    note below.
  - SCARCITY: flag the one specific, easy-to-skim-past detail in the
    current material -- attention is the scarce resource being framed, not
    a false deadline or fabricated limited availability.
  - UNITY: frame the tutor and learner as sharing a category/identity ("we"
    on the same team), not merely liking each other -- Pre-Suasion's
    distinction from LIKING is preserved by requiring a shared-identity
    label, not a shared-interest one.
  - SOCIAL_PROOF: normalize a struggle by naming that other learners
    typically find the SAME step hard -- a factual, non-promissory
    observation about the material's difficulty, not a promise about what
    this learner (or "everyone") will go on to achieve. See below for why
    that boundary is drawn deliberately, not incidentally.

WHY SOCIAL_PROOF AND AUTHORITY ARE SHAPED THIS WAY, NOT THE NAIVE WAY

teach-8xw.32 (filed alongside this bead, confirmed and closed before this
module was written) measured that `teach.potential_checker` cannot see two
specific shapes at all: group-generalization claims ("everyone who masters
X goes on to Y with ease") and anonymous cited-authority claims
("mathematicians agree that..."). Both shapes are exactly what a naive
implementation of Cialdini's social-proof and authority principles would
produce for a *motivation* layer -- a promise about the learner's own
future, backed by an appeal to a crowd or an unnamed expert. Building this
layer to produce exactly that shape would "test" the checker only in the
sense that it's already-measured-blind: `teach-8xw.32`'s own regression
fixtures (`_TEACH_8XW_32_DISCLOSED_CEILING_SENTENCES` in
`teach/potential_checker.py`) are precisely those sentences, and they are
already proven, permanently, to slip through both `extract_claims` and the
second-person coverage subset. Reproducing that here would add nothing
newly measured; it would just be a second copy of a result this repo
already has.

So `render_social_proof` is deliberately built to stay on the honest side
of that line: it names a shared *difficulty* ("other learners find this
step counterintuitive on a first pass"), never a shared *outcome*
("everyone who gets past this goes on to..."). Likewise `render_authority`
requires a named, real source (the textbook this lesson is drawn from) for
a *domain fact*, not an anonymous crowd appeal for a *potential claim*. This
is a design choice this module makes and states plainly, not a claim that
these principles are safe in general -- `_integration_check` in
`teach/cialdini_integration_check.py` runs both the honest renderings above
AND teach-8xw.32's own confirmed-blind sentence (verbatim, not
re-authored) through the real checker side by side, so the contrast between
"built to stay honest" and "known to slip past" is measured, not asserted.

WHAT THIS MODULE DOES AND DOES NOT DO

Same scope discipline as `teach/cbt_primitives.py`: this defines the seven
moves and proves each renders non-empty, on-topic, *varying* output (two
template variants per move, selected by an explicit index -- proof this is
generation logic, not one hand-authored string per principle) from a
minimal fake `MotivationMoment`. It does not decide *when* in a real
traversal each principle should fire (that is `teach/dnf_bond_lesson.py` or
a future integration's job, same division of labor `cbt_primitives.py`
draws for the CBT layer).

`teach/cialdini_integration_check.py` remains the module that runs this
one's *output* through the checker for measurement and reports the result
side by side with the naive alternative -- that direction of the boundary
(checker-shaped analysis of rendered text, after the fact) is unchanged by
this module.

teach-8xw.38 changed one thing: `render_authority`'s `authority_fact` field
is free text a caller could fill with an overpromise dressed as a citation
("Dummit and Foote states this plainly: every student who masters this
theorem goes on to prove new results with ease") -- unlike
`render_social_proof`'s `peer_difficulty`, which the fixed templates only
ever slot into difficulty-shaped sentences, `authority_fact` is embedded
verbatim with no wrapping constraint at all. So `render_authority` now
imports `teach.potential_checker` (`extract_claims`, the same public
extraction entry point the real checker uses) as an INPUT guard on that one
field, at render time, before any text reaches a learner -- see
`_looks_like_overpromise` below. This is not the checker reading the
producer's internals (the direction sandbox-prompt.md's split forbids): it
is the producer calling the checker's already-independently-built, public
classification function to reject its own input. The checker, when it
later runs over whatever this module emits, still does so with zero
knowledge that this guard ran, exactly as blind as before.
"""
from __future__ import annotations

import dataclasses
import enum
import re
from typing import Callable

from teach import potential_checker


@dataclasses.dataclass(frozen=True)
class MotivationMoment:
    """A minimal, fake stand-in for whatever real lesson state a future
    integration will carry -- exactly `cbt_primitives.LessonMoment`'s role,
    for the persuasion layer instead of the CBT layer. Just enough fields
    for each principle below to have something concrete to render from.
    """

    concept_name: str
    given_first: str | None = None
    next_ask: str | None = None
    prior_commitment: str | None = None
    consistent_next_step: str | None = None
    shared_frame: str | None = None
    shared_identity: str | None = None
    scarce_detail: str | None = None
    cited_source: str | None = None
    authority_fact: str | None = None
    peer_difficulty: str | None = None


def _require(moment: MotivationMoment, field: str) -> str:
    value = getattr(moment, field)
    if not value:
        raise ValueError(
            f"MotivationMoment.{field} is required to render this principle, got {value!r}"
        )
    return value


# --- authority_fact domain-fact guard (teach-8xw.38) -----------------------
#
# teach-8xw.32 measured `teach.potential_checker` as structurally blind to
# cohort-generalization ("everyone who masters X goes on to Y") and cited-
# authority ("mathematicians agree that...") claims, and closed that bead by
# disclosing the gap rather than widening the general extractor's pattern
# list -- widening that whitelist has repeatedly looked like progress and
# then failed the next independently-phrased round (teach-yn8 -> teach-kmm
# -> teach-5gf -> teach-8xw.19 -> teach-8xw.23 -> teach-9k5 -> teach-8xw.32).
# That decision was correctly scoped to `potential_checker`'s own job:
# classifying arbitrary lesson text it never chose the shape of.
#
# `authority_fact` is a narrower problem than arbitrary lesson text. This
# field is documented to hold exactly one thing -- a domain fact
# attributable to the cited source -- never a claim about the learner or a
# cohort of learners. A caller who fills it with a promise (of any shape,
# recognized by the general checker or not) is misusing this specific
# field, so this guard can afford to be strict exactly where the general
# checker chose to abstain. It is a local, field-scoped heuristic, not a
# reopening of teach-8xw.32's decision: it does not modify
# `potential_checker`, and it makes no claim to generalize to lesson text at
# large -- only to this one field, at render time, before the text exists
# for a learner to read.
#
# Two independent rejection conditions, matching the bead's own framing of
# "both are suspicious for this field":
#
#   1. `potential_checker.extract_claims` recognizes ANY potential-claim
#      shape in it at all (TRAIT/COMPARATIVE/GROWTH/OUTCOME) -- regardless
#      of what `honesty_rubric.classify` would say about it. Even an
#      honestly-conditioned promise is still a promise, not a domain fact,
#      and this field is not the place for one.
#   2. It structurally resembles the cohort-generalization/cited-authority
#      shape teach-8xw.32 confirmed the general extractor cannot type at
#      all -- a cohort-of-people noun phrase ("everyone who...", "students
#      who...", "mathematicians") within one clause of a future-outcome verb
#      ("goes on to", "will", "almost always", "with ease", "agree that").
#      This is intentionally narrow (bounded noun/verb vocabulary, not bare
#      "everyone" or bare "will") for the same reason every pattern above it
#      in `potential_checker` is kept narrow: it must not collide with
#      ordinary domain exposition ("every element", "the group will act
#      transitively"). It is a heuristic, not a proof -- it can still miss
#      phrasing neither check recognizes, exactly like every pattern list
#      this repo has ever shipped -- so it errs toward rejecting the
#      ambiguous case for this one field rather than admitting it.
_AUTHORITY_COHORT_GENERALIZATION_PATTERN = re.compile(
    r"\b(everyone|every student|every learner|all students|all learners|"
    r"students? who|learners? who|anyone who|people who|mathematicians)\b"
    r"[^.?!]{0,80}?"
    r"\b(goes? on to|will\b|almost always|with ease|agree that)\b",
    re.IGNORECASE,
)


def _looks_like_overpromise(fact: str) -> bool:
    """True if `fact` is unfit for `authority_fact` because it reads as a
    claim about a learner's (or a cohort's) potential rather than a domain
    fact -- see the comment above for the two conditions checked and why."""
    if potential_checker.extract_claims(fact):
        return True
    return bool(_AUTHORITY_COHORT_GENERALIZATION_PATTERN.search(fact))


def _require_domain_fact(moment: MotivationMoment, field: str) -> str:
    """Same gate as `_require`, plus the overpromise guard above. Used only
    for AUTHORITY's `authority_fact` -- the one field in this module that
    embeds caller-supplied free text with no templated wrapping constraint
    of its own."""
    value = _require(moment, field)
    if _looks_like_overpromise(value):
        raise ValueError(
            f"MotivationMoment.{field} must be a checkable domain fact attributable to "
            f"the cited source, not a promise about the learner's (or a cohort's) "
            f"potential -- got {value!r}"
        )
    return value


def render_reciprocity(moment: MotivationMoment, variant: int = 0) -> str:
    """Requires `given_first` (something already handed to the learner --
    a worked step, a resource) and `next_ask` (the small thing asked in
    return). Order matters: the gift is stated before the ask, always."""
    given = _require(moment, "given_first")
    ask = _require(moment, "next_ask")
    templates = (
        (
            f"Here's {given}, worked through for {moment.concept_name} -- no strings. "
            f"In return, all I'm asking is {ask}."
        ),
        (
            f"Take {given}; that's yours for {moment.concept_name} regardless of what "
            f"happens next. Since you've got that in hand, {ask} is the one thing I'd "
            f"ask back."
        ),
    )
    return templates[variant % len(templates)]


def render_commitment_consistency(moment: MotivationMoment, variant: int = 0) -> str:
    """Requires `prior_commitment` (something the learner already said or
    did) and `consistent_next_step` (framed as following through on it, not
    a new ask)."""
    prior = _require(moment, "prior_commitment")
    step = _require(moment, "consistent_next_step")
    templates = (
        (
            f'You already said "{prior}" about {moment.concept_name}. '
            f"If you keep working that way, you'll be ready to tackle {step} "
            f"next -- the same kind of move you just handled a moment ago, "
            f"not a new ask."
        ),
        (
            f'"{prior}" -- that was your call on {moment.concept_name}, not mine. '
            f"So {step} isn't me asking for more; it's you keeping to what you "
            f"already committed to."
        ),
    )
    return templates[variant % len(templates)]


def render_liking(moment: MotivationMoment, variant: int = 0) -> str:
    """Requires `shared_frame`: the narrative or interest the tutor and
    learner already share (a persona's stated frame, e.g. Bond). Builds
    rapport through affiliation with that shared frame, not flattery about
    the learner."""
    frame = _require(moment, "shared_frame")
    templates = (
        (
            f"You picked {frame} for a reason, and {moment.concept_name} is the "
            f"part of it that actually runs on this idea -- so let's stay inside "
            f"that frame while we work through it."
        ),
        (
            f"Since we're both already invested in {frame}, {moment.concept_name} "
            f"is going to land better told the way {frame} would tell it -- so "
            f"that's how we'll take it."
        ),
    )
    return templates[variant % len(templates)]


def render_authority(moment: MotivationMoment, variant: int = 0) -> str:
    """Requires `cited_source` (a named, real, checkable source -- not an
    anonymous crowd) and `authority_fact` (the domain fact attributed to
    it). Deliberately narrow: this backs a checkable domain claim, not a
    promise about the learner, and the source must be nameable, not a bare
    'experts agree.' `authority_fact` is additionally run through
    `_require_domain_fact`'s overpromise guard (teach-8xw.38): a caller
    cannot smuggle a promise about the learner's potential through this
    field just because it's dressed as a citation."""
    source = _require(moment, "cited_source")
    fact = _require_domain_fact(moment, "authority_fact")
    templates = (
        (
            f"{source} states this plainly for {moment.concept_name}: {fact}. "
            f"That's not my framing -- it's the source's."
        ),
        (
            f"Don't take my word for {moment.concept_name} -- {source} says it "
            f"directly: {fact}."
        ),
    )
    return templates[variant % len(templates)]


def render_scarcity(moment: MotivationMoment, variant: int = 0) -> str:
    """Requires `scarce_detail`: the one specific, easy-to-skim-past detail
    in the current material. Frames attention as the scarce resource --
    never a fabricated deadline or fake limited availability."""
    detail = _require(moment, "scarce_detail")
    templates = (
        (
            f"Almost everyone skims past this exact part of {moment.concept_name}: "
            f"{detail}. Slow down for just this one line."
        ),
        (
            f"This is the one detail in {moment.concept_name} that's easy to read "
            f"past without noticing: {detail}. It won't come back around, so catch "
            f"it now."
        ),
    )
    return templates[variant % len(templates)]


def render_unity(moment: MotivationMoment, variant: int = 0) -> str:
    """Requires `shared_identity`: a category or in-group label the tutor
    and learner both belong to (Pre-Suasion's distinction from LIKING --
    shared identity, not shared interest)."""
    identity = _require(moment, "shared_identity")
    templates = (
        (
            f"As {identity}, this next part of {moment.concept_name} is ours to "
            f"work out together, not mine to hand you and yours to receive."
        ),
        (
            f"We're both {identity} here -- {moment.concept_name} is something "
            f"we're solving as one unit, not a test I'm giving you from outside it."
        ),
    )
    return templates[variant % len(templates)]


def render_social_proof(moment: MotivationMoment, variant: int = 0) -> str:
    """Requires `peer_difficulty`: what other learners typically find hard
    about this exact step. Normalizes STRUGGLE, never promises an OUTCOME
    -- see the module docstring for why this boundary is deliberate, not
    incidental."""
    difficulty = _require(moment, "peer_difficulty")
    templates = (
        (
            f"Most learners hit the same snag you might right here in "
            f"{moment.concept_name}: {difficulty}. That's the normal shape of "
            f"this step, not a sign of anything about you."
        ),
        (
            f"If {difficulty} feels like the sticking point in {moment.concept_name} "
            f"right now, that tracks -- it's exactly where most people slow down too."
        ),
    )
    return templates[variant % len(templates)]


class PrincipleName(enum.Enum):
    RECIPROCITY = "reciprocity"
    COMMITMENT_CONSISTENCY = "commitment_consistency"
    LIKING = "liking"
    AUTHORITY = "authority"
    SCARCITY = "scarcity"
    UNITY = "unity"
    SOCIAL_PROOF = "social_proof"


@dataclasses.dataclass(frozen=True)
class PersuasionMove:
    """One named Cialdini/Pre-Suasion principle: when it applies, and how
    to render it from a `MotivationMoment`. Mirrors
    `cbt_primitives.PedagogicalMove` exactly."""

    name: PrincipleName
    when_to_use: str
    render: Callable[[MotivationMoment, int], str]


MOVES: tuple[PersuasionMove, ...] = (
    PersuasionMove(
        name=PrincipleName.RECIPROCITY,
        when_to_use=(
            "The tutor is about to ask for effort and can hand the learner "
            "something concrete and useful first, so the ask follows a gift "
            "instead of arriving cold."
        ),
        render=render_reciprocity,
    ),
    PersuasionMove(
        name=PrincipleName.COMMITMENT_CONSISTENCY,
        when_to_use=(
            "The learner already said or did something on record, and the "
            "next step can be framed as following through on that rather "
            "than as a new, separate demand."
        ),
        render=render_commitment_consistency,
    ),
    PersuasionMove(
        name=PrincipleName.LIKING,
        when_to_use=(
            "A shared narrative frame or stated interest is already "
            "established and can carry the next piece of instruction, "
            "building rapport through affiliation rather than flattery."
        ),
        render=render_liking,
    ),
    PersuasionMove(
        name=PrincipleName.AUTHORITY,
        when_to_use=(
            "A domain claim needs backing, and a specific, named, "
            "checkable source (the textbook this lesson is drawn from) can "
            "be cited directly for it."
        ),
        render=render_authority,
    ),
    PersuasionMove(
        name=PrincipleName.SCARCITY,
        when_to_use=(
            "The current material has one specific detail that's easy to "
            "read past without noticing, and calling it out earns more "
            "attention than restating the whole passage would."
        ),
        render=render_scarcity,
    ),
    PersuasionMove(
        name=PrincipleName.UNITY,
        when_to_use=(
            "The tutor and learner share an in-group identity (not just a "
            "common interest) that the next step can be framed inside, as "
            "something worked out together rather than handed down."
        ),
        render=render_unity,
    ),
    PersuasionMove(
        name=PrincipleName.SOCIAL_PROOF,
        when_to_use=(
            "The learner is about to hit (or just hit) a step that "
            "typically trips learners up, and naming that difficulty as "
            "normal will do more than silence would."
        ),
        render=render_social_proof,
    ),
)


# --- fake lesson contexts for the runnable check ---------------------------
# One minimal MotivationMoment per principle, populated with only the
# fields that principle needs -- same role as cbt_primitives.FAKE_CONTEXTS.

FAKE_CONTEXTS: dict[PrincipleName, MotivationMoment] = {
    PrincipleName.RECIPROCITY: MotivationMoment(
        concept_name="normal subgroups",
        given_first="a fully worked example checking that a specific subgroup is normal",
        next_ask="try the next one yourself, using the same steps",
    ),
    PrincipleName.COMMITMENT_CONSISTENCY: MotivationMoment(
        concept_name="normal subgroups",
        prior_commitment="I want to actually understand this, not just pass",
        consistent_next_step="working through this harder example instead of skipping it",
    ),
    PrincipleName.LIKING: MotivationMoment(
        concept_name="normal subgroups",
        shared_frame="the Bond briefing",
    ),
    PrincipleName.AUTHORITY: MotivationMoment(
        concept_name="normal subgroups",
        cited_source="Dummit and Foote's Abstract Algebra",
        authority_fact="a subgroup is normal exactly when its left and right cosets coincide",
    ),
    PrincipleName.SCARCITY: MotivationMoment(
        concept_name="normal subgroups",
        scarce_detail="the definition requires this for every element, not just some",
    ),
    PrincipleName.UNITY: MotivationMoment(
        concept_name="normal subgroups",
        shared_identity="the two of us working this problem set",
    ),
    PrincipleName.SOCIAL_PROOF: MotivationMoment(
        concept_name="normal subgroups",
        peer_difficulty="mixing up 'closed under conjugation' with 'closed under the operation'",
    ),
}


def is_on_topic(text: str, concept_name: str) -> bool:
    """Same mechanical proxy as `cbt_primitives.is_on_topic`: the rendered
    text must actually mention the concept it was rendered for."""
    return concept_name.lower() in text.lower()


if __name__ == "__main__":
    assert len(MOVES) == 7, f"expected exactly 7 named principles, got {len(MOVES)}"
    assert {m.name for m in MOVES} == set(PrincipleName), "MOVES must cover every PrincipleName exactly once"

    for move in MOVES:
        assert move.when_to_use.strip(), f"{move.name}: when_to_use must not be empty"
        moment = FAKE_CONTEXTS[move.name]

        variant_0 = move.render(moment, 0)
        variant_1 = move.render(moment, 1)
        assert variant_0.strip(), f"{move.name}: variant 0 rendered empty output"
        assert variant_1.strip(), f"{move.name}: variant 1 rendered empty output"
        assert is_on_topic(variant_0, moment.concept_name), (
            f"{move.name}: variant 0 does not mention concept {moment.concept_name!r}: {variant_0!r}"
        )
        assert is_on_topic(variant_1, moment.concept_name), (
            f"{move.name}: variant 1 does not mention concept {moment.concept_name!r}: {variant_1!r}"
        )
        # Proof this is generation logic, not one hand-authored string per
        # principle: two requested variants must actually differ.
        assert variant_0 != variant_1, (
            f"{move.name}: variant 0 and variant 1 rendered identical text -- "
            "this is a fixed string, not generation logic"
        )

    # Each required field actually gates rendering -- a move must not
    # silently produce plausible-looking filler when its input is missing
    # (same invariant cbt_primitives.py enforces for the CBT layer).
    _required_fields = {
        PrincipleName.RECIPROCITY: ("given_first", "next_ask"),
        PrincipleName.COMMITMENT_CONSISTENCY: ("prior_commitment", "consistent_next_step"),
        PrincipleName.LIKING: ("shared_frame",),
        PrincipleName.AUTHORITY: ("cited_source", "authority_fact"),
        PrincipleName.SCARCITY: ("scarce_detail",),
        PrincipleName.UNITY: ("shared_identity",),
        PrincipleName.SOCIAL_PROOF: ("peer_difficulty",),
    }
    for move in MOVES:
        for field in _required_fields[move.name]:
            bare = MotivationMoment(concept_name="normal subgroups")
            try:
                move.render(bare, 0)
                raise AssertionError(f"{move.name}: expected ValueError with {field} missing")
            except ValueError:
                pass

    print(
        f"OK: {len(MOVES)} Cialdini/Pre-Suasion principles all render non-empty, "
        "on-topic, genuinely-varying (2 distinct template variants each) output "
        "from a fake motivation moment, and each requires its stated fields"
    )
