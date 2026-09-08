"""Producer-side planning state -- never crosses to the checker.

This is a stand-in for whatever the real planner (teach-8xw.4/.5/.6) ends up
being. It exists here so the boundary in `teach.boundary` has something
realistic to be tested against: a type that genuinely carries target node,
traversal, and answer key, plus the one function (`emit_lesson_artifact`)
that is allowed to reach across the line and what it's allowed to take.

Nothing outside this module -- and specifically nothing in a checker -- may
import `PlannerState`. There's no import-time enforcement for that (Python
doesn't have one that isn't its own footgun); the enforcement is that the
checker only ever receives a `LessonArtifact`, and `test_boundary.py` fails
if `LessonArtifact` ever grows a field that looks like it came from here.
"""
from __future__ import annotations

import dataclasses

from teach.boundary import LessonArtifact, Turn


@dataclasses.dataclass(frozen=True)
class PlannerState:
    """Everything the producer knows while building a lesson.

    target_node_id / traversal / answer_key are exactly the three examples
    sandbox-prompt.md names as things the checker must never see.
    """

    target_node_id: str
    traversal: tuple[str, ...]
    answer_key: dict[str, str]
    turns: tuple[Turn, ...]


def emit_lesson_artifact(state: PlannerState) -> LessonArtifact:
    """The single crossing point from producer state to checker input.

    Pulls `turns` -- the rendered dialogue -- and nothing else. Adding a
    second field read here (e.g. `state.target_node_id`) without also adding
    it to `LessonArtifact` would just be dropped; adding it to both is what
    `test_boundary.py::test_lesson_artifact_has_no_forbidden_fields` exists
    to catch.
    """
    return LessonArtifact(turns=state.turns)


if __name__ == "__main__":
    from teach.boundary import check_no_forbidden_fields

    state = PlannerState(
        target_node_id="dummit-foote-3.1-normal-subgroups",
        traversal=("groups", "subgroups", "normal-subgroups"),
        answer_key={"q1": "the kernel of a homomorphism is normal"},
        turns=(Turn(speaker="tutor", text="example turn"),),
    )
    artifact = emit_lesson_artifact(state)
    violations = check_no_forbidden_fields(type(artifact))
    assert violations == [], f"emit_lesson_artifact leaked planner fields: {violations}"
    assert not hasattr(artifact, "target_node_id")
    print("OK: emit_lesson_artifact strips all planner-only state")
