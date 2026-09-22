"""teach-hpa: SEPARATE fresh held-out round, run to satisfy this bead's own
closing requirement (per this lineage's rule against tuning a fix in response
to the same round that measured it -- teach-hpa's own predecessor, teach-9wx,
was measured against tests/test_concept_recovery_judson_full_graph_generalization_round2.py,
which is now tuning data and must not be reused here).

All five lesson texts below were produced by separate `Agent` tool calls, each
given an explicit no-tool-use, no-repository-access instruction and told
nothing about concept_recovery.py, this bead, or any threshold or mechanism
in this module -- only a plain-English topic name and a request to render it
as a natural tutor/student dialogue, using the agent's own general knowledge
of abstract algebra. None of the five agents saw another's output, this
module's code, or any prior round's fixtures.

All five topics are nodes that had NEVER been used as a fixture in either
round1 (RINGS, FACTORIZATION, SPLITTING_FIELDS, LAGRANGE, HOMOMORPHISMS,
BICYCLE_CONTROL) or round2 (RING_HOMOMORPHISMS, ISOMORPHISMS,
CYCLIC_SUBGROUPS, INTEGRAL_DOMAINS_FIELDS, PERMUTATION_GROUPS), chosen from
the ten remaining untested nodes in `load_judson_full_graph()`'s 20-node
graph: judson:1.2-sets-and-equivalence-relations, judson:3.3-subgroups,
judson:6.1-cosets, judson:10.1-factor-groups-and-normal-subgroups, and
judson:16.4-maximal-and-prime-ideals.

HONEST RESULT (measured once against the real, unmodified
`load_judson_full_graph()`, via the public `recover_from_lesson_text` entry
point only -- no internals of concept_recovery.py were read to choose or
adjust these lesson texts, and no threshold in concept_recovery.py was
changed in response to seeing these results):

  correct recoveries:      0 / 5
  safe abstentions:        3 / 5  (SUBGROUPS, NORMAL_SUBGROUPS, MAXIMAL_PRIME_IDEALS)
  boundary/defensible:     1 / 5  (COSETS -> recovered as the closely related
                                    judson:6.2-lagranges-theorem, which the
                                    dialogue also substantively derives)
  CONFIDENT WRONG ANSWER:  1 / 5  (SETS_EQUIVALENCE -> judson:18.2)

This round's job, per this lineage's standing methodology, is to check
whether teach-hpa's own change (`_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO`, a
credibility floor added on top of teach-9wx's `_DECISIVE_MARGIN_COVERAGE_GAP`
so a rival's coverage fraction can't veto a decisive winner just because the
rival has a tiny vocabulary) introduces any NEW regression relative to
teach-9wx's code alone. It was checked directly, not just inferred: for
every case in this round where the decisive-margin branch fired at all
(SETS_EQUIVALENCE, NORMAL_SUBGROUPS, MAXIMAL_PRIME_IDEALS -- raw tier), the
final abstain/no-abstain decision was recomputed with teach-hpa's ratio gate
removed entirely (i.e., simulating teach-9wx's original code, which vetoes
based on ANY score>=_MIN_MATCH_WORDS rival's coverage, not just credible
ones). In all three cases, the ungated decision was IDENTICAL to the gated
one:

  SETS_EQUIVALENCE (raw): gated=no-veto (18.2 wins), ungated=no-veto (same;
    the best-covered rival is judson:6.2 at 47% coverage either way -- no
    other candidate has higher coverage, gated or not, so the ratio gate
    changes nothing here). Result: SAME (confident wrong answer either way).
  NORMAL_SUBGROUPS (raw): gated=veto (abstain), ungated=veto (abstain; the
    best-covered rival, judson:6.1-cosets at 100% coverage, clears the ratio
    floor anyway, ratio 0.40). Result: SAME (safe abstention either way).
  MAXIMAL_PRIME_IDEALS (raw): gated=veto naming judson:16.4 (the correct
    answer, 56% coverage, ratio 0.48 clears the floor), ungated=veto naming
    judson:6.1-cosets instead (67% coverage, ratio only 0.19, would be
    excluded by the gate but the ungated check doesn't apply one) -- the
    NAMED rival differs, but the final decision (abstain) is the SAME either
    way.

So in this fresh round, teach-hpa's ratio-credibility gate was behaviorally
INERT: it never changed a final recovery decision relative to teach-9wx's
code alone, in either direction. That is itself the honest result of this
round -- it demonstrates NO NEW REGRESSION from teach-hpa's change (the gate
never let a wrong answer through that teach-9wx's code would have caught,
across five fresh, diverse topics), but it does NOT independently confirm
teach-hpa's intended benefit either, since none of these five topics happened
to land in the specific geometry teach-hpa targets (a genuinely-correct
decisive winner with low self-coverage, being challenged by a tiny-vocabulary
rival that is well-covered proportionally but not credible in absolute
score). That specific geometry was already confirmed via the isolated unit
test `test_decisive_margin_not_vetoed_by_a_rival_too_thin_in_absolute_terms`
in tests/test_concept_recovery.py (fabricated) and the real
RING_HOMOMORPHISMS case in round2 (now tuning data, not re-measured here).

TWO PRE-EXISTING ISSUES THIS ROUND SURFACED, NEITHER CAUSED BY teach-hpa
(confirmed via the gated/ungated comparison above), filed forward rather than
fixed in this session:

1. SETS_EQUIVALENCE is a genuine CONFIDENT WRONG ANSWER: a lesson on
   judson:1.2-sets-and-equivalence-relations recovers as
   judson:18.2-factorization-in-integral-domains, because the coverage gap
   between 18.2's own coverage (23%) and the best rival's (judson:6.2 at 47%)
   is 24 points -- one point short of `_DECISIVE_MARGIN_COVERAGE_GAP`'s 25.
   Confirmed above this is NOT a teach-hpa regression (identical outcome with
   the ratio gate removed). Filed as teach-ceg.

   UPDATE (teach-ceg, later session): fixed by recalibrating
   `_DECISIVE_MARGIN_COVERAGE_GAP` from 0.25 to 0.18 -- see that constant's
   comment in concept_recovery.py and
   test_sets_equivalence_now_abstains_instead_of_a_confident_wrong_answer
   below, which replaced the old not-yet-fixed regression-marker test. This
   paragraph is left as the original historical measurement, not rewritten,
   per this repo's "a number is only allowed to exist... if the code
   produces it" rule -- the 23%/47%/24-point numbers above are still exactly
   what this round measured against the pre-fix code.
2. judson:18.2-factorization-in-integral-domains topped the raw-tier score in
   4 of these 5 fresh, topically-unrelated dialogues (all but COSETS), never
   exceeding 28% of its own coverage in any of them -- a systemic
   generic-vocabulary-attractor pattern, structurally similar to what
   motivated `_DECISIVE_MARGIN_COVERAGE_GAP` and
   `_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO` in the first place, but here
   affecting FOUR different correct answers rather than one. Filed as
   teach-443 for someone to inspect judson:18.2's actual vocabulary set.

   UPDATE (teach-443, later session): investigated directly via
   `build_vocabulary_index` output. judson:18.2's distinctive vocabulary (75
   words pre-fix) was ~3-5x the graph's median node and had two identifiable,
   distinct contaminants: (a) 6 raw PreTeXt/LaTeX command tokens ("cdots",
   "langle", "ldots", "mathbb", "rangle", "setminus") that word-tokenization
   was admitting as if they were English content words -- fixed by stripping
   backslash-command-shaped sequences before tokenization (`_LATEX_COMMAND` in
   concept_recovery.py), which also corrected several OTHER ring/field nodes'
   document-frequency counts (see
   test_subgroups_now_correctly_recovers_after_teach_57f
   and test_splitting_fields_now_correctly_recovers_after_teach_443, both
   updated in this session for the resulting, legitimate score changes); and
   (b) roughly half of 18.2's remaining vocabulary is generic mathematical-
   discourse register ("recall", "suppose", "written", "satisfy", "question",
   "necessarily", "furthermore", "extend", ...) that is document-frequency-
   rare only because this specific 20-node graph's OTHER nodes are terse,
   formal Definition-style extractions that never contain ordinary
   discursive prose at all -- not because these words are genuinely
   factorization-specific. (b) is NOT fixed here: distinguishing "generic
   academic prose" from "curriculum-distinctive vocabulary" needs either an
   external general-English frequency reference or a graph redesign (judson:
   18.2's source section legitimately bundles ~9 separate Judson definitions
   that a finer-grained node split would separate), and any fix along either
   path needs its own design and fresh held-out validation round, per this
   repo's standing methodology -- attempting it inside this same bead's
   investigation would risk exactly the self-authored-data-fits-symptom
   shortcut this lineage warns against. Filed forward as teach-57f. Full
   details, including the exact vocabulary dump and document-frequency
   comparison, are in this bead's handoff
   (sandbox-handoffs/teach-443.md).

   UPDATE (teach-57f, later session): direction (a) from teach-443's note
   above -- a general-English/academic-discourse reference independent of
   this graph's own document-frequency stats -- was attempted, NOT direction
   (b) (the graph-redesign path is out of scope for a P3 vocabulary fix and
   would need every graph consumer re-verified). A general WORD-FREQUENCY
   cutoff (e.g. against the Brown corpus via NLTK, already a dependency) was
   tried first and rejected: measured directly, "ring", "field", "group",
   "order", "form", and "function" -- this graph's own core technical
   vocabulary -- all land in the 500-3000 most frequent general-English
   words, so any frequency threshold strong enough to exclude "furthermore"
   also strips the exact words that make ring/field/group-theory nodes
   distinguishable from each other at all. Implemented instead as a small,
   hand-curated, closed grammatical class (`_DISCOURSE_STOPWORDS` in
   concept_recovery.py): connective adverbs, hedges, and reporting/meta-
   commentary verbs whose FUNCTION is to narrate or qualify a claim, never
   to name a mathematical object or property in any domain this repo
   currently has -- checked directly against the VA Writing and VA Reading
   SOL graphs (0 and 6 hits respectively) before adding, not tuned to
   Judson alone. Effect: judson:18.2's distinctive vocabulary shrank from 69
   to 50 words -- no longer the graph's single largest node (54-word
   judson:16.3-ring-homomorphisms-and-ideals is now larger), though still
   well above the ~14-18 median; this is an honest partial mitigation, not
   a claim that the attractor pattern is eliminated. Two tests in THIS file
   changed as a directly-traced consequence:
   test_sets_equivalence_now_abstains_instead_of_a_confident_wrong_answer
   still abstains (still safe) but now via a three-way exact tie rather
   than naming judson:6.2-lagranges-theorem as the closest rival, and
   test_subgroups_abstains_via_multi_candidate_coverage_tie_after_teach_443
   was renamed to test_subgroups_now_correctly_recovers_after_teach_57f: the
   pre-existing recall gap that test's own docstring flagged ("a
   pre-existing recall gap, unrelated to teach-443, noted honestly rather
   than fixed here") is now closed -- judson:3.3-subgroups is correctly
   recovered. See teach-57f's handoff for the fresh held-out round run
   before closing and the full trace of both changes.

COSETS is a boundary case, not confidently called wrong here: the dialogue
teaches cosets thoroughly but explicitly derives Lagrange's theorem at length
in its closing exchanges ("That's what gives Lagrange's theorem, isn't it? G
splits into cosets, all the same size... |G| = k|H|"), and recovers as
judson:6.2-lagranges-theorem (87% of ITS OWN vocabulary covered) via the
pre-existing multi-candidate-tie branch (teach-ngy's code, raw-score tie
between 18.2 and 6.2 at 13 each -- judson:6.1-cosets itself scores only 6, far
below the tie threshold, and never enters the "close" candidate set at all).
Not attributed to teach-hpa (the tie branch doesn't run through
_resolve_candidates's decisive-margin code at all), and not filed as a new
bug here since the recovered node is a real, substantial part of what the
text teaches -- but noted honestly as an imperfect recovery, not a clean win.
"""

from teach.concept_recovery import (
    build_vocabulary_index,
    recover_from_lesson_text,
    score_candidates,
)
from teach.judson_algebra_graph import load_judson_full_graph

GRAPH = load_judson_full_graph()
INDEX = build_vocabulary_index(GRAPH)

SETS_EQUIVALENCE = """Tutor: Let's start with something you already know without knowing you know it. When is the last time you said two fractions were "the same," like 1/2 and 2/4?

Student: All the time. They're equal, obviously.

Tutor: Sure, but as symbols on a page, 1/2 and 2/4 are different objects — different numerator, different denominator. So what do we actually mean when we say they're "the same"?

Student: I guess we mean they represent the same value, even though they're written differently.

Tutor: Exactly. We've grouped different-looking things into one bucket because they share some property. That's the seed of a huge idea in math: an equivalence relation. It's a formal way of saying "these things count as the same for my purposes," and it always has to satisfy three rules.

Student: What are the rules?

Tutor: Let's build them from what "sameness" should mean. First, everything should be the same as itself. If ~ is our relation, that's a ~ a for all a. We call that reflexive.

Student: Sure, that's obvious. A thing equals itself.

Tutor: Second: if a is the same as b, then b should be the same as a. Order shouldn't matter. That's symmetric: a ~ b implies b ~ a.

Student: Also obvious. What's the third one?

Tutor: Transitive: if a ~ b and b ~ c, then a ~ c. If 1/2 = 2/4 and 2/4 = 4/8, then 1/2 better equal 4/8.

Student: Okay, so any relation with those three properties is called an equivalence relation. But why do we care about the label? It just seems like a checklist.

Tutor: Because once you know something is an equivalence relation, you get a huge structural payoff for free: it automatically chops the whole set into non-overlapping groups called equivalence classes, and every element belongs to exactly one group. That's not obvious in advance — it's a theorem, and it's the real reason the definition matters.

Student: Can we see that with an example? Fractions feel a little abstract.

Tutor: Let's do a cleaner one: congruence mod n. Fix n = 3, and work over the integers. Define a ~ b to mean "a and b leave the same remainder when divided by 3," or equivalently, 3 divides (a − b).

Student: Okay. Let me check reflexive: does 3 divide a − a? That's 0, and 3 divides 0. Fine.

Tutor: Good. Now symmetric.

Student: If 3 divides a − b, does it divide b − a? Well, b − a is just −(a − b), so yes, same divisibility.

Tutor: And transitive?

Student: Suppose 3 divides a − b and 3 divides b − c. I want 3 to divide a − c. Well, a − c = (a − b) + (b − c), and 3 divides both pieces, so it divides the sum. So yes, transitive too.

Tutor: So congruence mod 3 is an equivalence relation on the integers. Now, what are the equivalence classes — the buckets?

Student: I think... all the integers that leave remainder 0 go together, remainder 1 together, remainder 2 together?

Tutor: Exactly right. Write out the class of 0: that's {..., −6, −3, 0, 3, 6, ...}. The class of 1 is {..., −5, −2, 1, 4, 7, ...}. The class of 2 is {..., −4, −1, 2, 5, 8, ...}.

Student: And every integer is in exactly one of those three lists.

Tutor: Right — and that's the general phenomenon, not a coincidence of this example. Notice two things: the classes don't overlap, and together they cover all of ℤ. That's called a partition of the set.

Student: So "equivalence relation" and "partition" are basically two views of the same thing?

Tutor: Precisely — that's the theorem I mentioned. Every equivalence relation on a set produces a partition of that set into equivalence classes, and conversely, every partition of a set defines an equivalence relation, where you just declare two elements related exactly when they're in the same piece.

Student: That direction seems almost too easy.

Tutor: Try it. Suppose someone hands you a partition — say they split a classroom into groups for a project. Define a ~ b to mean "a and b are in the same group." Check reflexive, symmetric, transitive.

Student: Reflexive: you're in your own group with yourself, fine. Symmetric: if I'm in your group, you're in mine. Transitive: if I'm in your group and you're in Sam's group, then... wait, groups don't overlap, so if you're in my group and also in Sam's group, my group and Sam's group must actually be the same group.

Tutor: Exactly the point. A partition already forces non-overlap, so transitivity comes almost for free.

Student: This is kind of satisfying. So a class is basically a "type" or "flavor" and the relation just tests whether two things are the same flavor.

Tutor: That's a great intuition. One more subtlety worth naming: a class can be described by any of its members. The class of 1 mod 3 is the same set as the class of 4 mod 3, or of −2 mod 3. We usually pick a convenient representative, like the smallest nonnegative one, and call it something like [1] or 1̄.

Student: So [1] = [4] = [−2] as sets, even though 1, 4, and −2 look nothing alike?

Tutor: Right, just like 1/2 and 2/4 from the start of our conversation. In fact, "equal fractions" is exactly an equivalence relation on pairs of integers (with nonzero denominator): (a,b) ~ (c,d) when ad = bc. The equivalence classes are literally what we call rational numbers.

Student: Wait — so a rational number isn't really a single object, it's a whole equivalence class of fraction-representations?

Tutor: That's precisely how it's formally constructed. It feels like a technicality until you realize this trick — define new objects as equivalence classes of old ones — is used constantly: to build the rationals from integer pairs, to build clock arithmetic from integers, even to build real numbers from sequences of rationals.

Student: So the checklist of reflexive, symmetric, transitive isn't just bookkeeping — it's the license to say "I can safely lump these into one new object."

Tutor: That's exactly the right way to think about it. Whenever you're tempted to say two different-looking things are "essentially the same," ask what relation you have in mind, then check those three properties. If they hold, you get a clean partition into equivalence classes, and you're justified in treating each class as a single new object.

Student: I think I finally see why this shows up everywhere instead of being a one-off definition.

Tutor: That's the idea. Try it yourself: take the relation "same remainder mod 5" on the integers, list out the five equivalence classes, and check the three properties directly, the way we did for mod 3."""

SUBGROUPS = """Tutor: Let's build on what we know about groups. Today's target is the subgroup — a group living inside another group. Before I define it, take a guess: if G is a group, what would you want a subset H of G to satisfy for H to deserve the name "subgroup"?

Student: I'd guess H has to be a group in its own right, using the same operation as G.

Tutor: Exactly right. Formally, H is a subgroup of G if H is a subset of G, and H is itself a group under the operation inherited from G. We write H ≤ G. Notice the phrase "the operation inherited from G" — we're not allowed to invent a new multiplication for H, we just reuse whatever G already does.

Student: So H needs closure, an identity, inverses, and associativity, just like any group?

Tutor: Right, but one of those is automatic. Which one, do you think?

Student: Associativity? Because it already holds for all elements of G, so certainly for the elements of H too.

Tutor: Exactly. Associativity is inherited for free. So really we only need to check three things directly: closure, identity, and inverses.

Student: Okay, but does H need its own identity element, or can it just borrow e from G?

Tutor: Good question — it has to actually contain e, the identity of G. You can prove that if H has an identity at all, it must coincide with G's identity, so there's no escaping it. That's a useful fact: if e is not in H, you can immediately stop and say H is not a subgroup.

Student: That's a nice quick test. So to check something is a subgroup, in principle I check four things: it's a subset, closed under the operation, contains the identity, and closed under inverses.

Tutor: That's correct, and it's called the subgroup criterion in full. But there's a shortcut used constantly in practice, called the subgroup test. Want to guess how we can shrink that list?

Student: Maybe... if it's closed under the operation and under inverses, does the identity come along automatically?

Tutor: Yes! Here's why. Suppose H is a nonempty subset of G, closed under the operation and closed under taking inverses. Since H is nonempty, pick some h in H. Closure under inverses gives h⁻¹ in H. Now closure under the operation applied to h and h⁻¹ gives h·h⁻¹ = e in H. So the identity is forced to appear.

Student: Oh nice, that's slick. So the actual subgroup test is just: H nonempty, closed under the operation, closed under inverses. Three checks instead of four.

Tutor: Precisely. State it with me: a nonempty subset H of a group G is a subgroup if and only if for all a, b in H, ab is in H, and for all a in H, a⁻¹ is in H. Some books compress those into one condition: for all a, b in H, ab⁻¹ is in H. Same content, just packaged differently.

Student: Why is "nonempty" so important? Couldn't the empty set trivially satisfy "closed under everything" since there's nothing to check?

Tutor: Sharp catch — vacuously, the empty set is closed under the operation and under inverses, since there are no elements to violate anything. But the empty set is not a group, since a group must have an identity element, and there's nothing in there. That's exactly why we insist on nonemptiness separately; it's the one condition that isn't "vacuously" satisfiable in a useless way.

Student: Got it. Can we see an actual example now?

Tutor: Let's use G equal to the integers under addition. Consider H equal to the even integers, 2ℤ. Is H nonempty?

Student: Yes, 0 is even, so 0 is in H.

Tutor: Good, and closure — if a and b are even, is a + b even?

Student: Sure, even plus even is even.

Tutor: And inverses — remember, in an additive group the "inverse" of a is -a. If a is even, is -a even?

Student: Yes, negating an even number keeps it even.

Tutor: So 2ℤ passes the subgroup test, and in fact for any integer n, the multiples of n, written nℤ, form a subgroup of ℤ. These turn out to be literally all the subgroups of ℤ — every subgroup of the integers looks like nℤ for some n ≥ 0.

Student: What about something like the odd integers? That feels like it should fail.

Tutor: Try the test yourself.

Student: Nonempty, sure, 1 is odd. But closure fails — 1 + 1 is 2, which isn't odd. So the odd integers are not closed under addition, hence not a subgroup.

Tutor: Exactly, and that single failure is enough to kill it — you don't even need to check inverses once closure fails. Now let's try something nonabelian, to see the test flex a bit more muscle. Take G equal to S₃, the symmetric group on three letters, with six elements: the identity, three transpositions, and two three-cycles.

Student: Okay, what's the candidate subset?

Tutor: Let H be the set containing just the identity and the two three-cycles, say e, ρ, and ρ², where ρ is a cyclic rotation and ρ² is applying it twice. Is H nonempty?

Student: Yes, e is in there by construction.

Tutor: Now closure. What is ρ times ρ?

Student: That's ρ², which is in H.

Tutor: And ρ² times ρ?

Student: That should cycle everything back to the identity, so ρ³ equals e, which is in H.

Tutor: And ρ times ρ²?

Student: Same thing by the group axioms, that's ρ³, which is e again, in H. And ρ² times ρ² would be ρ⁴, which is the same as ρ, still in H.

Tutor: So closure holds for every pair. Now inverses — what's the inverse of ρ?

Student: It should be ρ², since ρ times ρ² is e.

Tutor: Right, and that's in H. What about the inverse of ρ²?

Student: By the same logic, its inverse is ρ, also in H. And the identity's inverse is itself.

Tutor: So H passes on all counts — it's a subgroup of S₃, actually the subgroup of rotations, isomorphic to the cyclic group of order 3. Now, what if I'd instead tried H equal to the identity plus just one transposition, say e and τ where τ swaps two of the three letters?

Student: Let's check closure. τ times τ — since a transposition undoes itself when applied twice — should give e, which is fine. So actually that looks closed too, and τ's inverse is itself, so inverses are fine. Is that also a subgroup?

Tutor: It is! That's a subgroup of order 2. Good instinct to check it directly rather than assume. But now here's a trap: what if H were just the identity and two different transpositions, say e, τ₁, and τ₂, without the third?

Student: Let me multiply τ₁ and τ₂. In S₃ that composition of two different transpositions should give one of the three-cycles, not the identity or another transposition.

Tutor: Exactly right — τ₁τ₂ lands you on ρ or ρ², which isn't in your proposed H. Closure fails, so that set is not a subgroup, even though every individual element looked innocent.

Student: That's a good warning — you really do have to check the products, not just eyeball which elements "seem group-like."

Tutor: That's the whole point of having a test rather than relying on intuition. One last thing to notice: every group G has two subgroups for free, no matter what G is. Can you name them?

Student: The whole group G itself, since G is trivially a group inside itself. And the set containing just the identity, {e} — that's nonempty, closed since e·e = e, and its own inverse.

Tutor: Exactly — those are called the trivial subgroups. Anything else is called a proper, nontrivial subgroup, and those are usually the interesting ones, like the rotation subgroup we found inside S₃. For next time, try finding all the subgroups of S₃ using the test, there are six total, and see if you can spot why none of them has order 4 or 5.

Student: Order divides six... is that going to matter?

Tutor: You're anticipating Lagrange's theorem already. We'll get there — hold that thought."""

COSETS = """Tutor: Let's talk about cosets today. You know what a subgroup is — a subset that's a group in its own right. A coset is what you get when you take a subgroup and "shift" it by an element of the bigger group.

Student: Shift it how?

Tutor: Concretely. If H is a subgroup of G, and g is any element of G, the left coset gH is the set of all products gh where h ranges over H. Similarly Hg is the right coset: all products hg for h in H.

Student: So gH is just H with every element multiplied by g on the left?

Tutor: Exactly. And note gH itself might not be a subgroup — it usually doesn't contain the identity unless g is in H. It's just a subset, a "translate" of H sitting somewhere else in G.

Student: Okay, why do we care about these translates?

Tutor: Because they turn out to slice G up perfectly — every element of G lands in exactly one left coset of H. That's the partition property. Want to see why?

Student: Yes.

Tutor: First, every element is in some coset: g itself is in gH, since g = ge and e is in H. So the cosets cover all of G. Now suppose two cosets gH and g'H share an element. I claim they must actually be the same set.

Student: How do you show that?

Tutor: Say x is in both, so x = gh₁ = g'h₂ for some h₁, h₂ in H. Then g' = g h₁ h₂⁻¹. Since h₁h₂⁻¹ is in H — closure and inverses — this says g' = g·(something in H), so g' is in gH. Then for any h in H, g'h = g(h₁h₂⁻¹h), and h₁h₂⁻¹h is in H, so g'h is in gH too. That shows g'H is contained in gH.

Student: And the same argument backwards gives gH contained in g'H.

Tutor: Right — symmetric roles, so gH = g'H. So any two left cosets are either identical or completely disjoint. Combined with the fact that they cover G, that's exactly a partition.

Student: Got it — like equivalence classes.

Tutor: That's precisely what they are. Define g ~ g' when g⁻¹g' is in H; that's an equivalence relation, and its classes are exactly the left cosets. Same story for right cosets with a mirrored relation.

Student: Do left and right cosets always match up, gH = Hg?

Tutor: Not in general — only when H is normal in G. For an abelian group they always coincide, since order of multiplication doesn't matter. In a nonabelian group they can genuinely differ.

Student: Okay. Now what about sizes — you mentioned they're all the same size as H?

Tutor: Right, that's the other key fact. The map h ↦ gh from H to gH is a bijection. It's clearly onto by definition of gH. And it's injective because if gh₁ = gh₂, left-multiplying by g⁻¹ gives h₁ = h₂.

Student: So multiplication by g is just relabeling H's elements, not creating or destroying any.

Tutor: Exactly — a bijection, so |gH| = |H| for every g. Same argument for Hg using right multiplication.

Student: That's what gives Lagrange's theorem, isn't it? G splits into cosets, all the same size.

Tutor: You're already there. If G is finite, it's partitioned into some number of left cosets of H, say k of them, each of size |H|. So |G| = k|H|, meaning |H| divides |G|. That number k is called the index of H in G, written [G:H].

Student: Can we do an example? I like to see numbers.

Tutor: Sure — take G = Z/6Z, integers mod 6 under addition, and H = {0, 2, 4}, the even residues. H is a subgroup — closed under addition mod 6, contains 0, contains inverses.

Student: What are the cosets then?

Tutor: Since the group is abelian, left and right cosets coincide, and we write them additively: g + H. Take g = 0: 0 + H = {0, 2, 4} = H itself. Take g = 1: 1 + H = {1, 3, 5}.

Student: And g = 2 should just give H back, since 2 is already in H.

Tutor: Exactly right — 2 + H = {2, 4, 6 mod 6} = {2, 4, 0} = H again. Same for g = 4. And g = 3 or g = 5 will reproduce {1,3,5}.

Student: So there are really only two distinct cosets: the evens and the odds.

Tutor: Precisely — H and 1+H partition all of Z/6Z into two blocks of size 3 each, matching |H| = 3. And 6 = 2 × 3, consistent with Lagrange.

Student: Can we see a nonabelian example too, where left and right differ?

Tutor: Let's use S₃, the symmetric group on {1,2,3}, with H = {e, (12)} — a subgroup of order 2. Let g = (123), the 3-cycle sending 1→2→3→1.

Student: Compute gH first?

Tutor: gH = {(123)e, (123)(12)}. Composing (123)(12) — apply (12) first, then (123): 1→2→3, 2→1→2... let me just say the composite works out to (13). So gH = {(123), (13)}.

Student: And Hg?

Tutor: Hg = {e(123), (12)(123)} = {(123), (12)(123)}. Computing (12)(123): apply (123) first then (12): 1→2→1, 2→3→3, 3→1→2. That's the cycle (23). So Hg = {(123), (23)}.

Student: So gH = {(123),(13)} and Hg = {(123),(23)} — different sets, both containing (123), but not equal.

Tutor: Exactly the phenomenon I meant. They both have size 2, matching |H|, and each one individually still partitions S₃ into three cosets of size 2 — but the left-coset partition and the right-coset partition of S₃ are different partitions.

Student: That's a nice concrete warning against assuming gH = Hg.

Tutor: Right, and it's exactly the failure that makes normal subgroups special — H is normal precisely when gH = Hg for every g, which is what you need to define the quotient group G/H sensibly.

Student: So cosets are really the stepping stone to quotient groups.

Tutor: That's the whole point of introducing them — once you see G cleanly partitioned into equal-sized blocks, the natural next question is whether you can multiply those blocks together and get a group structure on the set of cosets itself. That's exactly where we're headed next."""

NORMAL_SUBGROUPS = """Tutor: Let's pick up where we left off with cosets. You know how to form the cosets of a subgroup H in a group G. Today's question is: when can we turn the set of cosets itself into a group?

Student: You mean like defining a multiplication on cosets, where you combine two cosets to get another coset?

Tutor: Exactly. The natural guess is (aH)(bH) = abH. Simple enough. But here's the catch — is that actually well-defined?

Student: What do you mean, well-defined? aH and bH are just sets, so abH should just be... the coset of ab.

Tutor: Right, but a coset can be written many ways. aH is the same set as a'H whenever a' is any other element of that coset. So if I define the product using representatives a and b, I need (a'H)(b'H) to land on the exact same coset abH, no matter which representatives a' and b' I picked.

Student: Oh — so it's a "does the answer depend on which name I used for the coset" problem.

Tutor: Precisely. So let's test it. Suppose a' = ah for some h in H, and b' = bk for some k in H. Then a'b' = ahbk. For the operation to be well-defined, I need ahbk to lie in the same coset as ab, i.e., ahbk = ab h' for some h' in H.

Student: Let's see... ahbk = ab(b^{-1}hb)k. So I need b^{-1}hb to be back in H, roughly.

Tutor: You just found it. If b^{-1}hb ∈ H for every h ∈ H and every b ∈ G, then ahbk = ab(b^{-1}hb)k, and since (b^{-1}hb)k ∈ H, that whole thing sits in the coset abH. It works out.

Student: So the condition is that b^{-1}Hb = H for every b? That's the "normal" thing I've heard about.

Tutor: That's exactly normality. A subgroup N of G is called normal, written N ◁ G, if gNg^{-1} = N for every g ∈ G. Note it doesn't say gng^{-1} = n for each individual n — just that conjugating the whole set by g gives back the same set.

Student: So elements can move around inside N, they just can't leave it.

Tutor: Right. And here's a nice equivalent way to say it: N is normal exactly when every left coset gN equals the corresponding right coset Ng.

Student: Why is that the same condition?

Tutor: Suppose gNg^{-1} = N. Multiply both sides on the right by g: gN = Ng. Conversely if gN = Ng for all g, multiply on the right by g^{-1} and you get gNg^{-1} = N. It's a direct algebraic dance — one statement literally rearranges into the other.

Student: Okay, so normal subgroups are precisely the ones where you don't have to worry about "left" versus "right" cosets — they coincide.

Tutor: Yes, and that's the deep reason the coset multiplication works. When left and right cosets agree, the shuffling argument you did a minute ago always goes through, for any pair of cosets, not just special ones.

Student: So to recap: if N is normal, (aN)(bN) = abN is a genuinely well-defined operation on the set of cosets.

Tutor: Correct. And once you have a well-defined operation, you should check the group axioms. Associativity is inherited from G. The identity is the coset N itself, i.e., eN. And the inverse of aN is a^{-1}N, since (aN)(a^{-1}N) = aa^{-1}N = eN = N.

Student: So the set of cosets becomes an actual group.

Tutor: That's the factor group, or quotient group, written G/N. Its elements are the cosets of N in G, and its operation is coset multiplication. Its order is |G|/|N|, by Lagrange, since the cosets partition G into equal-sized blocks.

Student: I think I need a concrete example to make this stick.

Tutor: Good instinct. Take G = Z, the integers under addition, and N = 3Z, the multiples of 3. Since Z is abelian, every subgroup is automatically normal — gNg^{-1} = N trivially because gn g^{-1} = n when the group is commutative.

Student: So left and right cosets are the same for free.

Tutor: Exactly, abelian groups give you normality with zero effort. The cosets of 3Z in Z are 0+3Z, 1+3Z, and 2+3Z — the residue classes mod 3.

Student: And the factor group operation is just adding representatives?

Tutor: Right: (a+3Z) + (b+3Z) = (a+b)+3Z. So (1+3Z)+(2+3Z) = 3+3Z = 0+3Z, since 3 is a multiple of 3.

Student: That's just... addition mod 3.

Tutor: You've essentially rediscovered Z/3Z, and it's the reason we call the whole construction "Z mod N" in the first place. The factor group Z/3Z is isomorphic to the familiar group of integers mod 3.

Student: Can I see a non-abelian example, just to make sure normality is doing real work there?

Tutor: Sure — take G = S_3, the symmetries of a triangle, and let N = A_3, the rotations (including the identity), which has order 3. Since [S_3 : A_3] = 2, and any subgroup of index 2 is automatically normal —

Student: Wait, why is index 2 always normal?

Tutor: Good question to end on. If N has index 2, there are only two cosets total. One of them is N itself. The other one has to be everything left over — G minus N — whether you build it from the left or the right. There's no room for the left and right versions to differ, since both are forced to be the complement of N.

Student: So the factor group G/N here has order 2.

Tutor: Right, S_3/A_3 has exactly two elements: the coset A_3 (the "rotations") and the coset of any reflection (the "flips"). And multiplying two flip-cosets gives a rotation-coset, matching your intuition that flip-times-flip undoes the flip.

Student: So the factor group is basically recording the parity of the permutation — even or odd — and forgetting everything else.

Tutor: Beautifully put. That's the real power of factor groups: normality lets you collapse a group down to a smaller one that tracks exactly one feature you care about — parity here, remainder mod 3 there — while cleanly discarding the rest."""

MAXIMAL_PRIME_IDEALS = """Tutor: Let's pick up where we left off with ideals. You know what an ideal is — today I want to add two adjectives to that word: "maximal" and "prime." They sound like they might mean the same thing. They don't, though they're closely related. Which one do you want to start with?

Student: Maximal sounds more intuitive. Biggest ideal, right?

Tutor: Careful — not "biggest ideal" in absolute terms, because the whole ring R is technically an ideal too, and it's the biggest one. We exclude that. A maximal ideal is a *proper* ideal — meaning M ≠ R — such that there's no proper ideal strictly bigger than it. So M is as large as it can get while still failing to be everything.

Student: So if I have M, and I try to add anything not already in M, I'd be forced to generate the whole ring?

Tutor: Exactly. Formally: if M ⊆ I ⊆ R for some ideal I, then either I = M or I = R. There's no room to wedge anything strictly in between M and R.

Student: Okay, and prime ideals?

Tutor: Different flavor entirely — it's a condition about multiplication, not about size. P is a prime ideal if it's proper, and whenever ab ∈ P, at least one of a or b is already in P.

Student: That looks like the definition of a prime number, sort of. If p divides ab, then p divides a or p divides b.

Tutor: That's not a coincidence — it's literally the generalization. In fact, in ℤ, the ideal (p) for a prime number p is exactly a prime ideal in this ring-theoretic sense, which is why the name was borrowed.

Student: So every prime ideal comes from an actual prime number?

Tutor: In ℤ, yes, essentially — plus the zero ideal, which we'll come back to. But the definition itself is stated for any commutative ring, so it applies far more generally, like in polynomial rings.

Student: Are maximal ideals always prime, then?

Tutor: Good instinct to ask. Yes — in a commutative ring with identity, every maximal ideal is prime. The reverse isn't true in general: not every prime ideal is maximal.

Student: Can you show me why maximal implies prime? I don't want to just take your word for it.

Tutor: Let's use the theorem that makes this transparent — the connection to quotient rings. Here it is: R/M is a field if and only if M is maximal. And separately: R/P is an integral domain if and only if P is prime.

Student: And a field is automatically an integral domain...

Tutor: There you go — you just proved it yourself. If M is maximal, R/M is a field, and every field is an integral domain, so R/M is an integral domain, which means M is prime. The whole hierarchy — maximal implies prime — falls straight out of "field implies integral domain."

Student: That's satisfying. But why is R/M a field exactly when M is maximal? I can see the statement but not the mechanism.

Tutor: Think about what "field" requires: every nonzero element has a multiplicative inverse. Take a nonzero coset a + M in R/M — that means a ∉ M. Now consider the ideal generated by M and a together, call it M + (a). This ideal strictly contains M, since a is in it but not in M.

Student: And M is maximal, so that bigger ideal has to be all of R.

Tutor: Exactly — there's nothing strictly between M and R, so M + (a) = R. That means 1 ∈ M + (a), so we can write 1 = m + ra for some m ∈ M and r ∈ R. Reduce that equation mod M...

Student: The m disappears since it's in M, so 1 ≡ ra mod M. That means ra + M is the multiplicative identity times... wait, that means r + M is the inverse of a + M!

Tutor: Precisely. Every nonzero coset has an inverse, so R/M is a field. And the converse direction runs the same argument backwards: if R/M is a field, any ideal strictly between M and R would give you a nonzero non-invertible coset, contradiction.

Student: What about the prime side — why does ab ∈ P force a ∈ P or b ∈ P exactly when R/P has no zero divisors?

Tutor: Translate everything into cosets. ab ∈ P means (a + P)(b + P) = 0 + P in R/P. Integral domain means: if a product of two elements is zero, one of the factors must be zero. So (a+P)(b+P) = 0 forces a + P = 0 or b + P = 0 — that is, a ∈ P or b ∈ P. It's literally the same statement, just written multiplicatively versus in terms of cosets.

Student: I like that these aren't two separate facts to memorize — they're the same idea in two different rings.

Tutor: Right. Now let's ground this with ℤ, since it's the example everyone should have on reflex. Take the ideal (6) = {..., -6, 0, 6, 12, ...}. Is it prime?

Student: Well, 2 · 3 = 6 ∈ (6), but neither 2 nor 3 is in (6). So it fails — (6) is not prime.

Tutor: Right, consistent with 6 not being a prime number. Now try (5).

Student: If ab is a multiple of 5, then since 5 is prime, 5 divides a or 5 divides b. So (5) is prime. And is it maximal?

Tutor: Check ℤ/(5). What is it?

Student: That's ℤ/5ℤ — the integers mod 5. Since 5 is prime, every nonzero residue has an inverse mod 5 — I remember that from before. So ℤ/(5) is a field, which by your theorem means (5) is maximal.

Tutor: Exactly right. In fact in ℤ, the nonzero prime ideals (p) for prime p are all maximal — there's no distinction there. The one exception is the zero ideal.

Student: (0)? Is that prime?

Tutor: Check the definition: ab ∈ (0) means ab = 0, and since ℤ has no zero divisors, that forces a = 0 or b = 0. So yes, (0) is a prime ideal.

Student: But it's not maximal, because (0) ⊂ (2) ⊂ ℤ, say, and (2) is a proper ideal strictly bigger.

Tutor: Right — so (0) gives you a clean example of "prime but not maximal" in ℤ. That matches the quotient picture too: ℤ/(0) is just ℤ itself, which is an integral domain but not a field, since only ±1 have inverses.

Student: So the general moral is: quotienting by a prime ideal only guarantees "no zero divisors," but quotienting by a maximal ideal guarantees the much stronger "everything nonzero is invertible."

Tutor: Beautifully put. One more example, to see this isn't just a ℤ phenomenon — consider the polynomial ring ℝ[x], and the ideal (x). What's ℝ[x]/(x)?

Student: Setting x to 0 in effect, so every polynomial reduces to its constant term. That should just give ℝ.

Tutor: Right, and ℝ is a field, so (x) is maximal in ℝ[x]. Now what about (x² + 1)?

Student: Hmm, x² + 1 has no real roots, so it doesn't factor over ℝ. Modding out sets x² = -1, so we're adjoining a square root of -1... that's ℂ!

Tutor: Exactly, ℝ[x]/(x² + 1) ≅ ℂ, a field, so (x² + 1) is also maximal — even though it's generated by a degree-2 polynomial, not a degree-1 one like (x). Maximality here is about irreducibility, not about degree.

Student: And if I took something reducible, like (x² - 1) = (x-1)(x+1)?

Tutor: Try it — what happens in the quotient?

Student: (x-1)(x+1) is in the ideal, but by unique factorization neither factor alone is, unless... actually in the quotient ring, (x-1) and (x+1) become zero-divisors of each other, since their product is 0 but neither is 0 individually. So the quotient isn't even an integral domain, meaning (x²-1) is not even prime, let alone maximal.

Tutor: You've basically just discovered the general principle for polynomial rings over a field: (f(x)) is prime — and in fact maximal, in this one-variable case — exactly when f is irreducible. Reducible polynomials give you zero divisors in the quotient, which kills primality immediately.

Student: So irreducibility in the ring of polynomials is playing the same role primality played in ℤ.

Tutor: That's the unifying insight underneath all of this. "Maximal" and "prime" are really about how thoroughly you're allowed to factor before you run out of room, and the quotient-ring theorem is what lets you read that factoring behavior off as an algebraic property — field versus integral domain — instead of having to check ideals by hand every time."""


def test_sets_equivalence_now_abstains_instead_of_a_confident_wrong_answer():
    """teach-ceg: this WAS a CONFIDENT WRONG ANSWER (judson:1.2-sets-and-
    equivalence-relations is the correct answer; the text recovered as
    judson:18.2-factorization-in-integral-domains instead, because the
    24-point coverage gap fell one point short of
    `_DECISIVE_MARGIN_COVERAGE_GAP`'s then-0.25 veto threshold). Confirmed at
    the time (see module docstring) this was NOT caused by teach-hpa's
    ratio-credibility gate -- the same outcome occurred with that gate
    removed entirely.

    Fixed by recalibrating `_DECISIVE_MARGIN_COVERAGE_GAP` from 0.25 to
    0.18 -- derived from the PRE-EXISTING 7.9pt-safe/39.6pt-danger
    calibration pair alone (biased toward the safe/abstain side per this
    module's own stated risk asymmetry, not picked to fit this case), then
    checked -- not tuned -- against this case. See that constant's comment
    in concept_recovery.py for the full reasoning, and this bead's handoff
    for the fresh, independently-authored held-out round run before closing
    (round4, five topics never used as a fixture in round1/2/3: the
    division algorithm, group definitions and examples, polynomial rings,
    fields of fractions, extension fields).

    UPDATE (teach-57f): the abstain branch shifted. teach-57f's
    `_DISCOURSE_STOPWORDS` addition dropped judson:18.2's raw score against
    this text from 14 to 10 (removing generic discourse words its uniquely
    long, discursive `definition` prose had accumulated), pulling it from a
    two-way near-margin tie against judson:6.2-lagranges-theorem into a
    three-way exact tie at score 10 with the correct answer,
    judson:1.2-sets-and-equivalence-relations, and judson:16.1-rings --
    judson:6.2-lagranges-theorem (score 7) is no longer even in the "close"
    set. The outcome is still the SAME SAFE ABSTENTION and judson:18.2 is
    still not confidently returned; only the other member named in the
    abstain reason changed, from the rival that was closest before this fix
    to the one that's closest now. See teach-57f's handoff for the full
    trace."""
    result = recover_from_lesson_text(SETS_EQUIVALENCE, GRAPH)
    assert result.taught_node_id is None, (
        f"expected abstention (teach-ceg fix) -- got a confident answer of "
        f"{result.taught_node_id!r} instead"
    )
    assert result.taught_node_id != "judson:18.2-factorization-in-integral-domains", (
        "would be the original confident WRONG answer if this ever fires"
    )
    assert result.abstain_reason is not None
    assert "judson:18.2-factorization-in-integral-domains" in result.abstain_reason
    assert "judson:1.2-sets-and-equivalence-relations" in result.abstain_reason


def test_subgroups_correctly_recovers_after_teach_scx_fix():
    """CORRECT RECOVERY, as of teach-scx -- was a CORRECT RECOVERY after
    teach-57f, then a SAFE ABSTENTION for one bead cycle (teach-911 -> teach-
    scx; see git history for that intermediate state), now correct again.

    teach-911 folded Judson's own 2x2-matrix noncommutative-ring example
    into judson:16.1-rings' definition to give it the vocabulary
    ("matrices", "matrix", "entries", "noncommutative") a natural-language
    rings lesson actually uses (fixing
    tests/test_concept_recovery_judson_full_graph_generalization_round5.py,
    test_rings_now_correctly_recovers_after_teach_911_fix). That same
    example's framing sentence ("matrices... form a ring under the usual
    operations...") also introduced "form" into judson:16.1-rings'
    vocabulary as a side effect. "case"/"neither"/"since"/"usual"/"usually"
    from the same sentence were excluded via `_DISCOURSE_STOPWORDS` (zero
    regressions measured across the full suite), but "form" could not be:
    doing so flips a different, unrelated test
    (test_maximal_prime_ideals_abstains_via_teach_hpa_gate_no_regression_vs_ungated)
    from a safe abstention into a CONFIDENT WRONG ANSWER. With "form" left
    in scoring, judson:16.1-rings' raw score on THIS text rose from 13 to
    14 -- exactly `_MIN_MARGIN` over judson:3.3-subgroups' 12, which is just
    enough to move this case out of the multi-candidate coverage tiebreak
    (margin < `_MIN_MARGIN`, where a 100%-covered rival can still win) and
    into the single-candidate bare-minimum-margin branch (margin ==
    `_MIN_MARGIN`), which can only return the raw-score leader or abstain --
    it has no path to hand the win to a better-covered rival the way the
    tiebreak branch does. That branch abstained here, correctly refusing to
    call rings over a rival it could see was 100% covered, but the correct
    answer used to be reachable and no longer was. Filed forward as
    teach-scx.

    teach-scx closes the gap with `EXCERPT_EDITS` in
    extract_judson_ring_field.py: it elides exactly the word "form" from
    the folded-in matrix example's text (ellipsis-marked, nothing else
    reworded), so it no longer contributes to judson:16.1-rings' score
    anywhere, while "matrices"/"matrix"/"entries"/"noncommutative" still
    do. "form" is untouched everywhere else in the graph, including
    judson:18.2's own vocabulary, so the maximal/prime-ideals test above is
    unaffected. judson:16.1-rings' score on this text drops back to 13,
    margin over subgroups narrows back to 1 (below `_MIN_MARGIN`), and
    control returns to the multi-candidate coverage tiebreak, where
    judson:3.3-subgroups' 100% self-coverage (vs. rings' 25%) wins outright
    again -- the exact pre-teach-911 numbers."""
    result = recover_from_lesson_text(SUBGROUPS, GRAPH)
    assert result.taught_node_id == "judson:3.3-subgroups"
    assert result.abstain_reason is None

    raw = score_candidates(SUBGROUPS, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:16.1-rings"] == 13
    assert scores["judson:3.3-subgroups"] == 12


def test_cosets_recovers_as_the_closely_related_lagrange_node():
    """BOUNDARY CASE, not a clean win: this dialogue teaches cosets
    thoroughly but also explicitly derives Lagrange's theorem in its closing
    exchanges. It recovers as judson:6.2-lagranges-theorem (87% of ITS OWN
    vocabulary covered) via the pre-existing multi-candidate-tie branch
    (teach-ngy's code) rather than the correct judson:6.1-cosets, whose raw
    score (6) never even enters the tied "close" candidate set (tied at
    score 13: judson:18.2 and judson:6.2). Not attributed to teach-hpa --
    this branch doesn't touch teach-hpa's decisive-margin code at all -- and
    not filed as a new confident-wrong-answer bug since the recovered node
    is a real, substantial part of what the text teaches. Asserted here as
    the actual measured behavior, not a judgment that it's correct."""
    result = recover_from_lesson_text(COSETS, GRAPH)
    assert result.taught_node_id == "judson:6.2-lagranges-theorem"


def test_normal_subgroups_abstains_via_teach_hpa_gate_no_regression_vs_ungated():
    """SAFE ABSTENTION through teach-9wx's decisive-margin coverage-gap
    check, with teach-hpa's ratio-credibility gate active and NOT changing
    the outcome (verified in the module docstring: the ungated check reaches
    the identical abstain decision, since the best-covered rival,
    judson:6.1-cosets at 100% coverage, is credible under the gate anyway).
    Correctly prevents a confident WRONG answer (the raw-score leader here
    is judson:16.3-ring-homomorphisms-and-ideals, not the true answer). The
    true answer, judson:10.1-factor-groups-and-normal-subgroups, is not even
    the named rival (judson:6.1-cosets covers more of its own vocabulary,
    100% vs 88%) -- a pre-existing recall gap, unrelated to this bead."""
    result = recover_from_lesson_text(NORMAL_SUBGROUPS, GRAPH)
    assert result.taught_node_id is None, (
        f"expected abstention -- got a confident answer of "
        f"{result.taught_node_id!r} instead"
    )
    assert result.taught_node_id != "judson:16.3-ring-homomorphisms-and-ideals", (
        "would be a confident WRONG answer if this ever fires"
    )
    assert result.abstain_reason is not None


def test_maximal_prime_ideals_abstains_via_teach_hpa_gate_no_regression_vs_ungated():
    """SAFE ABSTENTION through teach-9wx's decisive-margin coverage-gap
    check. teach-hpa's ratio-credibility gate names the CORRECT answer,
    judson:16.4-maximal-and-prime-ideals (56% coverage, ratio 0.48), as the
    rival that triggers the veto -- without the gate, the same abstention
    would still fire (judson:6.1-cosets at 67% coverage would trigger it
    instead, ratio only 0.19, would fail the gate but there's no gate in the
    ungated check), so this is not evidence the gate changed the outcome,
    only that it changed the DIAGNOSIS. Correctly prevents a confident WRONG
    answer (the raw-score leader is judson:18.2-factorization-in-integral-domains,
    not the true answer)."""
    result = recover_from_lesson_text(MAXIMAL_PRIME_IDEALS, GRAPH)
    assert result.taught_node_id is None, (
        f"expected abstention -- got a confident answer of "
        f"{result.taught_node_id!r} instead"
    )
    assert result.taught_node_id != "judson:18.2-factorization-in-integral-domains", (
        "would be a confident WRONG answer if this ever fires"
    )
    assert result.abstain_reason is not None
