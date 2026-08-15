#!/usr/bin/env python3
"""Generate the explicit UDS/security-state composition model.

Composes the firmware-proven state machines that jointly determine what an
external tester can do at any moment:

  - UDS diagnostic session (bootloader and application contexts, separate)
  - application SecurityAccess level 2 (send-key success bit)
  - proprietary BA persistent authorization (marker FEBE5F27 + countdown)
  - programming handoff / lifecycle phase (FEBEE81F)
  - CommunicationControl communication mode
  - XCP 0x7F7 connected state (no GET_SEED/UNLOCK in this image)
  - bootloader SA unlock byte FEBF2B0F

Each state variable lists: holder RAM byte, writers, readers, reset behavior,
and session/SA dependencies — all pinned by verified findings. The generator
emits a machine-readable composition table plus carries-out queries:

  - privilege carryover: which privileges survive a transition (session
    change, soft reset within a context, context handoff, hard reset)?
  - stale authorization: which state is checked but not re-derived?

The model is derived from curated constants (every one traceable to a
verified finding referenced in docs/status/FINDINGS.md). It is a composition
of firmware-static facts, not a dynamic claim.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_JSON = REPO / "data" / "generated" / "security_state_composition.json"
OUT_CSV = REPO / "data" / "generated" / "security_state_composition.csv"

# ---------------------------------------------------------------------------
# State variables. Provenance references canonical finding IDs.
# ---------------------------------------------------------------------------
STATES = [
    {
        "id": "boot_sa_unlock",
        "context": "bootloader",
        "holder": "FEBF2B0F",
        "type": "byte enum",
        "values": {"0/1": "locked/armed (session-change writes 1)", "2": "unlocked"},
        "writers": [
            {"addr": "0x5090", "action": "boot init writes 1", "provenance": "SEC-BOOT-007"},
            {"addr": "0x561E", "action": "session-change writes 1 (never 2)", "provenance": "SEC-BOOT-007"},
            {"addr": "0x54DC", "action": "SA send-key success writes 2", "provenance": "SEC-BOOT-007"},
        ],
        "readers": [
            {"addr": "0x5D68", "action": "RequestDownload gate ==2", "provenance": "SEC-BOOT-007"},
            {"addr": "0x4948", "action": "WDBI gate ==2", "provenance": "SEC-BOOT-007"},
            {"addr": "0x60C2", "action": "ECUReset gate ==2", "provenance": "SEC-BOOT-007"},
        ],
        "reset_behavior": "cleared to 1 at boot init; any session change downgrades 2->1",
        "attacker_writable_pre_auth": False,
    },
    {
        "id": "app_session",
        "context": "application",
        "holder": "Dcm session state (FEBE5D.. region)",
        "type": "enum 1/2/3",
        "values": {"1": "default", "2": "programming", "3": "extended"},
        "writers": [
            {"addr": "0x93FF6", "action": "subfunction 01", "provenance": "DIAG-APP-001"},
            {"addr": "0x94006", "action": "subfunction 02 (programming)", "provenance": "DIAG-APP-001"},
            {"addr": "0x94016", "action": "subfunction 03 (extended)", "provenance": "DIAG-APP-001"},
        ],
        "readers": [{"addr": "service objects", "action": "session allow-lists", "provenance": "DIAG-APP-001"}],
        "reset_behavior": "returns to default (1) on ECU reset",
        "attacker_writable_pre_auth": True,
    },
    {
        "id": "app_sa_level2",
        "context": "application",
        "holder": "Dcm security bitmask (bit 1)",
        "type": "bitmask",
        "values": {"0x02": "SecurityAccess level 2 active"},
        "writers": [
            {"addr": "0x8C82A", "action": "SA 27 04 send-key success (level 2)", "provenance": "SEC-APP-001"},
        ],
        "readers": [
            {"addr": "0x8FDCA->0x906F8", "action": "Dcm security mask reader", "provenance": "SEC-APP-007"},
        ],
        "reset_behavior": "cleared on ECU reset; NOT cleared on session change in this calibration (empty policy tables)",
        "attacker_writable_pre_auth": False,
    },
    {
        "id": "ba_persistent_auth",
        "context": "application",
        "holder": "FEBE5F27 (marker) + object 24 countdown + object 5 (0x105)",
        "type": "marker+countdown",
        "values": {"0x5A": "BA dispatch without fresh SA read", "other": "requires fresh SA2"},
        "writers": [
            {"addr": "0x34DAE chain", "action": "BA F7/BAENA success persists marker+count 30", "provenance": "SEC-APP-007"},
            {"addr": "0x347B0", "action": "restore helper reconstructs from NvM after reset", "provenance": "SEC-APP-007"},
            {"addr": "0x34FB6", "action": "countdown step decrements, clears on expiry", "provenance": "SEC-APP-007"},
            {"addr": "F6/BADIS", "action": "explicit clear", "provenance": "SEC-APP-007"},
        ],
        "readers": [
            {"addr": "0x348B4", "action": "BA dispatcher gate: marker==0x5A skips fresh SA read", "provenance": "SEC-APP-007"},
        ],
        "reset_behavior": "PERSISTS across reset via NvM objects 24/5 until 30 countdown steps",
        "attacker_writable_pre_auth": False,
        "carryover": "This is the one verified reset-persistent authorization: a legitimate SA2 enable remains effective after reset until the 30-invocation countdown expires.",
    },
    {
        "id": "programming_handoff",
        "context": "application->bootloader",
        "holder": "FEBEE81F (phase snapshot)",
        "type": "byte",
        "values": {"0x11": "handoff rejected", "other": "permitted"},
        "writers": [{"addr": "lifecycle phase machine", "action": "phase snapshot", "provenance": "DIAG-APP-003"}],
        "readers": [{"addr": "0x10 02 handler", "action": "handoff gate", "provenance": "DIAG-APP-003"}],
        "reset_behavior": "re-derived from lifecycle state after reset",
        "attacker_writable_pre_auth": False,
    },
    {
        "id": "communication_control",
        "context": "application",
        "holder": "communication-mode state",
        "type": "enum",
        "values": {"0": "enable", "1/2": "disable variants"},
        "writers": [{"addr": "0x95154", "action": "28 01/00 control request", "provenance": "SEC-APP-005"}],
        "readers": [{"addr": "Tx gating", "action": "suppresses communication", "provenance": "SEC-APP-005"}],
        "reset_behavior": "restored on reset; 28 00 01 restores unconditionally",
        "attacker_writable_pre_auth": True,
    },
    {
        "id": "xcp_connected",
        "context": "application (CAN 0x7F7)",
        "holder": "XCP connection state",
        "type": "bool",
        "values": {"connected": "memory commands permitted"},
        "writers": [{"addr": "0xFF CONNECT", "action": "sets connected; no GET_SEED/UNLOCK configured", "provenance": "COM-005"}],
        "readers": [{"addr": "0x97160 dispatcher", "action": "requires connection before commands", "provenance": "COM-005"}],
        "reset_behavior": "cleared on reset; no SA dependency exists in this image",
        "attacker_writable_pre_auth": True,
        "carryover": "No SA gating exists at any layer of the XCP family in this calibration.",
    },
]

# ---------------------------------------------------------------------------
# Transition queries: which privileges survive which transitions?
# ---------------------------------------------------------------------------
TRANSITIONS = [
    {
        "id": "app_session_change",
        "from": "application session S",
        "to": "application session S'",
        "privileges": [
            {"privilege": "app_sa_level2", "survives": True,
             "note": "session change does not clear the Dcm security mask in this calibration (empty policy tables, SEC-APP-004)"},
            {"privilege": "ba_persistent_auth", "survives": True,
             "note": "marker/countdown unaffected by session state (SEC-APP-007)"},
            {"privilege": "xcp_connected", "survives": True,
             "note": "XCP connection state is independent of UDS session (COM-005)"},
        ],
    },
    {
        "id": "app_soft_reset",
        "from": "application",
        "to": "application after ECUReset",
        "privileges": [
            {"privilege": "app_sa_level2", "survives": False, "note": "cleared on reset"},
            {"privilege": "ba_persistent_auth", "survives": True,
             "note": "restored from NvM objects 24/5; 30 countdown invocations remain (SEC-APP-007)"},
            {"privilege": "xcp_connected", "survives": False, "note": "cleared on reset"},
            {"privilege": "app_session", "survives": False, "note": "returns to default"},
        ],
    },
    {
        "id": "programming_handoff",
        "from": "application programming session",
        "to": "bootloader context",
        "privileges": [
            {"privilege": "app_sa_level2", "survives": False,
             "note": "bootloader has its own SA; the application Dcm mask is not consulted and FEBF2B0F boots at 1 (SEC-BOOT-007)"},
            {"privilege": "ba_persistent_auth", "survives": False,
             "note": "BA dispatcher exists only in application context; no bootloader reader recovered"},
            {"privilege": "xcp_connected", "survives": False, "note": "separate context"},
            {"privilege": "boot_sa_unlock", "survives": False,
             "note": "handoff is identity-unauthenticated but the bootloader SA byte starts locked; each context gates independently"},
        ],
    },
    {
        "id": "boot_session_change",
        "from": "bootloader session S",
        "to": "bootloader session S'",
        "privileges": [
            {"privilege": "boot_sa_unlock", "survives": False,
             "note": "session-change handler 0x561E writes 1, downgrading an existing unlock (SEC-BOOT-007)"},
        ],
    },
]

QUERY_RESULTS = [
    {
        "query": "privilege carryover across reset",
        "result": "Exactly one verified reset-persistent authorization exists: BA persistent auth "
                  "(SEC-APP-007). Application SA level 2, XCP connection, sessions, and bootloader SA "
                  "are all reset-cleared or independently re-gated.",
        "grade": "verified (composition of verified findings)",
    },
    {
        "query": "stale authorization (checked but not re-derived)",
        "result": "BA dispatcher 0x348B4 skips the fresh SA2 read while marker FEBE5F27==0x5A. This is "
                  "the one stale-authorization window; it is bounded by the 30-invocation countdown and "
                  "requires a prior legitimate SA2 enable (SEC-APP-007).",
        "grade": "verified",
    },
    {
        "query": "cross-context state confusion (application vs bootloader)",
        "result": "No shared privilege byte exists between contexts: application SA lives in the Dcm "
                  "mask, bootloader SA in FEBF2B0F; each is written/cleared independently and the "
                  "programming handoff performs no SA transfer (SEC-BOOT-007, DIAG-APP-003). Residue "
                  "disclosure across handoff (FEBF2D08..) is a separate confidentiality question "
                  "(SEC-APP-006), not an authorization transfer.",
        "grade": "verified negative (authorization); bounded (residue value)",
    },
    {
        "query": "XCP privilege composition",
        "result": "The XCP family composes only its own connected flag: no SA level, session, or BA "
                  "state gates any XCP memory command (COM-005). Its memory primitives are "
                  "pre-SA by construction.",
        "grade": "verified",
    },
]


def main() -> int:
    payload = {
        "schema": "security-state-composition/1",
        "scope": "Sienna EPS 8965B4512000",
        "evidence_source": "firmware-static (composed from verified findings)",
        "states": STATES,
        "transitions": TRANSITIONS,
        "queries": QUERY_RESULTS,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    with OUT_CSV.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([
            "state_id", "context", "holder", "type", "attacker_writable_pre_auth",
            "reset_behavior", "writers", "readers", "carryover_note",
        ])
        for state in STATES:
            writer.writerow([
                state["id"], state["context"], state["holder"], state["type"],
                state.get("attacker_writable_pre_auth", ""),
                state["reset_behavior"],
                "; ".join(f"{w['addr']} {w['action']} [{w['provenance']}]" for w in state["writers"]),
                "; ".join(f"{r['addr']} {r['action']} [{r['provenance']}]" for r in state["readers"]),
                state.get("carryover", ""),
            ])
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
