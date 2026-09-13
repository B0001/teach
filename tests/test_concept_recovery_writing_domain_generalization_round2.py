"""teach-8xw.53: SECOND held-out generalization round for concept_recovery.py
against the VA Writing SOL K-12 graph, run by a session that did NOT write
teach-l7u's fix (the coverage-tiebreak gate, `_MIN_WINNING_COVERAGE`).

teach-l7u fixed concept_recovery.py's two confident-wrong-answer holes (a
semantic-tier document-frequency gap, and a raw-tier bare-minimum-margin win
with no floor on the winner's own coverage) against its own three
reproduction cases, all three of which live in
tests/test_concept_recovery_writing_domain_generalization.py (round 1,
teach-25s). Per sandbox-prompt.md's "you cannot hold out examples from
yourself", that round-1 set is tuning data for the fix -- it is guaranteed to
pass and proves nothing about generalization. teach-l7u closed itself
honestly on that basis and filed this bead (teach-8xw.53) as the required
follow-up: a THIRD, independently-authored round, generated after the fix
was already committed, by agents with no repository access and no knowledge
of this module, its thresholds, or either bead's history.

WHERE THIS TEXT CAME FROM

Eight lesson dialogues below were each produced by a separate `Agent` tool
call (same method as round 1's teach-8xw.33 precedent). Each agent call was
given an explicit no-tool-use, no-repository-access instruction and was told
nothing about concept_recovery.py's existence, scoring mechanism, thresholds,
or this bead's history -- only plain-English curriculum content (itself
paraphrased by this bead's session from the real VA Writing SOL leaf-standard
text in teach/data/va_writing_sol_k12.json, with an explicit instruction to
each agent not to copy any list verbatim but to render it as natural
tutor/student dialogue). Every one of the eight agents was independent: none
saw another's output, this module's code, or round 1's fixtures. Full
transcripts are reproduced verbatim below (not summarized in prose) per
teach-8xw.40's correction of teach-8xw.33 -- only text actually committed as
runnable data can be re-measured by a future worker.

Grades were deliberately chosen NOT to overlap round 1's (K, 4, 7, 10, 12):
this round covers 1, 2, 6, 9, 11, plus a math lesson and a reading-inference
lesson (both off-domain, but different topics from round 1's water-cycle and
theme-analysis cases) and one deliberately grade-neutral generic case.

HONEST RESULT (measured against the real, unmodified
`teach.va_writing_sol_graph`, via the public `recover_from_lesson_text` entry
point only -- no internals of concept_recovery.py were read to choose these
lesson texts, and no threshold in concept_recovery.py was changed in response
to seeing these results):

  5 cases were designed to recover a specific taught grade (2 signposted with
  a prior grade as an assumed prerequisite, 1 unsignposted, 2 standalone):

    - GRADE2_SIGNPOSTED (intended taught=2.W, assumed=(1.W,)): SAFE
      ABSTENTION. 2.W is the correct top scorer (8) but 1.W (7) is within
      `_MIN_MARGIN`, so the module declines rather than guess. A miss, but
      the safe kind.
    - GRADE6_SIGNPOSTED (intended taught=6.W, assumed=(5.W,)): **CONFIDENT
      WRONG ANSWER.** Recovered taught=7.W (not 6.W), with a wrong
      prerequisite claim assumed=(6.W,) riding on top of it (6.W is a real
      direct prerequisite of 7.W, so the machinery reported it consistently
      wrong, not just topically wrong). This is the exact failure mode
      teach-l7u's fix targeted, and it was NOT caught. See
      "WHY THIS IS A DIFFERENT HOLE THAN teach-l7u's" below -- this is a new,
      structurally distinct gap, not a regression of teach-l7u's own fix.
    - GRADE9_UNSIGNPOSTED (intended taught=9.W, prerequisite 8.W present but
      deliberately not signposted with a "remember/recall" phrase): SAFE
      ABSTENTION. Top four candidates (10.W=10, 9.W=10, 11.W=9, 12.W=9) are
      all within margin of each other -- correctly ambiguous, since this
      text's content genuinely straddles several upper-grade nodes' nearly
      identical vocabulary.
    - GRADE11_STANDALONE (intended taught=11.W, no prior-grade reference):
      SAFE ABSTENTION. 11.W scored 8, tied within margin against 8.W (10)
      and 7.W (9) -- the actual top-scoring candidates were NOT the intended
      grade at all, but the module still declined rather than confidently
      naming the wrong one.
    - GRADE1_STANDALONE (intended taught=1.W, no prior-grade reference):
      SAFE ABSTENTION. 1.W is in fact the correct top scorer (4) but wins by
      only 2 over the runner-up while covering just 16% of its own
      vocabulary -- below `_MIN_WINNING_COVERAGE` (20%) -- so the module
      abstains on a genuine correct answer. Costs recall, not correctness.

  2 cases were designed to be clearly outside the writing-SOL vocabulary (a
  math lesson on fraction arithmetic, and a reading-comprehension lesson on
  inference/author's-purpose -- deliberately different topics from round 1's
  water-cycle and theme-analysis cases so this isn't measuring the same two
  texts again):

    - ABSTAIN_MATH: correctly abstained (best candidate shared only 2
      distinctive words, below `_MIN_MATCH_WORDS`).
    - ABSTAIN_READING_INFERENCE: correctly abstained (7.W/8.W tied within
      margin).

  1 case (AMBIGUOUS_GENERIC) was deliberately written as grade-neutral,
  generic writing-process advice with no escalation language at all, to see
  whether the module would honestly decline rather than pick a plausible-
  looking grade out of boilerplate. It abstained (1.W/2.W/7.W tied) -- the
  honest outcome, since there was no single correct answer to recover here
  either.

  SCOPED SUMMARY, PER THIS BEAD'S REQUESTED BREAKDOWN (8 held-out texts, 1
  domain, 1 checker, measured once, thresholds NOT touched afterward):

    correct recoveries:        0 / 8
    safe abstentions:          7 / 8
    CONFIDENT WRONG ANSWERS:   1 / 8  (GRADE6_SIGNPOSTED)

  Before teach-l7u's fix, round 1 measured 2/8 confident wrong answers (out
  of its own 8, a different set of texts). This round, on a fresh set the fix
  was never tuned against, the rate is 1/8 -- lower, but not zero. The
  fix reduced the failure mode; it did not close it. Per sandbox-prompt.md,
  this is reported as a measurement, not extrapolated into either "the fix
  works" or "the fix is broken" -- it is what these 8 texts showed.

WHY THIS IS A DIFFERENT HOLE THAN teach-l7u's

teach-l7u's raid-tier fix requires a bare-minimum-margin win (margin <=
`_MIN_MARGIN`) to be corroborated by `_MIN_WINNING_COVERAGE` (20%) of the
WINNER's own vocabulary. GRADE6_SIGNPOSTED's winner, 7.W, scored 18 with
36.0% coverage of its own 50-word vocabulary -- comfortably over both bars,
so the gate the fix installed never had a reason to fire. The problem is
that 6.W (the actually-intended node, scoring 16, covering 50.0% of its own
32-word vocabulary -- MORE proportionally exercised than the false winner)
was never compared against 7.W on coverage at all: the winning margin (18-16
= 2) is not *less than* `_MIN_MARGIN` (2), so `_resolve_candidates` takes the
"single close candidate" branch and only checks the winner's OWN coverage in
isolation, never the coverage tiebreak logic that compares rivals against
each other. That comparison logic exists in this module (see
`_MIN_COVERAGE_MARGIN`) but only runs when the raw-score margin is small
enough to put multiple candidates in the `close` list together -- and here
it wasn't, because 8.W also scored 16, tying with 6.W for second and
splitting what would otherwise have been the "close" group in a way that
still leaves 7.W's margin over the single largest rival right at 2, not
under it. Adjacent VA Writing SOL grades share large amounts of literal,
non-boilerplate escalation vocabulary by design (both 6.W and 7.W's real
standard text contain "cause-effect", "comparison", "transitional",
"multi-paragraph", "structure", etc.) -- unlike round 1's failures, which
were incidental overlap from ordinary English or synonym reach, this is
literal, on-topic vocabulary genuinely shared between two curriculum-
adjacent-but-different nodes, and margin-based winner-take-all scoring picks
whichever one happens to have accumulated a couple more matches, not
whichever one the text is more OF. Filed as teach-cpg (see below); NOT
fixed here per this bead's own instruction not to tune the threshold in
response to this round's results.

WHAT WAS NOT DONE: no threshold in concept_recovery.py was changed as a
result of this measurement. Nudging `_MIN_MARGIN`, `_MIN_WINNING_COVERAGE`,
or wiring the coverage-tiebreak comparison into the single-candidate branch
in response to GRADE6_SIGNPOSTED specifically would make this round's set
into tuning data too, repeating exactly the mistake this lineage keeps
disclosing (teach-8xw.33/40, teach-9k5, teach-l7u). That fix belongs to
teach-cpg, to be closed only against a FOURTH independently-authored
round from a session that did not read this file.
"""
from teach.concept_recovery import recover_from_lesson_text
from teach.va_writing_sol_graph import load_va_writing_sol_graph

WRITING_GRAPH = load_va_writing_sol_graph()

GRADE2_SIGNPOSTED = """Tutor: Before we jump into today's lesson, let's remember what you learned last year about writing. Do you remember how we used to tell stories about things that happened?

Student: Kind of? Like when things happened one after another?

Tutor: Exactly! You'd tell about two or more things that happened in order, and you'd add little details about what happened and who was there — sometimes you'd draw it, sometimes you'd tell someone out loud, and sometimes you'd write it yourself. Remember that?

Student: Oh yeah, like when I drew the picture about going to the zoo and told you what happened first and then what happened next.

Tutor: That's it! And you also learned how to write to teach people about something — you'd name your topic and give a few facts about it. Plus you learned how to share your opinion, like saying "I think dogs are the best pet" and giving one reason why.

Student: I remember doing that one about why recess should be longer!

Tutor: Right, and one reason was enough back then. You also practiced listening to a story and then sharing a little bit of your own thinking about it, using a detail or two from the story to back yourself up.

Student: Okay, I remember most of that now.

Tutor: Great, because now this year we're building on all of that. It's like leveling up! This year when you write a story, you're going to tell about a fuller event, or even a few events in a row, with really good details about what happened and about the characters. But here's the new part — you're going to use time words like "first," "after that," and "finally" to help your reader follow the order.

Student: Ooh, like the words that show what happened when?

Tutor: Exactly. Let's try one right now. Here's a sentence: "I woke up. I brushed my teeth." Can you add a time word to connect those?

Student: Um... "First I woke up, and after that I brushed my teeth"?

Tutor: Perfect, that's exactly the idea! See how much smoother that sounds? We're also building up your informative writing — instead of just naming a topic and giving a couple facts, you're going to actually develop your idea with facts AND examples to really explain it.

Student: So not just "sharks are fish," but like giving an example too?

Tutor: Right, like saying sharks are fish and then explaining that, for example, they breathe through gills just like other fish. And for opinion writing, you're not stopping at one reason anymore — you're going to support your opinion with reasons, plural.

Student: Can I try that? Like my recess opinion — "Recess should be longer because we need exercise, and also because it helps us focus better in class."

Tutor: I love that second reason — that's exactly what we're going for. When you respond to stories now, you'll also give a couple of supporting details from the text instead of just one. And this year you're learning to actually plan your writing first, thinking about your purpose and what type of writing it is before you even start.

Student: So like deciding if it's a story or a fact piece before I write it?

Tutor: Exactly. And then, with help from a grown-up, you'll go back and revise — that means making your ideas clearer, your organization better, your sentences flow nicer, and picking stronger words. After that, you'll also edit with help, checking things like capital letters, spelling, and punctuation.

Student: That sounds like a lot of steps!

Tutor: It is more steps, but you're ready for it — you've got a great foundation from last year. We're just adding new tools to your toolbox. Ready to practice a narrative with some time words today?

Student: Yeah, let's do it!"""

GRADE6_SIGNPOSTED = """Tutor: Before we jump into today's lesson, let's rewind a bit — remember all that writing work you did last year? You wrote personal narratives and even some fiction, right, stories built around a real problem or conflict, and you used description and dialogue to bring it to life?

Student: Oh yeah, I wrote that story about getting lost at my cousin's lake house. I used a lot of dialogue between me and my sister because we were arguing about which trail to take.

Tutor: Exactly, that's a great example. You also worked on expository writing — explaining a topic using facts and details you pulled from a few different sources, and organizing that information in a logical way. And you did persuasive writing too, even about media messages like commercials, where you had to back up your opinion with solid reasons.

Student: Right, I did that essay on whether video games are actually bad for kids. I used facts from like three different articles.

Tutor: And when you responded to books or texts you read, you had to show your thinking using details and evidence straight from the text, all grouped logically. Plus you built well-developed paragraphs as part of an actual writing process, and with help from me or your classmates, you revised for things like organization and word choice, and edited for grammar and punctuation.

Student: Yeah, I remember peer editing with Marcus. He always caught my comma splices.

Tutor: Well, this year we're leveling all of that up. Take narrative writing — now we're not just telling a story, we're using real narrative techniques, deliberate ones, to actually develop your characters and build out the events and experiences instead of just listing what happened.

Student: Like pacing and description that shows instead of tells?

Tutor: Exactly. And for expository writing, instead of just gathering facts, you're choosing a text structure on purpose — description, comparison, cause-and-effect — to make your ideas flow together and hold as one cohesive piece.

Student: Wait, so if I'm writing about why hurricanes form, I could use cause-and-effect structure instead of just listing facts?

Tutor: That's exactly the idea. Cause-and-effect would let you show how warm ocean water leads to evaporation, which leads to the storm system building — the structure itself does some of the explaining for you. Good instinct.

Student: Cool, I like that better than just dumping facts in order.

Tutor: For persuasive writing, you're now expected to support well-defined claims — not just an opinion, but a sharp, specific claim — with reasons and evidence that are logically grouped together. And when you respond to a text now, we're calling it reflective writing — you're still using details and evidence, but you're digging into your own thinking about what it means.

Student: So it's less "here's what happened in the book" and more "here's what I think about what happened"?

Tutor: Precisely. And on the process side, you're not stopping at a single well-developed paragraph anymore. You're planning, drafting, revising, and editing your way into full multi-paragraph pieces.

Student: That's what we're doing with the hurricane essay, right? Like four paragraphs?

Tutor: Right. And when you revise now, you're not just checking word choice and sentence variety within a paragraph — you're also working on the transitions between paragraphs, so the whole piece flows as one thing instead of four separate chunks.

Student: Can we practice that? I have Priya's draft here, and I feel like her second paragraph just kind of stops and the third one starts a totally different idea.

Tutor: Perfect, let's look. What would you suggest to her?

Student: Maybe something like "In addition to the ocean's warmth, wind patterns also play a role" — so it connects back to the last idea before moving on?

Tutor: That's a strong transition — it bridges her cause-and-effect points instead of just jumping. And notice, that's peer editing in action, which is new too — you're not just self-editing for capitalization, spelling, and punctuation anymore, you're doing that same close checking for a partner's sentence structure and paragraphing as well.

Student: It's kind of nice having another set of eyes catch stuff you can't see in your own writing.

Tutor: Couldn't have said it better myself. Let's get you started applying that same feedback to your own draft now."""

GRADE9_UNSIGNPOSTED = """Tutor: Let's start by nailing down your thesis for the school uniforms essay. What's your actual position?

Student: Uniforms should be optional, not mandatory. I think forcing everyone to wear the same thing doesn't actually fix the problems people say it fixes.

Tutor: Good, that's a clear stance. Now what's your strongest piece of evidence for that?

Student: I found a quote from a study that said schools with uniform policies didn't see meaningful drops in bullying rates.

Tutor: Perfect, that's the kind of thing that makes a claim land instead of just floating there. Where's it from?

Student: A peer-reviewed education journal. I've got the author's name and the year too.

Tutor: Great, cite it properly and then explain, in your own words, why that finding actually supports your point — don't just drop the quote and walk away from it.

Student: So I'd say something like, "This shows that appearance-based policies don't address the root causes of conflict between students."

Tutor: Exactly, that reasoning is what connects the evidence to your argument instead of leaving them as two separate things. Now, can I see the paragraph you revised from last week's draft?

Student: Yeah, here it is. I tried to fix the word choice but I'm not sure the ending works.

Tutor: Read the last sentence out loud for me.

Student: "So that is why uniforms are not a good idea and things should change."

Tutor: Right, "things should change" is vague, and it doesn't hand off to whatever comes next. What's your next paragraph about?

Student: Cost — how uniforms are actually expensive for low-income families.

Tutor: So rewrite that last line so it points toward cost specifically, something concrete that bridges the two ideas.

Student: Maybe, "But bullying isn't the only cost of these policies — there's a financial one too."

Tutor: That's a much cleaner handoff. Also vary your sentence lengths in that paragraph — you've got three sentences in a row that are all the same length and rhythm, and it starts to feel flat.

Student: Yeah I noticed that but didn't know what to do about it.

Tutor: Break one into two, or combine two short ones with a semicolon or a dash. Okay, shifting gears a little — I want you to think bigger than a single five-paragraph essay for a minute. What if this uniforms piece became something longer, like four or five pages, where you're not just arguing one claim but actually exploring the issue from a few angles — cost, bullying, self-expression, school identity?

Student: Like a research paper?

Tutor: Sort of, yeah, something that still holds together as one argument but has room to breathe and go deeper into each piece of it. Actually, let's pair that with something else — I want you to also write a shorter reflection, maybe half a page, on an article you read recently, comparing it to something else you've read on a similar topic.

Student: Wait, how is that different from what we were just doing with the uniforms paragraph?

Tutor: Good question. Before, we were tightening one paragraph's clarity and flow. Now I want you producing a whole range of pieces — a tight reflection, a longer argumentative piece, maybe even a letter to your principal about the same uniform issue — each one shaped for a different reader and a different job. The letter needs a totally different tone than the five-page exploration would.

Student: That makes sense. So how do I even start the longer one without it turning into a mess?

Tutor: Same process every time, just with more weight on each stage — you plan out your sections first, draft without worrying about perfection, then revise for whether your ideas are actually clear and fully explained, not just stated, and only at the end do you edit for grammar and style.

Student: What do you mean by "fully explained, not just stated"?

Tutor: Like if you write "uniforms limit self-expression," that's a claim, but you need a sentence or two after it unpacking why that actually matters, maybe an example of how. Don't leave your reader to fill in the gap themselves.

Student: Got it. Should I show a draft to someone before I turn it in?

Tutor: Yes, trade with a partner or read it back yourself with fresh eyes, and when you give feedback, always name one thing that's working clearly and one specific thing that could be clearer — not just "good job" or "fix this."

Student: Okay, and conventions and grammar stuff comes last?

Tutor: Right, once the ideas and structure are solid, then you clean up your sentences, check your tone matches your audience, and fix any mechanical errors. Go ahead and draft an outline for the longer piece tonight, and bring me a paragraph of the reflection tomorrow so we can look at both."""

GRADE11_STANDALONE = """Tutor: So you're really into competitive climbing—I saw the gym photos. What if we build today's writing project around that? Something with a real analytical spine to it.

Student: That could actually be fun. What kind of thing though?

Tutor: Let's aim for a multi-page piece analyzing a trend in the sport—say, why climbing gyms have shifted so heavily toward "spray wall" training and systems boards instead of just route-setting. That's a real argument you can build evidence for, not just a description of what a spray wall is.

Student: Okay, so it's not just "here's what a spray wall is and here's how it works"?

Tutor: Right, description tells me facts. Analysis tells me why it matters and what it means. You'd want to look at causes—maybe training efficiency, injury patterns, the rise of competition-style movement—and argue which factors are driving the shift and what tradeoffs come with it.

Student: I could pull in stuff from climbing forums and maybe an interview with my coach.

Tutor: Good instinct, but let's talk process first. Before you draft a single sentence, sketch a plan: what's your central claim, what are your three or four supporting points, and what evidence backs each one. That's the organizing step, and it's what keeps a long piece from wandering.

Student: I think my claim is that spray walls became popular mainly because they let you drill weaknesses precisely, more than for injury prevention.

Tutor: That's a strong, arguable claim—good. Now, separate task: imagine you're applying to a summer climbing-coach internship at your gym. You'd need a totally different piece—a short statement of qualifications. Same topic knowledge, different purpose and audience.

Student: So less "here's my theory about training" and more "here's why you should trust me with kids on a wall."

Tutor: Exactly. Different voice, different structure, probably tighter and more personal. Try drafting the opening two sentences of that qualifications statement right now.

Student: "I have been climbing for four years and I know a lot about training methods. I think I would be a good coach because I care about safety."

Tutor: Good starting material, but let's sharpen it. Right now it's telling me you're qualified rather than showing it. What's one specific, concrete thing you've actually done that proves training knowledge or safety awareness?

Student: I designed a warm-up circuit for the youth team and our coach started using it for everyone.

Tutor: That's it—lead with that. Try: "Last spring, I designed a warm-up circuit for our youth team that our head coach adopted for the entire gym, because I understand injury prevention isn't separate from skill training—it's part of it." See how that's doing double duty? It's specific and it signals judgment, which is exactly what a hiring audience wants.

Student: That does sound more like something an adult would actually read and believe.

Tutor: That's the audience-awareness piece—matching tone and content to who's reading and why. Now, back to the longer analytical piece: once you have a full draft, I want you to reread it purely for accuracy and depth. Are your claims about training trends actually supported, or are you asserting things you haven't verified?

Student: I probably said "most gyms now use spray walls" without really checking that.

Tutor: That's exactly the kind of thing revision should catch—vague, unverified generalizations. Either find a real source or soften the claim to something you can defend, like "many competitive gyms" if that's what your evidence actually shows.

Student: Got it. Should I also get someone else to read it before I call it done?

Tutor: Definitely—that's peer review, and it's not just "does this sound good." Ask a specific reader to name one thing that's working and one place that's confusing or underdeveloped. Vague praise doesn't help you revise; specific feedback does.

Student: I could ask my teammate who also writes for the gym newsletter.

Tutor: Perfect reader, actually, since they know the subject and can push back on the substance, not just the grammar. Last pass, once content is solid, is editing—conventions, word choice, cutting anything too casual for a piece meant to read as a serious analysis.

Student: Like cutting stuff like "basically" or "kind of."

Tutor: Exactly those. The goal is a piece that would hold up if a coach, an editor, or a college admissions reader picked it up—not just something that sounds fine read aloud once. That precision is what separates a strong draft from a finished piece.

Student: This is a lot more steps than I usually give a piece of writing.

Tutor: It is, but notice none of it was wasted—the planning shaped your argument, the draft gave you something to sharpen, and the revision made your claims trustworthy. Go finish that outline tonight, and bring me a full draft of the qualifications statement next time."""

GRADE1_STANDALONE = """Tutor: Today we're going to write about a trip we take to feed the ducks at the pond! Can you tell me two things that happened, in the order they happened?

Student: First we walked to the pond, then I throwed the bread!

Tutor: Nice job putting those in order! It's "threw," by the way — I threw the bread. Who else was there with us at the pond?

Student: My dog Biscuit came too, and he barked at a big goose!

Tutor: Ha, I bet that goose got a surprise. Let's draw a little picture first to help us think — can you draw the pond, you, and Biscuit?

Student: Okay... I drew Biscuit bigger than me because he's the best.

Tutor: I love that detail! Now let's dictate a sentence about it — tell me what to write and I'll write your words.

Student: biscuit barked at the goose

Tutor: Great sentence! Now look here — this word right at the start, "biscuit," is a name, so it needs something special. What do names need?

Student: A capital letter!

Tutor: Exactly, so let's fix it to "Biscuit." And what do we put at the very end of a sentence to show it's finished?

Student: A period! Like a little dot.

Tutor: Perfect, in it goes. Now let's try something new — let's make a fact page about ducks. What's one true thing you know about ducks?

Student: Ducks have feathers that don't get wet!

Tutor: That's a great fact! What's another one?

Student: They quack really loud and they like bread crumbs.

Tutor: Wonderful, so our topic is ducks, and we've got two facts already. Now let's try an opinion — do you think feeding ducks is fun or boring?

Student: Fun! Because you get to see them swim right up close to you.

Tutor: That's a strong opinion with a good reason behind it. Now, remember the story I read you yesterday about the little duckling who got lost?

Student: Yeah, the sad one where he couldn't find his mom!

Tutor: Right, so what did you think about that story?

Student: I felt bad for him, but I was happy when his mom found him at the end by the reeds.

Tutor: That's a lovely response — you told me how you felt and you used two things that really happened in the story to explain why. You worked so hard today, thinking up ideas, drawing, telling facts, sharing an opinion, and fixing up your sentence all by yourself. I'm so proud of you, duck expert!"""

ABSTAIN_MATH = """Tutor: Today let's tackle adding and subtracting fractions with different denominators. Ready to try one?

Student: Sure. Is it 1/4 plus 1/3?

Tutor: Exactly that one. What's stopping us from just adding the numerators?

Student: The denominators are different, so I can't just add 1 plus 1.

Tutor: Right. We need a common denominator first. What's the smallest number both 4 and 3 divide into?

Student: 4, 8, 12... and 3, 6, 9, 12. So 12.

Tutor: Perfect, 12 is the least common denominator. Now convert 1/4 into twelfths.

Student: 4 times 3 is 12, so I multiply the top by 3 too. 1/4 becomes 3/12.

Tutor: Good. Now do the same for 1/3.

Student: 3 times 4 is 12, so multiply top and bottom by 4. 1/3 becomes 4/12.

Tutor: Now add them.

Student: 3/12 plus 4/12 is 7/12.

Tutor: Nice work, and does 7/12 simplify?

Student: No, 7 is prime and doesn't divide 12, so it stays as is.

Tutor: Let's try a subtraction problem now: 5/6 minus 1/4.

Student: Okay, common denominator for 6 and 4... 6, 12, 18 and 4, 8, 12. So 12 again.

Tutor: Good. Convert 5/6.

Student: 6 times 2 is 12, so 5 times 2 is 10. That gives 10/12.

Tutor: And 1/4?

Student: 1/4 stays the same since the denominator's already 4... wait, no, I need to convert it too.

Tutor: Right, catch yourself there — every fraction in the problem has to be converted to the common denominator, not just the first one.

Student: Oops, okay. 4 times 3 is 12, so 1 times 3 is 3. So 1/4 becomes 3/12.

Tutor: Now subtract.

Student: 10/12 minus 3/12 is 7/12.

Tutor: Does that simplify?

Student: Same as before, 7 and 12 don't share factors, so it's already simplest form.

Tutor: Let's do one more, a little trickier: 2/3 plus 3/5.

Student: Denominators 3 and 5 don't share factors, so I think the common denominator is just 3 times 5, which is 15.

Tutor: Exactly, when there's no shared factor, multiplying them together works. Convert both.

Student: 3 times 5 is 15, so 2 times 5 is 10. 2/3 becomes 10/15. Then 5 times 3 is 15, so 3 times 3 is 9. 3/5 becomes 9/15.

Tutor: Now add.

Student: 10/15 plus 9/15 is 19/15.

Tutor: Since that's an improper fraction, can we write it differently?

Student: Yeah, 15 goes into 19 once with 4 left over, so it's 1 and 4/15.

Tutor: Perfect. You're getting the hang of finding common denominators and remembering to convert every fraction, not just one.

Student: Yeah, I just need to remind myself to check both fractions before I add or subtract."""

ABSTAIN_READING_INFERENCE = """Tutor: Today we're going to read a short article about honeybee "waggle dances" and figure out what the writer wants us to understand — even the parts they don't say outright.

Student: Okay. I read it already. It's about how bees dance to tell other bees where flowers are.

Tutor: Right. Now, the article ends with this line: "Beekeepers who lose entire colonies overnight are left wondering what their bees knew that they didn't." What do you think that sentence is really doing there?

Student: I guess... it's just a weird ending?

Tutor: Let's slow down. Who's mentioned right before that sentence — bees or beekeepers?

Student: Beekeepers.

Tutor: And what's implied about them compared to the bees?

Student: That the beekeepers don't understand something the bees do understand. Like the bees have information humans don't have.

Tutor: Exactly — that's an inference. The author never says "humans are behind bees in understanding this," but the wording sets up that comparison. What clue in that sentence tips you off?

Student: "What their bees knew that they didn't." It's saying the bees knew something first.

Tutor: Good catch. Now look at the second paragraph, where it says colony collapse has "cost farmers billions and put dinner tables at risk." Why include farmers and dinner tables in an article about dance moves?

Student: Maybe to show it's not just a cute bee fact — it actually matters to people.

Tutor: Right, so what does that tell you about who the author is writing for?

Student: Probably regular people, not just scientists. Like, "hey, this affects you too."

Tutor: That's the audience. Now let's think about purpose. Is this article trying to entertain you with a fun animal fact, warn you about a danger, or teach you a scientific process?

Student: It kind of does all three a little.

Tutor: It can do more than one, but usually there's a main one. Look at the title again: "The Silent Warning in the Hive."

Student: Oh — "warning." So maybe the main purpose is to warn people, not just to explain the dance.

Tutor: Nice. What evidence from the body of the article backs that up?

Student: There's a part that says scientists noticed the dances changing pattern right before several hives collapsed. That sounds like a warning sign.

Tutor: Perfect — that's the kind of specific detail you want to quote to support your claim. If someone asked you "why did the author write this," what would you say, using that evidence?

Student: I'd say the author wrote it to warn readers that changes in bee dances might predict hive collapse, and they used the detail about dance patterns shifting before hives died to prove it.

Tutor: That's a strong, text-supported answer. One more: the article never says "you should care about bees." How do we know the author still wants us to feel that way?

Student: Because of the tone — words like "silent warning" and "at risk" sound urgent, not neutral.

Tutor: Exactly, tone is another clue toward inference. So when you're asked to figure out what a text implies, what will you look for from now on?

Student: Word choice, what details they choose to include, and how the title or ending frames everything — even if they never say it straight out.

Tutor: That's exactly the skill. Nicely done today."""

AMBIGUOUS_GENERIC = """Tutor: So what did you bring in today?

Student: I've got this piece I've been working on. It's about a topic I picked myself, so I actually don't hate it, which is new.

Tutor: That already puts you ahead. Before we look at it, tell me — who's it for? Who do you picture reading this?

Student: I guess... whoever grades it? But also I kind of wrote it like I was explaining it to my friend.

Tutor: That's a good instinct actually. Thinking about your reader changes what you need to explain and what you can skip. Did you do any planning before you started writing, or did you just dive in?

Student: I scribbled some ideas on a sticky note first. Just random stuff I wanted to include, not in order or anything.

Tutor: That's exactly the point of jotting things down — get the ideas out before worrying about order. Then what?

Student: Then I just wrote a rough draft. It's messy in some places. I didn't stop to fix stuff, I just kept going.

Tutor: Good, that's how a first draft should feel — a little messy is fine, that's what revising is for. Let's read it out loud together. Go ahead and start.

Student: Okay. "My topic is interesting because there are a lot of parts to it. The first part is important. The second part is also important."

Tutor: Stop there for a second. Read that back — does anything feel thin or confusing to you?

Student: Yeah, actually. I say both parts are "important" but I don't really say why. It sounds kind of empty.

Tutor: Exactly what I was noticing too. That's a great catch. When you say something is important, your reader wants to know the reason. Can you add a sentence explaining why the first part matters?

Student: I could say something like, "The first part matters because without it, the rest wouldn't make sense." That's more specific.

Tutor: Much better — now the reader actually understands your thinking instead of just taking your word for it. Keep reading a bit more.

Student: "The second part is important. The second part connects to the first part. The second part changes things."

Tutor: Notice anything about those three sentences?

Student: They all start the same way. "The second part... the second part..." It's kind of repetitive when I hear it out loud.

Tutor: Right, and reading out loud is such a good way to catch that — repetition is way more obvious to your ears than your eyes. How might you mix those up?

Student: Maybe combine two of them? Like, "The second part connects to the first and changes how everything fits together." That's one sentence instead of two short choppy ones.

Tutor: Nice, and now you've got some variety in sentence length too, which makes it more pleasant to read. Once you've done a pass like that for the whole piece, what's left?

Student: The last step, right? Going through for spelling and punctuation mistakes.

Tutor: Exactly, and that comes last on purpose — no sense polishing sentences you might still cut or rewrite. Go ahead and mark up a few spots where you want to add detail, fix the repetition, and then do that final proofread pass.

Student: Okay, this actually makes sense now. I always thought revising just meant fixing typos.

Tutor: It's way more than that, but you're catching on fast. Bring me the revised version next time and we'll see how it reads."""


def test_grade2_signposted_safely_abstains():
    """SAFE ABSTENTION: 2.W is the correct top scorer (8) but 1.W (7) is
    within `_MIN_MARGIN`, so the module declines rather than guess. A miss,
    but the safe kind."""
    result = recover_from_lesson_text(GRADE2_SIGNPOSTED, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()


def test_grade6_signposted_now_safely_abstains_but_teach_cpg_is_not_fully_closed():
    """UPDATED by a teach-cpg validation round (fresh session, see
    sandbox-handoffs/teach-cpg.md). This case USED TO be a CONFIDENT WRONG
    ANSWER: intended taught=6.W, assumed=(5.W,), but actually recovered
    taught=7.W with assumed=(6.W,) -- teach-l7u's single-winner branch only
    checked the winner's own coverage against a fixed floor and never
    compared it to the rival's coverage (root cause detailed in this file's
    original module docstring and in the teach-cpg bead).

    teach-cpg's fix (the single-winner branch in _resolve_candidates now
    also compares the winner's coverage against candidates[1]'s coverage at
    the bare-minimum-margin scope) changes this specific case's raw-word-tier
    result from a confident wrong answer to a correct abstention -- measured
    here, not assumed.

    IMPORTANT: this does NOT mean teach-cpg is closed. A fresh,
    independently-authored FOURTH held-out round (round3, see
    tests/test_concept_recovery_writing_domain_generalization_round3.py)
    found teach-cpg's fix does NOT fully generalize: it protects the raw
    exact-word tier (candidates[1] there is reliably the true confusable
    rival), but the semantic fallback tier computes its own independently
    ranked candidate list, and when a third candidate's WordNet-expanded
    score outranks the true rival, candidates[1] is no longer that rival --
    the fix's single-candidate comparison silently checks the wrong node and
    a confident wrong answer slips through the semantic tier instead. See
    round3's GRADE6_UNSIGNPOSTED_GARDENING case and the follow-up bead it
    was filed under for the precise reproduction. teach-cpg itself is left
    OPEN pending that follow-up."""
    result = recover_from_lesson_text(GRADE6_SIGNPOSTED, WRITING_GRAPH)
    assert result.taught_node_id is None, (
        f"expected a safe abstention now that teach-cpg's fix is in place -- "
        f"got {result.taught_node_id!r} instead; if this is 'va-writing-sol:6.W' "
        f"the fix improved further, if it is anything else (especially "
        f"'va-writing-sol:7.W' again) the fix regressed"
    )
    assert "ambiguous" in result.abstain_reason.lower() or "leads" in result.abstain_reason.lower()


def test_grade9_unsignposted_safely_abstains():
    """SAFE ABSTENTION: intended taught=9.W with an unsignposted 8.W
    prerequisite. Top four candidates (10.W=10, 9.W=10, 11.W=9, 12.W=9) are
    all within margin of each other -- genuinely ambiguous given how close
    these adjacent grades' vocabulary is, and the module correctly declines
    rather than pick one."""
    result = recover_from_lesson_text(GRADE9_UNSIGNPOSTED, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()


def test_grade11_standalone_safely_abstains():
    """SAFE ABSTENTION: intended taught=11.W, no prior-grade reference. Actual
    top-scoring candidates (8.W=10, 7.W=9) are not even the intended grade,
    but the module still abstains rather than confidently naming the wrong
    one -- the safe outcome given the raw top scorers here are wrong."""
    result = recover_from_lesson_text(GRADE11_STANDALONE, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()


def test_grade1_standalone_safely_abstains_despite_being_top_scorer():
    """SAFE ABSTENTION: 1.W is in fact the correct top scorer (score 4) but
    wins by only 2 over the runner-up while covering just 16% of its own
    vocabulary -- below _MIN_WINNING_COVERAGE (20%) -- so the module abstains
    on what would have been a genuine correct answer. Costs recall, not
    correctness; consistent with this module's documented preference for
    erring toward abstention."""
    result = recover_from_lesson_text(GRADE1_STANDALONE, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "covers just" in result.abstain_reason


def test_abstain_math_correctly_abstains():
    """CORRECT ABSTENTION: a math lesson (fraction arithmetic) with no
    writing-SOL vocabulary at all correctly abstains -- best candidate
    shares only 2 distinctive words, below _MIN_MATCH_WORDS."""
    result = recover_from_lesson_text(ABSTAIN_MATH, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "shares only" in result.abstain_reason


def test_abstain_reading_inference_correctly_abstains():
    """CORRECT ABSTENTION: a reading-comprehension lesson (inference and
    author's purpose from a nonfiction article -- not composition) correctly
    abstains rather than being mistaken for a writing-composition grade."""
    result = recover_from_lesson_text(ABSTAIN_READING_INFERENCE, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()


def test_ambiguous_generic_correctly_abstains():
    """CORRECT ABSTENTION: deliberately grade-neutral, generic writing-process
    advice with no escalation language at all -- there is no single correct
    grade to recover here, so abstention is the only honest outcome. Ties
    1.W/2.W/7.W within margin."""
    result = recover_from_lesson_text(AMBIGUOUS_GENERIC, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()
