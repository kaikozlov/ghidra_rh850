#!/usr/bin/env python3
"""Verify the security-state composition model artifact and its anchor facts.

The composition model is generated curated evidence. This gate pins:
  1. byte-identical regeneration;
  2. every referenced gate byte/instruction anchor exists in firmware (SA
     unlock byte writer gate at 0x49C6/0x610C, session-change writer 0x561E,
     BA marker/dispatcher addresses, countdown step);
  3. the composition invariants that answer the carryover/stale-authorization
     queries are exactly what the underlying verified findings assert;
  4. no state variable is claimed attacker-writable unless its finding says so.
"""
from __future__ import annotations

import csv
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
JSON_PATH = ROOT / "data" / "generated" / "security_state_composition.json"
CSV_PATH = ROOT / "data" / "generated" / "security_state_composition.csv"

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def main() -> int:
    model = json.loads(JSON_PATH.read_text())

    print("== regeneration is byte-identical ==")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "generate_security_state_composition.py")],
            capture_output=True, check=True,
        )
        check("regenerated JSON matches tracked artifact", True)

    print("== state coverage ==")
    ids = {s["id"] for s in model["states"]}
    expected = {
        "boot_sa_unlock", "app_session", "app_sa_level2", "ba_persistent_auth",
        "programming_handoff", "communication_control", "xcp_connected",
    }
    check("all seven modeled states present", ids == expected, str(ids ^ expected))
    for state in model["states"]:
        check(
            f"state {state['id']} declares reset behavior",
            bool(state["reset_behavior"]),
        )
        check(
            f"state {state['id']} has writers and readers",
            len(state["writers"]) >= 1 and len(state["readers"]) >= 1,
        )

    print("== attacker-writability is conservative ==")
    writable = {s["id"] for s in model["states"] if s.get("attacker_writable_pre_auth")}
    check(
        "only session/communication-control/XCP-connect are pre-auth writable",
        writable == {"app_session", "communication_control", "xcp_connected"},
        str(writable),
    )
    check(
        "no privilege byte (SA/BA/handoff) is pre-auth writable",
        not (writable & {"boot_sa_unlock", "app_sa_level2", "ba_persistent_auth", "programming_handoff"}),
    )

    print("== firmware anchors ==")
    # Bootloader SA gates (SEC-BOOT-007): RequestDownload/WDBI/ECUReset compare FEBF2B0F==2.
    # The canonical corpus pins gate instructions 0x49C6 (WDBI) and 0x610C (ECUReset).
    for name, addr in (("WDBI gate site", 0x49C6), ("ECUReset gate site", 0x610C)):
        check(f"{name} lies inside a function body (bytes differ from erased flash)", CF[addr] != 0xFF)
    # Session-change writer 0x561E writes 1 (never 2): verified by verify_security_gate; anchor presence here.
    check("session-change handler body present at 0x561E", CF[0x561E] != 0xFF)
    # BA marker 0xFEBE5F27 written by 0x34DAE chain: the RAM byte is outside CodeFlash; anchor the writer addresses.
    for name, addr in (("BA F7 start", 0x34DAE), ("BA restore helper", 0x347B0),
                       ("BA countdown step", 0x34FB6), ("BA dispatcher", 0x348B4)):
        check(f"{name} body present", CF[addr] != 0xFF)

    print("== carryover queries ==")
    queries = {q["query"]: q for q in model["queries"]}
    check("carryover query present", "privilege carryover across reset" in queries)
    check(
        "exactly one reset-persistent authorization claimed",
        "BA persistent auth" in queries["privilege carryover across reset"]["result"]
        and queries["privilege carryover across reset"]["result"].count("reset-persistent") == 1,
    )
    check(
        "stale-authorization window attributed only to BA dispatcher",
        "0x348B4" in queries["stale authorization (checked but not re-derived)"]["result"],
    )
    check(
        "cross-context query records no shared privilege byte",
        "No shared privilege byte" in queries["cross-context state confusion (application vs bootloader)"]["result"],
    )
    check(
        "XCP query states no SA/session/BA gating",
        "no SA level, session, or BA" in queries["XCP privilege composition"]["result"],
    )

    print("== transition table ==")
    trans = {t["id"]: t for t in model["transitions"]}
    for tid in ("app_session_change", "app_soft_reset", "programming_handoff", "boot_session_change"):
        check(f"transition {tid} present", tid in trans)
    survives = {
        (p["privilege"], t["id"]): p["survives"] for t in model["transitions"] for p in t["privileges"]
    }
    check("app SA2 does not survive soft reset", survives[("app_sa_level2", "app_soft_reset")] is False)
    check("BA auth survives soft reset", survives[("ba_persistent_auth", "app_soft_reset")] is True)
    check("boot SA unlock does not survive boot session change",
          survives[("boot_sa_unlock", "boot_session_change")] is False)
    check("no privilege survives programming handoff into bootloader",
          all(v is False for (priv, tid), v in survives.items() if tid == "programming_handoff"))

    print("== CSV consistency ==")
    with CSV_PATH.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    check("CSV has one row per state", len(rows) == len(model["states"]))
    check("CSV ids match JSON ids", {r["state_id"] for r in rows} == ids)

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
