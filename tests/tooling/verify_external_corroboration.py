#!/usr/bin/env python3
"""Optional externally corroborated known-answer checks.

Derives payload roots from the committed Sienna CodeFlash image and proves that
pinned public upstream artifacts authenticate under them: Lochuan's combined
upstream image is joined against the canonical donor split, Calvin's six 4-KiB
range-dumper payloads authenticate under the recovered BFD8 payload-build root,
and Lochuan's deep-probe shellcode envelope reconstructs exactly and joins the
retained Albino live-RAM snapshot. The tracked compact opendbc DBC facts are
revalidated against the pinned upstream checkout when it is available.

The core ``make verify`` target never imports this module and requires no
external checkout. Run this suite explicitly with ``make verify-external``.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import struct
import sys
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

from tools import REPO_ROOT
REPO = REPO_ROOT
LOCK_PATH = REPO / "external-references.lock.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repos-dir",
        type=Path,
        default=REPO.parent,
        help="directory containing checkouts named as in external-references.lock.json",
    )
    args = parser.parse_args()
    refs_dir = args.repos_dir.expanduser().resolve()
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))

    needed = (
        "calvinpark_openpilot_dump",
        "lochuan_eps_telescope",
        "opendbc",
        "rh850_p1me_original",
    )
    roots: dict[str, Path] = {
        name: refs_dir / lock["repositories"][name]["directory"] for name in needed
    }
    missing = [name for name, root in roots.items() if not root.is_dir()]
    if missing:
        print(f"pinned external checkouts unavailable: {', '.join(missing)}")
        return 1

    print("== canonical donor image ==")
    codeflash = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
    split = (
        (REPO / "firmware" / "RH850_P1M-E_DataFlash.bin").read_bytes()
        + codeflash
    )
    upstream_combined = (roots["rh850_p1me_original"] / "RH850_P1M-E_Firmware.bin").read_bytes()
    check("pinned original equals DataFlash || CodeFlash", upstream_combined == split)
    canonical_sector_sha = hashlib.sha256(codeflash[0x88000:0x90000]).hexdigest()
    check(
        "canonical donor CodeFlash target-sector identity",
        canonical_sector_sha == "281a0ef918a1bd8e709bb579a7f19163d3e908eedb5bdf79ad7348c701177b01",
        canonical_sector_sha,
    )
    upstream_sector_sha = hashlib.sha256(upstream_combined[0x90000:0x98000]).hexdigest()
    check(
        "pinned original carries the same donor target sector",
        upstream_sector_sha == canonical_sector_sha,
        upstream_sector_sha,
    )

    print("\n== Calvin range payload corpus ==")
    zero16 = bytes(16)
    derived = AES.new(codeflash[0xBFD8:0xBFE8], AES.MODE_ECB).encrypt(zero16)
    dump_payload_paths = [
        "tsk/lib/payload_codeflash_00000000_00200000.bin",
        "tsk/lib/payload_dataflash_ff200000_ff210000.bin",
        "tsk/lib/payload_extended_codeflash_01000000_0100c000.bin",
        "tsk/lib/payload_global_ram_feef8000_fef08000.bin",
        "tsk/lib/payload_local_ram_pe1_febe0000_fec00000.bin",
        "tsk/lib/payload_local_ram_self_fede0000_fee00000.bin",
    ]
    range_plaintexts = []
    for rel in dump_payload_paths:
        ciphertext = (roots["calvinpark_openpilot_dump"] / rel).read_bytes()
        plaintext = AES.new(derived, AES.MODE_CBC, zero16).decrypt(ciphertext)
        cmac = CMAC.new(derived, ciphermod=AES)
        cmac.update(zero16 + plaintext[:0xFF0])
        check(
            f"Calvin range payload {Path(rel).name} authenticates under BFD8 payload root",
            len(ciphertext) == 0x1000
            and binascii.crc32(plaintext[:0xFF0]) % (1 << 32) == 0xFFFFFFFF
            and cmac.digest() == plaintext[0xFF0:]
            and struct.unpack_from("<I", plaintext, 0xFD0)[0] == 0xFEBF0000
            and struct.unpack_from("<II", plaintext, 0xFE0) == (0xFEBF0000, 0xFF0),
        )
        range_plaintexts.append(plaintext)
    varying = {
        i for i in range(0xFD0)
        if len({plaintext[i] for plaintext in range_plaintexts}) > 1
    }
    check(
        "six range payload executable bodies share exactly six varying immediate bytes",
        varying == {0x6A, 0x6B, 0x6F, 0x182, 0x183, 0x187},
        repr(sorted(hex(i) for i in varying)),
    )
    crc_fixups = {plaintext[0xFEC:0xFF0] for plaintext in range_plaintexts}
    check(
        "range payload CRC fixup also varies across all six packages",
        len(crc_fixups) == 6,
        repr(sorted(x.hex() for x in crc_fixups)),
    )

    print("\n== deep-probe envelope reconstruction ==")
    # Rebuild the exact default deep-probe envelope from the pinned upstream
    # shellcode/request geometry using the payload-build secret recovered from
    # the committed CodeFlash, then compare its terminal authentication state
    # with Albino's retained live RAM/DCRA snapshot.  The probe JSON does not
    # retain the envelope bytes themselves.
    telescope_shellcode = (
        roots["lochuan_eps_telescope"].joinpath("shellcode", "build", "deep_probe.bin").read_bytes()
    )
    telescope_request = bytes.fromhex(
        "50524f4203040008e6a0010000000000000ffde000400000000000017d80004000000000febf2cf8010000000000"
    )
    telescope_plain = bytearray(telescope_shellcode)
    telescope_plain.extend(bytes(0xF00 - len(telescope_plain)))
    telescope_plain.extend(telescope_request)
    telescope_plain.extend(bytes(0xFD0 - len(telescope_plain)))
    telescope_plain.extend(struct.pack("<I", 0xFEBF0000))
    telescope_plain.extend(bytes(0xFE0 - len(telescope_plain)))
    telescope_plain.extend(struct.pack("<I", 0xFEBF0000))
    telescope_plain.extend(struct.pack("<I", 0xFF0))
    telescope_plain.extend(bytes(4))
    telescope_crc_fixup = binascii.crc32(telescope_plain) ^ 0xFFFFFFFF
    telescope_plain.extend(struct.pack("<I", telescope_crc_fixup & 0xFFFFFFFF))
    telescope_derived_key = AES.new(codeflash[0xBFD8:0xBFE8], AES.MODE_ECB).encrypt(zero16)
    telescope_cmac = CMAC.new(telescope_derived_key, ciphermod=AES)
    telescope_cmac.update(zero16 + telescope_plain)
    telescope_tag = telescope_cmac.digest()
    telescope_plain.extend(telescope_tag)
    telescope_envelope = AES.new(
        telescope_derived_key, AES.MODE_CBC, iv=bytes(16)
    ).encrypt(bytes(telescope_plain))
    telescope_probe = json.loads((REPO / "community/albinoelephant/telescope/probe.json").read_text(encoding="utf-8"))
    telescope_live_ram = bytes.fromhex(telescope_probe["layer3"]["regions"][str(0xFEBF2CF8)])
    check(
        "pinned eps-telescope default envelope reconstructs exactly",
        len(telescope_plain) == len(telescope_envelope) == 0x1000
        and hashlib.sha256(telescope_envelope).hexdigest() == "e1d2ddcaa1a8b0cba0a5c4407bd2872619e14b81dc08dc50df8772de06a35910"
        and binascii.crc32(telescope_plain[:0xFF0]) & 0xFFFFFFFF == 0xFFFFFFFF,
    )
    check(
        "Albino live CMAC work buffer is the exact pinned deep-probe envelope tag",
        telescope_tag.hex() == "a5ebde539a7147cd61f21b4a5b222e1f"
        and telescope_live_ram[0x30:0x40] == telescope_tag,
    )
    check(
        "Albino live DCRA CIN is the exact pinned deep-probe CRC fixup word",
        telescope_crc_fixup == 0x6DAAE993
        and telescope_probe["layer3"]["registers"]["DCRA1CIN"] == telescope_crc_fixup
        and telescope_probe["layer3"]["registers"]["DCRA1COUT"] == 0xFFFFFFFF,
    )

    corolla_canary = (REPO / "exploit/ephemeral_runtime/audited/corolla_hf_runtime_canary.bin").read_bytes()
    telescope_canary_plain = bytearray(corolla_canary)
    telescope_canary_plain.extend(bytes(0xFD0 - len(telescope_canary_plain)))
    telescope_canary_plain.extend(struct.pack("<I", 0xFEBF0000))
    telescope_canary_plain.extend(bytes(0xFE0 - len(telescope_canary_plain)))
    telescope_canary_plain.extend(struct.pack("<I", 0xFEBF0000))
    telescope_canary_plain.extend(struct.pack("<I", 0xFF0))
    telescope_canary_plain.extend(bytes(4))
    telescope_canary_crc = binascii.crc32(telescope_canary_plain) ^ 0xFFFFFFFF
    telescope_canary_plain.extend(struct.pack("<I", telescope_canary_crc & 0xFFFFFFFF))
    telescope_canary_cmac = CMAC.new(telescope_derived_key, ciphermod=AES)
    telescope_canary_cmac.update(zero16 + telescope_canary_plain)
    telescope_canary_plain.extend(telescope_canary_cmac.digest())
    telescope_canary_envelope = AES.new(
        telescope_derived_key, AES.MODE_CBC, iv=bytes(16)
    ).encrypt(bytes(telescope_canary_plain))
    check(
        "pinned eps-telescope envelope algorithm reproduces the direct H/F canary package identity",
        len(telescope_canary_envelope) == 0x1000
        and hashlib.sha256(telescope_canary_envelope).hexdigest() == "b6d4b261ef6fb614ef0c9f8cd72bc7e7fb7608a793f9094ec76fe226bd884367"
        and binascii.crc32(telescope_canary_plain[:0xFF0]) & 0xFFFFFFFF == 0xFFFFFFFF,
    )

    print("\n== tracked compact opendbc corroboration ==")
    compact_dbc_facts = json.loads(
        (REPO / "data/external/opendbc/toyota_dbc_facts.json").read_text(encoding="utf-8")
    )
    toyota_2017_dbc = (
        roots["opendbc"] / "opendbc/dbc/generator/toyota/_toyota_2017.dbc"
    ).read_text(encoding="utf-8")
    toyota_secoc_dbc = (
        roots["opendbc"] / "opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc"
    ).read_text(encoding="utf-8")
    steer_facts = compact_dbc_facts["messages"]["STEER_ANGLE_SENSOR"]
    check(
        "compact CAN 0x025 steering facts match pinned DBC",
        steer_facts["can_id_decimal"] == 37
        and steer_facts["signals"]["STEER_ANGLE"] == {"start_bit_motorola": 3, "bit_length": 12, "signed": True}
        and steer_facts["signals"]["STEER_FRACTION"] == {"start_bit_motorola": 39, "bit_length": 4, "signed": True}
        and steer_facts["signals"]["STEER_RATE"] == {"start_bit_motorola": 35, "bit_length": 12, "signed": True}
        and "SG_ STEER_ANGLE : 3|12@0-" in toyota_2017_dbc
        and "SG_ STEER_FRACTION : 39|4@0-" in toyota_2017_dbc
        and "SG_ STEER_RATE : 35|12@0-" in toyota_2017_dbc,
    )
    eps_facts = compact_dbc_facts["messages"]["EPS_STATUS"]
    check(
        "compact CAN 0x262 EPS_STATUS facts match pinned DBC",
        eps_facts["can_id_decimal"] == 610
        and eps_facts["signals"]["IPAS_STATE"] == {"start_bit_motorola": 3, "bit_length": 4, "signed": False}
        and eps_facts["signals"]["LTA_STATE"] == {"start_bit_motorola": 15, "bit_length": 5, "signed": False}
        and eps_facts["signals"]["TYPE"] == {"start_bit_motorola": 24, "bit_length": 1, "signed": False}
        and eps_facts["signals"]["LKA_STATE"] == {"start_bit_motorola": 31, "bit_length": 7, "signed": False}
        and "SG_ IPAS_STATE : 3|4@0+" in toyota_secoc_dbc
        and "SG_ LTA_STATE : 15|5@0+" in toyota_secoc_dbc
        and "SG_ TYPE : 24|1@0+" in toyota_secoc_dbc
        and "SG_ LKA_STATE : 31|7@0+" in toyota_secoc_dbc,
    )

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
