#!/usr/bin/env python3
"""Verify the current GTS+ DDB corpus census and steering-control witnesses."""
from __future__ import annotations

import json
import hashlib
import struct
import tempfile
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream.extract_gtsplus_ddb_corpus_census import build
from tools.techstream.techstream_paths import resolve_gts_root
from tools.techstream.parse_ddb import DDBParser, Section, TableDataHead

ARTIFACT = REPO / "data/generated/gtsplus_2026/ddb_corpus_census.json"

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))




a = json.loads(ARTIFACT.read_text())

fresh = build(resolve_gts_root())
check("artifact regenerates exactly", fresh == a)

ds4 = a["ds4"]
check("every supplied DS4 input decoded", ds4["counts"]["ddb_files"] == 301)
check("all DS4 format variants retained",
      ds4["counts"]["formats"] == {"1": 4, "2": 199, "3": 2, "4": 24, "5": 24, "6": 48})
check("all DS4 product/family contexts retained",
      ds4["counts"]["groups"] == {"DM/Gen": 181, "DM/Spe": 4, "OS/Gen": 112, "OS/Spe": 4})
check("all 2519 master/ECU section instances retained",
      ds4["counts"]["section_instances"] == 2519
      and ds4["counts"]["sectioned_files"] == 203)
check("both Viewer inputs decoded with all eight sections",
      ds4["counts"]["viewer_section_instances"] == 8)
check("DS4 fixed and variable rows kept separate",
      ds4["counts"]["fixed_raw_rows_including_viewer"] == 446812
      and ds4["counts"]["variable_sections"] == 4)
check("every DS4 string and resource row retained",
      ds4["counts"]["string_entries"] == 3421680
      and ds4["counts"]["metadata_entries"] == 394416)
supplemental = a["supplemental"]
check("all main Viewer and string files retained",
      supplemental["counts"]["formats"] == {"3": 6, "4": 30, "5": 30, "6": 30}
      and supplemental["counts"]["ddb_files"] == 96)
check("main Viewer complete section and record census",
      supplemental["counts"]["viewer_section_instances"] == 26
      and supplemental["counts"]["fixed_raw_rows_including_viewer"] == 920200)
check("main string/resource census exact",
      supplemental["counts"]["string_entries"] == 14382390
      and supplemental["counts"]["metadata_entries"] == 788730)
check("main masters retain every section and declared row",
      a["main_masters"]["counts"] == {
          "ddb_files": 6, "section_instances": 248,
          "declared_records": 4079510, "variable_sections": 6,
      })
# Decode every source on demand. The census does not duplicate the databases.
row_parser = DDBParser()
for corpus in (ds4, supplemental, a["main_masters"]):
    for source in corpus["inputs"]:
        path = REPO / source["path"]
        version = source["format_version"]
        parse = {
            1: row_parser.parse_master_db, 2: row_parser.parse_ecu_db,
            3: row_parser.parse_viewer_db, 4: row_parser.load_string_db,
            5: row_parser.load_string_db, 6: row_parser.load_string_db,
        }[version]
        db = parse(path)
        sections = source.get("sections", source.get("strings", {}).get("sections", ()))
        for expected in sections:
            section = db.sections[expected["table_type"]]
            decoded = section.decoded_data
            check(f"{source['id']} section{expected['table_type']} complete decoded hash",
                  len(decoded) == expected["decoded_size"]
                  and hashlib.sha256(decoded).hexdigest() == expected["decoded_sha256"])
            valid = section.source_path == path
            count = 0
            for record in section.iter_records():
                valid &= (
                    record.index == count and record.source_path == section.source_path
                    and record.source_payload_offset == expected["data_offset"]
                    and record.table_type == expected["table_type"]
                )
                if section.variable_layout:
                    offset, length = struct.unpack("<IH", record.directory_raw)
                    logical = section.header.record_count * 6 + offset
                    valid &= (
                        record.directory_raw == decoded[count * 6:(count + 1) * 6]
                        and record.decoded_offset == (logical if length else None)
                        and record.raw == (decoded[logical:logical + length] if length else b"")
                    )
                else:
                    size = section.decoded_record_size
                    valid &= (
                        record.decoded_offset == count * size
                        and record.raw == decoded[count * size:(count + 1) * size]
                    )
                count += 1
            check(f"{source['id']} section{expected['table_type']} all ordered raw row identities",
                  valid and count == expected["record_count"])
            if "raw_rows" in expected:
                check(f"{source['id']} section{expected['table_type']} selection rows exact",
                      expected["raw_rows"] == [r.raw.hex() for r in section.iter_records()])

parser = DDBParser()
root = resolve_gts_root().parent / "DS-4"
for source in ds4["inputs"]:
    if source["format_version"] != 1:
        continue
    master = parser.parse_master_db(root / source["id"])
    if 19 not in master.sections:
        continue
    entries = parser.extract_master_dlls(master.sections[19])
    check(f"{source['id']} native DLL role/handling fields",
          all(entry.dll_role_id == entry.raw[0x56]
              and entry.handling_id == struct.unpack_from("<H", entry.raw, 0x52)[0]
              and entry.handling_flag == entry.raw[0x57] for entry in entries))


def rejects(call) -> bool:
    try:
        call()
    except ValueError:
        return True
    return False


# A fixed-divisible variable payload must still remain variable. Zero-length
# entries and nonmonotonic pool offsets are legal; out-of-pool rows are not.
variable_data = struct.pack("<IH", 2, 2) + struct.pack("<IH", 0xFFFFFFFF, 0) + b"abcd"
variable = Section(TableDataHead(0, 0, 2, len(variable_data)), 0,
                   variable_data, "ds4", True)
check("variable entries follow offsets and lengths", variable.variable_records() == [b"cd", b""])
check("variable table has no fixed decoded size",
      rejects(lambda: variable.decoded_record_size))
bad_variable = Section(TableDataHead(0, 0, 1, 7), 0,
                       struct.pack("<IH", 1, 1) + b"x", "ds4", True)
check("variable pool bounds remain enforced", rejects(bad_variable.variable_records))

# Header tags, directory boundaries, slot identities and compression gates.
sample = (root / "DM/DB/Gen/4WD_KWPDK.ddb").read_bytes()
with tempfile.TemporaryDirectory() as temporary:
    path = Path(temporary) / "boundary.ddb"
    mutations = {}
    data = bytearray(sample)
    data[0] ^= 0x80
    mutations["unknown DS4 family"] = data
    data = bytearray(sample)
    data[0x0A] ^= 1
    mutations["bad signature"] = data
    data = bytearray(sample)
    data[9] = 0xFF
    mutations["declared directory boundary"] = data
    data = bytearray(sample)
    struct.pack_into("<I", data, 0x24 + 5 * 4, 0x24)
    mutations["directory overlap"] = data
    offset = struct.unpack_from("<I", sample, 0x24 + 5 * 4)[0]
    data = bytearray(sample)
    data[offset] = 6
    mutations["slot/type mismatch"] = data
    data = bytearray(sample)
    data[offset + 1] = 2
    mutations["unknown compression"] = data
    data = bytearray(sample)
    struct.pack_into("<I", data, offset + 6, len(sample))
    mutations["payload past EOF"] = data
    for label, data in mutations.items():
        path.write_bytes(data)
        check(label + " rejected", rejects(lambda: DDBParser().parse_ecu_db(path)))
    type6 = bytearray((root / "DM/DB/Gen/U_English.ddb").read_bytes())
    type6[7] = 0xFF
    path.write_bytes(type6)
    check("unobserved DS4 type6 language tag rejected",
          rejects(lambda: parser.load_string_db(path)))
    check("ECU cannot be parsed as master",
          rejects(lambda: parser.parse_master_db(root / "DM/DB/Gen/4WD_KWPDK.ddb")))
    viewer = bytearray((root / "DM/DB/Gen/Viewer.ddb").read_bytes())
    offset = struct.unpack_from("<I", viewer, 0x24 + 2 * 4)[0]
    struct.pack_into("<I", viewer, offset + 2, 69403)
    path.write_bytes(viewer)
    check("Viewer native row stride enforced", rejects(lambda: parser.parse_viewer_db(path)))

    # A literal-only native LZSS block gives exact string-boundary witnesses.
    def string_fixture(offset: int, length: int) -> bytes:
        decoded = struct.pack("<IH", offset, length) + b"A\x00"
        block = struct.pack("<IB", len(decoded), 0) + b"\xff" + decoded
        header = bytearray(sample[:0x24])
        header[8:10] = bytes((4, 1))
        return (bytes(header) + struct.pack("<I", 0x28)
                + struct.pack("<BBII", 0, 1, 1, len(block)) + block)

    path.write_bytes(string_fixture(0, 2))
    check("minimal DS4 string resolves 1-based UTF-16 entry",
          parser.load_string_db(path).get_string(1) == "A")
    for offset, length, label in ((1, 2, "string past pool"), (0, 1, "odd UTF-16 length")):
        path.write_bytes(string_fixture(offset, length))
        check(label + " rejected", rejects(lambda: parser.load_string_db(path)))

# Empty main role fields cannot trigger the old content-dependent layout guess.
dll_raw = bytearray(88)
dll_raw[0x56] = 2
main_section = Section(TableDataHead(19, 0, 1, 88), 0, bytes(dll_raw), "gtsplus")
entry = parser.extract_master_dlls(main_section)[0]
check("main role zero stays role zero with nonzero handling flag",
      entry.dll_role_id == 0 and entry.handling_flag == 2)
category_raw = bytearray(76)
category_raw[0x48:0x4A] = bytes((20, 2))
category = parser.extract_master_ecu_categories(
    Section(TableDataHead(16, 0, 1, 76), 0, bytes(category_raw), "gtsplus")
)[0]
check("category generation excludes adjacent exception flag",
      category.generation == 20 and category.exception_flag == 2)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
