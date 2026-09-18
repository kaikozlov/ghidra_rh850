#!/usr/bin/env python3
"""Compare recovered Toyota/Denso reprogramming roots across EPS and SRS families.

This intentionally stays on the static/offline side of the boundary.  It joins
raw firmware constants with current GTS+ CUWPlus host-side key plumbing and
runs bounded tests for simple cross-family root relationships.  It does not
send diagnostics or construct a live reprogramming transaction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any

import pefile
from Crypto.Cipher import AES
from Crypto.Hash import CMAC

sys.path.insert(0, str(Path(__file__).resolve().parent))

from recover_cp_bodies import recover

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/reprogramming_root_pair_analysis.json"
TARGETS = REPO / "data/analysis_targets.json"
EPS_CODEFLASH = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
SRS_CODEFLASH = REPO / "community/yc/venza/cflash.bin"

EPS_PAYLOAD_OFFSET = 0xBFD8
EPS_SA_OFFSET = 0xBFE8
SRS_PAYLOAD_OFFSET = 0xC3AC
SRS_SA_OFFSET = 0xC3BC
BLOCK = 16

EXPECTED = {
    "eps_payload": "ba052435f8843f985fd1329d2b6117b0",
    "eps_sa": "f05f36b7d78c03e24ab4faef2a57d044",
    "srs_payload": "8af2c4708cd9cdec494da7acdaa9a8f7",
    "srs_sa": "8f69e6dc2a4b80b45054b4827a5ab622",
}

# Current recovered SecretInfo layout, pinned by GetSecretInfo @ 0x100010D0.
SECRETINFO_TABLE_VA = 0x100030A8
SECRETINFO_ENTRY_SIZE = 0x208
SECRETINFO_ENTRY_ID_OFFSET = 0x204
SECRETINFO_ENTRY_COUNT = 72
SECRETINFO_AUTH_STRING_VA = 0x1000D000
SECURITY_UP_SELECTOR = 0
EXPECTED_SELECTOR0 = "B45B26D6344FD60E80BC01D63C7584A0"

RECOVERED_NAMES = (
    "SecretInfo.dll",
    "TCUWCanCommonPrepareWriter.dll",
    "TCUWP4CanSecurityAirbagPrepareWriter.dll",
    "TCUWP4CanSecurityAirbagFlashWriter.dll",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def block(path: Path, offset: int) -> bytes:
    raw = path.read_bytes()[offset : offset + BLOCK]
    if len(raw) != BLOCK:
        raise ValueError(f"{path}: short block at {offset:#x}")
    return raw


def cmac(key: bytes, message: bytes) -> bytes:
    c = CMAC.new(key, ciphermod=AES)
    c.update(message)
    return c.digest()


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b, strict=True))


def hamming(a: bytes, b: bytes) -> int:
    return sum((x ^ y).bit_count() for x, y in zip(a, b, strict=True))


def relation_fingerprints(payload: bytes, sa: bytes) -> dict[str, str]:
    """Values that would repeat if a simple pair relation used one fixed constant."""
    return {
        "payload_xor_sa": xor(payload, sa).hex(),
        "aes_enc_key_payload_msg_sa": AES.new(payload, AES.MODE_ECB).encrypt(sa).hex(),
        "aes_dec_key_payload_msg_sa": AES.new(payload, AES.MODE_ECB).decrypt(sa).hex(),
        "aes_enc_key_sa_msg_payload": AES.new(sa, AES.MODE_ECB).encrypt(payload).hex(),
        "aes_dec_key_sa_msg_payload": AES.new(sa, AES.MODE_ECB).decrypt(payload).hex(),
        "cmac_key_payload_msg_sa": cmac(payload, sa).hex(),
        "cmac_key_sa_msg_payload": cmac(sa, payload).hex(),
    }


def pe_imports(path: Path) -> list[dict[str, str]]:
    pe = pefile.PE(str(path), fast_load=False)
    out: list[dict[str, str]] = []
    for desc in pe.DIRECTORY_ENTRY_IMPORT:
        dll = desc.dll.decode(errors="replace")
        for imp in desc.imports:
            if imp.name:
                out.append({"dll": dll, "name": imp.name.decode(errors="replace")})
    return out


def imported_names(path: Path) -> set[str]:
    return {entry["name"] for entry in pe_imports(path)}


def va_bytes(pe: pefile.PE, va: int, size: int) -> bytes:
    base = int(pe.OPTIONAL_HEADER.ImageBase)
    return pe.get_data(va - base, size)


def parse_secretinfo(path: Path) -> dict[str, Any]:
    pe = pefile.PE(str(path), fast_load=False)
    auth = va_bytes(pe, SECRETINFO_AUTH_STRING_VA, 32).split(b"\0", 1)[0].decode("ascii")
    entries: list[dict[str, Any]] = []
    table_raw = va_bytes(pe, SECRETINFO_TABLE_VA, SECRETINFO_ENTRY_SIZE * SECRETINFO_ENTRY_COUNT)
    for index in range(SECRETINFO_ENTRY_COUNT):
        raw = table_raw[index * SECRETINFO_ENTRY_SIZE : (index + 1) * SECRETINFO_ENTRY_SIZE]
        value = raw.split(b"\0", 1)[0].decode("ascii", errors="replace")
        selector = struct.unpack_from("<I", raw, SECRETINFO_ENTRY_ID_OFFSET)[0]
        entries.append({"index": index, "selector": selector, "value": value})

    selector0 = [entry for entry in entries if entry["selector"] == SECURITY_UP_SELECTOR]
    if len(selector0) != 1 or selector0[0]["value"] != EXPECTED_SELECTOR0:
        raise ValueError(f"SecretInfo selector-0 drift: {selector0!r}")

    aes128_entries: list[tuple[int, bytes]] = []
    for entry in entries:
        value = entry["value"]
        try:
            decoded = bytes.fromhex(value)
        except ValueError:
            continue
        if len(decoded) == BLOCK:
            aes128_entries.append((entry["selector"], decoded))

    return {
        "sha256": sha256_file(path),
        "authorize_literal": auth,
        "get_secret_info": {
            "table_va": f"0x{SECRETINFO_TABLE_VA:08X}",
            "entry_size": SECRETINFO_ENTRY_SIZE,
            "entry_count": len(entries),
            "entry_id_offset": f"0x{SECRETINFO_ENTRY_ID_OFFSET:X}",
            "selector0": selector0[0]["value"],
            "table_sha256": sha256_bytes(table_raw),
            "aes128_entry_count": len(aes128_entries),
        },
        "selector_ids": sorted(entry["selector"] for entry in entries),
        "aes128_entries": aes128_entries,
    }


def secretinfo_relation_tests(
    aes128_entries: list[tuple[int, bytes]],
    roots: dict[str, tuple[bytes, bytes]],
) -> dict[str, Any]:
    """Bounded one-step tests; absence is evidence only against these exact shapes."""
    family_hits: list[dict[str, Any]] = []
    formulas = (
        "payload=sa_xor_key",
        "payload=aes_enc(key,sa)",
        "payload=aes_dec(key,sa)",
        "sa=aes_enc(key,payload)",
        "sa=aes_dec(key,payload)",
        "payload=cmac(key,sa)",
        "sa=cmac(key,payload)",
        "payload=aes_enc(sa,key)",
        "payload=aes_dec(sa,key)",
        "sa=aes_enc(payload,key)",
        "sa=aes_dec(payload,key)",
        "payload=cmac(sa,key)",
        "sa=cmac(payload,key)",
    )

    for selector, key in aes128_entries:
        for family, (payload, sa) in roots.items():
            outputs = {
                formulas[0]: xor(sa, key),
                formulas[1]: AES.new(key, AES.MODE_ECB).encrypt(sa),
                formulas[2]: AES.new(key, AES.MODE_ECB).decrypt(sa),
                formulas[3]: AES.new(key, AES.MODE_ECB).encrypt(payload),
                formulas[4]: AES.new(key, AES.MODE_ECB).decrypt(payload),
                formulas[5]: cmac(key, sa),
                formulas[6]: cmac(key, payload),
                formulas[7]: AES.new(sa, AES.MODE_ECB).encrypt(key),
                formulas[8]: AES.new(sa, AES.MODE_ECB).decrypt(key),
                formulas[9]: AES.new(payload, AES.MODE_ECB).encrypt(key),
                formulas[10]: AES.new(payload, AES.MODE_ECB).decrypt(key),
                formulas[11]: cmac(sa, key),
                formulas[12]: cmac(payload, key),
            }
            for formula, output in outputs.items():
                target = payload if formula.startswith("payload=") else sa
                if output == target:
                    family_hits.append({"family": family, "selector": selector, "formula": formula})

    root_values = {
        f"{family}_{role}": value
        for family, pair in roots.items()
        for role, value in (("payload", pair[0]), ("sa", pair[1]))
    }
    reverse_roots = {value: name for name, value in root_values.items()}
    pairwise_hits: list[dict[str, Any]] = []
    for selector_a, a in aes128_entries:
        for selector_b, b in aes128_entries:
            outputs = {
                "xor": xor(a, b),
                "aes_enc": AES.new(a, AES.MODE_ECB).encrypt(b),
                "aes_dec": AES.new(a, AES.MODE_ECB).decrypt(b),
                "cmac": cmac(a, b),
            }
            for operation, output in outputs.items():
                if output in reverse_roots:
                    pairwise_hits.append(
                        {
                            "target": reverse_roots[output],
                            "operation": operation,
                            "selector_a": selector_a,
                            "selector_b": selector_b,
                        }
                    )

    return {
        "aes128_entry_count": len(aes128_entries),
        "one_step_formulas": list(formulas),
        "one_step_root_pair_hits": family_hits,
        "pairwise_table_operations": ["xor", "aes_enc", "aes_dec", "cmac"],
        "pairwise_table_to_root_hits": pairwise_hits,
        "scope": (
            "These are bounded falsification tests, not a proof that no upstream KDF exists. "
            "They reject only the listed one-step relationships involving current SecretInfo AES-128 entries."
        ),
    }


def tracked_eps_reuse(pair: bytes) -> list[dict[str, Any]]:
    registry = json.loads(TARGETS.read_text(encoding="utf-8"))["targets"]
    out: list[dict[str, Any]] = []
    for name, target in registry.items():
        path = REPO / target["codeflash"]
        raw = path.read_bytes()
        offset = raw.find(pair)
        out.append(
            {
                "target": name,
                "software_id": target["software_id"],
                "codeflash_sha256": sha256_file(path),
                "pair_offset": f"0x{offset:X}" if offset >= 0 else None,
            }
        )
    return out


def build() -> dict[str, Any]:
    eps_payload = block(EPS_CODEFLASH, EPS_PAYLOAD_OFFSET)
    eps_sa = block(EPS_CODEFLASH, EPS_SA_OFFSET)
    srs_payload = block(SRS_CODEFLASH, SRS_PAYLOAD_OFFSET)
    srs_sa = block(SRS_CODEFLASH, SRS_SA_OFFSET)
    actual = {
        "eps_payload": eps_payload.hex(),
        "eps_sa": eps_sa.hex(),
        "srs_payload": srs_payload.hex(),
        "srs_sa": srs_sa.hex(),
    }
    if actual != EXPECTED:
        raise ValueError(f"root bytes drifted: {actual!r}")

    roots = {"eps": (eps_payload, eps_sa), "srs": (srs_payload, srs_sa)}
    fingerprints = {name: relation_fingerprints(*pair) for name, pair in roots.items()}
    shared_fingerprints = [
        formula for formula, value in fingerprints["eps"].items() if fingerprints["srs"][formula] == value
    ]

    with tempfile.TemporaryDirectory(prefix="gtsplus-reprogramming-roots-", dir=REPO / "build/tmp") as td:
        recovered = Path(td) / "recovered"
        manifest = recover(output=recovered, only=list(RECOVERED_NAMES))
        paths = {name: recovered / name for name in RECOVERED_NAMES}
        for path in paths.values():
            if not path.is_file():
                raise FileNotFoundError(path)

        secret = parse_secretinfo(paths["SecretInfo.dll"])
        secret_tests = secretinfo_relation_tests(secret.pop("aes128_entries"), roots)
        prepare_imports = imported_names(paths["TCUWP4CanSecurityAirbagPrepareWriter.dll"])
        flash_imports = imported_names(paths["TCUWP4CanSecurityAirbagFlashWriter.dll"])
        common_imports = imported_names(paths["TCUWCanCommonPrepareWriter.dll"])

        required_prepare = {
            "?GetECUAuthKey@CalibrationFile@@QAEPBEXZ",
            "?GetServiceAuthKey@CalibrationFile@@QAEPBEXZ",
            "?CalcSeedKeyForSecurityUp@CCanCommonPrepareWriter@@QAE?AVCBytes@@PBE0@Z",
        }
        required_flash = {
            "?GetSeedKey@CalibrationFile@@QAEPBEH@Z",
            "?GetNonce@CalibrationFile@@QAEPBEH@Z",
            "?SendSeedKey@CCanCommonFlashWriter@@QAEXABVCBytes@@0PBEI@Z",
            "?SendNonce@CCanCommonFlashWriter@@QAEXABVCBytes@@0PBEI@Z",
        }
        if not required_prepare <= prepare_imports:
            raise ValueError("current security-airbag prepare imports drifted")
        if not required_flash <= flash_imports:
            raise ValueError("current security-airbag flash imports drifted")
        if "GetSecretInfo" not in " ".join(common_imports):
            raise ValueError("current common prepare writer no longer imports GetSecretInfo")

        recovery = {
            "format": manifest["format"],
            "files": {
                entry["relative_path"]: {
                    "stub_sha256": entry["stub_sha256"],
                    "sidecar_sha256": entry["sidecar_sha256"],
                    "output_sha256": entry["output_sha256"],
                }
                for entry in manifest["entries"]
            },
        }

    eps_pair = eps_payload + eps_sa
    reuse = tracked_eps_reuse(eps_pair)
    reuse_hits = [row for row in reuse if row["pair_offset"] is not None]

    return {
        "schema": "ghidra-rh850-reprogramming-root-pairs-v1",
        "firmware_roots": {
            "eps": {
                "source": str(EPS_CODEFLASH.relative_to(REPO)),
                "source_sha256": sha256_file(EPS_CODEFLASH),
                "payload_build": {"offset": f"0x{EPS_PAYLOAD_OFFSET:X}", "value": eps_payload.hex()},
                "boot_security_access": {"offset": f"0x{EPS_SA_OFFSET:X}", "value": eps_sa.hex()},
                "adjacent_payload_then_sa": EPS_PAYLOAD_OFFSET + BLOCK == EPS_SA_OFFSET,
            },
            "srs": {
                "source": str(SRS_CODEFLASH.relative_to(REPO)),
                "source_sha256": sha256_file(SRS_CODEFLASH),
                "payload_build": {"offset": f"0x{SRS_PAYLOAD_OFFSET:X}", "value": srs_payload.hex()},
                "boot_security_access": {"offset": f"0x{SRS_SA_OFFSET:X}", "value": srs_sa.hex()},
                "adjacent_payload_then_sa": SRS_PAYLOAD_OFFSET + BLOCK == SRS_SA_OFFSET,
            },
        },
        "tracked_eps_reuse": {
            "matching_target_count": len(reuse_hits),
            "targets": reuse,
            "meaning": (
                "The exact 32-byte payload-root || boot-SA-root pair occurs at 0xBFD8 in every currently registered "
                "EPS CodeFlash target, despite distinct software IDs. That rules out a direct per-software-ID root KDF."
            ),
        },
        "cross_family_relationship_tests": {
            "fingerprints": fingerprints,
            "shared_simple_fingerprints": shared_fingerprints,
            "hamming_bits": {
                "eps_payload_vs_eps_sa": hamming(eps_payload, eps_sa),
                "srs_payload_vs_srs_sa": hamming(srs_payload, srs_sa),
                "eps_payload_vs_srs_payload": hamming(eps_payload, srs_payload),
                "eps_sa_vs_srs_sa": hamming(eps_sa, srs_sa),
            },
            "interpretation": (
                "No listed XOR/AES/CMAC pair fingerprint repeats across EPS and SRS. This rejects those simple fixed-constant "
                "pair relationships but cannot rule out an upstream KDF with unknown master material or domain inputs."
            ),
        },
        "current_gtsplus": {
            "recovery": recovery,
            "secret_info": secret,
            "security_airbag_prepare": {
                "required_imports": sorted(required_prepare),
                "meaning": "current host reads ECUAuthKey and ServiceAuthKey and delegates the 16-byte SecurityUp calculation",
            },
            "security_airbag_flash": {
                "required_imports": sorted(required_flash),
                "meaning": "current host passes package SeedKey and Nonce through the secure-airbag flash path",
            },
            "secret_info_relation_tests": secret_tests,
        },
        "boundary": (
            "Both firmware families store the payload-build and boot SecurityAccess roots as literal adjacent 16-byte "
            "CodeFlash constants consumed by their crypto workers. No runtime root derivation is present in either dumped "
            "ECU. Current GTS+ contains frontend wrapping secrets but none of the four firmware roots, and the bounded "
            "SecretInfo tests find no one-step relation. Any common root derivation therefore remains an upstream "
            "Toyota/Denso build/provisioning hypothesis, not a recovered ECU or Techstream algorithm."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    artifact = build()
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
