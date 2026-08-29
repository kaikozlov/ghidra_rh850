#!/usr/bin/env python3
"""Extract TSS3 managed recorder tables from a CP-recovered PCS Data Viewer PE.

The shipped PCS Data Viewer.exe intentionally has zeroed managed method bodies.
Run ``tools/gts recover-aux-bodies`` (or ``recover-all-bodies``) first, then
point this extractor at the recovered PE.  It interprets only the straight-line
static-constructor subset needed for Toyota's Operation-FFD TSS3 definition
objects; it is not a general CLR interpreter.
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
DETAIL_FIELDS = (
    "DataName", "DataID", "DataSize", "SupportDID", "BytePosition", "BitPosition",
    "BitLength", "InvalidValueList", "Type", "Lsb", "Offset", "Point",
)
ROB_FIELDS = (
    "DataName", "SystemType", "Group", "Sampling", "PreTriggerNumber",
    "PostTriggerNumber", "IsMultiTrigger", "UniqueRoBCodeDID",
)
STEERING_DIDS = {"5282", "5285", "5531", "560D", "5631", "5681", "568D", "57A3", "57DE", "590C"}


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
    robs = []
    for rob_code, record in rob_records:
        item = {"rob_code": rob_code, **record}
        robs.append(_normalize(item))

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
        },
        "rob_codes": {
            "table_cctor_rva": rob_rva,
            "row_count": len(robs),
            "rows": robs,
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
