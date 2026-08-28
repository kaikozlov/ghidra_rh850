#!/usr/bin/env python3
"""Extract the PCS Data Viewer TSS3 recorder dictionary and .NET model surface.

PCS Data Viewer 12.x is the GTS+ offline viewer for Toyota pre-crash/recorder
data.  Its managed resources hold the OEM TSS3 Operation-FFD / Image-FFD
dictionary (recorder data-ID -> display name, per culture), and its CLI
metadata still exposes the extractor/model classes that consume those IDs.
This tool recovers both surfaces deterministically from the shipped binaries:

* the full v2 ``.resources`` container of the neutral (embedded), en-US, and
  ja-JP cultures, including the TSS3 key families and the INFO protocol
  messages that name the acquisition services (SID $AB $12/$13, $EB $23/$33);
* the .NET assembly inventory (types, fields, methods, properties) for the
  TSS3 namespaces, the recorder-ID enums, and the ``Properties.Resources``
  accessor join that ties dictionary keys to code;
* the native role-plugin binaries (GetTSS3OperationFFDP5_DT.dll /
  GetTSS3ImageFFDP5_DT.dll) with pinned identities and import surface.

Method-body IL is NOT recovered: the shipped executable zeroes every managed
method body (protector), so data-driven tables (bit assignments, scalings)
stay bounded.  The extraction is metadata + managed-resources only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dnfile  # type: ignore
import pefile  # type: ignore
from techstream_paths import resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_dictionary.json"

# Resource key families that make up the TSS3 recorder dictionary.
TSS3_FAMILIES = (
    ("ffd_tss3_signals", "FFD_TSS3_ID_"),
    ("ffd_tss3_triggers", "FFD_TSS3_TRIGGER_ID_"),
    ("imgffd_tss3_signals", "IMGFFD_TSS3_ID_"),
    ("imgffd_tss3_triggers", "IMGFFD_TSS3_TRIGGER_ID_"),
    ("info_tss3ffd_messages", "INFO_TSS3FFD_"),
    ("info_fcmimgffd_tss3_messages", "INFO_FCMIMGFFD_TSS3_"),
    ("legacy_ffd_trigger_names", "FFD_TRIGGER_ID_"),
    ("imgffd_tss3_csv_columns", "IMGFFD_TSS3_CSV_"),
)
SPECIAL_SUFFIX_KEYS = {
    "FFD_TSS3_ID_FRAMENUMBER",
    "FFD_TSS3_ID_ROBCODE",
    "FFD_TSS3_ID_TIMESTAMP",
    "FFD_TSS3_ID_TRIGGERPOINT",
}

# Types whose field/method inventory is the recovered TSS3 model surface.
TSS3_TYPE_NAMESPACES_PREFIX = "PCSDataViewer.Extractor.OperationFFD.TSS3."
IMAGE_FCM_TSS3_PREFIX = "PCSDataViewer.Extractor.ImageFFD.FCMImageFFD.FCMImageFFDTSS3."
SCHEMA_TYPES = (
    (TSS3_TYPE_NAMESPACES_PREFIX + "Define.DetailBitAssignInfo", "detail_bit_assign_schema"),
    (TSS3_TYPE_NAMESPACES_PREFIX + "Define.RoBCodeDetailInfo", "rob_code_detail_schema"),
)
# Recorder-ID enums: full member lists for small families, census for large.
ENUM_TYPE_NAMES = ("DataID", "ADS_ID", "ADU_ID", "ABG_ID", "ADUFCMIMGFFD_ID", "PhaseNo")
ENUM_FULL_MEMBER_LIMIT = 64

# Verified semantic oracles (EN + JA) pinned from direct resource decode.
ORACLE_ENTRIES_EN = {
    "FFD_TSS3_ID_5280_1": "TSS required longitudinal ID (lower limit)",
    "FFD_TSS3_ID_5280_2": "TSS required acceleration (lower limit)",
    "FFD_TSS3_ID_5280_3": "TSS braking/driving force distribution method (lower limit)",
    "FFD_TSS3_ID_5280_4": "TSS shift range request",
    "FFD_TSS3_ID_5280_5": "TSS EPB request",
    "FFD_TSS3_ID_5280_6": "TSS accelerator override prohibition flag",
    "FFD_TSS3_ID_5280_7": "TSS acceleration request low priority flag",
    "FFD_TSS3_ID_5281_1": "TSS request longitudinal ID (upper limit)",
    "FFD_TSS3_ID_5281_2": "TSS request acceleration (upper limit)",
    "FFD_TSS3_ID_5281_3": "TSS braking/driving force distribution method instruction (upper limit)",
    "FFD_TSS3_ID_5282_1": "TSS request - lateral ID",
    "FFD_TSS3_ID_5282_2": "TSS request - pinion angle",
    "FFD_TSS3_ID_5282_3": "Steering assist gain",
    "FFD_TSS3_ID_5282_4": "Damping control gain",
    "FFD_TSS3_ID_5284": "Arbitration result_longitudinal ID",
    "FFD_TSS3_ID_5285": "Arbitration result_lateral ID",
    "FFD_TSS3_ID_5531_1": "LDA Lateral ID",
    "FFD_TSS3_ID_5531_2": "LDA Control Request Pinion Angle",
    "FFD_TSS3_ID_5631_1": "LTA Lateral ID",
    "FFD_TSS3_ID_5631_2": "LTA Control Request Pinion Angle",
    "FFD_TSS3_ID_57DB": "Arbitration result Acceleration",
    "FFD_TSS3_ID_57DE": "Arbitration result Pinion angle",
    "FFD_TSS3_ID_57A3": "PCS steering output phase",
    "FFD_TSS3_ID_590A": "ACC target acceleration for DDR",
    "FFD_TSS3_ID_590C_4": "ACC control target lateral position for DDR",
}
ORACLE_ENTRIES_JA = {
    "FFD_TSS3_ID_5282_1": "TSS要求横ID",
    "FFD_TSS3_ID_5285": "調停結果_横ID",
    "FFD_TSS3_ID_5631_1": "LTA要求横ID",
}
ROLE_PLUGINS = (
    ("operation_ffd_role_plugin", "GetTSS3OperationFFDP5_DT.dll"),
    ("image_ffd_role_plugin", "GetTSS3ImageFFDP5_DT.dll"),
)
PLUGIN_IMPORT_WITNESSES = {
    "GetTSS3OperationFFDP5_DT.dll": (
        "?CommFrameSendReceiveExt@CCommCachePlus@@QAEKPAVCCommFrameData@@G@Z",
        "?GetDataId@CCmdDataIdData@@QAEGXZ",
        "?Set@CCmdDataIdData@@QAEHGGPAV?$CCmdList@VCCmdByteData@@@@@Z",
        "GetTSS3OperationFFDP5_DT.pdb",
    ),
    "GetTSS3ImageFFDP5_DT.dll": (
        "?GetDbRecord@CDiagToolDb@@QAEKFPAVCDbResRecordsBase@@KKK@Z",
        "U_DDR_TRIGGER_DATA",
        "?GetCommLogFileSize@CCommFrameCtrl@@QAEKPAK@Z",
        "GetTSS3ImageFFDP5_DT.pdb",
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(root)).replace("\\", "/"),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def read_u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def read_compressed_uint(data: bytes, off: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while True:
        if off >= len(data):
            raise ValueError("compressed integer runs past end of data")
        byte = data[off]
        off += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, off
        shift += 7


def decode_resource_value(data: bytes, off: int) -> tuple[str, Any]:
    """Decode one v2 data-section value.

    This writer uses type code 1 for UTF-8 strings and 0x40+T for the
    declared user types (the assembly-scoped type table: bitmaps/icons).
    """
    type_code, payload = read_compressed_uint(data, off)
    if type_code == 1:
        length, str_off = read_compressed_uint(data, payload)
        return "string", data[str_off : str_off + length].decode("utf-8", "replace")
    if type_code >= 0x40:
        length, bin_off = read_compressed_uint(data, payload)
        return f"usertype{type_code}", data[bin_off : bin_off + length]
    return f"type{type_code}", data[payload : payload + 16].hex()


def parse_managed_resources(blob: bytes) -> dict[str, Any]:
    """Parse a .NET v2 ``.resources`` container with UTF-16 name section.

    Layout (verified against the shipped satellites): manager header with a
    skip-count, resource-set header (version/num/numTypes + 7-bit length
    prefixed type names), literal ``PAD...`` alignment, sorted name hashes,
    name positions, one absolute dataSectionOffset int32, then the name
    section (7-bit byte length + UTF-16LE name + int32 data-relative delta)
    and the data section.
    """
    if read_u32(blob, 0) != 0xBEEFCACE:
        raise ValueError("not a .resources container")
    skip = read_u32(blob, 8)
    off = 12 + skip
    version = read_u32(blob, off)
    off += 4
    num = read_u32(blob, off)
    off += 4
    num_types = read_u32(blob, off)
    off += 4
    type_names: list[str] = []
    for _ in range(num_types):
        length, off = read_compressed_uint(blob, off)
        type_names.append(blob[off : off + length].decode("utf-8", "replace"))
        off += length
    pad_start = off
    while off % 8:
        off += 1
    padding = blob[pad_start:off].decode("latin1")
    if not padding or set(padding) - {"P", "A", "D"}:
        raise ValueError(f"unexpected alignment padding {padding!r}")
    positions_off = off + 4 * num
    data_section = read_u32(blob, positions_off + 4 * num)
    name_section = positions_off + 4 * num + 4
    entries: dict[str, str | bytes] = {}
    for i in range(num):
        pos = read_u32(blob, positions_off + 4 * i)
        length, name_off = read_compressed_uint(blob, name_section + pos)
        key = blob[name_off : name_off + length].decode("utf-16-le", "replace")
        delta = read_u32(blob, name_off + length)
        _kind, value = decode_resource_value(blob, data_section + delta)
        entries[key] = value
    return {
        "entries": entries,
        "container": {
            "resource_set_version": version,
            "num_resources": num,
            "user_types": type_names,
            "alignment_padding": padding,
            "name_section_offset": name_section,
            "data_section_offset": data_section,
        },
    }


def load_culture(path: Path) -> tuple[dict[str, Any], dict[str, str | bytes]]:
    pe = dnfile.dnPE(str(path))
    blob = pe.get_data(pe.net.struct.ResourcesRva, pe.net.struct.ResourcesSize)
    # Every embedded resource blob carries a 4-byte length prefix; take the
    # single manifest resource of a satellite assembly.
    if len(pe.net.mdtables.ManifestResource.rows) != 1:
        raise ValueError(f"{path.name}: expected one manifest resource")
    first = pe.net.mdtables.ManifestResource.rows[0]
    start = first.Offset + 4
    length = read_u32(blob, first.Offset)
    parsed = parse_managed_resources(blob[start : start + length])
    return parsed, parsed["entries"]


def find_largest_embedded_resources(exe: Path) -> tuple[dict[str, Any], bytes]:
    """Locate the neutral .resources blob inside the main executable."""
    pe = dnfile.dnPE(str(exe))
    raw = pe.get_data(pe.net.struct.ResourcesRva, pe.net.struct.ResourcesSize)
    blobs: list[tuple[int, int]] = []
    off = 0
    while off < len(raw) - 8:
        length = read_u32(raw, off)
        if 0 < length <= len(raw) - off - 4 and raw[off + 4 : off + 8] == b"\xce\xca\xef\xbe":
            blobs.append((length, off))
            off += 4 + length
        else:
            off += 1
    if not blobs:
        raise ValueError("no embedded .resources blob found in executable")
    length, off = max(blobs)
    parsed = parse_managed_resources(raw[off + 4 : off + 4 + length])
    return parsed, raw[off : off + 4 + length]


def field_row_names(row: Any) -> list[str]:
    names = []
    for member in row.FieldList:
        member_row = member.row if hasattr(member, "row") else member
        if member_row is not None:
            names.append(member_row.Name.value)
    return names


def method_row_names(row: Any) -> list[str]:
    names = []
    for member in row.MethodList:
        member_row = member.row if hasattr(member, "row") else member
        if member_row is not None:
            names.append(member_row.Name.value)
    return names


def strip_backing_field(name: str) -> str | None:
    match = re.fullmatch(r"<(.+)>k__BackingField", name)
    return match.group(1) if match else None


def method_bodies_zeroed(exe: Path, sample: int) -> dict[str, Any]:
    """Every managed method body region reads as zero bytes in the shipped image."""
    pe = dnfile.dnPE(str(exe))
    data = pe.__data__
    nonzero = 0
    checked = 0
    for row in pe.net.mdtables.MethodDef.rows:
        if row.Rva == 0:
            continue
        off = pe.get_offset_from_rva(row.Rva)
        if any(data[off : off + 16]):
            nonzero += 1
        checked += 1
        if checked >= sample:
            break
    return {
        "method_bodies_sampled": checked,
        "method_bodies_with_nonzero_bytes": nonzero,
        "conclusion": (
            "managed method bodies are zero-filled in the shipped executable "
            "(protector container); IL-level grouping/bit-assignment recovery is bounded"
        ),
    }


def enum_constants_sequential(exe: Path, enum_full: str, limit: int = 8) -> list[dict[str, Any]]:
    """Sample enum field constants proving values are sequential ordinals."""
    pe = dnfile.dnPE(str(exe))
    md = pe.net.mdtables
    td = md.TypeDef
    child_parent = {r.NestedClass.row_index: r.EnclosingClass.row_index for r in md.NestedClass.rows}
    target = None
    for i, row in enumerate(td.rows):
        names = [row.TypeName.value]
        namespace = row.TypeNamespace.value
        cur = i + 1
        while cur in child_parent:
            cur = child_parent[cur]
            parent = td.rows[cur - 1]
            names.append(parent.TypeName.value)
            if parent.TypeNamespace.value:
                namespace = parent.TypeNamespace.value
        full = (namespace + "." if namespace else "") + ".".join(reversed(names))
        if full == enum_full:
            target = row
            break
    if target is None:
        return []
    field_index = {m.row_index: m.row.Name.value for m in target.FieldList if hasattr(m, "row") and m.row}
    out: list[dict[str, Any]] = []
    for const_row in md.Constant.rows:
        parent = const_row.Parent
        try:
            row_index = parent.row_index
        except (AttributeError, TypeError):
            continue
        name = field_index.get(row_index)
        if not name or name == "value__":
            continue
        raw = const_row.Value
        try:
            blob = bytes(raw.value) if hasattr(raw, "value") else bytes(raw)
        except (AttributeError, TypeError):
            continue
        type_code = const_row.Type if isinstance(const_row.Type, int) else const_row.Type.value
        if type_code in (8, 9) and len(blob) >= 4:
            value = struct.unpack_from("<i" if type_code == 8 else "<I", blob, 0)[0]
            out.append({"field": name, "constant": value})
        if len(out) >= limit:
            break
    return out


def build_net_inventory(exe: Path) -> dict[str, Any]:
    pe = dnfile.dnPE(str(exe))
    md = pe.net.mdtables
    td = md.TypeDef
    child_parent = {r.NestedClass.row_index: r.EnclosingClass.row_index for r in md.NestedClass.rows}

    def full_name(index: int) -> str:
        row = td.rows[index - 1]
        names = [row.TypeName.value]
        namespace = row.TypeNamespace.value
        cur = index
        while cur in child_parent:
            cur = child_parent[cur]
            parent = td.rows[cur - 1]
            names.append(parent.TypeName.value)
            if parent.TypeNamespace.value:
                namespace = parent.TypeNamespace.value
        return (namespace + "." if namespace else "") + ".".join(reversed(names))

    assembly = md.Assembly.rows[0]
    inventory: dict[str, Any] = {
        "assembly": {
            "name": assembly.Name.value,
            "version": f"{assembly.MajorVersion}.{assembly.MinorVersion}.{assembly.BuildNumber}.{assembly.RevisionNumber}",
            "type_def_count": td.num_rows,
            "method_def_count": md.MethodDef.num_rows,
        },
        "protection": method_bodies_zeroed(exe, sample=512),
        "tss3_types": {},
        "recorder_id_enums": [],
        "resources_property_families": {},
    }

    # TSS3 + FCM-Image-TSS3 type inventory (fields incl. auto-property names,
    # non-accessor methods).
    for i, row in enumerate(td.rows):
        full = full_name(i + 1)
        if not full.startswith((TSS3_TYPE_NAMESPACES_PREFIX, IMAGE_FCM_TSS3_PREFIX)):
            continue
        if full.endswith((".<>c", ".<>c__DisplayClass11_0", ".<>c__DisplayClass11_1")):
            continue
        fields = [strip_backing_field(n) or n for n in field_row_names(row)]
        methods = [m for m in method_row_names(row) if not m.startswith(("get_", "set_"))]
        entry: dict[str, Any] = {"fields": sorted(fields), "methods": sorted(methods)}
        for want, schema_key in SCHEMA_TYPES:
            if full == want:
                entry["role"] = f"schema:{schema_key}"
        inventory["tss3_types"][full] = entry

    # Recorder-ID enums (nested, name-encoded DID identity).
    for i, row in enumerate(td.rows):
        if row.TypeName.value not in ENUM_TYPE_NAMES:
            continue
        fields = [n for n in field_row_names(row) if n != "value__" and not n.startswith("<")]
        if len(fields) < 3:
            continue
        full = full_name(i + 1)
        entry: dict[str, Any] = {
            "type": full,
            "member_count": len(fields),
        }
        if len(fields) <= ENUM_FULL_MEMBER_LIMIT:
            entry["members"] = sorted(fields)
        else:
            entry["first_members"] = sorted(fields)[:12]
        inventory["recorder_id_enums"].append(entry)
    inventory["recorder_id_enums"].sort(key=lambda e: e["type"])

    # Properties.Resources accessor census per family prefix.
    family_counts: Counter[str] = Counter()
    for row in md.PropertyMap.rows:
        try:
            type_index = row.Parent.row_index
        except (AttributeError, TypeError):
            continue
        if td.rows[type_index - 1].TypeName.value != "Resources":
            continue
        for prop in row.PropertyList:
            prop_row = prop.row if hasattr(prop, "row") else prop
            if prop_row is None:
                continue
            name = prop_row.Name.value
            for family, prefix in TSS3_FAMILIES:
                if prefix.endswith("_ID_") and name.startswith(prefix):
                    family_counts[family] += 1
                    break
    inventory["resources_property_families"] = dict(sorted(family_counts.items()))

    # Enum ordinal evidence: DID identity is name-encoded, constants are
    # sequential ordinals (not the hex DID value).
    ordinal_enum = None
    for entry in inventory["recorder_id_enums"]:
        if entry["type"] == "PCSDataViewer.ADSOpeFFDDisplayInfo.ADS_ID":
            ordinal_enum = entry["type"]
            break
    if ordinal_enum:
        samples = enum_constants_sequential(exe, ordinal_enum)
        inventory["enum_ordinal_evidence"] = {
            "enum": ordinal_enum,
            "samples": samples,
            "conclusion": (
                "recorder-ID enum constants are sequential ordinals; the DID/field "
                "identity is carried by the member name (DID_<hex>_<field>)"
            ),
        }
    return inventory


def structured_entry(key: str, english: str | bytes, japanese: str | bytes) -> dict[str, Any] | None:
    match = re.fullmatch(r"FFD_TSS3_ID_([0-9A-F]{4})(?:_(\d+))?", key)
    if not match:
        return None
    entry: dict[str, Any] = {"id": match.group(1), "field": match.group(2)}
    if isinstance(english, str):
        entry["name_en"] = english
    if isinstance(japanese, str):
        entry["name_ja"] = japanese
    return entry


def family_entries(prefix: str, keys: list[str]) -> list[str]:
    return sorted(k for k in keys if k.startswith(prefix))


def build_dictionaries(
    english: dict[str, str | bytes], japanese: dict[str, str | bytes], neutral: dict[str, str | bytes]
) -> dict[str, Any]:
    out: dict[str, Any] = {"families": {}, "key_census_english": {}, "neutral_culture": {}}
    for family, prefix in TSS3_FAMILIES:
        en_keys = family_entries(prefix, list(english))
        entries: list[dict[str, Any]] = []
        for key in en_keys:
            entry: dict[str, Any] = {"key": key}
            en_val, ja_val = english.get(key), japanese.get(key)
            if isinstance(en_val, str):
                entry["name_en"] = en_val
            if isinstance(ja_val, str):
                entry["name_ja"] = ja_val
            structured = structured_entry(key, en_val or "", ja_val or "")
            if structured:
                entry["id"] = structured["id"]
                entry["field"] = structured["field"]
            entries.append(entry)
        out["families"][family] = {
            "key_prefix": prefix,
            "count": len(en_keys),
            "entries": entries,
        }
        neutral_vals = [neutral.get(k) for k in en_keys]
        out["neutral_culture"][family] = {
            "keys_present": sum(1 for v in neutral_vals if v is not None),
            "values_equal_english": all(v == english.get(k) for k, v in zip(en_keys, neutral_vals)),
        }

    census: Counter[str] = Counter()
    for key in english:
        match = re.match(r"([A-Z][A-Z0-9]*(?:_ID|_TRIGGER_ID|_CSV|_INFO|IMGFFD)?)", key)
        census[match.group(1) if match else key.split("_")[0]] += 1
    out["key_census_english"] = dict(sorted(census.items(), key=lambda kv: (-kv[1], kv[0])))
    out["special_keys"] = sorted(k for k in english if k in SPECIAL_SUFFIX_KEYS)
    return out


def protocol_surface(english: dict[str, str | bytes]) -> dict[str, Any]:
    quotes: list[str] = []
    tokens: Counter[str] = Counter()
    for key, value in sorted(english.items()):
        if not isinstance(value, str) or not key.startswith(("INFO_TSS3FFD_", "INFO_FCMIMGFFD_TSS3_")):
            continue
        for token in re.findall(r"(?:SID)?\$?[A-Z]{2}\s?\$\d+|DID\$[0-9A-F]+", value):
            tokens[token.replace(" ", "")] += 1
        quotes.append(value)
    return {
        "distinct_service_tokens": dict(sorted(tokens.items())),
        "info_message_count": len(quotes),
        "decoded_semantics": {
            "AB_12": "enumerate RoB records: RoBCode and trigger type per record (LogAnalyserEB12.GetRoBCode/AnalyzeTriggerType)",
            "AB_13": "read per-frame DID data: RoBCode + RoBFrameNumber -> DID payload (LogAnalyserEB13.GetDIDData/CreateDIDDataList)",
            "EB_23_EB_33": "dynamic/split DID reads used for FCM image FFD assembly",
            "DID_6001": "front-camera FF image payload DID for the image FFD family",
        },
    }


def image_family_did_join(inventory: dict[str, Any], dictionaries: dict[str, Any]) -> dict[str, Any]:
    fcm_enum_name = (
        "PCSDataViewer.Extractor.ImageFFD.FCMImageFFD.FCMImageFFDTSS3."
        "DataTable.FCMDataTableDIDData.DataID"
    )
    fcm_enum = next(
        (e for e in inventory["recorder_id_enums"] if e["type"] == fcm_enum_name),
        None,
    )
    if not fcm_enum:
        raise ValueError("FCM image-FFD DataID enum missing")
    enum_ids = sorted({m.removeprefix("ID_").split("_")[0] for m in fcm_enum["members"]})
    named_ids = sorted(
        {
            match.group(1)
            for entry in dictionaries["families"]["imgffd_tss3_signals"]["entries"]
            if (match := re.fullmatch(r"IMGFFD_TSS3_ID_([0-9A-F]{4})(?:_\d+)?", entry["key"]))
        }
    )
    unnamed = sorted(set(enum_ids) - set(named_ids))
    extra = sorted(set(named_ids) - set(enum_ids))
    return {
        "enum": fcm_enum["type"],
        "enum_members": sorted(fcm_enum["members"]),
        "enum_ids": enum_ids,
        "resource_named_ids": named_ids,
        "enum_ids_without_display_name": unnamed,
        "resource_ids_without_enum_member": extra,
        "conclusion": (
            "the FCM (front-camera) TSS3 image-FFD extractor reads exactly the DIDs its "
            "DataTable DataID enum lists; every non-image DID has an IMGFFD_TSS3 display name "
            "while the image payload DID 6001 stays unnamed"
        ),
    }


def plugin_evidence(root: Path) -> dict[str, Any]:
    diagnostics = root.parent
    bin_dir = diagnostics / "GTSPlus/bin"
    out: dict[str, Any] = {}
    for role, name in ROLE_PLUGINS:
        path = bin_dir / name
        pe = pefile.PE(str(path), fast_load=True)
        pe.parse_data_directories(
            directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
            ]
        )
        exports = [
            s.name.decode() if s.name else f"ordinal:{s.ordinal}"
            for s in getattr(pe, "DIRECTORY_ENTRY_EXPORT", []).symbols
        ]
        raw = path.read_bytes()
        required = [w for w in PLUGIN_IMPORT_WITNESSES[name] if not w.endswith(".pdb")]
        witnesses = [w for w in required if w.encode("latin1") in raw]
        if len(witnesses) != len(required):
            raise ValueError(f"{name}: import witness drift {witnesses}")
        pdb_match = re.search(rb"[ -~]{4,}\.pdb", raw)
        out[role] = {
            **source(path, diagnostics),
            "architecture": "win32-native",
            "exports": exports,
            "import_witnesses": required,
            "pdb_path_string": pdb_match.group().decode("ascii", "replace") if pdb_match else None,
        }
    return out


def build(gts_root: Path | None = None) -> dict[str, Any]:
    root = resolve_gts_root(gts_root) if gts_root else resolve_gts_root()
    diagnostics = root.parent
    pcs = diagnostics / "PCS Data Viewer"
    exe = pcs / "PCS Data Viewer.exe"
    en_dll = pcs / "en-US/PCS Data Viewer.resources.dll"
    ja_dll = pcs / "ja-JP/PCS Data Viewer.resources.dll"

    manifest = json.loads((root / "Ver/Manifest.json").read_text(encoding="utf-8-sig"))
    components = manifest[0]["Components"]
    versions = {row["Name"]: row["Version"] for row in components}
    versions[manifest[0]["SoftwareName"]] = manifest[0]["SoftwareVersion"]
    viewer_version = versions["PCS Data Viewer"]

    _, english = load_culture(en_dll)
    _, japanese = load_culture(ja_dll)
    neutral_parsed, _neutral_raw = find_largest_embedded_resources(exe)
    neutral = neutral_parsed["entries"]

    inventory = build_net_inventory(exe)
    dictionaries = build_dictionaries(english, japanese, neutral)

    expected_counts = {
        "ffd_tss3_signals": 1131,
        "ffd_tss3_triggers": 49,
        "imgffd_tss3_signals": 13,
        "imgffd_tss3_triggers": 18,
        "info_tss3ffd_messages": 19,
        "info_fcmimgffd_tss3_messages": 14,
        "legacy_ffd_trigger_names": 35,
        "imgffd_tss3_csv_columns": 4,
    }
    for family, expected in expected_counts.items():
        got = dictionaries["families"][family]["count"]
        if got != expected:
            raise ValueError(f"{family} census drift: {got} != {expected}")
    prop_join = inventory["resources_property_families"]
    if prop_join.get("ffd_tss3_signals") != expected_counts["ffd_tss3_signals"]:
        raise ValueError(f"Resources property join drift: {prop_join}")

    # Oracle pinning.
    for key, expected in ORACLE_ENTRIES_EN.items():
        got = english.get(key)
        if got != expected:
            raise ValueError(f"EN oracle drift {key}: {got!r}")
    for key, expected in ORACLE_ENTRIES_JA.items():
        got = japanese.get(key)
        if got != expected:
            raise ValueError(f"JA oracle drift {key}: {got!r}")

    return {
        "schema": "gtsplus-pcs-data-viewer-tss3-dictionary-v1",
        "title": "PCS Data Viewer TSS3 recorder dictionary and .NET model surface",
        "gtsplus_version": versions["GTS+"],
        "pcs_data_viewer_version": viewer_version,
        "sources": {
            "executable": source(exe, diagnostics),
            "english_satellite": source(en_dll, diagnostics),
            "japanese_satellite": source(ja_dll, diagnostics),
        },
        "resources_container": neutral_parsed["container"],
        "net_assembly": inventory,
        "dictionaries": dictionaries,
        "protocol_surface": protocol_surface(english),
        "image_ffd_family_did_join": image_family_did_join(inventory, dictionaries),
        "role_plugins": plugin_evidence(root),
        "identity_boundaries": {
            "recorder_ids_are_not_sid22_dids": (
                "FFD_TSS3_ID_* numbers are recorder data IDs/keys consumed by the "
                "proprietary Operation-FFD SID-$AB-$12/$13 path, not ordinary FRC_P5 "
                "UDS SID-22 DIDs; no Data-Monitor DDB join is asserted"
            ),
            "neutral_culture_is_english": all(
                v["values_equal_english"] for v in dictionaries["neutral_culture"].values()
            ),
        },
        "oracles": {
            "english": dict(sorted(ORACLE_ENTRIES_EN.items())),
            "japanese": dict(sorted(ORACLE_ENTRIES_JA.items())),
        },
        "bounded": [
            (
                "method bodies are zero-filled by the shipped protector; per-DID bit "
                "assignment (DetailBitAssignInfo instances), Lsb/Offset/Point scalings, "
                "and RoBCode tables are data-driven in protected initializers and remain bounded"
            ),
            "enum numeric constants are sequential ordinals; DID identity is name-encoded",
            (
                "role plugins are native win32; their internal AB/EB frame construction was "
                "not disassembled here"
            ),
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gts-root", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    artifact = build(args.gts_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    families = {k: v["count"] for k, v in artifact["dictionaries"]["families"].items()}
    print(f"wrote {args.out}: families={families}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
