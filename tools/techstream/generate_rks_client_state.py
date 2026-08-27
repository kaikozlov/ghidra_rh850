#!/usr/bin/env python3
"""Generate the pinned Techstream V18 RKS client-side state/field map.

Static closure (this revision): the RKS SeedValue producer chain is fully
recovered inside Cuw.exe — no producer code is missing.  The chain is:

  CentralGW P5-CAN SecurityAccess `27 21` (CCentralGWModeChanger::
  CollateSeedKeyForP5CentralGW @ 0x590320) -> 16-byte response seed ->
  seed bridge (0x5907EC) into global 0x629CDC -> registered CUW callback
  invoker thunk (0x590858, `call [0x629CD0]`) -> request-builder callback
  0x49BCF8 -> 16 bytes hex-serialized into the ReproKeyRequest SeedValue.
  The portal's 512-character token is stored by 0x48013C and 256 decoded
  bytes are transmitted as `27 22 || token[256]` expecting `67 22`.

What remains external is only (a) the live gateway seed VALUE and (b) the
server-side signing algorithm/private key.  Nothing else is inferred.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path
import pefile

REPO=Path(__file__).resolve().parents[2]
CUW=REPO/'software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard'
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
# --- SeedValue producer chain (Cuw.exe static closure) -----------------------
(0x49BCF8,0x3E3,'rks_request_callback_builder'),      # registered callback / request builder
(0x47FB24,0x237,'rks_request_block_filler'),          # copies 16 seed bytes, hex-encodes to +0x28D
(0x48013C,0x82,'rks_signature_token_store'),          # portal token -> ctrlr/+0x14, 0x100-byte staging
(0x43E0C0,0xF74,'rks_ini_loader'),                    # reads Ini\RKS.ini [ReproKeyRequest]
(0x590320,0x2DF,'centralgw_collate_seed_key_for_p5'), # 27 21 / 67 21, then 27 22 || token[256] / 67 22
(0x5907EC,0x6C,'rks_seed_token_bridge'),              # seed -> 0x629CDC, token -> 0x629CEC
(0x590858,0x1C,'rks_callback_invoker_thunk'),         # EDX=0x629CDC, ECX=0x629CEC, call [0x629CD0]
]

NATIVE_FIELDS=[
{'name':'XVersion','native_offset':0x215,'wrapper_offset':0x00,'source':'RKS config object +0x00'},
{'name':'GTSSoftwareID','native_offset':0x218,'wrapper_offset':0x03,'source':'RKS config object +0x04'},
{'name':'GTSSoftwareVersion','native_offset':0x239,'wrapper_offset':0x24,'source':'RKS config object +0x08'},
{'name':'GTSLicenseKey','native_offset':0x243,'wrapper_offset':0x2E,'source':'RKS config object +0x0C or +0x10 selected by host mode'},
{'name':'VIN','native_offset':0x272,'wrapper_offset':0x5D,'source':'current vehicle object +0x7C'},
{'name':'RequesterKind','native_offset':0x284,'wrapper_offset':0x6F,'source':'RKS.ini [ReproKeyRequest] RequesterKind (shipped "0") loaded by 0x43E0C0 into config +0x18; read via accessor 0x43F06C at 0x49BFEA'},
{'name':'KeypairID','native_offset':0x286,'wrapper_offset':0x71,'source':'RKS.ini [ReproKeyRequest] KeypairID (shipped "RK0001") loaded by 0x43E0C0 into config +0x1C; read via accessor 0x43F078 at 0x49C009'},
{'name':'SeedValue','native_offset':0x28D,'wrapper_offset':0x78,'source':'CentralGW P5-CAN SecurityAccess 27 21 response seed: 16-byte record copied from the diag response at +0x1F, bridged through global 0x629CDC to the registered callback at 0x49BCF8; exactly 16 bytes serialized to 32 uppercase hex chars'},
]

# (name, VA, length, required-hex-substring) — asserted against the PE bytes.
ANCHORS=[
('flow_mode3_gate_cmp3',            0x492FBE,7,'83fa03'),
('registration_imm_0x49bcf8',       0x492FC7,7,'c745c8f8bc4900'),
('tmethod_store_code_plus_0xf18',   0x47A341,6,'8990180f0000'),
('tmethod_store_data_plus_0xf1c',   0x47A34A,6,'89901c0f0000'),
('invoker_push_pair_f1c_f18',       0x478BD2,12,'ffb31c0f0000ffb3180f0000'),
('globals_installer_body',          0x58FF44,0x19,'8905d09c6200'),
('globals_installer_body2',         0x58FF44,0x19,'8905d49c6200'),
('seed_bridge_memcpy16_to_0x629cdc',0x5907F5,14,'6a105268dc9c6200'),
('invoker_thunk_call_global',       0x590867,6,'ff15d09c6200'),
('callback_seed_arg_push',          0x49C027,5,'8b55bc5253'),
('secacc_request_sid_27_21',        0x590364,14,'c685a1efffff27c685a2efffff21'),
('secacc_expected_67_21',           0x590392,14,'c68569dfffff67c6856adfffff21'),
('seed_record_copy_16_from_resp',   0x5903F6,13,'6a108d8d33cfffff51'),
('secacc_sendkey_sid_27_22',        0x5904A4,14,'c685f9bdffff27c685fabdffff22'),
('secacc_sendkey_token_len_0x100',  0x5904B2,5,'6800010000'),
('secacc_sendkey_request_len_0x107',0x5904D3,10,'c785ecbdffff07010000'),
('secacc_expected_67_22',           0x5904EA,14,'c685c1adffff67c685c2adffff22'),
('nrc_gate_resp_len_8',             0x59055C,7,'83bd7c9dffff08'),
('nrc_gate_neg_sid_0x7f',           0x59056D,3,'83f87f'),
('nrc_gate_sid_0x27',               0x59057A,3,'83fa27'),
('nrc_gate_nrc_0x13',               0x590587,3,'83f813'),
('nrc_gate_nrc_0x35',               0x59058C,3,'83f835'),
('nrc_gate_nrc_0x36',               0x590591,3,'83f836'),
('token_store_push_0x100',          0x480180,5,'6800010000'),
]

# (name, call-site VA, expected callee) — rel32 resolved from raw bytes.
CALLS=[
('request_builder_reads_config_requesterkind',0x49BFEA,0x43F06C),
('request_builder_reads_config_keypairid',    0x49C009,0x43F078),
('request_builder_seed_ptr_via_accessor',     0x49C02C,0x43F03C),
('collate_seed_key_calls_p5can_diag',         0x5903F1,0x45D898),
('callback_sends_request_block_to_filler',    0x49C06B,0x47FB24),
('seed_bridge_memcpy_callee',                 0x5907FD,0x5AA540),
('token_store_memcpy_callee',                 0x48018D,0x5AA540),
]

# (name, VA, expected NUL-terminated ASCII) — loader string evidence.
STRINGS=[
('loader_ini_path',   0x5E06C9,b'Ini\\RKS.ini'),
('loader_section',    0x5E06D5,b'ReproKeyRequest'),
('loader_key_ifver',  0x5E06E5,b'IFVersion'),
('loader_key_swid',   0x5E06F0,b'SoftwareID'),
]

# Shipped Ini/RKS.ini is obfuscated: each nibble n is one ASCII char 0x20+4n,
# two chars per byte ("4L4(84<..." -> "[Re...").
def decode_rks_ini(raw:bytes)->bytes:
 out=bytearray()
 for i in range(0,len(raw)-1,2):
  out.append(((((raw[i]-0x20)&0xff)>>2)<<4)|(((raw[i+1]-0x20)&0xff)>>2))
 return bytes(out)

def parse_ini(text:str)->dict:
 vals={};section=None
 for line in text.replace('\r\n','\n').split('\n'):
  line=line.strip()
  if line.startswith('[') and line.endswith(']'): section=line[1:-1]; continue
  if '=' in line and section:
   k,v=line.split('=',1); vals[f'{section}/{k}']=v
 return vals

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

 # --- verify every raw anchor against the PE before emitting anything -------
 anchors=[]
 for name,va,n,must in ANCHORS:
  raw=bytes(pe.get_data(va-pe.OPTIONAL_HEADER.ImageBase,n))
  if bytes.fromhex(must) not in raw:
   raise SystemExit(f'anchor mismatch: {name} @ {va:#x}: {raw.hex()} lacks {must}')
  anchors.append({'name':name,'va':va,'len':n,'hex':raw.hex()})
 calls=[]
 for name,va,target in CALLS:
  o=pe.get_offset_from_rva(va-pe.OPTIONAL_HEADER.ImageBase)
  op=data[o]
  if op!=0xE8: raise SystemExit(f'call-site not E8: {name} @ {va:#x}')
  dest=va+5+struct.unpack_from('<i',data,o+1)[0]
  if dest!=target: raise SystemExit(f'call target mismatch: {name} @ {va:#x}: {dest:#x} != {target:#x}')
  calls.append({'name':name,'va':va,'target':target})
 strs=[]
 for name,va,exp in STRINGS:
  o=pe.get_offset_from_rva(va-pe.OPTIONAL_HEADER.ImageBase)
  got=data[o:data.find(b'\0',o)]
  if got!=exp: raise SystemExit(f'string mismatch: {name} @ {va:#x}: {got!r} != {exp!r}')
  strs.append({'name':name,'va':va,'value':exp.decode()})

 # --- shipped RKS.ini provenance --------------------------------------------
 ini_path=CUW/'Ini/RKS.ini'
 ini_raw=ini_path.read_bytes()
 ini_dec=decode_rks_ini(ini_raw)
 ini_vals=parse_ini(ini_dec.decode('ascii','replace'))
 for key,exp in (('ReproKeyRequest/RequesterKind','0'),('ReproKeyRequest/KeypairID','RK0001'),
                 ('ReproKeyRequest/SoftwareID','GTS'),('ReproKeyRequest/IFVersion','01')):
  if ini_vals.get(key)!=exp:
   raise SystemExit(f'RKS.ini decode mismatch: {key}={ini_vals.get(key)!r} != {exp!r}')

 obj={
 'schema_version':2,'distribution':'Toyota Techstream V18.00.003','cuw_sha256':hashlib.sha256(data).hexdigest(),
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
 'seed_producer_chain':{
   'summary':'RKS SeedValue = 16-byte CentralGW P5-CAN SecurityAccess 27 21 response seed; the whole producer is static Cuw.exe code — no producer edge is missing',
   'registration':'flow-mode-3 gate at 0x492FBE (cmp byte [flow+0xC64],3) stores TMethod{0x49BCF8, flow} at 0x492FC7; fcn 0x47A338 parks it at controller +0xF18/+0xF1C',
   'global_install':'invoker-side function at 0x478B68 pushes the parked pair (0x478BD2) into 0x58FF44, which installs globals 0x629CD0(callback code)/0x629CD4(callback self)',
   'invocation':'thunk 0x590858: EDX=0x629CDC (16-byte seed buffer), ECX=0x629CEC (0x100-byte token buffer), EAX=[0x629CD4], call [0x629CD0] at 0x590867; result byte -> 0x629DEC',
   'seed_bridge':'0x5907EC memcpy(0x629CDC, seed16, 0x10) at 0x5907F5 and, after a successful callback, memcpy(0x629CEC, token256, 0x100)',
   'callback_consume':'0x49BCF8 pushes its EDX seed pointer at 0x49C027, resolves the seed record via accessor 0x43F03C at 0x49C02C ([seed+4] -> AnsiString of the 16 seed bytes), and passes it to 0x47FB24 which copies exactly 16 bytes and hex-encodes 32 uppercase chars into controller +0x28D',
   'no_client_transform':'no RNG, time, or hash derivation exists anywhere in the producer chain; the value is the gateway SecurityAccess seed',
 },
 'centralgw_security_access':{
   'actor':'CCentralGWModeChanger::CollateSeedKeyForP5CentralGW = fcn 0x590320 (assertion string at 0x629BC5), entered from ChangeToReprogGWMode 0x58F028 -> 0x5901D0',
   'diag_send':'requests and expected responses are transmitted by CCanDiagCommUtils::SendRequMsgAndReceiveRespMsgForP5Can = fcn 0x45D898 (log string at 0x5EE616), called at 0x5903F1 and 0x59054C',
   'send_seed':'request 27 21 stored at 0x590364; expected positive response 67 21 at 0x590392',
   'seed_extract':'16-byte seed record memcpy from diag response +0x1F at 0x5903F6; the record dword at +4 is the AnsiString pointer to the 16 seed bytes',
   'send_key':'request 27 22 stored at 0x5904A4 followed by the 256 decoded token bytes (memcpy 0x100 at 0x5904B2); total request length 0x107 at 0x5904D3; expected positive response 67 22 at 0x5904EA',
   'nrc_gate':'negative responses are gated as 7F 27 with NRC 0x13 (0x590587), 0x35 (0x59058C), or 0x36 (0x590591); response length must be 8 (0x59055C)',
 },
 'rks_ini_provenance':{
   'path':'Calibration Update Wizard/Ini/RKS.ini (shipped, obfuscated)',
   'sha256':hashlib.sha256(ini_raw).hexdigest(),
   'decoded_sha256':hashlib.sha256(ini_dec).hexdigest(),
   'encoding':'per-nibble ASCII obfuscation: nibble n -> char 0x20+4n, two chars per byte',
   'decoded_section_fields':{k.split('/',1)[1]:v for k,v in ini_vals.items() if k.startswith('ReproKeyRequest/')},
   'loader':'fcn 0x43E0C0 references "Ini\\\\RKS.ini" (0x5E06C9), section "ReproKeyRequest" (0x5E06D5), and the key names; config singleton object at 0x6360B4 (getter 0x43DFBC, slot initializer 0x43DEBC)',
   'field_mapping':'RequesterKind -> config +0x18 (accessor 0x43F06C, read at 0x49BFEA); KeypairID -> config +0x1C (accessor 0x43F078, read at 0x49C009)',
 },
 'static_boundary':{
   'producer':'fully recovered inside Cuw.exe; there is no missing or unnamed producer code path',
   'external_residues':['the live Central Gateway seed VALUE returned by the vehicle for 27 21','the TIS-portal server-side signing algorithm and private key behind the 512-character token'],
   'priority':'reflash-security infrastructure: Layer A reaches the Central Gateway through 27 21/27 22 but remains separate from EPS flash-writer Layer B; this does not expose an unauthenticated primitive',
 },
 'raw_anchors':anchors,
 'call_anchors':calls,
 'string_anchors':strs,
 'function_identities':funcs,
 'server_boundary':'no client private key, public-key verification, or signature-generation algorithm is present; the server-produced 512-character token is decoded and sent to the Central Gateway as the 27 22 payload, not to the EPS flash writers; do not infer server cryptography from the fixed token format',
 }
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
 return 0
if __name__=='__main__': raise SystemExit(main())
