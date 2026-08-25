#!/usr/bin/env python3
"""Build the target-native 8965H1202000 FD/control-interface report.

This report deliberately separates raw generated configuration from recovered
consumer semantics. Direct-reference negatives are bounded to the target-native
Ghidra decompiler corpus; they are not claims against arbitrary computed-pointer
accesses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
GP = 0xFEBEB800
TX = struct.Struct("<IBBH")
PDU = struct.Struct("<HBBHBB")
TARGET_ANGLE = REPO / "data/generated/corolla_8965H1202000_b6_target_angle_ingress.json"
STATE_EVIDENCE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_codeflash(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) == 0x100000:
        return data
    if len(data) == 0x200000 and data[0x100000:] == b"\xff" * 0x100000:
        return data[:0x100000]
    raise ValueError(f"unsupported CodeFlash geometry: {path} size={len(data):#x}")


def validate_function_evidence(path: Path, image: bytes) -> tuple[dict, dict[int, dict]]:
    doc = json.loads(path.read_text())
    if doc["image"]["sha256"] != sha256(image):
        raise ValueError("function evidence is bound to a different image")
    rows = {}
    for row in doc["functions"]:
        entry = int(row["entry"], 16)
        body = image[entry : entry + row["body_size"]]
        if sha256(body) != row["body_sha256"]:
            raise ValueError(f"function raw-body mismatch at {entry:#x}")
        if sha256(row["decompiled_c"].encode()) != row["decompiled_c_sha256"]:
            raise ValueError(f"function decompiler-C mismatch at {entry:#x}")
        rows[entry] = row
    return doc, rows


def validate_reference_census(path: Path, image: bytes) -> dict:
    doc = json.loads(path.read_text())
    if doc["image"]["sha256"] != sha256(image):
        raise ValueError("reference census is bound to a different image")
    for term in doc["terms"].values():
        for row in term["matches"]:
            entry = int(row["entry"], 16)
            body = image[entry : entry + row["body_size"]]
            if sha256(body) != row["body_sha256"]:
                raise ValueError(f"reference-census body mismatch at {entry:#x}")
            needle = term["substring"].lower()
            if not all(needle in line.lower() for line in row["matching_lines"]):
                raise ValueError(f"reference-census line mismatch for {needle}")
    return doc


def need(code: str, *needles: str) -> None:
    for needle in needles:
        if needle not in code:
            raise ValueError(f"target-native semantic pin missing: {needle!r}")


def call_graph(functions: dict[int, dict]) -> dict[int, set[int]]:
    graph: dict[int, set[int]] = {}
    for entry, row in functions.items():
        graph[entry] = {
            int(m.group(1), 16)
            for m in re.finditer(r"FUN_([0-9a-fA-F]{8})\(", row["decompiled_c"])
            if int(m.group(1), 16) != entry
        }
    return graph


def path_from(graph: dict[int, set[int]], root: int, target: int, max_depth: int = 7) -> list[int] | None:
    q = deque([(root, [root])])
    seen = {root}
    while q:
        node, path = q.popleft()
        if len(path) > max_depth:
            continue
        for nxt in graph.get(node, set()):
            if nxt == target:
                return path + [nxt]
            if nxt in graph and nxt not in seen:
                seen.add(nxt)
                q.append((nxt, path + [nxt]))
    return None


def refs(census: dict, *term_names: str) -> set[int]:
    out: set[int] = set()
    for name in term_names:
        for row in census["terms"][name]["matches"]:
            out.add(int(row["entry"], 16))
    return out


def writes_for_term(census: dict, name: str) -> list[dict]:
    row = census["terms"][name]
    needle = row["substring"].lower()
    out = []
    for match in row["matches"]:
        for line in match["matching_lines"]:
            low = line.lower()
            pos = low.find(needle)
            eq = line.find("=")
            if eq >= 0 and pos >= 0 and pos < eq:
                out.append({"entry": match["entry"], "line": line})
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sienna", type=Path, default=REPO / "firmware/RH850_P1M-E_CodeFlash.bin")
    p.add_argument("--target", type=Path, default=REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin")
    p.add_argument("--function-evidence", type=Path, default=REPO / "data/generated/corolla_8965H1202000_fd_control_decompiler_evidence.json")
    p.add_argument("--reference-census", type=Path, default=REPO / "data/generated/corolla_8965H1202000_fd_control_reference_census.json")
    p.add_argument("--state-bridge-evidence", type=Path, default=STATE_EVIDENCE)
    p.add_argument("--structural", type=Path, default=REPO / "data/generated/corolla_8965H1202000_structural_function_transfer.json")
    p.add_argument("--out", type=Path, default=REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json")
    args = p.parse_args()

    s = load_codeflash(args.sienna)
    h = load_codeflash(args.target)
    fmeta, funcs = validate_function_evidence(args.function_evidence, h)
    smeta, state_funcs = validate_function_evidence(args.state_bridge_evidence, h)
    if smeta["schema"] != "corolla-h-openpilot-state-bridge-decompiler-evidence-v2":
        raise ValueError("state-bridge evidence schema drift")
    census = validate_reference_census(args.reference_census, h)
    structural = json.loads(args.structural.read_text())
    target_angle = json.loads(TARGET_ANGLE.read_text())
    if target_angle["sources"]["codeflash"]["sha256"] != sha256(h): raise ValueError("B6 target-angle artifact image drift")
    graph = call_graph(funcs)

    # ---- FD receive descriptor boundary ----
    from tools.compare_variant_application_rx import find_normal_rx_descriptor_table
    srx_base, srx = find_normal_rx_descriptor_table(s)
    hrx_base, hrx = find_normal_rx_descriptor_table(h)
    s_fd = [(row[0] & 0x7FF, row[1]) for row in srx if row[0] & 0x40000000]
    h_fd = [(row[0] & 0x7FF, row[1]) for row in hrx if row[0] & 0x40000000]
    if s_fd != [(0x25, 32), (0x90, 32), (0xD7, 32)]:
        raise ValueError(f"unexpected Sienna FD Rx set: {s_fd}")
    if h_fd != [(0x25, 32), (0x90, 32), (0xD7, 32), (0xB6, 32)]:
        raise ValueError(f"unexpected H FD Rx set: {h_fd}")

    # ---- shared FD025 boundary ----
    unique_shapes = {
        (int(row["reference_entry"], 16), int(row["target_entry"], 16)): row
        for row in structural["matches"]
    }
    for pair in ((0x4AD82, 0x4636A), (0x4B7BA, 0x46D9A), (0x4BB1E, 0x4749A)):
        if pair not in unique_shapes:
            raise ValueError(f"missing unique complete-shape transfer for {pair}")
    c025 = funcs[0x4636A]["decompiled_c"]
    need(c025,
         "FUN_0007643a(0xb8,0x11f,0xc,0,1,0xfebe7d34);",
         "FUN_0007643a(0xba,0x123,0xc,0,1,iVar2 + -0x3aca);")
    c4a3_prod = funcs[0x46D9A]["decompiled_c"]
    need(c4a3_prod,
         "uRamfebe7ddd = (undefined1)uRamfebe7d34;",
         "bRamfebe7ddc = (byte)((ushort)uRamfebe7d34 >> 8) & 0xf;")
    c4a3_pack = funcs[0x4749A]["decompiled_c"]
    need(c4a3_pack,
         "FUN_0007662e(0x2c,0x28,8,0,iVar2 + -0x2f09);",
         "FUN_0007662e(0x2d,0x29,8,0,iVar2 + -0x2f08);")

    # ---- H B6 exact scalar extraction/staging/snapshot ----
    cb6 = funcs[0x46A10]["decompiled_c"]
    expected_b6 = [
        # signal, COM offset, bits, bitoff, signed, raw, stage, snapshot, class, consumers
        (254, 0x1AA, 6, 0, 0, 0xFEBE7D96, 0xFEBEF127, 0xFEBEADB0, "target-lateral-control-id-mode-selector", [0xCBE6E]),
        (255, 0x1AB, 16, 0, 1, 0xFEBE7D94, 0xFEBEF1CC, 0xFEBEAE82, "signed16-target-steering-angle-command", [0xC86E8, 0xC87FC, 0xC9DB0, 0xCB4F4]),
        (256, 0x1AD, 1, 7, 0, 0xFEBE7DA2, 0xFEBEF147, 0xFEBEADDD, "snapshot-only-direct-xref-negative", []),
        (257, 0x1AD, 3, 4, 0, 0xFEBE7D97, 0xFEBEF128, 0xFEBEADB1, "snapshot-only-direct-xref-negative", []),
        (258, 0x1AD, 1, 2, 0, 0xFEBE7D98, 0xFEBEF129, 0xFEBEADBB, "steering-cone-gate", [0xCBEEE]),
        (259, 0x1AD, 2, 0, 0, 0xFEBE7D99, 0xFEBEF12A, None, "staged-only-direct-xref-negative", []),
        (260, 0x1AE, 2, 6, 0, 0xFEBE7D9A, 0xFEBEF12B, 0xFEBEADC2, "mode-table-selector", [0xC89D2, 0xC8D42]),
        (261, 0x1AE, 6, 0, 0, 0xFEBE7D9B, 0xFEBEF12C, 0xFEBEADBC, "modulo-sequence-delta", [0xCB246]),
        (262, 0x1AF, 8, 0, 0, 0xFEBE7D9C, 0xFEBEF12D, 0xFEBEADBD, "percentage-scaling", [0xCC442]),
        (263, 0x1B0, 8, 0, 0, 0xFEBE7D9D, 0xFEBEF12E, 0xFEBEADBE, "percentage-scaling", [0xCBFCE]),
        (264, 0x1B1, 1, 7, 0, 0xFEBE7D9E, 0xFEBEF12F, 0xFEBEADC1, "validity-reset-gate", [0xC819E]),
        (265, 0x1B1, 3, 0, 0, 0xFEBE7DA1, 0xFEBEF141, 0xFEBEADD9, "validity-gated-mode-status", [0xCCF58]),
    ]
    b6_buffer_base = struct.unpack_from("<H", h, 0x22788 + 42 * 2)[0]
    if b6_buffer_base != 0x1A7:
        raise ValueError(f"unexpected H B6 PDU buffer offset: {b6_buffer_base:#x}")
    b6_rows = []
    for sig, com_off, bits, bitoff, signed, raw, stage, snap, role, consumers in expected_b6:
        sig_text = f"0x{sig:x}" if sig >= 10 else str(sig)
        off_text = f"0x{com_off:x}"
        bits_text = f"0x{bits:x}" if bits >= 10 else str(bits)
        call_re = re.compile(
            rf"FUN_0007643a\({re.escape(sig_text)},{re.escape(off_text)},{re.escape(bits_text)},{bitoff},{signed},"
        )
        if not call_re.search(cb6):
            raise ValueError(f"B6 extraction call drifted for signal {sig}")
        # The compact direct-reference census bounds dead/staged-only claims.
        stage_name = f"b6_sig{sig}_stage_abs"
        stage_refs = refs(census, stage_name)
        if role.startswith("staged-only") and stage_refs != {0x5262C}:
            raise ValueError(f"B6 signal {sig} gained direct stage consumers: {stage_refs}")
        if sig == 254:
            mode = target_angle["mode_ingress"]
            if mode["snapshot_destination"] != "0xFEBEADB0" or mode["decoder"] != "0x000CBE6E":
                raise ValueError("B6 signal254 mode-ID join drift")
        if sig == 255:
            ta = target_angle["wire_ingress"]
            if ta["snapshot_destination"] != "0xFEBEAE82" or ta["classification"] != "authenticated-signed16-target-steering-angle-command":
                raise ValueError("B6 signal255 target-angle join drift")
        if role.startswith("snapshot-only"):
            rel_name = f"b6_sig{sig}_snapshot"
            abs_name = f"b6_sig{sig}_snapshot_abs"
            direct = refs(census, rel_name, abs_name)
            if direct - {0xB8EE4, 0xBBFE6}:
                raise ValueError(f"B6 signal {sig} gained direct snapshot consumers: {direct}")
        paths = {}
        for consumer in consumers:
            path = path_from(graph, 0xCEDAE, consumer)
            paths[f"0x{consumer:X}"] = None if path is None else [f"0x{x:X}" for x in path]
        b6_rows.append({
            "signal_id": sig,
            "wire_byte": com_off - b6_buffer_base,
            "bit_length": bits,
            "bit_offset": bitoff,
            "signed": bool(signed),
            "raw_destination": f"0x{raw:08X}",
            "staging_destination": f"0x{stage:08X}",
            "snapshot_destination": None if snap is None else f"0x{snap:08X}",
            "role": role,
            "direct_consumers": [f"0x{x:X}" for x in consumers],
            "paths_from_0xCEDAE": paths,
        })

    # Pin semantic roles to the target-native consumers rather than names transferred from Sienna.
    need(funcs[0xCBEEE]["decompiled_c"], "cRamfebeadbb != '\\x01'")
    need(funcs[0xC89D2]["decompiled_c"], "cRamfebeadc2 == '\\x01' || cRamfebeadc2 == '\\x02'")
    need(funcs[0xCB246]["decompiled_c"], "bRamfebeadbc - uRamfebec248")
    need(funcs[0xCC442]["decompiled_c"], "uVar1 = (uint)bRamfebeadbd;", "/ 100")
    need(funcs[0xCBFCE]["decompiled_c"], "uVar12 = (uint)bRamfebeadbe;", "/ 100")
    need(funcs[0xC819E]["decompiled_c"], "cRamfebeadc1")
    need(funcs[0xCCF58]["decompiled_c"], "-0xa27", "-0xa47")

    # ---- old Sienna-shaped torque/status branches on H ----
    cstage = funcs[0x5262C]["decompiled_c"]
    csnap = funcs[0xB8EE4]["decompiled_c"]
    need(cstage, "uRamfebef156 = uRamfebe6d7a;", "uRamfebef166 = 0;")
    need(csnap,
         "-0x9e0) = *(undefined2 *)(", "0x3956);",
         "0x3966),0x100,100,&uStack_34")
    need(funcs[0x35526]["decompiled_c"], "-0x4a86) =")
    need(funcs[0xC80C4]["decompiled_c"], "sRamfebeae20")
    need(funcs[0xC91B6]["decompiled_c"], "iVar8 = (int)sRamfebeae12;")
    need(funcs[0xCF12A]["decompiled_c"], "iVar1 = (int)((int)param_1 * (param_2 & 0xffff))", "*param_4 = param_1;")
    clamp_stage_writers = refs(census, "dormant_clamp_input_stage_abs", "dormant_clamp_input_stage_gp")
    if clamp_stage_writers != {0x5262C, 0x5389C, 0xB8EE4}:
        raise ValueError(f"unexpected direct references to FEBEF166/GP+3966: {clamp_stage_writers}")
    if "0x3966) = 0;" not in funcs[0x5389C]["decompiled_c"]:
        raise ValueError("second H clamp-input zero writer drifted")

    # ---- FD030 transmit generation ----
    s_tx = [TX.unpack_from(s, 0x21F78 + TX.size * i)[0] for i in range(6)]
    h_tx = [TX.unpack_from(h, 0x21F04 + TX.size * i)[0] for i in range(5)]
    if s_tx != [0x260, 0x262, 0x351, 0x394, 0x4A3, 0x4C8]:
        raise ValueError(f"unexpected Sienna COM Tx IDs: {s_tx}")
    if [(x & 0x7FF, bool(x & 0x40000000)) for x in h_tx] != [
        (0x30, True), (0x351, False), (0x394, False), (0x4A3, False), (0x4C8, False)
    ]:
        raise ValueError(f"unexpected H COM Tx IDs: {h_tx}")
    h_pdu0 = PDU.unpack_from(h, 0x22620)
    if h_pdu0 != (2, 0, 0, 32, 0, 3):
        raise ValueError(f"unexpected H PDU0 descriptor: {h_pdu0}")
    signal_map = [struct.unpack_from("<H", h, 0x223FC + 2 * i)[0] for i in range(274)]
    pdu0_ids = [i for i, pdu in enumerate(signal_map) if pdu == 0]
    if pdu0_ids != list(range(37)):
        raise ValueError(f"unexpected H PDU0 signal allocation: {pdu0_ids}")

    c030 = funcs[0x4766A]["decompiled_c"]
    copy_map = {
        int(dst, 16): int(src, 16)
        for dst, src in re.findall(r"uRam([0-9a-f]{8})\s*=\s*uRam([0-9a-f]{8});", c030)
    }
    pack_re = re.compile(r"FUN_0007662e\((0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),([^;]+)\);")
    calls = []
    for m in pack_re.finditer(c030):
        sig, byteoff, bits, bitoff = (int(m.group(i), 0) for i in range(1, 5))
        ptr = m.group(5)
        temp = None
        ma = re.search(r"0x(febe[0-9a-f]{4})", ptr)
        if ma:
            temp = int(ma.group(1), 16)
        mr = re.search(r"iVar3 \+ (-0x[0-9a-f]+)", ptr)
        if mr:
            temp = (GP + int(mr.group(1), 0)) & 0xFFFFFFFF
        source = copy_map.get(temp)
        calls.append((sig, byteoff, bits, bitoff, temp, source))
    if sorted(row[0] for row in calls) != list(range(35)):
        raise ValueError(f"H FD030 direct pack-call IDs are not exactly 0..34: {[x[0] for x in calls]}")
    calls.sort(key=lambda row: row[0])
    need(c030, "FUN_0007636c(0,acStack_28);", "while (uVar2 < 7);", "cVar5 + '8'", "FUN_0007662e(9,7,8,0")

    # The original direct textual-reference census missed GP-relative stores in
    # 0x47188/0x47430. Pin those functions from the independent compact steering
    # bridge evidence and explicitly recover all eleven affected PDU0 sources.
    # These are positive writer proofs, not a broader claim that arbitrary
    # computed-pointer writes cannot exist elsewhere.
    c47188 = state_funcs[0x47188]["decompiled_c"]
    c47430 = state_funcs[0x47430]["decompiled_c"]
    need(c47188,
         "*(undefined1 *)(iVar5 + -0x39fa) = auStack_11[0];",
         "*(bool *)(iVar5 + -0x39f9) = bVar1;",
         "*(char *)(iVar5 + -0x39f6) = (char)((iVar8 - iVar4) / 10);",
         "*(bool *)(iVar5 + -0x39f4) = bVar1;",
         "*(undefined1 *)(iVar5 + -0x39f2) = uVar6;",
         "*(undefined1 *)(iVar5 + -0x39f1) = *(undefined1 *)(iVar5 + -0x45c3);",
         "*(undefined1 *)(iVar5 + -0x39f0) = *(undefined1 *)(iVar5 + -0x3a49);",
         "*(undefined1 *)(iVar5 + -0x39ef) = *(undefined1 *)(iVar5 + -0x3a4a);",
         "*(char *)(iVar5 + -0x39ee) = (char)iVar4;",
         "*(short *)(iVar5 + -0x39c4) =")
    need(c47430, "*(undefined1 *)(iVar2 + -0x39b4) = uVar1;")

    gp_relative_writers = {
        0xFEBE7E06: (0x47188, "coarse signed driver-steering-torque encoding: saturating signed byte of trunc(native torque intermediate / 10)"),
        0xFEBE7E07: (0x47188, "runtime boolean copied from FEBE6497 != 0; exact OEM meaning unresolved"),
        0xFEBE7E0A: (0x47188, "second coarse driver-steering-torque encoding derived from the same native torque intermediate and decimal remainder"),
        0xFEBE7E0C: (0x47188, "mirror of the FEBE6497-derived runtime boolean used by signal 1"),
        0xFEBE7E0E: (0x47188, "runtime status derived from FEBE7D3C with local transition/debounce handling; exact OEM meaning unresolved"),
        0xFEBE7E0F: (0x47188, "runtime status copied from FEBE723D; exact OEM meaning unresolved"),
        0xFEBE7E4C: (0x47430, "2-bit internal status code produced by the 0x472F6/0x47334/0x47348/0x473DE decision family"),
        0xFEBE7E10: (0x47188, "runtime status copied from FEBE7DB7; exact OEM meaning unresolved"),
        0xFEBE7E11: (0x47188, "runtime status copied from FEBE7DB6; exact OEM meaning unresolved"),
        0xFEBE7E12: (0x47188, "signed decimal remainder/units nibble for the same native driver-steering-torque intermediate used by signals 0 and 10"),
        0xFEBE7E3C: (0x47188, "signed16 calibrated derivative of sign-inverted FEBE6592 Motor Actual Current (Q Axis); exact packet physical scale remains calibration-dependent"),
    }
    expected_gp_corrected_signals = {0, 1, 10, 14, 16, 17, 18, 27, 28, 31, 34}
    actual_gp_corrected_signals = {sig for sig, _, _, _, _, source in calls if source in gp_relative_writers}
    if actual_gp_corrected_signals != expected_gp_corrected_signals:
        raise ValueError(f"0x030 GP-relative writer set drift: {sorted(actual_gp_corrected_signals)}")

    tx030_rows = []
    for sig, byteoff, bits, bitoff, temp, source in calls:
        if sig == 9:
            writer_class = "computed-first-seven-byte-additive-field-plus-0x38"
            writers = ["0x4766A"]
            source_text = None
        else:
            name = f"tx030_sig{sig:02d}_source"
            writers_raw = writes_for_term(census, name)
            dynamic = [row for row in writers_raw if int(row["entry"], 16) != 0x5316C]
            source_text = None if source is None else f"0x{source:08X}"
            gp_writer = gp_relative_writers.get(source)
            if gp_writer is not None:
                writer_class = "runtime-produced-gp-relative"
                writers = [f"0x{gp_writer[0]:08X}"]
                semantic = gp_writer[1]
            elif not dynamic:
                writer_class = "default-init-only-direct-writer-census"
                writers = []
                semantic = None
            elif all(re.search(r"=\s*0;", row["line"]) for row in dynamic):
                writer_class = "runtime-constant-zero-direct-writer-census"
                writers = sorted({row["entry"] for row in dynamic})
                semantic = None
            else:
                writer_class = "runtime-produced"
                writers = sorted({row["entry"] for row in dynamic})
                semantic = None
        tx030_rows.append({
            "signal_id": sig,
            "wire_byte": byteoff,
            "bit_length": bits,
            "bit_offset": bitoff,
            "source": source_text,
            "writer_class": writer_class,
            "nondefault_writer_functions": writers,
            "recovered_semantic": semantic if sig != 9 else None,
        })

    # ---- final report ----
    report = {
        "schema": "corolla-8965H1202000-fd-control-interface-v2",
        "evidence_boundary": (
            "Raw generated CAN/PDU/signal configuration is exact-image byte evidence. Consumer roles are target-native decompiler recovery. "
            "Negative no-consumer/no-writer statements remain bounded to the direct textual-reference census, while B6 signals254/255 are explicitly corrected by the exact fixed-map GP-relative audit in the canonical target-angle ingress artifact."
        ),
        "images": {
            "sienna_sha256": sha256(s),
            "corolla_h_sha256": sha256(h),
        },
        "fd_receive_generation": {
            "sienna_normal_rx_table": f"0x{srx_base:X}",
            "corolla_h_normal_rx_table": f"0x{hrx_base:X}",
            "sienna_fd_rx": [{"can_id": f"0x{x:03X}", "length": n} for x, n in s_fd],
            "corolla_h_fd_rx": [{"can_id": f"0x{x:03X}", "length": n} for x, n in h_fd],
            "h_only_fd_rx": ["0x0B6"],
            "shared_0x025_boundary": {
                "classification": "shared-preexisting-fd-interface-not-h-replacement",
                "unique_instruction_shape_pairs": [
                    {"sienna": "0x4AD82", "corolla_h": "0x4636A", "role": "FD025 generated unpacker"},
                    {"sienna": "0x4B7BA", "corolla_h": "0x46D9A", "role": "FD025-to-4A3 producer"},
                    {"sienna": "0x4BB1E", "corolla_h": "0x4749A", "role": "CAN 0x4A3 packer"},
                ],
                "corolla_h_signed12_signal_184": {
                    "raw_destination": "0xFEBE7D34",
                    "corresponds_by_generated-shape_to_sienna_signal": 221,
                    "directly_repacked_to_can_0x4A3_bytes": [1, 2],
                },
            },
        },
        "secured_fd_0x0b6": {
            "pdu_id": 42,
            "buffer_offset": f"0x{b6_buffer_base:X}",
            "configured_signal_ids": list(range(252, 268)),
            "scalar_extracted_signal_ids": list(range(254, 266)),
            "configured_without_recovered_scalar_extract": [252, 253, 266, 267],
            "fields": b6_rows,
            "validity": {
                "staging_destination": "0xFEBEF132",
                "snapshot_destination": "0xFEBEADB9",
                "direct_consumers": ["0xC7C70", "0xC819E", "0xCC7F8", "0xCCF58"],
                "role": "control/status validity gating",
            },
            "signed16_target_angle_command": {
                "signal_id": 255,
                "snapshot_destination": "0xFEBEAE82",
                "classification": "authenticated target-steering-angle command; not torque",
                "canonical_proof": str(TARGET_ANGLE.relative_to(REPO)),
                "physical_scale_closed": target_angle["scaling"]["physical_degree_scale_closed"],
                "controller_equivalent_deg_per_count": target_angle["scaling"]["controller_equivalent_deg_per_b6_count"],
                "controller_equivalent_mrad_per_count": target_angle["scaling"]["controller_equivalent_mrad_per_b6_count"],
                "oem_wire_unit_name_closed": target_angle["scaling"]["oem_wire_unit_name_closed"],
            },
        },
        "sienna_shaped_branch_corrections": {
            "old_2e4_monitor_branch": {
                "h_chain": ["0x35526 -> FEBE6D7A", "0x5262C -> FEBEF156", "0xB8EE4 -> FEBEAE20", "0xC80C4 plausibility/status predicate"],
                "classification": "internal-controller-output-fed monitor/status branch; not the H clamp/rate command input",
            },
            "retained_torque_clamp_branch": {
                "clamp_function": "0xC91B6",
                "input": "0xFEBEAE12",
                "upstream_staging": "0xFEBEF166",
                "direct_writer_census": ["0x5262C writes zero", "0x5389C writes zero"],
                "scale_helper": "0xCF12A maps zero input to zero for the fixed 0x100/100 call",
                "classification": "retained framework branch with zero source in this calibration under the recovered direct-writer census",
            },
        },
        "fd_0x030_transmit": {
            "classification": "H-generation replacement/consolidation for Sienna 0x260/0x262 transmit slots; field-for-field equivalence not claimed",
            "sienna_tx_ids": [f"0x{x:03X}" for x in s_tx],
            "corolla_h_tx_ids": [f"0x{x & 0x7FF:03X}" for x in h_tx],
            "pdu0_descriptor": {"cycle_or_timeout": h_pdu0[0], "length": h_pdu0[3], "flags": h_pdu0[5]},
            "configured_signal_ids": pdu0_ids,
            "direct_packer_signal_ids": [row[0] for row in calls],
            "configured_without_recovered_direct_pack_call": [35, 36],
            "checksum_like_signal_9": {
                "wire_byte": 7,
                "formula": "sum(payload_bytes_0_through_6) + 0x38, low byte",
                "boundary": "recovered exact code behavior; OEM checksum naming/formula lineage is not inferred from the constant alone",
            },
            "fields": tx030_rows,
            "gp_relative_writer_correction": {
                "affected_signal_ids": sorted(expected_gp_corrected_signals),
                "affected_source_addresses": [f"0x{x:08X}" for x in sorted(gp_relative_writers)],
                "writer_functions": ["0x00047188", "0x00047430"],
                "correction": "Eleven fields previously classified as default-init-only by the direct textual-reference census have exact runtime GP-relative writers. The positive writers are now pinned from independent exact-image compact decompiler evidence.",
                "boundary": "This correction closes these eleven specific false negatives; it does not upgrade the direct-reference census into a complete arbitrary computed-pointer writer proof.",
            },
        },
        "evidence": {
            "function_evidence_sha256": sha256(args.function_evidence.read_bytes()),
            "function_count": fmeta["function_count"],
            "state_bridge_evidence_sha256": sha256(args.state_bridge_evidence.read_bytes()),
            "state_bridge_function_count": smeta["function_count"],
            "b6_target_angle_ingress_sha256": sha256(TARGET_ANGLE.read_bytes()),
            "reference_census_sha256": sha256(args.reference_census.read_bytes()),
            "reference_term_count": len(census["terms"]),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "out": str(args.out),
        "fd_rx_h": h_fd,
        "b6_scalar_fields": len(b6_rows),
        "tx030_direct_packer_signals": len(calls),
    }, indent=2))


if __name__ == "__main__":
    main()
