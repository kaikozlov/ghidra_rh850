#!/usr/bin/env python3
"""Apply reviewed cluster decisions to a generated candidate census."""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def number(text: str) -> int:
    return int(text, 0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--reviews", required=True, type=Path)
    parser.add_argument("--firmware", required=True, type=Path)
    args = parser.parse_args()

    image = args.firmware.read_bytes()
    with args.candidates.open(newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    if not fields or "adjudication_state" not in fields:
        raise SystemExit("candidate ledger lacks adjudication_state")

    with args.reviews.open(newline="") as handle:
        reviews = list(csv.DictReader(handle))
    seen_ranges: set[tuple[int, int]] = set()
    for review in reviews:
        start = number(review["source_start"])
        end = number(review["source_end_exclusive"])
        key = (start, end)
        if key in seen_ranges:
            raise SystemExit(f"duplicate reviewed range 0x{start:x}..0x{end:x}")
        seen_ranges.add(key)
        if start < 0 or end <= start or end > len(image):
            raise SystemExit(f"invalid reviewed range 0x{start:x}..0x{end:x}")
        actual_hash = hashlib.sha256(image[start:end]).hexdigest()
        if actual_hash != review["source_sha256"]:
            raise SystemExit(
                f"reviewed range 0x{start:x}..0x{end:x} hash {actual_hash} "
                f"!= {review['source_sha256']}"
            )
        if not review["rationale"].strip() or not review["evidence"].strip():
            raise SystemExit(f"reviewed range 0x{start:x} lacks rationale/evidence")

        matched = 0
        for row in rows:
            pointers = {
                number(value)
                for value in row["source_pointer_addrs"].split(";")
                if value
            }
            if not any(start <= pointer < end for pointer in pointers):
                continue
            if row["candidate_class"] != review["candidate_class"]:
                raise SystemExit(
                    f"{row['target_addr']} class {row['candidate_class']} does not match "
                    f"reviewed {review['candidate_class']}"
                )
            if row["adjudication_state"] != "unresolved":
                raise SystemExit(
                    f"{row['target_addr']} already adjudicated as {row['adjudication_state']}"
                )
            row["adjudication_state"] = review["adjudication_state"]
            matched += 1
        expected = int(review["expected_candidate_count"])
        if matched != expected:
            raise SystemExit(
                f"reviewed range 0x{start:x}..0x{end:x} matched {matched}, expected {expected}"
            )

    temporary = args.candidates.with_suffix(args.candidates.suffix + ".tmp")
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(args.candidates)
    print(f"Applied {len(reviews)} reviewed function-discovery clusters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
