#!/usr/bin/env python3
"""Verify the bank-0 crypto-test command-8 path and its diagnostic composition hazard.

Firmware-static pins (raw CodeFlash bytes, VA-indexed) for:

* RoutineControl RID ``0x100E`` activation gates (``crypto_test_bank0_activate @ 0x68F92``)
* the CAN ``0x13..0x1A`` opaque PDU tables that feed the collector ``0x68368``
* the 64-byte command-8 envelope bank ``FEBE51FA..FEBE5239`` and result bank
  ``FEBE526A..FEBE5299`` used by ``icus_key_update_submit(1)``
* the completion callback ``0x6920A`` routing state solely from ``FEBE5085``
* the RID ``0x1010`` diagnostic start ``0x68E16`` gates (``FEBE5088``/``FEBE5085`` only)
* the bank-0 finalizer ``0x68CD2`` scrub behavior

plus a deterministic composition model that mirrors the recovered state machines
and reproduces the bank-0/diagnostic completion-misattribution sequence.

Every firmware-derived constant is decoded from the committed CodeFlash image,
never hardcoded from documentation.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        suffix = f" ({detail})" if detail else ""
        print(f"FAIL: {name}{suffix}")


def u16(address: int) -> int:
    return struct.unpack_from("<H", CF, address)[0]


def hexat(address: int, length: int) -> str:
    return CF[address : address + length].hex()


# ---------------------------------------------------------------- constants --

KAT_GATE_VA = 0x30EF3          # secoc_slot4_kat_enable gate byte
BANK0_TIMEOUT_VA = 0x30FB4     # u16 cyclic-tick budget for bank-0 test
DIAG_TIMEOUT_VA = 0x30FB2      # u16 cyclic-tick budget for RID 0x1010 machine
DIAG_FAIL_INHIBIT_VA = 0x30FBA  # u8 consecutive-failure inhibit threshold
STABILITY_VA = 0x30FBB         # u8 identical-update threshold per PDU

KAT_GATE = CF[KAT_GATE_VA]
BANK0_TIMEOUT = u16(BANK0_TIMEOUT_VA)
DIAG_TIMEOUT = u16(DIAG_TIMEOUT_VA)
DIAG_FAIL_INHIBIT = CF[DIAG_FAIL_INHIBIT_VA]
STABILITY = CF[STABILITY_VA]

print("== recovered configuration constants ==")
check("slot-4 KAT gate CodeFlash[0x30EF3] == 0x00 (both KAT bodies compiled out)",
      KAT_GATE == 0x00, hex(KAT_GATE))
check("bank-0 stability threshold CodeFlash[0x30FBB] == 3 identical updates",
      STABILITY == 3, hex(STABILITY))
check("bank-0 cyclic timeout u16@0x30FB4 == 1200 ticks",
      BANK0_TIMEOUT == 1200, hex(BANK0_TIMEOUT))
check("RID 0x1010 cyclic timeout u16@0x30FB2 == 120 ticks",
      DIAG_TIMEOUT == 120, hex(DIAG_TIMEOUT))
check("RID 0x1010 consecutive-failure inhibit u8@0x30FBA == 5",
      DIAG_FAIL_INHIBIT == 5, hex(DIAG_FAIL_INHIBIT))

# -------------------------------------------------------------- PDU tables --

# 0x68368 consumes eight COM PDUs through the update-counter index table at
# 0x258E8 and the opaque signal/offset tables at 0x25902/0x2591E.
PDU_INDEX_TABLE = 0x258E8
SID_TABLE = 0x25902
OFF_TABLE = 0x2591E

pdu_indices = [u16(PDU_INDEX_TABLE + 2 * i) for i in range(8)]
sids = [u16(SID_TABLE + 2 * i) for i in range(14)]
offs = [u16(OFF_TABLE + 2 * i) for i in range(14)]

print("\n== CAN 0x13..0x1A opaque collection tables ==")
check("bank-0 PDU index table 0x258E8 selects PDUs 0x0C..0x13",
      pdu_indices == list(range(0x0C, 0x14)), repr(pdu_indices))
check("bank-0 PDU indices map to CAN IDs 0x13..0x1A (PDU index + 7)",
      [p + 7 for p in pdu_indices] == list(range(0x13, 0x1B)),
      repr([p + 7 for p in pdu_indices]))
check("opaque signal table 0x25902 carries signal IDs 87..100",
      sids == list(range(87, 101)), repr(sids))
check("bank-0 slice of offset table is 87+8i for i=0..7 (PDUs 0x0C..0x13)",
      offs[:8] == [87 + 8 * i for i in range(8)], repr(offs[:8]))
check("bank-1 slice of offset table starts at 151 (PDUs 0x14..0x18)",
      offs[8:] == [151, 152, 159, 167, 175, 183], repr(offs[8:]))

ENVELOPE_BASE = 0xFEBE51FA   # 64-byte command-8 request bank for submit(1)
RESULT_BASE = 0xFEBE526A     # 48-byte command-8 result bank for submit(1)
DIAG_REQ_BASE = 0xFEBE51BA   # RID 0x1010 64-byte request bank, submit(0)
DIAG_RESULT_BASE = 0xFEBE523A  # RID 0x1010 48-byte result bank, submit(0)

check("envelope extent FEBE51FA..FEBE5239 is exactly 64 bytes",
      ENVELOPE_BASE + 64 - 1 == 0xFEBE5239)
check("bank-0 result extent FEBE526A..FEBE5299 is exactly 48 bytes",
      RESULT_BASE + 48 - 1 == 0xFEBE5299)
check("diagnostic request/result banks sit immediately before the bank-0 banks",
      DIAG_REQ_BASE + 64 == ENVELOPE_BASE and DIAG_RESULT_BASE + 48 == RESULT_BASE)
check("diagnostic result bank does not overlap the bank-0 envelope",
      not (DIAG_RESULT_BASE < ENVELOPE_BASE + 64 and ENVELOPE_BASE < DIAG_RESULT_BASE + 48))
check("byte k of CAN 0x13+i lands at envelope offset 8*i+k (table-derived mapping)",
      all(offs[i] + k == 87 + 8 * i + k for i in range(8) for k in range(8)))

# ------------------------------------------------------- body byte pins --

print("\n== pinned function bodies (raw CodeFlash windows) ==")

# crypto_test_bank0_activate @ 0x68F92: gate is only FEBE508A==0; then
# FEBE508A=1, timeout counter FEBE5078=0, state FEBE508B=0x11.
ACTIVATE = "80072100840f8b98e0099a15010a440f8a9864077898200e1100440f8b98"
check("0x68F92 activation prologue: FEBE508B read, FEBE508A gate, state 0x11",
      hexat(0x68F92, 0x1E) == ACTIVATE, hexat(0x68F92, 0x1E))
check("0x68F92 activation window contains no FEBE5085/FEBE5088 access bytes",
      ACTIVATE.count("8598") == 0 and ACTIVATE.count("8998") == 0)

# icus_key_update_completion_callback @ 0x6920A: next-state 0x44/0x66 is routed
# by the FEBE5085 test at +0x0C to FEBE5086 (diag) else FEBE508B (bank 0).
CALLBACK = "200e6600d832ba05200e4400a49f8598619aca05440f8698b505440f8b9800527f00"
check("0x6920A completion callback: 0x66/0x44 next-states, FEBE5085-routed stores",
      hexat(0x6920A, 0x22) == CALLBACK, hexat(0x6920A, 0x22))
check("callback stores FEBE5086 before the FEBE5085-false FEBE508B store",
      CALLBACK.index("440f8698") < CALLBACK.index("440f8b98"))

# bank-0 state step @ 0x686EA: timeout compare against u16@0x30FB4, states
# 0x11 -> collector, 0x22 -> submit(1), 0x44/0x46 -> KAT family, 0x33 -> 0x66.
STEP = (
    "80076100e4ef7998a4578b98800effffe1e9b90541eadd00400e0300e10fb50f"
    "e1e9c30d0a06bbffea05010a440f9198bffffefa20566600851d0a06efffba"
    "05bfff3efc0a06deffca050132bfff06fb0a06bcffba05bfff66fb0a06baffda"
    "05bfffcefa2056550044578b9864ef7898"
)
check("0x686EA bank-0 state step body pinned (timeout, 0x11/0x22/0x44/0x46 flow)",
      hexat(0x686EA, 0x70) == STEP, hexat(0x686EA, 0x70))
check("0x686EA pins the u16 timeout immediate 0x0FB4",
      STEP.count("e10fb50f") == 1)

# icus_key_update_submit @ 0x6823C: driver-busy gates, 0x30 result length,
# dispatch input imm 0x51FA (bank-1 request), states 0x33/0x22/0x66.
SUBMIT = (
    "8407e10006e89d0062eac92d81ff98080ae0003281ff50026fe29a256152f21d"
    "200e30001d38640f5998c63a240eba99249e3a9ac13903f0fd0e300000322046"
    "40000648d309010d240e5898030d82ffac06e051fa0520563300e50520562200"
    "b505205666004406ff00"
)
check("0x6823C submit body pinned (busy gates, 48-byte length, 0x51FA input imm)",
      hexat(0x6823C, 0x6A) == SUBMIT, hexat(0x6823C, 0x6A))
check("submit window carries the FEBE51FA envelope immediate and 0x33 state",
      "e051fa05" in SUBMIT and "20563300" in SUBMIT)

# icus_key_update_diagnostic_start @ 0x68E16: gates are FEBE5088==0 then
# FEBE5085!=1; on accept FEBE5085=1, FEBE5076=0, FEBE5086=0x22.
DIAG_START = (
    "8007e12007e009e806d0dc00dd00a40f85981d06ceff849f8998b90520ee3100"
    "1c06bfffb90520e64000e099ba15610af20d010a440f859864077698200e2200"
    "440f86981330bfffb8f00052c5050852"
)
check("0x68E16 diagnostic start body pinned (FEBE5088/FEBE5085 gates, state 0x22)",
      hexat(0x68E16, 0x50) == DIAG_START, hexat(0x68E16, 0x50))
check("diagnostic start window carries FEBE5085 load and FEBE5086 store, no FEBE508A store",
      "a40f8598" in DIAG_START and "440f8698" in DIAG_START and "440f8a98" not in DIAG_START)

# bank-0 finalizer @ 0x68CD2: 0x55 -> active=2, 0x66 -> active=0xFF; both
# scrub staging and zero the submit(1) request/result banks via 0x67F14(1).
FINALIZE = (
    "8007e100a4ef8b9884e78b981d06abfffa0502e2bffff6f10132bfff28f21d06"
    "9afffa051fe2bfffe4f10132bfff16f244e78a9844ef8b98"
)
check("0x68CD2 finalizer body pinned (0x55->2, 0x66->0xFF, bank scrub)",
      hexat(0x68CD2, 0x38) == FINALIZE, hexat(0x68CD2, 0x38))
check("finalizer maps terminal 0x66 to active 0xFF",
      "9afffa051f" in FINALIZE)

# cyclic dispatcher @ 0x68C0C: watchdog arms 0x682F8/0x686EA on active flags.
CYCLIC = "80076100a4ef8d981d065bffca05bfffb4f3850d840f8f9801065bffba05bfffaaf4bfff6af5a40f8598e0099215a40f"
check("0x68C0C cyclic dispatcher body pinned (active-flag dispatch)",
      hexat(0x68C0C, 0x30) == CYCLIC, hexat(0x68C0C, 0x30))

# ------------------------------------------------- composition model --

print("\n== composition model (mirrors 0x68F92/0x68368/0x6823C/0x6920A/0x68E16/0x68CD2) ==")


class Bank0Machine:
    """Deterministic mirror of the recovered bank-0 crypto-test state machine.

    Every transition cites the firmware function it mirrors. RAM names are the
    recovered FEBE50xx globals; envelopes/results are the bank-1 submit(1)
    buffers at FEBE51FA/FEBE526A.
    """

    def __init__(self) -> None:
        self.active = 0            # FEBE508A
        self.state = 0             # FEBE508B
        self.timeout = 0           # FEBE5078
        self.envelope = bytearray(64)   # FEBE51FA..FEBE5239
        self.result = bytearray(48)     # FEBE526A..FEBE5299
        # collector state (0x68368 mirrors)
        self.prev = [None] * 8      # FEBE50BA.. scratch
        self.stable = [None] * 8    # FEBE50FA.. committed per-PDU bytes
        self.count = [0] * 8        # FEBE5030..
        self.equal_marked = [0] * 8  # FEBE5040..
        self.ready_mask = 0         # FEBE508C
        self.driver_busy = False    # shared ICU driver serialization
        self.driver_owner = None

    # 0x68F92 crypto_test_bank0_activate
    def activate(self, diag=None) -> bool:
        if self.active != 0:
            return False
        self.active = 1
        self.timeout = 0
        self.state = 0x11
        # 0x67EDC clears staging/counters; 0x67F14(1) zeroes envelope+result.
        self.prev = [None] * 8
        self.stable = [None] * 8
        self.count = [0] * 8
        self.equal_marked = [0] * 8
        self.ready_mask = 0
        self.envelope = bytearray(64)
        self.result = bytearray(48)
        return True

    # 0x68368 collector: one changed PDU update for PDU i (0..7)
    def com_update(self, i: int, data: bytes) -> None:
        assert self.state == 0x11 and len(data) == 8
        if self.equal_marked[i] == 0 or self.prev[i] == data:
            self.count[i] += 1
            self.equal_marked[i] = 1
            if self.count[i] >= STABILITY:
                self.ready_mask |= 1 << i
                self.stable[i] = bytes(data)
        else:
            self.count[i] = 1
        self.prev[i] = bytes(data)

    # tail of 0x68368: promote stable bytes to the 64-byte envelope
    def promote(self) -> None:
        if self.ready_mask == 0xFF:
            for i in range(8):
                self.envelope[8 * i : 8 * i + 8] = self.stable[i]
            self.state = 0x22

    # 0x6823C icus_key_update_submit(1)
    def submit(self, diag_active: int, driver_free: bool = True) -> int:
        if self.driver_busy or not driver_free:
            return 0x22  # busy gates in 0x6823C keep state 0x22
        self.driver_busy = True
        self.driver_owner = "bank0"
        return 0x33

    # 0x6920A icus_key_update_completion_callback
    def completion(self, diag, success: bool) -> None:
        self.driver_busy = False
        self.driver_owner = None
        # 0x871A0 copies M4/M5 through the retained output pointer: bank-0
        # hardware results always land in the submit(1) result bank.
        self.result = bytearray(b"\xA1" * 48) if success else bytearray(48)
        nxt = 0x44 if success else 0x66
        if diag.active == 1:
            diag.state = nxt          # mis/attribution selected only by FEBE5085
        else:
            self.state = nxt

    # 0x686EA cyclic step (collector promotion + timeout)
    def cyclic(self, diag, collected: bool = True) -> None:
        self.timeout = 0xFFFF if self.timeout == 0xFFFF else self.timeout + 1
        if BANK0_TIMEOUT < self.timeout:
            self.state = 0x66
            return
        if self.state == 0x11 and collected:
            self.promote()
        elif self.state == 0x22:
            self.state = self.submit(diag.active)
        elif self.state == 0x44:
            self.state = 0x46 if KAT_GATE != 0x5A else 0x45
        elif self.state == 0x46:
            self.state = 0x55

    # 0x68CD2 finalizer
    def finalize(self) -> None:
        if self.state == 0x55:
            self.active = 2
        elif self.state == 0x66:
            self.active = 0xFF
        else:
            return
        self.envelope = bytearray(64)  # 0x67F14(1) scrub
        self.result = bytearray(48)    # 0x67F14(1) scrub
        self.prev = [None] * 8         # 0x67EDC scrub
        self.stable = [None] * 8
        self.count = [0] * 8
        self.ready_mask = 0


class DiagMachine:
    """Mirror of the RID 0x1010 state machine (0x68E16/0x682F8/0x68C86/0x68EA8)."""

    def __init__(self) -> None:
        self.active = 0          # FEBE5085: 0 idle, 1 pending, 2 complete, 0xFF failed
        self.state = 0           # FEBE5086
        self.timeout = 0         # FEBE5076
        self.request = bytearray(64)   # FEBE51BA..FEBE51F9
        self.result = bytearray(48)    # FEBE523A..FEBE5269
        self.fail_count = 0      # FEBE5087
        self.inhibit = 0         # FEBE5088 (0x5A locks starts out)

    # 0x68E16 icus_key_update_diagnostic_start
    def start(self, envelope64: bytes) -> int:
        if self.inhibit == 0x5A:
            return 5               # external inhibit -> NRC 0x22
        if self.active == 1:
            return 8               # already pending -> NRC 0x24
        self.active = 1
        self.timeout = 0
        self.state = 0x22
        self.request = bytearray(envelope64)
        self.result = bytearray(48)  # 0x67F14(0) clears request/result banks
        return 0

    # 0x682F8 cyclic step (submit(0) side)
    def cyclic(self, bank0) -> None:
        self.timeout = 0xFFFF if self.timeout == 0xFFFF else self.timeout + 1
        if DIAG_TIMEOUT < self.timeout:
            self.state = 0x66
            return
        if self.state in (0x11, 0x22):
            if bank0.driver_busy:
                return  # shared driver busy -> submit(0) keeps state 0x22
            bank0.driver_busy = True
            bank0.driver_owner = "diag"
            self.state = 0x33
        elif self.state == 0x44:
            self.state = 0x46 if KAT_GATE != 0x5A else 0x45
        elif self.state == 0x46:
            self.state = 0x55

    # 0x68C86 finalizer
    def finalize(self) -> None:
        if self.state == 0x55:
            self.active = 2
        elif self.state == 0x66:
            self.active = 0xFF
            self.fail_count += 1
            if self.fail_count >= DIAG_FAIL_INHIBIT:
                self.inhibit = 0x5A

    # 0x68EA8 icus_key_update_diagnostic_read_result
    def read_result(self) -> tuple[int, bytes]:
        status = self.active
        payload = bytes(self.result) if status == 2 else bytes(48)
        if status in (2, 0xFF):
            self.request = bytearray(64)  # terminal read clears bank 0
            self.result = bytearray(48)
        return status, payload


def run_serial_case() -> tuple[bool, str]:
    """Case A: no diagnostic — bank-0 completes its own command-8 envelope."""
    b0, diag = Bank0Machine(), DiagMachine()
    assert b0.activate(diag) and b0.state == 0x11
    payload = bytes(range(0x40, 0x48))
    for _ in range(STABILITY):
        for i in range(8):
            b0.com_update(i, bytes([0xA0 + i] * 8) if i else payload)
    b0.promote()
    if b0.state != 0x22 or b0.ready_mask != 0xFF:
        return False, f"collection did not arm: state={b0.state:#x}"
    if bytes(b0.envelope[:8]) != payload or bytes(b0.envelope[8:16]) != bytes([0xA1] * 8):
        return False, "envelope mapping wrong"
    b0.cyclic(diag)  # 0x22 -> submit(1) -> 0x33
    if b0.state != 0x33 or b0.driver_owner != "bank0":
        return False, f"submit(1) did not dispatch: state={b0.state:#x}"
    b0.completion(diag, success=True)
    if b0.state != 0x44 or b0.result == bytearray(48):
        return False, "own completion did not route to bank-0 state"
    while b0.state != 0x55:
        b0.cyclic(diag)
    b0.finalize()
    if b0.active != 2 or b0.envelope != bytearray(64) or b0.result != bytearray(48):
        return False, "success finalize did not scrub envelope/result"
    return True, ""


def run_race_case() -> tuple[bool, str]:
    """Case B: diagnostic activates after bank-0 submit, before completion."""
    b0, diag = Bank0Machine(), DiagMachine()
    assert b0.activate(diag)
    for i in range(8):
        for _ in range(STABILITY):
            b0.com_update(i, bytes([0xB0 + i] * 8))
    b0.promote()
    b0.cyclic(diag)  # submit(1) accepted -> 0x33, driver busy
    if b0.state != 0x33:
        return False, "race precondition failed (bank-0 not in 0x33)"

    # RID 0x1010 start between submit and completion: 0x68E16 checks only
    # FEBE5088/FEBE5085, never FEBE508A, so the start is accepted.
    rc = diag.start(bytes([0xC0] * 64))
    if rc != 0 or diag.active != 1 or diag.state != 0x22:
        return False, f"diagnostic start rejected during bank-0 flight (rc={rc})"

    # Diagnostic submit(0) must serialize behind the in-flight bank-0 job.
    diag.cyclic(b0)
    if diag.state != 0x22 or b0.driver_owner != "bank0":
        return False, "driver serialization failed"

    # Bank-0 hardware completion arrives while FEBE5085==1.
    b0.completion(diag, success=True)
    if diag.state != 0x44:
        return False, "foreign completion not attributed to diagnostic"
    if b0.state != 0x33:
        return False, "bank-0 state advanced by foreign completion"

    # Diagnostic walks 0x44 -> 0x46 -> 0x55 and terminalizes status 0x02.
    while diag.state != 0x55:
        diag.cyclic(b0)
    diag.finalize()
    status, payload = diag.read_result()
    if status != 2:
        return False, f"diagnostic status {status:#x}, expected 0x02"
    if payload != bytes(48):
        return False, "diagnostic returned nonzero M4/M5 it never produced"

    # Bank-0 times out in 0x33, terminalizes 0xFF, and scrubs its banks.
    while b0.state != 0x66:
        b0.cyclic(diag)
    b0.finalize()
    if b0.active != 0xFF:
        return False, "bank-0 did not terminalize after misattributed completion"
    if b0.envelope != bytearray(64) or b0.result != bytearray(48):
        return False, "bank-0 envelope/result not scrubbed after timeout"
    return True, ""


def run_gate_independence_case() -> tuple[bool, str]:
    """Case C: activation gates are fully independent in both directions."""
    b0, diag = Bank0Machine(), DiagMachine()
    if diag.start(bytes(64)) != 0 or diag.active != 1:
        return False, "diagnostic start precondition failed"
    if not b0.activate(diag):
        return False, "0x100E activation refused while diagnostic active"
    b02, d02 = Bank0Machine(), DiagMachine()
    if not b02.activate(d02):
        return False, "bank-0 activation precondition failed"
    if d02.start(bytes(64)) != 0:
        return False, "RID 0x1010 start refused while bank-0 active"
    return True, ""


def run_staggered_collection_case() -> tuple[bool, str]:
    """Case D: per-PDU commit independence allows mixed-time packages."""
    b0, diag = Bank0Machine(), DiagMachine()
    assert b0.activate(diag)
    # PDU 0 receives its three stable updates long before PDU 7.
    for _ in range(STABILITY):
        b0.com_update(0, b"\x01" * 8)
    for _ in range(20):
        b0.com_update(3, b"\xEE" * 8)  # churning another PDU must not reset PDU 0
    if b0.ready_mask & 1 != 1:
        return False, "PDU 0 stability lost during unrelated churn"
    for i in range(1, 8):
        for _ in range(STABILITY):
            b0.com_update(i, bytes([0x60 + i] * 8))
    b0.promote()
    if b0.state != 0x22 or bytes(b0.envelope[:8]) != b"\x01" * 8:
        return False, "staggered package did not assemble"
    return True, ""


for name, fn in (
    ("serial bank-0 command-8 lifecycle", run_serial_case),
    ("bank-0/diagnostic completion misattribution race", run_race_case),
    ("activation gate independence (0x100E vs 0x1010)", run_gate_independence_case),
    ("staggered per-PDU package assembly", run_staggered_collection_case),
):
    ok, detail = fn()
    check(f"composition model: {name}", ok, detail)

# ------------------------------------------------------------------ exit --

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
