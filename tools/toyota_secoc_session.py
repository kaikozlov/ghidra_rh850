#!/usr/bin/env python3
"""Offline/read-only session manager for cross-variant Toyota SecOC research.

This tool turns the formerly implicit Sienna assumptions into explicit session
state without performing ECU mutation. It integrates with the read-only
``toyota_eps_bus_probe.py`` and the offline ``toyota_secoc_oracle.py``.

A session records:
- EPS physical UDS endpoint (0x7A1 -> 0x7A9 by default)
- diagnostic Panda logical bus once discovered
- explicit ELM327 routing parameter
- oracle buses
- protected classic-SecOC IDs
- target openpilot car enum used only for fingerprint planning
- F181/software identity when available
- per-bus/per-ID capture counts

Commands never enter programming mode, request SecurityAccess, write DIDs,
download payloads, start routines, patch firmware, or install keys.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_secoc_oracle import known_protected_ids

DEFAULT_TX = 0x7A1
DEFAULT_RX = 0x7A9
DEFAULT_ELM327_PARAM = 1
DEFAULT_BUSES = (0, 1, 2)
STATE_NAME = "session.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_state(
    *,
    target_car: str,
    elm327_param: int = DEFAULT_ELM327_PARAM,
    oracle_buses: Iterable[int] = DEFAULT_BUSES,
    protected_ids: Iterable[int] | None = None,
) -> dict:
    ids = sorted(set(known_protected_ids() if protected_ids is None else protected_ids))
    return {
        "schema_version": 1,
        "created_at": now(),
        "updated_at": now(),
        "endpoint": {"tx": DEFAULT_TX, "rx": DEFAULT_RX},
        "routing": {
            "diagnostic_bus": "auto",
            "elm327_param": elm327_param,
            "oracle_buses": sorted(set(oracle_buses)),
        },
        "secoc_profile": {
            "sync_id": 0x00F,
            "protected_ids": ids,
        },
        "target_car": target_car,
        "identity": {
            "f181_hex": None,
            "f181_ascii": None,
        },
        "capture": None,
        "fingerprint_plan": None,
    }


def state_path(session_dir: Path) -> Path:
    return session_dir / STATE_NAME


def load_state(session_dir: Path) -> dict:
    path = state_path(session_dir)
    if not path.exists():
        raise FileNotFoundError(f"session does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(session_dir: Path, state: dict) -> None:
    session_dir.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now()
    path = state_path(session_dir)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def response_rows(probe: dict) -> list[dict]:
    results = probe.get("results")
    if not isinstance(results, list):
        raise ValueError("probe JSON has no execution results; run toyota_eps_bus_probe.py --execute")
    return [row for row in results if row.get("status") == "response"]


def record_probe(session_dir: Path, probe_path: Path, *, choose_bus: int | None = None) -> dict:
    state = load_state(session_dir)
    probe = json.loads(probe_path.read_text(encoding="utf-8"))
    plan = probe.get("plan", {})
    if int(plan.get("tx_addr", -1)) != state["endpoint"]["tx"]:
        raise ValueError("probe TX endpoint does not match session")
    if int(plan.get("rx_addr", -1)) != state["endpoint"]["rx"]:
        raise ValueError("probe RX endpoint does not match session")
    if int(plan.get("elm327_param", -1)) != state["routing"]["elm327_param"]:
        raise ValueError("probe ELM327 routing parameter does not match session")

    rows = response_rows(probe)
    if choose_bus is None:
        if len(rows) != 1:
            raise ValueError(f"expected one F181 responder, got buses {[row.get('bus') for row in rows]}; specify --choose-bus")
        selected = rows[0]
    else:
        matches = [row for row in rows if int(row.get("bus", -1)) == choose_bus]
        if len(matches) != 1:
            raise ValueError(f"bus {choose_bus} is not a unique responding bus")
        selected = matches[0]

    state["routing"]["diagnostic_bus"] = int(selected["bus"])
    state["identity"]["f181_hex"] = selected.get("f181_hex")
    state["identity"]["f181_ascii"] = selected.get("f181_ascii")
    state["identity"]["probe_source"] = str(probe_path)
    state["identity"]["responding_buses"] = sorted(int(row["bus"]) for row in rows)
    save_state(session_dir, state)
    return state


def iter_ndjson(path: Path) -> Iterable[dict]:
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            try:
                addr = int(row["addr"])
                bus = int(row["bus"])
                data = bytes.fromhex(str(row["data"]))
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"invalid CAN row {line_no}: {error}") from error
            yield {**row, "addr": addr, "bus": bus, "data": data.hex()}


def ingest_capture(session_dir: Path, capture_path: Path) -> dict:
    state = load_state(session_dir)
    sync_id = int(state["secoc_profile"]["sync_id"])
    protected = set(int(value) for value in state["secoc_profile"]["protected_ids"])
    buses = set(int(value) for value in state["routing"]["oracle_buses"])
    oracle_ids = protected | {sync_id}

    out_path = session_dir / "can_oracle.ndjson"
    counts: Counter[tuple[int, int]] = Counter()
    all_counts: Counter[tuple[int, int]] = Counter()
    retained = 0
    with out_path.open("w", encoding="utf-8") as out:
        for row in iter_ndjson(capture_path):
            key = (row["bus"], row["addr"])
            all_counts[key] += 1
            if row["bus"] not in buses or row["addr"] not in oracle_ids:
                continue
            out.write(json.dumps(row, sort_keys=True) + "\n")
            counts[key] += 1
            retained += 1

    state["capture"] = {
        "source": str(capture_path),
        "oracle_file": str(out_path),
        "retained_frames": retained,
        "oracle_counts": {
            f"bus{bus}:0x{addr:03X}": count
            for (bus, addr), count in sorted(counts.items())
        },
        "all_bus_id_counts": {
            f"bus{bus}:0x{addr:03X}": count
            for (bus, addr), count in sorted(all_counts.items())
        },
    }
    save_state(session_dir, state)
    return state


def make_fingerprint_plan(session_dir: Path) -> dict:
    state = load_state(session_dir)
    f181 = state.get("identity", {}).get("f181_ascii")
    if not f181:
        raise ValueError("F181 is not recorded; record a read-only EPS probe first")
    clean = f181.replace("\x00", "").replace("\x01", "").strip()
    plan = {
        "target_car": state["target_car"],
        "ecu": "eps",
        "address": DEFAULT_TX,
        "sub_address": None,
        "observed_f181": clean,
        "action": "review-only",
        "note": "Use this observed marker when reviewing the target car's firmware fingerprint; this tool does not edit openpilot source.",
    }
    state["fingerprint_plan"] = plan
    save_state(session_dir, state)
    return plan


def oracle_command(session_dir: Path, dump: Path | None = None) -> list[str]:
    state = load_state(session_dir)
    capture = state.get("capture")
    if not capture:
        raise ValueError("no capture has been ingested")
    command = [
        "uv", "run", "--locked", "python", "tools/toyota_secoc_oracle.py",
        "scan" if dump else "profile",
    ]
    if dump:
        command += ["--capture", capture["oracle_file"], "--dump", str(dump)]
        for bus in state["routing"]["oracle_buses"]:
            command += ["--bus", str(bus)]
        for can_id in state["secoc_profile"]["protected_ids"]:
            command += ["--protected-id", hex(can_id)]
    return command


def parse_int(value: str) -> int:
    return int(value, 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("session_dir", type=Path)
    init.add_argument("--target-car", required=True)
    init.add_argument("--elm327-param", type=parse_int, default=DEFAULT_ELM327_PARAM)
    init.add_argument("--oracle-bus", action="append", type=parse_int)
    init.add_argument("--protected-id", action="append", type=parse_int)

    probe = sub.add_parser("record-probe")
    probe.add_argument("session_dir", type=Path)
    probe.add_argument("probe_json", type=Path)
    probe.add_argument("--choose-bus", type=parse_int)

    ingest = sub.add_parser("ingest-can")
    ingest.add_argument("session_dir", type=Path)
    ingest.add_argument("capture", type=Path)

    fp = sub.add_parser("fingerprint-plan")
    fp.add_argument("session_dir", type=Path)

    plan = sub.add_parser("oracle-plan")
    plan.add_argument("session_dir", type=Path)
    plan.add_argument("--dump", type=Path)

    show = sub.add_parser("show")
    show.add_argument("session_dir", type=Path)

    args = parser.parse_args()
    if args.command == "init":
        state = new_state(
            target_car=args.target_car,
            elm327_param=args.elm327_param,
            oracle_buses=args.oracle_bus or DEFAULT_BUSES,
            protected_ids=args.protected_id,
        )
        save_state(args.session_dir, state)
        output = state
    elif args.command == "record-probe":
        output = record_probe(args.session_dir, args.probe_json, choose_bus=args.choose_bus)
    elif args.command == "ingest-can":
        output = ingest_capture(args.session_dir, args.capture)
    elif args.command == "fingerprint-plan":
        output = make_fingerprint_plan(args.session_dir)
    elif args.command == "oracle-plan":
        output = {"command": oracle_command(args.session_dir, args.dump)}
    else:
        output = load_state(args.session_dir)

    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
