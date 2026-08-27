#!/usr/bin/env python3
"""Extract secret-free Toyota T-0035-22 FACI evidence from the pinned CUW.

The CUW carries two encrypted 4 KiB manufacturer erase/program routines. This
analyzer derives their package key from the already-recovered payload-build root,
validates both CMACs, and emits only source identities, plaintext hashes, selected
Ghidra-reviewed function-body hashes, and bounded semantic facts. No seed, nonce,
derived key, or plaintext payload is written to the tracked output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

REPO = Path(__file__).resolve().parents[2]
DEFAULT_CUW = REPO / "software/Techstream/cuw/T-0035-22.cuw"
DEFAULT_REFERENCE = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
DEFAULT_OUT = REPO / "data/generated/techstream_v18/t0035_faci_backend_evidence.json"
PAYLOAD_BUILD_ROOT_OFFSET = 0xBFD8
EXPECTED_CUW_SHA256 = "9882b1b6dd6acda2d142a2825eda396b0a425e41c13f822b9a18e022d4c43e81"
EXPECTED_CUW_SIZE = 5725237

# Function boundaries recovered from disposable Ghidra imports of the two exact
# CMAC-validated plaintext erase routines. Stored as payload-relative offsets.
FUNCTIONS = {
    "8965F3401200": {
        "frdy": (0x154, 14),
        "fentry_enter": (0x162, 100),
        "cmdlk": (0x1C6, 14),
        "fstatr_error": (0x1D4, 14),
        "forced_stop_cleanup": (0x1E2, 126),
        "pe_mode": (0x260, 92),
        "program_256b": (0x2BC, 128),
        "erase_block": (0x382, 32),
        "fentry_exit": (0x40A, 92),
        "operation_poll": (0x478, 88),
    },
    "8965F3402200": {
        "frdy": (0x164, 14),
        "fentry_enter": (0x172, 100),
        "cmdlk": (0x1D6, 14),
        "fstatr_error": (0x1E4, 14),
        "forced_stop_cleanup": (0x1F2, 126),
        "pe_mode": (0x270, 92),
        "program_256b": (0x2CC, 128),
        "erase_block": (0x392, 32),
        "fentry_exit": (0x41A, 92),
        "operation_poll": (0x488, 88),
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_ini(data: bytes) -> dict[str, dict[str, str]]:
    end = data.find(b"\x02\x00")
    if end < 0:
        raise ValueError("CUW INI terminator not found")
    text = data[:end].decode("latin-1", errors="strict")
    out: dict[str, dict[str, str]] = {}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            out[current] = {}
        elif "=" in line and current is not None:
            key, value = line.split("=", 1)
            out[current][key.strip()] = value.strip()
    return out


def parse_streams(data: bytes) -> list[list[bytes]]:
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


def stream_regions(stream: list[bytes]) -> list[tuple[int, bytes]]:
    records: dict[int, bytes] = {}
    for line in stream:
        if line[1:2] != b"3":
            continue
        count = int(line[2:4], 16)
        addr = int(line[4:12], 16)
        records[addr] = bytes.fromhex(line[12:12 + 2 * (count - 5)].decode("ascii"))
    regions: list[tuple[int, bytes]] = []
    for addr in sorted(records):
        chunk = records[addr]
        if regions and addr == regions[-1][0] + len(regions[-1][1]):
            regions[-1] = (regions[-1][0], regions[-1][1] + chunk)
        else:
            regions.append((addr, chunk))
    return regions


def deobfuscate_16(raw_hex: str) -> bytes:
    raw = bytes.fromhex(raw_hex)
    if len(raw) != 32:
        raise ValueError("expected 32-byte obfuscated 16-byte value")
    shifted = bytes((b - i) & 0xFF for i, b in enumerate(raw))
    return bytes.fromhex(shifted.decode("ascii"))


def decrypt_region(ciphertext: bytes, build_root: bytes, did201: bytes, did202: bytes) -> tuple[bytes, bool]:
    if len(ciphertext) % 16:
        raise ValueError("encrypted CUW region is not block aligned")
    derived = AES.new(build_root, AES.MODE_ECB).encrypt(did201)
    plaintext = AES.new(derived, AES.MODE_CBC, did202).decrypt(ciphertext)
    mac = CMAC.new(derived, ciphermod=AES)
    mac.update(did202 + plaintext[:-16])
    return plaintext, mac.digest() == plaintext[-16:]


def build(cuw_path: Path, reference_path: Path) -> dict[str, object]:
    source = cuw_path.read_bytes()
    if len(source) != EXPECTED_CUW_SIZE or sha256(source) != EXPECTED_CUW_SHA256:
        raise ValueError("T-0035-22 source identity mismatch")
    reference = reference_path.read_bytes()
    build_root = reference[PAYLOAD_BUILD_ROOT_OFFSET:PAYLOAD_BUILD_ROOT_OFFSET + 16]
    if len(build_root) != 16:
        raise ValueError("reference image does not contain payload-build root")

    ini = parse_ini(source)
    streams = parse_streams(source)
    sections = sorted((name for name in ini if re.fullmatch(r"CPU\d+", name)), key=lambda name: int(name[3:]))
    if len(sections) != 2 or len(streams) != 2:
        raise ValueError(f"expected two CPU sections/streams, got {len(sections)}/{len(streams)}")

    cpus: list[dict[str, object]] = []
    for sec_name, stream in zip(sections, streams):
        idx = sec_name[3:]
        desc = ini[sec_name]
        cid = desc["NewCID"]
        if cid not in FUNCTIONS:
            raise ValueError(f"unexpected T-0035 CID {cid}")
        did201 = deobfuscate_16(desc["SeedKey"])
        did202 = deobfuscate_16(desc["Nonce"])
        erase_addr = int(ini[f"EraseRoutine{idx}"]["01_StartAddress"], 16)
        erase_len = int(ini[f"EraseRoutine{idx}"]["01_Length"], 16)
        body_addr = int(ini[f"CPUImage{idx}"]["01_StartAddress"], 16)

        decoded: dict[str, tuple[bytes, bool]] = {}
        for addr, ciphertext in stream_regions(stream):
            pt, cmac_ok = decrypt_region(ciphertext, build_root, did201, did202)
            kind = "body" if addr == body_addr else "erase" if addr == erase_addr else f"unknown_{addr:08x}"
            decoded[kind] = (pt, cmac_ok)
        if set(decoded) != {"body", "erase"}:
            raise ValueError(f"unexpected decoded region set for {cid}: {sorted(decoded)}")
        erase, erase_cmac = decoded["erase"]
        body, body_cmac = decoded["body"]
        if not erase_cmac or not body_cmac or len(erase) != erase_len:
            raise ValueError(f"CMAC/length validation failed for {cid}")

        functions = {}
        for role, (offset, size) in FUNCTIONS[cid].items():
            blob = erase[offset:offset + size]
            if len(blob) != size:
                raise ValueError(f"{cid} {role} body outside erase routine")
            functions[role] = {
                "offset": f"0x{offset:X}",
                "load_address": f"0x{erase_addr + offset:08X}",
                "size": size,
                "body_sha256": sha256(blob),
            }

        cpus.append({
            "cpu_section": sec_name,
            "cid": cid,
            "target_calibration": desc["01_TargetCalibration"],
            "offset_address": desc["OffsetAddress"],
            "repro_method": desc["ReproMethod"],
            "security_property2": desc["SecurityProperty2"],
            "body": {"load_address": f"0x{body_addr:08X}", "size": len(body), "sha256": sha256(body), "cmac_valid": body_cmac},
            "erase": {"load_address": f"0x{erase_addr:08X}", "size": len(erase), "sha256": sha256(erase), "cmac_valid": erase_cmac},
            "functions": functions,
        })

    return {
        "schema": "toyota-t0035-faci-backend-evidence-v1",
        "source": {"filename": cuw_path.name, "size": len(source), "sha256": sha256(source)},
        "package": {
            "vehicle": ini["Vehicle"]["VehicleName"],
            "model_year": ini["Vehicle"]["ModelYear"],
            "contact_type": ini["Vehicle"]["ContactType"],
            "diag_id": ini["Node01"]["DiagID"],
            "required_spec_repro_ver": ini["Node01"]["RequiredSpecReproVer"],
        },
        "crypto_provenance": {
            "reference_image": str(reference_path.resolve().relative_to(REPO.resolve())),
            "payload_build_root_offset": f"0x{PAYLOAD_BUILD_ROOT_OFFSET:X}",
            "payload_build_root_sha256": sha256(build_root),
            "secret_values_recorded": False,
        },
        "cpus": cpus,
        "recovered_faci_semantics": {
            "erase_payload_load": "0xFEBF0000/0x1000 on both CPUs",
            "frdy_mask": "0x00008000",
            "command_lock_mask": "FASTAT 0x10",
            "fstatr_error_mask": "0x00007040",
            "program_sequence": "FSADDR; E8; 0x80 halfword-count; write 128 halfwords; after each write wait while FSTATR 0x00000400 (DBFULL); D0",
            "erase_sequence": "FPSADDR=1; FSADDR; 0x20; D0",
            "pe_entry": "FENTRYR=AA01; FHVE15=1; FHVE3=1; FAREASELC=3B00; FPROTR=5501",
            "pe_exit": "FHVE15=0; FHVE3=0; FPROTR=5500; FENTRYR=AA00",
            "forced_stop": "0xB3 with ready wait; exact extracted routine does not issue FCMD 0x50",
            "program_pacing_boundary": "The manufacturer routines use FSTATR bit10/0x400 after each halfword write. They do not use bit11/0x800 for this pacing loop.",
        },
        "scope_boundary": "Exact Toyota Tundra 8965F3401200/8965F3402200 manufacturer CUW evidence. It verifies P1M-E/F3-family flash-control behavior but is not an exact 8965F3307000 Camry calibration package.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cuw", type=Path, default=DEFAULT_CUW)
    ap.add_argument("--reference-codeflash", type=Path, default=DEFAULT_REFERENCE)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    obj = build(args.cuw, args.reference_codeflash)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(obj['cpus'])} CPUs; no secret values emitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
