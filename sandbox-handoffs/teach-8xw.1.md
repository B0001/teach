# teach-8xw.1 — Locate the 'narrator' story-generation package

## What was done

This bead was already fully investigated by a previous session, which
concluded no `narrator` package exists in this sandbox and asked for one of
two things to close it: a confirmed location for the real project, or an
explicit human decision that it should be built standalone. That session did
not have `bd human` flag it before running out of scope — the bead sat open
with the investigation written into its description but no actual request
routed to a human.

This session did not find the package either. Rather than repeat the same
three checks and reach the same conclusion, I extended the search across
every additional surface reachable from this sandbox, to find out whether
the original negative was a search-tool limitation rather than a real
absence:

- GitHub repo search `narrator+in:name`, sorted by stars — top 30 inspected
  by hand (`cbh123/narrator`, `ztellman/narrator`, `astrochili/narrator`,
  `DavidNTompkins/narrator`, etc.). None match "motive graph / personality
  as data structure" story engine.
- GitHub repo search for the exact phrase `"motive graph"` — `total_count: 0`.
- GitHub code search (`/search/code`) — `401 Requires authentication`. No
  GitHub token is available in this sandbox, so code-level search (as
  opposed to repo name/description search) could not be run at all. This is
  a real gap, not a confirmed absence — noted on the bead for whoever next
  has a token.
- `grep.app` and `sourcegraph.com` — both blocked (Vercel bot checkpoint /
  403) from this sandbox.
- DuckDuckGo HTML search — non-functional here even on a sanity-check query
  with obviously-indexed results (`python requests library` parsed to zero
  result links), so its zero-result answer for our actual query carries no
  evidential weight.
- PyPI — checked 6 plausible alternate package names (`motive-graph`,
  `storynarrator`, `narrative-engine`, `story-narrator`, `narrator-engine`,
  `python-narrator`). All 404.
- Confirmed the existing PyPI `narrator` package is unrelated, but not the
  way the previous session left it (see below).

**Notable finding, worth flagging on its own**: `WebFetch` on the PyPI
`narrator` package's JSON endpoint returned a summary claiming the package
"offers tools for story generation... features a motive graph to understand
character personality and motivations... keywords include story generation,
narrative, motive graphs, and personality as data structure," authored by
"brianmckenna13." That is fabricated. I fetched the raw JSON with `curl` and
read it directly: the real author is Chris A. Lindgren
(`chris.a.lindgren@gmail.com`), the real summary is "A set of functions that
process and create descriptive summary visualizations to help develop a
broader narrative through-line of tweet data," and the real keywords are
`data processing, descriptive statistics, data narratives, temporal charts`
— nothing about motive graphs or personality anywhere in it. WebFetch
hallucinated a match that exactly mirrored the search terms I gave it. This
is a live trap for future sessions: on a verification-critical lookup like
"does this package match the spec," fetch the raw source and read it
yourself — don't trust a summarizer's answer, especially one that
suspiciously confirms exactly what you were hoping to find. (This directly
validates sandbox-prompt.md's "the checker must not agree with the
producer" spirit, just applied to a tool call instead of a lesson.)

## What this does NOT do

- It does not resolve the underlying question. No `narrator` project
  matching the epic's description was found, on any surface this sandbox
  can reach.
- It does not decide to build the persona layer standalone. That is
  explicitly a human decision per the bead's own "what would close this,"
  and I am not the human.
- It does not close teach-8xw.6 (Producer: persona/narrative rendering),
  which stays blocked on this bead.

## Current state / why still open

I ran `bd update teach-8xw.1 --add-label human` with a full note of the
investigation and the specific question for a human: either narrator is
unavailable and the persona layer should be built standalone (with a named
subset of "motive graph as data structure" to satisfy), or a human has a
specific repo/location these tools can't reach (private repo, unpublished,
a name not yet tried). `bd human list` now shows teach-8xw.1 as the one
human-needed bead in the project.

Per this session's instructions, a bead only closes when its acceptance
evidence exists or the human decision has been made. Neither is true yet —
closing now would just make the queue look shorter without actually
resolving the blocker. Leaving it `in_progress`, human-flagged, open.

## Verification

```
uv run pytest -q     # 16 passed — unchanged, no code was touched by this bead
bd human list         # teach-8xw.1 now listed
```

## Files touched

None. This bead is pure investigation; no source files were created or
modified. The only state change is on the bead itself (`--claim`,
`--add-label human`, `--notes`).

Nothing committed — conservative git policy, bead did not say to commit, and
there is nothing to commit anyway.
