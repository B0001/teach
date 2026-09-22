# teach-8xw.57 -- GFDL copyleft vs the shared CC-BY dataset repo

## What was already done before this session

A prior session had already made the licensing decision (see the bead's
notes, decided by the repo owner) and landed the mechanical half of it in
commit `1aa67c5`:

- `_hf_license_id` in `teach/publish_graph.py` maps GFDL's spellings
  (`fdl-1.3.html`, `fdl.html`, `copyleft/fdl.html`, `"gnu fdl 1.3"`, `"gfdl-1.3"`,
  `"gfdl"`) to HF's exact `"gfdl"` identifier instead of degrading to `"other"`.
- Fixed a latent bug the GFDL case exposed: the old normalization appended a
  trailing slash to any http URL, which suited canonical CC URLs but silently
  broke any license URL ending in a filename (GFDL's does). Keys are now
  stored and matched without a trailing slash.

That part was already verified (three assertions in `publish_graph.py`'s own
`_selfcheck`) and is untouched by this session.

## What this session did

The bead's remaining requirement was: *"The GFDL notice and copyright ...
must appear in the published artifact, not only the license id."* Nothing in
the repo actually defined what that notice/copyright text was for the Judson
graph, or where it would live, so there was nothing yet to appear anywhere.

Added `JUDSON_SOURCE` to `teach/judson_algebra_graph.py` -- a `source` dict
in the same shape `va_math_sol_graph.py`'s data already uses
(`provider`/`author`/`license`/`attribution`/`retrieved_via`), which is the
dict `publish_graph.build_dataset_files`/`publish` serialize verbatim into
both `manifest.json` and the README "## Source" block. Its fields:

- `license`: `https://www.gnu.org/licenses/fdl-1.3.html` -- confirmed live
  (`curl -o /dev/null -w '%{http_code}'` -> 200, title tag confirms "GNU Free
  Documentation License v1.3") and confirmed it resolves through
  `_hf_license_id` to `"gfdl"`, not `"other"`.
- `attribution`: the verbatim text of `COPYING` at `github.com/twjudson/aata`,
  fetched directly with `curl` (raw bytes, not recalled -- this repo's
  standing rule after the `narrator`/PyPI incident in `teach-8xw.1`), which
  reads:

  > Copyright (C) 1997-2015 Thomas W. Judson, Robert A. Beezer.
  > Permission is granted to copy, distribute and/or modify this document
  > under the terms of the GNU Free Documentation License, Version 1.3
  > or any later version published by the Free Software Foundation;
  > with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
  > A copy of the license is included in the section entitled "GNU
  > Free Documentation License".

  (Note: the module's own docstring, written by the prior session, paraphrases
  this as "no Invariant Sections, no Cover Texts" -- accurate in substance but
  not the verbatim wording. Left as-is; not this bead's scope to edit that
  docstring, and `JUDSON_SOURCE["attribution"]` now carries the exact text
  regardless.)

Added assertions (both as a `tests/test_judson_algebra_graph.py` test trio
and mirrored into `judson_algebra_graph.py`'s own `_self_check`, per this
repo's "every module self-checks standalone" rule):

1. `_hf_license_id(JUDSON_SOURCE["license"]) == "gfdl"`.
2. The copyright line and "GNU Free Documentation License" are present in
   `JUDSON_SOURCE["attribution"]` itself.
3. They still appear, verbatim, after a full round-trip through
   `build_dataset_files` -- i.e. in the actual `README.md` and
   `manifest.json` bytes a consumer would receive, not just in the source
   dict before it's serialized. This is the actual acceptance criterion: a
   license id alone does not satisfy GFDL, the notice text has to travel with
   the artifact, and now there's a test that fails if a future refactor to
   `_dataset_card`/`build_dataset_files` ever stops forwarding `source`
   verbatim.

## What this session deliberately did NOT do

- Did **not** build the multi-graph HF repo layout (per-graph path prefix,
  root index, CLI graph selector). That is teach-8xw.55's scope, still open,
  and the bead's own notes are explicit that .57 must not get ahead of it.
- Did **not** publish the Judson graph, live or dry-run-against-the-real-repo.
  `publish_graph.py`'s CLI still only knows `load_va_math_sol_graph`
  (unchanged, also .55's job).
- Did **not** touch `_hf_license_id` or the GFDL entries in `_HF_LICENSE_IDS`
  -- already correct from the prior session, verified rather than re-done.

So `JUDSON_SOURCE` currently has no caller in production code -- it exists so
that when teach-8xw.55's per-graph layout lands and wires the Judson graph
in, the licensing/attribution decision is already made and tested, and
whoever builds .55 does not have to make a fresh licensing call or invent the
notice text under time pressure.

## Evidence

- `uv run pytest -q` -- 434 passed (was 431 before this session's 3 new
  tests; unrelated to the 422 the prior session reported, which predates
  several since-added test files already in the working tree, e.g.
  `test_judson_bond_integration.py`).
- `uv run python3 -m teach.judson_algebra_graph` -- self-check OK, now
  including the three GFDL assertions.
- `uv run python3 -m teach.publish_graph` -- self-check OK, unchanged.

## Files touched

- `teach/judson_algebra_graph.py` -- added `JUDSON_SOURCE`, added three
  assertions to `_self_check`.
- `tests/test_judson_algebra_graph.py` -- added three new tests, imported
  `JUDSON_SOURCE` and `publish_graph._hf_license_id`/`build_dataset_files`.

Both files were already untracked (new from the prior session's teach-8xw.56
work replacing Dummit & Foote) -- this session amended them in place rather
than creating new ones.

## Next steps (not this bead)

- teach-8xw.55: build the per-graph HF repo layout, and when it wires in the
  Judson graph, pass `JUDSON_SOURCE` as its `source=` -- do not invent a new
  source block for it.
- Whoever eventually builds the root dataset-card index (also .55) must not
  put a single blanket license in its front matter -- state per-directory
  licenses in the body, per this bead's decision.
