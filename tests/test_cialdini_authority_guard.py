"""teach-8xw.38: `render_authority`'s `authority_fact` field had no runtime
check that it holds a domain fact rather than a promise about the
learner's (or a cohort's) potential dressed up as a citation. Proves the
bead's exact repro is now rejected at render time, not silently passed
through to `teach.potential_checker` (which -- correctly, and by
teach-8xw.32's own design decision -- would not have caught it downstream).
"""
import pytest

from teach.cialdini import MotivationMoment, render_authority
from teach.potential_checker import extract_claims


# The bead's own repro sentence, verbatim: structurally identical to
# teach-8xw.32's disclosed cohort-generalization/cited-authority shape
# ("Students who reach this point almost always go on to master group
# theory with ease"), and confirmed unclassified by `extract_claims` either
# with or without a "tutor:" wrapper -- the same pre-existing gap, not a new
# detection failure.
_TEACH_8XW_38_REPRO_FACT = (
    "every student who masters this theorem goes on to prove new results with ease"
)


def test_repro_authority_fact_is_unclassified_by_the_general_checker():
    """Confirms the premise: this is the already-measured teach-8xw.32 gap,
    not something new `potential_checker` would catch on its own."""
    assert extract_claims(_TEACH_8XW_38_REPRO_FACT) == ()
    assert extract_claims("tutor: " + _TEACH_8XW_38_REPRO_FACT) == ()


def test_render_authority_rejects_the_teach_8xw_38_repro_fact():
    moment = MotivationMoment(
        concept_name="Lagrange theorem",
        cited_source="Dummit and Foote",
        authority_fact=_TEACH_8XW_38_REPRO_FACT,
    )
    with pytest.raises(ValueError, match="checkable domain fact"):
        render_authority(moment, 0)


@pytest.mark.parametrize(
    "overpromise_fact",
    [
        # cohort-generalization + future-outcome (the repro's exact shape).
        "every student who masters this theorem goes on to prove new results with ease",
        # cited-authority framing wrapping the same cohort-outcome shape.
        "mathematicians agree that a student who reasons like this is on track for real results",
        # a claim `_claim_type` classifies outright (OUTCOME shape, no
        # cohort wording at all) -- still not a domain fact, must still be
        # rejected regardless of what `honesty_rubric.classify` would say.
        "you will breeze through every proof after this one",
    ],
)
def test_render_authority_rejects_overpromise_shapes(overpromise_fact):
    moment = MotivationMoment(
        concept_name="Lagrange theorem",
        cited_source="Dummit and Foote",
        authority_fact=overpromise_fact,
    )
    with pytest.raises(ValueError):
        render_authority(moment, 0)


@pytest.mark.parametrize(
    "domain_fact",
    [
        "a subgroup is normal exactly when its left and right cosets coincide",
        "cosets partition the group",
        "a subgroup is normal exactly when its left and right cosets coincide for every element",
    ],
)
def test_render_authority_still_accepts_ordinary_domain_facts(domain_fact):
    """The guard must not reject the kind of plain domain content this
    field exists to carry -- proven against the exact facts already used in
    this module's own fixtures and the pre-existing test suite."""
    moment = MotivationMoment(
        concept_name="cosets",
        cited_source="Dummit and Foote's Abstract Algebra",
        authority_fact=domain_fact,
    )
    output = render_authority(moment, 0)
    assert domain_fact in output
