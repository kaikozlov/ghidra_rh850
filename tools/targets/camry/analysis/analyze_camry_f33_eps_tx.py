#!/usr/bin/env python3
"""Reconstruct the complete exact-F33 EPS transmit surface.

Scope is Toyota EPS application firmware 8965F3307000.  The reducer closes the
five generated-COM transmit I-PDUs, their direct signal writers and lower-stack
routes, plus the non-cyclic diagnostic and XCP-shaped transmit endpoints.  OEM
names are only attached where firmware/GTS evidence closes them; anonymous
status fields remain structural rather than inheriting stale public-DBC names.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
SECOC030 = ROOT / "data/generated/camry_8965F3307000_030_secoc_tx.json"
FAULT_STATUS = ROOT / "data/generated/camry_8965F3307000_fault_status.json"
LIVENESS = ROOT / "targets/camry-2026/raw-20260912/eps-recovery/saved-log-liveness.json"
LATERAL_TRACE = ROOT / "data/generated/camry_2026_lateral_flow_trace.json"
LOCAL_RAM = ROOT / "targets/camry-2026/raw-20260826/secoc-recovery/ram/local_ram_pe1.bin"
OUT = ROOT / "data/generated/camry_8965F3307000_eps_tx.json"
EXPECTED_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

TX_CLASS_PTRS = 0x21994
TX_CLASS_COUNTS = 0x21A48
TX_TABLE_CLASS0 = 0x21F58
TX_TABLE_CLASS2 = 0x21F80
TX_TABLE_CLASS5 = 0x21F48
PDU_TABLE = 0x226C0
PDU_SLICE_TABLE = 0x22840
INITIAL_TX_IMAGE = 0x22184
SIGNAL_TO_PDU = 0x22488
SIGNAL_COUNT = 284
PDU_COUNT = 5
FOREGROUND_MS = 5.0  # target-native TAUJ0 CH3 proof: docs/variants/camry-2026-live-baseline.md §12.1

PACKERS = {
    0: 0x4C97A,
    1: 0x4CED0,
    2: 0x4CE08,
    3: 0x4C7AA,
    4: 0x4C8E0,
}

FUNCTIONS = {
    0x4C000: "0x030/0x4A3 inhibit and feedback preparation",
    0x4C14E: "0x4A3 application staging",
    0x4C1C0: "0x351 debounce/state preparation",
    0x4C216: "0x351 status/force producer",
    0x4C24A: "0x394 classifier projection",
    0x4C294: "0x030 status snapshot",
    0x4C2DC: "0x030 cooperative-status projection",
    0x4C380: "0x030 signed feedback scaling",
    0x4C3D2: "0x030 position/status projection",
    0x4C490: "0x030 torque/current staging",
    0x4C738: "0x030 supervisory code producer",
    0x4C772: "0x030 status-byte staging",
    0x4C7AA: "0x4A3 generated-COM packer",
    0x4C8E0: "0x4C8 generated-COM packer",
    0x4C97A: "0x030 generated-COM packer",
    0x4CE08: "0x394 generated-COM packer",
    0x4CED0: "0x351 generated-COM packer",
    0x7BC42: "validated BswM/communication group-mask reader",
    0x7BF60: "generated-COM group-mask distributor",
    0x7D1DC: "generated-COM change-aware pack helper",
    0x7D31E: "generated-COM raw pack helper",
    0x7D8AE: "generated-COM group activation / timer arming",
    0x7DB0C: "generated-COM cyclic timer service",
    0x7DF14: "generated-COM transmit dispatcher",
    0x7E13A: "generated-COM pending-transmit service",
    0x7FEF8: "direct CanIf transmit class dispatcher",
    0x81A7E: "PduR transmit shim",
    0x81AB2: "PduR lower-route dispatcher",
    0x805C6: "CanIf HTH runtime initialization",
    0x85112: "lower CAN driver transmit dispatcher",
    0x853AA: "classic CAN transmit writer",
    0x8549E: "CAN-FD transmit writer",
    0x8ED8E: "SecOC transmit ingress",
}

# Exact generated-COM direct field map.  The source description is deliberately
# firmware-first.  "oem" is used only where Toyota diagnostic data closes a name.
FIELDS: dict[int, list[dict[str, Any]]] = {
    0: [
        {"signal": 0, "wire": "B0", "source": "0xFEBE8136", "producer": "0x4C490", "role": "coarse signed steering-wheel-torque projection (/10 path)", "grade": "firmware"},
        {"signal": 1, "wire": "B2[1]", "source": "constant 0", "producer": "0x4C97A", "role": "constant-clear application bit", "grade": "firmware"},
        {"signal": 2, "wire": "B2[0]", "source": "0xFEBE8137", "producer": "0x4C490", "role": "source-status boolean from FEBE65D3", "grade": "firmware"},
        {"signal": 3, "wire": "B3:B4[7:4]", "source": "0xFEBE8164", "producer": "0x4C3D2", "role": "signed12 quotient of E948-derived position/angle-family quantity", "grade": "firmware"},
        {"signal": 4, "wire": "B4[3:0]", "source": "0xFEBE8138", "producer": "0x4C3D2", "role": "signed4 remainder paired with signal 3", "grade": "firmware"},
        {"signal": 5, "wire": "B5:B6[7:4]", "source": "0xFEBE8166", "producer": "0x4C380", "role": "signed12 clamped projection of FEBE6776/8", "grade": "firmware"},
        {"signal": 6, "wire": "B6[3]", "source": "0xFEBE8139", "producer": "0x4C3D2", "role": "E888==0x5A validity/status mirror", "grade": "firmware"},
        {"signal": 7, "wire": "B6[2]", "source": "0xFEBE80DE", "producer": "0x4C000", "role": "steering/current fault-or-inhibit aggregate", "grade": "firmware"},
        {"signal": 8, "wire": "B6[1]", "source": "0xFEBE80E3", "producer": "0x4C294", "role": "status snapshot copied from FEBEE848", "grade": "firmware"},
        {"signal": 9, "wire": "B6[0]", "source": "0xFEBE80E2", "producer": "0x4C000", "role": "operational/status inhibit", "grade": "firmware"},
        {"signal": 10, "wire": "B7", "source": "computed", "producer": "0x4C97A", "role": "inner additive checksum: low8(sum(B0..B6)+0x38)", "grade": "firmware"},
        {"signal": 11, "wire": "B8", "source": "0xFEBE813A", "producer": "0x4C490", "role": "Steering Wheel Torque coarse component, signed8 * 0.1 N.m", "oem": "Steering Wheel Torque", "grade": "GTS+firmware"},
        {"signal": 12, "wire": "B9:B10[7:4]", "source": "0xFEBE8168", "producer": "0x4C3D2", "role": "copy of signal-3 signed12 quotient", "grade": "firmware"},
        {"signal": 13, "wire": "B10[3]", "source": "0xFEBE813B", "producer": "0x4C3D2", "role": "E888==0x5A validity/status mirror", "grade": "firmware"},
        {"signal": 14, "wire": "B11:B12:B13[7:6]", "source": "0xFEBE8174", "producer": "0x4C3D2", "role": "signed18 clamped projection of FEBEE94C", "grade": "firmware"},
        {"signal": 15, "wire": "B13[5]", "source": "0xFEBE813C", "producer": "0x4C490", "role": "second source-status boolean from FEBE65D3", "grade": "firmware"},
        {"signal": 16, "wire": "B13[4]", "source": "0xFEBE813D", "producer": "0x4C3D2", "role": "E888==0x5A validity/status", "grade": "firmware"},
        {"signal": 17, "wire": "B13[3]", "source": "0xFEBE813E", "producer": "0x4C490", "role": "transition/validity state derived from FEBE8050/FEBE8051 family", "grade": "firmware"},
        {"signal": 18, "wire": "B13[2]", "source": "0xFEBE813F", "producer": "0x4C490", "role": "status mirror from FEBE7475", "grade": "firmware"},
        {"signal": 19, "wire": "B13[1:0]", "source": "0xFEBE817C", "producer": "0x4C738", "role": "2-bit cooperative supervisory/readiness code; normal readiness requires <2", "grade": "firmware"},
        {"signal": 20, "wire": "B14:B15", "source": "0xFEBE816A", "producer": "0x4C380", "role": "signed16 scaled projection of FEBE6776", "grade": "firmware"},
        {"signal": 21, "wire": "B16[5]", "source": "0xFEBE80F6", "producer": "0x4C2DC", "role": "cooperative-control status mirror from FEBEE82F", "grade": "firmware"},
        {"signal": 22, "wire": "B16[4]", "source": "0xFEBE80F7", "producer": "0x4C2DC", "role": "cooperative-control status mirror from FEBEE83D", "grade": "firmware"},
        {"signal": 23, "wire": "B16[3]", "source": "0xFEBE80F8", "producer": "0x4C2DC", "role": "cooperative-control status mirror from FEBEE83B", "grade": "firmware"},
        {"signal": 24, "wire": "B16[2:1]", "source": "0xFEBE80F9", "producer": "0x4C2DC", "role": "2-bit cooperative-control state from FEBEE83C", "grade": "firmware"},
        {"signal": 25, "wire": "B16[0]", "source": "0xFEBE80EC", "producer": "0x4C2DC", "role": "cooperative-command inhibit (CAFC family)", "grade": "firmware"},
        {"signal": 26, "wire": "B17[7]", "source": "0xFEBE8140", "producer": "0x4C490", "role": "status mirror from FEBE80E7", "grade": "firmware"},
        {"signal": 27, "wire": "B17[6]", "source": "0xFEBE8141", "producer": "0x4C490", "role": "status mirror from FEBE80E6", "grade": "firmware"},
        {"signal": 28, "wire": "B17[5]", "source": "0xFEBE818E", "producer": "0x4C772", "role": "status mirror from FEBEE88D", "grade": "firmware"},
        {"signal": 29, "wire": "B17[4]", "source": "0xFEBE818D", "producer": "0x4C772", "role": "status mirror from FEBEE88C", "grade": "firmware"},
        {"signal": 30, "wire": "B17[3:0]", "source": "0xFEBE8142", "producer": "0x4C490", "role": "Steering Wheel Torque fine signed4 component, *0.01 N.m", "oem": "Steering Wheel Torque", "grade": "GTS+firmware"},
        {"signal": 31, "wire": "B19[0]", "source": "0xFEBE80E0", "producer": "0x4C2DC", "role": "cooperative-angle inhibit (CAD9 family)", "grade": "firmware"},
        {"signal": 32, "wire": "B20:B21", "source": "0xFEBE8156", "producer": "0x4C2DC", "role": "signed steering-control/angle-family feedback from FEBEE8BC", "grade": "firmware"},
        {"signal": 33, "wire": "B22:B23", "source": "0xFEBE816C", "producer": "0x4C490", "role": "signed motor-feedback/current-family proxy; related to, but not identical units with, DID1151 Q-axis current", "grade": "GTS+firmware"},
        {"signal": 34, "wire": "B27[1]", "source": "0xFEBE8150", "producer": "0x4C490", "role": "constant-clear in normal producer", "grade": "firmware"},
        {"signal": 35, "wire": "B27[0]", "source": "0xFEBE8151", "producer": "0x4C490", "role": "constant-clear in normal producer", "grade": "firmware"},
    ],
    1: [
        {"signal": 38, "wire": "B2[7:5]", "source": "0xFEBE8100", "producer": "0x4C1C0/0x4C216", "role": "debounced electrical-monitor/status code; force path writes 7", "grade": "firmware"},
        {"signal": 39, "wire": "B2[4]", "source": "0xFEBE8101", "producer": "0x4C216", "role": "companion force/special-status flag", "grade": "firmware"},
    ],
    2: [
        {"signal": 40, "wire": "B1[7:6]", "source": "0xFEBE8105", "producer": "0x4C24A", "role": "classifier table column 4", "grade": "firmware"},
        {"signal": 41, "wire": "B1[5:3]", "source": "0xFEBE8106", "producer": "0x4C24A", "role": "classifier table column 1", "grade": "firmware"},
        {"signal": 42, "wire": "B2[3:1]", "source": "0xFEBE8107", "producer": "0x4C24A", "role": "classifier table column 2", "grade": "firmware"},
        {"signal": 43, "wire": "B2[0]", "source": "0xFEBE8109", "producer": "0x4C24A", "role": "classifier table column 3", "grade": "firmware"},
    ],
    3: [
        {"signal": 44, "wire": "B0", "source": "0xFEBE810B", "producer": "0x4C14E", "role": "status/inhibit byte: FEBE80DE OR 0x20 marker", "grade": "firmware"},
        {"signal": 45, "wire": "B1", "source": "0xFEBE810C", "producer": "0x4C14E", "role": "signed12 coarse received 0x025 steering-angle-family source (FEBE8048), high byte", "grade": "firmware"},
        {"signal": 46, "wire": "B2", "source": "0xFEBE810D", "producer": "0x4C14E", "role": "signed12 coarse received 0x025 steering-angle-family source (FEBE8048), low byte", "grade": "firmware"},
        {"signal": 47, "wire": "B3", "source": "0xFEBE810E", "producer": "0x4C14E", "role": "signed12 filtered/voted Steering Angle high nibble; source FEBE7D46", "oem": "Steering Angle", "grade": "GTS+firmware"},
        {"signal": 48, "wire": "B4", "source": "0xFEBE810F", "producer": "0x4C14E", "role": "signed12 filtered/voted Steering Angle low byte; source FEBE7D46", "oem": "Steering Angle", "grade": "GTS+firmware"},
        {"signal": 49, "wire": "B5", "source": "0xFEBE8110", "producer": "0x4C14E", "role": "signed steering-wheel-torque projection, 0.1 N.m/count", "oem": "Steering Wheel Torque", "grade": "GTS+firmware"},
        {"signal": 50, "wire": "B6", "source": "0xFEBE8111", "producer": "0x4C14E", "role": "motor-feedback/current-family proxy high byte", "grade": "firmware"},
        {"signal": 51, "wire": "B7", "source": "0xFEBE8112", "producer": "0x4C14E", "role": "motor-feedback/current-family proxy low byte", "grade": "firmware"},
    ],
    4: [
        {"signal": 52, "wire": "B0", "source": "constant 0x09", "producer": "0x4C8E0", "role": "constant template byte", "grade": "firmware"},
        {"signal": 53, "wire": "B1[7]", "source": "constant 0", "producer": "0x4C8E0", "role": "constant-clear bit", "grade": "firmware"},
        {"signal": 54, "wire": "B2:B3", "source": "constant 0", "producer": "0x4C8E0", "role": "constant-clear 16-bit field", "grade": "firmware"},
    ],
}

# Wire calls recovered from the exact packers.  Used both as documentation and
# an executable cross-check against the decompiler corpus.
EXPECTED_DIRECT = {
    0: list(range(0, 36)),
    1: [38, 39],
    2: [40, 41, 42, 43],
    3: list(range(44, 52)),
    4: [52, 53, 54],
}
EXPECTED_CONFIG_ONLY = {0: [36, 37, 283], 4: [55]}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_corpus() -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    with CORPUS.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("record") == "function":
                rows[int(rec["entry_addr"], 16)] = rec
    return rows


def direct_signal_calls(rows: dict[int, dict[str, Any]]) -> dict[int, list[str]]:
    pattern = re.compile(r"FUN_0007d(?:31e|1dc)\((0x[0-9a-f]+|\d+)")
    hits: dict[int, list[str]] = defaultdict(list)
    for entry, rec in rows.items():
        for match in pattern.finditer(rec.get("decompiled_c", "")):
            signal = int(match.group(1), 0)
            hits[signal].append(f"0x{entry:06X}")
    return {k: sorted(set(v)) for k, v in sorted(hits.items())}


def find_techstream_dtc(code: str) -> dict[str, str] | None:
    obj = json.loads(FAULT_STATUS.read_text(encoding="utf-8"))
    found: list[dict[str, str]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("techstream_code") == code:
                found.append({
                    "code": code,
                    "description": str(node.get("techstream_description", "")),
                    "failure": str(node.get("techstream_failure", "")),
                })
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(obj)
    if not found:
        return None
    first = found[0]
    if any(row != first for row in found):
        raise RuntimeError(f"inconsistent Techstream labels for {code}")
    return first


def dynamic_observations() -> dict[str, Any]:
    result: dict[str, Any] = {
        "boundary": "tracked retained-log evidence; absence is an observation for these captures, not proof that a configured PDU can never transmit",
    }
    if LIVENESS.is_file():
        obj = json.loads(LIVENESS.read_text(encoding="utf-8"))
        positive = []
        for file in obj.get("files", []):
            for row in file.get("watched_frames", []):
                if row.get("event") == "can" and row.get("src") == 0 and row.get("address") in {"0x030", "0x351", "0x394", "0x4A3", "0x4C8"}:
                    positive.append({"path": file["path"], "duration_s": file["duration_s"], **row})
        result["saved_log_positive_native_frames"] = positive
    if LATERAL_TRACE.is_file():
        trace = json.loads(LATERAL_TRACE.read_text(encoding="utf-8"))
        result["parked_censuses"] = trace.get("parked_censuses", {})
    return result


def analyze() -> dict[str, Any]:
    image = IMAGE.read_bytes()
    if len(image) != 0x100000 or sha256(image) != EXPECTED_SHA256:
        raise RuntimeError("exact F33 CodeFlash identity mismatch")
    rows = read_corpus()
    missing_functions = sorted(set(FUNCTIONS) - set(rows))
    if missing_functions:
        raise RuntimeError(f"canonical corpus missing functions: {[hex(x) for x in missing_functions]}")

    u16 = lambda off: struct.unpack_from("<H", image, off)[0]
    u32 = lambda off: struct.unpack_from("<I", image, off)[0]
    txrec = struct.Struct("<IBBH")
    pdesc = struct.Struct("<HBBHBB")

    class_ptrs = [u32(TX_CLASS_PTRS + 4 * i) for i in range(6)]
    class_counts = [u16(TX_CLASS_COUNTS + 2 * i) for i in range(6)]
    if class_counts != [5, 0, 4, 0, 0, 1]:
        raise RuntimeError(f"unexpected Tx class counts {class_counts}")
    if class_ptrs != [0x21F58, 0x218BC, 0x21F80, 0x218C4, 0x218CC, 0x21F48]:
        raise RuntimeError(f"unexpected Tx class pointers {[hex(x) for x in class_ptrs]}")

    class0 = [txrec.unpack_from(image, TX_TABLE_CLASS0 + 8 * i) for i in range(5)]
    class2 = [txrec.unpack_from(image, TX_TABLE_CLASS2 + 8 * i) for i in range(4)]
    class5 = [txrec.unpack_from(image, TX_TABLE_CLASS5)]
    expected_class0_words = [0x40000030, 0x351, 0x394, 0x4A3, 0x4C8]
    if [r[0] for r in class0] != expected_class0_words:
        raise RuntimeError("normal Tx CanIf table drift")
    if [r[0] for r in class2] != [0x7A9, 0x7A9, 0x7A8, 0x7A8]:
        raise RuntimeError("diagnostic Tx table drift")
    if class5[0][0] != 0x9FE00002:
        raise RuntimeError("extended special Tx route drift")

    descriptors = [pdesc.unpack_from(image, PDU_TABLE + 8 * i) for i in range(PDU_COUNT)]
    slices = [u16(PDU_SLICE_TABLE + 2 * i) for i in range(PDU_COUNT)]
    lengths = [rec[3] for rec in descriptors]
    if slices != [0, 32, 36, 39, 47] or lengths != [32, 4, 3, 8, 8]:
        raise RuntimeError("generated-COM geometry drift")
    initial = [image[INITIAL_TX_IMAGE + slices[i]:INITIAL_TX_IMAGE + slices[i] + lengths[i]] for i in range(PDU_COUNT)]

    signal_to_pdu = [u16(SIGNAL_TO_PDU + 2 * i) for i in range(SIGNAL_COUNT)]
    assigned = {pdu: [sid for sid, owner in enumerate(signal_to_pdu) if owner == pdu] for pdu in range(PDU_COUNT)}
    expected_assigned = {
        0: list(range(0, 38)) + [283],
        1: [38, 39],
        2: [40, 41, 42, 43],
        3: list(range(44, 52)),
        4: [52, 53, 54, 55],
    }
    if assigned != expected_assigned:
        raise RuntimeError(f"signal ownership drift: {assigned}")

    calls = direct_signal_calls(rows)
    for pdu, expected in EXPECTED_DIRECT.items():
        got = [sid for sid in expected if calls.get(sid) == [f"0x{PACKERS[pdu]:06X}"]]
        if got != expected:
            raise RuntimeError(f"PDU{pdu} direct call mismatch: got={got}, expected={expected}")
    for sid in [36, 37, 55, 283]:
        if calls.get(sid):
            raise RuntimeError(f"configured-only signal {sid} unexpectedly has direct pack call {calls[sid]}")

    # PduR class-0 lower-routing table: PDU0 has an indirect security route;
    # PDU1..4 are 0xffff and fall through to the direct CanIf dispatcher.
    lower_select = [u16(0x229CE + 4 * i + 2) for i in range(5)]
    if lower_select != [0, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF]:
        raise RuntimeError(f"PduR lower route drift {lower_select}")
    if u32(0x21EF8) != 0x8ED8E or u32(0x21EAC) != 0x7FEF8:
        raise RuntimeError("PduR target function drift")

    secoc = json.loads(SECOC030.read_text(encoding="utf-8"))
    dtc = find_techstream_dtc("C159B49")
    if dtc is None:
        raise RuntimeError("missing C159B49 Techstream join")

    classifier = [list(image[0x2A19C + 5 * i:0x2A19C + 5 * (i + 1)]) for i in range(17)]
    debounce_count = u32(0x2FBF8)
    if debounce_count != 7:
        raise RuntimeError(f"0x351 debounce calibration drift: {debounce_count}")

    # One generated-COM Tx group owns all five normal PDUs.  The live RAM
    # snapshot is useful because it proves the group and all periodic timers
    # were actually armed on-car, independent of what a particular panda
    # capture happened to expose on the wire.
    group_count = image[0x21C6E]
    group_start, group_pdu_count = struct.unpack_from("<HH", image, 0x22140)
    group_masks = list(image[0x22148:0x22148 + PDU_COUNT])
    if (group_count != 1 or (group_start, group_pdu_count) != (0, 5) or group_masks != [0x10] * 5):
        raise RuntimeError("generated-COM Tx group geometry drift")

    runtime_snapshot: dict[str, Any] | None = None
    if LOCAL_RAM.is_file():
        ram = LOCAL_RAM.read_bytes()
        if len(ram) != 0x20000:
            raise RuntimeError("unexpected retained PE1 RAM size")
        runtime_snapshot = {
            "source": str(LOCAL_RAM.relative_to(ROOT)),
            "bswm_mask_and_complement": [ram[0x4FAC], ram[0x4FAD]],
            "bswm_secondary_mask_and_complement": [ram[0x4FAE], ram[0x4FAF]],
            "group_desired_mask": ram[0x4A3B],
            "group_current_mask": ram[0x4A3C],
            "pdu_state_bytes": list(ram[0x493E:0x493E + PDU_COUNT]),
            "periodic_countdowns": [struct.unpack_from("<H", ram, 0x496E + 2 * i)[0] for i in range(PDU_COUNT)],
            "minimum_delay_countdowns": [struct.unpack_from("<H", ram, 0x4978 + 2 * i)[0] for i in range(PDU_COUNT)],
            "canif_hth_state_bytes": list(ram[0x4904:0x4904 + 5]),
        }
        if runtime_snapshot["group_desired_mask"] != 0x10 or runtime_snapshot["group_current_mask"] != 0x10:
            raise RuntimeError("retained RAM does not show the normal Tx group active")
        if runtime_snapshot["pdu_state_bytes"] != [0x81] * 5:
            raise RuntimeError("retained RAM generated-COM PDU states drift")
        periods = [d[0] for d in descriptors]
        countdowns = runtime_snapshot["periodic_countdowns"]
        if not all(0 < c <= p for c, p in zip(countdowns, periods)):
            raise RuntimeError(f"retained periodic timers not armed as expected: {countdowns}")

    # CanIf class-0 hardware handles.  0x030 has handle 0 / driver object 0;
    # the four classic-CAN PDUs share handle 1 / driver object 3.  Both map to
    # the same lower driver node index 1, so the classic path is a real sibling
    # hardware route rather than dead configuration.
    hth_base = u32(0x218E4)
    hth_desc = [struct.unpack_from("<HHHHH", image, hth_base + 10 * i) for i in range(5)]
    hth_map_base = u32(0x22E38)
    driver_map = [tuple(image[hth_map_base + 2 * i:hth_map_base + 2 * i + 2]) for i in range(56)]
    if class0[0][3] != 0 or any(r[3] != 1 for r in class0[1:]):
        raise RuntimeError("normal Tx HTH selection drift")
    if driver_map[47] != (1, 0) or driver_map[50] != (1, 3):
        raise RuntimeError("lower driver HTH mapping drift")

    normal_ids = [0x030, 0x351, 0x394, 0x4A3, 0x4C8]
    pdu_names = [
        "EPS protected status/feedback/control-state",
        "EPS electrical-monitor/status projection",
        "EPS internal fault/state classifier projection",
        "EPS redundant angle/torque/motor-feedback status",
        "EPS constant/status template (OEM role unresolved)",
    ]
    messages = []
    for pdu, can_id in enumerate(normal_ids):
        cycle = descriptors[pdu][0]
        record = class0[pdu]
        messages.append({
            "pdu": pdu,
            "can_id": f"0x{can_id:03X}",
            "name": pdu_names[pdu],
            "can_fd": bool(record[0] & 0x40000000),
            "wire_length": lengths[pdu],
            "cycle_ticks": cycle,
            "nominal_cycle_ms": cycle * FOREGROUND_MS,
            "nominal_hz": 1000.0 / (cycle * FOREGROUND_MS),
            "initial_application_bytes": initial[pdu].hex(),
            "packer": f"0x{PACKERS[pdu]:06X}",
            "assigned_signal_ids": assigned[pdu],
            "direct_packed_signal_ids": EXPECTED_DIRECT[pdu],
            "configured_without_direct_pack_call": EXPECTED_CONFIG_ONLY.get(pdu, []),
            "fields": FIELDS[pdu],
            "protection": (
                {
                    "kind": "SecOC + inner additive checksum",
                    "application_bytes": "B0..B27",
                    "inner_checksum": "B7=low8(sum(B0..B6)+0x38)",
                    "outer_trailer": "B28[7:4]=FV4; B28[3:0]||B29..B31=MAC28",
                    "data_id": "0x0030",
                    "freshness_bits_full": 46,
                    "freshness_bits_transmitted": 4,
                    "authenticator_bits": 28,
                    "icu_s_command": 5,
                    "icu_s_key_selector": 4,
                    "route": "PDU0 -> PduR -> 0x8ED8E SecOC Tx -> lower PDU0 -> CanIf",
                }
                if pdu == 0
                else {
                    "kind": "direct generated-COM/CanIf; no configured SecOC Tx profile",
                    "route": f"PDU{pdu} -> PduR direct fallback -> 0x7FEF8 CanIf",
                    "application_integrity_field": None,
                }
            ),
        })

    messages[0]["unwritten_application_regions"] = [
        "B1", "B2[7:2]", "B10[2:0]", "B16[7:6]", "B18", "B19[7:1]",
        "B24:B26", "B27[7:2]",
    ]
    messages[0]["configured_only_note"] = (
        "signals 36, 37 and 283 are assigned to PDU0 by the exact signal->PDU table but no literal call to either generated pack helper exists anywhere in the 6,065-function canonical corpus; no wire field is invented for them"
    )
    messages[1]["fault_join"] = {
        "base_monitor_state": "FEBEBDE4 -> FEBEE82B -> 0x4C1C0 -> FEBE8100",
        "debounce_count": debounce_count,
        "force_path": "0x4C216 writes code 7 and flag 1 when (FEBE6764&3)!=0 and FEBE8143!=0",
        "related_techstream_dtc": dtc,
        "boundary": "the force-7 path is a distinct broad status override; do not rename it C159B49 or temporary/permanent",
    }
    messages[2]["classifier"] = {
        "internal_state_count": 17,
        "table_address": "0x2A19C",
        "table_rows": classifier,
        "projection": "0x4C24A exports columns 4,1,2,3 as signals 40..43; the projection is lossy",
        "boundary": "classifier state 0 is the deepest recovered clear/normal state, but is not itself the OEM DID Ready Status",
    }
    messages[3]["semantic_join"] = {
        "steering_angle_source": "FEBE7D46; also used by exact GTS DID1037 Steering Angle",
        "steering_wheel_torque": "B5 signed projection at 0.1 N.m/count",
        "motor_feedback": "B6:B7 derive from FEBE6718-family feedback; not a steering command and not literal DID1151 amp units",
    }
    messages[4]["constant_template"] = {
        "normal_packer_result": "09 00 00 00 00 00 00 00",
        "signal55": "assigned by configuration but has no direct generated pack call in the canonical corpus; B4..B7 stay at their zero initial image absent an unrecovered dynamic/raw writer",
        "oem_semantic": "unresolved",
    }

    function_evidence = {
        f"0x{entry:06X}": {
            "role": role,
            "body_size": rows[entry]["body_size"],
            "decompiled_c_sha256": rows[entry]["decompiled_c_sha256"],
        }
        for entry, role in FUNCTIONS.items()
    }

    diagnostic_rx = [u32(0x21FA0 + 8 * i) for i in range(3)]
    if diagnostic_rx != [0x7A1, 0x777, 0x7A0]:
        raise RuntimeError(f"diagnostic Rx table drift: {diagnostic_rx}")

    special_raw = class5[0][0]
    special_ext = special_raw & 0x1FFFFFFF
    request_raw = u32(0x21F50)
    request_ext = request_raw & 0x1FFFFFFF

    return {
        "schema": "camry-f33-eps-tx-v1",
        "target": {
            "software_id": "8965F3307000",
            "codeflash_sha256": sha256(image),
            "scope": "exact F33 EPS application image only",
        },
        "executive_summary": {
            "normal_generated_com_count": 5,
            "normal_ids": [f"0x{x:03X}" for x in normal_ids],
            "diagnostic_response_ids": ["0x7A9", "0x7A8"],
            "special_extended_response_id": f"0x{special_ext:08X}",
            "only_secoc_protected_normal_tx": "0x030",
            "semantic_boundary": "complete structural transmit surface; unresolved OEM field names stay explicitly unresolved",
        },
        "generated_configuration": {
            "class_pointers": [f"0x{x:05X}" for x in class_ptrs],
            "class_counts": class_counts,
            "normal_tx_records": [
                {
                    "raw_id_word": f"0x{r[0]:08X}",
                    "can_id": f"0x{(r[0] & 0x1FFFFFFF):03X}",
                    "controller": r[1],
                    "reserved": r[2],
                    "confirmation_route": r[3],
                }
                for r in class0
            ],
            "pdu_descriptors": [list(r) for r in descriptors],
            "slice_offsets": slices,
            "foreground_scheduler_ms": FOREGROUND_MS,
            "foreground_scheduler_evidence": "exact F33 TAUJ0 CH3 target-native proof in docs/variants/camry-2026-live-baseline.md §12.1",
            "signal_ownership": {str(k): v for k, v in assigned.items()},
            "direct_pack_call_census": {str(sid): calls.get(sid, []) for sid in list(range(56)) + [283]},
        },
        "scheduler": {
            "tx_group_count": group_count,
            "group_0": {
                "start_pdu": group_start,
                "pdu_count": group_pdu_count,
                "membership_masks": group_masks,
                "communication_mask": "0x10",
            },
            "periodic_cycle_ticks": [d[0] for d in descriptors],
            "periodic_cycle_ms": [d[0] * FOREGROUND_MS for d in descriptors],
            "packing_semantics": {
                "0x7D31E": "raw bit pack; does not request change-triggered transmit",
                "0x7D1DC": "change-aware pack; on a changed value calls 0x7E196(pdu,0x80) to request event transmission",
                "event_triggered_pdus": ["0x351", "0x394"],
                "periodic_only_at_direct-pack layer": ["0x030", "0x4A3", "0x4C8"],
            },
            "runtime_snapshot": runtime_snapshot,
        },
        "canif_hardware_routes": {
            "hth_table_address": f"0x{hth_base:05X}",
            "hth_descriptors": [list(x) for x in hth_desc],
            "normal_pdu_routes": [
                {"can_id": "0x030", "canif_handle": 0, "hth_index": 0, "driver_object_id": 47, "driver_node": driver_map[47][0], "driver_mailbox": driver_map[47][1], "lower_writer": "0x8549E CAN-FD"},
                {"can_id": "0x351", "canif_handle": 1, "hth_index": 1, "driver_object_id": 50, "driver_node": driver_map[50][0], "driver_mailbox": driver_map[50][1], "lower_writer": "0x853AA classic CAN"},
                {"can_id": "0x394", "canif_handle": 1, "hth_index": 1, "driver_object_id": 50, "driver_node": driver_map[50][0], "driver_mailbox": driver_map[50][1], "lower_writer": "0x853AA classic CAN"},
                {"can_id": "0x4A3", "canif_handle": 1, "hth_index": 1, "driver_object_id": 50, "driver_node": driver_map[50][0], "driver_mailbox": driver_map[50][1], "lower_writer": "0x853AA classic CAN"},
                {"can_id": "0x4C8", "canif_handle": 1, "hth_index": 1, "driver_object_id": 50, "driver_node": driver_map[50][0], "driver_mailbox": driver_map[50][1], "lower_writer": "0x853AA classic CAN"},
            ],
            "interpretation": "0x030 and the four classic PDUs use sibling hardware objects on the same lower CAN-driver node; retained HTH state 0x69 means idle/available, not disabled",
        },
        "normal_messages": messages,
        "noncyclic_transmit": {
            "diagnostic_transport": {
                "rx_ids": [f"0x{x:03X}" for x in diagnostic_rx],
                "tx_records": [
                    {"source_pdu": f"0x{0x0800+i:04X}", "can_id": f"0x{r[0]:03X}", "controller": r[1], "route": r[3]}
                    for i, r in enumerate(class2)
                ],
                "interpretation": "ISO-TP/UDS application responses: primary/functional paths use 0x7A9; secondary physical endpoint uses 0x7A8",
            },
            "xcp_shaped_extended": {
                "response_source_pdu": "0xF800",
                "response_raw_hardware_id_word": f"0x{special_raw:08X}",
                "response_extended_can_id": f"0x{special_ext:08X}",
                "paired_request_raw_hardware_id_word": f"0x{request_raw:08X}",
                "paired_request_extended_can_id": f"0x{request_ext:08X}",
                "stock_reachability": "request ingress exists, but exact F33 fixed CodeFlash 0x30D68=0x5A causes 0x98E80 to reject protocol execution before CONNECT/opcode dispatch",
            },
        },
        "secoc_030_crosscheck": {
            "schema": secoc.get("schema"),
            "data_id": secoc["secoc_tx_profile"]["data_id"],
            "authenticator_bits": secoc["secoc_tx_profile"]["authenticator_bits"],
            "security_trailer_bytes": secoc["secoc_tx_profile"]["security_trailer_bytes"],
            "icu_s_key_selector": secoc["live_crypto"]["icu_s_key_selector"],
            "tracked_oracle_frame_count": secoc["tracked_oracle"]["frame_count"],
        },
        "dynamic_observations": dynamic_observations(),
        "function_evidence": function_evidence,
        "evidence_boundary": (
            "Raw CodeFlash closes configuration, pack geometry, direct pack calls and routing. GTS joins are only used for explicitly named diagnostics. "
            "The whole canonical decompiler corpus proves no literal generated-pack-helper calls for configured-only signals 36/37/55/283, but computed indirect calls, DMA or unrecovered code remain outside that bounded negative. "
            "Retained logs show runtime behavior for captures we possess; absence of a configured cyclic PDU in those logs is not proof it can never be enabled."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()
    result = analyze()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
