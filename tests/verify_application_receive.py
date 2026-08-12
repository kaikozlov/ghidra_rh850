#!/usr/bin/env python3
"""Independent raw-CodeFlash checks for docs/communications/application-rx.md.

Recovered extraction rows are gated against the companion evidence artifact
`data/application_rx_signal_evidence.csv` using CodeFlash bytes (body hashes,
call-site windows, movea/mov immediates, GP-relative destinations). The test
does not reimport the generator's overlay dict.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CSV_PATH = REPO / "data" / "application_rx_map.csv"
EVIDENCE_PATH = REPO / "data" / "application_rx_signal_evidence.csv"
GEN = REPO / "tools" / "generate_application_rx_map.py"

ACCEPTANCE = 0x231A0
RX_DESC = 0x22018
COM_PDU = 0x2273C
BUF_OFF = 0x228E4
SIG2PDU = 0x224E4
SIGPROP = 0x223B8
SECOC_RECORDS = 0x25970
SECOC_RECORD_SIZE = 0x50
OPAQUE_SID_TABLE = 0x25902
OPAQUE_OFF_TABLE = 0x2591E

GP = 0xFEBEB800
COM_BUF_RAM = 0xFEBE4A49
VALIDITY_RAM = 0xFEBE52CC
UPDATE_COUNTER_RAM = 0xFEBE532C
RX_INDICATION = 0x7C640
RECEIVE_SIGNAL = 0x7C03E

PDU = struct.Struct("<HBBHBB")
RULE = struct.Struct("<IIII")
DESC = struct.Struct("<II")

NORMAL_IDS = [
    0x2E4, 0x3B0, 0x63B, 0x624, 0x63D, 0x00F, 0x013, 0x014,
    0x015, 0x016, 0x017, 0x018, 0x019, 0x01A, 0x01B, 0x01C,
    0x01D, 0x01E, 0x01F, 0x191, 0x131, 0x2FD, 0x0D0, 0x3BF,
    0x127, 0x115, 0x1C5, 0x294, 0x51E, 0x132, 0x611, 0x2D1,
    0x675, 0x2E8, 0x025, 0x423, 0x0AA, 0x101, 0x0D5, 0x13B,
    0x090, 0x0D7, 0x64F, 0x020, 0x403, 0x490, 0x1DA,
]
DIAG_CAN_IDS = [0x7A1, 0x777, 0x7A0, 0x7F7]

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def u16(offset: int) -> int:
    return struct.unpack_from("<H", CF, offset)[0]


def u32(offset: int) -> int:
    return struct.unpack_from("<I", CF, offset)[0]


def sha256_region(offset: int, size: int) -> str:
    return hashlib.sha256(CF[offset:offset + size]).hexdigest()


def secoc_can_ids() -> set[int]:
    return {u16(SECOC_RECORDS + i * SECOC_RECORD_SIZE + 0x0A) for i in range(6)}


_MOVEA_R0_RD = {6: 0x36, 7: 0x3E, 8: 0x46}


def movea_r0_rd(imm: int, rd: int) -> bytes:
    """Encoding for movea imm16, r0, rd observed in generated unpackers."""
    return bytes([0x20, _MOVEA_R0_RD[rd], imm & 0xFF, (imm >> 8) & 0xFF])


def movea_gp_r1(imm16: int) -> bytes:
    """Encoding for movea imm16, gp, r1 (imm16 is the raw 16-bit field)."""
    return bytes([0x24, 0x0E, imm16 & 0xFF, (imm16 >> 8) & 0xFF])


print("== raw acceptance / descriptor census ==")
descs = [DESC.unpack_from(CF, RX_DESC + DESC.size * i) for i in range(47)]
rules = [RULE.unpack_from(CF, ACCEPTANCE + RULE.size * i) for i in range(52)]
acceptance_ids = [row[0] for row in rules[:51]]
check("47 normal RX descriptors present", len(descs) == 47)
check("acceptance table has 51 rules plus terminator",
      rules[51] == (0xFFFFFFFF, 0, 0, 0))
check("normal hardware-rule IDs match documented sequence",
      acceptance_ids[:47] == NORMAL_IDS)
check("diagnostic/special acceptance tail is 7A1/777/7A0/7F7",
      acceptance_ids[47:] == DIAG_CAN_IDS)
check("CAN 0x344 is absent from application RX acceptance rules",
      0x344 not in acceptance_ids)
check("CAN 0x344 is absent from normal software descriptors",
      0x344 not in [soft & 0x7FF for soft, _ in descs]
      and 0x40000344 not in [soft for soft, _ in descs])

print("\n== COM PDU / signal map cardinalities ==")
pdus = [PDU.unpack_from(CF, COM_PDU + PDU.size * i) for i in range(53)]
offs = [u16(BUF_OFF + 2 * i) for i in range(53)]
s2p = [u16(SIG2PDU + 2 * i) for i in range(300)]
props = list(CF[SIGPROP:SIGPROP + 300])
check("53 COM PDU descriptors split as six Tx plus 47 Rx", 53 - 6 == 47)
check("Rx COM flags are all 0x0C", all(row[5] == 0x0C for row in pdus[6:]))
check("Rx buffer offsets are contiguous by COM length",
      offs[6:] == [offs[6] + sum(pdus[j][3] for j in range(6, i)) for i in range(6, 53)])
check("signals 58..299 are exactly 242 entries", len(s2p[58:]) == 242)
check("remaining 242 signals map only to 47 receive PDUs 6..52",
      min(s2p[58:]) == 6 and max(s2p[58:]) == 52 and len(set(s2p[58:])) == 47)
check("every Rx PDU owns at least one signal",
      all(any(s2p[sid] == pdu for sid in range(58, 300)) for pdu in range(6, 53)))
# Identity/membership: table slot i is signal i; Rx slots own PDUs 6..52 exactly.
owner_counts = Counter(s2p[58:])
check(
    "Rx signal ownership uses each PDU 6..52 at least once and only those PDUs",
    set(owner_counts) == set(range(6, 53)),
    repr(sorted(owner_counts)),
)
check(
    "Tx signals 0..57 map only to PDUs 0..5",
    set(s2p[:58]) == set(range(6)) and max(s2p[:58]) == 5,
)
check(
    "signal map length is 300 identity slots",
    len(s2p) == 300,
)
rx_prop_counts = Counter(props[58:])
check("Rx signal property classes are only 0/3/4",
      set(rx_prop_counts) <= {0, 3, 4}, repr(dict(rx_prop_counts)))

print("\n== COM RAM roots from GP-relative instruction immediates ==")
# GP = 0xFEBEB800 in application COM code; roots are GP + signed imm16.
root_imms = {
    "FEBE4A49": (COM_BUF_RAM - GP) & 0xFFFF,
    "FEBE52CC": (VALIDITY_RAM - GP) & 0xFFFF,
    "FEBE532C": (UPDATE_COUNTER_RAM - GP) & 0xFFFF,
}
check("GP-relative imm for COM buffer is -0x6DB7", root_imms["FEBE4A49"] == (-0x6DB7 & 0xFFFF))
check("GP-relative imm for validity is -0x6534", root_imms["FEBE52CC"] == (-0x6534 & 0xFFFF))
check("GP-relative imm for update counters is -0x64D4", root_imms["FEBE532C"] == (-0x64D4 & 0xFFFF))
check(
    "RxIndication body encodes movea COM buffer via GP",
    movea_gp_r1(root_imms["FEBE4A49"]) in CF[RX_INDICATION:RX_INDICATION + 212]
    or struct.pack("<H", root_imms["FEBE4A49"]) in CF[RX_INDICATION:RX_INDICATION + 212],
)
# Stronger: exact movea gp form 24 0e XX YY appears in RxIndication/receive_signal.
check(
    "exact movea-gp encoding for COM buffer in RxIndication or receive_signal",
    movea_gp_r1(root_imms["FEBE4A49"]) in CF[RX_INDICATION:RX_INDICATION + 212]
    or movea_gp_r1(root_imms["FEBE4A49"]) in CF[RECEIVE_SIGNAL:RECEIVE_SIGNAL + 178],
)
check(
    "timeout-on-indication encodes validity GP imm",
    struct.pack("<H", root_imms["FEBE52CC"]) in CF[0x8D682:0x8D682 + 30],
)
check(
    "timeout-on-indication encodes update-counter GP imm",
    struct.pack("<H", root_imms["FEBE532C"]) in CF[0x8D682:0x8D682 + 30],
)
check(
    "timeout-init encodes both validity and update-counter imms",
    struct.pack("<H", root_imms["FEBE52CC"]) in CF[0x8D65E:0x8D65E + 36]
    and struct.pack("<H", root_imms["FEBE532C"]) in CF[0x8D65E:0x8D65E + 36],
)

print("\n== SecOC envelope cross-check against 0x25970 ==")
secoc_ids = secoc_can_ids()
check("SecOC table has exactly six Data/CAN IDs", len(secoc_ids) == 6, repr(sorted(secoc_ids)))
check(
    "SecOC IDs are the documented six",
    secoc_ids == {0x00F, 0x2E4, 0x131, 0x132, 0x090, 0x0D7},
    repr(sorted(secoc_ids)),
)

print("\n== evidence artifact ==")
check("evidence CSV exists", EVIDENCE_PATH.is_file())
with EVIDENCE_PATH.open(newline="", encoding="utf-8") as stream:
    evidence = list(csv.DictReader(stream))
check("evidence has exactly 242 classified signal IDs", len(evidence) == 242)
check("evidence has unique signal IDs", len(evidence) == len({int(r["signal_id"]) for r in evidence}))
check("evidence signal IDs are exactly 58..299",
      [int(r["signal_id"]) for r in evidence] == list(range(58, 300)))
by_sid = {int(r["signal_id"]): r for r in evidence}
class_counts = Counter(r["classification"] for r in evidence)
check("evidence classification partition is exact", class_counts == {
    "extracted_bitfield": 131,
    "extracted_group_bytes": 14,
    "configured_not_extracted_by_pdu_handler": 93,
    "configured_no_com_unpacker_secoc_pdu": 3,
    "configured_no_com_unpacker": 1,
}, repr(class_counts))

print("\n== generated CSV agreement ==")
with CSV_PATH.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
check("CSV has exactly 242 signal rows", len(rows) == 242 and all(r["row_kind"] == "signal" for r in rows))
check("CSV covers all 47 Rx PDU ids",
      {int(r["rx_pdu_id"]) for r in rows} == set(range(6, 53)))
check("CSV signal IDs are exactly 58..299 in order",
      [int(r["signal_id"]) for r in rows] == list(range(58, 300)))
check("CSV PDU membership equals raw signal map",
      [int(r["rx_pdu_id"]) for r in rows] == s2p[58:])
check("CSV CAN IDs match acceptance table via 6+n",
      [int(r["can_id"], 0) for r in rows] ==
      [NORMAL_IDS[int(r["rx_pdu_id"]) - 6] for r in rows])
check(
    "CSV secoc_envelope=yes matches SecOC records at 0x25970",
    {int(r["can_id"], 0) for r in rows if r["secoc_envelope"] == "yes"} == secoc_ids,
)
check("CSV never lists diagnostic transport IDs as normal Rx rows",
      not any(int(r["can_id"], 0) in DIAG_CAN_IDS for r in rows))
check("CSV keeps CAN 0x344 absent",
      all(int(r["can_id"], 0) != 0x344 for r in rows))

recovered = [r for r in rows if r["evidence_status"] == "recovered"]
classified = [r for r in rows if r["evidence_status"] == "classified-no-com-extraction"]
check("recovered + classified partition all 242 signals",
      len(recovered) + len(classified) == 242, f"{len(recovered)}+{len(classified)}")
check("145 configured signals have positive extraction evidence", len(recovered) == 145, str(len(recovered)))
check("97 configured signals have deterministic no-COM-extraction classifications",
      len(classified) == 97, str(len(classified)))
check("no configured-unresolved Rx rows remain",
      not any(r["evidence_status"] == "configured-unresolved" for r in rows))
check("every CSV signal_id has an evidence/classification row",
      all(int(r["signal_id"]) in by_sid for r in rows))
check("three no-unpacker signals belong to SecOC sync CAN 0x00F",
      [int(r["signal_id"]) for r in evidence if r["classification"] == "configured_no_com_unpacker_secoc_pdu"] == [84, 85, 86])
check("sole ordinary no-unpacker signal is 217 / CAN 0x2E8",
      [int(r["signal_id"]) for r in evidence if r["classification"] == "configured_no_com_unpacker"] == [217]
      and next(r for r in rows if r["signal_id"] == "217")["can_id"] == "0x2E8")

print("\n== per-unpacker body hashes and per-signal immediates ==")
unpacker_meta: dict[int, tuple[int, str]] = {}
body_hash_ok = True
immediate_ok = True
dest_ok = True
for ev in evidence:
    kind = ev["extract_kind"]
    sid = int(ev["signal_id"])
    if kind == "none":
        # Negative rows are anchored by signal-to-PDU table bytes rather than a
        # nonexistent unpacker body.
        check_pdu = u16(0x224E4 + 2 * sid)
        if check_pdu != s2p[sid]:
            immediate_ok = False
            print(f"  NEGATIVE FAIL signal {sid} signal-to-PDU anchor")
        continue

    unp = int(ev["unpacker"], 0)
    size = int(ev["body_size"])
    digest = ev["body_sha256"]
    actual = sha256_region(unp, size)
    if actual != digest:
        body_hash_ok = False
        print(f"  HASH FAIL unpacker {unp:#x} size={size}")
    unpacker_meta[unp] = (size, digest)

    if kind == "bitfield":
        window_lo = int(ev["window_lo"], 0)
        window_hi = int(ev["window_hi"], 0)
        window = CF[window_lo:window_hi]
        # r6=3 -> nibble encoding 0x36 for movea r0,r6; r7=0x3e; observed patterns.
        if sid < 0x100:
            if (
                movea_r0_rd(sid, 6) not in window
                and movea_r0_rd(sid, 6) not in CF[unp:unp + size]
                and struct.pack("<H", sid) not in window
            ):
                immediate_ok = False
                print(f"  IMM FAIL signal {sid} id not in window {window_lo:#x}-{window_hi:#x}")
        buf_off = int(ev["buf_off"])
        if buf_off <= 0xFFFF:
            if (
                (buf_off < 0x100 and movea_r0_rd(buf_off, 7) not in window)
                and struct.pack("<H", buf_off) not in window
                and bytes([0x20, 0x3E, buf_off & 0xFF, (buf_off >> 8) & 0xFF]) not in window
            ):
                immediate_ok = False
                print(f"  IMM FAIL signal {sid} buf_off {buf_off}")
        bit_len = int(ev["bit_len"])
        if bit_len < 0x100 and (
            movea_r0_rd(bit_len, 8) not in window
            and bytes([bit_len, 0x42]) not in window  # mov imm,r8 form NN42
            and struct.pack("<H", bit_len) not in window
            and bytes([bit_len]) not in window
        ):
            immediate_ok = False
            print(f"  IMM FAIL signal {sid} bit_len {bit_len}")
        dest = int(ev["dest"], 0)
        gp_imm = (dest - GP) & 0xFFFF
        if movea_gp_r1(gp_imm) not in window and struct.pack("<H", gp_imm) not in window:
            dest_ok = False
            print(f"  DEST FAIL signal {sid} dest {dest:#x} gp_imm {gp_imm:#x}")
        # CSV agreement for recovered fields
        csv_row = next(r for r in recovered if int(r["signal_id"]) == sid)
        if (
            csv_row["unpacker"].lower() != ev["unpacker"].lower()
            or int(csv_row["bit_length"]) != bit_len
            or int(csv_row["start_arg"]) != int(ev["start_arg"])
            or int(csv_row["signed"]) != int(ev["signed"])
            or csv_row["dest"] != ev["dest"]
            or csv_row["call_site"].lower() != ev["call_site"].lower()
        ):
            immediate_ok = False
            print(f"  CSV/EVIDENCE MISMATCH signal {sid}")
    else:
        # opaque: signal id and buffer offset live in the constant tables
        opaque_sids = [u16(OPAQUE_SID_TABLE + 2 * i) for i in range(14)]
        opaque_offs = [u16(OPAQUE_OFF_TABLE + 2 * i) for i in range(14)]
        if sid not in opaque_sids:
            immediate_ok = False
            print(f"  OPAQUE FAIL signal {sid} not in 0x25902 table")
        else:
            idx = opaque_sids.index(sid)
            if opaque_offs[idx] != int(ev["buf_off"]):
                immediate_ok = False
                print(f"  OPAQUE FAIL signal {sid} buf_off mismatch")

check("all distinct unpacker bodies match evidence sha256", body_hash_ok,
      f"unpackers={len(unpacker_meta)}")
check("all recovered bitfield/opaque immediates match CodeFlash", immediate_ok)
check("all recovered RAM destinations match GP-relative encodings", dest_ok)
check(
    "CSV recovered set equals positive extraction evidence set",
    {int(r["signal_id"]) for r in recovered}
    == {int(e["signal_id"]) for e in evidence if e["classification"].startswith("extracted_")},
)
check(
    "CSV classified set equals negative evidence set",
    {int(r["signal_id"]) for r in classified}
    == {int(e["signal_id"]) for e in evidence if e["classification"].startswith("configured_")},
)

# Landmark bodies still locked.
check(
    "RxIndication body hash at 0x7C640",
    sha256_region(RX_INDICATION, 212)
    == "2097a94e790f063265e1d451270f5af5418c6f28978796458a081648d092d599",
)
check(
    "receive-signal helper body hash at 0x7C03E",
    sha256_region(RECEIVE_SIGNAL, 178)
    == "257bfbeca304f7ef650bc7ceee0d5a217e765a0043d48dd1d2527091c69e54a6",
)
check(
    "receive-signal helper stores <=8-bit values as bytes",
    CF[0x7C0D8:0x7C0DE] == bytes.fromhex("68eabb05800b"),
)
check(
    "receive-signal helper stores 9..16-bit values as halfwords",
    CF[0x7C0E0:0x7C0E8] == bytes.fromhex("1d06efffb105800c"),
)
check(
    "receive-signal helper stores 17..32-bit values as words",
    CF[0x7C0EA:0x7C0EC] == bytes.fromhex("010d"),
)
check(
    "generated destination widths match helper store-width policy",
    all(
        int(row["dest_width"])
        == (1 if int(row["bit_length"]) <= 8 else 2 if int(row["bit_length"]) <= 16 else 4)
        for row in recovered
        if row["dest_kind"] == "ram" and row["bit_length"] != "n/a"
    ),
)
check(
    "every evidence unpacker body hash is unique to its (addr,size)",
    len({(int(e["unpacker"], 0), int(e["body_size"]), e["body_sha256"])
         for e in evidence if e["extract_kind"] != "none"})
    >= len(unpacker_meta),
)

print("\n== generator determinism ==")
with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tmp:
    tmp_path = Path(tmp.name)
subprocess.check_call(
    [sys.executable, str(GEN), "-o", str(tmp_path), "--evidence", str(EVIDENCE_PATH)],
    cwd=REPO,
)
check(
    "generator regenerates CSV byte-for-byte from evidence",
    tmp_path.read_bytes() == CSV_PATH.read_bytes(),
)
tmp_path.unlink(missing_ok=True)

print(f"\nSummary: {passed} passed, {failed} failed; extracted={len(recovered)} classified-no-extraction={len(classified)}")
sys.exit(1 if failed else 0)
