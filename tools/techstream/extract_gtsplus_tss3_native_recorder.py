#!/usr/bin/env python3
"""Extract current-release native TSS3 recorder acquisition semantics.

This joins the current unprotected GetTSS3OperationFFDP5 plugin with the
installer-recovered original CommandCommon/GetTSS3ImageFFDP5 bodies.  All durable
claims are pinned to exact PE identities, export-body hashes, direct-call edges,
and raw constant/code anchors; Ghidra decompilation is used only to understand
what those exact current bodies mean.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any

import pefile  # type: ignore

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recover_gtsplus_bodies import recover
from techstream_paths import resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/tss3_native_recorder_protocol.json"

IMAGE_EXPORTS = {
    "calculate_key_level49": "?CalculateKeyDataSecLv49@CCmdImgOpeDdr@@AAEXPBEQAE@Z",
    "image_info": "?GetTSS3ImageFFDInfo@CCmdImgOpeDdr@@QAEKPAUtagCOMMAND_DATA@@PAVCCommCachePlusP5@@PAVCCommFrameData@@PAUTSS3IMAGE_FFD_MEMORIZED_INFO@@PAUTSS3IMAGE_FFD_INFO_P5@@@Z",
    "image_spec": "?GetTSS3ImageFFDSpecInformation@CCmdImgOpeDdr@@QAEKPAUtagCOMMAND_DATA@@PAVCCommCachePlusP5@@PAVCCommFrameData@@@Z",
    "image_availability": "?GetTSS3ImageFFDFlagAndAvailability@CCmdImgOpeDdr@@AAEKPAUtagCOMMAND_DATA@@PAVCCommCachePlusP5@@PAVCCommFrameData@@@Z",
    "image_encryption": "?GetTSS3ImageFFDEncryotionMethod@CCmdImgOpeDdr@@AAEKPAUtagCOMMAND_DATA@@PAVCCommCachePlusP5@@PAVCCommFrameData@@@Z",
    "security_unlock": "?SecurityUnlock@CCmdImgOpeDdr@@AAEKPAUtagCOMMAND_DATA@@PAVCCommCachePlusP5@@PAVCCommFrameData@@@Z",
    "security_unlock_16": "?SecurityUnlock16Byte@CCmdImgOpeDdr@@AAEKPAUtagCOMMAND_DATA@@PAVCCommCachePlusP5@@PAVCCommFrameData@@@Z",
}

# Current GetTSS3OperationFFDP5_DT.dll has only Execute exported; these are
# current-body function boundaries recovered from its exact pinned image.  Body
# hashes plus immediate-byte anchors make address drift fail closed.
OPERATION_FUNCTIONS = {
    "enumerate_behaviors": (0x10001130, 0x10001340),
    "parse_eb13_blocks": (0x10001420, 0x10001910),
    "fetch_record": (0x100019F0, 0x10001CB0),
    "enumerate_records": (0x10001E40, 0x10002190),
    "selector_66": (0x10002D50, 0x10002DA0),
    "execute": (0x10002DA0, 0x10003190),
}

OPERATION_CODE_ANCHORS = {
    # mov byte [stack], AB/11 and EB/11
    "ab11_eb11": (0x100011DE, "c645a0ab508d4decc645ac11", 0x100011F2, "c645d0ebc645dc11"),
    "ab13_eb13": (0x10001AC7, "c6857cffffffab", 0x10001ADE, "c645aceb", 0x10001AE2, "c645b813"),
    "ab12_eb12": (0x10001F12, "c64588ab", 0x10001F16, "c6459412", 0x10001F32, "c645b8eb", 0x10001F36, "c645c412"),
    # push selector 0x66 before current CCommCachePlus::GetCommFrmInfo call
    "selector_66": (0x10002D73, "6a66"),
}


IMAGE_PLUGIN_FUNCTIONS = {
    "enumerate_rob_codes": (0x100027A0, 0x100029E0),
    "parse_eb33": (0x10002AA0, 0x10003120),
    "frame_selector_time_series": (0x10003200, 0x10003250),
    "frame_selector_occurrence": (0x10003250, 0x10003290),
    "fetch_record": (0x10003290, 0x10003550),
    "init_fetch_record": (0x100036B0, 0x10003710),
}

IMAGE_PLUGIN_CODE_ANCHORS = {
    "ab31_eb31": (
        0x10002863, "c6857cffffffab",
        0x1000286E, "c6458831",
        0x1000287A, "c645c4eb",
        0x1000287E, "c645d031",
    ),
    "ab33_eb33": (
        0x100033AD, "c68540ffffffab",
        0x100033B4, "c6854cffffff33",
        0x100033C9, "c64588eb",
        0x100033CD, "c6459433",
    ),
    "eb33_offsets": (
        0x10002B04, "bf08000000",
        0x10002B20, "8d5f01",
    ),
    "eb33_length_selector": (
        0x10002CE3, "8a5008b8000100000fafc80fb6c2baff0f00006603c80fb7c189856cffffff05",
    ),
    "ab33_payload_big_endian": (
        0x100033FC, "0fb74b108bc1884db88b4b148b9d34ffffffc1e8088845ac8bc1c1e8188845c48bc1c1e8108845d08bc1c1e8088845dc8d45a4884de8",
    ),
    "frame_selector_divisor": (
        0x10003207, "b800020000",
        0x10003257, "b800020000",
    ),
}

SPECIAL_BEHAVIOR_IDS = [
    0x2270, 0x2271, 0x2272, 0x2273, 0x2274,
    0x2296, 0x2297, 0x2298, 0x2299,
    0x227C, 0x227D, 0x229A,
    0x22B0, 0x22B1, 0x22B2,
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def pe_info(path: Path) -> tuple[pefile.PE, bytes, int]:
    data = path.read_bytes()
    pe = pefile.PE(data=data, fast_load=False)
    return pe, data, int(pe.OPTIONAL_HEADER.ImageBase)


def read_va(pe: pefile.PE, data: bytes, base: int, va: int, size: int) -> bytes:
    off = pe.get_offset_from_rva(va - base)
    if off is None:
        raise ValueError(f"VA {va:#x} has no file offset")
    return data[off : off + size]


def exports(pe: pefile.PE, base: int) -> dict[str, int]:
    return {
        sym.name.decode("ascii", errors="replace"): base + int(sym.address)
        for sym in pe.DIRECTORY_ENTRY_EXPORT.symbols
        if sym.name
    }


def export_body(pe: pefile.PE, data: bytes, base: int, exps: dict[str, int], name: str) -> dict[str, Any]:
    start = exps[name]
    later = sorted({va for va in exps.values() if va > start})
    if not later:
        raise ValueError(f"cannot infer end of final export {name}")
    end = later[0]
    body = read_va(pe, data, base, start, end - start)
    return {"va": f"0x{start:08X}", "end_va": f"0x{end:08X}", "size": len(body), "sha256": sha256_bytes(body)}


def direct_export_calls(pe: pefile.PE, data: bytes, base: int, exps: dict[str, int], start: int, end: int) -> list[dict[str, str]]:
    blob = read_va(pe, data, base, start, end - start)
    by_va: dict[int, list[str]] = {}
    for name, va in exps.items():
        by_va.setdefault(va, []).append(name)
    result = []
    for i in range(len(blob) - 4):
        if blob[i] != 0xE8:
            continue
        rel = struct.unpack_from("<i", blob, i + 1)[0]
        call_va = start + i
        target = call_va + 5 + rel
        if target not in by_va:
            continue
        result.append({"call_va": f"0x{call_va:08X}", "target_va": f"0x{target:08X}", "target": min(by_va[target])})
    return result


def operation_anchor(pe: pefile.PE, data: bytes, base: int, spec: tuple[Any, ...]) -> list[dict[str, str]]:
    out = []
    for i in range(0, len(spec), 2):
        va = int(spec[i])
        expected = bytes.fromhex(str(spec[i + 1]))
        actual = read_va(pe, data, base, va, len(expected))
        if actual != expected:
            raise ValueError(f"operation anchor drift at {va:#x}: {actual.hex()} != {expected.hex()}")
        out.append({"va": f"0x{va:08X}", "bytes": expected.hex()})
    return out


def image_frame_selector_time_series(split_no: int, data_set_no: int, trigger_part_a: int, trigger_part_b: int) -> int:
    """Express FUN_10003200: packed current Image-FFD time-series selector."""
    high = ((split_no & 0xFF) * 0x200 + (data_set_no & 0xFF) * 10 - 9) & 0xFFFF
    low = ((trigger_part_a & 0xFF) + (trigger_part_b & 0xFF) - 1) & 0xFFFF
    return (high << 16) | low


def image_frame_selector_occurrence(split_no: int, data_set_no: int, trigger_no: int) -> int:
    """Express FUN_10003250: current Image-FFD occurrence selector (0000xxxx)."""
    return ((split_no & 0xFF) * 0x200 + (data_set_no & 0xFF) * 10 + (trigger_no & 0xFF) - 10) & 0xFFFF


def level49(seed: bytes) -> bytes:
    """Independently express current CalculateKeyDataSecLv49 semantics."""
    if len(seed) != 6:
        raise ValueError("level-49 seed must be six bytes")
    rotation_table = (1, 2, 3, 3, 2, 1)
    out = bytearray(6)
    for i, value in enumerate(seed):
        index = value & 7
        if index >= 6:
            index -= 6
        add = out[index] if index < i else seed[index]
        selector = (value >> rotation_table[i]) & 3
        count = selector + 1
        rotated = ((value << count) | (value >> (8 - count))) & 0xFF
        out[i] = (rotated + add) & 0xFF
    return bytes(out)


def build() -> dict[str, Any]:
    gts = resolve_gts_root()
    operation_path = gts / "bin/GetTSS3OperationFFDP5_DT.dll"
    if not operation_path.is_file():
        raise FileNotFoundError(operation_path)

    with tempfile.TemporaryDirectory(prefix="tss3-native-recorder-") as td:
        recovered_root = Path(td) / "recovered"
        manifest = recover(output=recovered_root)
        by_path = {row["path"]: row for row in manifest["binaries"]}
        command_path = recovered_root / "bin/CommandCommon.dll"
        image_path = recovered_root / "bin/GetTSS3ImageFFDP5_DT.dll"

        command_pe, command_data, command_base = pe_info(command_path)
        image_pe, image_data, image_base = pe_info(image_path)
        operation_pe, operation_data, operation_base = pe_info(operation_path)
        command_exports = exports(command_pe, command_base)
        image_exports = exports(image_pe, image_base)

        missing = [name for name in IMAGE_EXPORTS.values() if name not in command_exports]
        if missing:
            raise ValueError(f"current CommandCommon export drift: {missing}")

        functions = {
            key: export_body(command_pe, command_data, command_base, command_exports, name)
            for key, name in IMAGE_EXPORTS.items()
        }
        info_start = command_exports[IMAGE_EXPORTS["image_info"]]
        info_end = int(functions["image_info"]["end_va"], 16)
        info_calls = direct_export_calls(command_pe, command_data, command_base, command_exports, info_start, info_end)
        semantic_targets = [row["target"] for row in info_calls]
        expected_order = [
            IMAGE_EXPORTS["image_spec"],
            IMAGE_EXPORTS["image_availability"],
            IMAGE_EXPORTS["image_availability"],
            IMAGE_EXPORTS["security_unlock"],
            IMAGE_EXPORTS["image_encryption"],
        ]
        filtered = [x for x in semantic_targets if x in set(expected_order)]
        if filtered != expected_order:
            raise ValueError(f"TSS3 Image FFD call-order drift: {filtered}")

        constants = {
            "availability": {"request": "221101", "mask": "ffffff", "positive": "621101", "va": "0x100D7E5C"},
            "spec_information": {"request": "221103", "mask": "ffffff", "positive": "621103", "va": "0x100D7F08"},
            "encryption_method": {"request": "222081", "mask": "ffffff", "positive": "622081", "va": "0x100D7FBC"},
            "security_seed": {"request": "2703", "mask": "ffff", "positive": "6703", "request_va": "0x100D7E98", "positive_va": "0x100D7EA4"},
            "security_key": {"request_prefix": "2704", "mask_prefix": "ffff", "positive": "6704", "request_va": "0x100D7ED8", "positive_va": "0x100D7EE0"},
        }
        for block in constants.values():
            if "va" in block:
                start_va = int(block["va"], 16)
                for cell_index, field in enumerate(("request", "mask", "positive")):
                    expected = bytes.fromhex(block[field])
                    actual = read_va(command_pe, command_data, command_base, start_va + cell_index * 4, len(expected))
                    if actual != expected:
                        raise ValueError(
                            f"current CommandCommon {field} constant drift at {start_va + cell_index * 4:#x}"
                        )
        for key in ("security_seed", "security_key"):
            block = constants[key]
            req = bytes.fromhex(block.get("request", block.get("request_prefix", "")))
            pos = bytes.fromhex(block["positive"])
            if read_va(command_pe, command_data, command_base, int(block["request_va"], 16), len(req)) != req:
                raise ValueError(f"{key} request drift")
            if read_va(command_pe, command_data, command_base, int(block["positive_va"], 16), len(pos)) != pos:
                raise ValueError(f"{key} positive drift")

        op_functions: dict[str, Any] = {}
        for key, (start, end) in OPERATION_FUNCTIONS.items():
            body = read_va(operation_pe, operation_data, operation_base, start, end - start)
            op_functions[key] = {"va": f"0x{start:08X}", "end_va": f"0x{end:08X}", "size": len(body), "sha256": sha256_bytes(body)}
        op_anchors = {key: operation_anchor(operation_pe, operation_data, operation_base, spec) for key, spec in OPERATION_CODE_ANCHORS.items()}

        special_va = 0x10005548
        special_raw = read_va(operation_pe, operation_data, operation_base, special_va, 30)
        special_values = list(struct.unpack("<15H", special_raw))
        if special_values != SPECIAL_BEHAVIOR_IDS:
            raise ValueError(f"special behavior table drift: {special_values}")

        # The Image plugin also owns the split-record transport that follows the
        # CommandCommon setup/security path. Pin exact current function bodies
        # and direct machine-code anchors so this grammar fails closed on drift.
        image_execute = image_exports.get("Execute")
        if image_execute != 0x1000EEB0:
            raise ValueError(f"GetTSS3Image Execute drift: {image_execute}")
        image_plugin_functions: dict[str, Any] = {}
        for key, (start, end) in IMAGE_PLUGIN_FUNCTIONS.items():
            body = read_va(image_pe, image_data, image_base, start, end - start)
            image_plugin_functions[key] = {
                "va": f"0x{start:08X}",
                "end_va": f"0x{end:08X}",
                "size": len(body),
                "sha256": sha256_bytes(body),
            }
        image_plugin_anchors = {
            key: operation_anchor(image_pe, image_data, image_base, spec)
            for key, spec in IMAGE_PLUGIN_CODE_ANCHORS.items()
        }

        frame_vectors = {
            "occurrence_split1_set1_trigger1": f"0x{image_frame_selector_occurrence(1, 1, 1):08X}",
            "occurrence_split22_set3_trigger7": f"0x{image_frame_selector_occurrence(22, 3, 7):08X}",
            "time_series_split1_set1_parts1_0": f"0x{image_frame_selector_time_series(1, 1, 1, 0):08X}",
            "time_series_split22_set3_parts4_3": f"0x{image_frame_selector_time_series(22, 3, 4, 3):08X}",
        }

        vectors = {
            "000000000000": level49(bytes.fromhex("000000000000")).hex(),
            "010203040506": level49(bytes.fromhex("010203040506")).hex(),
            "123456789abc": level49(bytes.fromhex("123456789abc")).hex(),
            "deadbeefcafe": level49(bytes.fromhex("deadbeefcafe")).hex(),
        }

        return {
            "schema": "gtsplus-tss3-native-recorder-protocol-v1",
            "gtsplus_version": manifest["gtsplus_version"],
            "sources": {
                "command_common": {"path": "bin/CommandCommon.dll", "size": command_path.stat().st_size, "sha256": sha256_file(command_path), "provenance": by_path["bin/CommandCommon.dll"]["installer"]},
                "image_plugin": {"path": "bin/GetTSS3ImageFFDP5_DT.dll", "size": image_path.stat().st_size, "sha256": sha256_file(image_path), "provenance": by_path["bin/GetTSS3ImageFFDP5_DT.dll"]["installer"]},
                "operation_plugin": {"path": "bin/GetTSS3OperationFFDP5_DT.dll", "size": operation_path.stat().st_size, "sha256": sha256_file(operation_path), "provenance": "current installed image is already materialized"},
            },
            "operation_ffd": {
                "selector": "0x66",
                "requests": {
                    "enumerate_behavior_codes": {"request": "AB11", "positive": "EB11", "response_items": "BE16 behavior/RoB codes from response offset 2"},
                    "enumerate_behavior_records": {"request": "AB12 || behavior_id_be16", "positive": "EB12", "response_items": "BE16 record/frame IDs from response offset 4; sorted and deduplicated"},
                    "fetch_record": {"request": "AB13 || behavior_id_be16 || record_id_be16", "positive": "EB13"},
                },
                "record_parser": {"data_offset": 6, "block": "data_id_be16 || length_u8 || data[length]", "duplicate_policy": "deduplicate Data IDs within each parsed group", "special_data_id": "0x0501 is additionally surfaced as BE16 metadata when length >= 2"},
                "special_behavior_ids": [f"0x{x:04X}" for x in special_values],
                "special_behavior_table_va": f"0x{special_va:08X}",
                "functions": op_functions,
                "code_anchors": op_anchors,
            },
            "image_ffd": {
                "plugin_execute_va": f"0x{image_execute:08X}",
                "functions": functions,
                "get_info_direct_calls": info_calls,
                "semantic_call_order": ["get spec information", "get flag/availability", "get flag/availability (spec-dependent branch)", "security unlock", "get encryption method"],
                "frames": constants,
                "spec_contract": {"accepted_spec_values": [5, 7], "spec_5_availability_slots": list(range(1, 11)), "spec_7_availability_slots": list(range(1, 12)), "available_value": 2},
                "security": {"seed_length": 6, "seed_request": "2703", "key_request_prefix": "2704", "algorithm": "CCmdImgOpeDdr::CalculateKeyDataSecLv49", "algorithm_vectors": vectors, "boundary": "SecurityUnlock16Byte is a separate current body using CalculateKeyDataSecLv2; GetTSS3ImageFFDInfo calls the six-byte SecurityUnlock path."},
                "split_record_protocol": {
                    "requests": {
                        "enumerate_rob_codes": {
                            "request": "AB31",
                            "positive": "EB31",
                            "response_items": "BE16 RoB codes from response offset 2",
                        },
                        "fetch_record": {
                            "request": "AB33 || rob_code_be16 || frame_number_be32",
                            "positive": "EB33",
                        },
                    },
                    "eb33_response": {
                        "header": "EB33 || rob_code_be16 || frame_number_be32 || block_count_u8",
                        "block_count_offset": 8,
                        "blocks_offset": 9,
                        "block": "data_id_be16 || length || data[length]",
                        "length": "BE32 when data_id is 0x6000..0x6FFF; otherwise u8",
                        "count_zero_policy": "derive block count by scanning valid blocks from offset 9",
                        "duplicate_policy": "deduplicate Data IDs within the parsed record",
                        "special_data_id": "0x0501 is additionally surfaced as BE16 metadata when length >= 2",
                    },
                    "frame_number_helpers": {
                        "occurrence": "u32 = 0x00000000 | (split*0x200 + data_set*10 + trigger - 10)",
                        "time_series": "u32 = ((split*0x200 + data_set*10 - 9) << 16) | (trigger_part_a + trigger_part_b - 1)",
                        "split_range_observed_in_current acquisition loops": [1, 22],
                        "vectors": frame_vectors,
                    },
                    "functions": image_plugin_functions,
                    "code_anchors": image_plugin_anchors,
                },
            },
            "conclusions": [
                "The complete current-release native TSS3 recorder acquisition stack is now available without V18 behavioral transfer: current Operation plugin plus recovered-original current Image plugin and CommandCommon.",
                "Operation FFD uses proprietary AB11/12/13 requests with EB11/12/13 responses and selector 0x66; record payloads carry BE16 recorder Data IDs and u8 lengths.",
                "Current TSS3 Image FFD reads DID 0x1103 spec information and DID 0x1101 availability, then performs SecurityAccess 0x27 subfunctions 0x03/0x04 with a six-byte level-49 key before reading DID 0x2081 encryption method.",
                "Image spec values 5 and 7 are explicitly supported; availability value 2 marks memorized image slots, 1..10 for spec5 and 1..11 for spec7.",
                "Current Image-FFD split transport uses AB31/EB31 for RoB enumeration and AB33/EB33 for record fetch; EB33 carries RoB code, BE32 frame number, block count, and variable-length Data-ID blocks.",
            ],
            "boundary": "This is Techstream host acquisition/decoding semantics. It does not identify the ECU-side recorder producer, CAN/CAN-FD arbitration IDs, SecOC ownership, or arbitration execution owner.",
        }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    payload = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {payload['sources']['command_common']['sha256'][:12]} operation={payload['sources']['operation_plugin']['sha256'][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
