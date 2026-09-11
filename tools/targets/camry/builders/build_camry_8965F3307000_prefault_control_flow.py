#!/usr/bin/env python3
"""Build exact-F33 pre-fault control-flow/reset/boot-catch recovery evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from tools.targets.camry.support.camry_f33_corpus import IMAGE, IMAGE_SHA256

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/generated/camry_8965F3307000_prefault_control_flow.json"
STORE_AUDIT = ROOT / "data/generated/camry_8965F3307000_prefault_control_flow_store_audit.json"
OPS_AUDIT = ROOT / "data/generated/camry_8965F3307000_prefault_control_flow_ops.json"
STORE_CENSUS = ROOT / "data/generated/camry_8965F3307000_computed_store_target_census.json"
DECOMP = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"

CRITICAL_CELLS = [
    0xFEBE3DF0,0xFEBE3DF1,0xFEBE3DF2,0xFEBE3DF3,0xFEBE3DF4,0xFEBE3DF5,
    0xFEBE5628,0xFEBF0FD0,0xFEBF117C,0xFEBF1180,0xFEBF1194,0xFEBF1198,
    0xFEBF131C,0xFEBF1320,0xFEBF1324,0xFEBF6B04,
]
DCM_ROOTS = [0x920BE,0x92152,0x926D2,0x921D2,0x92836,0x92946]


def u16(b: bytes, off: int) -> int: return struct.unpack_from("<H", b, off)[0]
def u32(b: bytes, off: int) -> int: return struct.unpack_from("<I", b, off)[0]
def need(ok: bool, msg: str) -> None:
    if not ok: raise ValueError(msg)


def load_decomp() -> dict[int, dict]:
    out = {}
    for line in DECOMP.read_text().splitlines():
        r = json.loads(line)
        if r.get("record") == "function": out[int(r["entry_addr"],16)] = r
    return out


def bits(x: int) -> list[int]: return [i for i in range(32) if x & (1 << i)]


def build() -> dict:
    image = IMAGE.read_bytes()
    need(len(image) == 0x100000 and hashlib.sha256(image).hexdigest() == IMAGE_SHA256, "exact F33 image drift")
    dec = load_decomp()
    fn = lambda a: dec[a]["decompiled_c"]
    store = json.loads(STORE_AUDIT.read_text())
    ops = json.loads(OPS_AUDIT.read_text())
    census = json.loads(STORE_CENSUS.read_text())
    need(store["schema"] == "camry-8965f3307000-prefault-control-flow-store-audit-v1", "expanded store audit schema drift")
    need(store["summary"] == {"computed":366,"functions":307,"ranged":56,"stores":412,"unknown":307}, "expanded store denominator drift")
    need(store["pointer_parameter_dependent"]["store_count"] == 283 and store["pointer_parameter_dependent"]["function_count"] == 76, "expanded pointer-store denominator drift")
    need(ops["summary"] == {"arith":0,"functions":307,"indirects":20,"loads":854,"param_arith":0,"param_indirects":5,"param_loads":620}, "expanded memory-op denominator drift")
    cone_funcs = {int(x,16) for x in store["function_entries"]}

    # The expanded cone admits the DCM state helpers as coarse critical-cell hits.
    # Their index is resolved from the exact three-entry DCM route resolver below.
    critical_rows = []
    for row in census["candidates"]:
        lo,hi = int(row["lo"],16),int(row["hi"],16)
        if any(lo <= x <= hi for x in CRITICAL_CELLS) and int(row["function"],16) in cone_funcs:
            critical_rows.append(row)
    critical_funcs = sorted({int(x["function"],16) for x in critical_rows})
    need(len(critical_rows) == 15, f"expanded critical-row count drift: {len(critical_rows)}")
    need(critical_funcs == [0x8E7BA,0x93C6C,0x93C9A,0x93DE8,0x93E5C,0x93EF6,0x93F4E,0x9405C], f"expanded critical functions drift: {critical_funcs}")

    # DCM external PDU -> internal channel resolver has exactly three matches.
    resolver = fn(0x93F0E)
    need("uVar1 < 3" in resolver and "return 0xffff" in resolver, "DCM route resolver bound drift")
    dcm_routes = [u16(image,0x25EF2 + i*12) for i in range(3)]
    # 25EF2 is embedded in 12-byte-ish config rows as seen by 93F0E stride 6 ushort.
    need(dcm_routes == [2,3,4], f"DCM route IDs drift: {dcm_routes}")
    for a in (0x92152,0x921D2):
        need("FUN_00093f0e" in fn(a) and "0xffff" in fn(a), f"DCM callback 0x{a:X} resolver/reject drift")
    need("DAT_febe59dc" in fn(0x9405C) and "1 <" in fn(0x9405C), "DCM two-entry event helper drift")
    need("(param_1 & 0xffff) < 0x60" in fn(0x8E7BA), "8E7BA exact bound drift")

    # ECM starts with all maskable/NMI/internal-reset routing disabled, then enables
    # only eight maskable sources. RSCFD ECC sources 22/37/54 are absent.
    ecm_clear = fn(0x63338)
    for addr in range(0xFFD62004,0xFFD62028,4):
        need(f"DAT_{addr:08x} = 0;" in ecm_clear, f"ECM clear missing {addr:08X}")
    ecm_enable = fn(0x63738)
    need("DAT_ffd62004 = 0x100b001e" in ecm_enable, "ECM maskable enable drift")
    micfg0 = 0x100B001E
    enabled_ecm = bits(micfg0)
    need(enabled_ecm == [1,2,3,4,16,17,19,28], f"ECM enabled bits drift: {enabled_ecm}")
    rscfd_ecm_sources = {22:"RS-CANFD RAM uncorrectable ECC",37:"peripheral RAM ECC-address overflow including RS-CANFD",54:"RS-CANFD RAM correctable ECC"}
    need(not set(rscfd_ecm_sources) & set(enabled_ecm), "RSCFD ECM source unexpectedly routed maskable")

    # Interrupt routing: only CAN1 RX/TX are enabled. Error/global CAN lines remain masked.
    intbp = {n:u32(image,0x20200+n*4) for n in range(183,191)}
    need(intbp == {183:0x62E1E,184:0x62E1E,185:0x62E1E,186:0x62E1E,187:0x66100,188:0x660BE,189:0x62E1E,190:0x62E1E}, f"CAN INTBP table drift: {intbp}")
    eic = fn(0x62E6A)
    for n,addr in [(183,0xFFFFB16E),(184,0xFFFFB170),(185,0xFFFFB172),(186,0xFFFFB174),(189,0xFFFFB17A),(190,0xFFFFB17C)]:
        need(f"DAT_{addr:08x} = 0x80cf" in eic, f"CAN EIC{n} mask drift")
    need("FUN_00062e44(&DAT_ffffb176,&DAT_00008048)" in eic and "FUN_00062e44(&DAT_ffffb178,&DAT_00008048)" in eic, "CAN1 RX/TX EIC enable drift")
    default_isr = image[0x62E1E:0x62E44]
    need(image[0x62E42:0x62E44] == bytes.fromhex("8505"), "default ISR terminal self-branch drift")

    # CAN1: bus-off automatically enters channel halt, but all channel/global error
    # interrupt enables are disabled. Its foreground recovery worker is after 7A272.
    cctr = u32(image,0x233EC+0x10) | 1
    need(cctr == 0x00A00001, f"CAN1 CCTR drift: {cctr:08X}")
    error_enable_names = {8:"BEIE",9:"EWIE",10:"EPIE",11:"BOEIE",12:"BORIE",13:"OLIE",14:"BLIE",15:"ALIE",16:"TAIE",17:"EOCOIE",18:"SOCOIE",19:"TDCVFIE"}
    channel_error_enables = {name:(cctr>>bit)&1 for bit,name in error_enable_names.items()}
    need(not any(channel_error_enables.values()), f"CAN1 error IRQ unexpectedly enabled: {channel_error_enables}")
    bom = (cctr >> 21) & 0x3
    need(bom == 1, f"CAN1 BOM drift: {bom}")
    gctr = 0x00010001
    global_error_enables = {"DEIE":(gctr>>8)&1,"MEIE":(gctr>>9)&1,"THLEIE":(gctr>>10)&1,"CMPOFIE":(gctr>>11)&1}
    need(not any(global_error_enables.values()), f"global CAN error IRQ unexpectedly enabled: {global_error_enables}")
    agg = fn(0x7A254)
    need(agg.index("FUN_00079ede") < agg.index("FUN_00079f16"), "foreground CAN recovery order drift")
    need(image[0x7A272:0x7A278] == bytes.fromhex("80ffee1c2436"), "incident malformed JARL bytes drift")

    # WDTA0 is not referenced by exact CodeFlash. OPWDRUN is outside the retained
    # CodeFlash/DataFlash dumps, so automatic-start remains explicitly unknown.
    wdta = {0xFFD74000,0xFFD74004,0xFFD74008,0xFFD7400C}
    wdta_refs = []
    for a,r in dec.items():
        for ref in r.get("data_references",[]):
            if int(ref.get("to_addr","0"),16) in wdta:
                wdta_refs.append((a,ref))
    need(not wdta_refs, f"unexpected WDTA refs: {wdta_refs[:4]}")

    # RS-CANFD FIFO DMA/DTS request generation remains disabled: CFDCDTCT=0.
    cdtct_refs=[]
    for a,r in dec.items():
        refs=[x for x in r.get("data_references",[]) if x.get("to_addr","").lower()=="0xffd20490"]
        if refs: cdtct_refs.append((a,refs,r["decompiled_c"]))
    need({a for a,_,_ in cdtct_refs} == {0x84C2C,0x8488C,0x84E16}, f"CFDCDTCT ref-set drift: {[hex(x[0]) for x in cdtct_refs]}")
    need("PTR_DAT_0002309c = 0" in fn(0x84E16), "CFDCDTCT zero writer drift")
    need("**(undefined4 **)(puVar7 + -0xd60) = 0" in fn(0x8488C), "CFDCDTCT init zero drift")
    need("PTR_DAT_0002309c & 0xffff) == 0" in fn(0x84C2C), "CFDCDTCT consistency check drift")
    need(u32(image,0x2309C)==0xFFD20490, "CFDCDTCT pointer-table drift")

    # All five parameter-dependent indirect calls are exact, and the only PduR
    # sites independently bound group/index before callback selection.
    ind_rows = ops["parameter_dependent_indirect_rows"]
    ind_sites = {(int(x.split("|")[2],16),int(x.split("|")[3],16)) for x in ind_rows}
    need(ind_sites == {(0x80884,0x808BE),(0x810F2,0x8115C),(0x810F2,0x8117A),(0x81938,0x81988),(0x81D30,0x81DD4)}, f"indirect site set drift: {ind_sites}")
    need("uVar1 < 0xc" in fn(0x81938) and "param_1 & 0x7ff" in fn(0x81938), "81938 route bounds drift")
    need("0xb < uVar1" in fn(0x81D30) and "uVar3" in fn(0x81D30) and "PTR_LAB_00021d28" in fn(0x81D30), "81D30 route bounds drift")
    need(ops["summary"]["arith"] == 0, "unexpected integer divide/remainder in expanded cone")

    # Exact synchronous normal-CAN ingress mapping: three protected PDUs enter
    # SecOC, all other 40 accepted rules enter raw COM. No raw-COM pre-copy hook
    # is enabled on any configured PDU 5..47.
    route_base = u32(image,0x21D40)
    need(route_base == 0x229CE, f"PduR group0 route table drift: {route_base:X}")
    desc0 = u32(image,0x21EE4)
    need(desc0 == 0x21E00 and u32(image,desc0+8)==0x7D72C, "PduR group0 raw-COM callback drift")
    need(u32(image,0x21E48)==0x8EE7C, "PduR SecOC callback drift")
    protected_rules=[]; raw_rules=[]
    rule_map=[]
    for rule in range(43):
        can_id = u32(image,0x230B8+rule*16) & 0x1FFFFFFF
        pid=5+rule
        first=u16(image,route_base+pid*4); second=u16(image,route_base+pid*4+2)
        if second != 0xFFFF:
            protected_rules.append(rule); cb=0x8EE7C; kind="secoc"
        else:
            g=(first>>11)&0x1F; idx=first&0x7FF
            need(g < 12, f"normal PDU fallback group out of range rule {rule}")
            desc=u32(image,0x21EE4+g*4); cb=u32(image,desc+8); kind="raw_com"
            need(cb==0x7D72C, f"normal PDU non-COM callback rule {rule}: {cb:X}")
            raw_rules.append(rule)
        rule_map.append({"rule":rule,"can_id":f"0x{can_id:03X}","pdur_id":pid,"kind":kind,"callback":f"0x{cb:08X}"})
    need(protected_rules == [4,36,39] and len(raw_rules)==40, f"normal ingress partition drift: {protected_rules}")
    pdu_records=[]
    for pid in range(5,48):
        rec=image[0x226C0+pid*8:0x226C8+pid*8]
        pdu_records.append({"pdu":pid,"selector":rec[2],"flags":rec[7]})
    need(all(x["selector"]==0 and x["flags"]==0x0C for x in pdu_records), "raw COM pre-copy-hook flags drift")
    need("& 0x10" in fn(0x7D72C) and "FUN_0008e772" in fn(0x7D72C), "raw COM callback semantics drift")
    need("param_1 < 0x60" in fn(0x8E772) and "DAT_febe5338" in fn(0x8E772), "COM generation bookkeeping drift")

    # The FE01 guard is the only precondition around the malformed aggregate, and
    # only one-time startup writes it. There is no asynchronous legitimate off switch.
    guard_refs=[]
    for a,r in dec.items():
        for ref in r.get("data_references",[]):
            if ref.get("to_addr","").lower()=="0xfebe3df2": guard_refs.append((a,ref["from_addr"],ref["ref_type"]))
    writers=[x for x in guard_refs if x[2]=="WRITE"]
    need(writers == [(0x7A132,"0x0007a13a","WRITE"),(0x7A132,"0x0007a184","WRITE")], f"guard writer set drift: {writers}")
    need("if (DAT_febe3df2 == -0x1ff)" in agg, "aggregate guard drift")

    # Valid cold boot jumps to application before the bootloader CAN loop; CAN is
    # initialized only on the failed-validation branch.
    boot = fn(0x13B0)
    need("iVar3 = FUN_0000119e()" in boot and "PTR_f33_application_entry_000ffdb8" in boot and "FUN_00001398()" in boot, "boot branch structure drift")
    need(boot.index("PTR_f33_application_entry_000ffdb8") < boot.index("FUN_00001398()"), "boot branch textual order drift")
    need("FUN_00001338()" in fn(0x1398) and "FUN_00003b3c()" in fn(0x1338), "bootloader CAN init chain drift")

    # No direct hard-reset/fatal helper is in the expanded direct-call cone.
    need(not ({0x608AA,0x7059E,0x61940,0x62E1E} & cone_funcs), "fatal/reset helper unexpectedly reachable in expanded cone")

    return {
        "schema":"camry-8965f3307000-prefault-control-flow-v1",
        "target":{"software_id":"8965F3307000","codeflash_sha256":IMAGE_SHA256},
        "expanded_cone":{
            "roots":store["roots"],"store_summary":store["summary"],"memory_op_summary":ops["summary"],
            "pointer_parameter_store_count":store["pointer_parameter_dependent"]["store_count"],
            "critical_known_range_rows":len(critical_rows),
            "critical_known_range_functions":[f"0x{x:08X}" for x in critical_funcs],
            "dcm_route_domain":[0,1,2],
            "classification":"original receive/interrupt cone plus all six resolved DCM transport callbacks",
        },
        "ecm_reset_routing":{
            "initial_clear":"0x63338 clears MICFG0..2, NMICFG0..2, IRCFG0..2",
            "runtime_micfg0":f"0x{micfg0:08X}","maskable_sources":enabled_ecm,
            "rscfd_ecm_sources":{str(k):v for k,v in rscfd_ecm_sources.items()},
            "rscfd_sources_routed":[],
            "classification":"RS-CANFD ECC sources are not routed to application maskable ECM, NMI, or ECM internal reset",
        },
        "can_interrupt_error_surface":{
            "intbp_entries":{str(k):f"0x{v:08X}" for k,v in intbp.items()},
            "eic":{"183":"masked 0x80CF","184":"masked 0x80CF","185":"masked 0x80CF","186":"masked 0x80CF","187":"enabled table-reference priority8 0x8048","188":"enabled table-reference priority8 0x8048","189":"masked 0x80CF","190":"masked 0x80CF"},
            "default_handler":{"entry":"0x00062E1E","sha256":hashlib.sha256(default_isr).hexdigest(),"terminal":"self-loop at 0x62E42"},
            "can1_cctr":f"0x{cctr:08X}","bus_off_mode":bom,"channel_error_interrupt_enables":channel_error_enables,
            "global_gctr":f"0x{gctr:08X}","global_error_interrupt_enables":global_error_enables,
            "bus_off_effect":"hardware automatically enters CAN1 channel halt; the software channel recovery state machine is later in the poisoned foreground",
        },
        "watchdog_boundary":{
            "wdta0_mmio":["0xFFD74000","0xFFD74004","0xFFD74008","0xFFD7400C"],"codeflash_reference_count":0,
            "ecm_source":0,"runtime_ecm_routed":False,
            "option_byte_startup":"unknown: OPWDRUN option storage is outside the retained CodeFlash/DataFlash dumps",
            "classification":"no recovered watchdog-service/starvation reset primitive in the running application",
        },
        "rscfd_dma":{
            "cdtct":"0xFFD20490","pointer_source":"CodeFlash[0x2309C]","reference_functions":["0x0008488C","0x00084C2C","0x00084E16"],
            "writers":"0x8488C and 0x84E16 write zero; 0x84C2C requires low16 == 0",
            "classification":"RS-CANFD DMA/DTS request generation is disabled; CAN ingress cannot bypass CPU store bounds through CFDCDTCT",
        },
        "indirect_control_flow":{
            "parameter_dependent_sites":[{"function":f"0x{f:08X}","site":f"0x{s:08X}"} for f,s in sorted(ind_sites)],
            "pdur_bounds":"0x81938 and 0x81D30 require group<12 and index<configured_count[group] before callback lookup",
            "integer_divide_or_remainder_ops":0,
            "classification":"no payload-controlled indirect call or divide/remainder fault recovered in the expanded cone",
        },
        "synchronous_ingress":{
            "normal_rule_count":43,"protected_rules":protected_rules,"protected_can_ids":[rule_map[i]["can_id"] for i in protected_rules],
            "raw_com_rule_count":len(raw_rules),"rule_map":rule_map,
            "raw_com_pdu_records":{"ids":"5..47","selector":0,"flags":"0x0C","pre_copy_hook_enabled":False},
            "raw_com_effect":"bounded copy plus state bookkeeping and 0x8E772 generation-byte update only; application signal unpack/control logic is deferred",
            "diagnostics":"bounded DCM transport/event state; internal channel domain 0..2",
            "xcp":"staging only before the dead foreground protocol dispatch",
        },
        "guard_and_boot":{
            "guard":"0xFEBE3DF2","guard_writers":[{"function":"0x0007A132","site":"0x0007A13A","value":"0xFD02"},{"function":"0x0007A132","site":"0x0007A184","value":"0xFE01"}],
            "post_startup_guard_writer":False,"aggregate_skip":"0x7A260 skips entire aggregate only when guard != FE01",
            "bad_callsite":"0x0007A272","bad_bytes":"80 FF EE 1C 24 36","conditional_bypass_between_79EDE_and_bad_call":False,
            "cold_boot":"valid 0x119E result calls FFDB8/0x20880 directly; 0x1398 bootloader CAN init is reached only on validation failure",
            "cold_boot_can_race":False,
        },
        "verdict":{
            "network_guard_transition_recovered":False,"network_reset_recovered":False,"network_control_flow_pivot_recovered":False,"bootloader_can_catch_with_valid_application":False,
            "remaining_boundary":"exact post-0x7A272 fault context remains unobserved; unrecovered hardware/debug/board-level paths and mechanisms outside the retained software/hardware configuration remain open",
        },
        "evidence":{
            "store_audit":"data/generated/camry_8965F3307000_prefault_control_flow_store_audit.json",
            "memory_ops":"data/generated/camry_8965F3307000_prefault_control_flow_ops.json",
            "store_script":"ghidra/scripts/investigate/AuditCallConeStores.java","memory_ops_script":"ghidra/scripts/investigate/AuditCallConeMemoryOps.java",
            "manual":"REFERENCE/r01uh0585ej0120_manual.pdf (ECM, RS-CANFD CCTR/GCTR, EIC, WDTA sections)",
        },
    }


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,default=OUT); args=ap.parse_args()
    obj=build(); args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n"); print(args.out); return 0

if __name__ == "__main__": raise SystemExit(main())
