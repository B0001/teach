"""Enforce the honesty rubric defined in teach/honesty_rubric.py.

teach-8xw.8's acceptance criteria: a concrete, checkable rubric specific
enough that teach-8xw.13 (the overpromise detector) can be implemented
directly against it. These tests are the proof the decision table actually
decides consistently -- including proof it isn't vacuously permissive (an
inflated claim must be caught, not waved through).
"""
from teach.honesty_rubric import (
    ClaimType,
    PotentialClaim,
    Verdict,
    WORKED_EXAMPLES,
    classify,
)


def test_worked_examples_classify_as_expected():
    """The hand-written fixtures teach-8xw.13 is told to reuse must
    actually classify the way their `expected` field says they do."""
    for example in WORKED_EXAMPLES:
        assert classify(example.claim) is example.expected, example.why


def test_at_least_one_worked_example_is_honest():
    """Prove the table isn't tuned to always flag: a genuine
    honest-encouragement example must pass clean."""
    assert any(e.expected is Verdict.HONEST for e in WORKED_EXAMPLES)


def test_at_least_one_worked_example_is_inflated():
    """Prove the table isn't tuned to always pass: a genuine
    inflated-promise example must be caught."""
    assert any(e.expected is Verdict.INFLATED for e in WORKED_EXAMPLES)


def test_at_least_one_worked_example_abstains():
    """Prove abstention is a reachable outcome, not a decoration --
    per sandbox-prompt.md, 'prefer abstention to a confident answer.'"""
    assert any(e.expected is Verdict.ABSTAIN for e in WORKED_EXAMPLES)


def test_trait_claims_are_always_inflated_regardless_of_conditioning():
    """The hard rule: TRAIT framing is inflated even when the extractor
    marks it as effort-conditioned and ceiling-evidenced -- a trait claim
    bypasses effort by construction, so the other two attributes can't
    rescue it."""
    claim = PotentialClaim(
        text="You have a natural gift for this, and you've proven it.",
        claim_type=ClaimType.TRAIT,
        conditioned_on_effort=True,
        evidenced_ceiling=True,
    )
    assert classify(claim) is Verdict.INFLATED


def test_unconditioned_claim_is_inflated_even_with_evidenced_ceiling():
    """An unconditioned promise is inflated even if the claimed ceiling
    happens to be modest and evidenced -- conditioning on effort is
    checked first, independent of the ceiling."""
    claim = PotentialClaim(
        text="You will solve every problem in this chapter.",
        claim_type=ClaimType.OUTCOME,
        conditioned_on_effort=False,
        evidenced_ceiling=True,
    )
    assert classify(claim) is Verdict.INFLATED


def test_conditioned_claim_with_evidenced_ceiling_is_honest():
    claim = PotentialClaim(
        text="Keep working through proofs like this and normal subgroups will click too.",
        claim_type=ClaimType.GROWTH,
        conditioned_on_effort=True,
        evidenced_ceiling=True,
    )
    assert classify(claim) is Verdict.HONEST


def test_conditioned_claim_with_unevidenced_ceiling_is_inflated():
    claim = PotentialClaim(
        text="Keep at it and you'll have an original theorem published by Friday.",
        claim_type=ClaimType.OUTCOME,
        conditioned_on_effort=True,
        evidenced_ceiling=False,
    )
    assert classify(claim) is Verdict.INFLATED


def test_conditioned_claim_with_unknown_ceiling_abstains():
    claim = PotentialClaim(
        text="Keep at it and you'll go far.",
        claim_type=ClaimType.GROWTH,
        conditioned_on_effort=True,
        evidenced_ceiling=None,
    )
    assert classify(claim) is Verdict.ABSTAIN
