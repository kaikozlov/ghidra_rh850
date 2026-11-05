#!/usr/bin/env python3
"""Extract byte-pinned current P6 Data List admission, metadata, and live-reader evidence.

Offline research only: regional counts and compact exact DDB witnesses are not a
runtime monitor catalog. Run recovery separately and supply --recovered-root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path
from typing import Any

import pefile  # type: ignore

from tools import REPO_ROOT
from tools.techstream.ddb_semantics import (
    NativeSelectionError, UnresolvedNativeContext, extract_monitor_records, extract_msb0,
    format_p5_decimal, native_context, records, resolve_frame_program, select_for_consumer,
)
from tools.techstream.ddb_strings import load_string_db
from tools.techstream.gts.master import _master_variable
from tools.techstream.gts.support import support_plugin
from tools.techstream.parse_ddb import DDBParser
from tools.techstream.techstream_paths import gts_db_root, resolve_gts_root
from tools.techstream.recover_all_gtsplus_bodies import DEFAULT_OUTPUT, qualify_recovered_source

DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/p6_data_list_semantics.json"
DEFAULT_RECOVERED = DEFAULT_OUTPUT / "GTSPlus"
REGIONS = ("NA", "EU", "JP")
WITNESSES = ("ADCU_P6.ddb", "Engine_CM_P6.ddb")

# Exact current-release images, not similarly named P5 predecessors or CP stubs.
SOURCE_SHA256 = {'GetDatMonListP6_DT.dll': 'd5a7c02603373d5b3b986856be42281375151d502e0adfa1d395f79c53582b7f',
 'GetDatMonSignalInfoP6_DT.dll': '014d5a6eeeb34247bb65c9f117408a56a2793930aa5ba493b0a90e3187863990',
 'GetDatMonListP5_DT.dll': '8db35a64b020a18b14f361e3fbb4f7375fc9a35293abb4b62f7a00e7c6a3a07c',
 'CommandCommon.dll': '98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3',
 'DataMonitorPhase6_DT.dll': '45633f2c6b2a1540e736cb55cf2374922bb97f97f516690d9b2c2cb710985eeb',
 'DataListIF.dll': 'cce3ecd1203f81914c51d5b2599ee68eb4f7faafa8cbd9bb24fd7390b54d651d',
 'CommandDataLib.dll': 'ffce12af45554a552dbf616545c4c4e02780702e4cb9e2c6f8235ff4f05c79ab',
 'DatMonCommon.dll': '5f244b62937aa646eda6c145eff7dfdf64a6135ebc69d179e4b9f9481dcc7090'}

# Ghidra function body extents, after decompilation and branch/disassembly review.
FUNCTIONS = {
    'GetDatMonListP6_DT.dll': {
        'composite_membership': (0x100013B0, 525),
        'execute': (0x100015C0, 798),
        'select_supported_rows': (0x10001A90, 920),
        'admit_composites': (0x10001E30, 830),
        'merge_original_order': (0x10002290, 905),
        'emit_metadata': (0x10002730, 1402),
    },
    'GetDatMonSignalInfoP6_DT.dll': {
        'metadata_joins': (0x10001000, 966),
        'execute': (0x100013E0, 1464),
    },
    'GetDatMonListP5_DT.dll': {
        'current_p5_list_caller': (0x10001AB0, 1122),
    },
    'CommandCommon.dll': {
        'enabled_bitmap': (0x100678D0, 206),
        'enabled_dids': (0x100679A0, 843),
        'shared_field_admission': (0x10072180, 3014),
        'cross_did_support': (0x10070AC0, 749),
        'cross_did_comparison': (0x10071A80, 871),
        'lsb_gate': (0x100142C0, 60),
        'lsb_metadata': (0x10014930, 535),
        'lsb_support': (0x10014300, 143),
        'lsb_support_list': (0x10014420, 150),
        'lsb_init': (0x10014B50, 175),
        'lsb_fetch': (0x100144C0, 588),
        'lsb_physical_max': (0x10014390, 143),
    },
    'DataMonitorPhase6_DT.dll': {
        'make_assembler': (0x10006590, 58),
        'assemble_p6': (0x10006E60, 910),
        'select_live_dids': (0x100076B0, 1429),
        'direct_did_schedule': (0x100083A0, 967),
        'define_dynamic_dids': (0x100067B0, 1615),
        'probe_dynamic_dids': (0x10007C50, 1867),
    },
    'DataListIF.dll': {
        'live_did_setup': (0x10042450, 486),
        'live_receive': (0x10042020, 572),
        'zero_receive_buffer': (0x100423E0, 98),
    },
    'CommandDataLib.dll': {
        'basic_conversion': (0x10022AC0, 153),
        'conversion_table': (0x10022C20, 38),
        'converted_pattern': (0x10022910, 112),
    },
    'DatMonCommon.dll': {
        'extract_value': (0x100033C0, 321),
        'convert_value': (0x10003680, 111),
    },
}

# Decisive instruction windows, checked in addition to each complete source hash.
ANCHORS = {
    "GetDatMonListP6_DT.dll": {
        "composite_vs_single": (0x10001D0B, "a810740ca8017459", "flags10 selects composites; flags1 makes them list candidates"),
    },
    "CommandCommon.dll": {
        "p6_support_selector": (0x10067AD0, "68c8000000", "GetCommFrmInfo selectorC8"),
        "short_field_gate": (0x10072620, "0fb7503e8bc1c1e0038bca3bc10f86c7010000", "endbit must be strictly below payload_length*8"),
        "support_modes": (0x1007291E, "0fb6400683e800744883e801740a83e801743e", "type61+6 modes0/2 pass;1 checks mask"),
        "preceding_byte_mask": (0x10072936, "c1ea038d04d5000000002bc8b880000000d3f8", "mask80>>(endbit&7), byte(endbit>>3)+2 in response"),
        "row_override": (0x10072CB2, "0fb6404b83e800741d83e801740b", "row+4B zero preserves,one enables,other disables"),
    },
    "DataMonitorPhase6_DT.dll": {
        "assembler_dispatch": (0x1000659F, "c70634970110", "current CAssembleFrameP6 vtable10019734; slot7C points100083A0"),
    },
    "DataListIF.dll": {
        "request_sid_did": (0x10042567, "c600228b47288b0e0fb64458018841018b47288b0e0fb60458884102", "22 then big-endian DID; linked request length3"),
        "short_data_copy": (0x10042059, "8b450c83c2030fb74e5883c0fd530fb7d88b462c578b7e5c0fb704488b4e50663bc37203", "copy minimum of u16(rxlen-3) and expected length"),
    },
    "CommandDataLib.dll": {
        "division_gate": (0x10022B35, "8b451483f8017612", "unsigned divisor<=1 skips division"),
    },
}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(), "size": len(data), "sha256": digest(data)}


def u16(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<H", raw, offset)[0]


def u32(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<I", raw, offset)[0]


def table_rows(db: Any, table: int) -> list[bytes]:
    return list(records(db.sections[table])) if table in db.sections else []


def native_sources(gts: Path, recovered: Path) -> dict[str, Any]:
    out = {}
    for filename, functions in FUNCTIONS.items():
        source_root = recovered if filename == "CommandCommon.dll" else gts
        path = source_root / "bin" / filename
        qualification = (
            qualify_recovered_source(path, gts / "bin" / filename, component_root=recovered)
            if filename == "CommandCommon.dll" else None
        )
        data = path.read_bytes()
        if digest(data) != SOURCE_SHA256[filename]:
            raise ValueError(f"current-release PE identity mismatch: {filename}")
        pe = pefile.PE(data=data)
        base = int(pe.OPTIONAL_HEADER.ImageBase)
        imports = {
            int(symbol.address): {"dll": entry.dll.decode("ascii"), "name": symbol.name.decode("ascii")}
            for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", [])
            for symbol in entry.imports if symbol.name
        }
        bodies = {}
        for role, (va, size) in functions.items():
            body = pe.get_data(va - base, size)
            if len(body) != size:
                raise ValueError(f"unmaterialized body: {filename}:{va:#x}")
            # Restrict indirect import edges to the exact pinned function bytes.
            calls = []
            for offset in range(len(body) - 5):
                if body[offset:offset + 2] != b"\xff\x15":
                    continue
                address = u32(body, offset + 2)
                if address in imports:
                    calls.append({"va": f"0x{va + offset:08X}", "iat_va": f"0x{address:08X}", **imports[address]})
            bodies[role] = {"va": f"0x{va:08X}", "rva": f"0x{va - base:X}", "size": size,
                            "sha256": digest(body), "bytes": body.hex(), "import_calls": calls}
        anchors = {}
        for role, (va, expected_hex, derivation) in ANCHORS.get(filename, {}).items():
            expected = bytes.fromhex(expected_hex)
            actual = pe.get_data(va - base, len(expected))
            if actual != expected:
                raise ValueError(f"native anchor drift: {filename}:{va:#x}")
            anchors[role] = {"va": f"0x{va:08X}", "rva": f"0x{va - base:X}",
                             "bytes": actual.hex(), "derivation": derivation}
        out[filename] = {**identity(path, source_root), "materialization": "installer plaintext twin" if filename == "CommandCommon.dll" else "installed PE",
                         "functions": bodies, "anchors": anchors}
        if qualification is not None:
            out[filename]["qualification"] = qualification
    common = gts / "bin/CommandCommon.dll"
    sidecar = gts / "bin/CommandCommon.dll._"
    if digest(common.read_bytes()) != "89fe3c1f17d7ec58e659a099fc4fc96b55d30534d813c2a4c26211c4d30284c2":
        raise ValueError("installed CommandCommon CP stub differs from analyzed release")
    if digest(sidecar.read_bytes()) != "2fd7211088bee794d56239d3f2960d03f5747dbe7c20097fca6c34559f80d6da":
        raise ValueError("installed CommandCommon CP sidecar differs from analyzed release")
    out["CommandCommon.dll"]["installed_protected_sources"] = [identity(common, gts), identity(sidecar, gts)]
    out["CommandCommon.dll"]["provenance"] = {
        "installer": "Setup_PF.exe", "version": "2026.03.002.02",
        "source_archive_sha256": "fb65ac31b1c0a0c1b28d53af8cf540d12eb46d77ba1e6645a014473352ce00c4",
        "method": "qualified aggregate GTSPlus component; exact source-relative output and installed protected-pair manifest match",
    }
    return out


def support_bitmap(base: int, payload: bytes) -> list[int]:
    """Express the P6 mode-zero AnalyzeFrameData used by enabled-DID acquisition."""
    return [(base + index * 8 + bit) & 0xFFFF
            for index, value in enumerate(payload[:32]) for bit in range(8)
            if value & (0x80 >> bit)]


def scalar_conversion(value: int, width: int, physical: bytes) -> int:
    """Express the basic CComDataConvert overload, with native 32-bit result."""
    mode = physical[0x14]
    value &= 0xFFFFFFFF
    if mode == 1 and value & (1 << ((width - 1) & 31)):
        value |= (-1 << ((width - 1) & 31))
    elif mode == 3 and value & (1 << ((width - 1) & 31)):
        value = -(value & ((1 << ((width - 1) & 31)) - 1))
    mul, div, offset = struct.unpack_from("<iii", physical)
    numerator = value * mul
    if (div & 0xFFFFFFFF) > 1:
        quotient = abs(numerator) // abs(div)
        numerator = -quotient if (numerator < 0) != (div < 0) else quotient
    result = (numerator + offset) & 0xFFFFFFFF
    return result - (1 << 32) if result & 0x80000000 else result


def joined_witness(db: Any, master: Any, strings: Any, record: Any, reasons: list[str]) -> dict[str, Any]:
    raw = record.raw
    did = record.primary_did
    wire_field = not (record.flags & (0x08 | 0x10)) and did != 0
    did_row = next((x for x in table_rows(db, 61) if u16(x, 2) == did), None)
    physical = next((x for x in table_rows(db, 13) if u16(x, 0x0C) == record.physical_data_key), None)
    unit = None if physical is None else next((x for x in table_rows(db, 15) if u16(x, 4) == u16(physical, 0x0E)), None)
    patterns = [x for x in table_rows(db, 14) if u16(x, 0x0C) == record.pattern_display_key] if record.pattern_display_key else []
    condition_key = u16(raw, 0x36)
    condition = next((x for x in table_rows(db, 63) if u16(x, 0) == condition_key), None) if condition_key else None
    result: dict[str, Any] = {
        "selection_reasons": reasons, "table": 62, "record": record.index, "raw": raw.hex(),
        "name_string_index": record.name_string_index, "name": strings.get_string(record.name_string_index),
        "monitor_key": record.monitor_key, "flags": u32(raw, 0x30), "live_override": raw[0x4B],
        "live_support_condition_key": condition_key, "snapshot_support_condition_key": record.ffd_support_condition_key,
        "primary_did": f"0x{did:04X}", "snapshot_did": f"0x{record.alternate_did:04X}",
        "bits": [record.bit_start, record.bit_end], "extraction_mode": raw[0x4A],
        "physical_range": list(reversed(struct.unpack_from("<dd", raw, 0))),
        "graph_range": [struct.unpack_from("<i", raw, 0x18)[0], struct.unpack_from("<i", raw, 0x14)[0]],
        "physical_key": record.physical_data_key, "pattern_key": record.pattern_display_key,
        "request": (b"\x22" + did.to_bytes(2, "big")).hex() if wire_field else None,
        "positive_header": (b"\x62" + did.to_bytes(2, "big")).hex() if wire_field else None,
        "wire_field": wire_field,
        "data_id_row": None if did_row is None else {"table": 61, "raw": did_row.hex(), "declared_length": u16(did_row, 4), "support_mode": did_row[6]},
        "physical_row": None, "unit_row": None, "patterns": [], "live_condition": None,
        "composite_rows": [x.hex() for x in table_rows(db, 26) if u16(x, 0) == record.monitor_key],
        "native_derivation": "GetDatMonListP6 10001A90/10002730; GetDatMonSignalInfoP6 10001000; shared admission CommandCommon 10072180",
    }
    if physical is not None:
        result["physical_row"] = {"table": 13, "raw": physical.hex(), "mul": struct.unpack_from("<i", physical, 0)[0],
                                  "div": struct.unpack_from("<i", physical, 4)[0], "offset": struct.unpack_from("<i", physical, 8)[0],
                                  "unit_key": u16(physical, 0x0E), "sign_mode": physical[0x14], "decimal_precision": physical[0x15]}
    if unit is not None:
        result["unit_row"] = {"table": 15, "raw": unit.hex(), "text": strings.get_string(u32(unit, 0)), "genre": u16(unit, 6)}
    result["patterns"] = [{"table": 14, "raw": x.hex(), "value": struct.unpack_from("<i", x, 4)[0], "text": strings.get_string(u32(x, 0))} for x in patterns]
    if condition is not None:
        variable = _master_variable(master, u16(condition, 2))
        result["live_condition"] = {"table": 63, "raw": condition.hex(), "variable": variable,
                                    "referenced_did": f"0x{int.from_bytes(bytes.fromhex(variable['bytes']), 'big'):04X}",
                                    "bits": [u16(condition, 6), u16(condition, 8)], "comparison_value": u16(condition, 10),
                                    "condition_type": condition[0x0D], "comparison_mode": condition[0x0E]}
    # Analytical wire examples use actual DDB geometry. They are not ECU captures.
    if wire_field and physical is not None and 0 <= record.bit_start <= record.bit_end < 32 and raw[0x4A] in (1, 2):
        size = record.bit_end // 8 + 1
        payload = bytes([0x55] * size)
        extracted = extract_msb0(payload, record.bit_start, record.bit_end)
        converted = scalar_conversion(extracted, record.bit_end - record.bit_start + 1, physical)
        result["analytical_value_example"] = {"provenance": "constructed input, not a vehicle observation",
                                               "response": result["positive_header"] + payload.hex(), "value_payload": payload.hex(),
                                               "extracted": extracted, "converted_integer": converted,
                                               "decimal_value": format_p5_decimal(converted, physical[0x15]),
                                               "matching_patterns": [x["text"] for x in result["patterns"] if x["value"] == converted]}
    return result


def db_census(db: Any) -> dict[str, Any]:
    rows = extract_monitor_records(db.sections[62]) if 62 in db.sections else []
    return {
        "tables": {str(t): {"count": db.sections[t].header.record_count, "record_size": db.sections[t].decoded_record_size}
                   for t in (13, 14, 15, 26, 61, 62, 63, 64, 156, 157) if t in db.sections},
        "rows62": len(rows), "visible_candidates": sum(bool(x.flags & 1) for x in rows),
        "composite_rows": sum(bool(x.flags & 0x10) for x in rows),
        "live_conditioned_rows": sum(u16(x.raw, 0x36) != 0 for x in rows),
        "flags": dict(sorted(Counter(u32(x.raw, 0x30) for x in rows).items())),
        "override_modes": dict(sorted(Counter(x.raw[0x4B] for x in rows).items())),
        "did_support_modes": dict(sorted(Counter(x[6] for x in table_rows(db, 61)).items())),
        "extraction_modes": dict(sorted(Counter(x.raw[0x4A] for x in rows).items())),
        "physical_sign_modes": dict(sorted(Counter(x[0x14] for x in table_rows(db, 13)).items())),
        "dynamic_lsb_rows": len(table_rows(db, 64)),
    }


def select_witnesses(db: Any, master: Any, strings: Any) -> list[dict[str, Any]]:
    rows = extract_monitor_records(db.sections[62])
    modes = {u16(x, 2): x[6] for x in table_rows(db, 61)}
    criteria = {
        "first_row": lambda x: True,
        "ordinary_visible": lambda x: bool(x.flags & 1) and x.raw[0x4B] == 0,
        "force_visible": lambda x: x.raw[0x4B] == 1,
        "force_hidden": lambda x: x.raw[0x4B] == 2,
        "support_mask": lambda x: modes.get(x.primary_did) == 1 and x.raw[0x4B] == 0,
        "mode2": lambda x: modes.get(x.primary_did) == 2,
        "cross_did_condition": lambda x: u16(x.raw, 0x36) != 0,
        "composite": lambda x: bool(x.flags & 0x10),
        "pattern_join": lambda x: x.pattern_display_key != 0,
        "signed_conversion": lambda x: any(u16(p, 0x0C) == x.physical_data_key and p[0x14] != 0 for p in table_rows(db, 13)),
    }
    chosen: dict[int, list[str]] = {}
    for name, predicate in criteria.items():
        match = next((x for x in rows if predicate(x)), None)
        if match is not None:
            chosen.setdefault(match.index, []).append(name)
    return [joined_witness(db, master, strings, rows[index], reasons) for index, reasons in sorted(chosen.items())]


CONTRACTS = {
    "selection": {
        "native": "GetDatMonListP6_DT 10001A90/100015C0/10001E30/100013B0/10002290",
        "row_source": "0x23E/type62 only; no union with type157 or type156",
        "ordinary": "flags+30&10==0: shared CheckSupportPid(..., apply_override=1); supported rows become dependency pool; flags&1 additionally emits them",
        "composite": "flags&10 and flags&1: type26/0x21A dependencies must exist in type62; every dependency must be supported or type26+9==1; merge by original type62 row index",
        "current_p5_comparison": "Current GetDatMonListP5 10001AB0 and P6 10001A90 both call CCommCachePlusP5::CheckSupportPid. P5 uses CCmdSupportDataIdList (and manufacturer branches), P6 uses distinct CCmdSupportDataIdListP6. P5 list selects type157 for category+48&E0==60; P6 list enumerates type62 unconditionally.",
    },
    "enabled_dids": {
        "native": "CommandCommon 100679A0/100678D0",
        "first": "selector C8: 22 A1 00 -> 62 A1 00 || bitmap; consume at most32 payload bytes from offset3",
        "first_bitmap": "MSB0 set bit i adds A100+i (no P5 +1 bias)",
        "second": "iterate initial A1xx list; skip A1FD/A1FE; send22 A1 xx; MSB0 set bit i adds (xx<<8)+i, at most32 bytes",
        "cache": "per category, share-data slot22; failed/empty first acquisition still caches resulting list and returns success; follow-up failures do not erase earlier enabled DIDs",
    },
    "field_admission": {
        "native": "CommandCommon 10072180/10070AC0/10071A80; disassembly10072612/10072903/10072CAA",
        "base": "require primaryDID+46 in enabled list; normal P6(category16) reads selectorCA with22 DIDbe16; failed read hides; response<=3 hides; require end_bit+3E < (rxlen-3)*8",
        "support_mode": "type61+6:0 or2 passes length gate;1 additionally requires response[(end_bit>>3)+2] & (80>>(end_bit&7)); this is the preceding value-payload byte, not the field value",
        "cross_did": "monitor+36 ->type63; condition-type+0D must7; variable+2 gives a two-byte big-endian DID read through selectorC9; bits+6/+8 MSB0; comparison_mode+0E:0 nonzero bits,1 equals u16+0A,2 not-equals. Comparison modes1/2 verify referenced signal support and are re-evaluated after cache hits",
        "override": "after normal admission/caching, apply_override==1: monitor+4B==0 preserves,1 forces visible, every other nonzero forces hidden",
        "manufacturer_boundary": "shared checker chooses type157 only(category+48&E0)==60; low5bits15 and manufacturer60 use cached lengths and bypass normal support-mask branch. Current P6 role bindings and category raw bytes are retained separately.",
    },
    "metadata": {
        "native": "GetDatMonSignalInfoP6 10001000/100013E0; list10002730; CommandCommon100142C0/10014930/100144C0",
        "joins": "monitor+3A -> type13 key+C; physical+E -> type15 key+4; monitor+42 -> type14 key+C",
        "conversion": "physical+0/+4/+8 signed32 mul/div/offset; +14 sign-mode, +15 decimal precision; width=end-start+1; unit+6 genre; type14+4 pattern compares converted integer",
        "basic_integer": "CommandDataLib10022AC0: mode0 unsigned,1 twos-complement,3 sign-magnitude; signed64 product; unsigned(div)<=1 bypasses division, otherwise signed truncation toward zero; low32 result plus offset; decimal precision is separate",
        "packet_reader": "DatMonCommon100033C0 assembles covered bytes big-endian then shift/mask/subtracts pickup offset;10003680 forwards installed conversion to CComDataConvert special-format overload. Packet framing+4 is not a DID payload offset.",
        "dynamic_lsb": "only category+48&1F==16; querytype64 by monitor; absent table leaves static conversion. Existing table uses DID+8/bits+C,+E; read22 DID through CA; nonzero extracted slope is multiplied by row+0 and10^precision, divided by row+4, reduced by GCD; metadata overload also recomputes maximum in physical units with offset/10^precision. No type64 in applicable regional corpus.",
        "dynamic_lsb_support": "10014420 uses the base CCmdSupportDataIdList::CreateEnableDataIdList;10014300 then checks its DID membership and invokes the same shared CheckSupportPid(...,1). This differs from ordinary P6-list enabled-DID acquisition.",
        "metadata_error_policy": "role41 treats missing physical/unit or nonzero pattern-key without rows as errors; list role05 tolerates absent physical row with identity mul/div=1 and offset=0",
    },
    "live_reader": {
        "native": "DataMonitorPhase6 10006590/10006E60/100076B0/100083A0; DataListIF10042450/100423E0/10042020",
        "selection": "current CAssembleFrameP6 selected rows read type62, primaryDID+46,bits+3C/+3E,override+4B,flags+30; excludes flags&8 voltage path; deduplicates DIDs and expected length=max(end_bit>>3)+1; unsupported DID requires override1 or optional membership handling",
        "direct_request": "DataListIF CCommEventPhase6DM::DataidSetup emits a linked list of separate22 DIDbe16 requests, exactly3 bytes each; no inline-length field, no bundled DID request",
        "response": "CheckRcvFrame SID62 copies min(u16(rxlen-3),expected_length) bytes from offset3, advances by expected_length, concatenates slots in scheduled order; zero-initialized and cycle-cleared buffer retains zero padding for short data and discards excess. This method checks SID, not returned DID equality.",
        "dynamic_path": "optional P6 assembler probes selectorD4 and defines selectorD3: writes target dynamicDID at2/3, appends[sourceDIDbe16,position_u8,length_u8] for contiguous requested byte runs; validates resulting DID withCA. Scheduling falls back to directDID reads for remaining entries. ADCU/Engine templates are retained without inventing absent selectors.",
        "boundary": "host Phase6 monitor/transport contract; source metadata and constructed examples are not live ECU observations or exported runtime catalogs",
    },
}


def native_failure(error: NativeSelectionError | UnresolvedNativeContext) -> dict[str, Any]:
    result = getattr(error, "result", None)
    return {"status": getattr(error, "status", None), "error": str(error),
            "query": None if result is None else result.as_dict()}


def native_frame_witness(context: Any, category_id: int, selector: int) -> dict[str, Any]:
    """Retain a complete initial/event selector program, including native failures."""
    query = context.query(18, category_id, selector)
    witness: dict[str, Any] = {"selector_query": query.as_dict(), "frames": []}
    try:
        witness["frames"] = resolve_frame_program(context, category_id, selector, variable_namespace_base=0x2710)
        witness["status"] = query.status
    except (NativeSelectionError, UnresolvedNativeContext) as error:
        witness.update(native_failure(error))
    return witness


def _master_record_ref(row: Any) -> list[Any]:
    return [row.source.family, row.table_type, row.ordinal]


def _master_query_reference(query: Any, record_refs: dict[str, list[Any]]) -> dict[str, Any]:
    """Reference the regional raw catalog and its single context snapshot."""
    provenance = []
    for origin in query.provenance:
        item = {key: value for key, value in origin.items()
                if key not in ("context", "source", "selected_ids")}
        if "selected_ids" in origin:
            item["selected_record_refs"] = [record_refs[key] for key in origin["selected_ids"]]
        provenance.append(item)
    return {
        "status": query.status, "mode": query.mode,
        "record_refs": [_master_record_ref(row) for row in query.records],
        "raw_variant_refs": [_master_record_ref(row) for row in query.raw_variants],
        "provenance": provenance,
    }


def native_source_census(parser: DDBParser, root: Path, region: str, role: int,
                         plugin: str) -> tuple[Any, list[tuple[Any, Any, Any, Any]], dict[str, Any]]:
    """Separate physical source occurrences from an explicitly initial resolution.

    ECU table joins below remain raw source evidence: their comparators are outside
    the proved native master-index API. No raw category or DLL row is a live claim.
    """
    masters = {family: parser.parse_master_db(gts_db_root(root, region, family) / "Toyota.ddb")
               for family in ("Gen", "Spe")}
    context = native_context(masters["Gen"], masters["Spe"])
    raw_categories = context.raw_records(16)
    raw_bindings = [row for row in context.raw_records(19) if row.dll_role_id == role]
    record_refs = {row.identity: _master_record_ref(row) for row in (*raw_categories, *raw_bindings)}
    candidate_ids = {row.category_id for row in raw_bindings if row.dll_name == plugin}
    initial = {}
    for category_id in sorted({u16(row.raw, 0x44) for row in raw_categories}):
        category_query = context.query(16, category_id)
        binding_query = context.query(19, role, category_id)
        item: dict[str, Any] = {
            "category_query": _master_query_reference(category_query, record_refs),
            "binding_query": _master_query_reference(binding_query, record_refs),
            "category": None, "plugin": None,
        }
        try:
            selected = select_for_consumer(category_query, "category")
            item["category"] = _master_record_ref(selected)
        except (NativeSelectionError, UnresolvedNativeContext) as error:
            item["category_failure"] = {
                "status": getattr(error, "status", None), "error": str(error), "query_ref": "category_query",
            }
        try:
            item["plugin"] = support_plugin(context, category_id, role)
            if item["plugin"] is not None:
                item["plugin"].pop("selection")
                item["plugin"]["query_ref"] = "binding_query"
        except (NativeSelectionError, UnresolvedNativeContext) as error:
            item["plugin_failure"] = {
                "status": getattr(error, "status", None), "error": str(error), "query_ref": "binding_query",
            }
        if category_id in candidate_ids or (item["plugin"] is not None and item["plugin"]["dll"] == plugin):
            initial[str(category_id)] = item
    sources = []
    for family, master in masters.items():
        strings_path = gts_db_root(root, region, family) / "M_English.ddb"
        strings = load_string_db(parser, strings_path) if strings_path.is_file() else None
        decoded = parser.extract_master_ecu_categories(master.sections[16])
        for occurrence, category in zip(context.raw_records(16, family=family), decoded, strict=True):
            if str(category.category_id) in initial:
                sources.append((occurrence, category, master, strings))
    return context, sources, {
        "context": context.as_dict(), "context_label": "explicit_initial",
        "record_reference_format": "Triples are [source family, table type, physical ordinal] within this regional context. They resolve in raw_categories or raw_role_bindings; context stores the complete source, load and history metadata once.",
        "raw_categories": [row.as_dict() for row in raw_categories],
        "raw_role_bindings": [row.as_dict() for row in raw_bindings],
        "raw_role_binding_count": len(raw_bindings),
        "raw_plugin_binding_count": sum(row.dll_name == plugin for row in raw_bindings),
        "initial_plugin_category_count": sum(
            item["plugin"] is not None and item["plugin"]["dll"] == plugin for item in initial.values()),
        "native_initial": initial,
        "raw_string_sources": {
            family: {"source": identity(gts_db_root(root, region, family) / "M_English.ddb", root)
                     if (gts_db_root(root, region, family) / "M_English.ddb").is_file() else None,
                     "boundary": "Exact family-local raw annotation source only; absent source leaves names/annotated witnesses unresolved, with no cross-family fallback."}
            for family in masters
        },
        "source_census_boundary": "Physical Gen/Spe category occurrences and raw ECU-table joins; not selected ECU metadata or live eligibility.",
    }


def build(gts_root: Path, recovered_root: Path) -> dict[str, Any]:
    gts = resolve_gts_root(gts_root)
    binaries = native_sources(gts, recovered_root)
    parser = DDBParser()
    regions = {}
    for region in REGIONS:
        context, sources, selection = native_source_census(parser, gts, region, 5, "GetDatMonListP6_DT.dll")
        catalogs = []
        witnesses = {}
        for occurrence, cat, master, strings in sources:
            db_root = Path(occurrence.source.path).parent
            path = db_root / cat.database_name
            entry: dict[str, Any] = {"category_id": cat.category_id, "generation": cat.generation,
                                     "database": cat.database_name, "category_occurrence": occurrence.as_dict(),
                                     "available": bool(cat.database_name) and path.is_file()}
            if entry["available"]:
                db = parser.parse_ecu_db(path)
                entry.update({"source": identity(path, gts), **db_census(db)})
                if cat.database_name in WITNESSES:
                    witness_key = f"{occurrence.source.family}:{occurrence.ordinal}:{cat.database_name}"
                    witnesses[witness_key] = {
                        "source": identity(path, gts), "category_id": cat.category_id,
                        "category_occurrence": occurrence.as_dict(),
                        "frames": {f"0x{s:X}": native_frame_witness(context, cat.category_id, s) for s in (0xC8, 0xC9, 0xCA, 0xD3, 0xD4)},
                        "records": select_witnesses(db, master, strings) if strings is not None else [],
                        "annotation_status": "source_available" if strings is not None else "unresolved_family_string_source",
                    }
            catalogs.append(entry)
        available = [x for x in catalogs if x["available"]]
        regions[region] = {
            **selection,
            "available_source_occurrence_count": len(available),
            "totals": {key: sum(x[key] for x in available) for key in ("rows62", "visible_candidates", "composite_rows", "live_conditioned_rows", "dynamic_lsb_rows")},
            "catalogs": catalogs, "witnesses": witnesses,
        }
    bitmap = bytes.fromhex("000080")
    return {
        "schema": "gtsplus-p6-data-list-semantics-v3", "version": "2026.03.002.02",
        "binaries": binaries, "contracts": CONTRACTS, "regions": regions,
        "analytical_wire_example": {
            "provenance": "constructed branch input using the current Engine_CM_P6 DID1002, not an observed response",
            "first_request": "22a100", "first_response": "62a100" + bitmap.hex(),
            "initial_enabled_list": [f"0x{x:04X}" for x in support_bitmap(0xA100, bitmap)],
            "second_request": "22a110", "second_response": "62a11020",
            "second_level_dids": [f"0x{x:04X}" for x in support_bitmap(0x1000, b"\x20")],
            "enabled_did_membership": ["0x1002", "0xA110"],
            "live_request": "221002", "live_response": "6210021234", "expected_length": 2,
            "short_live_response": "62100212", "padded_value_slot": "1200",
        },
        "residual_questions": [
            "A live target supplies its enabled A1xx bitmap, per-DID field support, and actual values; offline dictionaries cannot decide that target's admitted list.",
            "Dynamic-LSB execution is source-recovered but has no type64 row witnesses in the exact role05 P6 regional bindings; runtime slope values remain target inputs.",
            "DataListIF CheckRcvFrame subtracts3 in u16 before copying and has no local guard for total response lengths below3; this artifact does not assert upstream transport rejects such malformed envelopes.",
            "This evidence artifact retains census/representative records; exporting every P6 runtime monitor catalog and implementing special-format/byte-string UI presentation remain separate runtime work.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gts-root", type=Path)
    ap.add_argument("--recovered-root", type=Path, default=DEFAULT_RECOVERED, help="Qualified aggregate GTSPlus component root")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    payload = build(resolve_gts_root(args.gts_root), args.recovered_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
