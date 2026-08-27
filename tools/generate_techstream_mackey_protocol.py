#!/usr/bin/env python3
"""Generate deterministic Techstream MACKey native-protocol evidence.

The source artifacts are pinned PE files in the unpacked Techstream V18 tree.
This generator intentionally does not consume a Ghidra database: RTTI, vtables,
function bodies, strings, imports, and diagnostic literals are recovered from
the PE bytes so the output is reproducible from a clean checkout plus artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
from pathlib import Path

import pefile


REPO = Path(__file__).resolve().parents[1]
BIN = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream/bin"
OUT_DIR = REPO / "data/generated/techstream_v18"

CLASS_STATES = {
    "CMAC_01": ["02", "03A", "03B", "04", "05", "06", "10", "11A", "11B",
                "12A", "13A", "13B", "13C", "14B", "16", "18", "40", "43",
                "24", "26", "27", "29", "30", "32", "33", "34", "35", "37"],
    "CMAC_01_000": ["00"],
    "CMAC_01_000_S": ["15"],
    "CMAC_01_000A": ["00A"],
    "CMAC_01_001A": ["01A", "08"],
    "CMAC_01_001B": ["01B"],
    "CMAC_01_001C": ["01C", "41", "42"],
    "CMAC_01_001C_S": ["01C"],
    "CMAC_01_001D": ["01D", "19"],
    "CMAC_01_001E": ["01E", "07"],
    "CMAC_01_001F": ["01F"],
    "CMAC_01_001F_S": ["01F"],
    "CMAC_01_009A": ["09A"],
    "CMAC_01_009A_S": ["09A"],
    "CMAC_01_009B": ["09B"],
    "CMAC_01_009B_S": ["09B"],
    "CMAC_01_015": ["15"],
    "CMAC_01_017": ["17"],
    "CMAC_01_025_S": ["25"],
    "CMAC_01_028_S": ["28"],
    "CMAC_01_031_S": ["31"],
    "CMAC_01_036_S": ["36"],
    "CMAC_01_038_S": ["38"],
    "CMAC_01_039_S": ["39"],
}

# Function starts containing references to each displayed S324 procedure code.
# These are string-reference sites, NOT one-handler-per-state ownership. A
# function may reference more than one S324 label (0x10241650 references both
# S324-08 and S324-19), and one code may be referenced from multiple functions.
# Keep this evidence separate from class-wide ComProcess operation recovery.
STATE_REFERENCE_FUNCTIONS = {
    "02": [0x10235CA0], "03A": [0x10235D60], "03B": [0x102360D0],
    "04": [0x102362D0], "05": [0x10236370], "06": [0x10236410],
    "10": [0x102364C0], "11A": [0x10236580], "11B": [0x102366D0],
    "12A": [0x10236820], "13A": [0x10236A10], "13B": [0x10236D80],
    "13C": [0x10237020], "14B": [0x102372C0], "16": [0x102374F0],
    "18": [0x10237590], "40": [0x10237650], "43": [0x102376F0],
    "24": [0x1023C530, 0x1023C7D0], "26": [0x1023C980], "27": [0x1023CA20],
    "29": [0x1023CAC0], "30": [0x1023CB60], "32": [0x1023CC00],
    "33": [0x1023CDE0], "34": [0x1023CF90], "35": [0x1023D030],
    "37": [0x1023D230],
    "00": [0x1023D510, 0x1023E0C0], "15": [0x1023DFC0, 0x10243670],
    "00A": [0x1023E6B0], "01A": [0x1023E980],
    "08": [0x1023ED20, 0x1023F490, 0x10241650], "01B": [0x1023EF10],
    "01C": [0x1023F6A0, 0x10240F80], "41": [0x1023F900],
    "42": [0x10240DB0], "01D": [0x102410B0], "19": [0x10241650],
    "01E": [0x10241870], "07": [0x10241ED0, 0x102443C0],
    "01F": [0x102420C0, 0x10242160], "09A": [0x10242240, 0x102428C0],
    "09B": [0x10242BB0, 0x10243370], "17": [0x10243A90],
    "25": [0x10243B60], "28": [0x10244080], "31": [0x10244F60],
    "36": [0x10244FF0], "38": [0x10245260], "39": [0x10245370],
}

# Operation selectors observed across all methods of each product class. These
# are class-wide and were the previous basis for the CSV. They are retained for
# cross-reference but must NOT be mistaken for per-state attributions.
CLASS_OPERATIONS = {
    "CMAC_01_000": [1, 2, 4, 5, 6], "CMAC_01_000A": [1, 2],
    "CMAC_01_001A": [1, 2, 4], "CMAC_01_001B": [2, 3, 4],
    "CMAC_01_001C": [0, 1, 2, 3, 4, 5, 6],
    "CMAC_01_001D": [1, 2, 3, 4], "CMAC_01_001E": [1, 2, 4],
    "CMAC_01_009A": [4, 5, 6], "CMAC_01_009B": [1, 2, 4, 6],
    "CMAC_01_015": [7],
}

# MACK4 disposition: the server-side MACK4 field (32 bytes) is parsed and
# stored in the native exchange record at struct offset +0x18f0, read by
# decode_exchange_records on SafekeyNumber match (same path as M1/M2/M3),
# and destroyed on cleanup. But no diagnostic operation ever transmits it:
# start_key_update_3002 sends exactly 68 bytes (header + M1/M2/M3); MACK4 is
# absent from UtilityExNK2.dll and the managed layer entirely. All +0x18f0
# references outside parse/decode are std::string destructors.
MACK4_DISPOSITION = {
    "parsed_at": "IT3UtilityNK.dll parse_exchange_key_entry +0x439",
    "struct_offset": "0x18f0",
    "consumed_by_vehicle_write": False,
    "start_key_update_payload": "header(4) + M1(16) + M2(32) + M3(16) = 68 bytes",
    "appears_in_managed": False,
    "appears_in_utilityexnk2": False,
    "non_parse_refs": "std::string destructors only",
    "conclusion": (
        "MACK4 is parsed, stored, matched, and destroyed — but never reaches "
        "any diagnostic wire operation. It is a dead-stored server response "
        "field retained for potential host-side validation that this binary "
        "does not implement."
    ),
}

OPERATION_MEANINGS = {
    0: "update_vehicle_status",
    1: "security_access_seed_update",
    2: "read_safekey_and_mac",
    3: "upload_after_get_seed",
    4: "upload_after_send_key",
    5: "upload_ecu_list",
    6: "change_default_session",
    7: "read_safekey_variant",
}

FUNCTIONS = {
    # IT3UtilityNK.dll: response parser and native bridge.
    "IT3UtilityNK.dll": {
        "mackey_com_process": (0x10237970, 300),
        "parse_exchange_key_entry": (0x102397C0, 1201),
        "parse_response_xml_28": (0x10238B60, 1756),
        "parse_response_xml_8": (0x1023B660, 1756),
        "decode_exchange_records": (0x1023BD90, 1323),
        "validation_ecu_sec_key_wrapper": (0x1023D4D0, 57),
    },
    # UtilityExNK2.dll: exact diagnostic producers/consumers.
    "UtilityExNK2.dll": {
        "read_security_version_103a": (0x100EB690, 165),
        "read_vehicle_status_103b": (0x100EB740, 146),
        "session_104f": (0x100EB7E0, 105),
        "security_seed_2741": (0x100EB850, 191),
        "security_key_2742": (0x100EB910, 158),
        "write_topology_1035": (0x100EB9B0, 151),
        "read_vin_f190": (0x100EBD80, 174),
        "read_mac_tuple_102e": (0x100EBE30, 155),
        "read_safekey_1010": (0x100EBED0, 167),
        "start_key_update_3002": (0x100EC0E0, 226),
        "poll_key_update_3002": (0x100EC1D0, 256),
        "read_topology_1033": (0x100EC2D0, 156),
        "discover_master_slaves": (0x100EC4C0, 1004),
    },
}

COMMAND_ROWS = [
    ("read VIN", "UDS ReadDataByIdentifier", "22 f1 90", 3, ">=20", "ECU 0x763", "VIN[17]", "recovered"),
    ("read MAC tuple", "UDS ReadDataByIdentifier", "22 10 2e", 3, ">=67", "ECU 0x763", "MACM1[16] || MACM2[32] || MACM3[16]", "recovered"),
    ("read SafekeyNumber", "UDS ReadDataByIdentifier", "22 10 10", 3, ">=19", "master/slave ECU", "SafekeyNumber[16]", "recovered"),
    ("request seed", "UDS SecurityAccess", "27 41", 2, "18", "selected ECU", "seed[16]", "recovered"),
    ("send key", "UDS SecurityAccess", "27 42 || key[16]", 18, ">=2", "derived key[16]", "selected ECU", "recovered"),
    ("write ECU topology", "UDS WriteDataByIdentifier", "2e 10 35 || topology[25]", 28, ">=3", "discovered ECU map", "ECU 0x763", "recovered"),
    ("start key update", "UDS RoutineControl start", "31 01 30 02 || M1[16] || M2[32] || M3[16]", 68, ">=4", "server exchange record", "each selected ECU", "recovered"),
    ("poll key update", "UDS RoutineControl results", "31 03 30 02", 4, ">=6; >=54 when complete", "each selected ECU", "state[2], M4[32], M5[16]", "recovered"),
    ("read ECU topology", "UDS ReadDataByIdentifier", "22 10 33", 3, ">=28", "ECU 0x763", "topology[25]", "recovered"),
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class PEView:
    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        self.pe = pefile.PE(data=self.data, fast_load=False)
        self.base = self.pe.OPTIONAL_HEADER.ImageBase

    def va_to_offset(self, va: int) -> int:
        return self.pe.get_offset_from_rva(va - self.base)

    def offset_to_va(self, offset: int) -> int:
        return self.base + self.pe.get_rva_from_offset(offset)

    def u32(self, offset: int) -> int:
        return struct.unpack_from("<I", self.data, offset)[0]

    def refs32(self, value: int) -> list[int]:
        needle = struct.pack("<I", value)
        refs: list[int] = []
        start = 0
        while (found := self.data.find(needle, start)) >= 0:
            refs.append(found)
            start = found + 1
        return refs

    def body(self, va: int, size: int) -> bytes:
        offset = self.va_to_offset(va)
        return self.data[offset:offset + size]


def recover_rtti(view: PEView) -> list[dict[str, object]]:
    classes: list[dict[str, object]] = []
    for match in re.finditer(rb"\.\?AV(CMAC_01[^@]*)@@", view.data):
        name = match.group(1).decode("ascii")
        string_va = view.offset_to_va(match.start())
        type_descriptor_va = string_va - 8
        vtables: list[tuple[int, list[int]]] = []
        for type_ref in view.refs32(type_descriptor_va):
            if type_ref < 12 or view.u32(type_ref - 12) != 0:
                continue
            col_va = view.offset_to_va(type_ref - 12)
            for col_ref in view.refs32(col_va):
                values: list[int] = []
                cursor = col_ref + 4
                while cursor + 4 <= len(view.data):
                    value = view.u32(cursor)
                    if not (view.base + 0x1000 <= value < view.base + 0x2B0000):
                        break
                    values.append(value)
                    cursor += 4
                if values:
                    vtables.append((view.offset_to_va(col_ref) + 4, values))
        if len(vtables) != 1:
            raise RuntimeError(f"{name}: expected one vtable, got {len(vtables)}")
        vtable_va, methods = vtables[0]
        classes.append({
            "name": name,
            "rtti_string_va": f"0x{string_va:08x}",
            "vtable_va": f"0x{vtable_va:08x}",
            "vtable_entries": len(methods),
            "vtable_sha256": sha256(b"".join(struct.pack("<I", value) for value in methods)),
            "first_method_va": f"0x{methods[0]:08x}",
            "states": CLASS_STATES[name],
            "operation_selectors": CLASS_OPERATIONS.get(name, []),
        })
    return classes


def make_outputs() -> tuple[dict[str, object], list[dict[str, object]]]:
    native = PEView(BIN / "IT3UtilityNK.dll")
    utility = PEView(BIN / "UtilityExNK2.dll")
    views = {"IT3UtilityNK.dll": native, "UtilityExNK2.dll": utility}

    classes = recover_rtti(native)
    bodies: dict[str, dict[str, object]] = {}
    for dll, functions in FUNCTIONS.items():
        view = views[dll]
        for name, (va, size) in functions.items():
            body = view.body(va, size)
            bodies[name] = {
                "dll": dll, "va": f"0x{va:08x}", "rva": f"0x{va - view.base:x}",
                "size": size, "sha256": sha256(body),
            }

    required_tags = [
        "<ExchangeKeyList>", "<ExchangeKey", "SafekeyNumber", "<MACM1>",
        "<MACM2>", "<MACM3>", "<MACK4>", "\\Memg\\MAC_01_WriteData.xml",
    ]
    tags = {}
    for tag in required_tags:
        offset = native.data.index(tag.encode("ascii"))
        tags[tag] = f"0x{native.offset_to_va(offset):08x}"

    utility_exports = {
        symbol.ordinal: symbol.name.decode("ascii")
        for symbol in utility.pe.DIRECTORY_ENTRY_EXPORT.symbols if symbol.name
    }
    companion_imports = sorted(
        utility_exports[entry.ordinal]
        for descriptor in native.pe.DIRECTORY_ENTRY_IMPORT
        if descriptor.dll.lower() == b"utilityexnk2.dll"
        for entry in descriptor.imports
        if entry.ordinal in utility_exports and "Ex2MAC_01" in utility_exports[entry.ordinal]
    )

    evidence = {
        "schema": 2,
        "artifacts": {name: sha256(view.data) for name, view in views.items()},
        "rtti_classes": classes,
        "function_bodies": bodies,
        "companion_imports": companion_imports,
        "operation_selectors": {str(key): value for key, value in OPERATION_MEANINGS.items()},
        "state_reference_model": {
            "meaning": "S324 string-reference census; no per-state operation ownership",
            "references": {
                state: [f"0x{va:08x}" for va in vas]
                for state, vas in sorted(STATE_REFERENCE_FUNCTIONS.items())
            },
            "reference_associations": sum(len(vas) for vas in STATE_REFERENCE_FUNCTIONS.values()),
            "unique_reference_functions": len({
                va for vas in STATE_REFERENCE_FUNCTIONS.values() for va in vas
            }),
            "shared_reference_functions": {
                f"0x{va:08x}": sorted(states)
                for va in sorted({
                    va for vas in STATE_REFERENCE_FUNCTIONS.values() for va in vas
                })
                if len(states := [
                    state for state, vas in STATE_REFERENCE_FUNCTIONS.items() if va in vas
                ]) > 1
            },
        },
        "mack4_disposition": MACK4_DISPOSITION,
        "response_parser": {
            "tags": tags,
            "maximum_exchange_records": {"standard": 28, "short_variant": 8},
            "identity_match": "32 hexadecimal characters decoded to 16 raw bytes",
            "record_fields": {"SafekeyNumber": 16, "MACM1": 16, "MACM2": 32,
                              "MACM3": 16, "MACK4": 32},
        },
        "vehicle_architecture": {
            "master_request_id": "0x763",
            "gateway_check_id": "0x7a2",
            "maximum_ecu_records": 8,
            "discovery_dids": ["0x1100", "0x1101", "0x1102", "0x1103", "0x1104",
                               "0x1105", "0x1107", "0x1108", "0x1033", "0x1035"],
            "association_key": "raw 16-byte SafekeyNumber",
        },
        "commands": [
            {"name": name, "api": api, "request": request, "request_length": request_length,
             "response_length": response_length, "source": source, "destination": destination,
             "grade": grade}
            for name, api, request, request_length, response_length, source, destination, grade
            in COMMAND_ROWS
        ],
        "firmware_join": {
            "techstream": {"start": "31 01 30 02 || M1[16] || M2[32] || M3[16]",
                           "poll": "31 03 30 02", "result": "M4[32] || M5[16]"},
            "sienna_4512000": {"start": "31 01 10 10 || M1[16] || M2[32] || M3[16]",
                              "poll": "31 03 10 10", "result": "status || M4[32] || M5[16]"},
            "conclusion": "same cryptographic envelope; different service/procedure",
        },
    }

    rows: list[dict[str, object]] = []
    for item in classes:
        class_name = str(item["name"])
        states = list(item["states"])
        for state in states:
            references = STATE_REFERENCE_FUNCTIONS[state]
            rows.append({
                "row_kind": "state",
                "class_state": f"{class_name}/S324-{state}",
                "state_code_reference_rvas": "|".join(
                    f"0x{va - native.base:x}" for va in references
                ),
                "predecessor": "caller-selected class entry/branch",
                "successor": "handler-specific success/failure; cross-class edge caller-selected",
                "class_operations": (
                    "Ex2MAC_01_ComProcess " + "/".join(
                        f"{s}:{OPERATION_MEANINGS[s]}"
                        for s in item["operation_selectors"]
                    )
                    if item["operation_selectors"]
                    else "none"
                ),
                "source_field": "CMAC_01 class-local procedure/display state",
                "destination_field": f"displayed procedure code S324-{state}",
                "interpretation": (
                    "procedure/UI label; reference RVAs are all native functions "
                    "that reference this code and do not imply operation ownership"
                ),
                "evidence_grade": "bounded",
            })
    for name, api, request, request_length, response_length, source, destination, grade in COMMAND_ROWS:
        rows.append({
            "row_kind": "vehicle_command", "class_state": name,
            "state_code_reference_rvas": "see protocol JSON",
            "predecessor": "vehicle connection/session", "successor": "positive response or error branch",
            "class_operations": f"{api}: {request}", "request_length": request_length,
            "response_length": response_length, "source_field": source, "destination_field": destination,
            "interpretation": name, "evidence_grade": grade,
        })
    return evidence, rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files differ")
    args = parser.parse_args()
    evidence, rows = make_outputs()
    json_text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    fieldnames = ["row_kind", "class_state", "state_code_reference_rvas",
                  "predecessor", "successor", "class_operations",
                  "request_length", "response_length", "source_field",
                  "destination_field", "interpretation", "evidence_grade"]
    from io import StringIO
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    csv_text = stream.getvalue()
    outputs = {
        OUT_DIR / "mackey_vehicle_protocol.json": json_text,
        OUT_DIR / "mackey_state_machine.csv": csv_text,
    }
    if args.check:
        stale = [str(path.relative_to(REPO)) for path, text in outputs.items()
                 if not path.exists() or path.read_text() != text]
        if stale:
            raise SystemExit("stale generated outputs: " + ", ".join(stale))
        print("Techstream MACKey generated evidence is current")
        return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, text in outputs.items():
        path.write_text(text)
        print(path.relative_to(REPO))


if __name__ == "__main__":
    main()
