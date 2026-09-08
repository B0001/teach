You are working autonomously in the teach repo. Make aggressive, real
progress. Do not stop to ask permission; do not stop early because you are
unsure whether there is work left.

## What this repo is

A multi-disciplinary teaching system with two front-ends over one engine: interactive 1:1 tutoring and static curriculum development. Instruction is planned as a traversal of a prerequisite knowledge graph (the mathgraph dependency-DAG idea, seeded from the Virginia Mathematics Standards of Learning and published as an AI-consumable graph on HuggingFace), and delivered through a fluid persona that renders that path as narrative using the story-generation machinery from narrator. Pedagogy is built on cognitive behavioural therapy primitives; motivation is guided by Cialdini's Influence and Pre-Suasion, bounded by a hard honesty constraint. Domains span reading, writing, foreign language and arithmetic through undergraduate mathematics. Test case: teach Dummit & Foote abstract algebra to a learner whose stated interest is James Bond.

`bd show teach-8xw` is the epic; its children are the stages.

## The standard everything is held to

**The output of this system is a claim that a learner who followed this instruction actually learned the concept it purports to teach - that the prerequisites it assumed were genuinely established, that every domain fact it asserted is correct, and that every statement about the learner's potential is one they can actually reach by working hard.**

The producer is explicitly optimized to be persuasive: Cialdini-guided, narratively engaging, persona-adaptive. That is precisely the machinery that makes an ineffective lesson feel like an effective one, so learner satisfaction is worthless as evidence and fluency reads as correctness. A tutor that grades its own lesson against the same knowledge graph it planned from will always find the prerequisites satisfied - the failure is invisible from inside. So the checker sees only what the learner saw: emitted lesson text, with no access to the planner's target node, traversal, or answer key. From that alone it must independently recover which concept was taught and which prerequisites were assumed, verify the domain facts against source, and flag any promise about the learner's potential that outruns what effort can deliver. Where instruction touches biblical text, fidelity is judged against BHS/Leningrad Codex with Dead Sea Scrolls and ancient-version variants for the OT, and NA27/28 with UBS4/5 for the NT - never against the model's recollection.

That is the kind of claim that is easy to get wrong and hard to notice being
wrong. The whole value of the tool is whether it can be trusted.

So:

- **A result is a candidate until something measured says otherwise.** Never
  let a producer's output be phrased, logged, or reported as if it were
  verified. State the scope you actually covered: *this* index, *these*
  inputs, *this* threshold. Coverage you did not measure is not coverage you
  have.
- **Prefer abstention to a confident answer.** A component that returns
  "cannot tell" on the cases it cannot separate is worth more than one that
  guesses and is right most of the time — because the consumer of the output
  cannot tell which mode they are in.
- **A number is only allowed to exist in a document if the code produces it,
  or the document says where it came from.** When a documented figure and the
  code disagree you have two honest moves: fix the code, or fix the document.
  Never a third. Do not quietly delete a number and do not round it into
  vagueness.
- **A passing test with a name is evidence. Your reasoning is not.** Do not
  claim a behaviour holds because it looks like it should. Make it fail first
  if you can — an assertion you never saw fail is an assertion you have not
  verified.
- **The checker must not be able to see the producer's internals.** If the
  verifying half can read the generating half's state, it will agree with it,
  and you will have tested nothing. Give it only what a real consumer gets.
- **The same rule applies to your own tool calls.** A summarizer is a producer
  too, and it will agree with the thing that queried it. On any lookup that
  decides a question — does this package exist, does this source say that,
  does this dataset contain those edges — fetch the raw bytes and read them
  yourself. Be most suspicious when the answer confirms exactly what you were
  hoping to find. This is not hypothetical: in `teach-8xw.1`, WebFetch on the
  PyPI `narrator` package returned a summary claiming it "features a motive
  graph… personality as data structure," mirroring the searcher's own terms.
  The real package is tweet-data visualization by an unrelated author. `curl`
  on the same JSON showed it immediately. A fabricated confirmation is the
  single most expensive thing you can carry into a bead, because everything
  downstream inherits it silently.

## Working rules

- The bead is the specification. Where a design document and a bead disagree,
  the bead wins; where the code and a bead disagree, say so rather than
  silently following one.
- Reproduce before you file. A bead asserting a problem you did not observe
  wastes a whole worker session.
- Work outside the current bead's scope gets filed as a new bead, not done now.
- Leave one runnable check behind for any non-trivial logic. It does not need
  a framework; it needs to fail if the logic breaks.
- Do not commit or push unless the bead explicitly says to.
