# teach-d8g: drift-guard kind mismatch in test_judson_ring_field.py

## Bug, confirmed

`test_extract_still_matches_the_live_pinned_source` filtered live blocks with
`b.kind == DEFINITION_KIND` (hardcoded), but `EXTRA_STATEMENT_IDS`
(teach-59u, teach-911) deliberately folds in `TAGGED_BLOCK_KINDS` blocks --
theorem, lemma, example -- whose provenance records their real `kind`. A
provenance entry with `kind='example'` (`judson:16.1-rings` /
`rings-example-matrix`, added by teach-911) could never match the guard's
DEFINITION_KIND-only filter, so the guard always failed for that node
regardless of whether the source had actually drifted. Reproduced with the
live pinned source fetched into a scratch `$HOME` (see "How I verified
this" below) before making any change -- same `AssertionError` the bead
quotes, byte for byte.

Per the bead's own framing: the `file_sha256` for `rings.xml` still matched,
so this was an extractor/guard mismatch, not upstream drift -- confirming the
guard was the wrong side, not the extractor or the stored provenance.

## Fix

`tests/test_judson_ring_field.py`, `test_extract_still_matches_the_live_pinned_source`:

1. Match on `b.kind == p["kind"]` (the kind the extractor actually recorded)
   instead of the hardcoded `DEFINITION_KIND` import. This generically covers
   every kind `extract_judson_ring_field.py` can produce (term-definition,
   theorem, lemma, example, ...) without special-casing any one of them.
2. Fixing (1) surfaced a second, previously-unreached bug in the same
   assertion: for `judson:16.1-rings` / `rings-example-matrix`, provenance
   carries `"excerpted": True` (teach-scx elides the word "form" from the
   live block's raw text before it goes into the node's `definition`). The
   guard's second assert compared the *unedited* live block text against the
   *edited* extracted definition, so it would always fail for any excerpted
   entry -- this was unreached before only because the kind-filter bug above
   made `match` empty and raised first. Fixed by applying
   `extract_judson_ring_field._excerpted_text(node_id, block)` to the live
   block before the substring check whenever `p.get("excerpted")` is set,
   which is the same transform the extractor itself applies, so the guard now
   checks "would re-running the extractor today produce the same excerpted
   text," not "is the raw source byte-identical to the excerpt."

Both fixes are additive precision (the guard now checks more of what it
claims to check); neither loosens any existing check. The `file_sha256`
comparison (whole-file drift) is untouched.

## How I verified this

The pinned Judson source (`aata-3069910e3ded72ff5e18837a97a0e810c92790e2`,
881MB-class, deliberately not vendored) is not cached under this sandbox's
real `$HOME` and `~/.cache` is root-owned (not writable by `node`), so
`needs_judson`-marked tests normally skip here. To actually exercise the
drift guard against live source rather than reasoning about it from the
diff:

```
curl -sL -o /tmp/aata.tar.gz \
  "https://codeload.github.com/twjudson/aata/tar.gz/3069910e3ded72ff5e18837a97a0e810c92790e2"
mkdir -p /tmp/fakehome/.cache/teach-upstream/textbooks
tar xzf /tmp/aata.tar.gz -C /tmp/fakehome/.cache/teach-upstream/textbooks
HOME=/tmp/fakehome uv run pytest tests/test_judson_ring_field.py -v
```

(`teach.pretext_parser.JUDSON_SRC` is built from `pathlib.Path.home()`, which
respects `$HOME`, so this is the real `iter_blocks` parse of the real pinned
source -- not a fixture standing in for it.)

- Before the fix: reproduced the exact failure the bead quotes (`no live
  block for {..., 'kind': 'example', ...}`).
- After fix (1) alone: a *new* failure appeared at the excerpted-text assert
  -- confirms fix (1) was necessary but not sufficient, and that the
  excerpted-text bug was real and previously unreached, not hypothetical.
- After both fixes: `tests/test_judson_ring_field.py` -- 19 passed, 0 skipped
  (all `needs_judson` tests ran against live source).
- Drift-guard sensitivity check: mutated a word inside the
  `rings-example-matrix` block in the live `rings.xml`, reran the single
  drift test -- it failed loudly on the `file_sha256` mismatch (`rings.xml
  changed on disk`), confirming the guard still catches real drift and my
  change didn't make it vacuously pass. Restored the file, reran, back to
  green.
- Full suite with `HOME=/tmp/fakehome` (Judson source present, Levin source
  still absent): 716 passed, 3 skipped (all 3 are Levin-source-only tests,
  unrelated to this bead), 1 xfailed.
- Full suite in the normal (unmodified) environment, to confirm no
  regression for workers without a fetched source cache: 703 passed, 16
  skipped, 1 xfailed -- same as pre-fix modulo the tests this bead's fix
  touches, all `needs_judson` tests skip exactly as before.
- Deleted the scratch tarball (`/tmp/aata.tar.gz`, `/tmp/judsontest`) when
  done; `/tmp/fakehome` is scratch-only and was never referenced from
  anything committed. Nothing under `/workspace` was touched except the one
  test file.

## Files changed

- `tests/test_judson_ring_field.py` -- the two-part fix above. No production
  code (`teach/extract_judson_ring_field.py`, `teach/pretext_parser.py`,
  `teach/data/judson_ring_field.json`) changed; the bead's own analysis said
  the guard was the wrong side, and that held up under live verification.

## Scope note

The working tree had substantial unrelated pre-existing modifications and
untracked files (other `teach-8xw.*` sub-beads, other sandbox-handoffs) when
I started. I did not touch any of them -- only
`tests/test_judson_ring_field.py`. Not committing per the conservative git
policy; `git status`/`git diff` on that one file is the full change.
