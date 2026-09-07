# teach

A multi-disciplinary teaching engine with two front-ends — interactive 1:1
tutoring and static curriculum development — over one planner. Instruction is
a traversal of a prerequisite knowledge graph, seeded from the Virginia
Mathematics Standards of Learning. A fluid persona renders that traversal as
narrative, reusing the story-generation machinery from `narrator`. Cognitive
behavioural therapy primitives are the pedagogical building blocks, and
Cialdini's *Influence* and *Pre-Suasion* guide the learner toward excellence.

That last sentence is the problem this repo is organized around.

A tutor optimized to be persuasive is optimized to make an ineffective lesson
*feel* like an effective one. Learner satisfaction is therefore worthless as
evidence, fluency reads as correctness, and a tutor that grades its own lesson
against the graph it planned from will always find its prerequisites
satisfied. The failure is invisible from inside.

So the checker is blind by construction. It sees only what the learner saw —
emitted lesson text, with no access to the planner's target node, traversal,
or answer key. From that alone it must independently recover which concept was
taught and which prerequisites it assumed, verify every domain fact against
source, and flag any claim about the learner's potential that outruns what
effort can actually deliver. Encouragement has to be honest to pass, not
merely warm.

Domains span reading, writing, foreign language, and arithmetic through
undergraduate mathematics. Where instruction touches biblical text, fidelity
is judged against sources rather than model recollection: BHS / Leningrad
Codex, with the Dead Sea Scrolls and ancient versions for variants, in the Old
Testament; Nestle-Aland 27/28 and UBS 4/5 in the New.

The test case is Dummit & Foote taught to a learner whose stated interest is
James Bond. It passes when the checker confirms the algebra is correct and the
prerequisites genuinely landed — not when the Bond framing was enjoyable.

Status: scaffolded, nothing built. The epic is `teach-8xw`.
