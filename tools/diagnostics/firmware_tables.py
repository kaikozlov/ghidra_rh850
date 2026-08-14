#!/usr/bin/env python3
"""Extract diagnostic table structures from the raw Sienna CodeFlash binary.

This module reads diagnostic tables directly from firmware bytes — no Ghidra
required.  It is the firmware-side input to the correlation engine
(``correlate_vocabulary.py``) and the verification suite.

Every address and constant here must match ``AnnotateApplicationDiagnostics.java``
and the raw-firmware tests in ``tests/``.  If those change, update this file too.

Record layouts (all little-endian, struct codes in parentheses):

DID record (16 bytes, ``<HHIII``):
    [0:2]  DID identifier
    [2:4]  response-size/attribute field (not access flags)
    [4:8]  read callback address (0 = none)
    [8:12] extra pointer 1 (source record / config address)
    [12:16] extra pointer 2

UDS service object (24 bytes, ``<IIIIBBBBB3x``):
    [0:4]   direct service callback (0 = subfunction-table driven/null-direct)
    [4:8]   security-allow-list pointer
    [8:12]  session-allow-list pointer
    [12:16] subfunction-table pointer
    [16]    SID
    [17]    subfunction-routing mode/attribute
    [18]    security-allow-list length
    [19]    session-allow-list length
    [20]    subfunction count

WDBI callback record (12 bytes, ``<HHII``):
    [0:2]  DID
    [2:4]  reserved/flags
    [4:8]  start callback
    [8:12] result callback

RoutineControl descriptor (8 bytes, ``<HBBI``):
    [0:2] RID
    [2]   policy/index byte
    [3]   enable byte
    [4:8] descriptor/config pointer

Usage::

    from firmware_tables import extract_all
    tables = extract_all()  # reads firmware/RH850_P1M-E_CodeFlash.bin
    for did in tables["dids"]:
        print(f"DID 0x{did.identifier:04X} callback 0x{did.callback:05X}")
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEFLASH_PATH = REPO_ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin"

# Table locations — must match AnnotateApplicationDiagnostics.java and tests/.
DID_TABLE_BASE = 0x2941C
DID_TABLE_COUNT = 0xF2  # 242

# Subset of DID records with known application semantics (annotated in Java).
APP_DID_RECORDS_BASE = 0x2A30C  # F181, F186, F18C

SERVICE_TABLE_BASE = 0x25E28
SERVICE_TABLE_COUNT = 17
EXTRA_SERVICE_TABLE_BASE = 0x25FC0  # 6 secondary-endpoint records
EXTRA_SERVICE_COUNT = 6

WDBI_CALLBACK_TABLE_BASE = 0x25768
WDBI_CALLBACK_TABLE_COUNT = 13

ROUTINE_CONTROL_TABLE_BASE = 0x26AEC
ROUTINE_CONTROL_TABLE_COUNT = 0x13  # 19


# ── Struct definitions ────────────────────────────────────────────────────────

DID_RECORD = struct.Struct("<HHIII")
SERVICE_RECORD = struct.Struct("<IIIIBBBBB3x")
WDBI_CALLBACK_RECORD = struct.Struct("<HHII")
ROUTINE_CONTROL_RECORD = struct.Struct("<HBBI")


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class DidEntry:
    """One DID record from the firmware table."""
    identifier: int
    response_size_or_attribute: int
    callback: int
    extra1: int
    extra2: int
    table_index: int


    @property
    def has_callback(self) -> bool:
        return self.callback != 0


@dataclass
class ServiceEntry:
    """One UDS service record."""
    session_list_ptr: int
    subfunc_table_ptr: int
    sid: int
    subfunction_mode: int
    session_count: int
    security_count: int
    subfunction_count: int
    callback: int
    security_list_ptr: int
    sessions: list[int]
    table_index: int


@dataclass
class WdbiCallbackEntry:
    """One active SID-0x2E WDBI DID callback record."""
    identifier: int
    flags: int
    start_callback: int
    result_callback: int
    table_index: int


@dataclass
class RoutineControlEntry:
    """One SID-0x31 RoutineControl RID descriptor."""
    identifier: int
    policy_index: int
    enable: int
    extra: int
    table_index: int


@dataclass
class FirmwareTables:
    """All diagnostic tables extracted from the firmware."""
    dids: list[DidEntry] = field(default_factory=list)
    services: list[ServiceEntry] = field(default_factory=list)
    wdbi_callbacks: list[WdbiCallbackEntry] = field(default_factory=list)
    routine_control: list[RoutineControlEntry] = field(default_factory=list)

    @property
    def did_by_id(self) -> dict[int, DidEntry]:
        return {d.identifier: d for d in self.dids}

    @property
    def did_callbacks(self) -> dict[int, int]:
        """Map callback address -> DID identifier (for reverse lookup)."""
        return {d.callback: d.identifier for d in self.dids if d.has_callback}

    @property
    def wdbi_by_did(self) -> dict[int, WdbiCallbackEntry]:
        return {r.identifier: r for r in self.wdbi_callbacks}

    @property
    def routine_control_by_rid(self) -> dict[int, RoutineControlEntry]:
        return {r.identifier: r for r in self.routine_control}

    @property
    def service_by_sid(self) -> dict[int, ServiceEntry]:
        return {s.sid: s for s in self.services}


# ── Extractors ────────────────────────────────────────────────────────────────

def extract_dids(cf: bytes | None = None) -> list[DidEntry]:
    """Extract all 242 DID records from the application DID table."""
    if cf is None:
        cf = CODEFLASH_PATH.read_bytes()
    entries = []
    for i in range(DID_TABLE_COUNT):
        offset = DID_TABLE_BASE + i * DID_RECORD.size
        did, attribute, callback, extra1, extra2 = DID_RECORD.unpack_from(cf, offset)
        entries.append(DidEntry(
            identifier=did, response_size_or_attribute=attribute,
            callback=callback,
            extra1=extra1, extra2=extra2, table_index=i,
        ))
    return entries


def extract_services(cf: bytes | None = None) -> list[ServiceEntry]:
    """Extract all 23 UDS service records (17 primary + 6 extra)."""
    if cf is None:
        cf = CODEFLASH_PATH.read_bytes()
    entries = []

    def decode(row: tuple[int, ...], table_index: int) -> ServiceEntry:
        callback, security_ptr, session_ptr, subfunc_ptr, sid, mode, security_count, session_count, subfunction_count = row
        if session_ptr + session_count > len(cf):
            raise ValueError(
                f"service 0x{sid:02X} session list extends past firmware"
            )
        sessions = (
            list(cf[session_ptr:session_ptr + session_count])
            if session_ptr and session_count else []
        )
        return ServiceEntry(
            session_list_ptr=session_ptr,
            subfunc_table_ptr=subfunc_ptr,
            sid=sid,
            subfunction_mode=mode,
            security_count=security_count,
            session_count=session_count,
            subfunction_count=subfunction_count,
            callback=callback,
            security_list_ptr=security_ptr,
            sessions=sessions,
            table_index=table_index,
        )

    for i in range(SERVICE_TABLE_COUNT):
        offset = SERVICE_TABLE_BASE + i * SERVICE_RECORD.size
        row = SERVICE_RECORD.unpack_from(cf, offset)
        entries.append(decode(row, i))
    for i in range(EXTRA_SERVICE_COUNT):
        offset = EXTRA_SERVICE_TABLE_BASE + i * SERVICE_RECORD.size
        row = SERVICE_RECORD.unpack_from(cf, offset)
        entries.append(decode(row, SERVICE_TABLE_COUNT + i))
    return entries


def extract_wdbi_callbacks(cf: bytes | None = None) -> list[WdbiCallbackEntry]:
    """Extract the 13 active lower SID-0x2E WDBI callback records."""
    if cf is None:
        cf = CODEFLASH_PATH.read_bytes()
    entries = []
    for i in range(WDBI_CALLBACK_TABLE_COUNT):
        offset = WDBI_CALLBACK_TABLE_BASE + i * WDBI_CALLBACK_RECORD.size
        did, flags, start_cb, result_cb = WDBI_CALLBACK_RECORD.unpack_from(cf, offset)
        entries.append(WdbiCallbackEntry(
            identifier=did, flags=flags, start_callback=start_cb,
            result_callback=result_cb, table_index=i,
        ))
    return entries


def extract_routine_control(cf: bytes | None = None) -> list[RoutineControlEntry]:
    """Extract all 19 SID-0x31 RoutineControl RID descriptors."""
    if cf is None:
        cf = CODEFLASH_PATH.read_bytes()
    entries = []
    for i in range(ROUTINE_CONTROL_TABLE_COUNT):
        offset = ROUTINE_CONTROL_TABLE_BASE + i * ROUTINE_CONTROL_RECORD.size
        rid, policy_index, enable, extra = ROUTINE_CONTROL_RECORD.unpack_from(cf, offset)
        entries.append(RoutineControlEntry(
            identifier=rid, policy_index=policy_index, enable=enable,
            extra=extra, table_index=i,
        ))
    return entries


def extract_all(cf: bytes | None = None) -> FirmwareTables:
    """Extract all diagnostic tables from the firmware."""
    return FirmwareTables(
        dids=extract_dids(cf),
        services=extract_services(cf),
        wdbi_callbacks=extract_wdbi_callbacks(cf),
        routine_control=extract_routine_control(cf),
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    tables = extract_all()

    print(f"DID table: {len(tables.dids)} entries")
    with_cb = sum(1 for d in tables.dids if d.has_callback)
    print(f"  with callback: {with_cb}")

    print(f"\nService table: {len(tables.services)} entries")
    for s in tables.services:
        cb = f"0x{s.callback:05X}" if s.callback else "—"
        print(f"  SID 0x{s.sid:02X}  callback={cb}")

    print(f"\nWDBI callback table: {len(tables.wdbi_callbacks)} entries")
    print(f"  DIDs: {', '.join(f'0x{r.identifier:04X}' for r in tables.wdbi_callbacks)}")

    print(f"\nRoutineControl table: {len(tables.routine_control)} entries")


if __name__ == "__main__":
    main()
