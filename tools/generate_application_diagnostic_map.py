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

SERVICE_TABLE = 0x25E30
SERVICE_COUNT = 17
SERVICE = struct.Struct("<IIBBBBIII")
SUBFN = struct.Struct("<IIIHH")
DID = struct.Struct("<HHIII")
WRITE_DID = struct.Struct("<HBBI")
ROUTINE = struct.Struct("<HHII")

DID_TABLE = 0x2941C
DID_COUNT = 0xF2
WRITE_DID_TABLE = 0x26AEC
WRITE_DID_COUNT = 0x13
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
        "notes": "See existing session/handoff analysis in APPLICATION_DIAGNOSTICS.md",
    },
    0x11: {
        "service_callback_role": "phase_dispatcher 0=start 0x8B144; nonzero=cancel/finalize 0x8B1D4",
        "async_worker": "0x8AF28/0x8B014 lower reset stages via stub ops 0x18000000/0x18000001",
        "security_policy": "none at service level (b10=0)",
        "nrcs": "0x13 wrong length; 0x22/0x31/0x72 from lower-stage mapper",
        "side_effects": "packs 3 request bytes; queues lower reset ops; pending value 10",
        "config_tables": "none beyond service record; session allow [2]",
        "evidence_status": "recovered",
        "notes": "Requires request length 3; not bootloader hardReset-only shape",
    },
    0x14: {
        "service_callback_role": "null in service table; simple-response path (byte[9]==0)",
        "async_worker": "",
        "security_policy": "none at service level (b10=0)",
        "nrcs": "generic session NRC 0x7F via dispatcher when session not allowed",
        "side_effects": "none; simple positive response (SID|0x40 + request echo) via 0x8F6FA",
        "config_tables": "session allow [1,3] only in service record",
        "evidence_status": "resolved; simple-response-only",
        "notes": (
            "DSP dispatch resolved: start-phase DSP globally disabled (flag @0x25DCC=0), "
            "byte[9]==0 selects simple-response path. Service echoes SID|0x40 + request "
            "without service-specific processing. No hidden DSP handler."
        ),
    },
    0x19: {
        "service_callback_role": "phase_dispatcher 0=start 0x944C6; 2=complete 0x9452E",
        "async_worker": "subfn workers 0x8B532/0x8B99A/0x8BD30/0x8C276; pending returns 10",
        "security_policy": "none at service level; subfn sessions [1,3]",
        "nrcs": "0x13 length; 0x14 responseTooLong; internal 0x21 mapped via 0x93910",
        "side_effects": (
            "request-context mirrors via absolute mov: "
            "FEBF3BFC/3F24/4248/457C (subfn 01..04); structure opaque"
        ),
        "config_tables": "subfn table 0x25BF0 (01..04)",
        "evidence_status": "recovered",
        "notes": "Subfunctions 01..04 are report-style DTC readers; OEM report names not assigned",
    },
    0x22: {
        "service_callback_role": "phase_dispatcher 0=start 0x9479A; 2=cancel 0x9486C; 3=poll 0x946FA",
        "async_worker": "0x946FA poll may return pending 10 / NRC 0x78 path",
        "security_policy": "per-DID via 0x92FEE against session security state from 0x8FDCA",
        "nrcs": "0x13 length; 0x31 did; 0x33 security; 0x78 pending",
        "side_effects": "reads through DID table callbacks; per-DID storage not enumerated here",
        "config_tables": f"DID table 0x{DID_TABLE:X} count {DID_COUNT} (getter 0x4F928)",
        "evidence_status": "recovered",
        "notes": "242 DID records; F181/F186/F18C previously documented",
    },
    0x23: {
        "service_callback_role": "null in service table; simple-response path (byte[9]==0)",
        "async_worker": "",
        "security_policy": "none at service level (b10=0)",
        "nrcs": "generic session NRC 0x7F when not in extended",
        "side_effects": "none; simple positive response (SID|0x40 + request echo) via 0x8F6FA",
        "config_tables": "session allow [3] only",
        "evidence_status": "resolved; simple-response-only",
        "notes": (
            "DSP dispatch resolved: start-phase DSP globally disabled (flag @0x25DCC=0), "
            "byte[9]==0 selects simple-response path. No memory-range table or read handler."
        ),
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
        "service_callback_role": "phase_dispatcher 0=start 0x93B56; 2=complete 0x93BDE",
        "async_worker": "subfn wrappers -> 0x95154; may post events 0x11/0x12/0x13",
        "security_policy": "none at service level; subfn sessions [3]",
        "nrcs": "0x13 length; 0x31 out-of-range control",
        "side_effects": "0x95154 jarls helpers 0x94F8E/0x9505C (mode apply); no typed RAM root claimed",
        "config_tables": "subfn 0x25C70 (00/01/03); mode bytes at tp+0x249B",
        "evidence_status": "recovered",
        "notes": "Subfunctions 0/1/3 only; not the bootloader acknowledge-only 28 01 01",
    },
    0x2E: {
        "service_callback_role": "phase_dispatcher 0=start 0x95C8C; 2=cancel 0x95D7E; 3=poll 0x95DB4",
        "async_worker": "0x95B0C write worker; pending path posts event 6",
        "security_policy": "per-DID via 0x95556/0x955DC; NRC 0x33 when locked",
        "nrcs": "0x13 length; 0x12 subfn/did shape; 0x31 did; 0x33 security",
        "side_effects": "dispatches through write-DID table callbacks; per-DID RAM/NvM not enumerated here",
        "config_tables": f"write-DID table 0x{WRITE_DID_TABLE:X} count {WRITE_DID_COUNT}",
        "evidence_status": "recovered",
        "notes": "Write set is a 19-entry subset (1000..110D class), not the full 242-DID read table",
    },
    0x31: {
        "service_callback_role": "null in service table; simple-response path (byte[9]==0)",
        "async_worker": "",
        "security_policy": "none at service level (b10=0)",
        "nrcs": "shared gate NRC 0x7F when session not allowed",
        "side_effects": "none from SID dispatch; RID table consumed only by 0xAB callback 0x8D3CC",
        "config_tables": f"routine-ID table 0x{ROUTINE_TABLE:X} count {ROUTINE_COUNT}",
        "evidence_status": "resolved; simple-response-only (RID table for AB consumer)",
        "notes": (
            "DSP dispatch resolved: start-phase DSP globally disabled (flag @0x25DCC=0), "
            "byte[9]==0 selects simple-response path. SID 0x31 also excluded from subfn "
            "path by gate check (SID==0x31=ASCII '1'). The 32-entry RID table at 0x25768 "
            "is consumed only by the 0xAB callback (0x8D3CC scans entries 0..12). SID 0x31 "
            "itself echoes SID|0x40 without dispatching routines."
        ),
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
        "service_callback_role": (
            "phase_dispatcher 0x8D344 copies request then 0x8D2B2; "
            "subfn wrappers 0x96A34/0x96A56/0x96A78"
        ),
        "async_worker": "0x96918/0x968A6; pending 10 posts event 0x16",
        "security_policy": "none at service level; subfn sessions [1,3]",
        "nrcs": "0x13 length; 0x31 lookup miss; vendor byte from worker",
        "side_effects": (
            "absolute mov 0xFEBF48EC; primary mirror at FEBF48EC; secondary at "
            "FEBF493C via st.w 0x50[r1]; may invoke routine-ID entries 0..12"
        ),
        "config_tables": "subfn 0x25CD0 (01/02/03); routine-ID table head used by 0x8D3CC",
        "evidence_status": "structural-recovered",
        "notes": "Proprietary; no OEM service name assigned. Secondary record uses data ptrs 0x26104/0x26110",
    },
    0xBA: {
        "service_callback_role": "null in service table; simple-response path (byte[9]==0)",
        "async_worker": "",
        "security_policy": "none at service level (b10=0)",
        "nrcs": "shared gate NRC 0x7F outside extended",
        "side_effects": "none; simple positive response (SID|0x40 + request echo) via 0x8F6FA",
        "config_tables": "session allow [3] only",
        "evidence_status": "resolved; simple-response-only",
        "notes": (
            "DSP dispatch resolved: start-phase DSP globally disabled (flag @0x25DCC=0), "
            "byte[9]==0 selects simple-response path. No OEM service handler; "
            "service echoes positive response without service-specific processing."
        ),
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
    # Sanity: DID/write/routine tables parse cleanly.
    dids = [DID.unpack_from(CF, DID_TABLE + i * DID.size) for i in range(DID_COUNT)]
    if dids[0][0] != 0x0100 or dids[-1][0] != 0xF18C:
        raise SystemExit("DID table bounds mismatch")
    write_dids = [
        WRITE_DID.unpack_from(CF, WRITE_DID_TABLE + i * WRITE_DID.size)
        for i in range(WRITE_DID_COUNT)
    ]
    if write_dids[0][0] != 0x1000 or write_dids[-1][0] != 0x110D:
        raise SystemExit("write-DID table bounds mismatch")
    routines = [
        ROUTINE.unpack_from(CF, ROUTINE_TABLE + i * ROUTINE.size) for i in range(ROUTINE_COUNT)
    ]
    if routines[0][0] != 0x0204 or routines[-1][0] != 0x110D:
        raise SystemExit("routine-ID table bounds mismatch")

    rows: list[dict[str, str]] = []
    for index in range(SERVICE_COUNT):
        offset = SERVICE_TABLE + index * SERVICE.size
        session_ptr, subfn_ptr, sid, has_subfn, sec_count, session_count, subfn_count, callback, word4 = (
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
                "trailing_word": f"0x{word4:X}",
                "evidence_status": sem["evidence_status"],
                "notes": sem["notes"],
                "did_table_addr": f"0x{DID_TABLE:X}" if sid in (0x22,) else "",
                "did_table_count": str(DID_COUNT) if sid in (0x22,) else "",
                "write_did_table_addr": f"0x{WRITE_DID_TABLE:X}" if sid in (0x2E,) else "",
                "write_did_table_count": str(WRITE_DID_COUNT) if sid in (0x2E,) else "",
                "routine_table_addr": f"0x{ROUTINE_TABLE:X}" if sid in (0x31, 0xAB) else "",
                "routine_table_count": str(ROUTINE_COUNT) if sid in (0x31, 0xAB) else "",
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
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} service rows to {args.output}")


if __name__ == "__main__":
    main()
