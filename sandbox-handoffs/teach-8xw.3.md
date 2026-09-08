# teach-8xw.3 — Find or stand up a common reference site for AI-consumable knowledge graphs

## Bottom line

**A real, actively-maintained registry already exists and should be the target: 1EdTech's CASE standard, browsable/queryable today via the open-source OpenSALT reference instance (`opensalt.net`), with a federated discovery layer (CASE Network) on top of it.** CASE has a purpose-built prerequisite-style association type (`precedes`), a documented JSON REST API, real curriculum content already loaded (including actual Virginia SOL documents), and an open-source (MIT) implementation that any org — including this one — can read from or publish into. A second, more general-purpose registry, **LOD Cloud** (`lod-cloud.net`), is the better answer if "any domain" is read literally rather than through this project's actual (education/prerequisite-graph) use case; it indexes ~1,700 machine-readable knowledge graphs across all domains and has been running since 2007 with an open submission process, but is not prerequisite/DAG-specific — most of its entries are general RDF/Linked-Data graphs, not learning-sequence graphs.

Recommendation: **target CASE for this project's own publishing** (model the HuggingFace dataset schema in teach-8xw.14 on CASE's `CFItem`/`CFAssociation` shape, and use `precedes` for prerequisite edges) rather than stand up a new registry. That's a design decision for teach-8xw.14/teach-8xw.5, not executed in this bead — flagging it, not doing it.

Every claim below is grounded in a `curl` command run this session against a real API and inspected as raw JSON/HTML — no WebSearch or WebFetch was used, per the standing tooling warning from teach-8xw.1/teach-8xw.2 (those tools have fabricated results in this sandbox before).

## What exists: 1EdTech CASE (Competencies and Academic Standards Exchange)

- **Standard**: `www.1edtech.org/standards/case` (1EdTech = the renamed IMS Global Learning Consortium; `imsglobal.org` 301-redirects there — confirmed live, not defunct).
- **Spec text fetched directly**: `imsglobal.org/sites/default/files/spec/case/v1p1/information_model/caseservicev1p1_infomodelv1p0.html` (918KB HTML, fetched and parsed this session). Section 7.4.1 defines the `CFAssociationTypeEnum` vocabulary. It includes, verbatim:
  > `"precedes"` - the origin of the association comes before the destination of the association in time or order.
  Also present: `isChildOf` (hierarchy), `exactMatchOf` (crosswalk/equivalence), `isPartOf`, `isPeerOf`, `isRelatedTo`, `replacedBy`, `exemplar`, `hasSkillLevel`, `isTranslationOf`. `precedes` is exactly a prerequisite/sequence edge type, native to the standard.
- **Open-source reference implementation**: `opensalt.net`, software `github.com/opensalt/opensalt`. Confirmed via GitHub API this session: MIT license, 44 stars, `updated_at: 2026-09-03` (5 days before this session) — actively maintained, not abandoned.
- **Public REST API, no auth required for reads**, confirmed live this session:
  - `GET https://opensalt.net/ims/case/v1p0/CFDocuments` → JSON list of published frameworks. Real content present: Norm Webb's Depth-of-Knowledge levels, Next Generation Science Standards, Common Core Math (creator: CCSSO), and — directly relevant to teach-8xw.2/teach-8xw.5 — **"Mathematics Standards of Learning for Virginia Public Schools 2023"** and **"English Standards of Learning for Virginia Public Schools 2024"**, creator "Virtual Virginia," `officialSourceURL` pointing at `doe.virginia.gov`.
  - `GET .../CFPackages/{id}` for the VA Math SOL 2023 doc (`aa7ab56a-276b-11ef-8aff-0242ac140003`) returns the full graph: 1,759 `isChildOf` edges (hierarchy) and 71 `exactMatchOf` edges (crosswalk to another CASE-hosted framework), **zero `precedes` edges**. This is a second, independent confirmation of teach-8xw.2's finding (no VA SOL prerequisite graph exists anywhere) — but through a completely different channel (a live ed-tech standards API, not a general-purpose KG dataset host), and it shows the *schema* has a slot for exactly this relation even though *this content* doesn't populate it.
- **Federated network layer**: `casenetwork.imsglobal.org` returns HTTP 200 but its API responds `{"message":"Invalid credentials provided 1"}` without auth — CASE Network proper is a membership-gated federation of publisher endpoints (consistent with 1EdTech being a paid-membership standards body). The publicly-open `opensalt.net` instance is what a non-member can actually read and write against today; several of its `destinationNodeURI`s point at `casenetwork.imsglobal.org` URIs, showing OpenSALT content is meant to interoperate with the larger federated network even though this session couldn't authenticate into the network API directly.
- **Contribution model**: OpenSALT is MIT-licensed and self-hostable — any org (or this project) can stand up its own instance or, evidently, get write access to the shared public instance (Virtual Virginia, a real VDOE program, has done exactly that with real 2023/2024 standards text). This is existence proof of external contribution, not just a theoretical "should accept" claim.

## What exists: LOD Cloud (general, not prerequisite-specific)

- `lod-cloud.net` — the Linked Open Data Cloud, a long-running (since ~2007) index of published Linked Data / RDF knowledge graphs across every domain (geography, life sciences, government, media, etc.), still actively served.
- `GET https://lod-cloud.net/versions/latest/lod-data.json` → 4.2MB JSON, confirmed 1,683 dataset entries this session (each with identifier, title, keywords, links to other datasets, download URLs).
- Accepts external submissions: the site has a live `/add-dataset` page (HTTP 302, i.e. a real routed endpoint, not a dead link), and its rendering code is open on GitHub (`jmccrae/lod-cloud-draw`).
- **Not prerequisite-style.** It indexes graphs of arbitrary shape and purpose — most are general entity/RDF graphs, not directed learning-sequence DAGs. It answers the literal "any domain, general registry of AI-consumable knowledge graphs" reading of the bead, but is a weaker fit for this project's actual need (prerequisite/dependency graphs specifically) than CASE.

## Why CASE over LOD Cloud for this project

The bead asks whether this project should "adopt [a registry] as its publishing target or model its own HuggingFace dataset schema on [it]." LOD Cloud is a directory of *existing* graphs in heterogeneous RDF shapes with no shared prerequisite semantics — there's nothing to model a *prerequisite-edge schema* on there. CASE is the opposite: a single, documented, versioned schema with a real prerequisite-relation token (`precedes`), already used by real state education agencies (including VDOE, for the exact SOL content teach-8xw.2 investigated), with open tooling to read and write it. Modeling this project's own dependency-DAG schema on CASE's `CFItem`/`CFAssociation` shape — and publishing/mirroring into an OpenSALT-compatible format alongside the HuggingFace dataset from teach-8xw.14 — would make this project's graph interoperable with the existing ed-tech ecosystem instead of inventing a one-off schema nobody else can consume. That is a recommendation, not an action taken in this bead.

## What this does NOT do

- Does not build or publish anything. teach-8xw.5 (build the graph) and teach-8xw.14 (HuggingFace publish pipeline) are still fully open; this bead only surveys and recommends a target/model.
- Does not attempt to obtain 1EdTech membership credentials or push any data into CASE Network or OpenSALT — read-only investigation via the public API.
- Does not re-verify the VA SOL prerequisite-edge gap from scratch (teach-8xw.2 already did that against a different dataset); this bead's CASE finding is a second independent confirmation via a different source, not a redundant re-survey.

## Tooling note (consistent with teach-8xw.1 / teach-8xw.2)

WebSearch/WebFetch were not used. All claims above come from `curl` against live endpoints (1edtech.org, opensalt.net, casenetwork.imsglobal.org, lod-cloud.net, api.github.com) and direct inspection of the returned JSON/HTML in this session — continuing the pattern flagged twice before in this repo of summarizer tools fabricating confirmations that mirror the query.

## Verification

```
uv run pytest -q     # 46 passed — unchanged; no source file was created or modified by this bead
```

## Files touched

None in the repo tree besides this handoff and the bead's own notes/status. Nothing committed — conservative git policy, bead did not say to commit.
