#!/usr/bin/env python3
"""Extract TSS3 managed recorder tables from a CP-recovered PCS Data Viewer PE.

The shipped PCS Data Viewer.exe intentionally has zeroed managed method bodies.
Run ``tools/gts recover-aux-bodies`` (or ``recover-all-bodies``) first, then
point this extractor at the recovered PE.  It interprets the straight-line
static-constructor subset needed for Toyota's Operation-FFD TSS3 definition
objects and validates the exact FCM TSS3 image-decoder IL shape; it is not a
general CLR interpreter.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dnfile  # type: ignore
from dncil.cil.body import CilMethodBody  # type: ignore

from extract_pcs_data_viewer_tss3_dictionary import load_culture
from inspect_dotnet_il import MethodBodyReader, resolve_token, type_name
from techstream_paths import resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json"
DID_DEFINE = "PCSDataViewer.Extractor.OperationFFD.TSS3.Define.DIDDataDefine"
DETAIL_INFO = "PCSDataViewer.Extractor.OperationFFD.TSS3.Define.DetailBitAssignInfo"
ROB_DEFINE = "PCSDataViewer.Extractor.OperationFFD.TSS3.Define.RoBCodeDefine"
ROB_INFO = "PCSDataViewer.Extractor.OperationFFD.TSS3.Define.RoBCodeDetailInfo"
TSS3_OPERATION_EXTRACTOR = "PCSDataViewer.Extractor.OperationFFD.TSS3.TSS3OperationFFDExtractor"
DETAIL_FIELDS = (
    "DataName", "DataID", "DataSize", "SupportDID", "BytePosition", "BitPosition",
    "BitLength", "InvalidValueList", "Type", "Lsb", "Offset", "Point",
)
ROB_FIELDS = (
    "DataName", "SystemType", "Group", "Sampling", "PreTriggerNumber",
    "PostTriggerNumber", "IsMultiTrigger", "UniqueRoBCodeDID",
)
STEERING_DIDS = {"5282", "5285", "5531", "560D", "5631", "5681", "568D", "57A3", "57DE", "590C"}
FCM_IMAGE_TYPE = "PCSDataViewer.Extractor.ImageFFD.FCMImageFFD.FCMImageFFDTSS3.DataTable.FCMDataTableImage"
FCM_IMAGE_MODEL = "PCSDataViewer.Extractor.ImageFFD.FCMImageFFD.FCMImageFFDTSS3.Model.FFImage"
FCM_IMAGE_LOG = "PCSDataViewer.Extractor.ImageFFD.FCMImageFFD.FCMImageFFDTSS3.LogAnalyser.LogAnalyser622081"
FCM_IMAGE_EXTRACTOR = "PCSDataViewer.Extractor.ImageFFD.FCMImageFFD.FCMImageFFDTSS3.FCMImageFFDTTS3"
FCM_IMAGE_EB33 = "PCSDataViewer.Extractor.ImageFFD.FCMImageFFD.FCMImageFFDTSS3.LogAnalyser.LogAnalyserEB33"
FCM_IMAGE_EB33_LIST = "PCSDataViewer.Extractor.ImageFFD.FCMImageFFD.FCMImageFFDTSS3.LogAnalyser.LogAnalyserEB33List"
FCM_IMAGE_DID_TABLE = "PCSDataViewer.Extractor.ImageFFD.FCMImageFFD.FCMImageFFDTSS3.DataTable.FCMDataTableDIDData"
FCM_IMAGE_FRAME = "PCSDataViewer.Extractor.ImageFFD.FCMImageFFD.FCMImageFFDTSS3.Model.FrameNumberData"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class Collection:
    kind: str
    data: list[Any]


@dataclass
class Record:
    data: dict[str, Any]


def _int_constant(ins: Any) -> int | None:
    op = str(ins.opcode)
    table = {
        "ldc.i4.m1": -1,
        "ldc.i4.0": 0,
        "ldc.i4.1": 1,
        "ldc.i4.2": 2,
        "ldc.i4.3": 3,
        "ldc.i4.4": 4,
        "ldc.i4.5": 5,
        "ldc.i4.6": 6,
        "ldc.i4.7": 7,
        "ldc.i4.8": 8,
    }
    if op in table:
        return table[op]
    if op in ("ldc.i4.s", "ldc.i4"):
        return int(ins.operand)
    return None


def _method_owner_map(pe: dnfile.dnPE) -> dict[int, str]:
    out: dict[int, str] = {}
    for td in pe.net.mdtables.TypeDef.rows:
        owner = type_name(td)
        for item in td.MethodList:
            if getattr(item, "row", None) is not None:
                out[id(item.row)] = owner
    return out


def _owner_and_name(row: Any, method_owners: dict[int, str]) -> tuple[str, str]:
    if isinstance(row, dnfile.mdtable.MethodDefRow):
        return method_owners.get(id(row), "?"), str(row.Name)
    if isinstance(row, dnfile.mdtable.MemberRefRow):
        class_row = getattr(row.Class, "row", None)
        return type_name(class_row) if class_row is not None else "?", str(row.Name)
    return "?", str(getattr(row, "Name", row))


def _field_owner_and_name(row: Any) -> tuple[str, str]:
    if isinstance(row, dnfile.mdtable.MemberRefRow):
        class_row = getattr(row.Class, "row", None)
        return type_name(class_row) if class_row is not None else "?", str(row.Name)
    return "?", str(getattr(row, "Name", row))


def _find_method(pe: dnfile.dnPE, full_type: str, name: str) -> dnfile.mdtable.MethodDefRow:
    for td in pe.net.mdtables.TypeDef.rows:
        if type_name(td) != full_type:
            continue
        matches = [item.row for item in td.MethodList if str(item.row.Name) == name]
        if len(matches) != 1:
            raise ValueError(f"{full_type}: expected one {name}, got {len(matches)}")
        return matches[0]
    raise ValueError(f"type not found: {full_type}")


def _method_instructions(pe: dnfile.dnPE, full_type: str, name: str) -> tuple[int, list[Any]]:
    method = _find_method(pe, full_type, name)
    body = CilMethodBody(MethodBodyReader(pe, method))
    return int(method.Rva), list(body.instructions)


def _call_names(pe: dnfile.dnPE, instructions: list[Any]) -> list[tuple[str, str]]:
    owners = _method_owner_map(pe)
    out: list[tuple[str, str]] = []
    for ins in instructions:
        if str(ins.opcode) not in ("call", "callvirt", "newobj"):
            continue
        out.append(_owner_and_name(resolve_token(pe, ins.operand), owners))
    return out


def _extract_fcm_image_contract(pe: dnfile.dnPE) -> dict[str, Any]:
    table_rva, table = _method_instructions(pe, FCM_IMAGE_TYPE, ".cctor")
    table_ints = [value for ins in table if (value := _int_constant(ins)) is not None]
    table_strings = [str(resolve_token(pe, ins.operand)) for ins in table if str(ins.opcode) == "ldstr"]
    table_fields = [
        _field_owner_and_name(resolve_token(pe, ins.operand))[1]
        for ins in table
        if str(ins.opcode) == "ldsfld"
    ]
    if table_ints != [360, 180, 170, 0, 0] or table_strings != ["{0:D3}.jpg"] or table_fields != ["NO_05", "NO_07"]:
        raise ValueError(
            "unexpected FCM TSS3 image table constructor: "
            f"ints={table_ints!r} strings={table_strings!r} fields={table_fields!r}"
        )

    judge_rva, judge = _method_instructions(pe, FCM_IMAGE_MODEL, "JudgeEncryption")
    judge_ops = [str(ins.opcode) for ins in judge]
    judge_strings = [str(resolve_token(pe, ins.operand)) for ins in judge if str(ins.opcode) == "ldstr"]
    judge_calls = _call_names(pe, judge)
    if judge_strings != ["01"] or judge_ops != ["ldarg.0", "ldstr", "call", "ldc.i4.0", "cgt.un", "ret"]:
        raise ValueError(f"unexpected FCM TSS3 JudgeEncryption body: ops={judge_ops!r} strings={judge_strings!r}")
    if judge_calls != [("System.String", "op_Equality")]:
        raise ValueError(f"unexpected FCM TSS3 JudgeEncryption call: {judge_calls!r}")

    log_rva, log = _method_instructions(pe, FCM_IMAGE_LOG, "GetEncryption")
    log_ints = [value for ins in log if (value := _int_constant(ins)) is not None]
    log_calls = _call_names(pe, log)
    if log_ints != [0, 8, 1, 6, 2, 1]:
        raise ValueError(f"unexpected FCM TSS3 GetEncryption constants: {log_ints!r}")
    if ("System.String", "Substring") not in log_calls or (FCM_IMAGE_MODEL, "JudgeEncryption") not in log_calls:
        raise ValueError(f"unexpected FCM TSS3 GetEncryption calls: {log_calls!r}")

    decrypt_rva, decrypt = _method_instructions(pe, FCM_IMAGE_MODEL, "DecryptionImageBuffer")
    decrypt_ops = [str(ins.opcode) for ins in decrypt]
    decrypt_ints = [value for ins in decrypt if (value := _int_constant(ins)) is not None]
    decrypt_calls = _call_names(pe, decrypt)
    expected_bit_reverse = [1, 7, 2, 5, 4, 3, 8, 1, 16, 1, 32, 3, 64, 5, 128, 7]
    if decrypt_ints != expected_bit_reverse:
        raise ValueError(f"unexpected FCM TSS3 byte transform constants: {decrypt_ints!r}")
    if decrypt_ops.count("and") != 8 or decrypt_ops.count("or") != 7 or decrypt_ops.count("xor") != 1:
        raise ValueError("unexpected FCM TSS3 byte transform opcode census")
    if (FCM_IMAGE_TYPE, "GetEncryptionKey") not in decrypt_calls:
        raise ValueError(f"FCM TSS3 decryption does not fetch image encryption key: {decrypt_calls!r}")

    create_rva, create = _method_instructions(pe, FCM_IMAGE_MODEL, "Create")
    create_calls = _call_names(pe, create)
    if (FCM_IMAGE_MODEL, "DecryptionImageBuffer") not in create_calls or ("System.Drawing.ImageConverter", ".ctor") not in create_calls:
        raise ValueError(f"unexpected FCM TSS3 image creation path: {create_calls!r}")

    extract_rva, extract = _method_instructions(pe, FCM_IMAGE_EXTRACTOR, "Extract")
    extract_calls = _call_names(pe, extract)
    for required in (
        (FCM_IMAGE_EXTRACTOR, "AnalyzeExtractionsType"),
        (FCM_IMAGE_EXTRACTOR, "GetImageFFDInfoForSplit"),
        (FCM_IMAGE_EXTRACTOR, "CreateImageFFDExtractDataForSplit"),
    ):
        if required not in extract_calls:
            raise ValueError(f"FCM TSS3 split extractor missing {required}: {extract_calls!r}")
    if [value for ins in extract if (value := _int_constant(ins)) is not None] != [1]:
        raise ValueError("unexpected FCM TSS3 Extract type discriminator")

    analyze_rva, analyze = _method_instructions(pe, FCM_IMAGE_EXTRACTOR, "AnalyzeExtractionsType")
    analyze_strings = [str(resolve_token(pe, ins.operand)) for ins in analyze if str(ins.opcode) == "ldstr"]
    if [value for value in analyze_strings if value] != ["EB21", "EB31"]:
        raise ValueError(f"unexpected FCM TSS3 extraction markers: {analyze_strings!r}")

    split_info_rva, split_info = _method_instructions(pe, FCM_IMAGE_EXTRACTOR, "GetImageFFDInfoForSplit")
    split_info_strings = [str(resolve_token(pe, ins.operand)) for ins in split_info if str(ins.opcode) == "ldstr"]
    if split_info_strings != ["621103", "622081", "EB33"]:
        raise ValueError(f"unexpected FCM TSS3 split-info markers: {split_info_strings!r}")

    rob_rva, rob = _method_instructions(pe, FCM_IMAGE_EB33, "GetRoBCode")
    frame_rva, frame = _method_instructions(pe, FCM_IMAGE_EB33, "GetFrameNumber")
    rob_ints = [value for ins in rob if (value := _int_constant(ins)) is not None]
    frame_ints = [value for ins in frame if (value := _int_constant(ins)) is not None]
    if rob_ints != [8, 1, 4, 4, 1] or frame_ints != [16, 1, 8, 8, 1]:
        raise ValueError(f"unexpected FCM TSS3 EB33 header geometry: rob={rob_ints!r} frame={frame_ints!r}")

    split_ids_rva, split_ids_method = _method_instructions(pe, FCM_IMAGE_DID_TABLE, "GetAllSplitImageDataID")
    split_fields = [
        _field_owner_and_name(resolve_token(pe, ins.operand))[1]
        for ins in split_ids_method
        if str(ins.opcode) == "ldsfld"
    ]
    expected_split_fields = [f"ID_{value:04X}" for value in range(0x6002, 0x6018)]
    if split_fields != expected_split_fields:
        raise ValueError(f"unexpected FCM TSS3 split image IDs: {split_fields!r}")

    parse_rva, parse = _method_instructions(pe, FCM_IMAGE_EB33_LIST, "CreateDIDDataList")
    parse_ints = [value for ins in parse if (value := _int_constant(ins)) is not None]
    parse_strings = [str(resolve_token(pe, ins.operand)) for ins in parse if str(ins.opcode) == "ldstr"]
    if parse_ints != [18, 1, 18, 4, 0, 4, 2, 8, 4, 4, 0x203, 2, 4, 4, 4, 1] or parse_strings != ["6"]:
        raise ValueError(f"unexpected FCM TSS3 EB33 DID grammar: ints={parse_ints!r} strings={parse_strings!r}")

    join_rva, join = _method_instructions(pe, FCM_IMAGE_EB33_LIST, "CreateDIDDataListjoinedLog")
    join_fields = [
        _field_owner_and_name(resolve_token(pe, ins.operand))[1]
        for ins in join
        if str(ins.opcode) == "ldsfld"
    ]
    join_calls = _call_names(pe, join)
    if join_fields != ["Empty", "ID_6002", "Empty", "ID_6001"]:
        raise ValueError(f"unexpected FCM TSS3 split join fields: {join_fields!r}")
    if (FCM_IMAGE_DID_TABLE, "GetAllSplitImageDataID") not in join_calls or ("System.Text.StringBuilder", "Append") not in join_calls:
        raise ValueError(f"unexpected FCM TSS3 split join calls: {join_calls!r}")

    frame_table_rva, frame_table = _method_instructions(pe, FCM_IMAGE_FRAME, ".cctor")
    if [value for ins in frame_table if (value := _int_constant(ins)) is not None] != [0x200, 10]:
        raise ValueError("unexpected FCM TSS3 frame-number constants")
    split_number_rva, split_number = _method_instructions(pe, FCM_IMAGE_FRAME, "ExtractSplitNumber")
    if [str(ins.opcode) for ins in split_number] != ["ldarg.1", "ldsfld", "div", "ret"]:
        raise ValueError("unexpected FCM TSS3 split-number extraction")

    frame_ctor_rva, frame_ctor = _method_instructions(pe, FCM_IMAGE_FRAME, ".ctor")
    ctor_strings = [str(resolve_token(pe, ins.operand)) for ins in frame_ctor if str(ins.opcode) == "ldstr"]
    ctor_calls = _call_names(pe, frame_ctor)
    expected_frame_calls = [
        (FCM_IMAGE_FRAME, "ExtractSplitNumber"),
        (FCM_IMAGE_FRAME, "ExtractTriggerNumberForOccur"),
        (FCM_IMAGE_FRAME, "ExtractDataSetNumberForOccur"),
        (FCM_IMAGE_FRAME, "ExtractTriggerNumberForTimeSeries"),
        (FCM_IMAGE_FRAME, "ExtractDataSetNumberForTimeSeries"),
    ]
    if ctor_strings != ["0000"] or any(call not in ctor_calls for call in expected_frame_calls):
        raise ValueError(f"unexpected FCM TSS3 frame constructor: strings={ctor_strings!r} calls={ctor_calls!r}")

    occur_trigger_rva, occur_trigger = _method_instructions(pe, FCM_IMAGE_FRAME, "ExtractTriggerNumberForOccur")
    if [str(ins.opcode) for ins in occur_trigger] != ["ldarg.1", "ldsfld", "rem", "ldc.i4.1", "sub", "ldsfld", "rem", "ldc.i4.1", "add", "ret"]:
        raise ValueError("unexpected FCM TSS3 occurrence-trigger decoder")
    occur_set_rva, occur_set = _method_instructions(pe, FCM_IMAGE_FRAME, "ExtractDataSetNumberForOccur")
    occur_set_calls = _call_names(pe, occur_set)
    if ("System.Math", "Ceiling") not in occur_set_calls or ("System.Decimal", "ToInt32") not in occur_set_calls:
        raise ValueError(f"unexpected FCM TSS3 occurrence-set decoder: {occur_set_calls!r}")

    series_trigger_rva, series_trigger = _method_instructions(pe, FCM_IMAGE_FRAME, "ExtractTriggerNumberForTimeSeries")
    if [str(ins.opcode) for ins in series_trigger] != ["ldarg.1", "ldc.i4.1", "add", "ret"]:
        raise ValueError("unexpected FCM TSS3 time-series trigger decoder")
    series_set_rva, series_set = _method_instructions(pe, FCM_IMAGE_FRAME, "ExtractDataSetNumberForTimeSeries")
    if [str(ins.opcode) for ins in series_set] != ["ldarg.1", "ldsfld", "ldarg.2", "mul", "sub", "ldc.i4.1", "sub", "ldsfld", "div", "ldc.i4.1", "add", "ret"]:
        raise ValueError("unexpected FCM TSS3 time-series set decoder")

    return {
        "image_table_cctor_rva": table_rva,
        "accepted_specs": [5, 7],
        "width": 360,
        "height": 180,
        "filename_format": "{0:D3}.jpg",
        "encryption_key": 170,
        "encryption_status": {
            "diagnostic_did": "2081",
            "positive_response_prefix": "622081",
            "value_hex_offset": 6,
            "value_hex_length": 2,
            "unencrypted_value": "01",
            "decrypt_when": "value != 01",
            "source_method_rva": log_rva,
            "predicate_method_rva": judge_rva,
        },
        "decryption": {
            "per_byte": "reverse_bits8(cipher_byte) XOR 0xAA",
            "bit_mapping": "b0->b7,b1->b6,b2->b5,b3->b4,b4->b3,b5->b2,b6->b1,b7->b0",
            "source_method_rva": decrypt_rva,
            "create_method_rva": create_rva,
        },
        "split_transport": {
            "extract_method_rva": extract_rva,
            "extraction_type_method_rva": analyze_rva,
            "detected_markers": {"unsplit": "EB21", "split": "EB31"},
            "supported_path": "split EB31/EB33; Extract rejects the EB21 discriminator",
            "split_info_method_rva": split_info_rva,
            "split_info_markers": ["621103", "622081", "EB33"],
            "eb33": {
                "rob_code_hex_offset": 4,
                "rob_code_hex_length": 4,
                "frame_number_hex_offset": 8,
                "frame_number_hex_length": 8,
                "did_stream_hex_offset": 18,
                "did_id_hex_length": 4,
                "length_hex_length": {"did_starts_with_6": 8, "other": 2},
                "length_number_style": "0x203 (hex)",
                "data_hex_length": "2 * parsed byte length",
                "rob_parser_method_rva": rob_rva,
                "frame_parser_method_rva": frame_rva,
                "did_parser_method_rva": parse_rva,
            },
            "split_image_dids": [field.removeprefix("ID_") for field in split_fields],
            "assembled_raw_image_did": "6001",
            "reassembly": "for each split group, append the first present DID from 6002..6017; publish the concatenation as DID 6001",
            "first_split_group_required": 1,
            "first_group_metadata_split_id_removed": "6002",
            "join_method_rva": join_rva,
            "split_id_table_method_rva": split_ids_rva,
            "frame_number": {
                "split_divisor": 0x200,
                "trigger_point_max": 10,
                "format_width_hex": 8,
                "occurrence_selector": "first four frame-number hex characters are 0000",
                "occurrence_decode": {
                    "split": "value // 0x200",
                    "trigger": "((value % 0x200 - 1) % 10) + 1",
                    "data_set": "ceil((value % 0x200) / 10)",
                    "trigger_type": "1 when trigger == 1, otherwise 2",
                },
                "time_series_decode": {
                    "high16": "frame_number[0:4] as hex",
                    "low16": "frame_number[4:8] as hex",
                    "split": "high16 // 0x200",
                    "trigger": "low16 + 1",
                    "data_set": "((high16 - split*0x200 - 1) // 10) + 1",
                    "trigger_type": 3,
                },
                "methods": {
                    "constructor_rva": frame_ctor_rva,
                    "constants_rva": frame_table_rva,
                    "split_rva": split_number_rva,
                    "occurrence_trigger_rva": occur_trigger_rva,
                    "occurrence_data_set_rva": occur_set_rva,
                    "time_series_trigger_rva": series_trigger_rva,
                    "time_series_data_set_rva": series_set_rva,
                },
            },
        },
    }


def _decimal_from_ctor(stack: list[Any], row: dnfile.mdtable.MemberRefRow) -> Decimal:
    signature = bytes(row.Signature.value)
    argc = signature[1] if len(signature) > 1 else -1
    if argc == 1:
        return Decimal(stack.pop())
    if argc != 5:
        raise ValueError(f"unsupported Decimal ctor signature: {signature.hex()}")
    scale = int(stack.pop())
    negative = bool(stack.pop())
    hi = int(stack.pop()) & 0xFFFFFFFF
    mid = int(stack.pop()) & 0xFFFFFFFF
    lo = int(stack.pop()) & 0xFFFFFFFF
    value = Decimal((hi << 64) + (mid << 32) + lo) / (Decimal(10) ** scale)
    return -value if negative else value


def _interpret_collection(
    pe: dnfile.dnPE,
    english: dict[str, str | bytes],
    *,
    define_type: str,
    record_type: str,
    record_fields: tuple[str, ...],
    resource_prefix: str,
) -> tuple[int, list[tuple[Any, dict[str, Any]]]]:
    method = _find_method(pe, define_type, ".cctor")
    body = CilMethodBody(MethodBodyReader(pe, method))
    owners = _method_owner_map(pe)
    stack: list[Any] = []
    typespec_ctor_count = 0
    records: list[tuple[Any, dict[str, Any]]] = []

    for index, ins in enumerate(body.instructions):
        op = str(ins.opcode)
        integer = _int_constant(ins)
        if integer is not None:
            stack.append(integer)
            continue
        if op == "ldstr":
            stack.append(str(resolve_token(pe, ins.operand)))
            continue
        if op == "ldnull":
            stack.append(None)
            continue
        if op == "dup":
            stack.append(stack[-1])
            continue
        if op == "pop":
            stack.pop()
            continue
        if op == "ldsfld":
            field = resolve_token(pe, ins.operand)
            owner, name = _field_owner_and_name(field)
            if owner == "System.Decimal" and name == "One":
                stack.append(Decimal(1))
            elif owner == "System.Decimal" and name == "Zero":
                stack.append(Decimal(0))
            elif owner == "System.String" and name == "Empty":
                stack.append("")
            else:
                raise ValueError(f"{define_type}: unsupported static field {owner}::{name} at instruction {index}")
            continue
        if op in ("call", "callvirt"):
            called = resolve_token(pe, ins.operand)
            owner, name = _owner_and_name(called, owners)
            if name.startswith("get_") and name[4:].startswith(resource_prefix):
                key = name[4:]
                value = english.get(key)
                if not isinstance(value, str):
                    raise ValueError(f"missing English string resource {key}")
                stack.append(value)
                continue
            if name == "Add":
                if len(stack) >= 2 and isinstance(stack[-2], Collection) and stack[-2].kind == "list":
                    value = stack.pop()
                    target = stack.pop()
                    target.data.append(value)
                    continue
                if len(stack) >= 3 and isinstance(stack[-3], Collection) and stack[-3].kind == "outer":
                    value = stack.pop()
                    key = stack.pop()
                    target = stack.pop()
                    target.data.append((key, value))
                    if isinstance(value, Record):
                        records.append((key, value.data))
                    continue
                raise ValueError(f"{define_type}: unsupported Add stack at instruction {index}: {stack[-5:]!r}")
            raise ValueError(f"{define_type}: unsupported call {owner}::{name} at instruction {index}")
        if op == "newobj":
            called = resolve_token(pe, ins.operand)
            owner, name = _owner_and_name(called, owners)
            if name != ".ctor":
                raise ValueError(f"{define_type}: unsupported newobj {owner}::{name}")
            if owner.startswith("<dnfile.mdtable.TypeSpecRow") or owner == "?":
                typespec_ctor_count += 1
                stack.append(Collection("outer" if typespec_ctor_count == 1 else "list", []))
                continue
            if owner == "System.Decimal" and isinstance(called, dnfile.mdtable.MemberRefRow):
                stack.append(_decimal_from_ctor(stack, called))
                continue
            if owner == record_type:
                argc = len(record_fields)
                if len(stack) < argc:
                    raise ValueError(f"{define_type}: short stack for {record_type} ctor")
                values = stack[-argc:]
                del stack[-argc:]
                stack.append(Record(dict(zip(record_fields, values))))
                continue
            raise ValueError(f"{define_type}: unsupported constructor {owner}::{name} at instruction {index}")
        if op == "stsfld":
            stack.pop()
            if records:
                break
            continue
        if op in ("nop",):
            continue
        if op == "ret":
            break
        raise ValueError(f"{define_type}: unsupported opcode {op} at instruction {index}")

    if stack:
        raise ValueError(f"{define_type}: non-empty final evaluation stack: {stack[-5:]!r}")
    return int(method.Rva), records



def _enum_literal_map(pe: dnfile.dnPE, full_type: str) -> dict[int, str]:
    constants: dict[int, int] = {}
    for row in pe.net.mdtables.Constant.rows:
        parent = getattr(row.Parent, "row", None)
        raw = getattr(getattr(row, "Value", None), "value", None)
        if parent is None or not isinstance(raw, (bytes, bytearray)) or len(raw) not in (1, 2, 4, 8):
            continue
        constants[id(parent)] = int.from_bytes(raw, "little", signed=True)
    for td in pe.net.mdtables.TypeDef.rows:
        if type_name(td) != full_type:
            continue
        out: dict[int, str] = {}
        for item in td.FieldList:
            field = item.row
            name = str(field.Name)
            if name == "value__" or id(field) not in constants:
                continue
            value = constants[id(field)]
            if value in out:
                raise ValueError(f"{full_type}: duplicate enum value {value}")
            out[value] = name
        if not out:
            raise ValueError(f"{full_type}: no literal enum values")
        return dict(sorted(out.items()))
    raise ValueError(f"enum type not found: {full_type}")

def _normalize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Collection):
        return [_normalize(item) for item in value.data]
    if isinstance(value, Record):
        return {key: _normalize(item) for key, item in value.data.items()}
    if isinstance(value, dict):
        return {key: _normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    return value



def _rob_system_type_usage(pe: dnfile.dnPE) -> dict[str, Any]:
    analyze_rva, analyze = _method_instructions(pe, TSS3_OPERATION_EXTRACTOR, "AnalyzeRoBParameter")
    analyze_calls = _call_names(pe, analyze)
    required_analyze = [
        (DID_DEFINE, "GetDataCount"),
        (DID_DEFINE, "GetDetailBitAssignInfo"),
        ("PCSDataViewer.Extractor.OperationFFD.TSS3.Model.MeasuredValue", "GetValue"),
    ]
    if any(call not in analyze_calls for call in required_analyze):
        raise ValueError(f"AnalyzeRoBParameter DID-table scan drift: {analyze_calls!r}")
    if any(name == "get_SystemType" for _owner, name in analyze_calls):
        raise ValueError("AnalyzeRoBParameter unexpectedly binds DID extraction to SYSTEM_TYPE")

    multi_rva, multi = _method_instructions(pe, TSS3_OPERATION_EXTRACTOR, "CheckMultiTriggerInfo")
    multi_calls = _call_names(pe, multi)
    if multi_calls.count((ROB_DEFINE, "GetRoBCodeInfo")) != 2:
        raise ValueError("CheckMultiTriggerInfo RoB lookup drift")
    if multi_calls.count((ROB_INFO, "get_SystemType")) != 2 or multi_calls.count((ROB_INFO, "get_Group")) != 2:
        raise ValueError("CheckMultiTriggerInfo SYSTEM_TYPE/group comparison drift")

    return {
        "analyze_rob_parameter_rva": analyze_rva,
        "check_multi_trigger_info_rva": multi_rva,
        "did_decode_scans_full_definition_table": True,
        "analyze_rob_parameter_reads_system_type": False,
        "multi_trigger_matching_compares_system_type_and_group": True,
        "interpretation": "SYSTEM_TYPE classifies/matches RoB trigger families. The per-RoB parameter analyzer iterates the global DID definition table and does not read SYSTEM_TYPE, so the enum is not a per-DID ECU/producer binding.",
    }


def _lateral_arbitration_schema(details: list[dict[str, Any]]) -> dict[str, Any]:
    by_did: dict[str, list[dict[str, Any]]] = {}
    for row in details:
        by_did.setdefault(str(row["DataID"]), []).append(row)

    def selected(did: str, names: list[str]) -> list[dict[str, Any]]:
        rows = {str(row["DataName"]): row for row in by_did.get(did, [])}
        missing = [name for name in names if name not in rows]
        if missing:
            raise ValueError(f"{did}: missing lateral arbitration fields {missing!r}")
        return [rows[name] for name in names]

    generic_names = [
        "TSS request - lateral ID",
        "TSS request - pinion angle",
        "Steering assist gain",
        "Damping control gain",
    ]
    lda_names = [
        "LDA Lateral ID",
        "LDA Control Request Pinion Angle",
        "LDA Steering Assist Gain",
        "LDA Damping Control Gain",
    ]
    lta_names = [
        "LTA Lateral ID",
        "LTA Control Request Pinion Angle",
        "LTA Steering Assist Gain",
        "LTA Damping Control Gain",
    ]
    generic = selected("5282", generic_names)
    lda = selected("5531", lda_names)
    lta = selected("5631", lta_names)

    def shape(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "BytePosition": row["BytePosition"],
                "BitPosition": row["BitPosition"],
                "BitLength": row["BitLength"],
                "Type": row["Type"],
                "Lsb": row["Lsb"],
                "Offset": row["Offset"],
                "Point": row["Point"],
            }
            for row in rows
        ]

    generic_shape = shape(generic)
    if shape(lda) != generic_shape or shape(lta) != generic_shape:
        raise ValueError("generic/LDA/LTA lateral request tuple layout drift")

    pda_id = selected("5A09", ["ID Request Lateral ID"])[0]
    pda_angle = selected("5A0A", ["PDA(OAA) request pinion angle"])[0]
    pda_gains = selected("5A0D", ["PDA(OAA) Gain for steering support", "PDA(OAA) Damping control gain"])

    lca_presence = selected("5202", ["LCA presence information"])[0]
    lca_request_rows = [
        row for row in details
        if "LCA" in str(row["DataName"]).upper()
        and any(token in str(row["DataName"]).lower() for token in ("pinion", "lateral id", "steering assist gain", "damping control gain"))
    ]
    if lca_request_rows:
        raise ValueError(f"unexpected dedicated LCA request tuple rows: {lca_request_rows!r}")

    result_id = selected("5285", ["Arbitration result_lateral ID"])[0]
    result_angle = selected("57DE", ["Arbitration result Pinion angle"])[0]

    return {
        "generic_request": {
            "data_id": "5282",
            "fields": generic,
        },
        "feature_requests": {
            "LDA": {"data_id": "5531", "fields": lda, "layout_matches_generic_5282": True},
            "LTA": {"data_id": "5631", "fields": lta, "layout_matches_generic_5282": True},
            "PDA_OAA": {
                "data_ids": ["5A09", "5A0A", "5A0D"],
                "fields": [pda_id, pda_angle, *pda_gains],
                "layout": "same semantic ingredients but split across three recorder DIDs; lateral ID is 6 bits rather than generic/LDA/LTA 8 bits",
            },
            "LCA": {
                "presence_field": lca_presence,
                "dedicated_request_tuple_rows": [],
                "boundary": "LCA is explicitly present as a feature in DID 5202, but this 1,130-row current recorder dictionary contains no LCA-named lateral-ID/pinion-angle/assist-gain/damping-gain request tuple. This is a recorder-schema negative, not proof that LCA has no internal request path.",
            },
        },
        "arbitration_result": {
            "lateral_id": result_id,
            "pinion_angle": result_angle,
        },
        "shape_equivalence": {
            "generic_5282_equals_lda_5531_equals_lta_5631": True,
            "layout": generic_shape,
            "interpretation": "The current recorder exposes generic, LDA, and LTA request tuples with identical byte/bit/scaling geometry. This supports a normalized arbitration model but does not by itself prove runtime copy direction or ECU ownership.",
        },
    }

def extract(assembly: Path, *, gtsplus_root: Path | None = None) -> dict[str, Any]:
    assembly = assembly.expanduser().resolve()
    gts = resolve_gts_root(gtsplus_root)
    diagnostics = gts.parent
    pcs = diagnostics / "PCS Data Viewer"
    protected = pcs / "PCS Data Viewer.exe"
    sidecar = Path(str(protected) + "._")
    en_us = pcs / "en-US/PCS Data Viewer.resources.dll"

    with contextlib.redirect_stderr(io.StringIO()):
        pe = dnfile.dnPE(str(assembly))
    method_rows = list(pe.net.mdtables.MethodDef.rows)
    raw = assembly.read_bytes()
    body_rvas = [int(row.Rva or 0) for row in method_rows if int(row.Rva or 0)]
    materialized = sum(
        bool((off := pe.get_offset_from_rva(rva)) is not None and any(raw[off : off + 16]))
        for rva in body_rvas
    )
    if materialized != len(body_rvas):
        raise ValueError(f"assembly is not a complete CP recovery: {materialized}/{len(body_rvas)} method bodies materialized")

    _resource_meta, english = load_culture(en_us)
    did_rva, did_records = _interpret_collection(
        pe,
        english,
        define_type=DID_DEFINE,
        record_type=DETAIL_INFO,
        record_fields=DETAIL_FIELDS,
        resource_prefix="FFD_TSS3_ID_",
    )
    rob_rva, rob_records = _interpret_collection(
        pe,
        english,
        define_type=ROB_DEFINE,
        record_type=ROB_INFO,
        record_fields=ROB_FIELDS,
        resource_prefix="FFD_TSS3_TRIGGER_ID_",
    )

    details = []
    for index, record in did_records:
        item = {"index": index, **record}
        details.append(_normalize(item))
    system_types = _enum_literal_map(pe, "SYSTEM_TYPE")
    expected_system_types = {0: "None", 1: "AHBAHS", 2: "LDA", 3: "PCS", 4: "IDA", 5: "URSM", 6: "SDG"}
    if system_types != expected_system_types:
        raise ValueError(f"SYSTEM_TYPE enum drift: {system_types!r}")

    robs = []
    for rob_code, record in rob_records:
        system_type = int(record["SystemType"])
        if system_type not in system_types:
            raise ValueError(f"RoB {rob_code}: unknown SYSTEM_TYPE {system_type}")
        item = {"rob_code": rob_code, **record, "SystemName": system_types[system_type]}
        robs.append(_normalize(item))

    image_ffd = _extract_fcm_image_contract(pe)
    lateral_arbitration = _lateral_arbitration_schema(details)
    system_type_usage = _rob_system_type_usage(pe)

    steering = [item for item in details if item["DataID"] in STEERING_DIDS]
    by_did: dict[str, int] = {}
    for item in details:
        by_did[item["DataID"]] = by_did.get(item["DataID"], 0) + 1

    return {
        "schema": "gtsplus-pcs-data-viewer-tss3-managed-semantics-v1",
        "title": "GTS+ PCS Data Viewer TSS3 managed recorder semantics",
        "sources": {
            "protected_exe": {"path": str(protected.relative_to(diagnostics)), "size": protected.stat().st_size, "sha256": sha256_file(protected)},
            "protected_sidecar": {"path": str(sidecar.relative_to(diagnostics)), "size": sidecar.stat().st_size, "sha256": sha256_file(sidecar)},
            "english_resources": {"path": str(en_us.relative_to(diagnostics)), "size": en_us.stat().st_size, "sha256": sha256_file(en_us)},
            "recovered_analysis_pe_sha256": sha256_file(assembly),
        },
        "recovery_proof": {
            "method_def_count": len(method_rows),
            "method_body_rva_count": len(body_rvas),
            "method_body_materialized_count": materialized,
        },
        "operation_ffd": {
            "detail_table_cctor_rva": did_rva,
            "detail_row_count": len(details),
            "did_count": len(by_did),
            "rows_per_did": dict(sorted(by_did.items())),
            "physical_value_contract": {
                "types": {"u": "unsigned integer", "s": "signed integer", "f": "IEEE-754 single", "d": "IEEE-754 double"},
                "formula": "physical = raw * Lsb + Offset",
                "format": "fixed-point with Point decimal places",
                "source_methods": [
                    "PCSDataViewer.Extractor.OperationFFD.TSS3.Model.MeasuredValue::ConvertPhysicalValue",
                    "PCSDataViewer.Extractor.OperationFFD.TSS3.Model.MeasuredValue::ConvertPhysicalValueOfIntegerType",
                    "PCSDataViewer.Extractor.OperationFFD.TSS3.Model.MeasuredValue::ConvertPhysicalValueOfFloatType",
                    "PCSDataViewer.Extractor.OperationFFD.TSS3.Model.MeasuredValue::ConvertPhysicalValueOfDoubleType",
                    "PCSDataViewer.Extractor.OperationFFD.TSS3.Model.MeasuredValue::ConvertValue",
                ],
            },
            "detail_rows": details,
            "steering_relevant_rows": steering,
            "lateral_arbitration_schema": lateral_arbitration,
        },
        "rob_codes": {
            "table_cctor_rva": rob_rva,
            "row_count": len(robs),
            "system_type_enum": {str(key): value for key, value in system_types.items()},
            "system_type_usage": system_type_usage,
            "rows": robs,
        },
        "image_ffd": {
            "fcm_tss3": image_ffd,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assembly", type=Path, required=True, help="CP-recovered PCS Data Viewer.exe")
    parser.add_argument("--gtsplus-root", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = extract(args.assembly, gtsplus_root=args.gtsplus_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")
    print(
        "operation_rows=" + str(artifact["operation_ffd"]["detail_row_count"])
        + " rob_codes=" + str(artifact["rob_codes"]["row_count"])
        + " materialized=" + str(artifact["recovery_proof"]["method_body_materialized_count"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
