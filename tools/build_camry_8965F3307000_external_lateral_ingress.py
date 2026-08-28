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

    # Exact normal application receive descriptors, PDU IDs 5..47.
    rx: dict[int, dict] = {}
    for i in range(RX_COUNT):
        raw, length = struct.unpack_from("<II", image, RX_TABLE + i * 8)
        pdu = 5 + i
        rx[pdu] = {"pdu": pdu, "can_id": raw & 0x1FFFFFFF, "can_fd": bool(raw & 0x40000000), "length": length}
    need(len(rx) == 43 and rx[44] == {"pdu": 44, "can_id": 0x0B6, "can_fd": True, "length": 32}, "Rx table/B6 drift")

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
            "drive_artifacts": [{"path": str(p.relative_to(REPO)), "sha256": sha(p), "size": p.stat().st_size} for p in DRIVES],
        },
        "normal_rx": {
            "descriptor_table": f"0x{RX_TABLE:08X}", "descriptor_count": RX_COUNT,
            "accepted": [dict(x, can_id=f"0x{x['can_id']:03X}") for x in rx.values()],
            "scalar_receive_call_count": len(scalar),
            "signed_12plus_candidates": candidates,
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
            "normal_com": "Among exact F33 normal generated-COM signed fields >=12 bits, the two observed non-B6 candidates are 0x0D5 monitor channels and 0x115 Engine Revolution; 0x025 is measured steering feedback; 0x1C5/0x64F are absent. The generic group receive PDUs 0x013..0x01F are also absent. No observed ordinary EPS-CAN COM field besides B6 is identified as an external steering target/command.",
            "b6": "Protected 0x0B6 remains the only positively recovered external target-steering-angle ingress and now has selected downstream corroboration to Toyota-named 0x1C02 Command Value Torque, but it is absent in both relay-correct drives.",
            "next": "Do not search another arbitrary accepted EPS CAN ID first. Synchronize the FRC 0x1601 LTA-active oracle with relay-correct CAN. If LTA is machine-proved active while B6 remains absent, move the search outside ordinary EPS generated-COM ingress: upstream FRC/Brake transformation, an internal/non-COM path, or another controller/peripheral path.",
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
