#!/usr/bin/env python3
"""Regenerate the minimal shared H/F application seed manifest."""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
OUTPUT = REPO / "data/targets/corolla-hf/function_seeds.csv"
SOURCES = (
    "data/generated/corolla_8965H1202000_b6_full_receiver_decompiler_evidence.json",
    "data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json",
    "data/generated/corolla_8965H1202000_cooperative_authority_wire_decompiler_evidence.json",
    "data/generated/corolla_8965H1202000_lta_command_provenance_decompiler_evidence.json",
    "data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json",
    "data/generated/corolla_8965H1202000_secoc_key_provenance_decompiler_evidence.json",
)
EXPECTED_COUNT = 143


def render() -> str:
    provenance: dict[int, set[str]] = {}
    for relative in SOURCES:
        path = REPO / relative
        artifact = json.loads(path.read_text(encoding="utf-8"))
        if artifact.get("software_id") != "8965H1202000":
            raise SystemExit(f"software identity drift: {relative}")
        for row in artifact.get("functions", []):
            raw = row.get("entry") or row.get("entry_addr") or row.get("address")
            if not isinstance(raw, str) or not raw.startswith("0x"):
                raise SystemExit(f"missing function entry in {relative}")
            address = int(raw, 16)
            if not 0x20000 <= address < 0x100000:
                raise SystemExit(f"non-application seed {raw} in {relative}")
            provenance.setdefault(address, set()).add(relative)
    if len(provenance) != EXPECTED_COUNT:
        raise SystemExit(f"seed count drift: {len(provenance)} != {EXPECTED_COUNT}")

    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("address", "provenance", "note"))
    for address, sources in sorted(provenance.items()):
        writer.writerow((
            f"0x{address:08X}",
            ";".join(sorted(sources)),
            "exact-H function; transfers to F through verified byte-identical application",
        ))
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit(f"generated seed manifest drift: {OUTPUT.relative_to(REPO)}")
        print(f"checked {OUTPUT.relative_to(REPO)}")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8", newline="")
        print(f"wrote {EXPECTED_COUNT} seeds to {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
