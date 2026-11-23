#!/usr/bin/env python3
"""SID 0xAB (proprietary event read) output-contract audit for camry-8965F3307000.

The November output-contract audit only recorded the two-byte `AB 0N` header
cases for SID 0xAB.  This driver runs the full-capacity scenario end to end: a
completed request is admitted to Dcm receive slot 0 exactly as CanTp/Dcm
ingress leaves it (request phase 2, pending slot, slot-state row) and the
scheduled dispatcher ``dcm_run_scheduled_request @ 0x922AA`` is executed in
the exact-image GNU simulator.  Every case is judged against the firmware's
own hand-off of the response (breakpoint at ``dcm_enqueue_final_disposition
@ 0x933F8``), a full LocalRAM dump, and the instruction-attributed
memory-access trace.

Harness choice
--------------
The direct-dispatch priming contract of ``fuzz_camry_f33_dcm_handlers.py`` is
used instead of the machine scenario runner (``tools/rh850 test firmware``):

* ``dcm_run_scheduled_request`` is the stock scheduled entry.  The only
  priming it needs is the receive-slot admission state that real ingress
  writes, so the published capacity stays comparable with the November audit
  (766 bytes after the `EB ss` header).
* The machine scenario runner judges decompiled call plans, caps its
  memory-access trace at 16384 rows (``scenario._judge``) and has no batched
  response-poison, RAM-dump or PC-attributed write facility.
* The real LocalRAM snapshot is still the RAM base.  It carries the real
  stored-event objects the family serializes (latch bitmap 0xFEBE8A04, active
  capture pair 0xFEBE8684/0xFEBE86E4, capture banks 0xFEBE8744) and the real
  Dcm route configuration.  Stored-event records are synthesized by patching
  those objects in scenario memory.

Request format (derived from code; instruction addresses cited)
----------------------------------------------------------------
``dcm_dispatch_subfunction_service @ 0x91466`` resolves the subfunction with
``dcm_resolve_subfunction @ 0x9105A`` (16-byte rows, subfunction at +0xC:
0x91096).  The SID 0xAB rows are 0x25AFC (sub 1 -> 0x9874A), 0x25B0C
(sub 2 -> 0x9876C) and 0x25B1C (sub 3 -> 0x9878E), sessions {1, 3}, no
security.  Each wrapper calls ``dcm_begin_proprietary_event_read @ 0x9862E``
with its kind (0x98756 / 0x98778 / 0x9879A):

* ``AB 01``           kind 1: length 0 (0x98668), no echo, event id 0xFFFF,
                      subselector 0xFFFF (0x9866A-0x98670).
* ``AB 02 hh ll``     kind 2: length 2 (0x98686), echo (0x986B0-0x986CA),
                      event id big-endian from the request (0x9867A-0x98680).
* ``AB 03 hh ll sh sl`` kind 3: length 4 (0x98690), event id from bytes 0-1
                      and subselector from bytes 2-3 (0x9868E-0x98696).

A wrong length gives NRC 0x13 (0x9869C); an unmapped subfunction gives NRC
0x12.  ``select_proprietary_events_or_reset_selection @ 0x98850`` stores the
kind at 0xFEBF45DC through ``begin_proprietary_event_selection @ 0x8DE98``
(0x8DEAE), so 0x8E170/0x8E182 take the merge arm
(``merge_sorted_big_endian_u16_lists_dedup_equal_heads @ 0x8DEE2``) only for
kind 1 and ``select_first_successful_payload_or_error @ 0x8DFF6`` for kinds 2
and 3.  The serializer ``serialize_selected_proprietary_event @ 0x50922``
writes into the 768-byte staging buffer at 0xFEBF45E4 (0x8E08A) and accepts a
result only when 0 <= n <= capacity (0x5096A-0x50972); that capacity is the
remaining response room (0x985C8-0x985D2).

Staging overflow oracle
-----------------------
The serializers write first and compare against the size only afterwards
(0x5582C/0x5582E, 0x5096A-0x50972).  Their output is the 768-byte staging
buffer at 0xFEBF45E4, immediately followed by ``dcm_proprietary_continuation``
at 0xFEBF48E4.  Every traced write with a byte in [0xFEBF48E4, 0xFEBF5000)
is reported with its offset from 0xFEBF48E4 and its bytes under the
``staging_overflow`` key, per serializer mode (FEBE81AD = 1, 2, 3).

The accumulated count (0xFEBF45D4) and remaining size (0xFEBF45D6) are read
only by the resume branch (0x8E10C stores the remaining size, 0x8E116 calls
the serializer), which runs only while 0xFEBF45E1 == 2 and 0xFEBF45DD == 2.
That pair is stored only by the pending path (0x8E10E-0x8E100), which needs
serializer status 2; 0x5096A-0x50988 return 0, 4, 6 or 10 only.  No request
sequence can therefore build an accumulated count in front of a serializer.
Family ``accumulated`` primes the state anyway, for every serializer mode a
request can select, and reports the consequence separately from the
request-reachable cases.
"""

import argparse
import hashlib
import json
import re
import struct
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from tools import REPO_ROOT
from tools.rh850_codeflash import CodeFlashSimError, run, run_elf
from tools.targets.camry.research import fuzz_camry_f33_cantp_ingress as ci
from tools.targets.camry.research import fuzz_camry_f33_dcm_handlers as dcm
from tools.targets.camry.research.fuzz_camry_f33_stateful_coverage import (
    TRANSPORT_CONTEXT,
    parse_core_accesses,
)

SCHEMA = "camry-f33-ab-event-output-contract-v1"
IMAGE = dcm.IMAGE
IMAGE_SHA256 = dcm.IMAGE_SHA256
SNAPSHOT = REPO_ROOT / "targets/camry-2026/raw-20260826/secoc-recovery/ram/local_ram_pe1.bin"
SNAPSHOT_SHA256 = "0ddef478b15bcf3241c56573463eda25ba018081629daf0042fcae1204c435a7"
DEFAULT_OUT = (REPO_ROOT / "build/out/targets/camry-8965F3307000"
               / "ab-merge-capacity-20261123/contract")

RAM_BASE = dcm.RAM_BASE
RAM_SIZE = dcm.RAM_SIZE
RESP_BUF = dcm.RESP_BUF                        # 0xFEBE5A20 (gp-0x5DE0, 0x93CE6)
STOCK_CAPACITY = 0x300                         # CodeFlash u32 at 0x25F0C
CAPACITY_CELL = 0x25F0C
ACTIVE_CTX = dcm.ACTIVE_DCM_CONTEXT            # 0xFEBE5630
RETAINED_CTX = 0xFEBE5E34                      # gp-0x59CC (0x98638)
HEADER_COUNT = 0xFEBE562D                      # dispatcher header bytes (0x9151A)
FINAL_NRC = 0xFEBE5624                         # gp-0x61DC (dcm_stage_negative_response)
FINAL_NEGATIVE = 0xFEBE5967                    # 3-byte 7F sid nrc object (0x93162)
NODE_TABLE = 0xFEBE5984                        # dcm_response_node, 16 bytes each
IN_PLACE_MASK_PC = 0x914E8                     # traced PC of the store half of clr1 at 0x914E6

EVENT_STATE = 0xFEBF45D0                       # selection/serialization state
ACCUMULATED = 0xFEBF45D4                       # accumulated serialized count
REMAINING = 0xFEBF45D6                         # 0x300 minus the accumulated count
MERGE_FLAG = 0xFEBF45DC                        # == 1 selects 0x8DEE2 (0x8E170)
PHASE = 0xFEBF45DD                             # last serializer status
SUBCALL = 0xFEBF45E1                           # 2 while a pending resume is expected
STAGING = 0xFEBF45E4                           # serialization target (0x8E08A)
# 0xFEBF48E4 is dcm_proprietary_continuation (written by 0x8E1E0); nothing
# between it and the staging pointer is referenced by any function, and the
# family's own default "remaining" is 0x300 (0x8DE28): 768 bytes [INFERENCE].
STAGING_END = 0xFEBF48E4
STAGING_WINDOW_END = 0xFEBF5000                # write-watch window past the buffer
SELECTOR_KIND = 0xFEBE81AD                     # set by 0x50916, read by 0x50932
SELECTOR_EVENT = 0xFEBE81BA
SELECTOR_SUB = 0xFEBE81BC
LATCH_BITMAP = 0xFEBE8A04                      # 64 bits -> catalogue index (0x557CE + 0x40)
ACTIVE_SECONDARY = 0xFEBE8684                  # 96-byte record (gp-0x317C)
ACTIVE_PRIMARY = 0xFEBE86E4                    # 96-byte record (gp-0x311C)
ACTIVE_RECORD_NUMBER = 0x46                    # psVar7[0x23] (0x5584A)
CAPTURE_BANKS = 0xFEBE8744                     # 4 banks x 5 records x 0x20
BANK_RECORD_SIZE = 0x20
CATALOGUE = 0x2AB70                            # 64 x {u16 id, u16 mask, u8 type, u8 count}
RING_DESCRIPTORS = 0x2AA6C                     # 6 x 16 bytes (0x56674)
ACTIVE_DESCRIPTORS = 0x2A364                   # 75 x 0x18 bytes (0x56664)

# Instruction ranges whose stores belong to the 0xAB family.
FAMILY_RANGES = (
    (0x9862E, 0x98711),   # dcm_begin_proprietary_event_read
    (0x985BC, 0x9862C),   # read_selected_proprietary_events_and_report
    (0x98822, 0x9884E),   # resume entry that also calls 0x985BC
    (0x98870, 0x9887B),   # thunk to 0x8E074
    (0x8E074, 0x8E1DF),   # serialize_event_and_merge_selected_output
    (0x8DEE2, 0x8DFF5),   # merge_sorted_big_endian_u16_lists_dedup_equal_heads
    (0x8DFF6, 0x8E073),   # select_first_successful_payload_or_error
    (0x8DE98, 0x8DEBD),   # begin_proprietary_event_selection
    (0x8DEBE, 0x8DEE1),   # status -> NRC map
    (0x50916, 0x5098F),   # selector store + serialize_selected_proprietary_event
    (0x557C4, 0x562F9),   # catalogue serializers, active-pair writers, ring readers
    (0x6A55C, 0x6A5CB),   # big-endian store helpers
)

# The merge and select copy loops are the only family reads of the staging
# buffer that can run past its end when the accumulated count is too large.
COPY_RANGES = ((0x8DEE2, 0x8DFF5), (0x8DFF6, 0x8E073))


def is_copy_pc(pc: int | None) -> bool:
    return pc is not None and any(lo <= pc <= hi for lo, hi in COPY_RANGES)

EVENT_RE = re.compile(
    r"^(SERRET2|SERRET|SER|ARMMERGE|ARMSELECT|OUTLEN|READRET|NRC|PUB|CASE) (.*)$", re.MULTILINE)
RX_LINE = dcm.RX_LINE


@dataclass
class Case:
    name: str
    family: str
    request: bytes
    session: int = 1
    primes: tuple[tuple[int, bytes], ...] = ()
    capacity: int = STOCK_CAPACITY
    stored_event: str = "snapshot"
    note: str = ""


@dataclass
class Observation:
    case: Case
    pc: int
    dump: bytes | None
    image: bytes | None
    events: dict[str, list[str]] = field(default_factory=dict)
    trace: list[dict] = field(default_factory=list)
    error: str = ""


# ------------------------------------------------------------------ tables

def _image() -> bytes:
    data = IMAGE.read_bytes()
    if hashlib.sha256(data).hexdigest() != IMAGE_SHA256:
        raise SystemExit("CodeFlash.bin sha256 mismatch")
    return data


def _u16(image: bytes, address: int) -> int:
    return struct.unpack_from("<H", image, address)[0]


def _u32(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address)[0]


def catalogue(image: bytes) -> list[dict]:
    rows = []
    for index in range(64):
        base = CATALOGUE + index * 8
        event_id = _u16(image, base)
        if event_id:
            rows.append({
                "index": index,
                "id": f"0x{event_id:04X}",
                "field_mask": f"0x{_u16(image, base + 2):04X}",
                "type": f"0x{image[base + 4]:02X}",
                "count": image[base + 5],
            })
    return rows


def structural_bounds(image: bytes) -> dict:
    """Largest payload each serializer can emit, from the CodeFlash tables."""
    ring = []
    for index in range(6):
        base = RING_DESCRIPTORS + index * 16
        ring.append({"id": f"0x{_u16(image, base):04X}",
                     "mask": f"0x{_u16(image, base + 12):04X}",
                     "length": image[base + 14],
                     "availability": "0" if _u32(image, base + 8) == 0 else
                     f"0x{_u32(image, base + 8):08X}"})
    active = []
    for index in range(0x4B):
        base = ACTIVE_DESCRIPTORS + index * 0x18
        active.append({"id": f"0x{_u16(image, base + 8):04X}",
                       "writer": f"0x{_u32(image, base + 12):08X}",
                       "availability": f"0x{_u32(image, base + 16):08X}",
                       "mask": f"0x{_u16(image, base + 0x14):04X}",
                       "length": image[base + 0x16]})
    per_mask = {}
    for mask in sorted({int(row["field_mask"], 16) for row in catalogue(image)}):
        ring_bytes = sum(3 + row["length"] for row in ring if int(row["mask"], 16) & mask)
        fields = [row for row in active
                  if row["writer"] != "0x00000000" and int(row["mask"], 16) & mask]
        active_bytes = sum(3 + row["length"] for row in fields)
        per_mask[f"0x{mask:04X}"] = {
            "bank_record_max": 3 + ring_bytes,
            "bank_five_records_max": 5 * (3 + ring_bytes),
            "active_record_max": 3 + active_bytes,
            "active_pair_max": 2 * (3 + active_bytes),
            "active_fields": len(fields),
            "availability_gated_fields": sum(row["availability"] != "0x00000000"
                                             for row in fields),
        }
    return {
        "ring_descriptors": ring,
        "active_descriptors": active,
        "kind1_latched_list_max": 2 * len(catalogue(image)),
        "kind2_active_pair_max": 4,
        "kind2_bank_max": 10,
        "per_field_mask": per_mask,
        "max_payload_bytes": max(row["active_pair_max"] for row in per_mask.values()),
        "staging_buffer_bytes": STAGING_END - STAGING,
        "note": ("Field lengths are CodeFlash constants; stored-event state only gates "
                 "field availability and can never lengthen a record."),
    }


# --------------------------------------------------------- scenario memory

def be16(value: int) -> bytes:
    return bytes(((value >> 8) & 0xFF, value & 0xFF))


def active_record(event_id: int, number: int, fill: int = 0xA5) -> bytes:
    record = bytearray(bytes((fill + i) & 0xFF for i in range(0x60)))
    record[0:2] = event_id.to_bytes(2, "little")
    record[2:4] = b"\x00\x00"                  # marker: neither 0x1111 nor 0x2222
    record[ACTIVE_RECORD_NUMBER:ACTIVE_RECORD_NUMBER + 2] = number.to_bytes(2, "little")
    return bytes(record)


def bank_record(event_id: int, sequence: int) -> bytes:
    record = bytearray(bytes((0x5C + i) & 0xFF for i in range(BANK_RECORD_SIZE)))
    record[0:2] = event_id.to_bytes(2, "little")
    record[2:4] = sequence.to_bytes(2, "little")
    record[4:6] = b"\x00\x00"                  # marker: neither 0x1111 nor 0x2222
    return bytes(record)


def latch_bits(indices) -> bytes:
    value = 0
    for index in indices:
        value |= 1 << index
    return value.to_bytes(8, "little")


def active_primes(event_id: int, number: int, primary: bool = True,
                  secondary: bool = True) -> tuple[tuple[int, bytes], ...]:
    primes = []
    if primary:
        primes.append((ACTIVE_PRIMARY, active_record(event_id, number, 0xA5)))
    if secondary:
        primes.append((ACTIVE_SECONDARY, active_record(event_id, number, 0xE5)))
    return tuple(primes)


def bank_primes(event_id: int, bank: int, count: int = 5) -> tuple[tuple[int, bytes], ...]:
    return tuple(
        (CAPTURE_BANKS + BANK_RECORD_SIZE * (bank * 5 + index), bank_record(event_id, index))
        for index in range(count))


def stored_event_primes(row: dict) -> tuple[tuple[int, bytes], ...]:
    """Synthesize the stored-event record that lets one catalogue row serialize."""
    event_id = int(row["id"], 16)
    kind = int(row["type"], 16)
    if kind == 0x11:
        return active_primes(event_id, 3)
    bank = {0x22: 0, 0x33: 1, 0x44: 3, 0x55: 2}[kind]
    return bank_primes(event_id, bank)


# ------------------------------------------------------------------- cases

def kind2(event_id: int) -> bytes:
    return b"\xAB\x02" + be16(event_id)


def kind3(event_id: int, subselector: int = 0) -> bytes:
    return b"\xAB\x03" + be16(event_id) + be16(subselector)


def first_mask_row(rows: list[dict], mask: str) -> dict:
    return next(row for row in rows if row["field_mask"] == mask and row["type"] == "0x11")


def everything_primes(rows: list[dict], max_id: int) -> tuple[tuple[int, bytes], ...]:
    return ((LATCH_BITMAP, latch_bits([row["index"] for row in rows])),
            *active_primes(max_id, 3), *bank_primes(0xF016, 2))


def probe_cases(image: bytes) -> list[Case]:
    rows = catalogue(image)
    max_id = int(first_mask_row(rows, "0x0001")["id"], 16)
    everything = everything_primes(rows, max_id)
    tag = f"{first_mask_row(rows, '0x0001')['id']}_t11"
    return [
        Case("merge_latch_all_populated", "merge", b"\xAB\x01", 1, everything, stored_event="max"),
        Case(f"event_kind3_all_{tag}", "event_kind3", kind3(max_id, 0), 1, everything,
             stored_event="max"),
        Case("event_kind3_all_0xF016_t55", "event_kind3", kind3(0xF016, 0), 1, everything,
             stored_event="max"),
        Case("event_kind2_0xF016_t55", "event_kind2", kind2(0xF016), 1, everything,
             stored_event="max"),
    ]


def build_cases(image: bytes, observed: dict[str, int]) -> list[Case]:
    rows = catalogue(image)
    max_id = int(first_mask_row(rows, "0x0001")["id"], 16)
    cases: list[Case] = []

    # A. Selector paths: every subfunction row, sessions, suppression, lengths.
    for session in (1, 2, 3):
        for name, request in (("kind1", b"\xAB\x01"), ("kind2", kind2(0x206D)),
                              ("kind3", kind3(0x206D))):
            cases.append(Case(f"selector_{name}_s{session}", "selector", request, session,
                              active_primes(0x206D, 3), stored_event="active-0x206d"))
    for request, label in (
        (b"\xAB\x81", "kind1_suppressed"), (b"\xAB\x82" + be16(0x206D), "kind2_suppressed"),
        (b"\xAB\x83" + be16(0x206D), "kind3_short_suppressed"),
    ):
        cases.append(Case(f"selector_{label}", "selector", request, 1,
                          active_primes(0x206D, 3), stored_event="active-0x206d"))
    # Unmapped subfunctions: wrappers for kinds 0x11..0x13 exist (0x987B0,
    # 0x987D6, 0x987FC) but no DSL row points at them.
    for sub, body in ((0x00, b""), (0x04, b"\x20\x6D"), (0x05, b"\x20\x6D"), (0x11, b""),
                      (0x12, b"\x20\x6D"), (0x13, b"\x20\x6D\x00\x00"), (0x7F, b""),
                      (0xFF, b"")):
        cases.append(Case(f"selector_unknown_sub_{sub:02x}", "selector",
                          bytes((0xAB, sub)) + body, 1, active_primes(0x206D, 3)))
    for request, label in (
        (b"\xAB", "kind1_no_sub"), (b"\xAB\x02", "kind2_len0"), (b"\xAB\x02\x20", "kind2_len1"),
        (b"\xAB\x02\x20\x6D\x00", "kind2_len3"),
        (b"\xAB\x02" + b"\x11" * 0xFE, "kind2_len254"),
        (b"\xAB\x03", "kind3_len0"), (b"\xAB\x03\x20", "kind3_len1"),
        (b"\xAB\x03\x20\x6D", "kind3_len2"), (b"\xAB\x03\x20\x6D\x00", "kind3_len3"),
        (b"\xAB\x03\x20\x6D\x00\x00\x00", "kind3_len5"),
        (b"\xAB\x03" + b"\x11" * 0xFC, "kind3_len252"),
    ):
        assert len(request) <= 0x100
        cases.append(Case(f"selector_length_{label}", "selector", request, 1,
                          active_primes(0x206D, 3)))

    # B. Merge arm (`AB 01`): latched-ID list from none to every populated row.
    cases.append(Case("merge_snapshot_latch", "merge", b"\xAB\x01", 1))
    cases.append(Case("merge_no_latch", "merge", b"\xAB\x01", 1,
                      ((LATCH_BITMAP, b"\x00" * 8),), stored_event="none"))
    for row in rows:
        cases.append(Case(f"merge_latch_{row['id']}", "merge", b"\xAB\x01", 1,
                          ((LATCH_BITMAP, latch_bits([row["index"]])),),
                          stored_event=f"latch-{row['id']}"))
    cases.append(Case("merge_latch_all_populated", "merge", b"\xAB\x01", 1,
                      ((LATCH_BITMAP, latch_bits([row["index"] for row in rows])),),
                      stored_event="latch-all-51"))
    cases.append(Case("merge_latch_all_64", "merge", b"\xAB\x01", 1,
                      ((LATCH_BITMAP, b"\xFF" * 8),), stored_event="latch-all-64"))
    cases.append(Case("merge_suppressed_all", "merge", b"\xAB\x81", 1,
                      ((LATCH_BITMAP, latch_bits([row["index"] for row in rows])),),
                      stored_event="latch-all-51"))

    # C. Every populated event id through both non-merge selectors.
    for row in rows:
        event_id = int(row["id"], 16)
        tag = f"{row['id']}_t{row['type'][2:]}"
        primes = stored_event_primes(row)
        cases.append(Case(f"event_kind2_{tag}", "event_kind2", kind2(event_id), 1, primes,
                          stored_event=f"stored-{row['type']}"))
        cases.append(Case(f"event_kind3_all_{tag}", "event_kind3", kind3(event_id), 1, primes,
                          stored_event=f"stored-{row['type']}"))
        for sub in ((1, 2, 3, 4, 5, row["count"], 0xFF, 0xFFFF) if row["count"]
                    else (1, 3, 0xFFFF)):
            cases.append(Case(f"event_kind3_sub{sub}_{tag}", "event_kind3",
                              kind3(event_id, sub), 1, primes,
                              stored_event=f"stored-{row['type']}"))
    for event_id in (0x0000, 0x206C, 0x21B3, 0xF0FF, 0xFFFF):
        cases.append(Case(f"event_kind2_unpopulated_{event_id:04x}", "event_kind2",
                          kind2(event_id), 1, stored_event="none"))
        cases.append(Case(f"event_kind3_unpopulated_{event_id:04x}", "event_kind3",
                          kind3(event_id), 1, stored_event="none"))
    # Stored-event shapes for the active pair and the banks.
    shapes = (
        ("primary_only", active_primes(max_id, 3, secondary=False)),
        ("secondary_only", active_primes(max_id, 3, primary=False)),
        ("record_number_0", active_primes(max_id, 0)),
        ("record_number_5", active_primes(max_id, 5)),
        ("record_number_ffff", active_primes(max_id, 0xFFFF)),
        ("marker_1111", ((ACTIVE_PRIMARY, active_record(max_id, 3, 0xA5)[:2] + b"\x11\x11"
                          + active_record(max_id, 3, 0xA5)[4:]),
                          (ACTIVE_SECONDARY, active_record(max_id, 3, 0xE5)[:2] + b"\x11\x11"
                           + active_record(max_id, 3, 0xE5)[4:]))),
        ("marker_2222", ((ACTIVE_PRIMARY, active_record(max_id, 3, 0xA5)[:2] + b"\x22\x22"
                          + active_record(max_id, 3, 0xA5)[4:]),
                          (ACTIVE_SECONDARY, active_record(max_id, 3, 0xE5)[:2] + b"\x22\x22"
                           + active_record(max_id, 3, 0xE5)[4:]))),
    )
    for label, primes in shapes:
        for name, request in (("kind2", kind2(max_id)), ("kind3", kind3(max_id))):
            cases.append(Case(f"stored_active_{label}_{name}", "stored_shape", request, 1,
                              primes, stored_event=f"active-{label}"))
    bank_shapes = (
        ("two_records", bank_primes(0xF016, 2, 2)),
        ("marker_1111", tuple((address, data[:4] + b"\x11\x11" + data[6:])
                              for address, data in bank_primes(0xF016, 2))),
        ("wrong_bank", bank_primes(0xF016, 0)),
    )
    for label, primes in bank_shapes:
        for name, request in (("kind2", kind2(0xF016)), ("kind3", kind3(0xF016)),
                              ("kind3_sub3", kind3(0xF016, 3))):
            cases.append(Case(f"stored_bank_{label}_{name}", "stored_shape", request, 1,
                              primes, stored_event=f"bank-{label}"))

    # D. Serialization state machine: phase x sub-call kind for each selector.
    everything = everything_primes(rows, max_id)
    for kind_name, request in (("kind1", b"\xAB\x01"), ("kind2", kind2(0xF016)),
                               ("kind3", kind3(max_id))):
        for phase in (0, 1, 2):
            for subcall in (0, 1, 2):
                if phase == 1 and subcall == 0:
                    continue                     # stock state, covered above
                cases.append(Case(f"state_{kind_name}_phase{phase}_sub{subcall}", "state",
                                  request, 1,
                                  everything + ((PHASE, bytes((phase,))),
                                                (SUBCALL, bytes((subcall,)))),
                                  stored_event="active+bank+latch",
                                  note="synthetic serializer state"))

    # E. Capacity boundary.  The configured capacity is a CodeFlash constant,
    # so the series is driven by a sim-only overlay of 0x25F0C that straddles
    # the largest payloads observed at stock capacity.
    def sweep(name: str, request: bytes, payload: int | None, echo: int) -> None:
        if payload is None:
            return
        # remaining = capacity - 2 (header) - echo must reach the payload.
        boundary = payload + 2 + echo
        values = sorted({0, 1, 2, 2 + echo, 3 + echo, 8, 16, 32,
                         *(boundary + delta for delta in range(-4, 5)),
                         STOCK_CAPACITY - 1, STOCK_CAPACITY})
        for capacity in values:
            cases.append(Case(f"capacity_{name}_c{capacity}", "capacity", request, 1,
                              everything, capacity=capacity, stored_event="max",
                              note=f"sim-only capacity overlay 0x{capacity:X}"))

    sweep("kind1_latch51", b"\xAB\x01", observed.get("kind1_max"), 0)
    sweep("kind3_active", kind3(max_id), observed.get("kind3_active_max"), 2)
    sweep("kind3_bank", kind3(0xF016), observed.get("kind3_bank_max"), 2)
    sweep("kind2_bank", kind2(0xF016), observed.get("kind2_bank_max"), 2)

    # F. Accumulated count (0xFEBF45D4) near 0x300 with a small remaining size
    # (0xFEBF45D6) in front of a serializer.  Only the resume branch
    # (0x8E10C stores the remaining size, 0x8E116 calls the serializer) reads
    # those cells, and it runs solely when 0xFEBF45E1 == 2 and 0xFEBF45DD == 2
    # (0x8E104/0x8E108).  Both are stored only by the pending path
    # (0x8E10E-0x8E100), which needs serializer status 2; 0x5096A-0x50988
    # return only 0, 4, 6 or 10, so no request can build this state and it is
    # primed here.  Every serializer mode a request can select is covered.
    modes = (("kind1", b"\xAB\x01"), ("kind2_active", kind2(max_id)),
             ("kind2_bank", kind2(0xF016)), ("kind3_active", kind3(max_id)),
             ("kind3_bank", kind3(0xF016)))
    pairs = ((0x2F0, 0x10), (0x2FC, 0x4), (0x2FE, 0x2), (0x300, 0x0), (0x100, 0x200),
             (0x0, 0x300),                       # accumulated + remaining == 0x300
             (0x2FC, 0x66), (0x2FC, 0x150), (0x2F0, 0xFFFF))   # inconsistent
    for acc, remaining in pairs:
        for mode_name, request in modes:
            cases.append(Case(
                f"accumulated_{mode_name}_acc{acc:x}_rem{remaining:x}", "accumulated",
                request, 1,
                everything + ((ACCUMULATED, acc.to_bytes(2, "little")),
                              (REMAINING, remaining.to_bytes(2, "little")),
                              (PHASE, b"\x02"), (SUBCALL, b"\x02")),
                stored_event="active+bank+latch",
                note="synthetic pending state; not reachable by any request"))
    for acc, remaining in ((0x7F0, 0x10), (0xFFF0, 0x10)):
        for mode_name, request in (modes[0], modes[1]):
            cases.append(Case(
                f"accumulated_{mode_name}_acc{acc:x}_rem{remaining:x}", "accumulated",
                request, 1,
                everything + ((ACCUMULATED, acc.to_bytes(2, "little")),
                              (REMAINING, remaining.to_bytes(2, "little")),
                              (PHASE, b"\x02"), (SUBCALL, b"\x02")),
                stored_event="active+bank+latch",
                note="synthetic pending state; not reachable by any request"))
    return cases


# ------------------------------------------------------------------- runner

def scenario_image(base: bytes, case: Case, poison: bytes) -> bytes:
    image = bytearray(base)

    def wr(address: int, data: bytes) -> None:
        image[address - RAM_BASE:address - RAM_BASE + len(data)] = data

    slot_base = dcm.SLOT_BUFFERS[0]
    row = dcm.SLOT_STATE
    wr(row, (slot_base + len(case.request)).to_bytes(4, "little"))
    wr(row + 4, len(case.request).to_bytes(4, "little"))
    wr(row + 8, (0x100 - len(case.request)).to_bytes(2, "little"))
    wr(row + 0xA, b"\x00\x00")
    wr(dcm.REQUEST_PHASE, b"\x02")
    wr(dcm.PENDING_SLOT, b"\x00\x00")
    wr(dcm.SLOT_BUFFERS[1], b"\x00" * 0x100)
    wr(dcm.SLOT_BUFFERS[2], b"\x00" * 0x100)
    if case.request:
        wr(slot_base, case.request + bytes(0x100 - len(case.request)))
    wr(dcm.SESSION, bytes((case.session, case.session, case.session, 0)))
    wr(dcm.SECURITY_BITMAP, b"\x00" * 8)
    for address in dcm.ADMISSION:
        wr(address, b"\x5A")
    wr(dcm.ADMISSION_CLEAR, b"\x00")
    wr(RESP_BUF, poison)
    wr(TRANSPORT_CONTEXT,
       slot_base.to_bytes(4, "little") + len(case.request).to_bytes(4, "little")
       + RESP_BUF.to_bytes(4, "little") + (0).to_bytes(4, "little") + bytes(4)
       + STOCK_CAPACITY.to_bytes(4, "little")
       + bytes((case.request[0] if case.request else 0, 0)) + (2).to_bytes(2, "little"))
    for address, data in case.primes:
        wr(address, data)
    return bytes(image)


def observer_breakpoints() -> list[str]:
    first = len(dcm.SINKS) + 3
    probes = (
        (0x50922, '"SER %x %x\\n", *(unsigned char*)0xFEBE81AD, *(unsigned short*)$r7'),
        (0x8E0DE, '"SERRET %x %x\\n", $r10, *(unsigned short*)($sp+2)'),
        (0x8E11A, '"SERRET2 %x %x\\n", $r10, *(unsigned short*)($sp+2)'),
        (0x8DEE2, ('"ARMMERGE %x %x %x %x %x %x %x %x\\n", $r16, $r17, '
                  '*(unsigned char*)$r6, *(unsigned short*)($r6+2), *(unsigned int*)($r6+4), '
                  '*(unsigned char*)$r7, *(unsigned short*)($r7+2), $r8')),
        (0x8DFF6, ('"ARMSELECT %x %x %x %x %x %x\\n", *(unsigned char*)$r6, '
                  '*(unsigned short*)($r6+2), *(unsigned int*)($r6+4), *(unsigned char*)$r7, '
                  '*(unsigned short*)($r7+2), $r8')),
        (0x8E18E, '"OUTLEN %x %x\\n", *(unsigned short*)($sp+4), $r10'),
        (0x986E8, ('"READRET %x %x %x\\n", $r10, *(unsigned char*)($sp+3), '
                  '*(unsigned int*)0xFEBE5E40')),
        (0x98704, '"NRC %x\\n", $r7'),
        (0x933F8, '"PUB %x %x %x\\n", *(unsigned int*)$r6, *(unsigned short*)($r6+4), $r7'),
    )
    commands: list[str] = []
    for offset, (address, body) in enumerate(probes):
        number = first + offset
        commands += [f"break *{address:#x}", f"commands {number}", "silent",
                     f"printf {body}", "continue", "end"]
    return commands


def prelude() -> list[str]:
    return [*dcm.batch_prelude(), *observer_breakpoints()]


def case_script(index: int, case: Case, label: str) -> list[str]:
    return [
        f"restore /out/img-{label}-{index:06d}.bin binary {RAM_BASE:#x}",
        f"set {{unsigned int}}{CAPACITY_CELL:#x} = {case.capacity:#x}",
        f"sim trace-file /out/tr-{label}-{index:06d}.txt",
        "sim trace-core on",
        f'printf "CASE {index}\\n"',
        f"set $r3={dcm.STACK_TOP:#x}", f"set $r31={dcm.SENTINEL:#x}",
        f"set $r5={dcm.TP_BASE:#x}", f"set $tp={dcm.TP_BASE:#x}",
        f"set $pc={dcm.DISPATCH_TASK:#x}", "continue",
        "sim trace-core off",
        f"dump binary memory /out/tp-{label}-{index:06d}.bin {RAM_BASE:#x} {RAM_BASE + RAM_SIZE:#x}",
        f'printf "TPR {index} %u\\n", $pc',
        f"set $pc={dcm.SENTINEL:#x}",
    ]


def parse_events(output: str) -> dict[int, dict[str, list[str]]]:
    events: dict[int, dict[str, list[str]]] = {}
    current: dict[str, list[str]] = {}
    for match in EVENT_RE.finditer(output):
        if match.group(1) == "CASE":
            current = {}
            events[int(match.group(2))] = current
            continue
        current.setdefault(match.group(1), []).append(match.group(2))
    return events


def run_group(elf: Path, batch: list[tuple[int, Case]], base: bytes, poison: bytes,
              out: Path, timeout: float, label: str) -> list[Observation]:
    work = elf.parent
    commands = prelude()
    images: dict[int, bytes] = {}
    for index, case in batch:
        image = scenario_image(base, case, poison)
        images[index] = image
        (work / f"img-{label}-{index:06d}.bin").write_bytes(image)
        commands.extend(case_script(index, case, label))
    commands.append(f'printf "TP_END={batch[-1][0]}\\n"')
    log_path = out / f"{label}.txt"
    try:
        output = run_elf(root=REPO_ROOT, elf_path=elf, stop=f"{dcm.SENTINEL:#x}",
                         memory_regions=dcm.SIM_MEMORY_REGIONS, gdb_commands=commands,
                         expected_output=[f"TP_END={batch[-1][0]}"], timeout=timeout,
                         output_path=log_path)
    except CodeFlashSimError as error:
        log_path.unlink(missing_ok=True)
        for index, _case in batch:
            for stale in work.glob(f"tr-{label}-{index:06d}.txt"):
                stale.unlink()
        if len(batch) > 1:
            middle = len(batch) // 2
            return (run_group(elf, batch[:middle], base, poison, out, timeout, label + "a")
                    + run_group(elf, batch[middle:], base, poison, out, timeout, label + "b"))
        index, case = batch[0]
        detail = str(error).splitlines()[-1][:200]
        return [Observation(case, -1, None, images[index],
                            error=f"simulator did not reach the sentinel: {detail}")]
    log_path.unlink(missing_ok=True)
    events = parse_events(output)
    pcs = {int(m.group(1)): int(m.group(2)) for m in RX_LINE.finditer(output)}
    observations = []
    for index, case in batch:
        dump_path = work / f"tp-{label}-{index:06d}.bin"
        trace_path = work / f"tr-{label}-{index:06d}.txt"
        dump = dump_path.read_bytes() if dump_path.is_file() else None
        trace = parse_core_accesses(trace_path) if trace_path.is_file() else []
        observation = Observation(case, pcs.get(index, -1), dump, images[index],
                                  events.get(index, {}), trace)
        if index not in pcs or dump is None or len(dump) != RAM_SIZE:
            observation.error = "no complete dump: the case did not return to the sentinel"
        observations.append(observation)
        dump_path.unlink(missing_ok=True)
        trace_path.unlink(missing_ok=True)
        (work / f"img-{label}-{index:06d}.bin").unlink(missing_ok=True)
    return observations


def run_cases(elf: Path, cases: list[Case], base: bytes, poison: bytes, out: Path,
              timeout: float, batch_size: int, label: str) -> list[Observation]:
    observations: list[Observation] = []
    for offset in range(0, len(cases), batch_size):
        batch = list(enumerate(cases[offset:offset + batch_size], offset))
        observations.extend(run_group(elf, batch, base, poison, out, timeout,
                                      f"{label}-{offset // batch_size:04d}"))
    return observations


def normalize_snapshot(elf: Path, out: Path, timeout: float) -> tuple[bytes, dict]:
    """Drive the firmware's own Dcm init chain over the real snapshot once."""
    work = elf.parent
    snapshot = SNAPSHOT.read_bytes()
    if hashlib.sha256(snapshot).hexdigest() != SNAPSHOT_SHA256:
        raise SystemExit("LocalRAM snapshot sha256 mismatch")
    source = work / "snapshot-input.bin"
    dump = work / "snapshot-normalized.bin"
    source.write_bytes(snapshot)
    commands = prelude()
    commands += [
        f"restore /out/{source.name} binary {RAM_BASE:#x}",
        f"set $r3={dcm.STACK_TOP:#x}", f"set $r31={dcm.SENTINEL:#x}",
        "set $pc=0x9887C", "continue",
        f"dump binary memory /out/{dump.name} {RAM_BASE:#x} {RAM_BASE + RAM_SIZE:#x}",
        'printf "NORMALIZED\\n"',
    ]
    try:
        run_elf(root=REPO_ROOT, elf_path=elf, stop=f"{dcm.SENTINEL:#x}",
                memory_regions=dcm.SIM_MEMORY_REGIONS, gdb_commands=commands,
                expected_output=["NORMALIZED"], timeout=timeout, output_path=out / "normalize.txt")
    finally:
        source.unlink(missing_ok=True)
    base = dump.read_bytes()
    dump.unlink(missing_ok=True)
    if len(base) != RAM_SIZE:
        raise SystemExit("normalized snapshot has the wrong size")

    def at(address: int, width: int) -> bytes:
        return base[address - RAM_BASE:address - RAM_BASE + width]

    return base, {
        "sha256": hashlib.sha256(base).hexdigest(),
        "changed_bytes_vs_snapshot": sum(a != b for a, b in zip(base, snapshot)),
        "latch_bitmap": at(LATCH_BITMAP, 8).hex(),
        "active_secondary_head": at(ACTIVE_SECONDARY, 4).hex(),
        "active_primary_head": at(ACTIVE_PRIMARY, 4).hex(),
        "event_state": at(EVENT_STATE, 0x14).hex(),
        "request_phase": at(dcm.REQUEST_PHASE, 1)[0],
    }


# ------------------------------------------------------------------ oracles

def _runs(offsets) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    for offset in offsets:
        if runs and runs[-1][1] == offset - 1:
            runs[-1] = (runs[-1][0], offset)
        else:
            runs.append((offset, offset))
    return runs


def in_family(pc: int | None) -> bool:
    return pc is not None and any(lo <= pc <= hi for lo, hi in FAMILY_RANGES)


def region_of(address: int) -> str:
    if RESP_BUF <= address < RESP_BUF + STOCK_CAPACITY:
        return "response"
    if STAGING_END <= address < STAGING_WINDOW_END:
        return "past_staging"
    if STAGING <= address < STAGING_END:
        return "staging"
    if EVENT_STATE <= address < STAGING:
        return "event_state"
    if SELECTOR_KIND <= address < SELECTOR_SUB + 2:
        return "selector_state"
    if RETAINED_CTX <= address < RETAINED_CTX + 0x1C:
        return "retained_context"
    if dcm.STACK_TOP - 0x400 <= address < dcm.STACK_TOP:
        return "stack"
    return "other"


def write_runs(accesses: list[dict], predicate, base: int = 0,
               byte_lo: int | None = None, limit: int = 128) -> list[dict]:
    """Coalesce traced writes selected by ``predicate``; offsets from ``base``.

    Only bytes at or after ``byte_lo`` are recorded, so a store straddling an
    object edge reports just the bytes past it.  ``bytes`` carries at most
    ``limit`` bytes of each run."""
    values: dict[int, int] = {}
    pcs: dict[int, set[int]] = {}
    for access in accesses:
        if access["operation"] != "write" or not predicate(access):
            continue
        for offset in range(access["width"]):
            address = access["address"] + offset
            if byte_lo is not None and address < byte_lo:
                continue
            values[address] = (access["value"] >> (8 * offset)) & 0xFF
            pcs.setdefault(address, set()).add(access["pc"] or -1)
    runs = []
    for start, end in _runs(sorted(values)):
        data = bytes(values[a] for a in range(start, end + 1))
        runs.append({
            "start": hex(start), "end": hex(end), "length": end - start + 1,
            "offset": start - base,
            "bytes": data[:limit].hex(),
            "bytes_truncated": len(data) > limit,
            "pcs": sorted({f"{pc:#x}" for a in range(start, end + 1) for pc in pcs[a]}),
        })
    return runs


def envelope() -> list[tuple[int, int]]:
    """Legitimate write sites: the calibrated Dcm/handler envelope, the
    response object, the staging buffer and the saved transport context.  The
    receive slot buffers are deliberately excluded so cross-talk is reported;
    the handler envelope's proprietary-event entry is widened to the staging
    buffer's end because this family writes the whole buffer."""
    ranges = [(lo, hi) for lo, hi in ci.STATIC_ENVELOPE]
    ranges += [(lo, hi) for lo, hi in dcm.HANDLER_ENVELOPE if lo != 0xFEBF4564]
    ranges.append((0xFEBF4564, STAGING_END - 1))
    ranges.append((RESP_BUF, RESP_BUF + STOCK_CAPACITY - 1))
    ranges.append((TRANSPORT_CONTEXT, TRANSPORT_CONTEXT + 27))
    return ranges


def judge(observation: Observation, poison: bytes) -> dict:
    case = observation.case
    configured = case.capacity
    record: dict = {
        "name": case.name,
        "family": case.family,
        "session": case.session,
        "request_hex": case.request.hex(),
        "request_length": len(case.request),
        "capacity": configured,
        "capacity_overlay": None if configured == STOCK_CAPACITY else f"0x{configured:X}",
        "stored_event": case.stored_event,
    }
    if case.note:
        record["note"] = case.note
    record["termination"] = ("sentinel" if observation.pc == dcm.SENTINEL
                             else f"abnormal pc=0x{observation.pc:x}" if observation.pc >= 0
                             else "abnormal: no return")
    if observation.error:
        record["error"] = observation.error
        return record
    dump, image, events = observation.dump, observation.image, observation.events
    assert dump is not None and image is not None

    def rd(address: int, width: int) -> bytes:
        return dump[address - RAM_BASE:address - RAM_BASE + width]

    def word(address: int) -> int:
        return int.from_bytes(rd(address, 4), "little")

    def node(index: int) -> dict:
        address = NODE_TABLE + 0x10 * index
        return {"data": hex(word(address + 4)),
                "length": int.from_bytes(rd(address + 8, 2), "little"),
                "disposition": rd(address + 12, 1)[0]}

    # What the firmware handed to the response queue.
    published = None
    if events.get("PUB"):
        fields = events["PUB"][-1].split()
        disposition = int(fields[2], 16)
        if disposition == 0:
            data, size = int(fields[0], 16), int(fields[1], 16)
            shown = rd(data, min(size, 64)).hex() if RAM_BASE <= data < RAM_BASE + RAM_SIZE else ""
            published = {"data": "0x" + fields[0], "length": size, "disposition": 0,
                         "bytes": shown}
        elif disposition == 1:
            published = {"data": hex(FINAL_NEGATIVE), "length": 3, "disposition": 1,
                         "bytes": rd(FINAL_NEGATIVE, 3).hex()}
        elif disposition == 2:
            published = {"data": None, "length": 0, "disposition": 2, "bytes": ""}
        else:
            pending = node(3)
            data = int(pending["data"], 16)
            shown = (rd(data, min(pending["length"], 8)).hex()
                     if RAM_BASE <= data < RAM_BASE + RAM_SIZE else "")
            published = {"data": pending["data"], "length": pending["length"],
                         "disposition": disposition, "bytes": shown}
    record["published"] = published
    record["response_length"] = word(ACTIVE_CTX + 12)
    record["response_capacity_after_header"] = word(ACTIVE_CTX + 20)
    record["final_nrc"] = f"0x{rd(FINAL_NRC, 1)[0]:02X}"
    record["nrc_events"] = [f"0x{int(v, 16):02X}" for v in events.get("NRC", [])]
    record["serializer"] = [{"kind": int(a, 16), "capacity": int(b, 16)}
                            for a, b in (line.split() for line in events.get("SER", []))]
    record["serializer_returns"] = [
        {"status": int(line.split()[0], 16), "length": int(line.split()[1], 16)}
        for line in events.get("SERRET", []) + events.get("SERRET2", [])]
    record["read_return"] = [{"status": int(a, 16), "nrc": int(b, 16),
                              "retained_response_length": int(c, 16)}
                             for a, b, c in (line.split() for line in events.get("READRET", []))]
    if events.get("ARMMERGE"):
        f = events["ARMMERGE"][-1].split()
        record["arm"] = "merge"
        record["arm_entry"] = {
            "entry_r16": "0x" + f[0], "entry_r17": "0x" + f[1],
            "list1": {"status": int(f[2], 16), "count": int(f[3], 16), "ptr": "0x" + f[4]},
            "list2": {"status": int(f[5], 16), "count": int(f[6], 16), "ptr": None},
            "out": "0x" + f[7],
        }
    elif events.get("ARMSELECT"):
        f = events["ARMSELECT"][-1].split()
        record["arm"] = "select"
        record["arm_entry"] = {
            "list1": {"status": int(f[0], 16), "count": int(f[1], 16), "ptr": "0x" + f[2]},
            "list2": {"status": int(f[3], 16), "count": int(f[4], 16), "ptr": None},
            "out": "0x" + f[5],
        }
    else:
        record["arm"] = "none"
    record["selected_length"] = [int(line.split()[0], 16) for line in events.get("OUTLEN", [])]
    record["latch_bitmap_reads"] = sorted(
        {f"{a['address']:#x}@{a['pc']:#x}" for a in observation.trace
         if a["operation"] == "read" and a["pc"] is not None
         and LATCH_BITMAP <= a["address"] < LATCH_BITMAP + 8})

    # Published length versus capacity.
    length = published["length"] if published else 0
    record["length_within_capacity"] = length <= configured
    record["header_bytes"] = rd(HEADER_COUNT, 1)[0]
    record["response_prefix_hex"] = rd(RESP_BUF, 64).hex()

    # Response poison: bytes inside a published positive extent that no store
    # wrote, stores beyond that extent inside the physical buffer, and (for
    # negative or suppressed dispositions) the header bytes the dispatcher
    # wrote into the shared buffer although nothing from it is published.
    response = RESP_BUF - RAM_BASE
    positive = bool(published) and published["disposition"] == 0
    extent = min(length, STOCK_CAPACITY) if positive else None
    record["poison_unwritten_offsets"] = [
        offset for offset in range(extent or 0) if dump[response + offset] == poison[offset]]
    record["writes_beyond_published_length"] = write_runs(
        observation.trace,
        lambda a: extent is not None
        and extent <= a["address"] - RESP_BUF < STOCK_CAPACITY, RESP_BUF)
    record["response_bytes_changed_without_publication"] = (
        sum(1 for offset in range(STOCK_CAPACITY)
            if dump[response + offset] != poison[offset])
        if published and not positive else 0)
    beyond = write_runs(
        observation.trace,
        lambda a: RESP_BUF <= a["address"] < RESP_BUF + STOCK_CAPACITY
        and a["address"] + a["width"] > RESP_BUF + configured,
        RESP_BUF, byte_lo=RESP_BUF + configured)
    record["writes_beyond_capacity"] = beyond
    # The merge/select copy loops are the only family stores into the response
    # object; anything they write past its physical end is an overrun.
    overrun = write_runs(
        observation.trace,
        lambda a: is_copy_pc(a["pc"])
        and a["address"] + a["width"] > RESP_BUF + STOCK_CAPACITY,
        RESP_BUF + STOCK_CAPACITY, byte_lo=RESP_BUF + STOCK_CAPACITY, limit=64)
    record["response_overrun_writes"] = overrun
    record["response_overrun_bytes"] = sum(run["length"] for run in overrun)

    # Every family store outside the response object, by region.
    outside = write_runs(
        observation.trace,
        lambda a: in_family(a["pc"])
        and not (RESP_BUF <= a["address"]
                 and a["address"] + a["width"] <= RESP_BUF + STOCK_CAPACITY))
    for span in outside:
        pcs = [int(pc, 16) for pc in span["pcs"]]
        span["region"] = ("response_overrun" if all(is_copy_pc(pc) for pc in pcs)
                          else region_of(int(span["start"], 16)))
    record["family_stack_write_bytes"] = sum(span["length"] for span in outside
                                             if span["region"] == "stack")
    outside = [span for span in outside if span["region"] != "stack"]
    record["family_writes_outside_response"] = outside
    record["unexpected_family_writes"] = [run for run in outside if run["region"] == "other"]
    blocks = write_runs(
        observation.trace,
        lambda a: any(lo <= a["address"] < lo + 0x100 for lo in dcm.SLOT_BUFFERS),
        dcm.SLOT_BUFFERS[0])
    for block in blocks:
        block["expected_in_place_mask"] = block["pcs"] == [f"{IN_PLACE_MASK_PC:#x}"]
    record["logical_block_writes"] = blocks
    # Every family store at or above the staging pointer is a staging write;
    # the selector, event, retained-context, response and stack objects all
    # sit below it.
    staging = [a for a in observation.trace if a["operation"] == "write"
               and in_family(a["pc"]) and not is_copy_pc(a["pc"]) and a["address"] >= STAGING]
    record["staging"] = {
        "start": hex(STAGING), "end": hex(STAGING_END - 1),
        "capacity": STAGING_END - STAGING,
        "stores": len(staging),
        "max_offset": max((a["address"] + a["width"] - STAGING - 1 for a in staging), default=None),
        "overflow": any(a["address"] + a["width"] > STAGING_END for a in staging),
    }
    record["staging_prefix_hex"] = rd(STAGING, 64).hex()

    # (v) Every write whose bytes land at or after the staging buffer's end
    # and below 0xFEBF5000, any PC, with offsets from 0xFEBF48E4 and bytes.
    past = write_runs(
        observation.trace,
        lambda a: a["address"] < STAGING_WINDOW_END
        and a["address"] + a["width"] > STAGING_END,
        STAGING_END, byte_lo=STAGING_END, limit=64)
    for span in past:
        pcs = [int(pc, 16) for pc in span["pcs"]]
        span["copy_loop"] = any(is_copy_pc(pc) for pc in pcs)
        # A serializer overflow comes from the serializer/writer PCs; the
        # merge/select copy loop only reaches this window in a primed-state
        # response overrun, which is reported separately.
        span["family"] = all(in_family(pc) and not is_copy_pc(pc) for pc in pcs)
    record["writes_past_staging_end"] = past
    record["staging_overflow_writes"] = [run for run in past if run["family"]]
    overread = [a for a in observation.trace if a["operation"] == "read"
                and is_copy_pc(a["pc"]) and a["address"] >= STAGING_END]
    record["copy_reads_past_staging_end"] = {
        "count": len(overread),
        "max_offset": max((a["address"] - STAGING_END for a in overread), default=None)}

    # Whole-window diff outside the calibrated legitimate-write envelope.
    allowed = envelope()
    changed = [RAM_BASE + offset for offset in range(RAM_SIZE) if dump[offset] != image[offset]]
    outside_all = [address for address in changed
                   if not any(lo <= address <= hi for lo, hi in allowed)]
    record["outside_envelope_runs"] = [
        {"start": hex(start), "end": hex(end), "length": end - start + 1,
         "bytes": dump[start - RAM_BASE:end - RAM_BASE + 1].hex()}
        for start, end in _runs(outside_all)[:64]]
    record["outside_envelope_run_count"] = len(_runs(outside_all))
    return record


def confirm_poison(records: list[dict], observations: list[Observation], second_poison: bytes) -> None:
    """Keep only poison-unwritten offsets reproduced under the second salt."""
    by_name = {o.case.name: judge(o, second_poison) for o in observations}
    for record in records:
        if not record.get("poison_unwritten_offsets"):
            continue
        second = by_name.get(record["name"])
        if second is None or second.get("error"):
            record["poison_confirmation"] = "not re-run"
            continue
        common = sorted(set(record["poison_unwritten_offsets"])
                        & set(second["poison_unwritten_offsets"]))
        record["poison_unwritten_first_salt"] = record["poison_unwritten_offsets"]
        record["poison_unwritten_offsets"] = common
        record["poison_confirmation"] = "second salt 0xB22DF"


SYNTHETIC_FAMILIES = ("accumulated", "state")   # primed serializer state, not request-built


def summarize(records: list[dict]) -> dict:
    judged = [r for r in records if "error" not in r]
    reachable = [r for r in judged if r["family"] not in SYNTHETIC_FAMILIES]
    stock = [r for r in reachable if r["capacity"] == STOCK_CAPACITY]
    published = [r for r in judged if r["published"]]

    def largest(rows: list[dict]) -> dict:
        if not rows:
            return {}
        top = max((r for r in rows if r["published"]),
                  key=lambda r: r["published"]["length"], default=None)
        if top is None:
            return {}
        return {"request_hex": top["request_hex"], "name": top["name"],
                "length": top["published"]["length"], "capacity": top["capacity"]}

    return {
        "cases": len(records),
        "families": dict(Counter(r["family"] for r in records)),
        "synthetic_state_families": list(SYNTHETIC_FAMILIES),
        "arms": dict(Counter(r.get("arm") for r in judged)),
        "dispositions": dict(Counter(r["published"]["disposition"] for r in published)),
        "nrcs": dict(Counter(n for r in judged for n in r["nrc_events"])),
        "merge_mode_request": next((r["request_hex"] for r in stock if r.get("arm") == "merge"),
                                   None),
        "largest_stock_response": largest(stock),
        "largest_stock_response_serializer_output": max(
            (n for r in stock for n in r["selected_length"]), default=None),
        "largest_response_any_capacity": largest(reachable),
        "largest_per_family": {family: largest([r for r in stock if r["family"] == family])
                               for family in sorted({r["family"] for r in stock})},
        "max_staging_offset_request_reachable": max(
            (r["staging"]["max_offset"] or 0 for r in reachable), default=0),
        "max_staging_offset_any": max(
            (r["staging"]["max_offset"] or 0 for r in judged), default=0),
        "abnormal_terminations": [f"{r['request_hex']}:{r['name']}" for r in records
                                  if not r["termination"].startswith("sentinel")],
        "length_over_capacity": [r["name"] for r in reachable
                                 if not r["length_within_capacity"] and r["capacity"] >= 2],
        "length_over_capacity_overlay_below_header_size": [
            r["name"] for r in reachable
            if not r["length_within_capacity"] and r["capacity"] < 2],
        "writes_beyond_capacity": [r["name"] for r in reachable
                                   if r["writes_beyond_capacity"] and r["capacity"] >= 2],
        "writes_beyond_capacity_overlay_below_header_size": [
            r["name"] for r in reachable
            if r["writes_beyond_capacity"] and r["capacity"] < 2],
        "response_bytes_changed_without_publication_max": max(
            (r["response_bytes_changed_without_publication"] for r in judged), default=0),
        "response_overrun_request_reachable": [
            r["name"] for r in reachable if r["response_overrun_writes"]],
        "unexpected_family_writes_request_reachable": [
            r["name"] for r in reachable if r["unexpected_family_writes"]],
        "outside_envelope_request_reachable": [
            r["name"] for r in reachable if r["outside_envelope_run_count"]],
        "response_overrun_synthetic_state": [
            {"request_hex": r["request_hex"], "name": r["name"],
             "bytes": r["response_overrun_bytes"],
             "published_length": (r["published"] or {}).get("length")}
            for r in judged if r["family"] in SYNTHETIC_FAMILIES
            and r["response_overrun_writes"]],
        "unexpected_family_writes": [r["name"] for r in judged if r["unexpected_family_writes"]],
        "logical_block_writes_not_in_place_mask": [
            r["name"] for r in judged
            if any(not run["expected_in_place_mask"] for run in r["logical_block_writes"])],
        "staging_overflow": [r["name"] for r in judged if r["staging_overflow_writes"]],
        "writes_past_staging_end_any_pc": [
            r["name"] for r in judged if r["writes_past_staging_end"]],
        "copy_reads_past_staging_end_synthetic_state": [
            {"request_hex": r["request_hex"], "name": r["name"],
             **r["copy_reads_past_staging_end"]}
            for r in judged if r["family"] in SYNTHETIC_FAMILIES
            and r["copy_reads_past_staging_end"]["count"]],
        "poison_unwritten_confirmed": [r["name"] for r in judged if r["poison_unwritten_offsets"]],
        "writes_beyond_published_length": [r["name"] for r in reachable
                                           if r["writes_beyond_published_length"]],
        "outside_envelope": [r["name"] for r in judged if r["outside_envelope_run_count"]],
        "nonzero_list2": [r["name"] for r in judged
                          if r.get("arm_entry", {}).get("list2", {}).get("count")],
    }


def overlay_notes(records: list[dict]) -> list[dict]:
    """Contract behaviour observed only under the sim-only capacity overlay.

    None of it is reachable at the stock 0x300 capacity; it documents how the
    family reacts when a serialized payload does not fit."""
    overlay = [r for r in records if "error" not in r and r["capacity_overlay"]]
    if not overlay:
        return []

    def sample(rows: list[dict]) -> list[str]:
        return [f"{r['request_hex']}:{r['name']}" for r in rows[:4]]

    def statuses(r: dict) -> set[int]:
        return {s["status"] for s in r["serializer_returns"]}

    underflow = [r for r in overlay if r["capacity"] < 2]
    swallowed = [r for r in overlay if r["request_hex"] == "ab01" and 6 in statuses(r)
                 and (r["published"] or {}).get("disposition") == 0]
    dropped = [r for r in overlay if r["request_hex"] != "ab01" and 6 in statuses(r)
               and r["published"] is None]
    invalid_nrc = [r for r in overlay if 10 in statuses(r) and "0x10" in r["nrc_events"]]
    no_room = [r for r in overlay if r["capacity"] == 2 and r["request_hex"] != "ab01"
               and r["published"] is None and not r["serializer"]]
    notes = [
        {"note": ("A configured capacity below the 2-byte header underflows the u32 context "
                  "capacity (0x91510 add -2): the serializers see 0xFFFF and the full payload "
                  "is published past the configured capacity."),
         "cases": len(underflow), "sample": sample(underflow),
         "evidence": "0x9150E-0x91512 capacity -= 2, 0x985C8-0x985D2, 0x8E0C2 min(.., 0xFFFF)"},
        {"note": ("Kind 1 (merge arm) swallows an over-capacity list: serializer status 6 "
                  "leaves list 1 with status 6, 0x8DF02-0x8DF0C returns 0 without writing, and "
                  "an empty positive response `EB 01` is published instead of NRC 0x14."),
         "cases": len(swallowed), "sample": sample(swallowed),
         "evidence": "0x5582C-0x5582E, 0x5097A-0x50988, 0x8DF02-0x8DF0C"},
        {"note": ("Kinds 2 and 3 with serializer status 6 stage nothing at all: 0x986F4-0x986FE "
                  "returns 0 for NRC 0x14 without calling dcm_report_negative_or_pending, so "
                  "the request is dropped silently."),
         "cases": len(dropped), "sample": sample(dropped),
         "evidence": "0x986F4-0x986FE"},
        {"note": ("Kind 3 bank records that each fit the size (0x55B76 tests the un-reduced "
                  "capacity per record) but exceed it in total leave 0x5096E for 0x5098A: "
                  "status 10, NRC 0x10, `7F AB 10` published."),
         "cases": len(invalid_nrc), "sample": sample(invalid_nrc),
         "evidence": "0x55B76-0x55B78, 0x5096E-0x5098A, 0x8DEBE (status 10 -> 0x10)"},
        {"note": ("A configured capacity of exactly 2 makes 0x986A8 return before any "
                  "serialization; nothing is staged."),
         "cases": len(no_room), "sample": sample(no_room), "evidence": "0x986A4-0x986AA"},
    ]
    return notes


def staging_overflow_section(records: list[dict], bounds: dict) -> dict:
    """Per serializer mode: how far the staging buffer is written and whether
    anything lands at or after 0xFEBF48E4."""
    judged = [r for r in records if "error" not in r]
    structural = {
        1: bounds["kind1_latched_list_max"],
        2: max(bounds["kind2_active_pair_max"], bounds["kind2_bank_max"]),
        3: max(max(row["active_pair_max"], row["bank_five_records_max"])
               for row in bounds["per_field_mask"].values()),
    }
    modes = {}
    for mode, selector, serializer in (
        (1, "kind1", "serialize_latched_event_identifiers_be16 @ 0x557C4"),
        (2, "kind2", "dispatch_capture_record_number_serialization @ 0x5592C"),
        (3, "kind3", "dispatch_capture_field_serialization @ 0x55C6E"),
    ):
        rows = [r for r in judged if any(s["kind"] == mode for s in r["serializer"])]
        hits = [(r, run) for r in rows for run in r["staging_overflow_writes"]]
        first = min(hits, key=lambda item: item[1]["offset"]) if hits else None
        requests = sorted({r["request_hex"] for r in rows
                           if r["family"] not in SYNTHETIC_FAMILIES})
        modes[str(mode)] = {
            "selector": selector,
            "serializer": serializer,
            "reachable_by_request": bool(requests),
            "gating": ("0x986D4 select_proprietary_events_or_reset_selection -> 0x8DEB4/0x50916 "
                       "stores FEBE81AD = kind; 0x5093A-0x50950 dispatch on it"),
            "request_hex_exercised": requests[:8],
            "cases": len(rows),
            "structural_max_payload": structural[mode],
            "max_staging_write_offset": max(
                (r["staging"]["max_offset"] for r in rows
                 if r["staging"]["max_offset"] is not None), default=None),
            "first_write_at_or_past_0xFEBF48E4": None if first is None else {
                "request_hex": first[0]["request_hex"], "case": first[0]["name"],
                "offset": first[1]["offset"], "address": first[1]["start"]},
            "bytes_written_past_0xFEBF48E4_max": max(
                (sum(run["length"] for run in r["staging_overflow_writes"]) for r in rows),
                default=0),
        }
    return {
        "buffer": {"start": hex(STAGING), "end": hex(STAGING_END - 1),
                   "bytes": STAGING_END - STAGING,
                   "size_evidence": [
                       "0xFEBF48E4 is dcm_proprietary_continuation (0x8E1E0 writes 0xFEBF48E4-E8)",
                       "no function references 0xFEBF461E..0xFEBF48E3 except through the staging pointer",
                       "0x8DE28 initializes the remaining size to 0x300",
                   ]},
        "oracle": ("every traced write with a byte in [0xFEBF48E4, 0xFEBF5000), any PC, "
                   "offsets relative to 0xFEBF48E4, bytes and PCs"),
        "modes": modes,
        "other_writes_in_window": [
            {"request_hex": r["request_hex"], "name": r["name"], **run}
            for r in judged for run in r["writes_past_staging_end"] if not run["family"]],
        "accumulated_state": {
            "cells": {"accumulated": hex(ACCUMULATED), "remaining": hex(REMAINING),
                      "phase": hex(PHASE), "subcall": hex(SUBCALL)},
            "request_reachable": False,
            "gating_instruction": (
                "0x5096A-0x50988: serialize_selected_proprietary_event returns only 0, 4, 6 "
                "or 10, so 0x8E0FC (cmp 0x2,r28 / bne 0x8E14E) never falls through to the "
                "pending store at 0x8E10E-0x8E100; 0xFEBF45E1 and 0xFEBF45DD are therefore "
                "never 2, the resume serializer call at 0x8E116 never executes, and 0x8E1A0/"
                "0x8E1C6 resets the accumulated count to 0 after every completed call."),
            "cases": [
                {"request_hex": r["request_hex"], "name": r["name"],
                 "serializer_capacity": [s["capacity"] for s in r["serializer"]],
                 "serializer_returns": r["serializer_returns"],
                 "arm": r["arm"],
                 "list1_count": r.get("arm_entry", {}).get("list1", {}).get("count"),
                 "selected_length": r["selected_length"],
                 "published": r["published"], "length_within_capacity": r["length_within_capacity"],
                 "staging_max_offset": r["staging"]["max_offset"],
                 "bytes_past_0xFEBF48E4": sum(run["length"] for run in r["staging_overflow_writes"]),
                 "response_overrun_bytes": r["response_overrun_bytes"],
                 "copy_reads_past_staging_end": r["copy_reads_past_staging_end"],
                 "termination": r["termination"]}
                for r in judged if r["family"] == "accumulated"],
        },
    }


# --------------------------------------------------------------------- main

def build_elf(sim_out: Path) -> Path:
    sim_out.mkdir(parents=True, exist_ok=True)
    _output, elf = run(root=REPO_ROOT, image_path=IMAGE, entry=0x7A57A, stop=f"{dcm.SENTINEL:#x}",
                       memory_regions=dcm.SIM_MEMORY_REGIONS,
                       gdb_commands=[f"set $r4={dcm.GP:#x}", f"set $r3={dcm.STACK_TOP:#x}",
                                     f"set $r31={dcm.SENTINEL:#x}", f"set $tp={dcm.TP_BASE:#x}",
                                     f"set $r5={dcm.TP_BASE:#x}", "set $r7=0",
                                     f"break *{dcm.SENTINEL:#x}", "continue"],
                       expected_output=["RH850_EXECUTION_VERIFIED"], timeout=300.0,
                       output_dir=sim_out)
    if elf is None:
        raise SystemExit("simulator ELF was not retained")
    dcm.build_dcra1_model(sim_out)
    return elf


def poison_image(salt: int) -> bytes:
    return ci.pattern_image(salt)[RESP_BUF - RAM_BASE:RESP_BUF - RAM_BASE + STOCK_CAPACITY]


def audit(out: Path, timeout: float, batch_size: int) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    sim_out = out / "linked-image"
    for pattern in ("img-*.bin", "tr-*.txt", "tp-*.bin"):
        for stale in sim_out.glob(pattern):
            stale.unlink()
    image = _image()
    elf = build_elf(sim_out)
    base, normalization = normalize_snapshot(elf, out, timeout)
    (out / "base-localram.bin").write_bytes(base)
    poison = poison_image(0xA11CE)

    # Phase 1: the largest payloads, so the capacity series straddles them.
    probes = {case.name: case for case in probe_cases(image)}
    observed: dict[str, int] = {}
    keys = dict(zip(probes, ("kind1_max", "kind3_active_max", "kind3_bank_max",
                            "kind2_bank_max")))
    for observation in run_cases(elf, list(probes.values()), base, poison, out, timeout,
                                 batch_size, "probe"):
        record = judge(observation, poison)
        if record.get("published") and record["published"]["disposition"] == 0:
            observed[keys[observation.case.name]] = max(record["selected_length"] or [0])
    missing = sorted(set(keys.values()) - set(observed))
    if missing:
        raise SystemExit(f"probe cases produced no payload: {missing}")

    # Phase 2: the complete matrix including the capacity series.  The
    # synthetic-state families can corrupt Dcm state by design, so they run in
    # small groups that a wedged case cannot take down with it.
    cases = build_cases(image, observed)
    volatile = [case for case in cases if case.family in SYNTHETIC_FAMILIES]
    steady = [case for case in cases if case.family not in SYNTHETIC_FAMILIES]
    observations = run_cases(elf, steady, base, poison, out, timeout, batch_size, "main")
    observations += run_cases(elf, volatile, base, poison, out, min(timeout, 30.0), 4, "state")
    records = [judge(o, poison) for o in observations]
    flagged = [o for o in observations if not o.error and judge(o, poison)["poison_unwritten_offsets"]]
    if flagged:
        second_poison = poison_image(0xB22DF)
        second = run_cases(elf, [o.case for o in flagged], base, second_poison, out,
                           timeout, batch_size, "salt2")
        confirm_poison(records, second, second_poison)
    for stale in sim_out.glob("tp-*.bin"):
        stale.unlink()

    largest = max(observed.values())
    bounds = structural_bounds(image)
    staging_overflow = staging_overflow_section(records, bounds)
    blockers = []
    if largest + 4 < STOCK_CAPACITY:
        blockers.append({
            "step": "payload approaching the 766/767-byte response capacity",
            "blocker": (
                "No stored-event state can push a serialized 0xAB payload near the response "
                f"capacity: the largest stock payload is {largest} bytes (serializer output) "
                "against 764 bytes of remaining capacity.  Field lengths are CodeFlash "
                "descriptor constants and each capture bank holds five 32-byte records."),
            "resolution": (
                "The boundary series (family 'capacity') is driven by a sim-only overlay of "
                f"the configured capacity cell 0x{CAPACITY_CELL:X}, straddling each maximum."),
        })
    blockers.append({
        "step": "accumulated count near 0x300 in front of a serializer, built by requests",
        "blocker": staging_overflow["accumulated_state"]["gating_instruction"],
        "resolution": ("the state is primed instead (family 'accumulated') and reported "
                       "under staging_overflow.accumulated_state"),
    })
    summary = summarize(records)
    synthetic_names = {r["name"] for r in records if r["family"] in SYNTHETIC_FAMILIES}

    def split_terminations(synthetic: bool) -> list[str]:
        return [name for name in summary["abnormal_terminations"]
                if (name.split(":", 1)[1] in synthetic_names) == synthetic]

    verdict = {
        "request_reachable_stock_capacity": {
            "cases": sum(1 for r in records if r["family"] not in SYNTHETIC_FAMILIES
                         and r["capacity"] == STOCK_CAPACITY),
            "writes_outside_response_envelope": summary["response_overrun_request_reachable"],
            "unexpected_family_writes": summary["unexpected_family_writes_request_reachable"],
            "outside_calibrated_envelope": summary["outside_envelope_request_reachable"],
            "writes_into_receive_blocks_other_than_in_place_mask":
                summary["logical_block_writes_not_in_place_mask"],
            "staging_overflow": summary["staging_overflow"],
            "length_over_capacity": summary["length_over_capacity"],
            "published_bytes_never_written": summary["poison_unwritten_confirmed"],
            "abnormal_terminations": split_terminations(False),
        },
        "latent_only_with_primed_state": {
            "families": list(SYNTHETIC_FAMILIES),
            "response_overrun_cases": len(summary["response_overrun_synthetic_state"]),
            "response_overrun_bytes_max": max(
                (row["bytes"] for row in summary["response_overrun_synthetic_state"]),
                default=0),
            "smallest_primed_state": next(
                ({"request_hex": row["request_hex"], "bytes": row["bytes"],
                  "published_length": row["published_length"]}
                 for row in summary["response_overrun_synthetic_state"]
                 if row["bytes"] == 4), None),
            "copy_reads_past_staging_end_cases": len(
                summary["copy_reads_past_staging_end_synthetic_state"]),
            "abnormal_terminations": split_terminations(True),
            "why_not_reachable": staging_overflow["accumulated_state"]["gating_instruction"],
        },
        "capacity_overlay_only": {
            "length_over_capacity": summary["length_over_capacity"],
            "writes_beyond_capacity": summary["writes_beyond_capacity"],
            "below_header_size_overlay": summary["length_over_capacity_overlay_below_header_size"],
        },
    }
    result = {
        "schema": SCHEMA,
        "image": {"path": str(IMAGE.relative_to(REPO_ROOT)), "sha256": IMAGE_SHA256},
        "snapshot": {"path": str(SNAPSHOT.relative_to(REPO_ROOT)), "sha256": SNAPSHOT_SHA256,
                     "normalization": "run_init_chain_9887C @ 0x9887C over the raw snapshot",
                     **normalization},
        "harness": {
            "entry": hex(dcm.DISPATCH_TASK),
            "base": "direct-dispatch priming over the real LocalRAM snapshot",
            "poison_salts": ["0xA11CE", "0xB22DF"],
            "response_buffer": hex(RESP_BUF),
            "stock_capacity": STOCK_CAPACITY,
            "capacity_source": f"CodeFlash u32 at 0x{CAPACITY_CELL:X} (read at 0x93D24)",
        },
        "request_format": {
            "kind1": "AB 01 (merge arm: FEBF45DC=1)",
            "kind2": "AB 02 hh ll (select arm; echo hh ll)",
            "kind3": "AB 03 hh ll sh sl (select arm; echo hh ll)",
            "subfunction_rows": ["0x25AFC -> 0x9874A", "0x25B0C -> 0x9876C", "0x25B1C -> 0x9878E"],
            "sessions": [1, 3],
            "evidence": [
                "0x91096 subfunction byte at row +0xC, 0x91086 length >= 2",
                "0x98668 length 0 / 0x9866A-0x98670 ids for kind 1",
                "0x9867A-0x98680 big-endian event id, 0x98686 length 2 for kind 2",
                "0x9868E-0x98696 event id + subselector, 0x98690 length 4 for kind 3",
                "0x9869C NRC 0x13 on length mismatch, 0x986B0-0x986CA echo copy",
                "0x8DEAE FEBF45DC = kind, 0x8E170/0x8E182 arm selection",
                "0x8DEB4/0x50916 FEBE81AD = kind, 0x5093A-0x50950 serializer dispatch",
            ],
        },
        "stored_event_state": {
            "latch_bitmap": hex(LATCH_BITMAP),
            "active_pair_records": [hex(ACTIVE_SECONDARY), hex(ACTIVE_PRIMARY)],
            "active_record_bytes": 0x60,
            "active_record_number_offset": hex(ACTIVE_RECORD_NUMBER),
            "capture_banks": hex(CAPTURE_BANKS),
            "bank_record_bytes": BANK_RECORD_SIZE,
            "staging_buffer": [hex(STAGING), hex(STAGING_END - 1)],
            "latch_bitmap_evidence": (
                "0x557CE movea -0x2e3c,gp (= 0xFEBE89C4) and 0x557E6 ld.w 0x40: the two "
                "words are 0xFEBE8A04/0xFEBE8A08; the trace reads of 0x557E6 are recorded "
                "per case as latch_bitmap_reads"),
            "invalid_record_markers": ["0x1111", "0x2222"],
        },
        "structural_bounds": bounds,
        "observed_maxima": observed,
        "catalogue": catalogue(image),
        "blockers": blockers,
        "staging_overflow": staging_overflow,
        "capacity_overlay_notes": overlay_notes(records),
        "verdict": verdict,
        "summary": summary,
        "records": records,
    }
    (out / "output-contract.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--batch-size", type=int, default=96)
    args = parser.parse_args()
    if not args.out.resolve().is_relative_to(REPO_ROOT / "build/out"):
        raise SystemExit("outputs must live under build/out/")
    result = audit(args.out, args.timeout, args.batch_size)
    summary = result["summary"]
    print(json.dumps({
        "cases": summary["cases"],
        "observed_maxima": result["observed_maxima"],
        "arms": summary["arms"],
        "merge_mode_request": summary["merge_mode_request"],
        "largest_stock_response": summary["largest_stock_response"],
        "staging_overflow_modes": {
            mode: {"request_hex": row["request_hex_exercised"][:1],
                   "max_staging_write_offset": row["max_staging_write_offset"],
                   "first_write_at_or_past_end": row["first_write_at_or_past_0xFEBF48E4"],
                   "bytes_written_past_end": row["bytes_written_past_0xFEBF48E4_max"]}
            for mode, row in result["staging_overflow"]["modes"].items()},
        "response_overrun_request_reachable": summary["response_overrun_request_reachable"],
        "abnormal_terminations": summary["abnormal_terminations"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
