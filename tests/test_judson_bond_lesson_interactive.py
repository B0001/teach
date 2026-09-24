"""The interactive-CLI seam on teach.judson_bond_lesson.build_lesson
(on_turn / get_learner_answer): a real learner's own answers must flow into
the transcript, and the closing Lagrange credit line must not fire unless
the learner's own derivation actually states the divisibility conclusion --
the honesty constraint sandbox-prompt.md requires, exercised against a real
wrong answer rather than only the scripted-correct default.
"""
from teach.boundary import Turn
from teach.judson_bond_lesson import build_lesson


def test_get_learner_answer_feeds_live_answers_into_the_transcript():
    answers = {
        "bijective": "a pairing where nothing is left out and nothing doubled",
        "stuck_belief": "not sure I can do this",
        "lagrange": "the block count has to divide the total, I think",
    }
    artifact = build_lesson(get_learner_answer=lambda key: answers[key])
    for answer in answers.values():
        assert answer in artifact.text


def test_blank_answers_fall_back_to_the_scripted_lesson():
    # Not byte-identical to the pure no-args default: when a live callback
    # is wired up, identify_stuck_belief quotes back whatever the learner
    # answer resolves to (here, the scripted fallback's full sentence)
    # rather than the non-interactive path's hand-trimmed phrase -- see
    # build_planner_state's stuck_belief_statement branch. What must hold
    # is that the lesson still completes and still earns the Lagrange
    # credit line, since the scripted fallback answer states divisibility.
    scripted = build_lesson()
    interactive_blank = build_lesson(get_learner_answer=lambda key: "")
    assert len(interactive_blank.turns) == len(scripted.turns)
    assert "You just carried that coset argument through" in interactive_blank.text


def test_on_turn_is_called_once_per_turn_in_order():
    seen: list[Turn] = []
    artifact = build_lesson(on_turn=seen.append)
    assert tuple(seen) == artifact.turns


def test_wrong_derivation_does_not_earn_the_credit_line():
    artifact = build_lesson(get_learner_answer=lambda key: "I don't know" if key == "lagrange" else "")
    assert "You just carried that coset argument through" not in artifact.text
    assert "Not quite there yet" in artifact.text


def test_correct_derivation_earns_the_credit_line():
    artifact = build_lesson(
        get_learner_answer=lambda key: "so it has to divide the total" if key == "lagrange" else ""
    )
    assert "You just carried that coset argument through" in artifact.text
