"""Producer: the actual Dummit & Foote / James Bond lesson (teach-8xw.15).

Every producer-side piece this repo built exists in isolation until now:
`teach.persona` renders a traversal, `teach.cbt_primitives` renders a move
given a fake `LessonMoment`, `teach.honesty_rubric` classifies a claim
someone already extracted, `teach.dummit_foote_graph` is a validated graph
nobody has taught from. This module is the first thing that assembles them
into one real lesson for the epic's actual test case: "teach Dummit & Foote
to a learner whose stated interest is James Bond," ending at the graph's
`TARGET_NODE_ID` (Lagrange's Theorem).

WHAT CROSSES THE BOUNDARY AND WHAT DOESN'T

This module builds a real `teach.producer_state.PlannerState` -- target node,
traversal, answer key, the works -- and the ONLY thing `build_lesson()`
returns is the `LessonArtifact` that `teach.producer_state.emit_lesson_artifact`
produces from it. Nothing else in this module is importable by a checker;
`teach-8xw.15`'s own acceptance test (see `teach/dnf_bond_integration.py`)
enforces this the same way `test_boundary.py` does -- by typing the checker
phase to accept only `LessonArtifact`, so a checker author reaching for
`PlannerState` gets a type error, not a silent leak.

REUSE, NOT REIMPLEMENTATION

  - `teach.dummit_foote_graph.load_dummit_foote_graph` / `prerequisite_closure`
    -- the real, already-validated D&F chain. No new nodes or edges here.
  - `teach.persona.Persona` -- personality-as-data-structure, unmodified.
    `BOND_HANDLER` is one point in that trait space (calm, precise, dry),
    not a special case in the Persona type itself.
  - `teach.persona.beats()` -- the pure traversal-to-content step, reused
    exactly as-is so this module never re-derives "what does this node say"
    from the graph itself.
  - `teach.persona.Backend` protocol -- `BondNarrationBackend` below
    conforms to it (checked in this module's self-check via
    `persona.conforms`), so a future swap to a live model backend touches
    only this one class, per persona.py's own stated design intent.
  - `teach.cbt_primitives` -- the four primitives are invoked for real here
    (not against `FAKE_CONTEXTS`, against `LessonMoment`s built from this
    lesson's own content) and their output is re-voiced (wrapped, not
    replaced) into the persona's frame, exactly the division of labor
    cbt_primitives.py's docstring specifies ("the persona layer is expected
    to re-voice it, not consume it verbatim").
  - The closing encouragement line is written to satisfy
    `teach.honesty_rubric.classify` at HONEST -- effort-conditioned, and its
    claimed next step (the isomorphism theorems) is the ordinary next node
    past the target in the graph itself, not an invented reach. This is the
    bounded-Cialdini layer teach-8xw.8 specified applied to real text for
    the first time, rather than only to the module's own worked examples.
  - `teach.cialdini` -- all seven principles fire here, for real, as part of
    this traversal (teach-8xw.35; `teach.cialdini`'s own docstring named this
    module as the "future integration" that decides *when* each principle
    fires). Every `MotivationMoment` below is built from this lesson's own
    content -- the learner's actual prior turn, the actual textbook section
    just narrated, the actual next node in the traversal -- not
    `teach.cialdini.FAKE_CONTEXTS` or a hand-built demo transcript
    (`teach.cialdini_integration_check`'s `build_demo_lesson` remains a
    separate, smaller, self-contained check; this is the real artifact
    teach-8xw.15's acceptance test actually runs). Rendered, not
    re-authored: every persuasion turn below calls `teach.cialdini`'s
    unmodified `render_*` functions, so the honesty properties that
    module's own docstring argues for (bounded SOCIAL_PROOF and AUTHORITY
    shapes, in particular) carry over here rather than being reinvented.

BOND FRAMING IS FLAVOR, NOT SUBSTITUTE CONTENT

Every beat's spy narration is built to still contain the real D&F
definition in recognizable form -- so `teach.fact_checker` and
`teach.concept_recovery`, which key off the actual mathematical vocabulary
and phrasing, have something to find. A Bond-framed lesson that only used
metaphor and never stated "the order of the subgroup divides the order of
the finite group" would be exactly the failure mode sandbox-prompt.md warns
about: fluent and engaging with nothing underneath for a blind checker to
verify.
"""
from __future__ import annotations

from teach.boundary import LessonArtifact, Turn
from teach.cbt_primitives import (
    LessonMoment,
    render_behavioral_activation,
    render_graded_exposure,
    render_identify_stuck_belief,
    render_spaced_retrieval,
)
from teach.cialdini import (
    MotivationMoment,
    render_authority,
    render_commitment_consistency,
    render_liking,
    render_reciprocity,
    render_scarcity,
    render_social_proof,
    render_unity,
)
from teach.dummit_foote_graph import TARGET_NODE_ID, load_dummit_foote_graph, prerequisite_closure
from teach.persona import Backend, Persona, beats, conforms
from teach.producer_state import PlannerState, emit_lesson_artifact

# A calm, precise, dry-humored handler -- high conscientiousness (methodical,
# finishes what it starts), mild extraversion, low agreeableness (blunt,
# will contradict a wrong answer rather than smooth over it), and notably
# low neuroticism (steady under pressure) -- the register a Bond quartermaster
# briefing actually reads in, not a generic enthusiastic tutor voice.
BOND_HANDLER = Persona(
    openness=0.4,
    conscientiousness=0.8,
    extraversion=0.2,
    agreeableness=-0.3,
    neuroticism=-0.7,
)

# Hand-authored per-node Bond narration, keyed by node id (not label) so a
# later edit to a node's label can't silently detach its narration. Every
# entry is checked by this module's self-check to actually contain its
# node's label verbatim, mirroring the invariant persona.render_traversal
# already enforces for the generic TemplateBackend case.
_BOND_NARRATION: dict[str, str] = {
    "dummit-foote:0.1-sets-and-functions": (
        "MI6 keeps a roster of assets and a separate roster of handlers. "
        "Sets and Functions is the discipline of assigning each asset to "
        "exactly one handler: that assignment is a function from the "
        "domain of assets to the codomain of handlers. When no two assets "
        "share a handler, the assignment is injective; when every handler "
        "has at least one asset reporting to them, it's surjective; when "
        "both hold at once, it's bijective, and the whole roster is "
        "accounted for one-to-one."
    ),
    "dummit-foote:1.1-groups": (
        "Every field maneuver at Q Branch runs through one binary "
        "operation: combine any two moves and the result is a third move "
        "in the same repertoire. Binary Operations and the Group Axioms "
        "is the rulebook that makes that repertoire a group -- the "
        "operation is associative, there is an identity move that changes "
        "nothing, and every move has an inverse that undoes it exactly. "
        "When the order of combining two moves never matters, Q calls the "
        "group abelian."
    ),
    "dummit-foote:2.1-subgroups": (
        "Not every operation needs headquarters' full roster behind it. "
        "Subgroups and the Subgroup Criterion is how Bond vets whether a "
        "smaller unit, Q Branch, sitting inside the network G, can stand "
        "on its own: Q Branch is a subgroup exactly when it is a nonempty "
        "subset closed under the operation and closed under taking "
        "inverses -- a self-contained cell that never has to phone "
        "headquarters for backup."
    ),
    "dummit-foote:3.1-cosets": (
        "Cosets and Normal Subgroups is the payoff of vetting Q Branch. "
        "Pick any agent g in the network G: the left coset gH is the set "
        "of products gh for every h already in Q Branch. When every "
        "conjugate gHg-inverse folds back into Q Branch itself, MI6 calls "
        "Q Branch normal -- and that is exactly the condition that lets "
        "the cosets recombine into a single quotient group Bond can act "
        "on as one unit, instead of chasing every agent individually."
    ),
    TARGET_NODE_ID: (
        "This is Lagrange's Theorem, and the proof behind it is the whole "
        "reason the roster count was never going to be an accident: for a "
        "finite group G with subgroup H, the order of the subgroup divides the "
        "order of the finite group. The reason is exactly what Q Branch "
        "just watched happen -- the cosets partition G into blocks of "
        "equal size, no agent double-booked and none left standing "
        "outside every block, and the number of those blocks is the "
        "index. Q Branch's size was never free to be whatever it liked; "
        "it was always going to divide headquarters' full count."
    ),
}


def _bond_voice(line: str) -> str:
    """Re-voice a plain CBT-primitive line into the handler's frame. Wraps,
    does not replace -- the primitive's actual content (what teach-8xw.7's
    tests check for) survives verbatim inside the wrapper, per
    cbt_primitives.py's explicit division of labor between primitive
    content and persona styling."""
    return f'The handler doesn\'t blink. "{line}"'


class BondNarrationBackend:
    """Conforms to `teach.persona.Backend`: profile in, prompt in, text out.
    An honest, offline, deterministic stand-in for a live model call (same
    status as `persona.TemplateBackend`, just with real narrative content
    instead of an echo) -- swapping in narrator's ocean_ollama/ocean_fable
    backends later touches only this class.

    Looks up narration by node id rather than parsing it out of the
    rendered prompt string, so this class stays a thin data lookup instead
    of a second prompt-parser that could drift from `_beat_prompt`'s format.
    """

    def __init__(self, narration: dict[str, str]):
        self._narration = narration

    def __call__(self, profile, node_id: str, model: str = "bond-handler") -> str:
        return self._narration[node_id]


BOND_BACKEND: Backend = BondNarrationBackend(_BOND_NARRATION)
assert conforms(BOND_BACKEND), "BondNarrationBackend must conform to teach.persona.Backend"


def _tutor(text: str) -> Turn:
    return Turn(speaker="tutor", text=text)


def _learner(text: str) -> Turn:
    return Turn(speaker="learner", text=text)


def build_planner_state() -> PlannerState:
    """Assemble the full producer-side lesson: graph, traversal, persona,
    CBT primitives, and a bounded encouragement line, ending at Lagrange's
    Theorem. This is `PlannerState` -- the producer's own view, including
    everything `teach.boundary` forbids from crossing to a checker. Nothing
    outside this module (and `emit_lesson_artifact`) should call this.
    """
    graph = load_dummit_foote_graph()

    # The traversal taught in THIS lesson: Lagrange's prerequisite closure,
    # in a valid learning order, plus the target itself. Deliberately not
    # the whole 11-node graph -- teach-25o's 1.6/3.3 branch (added so
    # math_facts' kernel-normal-subgroup fact is reachable from *some*
    # traversal) is off this lesson's path to Lagrange, per
    # dummit_foote_graph.py's own docstring ("3.2 remains the target used by
    # teach-8xw.15's acceptance test"). Covering that second fact is a
    # different lesson, not something to fold in here just to raise a
    # coverage count -- see this module's self-check and the integration
    # report for the explicit disclosure of that scope boundary.
    closure = prerequisite_closure(graph, TARGET_NODE_ID)
    order = graph.topological_order()
    traversal = tuple(n for n in order if n in closure) + (TARGET_NODE_ID,)
    assert traversal == (
        "dummit-foote:0.1-sets-and-functions",
        "dummit-foote:1.1-groups",
        "dummit-foote:2.1-subgroups",
        "dummit-foote:3.1-cosets",
        TARGET_NODE_ID,
    ), traversal

    steps = beats(graph, traversal)
    by_id = {b.node_id: b for b in steps}

    turns: list[Turn] = [
        _tutor(
            "M's briefing is short: a network of field agents, one operation "
            "for combining their moves, and a target roster size that has to "
            "come out right by the end of this. Let's get there properly, "
            "one definition at a time."
        ),
        # LIKING: the shared frame is the actual reason this lesson is
        # Bond-framed at all -- the learner's own stated interest, not an
        # invented rapport move -- so it fires before any content, setting
        # the frame the rest of the lesson stays inside.
        _tutor(
            _bond_voice(
                render_liking(
                    MotivationMoment(
                        concept_name="Sets and Functions",
                        shared_frame="the Bond briefing",
                    )
                )
            )
        ),
        _tutor(BOND_BACKEND(BOND_HANDLER, by_id["dummit-foote:0.1-sets-and-functions"].node_id)),
        # RECIPROCITY: hand the learner the worked mapping above before
        # asking for the next small piece of effort -- the gift is the
        # narration that just ran, not a separate invented resource.
        _tutor(
            _bond_voice(
                render_reciprocity(
                    MotivationMoment(
                        concept_name="Sets and Functions",
                        given_first="the roster mapping between assets and handlers, worked through above",
                        next_ask=(
                            "write down, in your own words, what makes an "
                            "assignment from assets to handlers bijective"
                        ),
                    )
                )
            )
        ),
        _tutor(
            _bond_voice(
                render_behavioral_activation(
                    LessonMoment(
                        concept_name="Sets and Functions",
                        next_action=(
                            "write down, in your own words, what makes an "
                            "assignment from assets to handlers bijective"
                        ),
                    )
                )
            )
        ),
        _learner(
            "Bijective means every asset gets exactly one handler and every "
            "handler gets covered -- nobody's unassigned, nobody's doubled up."
        ),
        # COMMITMENT_CONSISTENCY: point back at the answer the learner just
        # gave rather than open the group axioms as a fresh, unrelated ask.
        _tutor(
            _bond_voice(
                render_commitment_consistency(
                    MotivationMoment(
                        concept_name="Sets and Functions",
                        prior_commitment=(
                            "Bijective means every asset gets exactly one "
                            "handler and every handler gets covered -- "
                            "nobody's unassigned, nobody's doubled up"
                        ),
                        consistent_next_step="the group axioms",
                    )
                )
            )
        ),
        _tutor(BOND_BACKEND(BOND_HANDLER, by_id["dummit-foote:1.1-groups"].node_id)),
        _tutor(BOND_BACKEND(BOND_HANDLER, by_id["dummit-foote:2.1-subgroups"].node_id)),
        # AUTHORITY: back the subgroup criterion with the actual named,
        # checkable textbook section this lesson is drawn from -- a domain
        # fact, not a claim about the learner.
        _tutor(
            _bond_voice(
                render_authority(
                    MotivationMoment(
                        concept_name="the subgroup criterion",
                        cited_source="Dummit and Foote's Abstract Algebra, section 2.1",
                        authority_fact=(
                            "a nonempty subset H of a group G is a subgroup "
                            "exactly when H is closed under the operation "
                            "and closed under taking inverses"
                        ),
                    )
                )
            )
        ),
        _tutor(
            _bond_voice(
                render_graded_exposure(
                    LessonMoment(
                        concept_name="cosets",
                        easier_problem="verifying that Q Branch satisfies the subgroup criterion",
                        harder_problem=(
                            "building out every left coset of Q Branch and "
                            "checking they all come out the same size"
                        ),
                    )
                )
            )
        ),
        _learner(
            "I don't know -- there are a lot of these definitions stacking "
            "up now. I'm not sure I'm cut out for this kind of maths."
        ),
        # SOCIAL_PROOF: normalize the struggle the learner just voiced --
        # names a shared difficulty, never a shared outcome (see
        # teach.cialdini's module docstring for why that boundary matters).
        _tutor(
            _bond_voice(
                render_social_proof(
                    MotivationMoment(
                        concept_name="subgroups",
                        peer_difficulty=(
                            "feeling like the definitions are stacking up "
                            "faster than they can stick"
                        ),
                    )
                )
            )
        ),
        _tutor(
            _bond_voice(
                render_identify_stuck_belief(
                    LessonMoment(
                        concept_name="subgroups",
                        learner_statement=(
                            "I'm not sure I'm cut out for this kind of maths"
                        ),
                    )
                )
            )
        ),
        # UNITY: reframe the next step as shared work between tutor and
        # learner (Pre-Suasion's distinction from LIKING -- a shared
        # identity, not just a shared interest) right after naming the
        # stuck belief, before moving back into content.
        _tutor(
            _bond_voice(
                render_unity(
                    MotivationMoment(
                        concept_name="subgroups",
                        shared_identity="Q Branch, working this case together",
                    )
                )
            )
        ),
        _tutor(BOND_BACKEND(BOND_HANDLER, by_id["dummit-foote:3.1-cosets"].node_id)),
        # SCARCITY: the one easy-to-skim-past detail in what was just
        # narrated -- attention as the scarce resource, not a fabricated
        # deadline.
        _tutor(
            _bond_voice(
                render_scarcity(
                    MotivationMoment(
                        concept_name="cosets and normal subgroups",
                        scarce_detail=(
                            "normal means every conjugate gHg-inverse folds "
                            "back into H, not just the ones for one "
                            "particular g"
                        ),
                    )
                )
            )
        ),
        _tutor(
            _bond_voice(
                render_spaced_retrieval(
                    LessonMoment(
                        concept_name="Lagrange's Theorem",
                        prior_concept_name="cosets",
                    )
                )
            )
        ),
        _tutor(
            "Recall that the left coset gH is the set of products gh, and "
            "you've already shown these cosets partition Q Branch's network "
            "into blocks with no agent left uncovered."
        ),
        _tutor(BOND_BACKEND(BOND_HANDLER, by_id[TARGET_NODE_ID].node_id)),
        _tutor(
            "You just carried that coset argument through to Lagrange's "
            "Theorem on your own. If you keep working through subgroup "
            "problems like this one, you'll be ready to tackle the "
            "isomorphism theorems next."
        ),
    ]

    answer_key = {
        "lagrange": "the order of a finite group's subgroup divides the order of the group",
        "coset-size": "every left coset of H has the same size as H",
    }

    return PlannerState(
        target_node_id=TARGET_NODE_ID,
        traversal=traversal,
        answer_key=answer_key,
        turns=tuple(turns),
    )


def build_lesson() -> LessonArtifact:
    """The single producer-side entry point for teach-8xw.15: build the full
    Bond-framed D&F lesson and cross the boundary exactly once. This is the
    only function of this module a checker script should ever call."""
    return emit_lesson_artifact(build_planner_state())


def _self_check() -> None:
    from teach.boundary import check_no_forbidden_fields

    state = build_planner_state()
    artifact = build_lesson()

    violations = check_no_forbidden_fields(type(artifact))
    assert violations == [], f"build_lesson leaked planner fields: {violations}"
    assert not hasattr(artifact, "target_node_id")
    assert not hasattr(artifact, "traversal")
    assert not hasattr(artifact, "answer_key")

    # Every taught beat's exact node label appears in the lesson text --
    # the same "narrative actually mentions the concept" invariant
    # persona.render_traversal's own self-check enforces, checked here
    # against this module's hand-authored narration instead of the
    # generic TemplateBackend.
    graph = load_dummit_foote_graph()
    for node_id in state.traversal:
        label = graph.by_id(node_id).label
        assert label in artifact.text, f"lesson text never states {label!r} verbatim"

    # The fact this lesson is actually built to let a checker confirm:
    # Lagrange's theorem, stated in the source's own true-pattern phrasing.
    assert "order of the subgroup divides the order of the finite group" in artifact.text

    # teach-8xw.35: prove all seven Cialdini/Pre-Suasion principles actually
    # rendered into THIS artifact's text, not just that teach.cialdini's own
    # module self-check passed against its fake contexts. Re-render each
    # move from the exact MotivationMoment this module built and confirm the
    # resulting string is really in the lesson -- so a future edit that
    # drops a call site (rather than just deleting an import) still fails
    # loud here instead of silently reopening this bead.
    liking = render_liking(MotivationMoment(concept_name="Sets and Functions", shared_frame="the Bond briefing"))
    reciprocity = render_reciprocity(
        MotivationMoment(
            concept_name="Sets and Functions",
            given_first="the roster mapping between assets and handlers, worked through above",
            next_ask=(
                "write down, in your own words, what makes an assignment "
                "from assets to handlers bijective"
            ),
        )
    )
    commitment = render_commitment_consistency(
        MotivationMoment(
            concept_name="Sets and Functions",
            prior_commitment=(
                "Bijective means every asset gets exactly one handler and "
                "every handler gets covered -- nobody's unassigned, "
                "nobody's doubled up"
            ),
            consistent_next_step="the group axioms",
        )
    )
    authority = render_authority(
        MotivationMoment(
            concept_name="the subgroup criterion",
            cited_source="Dummit and Foote's Abstract Algebra, section 2.1",
            authority_fact=(
                "a nonempty subset H of a group G is a subgroup exactly "
                "when H is closed under the operation and closed under "
                "taking inverses"
            ),
        )
    )
    social_proof = render_social_proof(
        MotivationMoment(
            concept_name="subgroups",
            peer_difficulty="feeling like the definitions are stacking up faster than they can stick",
        )
    )
    unity = render_unity(
        MotivationMoment(concept_name="subgroups", shared_identity="Q Branch, working this case together")
    )
    scarcity = render_scarcity(
        MotivationMoment(
            concept_name="cosets and normal subgroups",
            scarce_detail=(
                "normal means every conjugate gHg-inverse folds back into "
                "H, not just the ones for one particular g"
            ),
        )
    )
    for principle_name, rendered in (
        ("reciprocity", reciprocity),
        ("commitment_consistency", commitment),
        ("liking", liking),
        ("authority", authority),
        ("scarcity", scarcity),
        ("unity", unity),
        ("social_proof", social_proof),
    ):
        assert rendered in artifact.text, (
            f"{principle_name}: rendered move never made it into the lesson text -- "
            "teach-8xw.35 requires all seven principles wired into the real traversal"
        )

    print(
        f"OK: built a {len(artifact.turns)}-turn Bond-framed D&F lesson "
        f"targeting {state.target_node_id}, crossing the boundary as a "
        f"clean LessonArtifact (no planner fields survive)"
    )


if __name__ == "__main__":
    _self_check()
