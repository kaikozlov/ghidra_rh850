#!/usr/bin/env python3
"""Close the final 34 genuinely-unresolved canonical names for Corolla 8965H1202000.

Every promotion is target-native.  One canonical role (boot TAUJ0 CH2 EIINT 0x1087)
is intentionally closed by complete target-table recensus rather than a fake homolog.
"""
from __future__ import annotations
import argparse, hashlib, json, re, struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
EVID=ROOT/'data/generated/corolla_8965H1202000_final_named_residue_evidence.json'
OUT=ROOT/'data/generated/corolla_8965H1202000_final_named_residue.json'

ROLES=[
 ('boot_eiint_dispatch',0x748,0x72C,'boot-shared-block-byte-transfer'),
 ('boot_default_exception_handler',0x1E1E,0x1E02,'boot-handler-exact-shift'),
 ('boot_secondary_exception_handler',0x1E2A,0x1E0E,'boot-handler-exact-shift'),
 ('memory_crc_verify_result',0x47DE,0x47C2,'crc-peripheral-cluster'),
 ('memory_crc_verify_busy',0x47E4,0x47C8,'crc-peripheral-cluster'),
 ('crc32_hardware_compute',0x47EA,0x47CE,'crc-peripheral-cluster'),
 ('application_entry',0x20880,0x20880,'application-handoff-pointer'),
 ('application_programming_reset_marker_clear',0x4C986,0x482AE,'programming-readiness-call-slot'),
 ('application_ram_range_allowed',0x4EA78,0x4A4D4,'ram-policy-table-transfer'),
 ('application_event_record_query',0x4F8BA,0x4AF74,'proprietary-ab-event-call-chain'),
 ('application_event_active_id_list',0x54748,0x4FE70,'event-query-call-slot'),
 ('application_event_state_query',0x548B0,0x4FFD8,'event-query-call-slot'),
 ('application_event_detail_query',0x54BF2,0x5031A,'event-query-call-slot'),
 ('application_rx_signal_consumer_56fc2',0x56FC2,0x5262C,'dual-owner-singleton-intersection'),
 ('application_ram_default_init',0x57BFE,0x5316C,'scheduler-call-slot'),
 ('rte_input_staging_copy_c',0x5B9C4,0x56BAC,'scheduler-call-slot'),
 ('rte_input_staging_copy_b',0x5C0B6,0x5722E,'scheduler-call-slot'),
 ('rte_input_staging_copy_a',0x5C666,0x5778E,'scheduler-call-slot'),
 ('application_default_exception_handler',0x61D88,0x5C0F2,'application-vector-table'),
 ('application_vector_0x90_handler',0x64B3E,0x5EE7E,'application-vector-table'),
 ('application_timer_peripheral_reload',0x6547C,0x5F812,'fixed-peripheral-successor'),
 ('tauj0_ch0_sample_snapshot',0x6578E,0x5FB30,'tauj0-ch0-successor-chain'),
 ('boot_shutdown_reset_path',0x7059E,0x6A93E,'ecm-wrapper-embedded-jump'),
 ('application_programming_lower_request_stub',0x8A01C,0x8441C,'repeated-programming-call-slot'),
 ('application_proprietary_ab_event_worker',0x8CF84,0x87384,'proprietary-ab-thunk-chain'),
 ('application_read_memory_by_address_request_poll',0x946FA,0x8F720,'sid23-phase-call-slot'),
 ('application_read_memory_by_address_request_start',0x9479A,0x8F7C0,'sid23-phase-call-slot'),
 ('timer_expiry_07_callback',0x94B86,0x8FBAC,'expiry-table-index'),
 ('application_proprietary_ab_selector_worker',0x96918,0x9193E,'sidab-common-worker'),
 ('system_programming_shutdown_mode_entry',0xB20EA,0xB1F68,'mode9-transition-table'),
 ('fd0d7_status_fault_monitor',0xB6396,0xB5EA4,'consolidated-fd0d7-successor'),
 ('application_input_snapshot_update',0xBCB3A,0xBBA48,'per-tick-final-call'),
 ('application_substate_machine',0xCBCC8,0xCF27E,'single-child-wrapper'),
]
REMOVED=(0x1E44,'boot_tauj0_ch2_isr')

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def fmt(x:int)->str:return f'0x{x:08X}'
def u32(b:bytes,a:int)->int:return struct.unpack_from('<I',b,a)[0]
def fpmap(items):return {int(x['entry'],16):x for x in items}
def calls(fp,a):return [int(x,16) for x in fp[a]['direct_call_targets']]
def rh850_br(blob:bytes,a:int):
    if a<0 or a+4>len(blob):return None
    w0,w1=struct.unpack_from('<HH',blob,a)
    if ((w0>>6)&0x1f)!=0x1e or (w1&1):return None
    reg=(w0>>11)&0x1f;hi=w0&0x3f
    if hi&0x20:hi-=0x40
    return ('jarl' if reg else 'jr',a+(hi<<16)+w1)
def jarl_calls(blob:bytes,a:int,n:int):
    return [(x-a,d[1]) for x in range(a,a+n-3,2) if (d:=rh850_br(blob,x)) and d[0]=='jarl' and 0<=d[1]<0x100000]
def exact_shift(s,h,sa,ha,n):return s[sa:sa+n]==h[ha:ha+n]
def require(cond,msg):
    if not cond:raise ValueError(msg)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);args=ap.parse_args()
    s=SRAW.read_bytes();h=HRAW.read_bytes()[:0x100000];ev=json.loads(EVID.read_text())
    require(ev['images']['sienna_sha256']==sha(s) and ev['images']['h_sha256']==sha(h),'final evidence image hash mismatch')
    sf=fpmap(ev['sienna_fingerprints']);hf=fpmap(ev['h_fingerprints']);hd={int(x['entry'],16):x for x in ev['h_decompiler']}
    for a,r in sf.items(): require(sha(s[a:a+r['body_size']])==r['body_sha256'],f'S fp raw drift {a:#x}')
    for a,r in hf.items(): require(sha(h[a:a+r['body_size']])==r['body_sha256'],f'H fp raw drift {a:#x}')
    for a,r in hd.items():
        require(sha(h[a:a+r['body_size']])==r['body_sha256'] and sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'],f'H decomp drift {a:#x}')

    claims={}
    # Boot dispatcher is a non-contiguous canonical body embedded in shared startup code.
    require(s[0x730:0x770]==h[0x714:0x754],'boot shared dispatcher region no longer transfers at -0x1c')
    require(s[0x748:0x750]==h[0x72C:0x734] and s[0x756:0x75A]==h[0x73A:0x73E],'boot dispatcher owned ranges drifted')
    s_boot=[struct.unpack_from('<II',s,0x869C+i*8) for i in range(8)]
    h_boot=[struct.unpack_from('<II',h,0x869C+i*8) for i in range(4)]
    require(s_boot==[(0x1087,0x1E44),(0x10B8,0x1E50),(0x10B9,0x1E5E),(0x10BB,0x1E6C),(0x10BC,0x1E7A),(0x10C0,0x1E88),(0x10C1,0x1E96),(0xFFFFFFFF,0x1EA4)],'S boot EIINT table drift')
    require(h_boot==[(0x10BC,0x1E5E),(0x10C0,0x1E6C),(0x10C1,0x1E7A),(0xFFFFFFFF,0x1E88)],'H boot EIINT table drift')
    require(0x1087 not in [x for x,_ in h_boot],'H unexpectedly restored boot TAUJ0 CH2 EIINT role')
    claims['boot_eiint']={'sienna_rows':[[fmt(a),fmt(b)] for a,b in s_boot],'h_rows':[[fmt(a),fmt(b)] for a,b in h_boot],
      'dispatcher_shift':-0x1C,'dispatcher_target':'0x0000072C','removed_codes':['0x00001087','0x000010B8','0x000010B9','0x000010BB']}
    require(exact_shift(s,h,0x1E1E,0x1E02,8) and exact_shift(s,h,0x1E2A,0x1E0E,12),'boot exception handlers no longer exact at -0x1c')
    s_sec=[(a,d[0]) for a in range(0,0x2000,2) if (d:=rh850_br(s,a)) and d[1]==0x1E2A]
    h_sec=[(a,d[0]) for a in range(0,0x2000,2) if (d:=rh850_br(h,a)) and d[1]==0x1E0E]
    require(s_sec==[(0xD2,'jr')] and h_sec==[(0xD2,'jr')],'secondary exception vector JR drift')

    # CRC fixed peripheral semantics.
    require(exact_shift(s,h,0x47DE,0x47C2,6) and exact_shift(s,h,0x47E4,0x47C8,6),'CRC status helpers drift')
    crc=hd[0x47CE]['decompiled_c']
    require(all(x.lower() in crc.lower() for x in ['ffd51020','ffd51004','ffd51000']),'H CRC peripheral registers missing')
    claims['crc']={'result':'0x000047C2','busy':'0x000047C8','compute':'0x000047CE','fixed_registers':['0xFFD51020','0xFFD51004','0xFFD51000']}

    # Application entry handoff.
    require(u32(s,0xFFDB8)==0x20880 and u32(h,0xFFDB8)==0x20880,'application handoff pointer drift')
    require(0x20880 in hf and hf[0x20880]['body_size']==12,'H application entry thunk missing')

    # Programming helper call-slot invariants.
    for sa,ha in [(0x8A0C2,0x844C2),(0x8A482,0x84882),(0x8A542,0x84942)]:
        require(calls(sf,sa)[0]==0x8A01C and calls(hf,ha)[0]==0x8441C,f'programming lower stub slot drift at {sa:#x}')
    require(calls(sf,0x8A08E)[1]==0x4C986 and calls(hf,0x8448E)[1]==0x482AE,'programming reset marker call slot drift')

    # RAM range policy: same validator except relocated target-native exclusion table.
    require(sum(x==y for x,y in zip(s[0x4EA78:0x4EA78+66],h[0x4A4D4:0x4A4D4+66]))==64,'RAM validator no longer 64/66-byte transfer')
    s_ranges=[struct.unpack_from('<II',s,0x293F4+i*8) for i in range(5)]
    h_ranges=[struct.unpack_from('<II',h,0x28F0C+i*8) for i in range(5)]
    require(s_ranges[0]==h_ranges[0] and s_ranges[3]==h_ranges[3] and len(h_ranges)==5,'RAM exclusion architecture drift')
    claims['ram_policy']={'sienna_table':'0x000293F4','h_table':'0x00028F0C','sienna_ranges':[[fmt(a),fmt(b)] for a,b in s_ranges],'h_ranges':[[fmt(a),fmt(b)] for a,b in h_ranges]}

    # RMBA phase dispatcher and proprietary 0xAB chain use raw call offsets.
    require(jarl_calls(s,0x948AA,64)==[(0xC,0x9479A),(0x18,0x9486C),(0x22,0x946FA),(0x34,0x946FA)],'S RMBA phase layout drift')
    require(jarl_calls(h,0x8F8D0,64)==[(0xC,0x8F7C0),(0x18,0x8F892),(0x22,0x8F720),(0x34,0x8F720)],'H RMBA phase layout drift')
    require(jarl_calls(s,0x968A6,114)[1]==(0x2E,0x96B5A) and jarl_calls(h,0x918CC,114)[1]==(0x2E,0x91B80),'AB event thunk slot drift')
    require(jarl_calls(s,0x96B5A,12)==[(0x4,0x8CF84)] and jarl_calls(h,0x91B80,12)==[(0x4,0x87384)],'AB event worker thunk target drift')
    s_event=jarl_calls(s,0x8CF84,364); h_event=jarl_calls(h,0x87384,364)
    require([(o,t) for o,t in s_event if t==0x4F8BA]==[(0x66,0x4F8BA),(0xA2,0x4F8BA)],'S event-query positions drift')
    require([(o,t) for o,t in h_event if t==0x4AF74]==[(0x66,0x4AF74),(0xA2,0x4AF74)],'H event-query positions drift')
    require(jarl_calls(s,0x4F8BA,110)[:3]==[(0x2E,0x54BF2),(0x36,0x54748),(0x44,0x548B0)],'S event-query child order drift')
    require(jarl_calls(h,0x4AF74,110)[:3]==[(0x2E,0x5031A),(0x36,0x4FE70),(0x44,0x4FFD8)],'H event-query child order drift')

    # Timer expiry table uniquely re-identified by stable neighboring slots.
    s_exp=list(struct.unpack_from('<9I',s,0x26DA0));h_exp=list(struct.unpack_from('<9I',h,0x26AB0))
    require(s_exp[7:]==[0x94B86,0x94B86] and h_exp[7:]==[0x8FBAC,0x8FBAC],'timer expiry slot7 drift')
    claims['timer_expiry']={'sienna_base':'0x00026DA0','h_base':'0x00026AB0','sienna_targets':[fmt(x) for x in s_exp],'h_targets':[fmt(x) for x in h_exp]}

    # System transition mode 9 table.
    require(struct.unpack_from('<II',s,0xAEB48)==(0xB20EA,0xB213A) and struct.unpack_from('<II',h,0xAEB48)==(0xB1F68,0xB1FB8),'mode9 transition pair drift')

    # RTE/application owner call graph.
    require(set(calls(hf,0x5389C)) & set(calls(hf,0x58BBC)) == {0x5262C},'RX consumer is no longer singleton common H callee')
    require(calls(sf,0x5778C)[1]==0x57BFE and calls(hf,0x52CFA)[1]==0x5316C,'RAM default init owner slot drift')
    require(calls(sf,0x57980)==[0x5B9C4,0x5BEA6,0x6F110,0x6F116,0xFDC3C,0xFDC50],'S RTE-C owner order drift')
    require(calls(hf,0x52EEE)==[0x56BAC,0x5701E,0x694B0,0x694B6,0xFDC3C,0xFDC50],'H RTE-C owner order drift')
    require(calls(sf,0x57A7E)==[0x5C0B6,0x5C56A,0x5C666,0x6F110,0x6F116,0xFDC64,0xFDC78,0xFDC8C],'S RTE A/B owner order drift')
    require(calls(hf,0x52FEC)==[0x5722E,0x57692,0x5778E,0x694B0,0x694B6,0xFDC64,0xFDC78,0xFDC8C],'H RTE A/B owner order drift')

    # Application direct exception vector table.
    default_slots=[0x20014,0x20024,0x20034,0x20044,0x20054,0x20064,0x20074,0x20084,0x200A4,0x200B4,0x200C4,0x200E4,0x200F4]
    require(all(u32(s,x)==0x61D88 for x in default_slots) and all(u32(h,x)==0x5C0F2 for x in default_slots),'application default vector role drift')
    require(u32(s,0x20094)==0x64B3E and u32(h,0x20094)==0x5EE7E,'application vector 0x90 role drift')

    # Timer reload fixed hardware ownership and H-only extra channel.
    tr=hd[0x5F812]['decompiled_c']
    require(all(x in tr for x in ['Ramffe20000','Ramffe21000','Ramffe21008','Ramffe50000']),'H timer reload fixed peripheral set drift')

    # CH0 sample successor: mapped CH0 body -> regenerated intermediate -> snapshot publisher.
    require(calls(sf,0x64F18)[3]==0x656F0 and calls(hf,0x5F258)[3]==0x5FA96,'CH0 body fourth-child owner drift')
    require(0x6578E in calls(sf,0x656F0) and calls(hf,0x5FA96)==[0x52DBA,0x5B9AE,0x5FB30],'CH0 snapshot successor chain drift')
    snap=hd[0x5FB30]['decompiled_c'];require('FUN_0005bcba' in snap and 'FUN_0005bd3a' in snap and snap.count('*(undefined2 *)')>=8,'H snapshot publisher semantics drift')

    # ECM shutdown direct JMP target is embedded at identical wrapper offset +D0.
    require(s[0x70A54+0xD0:0x70A54+0xD6].hex()=='e0069e050700' and h[0x6ADF4+0xD0:0x6ADF4+0xD6].hex()=='e0063ea90600','ECM shutdown embedded JMP drift')

    # Per-tick ownership for input snapshot and expanded 0D7 fault monitor.
    require(calls(sf,0xBEC4C)[-1]==0xBCB3A and calls(hf,0xBD954)[-1]==0xBBA48,'input snapshot final-call role drift')
    require(0xB6396 in calls(sf,0xBEC4C) and 0xB5EA4 in calls(hf,0xBD954),'0D7 monitor owner call missing')
    fd=hd[0xB5EA4]['decompiled_c'];require('FUN_000b0374(0x2d)' in fd.lower() or 'FUN_000b0374(0x2d)' in fd,'H 0D7 successor lost event 0x2D')
    require(calls(sf,0xB893E)==[0xCBCC8] and calls(hf,0xB73F0)==[0xCF27E],'substate single-child wrapper drift')

    closures=[{'reference_entry':fmt(ref),'reference_name':name,'target_entry':fmt(target),'role':basis} for name,ref,target,basis in ROLES]
    recens=[{'reference_entry':fmt(REMOVED[0]),'reference_name':REMOVED[1],'reason':'H complete boot EIINT table removes code 0x1087; H 0x1E5E belongs to code 0x10BC and must not be misidentified as TAUJ0 CH2'}]
    payload={'schema':'corolla-h-final-named-residue-v1','software_id':'8965H1202000','images':{'sienna_sha256':sha(s),'h_sha256':sha(h)},
      'evidence':{'final_compact_evidence':str(EVID.relative_to(ROOT)),'final_compact_evidence_sha256':sha(EVID.read_bytes())},
      'claims':claims,'role_closure':closures,'role_closure_count':len(closures),'surface_recensus':recens,'surface_recensus_count':len(recens),
      'target_evidence_entries':[fmt(x) for x in sorted({target for _,_,target,_ in ROLES})],
      'static_conclusion':{'all_34_prior_unresolved_names_closed':len(closures)==33 and len(recens)==1,'direct_target_native_successors':33,'removed_target_surface_roles':1,
        'boundary':'Zero genuinely-unresolved canonical names means every canonical named role has exact-body, target-native role, target-surface recensus, or target-native inspection evidence. It does not promote structural-only candidates or imply field-for-field equivalence for consolidated/generated successors.'}}
    args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print(f'wrote {args.out}: {len(closures)} roles + {len(recens)} recensus')
if __name__=='__main__':main()
