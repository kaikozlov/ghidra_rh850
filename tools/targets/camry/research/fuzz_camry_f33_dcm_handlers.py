#!/usr/bin/env python3
"""Dcm service-handler fuzzer for camry-8965F3307000 (F33 EPS) on the GNU sim.

Drives eleven recovered diagnostic, transport, and crypto entry points directly
with tester-controlled request buffers and crypto vectors, reusing the strong
whole-window oracle from the CanTp ingress fuzzer (see
fuzz_camry_f33_cantp_ingress.py for the environment contract: TP/r5 priming,
PMR/syncp thunk patches, per-trial image restore):

- 0x922AA dcm_run_scheduled_request (void) — scheduled SID dispatcher
- 0x95978 dcm_write_did_service(op, ctx) — 0x2E WriteDataByIdentifier
- 0x97AE4 dispatch_routine_control_operation_status(op, ctx) — 0x31
- 0x8B632 write_did_payload_phase(idx, payload, len) — WDBI payload worker
- 0x962F2/0x965C0 — 0x22 ReadDataByIdentifier and 0x23 ReadMemoryByAddress
- 0x7B894 cantp_run_transmit_channels — TX state-machine tick
- 0x8B872/0x697F4/0x69BD8/0x69C58 — fixed-length crypto-bank
  activate/collect/submit/advance chain

The main oracle flags outside-envelope writes, boundary-watchpoint stops, slot
invariant violations, marker propagation, fill divergence, missing dumps, and
abnormal returns. Separate full-dispatch response-poison and exact-request
end-of-RAM passes expose under-written responses and request over-reads.
"""

import argparse
import hashlib
import json
import random
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from tools import REPO_ROOT
from tools.rh850_codeflash import CodeFlashSimError, run, run_elf
from tools.rh850_toolchain import command as rh850_command
from tools.targets.camry.research.fuzz_camry_f33_cantp_ingress import (
    CANTP_ENABLE,
    CELL_BASE,
    FENCES,
    GP,
    IMAGE,
    IMAGE_SHA256,
    RAM_BASE,
    RAM_REGION,
    RAM_SIZE,
    RESET_CELL,
    SENTINEL,
    SLOT_RANGES,
    STACK_TOP,
    STATIC_ENVELOPE,
    TP_BASE,
    attribute_sinks,
    fill_divergence,
    magic_hits,
    outside_runs,
    parallel_results,
    pattern_image,
    pattern_propagation,
    tx_state,
    verify_fill_divergence,
    verify_outside_runs,
)
from tools.targets.camry.research.fuzz_camry_f33_cantp_ingress import (
    SINKS as BASE_SINKS,
)

DISPATCH_TASK = 0x922AA
WDBI_SERVICE = 0x95978
ROUTINE_SERVICE = 0x97AE4
WDBI_WORKER = 0x8B632
CRYPTO_ACTIVATE = 0x8B872
CRYPTO_COLLECT = 0x697F4
CRYPTO_SUBMIT = 0x69BD8
CRYPTO_ADVANCE = 0x69C58

READ_DID_SERVICE = 0x962F2          # dcm_read_did_service (SID 0x22)
READ_MEM_SERVICE = 0x965C0          # dcm_read_memory_service (SID 0x23)
TX_TICK = 0x7B894                   # cantp_run_transmit_channels
RMEM_SOURCE = 0xFEBE7000            # allowed RAM source, primed for successful SID 0x23 reads
CRC_DCRA1_STORE = 0x67066           # first unmodeled DCRA1 MMIO access
# Keep the helper away from 0xFEC00000: request-tail tests deliberately place
# the last valid request byte at 0xFEBFFFFF and require the next byte unmapped.
DCRA1_MODEL_ENTRY = 0xFEF00000
DCRA1_MODEL_REGION = "0xFEF00000,0x1000"
DCRA1_MODEL_NAME = "dcra1-crc-model.bin"
DCRA1_MODEL_SOURCE = Path(__file__).with_name("dcra1_crc_model.c")
SIM_MEMORY_REGIONS = (RAM_REGION, DCRA1_MODEL_REGION)

# Handler-specific memory-copy and callback-dispatch sinks. The shared list
# covers transport and generic DCM paths; these prove the direct service
# families reach their payload-moving operations rather than only preflight.
SINKS = (
    *BASE_SINKS,
    (0x8E506, "dispatch_write_did_action"),
    (0x9847A, "dispatch_routine_start_callback"),
    (0x98590, "dispatch_routine_stop_callback"),
    (0x982E4, "dispatch_routine_result_callback"),
    (0x9767C, "pack_routine_scalar_response"),
    (0x8D546, "dispatch_memory_read_by_selector"),
    (0x8D4F6, "copy_memory_read_payload"),
)
REQUIRED_SINKS = (
    "cantp_build_consecutive_frame",
    "dcm_copy_transmit_data",
    "dcm_dispatch_did_length_callback",
    "execute_write_did_payload_and_report_result",
    "dcm_serialize_read_did_body",
    "execute_memory_read_and_report_result",
    "diag_routine_run_action_phase",
    "dispatch_write_did_action",
    "dispatch_routine_start_callback",
    "dispatch_routine_stop_callback",
    "dispatch_routine_result_callback",
    "pack_routine_scalar_response",
    "dispatch_memory_read_by_selector",
    "copy_memory_read_payload",
)


def sink_break_commands() -> list[str]:
    commands: list[str] = []
    for number, (addr, name) in enumerate(SINKS, start=2):
        commands += [
            f"break *{addr:#x}",
            f"commands {number}",
            "silent",
            f'printf "SINK {name}\\n"',
            "continue",
            "end",
        ]
    return commands


# Consumer buffers scanned for verbatim marker words (uninit-read propagation).
DCM_CONSUMER_RANGES = (
    *SLOT_RANGES,
    (0xFEBE5A20, 0xFEBE5D1F),   # shared response buffer, configured capacity 0x300
    (0xFEBE5140, 0xFEBE5208),   # crypto fragments/results staging
    (0xFEBF3B18, 0xFEBF3C20),   # WDBI action + clear-diagnostic state
)

# Shared driver constants (scout-recovered; see docs and the CantpFacts corpus)
SESSION = 0xFEBE595C          # app_dcm_session_snapshot.current (1/2/3)
SECURITY_BITMAP = 0xFEBE5954  # app_dcm_security_bitmap[2]
REQUEST_PHASE = 0xFEBE5960    # dcm_request_phase; 2 = dispatch a completed slot
PENDING_SLOT = 0xFEBE59E0     # u16
SLOT_STATE = 0xFEBE59F0       # 16 B/slot: cursor@+0 length@+4 remaining@+8 receiving@+0xA
SLOT_BUFFERS = (0xFEBE5651, 0xFEBE5751, 0xFEBE5851)
ADMISSION = (0xFEBE81CC, 0xFEBE81AC)  # degrade gates; admission passes when both 'Z'
ADMISSION_CLEAR = 0xFEBE7F97          # must NOT be 'Z' (0x5A) for admission to pass
WDBI_STAGING = 0xFEBF3B21     # write_did_payload_phase staging-branch prime
REQ_BUF = 0xFEBE4200          # scratch request bytes (never firmware-written)
CTX_BUF = 0xFEBE4300          # context after the full 0x100-byte request scratch
RESP_BUF = 0xFEBE5A20         # shared Dcm response buffer (0x300-byte configured capacity)
ACTIVE_DCM_CONTEXT = 0xFEBE5630  # full-dispatch F33DcmMessageContext
RDBI_CONTEXT = 0xFEBE5D84        # retained direct SID-0x22 context
# Exact CodeFlash configuration at 0x257D0/0x25806/0x30E2F:
# five u8 generation counters, byte-aligned selector/mode, threshold 3.
CRYPTO_POOL = 0xFEBE4A48
CRYPTO_COUNTERS = tuple(0xFEBE5338 + i for i in (0x12, 0x13, 0x14, 0x15, 0x16))
CRYPTO_POOL_OFFSETS = (0x9F, 0xA0, 0xA7, 0xAF, 0xB7, 0xBF)
CRYPTO_THRESHOLD = 3

WDBI_DIDS = (0x0204, 0x2001, 0x2002, 0x2005, 0x2006, 0x2007, 0x2008, 0x2009,
             0x200D, 0x2010, 0x2012, 0x2013, 0x2014)   # write_did_callbacks rows
ROUTINE_RIDS = (0x1000, 0x1001, 0x1002, 0x1004, 0x1007, 0x1008, 0x1009, 0x100E,
                0x100F, 0x1010, 0x1100, 0x1103, 0x1106, 0x1108, 0x1109, 0x110A,
                0x110B, 0x110C, 0x110D)               # routine_callbacks rows

# Additional legitimate write sites beyond the CanTp ingress envelope.
# Each row is per-service state owned by a named diagnostic writer
# (verified via tools/pseudo --data-ref on this image).
HANDLER_ENVELOPE = (
    (0xFEBE5044, 0xFEBE504B),   # crypto key-generation snapshot (69fa2)
    (0xFEBE5060, 0xFEBE50C0),   # crypto test chain cells (RID 0x100F)
    (0xFEBE5140, 0xFEBE5208),   # fixed crypto fragments/results + RID 0x1010 M4/M5
    (0xFEBE5620, 0xFEBE5650),   # NRC cell, active-callback cell, SID, message context
    (0xFEBE5A20, 0xFEBE5D1F),   # shared response buffer; configured capacity is 0x300
    (0xFEBE5D10, 0xFEBE5E0F),   # callback, retained request, and service state
    (0xFEBE5E10, 0xFEBE5E60),   # 0x31 pending row/type + request mirror
    (0xFEBE5F80, 0xFEBE6026),   # DTC iteration state + exact 160-byte snapshot
    (0xFEBE6AD0, 0xFEBE6AF0),   # learned-quad persist byte (357c0/35a96)
    (0xFEBE7F90, 0xFEBE7FA0),   # admission gate (liveness byte)
    (0xFEBE8190, 0xFEBE81D0),   # admission echo + gates (4d136)
    (0xFEBE82D0, 0xFEBE82E0),   # diagnostic clear-op queue (517dc)
    (0xFEBE6150, 0xFEBE615A),   # diagnostic capture request/completion state
    (0xFEBE8393, 0xFEBE8393),   # capture-slot dirty marker (52f32)
    (0xFEBE8483, 0xFEBE8483),   # capture-slot dirty marker (52f32)
    (0xFEBE8573, 0xFEBE8573),   # capture-slot dirty marker (52f32)
    (0xFEBE8607, 0xFEBE8608),   # counter-record dirty/completion state (54566)
    (0xFEBE8686, 0xFEBE8687),   # dual 96-byte record marker (54ac6)
    (0xFEBE86E6, 0xFEBE86E7),   # dual 96-byte record marker (54ac6)
    *((0xFEBE8748 + 0x20 * i, 0xFEBE8749 + 0x20 * i) for i in range(5)),
    *((0xFEBE8888 + 0x20 * i, 0xFEBE8889 + 0x20 * i) for i in range(10)),
    (0xFEBE89C4, 0xFEBE89D5),   # capture-bank write state
    (0xFEBF0311, 0xFEBF0317),   # NVM request state written by record reset
    (0xFEBF0488, 0xFEBF049A),   # NVM family-0 request/buffer state (672c0)
    (0xFEBF065A, 0xFEBF065A),   # redundant-u8 primary repaired by DID 0x010B (70a36)
    (0xFEBF067A, 0xFEBF067A),   # NVM family-0 request index (67350)
    (0xFEBF10A2, 0xFEBF10A2),   # redundant-u8 complement repaired by DID 0x010B (70a3c)
    (0xFEBF10C6, 0xFEBF10C6),   # redundant-u8 complement repaired by DID 0x010B (70a40)
    (0xFEBF10AA, 0xFEBF10AA),   # NVM hold/application family state (66d6e)
    (0xFEBF10CE, 0xFEBF10CE),   # NVM hold/application family state (66d6e)
    (0xFEBF6C10, 0xFEBF6C5A),   # NVM transfer and completion context
    (0xFEBF1310, 0xFEBF13B0),   # ICU crypto selection/lock/output service slots
    (0xFEBEAF40, 0xFEBEAF50),   # lifecycle normalization byte (b9212/b9320)
    (0xFEBEB200, 0xFEBEB4A0),   # routine 1106/1009/1007 lifecycle monitors
    (0xFEBEB18F, 0xFEBEB18F),   # DID 0x2012 availability override (b41a4)
    (0xFEBF3B18, 0xFEBF3C20),   # WDBI action + clear-diagnostic state (8c234)
    (0xFEBF3C21, 0xFEBF423F),   # DTC-list continuation metadata + scratch banks
    (0xFEBF4240, 0xFEBF4270),   # snapshot identifier sources (8ccb8/8ce84)
    (0xFEBF4564, 0xFEBF461D),   # DTC snapshot/control and proprietary-event state
    (0xFEBF48E4, 0xFEBF49A0),   # proprietary completion + dispatcher scratch
)
ENVELOPE = [list(r) for r in STATIC_ENVELOPE] + [list(r) for r in HANDLER_ENVELOPE]
_LIFECYCLE_BASES: dict[int, bytes] = {}
# dcm_begin_read_did_request @ 0x961DC copies all seven words of the 28-byte
# message context. The compiler copy includes two opaque fields that neither
# dcm_reset_message_context @ 0x91386 nor dcm_initialize_message_context @
# 0x913C2 writes. Exact-target xrefs and the typed corpus show no consumers;
# the copied bytes are inert retained padding, like dead returned stack bytes.
DIVERGENCE_DEAD_RANGES = (
    (0xFEBE1800, 0xFEBE1FFF),
    (0xFEBE5D96, 0xFEBE5D97),
    (0xFEBE5D9D, 0xFEBE5D9D),
)

RX_LINE = re.compile(r"^TPR (\d+) (\d+)$", re.MULTILINE)


@dataclass(frozen=True)
class Trial:
    family: str
    entry: int
    regs: tuple[tuple[str, int], ...] = ()       # (reg, value) set before continue
    primes: tuple[tuple[int, bytes], ...] = ()   # baked into the start image


def ctx_primes(request_len: int, service_id: int,
               response_capacity: int = 0x300) -> tuple[tuple[int, bytes], ...]:
    """One coherent 28-byte F33DcmMessageContext at CTX_BUF."""
    message = (
        REQ_BUF.to_bytes(4, "little")
        + request_len.to_bytes(4, "little")
        + RESP_BUF.to_bytes(4, "little")
        + (0).to_bytes(4, "little")       # response_length
        + b"\x00\x00\x00\x00"            # addressing, suppression, opaque_12
        + response_capacity.to_bytes(4, "little")
        + bytes([service_id, 0])          # service_id, opaque_19
        + b"\x00\x00"                    # service_list_selector
    )
    return ((CTX_BUF, message),)


def session_primes(session: int = 1, security_bitmap: int = 0) -> tuple[tuple[int, bytes], ...]:
    return (
        (SESSION, bytes([session, session, session, 0])),
        (SECURITY_BITMAP, security_bitmap.to_bytes(4, "little") + b"\x00" * 4),
    )


def nvm_direct_primes() -> tuple[tuple[int, bytes], ...]:
    """Reconstruct reset state, with the unavailable DataFlash driver blocked."""
    scheduler = bytearray(0x24)
    scheduler[0:4] = (0x9DA70AE7).to_bytes(4, "little")
    scheduler[4:6] = b"\xff\xff"
    scheduler[0x10:0x14] = (0x9DA70AE7).to_bytes(4, "little")
    scheduler[0x1E:0x20] = b"\xff\xff"
    scheduler[0x20] = 1

    operation = bytearray(0x15)
    operation[0:4] = b"\xff" * 4
    operation[4:6] = b"\xff\xff"
    operation[0x10:0x12] = (1).to_bytes(2, "little")
    operation[0x12:0x14] = b"\xff\xff"

    driver = bytearray(0x0D)
    driver[8:10] = b"\xff\xff"
    # The simulator has no FACI/DataFlash MMIO model. This is the firmware's
    # real latched-block state; it makes the public NVM API reject before MMIO.
    driver[0x0A] = 1

    physical = bytearray(0x10)
    physical[0:4] = b"\xff" * 4
    physical[0x0F] = 1

    transfer = bytearray(0x8B)
    transfer[0x60:0x64] = b"\xff" * 4
    transfer[0x68:0x6A] = b"\xff\xff"
    transfer[0x6C:0x6E] = b"\xff\xff"
    transfer[0x8A] = 0xFF

    service = bytearray(0x29)
    service[0x08:0x0A] = b"\xff\xff"
    service[0x10:0x12] = b"\xff\xff"
    service[0x18] = 0xFF
    service[0x19:0x1C] = b"\xff\x01\x01"
    service[0x1E] = 1
    service[0x1F:0x21] = b"\xff\xff"
    service[0x22:0x24] = b"\xff\xff"
    service[0x24] = 0xFF

    return (
        (0xFEBF0693, b"\x00\x00"),
        (0xFEBF6104, bytes(scheduler)),
        (0xFEBF6AEC, bytes(operation)),
        (0xFEBF6B04, (0x766F4).to_bytes(4, "little") + b"\x00" * 8),
        (0xFEBF6B18, bytes(driver)),
        (0xFEBF6B68, bytes(physical)),
        (0xFEBF6BD0, bytes(transfer)),
        (0xFEBF6CB4, bytes(service)),
    )


def crypto_primes(selector: int, mode: int, payload: bytes, expected: bytes,
                  *, ready_to_commit: bool = False, advance: bool = False
                  ) -> tuple[tuple[int, bytes], ...]:
    """Prime the fixed five-fragment collector or fixed-16-byte submitter."""
    if len(payload) != 16 or len(expected) != 16:
        raise ValueError("crypto test vectors are exactly 16 bytes")
    fragments = payload + expected
    primes: list[tuple[int, bytes]] = [
        (CRYPTO_POOL + CRYPTO_POOL_OFFSETS[0], bytes([selector & 0xFF])),
        (CRYPTO_POOL + CRYPTO_POOL_OFFSETS[1], bytes([mode & 0xFF])),
        (CRYPTO_POOL + CRYPTO_POOL_OFFSETS[2], fragments[0:8]),
        (CRYPTO_POOL + CRYPTO_POOL_OFFSETS[3], fragments[8:16]),
        (CRYPTO_POOL + CRYPTO_POOL_OFFSETS[4], fragments[16:24]),
        (CRYPTO_POOL + CRYPTO_POOL_OFFSETS[5], fragments[24:32]),
        (0xFEBE50A4, bytes([selector & 0xFF, mode & 0xFF])),
        (0xFEBE5186, payload),
        (0xFEBE5196, expected),
        # Mode-1 command 5 and mode-0 command 1 idle/lock gates.
        (0xFEBF1378, b"\xE1"),
        (0xFEBF137A, b"\xD2"),
        (0xFEBF1390, b"\xE1"),
        (0xFEBF1392, b"\xD2"),
    ]
    if ready_to_commit:
        primes.extend((counter, b"\x01") for counter in CRYPTO_COUNTERS)
        primes.extend((
            # last selector, staged selector/mode, last mode
            (0xFEBE509E, bytes([selector & 0xFF, selector & 0xFF,
                                mode & 0xFF, mode & 0xFF])),
            (0xFEBE50A6, bytes([CRYPTO_THRESHOLD - 1]) * 5),
            (0xFEBE50AB, b"\x00" * 5),
            (0xFEBE50B0, b"\x01" * 5),
            (0xFEBE5146, fragments),
        ))
    if advance:
        primes.extend(((0xFEBE509B, b"\x01"), (0xFEBE509C, b"\x11")))
    return tuple(primes)

def read_did_tables() -> tuple[list[int], list[tuple[int, int, int]]]:
    """Publication DIDs (0x2927C table, corpus-typed [242]) and the class
    table edges (dcm_did_class[5] @ 0x2603C, F33DcmDidClass: length fn-ptr
    +4, first_did +20, last_did +22). The configured-table count word at
    0x26014 is zero in this image, so runtime DID resolution rides the
    class ranges; both tables are swept regardless."""
    image = IMAGE.read_bytes()
    pub_dids = sorted({int.from_bytes(image[0x2927C + i * 16:0x2927C + i * 16 + 2], "little")
                       for i in range(242)})
    classes = []
    for i in range(min(int.from_bytes(image[0x26016:0x26018], "little"), 6)):
        entry = 0x2603C + i * 28
        classes.append((int.from_bytes(image[entry + 4:entry + 8], "little"),
                        int.from_bytes(image[entry + 20:entry + 22], "little"),
                        int.from_bytes(image[entry + 22:entry + 24], "little")))
    return pub_dids, classes


# ---------------------------------------------------------------- generation

def generate(seed: int, random_each: int) -> list[Trial]:
    rng = random.Random(seed)
    items: list[Trial] = []

    # 1) dispatcher: SID sweep with short bodies, all slots and sessions.
    for sid in range(0x100):
        for slot in (0, 1, 2):
            body = bytes([sid, 0x03]) if sid in (0x10, 0x11) else bytes([sid])
            items.append(Trial("disp_sid", DISPATCH_TASK, (),
                               dispatcher_primes(slot, body, 1)))
    for sid in (0x10, 0x11, 0x14, 0x19, 0x22, 0x23, 0x27, 0x2A, 0x2C, 0x2E,
                0x31, 0x37, 0x3D, 0x3E, 0x85, 0x86, 0x87):
        for sub in (0x00, 0x01, 0x02, 0x03, 0x7F, 0x80, 0xFF):
            items.append(Trial("disp_sub", DISPATCH_TASK, (),
                               dispatcher_primes(0, bytes([sid, sub, 0xA5]), 1)))
    for session in (0, 1, 2, 3, 0xFF):
        items.append(Trial("disp_session", DISPATCH_TASK, (),
                           dispatcher_primes(0, b"\x22\xf1\x90\x11", session)))
    for security_bitmap in (0, 1, 2, 0x8000_0000, 0xFFFF_FFFF):
        items.append(Trial("disp_bitmap", DISPATCH_TASK, (),
                           dispatcher_primes(0, b"\x27\x03", 1)
                           + session_primes(1, security_bitmap)))

    # 2) 0x2E service: every configured DID x boundary request lengths.
    for did in WDBI_DIDS:
        for session in (1, 2, 3):
            for length in (0, 1, 2, 3, 4, 5, 8, 0x10, 0x20, 0x40, 0x100):
                body = (bytes([did >> 8, did & 0xFF])
                        + b"\x5A" * max(0, length - 2))[:min(length, 0x100)]
                items.append(Trial("wdbi_len", WDBI_SERVICE, (("$r6", 0), ("$r7", CTX_BUF)),
                                   session_primes(session)
                                   + ((REQ_BUF, body),)
                                   + ctx_primes(min(length, 0x100), 0x2E)))
    for op in (1, 2, 3, 0xFF):
        items.append(Trial("wdbi_op", WDBI_SERVICE, (("$r6", op), ("$r7", CTX_BUF)),
                           tuple(session_primes(1))
                           + ((REQ_BUF, b"\x20\x12\x01"),)
                           + ctx_primes(3, 0x2E)))
    for security_bitmap in (1, 0xFFFF_FFFF):
        items.append(Trial("wdbi_bitmap", WDBI_SERVICE, (("$r6", 0), ("$r7", CTX_BUF)),
                           session_primes(1, security_bitmap)
                           + ((REQ_BUF, b"\x20\x12\x01"),)
                           + ctx_primes(3, 0x2E)))

    # 3) 0x31 service: every RID x control type x boundary lengths.
    for rid in ROUTINE_RIDS:
        for session in (1, 2, 3):
            for control in (0x00, 0x01, 0x02, 0x03, 0x81, 0xFF):
                for length in (0, 1, 2, 3, 4, 8, 0x43, 0x44):
                    body = (bytes([control, rid >> 8, rid & 0xFF])
                            + b"\xA5" * max(0, length - 3))[:min(length, 0x100)]
                    items.append(Trial("rid_len", ROUTINE_SERVICE, (("$r6", 0), ("$r7", CTX_BUF)),
                                       session_primes(session)
                                       + ((REQ_BUF, body),)
                                       + ctx_primes(min(length, 0x100), 0x31)))
    for op in (1, 2, 3, 0xFF):
        items.append(Trial("rid_op", ROUTINE_SERVICE, (("$r6", op), ("$r7", CTX_BUF)),
                           tuple(session_primes(1))
                           + ((REQ_BUF, b"\x01\x10\x0f"),)
                           + ctx_primes(3, 0x31)))

    # 4) WDBI payload worker: row index and length arithmetic (no Dcm gates).
    for matched in (*range(13), 13, 14, 0xFEFF, 0xFFFF):
        for length in (0, 1, 7, 8, 9, 0x10, 0x40, 0xFF, 0xFFFF):
            payload = bytes(rng.randrange(256) for _ in range(min(length, 0x100)))
            items.append(Trial("worker_len", WDBI_WORKER,
                               (("$r6", matched), ("$r7", REQ_BUF), ("$r8", length)),
                               ((REQ_BUF, payload),)))
    for staging in (0, 1):
        for length in (0, 1, 7, 8, 9, 0x20):
            payload = bytes(rng.randrange(256) for _ in range(min(length, 0x100)))
            items.append(Trial("worker_stage", WDBI_WORKER,
                               (("$r6", 10), ("$r7", REQ_BUF), ("$r8", length)),
                               ((REQ_BUF, payload),
                                (WDBI_STAGING, bytes([staging])))))

    # 5) fixed-length crypto bank: collector, direct submit, and full advance.
    # Selector/mode are tester-controlled, but all copy lengths are literal 8/16.
    items.append(Trial("crypto_activate", CRYPTO_ACTIVATE))
    for selector in (0, 1, 0xFF):
        for mode in (0, 1, 2, 0xFF):
            payload = bytes((selector + mode + i) & 0xFF for i in range(16))
            expected = bytes(b ^ 0xA5 for b in payload)
            items.append(Trial("crypto_collect", CRYPTO_COLLECT, (),
                               crypto_primes(selector, mode, payload, expected,
                                             ready_to_commit=True)))
            items.append(Trial("crypto_submit", CRYPTO_SUBMIT, (),
                               crypto_primes(selector, mode, payload, expected)))
    for selector, mode in ((0, 0), (0, 1), (1, 1)):
        payload = bytes((0x30 + selector + mode + i) & 0xFF for i in range(16))
        expected = bytes(b ^ 0x5A for b in payload)
        items.append(Trial("crypto_advance", CRYPTO_ADVANCE, (),
                           crypto_primes(selector, mode, payload, expected,
                                         ready_to_commit=True, advance=True)))

    # 6) seeded random: bodies, lengths, ops, slots, sessions, crypto vectors.
    for _ in range(random_each):
        which = rng.randrange(7)
        body = bytes(rng.randrange(256) for _ in range(min(0x100, 1 + rng.randrange(0x50))))
        if which == 0:
            slot = rng.randrange(3)
            items.append(Trial("rand_disp", DISPATCH_TASK, (),
                               dispatcher_primes(slot, body, rng.choice((0, 1, 2, 3)))))
        elif which == 1:
            items.append(Trial("rand_wdbi", WDBI_SERVICE,
                               (("$r6", rng.choice((0, 0, 2, 3))), ("$r7", CTX_BUF)),
                               session_primes(rng.choice((1, 2, 3)))
                               + ((REQ_BUF, body),) + ctx_primes(len(body), 0x2E)))
        elif which == 2:
            items.append(Trial("rand_rid", ROUTINE_SERVICE,
                               (("$r6", rng.choice((0, 0, 2, 3))), ("$r7", CTX_BUF)),
                               session_primes(rng.choice((1, 2, 3)))
                               + ((REQ_BUF, body),) + ctx_primes(len(body), 0x31)))
        elif which == 3:
            items.append(Trial("rand_worker", WDBI_WORKER,
                               (("$r6", rng.randrange(0x1_0000)), ("$r7", REQ_BUF),
                                ("$r8", rng.choice((0, 1, 7, 8, 9, 0x20, rng.randrange(0x1_0000))))),
                               ((REQ_BUF, bytes(rng.randrange(256) for _ in range(0x100))),)))
        else:
            selector = rng.choice((0, 1, rng.randrange(0x100)))
            mode = rng.choice((0, 1, 2, rng.randrange(0x100)))
            payload = bytes(rng.randrange(256) for _ in range(16))
            expected = bytes(rng.randrange(256) for _ in range(16))
            if which == 4:
                items.append(Trial("rand_crypto_collect", CRYPTO_COLLECT, (),
                                   crypto_primes(selector, mode, payload, expected,
                                                 ready_to_commit=True)))
            elif which == 5:
                items.append(Trial("rand_crypto_submit", CRYPTO_SUBMIT, (),
                                   crypto_primes(selector, mode, payload, expected)))
            else:
                items.append(Trial("rand_crypto_advance", CRYPTO_ADVANCE, (),
                                   crypto_primes(selector, mode, payload, expected,
                                                 ready_to_commit=True, advance=True)))
    # Read side (SID 0x22): every configured publication DID plus class-range
    # edges — the class `length` fn-ptr at 0x2603C+4 is not null-checked on
    # the 0x9449E path, so range-boundary DIDs probe it directly.
    pub_dids, classes = read_did_tables()

    def rdbi(name: str, body: bytes, session: int, security: int = 0,
             capacity: int = 0x300) -> Trial:
        return Trial(name, READ_DID_SERVICE, (("$r6", 0), ("$r7", CTX_BUF)),
                     session_primes(session, security) + ((REQ_BUF, body),)
                     + ctx_primes(len(body), 0x22, response_capacity=capacity))

    for did in pub_dids:
        items.append(rdbi(f"rdbi_{did:04x}", bytes((did >> 8, did & 0xFF)), 1))
    for did in pub_dids[:24]:
        for session in (2, 3):
            items.append(rdbi(f"rdbi_{did:04x}_s{session}",
                              bytes((did >> 8, did & 0xFF)), session))
    for did in pub_dids[:8]:
        items.append(rdbi(f"rdbi_{did:04x}_sec", bytes((did >> 8, did & 0xFF)), 2, 1))
    for _length_cb, first, last in classes:
        for did in {(first - 1) & 0xFFFF, first, first + 1, (first + last) // 2,
                    last - 1, last, (last + 1) & 0xFFFF}:
            for session in (1, 2):
                items.append(rdbi(f"rdbi_cls_{did:04x}_s{session}",
                                  bytes((did >> 8, did & 0xFF)), session))
    for length, name in ((1, "short"), (2, "one"), (3, "odd"), (4, "two"),
                         (5, "two_pad"), (0, "empty")):
        items.append(rdbi(f"rdbi_len_{name}", b"\x0f\x01\x0f\x01\xa5"[:length], 1))
    for capacity in (0, 1, 2, 0xFFFE, 0xFFFF):
        items.append(rdbi(f"rdbi_cap_{capacity:#x}", b"\xf1\x81", 1, capacity=capacity))

    # Read side (SID 0x23). Direct callback input excludes the SID byte.
    # CodeFlash allows one ALFID, 0x15: one-byte size plus memory ID and
    # four-byte address. All 256 nibble pairs still exercise the format gate.
    def fixed_width(value: int, width: int) -> bytes:
        if width == 0:
            return b""
        return (value & ((1 << (8 * width)) - 1)).to_bytes(width, "big")

    def rmem(addr_size: int, size_size: int, addr: int, size: int,
             session: int = 3, capacity: int = 0x300,
             memory_id: int | None = None) -> Trial:
        if memory_id is None:
            address = fixed_width(addr, addr_size)
            memory_tag = ""
        else:
            if addr_size != 5:
                raise ValueError("memory ID encoding requires five address bytes")
            address = bytes([memory_id]) + fixed_width(addr, 4)
            memory_tag = f"_m{memory_id:#x}"
        req = bytes([(size_size << 4) | addr_size]) + address + fixed_width(size, size_size)
        primes = (session_primes(session)
                  + ((REQ_BUF, req),)
                  + ctx_primes(len(req), 0x23, response_capacity=capacity))
        if memory_id == 1 and addr == RMEM_SOURCE and 0 < size <= 0xFF:
            primes += ((RMEM_SOURCE, bytes((0x40 + i) & 0xFF for i in range(size))),)
        if memory_id == 2:
            primes += nvm_direct_primes()
        return Trial(
            f"rmem_a{addr_size}_s{size_size}{memory_tag}_{addr:#x}_{size:#x}_c{capacity:#x}",
            READ_MEM_SERVICE, (("$r6", 0), ("$r7", CTX_BUF)), primes,
        )

    for addr_size in range(16):
        for size_size in range(16):
            valid_format = addr_size == 5 and size_size == 1
            items.append(rmem(
                addr_size, size_size, RMEM_SOURCE if valid_format else 0,
                1 if size_size else 0,
                memory_id=1 if addr_size == 5 else None,
            ))

    for memory_id, addr, size, capacity in (
        (1, RMEM_SOURCE, 0, 0x110),
        (1, RMEM_SOURCE, 1, 0),
        (1, RMEM_SOURCE, 1, 1),
        (1, RMEM_SOURCE, 2, 1),
        (1, RMEM_SOURCE, 2, 2),
        (1, RMEM_SOURCE, 0x10, 0x10),
        (1, RMEM_SOURCE, 0xFF, 0xFE),
        (1, RMEM_SOURCE, 0xFF, 0xFF),
        (1, RMEM_SOURCE, 0xFF, 0x110),
        (1, RMEM_SOURCE, 0xFF, 0xFFFE),
        (1, 0xFEBE37FF, 1, 0x110),
        (1, 0xFEBE3800, 1, 0x110),
        (1, 0xFEBE503B, 1, 0x110),
        (1, 0xFEBE503C, 1, 0x110),
        (1, 0xFEBE52A7, 1, 0x110),
        (1, 0xFEBE52A8, 1, 0x110),
        (1, 0xFEBFFFFF, 1, 0x110),
        (1, 0xFEBFFFFF, 2, 0x110),
        (1, 0xFEC00000, 1, 0x110),
        (1, 0xFFFFFFFF, 2, 0x110),
        (0, RMEM_SOURCE, 1, 0x110),
        (2, 0xFF200000, 1, 0x110),
        (0xFF, RMEM_SOURCE, 1, 0x110),
    ):
        items.append(rmem(5, 1, addr, size, capacity=capacity, memory_id=memory_id))

    # CanTp TX segmenter tick: primed TxState per state char, live response queue.
    for idx in (0, 2):
        for state in (0xE1, 0xD2, 0xC3, 0xB4, 0xA5, 0x96, 0x87, 0x78):
            for remaining, queue in ((0x10, 0x10), (0x100, 0x100), (1, 0)):
                armed = tx_state(remaining=remaining, transmit_id=0x800, state=state,
                                 block_size=1, spacing=3)
                items.append(Trial(f"tx_tick_{idx}_{state:#x}_{remaining:#x}", TX_TICK, (), (
                                      (CANTP_ENABLE, b"\xAA\x00"),
                                      (CELL_BASE + 0x20 * idx, armed),
                                      (0xFEBE5978, 0xFEBE5A20.to_bytes(4, "little")),
                                      (0xFEBE597C, queue.to_bytes(4, "little")),
                                      (0xFEBE5964, b"\x31"),
                                      (0xFEBE5A20, b"\x62\x22\xf1\x81" + b"\x00" * 12),
                                      # coherent one-node response queue + route index
                                      # (the TX teardown walks both):
                                      (0xFEBE5970, 0xFEBE5984.to_bytes(4, "little")),
                                      (0xFEBE5974, 0xFEBE5984.to_bytes(4, "little")),
                                      (0xFEBE5980, b"\x00\x00"),
                                      (0xFEBE5984, 0xFEBE5970.to_bytes(4, "little")),
                                      (0xFEBE5988, 0xFEBE5A20.to_bytes(4, "little")),
                                      (0xFEBE598C, (0x10).to_bytes(2, "little")),
                                      (0xFEBE5990, b"\x00"),
                                      (0xFEBE59E2, b"\x00\x00"))))
    return items


def dispatcher_primes(slot: int, body: bytes, session: int) -> tuple[tuple[int, bytes], ...]:
    base = SLOT_BUFFERS[slot]
    return (
        (REQUEST_PHASE, b"\x02"),
        (PENDING_SLOT, slot.to_bytes(2, "little")),
        (SLOT_STATE + 0x10 * slot + 4, len(body).to_bytes(4, "little")),
        (base, body),
        *session_primes(session),
        *((addr, b"\x5A") for addr in ADMISSION),
        (ADMISSION_CLEAR, b"\x00"),
    )


def crc32_raw_words(data: bytes, raw_seed: int) -> int:
    """Firmware-visible DCRA1 mode-0 result for complete little-endian words."""
    crc = raw_seed & 0xFFFFFFFF
    for offset in range(0, len(data) & ~3, 4):
        crc ^= int.from_bytes(data[offset:offset + 4], "little")
        for _bit in range(32):
            crc = (crc >> 1) ^ (0xEDB88320 if crc & 1 else 0)
    return crc & 0xFFFFFFFF


def build_dcra1_model(output_dir: Path) -> Path:
    """Build a relocation-free RAM helper for GNU sim's absent DCRA1 MMIO."""
    output_dir.mkdir(parents=True, exist_ok=True)
    source = DCRA1_MODEL_SOURCE.relative_to(REPO_ROOT).as_posix()
    base = rh850_command(output_dir)
    subprocess.run(base + [
        "v850-elf-gcc", "-mv850e3v5", "-mno-app-regs", "-ffreestanding",
        "-fno-builtin", "-Os", "-nostdlib", f"-Wl,-Ttext={DCRA1_MODEL_ENTRY:#x}",
        "-Wl,-e,_dcra1_crc_raw_words_model", "-Wl,--build-id=none",
        f"/src/{source}", "-o", "/out/dcra1-crc-model.elf",
    ], cwd=REPO_ROOT, check=True)
    subprocess.run(base + [
        "v850-elf-objcopy", "-O", "binary", "-j", ".text",
        "/out/dcra1-crc-model.elf", f"/out/{DCRA1_MODEL_NAME}",
    ], cwd=REPO_ROOT, check=True)
    relocations = subprocess.run(base + [
        "v850-elf-readelf", "-r", "/out/dcra1-crc-model.elf",
    ], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout
    symbols = subprocess.run(base + [
        "v850-elf-nm", "-n", "/out/dcra1-crc-model.elf",
    ], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout
    if "There are no relocations in this file." not in relocations:
        raise RuntimeError("DCRA1 simulator model contains relocations")
    entries = [
        int(fields[0], 16)
        for line in symbols.splitlines()
        if len(fields := line.split()) >= 3 and fields[-1] == "_dcra1_crc_raw_words_model"
    ]
    if entries != [DCRA1_MODEL_ENTRY]:
        raise RuntimeError(f"unexpected DCRA1 model entry: {entries}")
    model = output_dir / DCRA1_MODEL_NAME
    if not model.is_file() or not 0 < model.stat().st_size <= 0x1000:
        raise RuntimeError("DCRA1 simulator model does not fit its mapped region")
    return model


def dcra1_model_break_commands() -> list[str]:
    number = len(SINKS) + 2
    return [
        f"break *{0x67060:#x}",
        f"commands {number}",
        "silent",
        f"set $pc={DCRA1_MODEL_ENTRY:#x}",
        "continue",
        "end",
    ]


def verify_dcra1_model(elf: Path, timeout: float) -> dict:
    """Exercise the interception path against the standard reflected CRC vector."""
    payload = b"12345678"
    expected = crc32_raw_words(payload, 0xFFFFFFFF)
    if expected != 0x651F2550:
        raise RuntimeError(f"host DCRA1 oracle drifted: {expected:#x}")
    image = bytearray(RAM_SIZE)
    start = RMEM_SOURCE - RAM_BASE
    image[start:start + len(payload)] = payload
    path = elf.parent / "dcra1-model-selftest.bin"
    path.write_bytes(image)
    marker = f"DCRA1_MODEL=0x{expected:08x}"
    commands = batch_prelude()
    commands.extend((
        f"restore /out/{path.name} binary {RAM_BASE:#x}",
        f"set $r3={STACK_TOP:#x}",
        f"set $r31={SENTINEL:#x}",
        f"set $r6={RMEM_SOURCE:#x}",
        f"set $r7={len(payload)}",
        "set $r8=0xffffffff",
        "set $pc=0x67060",
        "continue",
        'printf "DCRA1_MODEL=0x%08x\\n", $r10',
    ))
    try:
        run_elf(
            root=REPO_ROOT,
            elf_path=elf,
            stop=f"{SENTINEL:#x}",
            memory_regions=SIM_MEMORY_REGIONS,
            gdb_commands=commands,
            expected_output=[marker],
            timeout=timeout,
        )
    finally:
        path.unlink(missing_ok=True)
    return {
        "entry": hex(DCRA1_MODEL_ENTRY),
        "input_hex": payload.hex(),
        "raw_seed": "0xFFFFFFFF",
        "expected_result": f"0x{expected:08X}",
    }


# ------------------------------------------------------------- GDB scripting

def trial_image(trial: Trial, salt: int | None = None) -> bytes:
    """Pattern (salt) or zero fill + lifecycle base primes + trial primes."""
    if salt is None:
        image = bytearray(RAM_SIZE)
    else:
        image = bytearray(_LIFECYCLE_BASES.get(salt, pattern_image(salt)))

    def wr(addr: int, data: bytes) -> None:
        image[addr - RAM_BASE:addr - RAM_BASE + len(data)] = data

    if salt is not None:
        # Lifecycle reconstruction belongs to pattern-fill runs: zero-fill
        # images stay byte-identical to the historical state model so the
        # machinery canaries keep their established meaning.
        # Shared transport reset state used by the TX-tick family.
        for index in range(3):
            wr(CELL_BASE + 0x20 * index, RESET_CELL)
        wr(CELL_BASE + 0x60, b"\x00" * 12)
        wr(0xFEBE59D8, b"\x00" * (0x59ED - 0x59D8))
        wr(0xFEBE59E0, b"\x00\x00")             # pending-dispatch slot
        wr(0xFEBE59E2, b"\x00\x00")             # current dispatch receive-route index
        wr(0xFEBE5960, b"\x00\x00")             # request phase 0 (receiving-capable)
        for slot in range(3):                   # coherent idle rows as boot leaves them
            wr(0xFEBE59F0 + 0x10 * slot, (0xFEBE5651 + 0x100 * slot).to_bytes(4, "little"))
            wr(0xFEBE59F0 + 0x10 * slot + 4, b"\x00\x00")
            wr(0xFEBE59F0 + 0x10 * slot + 8, (0x100).to_bytes(2, "little"))
            wr(0xFEBE59F0 + 0x10 * slot + 0xA, b"\x00\x00")
        # Exact post-reset state from diag_reset_routine_class_state @ 0x8B7B6.
        wr(0xFEBF3B2C, b"\x00" * (0x3BCB - 0x3B2C))
        wr(0xFEBF3B31, b"\x01\x01\xff\x02\x02")
        # BSS + reset_dtc_list_continuation_and_scratch @ 0x8C70C.
        wr(0xFEBF3F18, b"\x00" * (0x4240 - 0x3F18))
        wr(0xFEBF3F20, b"\xff")
        # reset_memory_read_status4598 @ 0x8D4AE plus zeroed selector byte.
        wr(0xFEBF4598, b"\x01\x01\x00\xff\x00")
    for addr, data in trial.primes:
        wr(addr, data)
    return bytes(image)



def trial_script(index: int, trial: Trial, arm_fences: bool = True) -> list[str]:
    commands = [f'restore /out/img-{index:06d}.bin binary {RAM_BASE:#x}']
    # Fences armed after each restore; batch_script deletes exactly the
    # captured numbers (gdb never reuses freed breakpoint numbers).
    # Liveness probes run unarmed: a fence hit must not cut a canary short.
    if arm_fences:
        for fence_number, (addr, _name) in enumerate(FENCES):
            commands += [f"watch *(unsigned char*){addr:#x}", f"set $fence{fence_number} = $bpnum"]
    commands += [f"set $r3={STACK_TOP:#x}", f"set $r31={SENTINEL:#x}",
                 f"set $r5={TP_BASE:#x}", f"set $tp={TP_BASE:#x}"]
    commands.extend(f"set {reg}={value:#x}" for reg, value in trial.regs)
    commands.extend((f"set $pc={trial.entry:#x}", "continue",
                     f"dump binary memory /out/tp-{index:06d}.bin {RAM_BASE:#x} {RAM_BASE + RAM_SIZE:#x}",
                     f'printf "TPR {index} %u\\n", $pc',
                     f"set $pc={SENTINEL:#x}"))
    return commands


def batch_prelude() -> list[str]:
    return [
        f"set $r4={GP:#x}", f"set $r5={TP_BASE:#x}", f"set $tp={TP_BASE:#x}",
        # PMR/syncp thunk neutering (see fuzz_camry_f33_cantp_ingress.py).
        # GDB writes target-endian u16; 0x007f yields bytes 7f 00 = jmp [lp].
        "set {unsigned short}0x6a45e = 0x007f", "set {unsigned short}0x6a4c4 = 0x007f",
        "set {unsigned short}0x6a4c0 = 0x0000", "set {unsigned short}0x6a51e = 0x0000",
        "set {unsigned short}0x701c4 = 0x007f", "set {unsigned short}0x70204 = 0x007f",
        # priority_mask_raise/restore: sim lacks stsr/ldsr PMR; no simulated IRQs
        f"break *{SENTINEL:#x}",
        f"restore /out/{DCRA1_MODEL_NAME} binary {DCRA1_MODEL_ENTRY:#x}",
        *sink_break_commands(),
        *dcra1_model_break_commands(),
        # harmless warmup dispatch (unknown canif id)
        "set {unsigned short}0xFEBE40E4 = 0", "set $r6=0xFFFF", "set $r7=0xFEBE40E0",
        f"set $r3={STACK_TOP:#x}", f"set $r31={SENTINEL:#x}", "set $pc=0x7A57A",
        "continue",
    ]


def prepare_pattern_lifecycle(elf: Path, out: Path, salt: int, timeout: float) -> None:
    """Capture exact Dcm and crypto reset state over one salted marker image."""
    input_path = elf.parent / f"lifecycle-{salt}-input.bin"
    dump_path = elf.parent / f"lifecycle-{salt}-dump.bin"
    log_path = out / f"lifecycle-{salt}.txt"
    marker = f"LIFECYCLE_{salt}_DONE"
    input_path.write_bytes(pattern_image(salt))
    commands = batch_prelude()
    commands.extend((
        f"restore /out/{input_path.name} binary {RAM_BASE:#x}",
        # dcm_get_shared_response_buffer_and_connection_limit indexes this
        # route while the response queue is reset.
        "set {unsigned short}0xFEBE59E2 = 0",
        f"set $r3={STACK_TOP:#x}",
        f"set $r31={SENTINEL:#x}",
        "set $pc=0x9887C",  # full Dcm timer/event/callback/session/queue init chain
        "continue",
        f"set $r3={STACK_TOP:#x}",
        f"set $r31={SENTINEL:#x}",
        "set $pc=0x8E74E",  # reset four COM generation/tracking arrays
        "continue",
        f"set $r3={STACK_TOP:#x}",
        f"set $r31={SENTINEL:#x}",
        "set $pc=0x69064",  # crypto-bank work and test-material initializer
        "continue",
        f"dump binary memory /out/{dump_path.name} {RAM_BASE:#x} {RAM_BASE + RAM_SIZE:#x}",
        f'printf "{marker}\\n"',
    ))
    try:
        run_elf(
            root=REPO_ROOT,
            elf_path=elf,
            stop=f"{SENTINEL:#x}",
            memory_regions=SIM_MEMORY_REGIONS,
            gdb_commands=commands,
            expected_output=[marker],
            timeout=timeout,
            output_path=log_path,
        )
        lifecycle = dump_path.read_bytes()
        if len(lifecycle) != RAM_SIZE:
            raise SystemExit(
                f"lifecycle dump has {len(lifecycle):#x} bytes, expected {RAM_SIZE:#x}"
            )
        _LIFECYCLE_BASES[salt] = lifecycle
        log_path.unlink(missing_ok=True)
    finally:
        input_path.unlink(missing_ok=True)
        dump_path.unlink(missing_ok=True)


def batch_script(
    batch: list[tuple[int, Trial]],
    extra_prelude: tuple[str, ...] = (),
) -> list[str]:
    commands = batch_prelude()
    commands.extend(extra_prelude)
    for position, (index, trial) in enumerate(batch):
        if position:
            commands.append("delete " + " ".join(f"$fence{i}" for i in range(len(FENCES))))
        commands.extend(trial_script(index, trial))
    commands.append(f'printf "TP_END={batch[-1][0]}\\n"')
    return commands


def run_batch(
    elf: Path,
    batch: list[tuple[int, Trial]],
    out: Path,
    timeout: float,
    label: str,
    salt: int | None = None,
    extra_prelude: tuple[str, ...] = (),
) -> tuple[str, dict[int, bytes]]:
    """Run one batch; retry only unfinished trials and fail fast if a retry wedges."""
    dump_dir = elf.parent  # mounted rw at /out inside the container
    images = {index: trial_image(trial, salt) for index, trial in batch}
    for index, image in images.items():
        (dump_dir / f"img-{index:06d}.bin").write_bytes(image)
    script = batch_script(batch, extra_prelude)
    marker = f"TP_END={batch[-1][0]}"
    batch_log = out / f"{label}.txt"
    try:
        output = run_elf(root=REPO_ROOT, elf_path=elf, stop=f"{SENTINEL:#x}",
                         memory_regions=SIM_MEMORY_REGIONS, gdb_commands=script,
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
                                     memory_regions=SIM_MEMORY_REGIONS,
                                     gdb_commands=batch_script([(index, trial)], extra_prelude),
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


def collect(
    output: str,
    dump_dir: Path,
    images: dict[int, bytes],
    keep: Path | None = None,
    pattern: bool = False,
    keep_indexes: set[int] | None = None,
    keep_dumps: dict[int, bytes] | None = None,
) -> tuple[list[dict], int, dict[int, Counter]]:
    failures: list[dict] = []
    seen = 0
    reported: set[int] = set()
    sinks = attribute_sinks(output)
    marker = pattern_image()
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
        runs = outside_runs(dump, images[index], ENVELOPE)
        magics = magic_hits(dump)
        propagated = pattern_propagation(dump, DCM_CONSUMER_RANGES) if pattern else []
        bad = []
        if pattern:
            # lenient row sanity: direct-entry trials only drive len/rem fields
            for slot in range(3):
                row = 0xFEBE59F0 + 0x10 * slot - RAM_BASE
                if dump[row:row + 8] == marker[row:row + 8]:
                    continue
                length = int.from_bytes(dump[row + 4:row + 6], "little")
                remaining = int.from_bytes(dump[row + 8:row + 10], "little")
                if length > 0x100 or remaining > 0x100:
                    bad.append(f"slot{slot}:len={length:#x} rem={remaining:#x}")
        if runs or magics or pc != SENTINEL or propagated or bad:
            record["outside_runs"] = " ".join(f"{lo:x}-{hi:x}" for lo, hi in runs[:24])
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



# --------------------------------------------------------------------- main

def verify_liveness(elf: Path, timeout: float) -> None:
    """Prove that every entry family executes its intended live path."""
    probes = (
        (999996, Trial("live_disp", DISPATCH_TASK, (),
                       dispatcher_primes(0, b"\x10\x03", 1)),
         'printf "LIVE_DISP %02x %02x\\n", *(unsigned char*)0xFEBE5A20, *(unsigned char*)0xFEBE5A21',
         "LIVE_DISP 50 03"),
        (999997, Trial("live_wdbi", WDBI_SERVICE, (("$r6", 0), ("$r7", CTX_BUF)),
                       session_primes(1)
                       + ((REQ_BUF, b"\x20\x12\x01"),)
                       + ctx_primes(3, 0x2E)),
         'printf "LIVE_WDBI %02x\\n", *(unsigned char*)0xFEBEB18F',
         "LIVE_WDBI 5a"),
        (999998, Trial("live_rid", ROUTINE_SERVICE, (("$r6", 0), ("$r7", CTX_BUF)),
                       session_primes(1)
                       + ((REQ_BUF, b"\x01\x10\x0f"),)
                       + ctx_primes(3, 0x31)),
         'printf "LIVE_RID %02x %02x\\n", *(unsigned char*)0xFEBE509B, *(unsigned char*)0xFEBE509C',
         "LIVE_RID 01 11"),
        (999999, Trial("live_worker", WDBI_WORKER,
                       (("$r6", 10), ("$r7", REQ_BUF), ("$r8", 0))),
         'printf "LIVE_WORKER %02x %02x\\n", *(unsigned char*)0xFEBF3B22, *(unsigned char*)0xFEBF3B23',
         "LIVE_WORKER 01 01"),
        (999995, Trial("live_crypto", CRYPTO_COLLECT, (),
                       crypto_primes(1, 1, bytes(range(0x10, 0x20)),
                                     bytes(range(0x20, 0x30)),
                                     ready_to_commit=True)),
         'printf "LIVE_CRYPTO %02x %02x %02x %02x %02x\\n", *(unsigned char*)0xFEBE50A2, *(unsigned char*)0xFEBE50A4, *(unsigned char*)0xFEBE50A5, *(unsigned char*)0xFEBE5186, *(unsigned char*)0xFEBE5195',
         "LIVE_CRYPTO 1f 01 01 10 1f"),
        (999994, Trial("live_rdbi", READ_DID_SERVICE,
                       (("$r6", 0), ("$r7", CTX_BUF)),
                       session_primes(1)
                       + ((REQ_BUF, b"\x01\x00"),)
                       + ctx_primes(2, 0x22)),
         'printf "LIVE_RDBI %02x %02x %02x %02x %02x\\n", *(unsigned char*)0xFEBE5A20, *(unsigned char*)0xFEBE5A21, *(unsigned char*)0xFEBE5A22, *(unsigned char*)0xFEBE5A23, *(unsigned char*)0xFEBE5A24',
         "LIVE_RDBI 01 00 e8 a1 40"),
        (999993, Trial("live_rmem", READ_MEM_SERVICE,
                       (("$r6", 0), ("$r7", CTX_BUF)),
                       session_primes(3)
                       + ((REQ_BUF, b"\x15\x01\xfe\xbe\x70\x00\x01"),
                          (RMEM_SOURCE, b"\xde"),
                          (0xFEBF4598, b"\x01\x01\x00\xff\x00"))
                       + ctx_primes(7, 0x23)),
         'printf "LIVE_RMEM %02x\\n", *(unsigned char*)0xFEBE5A20',
         "LIVE_RMEM de"),
    )
    dump_dir = elf.parent
    script = batch_prelude()
    expected = []
    for index, probe, observer, marker in probes:
        (dump_dir / f"img-{index:06d}.bin").write_bytes(trial_image(probe))
        script.extend(trial_script(index, probe, arm_fences=False))
        script.append(observer)
        expected.append(marker)
    script.append('printf "LIVE_DONE\\n"')
    expected.append("LIVE_DONE")
    run_elf(root=REPO_ROOT, elf_path=elf, stop=f"{SENTINEL:#x}",
            memory_regions=SIM_MEMORY_REGIONS, gdb_commands=script,
            expected_output=expected, timeout=timeout)
    for index, _probe, _observer, _marker in probes:
        (dump_dir / f"tp-{index:06d}.bin").unlink(missing_ok=True)
        (dump_dir / f"img-{index:06d}.bin").unlink(missing_ok=True)


def response_poison(salt: int) -> bytes:
    """Object-local poison; unlike whole-RAM fill it cannot corrupt control state."""
    start = RESP_BUF - RAM_BASE
    return pattern_image(salt)[start:start + 0x110]


def publication_rows() -> list[tuple[int, int, int]]:
    """Return the exact Camry DID, declared length, and active reader table."""
    image = IMAGE.read_bytes()
    rows = []
    for index in range(242):
        base = 0x2927C + index * 16
        rows.append((
            int.from_bytes(image[base:base + 2], "little"),
            int.from_bytes(image[base + 2:base + 4], "little"),
            int.from_bytes(image[base + 4:base + 8], "little"),
        ))
    return rows


def response_extent_trial(did: int, session: int, salt: int) -> Trial:
    request = bytes((0x22, did >> 8, did & 0xFF))
    return Trial(
        f"extent_rdbi_{did:04x}_s{session}",
        DISPATCH_TASK,
        (),
        dispatcher_primes(0, request, session)
        + ((RESP_BUF, response_poison(salt)),),
    )


def response_extent_observation(
    index: int,
    did: int,
    session: int,
    pc: int,
    image: bytes,
    dump: bytes,
) -> dict:
    context = ACTIVE_DCM_CONTEXT - RAM_BASE
    response = RESP_BUF - RAM_BASE
    length = int.from_bytes(dump[context + 12:context + 16], "little")
    capacity = int.from_bytes(dump[context + 20:context + 24], "little")
    bounded = min(length, 0x110)
    unchanged = [
        offset
        for offset in range(bounded)
        if dump[response + offset] == image[response + offset]
    ]
    body = dump[response:response + min(length, 8)]
    if pc == CRC_DCRA1_STORE and not length:
        kind = "peripheral-blocked"
    elif not length:
        kind = "no-response"
    elif length < 3:
        kind = "incomplete"
    elif body[0] == 0x62 and body[1:3] == bytes((did >> 8, did & 0xFF)):
        kind = "positive"
    elif body[0] == 0x7F and body[1] == 0x22:
        kind = "negative"
    else:
        kind = "malformed"
    return {
        "index": index,
        "did": f"0x{did:04X}",
        "session": session,
        "pc": pc,
        "kind": kind,
        "response_length": length,
        "response_capacity_after_sid": capacity,
        "prefix": body.hex(),
        "unchanged_offsets": unchanged if kind in ("positive", "negative", "malformed") else [],
    }


def collect_response_extent_batch(
    output: str,
    images: dict[int, bytes],
    metadata: dict[int, tuple[int, int]],
    dump_dir: Path,
) -> list[dict]:
    pcs = {int(match.group(1)): int(match.group(2)) for match in RX_LINE.finditer(output)}
    records = []
    for index, image in images.items():
        dump_path = dump_dir / f"tp-{index:06d}.bin"
        img_path = dump_dir / f"img-{index:06d}.bin"
        if index not in pcs or not dump_path.is_file():
            raise RuntimeError(f"response-extent trial {index} has no complete dump")
        did, session = metadata[index]
        dump = dump_path.read_bytes()
        records.append(response_extent_observation(
            index, did, session, pcs[index], image, dump,
        ))
        dump_path.unlink()
        img_path.unlink(missing_ok=True)
    return records


def verify_response_extent_oracle(elf: Path, out: Path, timeout: float) -> dict:
    """Stock producer must initialize fully; a sim-only no-write seed must fire."""
    did = 0x2030
    row = next(row for row in publication_rows() if row[0] == did)
    declared, reader = row[1], row[2]
    if declared != 16:
        raise RuntimeError(f"unexpected DID 2030 width: {declared}")
    stock_index = 980000
    stock_trial = response_extent_trial(did, 1, 0xA11CE)
    stock_output, stock_images = run_batch(
        elf, [(stock_index, stock_trial)], out, timeout,
        "extent-selftest-stock", salt=None,
    )
    stock = collect_response_extent_batch(
        stock_output, stock_images, {stock_index: (did, 1)}, elf.parent,
    )[0]
    if (stock["pc"] != SENTINEL or stock["kind"] != "positive"
            or stock["response_length"] != declared + 3
            or stock["unchanged_offsets"]):
        raise RuntimeError(f"stock response-extent seed is not fully initialized: {stock}")

    seeded_index = 980001
    seeded_trial = response_extent_trial(did, 1, 0xA11CE)
    seeded_output, seeded_images = run_batch(
        elf, [(seeded_index, seeded_trial)], out, timeout,
        "extent-selftest-seeded", salt=None,
        extra_prelude=(
            f"set {{unsigned short}}{reader:#x} = 0x5200",
            f"set {{unsigned short}}{reader + 2:#x} = 0x007f",
        ),
    )
    seeded = collect_response_extent_batch(
        seeded_output, seeded_images, {seeded_index: (did, 1)}, elf.parent,
    )[0]
    expected_unwritten = list(range(3, declared + 3))
    if (seeded["pc"] != SENTINEL or seeded["kind"] != "positive"
            or seeded["response_length"] != declared + 3
            or seeded["unchanged_offsets"] != expected_unwritten):
        raise RuntimeError(f"response-extent oracle missed seeded no-write producer: {seeded}")
    return {
        "did": "0x2030",
        "stock_unwritten": stock["unchanged_offsets"],
        "seeded_unwritten": seeded["unchanged_offsets"],
        "seed_patch": [
            f"{reader:#x}: mov 0,r10",
            f"{reader + 2:#x}: jmp lp",
        ],
    }


def audit_response_extents(
    elf: Path,
    out: Path,
    batch_size: int,
    timeout: float,
    jobs: int,
) -> dict:
    """Check transport-visible RDBI bytes against object-local poison twice."""
    selftest = verify_response_extent_oracle(elf, out, timeout)
    dids = sorted({did for did, _declared, _reader in publication_rows()})
    first: list[tuple[int, Trial]] = []
    metadata: dict[int, tuple[int, int]] = {}
    for ordinal, (session, did) in enumerate(
        (session, did) for session in (1, 2, 3) for did in dids
    ):
        index = 700000 + ordinal
        first.append((index, response_extent_trial(did, session, 0xA11CE)))
        metadata[index] = (did, session)
    groups = [
        (f"extent-a-{number:04d}", first[offset:offset + batch_size])
        for number, offset in enumerate(range(0, len(first), batch_size))
    ]
    records: list[dict] = []
    worker = lambda item: run_batch(
        elf, item[1], out, timeout, item[0], salt=None,
    )
    for (_label, _group), (output, images) in parallel_results(groups, worker, jobs):
        records.extend(collect_response_extent_batch(
            output, images, metadata, elf.parent,
        ))

    candidates = [
        record for record in records
        if record["kind"] != "peripheral-blocked"
        and (
            record["pc"] != SENTINEL
            or record["response_length"] > 0x110
            or record["unchanged_offsets"]
            or record["kind"] == "malformed"
        )
    ]
    alternate: dict[tuple[str, int], dict] = {}
    if candidates:
        second: list[tuple[int, Trial]] = []
        second_metadata: dict[int, tuple[int, int]] = {}
        for ordinal, record in enumerate(candidates):
            did = int(record["did"], 16)
            session = record["session"]
            index = 800000 + ordinal
            second.append((index, response_extent_trial(did, session, 0xB22DF)))
            second_metadata[index] = (did, session)
        second_groups = [
            (f"extent-b-{number:04d}", second[offset:offset + batch_size])
            for number, offset in enumerate(range(0, len(second), batch_size))
        ]
        second_worker = lambda item: run_batch(
            elf, item[1], out, timeout, item[0], salt=None,
        )
        for (_label, _group), (output, images) in parallel_results(
            second_groups, second_worker, jobs,
        ):
            for record in collect_response_extent_batch(
                output, images, second_metadata, elf.parent,
            ):
                alternate[(record["did"], record["session"])] = record

    findings = []
    collisions = 0
    for record in candidates:
        other = alternate[(record["did"], record["session"])]
        common = sorted(set(record["unchanged_offsets"])
                        & set(other["unchanged_offsets"]))
        behavior_changed = (
            record["kind"], record["response_length"], record["pc"]
        ) != (
            other["kind"], other["response_length"], other["pc"]
        )
        if common or behavior_changed or record["pc"] != SENTINEL:
            findings.append({
                **record,
                "confirmed_unwritten_offsets": common,
                "alternate_kind": other["kind"],
                "alternate_response_length": other["response_length"],
                "poison_changed_behavior": behavior_changed,
            })
        else:
            collisions += 1
    kinds = Counter(record["kind"] for record in records)
    return {
        "schema": "camry-f33-rdbi-response-extent-v1",
        "trials": len(records),
        "sessions": [1, 2, 3],
        "unique_dids": len(dids),
        "kinds": dict(kinds),
        "first_pass_candidates": len(candidates),
        "poison_value_collisions": collisions,
        "findings": findings,
        "peripheral_blocked": [
            {
                "did": record["did"],
                "session": record["session"],
                "pc": hex(record["pc"]),
            }
            for record in records
            if record["kind"] == "peripheral-blocked"
        ],
        "selftest": selftest,
    }


def request_tail_guard_trial(trial: Trial) -> tuple[Trial, int] | None:
    """Move an exact request object to the last mapped RAM byte."""
    if trial.entry not in (
        WDBI_SERVICE, ROUTINE_SERVICE, READ_DID_SERVICE, READ_MEM_SERVICE,
    ):
        return None
    context_data = next(
        (data for address, data in trial.primes if address == CTX_BUF),
        None,
    )
    request_data = next(
        (data for address, data in trial.primes if address == REQ_BUF),
        None,
    )
    if context_data is None or request_data is None or len(context_data) != 28:
        return None
    request_length = int.from_bytes(context_data[4:8], "little")
    if int.from_bytes(context_data[0:4], "little") != REQ_BUF:
        return None
    if len(request_data) != request_length or request_length > 0x100:
        return None
    guarded_address = RAM_BASE + RAM_SIZE - request_length
    guarded_context = bytearray(context_data)
    guarded_context[0:4] = guarded_address.to_bytes(4, "little")
    primes = []
    for address, data in trial.primes:
        if address == REQ_BUF:
            primes.append((guarded_address, data))
        elif address == CTX_BUF:
            primes.append((CTX_BUF, bytes(guarded_context)))
        else:
            primes.append((address, data))
    return Trial(
        f"tail_guard_{trial.family}",
        trial.entry,
        trial.regs,
        tuple(primes),
    ), request_length


def collect_request_tail_batch(
    output: str,
    images: dict[int, bytes],
    metadata: dict[int, tuple[Trial, int]],
    dump_dir: Path,
) -> list[dict]:
    pcs = {int(match.group(1)): int(match.group(2)) for match in RX_LINE.finditer(output)}
    records = []
    for index in images:
        dump_path = dump_dir / f"tp-{index:06d}.bin"
        img_path = dump_dir / f"img-{index:06d}.bin"
        if index not in pcs or not dump_path.is_file():
            raise RuntimeError(f"request-tail trial {index} has no complete dump")
        trial, request_length = metadata[index]
        record = {
            "index": index,
            "family": trial.family,
            "entry": hex(trial.entry),
            "request_length": request_length,
            "pc": pcs[index],
        }
        records.append(record)
        dump_path.unlink()
        img_path.unlink(missing_ok=True)
    return records


def verify_request_tail_oracle(elf: Path, out: Path, timeout: float) -> dict:
    """A known 16-byte writer must fault when its destination is one-past RAM."""
    reader = next(row[2] for row in publication_rows() if row[0] == 0x2030)
    index = 990000
    probe = Trial(
        "tail_guard_selftest",
        reader,
        (("$r6", RAM_BASE + RAM_SIZE),),
    )
    output, images = run_batch(
        elf, [(index, probe)], out, timeout,
        "guard-selftest", salt=None,
    )
    record = collect_request_tail_batch(
        output, images, {index: (probe, 0)}, elf.parent,
    )[0]
    if record["pc"] == SENTINEL:
        raise RuntimeError("request-tail oracle missed a seeded unmapped write")
    return {
        "entry": hex(reader),
        "fault_pc": hex(record["pc"]),
        "destination": hex(RAM_BASE + RAM_SIZE),
    }


def audit_request_tails(
    elf: Path,
    out: Path,
    trials: list[Trial],
    batch_size: int,
    timeout: float,
    jobs: int,
) -> dict:
    """Catch parser over-reads by ending each exact request at mapped RAM."""
    selftest = verify_request_tail_oracle(elf, out, timeout)
    guarded: list[tuple[int, Trial]] = []
    metadata: dict[int, tuple[Trial, int]] = {}
    for trial in trials:
        transformed = request_tail_guard_trial(trial)
        if transformed is None:
            continue
        guarded_trial, request_length = transformed
        index = 500000 + len(guarded)
        guarded.append((index, guarded_trial))
        metadata[index] = (guarded_trial, request_length)
    groups = [
        (f"guard-{number:04d}", guarded[offset:offset + batch_size])
        for number, offset in enumerate(range(0, len(guarded), batch_size))
    ]
    records: list[dict] = []
    worker = lambda item: run_batch(
        elf, item[1], out, timeout, item[0], salt=None,
    )
    for (_label, _group), (output, images) in parallel_results(groups, worker, jobs):
        records.extend(collect_request_tail_batch(
            output, images, metadata, elf.parent,
        ))
    peripheral = [
        record for record in records if record["pc"] == CRC_DCRA1_STORE
    ]
    findings = [
        record for record in records
        if record["pc"] not in (SENTINEL, CRC_DCRA1_STORE)
    ]
    return {
        "schema": "camry-f33-request-tail-guard-v1",
        "trials": len(records),
        "clean_returns": sum(record["pc"] == SENTINEL for record in records),
        "peripheral_blocked": peripheral,
        "findings": findings,
        "selftest": selftest,
    }


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
    for pattern in ("batch-*.txt", "div-*.txt", "extent-*.txt", "guard-*.txt",
                    "lifecycle-*.txt"):
        for stale in out.glob(pattern):
            stale.unlink()
    (out / "summary.json").unlink(missing_ok=True)
    keep = out / "findings"
    keep.mkdir(exist_ok=True)
    for stale in keep.glob("tp-*.bin"):
        stale.unlink()
    sim_out = out / "linked-image"
    sim_out.mkdir(exist_ok=True)
    for pattern in ("tp-*.bin", "img-*.bin", "lifecycle-*.bin"):
        for stale in sim_out.glob(pattern):
            stale.unlink()

    _output, elf = run(root=REPO_ROOT, image_path=IMAGE, entry=0x7A57A, stop=f"{SENTINEL:#x}",
                       memory_regions=SIM_MEMORY_REGIONS,
                       gdb_commands=[f"set $r4={GP:#x}", f"set $r3={STACK_TOP:#x}",
                                     f"set $r31={SENTINEL:#x}", f"set $tp={TP_BASE:#x}",
                                     f"set $r5={TP_BASE:#x}", "set $r7=0",
                                     f"break *{SENTINEL:#x}", "continue"],
                       expected_output=["RH850_EXECUTION_VERIFIED"], timeout=timeout,
                       output_dir=sim_out)
    assert elf is not None
    build_dcra1_model(sim_out)
    dcra1_model = verify_dcra1_model(elf, timeout)
    _LIFECYCLE_BASES.clear()
    if pattern_fill:
        prepare_pattern_lifecycle(elf, out, 0, timeout)
    if divergence_step:
        prepare_pattern_lifecycle(elf, out, 1, timeout)
    # Liveness canaries run under the zero-fill state model; pattern-fill
    # trials are behavior probes and their fill-dependent faults are findings.
    verify_liveness(elf, timeout)
    response_extent = audit_response_extents(
        elf, out, batch_size, timeout, jobs,
    )
    print(
        "response extent "
        f"{response_extent['trials']} trials "
        f"({len(response_extent['findings'])} findings)",
        flush=True,
    )


    trials = generate(seed, random_each)
    request_tail = audit_request_tails(
        elf, out, trials, batch_size, timeout, jobs,
    )
    print(
        "request tail "
        f"{request_tail['trials']} trials "
        f"({len(request_tail['findings'])} findings)",
        flush=True,
    )

    div_set = set(range(0, len(trials), divergence_step)) if divergence_step else set()
    if div_set:
        verify_fill_divergence()
    dump_store: dict[int, bytes] = {}
    failures: list[dict] = []
    families: Counter[str] = Counter()
    sink_totals: Counter[str] = Counter()
    sink_families: dict[str, Counter[str]] = {name: Counter() for _addr, name in SINKS}
    observed = 0
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
        batch_failures, seen, sinks = collect(output, elf.parent, images, keep=keep,
                                              pattern=pattern_fill,
                                              keep_indexes=div_set or None,
                                              keep_dumps=dump_store if div_set else None)
        for idx, hits in sinks.items():
            for name, count in hits.items():
                sink_totals[name] += count
                sink_families[name][trials[idx].family] += count
        observed += seen
        for record in batch_failures:
            trial = trials[record["index"]]
            record["family"] = trial.family
            record["entry"] = hex(trial.entry)
            record["regs"] = {r: hex(v) for r, v in trial.regs}
            body = b"".join(data for _a, data in trial.primes if _a in (REQ_BUF, *SLOT_BUFFERS))
            record["body"] = body[:32].hex()
            families[trial.family] += 1
        failures.extend(batch_failures)
        completed += len(group)
        print(f"simulated {completed}/{len(trials)}"
              f" ({len(batch_failures)} findings)", flush=True)

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
                output, elf.parent, images, keep=keep, keep_dumps=alt_dump_store,
                pattern=False,
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
                    ENVELOPE,
                    blocked=DIVERGENCE_DEAD_RANGES,
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
    for leftover in elf.parent.glob("tp-*.bin"):
        leftover.unlink(missing_ok=True)
    for leftover in elf.parent.glob("img-*.bin"):
        leftover.unlink(missing_ok=True)
    summary = {
        "schema": "camry-f33-dcm-handlers-original-rh850-fuzz-v5",
        "image_sha256": IMAGE_SHA256,
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
        "response_extent_trials": response_extent["trials"],
        "response_extent_findings": len(response_extent["findings"]),
        "response_extent": response_extent,
        "dcra1_model": dcra1_model,
        "request_tail_trials": request_tail["trials"],
        "request_tail_findings": len(request_tail["findings"]),
        "request_tail": request_tail,
        "by_family": dict(families),
        "sink_hits": {name: {"total": sink_totals[name],
                             "families": dict(sink_families[name])}
                      for _addr, name in SINKS},
        "missing_required_sinks": missing_required_sinks,
        "findings": failures,
        "divergence": divergence,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if missing_required_sinks:
        raise SystemExit(f"required sinks not reached: {', '.join(missing_required_sinks)}")
    return summary



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0xD17C)
    parser.add_argument("--random-each", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--jobs", type=int, default=4,
                        help="concurrent independent simulator batches")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--fill", choices=("pattern", "zero"), default="pattern",
                        help="RAM fill outside primes: address-derived pattern or zeros")
    parser.add_argument("--divergence-step", type=int, default=0,
                        help="re-run every Nth trial with a second pattern fill")
    parser.add_argument("--out", type=Path,
                        default=REPO_ROOT / "build/out/targets/camry-8965F3307000/dcm-handlers-fuzz")
    args = parser.parse_args()
    if not args.out.resolve().is_relative_to(REPO_ROOT / "build/out"):
        raise SystemExit("fuzz outputs must live under build/out/")
    result = fuzz(args.out, args.seed, args.random_each, args.batch_size, args.timeout,
                  jobs=args.jobs, pattern_fill=args.fill == "pattern",
                  divergence_step=args.divergence_step)
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("findings", "divergence",
                                   "response_extent", "request_tail")}, indent=2))
    return 0 if (
        result["failures"] == 0
        and result["divergence_findings"] == 0
        and result["response_extent_findings"] == 0
        and result["request_tail_findings"] == 0
    ) else 1



if __name__ == "__main__":
    raise SystemExit(main())
