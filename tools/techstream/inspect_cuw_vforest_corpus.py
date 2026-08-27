#!/usr/bin/env python3
"""Inspect the local Toyota Tacoma VFOREST CUW corpus comparatively.

This tool treats the ignored files under software/Techstream/cuw as external specimens.
It validates each Format-4 package, maps archive members to CPU descriptors in
archive/CPU order, expands ASCII-hex ZV/LZF payloads, joins each CPU to the
pinned Techstream V18 Parameter.ini route, and reports corpus-level invariants
and direct-update image diffs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from techstream_paths import CUW_CORPUS_ROOT, V18_CUW_ROOT
from typing import Any

from cuw_attach import parse_attach_bytes
from parse_cuw_container import first_member_payload

from inspect_cuw_legacy import (
    decode_legacy_target_data,
    decode_parameter_rows,
    exported_value_labels,
    legacy_check_id_payloads,
)
from inspect_cuw_vforest import decode_ascii_hex_payload, parse_zv_lzf_stream
from parse_cuw_container import parse as parse_container

REPO = Path(__file__).resolve().parents[2]
DEFAULT_CORPUS = CUW_CORPUS_ROOT
DEFAULT_TECHSTREAM_ROOT = V18_CUW_ROOT
FILL_WORD = bytes.fromhex("E203F133")
FOOTER_MAGIC = bytes.fromhex("B270AD78E88F32B558FEEB58D03B3B1D")
METADATA_MARKER = bytes.fromhex("9E5D123A")
TACOMA_GLOB = "T-*.cuw"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cpu_sections(attach: dict[str, dict[str, str]]) -> list[tuple[str, dict[str, str]]]:
    return [(key, attach[key]) for key in sorted(attach) if key.startswith("CPU")]


def expected_part_text(new_cid: str) -> bytes:
    if len(new_cid) < 10:
        raise ValueError(f"NewCID is too short for VFOREST part identity: {new_cid!r}")
    return f"{new_cid[:5]}-{new_cid[5:10]}-".encode("ascii")


def contiguous_ranges(values: list[int]) -> list[list[int]]:
    if not values:
        return []
    out: list[list[int]] = []
    start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1:
            previous = value
            continue
        out.append([start, previous])
        start = previous = value
    out.append([start, previous])
    return out


def fill_runs(image: bytes) -> list[list[int]]:
    if len(image) % 0x1000:
        raise ValueError("logical VFOREST image is not 4-KiB block aligned")
    fill_block = FILL_WORD * (0x1000 // len(FILL_WORD))
    indices = [
        index
        for index in range(len(image) // 0x1000)
        if image[index * 0x1000:(index + 1) * 0x1000] == fill_block
    ]
    return contiguous_ranges(indices)


def trailing_fill_before_footer(image: bytes) -> dict[str, int]:
    """Return the exact word-aligned E203F133 run immediately before the 52-byte footer."""
    footer_offset = len(image) - 52
    start = footer_offset
    while start >= 4 and image[start - 4:start] == FILL_WORD:
        start -= 4
    return {
        "start_offset": start,
        "end_exclusive": footer_offset,
        "length": footer_offset - start,
    }


def diff_images(before: bytes, after: bytes) -> dict[str, Any]:
    if len(before) != len(after):
        raise ValueError("direct-update image lengths differ")
    changed_by_block: list[dict[str, Any]] = []
    changed_bytes = 0
    changed_blocks: list[int] = []
    for block in range(len(before) // 0x1000):
        left = before[block * 0x1000:(block + 1) * 0x1000]
        right = after[block * 0x1000:(block + 1) * 0x1000]
        count = sum(a != b for a, b in zip(left, right))
        if not count:
            continue
        changed_bytes += count
        changed_blocks.append(block)
        changed_by_block.append({
            "block": block,
            "offset": block * 0x1000,
            "changed_bytes": count,
            "before_sha256": sha256(left),
            "after_sha256": sha256(right),
        })
    byte_offsets = [index for index, (a, b) in enumerate(zip(before, after)) if a != b]
    byte_spans = contiguous_ranges(byte_offsets)
    return {
        "length": len(before),
        "identical": not changed_bytes,
        "changed_bytes": changed_bytes,
        "changed_fraction": changed_bytes / len(before),
        "changed_block_count": len(changed_blocks),
        "changed_blocks": changed_blocks,
        "changed_block_ranges": contiguous_ranges(changed_blocks),
        "changed_by_block": changed_by_block,
        "changed_byte_span_count": len(byte_spans),
        "first_changed_byte_spans": byte_spans[:64],
        "dense_changed_blocks_gt_2048_bytes": [
            row["block"] for row in changed_by_block if row["changed_bytes"] > 0x800
        ],
    }


def decode_one_package(
    path: Path,
    route_rows: dict[str, list[dict[str, str]]],
    cpu_labels: dict[str, str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    package = path.read_bytes()
    container = parse_container(package)
    if container["errors"]:
        raise ValueError(f"{path.name}: " + "; ".join(container["errors"]))
    attach_raw = first_member_payload(package, container)
    attach = parse_attach_bytes(attach_raw)
    vehicle = attach.get("Vehicle", {})
    if vehicle.get("VehicleName") != "Tacoma":
        raise ValueError(f"{path.name}: non-Tacoma package in Tacoma VFOREST corpus")
    cpus = cpu_sections(attach)
    archives = container.get("format4_archives", [])
    declared_cpu_count = int(vehicle.get("NumberOfCalibration", "0") or 0)
    if not (len(cpus) == len(archives) == declared_cpu_count):
        raise ValueError(
            f"{path.name}: CPU/archive count mismatch: descriptor={declared_cpu_count}, "
            f"sections={len(cpus)}, archives={len(archives)}"
        )

    image_rows: list[dict[str, Any]] = []
    for member_index, ((section_name, cpu), archive) in enumerate(zip(cpus, archives), start=1):
        start = int(archive["payload_offset"])
        payload = package[start:start + int(archive["payload_length"])]
        zv = decode_ascii_hex_payload(payload)
        records, image = parse_zv_lzf_stream(zv)

        new_cid = cpu.get("NewCID", "")
        expected_part = expected_part_text(new_cid)
        part_offset = image.find(expected_part)
        if part_offset != 0x100C:
            raise ValueError(
                f"{path.name}/{section_name}: expected {expected_part!r} at 0x100C, got {part_offset:#x}"
            )

        route_key = f"{vehicle.get('KindOfECU', '')}{vehicle.get('ContactType', '')}{cpu.get('CPUType', '')}"
        matching_rows = route_rows.get(route_key, [])
        if len(matching_rows) != 1:
            raise ValueError(f"{path.name}/{section_name}: expected one Parameter.ini row for {route_key}")
        route = matching_rows[0]
        password_address = int(route.get("PasswordAddress", "0"), 16)
        byte_order = int(route.get("ByteOrder", "0") or 0)
        raw_password = zv[password_address:password_address + 4]
        if len(raw_password) != 4:
            raise ValueError(f"{path.name}/{section_name}: PasswordAddress outside decoded ZV stream")
        ordered = raw_password if byte_order != 0 else raw_password[::-1]
        new_password = int.from_bytes(ordered, "big")
        location = bytes.fromhex(cpu.get("LocationID", ""))
        new_frames = legacy_check_id_payloads(location, new_password)

        source_passwords = []
        for target_index in range(1, int(cpu.get("NumberOfTargets", "0") or 0) + 1):
            calibration = cpu.get(f"{target_index:02d}_TargetCalibration", "")
            target_data = cpu.get(f"{target_index:02d}_TargetData", "")
            password = decode_legacy_target_data(target_data)
            frames = legacy_check_id_payloads(location, password)
            source_passwords.append({
                "calibration": calibration,
                "target_data": target_data,
                "password_hex": f"{password:08X}",
                "wire_password_hex": frames[-1].hex().upper(),
            })

        type_counts = {
            "0": sum(record["type"] == 0 for record in records),
            "1": sum(record["type"] == 1 for record in records),
        }
        metadata_window = image[0x1004:0x1024]
        footer = image[-52:]
        footer_expected = FOOTER_MAGIC + bytes(4) + metadata_window
        image_rows.append({
            "package": path.name,
            "cpu_section": section_name,
            "member_index": member_index,
            "archive_member_name": archive["name"],
            "archive_payload_length": int(archive["payload_length"]),
            "archive_payload_sha256": archive["payload_sha256"],
            "cpu_type": cpu.get("CPUType"),
            "cpu_type_export": cpu_labels.get(cpu.get("CPUType", "")),
            "cpu_image_name": cpu.get("CPUImageName"),
            "new_cid": new_cid,
            "location_id": cpu.get("LocationID"),
            "route_key": route_key,
            "route": {
                key: route.get(key)
                for key in (
                    "PasswordAddress", "ByteOrder", "CalibrationType", "EngineTypeFlag",
                    "FORESTTypeFlag", "M16CTypeFlag", "FlagToUseCIDGetterAndFlashWriterDLL",
                    "FlagToUseGetFlashSizeFunc", "PrepareRetryFlag",
                    "WaitTimeAfterIGOn", "WaitTimeForIGOFFON",
                    "FlagToChangeToReprogGWModeForCentralGW", "FlagToCancelAutomaticIGOFF",
                    "FlagToDoIGOFFONAtCPUTypeChange", "CPUTypeWithModeChangeAtCPUTypeChangeFlag",
                )
            },
            "decoded_zv": {
                "length": len(zv),
                "sha256": sha256(zv),
                "record_count": len(records),
                "record_type_counts": type_counts,
                "stream_consumed_exactly": sum(r["header_length"] + r["stored_length"] for r in records) == len(zv),
            },
            "logical_image": {
                "length": len(image),
                "sha256": sha256(image),
                "block_count": len(image) // 0x1000,
                "part_identity_offset": part_offset,
                "part_identity_ascii": expected_part.decode("ascii"),
                "fill_word_hex": FILL_WORD.hex().upper(),
                "full_fill_block_runs": fill_runs(image),
                "trailing_fill_before_footer": trailing_fill_before_footer(image),
            },
            "metadata": {
                "password_field_logical_offset": 0x1004,
                "password_field_hex": image[0x1004:0x1008].hex().upper(),
                "marker_offset": 0x1008,
                "marker_hex": image[0x1008:0x100C].hex().upper(),
                "password_address_in_decoded_zv": password_address,
                "password_bytes_in_decoded_zv_hex": raw_password.hex().upper(),
                "logical_password_equals_zv_password": image[0x1004:0x1008] == raw_password,
                "footer_offset": len(image) - 52,
                "footer_magic_hex": footer[:16].hex().upper(),
                "footer_repeats_metadata_window": footer == footer_expected,
            },
            "security": {
                "source_passwords": source_passwords,
                "new_image_password_hex": f"{new_password:08X}",
                "new_image_wire_password_hex": new_frames[-1].hex().upper(),
                "new_image_check_id_payloads_after_can_id": [x.hex().upper() for x in new_frames],
                "security_access": "shared integrated legacy 27 01/02 path; key = seed XOR 00 60 60 00",
            },
            "_image": image,
            "_zv": zv,
        })

    package_row = {
        "filename": path.name,
        "size": len(package),
        "sha256": sha256(package),
        "format_type": container["format_type"],
        "format4_archive_count": container["format4_archive_count"],
        "descriptor": attach,
    }
    return package_row, image_rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("corpus", nargs="?", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--techstream-root", type=Path, default=DEFAULT_TECHSTREAM_ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    corpus = args.corpus
    techstream = args.techstream_root
    if not corpus.is_dir():
        raise SystemExit(f"missing corpus directory: {corpus}")
    if not techstream.is_dir():
        raise SystemExit(f"missing Techstream CUW root: {techstream}")

    parameter_rows = decode_parameter_rows(techstream)
    route_rows: dict[str, list[dict[str, str]]] = {}
    for row in parameter_rows:
        route_rows.setdefault(row.get("ParamFileKeySystemProtocolMicon", ""), []).append(row)
    cpu_labels = exported_value_labels(techstream / "TCUWCalibrationFile.dll", "glptrCPUType_")

    paths = sorted(path for path in corpus.glob(TACOMA_GLOB) if path.name != "T-0087-17.cuw")
    packages: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    for path in paths:
        package_row, image_rows = decode_one_package(path, route_rows, cpu_labels)
        packages.append(package_row)
        images.extend(image_rows)

    if not images:
        raise SystemExit("no Tacoma VFOREST images found")
    minimum = min(len(row["_image"]) for row in images)
    common_prefix = 0
    while common_prefix < minimum:
        if len({row["_image"][common_prefix] for row in images}) != 1:
            break
        common_prefix += 1

    common_block0 = images[0]["_image"][:0x1000]
    if not all(row["_image"][:0x1000] == common_block0 for row in images):
        raise ValueError("first 4-KiB block is not common across corpus")

    by_identity = {(row["package"], row["new_cid"]): row for row in images}
    a71 = by_identity[("T-0037-18 - 04A71.cuw", "8966304A7100")]
    a72 = by_identity[("T-0002-21 - 04A72.cuw", "8966304A7200")]
    b81_main = by_identity[("T-0023-20 - 04B81.cuw", "8966304B8100")]
    b82_main = by_identity[("T-0012-21 - 04B82.cuw", "8966304B8200")]
    b81_companion = by_identity[("T-0023-20 - 04B81.cuw", "896650410100")]
    b82_companion = by_identity[("T-0012-21 - 04B82.cuw", "896650410100")]

    predecessor_password_closures = []
    cid_index: dict[str, list[dict[str, Any]]] = {}
    for row in images:
        cid_index.setdefault(row["new_cid"], []).append(row)
    for successor in images:
        for target in successor["security"]["source_passwords"]:
            for predecessor in cid_index.get(target["calibration"], []):
                predecessor_password_closures.append({
                    "predecessor_package": predecessor["package"],
                    "predecessor_cid": predecessor["new_cid"],
                    "successor_package": successor["package"],
                    "successor_cid": successor["new_cid"],
                    "target_old_password_hex": target["password_hex"],
                    "predecessor_new_password_hex": predecessor["security"]["new_image_password_hex"],
                    "password_matches": target["password_hex"] == predecessor["security"]["new_image_password_hex"],
                })

    comparisons = [
        {
            "name": "04A71_to_04A72",
            "before_package": a71["package"],
            "before_cid": a71["new_cid"],
            "after_package": a72["package"],
            "after_cid": a72["new_cid"],
            "target_edge_present": any(x["calibration"] == a71["new_cid"] for x in a72["security"]["source_passwords"]),
            "logical_image_diff": diff_images(a71["_image"], a72["_image"]),
        },
        {
            "name": "04B81_to_04B82_companion_CPUType89",
            "before_package": b81_companion["package"],
            "before_cid": b81_companion["new_cid"],
            "after_package": b82_companion["package"],
            "after_cid": b82_companion["new_cid"],
            "decoded_zv_identical": b81_companion["_zv"] == b82_companion["_zv"],
            "logical_image_diff": diff_images(b81_companion["_image"], b82_companion["_image"]),
        },
        {
            "name": "04B81_to_04B82_main_CPUType86",
            "before_package": b81_main["package"],
            "before_cid": b81_main["new_cid"],
            "after_package": b82_main["package"],
            "after_cid": b82_main["new_cid"],
            "target_edge_present": any(x["calibration"] == b81_main["new_cid"] for x in b82_main["security"]["source_passwords"]),
            "logical_image_diff": diff_images(b81_main["_image"], b82_main["_image"]),
        },
    ]

    type_summary: dict[str, dict[str, Any]] = {}
    for cpu_type in sorted({row["cpu_type"] for row in images}):
        rows = [row for row in images if row["cpu_type"] == cpu_type]
        type_summary[cpu_type] = {
            "cpu_type_export": rows[0]["cpu_type_export"],
            "logical_image_lengths": sorted({row["logical_image"]["length"] for row in rows}),
            "route_keys": sorted({row["route_key"] for row in rows}),
            "image_count": len(rows),
        }

    cpu86_rows = sorted(
        (row for row in images if row["cpu_type"] == "86"),
        key=lambda row: row["new_cid"],
    )
    cpu86_pairwise: list[dict[str, Any]] = []
    for left in cpu86_rows:
        counts: dict[str, int] = {}
        for right in cpu86_rows:
            counts[right["new_cid"]] = sum(
                left["_image"][offset:offset + 0x1000] != right["_image"][offset:offset + 0x1000]
                for offset in range(0, len(left["_image"]), 0x1000)
            )
        cpu86_pairwise.append({"new_cid": left["new_cid"], "changed_4k_blocks": counts})
    cpu86_common_blocks = [
        block
        for block in range(0x200000 // 0x1000)
        if len({row["_image"][block * 0x1000:(block + 1) * 0x1000] for row in cpu86_rows}) == 1
    ]

    public_images = []
    for row in images:
        public = {key: value for key, value in row.items() if not key.startswith("_")}
        public_images.append(public)

    result = {
        "schema_version": 1,
        "corpus": {
            "directory": "software/Techstream/cuw",
            "package_count": len(packages),
            "logical_image_count": len(images),
            "cpu_types": type_summary,
        },
        "packages": packages,
        "images": public_images,
        "cross_image_invariants": {
            "exact_common_prefix_length": common_prefix,
            "exact_common_prefix_sha256": sha256(images[0]["_image"][:common_prefix]),
            "common_first_4k_block_sha256": sha256(common_block0),
            "first_divergent_offset": common_prefix,
            "first_divergent_semantic": "per-image software-password field",
            "password_field_offset": 0x1004,
            "metadata_marker_offset": 0x1008,
            "metadata_marker_hex": METADATA_MARKER.hex().upper(),
            "part_identity_offset": 0x100C,
            "footer_magic_hex": FOOTER_MAGIC.hex().upper(),
            "footer_layout": "magic[16] || zero[4] || image[0x1004:0x1024]",
            "all_images_have_footer_layout": all(row["metadata"]["footer_repeats_metadata_window"] for row in public_images),
            "all_password_fields_match_decoded_zv_at_password_address": all(row["metadata"]["logical_password_equals_zv_password"] for row in public_images),
            "all_images_use_fill_word_hex": FILL_WORD.hex().upper(),
            "representation_boundary": (
                "The LZF-expanded images are strongly structured and preserve sparse/local update deltas, "
                "plaintext part metadata, a corpus-wide common 0x1004-byte prefix, and fixed footer layout. "
                "They are therefore not behaving as whole-image cryptographic ciphertext. Direct native "
                "V850E2 interpretation remains unproven and forced disassembly of representative data is incoherent; "
                "a Denso/VFOREST storage/coding transform remains bounded."
            ),
        },
        "cpu86_comparative_structure": {
            "pairwise_changed_4k_block_counts": cpu86_pairwise,
            "common_4k_blocks": cpu86_common_blocks,
            "common_4k_block_ranges": contiguous_ranges(cpu86_common_blocks),
        },
        "direct_update_comparisons": comparisons,
        "predecessor_password_closures": predecessor_password_closures,
        "multi_cpu_packages": [
            {
                "package": package["filename"],
                "archive_member_count": package["format4_archive_count"],
                "cpu_member_order": [
                    {
                        "cpu_section": row["cpu_section"],
                        "member_index": row["member_index"],
                        "cpu_type": row["cpu_type"],
                        "new_cid": row["new_cid"],
                        "archive_member_name": row["archive_member_name"],
                    }
                    for row in public_images if row["package"] == package["filename"]
                ],
            }
            for package in packages if package["format4_archive_count"] > 1
        ],
        "security_boundary": {
            "cpu_types_86_87_89_route_equivalence": (
                "All three real P5-CAN VFOREST size classes select integrated CCanFlashWriter/"
                "CCanVFORESTFlashWriter rows with PasswordAddress=0x100E, ByteOrder=0, FORESTTypeFlag=1, "
                "M16CTypeFlag=0, and FlagToUseCIDGetterAndFlashWriterDLL=0."
            ),
            "diagnostic_security_access": "legacy four-byte 27 01/02 path; key = seed XOR 00 60 60 00",
            "software_password": "independent CheckID control; source value from TargetData and new value from archive PasswordAddress",
            "modern_eps_transfer": "comparative only; no ECUAuthKey/ServiceAuthKey/SeedKey/Nonce/OffsetAddress/SecurityProperty2 evidence in these legacy integrated packages",
        },
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
