# teach-8xw.12 — Checker: research biblical-text source access

## What was done

Pure research bead, no code — the bead's own acceptance criteria asks for a
documented answer, for each of four sources (BHS/Leningrad Codex, DSS
variants, NA27/28, UBS4/5), to "is there a digital, queryable edition
available, under what license, and what if anything is a legally usable
substitute." Answered all four by fetching raw bytes myself (curl on
primary sites, GitHub API/raw content, Wayback Machine snapshots, Wikipedia
REST API raw wikitext) rather than trusting a WebFetch/WebSearch summary —
per sandbox-prompt.md's explicit rule that "the same rule applies to your
own tool calls."

**That rule caught something real this session.** A WebSearch for DSS
datasets returned two specific, plausible-sounding GitHub project names
("Dead Sea Scrolls Project (DSSP)... University of Texas at Austin",
"Dead Sea Scrolls Transcription Initiative (DSTI)... University of Sydney")
that do not exist — confirmed by querying the GitHub search API directly
and finding nothing but unrelated placeholder repos. Same failure mode as
the `narrator`/PyPI fabrication sandbox-prompt.md documents for
teach-8xw.1: a summarizer producing a plausible-sounding answer that
mirrors the query terms. Full findings, with every claim's verification
method, are posted as a note on the bead (`bd show teach-8xw.12` →
Comments/Notes) and duplicated in the summary below.

## Findings (see bead notes for full detail + direct quotes)

| Source | Digital + queryable? | License | Usable as-is? |
|---|---|---|---|
| Leningrad Codex text (WLC/OpenScriptures, `github.com/openscriptures/morphhb`) | Yes | CC BY 4.0 (base ms. public domain) | Yes |
| BHS critical apparatus (Masorah/variants, as opposed to base text) | Not researched | Presumptively DBG-copyrighted like NA/UBS | Unknown — follow-on bead teach-8xw.18 |
| DSS images + curated transcriptions (Leon Levy Digital Library, `deadseascrolls.org.il`) | Yes (images), all rights reserved | Closed | No |
| DSS scholarly transcriptions (`github.com/ETCBC/dss`, Abegg data, Text-Fabric) | Yes | CC BY-NC 4.0 | Yes, non-commercial only |
| NA27/28 | Read-only browsing only; bulk/integration "completely forbidden" per DBG's own copyright page | Closed, written permission required | No |
| UBS4/5 | Same as NA27/28 (identical text since UBS5=NA28, same publisher, same restriction) | Closed, written permission required | No |
| SBLGNT (`sblgnt.com`) — open proxy for NA/UBS | Yes | CC BY 4.0 | Yes, but differs from NA/UBS at 540+ variation units (SBL's own stated figure) — document this divergence as a caveat on any checker verdict near one of those units, don't treat SBLGNT as identical to NA/UBS |
| Septuagint (Rahlfs 1935) — spot-checked only, not required by this bead's closing criteria | Yes | Mixed (base is an old academic archive; some GitHub mirrors add their own NC license) | Provisionally yes, needs its own dedicated check before use |

Samaritan Pentateuch and Syriac Peshitta were not researched (named in the
epic's "ancient-version variants" list but outside this bead's own closing
criteria, which only names four sources) — filed as teach-8xw.18 rather
than guessed at.

## What this does NOT do

- Does not implement a `SourceAdapter` for biblical text (that's
  teach-8xw.11's engine, `teach/fact_checker.py`, waiting for this answer —
  now it has one: build the OT adapter against WLC/OpenScriptures for base
  text and ETCBC/dss for DSS cross-checking (non-commercial-only caveat
  must be carried forward into that adapter's docstring/license notice);
  build the NT adapter against SBLGNT, with the 540-variation-unit caveat
  surfaced wherever the checker reports a verdict that could be one of
  those units — that's a precision question the adapter author will need
  to decide how to handle, not resolved here).
- Does not answer the BHS-apparatus / Samaritan Pentateuch / Peshitta
  questions — filed as teach-8xw.18.
- Does not touch any code in `teach/`. No tests added — nothing here is
  logic, it's a documented research answer. The "one runnable check"
  working-rule doesn't apply to a research bead with no code artifact.

## Verification

Every source-availability claim above was checked with a command that
returns raw bytes, not a model-generated summary:

```
curl -sL https://raw.githubusercontent.com/openscriptures/morphhb/master/LICENSE.md
curl -sL https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Gen.xml | head
curl -s https://www.deadseascrolls.org.il/terms                     # IAA all-rights-reserved, confirmed
curl -sL https://raw.githubusercontent.com/etcbc/dss/master/README.md   # CC BY-NC 4.0, confirmed
curl -s https://sblgnt.com/license/                                  # CC BY 4.0 full legal code, confirmed
curl -s https://sblgnt.com/about/                                    # "540 variation units", "freely download", confirmed
curl -sL "https://web.archive.org/web/2023/https://www.academic-bible.com/en/online-bibles/novum-testamentum-graece-na-28/copyright/"  # DBG's own "completely forbidden" language, confirmed
curl -sL "https://web.archive.org/web/2023/https://www.academic-bible.com/en/online-bibles/greek-new-testament-ubs5/copyright/"        # same, for UBS5
curl -s "https://api.github.com/search/repositories?q=dead+sea+scrolls+transcription"   # disproved the two fabricated WebSearch repo names
curl -s "https://en.wikipedia.org/w/rest.php/v1/page/Novum_Testamentum_Graece"          # raw wikitext confirms NA28 text == UBS5 text
```

`uv run pytest -q` was not re-run — no source files changed this session.

## Files touched

`sandbox-handoffs/teach-8xw.12.md` (this file). No `teach/` source changed.
Bead notes on teach-8xw.12 carry the full findings write-up. New bead
teach-8xw.18 filed for the three sources this one didn't cover.

Nothing committed — conservative git policy, not asked to commit.

## Next step

Closing teach-8xw.12: its own stated closing criteria (documented answer
for the four named sources) is met. teach-8xw.11's `SourceAdapter` seam is
now unblocked for a biblical-text adapter, with two license constraints to
carry forward (DSS: non-commercial only via ETCBC/dss; NT: SBLGNT is not
byte-identical to NA/UBS, 540+ variation units apart) and one gap
(BHS critical apparatus / Samaritan Pentateuch / Peshitta) tracked as
teach-8xw.18.
