#!/usr/bin/env python3
"""Verify the pinned Renesas RFP/RV40F external-source analysis.

With no local package this suite still validates the committed lock, command
model, and wire fixtures. ``--require-package`` additionally requires and
verifies the package artifacts, resource inventory, Mach-O symbol table,
embedded data, and exact analyzed function bodies.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOCK_PATH = REPO / "software/locks/renesas-rfp.json"
COMMANDS_PATH = REPO / "data" / "renesas_rfp_rv40f_commands.csv"
CAPABILITIES_PATH = REPO / "data" / "renesas_rfp_rv40f_capabilities.csv"

LC_SEGMENT_64 = 0x19
LC_SYMTAB = 0x2
MH_MAGIC_64 = 0xFEEDFACF

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def request_frame(command: int, payload: bytes = b"") -> bytes:
    """Build the RV40F host request framing recovered from ProcessCommand."""

    body_length = len(payload) + 1
    length = body_length.to_bytes(2, "big")
    checksum = (-sum(length + bytes([command]) + payload)) & 0xFF
    return b"\x01" + length + bytes([command]) + payload + bytes([checksum, 0x03])


def parse_macho(data: bytes) -> tuple[int, dict[str, list[int]], list[tuple[int, int, int]]]:
    """Return CPU type, symbol values, and file-backed segment mappings."""

    if len(data) < 32:
        raise ValueError("file is too small for a Mach-O 64 header")
    magic, cpu_type, _, _, ncmds, _, _, _ = struct.unpack_from("<IiiIIIII", data, 0)
    if magic != MH_MAGIC_64:
        raise ValueError(f"unexpected Mach-O magic {magic:#x}")

    commands_offset = 32
    symtab: tuple[int, int, int, int] | None = None
    segments: list[tuple[int, int, int]] = []
    for _ in range(ncmds):
        command, command_size = struct.unpack_from("<II", data, commands_offset)
        if command_size < 8:
            raise ValueError("invalid Mach-O load-command size")
        if command == LC_SEGMENT_64:
            (
                _,
                _,
                _,
                vmaddr,
                _,
                file_offset,
                file_size,
                _,
                _,
                _,
                _,
            ) = struct.unpack_from("<II16sQQQQiiII", data, commands_offset)
            segments.append((vmaddr, file_offset, file_size))
        elif command == LC_SYMTAB:
            _, _, symbol_offset, symbol_count, string_offset, string_size = struct.unpack_from(
                "<IIIIII", data, commands_offset
            )
            symtab = (symbol_offset, symbol_count, string_offset, string_size)
        commands_offset += command_size

    if symtab is None:
        raise ValueError("Mach-O has no LC_SYMTAB")
    symbol_offset, symbol_count, string_offset, string_size = symtab
    strings = data[string_offset : string_offset + string_size]
    symbols: dict[str, list[int]] = {}
    for index in range(symbol_count):
        entry = symbol_offset + index * 16
        string_index, _, _, _, value = struct.unpack_from("<IBBHQ", data, entry)
        if string_index == 0 or string_index >= len(strings):
            continue
        end = strings.find(b"\0", string_index)
        if end < 0:
            continue
        name = strings[string_index:end].decode("utf-8", errors="replace")
        symbols.setdefault(name, []).append(value)
    return cpu_type, symbols, segments


def address_to_file_offset(address: int, segments: list[tuple[int, int, int]]) -> int:
    for vmaddr, file_offset, file_size in segments:
        if vmaddr <= address < vmaddr + file_size:
            return file_offset + address - vmaddr
    raise ValueError(f"address {address:#x} has no file-backed segment")


def verify_committed_model(lock: dict[str, object]) -> None:
    print("== complete committed RFP command model ==")
    with COMMANDS_PATH.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    with CAPABILITIES_PATH.open(newline="", encoding="utf-8") as stream:
        capabilities = list(csv.DictReader(stream))

    commands = {row["command"]: row for row in rows}
    expected_commands = {
        "0x00", "0x10", "0x12", "0x13", "0x14", "0x15", "0x16", "0x18", "0x1C",
        "0x20", "0x21", "0x22", "0x23", "0x26", "0x27", "0x28", "0x29", "0x2A",
        "0x2B", "0x2C", "0x2D", "0x2E", "0x30", "0x32", "0x34", "0x36", "0x38",
        "0x3A", "0x3C", "0x48", "0x49", "0x4A", "0x4B", "0x4D", "0x4E", "0x4F",
        "0x50", "0x51", "0x52", "0x53", "0x54", "0x56", "0x57", "0x6E", "0x6F",
        "0x70", "0x71", "0x74", "0x75", "0x78", "0x79", "0x7A",
    }
    check("52 distinct RV40F command rows", len(rows) == 52)
    check("complete recovered command-ID census", set(commands) == expected_commands)
    check("every command has a host method", all(row["host_methods"] for row in rows))
    check("every command records request and response layouts",
          all(row["request_layout"] and row["response_layout"] for row in rows))
    check("every command records task/precondition/result evidence",
          all(row["calling_tasks"] and row["capability_or_preconditions"] and row["result_handling"] for row in rows))
    check("command confidence is verified/recovered only",
          all(row["confidence"] in {"verified", "recovered"} for row in rows))

    print("\n== security/configuration negative boundary ==")
    security_config_ids = {
        "0x20", "0x21", "0x22", "0x23", "0x26", "0x27", "0x28", "0x29", "0x2A",
        "0x2B", "0x2C", "0x2D", "0x2E", "0x30", "0x48", "0x49", "0x4A", "0x4B",
        "0x4E", "0x4F", "0x56", "0x57", "0x6E", "0x6F", "0x70", "0x71", "0x74",
        "0x75", "0x78", "0x79", "0x7A",
    }
    check("all security/configuration commands are represented",
          security_config_ids <= set(commands))
    check("no security/configuration command has a fixed 64-byte request",
          not any(commands[c]["request_payload_length"] == "64" for c in security_config_ids))
    check("CheckPassword is selector + 32 + 32, not SHE M1/M2/M3",
          commands["0x78"]["request_payload_length"] == "65"
          and commands["0x78"]["request_layout"] == "selector_u8 || valueA[32] || valueB[32]")
    check("WriteConfig is address/config + 16 bytes, not a dedicated key-load primitive",
          commands["0x79"]["request_payload_length"] == "20"
          and commands["0x79"]["request_layout"] == "config_or_address_be32 || data[16]")
    check("legacy SetICUM is split 4 + 15 bytes",
          commands["0x75"]["request_payload_length"] == "4"
          and commands["0x74"]["request_payload_length"] == "15")

    print("\n== capability-word model ==")
    cap = {row["key"]: row for row in capabilities}
    check("capability table covers 0x1001..0x1212 recovered keys", len(capabilities) == 22)
    check("0x1106 is a bits48..50 predicate",
          cap["0x1106"]["normal_8byte_typecode_projection"] == "bits48..50 in {1,4}")
    check("0x1109 is bit51", cap["0x1109"]["normal_8byte_typecode_projection"] == "bit51")
    check("0x1205 recovers the legacy 20-byte option width",
          "20 if bits48..50==2" in cap["0x1205"]["normal_8byte_typecode_projection"])
    check("phase2 low-byte 0x30 promotes only 0x1108 in 0x110x family",
          cap["0x1108"]["phase2_low_byte_0x30"] == "phase2: 1"
          and all(cap[key]["phase2_low_byte_0x30"] == "phase2: 0"
                  for key in ("0x1101", "0x1102", "0x1103", "0x1104", "0x1105", "0x1106", "0x1107", "0x1109", "0x110A")))

    print("\n== recovered RV40F wire fixtures ==")
    check("ValidateICU_S frame", request_frame(0x70).hex() == "010001708f03")
    check("CheckICUMode FF probe", request_frame(0x71, b"\xff").hex() == "01000271ff8e03")
    check("CheckICUMode 00 fallback", request_frame(0x71, b"\x00").hex() == "01000271008d03")
    check(
        "SetICUSOptionByte fixture",
        request_frame(0x6E, bytes.fromhex("11223344")).hex() == "0100056e11223344e303",
    )
    check(
        "SetICUM auxiliary fixture",
        request_frame(0x75, bytes.fromhex("01020304")).hex() == "01000575010203047c03",
    )
    check("CheckPassword fixture has 65-byte payload",
          len(request_frame(0x78, bytes(65))) == 71)

    package = lock["package"]
    scope = lock["analysis_scope"]
    check("lock schema version", lock["schema_version"] == 2)
    check("lock records 52-command scope", scope["bootrv40f_command_count"] == 52)
    check("lock records 61-symbol BootRV40F surface", scope["bootrv40f_symbol_count"] == 61)
    check("pinned RFP package version", package["package_version"] == "V3.24.00")
    check("pinned package platform", package["platform"] == "macos-arm64")
    report = (REPO / "docs/tooling/renesas-rfp-rv40f.md").read_text(encoding="utf-8")
    open_questions = (REPO / "docs/status/OPEN_QUESTIONS.md").read_text(encoding="utf-8")
    check("P1M-E all-FF ID remains explicitly hypothesis-grade",
          "reasonable **probe hypothesis**" in report
          and "no specific P1M-E device record" in report
          and "**only as a target-transfer hypothesis**" in open_questions)


def verify_package(root: Path, lock: dict[str, object]) -> None:
    print("\n== pinned local RFP artifacts ==")
    artifacts = lock["artifacts"]
    for relative, metadata in artifacts.items():
        path = root / relative
        check(f"{relative} exists", path.is_file(), str(path))
        if not path.is_file():
            continue
        data = path.read_bytes()
        check(f"{relative} size", len(data) == metadata["size"], str(len(data)))
        digest = sha256_bytes(data)
        check(f"{relative} SHA-256", digest == metadata["sha256"], digest)

    library_path = root / "libRFP.dylib"
    devices_path = root / "Devices.xml"
    cli_docs_path = root / "docs/rfp-cli.md"
    if not library_path.is_file() or not devices_path.is_file():
        return

    library = library_path.read_bytes()
    if cli_docs_path.is_file():
        cli_docs = cli_docs_path.read_text(encoding="utf-8", errors="replace")
        check("shipped CLI has a generic all-FF ID-code example",
              "-auth id FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" in cli_docs)
    check("library retains generic UserID=0xFFFFFFFF configuration strings",
          b"E01_RFP.ncd;UserID=0xFFFFFFFF" in library
          and b"E20_RFP.ncd;UserID=0xFFFFFFFF" in library)

    print("\n== Mach-O symbols and analyzed function bodies ==")
    try:
        cpu_type, symbols, segments = parse_macho(library)
    except (ValueError, struct.error) as error:
        check("parse libRFP Mach-O", False, str(error))
        return
    check("libRFP CPU type is pinned arm64", cpu_type == lock["macho"]["cpu_type"], hex(cpu_type))

    functions = lock["macho"]["functions"]
    for symbol, metadata in functions.items():
        addresses = symbols.get(symbol, [])
        check(f"{symbol} symbol exists", bool(addresses))
        if not addresses:
            continue
        address = metadata["address"]
        check(
            f"{symbol} address",
            address in addresses,
            ", ".join(hex(candidate) for candidate in addresses),
        )
        if address not in addresses:
            continue
        try:
            offset = address_to_file_offset(address, segments)
        except ValueError as error:
            check(f"{symbol} file mapping", False, str(error))
            continue
        body = library[offset : offset + metadata["size"]]
        check(
            f"{symbol} body SHA-256",
            sha256_bytes(body) == metadata["sha256"],
            sha256_bytes(body),
        )

    print("\n== embedded firmware/resource triage ==")
    for symbol, metadata in lock["macho"]["embedded_data"].items():
        addresses = symbols.get(symbol, [])
        check(f"{symbol} symbol exists", bool(addresses))
        if not addresses:
            continue
        address = metadata["address"]
        check(
            f"{symbol} address",
            address in addresses,
            ", ".join(hex(candidate) for candidate in addresses),
        )
        if address not in addresses:
            continue
        try:
            offset = address_to_file_offset(address, segments)
        except ValueError as error:
            check(f"{symbol} file mapping", False, str(error))
            continue
        prefix = bytes.fromhex(metadata["prefix_hex"])
        check(f"{symbol} byte prefix", library[offset : offset + len(prefix)] == prefix)

    firmware_dir = root / "Firmwares"
    firmware_files = sorted(firmware_dir.glob("*.bin"))
    check("68 shipped probe-firmware images", len(firmware_files) == 68, str(len(firmware_files)))
    probe_markers = (b"J-Link", b"J-Trace", b"Flasher")
    check(
        "every Firmwares image identifies as SEGGER probe firmware",
        all(
            b"SEGGER" in (data := path.read_bytes())
            and any(marker in data for marker in probe_markers)
            for path in firmware_files
        ),
    )

    resources_dir = root / "Resources"
    resource_files = sorted(path for path in resources_dir.rglob("*") if path.is_file())
    check("31 explicit target-resource files", len(resource_files) == 31, str(len(resource_files)))
    resource_names = [str(path.relative_to(resources_dir)).lower() for path in resource_files]
    check(
        "no explicit RH850/P1M/ICU target resource",
        not any(
            token in relative
            for relative in resource_names
            for token in ("rh850", "rv40f", "p1m", "icus")
        ),
    )
    provisioning = resources_dir / "ProvisioningSW" / "RA6B1" / "provsw_sec_enc.bin"
    provisioning_files = sorted(
        path for path in (resources_dir / "ProvisioningSW").rglob("*") if path.is_file()
    )
    check(
        "only explicit provisioning payload is RA6B1",
        provisioning_files == [provisioning],
    )
    if provisioning.is_file():
        check("RA6B1 provisioning image has imag header", provisioning.read_bytes()[:4] == b"imag")

    rv40f_symbols = [name for name in symbols if "BootRV40F" in name]
    gen2_symbols = [name for name in symbols if "BootRH850Gen2" in name]
    check("complete BootRV40F symbol census", len(rv40f_symbols) == 61, str(len(rv40f_symbols)))
    check("separate BootRH850Gen2 API retained", len(gen2_symbols) >= 10, str(len(gen2_symbols)))
    forbidden_names = ("setkey", "loadkey", "keyupdate", "provisionkey")
    check(
        "no named BootRV40F key-loading API",
        not any(token in name.lower() for name in rv40f_symbols for token in forbidden_names),
    )
    check(
        "no BootRV40F provisioning-image downloader",
        not any("Provision" in name or "DownloadImage" in name for name in rv40f_symbols),
    )

    print("\n== device-family routing metadata ==")
    devices = devices_path.read_text(encoding="utf-8-sig")
    check("generic RH850 device entry", "<Name>RH850</Name>" in devices)
    check("generic RH850 uses default mode entry", "<Entry>MODEENTRY_DEFAULT</Entry>" in devices)
    check("RH850/E2x entry is separate", "<DisplayName>RH850/E2x</DisplayName>" in devices)
    check("RH850/U2x entry is separate", "<DisplayName>RH850/U2x</DisplayName>" in devices)

    cli_doc = (root / "docs" / "rfp-cli.md").read_text(encoding="utf-8")
    check("CLI documents ICU-S enable flag", "|icus|Enable ICU-S|" in cli_doc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=Path)
    parser.add_argument("--require-package", action="store_true")
    args = parser.parse_args()

    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    verify_committed_model(lock)

    default_root = REPO / lock["package"]["default_path"]
    root = (args.package_dir or default_root).expanduser().resolve()
    if root.is_dir():
        verify_package(root, lock)
    elif args.require_package:
        check("local RFP package exists", False, str(root))
    else:
        print(f"\n[SKIP] licensed local RFP package not present: {root}")
        print("       Run `make verify-rfp` to require the pinned package checks.")

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
