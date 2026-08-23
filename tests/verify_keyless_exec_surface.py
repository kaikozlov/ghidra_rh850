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
- KEYLESS-006: application startup copies the application-SA root from
  CodeFlash into a LocalRAM mirror that is readable before SecurityAccess by
  both SID 0x23 RMBA and XCP SHORT_UPLOAD on all three tracked images.
- KEYLESS-007: preloading boot TransferData state does not bypass RequestDownload
  SA. The live application-to-boot handoff enters boot failure/programming init,
  which deterministically resets transfer/auth state before DCM accepts traffic;
  the complete reset/TransferData bodies transfer to H/F.
- KEYLESS-008: CTBP is initialized to zero once at reset and is not attacker-set
  before the live handoff; the one boot CALLT therefore resolves through a fixed
  low-CodeFlash table entry.
- KEYLESS-009: RequestDownload has pre-SA setup side effects, but its payload-ready
  prerequisite is itself SA-gated through WDBI and destination/length commits are
  after the final SA check.
- KEYLESS-012: once KEYLESS-006 recovers application SA, the broad Dcm/RDBI/RID/
  WDBI policy tables do not expose a new privilege boundary because their
  configured security lists are empty; the material callback-local exception is
  proprietary BA selector F7/BAENA, which tests SA level-2 mask bit 0x02.
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
    # The live app->boot programming path eventually reaches these before DCM
    # accepts tester traffic.  Together they reset transfer/auth state.
    ("boot_diag_init_root", 0x0770, 16),
    ("boot_diag_enable_record", 0x69D2, 52),
    ("boot_diag_init_dispatch", 0x6A22, 138),
    ("boot_transfer_auth_state_init", 0x5086, 100),
]

XCP_ROUTE_IDS = (0x7F7, 0x7F8)
XCP_DESCRIPTOR_ATTR = 2
XCP_DESCRIPTOR_TAG = 0x80000000
XCP_WINDOW = (0xFEBF7C00, 0xFEBFFBFF)
BOOT_GP = 0xFEBF9800
APP_INFO_COPY = {
    "sienna-8965B4512000": (0x62662, 0xFEBF7BB0, 0x25EA0, 0x293F4),
    "albinoelephant-8965H1202000": (0x5C9B6, 0xFEBF7B50, 0x25BB0, 0x28F0C),
    "spanconstant-8965F1208000": (0x5C9B6, 0xFEBF7B50, 0x25BB0, 0x28F0C),
}
APP_INFO_SOURCE = 0x20810
APP_SA_OFFSET_IN_COPY = 0x20840 - APP_INFO_SOURCE

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


def overlaps(start: int, size: int, exclusions: list[tuple[int, int]]) -> bool:
    end = start + size - 1
    return any(start <= hi and lo <= end for lo, hi in exclusions)


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


print("== KEYLESS-006: application SA root is self-disclosing before SA ==")
for image_name, image in IMAGES.items():
    copy_entry, copy_base, rmba_obj, xcp_excl_base = APP_INFO_COPY[image_name]
    mirror = copy_base + APP_SA_OFFSET_IN_COPY

    # The 32-byte copy body loads CodeFlash 0x20810+index, writes one byte to
    # the fixed LocalRAM base+index, and iterates exactly 0x40 bytes.  H and F
    # differ from Sienna only in the destination immediate.
    body = image[copy_entry : copy_entry + 32]
    check(f"{image_name}: app-info copier has pinned 32-byte loop shape",
          len(body) == 32
          and body[:14] == bytes.fromhex("000a409e0200c199939f11083e06")
          and body[16:] == bytes.fromhex("bffec1f1410a0106c0ff809bb9f57f00")
          and body[14:16] == struct.pack("<H", copy_base & 0xFFFF))
    check(f"{image_name}: app-info source ends with application-SA root",
          image[APP_INFO_SOURCE + APP_SA_OFFSET_IN_COPY:
                APP_INFO_SOURCE + APP_SA_OFFSET_IN_COPY + 16] == APP_SA_SECRET)
    check(f"{image_name}: startup copy places application-SA root at 0x{mirror:08X}",
          APP_INFO_SOURCE + APP_SA_OFFSET_IN_COPY == 0x20840
          and mirror == (0xFEBF7BE0 if image_name.startswith("sienna") else 0xFEBF7B80))

    # SID 0x23 has no service-level SecurityAccess list and is reachable in
    # extended session.  Its LocalRAM class/exclusion policy is independently
    # pinned by the application RMBA/H-variant suites; here we pin the exact
    # no-SA service object plus the relevant exclusion geometry.
    callback, sec_ptr, session_ptr, sub_ptr = struct.unpack_from("<IIII", image, rmba_obj)
    sid, has_sub, sec_count, session_count, sub_count = image[rmba_obj + 16:rmba_obj + 21]
    check(f"{image_name}: SID 0x23 RMBA service object has no SA policy",
          sid == 0x23 and has_sub == 0 and sec_ptr == 0 and sec_count == 0
          and session_count == 1 and image[session_ptr] == 3
          and sub_ptr == 0 and sub_count == 0 and callback != 0)

    exclusions = [struct.unpack_from("<II", image, xcp_excl_base + i * 8) for i in range(5)]
    check(f"{image_name}: 16-byte application-SA mirror is outside LocalRAM read exclusions",
          not overlaps(mirror, 16, exclusions))

# XCP SHORT_UPLOAD uses the same five LocalRAM exclusions.  The standard map
# has no GET_SEED/UNLOCK implementation, yet SHORT_UPLOAD is configured.
for image_name, image in IMAGES.items():
    if image_name.startswith("sienna"):
        count_off, map_off, cb_off, short_upload = 0x22BD1, 0x22C04, 0x22C30, 0x81A2E
    else:
        count_off, map_off, cb_off, short_upload = 0x22A15, 0x22A48, 0x22A74, 0x7BE2A
    command_map = image[map_off:map_off + image[count_off]]
    callbacks = [struct.unpack_from("<I", image, cb_off + i * 4)[0] for i in range(18)]
    f4_index = command_map[0xFF - 0xF4]
    check(f"{image_name}: XCP SHORT_UPLOAD remains configured without GET_SEED/UNLOCK",
          command_map[0xFF - 0xF8] == 0
          and command_map[0xFF - 0xF7] == 0
          and f4_index != 0
          and callbacks[f4_index] == short_upload)


print("== KEYLESS-007: retained TransferData context is reset before boot DCM ==")
transfer_data = canonical_function("uds_transfer_data")
transfer_init = canonical_function("FUN_00005086")
boot_diag_enable = canonical_function("FUN_000069d2")
boot_diag_dispatch = canonical_function("FUN_00006a22")
boot_failure_loop = canonical_function("boot_failure_main_loop")
boot_failure_init = canonical_function("FUN_00001338")
live_entry = canonical_function("FUN_0000148e")

check("Sienna TransferData dispatches only from transfer-state FEBF2B13",
      any(ref.get("from_addr") == "0x00004dc0"
          and ref.get("ref_type") == "READ"
          and ref.get("to_addr") == "0xfebf2b13"
          for ref in transfer_data.get("data_references") or []))
check("Sienna diagnostic init clears transfer-state FEBF2B13",
      any(ref.get("ref_type") == "WRITE" and ref.get("to_addr") == "0xfebf2b13"
          for ref in transfer_init.get("data_references") or [])
      and "DAT_febf2b13 = 0;" in transfer_init.get("decompiled_c", ""))
check("Sienna diagnostic init re-locks boot SA and clears authorization bits",
      all(token in transfer_init.get("decompiled_c", "") for token in (
          r"uds_security_access_state = '\x01';",
          "DAT_febf2b11 = 0;",
          r"payload_did_crypto_ready = '\0';",
          "DAT_febf2b17 = 0;",
      )))
check("live 0x9F00 path enters failure/programming main-loop init",
      "boot_failure_main_loop();" in live_entry.get("decompiled_c", "")
      and "FUN_00001338();" in boot_failure_loop.get("decompiled_c", "")
      and "FUN_00000770();" in boot_failure_init.get("decompiled_c", ""))
check("boot diagnostic root enables and then runs state initializer",
      "DAT_febf2bd0 = 1;" in boot_diag_enable.get("decompiled_c", "")
      and "FUN_00005086();" in boot_diag_dispatch.get("decompiled_c", ""))
check("fixed live-handoff record requests programming session",
      SIENNA[0x31914:0x31914+20] == struct.pack("<IIIII", 0, 0x7A1, 0, 0, 2))

# H/F move this complete boot cohort by -0x1C. The service handler itself was
# already covered by KEYLESS-002; pin it here as the context-bypass sink too.
for image_name, image in FOREIGN.items():
    check(f"{image_name}: TransferData complete body transfers at -0x1C for context-bypass audit",
          exact_shifted_body(image, 0x4DBA, 56))


print("== KEYLESS-008: live handoff cannot inherit attacker-selected CTBP ==")
CTBP_ZERO = bytes.fromhex("e0a72000")  # ldsr r0,CTBP
for image_name, image in IMAGES.items():
    hits = [off for off in range(len(image) - len(CTBP_ZERO) + 1)
            if image[off:off + len(CTBP_ZERO)] == CTBP_ZERO]
    check(f"{image_name}: CTBP-zero instruction occurs exactly once at reset startup ({[hex(x) for x in hits]})",
          hits == [0x25E])
    check(f"{image_name}: live 0x9F00 handoff does not rewrite CTBP",
          CTBP_ZERO not in image[0x9F00:0x9F64])

# The one boot CALLT used by the timer helper indexes table entry 0x22. With
# CTBP fixed to zero, vector 0x22 selects the halfword at CodeFlash 0x44.
check("Sienna boot CALLT 0x22 is pinned at 0x1D5C", SIENNA[0x1D5C:0x1D5E] == bytes.fromhex("2202"))
check("Sienna CTBP=0 table entry 0x22 resolves to fixed 0x1E1E",
      struct.unpack_from("<H", SIENNA, 0x44)[0] == 0x1E1E)
for image_name, image in FOREIGN.items():
    check(f"{image_name}: relocated boot CALLT 0x22 is pinned at 0x1D40",
          image[0x1D40:0x1D42] == bytes.fromhex("2202"))
    check(f"{image_name}: CTBP=0 table target relocates exactly -0x1C",
          struct.unpack_from("<H", image, 0x44)[0] == 0x1E02)


print("== KEYLESS-009: RequestDownload pre-SA side effects cannot arm a transfer ==")
request_download = canonical_function("uds_request_download")
wdbi = canonical_function("uds_write_data_by_identifier")
boot_init = canonical_function("FUN_00005086")
# RequestDownload may set transfer-status FEBF2B17 before the final SA comparison,
# but it consults payload-ready FEBF2B16 first.  The only non-init writer of
# FEBF2B16 is WDBI, whose own SA==2 gate precedes that write.
check("Sienna RequestDownload reads payload-ready before final SA gate",
      any(ref.get("from_addr") == "0x00005e4a" and ref.get("to_addr") == "0xfebf2b16"
          for ref in request_download.get("data_references") or [])
      and any(ref.get("from_addr") == "0x00005efc" and ref.get("to_addr") == "0xfebf2b0f"
              for ref in request_download.get("data_references") or []))
check("Sienna RequestDownload can write transfer-status before final SA gate",
      any(ref.get("from_addr") == "0x00005e60" and ref.get("to_addr") == "0xfebf2b17"
          for ref in request_download.get("data_references") or []))
check("Sienna WDBI SA gate precedes its payload-ready write",
      any(ref.get("from_addr") == "0x000049c6" and ref.get("to_addr") == "0xfebf2b0f"
          for ref in wdbi.get("data_references") or [])
      and any(ref.get("from_addr") == "0x00004a76" and ref.get("to_addr") == "0xfebf2b16"
              for ref in wdbi.get("data_references") or []))
check("Sienna boot init clears payload-ready and transfer-status",
      "payload_did_crypto_ready = '\\0';" in boot_init.get("decompiled_c", "")
      and "DAT_febf2b17 = 0;" in boot_init.get("decompiled_c", ""))
# Destination/remaining-length commits occur only after the final SA comparison.
for addr, target in (("0x00005f1e", "0xfebf2b00"), ("0x00005f22", "0xfebf2b04")):
    check(f"Sienna RequestDownload commits {target} only after SA gate",
          any(ref.get("from_addr") == addr and ref.get("ref_type") == "WRITE" and ref.get("to_addr") == target
              for ref in request_download.get("data_references") or []))
for image_name, image in FOREIGN.items():
    check(f"{image_name}: complete RequestDownload body carries the same ordering at -0x1C",
          exact_shifted_body(image, 0x5D68, 468))
    check(f"{image_name}: complete WDBI body carries the same payload-ready prerequisite at -0x1C",
          exact_shifted_body(image, 0x4948, 328))


print("== KEYLESS-012: recovered application SA only adds the BA F7 local gate ==")
# All primary Sienna Dcm service objects advertise zero configured security
# levels. The dedicated security-consumer and routine-control suites separately
# pin all 242 RDBI policies, 19 RIDs, and WDBI policy records to no effective
# level > 0. The material callback-local exception is BA F7/BAENA.
app_sec_counts = [SIENNA[0x25E28 + i * 0x18 + 0x12] for i in range(17)]
check("Sienna primary application Dcm service security counts are all zero",
      app_sec_counts == [0] * 17)
check("Sienna BA service itself has no Dcm-level SA requirement",
      SIENNA[0x25E28 + 16 * 0x18 + 0x10] == 0xBA
      and SIENNA[0x25E28 + 16 * 0x18 + 0x12] == 0)
check("Sienna BA F7 local helper tests application-SA level-2 mask bit 0x02",
      SIENNA[0x34DA2:0x34DA6] == bytes.fromhex("ca9e0200"))
check("Sienna BA F7/BAENA token is pinned", SIENNA[0x210B6:0x210BB] == b"BAENA")
# H/F preserve the BA token family and the same post-reader bit-2 test shape,
# although their proprietary-operation table is target-specific and is not
# promoted here to a complete Sienna operation-map transfer.
for image_name, image in FOREIGN.items():
    check(f"{image_name}: BAENA token remains present at target-native location",
          image[0x21078:0x2107D] == b"BAENA")
    check(f"{image_name}: BA F7 target-native gate retains level-2 bit-test tail",
          image[0x30984:0x30994] == SIENNA[0x34D9E:0x34DAE])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
