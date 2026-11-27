#!/usr/bin/env python3
"""Verify that tracked recognizer ledgers match the current recognizer inputs."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from tools import REPO_ROOT
from tools.project.analysis_target import load
from tools.project.recognizer_revision import compute_recognizer_revision

HEX_SHA256 = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class Stage:
    name: str
    ledger_field: str
    summary_field: str
    make_target: str
    bound_schema: int


STAGES = (
    Stage(
        "function discovery",
        "outside_function_candidates",
        "outside_function_summary",
        "generate-function-discovery",
        2,
    ),
    Stage(
        "semantic coverage",
        "semantic_coverage_ledger",
        "semantic_coverage_summary",
        "generate-semantic-coverage",
        3,
    ),
)


def regeneration_command(stage: Stage, target_name: str, metadata: dict) -> str:
    return (
        f'make {stage.make_target} TARGET={target_name} '
        f'PROJECT_DIR="$PWD/{metadata["work_dir"]}"'
    )


def check_stage(
    stage: Stage, target_name: str, metadata: dict, current: str
) -> tuple[bool, bool]:
    ledger = REPO_ROOT / metadata[stage.ledger_field]
    summary_path = REPO_ROOT / metadata[stage.summary_field]
    command = regeneration_command(stage, target_name, metadata)
    label = f"{target_name} {stage.name}"

    if not ledger.is_file() or not summary_path.is_file():
        print(f"[FAIL] {label}: missing {ledger if not ledger.is_file() else summary_path}")
        print(f"       regenerate: {command}")
        return False, False

    summary = json.loads(summary_path.read_text())
    recorded_revision = summary.get("recognizer_revision")
    recorded_ledger_sha256 = summary.get("ledger_sha256")

    if recorded_revision == "unbound":
        if recorded_ledger_sha256 != "unbound":
            print(
                f"[FAIL] {label}: unbound revision has ledger SHA-256 "
                f"{recorded_ledger_sha256!r}"
            )
            print(f"       regenerate: {command}")
            return False, False
        print(f"[WARN] {label}: recognizer revision and ledger SHA-256 are unbound")
        print(f"       establish the first binding: {command}")
        return True, True

    problems: list[str] = []
    if (
        not isinstance(recorded_revision, str)
        or HEX_SHA256.fullmatch(recorded_revision) is None
    ):
        problems.append(f"invalid summary revision {recorded_revision!r}")
    elif recorded_revision != current:
        problems.append(f"recorded revision {recorded_revision}, current {current}")
    if (
        not isinstance(recorded_ledger_sha256, str)
        or HEX_SHA256.fullmatch(recorded_ledger_sha256) is None
    ):
        problems.append(f"invalid ledger SHA-256 {recorded_ledger_sha256!r}")
    else:
        with ledger.open("rb") as handle:
            current_ledger_sha256 = hashlib.file_digest(handle, "sha256").hexdigest()
        if recorded_ledger_sha256 != current_ledger_sha256:
            problems.append(
                f"recorded ledger SHA-256 {recorded_ledger_sha256}, current {current_ledger_sha256}"
            )
    if summary.get("schema_version") != stage.bound_schema:
        problems.append(
            f"summary schema {summary.get('schema_version')!r}, expected {stage.bound_schema}"
        )

    if problems:
        print(f"[FAIL] {label}: {'; '.join(problems)}")
        print(f"       regenerate: {command}")
        return False, False

    print(
        f"[PASS] {label}: revision {recorded_revision}, "
        f"ledger {recorded_ledger_sha256}"
    )
    return True, False


def main() -> int:
    current = compute_recognizer_revision()
    print(f"Recognizer revision: {current}")
    checked = 0
    unbound = 0
    failed = 0
    for target_name, metadata in load()["targets"].items():
        for stage in STAGES:
            if stage.ledger_field not in metadata:
                continue
            checked += 1
            passed, was_unbound = check_stage(stage, target_name, metadata, current)
            failed += not passed
            unbound += was_unbound
    if checked == 0:
        print("[FAIL] no registered recognizer ledgers")
        return 1
    print(f"Summary: {checked - unbound - failed} bound, {unbound} unbound, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
