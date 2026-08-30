#!/usr/bin/env python3
"""Verify per-target RAM-exec geometry without cross-variant inheritance."""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.common import ram_exec
from exploit.common.payload_package import inspect_payload, package_shellcode

passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


obj = json.loads((ROOT / "data/variant_ram_exec_requirements.json").read_text())
rows = {row["id"]: row for row in obj["variants"]}
sienna = rows["sienna-8965b4512000"]
camry = rows["camry-2026-8965f3307000-high-tail"]
newer = rows["yc-newer-toyota-field-report-2026-08-16"]

print("== evidence boundary ==")
check("metadata schema is pinned", obj["schema"] == "toyota-eps-ram-exec-variant-requirements-v1")
check("Sienna download base remains verified FEBF0000", sienna["authenticated_download_base"] == "0xFEBF0000")
check("executable bootstrap default remains Sienna FEBF0000", ram_exec.RAM_LOAD_ADDR == 0xFEBF0000)
check(
    "Sienna authenticated window remains 4 KiB",
    ram_exec.RAM_LOAD_SIZE == 0x1000 and sienna["authenticated_download_size"] == "0x1000",
)
check(
    "Camry high-tail is exact-target live-verified geometry",
    camry["evidence"] == "dynamic-probe-verified"
    and camry["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
    and camry["retained_application_rwx_base"] == "0xFEBFF9F0"
    and camry["retained_application_rwx_end_exclusive"] == "0xFEBFFBFC"
    and camry["retained_application_rwx_size"] == "0x20C"
    and camry["shellcode_link_vma"] == "0xFEBFF9F0",
)
check(
    "Camry boot staging is distinct from retained high-tail VMA",
    camry["authenticated_download_base"] == "0xFEBF0000"
    and camry["payload_callback_cell"] == "0xFEBF0FD0"
    and camry["authenticated_download_base"] != camry["retained_application_rwx_base"],
)
check(
    "Camry command5 anchors are exact but production mailbox remains intentionally unassigned",
    camry["command5_dispatch_address"] == "0x89440"
    and camry["command5_driver_record"] == 0
    and camry["command5_key_selector"] == 4
    and camry["command5_done_flag"] == "0xFEBF13BC"
    and camry["command5_status_flag"] == "0xFEBF13BD"
    and camry["command5_mailbox_address"] is None,
)
check(
    "newer-target FEBE0000 is explicitly external evidence",
    newer["evidence"] == "external-source-observed" and newer["shellcode_link_vma"] == "0xFEBE0000",
)
check(
    "newer-target field report does not assert boot download base",
    newer["authenticated_download_base"] is None and newer["payload_callback_base"] is None,
)
check(
    "newer-target metadata cannot silently override Sienna bootstrap",
    newer["shellcode_link_vma"] != sienna["authenticated_download_base"],
)

print("\n== explicit geometry hook ==")
default_geometry = ram_exec.SIENNA_RAM_EXEC_GEOMETRY
check(
    "default geometry is evidence-labelled Sienna FEBF0000",
    default_geometry.load_addr == 0xFEBF0000
    and default_geometry.load_size == 0x1000
    and "sienna" in default_geometry.evidence,
)
external_geometry = ram_exec.explicit_ram_exec_geometry(
    load_addr=0xFEBE0000,
    evidence="external-source:yc-2026-08-16-link-vma",
)
check(
    "explicit external geometry can move the 4 KiB package without changing defaults",
    external_geometry.load_addr == 0xFEBE0000
    and external_geometry.load_size == 0x1000
    and ram_exec.SIENNA_RAM_EXEC_GEOMETRY.load_addr == 0xFEBF0000,
)
try:
    ram_exec.explicit_ram_exec_geometry(load_addr=0xFEBE0000, evidence="")
except ram_exec.RamExecError as exc:
    check("non-default geometry requires evidence provenance", "evidence" in str(exc).lower(), str(exc))
else:
    check("non-default geometry requires evidence provenance", False)

secret = bytes(range(16))
relocated_payload = package_shellcode(
    b"\x00" * 0x20,
    secret=secret,
    payload_load_addr=external_geometry.load_addr,
)
inspection = inspect_payload(relocated_payload, secret=secret)
check(
    "authenticated package callback and CRC descriptor follow explicit load address",
    inspection.callback_address == 0xFEBE0000
    and inspection.descriptor_address == 0xFEBE0000
    and inspection.descriptor_length == 0xFF0
    and inspection.cmac_valid
    and inspection.crc_residue == 0xFFFFFFFF,
)

print("\n== UDS upload/verify uses the same explicit geometry ==")
class FakeUds:
    def __init__(self) -> None:
        self.writes: list[tuple[int, bytes]] = []
        self.requests: list[tuple[int, bytes]] = []
        self.transfers: list[tuple[int, bytes]] = []
        self.routines: list[tuple[int, int, bytes]] = []
        self.exited = False

    def write_data_by_identifier(self, did: int, data: bytes) -> None:
        self.writes.append((did, data))

    def _uds_request(self, service: int, *, data: bytes) -> None:
        self.requests.append((service, data))

    def transfer_data(self, block: int, data: bytes) -> None:
        self.transfers.append((block, data))

    def request_transfer_exit(self) -> None:
        self.exited = True

    def routine_control(self, control_type: int, rid: int, data: bytes) -> None:
        self.routines.append((control_type, rid, data))


fake_uds = FakeUds()
fake_mod = SimpleNamespace(
    SERVICE_TYPE=SimpleNamespace(REQUEST_DOWNLOAD=0x34),
    ROUTINE_CONTROL_TYPE=SimpleNamespace(START=1),
)
route = ram_exec.explicit_route(bus=1, elm327_param=1, uds_variant="old")
isotp_rows: list[tuple[bytes, int, int]] = []
original_isotp = ram_exec._import_isotp_send
ram_exec._import_isotp_send = lambda: (
    lambda _panda, data, addr, *, bus: isotp_rows.append((bytes(data), int(addr), int(bus)))
)
class FakePanda:
    def __init__(self) -> None:
        self.clears: list[int] = []

    def can_clear(self, bus: int) -> None:
        self.clears.append(int(bus))


fake_panda = FakePanda()
try:
    ram_exec._upload_and_trigger(
        fake_panda,
        fake_uds,
        fake_mod,
        route,
        b"\x00" * 0x1000,
        geometry=external_geometry,
    )
finally:
    ram_exec._import_isotp_send = original_isotp

expected_download_tail = struct.pack("!II", 0xFEBE0000, 0x1000)
check(
    "RequestDownload carries explicit FEBE0000 geometry",
    len(fake_uds.requests) == 1
    and fake_uds.requests[0][0] == 0x34
    and fake_uds.requests[0][1].endswith(expected_download_tail),
    repr(fake_uds.requests),
)
check("FF00 bootstrap clears Panda host RX backlog", fake_panda.clears == [0xFFFF], repr(fake_panda.clears))
check(
    "0x10F0 verification covers the same explicit geometry",
    len(fake_uds.routines) == 1
    and fake_uds.routines[0][1] == 0x10F0
    and fake_uds.routines[0][2] == b"\x45\x00" + expected_download_tail,
    repr(fake_uds.routines),
)
check(
    "4 KiB upload still uses four 0x400 TransferData chunks",
    [block for block, _ in fake_uds.transfers] == [1, 2, 3, 4]
    and all(len(data) == 0x400 for _, data in fake_uds.transfers)
    and fake_uds.exited,
)
check(
    "FF00 trigger remains separate from RAM window geometry",
    len(isotp_rows) == 1
    and isotp_rows[0][1:] == (ram_exec.TX_ADDR, 1)
    and isotp_rows[0][0].startswith(b"\x31\x01\xFF\x00\x45\x00"),
)

print("\n== host safety/timeout contract ==")
source = (ROOT / "exploit/common/ram_exec.py").read_text().lower()
deploy_source = (ROOT / "exploit/patcher/deploy.py").read_text().lower()
build_source = (ROOT / "exploit/patcher/build_payload.py").read_text().lower()
check("RAM-exec implementation retains 120s caller-configurable timeout", "timeout: float = 120.0" in source)
check("RAM-exec UDS client handles response-pending separately", "response_pending_timeout=1.0" in source)
check("RAM-exec host guard covers both modern pandad and legacy boardd", "selfdrive\\.pandad\\.pandad" in source and '"pidof", "pandad"' in source and '"pidof", "boardd"' in source)

original_run = ram_exec.subprocess.run
seen_process_checks = []
class _Proc:
    def __init__(self, returncode=1, stdout=""):
        self.returncode = returncode
        self.stdout = stdout

def _fake_pandad_running(argv, **kwargs):
    seen_process_checks.append(tuple(argv))
    if argv[:2] == ["pgrep", "-f"]:
        return _Proc(0, "1234\n")
    return _Proc()

ram_exec.subprocess.run = _fake_pandad_running
try:
    ram_exec.ensure_boardd_stopped()
except ram_exec.RamExecError as exc:
    pandad_blocked = "boardd/pandad is running" in str(exc)
else:
    pandad_blocked = False
finally:
    ram_exec.subprocess.run = original_run
check("modern pandad ownership blocks direct Panda access", pandad_blocked and seen_process_checks == [("pgrep", "-f", r"selfdrive\.pandad\.pandad")])

seen_process_checks = []
def _fake_no_owner(argv, **kwargs):
    seen_process_checks.append(tuple(argv))
    return _Proc()

ram_exec.subprocess.run = _fake_no_owner
try:
    ram_exec.ensure_boardd_stopped()
    no_owner_allowed = True
except ram_exec.RamExecError:
    no_owner_allowed = False
finally:
    ram_exec.subprocess.run = original_run
check("host guard allows direct access only after checking all known owners", no_owner_allowed and seen_process_checks == [("pgrep", "-f", r"selfdrive\.pandad\.pandad"), ("pidof", "pandad"), ("pidof", "boardd")])
check("deployer exposes explicit RAM-load hook", "--ram-load-addr" in deploy_source)
check(
    "deployer requires provenance for non-default RAM geometry",
    "--ram-geometry-evidence" in deploy_source and "non-default --ram-load-addr requires" in deploy_source,
)
check("offline payload builder exposes matching RAM-load hook", "--ram-load-addr" in build_source)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
