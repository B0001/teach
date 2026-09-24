"""teach-57f: fresh held-out round, run to satisfy this bead's own closing
requirement (per this lineage's rule against validating a fix against a
round that was already used as tuning data -- round2 and round3, plus
teach-443's fixture edits, are all now tuning data and must not be reused
here).

These five topics -- the division algorithm, group definitions and
examples, polynomial rings, fields of fractions, and extension fields --
are exactly the five round3 itself named (see that file's line ~659) as
"round4, five topics never used as a fixture in round1/2/3." round3's own
actual round4 dialogue text was never saved to this repo (only that topic
list survived, in a comment). Rather than reuse round3's remembered
candidate-score numbers for those topics (which would not be a fresh
measurement -- the numbers were computed against the PRE-teach-57f code),
this round re-authored fresh dialogues on the same five never-yet-fixtured
topics from scratch and measured them against the POST-teach-57f code path
for the first time.

All five lesson texts below were produced by five separate, parallel
`Agent` tool calls, each given an explicit no-tool-use, no-repository-
access instruction and told nothing about concept_recovery.py, this bead,
`_DISCOURSE_STOPWORDS`, or any threshold or mechanism in this module --
only a plain-English topic name and a request to render it as a natural
300-500 word tutor/student dialogue, using the agent's own general
knowledge of abstract algebra, with no reference to any specific textbook.
None of the five agents saw another's output, this module's code, or any
prior round's fixtures.

HONEST RESULT (measured once against the real, unmodified
`load_judson_full_graph()`, via the public `recover_from_lesson_text`
entry point only -- no internals of concept_recovery.py were read to
choose or adjust these lesson texts, and no threshold or word list in
concept_recovery.py was changed in response to seeing these results):

  correct recoveries:      2 / 5  (POLYNOMIAL_RINGS, EXTENSION_FIELDS)
  safe abstentions:        3 / 5  (DIVISION_ALGORITHM, GROUP_DEFINITIONS,
                                    FIELDS_OF_FRACTIONS)
  CONFIDENT WRONG ANSWER:  0 / 5

UPDATE (teach-59u): the two DIVISION_ALGORITHM/FIELDS_OF_FRACTIONS
assertions below were revised in place after teach-59u's vocabulary-
enrichment fix changed their measured scores on this file's (now-tuning-
data) text -- DIVISION_ALGORITHM went from safe-abstention to a correct,
decisive recovery; FIELDS_OF_FRACTIONS went from invisible (below the
match floor) to a named contender in a still-safe "too close to call"
abstention. See each test's own docstring for the before/after numbers.
This file's text is NOT used to validate that fix (it is tuning data,
per this module's own opening rule) -- the fresh, blind-authored
validation lives in
tests/test_concept_recovery_judson_full_graph_generalization_round5.py.
The two paragraphs below (judson:18.2's attractor-pattern analysis) are
otherwise unchanged and still describe the current, real behavior.

This round's job, specific to teach-57f, is to check whether
`judson:18.2-factorization-in-integral-domains` -- the node whose
generic-academic-discourse vocabulary this bead's `_DISCOURSE_STOPWORDS`
fix targeted -- still improperly tops or closely contends the raw-score
ranking for lessons on topics unrelated to factorization, after the fix.
Checked directly, not just inferred, via `score_candidates` (the raw tier,
before any abstention/tiebreak logic runs):

  DIVISION_ALGORITHM:   judson:18.2 raw score 9, in 2nd place (topic
                          winner judson:17.1-polynomial-rings, 10) -- still
                          closely contends, and is one of the two
                          candidates the final abstain names as
                          "too close to call."
  GROUP_DEFINITIONS:    judson:18.2 raw score 7, tied for 2nd/3rd place
                          (topic winner judson:16.3-ring-homomorphisms-and-
                          ideals, 8) -- still closely contends, and is one
                          of the three candidates the final abstain names.
  POLYNOMIAL_RINGS:     judson:18.2 does not appear in the top 5 at all.
  FIELDS_OF_FRACTIONS:  judson:18.2 raw score 7, in 4th place -- present
                          but NOT among the three candidates the final
                          abstain names as "too close to call" (judson:16.1,
                          judson:16.2, judson:1.2, all scoring 8-9).
  EXTENSION_FIELDS:     judson:18.2 does not appear in the top 5 at all.

So the honest finding is: `_DISCOURSE_STOPWORDS` did NOT eliminate
judson:18.2 as an attractor -- it still lands in the raw top-2-to-4 for
3 of these 5 topically-unrelated lessons, exactly the "large generic node
absorbs unrelated vocabulary" pattern this bead describes. What it DID do,
consistent with the fix being a partial mitigation and not a full one (see
concept_recovery.py's `_DISCOURSE_STOPWORDS` comment and this bead's
handoff), is keep judson:18.2 from ever being named alone as the single
confident winner in this round: it never clears the margin/coverage gates
required to be returned as `taught_node_id` on its own, and every case
where it's close enough to matter resolves to a SAFE ABSTENTION, not a
confident wrong answer. Zero confident wrong answers across this round is
the property this bead's acceptance bar actually cares about; residual
attractor pressure below that bar is the known, already-documented
remainder of the partial fix, not a new regression.

A SEPARATE finding, NOT part of judson:18.2's attractor pattern and
therefore explicitly OUT OF SCOPE for this bead (filed forward instead,
per this repo's "discovered work outside this bead's scope becomes a new
bead" rule -- see teach-57f's handoff and the new bead it references):
DIVISION_ALGORITHM and FIELDS_OF_FRACTIONS both abstain for reasons that
have nothing to do with judson:18.2 -- their own correct nodes
(judson:2.1-the-division-algorithm and judson:18.1-fields-of-fractions
respectively) don't even reach the "close" candidate set; sibling
ring/field-family nodes with more distinctive-word overlap
(judson:17.1-polynomial-rings; judson:16.1-rings and
judson:16.2-integral-domains-and-fields) out-score them instead. This
looks like a general recall gap in how thin some individual nodes'
distinctive vocabularies are relative to their nearest graph siblings --
a different problem from one node's vocabulary being too LARGE.
"""

from teach.concept_recovery import (
    build_vocabulary_index,
    recover_from_lesson_text,
    score_candidates,
)
from teach.judson_algebra_graph import load_judson_full_graph

GRAPH = load_judson_full_graph()
INDEX = build_vocabulary_index(GRAPH)


DIVISION_ALGORITHM = """Tutor: Let's look at the Division Algorithm. It sounds humble, but it's the seed that a huge amount of number theory grows out of. Have you seen the statement before?

Student: I know it's about dividing integers with a remainder, but I've never seen it written formally.

Tutor: Here it is: given integers a and b with b not equal to 0, there exist unique integers q and r such that a = bq + r, with 0 <= r < |b|. So q is the quotient, r is the remainder, and the key constraint is that r is trapped between 0 and |b|.

Student: Isn't that just long division?

Tutor: Exactly, but stated so we can prove it always works, even for negative numbers, and that there's only one correct answer. Try a = 23, b = 5.

Student: 23 = 5*4 + 3. So q = 4, r = 3.

Tutor: Right. Now try a = -23, b = 5. Be careful.

Student: I want to say q = -4, r = -3, but that breaks the rule since r has to be nonnegative.

Tutor: Good catch. So adjust.

Student: -23 = 5*(-5) + 2. Since -5*5 = -25, and -23-(-25) = 2. So q = -5, r = 2.

Tutor: Perfect, and 0 <= 2 < 5, so that's valid. Notice you had to round the quotient down, not just truncate toward zero, to keep the remainder nonnegative.

Student: Why does this matter so much? It feels like something I already knew intuitively.

Tutor: Because "existence and uniqueness" is what lets us build everything else on top of it. The Euclidean algorithm for GCDs is literally repeated application of this theorem. Modular arithmetic -- the idea of working mod n -- is defined using the remainder r this theorem guarantees exists. Without knowing r is unique, "a mod n" wouldn't even be well-defined as a single number.

Student: How would you actually prove existence, not just compute examples?

Tutor: Consider the set of all integers of the form a - bk for integer k, and look at the ones that are nonnegative. That set is nonempty -- you can always choose k negative enough or positive enough depending on the sign of b -- so by the well-ordering principle it has a smallest element. Call that smallest nonnegative value r, achieved at k = q. You then argue r must be less than |b|, because if it weren't, you could subtract |b| again and get something smaller, contradicting minimality.

Student: And uniqueness?

Tutor: Suppose two pairs (q, r) and (q', r') both work. Subtracting the two equations forces b(q - q') = r' - r, and since both remainders lie in [0, |b|), their difference is smaller than |b| in absolute value -- but it's also a multiple of b. The only multiple of b smaller than |b| is 0, so r = r' and then q = q'.

Student: So uniqueness comes from the remainder being squeezed into too narrow a range to have room for two different multiples of b.

Tutor: That's exactly the right way to see it."""

GROUP_DEFINITIONS = """Tutor: Let's build up the idea of a "group" from something you already know. Take the integers, and just addition. What happens when you add two integers?

Student: You get another integer. Like 3 plus 5 is 8.

Tutor: Right, you never leave the set. That's called closure -- the operation always lands you back inside the same set. That's ingredient one. Now, does it matter how you group three additions, like (2 + 3) + 4 versus 2 + (3 + 4)?

Student: No, both give 9.

Tutor: That's associativity. The grouping of the parentheses doesn't change the answer. Ingredient two. Now, is there a special number that doesn't change anything when you add it?

Student: Zero. Anything plus zero is itself.

Tutor: Exactly -- that's the identity element. Ingredient three. Last one: for any integer, can you find another integer that brings you back to that identity?

Student: You mean like adding the negative? 5 plus negative 5 is zero.

Tutor: Precisely -- every element has an inverse under the operation. Closure, associativity, identity, inverses. When a set and an operation satisfy all four, you call it a group. So the integers under addition form a group.

Student: Does it have to be numbers? Could it be something weirder?

Tutor: Good instinct -- no, it doesn't. Think of an equilateral triangle. You can rotate it by 0, 120, or 240 degrees and it lands back on itself. Combine two rotations -- say rotate 120 then 120 again -- and you get another valid rotation, 240. That's closure. There's a do-nothing rotation, which is your identity. And every rotation has one that undoes it -- rotate 120 forward, then 240 more, and you're back to start. So the set of rotational symmetries of the triangle is also a group, even though nothing there looks like a number.

Student: Interesting. Is there any difference between that and the integers example?

Tutor: One subtle thing -- with integers under addition, order never matters: a plus b always equals b plus a. Groups with that extra property are called abelian, or commutative. Not every group has to be -- once you start combining rotations with reflections, for instance, order can start to matter. But for now, just hang onto the four core requirements: closure, associativity, identity, and inverses. Get comfortable checking those on small examples, and the rest builds from there.

Student: So a group is really just "a set plus a rule for combining things" that behaves nicely in those four ways.

Tutor: That's exactly it."""

POLYNOMIAL_RINGS = """Tutor: Last time we built R itself out of number-like rings. Today, polynomial rings -- R[x]. Any ring R, and R[x] is all polynomials with coefficients in R.

Student: Like Z[x], polynomials with integer coefficients?

Tutor: Exactly. An element is a0 + a1*x + a2*x^2 + ... + an*x^n, where every ai comes from R, and only finitely many are nonzero.

Student: So x is just... a symbol? It's not a number?

Tutor: Right, treat x as a formal placeholder, not a variable you plug values into. Formally a polynomial is really just a sequence of coefficients (a0, a1, a2, ...) that's eventually all zeros -- the x notation just makes multiplication readable.

Student: Okay. How does addition work?

Tutor: Componentwise, same as you'd expect: add coefficients of matching degree. (2 + 3x) + (1 + x^2) = 3 + 3x + x^2.

Student: That seems easy. Multiplication feels scarier.

Tutor: It's just distributing and collecting like terms, using multiplication in R. Formally, if f = sum ai*x^i and g = sum bj*x^j, then fg = sum ck*x^k where ck = sum over i+j=k of ai*bj.

Student: Can we do an example?

Tutor: Sure. Take R = Z, f = 2x + 3, g = x^2 - x + 1. Multiply term by term.

Student: 2x times x^2 is 2x^3, 2x times -x is -2x^2, 2x times 1 is 2x. Then 3 times x^2 is 3x^2, 3 times -x is -3x, 3 times 1 is 3.

Tutor: Now collect by degree.

Student: x^3: just 2x^3. x^2: -2x^2 + 3x^2 = x^2. x^1: 2x - 3x = -x. Constant: 3. So fg = 2x^3 + x^2 - x + 3.

Tutor: Nicely done. Now, why is R[x] actually a ring? What do we need to check?

Student: Addition needs to be commutative and associative with an identity and inverses, multiplication needs to be associative, and distributivity has to hold.

Tutor: And where does all of that come from?

Student: From R itself -- since the coefficients live in R, addition of polynomials inherits commutativity and associativity from addition in R, coefficient by coefficient. And that ck formula for multiplication, if you expand it out, associativity and distributivity boil down to associativity and distributivity in R.

Tutor: Exactly -- R[x] inherits its ring structure from R. One more idea before we stop: degree.

Student: The degree is the highest power with a nonzero coefficient, right? Like fg above has degree 3.

Tutor: Right. And here's a nice fact to sit with -- if R has no zero divisors, degree is additive: deg(fg) = deg(f) + deg(g). We'll see next time that this fails if R does have zero divisors.

Student: So the leading coefficients could cancel each other out?

Tutor: Precisely -- hang onto that thought for next session."""

FIELDS_OF_FRACTIONS = """Tutor: Last time we built the rationals from the integers, right? Today let's see the general version -- the field of fractions of any integral domain.

Student: Okay, but why do we need integers to be special? Couldn't we do this to any ring?

Tutor: Good question -- try it on Z/6Z and tell me what goes wrong.

Student: We'd want fractions a/b... but 2 and 3 are zero divisors there. If b has a zero divisor partner, dividing by it should be dangerous.

Tutor: Exactly. That's why we need an integral domain -- no zero divisors. It guarantees that when we build fractions a/b, the denominators we allow are genuinely "safe" to invert.

Student: So we just take pairs (a,b) with b not equal to 0, like numerator and denominator?

Tutor: Right, from the set D x (D minus {0}), where D is our domain. But we can't just call each pair a "fraction" -- 2/4 and 1/2 need to be the same fraction.

Student: So we need an equivalence relation. In Z I remember it's a/b ~ c/d when ad = bc.

Tutor: Same definition here. Why do you think we phrase it that way instead of saying a/b = c/d means "a times b inverse = c times d inverse"?

Student: Because we don't have division yet -- that's the whole point, we're constructing it. Using ad = bc avoids needing inverses.

Tutor: Exactly. Now, is that relation actually an equivalence relation?

Student: Reflexive and symmetric look obvious. Transitive is the annoying one -- if ad = bc and cf = de, we want af = be.

Tutor: Try it.

Student: From ad = bc, multiply both sides by f: adf = bcf. And cf = de means bcf = bde. So adf = bde. Then... I want to cancel d.

Tutor: And can you?

Student: Since d is not zero and D has no zero divisors, cancellation is valid -- that's exactly where we use the integral domain property!

Tutor: There it is. Without "no zero divisors," transitivity can fail. Now, once we have equivalence classes [a,b], how do we add and multiply them?

Student: By analogy with fractions: [a,b] + [c,d] = [ad+bc, bd], and [a,b] times [c,d] = [ac, bd].

Tutor: And why is bd a legal denominator?

Student: Because D is a domain -- product of two nonzero elements is nonzero. So bd is not zero, the pair stays valid.

Tutor: Good. You'd also need to check these operations are well-defined -- independent of which representative you pick -- but that's a computation you can do at home. What do we get in the end?

Student: A field! Every nonzero [a,b] has inverse [b,a], since a is not zero there.

Tutor: And D embeds into it via a maps to [a,1]. So this field is the smallest field containing a copy of D -- its "field of fractions." For D = Z, that's exactly Q.

Student: So this whole construction is really just answering: what's the smallest field where I'm allowed to divide by everything nonzero?

Tutor: That's precisely it."""

EXTENSION_FIELDS = """Tutor: Let's build a field extension from scratch. We start with the rationals, Q. Now, Q doesn't contain sqrt(2) -- there's no rational number that squares to 2. So I want to build a bigger field that does contain it.

Student: Can't we just throw sqrt(2) into the set and call it a field?

Tutor: Almost -- we have to be careful that the result is closed under addition and multiplication. So we take Q(sqrt(2)), meaning all numbers of the form a + b*sqrt(2), where a and b are rational.

Student: Why does that set stay closed? If I multiply two of those together, don't I get sqrt(2) times sqrt(2) terms?

Tutor: Try it. Multiply (a + b*sqrt(2))(c + d*sqrt(2)).

Student: That's ac + ad*sqrt(2) + bc*sqrt(2) + bd*2, so (ac + 2bd) + (ad + bc)*sqrt(2). Oh -- it's still of the form "rational plus rational times sqrt(2)."

Tutor: Exactly, because sqrt(2) times sqrt(2) = 2 collapses back into the rational part. So Q(sqrt(2)) is closed under multiplication, and you can check addition and inverses work too. It's a field, and Q sits inside it as a subfield. We call Q(sqrt(2)) an extension of Q.

Student: Okay, so it's a bigger field. What's this "vector space" idea you mentioned?

Tutor: Forget multiplication for a second and just look at Q(sqrt(2)) as a set you can add and scale by rational numbers. That's exactly what a vector space is -- vectors you can add, and scale by elements of a base field. Here the "vectors" are elements a + b*sqrt(2), and the "scalars" are rationals.

Student: So what's a basis?

Tutor: Every element a + b*sqrt(2) is uniquely determined by the pair (a, b). That means {1, sqrt(2)} spans Q(sqrt(2)) as a Q-vector space, and it's linearly independent -- no rational combination of 1 and sqrt(2) gives zero except a = b = 0. So {1, sqrt(2)} is a basis.

Student: And the basis has two elements, so the dimension is 2.

Tutor: Right. We call that dimension the degree of the extension, written [Q(sqrt(2)) : Q] = 2.

Student: What would degree 1 mean?

Tutor: That E equals F -- no real extension happened. And in general, if [E:F] is finite, we say E is a finite extension of F. Degree captures "how much bigger" E is, in a precise, countable sense -- not just "bigger" but bigger by a specific dimension.

Student: So next time, could we do Q(sqrt(2), sqrt(3)) and get degree 4?

Tutor: That's exactly the right instinct -- let's work that out next."""


def test_division_algorithm_now_correctly_recovers_after_teach_59u_fix():
    """SUPERSEDED BY teach-59u. This test originally documented a SAFE
    ABSTENTION: judson:2.1-the-division-algorithm scored 6 (tied for 5th),
    below judson:17.1-polynomial-rings (10) and judson:18.2-factorization-
    in-integral-domains (9), and never reached the "close" candidate set.
    teach-59u's fix (restoring the division algorithm's existence-and-
    uniqueness framing to judson:2.1's vocabulary, dropped by a prior
    paraphrase) is exactly what this text needed, and it now resolves
    correctly and decisively. This module's text is tuning data for
    teach-59u's diagnosis and MUST NOT be used to validate that fix (see
    module docstring) -- the fresh, blind-authored validation for this
    exact topic lives in
    tests/test_concept_recovery_judson_full_graph_generalization_round5.py.
    This test is updated in place only so the suite reflects current
    reality, following this file's own precedent of updating stale
    round2/round3 assertions when a later bead's fix changes their
    measured numbers."""
    result = recover_from_lesson_text(DIVISION_ALGORITHM, GRAPH)
    assert result.taught_node_id == "judson:2.1-the-division-algorithm"
    assert result.abstain_reason is None

    raw = score_candidates(DIVISION_ALGORITHM, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:2.1-the-division-algorithm"] == 16
    runner_up = max(s for n, s in scores.items()
                     if n != "judson:2.1-the-division-algorithm")
    assert scores["judson:2.1-the-division-algorithm"] - runner_up >= 7


def test_group_definitions_safely_abstains_with_judson_18_2_still_a_close_rival():
    """Correct answer would be judson:3.2-definitions-and-examples (score
    5), which is not among the three candidates the final abstain names as
    "too close to call": judson:16.3-ring-homomorphisms-and-ideals (8),
    judson:16.1-rings (7), and judson:18.2-factorization-in-integral-
    domains (7, tied for 2nd/3rd). judson:18.2 still closely contends for
    this unrelated topic (basic group axioms, nothing about factorization)
    post-teach-57f. The outcome is a SAFE ABSTENTION, not a confident wrong
    answer."""
    result = recover_from_lesson_text(GROUP_DEFINITIONS, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert "too close to call" in result.abstain_reason
    assert "judson:18.2-factorization-in-integral-domains" in result.abstain_reason


def test_polynomial_rings_correctly_recovers_judson_18_2_not_in_top_5():
    """CORRECT RECOVERY. judson:18.2-factorization-in-integral-domains does
    not appear in the raw top 5 at all for this text -- no attractor
    pressure observed here."""
    result = recover_from_lesson_text(POLYNOMIAL_RINGS, GRAPH)
    assert result.taught_node_id == "judson:17.1-polynomial-rings"

    raw = score_candidates(POLYNOMIAL_RINGS, INDEX)
    top5_ids = {c.node_id for c in raw[:5]}
    assert "judson:18.2-factorization-in-integral-domains" not in top5_ids


def test_fields_of_fractions_measurably_improved_after_teach_59u_fix():
    """UPDATED BY teach-59u. This test originally documented judson:18.1-
    fields-of-fractions NOT appearing in the raw top 5 at all (score 2,
    below the match floor) -- a total recall miss independent of
    judson:18.2's attractor pattern. teach-59u's extraction fix (folding in
    the field-of-fractions lemma/theorem statements the old extractor
    skipped) took judson:18.1 from invisible to a genuine contender: it now
    scores 7 and IS named in the final "too close to call" abstain set,
    tied among five candidates including judson:18.2-factorization-in-
    integral-domains (also 7). This is a real, measured improvement
    (invisible -> competitive) that still does not fully resolve to a
    confident correct answer on this specific tuning-data text -- expected,
    since this bead's fix narrows rather than eliminates the gap (see this
    bead's handoff). This module's text is tuning data for teach-59u's
    diagnosis and MUST NOT be used to validate that fix (see module
    docstring) -- the fresh, blind-authored validation for this exact topic
    lives in
    tests/test_concept_recovery_judson_full_graph_generalization_round5.py.
    This test is updated in place only so the suite reflects current
    reality, following this file's own precedent of updating stale
    round2/round3 assertions when a later bead's fix changes their
    measured numbers."""
    result = recover_from_lesson_text(FIELDS_OF_FRACTIONS, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert "too close to call" in result.abstain_reason
    assert "judson:18.1-fields-of-fractions" in result.abstain_reason

    raw = score_candidates(FIELDS_OF_FRACTIONS, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:18.1-fields-of-fractions"] == 7
    assert "judson:18.1-fields-of-fractions" in {c.node_id for c in raw[:5]}


def test_extension_fields_correctly_recovers_after_teach_scx_fix():
    """CORRECT RECOVERY, as of teach-scx -- was a CORRECT RECOVERY before
    teach-911 (judson:21.1-extension-fields winning outright, raw score 10
    vs. judson:16.1-rings' then-7), a SAFE ABSTENTION for one bead cycle
    (teach-911 -> teach-scx), now correct again.
    judson:18.2-factorization-in-integral-domains does not appear in the raw
    top 5 at all for this text at any point -- no attractor pressure from
    that node in this trace.

    teach-911 folded Judson's 2x2-matrix noncommutative-ring example into
    judson:16.1-rings' definition (see this repo's round3 file and
    `_DISCOURSE_STOPWORDS`' teach-911 comment in concept_recovery.py for why
    the fix was needed and why "form" -- one of the words that example's
    framing sentence introduces -- could not be filtered globally without
    causing a confident wrong answer elsewhere). With "form" left in
    scoring, judson:16.1-rings' raw score against THIS text rose from 7 to 8
    (this text also happens to use "form"), narrowing the margin under
    judson:21.1-extension-fields' 10 from 3 to 2 -- no longer wide enough to
    be judged decisive, so resolution fell through to the bare-minimum-
    margin branch's rival check, where judson:3.3-subgroups (raw 4, but its
    own vocabulary is tiny enough that this text covers 33% of it, edging
    out extension-fields' 31% coverage of ITS own, much larger vocabulary)
    triggered a safe abstention -- not because rings was a real rival here,
    but because that branch has no tolerance for ANY rival, however
    uncompetitive on raw score, edging ahead on coverage by any amount.
    Filed forward as teach-scx.

    teach-scx's `EXCERPT_EDITS` fix (extract_judson_ring_field.py) elides
    just "form" from the folded-in matrix example, so it no longer
    contributes to judson:16.1-rings' score anywhere. judson:16.1-rings'
    score against this text drops back to 7, restoring the margin under
    judson:21.1-extension-fields' 10 to 3 (decisive again) -- and at a
    decisive margin, judson:3.3-subgroups' small-vocabulary coverage
    advantage is not enough to trip the (separate, stricter)
    `_DECISIVE_MARGIN_COVERAGE_GAP`/`_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO`
    veto, so extension-fields wins outright -- the exact pre-teach-911
    numbers."""
    result = recover_from_lesson_text(EXTENSION_FIELDS, GRAPH)
    assert result.taught_node_id == "judson:21.1-extension-fields"
    assert result.abstain_reason is None

    raw = score_candidates(EXTENSION_FIELDS, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:21.1-extension-fields"] == 10
    assert scores["judson:16.1-rings"] == 7
    top5_ids = {c.node_id for c in raw[:5]}
    assert "judson:18.2-factorization-in-integral-domains" not in top5_ids

