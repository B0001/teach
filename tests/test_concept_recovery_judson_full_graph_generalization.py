"""teach-ngy: held-out generalization round for concept_recovery.py against
`teach.judson_algebra_graph.load_judson_full_graph` (the 20-node group+ring+
field graph, teach-b5k.1), run by the same session that wrote teach-ngy's fix
-- so, per this repo's standing "you cannot hold out examples from yourself"
rule, this round is NOT self-authored tuning data: none of the six lesson
texts below were written by the fixing session. Each was produced by a
separate `Agent` tool call given an explicit no-tool-use, no-repository-access
instruction and told nothing about concept_recovery.py, its scoring
mechanism, thresholds, teach-ngy, or teach-i35/teach-cpg's prior fixes --
only plain-English definition text sourced directly from
teach/data/judson_ring_field.json (for the three ring/field cases) or general
group-theory knowledge (for the two group-theory cases), with an instruction
to render it as a natural tutor/student dialogue. None of the six agents saw
another's output, this module's code, or any prior round's fixtures.

WHAT teach-ngy's FIX ACTUALLY CHANGED

The bead's own reproduction (`judson:6.2-lagranges-theorem` losing to
`judson:18.2-factorization-in-integral-domains` on the Bond/Lagrange lesson)
was traced to a positional-assumption bug in `_resolve_candidates`'s
multi-candidate-tie branch (the `len(close) > 1` path, reached when raw-score
margin doesn't clear `_MIN_MARGIN`): it only ever tested the raw-score
LEADER for decisive coverage dominance over the tied group, the same class of
bug teach-i35 had already fixed one branch up (the single-close-candidate
case) but left unfixed here. The fix broadens the search to every tied
candidate clearing `_MIN_MATCH_WORDS`, taking whichever is best-covered
regardless of raw-score rank -- exactly mirroring teach-i35's fix, one branch
over. This is verified directly and in isolation by
`test_concept_recovery.py::test_multi_candidate_tie_coverage_winner_need_not_be_the_raw_score_leader`,
and confirmed (diagnostically, NOT as validation -- the bead explicitly
forbids using the Bond/Lagrange lesson to validate this fix, since it is now
tuning data) to make the epic's own Bond/Lagrange lesson recover correctly
against the full 20-node graph.

HONEST RESULT (measured once against the real, unmodified
`load_judson_full_graph()`, via the public `recover_from_lesson_text` entry
point only -- no internals of concept_recovery.py were read to choose or
adjust these lesson texts, and no threshold in concept_recovery.py was
changed in response to seeing these results):

  correct recoveries:      4 / 6  (RINGS -> 16.1, FACTORIZATION -> 18.2,
                                    LAGRANGE -> 6.2, BICYCLE_CONTROL -> None)
  safe abstentions:        1 / 6  (SPLITTING_FIELDS, expected 21.2, got None)
  CONFIDENT WRONG ANSWERS: 1 / 6  (HOMOMORPHISMS, expected 11.1-group-
                                    homomorphisms, got 16.3-ring-
                                    homomorphisms-and-ideals)

THIS ROUND DOES NOT SHOW teach-ngy's FIX FULLY RESOLVES THE BEAD'S NAMED
PROBLEM ("concept_recovery discrimination degrades as the graph grows").
It shows the specific mechanism the fix targets is real, non-regressing, and
does help (LAGRANGE and RINGS both recover correctly against the full
graph -- RINGS in particular is a raw three-way-plus tie at the top that the
fixed multi-candidate branch resolves cleanly). But HOMOMORPHISMS is a
genuine, confident wrong answer, and it is NOT reached through the branch
this bead fixed.

Diagnosed directly (not tuned against): HOMOMORPHISMS scores
`judson:16.3-ring-homomorphisms-and-ideals`=17,
`judson:16.1-rings`=10, `judson:11.1-group-homomorphisms`=7 (the correct
answer, in third place). The raw margin between the leader and the runner-up
is 7, which is decisively larger than `_MIN_MARGIN` (2) -- so this resolves
in `_resolve_candidates`'s SINGLE-close-candidate branch (`len(close) == 1`)
under the `margin > min_margin` condition, which by design returns the
raw-score leader with NO coverage check of any kind. That short-circuit is
deliberate, not an oversight: see concept_recovery.py's own comment at the
top of that branch, which cites `judson_algebra_graph.py`'s
`SIGNPOSTED_LESSON` fixture as a real case where a decisively-separated
raw-score win must NOT be second-guessed against a smaller-vocabulary rival's
proportionally-higher coverage, or a genuinely correct decisive win would be
thrown away. Loosening that short-circuit to always coverage-check is exactly
the kind of change that could fix HOMOMORPHISMS while breaking
`test_judson_algebra_graph.py::test_signposted_prerequisites_are_recovered` --
untangling that tension is real, separate design work, not a one-line
addition to teach-ngy's fix, so it is filed as its own bead (teach-ngy's
closing notes) rather than attempted here under this round's own result,
which would be exactly the "tuning against your own held-out measurement"
this repo's methodology exists to prevent.

WHAT THIS MEANS FOR teach-ngy's OWN CLOSURE

teach-ngy's fix is a real, verified improvement to the multi-candidate-tie
coverage mechanism (unit-tested directly in
`test_concept_recovery.py::test_multi_candidate_tie_coverage_winner_need_not_be_the_raw_score_leader`,
and confirmed above to resolve the bead's own named reproduction) with no
measured regression on this fresh round or the full suite. But this fresh
round found a genuine, DIFFERENT confident-wrong-answer case
(HOMOMORPHISMS) in a branch teach-ngy's fix does not touch, so the bead's
named problem -- discrimination degrading as the graph grows -- is not fully
resolved. Per this lineage's standing rule (a mechanism fix being real and
unit-verified is not sufficient to close a bead if a genuine held-out round
shows a confident wrong answer), teach-ngy stays open with this file as its
evidence, and the residual gap is filed as a new, separate bead.

TEACH-9WX (later bead, fixed the residual gap named above): the decisive-
margin short-circuit this file's HOMOMORPHISMS diagnosis identified as
"deliberate, not an oversight" turned out to be too blunt -- it skipped
coverage checking entirely rather than checking it with a wide enough
tolerance. `_resolve_candidates` now applies a coverage-gap check
(`_DECISIVE_MARGIN_COVERAGE_GAP`) even at a decisive margin: a rival that is
only SOMEWHAT better covered still does not veto the winner (this is what
keeps `test_judson_algebra_graph.py::test_signposted_prerequisites_are_recovered`
passing), but a rival covered so much better that the winner looks like
incidental overlap by comparison now does. HOMOMORPHISMS below is
re-checked, not re-measured -- see
`test_homomorphisms_no_longer_a_confident_wrong_answer` -- and teach-9wx's
own required closing validation is a SEPARATE fresh held-out round with no
access to this file, per this repo's "you cannot hold out examples from
yourself" rule.
"""

from teach.concept_recovery import recover_from_lesson_text
from teach.judson_algebra_graph import load_judson_full_graph

GRAPH = load_judson_full_graph()

RINGS = """Tutor: Let's build up what a "ring" actually is. Take a nonempty set R with two operations, addition and multiplication, both closed. First, forget multiplication for a second — under addition alone, R has to be an abelian group: addition's commutative, associative, there's a 0, and every element has a negative.

Student: So a ring is just a group with extra stuff bolted on?

Tutor: Exactly — an abelian group under addition, plus multiplication that's associative and distributes over addition on both sides. That's the whole definition.

Student: What if there's a multiplicative identity, like 1?

Tutor: Then, provided 1 isn't 0 and 1·a = a·1 = a for every a, we call it a ring with unity. If multiplication also commutes — ab = ba always — it's a commutative ring.

Student: Can you divide in a ring?

Tutor: Not generally. If every nonzero element has a multiplicative inverse, and the ring has identity, that's a division ring. Commutative division ring? That's a field — think rationals, reals.

Student: What about integral domains?

Tutor: A commutative ring with identity where ab = 0 forces a = 0 or b = 0. No sneaky zero divisors.

Student: Zero divisor — meaning?

Tutor: A nonzero a in a commutative ring is a zero divisor if some nonzero b gives ab = 0. Like 2 and 3 in integers mod 6: neither is zero, but 2·3 = 6 = 0.

Student: So integral domains are rings without that pathology.

Tutor: Precisely."""

FACTORIZATION = """Tutor: Let's build up to unique factorization. In a commutative ring R, a divides b if b = ac for some c in R. A unit is just an element with a multiplicative inverse — like 1 and -1 in the integers. And if a = ub for a unit u, we call a and b associates — they're really "the same" factorization-wise.

Student: So 5 and -5 are associates in the integers, since -5 = (-1)(5)?

Tutor: Exactly. Now, in an integral domain D, a nonzero nonunit p is irreducible if the only way to write p = ab forces a or b to be a unit — p can't be broken apart nontrivially. But there's a sneakier property: p is prime if whenever p divides a product ab, p must divide a or divide b.

Student: Aren't those the same thing?

Tutor: Not in general! They coincide in nice rings, but the distinction matters. Think of the integers: every number greater than 1 factors into primes uniquely, up to order — that's the Fundamental Theorem of Arithmetic.

Student: And that generalizes?

Tutor: Right. An integral domain is a unique factorization domain, or UFD, if every nonzero nonunit factors into irreducibles, uniquely up to order and up to swapping factors for associates. Stronger still is a principal ideal domain, a PID, where every ideal is generated by one element. And a Euclidean domain is one with a "size" function letting you do division with remainder, just like ordinary long division with integers.

Student: So Euclidean domains, PIDs, UFDs — they're nested notions of "well-behaved" rings?

Tutor: Precisely — each one buys you factorization structure like the integers enjoy."""

SPLITTING_FIELDS = """Tutor: Let's talk about splitting fields. Say you've got a field F, and a nonconstant polynomial p(x) with coefficients in F. Sometimes p(x) doesn't factor into linear pieces over F itself — think of x squared plus one over the rationals. So we go looking for a bigger field where it does.

Student: A field where all the roots actually live?

Tutor: Exactly. An extension field E of F is called a splitting field of p(x) if p(x) factors completely into linear factors over E. That means there are elements alpha_1 through alpha_n in E so that p(x) equals (x minus alpha_1) times (x minus alpha_2) and so on down to (x minus alpha_n).

Student: So E just has to be big enough to hold every root.

Tutor: Right, but there's a second condition people forget: E has to be the smallest such field — the smallest field containing F and all those alpha_i. You can't throw in extra elements you don't need.

Student: So it's exactly big enough, no bigger.

Tutor: That's the phrase to remember. It contains every root of p(x), but nothing more than what's forced by adjoining those roots to F.

Student: And what does it mean for p(x) to "split," on its own?

Tutor: We say p(x) splits in a field E if it factors into a product of linear factors over E — same idea, just without insisting E is the minimal such field. A splitting field is a field where p(x) splits and which is as small as possible.

Student: Got it — split first, then shrink to the smallest field that makes it happen."""

LAGRANGE = """Tutor: Let's talk about cosets. Say H is a subgroup of a group G. If you pick any element g in G, the set gH — meaning all products gh where h ranges over H — is called a left coset of H.

Student: So it's like shifting H by g?

Tutor: Exactly, a translated copy of H. Now here's the key fact: distinct left cosets never overlap. If two cosets share even one element, they're actually the same set. So the left cosets of H chop all of G into disjoint pieces.

Student: Okay, disjoint pieces. But why does that matter?

Tutor: Because every single one of those pieces has exactly the same size — namely |H|. Think about why: the map h maps to gh is a bijection from H to gH, since you can always undo it by multiplying by g inverse. So gH always has exactly as many elements as H, no matter which g you chose.

Student: So G gets sliced into same-size chunks, each chunk the size of H.

Tutor: Right. And if G is finite, that means |G| is literally the number of cosets times |H|. It's just counting: total equals (number of pieces) times (size of each piece).

Student: And since the number of pieces is a whole number...

Tutor: ...that means |H| divides |G| evenly. That's Lagrange's Theorem: for a finite group G and a subgroup H, |H| must divide |G|.

Student: So if I had a group with 10 elements, a subgroup couldn't have, say, 3 elements?

Tutor: Correct — 3 doesn't divide 10, so no subgroup of size 3 can exist there. Only subgroups whose order divides 10 are even possible: 1, 2, 5, or 10.

Student: That's a strong restriction from something that seemed like a small observation about shifted copies of H.

Tutor: That's the beauty of it — the partition argument is simple, but it constrains the whole structure of the group."""

HOMOMORPHISMS = """Tutor: Let's talk about maps between groups that actually respect the group structure. Say phi is a map from G to H. We call it a homomorphism if phi(g1 g2) = phi(g1) phi(g2) for every g1, g2 in G.

Student: So it doesn't matter whether I combine first and then map, or map first and then combine?

Tutor: Exactly — same answer either way. The map is "compatible" with the operation. If it scrambled that relationship, it wouldn't tell us anything useful about the group structure.

Student: Okay. Now what's this "kernel" thing I keep hearing about?

Tutor: The kernel of phi is just the set of elements in G that get sent to the identity of H — everything phi crushes down to "nothing," so to speak.

Student: So it's a subset of G. Is it more than that — like, does it have structure?

Tutor: Good instinct. It's actually a subgroup of G — and not just any subgroup, it's a normal subgroup.

Student: Remind me why normal matters?

Tutor: A normal subgroup is one that's invariant under conjugation — it sits inside G in a way that plays nicely with all of G's elements, not just its own. And here's the theorem: the kernel of any homomorphism is always normal in G. Every single time.

Student: That seems like a strong guarantee for something defined so simply.

Tutor: It is — and it's part of why kernels are so central. Given any homomorphism, you instantly know its kernel isn't just some random subgroup; it's guaranteed to be normal, no extra work required.

Student: So: homomorphism preserves the operation, kernel is what maps to the identity, and that kernel is always normal.

Tutor: You've got it exactly."""

BICYCLE_CONTROL = """Tutor: Let's start simple. When you pedal, your feet turn the front chainring, and the chain carries that motion back to a cog on the rear wheel. Shift gears, and you change which cogs the chain uses.

Student: But why does that make pedaling harder or easier?

Tutor: It's about the size difference between the front chainring and the rear cog the chain is on. Picture a small rear cog versus a big one. Which do you think makes one pedal stroke turn the wheel more times?

Student: I'd guess the small one, since it's got less to turn.

Tutor: Exactly. A small rear cog spins many times for each turn of the pedals, so the wheel covers more ground per stroke, but it takes more muscle to push through. A big rear cog turns less per pedal stroke, so you go slower for the same effort, but each stroke feels lighter.

Student: So a big cog is like an "easy" gear, and a small one is "hard but fast."

Tutor: Right. Now, how does the chain actually jump between those cogs when you shift?

Student: That's the derailleur, isn't it? I've seen the little cage thing near the wheel.

Tutor: Exactly right. When you shift, a cable pulls the derailleur sideways, and it physically nudges the moving chain off one cog and onto the neighboring one. It also has a spring-loaded arm that takes up slack so the chain stays tight no matter which combination you're in.

Student: So going uphill, I'd want a bigger rear cog for easier pedaling, even though I'll be slower?

Tutor: That's it exactly. Trade speed for effort on the climb, then shift back down to a smaller cog once you're back on flat ground and want speed."""


def test_rings_correctly_recovers():
    """CORRECT RECOVERY: RINGS lands squarely on the multi-candidate-tie
    branch teach-ngy fixed -- top raw scores are close (17/9/9/4/4) with
    `judson:16.1-rings` NOT the outright raw-score leader by a decisive
    margin, so this exercises the exact coverage-tiebreak-among-ties
    mechanism the fix broadened. Measured: matches exactly."""
    result = recover_from_lesson_text(RINGS, GRAPH)
    assert result.taught_node_id == "judson:16.1-rings"


def test_factorization_correctly_recovers():
    """CORRECT RECOVERY: decisive raw-score win (24 vs runner-up 8), so this
    resolves in the single-candidate branch without needing any tiebreak."""
    result = recover_from_lesson_text(FACTORIZATION, GRAPH)
    assert result.taught_node_id == "judson:18.2-factorization-in-integral-domains"


def test_splitting_fields_now_correctly_recovers_after_teach_443():
    """CORRECT RECOVERY (was a SAFE ABSTENTION until teach-443): this used to
    tie exactly with judson:21.1-extension-fields at raw score 9, and neither
    cleared the multi-candidate coverage tiebreak's margin requirement, so
    the module declined rather than guess between two genuinely close
    neighbors -- a real, close confusability (a splitting field IS an
    extension field with an extra condition), not a fix failure.

    teach-443 found that judson:18.2-factorization-in-integral-domains'
    verbatim-extracted `definition` text (and several other ring/field
    nodes', including this one's own judson:21.2-splitting-fields) still
    carries raw PreTeXt/LaTeX source -- commands like \\cdots and \\ldots --
    that word-tokenization was silently admitting as if the bare command name
    were an English content word. Stripping those before tokenization
    (`_LATEX_COMMAND` in concept_recovery.py) shrinks the affected nodes'
    vocabularies to their real prose, which breaks this exact tie: judson:21.2
    now covers 88.9% of its own (cleaned) vocabulary against
    judson:21.1's 24.2%, clearing `_MIN_COVERAGE_FRACTION`/
    `_MIN_COVERAGE_MARGIN` decisively. This is a side effect of a correctness
    fix made for an unrelated reason (teach-443's investigation of
    judson:18.2), not a threshold retuned to make this fixture pass."""
    result = recover_from_lesson_text(SPLITTING_FIELDS, GRAPH)
    assert result.taught_node_id == "judson:21.2-splitting-fields"


def test_lagrange_correctly_recovers_against_the_full_graph():
    """CORRECT RECOVERY: this is the bead's own named lesson shape (Judson's
    cosets-to-Lagrange argument, without Bond framing so it is not the exact
    fixture named in teach-ngy's bug report) run against the full 20-node
    graph the bead is about. Measured: matches exactly, unlike the bug
    report's pre-fix reproduction."""
    result = recover_from_lesson_text(LAGRANGE, GRAPH)
    assert result.taught_node_id == "judson:6.2-lagranges-theorem"


def test_homomorphisms_no_longer_a_confident_wrong_answer():
    """teach-9wx fixed the mechanism this test used to pin as broken: the
    DECISIVE-margin path (`margin > min_margin`) of `_resolve_candidates`'s
    single-close-candidate branch used to return the raw-score leader with
    NO coverage check at all. On this text (semantic tier), that leader was
    judson:16.3-ring-homomorphisms-and-ideals (score 17, margin 7 over the
    runner-up -- decisively above `_SEMANTIC_MIN_MARGIN`'s 3) covering only
    17.5% of its own vocabulary, while the true answer,
    judson:11.1-group-homomorphisms (score 7, third place by raw count),
    covered 57.1% of its own -- a 39.6-point coverage gap the old code never
    looked at. teach-9wx added `_DECISIVE_MARGIN_COVERAGE_GAP`: a decisive
    margin is still not second-guessed against a rival that is only somewhat
    better covered (see judson_algebra_graph.py's SIGNPOSTED_LESSON, still
    passing), but a gap this wide is no longer trusted.

    This is a DIAGNOSTIC RE-CHECK, NOT the fix's validation -- this exact
    case is the bug's own named reproduction (teach-ngy's fresh held-out
    round) and this lineage's standing rule is that a case which measured a
    fix cannot also validate it. The fix's actual closing validation is a
    separate, freshly-authored held-out round with no access to this file,
    teach-9wx, or teach-ngy (see the bead's closing notes for that round).
    This test only pins that the mechanism bug demonstrated here is gone --
    the safe direction (abstention), not a claim that judson:11.1 is now
    recovered outright (it is not: the correct answer is still buried under
    two other candidates by raw score, so this abstains rather than guesses,
    per this module's whole design)."""
    result = recover_from_lesson_text(HOMOMORPHISMS, GRAPH)
    assert result.taught_node_id is None, (
        f"expected a safe abstention now that teach-9wx's decisive-margin "
        f"coverage gap check is in place -- got {result.taught_node_id!r} "
        f"instead; if this is 'judson:16.3-ring-homomorphisms-and-ideals' "
        f"the fix regressed"
    )
    assert result.abstain_reason is not None


def test_offdomain_bicycle_control_safely_abstains():
    """SAFE ABSTENTION: pure bicycle-mechanics content, no group/ring/field
    vocabulary at all. Correctly ambiguous/no-signal rather than a
    false-positive match to any Judson node."""
    result = recover_from_lesson_text(BICYCLE_CONTROL, GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
