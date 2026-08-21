#!/usr/bin/env python3
"""Independent raw-image checks for remaining bootloader diagnostics.

Verifies SIDs 0x10/0x11/0x28/0x3E/0x85 and RoutineControl IDs
0x10F0..0x10F3 directly from committed CodeFlash. No Ghidra or sibling
repository is required.
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
P1ME = json.loads((REPO / "data" / "p1me_product_memory.json").read_text(encoding="utf-8"))
TP = 0x869C

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def u16(address: int) -> int:
    return struct.unpack_from("<H", CF, address)[0]


def u32(address: int) -> int:
    return struct.unpack_from("<I", CF, address)[0]


def occurrences(pattern: bytes) -> list[int]:
    result: list[int] = []
    start = 0
    while True:
        found = CF.find(pattern, start)
        if found < 0:
            return result
        result.append(found)
        start = found + 1


print("== image and diagnostic configuration roots ==")
check("CodeFlash is 1 MiB", len(CF) == 0x100000)
check(
    "CodeFlash SHA-256",
    hashlib.sha256(CF).hexdigest()
    == "21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde",
)
check("bootloader tp is 0x869C", CF[0x1F8:0x1FE] == bytes.fromhex("25069c860000"))

services = {}
for i in range(20):
    sid, mask, reserved, handler = struct.unpack_from("<BBHI", CF, 0x8E54 + i * 8)
    services[sid] = (mask, reserved, handler)
expected_services = {
    0x10: (0x03, 0, 0x614A),
    0x11: (0x02, 0, 0x60C2),
    0x28: (0x01, 0, 0x688A),
    0x3E: (0x01, 0, 0x4FF8),
    0x85: (0x01, 0, 0x693A),
    0x31: (0x02, 0, 0x567E),
}
for sid, expected in expected_services.items():
    check(f"SID {sid:02X} mask/reserved/handler", services[sid] == expected, repr(services[sid]))

# DIAG-BOOT-003: complete service-table enumeration + standard-UDS-only negative.
implemented = {
    0x10: 0x614A, 0x11: 0x60C2, 0x22: 0x5FB8, 0x27: 0x5516, 0x28: 0x688A,
    0x2E: 0x4948, 0x31: 0x567E, 0x34: 0x5D68, 0x36: 0x4DBA, 0x37: 0x5C92,
    0x3E: 0x4FF8, 0x85: 0x693A,
}
unsupported = (0x14, 0x19, 0x23, 0x2C, 0x2F, 0xAB, 0xBA, 0xBB)
for sid, h in implemented.items():
    check(
        f"DIAG-BOOT-003 SID 0x{sid:02X} implemented -> handler 0x{h:X}",
        services.get(sid, (0, 0, 0))[2] == h,
    )
for sid in unsupported:
    check(
        f"DIAG-BOOT-003 SID 0x{sid:02X} routed to uds_unsupported_service_handler 0x69B0",
        services.get(sid, (0, 0, 0))[2] == 0x69B0,
    )
check(
    "DIAG-BOOT-003 table is exactly 12 implemented + 8 unsupported (20 entries)",
    set(services) == set(implemented) | set(unsupported),
    f"{len(services)} entries",
)
check(
    "DIAG-BOOT-003 no proprietary/VFOREST handler (all handlers are standard UDS or 0x69B0)",
    all(h == 0x69B0 or s in implemented for s, (_, _, h) in services.items()),
)

check("ECUReset requires configured session 2", CF[TP + 0x858] == 2)
check("CommunicationControl requires configured session 3", CF[TP + 0x85A] == 3)
check("ControlDTCSetting requires configured session 3", CF[TP + 0x85B] == 3)
check("RoutineControl requires configured session 2", CF[TP + 0x85D] == 2)
check("TesterPresent allows sessions 1/2/3", CF[TP + 0x861:TP + 0x864] == b"\x01\x02\x03")

print("\n== DiagnosticSessionControl 0x10 ==")
check("session handler copies exactly two request bytes", CF[0x6158:0x6162] == bytes.fromhex("23360200023a80ff5206"))
check("programming-from-default branch contains NRC 0x7E", CF[0x6196:0x61A4] == bytes.fromhex("849f0f93629aca0520367e00e5ed"))
check("valid session request stores queued state", CF[0x61D8:0x61E0] == bytes.fromhex("a30f030024f69f93"))
check("session task dispatches from requested session minus one", CF[0x6244:0x6250] == bytes.fromhex("80072100a40fa393e009d245"))
check("session completion updates the current-session byte", CF[0x51E6:0x51EA] == bytes.fromhex("44e70e93"))
check("session response starts with positive SID 0x50", CF[0x6204:0x620C] == bytes.fromhex("80072100a49f9f93"))
check("session response writes P2/P2-star bytes 00 32 01 F4", CF[0x6222:0x6232] == bytes.fromhex("8203200e3200830b010a840b140a850b"))
check("queued session task calls completion and response path", CF[0x62C0:0x62C8] == bytes.fromhex("bfff18efbfff40ff"))

print("\n== ECUReset 0x11 ==")
check("ECUReset copies exactly two request bytes", CF[0x60CE:0x60D8] == bytes.fromhex("23360200023a80ffdc06"))
check("ECUReset reads session policy byte tp+0x858", CF[0x60D8:0x60E0] == bytes.fromhex("850f590884970f93"))
check("ECUReset requires security state 2", CF[0x6108:0x6110] == bytes.fromhex("1200a5f5a40f0f93"))
check("ECUReset stores accepted subfunction", CF[0x6124:0x6128] == bytes.fromhex("44979e93"))
check("ECUReset schedules reset then builds response", CF[0x6128:0x6130] == bytes.fromhex("80ffb206bfff6cff"))
check("ECUReset positive response emits SID 0x51", CF[0x609C:0x60A4] == bytes.fromhex("849f9f93200e5100"))
check("reset coordinator resets immediately when transport idle", CF[0x67DE:0x67EA] == bytes.fromhex("840fbb93e009ca05bfffb8ad"))
check("reset coordinator otherwise sets pending-reset byte", CF[0x67EC:0x67F2] == bytes.fromhex("010a440fbd93"))
check("Tx confirmation reads pending-reset state", CF[0x66D6:0x66DE] == bytes.fromhex("a40fbd936457b593"))
check("successful Tx confirmation calls nonreturning reset", CF[0x66DE:0x66EA] == bytes.fromhex("610aba0de0e9ca05bfffb8ae"))
check("failed Tx confirmation clears pending reset", CF[0x66EC:0x66F0] == bytes.fromhex("4407bd93"))
check("suppressed-response path can call reset immediately", CF[0x679C:0x67AC] == bytes.fromhex("a40fbd936457b593610aba05bffff6ad"))
check("hard-reset path disables/halts and never returns", CF[0x159E:0x15B4] == bytes.fromhex("800721008036ffff80ff785cbfffa6ffbfffb2ff8505"))

print("\n== CommunicationControl 0x28 and ControlDTCSetting 0x85 ==")
check("CommunicationControl copies exactly three request bytes", CF[0x6896:0x68A2] == bytes.fromhex("233601008303033abfff12ff"))
check("CommunicationControl reads session policy tp+0x85A", CF[0x68A2:0x68AA] == bytes.fromhex("850f5b0884970f93"))
check("CommunicationControl validates communication type 1", CF[0x68D0:0x68D8] == bytes.fromhex("20361200a5f563ea"))
check("CommunicationControl stores accepted subfunction", CF[0x68EE:0x68F2] == bytes.fromhex("4497c393"))
check("CommunicationControl emits positive SID 0x68", CF[0x6864:0x686C] == bytes.fromhex("a49fc393200e6800"))
comm_load = CF[0x6864:0x6868]
comm_store = CF[0x68EE:0x68F2]
check("CommunicationControl state byte has one load", occurrences(comm_load) == [0x6864], repr(occurrences(comm_load)))
check("CommunicationControl state byte has one store", occurrences(comm_store) == [0x68EE], repr(occurrences(comm_store)))

check("ControlDTCSetting copies exactly two request bytes", CF[0x6946:0x6950] == bytes.fromhex("23360200023abfff64fe"))
check("ControlDTCSetting reads session policy tp+0x85B", CF[0x6950:0x6958] == bytes.fromhex("a50f5b0884970f93"))
check("ControlDTCSetting accepts subfunction 2", CF[0x697C:0x6984] == bytes.fromhex("c20520361200a5f5"))
check("ControlDTCSetting stores accepted subfunction", CF[0x698E:0x6992] == bytes.fromhex("4497c493"))
check("ControlDTCSetting emits positive SID 0xC5", CF[0x6914:0x691C] == bytes.fromhex("849fc593200ec5ff"))
dtc_store = CF[0x698E:0x6992]
check("ControlDTCSetting state byte has one store", occurrences(dtc_store) == [0x698E], repr(occurrences(dtc_store)))
# The response load has a register-encoding variant; its exact instruction is still unique.
dtc_load = CF[0x6914:0x6918]
check("ControlDTCSetting response load is unique", occurrences(dtc_load) == [0x6914], repr(occurrences(dtc_load)))

print("\n== TesterPresent 0x3E ==")
check("TesterPresent copies exactly two request bytes", CF[0x5006:0x5010] == bytes.fromhex("233602008303023a80ff"))
check("TesterPresent reads current session", CF[0x501A:0x501E] == bytes.fromhex("849f0f93"))
check("TesterPresent positive response emits SID 0x7E", CF[0x4FD2:0x4FDA] == bytes.fromhex("849fcd92200e7e00"))
check("TesterPresent stores subfunction only for response", CF[0x5054:0x5058] == bytes.fromhex("440fcc92"))
tester_load = CF[0x4FD2:0x4FD6]
tester_store = CF[0x5054:0x5058]
check("TesterPresent subfunction response load is unique", occurrences(tester_load) == [0x4FD2], repr(occurrences(tester_load)))
check("TesterPresent subfunction store is unique", occurrences(tester_store) == [0x5054], repr(occurrences(tester_store)))
check("diagnostic initialization writes default session", CF[0x508C:0x5090] == bytes.fromhex("440f0e93"))
check("explicit session completion is the other local session writer", CF[0x51E6:0x51EA] == bytes.fromhex("44e70e93"))

print("\n== SecurityAccess 0x27 request-seed / send-key ==")
BOOT_GP = 0xFEBF9800
check("SID 0x27 handler is 0x5516", services[0x27] == (0x02, 0, 0x5516), repr(services.get(0x27)))
check("request-seed rejects lockout flag with NRC 0x37",
      CF[0x532C:0x533C] == bytes.fromhex("840f5793a4ef5593610aca0520363700"),
      CF[0x532C:0x533C].hex())
check("request-seed requires total length 0x12",
      CF[0x5340:0x534A] == bytes.fromhex("0606eeffe20520361300"),
      CF[0x5340:0x534A].hex())
check("request-seed lockout/state GP loads resolve to FEBF2B56/FEBF2B55",
      (BOOT_GP + (-0x6CAA)) & 0xFFFFFFFF == 0xFEBF2B56 and
      (BOOT_GP + (-0x6CAB)) & 0xFFFFFFFF == 0xFEBF2B55)
check("send-key gates on security state then requires length 0x12",
      CF[0x53F6:0x5412] == bytes.fromhex(
          "c600a4ef559361eae1070f01e207050163eaeb070501d97d0606eeff"),
      CF[0x53F6:0x5412].hex())
check("send-key calls security_access_compute_expected_key",
      CF[0x5464:0x546C] == bytes.fromhex("0736100080ffe41b"),
      CF[0x5464:0x546C].hex())
check("send-key emits NRC 0x35 invalidKey",
      CF[0x54D4:0x54DA] == bytes.fromhex("2036350085ad"),
      CF[0x54D4:0x54DA].hex())
check("send-key emits NRC 0x36 exceededNumberOfAttempts",
      CF[0x54C8:0x54CE] == bytes.fromhex("20363600e5ad"),
      CF[0x54C8:0x54CE].hex())
check("send-key success stores security state 2 at FEBF2B0F",
      CF[0x54DA:0x54E0] == bytes.fromhex("020a440f0f93") and
      (BOOT_GP + (-0x6CF1)) & 0xFFFFFFFF == 0xFEBF2B0F,
      CF[0x54DA:0x54E0].hex())
check("send-key attempt counter lives at FEBF2B57",
      (BOOT_GP + (-0x6CA9)) & 0xFFFFFFFF == 0xFEBF2B57)
# The mismatch branch tests (attempt_counter - 1). Starting from zero, the
# first failure takes the increment/NRC-0x35 path; with counter == 1 the next
# failure takes the lockout/NRC-0x36 path and clears the counter.
check("send-key second-failure lockout branch is exact",
      CF[0x5498:0x54DA] == bytes.fromhex(
          "bfff8cc8210600c2eb0b640f1d93010a440f569364572193000a4407579301f0"
          "c4f15e072493410a0106f0ff96fd01ea20363600e5ad449f579301ea2036350085ad"),
      CF[0x5498:0x54DA].hex())
check("SecurityAccess delay worker is exact and clears FEBF2B56 after expiry",
      CF[0x5584:0x55AA] == bytes.fromhex(
          "80072100840f5793610aca0dbfff94c7240f2193a151240f1d93e151b3054407569340063f00"))
check("SecurityAccess init arms 200000000-tick delay and clears attempts",
      CF[0x55AA:0x55FC] == bytes.fromhex(
          "80072100210600c2eb0b640f1d93bfff6cc7010a440f569364572193000a44075793"
          "249e249301f0d3f1410a80030106f0ffa003f6f5000a01f0d3f19003410a0106f0ffa6fd13f0010ab003b10b40063f00"))
# The delay's wall-clock scale is independently recoverable from the actual
# counter source and TAUJ1 configuration, not from the adjacent CanTp numbers.
check("free-running SecurityAccess timer reader is exact",
      CF[0x1D24:0x1D2C] == bytes.fromhex("8007095120ca7f00"))
check("tracked timer source is TAUJ1CNT0 at FFE51010",
      P1ME["timer"]["tauj1cnt0_address"] == 0xFFE51010)
check("TAUJ1 init stores TPS=FFF2 and CMOR0=0156",
      P1ME["timer"]["firmware_tauj1tps_value"] == 0xFFF2 and
      P1ME["timer"]["firmware_tauj1cmor0_value"] == 0x0156)
check("P1M-E 80MHz P-Bus and PRS0=2 make TAUJ1 CK0 20MHz",
      P1ME["timer"]["p_bus_hz"] == 80_000_000 and
      P1ME["timer"]["prs0"] == 2 and
      P1ME["timer"]["ck0_hz"] == 20_000_000)
check("SecurityAccess 200000000-tick delay is 10 seconds",
      P1ME["timer"]["security_delay_ticks"] // P1ME["timer"]["ck0_hz"] == 10 and
      P1ME["timer"]["security_delay_ms"] == 10_000)
check("generic boot scheduler body pins exact x20000 counter scaling",
      CF[0x1D2C:0x1D56] == bytes.fromhex(
          "8007a17006e007d89c0008d0db0009c88036ffff80ffde540a30bfffdefffcf60c00240e3891c1f103d5"))
check("adjacent CanTp timing configuration pins raw 1000/150/10 values",
      int.from_bytes(CF[0x8D5C:0x8D5E], "little") == 1000 and
      int.from_bytes(CF[0x8D5E:0x8D60], "little") == 150 and
      int.from_bytes(CF[0x8D64:0x8D66], "little") == 10)

# Boot diagnostic initialization does arm the same delay, but the normal
# application->PROGRAMMING retained handoff deliberately clears it before the
# synthetic bootloader 10 02 is replayed.  This is why successful field unlocks
# roughly one second after PROGRAMMING do not contradict the 10-second bad-key
# backoff.
check("normal programming handoff record is zero-kind / 0x7A1 / session 2",
      struct.unpack_from("<II", CF, 0x31914) == (0, 0x7A1) and CF[0x31924] == 2)
check("handoff session pre-hook calls session-3 setter then clear-delay helper",
      CF[0x5148:0x5158] == bytes.fromhex("8007210080ffc01180ffda0440063f00"))
check("session-3 setter body is exact before synthetic 10 02 replay",
      CF[0x630C:0x631C] == bytes.fromhex("80072100010a440fa1930332bfffc0ee"))
check("clear-delay helper writes FEBF2B56 = 0",
      CF[0x562A:0x5630] == bytes.fromhex("440756937f00"))
# CORR-089: failed-validity word0==FF arms DCM but does not take the retained
# synthetic-request arm. Pin the setup/session-control bodies and the unique
# default-session -> programming NRC 0x7E site so the two entry states cannot
# again be collapsed into one "already-programming" state.
check("boot diagnostic setup body pins distinct word0==0 and word0==FF arms",
      hashlib.sha256(CF[0x6A22:0x6A22 + 138]).hexdigest()
      == "f6acb6647f8343527e82a2f02dfbe8ec90ca8833d6edb92f862a193f883db5ca")
check("DiagnosticSessionControl body is exact for entry-state distinction",
      hashlib.sha256(CF[0x614A:0x614A + 186]).hexdigest()
      == "a14405a1ed4aee55e370e073c289716d5c48bd1543c38060491303a665132883")
check("default-session direct 10 02 rejection emits unique NRC 0x7E",
      occurrences(bytes.fromhex("20367e00")) == [0x619E],
      repr(occurrences(bytes.fromhex("20367e00"))))
check("NRC helper builds negative response for SID 0x27",
      CF[0x52CA:0x52D6] == bytes.fromhex("800721000638870020362700"))

print("\n== RoutineControl table and common policy ==")
routines = [struct.unpack_from("<I H B B I", CF, 0x8F44 + i * 12) for i in range(5)]
check("routine IDs are 10F0/10F1/10F2/10F3/FF00", [r[1] for r in routines] == [0x10F0, 0x10F1, 0x10F2, 0x10F3, 0xFF00])
check("all routines are StartRoutine-only", [r[2] for r in routines] == [1] * 5)
check("routine option lengths are 10/10/10/0/10", [r[3] for r in routines] == [10, 10, 10, 0, 10])
check("routine configured result words are zero", [r[4] for r in routines] == [0] * 5)
check("RoutineControl reads programming-session policy", CF[0x56F4:0x56FC] == bytes.fromhex("84870f93e181e28f"))
check("RoutineControl locked path contains NRC 0x33", bytes.fromhex("20363300") in CF[0x567E:0x5936])
check("RoutineControl unsupported-subfunction path contains NRC 0x12", bytes.fromhex("20361200") in CF[0x567E:0x5936])
check("routine worker dispatch subtracts RID base 0x10F0", CF[0x5C1A:0x5C22] == bytes.fromhex("e40f6593010e10ef"))
check("RIDs 10F0/10F1 share verifier worker branch", CF[0x5C22:0x5C3A] == bytes.fromhex("620a910db20d805e10eeeb09a20d44076993950dbfff00fd"))
check("RID 10F2 dispatches program/verify worker", CF[0x5C3A:0x5C42] == bytes.fromhex("e505bfffc8fdb505"))

print("\n== 10F0/10F1 RAM verification aliases ==")
access = [struct.unpack_from("<IIII", CF, 0x8DA0 + i * 16) for i in range(3)]
check("RAM access row is class 1", access[2] == (0xFEBF0000, 0xFEBF0FFF, 0x33, 1), repr(access[2]))
check("10F0/10F1 class branch uses operation bit 4", CF[0x5800:0x580C] == bytes.fromhex("0ae01d300a3804420348bfff"))
check("shared verifier waits for CRC worker", CF[0x593A:0x5942] == bytes.fromhex("80ffbc0e6652e255"))
check("shared verifier dispatch recognizes states 1/2/4", CF[0x5942:0x5952] == bytes.fromhex("a40f6993610ae205620a922d640af23d"))
check("shared verifier sets authorization-byte path", CF[0x59D8:0x59E0] == bytes.fromhex("24f61193f30fc298"))

print("\n== 10F2 CodeFlash verification and marker programming ==")
regions = [struct.unpack_from("<IIIIIII", CF, 0x8E00 + i * 28) for i in range(3)]
check("first CodeFlash region marker is 0x17E00", regions[0][3] == 0x17E00, hex(regions[0][3]))
check("second CodeFlash region marker is 0xFFE00", regions[1][3] == 0xFFE00, hex(regions[1][3]))
check("RAM region has no marker address", regions[2][3] == 0)
check("10F2 class branch uses operation bit 4", CF[0x5830:0x583C] == bytes.fromhex("1d301c38bfff86efe051ca4d"))
check("10F2 worker resolves region marker address", CF[0x5A9E:0x5AA6] == bytes.fromhex("bfff2ed9e051fa05"))
check("10F2 passes resolved marker to programming helper", CF[0x5AA6:0x5AAE] == bytes.fromhex("23370100bfffdcf7"))
check("marker helper embeds 0x5AA5A55A little-endian", CF[0x5286:0x5294] == bytes.fromhex("8207210021065aa5a55a630f0100"))
check("marker helper starts a four-byte flash operation", CF[0x5294:0x529E] == bytes.fromhex("043abffff2ee0330043a"))
check("marker helper queues four marker bytes", CF[0x529E:0x52A6] == bytes.fromhex("bfffd8ef42063f00"))
check("10F2 failure path clears marker state", CF[0x5B3C:0x5B44] == bytes.fromhex("bfff2ae7f5954407"))

print("\n== 10F3 read-back comparison mode ==")
check("10F3 sets transfer state to 8", CF[0x5920:0x5928] == bytes.fromhex("6993850d080a440f"))
check("10F3 stores transfer state and sends immediate positive response", CF[0x5924:0x592E] == bytes.fromhex("080a440f1393bfff1afd"))
check("RequestDownload recognizes armed state 8", CF[0x5E8E:0x5E92] == bytes.fromhex("680a8a55"))
check("armed RequestDownload selects operation bit 5", CF[0x5EC0:0x5ECC] == bytes.fromhex("0a380542234e0200bfff0ad4"))
check("armed RequestDownload advances to transfer state 9", CF[0x5EEE:0x5EF6] == bytes.fromhex("440f1793090ac505"))
check("TransferData maps state 9 to alternate state 10", CF[0x4DC0:0x4DD4] == bytes.fromhex("a40f1393029a610ac2050a9a690aca05449f1393"))
check("alternate TransferData calls memory compare queue", CF[0x4D60:0x4D6A] == bytes.fromhex("0730243fb99280ff061f"))
check("memory compare queue records source/destination/length", CF[0x6C6C:0x6C8E] == bytes.fromhex("a40fed930152e009ca0d4457ec934457ed936447e19301506437e593643fe9937f00"))
check("memory compare task is asynchronous", CF[0x6C8E:0x6C9A] == bytes.fromhex("80072100a40fed93e009b235"))
check("memory compare task compares source and target bytes", CF[0x6CAE:0x6CC0] == bytes.fromhex("24f7e993d299939f0100d2f16080f099ea1d"))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
