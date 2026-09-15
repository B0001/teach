"""teach-9wx: SEPARATE fresh held-out round, run to satisfy this bead's own
closing requirement ("must not validate against the homomorphisms case above
or any other fixture in test_concept_recovery_judson_full_graph_generalization.py
-- all six are now tuning data. Needs a fresh, independently-authored held-out
round (new Agent-generated dialogues, zero access to this bead or that file)
before closing.").

All five lesson texts below were produced by separate `Agent` tool calls, each
given an explicit no-tool-use, no-repository-access instruction and told
nothing about concept_recovery.py, teach-9wx, teach-ngy, or any threshold or
mechanism in this module -- only a plain-English topic name and a request to
render it as a natural tutor/student dialogue, using the agent's own general
knowledge of abstract algebra. None of the five agents saw another's output,
this module's code, or round1's fixtures. None of the five topics overlaps
with round1's six fixtures (RINGS, FACTORIZATION, SPLITTING_FIELDS, LAGRANGE,
HOMOMORPHISMS, BICYCLE_CONTROL).

One topic (ring homomorphisms and ideals) was deliberately chosen to be the
same NODE that was the original bug's false winner
(`judson:16.3-ring-homomorphisms-and-ideals`) -- but here it is the TRUE
target, not a wrong answer some other lesson accidentally won. This checks
that the fix does not overcorrect against that node when it is genuinely
what is being taught.

HONEST RESULT (measured once against the real, unmodified
`load_judson_full_graph()`, via the public `recover_from_lesson_text` entry
point only -- no internals of concept_recovery.py were read to choose or
adjust these lesson texts, and no threshold in concept_recovery.py was
changed in response to seeing these results):

  correct recoveries:      2 / 5  (CYCLIC_SUBGROUPS -> 4.1, PERMUTATION_GROUPS -> 5.1)
  safe abstentions:        3 / 5  (RING_HOMOMORPHISMS, ISOMORPHISMS, INTEGRAL_DOMAINS_FIELDS)
  CONFIDENT WRONG ANSWERS: 0 / 5

No fresh case produced a confident wrong answer. That is the bar teach-9wx's
fix exists to clear (a decisive raw-score margin no longer bypasses coverage
checking outright), and this round clears it.

But the result is not an unqualified win, and this file says so plainly:

RING_HOMOMORPHISMS is the one case teach-9wx's own new code path
(`_DECISIVE_MARGIN_COVERAGE_GAP`) actually changes the outcome of, and it
changes it from "would have been a correct decisive win" to "abstains".
Diagnosed directly: `judson:16.3-ring-homomorphisms-and-ideals` (the correct
answer for this text) leads decisively on raw score (17 vs runner-up 11,
comfortably clear of `_MIN_MARGIN`), which is exactly the shape of case the
old code returned with no coverage check at all -- so pre-teach-9wx, this
text would have been recovered correctly. But its own coverage is only 30%
(this dialogue leans on general homomorphism/kernel vocabulary shared with
`judson:11.1-group-homomorphisms`, which covers 71% of its own vocabulary
here), a 41-point gap that clears `_DECISIVE_MARGIN_COVERAGE_GAP` (0.25) and
triggers abstention. So the fix's real-world cost, measured here and not
hidden: it can turn a genuinely-correct decisive win into a false abstention
when a rival happens to be even better covered by incidental vocabulary
overlap, not just prevent false wins. This is the same trade-off direction
the whole module already makes everywhere else (a checker that says "I don't
know" is safer than one that confidently names the wrong concept), so it is
consistent with this module's design, but it is a real, disclosed recall
cost of this specific fix, not a free win. Filed as its own follow-up bead
rather than tuned away here, per this lineage's rule against adjusting a
threshold in response to the same round that measured it.

ISOMORPHISMS and INTEGRAL_DOMAINS_FIELDS abstain through mechanisms teach-9wx
did NOT touch: ISOMORPHISMS ties three ring-flavored candidates
(`judson:16.1-rings`, `judson:16.3-ring-homomorphisms-and-ideals`,
`judson:18.2-factorization-in-integral-domains`) in the pre-existing
multi-candidate-tie branch (teach-ngy's code, not teach-9wx's) -- the correct
answer, `judson:9.1-definition-and-examples`, is not even among the tied
candidates, a pre-existing recall gap unrelated to this bead.
INTEGRAL_DOMAINS_FIELDS abstains through the pre-existing near-margin
self-floor check (teach-l7u/teach-i35's code): the winner needs 20% coverage
at that margin and gets only 16%. Neither of these is evidence for or against
teach-9wx's fix; they are pre-existing behavior, confirmed unchanged, and are
noted here for an honest accounting of the round rather than claimed as
teach-9wx's doing.

WHAT THIS MEANS FOR teach-9wx's OWN CLOSURE

The bead's named bug -- a decisive margin bypassing the coverage check
entirely, letting a long verbatim node beat a correct terse rival -- is
fixed and unit-verified
(test_concept_recovery.py::test_decisive_margin_still_abstains_when_a_rival_is_covered_far_better,
test_concept_recovery.py::test_decisive_margin_not_second_guessed_when_the_rival_gap_is_narrow),
does not regress `test_judson_algebra_graph.py::test_signposted_prerequisites_are_recovered`
or any of the 548 tests in the full suite, and produces zero confident wrong
answers across this fresh round. Per this lineage's standing rule, a
mechanism fix being real and unit-verified is not enough to close without a
genuinely fresh round showing no confident wrong answer -- this round is that
evidence, and it shows exactly that: no fresh confident wrong answer, at the
honestly-disclosed cost of one new false abstention on a case that shares the
same false winner's target node. That cost is filed as a new, separate bead
(follow-up recall work) rather than blocking this closure, consistent with
how teach-cpg and teach-i35 both closed with a residual gap filed forward
rather than solved in the same session that measured it.
"""

from teach.concept_recovery import recover_from_lesson_text
from teach.judson_algebra_graph import load_judson_full_graph

GRAPH = load_judson_full_graph()

RING_HOMOMORPHISMS = """Tutor: Last time we established rings—sets with addition and multiplication that play nicely together. Today, how do we compare two rings? What makes a map between them "structure-preserving"?

Student: I'd guess it has to respect both operations somehow.

Tutor: Exactly. A ring homomorphism from a ring R to a ring S is a function f: R → S such that for all a, b in R, f(a + b) = f(a) + f(b), and f(ab) = f(a)f(b). We usually also want f(1) = 1 if both rings have identity. So it's not enough to just preserve addition—that would just make it a group homomorphism of the additive groups. It has to preserve multiplication too.

Student: So it's like it doesn't matter whether you combine elements first and then map, or map first and then combine.

Tutor: That's the right intuition—it's "compatible" with the arithmetic on both sides. Now, here's an example: the map from the integers to Z/nZ sending an integer to its residue mod n. Addition and multiplication mod n behave exactly like the reduction of ordinary addition and multiplication.

Student: Right, that's why modular arithmetic works at all.

Tutor: Precisely. Now here's a key question: which elements does that map send to zero?

Student: The multiples of n.

Tutor: Right—that set is called the kernel. In general, for any ring homomorphism f: R → S, the kernel is the set of elements of R that map to 0 in S: ker(f) = {r in R : f(r) = 0}.

Student: Okay, so it's like the kernel of a linear map, or a group homomorphism—the stuff that gets collapsed.

Tutor: Same idea. And the kernel has special structure. First, since f is additive, ker(f) is closed under addition, and it contains 0, and it's closed under negation—so it's a subgroup of R under addition. But there's more: suppose k is in the kernel, and r is any element of R at all. What is f(rk)?

Student: f(rk) = f(r)f(k) = f(r)·0 = 0.

Tutor: So rk is also in the kernel. And by the same argument, kr is in the kernel too. So the kernel isn't just closed under addition—it absorbs multiplication by anything in the whole ring, not just by other kernel elements.

Student: That's a stronger property than just being a subring, then.

Tutor: Much stronger. A subring only needs to be closed under multiplication with itself. This absorption property is exactly the defining feature of something called an ideal. A subset I of a ring R is an ideal if it's closed under addition (and contains 0, closed under negatives), and for every i in I and every r in R, both ri and ir are in I.

Student: So every kernel is an ideal.

Tutor: Every kernel is an ideal—that's the theorem we just proved together. It's one of the most important facts in ring theory, because it's the reason ideals are the "right" generalization of kernels, the same way normal subgroups are the right generalization of kernels for groups. In fact, it goes the other way too: every ideal actually is the kernel of some homomorphism—the quotient map onto R/I. But that's a story for next time.

Student: So ideals are basically ring theory's version of normal subgroups.

Tutor: That's exactly the right analogy to carry forward."""

ISOMORPHISMS = """Tutor: Last time we talked about groups in the abstract — a set, an operation, the axioms. Today let's talk about when two groups that look completely different are secretly "the same." That's the idea of isomorphism.

Student: Like when a group of numbers and a group of symmetries turn out to be related?

Tutor: Exactly the kind of example we'll get to. Formally, an isomorphism from a group G to a group H is a function φ: G → H that's bijective — so it's one-to-one and onto, every element of G maps to a unique element of H and every element of H gets hit — and it preserves the operation. That means for all a, b in G, φ(a ·_G b) = φ(a) ·_H φ(b).

Student: So it doesn't matter whether I combine a and b first in G and then map the result, or map a and b first and then combine them in H?

Tutor: Right, you get the same answer either way. That's the crucial part. The bijection alone just says the two sets have the same size — same number of elements. The operation-preserving part is what says the entire algebraic structure matches: identity maps to identity, inverses map to inverses, subgroups map to subgroups, element orders are preserved. Everything you could ever compute about the group's structure transfers across φ.

Student: So "isomorphic" means "the same group, just relabeled"?

Tutor: That's a good way to think of it. The elements might have totally different flavors — numbers, symmetries, permutations — but if there's an isomorphism between them, they're indistinguishable as groups. Any true statement about one, phrased purely in terms of the group operation, is automatically true of the other.

Student: Can you give me an actual example?

Tutor: Sure. Take Z/4Z, the integers mod 4 under addition: {0,1,2,3}. And take U(5), the group of units mod 5 under multiplication: {1,2,3,4}. Both have order 4. In Z/4Z, the element 1 generates everything: 1,2,3,0. In U(5), does anything generate everything?

Student: Let's see... 2^1=2, 2^2=4, 2^3=8=3, 2^4=16=1. So 2,4,3,1 — yes, 2 generates the whole group.

Tutor: Perfect. So define φ: Z/4Z → U(5) by φ(k) = 2^k mod 5. That gives φ(0)=1, φ(1)=2, φ(2)=4, φ(3)=3. It's clearly bijective — four inputs, four distinct outputs. And you can check it preserves the operation: φ(a+b mod 4) = 2^(a+b) mod 5 = 2^a · 2^b mod 5 = φ(a)·φ(b).

Student: So addition mod 4 on one side corresponds exactly to multiplication mod 5 on the other, once you relabel with powers of 2.

Tutor: Precisely. Additively written cyclic group of order 4, multiplicatively written cyclic group of order 4 — different-looking operations, different-looking elements, but the same underlying structure. In fact this generalizes: any two cyclic groups of the same order are isomorphic to each other, always via k ↦ (generator)^k.

Student: So when we say "there's essentially only one group of order 4 that's cyclic," we really mean up to isomorphism.

Tutor: Exactly — that phrase "up to isomorphism" is how algebraists say "ignoring relabeling of elements." It's the natural notion of sameness for groups, the same way "congruent" is the natural notion of sameness for triangles."""

CYCLIC_SUBGROUPS = """Tutor: Last time we settled on what a group and a subgroup are. Today let's look at a way to build a subgroup out of a single element.

Student: Just one element?

Tutor: Just one. Take any element g in a group G. Consider all its powers: g⁰, g¹, g², g⁻¹, g⁻², and so on — every integer power of g, positive, negative, and zero. Call that set ⟨g⟩.

Student: And that's automatically a subgroup?

Tutor: Yes. It contains the identity, since g⁰ = e. It's closed under the operation, since gᵃ times gᵇ is gᵃ⁺ᵇ, which is still a power of g. And every element has an inverse in the set, since the inverse of gᵃ is g⁻ᵃ. So ⟨g⟩ satisfies all the subgroup requirements. We call it the cyclic subgroup generated by g.

Student: Okay, so it's the smallest subgroup that has to contain g, basically, because anything containing g has to contain all its powers anyway.

Tutor: Exactly right — that's actually the cleanest way to think about it. Now here's the important companion idea: the order of the element g is the smallest positive integer n such that gⁿ = e. If no such positive integer exists, we say g has infinite order.

Student: So order of the element versus order of the group — those are different numbers?

Tutor: Related but different. The order of an element is about that one element's power cycle. It turns out — though we won't prove it today — that the order of g equals the size of ⟨g⟩ exactly. If gⁿ = e for the smallest such n, then ⟨g⟩ = {e, g, g², ..., gⁿ⁻¹}, and those n elements are all distinct.

Student: Can we see a concrete example?

Tutor: Take the group Z mod 6, integers under addition mod 6, elements {0,1,2,3,4,5}. Let's find the order of the element 2. "Powers" here mean repeated addition, since the operation is addition, not multiplication.

Student: So 2, then 2+2=4, then 2+2+2=6=0.

Tutor: Right. So 2·1=2, 2·2=4, 2·3=0. The smallest positive n with n·2 ≡ 0 mod 6 is n=3. So the order of 2 is 3.

Student: And ⟨2⟩ is {0,2,4}?

Tutor: Precisely — a subgroup of size 3 sitting inside a group of size 6. Notice 3 divides 6; that's not a coincidence, though again, that's a theorem for another day.

Student: What about an element like 1?

Tutor: Try it yourself — what's the smallest n with n·1 ≡ 0 mod 6?

Student: n=6, since you have to go all the way around. So 1 generates the whole group?

Tutor: Exactly, ⟨1⟩ = all of Z mod 6. An element whose cyclic subgroup is the entire group is called a generator of the group. And if you wanted an infinite-order example, think of a nonzero integer inside the additive group of all integers, Z — no positive multiple of it ever gets back to 0, so it generates an infinite cyclic subgroup."""

INTEGRAL_DOMAINS_FIELDS = """Tutor: Last time we nailed down what a commutative ring with identity looks like. Today let's build two more layers on top: integral domains and fields. They both start from that same base, but they diverge in an important way.

Student: Okay. I remember — commutative means ab = ba, and "with identity" means there's a 1 that acts like a multiplicative identity.

Tutor: Right. Now, an integral domain is a commutative ring with identity that has no zero divisors. Do you remember what a zero divisor is?

Student: A nonzero element a such that there's some nonzero b with ab = 0?

Tutor: Exactly. So "no zero divisors" means: if ab = 0, then a = 0 or b = 0. That's the whole extra condition. It sounds small, but it buys you a lot — for instance, you can cancel: if ab = ac and a isn't zero, you can conclude b = c, because a(b - c) = 0 forces b - c = 0.

Student: Got it. And a field is different?

Tutor: A field is also a commutative ring with identity, but with a stronger condition: every nonzero element has a multiplicative inverse. That is, for every a ≠ 0, there's some a⁻¹ in the ring with a·a⁻¹ = 1.

Student: So fields let you divide by anything except zero.

Tutor: Precisely. Now here's the natural question: is every field automatically an integral domain?

Student: Let me think... if ab = 0 and a ≠ 0, then a has an inverse, so I can multiply both sides by a⁻¹: a⁻¹(ab) = a⁻¹·0, which gives b = 0.

Tutor: Exactly right. So invertibility of every nonzero element automatically kills the possibility of zero divisors. That's why every field is an integral domain — the field condition is strictly stronger.

Student: But not every integral domain is a field, I'm guessing?

Tutor: Correct, and this is the key example to remember. Take the integers, ℤ. It's commutative, has identity 1, and has no zero divisors — if two integers multiply to zero, one of them must be zero. So ℤ is an integral domain.

Student: But 2 doesn't have a multiplicative inverse in ℤ.

Tutor: Right — there's no integer n with 2n = 1. So ℤ fails to be a field, even though it's a perfectly good integral domain.

Student: And the rationals fix that?

Tutor: Exactly. ℚ is also commutative with identity, still has no zero divisors, but now every nonzero rational p/q has an inverse q/p. So ℚ is a field.

Student: So the integers are like the "before" picture, and the rationals are the "after" — you formally throw in inverses for everything nonzero and you upgrade from integral domain to field.

Tutor: That's a great way to see it — in fact that's literally how the field of fractions construction works, going from ℤ to ℚ in general. Integral domain is the weaker, more common structure; field is the stronger one where division actually works."""

PERMUTATION_GROUPS = """Tutor: So — you know what a group is: a set with an operation that's associative, has an identity, and every element has an inverse. Today let's build a specific example that shows up everywhere: permutation groups.

Student: Okay. Permutation just means rearrangement, right?

Tutor: Right, but let's be precise about it. If S is a finite set, a permutation of S is a bijection from S to itself — a function that's both one-to-one and onto. So every element of S gets sent somewhere in S, no two elements collide, and nothing is left unhit.

Student: So if S is {1, 2, 3}, a permutation might send 1 to 2, 2 to 3, and 3 to 1?

Tutor: Exactly. Every element has exactly one output, every element appears exactly once as an output. Now here's the key move: since a permutation is just a function, we can compose two of them. If σ and τ are both permutations of S, then σ∘τ is the function that sends x to σ(τ(x)) — do τ first, then σ. And the composition of two bijections is always a bijection, so σ∘τ is again a permutation of S.

Student: So the set of permutations is closed under composition.

Tutor: Right. And that's the first thing you need for a group. Let's check the rest. Composition of functions is always associative — that's just a general fact, not special to permutations. The identity element is the identity function, the permutation that sends every element to itself; composing anything with it changes nothing. And every permutation has an inverse: since it's a bijection, you can reverse the arrows, and that reversed function is also a bijection of S, and it composes with the original to give the identity.

Student: So closure, associativity, identity, inverses — that's all four. So the set of all permutations of S actually is a group.

Tutor: Exactly, and it has a name: the symmetric group on S, written S_n when |S| = n, since up to relabeling it only depends on the size of the set. Its order is n! — that's how many bijections there are from an n-element set to itself.

Student: How do people actually write one of these down without drawing arrows everywhere?

Tutor: Cycle notation. You track where an element goes, then where that goes, until you get back to the start. Take the example you gave: 1→2, 2→3, 3→1. That's a single cycle, written (1 2 3), meaning 1 goes to 2, 2 goes to 3, 3 goes back to 1.

Student: What if it doesn't loop through everything?

Tutor: Then you write it as a product of disjoint cycles. Say in S_4, 1→2, 2→1, 3→4, 4→3. That's (1 2)(3 4) — two separate 2-cycles, called transpositions, acting on disjoint parts of the set. Any element not mentioned, like a 5 in S_5, is understood to be fixed.

Student: And composing permutations in cycle notation just means applying them one after another?

Tutor: Precisely — work right to left, track each element through both cycles, and you'll land on the composite permutation."""


def test_cyclic_subgroups_correctly_recovers():
    """CORRECT RECOVERY: decisive raw-score win, own coverage high enough
    that no rival comes close -- the fix's decisive-margin gap check does
    not fire here, and correctly does not need to."""
    result = recover_from_lesson_text(CYCLIC_SUBGROUPS, GRAPH)
    assert result.taught_node_id == "judson:4.1-cyclic-subgroups"


def test_permutation_groups_correctly_recovers():
    """CORRECT RECOVERY: same shape as CYCLIC_SUBGROUPS -- a decisive win
    that is also well-covered, so the new gap check passes it through."""
    result = recover_from_lesson_text(PERMUTATION_GROUPS, GRAPH)
    assert result.taught_node_id == "judson:5.1-definitions-and-notation"


def test_ring_homomorphisms_safely_abstains_not_a_confident_wrong_answer():
    """The one case in this round teach-9wx's new code path actually decides.
    `judson:16.3-ring-homomorphisms-and-ideals` is the CORRECT target here
    (unlike round1's HOMOMORPHISMS, where the same node was a wrong answer)
    and leads decisively on raw score (17 vs runner-up 11). Pre-teach-9wx
    this would have recovered correctly. But its own coverage is only 30%
    against `judson:11.1-group-homomorphisms`'s 71% (this dialogue leans on
    generic homomorphism/kernel vocabulary shared with the group-homomorphism
    node), a 41-point gap that clears `_DECISIVE_MARGIN_COVERAGE_GAP` --
    so the fix abstains rather than confidently answering, trading a
    genuinely correct decisive win for a false abstention on this specific
    text. This is disclosed here as a real, measured cost of the fix, not
    swept under a passing assertion: the test only asserts the SAFE
    direction (abstain, not a wrong answer), matching what was actually
    measured, and the recall cost is written up in the module docstring
    above and filed as follow-up work rather than tuned away in this round."""
    result = recover_from_lesson_text(RING_HOMOMORPHISMS, GRAPH)
    assert result.taught_node_id != "judson:11.1-group-homomorphisms", (
        "would be a confident WRONG answer if this ever fires -- "
        "ring-homomorphisms text should not be attributed to the group-"
        "homomorphisms node"
    )
    if result.taught_node_id is not None:
        assert result.taught_node_id == "judson:16.3-ring-homomorphisms-and-ideals"
    else:
        assert result.abstain_reason is not None


def test_isomorphisms_abstains_via_preexisting_multi_candidate_tie_not_teach_9wx():
    """SAFE ABSTENTION, but through teach-ngy's pre-existing multi-candidate
    coverage-tiebreak machinery, not teach-9wx's new decisive-margin gap
    check -- confirmed unrelated to this bead by checking which abstain
    branch actually fired. The correct answer,
    judson:9.1-definition-and-examples, is not even among the tied
    candidates: a pre-existing recall gap, noted honestly here, not claimed
    as evidence for or against this bead's fix."""
    result = recover_from_lesson_text(ISOMORPHISMS, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert "ambiguous match" in result.abstain_reason


def test_integral_domains_fields_abstains_via_preexisting_near_margin_floor():
    """SAFE ABSTENTION through the pre-existing near-margin self-floor check
    (teach-l7u/teach-i35's code, margin <= min_margin branch), not
    teach-9wx's new decisive-margin code -- confirmed unrelated to this bead
    by checking which abstain branch actually fired."""
    result = recover_from_lesson_text(INTEGRAL_DOMAINS_FIELDS, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
    assert "covers just" in result.abstain_reason
