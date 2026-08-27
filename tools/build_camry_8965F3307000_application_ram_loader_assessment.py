#!/usr/bin/env python3
"""Build the exact-F33 application-mode volatile signer loader assessment.

This artifact intentionally separates byte placement from control transfer.  It
uses exact CodeFlash bytes plus retained live evidence.  It does not authorize
or implement a vehicle-side execution pivot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin"
IMAGE_SHA = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
RAW = ROOT / "community/kai/camry-2026/raw-20260826"
HIGH = RAW / "high-tail-20260826.json"
LOW = RAW / "stock-retention-20260826.json"
STOCK_HANDOFF = RAW / "stock-handoff-20260826.json"
POSTSTARTUP = RAW / "poststartup-canary-20260826.json"
RETENTION_MANIFEST = RAW / "RAM_RETENTION_MANIFEST.txt"
XCP_LIVE = RAW / "xcp_probe.json"
OUT = ROOT / "data/generated/camry_8965F3307000_application_ram_loader_assessment.json"

HIGH_BASE, HIGH_END = 0xFEBFF9F0, 0xFEBFFBFB
XCP_LO, XCP_HI = 0xFEBF7C00, 0xFEBFFBFF
CAL_SOURCE_LO, CAL_SOURCE_END = 0x00010000, 0x00017DEF
CAL_SHADOW_LO, CAL_SHADOW_END = 0xFEBF7C00, 0xFEBFF9EF
CAL_PAGE_STATE = (0xFEBE5EC4, 0xFEBE5EC5)

# Body sizes were recovered target-natively from the F33 Ghidra project.  Hashes
# bind every semantic address used by this assessment to exact firmware bytes.
FUNCTIONS = {
    "xcp_download": (0x081FFE, 198, "f3613623e5efa233ad8efae23b047fcde6389822c5828f8ce7ead4f5089a88fd"),
    "xcp_modify_bits": (0x0820C4, 162, "1483cd6c21500222dbfad1111e2c2c95f6fee74d33b4170dacb3585beb32c025"),
    "xcp_short_upload": (0x082B1A, 184, "aae466f7119d249039aba6275df9aecbf23ba189238f2ed8cc8256b90707430c"),
    "xcp_set_mta": (0x082C62, 60, "5317d2d72b3d7b53d6bdc1f70f8102102fb9397c8d17afbf1e2b645a40a06734"),
    "xcp_can_rx_adapter": (0x08312E, 40, "fa43c5695d69f92cc770d4d81a9be566a1a66a23bc77b8291befeb1013bf497c"),
    "xcp_custom_dispatcher": (0x098E80, 110, "9abe28c874bd5187a00ec5f663114ecb41cca444afb11f047f36152dbc86094e"),
    "xcp_read_range_validator": (0x098EF2, 58, "b6ee1f7409da646a7b7de61950f5765bc7cb5183ab34a89e46800d3fb89e765c"),
    "xcp_write_range_validator": (0x098F2C, 32, "72c0c9458c91187f17087247ba220211e69d3294aa429d58b3ee84689827db9e"),
    "xcp_custom_fb": (0x098FBA, 74, "65e792f96dc7cd1e08df9ced0309109b115144e3797b9ed9014afed4a23f6cf9"),
    "xcp_custom_fa": (0x09901A, 96, "c3875456a35d50fdd1fb2791a8f989d151a8065fe26b7ce9f8faf05ee8595f51"),
    "xcp_custom_range_validator": (0x09907A, 172, "75ad549642ded380807a40e8aa9959029b5289bca28e9759461275abecd60284"),
    "xcp_custom_f5": (0x099152, 100, "9408ed82510985279521923fa92a79c492661acbe8e487f28ffa51bd0fb6f89e"),
    "xcp_custom_f3": (0x099266, 168, "8931f1c77b2df68fdc6633ac1981978e82675d29ad91c6e8472349e2327569bd"),
    "xcp_custom_eb": (0x09930E, 122, "d41160a43e5e76c36ff75675f53da5ba78912caae371973997760c06c6a2370b"),
    "xcp_custom_ea": (0x099388, 104, "87f871160bd508df72f736210dacec083730a45403788d0cea4d76082b0b7923"),
    "xcp_custom_e4": (0x099414, 106, "14367502c37c230022c4c3d55fded0377095e663d89fbe83efc0834efa84050b"),
    "rid100f_precondition": (0x08B858, 12, "dfac33733e8cadab3a1f90e1bb9cce317cfae3e809bb401602a7b05f72d6876c"),
    "rid100e_action": (0x08B864, 14, "9146e9352147cbe6700e963e525c5cc9368477ab0e1bee4d9e987034746ba50c"),
    "rid100f_action": (0x08B872, 14, "03a6801ea225a9427f89e76b7584c1adbf82b6b6b9d2db49274e1cd53f7db20f"),
    "crypto_bank0_activate": (0x06A028, 48, "ecb160156d319b1524ef16c9da2cba78e60d6ab221c3d4fcf40fe13c1312524f"),
    "crypto_bank1_activate": (0x06A0AE, 42, "e6b1c4dbd1fff1a807f4f1cc2d693f41a2cd5e714f3a038e136a2f38f69fe3a8"),
    "crypto_bank1_step": (0x069C58, 74, "18cd09a08713679113856921b1c43a111373d30b6882c08e24377d70244c0c2d"),
    "crypto_bank_submit": (0x069BD8, 128, "abc4d5fc3214238014c03ca1533486f35cae88dfe388e1fa127680c953b915f3"),
    "crypto_bank1_complete": (0x06A300, 26, "668d483de8a3005469d08678f1b2d155df73a6f2f0c0260432713fa52979707b"),
    # Exact F33 fixed-DMAC descriptor consumers recovered target-natively. These
    # ranges bind the DMA hardening below to this image without importing a
    # Sienna/H semantic claim by address.
    "dmac_primary_table_caller": (0x060462, 432, "8f3319ccf077efb5061e6f270a3768ad4a59726bbd304ba4db36bf381a40c568"),
    "dmac_descriptor_apply": (0x060A6A, 62, "434536acdce138f2b08407b8c38c19227b9b7cde3a7db014a5127f282c64b23b"),
    "dmac_pair_table_caller": (0x060C20, 64, "76ad3e79f24b67da0d1728bc3287ea1a25d4f96e2ea5a8441fa10983dfd9bdd8"),
    "dmac_small_table_caller": (0x061B90, 176, "27d66c6339bdb867194fae88449c0b08c57b5e564343ca535b463b092b94e180"),
    "dmac_three_table_caller": (0x0628B2, 156, "52cbdb5d2b6ab4c70437aa1bb33d8c941bd23a7b3ff4db36ca72d7f023c8c4d7"),
}

# Exact instruction/data ranges recovered while closing the residual execution-
# pivot question. These small startup/custom-XCP islands are not all owned by
# stable Ghidra function objects, so keep them separate from function bodies.
RAW_RANGES = {
    "application_entry_wrapper": (0x020880, 0x0C, "e8f5ceae08d8f49cbed117749e2c048bf1fb446f48665d4921fd098ab8072ae5"),
    "startup_calibration_shadow_copy": (0x0636D4, 0x24, "969ee65ec1d2a2523c1bd97a317de7923bc05a7e5ca3785760e5cb78296dc8b2"),
    "startup_coordinator_prefix": (0x0637EE, 0x70, "699b5fba4d401cbe090e5344beeb22161af0cbbd23041b93aed92dc90166972a"),
    "xcp_calibration_page_translator": (0x0991D2, 0x54, "22bb704d8afb3814195201d26b1e21662364e6815eff7e3ca58730dc6c255b26"),
    "xcp_build_checksum_worker": (0x099226, 0x40, "c1507aa150c0ac06ca3d02c29f70da68af44967f94232412b0449b39a639516e"),
    "xcp_calibration_shadow_copy": (0x0993F0, 0x24, "969ee65ec1d2a2523c1bd97a317de7923bc05a7e5ca3785760e5cb78296dc8b2"),
    "calibration_source_page": (CAL_SOURCE_LO, 0x7DF0, "675e9f5f360277c6eb27ef73bb021e40861a88d99dd283adb2d7062506d246b6"),
}

# Fixed F33 application DMAC descriptor families recovered from the target-native
# callers above. Each record is 0x28 bytes; both endpoint pairs live at +8/+0xC
# and +0x18/+0x1C. The first 10-row family is two contiguous 5-row banks.
DMAC_TABLES = [
    (0x0310A8, 10, "389fe2a8f41285dd2ed267bc1e8729bffad11805d2b92f221e6d953c48a0b324"),
    (0x03125C, 2, "47a68294ea24488048010160dd508d7e3b00bbaad21c35879a3138813013b7d8"),
    (0x0312AC, 2, "2abcfe2f189216a8a07166a5a17c8210306a1dbdd11e9a4fa751be899af74a7d"),
    (0x0314AC, 2, "1d5008b873b3c1b85d2e81ed7eee2e4f89b1b89884811ea6adc45101c53f30f3"),
    (0x0314FC, 2, "f7148ee26c36962b06afe5bddb306099755281c1c39d770075b877ef13af38e0"),
    (0x03154C, 2, "33429f1ed54ed419082075b301b57b885b7218e82f7f81943359070cfd91d67c"),
    (0x03161C, 2, "b34e78417870d0774c8fd053475ff25e7eea52e03199e80ec18e2bc4860b9013"),
]

DMAC_TABLE_POINTER_HITS = {
    0x0310A8: [0x0605D8],
    0x03125C: [0x060C38, 0x062B40],
    0x0312AC: [0x060C4C],
    0x0314AC: [0x062922],
    0x0314FC: [0x06292E],
    0x03154C: [0x06293A],
    0x03161C: [0x061C22],
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: Path) -> str:
    return sha(p.read_bytes())


def u32(b: bytes, off: int) -> int:
    return struct.unpack_from("<I", b, off)[0]


def need(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def load(p: Path) -> dict:
    return json.loads(p.read_text())


def find_all(b: bytes, needle: bytes) -> list[int]:
    out=[]; pos=0
    while True:
        pos=b.find(needle,pos)
        if pos < 0: return out
        out.append(pos); pos += 1


def find_ldsr_writers(image: bytes, system_register: int, selector: int) -> list[dict]:
    """Whole-image RH850/E3 LDSR census using the repository SLEIGH encoding.

    `v850e3.sinc` defines LDSR with op0510=0x3F, SR1115=<system register>,
    op1626=0x20, op2731=<selector>, and R0004 as the source GPR. RH850
    instructions are 2-byte aligned, so this covers undiscovered instruction
    islands instead of relying on Ghidra function ownership.
    """
    out=[]
    for off in range(0,len(image)-3,2):
        word=u32(image,off)
        if (((word >> 5) & 0x3F) == 0x3F and
            ((word >> 11) & 0x1F) == system_register and
            ((word >> 16) & 0x7FF) == 0x20 and
            ((word >> 27) & 0x1F) == selector):
            out.append({
                "address":f"0x{off:08X}",
                "source_register":f"r{word & 0x1F}",
                "bytes":image[off:off+4].hex(),
            })
    return out


def build() -> dict:
    image=IMAGE.read_bytes()
    need(len(image)==0x100000 and sha(image)==IMAGE_SHA, "exact F33 image drift")
    high,low,handoff,poststartup,xlive=load(HIGH),load(LOW),load(STOCK_HANDOFF),load(POSTSTARTUP),load(XCP_LIVE)
    need(high["schema"]=="camry-f33-high-tail-exec-retention-v1", "high-tail evidence schema drift")
    need(high["result"]["tail_524_byte_exact"] and high["result"]["tail_marker_executed"], "high-tail retention/exec result drift")
    need(high["result"]["retained_sha256"]=="89ffed31c24e746a57171e6f3e22f99d1e78d57b63bccb8778c7fe715d18800c", "high-tail retained bytes drift")
    need(high["result"]["stock_application_reappeared"] and high["result"]["safety_tx_blocked_delta"]==0, "high-tail stock-return result drift")
    need(low["schema"]=="camry-f33-stock-handoff-probe-v1" or low["schema"]=="camry-f33-stock-retention-probe-v1", "low-carrier evidence schema drift")
    need(low["result"]["prefix_648_byte_exact"] is False and low["result"]["shell_retained"] is False, "low-carrier rejection drift")
    need(handoff["schema"]=="camry-f33-stock-handoff-probe-v1" and handoff["result"]["stock_application_reappeared"] is True, "stock handoff evidence drift")
    need(poststartup["schema"]=="camry-f33-poststartup-canary-live-v1", "poststartup canary schema drift")
    need(poststartup["payload"]["command5_calls"] is False and poststartup["payload"]["flash_write"] is False and poststartup["payload"]["steering_can_transmit"] is False, "poststartup canary safety boundary drift")

    # Packed Denso/Toyota standard-CAN descriptor encoding used by the F33 image.
    req_desc=(0x80000000 | (0x7F7 << 18) | 2).to_bytes(4,"little")
    rsp_desc=(0x80000000 | (0x7F8 << 18) | 2).to_bytes(4,"little")
    req_hits=find_all(image,req_desc); rsp_hits=find_all(image,rsp_desc)
    need(req_hits==[0x21F50,0x23398], f"packed 7F7 descriptor drift: {req_hits}")
    need(rsp_hits==[0x21F48], f"packed 7F8 descriptor drift: {rsp_hits}")

    # Standard XCP opcode map and callback table.
    opmap=image[0x22B24:0x22B24+41]
    expected_map=bytes.fromhex("0001020300000000000400050000000600000007000000000000000008090a0b000c0d00000e0f1011")
    need(opmap==expected_map, "F33 standard XCP opcode map drift")
    callbacks=[u32(image,0x22B50+i*4) for i in range(18)]
    expected_callbacks=[0x82A5C,0x82A6E,0x82ACE,0x82AA2,0x82C62,0x82B1A,0x81FFE,0x820C4,0x82880,0x824B8,0x82510,0x82616,0x826D6,0x827B4,0x8295C,0x8299A,0x82910,0x829CE]
    need(callbacks==expected_callbacks, "F33 standard XCP callback table drift")
    need(opmap[0xFF-0xF8]==0 and opmap[0xFF-0xF7]==0, "GET_SEED/UNLOCK unexpectedly configured")
    need(u32(image,0x2B21C)==XCP_LO and u32(image,0x2B220)==XCP_HI, "XCP software window constants drift")

    selectors=[]; custom=[]
    for i in range(7):
        off=0x2B250+i*8
        selectors.append(image[off]); custom.append(u32(image,off+4))
    need(selectors==[0xFB,0xFA,0xF5,0xF3,0xEB,0xEA,0xE4], "custom XCP selector table drift")
    need(custom==[0x98FBA,0x9901A,0x99152,0x99266,0x9930E,0x99388,0x99414], "custom XCP handlers drift")

    # Application Dcm service table: 17 x 24-byte service objects.
    service_base=0x25C54; stride=24
    service_rows=[]
    for i in range(17):
        off=service_base+i*stride
        cb,sec_ptr,sess_ptr,sub_ptr=struct.unpack_from("<IIII",image,off)
        sid,has_sub,sec_count,sess_count,sub_count=struct.unpack_from("<BBBBB",image,off+16)
        service_rows.append({"sid":sid,"callback":cb,"security_count":sec_count,"sessions":list(image[sess_ptr:sess_ptr+sess_count]),"has_subfunctions":bool(has_sub),"sub_count":sub_count})
    need([r["sid"] for r in service_rows]==[0x10,0x11,0x14,0x19,0x22,0x23,0x27,0x28,0x2E,0x31,0x34,0x36,0x37,0x3E,0x85,0xAB,0xBA], "application service table drift")
    bysid={r["sid"]:r for r in service_rows}
    need(0x3D not in bysid, "WriteMemoryByAddress unexpectedly configured")
    for sid in (0x34,0x36,0x37):
        need(bysid[sid]["callback"]==0 and bysid[sid]["sessions"]==[2], f"SID {sid:02X} app download policy drift")

    # RoutineControl exact F33 table.  0x100F is row 8 and uses the row-8 callback tuple.
    rids=[struct.unpack_from("<H",image,0x26918+i*8)[0] for i in range(19)]
    expected_rids=[0x1000,0x1001,0x1002,0x1004,0x1007,0x1008,0x1009,0x100E,0x100F,0x1010,0x1100,0x1103,0x1106,0x1108,0x1109,0x110A,0x110B,0x110C,0x110D]
    need(rids==expected_rids, "F33 routine ID table drift")
    rid100f_row=struct.unpack_from("<III",image,0x256DC+8*12)
    need(rid100f_row==(0x100F,0x8B858,0x8B872), f"RID100F callback row drift: {rid100f_row}")

    ranges={}
    for name,(off,size,digest) in FUNCTIONS.items():
        body=image[off:off+size]
        need(len(body)==size and sha(body)==digest, f"{name} body identity drift")
        ranges[name]={"address":f"0x{off:08X}","size":size,"sha256":digest}

    raw_ranges={}
    for name,(off,size,digest) in RAW_RANGES.items():
        body=image[off:off+size]
        need(len(body)==size and sha(body)==digest, f"{name} raw-range identity drift")
        raw_ranges[name]={"address":f"0x{off:08X}","size":size,"sha256":digest}

    # F33 has two byte-identical calibration-page copy loops: one in normal
    # application startup and one behind XCP COPY_CAL_PAGE (0xE4). Both copy the
    # exact low calibration page into the lower XCP window. This is a calibration
    # shadow/data path, not evidence of instruction-fetch remapping.
    need(CAL_SOURCE_END-CAL_SOURCE_LO+1==0x7DF0, "calibration page size drift")
    need(CAL_SHADOW_END-CAL_SHADOW_LO+1==0x7DF0, "calibration shadow size drift")
    need(image[0x636D4:0x636F8]==image[0x993F0:0x99414], "startup/XCP calibration copy loops diverged")
    need(image[0x63822:0x63826]==bytes.fromhex("bfffb2fe"), "startup calibration-copy callsite drift")

    # MPU region 1 contains the entire live high tail. Region 1 is supervisor RWX in
    # context 0 and supervisor RX in context 1.
    mpu=0x31688
    bounds=[(u32(image,mpu+i*8),u32(image,mpu+i*8+4)) for i in range(16)]
    ctx0=[u32(image,mpu+0x80+i*4) for i in range(16)]
    ctx1=[u32(image,mpu+0xC0+i*4) for i in range(16)]
    need(bounds[1]==(0xFEBF7C00,0xFEBFFBFC) and ctx0[1]==0xB8 and ctx1[1]==0xA8, "MPU region1 drift")
    need(HIGH_BASE>=bounds[1][0] and HIGH_END<bounds[1][1], "high tail outside MPU region1")

    # A direct CodeFlash pointer census finds no embedded u32 pointer into the
    # retained high tail. This is stronger than a single named-table search but
    # still does not cover synthesized/computed aliases at runtime.
    high_tail_pointer_hits=[]
    for off in range(0,len(image)-3):
        value=u32(image,off)
        if HIGH_BASE <= value <= HIGH_END:
            high_tail_pointer_hits.append({"offset":f"0x{off:06X}","value":f"0x{value:08X}"})
    need(high_tail_pointer_hits==[], f"unexpected CodeFlash pointer into high tail: {high_tail_pointer_hits[:8]}")

    # Close the obvious target-native DMA composition. The recovered F33 DMAC
    # setup callers consume only these fixed CodeFlash-resident 0x28-byte
    # descriptors. No endpoint field in any recovered family enters the XCP
    # software window, so the known fixed-DMA paths cannot be repurposed into an
    # XCP-window callback/PC pivot. This remains bounded against a separate,
    # undiscovered DMA programmer or hardware-owned mutation path.
    dmac_tables=[]
    dmac_endpoints=[]
    for base,count,digest in DMAC_TABLES:
        body=image[base:base+count*0x28]
        need(len(body)==count*0x28 and sha(body)==digest, f"DMAC table {base:#x} identity drift")
        expected_hits=DMAC_TABLE_POINTER_HITS[base]
        actual_hits=find_all(image,struct.pack("<I",base))
        need(actual_hits==expected_hits, f"DMAC table {base:#x} pointer provenance drift: {actual_hits}")
        rows=[]
        for i in range(count):
            off=base+i*0x28
            endpoints=[u32(image,off+x) for x in (8,0xC,0x18,0x1C)]
            rows.append({"index":i,"address":f"0x{off:08X}","endpoints":[f"0x{x:08X}" for x in endpoints]})
            dmac_endpoints.extend(endpoints)
        dmac_tables.append({"base":f"0x{base:08X}","count":count,"record_size":0x28,"sha256":digest,"raw_pointer_hits":[f"0x{x:06X}" for x in actual_hits],"rows":rows})
    dmac_window_hits=[x for x in dmac_endpoints if XCP_LO <= x <= XCP_HI]
    need(len(dmac_endpoints)==88, f"DMAC endpoint census size drift: {len(dmac_endpoints)}")
    need(dmac_window_hits==[], f"fixed DMAC endpoint enters XCP window: {dmac_window_hits}")

    # Close CALLT base retargeting against the exact image, including undiscovered
    # instruction islands. CTBP is system-register id 20, selector 0 under the
    # repository RH850/E3 SLEIGH. The only matching LDSR in the complete 1-MiB
    # CodeFlash is reset's `ldsr r0,CTBP` at 0x25E, fixing CTBP to zero.
    ctbp_writers=find_ldsr_writers(image,20,0)
    need(ctbp_writers==[{"address":"0x0000025E","source_register":"r0","bytes":"e0a72000"}], f"CTBP writer census drift: {ctbp_writers}")

    # Exact current dynamic reachability result is only the normal EPS route.
    need(xlive["status"]=="unreachable" and xlive["route"]["eps_bus"]==1 and xlive["route"]["elm327_param"]==1, "XCP live discriminator drift")
    need(xlive["write_commands_implemented"] is False and xlive["source_memory_writes_implemented"] is False, "XCP live probe write guard drift")

    return {
      "schema":"camry-8965f3307000-application-ram-loader-assessment-v1",
      "target":{"software_id":"8965F3307000","secondary":"8A3113303100","codeflash_sha256":IMAGE_SHA,"mcu":"R7F701381"},
      "live_runtime_carrier":{
        "base":f"0x{HIGH_BASE:08X}","end_inclusive":f"0x{HIGH_END:08X}","size":HIGH_END-HIGH_BASE+1,
        "retained_sha256":high["result"]["retained_sha256"],"exact_after_stock_startup":True,"executed_live":True,"stock_application_reappeared":True,
        "safety_tx_blocked_delta":0,"low_febf0000_carrier_rejected":True,
        "source_files":{p.name:sha_file(p) for p in (HIGH,LOW,STOCK_HANDOFF,POSTSTARTUP,RETENTION_MANIFEST)},
        "poststartup_direct_canary_result":"negative/no application reappearance; retained as a failed architecture probe, not evidence against the proven high-tail carrier",
      },
      "application_xcp":{
        "request_can_id":"0x7F7","response_can_id":"0x7F8",
        "packed_descriptor_hits":{"request":[f"0x{x:06X}" for x in req_hits],"response":[f"0x{x:06X}" for x in rsp_hits]},
        "rx_adapter":"0x0008312E","standard_opcode_map":"0x00022B24","standard_callback_table":"0x00022B50",
        "get_seed_configured":False,"unlock_configured":False,
        "set_mta":"0x00082C62","download":"0x00081FFE","modify_bits":"0x000820C4","short_upload":"0x00082B1A",
        "write_validator":"0x00098F2C","software_write_window":[f"0x{XCP_LO:08X}",f"0x{XCP_HI:08X}"],
        "high_tail_fully_inside_write_window":XCP_LO<=HIGH_BASE<=HIGH_END<=XCP_HI,
        "placement_static_verdict":"proven: generic XCP DOWNLOAD can directly store tester-controlled bytes into the live-proven high tail while the application handler is executing",
        "normal_route_live_result":{"status":"no_response_timeout","tested_bus":1,"elm327_param":1,"source":str(XCP_LIVE.relative_to(ROOT)),"source_sha256":sha_file(XCP_LIVE)},
        "reachability_boundary":"firmware endpoint exists; only the normal bus1/ELM1 route has been dynamically falsified. Physical/special routing elsewhere remains unobserved.",
      },
      "application_uds":{
        "service_table":"0x00025C54","configured_sids":[f"0x{r['sid']:02X}" for r in service_rows],
        "write_memory_by_address_0x3d_configured":False,
        "read_memory_by_address":{"sid":"0x23","callback":"0x000965C0","sessions":bysid[0x23]["sessions"]},
        "write_data_by_identifier":{"sid":"0x2E","callback":"0x00095978","sessions":bysid[0x2E]["sessions"],"arbitrary_memory_writer":False},
        "request_download":{"sid":"0x34","callback":None,"sessions":[2],"application_download_context_recovered":False},
        "transfer_data":{"sid":"0x36","callback":None,"sessions":[2],"application_transfer_context_recovered":False},
        "request_transfer_exit":{"sid":"0x37","callback":None,"sessions":[2],"application_transfer_context_recovered":False},
        "programming_session_is_disruptive_handoff":True,
      },
      "stock_command5_routine":{
        "rid":"0x100F","routine_table":"0x00026918","callback_table":"0x000256DC","precondition":"0x0008B858","action":"0x0008B872",
        "chain":["0x0008B872","0x0006A0AE","0x00069C58","0x00069BD8","0x00089440"],
        "command5_dispatcher":"0x00089440","input_length":16,"input":"0xFEBE5186","output":"0xFEBE51B6","output_exposed_to_tester":False,
        "xcp_can_rewrite_input_or_output":False,
        "verdict":"real no-service-SA stock command-5 test path, but not a direct SecOC signer API: fixed 16-byte input and local/private result path",
      },
      "control_transfer_audit":{
        "computed_call_sites_reviewed_total":312,
        "computed_call_sites_reviewed_application":305,
        "only_recovered_computed_call_with_fixed_localram_pointer":"0xFEBF0FD0",
        "fixed_localram_pointer_consumers":["0x0000435E","0x0000437C","0x0000440E"],
        "fixed_pointer_is_boot_region":True,"fixed_pointer_inside_xcp_write_window":False,
        "residual_computed_calls":{
          "sites":["0x0008863E","0x0008AF7A","0x0008AF88","0x0008AFAA"],
          "callback_cells":["0xFEBF117C","0xFEBF1180","0xFEBF131C","0xFEBF1320","0xFEBF1324"],
          "all_cells_below_xcp_write_window":True,
          "writers_install_fixed_codeflash_targets":True,
          "bitwise_complement_guards":True,
          "representative_fixed_targets":["0x0008813C","0x00088086","0x0008892C","0x00088876","0x00088D60","0x00088CAA","0x00089170","0x000890BA","0x0008A538","0x0008A5AE","0x0008A600","0x0008A832","0x0008A898"],
          "verdict":"the four call sites not closed by the local 24-instruction backtracker resolve to lower-RAM callback cells whose recovered writers install fixed CodeFlash targets plus complement guards; they are not XCP-writable pivots",
        },
        "exception_saved_pc_audit":{
          "exception_return_sites":["0x000200C8","0x00020102","0x00071372","0x00071456","0x00071502","0x000715AE","0x00071A90","0x00071C40"],
          "exception_return_count":8,
          "application_initial_sp":"0xFEBE2000",
          "temporary_isr_stacks":["0xFEBE0800","0xFEBE1000","0xFEBE1800","0xFEBE2800"],
          "context_wrappers":["0x000713B0","0x0007145C","0x00071508"],
          "eipc_saved_on_interrupted_stack":True,
          "all_recovered_saved_pc_stacks_below_xcp_write_window":True,
          "direct_flow_edges_into_xcp_write_window":0,
        },
        "recovered_static_references_into_xcp_write_window":0,
        "high_tail_function_entries":0,
        "raw_codeflash_u32_pointers_into_high_tail":high_tail_pointer_hits,
        "fixed_dmac_descriptor_audit":{
          "descriptor_apply":"0x00060A6A",
          "recovered_channel_programmers":["0x00060A6A"],
          "recovered_channel_register_accessors":["0x0006091E","0x00060934","0x00060940","0x000609B0","0x00060A6A"],
          "fixed_global_setup":"0x00060A10",
          "recovered_fixed_table_callers":["0x00060462","0x00060C20","0x00061B90","0x000628B2"],
          "tables":dmac_tables,
          "endpoint_field_offsets":["+0x08","+0x0C","+0x18","+0x1C"],
          "endpoint_count":len(dmac_endpoints),
          "endpoints_in_xcp_window":[f"0x{x:08X}" for x in dmac_window_hits],
          "fixed_descriptor_paths_closed":True,
          "boundary":"All recovered F33 fixed CodeFlash DMAC descriptor families and their endpoint fields are target-natively enumerated, and 0x60A6A is the only recovered application channel-register programmer. A separate undiscovered DMA programmer, computed descriptor source, or hardware-owned mutation path remains outside this proof.",
        },
        "ctbp_writer_census":{
          "sleigh_encoding":"op0510=0x3F, SR1115=20, op1626=0x20, op2731=0",
          "alignment":2,
          "image_bytes_scanned":len(image),
          "writers":ctbp_writers,
          "all_ctbp_writers_census_closed":True,
          "only_writer_sets_zero":True,
          "verdict":"CALLT base cannot be retargeted by application/tester state in the exact image; the sole LDSR-to-CTBP is reset's ldsr r0,CTBP at 0x25E",
        },
        "audit_scripts":{
          "computed_calls":{"path":"ghidra/scripts/investigate/ClassifyComputedCallTargets.java","sha256":sha_file(ROOT / "ghidra/scripts/investigate/ClassifyComputedCallTargets.java")},
          "range_references":{"path":"ghidra/scripts/investigate/InspectRangeReferences.java","sha256":sha_file(ROOT / "ghidra/scripts/investigate/InspectRangeReferences.java")},
          "exception_flow":{"path":"ghidra/scripts/investigate/FindExceptionAndXcpFlowOps.java","sha256":sha_file(ROOT / "ghidra/scripts/investigate/FindExceptionAndXcpFlowOps.java")},
          "stack_refs":{"path":"ghidra/scripts/investigate/FindStackPointerOps.java","sha256":sha_file(ROOT / "ghidra/scripts/investigate/FindStackPointerOps.java")},
        },
        "bounded_negative":"No recovered scheduler/task/diagnostic/CAN/CryptoIf/ICU-S/OS/interrupt/PDU callback pointer or saved-PC cell lies in the XCP-writable window. The four residual computed-call sites resolve to guarded lower-RAM callbacks, the exact whole-image CTBP-writer census closes CALLT-base retargeting, and the recovered fixed F33 DMAC families have zero endpoints in the window. Arbitrary synthesized/computed aliases, a separate undiscovered DMA programmer/hardware mutation path, and undiscovered code remain outside this static negative.",
      },
      "mpu":{
        "region_index":1,"bounds":["0xFEBF7C00","0xFEBFFBFC"],"ctx0_mpat":"0x000000B8","ctx1_mpat":"0x000000A8",
        "ctx0":"supervisor R/W/X","ctx1":"supervisor R/X","live_execution_in_high_tail_proven":True,
      },
      "custom_xcp":{
        "table":"0x0002B250","selectors":[f"0x{x:02X}" for x in selectors],"handlers":[f"0x{x:08X}" for x in custom],
        "semantic_roles":{"0xF3":"BUILD_CHECKSUM","0xEB":"SET_CAL_PAGE","0xEA":"GET_CAL_PAGE","0xE4":"COPY_CAL_PAGE"},
        "calibration_page_state":[f"0x{x:08X}" for x in CAL_PAGE_STATE],
        "page_translator":"0x000991D2","build_checksum_worker":"0x00099226",
        "e4_copy":{"handler":"0x00099414","copy_helper":"0x000993F0","source":[f"0x{CAL_SOURCE_LO:08X}",f"0x{CAL_SOURCE_END:08X}"],"destination":[f"0x{CAL_SHADOW_LO:08X}",f"0x{CAL_SHADOW_END:08X}"]},
        "startup_copy":{"application_entry":"0x00020880","startup_coordinator":"0x000637EE","callsite":"0x00063822","copy_helper":"0x000636D4","same_copy_loop_as_xcp":image[0x636D4:0x636F8]==image[0x993F0:0x99414]},
        "calibration_shadow_classification":{
          "source_sha256":sha(image[CAL_SOURCE_LO:CAL_SOURCE_END+1]),
          "recovered_function_entries_in_source_range":0,
          "recovered_function_owned_flow_edges_into_source_range":0,
          "recovered_flow_edges_into_ram_shadow":0,
          "page_state_application_consumers_recovered":0,
          "translator_recovered_use":"BUILD_CHECKSUM memory-address translation",
          "instruction_fetch_or_branch_remap_recovered":False,
          "verdict":"closed as calibration-page data shadow, not a recovered execution overlay or PC pivot",
          "boundary":"Function/flow counts are from the exact F33 recovered Ghidra corpus. Undiscovered code remains outside that census, but exact startup/XCP copy identity and standard page-command semantics independently support the data-shadow classification.",
        },
        "residual_tail_starts_exactly_after_e4_copy":HIGH_BASE==CAL_SHADOW_END+1,
        "arbitrary_high_tail_writer":False,
      },
      "function_evidence":ranges,
      "raw_range_evidence":raw_ranges,
      "architectures":[
        {
          "rank":1,"name":"stock application XCP DOWNLOAD + separate volatile execution pivot",
          "exact_surface":{"set_mta":"0x00082C62","download":"0x00081FFE","write_validator":"0x00098F2C","request":"0x7F7","response":"0x7F8"},
          "placement":"proven statically: tester bytes -> MTA -> direct byte stores in FEBF7C00..FEBFFBFF, including the full high tail",
          "execution":"not recovered; requires a separate already-running-application callback/continuation pivot",
          "network_visibility":"no application->PROGRAMMING handoff is inherent; handler executes in the stock application, so no ECU disappearance is expected from the mechanism itself",
          "privilege_mpu_context":"high tail is MPU region1; ctx0 supervisor R/W/X, ctx1 supervisor R/X. Live execution from the tail is independently proven. Actual XCP handler context must still be confirmed dynamically by a harmless write/readback.",
          "lifetime":"volatile LocalRAM only; power loss removes payload/state",
          "diagnostic_side_effects":"XCP connected/MTA state only under recovered software semantics; no flash/NvM write in DOWNLOAD path. Physical transport route and any gateway diagnostics remain unobserved.",
          "remaining_unknowns":["reachable physical path to packed 0x7F7/0x7F8 endpoint","safe mutable control-transfer object","runtime write context/latency on the live route"],
          "verdict":"best architecture but incomplete"
        },
        {
          "rank":2,"name":"stock RID 0x100F command-5 service",
          "exact_surface":{"rid":"0x100F","action":"0x0008B872","state_machine":"0x0006A0AE/0x00069C58/0x00069BD8","command5_dispatcher":"0x00089440"},
          "placement":"not applicable: stock routine uses its own lower-RAM buffers",
          "execution":"stock application code; no RAM payload required",
          "network_visibility":"application remains online; ordinary RoutineControl path",
          "privilege_mpu_context":"stock diagnostic/crypto task context; no high-tail MPU dependency",
          "lifetime":"routine state is volatile under recovered path; no persistent modification recovered",
          "diagnostic_side_effects":"starts the stock asynchronous crypto test state machine; exact Toyota-facing semantic name/result exposure is not recovered",
          "remaining_unknowns":["exact internal selector/config value under all states","whether any unobserved result-read routine exposes the generated 16 bytes"],
          "verdict":"usable command-5 permission/oracle surface only; fixed 16-byte/private result prevents direct 0x00F/0x0D7/0x0B6 signer use"
        },
        {
          "rank":3,"name":"application UDS 0x34/0x36/0x37",
          "exact_surface":{"service_table":"0x00025C54","request_download":"0x34","transfer_data":"0x36","request_transfer_exit":"0x37"},
          "placement":"no application transfer state recovered; all three service objects have null direct callbacks",
          "execution":"real loader requires session-2 PROGRAMMING handoff into bootloader",
          "network_visibility":"PROGRAMMING handoff is disruptive and makes the EPS temporarily disappear; violates production requirement",
          "privilege_mpu_context":"bootloader/application handoff, not an already-running stock-application mechanism",
          "lifetime":"payload may be volatile, but the transition itself is unacceptable",
          "diagnostic_side_effects":"known ECU disappearance/communication-fault risk during PROGRAMMING transition",
          "remaining_unknowns":[],
          "verdict":"rejected for production"
        },
      ],
      "implementation_readiness":{
        "complete_non_disruptive_loader_and_execution_path":False,
        "safe_inert_vehicle_poc_built":False,
        "reason":"The exact application-mode byte-placement primitive is closed, but no application-mode control-transfer primitive into the high tail is statically recovered; emitting a vehicle execution PoC would therefore invent an unproved pivot.",
      },
      "minimum_next_observations":[
        "Resolve whether the stock 0x7F7/0x7F8 endpoint is physically reachable from any Panda-visible CAN path other than the already-falsified normal bus1/ELM1 route; CONNECT-only is sufficient.",
        "If and only if XCP is reachable, a bounded application-mode DOWNLOAD + SHORT_UPLOAD readback inside the already-live-proven high tail would close transport-to-writer reachability without executing the bytes.",
        "No safe execution live test is defined until static work recovers a concrete mutable control-transfer object or stock callback registration path; do not probe arbitrary PC writes.",
      ],
      "production_answer":"Not yet. F33 has a target-native, unauthenticated application XCP writer that can place arbitrary bytes in FEBFF9F0..FEBFFBFB without a programming handoff, and that tail is live-proven retained/executable. Current static evidence does not provide the second half: a non-disruptive application-mode transfer of control to those bytes."
    }


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,default=OUT); args=ap.parse_args()
    obj=build(); args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n"); print(args.out)
    return 0

if __name__=="__main__": raise SystemExit(main())
