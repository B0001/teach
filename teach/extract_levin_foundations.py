"""Generate teach/data/levin_dmoi_foundations.json from the pinned Levin source.

Selection is by (file, subsection) or by term, in document order, excluding
<example> blocks -- they illustrate rather than define.
illustrations, and examples bloat a node's text without defining anything.
Term-only selection is used where a subsection mixes topics.

Every node records the exact (source_file, xml_id, kind) blocks its text came
from plus the file's sha256, so the extract is re-derivable and checkable with
teach.pretext_parser alone.
"""
import hashlib, json, pathlib

from teach.pretext_parser import LEVIN_SRC, DEFINITION_KIND, PROSE_KIND, iter_blocks

DEF_KINDS = (DEFINITION_KIND, "assemblage")

# id, label, [(file, subsections|None, terms|None, include_prose)]
SPECS = [
 ("sets", "Sets", [
   ("sec_intro-sets.ptx", None, ["set","natural numbers","set builder notation","cardinality"], False)]),
 ("set-operations", "Set Operations", [
   ("sec_intro-sets.ptx", None, ["empty set","universe set","power set","union","intersection",
                                 "complement","set difference","Cartesian product"], False)]),
 ("statements", "Statements and Logical Connectives", [
   ("sec_intro-statements.ptx", None, ["statement","atomic","molecular","logical connectives",
     "binary connectives","unary connective","truth value","propositional variables","inclusive or"], False)]),
 ("predicates-and-quantifiers", "Predicates and Quantifiers", [
   ("sec_intro-statements.ptx", None, ["free variable","predicate"], False),
   ("sec_logic-prop.ptx", ["Beyond Propositions"], None, False)]),
 ("propositional-logic", "Propositional Logic", [
   ("sec_logic-prop.ptx", [None, "Truth Tables", "Logical Equivalence"], None, False)]),
 ("deduction-rules", "Rules of Deduction", [
   ("sec_logic-prop.ptx", ["Deductions"], None, True)]),
 ("functions", "Functions", [
   ("sec_intro-functions.ptx", None, ["function","domain","codomain","range","image"], False)]),
 ("function-properties", "Injective, Surjective and Bijective Functions", [
   ("sec_intro-functions.ptx", None, ["onto","surjection","surjective","one-to-one","injection",
                                      "injective","bijection","bijective"], False)]),
 ("direct-proof", "Direct Proof", [
   ("sec_logic-proofs.ptx", ["Direct Proof"], None, True)]),
 ("proof-by-contrapositive", "Proof by Contrapositive", [
   ("sec_logic-proofs.ptx", ["Proof by Contrapositive"], None, True)]),
 ("proof-by-contradiction", "Proof by Contradiction", [
   ("sec_logic-proofs.ptx", ["Proof by Contradiction"], None, True)]),
 ("mathematical-induction", "Mathematical Induction", [
   ("sec_seq-induction.ptx", ["Stamps", "Formalizing Proofs", "Strong Induction"], None, False)]),
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def harvest(fname, subsections, terms, include_prose):
    """Matching blocks in document order. <example> blocks are excluded (they
    illustrate, they do not define) but do NOT terminate collection: Levin
    interleaves definitions and examples throughout a section, so stopping at
    the first example cost `statements` five of its six blocks and dropped the
    definition of a tautology, which follows an example."""
    kinds = DEF_KINDS + ((PROSE_KIND,) if include_prose else ())
    out = []
    for b in iter_blocks(LEVIN_SRC / fname, include_prose=include_prose):
        if subsections is not None and b.subsection_title not in subsections:
            continue
        if b.kind not in kinds:
            continue
        if terms is not None and not any(t in b.terms for t in terms):
            continue
        # No length filter on prose. A "short prose is filler" rule looks
        # reasonable and silently deleted the most important sentence in the
        # direct-proof node -- Levin states the proof skeleton "Assume P.
        # Explain, explain, ..., explain. Therefore Q." in a 57-character
        # blockquote, leaving the node ending on "The general format to prove
        # P => Q is this:" and never saying what the format is. It did not
        # even remove the trailing "Here are a few examples..." filler it was
        # aimed at, which is over the threshold.
        out.append(b)
    return out

nodes = []
for suffix, label, sources in SPECS:
    texts, prov, terms = [], [], []
    for fname, subs, tf, prose in sources:
        for b in harvest(fname, subs, tf, prose):
            texts.append(b.text)
            prov.append({"source_file": fname, "xml_id": b.xml_id, "kind": b.kind,
                         "section_title": b.section_title,
                         "subsection_title": b.subsection_title,
                         "file_sha256": sha(LEVIN_SRC / fname)})
            terms.extend(t for t in b.terms if t not in terms)
    if not texts:
        raise SystemExit(f"NO BLOCKS for {suffix}")
    nodes.append({
        "id": f"levin-dmoi:{suffix}",
        "label": label,
        "standard_ref": (f'Levin, Discrete Mathematics: An Open Introduction, 3rd ed., '
                         f'sec. "{prov[0]["section_title"]}"'),
        "terms": terms,
        "definition": " ".join(texts),
        "provenance": prov,
    })

data = {
 "schema": "levin-dmoi-foundations-v1",
 "source": {
   "provider": "Oscar Levin, Discrete Mathematics: An Open Introduction, 3rd edition",
   "author": "Oscar Levin",
   "license": "https://creativecommons.org/licenses/by-sa/4.0/",
   "attribution": (
     "Discrete Mathematics: An Open Introduction, 3rd edition, by Oscar Levin, "
     "licensed under the Creative Commons Attribution-ShareAlike 4.0 International "
     "License (https://creativecommons.org/licenses/by-sa/4.0/). Source: "
     "https://github.com/oscarlevin/discrete-book at tag 3rd-ed, commit "
     "a8e4949bc45daf100930c1182983778f56ab689f."),
   "retrieved_via": ("https://codeload.github.com/oscarlevin/discrete-book/tar.gz/"
                     "a8e4949bc45daf100930c1182983778f56ab689f (ptx/*.ptx PreTeXt source; "
                     "LICENSE for the notice above)"),
   "commit": "a8e4949bc45daf100930c1182983778f56ab689f",
   "git_tag": "3rd-ed",
   "license_note": (
     "CC BY-SA 4.0 applies to the 3rd edition, which is what this commit is. The "
     "repository's master branch is the 4th edition and is CC BY-NC-SA 4.0 -- the "
     "pinned commit is what makes this publishable, not the repository."),
   "extracted_by": "teach/extract_levin_foundations.py, via teach.pretext_parser. Re-derive with: uv run python -m teach.extract_levin_foundations",
 },
 "nodes": nodes,
}
out = pathlib.Path(__file__).parent / "data" / "levin_dmoi_foundations.json"
out.write_text(json.dumps(data, indent=2) + "\n")
print("wrote", out.name, out.stat().st_size, "bytes,", len(nodes), "nodes")
for n in nodes:
    print(f"  {n['id']:42s} {len(n['provenance'])}blk {len(n['definition']):5d}ch  {n['terms'][:6]}")
