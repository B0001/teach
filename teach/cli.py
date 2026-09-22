"""Interactive teaching CLI: a real terminal session through the one lesson
this repo has fully built and verified end-to-end -- the Judson/Bond
Lagrange's-Theorem lesson -- typed live by a real learner, then handed to the
blind checker for a real verdict on that real session.

No LLM. `teach.judson_bond_lesson.BOND_BACKEND` is a fixed, offline lookup
of hand-authored narration per node -- same as running
`python3 -m teach.judson_bond_integration`. What's different here is that
the three learner turns are your own typed answers (fed live into
`build_lesson`'s `on_turn`/`get_learner_answer` seam), not the hardcoded
script, and the closing line only credits you with the Lagrange derivation
if your own answer actually states it (teach.judson_bond_lesson's honesty
gate) -- pressing Enter to skip a question falls back to the scripted
answer, so the lesson always completes even with no input.

Scope: this is the one lesson the producer has -- Judson chapters 1-6 up to
Lagrange's Theorem, Bond-framed. There is no topic selection; "teach me
something else" is a real gap, not something faked here. See sandbox-prompt.md.
"""
from __future__ import annotations

from teach.boundary import Turn
from teach.judson_bond_integration import run_integration_check
from teach.judson_bond_lesson import build_lesson

_WIDTH = 78


def _print_turn(turn: Turn) -> None:
    label = "TUTOR" if turn.speaker == "tutor" else "YOU"
    print(f"\n[{label}] {turn.text}")


def _get_learner_answer(key: str) -> str | None:
    try:
        return input("\n> ").strip()
    except EOFError:
        return None


def main() -> None:
    print("=" * _WIDTH)
    print("Q BRANCH BRIEFING -- Judson, Abstract Algebra, ch. 1, 3, 6")
    print("Type your own answers when prompted. Blank + Enter (or Ctrl-D)")
    print("uses the scripted answer instead.")
    print("=" * _WIDTH)

    artifact = build_lesson(on_turn=_print_turn, get_learner_answer=_get_learner_answer)

    print("\n" + "=" * _WIDTH)
    print("CHECKER REPORT -- blind: sees only the transcript above, nothing else")
    print("=" * _WIDTH)
    print(run_integration_check(artifact).render())


if __name__ == "__main__":
    main()
