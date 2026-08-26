#!/usr/bin/env python3
"""Verify exact-H/F command-5 portability and the non-transfer of Sienna RAM placement."""
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
ART=REPO/'data/generated/corolla_hf_command5_portability.json'
BUILDER=REPO/'tools/build_corolla_hf_command5_portability.py'
H=REPO/'community/albinoelephant/normalized/8965H1202000_CodeFlash.bin'
passed=failed=0

def check(name, cond):
 global passed,failed
 if cond: passed+=1; print(f'[PASS][raw_bytes] {name}')
 else: failed+=1; print(f'[FAIL][raw_bytes] {name}')

def sha(b): return hashlib.sha256(b).hexdigest()

art=json.loads(ART.read_text()); h=H.read_bytes()
check('schema exact',art['schema']=='corolla-hf-command5-portability-v1')
check('applies to H/F only',art['applies_to']==['8965H1202000','8965F1208000'])
core=art['command5_core']; fields=core['record_fields']
check('record0 raw bytes exact',core['driver_record_address']=='0x00027C88' and core['driver_record_raw_hex']==h[0x27C88:0x27CA8].hex())
check('record0 completion callback exact',fields['completion_callback']=='0x00082F5C')
check('record0 adapter exact',fields['adapter_callback']=='0x000820CC')
check('record0 worker exact',fields['worker_callback']=='0x000821D0')
check('record0 config pointer exact',fields['config_pointer']=='0x00027C84' and core['config_type_word']==1)
check('serialized command5 dispatcher exact',core['serialized_dispatcher']=='0x00082750' and core['record_lookup']=='0x00082702')
check('variable length command5 input supports B6 36 bytes',core['variable_length_prepare']=='0x00081E94' and core['maximum_input_bytes']==80 and core['b6_authenticated_input_bytes']==36 and core['b6_authenticated_input_fits'])
check('lower ICU-S command5 engine exact',core['lower_icus_engine']=='0x00083A30' and core['command_word_formula']=='(key_selector << 16) | 5')
check('record0 completion state exact',core['synchronous_wrapper']=='0x00082ED2' and core['done_flag']=='0xFEBF1280' and core['status_flag']=='0xFEBF1281')
check('H/F application command5 path byte-identical',core['h_f_application_byte_identical'] is True)
rb=art['resident_runtime_boundary']
check('Sienna resident geometry explicitly does not transfer',rb['sienna_single_stage_geometry_transfers'] is False and rb['h_f_verified_ram_exec_requirement_entry_present'] is False)
check('H startup clear ranges exact',rb['h_startup_clear_ranges_inclusive']==[['0xFEBF05CC','0xFEBF09CB'],['0xFEBF0B4C','0xFEBF0F4B']])
check('naive FEBF0000 Sienna proxy rejected', 'does not authorize the Sienna 546-byte proxy' in rb['interpretation'] and 'TMS-054' in rb['interpretation'])
two=art['two_stage_candidate']
check('TMS053 two-stage shadow idea retained as historical bounded hypothesis',two['status'].startswith('historical-tms053') and two['xcp_write_shadow_bounds']==['0xFEBF7C00','0xFEBFFBFF'] and 'TMS-054' in two['interpretation'] and 'Neither artifact proves' in two['interpretation'])
con=art['static_conclusion']
check('software machinery transfer closed',con['h_f_command5_software_machinery_transfers'] and con['b6_36_byte_input_supported'])
check('resident signer and live policy remain open',not con['h_f_resident_signer_runtime_closed'] and not con['slot4_live_permission_closed'] and not con['signing_latency_closed'])
check('evidence boundary rejects working-oracle overclaim','working H/F' in art['evidence_boundary'] and 'still requires live carrier retention' in art['evidence_boundary'])
with tempfile.TemporaryDirectory(prefix='hf-command5-port-') as td:
 out=Path(td)/'a.json'
 p=subprocess.run([sys.executable,str(BUILDER),'--out',str(out)],cwd=REPO,capture_output=True,text=True)
 check('builder exits cleanly',p.returncode==0)
 check('builder reproduces artifact exactly',out.exists() and json.loads(out.read_text())==art)
print(f'\nResults: {passed} passed, {failed} failed')
raise SystemExit(1 if failed else 0)
