#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'data/generated/corolla_8965H1202000_final_named_residue.json'
EVID=ROOT/'data/generated/corolla_8965H1202000_final_named_residue_evidence.json'
TOOL=ROOT/'tools/build_corolla_h_final_named_residue.py'
SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'
HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());e=json.loads(EVID.read_text());s=SRAW.read_bytes();h=HRAW.read_bytes()[:0x100000]
check('image hashes pinned',d['images']['sienna_sha256']==sha(s) and d['images']['h_sha256']==sha(h) and e['images']==d['images'])
check('compact evidence raw-bound',all(sha((s if k=='sienna_fingerprints' else h)[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] for k in ('sienna_fingerprints','h_fingerprints') for r in e[k]))
check('33 roles + one recensus close final 34',d['role_closure_count']==33 and d['surface_recensus_count']==1 and d['static_conclusion']['all_34_prior_unresolved_names_closed'])
check('boot dispatcher transferred at -0x1C',d['claims']['boot_eiint']['dispatcher_target']=='0x0000072C' and d['claims']['boot_eiint']['dispatcher_shift']==-0x1c and s[0x730:0x770]==h[0x714:0x754])
check('H boot EIINT table shrinks to 10BC/10C0/10C1/default',[x[0] for x in d['claims']['boot_eiint']['h_rows']]==['0x000010BC','0x000010C0','0x000010C1','0xFFFFFFFF'])
check('boot TAUJ0 CH2 is removed, not remapped',d['surface_recensus']==[{'reason':'H complete boot EIINT table removes code 0x1087; H 0x1E5E belongs to code 0x10BC and must not be misidentified as TAUJ0 CH2','reference_entry':'0x00001E44','reference_name':'boot_tauj0_ch2_isr'}])
check('boot exception handlers exact at -0x1C',s[0x1e1e:0x1e26]==h[0x1e02:0x1e0a] and s[0x1e2a:0x1e36]==h[0x1e0e:0x1e1a])
roles={x['reference_name']:x['target_entry'] for x in d['role_closure']}
check('CRC trio exact',roles['memory_crc_verify_result']=='0x000047C2' and roles['memory_crc_verify_busy']=='0x000047C8' and roles['crc32_hardware_compute']=='0x000047CE')
check('application entry remains 20880',roles['application_entry']=='0x00020880')
check('RAM policy maps to 4A4D4',roles['application_ram_range_allowed']=='0x0004A4D4' and d['claims']['ram_policy']['h_table']=='0x00028F0C')
check('event-query cone exact',{n:roles[n] for n in ['application_event_record_query','application_event_active_id_list','application_event_state_query','application_event_detail_query']}=={'application_event_record_query':'0x0004AF74','application_event_active_id_list':'0x0004FE70','application_event_state_query':'0x0004FFD8','application_event_detail_query':'0x0005031A'})
check('RMBA start/poll exact',roles['application_read_memory_by_address_request_start']=='0x0008F7C0' and roles['application_read_memory_by_address_request_poll']=='0x0008F720')
check('proprietary AB workers exact',roles['application_proprietary_ab_selector_worker']=='0x0009193E' and roles['application_proprietary_ab_event_worker']=='0x00087384')
check('RTE copy trio exact',[roles[x] for x in ['rte_input_staging_copy_c','rte_input_staging_copy_b','rte_input_staging_copy_a']]==['0x00056BAC','0x0005722E','0x0005778E'])
check('application exception vectors exact',roles['application_default_exception_handler']=='0x0005C0F2' and roles['application_vector_0x90_handler']=='0x0005EE7E')
check('changed generated successors pinned',roles['application_timer_peripheral_reload']=='0x0005F812' and roles['tauj0_ch0_sample_snapshot']=='0x0005FB30' and roles['fd0d7_status_fault_monitor']=='0x000B5EA4' and roles['application_input_snapshot_update']=='0x000BBA48')
check('system/scheduler successors pinned',roles['application_rx_signal_consumer_56fc2']=='0x0005262C' and roles['application_ram_default_init']=='0x0005316C' and roles['application_substate_machine']=='0x000CF27E')
check('shutdown/programming/timer targets pinned',roles['boot_shutdown_reset_path']=='0x0006A93E' and roles['application_programming_lower_request_stub']=='0x0008441C' and roles['application_programming_reset_marker_clear']=='0x000482AE' and roles['timer_expiry_07_callback']=='0x0008FBAC' and roles['system_programming_shutdown_mode_entry']=='0x000B1F68')
check('zero-residue boundary does not overclaim','does not promote structural-only candidates' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
