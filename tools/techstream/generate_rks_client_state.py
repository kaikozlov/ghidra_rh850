#!/usr/bin/env python3
"""Generate the pinned Techstream V18 RKS client-side state/field map.

This stops at the server boundary.  It records native/UI/.NET edges that are
recoverable from the installed client and deliberately does not infer a server
signing algorithm or a target-specific requirement policy absent evidence.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path
import pefile

REPO=Path(__file__).resolve().parents[2]
CUW=REPO/'Techstream/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard'
OUT=REPO/'data/generated/techstream_v18/rks_client_state.json'

HANDLERS={
'Button_StartRequestReproKey_NextClick':0x49C62C,
'Button_StartRequestReproKey_OffLineClick':0x49C83C,
'Button_StartRequestReproKey_CancelClick':0x49C8BC,
'Button_RequestingReproKey_CancelClick':0x49CC10,
'Button_ImportReproKey_NextClick':0x49C2C0,
'Button_ImportReproKey_BackClick':0x49CCE0,
'Button_OfflineImportReproKey_NextClick':0x49CD24,
'Button_OfflineImportReproKey_BackClick':0x49CD68,
'Button_RequestReproKeyError_BackClick':0x49CDAC,
'Button_PasteReproKey_NextClick':0x49D3B4,
'Button_PasteReproKey_CancelClick':0x49D500,
'Button_InputReproKeyError_CancelClick':0x49DEB8,
'Button_InputReproKeyError_RetryClick':0x49DE70,
'Button_RKSNetworkError_RetryClick':0x49CC5C,
'Button_RKSNetworkError_CancelClick':0x49CF00,
}

# Extents are kept only for bodies that are stable in the pinned PE analysis.
FUNCTIONS=[
(0x49C0DC,482,'modal_request_driver'),(0x49C304,402,'shared_signature_file_import'),
(0x49C498,404,'shared_back_transition'),(0x49C62C,525,'online_start'),
(0x49C83C,125,'offline_start'),(0x49CC5C,71,'network_retry'),
(0x49CD24,68,'offline_import_next'),(0x49CF00,246,'network_cancel'),
(0x49D250,353,'offline_export_page'),(0x49D3BA,324,'pasted_signature_import'),
(0x49D544,64,'online_request_page'),(0x49D584,46,'vin_required_page'),
(0x49DE70,71,'signature_retry'),(0x49DEB8,246,'signature_cancel'),
(0x47FD5C,525,'offline_export_path'),(0x47FF6C,131,'signature_file_import_adapter'),
(0x4801C0,4,'state_setter'),(0x4801C4,4,'state_getter'),
(0x44D0FC,138,'flow_mode_copy'),(0x49B3D0,1970,'cuw_reprogram_flow_init'),
]

NATIVE_FIELDS=[
{'name':'XVersion','native_offset':0x215,'wrapper_offset':0x00,'source':'RKS config object +0x00'},
{'name':'GTSSoftwareID','native_offset':0x218,'wrapper_offset':0x03,'source':'RKS config object +0x04'},
{'name':'GTSSoftwareVersion','native_offset':0x239,'wrapper_offset':0x24,'source':'RKS config object +0x08'},
{'name':'GTSLicenseKey','native_offset':0x243,'wrapper_offset':0x2E,'source':'RKS config object +0x0C or +0x10 selected by host mode'},
{'name':'VIN','native_offset':0x272,'wrapper_offset':0x5D,'source':'current vehicle object +0x7C'},
{'name':'RequesterKind','native_offset':0x284,'wrapper_offset':0x6F,'source':'RKS config object +0x18'},
{'name':'KeypairID','native_offset':0x286,'wrapper_offset':0x71,'source':'RKS config object +0x1C'},
{'name':'SeedValue','native_offset':0x28D,'wrapper_offset':0x78,'source':'second argument of registered CUW callback; exactly 16 bytes serialized to 32 uppercase hex chars'},
]

def sha(pe,va,size):
 return hashlib.sha256(pe.get_data(va-pe.OPTIONAL_HEADER.ImageBase,size)).hexdigest()

def method_table_ptr(data:bytes,name:str):
 off=data.find(name.encode('ascii'))
 if off<5: return None
 if data[off-1] != len(name): return None
 return struct.unpack_from('<I',data,off-5)[0]

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=OUT); a=ap.parse_args()
 p=CUW/'Cuw.exe'; data=p.read_bytes(); pe=pefile.PE(data=data)
 handlers=[]
 for n,expected in HANDLERS.items():
  handlers.append({'name':n,'va':expected,'method_table_va':method_table_ptr(data,n)})
 funcs=[{'va':va,'size':sz,'role':role,'sha256':sha(pe,va,sz)} for va,sz,role in FUNCTIONS]
 obj={
 'schema_version':1,'distribution':'Toyota Techstream V18.00.003','cuw_sha256':hashlib.sha256(data).hexdigest(),
 'request_fields':NATIVE_FIELDS,
 'managed_mapping':{
   'SetDataForReproKey':'CUWAccessRKSWrapper.SetDataForReproKey',
   'is_stored':'hardcoded true before all string fields are copied; this is a DataForReproKey-validity flag, not evidence of a cached server token',
   'xml_fields':['X-Version','SoftwareID','SoftwareVersion','LicenseKey','VehicleIdentificationNumber','RequesterKind','KeypairID','SeedValue'],
 },
 'ui_handlers':handlers,
 'state_machine':{
   'online_start':'StartRequestReproKey Next -> browser launch/request page -> managed RequestReproKey/PasteSeedData -> polling -> import',
   'offline_start':'Offline button -> ExportDataForReproKey XML file/path -> offline instruction page -> same shared signature-file import as online file-reading path',
   'file_import':'online ImportReproKey Next and OfflineImportReproKey Next both converge at 0x49C304; file import extracts XML <Signature>, requires exactly 0x200 characters and alphanumeric-only, then sets native state 1 on success or 2 on failure/cancel',
   'paste_import':'Paste Signature Next uses the same native 0x200-character format checker before storing the token and setting state 1',
   'retry_state_values':{'network_retry':4,'network_cancel':2,'signature_retry':4,'signature_cancel':2},
   'state_byte':'RKS controller +0x04; 0 while modal request runs, 1 success, 2 abort/failure; retry UI side fields use value 4',
   'vin_gate':'empty current VIN branches to the S701-94 VIN-required page; nonempty VIN enters request/import navigation',
 },
 'requirement_boundary':{
   'calibration_predicate':'none recovered in the attach.att schema or flash-writer dataflow',
   'client_ui':'shipped locale explicitly instructs technicians to consult the repair manual whether the target needs Signature Request and, on unsupported IE/.NET prerequisite dialogs, choose No to continue reprogramming when Signature Request is not necessary',
   'conclusion':'V18 does not justify treating RKS as mandatory for every EPS reflash; exact target/regional requirement remains external policy/runtime evidence',
 },
 'seed_boundary':{
   'producer':'the 16-byte value arrives as callback argument 2 to the registered CUW reprogram-flow callback; no RNG/time/hash transform occurs in the recovered request-construction edge',
   'registration':'flow mode 3 registers the callback at 0x49BCF8 from 0x492D00; the actual callback invoker/runtime producer is one external controller/event edge upstream',
   'priority':'low for ECU security because Layer A never reaches a flash writer or ECU',
 },
 'function_identities':funcs,
 'server_boundary':'no client private key, public-key verification, signature-generation algorithm, or ECU-facing RKS token dataflow is present; do not infer server cryptography from the fixed token format',
 }
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
 return 0
if __name__=='__main__': raise SystemExit(main())
