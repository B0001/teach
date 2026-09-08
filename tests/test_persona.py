"""Enforce teach/persona.py: the producer's persona/narrative rendering of a
planned graph traversal (teach-8xw.6).

teach-8xw.6's acceptance criteria: given a traversal (sequence of graph
nodes) and a persona config, produce lesson narrative text, with a runnable
check that feeds a small fixed traversal and asserts the output actually
mentions each node's concept. These tests are that check, plus proof of the
surrounding invariants: traversal order survives into the rendered text, the
output stays within the producer/checker boundary, an empty or unknown
traversal fails loud rather than silently, and `Persona` is a real
personality-as-data-structure type (range-validated, round-trips through
JSON) rather than a bag of unchecked floats.
"""
import pytest

from teach.boundary import LessonArtifact, check_no_forbidden_fields
from teach.concept_graph import ConceptGraph, ConceptNode
from teach.persona import (
    DEFAULT_BACKEND,
    Persona,
    TemplateBackend,
    beats,
    conforms,
    render_traversal,
)


@pytest.fixture
def graph():
    return ConceptGraph(
        nodes=(
            ConceptNode(
                id="dummit-foote:3.1-cosets", domain="math", label="cosets",
                facts={"statement": "a coset partitions a group into equal-size classes"},
            ),
            ConceptNode(
                id="dummit-foote:3.1-normal-subgroups", domain="math", label="normal subgroups",
                facts={"statement": "a subgroup is normal when its left and right cosets coincide"},
            ),
            ConceptNode(
                id="dummit-foote:3.3-quotient-groups", domain="math", label="quotient groups",
                facts={"statement": "the cosets of a normal subgroup form a group under coset multiplication"},
            ),
        ),
        edges=(),
    )


@pytest.fixture
def traversal(graph):
    return tuple(n.id for n in graph.nodes)


# --- Persona: personality as data structure ---------------------------------


def test_persona_rejects_out_of_range_trait():
    for bad in (1.5, -2.0):
        with pytest.raises(ValueError):
            Persona(openness=bad)


def test_persona_default_system_prompt_is_neutral():
    assert Persona().system_prompt().startswith("Adopt a neutral")


def test_persona_system_prompt_reflects_strong_traits():
    outgoing = Persona(extraversion=0.9)
    assert "outgoing" in outgoing.system_prompt()
    reserved = Persona(extraversion=-0.9)
    assert "reserved" in reserved.system_prompt()


def test_persona_at_threshold_is_not_over_it():
    from teach.persona import THRESHOLD

    assert Persona(openness=THRESHOLD).system_prompt().startswith("Adopt a neutral")


def test_persona_options_vary_with_traits():
    calm = Persona(conscientiousness=0.9)
    anxious = Persona(neuroticism=0.9, conscientiousness=-0.5)
    assert calm.options()["temperature"] < anxious.options()["temperature"]


def test_persona_save_load_round_trips(tmp_path):
    original = Persona(openness=0.3, conscientiousness=-0.7, extraversion=0.0, agreeableness=0.95, neuroticism=-0.25)
    path = tmp_path / "persona.json"
    original.save(str(path))
    assert Persona.load(str(path)) == original


def test_persona_load_rejects_missing_or_unknown_traits(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"openness": 0.5}')
    with pytest.raises(ValueError):
        Persona.load(str(path))

    path.write_text(
        '{"openness": 0, "conscientiousness": 0, "extraversion": 0, '
        '"agreeableness": 0, "neuroticism": 0, "charisma": 1}'
    )
    with pytest.raises(ValueError):
        Persona.load(str(path))


# --- Backend seam ------------------------------------------------------------


def test_template_backend_conforms_to_backend_protocol():
    assert conforms(TemplateBackend())
    assert conforms(DEFAULT_BACKEND)


def test_non_callable_does_not_conform():
    assert not conforms(object())
    assert not conforms(5)


def test_template_backend_includes_persona_tone_and_prompt():
    backend = TemplateBackend()
    persona = Persona(extraversion=0.9)
    out = backend(persona, "teach cosets", model="template")
    assert "outgoing" in out
    assert "teach cosets" in out


# --- beats(): pure traversal -> plain content -------------------------------


def test_beats_preserves_traversal_order_and_labels(graph, traversal):
    steps = beats(graph, traversal)
    assert [b.node_id for b in steps] == list(traversal)
    assert [b.label for b in steps] == ["cosets", "normal subgroups", "quotient groups"]


def test_beats_flattens_opaque_facts_regardless_of_shape():
    graph = ConceptGraph(
        nodes=(
            ConceptNode(
                id="x:1", domain="reading", label="main idea",
                facts={"passage": "some text", "targets": ["identify theme", "cite evidence"]},
            ),
        ),
        edges=(),
    )
    (beat,) = beats(graph, ("x:1",))
    assert "some text" in beat.facts_text
    assert "identify theme" in beat.facts_text
    assert "cite evidence" in beat.facts_text


def test_beats_rejects_empty_traversal(graph):
    with pytest.raises(ValueError):
        beats(graph, ())


def test_beats_rejects_unknown_node_id(graph):
    with pytest.raises(KeyError):
        beats(graph, ("no-such-node",))


# --- render_traversal(): the bead's acceptance criterion --------------------


def test_render_traversal_mentions_every_node_concept_in_order(graph, traversal):
    artifact = render_traversal(graph, traversal, Persona(openness=0.8, extraversion=0.6, neuroticism=-0.5))
    text = artifact.text
    positions = [text.index(graph.by_id(n).label) for n in traversal]
    assert positions == sorted(positions)


def test_render_traversal_produces_one_turn_per_node(graph, traversal):
    artifact = render_traversal(graph, traversal, Persona())
    assert len(artifact.turns) == len(traversal)
    assert all(t.speaker == "tutor" for t in artifact.turns)


def test_render_traversal_output_stays_within_the_boundary(graph, traversal):
    artifact = render_traversal(graph, traversal, Persona())
    assert isinstance(artifact, LessonArtifact)
    assert check_no_forbidden_fields(type(artifact)) == []
    assert not hasattr(artifact, "traversal")
    assert not hasattr(artifact, "target_node_id")


def test_render_traversal_rejects_empty_traversal(graph):
    with pytest.raises(ValueError):
        render_traversal(graph, (), Persona())


def test_render_traversal_rejects_unknown_node_id(graph):
    with pytest.raises(KeyError):
        render_traversal(graph, ("no-such-node",), Persona())


def test_render_traversal_different_personas_render_different_text(graph, traversal):
    warm = render_traversal(graph, traversal, Persona(agreeableness=0.9))
    blunt = render_traversal(graph, traversal, Persona(agreeableness=-0.9))
    assert warm.text != blunt.text


def test_render_traversal_uses_a_custom_backend(graph, traversal):
    class EchoBackend:
        def __call__(self, profile, prompt, model="echo"):
            return f"ECHO[{model}]: {prompt}"

    artifact = render_traversal(graph, traversal, Persona(), backend=EchoBackend(), model="my-model")
    assert all(t.text.startswith("ECHO[my-model]:") for t in artifact.turns)
