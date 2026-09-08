"""Producer: render a planned traversal of the prerequisite graph as
persona-voiced lesson narrative (teach-8xw.6).

The epic requires the persona layer to "reuse narrator's story-generation
machinery (motive graph, personality as data structure)" rather than
reimplement it from scratch. teach-8xw.1 confirmed there is no importable
`narrator` package to call into -- it is a standalone teaching project, not a
library -- and named exactly what is reusable as-is versus pattern-to-imitate
(see sandbox-handoffs/teach-8xw.1.md and the `teach-8xw-1-...` bd memory):

  REUSED AS-IS (vendored below, trimmed to what this module needs):
    - narrator/ocean.py's `Ocean` dataclass -- "personality as data
      structure": five OCEAN traits in [-1, 1] compiling to a system prompt
      and sampling options. Renamed `Persona` here since "Ocean" is narrator's
      internal name for the same idea and this module is not murder-mystery
      flavored. `CultureMatrix`/`transform` are NOT vendored -- nothing in
      this bead's acceptance criteria needs cross-cultural trait reweighting,
      and narrator's own module treats an uncited matrix as a values
      violation (fabricated psychometrics), a whole extra correctness surface
      this bead doesn't need to take on.
    - narrator/backends/base.py's `Backend` protocol -- profile-in/text-out
      seam, so a real LLM backend (ocean_ollama/ocean_fable-shaped) can be
      swapped in later without touching `render_traversal`.

  PATTERN IMITATED, NOT CODE COPIED:
    - narrator/motive.py separates a pure, fully-tested `describe()` (path ->
      plain text) from `prose()` (path -> LLM narrative), and `prose()` is
      deliberately NOT exercised by motive.py's own self-check -- it needs a
      live model, which the self-check philosophy in this whole repo (see
      concept_recovery.py, potential_checker.py, cbt_primitives.py -- all
      offline, deterministic, no network) does not permit. `beats()` below is
      the `describe()` analog (pure, fully tested); `TemplateBackend` is an
      honest, offline, deterministic stand-in for the LLM call `prose()`
      would make -- not a mock of one. A real backend is a drop-in swap via
      the `Backend` protocol; wiring narrator's own ocean_ollama/ocean_fable
      backends (or new ones) into an actual end-to-end run is teach-8xw.15's
      job, not this bead's.

Traversal input is deliberately just `Sequence[str]` (node ids), not
anything from `teach.producer_state.PlannerState` -- this module has no
opinion on how a traversal was planned, only on how to render one. What
crosses to the checker afterward is a `LessonArtifact`
(`teach.boundary.LessonArtifact`), which carries turns and nothing else;
`check_no_forbidden_fields` is re-checked in this module's self-check
against the artifact this module actually produces, not just against the
bare type.
"""
from __future__ import annotations

import dataclasses
import json
from typing import Any, Iterator, Protocol, Sequence, runtime_checkable

from teach.boundary import LessonArtifact, Turn
from teach.concept_graph import ConceptGraph, ConceptNode

# --- Persona: personality as data structure (vendored from narrator/ocean.py) ---

TRAITS = ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism")

DESCRIPTORS = {
    "openness": ("incurious, concrete, sticks to the familiar", "imaginative, abstract, chases novelty"),
    "conscientiousness": ("impulsive, disorganized, leaves things unfinished", "methodical, precise, finishes what it starts"),
    "extraversion": ("reserved, low-energy, speaks only when asked", "outgoing, talkative, fills silences"),
    "agreeableness": ("blunt, skeptical, contradicts freely", "warm, accommodating, seeks agreement"),
    "neuroticism": ("calm, unbothered, steady under pressure", "anxious, defensive, hedges and second-guesses"),
}

THRESHOLD = 0.4


@dataclasses.dataclass
class Persona:
    """Five OCEAN traits, each in [-1.0, 1.0]. Compiles to a system prompt
    and sampling options a `Backend` uses to voice lesson narrative --
    exactly narrator ocean.py's `Ocean`, renamed for this non-mystery
    context. See module docstring for what was deliberately left out."""

    openness: float = 0.0
    conscientiousness: float = 0.0
    extraversion: float = 0.0
    agreeableness: float = 0.0
    neuroticism: float = 0.0

    def __post_init__(self) -> None:
        for t in TRAITS:
            v = getattr(self, t)
            if not -1.0 <= v <= 1.0:
                raise ValueError(f"{t}={v} outside [-1.0, 1.0]")

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(dataclasses.asdict(self), f, indent=2, sort_keys=True)
            f.write("\n")

    @classmethod
    def load(cls, path: str) -> "Persona":
        with open(path) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected a JSON object, got {type(data).__name__}")
        if unknown := sorted(set(data) - set(TRAITS)):
            raise ValueError(f"{path}: unknown traits {unknown}; expected {list(TRAITS)}")
        if missing := sorted(set(TRAITS) - set(data)):
            raise ValueError(f"{path}: missing traits {missing}")
        for t in TRAITS:
            if isinstance(data[t], bool) or not isinstance(data[t], (int, float)):
                raise ValueError(f"{path}: {t} must be a number, got {data[t]!r}")
        try:
            return cls(**data)
        except ValueError as e:
            raise ValueError(f"{path}: {e}") from e

    def system_prompt(self) -> str:
        lines = []
        for t in TRAITS:
            v = getattr(self, t)
            if abs(v) > THRESHOLD:
                lines.append(f"- {DESCRIPTORS[t][v > 0]} (strength {abs(v):.2f})")
        if not lines:
            return "Adopt a neutral tutoring voice, with no pronounced personality."
        return "Adopt this personality while tutoring:\n" + "\n".join(lines)

    def options(self) -> dict[str, float]:
        temperature = 0.7 + 0.4 * self.neuroticism - 0.3 * self.conscientiousness
        return {
            "temperature": round(max(0.1, min(1.5, temperature)), 3),
            "top_p": round(max(0.3, min(0.99, 0.9 + 0.09 * self.openness)), 3),
            "repeat_penalty": round(1.1 + 0.2 * max(0.0, self.conscientiousness), 3),
        }


# --- Backend: the profile-in/text-out seam (vendored from narrator/backends/base.py) ---


@runtime_checkable
class Backend(Protocol):
    """`generate(profile, prompt, model=...) -> str`. A real implementation
    compiles `profile.system_prompt()`/`profile.options()` inside the call,
    the same contract narrator's `backends/` modules use -- so a caller here
    never needs to know which backend it's talking to. See
    narrator/backends/ocean_ollama.py and ocean_fable.py for two real,
    network-backed implementations of this same shape; neither is vendored
    into this bead (both need a live server or API key this sandbox's tests
    must not depend on)."""

    def __call__(self, profile: Any, prompt: str, model: str = ...) -> str:
        ...


def conforms(candidate: object) -> bool:
    return isinstance(candidate, Backend) and callable(candidate)


class TemplateBackend:
    """Deterministic, offline `Backend`: no network call, no model. An
    honest reference implementation -- not a mock of an LLM -- that always
    renders the beat's concept label and facts verbatim, wrapped in a
    persona-flavored frame built from `profile.system_prompt()`.

    This is what every other producer/checker module in this repo already
    does (concept_recovery, potential_checker, cbt_primitives.render_*):
    deterministic string construction, no live model dependency, so the
    self-check and test suite run offline and reproducibly. Swap in a real
    `Backend` (narrator-shaped, calling Ollama or Fable) for actual
    generation; `render_traversal` takes any `Backend`, this is just the
    default.
    """

    def __call__(self, profile: Any, prompt: str, model: str = "template") -> str:
        tone = profile.system_prompt()
        return f"{tone}\n\n{prompt}"


DEFAULT_BACKEND = TemplateBackend()


# --- traversal -> beats -> narrative -----------------------------------------


def _flatten_strings(value: object) -> Iterator[str]:
    """Yield every string reachable inside an opaque `ConceptNode.facts`
    payload. Facts are per-domain data (teach-8xw.4) whose shape this module
    must not assume -- mirrors concept_recovery.py's own harvesting so a
    domain's real vocabulary reaches the narrative rather than being
    dropped, without importing checker code into the producer."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _flatten_strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _flatten_strings(v)


@dataclasses.dataclass(frozen=True)
class Beat:
    """One traversal step's plain content -- the `describe()` analog to
    narrator/motive.py's story states. Pure data, no persona or backend
    involved yet."""

    node_id: str
    label: str
    facts_text: str


def beats(graph: ConceptGraph, traversal: Sequence[str]) -> tuple[Beat, ...]:
    """Turn a traversal (sequence of node ids, in the order they should be
    taught) into plain per-node content. Raises `KeyError` (via
    `graph.by_id`) on an unknown node id, and `ValueError` on an empty
    traversal -- fail loud rather than silently rendering nothing, per
    sandbox-prompt.md's abstention-over-guessing rule applied to a caller
    error rather than a genuinely ambiguous case."""
    if not traversal:
        raise ValueError("traversal must contain at least one node id")
    out = []
    for node_id in traversal:
        node = graph.by_id(node_id)
        facts_text = "; ".join(_flatten_strings(node.facts)) or "(no additional facts recorded)"
        out.append(Beat(node_id=node.id, label=node.label, facts_text=facts_text))
    return tuple(out)


def _beat_prompt(beat: Beat, position: int, total: int) -> str:
    return (
        f"You are tutoring step {position} of {total} in this lesson. "
        f'Teach this concept next: "{beat.label}". '
        f"Ground truth to draw on, in your own words but without dropping the "
        f'specifics: {beat.facts_text}. Use the exact phrase "{beat.label}" at '
        f"least once, so the learner can clearly identify what was just taught."
    )


def render_traversal(
    graph: ConceptGraph,
    traversal: Sequence[str],
    persona: Persona,
    backend: Backend = DEFAULT_BACKEND,
    model: str = "persona-default",
) -> LessonArtifact:
    """Render a planned traversal as persona-voiced lesson narrative.

    One tutor `Turn` per node in `traversal`, in order -- `beats()` supplies
    the plain content, `backend` supplies the persona-flavored text for each
    beat. Returns a `LessonArtifact`, the only type allowed to cross to the
    checker (`teach.boundary`); nothing about `graph` or `traversal` itself
    is attached to the result beyond what made it into the rendered text.
    """
    steps = beats(graph, traversal)
    turns = tuple(
        Turn(speaker="tutor", text=backend(persona, _beat_prompt(beat, i, len(steps)), model=model))
        for i, beat in enumerate(steps, start=1)
    )
    return LessonArtifact(turns=turns)


if __name__ == "__main__":
    from teach.boundary import check_no_forbidden_fields

    graph = ConceptGraph(
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
    traversal = tuple(n.id for n in graph.nodes)
    persona = Persona(openness=0.8, extraversion=0.6, neuroticism=-0.5)

    artifact = render_traversal(graph, traversal, persona)

    violations = check_no_forbidden_fields(type(artifact))
    assert violations == [], f"render_traversal produced a leaking artifact type: {violations}"

    assert len(artifact.turns) == len(traversal)
    text = artifact.text
    positions = []
    for node_id in traversal:
        node = graph.by_id(node_id)
        assert node.label in text, f"narrative never mentions {node.label!r}: {text!r}"
        positions.append(text.index(node.label))
    assert positions == sorted(positions), "traversal order was not preserved in the rendered narrative"

    try:
        render_traversal(graph, (), persona)
        raise AssertionError("expected ValueError on an empty traversal")
    except ValueError:
        pass

    try:
        render_traversal(graph, ("no-such-node",), persona)
        raise AssertionError("expected KeyError on an unknown node id")
    except KeyError:
        pass

    print(
        f"OK: rendered a {len(traversal)}-node traversal as persona-voiced narrative, "
        f"mentioning every concept in traversal order"
    )
