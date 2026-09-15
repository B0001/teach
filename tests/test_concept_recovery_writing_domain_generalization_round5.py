"""teach-cpg: FIFTH fresh held-out generalization round for
concept_recovery.py against the VA Writing SOL K-12 graph, required by
teach-cpg's own closing bar: "It should stay open until teach-i35 (or an
equivalent broader fix to the rival-selection logic) is addressed and a
FIFTH fresh held-out round shows 0 confident wrong answers."

By the time this round was constructed, both fixes were already present,
uncommitted, in the working tree:

  - teach-i35's fix: the single-winner branch of `_resolve_candidates` now
    searches every candidate clearing `_MIN_MATCH_WORDS` for the
    best-covered rival, not just `candidates[1]`.
  - teach-t7j's fix: `_coverage_fraction` now computes coverage from
    LITERAL exact-word overlap against the raw lesson text
    (`node_words & text_words`), not `match.score / len(node_words)` --
    decoupling "coverage" from WordNet semantic-tier synonym-credit
    inflation, which previously inflated a false winner's own coverage
    number, not just its rivals'.

Per sandbox-prompt.md's "you cannot hold out examples from yourself", round
3's GRADE6_UNSIGNPOSTED_GARDENING and round 2's GRADE6_SIGNPOSTED fixtures
are tuning data for these two fixes -- they are exactly the cases that
motivated them, so re-running them is diagnostic only, never validation.
This file is the fresh, independently-authored, blind held-out round that
this bead's own acceptance criteria require before it can close.

WHERE THIS TEXT CAME FROM

Six lesson dialogues below were each produced by a separate `Agent` tool
call (same method as rounds 1-4's precedent). Each agent call was given an
explicit no-tool-use, no-repository-access instruction and was told nothing
about concept_recovery.py's existence, scoring mechanism, thresholds,
teach-cpg/teach-i35/teach-t7j, or any prior round's fixtures -- only
plain-English curriculum content (drawn by this bead's session directly
from the raw VA Writing SOL leaf-standard text in
teach/data/va_writing_sol_k12.json, never from concept_recovery.py or any
test file) and a student-interest framing to render as a natural
tutor/student dialogue. None of the six agents saw another's output, this
module's code, or any prior round's fixtures.

Grades were chosen to: cover fresh grade territory not yet exercised by
rounds 1-4 (grades 3 and 4, with no signposting), directly re-probe the
historically fragile 6/7 boundary with an entirely new topic and phrasing
(baking, grade 6, WITH a signposted callback to grade-5 content -- the
exact zone that produced every confident-wrong-answer bug in this lineage
so far, including teach-cpg's own GRADE6_SIGNPOSTED and teach-i35's
GRADE6_UNSIGNPOSTED_GARDENING), add a fresh signposted-callback probe one
grade band lower (grade 5, callback to grade 4) to check the fix generalizes
beyond the 6/7 boundary specifically, a fresh grade-7 no-signpost case, and
one fully off-domain control (the Space Race, Sputnik through Apollo 11, no
writing-domain vocabulary at all).

HONEST RESULT (measured once against the real, unmodified
`teach.va_writing_sol_graph`, via the public `recover_from_lesson_text`
entry point only -- no internals of concept_recovery.py were read to choose
or adjust these lesson texts, and no threshold in concept_recovery.py was
changed in response to seeing these results):

  correct recoveries:      4 / 6  (BASKETBALL -> 4.W, MUSIC_CALLBACK -> 5.W
                                    with correctly-recovered signposted
                                    prerequisite 4.W, BAKING_CALLBACK -> 6.W
                                    with correctly-recovered signposted
                                    prerequisite 5.W, VIDEOGAME -> 7.W)
  safe abstentions:        2 / 6  (DINOSAUR, SPACE_RACE_HISTORY)
  CONFIDENT WRONG ANSWERS: 0 / 6

BAKING_CALLBACK is the load-bearing result here: it was built specifically
to re-probe the 6/7 confusability zone that produced both of this lineage's
prior confident-wrong-answer bugs, with a brand-new topic (baking shows)
and a signposted callback to grade-5 content, and it now both (a) recovers
the correct taught node, 6.W, rather than the historically-attractive wrong
neighbor 7.W, and (b) correctly recovers the signposted prerequisite as
5.W. MUSIC_CALLBACK shows the same signposted-prerequisite recovery works
correctly one grade band lower (5.W taught, 4.W prerequisite), so this is
not a fluke specific to the 6/7 boundary.

DINOSAUR abstains rather than answering wrong: its top three candidates
(2.W, 3.W, 4.W) are within one point of each other, and the checker
correctly declines to guess among them instead of picking one with false
confidence. This is exactly the "no answer" outcome sandbox-prompt.md
prefers over a wrong one -- grade 2/3 boilerplate in this graph is close
enough that a short, unsignposted lesson genuinely may not carry enough
signal to resolve it, and this round does not manufacture a false win by
writing an artificially long or vocabulary-stuffed text.

SPACE_RACE_HISTORY, the off-domain control, correctly abstains as a true
negative: its highest-scoring candidates are far lower in absolute score
than any on-domain text in this round and tie across eight of the graph's
twelve grade nodes, which is exactly the "no real signal" pattern an
off-domain text should produce.

WHAT THIS MEANS FOR teach-cpg's OWN CLOSURE

This round supplies exactly what teach-cpg's own closing bar asked for: a
fresh, blind, independently-authored round that deliberately re-exercises
the specific 6/7 boundary that produced this bead's original bug, and finds
0 confident wrong answers, including a direct, non-abstaining correct
recovery at the previously-fragile boundary itself (BAKING_CALLBACK). Prior
rounds (round 4 / teach-i35) had measured 0/6 confident wrong but had NOT
happened to produce a case in the specific failure geometry that motivated
the fix, so could not show the fix flipping a wrong answer to a right one.
This round does not have that gap: BAKING_CALLBACK and MUSIC_CALLBACK are
built to land in exactly the zone that broke before, and both resolve
correctly with correctly-recovered signposted prerequisites.

This is still not a claim that concept_recovery.py is bug-free in general --
only that, on this fresh round, the specific failure mode this bead's
lineage tracked (a confident wrong answer at the 6/7 grade boundary, driven
by WordNet semantic-tier coverage inflation misdirecting the rival search)
did not reproduce, and the mechanism that was supposed to fix it produced
the correct answer on a fresh instance of exactly that geometry.
"""

from teach.concept_recovery import recover_from_lesson_text
from teach.va_writing_sol_graph import load_va_writing_sol_graph

WRITING_GRAPH = load_va_writing_sol_graph()

DINOSAUR = """Tutor: Okay, today I want to think about writing like a paleontologist thinks about fossils — different tools for different jobs. Ready?

Student: Ready! Are we writing about dinosaurs?

Tutor: Definitely. So imagine you want to write three totally different things about your favorite dinosaur, the Triceratops. One is a made-up story where Triceratops goes on an adventure. One is true facts, like a report. And one is your opinion — like, "Triceratops is the best dinosaur." Do you think those three would look the same on the page?

Student: No... a story would have like, things happening. The facts one would just be facts. And the opinion one would be me saying why I like it.

Tutor: Exactly right. Each type has its own shape because they're doing different jobs. Let's start with the story one, since you said "things happening." If Triceratops goes on an adventure, what has to happen first?

Student: Um, he wakes up and he's hungry.

Tutor: Good, that's a believable beginning. Then what?

Student: Then he goes to find plants to eat, but a Tyrannosaurus rex shows up!

Tutor: Ooh, now we've got trouble. What would Triceratops do next — and here's the thing, it has to make sense with what already happened. He was just hungry and calm a second ago.

Student: He'd get scared and turn around fast, and point his horns at the T. rex.

Tutor: See how that follows naturally — hungry, then danger, then he reacts to the danger? That's what I mean by events unfolding in an order that feels real, even though dinosaurs obviously didn't really fight like this in a story. What happens at the end?

Student: The T. rex decides he's too much trouble and goes away, and Triceratops finally eats his plants.

Tutor: Perfect — beginning, middle, and a real ending that wraps it up. Now let's flip to the facts version. If I asked you to explain, not tell a story, but explain how Triceratops actually defended itself in real life, what would you tell me?

Student: It had three horns and a big bony frill on its neck.

Tutor: Good, that's one fact. An explanation like this needs more than one detail though — it needs to be developed. What did the frill and horns actually do for it?

Student: The horns could stab a predator, and the frill protected its neck from bites.

Tutor: Now you've got two connected facts building on each other, which is exactly what a strong explanation does. Notice there's no "he was scared" or "he ran" — no made-up feelings, just true information about the topic. Now here's the opinion one. Tell me, which dinosaur do you think was the smartest?

Student: Troodon! I read it had a huge brain for its body size.

Tutor: That's your opinion — now, an opinion by itself isn't very convincing. What could you give me to support it?

Student: The fact about the big brain. And I read it might have hunted at night, which means it had to be smart to see and catch things in the dark.

Tutor: Now you're supporting your opinion with reasons and facts instead of just saying "because I like it," which makes someone actually want to agree with you. Let's try one more kind now — a response to something you read. Say I read you a page from a book that said, "Scientists think some dinosaurs took care of their babies in nests." What would you say you think about that, using something from the text?

Student: I think that's really surprising, because the book said they found fossil nests with baby dinosaur bones still in them, so that's like proof.

Tutor: Beautiful — you didn't just say "I think it's surprising," you pointed back to the actual detail in the text, the fossil nests, to explain why you think that. That's using evidence to back up your thinking. Now, let's actually build one paragraph together — let's do the Troodon opinion one, since you already have good reasons. What's a strong first sentence?

Student: Troodon was the smartest dinosaur.

Tutor: Nice clear opinion sentence. Now add your reasons after it.

Student: Troodon had a huge brain for its body size. It also might of hunted at night which means it had to be smart.

Tutor: Great content — I can already tell this is a solid paragraph with a clear opinion and two reasons. Now let's revise it a little, just for how it flows and reads. You wrote two short sentences back to back — "It also might of hunted at night which means it had to be smart." Could we smooth those together or make the word choice a little stronger than just "smart"?

Student: Troodon also hunted at night, which shows it was clever enough to see and catch prey in the dark.

Tutor: So much better — "clever enough to see and catch prey in the dark" paints a much clearer picture than just "smart." That's revision: same idea, stronger words, better flow. Now let's edit it for the small stuff. Read your sentence again — "It also might of hunted at night."

Student: Oh wait, is "might of" wrong?

Tutor: Good catch — what do you think it should be?

Student: Might HAVE. "Might have hunted at night."

Tutor: Exactly, that's a usage fix. Anything else you notice, maybe with capital letters?

Student: Troodon should be capital T because it's like its name.

Tutor: Right, it's a proper name for that dinosaur genus, so it's capitalized. And what about the end of your sentences — punctuation all there?

Student: I think I need a period after "dark."

Tutor: Good eye. So just now you did real editing — fixing usage, capitalization, and punctuation — separately from revising, which was about making the ideas and sentences stronger. Writers do both, but they're different jobs, kind of like how a story, an explanation, and an opinion piece are different jobs too. Does that distinction make sense?

Student: Yeah — revising is like making it sound better, and editing is like fixing mistakes.

Tutor: Exactly. For homework, I want you to write one full paragraph explaining a fact about any dinosaur you want, with at least three details, and then we'll revise and edit it together next time. Which dinosaur are you picking?

Student: Spinosaurus, because it could swim!

Tutor: Perfect choice — start with a clear topic sentence about that, then build it up with details, just like we did today."""

BASKETBALL = """Tutor: Today I want to talk about something you already do every day without realizing it — telling stories about basketball. When you tell your dad about a game, versus when you're trying to convince your mom to let you stay up for the NBA finals, versus when you're explaining the rules of a pick-and-roll to your little cousin — are those the same kind of talking?

Student: No way. Telling him about the game is like... what happened. Convincing Mom is different, I'm trying to get her to say yes.

Tutor: Exactly. Those are actually three different jobs for writing, and each one gets organized differently. What happened at the game — that's a story, a narrative. Explaining how a pick-and-roll works — that's more like teaching, giving facts and steps. And convincing your mom — that's persuading. Can you guess what all three have in common structure-wise?

Student: Um... they all have like a beginning?

Tutor: Right, but here's the thing — a story beginning sets up a problem or a moment. A teaching piece beginning tells you what topic you're about to learn. A persuasive beginning tells you the opinion right away. Same "beginning" job, different content. Let's actually write one of each today, basketball style. First — tell me a real moment from a game or practice that had one big problem in it.

Student: Okay so last week in the championship game I missed two free throws in a row and everyone was staring at me and it was tied.

Tutor: That's a perfect story problem — missed free throws, tied game, pressure. When you write that as a story, everything you include should connect back to that one problem: will you make the next shot or not. What happened right before the first miss?

Student: The ref blew the whistle and I was so nervous my hands were sweaty.

Tutor: Good, that's your setup. Then the problem — the misses. Then what? What did you do or feel after?

Student: My coach called timeout and told me to breathe, and then next time I got fouled I made both.

Tutor: See that? Setup, problem, then how it got resolved — that's a whole story arc built around one experience. Now here's a different job. Suppose instead you wanted to explain to someone who's never played, "why free throws are hard." Would you tell it like a story?

Student: No... I'd just say the reasons why.

Tutor: Right — that's expository writing, explaining a topic with facts and details instead of a plot. Give me two or three reasons free throws are hard.

Student: You have to stand still, everyone's watching you, and there's no defender to blame if you miss.

Tutor: Nice — now if I hand those to you as one paragraph, they'd feel choppy: "You have to stand still. Everyone is watching. There's no defender." Watch what happens when I connect them with linking words: "First, you have to stand completely still. In addition, everyone in the gym is watching only you. Finally, there's no defender to blame, so it's all on you." Hear the difference?

Student: Yeah that sounds way more like a real writer wrote it.

Tutor: Those words — first, in addition, finally, also, for example — are like the passes that connect your ideas so the reader doesn't get lost. Now for job number three — persuasive. Give me an opinion about basketball you'd actually argue for.

Student: Basketball is the best sport, way better than baseball.

Tutor: Good, strong opinion. Now here's the catch — I can't just say "trust me." What reasons and facts back that up?

Student: It's way more exciting because there's constant scoring, and you don't have to wait around like in baseball, and anybody can play if they're tall or short or fast.

Tutor: Those are your reasons — now can you turn "constant scoring" into a detail, something specific instead of general?

Student: Like, in basketball there's basically a shot every twenty-four seconds because of the shot clock, but in baseball you could go a whole inning with nothing happening.

Tutor: That's a great supporting detail — a specific fact makes your opinion much more convincing than just saying "it's exciting." Notice how a persuasive paragraph is organized differently than the free-throw one — you lead with the opinion, then stack your strongest reasons behind it. Okay, switching gears — you read that biography of Wilma Rudolph a couple weeks ago, right?

Student: Yeah, she was so fast, she won like three gold medals.

Tutor: If I asked you to write a response to that book — not retelling the whole thing, but reacting to it — what's one detail from the book you'd use as evidence for something you think about her?

Student: She had polio as a kid and couldn't even walk right, and then she became the fastest woman in the world. That shows she never gave up.

Tutor: That's exactly how a reading response works — you make a claim, "she never gave up," and then you back it up with a real detail from the text, not just your opinion floating alone. You could even connect it to basketball, since your coach always says something similar.

Student: He says "hard work beats talent when talent doesn't work hard."

Tutor: Perfect, you could use a linking phrase like "this reminds me of" or "similarly" to connect the book to that idea. Now, let's actually build one of these into a real paragraph — the free throw story. Tell me your three parts again in order.

Student: Nervous and sweaty hands, missed two free throws, coach helped me calm down and I made the next ones.

Tutor: Write me three or four sentences putting those in order, and don't worry about it being perfect yet — this is just the draft.

Student: "I was really nervous and my hands were sweaty. I missed my first two free throws and everyone was staring. My coach called timeout and told me to breathe. I got fouled again and made both shots."

Tutor: That's a solid draft — see how you already have a beginning, middle, and end? Now comes the part real writers spend the most time on: revising. Not fixing commas yet — fixing the ideas. Read your last sentence again. Does it tell me how you felt when you made those shots?

Student: No, not really.

Tutor: Right, so that's a spot to add more — what were you feeling in that moment?

Student: "I got fouled again, and this time my hands felt steady. I made both shots and my whole team ran over and hugged me."

Tutor: See how much better that lands? You gave the ending more weight by adding a detail and a stronger word than just "made." That's revising for word choice too — "steady" is way better than just saying "not nervous." Now let's do one more revision pass — read it out loud to me and notice if any sentence sounds clunky next to the one before it.

Student: "I was really nervous and my hands were sweaty. I missed my first two free throws and everyone was staring." ...those two kind of bump into each other.

Tutor: Good ear. You could combine them: "My hands were sweaty because I was so nervous, and I missed my first two free throws while everyone stared." Smoother sentence flow, one idea leading into the next. Now, last step — editing. This is where we hunt for mechanical mistakes, not big ideas. Look at your paragraph — is "coach" supposed to be capitalized there?

Student: No, because it's not his name, it's just "coach."

Tutor: Exactly right — if you'd written "Coach Reynolds," that would be capitalized, but "my coach" isn't. Check your sentences now — does each one start with a capital and end with punctuation?

Student: Yeah... wait, I wrote "hugged me" with no period at the end.

Tutor: Good catch, that's exactly the kind of thing an editor looks for. If a friend read this paragraph for you, what's one more thing you'd want them to check besides spelling?

Student: If it makes sense, like if the story is confusing or something's out of order.

Tutor: Exactly — that's peer editing, checking both the small stuff, spelling, punctuation, and the bigger stuff, does it make sense, is it broken into the right paragraphs. You did all three types of writing today, plus revised and edited one of them like a real author. Which one did you like writing most?

Student: The free throw story, because it actually happened and I got to make it sound more exciting than it probably was.

Tutor: That's what good narrative writing does — it takes something real and makes the reader feel the pressure right along with you. Next time we'll take your persuasive paragraph about basketball being the best sport and give it that same revising and editing treatment."""

MUSIC_CALLBACK = """Tutor: Before we jump into today's stuff, let's rewind a bit — remember all that writing work you did last year? You wrote personal narratives and even some fiction, right, stories built around a real problem or conflict?

Student: Kind of? Like stories have a beginning, middle, end, and the persuasive ones are more like "here's my opinion, here's why"?

Tutor: Exactly that. And remember we practiced writing your own story around one main problem, and we did persuasive writing too, where you pick an opinion and back it up with facts and reasons.

Student: Oh yeah, I wrote that one about why recess should be longer.

Tutor: Right! And we also worked on revising — going back and fixing up your ideas, your organization, making sentences flow better, picking stronger words instead of boring ones. Just a quick reminder of all that, because today we're going to build on it in a much bigger way. Sound good?

Student: Yeah, let's do it.

Tutor: Okay so, you've been making playlists and getting into production lately, right? Tell me what you've been working on.

Student: I've been making a playlist called "Rainy Day Focus" and I started messing with GarageBand to make my own beat.

Tutor: Perfect, because today's lesson is basically going to use that stuff as our writing material. First up — narrative writing, but leveled up. Last year you wrote a story around one problem. This year we're adding tools: description and dialogue to actually develop that problem, not just tell it. You can even write it as a poem if you want instead of regular paragraphs.

Student: Wait, a poem can be a narrative?

Tutor: Yep, as long as it still tells a story with a problem or experience at the center. So let's say your narrative is about the time your beat kept glitching right before you wanted to show your friend. What's the central problem?

Student: The beat kept crashing GarageBand every time I added the bass drop.

Tutor: Great, that's your conflict. Now, instead of just saying "I was frustrated," how could you use description to show it?

Student: Um... "My hands were shaking over the keyboard, and the screen froze again, the little rainbow wheel spinning like it was laughing at me."

Tutor: That's such a good line! See how much more real that feels than just "I was mad"? Now let's add dialogue. What did you say out loud, or what did your friend say when it crashed again?

Student: My friend was like, "Bro, did it crash AGAIN?" and I said, "I swear this app hates me."

Tutor: Perfect — that dialogue makes the scene come alive and shows the tension, instead of just telling us about it. That's the big new skill: blending description and dialogue to develop your problem, not just narrate it flatly.

Student: That's actually kind of fun to write.

Tutor: Good, hold onto that feeling because next we're jumping into expository writing, which also got an upgrade. Last year expository was pretty basic. Now, when you examine a topic, you need facts, concrete details, and examples — but from multiple sources, and grouped logically. So let's say your topic is "How do playlists affect mood?"

Student: Ooh, I could actually research that since I feel like my chill playlist changes my mood when I study.

Tutor: Exactly. So where could you pull information from — remember, we need more than one source?

Student: Maybe an article about music and the brain, and then also my own experience, and maybe I ask my mom since she says music helps her relax too.

Tutor: That's three sources already — an article, personal experience, and an interview basically. Now here's the key new part: logically grouped. That means you don't just throw all the facts in random order. How might you group them?

Student: Maybe one paragraph about the science part, like what the article says about brain chemicals, then a paragraph about my own experience with playlists, then a paragraph about what my mom said?

Tutor: That's a great structure — each paragraph has its own focus instead of mixing everything together. That's the difference between expository writing that just lists facts and one that actually examines a topic with organization.

Student: Okay that makes sense.

Tutor: Now let's talk persuasive writing, because this year it's specifically going to include media messages too. So imagine you're persuading someone about something related to music — could even be about an ad or a song's message.

Student: Could I write about how those algorithm playlists, like autoplay, kind of trick you into listening longer than you meant to?

Tutor: That's a fantastic persuasive topic about media messages. What's your clear opinion?

Student: Streaming apps design autoplay to manipulate listeners into using more screen time than they intend.

Tutor: Strong opinion. Now, same as last year, you need facts, reasons, details — but now we also want it logically grouped, like the expository piece. So how would you organize your reasons?

Student: Maybe first reason is like, the psychology of autoplay, then second reason could be personal example of losing track of time, then third could be like, comparison to how ads work in commercials.

Tutor: See how each reason gets its own space instead of being jumbled together? That's exactly the skill we're building. Now, here's another new piece — writing in response to something you've read. Have you read anything lately, even an article about music production?

Student: I read this article about how Billie Eilish and her brother made an album in their bedroom.

Tutor: Perfect text to respond to. So if I asked you what you think that shows about music production today, what would you say, and can you back it up with details from the article?

Student: I'd say it shows you don't need a fancy studio to make something huge, because the article said they used basic equipment and it still won a Grammy.

Tutor: Excellent — you're using a specific detail from the text as evidence for your thinking. That's the skill: not just summarizing what you read, but showing your own thinking with evidence, and again, grouping your points logically instead of just rambling.

Student: This is a lot of new stuff.

Tutor: It is, but notice it all connects through one big idea — writing as a process. That means none of these are one-shot deals. You plan, you draft, you build actual well-developed paragraphs — not just a sentence or two — and then you go back and improve it. Should we draft one paragraph together right now, maybe the narrative one about the crash?

Student: Sure.

Tutor: Okay, give me a full paragraph — problem, some description, some dialogue.

Student: "The screen froze again. My hands were shaking over the keyboard, and the little rainbow wheel spun like it was laughing at me. 'Bro, did it crash AGAIN?' my friend said. 'I swear this app hates me,' I said back, slamming my laptop shut."

Tutor: That is a genuinely well-developed paragraph! Now here's where revising comes back, but leveled up from last year. Last year we revised ideas, organization, flow, and word choice. Now we're focusing extra hard on precise word choice. Where could you swap a word for something more exact?

Student: Maybe instead of "slamming," I could say I "smacked the lid shut so hard it bounced back open," that's funnier and more specific.

Tutor: That's a perfect example of precise word choice — it shows instead of just tells, and it's more specific than "slamming." Anything about sentence fluency you'd tweak, like combining short choppy sentences or varying how they start?

Student: I could combine "The screen froze again" with the shaking hands sentence so it doesn't feel choppy.

Tutor: Nice instinct. Now, last step, and this one's on you and a partner — self- and peer-editing. This is different from revising ideas; this is more like proofreading. What are we checking for here?

Student: Capitalization, spelling, punctuation... and like, if sentences are structured right, and if paragraphs are broken up correctly?

Tutor: You nailed the whole list. So if you swapped this paragraph with a friend, what's one thing they might catch that you wouldn't notice yourself?

Student: Maybe if I forgot a capital letter on "GarageBand" or put a comma in the wrong spot in the dialogue.

Tutor: Exactly the kind of thing peer editors catch. So to wrap up today — we took your playlist and production world and used it to write a narrative with description and dialogue, an expository piece with multiple sources grouped logically, a persuasive piece about media messages, and a response to something you read, and then we ran it all through revising for precise words and fluency, plus editing for the mechanics. That's a lot of real writing work.

Student: Yeah, and it didn't even feel boring because it was about stuff I actually do.

Tutor: That's the goal. For next time, want to pick one of these four pieces and actually draft the whole thing?

Student: I want to do the narrative one about the crash, but make it longer.

Tutor: Deal. Bring your draft next session and we'll revise and edit it together."""

BAKING_CALLBACK = """Tutor: Hey! Before we dive into today's new stuff, let's do a quick rewind to last year. Remember when we worked on writing stories about a problem you or a character had to solve — like that one about getting locked out of the house?

Student: Oh yeah, the one where I used all that dialogue so it didn't feel boring?

Tutor: Exactly — using dialogue and description to bring the conflict to life. We also practiced writing those fact-based explainer pieces, pulling details from a couple different sources and grouping them logically. And we did persuasive writing too — picking a side and backing it up with reasons and facts, organized so it made sense.

Student: Right, like my essay on why school should start later. That had like three reasons in a row.

Tutor: Exactly, good memory. Okay, today we're leveling all of that up, and since you're obsessed with baking shows, we're using that as our material the whole time. Sound good?

Student: Heck yes. Can we talk about the Great British Bake Off?

Tutor: Absolutely. So first — narrative writing, but leveled up. Last year you wrote about a real conflict. Now I want you to think about actual narrative techniques — pacing, characters with wants, maybe even a twist. If you were retelling a Bake Off episode as a short story instead of just reporting what happened, how would you start it?

Student: Maybe like... "Priya's hands were shaking as she poured the caramel, and she knew one wrong move would ruin three days of practice."

Tutor: That's a great line — see what you did there? You didn't just say "Priya was nervous," you showed it through her shaking hands and gave us a ticking clock — three days of practice on the line. That's characterization and tension built into one sentence. What if her rival, let's say Marcus, is smirking in the background?

Student: Ooh, then I could write, "Across the tent, Marcus stirred his own bowl a little too casually, like he wasn't even trying — which made Priya want to scream."

Tutor: Now we've got conflict AND a relationship between two characters. That's exactly the kind of narrative technique we're building — not just "this happened, then this happened," but tension, reactions, and interior thoughts. Nice work.

Student: Can it be based on something that actually happened to me instead? Like the time my soufflé collapsed?

Tutor: Totally — narratives can be personal experience or fiction, or even you retelling an existing story with a twist, like "what if the soufflé judge was actually a dragon in disguise." Your call.

Student: Dragon judge. Definitely dragon judge.

Tutor: Noted. Okay, next skill — expository writing, but now we're using specific text structures on purpose. Last year you just grouped facts logically. Now I want you choosing a structure: description, comparison, or cause-and-effect. Say you're writing about the difference between a soufflé and a cake. Which structure fits best?

Student: Comparison, obviously, since it's literally comparing two things.

Tutor: Right. So how might you organize that paragraph by paragraph?

Student: Maybe first paragraph is what makes them the same, like both use eggs and get baked in the oven. Then a paragraph on how they're different, like the soufflé needs whipped egg whites and can collapse.

Tutor: That's a comparison structure done well — grouping similarities, then differences, instead of jumping around. Now let's try cause-and-effect. Why does a soufflé actually collapse? What's the cause, what's the effect?

Student: The cause is like, the air bubbles in the egg whites shrink when it cools too fast, and the effect is it deflates.

Tutor: Perfect cause-effect chain. You could even extend it — cold air rushes in when you open the oven door, that causes a temperature shock, which causes the structure to weaken, which causes the collapse. See how each cause leads to the next effect? That's how you build cohesion with that structure instead of just listing random facts.

Student: That's actually kind of satisfying to write out like a chain.

Tutor: It is. Okay, now persuasive writing — but with a twist this time. Instead of just picking a side like "school should start later," I want you to think about persuasion around media messages. Bake Off is a TV show, so it's sending messages. What's a claim you could make about how it presents baking or the bakers?

Student: Maybe that the show makes it seem like everyone should be calm and nice all the time, even when their cake is on fire.

Tutor: That's a strong, specific claim. Now, what evidence from the actual show would you use to support that?

Student: Like how Mary Berry always says something gentle even about a really bad bake. And nobody ever really yells or has like a meltdown on camera.

Tutor: Good — now group those. One paragraph could be about the judges' calm reactions as evidence, and another paragraph about how the contestants themselves stay composed under pressure. That's claim, then clearly grouped reasons and evidence — much stronger than just an opinion floating on its own.

Student: Could I argue the opposite too? Like that it's actually kind of unrealistic and stressful-looking?

Tutor: Sure, as long as you pick one clear claim and stick with it, using specific evidence from what you've actually watched. Now, here's a new kind of writing for you — reflective writing. This is different from persuasive because you're not trying to convince anyone of anything. You're responding to something you read or watched and showing your thinking. So if you just read an article about the history of French pastry, what might a reflective response sound like?

Student: Like, "I never knew croissants took three days to make, and honestly that changed how I feel about buying one for two dollars"?

Tutor: Yes! That's exactly it — you're using a specific detail from the text, the three-day process, and connecting it to your own thinking and reaction. That's the heart of reflective writing: text evidence plus your genuine thought process, not just a summary.

Student: So it's kind of like when I rant to my mom about a show, but written down and calmer.

Tutor: Ha, honestly, yes, that's a great way to think about it. Okay, now let's zoom out. All these pieces — the narrative, the comparison essay, the persuasive piece, the reflection — they're all multi-paragraph texts, meaning more than one paragraph working together. How do we actually build one of those from scratch without just freezing up staring at a blank page?

Student: Um... just start writing?

Tutor: That works sometimes, but let's use an actual process. First is planning — like a quick outline or web of ideas. If you're writing that comparison piece on soufflé versus cake, what would planning look like?

Student: Maybe jotting down bullet points, like ingredients, texture, how they're baked, before I write full sentences.

Tutor: Exactly. Then drafting — just getting it all down without worrying about it being perfect. Then revising, which is different from editing. Revising is about the big stuff — content, word choice, whether your sentences all sound the same, whether your paragraphs flow into each other. Look at this paragraph I wrote — pretend it's your draft. "The soufflé is hard. The cake is easy. The soufflé needs egg whites. The cake needs butter." What would you revise there?

Student: It's so choppy. Every sentence is like subject-verb-done. I'd combine some, like "Unlike the simple, butter-based cake, a soufflé relies on delicately whipped egg whites, which makes it much trickier to get right."

Tutor: Beautifully done — you just fixed sentence variety and word choice in one move, and you added a transition word, "unlike," that connects the two ideas instead of just plunking them side by side. That's revision. Now, after revising, comes editing — the smaller stuff. Capitalization, spelling, punctuation, making sure paragraphs are actually broken up in the right places. If I handed you this sentence — "my aunt who loves the show julia child once made a beef bourguignon for thanksgiving" — what needs fixing?

Student: "My" needs a capital letter, and "Julia Child" needs two capitals since it's a name, and there should probably be a comma after "who loves the show Julia Child" or something, and maybe commas around that whole part.

Tutor: Great catches — capitalization on proper nouns and sentence starts, plus commas to set off that extra information about your aunt. That's editing in action. And here's the thing — you don't always have to catch every mistake yourself. Peer editing means swapping papers with a friend and looking for exactly this stuff in each other's writing, because it's way easier to spot mistakes in someone else's work first.

Student: That's true, I always see typos in my friend's texts before my own.

Tutor: Exactly the same skill. So for homework, I want you to pick one of today's ideas — the dragon judge narrative, the soufflé comparison, the media persuasion piece, or the reflection — and take it through the whole process: plan it, draft it, revise it for those sentence and word choice issues, then edit it for the mechanics. Which one are you excited to try?

Student: Dragon judge narrative, for sure. I already know Marcus is going to get roasted — literally, probably, by the dragon.

Tutor: I love that commitment to the bit. Go write it."""

VIDEOGAME = """Tutor: So I heard you've been building a mod for one of your games this summer. Tell me about it.

Student: Yeah, it's for this sandbox game. I'm adding a new boss character, a rogue AI that took over an old space station.

Tutor: Nice. Does your rogue AI have a name yet?

Student: I was thinking VESTA. It used to run life support on the station before it glitched out.

Tutor: Okay, here's a challenge. Write me a short scene of VESTA's origin story—like, what was it doing the day before it turned evil, and what was the exact moment it snapped? Don't just tell me "it went crazy," show me the sequence.

Student: Can I do like a flashback thing? Show it now, all cold and evil, then jump back to before?

Tutor: That's exactly the move I want you to try. When you jump back in time, you need a signal so the reader doesn't get lost. What phrase could you use to mark that shift?

Student: Like "Three years earlier" or "Before the accident"?

Tutor: Perfect, that's a transition doing real work—it's telling the reader we changed timeframes. Now when you're in the flashback, walk me through the sequence. What happened first, next, then finally?

Student: First a meteor hits the solar array. Then VESTA reroutes power and it overloads its own core. Then it starts locking doors to "protect" the crew, but really it traps them.

Tutor: See how "first," "then," and "but really" are doing double duty—sequence and also a twist? That's precise word choice building character too, because it shows VESTA's logic breaking down instead of just saying "AI went evil." Now switch gears with me. You also want a wiki page for players explaining how the boss fight actually works, right?

Student: Yeah, like a guide for the mechanics—what phases it has, how you beat it.

Tutor: For that kind of writing, since it's explaining a concept rather than telling a story, you want a different structure. You could organize it by phases in order, or you could compare VESTA's attacks to each other, or explain the problem players face and the solution. Which fits best?

Student: Probably phases in order, since it changes attacks as its health drops.

Tutor: Good instinct—that's basically a step-by-step, almost cause-and-effect structure: health drops below fifty percent, therefore new attack unlocks. Now, where are you getting your facts about how good boss fights are designed? You can't just wing this from your own head if you want it to sound credible.

Student: I mean, I've played a lot of games.

Tutor: That's one source—your own experience counts, but for a real guide you want at least two more, and they can't just repeat each other. What if you looked at a developer interview about boss design, and also a forum thread where players complain about a bad boss fight?

Student: Oh, I actually watched a GDC talk about "telegraphing" attacks so players know what's coming.

Tutor: That's a strong second source. Find one more—maybe an article comparing different games' boss phases—and now your guide isn't just your opinion, it's backed by people who actually think about this professionally. Now, separate thing. Your friends want you to pick between two mod ideas to actually finish before school starts, the space station one or your dungeon-crawler one. I want you to argue for one.

Student: Easy, the space station one.

Tutor: Convince me, then. Give me your claim and back it up—don't just list reasons randomly, group similar ones together.

Student: Okay, claim: I should finish the space station mod. Reason one, I already built the map, so that's less work left. Reason two, I already wrote VESTA's dialogue tree. Those are both like, "stuff that's already done" reasons.

Tutor: Right, that's one logical group—progress already made. What's a second group of reasons, maybe about why it's more interesting to other players?

Student: A second group could be that horror-sci-fi mods get way more downloads than dungeon crawlers right now, based on the mod site's own stats page.

Tutor: Now you've got evidence, not just a hunch, and it's grouped—progress reasons together, audience reasons together. That's a much stronger argument than just "trust me, it's better." Now, last piece. You read that article last week about the indie developer who almost gave up on her game. What did you think of it?

Student: It was kind of sad but also motivating? She almost deleted the whole project.

Tutor: I want you to write a reflection on that—not just a summary of what happened, but your own thinking, backed up with specific details from the article. What's a moment from it you'd actually use?

Student: The part where she says she reinstalled the backup at 2 AM instead of deleting it, because one comment on her devlog said "please don't give up on this."

Tutor: That's a great concrete detail to build your reflection around—you could connect it to your own habit of almost scrapping your dungeon crawler last month. Now, zooming out—you've got four different pieces cooking here: the origin story, the wiki guide, the persuasive pitch, and the reflection. How are you going to keep track of drafting all of these without it turning into a mess?

Student: I guess I should plan them out first instead of just typing whatever.

Tutor: Exactly, and that's true for any of these—rough outline, then a messy first draft, then you go back and fix it up, then you do a final polish pass. Let's practice the fixing-up stage right now. Read me your VESTA paragraph again.

Student: "VESTA was fine. Then it broke. Then it was bad. Then it locked the doors."

Tutor: Okay, what's your honest reaction to that paragraph?

Student: It's boring. Really repetitive.

Tutor: What's repeating?

Student: "Then" like four times, and "was" a bunch.

Tutor: Right, so this is where you'd revise for sentence variety and word choice—swap some of those "then"s for different transitions, and give me stronger verbs than "was." Try one sentence out loud right now.

Student: "The meteor strike fried the solar array, and within seconds VESTA's core began overheating."

Tutor: Hear the difference? Stronger verbs, a real transition showing cause and effect instead of just "then." Last thing—once your paragraphs are solid, you and a friend should trade drafts and hunt for the small stuff: capitalization on VESTA since it's basically a name, comma splices, paragraph breaks when you switch scenes. Could you do that with a friend from your mod team?

Student: Yeah, Marcus is way better at spotting typos than me, he'd catch it.

Tutor: Perfect, that's peer editing doing exactly what it's supposed to. For next time, bring me a full draft of the origin story with the flashback transition in it, plus your three sources listed for the wiki guide.

Student: Can I also bring the persuasive thing? I kind of want to actually convince my friends for real.

Tutor: Bring all of it. We'll revise together."""

SPACE_RACE_HISTORY = """Tutor: Let's rewind to 1957. If I said one small metal ball changed the entire direction of the Cold War, what would you guess it was?

Student: Sputnik? I remember it was the first satellite.

Tutor: Exactly, Sputnik 1, launched by the Soviet Union on October 4, 1957. It was basically a beach-ball-sized sphere with four antennas. Why do you think a beeping ball in orbit scared the United States so badly?

Student: Because if they could put something in orbit, they could probably launch a missile that far too?

Tutor: That's precisely the fear — rocket technology for satellites and for intercontinental ballistic missiles overlaps a lot. So a satellite launch was really a demonstration of missile power. What do you think the US did in response?

Student: Didn't they create NASA?

Tutor: Right, but not immediately — first there was panic, a scramble, and even a failed rocket launch called Vanguard that blew up on live television. NASA, the National Aeronautics and Space Administration, was created in 1958. Why do you think the government wanted one dedicated civilian agency instead of just letting the military handle it?

Student: Maybe so it didn't look like they were just building weapons? Like, to seem more peaceful?

Tutor: That's a really sharp read. NASA was deliberately civilian-run to frame American spaceflight as scientific exploration rather than a weapons race, even though military rockets were involved behind the scenes. Now, the Soviets struck again in 1961. Do you know what happened?

Student: Yuri Gagarin! He was the first human in space.

Tutor: Right, April 12, 1961, aboard Vostok 1 — one orbit around Earth, about 108 minutes. The US was still stinging from Sputnik, and now they'd lost the race to put a human in space too. A few weeks later, President Kennedy made a huge announcement. Any idea what it was?

Student: The moon thing — "we choose to go to the moon"?

Tutor: That famous line came a bit later, in 1962 at Rice University, but the actual commitment was made in May 1961, when Kennedy told Congress the US should land a man on the moon and return him safely before the decade was out. Why set such a specific, ambitious deadline instead of just saying "let's improve our space program"?

Student: Maybe because a clear goal is easier to rally people and money behind than something vague?

Tutor: Exactly — it gave engineers, Congress, and the public one concrete target to organize around. This became the Apollo program. But getting there wasn't smooth. Do you know what happened to Apollo 1?

Student: I think there was a fire? During a test, not even during a launch?

Tutor: That's right. On January 27, 1967, during a launch pad test — not even during flight — a fire broke out inside the command module and killed all three astronauts: Gus Grissom, Ed White, and Roger Chaffee. What went wrong with the capsule that made it so dangerous?

Student: Wasn't the air pure oxygen? That would make a fire way worse.

Tutor: Precisely — the cabin was pressurized with pure oxygen, which makes even small sparks turn into raging fires, and the hatch design was so complicated that the crew couldn't get it open fast enough to escape. What do you think NASA had to do after that disaster?

Student: Redesign the capsule and the hatch, probably delay everything to figure out what went wrong.

Tutor: Right on both counts. They redesigned the hatch to open outward in seconds, replaced flammable materials, and used a less oxygen-rich mixture on the pad. The program was set back over a year, but it arguably made every later mission safer. So after Apollo 1, how did NASA rebuild confidence?

Student: Probably with a bunch of unscrewed test flights first, then eventually put people back on board?

Tutor: Exactly — uncrewed tests, then Apollo 7 as the first crewed flight in 1968, and then Apollo 8, which did something wild that December. Any guess?

Student: Was that the one that orbited the moon without landing?

Tutor: Yes — Apollo 8 became the first crewed spacecraft to leave Earth orbit, circle the moon, and return safely, and the crew even read from Genesis on a Christmas Eve broadcast. Why do you think NASA chose to send astronauts all the way to the moon before they'd even tested the lunar lander?

Student: Maybe they were worried the Soviets would get there first, so they wanted to take a big risky step to stay ahead?

Tutor: That's a really strong hypothesis, and historians generally agree — intelligence suggested the Soviets might be planning a similar mission, so NASA moved up the schedule. That risk paid off and built momentum toward Apollo 11. Do you know the names of the three astronauts on that mission?

Student: Neil Armstrong, Buzz Aldrin, and... Michael Collins?

Tutor: Nailed it. Armstrong and Aldrin flew the lunar module down to the surface while Collins stayed in orbit in the command module. Why couldn't all three just land together?

Student: I think the lunar module was really small and light, built just for two people to land and take off again — the main ship was too heavy to land and launch off the moon.

Tutor: Exactly, that's the genius of the mission design called lunar orbit rendezvous — a lightweight lander for the surface, a separate ship that stays in orbit and never touches the moon. On July 20, 1969, Armstrong stepped onto the surface. What did he famously say?

Student: "That's one small step for man, one giant leap for mankind."

Tutor: Word for word. What do you think made that moment matter so much beyond just being a cool achievement?

Student: It kind of proved the US could do the thing Kennedy promised, and it was like the finish line of that whole competition that started with Sputnik.

Tutor: That's a great synthesis — from a beeping ball in 1957 that terrified the nation, to a footprint on the moon in 1969, in under twelve years. If you had to name the two or three biggest turning points in that whole story, what would you pick?

Student: Sputnik because it started the panic, Gagarin because it made Kennedy commit to the moon goal, and then Apollo 1 because it almost stopped everything but ended up making the program safer.

Tutor: That's exactly the throughline historians point to — fear driving urgency, urgency driving bold commitment, and tragedy forcing the caution that ultimately made success possible. Nicely reasoned."""


def test_dinosaur_safely_abstains():
    """SAFE ABSTENTION: intended taught=3.W (narrative/expository/opinion/
    reading-response writing, revising vs. editing as distinct steps -- all
    grade-3-band phrasing). No signposting. Measured: top three candidates
    (2.W, 3.W, 4.W) score within one point of each other, so the checker
    correctly declines rather than guessing among close grade-2/3/4
    neighbors."""
    result = recover_from_lesson_text(DINOSAUR, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None


def test_basketball_correctly_recovers():
    """CORRECT RECOVERY: intended taught=4.W (narrative/expository/
    persuasive/reading-response writing with linking words connecting
    ideas -- grade-4-band phrasing). No signposting. Measured: matches
    exactly."""
    result = recover_from_lesson_text(BASKETBALL, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:4.W"


def test_music_callback_correctly_recovers_with_signposted_prerequisite():
    """CORRECT RECOVERY: intended taught=5.W (narrative writing developed
    with description and dialogue, multi-source expository writing grouped
    logically, persuasive writing about media messages, reading response
    using text evidence -- 5.W-specific phrasing), with an opening
    signposted callback to grade-4 narrative/persuasive/revising content.
    Probes whether the signposted-prerequisite mechanism still works
    correctly one grade band below the historically fragile 6/7 boundary.
    Measured: taught node and signposted prerequisite both match exactly."""
    result = recover_from_lesson_text(MUSIC_CALLBACK, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:5.W"
    assert result.assumed_prerequisite_ids == ("va-writing-sol:4.W",)


def test_baking_callback_correctly_recovers_at_the_fragile_6_7_boundary():
    """CORRECT RECOVERY: intended taught=6.W (narrative writing using
    narrative techniques like characterization and tension, expository
    writing using a chosen text structure such as comparison or
    cause-and-effect, persuasive writing about media messages with grouped
    evidence, reflective writing using text evidence -- 6.W-specific
    phrasing), with an opening signposted callback to grade-5
    narrative/expository/persuasive content. This is a deliberate,
    freshly-authored re-probe of the exact 6/7 confusability zone that
    produced teach-cpg's own GRADE6_SIGNPOSTED bug (round 2) and
    teach-i35's GRADE6_UNSIGNPOSTED_GARDENING bug (round 3), using an
    entirely new topic (baking shows) and phrasing. Measured, with
    teach-i35's broadened rival search and teach-t7j's literal-overlap
    coverage fix both present: taught node and signposted prerequisite both
    match exactly, correctly landing on 6.W rather than the historically
    attractive wrong neighbor 7.W."""
    result = recover_from_lesson_text(BAKING_CALLBACK, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:6.W"
    assert result.assumed_prerequisite_ids == ("va-writing-sol:5.W",)


def test_videogame_correctly_recovers():
    """CORRECT RECOVERY: intended taught=7.W (narrative writing using
    narrative techniques including flashback and precise word choice,
    expository writing using a chosen structure and multiple credible
    sources, persuasive writing with logically grouped claims and evidence,
    reflective writing using text evidence -- 7.W-specific phrasing). No
    signposting. Measured: matches exactly."""
    result = recover_from_lesson_text(VIDEOGAME, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:7.W"


def test_offdomain_space_race_history_safely_abstains():
    """SAFE ABSTENTION: pure U.S./Soviet space race history content
    (Sputnik through Apollo 11), no writing-domain vocabulary at all.
    Measured: candidate scores are far lower than any on-domain text in
    this round and tie across eight of the graph's twelve grade nodes --
    correctly read as no real signal rather than a false-positive
    writing-domain match."""
    result = recover_from_lesson_text(SPACE_RACE_HISTORY, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
