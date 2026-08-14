#!/usr/bin/env python3
"""Generate the application UDS service map as CSV.

Raw-table facts (record fields, session allow-lists, subfunction rows, DID /
write-DID / routine-ID tables) are derived only from the committed CodeFlash
image. Semantic columns are explicit, auditable literals tied to recovered
handlers; they are not inferred OEM names.
"""
from __future__ import annotations

import argparse
import csv
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

SERVICE_TABLE = 0x25E28
SERVICE_COUNT = 17
# callback, security-list ptr, session-list ptr, subfunction-table ptr,
# SID, has-subfunction-table, security-count, session-count, subfunction-count.
SERVICE = struct.Struct("<IIIIBBBBB3x")
SUBFN = struct.Struct("<IIIHH")
DID = struct.Struct("<HHIII")
ROUTINE_CONTROL = struct.Struct("<HBBI")
ROUTINE = struct.Struct("<HHII")

DID_TABLE = 0x2941C
DID_COUNT = 0xF2
ROUTINE_CONTROL_TABLE = 0x26AEC
ROUTINE_CONTROL_COUNT = 0x13
ROUTINE_TABLE = 0x25768
ROUTINE_COUNT = 32
SA_SLOT0 = 0x26338
SA_SLOT_SIZE = 0x18

STANDARD_NAMES = {
    0x10: "DiagnosticSessionControl",
    0x11: "ECUReset",
    0x14: "ClearDiagnosticInformation",
    0x19: "ReadDTCInformation",
    0x22: "ReadDataByIdentifier",
    0x23: "ReadMemoryByAddress",
    0x27: "SecurityAccess",
    0x28: "CommunicationControl",
    0x2E: "WriteDataByIdentifier",
    0x31: "RoutineControl",
    0x34: "RequestDownload",
    0x36: "TransferData",
    0x37: "RequestTransferExit",
    0x3E: "TesterPresent",
    0x85: "ControlDTCSetting",
    0xAB: "proprietary_0xAB",
    0xBA: "proprietary_0xBA",
}

# Evidence-bounded semantic overlay keyed by SID. Raw fields always win when
# they disagree; these strings only document recovered behavior.
SEMANTICS = {
    0x10: {
        "service_callback_role": "subfunction_table_only",
        "async_worker": "0x8A244 application_session_transition_async_worker (programming)",
        "security_policy": "none at service or subfunction level",
        "nrcs": "0x13 length; 0x7E via session allow-list; 0x88 speed; 0x22 handoff; 0x78 pending",
        "side_effects": "session transition; programming queues event 9 / mode 0x900 reset",
        "config_tables": "subfn 0x25BC0; runtime 0x262F6; speed/supply 0x181DC/0x181DE",
        "evidence_status": "recovered",
        "notes": "See existing session/handoff analysis in docs/diagnostics/application.md",
    },
    0x11: {
        "service_callback_role": "null direct callback; generic positive-response path",
        "async_worker": "",
        "security_policy": "none at service level; programming session only",
        "nrcs": "generic session rejection outside programming",
        "side_effects": "no service-specific callback recovered from runtime object",
        "config_tables": "session allow [2] only",
        "evidence_status": "verified null-direct service",
        "notes": "The prior 0x8B1F0 ECUReset attribution was an 8-byte service-object parsing error; 0x8B1F0 belongs to SID 0x14.",
    },
    0x14: {
        "service_callback_role": "direct callback 0x8B1F0; phase 0 starts 0x8B144",
        "async_worker": "0x8AF28/0x8B014 lower clear stages; nonzero callback phase finalizes via 0x8B1D4",
        "security_policy": "none at service level; sessions [1,3]",
        "nrcs": "0x13 wrong length; 0x22/0x31/0x72 from lower-stage mapper",
        "side_effects": "requires and packs the three-byte groupOfDTC, then executes the configured clear operation",
        "config_tables": "runtime service object 0x25E58",
        "evidence_status": "recovered",
        "notes": "Request shape is ClearDiagnosticInformation, not ECUReset.",
    },
    0x19: {
        "service_callback_role": "subfunction_table_only",
        "async_worker": "subfn workers 0x8B532/0x8B99A/0x8BD30/0x8C276; pending returns 10",
        "security_policy": "none at service level; subfn sessions [1,3]",
        "nrcs": "0x13 length; report-specific worker failures",
        "side_effects": "read/report operations only in recovered subfunction graph",
        "config_tables": "subfn table 0x25BF0 (01..04)",
        "evidence_status": "recovered",
        "notes": "The prior 0x945DC service-level attribution was shifted; 0x945DC is SID 0x22 RDBI.",
    },
    0x22: {
        "service_callback_role": "direct callback 0x945DC; phase 0=0x944C6, phase 2=0x9452E",
        "async_worker": "0x94426/0x9429E drive generic configured DID-record reads through 0x92810/0x929B0",
        "security_policy": "per-DID/session/security through generic DID capability and record policy",
        "nrcs": "0x13 request shape; 0x31 DID/policy; 0x14 responseTooLong; pending supported",
        "side_effects": "reads through the 242-row DID table; disclosure and side-effect boundaries verified separately",
        "config_tables": f"DID table 0x{DID_TABLE:X} count {DID_COUNT} (getter 0x4F928)",
        "evidence_status": "recovered",
        "notes": "Runtime object 0x25E88 and secondary object 0x26008 both bind SID 0x22 to 0x945DC.",
    },
    0x23: {
        "service_callback_role": "direct callback 0x948AA; phases 0/2/3 start/cancel/poll through 0x9479A/0x9486C/0x946FA",
        "async_worker": "0x9479A parses addressAndLengthFormatIdentifier; 0x8C456/0x4EB1C execute configured memory reads",
        "security_policy": "extended-session outer gate plus configured memory-range/session/security checks via 0x92ECC/0x92FAE/0x92FEE",
        "nrcs": "0x13 malformed length; 0x31 unsupported range/format; 0x33 security",
        "side_effects": "bounded configured memory read",
        "config_tables": "generic memory-range policy rooted through PTR_PTR_00026208",
        "evidence_status": "recovered",
        "notes": "The prior simple-response/RDBI attribution was caused by the 8-byte-shifted service parser.",
    },
    0x27: {
        "service_callback_role": "subfunction_table_only",
        "async_worker": (
            "0x9497C request-seed / 0x94A72 send-key; pending 10 supported. "
            "Level 1 (01/02, programming) uses stubs at 0x94E0E/0x94E22 that always "
            "return 1 (non-functional). Level 2 (03/04, extended) uses actual "
            "implementations: seed via 0x94E12->0x8C734, key via 0x94E26->0x8C82A."
        ),
        "security_policy": (
            "levels 1 and 2; subfn sessions 1/2 require programming, 3/4 extended. "
            "Level 1 is a compiled-out stub; only level 2 is functional."
        ),
        "nrcs": "0x13 length; 0x24 sequence; 0x35 invalidKey; 0x36 attempts; 0x37 delay",
        "side_effects": (
            "successful send-key calls unlock helper 0x900FC->0x9075A which sets "
            "bit (level-1) in 2-dword bitmask. Seed stored at FEBF495A (16 bytes), "
            "provisioned flag FEBF4958 (0x5A). Key derived via AES/CMAC using "
            "CodeFlash secret at 0x20840."
        ),
        "config_tables": (
            f"subfn 0x25C30; slots @0x{SA_SLOT0:X}/0x{SA_SLOT0+SA_SLOT_SIZE:X} "
            "seed/key len 0x10, levels 1/2; key material @0x20840"
        ),
        "evidence_status": "recovered",
        "notes": (
            "Application SA algorithm: level 2 seed generated via crypto hardware "
            "(0x8C65A) and stored at FEBF495A; expected key = AES/CMAC transform of "
            "stored seed under 16-byte secret at 0x20840. Attempt counter is per-level "
            "RAM-only (not NvM-persisted). Independent of bootloader SEED_KEY_SECRET."
        ),
    },
    0x28: {
        "service_callback_role": "subfunction_table_only; wrappers 0x9542C/0x9543C/0x9544C",
        "async_worker": "0x95306 -> 0x95154 shared CommunicationControl request worker",
        "security_policy": "none at service level; subfunctions allowed in extended session",
        "nrcs": "0x13 length; 0x31 unsupported control",
        "side_effects": "configured communication-mode updates through 0x94F8E/0x9505C",
        "config_tables": "subfn 0x25C70 (00/01/03); mode bytes at tp+0x249B",
        "evidence_status": "recovered",
        "notes": "0x93C62 is not CommunicationControl; it is the direct SID 0x2E WDBI callback.",
    },
    0x2E: {
        "service_callback_role": "direct callback 0x93C62; phase 0=0x93B56, phase 2=0x93BDE",
        "async_worker": "generic write-record operations via 0x93AF2/0x93A1E/0x9395E -> 0x92A70",
        "security_policy": "generic DID write capability/session/security policy; not the 19-entry 0x26AEC table",
        "nrcs": "0x13 length; 0x31 DID/write capability; 0x33 security; configured worker NRC",
        "side_effects": "writes only DIDs carrying configured write capability in the generic DID model",
        "config_tables": f"generic DID table 0x{DID_TABLE:X} count {DID_COUNT}; record-operation tables near 0x26210",
        "evidence_status": "recovered",
        "notes": "The prior 19-entry WDBI surface was actually RoutineControl RID configuration.",
    },
    0x31: {
        "service_callback_role": "direct callback 0x95DCE; phases 0/2/3 start/cancel/poll via 0x95C8C/0x95D7E/0x95DB4",
        "async_worker": "0x95B0C configured RoutineControl worker; 19-RID surface at 0x26AEC",
        "security_policy": "19 RID records have their own policy/session configuration; service outer sessions are 1/2/3",
        "nrcs": "0x13 length; 0x12 unsupported controlType; 0x31 RID; 0x33 policy/security",
        "side_effects": "configured RID actions include crypto-test bank activation, key update, lifecycle reinitialization, and service-mode controls",
        "config_tables": f"RoutineControl RID table 0x{ROUTINE_CONTROL_TABLE:X} count {ROUTINE_CONTROL_COUNT}; callback table 0x25804",
        "evidence_status": "recovered",
        "notes": "Request shape is controlType + 16-bit RID. The separate 0x25768 callback table is a distinct dormant/internal routine subsystem.",
    },
    0x34: {
        "service_callback_role": "null in service table; simple-response path (byte[9]==0)",
        "async_worker": "",
        "security_policy": "none at service level (b10=0)",
        "nrcs": "shared gate NRC 0x7F outside programming",
        "side_effects": "none; simple positive response (SID|0x40 + request echo) via 0x8F6FA",
        "config_tables": "session allow [2] only",
        "evidence_status": "resolved; simple-response-only",
        "notes": (
            "DSP dispatch resolved: start-phase DSP globally disabled (flag @0x25DCC=0), "
            "byte[9]==0 selects simple-response path. Unlike bootloader RequestDownload "
            "at 0x5D68; no download-range table or transfer state machine."
        ),
    },
    0x36: {
        "service_callback_role": "null in service table; simple-response path (byte[9]==0)",
        "async_worker": "",
        "security_policy": "none at service level (b10=0)",
        "nrcs": "shared gate NRC 0x7F outside programming",
        "side_effects": "none; simple positive response (SID|0x40 + request echo) via 0x8F6FA",
        "config_tables": "session allow [2] only",
        "evidence_status": "resolved; simple-response-only",
        "notes": (
            "DSP dispatch resolved: start-phase DSP globally disabled (flag @0x25DCC=0), "
            "byte[9]==0 selects simple-response path. No transfer state machine."
        ),
    },
    0x37: {
        "service_callback_role": "null in service table; simple-response path (byte[9]==0)",
        "async_worker": "",
        "security_policy": "none at service level (b10=0)",
        "nrcs": "shared gate NRC 0x7F outside programming",
        "side_effects": "none; simple positive response (SID|0x40 + request echo) via 0x8F6FA",
        "config_tables": "session allow [2] only",
        "evidence_status": "resolved; simple-response-only",
        "notes": (
            "DSP dispatch resolved: start-phase DSP globally disabled (flag @0x25DCC=0), "
            "byte[9]==0 selects simple-response path. No transfer-exit handler."
        ),
    },
    0x3E: {
        "service_callback_role": "subfunction_table_only; row callback 0x93CFE",
        "async_worker": "none; phase-2 path only clears busy via 0x93CF0",
        "security_policy": "none; subfn 0 allowed in sessions 1/2/3",
        "nrcs": "0x13 when request data length nonzero",
        "side_effects": "positive acknowledgment only; no service-local S3 timer",
        "config_tables": "subfn 0x25CA0 (00)",
        "evidence_status": "recovered",
        "notes": "Mirrors bootloader acknowledge-only TesterPresent shape",
    },
    0x85: {
        "service_callback_role": "subfunction_table_only",
        "async_worker": "none beyond 0x8CC7C length check / state store",
        "security_policy": "none; subfn sessions [3]",
        "nrcs": "0x13 when request data length nonzero",
        "side_effects": (
            "absolute mov 0xFEBF45A8 then st.b setting at [r1]; also mirrors 0x1C-byte "
            "request context to FEBF45A8+0xC via movea 0xC,r1"
        ),
        "config_tables": "subfn 0x25CB0 (01/02)",
        "evidence_status": "recovered",
        "notes": "on/off style settings 1 and 2; not bootloader acknowledge-only 85 02",
    },
    0xAB: {
        "service_callback_role": "subfunction_table_only; wrappers 0x96A34/0x96A56/0x96A78",
        "async_worker": "0x96918 shared event-record query worker; pending path posts event 0x16",
        "security_policy": "none at service level; subfn sessions [1,3]",
        "nrcs": "0x13 length; vendor byte from worker",
        "side_effects": "lists checkpoint-backed active event IDs and reads per-ID state/detail",
        "config_tables": "subfn 0x25CD0 (01/02/03); event catalogue 0x2AD10; snapshot/detail descriptors",
        "evidence_status": "recovered",
        "notes": "SID 0xAB does not own callback 0x8D344; 0x8D344 belongs to SID 0xBA.",
    },
    0xBA: {
        "service_callback_role": "direct callback 0x8D344; phase 0 mirrors request context then enters 0x8D2B2",
        "async_worker": "0x8D2B2/0x8D32E operation-F1 state machine",
        "security_policy": "none at service level; extended session only",
        "nrcs": "worker-defined; OEM semantics not yet assigned",
        "side_effects": "asynchronous proprietary operation; exact OEM purpose remains open",
        "config_tables": "runtime service object 0x25FA8",
        "evidence_status": "structurally recovered; semantics open",
        "notes": "Previously mislabeled as SID 0xAB event-record callback by the shifted service parser.",
    },
}


def u32(offset: int) -> int:
    return struct.unpack_from("<I", CF, offset)[0]


def parse_subfunctions(table: int, count: int) -> list[dict[str, int | str]]:
    rows = []
    for i in range(count):
        cb, _zero, allow_ptr, subfn, allow_count = SUBFN.unpack_from(CF, table + i * SUBFN.size)
        allow = list(CF[allow_ptr : allow_ptr + allow_count])
        rows.append(
            {
                "subfunction": subfn,
                "callback": cb,
                "session_allow_ptr": allow_ptr,
                "session_allow": ",".join(str(x) for x in allow),
            }
        )
    return rows


def format_subfunctions(rows: list[dict[str, int | str]]) -> str:
    parts = []
    for row in rows:
        parts.append(
            f"{int(row['subfunction']):02X}@0x{int(row['callback']):X}"
            f"[sessions {row['session_allow']}]"
        )
    return "; ".join(parts)


def build_rows() -> list[dict[str, str]]:
    # Sanity: DID / configured RoutineControl / separate internal routine tables parse cleanly.
    dids = [DID.unpack_from(CF, DID_TABLE + i * DID.size) for i in range(DID_COUNT)]
    if dids[0][0] != 0x0100 or dids[-1][0] != 0xF18C:
        raise SystemExit("DID table bounds mismatch")
    control_rids = [
        ROUTINE_CONTROL.unpack_from(CF, ROUTINE_CONTROL_TABLE + i * ROUTINE_CONTROL.size)
        for i in range(ROUTINE_CONTROL_COUNT)
    ]
    if control_rids[0][0] != 0x1000 or control_rids[-1][0] != 0x110D:
        raise SystemExit("RoutineControl RID table bounds mismatch")
    routines = [
        ROUTINE.unpack_from(CF, ROUTINE_TABLE + i * ROUTINE.size) for i in range(ROUTINE_COUNT)
    ]
    if routines[0][0] != 0x0204 or routines[-1][0] != 0x110D:
        raise SystemExit("routine-ID table bounds mismatch")

    rows: list[dict[str, str]] = []
    for index in range(SERVICE_COUNT):
        offset = SERVICE_TABLE + index * SERVICE.size
        callback, security_ptr, session_ptr, subfn_ptr, sid, has_subfn, sec_count, session_count, subfn_count = (
            SERVICE.unpack_from(CF, offset)
        )
        sessions = list(CF[session_ptr : session_ptr + session_count])
        sub_rows: list[dict[str, int | str]] = []
        if has_subfn and subfn_ptr and subfn_count:
            sub_rows = parse_subfunctions(subfn_ptr, subfn_count)
        sem = SEMANTICS[sid]
        rows.append(
            {
                "table_index": str(index),
                "record_addr": f"0x{offset:X}",
                "sid": f"0x{sid:02X}",
                "sid_name": STANDARD_NAMES[sid],
                "session_allow_ptr": f"0x{session_ptr:X}",
                "session_allow_list": ",".join(str(x) for x in sessions),
                "session_allow_count": str(session_count),
                "security_allow_count": str(sec_count),
                "has_subfunction_table": str(has_subfn),
                "subfunction_table_ptr": f"0x{subfn_ptr:X}" if subfn_ptr else "",
                "subfunction_count": str(subfn_count),
                "subfunctions": format_subfunctions(sub_rows),
                "service_callback": f"0x{callback:X}" if callback else "",
                "service_callback_role": sem["service_callback_role"],
                "async_worker": sem["async_worker"],
                "security_policy": sem["security_policy"],
                "nrcs": sem["nrcs"],
                "side_effects": sem["side_effects"],
                "config_tables": sem["config_tables"],
                "security_allow_ptr": f"0x{security_ptr:X}" if security_ptr else "",
                "evidence_status": sem["evidence_status"],
                "notes": sem["notes"],
                "did_table_addr": f"0x{DID_TABLE:X}" if sid in (0x22,) else "",
                "did_table_count": str(DID_COUNT) if sid in (0x22,) else "",
                "routine_control_table_addr": f"0x{ROUTINE_CONTROL_TABLE:X}" if sid == 0x31 else "",
                "routine_control_table_count": str(ROUTINE_CONTROL_COUNT) if sid == 0x31 else "",
                "internal_routine_table_addr": f"0x{ROUTINE_TABLE:X}" if sid == 0x31 else "",
                "internal_routine_table_count": str(ROUTINE_COUNT) if sid == 0x31 else "",
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=REPO / "data" / "application_diagnostic_map.csv",
    )
    args = parser.parse_args()
    rows = build_rows()
    fieldnames = list(rows[0].keys())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} service rows to {args.output}")


if __name__ == "__main__":
    main()
