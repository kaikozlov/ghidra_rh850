#!/usr/bin/env python3
"""Build exact-F33 passive diagnostic oracles for B6-independent assist internals.

Firmware-first, read-only/offline.  This does not assign Toyota semantics to unnamed
DIDs.  It answers two narrower questions:

* are the recovered C54A2/C5554 selector cells directly exposed by exact F33 RDBI?
* do exact RDBI records expose deterministic scaled proxies of any D0218 terms?

The current GTS+ name boundary is consumed from the tracked target-native EMPS semantic
artifact; this builder never requires live vehicle I/O.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

from camry_f33_corpus import CORPUS, IMAGE, IMAGE_SHA256, REPO

OUT = REPO / "data/generated/camry_8965F3307000_internal_assist_oracles.json"
GTS = REPO / "data/generated/gtsplus_2026/camry_8965F3307000_emps_semantics.json"
LIVE_SELECTOR = REPO / "data/generated/camry_2026_baseline_selector_live.json"
RDBI_OFFSET = 0x2928C
RDBI_COUNT = 241


def need(cond: object, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def corpus_map() -> dict[int, dict]:
    out: dict[int, dict] = {}
    with CORPUS.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") == "function":
                out[int(row["entry_addr"], 16)] = row
    return out


def text(funcs: dict[int, dict], ea: int) -> str:
    need(ea in funcs, f"missing function {ea:#x}")
    return funcs[ea]["decompiled_c"]


def tokens(funcs: dict[int, dict], ea: int, *needles: str) -> None:
    body = text(funcs, ea)
    for needle in needles:
        need(needle in body, f"{ea:#x} missing token {needle!r}")


def data_refs(row: dict, addr: int, kind: str | None = None) -> list[dict]:
    out = []
    for ref in row.get("data_references", []):
        try:
            target = int(ref["to_addr"], 16)
        except (KeyError, TypeError, ValueError):
            continue
        if target == addr and (kind is None or ref.get("ref_type") == kind):
            out.append(ref)
    return out



def direct_users(funcs: dict[int, dict], addr: int, kind: str) -> list[int]:
    return sorted(ea for ea, row in funcs.items() if data_refs(row, addr, kind))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    funcs = corpus_map()
    image = IMAGE.read_bytes()
    need(len(image) == 0x100000, "unexpected CodeFlash length")

    rdbi = []
    for i in range(RDBI_COUNT):
        off = RDBI_OFFSET + i * 16
        did, size, callback, aux, selector = struct.unpack_from("<HHIII", image, off)
        rdbi.append({
            "record_index": i, "record_offset": f"0x{off:06X}", "data_id": did,
            "payload_size": size, "callback": callback, "aux": aux, "selector": selector,
            "raw_hex": image[off:off + 16].hex(),
        })
    by_did = {r["data_id"]: r for r in rdbi}

    # Direct selector-state exposure: no RDBI callback has a canonical direct ref to the
    # two state cells.  Keep this claim deliberately direct; derived diagnostic effects
    # through other control calculations are outside this negative.
    selector_cells = {0xFEBEC158: "FEBEC158", 0xFEBEC156: "FEBEC156"}
    selector_direct = {}
    for addr, name in selector_cells.items():
        callbacks = []
        for rr in rdbi:
            cb = rr["callback"]
            if cb and cb in funcs and data_refs(funcs[cb], addr, "READ"):
                callbacks.append(f"0x{rr['data_id']:04X}")
        selector_direct[name] = callbacks
    need(selector_direct == {"FEBEC158": [], "FEBEC156": []},
         f"selector RDBI direct-ref negative drift: {selector_direct}")

    unique_callbacks = {rr["callback"] for rr in rdbi if rr["callback"]}
    need(len(unique_callbacks) == 195 and all(cb in funcs for cb in unique_callbacks),
         f"RDBI callback denominator drift: {len(unique_callbacks)}")
    did_read_cells = set()
    for cb in unique_callbacks:
        for ref in funcs[cb].get("data_references", []):
            if ref.get("ref_type") != "READ":
                continue
            try:
                addr = int(ref["to_addr"], 16)
            except (KeyError, TypeError, ValueError):
                continue
            if addr >= 0xFEBE0000:
                did_read_cells.add(addr)
    selector_readers = set()
    selector_reader_writes = set()
    for ea, row in funcs.items():
        if any(data_refs(row, addr, "READ") for addr in selector_cells):
            selector_readers.add(ea)
            for ref in row.get("data_references", []):
                if ref.get("ref_type") != "WRITE":
                    continue
                try:
                    selector_reader_writes.add(int(ref["to_addr"], 16))
                except (KeyError, TypeError, ValueError):
                    pass
    need(len(did_read_cells) == 136, f"RDBI direct RAM-cell denominator drift: {len(did_read_cells)}")
    need(len(selector_readers) == 34, f"selector reader denominator drift: {len(selector_readers)}")
    need(not (selector_reader_writes & did_read_cells),
         f"selector-reader write now reaches DID-read cell: {sorted(selector_reader_writes & did_read_cells)}")

    # D0218 term proxy 1: C5EE -> D0D7C scaled/clamped AE12 -> BF3AA EE8B6 -> DID 1C3E.
    tokens(funcs, 0xD0D7C,
           "uVar1 = (uint)DAT_febeae3c;",
           "(int)DAT_febec5ee * uVar1",
           "DAT_febeae12 = SUB42(puVar3,0);",
           "(int)DAT_febecb38 * uVar1",
           "DAT_febeae6e = SUB42(puVar3,0);")
    tokens(funcs, 0xBF3AA,
           "DAT_febee8b6 = DAT_febeae12;",
           "DAT_febee8c2 = DAT_febeae6e;")

    # AE3C is itself an internal calibration-derived snapshot from FEBEB140.
    tokens(funcs, 0xBCD66, "*(undefined2 *)(puVar15 + -0x9c4) = *(undefined2 *)(puVar15 + -0x6c0);")
    need(0xFEBEB800 - 0x9C4 == 0xFEBEAE3C and 0xFEBEB800 - 0x6C0 == 0xFEBEB140,
         "AE3C/B140 GP geometry drift")

    term_specs = {
        0x1C3E: {
            "term": "FEBEC5EE", "intermediate": "FEBEAE12", "diagnostic_cell": "FEBEE8B6",
            "callback": 0x4EA90,
        },
        0x1C38: {
            "term": "FEBECB38", "intermediate": "FEBEAE6E", "diagnostic_cell": "FEBEE8C2",
            "callback": 0x4EA06,
        },
        0x1C4A: {
            "term": "FEBECB38", "intermediate": "FEBEAE6E", "diagnostic_cell": "FEBEE8C2",
            "callback": 0x4EB7C,
        },
        0x1C50: {
            "term": "FEBECB38", "intermediate": "FEBEAE6E", "diagnostic_cell": "FEBEE8C2",
            "callback": 0x4EC06,
        },
    }
    oracle_rows = []
    for did, spec in term_specs.items():
        rr = by_did[did]
        need((rr["payload_size"], rr["callback"], rr["selector"]) == (2, spec["callback"], 0),
             f"RDBI {did:#x} record drift: {rr}")
        cbtxt = text(funcs, spec["callback"])
        cell = spec["diagnostic_cell"].lower()
        need(f"DAT_{cell}" in cbtxt, f"RDBI {did:#x} no longer reads {spec['diagnostic_cell']}")
        need("* 100) / 0x80" in cbtxt and "FUN_00070110" in cbtxt and "FUN_0006a5ac" in cbtxt,
             f"RDBI {did:#x} scaling/emission drift")
        oracle_rows.append({
            "data_id": f"0x{did:04X}", "payload_size": 2,
            "callback": f"0x{spec['callback']:08X}", "selector": 0,
            "source_term": spec["term"], "scaled_intermediate": spec["intermediate"],
            "diagnostic_cell": spec["diagnostic_cell"],
            "term_to_intermediate": (
                f"D0D7C: clamp(({spec['term']} * FEBEAE3C) / 0x8000, +/-0x569A) -> {spec['intermediate']}"
            ),
            "rdbi_transform": f"({spec['diagnostic_cell']} * 100) / 0x80 -> saturate16 -> 2-byte RDBI payload",
            "classification": "exact scaled/clamped passive proxy of one D0218 internal term; OEM semantic name not inferred",
        })

    # Current target-native GTS+ name boundary.  1C02/1C03 are named, but these four
    # exact F33 records are absent from the current EMPS_P5 named intersection.
    gts = json.loads(GTS.read_text())
    named = {r["data_id"]: r for r in gts["f33_rdbi_join"]["named_data_ids"]}
    need("0x1C02" in named and named["0x1C02"]["signals"][0]["name"] == "Command Value Torque",
         "GTS+ exact-F33 name join anchor drift")
    for row in oracle_rows:
        row["current_gtsplus_emps_p5_name"] = (
            named[row["data_id"]]["signals"][0]["name"] if row["data_id"] in named else None
        )
    need(all(r["current_gtsplus_emps_p5_name"] is None for r in oracle_rows),
         "one of the formerly unnamed internal proxy DIDs gained a current GTS+ EMPS name")

    # Selector influence is distinguishable from selector-state readout. C9812 indexes an
    # exact calibration table with FEBEC156 and integrates the result into FEBEC5EC; C9A84
    # consumes C5EC and writes C5EE.  Thus DID 1C3E is a selector-modulated term proxy,
    # not an enum/state DID. C8678 independently proves C4C0 is selector-indexed too, but
    # no exact RDBI callback exposes C4C0 directly.
    tokens(funcs, 0xC9812,
           "uVar3 = (uint)DAT_febec156;",
           "FUN_000d0768((&PTR_DAT_000d39dc)[uVar3 & 3],uVar5);",
           "*(short *)(puVar4 + 0xdec) = (short)((iVar6 * 0x400) / (int)DAT_000b0174);")
    need(0xFEBEB800 + 0xDEC == 0xFEBEC5EC, "C9812 C5EC GP geometry drift")
    tokens(funcs, 0xC9A84,
           "iVar2 = (int)*(short *)(puVar4 + 0xdec) + (int)*(short *)(puVar4 + -0xc06);",
           "*(short *)(puVar4 + 0xdee) = (short)(((int)(short)iVar6 * (int)sVar1) / 0x400);")
    need(0xFEBEB800 + 0xDEE == 0xFEBEC5EE, "C9A84 C5EE GP geometry drift")
    tokens(funcs, 0xC8678,
           "uVar2 = (uint)DAT_febec156;",
           "FUN_000d0768((&PTR_LAB_000d3630)[uVar2 & 3],uVar5);",
           "*(int *)(puVar3 + 0xcc0) = iVar7;")
    need(0xFEBEB800 + 0xCC0 == 0xFEBEC4C0, "C8678 C4C0 GP geometry drift")

    # Critically, the apparent selector dependency of both C5EE and C4C0 aliases away in
    # this exact calibration. All four C9812 selector table entries point to the same map;
    # C8678's selector-strided table families likewise repeat the same pair for each bank.
    c5ee_selector_ptrs = [struct.unpack_from("<I", image, 0xD39DC + 4*i)[0] for i in range(4)]
    c4c0_map_ptrs = [struct.unpack_from("<I", image, 0xD3630 + 4*i)[0] for i in range(4)]
    c4c0_lohi = [struct.unpack_from("<I", image, 0xD3670 + 4*i)[0] for i in range(8)]
    need(c5ee_selector_ptrs == [0xB018A] * 4, f"C5EE selector map alias drift: {c5ee_selector_ptrs}")
    need(c4c0_map_ptrs == [0xB1208] * 4, f"C4C0 selector map alias drift: {c4c0_map_ptrs}")
    need(c4c0_lohi == [0xB1248, 0xB121C] * 4, f"C4C0 selector pair alias drift: {c4c0_lohi}")

    # Close the C28FC/C2B64 normal selector effect against the retained zero sig160 value.
    # Healthy AC3C=1 selects base 0x10100; integrity fallback AC3C=0 selects 0x18100.
    # Each FEBEC156 bank is eight 0x44-byte curves (=0x220 bytes). In the healthy bank
    # selector1 is genuinely different, while selectors0/2/3 are byte-identical; in the
    # fallback bank all four are identical. B35DC/B372A with mode value FEBEB124==0 can
    # produce AC2F only 0 or 0x22, which C54A2/C5554 map to C156 0 or 2 — exactly the two
    # identical normal blocks. The selector-indexed C58B8 record supplying C1A4/C1A6 is
    # also byte-identical for all selector values in both bases.
    bank_ptrs = [struct.unpack_from("<I", image, 0xB144C + 4*i)[0] for i in range(2)]
    need(bank_ptrs == [0x18100, 0x10100], f"C28FC base pointers drift: {bank_ptrs}")
    block_size = 8 * 0x44
    block_hashes = {}
    c58_records = {}
    import hashlib
    for label, base in (("integrity_fallback", bank_ptrs[0]), ("healthy", bank_ptrs[1])):
        blocks = [image[base + sel*block_size: base + (sel+1)*block_size] for sel in range(4)]
        block_hashes[label] = [hashlib.sha256(x).hexdigest() for x in blocks]
        c58_records[label] = [image[base + 0x9C4 + sel*0x12: base + 0x9C4 + (sel+1)*0x12].hex() for sel in range(4)]
    need(block_hashes["healthy"][0] == block_hashes["healthy"][2] == block_hashes["healthy"][3]
         and block_hashes["healthy"][1] != block_hashes["healthy"][0],
         f"healthy C28FC selector block relation drift: {block_hashes['healthy']}")
    need(len(set(block_hashes["integrity_fallback"])) == 1,
         f"fallback C28FC selector blocks no longer alias: {block_hashes['integrity_fallback']}")
    need(all(len(set(rows)) == 1 for rows in c58_records.values()),
         f"C58B8 selector records no longer alias: {c58_records}")
    tokens(funcs, 0xB35DC, "uVar1 = (uint)DAT_febeb124;", "DAT_febeb121 = 0x22;", "DAT_febeb121 = 0;")
    tokens(funcs, 0xB372A, "uVar1 = (uint)DAT_febeb124;", "DAT_febeb121 = 0x22;", "DAT_febeb121 = 0;")
    live_selector = json.loads(LIVE_SELECTOR.read_text())
    for label in ("drive_a", "drive_b"):
        s160 = live_selector["drives"][label]["signals"]["sig160"]
        need(s160["all"]["values"] == {"0": s160["all"]["frames"]}, f"{label} sig160 no longer route-zero")

    # Close the exact-F33 command-value-model -> motor-current boundary.  The earlier
    # direct-reader-only interpretation was incomplete because D042C writes FEBECC62 and
    # immediately reuses the same value to form FEBECC66 inside one function.  The
    # motor-driving branch is the post-slew CC64/AC54/EE40C path; AC56/EE40A/1C02 is a
    # diagnostic/model mirror of the pre-slew CC62 value.
    cc62_readers = direct_users(funcs, 0xFEBECC62, "READ")
    ac56_readers = direct_users(funcs, 0xFEBEAC56, "READ")
    e40a_readers = direct_users(funcs, 0xFEBEE40A, "READ")
    v6772_readers = direct_users(funcs, 0xFEBE6772, "READ")
    need(cc62_readers == [0xC4F04, 0xD0AAE], f"FEBECC62 canonical direct-reader drift: {cc62_readers}")
    need(v6772_readers == [0x4E7D6], f"FEBE6772 reader set drift: {v6772_readers}")

    # Pre-slew model value -> post-slew/override actuation command.
    tokens(funcs, 0xD042C,
           "DAT_febecc62 = (short)((int)((int)DAT_febecc50 * (uint)DAT_febeac5a) / 0x400);",
           "iVar2 = (int)DAT_febecc62;",
           "DAT_febecc66 = DAT_febecc62,")
    tokens(funcs, 0xD047C,
           "DAT_febecc64 = DAT_febecc66;",
           "DAT_febecc64 = 0x569a;")
    tokens(funcs, 0xD0AAE,
           "DAT_febeac54 = DAT_febecc64;",
           "DAT_febeac56 = DAT_febecc62;")
    tokens(funcs, 0xBF33E,
           "DAT_febee40a = DAT_febeac56;",
           "DAT_febee40c = DAT_febeac54;")
    tokens(funcs, 0x35C4C,
           "DAT_febe6af6 = DAT_febee40a;",
           "sVar1 = DAT_febee40c;",
           "DAT_febe6af4 = -sVar1;")
    tokens(funcs, 0x387BA, "DAT_febe6e0a = DAT_febe6af4;")
    tokens(funcs, 0x38502, "uVar1 = (uint)DAT_febe6e0a;", "DAT_febe6dec")
    tokens(funcs, 0x3835E, "iVar2 = (int)DAT_febe6dec;", "DAT_febe6dc8 = DAT_febe6dec,")
    tokens(funcs, 0x384D8, "sVar2 = DAT_febe6e0a;", "FUN_00038396((int)DAT_febe6dc8)")
    tokens(funcs, 0x37F16, "DAT_febe6d84 = DAT_febe6dd6;", "DAT_febe6d86 = DAT_febe6dc8;")

    funnel_cells = {
        "FEBECC64": 0xFEBECC64,
        "FEBEAC54": 0xFEBEAC54,
        "FEBEE40C": 0xFEBEE40C,
        "FEBE6AF4": 0xFEBE6AF4,
        "FEBE6E0A": 0xFEBE6E0A,
        "FEBE6DEC": 0xFEBE6DEC,
        "FEBE6DC8": 0xFEBE6DC8,
        "FEBE6DD6": 0xFEBE6DD6,
    }
    funnel_writers = {name: direct_users(funcs, addr, "WRITE") for name, addr in funnel_cells.items()}
    need(funnel_writers["FEBECC64"] == [0xD01B4, 0xD047C], f"CC64 writers drift: {funnel_writers['FEBECC64']}")
    need(funnel_writers["FEBEAC54"] == [0xBF97A, 0xD0AAE], f"AC54 writers drift: {funnel_writers['FEBEAC54']}")
    need(funnel_writers["FEBEE40C"] == [0xBF33E, 0xBF97A], f"E40C writers drift: {funnel_writers['FEBEE40C']}")
    need(funnel_writers["FEBE6AF4"] == [0x35C4C, 0x59448], f"6AF4 writers drift: {funnel_writers['FEBE6AF4']}")
    need(funnel_writers["FEBE6E0A"] == [0x387BA, 0x59448], f"6E0A writers drift: {funnel_writers['FEBE6E0A']}")
    need(funnel_writers["FEBE6DEC"] == [0x38502, 0x59448], f"6DEC writers drift: {funnel_writers['FEBE6DEC']}")
    need(funnel_writers["FEBE6DC8"] == [0x3835E, 0x59448], f"6DC8 writers drift: {funnel_writers['FEBE6DC8']}")
    need(funnel_writers["FEBE6DD6"] == [0x384D8, 0x59448], f"6DD6 writers drift: {funnel_writers['FEBE6DD6']}")
    need(0x38162 in direct_users(funcs, 0xFEBE6DC8, "READ") and 0x38162 in direct_users(funcs, 0xFEBE6DD6, "READ"),
         "downstream motor transform no longer reads both 6DC8/6DD6")

    # Diagnostic/model mirror branch of the pre-slew CC62 value.
    tokens(funcs, 0x5D5E0, "DAT_febe6772 = DAT_febee40a;")
    tokens(funcs, 0x4E7D6, "DAT_febe6772", "FUN_0006a5ac")
    tokens(funcs, 0xC4F04, "iVar8 = (int)DAT_febecc62;", "puVar3[0x92a] = bVar11;")
    qcmd84_writers = direct_users(funcs, 0xFEBE6D84, "WRITE")
    qcmd86_writers = direct_users(funcs, 0xFEBE6D86, "WRITE")
    need(qcmd84_writers == [0x37F16, 0x59448] and qcmd86_writers == [0x37F16, 0x59448],
         f"Q-current diagnostic mirror writer drift: {qcmd84_writers}/{qcmd86_writers}")
    mirror6af6_readers = direct_users(funcs, 0xFEBE6AF6, "READ")
    e22_readers = direct_users(funcs, 0xFEBE6E22, "READ")
    e24_readers = direct_users(funcs, 0xFEBE6E24, "READ")
    need(mirror6af6_readers == [0x387CE], f"6AF6 reader drift: {mirror6af6_readers}")
    need(e22_readers == [0x59448, 0x5CA3A, 0x5D12C] and e24_readers == [0x59448, 0x5CA3A, 0x5D12C],
         f"6E22/24 mirror readers drift: {e22_readers}/{e24_readers}")
    # Term-level semantic closure inside the B6-inactive D0218 / 1C02 observable cone.
    # These names are structural classes, not Toyota OEM labels.  The important preserved
    # negative is that no term below is an independently recovered external lane-target
    # magnitude; their primal values reduce to torque/speed/angle feedback, internal
    # phase/mode state, and ROM calibration.
    d0218_terms = [
        {"cell": "FEBEC43C", "runtime_writer": "0x000C7E36", "classification": "measured steering-torque-shaped assist", "provenance": "C7E36 clamps C472+C45A+C44C against AC6C; the upstream family is the conditioned four-sensor steering-torque chain"},
        {"cell": "FEBEC4C0", "runtime_writer": "0x000C8678", "classification": "torque+speed gain/map term", "provenance": "C8678 maps filtered torque-family C266 through ROM tables and crossfades with C1AA/BF40; exact ordinary selector maps alias"},
        {"cell": "FEBEC3BA", "runtime_writer": "0x000C74AC", "classification": "measured steering-torque-family term", "provenance": "C74AC clamps ABB0+C3A4, both recovered in the torque-filter family"},
        {"cell": "FEBECC2C", "runtime_writer": "0x000D0162", "classification": "internal assist aggregate with ROM slew bound", "provenance": "D0162 sums C3A0+C39C+C41E+C5A8+C53A with constant/ROM-bounded accumulator state"},
        {"cell": "FEBEBF3C", "runtime_writer": "0x000C2B64", "classification": "nonnegative |measured torque| calibration-curve term", "provenance": "C2B64 interpolates C28FC-selected curves over |C128| and scales by ROM gain; route-zero ordinary selector can reach only equivalent normal banks 0/2"},
        {"cell": "FEBECB38", "runtime_writer": "0x000CF2B2", "classification": "angle-domain ramp/return/dither term", "provenance": "CF2B2 slew/median-limits CB08*CB20/0x100; CB08 is recovered from the 0x025 angle-processing family and CB20 is an internal ramp sequencer"},
        {"cell": "FEBEC5EE", "runtime_writer": "0x000C9A84", "classification": "moving-mode monitor/assist term; zero in retained drives", "provenance": "C9A84 scales C5EC by C5B8; retained 0x0D5 s213 source is identically zero"},
        {"cell": "FEBECBE8", "runtime_writer": "0x000CFCD4", "classification": "phase-window angle excitation/return term", "provenance": "CFCD4 clamps CC22+CB64; both are internally sequenced angle/phase waveform state, not an external lane target"},
    ]
    runtime_writer_expect = {
        "FEBEC43C": 0xC7E36, "FEBEC4C0": 0xC8678, "FEBEC3BA": 0xC74AC,
        "FEBECC2C": 0xD0162, "FEBEBF3C": 0xC2B64, "FEBECB38": 0xCF2B2,
        "FEBEC5EE": 0xC9A84, "FEBECBE8": 0xCFCD4,
    }
    for row in d0218_terms:
        cell = int(row["cell"][4:], 16) + 0xFEBE0000 if False else int("0x" + row["cell"][4:], 16)
        # Cell strings already contain the complete hexadecimal address after FEBE.
        cell = int(row["cell"].replace("FEBE", "0xFEBE"), 16)
        need(runtime_writer_expect[row["cell"]] in direct_users(funcs, cell, "WRITE"),
             f"{row['cell']} runtime writer drift")

    out = {
        "schema": "camry-8965f3307000-internal-assist-oracles-v1",
        "target": {"software_id": "8965F3307000", "codeflash_sha256": IMAGE_SHA256,
                   "corpus_function_count": len(funcs)},
        "exact_rdbi_table": {"offset": f"0x{RDBI_OFFSET:05X}", "record_count": RDBI_COUNT},
        "selector_state_direct_rdbi": {
            "cells": selector_direct,
            "denominator": {
                "rdbi_records": len(rdbi),
                "unique_callbacks": len(unique_callbacks),
                "distinct_direct_ram_read_cells_ge_FEBE0000": len(did_read_cells),
                "selector_direct_reader_functions": len(selector_readers),
                "selector_reader_write_targets_intersecting_rdbi_read_cells": len(selector_reader_writes & did_read_cells),
            },
            "classification": (
                "verified canonical direct-reference negative: no exact F33 RDBI callback directly reads FEBEC158/FEBEC156, "
                "and canonical write targets of all direct selector-reader functions do not intersect the 136 direct RDBI "
                "RAM source cells. Pointer/indexed or downstream-derived diagnostic effects remain outside this negative."
            ),
        },
        "d0218_term_proxies": oracle_rows,
        "d0218_term_semantic_closure": {
            "terms": d0218_terms,
            "classification": (
                "recovered/bounded inside the B6-inactive D0218 contribution to the shared CC50/CC62 actuation funnel: "
                "no term is an independently recovered external lane-target magnitude; term values reduce to measured steering "
                "torque, vehicle speed, steering-angle feedback, internal phase/mode state, and ROM calibration. The shared "
                "downstream physical funnel is separately verified below; how stock LTA creates/selects a lane target with B6 "
                "absent remains unresolved upstream of that convergence."
            ),
        },
        "command_value_torque_observable_branch": {
            "pre_slew_value": "FEBECC62",
            "observable_chain": "FEBECC62 -> D0AAE/FEBEAC56 -> BF33E/FEBEE40A -> 5D5E0/FEBE6772 -> DID 0x1C02 Command Value Torque",
            "FEBECC62_canonical_direct_readers": [f"0x{x:08X}" for x in cc62_readers],
            "FEBEAC56_direct_readers": [f"0x{x:08X}" for x in ac56_readers],
            "FEBEE40A_direct_readers": [f"0x{x:08X}" for x in e40a_readers],
            "FEBE6772_direct_readers": [f"0x{x:08X}" for x in v6772_readers],
            "mirror_tail": {
                "0x35C4C": "FEBEE40A -> FEBE6AF6",
                "0x387CE": "FEBE6AF6 -> FEBE6E22/FEBE6E24",
                "FEBE6AF6_direct_readers": [f"0x{x:08X}" for x in mirror6af6_readers],
                "FEBE6E22_direct_readers": [f"0x{x:08X}" for x in e22_readers],
                "FEBE6E24_direct_readers": [f"0x{x:08X}" for x in e24_readers],
            },
            "classification": (
                "verified distinction: AC56/EE40A/FEBE6772 is the diagnostic/model mirror of the pre-slew CC62 value. "
                "Its 6AF6->6E22/6E24 tail terminates in snapshot/report consumers. The physical motor-driving mirror is "
                "the sibling AC54/EE40C branch below. Canonical direct-reader census alone is insufficient to infer that "
                "CC62 is non-actuating because D042C writes CC62 and immediately reuses the same value intra-function to "
                "form CC66."
            ),
        },
        "physical_actuation_funnel": {
            "chain": (
                "D039E/FEBECC50 -> D042C/FEBECC62 -> D042C/FEBECC66 -> D047C/FEBECC64 -> "
                "D0AAE/FEBEAC54 -> BF33E/FEBEE40C -> 35C4C/FEBE6AF4 -> 387BA/FEBE6E0A -> "
                "38502/FEBE6DEC -> 3835E/FEBE6DC8 + 384D8/FEBE6DD6 -> 38162 motor-control transform"
            ),
            "normal_motor_mirror": "0x35C4C normally sets FEBE6AF4=-FEBEE40C; service/limit branches can substitute bounded internal FEBE6AF8 before the same 6AF4 funnel",
            "pre_slew_intra_function_edge": "D042C computes FEBECC62=FEBECC50*FEBEAC5A/0x400, immediately loads it to iVar2, and writes/slew-limits FEBECC66 from the same value",
            "post_slew_override": "D047C normally copies FEBECC66->FEBECC64; if FEBECC98 is nonzero it substitutes clamp(FEBECC94,+/-0x569A), an internally generated return/limit path",
            "writer_sets": {name: [f"0x{x:08X}" for x in writers] for name, writers in funnel_writers.items()},
            "downstream_current_diagnostic_mirror": {
                "cells": ["FEBE6D84", "FEBE6D86"],
                "runtime_copy": "0x00037F16: FEBE6D84=FEBE6DD6; FEBE6D86=FEBE6DC8",
                "direct_writers": {
                    "FEBE6D84": [f"0x{x:08X}" for x in qcmd84_writers],
                    "FEBE6D86": [f"0x{x:08X}" for x in qcmd86_writers],
                },
            },
            "classification": (
                "verified cell-level physical-current convergence through the exact F33 command/current chain. CC62 is a "
                "real pre-slew stage in this funnel; AC56/EE40A/1C02 is its diagnostic mirror, while AC54/EE40C carries "
                "the motor-driving post-slew/override value. No second additive lateral-command injection is recovered "
                "downstream of CC50; special 35C4C and D047C branches are bounded internal limit/override selections. "
                "The remaining stock-LTA contradiction is upstream: how a lane-target/authority state enters or selects "
                "CC50/CC62 while B6 is absent on the captured EPS network."
            ),
        },
        "normal_selector_effect_closure": {
            "base_pointer_table_0xB144C": {"AC3C_0_integrity_fallback": "0x18100", "AC3C_1_healthy": "0x10100"},
            "normal_block_geometry": "four FEBEC156 banks x eight rows x 0x44 bytes = 0x220 bytes per selector bank",
            "healthy_block_sha256": block_hashes["healthy"],
            "fallback_block_sha256": block_hashes["integrity_fallback"],
            "healthy_equivalence": "selector 0 == selector 2 == selector 3 byte-for-byte; selector 1 differs",
            "fallback_equivalence": "selectors 0/1/2/3 all byte-identical",
            "healthy_selector0_vs_1_diff_bytes": sum(a != b for a,b in zip(
                image[0x10100:0x10100+block_size], image[0x10100+block_size:0x10100+2*block_size])),
            "C58B8_C1A4_C1A6_selector_records": c58_records,
            "zero_sig160_state_reduction": (
                "retained drives have sig160/FEBEF050 value 0 route-wide; with FEBEB124==0, B35DC/B372A can "
                "emit FEBEB121 only 0 or 0x22 on the ordinary COM branch; C54A2 maps those to FEBEC158 0 or "
                "0x44 and C5554 maps them to FEBEC156 0 or 2. Those two C28FC normal blocks are identical in "
                "both healthy and fallback banks, so ordinary zero-valued COM selector state cannot change C2B64 curves."
            ),
            "remaining_special_modes": (
                "C54A2 internal 0x55/0x11 and diagnostic 0x66 branches bypass the normal FEBEC156 bank selection "
                "inside C28FC and remain separate internal/fault/diagnostic possibilities."
            ),
            "live_source": str(LIVE_SELECTOR.relative_to(REPO)),
            "classification": (
                "verified static+retained-drive closure: the ordinary COM parameter selector has no effective "
                "C2B64 calibration effect under the route-wide zero sig160 state; the sole distinct normal bank "
                "is FEBEC156=1, which the zero mode value cannot select."
            ),
        },
        "selector_influence_observability": {
            "FEBEC5EE_via_0x1C3E": (
                "C9812 syntactically indexes PTR_DAT_000D39DC[FEBEC156&3], filters/integrates into FEBEC5EC; "
                "C9A84 consumes FEBEC5EC and writes FEBEC5EE; D0D7C/BF3AA then expose its scaled/clamped "
                "proxy at DID 0x1C3E. In exact 8965F3307000 all four selector entries alias 0xB018A, so this "
                "path cannot distinguish FEBEC156 choices in this calibration."
            ),
            "FEBEC4C0_no_direct_term_did": (
                "C8678 syntactically indexes PTR_LAB_000D3630[FEBEC156&3] and selector-strided D3670/D3674 "
                "tables before writing FEBEC4C0, but exact pointer entries alias across all four selector banks "
                "(D3630=0xB1208 x4; D3670 family repeats 0xB1248/0xB121C). No exact F33 RDBI callback directly "
                "reads FEBEC4C0."
            ),
            "exact_alias_tables": {
                "C5EE_D39DC": [f"0x{x:05X}" for x in c5ee_selector_ptrs],
                "C4C0_D3630": [f"0x{x:05X}" for x in c4c0_map_ptrs],
                "C4C0_D3670_family": [f"0x{x:05X}" for x in c4c0_lohi],
            },
            "classification": (
                "Direct selector state remains unexposed by the exact RDBI callback census. 1C3E observes C5EE, "
                "but exact selector-indexed maps alias, so it is a moving-assist term oracle/control rather than a "
                "selector-state discriminator. Selector influence that survives calibration aliasing must be sought in "
                "other internal terms (notably C28FC/C2B64) or blended final command state."
            ),
        },
        "shared_proxy_scale": {
            "intermediate_scale_cell": "FEBEAE3C <- FEBEB140 via BCD66",
            "intermediate_clamp": "+/-0x569A",
            "rdbi_post_scale": "*100/0x80",
            "boundary": (
                "The returned DID value is a scaled/clamped proxy, not the raw D0218 term and not an OEM-named engineering unit."
            ),
        },
        "current_gtsplus_boundary": {
            "source": str(GTS.relative_to(REPO)),
            "named_anchor": {"data_id": "0x1C02", "name": "Command Value Torque"},
            "unnamed_exact_f33_proxy_dids": [r["data_id"] for r in oracle_rows],
        },
        "recommended_passive_oracles": [
            {
                "rank": 1, "data_id": "0x1C38", "reason": "scaled/clamped FEBECB38 proxy; direct visibility into an unresolved nonzero-capable D0218 term"
            },
            {
                "rank": 2, "data_id": "0x1C02", "reason": "Toyota-named Command Value Torque pre-slew model/observable; diagnostic mirror of a value that D042C also feeds into the verified CC66/CC64 physical actuation funnel"
            },
            {
                "rank": 3, "data_id": "0x1C3E", "reason": "scaled/clamped FEBEC5EE proxy; useful control oracle, but exact selector maps alias and retained-drive evidence already bounds this moving-mode term to zero"
            },
        ],
        "production_output_authorized": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
