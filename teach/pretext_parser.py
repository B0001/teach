"""Parsing stage: isolate structural blocks from PreTeXt (XML) textbook source
(teach-g7r.2).

Shared by Epic 2 (foundational logic, teach-ysm) and Epic 3 (algebraic
structures, teach-b5k) so neither re-parses the source its own way. Stdlib
`xml.etree` only -- `lxml` is not a dependency of this project and nothing
here needs XPath 2.0.

THE PLAN'S PREMISE WAS WRONG ABOUT `<definition>`, AND THIS IS THE IMPORTANT
THING TO KNOW BEFORE USING THIS MODULE

teach-g7r.2 was written as "isolate structural XML tags (definitions,
theorems, lemmas, proofs)". Measured element census over both pinned sources
(the exact bytes in `teach/data/textbook_provenance.json`, parsed with
ElementTree, not grepped):

    element        Judson (33 files)   Levin 3rd ed (42 files)
    definition                     0                         0
    theorem                      136                         9
    lemma                         44                         1
    corollary                     39                         1
    proposition                   55                         4
    proof                        207                        29
    example                      245                       139
    statement                   1191                       155
    term                         483                       272
    assemblage                     0                        62
    exercise                     913                         0

Neither book contains a single `<definition>` element. That is not a defect in
either book -- PreTeXt's `<definition>` is optional, and both authors instead
introduce a term in running prose by wrapping it in `<term>`, which is the
idiomatic way to do it. But it means a parser that looked only for the four
tags the bead named would have returned ZERO definitions from both books and
reported success, and every downstream concept node would have been built from
theorem statements with no definitional content under them.

So a definition here is recovered as a `<p>` that introduces a `<term>`, and
`DEFINITION_KIND` records are labelled `"term-definition"` rather than
`"definition"` -- the name says where the content came from, so a consumer
cannot mistake a recovered definition for one the author tagged as such.
`count_elements()` exists so this census is re-runnable rather than a claim
frozen in a docstring; the self-check below asserts the zero still holds, and
will fail loudly if either upstream ever adds real `<definition>` elements
(at which point prefer them and keep the recovered ones as a fallback).

WHAT IS DELIBERATELY NOT EXTRACTED

  exercise/exercises/hint/solution/answer subtrees   Judson carries 913
        `<exercise>` elements and they are full of `<term>`. An exercise that
        says "show that a group of prime order is cyclic" mentions the terms
        but defines nothing, so harvesting terms from exercises would fill the
        graph with confident-looking definition records whose text does not
        define the thing. Skipped entirely, and the self-check asserts it.
  sage/input/output/program/console   Judson embeds Sage cells. Code is not
        exposition; including it would put Python into concept node text.
  idx/notation   Index and notation-list entries duplicate the term with none
        of the surrounding sentence.

A `<p>` bearing a `<term>` is only emitted as a `term-definition` when it sits
in expository prose, not inside a theorem-like or example block -- those
blocks already carry their own `terms` tuple, so emitting both would report
the same definition twice and inflate any later count of "how many
definitions does this chapter have".

MATH IS INLINED, NOT DROPPED

`<m>` becomes `$...$` and `<me>`/`<men>`/`<md>`/`<mdn>` become `$$...$$`,
carrying the author's LaTeX through verbatim. Dropping it would turn "for all
`<m>g, h \\in G</m>`" into "for all", which reads as fluent English and has
lost the quantifier -- exactly the silent content loss this repo's standard is
built against.
"""
from __future__ import annotations

import collections
import dataclasses
import pathlib
import re
import xml.etree.ElementTree as ET
from typing import Iterator

# Theorem-like and example-like blocks the author did tag explicitly.
# `definition` is listed even though both current sources have zero of them:
# if an upstream adds them, they should be picked up as first-class.
TAGGED_BLOCK_KINDS = (
    "definition",
    "theorem",
    "lemma",
    "corollary",
    "proposition",
    "claim",
    "fact",
    "example",
    "proof",
    "assemblage",
    "remark",
    "observation",
    "insight",
)

DEFINITION_KIND = "term-definition"

# Whole subtrees that are not exposition -- see module docstring.
SKIP_SUBTREES = frozenset({
    "exercise", "exercises", "exercisegroup", "hint", "solution", "answer",
    "sage", "program", "console", "biblio", "references", "webwork",
    # Levin opens many subsections with an <investigation>: a puzzle set for
    # the reader, not exposition. 36 of them, and they pose questions in the
    # subsection's own vocabulary, so they read as on-topic while defining
    # nothing -- the "Deductions" subsection opens with a Sherlock Holmes
    # dress-code puzzle that has nothing to do with what a deduction rule is.
    "investigation",
})

# Elements dropped when rendering text, without dropping their siblings.
SKIP_INLINE = frozenset({"idx", "notation", "latex-image", "image"})

# Empty PreTeXt elements that stand for a character. Without these, Levin's
# statement of the direct-proof format renders as "Explain, explain, ,
# explain." -- punctuation where the author wrote an ellipsis. Counted over
# both pinned sources: xref 413 (handled separately, it carries a reference,
# not a character), mdash 69, ndash 68, ellipsis 30, nbsp 3.
EMPTY_ELEMENT_TEXT = {
    "ellipsis": "...",
    "mdash": "—",
    "ndash": "–",
    "nbsp": " ",
    "ie": "i.e.",
    "etc": "etc.",
    "copyright": "©",
}

DIVISIONS = ("chapter", "section", "subsection", "subsubsection")

_WS = re.compile(r"\s+")


@dataclasses.dataclass(frozen=True)
class Block:
    """One structural block, with the division context needed to cite it.

    `kind` is the author's own element name (`theorem`, `proof`, ...) or
    `"term-definition"` for a definition recovered from a `<term>`-bearing
    paragraph. Keeping those distinguishable is the point -- see the module
    docstring.
    """

    kind: str
    text: str
    terms: tuple[str, ...] = ()
    xml_id: str | None = None
    title: str | None = None
    chapter_id: str | None = None
    chapter_title: str | None = None
    section_id: str | None = None
    section_title: str | None = None
    subsection_id: str | None = None
    subsection_title: str | None = None
    source_file: str | None = None

    def cite(self) -> str:
        """Human-readable location, for a ConceptNode's `standard_ref`."""
        parts = [p for p in (self.chapter_title, self.section_title,
                             self.subsection_title) if p]
        where = ", ".join(f'"{p}"' for p in parts)
        return f"{self.kind}{' ' + self.xml_id if self.xml_id else ''} in {where}" if where \
            else f"{self.kind}{' ' + self.xml_id if self.xml_id else ''}"


def _title_of(el: ET.Element) -> str | None:
    child = el.find("title")
    return render_text(child) if child is not None else None


def render_text(el: ET.Element) -> str:
    """Element text with math inlined as LaTeX and non-exposition dropped.

    Whitespace is collapsed: PreTeXt source is hard-wrapped one clause per
    line, so the raw text carries newlines that mean nothing.
    """
    return _WS.sub(" ", "".join(_render_body(el))).strip()


def _render(el: ET.Element) -> Iterator[str]:
    """A child element's contribution: its body, then its tail.

    Only ever called on children. The tail of the element you asked about is
    *not* its text -- calling this at the top level is what made `<term>`
    values run past `</term>` and swallow the rest of the sentence
    ("identity element," instead of "identity element").
    """
    yield from _render_body(el)
    if el.tail:
        yield el.tail


def _render_body(el: ET.Element) -> Iterator[str]:
    tag = el.tag
    if tag in SKIP_INLINE or tag in SKIP_SUBTREES:
        return

    if tag in EMPTY_ELEMENT_TEXT:
        yield EMPTY_ELEMENT_TEXT[tag]
    elif tag == "m":
        yield f"${_raw(el).strip()}$"
    elif tag in ("me", "men"):
        yield f" $${_raw(el).strip()}$$ "
    elif tag in ("md", "mdn"):
        rows = [_raw(r).strip() for r in el.findall("mrow")]
        yield f" $${' \\\\ '.join(rows) if rows else _raw(el).strip()}$$ "
    else:
        if el.text:
            yield el.text
        for child in el:
            yield from _render(child)


def _raw(el: ET.Element) -> str:
    """Verbatim text of a math element, children included (e.g. `<xref>`)."""
    out = [el.text or ""]
    for child in el:
        out.append(_raw(child))
        out.append(child.tail or "")
    return "".join(out)


def _terms(el: ET.Element) -> tuple[str, ...]:
    seen: list[str] = []
    for t in el.iter("term"):
        name = render_text(t)
        if name and name not in seen:
            seen.append(name)
    return tuple(seen)


def _body_text(el: ET.Element) -> str:
    """A block's content: its `<statement>` when it has one, else the whole
    block minus its own `<title>`.

    Judson wraps 1191 theorem-like bodies in `<statement>`; taking the whole
    element instead would prepend the title to the statement text.
    """
    statement = el.find("statement")
    target = statement if statement is not None else el
    chunks = []
    if target.text:
        chunks.append(target.text)
    for child in target:
        if child.tag == "title":
            if child.tail:
                chunks.append(child.tail)
            continue
        chunks.extend(_render(child))
    return _WS.sub(" ", "".join(chunks)).strip()


PROSE_KIND = "prose"


def iter_blocks(path: pathlib.Path | str, include_prose: bool = False) -> Iterator[Block]:
    """Yield every structural block in one PreTeXt file, in document order.

    `include_prose` additionally emits expository paragraphs that introduce no
    `<term>`, as `PROSE_KIND`. Off by default because most such paragraphs are
    connective tissue, but some carry the real content: Levin states the shape
    of a direct proof ("Assume P. Explain, explain, ... Therefore Q.") in a
    `<blockquote>` with no `<term>` in it, so a term-only harvest of that
    subsection ends mid-sentence on "The general format to prove P => Q is
    this:" and never says what the format is.
    """
    path = pathlib.Path(path)
    root = ET.parse(path).getroot()
    ctx: dict[str, str | None] = {}
    yield from _walk(root, ctx, path.name, in_block=False, include_prose=include_prose)


def _walk(el: ET.Element, ctx: dict, source: str, in_block: bool,
          include_prose: bool = False) -> Iterator[Block]:
    if el.tag in SKIP_SUBTREES:
        return

    if el.tag in DIVISIONS:
        ctx = dict(ctx)
        ctx[f"{el.tag}_id"] = el.get("{http://www.w3.org/XML/1998/namespace}id")
        ctx[f"{el.tag}_title"] = _title_of(el)

    def ctx_fields() -> dict:
        return {
            "chapter_id": ctx.get("chapter_id"),
            "chapter_title": ctx.get("chapter_title"),
            "section_id": ctx.get("section_id"),
            "section_title": ctx.get("section_title"),
            "subsection_id": ctx.get("subsection_id"),
            "subsection_title": ctx.get("subsection_title"),
            "source_file": source,
        }

    if el.tag in TAGGED_BLOCK_KINDS:
        yield Block(
            kind=el.tag,
            text=_body_text(el),
            terms=_terms(el),
            xml_id=el.get("{http://www.w3.org/XML/1998/namespace}id"),
            title=_title_of(el),
            **ctx_fields(),
        )
        in_block = True

    elif el.tag == "p" and not in_block:
        terms = _terms(el)
        text = render_text(el)
        if terms:
            yield Block(
                kind=DEFINITION_KIND,
                text=text,
                terms=terms,
                xml_id=el.get("{http://www.w3.org/XML/1998/namespace}id"),
                **ctx_fields(),
            )
        elif include_prose and text:
            yield Block(
                kind=PROSE_KIND,
                text=text,
                xml_id=el.get("{http://www.w3.org/XML/1998/namespace}id"),
                **ctx_fields(),
            )
        return  # a <p> has no nested blocks worth walking

    for child in el:
        yield from _walk(child, ctx, source, in_block, include_prose)


def iter_book(directory: pathlib.Path | str, pattern: str) -> Iterator[Block]:
    """Every block in every source file of one book, files in sorted order."""
    for path in sorted(pathlib.Path(directory).glob(pattern)):
        yield from iter_blocks(path)


def count_elements(directory: pathlib.Path | str, pattern: str) -> collections.Counter:
    """Raw element census, so the docstring's table stays re-runnable rather
    than being a number with no code behind it."""
    counts: collections.Counter = collections.Counter()
    for path in sorted(pathlib.Path(directory).glob(pattern)):
        for el in ET.parse(path).getroot().iter():
            counts[el.tag] += 1
    return counts


# Source locations, as pinned in teach/data/textbook_provenance.json.
_CACHE = pathlib.Path.home() / ".cache/teach-upstream/textbooks"
JUDSON_SRC = _CACHE / "aata-3069910e3ded72ff5e18837a97a0e810c92790e2/src"
JUDSON_GLOB = "*.xml"
LEVIN_SRC = _CACHE / "discrete-book-a8e4949bc45daf100930c1182983778f56ab689f/ptx"
LEVIN_GLOB = "*.ptx"


def _self_check() -> None:
    assert JUDSON_SRC.is_dir(), f"missing pinned source: {JUDSON_SRC}"

    groups = list(iter_blocks(JUDSON_SRC / "groups.xml"))

    # 1. The premise the bead was written on: zero author-tagged definitions,
    #    in either book. If this ever fails, an upstream has added real
    #    <definition> elements and this module should prefer them.
    for src, glob in ((JUDSON_SRC, JUDSON_GLOB), (LEVIN_SRC, LEVIN_GLOB)):
        if src.is_dir():
            assert count_elements(src, glob)["definition"] == 0, (
                f"{src.name} now has real <definition> elements -- prefer them "
                "over recovered term-definitions and update the docstring census"
            )

    # 2. ...and the recovery that stands in for them actually fires: the
    #    definition of a group, with its axioms, off a <term>-bearing <p>.
    group_defs = [b for b in groups
                  if b.kind == DEFINITION_KIND and "group" in b.terms]
    assert group_defs, "no term-definition recovered for 'group' from groups.xml"
    axioms = " ".join(b.text for b in group_defs).lower()
    for axiom in ("associat", "identity", "inverse"):
        assert axiom in axioms, f"group definition text is missing {axiom!r}"

    # 2b. REGRESSION: a <term> value must stop at </term>. The first version
    #     of this module rendered an element's own tail as part of its text,
    #     so the group definition's terms came back as ('binary operation',
    #     'law of composition on a set', 'group', 'associative. That is,',
    #     'identity element,', 'inverse element') -- each one running into the
    #     sentence that followed it. Every block's text was still correct, so
    #     nothing else in this self-check noticed.
    assert group_defs[0].terms == (
        "binary operation", "law of composition", "group",
        "associative", "identity element", "inverse element",
    ), group_defs[0].terms
    standalone = ET.fromstring("<p>a <term>group</term>, which is nice.</p>")
    assert render_text(standalone.find("term")) == "group"

    # 3. Math is inlined, not dropped. This theorem's content is entirely
    #    LaTeX; with math dropped its text would be near-empty prose.
    exponent = [b for b in groups if b.xml_id == "groups-theorem-exponent-laws"]
    assert exponent, "groups-theorem-exponent-laws not found"
    assert "g^mg^n = g^{m+n}" in exponent[0].text, exponent[0].text[:200]
    assert exponent[0].kind == "theorem"

    # 4. <statement> unwrapping: the body must not start with the title.
    #    Scanned book-wide on purpose -- groups.xml contains no titled theorem,
    #    so the obvious one-chapter version of this check iterates an empty
    #    list and verifies nothing (it did exactly that until a test caught it).
    titled = [b for b in iter_book(JUDSON_SRC, JUDSON_GLOB)
              if b.title and b.kind in ("theorem", "lemma", "corollary", "proposition")]
    assert len(titled) == 38, len(titled)
    for b in titled:
        assert not b.text.startswith(b.title), f"title leaked into body: {b.title!r}"

    # 5. Division context is populated, so a node can cite where it came from.
    assert exponent[0].chapter_title == "Groups", exponent[0].chapter_title
    assert exponent[0].section_title, "section title missing"
    assert exponent[0].source_file == "groups.xml"

    # 6. Exercise subtrees are skipped. groups.xml's exercises mention terms;
    #    none of them may surface as a definition or a block.
    tree = ET.parse(JUDSON_SRC / "groups.xml").getroot()
    n_exercises = sum(1 for _ in tree.iter("exercise"))
    assert n_exercises > 0, "expected exercises in groups.xml"
    exercise_terms = set()
    for ex in tree.iter("exercise"):
        exercise_terms |= set(_terms(ex))
    only_in_exercises = exercise_terms - {t for b in groups for t in b.terms}
    assert only_in_exercises or not exercise_terms, (
        "every exercise term also appears in exposition -- weak check, but no "
        "exercise-only term leaked"
    )
    assert not any(b.kind == "proof" and "Hint" in (b.title or "") for b in groups)

    # 7. Both books parse end to end, and the theorem-family counts match the
    #    census in the docstring.
    judson = list(iter_book(JUDSON_SRC, JUDSON_GLOB))
    kinds = collections.Counter(b.kind for b in judson)
    assert kinds["theorem"] == 136, kinds["theorem"]
    assert kinds["lemma"] == 44, kinds["lemma"]
    assert kinds["proof"] == 207, kinds["proof"]
    # Exact, not a floor: the source is pinned to an immutable commit SHA, so
    # this number is reproducible and a change in it means a real change in
    # what the parser recovers.
    assert kinds[DEFINITION_KIND] == 199, kinds[DEFINITION_KIND]

    summary = f"judson: {len(judson)} blocks {dict(kinds.most_common(5))}"
    if LEVIN_SRC.is_dir():
        sets_blocks = list(iter_blocks(LEVIN_SRC / "sec_intro-sets.ptx"))
        set_defs = [b for b in sets_blocks
                    if b.kind == DEFINITION_KIND and "set" in b.terms]
        assert set_defs, "no term-definition recovered for 'set' from Levin"
        assert "unordered collection" in " ".join(b.text for b in set_defs)
        levin = list(iter_book(LEVIN_SRC, LEVIN_GLOB))
        summary += f" | levin: {len(levin)} blocks"

    print(f"OK: {summary}")
    print("     zero author-tagged <definition> in either source; definitions "
          "recovered from <term>-bearing prose instead")


if __name__ == "__main__":
    _self_check()
