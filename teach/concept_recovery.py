"""Checker: recover which concept a lesson taught and which prerequisites it
assumed, from lesson text alone (teach-8xw.10).

sandbox-prompt.md: the checker "sees only what the learner saw... From that
alone it must independently recover which concept was taught and which
prerequisites were assumed." teach-8xw.9 built the boundary that makes sure
nothing else crosses; this module is the first thing that has to actually do
something useful with only what's on the other side of it.

THIS IS AN INFERENCE, NOT A LOOKUP. There is no field on `LessonArtifact`
naming the concept -- if there were, this bead wouldn't exist. What this
module has instead is a fixed *vocabulary*: the whole domain's
`ConceptGraph` (every node's label and `facts` payload), built ahead of time
from the domain's own standards, exactly like a human checker who already
knows the curriculum would recognize "this is teaching perimeter and area
formulas" without being told. Matching lesson prose against that vocabulary
is the recovery step. It is NOT told which node the planner actually
traversed to -- that traversal is exactly the thing teach-8xw.9's boundary
keeps off the wire.

Domain-agnostic by construction, following the split teach-8xw.4 decided:
`ConceptNode.facts` is opaque to `concept_graph.py`, and it stays opaque
here too. `_node_vocabulary` below never reads a named key like
"leaf_standards" -- it recursively harvests every string reachable inside
`facts` (whatever shape a domain gave it) plus `label`, so a reading-domain
or foreign-language graph plugs in without this module changing.

GENERICITY: MEASURED, NOT JUST DESIGNED-FOR (teach-8xw.29)

The paragraph above is a design intent, not by itself evidence: until
teach-8xw.29, every graph this module had actually been exercised against
was math (VA Math SOL, Dummit & Foote). It is now also exercised against a
real, curriculum-scale non-math graph: `teach/va_reading_sol_graph.py`, the
Virginia English SOL reading strands (RI/RL) grades K-8, sourced the same
way teach-8xw.5 sourced VA Math SOL -- real VDOE standard text, not
synthetic filler written to make this module look good (see
tests/test_concept_recovery_non_math_domain.py, and sandbox-prompt.md's "you
cannot hold out examples from yourself"). That graph has the same
boilerplate-heavy, grade-to-grade-overlapping structure VA Math SOL has (see
"WHY OVERLAP-COUNTING ALONE IS NOT ENOUGH" below), and recovery, both
prerequisite outcomes, and the abstention/ambiguity gates all measurably
work against it. What this does NOT establish: the lesson text in that test
file is still hand-written by the session that wrote this note, not a held-
out generalization set (same limit CORRECT_RECOVERY_TEXT/ABSTAIN_TEXT below
have always had for math) -- so "recovery works on VA Reading SOL K-8 given
these specific lesson texts" is measured; "recovery generalizes to
arbitrary reading, writing, or foreign-language lesson text" is not, and
this module does not claim it is.

WHY OVERLAP-COUNTING ALONE IS NOT ENOUGH

Curriculum standards are boilerplate-heavy: "The student will use
mathematical reasoning and justification to solve contextual problems..."
recurs, near-verbatim, across most of a strand's grades. A word that shows
up in most nodes' vocabulary carries no discriminating power -- matching on
it ties every grade of a strand together instead of picking out the one the
lesson is actually about. So vocabulary is built with a per-word document
frequency across the whole graph, and only words below `_MAX_DOCUMENT_FREQ`
count toward a match. This is the reason a fixture built from real,
truncated SOL descriptions can still be told apart from its neighboring
grades: "formula" and "quadrilaterals" are discriminating; "reasoning" and
"problems" are not, and are excluded before scoring ever runs.

TWO-WAY ABSTENTION, per sandbox-prompt.md's "prefer abstention to a
confident answer":

  - No node clears the minimum match bar (`_MIN_MATCH_WORDS` distinctive
    words in common) -> abstain. This is the case a lesson entirely outside
    the graph's vocabulary hits -- e.g. group-theory content checked
    against a K-8 VA Math SOL graph, which is the actual, disclosed gap
    teach-8xw.15 flags for the Dummit & Foote test case (that graph does
    not cover undergraduate abstract algebra at all; see
    teach/va_math_sol_graph.py's docstring). A checker that guessed "K.NS"
    for a lesson about cosets because *something* had the highest score
    would be worse than useless -- it would look like a working checker
    while being wrong every time it mattered.
  - The top two candidates are too close to call (`_MIN_MARGIN`) -> abstain,
    UNLESS the coverage tiebreak below resolves it.

COVERAGE TIEBREAK (teach-ed3)

Raw overlap count alone tends to reward whichever candidate happens to have
the larger vocabulary, not whichever candidate the lesson actually spent its
depth on. A lesson that walks a full prerequisite chain with real
definitional content at every step (not just its target) routinely gives an
earlier, more heavily-scaffolded node -- e.g. cosets, on the way to
Lagrange's theorem -- a large raw overlap too, purely because that node's
own vocabulary list is longer, even though the *target* node is the one the
lesson's climactic, most detailed passage is actually about. Raw-count
margin can come out at 1 for a lesson that is not actually ambiguous to a
human reader.

So when the raw-score margin does not clear `_MIN_MARGIN`, a second signal
gets a chance before abstaining: coverage, i.e. what fraction of a
candidate's OWN distinctive vocabulary shows up in the text at all
(`score / len(node's distinctive vocabulary)`). A node whose vocabulary is
*almost entirely* present (`_MIN_COVERAGE_FRACTION`) and clearly more fully
covered than every other close rival (`_MIN_COVERAGE_MARGIN`) is the one the
lesson gave its fullest treatment to -- that is a legitimate, independent
piece of textual evidence, not a threshold softened to make abstention
happen less often. It still requires BOTH near-total coverage of the
winner's own vocabulary AND a decisive gap over every rival close on raw
score; two candidates that are both partially, similarly covered (the
synthetic exact-tie fixture in tests/test_concept_recovery.py) still
abstain, because neither condition is met.

A FAITHFUL PARAPHRASE CAN STILL LOOK LIKE NOTHING MATCHED (teach-8xw.26)

Raw exact-word overlap has no stemming or synonym handling: a lesson that
paraphrases a real node's content ("rules" for "formulas", "space covered"
for "area", "four-sided shapes with square corners" for "rectangles and
squares") shares almost none of that node's literal distinctive vocabulary,
even though a human reader would recognize it instantly. Left alone, that
collapses the correct node's score down near unrelated neighbors and the
match goes ambiguous -- not because the text was actually unclear, but
because the matcher's notion of "the same word" was too narrow.

So when raw-vocabulary scoring (`score_candidates`) abstains -- either no
candidate clears `_MIN_MATCH_WORDS`, or the top candidates are too close to
call and the coverage tiebreak doesn't resolve it -- a second, strictly
narrower-scope tier gets a try before giving up: `score_candidates_semantic`
re-scores the same text against the same per-node vocabulary, but counts a
node word as matched if the text contains that word, its WordNet lemma, or
a word sharing a WordNet synset with it (`_semantic_match`). This is a
generic, off-the-shelf normalization -- the same lemma/synonym linkage
applies uniformly to any domain's vocabulary -- not a hand-curated synonym
table tuned to any one lesson's specific word choices. It is deliberately
scoped to fire ONLY as a fallback: any text the raw exact-match tier already
resolves is untouched, so this tier cannot change behavior on the common,
already-working case, only offer a second chance on the case that would
otherwise abstain. The same abstention thresholds apply to the semantic
tier as to the raw one -- a paraphrase vague enough to stay ambiguous even
with synonym credit still abstains, per this module's whole design.

WordNet coverage is real but partial: it links close everyday synonyms
("cross"/"intersect", "rule"/"formula") but not every paraphrase a persona
might produce ("area" and "space" share no synset), and it has essentially
nothing for graduate-level technical vocabulary (Dummit & Foote's "coset",
"homomorphism"). This tier narrows the gap; it does not close it, and
nothing in this module claims it does -- see the generalization measurement
recorded against teach-8xw.26 for the actually-measured hit rate.

Recovered prerequisites get the same abstention discipline at the level of
each candidate: a direct-prerequisite node in the graph is only reported as
"assumed" if the text both (a) signals that *something* is being treated as
already known (a "you already..."/"recall.../"remember.../"you learned..."
phrase) and (b) that phrase's sentence, or one of the
`_ASSUMED_KNOWN_WINDOW_SENTENCES` sentences immediately following it,
overlaps that specific node's distinctive vocabulary. The forward window
exists because an ordinary teaching announcement often splits the cue from
its elaboration across an adjacent sentence or two ("Remember polygons from
last year? Great. Now we'll combine and subdivide them..." -- teach-8xw.27)
rather than always packing both into one sentence. A generic "you've got
this" with no content-bearing overlap to any candidate within that window is
not evidence that a specific prerequisite was assumed, and is not reported
as one.
"""
from __future__ import annotations

import dataclasses
import re
from functools import lru_cache
from typing import Iterator

from teach.concept_graph import ConceptGraph, ConceptNode

_WORD = re.compile(r"[a-z]+")

# Bookkeeping identifiers (e.g. va_math_sol_graph.py's case_identifier_uuid)
# sit in ConceptNode.facts as opaque UUID4 strings, not curriculum content --
# but _flatten_strings has to stay ignorant of key names (concept_graph.py's
# opacity rule, teach-8xw.10), so there is no "skip this field" option. This
# strips UUID-*shaped* substrings out of harvested text before it is
# word-tokenized, so their hex-letter runs ("ededf", "baca", ...) never enter
# a node's vocabulary as if they were real words (teach-klm). Matches
# anywhere in a string, not just a whole-string match, in case a future
# domain embeds an id inside a longer sentence rather than as its own field.
_UUID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)

_STOPWORDS = frozenset(
    """
    the a an and or of to in on for with will student students demonstrate
    following knowledge skills that this these those is are was were be
    been being it its as by at from into up down out about than then so
    not no yes you your yours we our ours they their them he she his her
    i me my mine but if when while can may might shall should would could
    do does did done have has had having use using used also which who
    whom what where why how all each every both few more most other some
    such only own same too very just one two three four five
    """.split()
)

# A candidate concept must share at least this many distinctive words with
# the lesson text to be considered a match at all.
_MIN_MATCH_WORDS = 3
# The top candidate's score must beat the runner-up's by at least this much,
# or the match is ambiguous and this module abstains rather than guess --
# unless the coverage tiebreak below resolves it.
_MIN_MARGIN = 2
# Coverage tiebreak (teach-ed3, see module docstring): when the raw-score
# margin doesn't clear _MIN_MARGIN, the top candidate can still win if it
# covers almost all of its OWN distinctive vocabulary...
_MIN_COVERAGE_FRACTION = 0.85
# ...AND that coverage fraction beats every other close-on-raw-score rival's
# own coverage fraction by at least this much. Both conditions are required
# so two candidates that are each partially and similarly covered (a real
# ambiguous match) still abstain.
_MIN_COVERAGE_MARGIN = 0.15
# A word that appears in the vocabulary of more than this many nodes is
# curriculum boilerplate, not a discriminating signal -- excluded from
# scoring entirely. See module docstring.
_MAX_DOCUMENT_FREQ = 4
# The semantic fallback tier's margin requirement (teach-8xw.26) -- stricter
# than _MIN_MARGIN. WordNet synonym links include ordinary-English pairs
# with no domain content at all ("want"/"require", "answer"/"solution"),
# so a semantic-tier match can clear the raw tier's margin by accident: the
# blind generalization set this was calibrated against had exactly this
# happen (a probability/statistics paraphrase mentioning "the information
# we want" and "an answer" spuriously out-scored its own true topic's
# node -- see the teach-8xw.26 handoff for the full measurement). Margin 2
# let that false positive through; margin 3 rejects it while still
# resolving both this bead's own reproduction (margin 3) and every
# genuine paraphrase-driven recovery in that same measurement (margin >=
# 5). This is a calibration against one held-out set, not a proof it can
# never happen again at margin 3 -- a wider set could still surface one.
_SEMANTIC_MIN_MARGIN = 3
# A direct prerequisite is reported as UNSIGNPOSTED USE (teach-20c) when the
# lesson text as a whole shares at least this many distinctive words with
# that prerequisite's vocabulary and no "assumed known" phrase covers it.
# Same bar as _MIN_MATCH_WORDS: the claim "this text is meaningfully about
# that node's content" should take the same amount of evidence whether the
# node is the one being taught or one being silently leaned on.
_MIN_UNSIGNPOSTED_MATCH_WORDS = _MIN_MATCH_WORDS

_ASSUMED_KNOWN_PATTERNS = (
    re.compile(r"\byou (already|previously) (know|learned|learnt)\b", re.IGNORECASE),
    re.compile(r"\byou'?ve already (learned|learnt|seen|done)\b", re.IGNORECASE),
    re.compile(r"\byou can already\b", re.IGNORECASE),
    re.compile(r"\brecall\b", re.IGNORECASE),
    re.compile(r"\bremember (when|how|that)\b", re.IGNORECASE),
    # Bare "remember <topic>" ("Remember polygons from last year?") is the
    # same already-known cue as "remember when/how/that" -- just aimed at a
    # noun phrase instead of a clause. Excludes "remember to <verb>", which
    # is a forward-looking instruction ("remember to bring your homework"),
    # not a recall-of-prior-content signal.
    re.compile(r"\bremember\b(?!\s+to\b)", re.IGNORECASE),
    re.compile(r"\blast (year|grade|time) you\b", re.IGNORECASE),
    re.compile(r"\byou (already )?know how to\b", re.IGNORECASE),
)
# An already-known cue's referent is often elaborated a sentence or two
# later ("Remember X? Good. Now we'll build on it...") rather than always
# sharing its own sentence with the prerequisite's vocabulary -- teach-8xw.27.
# The window looks forward only: in ordinary teaching dialogue the cue
# announces first and the elaboration follows, never the reverse.
_ASSUMED_KNOWN_WINDOW_SENTENCES = 2


def _words(text: str) -> set[str]:
    text = _UUID.sub(" ", text)
    return {w for w in _WORD.findall(text.lower()) if len(w) >= 4 and w not in _STOPWORDS}


def _flatten_strings(value: object) -> Iterator[str]:
    """Yield every string reachable inside an arbitrary opaque value --
    dict, list, tuple, or nested combinations thereof. `ConceptNode.facts`
    is a domain's own payload shape (per concept_graph.py's docstring, this
    module must not assume a key name like "leaf_standards" exists), so
    vocabulary extraction has to work on whatever shape shows up rather than
    reading named fields."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _flatten_strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _flatten_strings(v)


def _node_vocabulary(node: ConceptNode) -> set[str]:
    text = node.label + " " + " ".join(_flatten_strings(node.facts))
    return _words(text)


@dataclasses.dataclass(frozen=True)
class VocabularyIndex:
    """Per-node distinctive vocabulary for one ConceptGraph, built once and
    reused across every lesson text checked against that graph."""

    graph: ConceptGraph
    by_node_id: dict[str, frozenset[str]]

    def node_words(self, node_id: str) -> frozenset[str]:
        return self.by_node_id.get(node_id, frozenset())


def build_vocabulary_index(graph: ConceptGraph) -> VocabularyIndex:
    """Build the distinctive (low-document-frequency) vocabulary for every
    node in `graph`. Boilerplate words shared by most nodes are dropped
    before any lesson text is ever scored -- see module docstring."""
    raw = {node.id: _node_vocabulary(node) for node in graph.nodes}

    document_freq: dict[str, int] = {}
    for words in raw.values():
        for w in words:
            document_freq[w] = document_freq.get(w, 0) + 1

    distinctive = {
        node_id: frozenset(w for w in words if document_freq[w] <= _MAX_DOCUMENT_FREQ)
        for node_id, words in raw.items()
    }
    return VocabularyIndex(graph=graph, by_node_id=distinctive)


@dataclasses.dataclass(frozen=True)
class ConceptMatch:
    """One candidate node and how many distinctive words it shares with the
    lesson text -- kept around (not just the winner) so an abstention can
    show its work: what it considered and why nothing (or too many things)
    won."""

    node_id: str
    score: int
    matched_words: frozenset[str]


def score_candidates(text: str, index: VocabularyIndex) -> tuple[ConceptMatch, ...]:
    """Every node with a nonzero overlap against `text`, most-overlap
    first. Ties broken by node id for determinism, not by any signal in the
    text -- a real tie is exactly the case `recover_taught_concept` should
    abstain on, not silently resolve.
    """
    text_words = _words(text)
    matches = []
    for node in index.graph.nodes:
        overlap = index.node_words(node.id) & text_words
        if overlap:
            matches.append(ConceptMatch(node_id=node.id, score=len(overlap), matched_words=frozenset(overlap)))
    matches.sort(key=lambda m: (-m.score, m.node_id))
    return tuple(matches)


@lru_cache(maxsize=None)
def _wordnet_lemmatizer():
    """Lazily construct (and cache) the WordNet-backed lemmatizer. Returns
    None if the WordNet corpus isn't available (no network on first use, or
    a stripped-down environment) -- callers degrade to treating a word as
    its own lemma with no synonym expansion rather than crashing, per this
    module's abstention discipline: no semantic credit is still a safe
    answer, a crash is not."""
    try:
        from nltk.corpus import wordnet
        wordnet.synsets("test")  # forces the corpus to load / fail here
    except LookupError:
        try:
            import nltk
            nltk.download("wordnet", quiet=True)
            from nltk.corpus import wordnet
            wordnet.synsets("test")
        except Exception:
            return None
    from nltk.stem import WordNetLemmatizer
    return WordNetLemmatizer()


@lru_cache(maxsize=None)
def _lemma(word: str) -> str:
    """Canonical singular/base form of `word` (e.g. "formulas" ->
    "formula", "classify"/"classifying" -> "classify"), used only inside
    the semantic fallback tier -- see module docstring's "A FAITHFUL
    PARAPHRASE..." section. Falls back to `word` unchanged if WordNet isn't
    available."""
    lemmatizer = _wordnet_lemmatizer()
    if lemmatizer is None:
        return word
    for pos in ("n", "v", "a"):
        reduced = lemmatizer.lemmatize(word, pos=pos)
        if reduced != word:
            return reduced
    return word


@lru_cache(maxsize=None)
def _synonym_lemmas(word: str) -> frozenset[str]:
    """Every single-word WordNet lemma reachable from `word`'s synsets,
    across all parts of speech, itself reduced to `_lemma` form -- a
    generic semantic neighborhood built the same way for every word in
    every domain, not a table curated for any one lesson's phrasing (see
    module docstring). Falls back to `{_lemma(word)}` if WordNet has
    nothing for this word (unknown or too technical -- e.g. "coset") or
    isn't available at all, which means the semantic tier contributes no
    extra credit for that word rather than guessing at a synonym."""
    base = _lemma(word)
    lemmatizer = _wordnet_lemmatizer()
    if lemmatizer is None:
        return frozenset({base})
    from nltk.corpus import wordnet
    out = {base}
    for synset in wordnet.synsets(word):
        for lemma_obj in synset.lemmas():
            name = lemma_obj.name().lower()
            if "_" in name or "-" in name:
                continue  # multi-word lemma phrases don't map onto single vocabulary tokens
            out.add(_lemma(name))
    return frozenset(out)


def _semantic_match(text_word: str, node_word: str) -> bool:
    """True if `text_word` and `node_word` are the same word, the same
    WordNet lemma, or lie in each other's WordNet synonym neighborhood.
    Symmetric and word-level only -- this cannot bridge multi-word
    paraphrases ("space covered" for "area") or vocabulary WordNet simply
    doesn't cover."""
    if text_word == node_word:
        return True
    text_lemma, node_lemma = _lemma(text_word), _lemma(node_word)
    if text_lemma == node_lemma:
        return True
    return node_lemma in _synonym_lemmas(text_word) or text_lemma in _synonym_lemmas(node_word)


def score_candidates_semantic(text: str, index: VocabularyIndex) -> tuple[ConceptMatch, ...]:
    """Same shape and ranking as `score_candidates`, but a node word counts
    as matched if the text contains it, its WordNet lemma, or a WordNet
    synonym of it (`_semantic_match`) -- see module docstring's "A FAITHFUL
    PARAPHRASE..." section. This is the fallback tier `recover_taught_concept`
    reaches for only after raw exact-word scoring has already abstained.
    """
    text_words = _words(text)
    matches = []
    for node in index.graph.nodes:
        node_words = index.node_words(node.id)
        overlap = frozenset(
            nw for nw in node_words if any(_semantic_match(tw, nw) for tw in text_words)
        )
        if overlap:
            matches.append(ConceptMatch(node_id=node.id, score=len(overlap), matched_words=overlap))
    matches.sort(key=lambda m: (-m.score, m.node_id))
    return tuple(matches)


@dataclasses.dataclass(frozen=True)
class RecoveryResult:
    """What this checker could establish from lesson text alone.

    `taught_node_id=None` means abstain -- either nothing in the graph's
    vocabulary matched well enough, or two or more candidates were too
    close to call. It is NOT the same thing as "the graph has no node for
    this" (this checker cannot tell those apart, and does not claim to).

    Prerequisite recovery has three distinct outcomes, not two (teach-20c).
    For a given direct prerequisite of `taught_node_id`, it is either:

      - in `assumed_prerequisite_ids`: the text both signals *something* as
        already known and that signal co-occurs with this node's vocabulary.
      - in `unsignposted_prerequisite_ids`: the text leans on enough of this
        node's distinctive vocabulary to say the lesson assumes it, but no
        "you already know"-style phrase covers it anywhere. This is the
        unannounced-assumed-knowledge case -- the one that actually costs a
        learner, because they get lost without being told why.
      - in neither: this checker found no recoverable signal that the text
        assumes this prerequisite at all. That is still not proof the lesson
        assumed nothing -- only that neither detector above fired.
    """

    taught_node_id: str | None
    candidates: tuple[ConceptMatch, ...]
    abstain_reason: str | None
    assumed_prerequisite_ids: tuple[str, ...]
    unsignposted_prerequisite_ids: tuple[str, ...]


def _coverage_fraction(match: ConceptMatch, index: VocabularyIndex) -> float:
    """What fraction of `match.node_id`'s own distinctive vocabulary shows
    up in the text at all -- see module docstring's COVERAGE TIEBREAK
    section. `match.score` is always a subset of that node's vocabulary and
    nonzero (only nonzero-overlap nodes reach `score_candidates`'s output),
    so the vocabulary is never empty here."""
    return match.score / len(index.node_words(match.node_id))


def _resolve_candidates(
    candidates: tuple[ConceptMatch, ...], index: VocabularyIndex, min_margin: int = _MIN_MARGIN
) -> tuple[str | None, str | None]:
    """Apply this module's abstention thresholds (min-match, margin, then
    the coverage tiebreak) to an already-scored candidate list. Shared by
    the raw exact-word tier and the semantic fallback tier so both tiers
    abstain under exactly the same discipline by default -- the fallback
    tier is a broader notion of "the same word", never a looser bar for
    calling a match. `min_margin` lets a caller require more daylight than
    `_MIN_MARGIN` before calling a winner (the semantic tier passes
    `_SEMANTIC_MIN_MARGIN` -- see that constant's comment). Returns
    (taught_node_id or None, abstain_reason or None)."""
    if not candidates:
        return None, "no graph node's vocabulary overlaps this text at all"
    top = candidates[0]
    if top.score < _MIN_MATCH_WORDS:
        return None, (
            f"best candidate {top.node_id!r} shares only {top.score} distinctive "
            f"word(s) with the text (need >= {_MIN_MATCH_WORDS})"
        )
    close = [c for c in candidates if top.score - c.score < min_margin]
    if len(close) == 1:
        return top.node_id, None

    # Raw-score margin alone doesn't clear the bar -- try the coverage
    # tiebreak (module docstring) before abstaining. Requires BOTH the
    # winner covering almost all of its own vocabulary AND a decisive gap
    # over every other close rival's own coverage, not just a higher count.
    top_fraction = _coverage_fraction(top, index)
    rival_fractions = [_coverage_fraction(c, index) for c in close if c is not top]
    if top_fraction >= _MIN_COVERAGE_FRACTION and all(
        top_fraction - f >= _MIN_COVERAGE_MARGIN for f in rival_fractions
    ):
        return top.node_id, None

    tied = [c.node_id for c in close]
    return None, f"ambiguous match -- candidates too close to call: {tied}"


def recover_taught_concept(text: str, index: VocabularyIndex) -> tuple[str | None, tuple[ConceptMatch, ...], str | None]:
    """Best-matching node id, the full candidate list, and an abstain
    reason (None if a node was recovered).

    Tries raw exact-word scoring first; if and only if that abstains, tries
    the semantic fallback tier (WordNet lemma/synonym matching -- module
    docstring's "A FAITHFUL PARAPHRASE..." section, teach-8xw.26) under the
    identical thresholds before giving up. A text the raw tier already
    resolves never reaches the semantic tier, so this cannot change the
    outcome for any lesson that already worked."""
    candidates = score_candidates(text, index)
    taught_node_id, abstain_reason = _resolve_candidates(candidates, index)
    if taught_node_id is not None:
        return taught_node_id, candidates, None

    semantic_candidates = score_candidates_semantic(text, index)
    semantic_taught_node_id, semantic_abstain_reason = _resolve_candidates(
        semantic_candidates, index, min_margin=_SEMANTIC_MIN_MARGIN
    )
    if semantic_taught_node_id is not None:
        return semantic_taught_node_id, semantic_candidates, None

    # Both tiers abstained -- report the raw-tier candidates and reason:
    # they're what the common case debugs against, and reporting two
    # different candidate lists/reasons for one abstention would be noise,
    # not evidence.
    return None, candidates, abstain_reason


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def recover_assumed_prerequisites(text: str, index: VocabularyIndex, taught_node_id: str) -> tuple[str, ...]:
    """Direct-prerequisite nodes of `taught_node_id` that this text signals
    as already established, per the module docstring's two-part test:
    an assumed-known phrase, plus vocabulary overlap within that phrase's
    sentence OR the `_ASSUMED_KNOWN_WINDOW_SENTENCES` sentences immediately
    following it (teach-8xw.27 -- an ordinary discourse-marker gap, e.g. a
    short acknowledgment sentence between the cue and its elaboration, must
    not make a signposted prerequisite look silent). Returns in graph-edge
    order; empty if no candidate clears the bar -- that means this text gave
    no recoverable signal, not that the lesson assumed nothing.
    """
    prereq_ids = tuple(
        edge.src for edge in index.graph.edges if edge.dst == taught_node_id
    )
    if not prereq_ids:
        return ()

    sentences = _sentences(text)
    signaled_windows = [
        _words(" ".join(sentences[i : i + 1 + _ASSUMED_KNOWN_WINDOW_SENTENCES]))
        for i, sentence in enumerate(sentences)
        if any(p.search(sentence) for p in _ASSUMED_KNOWN_PATTERNS)
    ]
    if not signaled_windows:
        return ()

    assumed = []
    for prereq_id in prereq_ids:
        prereq_words = index.node_words(prereq_id)
        for window_words in signaled_windows:
            if window_words & prereq_words:
                assumed.append(prereq_id)
                break
    return tuple(assumed)


def recover_unsignposted_prerequisites(
    text: str,
    index: VocabularyIndex,
    taught_node_id: str,
    assumed_prerequisite_ids: tuple[str, ...],
) -> tuple[str, ...]:
    """Direct-prerequisite nodes of `taught_node_id` whose distinctive
    vocabulary this text leans on WITHOUT any "you already know"-style
    signal marking it as established -- teach-20c's third outcome, distinct
    from both `assumed_prerequisite_ids` (signposted) and "no signal at all"
    (empty on both). See `RecoveryResult`'s docstring for the three-way
    split.

    A node already in `assumed_prerequisite_ids` is excluded here -- it is
    signposted, so it is not also unsignposted. Otherwise the bar is the
    same overlap discipline as concept identification itself: at least
    `_MIN_UNSIGNPOSTED_MATCH_WORDS` of that node's distinctive words have to
    appear anywhere in the text, not just near a signal phrase, because
    there is no signal phrase to anchor to -- that is exactly what makes
    this case silent.
    """
    prereq_ids = tuple(
        edge.src for edge in index.graph.edges if edge.dst == taught_node_id
    )
    text_words = _words(text)
    unsignposted = []
    for prereq_id in prereq_ids:
        if prereq_id in assumed_prerequisite_ids:
            continue
        overlap = index.node_words(prereq_id) & text_words
        if len(overlap) >= _MIN_UNSIGNPOSTED_MATCH_WORDS:
            unsignposted.append(prereq_id)
    return tuple(unsignposted)


def recover_from_lesson_text(text: str, graph: ConceptGraph) -> RecoveryResult:
    """The checker entry point: lesson text and the domain's ConceptGraph
    (the fixed vocabulary; NOT the planner's traversal for this specific
    lesson -- see module docstring) in, a RecoveryResult out.
    """
    index = build_vocabulary_index(graph)
    taught_node_id, candidates, abstain_reason = recover_taught_concept(text, index)
    assumed = (
        recover_assumed_prerequisites(text, index, taught_node_id)
        if taught_node_id is not None
        else ()
    )
    unsignposted = (
        recover_unsignposted_prerequisites(text, index, taught_node_id, assumed)
        if taught_node_id is not None
        else ()
    )
    return RecoveryResult(
        taught_node_id=taught_node_id,
        candidates=candidates,
        abstain_reason=abstain_reason,
        assumed_prerequisite_ids=assumed,
        unsignposted_prerequisite_ids=unsignposted,
    )


# --- hand-written examples for the runnable check ---------------------------
# Per this bead's acceptance criteria: a correct-recovery path and an
# abstention path, against real graph nodes (teach-8xw.5's VA Math SOL K-8
# data), built from the actual sourced standard text quoted in
# va_math_sol_graph.py's docstring/data file, not invented content.

CORRECT_RECOVERY_TEXT = (
    "tutor: Last year you already learned how to combine and subdivide "
    "polygons using grids and simple tools.\n"
    "learner: Right, we cut some polygons into equal pieces.\n"
    "tutor: Today we go one step further: instead of just combining shapes "
    "by eye, you'll develop and use actual formulas for rectangles, "
    "parallelograms, rhombi, and trapezoids -- and draw the intersecting "
    "and perpendicular lines that make up their angles."
)
CORRECT_RECOVERY_TAUGHT = "va-math-sol:4.MG"
CORRECT_RECOVERY_ASSUMED = ("va-math-sol:3.MG",)

ABSTAIN_TEXT = (
    "tutor: M needs proof this cell can survive interrogation -- show me the "
    "kernel of this homomorphism is normal, and that every coset of it "
    "partitions the group into equal pieces."
)


if __name__ == "__main__":
    from teach.va_math_sol_graph import load_va_math_sol_graph

    graph = load_va_math_sol_graph()
    index = build_vocabulary_index(graph)

    result = recover_from_lesson_text(CORRECT_RECOVERY_TEXT, graph)
    assert result.taught_node_id == CORRECT_RECOVERY_TAUGHT, (
        f"expected {CORRECT_RECOVERY_TAUGHT}, got {result.taught_node_id} "
        f"(candidates: {result.candidates})"
    )
    assert result.assumed_prerequisite_ids == CORRECT_RECOVERY_ASSUMED, (
        f"expected {CORRECT_RECOVERY_ASSUMED}, got {result.assumed_prerequisite_ids}"
    )

    abstained = recover_from_lesson_text(ABSTAIN_TEXT, graph)
    assert abstained.taught_node_id is None, (
        f"expected abstention on out-of-graph content, got {abstained.taught_node_id}"
    )
    assert abstained.abstain_reason is not None

    print(
        "OK: correct-recovery example identifies "
        f"{result.taught_node_id} with assumed prerequisite(s) "
        f"{result.assumed_prerequisite_ids}; out-of-graph (group theory) "
        f"lesson text abstains ({abstained.abstain_reason!r})"
    )
