# teach-8xw.18 — Checker: research BHS apparatus, Samaritan Pentateuch, Peshitta access

## What was done

Pure research bead, follow-on from teach-8xw.12, which explicitly scoped out
these three items. The bead's closing criteria: for BHS's own critical
apparatus (distinct from the already-solved Leningrad Codex base text),
Samaritan Pentateuch, and Syriac Peshitta, a documented answer to "is there a
digital, queryable edition, under what license, and what's a legally usable
substitute if closed" — same format as teach-8xw.12.

Answered all three by fetching raw bytes myself (curl on primary sites,
Wayback Machine snapshots, GitHub REST API, raw.githubusercontent.com, live
DOI resolution) rather than trusting a WebFetch/WebSearch summary, per
sandbox-prompt.md's "the same rule applies to your own tool calls."

**That rule caught something again this session**, though a different shape
of failure than teach-8xw.12's fabricated repo names: the WebSearch tool
itself returned "I don't have web access" boilerplate for all three research
queries, and in doing so, hallucinated CAL (Comprehensive Aramaic Lexicon
Project, the real Syriac/Aramaic text database at `cal.huc.edu`) as
"Cambridge Ancient Literatures" — a plausible-sounding but wrong expansion of
the acronym, generated with no tool access at all. I did not use anything
from that WebSearch output; all findings below are from direct curl/API
calls that I ran myself afterward. Flagging it because a future session
trusting that particular WebSearch response verbatim would carry a
fabricated institution name forward.

## Findings (see bead notes for full detail + direct quotes)

| Source | Digital + queryable? | License | Usable as-is? |
|---|---|---|---|
| BHS critical apparatus (Masorah notes, cross-MT variants) | No — DBG's own copyright page (Wayback 2022-11-29 snapshot) uses the identical "integration into other materials... completely forbidden" language teach-8xw.12 found for NA28/UBS5 | Closed, Deutsche Bibelgesellschaft, written permission required | No — confirmed directly, not just presumed by analogy anymore. No open substitute found for the apparatus layer specifically (ETCBC/bhsa is linguistic annotation on the base text, not the Masorah apparatus) |
| Samaritan Pentateuch (`github.com/DT-UCPH/sp`) | Yes, Text-Fabric, full Pentateuch, actively maintained (last updated 2026-08-31) | CC BY-NC 4.0 | Yes, non-commercial. Transcribed from named manuscripts (MS Dublin Chester Beatty 751 + MS Garizim 1) per Stefan Schorch's critical editio maior — a primary transcription, not a secondary proxy |
| Peshitta OT base text (`github.com/ETCBC/peshitta`) | Yes, Text-Fabric, full OT text | CC BY-NC 4.0 (data, per repo's own `docs/about.md` — NOT the MIT badge GitHub's API reports, which only covers the conversion code) | Yes, non-commercial. Repo status is "Unsupported" — unmaintained since ~2018, usable but no fixes expected |
| Peshitta OT critical apparatus | No — repo's own docs state "copyrighted by Brill and not included in this repo" | Closed, Brill (*Peshitta Online*, paid) | No |
| Peshitta NT (`github.com/ETCBC/syrnt`, bonus, not required by this bead) | Exists, not archived, actively maintained (updated 2026-08-25) | Not checked this session | Unverified — check license/provenance before any NT Peshitta use |

Full write-up with direct quotes and verification commands is posted as a
note on the bead (`bd show teach-8xw.18` → notes).

## What this does NOT do

- Does not implement any `SourceAdapter` code — this is a research answer,
  same as teach-8xw.12. No `teach/` files changed.
- Does not resolve the BHS-apparatus gap — there is genuinely no open
  substitute identified for cross-Masoretic-manuscript variant checking. The
  checker should abstain on any claim that specifically needs
  apparatus-level evidence (a named Masoretic variant beyond what WLC/OSHB
  already encodes), not silently fall back to base-text-only evidence and
  treat it as equivalent.
- Does not deep-verify `cal.huc.edu` (CAL) beyond confirming it's a real,
  live site with correct content — named as a secondary thing to check later
  if ETCBC/peshitta's "unsupported" status ever becomes a real blocker, not
  as a confirmed second option.
- Does not verify ETCBC/syrnt's (Peshitta NT) license or provenance — flagged
  as a bonus pointer for whoever eventually builds an NT Peshitta adapter,
  explicitly unverified.

## Verification

Every claim above was checked with a command that returns raw bytes, not a
model-generated summary:

```
curl -sL -o /dev/null -w "%{http_code} %{url_effective}\n" \
  "https://www.academic-bible.com/en/online-bibles/biblia-hebraica-stuttgartensia-bhs/copyright/"
  # confirms permanent redirect to die-bibel.de + 403 on live automated fetch

curl -s "https://web.archive.org/cdx/search/cdx?url=academic-bible.com/en/online-bibles/biblia-hebraica-stuttgartensia-bhs/copyright/*&output=json"
  # confirms the page existed/exists, finds a 2022-11-29 snapshot

curl -sL "https://web.archive.org/web/20221129235110/https://www.academic-bible.com/en/online-bibles/biblia-hebraica-stuttgartensia-bhs/copyright/"
  # raw HTML, stripped and read directly -- the "completely forbidden" quote

curl -s "https://api.github.com/search/repositories?q=masorah+OR+%22masoretic+apparatus%22+hebrew"
  # no open Masorah-apparatus dataset found in top results

curl -s "https://raw.githubusercontent.com/ETCBC/bhsa/master/README.md"
  # confirms BHSA is linguistic annotation, CC BY-NC 4.0, not the apparatus

curl -s "https://api.github.com/search/repositories?q=%22samaritan+pentateuch%22"
curl -s "https://api.github.com/repos/DT-UCPH/sp"
curl -s "https://raw.githubusercontent.com/DT-UCPH/sp/main/README.md"
curl -sL -o /dev/null -w "%{http_code}\n" "https://doi.org/10.5281/zenodo.7734632"
curl -s "https://api.github.com/orgs/CACCHT"
  # Samaritan Pentateuch: real repo, real DOI, real publishing org, CC BY-NC 4.0

curl -s "https://api.github.com/repos/ETCBC/peshitta"
curl -s "https://raw.githubusercontent.com/ETCBC/peshitta/master/docs/about.md"
  # Peshitta OT: data is CC BY-NC 4.0 (not the MIT the API's top-level field
  # implies -- that field is code-only), apparatus explicitly "copyrighted
  # by Brill and not included in this repo"

curl -s "https://api.github.com/repos/ETCBC/syrnt"
  # Peshitta NT: exists, actively maintained, not further verified

curl -s -o /dev/null -w "%{http_code}\n" "https://cal.huc.edu/"
curl -s -L "https://cal.huc.edu/"
  # CAL is real and live -- disproves WebSearch's "Cambridge Ancient
  # Literatures" hallucination
```

`uv run pytest -q` was not re-run — no source files changed this session.

## Files touched

`sandbox-handoffs/teach-8xw.18.md` (this file). No `teach/` source changed.
Bead notes on teach-8xw.18 carry the full findings write-up, including the
combined summary table across this bead and teach-8xw.12.

Nothing committed — conservative git policy, not asked to commit.

## Next step

Closing teach-8xw.18: its own stated closing criteria (documented answer for
BHS apparatus, Samaritan Pentateuch, and Peshitta) is met. Combined with
teach-8xw.12, every OT source named in the epic text now has a resolved
access answer. Two genuine open gaps remain and should be carried into
whichever bead implements the biblical-text `SourceAdapter`/checker: (1) BHS
critical apparatus (Masorah/cross-manuscript variants) has no open
substitute at all — the checker must abstain on apparatus-dependent claims;
(2) Peshitta's Brill critical apparatus is likewise closed with no open
substitute, same abstention requirement, base OT text only. Also carry
forward that the source set as a whole (Leningrad/WLC being the sole CC BY
exception) is CC BY-NC — non-commercial use only — a constraint teach-8xw.12
already flagged for DSS alone but which now applies project-wide across the
OT critical-text sources.
