#!/usr/bin/env python3
"""Verify the authenticated meter dumper against exact firmware bytes.

GNU sim executes the target's relocated crypto, watchdog and payload code.
GDB supplies inherited RSCAN configuration and transmit results; it is not a
D1L peripheral simulation.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import re
import struct
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

from tools import REPO_ROOT

from tools.rh850_codeflash import run as run_codeflash
from tsk.common.payload_package import derive_payload_key
from tsk.dumper.build_rav4_meter_payload import (
    CRC_OFFSET,
    DID_IV,
    DID_KEY,
    PAYLOAD_ROOT,
    TAG_OFFSET,
    TRIGGER_ADDRESS,
    TRIGGER_LENGTH,
    TRIGGER_OPTION,
    TRIGGER_ROUTINE,
    build,
)
from tsk.dumper.reassemble import CodeFlashReassembler

ROOT = REPO_ROOT
IMAGE = ROOT / "firmware/r4p-838004AD91/cflash.bin"
BOOT_IMAGE = ROOT / "firmware/r4p-838004AD91/boot.bin"
IMAGE_SHA256 = "cc75cac2aaa4a648dadcad3d3d59d0c1bb293c53f1dbfcf9bc0fc88b4b6a4322"
BOOT_SHA256 = "e8c3058f637725ca9a32b3ec6e38eb9408cf76c18847139cac22b853da6225d9"
LOAD = 0xFEDD7800
TMC = 0xFFD00272
TMSTS = 0xFFD002F2
TMID = 0xFFD01220
TMPTR = TMID + 4
DATA = TMID + 8
RESET = 0x00000AD4
RETURN_STOP = 0x001FF000
GP = 0xFEDD9AD4
TP = 0xFEDD_BA98
CRYPTO_BASE = 0xFEDA0000
RUNTIME_COPIES = (
    (0xFEDC0110, 0x1510, 0x34A0),
    (0xFEDC20D0, 0x34A0, 0x9F2C),
    (0xFEDD0110, 0x9F2C, 0xB8C0),
    (0xFEDD3A98, 0xC0AC, 0xCD00),
    (0xFEDD46EC, 0xCD00, 0xD370),
    (0xFEDD543C, 0xD370, 0xDF0C),
    (0xFEDD8000, 0xB8C0, 0xC0AC),
    (0xFEDDA884, 0xDF0C, 0xDF50),
)
BOOT_RUNTIME_COPIES = (
    (0xFEDC8B5C, 0x0000, 0x75B4),
    (0xFEDD4D5C, 0x75B4, 0x7C94),
)



def symbols(path: Path) -> dict[str, int]:
    result = {}
    for line in path.read_text().splitlines():
        fields = line.split()
        if len(fields) == 3:
            result[fields[2].lstrip("_")] = int(fields[0], 16)
    return result

def runtime_loads(
    work: Path, image: bytes, boot: bytes | None = None,
) -> tuple[tuple[int, Path], ...]:
    loads = []
    copies = [(image, *row) for row in RUNTIME_COPIES]
    if boot is not None:
        copies.extend((boot, *row) for row in BOOT_RUNTIME_COPIES)
    for source, address, start, end in copies:
        path = work / f"runtime-{address:08x}.bin"
        path.write_bytes(source[start:end])
        loads.append((address, path))
    return tuple(loads)


def inspect_package(payload: bytes, plaintext: bytes) -> None:
    key = derive_payload_key(PAYLOAD_ROOT, DID_KEY)
    assert struct.unpack_from("<I", plaintext, CRC_OFFSET)[0] == (
        binascii.crc32(plaintext[:CRC_OFFSET]) & 0xFFFFFFFF
    )
    cmac = CMAC.new(key, ciphermod=AES)
    cmac.update(DID_IV + plaintext[:TAG_OFFSET])
    assert plaintext[TAG_OFFSET:] == cmac.digest()


def verify_package_with_firmware(work: Path, payload: Path, image: bytes) -> None:
    plaintext = payload.with_suffix(".plaintext.bin").read_bytes()
    inspect_package(payload.read_bytes(), plaintext)
    derived = derive_payload_key(PAYLOAD_ROOT, DID_KEY)
    vector = bytearray(0x4000)
    root = CRYPTO_BASE
    did_key = root + 0x10
    did_iv = root + 0x20
    derived_out = root + 0x30
    ciphertext = root + 0x100
    decrypted = root + 0x900
    kdf_context = root + 0x1200
    cbc_context = root + 0x1400
    cmac_context = root + 0x1600
    tag_out = root + 0x1800
    stack = root + 0x3F00
    vector[0:0x10] = PAYLOAD_ROOT
    vector[0x10:0x20] = DID_KEY
    vector[0x20:0x30] = DID_IV
    vector[0x100:0x900] = payload.read_bytes()
    vector_path = work / "crypto-vector.bin"
    vector_path.write_bytes(vector)

    commands = [
        f"set $sp = 0x{stack:x}", f"set $lp = 0x{RETURN_STOP:x}",
        f"set $r4 = 0x{GP:x}", f"set $r5 = 0x{TP:x}",
        f"break *0x{RETURN_STOP:x}",
    ]

    def call(
        address: int, r6: int, r7: int = 0, r8: int = 0, r9: int = 0,
        fifth: int | None = None, expected: int = 0,
    ) -> None:
        commands.extend([
            f"set $r6 = 0x{r6:x}", f"set $r7 = 0x{r7:x}",
            f"set $r8 = 0x{r8:x}", f"set $r9 = 0x{r9:x}",
            f"set $r31 = 0x{RETURN_STOP:x}",
        ])
        if fifth is not None:
            commands.append(f"set {{unsigned int}}0x{stack:x} = 0x{fifth:x}")
        commands.extend([
            f"set $pc = 0x{address:x}", "continue",
            f'if $r10 != 0x{expected:x}\nprintf "firmware call failed at '
            f'0x%x: %u\\n", 0x{address:x}, $r10\nquit 1\nend',
        ])

    assert TRIGGER_ROUTINE == 0xFF00 and TRIGGER_OPTION == b"\x45\x00"
    commands.append("set {unsigned char}0xfedd3710 = 1")
    call(0xFEDC6F08, TRIGGER_ADDRESS, TRIGGER_LENGTH)
    call(0xFEDD04C4, root, 0x10, kdf_context)
    call(0xFEDD0196, did_key, derived_out, 0x10, kdf_context)
    call(0xFEDD1020, derived_out, 0x10, did_iv, 0x10, cbc_context)
    for offset in range(0, 0x800, 0x10):
        call(0xFEDD0ECC, ciphertext + offset, decrypted + offset, 0x10, cbc_context)
    call(
        0xFEDD10CC, decrypted, TAG_OFFSET, 0, 1,
        expected=binascii.crc32(plaintext[:TAG_OFFSET]) & 0xFFFFFFFF,
    )
    call(0xFEDD0D66, derived_out, 0x10, cmac_context)
    call(0xFEDD0B1E, cmac_context)
    call(0xFEDD0BBE, did_iv, tag_out, 0x10, 0, cmac_context)
    for offset in range(0, TAG_OFFSET - 0x10, 0x10):
        call(0xFEDD0BBE, decrypted + offset, tag_out, 0x10, 0, cmac_context)
    call(0xFEDD0BBE, decrypted + TAG_OFFSET - 0x10, tag_out, 0x10, 1, cmac_context)
    commands.extend([
        f"dump binary memory /out/firmware-derived.bin 0x{derived_out:x} 0x{derived_out + 16:x}",
        f"dump binary memory /out/firmware-plaintext.bin 0x{decrypted:x} 0x{decrypted + 0x800:x}",
        f"dump binary memory /out/firmware-tag.bin 0x{tag_out:x} 0x{tag_out + 16:x}",
    ])
    sim = work / "crypto-sim"
    run_codeflash(
        root=ROOT, image_path=IMAGE, entry=0,
        ram_loads=(*runtime_loads(work, image), (CRYPTO_BASE, vector_path)),
        memory_regions=("0xfeda0000,0x4000", "0xfedc0000,0x40000"),
        stop=f"0x{RETURN_STOP:x}", gdb_commands=commands,
        assertions=("$r10 == 0",), timeout=180, output_dir=sim,
    )
    assert (sim / "firmware-derived.bin").read_bytes() == derived
    assert (sim / "firmware-plaintext.bin").read_bytes() == plaintext
    assert (sim / "firmware-tag.bin").read_bytes() == plaintext[TAG_OFFSET:]
    print(
        "PASS authenticated-package: firmware AES-CBC/CRC32/CMAC accepted exact payload; "
        "FF00 range accepted", flush=True,
    )


def verify_diagnostic_path(
    work: Path, payload: Path, image: bytes, boot: bytes,
) -> None:
    """Run one stateful upload, authentication, trigger and dump session."""
    work.mkdir(parents=True, exist_ok=True)
    package = payload.read_bytes()
    plaintext = payload.with_suffix(".plaintext.bin").read_bytes()
    inspect_package(package, plaintext)
    syms = symbols(payload.with_suffix(".nm"))
    terminal = syms["terminal_reset"]
    disasm = payload.with_suffix(".disasm").read_text()
    stores = re.findall(
        r"^([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s+st\.b\s+(?!r0,)([^\n]+)",
        disasm, re.M,
    )
    assert len(stores) == 1, stores
    submitted = int(stores[0][0], 16) + len(stores[0][1].split())

    requests = {
        "download": (
            b"\x34\x01\x46\x01\x00" + struct.pack(">II", LOAD, len(package))
        ),
        "block1": b"\x36\x01" + package[:0x400],
        "block2": b"\x36\x02" + package[0x400:],
        "exit": b"\x37",
        "verify": (
            b"\x31\x01\x10\xf0\x45\x00" + struct.pack(">II", LOAD, len(package))
        ),
        "trigger": (
            b"\x31\x01" + struct.pack(">H", TRIGGER_ROUTINE) + TRIGGER_OPTION
            + struct.pack(">II", TRIGGER_ADDRESS, TRIGGER_LENGTH)
        ),
    }
    request_base = 0xFEDA2000
    request_blob = bytearray(0x2000)
    request_addresses = {}
    cursor = 0
    for name, data in requests.items():
        request_addresses[name] = request_base + cursor
        request_blob[cursor:cursor + len(data)] = data
        cursor = (cursor + len(data) + 0x3F) & ~0x3F
    request_path = work / "diagnostic-requests.bin"
    request_path.write_bytes(request_blob)

    scratch = 0xFEDA0000
    pdu = 0xFEDA1000
    available = 0xFEDA1010
    commands = [
        "set $r3 = 0xfedd7000",
        f"set $r4 = 0x{GP:x}",
        f"set $r5 = 0x{TP:x}",
        "set $r30 = 0xfedd5fd8",
        f"break *0x{RETURN_STOP:x}",
        "commands 1", "silent", "end",
        # The simulator has no response transport. Report successful transmit
        # confirmation to the exact SecurityAccess confirmation callback.
        "break *0xfedcbe86",
        "commands 2", "silent", "set $r6 = 0", "continue", "end",
    ]

    def call(address: int, *registers: int) -> None:
        commands.extend(
            [f"set $r{index + 6} = 0x{value:x}"
             for index, value in enumerate(registers)]
            + [
                f"set $r31 = 0x{RETURN_STOP:x}",
                f"set $pc = 0x{address:x}",
                "continue",
            ]
        )

    def receive_pointer(address: int, length: int) -> None:
        commands.extend([
            f"set {{unsigned int}}0x{pdu:x} = 0x{address:x}",
            f"set {{unsigned short}}0x{pdu + 4:x} = 0x{length:x}",
        ])
        call(0xFEDCDF78, 0, pdu, length, available)
        call(0xFEDCDF96, 0, pdu, available)
        call(0xFEDCDFB2, 0, 0)
        call(0xFEDCE3EE, 0)

    def receive(data: bytes) -> None:
        commands.extend(
            f"set {{unsigned char}}0x{scratch + offset:x} = 0x{value:x}"
            for offset, value in enumerate(data)
        )
        receive_pointer(scratch, len(data))

    def confirm_response() -> None:
        call(0xFEDCDFE8, 0, 0)
        call(0xFEDCE3EE, 0)

    def request(data: bytes) -> None:
        receive(data)
        confirm_response()

    # The retained programming handoff flag is the bootloader's own entry
    # condition. The initializers consume it and establish session index 2.
    commands.append("set {unsigned char}0xfedd3209 = 1")
    call(0xFEDC7FD0)
    call(0xFEDC808C)
    request(b"\x10\x02")
    call(0xFEDCB440, 0)
    call(0xFEDCA5C8)

    request(b"\x27\x01" + bytes(16))
    call(0xFEDCBF68)
    call(0xFEDCA5C8)
    call(0xFEDC6D56, 0xFEDD3A58)
    call(0xFEDC6D8E, 0xFEDD3A58, 0xFEDD3A88, 0xFEDD3A68)
    commands.extend([
        f"set {{unsigned char}}0x{scratch:x} = 0x27",
        f"set {{unsigned char}}0x{scratch + 1:x} = 0x02",
    ])
    commands.extend(
        f"set {{unsigned char}}0x{scratch + 2 + offset:x} = "
        f"*(unsigned char *)0x{0xFEDD3A68 + offset:x}"
        for offset in range(16)
    )
    receive_pointer(scratch, 18)

    # Full boot RTOS startup needs unmodelled SFRs. This shim supplies only the
    # successful elapsed-time/resource read used by the transfer manager.
    commands.extend([
        "break *0xfedc1362",
        "commands 3", "silent",
        "set $r10 = 0", "set $pc = $r31", "continue", "end",
    ])
    request(b"\x2e\x02\x03" + bytes(5))
    request(b"\x2e\x02\x01" + bytes(16))
    request(b"\x2e\x02\x02" + bytes(16))
    receive_pointer(request_addresses["download"], len(requests["download"]))
    confirm_response()

    def transfer_block(name: str) -> None:
        receive_pointer(request_addresses[name], len(requests[name]))
        for _ in range(0x400 // 0x10):
            call(0xFEDC5EAC)
        call(0xFEDCD7EA)
        call(0xFEDD00CA)
        call(0xFEDCFDB4)
        call(0xFEDCD7EA)
        confirm_response()

    transfer_block("block1")
    transfer_block("block2")
    receive_pointer(request_addresses["exit"], len(requests["exit"]))
    confirm_response()

    receive_pointer(request_addresses["verify"], len(requests["verify"]))
    # 10F0 reads and CRC-checks the payload through 16-byte memory-manager
    # operations, then feeds the IV and plaintext through the same manager.
    for _ in range(140):
        call(0xFEDD00CA)
        call(0xFEDCFDB4)
        call(0xFEDC4F3E)
    call(0xFEDC663C)
    for _ in range(140):
        call(0xFEDC7A7A)
        call(0xFEDD00CA)
        call(0xFEDCFDB4)
    call(0xFEDC663C)
    call(0xFEDCC7A6)
    commands.extend([
        "if *(unsigned char *)0xfedd2bdc != 1 "
        "|| *(unsigned char *)0xfedd2bde != 1 "
        "|| *(unsigned char *)0xfedd2c3e != 0 "
        "|| *(unsigned char *)0xfedd3538 != 0",
        'printf "diagnostic authentication did not complete\\n"',
        "quit 1", "end",
        f"dump binary memory /out/diagnostic-plaintext.bin "
        f"0x{LOAD:x} 0x{LOAD + len(plaintext):x}",
    ])
    confirm_response()

    commands.extend([
        "set $frames = 0",
        "set {unsigned int}0xffcd0030 = 0x0808",
        "set {unsigned char}0xffed0008 = 0x11",
        "set {unsigned char}0xffed1008 = 0x22",
        "set {unsigned int}0xffd0008c = 0",
        "set {unsigned int}0xffd00028 = 0",
        f"set {{unsigned int}}0x{TMID:x} = 0x7c8",
        f"set {{unsigned int}}0x{TMPTR:x} = 0x80000000",
        f"set {{unsigned char}}0x{TMC:x} = 0",
        f"set {{unsigned char}}0x{TMSTS:x} = 0",
        f"break *0x{terminal:x}",
        "commands 4", "silent",
        f"break *0x{RESET:x}", "continue", "end",
        f"break *0x{submitted:x}",
        "commands 5", "silent",
        f"if *(unsigned int *)0x{TMID:x} != 0x7c8 "
        f"|| *(unsigned int *)0x{TMPTR:x} != 0x80000000 "
        f"|| *(unsigned char *)0x{TMC:x} != 1",
        'printf "invalid transmit registers\\n"', "quit 1", "end",
        "set $frames = $frames + 1",
        f'printf "METER_FRAME %08x %08x\\n", '
        f'*(unsigned int *)0x{DATA:x}, *(unsigned int *)0x{DATA + 4:x}',
        f"set {{unsigned char}}0x{TMC:x} = 0",
        f"set {{unsigned char}}0x{TMSTS:x} = 4",
        "continue", "end",
    ])
    receive_pointer(request_addresses["trigger"], len(requests["trigger"]))
    commands.extend([
        "if *(unsigned char *)0xfedd2c3e != 0x11 "
        "|| *(unsigned char *)0xfedd3538 != 0x11 "
        "|| *(unsigned char *)0xfedd3228 != 2",
        'printf "FF00 trigger was not accepted\\n"', "quit 1", "end",
    ])
    call(0xFEDCFDB4)
    commands.extend([
        "if *(unsigned char *)0xfedd3710 != 2 "
        "|| *(unsigned char *)0xfedd3712 != 0x11",
        'printf "FF00 payload execution was not armed\\n"', "quit 1", "end",
        f"set $r31 = 0x{RETURN_STOP:x}",
        "set $pc = 0xfedc77be",
        "continue",
    ])

    sim = work / "diagnostic-sim"
    output, _ = run_codeflash(
        root=ROOT, image_path=IMAGE, entry=0,
        ram_loads=(
            (request_base, request_path),
            *runtime_loads(work, image, boot),
        ),
        memory_regions=(
            "0xfeda0000,0x4000", "0xfedc0000,0x40000",
            "0xff200000,0x10000", "0xffc00000,0x400000",
        ),
        stop=f"0x{RESET:x}", gdb_commands=commands,
        assertions=("$pc == 0xad4", "$frames == 9", "$r6 == 0"),
        timeout=1200, output_dir=sim,
    )
    assert (sim / "diagnostic-plaintext.bin").read_bytes() == plaintext
    frames = [
        struct.pack("<II", int(first, 16), int(second, 16))
        for first, second in re.findall(
            r"^METER_FRAME ([0-9a-f]{8}) ([0-9a-f]{8})$", output, re.M
        )
    ]
    assert len(frames) == 9
    reassembler = CodeFlashReassembler(expected_base=0, expected_size=16)
    for frame in frames:
        reassembler.feed(frame)
    assert reassembler.complete, reassembler.protocol_errors()
    assert bytes(reassembler.image) == image[:16]
    (work / "diagnostic-frames.bin").write_bytes(b"".join(frames))
    (work / "diagnostic-report.json").write_text(json.dumps({
        "session": "programming",
        "security_level": 1,
        "upload_size": len(package),
        "trigger": requests["trigger"].hex(),
        "frames": len(frames),
        "dump_sha256": hashlib.sha256(reassembler.image).hexdigest(),
        "byte_identical": True,
        "transport_boundary": "PduR/DCM receive API and transmit confirmation",
        "os_boundary": "successful resource/timer read",
    }, indent=2) + "\n")
    print(
        "PASS diagnostic-session: upload, CRC/CMAC, FF00 and 16-byte dump "
        "completed through relocated firmware", flush=True,
    )


def run_case(
    name: str, *, start: int, length: int, mode: str = "complete",
    watchdog: str = "fixed", timeout: float = 120,
) -> dict[str, object]:
    work = ROOT / "build/out/rav4-meter-dumper-verification" / name
    work.mkdir(parents=True, exist_ok=True)
    (work / "report.json").unlink(missing_ok=True)
    payload = work / "payload.bin"
    spin_limit = 0x100 if mode in ("busy", "no_ack") else 0x01000000
    metadata = build(payload, start=start, length=length, spin_limit=spin_limit)
    plaintext_path = payload.with_suffix(".plaintext.bin")
    plaintext = plaintext_path.read_bytes()
    inspect_package(payload.read_bytes(), plaintext)
    image = IMAGE.read_bytes()
    syms = symbols(payload.with_suffix(".nm"))
    terminal = syms["terminal_reset"]
    assert LOAD <= terminal < LOAD + CRC_OFFSET
    disasm = payload.with_suffix(".disasm").read_text()
    reset_body = disasm.split("<_terminal_reset>:\n", 1)[1].split("\n\n", 1)[0]
    assert re.search(r"\bmovea\s+2772,", reset_body)
    assert re.search(r"\bjarl\s+\[r10\], lp", reset_body)
    watchdog_body = disasm.split("<_feed_watchdog>:\n", 1)[1].split("\n\n", 1)[0]
    assert "0xfedc1d7e" in watchdog_body
    stores = re.findall(
        r"^([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s+st\.b\s+(?!r0,)([^\n]+)",
        disasm, re.M,
    )
    assert len(stores) == 1, stores
    submitted = int(stores[0][0], 16) + len(stores[0][1].split())
    expected_reason = {
        "complete": 0, "busy": 1, "no_ack": 2, "abort": 3, "uninitialized": 4,
    }.get(mode)
    opbt0 = 0x4848 if watchdog == "variable" else 0x0808
    stop = RETURN_STOP if mode == "mode_rejected" else RESET
    commands = [
        f"set $r31 = 0x{RETURN_STOP:x}",
        "set $sp = 0xfedd7000", f"set $lp = 0x{RETURN_STOP:x}",
        f"set $r4 = 0x{GP:x}", f"set $r5 = 0x{TP:x}",
        f"set $r6 = {0 if mode == 'mode_rejected' else 1}",
        "set $frames = 0",
        f"set {{unsigned int}}0xffcd0030 = 0x{opbt0:x}",
        "set {unsigned char}0xffed0008 = 0x11",
        "set {unsigned char}0xffed1008 = 0x22",
        "set {unsigned int}0xffd0008c = 0",
        "set {unsigned int}0xffd00028 = 0",
        f"set {{unsigned int}}0x{TMID:x} = {0 if mode == 'uninitialized' else 0x7c8}",
        f"set {{unsigned int}}0x{TMPTR:x} = 0x80000000",
        f"set {{unsigned char}}0x{TMC:x} = {1 if mode == 'busy' else 0}",
        f"set {{unsigned char}}0x{TMSTS:x} = {8 if mode == 'busy' else 0}",
    ]
    if mode == "mode_rejected":
        commands.append(f"break *0x{stop:x}")
    else:
        commands += [
            f"break *0x{terminal:x}", "commands 1", "silent",
            f"break *0x{RESET:x}", "continue", "end",
        ]
    if mode != "mode_rejected":
        commands += [
            f"break *0x{submitted:x}",
            "commands 2", "silent",
            f'if *(unsigned int *)0x{TMID:x} != 0x7c8 || '
            f'*(unsigned int *)0x{TMPTR:x} != 0x80000000 || '
            f'*(unsigned char *)0x{TMC:x} != 1',
            'printf "invalid transmit registers\\n"', "quit 1", "end",
            'set $frames = $frames + 1',
            f'printf "METER_FRAME %08x %08x\\n", '
            f'*(unsigned int *)0x{DATA:x}, *(unsigned int *)0x{DATA + 4:x}',
        ]
        if mode in ("complete", "abort"):
            commands += [
                f"set {{unsigned char}}0x{TMC:x} = 0",
                f"set {{unsigned char}}0x{TMSTS:x} = {4 if mode == 'complete' else 2}",
            ]
        commands += ["continue", "end"]
    commands += ["continue"]
    count = (
        4 + length // 4 + (length // 4) // 4096 + 1
        if mode == "complete"
        else 0 if mode in ("busy", "uninitialized", "mode_rejected") else 1
    )
    assertions = [f"$frames == {count}"]
    if mode == "mode_rejected":
        assertions.append("$r10 == 1")
    else:
        assertions.append(f"$r6 == {expected_reason}")
        assertions.extend((
            "*(unsigned char *)0xffed000c == 0x5f",
            "*(unsigned char *)0xffed100c == 0x5f",
        ))
        if watchdog == "variable":
            assertions.extend((
                "*(unsigned char *)0xffed0004 == 0x9b",
                "*(unsigned char *)0xffed1004 == 0x8a",
            ))
        else:
            assertions.extend((
                "*(unsigned char *)0xffed0000 == 0xac",
                "*(unsigned char *)0xffed1000 == 0xac",
            ))
    output, _ = run_codeflash(
        root=ROOT, image_path=IMAGE, entry=LOAD,
        ram_loads=((LOAD, plaintext_path), *runtime_loads(work, image)),
        memory_regions=(
            "0xfedc0000,0x40000", "0xffcd0000,0x1000",
            "0xffd00000,0x2000", "0xffed0000,0x2000",
        ),
        stop=f"0x{stop:x}", gdb_commands=commands, assertions=tuple(assertions),
        timeout=timeout, output_dir=work / "sim",
    )
    frames = [
        struct.pack("<II", int(a, 16), int(b, 16))
        for a, b in re.findall(
            r"^METER_FRAME ([0-9a-f]{8}) ([0-9a-f]{8})$", output, re.M
        )
    ]
    assert len(frames) == count
    (work / "frames.bin").write_bytes(b"".join(frames))
    result: dict[str, object] = {
        "case": name, "mode": mode, "start": start, "length": length,
        "frames": len(frames), "terminal_reason": expected_reason,
        "rom_sha256": IMAGE_SHA256,
        "payload_sha256": hashlib.sha256(payload.read_bytes()).hexdigest(),
        "plaintext_sha256": hashlib.sha256(plaintext).hexdigest(),
        "model": (
            "GNU RH850 CPU with exact relocated watchdog code and "
            "GDB-supplied RSCAN completion"
        ),
        "termination": (
            "stock software-reset entry reached before simulator-side reset effects"
        ),
        "watchdog": watchdog, "build": metadata,
    }
    if mode == "complete":
        reassembler = CodeFlashReassembler(expected_base=start, expected_size=length)
        for frame in frames:
            reassembler.feed(frame)
        expected = image[start:start + length]
        assert reassembler.complete, reassembler.protocol_errors()
        assert bytes(reassembler.image) == expected
        result["reassembled_sha256"] = hashlib.sha256(reassembler.image).hexdigest()
        result["byte_identical"] = True
    (work / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"PASS {name}: {len(frames)} native payload frames, "
        f"terminal reason {expected_reason}", flush=True,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="also execute/reassemble all 2 MiB")
    args = parser.parse_args()
    image = IMAGE.read_bytes()
    boot = BOOT_IMAGE.read_bytes()
    assert len(image) == 0x200000
    assert len(boot) == 0x8000
    assert hashlib.sha256(image).hexdigest() == IMAGE_SHA256
    assert hashlib.sha256(boot).hexdigest() == BOOT_SHA256
    package_work = ROOT / "build/out/rav4-meter-dumper-verification/authenticated-package"
    package_work.mkdir(parents=True, exist_ok=True)
    package = package_work / "payload.bin"
    build(package, start=0, length=16)
    verify_package_with_firmware(package_work, package, image)
    verify_diagnostic_path(
        ROOT / "build/out/rav4-meter-dumper-verification/diagnostic-session",
        package, image, boot,
    )
    # Both address zero and the physical final word must be executed reads.
    run_case("first-words", start=0, length=16)
    run_case("last-words", start=0x1ffff0, length=16)
    run_case("progress-boundary", start=0, length=0x4004)
    run_case("variable-watchdog", start=0, length=4, watchdog="variable")
    run_case("mode-rejected", start=0, length=4, mode="mode_rejected")
    for mode in ("busy", "no_ack", "abort", "uninitialized"):
        run_case(mode, start=0, length=4, mode=mode)
    if args.full:
        run_case("full-codeflash", start=0, length=0x200000, timeout=900)


if __name__ == "__main__":
    main()
