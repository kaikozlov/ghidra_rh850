#!/usr/bin/env python3
"""Build the static 8965H1202000 SecOC key-selector/provisioning provenance report.

The report deliberately separates facts about the *protected ICU-S slot selector*
from facts about raw AES-key bytes. It proves what the CPU/application passes to
command 7 and command 8; it does not claim visibility into undocumented ICU-S
internal storage/derivation beyond those interfaces.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
H_CONFIG = bytes.fromhex("0100000004000000000000000000000000000000")
H_RECORD_BASE = 0x2572C
H_RECORD_COUNT = 3
S_CONFIG_BASE = 0x25950
H_CONFIG_BASE = 0x2570C
H_KAT_CONFIG_BASE = 0x215B0
H_KAT_GATE = 0x2CA9F


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
        raise ValueError("decompiler evidence is bound to a different image")
    rows = {}
    for row in doc["functions"]:
        entry = int(row["entry"], 16)
        body = image[entry : entry + row["body_size"]]
        if sha256(body) != row["body_sha256"]:
            raise ValueError(f"raw body mismatch at {entry:#x}")
        code = row["decompiled_c"]
        if sha256(code.encode()) != row["decompiled_c_sha256"]:
            raise ValueError(f"decompiled C mismatch at {entry:#x}")
        rows[entry] = row
    return doc, rows


def need(code: str, *needles: str) -> None:
    for needle in needles:
        if needle not in code:
            raise ValueError(f"semantic pin missing: {needle!r}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sienna", type=Path, default=REPO / "firmware/RH850_P1M-E_CodeFlash.bin")
    ap.add_argument("--target", type=Path, default=REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin")
    ap.add_argument("--evidence", type=Path, default=REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance_decompiler_evidence.json")
    ap.add_argument("--dataflash-analysis", type=Path, default=REPO / "data/generated/corolla_2023_albino_dataflash_analysis.json")
    ap.add_argument("--out", type=Path, default=REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json")
    args = ap.parse_args()

    s = load_codeflash(args.sienna)
    h = load_codeflash(args.target)
    emeta, f = validate_function_evidence(args.evidence, h)
    df = json.loads(args.dataflash_analysis.read_text())

    # Static config object must be the same generated {type=1, selector=4} object.
    if h[H_CONFIG_BASE:H_CONFIG_BASE + 20] != H_CONFIG:
        raise ValueError("H SecOC config object is not {type=1, selector=4}")
    if s[S_CONFIG_BASE:S_CONFIG_BASE + 20] != H_CONFIG:
        raise ValueError("Sienna SecOC config object differs from H slot-4 config")
    if h[H_KAT_CONFIG_BASE:H_KAT_CONFIG_BASE + 20] != H_CONFIG:
        raise ValueError("H disabled KAT does not use the same slot-4 config")
    if h[H_KAT_GATE] != 0:
        raise ValueError("H slot-4 KAT compile gate unexpectedly enabled")

    records = []
    for i in range(H_RECORD_COUNT):
        off = H_RECORD_BASE + i * 0x50
        can_id = struct.unpack_from("<H", h, off + 0x0A)[0]
        profile_word = struct.unpack_from("<I", h, off + 0x10)[0]
        config_id = struct.unpack_from("<H", h, off + 0x16)[0]
        crypto_job_handle = struct.unpack_from("<H", h, off + 0x20)[0]
        pdu_id = struct.unpack_from("<H", h, off + 0x34)[0]
        secured_length = struct.unpack_from("<I", h, off + 0x3C)[0]
        records.append({
            "index": i,
            "address": f"0x{off:X}",
            "can_id": f"0x{can_id:03X}",
            "profile_word_0x10": f"0x{profile_word:08X}",
            "secoc_crypto_config_id": config_id,
            "cryptoif_job_handle": crypto_job_handle,
            "application_pdu_id": pdu_id,
            "secured_length": secured_length,
        })
    if [row["can_id"] for row in records] != ["0x00F", "0x0D7", "0x0B6"]:
        raise ValueError(f"unexpected H SecOC queue records: {records}")
    if any(row["secoc_crypto_config_id"] != 0 or row["cryptoif_job_handle"] != 0 for row in records):
        raise ValueError("H SecOC profiles do not all select config/job 0")

    # H startup/config path.
    c_init = f[0x88024]["decompiled_c"]
    c_set = f[0x88458]["decompiled_c"]
    c_get = f[0x884AA]["decompiled_c"]
    c_worker = f[0x88A56]["decompiled_c"]
    need(c_init, "FUN_00088458(0", "0x19a0")
    need(c_set,
         "if ((param_1 == 0) && (*param_2 - 1U < 0x10))",
         "*(int *)(iVar1 + -0x6410) = *param_2",
         "FUN_0008323e(iVar1 + -0x640c,param_2 + 1,0x10)")
    need(c_get,
         "if (param_1 == 0)",
         "*param_2 = *(undefined4 *)(iVar1 + -0x6410)",
         "FUN_0008323e(param_2 + 1,iVar1 + -0x640c,0x10)")
    need(c_worker,
         "FUN_000884aa(*(undefined2 *)(iVar8 + 0x25742),auStack_48)",
         "FUN_00088986(*(undefined2 *)(iVar8 + 0x2574c),auStack_48)")

    # CryptoIf forwarding path: begin stores config pointer, finish forwards it
    # through generic dispatch, then command-7 prepare extracts byte +4.
    c_begin = f[0x82F6A]["decompiled_c"]
    c_finish = f[0x82FA8]["decompiled_c"]
    c_dispatch = f[0x82956]["decompiled_c"]
    c_prepare7 = f[0x822D0]["decompiled_c"]
    c_cmd7 = f[0x83BF4]["decompiled_c"]
    need(c_begin,
         "if (abStack_9[0] == 1)",
         "*(undefined4 *)(iVar1 + 0x5a74) = param_2")
    need(c_finish,
         "FUN_00082956(param_1,uRamfebf1274",
         "param_2,param_3,param_4)")
    need(c_dispatch,
         "uVar5 = FUN_00082908(param_1)",
         "(*pcVar6)(uVar3,param_2,param_3,param_4,param_5,param_6,param_7)")
    need(c_prepare7,
         "param_6 == 0 || (*param_1 != 1)",
         "*(uint *)(iVar1 + 0x5974) = (uint)*(byte *)(param_1 + 1)",
         "*(int *)(iVar1 + 0x595c) = iVar1 + 0x5964")
    need(c_cmd7,
         "puVar2[4] < 0xf",
         "Ramffc5d004 = puVar2[3]",
         "Ramffc5d000 = puVar2[4] << 0x10 | 7")

    # Disabled KAT corroboration uses exact same config and job 0.
    c_kat = f[0x62430]["decompiled_c"]
    need(c_kat, "if (DAT_0002ca9f == 'Z')", "FUN_00082f6a(0,0x215b0)")

    # Command-8 update path: exact 64-byte M1/M2/M3-shaped package is staged as
    # 16+32+16 and handed to ICUSCMD=8. No fixed slot selector appears in this
    # CPU-side descriptor; target/key identity is inside the authenticated package.
    c_prepare8 = f[0x81262]["decompiled_c"]
    c_cmd8 = f[0x83D7A]["decompiled_c"]
    c_submit8 = f[0x62574]["decompiled_c"]
    need(c_prepare8,
         "param_2 != 0x40",
         "FUN_0008323e(0xfebf0fc0,param_1,0x10)",
         "FUN_0008323e(&DAT_febf0fd0,param_1 + 0x10,0x20)",
         "FUN_0008323e(0xfebf0ff0,param_1 + 0x30,0x10)")
    need(c_cmd8, "Ramffc5d000 = 8")
    need(c_submit8, "FUN_00082d36(0", "0x40", "0x30")

    scan = df["key_domain_scan"]
    if scan["candidates_tested"] != 23277:
        raise ValueError("DataFlash raw-window scan denominator drifted")
    if scan["matches"]:
        raise ValueError("unexpected DataFlash raw-key candidate match")

    payload = {
        "schema": "corolla-8965H1202000-secoc-key-provenance-v1",
        "evidence_boundary": (
            "Static CPU/application proof: all configured H SecOC queue records select one generated config/job, whose config is {type=1, selector=4}; CryptoIf forwards that object into the command-7 descriptor and ICUSCMD receives selector 4. No 16-byte raw key is passed through the command-7 CPU descriptor. This does not reveal undocumented ICU-S internal storage/derivation. DataFlash raw-key negatives retain their acquisition-epoch boundary."
        ),
        "images": {
            "sienna_sha256": sha256(s),
            "corolla_h_sha256": sha256(h),
        },
        "secoc_records": records,
        "shared_crypto_selection": {
            "secoc_crypto_config_id": 0,
            "cryptoif_job_handle": 0,
            "config_object_address": f"0x{H_CONFIG_BASE:X}",
            "config_bytes": H_CONFIG.hex(),
            "config_type": 1,
            "icus_slot_selector": 4,
            "same_bytes_as_sienna": True,
            "sienna_config_address": f"0x{S_CONFIG_BASE:X}",
            "conclusion": "00F, 0D7, and 0B6 share one ICU-S slot-4 authentication key selection; the firmware does not select three independent keys for these profiles",
        },
        "command7_cpu_to_icus_path": {
            "secoc_rx_init": "0x88024",
            "config_set": "0x88458",
            "config_get": "0x884AA",
            "verify_worker": "0x88A56",
            "cmac_submit": "0x88986",
            "cryptoif_begin": "0x82F6A",
            "cryptoif_finish": "0x82FA8",
            "crypto_driver_dispatch": "0x82956",
            "icus_command7_prepare": "0x822D0",
            "icus_command7": "0x83BF4",
            "selector_flow": [
                "CodeFlash[0x2570C] config0 = type1 + selector4 + zero padding",
                "secoc_rx_init installs config0",
                "every H queue record references config0 and CryptoIf job0",
                "CryptoIf begin stores the config pointer and finish forwards it through driver dispatch",
                "command7 prepare copies config byte +4 into descriptor word4",
                "command7 validates descriptor word4 < 15 and writes (word4 << 16) | 7 to ICUSCMD",
            ],
            "raw_key_bytes_in_cpu_command_descriptor": False,
        },
        "slot4_kat": {
            "config_address": f"0x{H_KAT_CONFIG_BASE:X}",
            "config_bytes": H_CONFIG.hex(),
            "compile_gate_address": f"0x{H_KAT_GATE:X}",
            "compile_gate_value": h[H_KAT_GATE],
            "enabled": False,
            "meaning": "disabled known-answer path independently corroborates job0/config type1/slot4 but places no constraint on the live slot-4 key value",
        },
        "command8_key_update": {
            "configured_submit_worker": "0x62574",
            "prepare": "0x81262",
            "driver": "0x83D7A",
            "request_length": 64,
            "staging_shape": [16, 32, 16],
            "success_output_length": 48,
            "icus_command": 8,
            "fixed_cpu_side_target_slot_selector": None,
            "conclusion": "the CPU forwards the authenticated 64-byte key-update package to ICU-S command 8; no fixed slot is selected by the CPU-side command descriptor, so target/key identity remains package-authenticated rather than a raw application key write",
        },
        "dataflash_raw_key_negative": {
            "snapshot_sha256": df["dump_sha256"],
            "candidates_tested": scan["candidates_tested"],
            "matches": scan["matches"],
            "min_entropy": scan["min_entropy"],
            "capture_summary": df["capture"]["summary"],
            "boundary": "The DataFlash dump and retained CAN oracle are contributor artifacts and are not proven same-runtime-epoch. The scan excludes an exact raw 16-byte candidate among the 23,277 tested windows; it does not exclude transformed/derived values or ICU-S-internal storage.",
            "interpretation": "the committed exhaustive raw-window scan found zero candidate matches; this supports absence of an obvious CPU-visible raw key in the supplied DataFlash snapshot, not absence of derivation or protected hardware storage",
        },
        "static_storage_derivation_conclusion": {
            "mapped_secoc_init_raw_key_load_found": False,
            "mapped_secoc_init_key_derivation_found": False,
            "cpu_visible_slot4_selector": True,
            "cpu_visible_raw_slot4_key": False,
            "provisioning_interface_found": True,
            "best_static_model": "mapped application SecOC init selects protected ICU-S slot 4; key value is opaque to command-7 CPU software and can be refreshed through authenticated ICU-S command-8 package handling",
        },
        "decompiler_evidence": {
            "path": str(args.evidence.relative_to(REPO)) if args.evidence.resolve().is_relative_to(REPO.resolve()) else str(args.evidence),
            "sha256": sha256(args.evidence.read_bytes()),
            "function_count": emeta["function_count"],
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "out": str(args.out),
        "profiles": [row["can_id"] for row in records],
        "shared_slot": 4,
        "dataflash_raw_matches": len(payload["dataflash_raw_key_negative"]["matches"]),
    }, indent=2))


if __name__ == "__main__":
    main()
