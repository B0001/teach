"""teach-i35: FIFTH held-out generalization round for concept_recovery.py
against the VA Writing SOL K-12 graph, run by a session that did NOT write
teach-i35's fix (the broadened rival search in the single-winner branch of
`_resolve_candidates`, teach/concept_recovery.py).

teach-i35 found that teach-cpg's fix (round 3, this repo) only ever compared
the winner's coverage against `candidates[1]` -- the single next-highest
RAW-SCORING candidate -- not against whichever close candidate actually has
the best coverage. When 2+ non-rival candidates outscore the true rival on
raw overlap (observed here via WordNet semantic-tier synonym-expansion
inflation), the true rival is pushed out of the `candidates[1]` slot and
teach-cpg's gate silently checks the wrong node. teach-i35's fix replaces
the single `candidates[1]` lookup with a search over every candidate that
clears `_MIN_MATCH_WORDS`, picking whichever has the best coverage fraction
regardless of raw-score rank.

Per sandbox-prompt.md's "you cannot hold out examples from yourself",
round 3's own fixture (GRADE6_UNSIGNPOSTED_GARDENING, in
test_concept_recovery_writing_domain_generalization_round3.py) is now
tuning data for teach-i35's fix -- it is exactly the case that motivated the
fix, so it cannot be used to validate that the fix generalizes. teach-i35's
own acceptance criteria require a FRESH, independently-authored held-out
round, from a session that had not read teach-i35, its fix, or round 3,
before the bead can be closed. This file is that round.

WHERE THIS TEXT CAME FROM

Six lesson dialogues below were each produced by a separate `Agent` tool
call (same method as round 1/round 2/round 3's precedent). Each agent call
was given an explicit no-tool-use, no-repository-access instruction and was
told nothing about concept_recovery.py's existence, scoring mechanism,
thresholds, teach-i35, or any prior round's fixtures -- only plain-English
curriculum content (drawn by this bead's session directly from the raw VA
Writing SOL leaf-standard text in teach/data/va_writing_sol_k12.json, never
from concept_recovery.py or any test file) and an instruction to render it
as a natural tutor/student dialogue. None of the six agents saw another's
output, this module's code, or any prior round's fixtures.

Grades were chosen to include: one straightforward case (grade 7, no
signposting), one signposted-callback case whose new content is grade 9 but
whose "already know this" callback deliberately echoes grades 6-8's shared
boilerplate (to probe the same near-neighbor-grade confusability
teach-i35's fix targets, without reusing round 3's exact text), two
standalone cases likely to land in the crowded, nearly-identical grade
9/10/12 vocabulary band (a genuinely hard region for this graph,
independent of teach-i35), and one fully off-domain control (U.S. history,
no writing-domain vocabulary at all).

HONEST RESULT (measured once against the real, unmodified
`teach.va_writing_sol_graph`, via the public `recover_from_lesson_text`
entry point only -- no internals of concept_recovery.py were read to choose
or adjust these lesson texts, and no threshold in concept_recovery.py was
changed in response to seeing these results):

  correct recoveries:      2 / 6  (SKATEBOARDING -> 7.W, COLLEGE_ESSAY -> 12.W)
  safe abstentions:        4 / 6  (PODCAST, DRONE_RACING, RESTAURANT_REVIEW,
                                    GOLD_RUSH_HISTORY)
  CONFIDENT WRONG ANSWERS: 0 / 6

THIS ROUND DOES NOT PROVE teach-i35's FIX GENERALIZES. It shows no
regression (0/6 confident wrong, same as it would need to be), but by
construction it also does not exercise the specific failure geometry
teach-i35 targets (2+ non-rival candidates displacing the true rival out of
the `candidates[1]` slot) -- none of these six texts happened to produce
that geometry. A held-out round that doesn't reproduce the failure mode
cannot demonstrate the fix corrects it; it can only fail to demonstrate a
new regression, which is what happened.

Cross-checked directly (not via this round, but worth recording here since
it bears on the same closing question): running this exact round's six
texts through a reconstructed pre-fix copy of `_resolve_candidates`
(candidates[1] hardcoded, as it was before teach-i35's change) produces
BYTE-IDENTICAL results to the fixed code on all six texts. This round is
silent on whether the fix helps, in either direction.

A SEPARATE, MORE DIRECT CHECK (not this round -- reusing round 3's fixture
under the fix, which teach-i35's own rule forbids treating as validation,
but which is still worth recording honestly as a diagnostic): re-running
round 3's GRADE6_UNSIGNPOSTED_GARDENING case through the FIXED code shows
the mechanism bug teach-i35 describes is genuinely gone -- the broadened
rival search now correctly identifies va-writing-sol:6.W (50% coverage) as
the best-covered rival, instead of the old code's wrong pick of
va-writing-sol:8.W (42.86% coverage). But the gate still does not fire and
GRADE6_UNSIGNPOSTED_GARDENING is STILL a confident wrong answer post-fix
(taught=7.W, unchanged), because 7.W's OWN coverage (54%) is higher than
6.W's (50%) -- WordNet semantic-tier synonym expansion inflates the FALSE
winner's own coverage, not just irrelevant rivals' scores. Fixing which
rival gets checked does not help when the winner being checked against is
itself the one that's been inflated. This is a distinct, deeper limitation
of the coverage-fraction heuristic than the candidates[1]-hardcoding bug
teach-i35 describes, filed separately (see teach-i35's closing notes for
the new bead id) rather than tuned here, per this lineage's standing rule
against tuning a fix in response to the same case that measured it.

WHAT THIS MEANS FOR teach-i35's OWN CLOSURE

teach-i35's fix is a real, verified improvement to the rival-selection
*mechanism* (unit-tested directly in
test_concept_recovery.py::test_resolve_candidates_checks_every_candidates_coverage_not_just_the_runner_up,
and confirmed above to now select the geometrically-correct rival on round
3's own case) with no measured regression on this fresh round or the full
suite. But it does not resolve the symptom that motivated the bead
(GRADE6_UNSIGNPOSTED_GARDENING remains a confident wrong answer), and this
fresh round did not happen to supply an independent case where the fix
demonstrably flips a wrong answer to a right one or a safe abstention.
Per teach-i35's own validation requirement, that is not evidence the fix
"generalizes" in the sense the bead cared about -- it is evidence the
mechanism is correct and non-regressing, which is a narrower claim.
"""

from teach.concept_recovery import recover_from_lesson_text
from teach.va_writing_sol_graph import load_va_writing_sol_graph

WRITING_GRAPH = load_va_writing_sol_graph()

SKATEBOARDING = """Tutor: Hey! So today we're going to work on writing, several different kinds actually, and since you're the skateboarding expert here, we're using your world for basically every example.

Student: Okay, that already sounds better than the fake stories in my textbook.

Tutor: Let's start with narrative writing. That's telling a story, real or made up. Say you're writing about the first time you landed a kickflip. What's the very first thing that happened?

Student: I guess I kept bailing for like two weeks straight.

Tutor: Good, that's your beginning. Now here's the key skill: precise words. Instead of "I fell," what's more specific?

Student: I slammed. Or caught the board on my shin.

Tutor: Exactly, "slammed" tells me so much more than "fell." Now, how do you move the reader from those two weeks of failing to the day it clicked?

Student: Maybe "after two weeks of slamming" or "finally, one Saturday..."

Tutor: Those are transitional words and phrases, and they're doing real work, they signal a shift in time. If you also changed location, like from your driveway to the actual skate park, you'd need a transition for that too, something like "once I finally worked up the nerve to try it at the park."

Student: Got it. Setting change, time change, both need a signal.

Tutor: Now let's switch modes. Expository writing means explaining a topic with facts, not opinions. Pick a topic.

Student: Types of skateboard trucks?

Tutor: Perfect. You'd develop that with concrete details, definitions, facts from a few credible sources, not just one YouTube comment. And you'd pick a structure. Since you're sorting trucks into types, that's classification. If you were explaining how trucks affect turning, that might be cause-effect instead.

Student: So the structure depends on what I'm actually trying to show.

Tutor: Right, comparison, problem-solution, enumeration, description, whichever one clarifies the relationships between your ideas best. Now, persuasive writing is different again. Convince me skate parks need more funding.

Student: Because the one near me has cracked concrete and it's dangerous.

Tutor: That's a claim. What evidence backs it up?

Student: Two kids got hurt there last month, and I could look up injury reports or city maintenance records.

Tutor: That's relevant evidence, and from credible sources. Now group your claims logically, maybe safety first, then community benefit, then cost comparison to other repairs, so your reasoning builds instead of jumping around.

Student: What about reflective writing?

Tutor: That's responding to something you've read, using details and evidence from the text to show your thinking. If you read an article about a pro skater's injury comeback, you'd reflect using specific moments from that article, not just "it was inspiring."

Student: Okay, so for all of these, do I just write it in one shot?

Tutor: No, and this matters a lot: you plan first, maybe an outline of your tricks story. Then draft. Then revise, that's where you check clarity, word choice, sentence variety, and whether your paragraphs transition smoothly into each other.

Student: And editing is separate from revising?

Tutor: Different job entirely. Revising is about ideas and flow. Editing is capitalization, spelling, punctuation, sentence structure, paragraphing, making sure it follows standard English conventions. You can even trade papers with a friend and peer-edit each other's work.

Student: So plan, draft, revise, edit, in that order.

Tutor: Exactly. Want to outline your kickflip narrative right now and walk through all four steps?

Student: Yeah, let's do it."""

PODCAST = """Tutor: You mentioned you want to start a podcast. What kind — interviews, storytelling, reviews?

Student: Maybe all three, honestly. I want to do movie reviews but also interview people, and maybe some storytelling episodes.

Tutor: That's a great range, and it's actually a nice model for what we're doing today, because writing works the same way. You don't just write one kind of thing — you write short pieces and long pieces, depending on the job. A tweet announcing your episode is short. Show notes are medium. A full episode script is long and extended. Same person, same topic, different sizes for different purposes.

Student: So like — a summary of the episode versus the actual script?

Tutor: Exactly. Let's say your first episode is a review comparing two movies. Before you write a word of the script, what's your first move?

Student: Watch both movies again and take notes?

Tutor: Right — that's planning. You're gathering the textual evidence: specific scenes, lines of dialogue, moments that support whatever point you want to make. If you're comparing two heist movies, you might notice one uses fast editing to build tension and the other uses long silences. That's a detail you could cite directly, almost like a text ratefeed for your listener.

Student: So the reflective part is where I actually say which one worked better and why.

Tutor: Yes — you compare the two texts, use details and examples from each, and build toward your own position. That's the heart of a reflective piece. Once you've planned it, what comes next?

Student: Drafting it — just getting the whole thing down.

Tutor: Right, messy first pass, all your points in some order. Then?

Student: Revising, I guess. Making it actually make sense.

Tutor: That's the step people skip, and it's the one that matters most. When you revise, you're checking for clarity — would a listener who hasn't seen either movie follow this? — and accuracy, meaning did you get the plot details right, and elaboration, meaning did you actually explain your point or just assert it. "The pacing was better" isn't enough. Better how? Compared to what moment?

Student: I do that. I'll write something and then read it back and think, wait, that doesn't even explain what I mean.

Tutor: That instinct is useful — and it gets even sharper with another set of ears. Before you record, what if you had a friend read your script, or even just your own outline?

Student: Like ask them what's confusing?

Tutor: Exactly — peer evaluation. They'd tell you what worked, what confused them, and where they'd want more detail. Then you do the same thing yourself, stepping back from your own draft like a listener would. Both are about the same goal: making the writing clearer and stronger, not just marking it wrong.

Student: And after all that?

Tutor: Editing — the last pass. This is where you fix the small stuff: word choice, sentence style, whether your tone matches the show's voice, punctuation, all the conventions. If your podcast is casual and funny, an interview intro shouldn't suddenly sound like a formal essay.

Student: So the same process works whether I'm writing a two-sentence teaser or a whole ten-minute segment.

Tutor: That's the real point. Whether it's a short description of an episode, a letter pitching a guest, a full narrative for a storytelling episode, or even show notes written as a poem if you're feeling ambitious — plan it for your audience and purpose, draft it, revise it for clarity and depth, get eyes on it, and edit it clean. Want to try planning that movie-comparison script right now?

Student: Yeah, let's do it."""

DRONE_RACING = """Tutor: Before we look at anything on paper, tell me — what's the last drone race you were part of, or watched closely?

Student: Last weekend. My buddy's quad clipped a gate on the third lap and went into a tree. Total wreck.

Tutor: Perfect, that's exactly what we're going to write about today. I want you to write about that crash two different ways. First, a quick two- or three-sentence summary — just what happened, plain facts, like you're texting someone who wasn't there. Then, separately, a longer reflection where you actually dig into why it happened and what it felt like to watch.

Student: Okay, the summary's easy. "Marcus clipped gate three on lap three and crashed into a tree. His frame cracked and he didn't finish the race."

Tutor: Good — notice how different that voice is from how you'd write the longer piece. Same event, but a summary strips it down, while a reflection lets you slow down and explain. That's the kind of range I want you building — you should be able to shrink a topic into a few tight lines or stretch it into pages, and shift your voice depending on whether you're writing a caption, a letter to a sponsor, a set of race-day notes, or even a poem about the moment the drone hit the branch.

Student: A poem about a drone crash sounds ridiculous.

Tutor: Try it sometime — ridiculous is allowed. For today, let's push toward something meatier: an argument. Pick a position about racing strategy and defend it.

Student: Okay — freestyle pilots make worse racers than people who train specifically on the track layout.

Tutor: Strong claim. Now, before you draft a single sentence, who's your audience, and what's your purpose?

Student: Probably other pilots in my league, arguing my case for why we should get practice laps before qualifying.

Tutor: Good, that shapes everything — word choice, examples, tone. So plan it first: jot the reasons, then order them by strength. Only after that do you draft. And here's where the readings come in — I want you to compare two race recaps, the one from the regional final and the one from nationals, and pull specific details from each — line speeds, crash counts, pilot quotes — as evidence for your position.

Student: So I'm using their actual numbers, not just my opinion.

Tutor: Exactly — textual evidence, not just gut feeling. Once you've got a draft, read it back and ask: is this clear, is it accurate, did I actually elaborate enough, or did I just assert things? That's revising.

Student: I always think my drafts are clear until I reread them a day later and have no idea what I meant.

Tutor: That gap is exactly why revising is its own separate step from drafting. And after you revise, you're going to trade drafts with another pilot in your group — a self- and peer check. They tell you what's working, what's confusing, and one concrete suggestion for improvement. You do the same for theirs.

Student: What if their argument is bad?

Tutor: Say so, kindly and specifically — not "this is bad" but "your third reason needs an actual number from the recap." Last pass, once the ideas are solid, is editing — fixing grammar, punctuation, tightening word choice, making sure the tone matches a league audience rather than a casual post.

Student: So four separate passes, not just writing it once and being done.

Tutor: Planning, drafting, revising, editing — each one doing different work. Draft your opening paragraph now, and let's see what you've got."""

COLLEGE_ESSAY = """Tutor: You mentioned you're staring down two writing projects at once — the college application essay and maybe a cover letter for a part-time job. Good news: they draw on the exact same muscles, even though they'll end up sounding completely different on the page.

Student: Different how? Isn't writing just writing?

Tutor: Try this: read me one sentence you'd put in the application essay, and one you'd put in a job cover letter.

Student: For the essay — "The summer I fixed my neighbor's ancient lawnmower, I understood for the first time that failure is just information." For the cover letter — "I am writing to apply for the cashier position and am available for weekend shifts."

Tutor: Hear the gap? The essay sentence has voice — rhythm, a little drama, it's built to be read for pleasure and insight. The cover letter sentence is doing a job: clear, efficient, no flourishes. Same writer, two completely different tones because the audience and purpose changed. A college admissions reader wants to discover who you are. A hiring manager wants proof you're reliable and can follow instructions.

Student: So how do I know which mode to use for something?

Tutor: You ask what the piece needs to do. A reflection, like your lawnmower essay, needs to explore meaning — it can be introspective and layered. A technical piece, like instructions for closing out a cash register at the end of a shift, needs to be precise and sequential, no ambiguity allowed. A workplace email asking your manager for Tuesday off needs to be brief, polite, and get straight to the request. Each one calls for its own vocabulary and tone even though you're the one writing all of them.

Student: Okay, so where do I actually start on the essay? I've got a topic but no idea what order things go in.

Tutor: Start before you draft a single sentence — plan. Jot down the moments you might include, decide which one actually reveals something about you, and sketch a rough order. Then draft loosely, just getting it down. The real shaping happens after: revising for content — is the depth of information there, does the reader actually learn something true about you, is every detail accurate? Then editing, which is a separate, later pass — grammar, word choice, formal conventions.

Student: Why separate revising from editing? Seems like the same thing.

Tutor: Because they fix different problems. If you fix commas before you've decided whether a paragraph even belongs, you've polished something you might delete. Revise first for clarity and substance, then edit for correctness and style once the content's settled.

Student: Could someone else read my draft and tell me what's not working?

Tutor: That's exactly what peer feedback is for. Hand your essay to a friend and ask two things: what's one strength here, and what's one specific place I could push further? Do the same for your own draft with fresh eyes a day later — self-evaluation works the same way, naming what's strong before hunting for what's weak. It's not about tearing the piece apart; it's targeted suggestions for improvement.

Student: And for the cover letter, I guess the conventions are stricter?

Tutor: Right — that's the formal-versus-informal distinction. A text to a friend can be loose and casual. A cover letter needs professional conventions: full sentences, a proper greeting, no slang. The standard you're aiming for there is the same one that'll serve you in a job or in a college classroom — writing that's clear, accurate, and polished enough to be taken seriously in either world.

Student: So the essay and the cover letter aren't really opposites — they're just two settings on the same dial.

Tutor: Exactly. Same process, same care in revising and editing, just tuned differently for who's reading and why."""

RESTAURANT_REVIEW = """Tutor: Before we dive in, let's remember what you've already got down cold—writing narratives with strong event sequences and precise details, expository pieces backed by good facts and sources, persuasive writing with solid reasoning, and moving through the whole writing process—planning, drafting, revising, editing—to build multi-paragraph pieces. That's your foundation. Today we're building on it.

Student: Okay, so what are we doing today?

Tutor: You mentioned you want to start writing restaurant reviews for the school blog. Let's actually build that skill properly. First question—when you imagine your review, who's reading it, and why?

Student: I guess... other students? People deciding where to eat after school?

Tutor: Exactly—that's your audience and purpose, and everything else follows from that. A review for hungry classmates reads differently than, say, a formal critique for a food magazine. Same meal, different piece. That's something I want you to get comfortable with this year—flexibility. Writing short and long pieces for all kinds of tasks. A review is one form, but you could take that same restaurant visit and write a two-sentence summary, a reflective piece on why the meal mattered to you, a description of just the dessert, even a poem about the fries.

Student: A poem about fries?

Tutor: Why not? Let's actually try something today that's a step up—a reflective piece where you compare two restaurants you've been to. Not just "this one's better," but using real details and evidence—the texture of the crust, how long you waited, what the server said—to support your idea.

Student: Like comparing the pizza place to that ramen spot?

Tutor: Perfect example. Start planning it—jot down what point you're actually trying to make. Are you arguing one has better value? More authentic flavor? Once you know your idea, draft it, using specific moments from each place as your textual evidence, basically.

Student: I can do that. What about revising after?

Tutor: That's the next big piece. When you revise, don't just fix commas—check for clarity, accuracy, and whether you've elaborated enough. If you say "the broth was rich," push further—rich how? What made it rich?

Student: Got it. Should I show it to someone before I turn it in?

Tutor: Yes—that's peer evaluation. Trade with a partner, and instead of just saying "good job," each of you should name a real strength and one specific suggestion for improvement. Then do that same evaluation on your own draft too.

Student: That feels a little scary, showing my writing.

Tutor: It gets easier. The goal is clarity and quality, not judgment. Last step, once the content's solid, is editing—checking your conventions, your style, making sure the tone actually fits a food blog voice, casual but sharp.

Student: So plan, draft, get feedback, revise, edit.

Tutor: Exactly. Tonight, pick your two restaurants, and write me a reflective comparison—at least one full page. Bring specific details, not just opinions.

Student: Can I include the poem about fries too?

Tutor: Absolutely. Extra credit for flexibility."""

GOLD_RUSH_HISTORY = """Tutor: So — 1849. What do you think made thousands of people suddenly drop everything and head to California?

Student: Gold, obviously. But why did it work so fast? Like, wasn't California really far away?

Tutor: Exactly, and that's the interesting part. Gold was found at Sutter's Mill in January 1848, but the news didn't really explode until President Polk confirmed it publicly at the end of that year. Then in 1849 alone, something like eighty thousand people poured in. They got called the "forty-niners."

Student: How'd they even get there? No railroad yet, right?

Tutor: Right, no transcontinental railroad until 1869. So people either sailed around the tip of South America — five to eight months — or crossed Panama by land and caught a ship on the other side, or took wagon trails overland across the whole continent. All slow, all dangerous.

Student: That seems like a huge problem for a country trying to grow.

Tutor: It was, and that's exactly why the Gold Rush mattered so much for trains later. All that gold money needed a faster way to move people and goods between the coasts. The demand created by California's sudden population boom is one of the big reasons Congress eventually backed the Pacific Railway Acts in the 1860s, funding companies like Central Pacific and Union Pacific to build that transcontinental line.

Student: So mining basically paid for the railroad?

Tutor: Partly, yes — gold wealth funded banks, shipping, and eventually rail investment. Meanwhile back in the gold fields, towns sprang up almost overnight. Places like Coloma and later Sacramento grew from tiny settlements into bustling supply centers.

Student: Did the towns last?

Tutor: Some did, many didn't. Once the easy surface gold ran out, a lot of mining camps emptied out into ghost towns. But San Francisco exploded from a village of a few hundred people to a city of tens of thousands within a couple years, since it was the main port everyone passed through.

Student: What about the people already living there before all this?

Tutor: Huge consequences. Native Californian populations suffered devastating losses from violence and disease as miners flooded their land. Mexican and Chilean miners, plus large numbers of Chinese immigrants, arrived too, but often faced discriminatory taxes and laws designed to push them out of the most profitable claims.

Student: So it reshaped who lived there completely.

Tutor: Completely — and set the stage, economically and demographically, for California statehood in 1850, and eventually for those very railroads you're curious about."""


def test_skateboarding_correctly_recovers():
    """CORRECT RECOVERY: intended taught=7.W (precise words/phrases,
    transitional words signaling time/setting shifts, multi-source
    expository facts -- all 7.W-specific phrasing, distinct from 6.W's and
    8.W's near-identical neighbors). No signposting in the text. Measured:
    matches exactly."""
    result = recover_from_lesson_text(SKATEBOARDING, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:7.W"


def test_podcast_safely_abstains():
    """SAFE ABSTENTION: intended taught=9.W (flexibility across short/long
    pieces for a range of tasks and audiences, reflective comparison of two
    texts, peer- and self-evaluation for clarity/quality -- all 9.W-specific
    phrasing). 9.W, 10.W, and 12.W share heavily overlapping vocabulary in
    this graph (all three cover "flexibility"/"range of...pieces" and
    peer/self-evaluation in nearly identical language), so this is a
    genuinely hard region of the graph independent of teach-i35 -- declining
    rather than guessing among three near-identical neighbors is the
    correct call."""
    result = recover_from_lesson_text(PODCAST, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None


def test_drone_racing_safely_abstains():
    """SAFE ABSTENTION: intended taught=10.W ("write arguments that..." is
    10.W-specific vocabulary; audience/purpose planning and comparing two
    texts for evidence also appear in 9.W). 9.W and 10.W are close enough
    neighbors in this graph that abstaining is the correct, honest call
    rather than a guess."""
    result = recover_from_lesson_text(DRONE_RACING, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None


def test_college_essay_correctly_recovers():
    """CORRECT RECOVERY: intended taught=12.W (technical pieces, blending
    multiple modes/vocabulary/voice/tone, and the workplace-and-postsecondary
    standard are all 12.W-specific phrasing found nowhere else in the
    graph). No signposting. Measured: matches exactly."""
    result = recover_from_lesson_text(COLLEGE_ESSAY, WRITING_GRAPH)
    assert result.taught_node_id == "va-writing-sol:12.W"


def test_restaurant_review_safely_abstains():
    """SAFE ABSTENTION: intended taught=9.W (flexibility across short/long
    pieces including a poem, reflective comparison of two things with
    evidence, peer/self-evaluation for clarity), with an opening signposted
    callback to 6.W/7.W/8.W's shared narrative/expository/persuasive/process
    boilerplate. This deliberately echoes round 3's
    GRADE6_UNSIGNPOSTED_GARDENING setup (a lower-grade callback plus new
    9-12-band content) without reusing its text. 9.W/10.W's near-identical
    vocabulary makes this graph's hardest region to call precisely;
    declining is correct here too."""
    result = recover_from_lesson_text(RESTAURANT_REVIEW, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None


def test_offdomain_gold_rush_history_safely_abstains():
    """SAFE ABSTENTION: pure U.S. history content (the 1849 California Gold
    Rush), no writing-domain vocabulary at all. Correctly ambiguous/no-signal
    rather than a false-positive writing-domain match."""
    result = recover_from_lesson_text(GOLD_RUSH_HISTORY, WRITING_GRAPH)
    assert result.taught_node_id is None
    assert result.abstain_reason is not None
