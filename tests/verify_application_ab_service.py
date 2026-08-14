#!/usr/bin/env python3
"""Verify the application SID 0xAB event-record service from firmware bytes.

The service is distinct from SID 0xBA and from the separate internal routine
callback table. This suite pins the 0xAB subfunctions/event-record tables, the
complete configured event callback closure, and the adjacent 0xBA operation-F1
boundary so service ownership cannot shift again.
"""
from pathlib import Path
import struct
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()

passed = 0
failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        mark = "PASS"
    else:
        failed += 1
        mark = "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"[{mark}] {name}{suffix}")


def decode_branch(addr):
    """Decode RH850 jarl/jr with the SLEIGH op1616=0 constraint."""
    if addr + 4 > len(CF):
        return None
    w0, w1 = struct.unpack_from("<HH", CF, addr)
    if ((w0 >> 6) & 0x1F) != 0x1E or (w1 & 1):
        return None
    reg2 = (w0 >> 11) & 0x1F
    disp_hi = w0 & 0x3F
    if disp_hi & 0x20:
        disp_hi -= 0x40
    return ("jarl" if reg2 else "jr", ((disp_hi << 16) | w1) + addr)


def direct_targets(start, end):
    return {
        decoded[1]
        for addr in range(start, end, 2)
        if (decoded := decode_branch(addr)) is not None
        and 0 < decoded[1] < len(CF)
    }


print("== SID 0xAB configuration ==")
service = 0x25F90
check("SID 0xAB runtime service byte", CF[service + 0x10] == 0xAB)
check("SID 0xAB has no direct service callback", struct.unpack_from("<I", CF, service)[0] == 0)
check("SID 0xAB subfunction table is 0x25CD0", struct.unpack_from("<I", CF, service + 0x0C)[0] == 0x25CD0)
check("SID 0xAB has three subfunctions", CF[service + 0x14] == 3)

ba_service = 0x25FA8
check("SID 0xBA runtime service byte", CF[ba_service + 0x10] == 0xBA)
check("SID 0xBA direct callback is 0x8D344", struct.unpack_from("<I", CF, ba_service)[0] == 0x8D344)

selector_table = 0x25CD0
expected_selectors = [
    (0x01, 0x96A34, 0x25B78),
    (0x02, 0x96A56, 0x25B7A),
    (0x03, 0x96A78, 0x25B7C),
]
for index, (selector, callback, policy) in enumerate(expected_selectors):
    off = selector_table + index * 0x10
    actual = (
        CF[off + 0x0C],
        struct.unpack_from("<I", CF, off)[0],
        struct.unpack_from("<I", CF, off + 8)[0],
    )
    check(
        f"selector 0x{selector:02X} callback/policy",
        actual == (selector, callback, policy),
        repr(actual),
    )

print("\n== SID 0xBA operation-F1 handoff ==")
check("operation dispatch table has ten entries", struct.unpack_from("<I", CF, 0x28094)[0] == 10)
f1 = CF[0x28098:0x280A8]
check(
    "operation F1 record",
    f1[:4] == bytes((0xF1, 0x06, 0x00, 0x0C))
    and struct.unpack_from("<I", f1, 4)[0] == 0
    and struct.unpack_from("<I", f1, 8)[0] == 0x34B74
    and struct.unpack_from("<I", f1, 12)[0] == 0x34B9A,
    f1.hex(),
)
# The literal lives in the shared string bank; the start callback passes its address.
check("F1 JTEKM token exists in firmware", CF.find(b"JTEKM") >= 0)
check(
    "F1 start/result branch only through their two thunks and comparator",
    direct_targets(0x34B74, 0x34BA8) == {0x3485A, 0xFE024, 0xFE150},
    repr(sorted(hex(x) for x in direct_targets(0x34B74, 0x34BA8))),
)

print("\n== event-record catalogue and active set ==")
records = []
for index in range(64):
    off = 0x2AD10 + index * 8
    records.append(
        (
            struct.unpack_from("<I", CF, off)[0],
            CF[off + 4],
            CF[off + 5],
        )
    )
nonzero = [(i, row) for i, row in enumerate(records) if row[0] != 0]
check("event catalogue has 64 slots", len(records) == 64)
check("event catalogue has 51 populated slots", len(nonzero) == 51, str(len(nonzero)))
check("event catalogue populated span is 1..51", [i for i, _ in nonzero] == list(range(1, 52)))
check("event catalogue first ID", records[1] == (0x00080455, 0x11, 0x00), repr(records[1]))
check("event catalogue last ID", records[51] == (0x0010F022, 0x11, 0x00), repr(records[51]))

print("\n== configured indirect-callback closure ==")
# Selector 3 type 0x11 reaches this 75-record snapshot descriptor table.
snapshot_callbacks = []
for index in range(0x4B):
    off = 0x2A504 + index * 0x18
    snapshot_callbacks.append(struct.unpack_from("<I", CF, off + 0x0C)[0])
nonzero_snapshot_callbacks = {value for value in snapshot_callbacks if value}
check("snapshot table has 75 records", len(snapshot_callbacks) == 0x4B)
check("snapshot table resolves to 35 non-null callbacks",
      len(nonzero_snapshot_callbacks) == 35,
      str(len(nonzero_snapshot_callbacks)))
check("snapshot callbacks stay in recovered event-data block",
      min(nonzero_snapshot_callbacks) == 0x54C64
      and max(nonzero_snapshot_callbacks) == 0x551C2)

# Non-type-0x11 selector-3 records reach this six-entry detail table.
detail_data_callbacks = set()
detail_gate_callbacks = set()
for index in range(6):
    off = 0x2AC0C + index * 0x10
    detail_data_callbacks.add(struct.unpack_from("<I", CF, off + 4)[0])
    detail_gate_callbacks.add(struct.unpack_from("<I", CF, off + 8)[0])
check("detail table resolves six data callbacks",
      detail_data_callbacks == {0x551CA, 0x55204, 0x5522E, 0x5524E, 0x5525E, 0x5526E})
check("detail table has no configured gate callbacks", detail_gate_callbacks == {0})

callback_targets = direct_targets(0x54C64, 0x55280)
check(
    "resolved event callbacks have exact direct-target closure",
    callback_targets == {0x524B6, 0x5258C, 0x5260A, 0x694CC, 0x694E4, 0x6951C, 0x6F080},
    repr(sorted(hex(x) for x in callback_targets)),
)
for displacement, address in ((0x5AE8, 0xFEBF02E8), (0x5AF8, 0xFEBF02F8)):
    hit = CF.find(struct.pack("<h", displacement), 0x54C64, 0x55280)
    check(f"event callbacks do not use GP displacement for 0x{address:08X}", hit < 0, hex(hit))

print("\n== separation from internal routine callback table ==")
rid_lookup_callers = []
for addr in range(0, len(CF) - 3, 2):
    decoded = decode_branch(addr)
    if decoded is not None and decoded[1] == 0x8D3CC:
        rid_lookup_callers.append(addr)
check("RID lookup has one direct caller", rid_lookup_callers == [0x8A50C], repr(rid_lookup_callers))
check("RID lookup has no function-pointer literal", CF.find(struct.pack("<I", 0x8D3CC)) < 0)
check("SID 0x31 direct callback is configured RoutineControl 0x95DCE", struct.unpack_from("<I", CF, 0x25F00)[0] == 0x95DCE)

sensitive_targets = {
    0x865D4, 0x853EE, 0x852B0, 0x8496C,
    0x72F58, 0x72F84,
    0x84850, 0x84874, 0x8488C, 0x880DC,
    0x88B6A, 0x88B9C, 0x88BA8, 0x88556, 0x88080,
    0x897F4, 0x8C7BC, 0x8C7F6, 0x8FDCA, 0x8F242,
    0x92FEE, 0x900FC,
}
ab_targets = set()
for start, end in ((0x8CF84, 0x8D0F0), (0x4F8BA, 0x4FC00)):
    ab_targets |= direct_targets(start, end)
ab_targets |= callback_targets
check("closed 0xAB event graph has no direct sensitive targets",
      not (ab_targets & sensitive_targets),
      repr(sorted(hex(x) for x in ab_targets & sensitive_targets)))
ba_targets = direct_targets(0x34B74, 0x34BA8)
check("bounded 0xBA operation-F1 path has no direct sensitive targets",
      not (ba_targets & sensitive_targets),
      repr(sorted(hex(x) for x in ba_targets & sensitive_targets)))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    sys.exit(1)
