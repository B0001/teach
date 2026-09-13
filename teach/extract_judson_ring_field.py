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
"""
import hashlib
import json
import pathlib

from teach.pretext_parser import DEFINITION_KIND, JUDSON_SRC, iter_blocks

# (node id, label, chapter number, source file, section title)
# Section titles are matched exactly against the parsed <section><title>.
SPECS = [
    ("judson:16.1-rings", "Rings", 16, "rings.xml", "Rings"),
    ("judson:16.2-integral-domains-and-fields", "Integral Domains and Fields",
     16, "rings.xml", "Integral Domains and Fields"),
    ("judson:16.3-ring-homomorphisms-and-ideals", "Ring Homomorphisms and Ideals",
     16, "rings.xml", "Ring Homomorphisms and Ideals"),
    ("judson:16.4-maximal-and-prime-ideals", "Maximal and Prime Ideals",
     16, "rings.xml", "Maximal and Prime Ideals"),
    ("judson:17.1-polynomial-rings", "Polynomial Rings",
     17, "poly.xml", "Polynomial Rings"),
    ("judson:18.1-fields-of-fractions", "Fields of Fractions",
     18, "domains.xml", "Fields of Fractions"),
    ("judson:18.2-factorization-in-integral-domains",
     "Factorization in Integral Domains",
     18, "domains.xml", "Factorization in Integral Domains"),
    ("judson:21.1-extension-fields", "Extension Fields",
     21, "fields.xml", "Extension Fields"),
    ("judson:21.2-splitting-fields", "Splitting Fields",
     21, "fields.xml", "Splitting Fields"),
]

# The Sage sections are code, not exposition, and every chapter has one. They
# are never selected because no spec names them, but the guard is explicit so
# a future spec cannot pull one in by accident.
EXCLUDED_SECTIONS = ("Sage",)


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    nodes = []
    for node_id, label, chapter, fname, section in SPECS:
        assert section not in EXCLUDED_SECTIONS, section
        blocks = [
            b for b in iter_blocks(JUDSON_SRC / fname)
            if b.kind == DEFINITION_KIND and b.section_title == section and b.terms
        ]
        if not blocks:
            raise SystemExit(f"NO BLOCKS for {node_id} ({section} in {fname})")

        terms: list[str] = []
        for b in blocks:
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
            "definition": " ".join(b.text for b in blocks),
            "provenance": [
                {"source_file": fname, "xml_id": b.xml_id, "kind": b.kind,
                 "section_title": b.section_title,
                 "file_sha256": _sha256(JUDSON_SRC / fname)}
                for b in blocks
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
