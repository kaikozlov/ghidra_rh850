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
                "rank": 2, "data_id": "0x1C02", "reason": "Toyota-named final Command Value Torque; blended but target-native downstream command observable"
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
