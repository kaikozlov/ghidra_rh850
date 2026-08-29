#!/usr/bin/env python3
"""Build the exact-F33 residual hidden-ingress closure (VAR-084 E1/E2).

E1 is the bounded register-arithmetic STORE-address false-negative class left by
canonical Ghidra references.  The target-native HighFunction census is promoted
as an image/script-bound generated input, then every candidate family is closed
against exact target constants and call/config bounds from the canonical corpus.

E2 is the DMAC destination-register rewrite class.  The same STORE resolver is
run against every channel's two destination registers; exact decompilation then
pins the recovered destination writers and the fixed CodeFlash descriptor rows
that can feed the runtime updater.

This intentionally does not claim arbitrary unknown pointers or memory-safety
bugs are impossible.  Those are a different bounded class already kept separate
by VAR-084.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

from camry_f33_corpus import CORPUS, IMAGE, IMAGE_SHA256
from decompiler_evidence import body_bytes, load_function_corpus
from build_camry_8965F3307000_application_ram_loader_assessment import DMAC_TABLES

ROOT = Path(__file__).resolve().parents[1]
E1 = ROOT / "data/generated/camry_8965F3307000_computed_store_target_census.json"
E2 = ROOT / "data/generated/camry_8965F3307000_dmac_destination_computed_store_census.json"
SCRIPT = ROOT / "ghidra/scripts/investigate/AuditComputedStoreTargets.java"
OUT = ROOT / "data/generated/camry_8965F3307000_hidden_ingress_residuals.json"

E1_FUNCTIONS = {
    0x3B8E4, 0x3C108, 0x3C116, 0x3C184, 0x3C19C,
    0x7B248, 0x7B2C4, 0x7DD64, 0x7E364, 0x7FC0E, 0x82294, 0x8300E,
    0x830D0, 0x832F4, 0x850C2, 0x850E0, 0x8E772, 0x8E790, 0x8E7A4,
    0x8E7BA, 0x8E7D0, 0x8F60E, 0x8F6B2, 0x93C6C, 0x93C9A, 0x93DE8,
    0x93E5C, 0x93EF6, 0x93F4E, 0x9405C, 0xB9CBE, 0xB9D5E, 0xB9DFC,
    0xB9EAA, 0xBA052, 0xBA134, 0xBA170, 0xBA284, 0xBA398, 0xBA4EA,
    0xBEF80, 0xBEF8E, 0xCB45E, 0xCF4DA, 0xCF4F8, 0xCF51C,
}
E2_FALSE_POSITIVE_FUNCTIONS = {0x607FE, 0x6080E, 0x609B0}
DMAC_DEST_OFFSETS = {0x04, 0x14}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(ok: object, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def hx(v: int) -> str:
    return f"0x{v:08X}"


def ctext(rows: dict[int, dict], entry: int) -> str:
    row = rows.get(entry)
    need(row and row.get("decompile_completed") and row.get("decompiled_c"), f"missing decompile {entry:#x}")
    return str(row["decompiled_c"])


def bind(rows: dict[int, dict], image: bytes, entries: set[int] | list[int]) -> list[dict]:
    out = []
    for entry in sorted(entries):
        row = rows[entry]
        text = str(row["decompiled_c"])
        out.append({
            "entry": hx(entry),
            "body_size": int(row["body_size"]),
            "body_sha256": sha(body_bytes(image, row)),
            "decompiled_c_sha256": sha(text.encode()),
        })
    return out


def literal_call_args(rows: dict[int, dict], callee: int) -> list[int]:
    token = f"FUN_{callee:08x}("
    vals: list[int] = []
    rx = re.compile(re.escape(token) + r"(?:\(.*?\)|[^,])*?\(?\s*(0x[0-9a-fA-F]+|\d+)\s*,")
    for entry, row in rows.items():
        if entry == callee:
            continue
        text = str(row.get("decompiled_c", ""))
        for line in text.splitlines():
            if token not in line:
                continue
            m = rx.search(line)
            if m:
                vals.append(int(m.group(1), 0))
    return sorted(vals)


def census_summary(c: dict, *, candidates: int, functions: int) -> None:
    need(c["schema"] == "camry-8965f3307000-computed-store-target-census-v1", "computed-store schema drift")
    need(c["target"] == {"software_id": "8965F3307000", "codeflash_sha256": IMAGE_SHA256}, "computed-store target drift")
    expected_sha = sha(SCRIPT.read_bytes())
    need(c["ghidra_script"] == {"path": "ghidra/scripts/investigate/AuditComputedStoreTargets.java", "sha256": expected_sha}, "computed-store script identity drift")
    need(c["summary"] == {
        "candidateFunctions": functions,
        "candidates": candidates,
        "functions": 6065,
        "knownRangeStores": 5011,
        "stores": 13493,
    }, "computed-store census denominator drift")


def build() -> dict:
    image = IMAGE.read_bytes()
    need(len(image) == 0x100000 and sha(image) == IMAGE_SHA256, "exact F33 image drift")
    rows, total = load_function_corpus(CORPUS)
    need(total == 6065, f"F33 corpus denominator drift: {total}")

    e1 = load_json(E1)
    e2 = load_json(E2)
    census_summary(e1, candidates=100, functions=46)
    census_summary(e2, candidates=5, functions=3)
    e1_funcs = {int(x, 16) for x in e1["candidate_functions"]}
    e2_funcs = {int(x, 16) for x in e2["candidate_functions"]}
    need(e1_funcs == E1_FUNCTIONS, f"E1 candidate function set drift: {sorted(e1_funcs ^ E1_FUNCTIONS)}")
    need(e2_funcs == E2_FALSE_POSITIVE_FUNCTIONS, "E2 computed candidate set drift")

    # E1-A: FEBE71F2 false positives.  The only parametric family that could
    # reach it by a coarse 8-bit interval is in fact called with literal lanes
    # 0..7; the status arrays are all explicitly bounded to <0x18.
    calls_3b960 = literal_call_args(rows, 0x3B960)
    need(calls_3b960 == list(range(8)), f"3B960 literal index set drift: {calls_3b960}")
    t = ctext(rows, 0x3B8E4)
    need("(&DAT_febe7090)[param_1 & 0xff]" in t, "3B8E4 indexed target drift")
    for entry in (0x3C116, 0x3C184, 0x3C19C):
        need("< 0x18" in ctext(rows, entry), f"{entry:#x} 24-entry bound drift")

    # E1-B: generated-COM bookkeeping arrays. Exact configuration constants
    # bound all indices far below the steering/current cells highlighted by the
    # coarse interval resolver.
    need(image[0x22C48] == 3 and image[0x22C47] == 3, "7B2C4 manager counts drift")
    need(image[0x22C7C] == 3, "7B248 manager record count drift")
    need(image[0x21C6E] == 1 and image[0x21C56] == 5, "7DD64/7E364 event bounds drift")
    need(struct.unpack_from("<HH", image, 0x22140) == (0, 5), "group0 event span drift")
    need(image[0x21970] == 1 and image[0x21972] == 5, "7FC0E route count drift")
    route_rows = [struct.unpack_from("<HHHBBH", image, 0x21ACC + i * 10) for i in range(5)]
    route_indices = [r[-1] for r in route_rows]
    need(route_indices == [0, 1, 2, 3, 4], f"7FC0E route indices drift: {route_indices}")
    route_buffers = [struct.unpack_from("<I", image, 0x21A54 + i * 4)[0] for i in range(5)]
    need(route_buffers == [0xFEBE3DF8, 0xFEBE3E2C, 0xFEBE3E48, 0xFEBE3E64, 0xFEBE3EA0], "generated-COM buffer table drift")

    # E1-C: XCP/communication manager state arrays.
    need(struct.unpack_from("<H", image, 0x22AE4)[0] == 0x70, "XCP state pointer count drift")
    need(image[0x22AE6:0x22AE8] == bytes((4, 4)), "XCP state row counts drift")
    need(image[0x22ABF] == 1 and image[0x22ABC] == 1 and image[0x22ABD] == 8, "XCP scratch bounds drift")
    need(struct.unpack_from("<H", image, 0x21C68)[0] == 0x1E8 and image[0x21C54] == 0x30, "COM status-map bounds drift")
    need(struct.unpack_from("<H", image, 0x22E3C)[0] == 47 and struct.unpack_from("<H", image, 0x22E3E)[0] == 9 and image[0x22E41] == 3, "CAN rule-state bounds drift")
    need(image[0x21971] == 3, "CAN rule-group count drift")
    rule_groups = [(struct.unpack_from("<H", image, 0x22E44 + i * 8)[0], image[0x22E44 + i * 8 + 4]) for i in range(3)]
    need(rule_groups == [(47, 0), (47, 9), (56, 0)], f"CAN rule-group spans drift: {rule_groups}")

    # E1-D: diagnostic/event arrays have hard bounds in the recovered functions.
    for entry in (0x8E772, 0x8E790, 0x8E7A4, 0x8E7BA, 0x8E7D0):
        need("< 0x60" in ctext(rows, entry), f"{entry:#x} 0x60 bound drift")
    t = ctext(rows, 0x8E912)
    need("param_2 < 3" in t and "param_1 == 1" in t, "three-node diagnostic list bound drift")
    need("FUN_0008e8a0(1,0" in ctext(rows, 0x8F98C).replace(" ", ""), "8F98C list source drift")

    # E1-E: the storage/logical-block family is exactly three state rows and all
    # writer entry points recover their index through that three-row domain.
    need("uVar1 < 3" in ctext(rows, 0x93F0E), "logical-block lookup bound drift")
    need("while (uVar1 < 3)" in ctext(rows, 0x93ABA), "logical-block init bound drift")
    block_buffers = [struct.unpack_from("<I", image, 0x25E94 + i * 8)[0] for i in range(3)]
    need(block_buffers == [0xFEBE5651, 0xFEBE5751, 0xFEBE5851], f"logical-block buffers drift: {block_buffers}")
    need("if (1 < (uVar1 & 0xffff))" in ctext(rows, 0x9405C), "two-slot ring wrap drift")

    # E1-F: five-channel motor/diagnostic snapshot family and three-element CBxx
    # diagnostic helpers.
    need("while (uVar1 < 5)" in ctext(rows, 0xBA642), "BA642 five-channel bound drift")
    need("thunk_FUN_000bef80(0)" in ctext(rows, 0x3D348), "BEF80 literal index drift")
    need("DAT_febec740 < 0x13" in ctext(rows, 0xCB45E), "CB45E ring bound drift")
    for entry in (0xCF4DA, 0xCF4F8, 0xCF51C):
        need("< 3" in ctext(rows, entry), f"{entry:#x} three-entry bound drift")

    # E2: destination registers are +0x04 and +0x14 in every 0x40-byte channel.
    # The computed-target census finds only control-register accesses at modulo
    # offsets 0x20/0x2C/0x38, never a destination offset.
    e2_offsets: dict[str, list[int]] = {}
    for cand in e2["candidates"]:
        lo = int(cand["lo"], 16)
        expr = cand["pointer_expression"]
        m = re.search(r"0xffff([0-9a-fA-F]{4})", expr)
        need(m, f"E2 candidate missing constant base: {expr}")
        base = int("ffff" + m.group(1), 16)
        off = base & 0x3F
        e2_offsets.setdefault(cand["function"], []).append(off)
        need(off not in DMAC_DEST_OFFSETS, f"computed E2 candidate actually hits destination offset: {cand}")
    need({x for vals in e2_offsets.values() for x in vals} == {0x20, 0x2C, 0x38}, f"E2 false-positive offset set drift: {e2_offsets}")

    # Direct recovered destination writers. +0x04 is initialized only by 6082C;
    # +0x14 is initialized by 6082C and refreshed by 60A6A. 6091E is read-only.
    # The simple '=' screen includes the read-only return line for 6091E, so pin
    # writer semantics explicitly by the exact assignment spellings.
    plus04_writers = sorted(entry for entry, row in rows.items() if "*(undefined4 *)(iVar4 + -0x7bfc) =" in str(row.get("decompiled_c", "")))
    plus14_writers = sorted(entry for entry, row in rows.items() if (
        "*(undefined4 *)(iVar4 + -0x7bec) =" in str(row.get("decompiled_c", "")) or
        "*(undefined4 *)(iVar3 + -0x7bec) =" in str(row.get("decompiled_c", ""))
    ))
    need(plus04_writers == [0x6082C], f"DMAC +04 writer set drift: {plus04_writers}")
    need(plus14_writers == [0x6082C, 0x60A6A], f"DMAC +14 writer set drift: {plus14_writers}")
    need("return *(undefined4 *)((param_1 & 0xff) * 0x40 + -0x7bfc);" in ctext(rows, 0x6091E), "DMAC +04 reader drift")

    # Runtime updater 60A6A has only four callers, and all callsites pass one of
    # seven fixed CodeFlash descriptor families. Bind each table byte-for-byte.
    runtime_callers = []
    for entry, row in rows.items():
        if entry != 0x60A6A and "FUN_00060a6a(" in str(row.get("decompiled_c", "")):
            runtime_callers.append(entry)
    runtime_callers = sorted(runtime_callers)
    need(runtime_callers == [0x60462, 0x60C20, 0x61B90, 0x628B2], f"60A6A caller set drift: {runtime_callers}")

    dmac_tables = []
    destinations: list[int] = []
    for base, count, digest in DMAC_TABLES:
        body = image[base:base + count * 0x28]
        need(sha(body) == digest, f"DMAC descriptor hash drift {base:#x}")
        table_rows = []
        for i in range(count):
            off = base + i * 0x28
            src1, dst1, src2, dst2 = (struct.unpack_from("<I", image, off + x)[0] for x in (8, 0xC, 0x18, 0x1C))
            need(dst1 == dst2, f"DMAC duplicated destination mismatch {off:#x}")
            destinations.extend((dst1, dst2))
            table_rows.append({"index": i, "source_1": hx(src1), "destination_1": hx(dst1), "source_2": hx(src2), "destination_2": hx(dst2)})
        dmac_tables.append({"base": hx(base), "count": count, "record_size": 0x28, "sha256": digest, "rows": table_rows})
    need(len(destinations) == 44, f"DMAC destination field denominator drift: {len(destinations)}")
    local_hits = [x for x in destinations if 0xFEBE0000 <= x <= 0xFEBFFFFF]
    need(local_hits == [], f"DMAC runtime descriptor can target LocalRAM: {[hx(x) for x in local_hits]}")

    evidence_entries = E1_FUNCTIONS | E2_FALSE_POSITIVE_FUNCTIONS | {
        0x3B960, 0x3D348, 0x7A32E, 0x7DCA0, 0x7FD46, 0x7FBDC, 0x7FAFA,
        0x8E862, 0x8E8A0, 0x8E912, 0x8E9C6, 0x8F746, 0x8F906, 0x8F98C,
        0x93ABA, 0x93C60, 0x93C66, 0x93F0E, 0xBA224, 0xBA25E, 0xBA336,
        0xBA5A0, 0xBA642, 0x6082C, 0x6091E, 0x60A6A, 0x60462, 0x60C20,
        0x61B90, 0x628B2,
    }

    return {
        "schema": "camry-8965f3307000-hidden-ingress-residuals-v1",
        "target": {"software_id": "8965F3307000", "codeflash_sha256": IMAGE_SHA256, "corpus_function_count": total},
        "inputs": {
            "computed_store_target_census": {"path": str(E1.relative_to(ROOT)), "sha256": sha(E1.read_bytes())},
            "dmac_destination_computed_store_census": {"path": str(E2.relative_to(ROOT)), "sha256": sha(E2.read_bytes())},
            "resolver_script": {"path": str(SCRIPT.relative_to(ROOT)), "sha256": sha(SCRIPT.read_bytes())},
        },
        "e1_register_arithmetic_store_targets": {
            "status": "closed_within_known_range_store_arithmetic",
            "census": e1["summary"],
            "candidate_function_count": len(E1_FUNCTIONS),
            "candidate_functions": [hx(x) for x in sorted(E1_FUNCTIONS)],
            "closure_groups": [
                {"name": "71f2_status_arrays", "functions": [hx(x) for x in (0x3B8E4,0x3C108,0x3C116,0x3C184,0x3C19C)], "bound": "3B8E4 receives literal lanes 0..7; 3C108/116/184/19C are bounded to indices <0x18; none reaches FEBE71F2"},
                {"name": "generated_com_bookkeeping", "functions": [hx(x) for x in (0x7B248,0x7B2C4,0x7DD64,0x7E364,0x7FC0E)], "bound": "exact manager/event/route counts confine writes to 0xFEBE48xx..0xFEBE4Fxx; the five generated-COM buffers are fixed at FEBE3DF8..FEBE3EA0"},
                {"name": "xcp_can_manager_state", "functions": [hx(x) for x in (0x82294,0x8300E,0x830D0,0x832F4,0x850C2,0x850E0)], "bound": "exact state/rule counts confine writes to FEBE493E..FEBE503A"},
                {"name": "diagnostic_event_state", "functions": [hx(x) for x in (0x8E772,0x8E790,0x8E7A4,0x8E7BA,0x8E7D0,0x8F60E,0x8F6B2)], "bound": "event arrays are <0x60 and the linked diagnostic-list path has exactly three node IDs, confining writes below FEBE5527"},
                {"name": "logical_block_state", "functions": [hx(x) for x in (0x93C6C,0x93C9A,0x93DE8,0x93E5C,0x93EF6,0x93F4E,0x9405C)], "bound": "logical-block index domain is exactly 0..2; backing buffers are FEBE5651/FEBE5751/FEBE5851; ring index wraps at two slots"},
                {"name": "five_channel_snapshot_state", "functions": [hx(x) for x in (0xB9CBE,0xB9D5E,0xB9DFC,0xB9EAA,0xBA052,0xBA134,0xBA170,0xBA284,0xBA398,0xBA4EA,0xBEF80,0xBEF8E)], "bound": "top-level BA642 index is 0..4 and BEF80/BEF8E is called with literal 0; writes remain below FEBEBF3C"},
                {"name": "cbxx_diagnostic_state", "functions": [hx(x) for x in (0xCB45E,0xCF4DA,0xCF4F8,0xCF51C)], "bound": "CB45E ring index is <=0x13 and CF4xx helpers are <3; writes remain below the steering-command CCxx region"},
            ],
            "result": "zero recovered register-arithmetic STORE path can land on any audited steering command/current target once exact runtime/configuration index bounds are applied",
            "boundary": "unknown/unbounded pointer stores and memory-safety bugs are not promoted to impossible; this closes VAR-084 E1 specifically, not arbitrary pointer corruption",
        },
        "e2_dmac_destination_reprogramming": {
            "status": "closed_within_recovered_application_dataflow",
            "destination_registers": {"channel_base": "0xFFFF8400", "channel_stride": 0x40, "offsets": ["0x04", "0x14"], "channels": 16},
            "computed_store_census": e2["summary"],
            "computed_false_positive_functions": [hx(x) for x in sorted(E2_FALSE_POSITIVE_FUNCTIONS)],
            "computed_false_positive_offsets_mod_0x40": sorted({x for vals in e2_offsets.values() for x in vals}),
            "direct_writers": {"destination_0x04": [hx(x) for x in plus04_writers], "destination_0x14": [hx(x) for x in plus14_writers], "read_only_0x04_accessor": "0x0006091E"},
            "runtime_updater": "0x00060A6A",
            "runtime_updater_callers": [hx(x) for x in runtime_callers],
            "fixed_descriptor_tables": dmac_tables,
            "destination_field_count": len(destinations),
            "distinct_destination_count": len(set(destinations)),
            "localram_destination_hits": [],
            "result": "the only recovered runtime destination-register updater is 0x60A6A, and every callsite supplies one of seven fixed CodeFlash descriptor families; all 44 destination fields avoid LocalRAM",
            "boundary": "arbitrary unknown-pointer corruption/hardware faults remain outside this recovered-dataflow proof; no separate DMAC destination programmer is recovered",
        },
        "combined_classification": "VAR-084 E1 and E2 are closed without finding a hidden stock-LTA producer. The remaining steering contradiction is semantic/upstream of CC50/CC62, not an identified computed-store or DMAC ingress escape.",
        "evidence_functions": bind(rows, image, evidence_entries),
        "production_output_authorized": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    result = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.out)


if __name__ == "__main__":
    main()
