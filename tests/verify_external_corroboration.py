#!/usr/bin/env python3
"""Optional checks against pinned public upstream repositories.

The core ``make verify`` target never imports this module and requires no
external checkout. Run this suite explicitly with ``make verify-external``.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import io
import json
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

REPO = Path(__file__).resolve().parents[1]
LOCK_PATH = REPO / "external-references.lock.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def git_show(path: Path, spec: str) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "show", spec],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def pdf_text(path: Path) -> str:
    return subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def dbc_message(dbc: str, can_id: int, name: str) -> str:
    """Return one DBC message block, excluding following BO_ definitions."""
    marker = f"BO_ {can_id} {name}:"
    start = dbc.find(marker)
    if start < 0:
        return ""
    end = dbc.find("\nBO_ ", start + len(marker))
    return dbc[start:] if end < 0 else dbc[start:end]


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

    print("== pinned external repositories ==")
    roots: dict[str, Path] = {}
    for name, metadata in lock["repositories"].items():
        root = refs_dir / metadata["directory"]
        roots[name] = root
        check(f"{name} checkout exists", root.is_dir(), str(root))
        if root.is_dir():
            try:
                head = git_head(root)
            except (OSError, subprocess.CalledProcessError) as error:
                check(f"{name} is a Git checkout", False, str(error))
            else:
                check(f"{name} commit is pinned", head == metadata["commit"], head)

    if any(not root.is_dir() for root in roots.values()):
        print(f"\n== RESULT: {passed} passed, {failed} failed ==")
        return 1

    print("\n== pinned artifacts and local fixtures ==")
    for artifact in lock["artifacts"]:
        root = roots[artifact["repository"]]
        path = root / artifact["path"]
        label = f"{artifact['repository']}:{artifact['path']}"
        check(f"{label} exists", path.is_file(), str(path))
        if not path.is_file():
            continue
        if "size" in artifact:
            check(f"{label} size", path.stat().st_size == artifact["size"], str(path.stat().st_size))
        digest = sha256(path)
        check(f"{label} SHA-256", digest == artifact["sha256"], digest)
        fixture_name = artifact.get("fixture")
        if fixture_name:
            fixture = REPO / fixture_name
            check(f"{label} fixture exists", fixture.is_file(), str(fixture))
            if fixture.is_file():
                check(f"{label} equals committed fixture", path.read_bytes() == fixture.read_bytes())

    print("\n== official comma Toyota-B harness topology ==")
    harness_box = pdf_text(roots["commaai_hardware"] / "harness/v3/Harness_Box.pdf")
    toyota_b = pdf_text(roots["commaai_hardware"] / "harness/v3/Toyota_B_Harness.pdf")
    obd_c = pdf_text(roots["commaai_hardware"] / "harness/OBD-C.sch.pdf")
    check(
        "official harness box assigns CAN0=CAR, CAN1=RADAR, CAN2=CAMERA, CAN3=COMMA POWER",
        all(token in harness_box for token in ("CAN0 = CAR", "CAN1 = RADAR", "CAN2 = CAMERA", "CAN3 = COMMA POWER")),
    )
    check(
        "official harness box relay is the CAN0/CAN2 split pair",
        'SOLID-STATE "RELAY"' in harness_box and "CAN2_H 1" in harness_box and "CAN0_H" in harness_box
        and "CAN2_L" in harness_box and "CAN0_L" in harness_box,
    )
    check(
        "official Toyota-B adapter puts CAN2+CAN1 on camera side and CAN0+CAN1 on car side",
        "TO CAMERA" in toyota_b and "TO CAR" in toyota_b
        and "CAN2_H - ORANGE" in toyota_b and "CAN2_L - GREEN" in toyota_b
        and "CAN1_H - PINK" in toyota_b and "CAN1_L - BLUE" in toyota_b
        and "CAN0_H - ORANGE" in toyota_b and "CAN0_L - GREEN" in toyota_b,
    )
    check(
        "official OBD-C mapping uses SBU1 for the CAN0/CAN2 relay and keeps CAN1 distinct",
        "SBU1 is used for driving the relay between CAN0 and CAN2" in obd_c
        and "CAN1_H" in obd_c and "CAN1_L" in obd_c,
    )

    print("\n== pinned Stage-8 optskug evidence ==")
    optskug_readme = (roots["optskug_docs"] / "README.md").read_text(encoding="utf-8")
    check(
        "optskug records MCU ID + VIN as required official rekey inputs",
        "requires uploading both the MCU ID and VIN" in optskug_readme
        and "refuses to provide a key update when only the VIN is supplied" in optskug_readme,
    )
    check(
        "optskug keeps MCU-ID cryptographic role bounded",
        "does not yet establish the exact calculation" in optskug_readme,
    )
    check(
        "optskug records physical Toyota-B CAN0/CAN1 swap anomaly",
        "after physically swapping CAN 0 and CAN 1 at the harness, they were able to dump the firmware" in optskug_readme,
    )
    check(
        "optskug records the first 2023-US-Corolla public route",
        "a74eba85c97eaf67/00000004--555953f500/0" in optskug_readme,
    )
    check(
        "optskug records failed 2024 RAV4 Prime persistent-patch field test",
        "Techstream reported EPMS code `U023A87`" in optskug_readme,
    )
    check(
        "optskug records Toyota-B physical bus assignment can move the relay onto bus 1",
        "the relay ends up on bus 1 instead of bus 0/2" in optskug_readme.lower(),
    )
    check(
        "optskug records the exact Tundra CUW source for the 8965F3 flash driver",
        "T-SB-0069-22" in optskug_readme
        and "T-0035-22.cuw" in optskug_readme
        and "flash driver that's uploaded before flashing" in optskug_readme
        and "This flash driver should be applicable to all cars" in optskug_readme,
    )
    check(
        "optskug records community extraction of the flash driver from Techinfo CUW",
        "script for extracting the flash driver from the Techinfo `.cuw` package" in optskug_readme
        and "computes `0x201` and `0x202`" in optskug_readme,
    )

    print("\n== blurbdust public lineage and CUW chronology ==")
    blur_root = roots["blurbdust_secoc"]
    blur_first = "dbfd991bc817deca0c5c94e2fb5171d1142682c1"
    blur_parent = subprocess.run(
        ["git", "-C", str(blur_root), "rev-parse", f"{blur_first}^"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    blur_first_date = subprocess.run(
        ["git", "-C", str(blur_root), "show", "-s", "--format=%aI", blur_first],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    check(
        "blurbdust first flash-writer commit forks directly from pinned I-CAN-hack tip",
        blur_parent == lock["repositories"]["icanhack_secoc"]["commit"],
        blur_parent,
    )
    check(
        "blurbdust first flash-writer commit dates to 2026-04-28",
        blur_first_date.startswith("2026-04-28T"),
        blur_first_date,
    )

    tundra_root = roots["icanhack_secoc_tundra"]
    tundra_date = subprocess.run(
        ["git", "-C", str(tundra_root), "show", "-s", "--format=%aI", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    tundra_host = (tundra_root / "extract_keys.py").read_text(encoding="utf-8")
    first_host = git_show(blur_root, f"{blur_first}:flash_patcher.py")
    check(
        "Willem tundra precursor predates blurbdust writer and names the exact F340 pair",
        tundra_date.startswith("2025-07-13T")
        and "8965F3401200" in tundra_host
        and "8965F3402200" in tundra_host
        and "8965F3401200" in first_host
        and "8965F3402200" in first_host,
        tundra_date,
    )
    check(
        "Willem tundra precursor supplies the CPU0 0203 offset and new-UDS 45 01 grammar generalized by blurbdust",
        'write_data_by_identifier(0x203, b"\\x01\\x00\\x00\\x00\\x00")' in tundra_host
        and 'offset_addr = b"\\x01\\x00\\x00\\x00\\x00" if cpu_index == 0' in first_host
        and 'data = b"\\x45\\x01"' in tundra_host
        and 'routine_magic = b"\\x45\\x01" if new_uds else' in first_host,
    )
    check(
        "blurbdust generalized rather than byte-copying the tundra RequestDownload prefix",
        'data += b"\\x01" # [4]' in tundra_host
        and 'data = b"\\x01\\x46" + mem_id + b"\\x00"' in first_host,
    )

    public_shell = (blur_root / "shellcode/main_flash_patch.c").read_bytes()
    community_shell = (REPO / "community/blurbdust_secoc_flash_patcher/main.c").read_bytes()
    check(
        "retained Discord main.c is byte-identical to pinned public main_flash_patch.c",
        public_shell == community_shell,
        hashlib.sha256(public_shell).hexdigest()[:16],
    )

    public_host = (blur_root / "flash_patcher.py").read_text(encoding="utf-8")
    community_host_exact = (REPO / "community/blurbdust_secoc_flash_patcher/flash_patcher.py").read_text(encoding="utf-8")
    normalized_public_host = public_host.replace('struct.unpack(">I"', 'struct.unpack("<I"')
    check(
        "Discord/public host tools differ only in two decode_frame endian format strings",
        public_host.count('struct.unpack(">I"') == 2
        and community_host_exact.count('struct.unpack("<I"') == 2
        and normalized_public_host == community_host_exact,
    )

    public_history_paths = subprocess.run(
        ["git", "-C", str(blur_root), "log", "--all", "--name-only", "--pretty=format:"],
        check=True, capture_output=True, text=True,
    ).stdout
    check(
        "public blurbdust history never contains the retained T-0035 decryptor",
        "decrypt.T-0035-22.py" not in public_history_paths
        and not (blur_root / "decrypt.T-0035-22.py").exists(),
    )

    first_shell = git_show(blur_root, f"{blur_first}:shellcode/main_flash_patch.c")
    check(
        "first public writer already targets exact T-0035-22 F3401200/F3402200 pair",
        "8965F3401200" in first_host and "8965F3402200" in first_host,
    )
    check(
        "first public writer already carries the OEM-shaped FACI raw sequence",
        "0xFFA10080" in first_shell
        and "0xFFA10010" in first_shell
        and "0xFFA10084" in first_shell
        and "0xFFA10088" in first_shell
        and "0xFFF8A430" in first_shell
        and "0xFFF82410" in first_shell
        and "FACI_FCMD8 = 0x20" in first_shell
        and "FACI_FCMD8 = 0xE8" in first_shell
        and "FACI_FCMD8 = 0x80" in first_shell
        and "FACI_FCMD8 = 0xD0" in first_shell,
    )
    check(
        "first public writer contains the obsolete bit-21 pacing later corrected from Toyota CUW",
        "while (FACI_FASTAT & (1 << 21))" in first_shell,
    )

    discord_cuw_message = 1496150355224952995
    discord_cuw_ms = (discord_cuw_message >> 22) + 1420070400000
    check(
        "optskug pins the exact blurbdust CUW-extractor Discord message",
        str(discord_cuw_message) in optskug_readme
        and discord_cuw_ms == 1776780441815,
        str(discord_cuw_ms),
    )
    check(
        "CUW-extractor statement predates the first public writer by seven calendar days",
        "### April 2026" in optskug_readme
        and "2026-04-28" in blur_first_date,
    )

    corrected_faci = (roots["lochuan_b4512000_fw_patch"] / "payload/faci_dual.h").read_text(encoding="utf-8")
    check(
        "Lochuan manufacturer comparison supplies exactly the missing pacing/status semantics",
        "0x00000800u" in corrected_faci
        and "0x00007040u" in corrected_faci
        and "FACI_CMD8=0x50u" in corrected_faci
        and "manufacturer's CUW" in corrected_faci,
    )

    print("\n== Calvin dump-branch archaeology and range evidence ==")
    dump_root = roots["calvinpark_openpilot_dump"]
    dump_claude = (dump_root / "CLAUDE.md").read_text(encoding="utf-8")
    dump_range = (dump_root / "tsk/lib/dump_range.py").read_text(encoding="utf-8")
    dump_preflight = (dump_root / "tsk/lib/preflight.py").read_text(encoding="utf-8")
    local_cf = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
    local_p1me = json.loads((REPO / "data/p1me_product_memory.json").read_text(encoding="utf-8"))
    local_archaeology = (REPO / "docs/history/2026-08/CALVIN_TSKM_DUMP_ARCHAEOLOGY_2026-08-21.md").read_text(encoding="utf-8")

    visible = [
        "7f207ac644d466723c58e3f02b9d583d00fea2eb",
        "ce279fcb5cadefa584e9ac1d6ab14be6a44426d8",
        "725f84756dda589894bd85e6c4a02e2dd3c41c2d",
        "42d1120395877e96ed440646a765157a0ad7646b",
    ]
    subjects = [subprocess.run(
        ["git", "-C", str(dump_root), "show", "-s", "--format=%s", commit],
        check=True, capture_output=True, text=True,
    ).stdout.strip() for commit in visible]
    check("dump visible research chain is TSKM Web -> Range dumper -> mo-dump -> spanconstants",
          subjects == ["TSKM Web", "Range dumper", "mo-dump", "spanconstants"], repr(subjects))

    rewritten = {
        "37181a271a4ce9ec83354fb64c491bc17223b56b": "TSKM Web",
        "a7b90ffb45846495b16416a05904ecab87af2290": "Range dumper",
        "28ff8452ee4633f17a8fd2a4c590f9022998cd2a": "mo-dump",
        "5feb4f4ca0b9319989f1392d95137c85932f3fbe": "TSKM Web",
        "9a18846efe5d20a15acc78e905ff9cd407132022": "Range dumper",
        "6ffa39e634a49bf23fe50dff4f864938fc9e5906": "mo-dump",
        "823d9293c0e4564afb6126f61ac6227f068da924": "save",
        "60d4ec550f26b0c4a867122ab43c3d54a7da6c3a": "spanconstants",
    }
    for commit, subject in rewritten.items():
        proc = subprocess.run(
            ["git", "-C", str(dump_root), "show", "-s", "--format=%s", commit],
            capture_output=True, text=True,
        )
        check(f"rewritten dump commit {commit[:9]} remains archaeology-readable",
              proc.returncode == 0 and proc.stdout.strip() == subject,
              proc.stdout.strip() if proc.returncode == 0 else "missing")

    check("save and both spanconstants generations amend the same 725f parent",
          all(subprocess.run(
              ["git", "-C", str(dump_root), "show", "-s", "--format=%P", c],
              check=True, capture_output=True, text=True,
          ).stdout.strip() == "725f84756dda589894bd85e6c4a02e2dd3c41c2d"
          for c in ("823d9293c0e4564afb6126f61ac6227f068da924",
                    "60d4ec550f26b0c4a867122ab43c3d54a7da6c3a",
                    "42d1120395877e96ed440646a765157a0ad7646b")))
    check("spanconstants generations preserve Aug-18 author time while commit time advances",
          subprocess.run(["git", "-C", str(dump_root), "show", "-s", "--format=%aI|%cI", "60d4ec550"],
                         check=True, capture_output=True, text=True).stdout.strip()
          == "2026-08-18T17:01:45-07:00|2026-08-19T17:03:05-07:00"
          and subprocess.run(["git", "-C", str(dump_root), "show", "-s", "--format=%aI|%cI", "42d112039"],
                             check=True, capture_output=True, text=True).stdout.strip()
          == "2026-08-18T17:01:45-07:00|2026-08-20T17:18:00-07:00")

    check("current range dumper pins the six RH850 exploratory windows",
          all(token in dump_range for token in (
              "0x00000000, 0x00200000", "0x01000000, 0x0100C000",
              "0xFEBE0000, 0xFEC00000", "0xFEDE0000, 0xFEE00000",
              "0xFEEF8000, 0xFEF08000", "0xFF200000, 0xFF210000")))
    dump_payload_paths = [
        "tsk/lib/payload_codeflash_00000000_00200000.bin",
        "tsk/lib/payload_dataflash_ff200000_ff210000.bin",
        "tsk/lib/payload_extended_codeflash_01000000_0100c000.bin",
        "tsk/lib/payload_global_ram_feef8000_fef08000.bin",
        "tsk/lib/payload_local_ram_pe1_febe0000_fec00000.bin",
        "tsk/lib/payload_local_ram_self_fede0000_fee00000.bin",
    ]
    local_codeflash = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
    build_secret = local_codeflash[0xBFD8:0xBFE8]
    zero16 = bytes(16)
    derived = AES.new(build_secret, AES.MODE_ECB).encrypt(zero16)
    range_plaintexts = []
    for rel in dump_payload_paths:
        ciphertext = (dump_root / rel).read_bytes()
        plaintext = AES.new(derived, AES.MODE_CBC, zero16).decrypt(ciphertext)
        cmac = CMAC.new(derived, ciphermod=AES)
        cmac.update(zero16 + plaintext[:0xFF0])
        check(f"Calvin range payload {Path(rel).name} authenticates under BFD8 payload root",
              len(ciphertext) == 0x1000
              and binascii.crc32(plaintext[:0xFF0]) % (1 << 32) == 0xFFFFFFFF
              and cmac.digest() == plaintext[0xFF0:]
              and struct.unpack_from("<I", plaintext, 0xFD0)[0] == 0xFEBF0000
              and struct.unpack_from("<II", plaintext, 0xFE0) == (0xFEBF0000, 0xFF0))
        range_plaintexts.append(plaintext)
    varying = {
        i for i in range(0xFD0)
        if len({plaintext[i] for plaintext in range_plaintexts}) > 1
    }
    check("six range payload executable bodies share exactly six varying immediate bytes",
          varying == {0x6A, 0x6B, 0x6F, 0x182, 0x183, 0x187},
          repr(sorted(hex(i) for i in varying)))
    crc_fixups = {plaintext[0xFEC:0xFF0] for plaintext in range_plaintexts}
    check("range payload CRC fixup also varies across all six packages", len(crc_fixups) == 6,
          repr(sorted(x.hex() for x in crc_fixups)))

    bk_dump = (roots["toyota_dataflash_secoc_setup"] / "steps/step_dump_dataflash.py").read_text(encoding="utf-8")
    check("Calvin 0.5/0.7/1.0 + repeated PROGRAMMING ladder has a pinned Bk2ol precursor",
          "diagnostic_session_control(uds_mod.SESSION_TYPE.DEFAULT)" in bk_dump
          and "time.sleep(0.5)" in bk_dump
          and "diagnostic_session_control(uds_mod.SESSION_TYPE.EXTENDED_DIAGNOSTIC)" in bk_dump
          and "time.sleep(0.7)" in bk_dump
          and bk_dump.count("diagnostic_session_control(uds_mod.SESSION_TYPE.PROGRAMMING)") >= 2
          and "time.sleep(1.0)" in bk_dump
          and '("default", SESSION_TYPE.DEFAULT, 0.5)' in dump_range
          and '("extended", SESSION_TYPE.EXTENDED_DIAGNOSTIC, 0.7)' in dump_range
          and '("programming", SESSION_TYPE.PROGRAMMING, 1.0)' in dump_range
          and '("programming_repeat", SESSION_TYPE.PROGRAMMING, 0.0)' in dump_range)
    check("range dumper explicitly warns that one complete DataFlash capture is weak",
          "16,703 of 65,536 bytes (25.487 %)" in dump_range
          and "A SINGLE CAPTURE IS WEAK" in dump_range)
    check("Calvin journal records external 0x40-stride/key labels and dealer-rekey residue",
          "`0x40` stride" in dump_claude and "ID/AuthID at `+0x04`/`+0x08`" in dump_claude
          and "dealer rekey does not erase the previous key" in dump_claude)
    check("local audit corrects FF206ED4 to object 12 while keeping Calvin labels external",
          "FF206ED4` is **object 12's**" in local_archaeology
          and "ID/AuthID" in local_archaeology and "external field observation" in local_archaeology)

    check("Calvin journal records R7F701381 FEBE/FEDE live alias observation",
          "`0xFEDE0000` and `0xFEBE0000` are two address windows onto one array" in dump_claude)
    check("local Renesas geometry independently closes the PE1/self mapping",
          local_p1me["products"]["R7F701383"]["local_ram_bytes"] == 0x20000
          and local_p1me["address_space"]["local_ram_pe1"] == {"start": 0xFEBE0000, "end_exclusive": 0xFEC00000}
          and local_p1me["address_space"]["local_ram_self"] == {"start": 0xFEDE0000, "end_exclusive": 0xFEE00000})

    check("Calvin journal records broad Corolla no-key scan with positive control",
          "6,389,280 sliding-window scans and zero matches" in dump_claude
          and "key planted at offset `0x4000`" in dump_claude)
    check("local audit bounds no-key result to cross-session raw-window matching",
          "cross-session" in local_archaeology and "raw 16-byte value" in local_archaeology
          and "6,389,280 window/oracle invocations" in local_archaeology)

    check("Calvin journal records roughly-one-second PROGRAMMING unlock chronology",
          "roughly one second after entering PROGRAMMING" in dump_claude
          and "A fresh 10-second delay on bootloader entry would have returned `0x37`" in dump_claude)
    check("local firmware/device evidence preserves 10-second bad-key backoff and handoff clear",
          local_p1me["timer"]["security_delay_ms"] == 10_000
          and local_cf[0x562A:0x5630] == bytes.fromhex("440756937f00")
          and struct.unpack_from("<II", local_cf, 0x31914) == (0, 0x7A1)
          and local_cf[0x31924] == 2)

    check("final preflight chooses routes by actual PROGRAMMING reachability",
          "_probe_route" in dump_preflight and "PROGRAMMING" in dump_preflight
          and "param=1" in dump_claude and "Whether PROGRAMMING answers there is still unmeasured" in dump_claude)
    check("Calvin journal stale DataFlash-extent caveat is superseded by official local geometry",
          "`R7F701383`'s DataFlash extent is unsettled" in dump_claude
          and local_p1me["products"]["R7F701383"]["dataflash_bytes"] == 0x8000
          and local_p1me["address_space"]["dataflash_1mb"] == {"start": 0xFF200000, "end_exclusive": 0xFF208000})

    print("\n== Lochuan historical/persistent-patch provenance ==")
    lochuan_report = (roots["rh850_p1me_original"] / "RESEARCH_REPORT_EN.md").read_text(encoding="utf-8")
    lochuan_manifest = (roots["lochuan_b4512000_fw_patch"] / "eps_patch/manifest.py").read_text(encoding="utf-8")
    check(
        "Lochuan historical report labels 0x66374 as SecOC MAC scheduler",
        "secoc_mac_job_scheduler @ 0x66374" in lochuan_report,
    )
    check(
        "Lochuan historical report labels 0x674A8 as SecOC MAC generate submit",
        "secoc_mac_generate_submit(obj) @ 0x674A8" in lochuan_report,
    )
    check(
        "Lochuan historical report maps objects 5/6 to likely 0x131/0x2E4",
        "| 5 | 8 | 6 | 64 | `FEBEF430`" in lochuan_report
        and "| 6 | 56 | 6 | 70 | `FEBEF4D0`" in lochuan_report,
    )
    check(
        "Lochuan current manifest converges on the corrected Gate-2 compare neutralization",
        "patch_address=0x8E6C7" in lochuan_manifest
        and 'original_instruction=bytes.fromhex("1d 30 e0 d1")' in lochuan_manifest
        and 'patched_instruction=bytes.fromhex("1d 30 e0 01")' in lochuan_manifest
        and "crc_patched_prefix_sw=0xBE36F00D" in lochuan_manifest
        and "crc_patched_adjust_word=0x41C90FF2" in lochuan_manifest,
    )
    lochuan_readme = (roots["lochuan_b4512000_fw_patch"] / "README.md").read_text(encoding="utf-8")
    check(
        "Lochuan public guide explicitly separates Flash PASS from RX SecOC proof",
        "PASS is a Flash-level result" in lochuan_readme
        and "does not, by itself, prove that the EPS RX SecOC behavior is functionally bypassed" in lochuan_readme,
    )
    check(
        "Lochuan current README claims corrected artifacts came from a full bench probe-patch-verify run",
        "captured from the actual bench vehicle" in lochuan_readme
        and "full `probe → patch → verify` run" in lochuan_readme,
    )
    check(
        "Lochuan current README claims RAV4 Prime 2024 and Sienna 2026 PRC verification",
        "Verified working on a **2024 Toyota RAV4 Prime**" in lochuan_readme
        and "a **2026 Toyota Sienna (PRC made)**" in lochuan_readme,
    )
    canonical_code = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
    upstream_combined = (roots["rh850_p1me_original"] / "RH850_P1M-E_Firmware.bin").read_bytes()
    canonical_target_sector_sha = hashlib.sha256(canonical_code[0x88000:0x90000]).hexdigest()
    upstream_target_sector_sha = hashlib.sha256(upstream_combined[0x90000:0x98000]).hexdigest()
    check(
        "Lochuan current bench target is bound to the canonical 8965B4512000 CN-Sienna donor image",
        'part_number=b"8965B4512000"' in lochuan_manifest
        and 'application_software_id=b"\\x018965B4512000\\x00\\x00\\x00\\x00"' in lochuan_manifest
        and canonical_target_sector_sha == "281a0ef918a1bd8e709bb579a7f19163d3e908eedb5bdf79ad7348c701177b01"
        and upstream_target_sector_sha == canonical_target_sector_sha
        and f'original_sha256="{canonical_target_sector_sha}"' in lochuan_manifest,
        canonical_target_sector_sha,
    )
    lochuan_faci = (roots["lochuan_b4512000_fw_patch"] / "payload/faci_dual.h").read_text(encoding="utf-8")
    check(
        "Lochuan current FACI source carries the CUW-correlated status/pacing correction",
        "#define FSTATR_ERROR_MASK 0x00007040u" in lochuan_faci
        and "FACI_FSTATR&0x00000800u" in lochuan_faci
        and "0x00200000" not in lochuan_faci
        and "0xFFA10080" in lochuan_faci
        and "0xFFA10010" in lochuan_faci,
    )
    faci_correction_commit = git_show(
        roots["lochuan_b4512000_fw_patch"],
        "390ddb730ca24265c7935989e251f45545909d65",
    )
    check(
        "Lochuan FACI correction commit explicitly says 8965F3 CUW shellcode was imported into Ghidra",
        "manufacturer's own CUW flash-programming shellcode" in faci_correction_commit
        and "8965F3 series, imported into Ghidra" in faci_correction_commit
        and "manufacturer's andi 0x7040" in faci_correction_commit
        and "SUSRDY" in faci_correction_commit,
    )
    migration_report = git_show(
        roots["lochuan_b4512000_fw_patch"],
        "1118d031d7d7a03ec10312cc7140904e2cc923f3:.superpowers/sdd/2026-08-17-eps-patch-migration/task-4-report.md",
    )
    check(
        "Lochuan deleted migration report binds the public writer to a private reviewed predecessor tree",
        "/Users/kevin/Desktop/disable-secoc/sienna-b4512000-rx-secoc/.venv/bin/python" in migration_report
        and "After migrating the reviewed sources" in migration_report
        and "previously\nreviewed GCC 13.2.0/binutils 2.41 artifacts" in migration_report
        and "mechanically\nmigrated patch-era sources" in migration_report,
    )
    telescope_design = git_show(
        roots["lochuan_eps_telescope"],
        "99b98f0a42fdb519f9a2fb6c47e71d75e906f6d2:docs/superpowers/specs/2026-08-19-rh850-eps-probe-design.md",
    )
    check(
        "Lochuan Aug-19 eps-telescope design already derives corrected FACI register names from the hardware manual",
        "正确寄存器映射（来自 RH850/P1M-E 硬件手册）" in telescope_design
        and "| 0xFFA10010 | FASTAT |" in telescope_design
        and "| 0xFFA10020 | FAREASELC |" in telescope_design
        and "| 0xFFA10080 | FSTATR |" in telescope_design
        and "| 0xFFF82410 | FHVE3 |" in telescope_design
        and "| 0xFFF8A430 | FHVE15 |" in telescope_design,
    )

    # The public-release commit deleted the internal design/report tree, but the
    # pinned commit retains that history. Pin the specific ancestors that record
    # the actual bench incident so deployment evidence is not conflated with the
    # later offline migration/recovery test reports.
    lochuan_root = roots["lochuan_b4512000_fw_patch"]
    dcra_design = git_show(
        lochuan_root,
        "b23649d688022413647f3412e409e121e91372d8:docs/superpowers/specs/2026-08-17-dcra-cout-and-adjustment-correction-design.md",
    )
    dcra_flat = " ".join(dcra_design.split())
    check(
        "Lochuan history records a real failed read-only DCRA probe",
        "complete diagnostic report from the failed read-only probe" in dcra_flat
        and "primary code `3`" in dcra_flat
        and "0xf5ee5210" in dcra_flat,
    )
    four_kib_design = git_show(
        lochuan_root,
        "efe9ecea97777fd4ed8bbfc4c9309623a08b178d:docs/superpowers/specs/2026-08-17-four-kib-payload-download-design.md",
    )
    check(
        "Lochuan history records the rejected 32-KiB RequestDownload",
        "0xFEBF2000" in four_kib_design
        and "32 KiB" in four_kib_design
        and "request out of range" in four_kib_design.lower(),
    )
    crc_route_design = git_show(
        lochuan_root,
        "1c0735176a60ae2c6f76d29aa5d2fb281e4373de:docs/superpowers/specs/2026-08-17-crc-trigger-route-recovery-design.md",
    )
    check(
        "Lochuan history records a successful real target-sector commit/readback",
        "target source was prechecked, armed, written, and completely read back" in crc_route_design
        and "exact target candidate" in crc_route_design,
    )
    crc_route_flat = " ".join(crc_route_design.split())
    check(
        "same incident later observed target=candidate while CRC remained source",
        "proved the target was the exact candidate and the CRC sector was still the exact source" in crc_route_flat,
    )
    check(
        "same incident ended CRC trigger with exact NRC31 raw frame",
        "03 7f 31 31 00 00 00 00" in crc_route_design
        and "Request Out Of Range" in crc_route_design,
    )
    recovery_report = git_show(
        lochuan_root,
        "9f5fbffc905c64c1f26f4991a2e2468f64ce78f7:.superpowers/sdd/2026-08-17-crc-trigger-route-recovery-report.md",
    )
    check(
        "post-incident CRC recovery verification was offline only",
        "No hardware, ECU, vehicle, Panda, comma, Docker, SSH, network, or external" in recovery_report
        and "All evidence came from local deterministic fakes" in recovery_report,
    )

    print("\n== Lochuan patch deployment lineage ==")
    check(
        "Lochuan deleted design explicitly cites I-CAN-hack plus independent friend patcher",
        "`secoc-icanhack/extract_keys.py` and its independent friend script" in crc_route_design
        and "`disable-secoc-script/flash_patcher.py`" in crc_route_design,
    )
    check(
        "Lochuan reference route is FEBF0000/0x1000 upload plus fixed E0000/0x8000 FF00",
        "RAM `0xFEBF0000 / 0x1000`" in crc_route_design
        and "range `0xE0000 / 0x8000`" in crc_route_design,
    )
    migration_report = git_show(
        lochuan_root,
        "8d0f29fbe506e36de37a912930f6c68c10a75c42:.superpowers/sdd/2026-08-17-eps-patch-migration/task-4-report.md",
    )
    check(
        "first public payload commit says reviewed sources were migrated",
        "After migrating the reviewed sources" in migration_report,
    )
    check(
        "first public payload commit calls binaries previously reviewed artifacts",
        "previously\nreviewed GCC 13.2.0/binutils 2.41 artifacts" in migration_report,
    )
    check(
        "first public payload commit says patch-era sources were mechanically migrated",
        "mechanically\nmigrated patch-era sources retain their own exact shared headers" in migration_report,
    )
    icanhack_host = (roots["icanhack_secoc"] / "extract_keys.py").read_text(encoding="utf-8").lower()
    community_host = (REPO / "community/blurbdust_secoc_flash_patcher/flash_patcher.py").read_text(encoding="utf-8").lower()
    community_shell = (REPO / "community/blurbdust_secoc_flash_patcher/main.c").read_text(encoding="utf-8").lower()
    upstream_text = "\n".join((icanhack_host, community_host, community_shell))
    check(
        "upstream I-CAN-hack/blurbdust sources do not contain Lochuan 0x664E6 target",
        "664e6" not in upstream_text and "664e4" not in upstream_text
        and "20 e6 31 00" not in upstream_text and "20 e6 10 00" not in upstream_text,
    )
    check(
        "blurbdust semantic target is the independent eight-byte egg",
        all(token in community_shell for token in (
            "#define egg_0 0x88", "#define egg_1 0x00", "#define egg_2 0x01",
            "#define egg_3 0x52", "#define egg_4 0x00", "#define egg_5 0x0a",
            "#define egg_6 0xe5", "#define egg_7 0x0d",
        ))
        and "0x007f5201" in community_shell,
    )

    print("\n== Lochuan semantic-error chronology ==")
    initial_report = git_show(
        roots["rh850_p1me_original"],
        "4e5464d7871a608b7aa9772f3b1414d873823897:RESEARCH_REPORT_EN.md",
    )
    jul24_report = git_show(
        roots["rh850_p1me_original"],
        "c3d619f8708f408991a27e013f21d3d3e087aafe:RESEARCH_REPORT_EN.md",
    )
    for label, report in (("initial Jul-20", initial_report), ("Jul-24 edited", jul24_report)):
        check(
            f"Lochuan {label} report retains checkpoint-as-MAC model",
            "secoc_mac_job_scheduler @ 0x66374" in report
            and "secoc_mac_generate_submit(obj) @ 0x674A8" in report
            and "| 5 | 8 | 6 | 64 | `FEBEF430`" in report
            and "| 6 | 56 | 6 | 70 | `FEBEF4D0`" in report,
        )
    check(
        "Jul-20 report does not record the eventual 0x664E6 target derivation",
        all(token.lower() not in initial_report.lower() for token in ("0x66446", "0x664e4", "0x664e6")),
    )
    migration_design = git_show(
        lochuan_root,
        "37d9dbda1e590b7fe57949950c71545f00d71fb8:docs/superpowers/specs/2026-08-17-eps-patch-migration-design.md",
    )
    check(
        "public repo begins by migrating an existing reviewed fixed patch",
        "Migrate the useful parts of the existing 8965B4512000 EPS patch tool" in migration_design
        and "The tool targets only the reviewed `8965B4512000` EPS" in migration_design
        and "the reviewed order" in migration_design,
    )
    migration_plan = git_show(
        lochuan_root,
        "ea35228f3fe4ef9585d0489fda6dd84ad19eecbe:docs/superpowers/plans/2026-08-17-eps-patch-migration.md",
    )
    migration_plan_flat = " ".join(migration_plan.split())
    check(
        "migration plan imports proven fixed-writer primitives instead of re-deriving target",
        "Migrate the proven transport, protocol, CRC, fixed-writer, and recovery primitives" in migration_plan_flat
        and "Copy only the listed primitive source files" in migration_plan_flat,
    )
    first_public_manifest = git_show(
        lochuan_root,
        "0f0c3ef8ba26ba1ce8b2f51aed163abcbaf00174:eps_patch/manifest.py",
    )
    check(
        "first public primitive migration already contains fixed 0x664E6 target",
        "patch_address=0x664E6" in first_public_manifest
        and 'original_instruction=bytes.fromhex("20 e6 31 00")' in first_public_manifest
        and 'patched_instruction=bytes.fromhex("20 e6 10 00")' in first_public_manifest,
    )

    print("\n== original combined image reconstruction ==")
    combined = roots["rh850_p1me_original"] / "RH850_P1M-E_Firmware.bin"
    split = (
        (REPO / "firmware" / "RH850_P1M-E_DataFlash.bin").read_bytes()
        + (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
    )
    check("pinned original equals DataFlash || CodeFlash", combined.is_file() and combined.read_bytes() == split)

    print("\n== public tooling semantics ==")
    semantic_inputs = [
        roots["icanhack_secoc"] / "extract_keys.py",
        roots["icanhack_secoc"] / "shellcode/main.c",
        roots["toyota_dataflash_secoc_setup"] / "steps/step_dump_dataflash.py",
        roots["toyota_dataflash_secoc_setup"] / "steps/step_collect_can.py",
        roots["toyota_dataflash_secoc_setup"] / "steps/step_extract_verify_key.py",
        roots["toyota_dataflash_secoc_setup"] / "steps/step_eps_probe.py",
        roots["toyota_dataflash_secoc_setup"]
        / "payload_source/shellcode/main_ff1ff000_ff209000.c",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/car/uds.py",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/car/panda_runner.py",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/safety/modes/defaults.h",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/safety/modes/elm327.h",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/safety/modes/toyota.h",
        roots["calvinpark_openpilot"] / "opendbc_repo/opendbc/safety/safety.h",
        roots["calvinpark_openpilot"] / "panda/board/can_comms.h",
        roots["calvinpark_openpilot"] / "panda/board/main.c",
        roots["calvinpark_openpilot"] / "panda/board/main_comms.h",
        roots["calvinpark_openpilot"] / "panda/board/boards/tres.h",
        roots["calvinpark_openpilot"] / "panda/board/boards/cuatro.h",
        roots["calvinpark_openpilot"] / "panda/board/drivers/can_common.h",
        roots["calvinpark_openpilot"] / "panda/board/drivers/fdcan.h",
        roots["calvinpark_openpilot"] / "panda/board/drivers/harness.h",
        roots["calvinpark_openpilot"] / "panda/python/__init__.py",
        roots["calvinpark_openpilot"] / "panda/examples/query_fw_versions.py",
        roots["calvinpark_openpilot"] / "panda/scripts/can_printer.py",
        roots["calvinpark_openpilot"] / "openpilot/selfdrive/pandad/panda.h",
        roots["calvinpark_openpilot"] / "openpilot/selfdrive/pandad/panda.cc",
        roots["calvinpark_openpilot"] / "tsk/COROLLA_INVESTIGATION.md",
        roots["opendbc"] / "opendbc/dbc/generator/toyota/_toyota_2017.dbc",
        roots["opendbc"] / "opendbc/dbc/generator/toyota/_toyota_adas_standard.dbc",
        roots["opendbc"] / "opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc",
        roots["opendbc"] / "opendbc/car/secoc.py",
        roots["opendbc"] / "opendbc/car/toyota/carcontroller.py",
        roots["opendbc"] / "opendbc/car/toyota/toyotacan.py",
        roots["opendbc"] / "opendbc/car/toyota/values.py",
        roots["vance_sienna_2024"] / "docs/tss3-secoc-key-recovery-20260608-zh.md",
        roots["vance_sienna_2024"] / "docs/secoc-20260522-steering-lka-key-validation-full-zh.md",
    ]
    if any(not path.is_file() for path in semantic_inputs):
        print("source-level corroboration skipped because a pinned input is missing")
        print(f"\n== RESULT: {passed} passed, {failed} failed ==")
        return 1

    extract = (roots["icanhack_secoc"] / "extract_keys.py").read_text(encoding="utf-8")
    extract_lower = extract.lower()
    shellcode = (roots["icanhack_secoc"] / "shellcode/main.c").read_text(encoding="utf-8").lower()
    dump_step = (
        roots["toyota_dataflash_secoc_setup"] / "steps/step_dump_dataflash.py"
    ).read_text(encoding="utf-8").lower()
    collect_step = (
        roots["toyota_dataflash_secoc_setup"] / "steps/step_collect_can.py"
    ).read_text(encoding="utf-8").lower()
    verify_key_step = (
        roots["toyota_dataflash_secoc_setup"] / "steps/step_extract_verify_key.py"
    ).read_text(encoding="utf-8").lower()
    eps_probe_step = (
        roots["toyota_dataflash_secoc_setup"] / "steps/step_eps_probe.py"
    ).read_text(encoding="utf-8").lower()
    dump_shellcode_source = (
        roots["toyota_dataflash_secoc_setup"]
        / "payload_source/shellcode/main_ff1ff000_ff209000.c"
    ).read_text(encoding="utf-8").lower()
    uds = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/car/uds.py"
    ).read_text(encoding="utf-8")
    panda_runner = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/car/panda_runner.py"
    ).read_text(encoding="utf-8")
    default_safety = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/safety/modes/defaults.h"
    ).read_text(encoding="utf-8")
    elm327_safety = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/safety/modes/elm327.h"
    ).read_text(encoding="utf-8")
    calvin_toyota_safety = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/safety/modes/toyota.h"
    ).read_text(encoding="utf-8")
    calvin_safety_core = (
        roots["calvinpark_openpilot"]
        / "opendbc_repo/opendbc/safety/safety.h"
    ).read_text(encoding="utf-8")
    panda_can_comms = (
        roots["calvinpark_openpilot"] / "panda/board/can_comms.h"
    ).read_text(encoding="utf-8")
    panda_main = (
        roots["calvinpark_openpilot"] / "panda/board/main.c"
    ).read_text(encoding="utf-8")
    panda_main_comms = (
        roots["calvinpark_openpilot"] / "panda/board/main_comms.h"
    ).read_text(encoding="utf-8")
    panda_tres = (
        roots["calvinpark_openpilot"] / "panda/board/boards/tres.h"
    ).read_text(encoding="utf-8")
    panda_cuatro = (
        roots["calvinpark_openpilot"] / "panda/board/boards/cuatro.h"
    ).read_text(encoding="utf-8")
    panda_can_common = (
        roots["calvinpark_openpilot"] / "panda/board/drivers/can_common.h"
    ).read_text(encoding="utf-8")
    panda_fdcan = (
        roots["calvinpark_openpilot"] / "panda/board/drivers/fdcan.h"
    ).read_text(encoding="utf-8")
    panda_harness = (
        roots["calvinpark_openpilot"] / "panda/board/drivers/harness.h"
    ).read_text(encoding="utf-8")
    panda_python = (
        roots["calvinpark_openpilot"] / "panda/python/__init__.py"
    ).read_text(encoding="utf-8")
    panda_query_fw = (
        roots["calvinpark_openpilot"] / "panda/examples/query_fw_versions.py"
    ).read_text(encoding="utf-8")
    panda_can_printer = (
        roots["calvinpark_openpilot"] / "panda/scripts/can_printer.py"
    ).read_text(encoding="utf-8")
    pandad_header = (
        roots["calvinpark_openpilot"] / "openpilot/selfdrive/pandad/panda.h"
    ).read_text(encoding="utf-8")
    pandad_source = (
        roots["calvinpark_openpilot"] / "openpilot/selfdrive/pandad/panda.cc"
    ).read_text(encoding="utf-8")
    toyota_2017_dbc = (
        roots["opendbc"]
        / "opendbc/dbc/generator/toyota/_toyota_2017.dbc"
    ).read_text(encoding="utf-8")
    toyota_adas_dbc = (
        roots["opendbc"]
        / "opendbc/dbc/generator/toyota/_toyota_adas_standard.dbc"
    ).read_text(encoding="utf-8")
    toyota_secoc_dbc = (
        roots["opendbc"]
        / "opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc"
    ).read_text(encoding="utf-8")
    compact_dbc_facts = json.loads(
        (REPO / "data/external/opendbc/toyota_dbc_facts.json").read_text(encoding="utf-8")
    )
    opendbc_secoc = (
        roots["opendbc"] / "opendbc/car/secoc.py"
    ).read_text(encoding="utf-8")
    opendbc_toyota_controller = (
        roots["opendbc"] / "opendbc/car/toyota/carcontroller.py"
    ).read_text(encoding="utf-8")
    opendbc_toyotacan = (
        roots["opendbc"] / "opendbc/car/toyota/toyotacan.py"
    ).read_text(encoding="utf-8")
    opendbc_toyota_values = (
        roots["opendbc"] / "opendbc/car/toyota/values.py"
    ).read_text(encoding="utf-8")
    vance_final = (
        roots["vance_sienna_2024"]
        / "docs/tss3-secoc-key-recovery-20260608-zh.md"
    ).read_text(encoding="utf-8").lower()
    vance_may = (
        roots["vance_sienna_2024"]
        / "docs/secoc-20260522-steering-lka-key-validation-full-zh.md"
    ).read_text(encoding="utf-8").lower()
    variant_page = (
        REPO / "docs/variants/sienna-8965B4514000.md"
    ).read_text(encoding="utf-8").lower()

    p203 = extract.find("write_data_by_identifier(0x203")
    p201 = extract.find("write_data_by_identifier(0x201")
    p202 = extract.find("write_data_by_identifier(0x202")
    check("Willem tooling writes 0203 -> 0201 -> 0202", -1 < p203 < p201 < p202)
    check("Willem tooling uses exactly five bytes for 0203", '0x203, b"\\x00" * 5' in extract)
    check("Willem tooling transmits to CAN 0x7A1", "addr = 0x7a1" in extract_lower)
    check("DataFlash tooling uses TX 0x7A1", "tx_addr = 0x7a1" in dump_step)
    check("DataFlash tooling expects RX 0x7A9", "rx_addr = 0x7a9" in dump_step)
    check("DataFlash tooling hardcodes Panda bus 0", "bus = 0" in dump_step)
    check("EPS probe independently hardcodes Panda bus 0", "bus = 0" in eps_probe_step)
    check(
        "current CAN collector restricts oracle buses to 0 and 2",
        "oracle_buses = {0, 2}" in collect_step,
    )
    check(
        "current CAN collector recognizes only sync plus Sienna protected IDs",
        "oracle_addrs = {0x0f, 0x131, 0x2e4, 0x344}" in collect_step,
    )
    check(
        "current key verifier likewise restricts protected IDs",
        "protected_addrs = {0x131, 0x2e4, 0x344}" in verify_key_step,
    )
    check(
        "current key verifier likewise restricts buses to 0 and 2",
        "buses = {0, 2}" in verify_key_step,
    )
    check(
        "DataFlash tooling selects ELM327 without an explicit nonzero routing parameter",
        "panda.set_safety_mode(3)" in dump_step,
    )
    check(
        "EPS probe also selects implicit ELM327 param 0",
        "panda.set_safety_mode(3)" in eps_probe_step,
    )
    check(
        "CAN collector also selects implicit ELM327 param 0",
        "panda.set_safety_mode(3)" in collect_step,
    )
    check(
        "DataFlash programming client prefers a 100 ms UDS timeout",
        '{"timeout": 0.1, "debug": false}' in dump_step
        and '{"timeout": 0.1}' in dump_step,
    )
    check(
        "DataFlash flow retries PROGRAMMING after a one-second reset window",
        dump_step.count("diagnostic_session_control(uds_mod.session_type.programming)") == 2
        and "time.sleep(1.0)" in dump_step,
    )

    print("\n== pinned Panda ELM327 and harness routing ==")
    check(
        "ELM327 safety source documents param 0 bus-1 OBD multiplexing",
        "if safety_param == 0, bus 1 is multiplexed to the obd-ii port" in elm327_safety.lower(),
    )
    check(
        "Panda firmware selects OBD CAN2 mode when ELM327 param is zero",
        "if (param == 0u)" in panda_main.lower()
        and "set_can_mode(can_mode_obd_can2)" in panda_main.lower(),
    )
    check(
        "Panda firmware selects normal CAN mode for nonzero ELM327 param",
        "else" in panda_main.lower()
        and "set_can_mode(can_mode_normal)" in panda_main.lower(),
    )
    check(
        "Panda query_fw_versions exposes the same no-OBD routing switch",
        "set_safety_mode(carparams.safetymodel.elm327, 1 if args.no_obd else 0)"
        in panda_query_fw.lower(),
    )
    check(
        "Panda can_printer's pseudo bus 3 is actually OBD-muxed logical bus 1",
        'if canbus == "3":' in panda_can_printer
        and "p.set_obd(True)" in panda_can_printer
        and 'canbus = "1"' in panda_can_printer,
    )
    check(
        "normal openpilot PandaRunner establishes ELM param 1 before fingerprinting",
        "self.p.set_safety_mode(carparams.safetymodel.elm327, 1)" in panda_runner.lower()
        and "self.p.set_obd" in panda_runner.lower(),
    )
    check(
        "ELM safety-policy init ignores the routing parameter",
        ".init = nooutput_init" in elm327_safety
        and "SAFETY_UNUSED(param);" in default_safety,
    )
    elm_tx_body = elm327_safety.split("static bool elm327_tx_hook", 1)[1].split("// If safety_param", 1)[0]
    check("ELM transmit policy itself has no safety-param branch", "param" not in elm_tx_body.lower())
    check(
        "ELM diagnostic whitelist admits EPS request 0x7A1",
        "((msg->addr & 0x1FFFFF00U) != 0x700U)" in elm327_safety
        and (0x7A1 & 0x1FFFFF00) == 0x700,
    )
    check(
        "ELM mode disables software forwarding while leaving the harness relay unintercepted",
        "return (safety_config){NULL, 0, NULL, 0, true}" in default_safety
        and "case SAFETY_ELM327:" in panda_main
        and "set_intercept_relay(false, false);" in panda_main,
    )
    check(
        "Panda logical bus orientation swaps buses 0 and 2 only",
        "bus_config[0].bus_lookup = flipped ? 2u : 0u" in panda_can_common.lower()
        and "bus_config[2].bus_lookup = flipped ? 0u : 2u" in panda_can_common.lower(),
    )
    check(
        "Panda generic harness forwarding is a bus-0/bus-2 pair and excludes bus 1",
        "if (bus_num == 0)" in calvin_safety_core.lower()
        and "destination_bus = 2" in calvin_safety_core.lower()
        and "else if (bus_num == 2)" in calvin_safety_core.lower()
        and "destination_bus = 0" in calvin_safety_core.lower()
        and "destination_bus = -1" in calvin_safety_core.lower(),
    )
    check(
        "harness default and ELM both keep the physical intercept relay closed/pass-through",
        "set_intercept_relay(false, false);" in panda_harness
        and panda_main.count("set_intercept_relay(false, false);") >= 3,
    )
    check(
        "harness orientation changes reapply the remembered safety mode and parameter",
        "can_set_orientation(harness.status == HARNESS_STATUS_FLIPPED);" in panda_main
        and "set_safety_mode(current_safety_mode, current_safety_param);" in panda_main,
    )
    obd_handler = panda_main_comms.split("// **** 0xdb: set OBD CAN multiplexing mode", 1)[1].split("// **** 0xdc: set safety mode", 1)[0]
    safety_handler = panda_main_comms.split("// **** 0xdc: set safety mode", 1)[1].split("// **** 0xdd:", 1)[0]
    check(
        "Panda set_obd USB request changes board CAN mode without updating remembered safety param",
        "current_board->set_can_mode" in obd_handler and "current_safety_param" not in obd_handler,
    )
    check(
        "Panda set_safety_mode USB request updates the persistent safety state through set_safety_mode",
        "set_safety_mode(req->param1, (uint16_t)req->param2);" in safety_handler
        and "current_safety_param = param;" in calvin_safety_core,
    )
    check(
        "Python set_obd and set_safety_mode are distinct USB controls",
        "controlWrite(Panda.REQUEST_OUT, 0xdb, int(obd), 0, b'')" in panda_python
        and "controlWrite(Panda.REQUEST_OUT, 0xdc, mode, param, b'')" in panda_python,
    )
    check(
        "Panda constructor defaults to disabling heartbeat checks for standalone scripts",
        "disable_checks: bool = True" in panda_python
        and "self.set_heartbeat_disabled()" in panda_python,
    )
    check(
        "pandad marks returned CAN with source offset 0x80",
        "#define CAN_RETURNED_BUS_OFFSET 0x80U" in pandad_header
        and "canData.src += CAN_RETURNED_BUS_OFFSET" in pandad_source,
    )
    check(
        "pandad marks rejected CAN with source offset 0xC0",
        "#define CAN_REJECTED_BUS_OFFSET   0xC0U" in pandad_header
        and "canData.src += CAN_REJECTED_BUS_OFFSET" in pandad_source,
    )
    check(
        "Tres OBD mode changes the FDCAN2 physical pin/transceiver selection",
        "case can_mode_obd_can2:" in panda_tres.lower()
        and "gpio_af9_fdcan2" in panda_tres.lower()
        and "enable_can_transceiver(2u, true)" in panda_tres.lower()
        and "enable_can_transceiver(4u, true)" in panda_tres.lower(),
    )
    check(
        "Tres normal/OBD selection is explicitly coupled to harness orientation",
        "(bool)(mode == CAN_MODE_NORMAL) != (bool)(harness.status == HARNESS_STATUS_FLIPPED)"
        in panda_tres,
    )
    check(
        "comma 4 Cuatro inherits the Tres FDCAN2 physical-routing implementation",
        ".set_can_mode = tres_set_can_mode" in panda_cuatro.lower(),
    )
    check(
        "UdsClient bus selection only feeds CAN send and receive-bus filtering",
        "self.tx(self.tx_addr, msg, self.bus)" in uds
        and "return bus == self.bus and addr == self.rx_addr" in uds,
    )
    check(
        "Panda CAN send path maps the UDS logical bus through bus_config into an MCU CAN controller",
        "can_send(&to_push, to_push.bus, false);" in panda_can_comms
        and "process_can(CAN_NUM_FROM_BUS_NUM(bus_number));" in panda_can_common
        and "uint8_t bus_number = BUS_NUM_FROM_CAN_NUM(can_number);" in panda_fdcan,
    )
    check(
        "FDCAN2 mux error recovery explicitly accounts for ACK errors while switching physical paths",
        "while multiplexing between buses 1 and 3 we are getting ACK errors" in panda_fdcan
        and "can_clear_send(FDCANx, can_number);" in panda_fdcan,
    )
    check("dump shellcode transmits CAN 0x7A9", "= 0x7a9;" in shellcode)
    for address in (
        "0xffd20250", "0xffd202d0", "0xffd24000", "0xffd24004",
        "0xffd24008", "0xffd2400c", "0xffd24010",
    ):
        check(f"dump shellcode independently uses RSCFD {address}", address in shellcode)
        check(
            f"DataFlash source independently uses RSCFD {address}",
            address in dump_shellcode_source,
        )
    check(
        "DataFlash source uses the candidate's CAN 0x7A9 word-frame expression",
        "((int)addr << 8) | 0x07" in dump_shellcode_source
        and "= *addr;" in dump_shellcode_source
        and "= 0x7a9;" in dump_shellcode_source,
    )
    check(
        "DataFlash source carries the candidate's boot-reset target",
        "0x0000157e" in dump_shellcode_source and "bl_reset();" in dump_shellcode_source,
    )
    check(
        "public extraction tooling does not name functional 0x777",
        "0x777" not in extract_lower and "0x777" not in dump_step and "0x777" not in shellcode,
    )
    check(
        "public UDS enum identifies F181 as application software ID",
        "APPLICATION_SOFTWARE_IDENTIFICATION = 0xF181" in uds,
    )
    check(
        "pinned Toyota DBC names CAN 0x260 STEER_TORQUE_SENSOR",
        "BO_ 608 STEER_TORQUE_SENSOR: 8" in toyota_2017_dbc,
    )
    for signal in (
        "STEER_OVERRIDE", "STEER_ANGLE_INITIALIZING", "STEER_TORQUE_DRIVER",
        "STEER_ANGLE", "STEER_TORQUE_EPS", "CHECKSUM",
    ):
        check(f"pinned CAN 0x260 DBC contains {signal}", signal in toyota_2017_dbc)
    print("\n== tracked compact opendbc corroboration ==")
    check(
        "compact DBC facts pin the locked opendbc commit",
        compact_dbc_facts["repository"]["commit"] == lock["repositories"]["opendbc"]["commit"],
    )
    for key, rel in (
        ("toyota_2017", "opendbc/dbc/generator/toyota/_toyota_2017.dbc"),
        ("toyota_secoc_pt", "opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc"),
    ):
        check(
            f"compact DBC source hash {key} matches pinned checkout",
            compact_dbc_facts["sources"][key]["sha256"] == sha256(roots["opendbc"] / rel),
        )
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

    check(
        "pinned Toyota DBC names CAN 0x262 EPS_STATUS",
        "BO_ 610 EPS_STATUS: 8 EPS" in toyota_secoc_dbc,
    )
    check(
        "pinned CAN 0x262 DBC places checksum in final byte",
        "SG_ CHECKSUM : 63|8@0+" in toyota_secoc_dbc,
    )
    check(
        "pinned Toyota checksum source matches recovered additive algorithm",
        "def toyota_checksum(address: int, sig, d: bytearray) -> int:" in opendbc_toyotacan
        and "s = len(d)" in opendbc_toyotacan
        and "while addr:" in opendbc_toyotacan
        and "s += addr & 0xFF" in opendbc_toyotacan
        and "for i in range(len(d) - 1):" in opendbc_toyotacan
        and "s += d[i]" in opendbc_toyotacan
        and "return s & 0xFF" in opendbc_toyotacan,
    )
    check(
        "pinned Toyota SecOC DBC names CAN 0x2E4 STEERING_LKA",
        "BO_ 740 STEERING_LKA: 8" in toyota_secoc_dbc,
    )
    check(
        "pinned CAN 0x2E4 DBC identifies signed B1..B2 torque command",
        "SG_ STEER_TORQUE_CMD : 15|16@0-" in toyota_secoc_dbc,
    )
    for can_id, message_name in (
        (278, "GAS_PEDAL"),
        (305, "STEERING_LTA_2"),
        (375, "PCM_CRUISE_3"),
        (387, "ACC_CONTROL_2"),
        (589, "PCM_CRUISE_4"),
        (643, "PRE_COLLISION"),
        (740, "STEERING_LKA"),
        (836, "PRE_COLLISION_2"),
    ):
        block = dbc_message(toyota_secoc_dbc, can_id, message_name)
        check(
            f"classic SecOC profile contains {message_name} at CAN {can_id:#x}",
            bool(block),
        )
        for signal in ("AUTHENTICATOR", "RESET_FLAG", "MSG_CNT_LOWER"):
            check(
                f"CAN {can_id:#x} {message_name} carries {signal}",
                signal in block,
            )

    print("\n== pinned opendbc SecOC sender ==")
    check(
        "opendbc authenticates DataID_be16 plus payload4 plus freshness48",
        "struct.pack('>H', addr) + payload + freshness_value" in opendbc_secoc,
    )
    check(
        "opendbc packs trip16/reset20/message8/reset-low2 freshness",
        "(reset_cnt << 12) | ((msg_cnt & 0xff) << 4) | (reset_flag << 2)"
        in opendbc_secoc,
    )
    check(
        "opendbc transmits the first 28 CMAC bits",
        "cmac.digest().hex()[:7]" in opendbc_secoc,
    )
    check(
        "opendbc synchronization authenticator defaults to DataID 0x00F",
        "def build_sync_mac(key, trip_cnt, reset_cnt, id_=0xf):" in opendbc_secoc,
    )
    check(
        "Toyota controller signs three independent output streams",
        opendbc_toyota_controller.count("add_mac(self.secoc_key") == 3,
    )
    for counter in (
        "secoc_lka_message_counter",
        "secoc_lta_message_counter",
        "secoc_acc_message_counter",
    ):
        check(f"Toyota controller tracks {counter}", counter in opendbc_toyota_controller)
    check(
        "Toyota controller checks the synchronization authenticator",
        "expected_mac = build_sync_mac(" in opendbc_toyota_controller,
    )
    for message_name in ("STEERING_LKA", "STEERING_LTA_2", "ACC_CONTROL_2"):
        check(
            f"Toyota CAN builder constructs {message_name}",
            f'make_can_msg("{message_name}"' in opendbc_toyotacan,
        )
    for can_id, message_name in (
        (740, "STEERING_LKA"),
        (305, "STEERING_LTA_2"),
        (387, "ACC_CONTROL_2"),
    ):
        check(
            f"SecOC DBC binds {message_name} to CAN {can_id:#x}",
            f"BO_ {can_id} {message_name}: 8" in toyota_secoc_dbc,
        )
    check(
        "opendbc marks fourth-generation Sienna as a SecOC platform",
        "TOYOTA_SIENNA_4TH_GEN = ToyotaSecOCPlatformConfig(" in opendbc_toyota_values,
    )
    check(
        "opendbc marks 2021-23 RAV4 Prime as a SecOC platform",
        "TOYOTA_RAV4_PRIME = ToyotaSecOCPlatformConfig(" in opendbc_toyota_values
        and 'ToyotaSecOcCarDocs("Toyota RAV4 Prime 2021-23"' in opendbc_toyota_values,
    )
    check(
        "Toyota SecOC controller derives outbound freshness from live synchronization",
        "CS.secoc_synchronization['TRIP_CNT']" in opendbc_toyota_controller
        and "CS.secoc_synchronization['RESET_CNT']" in opendbc_toyota_controller,
    )
    check(
        "wrong sync MAC is logged but does not directly abort controller update",
        'carlog.error("SecOC synchronization MAC mismatch, wrong key?")' in opendbc_toyota_controller,
    )
    check(
        "ACC_CONTROL_2 signing is gated by openpilot longitudinal control",
        "if self.CP.openpilotLongitudinalControl:" in opendbc_toyota_controller
        and "acc_cmd_2 = add_mac(self.secoc_key" in opendbc_toyota_controller,
    )

    print("\n== pinned forced RAV4 Prime SecOC safety substitution ==")
    check(
        "stock-longitudinal SecOC safety whitelist includes camera replacement 0x2E4 and 0x131",
        "TOYOTA_COMMON_SECOC_TX_MSGS" in calvin_toyota_safety
        and "{0x2E4, 0, 8, .check_relay = true}" in calvin_toyota_safety
        and "{0x131, 0, 8, .check_relay = true}" in calvin_toyota_safety,
    )
    check(
        "base Toyota safety whitelist also replaces 0x191 and 0x412",
        "{0x191, 0, 8, .check_relay = true}" in calvin_toyota_safety
        and "{0x412, 0, 8, .check_relay = true}" in calvin_toyota_safety,
    )
    check(
        "SecOC openpilot-long whitelist adds authenticated 0x183",
        "{0x183, 0, 8, .check_relay = true}" in calvin_toyota_safety,
    )
    check(
        "stock-longitudinal SecOC selects the whitelist without 0x183",
        "if (toyota_secoc)" in calvin_toyota_safety
        and "if (toyota_stock_longitudinal)" in calvin_toyota_safety
        and "SET_TX_MSGS(TOYOTA_SECOC_TX_MSGS, ret);" in calvin_toyota_safety
        and "SET_TX_MSGS(TOYOTA_SECOC_LONG_TX_MSGS, ret);" in calvin_toyota_safety,
    )
    check(
        "generic Panda safety forwarding is bus 0<->2",
        "if (bus_num == 0)" in calvin_safety_core
        and "destination_bus = 2;" in calvin_safety_core
        and "else if (bus_num == 2)" in calvin_safety_core
        and "destination_bus = 0;" in calvin_safety_core,
    )
    check(
        "generic forwarding blocks stock frames matching destination check_relay TX entries",
        "m->check_relay" in calvin_safety_core
        and "m->addr == addr" in calvin_safety_core
        and "m->bus == (unsigned int)destination_bus" in calvin_safety_core
        and "blocked = true;" in calvin_safety_core,
    )
    check(
        "Toyota safety has no custom forward hook overriding the generic substitution",
        ".fwd =" not in calvin_toyota_safety,
    )
    check(
        "RAV4 Prime SecOC platform flags do not include UNSUPPORTED_DSU",
        "TOYOTA_RAV4_PRIME = ToyotaSecOCPlatformConfig(" in opendbc_toyota_values
        and "flags=ToyotaFlags.UNSUPPORTED_DSU" not in opendbc_toyota_values[opendbc_toyota_values.index("TOYOTA_RAV4_PRIME = ToyotaSecOCPlatformConfig("):opendbc_toyota_values.index("TOYOTA_YARIS =", opendbc_toyota_values.index("TOYOTA_RAV4_PRIME = ToyotaSecOCPlatformConfig("))],
    )
    check(
        "SecOC platform base flags are TSS2 NO_DSU SECOC",
        "self.flags |= ToyotaFlags.TSS2 | ToyotaFlags.NO_DSU | ToyotaFlags.SECOC" in opendbc_toyota_values,
    )
    check(
        "STEERING_LKA is always generated and SecOC-signed when the platform flag is set",
        "steer_command = toyotacan.create_steer_command" in opendbc_toyota_controller
        and "steer_command = add_mac(self.secoc_key" in opendbc_toyota_controller,
    )
    check(
        "STEERING_LTA and LTA_2 are generated on frame mod 2",
        "if self.frame % 2 == 0 and self.CP.carFingerprint in TSS2_CAR:" in opendbc_toyota_controller
        and "create_lta_steer_command_2" in opendbc_toyota_controller,
    )
    check(
        "LKAS HUD is generated on frame mod 20 or UI edge",
        "if self.frame % 20 == 0 or send_ui:" in opendbc_toyota_controller
        and "create_ui_command" in opendbc_toyota_controller,
    )
    check(
        "stock-long cancel chooses ACC_CONTROL unless UNSUPPORTED_DSU",
        "if self.CP.carFingerprint in UNSUPPORTED_DSU_CAR:" in opendbc_toyota_controller
        and "create_acc_cancel_command" in opendbc_toyota_controller
        and "create_accel_command(self.packer, 0, pcm_cancel_cmd" in opendbc_toyota_controller,
    )
    check(
        "ACC_CONTROL_2 is generated only inside openpilot longitudinal branch",
        "if self.CP.openpilotLongitudinalControl:" in opendbc_toyota_controller
        and "acc_cmd_2 = toyotacan.create_accel_command_2" in opendbc_toyota_controller,
    )

    print("\n== pinned opendbc CAN 0x344 provenance ==")
    secoc_344 = dbc_message(toyota_secoc_dbc, 836, "PRE_COLLISION_2")
    check(
        "pinned Toyota SecOC DBC names CAN 0x344 PRE_COLLISION_2 with logical DSU node",
        "BO_ 836 PRE_COLLISION_2: 8 DSU" in secoc_344,
    )
    for signal in ("AUTHENTICATOR", "RESET_FLAG", "MSG_CNT_LOWER"):
        check(f"pinned CAN 0x344 SecOC block contains {signal}", signal in secoc_344)
    legacy_344 = dbc_message(toyota_adas_dbc, 836, "PRE_COLLISION_2")
    check(
        "pinned legacy CAN 0x344 DBC preserves logical DSU node",
        "BO_ 836 PRE_COLLISION_2: 8 DSU" in legacy_344,
    )
    for signal in ("DSS1GDRV", "PCSALM", "IBTRGR", "PBATRGR", "PREFILL", "AVSTRGR"):
        check(f"pinned legacy CAN 0x344 block contains PCS signal {signal}", signal in legacy_344)

    print("\n== pinned Vance 8965B4514000 field report ==")
    for token, label in (
        ("8965b4514000", "application software ID"),
        ("0xff200000 - 0xff208000", "32 KiB DataFlash range"),
        ("0xff206e14", "candidate absolute address"),
        ("`28180`", "candidate offset"),
        ("1d1c53a6d634016a", "public key SHA-256 prefix"),
        ("`0x7a1`", "physical diagnostic TX"),
        ("`0x7a9`", "physical diagnostic RX"),
        ("`1024/1024`", "corrected synchronization result"),
        ("`226/226`", "CAN 0x131 validation count"),
        ("`225/225`", "CAN 0x2E4 validation count"),
        ("`112/113`", "CAN 0x344 validation count"),
        ("`563/564`", "protected-frame aggregate"),
        ("`730/750`", "later end-to-end protected result"),
    ):
        check(f"Vance final report contains {label}", token in vance_final)
    check(
        "Vance May report records the superseded sync mismatch",
        "0x0f sync mac match = 0/512" in vance_may,
    )
    check(
        "local variant page marks the May sync conclusion superseded",
        "may" in variant_page and "superseded" in variant_page
        and "1024/1024" in variant_page,
    )
    check(
        "local variant page keeps 4514000 runtime architecture unresolved",
        "bounded but unresolved" in variant_page
        and "missing codeflash/runtime access" in variant_page,
    )

    print("\n== pinned Vance deployment-bundle payloads ==")
    bundle_v3 = (
        roots["vance_sienna_2024"]
        / "scripts/secoc/20260531_othersienna_secoc_bundle_v3.zip"
    )
    with zipfile.ZipFile(bundle_v3) as archive:
        member_names = set(archive.namelist())
        standard_ciphertext = archive.read("payload_dataflash_ff200000_ff208000.bin")
        candidate_ciphertext = archive.read(
            "payload_candidate_f05_dataflash_ff200000_ff208000.bin"
        )
        bundle_readme = archive.read(
            "README_other_sienna_secoc_bundle_zh.md"
        ).decode("utf-8")

    check(
        "bundle standard payload matches committed DataFlash fixture",
        standard_ciphertext
        == (REPO / "tests/fixtures/payloads/dataflash_dump_payload.bin").read_bytes(),
    )
    check(
        "bundle candidate-f05 ciphertext SHA-256",
        hashlib.sha256(candidate_ciphertext).hexdigest()
        == "296d87d2e89b9c7e800122e4c7f6d3b9c876362e52586530cdd53c86ba1116f5",
    )
    check(
        "bundle candidate-f05 matches committed fixture",
        candidate_ciphertext
        == (REPO / "tests/fixtures/payloads/candidate_f05_dataflash_payload.bin").read_bytes(),
    )
    candidate_bundle_members = []
    for bundle_name in (
        "20260531_othersienna_secoc_bundle.zip",
        "20260531_othersienna_secoc_bundle_v2.zip",
        "20260531_othersienna_secoc_bundle_v3.zip",
    ):
        with zipfile.ZipFile(
            roots["vance_sienna_2024"] / "scripts/secoc" / bundle_name
        ) as candidate_bundle:
            candidate_bundle_members.append(
                candidate_bundle.read(
                    "payload_candidate_f05_dataflash_ff200000_ff208000.bin"
                )
            )
    check(
        "all three Vance deployment bundles carry the identical candidate-f05",
        all(payload == candidate_ciphertext for payload in candidate_bundle_members),
    )

    print("\n== candidate-f05 historical provenance ==")
    vance_root = roots["vance_sienna_2024"]
    earliest_commit = "97ba3d1d9e77a6e047887da04767538fe81fc674"
    earliest_meta = subprocess.run(
        ["git", "-C", str(vance_root), "show", "-s", "--format=%H|%ai|%an", earliest_commit],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    check(
        "earliest public Vance bundle commit metadata",
        earliest_meta
        == f"{earliest_commit}|2026-05-31 20:26:27 +0800|Vance425",
        earliest_meta,
    )
    earliest_zip = subprocess.run(
        ["git", "-C", str(vance_root), "show",
         f"{earliest_commit}:scripts/secoc/20260531_othersienna_secoc_bundle.zip"],
        check=True, capture_output=True,
    ).stdout
    with zipfile.ZipFile(io.BytesIO(earliest_zip)) as archive:
        earliest_candidate = archive.read("payload_candidate_f05_dataflash_ff200000_ff208000.bin")
        earliest_manifest = json.loads(archive.read("manifest_sha256.json").decode("utf-8-sig"))
        earliest_readme = archive.read("README_other_sienna_secoc_bundle_zh.md").decode("utf-8")
    check("earliest public bundle already contains identical candidate-f05",
          earliest_candidate == candidate_ciphertext)
    check("earliest public bundle README gives candidate-only bounded description",
          "保留候選 payload，預設不使用" in earliest_readme)
    manifest_text = json.dumps(earliest_manifest, ensure_ascii=False)
    check("earliest public manifest pins candidate ciphertext SHA",
          "296d87d2e89b9c7e800122e4c7f6d3b9c876362e52586530cdd53c86ba1116f5" in manifest_text)

    patch_commit = "abc871308b0933c13a2551852857c350ea0f5386"
    patch_source = subprocess.run(
        ["git", "-C", str(vance_root), "show",
         f"{patch_commit}:scripts/secoc/patch_secoc_payload_dump_range.py"],
        check=True, capture_output=True, text=True,
    ).stdout
    check("May-28 Vance helper is range-patch/reseal, not shellcode compiler",
          "replace_exact" in patch_source and "old_start" in patch_source
          and "old_end" in patch_source and "v850-elf-gcc" not in patch_source)

    bk_root = roots["toyota_dataflash_secoc_setup"]
    bk_first = subprocess.run(
        ["git", "-C", str(bk_root), "log", "--diff-filter=A", "--format=%H|%ai",
         "--", "payload_source/shellcode/main_ff1ff000_ff209000.c"],
        check=True, capture_output=True, text=True,
    ).stdout.strip().splitlines()
    check("Bk2ol public source first appears after Vance candidate",
          bk_first == ["db453752beeb7cdd024a1a9c38c6711c981e75ad|2026-07-11 18:29:18 -0500"],
          repr(bk_first))
    bk_build = (bk_root / "payload_source/shellcode/build.sh").read_text(encoding="utf-8")
    check("later Bk2ol source family uses v850 gcc plus objcopy",
          "v850-elf-gcc" in bk_build and "v850-elf-objcopy" in bk_build)

    codeflash = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
    zero = bytes(16)

    def decode_payload(ciphertext: bytes, build_secret: bytes) -> tuple[bytes, bool, bool]:
        derived = AES.new(build_secret, AES.MODE_ECB).encrypt(zero)
        plaintext = AES.new(derived, AES.MODE_CBC, zero).decrypt(ciphertext)
        cmac = CMAC.new(derived, ciphermod=AES)
        cmac.update(zero + plaintext[:0xFF0])
        cmac_ok = cmac.digest() == plaintext[0xFF0:]
        crc_ok = binascii.crc32(plaintext[:0xFF0]) % (1 << 32) == 0xFFFFFFFF
        return plaintext, cmac_ok, crc_ok

    standard_plain, standard_cmac, standard_crc = decode_payload(
        standard_ciphertext, codeflash[0xBFD8:0xBFE8]
    )
    candidate_normal_plain, candidate_normal_cmac, candidate_normal_crc = decode_payload(
        candidate_ciphertext, codeflash[0xBFD8:0xBFE8]
    )
    candidate_f05_plain, candidate_f05_cmac, candidate_f05_crc = decode_payload(
        candidate_ciphertext, codeflash[0xBFE8:0xBFF8]
    )
    check("bundle standard payload authenticates with payload-build secret",
          standard_cmac and standard_crc)
    check("candidate-f05 does not authenticate with payload-build secret",
          not candidate_normal_cmac and not candidate_normal_crc)
    check("candidate-f05 authenticates with SecurityAccess secret as build secret",
          candidate_f05_cmac and candidate_f05_crc)
    check(
        "candidate-f05 has valid callback and CRC descriptor",
        struct.unpack_from("<I", candidate_f05_plain, 0xFD0)[0] == 0xFEBF0000
        and struct.unpack_from("<II", candidate_f05_plain, 0xFE0)
        == (0xFEBF0000, 0xFF0),
    )
    check(
        "candidate-f05 plaintext materially differs from standard payload",
        sum(a != b for a, b in zip(standard_plain, candidate_f05_plain)) == 380
        and sum(a != b for a, b in zip(standard_plain[:0xFD0], candidate_f05_plain[:0xFD0]))
        == 360,
    )
    check(
        "bundle README labels candidate-f05 retained and not default",
        "保留候選 payload，預設不使用" in bundle_readme,
    )
    completed_outputs = {
        "metadata.json", "transcript.jsonl", "frames.csv", "frames.jsonl",
        "protected_frames.jsonl", "sync_frames.jsonl",
        "secoc_key_probe_results.json", "secoc_key_probe_results.csv",
    }
    check(
        "bundle contains no completed partner dump/capture outputs",
        not any(
            Path(name).name in completed_outputs
            or Path(name).name.startswith("dump_")
            for name in member_names
        ),
    )
    check(
        "wrong-key candidate plaintext is structurally invalid",
        struct.unpack_from("<I", candidate_normal_plain, 0xFD0)[0] != 0xFEBF0000,
    )

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
