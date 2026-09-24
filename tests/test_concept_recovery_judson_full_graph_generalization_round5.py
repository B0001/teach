"""teach-59u: fresh held-out round, required by this bead's own closing rule
against validating a fix against a round that was already used as tuning
data -- round4 (test_concept_recovery_judson_full_graph_generalization_
round4.py) is exactly the round that surfaced this bead's two recall gaps
(judson:2.1-the-division-algorithm and judson:18.1-fields-of-fractions both
scoring too low, or not appearing at all, against ring/field-family sibling
nodes), and re-scoring round4's own text after tuning the fix against it
would not be a fresh measurement -- it would be validating a fix against the
same data used to diagnose it. This round re-authored fresh dialogues on
five topics -- the two named in the bead, plus three sibling ring/field
topics never used in round4's fixture text, to check the enriched
vocabulary for judson:2.1/judson:18.1 has not created a NEW false-positive
attractor (mirroring judson:18.2's earlier too-large-vocabulary problem from
teach-57f) -- and measured them against the POST-teach-59u code path for the
first time.

All five lesson texts below were produced by five separate, parallel
`Agent` tool calls, each given an explicit no-tool-use, no-repository-
access instruction and told nothing about concept_recovery.py, this bead,
judson:2.1/judson:18.1, or any threshold or mechanism in this module --
only a plain-English topic name and a request to render it as a natural
300-500 word tutor/student dialogue, using the agent's own general
knowledge of abstract algebra, with no reference to any specific textbook.
None of the five agents saw another's output, this module's code, or any
prior round's fixtures.

HONEST RESULT AT THE TIME THIS FILE WAS FIRST WRITTEN (measured once against
the real, unmodified, POST-teach-59u `load_judson_full_graph()` /
`judson_ring_field.json`, via the public `recover_from_lesson_text` /
`score_candidates` entry points only -- no internals of concept_recovery.py
were read to choose or adjust these lesson texts, and no threshold, word
list, or node vocabulary was changed in response to seeing these results):

  correct recoveries:      2 / 5  (DIVISION_ALGORITHM, POLYNOMIAL_RINGS)
  safe abstentions:        3 / 5  (FIELDS_OF_FRACTIONS, RINGS,
                                    INTEGRAL_DOMAINS_AND_FIELDS)
  CONFIDENT WRONG ANSWER:  0 / 5

UPDATE (teach-911): RINGS moved from safe abstention to correct recovery
once judson:16.1-rings' own vocabulary was enriched -- see the RINGS entry
below and test_rings_now_correctly_recovers_after_teach_911_fix. Current
count: 3 / 5 correct recoveries, 2 / 5 safe abstentions, 0 / 5 confident
wrong answers.

This bead's two named gaps, checked directly on this fresh text:

  DIVISION_ALGORITHM:  FULLY RESOLVED. judson:2.1-the-division-algorithm
                          now wins outright -- raw score 11, a decisive
                          margin over the runner-up (judson:17.1-polynomial-
                          rings, 7). Before this bead's fix, this same node
                          scored 6 (tied for 5th) on round4's text and never
                          reached the "close" candidate set at all; the
                          `key_terms`/`definition` edit adding "unique",
                          "existence", "uniqueness" -- words the source
                          theorem itself uses, and that a lesson spending
                          real time on the theorem's existence-and-
                          uniqueness structure naturally uses too -- closes
                          this gap cleanly on genuinely fresh, non-verbatim
                          text.

  FIELDS_OF_FRACTIONS: MEASURABLY IMPROVED, NOT FULLY RESOLVED.
                          judson:18.1-fields-of-fractions now scores 9 and
                          is the runner-up in a two-way "too close to call"
                          abstention against judson:16.1-rings (10) --
                          before this bead's fix, judson:18.1 scored 2 (the
                          match floor is 3) and did not appear in the raw
                          top 5 AT ALL on round4's text. The extraction fix
                          (folding in the field-of-fractions lemma and
                          theorem statements via `extra_statement_ids`,
                          since the section's one term-definition paragraph
                          was a bare cross-reference naming no actual
                          content) took the node from invisible to
                          genuinely competitive -- but on this specific
                          fresh dialogue it still does not clear the margin
                          needed to win outright, because a construction
                          built directly on top of "integral domain" and
                          "ring" vocabulary will always share heavy overlap
                          with those exact sibling nodes. The result is a
                          SAFE ABSTENTION, not a confident wrong answer,
                          which is this system's designed-safe outcome when
                          candidates are this close -- and it is a real,
                          measured improvement over the pre-fix state (where
                          the correct node could not even be named as one of
                          the close candidates).

Three sibling topics, run to check the enriched judson:2.1/judson:18.1
vocabulary has not newly attracted unrelated lessons (the inverse failure
mode, mirroring teach-57f's judson:18.2 over-large-vocabulary problem) --
none show judson:2.1 or judson:18.1 anywhere in their raw top 6, so no such
regression is observed:

  RINGS (topic: definition of a ring, basic examples):  SAFE ABSTENTION when
      this file was first written, via the decisive-margin coverage-gap
      veto -- judson:16.1-rings led raw overlap decisively (12 vs
      runner-up 9) but covered only 26% of its own distinctive vocabulary
      on this text, against judson:3.2-definitions-and-examples' 55%
      coverage of its own (raw overlap 6). That finding, made here, became
      teach-911 (unrelated to and not caused by this bead's own fix --
      neither judson:16.1 nor judson:3.2 were touched by teach-59u, and
      judson:2.1/judson:18.1 did not appear anywhere in this text's raw top
      6). teach-911 has since fixed it by enriching judson:16.1-rings'
      extracted vocabulary from Judson's own "Rings" section worked
      example; see test_rings_now_correctly_recovers_after_teach_911_fix
      below and that bead's own handoff for the fix and its accepted,
      separately-filed residual cost (teach-scx).

  INTEGRAL_DOMAINS_AND_FIELDS (topic: integral domains and fields, zero
      divisors):  SAFE ABSTENTION -- "too close to call" between
      judson:18.2-factorization-in-integral-domains (11) and the correct
      node judson:16.2-integral-domains-and-fields (10). This is exactly
      teach-57f's already-documented judson:18.2 attractor pattern (a
      partial mitigation, not a full fix, per that bead's own closing
      note) recurring on fresh text -- not a new finding. judson:2.1 (score
      6) and judson:18.1 (score 4) do both appear in this text's raw top 6
      -- unsurprising, since zero divisors and cancellation are discussed
      using vocabulary ("divisor", "divide") that legitimately overlaps
      judson:2.1's domain, and this section is judson:18.1's direct
      neighbor in the same chapter -- but neither is named in the abstain
      reason's "too close to call" set, nor anywhere near the two
      contenders (11 and 10 vs 6 and 4), so this is not the kind of new
      attractor pressure this check is watching for.

  POLYNOMIAL_RINGS (topic: polynomial rings, degree, arithmetic):  CORRECT
      RECOVERY -- judson:17.1-polynomial-rings wins outright (raw score 14,
      next-best 8). No attractor pressure from judson:2.1/judson:18.1
      observed (neither appears in the raw top 6).
"""

from teach.concept_recovery import (
    build_vocabulary_index,
    recover_from_lesson_text,
    score_candidates,
)
from teach.judson_algebra_graph import load_judson_full_graph

GRAPH = load_judson_full_graph()
INDEX = build_vocabulary_index(GRAPH)


DIVISION_ALGORITHM = """Tutor: So today we're tackling the division algorithm. If I hand you two integers, say 47 and 5, what does "dividing" them even mean to you?

Student: Um, 47 divided by 5 is 9.4?

Tutor: Right, that's the real number answer. But in number theory we usually want to stay inside the integers. We want to write 47 as 5 times something, plus some leftover.

Student: Oh, like long division from grade school. 5 goes into 47 nine times, that's 45, and 2 left over.

Tutor: Exactly. So we write 47 = 5·9 + 2. That's the division algorithm in a nutshell. Formally: given integers a and b, with b positive, there exist unique integers q and r such that a = bq + r, and 0 ≤ r < b.

Student: Wait, why does r have to be less than b? Couldn't I just say 47 = 5·8 + 7?

Tutor: You could write that equation, sure, it's true. But 7 is bigger than 5 — it still has a whole copy of 5 inside it. The remainder is supposed to be what's left after you've pulled out as many full b's as possible. If r is allowed to be ≥ b, you haven't finished dividing.

Student: Okay that makes sense. So the "0 ≤ r < b" condition is really what pins down a single correct answer.

Tutor: That's the uniqueness part, yes. Existence says you can always find such q and r. Uniqueness says there's only one pair that works. Let's think about why existence is true. Take all the multiples of b: ..., -2b, -b, 0, b, 2b, 3b, .... Where does a land?

Student: Somewhere between two consecutive multiples?

Tutor: Right, unless it lands exactly on one. So there's some multiple qb that's the largest multiple of b not exceeding a. Then r = a - qb, and by construction 0 ≤ r < b.

Student: That's a slick argument — no actual division needed, just "find the biggest multiple underneath."

Tutor: Exactly, it's really an argument about the well-ordering of the naturals. Now, uniqueness — suppose we had two representations, a = bq1 + r1 = bq2 + r2, both remainders in [0,b). What happens if you subtract them?

Student: You get b(q1 - q2) = r2 - r1.

Tutor: Good. Now bound the right side.

Student: Since both remainders are between 0 and b, their difference is strictly between -b and b in absolute value... so |r2 - r1| < b.

Tutor: And the left side is a multiple of b. What multiple of b has absolute value less than b?

Student: Only zero.

Tutor: So r1 = r2, and then q1 = q2 falls out immediately. That's uniqueness.

Student: What about negative a, like -47 divided by 5?

Tutor: Same rule applies — remainder must stay in [0,5). So -47 = 5·(-10) + 3, not -47 = 5·(-9) + (-2), even though that's tempting.

Student: Right, because -2 isn't allowed as a remainder. Got it, this is cleaner than I expected."""

FIELDS_OF_FRACTIONS = """Tutor: So we've built the integers from the natural numbers, and now I want to ask: how do you build the rationals from the integers? Not just "put a fraction bar between them" — actually construct them.

Student: Isn't that just... division? Like 3/4 is 3 divided by 4?

Tutor: Right, but division isn't always defined in the integers — 3 divided by 4 has no answer *in* ℤ. So we build a new set whose elements *are* those unrealized quotients. Here's the trick: start with pairs. Take D × (D \\ {0}), where D is our integral domain, and think of the pair (a, b) as standing for "a/b."

Student: Okay, so (3,4) means 3/4.

Tutor: Exactly. But there's a problem already — what pair represents the same fraction as (3,4)?

Student: (6,8), obviously. Cross-multiplication: 3·8 = 4·6.

Tutor: You just invented the equivalence relation. We define (a,b) ~ (c,d) iff ad = bc. Why do you think we need D to be an *integral domain* — no zero divisors — for this to work cleanly?

Student: Hmm... I guess because if ad = bc could happen weirdly, the relation might not behave right?

Tutor: Close. The real reason shows up when you check transitivity. Suppose (a,b) ~ (c,d) and (c,d) ~ (e,f). You get ad=bc and cf=de. Multiply things around and you eventually need to cancel a factor of c to conclude af = be. If c could be a zero divisor times something, that cancellation fails.

Student: So no zero divisors means you can always cancel nonzero elements.

Tutor: Precisely — that's the whole reason "integral domain" is the hypothesis instead of just "commutative ring." Now, once you have equivalence classes [a,b], how would you define addition?

Student: By analogy with fractions... a/b + c/d = (ad+bc)/bd?

Tutor: Good instinct. So [a,b] + [c,d] := [ad+bc, bd]. And multiplication?

Student: [a,b]·[c,d] = [ac, bd].

Tutor: Now here's the subtle part students always trip on: we defined these operations using *representatives* a,b,c,d. Why isn't that automatically legitimate?

Student: ...because a class has infinitely many representatives, and maybe you'd get a different answer with a different representative?

Tutor: Exactly the worry. So there's real work — "well-definedness" — showing that if (a,b)~(a',b') and (c,d)~(c',d'), the sums and products land in the same class. It's routine but it's not optional.

Student: And that's the field of fractions?

Tutor: That's it — call it Frac(D). D embeds into it via a ↦ [a,1], every nonzero element has an inverse [b,a] for [a,b], and when D = ℤ, Frac(D) is literally ℚ.

Student: So ℚ isn't special — it's just what happens when you run this machine on ℤ.

Tutor: Now you're thinking like an algebraist."""

RINGS = """Tutor: So we've done groups. Today's ring, which is basically "what if I have two operations instead of one, and they play nice together." The go-to example is the integers with plus and times.

Student: Okay, so a ring is a group with extra steps?

Tutor: Sort of. It's an abelian group under addition, plus a multiplication that's associative, plus distributive laws tying them together. Let's be precise. A ring R has addition making it an abelian group — so there's a zero, every element has an additive inverse, addition commutes. Then multiplication is associative, and it distributes over addition both ways: a(b+c) = ab + ac, and (a+b)c = ac + bc.

Student: Why both ways? Doesn't multiplication commute anyway?

Tutor: Not necessarily — that's the catch. Some rings are commutative, like the integers, but plenty aren't. You need both distributive laws stated separately because you can't assume ab = ba.

Student: Give me an example where it's not commutative.

Tutor: Matrices. Take 2x2 matrices with real entries. Addition is entrywise, totally abelian group there. Multiplication is matrix multiplication — associative, distributes over addition, but AB usually isn't BA.

Student: Right, I remember that from linear algebra, order matters. So matrices form a ring?

Tutor: Exactly, denoted M_2(R). It even has a multiplicative identity, the identity matrix, though not every ring needs one — we call rings with a 1 "rings with unity" or "unital rings," depending on the textbook.

Student: Does the integers have a 1?

Tutor: Sure, plain old 1. And it's commutative, so Z is our friendliest example: abelian group under addition, multiplication is associative and commutative, distributes over addition, has an identity. What it doesn't have is multiplicative inverses for most elements — 2 has no inverse in Z. That's what keeps it from being a field.

Student: Okay so a field is a ring where everything nonzero is invertible?

Tutor: You're ahead of me, but yes, that's the idea, we'll formalize it later. For now, one more key example: polynomial rings. Take R[x], polynomials with real coefficients.

Student: Like x^2 + 3x + 1?

Tutor: Right. Add them coefficient-wise, multiply them by the usual expand-and-collect-terms process. Turns out that's a ring too — abelian under addition obviously, and multiplication of polynomials is associative and distributes, you can check that from how you learned to FOIL things out in high school.

Student: Wait, is it commutative? x times y is y times x for polynomials?

Tutor: For a single variable, yes, R[x] is commutative, because multiplying real coefficients commutes. Where it gets subtle is if your coefficients themselves come from a noncommutative ring, like matrices — then things change. But for now, keep it simple: R[x] over the reals is commutative with identity 1.

Student: So rings are everywhere — numbers, matrices, polynomials. What's the point of the abstract definition?

Tutor: Once you prove something using only the ring axioms, it's true for all of them at once — integers, matrices, polynomials, whatever comes next. That's the payoff."""

INTEGRAL_DOMAINS_AND_FIELDS = """Tutor: Okay, we've been talking about rings — sets with addition and multiplication that play nice together. Today I want to push on one weird thing that can happen: multiplying two nonzero things and getting zero.

Student: Wait, that's possible? Isn't that like saying 2 times 3 equals 0?

Tutor: Not in the integers, no. But try this: work in Z mod 6. What's 2 times 3?

Student: 6... which is 0 mod 6. Oh. So 2 and 3 are both nonzero in that ring, but their product is zero.

Tutor: Exactly. We call 2 and 3 "zero divisors" in that ring. A nonzero element a is a zero divisor if there's some nonzero b with ab = 0.

Student: So the integers don't have that problem?

Tutor: Right — if two integers multiply to zero, one of them has to already be zero. That property, "no zero divisors," combined with being a commutative ring with 1 where 1 ≠ 0, is called an integral domain.

Student: Why does it matter, though? Like, why do we care if zero divisors exist?

Tutor: Because it wrecks cancellation. In an integral domain, if ab = ac and a isn't zero, you can cancel and conclude b = c. Try that in Z mod 6: does 2·1 = 2·4?

Student: 2 is 2, and 2 times 4 is 8, which is 2 mod 6. So yes, 2·1 = 2·4.

Tutor: Right. But 1 ≠ 4 mod 6. So cancellation fails completely.

Student: Got it, that's because 2 and... what would you cancel with...

Tutor: The obstruction is basically 3, since 2·3 = 0. Whenever zero divisors are lurking, cancellation can break.

Student: Okay so integral domains are rings without that problem. What's a field then? I always mix these up.

Tutor: A field is stronger — every nonzero element has a multiplicative inverse. So you can not just cancel, but actually divide.

Student: Isn't that automatic from having no zero divisors?

Tutor: Good question, and no — not in general. Z is an integral domain, but 2 has no inverse in Z; there's no integer x with 2x = 1.

Student: Right, of course. So Z is a domain but not a field.

Tutor: Exactly. But here's a nice fact: every field IS an integral domain. If a field had zero divisors, say ab = 0 with a ≠ 0, you could multiply both sides by a's inverse and get b = 0, contradiction.

Student: Oh that's clean. So fields are a special, nicer kind of integral domain.

Tutor: Yes. And finite integral domains are automatically fields — that's a fun theorem for later. For now, let's classify: is Z mod 5 a field?

Student: 5 is prime, so... every nonzero residue should have an inverse? Let me check 2. 2 times 3 is 6, which is 1 mod 5. So 2 inverse is 3.

Tutor: Nice. And Z mod 6?

Student: Not a field, since we found 2 and 3 are zero divisors — they can't have inverses if their product is zero.

Tutor: Perfect intuition. Zero divisors and inverses can't coexist for the same element."""

POLYNOMIAL_RINGS = """Tutor: So today we're building a new ring out of an old one. Let's start with something familiar — the integers, ℤ. I want to form ℤ[x], the polynomials in x with integer coefficients.

Student: Okay, that's just like high school polynomials, right? Things like 3x² + 2x - 1?

Tutor: Exactly that kind of expression, but let's be careful about what it actually *is*. Formally, an element of ℤ[x] is a sequence of coefficients, almost all zero: a₀, a₁, a₂, ... with each aᵢ in ℤ. We just write it as a₀ + a₁x + a₂x² + ... The x is really a placeholder, a bookkeeping device for the position.

Student: Why not just say it's "an expression with a variable"? Seems more natural.

Tutor: You can think of it that way informally, but the sequence definition is what lets us define addition and multiplication rigorously, without worrying about what x "means." Addition is coordinate-wise: you just add corresponding coefficients.

Student: So (2x² + x + 1) + (x² - 3x + 5) would be... 3x² - 2x + 6?

Tutor: Right. Now multiplication is trickier — how would you multiply x² by x³?

Student: x⁵, since exponents add.

Tutor: Good instinct. In general, if p(x) = Σ aᵢxⁱ and q(x) = Σ bⱼxʲ, the product's coefficient of xᵏ is Σ aᵢbⱼ where i+j=k. It's a convolution of the coefficient sequences.

Student: That sounds complicated but I guess it's just "distribute everything and collect like terms."

Tutor: Exactly — that formula is just a precise way of saying that.

Student: What about degree? Is that just the highest power?

Tutor: The highest power with a nonzero coefficient, yes. So deg(3x² + 1) = 2.

Student: What's the degree of a constant, like 5?

Tutor: Degree 0, since 5 = 5x⁰.

Student: And the zero polynomial?

Tutor: Convention varies — usually we say its degree is -∞, or leave it undefined, precisely because it breaks the nice formulas otherwise.

Student: Wait, here's something confusing me. If R isn't a field — say R = ℤ/4ℤ — can degrees still add normally when you multiply?

Tutor: Great question, and no, not always! Take R = ℤ/4ℤ, and consider p(x) = 2x. Then p(x)² = 4x² = 0. The degree collapsed entirely, because 2·2 = 0 in ℤ/4ℤ — we have zero divisors.

Student: So deg(pq) ≤ deg(p) + deg(q), not always equal?

Tutor: Precisely. Equality is guaranteed only when R is an integral domain — no zero divisors — because then the leading coefficients multiply to something nonzero.

Student: That's a nice reason to care about integral domains.

Tutor: It's actually one of the first payoffs. R[x] itself turns out to be an integral domain whenever R is."""


def test_division_algorithm_now_correctly_recovers_after_teach_59u_fix():
    """CORRECT RECOVERY, decisive margin. Before this bead's fix, judson:2.1
    scored 6 (tied for 5th) on round4's text and never reached the "close"
    candidate set. On this fresh, blind-authored text it now wins outright."""
    result = recover_from_lesson_text(DIVISION_ALGORITHM, GRAPH)
    assert result.taught_node_id == "judson:2.1-the-division-algorithm"
    assert result.abstain_reason is None

    raw = score_candidates(DIVISION_ALGORITHM, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:2.1-the-division-algorithm"] == 11
    runner_up = max(s for n, s in scores.items() if n != "judson:2.1-the-division-algorithm")
    assert scores["judson:2.1-the-division-algorithm"] - runner_up >= 4


def test_fields_of_fractions_measurably_improved_still_safely_abstains():
    """MEASURABLY IMPROVED, NOT FULLY RESOLVED. Before this bead's fix,
    judson:18.1 scored 2 (below the match floor) and did not appear in the
    raw top 5 at all. After the extraction fix, it scores 9 and is the
    named runner-up in a two-way "too close to call" abstention against
    judson:16.1-rings (10) -- a real, measured improvement (invisible ->
    competitive) that still does not fully close the gap on this
    particular fresh text. The outcome is a SAFE ABSTENTION, not a
    confident wrong answer."""
    result = recover_from_lesson_text(FIELDS_OF_FRACTIONS, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert "too close to call" in result.abstain_reason
    assert "judson:18.1-fields-of-fractions" in result.abstain_reason

    raw = score_candidates(FIELDS_OF_FRACTIONS, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:18.1-fields-of-fractions"] == 9
    top5_ids = {c.node_id for c in raw[:5]}
    assert "judson:18.1-fields-of-fractions" in top5_ids


def test_rings_now_correctly_recovers_after_teach_911_fix():
    """CORRECT RECOVERY, as of teach-911 -- was a SAFE ABSTENTION when this
    test was first written (judson:16.1-rings led raw overlap decisively,
    12 vs runner-up 9, but covered only 26% of its own distinctive
    vocabulary on this text, tripping the decisive-margin coverage-gap veto
    against judson:3.2-definitions-and-examples' 55% self-coverage -- see
    teach-911 itself, filed directly against this test's own finding).

    teach-911's fix folded Judson's own "Rings" section worked example (2x2
    real matrices under matrix addition/multiplication, noncommutative) into
    judson:16.1-rings' extracted definition/terms (see EXTRA_STATEMENT_IDS in
    extract_judson_ring_field.py), plus extended `_DISCOURSE_STOPWORDS` in
    concept_recovery.py with five more closed-class hedges the folded-in
    example's prose introduces as a side effect ("since", "usual",
    "usually", "case", "neither") so they don't count as spurious vocabulary
    coverage. That takes judson:16.1-rings' raw score on this text from 12
    to 17 and its own-vocabulary coverage well past the veto's threshold, so
    it now wins outright with no abstention -- confirmed here unrelated to
    and not caused by any change to judson:2.1/judson:18.1 (this bead did
    not touch either node; neither appears anywhere near the top of this
    text's candidates).

    "form" -- one of the words the folded-in example's framing sentence
    ("matrices... form a ring under the usual operations") introduces -- was
    deliberately NOT added to `_DISCOURSE_STOPWORDS`: doing so was measured
    to turn a different, unrelated safe abstention into a CONFIDENT WRONG
    ANSWER elsewhere (test_maximal_prime_ideals_abstains_via_teach_hpa_gate_
    no_regression_vs_ungated), which this repo's own standard ranks strictly
    worse than the recall gap this bead is fixing. Leaving "form" in scoring
    had a real, measured cost, though: it narrowed the margin that used to
    protect two OTHER lessons squarely about different topics
    (judson:3.3-subgroups, judson:21.1-extension-fields) from
    judson:16.1-rings' now-larger vocabulary, flipping their own correct
    recoveries into safe abstentions -- filed forward as teach-scx.

    teach-scx has since closed that gap with a narrower fix than a global
    stopword: `EXCERPT_EDITS` in extract_judson_ring_field.py elides just
    the one word "form" from the folded-in matrix example's text (marked
    with an ellipsis, everything else Judson wrote there untouched), so it
    no longer counts toward judson:16.1-rings' score anywhere, while
    "matrices"/"matrix"/"entries"/"noncommutative" still do. That drops
    this test's own raw score by exactly one (17 -> 16, still a decisive,
    unambiguous win) and restores judson:3.3-subgroups' and
    judson:21.1-extension-fields' correct recoveries (see round3's
    test_subgroups_correctly_recovers and round4's
    test_extension_fields_correctly_recovers) without reopening the
    maximal/prime-ideals abstention "form" was protecting in the first
    place -- "form" is still there in every OTHER node's vocabulary,
    including judson:18.2's; only this one node, this one word, this one
    source block was touched."""
    result = recover_from_lesson_text(RINGS, GRAPH)
    assert result.taught_node_id == "judson:16.1-rings"
    assert result.abstain_reason is None

    raw = score_candidates(RINGS, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:16.1-rings"] == 16
    runner_up = max(s for n, s in scores.items() if n != "judson:16.1-rings")
    assert scores["judson:16.1-rings"] - runner_up >= 7

    assert scores.get("judson:2.1-the-division-algorithm", 0) <= 4
    assert scores.get("judson:18.1-fields-of-fractions", 0) <= 5


def test_integral_domains_and_fields_safely_abstains_no_regression():
    """SAFE ABSTENTION -- this is teach-57f's already-documented
    judson:18.2 attractor pattern recurring on fresh text (judson:18.2 at
    11 vs the correct judson:16.2-integral-domains-and-fields at 10, "too
    close to call"), not a new finding. judson:2.1 and judson:18.1 do
    appear in the raw top 6 (scores 6 and 4 -- unsurprising overlap with
    "divisor" vocabulary and chapter-adjacency), but nowhere near the two
    actual contenders and not named in the abstain reason, so this bead's
    fix did not introduce a new attractor here."""
    result = recover_from_lesson_text(INTEGRAL_DOMAINS_AND_FIELDS, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert "judson:2.1-the-division-algorithm" not in result.abstain_reason
    assert "judson:18.1-fields-of-fractions" not in result.abstain_reason

    raw = score_candidates(INTEGRAL_DOMAINS_AND_FIELDS, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores.get("judson:2.1-the-division-algorithm", 0) <= 6
    assert scores.get("judson:18.1-fields-of-fractions", 0) <= 4


def test_polynomial_rings_correctly_recovers_no_regression():
    """CORRECT RECOVERY, decisive margin. Checked here only to confirm this
    bead's fix did not introduce a new attractor -- judson:2.1/judson:18.1
    do not appear in the raw top 6."""
    result = recover_from_lesson_text(POLYNOMIAL_RINGS, GRAPH)
    assert result.taught_node_id == "judson:17.1-polynomial-rings"

    raw = score_candidates(POLYNOMIAL_RINGS, INDEX)
    top6_ids = {c.node_id for c in raw[:6]}
    assert "judson:2.1-the-division-algorithm" not in top6_ids
    assert "judson:18.1-fields-of-fractions" not in top6_ids
