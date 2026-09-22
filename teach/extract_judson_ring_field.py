"""Generate teach/data/judson_ring_field.json from the pinned Judson source.

teach-b5k.1 asks for group, ring AND field theory entities.
`teach.judson_algebra_graph` already carries the group-theory half as
hand-authored nodes (teach-8xw.56); this extractor adds the ring and field
half, read out of the PreTeXt source with `teach.pretext_parser` rather than
retyped.

Chapter and section numbers are not recalled -- they are read off the source.
`src/aata.xml`'s include order gives the chapter numbers (sets=1, integers=2,
groups=3, ..., rings=16, poly=17, domains=18, boolean=19, vect=20, fields=21,
finite=22, galois=23), which is consistent with the numbering the existing
hand-authored nodes already use (isomorph=9, normal=10, homomorph=11). Section
numbers are the order of `<section>` elements within each chapter file.

Re-derive with: uv run python -m teach.extract_judson_ring_field

EXTRA_STATEMENT_IDS (teach-59u): a section's only `<term>`-bearing paragraph
is sometimes a bare cross-reference to a theorem or lemma stated elsewhere in
the same section, rather than a self-contained definition -- "Fields of
Fractions" is exactly this: its one term-definition paragraph is "The field
$F_D$ in [xref to domains-lemma-field-of-fractions] is called the field of
fractions ... of the integral domain $D$", which names the term but states
none of what $F_D$ actually is. `iter_blocks` already recovers the lemma and
theorem statements that spell that out (`domains-lemma-field-of-fractions`:
what $F_D$ is, as equivalence classes with defined operations, and is a
field; `domains-theorem-field-of-quotients`: $D$ embeds in $F_D$, and $F_D$
is the smallest/unique such field) -- they were just never selected, because
this extractor only ever pulled `DEFINITION_KIND` blocks. `EXTRA_STATEMENT_IDS`
names theorem-like blocks (by `xml:id`, so a later source edit that moves or
retitles a section can't silently swap in the wrong one) whose `<statement>`
text is appended to the node's definition -- proofs are left out, same as
term-definition paragraphs never included proof text, because a block's
*statement* is what defines the term; its *proof* is how you'd verify that
definition holds; the vocabulary that identifies which concept a lesson is
about lives in the former; measured before/after in this bead's handoff.
This resolves the specific measured recall gap (judson:18.1's distinctive
vocabulary was 3 words: "fractions", "integral", "quotients" -- the smallest
node in the graph, unable to compete with any larger sibling on a lesson that
did not use its own extracted words verbatim) without touching any other
node's already-working extraction.

EXTRA_STATEMENT_IDS, second use (teach-911): judson:16.1-rings's own
DEFINITION_KIND block states the ring axioms as bare equations
("$(ab)c = a(bc)$", "$a(b+c) = ab+ac$ ...") and never uses the word
"associative", so a natural-language lesson that says multiplication "is
associative" scores no credit for that axiom at all -- confirmed against the
source: "associative" does not appear anywhere in rings.xml's "Rings"
section (rings-section-definitions), only later, in a different section
(Ring Homomorphisms and Ideals) and in an exercise, neither of which belongs
to this node. That is a genuine content gap, not fixable by folding in
existing Judson prose the way judson:18.1's fix was. What IS fixable the
same way: the node's extracted text is the formal axiom list alone, missing
every one of the "Rings" section's own worked examples -- the natural-
language register a lesson would actually talk in. `rings-example-matrix`
is not an arbitrary pick among those: it is the example Judson places
immediately after stating the distributive axiom specifically to justify why
BOTH distributive laws are required in the definition already extracted
("This last condition, the distributive axiom, relates the binary
operations...") -- 2x2 matrices, the standard noncommutative-ring example,
where $AB \neq BA$ in general. Folding it in completes an axiom the node's
definition already asserts but does not illustrate, the same "complete an
under-elaborated definition already present" logic as judson:18.1's fix, not
new content unrelated to what was already there. Measured before/after
against a fresh natural-language dialogue about rings (this bead's
handoff): raw score 12 -> 19, and the two new words this adds that no other
node in the graph's vocabulary contains ("matrices", "matrix", "entries",
"usual", "usually" are all unique to this node; "noncommutative" also
appears in judson:16.4, document-frequency 2, still well under
`_MAX_DOCUMENT_FREQ`) resolve the decisive-margin coverage-gap veto's
mistaken abstention without touching any other node's extraction.

EXCERPT_EDITS (teach-scx): teach-911's own fold-in measurably raised
judson:16.1-rings's raw score against two OTHER, unrelated lessons
(SUBGROUPS, EXTENSION_FIELDS -- round3/round4) enough to turn their
previously-clean correct recoveries into safe-but-regressed abstentions.
concept_recovery.py's `_DISCOURSE_STOPWORDS` comment traces this to one
specific word: "form" (from "matrices... form a ring under the usual
operations..."), and explains why it cannot be filtered globally --
"form" is load-bearing for a DIFFERENT node's (judson:18.2's) own
vocabulary denominator, and removing it there flips a maximal/prime-ideals
lesson from a safe abstention into a confident wrong answer (measured).
That comment names the fix this needed: "a curated partial extraction of
the matrix example (dropping 'form' specifically)". `EXCERPT_EDITS` is
that extraction, scoped to exactly the one `(node_id, xml_id)` pair that
needs it: it elides the single word "form" from `rings-example-matrix`'s
text, marks the elision with an ellipsis (the same thing an ellipsis does
in any other verbatim quotation -- every surviving word is still Judson's
own, in order; nothing is reworded or invented), and requires the exact
surrounding text to still be present before cutting, so a future source
edit that changes this sentence fails loudly here instead of silently
cutting the wrong thing or nothing at all. Every other word teach-911
added ("matrices", "matrix", "entries", "noncommutative") is untouched.
Re-measured after the cut: judson:16.1-rings's score against SUBGROUPS
drops back from 14 to 13 (margin over subgroups' 12 narrows from 2 back to
1, below `_MIN_MARGIN`, which hands resolution to the coverage tiebreak
that already correctly favors subgroups at 100% coverage -- see
concept_recovery.py's `_resolve_candidates`); against EXTENSION_FIELDS,
rings drops from 8 back to 7, restoring the margin over runner-up to 3
(decisive, and no credible rival then out-covers extension-fields enough
to trip the decisive-margin veto). Both match the pre-teach-911 numbers
exactly -- this is not a new calibration, it is undoing exactly the one
side effect teach-911 itself already identified and named as unresolved.
"""
import hashlib
import json
import pathlib

from teach.pretext_parser import (
    DEFINITION_KIND,
    JUDSON_SRC,
    TAGGED_BLOCK_KINDS,
    iter_blocks,
)

# (node id, label, chapter number, source file, section title, extra xml:ids)
# Section titles are matched exactly against the parsed <section><title>.
# `extra_statement_ids` (last element) is normally empty -- see
# EXTRA_STATEMENT_IDS above for the one case it isn't.
SPECS = [
    ("judson:16.1-rings", "Rings", 16, "rings.xml", "Rings",
     ("rings-example-matrix",)),
    ("judson:16.2-integral-domains-and-fields", "Integral Domains and Fields",
     16, "rings.xml", "Integral Domains and Fields", ()),
    ("judson:16.3-ring-homomorphisms-and-ideals", "Ring Homomorphisms and Ideals",
     16, "rings.xml", "Ring Homomorphisms and Ideals", ()),
    ("judson:16.4-maximal-and-prime-ideals", "Maximal and Prime Ideals",
     16, "rings.xml", "Maximal and Prime Ideals", ()),
    ("judson:17.1-polynomial-rings", "Polynomial Rings",
     17, "poly.xml", "Polynomial Rings", ()),
    ("judson:18.1-fields-of-fractions", "Fields of Fractions",
     18, "domains.xml", "Fields of Fractions",
     ("domains-lemma-field-of-fractions", "domains-theorem-field-of-quotients")),
    ("judson:18.2-factorization-in-integral-domains",
     "Factorization in Integral Domains",
     18, "domains.xml", "Factorization in Integral Domains", ()),
    ("judson:21.1-extension-fields", "Extension Fields",
     21, "fields.xml", "Extension Fields", ()),
    ("judson:21.2-splitting-fields", "Splitting Fields",
     21, "fields.xml", "Splitting Fields", ()),
]

# The Sage sections are code, not exposition, and every chapter has one. They
# are never selected because no spec names them, but the guard is explicit so
# a future spec cannot pull one in by accident.
EXCLUDED_SECTIONS = ("Sage",)

# (node id, xml:id) -> ((exact substring to find, its replacement), ...),
# applied only to that one EXTRA_STATEMENT_IDS block's text. See
# EXCERPT_EDITS in the module docstring above (teach-scx). Each `find` must
# match exactly once in the block's raw text or `build()` raises loudly --
# this is a targeted elision, not a rewrite, and a future source edit that
# moves or rewords the sentence must not silently cut the wrong thing.
EXCERPT_EDITS = {
    ("judson:16.1-rings", "rings-example-matrix"): (
        ("\\mathbb R}$ form a ring under", "\\mathbb R}$ … a ring under"),
    ),
}


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _excerpted_text(node_id: str, block) -> str:
    """`block.text`, with any `EXCERPT_EDITS` entry for `(node_id,
    block.xml_id)` applied. Raises loudly if a `find` substring is not
    present exactly once -- see EXCERPT_EDITS."""
    text = block.text
    for find, replace in EXCERPT_EDITS.get((node_id, block.xml_id), ()):
        count = text.count(find)
        if count != 1:
            raise SystemExit(
                f"EXCERPT_EDITS: {find!r} found {count} time(s) (need "
                f"exactly 1) in {block.xml_id!r} ({node_id}) -- source text "
                f"changed, re-check this cut"
            )
        text = text.replace(find, replace, 1)
    return text


def build() -> dict:
    nodes = []
    for node_id, label, chapter, fname, section, extra_statement_ids in SPECS:
        assert section not in EXCLUDED_SECTIONS, section
        all_blocks = list(iter_blocks(JUDSON_SRC / fname))
        blocks = [
            b for b in all_blocks
            if b.kind == DEFINITION_KIND and b.section_title == section and b.terms
        ]
        if not blocks:
            raise SystemExit(f"NO BLOCKS for {node_id} ({section} in {fname})")

        # teach-59u: fold in the theorem/lemma statements named by this
        # spec's extra_statement_ids -- see EXTRA_STATEMENT_IDS in the module
        # docstring. Looked up by xml:id among TAGGED_BLOCK_KINDS blocks only
        # (never DEFINITION_KIND, which blocks above already cover), so a
        # typo'd or moved id fails loudly instead of silently matching
        # nothing.
        extra_blocks = []
        for xml_id in extra_statement_ids:
            matches = [
                b for b in all_blocks
                if b.xml_id == xml_id and b.kind in TAGGED_BLOCK_KINDS
            ]
            if not matches:
                raise SystemExit(
                    f"NO BLOCK for extra_statement_id {xml_id!r} ({node_id})"
                )
            extra_blocks.extend(matches)

        terms: list[str] = []
        for b in blocks + extra_blocks:
            terms.extend(t for t in b.terms if t not in terms)

        nodes.append({
            "id": node_id,
            "label": label,
            "chapter": chapter,
            "section": section,
            "standard_ref": (
                f'Judson, Abstract Algebra: Theory and Applications, '
                f'ch. "{blocks[0].chapter_title}", sec. "{section}"'
            ),
            "terms": terms,
            "definition": " ".join(
                _excerpted_text(node_id, b) for b in blocks + extra_blocks
            ),
            "provenance": [
                {"source_file": fname, "xml_id": b.xml_id, "kind": b.kind,
                 "section_title": b.section_title,
                 "file_sha256": _sha256(JUDSON_SRC / fname),
                 **({"excerpted": True} if (node_id, b.xml_id) in EXCERPT_EDITS else {})}
                for b in blocks + extra_blocks
            ],
        })

    return {
        "schema": "judson-ring-field-v1",
        "source": {
            "provider": "Thomas W. Judson and Robert A. Beezer, "
                        "Abstract Algebra: Theory and Applications",
            "author": "Thomas W. Judson, Robert A. Beezer",
            "license": "https://www.gnu.org/licenses/fdl-1.3.html",
            "commit": "3069910e3ded72ff5e18837a97a0e810c92790e2",
            "retrieved_via": "https://codeload.github.com/twjudson/aata/tar.gz/"
                             "3069910e3ded72ff5e18837a97a0e810c92790e2 "
                             "(src/*.xml PreTeXt source; COPYING for the notice)",
            "extracted_by": "teach/extract_judson_ring_field.py, via "
                            "teach.pretext_parser. Re-derive with: "
                            "uv run python -m teach.extract_judson_ring_field",
            "license_note": (
                "GFDL 1.3+ is copyleft and is NOT the same license as the "
                "foundational half (Levin, CC BY-SA 4.0). The two do not merge; "
                "each node carries its own terms. The verbatim COPYING notice "
                "lives in teach.judson_algebra_graph.JUDSON_SOURCE."
            ),
        },
        "nodes": nodes,
    }


def main() -> None:
    data = build()
    out = pathlib.Path(__file__).parent / "data" / "judson_ring_field.json"
    out.write_text(json.dumps(data, indent=2) + "\n")
    print(f"wrote {out.name} {out.stat().st_size} bytes, {len(data['nodes'])} nodes")
    for n in data["nodes"]:
        print(f"  {n['id']:46s} {len(n['provenance'])}blk {len(n['definition']):5d}ch "
              f"{n['terms'][:4]}")


if __name__ == "__main__":
    main()
