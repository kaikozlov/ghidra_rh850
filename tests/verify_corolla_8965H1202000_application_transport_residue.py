#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'data/generated/corolla_8965H1202000_application_transport_residue.json';TOOL=ROOT/'tools/build_corolla_h_application_transport_residue.py';HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin';HEV=ROOT/'data/generated/corolla_8965H1202000_application_transport_decompiler_evidence.json'
p=f=0
def check(n,c):
 global p,f;ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {n}")
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';subprocess.run([sys.executable,str(TOOL),'--out',str(out)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);check('report regenerates exactly',out.read_bytes()==ART.read_bytes())
d=json.loads(ART.read_text());h=HRAW.read_bytes()[:0x100000];ev=json.loads(HEV.read_text())
check('H evidence image hash pinned',ev['image']['codeflash_sha256']==sha(h))
check('five H evidence bodies raw-bound',all(sha(h[int(r['entry'],16):int(r['entry'],16)+r['body_size']])==r['body_sha256'] and sha(r['decompiled_c'].encode())==r['decompiled_c_sha256'] for r in ev['functions']))
check('normal Rx table shrinks 47 to 40',d['rx_configuration']['sienna_count']==47 and d['rx_configuration']['h_count']==40)
check('2E4 Rx descriptor removed',d['rx_configuration']['can_2e4_removed'])
check('Tx IDs change exactly',d['tx_configuration']['sienna_ids']==['0x260','0x262','0x351','0x394','0x4A3','0x4C8'] and d['tx_configuration']['h_ids']==['0x030','0x351','0x394','0x4A3','0x4C8'])
check('260/262 removed',d['tx_configuration']['removed']==['0x260','0x262'])
check('H 394 remains PDU index 2',d['tx_configuration']['h_394_index']==2 and d['tx_configuration']['h_394_packer']['entry']=='0x00047ADA')
check('H 394 packer has four direct pack calls and submits index 2',d['tx_configuration']['h_394_packer']['direct_pack_call_count']==4 and d['tx_configuration']['h_394_packer']['submits_pdu_index_2'])
expected={'application_can_special_rx_demux':'0x0007A382','application_can_normal_rx_demux':'0x0007A402','application_pdu_transmit_router':'0x0007ADC2','application_pdu_rx_router':'0x0007B040','application_pack_can_394':'0x00047ADA'}
check('five transport roles exact', {x['reference_name']:x['target_entry'] for x in d['role_closure']}==expected)
check('three generated PDU roles recensused', {x['reference_name'] for x in d['surface_recensus']}=={'application_unpack_can_2e4','application_pack_can_260','application_pack_can_262'})
check('target-specific field boundary explicit','field identity is not transferred' in d['static_conclusion']['boundary'])
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
