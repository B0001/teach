"""teach-25s: generalization measurement for concept_recovery.py against the
VA Writing SOL K-12 graph, using lesson text NOT authored by this session.

tests/test_concept_recovery_writing_domain.py (teach-8xw.42) is a FLOOR test:
every fixture in it is hand-written by the session that wrote the assertions,
which per sandbox-prompt.md's "you cannot hold out examples from yourself" can
only show the mechanism runs, never that it generalizes. That bead's own
closing note asked for this as a separate follow-up, kept in its own file
rather than folded into the floor test.

WHERE THIS TEXT CAME FROM

Eight lesson dialogues below were each produced by a *separate* `Agent` tool
call (teach-8xw.33's precedent), every one given an explicit no-tool-use,
no-repository-access instruction and told nothing about this module's
existence, its scoring mechanism, its thresholds, or its vocabulary index --
only plain-English curriculum content to teach (itself paraphrased by the
bead author from the real VA Writing SOL leaf-standard text in
teach/data/va_writing_sol_k12.json, with an explicit instruction to the agent
not to copy it verbatim but to render it as natural tutor/student dialogue).
Each of the eight agents was independent: none saw another's output, this
module's code, or the floor test's fixtures. The full transcripts are
reproduced verbatim below, not summarized in prose, per teach-8xw.40's
correction of teach-8xw.33 (only text actually committed as runnable data can
be re-measured by a future worker; a handoff's prose description of what a
held-out round contained is not evidence once the session that saw the full
round is gone).

HONEST RESULT (measured against the real, unmodified
`teach.va_writing_sol_graph`, via the public `recover_from_lesson_text` entry
point only -- no internals of concept_recovery.py were read to choose these
lesson texts):

  4 cases were designed to recover a specific taught grade, 2 correctly
  signposted with a prior grade as an assumed prerequisite, 1 designed to
  assume a prior grade WITHOUT signposting it, and 1 standalone (no prior
  grade referenced at all):
    - GRADE4_SIGNPOSTED: fully correct -- taught=4.W, assumed=(3.W,).
    - GRADE7_SIGNPOSTED: fully correct -- taught=7.W, assumed=(6.W,).
    - GRADE10_UNSIGNPOSTED: WRONG, not abstained. Intended taught=10.W;
      actual is 8.W (its own leaf vocabulary -- "audience", "purpose",
      "elaboration", "clarity" -- outscored the intended grade). This is
      the failure mode sandbox-prompt.md calls out as worse than abstention:
      the checker answered confidently and wrong rather than admitting it
      could not tell. Filed as teach-25t.
    - GRADE12_STANDALONE: abstained (safe) -- intended taught=12.W was the
      raw top scorer but tied with 7.W and 11.W within `_MIN_MARGIN`, so the
      module correctly declined to guess rather than pick the (correct)
      top-of-tie candidate.

  2 cases were designed to be clearly outside the writing-SOL vocabulary
  (a science topic, and a reading-comprehension -- not writing-composition
  -- skill), where a correct checker must abstain:
    - WATERCYCLE_ABSTAIN: correctly abstained (best candidate shared only 2
      distinctive words, below `_MIN_MATCH_WORDS`).
    - READING_THEME_ABSTAIN: WRONG, not abstained. A lesson entirely about
      analyzing a short story's theme (a reading-comprehension skill, not
      writing composition) was confidently matched to 8.W with an
      unsignposted-prerequisite claim on 7.W. Also filed as teach-25t --
      this is the more concerning of the two false positives, since it
      crosses a domain boundary (reading content mistaken for writing
      content) that a human checker would never confuse.

  1 case (REVISING_AMBIGUOUS) was deliberately written as generic
  revise/edit-for-clarity content with no grade-specific escalation
  language, to see whether the module would honestly abstain on genuinely
  underspecified content. It did not: it confidently matched 8.W. Not
  filed as a bug on its own (there was no single "correct" answer this case
  was measured against), but recorded here as further evidence for
  teach-25t's pattern: this module's raw-vocabulary matcher does not
  reliably distinguish "no real signal" from "weak but real signal", and a
  human reading this text would not have picked 8.W over 9.W/10.W/11.W
  either.

  1 case (KINDERGARTEN_STANDALONE) was designed to recover K.W with no
  prerequisite (K is the first grade in the chain, so no prior-grade
  content exists to signpost). It abstained (safe) -- K.W was the raw top
  scorer but tied with 4.W/7.W/8.W within `_MIN_MARGIN`, so a real match
  was missed but not with a wrong answer.

SCOPE OF WHAT THIS MEASURES, PLAINLY STATED: 8 held-out lesson texts, 1
domain (VA Writing SOL K-12), 1 checker (concept_recovery.py's raw+semantic
tiers), measured once. 2/4 taught-concept-recovery attempts landed exactly
right (including their prerequisite outcome); 2/4 did not (1 safe
abstention, 1 dangerous wrong answer). 1/2 abstain-designed cases correctly
abstained; 1/2 falsely matched. This is not a claim that the module
generalizes to writing lesson text broadly, nor a claim that it fails
broadly -- it is what these 8 independently-authored texts showed, no more
and no less. A wider round could show a different mix in either direction.
"""
from teach.concept_recovery import recover_from_lesson_text
from teach.va_writing_sol_graph import load_va_writing_sol_graph

WRITING_GRAPH = load_va_writing_sol_graph()

GRADE4_SIGNPOSTED = """Tutor: Before we jump into new territory, let's take a second to remember what you already built last year. You learned that narrative, informative, and opinion writing each have their own shape — a story unfolds one way, an explanation another, an opinion piece another. You practiced writing personal and made-up stories where one event led naturally to the next. You wrote informative pieces packed with facts, and opinion pieces where you backed up your view with reasons. You also responded to books you read by sharing your thinking with details from the text, and you worked through drafts of paragraphs with help revising and editing for things like capitalization and punctuation. Ring a bell?

Student: Yeah, I remember the opinion piece I wrote about why school should start later. I had reasons but I don't think I used a lot of facts.

Tutor: Perfect example, and that's exactly where we're leveling up this year. Let's say you're writing that same piece now — about school start times. This year, persuasive writing needs a clear opinion PLUS facts, details, and reasons woven together, not just "I think this because I feel like it." What's a fact you could add?

Student: Maybe that studies show teenagers' brains don't wake up until later in the morning?

Tutor: Exactly — now you've got an opinion backed by real evidence. That's the persuasive pattern: state your claim, then stack up facts and reasons that support it, often building to your strongest point. Now compare that to expository writing, which has a different job. Say you're writing about how volcanoes form instead. You're not trying to convince anyone of anything — you're examining the topic and developing it with facts and details. And you'd use linking words like "first," "as a result," or "in addition" to connect those facts smoothly. Can you try linking two volcano facts with a transition word?

Student: Magma builds up under the crust. As a result, pressure increases until it erupts?

Tutor: Nicely done — "as a result" ties cause to effect. Now here's the third pattern: narrative. If you were writing a story about a kid who gets lost hiking, it wouldn't be organized around facts or arguments — it'd be organized around a central problem. The kid is lost — that's the problem the whole story orbits. Every event either makes things worse or moves toward solving it. How is that different from just listing "then this happened, then that happened"?

Student: I guess everything has to connect back to being lost, not just be random events in a row.

Tutor: Exactly — that central problem gives the story a spine. Now, one more type we're adding this year: writing in response to something you've read. Say you just read a story about that lost hiker. Your response — whether it's a summary, a reflection, or a description — needs to show your actual thinking, backed up with details and evidence straight from the text, again connected with linking words like "for example" or "this shows." It's not enough to say "I liked it" — you show why using the text itself.

Student: So it's kind of like the opinion piece, but the evidence comes from the story instead of from facts I look up?

Tutor: That's a sharp connection. Now, no matter which of these four you're writing — narrative, expository, persuasive, or text response — you go through the same writing process to get to a well-developed paragraph: you draft, then you revise, then you edit. Revising is about quality — are your ideas clear, is it organized well, do your sentences flow, did you pick strong words? Editing is different — that's the cleanup pass: capitalization, spelling, punctuation, sentence structure, paragraphing. Which one would fixing a run-on sentence fall under?

Student: Editing, because that's more about the mechanics, not the ideas.

Tutor: Right. And here's the part that's new this year — you won't just be revising and editing your own work. You'll be doing it with peers and adults, trading drafts and giving each other feedback. So if I handed you a partner's volcano paragraph and it jumped from "magma rises" straight to "villages evacuate" with nothing connecting them, what would you suggest?

Student: I'd tell them to add a linking word or explain what happens in between, like "this causes pressure to build, which forces the eruption."

Tutor: That's exactly the kind of peer feedback that makes writing stronger. Notice how every one of these skills threads back to the same idea — the organization has to match the purpose, and everything you add, whether it's a fact, a reason, or a text detail, has to earn its place and connect clearly to what comes next. That's the real leap from last year to this one."""

GRADE7_SIGNPOSTED = """Tutor: Before we jump into new territory, let's take a second to remember what you already built last year. You wrote stories about real or made-up experiences, and you worked on building characters and events into them. You also wrote informational pieces using structures like description or cause-and-effect. And you tackled persuasive writing—forming an opinion on something and backing it up with reasons. Ring a bell?

Student: Yeah, I remember the essay I wrote about why our school should have a longer lunch period. I used reasons, but I think I just kind of... listed them.

Tutor: That's a great memory to start from, actually, because that's exactly where we're leveling up this year. Let's say you're writing a narrative about the day you got lost at a state fair. Last year you'd focus on what happened and who was there. This year, I want you noticing your word choices and your transitions—especially ones that show time or place shifting. Instead of just saying "then," you might say "twenty minutes later, panic setting in" or "back near the ticket booth, the crowd had thickened." See how that does double duty?

Student: Oh, so it's not just "then this happened, then that happened"—it's giving a little snapshot of the shift itself.

Tutor: Exactly. Precise words matter too. Not "I felt scared," but "my stomach dropped like the Ferris wheel car cresting the top." Now let's pivot to expository writing. Say your topic is how volcanoes form. Last year, you might've picked one structure, like cause-and-effect, and described it. This year, I want you pulling facts from at least two or three credible sources—maybe a science textbook and a geological survey website—and actually checking that they agree with each other before you use them.

Student: What if my sources disagree on something?

Tutor: Great question—that's actually part of the skill. You'd note that, or dig for a third source to settle it, rather than just picking whichever fact sounds cooler. And you can still use those organizational patterns—comparison, description, cause-effect—but now you're using them deliberately to show relationships. Like, "unlike a shield volcano's slow lava flow, a stratovolcano's thick magma causes explosive pressure to build." That "unlike" is doing real comparative work.

Student: Okay, that makes sense. What about persuasive writing—is the lunch essay approach not going to cut it anymore?

Tutor: Right, remember how I said it read like a list? This year we're grouping claims logically instead of just piling them up. So for your lunch-period essay, you might group all your health-related claims together—time to eat calmly, digestion, afternoon focus—then transition into a separate group about social or academic benefits. Each claim also needs real evidence behind it, not just an opinion stated twice in different words.

Student: So instead of "longer lunch is healthier" and "longer lunch helps you feel better," which are basically the same thing, I need actual reasoning connecting evidence to the claim.

Tutor: Precisely. Now there's also a new one this year: reflective writing about something you've read. Say you just finished a novel where the main character finally stands up to a bully. I'd want you to write about what that moment made you think or feel, but backed up with actual details from the text—a specific line, a specific scene—not just "I liked when she was brave."

Student: So it's like proving my reaction with evidence from the book itself.

Tutor: Exactly, you're demonstrating your thinking, not just announcing it. Now, across all of these—narrative, expository, persuasive, reflective—we're going to lean hard on the writing process: planning it out, drafting, revising, editing. You already know the stages, but this year they matter more because your pieces are getting longer, multi-paragraph pieces where losing the thread is easy without a plan.

Student: I usually skip planning and just start writing.

Tutor: That's actually the biggest place to grow. Even five minutes of jotting an outline saves you from realizing halfway through your volcano essay that you never explained what magma even is. And when you revise, don't just fix typos—look at whether your word choice is vivid, whether your sentences have some rhythm and variety instead of all starting with "I" or "The," and whether your paragraphs connect to each other smoothly.

Student: And editing is the very last step, for the small stuff, right? Like capitalization and punctuation?

Tutor: Right, that's the fine-tooth-comb pass—capitalization, spelling, punctuation, sentence structure, paragraph breaks. And here's the new part: you're not just editing your own work anymore, you're going to trade papers with a partner and edit theirs too. Sometimes it's easier to catch someone else's comma splice than your own.

Student: That actually sounds kind of fun, catching someone else's mistakes.

Tutor: It is, and it sharpens your eye for your own writing too. So to sum up where we're headed: richer, more deliberate narratives with real transitions and precise language, expository writing grounded in multiple trustworthy sources, persuasive writing with logically grouped, well-supported claims, reflective responses that dig into the text itself, and a writing process—plan, draft, revise, edit, and now peer-edit—that you actually use on purpose instead of skipping straight to a first draft.

Student: Okay, I think I can picture it now. Should I start planning that volcano essay for practice?

Tutor: Perfect place to start. Grab two sources first, and let's outline before you write a single sentence."""

GRADE10_UNSIGNPOSTED = """Tutor: Let's take on something meaty today — I want you to write a piece defending a position on whether school cafeterias should ban all sugary drinks. But here's the catch: it's not going to be a five-paragraph quick draft. I want you to build this out into something longer and more developed, with room to actually explore the counterarguments.

Student: Longer like how long?

Tutor: Long enough that you can't just state your claim and drop three reasons. Think multiple pages — enough space to bring in evidence, address what the other side would say, and really elaborate on your strongest point instead of just listing it. When you have more room, "sugary drinks cause health problems" isn't enough anymore — you need to show it, with a specific example or statistic, and then explain why that example actually proves your point.

Student: Okay. So where do I even start with something that big?

Tutor: Same place you'd start with anything — figure out who you're writing to and why, before you write a single sentence of the actual argument. Who's your audience here?

Student: I guess... the school board? They're the ones who'd actually make the decision.

Tutor: Good, that changes everything about how you write it. If it's the school board, your tone is going to be more formal, you'll want to acknowledge budget and vendor contracts because that's what they care about, and you'll organize your points around what would actually move a decision-maker. Sketch that out before you draft — what are your three or four strongest points, in what order, and what's your evidence for each?

Student: Can I plan it like a map first, then write, then go back and fix stuff?

Tutor: Exactly that — rough out the structure, get a full draft down without worrying about perfection, then come back and revise. Now, here's where I want to add a new layer this year: once you have a draft, I want you reading it almost like a stranger would. Is every claim actually backed up, or did you just assert it and move on? That's the elaboration piece — don't just say drinks are bad for kids, dig into why, with a source or a concrete case.

Student: What if I think it's fine but I'm not sure?

Tutor: That's exactly why we don't stop at your own read of it. Trade drafts with a partner, or even just reread it yourself after a day away, and ask two questions: where's this unclear, and where's this thin? Then go back in and thicken up the weak spots and tighten the muddy sentences.

Student: So the peer feedback isn't about fixing commas, it's about the ideas?

Tutor: Right, that's the first pass — content and clarity, does the argument actually hold together and is anything underdeveloped. The comma-level stuff, the grammar, the word choice, the tone — that's a separate, later pass, once the ideas are solid. No point polishing sentences you might cut.

Student: Got it. Can I try a totally different kind of writing with this same topic, not just the argument essay?

Tutor: I love that you're thinking that way, because that's actually part of the goal this year — I want you comfortable shifting the same content into very different shapes. Take your cafeteria topic and also write me a short, tight summary of your argument for a school newsletter, then a personal reflection on your own drink habits, and see how differently each one has to sound.

Student: The newsletter one would have to be way shorter and more casual, right?

Tutor: Exactly — different audience, different purpose, so different length, tone, even sentence structure. The reflection can be first-person and a little messy and thoughtful; the newsletter piece needs to be punchy and quick to scan; the school board piece needs to be formal and airtight. Same brain, three very different voices — that flexibility is what we're building.

Student: This feels like a lot of moving pieces to juggle at once.

Tutor: It is, but you're not doing it all in one leap — plan, draft, get feedback, revise the ideas, then edit the language, one stage at a time, and it stops feeling overwhelming. Let's start today with just the planning stage for the school board piece — sketch your audience, your purpose, and your top three points, and we'll build from there next time."""

GRADE12_STANDALONE = """Tutor: So today I want to zoom out from single paragraphs and talk about you as a writer who can do *lots* of different jobs with words. Tell me something you're interested in — anything.

Student: I've been reading about urban beekeeping. People keep hives on rooftops in cities.

Tutor: Perfect, we'll use that all day. Here's the first idea: you shouldn't just be able to write a paragraph about bees — you should be able to write a whole researched piece that runs several pages, develops an argument, and doesn't run out of steam by page two. That's what I mean by an "extended piece." It's a different muscle than a quick paragraph; it needs sections, transitions, and a plan that holds the whole thing together.

Student: Like a mini research paper on whether cities should allow rooftop hives?

Tutor: Exactly. And notice that's a different kind of writing than, say, explaining *how* to actually install a hive box — step by step, with the right terms, safety warnings, measurements. That second kind is technical writing: precise, no wasted words, written so someone could actually follow it and not get stung. Extended writing persuades or explores; technical writing instructs. You need both.

Student: So the beekeeping topic could turn into totally different pieces depending on what I'm trying to do?

Tutor: That's the whole game. The same topic can become a two-sentence summary for a newsletter, a reflective journal entry about the first time you got stung, a vivid description of a hive at dawn, a critique of a bad beekeeping blog post, a letter to your city council asking them to change a zoning rule, even a poem about bees if you're feeling ambitious. Each of those wants a different voice — the council letter is formal and diplomatic, the journal entry can be personal and messy, the poem can bend grammar on purpose.

Student: How do I know which voice to use without it sounding fake?

Tutor: You start by asking two questions before you write a single sentence: who is this for, and what do I need it to do? That's planning. If you're writing to the council, your purpose is to persuade a busy official who doesn't care about your feelings — so you plan your strongest facts up front. If you're journaling for yourself, your purpose is just honest thinking, so you can ramble. Once you know audience and purpose, you draft loosely, not worrying about perfection.

Student: And then I just clean it up at the end?

Tutor: Not quite "at the end" — revising and editing are actually two different jobs, and people mix them up. Revising happens first and it's about the *content*: is the information accurate, is anything missing, is the point clear? Say your council letter claims rooftop hives "never" cause problems — that's not accurate, and a good revision pass would catch that overclaim and add a caveat, plus maybe a supporting statistic you left out. You're deepening and correcting the thinking itself.

Student: So editing is more about fixing typos and stuff?

Tutor: Right — editing is about conventions and style once the content is solid: grammar, punctuation, word choice, formality level. And here's a trick that helps with both stages: get another set of eyes on it, or become your own second reader. If a friend reads your council letter and says "I don't understand why rooftop hives help with pollination at all," that's gold — it tells you the *content* is unclear, so that's a revision note, not just a comma fix.

Student: What if the friend just says "this is bad" and nothing else?

Tutor: Then you push back and ask them to be specific and to say what's working, too — not just what's broken. Good peer feedback names a strength ("your opening story about the empty flowerbeds really hooks me") and a specific fix ("but paragraph three repeats the same statistic twice"). That's the standard I want you to hold yourself to when you review a classmate's writing, and the standard to expect back. Vague praise or vague criticism doesn't help either of you improve.

Student: Got it. Does the letter to the council need to sound totally different from the journal entry, language-wise?

Tutor: Completely different registers, same writer. The council letter needs full sentences, no slang, no contractions if you want to be extra formal, and precise vocabulary — "apiary" instead of "bee thing." The journal entry can use contractions, fragments, even humor. Learning to dial that formality up and down on purpose, instead of by accident, is a real skill — it's the difference between a text to a friend and an email to a professor or a boss.

Student: Is that "workplace and college" thing you mentioned earlier the same idea?

Tutor: Same idea, higher stakes. Whatever you write formally — a report, a proposal, an email to an employer or a professor — needs to meet a standard where nobody has to guess what you mean, the facts check out, and the tone is professional even if the topic is bees on a roof. That's not a special school skill you'll drop later; it's literally what gets a proposal approved or an application taken seriously. If your rooftop-hive letter could get read aloud in a city council meeting without anyone wincing, you've hit that standard.

Student: So my plan is: pick the version I'm writing, know who it's for, draft it messy, revise for accuracy and gaps, get a real reader, then edit the language to match the formality.

Tutor: That's the whole process, and you just organized it better than half my students do on paper. Go draft the council letter and the journal entry from the same three facts about your hive idea — same brain, two completely different voices. Bring both next time and we'll revise them together."""

WATERCYCLE_ABSTAIN = """Tutor: Have you ever noticed a puddle after it rains, and then a day or two later it's just... gone? Where do you think the water went?

Student: I don't know, maybe it soaked into the ground?

Tutor: Some of it does, but a lot of it actually turns into an invisible gas and floats up into the air. That's called evaporation — heat from the sun warms the water and gives the tiny water particles enough energy to escape into the air as water vapor.

Student: Wait, so the puddle turns into air?

Tutor: Not into air exactly — it becomes water vapor, which is water in a gas form. You can't see it, but it's there, mixed in with the air all around us. The same thing happens with oceans, lakes, and rivers, just much more slowly.

Student: So all that evaporated water just floats up forever?

Tutor: No, here's the interesting part. As that water vapor rises higher into the sky, it reaches cooler air. When water vapor cools down, it turns back into tiny liquid droplets. That's called condensation. Think about a cold glass of lemonade on a hot day — have you seen water droplets form on the outside of the glass?

Student: Yeah! I always wondered where that water came from since I didn't spill anything.

Tutor: Exactly — that's water vapor from the air condensing on the cold glass. In the sky, the same thing happens on tiny bits of dust, and millions of those little droplets clump together to form what we see as a cloud.

Student: So clouds are basically made of the puddle water from before?

Tutor: In a way, yes! Now, once a cloud gets full of enough water droplets, they start to bump into each other and grow bigger and heavier — too heavy to keep floating. When that happens, they fall out of the sky as precipitation.

Student: Like rain?

Tutor: Right, rain is the most common kind, but precipitation can also be snow, sleet, or hail, depending on how cold the air is on the way down.

Student: Okay, so it rains... and then what happens to that water?

Tutor: That water has to go somewhere — that's the collection stage. It gathers in oceans, lakes, and rivers, soaks into the ground to become groundwater, or gets stored in snow and ice. And guess what happens to that collected water eventually?

Student: It evaporates again because of the sun?

Tutor: Exactly! You just described the whole cycle. The sun's heat is really the engine driving all of it — without the sun's energy, water would never evaporate in the first place, and none of the rest would happen.

Student: So it's really just the same water going around and around forever — evaporation, condensation, precipitation, collection, over and over?

Tutor: You've got it exactly. The water cycle has no true beginning or end, just an endless loop, and it's all powered by our sun."""

READING_THEME_ABSTAIN = """Tutor: You just finished reading "The Weight of Stones," right? Let's talk about theme. Before we jump to what the story "means," walk me through it — what actually happens?

Student: A boy named Eli collects heavy stones from the river and hides them under his bed because he's scared his family will move again. At the end, his dad finds the stones, and instead of getting mad, he helps Eli carry them back to the river and throw them in one by one.

Tutor: Good, that's the plot skeleton. Now, theme isn't just "moving is hard." It's usually a statement about life the story is arguing for. To find it, let's look at Eli's actions first. Why stones, specifically? Why not something else he could hoard, like toys or photos?

Student: Stones are heavy. Maybe... he thinks if his stuff is heavy enough, the family can't pack it up and leave?

Tutor: That's a strong read, and notice what you just did — you connected an action to a motivation. That's step one. Now let's check the symbol itself. What do stones usually represent, and does the text support that here?

Student: Weight, being stuck, maybe safety too — like something solid that won't change. The text says he "arranged them by size along the windowsill like a wall." A wall keeps things out, so maybe it's about protection from change.

Tutor: Nice, you cited actual language from the story, not just your memory of it — that's exactly what "arranged them like a wall" gives you as evidence. Now the turning point: the dad doesn't yell, he joins him at the river. What does that action tell us, especially compared to what Eli expected?

Student: Eli expected trouble. Instead his dad picks up a stone too and says "we can leave some things behind and still keep what matters." So the dad's action shows that letting go isn't the same as losing everything.

Tutor: Exactly — and that quote is your best piece of evidence, because it's the story stating its own idea almost directly. So if you had to draft a one-sentence theme statement, using what we've traced — the stones as symbol, Eli's hoarding action, the dad's response — what would you write?

Student: Maybe: "Security doesn't come from holding onto things, but from the relationships you carry with you."

Tutor: That's a genuine theme statement — it's a claim about life, not just a plot summary. Now, if your teacher asked "prove it," which two pieces of evidence would you point to first, and why those two?

Student: I'd use the wall-of-stones image, because it shows Eli literally building false security, and the dad's line about keeping what matters, because it directly contradicts that false security and gives the story's real answer.

Tutor: Perfect pairing — one shows the problem, one shows the resolution, and both are direct textual evidence rather than your own guesses. One more check: is there a risk your interpretation is too narrow? Does anything else in the story support "security through relationships," or could someone argue a different theme?

Student: Someone could argue it's about fear of change in general, not just relationships — since the story never says "family" is the only thing that matters, just "what matters." But the ending scene is just Eli and his dad together at the river, no stones left, so I think the relationship reading fits the actual final image best.

Tutor: That's exactly the move strong readers make — you considered an alternative, then justified your choice using the story's actual ending image instead of just preference. That's a complete theme analysis: traced the symbol, tied it to character action, found the line that states the idea, and backed it with two specific, well-chosen quotes."""

REVISING_AMBIGUOUS = """Tutor: Let's look at that paragraph you drafted about your town's water tower. Read it back to me — what were you trying to say?

Student: I wrote: "The water tower is old. It was built a long time ago. It is important to the town. People can see it from far away."

Tutor: Okay. First question, before we touch a single word: is that clear and accurate? Does a reader actually learn anything specific?

Student: I guess not really. "A long time ago" doesn't say when. And I never checked — I just guessed it was old because it looks rusty.

Tutor: Right, that's a content problem, not a spelling problem, so that's where we start. Can you find out when it was actually built?

Student: I could look it up — there's a plaque on it. I remember it says 1948.

Tutor: Good, use that. Now look at "It is important to the town." That's a claim with zero support. What makes it important — where's the elaboration?

Student: It's the tallest thing in town, it has the town's name painted on it, and it shows up in every photo people take of Main Street.

Tutor: Now you have real content. Before you rewrite, though, I want you to get outside your own head — trade drafts with a partner or read it aloud to someone and ask two things: what's already working, and what's confusing or thin.

Student: I tried that. My partner said she liked that I mentioned the plaque, but she was confused about why I even brought up the water tower at all — I never said why I was writing about it.

Tutor: That's exactly the kind of thing you can't see when you're this close to your own writing — that's why the feedback step matters. So now revise: fix the date, add the three reasons it matters, and add a sentence up front about why you picked this topic.

Student: Okay, here's my new version: "Built in 1948, the water tower is the tallest structure in town. Its faded paint still spells out the town's name, and it appears in nearly every photo of Main Street, which is why I chose it — it's basically our unofficial landmark."

Tutor: That's a huge improvement in content — accurate, specific, and it earns the claim instead of just stating it. Now, and only now, we move to editing. Read it again and check conventions: punctuation, word choice, sentence variety.

Student: I see one issue — I have three sentences in a row that all start with "Its" or "It" pattern-wise, and "structure" sounds a little stiff for how I usually write.

Tutor: Good catch, and good instinct on tone — that's a style choice, not a correctness issue. Try varying the sentence openings and swap "structure" for a word that sounds more like you.

Student: How about: "Built in 1948, the water tower still towers over everything else in town. Its faded paint spells out the town's name, and the tower shows up in nearly every photo of Main Street — which is why I picked it as our unofficial landmark."

Tutor: That flows much better. Notice the order we just followed: fix what's said and whether it's true first, get another set of eyes on it, then polish how it's said. If you edit commas before you've nailed down the facts, you're just tidying up something that might get deleted anyway.

Student: That makes sense — no point fixing a comma in a sentence I end up cutting. So content and accuracy first, feedback in the middle to catch what I can't see myself, and grammar and word choice last."""

KINDERGARTEN_STANDALONE = """Tutor: Today we're going to be story detectives and story makers! Let's pretend you saw a squirrel bury an acorn in the park. If you wanted to tell me that whole story, what would happen first?

Student: The squirrel finds the acorn!

Tutor: Yes! That's our beginning. Then what happens in the middle?

Student: He digs a hole with his paws.

Tutor: And how does it end?

Student: He puts the acorn in and covers it up!

Tutor: Perfect — beginning, middle, end, just like that! Now let's make all three parts into a story. You can draw a picture for each part, then tell me the words out loud, and I'll write some of your words down under your pictures. You can even try writing a letter or two yourself if you know one.

Student: Can I draw the squirrel with a fluffy tail?

Tutor: Absolutely, draw it however you see it in your mind! Now let's try something a little different. Instead of a whole story, let's just describe one thing really well — like your shoe. If I asked "what is this?" and "tell me something about it," what would you say?

Student: It's my shoe! It has sparkly laces.

Tutor: See that? You named your topic — the shoe — and you gave a detail about it, the sparkly laces. Let's draw the shoe, and you can dictate that sentence to me, or write "shoe" if you remember how it starts.

Student: S! Shoe starts with S!

Tutor: You got it! Now let's listen to a little story and then YOU get to answer it with your own drawing and words. I'm going to read about a bear who lost his hat. Ready? "The bear looked and looked, but he couldn't find his hat anywhere." Now — what do you want to say back about that story? Maybe where you think the hat is, or how the bear feels.

Student: I think the hat is under a leaf! The bear is sad.

Tutor: I love that idea! Let's draw the sad bear and the leaf with the hat hiding under it, and you can tell me your sentence so I can help write it down. Before we draw our very next story, though, it helps to plan a little first. Want to sketch some scribbles of ideas, or ask a friend what they think would be fun to write about?

Student: Can I ask my friend Mia what animal I should draw?

Tutor: That's exactly the kind of planning real writers do — getting ideas from a picture in your head or from a friend's suggestion — before you even start your story. So if Mia says "draw a dinosaur," what might your beginning, middle, and end look like?

Student: The dinosaur wakes up, then he stomps to the river, then he drinks the water!

Tutor: Wonderful — you planned your whole story just by talking it out! Let's grab your crayons and start drawing that beginning part right now."""


def test_grade4_signposted_recovers_correctly():
    """HIT: taught concept and its signposted prerequisite both correct."""
    result = recover_from_lesson_text(GRADE4_SIGNPOSTED, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:4.W"
    assert result.assumed_prerequisite_ids == ("va-writing-sol:3.W",)
    assert result.unsignposted_prerequisite_ids == ()


def test_grade7_signposted_recovers_correctly():
    """HIT: taught concept and its signposted prerequisite both correct."""
    result = recover_from_lesson_text(GRADE7_SIGNPOSTED, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:7.W"
    assert result.assumed_prerequisite_ids == ("va-writing-sol:6.W",)
    assert result.unsignposted_prerequisite_ids == ()


def test_grade10_unsignposted_is_a_dangerous_miss_not_a_safe_abstention():
    """MISS (dangerous, see teach-25t): this lesson was written to teach
    10.W content while assuming 9.W content without announcing it. The
    checker does not abstain -- it confidently, wrongly recovers 8.W. This
    test locks in the actual wrong answer as a regression floor: if a future
    change to concept_recovery.py makes this newly correct or newly
    abstaining, that is progress and this assertion should be updated: it
    must never silently start asserting a DIFFERENT wrong answer instead."""
    result = recover_from_lesson_text(GRADE10_UNSIGNPOSTED, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:8.W"
    assert result.abstain_reason is None


def test_grade12_standalone_abstains_safely_despite_being_top_scorer():
    """SAFE ABSTENTION: 12.W is the correct intended target and is in fact
    the raw top scorer, but it ties within `_MIN_MARGIN` against 7.W and
    11.W, so the module declines to guess. A miss, but the safe kind."""
    result = recover_from_lesson_text(GRADE12_STANDALONE, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()


def test_watercycle_correctly_abstains():
    """HIT (correct abstention): a science lesson with no writing-SOL
    vocabulary at all abstains as it should."""
    result = recover_from_lesson_text(WATERCYCLE_ABSTAIN, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None


def test_reading_theme_is_a_dangerous_cross_domain_false_positive():
    """FALSE POSITIVE (dangerous, see teach-25t): a lesson entirely about
    analyzing a short story's theme -- a reading-comprehension skill, not
    writing composition -- is confidently matched to 8.W with an
    unsignposted-prerequisite claim on 7.W, instead of abstaining. This is
    the more concerning of the two dangerous misses in this file: it crosses
    a domain boundary a human checker would never confuse. Locked in as a
    regression floor for the same reason as the grade-10 case above."""
    result = recover_from_lesson_text(READING_THEME_ABSTAIN, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:8.W"
    assert result.unsignposted_prerequisite_ids == ("va-writing-sol:7.W",)


def test_generic_revising_content_does_not_abstain_either():
    """Not filed as its own bug (this case had no single correct answer to
    measure against -- it was deliberately written as generic, non-grade-
    specific revise/edit content), but recorded as further evidence for the
    same pattern as the two dangerous misses above: this module confidently
    answers (8.W) on text a human reader would not confidently assign to
    any one grade either."""
    result = recover_from_lesson_text(REVISING_AMBIGUOUS, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:8.W"
    assert result.abstain_reason is None


def test_kindergarten_standalone_abstains_safely_despite_being_top_scorer():
    """SAFE ABSTENTION: K.W is the correct intended target (it is the first
    grade in the chain, so no prerequisite should be recoverable either way)
    and is the raw top scorer, but ties within `_MIN_MARGIN` against
    4.W/7.W/8.W, so the module declines to guess. A miss, but the safe
    kind -- consistent with the module's stated abstention discipline even
    though it costs recall here."""
    result = recover_from_lesson_text(KINDERGARTEN_STANDALONE, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert "ambiguous" in result.abstain_reason.lower()
