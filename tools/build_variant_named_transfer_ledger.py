#!/usr/bin/env python3
"""Join exact-byte and structural cross-variant results for named functions.

The input artifacts intentionally have different evidence strengths:

* exact-body transfer proves every canonical Ghidra body range is byte-identical
  at one target relocation;
* unique structural transfer proves only that the complete mnemonic +
  instruction-length sequence is unique on both images. Operands/constants/data
  addresses/call targets may differ;
* absence from both classes is an unresolved/changed result, never proof that an
  analogous target function or behavior is absent.

The resulting ledger is designed for navigation and review, not automatic
semantic promotion.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "rh850-cross-image-named-function-transfer-ledger-v1"

EXACT_CLASSES = {"exact-same-va", "exact-unique-relocated"}

_TAG_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("diagnostics", re.compile(r"(uds_|dcm_|diagnostic|security_access|session|routine|did_|rdbi|wdbi|rmba|request_download|transfer_data|transfer_exit|tester_present|ecu_reset)", re.I)),
    ("secoc_icus", re.compile(r"(secoc|icus|cryptoif|freshness|key_update)", re.I)),
    ("xcp", re.compile(r"(^xcp_|xcp)", re.I)),
    ("storage_nvm", re.compile(r"(nvm_|dataflash|checkpoint|persist|triplicate)", re.I)),
    ("can_com", re.compile(r"(canif|cantp|rscfd|com_|pdur|can_rx|can_tx)", re.I)),
    ("steering", re.compile(r"(steer|torque_command|lta|angle_speed_plausibility)", re.I)),
    ("motor_control", re.compile(r"(motor|dq_|clarke|park|phase_|pwm|tsg3|current_|rotating_frame|duty_)", re.I)),
    ("scheduler_system", re.compile(r"(scheduler|system_mode|task_|watchdog|system_transition|subsystem_init|startup)", re.I)),
    ("crypto", re.compile(r"(aes|cmac|crypto|cipher|decrypt|encrypt)", re.I)),
)


def _tags(name: str) -> list[str]:
    return [tag for tag, pattern in _TAG_PATTERNS if pattern.search(name)]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build(raw: dict[str, Any], structural: dict[str, Any]) -> dict[str, Any]:
    structural_by_reference = {
        int(row["reference_entry"], 16): row for row in structural["matches"]
    }
    rows: list[dict[str, Any]] = []

    for raw_row in raw["functions"]:
        name = raw_row.get("name")
        if not name:
            continue
        reference_entry = int(raw_row["reference_entry"], 16)
        structural_row = structural_by_reference.get(reference_entry)

        if raw_row["classification"] in EXACT_CLASSES:
            status = "exact-byte-transfer"
            target_entry = raw_row["target_entry"]
            evidence = (
                "complete canonical Ghidra body ranges are byte-identical at the target entry"
            )
        elif structural_row is not None:
            status = "unique-instruction-shape-candidate"
            target_entry = structural_row["target_entry"]
            evidence = (
                "complete mnemonic + instruction-length sequence is unique on both images; "
                "operands/constants/data/call targets are not proved equal"
            )
        else:
            status = "changed-or-unresolved"
            target_entry = None
            evidence = (
                "no exact body transfer or unique complete instruction-shape match; analogous "
                "target behavior/function may still exist and requires target-native recovery"
            )

        candidate = raw_row.get("alignment_candidate")
        row = {
            "reference_entry": raw_row["reference_entry"],
            "reference_name": name,
            "reference_region": "boot" if reference_entry < 0x20000 else "application",
            "semantic_tags": _tags(name),
            "status": status,
            "target_entry": target_entry,
            "evidence_boundary": evidence,
            "body_size": raw_row["body_size"],
            "raw_body_classification": raw_row["classification"],
            "raw_body_target_entry": raw_row.get("target_entry"),
            "raw_body_delta": raw_row.get("delta"),
            "structural_target_entry": None if structural_row is None else structural_row["target_entry"],
            "structural_instruction_count": None if structural_row is None else structural_row["instruction_count"],
            "triage_alignment_target_entry": None if candidate is None else candidate.get("target_entry"),
            "triage_byte_equal_ratio": None if candidate is None else candidate.get("byte_equal_ratio"),
        }
        rows.append(row)

    rows.sort(key=lambda row: int(row["reference_entry"], 16))
    status_counts = collections.Counter(row["status"] for row in rows)
    region_counts: dict[str, dict[str, int]] = {}
    for region in ("boot", "application"):
        region_rows = [row for row in rows if row["reference_region"] == region]
        counts = collections.Counter(row["status"] for row in region_rows)
        region_counts[region] = {
            "named_function_count": len(region_rows),
            **dict(sorted(counts.items())),
        }

    tag_summary: dict[str, dict[str, int]] = {}
    for tag, _ in _TAG_PATTERNS:
        tagged = [row for row in rows if tag in row["semantic_tags"]]
        if not tagged:
            continue
        counts = collections.Counter(row["status"] for row in tagged)
        tag_summary[tag] = {
            "named_function_count": len(tagged),
            **dict(sorted(counts.items())),
        }

    return {
        "schema": SCHEMA,
        "evidence_boundary": (
            "Navigation ledger only. exact-byte-transfer is a raw body proof; "
            "unique-instruction-shape-candidate is not semantic identity; changed-or-unresolved "
            "is not proof of absence. Semantic tags are name-based review aids and can overlap."
        ),
        "reference": raw["reference"],
        "target": raw["target"],
        "source_artifacts": {
            "raw_body_schema": raw["schema"],
            "structural_schema": structural["schema"],
            "structural_reference_sha256": structural["reference"]["sha256"],
            "structural_target_sha256": structural["target"]["sha256"],
        },
        "summary": {
            "named_function_count": len(rows),
            "status_counts": dict(sorted(status_counts.items())),
            "region_counts": region_counts,
            "semantic_tag_counts": tag_summary,
        },
        "functions": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-body-transfer", type=Path, required=True)
    parser.add_argument("--structural-transfer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = build(_load(args.raw_body_transfer), _load(args.structural_transfer))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "summary": report["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
