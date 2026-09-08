"""The blind interface boundary between producer and checker.

sandbox-prompt.md: "the checker sees only what the learner saw: emitted
lesson text, with no access to the planner's target node, traversal, or
answer key." Nothing enforced that until this module existed -- a producer
author could add a `target_node_id` field to whatever crosses to the checker
and nothing would complain.

`LessonArtifact` is the only type allowed to cross from producer to checker.
`check_no_forbidden_fields` is the static check: it walks a dataclass's
fields (recursing into nested dataclasses) and fails if any field name
matches a planner-only concept. Run it against `LessonArtifact` itself (must
pass) and against any new type before wiring it in as something the checker
receives.
"""
from __future__ import annotations

import dataclasses
import typing
from typing import Iterator


# Substrings that mark a field as planner-only. Substrings, not exact names,
# because "target_node_id" and "target_node" and "node_id" should all be
# caught by one entry rather than three exact matches someone forgets to
# extend. Grow this list when the producer grows new planner-only concepts.
FORBIDDEN_FIELD_SUBSTRINGS = (
    "target_node",
    "target_concept",
    "traversal",
    "planner",
    "answer_key",
    "answer",
    "solution",
    "prerequisite",
    "prereq",
    "graph",
    "node_id",
    "dag",
)


@dataclasses.dataclass(frozen=True)
class BoundaryViolation:
    path: str  # dotted field path, e.g. "LessonArtifact.turns.node_id"
    field_name: str
    matched: str  # which forbidden substring matched


def _iter_dataclass_fields(cls: type, path: str) -> Iterator[BoundaryViolation]:
    if not dataclasses.is_dataclass(cls):
        return
    # get_type_hints resolves the string annotations that `from __future__
    # import annotations` produces back into real type objects -- reading
    # dataclasses.fields()[i].type directly would just give us strings.
    hints = typing.get_type_hints(cls)
    for f in dataclasses.fields(cls):
        field_path = f"{path}.{f.name}"
        lowered = f.name.lower()
        for forbidden in FORBIDDEN_FIELD_SUBSTRINGS:
            if forbidden in lowered:
                yield BoundaryViolation(
                    path=field_path, field_name=f.name, matched=forbidden
                )
                break
        # Recurse into nested dataclass field types, and into the element
        # type of list/tuple[...] containers holding a nested dataclass --
        # a leak inside `turns: tuple[Turn, ...]` is exactly as real as a
        # leak on a top-level field.
        inner = hints.get(f.name, f.type)
        args = getattr(inner, "__args__", None)
        if args:
            for arg in args:
                yield from _iter_dataclass_fields(arg, field_path)
        else:
            yield from _iter_dataclass_fields(inner, field_path)


def check_no_forbidden_fields(cls: type) -> list[BoundaryViolation]:
    """Static check: list every planner-only-looking field reachable from cls.

    Empty list means cls is clean. This is the check referenced by
    teach-8xw.9's acceptance criteria -- it must fail (return violations)
    when run against a type that leaks planner state, and pass (return [])
    against the real LessonArtifact.
    """
    return list(_iter_dataclass_fields(cls, cls.__name__))


@dataclasses.dataclass(frozen=True)
class Turn:
    """One turn of dialogue exactly as the learner saw it rendered."""

    speaker: str  # "tutor" or "learner"
    text: str


@dataclasses.dataclass(frozen=True)
class LessonArtifact:
    """The only thing that is allowed to cross from producer to checker.

    Carries exactly what a learner would have seen on screen: a transcript
    of rendered turns. Nothing else -- no target concept, no traversal, no
    answer key, no graph. If a checker needs to know something, it has to be
    recoverable from reading this like a learner would (teach-8xw.10's job),
    not smuggled in as a new field here.

    `check_no_forbidden_fields(LessonArtifact)` must return `[]`; that
    invariant is enforced by tests/test_boundary.py so a future edit that
    adds a planner-only field breaks the suite instead of shipping quietly.
    """

    turns: tuple[Turn, ...]

    @property
    def text(self) -> str:
        """Flattened lesson text -- the form most checkers will consume."""
        return "\n".join(f"{t.speaker}: {t.text}" for t in self.turns)


if __name__ == "__main__":
    violations = check_no_forbidden_fields(LessonArtifact)
    assert violations == [], f"LessonArtifact leaks planner fields: {violations}"
    print(f"OK: LessonArtifact is clean ({len(dataclasses.fields(LessonArtifact))} fields, no planner leaks)")
