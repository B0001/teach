"""teach-9ba: fresh held-out round testing this bead's own suggested next
step -- "check whether judson:3.2-definitions-and-examples (group axioms)
and other well-covered nodes show the same paraphrase-sensitivity [as
rings/subgroups] with their OWN fresh blind fixtures, to determine whether
this is rings-specific... or a general property."

Both texts below were produced by two separate, parallel `Agent` tool calls,
each given an explicit no-tool-use, no-repository-access, no-internet
instruction and told nothing about concept_recovery.py, this bead, or any
threshold/mechanism in this module -- only a plain-English topic name and a
request to render it as a natural tutor/student dialogue from the agent's own
general abstract-algebra knowledge. Neither agent saw the other's output, this
module's code, or teach-9ba's own three original fixtures (whose exact text
was never preserved -- see sandbox-handoffs/teach-scx.md's closing note).

HONEST RESULT (measured once against the real, unmodified, current-tree
`load_judson_full_graph()`, via the public `recover_from_lesson_text` /
`score_candidates` / `score_candidates_semantic` entry points only -- no
internals were read to choose or adjust either text, no threshold or
vocabulary was changed in response to seeing these results):

  CYCLIC_SUBGROUPS_BLIND: CORRECT RECOVERY (judson:4.1-cyclic-subgroups,
      raw tier, 81.8% coverage of its own vocabulary -- below the nominal
      85% coverage-tiebreak floor, but never needed it: this text clears
      the bare-minimum-margin branch outright).

  GROUP_AXIOMS_BLIND: two-part result.
      - Raw exact-word tier: SAFELY ABSTAINS, via the SAME decisive-margin
        coverage-gap veto (teach-9wx/teach-hpa) the bead's original three
        fixtures hit. judson:16.1-rings leads raw overlap (13, decisive
        margin 6) but covers only 25% of its own 52-word vocabulary; the
        true topic node judson:3.2-definitions-and-examples is found as the
        best-covered credible rival at 55% coverage of its own 11-word
        vocabulary -- a 29.5-point gap, comfortably clearing
        _DECISIVE_MARGIN_COVERAGE_GAP (18pt). This CONFIRMS the bead's own
        open question: the phenomenon is NOT narrowly rings/subgroups-
        specific paraphrase sensitivity -- it generalizes to a THIRD,
        unrelated topic (group axioms, which never mentions rings at all).
        judson:16.1-rings' vocabulary is simply broad/generic enough
        ("binary", "operation", "satisfying", "together", "abelian",
        "addition", "conditions", "notice", "first", "last") to decisively
        out-raw-score almost any group-theory-adjacent lesson; the coverage-
        gap veto is what has, so far, safely caught every one of these
        (rings/subgroups in teach-9ba's original round, now group axioms
        too), not a rings-specific vocabulary defect fixable by adding a
        few synonyms.
      - BUT: because the raw tier abstains, `recover_taught_concept` falls
        through to the semantic (WordNet) fallback tier, which surfaces a
        DIFFERENT, more severe bug: a CONFIDENT WRONG ANSWER
        (judson:16.1-rings again, this time with abstain_reason=None).
        WordNet synonym expansion inflates rings' score from 13 to 18 but
        judson:3.2's only from 6 to 6, so judson:3.2 drops below the
        decisive branch's `credible_rivals` score-ratio filter
        (_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO, teach-hpa) even though its
        LITERAL coverage (unchanged at 55%) is still the best of anyone's.
        This is a DIFFERENT failure mechanism than what this bead is about
        (a confident wrong answer, not a safe abstention) -- filed forward
        as teach-jkx (discovered-from this bead) rather than fixed here, per
        this lineage's standing rule against fixing in the same session that
        found the bug (teach-ceg, teach-i35 precedent). See teach-jkx for the
        full trace and root-cause analysis.

Net for THIS bead's own question: CONFIRMED as a general property of
judson:16.1-rings' vocabulary breadth, not rings-specific paraphrase
sensitivity -- see test_group_axioms_raw_tier_safely_abstains_confirms_general_property
below. The full-pipeline confident-wrong-answer outcome is a separate bug
(teach-jkx), demonstrated here only for the record
(test_group_axioms_full_pipeline_is_a_confident_wrong_answer_teach_jkx) and
NOT this bead's to fix.
"""

from teach.concept_recovery import (
    build_vocabulary_index,
    recover_from_lesson_text,
    score_candidates,
    score_candidates_semantic,
    _coverage_fraction,
    _resolve_candidates,
    _words,
)
from teach.judson_algebra_graph import load_judson_full_graph

GRAPH = load_judson_full_graph()
INDEX = build_vocabulary_index(GRAPH)


GROUP_AXIOMS_BLIND = """tutor: Let's define a group. It's a set G together with a binary operation, usually written multiplicatively, satisfying four axioms.

learner: Okay, what's the first one?

tutor: Closure. For any a, b in G, the product a·b must also be in G. The operation can't send you outside the set.

learner: And associativity is the usual thing?

tutor: Right — (a·b)·c = a·(b·c) for all a, b, c in G. It means we can drop parentheses in longer products without ambiguity. Note we're not requiring commutativity yet, so order still matters.

learner: What's third?

tutor: Identity. There must exist an element e in G such that e·a = a·e = a for every a in G. It's the "do nothing" element.

learner: And the last one is inverses?

tutor: Exactly. For every a in G, there exists some element a⁻¹ in G with a·a⁻¹ = a⁻¹·a = e. Every element can be "undone."

learner: So closure, associativity, identity, inverses — CAII, four conditions on a set-plus-operation pair.

tutor: That's the whole definition. Notice commutativity, a·b = b·a, was never required. When it does hold for all elements, we call the group abelian, or commutative — named after Niels Henrik Abel. The integers under addition are abelian; symmetries of a triangle under composition are not, since order of operations changes the outcome there.

learner: So every abelian group is a group, but not every group is abelian.

tutor: Precisely — abelian is a special, stronger property layered on top of the four basic axioms, not part of the base definition itself."""

CYCLIC_SUBGROUPS_BLIND = """Tutor: Let's talk about cyclic subgroups. If you take an element g in a group G and look at all its powers — g, g², g³, and so on, plus g⁰ = e and the negative powers g⁻¹, g⁻², ... — that whole collection is automatically a subgroup. We call it the subgroup generated by g, written ⟨g⟩, and g is called a generator.

Learner: Why is that automatically a subgroup? Couldn't the powers just be some random subset?

Tutor: Check the subgroup criteria: it contains the identity (g⁰), it's closed under the operation (gᵃ times gᵇ is just gᵃ⁺ᵇ, still a power of g), and every element has an inverse in the set (the inverse of gᵃ is g⁻ᵃ). So no matter what g you pick, ⟨g⟩ satisfies all three automatically.

Learner: What determines how big ⟨g⟩ is?

Tutor: That's the order of g — the smallest positive integer n such that gⁿ = e. If such an n exists, ⟨g⟩ has exactly n elements: e, g, g², ..., gⁿ⁻¹. If no power ever returns to e, g has infinite order and ⟨g⟩ is infinite.

Learner: Can you give me a concrete picture?

Tutor: Sure — think of rotating a square by 90°. Call that rotation r. Then r¹ is 90°, r² is 180°, r³ is 270°, and r⁴ brings you back to 0°, the identity. So r has order 4, and ⟨r⟩ = {e, r, r², r³} is a cyclic subgroup of order 4 sitting inside the symmetry group of the square.

Learner: And in ℤ mod n under addition?

Tutor: There, "powers" of 1 just mean repeated addition: 1, 1+1, 1+1+1, .... Since n·1 ≡ 0, the element 1 generates the whole group, and its order is n."""


def test_cyclic_subgroups_correctly_recovers():
    """CORRECT RECOVERY on fresh, blind text about a well-covered,
    non-rings/subgroups node -- a positive control showing this class of
    genuine, on-topic blind lesson does NOT always abstain."""
    result = recover_from_lesson_text(CYCLIC_SUBGROUPS_BLIND, GRAPH)
    assert result.taught_node_id == "judson:4.1-cyclic-subgroups"
    assert result.abstain_reason is None

    raw = score_candidates(CYCLIC_SUBGROUPS_BLIND, INDEX)
    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:4.1-cyclic-subgroups"] == 9
    text_words = _words(CYCLIC_SUBGROUPS_BLIND)
    top = next(c for c in raw if c.node_id == "judson:4.1-cyclic-subgroups")
    assert round(_coverage_fraction(top, INDEX, text_words), 3) == round(9 / 11, 3)


def test_group_axioms_raw_tier_safely_abstains_confirms_general_property():
    """This bead's own central question, answered: the raw exact-word tier
    hits the SAME decisive-margin coverage-gap veto (teach-9wx/teach-hpa) on
    a fresh, blind "group axioms" lesson that never mentions rings at all --
    confirming this is a general property of judson:16.1-rings' broad,
    generic vocabulary (which decisively out-raw-scores many distinct
    group-theory-adjacent topics), not a narrow rings/subgroups paraphrase
    mismatch. Tests the raw tier's own resolution directly (bypassing the
    semantic fallback, which surfaces a DIFFERENT bug -- see teach-jkx and
    the test below)."""
    raw = score_candidates(GROUP_AXIOMS_BLIND, INDEX)
    text_words = _words(GROUP_AXIOMS_BLIND)
    taught_node_id, abstain_reason = _resolve_candidates(raw, INDEX, text_words)

    assert taught_node_id is None
    assert "judson:16.1-rings" in abstain_reason
    assert "judson:3.2-definitions-and-examples" in abstain_reason

    scores = {c.node_id: c.score for c in raw}
    assert scores["judson:16.1-rings"] == 13
    assert scores["judson:3.2-definitions-and-examples"] == 6

    rings_match = next(c for c in raw if c.node_id == "judson:16.1-rings")
    g32_match = next(c for c in raw if c.node_id == "judson:3.2-definitions-and-examples")
    rings_coverage = _coverage_fraction(rings_match, INDEX, text_words)
    g32_coverage = _coverage_fraction(g32_match, INDEX, text_words)
    assert round(rings_coverage, 3) == round(13 / 52, 3)
    assert round(g32_coverage, 3) == round(6 / 11, 3)
    assert g32_coverage - rings_coverage >= 0.18  # _DECISIVE_MARGIN_COVERAGE_GAP


def test_group_axioms_full_pipeline_safely_abstains_teach_jkx_fixed():
    """teach-jkx FIXED in session 5. This test used to assert the bug's
    current (buggy) behavior on purpose, same discipline as teach-i35's
    pre-fix GRADE6_UNSIGNPOSTED_GARDENING test: the raw tier safely abstains
    (previous test), but recover_taught_concept fell through to the semantic
    tier, whose `credible_rivals` filter (teach-hpa's
    _DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO) compared semantically-inflated
    scores rather than literal coverage -- judson:3.2's semantic score (6)
    didn't clear 0.35 * rings' inflated semantic score (18), so it was
    excluded from the rival search even though its LITERAL coverage was
    still the best of anyone's, and no veto fired.

    Session 5's fix caps the winner's score used for that ratio at its own
    raw-tier score inflated by no more than `_SEMANTIC_INFLATION_CAP_RATIO`
    (see that constant's comment and the long comment above
    `_DECISIVE_MARGIN_RIVAL_MIN_SCORE_RATIO` in concept_recovery.py for the
    full mechanism and validation, including a third held-out round --
    tests/test_concept_recovery_judson_full_graph_generalization_round10.py
    -- built specifically to stress this fix on fresh material). Rings' raw
    score here is 13, so its capped credibility score is
    ceil(13 * 1.25) = 17; judson:3.2's semantic score of 6 now clears
    0.35 * 17 = 5.95, making it a credible rival, and the pre-existing
    decisive-margin coverage-gap veto fires -- the lesson now safely
    abstains instead of confidently naming the wrong node."""
    result = recover_from_lesson_text(GROUP_AXIOMS_BLIND, GRAPH)
    assert result.taught_node_id is None, (
        f"expected a safe abstention now that teach-jkx is fixed, got a "
        f"confident answer: {result.taught_node_id!r}"
    )
    assert result.abstain_reason

    semantic = score_candidates_semantic(GROUP_AXIOMS_BLIND, INDEX)
    scores = {c.node_id: c.score for c in semantic}
    assert scores["judson:16.1-rings"] == 18
    assert scores["judson:3.2-definitions-and-examples"] == 6


if __name__ == "__main__":
    test_cyclic_subgroups_correctly_recovers()
    test_group_axioms_raw_tier_safely_abstains_confirms_general_property()
    test_group_axioms_full_pipeline_is_a_confident_wrong_answer_teach_jkx()
    print(
        "OK: teach-9ba's phenomenon confirmed as a general property "
        "(cyclic-subgroups recovers correctly; group-axioms' raw tier "
        "safely abstains via the same veto rings/subgroups hit); the "
        "full-pipeline confident-wrong-answer on group-axioms is a separate "
        "bug, filed as teach-jkx"
    )
