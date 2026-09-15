"""teach-g7r.2: the PreTeXt structural-block parser.

These exercise the parser against the REAL pinned textbook sources (the commit
SHAs in teach/data/textbook_provenance.json), not fixtures, because the claim
under test is "this recovers the structure that is actually in these two
books" -- a hand-written fixture would only test my idea of what PreTeXt looks
like, which is the thing that was already wrong once here (the bead assumed
`<definition>` elements; neither book has any).

The sources live outside the repo by design, so every test that needs them
skips rather than fails when the cache is absent.
"""
import xml.etree.ElementTree as ET

import pytest

from teach.pretext_parser import (
    DEFINITION_KIND,
    JUDSON_GLOB,
    JUDSON_SRC,
    LEVIN_GLOB,
    LEVIN_SRC,
    count_elements,
    iter_blocks,
    iter_book,
    render_text,
)

needs_judson = pytest.mark.skipif(
    not JUDSON_SRC.is_dir(), reason=f"pinned Judson source not cached at {JUDSON_SRC}"
)
needs_levin = pytest.mark.skipif(
    not LEVIN_SRC.is_dir(), reason=f"pinned Levin source not cached at {LEVIN_SRC}"
)


@pytest.fixture(scope="module")
def groups():
    return list(iter_blocks(JUDSON_SRC / "groups.xml"))


@needs_judson
@needs_levin
def test_neither_source_tags_a_single_definition():
    """The premise teach-g7r.2 was written on is false, and stays checked.

    If this fails, an upstream added real `<definition>` elements: prefer them
    over recovered term-definitions and update the module docstring's census.
    """
    assert count_elements(JUDSON_SRC, JUDSON_GLOB)["definition"] == 0
    assert count_elements(LEVIN_SRC, LEVIN_GLOB)["definition"] == 0


@needs_judson
def test_group_definition_is_recovered_from_term_bearing_prose(groups):
    """The stand-in for the missing `<definition>` actually fires, and carries
    the axioms -- a definition of a group without associativity, identity and
    inverses is not a definition of a group."""
    defs = [b for b in groups if b.kind == DEFINITION_KIND and "group" in b.terms]
    assert defs, "no term-definition recovered for 'group'"
    text = " ".join(b.text for b in defs).lower()
    for axiom in ("associat", "identity", "inverse"):
        assert axiom in text


@needs_judson
def test_term_values_stop_at_the_closing_tag(groups):
    """Regression. The first version rendered an element's own tail as part of
    its text, so terms ran into the following sentence -- 'identity element,'
    and 'associative. That is,' instead of the terms themselves. Block text
    was unaffected, so only the term tuples showed it."""
    defs = [b for b in groups if b.kind == DEFINITION_KIND and "group" in b.terms]
    assert defs[0].terms == (
        "binary operation", "law of composition", "group",
        "associative", "identity element", "inverse element",
    )


def test_render_text_excludes_the_elements_own_tail():
    """The mechanism of the bug above, in isolation and with no source files:
    the text of `<term>` is the term, never what follows it."""
    p = ET.fromstring("<p>a <term>group</term>, which is nice.</p>")
    assert render_text(p.find("term")) == "group"
    assert render_text(p) == "a group, which is nice."


@needs_judson
def test_math_is_inlined_not_dropped(groups):
    """This theorem's content is almost entirely LaTeX. With math dropped its
    text would read as fluent English with the quantifiers gone."""
    (thm,) = [b for b in groups if b.xml_id == "groups-theorem-exponent-laws"]
    assert thm.kind == "theorem"
    assert "g^mg^n = g^{m+n}" in thm.text
    assert "$" in thm.text


@needs_judson
def test_statement_wrapper_is_unwrapped_so_titles_do_not_leak():
    """Judson wraps 1191 theorem-like bodies in `<statement>`; taking the
    whole element would prepend the title to the statement.

    Scanned book-wide, not over one chapter: `groups.xml` happens to contain
    no titled theorem at all, so the one-chapter version of this assertion
    looped over an empty list and passed without testing anything. Named
    theorems ("Lagrange", "First Isomorphism Theorem") live in other files.
    """
    titled = [
        b for b in iter_book(JUDSON_SRC, JUDSON_GLOB)
        if b.title and b.kind in ("theorem", "lemma", "corollary", "proposition")
    ]
    assert len(titled) == 38, len(titled)
    for b in titled:
        assert not b.text.startswith(b.title), (b.source_file, b.title)


@needs_judson
def test_blocks_carry_the_division_context_needed_to_cite_them(groups):
    (thm,) = [b for b in groups if b.xml_id == "groups-theorem-exponent-laws"]
    assert thm.chapter_title == "Groups"
    assert thm.chapter_id == "groups"
    assert thm.section_title
    assert thm.source_file == "groups.xml"
    assert "Groups" in thm.cite()


@needs_judson
def test_exercise_subtrees_are_not_harvested():
    """Judson has 913 `<exercise>` elements, full of `<term>`. An exercise
    mentions a term without defining it, so harvesting them would produce
    definition records whose text defines nothing."""
    root = ET.parse(JUDSON_SRC / "groups.xml").getroot()
    exercises = list(root.iter("exercise"))
    assert exercises, "expected exercises in groups.xml"

    exercise_ids = {
        e.get("{http://www.w3.org/XML/1998/namespace}id") for e in exercises
    } - {None}
    recovered_ids = {b.xml_id for b in iter_blocks(JUDSON_SRC / "groups.xml")}
    assert not (exercise_ids & recovered_ids)


@needs_judson
def test_judson_block_census_is_reproducible():
    """Exact counts, not floors: the source is pinned to an immutable commit
    SHA, so a change here means a real change in what the parser recovers."""
    import collections

    kinds = collections.Counter(b.kind for b in iter_book(JUDSON_SRC, JUDSON_GLOB))
    assert kinds["theorem"] == 136
    assert kinds["lemma"] == 44
    assert kinds["corollary"] == 39
    assert kinds["proposition"] == 55
    assert kinds["proof"] == 207
    assert kinds["example"] == 245
    assert kinds[DEFINITION_KIND] == 199


@needs_judson
def test_lagrange_theorem_text_matches_the_hand_authored_graphs_claim():
    """teach/judson_algebra_graph.py's target node asserts Lagrange says
    '|H| divides |G|', and refuses several edges on the grounds that this
    statement never mentions permutations or generators. That reasoning is
    only sound if the parsed statement really says so."""
    lagrange = [
        b for b in iter_blocks(JUDSON_SRC / "cosets.xml")
        if b.xml_id == "cosets-theorem-lagrange"
    ]
    assert lagrange, "Lagrange's theorem not found in cosets.xml"
    text = lagrange[0].text
    assert "divide the number of elements" in text
    assert "permutation" not in text.lower()
    assert "generator" not in text.lower()


@needs_levin
def test_levin_set_and_proof_technique_definitions_are_recovered():
    """The foundational-layer material Epic 2 needs, if teach-9ug picks Levin."""
    sets = [
        b for b in iter_blocks(LEVIN_SRC / "sec_intro-sets.ptx")
        if b.kind == DEFINITION_KIND and "set" in b.terms
    ]
    assert sets
    assert "unordered collection" in " ".join(b.text for b in sets)

    proofs = {
        t
        for b in iter_blocks(LEVIN_SRC / "sec_logic-proofs.ptx")
        if b.kind == DEFINITION_KIND
        for t in b.terms
    }
    assert {"direct proof", "proof by contrapositive", "proof by contradiction"} <= proofs
