#!/usr/bin/env python3
"""Independent raw-CodeFlash checks for FIRMWARE_ARCHITECTURE.md.

No Ghidra project, sibling checkout, or hardware manual is required. The test
checks firmware landmarks and channel numbers; peripheral names are documented
separately from the Renesas hardware manual.
"""
from collections import Counter
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


def u16(offset):
    return struct.unpack_from("<H", CF, offset)[0]


def u32(offset):
    return struct.unpack_from("<I", CF, offset)[0]


print("== boot/application partition and handoff ==")
check("CodeFlash image is exactly 1 MiB", len(CF) == 0x100000, hex(len(CF)))
check("reset vector syncp+jmp targets 0x1B0",
      CF[0:8] == bytes.fromhex("1f00e006b0010000"), CF[0:8].hex())
check("boot startup sets SP=0xFEBE8000",
      CF[0x1EC:0x1F2] == bytes.fromhex("23060080befe"))
check("boot startup sets GP=0xFEBF9800",
      CF[0x1F2:0x1F8] == bytes.fromhex("24060098bffe"))
check("boot startup sets TP=0x869C",
      CF[0x1F8:0x1FE] == bytes.fromhex("25069c860000"))
check("application entry pointer is at 0xFFDB8 and equals 0x20880",
      u32(0xFFDB8) == 0x20880, hex(u32(0xFFDB8)))
check("boot handoff reads pointer with GP displacement 0x1FFB",
      CF[0x13F2:0x13F8] == bytes.fromhex("8007890bfb1f"), CF[0x13F2:0x13F8].hex())
check("boot handoff performs an indirect call",
      CF[0x13F8:0x1400] == bytes.fromhex("630f010001e8fdc7"), CF[0x13F8:0x1400].hex())
check("application entry immediately calls startup coordinator 0x62758",
      CF[0x20880:0x20888] == bytes.fromhex("8007210084ffd41e"), CF[0x20880:0x20888].hex())

print("\n== application CPU context and scheduler ==")
check("CPU context initializer loads INTBP value 0x20200",
      CF[0x70524:0x7052A] == bytes.fromhex("2b0600020200"))
check("CPU context initializer writes INTBP",
      CF[0x7052C:0x70530] == bytes.fromhex("eb272008"))
check("CPU context initializer loads EBASE value 0x20000",
      CF[0x70530:0x70536] == bytes.fromhex("2b0600000200"))
check("CPU context initializer writes EBASE",
      CF[0x70538:0x7053C] == bytes.fromhex("eb1f2008"))
check("application GP/TP/SP constants are contiguous",
      CF[0x7053C:0x7054E] == bytes.fromhex(
          "240600b8befe2506e43e020023060020befe"))
check("foreground loop polls then clears EIC136.EIRF",
      CF[0x64FD0:0x64FDA] == bytes.fromhex("c0e711b1e2fdc0a711b1"),
      CF[0x64FD0:0x64FDA].hex())
check("foreground loop calls NvM/CSM task wrapper 0x65F5C",
      CF[0x64FFA:0x64FFE] == bytes.fromhex("80ff620f"))
check("foreground loop calls main application group 0x65750",
      CF[0x65002:0x65006] == bytes.fromhex("80ff4e07"))
check("foreground loop calls SecOC-NvM cyclic task 0x65C60",
      CF[0x6500A:0x6500E] == bytes.fromhex("80ff560c"))

print("\n== boot interrupt dispatch ==")
BOOT_IRQ = struct.Struct("<II")
boot_irq = [BOOT_IRQ.unpack_from(CF, 0x869C + i * BOOT_IRQ.size) for i in range(8)]
expected_boot_irq = [
    (0x1087, 0x1E44),
    (0x10B8, 0x1E50),
    (0x10B9, 0x1E5E),
    (0x10BB, 0x1E6C),
    (0x10BC, 0x1E7A),
    (0x10C0, 0x1E88),
    (0x10C1, 0x1E96),
    (0xFFFFFFFF, 0x1EA4),
]
check("boot EIINT dispatch table has eight records", len(boot_irq) == 8)
check("boot EIINT source/handler records match", boot_irq == expected_boot_irq, repr(boot_irq))
check("boot direct EIINT prologue calls dispatcher 0x748",
      CF[0x130:0x136] == bytes.fromhex("ff0218060000"), CF[0x130:0x136].hex())
check("boot fatal vector points to 0x1E36",
      CF[0xE0:0xE8] == bytes.fromhex("1f00e006361e0000"))

print("\n== application vectors and EIINT pointer table ==")
check("application direct-vector base has reset jump to address 0",
      CF[0x20000:0x20008] == bytes.fromhex("1f00e00600000000"))
check("application vector 0x90 points to 0x64B3E",
      CF[0x20090:0x20098] == bytes.fromhex("1f00e0063e4b0600"))
app_vectors = [u32(0x20200 + 4 * channel) for channel in range(384)]
counts = Counter(app_vectors)
check("application INTBP region has 384 entries", len(app_vectors) == 384)
check("application default handler occupies 373 entries",
      counts[0x61D88] == 373, repr(counts))
expected_special = {
    8: 0x70A54,
    133: 0x70320,
    134: 0x703CA,
    135: 0x70476,
    187: 0x6506A,
    188: 0x65028,
    292: 0x650AC,
    293: 0x650EE,
    379: 0x65130,
    382: 0x400040,
    383: 0x400040,
}
check("all non-default application vector entries match",
      {i: value for i, value in enumerate(app_vectors) if value != 0x61D88}
      == expected_special)
check("TAUJ0 channel 3 / EIINT136 remains on default pointer",
      app_vectors[136] == 0x61D88, hex(app_vectors[136]))
check("CAN1 receive/transmit channels are adjacent 187/188",
      app_vectors[187:189] == [0x6506A, 0x65028])
check("manual-reserved channels 292/293 retain explicit wrappers",
      app_vectors[292:294] == [0x650AC, 0x650EE])
check("channel 292/293 adapters have identical guarded callback bodies",
      CF[0x87610:0x87636] == CF[0x87636:0x8765C])
check("crypto adapters read callback/complement GP+0x5994/+0x5998",
      CF[0x87610:0x8761C] == bytes.fromhex("8007610024ef9559249f9959"))
check("crypto adapters set GP+0x5991 on complement failure",
      CF[0x8762C:0x87632] == bytes.fromhex("010a440f9159"))
check("driver interrupt control accesses EIC292/EIC293 short addresses",
      CF[0x89140:0x89154] == bytes.fromhex("e00f49b26132aa0dc10e7fff600f48b2e00f4bb2"))
check("same driver family writes ICU-S command SFR FFC5D000",
      CF[0x8990C:0x89912] == bytes.fromhex("80070f08a08b"))
check("flash completion channel 379 points to 0x65130",
      app_vectors[379] == 0x65130)
check("tail channels 382/383 contain unresolved pointer 0x00400040",
      app_vectors[382:] == [0x400040, 0x400040])

print("\n== application RSCFD register map ==")
RSCFD_RECORD = struct.Struct("<29I")
rscfd = [RSCFD_RECORD.unpack_from(CF, 0x22FE0 + i * RSCFD_RECORD.size) for i in range(3)]
check("RSCFD register map has three 0x74-byte records", RSCFD_RECORD.size == 0x74 and len(rscfd) == 3)
check("channel records begin with channel-specific control registers",
      [row[0] for row in rscfd] == [0xFFD20008, 0xFFD20018, 0xFFD20028])
check("channel records select FIFO RAM 0xFFD23400/3580/3700",
      [row[18] for row in rscfd] == [0xFFD23400, 0xFFD23580, 0xFFD23700])
check("channel records select Tx RAM 0xFFD24000/4200/4400",
      [row[19] for row in rscfd] == [0xFFD24000, 0xFFD24200, 0xFFD24400])

print("\n== application CAN1 acceptance and routing ==")
normal_ids = [
    0x2E4, 0x3B0, 0x63B, 0x624, 0x63D, 0x00F, 0x013, 0x014,
    0x015, 0x016, 0x017, 0x018, 0x019, 0x01A, 0x01B, 0x01C,
    0x01D, 0x01E, 0x01F, 0x191, 0x131, 0x2FD, 0x0D0, 0x3BF,
    0x127, 0x115, 0x1C5, 0x294, 0x51E, 0x132, 0x611, 0x2D1,
    0x675, 0x2E8, 0x025, 0x423, 0x0AA, 0x101, 0x0D5, 0x13B,
    0x090, 0x0D7, 0x64F, 0x020, 0x403, 0x490, 0x1DA,
]
normal_lengths = [8] * 47
for index in (34, 40, 41):
    normal_lengths[index] = 0x20
normal_lengths[35] = 1
normal_lengths[45] = 1
normal_descriptors = [struct.unpack_from("<II", CF, 0x22018 + 8 * i) for i in range(47)]
software_ids = normal_ids.copy()
for index in (34, 40, 41):
    software_ids[index] |= 0x40000000
expected_descriptors = list(zip(software_ids, normal_lengths))
check("47 normal RX descriptors match exact ID/length sequence",
      normal_descriptors == expected_descriptors)

RULE = struct.Struct("<IIII")
rules = [RULE.unpack_from(CF, 0x231A0 + RULE.size * i) for i in range(52)]
acceptance_ids = [row[0] for row in rules[:51]]
check("acceptance table has 51 rules plus terminator", len(rules) == 52)
check("normal hardware-rule IDs mirror descriptors without software CAN-FD marker",
      acceptance_ids[:47] == normal_ids)
check("diagnostic/special acceptance tail is 7A1/777/7A0/7F7",
      acceptance_ids[47:] == [0x7A1, 0x777, 0x7A0, 0x7F7],
      repr(acceptance_ids[47:]))
check("acceptance table terminator is exact",
      rules[51] == (0xFFFFFFFF, 0, 0, 0), repr(rules[51]))
check("normal rule hardware labels run from 9 through 55",
      [row[1] for row in rules[:47]] == [(i + 9) << 16 for i in range(47)])
check("normal rule route words are 2",
      all(row[2:] == (2, 0) for row in rules[:47]))
check("diagnostic rules use expected route classes",
      [row[2] for row in rules[47:51]] == [0x2000, 0x2000, 0x2000, 2])
check("hardware-to-software queue map contains 51 zero queue indexes",
      CF[0x219AC:0x219AC + 51] == bytes(51))
check("receive callback masks split normal/diagnostic/special classes",
      CF[0x219EC:0x219EC + 51] == bytes([1] * 47 + [4, 4, 4, 0x20]))
check("diagnostic software ID table is 7A1/777/7A0",
      [u32(0x21FC8 + 8 * i) for i in range(3)] == [0x7A1, 0x777, 0x7A0])

for can_id, index, pdu_id in [(0x2E4, 0, 6), (0x0F, 5, 11), (0x131, 20, 26)]:
    check(f"CAN {can_id:#x} has acceptance index {index}", acceptance_ids[index] == can_id)
    check(f"CAN {can_id:#x} maps by 6+n to application PDU {pdu_id}", 6 + index == pdu_id)
check("CAN 0x344 is absent from application RX acceptance rules", 0x344 not in acceptance_ids)

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
