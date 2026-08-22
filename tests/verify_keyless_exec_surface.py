#!/usr/bin/env python3
"""Verify the bounded keyless-execution surface across tracked EPS dumps.

FINDINGS coverage:
- KEYLESS-001: the three tracked security roots are byte-identical/co-located.
- KEYLESS-002: the 20-record boot UDS table and every unique referenced handler
  body transfer exactly to H/Span at -0x1C; critical SA/payload workers do too.
- KEYLESS-003: RequestDownload remains SecurityAccess-gated and its interval
  checker also contains the unsigned wrap guard in every tracked image.
- KEYLESS-004: the application's exact packed 0x7F7/0x7F8 XCP route descriptor
  is absent from every tracked boot region. This test intentionally does not
  promote descriptor absence into a universal "boot has no XCP" proof.
- KEYLESS-005: Sienna's canonical boot graph has only the known zero-trip WRITE
  into the XCP window; the startup shape and security-relevant boot bodies
  transfer exactly to H/Span, while recovered auth state remains below the
  window.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

SIENNA = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
ALBINO = (
    REPO / "community/albinoelephant/raw-20260818/"
    "albinoelephant-corolla-2023.20260814-0023/"
    "dump_codeflash_00000000_00200000_20260814-025814.bin"
).read_bytes()
SPAN = (
    REPO / "community/spanconstant/raw-20260821/"
    "span-corolla-2025.20260821-1511/"
    "dump_codeflash_00000000_00200000_20260821-152033.bin"
).read_bytes()

IMAGES = {
    "sienna-8965B4512000": SIENNA,
    "albinoelephant-8965H1202000": ALBINO,
    "spanconstant-8965F1208000": SPAN,
}
FOREIGN = {
    "albinoelephant-8965H1202000": ALBINO,
    "spanconstant-8965F1208000": SPAN,
}

PAYLOAD_BUILD_SECRET = bytes.fromhex("ba052435f8843f985fd1329d2b6117b0")
BOOT_SA_SECRET = bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044")
APP_SA_SECRET = bytes.fromhex("893e08418c741ffa2a9c044bffa55813")

BOOT_UDS_TABLE = {"sienna": 0x8E54, "corolla": 0x8E34}
UDS_RECORD_COUNT = 20
COROLLA_SHIFT = -0x1C
EXPECTED_SIDS = [
    0x10, 0x11, 0x27, 0x28, 0x3E, 0x85, 0x22, 0x23, 0x2C, 0x2E,
    0x14, 0x19, 0x2F, 0x31, 0x34, 0x36, 0x37, 0xAB, 0xBA, 0xBB,
]
EXPECTED_POLICIES = [
    3, 2, 2, 1, 1, 1, 2, 3, 3, 2,
    2, 3, 3, 2, 2, 2, 2, 3, 3, 3,
]

# Unique handlers referenced by the 20-record Sienna table. Body sizes are the
# complete contiguous canonical function extents, independently checked below
# against raw CodeFlash at the exact Corolla relocation.
UDS_HANDLER_BODIES = [
    ("uds_diagnostic_session_control", 0x614A, 186),
    ("uds_ecu_reset", 0x60C2, 114),
    ("uds_security_access", 0x5516, 110),
    ("uds_communication_control", 0x688A, 112),
    ("uds_tester_present", 0x4FF8, 104),
    ("uds_control_dtc_setting", 0x693A, 96),
    ("uds_read_data_by_identifier", 0x5FB8, 70),
    ("uds_unsupported_service_handler", 0x69B0, 34),
    ("uds_write_data_by_identifier", 0x4948, 328),
    ("uds_routine_control", 0x567E, 696),
    ("uds_request_download", 0x5D68, 468),
    ("uds_transfer_data", 0x4DBA, 56),
    ("uds_request_transfer_exit", 0x5C92, 152),
]

# Helpers/workers needed for the security-state and payload-gate transfer claim.
CRITICAL_BOOT_BODIES = [
    ("uds_security_access_request_seed", 0x5328, 202),
    ("uds_security_access_send_key", 0x53F2, 12),
    ("routine_verify_crc_cmac_task", 0x5936, 206),
    ("payload_decrypt_enqueue", 0x6BB4, 30),
    ("payload_decrypt_transfer_task", 0x6BDE, 116),
]

XCP_ROUTE_IDS = (0x7F7, 0x7F8)
XCP_DESCRIPTOR_ATTR = 2
XCP_DESCRIPTOR_TAG = 0x80000000
XCP_WINDOW = (0xFEBF7C00, 0xFEBFFBFF)
BOOT_GP = 0xFEBF9800
SECURITY_STATE = {
    "boot SecurityAccess state": 0xFEBF2B0F,
    "payload authorization bitfield": 0xFEBF2B11,
    "SA seed buffer": 0xFEBF2B24,
    "SA key/data buffer": 0xFEBF2B34,
    "SA handshake state": 0xFEBF2B55,
    "payload decrypt queue/busy flag": 0xFEBF2BDE,
}

passed = 0
failed = 0


def check(name: str, ok: bool) -> None:
    global passed, failed
    if ok:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}")


def find_all(image: bytes, needle: bytes) -> list[int]:
    offs: list[int] = []
    start = 0
    while True:
        i = image.find(needle, start)
        if i < 0:
            return offs
        offs.append(i)
        start = i + 1


def uds_table(image: bytes, base: int) -> list[bytes]:
    raw = image[base : base + UDS_RECORD_COUNT * 8]
    if len(raw) != UDS_RECORD_COUNT * 8:
        return []
    return [raw[i * 8 : (i + 1) * 8] for i in range(UDS_RECORD_COUNT)]


def shift_record(rec: bytes, delta: int) -> bytes:
    (handler,) = struct.unpack_from("<H", rec, 4)
    return rec[:4] + struct.pack("<H", (handler + delta) & 0xFFFF) + rec[6:]


def exact_shifted_body(image: bytes, sienna_entry: int, size: int) -> bool:
    target = sienna_entry + COROLLA_SHIFT
    return SIENNA[sienna_entry : sienna_entry + size] == image[target : target + size]


def canonical_sienna_boot_window_refs() -> list[tuple[str, int, list[tuple[str, str]]]]:
    rows = []
    lo, hi = XCP_WINDOW
    with (REPO / "data/generated/decompilations.jsonl").open() as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("record") != "function":
                continue
            try:
                entry = int(rec.get("entry_addr") or "", 16)
            except ValueError:
                continue
            if entry >= 0x20000:
                continue
            hits = []
            for ref in rec.get("data_references") or []:
                try:
                    target = int(str(ref.get("to_addr")), 16)
                except (TypeError, ValueError):
                    continue
                if lo <= target <= hi:
                    hits.append((ref.get("ref_type"), ref.get("to_addr")))
            if hits:
                rows.append((rec.get("name") or f"FUN_{entry:08x}", entry, hits))
    return rows


def canonical_function(name: str) -> dict:
    with (REPO / "data/generated/decompilations.jsonl").open() as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("record") == "function" and rec.get("name") == name:
                return rec
    raise AssertionError(f"canonical function missing: {name}")


print("== KEYLESS-001: security roots ==")
for image_name, image in IMAGES.items():
    for label, secret, expected_off in (
        ("payload-build", PAYLOAD_BUILD_SECRET, 0xBFD8),
        ("boot-SA", BOOT_SA_SECRET, 0xBFE8),
        ("application-SA", APP_SA_SECRET, 0x20840),
    ):
        check(
            f"{image_name}: {label} root occurs exactly once at 0x{expected_off:X}",
            find_all(image, secret) == [expected_off],
        )

print("== KEYLESS-002: table and handler implementation transfer ==")
sienna_table = uds_table(SIENNA, BOOT_UDS_TABLE["sienna"])
check("Sienna boot UDS table has exactly 20 complete records", len(sienna_table) == 20)
check("Sienna boot UDS SID order is pinned", [r[0] for r in sienna_table] == EXPECTED_SIDS)
check("Sienna boot UDS policy-byte order is pinned", [r[1] for r in sienna_table] == EXPECTED_POLICIES)

for image_name, image in FOREIGN.items():
    table = uds_table(image, BOOT_UDS_TABLE["corolla"])
    check(f"{image_name}: 20 complete boot UDS records", len(table) == 20)
    check(
        f"{image_name}: table is exact Sienna table with handler pointers shifted -0x1C",
        table == [shift_record(r, COROLLA_SHIFT) for r in sienna_table],
    )
    for body_name, entry, size in UDS_HANDLER_BODIES + CRITICAL_BOOT_BODIES:
        check(
            f"{image_name}: {body_name} complete body transfers at -0x1C",
            exact_shifted_body(image, entry, size),
        )

print("== KEYLESS-003: RequestDownload is SA-gated; wrap guard is defense-in-depth ==")
request_download = canonical_function("uds_request_download")
check(
    "canonical RequestDownload reads boot SA state FEBF2B0F at 0x5EFC",
    any(
        ref.get("from_addr") == "0x00005efc"
        and ref.get("ref_type") == "READ"
        and ref.get("to_addr") == "0xfebf2b0f"
        for ref in request_download.get("data_references") or []
    ),
)
# Raw bytes spanning the SA-state load/compare/NRC-0x33 gate at the canonical
# site. Exact RequestDownload body transfer above carries this sequence to H/F.
SA_GATE = bytes.fromhex("a49f0f93629ac20520363300")
check("Sienna RequestDownload SA gate bytes pinned at 0x5EFC", SIENNA[0x5EFC:0x5F08] == SA_GATE)
for image_name, image in FOREIGN.items():
    target = 0x5EFC + COROLLA_SHIFT
    check(f"{image_name}: RequestDownload SA gate transfers at 0x{target:X}", image[target:target+len(SA_GATE)] == SA_GATE)

WRAP_GUARD = bytes.fromhex("c6390796fffff231ab1d")
WRAP_GUARD_OFFSETS = {
    "sienna-8965B4512000": [0x32DA, 0x3320],
    "albinoelephant-8965H1202000": [0x32BE, 0x3304],
    "spanconstant-8965F1208000": [0x32BE, 0x3304],
}
for image_name, expected in WRAP_GUARD_OFFSETS.items():
    image = IMAGES[image_name]
    found = [
        off
        for off in range(0x3000, 0x4000)
        if image[off : off + len(WRAP_GUARD)] == WRAP_GUARD
    ]
    check(f"{image_name}: unsigned interval-wrap guard sites are exact", found == expected)

print("== KEYLESS-004: exact application XCP route descriptor absent from boot ==")
for image_name, image in IMAGES.items():
    hits = []
    for off in range(0, 0x20000 - 3):
        for endian in ("<", ">"):
            value = struct.unpack_from(endian + "I", image, off)[0]
            for ident in XCP_ROUTE_IDS:
                if value == XCP_DESCRIPTOR_TAG + (ident << 18) + XCP_DESCRIPTOR_ATTR:
                    hits.append((off, endian, ident))
    check(f"{image_name}: no exact packed 0x7F7/0x7F8 application descriptor in boot", hits == [])

print("== KEYLESS-005: recovered boot auth state does not overlap XCP window ==")
check("boot GP lies numerically inside XCP write window", XCP_WINDOW[0] <= BOOT_GP <= XCP_WINDOW[1])
for label, addr in SECURITY_STATE.items():
    check(f"{label} is below XCP write window", addr < XCP_WINDOW[0])

refs = canonical_sienna_boot_window_refs()
check(
    "Sienna boot direct-reference census is only zero-trip startup WRITE to FEBF7C00",
    refs == [("FUN_00001404", 0x1404, [("WRITE", "0xfebf7c00")])],
)
# The complete Sienna startup body transfers to H/Span at -0x1C. Its first RAM
# loop loads FEBF7C00 but compares against FEBE7000; unsigned start<end is false.
STARTUP_ENTRY = 0x1404
STARTUP_SIZE = 116
STARTUP_TARGET = STARTUP_ENTRY + COROLLA_SHIFT
ZERO_TRIP_LOOP = bytes.fromhex("3e06007cbffeb505010544f221060070befee1f1a1fd")
check("Sienna zero-trip clear-shape bytes pinned", SIENNA[0x1426:0x143C] == ZERO_TRIP_LOOP)
check("zero-trip loop direction is false", not (0xFEBF7C00 < 0xFEBE7000))
for image_name, image in FOREIGN.items():
    check(
        f"{image_name}: complete startup body transfers at -0x1C",
        SIENNA[STARTUP_ENTRY:STARTUP_ENTRY+STARTUP_SIZE]
        == image[STARTUP_TARGET:STARTUP_TARGET+STARTUP_SIZE],
    )

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
