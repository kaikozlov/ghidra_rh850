#!/usr/bin/env python3
"""Build the exact-Crown static contract needed by the volatile native-B6 signer."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CROWN = REPO / "firmware/crown-8965F3012000/CodeFlash.bin"
CAMRY = REPO / "firmware/camry-8965F3307000/CodeFlash.bin"
CROWN_CORPUS = REPO / "data/generated/crown-8965F3012000/decompilations.jsonl"
CAMRY_CORPUS = REPO / "data/generated/camry-8965F3307000/decompilations.jsonl"
OUT = REPO / "data/generated/crown_8965F3012000_b6_signer_contract.json"

CROWN_SHA = "5b89fdbc69edc2f66ef8a557f88b08c758e3146bd4e90067320d7966812b1273"
CAMRY_SHA = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
GP = 0xFEBEB800
TP = 0x00023C98

KEY_CONFIG = 0x25564
PROFILE_BASE = 0x25584
PROFILE_SIZE = 0x50
SIGNAL_TO_PDU = 0x2234C
SIGNAL_COUNT = 278
PDU_TABLE = 0x22578
PDU_COUNT = 46
PDU_OFFSETS = 0x226E8
RX_DESCRIPTOR_BASE = 0x21ED0
TX_PDU_COUNT = 5
NORMAL_RX_COUNT = 41
COM_RAW_BASE = 0xFEBE4891

B6_PDU = 42
B6_PROFILE = 2
B6_QUEUE = 0xFEBE4FA6
B6_SECURED = 0xFEBE5000
B6_AUTH_SYNC = 0xFEBE50EC
B6_COMMITTED = 0xFEBE5114

SIDEBAND_CAN_ID = 0x1DA
SIDEBAND_PDU = 45
SIDEBAND_RAW = 0xFEBE4A61
SIDEBAND_GENERATION = 0xFEBE4E91
SIDEBAND_SIGNAL = 276
SIDEBAND_SIGNAL_VALUE = 0xFEBE7BB6
SIDEBAND_SIGNAL_GENERATION = 0xFEBE7BB7
SIDEBAND_SIGNAL_STATUS = 0xFEBE7BB8

FUNCTIONAL_DIAG_CAN_ID = 0x777
FUNCTIONAL_CANTP_RX_PDU = 0x0805
FUNCTIONAL_PDUR_RX_PDU = 0x0803
FUNCTIONAL_DCM_CHANNEL = 1
FUNCTIONAL_DCM_BUFFER = 0xFEBE527D
FUNCTIONAL_CANTP_CONFIG = 0x2309E
DCM_CHANNEL_CONFIG = 0x25C24
DCM_BUFFER_POINTERS = 0x25BD0
DCM_SERVICE_SET_CONFIG = 0x25948
DCM_SERVICE_DESCRIPTOR_BASE = 0x25990

RESIDENT_BASE = 0xFEBFF9F0
RESIDENT_END = 0xFEBFFBFC
LOW_HELPER_BASE = 0xFEBF0000
LOW_HELPER_END = 0xFEBF0308


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def s16(data: bytes, off: int) -> int:
    return struct.unpack_from("<h", data, off)[0]


def corpus(path: Path) -> dict[int, dict]:
    out: dict[int, dict] = {}
    with path.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") == "function":
                out[int(row["entry_addr"], 16)] = row
    return out


def body(image: bytes, rows: dict[int, dict], address: int) -> bytes:
    row = rows[address]
    chunks = []
    for r in row["body_ranges"]:
        lo = int(r["min"], 16)
        hi = int(r["max"], 16) + 1
        chunks.append(image[lo:hi])
    return b"".join(chunks)


def need(text: str, *tokens: str) -> None:
    missing = [x for x in tokens if x not in text]
    if missing:
        raise ValueError(f"missing exact-Crown decompiler tokens: {missing}")


def profile(image: bytes, idx: int) -> dict[str, object]:
    a = PROFILE_BASE + idx * PROFILE_SIZE
    tx_mac = u16(image, a + 2)
    tx_fv = image[a + 0x15]
    trailer = math.ceil((tx_mac + tx_fv) / 8)
    secured_len = u32(image, a + 0x24)
    return {
        "index": idx,
        "address": f"0x{a:08X}",
        "data_id": f"0x{u16(image, a + 0x0A):03X}",
        "full_cmac_bits": u16(image, a),
        "transmitted_cmac_bits": tx_mac,
        "is_sync": bool(image[a + 9]),
        "freshness_id": u16(image, a + 0x12),
        "full_freshness_bits": image[a + 0x14],
        "transmitted_freshness_bits": tx_fv,
        "cryptoif_handle": u32(image, a + 0x20),
        "secured_pdu_length": secured_len,
        "application_bytes": secured_len - trailer,
        "commit_callback": f"0x{u32(image, a + 0x30):08X}",
        "application_pdu_id": u16(image, a + 0x34),
        "upper_route_id": u16(image, a + 0x36),
        "get_freshness_callback": f"0x{u32(image, a + 0x48):08X}",
        "upper_callback": f"0x{u32(image, a + 0x4C):08X}",
    }


def direct_refs(rows: dict[int, dict], lo: int, hi: int) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for address, row in rows.items():
        for ref in row.get("data_references", []):
            try:
                target = int(ref.get("to_addr", ""), 16)
            except (TypeError, ValueError):
                continue
            if lo <= target < hi:
                refs.append({"function": f"0x{address:08X}", "target": f"0x{target:08X}"})
    return refs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    crown = CROWN.read_bytes()
    camry = CAMRY.read_bytes()
    if len(crown) != 0x100000 or sha(crown) != CROWN_SHA:
        raise SystemExit("Crown CodeFlash identity drift")
    if len(camry) != 0x100000 or sha(camry) != CAMRY_SHA:
        raise SystemExit("Camry CodeFlash identity drift")
    cr = corpus(CROWN_CORPUS)
    ca = corpus(CAMRY_CORPUS)

    # Boot and application architecture roots.
    if crown[:0x9200] != camry[:0x9200]:
        raise ValueError("shared F3 boot core drift")
    if u32(crown, 0xFFDB8) != 0x20880:
        raise ValueError("Crown application entry pointer drift")
    if crown[0xBFD8:0xBFF8] != camry[0xBFD8:0xBFF8]:
        raise ValueError("payload/boot SecurityAccess roots drift")
    if crown[0x20840:0x20850] != camry[0x20840:0x20850]:
        raise ValueError("application SecurityAccess root drift")

    # Exact or nearly exact target-local counterparts used by the resident/helper.
    exact_pairs = {
        "startup_shadow_copy": (0x636D4, 0x62AD4),
        "generic_memcpy": (0x89F2E, 0x879CE),
        "command5_dispatcher": (0x89440, 0x86EE0),
        "command5_sync_wrapper": (0x89BC2, 0x87662),
        "freshness48_packer": (0x90566, 0x8E006),
    }
    exact_map: dict[str, dict[str, object]] = {}
    for name, (cam, crown_addr) in exact_pairs.items():
        cb = body(camry, ca, cam)
        rb = body(crown, cr, crown_addr)
        if cb != rb:
            raise ValueError(f"{name} is no longer byte-identical")
        exact_map[name] = {
            "camry": f"0x{cam:08X}", "crown": f"0x{crown_addr:08X}",
            "size": len(rb), "sha256": sha(rb),
        }

    # Command-5 command/config behavior stays exact even where the engine itself is relinked.
    for off, expected in {
        0x86642: "260f0100610ada0d",
        0x876A4: "bfff3cf8",
        0x876EC: "4437bd5b010a440fbc5b00527f00",
        0x882C4: "d092920e050080070f08",
    }.items():
        raw = bytes.fromhex(expected)
        if crown[off:off + len(raw)] != raw:
            raise ValueError(f"command-5 pin drift at 0x{off:X}")

    profiles = [profile(crown, i) for i in range(3)]
    if [p["data_id"] for p in profiles] != ["0x00F", "0x0D7", "0x0B6"]:
        raise ValueError("Crown secured profile membership drift")
    p2 = profiles[2]
    if not (
        p2["secured_pdu_length"] == 32 and p2["application_bytes"] == 28
        and p2["transmitted_cmac_bits"] == 28 and p2["freshness_id"] == 2
        and p2["application_pdu_id"] == B6_PDU and p2["upper_route_id"] == B6_PDU
    ):
        raise ValueError(f"Crown B6 profile drift: {p2}")
    if (u32(crown, KEY_CONFIG), u32(crown, KEY_CONFIG + 4)) != (1, 4):
        raise ValueError("Crown SecOC key config no longer selects type1/slot4")

    # Queue/freshness RAM geometry, derived from target-local worker bodies and profile fields.
    need(cr[0x8C302]["decompiled_c"], "DAT_febe4f96", "DAT_febe4fd8")
    if B6_QUEUE != 0xFEBE4F96 + B6_PROFILE * 8:
        raise ValueError("Crown B6 queue arithmetic drift")
    if B6_SECURED != 0xFEBE4FD8 + u32(crown, PROFILE_BASE + B6_PROFILE * PROFILE_SIZE + 0x28):
        raise ValueError("Crown B6 secured-buffer arithmetic drift")
    need(cr[0x8E46A]["decompiled_c"], "DAT_febe50f0")
    need(cr[0x8E4E8]["decompiled_c"], "DAT_febe50ec", "puVar5 + *(short *)(param_1 + 2) * 3 + -0x19be")

    # Normal generated-COM geometry and exact Crown B6 wire extraction.
    signal_to_pdu = [u16(crown, SIGNAL_TO_PDU + i * 2) for i in range(SIGNAL_COUNT)]
    pdu_offsets = [u16(crown, PDU_OFFSETS + i * 2) for i in range(PDU_COUNT)]
    if signal_to_pdu[255:268] != [B6_PDU] * 13:
        raise ValueError("Crown B6 scalar membership drift")
    b6_desc = struct.unpack_from("<II", crown, RX_DESCRIPTOR_BASE + (B6_PDU - TX_PDU_COUNT) * 8)
    if (b6_desc[0] & 0x1FFFFFFF, b6_desc[1]) != (0x0B6, 32):
        raise ValueError("Crown B6 normal-Rx descriptor drift")
    b6_raw_offset = pdu_offsets[B6_PDU]
    if b6_raw_offset != 0x1A7:
        raise ValueError(f"Crown B6 raw COM offset drift: 0x{b6_raw_offset:X}")
    unpack = cr[0x4B608]["decompiled_c"]
    for token in (
        "FUN_0007a8e6(0xff,0x1aa,6,0,0,&DAT_febe7b9c);",
        "FUN_0007a8e6(0x100,0x1ab,0x10,0,1,puVar2 + -0xf1a);",
        "FUN_0007a8e6(0x103,0x1ad,1,2,0,puVar2 + -0xf18);",
        "FUN_0007a8e6(0x106,0x1ae,6,0,0,(int)puVar2 + -0x3c5d);",
        "FUN_0007a8e6(0x107,0x1af,8,0,0,puVar2 + -0xf17);",
        "FUN_0007a8e6(0x108,0x1b0,8,0,0,(int)puVar2 + -0x3c5b);",
    ):
        if token not in unpack:
            raise ValueError(f"Crown B6 unpack token drift: {token}")
    need(cr[0x57562]["decompiled_c"], "DAT_febef130 = DAT_febe7b9c", "DAT_febef138 = DAT_febe7ba4", "DAT_febef139 = DAT_febe7ba5")
    need(cr[0xCBC52]["decompiled_c"], "DAT_febec200 = 7", "DAT_febeadb0", "DAT_febec200 = 2")
    need(cr[0xCB000]["decompiled_c"], "DAT_febeadbd", "/ 100")
    need(cr[0xCAC4E]["decompiled_c"], "DAT_febeadbe", "/ 100")

    # Exact Crown target-angle physical/controller scaling. This is the same
    # fixed-point relation independently closed on H/F and F33, but every code
    # address and numeric transform below is checked against Crown CodeFlash.
    target_scale = cr[0xC9B64]["decompiled_c"]
    need(target_scale, "iVar1 = DAT_febeae90 * 2", "DAT_febec09c = DAT_febebfb4", "DAT_febec0c8 = DAT_febebfb4")

    # ID11 selects mode/bank 2. The following target conditioner loads its
    # absolute and per-foreground-step limits from the mode/bank calibration
    # record before clamping the doubled B6 raw target.  AC3C selects one of two
    # calibration halves, but both ID11 records resolve to the same values.
    target_limit_select = cr[0xC9B22]["decompiled_c"]
    need(
        target_limit_select,
        "(DAT_febec200 & 7) == 7",
        "iVar1 = (int)(short)((DAT_febec200 & 7) + (DAT_febeac3c & 1) * 8)",
        "DAT_febec0fe = 0x7ffe", "DAT_febec100 = 0x7ffe",
        "(&PTR_LAB_000d094c)[iVar1 * 0x57]",
        "(&PTR_LAB_000d0950)[iVar1 * 0x57]",
        "DAT_febec0fe", "DAT_febec100",
    )
    target_limit_clamp = cr[0xC9C08]["decompiled_c"]
    need(
        target_limit_clamp,
        "uVar5 = (uint)DAT_febec0fe",
        "uVar4 = (uint)DAT_febec100",
        "DAT_febebfb0 = uVar4 + DAT_febec0a0",
        "DAT_febebfb8 = -uVar5",
        "DAT_febec0a0 = DAT_febebfb8",
    )
    id11_limit_records = []
    for bank_bit, index, expected_delta_ptr in ((0, 2, 0x1A99A), (1, 10, 0x1299A)):
        record = 0xD094C + index * 0x15C
        absolute_ptr = u32(crown, record)
        delta_ptr = u32(crown, record + 4)
        absolute_internal = s16(crown, absolute_ptr)
        delta_internal = s16(crown, delta_ptr)
        if not (
            absolute_ptr == 0xB057E and delta_ptr == expected_delta_ptr
            and absolute_internal == 3490 and delta_internal == 7
        ):
            raise ValueError(
                f"Crown ID11 target-limit calibration drift bank={bank_bit}: "
                f"record=0x{record:X} abs=0x{absolute_ptr:X}/{absolute_internal} "
                f"delta=0x{delta_ptr:X}/{delta_internal}"
            )
        id11_limit_records.append({
            "ac3c_bank_bit": bank_bit,
            "mode_index": index,
            "record": f"0x{record:08X}",
            "absolute_limit_pointer": f"0x{absolute_ptr:08X}",
            "absolute_limit_internal": absolute_internal,
            "step_limit_pointer": f"0x{delta_ptr:08X}",
            "step_limit_internal": delta_internal,
        })
    id11_raw_limit = 3490 // 2
    if id11_raw_limit * 2 != 3490:
        raise ValueError("Crown ID11 internal/raw target-limit relation no longer integral")
    measured_unpack = cr[0x4AEF8]["decompiled_c"]
    need(
        measured_unpack,
        "FUN_0007a8e6(0xb9,0x11f,0xc,0,1,&DAT_febe7b2c)",
        "FUN_0007a8e6(0xba,0x123,4,4,1,(int)puVar2 + -0x3ccd)",
    )
    measured_reconstruct = cr[0xCB640]["decompiled_c"]
    need(
        measured_reconstruct,
        "((int)DAT_febeacc5 + DAT_febeadfe * 0xf) * 0x6fb) / 0x200",
        "iVar13 = iVar12 * 2 - iVar1",
        "puVar6[0x26f] = iVar13",
    )
    measured_republish = cr[0xCB730]["decompiled_c"]
    need(
        measured_republish,
        "iVar2 = DAT_febeae5e * 2 - iVar2",
        "DAT_febec1d2", "DAT_febec1d4", "DAT_febec1d6",
    )
    # CB640 first stores (2*AE5E - measured_internal). CB730 later consumes that
    # voted value and computes (2*AE5E - prior), algebraically restoring the
    # same-sign measured_internal term. Pin the auxiliary AE5E copy edge too so
    # this cancellation cannot silently become an assumed sign convention.
    aux_writer = cr[0xB9066]["decompiled_c"]
    need(aux_writer, "DAT_febeb49e", "DAT_febeafe8", "0x188b", "0x4000")
    bb51a_refs = {(r.get("from_addr"), r.get("ref_type"), r.get("to_addr")) for r in cr[0xBB51A].get("data_references", [])}
    if not ({
        ("0x000bb8b4", "READ", "0xfebeb49e"),
        ("0x000bb8b8", "WRITE", "0xfebeae5e"),
    } <= bb51a_refs):
        raise ValueError("Crown AE5E auxiliary copy edge drift")
    comparator = cr[0xC9D7E]["decompiled_c"]
    need(
        comparator,
        "iVar1 = (iVar1 * 0xb76) / 0x400",
        "DAT_febebfdc = (iVar2 * 0xb76) / 0x400",
        "DAT_febebfe0 = iVar1 - DAT_febebfdc",
    )
    did1037 = cr[0x4D550]["decompiled_c"]
    need(did1037, "asStack_a[0] = DAT_febe7836", "FUN_000699dc((int)asStack_a[0],param_1)")
    measured_stage = cr[0x4749C]["decompiled_c"]
    need(measured_stage, "FUN_00069a2a((int)DAT_febe7b2c,auStack_e)", "-0x3fca")
    measured_snapshot = cr[0xB3842]["decompiled_c"]
    need(measured_snapshot, "DAT_febeb16c = DAT_febef1a0 * 0xf + (short)DAT_febef06f")

    controller_deg_num = 1024
    controller_deg_den = 17870
    controller_deg = controller_deg_num / controller_deg_den
    controller_mrad = controller_deg * math.pi / 180.0 * 1000.0

    # Diagnostic transport is target-native too. The boot core is byte-identical
    # through these tables, while the application carries a relocated but value-
    # identical physical/functional/secondary address block and only the CAN1
    # interrupt pair is active.
    if (u32(crown, 0x8924), u32(crown, 0x8930), u32(crown, 0x894C)) != (0x7A1, 0x777, 0x7A9):
        raise ValueError("Crown boot diagnostic address table drift")
    app_diag_ids = [u32(crown, off) for off in (0x21E68, 0x21E70, 0x21E78, 0x21E80, 0x21E88, 0x21E90, 0x21E98)]
    if app_diag_ids != [0x7A9, 0x7A9, 0x7A8, 0x7A8, 0x7A1, 0x777, 0x7A0]:
        raise ValueError(f"Crown application diagnostic address block drift: {app_diag_ids}")
    app_vectors = {irq: u32(crown, 0x20200 + irq * 4) for irq in (184, 185, 187, 188, 192, 193)}
    if not (
        app_vectors[187] == 0x65500 and app_vectors[188] == 0x654BE
        and len({app_vectors[x] for x in (184, 185, 192, 193)}) == 1
        and app_vectors[184] == 0x6221E
    ):
        raise ValueError(f"Crown application RSCFD interrupt routing drift: {app_vectors}")

    # Stock-firmware host->resident ingress. The functional 0x777 route is a
    # normal eight-byte ISO-TP receive endpoint. Its CanTp record maps Rx PDU
    # 0x805 to upper/PduR 0x803, which DCM maps to channel1 and its 0x100-byte
    # buffer at FEBE527D. The channel's request-type byte resolves to 1
    # (functional) through the exact DCM configuration graph.
    functional_address_row = 0x21E90
    if [u32(crown, functional_address_row), u32(crown, functional_address_row + 4)] != [FUNCTIONAL_DIAG_CAN_ID, 8]:
        raise ValueError("Crown functional diagnostic CAN row drift")
    functional_cantp = [u16(crown, FUNCTIONAL_CANTP_CONFIG + i) for i in range(0, 0x20, 2)]
    if functional_cantp != [
        0x0101, FUNCTIONAL_PDUR_RX_PDU, FUNCTIONAL_CANTP_RX_PDU, 0xFFFF, FUNCTIONAL_PDUR_RX_PDU, 0xFFFF, 0x0100, 0x0000,
        0x0000, 0x0014, 0x0000, 0x0000, 0x0000, 0x0001, 0x0000, 0x0000,
    ]:
        raise ValueError(f"Crown functional CanTp record drift: {functional_cantp}")
    if [u32(crown, DCM_BUFFER_POINTERS + i * 8) for i in range(3)] != [0xFEBE517D, 0xFEBE527D, 0xFEBE537D]:
        raise ValueError("Crown DCM receive-buffer pointers drift")
    dcm_upper_ids = [u16(crown, DCM_CHANNEL_CONFIG + i * 12 + 10) for i in range(3)]
    if dcm_upper_ids != [2, 3, 4]:
        raise ValueError(f"Crown DCM upper-PDU mapping drift: {dcm_upper_ids}")

    def dcm_request_type(channel: int) -> int:
        row = DCM_CHANNEL_CONFIG + channel * 12
        group = u16(crown, row)
        route = u16(crown, row + 2)
        config_index = u16(crown, row + 4)
        route_table = u32(crown, 0x25BFC + group * 20)
        protocol = u32(crown, route_table + route * 4)
        service_config = u32(crown, protocol + 4)
        return crown[service_config + config_index * 12 + 8]

    dcm_request_types = [dcm_request_type(i) for i in range(3)]
    if dcm_request_types != [0, 1, 0]:
        raise ValueError(f"Crown DCM addressing-type map drift: {dcm_request_types}")
    # Close the synchronous CanTp->PduR->DCM callback chain for upper PDU
    # 0x0803. The generic PduR vtable resolves StartOfReception/CopyRxData/
    # TpRxIndication to wrappers 7990C/79920/79944, whose configured DCM
    # callbacks are 8FB5E/8FBF2/8FC72. CopyRxData reaches 91888; TpRxIndication
    # only queues the request. Service lookup/dispatch is a separate DCM-main
    # path at 8F6AA -> 8F006, so the resident hook immediately after 792EE
    # samples the completed N-SDU before service processing can consume it.
    pdur_vtable = u32(crown, 0x21DFC + 4)
    if pdur_vtable != 0x21D48:
        raise ValueError(f"Crown PduR group1 vtable drift: 0x{pdur_vtable:08X}")
    pdur_tp_wrappers = [u32(crown, pdur_vtable + offset) for offset in (0x0C, 0x10, 0x18)]
    if pdur_tp_wrappers != [0x7990C, 0x79920, 0x79944]:
        raise ValueError(f"Crown PduR TP callback wrapper drift: {pdur_tp_wrappers}")
    dcm_tp_callbacks = [u32(crown, address) for address in (0x21884, 0x21888, 0x21890)]
    if dcm_tp_callbacks != [0x8FB5E, 0x8FBF2, 0x8FC72]:
        raise ValueError(f"Crown DCM TP callback drift: {dcm_tp_callbacks}")
    copy_rx = cr[0x91888]["decompiled_c"]
    need(copy_rx, "*(undefined1 *)*piVar1 = uVar3", "(&DAT_febe5520)[param_1 * 8]")
    copy_cb = cr[0x8FBF2]["decompiled_c"]
    need(copy_cb, "FUN_00091888")
    indication_cb = cr[0x8FC72]["decompiled_c"]
    need(indication_cb, "FUN_00091418", "FUN_00091734(0)")
    if "FUN_0008f006" in indication_cb:
        raise ValueError("Crown DCM TpRxIndication unexpectedly dispatches services inline")
    dcm_main = cr[0x8F6AA]["decompiled_c"]
    need(dcm_main, "FUN_0008f006")

    # Crown receives classic 0x127, but the exact EPS generated-COM unpacker does
    # not extract B5[7:4]. Upstream Toyota TSS3 calls that nibble GEAR; without a
    # Crown-native semantic consumer or field enum we deliberately do not use it
    # as an automatic Park safety gate.
    pdu127 = 25
    pdu127_desc = struct.unpack_from("<II", crown, RX_DESCRIPTOR_BASE + (pdu127 - TX_PDU_COUNT) * 8)
    pdu127_signals = [i for i, p in enumerate(signal_to_pdu) if p == pdu127]
    pdu127_unpack = cr[0x4AA6C]["decompiled_c"]
    if (pdu127_desc[0] & 0x1FFFFFFF, pdu127_desc[1]) != (0x127, 8) or pdu127_signals != list(range(124, 134)):
        raise ValueError("Crown 0x127 generated-COM geometry drift")
    for token in (
        "FUN_0007a8e6(0x82,0xda,0xb,0,1,&DAT_febe7af6)",
        "FUN_0007a8e6(0x7c,0xd7,6,2,0,(int)puVar2 + -0x3d06)",
        "FUN_0007a8e6(0x7e,0xd8,1,3,0,(int)puVar2 + -0x3d05)",
    ):
        if token not in pdu127_unpack:
            raise ValueError(f"Crown 0x127 unpack token drift: {token}")
    if ",0xdc," in pdu127_unpack:
        raise ValueError("Crown unexpectedly extracts the upstream-prior-art 0x127 B5 gear nibble")

    # Candidate Crown-native sideband: accepted classic 0x1DA/DLC8 with only B0 low nibble
    # configured in generated COM. B1..B7 have no generated scalar extraction.
    side_desc = struct.unpack_from("<II", crown, RX_DESCRIPTOR_BASE + (SIDEBAND_PDU - TX_PDU_COUNT) * 8)
    side_signals = [i for i, p in enumerate(signal_to_pdu) if p == SIDEBAND_PDU]
    if (side_desc[0] & 0x1FFFFFFF, side_desc[1]) != (SIDEBAND_CAN_ID, 8):
        raise ValueError("Crown 0x1DA descriptor drift")
    if pdu_offsets[SIDEBAND_PDU] != 0x1D0 or side_signals != [SIDEBAND_SIGNAL]:
        raise ValueError("Crown 0x1DA generated-COM geometry drift")
    need(cr[0x4B874]["decompiled_c"], "FUN_0007a8e6(0x114,0x1d0,4,0,0,&DAT_febe7bb6)")
    side_snapshot = cr[0x57562]["decompiled_c"]
    need(side_snapshot, "DAT_febef156 = DAT_febe7bb6", "DAT_febef157 = DAT_febe7bb8")
    side_readers = []
    for row in cr.values():
        for ref in row.get("data_references", []):
            if ref.get("ref_type") == "READ" and ref.get("to_addr") in ("0xfebef156", "0xfebef157"):
                side_readers.append({"function": row["entry_addr"], "target": ref["to_addr"]})
    side_raw_refs = direct_refs(cr, SIDEBAND_RAW, SIDEBAND_RAW + 8)
    if side_readers or side_raw_refs:
        raise ValueError(
            f"unexpected direct Crown 0x1DA consumers: snapshots={side_readers} raw={side_raw_refs}"
        )

    # Crown-specific READY/stationary guard. Do not import F33's 0x127 gear layout.
    # 0x51E signal155 is B0[7]. 0x0AA carries four 15-bit wheel values and the
    # target-native normalizer subtracts 0x1A6F from each value.
    ready_unpack = cr[0x4ACD2]["decompiled_c"]
    need(ready_unpack, "FUN_0007a8e6(0x9b,0xf7,1,7,0,&DAT_febe7b15)")
    wheel_unpack = cr[0x4AFE4]["decompiled_c"]
    for token in (
        "FUN_0007a8e6(0xc1,0x13f,0xf,0,0,&DAT_febe7b38)",
        "FUN_0007a8e6(0xc3,0x141,0xf,0,0,(int)puVar2 + -0x3cc6)",
        "FUN_0007a8e6(0xc5,0x143,0xf,0,0,puVar2 + -0xf31)",
        "FUN_0007a8e6(199,0x145,0xf,0,0,(int)puVar2 + -0x3cc2)",
    ):
        if token not in wheel_unpack:
            raise ValueError(f"Crown 0x0AA wheel unpack drift: {token}")
    if wheel_unpack.count("FUN_0004a988(0,0x1a6f,") != 4:
        raise ValueError("Crown 0x0AA wheel centering drift")
    need(cr[0x4A988]["decompiled_c"], "(param_3 & 0xffff) - (int)param_2")

    # Scheduler/hook boundary. The helper executes after the native receive drain and before
    # the untouched receive tail / later SecOC scheduling.
    aggregate = cr[0x65BE2]["decompiled_c"]
    receive = cr[0x7961A]["decompiled_c"]
    need(aggregate, "FUN_0006909e();", "FUN_0007961a();", "FUN_00096362();")
    need(receive, "FUN_000798f0();", "FUN_000796c2();", "FUN_00079ea2();", "FUN_000792ee();", "FUN_00079a10();")
    if crown[0x7961E:0x79628] != bytes.fromhex("e40ff385a10601fe8a35"):
        raise ValueError("Crown receive FE01 gate drift")

    # Application UDS SID 0x23 is present in EXTENDED and its entry wrapper is the same as F33.
    # Derive all three configured service sets rather than inferring descriptor
    # completeness from a contiguous table scan. FUN_8EE90 maps message channel
    # IDs 2/3/4 onto these rows; channel 1 above carries upper ID 3, so row 1 is
    # specifically the functional-0x777 service set.
    expected_service_sets = [
        {"message_channel_id": 2, "indices": list(range(17)), "index_table": 0x25960},
        {"message_channel_id": 3, "indices": [17, 2, 7, 9, 13, 14], "index_table": 0x25928},
        {"message_channel_id": 4, "indices": [18, 19, 20, 21, 22], "index_table": 0x25984},
    ]
    service_sets: list[dict[str, object]] = []
    referenced_service_indices: set[int] = set()
    for row_index, expected in enumerate(expected_service_sets):
        row = DCM_SERVICE_SET_CONFIG + row_index * 8
        message_channel_id = u16(crown, row)
        count = u16(crown, row + 2)
        index_table = u32(crown, row + 4)
        indices = [u16(crown, index_table + i * 2) for i in range(count)]
        observed = {"message_channel_id": message_channel_id, "indices": indices, "index_table": index_table}
        if observed != expected:
            raise ValueError(f"Crown DCM service-set row {row_index} drift: {observed}")
        referenced_service_indices.update(indices)
        service_sets.append(observed)
    if referenced_service_indices != set(range(23)):
        raise ValueError(f"Crown DCM service-descriptor coverage drift: {sorted(referenced_service_indices)}")

    all_service_sids = [crown[DCM_SERVICE_DESCRIPTOR_BASE + i * 24 + 16] for i in range(23)]
    expected_service_sids = [0x10,0x11,0x14,0x19,0x22,0x23,0x27,0x28,0x2E,0x31,0x34,0x36,0x37,0x3E,0x85,0xAB,0xBA,0x10,0x10,0x19,0x22,0x3E,0xAB]
    if all_service_sids != expected_service_sids or 0xC6 in all_service_sids or 0xC7 in all_service_sids:
        raise ValueError(f"Crown application UDS service table drift: {all_service_sids}")
    functional_service_indices = expected_service_sets[1]["indices"]
    functional_service_sids = [all_service_sids[i] for i in functional_service_indices]
    if functional_service_sids != [0x10, 0x14, 0x28, 0x31, 0x3E, 0x85]:
        raise ValueError(f"Crown functional UDS service-set drift: {functional_service_sids}")
    sid23 = DCM_SERVICE_DESCRIPTOR_BASE + all_service_sids.index(0x23) * 24
    if u32(crown, sid23) != 0x94060 or crown[0x94060:0x94060+18] != camry[0x965C0:0x965C0+18]:
        raise ValueError("Crown application SID23 wrapper drift")
    service_lookup = cr[0x8EA38]["decompiled_c"]
    need(service_lookup, "*param_4 = 0x11", "if (puVar2 == (undefined *)0x0)")
    service_dispatch = cr[0x8F006]["decompiled_c"]
    need(service_dispatch, "FUN_0008ea38", "if (cStack_15 != '\\x11')", "FUN_0008ec52(puVar5,cStack_15)")
    response_select = cr[0x8EC7A]["decompiled_c"]
    need(
        response_select,
        "*(char *)(param_1 + 0x10) == '\\x01'",
        "cVar1 == '\\x11'",
        "uVar3 = 3",
        "FUN_0008f782(param_1,uVar3)",
    )

    high_refs = direct_refs(cr, RESIDENT_BASE, RESIDENT_END)
    low_refs = direct_refs(cr, LOW_HELPER_BASE, LOW_HELPER_END)
    if high_refs or low_refs:
        raise ValueError(f"resident/helper direct-reference census drift: high={high_refs} low={low_refs}")

    out = {
        "schema": "crown-8965f3012000-b6-signer-contract-v1",
        "target": {
            "software_id": "8965F3012000",
            "secondary_id": "8A3113008000",
            "codeflash_sha256": CROWN_SHA,
            "mcu": "R7F701381",
            "gp": f"0x{GP:08X}", "tp": f"0x{TP:08X}",
        },
        "shared_architecture": {
            "boot_core_0_91ff_identical_to_f33": True,
            "crypto_roots_identical_to_f33": True,
            "exact_body_mappings": exact_map,
        },
        "secoc": {
            "key_config": {"address": f"0x{KEY_CONFIG:08X}", "type": 1, "selector": 4},
            "profiles": profiles,
            "b6_profile": B6_PROFILE,
            "b6_queue_record": f"0x{B6_QUEUE:08X}",
            "b6_secured_buffer": f"0x{B6_SECURED:08X}",
            "authenticated_sync": {"trip": f"0x{B6_AUTH_SYNC:08X}", "reset": f"0x{B6_AUTH_SYNC + 4:08X}"},
            "committed_slot1": {"trip": f"0x{B6_COMMITTED:08X}", "reset": f"0x{B6_COMMITTED + 4:08X}", "message": f"0x{B6_COMMITTED + 8:08X}"},
            "command5_sync_wrapper": "0x00087662",
            "freshness48_packer": "0x0008E006",
        },
        "b6_application": {
            "pdu_id": B6_PDU,
            "raw_buffer": f"0x{COM_RAW_BASE + b6_raw_offset:08X}",
            "target_lateral_id": {"signal": 255, "wire": "B3[5:0]", "raw": "0xFEBE7B9C", "snapshot": "0xFEBEADB0", "id11_bank": 2},
            "target_angle": {"signal": 256, "wire": "B4:B5 signed16", "raw": "0xFEBE7B98"},
            "signal259": {"wire": "B6[2]", "replacement_value": 0},
            "native_sequence": {"signal": 262, "wire": "B7[5:0]"},
            "contribution_1": {"signal": 263, "wire": "B8", "snapshot": "0xFEBEADBD", "scale": "percent / 100", "replacement_value": 100},
            "contribution_2": {"signal": 264, "wire": "B9", "snapshot": "0xFEBEADBE", "scale": "percent / 100", "replacement_value": 100},
            "replacement": "preserve native B0..B27 except B3 low6=11, B4:B5=target raw, B6 bit2=0, B8=B9=100; preserve native B7 sequence and all other fields",
        },
        "target_angle_scaling": {
            "physical_scale_closed": True,
            "oem_wire_unit_name_closed": False,
            "controller_equivalent_fraction_deg_per_b6_count": {"numerator": controller_deg_num, "denominator": controller_deg_den},
            "controller_equivalent_deg_per_b6_count": controller_deg,
            "controller_equivalent_mrad_per_b6_count": controller_mrad,
            "target_internal_relation": "C9B64: target_internal_pre_controller = saturate(2 * signed16(B6 B4:B5))",
            "id11_limits": {
                "selector": "CBC52 maps Target Lateral ID 11 to C200 mode 2; C9B22 then selects index 2+(AC3C&1)*8",
                "calibration_records": id11_limit_records,
                "absolute_limit_internal": 3490,
                "absolute_limit_b6_raw": id11_raw_limit,
                "absolute_limit_deg": id11_raw_limit * controller_deg,
                "step_limit_internal_per_foreground_invocation": 7,
                "step_limit_b6_raw_equivalent_per_foreground_invocation": 3.5,
                "step_limit_deg_equivalent_per_foreground_invocation": 3.5 * controller_deg,
                "clamp_function": "0x000C9C08",
                "boundary": "The step limit is per target-conditioner foreground invocation; no time unit is attached here. The host hard bound uses only the exact +/-1745 raw absolute envelope.",
            },
            "measured_wire": {
                "can_id": "0x025",
                "coarse_signal": 185,
                "coarse_wire": "signed12 starting at raw offset 0x11F",
                "fraction_signal": 186,
                "fraction_wire": "signed4 high nibble at raw offset 0x123",
                "combined_relation": "15*coarse + fraction",
                "combined_unit": "0.1 deg",
                "oem_join": "Crown DID1037 callback reads the same coarse source; current Toyota P5 Techstream names DID1037 Steering Angle at 1.5 deg/count, leaving the signed4 fraction as 0.1 deg/count",
            },
            "measured_internal_relation": "CB640: measured_internal=trunc((fraction + 15*coarse) * 1787 / 512), then stores prior=2*AE5E-measured_internal",
            "measured_republish": "CB730 consumes the voted prior and computes 2*AE5E-prior; substituting CB640 gives measured_internal with the original sign, then republishes it to C1D2/C1D4/C1D6",
            "measured_sign_proof": "CB640 prior=2*A-M and CB730 output=2*A-prior => output=M; AE5E cancels exactly before the common comparator",
            "auxiliary_term": "AE5E is copied from FEBEB49E by BB51A; B9066 computes FEBEB49E independently. Its physical meaning is not required for the scale/sign proof because it cancels algebraically.",
            "matched_controller": "C9D7E applies the same 0xB76/0x400 gain to target and measured domains before subtracting measured from target",
            "derivation": "2 B6-internal counts per B6 raw count versus (10 tenths/deg)*(1787/512) measured-internal counts/deg => 2*512/(10*1787) = 1024/17870 deg/count",
            "quantization_boundary": "integer truncation/saturation remain; the fraction is the exact linearized controller-equivalent conversion, not a claim that every integer code has a unique exact degree value",
            "functions": {
                "b6_unpack": "0x0004B608", "b6_target_scale": "0x000C9B64", "fd025_unpack": "0x0004AEF8",
                "fd025_stage": "0x0004749C", "did1037": "0x0004D550", "measured_reconstruct": "0x000CB640",
                "measured_republish": "0x000CB730", "matched_comparator": "0x000C9D7E",
            },
        },
        "runtime": {
            "resident_range": [f"0x{RESIDENT_BASE:08X}", f"0x{RESIDENT_END - 1:08X}"],
            "helper_range": [f"0x{LOW_HELPER_BASE:08X}", f"0x{LOW_HELPER_END - 1:08X}"],
            "direct_reference_census": {"resident": high_refs, "helper": low_refs},
            "foreground": {
                "aggregate": "0x00065BE2", "pre_receive_call": "0x0006909E", "stock_tail_after_receive": "0x00065BEE",
            },
            "receive_hook": {
                "wrapper": "0x0007961A", "pre_helper_calls": ["0x000798F0", "0x000796C2", "0x00079EA2", "0x000792EE"],
                "native_receive_drain": "0x000792EE", "stock_tail_after_drain": "0x00079638",
                "position": "after native receive drain and before untouched receive tail / later stock SecOC scheduling",
            },
            "application_sid23": {"service_table": "0x00025990", "callback": "0x00094060", "session": "EXTENDED"},
        },
        "diagnostic_transport": {
            "boot": {"physical_request": "0x7A1", "functional_request": "0x777", "physical_response": "0x7A9", "evidence": "exact Crown boot tables 0x8920/0x8948 inside byte-identical 0x0000..0x91FF boot core"},
            "application": {"address_block": "0x00021E68..0x00021E9F", "physical_request": "0x7A1", "functional_request": "0x777", "physical_response": "0x7A9", "secondary_request": "0x7A0", "secondary_response": "0x7A8"},
            "controller": {"rscfd_channel": 1, "rx_irq": 187, "tx_irq": 188, "rx_vector": "0x00065500", "tx_vector": "0x000654BE", "other_can_irq_vectors_default": True},
            "panda_stock_wire_route": {"bus": 1, "elm327_param": 1, "status": "contributor-reported acquisition route; no machine-readable route transcript accompanied the imported dumps"},
        },
        "park_gate_boundary": {
            "can_id": "0x127", "format": "classic", "dlc": 8, "pdu_id": 25,
            "configured_signal_ids": list(range(124, 134)),
            "exact_eps_extractions": ["signal130 raw+3 signed11", "signal124 B0[7:2]", "signal126 B1[3]"],
            "b5_high_nibble_extracted": False,
            "upstream_prior_art": "Toyota TSS3 DBC names 0x127 B5[7:4] GEAR, but exact Crown EPS firmware does not consume that nibble",
            "runtime_policy": "Park remains explicit operator confirmation; do not turn upstream gear enum into an exact-Crown safety claim",
        },
        "functional_diagnostic_ingress": {
            "status": "firmware-closed-live-unqualified",
            "can_id": f"0x{FUNCTIONAL_DIAG_CAN_ID:X}",
            "format": "classic",
            "dlc": 8,
            "wire": {
                "isotp": "single frame, PCI=0x07",
                "loader": "07 C6 index 00 word_le32",
                "runtime": "07 C7 seq 00 target_hi target_lo 00 00",
            },
            "application_route": {
                "address_row": f"0x{functional_address_row:08X}",
                "cantp_rx_pdu": f"0x{FUNCTIONAL_CANTP_RX_PDU:04X}",
                "cantp_config": f"0x{FUNCTIONAL_CANTP_CONFIG:08X}",
                "pdur_rx_pdu": f"0x{FUNCTIONAL_PDUR_RX_PDU:04X}",
                "dcm_upper_pdu": 3,
                "dcm_channel": FUNCTIONAL_DCM_CHANNEL,
                "dcm_buffer": f"0x{FUNCTIONAL_DCM_BUFFER:08X}",
                "dcm_buffer_capacity": 256,
                "request_type": "functional",
                "pdur_tp_wrappers": {
                    "start_of_reception": "0x0007990C",
                    "copy_rx_data": "0x00079920",
                    "rx_indication": "0x00079944",
                },
                "dcm_tp_callbacks": {
                    "start_of_reception": "0x0008FB5E",
                    "copy_rx_data": "0x0008FBF2",
                    "rx_indication": "0x0008FC72",
                    "copy_engine": "0x00091888",
                },
            },
            "service_semantics": {
                "loader_sid": "0xC6",
                "runtime_sid": "0xC7",
                "descriptor_count": len(all_service_sids),
                "configured_service_ids": [f"0x{x:02X}" for x in all_service_sids],
                "service_sets": [
                    {
                        "message_channel_id": row["message_channel_id"],
                        "indices": row["indices"],
                        "index_table": f"0x{int(row['index_table']):08X}",
                    }
                    for row in service_sets
                ],
                "functional_service_ids": [f"0x{x:02X}" for x in functional_service_sids],
                "c6_configured": False,
                "c7_configured": False,
                "unsupported_service_nrc": "0x11",
                "functional_nrc11_response": "suppressed",
                "service_lookup": "0x0008EA38",
                "response_selector": "0x0008EC7A",
                "dcm_main_worker": "0x0008F6AA",
                "service_dispatch": "0x0008F006",
                "rx_indication_dispatches_service_inline": False,
            },
            "resident_sampling_boundary": "after 0x792EE native receive drain has synchronously copied and indicated the complete N-SDU, before the untouched 0x79638 receive tail; service lookup runs later on the separate 0x8F6AA -> 0x8F006 DCM-main path",
            "persistent_flash_write": False,
            "firmware_patch": False,
        },
        "sideband_candidate": {
            "status": "rejected-as-idle-private-mailbox",
            "can_id": "0x1DA", "format": "classic", "dlc": 8, "pdu_id": SIDEBAND_PDU,
            "raw_buffer": f"0x{SIDEBAND_RAW:08X}", "raw_generation": f"0x{SIDEBAND_GENERATION:08X}",
            "configured_signal": {"signal": SIDEBAND_SIGNAL, "wire": "B0[3:0]", "value": f"0x{SIDEBAND_SIGNAL_VALUE:08X}", "generation": f"0x{SIDEBAND_SIGNAL_GENERATION:08X}", "status": f"0x{SIDEBAND_SIGNAL_STATUS:08X}"},
            "unused_wire_bytes": [1,2,3,4,5,6,7],
            "direct_snapshot_readers": side_readers,
            "direct_raw_buffer_references": side_raw_refs,
            "loader_frame": "00 C6 5A word_le32 index",
            "runtime_frame": "00 C7 5A target_hi target_lo 00 00 seq",
            "live_gate": "contributor preflight observed FEBE4E91 movement; exact firmware trace closes that byte to normal PDU45/0x1DA receive delivery",
            "boundary": "Generated-COM configuration still proves B1..B7 have no configured scalar extraction and no direct reader of the sole B0-low4 snapshot, but the original private-idle-mailbox premise is false on the contributor Crown. Do not transmit active 0x1DA sideband frames; the active runtime instead uses the stock functional-diagnostic ingress closed separately in this contract.",
        },
        "vehicle_state_guard": {
            "ready": {"can_id": "0x51E", "wire": "B0[7]", "signal": 155, "unpacker": "0x0004ACD2"},
            "wheel_speed": {
                "can_id": "0x0AA", "wire": ["B0:B1 15-bit", "B2:B3 15-bit", "B4:B5 15-bit", "B6:B7 15-bit"],
                "signals": [193, 195, 197, 199], "unpacker": "0x0004AFE4", "normalizer": "0x0004A988",
                "raw_zero": 6767, "stationary_guard": "absolute centered raw <= 50 counts on all four wheels",
            },
            "park": "operator-confirmed; F33 0x127 B5-high4 gear decode is deliberately not transferred to Crown",
        },
        "port_boundary": {
            "closed": ["RAM geometry", "startup/foreground replay", "post-receive/pre-SecOC hook", "B6 queue/buffer", "freshness state", "slot4 command5", "B6 mutation tuple", "B6 controller-equivalent target scale", "application SID23 readback", "Crown READY/stationary guard", "stock functional 0x777 host-to-resident ingress"],
            "live_required": ["functional 0x777 mailbox delivery", "resident startup survival", "native B6 presence", "no-mutation native trailer equality", "stationary one-shot replacement"],
            "not_claimed": ["literal OEM B6 engineering-unit label", "road actuation", "safe active 0x1DA overlay"],
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
