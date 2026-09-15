"""teach-cpg: FOURTH held-out generalization round for concept_recovery.py
against the VA Writing SOL K-12 graph, run by a session that did NOT write
teach-cpg's fix (the single-winner branch's rival-coverage comparison in
`_resolve_candidates`).

teach-cpg's fix addressed a hole teach-8xw.53's round 2 found: a
bare-minimum-margin winner's own coverage was checked against a fixed floor,
but never against the coverage of the single largest rival that put it in
the "close" group in the first place. Per sandbox-prompt.md's "you cannot
hold out examples from yourself", teach-cpg's own bug-report text
(GRADE6_SIGNPOSTED, in round 2) is tuning data for that fix -- guaranteed to
pass, proves nothing about generalization. teach-cpg's own acceptance
criteria require its own FOURTH independently-authored held-out round,
from a session that had not read the bead, the fix, or round 2, before it
can be closed. This file is that round.

WHERE THIS TEXT CAME FROM

Six lesson dialogues below were each produced by a separate `Agent` tool
call (same method as round 1's teach-8xw.33 precedent and round 2's
teach-8xw.53 precedent). Each agent call was given an explicit
no-tool-use, no-repository-access instruction and was told nothing about
concept_recovery.py's existence, scoring mechanism, thresholds, or any
bead's history -- only plain-English curriculum content (paraphrased by
this bead's session directly from the real VA Writing SOL leaf-standard
text in teach/data/va_writing_sol_k12.json, never from concept_recovery.py
or any test file) and an instruction to render it as a natural
tutor/student dialogue, not a copied list. None of the six agents saw
another's output, this module's code, or round 1/round 2's fixtures.

Grades were chosen to include: three signposted cases (prior grade
reviewed, then escalated -- grades 3, 5, 8), one unsignposted case with no
prior-grade callback at all (grade 6 -- deliberately the SAME grade as
round 2's confident-wrong-answer case, to directly re-probe the exact
failure mode teach-cpg's fix targets, but via fresh, independently
generated text rather than the original bug report), one fully standalone
case with no signposting (grade 4), and one off-domain control (fractions
and decimals -- pure math, no writing-domain vocabulary at all).

HONEST RESULT (measured once against the real, unmodified
`teach.va_writing_sol_graph`, via the public `recover_from_lesson_text`
entry point only -- no internals of concept_recovery.py were read to choose
or adjust these lesson texts, and no threshold in concept_recovery.py was
changed in response to seeing these results):

  correct recoveries: 3 / 6  (GRADE3_SIGNPOSTED_COOKING, GRADE5_SIGNPOSTED_ROBOTICS,
                               GRADE4_STANDALONE_BASKETBALL)
  safe abstentions:   2 / 6  (GRADE8_SIGNPOSTED_PHOTOGRAPHY, OFFDOMAIN_FRACTIONS_BAKING)
  CONFIDENT WRONG ANSWERS: 1 / 6  (GRADE6_UNSIGNPOSTED_GARDENING)

The one confident wrong answer matters most, and it is a genuinely new
finding, not a repeat of round 2's case:

  GRADE6_UNSIGNPOSTED_GARDENING (intended taught=6.W, no prerequisite claim
  expected since nothing is signposted): recovers taught=7.W with
  unsignposted_prerequisite_ids=('va-writing-sol:6.W',) -- the correct
  answer demoted to a "prerequisite" of the wrong one.

  Root-caused precisely (see tests/test_concept_recovery.py-adjacent
  diagnostics run during this round, not committed here since they are
  throwaway instrumentation, not fixture data):

    Raw exact-word tier -- teach-cpg's fix WORKS here:
      va-writing-sol:7.W  score=20  coverage=40.00%  (candidates[0])
      va-writing-sol:6.W  score=18  coverage=56.25%  (candidates[1], the
                                                       true rival)
    margin = 2 (<= _MIN_MARGIN). teach-cpg's gate compares top against
    candidates[1] (6.W); 6.W's coverage is higher, so the gate correctly
    fires and the raw tier ABSTAINS -- exactly as designed.

    Because the raw tier abstained, recover_taught_concept falls through to
    the semantic (WordNet) fallback tier, which computes its OWN
    independently-ranked candidate list:
      va-writing-sol:7.W   score=27  coverage=54.00%  (candidates[0])
      va-writing-sol:8.W   score=24  coverage=42.86%  (candidates[1] --
                                                        NOT the true rival)
      va-writing-sol:11.W  score=17  coverage=32.69%
      va-writing-sol:6.W   score=16  coverage=50.00%  (true rival, now
                                                        candidates[3])
    margin = 3 (<= _SEMANTIC_MIN_MARGIN). teach-cpg's gate compares top
    against candidates[1] -- which is now 8.W, not 6.W. 8.W's coverage
    (42.86%) is lower than 7.W's (54%), so the gate does not fire, and the
    semantic tier confidently returns 7.W.

  teach-cpg's fix only ever inspects `candidates[1]` (the single
  next-highest-by-raw-score candidate) as "the rival". That is reliably the
  true confusable rival on the raw tier here, but WordNet synonym expansion
  in the semantic tier inflates two OTHER candidates (8.W, 11.W) enough to
  outrank the true rival (6.W) by raw score, displacing it out of the
  candidates[1] slot the fix actually checks. This is a distinct structural
  gap from what teach-cpg fixed -- filed as teach-i35, discovered-from
  teach-cpg, NOT fixed in this session per this lineage's standing rule
  against tuning a fix against the same round that measured it.

WHAT THIS MEANS FOR teach-cpg's OWN CLOSURE

teach-cpg's fix demonstrably improved generalization (round 2's original
GRADE6_SIGNPOSTED case is now a safe abstention instead of a confident wrong
answer, confirmed in
tests/test_concept_recovery_writing_domain_generalization_round2.py), but a
fresh, independently-authored round found a new confident wrong answer the
fix does not cover. Per teach-cpg's own explicit closing requirement ("its
own FOURTH independently-authored held-out round" must show the fix
"generalizes"), 1/6 confident wrong answers means it does not fully
generalize. teach-cpg is left OPEN with this file as the evidence; the
newly-found gap is tracked separately as teach-i35.

Two secondary observations, reported as-is and not treated as failures of
this bead's scope:

  - GRADE8_SIGNPOSTED_PHOTOGRAPHY (intended taught=8.W, assumed=(7.W,)):
    the module abstains instead of recovering 8.W, via exactly the
    coverage-tiebreak reasoning teach-cpg's fix added (7.W is proportionally
    a slightly better-covered rival at this bare-minimum margin). This
    costs recall, not correctness -- consistent with this module's
    documented bias toward declining over guessing -- but it does mean
    teach-cpg's fix can suppress a genuinely correct recovery, not just
    incorrect ones, when a real (non-buggy) rival happens to score close.
  - GRADE4_STANDALONE_BASKETBALL correctly recovers taught=4.W but also
    reports unsignposted_prerequisite_ids=('va-writing-sol:3.W',) even
    though the lesson text was deliberately written with no prior-grade
    signposting at all. This may be the unsignposted-prerequisite
    detector correctly noticing genuine 3.W vocabulary overlap (narrative
    sequencing, linking words) that is structurally present in the text
    regardless of authorial intent to signpost it -- not necessarily a
    defect. Not investigated further here: recover_unsignposted_prerequisites
    is a different function than the one teach-cpg's fix touches, and this
    is reported as an observation, not a bug, per this bead's scope.
"""

import pytest

from teach.concept_recovery import recover_from_lesson_text
from teach.va_writing_sol_graph import load_va_writing_sol_graph

WRITING_GRAPH = load_va_writing_sol_graph()

GRADE3_SIGNPOSTED_COOKING = """
Tutor: Hey! Good to see you. Before we jump into today's lesson, let's rewind to last year for a second. Remember in second grade when you wrote that story about making pancakes with your grandpa on Saturday morning?

Student: Yeah! I wrote about how first we mixed the batter, then it got all bubbly, and then he flipped one and it landed on the floor.

Tutor: Exactly -- and do you remember what kind of words you used to show the order things happened?

Student: Um... "first," "then," "after that"?

Tutor: Right, time-order words! That's a big second-grade skill -- recounting an event with details and using words like "first," "next," and "finally" to show the sequence. You also wrote an informative piece, remember? About why flour is important in baking?

Student: Oh yeah, I said flour makes bread not flat, and I gave like two facts about it.

Tutor: Good memory. That's introducing a topic and developing it with facts and examples. And your opinion piece -- you argued chocolate chip cookies are better than oatmeal cookies.

Student: Because chocolate chips are sweeter and everyone likes them more!

Tutor: Reasons to back up your opinion, nice. You also did some revising last year, with my help, remember when we fixed up your run-on sentence about the mixer?

Student: Yeah you helped me split it into two sentences so it made sense.

Tutor: And we edited together for capitalization and punctuation. So -- that's everything you leveled up last year. Today we're taking every single one of those skills and leveling them up to third-grade versions. Ready?

Student: Ready!

Tutor: First big idea: different types of writing have different shapes. A narrative, an informative piece, and an opinion piece don't look the same on the page or follow the same pattern. Can you guess why?

Student: Because... they're trying to do different things?

Tutor: Exactly -- purpose shapes structure. If I wanted you to tell a story about baking your first cake, what would that look like versus explaining how to bake a cake?

Student: The story would have like, me and what happened, but the explaining one would be more like steps.

Tutor: Perfect instinct. A narrative has characters and events unfolding -- it should feel natural, not just a list. An informative piece develops a topic with facts and details. So let's start with narrative. Last year you recounted the pancake story with time words. This year, I want the events to "unfold naturally" -- meaning it flows like a real story, not just "this happened, then this happened." Try telling me a narrative moment from baking, but make it flow.

Student: Okay... So last weekend I was helping my mom make cupcakes, and I accidentally dumped in way too much vanilla extract, and the whole kitchen smelled so strong we had to open the windows, and my mom just started laughing.

Tutor: That's already unfolding naturally -- one thing led to the next without you forcing "first, then, next" onto every sentence. Do you feel the difference?

Student: Yeah, it kind of just flows because one thing caused the next thing.

Tutor: Exactly right -- that's the third-grade upgrade: cause and flow, not just a checklist of events. Now let's level up informative writing. Last year you gave a couple facts about flour. This year we want to examine a topic more, with facts and details that develop it. Pick a baking topic.

Student: Can I do... why you need to preheat the oven?

Tutor: Great topic. Give me your topic sentence.

Student: "Preheating the oven is important when you bake."

Tutor: Good start. Now develop it -- give me at least two facts or details that explain why.

Student: If the oven isn't hot enough, the cookies spread out flat instead of staying puffy. And if you put the pan in a cold oven, the baking time gets messed up.

Tutor: See how those are actual details, not just "flour is good"? You're examining the topic now, not just mentioning it. Now, opinion writing. Last year: chocolate chip versus oatmeal, with reasons. This year we add facts too. Give me an opinion about baking.

Student: I think baking cookies is more fun than baking bread.

Tutor: Good, now back it up with a reason AND a fact.

Student: A reason is cookies only take like ten minutes to bake, so you don't have to wait as long. And a fact is that bread needs yeast to rise, which takes like an hour or two, so it's a longer process.

Tutor: Excellent -- that fact about yeast makes your opinion piece stronger than just "reasons," because now you've got real information backing you up. Now let's talk about writing in response to something you read or heard. Last year you gave a couple supporting details. This year we want you using supporting details more precisely, tied closely to the text. Let's say you read a short passage about a baker named Alex who forgot to add sugar to a cake. What's your thinking about that?

Student: I think Alex was probably really embarrassed.

Tutor: Good start -- now give me a detail straight from the text that supports that.

Student: The text said Alex's face turned red when the customer took a bite, and Alex said "I'm so sorry" three times.

Tutor: Perfect -- that's pulling directly from the text to support your thinking, which is exactly the third-grade move. Now, here's a new one for this year: writing as a process to compose a well-developed paragraph. Do you know what makes a paragraph "well-developed"?

Student: Is it like... more than just one sentence?

Tutor: Close -- it needs a topic sentence, then supporting sentences with details, and usually a closing sentence that wraps it up. Let's build one about your favorite thing to bake. Give me a topic sentence.

Student: "My favorite thing to bake is banana bread."

Tutor: Nice. Now two or three supporting sentences with details.

Student: It's easy to make because you just mash the bananas and mix everything in one bowl. It also makes the whole house smell really good while it's baking. And you can add chocolate chips or walnuts to make it different every time.

Tutor: Now give me a closing sentence.

Student: "That's why banana bread will always be my favorite thing to bake."

Tutor: That is a genuinely well-developed paragraph -- topic sentence, three supporting details, closing sentence. You just did the whole process in your head. Now let's talk revising. Last year I helped you revise. This year, you're going to get help from me AND from a peer, and we look at quality of ideas, organization, sentence fluency, and word choice. Read me your banana bread paragraph again and let's see if any sentence could sound smoother.

Student: Um, "It also makes the whole house smell really good while it's baking" -- that one feels kind of clunky.

Tutor: What could you change to improve the word choice?

Student: Maybe "It fills the whole house with a warm, sweet smell while it bakes"?

Tutor: That's a big word-choice upgrade -- "warm, sweet smell" is so much more vivid than "smell really good." That's exactly the kind of revision we're aiming for. Last step: editing. Last year we edited together for spelling, capitalization, usage, and punctuation. This year you're also thinking about format. Let's look at a sentence with some mistakes. Here it is: "my mom and i baked Cookies on tuesday and they was delicious"

Student: Okay... "my" should be capitalized because it starts the sentence. And "i" needs to be capital I.

Tutor: Good, keep going.

Student: "Cookies" shouldn't be capitalized because it's not a special name. And "tuesday" should be capitalized because it's a day.

Tutor: Great catches. What about "they was delicious"?

Student: That should be "they were delicious" because "they" is plural.

Tutor: Perfect -- that's usage. And do we need any punctuation at the end?

Student: A period, because it's a statement.

Tutor: Nailed it. So let's recap real quick -- what did we level up today?

Student: We did narrative that flows naturally, informative with more facts, opinion with facts and reasons, responding to text with real details from it, building a whole paragraph, revising for word choice, and editing for capitalization and stuff.

Tutor: That is a complete and accurate list -- you just summarized an entire grade level of writing standards from memory. How do you feel about all of it?

Student: Pretty good, actually. It's kind of like leveling up a recipe -- same basic ingredients, just more of them and done better.

Tutor: That is a fantastic way to put it. Same skills, more sophistication -- exactly like turning a simple recipe into a more advanced one. For homework, I want you to write one well-developed paragraph about any baking topic you like, using everything we practiced today.

Student: Can I write about the time I made macarons and they all cracked?

Tutor: That sounds like a narrative with a lot of natural unfolding potential. Go for it, and bring it next time.

Student: Deal. See you next week!

Tutor: See you next week -- happy baking!
"""

GRADE5_SIGNPOSTED_ROBOTICS = """
Tutor: Hey! Good to see you. Before we jump into today's stuff, let's rewind to last year for a second. Remember in fourth grade when we talked about how narrative, expository, and persuasive writing all have different shapes?

Student: Yeah, kind of. Narrative is like telling a story, expository is like explaining something, and persuasive is trying to convince someone.

Tutor: Exactly right. And do you remember the narrative you wrote about your robot at the regional competition? The one where the wheel motor died right before your run?

Student: Oh yeah! I wrote about how our robot's wheel stopped working and we had like ten minutes to fix it before we got disqualified.

Tutor: That's a great example of what we called a "central problem" -- the whole story organized around one issue, the broken wheel, and how you solved it. That's fourth-grade narrative writing.

Student: I remember you said I needed to organize it -- like beginning, middle, end, not just jumping around.

Tutor: Right. And then there was your expository piece -- the one explaining how a line-following sensor works.

Student: I used facts about infrared light and how the sensor reads dark and light surfaces, and I used linking words like "first," "next," and "because" to connect it all.

Tutor: Perfect memory. And your persuasive piece?

Student: I wrote why our school should let the robotics club use the gym after school. I had an opinion -- "we should get more time" -- and I backed it up with reasons and facts about how little practice time we had.

Tutor: You nailed all of that last year. You also did a great job revising -- remember peer-editing with Marcus, checking capitalization and punctuation on each other's drafts?

Student: Yeah, he caught like five spelling mistakes in my sensor essay.

Tutor: Good. So here's the thing -- this year, in fifth grade, we're not throwing any of that out. We're leveling it up. Everything you just described gets a bit more sophisticated. Ready?

Student: Ready.

Tutor: Let's start with narrative. Last year it was: organize around a central problem. This year, we add two new tools -- descriptions and dialogue -- to actually develop the experience, not just report it. And you can even write it in poetic form if you want.

Student: Wait, poetry? Like a poem about my robot?

Tutor: Sure, why not. Let's try a quick example. Take that broken-wheel story. Instead of just saying "the wheel broke, we were worried, we fixed it," give me a line with dialogue in it.

Student: Um... "Is it dead?" Jake asked, staring at the smoking motor. "Not yet," I said, grabbing the screwdriver.

Tutor: That's fantastic! See how much more alive that is than just saying you were worried? That's dialogue developing the experience. Now give me one line of description -- not action, just describing something.

Student: The motor smelled like burnt plastic and the gears were grinding louder every second.

Tutor: Beautiful -- that's sensory description. That's the fifth-grade upgrade: same central problem structure as last year, but now dialogue and description make the reader feel it instead of just being told it.

Student: Okay, I like that actually. It's more like a movie scene.

Tutor: Exactly the goal. Now let's level up expository writing. Last year: facts, details, linking words. This year, we need facts, concrete details, AND examples from multiple sources, and everything has to be grouped logically -- not just listed randomly.

Student: What counts as "multiple sources"?

Tutor: Good question. If you're writing about how sensors work, last year you might've used just what you remember from class. This year, you'd pull from your robotics textbook, maybe a video you watched, and your own testing notes from club. Three different sources, all backing up the same point.

Student: Oh, so like if I say "infrared sensors detect light contrast," I could cite the club handbook, then also mention what our mentor Mr. Alvarez told us, then also what I tested myself.

Tutor: Exactly. And "grouped logically" means you don't jump from sensors to motors to sensors again. You'd have one paragraph fully about sensors, pulling in all three sources, before moving to motors.

Student: That makes sense. Keep similar ideas together instead of scattering them.

Tutor: Right. Let's practice. Give me a topic sentence for a paragraph about how your robot's claw mechanism works.

Student: "Our robot's claw uses a servo motor to open and close, and understanding this mechanism required research, testing, and help from our club mentor."

Tutor: That's a strong topic sentence -- it already signals multiple sources are coming. Nice work. Now, persuasive writing. Last year: opinion plus facts, details, reasons. This year we add something big -- media messages -- and we need "adequate" facts and reasons, logically grouped.

Student: What's a media message?

Tutor: Think commercials, social media posts, even a flyer -- any message trying to persuade you through media, not just plain text. This year you could analyze one, or make your own persuasive piece that responds to one.

Student: Could I write about that ad I saw for a robotics kit that said "the best kit for every builder"?

Tutor: Perfect example. What would you say persuasively in response?

Student: I could say the ad's claim isn't really true because it doesn't work for advanced builders, and give reasons -- like it doesn't have enough sensor ports, and the instructions are too basic for our club's projects.

Tutor: Excellent -- that's a clear perspective backed by reasons. Now, "logically grouped information" means -- if you also wanted to argue our school should buy better kits, how would you organize that instead of just listing random reasons?

Student: Maybe group all the money reasons together, then all the education reasons together, instead of mixing them up.

Tutor: Exactly. Cost arguments in one cluster, learning-benefit arguments in another. That's the fifth-grade level of organization. Now let's talk about responding to texts you read -- remember doing that with a book last year?

Student: Yeah, we wrote a summary and said what we thought about it.

Tutor: Right, and you used linking words to connect ideas. This year, when you write in response to a text -- summary, reflection, or description -- we want your details, examples, and evidence from the text to be logically grouped, same idea as before.

Student: So if I read that article about robots used in disaster rescue, I shouldn't just throw in random facts wherever I remember them?

Tutor: Right. Let's practice. Give me two facts from that rescue-robot article, but grouped under one idea -- like "robots are useful because they can go places humans can't."

Student: Okay -- the article said robots can fit through collapsed building gaps too small for rescuers, and they can survive heat and smoke that would hurt a person. Those both support that they go places humans can't.

Tutor: That's grouped beautifully -- both facts support the same claim, back to back. That's the skill. Now, writing as a process -- this one's actually the same as last year: we still compose well-developed paragraphs by drafting, revising, editing. No real change there, just keep practicing it.

Student: So that one didn't level up?

Tutor: Not really -- it's a steady skill you keep building every year. But revising did level up a little. Last year we revised for ideas, organization, sentence fluency, and word choice. This year, word choice becomes precise word choice.

Student: What's the difference?

Tutor: Let's find out. Look at this sentence from your claw-mechanism paragraph: "The claw is good at grabbing stuff." What's a more precise way to say "good at grabbing stuff"?

Student: Um... "The claw grips small objects firmly without dropping them"?

Tutor: That's so much better -- "firmly" and "without dropping them" are precise instead of vague. That's exactly the fifth-grade revising skill: swapping vague words for exact, specific ones.

Student: Precise word choice. Got it.

Tutor: Last piece -- editing. Last year you edited for capitalization, spelling, punctuation, sentence structure, paragraphing, and Standard English. This year it's basically the same list, but now it's sentence structures, plural -- meaning you check for variety, not just correctness.

Student: Variety, like not every sentence starting the same way?

Tutor: Exactly. Look at this from your draft: "The robot moved forward. The robot turned left. The robot stopped." What's repetitive there?

Student: They all start with "The robot" and they're all short and choppy.

Tutor: Right, so how could you combine or vary them?

Student: "The robot moved forward, turned left, and then stopped."

Tutor: Perfect -- one varied sentence instead of three identical ones. That's editing for sentence structures at the fifth-grade level.

Student: This is a lot of upgrades, but it actually all connects to what we already knew.

Tutor: That's exactly the point -- nothing from fourth grade gets thrown away, it just gets sharper. Let's do a full practice round. Write me one paragraph, narrative style, about your robotics club, using at least one line of dialogue and one line of description.

Student: Okay... "Do you smell that?" Priya said, wrinkling her nose. The burnt-plastic smell hung over the workbench like a warning. I unscrewed the motor housing with shaking hands, hoping we hadn't fried the whole board.

Tutor: That is genuinely great -- dialogue, sensory description, and a clear central problem. Now flip it -- give me one expository sentence about that same motor, using a fact from a source.

Student: "According to our club's repair manual, overheated motors often smell like burnt plastic before they fail completely."

Tutor: Nice, that's a cited fact grounding the story. Now a persuasive sentence -- maybe arguing the club needs a spare-parts budget because of moments like that.

Student: "Our club should have a spare-parts budget because losing a motor mid-competition, like ours almost did, can end a team's chances in seconds."

Tutor: That's a clear perspective with a solid reason. You're hitting every piece today -- narrative with dialogue and description, expository with sourced facts grouped logically, persuasive with grouped reasons, and precise revising. How are you feeling about all this?

Student: Honestly pretty good. It feels like leveling up a character in a game -- same skills, just stronger versions.

Tutor: That's exactly the right way to think about it. For homework, I want you to take your rescue-robot article response and reorganize it so all your evidence is grouped by idea, then revise one paragraph for precise word choice.

Student: Can I use the fire-and-smoke example and the tight-gap example again?

Tutor: Yes, group those two together since they support the same point, just like we practiced. Anything else feel unclear before we wrap up?

Student: No, I think I've got it. Central problem plus dialogue and description for narrative, multiple sources grouped logically for expository, media messages and grouped reasons for persuasive, grouped evidence for text responses, and precise word choice plus varied sentence structures when I edit.

Tutor: That's a complete, accurate summary of everything we covered. Great session today -- same great writer, just building sharper tools.
"""

GRADE8_SIGNPOSTED_PHOTOGRAPHY = """
Tutor: Alright, before we jump into today's stuff, let's rewind to seventh grade for a second. Remember that narrative you wrote about getting locked out during your cousin's birthday party?

Student: Oh yeah, the one where I had to use flashback to explain how we even got locked out in the first place.

Tutor: Right -- you used transitional phrases like "earlier that afternoon" to signal the shift back in time. That was solid seventh-grade work: varying your word choice, using transitions to move between timeframes. You also did that expository piece on how cameras capture light, remember?

Student: Yeah, I compared pinhole cameras to digital sensors. I used a comparison structure for that one.

Tutor: Exactly -- you picked a structure, comparison, and used it to organize facts from a couple of sources. And then there was the persuasive essay arguing your school should have a photography club.

Student: I had three reasons and I grouped them logically, like, "here's why it's good for creativity," then "here's why it's good for college applications."

Tutor: Good memory. You also did a reflective piece on a memoir you read, and you went through the whole writing process -- draft, revise, edit -- for a longer paper. And you and Marcus peer-edited each other's stuff for punctuation and sentence structure.

Student: I remember that. He caught like five comma splices in my draft.

Tutor: Well, this year we're leveling all of that up. Same skills, but eighth grade asks you to go deeper -- more well-chosen evidence, more well-structured sequences, evidence that actually advances your argument instead of just sitting there. Let's start with narrative. Say you're writing about the moment you got your first good photo published somewhere -- a real event. What's different about "well-structured event sequences" versus just "convey sequence," which is what you did last year?

Student: I guess... sequence just means put things in order? But structured means like, build it on purpose -- maybe don't just go start to finish, decide where the tension is?

Tutor: Yes! It's about deliberately shaping the sequence for effect, not just chronology. And this year we also want you to "capture the action" -- vivid, precise verbs and sensory detail in the moment itself. So instead of "I took the photo," what's more precise?

Student: "I crouched low, held my breath, and fired the shutter just as the hawk broke from the branch."

Tutor: That's capturing the action. Notice how much more alive that is. Now let's do expository. Last year you compared pinhole cameras and digital sensors using facts from a couple sources. This year, the standard wants "relevant, well-chosen facts, definitions, concrete details, quotations, and examples from multiple credible sources." What would you add to that old essay to hit the grade 8 bar?

Student: Maybe an actual quote from a photographer or an engineer, not just facts I found?

Tutor: Exactly -- a direct quotation adds authority and voice. What's a structure you could use to reorganize that essay so the relationships between ideas are clearer?

Student: Cause-effect? Like, "because sensors work this way, digital cameras can shoot in low light better than film"?

Tutor: Perfect example of cause-effect clarifying a relationship. Now let's talk persuasive writing. Last year you argued for a photography club with three logically grouped reasons. This year the standard says your evidence has to "logically advance the claim" -- meaning each piece of evidence needs to build on the last, not just sit in a pile. Let's practice. Your claim: "Aspiring photographers should learn manual mode before relying on auto settings." Give me your first piece of evidence.

Student: Manual mode teaches you how aperture, shutter speed, and ISO actually interact.

Tutor: Good. Now give me a second piece of evidence that builds on that one -- advances the claim rather than just adding another fact.

Student: Um... since you understand how they interact, you can fix a bad photo on the spot instead of hoping auto mode guesses right?

Tutor: That's it -- that logically advances from "you understand the relationship" to "therefore you can act on it in the moment." That's a step up from last year's just grouping claims together. Now, reasoning -- walk me through why that evidence actually supports your claim, out loud.

Student: Okay, so... if manual mode teaches the relationship between settings, and understanding that relationship lets you fix problems instantly, then learning manual mode makes you a more capable photographer overall, which is why it should come before relying on auto.

Tutor: Beautiful chain of reasoning. That's exactly the "clear reasoning" piece. Let's shift to reflective writing -- this one's actually unchanged from seventh grade, but it's worth practicing since it comes up on the writing SOL every year. Tell me about a photography book or article you've read recently.

Student: I read an interview with Annie Leibovitz about portrait lighting.

Tutor: Good. If you were writing reflectively about that, what's a detail from the text you'd use as evidence for your thinking?

Student: She said she studies her subject's face for ten minutes before ever touching the camera. I could reflect on how that changed how I think about rushing my own shots.

Tutor: That's exactly it -- using a specific detail from the text to demonstrate your thinking, not just summarizing what she said. Now, the writing process. You know the stages -- planning, drafting, revising, editing. For a multi-paragraph piece on, say, editing photos ethically, what would planning look like for you specifically?

Student: Maybe an outline -- one paragraph on cropping, one on color correction, one on where it crosses into misleading?

Tutor: Good structure. And remember, the process doesn't stop at drafting. Let's talk revision, since that standard is also unchanged but still critical. Say you've got this sentence in your draft: "Editing photos is something a lot of photographers do and it can be good or bad depending on how you do it." What's weak about that, in terms of clarity and word choice?

Student: It's really vague. "A lot of photographers" and "good or bad" don't say anything specific.

Tutor: Right. Revise it for me.

Student: "Editing walks a fine line: subtle color correction restores what the eye actually saw, while heavy retouching can quietly mislead the viewer."

Tutor: Huge improvement -- much more precise word choice and it actually says something. Now think about sentence variety. If every sentence in your paragraph started with "Editing..." what would you do?

Student: Combine some sentences, maybe start one with a dependent clause instead, like "Although editing can restore realism, it can also distort it."

Tutor: Exactly right. And what about transitions between paragraphs -- if your first paragraph is about cropping and the second is about color correction, how do you bridge them instead of just stopping and starting a new topic?

Student: Maybe end the cropping paragraph by saying something like, "But framing isn't the only choice that shapes a photo's story," and then start the next one talking about color.

Tutor: That's a strong transitional bridge. Last piece -- self- and peer-editing. Also unchanged from last year, but let's make sure it's solid. If you swapped that ethics essay with a partner, what are you checking for?

Student: Capitalization, spelling, punctuation, run-ons or fragments, paragraph breaks, and just... standard grammar stuff.

Tutor: Perfect list. Let's do a quick drill -- I'll give you a sentence with an error, you fix it. "my camera which i bought last summer takes better low light photos then my old one."

Student: "My camera, which I bought last summer, takes better low-light photos than my old one."

Tutor: Nice catch on "then" versus "than," plus the capitalization and the missing commas around the clause. One more: "The lens was expensive, but it takes stunning photos, I use it for every shoot."

Student: That's a comma splice. "The lens was expensive, but it takes stunning photos. I use it for every shoot."

Tutor: Exactly right. So let's zoom out -- today we took every skill from last year and pushed it further: narrative sequencing got more deliberate and action-focused, expository writing now demands quotations and multiple credible sources, and persuasive evidence has to actually build toward the claim instead of just being grouped. Reflective writing, the writing process, revision, and editing are the same expectations as last year, just at a higher stakes level since your paragraphs are getting longer and more complex.

Student: So basically, same skills, just sharper.

Tutor: That's the whole idea of eighth grade. For homework, take that photography ethics outline we planned and draft the first two paragraphs -- I want to see well-chosen evidence, at least one quotation, and a transition sentence bridging them.

Student: Can I use that quote from the Leibovitz interview somewhere too?

Tutor: If it fits naturally and supports your point, absolutely -- that's exactly the kind of well-chosen evidence we're after. Bring your draft next time and we'll revise it together.

Student: Sounds good. I'll work on the transition sentences too since those always trip me up.

Tutor: That's a great thing to focus on. See you next week.
"""

GRADE6_UNSIGNPOSTED_GARDENING = """
Tutor: Today let's dig into a few different kinds of writing you'll build this week. We'll do narrative, expository, persuasive, and reflective writing -- and since you're into gardening, we'll use that as our material. Sound good?

Student: Sure. Which one first?

Tutor: Let's start with narrative. A narrative shares a personal experience or tells a story, and it uses techniques like dialogue, description, and pacing to develop the characters and events. Tell me about something that happened in your garden that you remember clearly.

Student: Um, one time a rabbit ate all my lettuce.

Tutor: Good start -- now make it a scene. What did you see when you first noticed?

Student: I walked outside and the lettuce bed was just... stems. No leaves.

Tutor: That's a strong detail. Add how you felt and maybe a line of dialogue -- did you tell anyone?

Student: I could write: "I stared at the ragged stumps where my lettuce used to be. 'It's gone,' I said to my dad. 'All of it.'"

Tutor: Excellent -- see how the dialogue and the sensory detail "ragged stumps" pull the reader into the moment instead of just telling us a rabbit ate the lettuce?

Student: Yeah, it feels more like a story now.

Tutor: Exactly. Now let's shift to expository writing. This is where you examine a topic and convey information logically, using structures like description, comparison, or cause-effect. If you were explaining composting, which structure would fit best?

Student: Maybe cause-effect? Like, you add scraps, and then effect is it becomes soil?

Tutor: Good instinct. Try a sentence showing that cause-effect chain.

Student: "When you layer food scraps and dry leaves in a compost bin, microorganisms break them down, which causes the pile to heat up and eventually turn into rich soil."

Tutor: That's a clean cause-effect sentence. What if you wanted to explain the difference between compost and mulch instead?

Student: Then I'd use comparison, like, compost feeds the soil but mulch just covers it.

Tutor: Right -- you're matching the structure to your purpose, which is exactly what expository writing asks you to do. Now, persuasive writing. Here you support a well-defined claim with clear reasons and evidence, and those reasons need to be logically grouped. Give me a claim about gardening you actually believe.

Student: Everyone should grow at least one vegetable at home.

Tutor: Good claim. What's your first reason?

Student: It saves money on groceries?

Tutor: Good -- now what evidence backs that up?

Student: I guess I could say a packet of tomato seeds costs like three dollars but grows way more tomatoes than that would buy at the store.

Tutor: Perfect, that's concrete evidence. What's a second, different reason -- not just another money point?

Student: It's better for the environment because you're not using packaging or trucks to ship it.

Tutor: Good, now those are two separate reasons -- money and environment. How would you group them so the essay doesn't feel scattered?

Student: I could do one paragraph just about money, then a whole paragraph just about the environment, instead of mixing them together.

Tutor: Exactly -- logically grouped means each reason gets its own space with its own evidence. Now let's talk about media messages, since persuasive writing includes responding to those too. Have you seen an ad or a sign trying to persuade people about gardening?

Student: There's a seed company that says "Grow Your Own Food, Save the Planet" on their packets.

Tutor: What's the claim there, and is it fully supported just by the slogan?

Student: The claim is that gardening helps the planet, but the packet doesn't actually give evidence, it's just a catchy phrase.

Tutor: Right -- that's an important thing to notice: a media message can state a claim without reasons or evidence, which is different from what you just did with your tomato paragraph.

Student: So I did it better than the seed packet.

Tutor: You did. Now let's try reflective writing. This is where you respond to something you've read and show your thinking with details and evidence from the text. Have you read anything about gardening recently?

Student: We read that article about drought-tolerant plants in class.

Tutor: Good. Write a reflective sentence that uses a specific detail from that article.

Student: "The article said succulents store water in their leaves, which made me think about why my cactus survived when I forgot to water it for three weeks."

Tutor: That's a strong reflection -- you pulled a specific detail from the text and connected it to your own thinking. That's exactly what reflective writing asks for.

Student: It felt more personal than just summarizing the article.

Tutor: That's the difference between summary and reflection. Now, before you write any full piece, we use the writing process -- planning, drafting, revising, editing. Let's say you're planning that persuasive essay about growing your own vegetables. What would planning look like?

Student: Maybe jotting down my reasons first, like a list -- money, environment, taste?

Tutor: Good, and how would you organize a multi-paragraph structure from that list?

Student: Intro paragraph with my claim, then one paragraph per reason, then a conclusion.

Tutor: That's a solid plan. After you draft it, we revise. Revising is about clarity, word choice, sentence variety, and transitions between paragraphs -- not fixing commas yet. Let's look at this draft sentence: "Gardening is good. It is good for you. It saves money too." What's the problem?

Student: It's really choppy. Every sentence is short and starts the same way.

Tutor: Right, so how could you combine them and vary the sentence length?

Student: "Gardening benefits both your health and your wallet, since growing your own food saves money while also getting you outside and active."

Tutor: Much better -- one longer sentence with variety, instead of three short, repetitive ones. Now what about word choice -- "good" is pretty vague. What's a stronger word for the health part?

Student: Maybe "beneficial" or "rewarding"?

Tutor: Good options. Now, transitions -- if your next paragraph moves from the money reason to the environment reason, what transition word could bridge them?

Student: "In addition to saving money, gardening also helps the environment."

Tutor: Perfect, that connects the two ideas smoothly instead of just jumping to a new paragraph. Now, once revising is done, we move to editing -- and this is where self- and peer-editing come in, checking capitalization, spelling, punctuation, sentence structure, paragraphing, and standard English. Let's edit this sentence together: "my tomato plants are Taller then my sunflowers this year"

Student: "My" needs a capital letter since it starts the sentence. And "Taller" shouldn't be capitalized in the middle.

Tutor: Good catch on both. What about "then"?

Student: Oh, it should be "than" because we're comparing things, not talking about time.

Tutor: Exactly -- "than" for comparison, "then" for sequence. Nice fix. One more: "the garden club meet on Tuesdays we grow herbs and vegetables."

Student: That's a run-on -- it needs to be two sentences. "The garden club meets on Tuesdays. We grow herbs and vegetables."

Tutor: And you fixed subject-verb agreement too -- "meet" to "meets." Well done. When you peer-edit a partner's paragraph, what are you scanning for, in order?

Student: I guess first if the sentences make sense and aren't run-on or fragments, then spelling and punctuation, then capitalization.

Tutor: That's a reasonable approach -- some people do capitalization and punctuation first since those are quick to spot, then move to sentence structure. Either way works as long as you check all of them. Let's also check paragraphing -- should your money reason and environment reason be in the same paragraph or separate ones?

Student: Separate, since we said each reason gets its own paragraph.

Tutor: Right. So if you saw a paragraph that jumped from money straight into environment without a break, what would you do?

Student: Start a new paragraph right where the topic shifts, and add a transition sentence.

Tutor: Exactly. Let's put it all together now -- for homework, I want you to draft a short persuasive piece about home gardening, run it through planning, drafting, revising, and editing, and bring it back so we can peer-edit it together.

Student: Can I also try adding a narrative moment in the intro, like the rabbit story, to hook the reader?

Tutor: That's a great idea -- opening a persuasive piece with a brief narrative anecdote is a strong technique, as long as you connect it back to your claim quickly.

Student: Okay, I'll start with the lettuce disaster and then pivot to why people should still garden anyway.

Tutor: I love that. Bring your draft next time and we'll revise and edit it together, checking clarity, word choice, transitions, and all our editing basics.

Student: Sounds good -- I'm actually excited to write about the rabbit now.

Tutor: That's the goal -- turning something real from your own experience into writing that actually works on a reader. See you next time.
"""

GRADE4_STANDALONE_BASKETBALL = """
Tutor: Today we're going to work on writing skills. Before we start, tell me -- do you know a basketball player or team you could write a story about?

Student: Yeah! I could write about the time my team won our tournament game at the buzzer.

Tutor: Perfect. That's a personal narrative. Before we write it, let's talk about something important: different kinds of writing are built differently depending on what they're trying to do. If I'm telling a story, what does that writing need?

Student: Um... a beginning, middle, and end?

Tutor: Exactly -- and usually it's built around one main problem or experience, like your team being down by two points with ten seconds left. What if instead I wanted to explain how basketball scoring works?

Student: That would be different. I'd need facts, like a free throw is one point and a three-pointer is three points.

Tutor: Right, that's expository writing -- it explains a topic using facts and details. And what if I wanted to convince someone that basketball is the best sport to play?

Student: I'd need to give reasons why, like it builds teamwork and it's good exercise.

Tutor: That's persuasive writing -- it states an opinion and backs it up. Three different jobs, three different shapes. Let's start with your narrative about the buzzer-beater. What was the central problem in that story?

Student: We were losing by two points and almost ran out of time.

Tutor: Good, that's your central problem. Now walk me through it in order -- what happened first?

Student: Our coach called a timeout with fifteen seconds left and drew up a play for me to get the ball near the three-point line.

Tutor: Then what?

Student: The point guard passed it to me, I had a defender right in my face, and I had to decide fast.

Tutor: And the ending?

Student: I pump-faked, he jumped, and I shot right over him. It went in as the buzzer sounded!

Tutor: That's a great logically organized narrative -- problem, action, resolution. Now let's try expository writing. Pick a basketball topic to explain.

Student: How about how to shoot a free throw?

Tutor: Good topic. Give me one fact or detail to start.

Student: You have to line your feet up with the middle of the hoop.

Tutor: Good, now give me another detail and connect it with a linking word like "next" or "then."

Student: Next, you bend your knees and bring the ball up in one smooth motion.

Tutor: Nice use of "next" to connect your ideas. One more detail?

Student: Finally, you follow through by snapping your wrist forward.

Tutor: See how "finally" ties that last idea to the others? That's exactly how expository writing stays connected. Now let's try persuasive writing. What's an opinion you have about basketball?

Student: I think kids should play team sports like basketball instead of only playing video games.

Tutor: Strong opinion. What's a reason to support it?

Student: Because basketball teaches you to work with other people.

Tutor: Good -- can you add a detail or fact to back that up?

Student: When you're on a team, you have to pass the ball and trust your teammates, or you won't win games.

Tutor: That's a solid reason with a detail attached. What's another reason?

Student: It's also good exercise, so it keeps your body healthy.

Tutor: Great, now you've got an opinion with two supported reasons -- that's a real persuasive piece. Let's shift gears. Suppose you just read an article about a famous basketball player. What kind of writing would you do to respond to it?

Student: I could write a summary or say what I thought about it.

Tutor: Right -- summary, reflection, or description. If you were writing a reflection, what would you include?

Student: My own thinking about the article, plus examples from what I read.

Tutor: And how would you connect those ideas smoothly?

Student: With linking words, like "for example" or "because."

Tutor: Exactly. Let's say the article said the player practiced free throws for an hour every day. How would you respond to that using a linking word?

Student: I admire his dedication because practicing for an hour every day shows real discipline.

Tutor: That's a well-connected response using evidence from the text. Now, writing is a process -- it's not just one draft and done. What do you think the first step is?

Student: Coming up with ideas, like brainstorming?

Tutor: Right, and after brainstorming?

Student: Writing a draft.

Tutor: Then?

Student: Fixing it up -- making it better.

Tutor: That's revising. Let's revise your buzzer-beater narrative together. Read me your first sentence again.

Student: "I got the ball and shot it."

Tutor: That tells me what happened, but not how it felt. Can you add stronger word choice or a detail about the moment?

Student: "My hands were shaking as I caught the pass with the clock ticking down."

Tutor: Much better -- that improves your word choice and pulls the reader into the moment. Now look at your sentences. Are they all the same length and pattern?

Student: Kind of. They all start with "I."

Tutor: Let's fix your sentence fluency by varying that. Try starting one differently.

Student: "With ten seconds left, I caught the pass."

Tutor: Perfect, that's much smoother. Now, when we revise, is that something you do completely alone?

Student: No, I can ask a friend or my teacher for help too.

Tutor: Exactly, guidance from others helps strengthen the ideas and organization too. Now let's edit -- that's different from revising. What kinds of things do we check for when we edit?

Student: Spelling and punctuation?

Tutor: Yes, and what else?

Student: Capital letters, and making sure sentences aren't run-on or fragments.

Tutor: Right, and paragraphing too. Let's check your paragraph. Did you start a new paragraph when the topic shifted?

Student: I don't think so, I just kept going in one big block.

Tutor: Let's mark where a new idea starts -- right where the coach draws up the play would be a good new paragraph.

Student: Okay, I'll break it there.

Tutor: Now read this sentence and tell me what's wrong: "my coach called a timeout."

Student: It should start with a capital "M" since it's the beginning of the sentence.

Tutor: Exactly. And is "timeout" spelled correctly there?

Student: I think so -- t-i-m-e-o-u-t.

Tutor: That's right. Let's also swap roles -- I'll read your persuasive piece and you edit mine. Here's my sentence: "basketball are a fun sport and it help kids stay fit."

Student: "Basketball" needs a capital letter, and it should say "basketball is a fun sport" and "it helps kids stay fit."

Tutor: Excellent catch on subject-verb agreement and capitalization. That's exactly the kind of peer editing that makes writing stronger. So today we practiced telling stories with a clear problem, explaining topics with connected facts, persuading with reasons, responding to what we read with evidence, and then revising and editing our work. Which part felt most useful to you?

Student: I liked fixing my sentences so they didn't all sound the same and start with "I."

Tutor: That's a great skill to keep using. Want to finish polishing your buzzer-beater narrative for next time?

Student: Yes, I want to make the ending even more exciting.
"""

OFFDOMAIN_FRACTIONS_BAKING = """
Tutor: Hey! I heard you've been baking a lot lately. What have you made recently?

Student: I made cookies last weekend, but I messed up when I tried to make a bigger batch.

Tutor: Perfect, that's actually exactly what we're going to work on today -- fractions and decimals, using baking the whole way through. What went wrong with the batch?

Student: The recipe called for 1/3 cup of sugar and I wanted to double it, but then it also needed 1/4 cup of butter and I didn't know how to combine them.

Tutor: Right, so let's start there. If you double 1/3 cup, what do you get?

Student: 2/3 cup?

Tutor: Exactly -- you just multiply the numerator, the top number, by 2. Denominator stays the same since you're still talking about thirds. Now, here's the harder part: let's say a recipe needs 1/3 cup of sugar and 1/4 cup of brown sugar, and you want to know the total amount of sugar. Can you just add 1/3 + 1/4 directly?

Student: I don't think so, because the bottom numbers are different?

Tutor: Right -- you can't add fractions unless the denominators match. Thirds and fourths are different-sized pieces, like comparing a measuring cup marked in thirds to one marked in fourths. So what do we need to do first?

Student: Find a common denominator?

Tutor: Yes. What's a number that both 3 and 4 divide into evenly?

Student: 12?

Tutor: Perfect. So we rewrite both fractions with denominator 12. What does 1/3 become?

Student: Um... 4/12?

Tutor: Right, because 3 times 4 is 12, so we multiply the top by 4 too: 1 times 4 is 4. Now what does 1/4 become?

Student: 3/12, since 4 times 3 is 12, so 1 times 3 is 3.

Tutor: Exactly. Now add them.

Student: 4/12 + 3/12 = 7/12.

Tutor: You've got 7/12 cup of sugar total. Nice work. Now let's try subtraction, since that comes up in baking too. Say your recipe wants 3/4 cup of flour, but you already added 1/2 cup and want to know how much more to add.

Student: So I need 3/4 minus 1/2?

Tutor: Right. Same rule applies -- need a common denominator first. What works for 4 and 2?

Student: 4, since 2 goes into 4.

Tutor: Good instinct -- you don't always need to multiply both denominators together, just find the smallest shared one. So rewrite 1/2 with a denominator of 4.

Student: 2/4.

Tutor: Now subtract.

Student: 3/4 minus 2/4 is 1/4.

Tutor: So you still need to add 1/4 cup of flour. Now let's talk about comparing fractions, which is useful when you're deciding which ingredient amount is bigger. Which is more flour, 2/3 cup or 3/5 cup?

Student: I'm not sure, they don't look easy to compare.

Tutor: That's the point -- different denominators, so we need a common one. What number do 3 and 5 both go into?

Student: 15.

Tutor: Convert both. What's 2/3 as fifteenths?

Student: 3 times 5 is 15, so multiply top by 5 too... 10/15.

Tutor: And 3/5?

Student: 5 times 3 is 15, so 3 times 3 is 9. So 9/15.

Tutor: Now compare 10/15 and 9/15 -- which is bigger?

Student: 10/15, so 2/3 cup is more than 3/5 cup.

Tutor: Exactly right. Now let's shift to decimals, since a lot of kitchen scales show weight in decimals instead of fractions. If a recipe says you need 0.75 cups of milk, what fraction is that?

Student: Isn't that three-fourths?

Tutor: How'd you know that?

Student: We measure with quarter cups a lot, and 0.75 always shows up as three of the four lines.

Tutor: That's a great practical way to remember it. Let's build the rule though: 0.75 means 75 hundredths, or 75/100. How do we simplify that?

Student: Divide top and bottom by 25?

Tutor: Try it.

Student: 75 divided by 25 is 3, and 100 divided by 25 is 4. So 3/4.

Tutor: Nice. Now let's go the other direction -- turning a fraction into a decimal. If your recipe calls for 1/4 cup of cocoa powder, how do we write that as a decimal?

Student: Divide 1 by 4?

Tutor: Yes, exactly -- a fraction is just division. What's 1 divided by 4?

Student: 0.25.

Tutor: Right. Now here's a trickier one: what's 1/3 as a decimal?

Student: 1 divided by 3... 0.33?

Tutor: Close -- try dividing further. What happens?

Student: It keeps going, 0.333...

Tutor: Right, it repeats forever, so we usually round it, like 0.33. That matters in baking -- if a recipe says 1/3 cup and your scale only shows decimals, you'd enter about 0.33, understanding it's not perfectly exact. Now let's combine everything. Say you're scaling a cake recipe down to two-thirds size. The original recipe needs 3/4 cup of sugar. How much sugar do you need for the smaller batch?

Student: I multiply 3/4 by 2/3?

Tutor: Yes. How do we multiply fractions?

Student: Multiply the tops together and the bottoms together?

Tutor: Right. So what's 3 times 2?

Student: 6.

Tutor: And 4 times 3?

Student: 12. So 6/12.

Tutor: Can that be simplified?

Student: Divide by 6... 1/2.

Tutor: So you'd need 1/2 cup of sugar. Let's check that as a decimal too -- what's 1/2 as a decimal?

Student: 0.5.

Tutor: Good. Now one more scenario: you're comparing two brands of chocolate chips. One bag says it's 0.6 pure cacao, the other says 5/8. Which has more cacao?

Student: I should probably turn 5/8 into a decimal to compare easily?

Tutor: That's a smart approach. What's 5 divided by 8?

Student: Let me think... 0.625?

Tutor: Check that with long division if you want, but yes, 5/8 equals 0.625. So compare 0.6 and 0.625 -- which is bigger?

Student: 0.625, so the second bag has more cacao.

Tutor: Exactly. Let's do one final challenge that combines addition and decimals. If you use 0.5 cup of butter and 1/4 cup more, how much total, and can you express it as a fraction?

Student: 0.5 is the same as 1/2, so 1/2 plus 1/4. Common denominator is 4, so 2/4 plus 1/4 is 3/4.

Tutor: Exactly, 3/4 cup, or as a decimal?

Student: 0.75.

Tutor: You've now added, subtracted, and compared fractions with unlike denominators, and converted both directions between fractions and decimals. How are you feeling about doubling that cookie recipe now?

Student: A lot better -- I think I actually could have fixed my batch if I'd known common denominators earlier.

Tutor: That's the whole point. Next time you bake, try scaling a recipe up by 1.5 and see if you can predict each ingredient amount before you measure.

Student: I'll try that with brownies this weekend.

Tutor: Sounds great. Bring back the numbers next time and we'll check your math against your batter.
"""


def test_grade3_signposted_cooking_correctly_recovers():
    """CORRECT RECOVERY: intended taught=3.W, assumed=(2.W,) via explicit
    "remember in second grade" signposting. Measured: matches exactly."""
    result = recover_from_lesson_text(GRADE3_SIGNPOSTED_COOKING, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:3.W"
    assert result.assumed_prerequisite_ids == ("va-writing-sol:2.W",)


def test_grade5_signposted_robotics_correctly_recovers():
    """CORRECT RECOVERY: intended taught=5.W, assumed=(4.W,) via explicit
    "remember in fourth grade" signposting. Measured: matches exactly."""
    result = recover_from_lesson_text(GRADE5_SIGNPOSTED_ROBOTICS, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:5.W"
    assert result.assumed_prerequisite_ids == ("va-writing-sol:4.W",)


def test_grade8_signposted_photography_safely_abstains():
    """SAFE ABSTENTION (a miss, not a wrong answer): intended taught=8.W,
    assumed=(7.W,). 8.W is the raw top scorer (29 vs 7.W's 27) but at this
    bare-minimum margin (2), teach-cpg's fix compares coverage: 8.W covers
    52% of its own vocabulary, 7.W covers 54% -- 7.W is proportionally
    slightly better covered, so the gate fires and the module declines
    rather than guess. This suppresses a genuinely correct recovery; see
    this file's module docstring for why that's reported honestly rather
    than treated as a pure success."""
    result = recover_from_lesson_text(GRADE8_SIGNPOSTED_PHOTOGRAPHY, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "leads" in result.abstain_reason.lower() or "coverage" in result.abstain_reason.lower() or "bare-minimum" in result.abstain_reason.lower()


# XFAIL, and strict on purpose. This test PASSES when the confident-wrong-answer
# bug is PRESENT (it asserts recovery returns 7.W). It currently fails because
# the behaviour improved to a safe abstention. So:
#   XFAIL = the bug is gone. XPASS = the bug came BACK.
# With pytest's default strict=False an XPASS is reported and the build stays
# green -- which would let a regression to a confident wrong answer, the worst
# failure mode this repo has, pass CI unnoticed. strict=True makes that loud.
# raises=AssertionError keeps an ImportError or TypeError from being silently
# absorbed as "expected".
#
# Do NOT resolve this by flipping the assertion to the desired outcome. Per this
# lineage's standing rule (teach-cpg, teach-i35, teach-t7j) the improvement must
# be measured by a fresh round authored with no repo access before teach-i35 can
# be called fixed; GRADE6_UNSIGNPOSTED_GARDENING is already tuning data twice
# over and cannot serve as its own evidence.
@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="teach-i35 domain generalization boundary, requires no-repo-access round",
)
def test_grade6_unsignposted_gardening_is_a_confident_wrong_answer():
    """CONFIDENT WRONG ANSWER: intended taught=6.W, no prerequisite claim
    expected (nothing signposted). Actually recovers taught=7.W with
    unsignposted_prerequisite_ids=('va-writing-sol:6.W',) -- the correct
    answer relegated to a "prerequisite" of the wrong one.

    THIS IS THE FINDING THAT MATTERS in this round. teach-cpg's fix
    protects the raw exact-word tier correctly here (verified separately:
    the raw tier abstains, comparing 7.W's 40% coverage against the true
    rival 6.W's 56.25%, exactly as designed). But the raw tier abstaining
    means recover_taught_concept falls through to the semantic (WordNet)
    fallback tier, which computes its own independently-ranked candidate
    list where 8.W and 11.W's WordNet-expanded scores outrank 6.W, pushing
    6.W out of the `candidates[1]` slot teach-cpg's fix actually inspects.
    The gate then compares 7.W's coverage against 8.W's (not 6.W's), finds
    no problem, and confidently returns 7.W. See this file's module
    docstring for exact scores. Filed as teach-i35, discovered-from
    teach-cpg. THIS TEST ASSERTS CURRENT (BUGGY) BEHAVIOR ON PURPOSE, same
    discipline as this lineage's prior rounds -- do not flip it to the
    desired outcome without a fresh held-out round showing a future fix to
    teach-i35 actually generalizes."""
    result = recover_from_lesson_text(GRADE6_UNSIGNPOSTED_GARDENING, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:7.W", (
        f"if this now correctly recovers va-writing-sol:6.W or safely abstains, "
        f"teach-i35 may have been fixed -- got {result.taught_node_id!r}; "
        f"re-verify against a fresh held-out round before declaring it closed"
    )
    assert result.unsignposted_prerequisite_ids == ("va-writing-sol:6.W",)


def test_grade4_standalone_basketball_correctly_recovers():
    """CORRECT RECOVERY: intended taught=4.W, standalone (no signposting
    in the text). Measured: taught_node_id matches. The module also
    reports unsignposted_prerequisite_ids=('va-writing-sol:3.W',), which
    this file's module docstring discusses as a secondary observation, not
    a pass/fail criterion for this test -- recover_unsignposted_prerequisites
    is a different function than the one teach-cpg's fix touches."""
    result = recover_from_lesson_text(GRADE4_STANDALONE_BASKETBALL, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:4.W"


def test_offdomain_fractions_baking_safely_abstains():
    """SAFE ABSTENTION: pure math content (fractions, decimals), no
    writing-domain vocabulary at all. Correctly ambiguous/no-signal rather
    than a false-positive writing-domain match."""
    result = recover_from_lesson_text(OFFDOMAIN_FRACTIONS_BAKING, WRITING_GRAPH)
    assert result.taught_node_id is None
