#!/usr/bin/env python3
"""Extract the current-GTS+ Phase-5 live Data-ID transport used by FRC_P5 cruise oracles."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "REFERENCE/gtsplus.7z"
MEMBER = "gtsplus/Toyota Diagnostics/GTSPlus/bin/DataListIF.dll"
SEMANTICS = REPO / "data/generated/techstream_v18/tss3_cruise_engagement_semantics.json"
P5 = REPO / "data/generated/techstream_v18/p5_lateral_control_semantics.json"
OUT = REPO / "data/generated/techstream_v18/tss3_cruise_live_transport.json"
SELECTED = (0x1901, 0x1905, 0x1906, 0x1912, 0x1914)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_member(archive: Path, member: str) -> bytes:
    p = subprocess.run(["7z", "e", "-so", str(archive), member], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0 or not p.stdout:
        raise SystemExit(f"failed to extract {member}: {p.stderr.decode(errors='replace')[-500:]}")
    return p.stdout


def pe_image_base_and_sections(data: bytes) -> tuple[int, list[tuple[int, int, int, int]]]:
    if data[:2] != b"MZ":
        raise ValueError("not MZ")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("not PE")
    coff = pe + 4
    nsec = struct.unpack_from("<H", data, coff + 2)[0]
    opt_size = struct.unpack_from("<H", data, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    if magic != 0x10B:
        raise ValueError(f"expected PE32, got optional magic {magic:#x}")
    image_base = struct.unpack_from("<I", data, opt + 28)[0]
    sec = opt + opt_size
    sections = []
    for i in range(nsec):
        off = sec + i * 40
        vsize, va, raw_size, raw_ptr = struct.unpack_from("<IIII", data, off + 8)
        sections.append((va, max(vsize, raw_size), raw_ptr, raw_size))
    return image_base, sections


def read_va(data: bytes, va: int, size: int) -> bytes:
    image_base, sections = pe_image_base_and_sections(data)
    rva = va - image_base
    for sec_rva, span, raw_ptr, raw_size in sections:
        if sec_rva <= rva and rva + size <= sec_rva + span:
            delta = rva - sec_rva
            if delta + size > raw_size:
                raise ValueError(f"VA {va:#x} extends beyond raw section")
            return data[raw_ptr + delta:raw_ptr + delta + size]
    raise ValueError(f"VA {va:#x} not mapped")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", type=Path, default=ARCHIVE)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    if not args.archive.is_file():
        raise SystemExit(f"missing GTS+ archive: {args.archive}")

    dll = extract_member(args.archive, MEMBER)
    if len(dll) != 507920 or sha(dll) != "cce3ecd1203f81914c51d5b2599ee68eb4f7faafa8cbd9bb24fd7390b54d651d":
        raise ValueError("DataListIF.dll identity drift")

    functions = {
        "dataid_setup": (0x100393D0, 486, "4e08f6fcf01fd9d5511b73783c2bf5af9670360d3e856e866252b19aa5fc7ec6"),
        "check_rcv_frame": (0x10038FD0, 577, "932e5eee05d5605f13611e35bf9aad62fbb3dc3f86a8b444da5200f6a5d8a54e"),
    }
    function_evidence = {}
    for name, (va, size, expected) in functions.items():
        body = read_va(dll, va, size)
        if sha(body) != expected:
            raise ValueError(f"{name} body drift")
        function_evidence[name] = {"va": f"0x{va:08X}", "size": size, "sha256": expected}

    anchors = {
        "request_service_22": (0x100394E7, "c60022"),
        "request_did_hi_load": (0x100394EF, "0fb6445801"),
        "request_did_hi_store": (0x100394F4, "884101"),
        "request_did_lo_load": (0x100394FC, "0fb60458"),
        "request_did_lo_store": (0x10039500, "884102"),
        "request_length_3": (0x10039515, "c7460403000000"),
        "response_mode_is_22": (0x10038FF1, "80f922"),
        "response_positive_service_62": (0x10038FF6, "3c62"),
        "response_skip_three_bytes": (0x1003900C, "83c203"),
        "response_length_minus_three": (0x10039013, "83c0fd"),
        "response_expected_length_lookup": (0x10039021, "0fb70448"),
        "response_length_cap_compare": (0x10039028, "663bc3"),
    }
    raw_anchors = {}
    for name, (va, expected_hex) in anchors.items():
        expected = bytes.fromhex(expected_hex)
        actual = read_va(dll, va, len(expected))
        if actual != expected:
            raise ValueError(f"{name} drift: {actual.hex()} != {expected_hex}")
        raw_anchors[name] = {"va": f"0x{va:08X}", "bytes": expected_hex}

    sem_bytes = SEMANTICS.read_bytes()
    sem = json.loads(sem_bytes)
    p5_bytes = P5.read_bytes()
    p5 = json.loads(p5_bytes)
    frc_setting = [x for x in p5["vds_setting_table"]["ecu_setting_table_anchors"] if x["ecu_no"] == 498]
    if len(frc_setting) != 1 or frc_setting[0]["database"] != "FRC_P5" or frc_setting[0]["phase"] != 5 or frc_setting[0]["address"] != "792":
        raise ValueError("FRC_P5 VDS address join drift")
    rows = sem["frc_p5"]["monitors"]
    selected = []
    for did in SELECTED:
        did_s = f"0x{did:04X}"
        hits = [row for row in rows if row["primary_data_id"] == did_s]
        if not hits:
            raise ValueError(f"missing FRC monitor rows for {did_s}")
        max_bit = max(row["bit_range"][1] for row in hits)
        selected.append({
            "data_id": did_s,
            "request": f"22{did:04X}",
            "strict_capture_positive_prefix": f"62{did:04X}",
            "minimum_payload_bytes_from_monitored_bits": max_bit // 8 + 1,
            "monitor_rows": [
                {"monitor_key": row["monitor_key"], "name": row["name"], "bit_range": row["bit_range"], "monitor_record_sha256": row["monitor_record_sha256"]}
                for row in hits
            ],
        })

    out = {
        "schema": "techstream-gtsplus-p5-cruise-live-dataid-transport-v1",
        "scope": {"category_id": 498, "database": "FRC_P5.ddb", "ecu_name": "Front Recognition Camera 2", "physical_request_address": "0x792"},
        "sources": {
            "gtsplus_archive": {"path": str(args.archive.relative_to(REPO)) if args.archive.is_relative_to(REPO) else str(args.archive), "member": MEMBER},
            "data_list_if": {"size": len(dll), "sha256": sha(dll)},
            "cruise_semantics": {"path": str(SEMANTICS.relative_to(REPO)), "sha256": sha(sem_bytes)},
            "p5_lateral_control_semantics": {"path": str(P5.relative_to(REPO)), "sha256": sha(p5_bytes), "frc_vds_anchor": frc_setting[0]},
        },
        "raw_function_evidence": function_evidence,
        "raw_instruction_anchors": raw_anchors,
        "transport": {
            "request": "one 3-byte request per selected Data ID: 0x22 || DID_hi || DID_lo",
            "positive_response_gate": "the Phase-5 receive worker requires service byte 0x62 for a queued 0x22 request",
            "payload_copy": "advance response pointer by 3 bytes and copy min(received_length-3, runtime_expected_data_id_length)",
            "runtime_expected_length_source": "caller-provided per-Data-ID length array; DataMonitorPhase5 obtains this from the supported-ECU DataIdLengthList cache rather than from the FRC_P5 type-62 monitor bit range",
            "returned_did_validation_boundary": "CCommEventPhase5DM::CheckRcvFrame does not compare response bytes 1/2 with the queued DID before stripping the first three bytes. For an independent capture probe, require the stricter conventional 0x62||DID_hi||DID_lo prefix before treating payload as the requested oracle.",
            "outer_session_boundary": "The narrowed current-GTS+ Phase-5 live-monitor path proves the SID-0x22 transactions but does not prove a named outer UDS DiagnosticSessionControl prerequisite. Do not infer 0x10 01/03 or a SecurityAccess requirement from the monitor-internal state machine alone.",
        },
        "selected_cruise_oracles": selected,
        "capture_recipe": {
            "poll": [f"22{did:04X}" for did in SELECTED],
            "validate": "accept only 0x62 followed by the same requested two-byte Data ID, then decode the existing FRC_P5 monitor bit ranges",
            "purpose": "synchronize exact Toyota cruise permission/main/operation/set-speed/follow-distance diagnostic truth with all-bus CAN during the next firmware-identified target capture",
        },
        "conclusion": "For these five FRC_P5 cruise Data IDs, current GTS+ does use ordinary UDS ReadDataByIdentifier wire requests. The Phase-5-specific machinery is the monitor selection/scheduling/buffering layer around SID 0x22, not a different live data service. CAN-field mapping and any outer diagnostic-session prerequisite remain open/dynamic.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(selected)} selected Data IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
