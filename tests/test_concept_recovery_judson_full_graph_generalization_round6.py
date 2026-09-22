"""teach-911: fresh held-out round, required by that bead's own closing rule
against validating a fix against a round that discovered the finding it
fixes -- round5 (test_concept_recovery_judson_full_graph_generalization_
round5.py) is exactly the round whose blind-authored RINGS fixture first
surfaced judson:16.1-rings' coverage-gap-veto false abstention, and re-
scoring round5's own RINGS text after tuning the fix against it would not be
a fresh measurement. This round re-authored a fresh rings dialogue, plus two
sibling ring/field-family topics never used in round5's fixture text, to
check the judson:16.1-rings vocabulary enrichment has not created a NEW
false-positive attractor pulling in unrelated lessons.

All three lesson texts below were produced by three separate, parallel
`Agent` tool calls, each given an explicit no-tool-use, no-repository-access
instruction and told nothing about concept_recovery.py, this bead,
judson:16.1-rings, or any threshold or mechanism in this module -- only a
plain-English topic name and a request to render it as a natural 300-500
word tutor/student dialogue, using the agent's own general knowledge of
abstract algebra, with no reference to any specific textbook. None of the
three agents saw another's output, this module's code, or any prior round's
fixtures.

HONEST RESULT (measured once against the real, unmodified, POST-teach-911
`load_judson_full_graph()` / `judson_ring_field.json`, via the public
`recover_from_lesson_text` / `score_candidates` entry points only -- no
internals of concept_recovery.py were read to choose or adjust these lesson
texts, and no threshold, word list, or node vocabulary was changed in
response to seeing these results):

  correct recoveries:      1 / 3  (RINGS)
  safe abstentions:        2 / 3  (POLYNOMIAL_RINGS, INTEGRAL_DOMAINS)
  CONFIDENT WRONG ANSWER:  0 / 3

This bead's target bug, checked directly on this fresh text:

  RINGS:  FULLY RESOLVED on genuinely fresh, non-verbatim text.
      judson:16.1-rings now wins outright -- raw score 15, a decisive
      margin over the runner-up (judson:17.1-polynomial-rings, 7). Before
      teach-911's fix, this same node's own coverage-gap veto would have
      fired on any natural rings lesson scoring this way (see round5's own
      original finding); the matrix-example vocabulary fold-in plus the
      `_DISCOURSE_STOPWORDS` extension close that gap here too, on text
      neither of those changes was tuned against.

Two sibling topics, run to check the enrichment has not newly attracted
unrelated lessons (the inverse failure mode, mirroring teach-57f's
judson:18.2 over-large-vocabulary problem) -- both are PRE-EXISTING safe
abstentions, confirmed via direct pre/post-teach-911 comparison (reverting
only judson:16.1-rings' extraction to its pre-fix, git-HEAD state) to be
byte-for-byte IDENTICAL in outcome and score before and after this bead's
fix, so neither is caused by it:

  POLYNOMIAL_RINGS (topic: polynomial rings, degree, arithmetic, zero
      divisors and degree collapse):  SAFE ABSTENTION -- "too close to
      call" between judson:17.1-polynomial-rings (8) and judson:16.1-rings
      (7). Pre-teach-911 scores for both nodes on this exact text: 8 and 7,
      identical -- this text does not use any of the fold-in's new
      vocabulary ("matrices", "matrix", "entries", "noncommutative") at
      all, so the fix has zero effect on it either way. Not a new finding;
      not investigated further here as out of this bead's scope.

  INTEGRAL_DOMAINS (topic: integral domains and fields, zero divisors,
      cancellation, finite domains are fields):  SAFE ABSTENTION -- "too
      close to call" between judson:18.2-factorization-in-integral-domains
      (11), judson:16.1-rings (10), and judson:16.2-integral-domains-and-
      fields (10). This is the same teach-57f judson:18.2 attractor pattern
      already documented in round5's own INTEGRAL_DOMAINS_AND_FIELDS test,
      recurring on different fresh text -- not a new finding. Pre-teach-911
      scores for all three nodes on this exact text: 11, 10, 10, identical
      -- confirmed not caused by this bead's fix.
"""

from teach.concept_recovery import (
    build_vocabulary_index,
    recover_from_lesson_text,
    score_candidates,
)
from teach.judson_algebra_graph import load_judson_full_graph

GRAPH = load_judson_full_graph()
INDEX = build_vocabulary_index(GRAPH)


RINGS = """Tutor: So today's topic is rings. You've done group theory — think of a ring as a set with two operations instead of one: addition and multiplication.

Student: Okay, so does that mean it's just a group under both?

Tutor: Close, but not quite. A ring is an abelian group under addition — so you have zero, additive inverses, commutativity, all of that — but under multiplication it's much weaker. You just need multiplication to be associative, and you need the distributive laws to tie the two operations together.

Student: So multiplication doesn't need inverses at all?

Tutor: Right, not even for nonzero elements in general. It doesn't even need to be commutative, depending on which definition you're using. Some people require a multiplicative identity, "1," and some don't — we'll assume rings have a 1 unless I say otherwise.

Student: Can you give me an example so this feels less abstract?

Tutor: Sure — the integers. Under addition they're an abelian group, zero is the identity, negatives are inverses. Multiplication is associative, has an identity, 1, and distributes over addition. But notice: 2 has no multiplicative inverse in the integers, no integer times 2 gives you 1.

Student: Right, that's why we need the rationals for that.

Tutor: Exactly — the rationals are a ring too, but a special kind called a field, where every nonzero element does have a multiplicative inverse. Not all rings are fields, though.

Student: Got it. So integers are commutative — is there an example where multiplication isn't commutative?

Tutor: Great question. Take 2-by-2 matrices with real number entries. You can add them entry-wise, that's an abelian group. You can multiply them using matrix multiplication, which is associative and distributes over addition. But if you take two matrices A and B, AB usually isn't equal to BA.

Student: Can you show me quickly?

Tutor: Sure. Let A be the matrix with rows [1, 1] and [0, 1], and B be the matrix with rows [1, 0] and [1, 1]. If you multiply AB you get a different matrix than BA — try it and you'll see the top-right and bottom-left entries come out differently.

Student: Okay, I'll work that out. So a ring doesn't even need commutative multiplication, just associativity and distributing over addition.

Tutor: Exactly. And that's why we specifically call rings like the integers "commutative rings" — it's a meaningful extra property, not something automatic.

Student: This makes way more sense now. So basically: additive structure is strict, multiplicative structure is loose, and distributivity is the glue holding them together.

Tutor: Perfectly put. That's exactly the heart of the definition."""

POLYNOMIAL_RINGS = """Tutor: So today let's talk about polynomial rings. If I hand you a polynomial like 3x² + 2x + 1, what's its degree?

Student: That's easy, it's 2. The highest power of x.

Tutor: Right. Formally, if p(x) = aₙxⁿ + ... + a₁x + a₀ and aₙ ≠ 0, the degree is n. Now what about the zero polynomial?

Student: Zero has... no terms? Is its degree zero?

Tutor: Good instinct to ask, but no — by convention the degree of the zero polynomial is either left undefined or set to −∞. It causes too many exceptions otherwise, so we usually just set it aside as a special case.

Student: Okay, fair enough. So how does addition affect degree?

Tutor: Think about it directly. If f has degree m and g has degree n, and say m > n, what happens when you add them?

Student: The x^m term from f has nothing to cancel it, so the sum still has degree m. So deg(f+g) = max(m,n)?

Tutor: Exactly, as long as m ≠ n. What if m = n?

Student: Then the leading terms could cancel... so the degree could drop below m.

Tutor: Right, so in general deg(f+g) ≤ max(deg f, deg g), with equality unless the leading terms cancel. Now, multiplication — same setup, f degree m, g degree n. What's the leading term of the product?

Student: I'd multiply the leading terms together: aₘxᵐ times bₙxⁿ gives aₘbₙ x^(m+n). So the degree is m+n?

Tutor: That's the natural guess. It's true as long as aₘbₙ ≠ 0. When would that leading coefficient vanish even though aₘ and bₙ are both nonzero?

Student: Hmm... if the ring itself has zero divisors? Like nonzero elements that multiply to zero?

Tutor: Exactly. Take ℤ/4ℤ as the coefficient ring. Let f(x) = 2x + 1 and g(x) = 2x + 1. Multiply them.

Student: 4x² + 4x + 1... but 4 = 0 mod 4, so that's just 1. Whoa, the product has degree 0, even though both factors have degree 1!

Tutor: Right — the leading coefficients were both 2, and 2·2 = 4 = 0 in that ring. So degree can drop unexpectedly.

Student: So the clean rule deg(fg) = deg(f) + deg(g) only really holds when there are no zero divisors messing with the leading coefficients?

Tutor: Precisely — it holds whenever the ring is an integral domain, since then a product of nonzero elements is nonzero, so the leading coefficients can never cancel like that.

Student: That makes sense why we usually do polynomial rings over fields or ℤ in intro courses — it keeps degree well-behaved.

Tutor: Exactly the reason."""

INTEGRAL_DOMAINS = """Tutor: Let's talk about integral domains. Do you remember what makes a ring an integral domain?

Student: It's a commutative ring with identity where... there are no zero divisors? Something like that?

Tutor: Exactly. Formally, if a and b are elements of the ring and ab = 0, then a = 0 or b = 0. Can you think of a ring where that fails?

Student: Sure, integers mod 6. Like 2 times 3 is 6, which is 0 mod 6, but neither 2 nor 3 is 0.

Tutor: Perfect example. So 2 and 3 are zero divisors in Z/6Z. Now why do we care so much about avoiding zero divisors?

Student: I know it's important but I'm fuzzy on why.

Tutor: Think about cancellation. In the integers, if ac = bc and c isn't zero, you can cancel c and conclude a = b. Does that work in Z/6Z?

Student: Let me check... 2 times 1 is 2, and 2 times 4 is 8, which is 2 mod 6. So 2·1 = 2·4 but 1 ≠ 4. So cancellation fails.

Tutor: Right, and notice that failure happens precisely because 2 is a zero divisor there. In general, cancellation works if and only if the ring has no zero divisors. Can you see why?

Student: I think so — if ac = bc, that means ac - bc = 0, so (a-b)c = 0. If there are no zero divisors and c isn't zero, then a - b has to be zero.

Tutor: Exactly right. That's the whole trick — zero divisors are the only thing standing between "ac = bc" and "a = b".

Student: Okay, so integral domains let you cancel. Now how does that connect to fields? I always mix those up.

Tutor: Good question. Every field is an integral domain, but not every integral domain is a field. Do you remember what makes a field special?

Student: Every nonzero element has a multiplicative inverse.

Tutor: Right. And having inverses actually explains why fields can't have zero divisors — can you work that out?

Student: Hmm. If ab = 0 and a isn't zero, then a has an inverse, so I could multiply both sides by a⁻¹ and get b = 0. So there's no way to get zero divisors.

Tutor: Nicely done. So fields are automatically integral domains. But the integers show the converse fails — Z is an integral domain, obviously no zero divisors, but 2 has no multiplicative inverse in Z.

Student: Right, 1/2 isn't an integer. So integral domains are like a weaker version of fields — you get cancellation but not necessarily inverses.

Tutor: Exactly. Here's a nice fact to file away: every finite integral domain is automatically a field.

Student: Wait, really? Why would finiteness force inverses to exist?

Tutor: Think about multiplication by a fixed nonzero element a as a function from the ring to itself. Since there are no zero divisors, that function is injective. What does injective plus finite give you?

Student: Injective on a finite set means it's also surjective, so it has to hit 1 somewhere.

Tutor: Precisely — so some element maps to 1 under multiplication by a, meaning a has an inverse. That's why Z/pZ for prime p is a field, but Z itself, being infinite, gets to be a domain without being a field."""


def test_rings_correctly_recovers_on_fresh_held_out_text_teach_911():
    """CORRECT RECOVERY, decisive margin, on genuinely fresh text never seen
    while tuning teach-911's fix. This is the bead's own required
    validation: "Any fix must be validated against a NEW fresh
    blind-authored round, not round5 (round5 is now tuning data for this
    finding, having discovered it)." judson:16.1-rings wins outright here,
    confirming the fix (matrix-example vocabulary fold-in +
    `_DISCOURSE_STOPWORDS` extension) generalizes beyond the one fixture
    that discovered the bug."""
    result = recover_from_lesson_text(RINGS, GRAPH)
    assert result.taught_node_id == "judson:16.1-rings"
    assert result.abstain_reason is None

    raw = score_candidates(RINGS, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:16.1-rings"] == 15
    runner_up = max(s for n, s in scores.items() if n != "judson:16.1-rings")
    assert scores["judson:16.1-rings"] - runner_up >= 7


def test_polynomial_rings_safely_abstains_pre_existing_not_caused_by_teach_911():
    """SAFE ABSTENTION -- "too close to call" between judson:17.1-polynomial-
    rings (8) and judson:16.1-rings (7). Confirmed PRE-EXISTING and NOT
    caused by teach-911's fix: reverting judson:16.1-rings' extraction to
    its pre-fix, git-HEAD state and re-scoring this exact text produces the
    byte-for-byte identical scores (8 and 7) and the same abstention,
    because this text never uses any of the fold-in's new vocabulary
    ("matrices", "matrix", "entries", "noncommutative"). Checked here only
    to confirm the fix introduced no new attractor; the abstention itself
    is out of this bead's scope."""
    result = recover_from_lesson_text(POLYNOMIAL_RINGS, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert "judson:17.1-polynomial-rings" in result.abstain_reason
    assert "judson:16.1-rings" in result.abstain_reason

    raw = score_candidates(POLYNOMIAL_RINGS, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:17.1-polynomial-rings"] == 8
    assert scores["judson:16.1-rings"] == 7


def test_integral_domains_safely_abstains_pre_existing_not_caused_by_teach_911():
    """SAFE ABSTENTION -- teach-57f's already-documented judson:18.2
    attractor pattern (judson:18.2-factorization-in-integral-domains at 11
    vs. the correct judson:16.2-integral-domains-and-fields at 10, tied with
    judson:16.1-rings also at 10) recurring on fresh text, exactly as also
    seen in round5's INTEGRAL_DOMAINS_AND_FIELDS fixture -- not a new
    finding. Confirmed PRE-EXISTING and NOT caused by teach-911's fix: all
    three scores (11, 10, 10) are byte-for-byte identical whether
    judson:16.1-rings' extraction is reverted to its pre-fix, git-HEAD state
    or left as fixed, because this text never uses any of the fold-in's new
    vocabulary either."""
    result = recover_from_lesson_text(INTEGRAL_DOMAINS, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None

    raw = score_candidates(INTEGRAL_DOMAINS, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:18.2-factorization-in-integral-domains"] == 11
    assert scores["judson:16.1-rings"] == 10
    assert scores["judson:16.2-integral-domains-and-fields"] == 10


if __name__ == "__main__":
    test_rings_correctly_recovers_on_fresh_held_out_text_teach_911()
    test_polynomial_rings_safely_abstains_pre_existing_not_caused_by_teach_911()
    test_integral_domains_safely_abstains_pre_existing_not_caused_by_teach_911()
    print("OK: teach-911's fix generalizes to a fresh, blind-authored rings lesson")
