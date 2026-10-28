#!/usr/bin/env python3
"""CanTp ingress fuzzer for camry-8965F3307000 (F33 EPS) on the GNU sim.

Drives `cantp_receive_can_frame` @ ENTRY with raw (canif_id, PduInfo) pairs and
diffs a full RAM window dump per trial against the primed start image. Any
write outside the legitimate envelope (firmware write sites + calibration
bookkeeping) is a candidate memory-safety finding; magic-value materialization
of the RWX pocket addresses is flagged outright.

Container path note: `run_elf` mounts the ELF's parent directory at /out
read-write inside the container, so every restore/dump path in the GDB script
must be /out-relative.
"""

import argparse
import hashlib
import json
import random
import re
from collections import Counter
from collections.abc import Callable, Iterator, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TypeVar

from tools import REPO_ROOT
from tools.rh850_codeflash import CodeFlashSimError, run, run_elf

IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/cantp-ingress-fuzz"

ENTRY = 0x7A57A            # cantp_receive_can_frame(canif_receive_id, F33PduInfo*)
SENTINEL = 0x798
GP = 0xFEBEB800
STACK_TOP = 0xFEBE2000
RAM_BASE, RAM_SIZE = 0xFEBE0000, 0x20000
RAM_REGION = f"{RAM_BASE:#x},{RAM_SIZE:#x}"

CANTP_ENABLE = 0xFEBE4F3D
PDU_INFO = 0xFEBE40E0      # F33PduInfo {u32 data; u16 length; u16 opaque}
FRAME_BUF = 0xFEBE4100
CELL_BASE = 0xFEBE4F40     # + 0x20*channel_state_index; RxState at +0x10
# (canif_receive_id, state_index, receive_id)
CONNECTIONS = ((0x804, 0, 0x802), (0x805, 1, 0x803), (0x806, 2, 0x804))
TP_BASE = 0x23DFC          # tp - 0x118C = 0x22C70 (F33CanTpConfiguration); the sim
                           # decodes tp-relative encodings as r5, so r5 is primed instead.
DCM_COMM_MODE = 0xFEBE564C # communication slots 0/1 (routes' communication_slot); 2 = full
DCM_SLOT_STATE = 0xFEBE59F0  # F33DcmReceiveBufferState[3], stride 16: cursor@+0 len@+4 rem@+8 recv@+0xA
DCM_SLOT_REMAINING = tuple(DCM_SLOT_STATE + 0x10 * i + 8 for i in range(3))
DCM_PENDING_SLOT = 0xFEBE59E0   # u16 pending-dispatch slot; lifecycle-managed by Dcm
                               # (boot zero; zero-fill implicitly supplied it, the dcm
                               # harness primes it explicitly for dispatcher trials)
DCM_REQUEST_PHASE = 0xFEBE5960  # dcm request phase; 0/1 are receiving-capable, 2 dispatches
                               # (pattern fill silently broke FF claims until this was primed)
RESET_TX_STATE = bytes.fromhex("00000000ffff0000e1ff000000000000")
RESET_RX_STATE = bytes.fromhex("00000000ffff00000000e100ff00f000")
RESET_CELL = RESET_TX_STATE + RESET_RX_STATE
# Legitimate write envelope (start, end) inclusive, from recovered firmware
# structure; calibration extends it with observed Dcm bookkeeping writes.
STATIC_ENVELOPE = (
    (0xFEBE1800, 0xFEBE1FFF),   # dispatch call-stack scratch below STACK_TOP
    (0xFEBE39C0, 0xFEBE3DFF),   # Dcm software-timer table + lock (gp-0x7E24 cluster)
    (0xFEBE4EFC, 0xFEBE4F3F),   # shared frame scratch + fault nibble + enable
    (0xFEBE4F40, 0xFEBE4FB1),   # channel cells + flow parameters
    (0xFEBE5641, 0xFEBE5950),   # three Dcm receive buffers with slack
    (0xFEBE5951, 0xFEBE59EF),   # Dcm post-buffer bookkeeping (inactivity/response cells)
    (0xFEBE5E70, 0xFEBE5EBF),   # Dcm software-timer cells (gp-0x5988+slot*8, slot<9)
    (0xFEBE59F0, 0xFEBE5A20),   # Dcm buffer state row
)

MAGIC_VALUES = (0xFEBFF9F0, 0xFEF07C00)

# ------------------------------------------------------- strong oracle (v3)
# The historical zero fill made every zeroing write outside the envelope
# invisible and masked uninitialized reads. The address-derived pattern
# fill turns untouched RAM into markers: zeroing stores stay visible,
# untouched buffers stay distinguishable from written ones, and 4-byte
# marker words copied into consumer buffers expose reads of
# never-initialized RAM (CWE-457 propagation).

_PATTERN_CACHE: dict[int, bytes] = {}
_PATTERN_WORD_INDEX: dict[int, dict[bytes, int]] = {}


def _splitmix32(x: int) -> int:
    x = (x + 0x9E3779B9) & 0xFFFFFFFF
    x ^= x >> 16
    x = (x * 0x85EBCA6B) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 0xC2B2AE35) & 0xFFFFFFFF
    x ^= x >> 16
    return x


def pattern_image(salt: int = 0) -> bytes:
    """Word-stream marker image: every aligned 4-byte window equals a
    splitmix32 word unique to its address. A per-byte hash would repeat
    with period 256 and make every untouched byte "match" its own
    address + 256 — the first oracle draft did exactly that."""
    if salt not in _PATTERN_CACHE:
        words = [_splitmix32(addr ^ (salt << 20))
                 for addr in range(RAM_BASE, RAM_BASE + RAM_SIZE, 4)]
        _PATTERN_CACHE[salt] = b"".join(w.to_bytes(4, "little") for w in words)
    return _PATTERN_CACHE[salt]


def pattern_word_index(salt: int = 0) -> dict[bytes, int]:
    if salt not in _PATTERN_WORD_INDEX:
        image = pattern_image(salt)
        _PATTERN_WORD_INDEX[salt] = {
            image[i:i + 4]: RAM_BASE + i for i in range(0, RAM_SIZE, 4)
        }
    return _PATTERN_WORD_INDEX[salt]


def pattern_propagation(dump: bytes, ranges: tuple[tuple[int, int], ...]) -> list[dict]:
    """Aligned 4-byte windows in consumer buffers that are verbatim marker
    words from never-initialized RAM (uninitialized-read propagation)."""
    index = pattern_word_index()
    hits: list[dict] = []
    for lo, hi in ranges:
        base_off = lo - RAM_BASE
        seg = dump[base_off:hi - RAM_BASE + 1]
        for off in range((-base_off) % 4, len(seg) - 3, 4):
            source = index.get(seg[off:off + 4])
            if source is not None and abs(source - (lo + off)) > 4:
                hits.append({"consumer": hex(lo + off), "source": hex(source)})
                if len(hits) >= 16:
                    return hits
    return hits

# Access-time fences: bytes no legitimate store touches in this harness's
# scope. A watchpoint hit stops with the faulting PC (Fuzzware-style
# access-time detection) instead of waiting for the post-hoc diff.
FENCES = (
    (0xFEBE17FF, "stack-underflow"),      # below the enveloped foreground stack band
    (0xFEBE2000, "stack-overflow-up"),    # at/above SP start; the stack grows down
    (0xFEBE5D20, "response-buffer-end"),  # first byte past configured 0x300-byte buffer
    (0xFEBE4FB2, "post-channel-cells"),   # gap after CanTp cells + flow parameters
)

SLOT_RANGES = tuple((0xFEBE5651 + 0x100 * i, 0xFEBE5750 + 0x100 * i) for i in range(3))




def slot_invariants(dump: bytes, slots: frozenset[int]) -> list[str]:
    """Capacity sanity of firmware-driven slot-state rows for the slots a
    trial actually addresses. Fields: write_cursor u32 pointer @+0,
    received_length u16 @+4, remaining_capacity u16 @+8. Rows the firmware
    never drove still hold their marker words and are skipped."""
    bad = []
    marker = pattern_image()
    for slot in sorted(slots):
        row = DCM_SLOT_STATE + 0x10 * slot - RAM_BASE
        if dump[row:row + 8] == marker[row:row + 8]:
            continue                     # frame was ignored; row untouched
        cursor = int.from_bytes(dump[row:row + 4], "little")
        length = int.from_bytes(dump[row + 4:row + 6], "little")
        remaining = int.from_bytes(dump[row + 8:row + 10], "little")
        buf = SLOT_RANGES[slot][0]
        cursor_ok = (buf <= cursor <= buf + 0x100) or cursor <= 0x100
        if not cursor_ok or length > 0x100 or remaining > 0x100:
            bad.append(f"slot{slot}:cursor={cursor:#x} len={length:#x} rem={remaining:#x}")
    return bad


def slots_touched(trial: "Trial") -> frozenset[int]:
    ids = {frame.canif_id for frame in trial.frames}
    return frozenset(idx for cid, idx, _rid in CONNECTIONS if cid in ids)


def untouched_slots(trial: "Trial") -> list[tuple[int, int]]:
    """Slot buffers and state rows a trial never addresses; any write there
    is cross-talk. The contiguous envelope would otherwise hide the bleed."""
    touched = slots_touched(trial)
    blocked: list[tuple[int, int]] = []
    for idx in range(3):
        if idx not in touched:
            blocked.append(SLOT_RANGES[idx])
            blocked.append((DCM_SLOT_STATE + 0x10 * idx, DCM_SLOT_STATE + 0x10 * idx + 11))
    return blocked




RX_LINE = re.compile(r"^TPR (\d+) (\d+)$", re.MULTILINE)


@dataclass(frozen=True)
class Frame:
    canif_id: int
    dlc: int
    data: bytes

    def hex8(self) -> str:
        return self.data.ljust(8, b"\x00")[:8].hex()


@dataclass(frozen=True)
class Trial:
    family: str
    frames: tuple[Frame, ...]
    rx_state: bytes | None = None   # 16 B primed into the first frame's channel cell RxState
    cell_lead: int = 0              # byte primed at the cell base (TxState prefix)
    tx_state: bytes | None = None   # full 16 B TxState prefix at the cell base
    extra_primes: tuple[tuple[int, bytes], ...] = ()   # DCM/global state outside the cell


def sf(cid: int, n: int, payload: bytes = b"", dlc: int | None = None) -> Frame:
    return Frame(cid, dlc if dlc is not None else 8, (bytes([n]) + payload.ljust(7, b"\x00"))[:8])


def ff(cid: int, length: int, payload: bytes = b"", dlc: int | None = None) -> Frame:
    data = bytes([0x10 | ((length >> 8) & 0x0F), length & 0xFF]) + payload.ljust(6, b"\x00")
    return Frame(cid, dlc if dlc is not None else 8, data[:8])


def cf(cid: int, seq: int, payload: bytes = b"", dlc: int | None = None) -> Frame:
    return Frame(cid, dlc if dlc is not None else 8, (bytes([0x20 | (seq & 0x0F)]) + payload.ljust(7, b"\x00"))[:8])


def rx_state(*, receive_id: int = 0, remaining: int = 0, ticks: int = 0, wait: int = 0,
             state: int = 0, ff_dlc: int = 0, seq: int = 0, block_remaining: int = 0,
             flow: int = 0, admission: int = 0) -> bytes:
    b = bytearray(16)
    b[0x00:4] = remaining.to_bytes(4, "little")
    b[0x04:6] = receive_id.to_bytes(2, "little")
    b[0x06:8] = ticks.to_bytes(2, "little")
    b[0x08:10] = wait.to_bytes(2, "little")
    b[0x0A], b[0x0B], b[0x0C] = state, ff_dlc, seq
    b[0x0D], b[0x0E], b[0x0F] = block_remaining, flow, admission
    return bytes(b)

def tx_state(*, remaining: int = 0x10, transmit_id: int = 0, timeout: int = 0x3E8,
             state: int = 0xB4, seq: int = 1, block_remaining: int = 0,
             block_size: int = 0, spacing: int = 0) -> bytes:
    """16-byte TxState cell prefix (scout TxPathMap field layout)."""
    b = bytearray(16)
    b[0x00:4] = remaining.to_bytes(4, "little")
    b[0x04:6] = transmit_id.to_bytes(2, "little")
    b[0x06:8] = timeout.to_bytes(2, "little")
    b[0x08], b[0x09] = state, seq
    b[0x0A], b[0x0B], b[0x0C] = block_remaining, block_size, spacing
    return bytes(b)


def cf_stream(cid: int, length: int, payload_head: bytes = b"\x22\xf1\x81") -> tuple[Frame, ...]:
    """FF plus sequential CFs; each CF carries distinct bytes so cross-slot
    bleed names its source frame."""
    frames = [ff(cid, length, payload_head)]
    remaining, sn, mark = length - 6, 1, 0x40
    while remaining > 0:
        n = min(7, remaining)
        frames.append(cf(cid, sn, bytes((mark + i) & 0xFF for i in range(n))))
        remaining -= n
        sn = (sn + 1) & 0x0F
        mark = (mark + 8) & 0xFF
    return tuple(frames)



def cell_for(canif_id: int) -> int | None:
    for cid, idx, _rid in CONNECTIONS:
        if cid == canif_id:
            return CELL_BASE + 0x20 * idx
    return None


# ---------------------------------------------------------------- generation

def generate(seed: int, random_each: int) -> list[Trial]:
    multi, single, blk1 = (c[0] for c in CONNECTIONS)
    rid_multi = CONNECTIONS[0][2]
    items: list[Trial] = []
    for cid in (multi, single, blk1):
        for nib in range(16):
            items.append(Trial("sf_nibble", (sf(cid, nib, b"\x22\xf1\x81"),)))
        for nib in (0, 1, 7):
            for dlc in (0, 1, 2, 3, 7, 8, 9, 15, 0x3F, 0xFF):
                items.append(Trial("sf_dlc", (sf(cid, nib, b"\x22\xf1\x81", dlc=dlc),)))
    for payload_len in (0x07, 0xFF):
        items.append(Trial("sf_escape", (Frame(multi, 8, bytes([0x00, payload_len]) + b"\x22\xf1\x81\x00\x00\x00"),)))
    for length in (0, 1, 6, 7, 8, 9, 0x32, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE, 0xFF,
                   0x0FFF - 6, 0x0FFF - 7, 0x0FFF, 0x1000 - 6):
        items.append(Trial("ff_length", (ff(multi, length, b"\x22\xf1\x81"),)))
    for dlc in (0, 1, 2, 7, 8, 9, 15, 0xFF):
        items.append(Trial("ff_dlc", (ff(multi, 0x0B, b"\x22\xf1\x81", dlc=dlc),)))
    items.append(Trial("ff_on_single", (ff(single, 0x0B, b"\x22\xf1\x81"),)))
    ff_ok = ff(multi, 0x0B, b"\x22\xf1\x81")
    for seq in range(16):
        items.append(Trial("cf_seq", (ff_ok, cf(multi, seq, b"\x00" * 7))))
    for remaining in (0, 1, 6, 7, 8, 0xFF, 0x100, 0xFFF, 0xFFFFFFFF):
        items.append(Trial("cf_remaining", (cf(multi, 1, b"\x00" * 7),),
                           rx_state(receive_id=rid_multi, remaining=remaining, state=0x4B, seq=1)))
    for block_remaining in (0, 1, 0xFF):
        items.append(Trial("cf_block", (cf(multi, 1, b"\x00" * 7),),
                           rx_state(receive_id=rid_multi, remaining=7, state=0x4B,
                                    seq=1, block_remaining=block_remaining)))
    for st in (0x30, 0x31, 0x32, 0x3F):
        items.append(Trial("fc", (Frame(multi, 8, bytes([st, 0x0F, 0x0A]) + b"\x00" * 5),)))
    items.append(Trial("interleave", (ff_ok, cf(single, 1, b"\x00" * 7), cf(multi, 1, b"\x00" * 7))))
    items.append(Trial("ff_restart", (ff_ok, ff(multi, 0x20, b"\x22\xf1\x81"), cf(multi, 1, b"\x00" * 7))))
    # Streamed multi-frame assembly across the slot-capacity boundary (0x100).
    for length in (7, 0x0D, 0x40, 0xF8, 0xFE, 0xFF, 0x100, 0x101, 0x108, 0x110, 0x1F8):
        items.append(Trial(f"ff_assemble_{length:#x}", cf_stream(multi, length)))
    # DoCAN A2: completed stream plus surplus CFs.
    items.append(Trial("cf_oversupply", cf_stream(multi, 0x100)
                       + (cf(multi, 0, b"\xC0" * 7), cf(multi, 1, b"\xC1" * 7))))
    # DoCAN A6: SF override mid-reception; A5: SN skip / SN repeat.
    items.append(Trial("sf_override_mid", (ff(multi, 0x40, b"\x22\xf1\x81"),
                                           cf(multi, 1, b"\x41" * 7),
                                           sf(multi, 2, b"\x10\x03"),
                                           cf(multi, 2, b"\x43" * 7),
                                           cf(multi, 3, b"\x44" * 7))))
    items.append(Trial("sn_skip", (ff(multi, 0x40, b"\x22\xf1\x81"),
                                   cf(multi, 1, b"\x41" * 7), cf(multi, 3, b"\x43" * 7),
                                   cf(multi, 4, b"\x44" * 7), cf(multi, 5, b"\x45" * 7))))
    items.append(Trial("sn_repeat", (ff(multi, 0x40, b"\x22\xf1\x81"),
                                     cf(multi, 1, b"\x41" * 7), cf(multi, 1, b"\x42" * 7),
                                     cf(multi, 2, b"\x43" * 7))))
    items.append(Trial("fc_mid_stream", (ff(multi, 0x40, b"\x22\xf1\x81"),
                                         cf(multi, 1, b"\x41" * 7),
                                         Frame(multi, 8, bytes((0x30, 0x00, 0x00)) + b"\x00" * 5),
                                         cf(multi, 2, b"\x43" * 7), cf(multi, 3, b"\x44" * 7))))
    # TX side (DoCAN A7/A4): FC frames against a live transmitter. Connection
    # identities are the ROM tx-connection rows (0x22B9E: transmit_id 0x800,
    # FC-receive 0x804; 0x22BBE: 0x801/0x806). All three channel cells get an
    # armed TxState so whichever cell the connection maps to is live.
    def tx_fc_trial(cid: int, tid: int, state: int, block_size: int,
                    fs: int, bs: int, stmin: int, transport: int) -> Trial:
        armed = tx_state(remaining=0x10, transmit_id=tid, state=state, block_size=block_size)
        return Trial(
            f"tx_fc_{cid:#x}_{state:#x}_{fs}_{bs:#x}_{stmin:#x}",
            (Frame(cid, 8, bytes((0x30 | fs, bs, stmin)) + b"\x00" * 5),),
            rx_state=rx_state(remaining=0, state=0x5A),
            tx_state=armed,
            extra_primes=tuple((CELL_BASE + 0x20 * idx, armed) for idx in range(3)) + (
                (0xFEBE5978, 0xFEBE5A20.to_bytes(4, "little")),  # resp queue cursor
                (0xFEBE597C, (0x10).to_bytes(4, "little")),       # resp queue remaining
                (0xFEBE5964, bytes([transport])),                 # transport state
                (0xFEBE5A20, b"\x59\x02\x11" + b"\x00" * 13),     # response head
                # coherent one-node response queue (TX teardown walks it):
                (0xFEBE5970, 0xFEBE5984.to_bytes(4, "little")),   # sentinel -> node
                (0xFEBE5974, 0xFEBE5984.to_bytes(4, "little")),   # tail -> node
                (0xFEBE5980, b"\x00\x00"),                        # notification result/pending
                (0xFEBE5984, 0xFEBE5970.to_bytes(4, "little")),   # node.next -> sentinel
                (0xFEBE5988, 0xFEBE5A20.to_bytes(4, "little")),   # node.data
                (0xFEBE598C, (0x10).to_bytes(2, "little")),       # node.length
                (0xFEBE5990, b"\x00"),                            # node.disposition
                (0xFEBE59E2, b"\x00\x00"),   # current receive-route index (TX teardown)
            ))

    for fs, bs, stmin, transport in ((0, 0, 0, 0x31), (0, 1, 1, 0x31), (0, 0xFF, 0xFF, 0x31),
                                     (1, 0, 0, 0x30), (1, 1, 0xF1, 0x31), (2, 0, 0, 0x32),
                                     (3, 0, 0, 0x31), (3, 0xFF, 0xFF, 0x32), (0xF, 0, 0, 0x31),
                                     (0, 1, 0xF1, 0x40), (2, 0xFF, 1, 0x30), (0, 0xFF, 0, 0x40)):
        items.append(tx_fc_trial(multi, 0x800, 0xB4, 0, fs, bs, stmin, transport))
    items.append(tx_fc_trial(multi, 0x800, 0xA5, 0, 0, 1, 1, 0x31))            # WAIT-state CTS
    items.append(tx_fc_trial(multi, 0x800, 0x87, 1, 0, 0, 0, 0x31))            # next-block race
    items.append(tx_fc_trial(blk1, 0x801, 0xA5, 0, 1, 0xFF, 0xF1, 0x32))       # conn 1 WAIT
    rng = random.Random(seed)
    for _ in range(random_each):
        cid = rng.choice(CONNECTIONS)[0]
        frames = tuple(
            Frame(cid, rng.choice((0, 1, 2, 3, 7, 8, 9, 15, 0x3F, 0xFF)),
                  bytes(rng.randrange(256) for _ in range(8)))
            for _ in range(rng.randrange(1, 4)))
        if rng.randrange(4) == 0:
            frames = (Frame(rng.randrange(0x800, 0x900), 8, bytes(rng.randrange(256) for _ in range(8))),) + frames
        state = None
        if rng.randrange(2):
            state = rx_state(receive_id=rng.choice((0x802, 0x803, 0x804, rng.randrange(0x10000))),
                             remaining=rng.choice((0, 1, 7, 0x40, 0x100, 0xFFFF, rng.randrange(1 << 32))),
                             state=rng.choice((0, 0x4B, 0x5A, 0x69, rng.randrange(256))),
                             seq=rng.randrange(256), block_remaining=rng.randrange(256),
                             flow=rng.randrange(256), admission=rng.randrange(256))
        items.append(Trial("random", frames, state, cell_lead=rng.choice((0, 1, 0x5A, 0xFF))))
    return items



CALIBRATION: list[tuple[str, tuple[Frame, ...]]] = [
    ("sf_single", (sf(0x805, 2, b"\x10\x03"),)),
    ("ff_cf_multi", (ff(0x804, 0x0B, b"\x22\xf1\x81"), cf(0x804, 1, b"\x00" * 7),
                       cf(0x804, 2, b"\x00"))),
    ("sf_blk1", (sf(0x806, 3, b"\x22\xf1\x81"),)),
]


# ------------------------------------------------------------- GDB scripting

def trial_image(trial: Trial, salt: int | None = None) -> bytes:
    """Primed start image for one trial; doubles as the expected post image.

    salt=None keeps the historical zero fill; an int selects the
    address-derived pattern fill (strong oracle, schema v3).
    """

    def wr(addr: int, data: bytes) -> None:
        image[addr - RAM_BASE:addr - RAM_BASE + len(data)] = data

    if salt is None:
        image = bytearray(RAM_SIZE)
    else:
        image = bytearray(pattern_image(salt))

    wr(CANTP_ENABLE, b"\xAA\x00")
    wr(DCM_COMM_MODE, b"\x02\x00\x02\x00")   # communication slots 0/1 = full communication (2)
    wr(DCM_PENDING_SLOT, b"\x00\x00")      # pending-dispatch slot: boot zero either way
    for addr in DCM_SLOT_REMAINING:          # claim does not initialize capacity; boot does
        wr(addr, (0x100).to_bytes(4, "little"))
    if salt is not None:
        # Exact channel-cell and flow-row reset from
        # reset_cantp_channels_and_seed_flow_parameters @ 0x7B2C4.
        for index in range(3):
            wr(CELL_BASE + 0x20 * index, RESET_CELL)
        wr(CELL_BASE + 0x60, b"\x00" * 12)
        # Exact Dcm receive/deadline reset from
        # dcm_initialize_receive_buffers_and_transport_state @ 0x93ABA.
        wr(0xFEBE59D8, b"\x00" * (0x59ED - 0x59D8))
        # Lifecycle reconstruction belongs to pattern-fill runs: zero-fill
        # images stay byte-identical to the historical state model.
        wr(DCM_REQUEST_PHASE, b"\x00\x00")     # receiving-capable phase
        for slot in range(3):                  # coherent idle rows as boot leaves them:
            base = 0xFEBE5651 + 0x100 * slot   # cursor=base, len=0, rem=0x100, recv/abort=0
            row = DCM_SLOT_STATE + 0x10 * slot
            wr(row, base.to_bytes(4, "little"))
            wr(row + 4, b"\x00\x00")           # received_length = 0
            wr(row + 8, (0x100).to_bytes(2, "little"))
            wr(row + 0xA, b"\x00\x00")         # receiving = 0, abort_pending = 0
    cell = cell_for(trial.frames[0].canif_id)
    if cell is not None:
        tx_base = RESET_TX_STATE if salt is not None else b"\x00" * 16
        wr(cell, bytes([trial.cell_lead]) + tx_base[1:])
        if trial.rx_state is not None:
            wr(cell + 0x10, trial.rx_state)
        if trial.tx_state is not None:
            wr(cell, trial.tx_state)   # full TxState prefix overrides cell_lead
    for addr, data in trial.extra_primes:
        wr(addr, data)
    last = trial.frames[-1]
    wr(FRAME_BUF, bytes.fromhex(last.hex8()))
    wr(PDU_INFO, FRAME_BUF.to_bytes(4, "little") + last.dlc.to_bytes(2, "little") + b"\x00\x00")
    return bytes(image)



# Sink sites instrumented with silent logging breakpoints; their hit counts
# prove which copy sinks each trial family actually reaches. Breakpoint 1 is
# the SENTINEL stop, sinks take 2..1+len(SINKS), fence watches follow.
SINKS = (
    (0x7A8E8, "cantp_copy_upper_receive_bytes"),
    (0x7AD64, "cantp_start_upper_receive"),
    (0x7B74E, "cantp_build_consecutive_frame"),
    (0x7BA32, "cantp_apply_flow_control"),
    (0x7B894, "cantp_run_transmit_channels"),
    (0x920BE, "dcm_start_of_reception"),
    (0x92152, "dcm_copy_receive_data"),
    (0x926D2, "dcm_copy_transmit_data"),
    (0x93DE8, "dcm_append_receive_chunk"),
    (0x9449E, "dcm_dispatch_did_length_callback"),
    (0x95674, "execute_write_did_payload_and_report_result"),
    (0x95FB4, "dcm_serialize_read_did_body"),
    (0x96410, "execute_memory_read_and_report_result"),
    (0x8BD7C, "diag_routine_run_action_phase"),
)
REQUIRED_SINKS = (
    "cantp_copy_upper_receive_bytes",
    "cantp_start_upper_receive",
    "cantp_apply_flow_control",
    "dcm_start_of_reception",
    "dcm_copy_receive_data",
    "dcm_append_receive_chunk",
)


def sink_break_commands() -> list[str]:
    commands: list[str] = []
    for number, (addr, name) in enumerate(SINKS, start=2):
        commands += [f"break *{addr:#x}", f"commands {number}", "silent",
                     f'printf "SINK {name}\\n"', "continue", "end"]
    return commands


SINK_STREAM_RE = re.compile(r"^SINK (\S+)$|^TPR (\d+) \d+$", re.MULTILINE)


def attribute_sinks(output: str) -> dict[int, Counter]:
    """Map each trial index to the sinks hit while it ran (sink prints
    precede the trial's own TPR line)."""
    hits: dict[int, Counter] = {}
    pending: Counter = Counter()
    for match in SINK_STREAM_RE.finditer(output):
        if match.group(1):
            pending[match.group(1)] += 1
        else:
            hits[int(match.group(2))] = pending
            pending = Counter()
    return hits


def trial_script(index: int, trial: Trial) -> list[str]:
    commands = [f'restore /out/img-{index:06d}.bin binary {RAM_BASE:#x}']
    # Fences are armed after each restore so the restored marker value is
    # the baseline; a hit stops with the faulting PC. Each watchpoint's
    # number is captured in a convenience var; batch_script deletes exactly
    # those (gdb assigns numbers monotonically, never reusing freed ones).
    for fence_number, (addr, _name) in enumerate(FENCES):
        commands += [f"watch *(unsigned char*){addr:#x}", f"set $fence{fence_number} = $bpnum"]
    for position, frame in enumerate(trial.frames):
        data = bytes.fromhex(frame.hex8())
        commands.extend((
            f"set {{unsigned int}}{FRAME_BUF:#x}={int.from_bytes(data[0:4], 'little'):#x}",
            f"set {{unsigned int}}{FRAME_BUF + 4:#x}={int.from_bytes(data[4:8], 'little'):#x}",
            f"set $r3={STACK_TOP:#x}", f"set $r31={SENTINEL:#x}",
            f"set $r5={TP_BASE:#x}", f"set $tp={TP_BASE:#x}",
            f"set $r6={frame.canif_id}", f"set $r7={PDU_INFO:#x}",
            f"set $pc={ENTRY:#x}",
            "continue",
        ))
        # Grant flow status between an FF and its CFs: on hardware the periodic
        # channel task moves the post-FF RxState ('i') to 'Z'/flow-0xF0 once
        # Dcm grants capacity; the CF gate requires it.
        nxt = trial.frames[position + 1] if position + 1 < len(trial.frames) else None
        if nxt is not None and (nxt.data[0] & 0xF0) == 0x20:
            grant = cell_for(nxt.canif_id)
            if grant is not None:
                commands.extend((
                    f"set {{unsigned char}}{grant + 0x10 + 0xA:#x}=0x5A",   # state 'Z'
                    f"set {{unsigned char}}{grant + 0x10 + 0xE:#x}=0xF0",   # flow status
                ))
    commands.extend((
        f"dump binary memory /out/tp-{index:06d}.bin {RAM_BASE:#x} {RAM_BASE + RAM_SIZE:#x}",
        f'printf "TPR {index} %u\\n", $pc',
        f"set $pc={SENTINEL:#x}",
    ))
    return commands


def batch_script(batch: list[tuple[int, Trial]]) -> list[str]:
    commands = [
        f"set $r4={GP:#x}", f"set $r3={STACK_TOP:#x}", f"set $r31={SENTINEL:#x}",
        f"set $r5={TP_BASE:#x}", f"set $tp={TP_BASE:#x}",
        # The GNU sim does not implement `stsr PMR`; neuter the two compiler
        # runtime thunks that read/restore it (0x6A45E push, 0x6A4C4 pop) so
        # Dcm timer arming does not SIGILL. Sim-only byte patch, not firmware.
        # GDB writes target-endian u16; 0x007f yields bytes 7f 00 = jmp [lp].
        "set {unsigned short}0x6a45e = 0x007f", "set {unsigned short}0x6a4c4 = 0x007f",
        f"break *{SENTINEL:#x}",
        *sink_break_commands(),
        # Harmless warmup dispatch (unknown canif id) satisfies the executor's
        # leading-continue requirement and initializes the module.
        f"set {{unsigned short}}{PDU_INFO + 4:#x}=0", "set $r6=0xFFFF", f"set $r7={PDU_INFO:#x}",
        f"set $pc={ENTRY:#x}",
        "continue",
    ]
    delete_fences = "delete " + " ".join(f"$fence{i}" for i in range(len(FENCES)))
    for position, (index, trial) in enumerate(batch):
        if position:
            commands.append(delete_fences)   # fence watchpoints from the prior trial
        commands.extend(trial_script(index, trial))
    commands.append(f'printf "TP_END={batch[-1][0]}\\n"')
    return commands

_Item = TypeVar("_Item")
_Result = TypeVar("_Result")


def parallel_results(
    items: Sequence[_Item],
    worker: Callable[[_Item], _Result],
    jobs: int,
) -> Iterator[tuple[_Item, _Result]]:
    """Run independent simulator batches concurrently, cancelling queued work on failure."""
    if jobs <= 0:
        raise ValueError("jobs must be positive")
    if jobs == 1:
        for item in items:
            yield item, worker(item)
        return
    with ThreadPoolExecutor(max_workers=min(jobs, len(items))) as executor:
        futures = {executor.submit(worker, item): item for item in items}
        try:
            for future in as_completed(futures):
                yield futures[future], future.result()
        finally:
            for future in futures:
                future.cancel()


def _merge_ranges(ranges: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for lo, hi in sorted(ranges):
        lo = max(lo, RAM_BASE)
        hi = min(hi, RAM_BASE + RAM_SIZE - 1)
        if lo > hi:
            continue
        if merged and lo <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return merged


@lru_cache(maxsize=64)
def _checked_offsets(
    envelope: tuple[tuple[int, int], ...],
    blocked: tuple[tuple[int, int], ...],
) -> tuple[tuple[int, int], ...]:
    """Half-open RAM offsets that the outside-envelope oracle must compare."""
    checked: list[tuple[int, int]] = []
    cursor = RAM_BASE
    for lo, hi in _merge_ranges(envelope):
        if cursor < lo:
            checked.append((cursor, lo - 1))
        cursor = max(cursor, hi + 1)
    if cursor < RAM_BASE + RAM_SIZE:
        checked.append((cursor, RAM_BASE + RAM_SIZE - 1))
    # Blocked ranges are intentionally checked even where they overlap the
    # normal envelope (untouched-slot isolation).
    checked.extend(blocked)
    return tuple(
        (lo - RAM_BASE, hi - RAM_BASE + 1)
        for lo, hi in _merge_ranges(checked)
    )




# --------------------------------------------------------------- host diffing

def outside_runs(dump: bytes, expected: bytes, envelope: list[list[int]],
                 blocked: Sequence[tuple[int, int]] = ()) -> list[tuple[int, int]]:
    """Return changed runs outside the allowed envelope.

    Equal checked spans are rejected by C-level bytes comparison. The old
    byte-at-a-time scan spent most host CPU examining 128 KiB of equal RAM for
    every trial.
    """
    if len(dump) != RAM_SIZE or len(expected) != RAM_SIZE:
        raise ValueError("outside-run inputs must cover the full RAM window")
    envelope_key = tuple((lo, hi) for lo, hi in envelope)
    blocked_key = tuple(blocked)
    runs: list[tuple[int, int]] = []
    for lo, hi in _checked_offsets(envelope_key, blocked_key):
        if dump[lo:hi] == expected[lo:hi]:
            continue
        start: int | None = None
        for offset in range(lo, hi):
            if dump[offset] != expected[offset]:
                if start is None:
                    start = offset
            elif start is not None:
                runs.append((RAM_BASE + start, RAM_BASE + offset - 1))
                start = None
        if start is not None:
            runs.append((RAM_BASE + start, RAM_BASE + hi - 1))
    return runs


def verify_outside_runs() -> None:
    """Seed envelope, blocked-range, boundary, and run-coalescing behavior."""
    expected = bytes(RAM_SIZE)
    dump = bytearray(expected)
    for offset in (1, 2, 9, 10, 11, 15, 16, 17):
        dump[offset] = 0xA5
    actual = outside_runs(
        bytes(dump),
        expected,
        [[RAM_BASE + 8, RAM_BASE + 15]],
        ((RAM_BASE + 10, RAM_BASE + 11),),
    )
    wanted = [
        (RAM_BASE + 1, RAM_BASE + 2),
        (RAM_BASE + 10, RAM_BASE + 11),
        (RAM_BASE + 16, RAM_BASE + 17),
    ]
    if actual != wanted:
        raise RuntimeError(f"outside-run oracle self-test failed: {actual!r}")



def magic_hits(dump: bytes) -> list[int]:
    hits = []
    for value in MAGIC_VALUES:
        needle = value.to_bytes(4, "little")
        seg = dump.find(needle)
        while seg != -1:
            hits.append(RAM_BASE + seg)
            seg = dump.find(needle, seg + 1)
    return hits


def merge_envelope(calibration_outside: dict[str, list[tuple[int, int]]]) -> tuple[list[list[int]], list]:
    env = sorted([lo, hi] for lo, hi in STATIC_ENVELOPE)
    added: list = []
    for name, runs in calibration_outside.items():
        for lo, hi in runs:
            added.append([lo, hi, name])
            env.append([lo, hi])
    env.sort()
    return env, added


def parse_runs(field: str) -> list[tuple[int, int]]:
    runs = []
    for token in field.split():
        if "-" in token:
            lo, _, hi = token.partition("-")
            try:
                runs.append((int(lo, 16), int(hi, 16)))
            except ValueError:
                pass
    return runs


def fill_divergence(
    base_dump: bytes,
    alt_dump: bytes,
    base_image: bytes,
    alt_image: bytes,
    envelope: list[list[int]],
    blocked: tuple[tuple[int, int], ...] = (),
) -> list[int]:
    """Return envelope bytes whose post-state depends on the unprimed fill."""
    if not (len(base_dump) == len(alt_dump) == len(base_image) == len(alt_image) == RAM_SIZE):
        raise ValueError("divergence inputs must cover the full RAM window")
    differing: list[int] = []
    for offset in range(RAM_SIZE):
        if base_dump[offset] == alt_dump[offset]:
            continue
        if base_dump[offset] == base_image[offset] and alt_dump[offset] == alt_image[offset]:
            continue
        address = RAM_BASE + offset
        if any(lo <= address <= hi for lo, hi in blocked):
            continue
        if any(lo <= address <= hi for lo, hi in envelope):
            differing.append(address)
    return differing


def verify_fill_divergence() -> None:
    """Seed the host oracle so a vacuous divergence pass fails immediately."""
    base_image = bytes(RAM_SIZE)
    alt_image = b"\x01" * RAM_SIZE
    probe_offset = 8
    envelope = [[RAM_BASE + probe_offset, RAM_BASE + probe_offset]]
    if fill_divergence(base_image, alt_image, base_image, alt_image, envelope):
        raise RuntimeError("divergence oracle did not normalize untouched fill")
    base_dump = bytearray(base_image)
    alt_dump = bytearray(alt_image)
    base_dump[probe_offset] = 2
    alt_dump[probe_offset] = 3
    if fill_divergence(bytes(base_dump), bytes(alt_dump), base_image, alt_image, envelope) != [
        RAM_BASE + probe_offset
    ]:
        raise RuntimeError("divergence oracle missed its seeded fill-dependent byte")
    if fill_divergence(
        bytes(base_dump), bytes(alt_dump), base_image, alt_image, envelope,
        blocked=((RAM_BASE + probe_offset, RAM_BASE + probe_offset),),
    ):
        raise RuntimeError("divergence oracle ignored its blocked range")


def run_batch(elf: Path, batch: list[tuple[int, Trial]], out: Path,
              timeout: float, label: str, salt: int | None = None) -> tuple[str, dict[int, bytes]]:
    """Run one batch; retry only unfinished trials and fail fast if a retry wedges."""
    dump_dir = elf.parent  # mounted rw at /out inside the container
    images = {index: trial_image(trial, salt) for index, trial in batch}
    for index, image in images.items():
        (dump_dir / f"img-{index:06d}.bin").write_bytes(image)
    script = batch_script(batch)
    marker = f"TP_END={batch[-1][0]}"
    batch_log = out / f"{label}.txt"
    try:
        output = run_elf(root=REPO_ROOT, elf_path=elf, stop=f"{SENTINEL:#x}",
                         memory_regions=[RAM_REGION], gdb_commands=script,
                         expected_output=[marker], timeout=timeout,
                         output_path=batch_log)
        return output, images
    except CodeFlashSimError:
        partial = batch_log.read_text(encoding="utf-8") if batch_log.is_file() else ""
        completed = {int(match.group(1)) for match in RX_LINE.finditer(partial)}
        parts = [partial] if partial else []
        # A singleton should finish in about one second. Cap retries and abort
        # on the first retry without TPR so one wedged trial cannot fan out.
        retry_timeout = min(timeout, 10.0)
        for index, trial in batch:
            if index in completed:
                continue
            retry_log = out / f"{label}-{index:06d}.txt"
            try:
                parts.append(run_elf(root=REPO_ROOT, elf_path=elf, stop=f"{SENTINEL:#x}",
                                     memory_regions=[RAM_REGION],
                                     gdb_commands=batch_script([(index, trial)]),
                                     expected_output=[f"TP_END={index}"], timeout=retry_timeout,
                                     output_path=retry_log))
            except CodeFlashSimError as exc:
                retry = retry_log.read_text(encoding="utf-8") if retry_log.is_file() else ""
                if retry:
                    parts.append(retry)
                if index not in {int(match.group(1)) for match in RX_LINE.finditer(retry)}:
                    detail = str(exc).splitlines()[-1][:120]
                    raise RuntimeError(
                        f"trial {index} failed without TPR after {retry_timeout:g}s; "
                        f"log: {retry_log} ({detail})"
                    ) from exc
        return "\n".join(parts) + "\n", images



def collect(output: str, dump_dir: Path, images: dict[int, bytes],
            envelope: list[list[int]], keep: Path | None = None,
            trials: dict[int, Trial] | None = None,
            keep_indexes: set[int] | None = None,
            keep_dumps: dict[int, bytes] | None = None,
            pattern: bool = False) -> tuple[list[dict], int, dict[int, Counter]]:
    failures: list[dict] = []
    seen = 0
    reported: set[int] = set()
    sinks = attribute_sinks(output)
    for match in RX_LINE.finditer(output):
        index, pc = int(match.group(1)), int(match.group(2))
        seen += 1
        if index in reported or index not in images:
            continue
        reported.add(index)
        record: dict = {"index": index, "pc": pc}
        dump_path = dump_dir / f"tp-{index:06d}.bin"
        img_path = dump_dir / f"img-{index:06d}.bin"
        if not dump_path.is_file():
            failures.append(record | {"outside_runs": "missing-dump"})
            img_path.unlink(missing_ok=True)
            continue
        dump = dump_path.read_bytes()
        if keep_dumps is not None and (keep_indexes is None or index in keep_indexes):
            keep_dumps[index] = dump
        blocked = untouched_slots(trials[index]) if trials else []
        runs = outside_runs(dump, images[index], envelope, blocked)
        magics = magic_hits(dump)
        propagated = pattern_propagation(dump, SLOT_RANGES) if pattern else []
        bad = slot_invariants(dump, slots_touched(trials[index])) \
            if (pattern and trials and trials[index].rx_state is None) else []
        if runs or magics or pc != SENTINEL or propagated or bad:
            record["outside_runs"] = " ".join(f"{lo:x}-{hi:x}" for lo, hi in runs[:24])
            if blocked:
                record["blocked"] = " ".join(f"{lo:x}-{hi:x}" for lo, hi in blocked)
            if magics:
                record["magic"] = [hex(m) for m in magics[:8]]
            if propagated:
                record["propagation"] = propagated
            if bad:
                record["invariants"] = bad
            failures.append(record)
            if keep is not None:
                dump_path.replace(keep / f"tp-{index:06d}.bin")
        dump_path.unlink(missing_ok=True)
        img_path.unlink(missing_ok=True)
    return failures, seen, sinks


def verify_liveness(elf: Path, timeout: float, salt: int | None = None) -> None:
    """Canary: a well-formed SF on 0x7A1 must land in Dcm slot 0's buffer.

    Guards against environment regressions (lost TP prime, sim thunk SIGILLs,
    dropped Dcm state primes) that would make every trial silently no-op and
    report a false-clean campaign.
    """
    probe = Trial("liveness", (sf(0x804, 7, b"\xde\xad\xbe\xef\xaa\x55\x33"),))
    dump_dir = elf.parent
    (dump_dir / "img-999999.bin").write_bytes(trial_image(probe, salt))
    script = [
        f"set $r4={GP:#x}", f"set $r5={TP_BASE:#x}", f"set $tp={TP_BASE:#x}",
        "set {unsigned short}0x6a45e = 0x007f", "set {unsigned short}0x6a4c4 = 0x007f",
        f"restore /out/img-999999.bin binary {RAM_BASE:#x}",
        f"break *{SENTINEL:#x}",
        *trial_script(999999, probe)[:-1],
        'printf "LIVE %02x%02x%02x\\n", *(unsigned char*)0xFEBE5651, *(unsigned char*)0xFEBE5652, *(unsigned char*)0xFEBE5653',
        f"set $pc={SENTINEL:#x}",
    ]
    output = run_elf(root=REPO_ROOT, elf_path=elf, stop=f"{SENTINEL:#x}",
                     memory_regions=[RAM_REGION], gdb_commands=script,
                     expected_output=["LIVE deadbe"], timeout=timeout)
    match = re.search(r"^LIVE ([0-9a-f]+)$", output, re.MULTILINE)
    if not match or match.group(1) != "deadbe":
        raise SystemExit(f"liveness canary failed: SF delivery broken ({match and match.group(1)})")
    (dump_dir / "tp-999999.bin").unlink(missing_ok=True)
    (dump_dir / "img-999999.bin").unlink(missing_ok=True)



# --------------------------------------------------------------------- main

def fuzz(out: Path, seed: int, random_each: int, batch_size: int, timeout: float,
         jobs: int = 1, pattern_fill: bool = True, divergence_step: int = 0) -> dict:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if jobs <= 0:
        raise ValueError("jobs must be positive")
    verify_outside_runs()
    image = IMAGE.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise SystemExit("CodeFlash.bin sha256 mismatch")
    salt = 0 if pattern_fill else None
    out.mkdir(parents=True, exist_ok=True)
    for pattern in ("batch-*.txt", "div-*.txt", "calibration*.txt"):
        for stale in out.glob(pattern):
            stale.unlink()
    (out / "summary.json").unlink(missing_ok=True)
    keep = out / "findings"
    keep.mkdir(exist_ok=True)
    for stale in keep.glob("tp-*.bin"):
        stale.unlink()
    sim_out = out / "linked-image"
    sim_out.mkdir(exist_ok=True)
    for pattern in ("tp-*.bin", "img-*.bin"):
        for stale in sim_out.glob(pattern):
            stale.unlink()

    _output, elf = run(root=REPO_ROOT, image_path=IMAGE, entry=ENTRY, stop=f"{SENTINEL:#x}",
                       memory_regions=[RAM_REGION],
                       gdb_commands=[f"set $r4={GP:#x}", f"set $r3={STACK_TOP:#x}",
                                     f"set $r31={SENTINEL:#x}", f"set $tp={TP_BASE:#x}",
                                     f"set $r5={TP_BASE:#x}", "set $r7=0",
                                     f"break *{SENTINEL:#x}", "continue"],
                       expected_output=["RH850_EXECUTION_VERIFIED"], timeout=timeout,
                       output_dir=sim_out)
    assert elf is not None
    dump_dir = elf.parent
    # The liveness canary checks transport machinery under the established
    # zero-fill state model; pattern-fill trials are behavior probes and
    # their fill-dependent faults are findings, not environment failures.
    verify_liveness(elf, timeout)

    # Calibration: well-formed traffic defines additional legitimate writes.
    cal_trials = [(-idx - 1, Trial(name, frames)) for idx, (name, frames) in enumerate(CALIBRATION)]
    output, cal_images = run_batch(elf, cal_trials, out, timeout, "calibration", salt=salt)
    calibration_outside: dict[str, list[tuple[int, int]]] = {}
    static_env = [list(r) for r in STATIC_ENVELOPE]
    cal_failures, _seen, _sinks = collect(output, dump_dir, cal_images, static_env, pattern=pattern_fill)
    for record in cal_failures:
        runs = parse_runs(record.get("outside_runs", ""))
        if runs:
            name = CALIBRATION[-record["index"] - 1][0]
            calibration_outside[name] = runs
    envelope, added = merge_envelope(calibration_outside)
    (out / "calibration.txt").write_text(
        "\n".join(f"{name}: {' '.join(f'{lo:#x}-{hi:#x}' for lo, hi in runs)}"
                  for name, runs in calibration_outside.items())
        + "\n" + (json.dumps(added) if added else "no envelope additions") + "\n")

    trials = generate(seed, random_each)
    trial_map = {i: t for i, t in enumerate(trials)}
    div_set = set(range(0, len(trials), divergence_step)) if divergence_step else set()
    if div_set:
        verify_fill_divergence()
        pattern_image(1)  # populate once before concurrent alternate-fill batches
    dump_store: dict[int, bytes] = {}
    failures: list[dict] = []
    families: Counter[str] = Counter()
    observed = 0
    sink_totals: Counter[str] = Counter()
    sink_families: dict[str, Counter[str]] = {name: Counter() for _addr, name in SINKS}
    batch_groups = [
        (f"batch-{batch_number:04d}",
         list(enumerate(trials[offset:offset + batch_size], offset)))
        for batch_number, offset in enumerate(range(0, len(trials), batch_size))
    ]
    completed = 0
    worker = lambda item: run_batch(
        elf, item[1], out, timeout, item[0], salt=salt,
    )
    for (_label, group), (output, images) in parallel_results(batch_groups, worker, jobs):
        batch_failures, seen, sinks = collect(output, dump_dir, images, envelope, keep=keep,
                                              trials=trial_map,
                                              keep_indexes=div_set or None,
                                              keep_dumps=dump_store if div_set else None,
                                              pattern=pattern_fill)
        for idx, hits in sinks.items():
            family = trials[idx].family
            for name, count in hits.items():
                sink_totals[name] += count
                sink_families[name][family] += count
        observed += seen
        for record in batch_failures:
            trial = trials[record["index"]]
            record["family"] = trial.family
            record["frames"] = [[hex(f.canif_id), f.dlc, f.hex8()] for f in trial.frames]
            record["rx_state"] = trial.rx_state.hex() if trial.rx_state else None
            families[trial.family] += 1
        failures.extend(batch_failures)
        completed += len(group)
        print(f"simulated {completed}/{len(trials)}"
              f" ({len(batch_failures)} findings)", flush=True)

    # Divergence pass: every Nth trial re-run with a second pattern fill.
    # Compare each post-state against its own start image so untouched marker
    # bytes do not masquerade as fill-influenced writes.
    divergence: list[dict] = []
    divergence_compared = 0
    div_groups: list[tuple[str, list[tuple[int, Trial]]]] = []
    if div_set:
        missing_base = div_set - dump_store.keys()
        if missing_base:
            raise SystemExit(f"base divergence dumps missing: {sorted(missing_base)[:8]}")
        selected = [(index, trials[index]) for index in sorted(div_set)]
        div_groups = [
            (f"div-{batch_number:04d}", selected[offset:offset + batch_size])
            for batch_number, offset in enumerate(range(0, len(selected), batch_size))
        ]
        div_worker = lambda item: run_batch(
            elf, item[1], out, timeout, item[0], salt=1,
        )
        for (_label, group), (output, images) in parallel_results(div_groups, div_worker, jobs):
            alt_dump_store: dict[int, bytes] = {}
            div_failures, _seen, _sinks = collect(
                output, dump_dir, images, envelope, keep=keep, trials=trial_map,
                keep_dumps=alt_dump_store, pattern=False,
            )
            for record in div_failures:
                record["family"] = trials[record["index"]].family + ":div-run"
                failures.append(record)
            for index, trial in group:
                if index not in alt_dump_store:
                    raise SystemExit(f"alternate divergence dump missing for trial {index}")
                diff = fill_divergence(
                    dump_store[index],
                    alt_dump_store[index],
                    trial_image(trial, salt),
                    images[index],
                    envelope,
                    blocked=((0xFEBE1800, 0xFEBE1FFF),),
                )
                divergence_compared += 1
                if diff:
                    divergence.append({
                        "index": index,
                        "family": trial.family,
                        "diff": [hex(address) for address in diff[:16]],
                        "diff_count": len(diff),
                    })
        if divergence_compared != len(div_set):
            raise SystemExit(
                f"divergence pass compared {divergence_compared}/{len(div_set)} trials"
            )
    missing_required_sinks = [name for name in REQUIRED_SINKS if not sink_totals[name]]
    failures.sort(key=lambda record: (record["index"], record.get("family", "")))
    divergence.sort(key=lambda record: record["index"])
    for leftover in dump_dir.glob("tp-*.bin"):
        leftover.unlink(missing_ok=True)
    for leftover in dump_dir.glob("img-*.bin"):
        leftover.unlink(missing_ok=True)
    summary = {
        "schema": "camry-f33-cantp-ingress-original-rh850-fuzz-v3",
        "image_sha256": IMAGE_SHA256,
        "entry": hex(ENTRY),
        "seed": seed,
        "random_each": random_each,
        "fill": "pattern" if pattern_fill else "zero",
        "batch_size": batch_size,
        "jobs": jobs,
        "batch_runs": len(batch_groups),
        "divergence_batch_runs": len(div_groups),
        "fences": [[hex(addr), name] for addr, name in FENCES],
        "trials": len(trials),
        "observed_tpr": observed,
        "failures": len(failures),
        "divergence_findings": len(divergence),
        "divergence_trials": len(div_set),
        "divergence_compared": divergence_compared,
        "by_family": dict(families),
        "envelope": [[hex(lo), hex(hi)] for lo, hi in envelope],
        "envelope_added": added,
        "findings": failures,
        "divergence": divergence,
        "sink_hits": {name: {"total": sink_totals[name],
                             "families": dict(sink_families[name])}
                      for _addr, name in SINKS},
        "missing_required_sinks": missing_required_sinks,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if missing_required_sinks:
        raise SystemExit(f"required sinks not reached: {', '.join(missing_required_sinks)}")
    return summary



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0xC2A7)
    parser.add_argument("--random-each", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--jobs", type=int, default=4,
                        help="concurrent independent simulator batches")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--fill", choices=("pattern", "zero"), default="pattern",
                        help="RAM fill outside primes: address-derived pattern (v3) or historical zeros")
    parser.add_argument("--divergence-step", type=int, default=0,
                        help="re-run every Nth trial with a second pattern fill; differing "
                             "envelope bytes flag uninitialized-read influence")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.resolve() == REPO_ROOT or not out.resolve().is_relative_to(REPO_ROOT / "build/out"):
        raise SystemExit("fuzz outputs must live under build/out/")
    result = fuzz(args.out, args.seed, args.random_each, args.batch_size, args.timeout,
                  jobs=args.jobs, pattern_fill=args.fill == "pattern",
                  divergence_step=args.divergence_step)
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("findings", "divergence")}, indent=2))
    return 0 if result["failures"] == 0 and result["divergence_findings"] == 0 else 1



if __name__ == "__main__":
    raise SystemExit(main())
