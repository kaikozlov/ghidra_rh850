#!/usr/bin/env python3
"""Decompile every selected semantic-interest function reproducibly."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RANKING = REPO / "data/generated/semantic_interest_ranking.csv"
INVENTORY = REPO / "data/ghidra_project_inventory.baseline.jsonl"
DEFAULT_OUTPUT = REPO / "data/generated/semantic_sweep_decompilations.jsonl"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_payload(stdout: str) -> dict:
    for line in reversed(stdout.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list) and len(payload) == 1 and isinstance(payload[0], dict):
            return payload[0]
        if isinstance(payload, dict):
            return payload
    raise ValueError("tools/g produced no JSON payload")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=REPO / "build/work/project")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    project_dir = args.project_dir.resolve()
    committed = (REPO / "project").resolve()
    if project_dir == committed or committed in project_dir.parents:
        raise SystemExit(f"refusing committed project: {project_dir}")
    if not (project_dir / "rh850_p1me_mapped.rep").is_dir():
        raise SystemExit(f"missing working project: {project_dir}")

    with RANKING.open(newline="") as stream:
        selected = [row for row in csv.DictReader(stream)
                    if row["selected_for_sweep"] == "true"]
    environment = os.environ.copy()
    environment.update({"GHIDRA_AGENT": "1", "GHIDRA_PROJECT": str(project_dir)})
    (REPO / "build" / "tmp").mkdir(parents=True, exist_ok=True)
    # Refuse to attribute the committed inventory hash to an unrelated live
    # project.  Export and compare the selected project before decompiling it.
    with tempfile.TemporaryDirectory(prefix="semantic-sweep-inventory-", dir=REPO / "build" / "tmp") as tmp:
        live_inventory = Path(tmp) / "live-project.jsonl"
        inventory_env = environment.copy()
        inventory_env["PROJECT_DIR"] = str(project_dir)
        exported = subprocess.run(
            [str(REPO / "tools/generate_project_inventory.sh"), str(live_inventory)],
            cwd=REPO, env=inventory_env, capture_output=True, text=True,
        )
        if exported.returncode:
            raise SystemExit(
                "live project inventory export failed:\n"
                + exported.stdout + "\n" + exported.stderr
            )
        compared = subprocess.run(
            [sys.executable, str(REPO / "tools/project_inventory.py"), "compare",
             str(INVENTORY), str(live_inventory)],
            cwd=REPO, capture_output=True, text=True,
        )
        if compared.returncode:
            raise SystemExit(
                f"live project does not match {INVENTORY.relative_to(REPO)}:\n"
                + compared.stdout + "\n" + compared.stderr
            )
    records = []
    try:
        for index, row in enumerate(selected, 1):
            address = row["entry_addr"]
            completed = subprocess.run(
                [str(REPO / "tools/g"), "decompile", address, "--json"],
                cwd=REPO, env=environment, capture_output=True, text=True,
            )
            if completed.returncode:
                raise SystemExit(
                    f"decompile failed for {address}:\n{completed.stdout}\n{completed.stderr}"
                )
            payload = parse_payload(completed.stdout)
            if payload.get("error"):
                raise SystemExit(f"decompile failed for {address}: {payload['error']}")
            code = payload.get("code", "").replace("\r\n", "\n")
            if not code.strip():
                raise SystemExit(f"empty decompilation for {address}")
            records.append({
                "record": "function",
                "entry_addr": address,
                "rank": int(row["rank"]),
                "scalar_top_n": row["scalar_top_n"] == "true",
                "strata": row["strata"].split(";") if row["strata"] else [],
                "name": payload.get("name", ""),
                "signature": payload.get("signature", ""),
                "normalized_c_sha256": hashlib.sha256(code.encode()).hexdigest(),
                "decompiled_c": code,
            })
            print(f"[{index}/{len(selected)}] {address} {payload.get('name', '')}")
    finally:
        subprocess.run(
            [str(REPO / "tools/g"), "stop"], cwd=REPO, env=environment,
            capture_output=True, text=True,
        )

    metadata = {
        "record": "metadata",
        "schema_version": 1,
        "selected_count": len(selected),
        "ranking_path": RANKING.relative_to(REPO).as_posix(),
        "ranking_sha256": sha256(RANKING),
        "project_inventory_path": INVENTORY.relative_to(REPO).as_posix(),
        "project_inventory_sha256": sha256(INVENTORY),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        for record in (metadata, *records):
            stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"Wrote {len(records)} decompilations to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
