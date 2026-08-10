#!/usr/bin/env python3
"""Verify the cross-variant Toyota SecOC research-session manager."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_secoc_session import (
    DEFAULT_BUSES,
    DEFAULT_ELM327_PARAM,
    ingest_capture,
    load_state,
    make_fingerprint_plan,
    new_state,
    oracle_command,
    record_probe,
    save_state,
)
from tools.toyota_secoc_signer import sign_classic_frame, sign_sync_frame

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


KEY = bytes.fromhex("00112233445566778899aabbccddeeff")
TRIP, RESET = 0x1234, 0x56789

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    session = root / "session"
    state = new_state(target_car="CAR.TEST", elm327_param=1)
    save_state(session, state)

    print("== explicit session defaults ==")
    state = load_state(session)
    check("diagnostic bus starts unresolved", state["routing"]["diagnostic_bus"] == "auto")
    check("normal ELM327 routing is explicit default", state["routing"]["elm327_param"] == DEFAULT_ELM327_PARAM == 1)
    check("all Panda buses are oracle candidates", state["routing"]["oracle_buses"] == list(DEFAULT_BUSES))
    check("full eight-ID protected profile is stored", len(state["secoc_profile"]["protected_ids"]) == 8)
    check("profile includes 0x116", 0x116 in state["secoc_profile"]["protected_ids"])
    check("profile includes 0x24D", 0x24D in state["secoc_profile"]["protected_ids"])
    check("target car is a recorded session property", state["target_car"] == "CAR.TEST")

    print("\n== read-only F181 probe integration ==")
    probe = root / "probe.json"
    probe.write_text(json.dumps({
        "plan": {"tx_addr": 0x7A1, "rx_addr": 0x7A9, "elm327_param": 1},
        "results": [
            {"bus": 0, "status": "no-response", "error": "timeout"},
            {"bus": 1, "status": "response", "f181_hex": "0138393635463132333435363700", "f181_ascii": "\u00018965F1234567\u0000"},
            {"bus": 2, "status": "no-response", "error": "timeout"},
        ],
    }) + "\n")
    state = record_probe(session, probe)
    check("unique F181 responder becomes diagnostic bus", state["routing"]["diagnostic_bus"] == 1)
    check("F181 hex is persisted", state["identity"]["f181_hex"].startswith("01"))
    check("responding-bus set is persisted", state["identity"]["responding_buses"] == [1])

    ambiguous = root / "ambiguous.json"
    ambiguous.write_text(json.dumps({
        "plan": {"tx_addr": 0x7A1, "rx_addr": 0x7A9, "elm327_param": 1},
        "results": [
            {"bus": 0, "status": "response", "f181_hex": "01", "f181_ascii": "a"},
            {"bus": 2, "status": "response", "f181_hex": "02", "f181_ascii": "b"},
        ],
    }) + "\n")
    try:
        record_probe(session, ambiguous)
    except ValueError as error:
        check("ambiguous F181 responders fail closed", "expected one F181 responder" in str(error))
    else:
        check("ambiguous F181 responders fail closed", False)

    print("\n== capture ingestion ==")
    capture = root / "all_can.ndjson"
    sync = sign_sync_frame(KEY, TRIP, RESET)
    f116 = sign_classic_frame(KEY, 0x116, bytes.fromhex("01020304"), TRIP, RESET, 0x2A)
    f24d = sign_classic_frame(KEY, 0x24D, bytes.fromhex("10203040"), TRIP, RESET, 0x31)
    rows = [
        {"addr": 0x0F, "bus": 1, "data": sync.hex(), "ts_ms": 1},
        {"addr": 0x116, "bus": 1, "data": f116.hex(), "ts_ms": 2},
        {"addr": 0x24D, "bus": 1, "data": f24d.hex(), "ts_ms": 3},
        {"addr": 0x2E4, "bus": 2, "data": "0000000000000000", "ts_ms": 4},
        {"addr": 0x123, "bus": 1, "data": "0000000000000000", "ts_ms": 5},
    ]
    capture.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    state = ingest_capture(session, capture)
    counts = state["capture"]["oracle_counts"]
    check("ingest records bus-1 sync count", counts["bus1:0x00F"] == 1)
    check("ingest records bus-1 0x116 count", counts["bus1:0x116"] == 1)
    check("ingest records bus-1 0x24D count", counts["bus1:0x24D"] == 1)
    check("ingest retains configured known 0x2E4 on another bus", counts["bus2:0x2E4"] == 1)
    check("unprofiled 0x123 stays out of oracle counts", not any("0x123" in key for key in counts))
    check("full traffic inventory still records unprofiled 0x123", state["capture"]["all_bus_id_counts"]["bus1:0x123"] == 1)

    print("\n== fingerprint planning and oracle handoff ==")
    plan = make_fingerprint_plan(session)
    check("fingerprint plan is review-only", plan["action"] == "review-only")
    check("fingerprint plan uses observed EPS address", plan["address"] == 0x7A1)
    check("fingerprint plan uses recorded F181", "8965F1234567" in plan["observed_f181"])

    dump = root / "dump.bin"
    dump.write_bytes(b"\x00" * 32768)
    command = oracle_command(session, dump)
    check("oracle plan delegates to generic scanner", "tools/toyota_secoc_oracle.py" in command and "scan" in command)
    check("oracle plan passes all three buses", all(str(bus) in command for bus in (0, 1, 2)))
    check("oracle plan passes 0x116", "0x116" in command)
    check("oracle plan passes 0x24d", "0x24d" in command)

    print("\n== CLI is dry/offline by construction ==")
    script = REPO / "tools/toyota_secoc_session.py"
    show = subprocess.run([sys.executable, str(script), "show", str(session)], cwd=REPO, text=True, capture_output=True)
    check("show CLI succeeds", show.returncode == 0, show.stderr.strip())
    cli_state = json.loads(show.stdout)
    check("show CLI preserves diagnostic bus", cli_state["routing"]["diagnostic_bus"] == 1)
    source = script.read_text(encoding="utf-8")
    for forbidden in (
        "diagnostic_session_control(", "security_access(", "write_data_by_identifier(",
        "request_download", "routine_control(", "can_send(", "set_safety_mode(",
    ):
        check(f"session manager does not perform {forbidden}", forbidden not in source)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
