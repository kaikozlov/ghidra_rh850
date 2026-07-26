#!/usr/bin/env python3
"""Fingerprint the vendored Renesas_v850 processor sources."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "ghidra" / "ghidra_v850"
LANG = VENDOR / "data" / "languages"

SOURCE_GLOBS = (
    "*.slaspec",
    "*.sinc",
    "*.cspec",
    "*.pspec",
    "*.ldefs",
    "*.opinion",
)
META_FILES = (
    VENDOR / "extension.properties",
    VENDOR / "Module.manifest",
    VENDOR / "PROVENANCE.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_sources() -> dict[str, str]:
    files: dict[str, str] = {}
    for pattern in SOURCE_GLOBS:
        for path in sorted(LANG.glob(pattern)):
            rel = path.relative_to(ROOT).as_posix()
            files[rel] = sha256_file(path)
    for path in META_FILES:
        if path.is_file():
            rel = path.relative_to(ROOT).as_posix()
            files[rel] = sha256_file(path)
    return files


def build_manifest(
    *,
    ghidra_version: str | None = None,
    cli_version: str | None = None,
    sla_hash: str | None = None,
) -> dict[str, object]:
    files = collect_sources()
    ordered = sorted(files.items())
    aggregate = hashlib.sha256()
    for rel, digest in ordered:
        aggregate.update(rel.encode())
        aggregate.update(b"\0")
        aggregate.update(digest.encode())
        aggregate.update(b"\0")
    return {
        "schema_version": 1,
        "language_id": "v850e3:LE:32:default",
        "source_fingerprint": aggregate.hexdigest(),
        "files": dict(ordered),
        "ghidra_version": ghidra_version,
        "ghidra_cli_version": cli_version,
        "compiled_sla_sha256": sla_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="Write manifest JSON to this path")
    parser.add_argument("--expect", type=Path, help="Compare against an existing manifest")
    parser.add_argument("--ghidra-version")
    parser.add_argument("--cli-version")
    parser.add_argument("--sla", type=Path, help="Compiled v850e3.sla to hash")
    args = parser.parse_args()

    sla_hash = sha256_file(args.sla) if args.sla else None
    manifest = build_manifest(
        ghidra_version=args.ghidra_version,
        cli_version=args.cli_version,
        sla_hash=sla_hash,
    )

    if args.expect:
        expected = json.loads(args.expect.read_text())
        if expected.get("source_fingerprint") != manifest["source_fingerprint"]:
            print(
                "ERROR: processor source fingerprint mismatch\n"
                f"  expected={expected.get('source_fingerprint')}\n"
                f"  actual  ={manifest['source_fingerprint']}",
                file=sys.stderr,
            )
            return 1
        print(f"[PASS] source_fingerprint == {manifest['source_fingerprint']}")

    text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text)
        print(f"Wrote {args.write}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
