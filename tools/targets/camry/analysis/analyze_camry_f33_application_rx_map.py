#!/usr/bin/env python3
"""Camry EPS 8965F3307000 application receive map builder.

Transfer of the Sienna receive-map method (docs/communications/application-rx.md,
ghidra/scripts/verify/ExportApplicationRxSignalEvidence.java,
tests/diagnostics/verify_application_receive.py) to the exact Camry image.

Everything is read-only against the CodeFlash, the pinned Ghidra project
inventory (function bodies/names) and an objdump disassembly cached under
build/out/targets/camry-8965F3307000/analysis/. It writes
application_rx_map.csv (one row per acceptance rule),
application_rx_signal_evidence.csv and tables.json into
data/generated/camry_f33_application_rx/. No OEM signal names are assigned.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import re
import struct
import subprocess
import sys
from collections import Counter, defaultdict

from tools import REPO_ROOT

ROOT = REPO_ROOT
IMAGE_REL = "firmware/camry-8965F3307000/CodeFlash.bin"
INVENTORY_REL = "data/targets/camry-8965F3307000/ghidra_project_inventory.baseline.jsonl"
DISASM = ROOT / "build/out/targets/camry-8965F3307000/analysis/application-rx/disasm-full.txt"
ARTIFACT_OUTPUT_DIR = "data/generated/camry_f33_application_rx"
EXPECTED_SHA = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

GP = 0xFEBEB800
TP = 0x23DFC

# Generated configuration tables (exact F33).
ACCEPTANCE = 0x230B8          # 47 rules x 16 bytes + 0xFFFFFFFF terminator
RULE_COUNT = 47
MASK_LUT = 0x22E68            # mask selector -> CFDGAFLM value
RULE_RING = 0x219AC           # rule -> software ring index (0xFF = none)
RULE_SELECTOR = 0x219DC       # rule -> callback selector bits (frame byte 6)
CALLBACKS = 0x21A24           # six per-ring callbacks
SLOT_STRUCTS = 0x21A0C        # per-callback-slot {desc table, dispatcher, mask table, range table}
SLOT_BASE = 0x21A48           # per-slot PDU-id base
SLOT_BANK = 0x22D94           # per-slot route-id bank bits
NORMAL_RX_DESC = 0x21FE8      # 43 x {software_id:u32, length:u32}
DIAG_RX_DESC = 0x21FA0        # 3 x {software_id:u32, length:u32}
XCP_RX_DESC = 0x21F50         # 1 x {software_id:u32, length:u32}
CANIF_PDU_PROP = 0x21FB8      # 48 bytes
ROUTE_SLOT0 = 0x229CE         # 48 x u32 {lo:u16 route, hi:u16 alternative}
ROUTE_SLOT1 = 0x2294E         # 5 x u32
CALLBACK_TABLES = 0x21EE4     # per callback-index pointer to a 16-pointer table
ROUTE_COUNTS = 0x21D28        # per slot entry count (u16)
SIG2PDU = 0x22488             # 284 x u16 (signals 0..282; index 283 = 0)
SIGNAL_COUNT = 283            # configured signal IDs 0..282
RX_SIGNAL_FIRST = 58
SIGPROP = 0x2236C             # per-signal property byte (COM insert policy)
COM_PDU = 0x226C0             # 48 x {timeout:u16, b1, b2, len:u16, b4, flags}
COM_BUF_OFF = 0x22840         # 48 x u16
SECOC_RECORDS = 0x25848       # 3 x 0x50
SECOC_RECORD_SIZE = 0x50
COM_BUF_RAM = GP - 0x6DB8     # 0xFEBE4A48
COM_VALID_RAM = GP - 0x6EC2   # 0xFEBE493E + pdu (bit7 = invalid)
COM_UPDATE_RAM = GP - 0x64C8  # 0xFEBE5338 + pdu
COM_TRACK_RAM = GP - 0x6528   # 0xFEBE52D8 + pdu
CANIF_TRACK_RAM = GP - 0x6468  # 0xFEBE5398 + pdu

RECEIVE_SIGNAL = 0x7D12A      # COM big-endian bitfield extractor
GROUP_COPY = 0x7E72A          # COM opaque byte-range copy
CANIF_FILTER = 0x810F2        # slot 0: CanIf normal receive
CANIF_DLC_CHECK = 0x8103E
CANIF_CHECKSUM = 0x80FDE          # slot-0 plain additive checksum hook (CanIf PDU property bit 0)
ID_CHECKSUM_GATE = 0x6A3BE        # CanIf PDU property bit 4 -> 0x6A328/0x6A32C
BOOT_CORE_END = 0x7208            # functions below are the bootloader core (its own GP = 0xFEBF9800), not application code
ID_CHECKSUM_TABLE = 0x28FE4       # 30 x {u16 CanIf PDU id, u8, u8 status slot, u16 Dem event, u8, u8 enabled(0x5A)}
ID_CHECKSUM_COUNT = 0x28FD4       # u16 record count
ID_CHECKSUM_ENABLE = (0x28FD6, 0x28FD7)   # both stages enabled when 0x5A
DIAG_DEMUX = 0x81200          # slot 2
XCP_DEMUX = 0x8312E           # slot 5
ROUTE_DISPATCH = 0x81D30
ROUTE_DISPATCH_PRIMARY = 0x81CA6
COM_RX_INDICATION = 0x7D72C
SECOC_INGRESS = 0x8EE7C
CANTP_RX = 0x79DB0
XCP_STAGE = 0x830D0
XCP_DISPATCH = 0x821D6

CF: bytes = b""
PDU_S = struct.Struct("<HBBHBB")
RULE_S = struct.Struct("<IIII")
DESC_S = struct.Struct("<II")


def u8(a: int) -> int:
    return CF[a]


def u16(a: int) -> int:
    return struct.unpack_from("<H", CF, a)[0]


def u32(a: int) -> int:
    return struct.unpack_from("<I", CF, a)[0]


def sha_region(off: int, size: int) -> str:
    return hashlib.sha256(CF[off:off + size]).hexdigest()


# --------------------------------------------------------------------------
# Ghidra inventory: function bodies
# --------------------------------------------------------------------------
class Function:
    __slots__ = ("entry", "hi", "lo", "name", "ranges", "size")

    def __init__(self, rec: dict) -> None:
        self.entry = int(rec["entry"]["offset"], 16)
        self.ranges = sorted((int(r["min"]["offset"], 16), int(r["max"]["offset"], 16)) for r in rec["body_ranges"])
        self.lo = self.ranges[0][0]
        self.hi = max(hi for _, hi in self.ranges)
        self.size = sum((hi - lo) // 2 + 1 for lo, hi in self.ranges) * 2
        self.name = rec.get("user_name") or f"FUN_{self.entry:08X}"


def load_functions() -> list[Function]:
    funcs: list[Function] = []
    with (ROOT / INVENTORY_REL).open(encoding="utf-8") as stream:
        for line in stream:
            rec = json.loads(line)
            if rec.get("record") == "function":
                funcs.append(Function(rec))
    funcs.sort(key=lambda f: f.lo)
    return funcs


class FunctionIndex:
    def __init__(self, funcs: list[Function]) -> None:
        self.starts = [f.lo for f in funcs]
        self.funcs = funcs
        self.by_entry = {f.entry: f for f in funcs}

    def containing(self, addr: int):
        i = bisect.bisect_right(self.starts, addr) - 1
        if i < 0:
            return None
        for j in (i,):
            f = self.funcs[j]
            if any(lo <= addr <= hi for lo, hi in f.ranges):
                return f
        # a later function may start inside a gap; check the next few
        for f in self.funcs[j + 1:j + 4]:
            if f.lo > addr:
                break
            if any(lo <= addr <= hi for lo, hi in f.ranges):
                return f
        return None


# --------------------------------------------------------------------------
# objdump disassembly
# --------------------------------------------------------------------------
LINE_RE = re.compile(r"^\s*([0-9a-f]+):\t([0-9a-f ]{2,})\t(\S+)\s*(.*?)\s*$")


class Ins:
    __slots__ = ("addr", "mnem", "ops", "regs")

    def __init__(self, addr: int, mnem: str, ops: str) -> None:
        self.addr = addr
        self.mnem = mnem
        self.ops = ops
        self.regs = re.findall(r"(?<![\w])((?:r|p)[0-9]+|gp|sp|tp|ep|lp)(?![\w])", ops)

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.addr:06X}: {self.mnem} {self.ops}"


def disassemble_image() -> None:
    """Disassemble the CodeFlash with the pinned toolchain into DISASM."""
    DISASM.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["tools/rh850", "toolchain", "run", "v850-elf-objdump", "-D", "-b", "binary",
         "-m", "v850e3v5", "--adjust-vma=0", f"/src/{IMAGE_REL}"],
        capture_output=True, text=True, check=True)
    text = proc.stdout
    if text.count("jarl") < 1000:
        raise SystemExit("objdump produced no code")
    DISASM.write_text(text, encoding="utf-8")


def load_instructions() -> list[Ins]:
    if not DISASM.exists():
        disassemble_image()
    out: list[Ins] = []
    with DISASM.open(encoding="utf-8") as stream:
        for line in stream:
            m = LINE_RE.match(line)
            if not m:
                continue
            if m.group(3).startswith("."):
                continue
            out.append(Ins(int(m.group(1), 16), m.group(3), m.group(4)))
    return out


# --------------------------------------------------------------------------
# static tables
# --------------------------------------------------------------------------
def read_acceptance() -> list[dict]:
    rules = []
    for i in range(RULE_COUNT):
        w = RULE_S.unpack_from(CF, ACCEPTANCE + 16 * i)
        sel = w[3] & 0xFF
        rules.append({
            "index": i, "address": ACCEPTANCE + 16 * i,
            "gaflid": w[0], "gaflp0": w[1], "gaflp1": w[2], "mask_selector": sel,
            "mask": u32(MASK_LUT + 4 * sel),
            "ide": (w[0] >> 31) & 1, "rtr": (w[0] >> 30) & 1, "lb": (w[0] >> 29) & 1,
            "id": w[0] & 0x1FFFFFFF,
            "gafl_dlc": (w[1] >> 28) & 0xF, "label": (w[1] >> 16) & 0xFFF,
            "fifo_rx": [x for x in range(8) if (w[2] >> x) & 1],
            "fifo_txrx": [x for x in range(8) if (w[2] >> (8 + x)) & 1],
            "ring": u8(RULE_RING + i), "selector": u8(RULE_SELECTOR + i),
        })
    assert u32(ACCEPTANCE + 16 * RULE_COUNT) == 0xFFFFFFFF, "acceptance terminator missing"
    assert u32(MASK_LUT) == 0xC00007FF and u32(MASK_LUT + 4) == 0xDFFFFFFF, "mask LUT drift"
    return rules


def read_route_table(base: int, count: int) -> list[dict]:
    rows = []
    for i in range(count):
        w = u32(base + 4 * i)
        lo, hi = w & 0xFFFF, w >> 16
        rows.append({"address": base + 4 * i, "word": w, "lo": lo, "hi": hi,
                     "lo_cb": lo >> 11, "lo_val": lo & 0x7FF, "hi_cb": hi >> 11, "hi_val": hi & 0x7FF})
    return rows


def callback_cell(index: int, slot: int) -> tuple[int, int]:
    table = u32(CALLBACK_TABLES + 4 * index)
    cell = table + 4 * slot
    return cell, u32(cell)


def read_com() -> list[dict]:
    pdus = []
    for i in range(48):
        t, b1, b2, ln, b4, fl = PDU_S.unpack_from(CF, COM_PDU + 8 * i)
        pdus.append({"id": i, "address": COM_PDU + 8 * i, "timeout": t, "b1": b1, "b2": b2,
                     "len": ln, "b4": b4, "flags": fl, "buf_off": u16(COM_BUF_OFF + 2 * i)})
    return pdus


def read_secoc() -> list[dict]:
    recs = []
    for i in range(3):
        a = SECOC_RECORDS + SECOC_RECORD_SIZE * i
        recs.append({
            "index": i, "address": a, "data_id": u16(a + 0x0A), "is_sync": u8(a + 9),
            "freshness_id": u16(a + 0x12), "tx_fv": u8(a + 0x15), "tx_mac": u16(a + 2),
            "secured_len": u32(a + 0x24), "app_pdu": u16(a + 0x34), "upper_route": u16(a + 0x36),
            "upper_cb": u32(a + 0x4C), "commit_cb": u32(a + 0x30), "fresh_cb": u32(a + 0x48),
            "record_sha256": sha_region(a, SECOC_RECORD_SIZE),
        })
    return recs


# --------------------------------------------------------------------------
# operand helpers
# --------------------------------------------------------------------------
IMM_RE = re.compile(r"^(-?(?:0x[0-9a-fA-F]+|\d+))$")
MEM_RE = re.compile(r"^(-?\d+)\[(\w+)\]$")


def split_ops(ops: str) -> list[str]:
    return [p.strip() for p in ops.split(",")] if ops else []


def parse_imm(tok: str):
    tok = tok.strip()
    if IMM_RE.match(tok):
        return int(tok, 0)
    return None


def width_for(bit_len: int) -> int:
    return 1 if bit_len <= 8 else 2 if bit_len <= 16 else 4


def wire_field(buf_off: int, start: int, length: int, pdu_off: int) -> str:
    """Render the extracted field as B<n>[hi:lo] segments relative to the PDU.

    0x7D12A forms the big-endian word w at COM+buf_off and returns
    (w >> shift) & ((1 << length) - 1) with
    shift = (32 + start - ((start + length + 7) & 0xF8)) & 0x1F (verified at
    0x7D188..0x7D19A).  `start` is the LSB index of the field inside the first
    window byte; longer fields continue with the low bits of the *preceding*
    byte.  Whole-byte big-endian fields are rendered as `B<first>..B<last> BE<n>`.
    """
    base = buf_off - pdu_off
    shift = (32 + start - ((start + length + 7) & 0xF8)) & 0x1F
    segs: list[list[int]] = []
    for i in range(length - 1, -1, -1):          # MSB first
        p = shift + i
        byte, bit = base + 3 - p // 8, p % 8
        if segs and segs[-1][0] == byte and segs[-1][2] == bit + 1:
            segs[-1][2] = bit
        else:
            segs.append([byte, bit, bit])
    if (all(lo == 0 and hi == 7 for _, hi, lo in segs)
            and all(segs[k + 1][0] == segs[k][0] + 1 for k in range(len(segs) - 1))):
        return f"B{segs[0][0]}" if len(segs) == 1 else f"B{segs[0][0]}..B{segs[-1][0]} BE{8 * len(segs)}"
    return "..".join(f"B{b}[{hi}]" if hi == lo else f"B{b}[{hi}:{lo}]" for b, hi, lo in segs)

# Crypto bank geometry, pinned to the Ghidra user labels of the inventory and to
# the GP-relative stores/copies in 0x693FE (key fragments) and 0x697F4 (test vector).
KV_PREVIOUS = GP - 0x673A   # 0xFEBE50C6 crypto_key_fragment_previous, 8 x 8 bytes
KV_QUALIFIED = GP - 0x66FA  # 0xFEBE5106 crypto_key_fragment_qualified, 8 x 8 bytes
KV_REQUEST = GP - 0x65FA    # 0xFEBE5206 crypto_key_request + 0x40 (slot 1), copied when all 8 qualify
TV_PREVIOUS = GP - 0x66BA   # 0xFEBE5146 crypto_test_fragment_previous, 4 x 8 bytes
TV_QUALIFIED = GP - 0x669A  # 0xFEBE5166 crypto_test_fragment_qualified, 4 x 8 bytes
TV_INPUT = GP - 0x667A      # 0xFEBE5186 crypto_test_input, 16 bytes (fragments j = 0, 1)
TV_EXPECTED = GP - 0x666A   # 0xFEBE5196 crypto_test_expected, 16 bytes (fragments j = 2, 3)
TV_SELECTOR = GP - 0x6761   # 0xFEBE509F selector / 0xFEBE50A0 mode (commit cells of 0x697F4)
REPEAT_THRESHOLD = 0x30E2F    # CodeFlash[0x30E2F] = 3: identical observations before a fragment qualifies


def crypto_bank(o: dict) -> dict:
    if o["collector"] == 0x693FE:
        i = o["signal"] - 90
        assert 0 <= i < 8
        return {"previous": KV_PREVIOUS + 8 * i, "qualified": KV_QUALIFIED + 8 * i, "commit": KV_REQUEST + 8 * i}
    j = o["signal"] - 100
    assert 0 <= j < 4
    commit = TV_INPUT + 8 * j if j < 2 else TV_EXPECTED + 8 * (j - 2)
    return {"previous": TV_PREVIOUS + 8 * j, "qualified": TV_QUALIFIED + 8 * j, "commit": commit}


# --------------------------------------------------------------------------
# extraction call-site parsing (ExportApplicationRxSignalEvidence.parseCallSite)
# --------------------------------------------------------------------------
def parse_call_site(window: list[Ins]):
    signal = buf = bits = start = signed = None
    r1_gp = r1_sp = dest = stack_off = None
    for ins in window:
        m, ops = ins.mnem, split_ops(ins.ops)
        if m == "movea" and len(ops) == 3:
            imm = parse_imm(ops[0])
            if imm is None:
                continue
            if ops[1] == "r0" and ops[2] == "r6":
                signal = imm & 0xFFFF
            elif ops[1] == "r0" and ops[2] == "r7":
                buf = imm & 0xFFFF
            elif ops[1] == "r0" and ops[2] == "r8":
                bits = imm & 0xFF
            elif ops[1] == "gp" and ops[2] == "r1":
                r1_gp, r1_sp = imm, None
            elif ops[1] == "sp" and ops[2] == "r1":
                r1_sp, r1_gp = imm, None
        elif m == "movea" and len(ops) == 3 and ops[1] == "r0":
            pass
        elif m == "mov" and len(ops) == 2:
            if ops[0] == "r8" and ops[1] == "r9" and bits is not None:
                start = bits
                continue
            imm = parse_imm(ops[0])
            if imm is None:
                continue
            if ops[1] == "r8":
                bits = imm & 0xFF
            elif ops[1] == "r9":
                start = imm & 0xFF
            elif ops[1] == "r1" and imm == 1:
                signed = 1
        elif m == "sst.w" and len(ops) == 2:
            mm = re.match(r"^(-?\d+)\[ep\]$", ops[1])
            if not mm:
                continue
            slot = int(mm.group(1))
            if slot == 0:
                signed = 0 if ops[0] == "r0" else 1
            elif slot == 4 and ops[0] == "r1":
                dest = None if r1_gp is None else (GP + r1_gp) & 0xFFFFFFFF
                stack_off = r1_sp
    if signal is None or buf is None or bits is None or start is None or signed is None:
        return None
    return {"signal": signal, "buf_off": buf, "bit_len": bits, "start": start, "signed": signed,
            "dest": dest, "stack_off": stack_off}


def persisted_stack_dest(body: list[Ins], call_addr: int, stack_off: int, width: int):
    """Transfer of ExportApplicationRxSignalEvidence.findPersistedStackDest.

    Returns every GP-relative store, in address order, of a register reloaded
    from the generated stack temporary `stack_off[sp]` (the caller passes the
    destination as SP+stack_off and persists the byte after the call).  SP- and
    EP-relative loads are both accepted because `mov sp, ep` precedes `sld.*`.
    """
    loads = {1: ("ld.b", "ld.bu", "sld.b", "sld.bu"), 2: ("ld.h", "ld.hu", "sld.h", "sld.hu"),
             4: ("ld.w", "sld.w")}[width]
    store = {1: "st.b", 2: "st.h", 4: "st.w"}[width]
    found: list[tuple[int, int]] = []
    loaded = None
    since = 0
    for ins in body:
        if ins.addr <= call_addr:
            continue
        parts = split_ops(ins.ops)
        if ins.mnem in loads and len(parts) == 2:
            mm = re.match(r"^(-?\d+)\[(?:sp|ep)\]$", parts[0])
            if mm and int(mm.group(1)) == stack_off:
                loaded, since = parts[1], 0
                continue
        if loaded is None:
            continue
        since += 1
        if since > 8:
            loaded = None
            continue
        if ins.mnem == store and len(parts) == 2 and parts[0] == loaded:
            mm = re.match(r"^(-?\d+)\[gp\]$", parts[1])
            if mm:
                found.append(((GP + int(mm.group(1))) & 0xFFFFFFFF, ins.addr))
    return found


def abs_table_snapshots(window: list[Ins]) -> list[dict[str, int]]:
    """Resolve `movhi H, r0, rX; ld.* D[rX], rY` absolute table reads.

    Returns one register snapshot *after* each instruction of the window, so the
    caller can read argument registers at the call and at the stack-argument
    stores that precede it.
    """
    regs: dict[str, int] = {}
    snaps: list[dict[str, int]] = []
    for ins in window:
        ops = split_ops(ins.ops)
        if ins.mnem == "movhi" and len(ops) == 3:
            imm = parse_imm(ops[0])
            if imm is not None and ops[1] == "r0":
                regs[ops[2]] = imm << 16
            else:
                regs.pop(ops[2], None)
        elif ins.mnem in ("ld.hu", "ld.h", "ld.bu", "ld.b", "ld.w") and len(ops) == 2:
            mm = MEM_RE.match(ops[0])
            base = regs.get(mm.group(2)) if mm else None
            regs.pop(ops[1], None)
            if mm and base is not None:
                regs[ops[1]] = (base + int(mm.group(1))) & 0xFFFFFFFF
        elif ins.mnem == "movea" and len(ops) == 3:
            regs.pop(ops[2], None)
        elif ins.mnem == "mov" and len(ops) == 2:
            regs.pop(ops[1], None)
        elif ins.mnem in ("st.b", "st.h", "st.w", "sst.w", "sst.h", "sst.b", "cmp", "mov"):
            pass
        else:
            for r in ins.regs[-1:]:
                regs.pop(r, None)
        snaps.append(dict(regs))
    return snaps


def abs_table_address(window: list[Ins], reg: str, at: Ins | None = None):
    """Absolute table address held by `reg` at instruction `at` (default: window end)."""
    snaps = abs_table_snapshots(window)
    if at is None:
        return snaps[-1].get(reg) if snaps else None
    for ins, snap in zip(window, snaps):
        if ins.addr == at.addr:
            return snap.get(reg)
    return None

# --------------------------------------------------------------------------
# GP-relative address resolver for the consumer census
# --------------------------------------------------------------------------
LOADS = {"ld.b": 1, "ld.bu": 1, "ld.h": 2, "ld.hu": 2, "ld.w": 4}
SLOADS = {"sld.b": 1, "sld.bu": 1, "sld.h": 2, "sld.hu": 2, "sld.w": 4}
STORES = {"st.b": 1, "st.h": 2, "st.w": 4}
SSTORES = {"sst.b": 1, "sst.h": 2, "sst.w": 4}
CALLEE_SAVED = {f"r{n}" for n in range(20, 30)}
CONTROL = {"br", "jmp", "jarl", "dispose", "prepare", "dbtrap", "reti", "eiret", "feret", "halt",
           "setpsw", "ldsr", "stsr", "synci", "syncp", "synce", "syncm", "rmtr", "wait", "callt"}


def is_cond_branch(m: str) -> bool:
    return m in ("br", "jmp", "jarl", "loop", "ctret") or (
        m.startswith("b") and len(m) <= 7 and (m[1:] in ("v", "nv", "l", "nl", "e", "ne", "nh", "h", "s", "ns", "c", "nc", "z", "nz", "r", "sa", "san", "lt", "ge", "le", "gt"))
    )


def resolve(regs: dict, base: str):
    if base == "gp":
        return 0
    v = regs.get(base)
    return v[1] if v and v[0] == "gp" else None


def census(ins_list: list[Ins], findex: FunctionIndex):
    """Return (reads, writes): address -> {function entry: set of widths}."""
    reads: dict[int, dict[int, set]] = defaultdict(lambda: defaultdict(set))
    writes: dict[int, dict[int, set]] = defaultdict(lambda: defaultdict(set))
    targets: set[int] = set()
    for ins in ins_list:
        if is_cond_branch(ins.mnem):
            for tok in split_ops(ins.ops):
                t = re.match(r"^0x([0-9a-f]+)$", tok)
                if t:
                    targets.add(int(t.group(1), 16))
    cur = None
    regs: dict[str, tuple[str, int]] = {}
    for ins in ins_list:
        m, ops = ins.mnem, split_ops(ins.ops)
        if m == "jarl":
            regs = {k: v for k, v in regs.items() if k in CALLEE_SAVED or k == "ep"}
            continue
        if m == "dispose":
            regs = {}
            continue
        if ins.addr in targets and m != "prepare":
            regs = {k: v for k, v in regs.items() if k in CALLEE_SAVED or k == "ep"}
        if ins.addr in findex.by_entry:
            cur = findex.by_entry[ins.addr] if ins.addr >= BOOT_CORE_END else None
            regs = {}
        if m in LOADS and len(ops) == 2:
            mm = MEM_RE.match(ops[0])
            if mm and cur is not None:
                off = resolve(regs, mm.group(2))
                if off is not None:
                    reads[(GP + off + int(mm.group(1))) & 0xFFFFFFFF][cur.entry].add(LOADS[m])
            regs.pop(ops[1], None)
        elif m in SLOADS and len(ops) == 2:
            mm = MEM_RE.match(ops[0])
            if mm and cur is not None:
                off = resolve(regs, "ep")
                if off is not None:
                    reads[(GP + off + int(mm.group(1))) & 0xFFFFFFFF][cur.entry].add(SLOADS[m])
            regs.pop(ops[1], None)
        elif m in STORES and len(ops) == 2:
            mm = MEM_RE.match(ops[1])
            if mm and cur is not None:
                off = resolve(regs, mm.group(2))
                if off is not None:
                    writes[(GP + off + int(mm.group(1))) & 0xFFFFFFFF][cur.entry].add(STORES[m])
        elif m in SSTORES and len(ops) == 2:
            mm = MEM_RE.match(ops[1])
            if mm and mm.group(2) == "ep" and cur is not None:
                off = resolve(regs, "ep")
                if off is not None:
                    writes[(GP + off + int(mm.group(1))) & 0xFFFFFFFF][cur.entry].add(SSTORES[m])
        elif m == "movea" and len(ops) == 3:
            imm, src, dst = parse_imm(ops[0]), ops[1], ops[2]
            val = None
            if imm is not None:
                if src == "gp":
                    val = ("gp", imm)
                elif src in regs and regs[src][0] == "gp":
                    val = ("gp", regs[src][1] + imm)
            if val is None:
                regs.pop(dst, None)
            else:
                regs[dst] = val
        elif m == "movhi" and len(ops) == 3:
            regs.pop(ops[2], None)
        elif m == "addi" and len(ops) == 3:
            imm, src, dst = parse_imm(ops[0]), ops[1], ops[2]
            if imm is not None and src in regs and regs[src][0] == "gp":
                regs[dst] = ("gp", regs[src][1] + imm)
            else:
                regs.pop(dst, None)
        elif m == "add" and len(ops) == 2:
            src, dst = ops
            if src in regs and regs[src][0] == "gp" and dst not in regs:
                regs[dst] = regs[src]
            else:
                regs.pop(dst, None)
        elif m == "mov" and len(ops) == 2:
            src, dst = ops
            if src in regs and regs[src][0] == "gp":
                regs[dst] = regs[src]
            else:
                regs.pop(dst, None)
        elif m in CONTROL or is_cond_branch(m) or m in ("cmp", "tst1", "cmpfs", "satadd", "satsub", "sadiff", "mulhi", "mullo", "divhu", "divh", "divqu", "divq", "remu", "rem", "madh", "madl", "mach", "macl", "msubh", "msubl", "ffma", "ffms", "mul", "mulx", "nmul", "nmadx", "bst", "bclr", "bset", "bnot", "btst", "bsh", "caxi", "absf", "addf", "subf", "mulf", "divf", "negf", "cmpf", "cvf", "fcnv", "scallf", "sndf", "sndfr", "sndv", "rcr", "rsw", "swsr", "ssar", "sstsr", "ldsr", "stsr", "pushsp", "popsp", "clr1", "set1", "not1", "tst1", "xl", "xtr", "xchg"):
            continue
        else:
            for r in ins.regs[-1:]:
                regs.pop(r, None)
    return reads, writes


def fname(findex: FunctionIndex, entry: int) -> str:
    f = findex.by_entry.get(entry)
    return f.name if f else f"FUN_{entry:08X}"


def main() -> int:
    global CF
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output-dir", default=ARTIFACT_OUTPUT_DIR,
                        help="directory receiving the map, the signal evidence and the tables")
    out_dir = ROOT / parser.parse_args().output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    CF = (ROOT / IMAGE_REL).read_bytes()
    digest = hashlib.sha256(CF).hexdigest()
    if digest != EXPECTED_SHA:
        raise SystemExit(f"unexpected image hash {digest}")
    funcs = load_functions()
    findex = FunctionIndex(funcs)
    ins_list = load_instructions()
    by_addr = {ins.addr: ins for ins in ins_list}
    ordered = sorted(ins_list, key=lambda i: i.addr)
    addr_index = {ins.addr: k for k, ins in enumerate(ordered)}

    rules = read_acceptance()
    route0 = read_route_table(ROUTE_SLOT0, 48)
    route1 = read_route_table(ROUTE_SLOT1, 5)
    com = read_com()
    secoc = read_secoc()
    s2p = [u16(SIG2PDU + 2 * i) for i in range(SIGNAL_COUNT)]
    props = [u8(SIGPROP + i) for i in range(SIGNAL_COUNT)]
    normal_desc = [DESC_S.unpack_from(CF, NORMAL_RX_DESC + 8 * i) for i in range(43)]
    diag_desc = [DESC_S.unpack_from(CF, DIAG_RX_DESC + 8 * i) for i in range(3)]
    xcp_desc = [DESC_S.unpack_from(CF, XCP_RX_DESC + 8 * i) for i in range(1)]
    pdu_props = [u8(CANIF_PDU_PROP + i) for i in range(48)]
    id_checksum: dict[int, dict] = {}
    for i in range(u16(ID_CHECKSUM_COUNT)):
        a = ID_CHECKSUM_TABLE + 8 * i
        id_checksum[u16(a)] = {"address": a, "slot": u8(a + 2), "event": u16(a + 3), "enabled": u8(a + 7)}
    callbacks = [u32(CALLBACKS + 4 * i) for i in range(6)]
    slot_structs = [u32(SLOT_STRUCTS + 4 * i) for i in range(6)]
    slot_base = [u16(SLOT_BASE + 2 * i) for i in range(6)]
    slot_bank = [u16(SLOT_BANK + 2 * i) for i in range(6)]
    route_counts = [u16(ROUTE_COUNTS + 2 * i) for i in range(2)]

    # ------------------------------------------------------------------
    # extraction call sites
    # ------------------------------------------------------------------
    extraction_sites = [ins for ins in ordered if ins.mnem == "jarl" and ins.ops.startswith("0x7d12a")]
    unpacker_set: dict[int, Function] = {}
    bitfield_rows: list[dict] = []
    unparsed_sites: list[dict] = []
    for call in extraction_sites:
        fn = findex.containing(call.addr)
        if fn is None:
            unparsed_sites.append({"call": call.addr, "reason": "no function"})
            continue
        k = addr_index[call.addr]
        window = [i for i in ordered[max(0, k - 32):k] if i.addr >= fn.lo and i.addr < call.addr][-24:]
        window = [i for i in window if call.addr - i.addr <= 0x40]
        parsed = parse_call_site(window)
        if parsed is None:
            unparsed_sites.append({"call": call.addr, "function": fn.entry, "function_name": fn.name})
            continue
        unpacker_set.setdefault(fn.entry, fn)
        dest, persist_site, persist_all = parsed["dest"], None, []
        stack_persisted = False
        if dest is None and parsed["stack_off"] is not None:
            body = [i for i in ordered if fn.lo <= i.addr <= fn.hi]
            found = persisted_stack_dest(body, call.addr, parsed["stack_off"], width_for(parsed["bit_len"]))
            dest, persist_site = found[0] if found else (None, None)
            persist_all = [f"0x{a:08X}@0x{s:06X}" for a, s in found]
            stack_persisted = dest is not None
        if dest is None:
            unparsed_sites.append({"call": call.addr, "function": fn.entry, "function_name": fn.name,
                                   "reason": "destination not recovered", "parsed": parsed})
            continue
        bitfield_rows.append({**parsed, "dest": dest, "call_site": call.addr, "unpacker": fn.entry,
                              "unpacker_name": fn.name, "unpacker_size": fn.size,
                              "unpacker_sha256": sha_region(fn.lo, fn.hi - fn.lo + 2),
                              "window_lo": window[0].addr, "stack_persisted": stack_persisted,
                              "persist_site": persist_site, "persist_dests": persist_all})

    # table-driven extraction calls (0x697F4): arguments come from CodeFlash tables
    table_rows: list[dict] = []
    for site in unparsed_sites:
        if "function" not in site or site["function"] != 0x697F4:
            continue
        call = by_addr[site["call"]]
        k = addr_index[call.addr]
        window = [i for i in ordered[max(0, k - 40):k] if call.addr - i.addr <= 0x50]
        sig_addr = abs_table_address(window, "r6")
        buf_addr = abs_table_address(window, "r7")
        bits_addr = abs_table_address(window, "r8")
        start_addr = abs_table_address(window, "r9")
        signed_store = next((i for i in reversed(window) if i.mnem == "sst.w" and split_ops(i.ops) == ["r1", "0[ep]"]), None)
        signed_addr = abs_table_address(window, "r1", signed_store)
        stack_off = None
        for ins in reversed(window):
            ops = split_ops(ins.ops)
            if ins.mnem == "movea" and len(ops) == 3 and ops[1] == "sp" and ops[2] == "r1":
                stack_off = parse_imm(ops[0])
                break
        fn = findex.by_entry[0x697F4]
        body = [i for i in ordered if fn.lo <= i.addr <= fn.hi]
        found = persisted_stack_dest(body, call.addr, stack_off, 1) if stack_off is not None else []
        dest, persist_site = found[0] if found else (None, None)
        table_rows.append({
            "signal": u16(sig_addr), "buf_off": u16(buf_addr), "bit_len": u8(bits_addr),
            "start": u8(start_addr), "signed": u8(signed_addr), "dest": dest,
            "call_site": call.addr, "unpacker": 0x697F4, "unpacker_name": fn.name,
            "unpacker_size": fn.size, "unpacker_sha256": sha_region(fn.lo, fn.hi - fn.lo + 2),
            "tables": {"signal": sig_addr, "buf_off": buf_addr, "bit_len": bits_addr,
                       "start": start_addr, "signed": signed_addr},
            "stack_off": stack_off, "persist_site": persist_site,
            "persist_dests": [f"0x{a:08X}@0x{s:06X}" for a, s in found],
        })
    remaining_unparsed = [s for s in unparsed_sites if not ("function" in s and s["function"] == 0x697F4)]

    # opaque group copies (0x7E72A): signal index and byte offset tables
    opaque_rows: list[dict] = []
    group_sites = [ins for ins in ordered if ins.mnem == "jarl" and ins.ops.startswith("0x7e72a")]
    for call in group_sites:
        fn = findex.containing(call.addr)
        k = addr_index[call.addr]
        window = ordered[max(0, k - 14):k]
        window = [i for i in window if call.addr - i.addr <= 0x40]
        sig_addr = abs_table_address(window, "r6")
        off_addr = abs_table_address(window, "r7")
        gen_addr = None
        for ins in reversed(window):
            if ins.mnem == "ld.hu" and len(split_ops(ins.ops)) == 2 and split_ops(ins.ops)[1] == "ep":
                # block head: movhi 2, r0, ep ; ld.hu D[ep], ep
                j = addr_index[ins.addr]
                prev = ordered[j - 1]
                if prev.mnem == "movhi" and split_ops(prev.ops)[2] == "ep":
                    mm = MEM_RE.match(split_ops(ins.ops)[0])
                    gen_addr = 0x20000 + int(mm.group(1))
                break
        count = None
        stack_dest = None
        for ins in reversed(window):
            ops = split_ops(ins.ops)
            if ins.mnem == "mov" and len(ops) == 2 and ops[1] == "r8":
                count = parse_imm(ops[0])
            if ins.mnem == "mov" and len(ops) == 2 and ops[1] == "r9" and ops[0] == "sp":
                stack_dest = 0
            if ins.mnem in ("addi", "movea") and len(ops) == 3 and ops[1] == "sp" and ops[2] == "r9":
                stack_dest = parse_imm(ops[0])
        opaque_rows.append({"signal": u16(sig_addr), "buf_off": u16(off_addr), "count": count,
                            "gen_pdu": u16(gen_addr) if gen_addr else None,
                            "call_site": call.addr, "collector": fn.entry, "collector_name": fn.name,
                            "signal_table": sig_addr, "offset_table": off_addr, "gen_table": gen_addr,
                            "stack_dest": stack_dest})

    # consumer census
    reads, writes = census(ins_list, findex)

    # per-signal classification
    by_signal: dict[int, dict] = {}
    for r in bitfield_rows + table_rows:
        by_signal.setdefault(r["signal"], r)
    opaque_by_signal = {r["signal"]: r for r in opaque_rows}

    signal_rows: list[dict] = []
    reader_defaults = {"readers_same_signal_unpacker": 0, "readers_other_unpackers": "", "consumer_count": 0,
                       "first_consumer": "none", "first_consumer_name": "", "consumers": "",
                       "other_writer_count": 0, "other_writers": ""}
    for sid in range(RX_SIGNAL_FIRST, SIGNAL_COUNT):
        pdu = s2p[sid]
        row = {"signal_id": sid, "com_pdu": pdu, "signal_property": f"0x{props[sid]:X}", **reader_defaults}
        r = by_signal.get(sid)
        region = None
        exclude = set()
        if r is not None:
            row.update({"extract_kind": "bitfield" if r in bitfield_rows else "table-driven bitfield",
                        "unpacker": f"0x{r['unpacker']:06X}", "call_site": f"0x{r['call_site']:06X}",
                        "buf_off": r["buf_off"], "bit_len": r["bit_len"], "start_arg": r["start"],
                        "signed": r["signed"], "dest": f"0x{r['dest']:08X}", "dest_width": width_for(r["bit_len"]),
                        "wire_field": wire_field(r["buf_off"], r["start"], r["bit_len"], com[pdu]["buf_off"]),
                        "stack_persisted": r.get("stack_persisted", r.get("persist_site") is not None),
                        "persist_dests": ";".join(r.get("persist_dests", [])), "ram_path": ""})
            region = (r["dest"], row["dest_width"])
            owners = {r2["unpacker"] for r2 in bitfield_rows + table_rows if r2["dest"] == r["dest"]}
            exclude = owners
        elif sid in opaque_by_signal:
            o = opaque_by_signal[sid]
            bank = crypto_bank(o)
            row.update({"extract_kind": "opaque_pdu_bytes", "unpacker": f"0x{o['collector']:06X}",
                        "call_site": f"0x{o['call_site']:06X}", "buf_off": o["buf_off"],
                        "bit_len": o["count"] * 8, "start_arg": 0, "signed": 0,
                        "dest": f"0x{bank['commit']:08X}", "dest_width": o["count"],
                        "wire_field": f"B{o['buf_off'] - com[pdu]['buf_off']}..B{o['buf_off'] - com[pdu]['buf_off'] + o['count'] - 1} opaque",
                        "stack_persisted": False, "persist_dests": "",
                        "ram_path": " -> ".join([f"COM 0x{COM_BUF_RAM + o['buf_off']:08X}", "stack",
                                                f"previous 0x{bank['previous']:08X}",
                                                f"qualified 0x{bank['qualified']:08X}",
                                                f"committed 0x{bank['commit']:08X}"])})
            region = (bank["commit"], o["count"])
            exclude = {o["collector"]}
        else:
            row.update({"extract_kind": "none", "unpacker": "none", "call_site": "", "buf_off": com[pdu]["buf_off"],
                        "bit_len": 0, "start_arg": 0, "signed": 0, "dest": "none", "dest_width": 0,
                        "wire_field": "n/a", "stack_persisted": False, "persist_dests": "", "ram_path": ""})
        row.setdefault("ram_path", "")
        # readers / other writers of the destination region
        if region is not None:
            a, w = region
            rd = {}
            for addr, per in reads.items():
                if addr < a + w:
                    for fe, ws in per.items():
                        hit = [x for x in ws if not (addr + x <= a or addr >= a + w)]
                        if hit:
                            rd.setdefault(fe, set()).update(hit)
            consumers = sorted(fe for fe in rd if fe not in unpacker_set and fe not in exclude)
            other_unpackers = sorted(fe for fe in rd if fe in unpacker_set and fe not in exclude)
            row["readers_other_unpackers"] = " ".join(f"0x{fe:06X}" for fe in other_unpackers)
            row["consumer_count"] = len(consumers)
            row["first_consumer"] = f"0x{consumers[0]:06X}" if consumers else "none"
            row["first_consumer_name"] = fname(findex, consumers[0]) if consumers else ""
            row["consumers"] = " ".join(f"0x{fe:06X}" for fe in consumers[:8])
            wr = sorted({fe for addr, per in writes.items() if addr < a + w and addr + 4 > a for fe in per} - exclude)
            row["other_writer_count"] = len(wr)
            row["other_writers"] = " ".join(f"0x{fe:06X}" for fe in wr[:4])
        signal_rows.append(row)
    pdu_has_extraction = {s2p[r["signal"]] for r in bitfield_rows + table_rows}
    pdu_has_opaque = {s2p[r["signal"]] for r in opaque_rows}
    secoc_pdus = {rec["app_pdu"] for rec in secoc}
    for row in signal_rows:
        pdu = row["com_pdu"]
        if row["extract_kind"] == "bitfield":
            row["classification"] = "extracted_bitfield"
        elif row["extract_kind"] == "table-driven bitfield":
            row["classification"] = "extracted_bitfield_table_driven"
        elif row["extract_kind"] == "opaque_pdu_bytes":
            row["classification"] = "extracted_group_bytes"
        elif pdu in pdu_has_extraction or pdu in pdu_has_opaque:
            row["classification"] = "configured_not_extracted_by_pdu_handler"
        elif pdu in secoc_pdus:
            row["classification"] = "configured_no_com_unpacker_secoc_pdu"
        else:
            row["classification"] = "configured_no_com_unpacker"

    # per-PDU summary
    per_pdu: dict[int, dict] = {}
    for row in signal_rows:
        d = per_pdu.setdefault(row["com_pdu"], {"signals": [], "bitfield": 0, "opaque": 0, "none": 0,
                                                "unpackers": set(), "dests": [], "consumers": set(),
                                                "fields": []})
        d["signals"].append(row["signal_id"])
        if row["classification"].startswith("extracted_bitfield"):
            d["bitfield"] += 1
            d["unpackers"].add(int(row["unpacker"], 16))
            d["dests"].append(int(row["dest"], 16))
            d["fields"].append(f"sig{row['signal_id']}={row['wire_field']}@{row['dest']}")
            d["consumers"].update(int(x, 16) for x in row["consumers"].split())
        elif row["classification"] == "extracted_group_bytes":
            d["opaque"] += 1
            d["unpackers"].add(int(row["unpacker"], 16))
        else:
            d["none"] += 1

    # ------------------------------------------------------------------
    # per accepted ID rows
    # ------------------------------------------------------------------
    desc_by_rule: dict[int, int] = {}
    for idx, (sw, _) in enumerate(normal_desc):
        for rule in rules[:43]:
            if rule["id"] == (sw & 0x7FF):
                desc_by_rule[rule["index"]] = idx
    assert len(desc_by_rule) == 43, "normal descriptors do not map one-to-one onto rules 0..42"

    def route_summary(pdu: int) -> tuple[str, str]:
        entry = route0[pdu]
        if entry["hi"] != 0xFFFF:
            # 0x81D90: a non-0xFFFF high half selects the table at [0x21CBC] and its +8 cell.
            alt_cell = u32(0x21CBC) + 8
            return (f"0x{entry['address']:06X}=0x{entry['word']:08X}",
                    f"0x{alt_cell:06X}->0x{u32(alt_cell):06X}({entry['hi_val']})")
        cell, target = callback_cell(entry["lo_cb"], 2)
        return (f"0x{entry['address']:06X}=0x{entry['word']:08X}", f"0x{cell:06X}->0x{target:06X}({entry['lo_val']})")

    def span(vals):
        return "none" if not vals else (f"0x{min(vals):08X}" if min(vals) == max(vals) else f"0x{min(vals):08X}..0x{max(vals):08X}")

    CRYPTO_KEY_PDUS = set(range(10, 18))       # CAN 0x013..0x01A, key fragments 0..7
    CRYPTO_TEST_PDUS = set(range(19, 23))      # CAN 0x01C..0x01F, test-vector fragments 0..3
    rows_out: list[dict] = []
    for rule in rules:
        base = {
            "rule_index": rule["index"], "rule_address": f"0x{rule['address']:06X}",
            "can_id": f"0x{rule['id']:03X}" if rule["ide"] == 0 else f"0x{rule['id']:08X}",
            "id_format": "extended" if rule["ide"] else "standard",
            "gaflid_word": f"0x{rule['gaflid']:08X}", "gaflm_mask": f"0x{rule['mask']:08X}",
            "mask_selector": rule["mask_selector"],
            "gaflp0_word": f"0x{rule['gaflp0']:08X}", "gaflp1_word": f"0x{rule['gaflp1']:08X}",
            "gafl_label": f"0x{rule['label']:02X}", "gafl_dlc_check": rule["gafl_dlc"],
            "rscfd_fifo": (f"RFIFO{rule['fifo_rx'][0]}" if rule["fifo_rx"] else f"CFIFO{rule['fifo_txrx'][0]}"),
            "handler_chain": "", "consumers": "", "consumer_count": 0, "com_buffer_readers": "n/a",
        }
        id_mask = rule["mask"] & (0x1FFFFFFF if rule["ide"] else 0x7FF)
        if id_mask == (0x1FFFFFFF if rule["ide"] else 0x7FF):
            id_text = f"all {29 if rule['ide'] else 11} ID bits compared"
        else:
            id_text = (f"only ID bits 10:0 compared (GAFLMASK 0x{rule['mask']:08X}): the hardware rule admits every"
                       f" IDE={rule['ide']} non-RTR frame with ID[10:0]=0x{rule['id'] & 0x7FF:03X}; the software"
                       " descriptor match narrows it to the exact 32-bit software id")
        ide_rule = (f"IDE={rule['ide']} compared, RTR=0 compared, {id_text}; GAFLDLC=0 (no hardware length rule); "
                    "no FDF/BRS rule")
        if rule["index"] <= 42:
            idx = desc_by_rule[rule["index"]]
            sw, length = normal_desc[idx]
            fd = bool(sw & 0x40000000)
            pdu = 5 + idx
            c = com[pdu]
            entry = route0[pdu]
            route_addr, route_target = route_summary(pdu)
            sec = [rec for rec in secoc if rec["app_pdu"] == pdu]
            summ = per_pdu[pdu]
            props_ = pdu_props[pdu]
            checksum_gate = props_ & 1
            idck = id_checksum.get(pdu)
            id_checksum_gate = bool(props_ & 0x10) and idck is not None and idck["enabled"] == 0x5A
            unpackers = sorted(summ["unpackers"])
            consumers = sorted(summ["consumers"])
            cb0 = COM_BUF_RAM + c["buf_off"]
            direct: set[int] = set()
            for a2, per in reads.items():
                if cb0 <= a2 < cb0 + c["len"]:
                    direct.update(per)
            buf_readers = sorted(direct)
            base["com_buffer_readers"] = " ".join(f"0x{fe:06X}" for fe in buf_readers) if buf_readers else "none"
            chain = [
                f"RSCFD rule {rule['index']} (label 0x{rule['label']:02X}, {base['rscfd_fifo']})",
                f"RX ISR 0x83E0C -> 0x83D14 -> 0x80B42 -> ring 0xFEBE4038 -> 0x808D6 -> 0x80884 (selector 0x{rule['selector']:02X})",
                f"0x810F2 (slot 0, descriptor {idx})",
            ]
            if checksum_gate:
                chain.append(f"0x80FDE plain additive checksum via slot hook table 0x21950[0] (fail: drop +"
                             f" FEBE{CANIF_TRACK_RAM + pdu - 0xFEBE0000:04X}++)")
            chain.append(f"0x8103E DLC check via slot hook table 0x21954[0] (length <= {length}, <= {64 if fd else 8}; fail: drop)")
            if props_ & 0x10:
                if idck is None:
                    chain.append(f"0x6A3BE ID-checksum gate: no status-map record (0x28FE4) for CanIf PDU {pdu} -> passes")
                elif id_checksum_gate:
                    chain.append(f"0x6A3BE -> 0x6A328/0x6A32C ID checksum (record 0x{idck['address']:06X} enabled;"
                                 f" fail: drop + FEBE{CANIF_TRACK_RAM + pdu - 0xFEBE0000:04X}++)")
                else:
                    chain.append(f"0x6A3BE ID-checksum gate: record 0x{idck['address']:06X} byte7=0x{idck['enabled']:02X}"
                                 " (not 0x5A) -> disabled, passes")
            if entry["hi"] != 0xFFFF:
                chain.append("0x8EE7C SecOC ingress -> 0x8F34A queue -> 0x8F98C/0x8F746/0x8F906 verify -> 0x8F546 -> 0x90204 -> 0x81CA6")
            chain.append(f"0x81D16 -> 0x81D30[{route_addr}] -> " + route_target)
            chain.append(f"0x7D72C(COM PDU {pdu}): copy min(len,{c['len']}) bytes to 0x{COM_BUF_RAM + c['buf_off']:08X}")
            if unpackers:
                chain.append("unpacker " + " / ".join(f"0x{u:06X}" for u in unpackers) + f" ({summ['bitfield']} bitfields, {summ['opaque']} opaque)")
            else:
                chain.append("no COM unpacker (no stock scalar extraction for this PDU)")
            chain.append(f"{len(consumers)} reader function(s) of the extracted cells" if consumers else "no reader of extracted cells recovered")
            chain.append(f"{len(buf_readers)} direct reader function(s) of the COM buffer" if buf_readers else "no direct reader of the COM buffer outside COM/CanIf")
            parts = []
            if checksum_gate:
                parts.append("yes: plain additive checksum (slot hook 0x80FDE, PDU property bit 0): "
                             "data[len-1] == ((id & 0xFF) + ((id >> 8) & 7) + len + sum(data[0..len-2])) mod 256, "
                             f"length 1..{64 if rule['ide'] else 8}; mismatch drops the frame and increments"
                             f" 0x{CANIF_TRACK_RAM + pdu:08X}")
            if props_ & 0x10:
                if idck is None:
                    parts.append("ID-checksum gate configured without a status-map record (0x28FE4): none")
                elif id_checksum_gate:
                    parts.append(f"yes: ID checksum (0x6A3BE -> 0x6A328/0x6A32C, record 0x{idck['address']:06X} byte7=0x5A,"
                                 " PDU property bit 4): data[7] == ((id & 0xFF) + ((id >> 8) & 7) + sum(data[0..6]) + 8)"
                                 f" mod 256, length >= 8; mismatch drops the frame and increments 0x{CANIF_TRACK_RAM + pdu:08X}")
                else:
                    parts.append(f"ID-checksum record 0x{idck['address']:06X} present but disabled"
                                 f" (byte7=0x{idck['enabled']:02X} != 0x5A)")
            checksum_text = "; ".join(parts) if parts else "no"
            controls = (f"{c['len']} COM bytes at 0x{COM_BUF_RAM + c['buf_off']:08X}; {summ['bitfield']} extracted"
                        f" scalars ({'; '.join(summ['fields'][:6]) or 'none'})")
            mem = (f"none: fixed destinations (COM buffer 0x{COM_BUF_RAM + c['buf_off']:08X}..+{c['len'] - 1}"
                   " and GP-relative signal cells)")
            if pdu in CRYPTO_KEY_PDUS:
                i = pdu - 10
                controls = (f"key fragment {i} of 8: B0..B7 -> COM 0x{COM_BUF_RAM + c['buf_off']:08X} -> 0x{KV_PREVIOUS + 8 * i:08X} (previous)"
                            f" -> 0x{KV_QUALIFIED + 8 * i:08X} (after {u8(REPEAT_THRESHOLD)} identical observations)"
                            f" -> 0x{KV_REQUEST + 8 * i:08X} crypto_key_request slot 1 when all 8 fragments qualify (0x693FE);"
                            " consumed only after UDS RID 0x100E starts the collected key update (0x8B864 -> 0x6A028 -> 0x69CA2 -> 0x69780 -> 0x692D2)")
                mem = (f"none in EPS RAM: fixed crypto banks 0x{KV_PREVIOUS:08X}..0x{KV_REQUEST + 63:08X}; the bytes become"
                       " ICU-S key material only through the UDS-activated collected key update")
            elif pdu == 18:
                controls = (f"B0 selector -> 0x{TV_SELECTOR:08X}, B1 mode -> 0x{TV_SELECTOR + 1:08X} (after {u8(REPEAT_THRESHOLD)} identical"
                            " observations; 0x697F4); consumed only after UDS RID 0x100F starts the crypto test (0x8B872 -> 0x6A0AE -> 0x69C58 -> 0x69BD8)")
                mem = f"none in EPS RAM: two fixed selector/mode cells 0x{TV_SELECTOR:08X}/0x{TV_SELECTOR + 1:08X}"
            elif pdu in CRYPTO_TEST_PDUS:
                j = pdu - 19
                role = f"crypto_test_input 0x{TV_INPUT + 8 * j:08X}" if j < 2 else f"crypto_test_expected 0x{TV_EXPECTED + 8 * (j - 2):08X}"
                controls = (f"test-vector fragment {j}: B0..B7 -> COM 0x{COM_BUF_RAM + c['buf_off']:08X} -> 0x{TV_PREVIOUS + 8 * j:08X} (previous)"
                            f" -> 0x{TV_QUALIFIED + 8 * j:08X} (qualified) -> {role}; consumed only after UDS RID 0x100F"
                            " (AES/MAC verification 0x69BD8, compared by 0x6A0D8/0x6A0FE)")
                mem = f"none in EPS RAM: fixed crypto-test banks 0x{TV_PREVIOUS:08X}..0x{TV_EXPECTED + 15:08X}"
            base.update({
                "demux_class": "normal application (COM)",
                "frame_format": f"CAN-FD (descriptor 0x40000000|id, length {length})" if fd else f"classic (length {length})",
                "canif_descriptor_index": idx,
                "canif_software_id": f"0x{sw:08X}",
                "canif_length": length,
                "canif_dlc_rule": f"0x{CANIF_DLC_CHECK:06X}: frame length <= descriptor length ({length}) and <= {64 if fd else 8} (FD flag from RFFDF); shorter frames accepted",
                "canif_pdu_prop": f"0x{props_:02X}",
                "checksum_gate": checksum_text,
                "com_pdu_id": pdu,
                "com_pdu_descriptor": f"0x{c['address']:06X}: timeout={c['timeout']} b1={c['b1']} b2={c['b2']} len={c['len']} flags=0x{c['flags']:02X}",
                "com_buf_off": c["buf_off"],
                "com_buf_ram": f"0x{COM_BUF_RAM + c['buf_off']:08X}",
                "com_validity_ram": f"0x{COM_VALID_RAM + pdu:08X}",
                "com_update_counter_ram": f"0x{COM_UPDATE_RAM + pdu:08X}",
                "route_entry": route_addr,
                "upper_route": ("SecOC ingress " if entry["hi"] != 0xFFFF else "COM RxIndication ") + route_target,
                "secoc_gate": (f"yes: profile {sec[0]['index']} @0x{sec[0]['address']:06X} data_id 0x{sec[0]['data_id']:03X}"
                               f" app_pdu {sec[0]['app_pdu']} upper_cb 0x{sec[0]['upper_cb']:06X}; COM delivery only through"
                               " 0x8F546 (success, or failure while the failure counter stays below"
                               f" CodeFlash[0x25842]=0x{u16(0x25842):04X})") if sec else "no",
                "configured_signals": (f"{summ['signals'][0]}..{summ['signals'][-1]} ({len(summ['signals'])})"
                                       if summ["signals"] else "none"),
                "extracted_bitfield_signals": summ["bitfield"],
                "opaque_signals": summ["opaque"],
                "no_extraction_signals": summ["none"],
                "unpackers": " ".join(f"0x{u:06X}" for u in unpackers),
                "signal_dest_ram": span(summ["dests"]),
                "first_consumer": f"0x{consumers[0]:06X}" if consumers else "none",
                "consumers": " ".join(f"0x{fe:06X}" for fe in consumers[:10]),
                "consumer_count": len(consumers),
                "handler_chain": " -> ".join(chain),
                "request_response": "no (periodic signal broadcast)",
                "memory_semantics": mem,
                "what_frame_controls": controls,
                "comma_bus0_delivery": (
                    "not deliverable: host CAN-FD from the comma does not reach F33 on the current topology (live negatives,"
                    " baseline 6, 57.10, 59, 60); a classic frame on the same ID passes the rule but matches no descriptor (dropped at 0x810F2)"
                    if fd else
                    "accepted (classic <= 8 bytes); deliverable from Panda bus 0 on the post-repin chassis segment"
                    " [INFERENCE: same RSCFD controller, RFIFO1 and ISR path as the live-proven UDS and XCP routes; per-ID live delivery not observed]"),
                "acceptance_constraints": ide_rule,
            })
        elif rule["index"] <= 45:
            j = rule["index"] - 43
            sw, length = diag_desc[j]
            assert sw == rule["id"], "diagnostic descriptor order drift"
            names = ["diagnostic physical UDS (0x7A1 -> 0x7A9)", "diagnostic functional UDS (0x777)",
                     "diagnostic secondary (0x7A0)"]
            base.update({
                "demux_class": names[j],
                "frame_format": f"classic (length {length})",
                "canif_descriptor_index": j,
                "canif_software_id": f"0x{sw:08X}",
                "canif_length": length,
                "canif_dlc_rule": f"slot-2 hook 0x7F3F8 and 0x{CANIF_DLC_CHECK:06X}: frame length <= {length} and <= 8",
                "canif_pdu_prop": "n/a",
                "checksum_gate": "no",
                "com_pdu_id": "none (not a COM PDU)",
                "com_pdu_descriptor": "none",
                "com_buf_off": "none",
                "com_buf_ram": "CanTp/DCM receive buffers only",
                "com_validity_ram": "n/a",
                "com_update_counter_ram": "n/a",
                "route_entry": f"CanIf diag route id 0x{0x800 | j:04X}",
                "upper_route": f"0x{DIAG_DEMUX:06X} -> 0x{CANTP_RX:06X}(0x{0x800 | j:04X}) -> cantp_receive_can_frame 0x7A57A -> 0x7A4E4 -> DCM 0x921D2",
                "secoc_gate": "no",
                "configured_signals": "none", "extracted_bitfield_signals": 0, "opaque_signals": 0,
                "no_extraction_signals": 0, "unpackers": "none", "signal_dest_ram": "CanTp/DCM buffers (not mapped here)",
                "first_consumer": "DCM main SID dispatch over the 17-SID table at 0x25C54 (baseline 13.4, 13.11-13.15)",
                "consumers": "0x007A57A 0x007A4E4 0x00921D2",
                "consumer_count": 3,
                "handler_chain": " -> ".join([
                    f"RSCFD rule {rule['index']} (label 0x{rule['label']:02X}, {base['rscfd_fifo']})",
                    "RX ISR 0x83D40 -> 0x83D14 -> 0x80B42 -> ring 0xFEBE4038 -> 0x808D6 -> 0x80884 (selector 0x04)",
                    f"0x81200 (slot 2, diag descriptor {j}) -> 0x7F3F8 hook -> 0x{CANTP_RX:06X}(0x{0x800 | j:04X})",
                    "cantp_receive_can_frame 0x7A57A -> 0x7A4E4 (PCI dispatch) -> dcm_receive_indication 0x921D2 -> DCM main (0x25C54 service table)"]),
                "request_response": "yes (UDS on ISO-TP)",
                "memory_semantics": "diagnostic only: SID 0x23 bounded RMBA read and SID 0x2E configured-DID write; no SID 0x2F/0x3D (baseline 13.4)",
                "what_frame_controls": "ISO-TP connection state and the DCM request buffer; control-transfer surface audited and closed in baseline 13.4-13.15",
                "comma_bus0_delivery": "yes: live-proven UDS route (0x7A1 physical: ELM327 param 1 on bus 1 pre-repin, on bus 0 post-repin; functional 0x777 live on bus 1)",
                "acceptance_constraints": ide_rule + "; routed to CFIFO5 by GAFLP1 bit 13",
            })
        else:
            sw, length = xcp_desc[0]
            assert sw == rule["gaflid"], "XCP descriptor drift"
            base.update({
                "demux_class": "XCP (extended)",
                "frame_format": f"classic (length {length})",
                "canif_descriptor_index": 0,
                "canif_software_id": f"0x{sw:08X}",
                "canif_length": length,
                "canif_dlc_rule": f"0x{XCP_STAGE:06X}: 1 <= length <= CodeFlash[0x22ABD]={u8(0x22ABD)}; otherwise dropped",
                "canif_pdu_prop": "n/a",
                "checksum_gate": "no",
                "com_pdu_id": "none (not a COM PDU)", "com_pdu_descriptor": "none", "com_buf_off": "none",
                "com_buf_ram": "XCP staging 0xFEBE4C34..0xFEBE4C73 (64 bytes cleared, then length bytes copied)",
                "com_validity_ram": "FEBE4EE6 (channel-0 enabled flag, must be 0x5A)", "com_update_counter_ram": "n/a",
                "route_entry": "n/a (slot-5 dispatcher, route id 0xF801)",
                "upper_route": f"0x{XCP_DEMUX:06X}(0xF801) -> 0x{XCP_STAGE:06X}(0) -> 0x82FEC -> [FEBE4EE6==0x5A] 0x{XCP_DISPATCH:06X} -> 0x830C0 -> 0x98E80",
                "secoc_gate": "no",
                "configured_signals": "none", "extracted_bitfield_signals": 0, "opaque_signals": 0,
                "no_extraction_signals": 0, "unpackers": "none", "signal_dest_ram": "0xFEBE4C34..0xFEBE4C73",
                "first_consumer": f"0x{XCP_DISPATCH:06X} -> 0x830C0 -> 0x98E80 (returns 1 while fixed CodeFlash[0x30D68]=0x{u8(0x30D68):02X}, so no opcode dispatch)",
                "consumers": f"0x{XCP_DISPATCH:06X} 0x00830C0 0x0098E80",
                "consumer_count": 3,
                "handler_chain": " -> ".join([
                    f"RSCFD rule {rule['index']} (label 0x{rule['label']:02X}, {base['rscfd_fifo']})",
                    "RX ISR 0x83E0C -> 0x83D14 -> 0x80B42 -> ring 0xFEBE4038 -> 0x808D6 -> 0x80884 (selector 0x20)",
                    f"0x81072 (slot 5, descriptor 0x9FDC0002) -> 0x{XCP_DEMUX:06X}(0xF801) -> 0x{XCP_STAGE:06X}(0)",
                    f"0x82FEC -> [FEBE4EE6==0x5A] 0x{XCP_DISPATCH:06X} -> 0x830C0 -> 0x98E80 (blocked by CodeFlash[0x30D68]=0x5A)"]),
                "request_response": "yes (XCP on CAN)",
                "memory_semantics": ("read/write protocol: SET_MTA 0x82C62, DOWNLOAD 0x81FFE, MODIFY_BITS 0x820C4, SHORT_UPLOAD 0x82B1A;"
                                     " validator 0x98F2C admits 0xFEBF7C00..0xFEBFFBFF (baseline 13.5); command dispatch is compiled out by fixed CodeFlash[0x30D68]=0x5A"),
                "what_frame_controls": "up to 8 staging bytes at 0xFEBE4C34 (live-proven 2026-09-06 marker); no command executes",
                "comma_bus0_delivery": "yes: live-proven classic extended marker on post-repin Panda bus 0 (baseline 6, 73.3); FD forms of the same ID do not arrive",
                "acceptance_constraints": ide_rule + "; an FD frame on the same ID is dropped at 0x81072 (no 0xDFDC0002 descriptor)",
            })
        rows_out.append(base)
    # classic 8-byte IDs first, then CAN-FD, then extended
    def rank(r):
        if r["id_format"] == "extended":
            return (2, r["rule_index"])
        return (1, r["rule_index"]) if r["frame_format"].startswith("CAN-FD") else (0, r["rule_index"])
    rows_out.sort(key=rank)

    # ------------------------------------------------------------------
    # write outputs
    # ------------------------------------------------------------------
    columns = list(rows_out[0].keys())
    with (out_dir / "application_rx_map.csv").open("w", newline="", encoding="utf-8") as stream:
        w = csv.DictWriter(stream, fieldnames=columns)
        w.writeheader()
        for r in rows_out:
            w.writerow(r)

    sig_cols = [k for k in signal_rows[0] if not k.startswith("_")]
    with (out_dir / "application_rx_signal_evidence.csv").open("w", newline="", encoding="utf-8") as stream:
        w = csv.DictWriter(stream, fieldnames=sig_cols)
        w.writeheader()
        for r in signal_rows:
            w.writerow({k: r[k] for k in sig_cols})

    tables = {
        "image_sha256": digest,
        "acceptance_rules": [{k: v for k, v in r.items()} for r in rules],
        "callbacks": [f"0x{x:06X}" for x in callbacks],
        "slot_structs": [f"0x{x:06X}" for x in slot_structs],
        "slot_base": slot_base, "slot_bank": [f"0x{x:04X}" for x in slot_bank], "route_counts": route_counts,
        "normal_rx_descriptors": [{"index": i, "software_id": f"0x{sw:08X}", "length": ln} for i, (sw, ln) in enumerate(normal_desc)],
        "diag_rx_descriptors": [{"index": i, "software_id": f"0x{sw:08X}", "length": ln} for i, (sw, ln) in enumerate(diag_desc)],
        "xcp_rx_descriptor": {"software_id": f"0x{xcp_desc[0][0]:08X}", "length": xcp_desc[0][1]},
        "canif_pdu_props": [f"0x{x:02X}" for x in pdu_props],
        "route_slot0": [{"address": f"0x{r['address']:06X}", "word": f"0x{r['word']:08X}"} for r in route0],
        "route_slot1": [{"address": f"0x{r['address']:06X}", "word": f"0x{r['word']:08X}"} for r in route1],
        "com_pdus": [{k: (f"0x{v:06X}" if k == "address" else v) for k, v in c.items()} for c in com],
        "secoc": secoc,
        "signal_to_pdu": s2p,
        "extraction_call_sites": len(extraction_sites),
        "bitfield_rows": len(bitfield_rows),
        "table_driven_rows": len(table_rows),
        "opaque_rows": len(opaque_rows),
        "unparsed_sites": remaining_unparsed,
        "opaque_table": [
            {k: (f"0x{v:06X}" if isinstance(v, int) and k in ("signal_table", "offset_table", "gen_table", "call_site", "collector") else v)
             for k, v in r.items()} for r in opaque_rows],
        "table_driven_table": [
            {k: (f"0x{v:06X}" if isinstance(v, int) and k in ("call_site", "unpacker", "dest", "persist_site") else v)
             for k, v in r.items()} for r in table_rows],
    }
    (out_dir / "tables.json").write_text(json.dumps(tables, indent=1, default=str) + "\n", encoding="utf-8")

    cls = Counter(r["classification"] for r in signal_rows)
    print(f"functions={len(funcs)} instructions={len(ins_list)}")
    print(f"extraction call sites={len(extraction_sites)} bitfield={len(bitfield_rows)} table-driven={len(table_rows)} "
          f"unparsed={len(remaining_unparsed)} opaque={len(opaque_rows)}")
    print("signal classification:", dict(cls))
    for r in rows_out:
        print(r["rule_index"], r["can_id"], r["demux_class"], r["frame_format"], r["com_pdu_id"],
              r["extracted_bitfield_signals"], r["opaque_signals"], r["no_extraction_signals"], r["secoc_gate"][:12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
