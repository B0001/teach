# teach-25o — Extend D&F chain past Lagrange (homomorphisms, isomorphism theorems)

## Bottom line

Added two nodes to `teach/dummit_foote_graph.py` past the existing Lagrange
target — `1.6-homomorphisms` (D&F §1.6, homomorphisms/isomorphisms/kernel)
and `3.3-isomorphism-theorems` (§3.3, First Isomorphism Theorem) — and moved
the `kernel-normal-subgroup` `fact_topics` tag from `3.1-cosets` (where it
was wrong: cosets' own definition never mentions homomorphisms or kernels)
to `3.3-isomorphism-theorems` (where the content actually matches). Graph is
now 11 nodes / 13 edges, still a validated DAG, same strict edge rule as
before (content-dependency only, not chapter order).

The `teach.math_facts` `kernel-normal-subgroup` `SourceFact` (D&F §3.2 Prop 7)
is now reachable from a traversal — it wasn't before this bead, because no
node in the graph carried the concept of a homomorphism/kernel at all.

`uv run pytest -q`: **142 passed** (140 pre-existing + 2 new). One
pre-existing test's fixture text had to change (see "Collateral effect on an
existing test" below) — no test was weakened, only its wording.

## What I added and why

- `dummit-foote:1.6-homomorphisms` — homomorphism, isomorphism, kernel.
  Edges in: `0.1-sets-and-functions` (isomorphism's definition needs
  "bijection") and `1.1-groups` (homomorphism's definition needs "group").
  Nothing else — the node's own definition never mentions subgroups, so no
  edge from `2.1-subgroups`.
- `dummit-foote:3.3-isomorphism-theorems` — First Isomorphism Theorem,
  `G/ker(phi) ≅ im(phi)`, kernel normal in `G`. Edges in: `1.6-homomorphisms`
  (needs kernel/homomorphism/isomorphic) and `3.1-cosets` (needs "quotient
  group", which is `3.1`'s term, not `1.6`'s). Carries
  `fact_topics=("kernel-normal-subgroup",)`.
- Removed `fact_topics=("kernel-normal-subgroup",)` from `3.1-cosets`. That
  placement predates this bead and was wrong on inspection: `3.1`'s own
  definition text is entirely about cosets/normal-subgroup-by-conjugation
  and never uses "homomorphism" or "kernel" — the fact it was tagged with
  needs both concepts, and until this bead the graph had no way to state
  "kernel" at all. Confirmed via the module docstring's own dependency rule:
  a node can only carry a fact whose content it can actually state.
- Two new `NON_EDGES`, following the existing pattern (see `2.3 -> TARGET`
  for precedent): `1.6 -> 2.1` (chapter order tempts it; subgroup criterion
  needs no map between groups) and `3.2(TARGET) -> 3.3` (3.2 immediately
  precedes 3.3 in the book and some courses use Lagrange for isomorphism-
  theorem corollaries, but the First Isomorphism Theorem's own statement
  doesn't use "|H| divides |G|"). Both documented in the module docstring's
  "EDGES DELIBERATELY NOT ASSERTED" table and asserted absent by both the
  self-check and the existing parametrized `test_chapter_order_edges_stay_unasserted`.
- `TARGET_NODE_ID` unchanged (`3.2-lagrange-theorem`) — teach-8xw.15's
  acceptance test targets it; the new nodes hang off the side, downstream of
  `1.6`/`3.1` but not of `3.2`.

## Collateral effect on an existing test (in-scope, not a new bead)

`tests/test_dummit_foote_graph.py::test_signposted_prerequisites_are_recovered`
started failing after adding `3.3` — not because of a bug, but because it
was riding right at `concept_recovery.py`'s document-frequency boilerplate
cutoff (`_MAX_DOCUMENT_FREQ = 4`). The word "subgroup" already appeared in 4
of the (then) 9 nodes' vocabulary (`2.1`, `2.3`, `3.1`, `3.2`) — exactly at
the cutoff, so still "distinctive" by a hair. `3.3`'s
`fact_topics=("kernel-normal-subgroup",)` string itself tokenizes to
`kernel`, `normal`, `subgroup` (the recovery module's `_flatten_strings`
walks every string reachable in a node's `facts`, including `fact_topics`),
pushing the count to 5 and correctly demoting "subgroup" to boilerplate
within this graph — it now really does span more than half the graph's
content (subgroups, cyclic groups, cosets, Lagrange, isomorphism theorems),
so no longer discriminates which one a lesson is about.

The failing test's `SIGNPOSTED_LESSON` fixture had been relying on that one
shared word to signal recall of `3.1-cosets` specifically, even though the
"recall" sentence was actually restating `2.1`'s subgroup definition, not
anything coset-specific. I reworded the fixture's recall sentence to
actually invoke coset vocabulary ("left coset gH is the set of products gh
... these cosets partition the group into equal blocks") instead of
subgroup vocabulary, which is a more honest test of the behavior it claims
to check (recall of the coset prerequisite, not an accidental word overlap
with a different node). Reran the full suite after the change — passes
clean, no other test touched this vocabulary boundary.

I did not touch `teach/concept_recovery.py` or its thresholds — that engine
belongs to a different, already-closed bead (teach-8xw.10), and the shift in
document frequency here is a real, correct consequence of adding legitimate
new content to this graph, not a bug in that module.

Also worth flagging for whoever next edits `math_facts.py` or this graph:
`fact_topics` values bleed into recovery vocabulary as ordinary words
(hyphens split on the same regex as spaces) since `_flatten_strings` doesn't
special-case that key. That's mildly surprising but out of scope to change
here — noting it rather than silently working around it.

## New tests

- `test_isomorphism_theorems_closure_excludes_lagrange` — `3.3`'s
  prerequisite closure is exactly `{1.6, 3.1, 2.1, 1.1, 0.1}`, and does not
  include `TARGET_NODE_ID` (Lagrange) despite the two being adjacent in the
  book.
- `test_kernel_normal_subgroup_fact_is_reachable` — exactly one node
  (`3.3-isomorphism-theorems`) carries the `kernel-normal-subgroup` fact
  topic. This is the bead's actual acceptance criterion made mechanical:
  before this bead, zero nodes could have asserted this because `3.3`/`1.6`
  didn't exist.

`_self_check()` in `dummit_foote_graph.py` also extended: node/edge counts
(11/13), topological ordering of the four new edges, the `3.3` closure, both
new `NON_EDGES` staying absent, and the reachability assertions above.

## Verification

```
uv run python -m teach.dummit_foote_graph   # self-check: "11 nodes, 13 edges"
uv run pytest -q                            # 142 passed
```

## Files touched

- `teach/dummit_foote_graph.py` — two new nodes, four new edges, two new
  `NON_EDGES`, moved `fact_topics`, extended docstring and `_self_check`.
- `tests/test_dummit_foote_graph.py` — reworded `SIGNPOSTED_LESSON`, added
  two new tests.
- `sandbox-handoffs/teach-25o.md` (this file).

Not touched: `teach/math_facts.py` (the `SourceFact` itself needed no
change — only a graph node to attach to), `teach/concept_recovery.py` (see
above).

Nothing committed — conservative git policy, bead did not say to commit.
There is unrelated pre-existing uncommitted work in the tree from a prior
session (`teach-20c`'s changes to `teach/concept_recovery.py` and
`tests/test_concept_recovery.py`, plus its own handoff file) — present
before this session started, not touched or reviewed by me beyond running
the full suite, which passes with it in place.
