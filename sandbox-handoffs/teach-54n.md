# teach-54n handoff

## What this bead reported

Filed by a session running the full suite as a regression check for
teach-g7r.2. It found `uv run pytest` at `480 passed, 1 failed`, with the
failure in
`tests/test_concept_recovery_writing_domain_generalization_round3.py::test_grade6_unsignposted_gardening_is_a_confident_wrong_answer`
(`assert None == 'va-writing-sol:7.W'`). It attributed this to 126
insertions / 36 deletions of uncommitted work already sitting in
`teach/concept_recovery.py` at session start, guessed to be "an attempt at
teach-i35/teach-t7j," and explicitly forbade the obvious shortcut (editing
the round-3 file's assertion to match the new behavior), since
`GRADE6_UNSIGNPOSTED_GARDENING` is tuning data twice over (teach-cpg,
teach-i35) and abstaining here is not evidence a fix generalizes.

## What I found on arrival

The bead was still open (not previously claimed). Current `git status`
showed the same three modified files the bead described (`.beads/interactions.jsonl`,
`teach/concept_recovery.py`, `tests/test_concept_recovery.py`), plus several
untracked handoffs and scratch files from other sessions. I left all of that
untouched — it belongs to other beads (teach-i35, teach-ngy, teach-cpg, etc.),
not this one.

Running `uv run pytest -q` immediately showed **546 passed, 16 skipped, 1
xfailed — zero failures.** The exact failure this bead reports does not
currently reproduce.

## Why it doesn't reproduce: two independent things changed since filing

1. **`tests/test_concept_recovery_writing_domain_generalization_round3.py`
   was committed** (commit `18c8fc0`, "Track the held-out generalization
   rounds; xfail the teach-i35 boundary," made *after* this bead was filed).
   That commit added `@pytest.mark.xfail(strict=True, raises=AssertionError,
   reason="teach-i35 domain generalization boundary, requires no-repo-access
   round")` to exactly the test this bead names. It does **not** flip the
   assertion — the test still asserts the buggy `7.W` outcome, unchanged.
   `strict=True` means: XFAIL today (abstention, the bug's current state) is
   quiet; XPASS (the confident-wrong-answer regressing back) fails the build
   loudly. This is precisely the mechanism this bead itself said was the only
   acceptable way to resolve the discrepancy ("editing the assertion...
   would convert a measured open question into a false green" — marking
   known-buggy-behavior-as-xfail is not editing the assertion, it's
   classifying the failure honestly). Someone else already did the legitimate
   fix.

2. **The bead's own causal diagnosis was wrong.** I isolated the still-
   uncommitted `teach/concept_recovery.py` diff (via `git stash push -- teach/concept_recovery.py
   tests/test_concept_recovery.py`, confirmed content-identical before/after
   with `git stash show -p`, then `git stash pop` to restore) and re-ran just
   the pinned test with the diff removed:

   ```
   tests/test_concept_recovery_writing_domain_generalization_round3.py x
   1 xfailed
   ```

   Still abstains — **with the uncommitted diff entirely absent.** The flip
   from confident-wrong to abstention was not caused by the uncommitted work
   at all. It was already produced by the previously-*committed* teach-t7j
   fix: `_coverage_fraction` now always recomputes coverage from literal
   word overlap, never from `match.score`, specifically so semantic-tier
   synonym inflation can't lift a false winner's own coverage (see
   `teach/concept_recovery.py`'s module docstring, "COVERAGE IS MEASURED ON
   EXACT WORDS ONLY, EVEN IN THE SEMANTIC TIER (teach-t7j)," which names
   this exact case: "the wrong winner's semantic coverage was 54%, but only
   40% of that was literal overlap, while the true rival's *literal*
   coverage, 56%, exceeded the winner's on either measure"). `git blame`
   traces this to commit `d2f765a` ("Complete the Dummit & Foote -> Judson
   migration," 2026-09-13 15:49, five minutes before the xfail-tracking
   commit) — an oddly-named commit for a `concept_recovery.py` fix, but the
   content is unambiguous.

   The still-uncommitted diff is unrelated: it's teach-ngy's fix to the
   *multi-candidate tie* branch of `_resolve_candidates` (`len(close) > 1`),
   generalizing teach-i35's rival-search pattern to a different branch than
   the one `GRADE6_UNSIGNPOSTED_GARDENING` exercises (the single-close-
   candidate branch). I confirmed it doesn't affect this bead's test either
   way, and confirmed the full suite is green both with it present (546
   passed, 16 skipped, 1 xfailed) and with it stashed out (545 passed — one
   fewer, the missing teach-ngy unit test — 16 skipped, 1 xfailed, still zero
   failures). It remains legitimately in-tree, pending teach-ngy's own
   closing requirements — not this bead's concern.

## What I did NOT do

- Did not touch `tests/test_concept_recovery_writing_domain_generalization_round3.py`
  — no edits needed; it already has the correct xfail-strict marker.
- Did not touch the uncommitted `teach/concept_recovery.py` /
  `tests/test_concept_recovery.py` diff (teach-ngy's in-progress work) — it's
  unrelated to this bug and not this bead's scope.
- Did not run or attempt a fresh held-out round — that's teach-i35's and
  teach-t7j's own closing requirement (showing their fixes generalize), not
  something this bead asked for or needed to establish. Both remain open.
- Did not commit or push anything, per the repo's conservative git policy.
- Left the various untracked scratch files and other-bead handoffs in the
  tree exactly as found.

## Verification

- `uv run pytest -q` (current tree, unmodified): **546 passed, 16 skipped, 1
  xfailed.** No failures.
- `uv run pytest -q -k gardening` on the round3 file, with the uncommitted
  `teach/concept_recovery.py`/`tests/test_concept_recovery.py` diff
  temporarily stashed out: still `1 xfailed` — confirms the abstention is
  independent of that uncommitted work.
- `uv run pytest -q` full suite with the same diff stashed out: `545 passed,
  16 skipped, 1 xfailed` — confirms no failures either way.
- `git status` / `git diff --stat` after all investigation: identical to the
  state at session start (stash pushed and popped cleanly, verified via
  `git stash show -p` byte-for-byte match before dropping).

## Bead disposition

**Closing with `--reason`, not as completed work.** This bead's concrete,
falsifiable claim — "the suite has 1 failing test caused by uncommitted
work" — is no longer true, and wasn't fully true even in its causal
mechanism. The symptom was independently fixed by commit `18c8fc0` (added
after this bead was filed) using exactly the legitimate mechanism this bead
demanded; and the causal attribution to "uncommitted work" doesn't hold up
under isolation — the real cause was an earlier-committed fix (teach-t7j,
commit `d2f765a`). There is nothing left to fix under this bead's title.
The open question this bead gestured at (does teach-i35/teach-t7j's fix
generalize?) is real but belongs to those beads, which are already open,
already carry that exact requirement in their own text, and were not
created or altered by this session.
