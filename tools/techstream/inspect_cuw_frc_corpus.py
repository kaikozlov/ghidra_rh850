#!/usr/bin/env python3
"""Inspect the external FRC (front-camera) CUW corpus and its payload boundary.

Six format-0x67 packages (DiagID 0792, Corolla-family front recognition
camera, e.g. T-0058-23 ``8646F1204300 -> 8646F1204500``) are the only
``ReproMethod=07`` (delta) packages in the local corpus.  This tool validates
each container, decodes the attach descriptor (including the index-obfuscated
``ServiceAuthKey``/``Nonce`` and per-area ``DigitalSignature`` fields), decodes
the Motorola S-record *framing* of the ``.xx`` members, and records corpus
invariants.  Five further format-0x67 camera packages with ``ReproMethod=01``
are recorded as the whole-repro contrast set. A lightweight identity/descriptor
inventory of every ``software/Techstream/cuw/*.cuw`` package is also emitted so acquisition
targets can be tested against the complete local corpus without deep-decoding every
payload.

Evidence boundaries kept by this tool (do not weaken them):

- The ``.xx`` members are Motorola S-record **framing**; the decoded flash
  data is high-entropy and its exact encoding is unknown.  No plaintext
  claim is made about the decoded image content.
- The ``Delta-*-write.datx`` member is the ``DeltaReproData`` payload.  The
  host ReproStd writer downloads it with RequestDownload
  ``dataFormatIdentifier 0x21`` (compact delta representation) consumed
  ECU-side as its delta input.  The exact transform is unknown — "decrypted"
  is NOT claimed.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

from techstream_paths import CUW_CORPUS_ROOT
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cuw_attach import parse_attach_bytes
from parse_cuw_container import parse as parse_container

DEFAULT_CORPUS = CUW_CORPUS_ROOT

# Pinned FRC corpus (DiagID 0792 / ReproMethod 07) and pinned whole-repro
# contrast set (ReproMethod 01).  The remaining corpus files are summarized in
# ``reference_inventory`` only; identities are asserted by the verification suite.
FRC_PACKAGES: dict[str, tuple[int, str]] = {
    "T-0058-23.cuw": (256400446, "ac5015118d3c5541c62ac3b0626a2d676681b3c4dee2ce6cb84ad547d116fdd9"),
    "T-0060-23.cuw": (256399534, "b3e4a7a951c74ef9985cf05f5151a36538e57bd84392da988d5f8102c652837f"),
    "T-0061-23.cuw": (256401572, "007a351fa0ac096af6c9c7c8085c6690c79abefea058e1fc438033ef3512bf94"),
    "T-0062-23.cuw": (257142135, "9971e3052d63dfe1fb262509ec59bcc8924db0082210117c63e9b01b73070e5b"),
    "T-0149-24.cuw": (257894251, "70bea932f3ae641e0d9fab99419aeb59ac76b08adcfeca97b9278d59d15ad6a8"),
    "T-0150-24.cuw": (257646163, "c28455c5b4ee6b48b4bf7b0fc51c6110969c6de9294bf488583e50727f91b5f1"),
}
CONTRAST_PACKAGES: dict[str, tuple[int, str]] = {
    "T-0003-25.cuw": (7872007, "ec52b1b673d9bf1c1497fc6f0ac2c5f7bfd8bf330907a2e9162c0c84eb9824b4"),
    "T-0005-25.cuw": (7872031, "3f72d67aa4da84aa02d4a9a3661ae458e1d2015c9fcba2f1e4a9961cb39f419e"),
    "T-0008-22.cuw": (35551267, "df77121f29aa45a8ebc203f9bec22147ed2e62362c8d267380ef21637ff90630"),
    "T-0009-22.cuw": (5481006, "a2cdb0667ae07822e5622569b8fbc9e552e51a94c616aff18d5fa66b29574018"),
    "T-0051-26.cuw": (13045570, "536bf4c05e7c135445547574c4bb321d4521e413765be0c6c2ec42d13a1c0117"),
}

FRC_DIAG_ID = "0792"
ROUTINE_RANGE = (0x008F6C00, 0x008F7170)  # from EraseAndReproRoutine101 area


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def entropy_bits(data: bytes) -> float:
    if not data:
        return 0.0
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in Counter(data).values())


def decode_index_obfuscated_hex(value: str) -> bytes:
    """Hex-decode then subtract the byte index (TMS-037 transform)."""
    raw = bytes.fromhex(value)
    return bytes((b - i) & 0xFF for i, b in enumerate(raw))


def scan_srec(payload: bytes) -> dict[str, Any]:
    """Fast S-record framing scan with count/checksum validation.

    Returns record census, bad-record count, contiguous data ranges, and the
    materialized bytes of the largest range.  Only the framing is interpreted.
    """
    kinds: Counter[str] = Counter()
    bad = 0
    total = 0
    ranges: list[tuple[int, int]] = []
    chunks: dict[tuple[int, int], bytes] = {}
    cur_start: int | None = None
    cur_end = 0
    buf = bytearray()
    addr_len = {"1": 2, "2": 3, "3": 4}
    for line in payload.split(b"\r\n"):
        if not line:
            continue
        total += 1
        if line[:1] != b"S" or line[1:2] not in b"0123456789":
            bad += 1
            continue
        kind = line[1:2]
        try:
            count = int(line[2:4], 16)
            body = binascii.unhexlify(line[4:])
        except ValueError:
            bad += 1
            continue
        if len(body) != count or (sum(body) + count) & 0xFF != 0xFF:
            bad += 1
            continue
        k = kind.decode()
        kinds[k] += 1
        if k in addr_len:
            al = addr_len[k]
            addr = int.from_bytes(body[:al], "big")
            chunk = body[al:-1]
            end = addr + len(chunk)
            if cur_start is None:
                cur_start, cur_end = addr, end
                buf = bytearray()
            elif addr == cur_end:
                cur_end = end
            elif addr > cur_end:
                ranges.append((cur_start, cur_end))
                chunks[(cur_start, cur_end)] = bytes(buf)
                cur_start, cur_end = addr, end
                buf = bytearray()
            else:
                bad += 1  # overlapping/retreating record
                continue
            buf += chunk
        # S0/S7..S9 carry no flash data here.
    if cur_start is not None:
        ranges.append((cur_start, cur_end))
        chunks[(cur_start, cur_end)] = bytes(buf)
    ordered = sorted(chunks)
    return {
        "record_count": total,
        "bad_record_count": bad,
        "record_kinds": dict(sorted(kinds.items())),
        "ranges": [{"start": a, "end": b, "length": b - a} for a, b in ordered],
        "range_bytes": {rng: bytes(chunks[rng]) for rng in ordered},
    }


def largest_range(scan: dict[str, Any]) -> tuple[int, int]:
    return max(scan["ranges"], key=lambda r: r["length"])


def block_digests(data: bytes, block: int = 16) -> list[bytes]:
    return [hashlib.blake2b(data[i:i + block], digest_size=8).digest()
            for i in range(0, len(data) - len(data) % block, block)]


def summarize_member_datx(payload: bytes) -> dict[str, Any]:
    digests = block_digests(payload)
    counts = Counter(digests)
    return {
        "length": len(payload),
        "length_mod_16": len(payload) % 16,
        "sha256": sha256(payload),
        "entropy_bits_per_byte": round(entropy_bits(payload), 3),
        "block_count": len(digests),
        "repeated_block_count": sum(1 for c in counts.values() if c > 1),
        "unique_block_count": len(counts),
        "first_block_hex": payload[:16].hex(),
    }


def descriptor_summary(attach: dict[str, dict[str, str]]) -> dict[str, Any]:
    fmt = attach.get("Format", {})
    kind = attach.get("KindOfCal", {})
    vehicle = attach.get("Vehicle", {})
    node = next((attach[s] for s in attach if s.startswith("Node")), {})
    block = next((attach[s] for s in attach if s.startswith("LogicalBlock")), {})

    def area(section: str) -> dict[str, Any] | None:
        raw = attach.get(section)
        if not raw:
            return None
        out: dict[str, Any] = {
            "start_address": raw.get("StartAddress", ""),
            "length": raw.get("Length", ""),
            "crc_empty": raw.get("CRC", "") == "",
            "cmac_empty": raw.get("CMAC", "") == "",
        }
        sig = raw.get("DigitalSignature", "")
        # CUW descriptor string fields are first index-obfuscated.  For the
        # FRC DigitalSignature field the deobfuscated value is itself ASCII
        # hex: 512 wire/descriptor characters encode a 256-byte signature.
        # Keep the transport representation and cryptographic object distinct.
        decoded_ascii = decode_index_obfuscated_hex(sig) if sig else b""
        signature = b""
        encoding = ""
        if decoded_ascii:
            try:
                signature = bytes.fromhex(decoded_ascii.decode("ascii"))
                encoding = "ascii-hex"
            except (UnicodeDecodeError, ValueError):
                # Preserve unknown descriptor encodings without silently
                # reclassifying their byte length as a crypto-object width.
                encoding = "opaque"
        out["digital_signature_encoding"] = encoding
        out["digital_signature_wire_ascii_length"] = len(decoded_ascii)
        out["digital_signature_wire_ascii_sha256"] = sha256(decoded_ascii) if decoded_ascii else ""
        out["digital_signature_length"] = len(signature)
        out["digital_signature_sha256"] = sha256(signature) if signature else ""
        return out

    areas = {name: area(name) for name in (
        "ReproData101", "EraseAndReproRoutine101",
        "DeltaReproData101", "DeltaEraseAndReproRoutine101")}

    # ServiceAuthKey lives in the Node01 section; Nonce in the LogicalBlock
    # section (verified on all six FRC descriptors).
    def decoded_hex(section: dict[str, str], key: str) -> str:
        value = section.get(key, "")
        if not value:
            return ""
        try:
            return decode_index_obfuscated_hex(value).decode("ascii")
        except (UnicodeDecodeError, ValueError):
            return ""

    return {
        "format_version": fmt.get("Version", ""),
        "version_for_cfm2": fmt.get("VersionForCFM2", ""),
        "is_controlled_by_scc": kind.get("IsControlledBySCC", ""),
        "is_blank_ecu": kind.get("IsBlankECU", ""),
        "vehicle_name": vehicle.get("VehicleName", ""),
        "vehicle_type": vehicle.get("VehicleType", ""),
        "engine_type": vehicle.get("EngineType", ""),
        "model_year": vehicle.get("ModelYear", ""),
        "date_of_issue": vehicle.get("DateOfIssue", ""),
        "contact_type": vehicle.get("ContactType", ""),
        "diag_id": node.get("DiagID", ""),
        "required_spec_repro_ver": node.get("RequiredSpecReproVer", ""),
        "gateway_mode_1": node.get("01_GatewayMode", ""),
        "gateway_diag_id_1": node.get("01_GatewayDiagID", ""),
        "new_cid": block.get("NewCID", ""),
        "repro_method": block.get("ReproMethod", ""),
        "security_property2": block.get("SecurityProperty2", ""),
        "p4_server_max_time": block.get("P4ServerMaxTime", ""),
        "source_target_calibration_1": block.get("01_TargetCalibration", ""),
        "service_auth_key_decoded": decoded_hex(node, "ServiceAuthKey"),
        "nonce_decoded": decoded_hex(block, "Nonce"),
        "area_sections_present": [s for s in areas if areas[s]],
        "areas": {k: v for k, v in areas.items() if v},
    }


def inspect_package(path: Path, deep: bool = True) -> tuple[dict[str, Any], dict[str, bytes]]:
    data = path.read_bytes()
    parsed = parse_container(data)
    out: dict[str, Any] = {
        "filename": path.name,
        "size": len(data),
        "sha256": sha256(data),
        "format_type": hex(parsed["format_type"]),
        "outer_crc_ok": not parsed["errors"],
        "declared_total_matches_file": parsed["declared_total_size"] == len(data),
        "errors": parsed["errors"],
    }
    # descriptor
    end = parsed["first_member_end"]
    attach = data[end - parsed["payload_length"]:end]
    out["attach_size"] = parsed["payload_length"]
    out["attach_sha256"] = sha256(attach)
    desc = parse_attach_bytes(attach)
    out["descriptor"] = descriptor_summary(desc)
    out["descriptor_sections"] = sorted(desc)

    members = parsed.get("format67_members") or []
    out["member_count"] = parsed.get("format67_member_count")
    out["members"] = [
        {
            "name": m["name"],
            "payload_length": m["payload_length"],
            "payload_sha256": m["payload_sha256"],
            "payload_crc_ok": m["computed_payload_crc32"] == m["payload_crc32"],
        }
        for m in members
    ]
    if not deep:
        return out, {}

    by_name = {m["name"]: data[m["payload_offset"]:m["payload_offset"] + m["payload_length"]]
               for m in members}
    whole_name = desc.get("LogicalBlock101", {}).get("WholeReproFileName", "")
    delta_name = desc.get("LogicalBlock101", {}).get("DeltaReproDataFileName", "")
    routine_name = desc.get("LogicalBlock101", {}).get("DeltaEraseAndReproRoutineFileName", "")

    images: dict[str, bytes] = {}
    deep_entropy_probe = path.name == "T-0058-23.cuw"
    if whole_name and whole_name in by_name:
        scan = scan_srec(by_name[whole_name])
        flash = largest_range(scan)
        image = scan["range_bytes"][(flash["start"], flash["end"])]
        images[whole_name] = image
        routine_slot = b""
        for rng in scan["ranges"]:
            if 0 < rng["length"] <= 0x1000:
                routine_slot = scan["range_bytes"][(rng["start"], rng["end"])]
        out["whole_repro"] = {
            "member": whole_name,
            "record_count": scan["record_count"],
            "bad_record_count": scan["bad_record_count"],
            "record_kinds": scan["record_kinds"],
            "ranges": scan["ranges"],
            "flash_region": flash,
            "decoded_image_length": len(image),
            "decoded_image_sha256": sha256(image),
            "decoded_image_entropy_bits": round(entropy_bits(image), 7),
            "first_32_bytes_hex": image[:32].hex(),
            "first_64_bytes_hex": image[:64].hex(),
            "routine_slot_length": len(routine_slot),
            "routine_slot_sha256": sha256(routine_slot) if routine_slot else "",
        }
        if deep_entropy_probe:
            # Complete non-overlapping 4-KiB window scan of the decoded flash
            # body: no low-entropy/plaintext island.  Supports "encoded body
            # opaque/high-entropy throughout" only — NOT any specific crypto
            # transform (ECB vs stream etc. cannot be distinguished).
            windows = [image[i:i + 0x1000] for i in range(0, len(image) - 0xFFF, 0x1000)]
            out["entropy_probe"] = {
                "package": path.name,
                "global_entropy_bits": round(entropy_bits(image), 7),
                "window_size": 0x1000,
                "window_count": len(windows),
                "min_window_entropy_bits": round(min(entropy_bits(w) for w in windows), 5),
                "printable_ascii_fraction": round(
                    sum(1 for b in image[::97] if 0x20 <= b <= 0x7E) / len(image[::97]), 5),
                "zero_fraction": round(image.count(0) / len(image), 6),
                "ff_fraction": round(image.count(0xFF) / len(image), 6),
                "routine_range_entropy_bits": round(entropy_bits(routine_slot), 6) if routine_slot else None,
            }
    if routine_name and routine_name in by_name:
        scan = scan_srec(by_name[routine_name])
        # The whole-repro image embeds the same routine bytes at the routine
        # slot; assert the identity explicitly (holds on all six packages).
        routine = scan["range_bytes"].get((ROUTINE_RANGE[0], ROUTINE_RANGE[1]), b"")
        out["routine_member"] = {
            "member": routine_name,
            "raw_sha256": sha256(by_name[routine_name]),
            "record_count": scan["record_count"],
            "bad_record_count": scan["bad_record_count"],
            "record_kinds": scan["record_kinds"],
            "ranges": scan["ranges"],
            "decoded_length": len(routine),
            "decoded_sha256": sha256(routine) if routine else "",
        }
    if delta_name and delta_name in by_name:
        out["delta_datx"] = summarize_member_datx(by_name[delta_name])
    return out, by_name


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    packages: list[dict[str, Any]] = []
    images_by_pkg: dict[str, bytes] = {}
    datx_by_pkg: dict[str, bytes] = {}
    contrast: list[dict[str, Any]] = []

    for name, (size, digest) in FRC_PACKAGES.items():
        path = args.corpus / name
        summary, payloads = inspect_package(path, deep=True)
        if summary["size"] != size or summary["sha256"] != digest:
            summary["errors"].append("FRC package identity mismatch against pinned corpus identity")
        packages.append(summary)
        for member, payload in payloads.items():
            if member.endswith(".xx") and not member.startswith("Delta-"):
                images_by_pkg[name] = payload
            elif member.endswith(".datx"):
                datx_by_pkg[name] = payload

    for name, (size, digest) in CONTRAST_PACKAGES.items():
        path = args.corpus / name
        if not path.is_file():
            continue
        summary, _ = inspect_package(path, deep=False)
        if summary["size"] != size or summary["sha256"] != digest:
            summary["errors"].append("contrast package identity mismatch against pinned corpus identity")
        contrast.append(summary)

    # ---- complete local reference inventory (descriptor/identity only)
    # Reuse the already-inspected focal/contrast packages and inspect only the
    # remainder.  This keeps acquisition negatives tied to the actual local
    # corpus without doing S-record/entropy work on unrelated packages.
    cached = {row["filename"]: row for row in packages + contrast}
    reference_inventory: list[dict[str, Any]] = []
    diag_counts: Counter[str] = Counter()
    for path in sorted(args.corpus.glob("*.cuw"), key=lambda p: p.name):
        summary = cached.get(path.name)
        if summary is None:
            summary, _ = inspect_package(path, deep=False)
        descriptor = summary.get("descriptor", {})
        diag_id = descriptor.get("diag_id", "")
        diag_counts[diag_id] += 1
        reference_inventory.append({
            "filename": summary["filename"],
            "size": summary["size"],
            "sha256": summary["sha256"],
            "format_type": summary["format_type"],
            "outer_crc_ok": summary["outer_crc_ok"],
            "declared_total_matches_file": summary["declared_total_matches_file"],
            "diag_id": diag_id,
            "contact_type": descriptor.get("contact_type", ""),
            "new_cid": descriptor.get("new_cid", ""),
            "repro_method": descriptor.get("repro_method", ""),
            "required_spec_repro_ver": descriptor.get("required_spec_repro_ver", ""),
        })
    abs_matches = [row["filename"] for row in reference_inventory if row["diag_id"] == "07B0"]

    # ---- cross-package invariants
    routine_shas = {p["filename"]: p["routine_member"]["raw_sha256"] for p in packages if "routine_member" in p}
    routine_slot_matches = all(
        p["whole_repro"]["routine_slot_sha256"] == p["routine_member"]["decoded_sha256"]
        for p in packages if "whole_repro" in p and "routine_member" in p)
    digests = {p["filename"]: p["whole_repro"]["decoded_image_sha256"] for p in packages if "whole_repro" in p}
    prefixes = {p["filename"]: p["whole_repro"]["first_32_bytes_hex"] for p in packages if "whole_repro" in p}

    shared_image_groups: dict[str, list[str]] = {}
    for fn, dg in digests.items():
        shared_image_groups.setdefault(dg, []).append(fn)

    # delta chains: this package's source CID == another package's NewCID.
    # A chain is *closed* when the predecessor package is in the corpus, so
    # both the old and the new whole-repro image are locally available.
    by_newcid = {p["descriptor"]["new_cid"]: p for p in packages}
    chains = []
    for p in packages:
        src = p["descriptor"]["source_target_calibration_1"]
        new = p["descriptor"]["new_cid"]
        tgt = by_newcid.get(src)
        chains.append({
            "package": p["filename"],
            "source_calibration": src,
            "new_calibration": new,
            "source_package_in_corpus": tgt["filename"] if tgt else "",
        })

    direct_comparisons = []
    for chain in chains:
        src_pkg = chain["source_package_in_corpus"]
        if not src_pkg:
            continue
        new_pkg = chain["package"]
        scan_new = scan_srec(images_by_pkg[new_pkg])
        scan_old = scan_srec(images_by_pkg[src_pkg])
        a = scan_new["range_bytes"][(largest_range(scan_new)["start"], largest_range(scan_new)["end"])]
        b = scan_old["range_bytes"][(largest_range(scan_old)["start"], largest_range(scan_old)["end"])]
        if len(a) != len(b):
            direct_comparisons.append({
                "new_package": new_pkg, "old_package": src_pkg,
                "length_mismatch": [len(a), len(b)],
            })
            continue
        same = sum(1 for x, y in zip(a, b) if x == y)
        blocks_a = set(block_digests(a))
        shared_blocks = sum(1 for d in block_digests(b) if d in blocks_a)
        # longest identical run >= 8 beyond the shared 32-byte prefix
        longest = run = 0
        for x, y in zip(a[32:], b[32:]):
            run = run + 1 if x == y else 0
            longest = max(longest, run)
        prefix_shared = a[:32] == b[:32] and a[32] != b[32]
        direct_comparisons.append({
            "new_package": new_pkg,
            "old_package": src_pkg,
            "length": len(a),
            "identical_byte_count": same,
            "identical_fraction": round(same / len(a), 6),
            "expected_chance_fraction": round(1 / 256, 6),
            "shared_16b_block_count": shared_blocks,
            "shared_16b_blocks_beyond_prefix": max(0, shared_blocks - 2),
            "longest_run_beyond_prefix32": longest,
            "exact_32b_prefix_shared": a[:32] == b[:32],
            "prefix32_is_exactly_shared": prefix_shared,
        })

    # ReproStd whole-image contrast with a useful crypto differential.  The two
    # 0x7D2 packages use the same family ServiceAuthKey and declare the same
    # erase/repro routine target + CMAC, but carry different descriptor Nonces.
    # Their stored routine representations are chance-correlated.  This is a
    # bounded correlation/oracle: it does not prove that Nonce alone causes the
    # ciphertext change or identify the exact integrity object/cipher.
    nonce_pair_names = ("T-0003-25.cuw", "T-0005-25.cuw")
    nonce_rows: list[dict[str, Any]] = []
    for name in nonce_pair_names:
        path = args.corpus / name
        data = path.read_bytes()
        parsed = parse_container(data)
        end = parsed["first_member_end"]
        desc = parse_attach_bytes(data[end - parsed["payload_length"]:end])
        members = parsed.get("format67_members") or []
        whole_name = desc["LogicalBlock101"]["WholeReproFileName"]
        member = next(m for m in members if m["name"] == whole_name)
        payload = data[member["payload_offset"]:member["payload_offset"] + member["payload_length"]]
        scan = scan_srec(payload)
        routine_area = desc["EraseAndReproRoutine101"]
        routine_range = (int(routine_area["StartAddress"], 16),
                         int(routine_area["StartAddress"], 16) + int(routine_area["Length"], 16))
        routine = scan["range_bytes"][routine_range]
        cmac_ascii = decode_index_obfuscated_hex(routine_area["CMAC"])
        cmac = bytes.fromhex(cmac_ascii.decode("ascii"))
        nonce_rows.append({
            "filename": name,
            "diag_id": desc["Node01"]["DiagID"],
            "new_cid": desc["LogicalBlock101"]["NewCID"],
            "service_auth_key": decode_index_obfuscated_hex(desc["Node01"]["ServiceAuthKey"]).decode("ascii"),
            "nonce": decode_index_obfuscated_hex(desc["LogicalBlock101"]["Nonce"]).decode("ascii"),
            "routine_start": routine_area["StartAddress"],
            "routine_length": routine_area["Length"],
            "routine_cmac": cmac.hex().upper(),
            "routine_stored_sha256": sha256(routine),
            "routine_stored_first_32_bytes_hex": routine[:32].hex(),
            "routine_stored_bytes": routine,
        })
    left, right = nonce_rows
    lr = left.pop("routine_stored_bytes")
    rr = right.pop("routine_stored_bytes")
    same_routine_bytes = sum(a == b for a, b in zip(lr, rr))
    left_blocks = set(block_digests(lr))
    shared_routine_blocks = sum(1 for d in block_digests(rr) if d in left_blocks)
    reprostd_nonce_differential = {
        "packages": nonce_rows,
        "same_diag_id": left["diag_id"] == right["diag_id"] == "07D2",
        "same_service_auth_key": left["service_auth_key"] == right["service_auth_key"],
        "different_nonce": left["nonce"] != right["nonce"],
        "same_routine_target": (
            left["routine_start"] == right["routine_start"]
            and left["routine_length"] == right["routine_length"]
        ),
        "same_routine_cmac": left["routine_cmac"] == right["routine_cmac"],
        "routine_stored_identical_fraction": round(same_routine_bytes / len(lr), 6),
        "routine_stored_expected_chance_fraction": round(1 / 256, 6),
        "routine_stored_shared_16b_blocks": shared_routine_blocks,
        "bounded_interpretation": (
            "The two 0x7D2 ReproStd packages share family ServiceAuthKey plus the same declared "
            "erase/repro routine address/length and 16-byte CMAC, but carry different descriptor Nonces "
            "and chance-correlated stored routine bytes. This proves the serialized encrypted routine "
            "representation is not fixed by target address/length/CMAC + ServiceAuthKey alone. It does "
            "not prove Nonce causality, the plaintext routine identity, or the exact cipher/IV/KDF. "
            "Combined with the selected ReproStd host route's lack of explicit Nonce transfer, any "
            "package-specific crypto context must be embedded/derived or otherwise ECU-local."
        ),
    }

    # datx corpus census
    datx_first_blocks = {fn: p[:16].hex() for fn, p in datx_by_pkg.items()}
    datx_shared_first_block = len(set(datx_first_blocks.values())) == 1
    cross_datx_shared_blocks = 0
    datx_list = list(datx_by_pkg.items())
    for i in range(len(datx_list)):
        # exclude each file's leading (shared) block from the census
        set_a = set(block_digests(datx_list[i][1])[1:])
        for j in range(i + 1, len(datx_list)):
            cross_datx_shared_blocks += sum(1 for d in block_digests(datx_list[j][1])[1:] if d in set_a)

    result = {
        "schema_version": 3,
        "reference_inventory": {
            "package_count": len(reference_inventory),
            "diag_id_counts": dict(sorted(diag_counts.items())),
            "packages": reference_inventory,
            "category_435_acquisition": {
                "target_diag_id": "07B0",
                "matching_packages": abs_matches,
                "positive_controls": {
                    "front_recognition_camera_0792": diag_counts.get("0792", 0),
                    "power_steering_07A1": diag_counts.get("07A1", 0),
                },
                "boundary": (
                    "Local software/Techstream/cuw inventory only. An empty 07B0 match list proves that the "
                    "currently pinned local corpus lacks a category-435 candidate package; it does "
                    "not prove Toyota/TIS has no such calibration package."
                ),
            },
        },
        "corpus": {
            "directory": str(args.corpus.relative_to(REPO)) if args.corpus.is_relative_to(REPO) else str(args.corpus),
            "frc_package_count": len(packages),
            "frc_descriptor_signature": {
                "contact_type": "P5-Unified",
                "required_spec_repro_ver": "04",
                "diag_id": FRC_DIAG_ID,
                "repro_method": "07",
                "security_property2": "9C",
                "is_controlled_by_scc": "1",
                "is_blank_ecu": "0",
                "gateway_diag_id_1": "07505F",
            },
            "contrast_format67_package_count": len(contrast),
            "contrast_descriptor_signature": {
                "repro_method": "01",
                "security_property2": "98",
                "is_controlled_by_scc": "0",
            },
        },
        "packages": packages,
        "contrast_packages": contrast,
        "cross_package_invariants": {
            "routine_member_raw_identical_across_all": len(set(routine_shas.values())) == 1,
            "routine_member_raw_sha256": next(iter(set(routine_shas.values())), ""),
            "routine_slot_in_whole_image_equals_routine_member": routine_slot_matches,
            "whole_repro_shared_target_groups": {k: v for k, v in shared_image_groups.items() if len(v) > 1},
            "distinct_decoded_image_count": len(set(digests.values())),
            "decoded_images_share_first_32_bytes": len(set(prefixes.values())) == 1,
            "first_32_bytes_hex": next(iter(set(prefixes.values())), ""),
            "first_32_bytes_is_exactly_the_shared_prefix": (
                len({bytes.fromhex(first64)[32] for first64 in {
                    p["whole_repro"]["decoded_image_sha256"]: p["whole_repro"]["first_64_bytes_hex"]
                    for p in packages if "whole_repro" in p
                }.values()}) == len(set(digests.values()))
            ),
            "datx_sizes_are_16_byte_multiples": all(p["delta_datx"]["length_mod_16"] == 0 for p in packages if "delta_datx" in p),
            "datx_shared_single_leading_block": datx_shared_first_block,
            "datx_shared_leading_block_hex": next(iter(set(datx_first_blocks.values())), ""),
            "datx_interior_cross_package_shared_blocks": cross_datx_shared_blocks,
        },
        "delta_chains": chains,
        "direct_update_comparisons": direct_comparisons,
        "reprostd_nonce_differential": reprostd_nonce_differential,
        "transform_boundary": {
            "xx_members": "Motorola S-record framing carrying an encrypted target representation. ReproStd downloads whole/routine data with UDS RequestDownload DFI 0x01; by the UDS dataFormatIdentifier definition that is compression method 0 plus manufacturer-specific encryption method 1. The exact FRC cipher/key/IV remain unknown.",
            "datx_members": "DeltaReproData payload; ReproStd downloads it with DFI 0x21. UDS assigns the high nibble to compressionMethod and the low nibble to encryptingMethod; Toyota host code independently names high-nibble method 2 as DeltaRepro, so this is Toyota delta method 2 layered with the same manufacturer-specific encryption method 1.",
            "routine_member": "byte-identical encrypted blob in all six packages; it decodes from S-record framing to the same 1392 stored bytes every whole image carries at 0x008F6C00. Exact plaintext/ECU-side interpretation remain unknown.",
            "data_format_identifier": {
                "whole_or_routine": "0x01",
                "compression": "0x11",
                "delta": "0x21",
                "uds_semantics": "high nibble=compressionMethod, low nibble=encryptingMethod; 0 means no transform and nonzero values are manufacturer-specific",
                "toyota_host_names": "whole/default -> 0x01; CompressionRepro -> 0x11; DeltaRepro -> 0x21",
                "bounded_conclusion": "all ReproStd payload families here use manufacturer-specific encryptingMethod 1; compression method 1 is Toyota CompressionRepro and compression method 2 is Toyota DeltaRepro",
            },
            "host_transform": "host parses S-record framing for .xx members and passes the decoded encrypted payload bytes; .datx remains an opaque raw member buffer. No host-side payload decryption/decompression is recovered in the selected ReproStd path.",
            "selected_route_key_material": "The selected ReproStd prepare path enters 10 02, sends bare 27 01, extracts exactly 16 seed bytes from 67 01, calls CalcSeedKey with GetServiceAuthKey + that seed, then sends 27 02 plus a 16-byte key and expects 67 02. It imports GetServiceAuthKey but not GetNonce/GetSeedKey/GetECUAuthKey/GetSecurityProperty2; ReproStd flash imports only GetReproMethodType from these security/format getters. The recovered prepare/flash send grammar has no explicit Nonce/SeedKey transfer, so the selected route supplies no host-side nonce/seed material to the FRC payload decoder. This does not prove the package-generation Nonce is cryptographically irrelevant.",
            "member_read_path": "format-0x67 members are raw length+CRC32 payloads; the CUW.dll read path is a chunked fread(dst,1,0xFFF) loop (reader 0x1002BEB0, push site 0x1002BF83) with a whole-file CRC32 gate (0x1002A3B0, called from loader 0x10031A20 at 0x10031C0C; mismatch -> Error FileCRC); CDeltaReproArchiveCtrlr (RTTI 0x1008A9A0, vtable 0x1007C918, single deleting-dtor virtual 0x10066DC0, global instance 0x1008CA0C) holds only 0xAC-stride path/name/count entries with no payload pointer or byte fields - orchestration-only; CAES encrypt/decrypt callers are only 0x1001B9B2/0x1005AC52/0x1005AD02 (INI parameter decode, SecurityUp helpers), never the member path; TCUWCalibrationFile.dll and TCUWCanReproStdFlashWriter.dll have no crypto or compression imports.",
            "entropy_support": "encrypted flash body is high-entropy throughout (T-0058: global 7.9999977 bits/byte, minimum complete 4-KiB window 7.93098; routine range 7.8798 over 1392 B). The two corpus-internal updates carry only 1,503,040 B and 1,254,976 B of delta input (1.76% and 1.47% of the 85,458,944-B target span) while their stored whole-image bytes decorrelate to chance immediately after a shared 32-byte prefix. Localized plaintext edits therefore do not remain localized in the stored representation.",
            "cbc_shape_hypothesis": "All five distinct FRC target images share exactly the first two 16-byte stored blocks and first differ at byte 32, then the two locally closed small-delta updates remain chance-correlated for the rest of the 85,458,944-byte image. Fixed-key/fixed-IV CBC with two common plaintext header blocks followed by a changed third block produces exactly this prefix-then-avalanche shape and is a better fit than a whole-image rekey, which would not naturally preserve the identical ciphertext prefix. This is a structural hypothesis only: a custom chaining transform, partially clear/encrypted envelope, or another construction can reproduce the same observation; no FRC key/plaintext/cipher implementation has been recovered.",
            "digital_signature": "RequiredSpecReproVer04 FRC descriptors carry 512 deobfuscated ASCII-hex characters encoding a 256-byte signature. The ReproStd RoutineControl builder selects the alternate integrity field and declares length 0x0100; RequiredSpec03 instead declares a 0x0010 CMAC. Whole/delta entries share the same target signature, so the exact signed object is not either serialized member byte stream directly.",
        },
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k in ("corpus", "cross_package_invariants")},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
