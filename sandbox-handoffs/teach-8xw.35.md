# teach-8xw.35 handoff

## What this bead was

The epic and `sandbox-prompt.md` both claim "motivation is guided by
Cialdini's Influence and Pre-Suasion" and name it the highest-risk mechanism
in the whole system. `teach-8xw.31` built `teach/cialdini.py` (the seven
principles, each a real render function) and
`teach/cialdini_integration_check.py` (ran a hand-built demo transcript
through the real checkers). Both closed clean. But `teach.cialdini` was
imported by exactly one module: its own integration check. The actual
end-to-end lesson pipeline — `teach/dnf_bond_lesson.py`, what `teach-8xw.15`'s
acceptance test (`tests/test_dnf_bond_integration.py`) runs — never imported
it. So the epic's flagship "teach Dummit & Foote to a learner interested in
James Bond" test case shipped with zero persuasion content, and the only
Cialdini text a checker had ever seen was a self-authored demo, not the real
artifact.

## What I did

Reproduced the gap first, exactly as described in the bead: confirmed via
grep that `teach/dnf_bond_lesson.py` imported none of `cbt_primitives`'
siblings from `cialdini.py`, and that `teach.cialdini` had exactly one
importer before this change.

Wired all seven `teach.cialdini` moves into `teach/dnf_bond_lesson.py`'s
`build_planner_state()` — the function that builds the real traversal-driven
lesson `teach-8xw.15`'s acceptance test actually runs. Each move:

- calls the **unmodified** `render_*` function from `teach.cialdini` (no new
  template logic — reuse, not reimplementation, so the honesty properties
  that module's docstring argues for carry over rather than being
  reinvented)
- is fed a `MotivationMoment` built from **this lesson's own real content**
  (the learner's actual prior turn, the textbook section just narrated, the
  real next node in the traversal) — not `cialdini.FAKE_CONTEXTS` and not a
  copy of `cialdini_integration_check.py`'s demo moment
- is wrapped in `_bond_voice()`, the same re-voicing wrapper already used for
  the CBT primitives, so persuasion and CBT turns read in one consistent
  persona voice

Placement (all 7 fire once, at points that make sense in the narrative):

| Principle | Where | What it's tied to |
|---|---|---|
| LIKING | right after the intro, before any content | the Bond frame itself — the actual reason this lesson exists in this framing |
| RECIPROCITY | before the behavioral-activation "write this down" ask | the sets/functions narration that was just given |
| COMMITMENT_CONSISTENCY | right after the learner's own bijective answer | points back at that exact answer before moving to groups |
| AUTHORITY | after the subgroups narration | cites Dummit & Foote §2.1 for the subgroup criterion (a fact NOT in `teach.math_facts.MATH_SOURCE`, so it's inert to `fact_checker`, not a collision risk) |
| SOCIAL_PROOF | right after the learner's "not sure I'm cut out for this" line | normalizes the struggle just voiced |
| UNITY | right after `identify_stuck_belief`, same moment | reframes the next step as shared work |
| SCARCITY | after the cosets narration | flags the "every conjugate, not just one g" detail |

`build_lesson()` and the checker-side `teach/dnf_bond_integration.py` needed
no changes to their *shape* — `run_integration_check` already took only a
`LessonArtifact` and ran the three real blind checkers on `.text`. What
changed is what's actually in that text now.

Extended `dnf_bond_lesson.py`'s self-check to positively prove the wiring:
it re-renders each of the seven `MotivationMoment`s from the exact fields
used in `build_planner_state()` and asserts the resulting string is
literally present in `artifact.text` — so a future edit that silently drops
a call site (not just a deleted import) fails loud here, not just via a
"boundary" or "label present" check that wouldn't notice content missing.

## What the real checker run measured (not asserted — measured)

Ran the wired lesson through `teach.concept_recovery`,
`teach.fact_checker`, and `teach.potential_checker` — the same three real,
unmodified checkers `teach-8xw.15` already used, now against a 21-turn
artifact that actually contains all seven persuasion moves interleaved with
domain content:

- **concept_recovery**: unchanged — `taught_node_id` still recovered
  correctly, `assumed_prerequisite_ids == ("dummit-foote:3.1-cosets",)`,
  `unsignposted_prerequisite_ids == ()`. The Cialdini commitment_consistency
  template's own "You already said..." phrasing is an assumed-known trigger
  pattern, but it fires on Sets-and-Functions content, which is not a direct
  prerequisite edge of the target node in the graph, so it does not spuriously
  add a false assumed-prerequisite. Verified by running the actual recovery,
  not inferred.
- **fact_checker**: unchanged from before this bead — one CONFIRMED
  Lagrange verdict, zero CONTRADICTED, `kernel-normal-subgroup` still
  disclosed out-of-scope. The AUTHORITY move's subgroup-criterion fact isn't
  in `MATH_SOURCE` at all, so it's CANNOT_VERIFY by construction (not
  extracted as a domain claim), not a new risk surface.
- **potential_checker**: `potential_flags == ()` — still clean. But
  `classified` moved from **1 to 2**: the COMMITMENT_CONSISTENCY move's
  rendered text ("if you keep working that way, you'll be ready to tackle
  the group axioms next -- the same kind of move you just handled a moment
  ago") independently satisfies `_claim_type` (GROWTH), effort-conditioning,
  and `_evidenced_ceiling` (the template's own "you just handled" +
  "next" wording trips the `_JUST_DID_PATTERN` / `_ORDINARY_NEXT_STEP_PATTERN`
  evidence rule) — so it lands HONEST, same as the pre-existing closing
  line. This is a genuinely new, measured result: adding a second real
  Cialdini-generated potential claim to the actual pipeline still classifies
  HONEST under the real rubric, not just in `cialdini_integration_check.py`'s
  isolated demo. `seen`/`unclassified` grew (51/49, up from ~32/31) because
  there are more tutor turns now — per `teach-8xw.21`'s established
  precedent, that raw count is lesson-length noise and isn't pinned; only
  `classified` (a real signal) is pinned, updated 1 → 2.
- Updated the two places that asserted the old `classified == 1` invariant
  (`teach/dnf_bond_integration.py`'s self-check and
  `tests/test_dnf_bond_integration.py::test_potential_checker_coverage_gap_is_disclosed_not_hidden`)
  to `== 2`, with comments explaining why, per sandbox-prompt.md's "fix the
  code or fix the document, never a third" rule — the old pinned number was
  a real measurement that changed for a real reason, not something to round
  away or silently leave stale.

## Re-ran `teach-8xw.15`'s acceptance test end-to-end

`uv run pytest tests/test_dnf_bond_integration.py -v` → 6/6 pass, with the
wired-in version. Full suite: `uv run pytest -q` → 265 passed. Every
module's own `python3 -m <module>` self-check also passes:
`teach.cialdini`, `teach.cialdini_integration_check`, `teach.dnf_bond_lesson`,
`teach.dnf_bond_integration`, `teach.boundary`, `teach.dummit_foote_graph`.

## What this does NOT establish

Same caveat this repo's Cialdini lineage already states and I am not
rounding away: the seven `render_*` functions themselves are unchanged from
`teach-8xw.31`/`.32` (already measured against their own fake contexts and a
self-authored demo). What's newly measured here is that wiring them into a
*different*, real, traversal-driven lesson with different fill content still
produces a clean run under the same unmodified checkers — not that the
templates generalize to phrasing nobody here wrote. That generalization
question is still open and out of this bead's scope; it would need an
independently-authored round the way `teach-8xw.25`'s Lagrange work did.

Also unchanged, and still worth naming: this run only exercises the
Lagrange/cosets branch of the D&F graph (`kernel-normal-subgroup` stays
out-of-scope, same disclosed gap as before this bead), and
`potential_checker`'s `evidenced_ceiling` can still only check a claim
against evidence present in this same lesson's text, same standing
limitation flagged in `sandbox-handoffs/teach-8xw.8.md`.

## Files changed

- `teach/dnf_bond_lesson.py` — the actual wiring: 7 new turns calling
  `teach.cialdini`'s render functions with real `MotivationMoment`s, plus a
  self-check extension proving each rendered string is in the final text.
- `teach/dnf_bond_integration.py` — updated the `classified == 1` self-check
  assertion to `== 2` with an explanatory comment.
- `tests/test_dnf_bond_integration.py` — same assertion update, plus a
  docstring note explaining why.

Left untouched, not part of this bead's scope (pre-existing uncommitted work
from another session found at claim time — `teach/math_facts.py`,
`tests/test_fact_checker.py`, see `sandbox-handoffs/teach-8xw.33.md`): did
not touch, did not commit.

## Status

Closing as done. All three acceptance-criteria items from the bead
description are satisfied: (1) `teach.cialdini`'s moves are wired into
`teach/dnf_bond_lesson.py`'s real traversal rendering, producing one real
`LessonArtifact`; (2) that real artifact was run through
`fact_checker.check_lesson_text` and `potential_checker.check_lesson_text`
with the actual flags/coverage reported above, no special-casing; (3)
`teach-8xw.15`'s acceptance test was re-run end-to-end with the wired-in
version and passes clean, with the one real, disclosed change (classified
1 → 2) reported rather than hidden.
