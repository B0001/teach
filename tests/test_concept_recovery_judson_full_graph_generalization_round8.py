"""teach-ceg: this bead's own required fresh held-out round, run before
closing (see teach-ceg's description: "Any fix must not use this bead's own
SETS_EQUIVALENCE fixture ... to validate -- it is now tuning data -- and
needs its own fresh held-out round before closing").

By the time this round was written, every one of the 20 nodes in
`load_judson_full_graph()` already had at least one fixture somewhere in
rounds 1-7 -- there is no topic left in this graph that has never been used
as a fixture. "Fresh" here therefore means what the rest of this lineage has
already established it means when the graph itself runs out of unused nodes
(see round4's own opening docstring, re-authoring round3's named-but-lost
topics from scratch): newly, independently authored dialogue text on a topic
already in the graph, produced blind and measured once, not a topic nobody
has ever touched. Two of the three topics here (cosets, judson:6.1; group
homomorphisms, judson:11.1) are historically the most fragile ones in this
lineage -- HOMOMORPHISMS was teach-9wx's original bug, and cosets/Lagrange's
theorem is the exact rival pair `_DECISIVE_MARGIN_COVERAGE_GAP` was calibrated
never to break (see that constant's SIGNPOSTED_LESSON comment in
concept_recovery.py) -- chosen deliberately to stress the mechanism teach-ceg
changed, not to find the easiest possible pass.

All three lesson texts below were produced by three separate, parallel
`Agent` tool calls, each given an explicit no-tool-use, no-repository-access
instruction and told nothing about concept_recovery.py, this bead, or any
threshold or mechanism in this module -- only a plain-English topic name and
a request to render it as a natural tutor/student dialogue from the agent's
own general abstract-algebra knowledge, with no reference to any specific
textbook. None of the three agents saw another's output, this module's code,
or any prior round's fixtures.

HONEST RESULT (measured once against the real, unmodified, current-tree
`load_judson_full_graph()`, via the public `recover_from_lesson_text` /
`score_candidates` / `_resolve_candidates` entry points only -- no internals
were read to choose or adjust these lesson texts, and no threshold or word
list in concept_recovery.py was changed in response to seeing these results):

  correct recoveries:      0 / 3
  safe abstentions:        3 / 3  (COSETS_FRESH, ISOMORPHISMS_FRESH,
                                    GROUP_HOMOMORPHISMS_FRESH)
  CONFIDENT WRONG ANSWERS: 0 / 3

Zero confident wrong answers is the property teach-ceg's own bar cares about
(the bead's named bug was SETS_EQUIVALENCE landing exactly one point under
the old 0.25 veto threshold and being confidently misnamed -- a coverage-gap
near-miss). None of these three all-safe outcomes is itself a strong
generalization claim (0/3 correct is a real, disclosed recall cost, not a
free win -- see the per-test docstrings for exactly why each one abstains),
but that is consistent with this lineage's own stated priority that a false
abstention is cheaper than a confident wrong answer, and none of the three
is a confident wrong answer.

Most directly relevant to teach-ceg's own mechanism: COSETS_FRESH hits the
exact decisive-margin `_DECISIVE_MARGIN_COVERAGE_GAP` branch this bead
changed (see `test_cosets_fresh_hits_decisive_margin_coverage_gap_veto`
below), landing at a 20-point coverage gap -- 2 points clear of the new
0.18 threshold, on text nobody wrote with that threshold in mind. That is
a genuine, if narrow, confirmation that 0.18 does not itself have a
near-miss failure in the same direction as the bug this bead fixed. It is
one data point, not a proof the boundary is safe everywhere; a future round
that happens to land a gap between 18 and 25 points (the zone the old
threshold would have vetoed and the new one might not, depending on which
side) would be the sharper test, and none of these three happened to land
there.

ISOMORPHISMS_FRESH and GROUP_HOMOMORPHISMS_FRESH both abstain via a
different branch entirely (the bare-minimum-margin "too close to call" path,
not the decisive-margin path teach-ceg touched) -- included for the record
because they stress the two topics most associated with this lineage's
history of confident-wrong-answer bugs, and because a null result there
(no NEW failure mode surfacing) is itself worth recording, not because they
individually validate `_DECISIVE_MARGIN_COVERAGE_GAP`.
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


COSETS_FRESH = """Tutor: You've seen that subgroups act like little copies of a group sitting inside it. Today let's ask: if H is a subgroup of G, what happens when you shift H by some element?

Student: Shift it how?

Tutor: Pick g in G and form the set gH -- meaning every element of H, multiplied on the left by g. That's called a left coset of H.

Student: So it's just H moved somewhere else in G?

Tutor: Exactly. And you can also multiply on the right, getting Hg -- a right coset. In general gH and Hg aren't the same set unless the group is abelian, or g happens to commute with everything in H.

Student: Okay, so we get a bunch of these shifted copies. What's special about them?

Tutor: Here's the key fact: the left cosets of H partition G. Every element of G lies in exactly one left coset.

Student: Why exactly one? Couldn't an element land in two different shifted copies?

Tutor: Suppose x is in both aH and bH. Then x = ah1 = bh2 for some h1, h2 in H. Solve for a: a = bh2h1 inverse. Since h2h1 inverse is in H, that means a is in bH. And once a is in bH, you can show aH and bH are literally the same set -- multiply through and use closure of H.

Student: So "sharing one element" forces the cosets to be identical.

Tutor: Right. Two cosets are either disjoint or identical, never partially overlapping. Combined with the fact that every g is in its own coset gH -- since e is in H, g = ge is in gH -- that's exactly what it means to partition G.

Student: And each of these pieces is the same size?

Tutor: Yes -- the map h to gh from H to gH is a bijection, since it has an inverse, multiplying by g inverse. So every coset has exactly the same number of elements as H, regardless of which g you picked.

Student: I think I see where this is going. If G is finite, we've chopped it into equal-sized pieces...

Tutor: ...and the number of pieces times the size of each piece has to equal the size of G. That number of pieces is called the index of H in G. So the order of G equals the index times the order of H, which means the order of H divides the order of G.

Student: That's Lagrange's theorem.

Tutor: Exactly -- and notice it fell out almost for free once we had the partition. The hard work was showing cosets tile the group cleanly; the divisibility is just counting after that.

Student: So the takeaway is: cosets aren't just a bookkeeping device, they're literally why subgroup order has to divide group order.

Tutor: That's the idea. Next time, we'll use this same partition to build the quotient group, once we ask when the cosets themselves can be multiplied together consistently."""

ISOMORPHISMS_FRESH = """Tutor: Ready to talk about isomorphisms?

Student: I think so. It's about two groups being "the same," right?

Tutor: Structurally the same, yes. Formally, an isomorphism from a group G to a group H is a function phi from G to H that's a bijection -- one-to-one and onto -- and also a homomorphism, meaning phi(ab) = phi(a)phi(b) for all a, b in G.

Student: So it's a relabeling. It matches up elements, but keeps the multiplication table consistent.

Tutor: Exactly. If phi is an isomorphism, then G and H have identical structure -- same order, same element orders, same subgroup lattice, everything. Any property you can phrase purely in terms of the group operation transfers across.

Student: Can we do an example?

Tutor: Take G, the integers mod 4 under addition, and H, the group of fourth roots of unity under multiplication. Define phi(k) as i to the k.

Student: So phi(0) = 1, phi(1) = i, phi(2) = -1, phi(3) = -i.

Tutor: Right, and that's clearly a bijection -- four elements map to four elements, no repeats. Now check the homomorphism property: phi(a+b mod 4) should equal phi(a)phi(b). Try a=2, b=3: phi(2+3 mod 4) = phi(1) = i. And phi(2)phi(3) = (-1)(-i) = i. Matches.

Student: Because adding exponents mod 4 corresponds to multiplying powers of i, since i to the 4 is 1.

Tutor: Precisely -- the exponent arithmetic naturally happens mod 4. So the two groups are isomorphic.

Student: Now what about two groups of the same order that aren't isomorphic?

Tutor: Classic case: the integers mod 4 versus the Klein four-group, which is the direct product of two copies of the integers mod 2. Both have order 4.

Student: But they can't be isomorphic?

Tutor: Look at element orders. The integers mod 4 has an element of order 4 -- namely 1, since 1+1+1+1=0 but no smaller sum is 0. Does the Klein four-group have any element of order 4?

Student: Every nonidentity element there satisfies x+x=0, so every nonidentity element has order 2.

Tutor: So its element orders are all 1 or 2, while the integers mod 4 has an element of order 4. If there were an isomorphism between them, it would have to send the order-4 element to an element of the same order in the other group. There isn't one.

Student: So having an isomorphism preserve element order is what breaks it -- the "shapes" of the two groups are different even though the sizes match.

Tutor: Exactly. Same cardinality, different structure. That's the whole point of isomorphism as a notion of sameness -- it's much finer than just counting elements."""

GROUP_HOMOMORPHISMS_FRESH = """Tutor: Let's build on isomorphisms. Suppose we drop the requirement that the map be bijective -- just keep the structure-preserving part. That's a homomorphism.

Student: So it's a function phi from one group to another where phi(ab) = phi(a)phi(b)?

Tutor: Exactly. No injectivity, no surjectivity required. Just: applying the operation before or after mapping gives the same answer.

Student: Can you give me one that isn't injective?

Tutor: Take phi from the integers under addition to itself... actually, better: phi from the integers under addition, mapping n to n mod 2, landing in the two-element group. phi(3) = 1, phi(2) = 0. Multiple integers map to the same output.

Student: Right, that's clearly not injective. What's special about the elements that map to the identity?

Tutor: That set has a name -- the kernel. Formally, the kernel of phi is the set of all g in G such that phi(g) equals the identity of the target group. In my example, the kernel is the even integers.

Student: And the even integers form a subgroup of the integers. Is that a coincidence?

Tutor: Never. The kernel of any homomorphism is always a subgroup of the domain. Want to see why?

Student: Sure. I guess I need identity, closure, and inverses.

Tutor: Start with identity: phi of the identity of G is always the identity of H, since phi(e) = phi(e times e) = phi(e)phi(e), and cancelling gives phi(e) equal to the identity of H. So e is in the kernel.

Student: Okay, and closure -- if a and b are both in the kernel?

Tutor: Then phi(ab) = phi(a)phi(b), and both factors are the identity, so the product is the identity. So ab is in the kernel too.

Student: And inverses -- if phi(a) is the identity, what about phi of a inverse?

Tutor: phi(a)phi(a inverse) = phi(a times a inverse) = phi(e), which is the identity. Since phi(a) is the identity, that forces phi(a inverse) to be the identity as well. So a inverse is in the kernel. All three conditions hold -- it's a subgroup.

Student: Got it. Now, is there a connection between the kernel and whether phi is injective?

Tutor: A very clean one. phi is injective if and only if the kernel is trivial -- just the identity element.

Student: Why would that be true?

Tutor: One direction is easy: if phi is injective, only one element can map to the identity, and we already know the identity of G does, so the kernel can only contain that one element. For the other direction, suppose the kernel is trivial, and suppose phi(a) equals phi(b). Then phi(a) times phi(b) inverse is the identity, and since phi is a homomorphism, phi(a)phi(b inverse) = phi(a times b inverse). So phi(a times b inverse) is the identity, meaning a times b inverse is in the kernel. But the kernel is trivial, so a times b inverse is the identity, which gives a = b.

Student: So a whole subgroup collapsing to a single point is exactly what forces the map to separate everything else.

Tutor: Nicely put. The kernel measures the failure of injectivity -- the bigger it is, the more collapsing happens."""


def test_cosets_fresh_hits_decisive_margin_coverage_gap_veto():
    """This is the one test in this round that directly exercises the
    branch teach-ceg changed. judson:6.2-lagranges-theorem leads raw overlap
    decisively (score 12, margin 7 over the runner-up -- comfortably above
    `_MIN_MARGIN`), which is exactly the shape of case that used to bypass
    coverage checking outright (pre-teach-9wx) and, before teach-ceg, would
    have needed a 25-point coverage gap to veto. Measured here: 20-point gap
    (Lagrange's own coverage 80%, judson:6.1-cosets -- the correct answer --
    covers 100% of its own vocabulary), which clears the new 0.18 threshold
    by 2 points and correctly, safely abstains. Under the pre-teach-ceg 0.25
    threshold this 20-point gap would NOT have cleared the veto, and this
    fresh, independently-authored dialogue would have been a confident wrong
    answer (Lagrange's theorem instead of cosets) -- the same failure shape
    as the bead's own named SETS_EQUIVALENCE bug, on a different rival pair.
    """
    raw = score_candidates(COSETS_FRESH, INDEX)
    text_words = _words(COSETS_FRESH)
    taught_node_id, abstain_reason = _resolve_candidates(raw, INDEX, text_words)

    assert taught_node_id is None
    assert "judson:6.2-lagranges-theorem" in abstain_reason
    assert "judson:6.1-cosets" in abstain_reason

    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:6.2-lagranges-theorem"] == 12
    assert scores["judson:6.1-cosets"] == 5

    lagrange_match = next(c for c in raw if c.node_id == "judson:6.2-lagranges-theorem")
    cosets_match = next(c for c in raw if c.node_id == "judson:6.1-cosets")
    lagrange_coverage = _coverage_fraction(lagrange_match, INDEX, text_words)
    cosets_coverage = _coverage_fraction(cosets_match, INDEX, text_words)
    assert round(lagrange_coverage, 2) == 0.80
    assert round(cosets_coverage, 2) == 1.00
    gap = cosets_coverage - lagrange_coverage
    assert 0.18 <= gap < 0.25, (
        f"expected this fresh case to land between the new (0.18) and old "
        f"(0.25) thresholds -- that is what makes it a real test of "
        f"teach-ceg's fix rather than a case either threshold would have "
        f"handled identically; got gap={gap:.3f}"
    )

    # Full pipeline: confirms the raw-tier abstention above is not overturned
    # by the semantic fallback tier (a different bug class -- see teach-jkx).
    result = recover_from_lesson_text(COSETS_FRESH, GRAPH)
    assert result.taught_node_id is None
    assert result.taught_node_id != "judson:6.2-lagranges-theorem"


def test_isomorphisms_fresh_safely_abstains_no_confident_wrong_answer():
    """Not a decisive-margin case (top score 7 vs runner-up 6, margin 1 <=
    `_MIN_MARGIN`) -- abstains via the separate "too close to call" branch,
    unrelated to the constant this bead changed. Recorded because
    isomorphisms/homomorphisms are this lineage's historically most fragile
    topics (teach-9wx's original bug was HOMOMORPHISMS), so a null result
    here (no new confident-wrong-answer surfacing) is worth having on
    record, not because it validates `_DECISIVE_MARGIN_COVERAGE_GAP`
    specifically."""
    result = recover_from_lesson_text(ISOMORPHISMS_FRESH, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None

    raw = score_candidates(ISOMORPHISMS_FRESH, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:16.3-ring-homomorphisms-and-ideals"] == 7
    assert scores["judson:16.1-rings"] == 6
    # judson:9.1-definition-and-examples (the actual correct answer) clears
    # _MIN_MATCH_WORDS (score 4) but is not competitive -- tied for 4th-7th
    # place, 3 points behind the raw-score leader. An honest recall gap, not
    # this bead's failure mode (a confident wrong answer), and out of this
    # bead's scope to fix.
    assert scores["judson:9.1-definition-and-examples"] == 4
    assert scores["judson:9.1-definition-and-examples"] < scores["judson:16.3-ring-homomorphisms-and-ideals"]


def test_group_homomorphisms_fresh_safely_abstains_no_confident_wrong_answer():
    """Same shape as the isomorphisms case above: top score 7 vs runner-up
    6, margin 1 <= `_MIN_MARGIN`, abstains via the "too close to call"
    branch, not the decisive-margin branch this bead changed. Recorded for
    the same reason -- group homomorphisms is the exact topic of teach-9wx's
    original bug, so a null result on a fresh dialogue is worth having on
    record."""
    result = recover_from_lesson_text(GROUP_HOMOMORPHISMS_FRESH, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None

    raw = score_candidates(GROUP_HOMOMORPHISMS_FRESH, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:16.3-ring-homomorphisms-and-ideals"] == 7
    assert scores["judson:18.2-factorization-in-integral-domains"] == 6
    # judson:11.1-group-homomorphisms (the actual correct answer) clears
    # _MIN_MATCH_WORDS (score 5, after teach-zgn added "injective" and
    # "image" to that node's vocabulary) but is not competitive -- still
    # well behind the raw-score leader. An honest recall gap, not this
    # bead's failure mode (a confident wrong answer), and out of this
    # bead's scope to fix.
    assert scores["judson:11.1-group-homomorphisms"] == 5
    assert scores["judson:11.1-group-homomorphisms"] < scores["judson:16.3-ring-homomorphisms-and-ideals"]
