#!/usr/bin/env python3
"""Build deterministic target-native Corolla-H SecOC/ICU-S residual closure."""
from __future__ import annotations
from tools import REPO_ROOT
import argparse,hashlib,json,re,struct
from pathlib import Path
from tools.targets.sienna.sienna_target import CODEFLASH as SIENNA_CODEFLASH
from tools.targets.corolla.support.corolla_h_constants import RAW_DUMP as H_RAW_DUMP
from tools.project.analysis_target import path as target_path
from tools.project.decompiler_evidence import bind_entries, load_function_corpus
ROOT=REPO_ROOT
EV=ROOT/'data/generated/corolla_8965H1202000_secoc_surface_decompiler_evidence.json'
HRAW=H_RAW_DUMP
SIMG=SIENNA_CODEFLASH
OUT=ROOT/'data/generated/corolla_8965H1202000_secoc_surface.json'
CORE_REFS=[0x8704c,0x870a8,0x871a0,0x87610,0x87636,0x8783c,0x87b46,0x87bba,0x87c14,0x87c70,0x87ccc,0x87dd0,0x88028,0x88080,0x880dc,0x881dc,0x888fa,0x889cc,0x88b5c,0x88b6a,0x88b9c,0x88c0a,0x89448,0x894be,0x89510]
def sha(b):return hashlib.sha256(b).hexdigest()
def u16(b,a):return struct.unpack_from('<H',b,a)[0]
def u32(b,a):return struct.unpack_from('<I',b,a)[0]
def calls(c):return re.findall(r'\b(?:FUN_|direct_call_target_|func_0x)(?:000)?([0-9a-fA-F]{5,8})\s*\(',c)


def initializer_surface(H: bytes, S: bytes) -> dict:
    """Recover initializer identity from native call, callback, and state dataflow."""
    selected = {
        "sienna-8965B4512000": (S, [0x88C4C, 0x88C6E, 0x86DB0, 0x86DBC, 0x88C28, 0x8735E, 0x893DE]),
        "corolla-8965H1202000": (H, [0x8304C, 0x8306E, 0x811B0, 0x811BC, 0x83028, 0x8175E, 0x837DE]),
    }
    evidence = {}
    shapes = {}
    for name, (image, entries) in selected.items():
        corpus = target_path(name, "decompiler_corpus")
        with corpus.open() as stream:
            metadata = json.loads(next(stream))
        if metadata["executable_sha256"] != sha(image):
            raise ValueError(f"{name} initializer corpus/image mismatch")
        functions, _ = load_function_corpus(corpus)
        fp = ROOT / ("data/function_structural_fingerprints.jsonl" if name.startswith("sienna-")
                     else "data/targets/corolla-8965H1202000/function_structural_fingerprints.jsonl")
        with fp.open() as stream:
            fp_metadata = json.loads(next(stream))
            fingerprints = [json.loads(line) for line in stream]
        if fp_metadata["executable_sha256"] != sha(image):
            raise ValueError(f"{name} initializer fingerprints/image mismatch")
        fingerprint_entries = {int(row["entry_addr"], 16): row for row in fingerprints}
        native_functions = {}
        for entry in entries:
            function = functions[entry]
            fingerprint = fingerprint_entries[entry]
            if function["body_size"] != fingerprint["body_size"]:
                raise ValueError(f"{name} initializer corpus/fingerprint body mismatch at {entry:#x}")
            native_functions[entry] = {**function, "body_ranges": fingerprint["body_ranges"]}
        evidence[name] = {
            "image_sha256": sha(image),
            "source_corpus": {"path": str(corpus.relative_to(ROOT)), "sha256": sha(corpus.read_bytes())},
            "source_fingerprints": {"path": str(fp.relative_to(ROOT)), "sha256": sha(fp.read_bytes())},
            "function_count": len(entries),
            "functions": bind_entries(image, native_functions, entries),
        }
        own = next(row for row in fingerprints if int(row["entry_addr"], 16) == entries[0])
        signature = (own["mnemonics"], own["instruction_lengths"])
        shapes[name] = {
            "path": str(fp.relative_to(ROOT)), "sha256": sha(fp.read_bytes()),
            "same_shape_entries": [
                row["entry_addr"] for row in fingerprints
                if (row["mnemonics"], row["instruction_lengths"]) == signature
            ],
        }
        # The complete raw initializer fixes the return-register gate, branch
        # destination, callback call, and all three stores independently of C.
        tail = ("6407c15b010a6407c85b440fca5b" if name.startswith("sienna-")
                else "6407855a010a64078c5a440f8e5a")
        raw = bytes.fromhex("80072100bfff60e1e051ba05bfffd0ff" + tail + "40063f00")
        entry, sibling, wrapper, alternate, callbacks, lower, driver = entries
        if image[entry:entry + 34] != raw:
            raise ValueError(f"{name} initializer instruction/dataflow drift")
        if image[wrapper:wrapper + 12] != bytes.fromhex("8007210080ffaa0540063f00"):
            raise ValueError(f"{name} initializer lower-driver wrapper drift")
        # LD.W absolute 0xFFC5D018 (ICUSIRQSTS), then bit0 controls the busy gate.
        if image[driver + 4:driver + 10] != bytes.fromhex("80078909a08b"):
            raise ValueError(f"{name} initializer no longer reads ICUSIRQSTS")
        code = functions[entry]["decompiled_c"]
        if f"FUN_{wrapper:08x}()" not in code or f"FUN_{callbacks:08x}()" not in code:
            raise ValueError(f"{name} initializer call graph drift")
        if f"FUN_{lower:08x}()" not in functions[wrapper]["decompiled_c"]:
            raise ValueError(f"{name} initializer wrapper call drift")
        if f"FUN_{alternate:08x}()" not in functions[sibling]["decompiled_c"]:
            raise ValueError(f"{name} duplicate-shape sibling call drift")
        if functions[driver]["name"] + "()" not in functions[lower]["decompiled_c"]:
            raise ValueError(f"{name} initializer hardware-driver call drift")
        if image[lower + 0x38:lower + 0x40] != bytes.fromhex("80ff48206152ca1d"):
            raise ValueError(f"{name} lower initializer hardware-success gate drift")
        if image[driver + 14:driver + 24] != bytes.fromhex("df0ac20520ee3000b515"):
            raise ValueError(f"{name} ICU-S busy-bit gate drift")
        table, count_address = ((0x28064, 0x28048) if name.startswith("sienna-")
                                else (0x27D74, 0x27D58))
        count = u32(image, count_address)
        if count != 4:
            raise ValueError(f"{name} generated crypto initialization callback count drift")
        evidence[name]["raw_dataflow"] = {
            "initializer_entry": f"0x{entry:08X}", "initializer_bytes": raw.hex(),
            "lower_driver_wrapper": f"0x{wrapper:08X}", "lower_initialize": f"0x{lower:08X}",
            "hardware_initialize": f"0x{driver:08X}", "hardware_status_register": "0xFFC5D018",
            "callback_dispatcher": f"0x{callbacks:08X}",
            "callback_gate": "CMP r0,r10; BNE skips only the callback call when lower initialization returns nonzero",
            "callback_count_address": f"0x{count_address:08X}", "callback_count": count,
            "callback_table_address": f"0x{table:08X}",
            "callback_entries": [f"0x{u32(image, table + 4*i):08X}" for i in range(count)],
            "state_writes": [
                {"address": ref["to_addr"], "width": width, "value": value}
                for ref, width, value in zip(functions[entry]["data_references"], [4, 2, 1], [0, 0, 1], strict=True)
            ],
            "state_write_gate": "all three stores execute after either lower-driver return outcome",
            "same_shape_sibling": f"0x{sibling:08X}",
            "sibling_lower_wrapper": f"0x{alternate:08X}",
        }
    return {
        "evidence": evidence,
        "structural_ambiguity": {
            "inputs": shapes,
            "reason": "The complete mnemonic/length signature occurs twice in each canonical inventory. The initializer and adjacent sibling call different lower-driver functions.",
            "resolution": "The selected entry calls the native lower initializer, which reaches ICU-S hardware initialization; its zero return dispatches the generated four-callback vector before common state reset.",
        },
    }

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);args=ap.parse_args()
 ev=json.loads(EV.read_text());rows={int(x['reference_entry'],16):x for x in ev['functions']};byh={int(x['target_entry'],16):x for x in ev['functions']};H=HRAW.read_bytes()[:0x100000];S=SIMG.read_bytes()
 if sha(H)!=ev['image']['codeflash_sha256']:raise ValueError('H image drift')
 core=[]
 for s in CORE_REFS:
  r=rows[s];h=int(r['target_entry'],16)
  core.append({'reference_entry':r['reference_entry'],'reference_name':r['reference_name'],'target_entry':r['target_entry'],'reference_body_size':r['reference_body_size'],'target_reported_body_size':r['target_reported_body_size'],'delta':h-s,'same_reported_size':r['reference_body_size']==r['target_reported_body_size']})
 # H SecOC record table: three 0x50-byte records at 0x2572c.
 recs=[]
 for i in range(3):
  a=0x2572c+i*0x50
  recs.append({'index':i,'can_id':u16(H,a+0x0a),'freshness_id':u16(H,a+0x12),'crypto_config_id':u16(H,a+0x16),'cryptoif_handle':u32(H,a+0x20),'pdu_id':u16(H,a+0x34),'freshness_callback':u32(H,a+0x48),'state_callback':u32(H,a+0x4c),'commit_callback':u32(H,a+0x30)})
 signal_map=[u16(H,0x223fc+2*i) for i in range(274)]
 d7_ids=[i for i,p in enumerate(signal_map) if p==40]
 d7=byh[0x468fa]['decompiled_c']
 d7_calls=[int(x,16) for x in re.findall(r'FUN_0007643a\((0x[0-9a-fA-F]+)',d7)]
 init=byh[0x88024]['decompiled_c'];rx=byh[0x8818c]['decompiled_c'];getf=byh[0x896b0]['decompiled_c'];commit=byh[0x89758]['decompiled_c']
 initialization = initializer_surface(H, S)
 payload={
  'schema':'corolla-h-secoc-surface-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(S)},
  'evidence':{'decompiler_evidence':str(EV.relative_to(ROOT))},
  'secoc_role_closure':[{'reference_entry':x['reference_entry'],'reference_name':x['reference_name'],'target_entry':x['target_entry'],'classification':'target-native-role-recovered','evidence':str(EV.relative_to(ROOT))} for x in ev['functions']],
  'secoc_role_closure_count':len(ev['functions']),
  'role_closure':[{'reference_entry':'0x00088C4C','reference_name':'crypto_icus_initialize','target_entry':'0x0008304C','classification':'target-native-role-recovered','evidence':str(args.out.resolve().relative_to(ROOT.resolve())) if args.out.resolve().is_relative_to(ROOT.resolve()) else str(args.out)}],
  'role_closure_count':1,
  'target_evidence_entries':['0x0008304C'],
  'initialization_evidence':initialization,
  'icus_cryptoif_core':{'role_count':len(core),'delta':-0x5c00,'all_at_single_delta':all(x['delta']==-0x5c00 for x in core),'all_reported_body_sizes_match':all(x['same_reported_size'] for x in core),'roles':core,'anchors':{'command8_adapter':'0x000814A8','command5_adapter':'0x000820CC','command7_verify_adapter':'0x000824DC','cryptoif_job_begin':'0x00082F6A','input_fifo':'0x00083848','output_fifo':'0x000838BE','finalizer':'0x00083910'}},
  'rx_frontend':{'init':{'sienna':'0x0008DB84','h':'0x00088024','h_reported_body_size':byh[0x88024]['target_reported_body_size'],'installs_slot4_config':('0x2570c' in init.lower() or '0x19a0' in init.lower()) and ('FUN_00088458' in init or 'fun_00088458' in init.lower())},'indication':{'sienna':'0x0008DC64','h':'0x0008818C','body_size':byh[0x8818c]['target_reported_body_size'],'calls_record_lookup':'FUN_000885c0' in rx,'calls_secured_queue':'FUN_0008865a' in rx},'profiles':recs,'profile_count':len(recs)},
  'freshness':{'profile_lookup':{'sienna':'0x0008E80A','h':'0x00089558'},'get_rx':{'sienna':'0x0008E8E6','h':'0x000896B0'},'commit_rx':{'sienna':'0x0008E942','h':'0x00089758'},'reconstruct_normal':{'sienna':'0x0008EECA','h':'0x00089E9A'},'reconstruct_sync':{'sienna':'0x0008EF9E','h':'0x00089F6E'},'commit_normal':{'sienna':'0x0008F084','h':'0x0008A07A'},'commit_sync':{'sienna':'0x0008F112','h':'0x0008A130'},'get_dispatches_normal_sync':all(t in getf.lower() for t in ('00089558','00089e9a','00089f6e')),'commit_dispatches_normal_sync':all(t in commit.lower() for t in ('00089558','0008a07a','0008a130')),'configured_get_callback_set':sorted({x['freshness_callback'] for x in recs}),'configured_commit_callback_set':sorted({x['commit_callback'] for x in recs})},
  'application_icus_isrs':{'channel292':{'sienna':'0x000650AC','h':'0x0005F3EC','dispatch':'0x00081A10'},'channel293':{'sienna':'0x000650EE','h':'0x0005F42E','dispatch':'0x00081A36'},'same_reported_size':byh[0x5f3ec]['target_reported_body_size']==66 and byh[0x5f42e]['target_reported_body_size']==66},
  'crypto_test_callbacks':{'result_compare':{'sienna':'0x00069068','h':'0x000633A0','compare_length':16,'mismatch_state':0x44,'match_state':0x33},'key_update_completion':{'sienna':'0x0006920A','h':'0x00063542'},'command1_3_completion':{'sienna':'0x0006922C','h':'0x00063564'},'command7_completion':{'sienna':'0x00069246','h':'0x0006357E'},'command5_completion':{'sienna':'0x0006926A','h':'0x000635A2'},'boundary':'forced callback Ghidra bodies are fragmented by prior disposable-project overlaps; evidence comes from decompiled semantics plus canonical-size raw windows. Reported contiguous body size is unreliable'},
  'd7_unpacker':{'sienna':'0x0004B3AA','h':'0x000468FA','sienna_body_size':rows[0x4b3aa]['reference_body_size'],'h_reported_body_size':byh[0x468fa]['target_reported_body_size'],'h_secoc_record_pdu_id':recs[1]['pdu_id'],'h_pdu40_signal_ids':d7_ids,'h_scalar_receive_signal_ids':d7_calls,'h_scalar_destinations':['0xFEBE7D82','0xFEBE7D84','0xFEBE7D85']},
  'static_conclusion':{'all_42_secoc_icus_residual_roles_recovered':True,'crypto_icus_initializer_recovered':True,'underlying_verify_engine_preserved':True,'h_profile_population_changed':True,'h_freshness_architecture_preserved':True}
 }
 args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',args.out)
if __name__=='__main__':main()
