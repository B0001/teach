"""teach-jkx round 10: the final fresh, independently-authored held-out round
used to validate session 5's fix -- capping the SEMANTIC tier's own score
inflation for the winning candidate at a bounded multiple of its raw-tier
score (`_SEMANTIC_INFLATION_CAP_RATIO`, currently 1.25), applied inside
`_resolve_candidates` via the new `raw_scores` parameter.

WHY THIS ROUND EXISTS. Sessions 1-4 falsified five directions and one
threshold-move lead, and instrumented away the last threshold-move lead
(winner's-own-coverage floor -- confirmed-correct recoveries exist as low as
8.1% coverage, so no floor separates them from the bug). Session 5's fix is
structurally different: it targets the bug's own named root cause (uneven
WordNet synonym inflation between the winner and rival at the semantic tier)
by capping the winner's inflated score directly, rather than gating a derived
ratio or coverage number. This lineage's rule (teach-ceg, teach-i35, restated
in teach-jkx's own notes) is that a fix may not be validated only against the
fixture that motivated it (GROUP_AXIOMS_BLIND, round7) or against fixtures
authored in the same session that invented the fix. This round supplies that:
three topics, three separate parallel blind `Agent` tool calls, each given an
explicit no-tool-use, no-repository-access, no-internet instruction and told
nothing about concept_recovery.py, this bead, any threshold, or any mechanism
in this module -- only a plain-English topic name (cyclic groups and
generators; group homomorphisms; Lagrange's theorem) and a request to render
it as a natural tutor/student dialogue from the agent's own general
abstract-algebra knowledge. All three returned with zero tool calls,
confirming the blind condition held.

TOPIC CHOICE. Two topics (cyclic groups, Lagrange's theorem) were chosen
because they are exactly the shape of lesson teach-jkx is about: on-topic,
never mentions rings, but shares enough generic algebra vocabulary
(subgroup, element, order, divides, finite, identity) that judson:16.1-rings'
broad vocabulary is a plausible raw-tier rival -- the same shape that put
GROUP_AXIOMS_BLIND's raw tier into the semantic fallback in the first place.
The third (group homomorphisms) was chosen to stress a different sibling-node
adjacency (group homomorphisms vs. ring homomorphisms) and, unexpectedly,
surfaced a SEPARATE bug -- see below.

MEASURED ONCE against the fixed tree
(`_SEMANTIC_INFLATION_CAP_RATIO = 1.25`), through the public entry point:

  CYCLIC_GROUPS_BLIND       raw tier abstains (best raw candidate
      judson:18.2-factorization 12/24% vs. judson:4.1-cyclic-subgroups
      9/82% -- ambiguous-decisive-gap abstention). Semantic tier is then
      tried and ALSO abstains, with the fix's cap now in effect. Safe.
  LAGRANGES_THEOREM_BLIND   raw tier abstains (best raw candidate
      judson:6.2-lagranges-theorem 13 vs. judson:16.1-rings 11 --
      ambiguous). Semantic tier tried, ALSO abstains under the fix. Safe.
  GROUP_HOMOMORPHISMS_BLIND raw tier ALONE resolves CONFIDENTLY to
      judson:16.3-ring-homomorphisms-and-ideals (score 20) over
      judson:16.1-rings (12), never reaching the semantic tier at all, with
      the true topic judson:11.1-group-homomorphisms scoring only 6 --
      not even runner-up. This is a CONFIDENT WRONG ANSWER, but it is NOT
      teach-jkx's mechanism: no semantic/WordNet tier is involved, so
      session 5's fix cannot touch it (and does not -- the raw tier result
      is identical with and without the fix). Root cause looks structurally
      different: judson:16.3's own node text is long and explicitly explains
      ring homomorphisms BY ANALOGY to group homomorphisms ("Similarly, a
      homomorphism between rings preserves...", "Just as with group
      homomorphisms and normal subgroups..."), so its distinctive vocabulary
      legitimately, literally overlaps a group-homomorphisms lesson. Filed
      as its own bead, teach-zgn, rather than folded into teach-jkx's scope.

THIS ROUND THEREFORE VALIDATES TWO THINGS AT ONCE: the fix behaves safely on
fresh material that exercises the exact mechanism it targets (the semantic
tier), and the fix does NOT mask or paper over an unrelated raw-tier bug it
was never meant to fix -- teach-zgn's pinned test below asserts the bug is
still visibly present and unfixed, so this round cannot be mistaken for
having "solved" it.
"""

from teach.concept_recovery import (
    build_vocabulary_index,
    recover_from_lesson_text,
    score_candidates,
    score_candidates_semantic,
    _resolve_candidates,
    _words,
)
from teach.judson_algebra_graph import load_judson_full_graph

GRAPH = load_judson_full_graph()
INDEX = build_vocabulary_index(GRAPH)

CYCLIC_GROUPS_BLIND = """Tutor: Let's talk about cyclic groups today. Have you seen the definition of a group yet — set with an operation, identity, inverses, associativity?

Student: Yeah, I've got that down. But "cyclic" is throwing me off. What makes a group cyclic?

Tutor: A group G is cyclic if there's some single element g in G such that every element of G can be written as a power of g. In additive notation that means every element is some integer multiple of g; in multiplicative notation, every element is g raised to some integer power.

Student: So the whole group is basically "generated" by repeatedly combining one element with itself?

Tutor: Exactly. That element g is called a generator. We write G = ⟨g⟩ to mean "the group generated by g."

Student: Can you give me a concrete example? Abstract definitions never stick until I see numbers.

Tutor: Sure. Take the integers under addition, Z. Is that cyclic?

Student: Hmm, every integer is a multiple of 1, so... yes? 1 generates it?

Tutor: Right. And notice -1 also generates it, since every integer is also a multiple of -1. So a cyclic group can have more than one generator.

Student: Okay that makes sense for Z, which is infinite. What about a finite example?

Tutor: Let's use Z/nZ, the integers mod n, under addition. Take n = 6, so we have {0,1,2,3,4,5} with addition mod 6. Is 1 a generator?

Student: Let me compute. 1, 1+1=2, 3, 4, 5, and then 1+1+1+1+1+1 = 6 which is 0 mod 6. So I get 1,2,3,4,5,0 — that's everything.

Tutor: Right, so ⟨1⟩ = Z/6Z. Now here's the key question: does every element of Z/6Z generate the whole group?

Student: Let me check 2. 2, 4, 6=0, 8=2... wait I'm just cycling through 2, 4, 0. That's only three elements, not six.

Tutor: Good catch. So 2 does not generate Z/6Z — it only generates the subgroup {0,2,4}. Why do you think that happens?

Student: Because 2 and 6 share a common factor? gcd(2,6) = 2.

Tutor: That's exactly the right instinct. In general, for Z/nZ, the element k generates the whole group if and only if gcd(k,n) = 1.

Student: So for n=6, the generators would be the numbers coprime to 6, which are 1 and 5?

Tutor: Check it yourself — try 5.

Student: 5, 5+5=10=4, 15=3, 20=2, 25=1, 30=0. So I got 5,4,3,2,1,0 — all six elements. Yes, 5 works too.

Tutor: Great. And that count of generators — the number of integers from 1 to n that are coprime to n — has a name.

Student: Isn't that Euler's totient function, φ(n)?

Tutor: Exactly. φ(6) = 2, matching the two generators we found, 1 and 5.

Student: This is starting to connect. Now, what's the "order" of an element? I keep seeing that term.

Tutor: The order of an element g is the smallest positive integer m such that combining g with itself m times gives the identity. In Z/nZ with addition, that means the smallest positive m with m·g ≡ 0 mod n.

Student: So for 2 in Z/6Z, we found 2,4,0 — that took 3 steps to hit 0. So the order of 2 is 3?

Tutor: Correct. And notice 3 divides 6. That's not a coincidence — in any finite group, the order of an element always divides the order of the group.

Student: Is there a formula for the order of k in Z/nZ, rather than just listing multiples?

Tutor: Yes: the order of k in Z/nZ is n / gcd(k,n). Try it for k=2, n=6.

Student: gcd(2,6)=2, so order is 6/2 = 3. Matches what I found by brute force.

Tutor: And for a generator, we need the order to equal n itself, meaning n/gcd(k,n) = n, which forces gcd(k,n) = 1. That's the same condition as before, just derived a different way.

Student: That ties it together nicely. One more thing — is every cyclic group basically "the same" as Z or Z/nZ?

Tutor: In a precise sense, yes. Every infinite cyclic group is structurally identical to Z, and every finite cyclic group of order n is structurally identical to Z/nZ. That's essentially the classification theorem for cyclic groups — up to relabeling elements, there's only one cyclic group of each size, plus one infinite one.

Student: So once I understand Z/nZ, I basically understand every cyclic group?

Tutor: That's the right takeaway. The specific elements might be rotations of a polygon, roots of unity, or residues mod n, but the underlying structure — generated by one element, with the generator condition tied to coprimality when finite — is always the same.

Student: This makes cyclic groups feel a lot less mysterious. Thanks — I want to go compute the generators of Z/12Z now just to practice.

Tutor: Perfect exercise. Figure out φ(12) first, then list which residues are coprime to 12, and check a couple of orders to build your intuition."""

GROUP_HOMOMORPHISMS_BLIND = """Tutor: Today let's look at homomorphisms between groups. Do you remember what a group is — set, operation, identity, inverses?

Student: Yes, I've got groups down. But what's a homomorphism exactly?

Tutor: A homomorphism is a function between two groups that respects the group operation. If G and H are groups and f: G → H is a function, f is a homomorphism if for all a, b in G, f(a * b) = f(a) *' f(b), where * is the operation in G and *' is the operation in H.

Student: So it doesn't matter whether I combine first in G and then map, or map first and then combine in H — I get the same answer either way?

Tutor: Precisely. That's the defining property, and it's really the whole point: the function preserves the algebraic structure, not just some vague "similarity" between the sets.

Student: Can you give me a concrete example so I can see it in action?

Tutor: Sure. Let G be the integers under addition, and H be Z/nZ, also under addition. Define f(x) = x mod n. Is that a homomorphism?

Student: Let's check. f(a+b) should equal f(a) + f(b) mod n. And (a+b) mod n is indeed the same as (a mod n) + (b mod n), reduced mod n. So yes, that works.

Tutor: Exactly right. That's called the reduction-mod-n map, and it's one of the most useful homomorphisms you'll encounter.

Student: What happens to the identity element under a homomorphism?

Tutor: Good question — it's always forced. If e_G is the identity in G, then f(e_G) must be the identity e_H in H. You can prove it: f(e_G) = f(e_G * e_G) = f(e_G) *' f(e_G), and then cancel one copy of f(e_G) from both sides using inverses in H, leaving f(e_G) = e_H.

Student: And what about inverses — does f(a⁻¹) = f(a)⁻¹?

Tutor: Yes, that follows too. Since a * a⁻¹ = e_G, applying f gives f(a) *' f(a⁻¹) = e_H, which means f(a⁻¹) is the inverse of f(a) in H.

Student: Okay, now I keep hearing "kernel" and "image" — what are those?

Tutor: The kernel of f is the set of all elements in G that map to the identity in H. Formally, ker(f) = { a in G : f(a) = e_H }. The image is the set of all values f actually hits in H: im(f) = { f(a) : a in G }.

Student: For your mod-n example, what's the kernel?

Tutor: Think about it — which integers map to 0 under x mod n?

Student: The multiples of n. So the kernel is nZ, all integer multiples of n.

Tutor: Exactly. And the image?

Student: Since every residue class 0 through n-1 gets hit, the image is all of Z/nZ.

Tutor: Right, so this particular homomorphism is surjective — its image is the entire target group. Now, here's an important fact: the kernel is always a subgroup of G, and in fact it's a special kind called a normal subgroup. And a homomorphism is injective — one-to-one — exactly when its kernel contains only the identity element.

Student: Why does a trivial kernel imply injectivity?

Tutor: Suppose f(a) = f(b). Then f(a) *' f(b)⁻¹ = e_H, and using the homomorphism property this becomes f(a * b⁻¹) = e_H, meaning a * b⁻¹ is in the kernel. If the kernel is trivial, that forces a * b⁻¹ = e_G, so a = b. That's injectivity.

Student: That's a slick argument. Can you show me a non-example now — something that looks like it might be a homomorphism but isn't?

Tutor: Sure. Let G = H = the nonzero real numbers under multiplication, and define f(x) = x + 1. Is that a homomorphism?

Student: Let's test it. We'd need f(a*b) = f(a)*f(b), meaning ab + 1 should equal (a+1)(b+1) = ab + a + b + 1. Those aren't equal unless a + b = 0, which isn't true for all a, b.

Tutor: Right, so that function fails to respect the operation — it's just some function between two groups, not a homomorphism. The operation gets mangled.

Student: What would be a better non-example, something a student might plausibly mistake for a homomorphism?

Tutor: How about f: Z → Z under addition, defined by f(x) = x + 5?

Student: Check: f(a+b) = a + b + 5. And f(a) + f(b) = (a+5) + (b+5) = a + b + 10. Those don't match unless 5 = 10, which is false. So that's not a homomorphism either, even though it "looks" additive because of the plus sign.

Tutor: Exactly — a common trap. Adding a constant shifts the identity away from mapping to the identity, which we proved earlier is forbidden for any genuine homomorphism.

Student: That's a good sanity check to remember: does the identity map to the identity? If not, stop right there.

Tutor: Precisely, it's a fast first test, though satisfying it doesn't guarantee a homomorphism — you still need to check the full property for arbitrary elements, not just the identity.

Student: One more example, please — something a bit richer than mod-n reduction.

Tutor: Let's do the determinant. Let G be the group of invertible n-by-n matrices under matrix multiplication, and H be the nonzero real numbers under multiplication. Define f(A) = det(A).

Student: And the defining property would be det(AB) = det(A)det(B), which I remember is a real theorem from linear algebra.

Tutor: Exactly, so determinant is a genuine group homomorphism. Its kernel — matrices with determinant 1 — is a well-known subgroup called the special linear group, and its image is all of the nonzero reals, since you can always find a matrix with any given nonzero determinant.

Student: This is clicking now. Homomorphisms are basically the "structure-preserving" maps of group theory, kernel measures the failure of injectivity, and image measures how much of the target you actually reach.

Tutor: That's a great summary. Next time we can talk about how the kernel and image relate via the isomorphism theorems, but for now, practice checking the homomorphism property on a few maps of your own choosing, including ones you suspect will fail.

Student: Will do — I want to try f(x) = 2x on the integers under addition next.

Tutor: Good choice, work it out and see what the kernel and image turn out to be."""

LAGRANGES_THEOREM_BLIND = """Tutor: Let's talk about Lagrange's theorem today. Do you know what it says, even roughly?

Student: I've heard it's about subgroups and divisibility, but I don't remember the exact statement.

Tutor: Here it is: if G is a finite group and H is a subgroup of G, then the order of H divides the order of G. "Order" here just means the number of elements.

Student: So if G has, say, 12 elements, then any subgroup can only have 1, 2, 3, 4, 6, or 12 elements? Not 5 or 7?

Tutor: Exactly right. Those are the only possible subgroup sizes, since those are the only divisors of 12. It doesn't mean subgroups of every one of those sizes must exist, just that no subgroup can have a size outside that list.

Student: That's a strong restriction. Why would that be true in general?

Tutor: The proof goes through something called cosets. Given a subgroup H of G, and any element g in G, we form the set gH = { g*h : h in H }, called a left coset of H.

Student: What does a coset actually look like? Can you give me a picture?

Tutor: Think of H sitting inside G as one chunk of elements. Then gH is that same chunk, shifted by g — take every element of H and multiply it by g on the left. Each choice of g gives you a subset of G the same size as H.

Student: Same size? Why can't the coset be smaller, if some products happen to collide?

Tutor: Good question. The map h ↦ g*h is invertible — you can undo it by multiplying by g⁻¹ — so it's a bijection from H to gH. A bijection between finite sets means they have exactly the same number of elements. So every coset has exactly |H| elements, no collisions possible.

Student: Okay. Now why do these cosets help prove the divisibility?

Tutor: The key fact is that the collection of all left cosets of H partitions G. That means every element of G lands in exactly one coset, and two cosets are either identical or completely disjoint — they never partially overlap.

Student: Why can't two cosets partially overlap?

Tutor: Suppose gH and g'H share a common element. Then that element equals g*h1 for some h1 in H, and also g'*h2 for some h2 in H. From that you can derive that g' = g*h1*h2⁻¹, which is g times something in H, so g' is actually in gH. Once that happens, you can show every element of g'H is also in gH, and vice versa — so the two cosets are forced to be exactly equal, not just overlapping.

Student: So each element of G falls into exactly one coset, and every coset has the same size as H.

Tutor: Exactly. So if there are k distinct cosets, the total count of elements in G is k times |H|, since the cosets don't overlap and together they cover everything. That means |G| = k * |H|, so |H| divides |G|.

Student: That's clean. The number k — the number of distinct cosets — does that have a name?

Tutor: Yes, it's called the index of H in G, usually written [G : H]. And the equation becomes |G| = [G : H] * |H|.

Student: Can we do a concrete example? Something small enough to see all the cosets explicitly.

Tutor: Let's use G = Z/8Z under addition, which has order 8, and let H = {0, 4}, the subgroup generated by 4.

Student: H has order 2. Let's find the cosets. 0 + H = {0,4}. 1 + H = {1,5}. 2 + H = {2,6}. 3 + H = {3,7}. And 4 + H would just be {4,0} again, same as the first one.

Tutor: Right, so we get four distinct cosets: {0,4}, {1,5}, {2,6}, {3,7}, and together they cover all 8 elements with no overlap. So |G| = 8, |H| = 2, and the index is 4, confirming 8 = 4 × 2.

Student: Nice, that matches perfectly. Can you show me one more, maybe with a non-abelian group so I see it's not just an additive-group trick?

Tutor: Sure. Consider the symmetries of an equilateral triangle — three rotations (including the identity rotation) and three reflections, six symmetries total, so |G| = 6. Take H to be the subgroup of rotations only: the identity, rotate 120 degrees, and rotate 240 degrees. That's a subgroup of order 3.

Student: And 3 divides 6, so that's consistent with the theorem.

Tutor: Right, and here the index [G:H] is 2 — there are exactly two cosets: the rotations themselves, and the coset formed by picking any reflection and combining it with each rotation, which turns out to be exactly the three reflections.

Student: So the whole group splits into "the rotations" and "the reflections," each a coset of size 3.

Tutor: Exactly. Now here's an important corollary that falls straight out of Lagrange's theorem: the order of any single element also divides the order of the group, because the cyclic subgroup generated by that element is itself a subgroup, and its order equals the order of the element.

Student: So if G has 6 elements, no element can have order 4, only order 1, 2, 3, or 6?

Tutor: Correct — order 4 is impossible in a group of size 6, since 4 doesn't divide 6.

Student: I want to make sure I understand the limits of the theorem. Does Lagrange's theorem guarantee a subgroup exists for every divisor?

Tutor: No, and that's a common misconception. The theorem only rules out sizes that don't divide |G| — it doesn't promise a subgroup for every divisor that does. There are groups of order 12, for instance, with no subgroup of order 6, even though 6 divides 12. Lagrange gives you a necessary condition on subgroup size, not a sufficient one.

Student: That distinction is important — it's a one-directional divisibility constraint, not an existence guarantee.

Tutor: Exactly the right way to phrase it. For your practice, try listing all possible subgroup orders for a group of order 20, and then see if you can find explicit subgroups of at least a couple of those sizes in a group you already know, like Z/20Z.

Student: I'll start with the divisors of 20 — 1, 2, 4, 5, 10, 20 — and try to construct subgroups of each size inside Z/20Z using generators.

Tutor: Good plan — since Z/20Z is cyclic, you'll actually find a subgroup of every one of those sizes, which is a nice special property of cyclic groups that doesn't hold for general groups."""

SAFE_CASES = [
    ("CYCLIC_GROUPS_BLIND", CYCLIC_GROUPS_BLIND, "judson:4.1-cyclic-subgroups"),
    ("LAGRANGES_THEOREM_BLIND", LAGRANGES_THEOREM_BLIND, "judson:6.2-lagranges-theorem"),
]


def test_no_case_is_a_confident_wrong_answer():
    """THE SAFETY GATE for the semantic-tier-exercising cases, written before
    any measurement beyond the initial diagnostic run was recorded here.

    Recovering the right node or abstaining with a reason are both
    acceptable; only a confident wrong answer is not. This mirrors round9's
    gate, but these two cases are the ones that actually reach the semantic
    tier (round9's cases all resolved or abstained at the raw tier alone),
    so this is the round that actually exercises session 5's fix.
    """
    for name, text, expected in SAFE_CASES:
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
    """Whatever the resolver decides, the correct node must at least be SEEN."""
    for name, text, expected in SAFE_CASES:
        scored = {c.node_id for c in score_candidates(text, INDEX)}
        assert expected in scored, f"{name}: {expected} never scored at all"


def test_raw_tier_abstains_so_the_semantic_tier_is_what_is_actually_tested():
    """Confirms these two cases reach the semantic tier at all.

    If the raw tier resolved confidently here, the semantic tier (and
    session 5's fix inside it) would never run, and this round would not
    actually validate anything about the fix -- it would just be another
    round9-shaped raw-tier case. Pinning the raw tier's own abstention here
    makes that failure mode visible if it ever stops holding.
    """
    for name, text, expected in SAFE_CASES:
        tw = _words(text)
        raw_id, raw_abstain = _resolve_candidates(score_candidates(text, INDEX), INDEX, tw)
        assert raw_id is None, (
            f"{name}: raw tier already resolved to {raw_id!r} -- this case no "
            f"longer exercises the semantic tier and does not validate teach-jkx's fix"
        )
        assert raw_abstain, f"{name}: raw tier abstained with no reason"


def test_group_homomorphisms_confident_wrong_answer_is_teach_zgn_not_teach_jkx():
    """teach-zgn fixed the bug this round surfaced. Root cause: judson:11.1's
    hand-authored vocabulary never mentioned "image" or "injective" -- two
    of the most basic things a lesson on group homomorphisms talks about
    (kernel's usual companion concept, and the standard injective/trivial-
    kernel characterization) -- even though Judson's own text (ch. 11,
    "Group Homomorphisms") covers both. That left judson:11.1 too thin to
    ever look credible against judson:16.3-ring-homomorphisms-and-ideals,
    a long, verbatim-extracted node that racks up incidental raw overlap
    with ordinary "homomorphism" prose. The fix adds "injective" and
    "image" -- both drawn from the real Judson source (ch. 11, commit
    3069910e3ded72ff5e18837a97a0e810c92790e2) -- to judson:11.1's key_terms
    and definition. Measured: this raises judson:11.1's raw overlap on
    GROUP_HOMOMORPHISMS_BLIND from 6 to 12 and its own-vocabulary coverage
    from 66.7% to 86%, which now clears the decisive-margin credibility
    gate (`_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO`) and coverage-gap veto
    (`_DECISIVE_MARGIN_COVERAGE_GAP`) against judson:16.3's 37% coverage of
    its own vocabulary -- a safe abstention, not a confident wrong answer,
    since judson:11.1 does not decisively outscore judson:16.3 outright.

    Measured (this exact fixture, teach-full graph): before the fix,
    judson:11.1 scored 6 (85.7% of its own then-7-word vocabulary) --
    below `_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO * 20 = 7.0`, so it was
    never even considered a credible rival to judson:16.3's 20/37%. After
    the fix, judson:11.1 scores 8 (80.0% of its now-10-word vocabulary),
    clearing that 7.0 bar and forcing the coverage-gap comparison that
    vetoes judson:16.3's decisive-but-barely-covered raw lead."""
    result = recover_from_lesson_text(GROUP_HOMOMORPHISMS_BLIND, GRAPH)
    assert result.taught_node_id is None, (
        f"expected a safe abstention now that teach-zgn's vocabulary fix is "
        f"in place -- got {result.taught_node_id!r} instead; if this is "
        f"'judson:16.3-ring-homomorphisms-and-ideals' the fix regressed"
    )
    assert result.abstain_reason is not None


def test_group_homomorphisms_bug_is_raw_tier_not_semantic_tier():
    """Confirms teach-zgn's fix resolves the bug at the RAW tier -- the same
    tier that decided the wrong answer before the fix -- rather than merely
    relocating it to the semantic fallback tier (session 5's mechanism,
    already fixed for RING_HOMOMORPHISMS/HOMOMORPHISMS by
    `_SEMANTIC_INFLATION_CAP_RATIO`). If this ever starts asserting the raw
    tier again returns judson:16.3-ring-homomorphisms-and-ideals with no
    abstain reason, teach-zgn's fix has regressed.
    """
    tw = _words(GROUP_HOMOMORPHISMS_BLIND)
    raw_id, raw_abstain = _resolve_candidates(
        score_candidates(GROUP_HOMOMORPHISMS_BLIND, INDEX), INDEX, tw
    )
    assert raw_id is None
    assert raw_abstain is not None
