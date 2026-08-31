#!/usr/bin/env python3
"""Derive cross-ECU Toyota CUW SecurityAccess candidates from the local corpus.

This deliberately distinguishes values the CUW/Techstream frontend exposes from
backend ECU roots.  For every modern descriptor carrying ServiceAuthKey it:

* decodes the index-obfuscated 16-byte field;
* unwraps the exact Techstream selector-0 AES key to recover the effective
  SecurityAccess working key used to encrypt the ECU seed;
* checks the known EPS Unified specimen where ECUAuthKey is present; and
* computes, but labels only as a hypothesis, the ECUAuthKey-shaped wrapper that
  would produce the same working key if the recovered EPS boot root were shared
  by another ECU family.

It also tests the recovered EPS payload-build root against every retained CUW
that exposes the legacy/Unified ``SeedKey + Nonce + S-record`` image grammar.
That gives a direct CMAC oracle for cross-package root reuse. Finally, two
bounded negatives avoid obvious dead ends: working keys are compared against
simple DiagID KDFs under the three recovered EPS roots, and selected ReproStd
image pairs are tested against a small explicit set of one-step AES image-key
guesses. These negatives do not identify the actual ReproStd image transform or
disprove a shared backend root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import defaultdict
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from cuw_attach import parse_attach_bytes
from cuw_security_up import (
    SECURITY_UP_WRAP_KEY,
    firmware_security_access_working_key,
    unwrap_service_auth_key,
)
from techstream_paths import CUW_CORPUS_ROOT, REPO

DEFAULT_OUT = REPO / "data/generated/techstream_v18/cuw_cross_ecu_security_derivations.json"

# Recovered EPS-family roots.  Their cross-ECU reuse is the hypothesis under test.
EPS_PAYLOAD_BUILD_ROOT = bytes.fromhex("ba052435f8843f985fd1329d2b6117b0")
EPS_BOOT_SA_ROOT = bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044")
EPS_APPLICATION_SA_ROOT = bytes.fromhex("893e08418c741ffa2a9c044bffa55813")

# Exact control specimen: the descriptor contains both sides of the wrapping
# relation, so the frontend/backend algebra is independently checkable.
EPS_CONTROL_SPECIMEN = "T-0035-22.cuw"

# Pairs chosen because they provide useful differential oracles:
# - FRC: same family working key + same Nonce across adjacent revisions.
# - HV: same family working key + different Nonces across two packages.
IMAGE_PAIR_SPECS = (
    ("frc_same_nonce", "T-0062-23.cuw", "T-0149-24.cuw"),
    ("hv_different_nonce", "T-0003-25.cuw", "T-0005-25.cuw"),
)
IMAGE_SAMPLE_BYTES = 0x10000
EPS_PAYLOAD_GRAMMAR_PACKAGES = ("T-0015-20.cuw", "T-0035-22.cuw", "T-0036-22.cuw")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_index_obfuscated_16(value: str) -> bytes:
    """Decode Toyota's index-added ASCII-hex field to its first 16 data bytes."""
    raw = bytes.fromhex(value)
    if len(raw) < 32:
        raise ValueError("index-obfuscated CUW field is shorter than 32 bytes")
    ascii_hex = bytes((byte - index) & 0xFF for index, byte in enumerate(raw[:32]))
    decoded = bytes.fromhex(ascii_hex.decode("ascii"))
    if len(decoded) != 16:
        raise ValueError("decoded CUW field is not 16 bytes")
    return decoded


def read_attach(path: Path) -> tuple[dict[str, dict[str, str]], int, int]:
    """Read only the first CUW member (attach.att), avoiding multi-hundred-MB bodies."""
    with path.open("rb") as f:
        header = f.read(22)
        if len(header) != 22 or header[:13] != b"\x00CALIBRATION\x00":
            raise ValueError(f"{path.name}: invalid CUW header")
        format_type = header[13]
        name_len_raw = f.read(2)
        if len(name_len_raw) != 2:
            raise ValueError(f"{path.name}: truncated first-member name length")
        name_len = struct.unpack(">H", name_len_raw)[0]
        name = f.read(name_len)
        lengths = f.read(8)
        if len(lengths) != 8:
            raise ValueError(f"{path.name}: truncated first-member header")
        payload_len, _payload_crc = struct.unpack(">II", lengths)
        payload = f.read(payload_len)
        if len(payload) != payload_len:
            raise ValueError(f"{path.name}: truncated attach.att")
        if name != b"attach.att":
            raise ValueError(f"{path.name}: first member is {name!r}, not attach.att")
        first_member_end = f.tell()
    return parse_attach_bytes(payload), format_type, first_member_end


def first_logical_block(attach: dict[str, dict[str, str]]) -> tuple[str, dict[str, str]]:
    names = sorted(name for name in attach if name.startswith("LogicalBlock"))
    if not names:
        return "", {}
    return names[0], attach[names[0]]


def cmac(key: bytes, message: bytes) -> bytes:
    obj = CMAC.new(key, ciphermod=AES)
    obj.update(message)
    return obj.digest()


def simple_diag_derivation_matches(diag_id: str, working_key: bytes) -> list[str]:
    """Try only explicit, obvious public-ID KDFs; this is not a broad KDF search."""
    if not diag_id:
        return []
    value = int(diag_id, 16)
    if value > 0xFFFF or len(diag_id) != 4:
        return []
    forms = {
        "be16||0*14": value.to_bytes(2, "big") + bytes(14),
        "le16||0*14": value.to_bytes(2, "little") + bytes(14),
        "0*14||be16": bytes(14) + value.to_bytes(2, "big"),
        "0*14||le16": bytes(14) + value.to_bytes(2, "little"),
        "ascii||0": diag_id.encode("ascii") + bytes(16 - len(diag_id)),
        "0||ascii": bytes(16 - len(diag_id)) + diag_id.encode("ascii"),
    }
    roots = {
        "eps_payload_root": EPS_PAYLOAD_BUILD_ROOT,
        "eps_boot_sa_root": EPS_BOOT_SA_ROOT,
        "eps_application_sa_root": EPS_APPLICATION_SA_ROOT,
    }
    matches: list[str] = []
    for root_name, root in roots.items():
        for form_name, block in forms.items():
            if AES.new(root, AES.MODE_ECB).encrypt(block) == working_key:
                matches.append(f"AES-ENC({root_name},{form_name})")
            if AES.new(root, AES.MODE_ECB).decrypt(block) == working_key:
                matches.append(f"AES-DEC({root_name},{form_name})")
        if cmac(root, value.to_bytes(2, "big")) == working_key:
            matches.append(f"CMAC({root_name},diag_be16)")
        if cmac(root, diag_id.encode("ascii")) == working_key:
            matches.append(f"CMAC({root_name},diag_ascii)")
    return matches


def read_first_tail_member_header(path: Path, first_member_end: int, format_type: int) -> tuple[int, int, str]:
    if format_type != 0x67:
        raise ValueError(f"{path.name}: image-pair sampler currently requires format 0x67")
    with path.open("rb") as f:
        f.seek(first_member_end)
        count_raw = f.read(1)
        if not count_raw or count_raw[0] < 1:
            raise ValueError(f"{path.name}: no format-0x67 tail members")
        name_len_raw = f.read(2)
        name_len = struct.unpack(">H", name_len_raw)[0]
        name = f.read(name_len).decode("ascii")
        header = f.read(8)
        payload_len, _payload_crc = struct.unpack(">II", header)
        return f.tell(), payload_len, name


def materialize_srec_sample(path: Path, payload_offset: int, payload_len: int, start: int, count: int) -> bytes:
    """Stream an S3 member and materialize one contiguous range sample."""
    output = bytearray()
    expected = start
    end_offset = payload_offset + payload_len
    with path.open("rb") as f:
        f.seek(payload_offset)
        while f.tell() < end_offset and len(output) < count:
            line = f.readline()
            if not line:
                break
            if not line.startswith(b"S3"):
                continue
            try:
                byte_count = int(line[2:4], 16)
                address = int(line[4:12], 16)
                chunk = bytes.fromhex(line[12:12 + 2 * (byte_count - 5)].decode("ascii"))
            except (ValueError, UnicodeDecodeError):
                continue
            if address + len(chunk) <= start:
                continue
            if output and address > expected:
                break
            if address <= expected < address + len(chunk):
                chunk = chunk[expected - address:]
                take = min(len(chunk), count - len(output))
                output += chunk[:take]
                expected += take
    if len(output) != count:
        raise ValueError(f"{path.name}: materialized {len(output)} bytes, expected {count}")
    return bytes(output)


def byte_identity(left: bytes, right: bytes, skip: int = 32) -> float:
    n = min(len(left), len(right))
    if n <= skip:
        raise ValueError("identity sample too short")
    left = left[skip:n]
    right = right[skip:n]
    return sum(a == b for a, b in zip(left, right)) / len(left)


def candidate_image_keys(service_auth: bytes, working_key: bytes) -> dict[str, bytes]:
    return {
        "eps_payload_root": EPS_PAYLOAD_BUILD_ROOT,
        "eps_boot_sa_root": EPS_BOOT_SA_ROOT,
        "eps_application_sa_root": EPS_APPLICATION_SA_ROOT,
        "service_auth": service_auth,
        "working_key": working_key,
        "AES-ENC(eps_payload_root,working_key)": AES.new(EPS_PAYLOAD_BUILD_ROOT, AES.MODE_ECB).encrypt(working_key),
        "AES-DEC(eps_payload_root,working_key)": AES.new(EPS_PAYLOAD_BUILD_ROOT, AES.MODE_ECB).decrypt(working_key),
    }


def decrypt_candidate(ciphertext: bytes, key: bytes, nonce: bytes, mode: str) -> bytes:
    if mode == "CBC":
        return AES.new(key, AES.MODE_CBC, nonce).decrypt(ciphertext)
    if mode == "CFB128":
        return AES.new(key, AES.MODE_CFB, nonce, segment_size=128).decrypt(ciphertext)
    if mode == "OFB":
        return AES.new(key, AES.MODE_OFB, nonce).decrypt(ciphertext)
    if mode == "CTR_BE":
        return AES.new(key, AES.MODE_CTR, nonce=b"", initial_value=int.from_bytes(nonce, "big")).decrypt(ciphertext)
    if mode == "CTR_LE":
        return AES.new(key, AES.MODE_CTR, nonce=b"", initial_value=int.from_bytes(nonce, "little")).decrypt(ciphertext)
    raise ValueError(mode)


def image_pair_trial(name: str, left_name: str, right_name: str, packages: dict[str, dict]) -> dict:
    left_meta = packages[left_name]
    right_meta = packages[right_name]
    if left_meta["working_key"] != right_meta["working_key"]:
        raise ValueError(f"{name}: pair does not share the same working key")
    left_path = CUW_CORPUS_ROOT / left_name
    right_path = CUW_CORPUS_ROOT / right_name

    left_attach, left_format, left_first_end = read_attach(left_path)
    right_attach, right_format, right_first_end = read_attach(right_path)
    left_lb_name, _ = first_logical_block(left_attach)
    right_lb_name, _ = first_logical_block(right_attach)
    left_section = "ReproData" + left_lb_name.removeprefix("LogicalBlock")
    right_section = "ReproData" + right_lb_name.removeprefix("LogicalBlock")
    left_start = int(left_attach[left_section]["StartAddress"], 16)
    right_start = int(right_attach[right_section]["StartAddress"], 16)
    if left_start != right_start:
        raise ValueError(f"{name}: differing ReproData start addresses")

    left_payload_offset, left_payload_len, left_member = read_first_tail_member_header(left_path, left_first_end, left_format)
    right_payload_offset, right_payload_len, right_member = read_first_tail_member_header(right_path, right_first_end, right_format)
    left_sample = materialize_srec_sample(left_path, left_payload_offset, left_payload_len, left_start, IMAGE_SAMPLE_BYTES)
    right_sample = materialize_srec_sample(right_path, right_payload_offset, right_payload_len, right_start, IMAGE_SAMPLE_BYTES)
    usable = IMAGE_SAMPLE_BYTES // 16 * 16
    left_sample = left_sample[:usable]
    right_sample = right_sample[:usable]

    left_nonce = bytes.fromhex(left_meta["nonce"])
    right_nonce = bytes.fromhex(right_meta["nonce"])
    working_key = bytes.fromhex(left_meta["working_key"])
    service_auth = bytes.fromhex(left_meta["service_auth_key"])
    candidates = candidate_image_keys(service_auth, working_key)
    modes = ("CBC", "CFB128", "OFB", "CTR_BE", "CTR_LE")
    results = []
    for key_name, key in candidates.items():
        for mode in modes:
            left_plain = decrypt_candidate(left_sample, key, left_nonce, mode)
            right_plain = decrypt_candidate(right_sample, key, right_nonce, mode)
            results.append({
                "key": key_name,
                "mode": mode,
                "byte_identity_after_32": byte_identity(left_plain, right_plain),
            })
    best = max(results, key=lambda row: row["byte_identity_after_32"])
    return {
        "name": name,
        "left": left_name,
        "right": right_name,
        "left_member": left_member,
        "right_member": right_member,
        "reprodata_start": f"0x{left_start:X}",
        "sample_bytes": usable,
        "same_service_auth": left_meta["service_auth_key"] == right_meta["service_auth_key"],
        "same_working_key": True,
        "same_nonce": left_meta["nonce"] == right_meta["nonce"],
        "encoded_byte_identity_after_32": byte_identity(left_sample, right_sample),
        "tested_key_candidates": list(candidates),
        "tested_modes": list(modes),
        "best_candidate": best,
        "all_results": sorted(results, key=lambda row: (-row["byte_identity_after_32"], row["key"], row["mode"])),
        "boundary": "A chance-level result rejects only these explicit one-step AES guesses. It does not recover or exclude a more complex ECU-side image transform and does not disprove reuse of the EPS payload-build root.",
    }



def parse_srec_streams(data: bytes) -> list[list[bytes]]:
    lines = [m.group(0) for m in re.finditer(rb"S[03789][0-9A-Fa-f]+(?=\r\n)", data)]
    streams: list[list[bytes]] = []
    current: list[bytes] = []
    for line in lines:
        kind = line[1:2]
        if kind == b"0":
            if current:
                streams.append(current)
            current = [line]
        else:
            current.append(line)
            if kind == b"7":
                streams.append(current)
                current = []
    if current:
        streams.append(current)
    return streams


def srec_regions(stream: list[bytes]) -> list[tuple[int, bytes]]:
    records: dict[int, bytes] = {}
    for line in stream:
        if line[1:2] != b"3":
            continue
        count = int(line[2:4], 16)
        address = int(line[4:12], 16)
        records[address] = bytes.fromhex(line[12:12 + 2 * (count - 5)].decode("ascii"))
    regions: list[tuple[int, bytes]] = []
    for address in sorted(records):
        chunk = records[address]
        if regions and address == regions[-1][0] + len(regions[-1][1]):
            regions[-1] = (regions[-1][0], regions[-1][1] + chunk)
        else:
            regions.append((address, chunk))
    return regions


def eps_payload_root_trial(path: Path) -> dict:
    attach, _format_type, _first_member_end = read_attach(path)
    cpu_names = sorted(
        (name for name in attach if re.fullmatch(r"CPU\d+", name) and attach[name].get("SeedKey") and attach[name].get("Nonce")),
        key=lambda name: int(name[3:]),
    )
    streams = parse_srec_streams(path.read_bytes())
    if len(cpu_names) != len(streams):
        raise ValueError(f"{path.name}: CPU/stream mismatch {len(cpu_names)}/{len(streams)}")

    cpu_rows = []
    for cpu_name, stream in zip(cpu_names, streams):
        index = cpu_name[3:]
        cpu = attach[cpu_name]
        did201 = decode_index_obfuscated_16(cpu["SeedKey"])
        did202 = decode_index_obfuscated_16(cpu["Nonce"])
        derived = AES.new(EPS_PAYLOAD_BUILD_ROOT, AES.MODE_ECB).encrypt(did201)

        areas: dict[int, str] = {}
        for prefix, label in (("CPUImage", "body"), ("EraseRoutine", "erase")):
            section = attach.get(prefix + index, {})
            for area_index in range(1, int(section.get("NumberOfAreaSettings", "0")) + 1):
                key = f"{area_index:02d}_StartAddress"
                if key in section:
                    areas[int(section[key], 16)] = label

        regions = []
        for address, ciphertext in srec_regions(stream):
            if len(ciphertext) % 16:
                raise ValueError(f"{path.name}/{cpu_name}: unaligned region at 0x{address:X}")
            plaintext = AES.new(derived, AES.MODE_CBC, did202).decrypt(ciphertext)
            tag = cmac(derived, did202 + plaintext[:-16])
            regions.append({
                "kind": areas.get(address, "unknown"),
                "load_address": f"0x{address:X}",
                "size": len(ciphertext),
                "cmac_valid": tag == plaintext[-16:],
                "plaintext_sha256": sha256(plaintext),
            })
        cpu_rows.append({
            "cpu_section": cpu_name,
            "new_cid": cpu.get("NewCID", ""),
            "regions": regions,
            "all_regions_cmac_valid": bool(regions) and all(region["cmac_valid"] for region in regions),
        })

    return {
        "filename": path.name,
        "vehicle": attach.get("Vehicle", {}).get("VehicleName", ""),
        "diag_id": attach.get("Node01", {}).get("DiagID", ""),
        "required_spec_repro_ver": attach.get("Node01", {}).get("RequiredSpecReproVer", ""),
        "contact_type": attach.get("Vehicle", {}).get("ContactType", ""),
        "cpus": cpu_rows,
        "all_regions_cmac_valid": bool(cpu_rows) and all(cpu["all_regions_cmac_valid"] for cpu in cpu_rows),
    }

def build() -> dict:
    packages: dict[str, dict] = {}
    for path in sorted(CUW_CORPUS_ROOT.glob("*.cuw")):
        attach, format_type, first_member_end = read_attach(path)
        node = attach.get("Node01", {})
        service_field = node.get("ServiceAuthKey", "")
        if not service_field:
            continue
        service_auth = decode_index_obfuscated_16(service_field)
        working_key = unwrap_service_auth_key(service_auth)
        lb_name, lb = first_logical_block(attach)
        nonce = ""
        if lb.get("Nonce"):
            nonce = decode_index_obfuscated_16(lb["Nonce"]).hex()
        actual_ecu_auth = None
        if node.get("ECUAuthKey"):
            actual_ecu_auth = decode_index_obfuscated_16(node["ECUAuthKey"])
        hypothesized_ecu_auth = AES.new(EPS_BOOT_SA_ROOT, AES.MODE_ECB).encrypt(working_key)
        exact_eps_relation = None
        if actual_ecu_auth is not None:
            exact_eps_relation = firmware_security_access_working_key(EPS_BOOT_SA_ROOT, actual_ecu_auth) == working_key
        packages[path.name] = {
            "filename": path.name,
            "size": path.stat().st_size,
            "format_type": f"0x{format_type:02X}",
            "vehicle": attach.get("Vehicle", {}).get("VehicleName", ""),
            "diag_id": node.get("DiagID", ""),
            "contact_type": attach.get("Vehicle", {}).get("ContactType", ""),
            "logical_block": lb_name,
            "new_cid": lb.get("NewCID", ""),
            "target_calibration": lb.get("01_TargetCalibration", ""),
            "repro_method": lb.get("ReproMethod", ""),
            "service_auth_key": service_auth.hex(),
            "working_key": working_key.hex(),
            "nonce": nonce,
            "actual_ecu_auth_key": actual_ecu_auth.hex() if actual_ecu_auth else None,
            "eps_boot_root_hypothesis_ecu_auth_key": hypothesized_ecu_auth.hex(),
            "eps_boot_root_relation_exact_when_actual_present": exact_eps_relation,
            "simple_diag_kdf_matches": simple_diag_derivation_matches(node.get("DiagID", ""), working_key),
            "first_member_end": first_member_end,
        }

    groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for filename, row in packages.items():
        groups[(row["diag_id"], row["service_auth_key"], row["working_key"])].append(filename)
    group_rows = []
    for (diag_id, service_auth, working_key), filenames in sorted(groups.items()):
        group_rows.append({
            "diag_id": diag_id,
            "service_auth_key": service_auth,
            "working_key": working_key,
            "package_count": len(filenames),
            "packages": sorted(filenames),
            "eps_boot_root_hypothesis_ecu_auth_key": AES.new(EPS_BOOT_SA_ROOT, AES.MODE_ECB).encrypt(bytes.fromhex(working_key)).hex(),
            "simple_diag_kdf_match_count": sum(len(packages[name]["simple_diag_kdf_matches"]) for name in filenames),
        })

    control = packages.get(EPS_CONTROL_SPECIMEN)
    if not control or not control["actual_ecu_auth_key"] or control["eps_boot_root_relation_exact_when_actual_present"] is not True:
        raise ValueError("EPS control specimen does not reproduce the recovered backend relation")

    payload_trials = [eps_payload_root_trial(CUW_CORPUS_ROOT / filename) for filename in EPS_PAYLOAD_GRAMMAR_PACKAGES]
    pair_trials = [image_pair_trial(name, left, right, packages) for name, left, right in IMAGE_PAIR_SPECS]
    for trial in pair_trials:
        # Random byte identity is 1/256 ~= 0.003906.  Keep a generous ceiling:
        # these are merely dead-end guards, not a statistical cryptanalysis claim.
        if trial["best_candidate"]["byte_identity_after_32"] >= 0.01:
            raise ValueError(f"unexpectedly strong simple image-key candidate: {trial['best_candidate']}")

    return {
        "schema": "toyota-cuw-cross-ecu-security-derivations-v1",
        "roots": {
            "techstream_security_up_wrap_key": SECURITY_UP_WRAP_KEY.hex(),
            "eps_payload_build_root": EPS_PAYLOAD_BUILD_ROOT.hex(),
            "eps_boot_security_access_root": EPS_BOOT_SA_ROOT.hex(),
            "eps_application_security_access_root": EPS_APPLICATION_SA_ROOT.hex(),
            "cross_ecu_status": "The three EPS roots are proven across tracked EPS images only. Their reuse in FRC/HV/MG/Brake remains a hypothesis.",
        },
        "security_access_model": {
            "frontend": "Kwork = AES-128-ECB-DEC(Kwrap, ServiceAuthKey); response = AES-128-ECB-ENC(Kwork, ECU_seed)",
            "eps_unified_backend": "Kwork = AES-128-ECB-DEC(EPS_BOOT_SA_ROOT, ECUAuthKey); response = AES-128-ECB-ENC(Kwork, ECU_seed)",
            "universal_root_test": "If a non-EPS backend uses the same EPS root/wrapper algebra, its ECUAuthKey-shaped stored/provisioned value must equal AES-128-ECB-ENC(EPS_BOOT_SA_ROOT, Kwork).",
            "reprostd_boundary": "ReproStd uses a bare 27 01 seed request and the CUW ServiceAuthKey-derived working key; unlike Unified, it does not send ECUAuthKey in the request. Therefore the backend must already hold or derive an equivalent effective key by some ECU-local mechanism.",
        },
        "eps_control_specimen": {
            "filename": EPS_CONTROL_SPECIMEN,
            "service_auth_key": control["service_auth_key"],
            "working_key": control["working_key"],
            "actual_ecu_auth_key": control["actual_ecu_auth_key"],
            "eps_root_reproduces_actual_ecu_auth_key": control["eps_boot_root_hypothesis_ecu_auth_key"] == control["actual_ecu_auth_key"],
        },
        "credential_groups": group_rows,
        "packages": packages,
        "high_value_non_eps_predictions": {
            diag: next(row["eps_boot_root_hypothesis_ecu_auth_key"] for row in group_rows if row["diag_id"] == diag)
            for diag in ("0792", "07D2", "0724")
        },
        "simple_public_id_kdf_negative": {
            "tested": "AES-ENC/AES-DEC of six obvious 16-byte DiagID embeddings and CMAC of binary/ascii DiagID under the recovered EPS payload/boot/application roots",
            "matching_packages": [name for name, row in packages.items() if row["simple_diag_kdf_matches"]],
            "interpretation": "No tested working key is an obvious one-step derivation of the public diagnostic identifier under the recovered EPS roots. This is a bounded negative, not an exhaustive KDF search.",
        },
        "eps_payload_root_cuw_trials": {
            "grammar": "Kimage=AES-128-ECB-ENC(EPS_PAYLOAD_BUILD_ROOT, deobfuscate(SeedKey)); plaintext=AES-128-CBC-DEC(Kimage, deobfuscate(Nonce), ciphertext); CMAC is stored in the final 16 plaintext bytes",
            "packages_with_seedkey_nonce_grammar": [trial["filename"] for trial in payload_trials],
            "trials": payload_trials,
            "verified_shared_root_packages": [trial["filename"] for trial in payload_trials if trial["all_regions_cmac_valid"]],
            "rejected_same_root_packages": [trial["filename"] for trial in payload_trials if not trial["all_regions_cmac_valid"]],
            "boundary": "This proves payload-build-root reuse only for packages whose own SeedKey/Nonce grammar validates under the recovered EPS root. A CMAC failure can reflect a different root or a different generation-specific payload construction; it is not evidence about ReproStd packages that omit SeedKey.",
        },
        "reprostd_image_key_trials": pair_trials,
        "conclusion": {
            "verified": "Techstream/CUW exposes stable effective SecurityAccess working keys for several non-EPS ReproStd families. The T-0035 EPS control specimen exactly validates the frontend/backend wrapping algebra under the recovered EPS boot root. Separately, the recovered EPS payload-build root CMAC-validates every encrypted body/erase region in both T-0035-22 and T-0036-22, while the older T-0015-20 RAV4 EPS package rejects that same root on every region.",
            "hypothesis": "If that backend root and wrapper algebra are shared cross-ECU, the predicted ECUAuthKey-shaped values are concrete firmware-search fingerprints for FRC/HV/MG.",
            "not_proved": "The corpus alone cannot decide whether a ReproStd ECU stores Kwork directly, stores the predicted wrapper under a universal root, derives it another way, or uses a different backend root. The tested simple ReproStd image-key guesses also do not identify the image transform or settle payload-build-root reuse.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    result = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
