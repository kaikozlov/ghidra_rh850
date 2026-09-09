#!/usr/bin/env python3
"""Re-derive the exact F33 B6 receive/publication path from CodeFlash + canonical corpus.

This deliberately does not consume findings/docs as proof inputs.  It joins the raw
RSCFD/CanIf/PduR/SecOC configuration tables to the canonical function graph and emits
the exact boundary that still requires runtime observation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
DEFAULT_OUT = ROOT / "data/generated/camry_8965F3307000_b6_ingress_closure.json"
SHA = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
COUNT = 6065

# Entries whose exact graph placement matters to this proof.  Three of these were
# historically missing from the canonical graph and are now explicit target seeds.
ROLE = {
    0x71508: "controller-1 receive interrupt wrapper",
    0x66026: "interrupt dispatch aggregate",
    0x667B6: "CAN receive interrupt task",
    0x7A232: "CAN receive interrupt state gate",
    0x79EBA: "RSCFD hardware receive aggregate",
    0x83CE4: "RSCFD group receive loop",
    0x83EDA: "RSCFD group receive wrapper",
    0x83E0C: "RSCFD FIFO drain",
    0x83D14: "RSCFD rule-to-generic-Rx adapter",
    0x80B42: "generic Rx admission/ring writer",
    0x80A4A: "software Rx ring writer",
    0x667E6: "foreground communications/application aggregate",
    0x7A254: "foreground CAN/PduR/SecOC aggregate",
    0x79EDE: "software Rx ring foreground drain aggregate",
    0x809FE: "software Rx ring controller loop",
    0x808D6: "software Rx ring drain",
    0x80884: "software Rx callback fanout",
    0x810F2: "normal CanIf Rx callback",
    0x6A3BE: "legacy Toyota checksum dispatcher",
    0x6A32C: "legacy Toyota checksum evaluator",
    0x81D16: "PduR lower-route shim",
    0x81D30: "PduR lower-route dispatcher",
    0x8EE7C: "SecOC secured-PDU ingress",
    0x8F2B0: "SecOC route-to-profile resolver",
    0x8F34A: "SecOC receive queue wrapper",
    0x8E862: "SecOC queue-family resolver",
    0x8E912: "SecOC profile queue geometry resolver",
    0x8E9C6: "SecOC queue insert/copy",
    0x6A410: "foreground SecOC aggregate wrapper",
    0x8EFF8: "SecOC foreground receive aggregate",
    0x8EF84: "SecOC receive queue consumer loop",
    0x8F98C: "SecOC one-PDU verify/deliver transaction",
    0x8E8A0: "SecOC queue head selector",
    0x8F746: "SecOC freshness/auth verification coordinator",
    0x8F906: "SecOC post-verify delivery gate",
    0x8F546: "verified upper-PDU delivery",
    0x90204: "upper PduR indication shim",
    0x81CA6: "PduR upper-route dispatcher",
    0x7D72C: "generated-COM receive callback",
    0x8E772: "generated-COM generation update",
    0x4BD46: "generated-COM route44 unpacker",
    0x8FABA: "opposite queue-family insertion helper",
    0x8ED8E: "opposite queue-family public ingress",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u16(b: bytes, off: int) -> int:
    return struct.unpack_from("<H", b, off)[0]


def u32(b: bytes, off: int) -> int:
    return struct.unpack_from("<I", b, off)[0]


def load_corpus() -> tuple[dict[str, Any], dict[int, dict[str, Any]]]:
    meta = None
    funcs: dict[int, dict[str, Any]] = {}
    for line in CORPUS.read_text().splitlines():
        row = json.loads(line)
        if row.get("record") == "metadata":
            meta = row
        elif row.get("record") == "function":
            funcs[int(row["entry_addr"], 16)] = row
    if meta is None:
        raise RuntimeError("missing corpus metadata")
    return meta, funcs


def need(ok: object, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def body_hash(img: bytes, rec: dict[str, Any]) -> str:
    out = bytearray()
    for r in rec["body_ranges"]:
        lo, hi = int(r["min"], 16), int(r["max"], 16)
        out += img[lo:hi+1]
    return sha(bytes(out))


def direct_calls(text: str) -> set[int]:
    # Exclude the function's own declaration; only call expressions in the
    # decompiled body are graph edges.
    body = text.split("{", 1)[1] if "{" in text else text
    return {int(x, 16) for x in re.findall(r"FUN_([0-9a-fA-F]{8})\s*\(", body)}


def call_path(funcs: dict[int, dict[str, Any]], path: list[int]) -> bool:
    return all(b in direct_calls(funcs[a]["decompiled_c"]) for a, b in zip(path, path[1:]))


def refs_to(funcs: dict[int, dict[str, Any]], target: int, typ: str | None = None) -> list[dict[str, str]]:
    out = []
    for entry, rec in sorted(funcs.items()):
        for ref in rec.get("data_references", []):
            try:
                dst = int(ref["to_addr"], 16)
            except (KeyError, ValueError):
                continue
            if dst == target and (typ is None or ref.get("ref_type") == typ):
                out.append({"function": f"0x{entry:08X}", "from": ref["from_addr"], "type": ref["ref_type"]})
    return out


def analyze() -> dict[str, Any]:
    img = IMAGE.read_bytes()
    need(sha(img) == SHA, "CodeFlash identity drift")
    meta, funcs = load_corpus()
    need(len(funcs) == COUNT == meta["function_count"] == meta["decompiled_count"], "canonical function-count drift")
    missing = sorted(set(ROLE) - set(funcs))
    need(not missing, f"critical canonical entries missing: {[hex(x) for x in missing]}")
    c = {a: funcs[a]["decompiled_c"] for a in ROLE}

    # 1) Physical RSCFD acceptance and generic Rx object order.
    rules = [struct.unpack_from("<IIII", img, 0x230B8 + i*16) for i in range(47)]
    need(u16(img, 0x22ECE) == 0 and img[0x22ED0] == 47, "controller-1 rule span drift")
    descriptors = []
    for i in range(43):
        raw, length = struct.unpack_from("<II", img, 0x21FE8 + i*8)
        descriptors.append({"index": i, "raw": raw, "can_id": raw & 0x1FFFFFFF,
                            "fd": bool(raw & 0x40000000), "length": length, "pdu": 5+i})
    need([r[0] for r in rules[:43]] == [d["can_id"] for d in descriptors], "RSCFD normal-rule/CanIf descriptor order drift")
    need([r[0] for r in rules[43:46]] == [0x7A1, 0x777, 0x7A0] and rules[46][0] == 0x9FDC0002,
         "controller-1 special tail drift")
    b6 = descriptors[39]
    need(b6 == {"index":39,"raw":0x400000B6,"can_id":0xB6,"fd":True,"length":32,"pdu":44}, "B6 descriptor drift")
    need(rules[39] == (0xB6, 0x00300000, 2, 0), f"B6 RSCFD rule drift: {rules[39]}")
    need(img[0x219AC:0x219AC+47] == b"\0"*47, "generic Rx objects no longer map wholly to software controller0")
    need(img[0x219DC:0x219DC+43] == b"\x01"*43, "normal Rx callback selector drift")
    need(img[0x21970] == 1, "software Rx controller count drift")

    irq_path = [0x71508,0x66026,0x667B6,0x7A232,0x79EBA,0x83CE4,0x83EDA,0x83E0C,0x83D14,0x80B42,0x80A4A]
    # The vector wrapper -> 66026 and the remaining direct calls are explicit in the promoted corpus.
    need(call_path(funcs, irq_path), "hardware Rx interrupt call path drift")
    need("eiret" in funcs[0x71508].get("mnemonics", []) or "FUN_00066026" in c[0x71508], "interrupt wrapper evidence drift")

    # 2) Foreground ring drain and exact normal CanIf B6 admission.
    fg_rx_path = [0x667E6,0x7A254,0x79EDE,0x809FE,0x808D6,0x80884]
    need(call_path(funcs, fg_rx_path), "foreground software-ring drain path drift")
    need(u16(img,0x21908) == 0 and u16(img,0x2190A) == 43, "CanIf controller0 descriptor range drift")
    callback_table = [u32(img,0x21A24+i*4) for i in range(6)]
    need(callback_table[0] == 0x810F2, f"normal CanIf callback slot0 drift: {callback_table}")
    need(all(x in c[0x810F2] for x in ("DAT_00021a48 + uVar5", "FUN_0006a3be", "FUN_00081d16")), "CanIf receive body drift")
    need(img[0x21A48] == 5 and img[0x21FB8+44] == 0x10, "B6 PDU base/flags drift")

    # PDU44 executes the legacy checksum hook, but its own config disables checksum enforcement.
    legacy_records = [img[0x28FE4+i*8:0x28FE4+(i+1)*8] for i in range(img[0x28FD4])]
    p44_legacy = next(r for r in legacy_records if r[0] == 44)
    need(p44_legacy == bytes.fromhex("2c00000bb8010200"), f"PDU44 legacy-checksum record drift: {p44_legacy.hex()}")
    need("== 'Z'" in c[0x6A32C] or "== 0x5a" in c[0x6A32C].lower(), "legacy checksum enable predicate drift")

    # 3) PduR lower route concretely resolves PDU44 -> SecOC secured ingress.
    need(u32(img,0x21CE4) == 0x81D30, "lower PduR dispatcher pointer drift")
    need(u16(img,0x21D1E) == 0xFFFF, "lower PduR pre-remap drift")
    need(u16(img,0x21D28) == 48 and u32(img,0x21D40) == 0x229CE, "lower PduR group0 geometry drift")
    lower44 = (u16(img,0x229CE+44*4), u16(img,0x229D0+44*4))
    need(lower44 == (44,44), f"lower PduR route44 drift: {lower44}")
    need(u32(img,0x21CBC) == 0x21E40 and u32(img,0x21E48) == 0x8EE7C, "PduR SecOC callback-table drift")
    # CanIf calls the 81D16 shim directly; the shim dispatches through the
    # configured pointer at 21CE4, whose exact value is 81D30.  Do not model
    # that table-selected edge as a direct call in the corpus graph.
    need(call_path(funcs,[0x810F2,0x81D16]), "CanIf->PduR lower-shim direct edge drift")

    # 4) SecOC profile selection and receive queue geometry.
    profiles = []
    for i in range(3):
        p = 0x2586C + i*0x50
        profiles.append({
            "index": i, "address": f"0x{p:06X}", "max_length": u32(img,p),
            "secured_buffer_displacement": u32(img,p+4),
            "input_route": u16(img,p+0x10), "output_route": u16(img,p+0x12),
            "min_length": u16(img,p+0x32), "selector": u16(img,p+0x3C),
            "raw_sha256": sha(img[p:p+0x50]),
        })
    p2 = profiles[2]
    need(p2["input_route"] == p2["output_route"] == 44 and p2["max_length"] == 32 and
         p2["secured_buffer_displacement"] == 40 and p2["min_length"] == 4 and p2["selector"] == 0,
         f"SecOC profile2 geometry drift: {p2}")
    need(all(x in c[0x8F2B0] for x in
             ("param_2 == '\\0'", "(&DAT_0002587c)[(short)uVar1 * 0x28]", "2 < uVar1")),
         "route-to-profile resolver drift")
    need(call_path(funcs,[0x8EE7C,0x8F34A,0x8E9C6]), "SecOC receive-enqueue path drift")
    need("FUN_0008e9c6(1" in c[0x8F34A], "receive wrapper no longer uses queue family1")
    need(all(x in c[0x8E862] for x in ("&DAT_febe546a", "&DAT_febe54ac")), "receive queue-family base drift")
    need(all(x in c[0x8E912] for x in ("param_1 == 1", "&DAT_0002586c", "&DAT_00025870")), "profile queue resolver drift")
    queue_record = 0xFEBE546A + 2*8
    secured_buffer = 0xFEBE54AC + p2["secured_buffer_displacement"]
    need(queue_record == 0xFEBE547A and secured_buffer == 0xFEBE54D4, "profile2 RAM geometry arithmetic drift")
    copy_pos = c[0x8E9C6].find("FUN_00089f2e")
    pub_pos = c[0x8E9C6].find("*puVar1 = *(undefined2 *)(param_3 + 1)")
    need(copy_pos >= 0 and pub_pos > copy_pos, "SecOC queue publication order drift")

    # Opposite queue-family insertion exists but cannot populate the family1 receive queue:
    # it explicitly invokes 8E9C6(0,...), while B6 receive invokes 8E9C6(1,...).
    need("FUN_0008e9c6(0" in c[0x8FABA] and "FUN_0008faba" in c[0x8ED8E], "opposite queue-family path drift")

    # 5) The timing blind spot: software-ring drain/enqueue and SecOC consume are ordered
    # inside one 7A254 invocation, not separated by a foreground wait.
    t = c[0x7A254]
    need(t.find("FUN_00079ede();") < t.find("FUN_0006a410();"), "same-invocation receive/consumer ordering drift")
    consume_path = [0x6A410,0x8EFF8,0x8EF84,0x8F98C]
    need(call_path(funcs,consume_path), "SecOC consumer path drift")
    need(all(x in c[0x8F98C] for x in ("FUN_0008e8a0(1,0", "FUN_0008f746", "FUN_0008f906")), "SecOC consumer transaction drift")

    # 6) Successful profile2 delivery resolves the same secured buffer and route44 into COM.
    need("FUN_0008f546" in c[0x8F906], "post-verify upper delivery edge drift")
    need("FUN_0008eb1c(1" in c[0x8F546] and "FUN_00090204" in c[0x8F546], "upper delivery queue-family/pdur edge drift")
    need(call_path(funcs,[0x90204,0x81CA6]), "upper PduR shim path drift")
    need(u32(img,0x21E08) == 0x7D72C, "generated COM Rx callback pointer drift")
    route44_rec = img[0x226C0+44*8:0x226C0+(44+1)*8]
    need(route44_rec == bytes.fromhex("060000002000000c"), f"route44 COM record drift: {route44_rec.hex()}")
    com_offset = u16(img,0x22840+44*2)
    com_base = 0xFEBEB800 - 0x6DB8 + com_offset
    need(com_offset == 0x1B7 and com_base == 0xFEBE4BFF, "route44 COM window drift")
    need("FUN_0008e772(param_1)" in c[0x7D72C], "COM callback generation-update edge drift")
    need(refs_to(funcs,0x8E772) == [], "unexpected direct data ref to helper")
    # Canonical caller identity is stronger than a docs claim: promoted 7D72C is the sole direct caller.
    callers_8e772 = sorted(f"0x{a:08X}" for a,r in funcs.items() if 0x8E772 in direct_calls(r["decompiled_c"]))
    callers_7d72c = sorted(f"0x{a:08X}" for a,r in funcs.items() if 0x7D72C in direct_calls(r["decompiled_c"]))
    need(callers_8e772 == ["0x0007D72C"], f"8E772 caller census drift: {callers_8e772}")
    # 7D72C is table-dispatched, so no direct caller is expected.
    need(callers_7d72c == [], f"7D72C unexpectedly gained direct callers: {callers_7d72c}")
    generation = 0xFEBE5338 + 44
    need(generation == 0xFEBE5364 and "(&DAT_febe5338)[param_1]" in c[0x8E772], "route44 generation arithmetic drift")
    unpack_refs = {int(r["to_addr"], 16) for r in funcs[0x4BD46].get("data_references", [])}
    need({0xFEBE5364, 0xFEBE7F68, 0xFEBE80C8, 0xFEBE80BC, 0xFEBE80B8} <= unpack_refs and
         all(x in c[0x4BD46] for x in ("FUN_0007d12a(0x105,0x1ba", "FUN_0007d12a(0x111,0x1c1")),
         "route44 unpacker drift")

    # Exact upper-source uniqueness: 90204 only comes from 8F546; 8F546 only from the
    # SecOC receive result machinery.  This rules out an autonomous software route44 ticker.
    def callers_of(target: int) -> list[str]:
        return sorted(f"0x{a:08X}" for a,r in funcs.items() if target in direct_calls(r["decompiled_c"]))
    upper_census = {f"0x{x:08X}": callers_of(x) for x in (0x90204,0x8F546,0x8F906,0x8F34A,0x8EE7C)}
    need(upper_census["0x00090204"] == ["0x0008F546"], f"90204 caller drift: {upper_census}")
    need(set(upper_census["0x0008F546"]) == {"0x0008F596","0x0008F906"}, f"8F546 caller drift: {upper_census}")
    need(upper_census["0x0008F34A"] == ["0x0008EE7C"], f"8F34A caller drift: {upper_census}")

    # Function evidence pins the proof to canonical corpus bytes, not documentation labels.
    evidence = {}
    for a, role in ROLE.items():
        r = funcs[a]
        evidence[f"0x{a:08X}"] = {"role": role, "body_size": r["body_size"],
                                    "body_sha256": body_hash(img,r),
                                    "decompiled_c_sha256": r["decompiled_c_sha256"]}

    static_conclusions = [
        "Exact F33 contains one configured normal B6 receive chain: controller-1 rule39 -> normal descriptor39 -> PDU44 -> protected SecOC profile2 -> generated COM route44.",
        "The B6 receive queue is family1/profile2: pending record FEBE547A and secured buffer FEBE54D4; 8E9C6 copies payload bytes before publishing queue length.",
        "The software Rx drain that can enqueue B6 occurs before the SecOC receive consumer inside the same 7A254 foreground invocation, so a monitor that samples only between foreground invocations can miss a complete 0->32->0 queue lifetime.",
        "Successful profile2 delivery re-resolves the same family1/profile2 secured buffer and publishes output route44 through 90204 -> 81CA6 -> table-selected 7D72C, which copies into FEBE4BFF and advances FEBE5364.",
        "No autonomous software route44 generation path was recovered: 8E772 has only 7D72C as a direct caller, and upper route publication is rooted in SecOC receive delivery. The observed no-host-TX route44 activity therefore implies an actual profile2 delivery source or an unrecovered mechanism; generation activity alone does not identify the physical source.",
        "The separate 8ED8E/8FABA insertion path uses SecOC queue family0 and cannot by itself explain family1/profile2 B6 receive-queue contents.",
    ]
    runtime_only = [
        "Whether a particular Panda-transmitted B6 is physically observed by F33 rule39 on the installed harness/topology. Panda TX echo proves local transmission, not receiver admission.",
        "The physical provenance of the profile2 deliveries that advanced route44 during the retained zero-host-B6-TX control. Static software proves their route, not which external node/link produced the received frame.",
        "ICU-S silicon-internal cryptographic behavior beyond the recovered software-visible command/result contract.",
        "Final motor/PWM/plant response after the already-recovered software command/current funnel.",
    ]

    return {
        "schema": "camry-8965f3307000-b6-ingress-closure-v1",
        "target": {"software_id":"8965F3307000","codeflash_sha256":sha(img),
                   "canonical_function_count":len(funcs),
                   "canonical_inventory_sha256":meta["project_inventory_sha256"]},
        "canonical_graph_repair": {
            "added_real_entries": ["0x00071508","0x0007D72C","0x000810F2"],
            "function_count_before": 6062, "function_count_after": 6065,
            "distinction": "These are three real omitted entries, not a reversal of CORR-181's three false +4 child splits at BCD66/CCFB6/CEE80.",
        },
        "physical_ingress": {
            "controller1_rule_count":47,"normal_rule_count":43,"b6_rule_index":39,
            "b6_rule_hex":img[0x230B8+39*16:0x230B8+40*16].hex(),
            "b6_descriptor":b6,"all_normal_rules_equal_descriptor_order":True,
            "all_generic_rx_objects_to_software_controller0":True,
            "hardware_to_ring_path":[f"0x{x:08X}" for x in irq_path],
        },
        "canif_pdur": {
            "foreground_ring_drain_path":[f"0x{x:08X}" for x in fg_rx_path],
            "controller0_descriptor_range":[0,43],"normal_callback_table":[f"0x{x:08X}" for x in callback_table],
            "pdu44_flags":"0x10","legacy_checksum_record_hex":p44_legacy.hex(),
            "legacy_checksum_hook_executes":True,"legacy_checksum_enforced_for_pdu44":False,
            "lower_route44":list(lower44),"lower_dispatcher":"0x00081D30","secured_ingress_callback":"0x0008EE7C",
        },
        "secoc_receive": {
            "profiles":profiles,"b6_profile":2,"queue_family":1,
            "queue_record":f"0x{queue_record:08X}","secured_buffer":f"0x{secured_buffer:08X}",
            "payload_copy_precedes_length_publication":True,
            "enqueue_path":["0x0008EE7C","0x0008F34A","0x0008E9C6"],
            "opposite_family_insert_path":["0x0008ED8E","0x0008FABA","0x0008E9C6(family0)"],
        },
        "scheduler": {
            "foreground_root":"0x000667E6","aggregate":"0x0007A254",
            "ring_drain_call_site":"0x0007A26E","secoc_consumer_call_site":"0x0007A2B4",
            "same_invocation_order":"ring drain/enqueue precedes SecOC consumer",
            "consumer_path":[f"0x{x:08X}" for x in consume_path]+["0x0008E8A0(family1)","0x0008F746","0x0008F906"],
            "consequence":"between-tick and immediately-before-next-aggregate queue polling cannot exclude a complete same-invocation queue transaction",
        },
        "route44_publication": {
            "upper_path":["0x0008F906","0x0008F546","0x00090204","0x00081CA6","table 0x21E08 -> 0x0007D72C","0x0008E772"],
            "route44_record_hex":route44_rec.hex(),"com_offset":f"0x{com_offset:03X}",
            "com_window":f"0x{com_base:08X}","generation":f"0x{generation:08X}",
            "generation_helper_direct_callers":callers_8e772,"com_callback_direct_callers":callers_7d72c,
            "upper_caller_census":upper_census,
            "autonomous_software_route44_ticker_recovered":False,
        },
        "function_evidence":evidence,
        "static_conclusions":static_conclusions,
        "runtime_only_boundaries":runtime_only,
        "next_experiment_policy": "Do not return to the car merely to rediscover software routing. Only a receiver-side observation ordered inside 7A254 (after the software-ring drain and before SecOC consume), or an earlier interrupt/CanIf witness with equivalent proven ordering, can answer TX-echo -> exact receiver admission. Re-audit static open questions first.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args()
    data = analyze()
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if ns.check:
        need(ns.output.exists(), f"missing generated artifact {ns.output}")
        need(ns.output.read_text() == text, "generated artifact stale")
    else:
        ns.output.write_text(text)
        print(f"wrote {ns.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
