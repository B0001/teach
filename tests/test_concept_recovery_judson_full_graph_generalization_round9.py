"""teach-jkx round 9: the fresh, independently-authored held-out round this
bead's own standing discipline requires BEFORE any threshold is moved.

WHY THIS ROUND EXISTS. teach-jkx's remaining leads are both single-threshold
tunes against the very fixture that found the bug (GROUP_AXIOMS_BLIND). This
lineage's rule -- established by teach-ceg and teach-i35, and restated in
teach-jkx's own description -- is that a fix may not be validated on the
fixture that motivated it. Lead (a) proposes _DECISIVE_MARGIN_COVERAGE_GAP
0.18 -> ~0.26 because that value separates the four KNOWN cases
(GROUP_AXIOMS_BLIND 29.5pt must-veto, RINGS-round5 23.8pt must-not-veto,
SIGNPOSTED_LESSON 21.2pt must-not-veto, RING_HOMOMORPHISMS 39.6pt must-veto),
closest-pair margin 5.7pt. Four points do not establish that 0.26
generalizes. This round supplies topics no calibration decision has seen.

By round 8 every one of the 20 nodes in `load_judson_full_graph()` already had
a fixture somewhere in rounds 1-8, so "fresh" here means what round4 and
round8 already established it means when the graph runs out of unused nodes:
newly, independently authored dialogue text, produced blind and measured once
-- not a topic nobody has ever touched.

TOPIC CHOICE IS DELIBERATELY ADVERSARIAL to lead (a). Raising the gap
threshold makes the veto HARDER to fire, i.e. produces FEWER abstentions and
MORE confident answers. That is the direction this module's own stated
priority disprefers (see `_MIN_WINNING_COVERAGE`'s comment: "erring low costs
a real recovery an abstention; erring high lets a confident wrong answer
through... this repo prefers the first"). The danger of 0.26 is therefore a
NEW confident wrong answer on a lesson whose true coverage gap lands in
[0.18, 0.26) -- a gap that vetoes today and would stop vetoing. Two of the
three topics below are group-theory topics of exactly the kind teach-jkx
showed judson:16.1-rings' broad 52-word vocabulary decisively out-raw-scores
(normal subgroups, permutation groups); the third (integral domains and
fields) is ring-adjacent, where judson:16.1-rings is a LEGITIMATE near
neighbour, stressing the opposite direction.

All three lesson texts below were produced by three separate, parallel
`Agent` tool calls, each given an explicit no-tool-use, no-repository-access,
no-internet instruction and told nothing about concept_recovery.py, this
bead, teach-jkx, any threshold, or any mechanism in this module -- only a
plain-English topic name and a request to render it as a natural
tutor/student dialogue from the agent's own general abstract-algebra
knowledge, with no reference to any specific textbook. All three returned
with zero tool calls, confirming the blind condition held. None saw another's
output, this module's code, or any prior round's fixtures.

THE GATES BELOW WERE WRITTEN BEFORE ANY MEASUREMENT WAS TAKEN. The safety
property asserted -- "never a confident wrong answer" -- is the one this
module's own priority ranks highest, and it is stated here without knowing
what the current tree does on these three texts, precisely so that the
measurement cannot retro-fit the gate. Whatever the numbers turn out to be,
they are recorded in this module's docstring by a later edit, not by
weakening these assertions.

MEASURED ONCE against the real, unmodified, current-tree
`load_judson_full_graph()`, through the public entry points only (raw tier
winner / its coverage / best-covered rival / its coverage / gap):

  NORMAL_SUBGROUPS_BLIND    16.1-rings 14, 26.9% | 6.1-cosets 5, 100.0% | 73.1pt
      -> ABSTAINS ("ambiguous match"). Safe. teach-jkx's rings-out-scores-
         group-theory effect reproduces a fourth time.
  PERMUTATION_GROUPS_BLIND  16.1-rings 12, 23.1% | 5.1-defs 12, 92.3% | 69.2pt
      -> CORRECT RECOVERY (judson:5.1-definitions-and-notation). A positive
         control: this class of lesson does not always abstain.
  INTEGRAL_DOMAINS_BLIND    18.2-factorization 18, 36.0% | 16.2-domains-and-
         fields 11, 57.9% | 21.9pt
      -> ABSTAINS today, correctly. THIS IS THE DECISIVE CASE.

LEAD (a) IS FALSIFIED BY THIS ROUND. INTEGRAL_DOMAINS_BLIND's 21.9pt gap sits
INSIDE the [0.18, 0.26) window that raising _DECISIVE_MARGIN_COVERAGE_GAP to
0.26 would stop vetoing. Measured by actually applying 0.26 to the tree: the
lesson stops abstaining and confidently returns
judson:18.2-factorization-in-integral-domains -- a CONFIDENT WRONG ANSWER on a
genuinely blind, on-topic lesson about integral domains and fields. That is
the same failure class as teach-jkx itself, newly created by the proposed fix
for teach-jkx. The full suite at 0.26 also breaks round3's
test_maximal_prime_ideals_abstains_via_teach_hpa_gate_no_regression_vs_ungated
and round8's test_cosets_fresh_hits_decisive_margin_coverage_gap_veto: 4
failed, 719 passed. The tree was restored byte-identical afterwards.

The four cases lead (a) was calibrated on (29.5 / 23.8 / 21.2 / 39.6pt) gave a
closest-pair margin of 5.7pt and looked separable. A single held-out topic
landed at 21.9pt and closed that window from the other side. This is exactly
what this lineage's hold-out rule exists to catch, and it caught it before any
threshold was moved.
"""

from teach.concept_recovery import (
    build_vocabulary_index,
    recover_from_lesson_text,
    score_candidates,
    _coverage_fraction,
    _resolve_candidates,
    _words,
)
from teach.judson_algebra_graph import load_judson_full_graph

GRAPH = load_judson_full_graph()
INDEX = build_vocabulary_index(GRAPH)

NORMAL_SUBGROUPS_BLIND = """Tutor: Before we get to definitions, let me ask you something. You know how when we look at the integers and we only care about even versus odd, we can do arithmetic with just those two classes? Odd plus odd is even, and so on.
Student: Yeah, that's arithmetic mod 2.
Tutor: Right. Now here's the question I want to motivate everything with: when can we do that in general? Given a group G and a subgroup H, when can we take the cosets of H and make them into a group in their own right?
Student: I'd guess always? Just multiply the cosets.
Tutor: That's exactly the right first guess, and it's exactly the thing that fails. Let's define the attempt precisely so we can see where it breaks. We want to define aH times bH equals abH. What's suspicious about that definition?
Student: Hmm. The left side is written in terms of a and b, but a coset doesn't have a unique name - aH equals a prime H for lots of other a prime.
Tutor: That's the whole story. So the operation is only well defined if whenever aH equals a prime H and bH equals b prime H, we get abH equals a prime b prime H. Try to see what condition on H makes that work. Take a prime equals ah for some h in H, and b prime equals b. Then a prime b prime equals ahb. When is ahb in abH?
Student: We'd need ahb equals abh prime for some h prime in H. So multiplying on the left by ab inverse, that gives b inverse h b equals h prime.
Tutor: Exactly. So you need b inverse h b to be back in H, for every h in H and every b in G. That's the condition, and that's the definition: H is normal in G if g inverse H g equals H for every g in G. Equivalently gH equals Hg - left cosets equal right cosets.
Student: Why equivalently? Those look like different statements to me.
Tutor: Good, don't take it on faith. g inverse H g equals H, multiply both sides on the left by g: you get Hg equals gH. It's the same equation rearranged. The reason both phrasings show up is that one is about conjugation and one is about cosets, and different arguments want different pictures.
Student: One thing bugs me. Should it be g inverse H g contained in H or equals? Some of what I've seen says containment.
Tutor: Sharp question. Containment for all g is actually enough, and the trick is that for all g includes g inverse. If g inverse H g is contained in H for every g, then also g H g inverse is contained in H, and conjugating that by g inverse gives H contained in g inverse H g. So the two containments combine into equality. But be careful - that argument needs all g. For a fixed single g, containment can be strict in infinite groups.
Student: Okay. So let's do a real example where it fails?
Tutor: Let's. Take S3, the symmetries of a triangle - six elements. Let H be the subgroup generated by a single transposition, say H equals the set containing the identity and (1 2). Compute (1 3)H and H(1 3) for me.
Student: (1 3)H is the set containing (1 3) and (1 3)(1 2). Composing those, if I go right to left, (1 2) then (1 3): 1 goes to 2, 2 goes to 1 then to 3, so 2 goes to 3, and 3 goes to 1. That's the 3-cycle (1 2 3).
Tutor: Good. And the other side?
Student: H(1 3) is the set containing (1 3) and (1 2)(1 3). That one sends 1 to 3, right to left again: (1 3) first sends 1 to 3, then (1 2) fixes 3. So 1 goes to 3. And 3 goes to 1 then to 2. So it's (1 3 2).
Tutor: So the two cosets are different sets, and H is not normal. Now watch the well-definedness die concretely. In S3, is (1 2)H the same coset as eH?
Student: Yes, both are H itself.
Tutor: So if the product were well defined, (1 3)H times (1 2)H should equal (1 3)H times eH. Left side is (1 3)(1 2)H equals (1 2 3)H, right side is (1 3)H. Are those the same coset?
Student: Let me just check whether (1 3) inverse times (1 2 3) lands in H. That's the clean test.
Tutor: Slow down and do exactly that.
Student: (1 3) is its own inverse. (1 3)(1 2 3): 1 goes to 2, 2 goes to 3 then to 1, 3 goes to 1 then to 3. So 3 is fixed and 1, 2 swap - that's (1 2). Which is in H. So they are the same coset, and I miscomputed something above.
Tutor: You did. The lesson is worth more than the arithmetic: my counterexample pairing was badly chosen. That happens constantly in this subject. The genuine failure shows up elsewhere. Try left coset (1 2)H equals H against right factor (1 3)H equals (1 2 3)H.
Student: (1 2)(1 3)H versus e(1 3)H. The second is (1 3)H, the set containing (1 3) and (1 2 3). The first: (1 2)(1 3) sends 1 to 3, 3 to 2. Let me be careful. Right to left: (1 3) first. 1 to 3, then (1 2) fixes 3, so 1 to 3. 3 to 1, then 1 to 2, so 3 to 2. 2 to 2, then 2 to 1. So it's (1 3 2). Is (1 3 2) in the set containing (1 3) and (1 2 3)? No. So the products differ.
Tutor: There it is. Same pair of cosets, two different representatives, two different answers. The multiplication is genuinely not a function. Now the payoff: what makes normality the right condition rather than a technical patch?
Student: I suppose because it's exactly what you need, not more.
Tutor: Right, and there's a structural reason it keeps appearing. Take any homomorphism phi from G to another group. What can you say about its kernel?
Student: It's a subgroup. And if k is in the kernel, then phi of g inverse k g equals phi of g inverse times phi of k times phi of g, which is the identity. So g inverse k g is in the kernel too. The kernel is normal.
Tutor: And the converse: every normal subgroup is the kernel of something, namely the map from G to G mod N sending g to gN. So normal subgroup and kernel of a homomorphism are the same concept seen from two sides. That's why normality isn't arbitrary.
Student: So G mod N is the set of cosets, with that multiplication, and it's a group?
Tutor: Check it yourself quickly. What's the identity, and what's the inverse of aN?
Student: Identity is N itself, since aN times N equals aN. Inverse of aN is a inverse N, since the product is a a inverse N equals N. And associativity comes from associativity in G.
Tutor: Good. Let's do a clean concrete one. Take G the integers under addition, N the multiples of 3. Additive notation, so cosets are a plus 3Z. What is the quotient?
Student: Three cosets: 0, 1, and 2 plus the multiples of 3. And adding them is mod-3 addition. It's the cyclic group of order 3.
Tutor: And why were the multiples of 3 automatically normal?
Student: Because the integers are abelian, so every subgroup is normal - conjugation does nothing.
Tutor: Exactly, which is why abelian groups hide the whole issue. Now one in S3 that works: let A3 be the even permutations, the identity and the two 3-cycles. It has index 2. Why is any index-2 subgroup automatically normal?
Student: If H has index 2, there are two left cosets, H and everything else. And two right cosets, H and everything else. So for g not in H, gH and Hg are both the complement of H. They're equal.
Tutor: Nice argument - it uses no computation at all. So S3 mod A3 has order 2, and the quotient map is exactly the sign homomorphism: even or odd. Notice what the quotient did.
Student: It threw away the information about which permutation, and kept only the parity. Like the even-odd thing you started with.
Tutor: That's the right way to think about every quotient: N is what you've decided to stop distinguishing, and G mod N records what survives. One last check - if N is normal in G and G mod N is abelian, what does that tell you about G?
Student: Hmm. Abelian quotient means aN bN equals bN aN, so abN equals baN, so ba inverse ab is in N. That's the commutator. So N contains all the commutators.
Tutor: Perfect, and that's the seed of the commutator subgroup: the smallest normal subgroup whose quotient is abelian. Work through S4 and A4 on your own with that lens, and see whether the subgroup of order 4 inside A4 is normal - it's the most instructive example in the whole chapter."""

PERMUTATION_GROUPS_BLIND = """Tutor: Before we get to any notation, let me ask you something. If I hand you three books and ask you to line them up on a shelf, how many different orders could you produce?
Student: Six. Three choices for the first slot, two for the second, one for the last.
Tutor: Right. Now here's the shift I want you to make. Instead of thinking of those six as six *arrangements*, I want you to think of them as six *actions* - six ways to rearrange whatever is already there. Why would that be a useful change of perspective?
Student: I guess because actions can be done one after another? Arrangements just sort of sit there.
Tutor: Exactly that. Actions compose. If I shuffle the books one way and then shuffle them again, the net effect is another shuffle. And every shuffle can be undone. That's precisely the structure of a group. So let's define it: a permutation of a set X is a bijection from X to itself. The set of all such bijections, under composition, is called the symmetric group on X, written S_X, or S_n when X is {1, 2, ..., n}.
Student: Why does it have to be a bijection and not just any function?
Tutor: Good question. Think about what "rearranging" means physically. Nothing gets destroyed and nothing gets duplicated. If the function weren't injective, two books would end up in the same slot. If it weren't surjective, some slot would end up empty. Bijectivity is exactly the condition that guarantees an inverse exists - which is the group axiom you'd otherwise be missing.
Student: Okay. So S_3 has six elements, and S_n has n factorial.
Tutor: Correct. Now the practical problem: how do we actually write one of these things down? The honest way is a table. For a permutation of {1,2,3,4,5} I could write the inputs on top and outputs below, meaning 1 goes to 3, 2 goes to 5, 3 goes to 4, 4 goes to 1, 5 goes to 2. What's annoying about this notation?
Student: The top row is always the same, so it's kind of wasted. And it's hard to see what's actually going on.
Tutor: Both true, and the second one matters more. Let me show you what's actually going on. Start at 1 and follow it. 1 goes to 3. Where does 3 go?
Student: To 4. And 4 goes back to 1.
Tutor: So we've closed a loop: 1 to 3 to 4 to 1. Now pick a number we haven't touched yet.
Student: 2. It goes to 5, and 5 goes to 2. Another loop.
Tutor: And you've just discovered that the permutation is built out of two disjoint cycles. We write it as (1 3 4)(2 5). The convention: inside each parenthesis, each element maps to the one on its right, and the last one wraps around to the first. That's cycle notation.
Student: So (1 3 4) means 1 to 3, 3 to 4, 4 to 1. What if a number doesn't move at all?
Tutor: Then it forms a cycle of length one, and by convention we just omit it. If a permutation of {1,...,5} were written (2 5), you'd read that as "2 and 5 swap, everything else stays put." A two-cycle like that has a name - a transposition.
Student: Is the way I write a cycle unique? Because (1 3 4) and (3 4 1) look like they'd do the same thing.
Tutor: Sharp catch, and yes, they're the same permutation. A cycle of length k has k equivalent spellings, since you can start at any of its elements and go around. And the disjoint cycles themselves can be written in any order: (1 3 4)(2 5) and (2 5)(1 3 4) are the same. People often standardize by starting each cycle with its smallest element and ordering the cycles by those, but that's cosmetic.
Student: Why can you swap the order of the cycles? I thought composing permutations wasn't commutative.
Tutor: It isn't in general - but these two cycles are disjoint. They touch completely different elements. (1 3 4) does nothing to 2 or 5, and (2 5) does nothing to 1, 3, or 4. When two permutations move disjoint sets, they never interfere, so they commute. That's a small theorem worth remembering: disjoint cycles commute. Non-disjoint ones generally don't.
Student: Got it.
Tutor: Let's test that. Compute (1 2)(2 3) and then (2 3)(1 2), in S_3. I'll use the right-to-left convention, same as function composition: apply the rightmost factor first.
Student: Okay, (1 2)(2 3). Starting with 1: the right factor (2 3) leaves 1 alone, then (1 2) sends it to 2. So 1 to 2. Then 2: the right factor sends 2 to 3, and (1 2) leaves 3 alone. So 2 to 3. And 3: right factor sends 3 to 2, left factor sends 2 to 1. So 3 to 1. That's (1 2 3).
Tutor: Perfect. Now the other order.
Student: (2 3)(1 2). Take 1: (1 2) sends it to 2, then (2 3) sends 2 to 3. So 1 to 3. Take 3: (1 2) fixes it, (2 3) sends it to 2. So 3 to 2. And 2: (1 2) sends it to 1, (2 3) fixes 1. So 2 to 1. That gives 1 to 3, 3 to 2, 2 to 1, so (1 3 2).
Tutor: And (1 2 3) is not (1 3 2), so the group isn't abelian. You did the composition correctly, which is the part people most often botch - watch that right-to-left habit, because some books and a lot of software go left-to-right instead. Always check which convention is in force.
Student: That's a little alarming. So the same symbols can mean two different things?
Tutor: They can, and the two answers are inverses of each other, so it's not catastrophic, but it is a real source of sign errors later. Just state your convention and stay consistent.
Student: Let me try one on my own. What about (1 2 3 4) composed with itself?
Tutor: Go ahead.
Student: Apply it twice. 1 to 2 to 3, so 1 to 3. 2 to 3 to 4, so 2 to 4. 3 to 4 to 1, so 3 to 1. And 4 to 1 to 2, so 4 to 2. So I get (1 3)(2 4).
Tutor: Correct. And notice what happened structurally: squaring a 4-cycle broke it into two 2-cycles. That's a hint that the cycle type - the multiset of cycle lengths - carries a lot of information. What do you think the order of (1 2 3 4) is, meaning the smallest positive power that gives the identity?
Student: Four? Since it takes four steps to get all the way around.
Tutor: Yes. And in general a single k-cycle has order k. Here's a harder one to think about: what's the order of (1 2 3)(4 5)?
Student: Hmm. The 3-cycle needs three applications and the 2-cycle needs two. So five?
Tutor: That's the natural first guess, but test it. Apply the whole thing five times. What has the 3-cycle done after five applications?
Student: Five isn't a multiple of three, so it's not back to where it started. So five is wrong. I need a number that's a multiple of both three and two. Six.
Tutor: Exactly - the least common multiple of the cycle lengths. You tripped on it and then fixed it yourself, which is the right instinct: when a guess about permutations feels plausible, just apply the thing and watch.
Student: One more question. Is every permutation guaranteed to decompose into disjoint cycles like this, or did we just get lucky with the example?
Tutor: Guaranteed, and the proof is essentially the procedure you already carried out. Pick any element, follow where it goes, then where that goes, and so on. Since the set is finite, you must eventually revisit something - and the first thing you revisit has to be your starting point, because injectivity forbids two different elements mapping into the same place. So you get a genuine cycle. Delete those elements and repeat on what's left. Every element lands in exactly one cycle, so the decomposition exists and is unique up to the rewritings we discussed.
Student: That's neat - the algorithm is the proof.
Tutor: It often is, in this subject. For practice, write out all six elements of S_3 in cycle notation and confirm you can build a multiplication table. Then, if you want the next thread to pull: every permutation can also be written as a product of transpositions - not disjoint ones, and not uniquely - but the parity of how many you use turns out to be well-defined. That's where the alternating group comes from."""

INTEGRAL_DOMAINS_BLIND = """Tutor: Before we put a name to anything, let me ask you something. You've been working with the integers for years. If I tell you that a times b equals zero, what can you conclude about a and b?
Student: That one of them has to be zero. Either a is zero or b is zero.
Tutor: Right. And that feels so obvious it's almost not worth saying. But here's the thing - it's a fact about the integers, not a fact about arithmetic in general. Let me show you something that breaks it. Do you remember arithmetic mod 6?
Student: Sure, you just take remainders after dividing by 6.
Tutor: Good. So tell me what 2 times 3 is in that system.
Student: Six, but six is zero mod 6. So it's zero.
Tutor: And neither 2 nor 3 is zero mod 6.
Student: Huh. So the thing I said is just false there.
Tutor: Exactly. That's the point. When we work abstractly with rings - sets with addition and multiplication behaving reasonably - the property you named is a genuine extra assumption, not something that comes free. Elements like 2 and 3 mod 6 get a name: they're called zero divisors. A nonzero element a is a zero divisor if there's some nonzero b with ab equal to zero.
Student: So an integral domain is a ring with no zero divisors?
Tutor: That's the heart of it. Formally: a commutative ring with a multiplicative identity 1, where 1 isn't 0, and which has no zero divisors. Equivalently, whenever ab is 0, at least one of a, b is zero. The integers are the model case - hence the name domain, from the old term domain of integrity.
Student: Why do we insist 1 isn't 0? That seems like a weird thing to have to say.
Tutor: Fair question. If 1 equals 0 in a ring, then for any element a you get a equals a times 1 equals a times 0 equals 0, so the whole ring collapses to a single element. That zero ring technically has no zero divisors, vacuously, but it's a degenerate nuisance - every theorem would need an exception clause for it. So we exclude it by fiat.
Student: Okay, that's reasonable. So what's a field then? I've heard the word but I don't have a crisp definition.
Tutor: A field is a commutative ring with 1 not equal to 0 in which every nonzero element has a multiplicative inverse. So you can divide by anything except zero. The rationals, the reals, the complex numbers - all fields. The integers are not.
Student: Because 2 has no integer inverse.
Tutor: Right, one half isn't an integer. So the integers are a domain but not a field. Now let me push you: is every field an integral domain?
Student: I want to say yes, but I'm not sure how to argue it. Let me think. Suppose ab is 0 and a isn't zero. Then a has an inverse, so multiply both sides by a inverse?
Tutor: Keep going.
Student: So a inverse times ab is a inverse times 0, which is 0. And the left side is b. So b is 0. So if ab is zero and a isn't, then b has to be. That's exactly no zero divisors.
Tutor: That's a clean proof, and it's the standard one. Fields are domains. The converse fails - the integers again. So field is strictly stronger.
Student: Is there a way to see which is which without hunting for inverses? Like, could I tell just by looking at the multiplication table mod n whether the integers mod n form a field?
Tutor: Excellent instinct, and yes. Try a couple. Is the integers mod 5 a field?
Student: Let's see. 2 times 3 is 6, which is 1. So 2 and 3 are inverses. 4 times 4 is 16, which is 1, so 4 is its own inverse. And 1 is its own inverse. So every nonzero element has one. Yes, it's a field.
Student: And mod 6 we already saw fails, because 2 times 3 is 0.
Tutor: So what's the pattern?
Student: 5 is prime, 6 isn't. So the integers mod n form a field exactly when n is prime?
Tutor: That's the theorem. And here's the pretty part of the proof: if n equals ab with both factors strictly between 1 and n, then a and b are nonzero mod n but their product is 0 - instant zero divisors, so not even a domain. And if n is prime, then for any nonzero a, the greatest common divisor of a and n is 1, so you can write ua plus vn equals 1 for some integers u and v. Reduce mod n and the vn term vanishes: ua equals 1. So u is the inverse of a.
Student: Oh, that's Bezout. Nice - the inverse just falls out of the gcd computation.
Tutor: It does, and that's also how you compute inverses in practice: extended Euclidean algorithm. Now, something slightly startling came out of that. For the integers mod n, being a domain and being a field turned out to be the same condition. That's not an accident.
Student: Wait, but you just said fields are strictly stronger. The integers are a domain and not a field.
Tutor: Right - and the integers are infinite. The theorem is: every finite integral domain is a field. Finiteness is doing the work.
Student: How would you prove that? I can't picture where finiteness gets used.
Tutor: Take a nonzero element a in a finite domain R, and look at the map that sends x to ax. Ask yourself whether that map is injective.
Student: Suppose ax equals ay. Then a times x minus y is zero, and a isn't zero, so x minus y is zero by the domain property. So x equals y. Yes, injective.
Tutor: And an injective map from a finite set to itself is what?
Student: Surjective. So 1 is hit by something, meaning ax equals 1 for some x, so a has an inverse. Oh, that's slick. And it obviously breaks for the integers because multiplying by 2 is injective but not surjective.
Tutor: Exactly the right diagnosis. Let me test one more thing. Is the ring of polynomials with real coefficients an integral domain? And is it a field?
Student: A domain, I think - if you multiply two nonzero polynomials, the degrees add and the leading coefficients multiply, so the product can't be zero. But it's not a field, because x doesn't have an inverse? There's no polynomial you can multiply x by to get 1.
Tutor: Correct, and your degree argument is the proof of both halves - degree of a product is the sum of degrees, so nothing of degree 1 or more can divide into a degree-0 polynomial. Notice that your first argument quietly used something: it needed the leading coefficients to multiply to something nonzero.
Student: Which is true over the reals because the reals are a domain. So polynomials over a domain form a domain, but polynomials over something with zero divisors might not?
Tutor: Precisely right, and that's a real phenomenon - over the integers mod 4, for instance, the polynomial 2x has square 4x squared, which is zero. So the coefficient ring's behavior propagates upward. That generalization you just made on your own is the actual theorem.
Student: One thing still nags at me. Why do we care about no zero divisors specifically? Out of all the properties we could demand, why is that the one worth naming?
Tutor: Because it's what makes cancellation work, and cancellation is what you lean on constantly without noticing. In a domain, ab equals ac with a nonzero lets you conclude b equals c - same one-line argument you gave for the injectivity. Without it, solving equations goes haywire: mod 6, the equation 2x equals 4 has x equals 2 and x equals 5 as solutions. Also, domains are exactly the rings you can embed in a field of fractions, the way the integers sit inside the rationals. That construction needs no zero divisors, or the fractions don't make sense.
Student: So a domain is sort of a ring that's on its way to being a field.
Tutor: That's a good way to hold it. Every domain sits inside a smallest field containing it, and finite domains skip the wait and are fields already. Before we stop - give me, from memory, one example each: a finite field, an infinite domain that isn't a field, and a commutative ring with 1 that isn't a domain.
Student: The integers mod 7 for the field. The integers for the domain that isn't a field - or polynomials over the reals. And the integers mod 6, or mod 4, for the ring with zero divisors.
Tutor: All three correct. Next time we'll look at ideals, where the same hierarchy shows up again - prime ideals are the ones whose quotient is a domain, maximal ideals the ones whose quotient is a field. You'll find the finite-domain theorem reappears there in disguise."""

CASES = (
    ("NORMAL_SUBGROUPS_BLIND", NORMAL_SUBGROUPS_BLIND,
     "judson:10.1-factor-groups-and-normal-subgroups"),
    ("PERMUTATION_GROUPS_BLIND", PERMUTATION_GROUPS_BLIND,
     "judson:5.1-definitions-and-notation"),
    ("INTEGRAL_DOMAINS_BLIND", INTEGRAL_DOMAINS_BLIND,
     "judson:16.2-integral-domains-and-fields"),
)


def _gap(text):
    """(winner, winner_coverage, best-covered rival, rival_coverage, gap) at the raw tier."""
    tw = _words(text)
    raw = score_candidates(text, INDEX)
    top = raw[0]
    cov_top = _coverage_fraction(top, INDEX, tw)
    rival, cov_rival = max(
        ((c, _coverage_fraction(c, INDEX, tw)) for c in raw[1:]),
        key=lambda pair: pair[1], default=(None, 0.0),
    )
    return top, cov_top, rival, cov_rival, cov_rival - cov_top


def test_no_case_is_a_confident_wrong_answer():
    """THE SAFETY GATE, written before any measurement was taken.

    This module's own priority (`_MIN_WINNING_COVERAGE`'s comment) ranks a
    false abstention as strictly cheaper than a confident wrong answer. So the
    property every one of these three blind, on-topic lessons must satisfy is
    the weakest one that still forbids the teach-jkx failure: recover the
    right node, or abstain with a reason -- never confidently name a node that
    is not the topic.

    This is deliberately NOT an assertion that all three recover correctly.
    teach-9ba and teach-jkx both established that genuine, on-topic blind
    lessons in this graph legitimately abstain (judson:16.1-rings' broad
    52-word vocabulary out-raw-scores many group-theory topics, and the
    coverage-gap veto correctly catches it). Demanding recovery here would be
    demanding the bug's absence AND the abstention's absence at once, which
    no value of any threshold in this module delivers.
    """
    for name, text, expected in CASES:
        result = recover_from_lesson_text(text, GRAPH)
        if result.taught_node_id is not None:
            assert result.taught_node_id == expected, (
                f"{name}: CONFIDENT WRONG ANSWER -- recovered "
                f"{result.taught_node_id!r}, expected {expected!r} or an abstention"
            )
            assert result.abstain_reason is None, name
        else:
            assert result.abstain_reason, f"{name}: abstained with no reason"


def test_the_true_topic_is_always_a_scoring_candidate():
    """Whatever the resolver decides, the correct node must at least be SEEN.

    If the true topic did not score at all, an abstention here would be
    uninformative -- it would mean the vocabulary index cannot represent the
    lesson, not that the resolver made a defensible call. Gating this
    separately keeps the safety gate above honest.
    """
    for name, text, expected in CASES:
        scored = {c.node_id for c in score_candidates(text, INDEX)}
        assert expected in scored, f"{name}: {expected} never scored at all"


def test_raw_tier_resolution_matches_the_full_pipeline_or_abstains():
    """The raw tier must not be the thing that introduces a wrong answer.

    teach-jkx's bug lives in the SEMANTIC fallback: the raw tier abstained
    correctly and the semantic tier then produced the confident wrong answer.
    This pins the raw tier's own behaviour on these three texts independently,
    so a future change that breaks the raw tier cannot hide behind the
    pipeline result.
    """
    for name, text, expected in CASES:
        tw = _words(text)
        raw_id, raw_abstain = _resolve_candidates(score_candidates(text, INDEX), INDEX, tw)
        if raw_id is not None:
            assert raw_id == expected, f"{name}: raw tier named {raw_id!r}, expected {expected!r}"
        else:
            assert raw_abstain, f"{name}: raw tier abstained with no reason"


def test_coverage_gaps_are_recorded_for_threshold_calibration():
    """Records each case's raw-tier coverage gap -- the quantity lead (a) moves.

    No threshold is asserted here on purpose. This test exists so the three
    gaps are measured and version-controlled by a round that was authored
    before any threshold decision, which is exactly what teach-jkx's
    remaining leads lack. A later change to _DECISIVE_MARGIN_COVERAGE_GAP must
    be argued against these numbers, not against the four cases that motivated
    it.
    """
    for name, text, expected in CASES:
        top, cov_top, rival, cov_rival, gap = _gap(text)
        assert top is not None and rival is not None, name
        assert 0.0 <= cov_top <= 1.0 and 0.0 <= cov_rival <= 1.0, name
        assert -1.0 <= gap <= 1.0, (name, gap)
