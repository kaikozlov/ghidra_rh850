#!/usr/bin/env python3
"""Build exact-F33 external lateral-ingress evidence and intersect it with live CAN.

This closes the normal generated-COM alternatives to the protected B6 target-angle
receiver.  It intentionally does not claim that a factory-LTA-active interval was
captured, nor does it exclude a non-COM/internal path or an upstream transform on a
network the EPS does not directly accept.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import re
import struct
from pathlib import Path

from camry_f33_corpus import CORPUS, IMAGE, IMAGE_SHA256, REPO

OUT = REPO / "data/generated/camry_8965F3307000_external_lateral_ingress.json"
GTS = REPO / "data/generated/gtsplus_2026/camry_8965F3307000_emps_semantics.json"
B6 = REPO / "data/generated/camry_8965F3307000_codeflash.json"
FAULT = REPO / "data/generated/camry_8965F3307000_fault_status.json"
DRIVES = [
    REPO / "targets/camry-2026/raw-20260827/camry_relay_route_can_20260827.ndjson.gz",
    REPO / "targets/camry-2026/raw-20260827/camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
]
GP = 0xFEBEB800
RX_TABLE = 0x21FE8
RX_COUNT = 43
SIGNAL_TO_PDU = 0x22488
SIGNAL_COUNT = 284
PDU_OFFSETS = 0x22840

# Authoritative exact-F33 scalar copy-edge cone.  These are the only scalar
# receive signals whose raw -> staged -> snapshot chain survives the pinned
# copy-edge model; all other 97 scalar extracts are empty under that model.
COMMAND_CONE = {
    130: (0xFEBE800E, 0xFEBEF192, 0xFEBEAE0A, [0xCC6BA], "gate"),
    141: (0xFEBE801E, 0xFEBEF196, 0xFEBEAE08, [0xCC6BA], "monitor"),
    186: (0xFEBE804E, 0xFEBEF06B, 0xFEBEACC4, [0xC2F78, 0xC2FAC, 0xCE9AC], "feedback-validity"),
    187: (0xFEBE8048, 0xFEBEF1A0, 0xFEBEADFE, [0xC2E2A, 0xCE9EA], "measured-feedback"),
    188: (0xFEBE804F, 0xFEBEF06F, 0xFEBEACC5, [0xC2E2A, 0xCE9EA], "measured-feedback"),
    189: (0xFEBE804A, 0xFEBEF19E, 0xFEBEAE22, [0xCC07A, 0xCE9EA, 0xCED28], "measured-feedback"),
    211: (0xFEBE8076, 0xFEBEF097, 0xFEBEACCE, [0xC9650, 0xC973A], "monitor-gate"),
    212: (0xFEBE8072, 0xFEBEF1BC, 0xFEBEAE04, [0xC3D4C, 0xC9D18], "monitor/plausibility"),
    213: (0xFEBE8074, 0xFEBEF1BE, 0xFEBEAE06, [0xC3D4C, 0xC9CAA], "monitor/plausibility"),
    223: (0xFEBE807F, 0xFEBEF091, 0xFEBEACD6, [0xC3008, 0xCECD6], "gate"),
    243: (0xFEBE80A0, 0xFEBEF094, 0xFEBEACCD, [0xC973A, 0xCB664, 0xCE772, 0xCE7A6], "protected-status-gate"),
    261: (0xFEBE80BC, 0xFEBEF130, 0xFEBEADB0, [0xCB73A, 0xCEFFC], "sole-mode-selector"),
    262: (0xFEBE80B8, 0xFEBEF1FA, 0xFEBEAE90, [0xCBA80, 0xCBB66, 0xCCF0E, 0xCEE80], "sole-command-magnitude"),
    263: (0xFEBE80CB, 0xFEBEF155, 0xFEBEADDD, [0xCB664], "command-gate"),
    265: (0xFEBE80C0, 0xFEBEF134, 0xFEBEADBB, [0xCDA20], "command-composition-gate"),
    268: (0xFEBE80C3, 0xFEBEF137, 0xFEBEADBC, [0xCEC8A], "sequence-state"),
    269: (0xFEBE80C4, 0xFEBEF138, 0xFEBEADBD, [0xCE3AA], "percentage-contribution"),
    270: (0xFEBE80C5, 0xFEBEF139, 0xFEBEADBE, [0xCDFF8], "percentage-contribution"),
    273: (0xFEBE80CA, 0xFEBEF14D, 0xFEBEADD9, [0xCFDA0], "command-gate"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(cond: object, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def corpus_map() -> dict[int, dict]:
    out = {}
    with CORPUS.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") == "function":
                out[int(row["entry_addr"], 16)] = row
    return out


def token(funcs: dict[int, dict], entry: int, *tokens: str) -> str:
    text = funcs[entry]["decompiled_c"]
    for item in tokens:
        need(item in text, f"0x{entry:08X} missing {item!r}")
    return text


def has_ref(funcs: dict[int, dict], entry: int, address: int, ref_type: str) -> bool:
    return any(
        int(ref["to_addr"], 0) == address and ref["ref_type"] == ref_type
        for ref in funcs[entry]["data_references"]
    )


def need_ref(funcs: dict[int, dict], entry: int, address: int, ref_type: str) -> None:
    need(has_ref(funcs, entry, address, ref_type),
         f"0x{entry:08X} missing {ref_type} reference to 0x{address:08X}")


def sx16be(data: bytes, off: int) -> int:
    return int.from_bytes(data[off:off + 2], "big", signed=True)


def live_summary() -> tuple[dict, dict]:
    counts: collections.Counter[tuple[int, int, int]] = collections.Counter()
    d5a: list[int] = []
    d5b: list[int] = []
    eng: list[int] = []
    total = 0
    for path in DRIVES:
        with gzip.open(path, "rt") as f:
            for line in f:
                _seg, _t, bus, addr, hx = json.loads(line)
                data = bytes.fromhex(hx)
                total += 1
                counts[(bus, addr, len(data))] += 1
                if bus != 0:
                    continue
                if addr == 0x0D5 and len(data) == 8:
                    d5a.append(sx16be(data, 1))
                    d5b.append(sx16be(data, 3))
                elif addr == 0x115 and len(data) == 8:
                    eng.append(sx16be(data, 0))
    def span(values: list[int]) -> dict:
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "unique": len(set(values)),
        }
    selected = {}
    for addr, dlc in ((0x025, 32), (0x0B6, 32), (0x0D5, 8), (0x115, 8), (0x1C5, 8), (0x64F, 8)):
        selected[f"0x{addr:03X}/{dlc}"] = {str(bus): counts[(bus, addr, dlc)] for bus in range(3)}
    return {
        "combined_incoming_frames": total,
        "selected_counts": selected,
        "d5_signed16_b1_b2": span(d5a),
        "d5_signed16_b3_b4": span(d5b),
        "id115_signed16_b0_b1": span(eng),
    }, counts


def build() -> dict:
    image = IMAGE.read_bytes()
    need(len(image) == 0x100000 and hashlib.sha256(image).hexdigest() == IMAGE_SHA256, "F33 image drift")
    funcs = corpus_map()
    need(len(funcs) == 6065, "F33 corpus function count drift")
    gts = json.loads(GTS.read_text())
    b6 = json.loads(B6.read_text())
    fault = json.loads(FAULT.read_text())

    # Exact normal application receive descriptors, PDU IDs 5..47.
    rx: dict[int, dict] = {}
    for i in range(RX_COUNT):
        raw, length = struct.unpack_from("<II", image, RX_TABLE + i * 8)
        pdu = 5 + i
        rx[pdu] = {"pdu": pdu, "can_id": raw & 0x1FFFFFFF, "can_fd": bool(raw & 0x40000000), "length": length}
    need(len(rx) == 43 and rx[44] == {"pdu": 44, "can_id": 0x0B6, "can_fd": True, "length": 32}, "Rx table/B6 drift")

    # Exhaust the physical steering/diagnostic RSCFD controller-1 acceptance span.
    # Existing target-native routing proves controller 1 owns exactly rules 0..46.
    # Rules 0..42 are the 43 normal descriptors in identical ID order; the only
    # remaining rules are three UDS addresses and the packed standard-CAN XCP 0x7F7.
    rule_base = 0x230B8
    rules = [struct.unpack_from("<IIII", image, rule_base + 0x10 * i) for i in range(47)]
    need(struct.unpack_from("<H", image, 0x22ECE)[0] == 0 and image[0x22ED0] == 47,
         "RSCFD controller-1 receive span drift")
    normal_rule_ids = [r[0] for r in rules[:43]]
    descriptor_ids = [rx[p]["can_id"] for p in range(5, 48)]
    need(normal_rule_ids == descriptor_ids, "normal Rx descriptors no longer exhaust rules 0..42")
    need([r[0] for r in rules[43:46]] == [0x7A1, 0x777, 0x7A0], "diagnostic acceptance tail drift")
    need(rules[46][0] == 0x9FDC0002, "packed XCP rule46 drift")

    # The receiver also tells us the source *module relationship* for B6. CAN frames
    # have no source-node address, so this comes from F33's own communication-loss
    # monitor rather than from the arbitration descriptor. The six-row monitor family
    # is the exact F33 homolog of the H family: row5 watches status slot 0x1A; the
    # status-map table maps 0x1A -> PDU44 -> 0x0B6. Loss selects Dem event 0x0143,
    # whose DTC index 82 is the same exact F33 DTC record used by populated event 0x00AA.
    # Current GTS+ names that record U012987 Lost Communication with Brake System
    # Control Module / Missing Message. Thus F33 itself expects B6 from the brake-system
    # source domain even though it cannot encode a transmitter ECU address on the wire.
    token(funcs, 0x3CBE8, "param_1 < 6", "DAT_000280a4", "DAT_000280a6")
    token(funcs, 0x3CCBE, "uVar5 < 6", "DAT_000280a9", "FUN_000498e0")
    monitor_table = 0x280A4
    status_map = 0x28FE4
    monitor_row = image[monitor_table + 5 * 8:monitor_table + 6 * 8]
    need(monitor_row == bytes.fromhex("00004301051aa506"), f"B6 communication-monitor row drift: {monitor_row.hex()}")
    dem_event = struct.unpack_from("<H", monitor_row, 2)[0]
    status_slot = monitor_row[5]
    need(dem_event == 0x143 and status_slot == 0x1A, "B6 monitor event/slot drift")
    monitored_pdu = image[status_map + status_slot * 8]
    need(monitored_pdu == 44 and rx[monitored_pdu]["can_id"] == 0x0B6, "B6 monitor slot no longer resolves PDU44")
    event_rec = image[0x2FC50 + dem_event * 8:0x2FC58 + dem_event * 8]
    dtc_index = event_rec[2]
    need(event_rec == bytes.fromhex("4200520000010000") and dtc_index == 82, "B6 monitor Dem/DTC join drift")
    dtc_rec = image[0x30850 + dtc_index * 8:0x30858 + dtc_index * 8]
    need(dtc_rec == bytes.fromhex("8729c10001000000"), "B6 monitor DTC record drift")
    dtc82 = None
    for cls in fault["dem"]["classes"].values():
        for event in cls["events"]:
            d = event.get("dtc")
            if d and d["dtc_index"] == 82:
                dtc82 = d
                break
        if dtc82:
            break
    need(dtc82 is not None and dtc82["techstream_code"] == "U012987"
         and dtc82["techstream_description"] == "Lost Communication with Brake System Control Module"
         and dtc82["techstream_failure"] == "Missing Message", "B6 source-module Techstream join drift")

    # Exact scalar generated-COM calls.  Relative byte geometry comes directly from
    # signal-to-PDU + PDU-buffer-offset tables, not guessed DBC layouts.
    s2p = [struct.unpack_from("<H", image, SIGNAL_TO_PDU + 2 * i)[0] for i in range(SIGNAL_COUNT)]
    pdu_off = [struct.unpack_from("<H", image, PDU_OFFSETS + 2 * i)[0] for i in range(48)]
    call_re = re.compile(
        r"FUN_0007d12a\((0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),"
        r"(0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),([^;]+)\);", re.I
    )
    scalar = []
    for entry, row in funcs.items():
        for m in call_re.finditer(row["decompiled_c"]):
            sid, off, bits, bitoff, signed = [int(m.group(i), 0) for i in range(1, 6)]
            pdu = s2p[sid]
            if pdu not in rx:
                continue
            r = rx[pdu]
            scalar.append({
                "signal": sid, "pdu": pdu, "can_id": r["can_id"], "length": r["length"],
                "can_fd": r["can_fd"], "byte_offset": off - pdu_off[pdu], "bits": bits,
                "bit_offset": bitoff, "signed": bool(signed), "unpacker": f"0x{entry:08X}",
                "destination_expression": m.group(6).strip(),
            })
    need(len(scalar) == 116, f"scalar call census drift: {len(scalar)}")
    large_signed = [x for x in scalar if x["signed"] and x["bits"] >= 12]
    shapes = {(x["can_id"], x["signal"], x["byte_offset"], x["bits"]) for x in large_signed}
    expected = {
        (0x025, 187, 0, 12), (0x025, 189, 4, 12), (0x0B6, 262, 4, 16),
        (0x0D5, 212, 1, 16), (0x0D5, 213, 3, 16), (0x115, 134, 0, 16),
        (0x1C5, 141, 2, 16), (0x64F, 255, 2, 18), (0x64F, 257, 4, 18),
    }
    need(shapes == expected, f"large signed ingress drift: {sorted(shapes)}")

    # Corrected scalar command-cone census.  Pin every surviving copy edge to
    # canonical-corpus instruction/data references, including signal243's
    # stack RMW (the generated unpacker does not receive FEBE80A0 directly).
    scalar_by_signal = {row["signal"]: row for row in scalar}
    need(len(scalar_by_signal) == len(scalar), "scalar signal IDs are no longer unique")
    expected_cone_ids = {261, 262, 263, 265, 268, 269, 270, 273,
                         186, 187, 188, 189, 211, 212, 213, 243, 223, 130, 141}
    need(set(COMMAND_CONE) == expected_cone_ids, "pinned command-cone ID set drift")
    cone_rows = []
    for sid in sorted(COMMAND_CONE):
        row = scalar_by_signal[sid]
        raw, stage, snapshot, consumers, classification = COMMAND_CONE[sid]
        unpacker = int(row["unpacker"], 0)
        if sid == 243:
            need(row["destination_expression"] == "auStack_9", "signal243 destination is no longer stack-backed")
            token(funcs, 0x4BB62,
                  "auStack_9[0] = DAT_febe80a0;",
                  "FUN_0007d12a(0xf3,0x187,1,7,0,auStack_9);",
                  "puVar2[-0x3760] = auStack_9[0];")
            need_ref(funcs, unpacker, raw, "READ")
            need_ref(funcs, unpacker, raw, "WRITE")
            raw_edge = "0x0004BB62 stack-RMW auStack_9[0]"
        else:
            # The call-site reference is DATA because the unpacker writes
            # through its destination pointer; the exact call arguments above
            # establish that this address is the raw destination.
            need_ref(funcs, unpacker, raw, "DATA")
            raw_edge = row["unpacker"]
        need_ref(funcs, 0x58074, raw, "READ")
        need_ref(funcs, 0x58074, stage, "WRITE")
        need_ref(funcs, 0xBCD66, stage, "READ")
        need_ref(funcs, 0xBCD66, snapshot, "WRITE")
        for consumer in consumers:
            need_ref(funcs, consumer, snapshot, "READ")
        cone_rows.append({
            **row,
            "can_id": f"0x{row['can_id']:03X}",
            "raw": f"0x{raw:08X}",
            "raw_copy": raw_edge,
            "stage": f"0x{stage:08X}",
            "stage_copy": "0x00058074",
            "snapshot": f"0x{snapshot:08X}",
            "snapshot_copy": "0x000BCD66",
            "consumers": [f"0x{x:08X}" for x in consumers],
            "classification": classification,
        })
    empty_cone_ids = sorted(set(scalar_by_signal) - expected_cone_ids)
    need(len(cone_rows) == 19 and len(empty_cone_ids) == 97, "19/116 scalar command-cone census drift")

    # Same-image identity: F181's secondary record is software compatibility
    # identity, protected at startup by exact image-local comparisons.  DID2032
    # is the separate 0x17D80 record and must not be conflated with F181.
    token(funcs, 0x4FA26, "*param_1 = 2;", "(&DAT_00020860)[iVar2]", "(&DAT_00017dc0)[iVar2]")
    token(funcs, 0x637EE, "FUN_00062d5e();")
    token(funcs, 0x62D5E, "(&DAT_00020850)[uVar1] != (&DAT_00017da0)[uVar1]",
          "DAT_00017dc0 != DAT_00020870", "iVar3 = -0x5aa55aa6;",
          "FUN_00070a92(iVar3,&DAT_febf0668,&DAT_febf10a4,&DAT_febf10c8);", "puVar2[0x4e6c] = uVar4;")
    token(funcs, 0x4F9DE, "*param_1 = 1;", "(&DAT_00017d80)[iVar2]")
    need(image[0x20860:0x2086C] == b"8965F3307000", "F181 primary identity drift")
    need(image[0x17DC0:0x17DCC] == b"8A3113303100", "F181 compatibility identity drift")
    need(image[0x17DA0:0x17DA8] == image[0x20850:0x20858] == b"JB1BA101", "JB compatibility pair drift")
    need(image[0x17DC0:0x17DC5] == image[0x20870:0x20875] == b"8A311", "8A311 prefix pair drift")
    need(image[0x17D80:0x17D8D] == b"8965H33030A00", "DID2032 record drift")

    # D5's two signed16 fields use saturating GP-relative snapshot copies that a
    # direct-xref-only census would miss.  Their consumers are monitor/plausibility paths.
    token(funcs, 0x4B86E,
          "FUN_0007d12a(0xd4,0x158,0x10,0,1,&DAT_febe8072);",
          "FUN_0007d12a(0xd5,0x15a,0x10,0,1,puVar2 + -0x378c);")
    token(funcs, 0x58074, "DAT_febef1bc = DAT_febe8072", "DAT_febef1be = DAT_febe8074")
    snap = token(funcs, 0xBCD66, "puVar15 + 0x39bc", "puVar15 + -0x9fc", "puVar15 + 0x39be", "puVar15 + -0x9fa")
    need("0x7fff" in snap and "-0x7fff" in snap, "D5 saturating snapshot clamp drift")
    token(funcs, 0xC9D18, "DAT_febeae04", "DAT_000b044c", "FUN_000bdb64(0xc9)")
    token(funcs, 0xC9CAA, "DAT_febeae06", "DAT_000b044a", "FUN_000bdb64(200)")
    need(struct.unpack_from("<H", image, 0xB044C)[0] == 100 and struct.unpack_from("<H", image, 0xB044A)[0] == 1000, "D5 thresholds drift")
    for event in (0xC8, 0xC9):
        rec = image[0x2FC50 + event * 8:0x2FC50 + (event + 1) * 8]
        need(rec == bytes.fromhex("4100000000010000"), f"DEM event 0x{event:02X} is no longer unpopulated")

    # 0x115's signed16 field ends at Toyota's exact F33 0x1032 Engine Revolution RDBI.
    token(funcs, 0x4B12E, "FUN_0007d12a(0x86,0xdf,0x10,0,1,&DAT_febe8014);")
    token(funcs, 0x58074, "DAT_febef194 = DAT_febe8014")
    token(funcs, 0xBE622, "DAT_febef194", "puVar3 + 0x682")
    token(funcs, 0xBE65C, "DAT_febef194", "puVar2 + 0x682")
    token(funcs, 0xBF3AA, "DAT_febebe82", "DAT_febee890")
    token(funcs, 0x4DAEE, "DAT_febee890")
    did1032 = next(x for x in gts["f33_rdbi_join"]["named_data_ids"] if x["data_id"] == "0x1032")
    need(did1032["callback"] == "0x0004DAEE" and did1032["signals"][0]["name"] == "Engine Revolution", "GTS+ DID1032 join drift")

    # Strengthen the known B6 path downstream to the exact Toyota-named torque observable.
    token(funcs, 0xCBA80, "DAT_febeae90", "DAT_febec7dc")
    token(funcs, 0xD039E, "puVar3 + 0x1450", "FUN_000cb9c8", "FUN_000cb9ae")
    token(funcs, 0xD042C, "DAT_febecc50", "DAT_febeac5a", "DAT_febecc62")
    token(funcs, 0xD0AAE, "DAT_febeac56 = DAT_febecc62")
    token(funcs, 0xBF33E, "DAT_febeac56", "DAT_febee40a")
    token(funcs, 0x5D5E0, "DAT_febee40a", "DAT_febe6772")
    token(funcs, 0x4E7D6, "DAT_febe6772")
    did1c02 = next(x for x in gts["f33_rdbi_join"]["named_data_ids"] if x["data_id"] == "0x1C02")
    need(did1c02["signals"][0]["name"] == "Command Value Torque" and did1c02["callback"] == "0x0004E7D6", "GTS+ 1C02 join drift")

    # Generic group/non-scalar receive copies are confined to signals 0x5A..0x67,
    # which map to 0x013..0x01F.  Those PDUs are all absent in the two live drives.
    token(funcs, 0x7E72A, "&DAT_00022488", "param_3 & 0xffff")
    group_callers = []
    for entry, row in funcs.items():
        if entry != 0x7E72A and "FUN_0007e72a(" in row["decompiled_c"]:
            group_callers.append(entry)
    need(group_callers == [0x693FE, 0x697F4], f"group receive caller drift: {group_callers}")
    group_signals = list(range(0x5A, 0x68))
    group_pdus = sorted({s2p[s] for s in group_signals})
    group_ids = sorted({rx[p]["can_id"] for p in group_pdus})
    need(group_ids == list(range(0x013, 0x020)), f"group receive ID drift: {group_ids}")

    live, counts = live_summary()
    need(live["combined_incoming_frames"] == 3574703, "combined live frame count drift")
    need(sum(live["selected_counts"]["0x0B6/32"].values()) == 0, "B6 unexpectedly present")
    need(all(sum(counts[(bus, addr, 8)] for bus in range(3)) == 0 for addr in group_ids), "group PDU unexpectedly present")

    candidates = []
    classifications = {
        (0x025, 187): ("measured-feedback", "Steering Angle; target-native 0x1037 join"),
        (0x025, 189): ("measured-feedback", "Steering Angle Velocity; target-native 0x1036 join"),
        (0x0B6, 262): ("external-lateral-command", "Target Steering Angle; protected B6 cooperative-control ingress"),
        (0x0D5, 212): ("monitor/plausibility", "saturating snapshot -> C9D18 threshold monitor; DEM event C9 unpopulated"),
        (0x0D5, 213): ("monitor/plausibility", "saturating snapshot -> C9CAA threshold monitor; DEM event C8 unpopulated"),
        (0x115, 134): ("engine-domain", "dataflow terminates at GTS+ DID1032 Engine Revolution"),
        (0x1C5, 141): ("not-observed", "accepted signed16 field; absent in both relay-correct drives"),
        (0x64F, 255): ("not-observed", "accepted signed18 field; absent in both relay-correct drives"),
        (0x64F, 257): ("not-observed", "accepted signed18 field; absent in both relay-correct drives"),
    }
    for row in sorted(large_signed, key=lambda x: (x["can_id"], x["signal"])):
        cls, why = classifications[(row["can_id"], row["signal"])]
        key = f"0x{row['can_id']:03X}/{row['length']}"
        candidates.append({**row, "classification": cls, "evidence": why, "live_counts": live["selected_counts"].get(key)})

    return {
        "schema": "camry-8965f3307000-external-lateral-ingress-v1",
        "target": {"software_id": "8965F3307000", "codeflash_sha256": IMAGE_SHA256, "corpus_function_count": len(funcs)},
        "sources": {
            "gtsplus_semantics": {"path": str(GTS.relative_to(REPO)), "sha256": sha(GTS)},
            "b6_static": {"path": str(B6.relative_to(REPO)), "sha256": sha(B6)},
            "fault_status": {"path": str(FAULT.relative_to(REPO)), "sha256": sha(FAULT)},
            "drive_artifacts": [{"path": str(p.relative_to(REPO)), "sha256": sha(p), "size": p.stat().st_size} for p in DRIVES],
        },
        "normal_rx": {
            "descriptor_table": f"0x{RX_TABLE:08X}", "descriptor_count": RX_COUNT,
            "accepted": [dict(x, can_id=f"0x{x['can_id']:03X}") for x in rx.values()],
            "scalar_receive_call_count": len(scalar),
            "signed_12plus_candidates": candidates,
        },
        "scalar_command_cone_census": {
            "model": "pinned raw -> stage@0x00058074 -> snapshot@0x000BCD66 copy edges with exact snapshot consumers",
            "scalar_receive_call_count": len(scalar),
            "nonempty_count": len(cone_rows),
            "empty_count": len(empty_cone_ids),
            "nonempty_signal_ids": [row["signal"] for row in cone_rows],
            "empty_signal_ids": empty_cone_ids,
            "chains": cone_rows,
            "semantics": {
                "signal261": "B6 signal261 is the sole recovered mode selector",
                "signal262": "B6 signal262 is the sole recovered command magnitude",
                "non_b6": "non-B6 cone members are feedback, monitors, plausibility inputs, or gates; none is a recovered command selector or magnitude",
            },
        },
        "same_image_software_compatibility_identity": {
            "f181_callback": "0x0004FA26",
            "f181_count": 2,
            "f181_records": ["8965F3307000 @ 0x00020860", "8A3113303100 @ 0x00017DC0"],
            "classification": "8A3113303100 is the same-image F181 software/compatibility identity",
            "startup_chain": ["0x000637EE", "0x00062D5E"],
            "startup_checks": [
                "8-byte JB1BA101: 0x00017DA0 <-> 0x00020850",
                "5-byte 8A311 prefix: 0x00017DC0 <-> 0x00020870",
            ],
            "mismatch_behavior": {
                "all_mismatches": "set protected error value -0x5AA55AA6 and pass it to 0x00070A92",
                "jb1ba101_mismatch": "additionally writes 0x5A to FEBF066C",
                "8a311_prefix_mismatch": "does not set the FEBF066C byte in this function",
            },
            "did2032": "0x0004F9DE separately emits count 1 from 0x00017D80 (8965H33030A00)",
        },
        "controller1_acceptance": {
            "rule_array": "0x000230B8", "start_index": 0, "count": 47,
            "normal_rule_indices": [0, 42],
            "normal_rule_ids": [f"0x{x:03X}" for x in normal_rule_ids],
            "normal_rules_equal_descriptor_order": True,
            "special_tail": [
                {"rule": 43, "can_id": "0x7A1", "role": "physical UDS"},
                {"rule": 44, "can_id": "0x777", "role": "functional UDS"},
                {"rule": 45, "can_id": "0x7A0", "role": "secondary diagnostics"},
                {"rule": 46, "packed_descriptor": "0x9FDC0002", "can_id": "0x7F7", "role": "application XCP"},
            ],
            "classification": "the exact steering/diagnostic RSCFD controller-1 hardware acceptance surface contains no hidden non-COM lateral CAN ID beyond the 43 normal descriptors",
        },
        "b6_receiver_source_expectation": {
            "receiver_controller": 1,
            "communication_monitor": {
                "dispatcher": "0x0003CBE8", "scheduler": "0x0003CCBE",
                "table": "0x000280A4", "row_index": 5, "raw_hex": monitor_row.hex(),
                "status_slot": "0x1A", "status_map_table": "0x00028FE4",
                "monitored_pdu": 44, "can_id": "0x0B6", "length": 32,
                "dem_event": "0x0143", "dem_event_raw_hex": event_rec.hex(),
                "dtc_index": dtc_index, "dtc_raw_hex": dtc_rec.hex(),
            },
            "techstream_dtc": {
                "code": dtc82["techstream_code"],
                "description": dtc82["techstream_description"],
                "failure": dtc82["techstream_failure"],
            },
            "classification": "exact F33 receiver expects B6/PDU44 as Brake System Control Module traffic; CAN itself carries no source-node address, so this identifies the monitored immediate source-domain relationship rather than a unique transmitter implementation",
        },
        "special_paths": {
            "0x0D5": {
                "wire": ["signal212 signed16 B1:B2", "signal213 signed16 B3:B4"],
                "path": ["FEBE8072/8074", "FEBEF1BC/F1BE", "FEBEAE04/AE06", "C9D18/C9CAA monitor paths"],
                "thresholds": [100, 1000], "dem_events": ["0x00C9 unpopulated", "0x00C8 unpopulated"],
                "live": {"signal212": live["d5_signed16_b1_b2"], "signal213": live["d5_signed16_b3_b4"]},
                "classification": "monitor/plausibility inputs; no target-angle/command-torque dataflow recovered",
            },
            "0x115": {
                "wire": "signal134 signed16 B0:B1",
                "path": ["FEBE8014", "FEBEF194", "BE622/BE65C", "FEBEBE82", "BF3AA", "FEBEE890", "RDBI 0x1032"],
                "gtsplus_name": "Engine Revolution", "live": live["id115_signed16_b0_b1"],
                "classification": "engine-domain readiness/measurement input; not lateral command",
            },
            "generic_group_receive": {
                "copy_function": "0x0007E72A", "callers": [f"0x{x:08X}" for x in group_callers],
                "signal_ids": [f"0x{x:02X}" for x in group_signals], "can_ids": [f"0x{x:03X}" for x in group_ids],
                "live_total": sum(counts[(bus, addr, 8)] for addr in group_ids for bus in range(3)),
                "classification": "generic group/non-scalar receive route is absent in both captured drives",
            },
        },
        "b6_to_command_torque": {
            "target_snapshot": "FEBEAE90",
            "selected_chain": ["CBA80 cooperative target state", "D039E command composition", "D042C scaling/clamp", "FEBECC62", "D0AAE -> FEBEAC56", "BF33E -> FEBEE40A", "5D5E0/5C6D8 -> FEBE6772", "RDBI 0x1C02"],
            "gtsplus_terminal": "0x1C02 Command Value Torque",
            "classification": "positive downstream corroboration of the already-proved protected B6 target-angle ingress",
        },
        "live_intersection": live,
        "conclusion": {
            "normal_com": "Exact controller-1 rules 0..42 equal the 43 normal generated-COM descriptors one-for-one; rules 43..46 are diagnostics/XCP only. The corrected pinned scalar copy-edge census has exactly 19 nonempty signals out of 116 and 97 empty: B6 signal261 is the sole mode selector and B6 signal262 the sole command magnitude; all non-B6 members are feedback, monitors, plausibility inputs, or gates. Signal243 uses the explicit 0x4BB62 stack-RMW path to FEBE80A0 -> FEBEF094 -> FEBEACCD. No observed ordinary EPS-CAN field besides B6 is identified as an external steering target/command, and there is no hidden controller-1 acceptance ID outside the normal COM table.",
            "b6": "Protected 0x0B6 remains the only positively recovered external target-steering-angle ingress. Exact F33 communication-monitor row5 independently maps PDU44/B6 loss to DTC index82, which GTS+ names U012987 Lost Communication with Brake System Control Module / Missing Message, so the EPS expects B6 from the brake-system source domain. This is an external cooperative-control interface, not proof that factory LTA uses B6: the retained machine-identified LTA/LCA intervals contain zero B6 and exact F33 has a separate B6-independent internal assist path into the physical command funnel.",
            "next": "Do not search another arbitrary accepted EPS CAN ID or infer an 0x08A-to-B6 translation. Factory LTA with zero B6 is already machine-proved and compatible with exact F33's D0218->CC48->CC60->CC50 internal assist path. Trace the exact external/local snapshot leaves that select or modulate that path during the LTA/LCA transition; treat 0x08A producer/SecOC ownership as a separate network-ownership question.",
            "production_output_authorized": False,
        },
        "boundary": [
            "The two drives do not machine-prove an exact factory-LTA-active interval.",
            "This census closes generated scalar COM plus the generic group-receive surface represented by exact F33 configuration; it does not prove the absence of DMA/peripheral mutation, diagnostics, computed aliases outside the recovered maps, or another internal controller path.",
            "Bus1 0x180..0x18C traffic is upstream candidate traffic only: those arbitration IDs are not in the exact F33 normal Rx descriptor table and cannot directly be the EPS normal-CAN command.",
            "GTS+ supplies diagnostic names/DIDs, not a CAN-ID database; CAN-to-name joins are through exact F33 firmware dataflow.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    obj = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
