"""What upstream bytes an extract in `teach/data/` was built from.

The Learning Commons exports this repo's VA SOL graphs are derived from are
881MB across two files. They are NOT in this repo and NOT gitignored inside
it -- they live in `~/.cache/teach-upstream/`, outside the working tree
entirely. A gitignored blob in the tree is one `git add -A` away from being
committed; a path outside it cannot be committed by accident at all. What
belongs in the repo is the provenance, not the payload:
`teach/data/upstream_provenance.json` is a few hundred bytes.

WHY THIS EXISTS (teach-8xw.54)

`retrieved_via` recorded a URL and nothing else, and the URL's only version
anchor is the string "v1.13.0" in a CDN path. That path is mutable: an
unauthenticated HEAD returns 200 from S3, and nothing stops the same version
being republished with different bytes. So "which graph was this lesson
planned from" had no answer, and this repo's central claim -- that the
prerequisites an instruction assumed were genuinely established -- was
unauditable after the fact. Not wrong; uncheckable, which is the failure mode
`sandbox-prompt.md` is built against.

WHAT THIS CANNOT DO

It cannot retroactively pin the extracts already committed here. The
downloads they were built from were deleted as re-downloadable (see
`sandbox-handoffs/teach-8xw.2.md`), so their upstream bytes are unrecoverable.
A hash taken today describes today's upstream, not theirs. Attaching one to
those files would be a fabricated audit trail -- strictly worse than the
missing field it replaced -- so the record says `does_not_apply_to` instead,
and this module reports "unrecorded" rather than guessing.
"""

import hashlib
import json
import pathlib
import urllib.request

CACHE = pathlib.Path.home() / ".cache/teach-upstream/learningcommons-v1.13.0"
RECORD = pathlib.Path(__file__).parent / "data/upstream_provenance.json"

# Extracts that predate any provenance record. Listed explicitly rather than
# inferred from mtimes: a file's mtime changes when anyone touches it, and
# "this extract's upstream state is unknown" must not quietly become "known"
# because someone reformatted the JSON.
UNRECORDED_EXTRACTS = (
    "va_math_sol_k8.json",
    "va_math_sol_hs.json",
    "va_reading_sol_k8.json",
    "va_writing_sol_k12.json",
)


def load_record() -> dict:
    return json.loads(RECORD.read_text())


def _sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_local(record: dict | None = None) -> dict[str, str]:
    """Do the cached files still hash to what the record says?

    Offline. Returns {filename: "ok" | "missing" | "MODIFIED"} -- a local
    cache that has drifted from the record is as much a provenance failure as
    an upstream that has, and is likelier, since anything on this machine can
    write to it.
    """
    record = record or load_record()
    out = {}
    for name, expected in record["files"].items():
        path = CACHE / name
        if not path.is_file():
            out[name] = "missing"
        elif _sha256(path) == expected["sha256"]:
            out[name] = "ok"
        else:
            out[name] = "MODIFIED"
    return out


def check_upstream(record: dict | None = None) -> dict[str, str]:
    """Has the CDN republished under the same version string? Needs network.

    Compares content-length and ETag, which is all a HEAD gives us -- cheap
    enough to run before any rebuild, and enough to catch a silent
    republication. A match is not proof the bytes are identical (only a full
    re-download and rehash is), so "unchanged" here means "nothing detected",
    which is what this returns rather than "verified".
    """
    record = record or load_record()
    out = {}
    for name, expected in record["files"].items():
        req = urllib.request.Request(record["base_url"] + name, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as resp:
            length = resp.headers.get("content-length")
            etag = resp.headers.get("etag")
        if str(expected["content_length"]) != str(length):
            out[name] = f"CHANGED: content-length {expected['content_length']} -> {length}"
        elif expected["upstream_etag"] != etag:
            out[name] = f"CHANGED: etag {expected['upstream_etag']} -> {etag}"
        else:
            out[name] = "nothing detected"
    return out


def upstream_state_for(extract_filename: str) -> dict | str:
    """The provenance for one `teach/data/` extract, or the plain string
    "unrecorded" for the ones that predate this record. Callers that publish
    or cite an extract must surface this verbatim -- an absent field reads as
    "not applicable", where "unrecorded" reads as what it is."""
    if extract_filename in UNRECORDED_EXTRACTS:
        return "unrecorded"
    return load_record()


def _selfcheck() -> None:
    record = load_record()
    assert record["files"], "provenance record has no files"
    for name, entry in record["files"].items():
        assert len(entry["sha256"]) == 64, f"{name}: sha256 is not a full digest"
        assert entry["content_length"] > 0, f"{name}: no content length"

    # The honesty property this module exists to protect: the four extracts
    # committed before any provenance existed must report "unrecorded", never
    # today's hashes. A refactor that makes this return the record for them
    # would manufacture an audit trail for bytes nobody has.
    for name in UNRECORDED_EXTRACTS:
        assert upstream_state_for(name) == "unrecorded", (
            f"{name} must report 'unrecorded' -- its upstream bytes are gone and "
            "cannot be reconstructed from a later download"
        )
    assert upstream_state_for("some_future_extract.json") == record

    # Drift detection has to actually detect drift. Checked against a doctored
    # record rather than trusted: an assertion never seen to fail is unverified.
    doctored = json.loads(json.dumps(record))
    first = next(iter(doctored["files"]))
    doctored["files"][first]["sha256"] = "0" * 64
    if (CACHE / first).is_file():
        assert verify_local(doctored)[first] == "MODIFIED", "hash drift went undetected"
        assert verify_local(record)[first] == "ok", "a matching hash was reported as drift"
        local = "verified against the real 881MB cache"
    else:
        local = "cache absent, hash comparison not exercised"

    print(
        f"OK: provenance record covers {len(record['files'])} upstream file(s) "
        f"retrieved {record['retrieved_at']}; all {len(UNRECORDED_EXTRACTS)} "
        f"pre-record extracts correctly report 'unrecorded'; local {local}. "
        "Upstream drift check (check_upstream) needs network and is not run here."
    )


if __name__ == "__main__":
    _selfcheck()
