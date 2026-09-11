#!/usr/bin/env python3
"""Build exact-F33 pre-fault memory-safety/recovery evidence.

This is deliberately scoped to code that can run before (or independently of)
the broken 0x7A272 foreground transfer.  It records one real RS-CANFD stale
stack ingestion condition and the static closures that currently prevent it
from becoming a write/control-flow recovery primitive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from tools.targets.camry.support.camry_f33_corpus import IMAGE, IMAGE_SHA256

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/generated/camry_8965F3307000_prefault_memory_safety.json"
CONE = ROOT / "data/generated/camry_8965F3307000_prefault_store_audit.json"
STORE_CENSUS = ROOT / "data/generated/camry_8965F3307000_computed_store_target_census.json"
DECOMP = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"

CRITICAL_CELLS = [
    0xFEBE3DF0, 0xFEBE3DF1, 0xFEBE3DF2, 0xFEBE3DF3, 0xFEBE3DF4, 0xFEBE3DF5,
    # Recovered lower-RAM indirect-call source cells from the first-class
    # application RAM-loader/control-transfer census.  Some consumers execute
    # later than the fault, but including all of them makes this intersection a
    # stronger write-to-control-object negative.
    0xFEBE5628, 0xFEBF0FD0, 0xFEBF117C, 0xFEBF1180, 0xFEBF1194, 0xFEBF1198,
    0xFEBF131C, 0xFEBF1320, 0xFEBF1324, 0xFEBF6B04,
]
STACK_RANGES = [
    (0xFEBE1700, 0xFEBE2020, "saved-context / IRQ + initial application stack"),
    (0xFEBE0000, 0xFEBE2200, "lower LocalRAM through initial application stack"),
]


def u16(b: bytes, off: int) -> int:
    return struct.unpack_from("<H", b, off)[0]


def u32(b: bytes, off: int) -> int:
    return struct.unpack_from("<I", b, off)[0]


def need(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def fn_decomp(addr: int) -> str:
    key = f"0x{addr:08x}"
    for line in DECOMP.read_text().splitlines():
        row = json.loads(line)
        if row.get("record") == "function" and row.get("entry_addr", "").lower() == key:
            return row.get("decompiled_c", "")
    raise ValueError(f"missing decompilation for 0x{addr:X}")


def overlaps(lo: int, hi: int, point: int) -> bool:
    return lo <= point <= hi


def build() -> dict:
    image = IMAGE.read_bytes()
    need(len(image) == 0x100000, "exact F33 image size drift")
    need(hashlib.sha256(image).hexdigest() == IMAGE_SHA256, "exact F33 image hash drift")

    cone = load(CONE)
    census = load(STORE_CENSUS)
    need(cone["schema"] == "camry-8965f3307000-prefault-store-audit-v1", "call-cone evidence drift")
    need(cone["summary"] == {"computed": 268, "functions": 151, "ranged": 37, "stores": 275, "unknown": 231}, "call-cone denominator drift")
    need(cone["pointer_parameter_dependent"]["store_count"] == 209, "parameter-store denominator drift")
    need(cone["pointer_parameter_dependent"]["function_count"] == 52, "parameter-store function denominator drift")
    cone_funcs = {int(x, 16) for x in cone["function_entries"]}

    # Whole-image statically ranged STORE candidates whose recovered interval can
    # touch any recovery-critical global cell, then intersect with the functions
    # that actually execute in the pre-fault/ISR cone.
    critical_rows = []
    for row in census["candidates"]:
        lo, hi = int(row["lo"], 16), int(row["hi"], 16)
        hits = [x for x in CRITICAL_CELLS if overlaps(lo, hi, x)]
        if hits:
            critical_rows.append((int(row["function"], 16), row, hits))
    cone_critical = [(fn, row, hits) for fn, row, hits in critical_rows if fn in cone_funcs]
    need(len(critical_rows) == 62, f"critical whole-image candidate denominator drift: {len(critical_rows)}")
    need({fn for fn, _, _ in cone_critical} == {0x8E7BA}, f"pre-fault critical intersection drift: {sorted({fn for fn,_,_ in cone_critical})}")
    e7ba = fn_decomp(0x8E7BA)
    need("(param_1 & 0xffff) < 0x60" in e7ba and "DAT_febe5398" in e7ba, "0x8E7BA exact bound drift")

    stack_intersections = []
    for lo0, hi0, label in STACK_RANGES:
        rows = []
        for row in census["candidates"]:
            lo, hi = int(row["lo"], 16), int(row["hi"], 16)
            if not (hi < lo0 or lo > hi0):
                rows.append(row)
        need(not rows, f"known-range computed STORE now overlaps {label}")
        stack_intersections.append({"label": label, "lo": f"0x{lo0:08X}", "hi": f"0x{hi0:08X}", "known_range_store_count": 0})

    # Prove which RS-CANFD configuration is live in application mode.  The older
    # fixed writer at 0x396C belongs to the bootloader loop; the application
    # startup reaches the table-driven writer at 0x84570 before 0x7A132 commits
    # FEBE3DF2=FE01.
    app_startup = fn_decomp(0x666BC)
    app_root = fn_decomp(0x7A132)
    app_comm = fn_decomp(0x79DFA)
    app_rscfd = fn_decomp(0x83F3E)
    app_driver = fn_decomp(0x84652)
    app_apply = fn_decomp(0x84570)
    boot_loop = fn_decomp(0x1398)
    boot_init = fn_decomp(0x1338)
    boot_rscfd = fn_decomp(0x3B3C)
    boot_gcfg = fn_decomp(0x396C)
    need("FUN_0007a132()" in app_startup, "application startup -> 7A132 edge drift")
    need("FUN_00079dfa()" in app_root and "0xfe01" in app_root, "7A132 application init/order drift")
    need("FUN_00083f3e(0)" in app_comm, "79DFA -> 83F3E edge drift")
    need("FUN_00084652()" in app_rscfd, "83F3E -> 84652 edge drift")
    need("FUN_00084570()" in app_driver, "84652 -> 84570 edge drift")
    need("PTR_DAT_0002303c = DAT_00022e80" in app_apply, "application GCFG writer drift")
    need("FUN_00001338()" in boot_loop and "FUN_00003b3c()" in boot_init and "FUN_0000396c()" in boot_rscfd, "boot RSCFD chain drift")
    need("DAT_ffd20084 = 0xffff0000" in boot_gcfg, "boot GCFG constant drift")

    # Exact RS-CANFD global configuration. Renesas P1M-E manual table 17.106:
    # bit5 CMPOC, bit2 DRE, bit1 DCE.
    gcfg = u32(image, 0x22E80)
    need(gcfg == 0xFFFF0020, f"RSCFD GCFG source drift: 0x{gcfg:08X}")
    need(bool(gcfg & (1 << 5)) and not (gcfg & (1 << 2)) and not (gcfg & (1 << 1)), "GCFG overflow/DLC mode drift")
    dlc_table = list(image[0x22E28:0x22E38])
    need(dlc_table == [0,1,2,3,4,5,6,7,8,12,16,20,24,32,48,64], "DLC decode table drift")
    rfifo_payload_words = list(image[0x22EB4:0x22EBC])
    need(rfifo_payload_words[1] == 8, "RFIFO1 physical payload geometry drift")
    cfifo0_payload_words = image[0x22EB7]
    need(cfifo0_payload_words == 2, "diagnostic CFIFO physical payload geometry drift")

    # 47 exact acceptance rules, 16 bytes each: GAFLID / GAFLM-ish metadata /
    # GAFLP1 / trailing word. Rules 43-45 are the three diagnostic IDs and use
    # Tx/Rx FIFO5 (bit 13 => 0x2000); rule46 is extended XCP on RFIFO1 (bit1).
    rules = [struct.unpack_from("<4I", image, 0x230B8 + i * 16) for i in range(47)]
    need([rules[i][0] for i in (43,44,45)] == [0x7A1,0x777,0x7A0], "diagnostic acceptance IDs drift")
    need([rules[i][2] for i in (43,44,45)] == [0x2000,0x2000,0x2000], "diagnostic CFIFO routing drift")
    need(rules[46][0] == 0x9FDC0002 and rules[46][2] == 0x0002, "XCP RFIFO1 routing drift")

    # Generated-COM consumer: first 48 records are the exact PDU table.
    pdu_lengths = [u16(image, 0x226C0 + i * 8 + 4) for i in range(48)]
    need(max(pdu_lengths) == 32, "class-0 COM max PDU length drift")
    need(sum(1 for x in pdu_lengths if x == 32) == 5, "class-0 32-byte PDU count drift")

    # The strongest remaining stack-overwrite-looking helper is 0x8549E.  It
    # rounds a queued logical byte length through two CodeFlash tables before
    # copying into a 64-byte local.  The receive producer limits the logical
    # domain to the hardware DLC decode (0..64); both tables cover that entire
    # domain and the rounded-copy table never exceeds 64.
    fd_len_to_dlc = list(image[0x2345A:0x2345A + 65])
    fd_len_to_copy = list(image[0x2349B:0x2349B + 65])
    need(fd_len_to_dlc[:9] == list(range(9)), "FD length->DLC short domain drift")
    need(fd_len_to_dlc[64] == 15 and max(fd_len_to_dlc) == 15, "FD length->DLC table bound drift")
    need(fd_len_to_copy[0] == 0 and fd_len_to_copy[64] == 64 and max(fd_len_to_copy) == 64, "FD rounded copy table bound drift")
    for n in range(65):
        expected = 0 if n == 0 else ((n + 3) // 4) * 4
        need(fd_len_to_copy[n] == expected, f"FD rounded-copy table drift at length {n}")

    # 0x80884's six-way callback bitmap looks wire-adjacent because it is stored
    # in the RX record header.  Exact 0x80B42 sources it from the fixed per-label
    # table at 0x219DC, after 0x83D14 derives the label from configured FIFO/rule
    # geometry.  Preserve the exact table and callback vector as evidence that
    # payload bytes do not become an indirect-call selector.
    callback_masks = list(image[0x219DC:0x219DC + image[0x21964]])
    callback_vector = [u32(image, 0x21A24 + i * 4) for i in range(6)]
    need(image[0x21964] == len(callback_masks), "acceptance-label count drift")
    need(all(x < 0x40 for x in callback_masks), "callback mask exceeds six-bit fanout")
    need(all(0 < x < len(image) for x in callback_vector), "callback vector target drift")

    # XCP staging cap used by 0x830D0.
    xcp_cap = image[0x22ABD]
    need(xcp_cap == 8, "XCP staging cap drift")

    # Exact transport configuration records selected by 0x7A5C2/0x7A620.
    # The strided 0x7B18A/0x7BB0E writers use record[1] as their state-slot
    # index; it is therefore configuration-derived, not a payload byte.
    transport_desc_base = u32(image, 0x22C70)
    transport_desc_count = image[0x22C7C]
    need(transport_desc_base == 0x22C4C and transport_desc_count == 3, "transport descriptor root drift")
    transport_records: list[dict[str, int | str]] = []
    for d in range(transport_desc_count):
        da = transport_desc_base + d * 12
        p0, p1 = u32(image, da), u32(image, da + 4)
        # 0x7A5C2 walks p0 using descriptor byte +10; 0x7A620 walks p1 using +9.
        for role, base, count in (("p0", p0, image[da + 10]), ("p1", p1, image[da + 9])):
            for i in range(count):
                ra = base + i * 0x20
                transport_records.append({"descriptor": d, "role": role, "address": ra, "state_index": image[ra + 1]})
    transport_state_indices = sorted({int(r["state_index"]) for r in transport_records})
    need(transport_state_indices == [0, 2], f"transport state-index domain drift: {transport_state_indices}")
    need(image[0x22C48] == 3, "transport state-slot count drift")

    # Exact controller-0 route configuration selected by 0x803B0/0x8043C/
    # 0x806A4/0x807D8.  Five fixed 10-byte rows carry state indices 0..4.
    route_count = image[0x21972]
    route_cfg_base = u32(image, 0x218E4)
    route_byte_state_base = u32(image, 0x218E8)
    need(route_count == 5 and route_cfg_base == 0x21ACC and route_byte_state_base == 0xFEBE3E94, "route-manager geometry drift")
    route_state_indices = [u16(image, route_cfg_base + i * 10 + 8) for i in range(route_count)]
    need(route_state_indices == [0,1,2,3,4], f"route state-index domain drift: {route_state_indices}")

    # Queue geometry. 0x80A4A treats this as a word count, not bytes.  The
    # backing pointer is fixed per controller; exact F33 configures one.
    queue_capacity_words = u16(image, 0x21966)
    queue_base = u32(image, 0x21904)
    need(image[0x21970] == 1, "configured controller count drift")
    need(queue_capacity_words == 0x228 and queue_base == 0xFEBE4038, "RX software queue geometry drift")
    queue_end = queue_base + queue_capacity_words * 4 - 1
    need(queue_end == 0xFEBE48D7, "RX software queue end drift")

    # Communication-manager dimensions that over-approximate to FEBE3DF2 in a
    # coarse range solver but make index 2 impossible in the exact calibration.
    comm_dims = {
        "DAT_2183C": image[0x2183C],
        "DAT_2183D": image[0x2183D],
        "DAT_21864": image[0x21864],
        "DAT_21865": image[0x21865],
        "DAT_21BE1": image[0x21BE1],
    }
    need(comm_dims == {"DAT_2183C":1,"DAT_2183D":0,"DAT_21864":2,"DAT_21865":1,"DAT_21BE1":1}, f"communication dimensions drift: {comm_dims}")

    # Unbounded-looking route-slot writers start above the guard. Even allowing
    # a full 8-bit slot, they cannot write backwards into FEBE3DF2 or reach FEBF.
    route_slot_base = u32(image, 0x21934)
    need(route_slot_base == 0xFEBE3E80, "route-slot base drift")
    route_slot_max = route_slot_base + 0xFF * 2

    # DCM StartOfReception/CopyRxData uses three fixed 0x100-byte buffers.
    dcm = []
    for i in range(3):
        cap = u32(image, 0x25E90 + i * 8)
        ptr = u32(image, 0x25E94 + i * 8)
        route = u16(image, 0x25EF2 + i * 6)
        dcm.append({"channel": i, "route": route, "capacity": cap, "start": ptr, "end_exclusive": ptr + cap})
    need([(x["route"],x["capacity"],x["start"]) for x in dcm] == [
        (2,0x100,0xFEBE5651),(1,0x100,0xFEBE5751),(3,0x100,0xFEBE5851)
    ], f"DCM buffer geometry drift: {dcm}")

    # RSCFD pointer parameters in 0x83xxx..0x85xxx resolve through this exact
    # one-controller descriptor row; every recovered entry is MMIO in 0xFFD2....
    rscfd_ptrs = [u32(image, a) for a in range(0x22EDC, 0x22F4C, 4)]
    need(len(rscfd_ptrs) == 28 and all((x & 0xFFFF0000) == 0xFFD20000 for x in rscfd_ptrs), "RSCFD MMIO pointer row drift")

    return {
        "schema": "camry-8965f3307000-prefault-memory-safety-v1",
        "target": {"software_id":"8965F3307000", "codeflash_sha256":IMAGE_SHA256},
        "recovery_target": {
            "hook_guard": "0xFEBE3DF2",
            "bad_hook_callsite": "0x0007A272",
            "goal": "obtain a write/control-flow primitive before or independently of the poisoned foreground transfer",
        },
        "active_rscfd_configuration": {
            "application_chain": ["0x000666BC", "0x0007A132", "0x00079DFA", "0x00083F3E", "0x00084652", "0x00084570", "0xFFD20084"],
            "application_gcfg_source": "CodeFlash[0x22E80]",
            "application_gcfg": f"0x{gcfg:08X}",
            "application_order": "0x7A132 reaches 0x84570 during startup before its final FEBE3DF2=FE01 write",
            "bootloader_chain": ["0x00001398", "0x00001338", "0x00003B3C", "0x0000396C", "0xFFD20084"],
            "bootloader_gcfg": "0xFFFF0000",
            "boundary": "the old 0x39xx fixed writer is bootloader-only; application-mode receive behavior uses the 0x22E80 table value",
        },
        "rscfd_oversized_fd": {
            "gcfg_source": "0x00022E80",
            "gcfg": f"0x{gcfg:08X}",
            "manual_decode": {"CMPOC":1,"DRE":0,"DCE":0},
            "manual_semantics": "oversized message is stored with excess payload discarded; received DLC is retained; DLC filtering disabled",
            "dlc_table": dlc_table,
            "rfifo1": {"payload_words":rfifo_payload_words[1],"physical_bytes":rfifo_payload_words[1]*4,"max_reported_bytes":64,"max_stale_bytes":64-rfifo_payload_words[1]*4},
            "diagnostic_cfifo": {"payload_words":cfifo0_payload_words,"physical_bytes":cfifo0_payload_words*4,"max_reported_bytes":64,"max_stale_bytes":64-cfifo0_payload_words*4},
            "classification": "verified source over-read / stale ISR-stack ingestion into software RX records; attacker control of stale bytes is not established",
        },
        "acceptance_routing": {
            "rule_count":47,
            "diagnostic_rules":[{"rule":i,"can_id":f"0x{rules[i][0]:X}","gaflp1":f"0x{rules[i][2]:08X}"} for i in (43,44,45)],
            "xcp_rule":{"rule":46,"can_id":"0x1FDC0002","raw_gaflid":"0x9FDC0002","gaflp1":"0x00000002"},
        },
        "fd_length_normalization": {
            "producer_domain": "0..64 bytes from the exact hardware DLC decode / 0x80A4A RX record",
            "length_to_dlc_table": "0x0002345A",
            "rounded_copy_table": "0x0002349B",
            "length_to_dlc": fd_len_to_dlc,
            "rounded_copy_bytes": fd_len_to_copy,
            "local_buffer_bytes": 64,
            "max_copy_bytes": max(fd_len_to_copy),
            "sink": "0x8549E local_54[64] before 0x85286/0x852FE",
            "classification": "complete 0..64 table domain; no stack overwrite from a valid RX record length",
        },
        "callback_selector_provenance": {
            "producer": "0x80B42",
            "consumer": "0x80884",
            "mask_table": "0x000219DC",
            "mask_count": len(callback_masks),
            "masks": callback_masks,
            "callback_vector_table": "0x00021A24",
            "callback_vector": [f"0x{x:08X}" for x in callback_vector],
            "classification": "six-way indirect-call selector is fixed per acceptance label; CAN payload bytes do not supply the mask or callback target",
        },
        "consumer_closure": {
            "class0_com":{"pdu_count":48,"max_configured_length":max(pdu_lengths),"length32_count":sum(1 for x in pdu_lengths if x==32),"effect":"0x7D72C copies min(received_len, configured_len), so RFIFO phantom bytes 32..63 are never imported"},
            "xcp":{"staging_cap":xcp_cap,"effect":"0x830D0 rejects length > 8 before copying to FEBE4C34"},
            "isotp":{"effect":"upstream dispatch reads PCI byte0 only; SF/FF/CF length validation rejects oversized descriptors before phantom bytes are consumed; FC accepts len>=8 but reads only bytes0..2"},
        },
        "transport_state_provenance": {
            "descriptor_root": "0x00022C70",
            "descriptor_base": f"0x{transport_desc_base:08X}",
            "descriptor_count": transport_desc_count,
            "reachable_records": [{"descriptor":r["descriptor"],"role":r["role"],"address":f"0x{int(r['address']):08X}","state_index":r["state_index"]} for r in transport_records],
            "state_indices": transport_state_indices,
            "state_slot_count": image[0x22C48],
            "classification": "0x7B18A/0x7BB0E state-slot index comes from fixed transport record[1], not CAN payload",
        },
        "route_manager_provenance": {
            "route_count": route_count,
            "route_config_base": f"0x{route_cfg_base:08X}",
            "route_byte_state_base": f"0x{route_byte_state_base:08X}",
            "state_indices": route_state_indices,
            "state_word_range": "0xFEBE48DA..0xFEBE48F5",
            "state_flag_range": "0xFEBE4909..0xFEBE490D",
            "classification": "route-manager computed destinations are configuration-indexed 0..4",
        },
        "software_queue":{"base":f"0x{queue_base:08X}","end_inclusive":f"0x{queue_end:08X}","capacity_words":queue_capacity_words,"capacity_bytes":queue_capacity_words*4,"fd_record_words_for_len64":19,"critical_section":"0x7A2DA -> 0x98B8A -> 0x6A45E installs IMSR 0xFF00; 0x7A2E8 -> 0x6A4C4 restores","classification":"bounded 16-bit word-index ring; no wrap/next-record overwrite recovered"},
        "dcm_copy":{"buffers":[{"channel":x["channel"],"route":x["route"],"capacity":f"0x{x['capacity']:X}","start":f"0x{x['start']:08X}","end_exclusive":f"0x{x['end_exclusive']:08X}"} for x in dcm],"classification":"0x92152 requires chunk_len <= remaining before 0x93DE8 advances fixed configured destination pointer"},
        "computed_store_audit": {
            "call_cone": cone["summary"],
            "pointer_parameter_dependent":{"stores":209,"functions":52,"interpretation":"over-approximation; caller/configuration provenance resolves the relevant route/controller/state pointers to fixed objects or RSCFD MMIO"},
            "critical_cells": [f"0x{x:08X}" for x in CRITICAL_CELLS],
            "whole_image_critical_candidate_rows":len(critical_rows),
            "prefault_critical_intersection_functions":["0x0008E7BA"],
            "intersection_closure":"0x8E7BA enforces index < 0x60 and writes FEBE5398..FEBE53F7, not a recovery cell",
            "stack_ranges":stack_intersections,
            "rscfd_pointer_row":[f"0x{x:08X}" for x in rscfd_ptrs],
            "route_slot_writer_range":{"base":f"0x{route_slot_base:08X}","max_if_slot_is_full_u8":f"0x{route_slot_max:08X}"},
            "communication_dimensions":comm_dims,
        },
        "verdict": {
            "real_memory_safety_defect_found": True,
            "controlled_write_primitive_recovered": False,
            "control_flow_pivot_recovered": False,
            "guard_write_recovered": False,
            "saved_pc_overwrite_recovered": False,
            "next_boundary": "A network-only recovery still requires an unrecovered write/control-flow side effect; the oversized-FD stale-byte condition does not cross any currently recovered consumer bound.",
        },
        "evidence": {
            "call_cone_store_audit":"data/generated/camry_8965F3307000_prefault_store_audit.json",
            "whole_image_computed_store_census":"data/generated/camry_8965F3307000_computed_store_target_census.json",
            "manual":"REFERENCE/r01uh0585ej0120_manual.pdf §17.4.4.1 / §17 receive storage behavior",
            "ghidra_script":"ghidra/scripts/investigate/AuditCallConeStores.java",
        },
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=OUT)
    args=ap.parse_args()
    obj=build()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
