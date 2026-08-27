#!/usr/bin/env python3
"""Verify that bootloader SecurityAccess is the prerequisite gate for the
download / write / reset services (SID 0x34, 0x2E, 0x11).

The bootloader tracks SA-unlock in a single byte at RAM 0xFEBF2B0F
(gp-relative displacement -0x6cf1 from gp = 0xFEBF9800, set by the reset
handler per ARCH-001). It is read by three UDS handlers, each of which requires
the byte == 2 and otherwise returns NRC 0x33 (securityAccessDenied):

    uds_request_download            (SID 0x34, handler 0x5D68)  read @ 0x5EFC
    uds_write_data_by_identifier    (SID 0x2E)                  read @ 0x49C6
    uds_ecu_reset                   (SID 0x11)                  read @ 0x610C

The byte reaches 2 via exactly one site: the success path of
uds_security_access_send_key (a correct 27 02 key derived from SEED_KEY_SECRET,
SEC-BOOT-002/003). Boot init and the diagnostic-session-change handler only
ever write 1, so DiagnosticSessionControl (10 0x) alone cannot satisfy the
gate -- SecurityAccess is mandatory, not redundant.

All assertions are exact instruction bytes at exact CodeFlash VAs (VA == file
offset in the standalone CodeFlash image; no Ghidra needed at test time). The
writer/reader provenance is re-runnable with:

    ghidra x-ref to 0xFEBF2B0F --projects-dir build/work/project --project rh850_p1me_mapped
"""
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from sienna_application_sa_keygen import (  # noqa: E402
    APPLICATION_LEVEL2_SA_SECRET,
    derive_application_sa_key,
)

CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

GP = 0xFEBF9800                       # set by reset handler 0x1F2 (ARCH-001)
STATE_BYTE = GP - 0x6CF1              # == 0xFEBF2B0F
ST_R1 = bytes.fromhex("440f0f93")     # st.b  r1, -0x6cf1[gp]   -> writes STATE_BYTE
REJECT = bytes.fromhex("20363300")    # movea 0x33, r0, r6       (NRC securityAccessDenied)

passed = failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def find_all(needle):
    out, i = [], 0
    while True:
        j = CF.find(needle, i)
        if j < 0:
            break
        out.append(j)
        i = j + 1
    return out


print("== SA-unlock state byte 0xFEBF2B0F ==")
check("gp displacement -0x6cf1 resolves to 0xFEBF2B0F",
      STATE_BYTE == 0xFEBF2B0F, hex(STATE_BYTE))

print("\n== Exhaustive writer set: only SA send_key writes 2 ==")
write_sites = find_all(ST_R1)
check("exactly three writers of 0xFEBF2B0F (st.b r1,-0x6cf1[gp])",
      write_sites == [0x5090, 0x54DC, 0x561E],
      str([hex(o) for o in write_sites]))

# 0x54dc: uds_security_access_send_key success path -- mov 0x2, r1 then store.
check("SA send_key success: mov 2,r1 @0x54da", CF[0x54DA:0x54DC] == bytes.fromhex("020a"), CF[0x54DA:0x54DC].hex())
check("SA send_key success: store 2 -> 0xFEBF2B0F @0x54dc", CF[0x54DC:0x54E0] == ST_R1, CF[0x54DC:0x54E0].hex())
# Immediately above: the key-mismatch path emits NRC 0x35 (invalidKey) and branches away.
check("SA send_key mismatch path emits NRC 0x35 @0x54d4", CF[0x54D4:0x54D8] == bytes.fromhex("20363500"), CF[0x54D4:0x54D8].hex())

# 0x5090: boot init (FUN_00005086) -- mov 0x1, r1 @0x508a.
check("boot init: mov 1,r1 @0x508a", CF[0x508A:0x508C] == bytes.fromhex("010a"), CF[0x508A:0x508C].hex())
check("boot init: store 1 -> 0xFEBF2B0F @0x5090", CF[0x5090:0x5094] == ST_R1, CF[0x5090:0x5094].hex())

# 0x561e: diagnostic-session-change handler (FUN_000055fc, called from
# bootloader_set_diagnostic_session) -- mov 0x1, r1 @0x561c.
check("session-change: mov 1,r1 @0x561c", CF[0x561C:0x561E] == bytes.fromhex("010a"), CF[0x561C:0x561E].hex())
check("session-change: store 1 -> 0xFEBF2B0F @0x561e", CF[0x561E:0x5622] == ST_R1, CF[0x561E:0x5622].hex())

print("\n== Gated service: RequestDownload (SID 0x34) ==")
check("RequestDownload loads 0xFEBF2B0F @0x5efc", CF[0x5EFC:0x5F00] == bytes.fromhex("a49f0f93"), CF[0x5EFC:0x5F00].hex())
check("RequestDownload rejects with NRC 0x33 unless == 2",
      CF[0x5F00:0x5F08] == bytes.fromhex("629ac205") + REJECT, CF[0x5F00:0x5F08].hex())

print("\n== Gated service: WriteDataByIdentifier (SID 0x2E) ==")
check("WDBI loads 0xFEBF2B0F @0x49c6", CF[0x49C6:0x49CA] == bytes.fromhex("a40f0f93"), CF[0x49C6:0x49CA].hex())
check("WDBI rejects with NRC 0x33 unless == 2",
      CF[0x49CA:0x49D2] == bytes.fromhex("620ac205") + REJECT, CF[0x49CA:0x49D2].hex())

print("\n== Gated service: ECUReset (SID 0x11) ==")
check("ECUReset loads 0xFEBF2B0F @0x610c", CF[0x610C:0x6110] == bytes.fromhex("a40f0f93"), CF[0x610C:0x6110].hex())
check("ECUReset rejects with NRC 0x33 unless == 2",
      CF[0x6110:0x6118] == bytes.fromhex("620ac205") + REJECT, CF[0x6110:0x6118].hex())

print("\n== Application SecurityAccess standalone key generator ==")
check(
    "application level-2 SA secret remains byte-exact",
    APPLICATION_LEVEL2_SA_SECRET.hex() == "893e08418c741ffa2a9c044bffa55813",
)
check(
    "application SA zero-record known-answer vector",
    derive_application_sa_key(
        bytes.fromhex("00112233445566778899aabbccddeeff"), bytes(16)
    ).hex() == "9112f86dad79b9ad61186a4a15d78cda",
)
check(
    "application SA chosen-record known-answer vector",
    derive_application_sa_key(
        bytes.fromhex("ffeeddccbbaa99887766554433221100"),
        bytes.fromhex("deadbeef000000000000000000000000"),
    ).hex() == "43b3af5a1cab4eda81d12df6329f6a62",
)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
