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
    [2:4]  access flags (bit 0=read, 1=write, etc.)
    [4:8]  read callback address (0 = none)
    [8:12] extra pointer 1 (source record / config address)
    [12:16] extra pointer 2

UDS service record (24 bytes, ``<IIBBBBIII``):
    [0:4]   session-allow-list pointer
    [4:8]   subfunction-table pointer
    [8]     SID
    [9]     session-allow-list length
    [10]    security-allow-list length
    [11]    reserved
    [12:16] reserved
    [16:20] reserved
    [20:24] service callback address (0 = subfunction-table driven)

Routine/control-ID record (12 bytes, ``<HHII``):
    [0:2]  routine/control ID
    [2:4]  flags
    [4:8]  start callback
    [8:12] result callback

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

SERVICE_TABLE_BASE = 0x25E30
SERVICE_TABLE_COUNT = 17
EXTRA_SERVICE_TABLE_BASE = 0x25FC8  # 6 additional records
EXTRA_SERVICE_COUNT = 6

ROUTINE_ID_TABLE_BASE = 0x25768
ROUTINE_ID_TABLE_COUNT = 32

WRITE_DID_TABLE_BASE = 0x26AEC
WRITE_DID_TABLE_COUNT = 0x13  # 19


# ── Struct definitions ────────────────────────────────────────────────────────

DID_RECORD = struct.Struct("<HHIII")
SERVICE_RECORD = struct.Struct("<IIBBBBIII")
ROUTINE_RECORD = struct.Struct("<HHII")
WRITE_DID_RECORD = struct.Struct("<HBBI")  # did, pad, enable, extra_ptr


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class DidEntry:
    """One DID record from the firmware table."""
    identifier: int
    flags: int
    callback: int
    extra1: int
    extra2: int
    table_index: int

    @property
    def is_readable(self) -> bool:
        return bool(self.flags & 0x0001)

    @property
    def is_writable(self) -> bool:
        return bool(self.flags & 0x0002)

    @property
    def has_callback(self) -> bool:
        return self.callback != 0


@dataclass
class ServiceEntry:
    """One UDS service record."""
    session_list_ptr: int
    subfunc_table_ptr: int
    sid: int
    session_count: int
    security_count: int
    reserved: int
    callback: int
    table_index: int

    @property
    def sessions(self) -> list[int]:
        """Resolve session allow-list bytes from firmware."""
        if self.session_list_ptr == 0 or self.session_count == 0:
            return []
        data = CODEFLASH_PATH.read_bytes()
        return list(data[self.session_list_ptr:self.session_list_ptr + self.session_count])


@dataclass
class RoutineEntry:
    """One routine/control-ID record."""
    identifier: int
    flags: int
    start_callback: int
    result_callback: int
    table_index: int


@dataclass
class WriteDidEntry:
    """One write-DID descriptor."""
    identifier: int
    enable: int
    extra: int
    table_index: int


@dataclass
class FirmwareTables:
    """All diagnostic tables extracted from the firmware."""
    dids: list[DidEntry] = field(default_factory=list)
    services: list[ServiceEntry] = field(default_factory=list)
    routines: list[RoutineEntry] = field(default_factory=list)
    write_dids: list[WriteDidEntry] = field(default_factory=list)

    @property
    def did_by_id(self) -> dict[int, DidEntry]:
        return {d.identifier: d for d in self.dids}

    @property
    def did_callbacks(self) -> dict[int, int]:
        """Map callback address -> DID identifier (for reverse lookup)."""
        return {d.callback: d.identifier for d in self.dids if d.has_callback}

    @property
    def routine_by_id(self) -> dict[int, RoutineEntry]:
        return {r.identifier: r for r in self.routines}

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
        did, flags, callback, extra1, extra2 = DID_RECORD.unpack_from(cf, offset)
        entries.append(DidEntry(
            identifier=did, flags=flags, callback=callback,
            extra1=extra1, extra2=extra2, table_index=i,
        ))
    return entries


def extract_services(cf: bytes | None = None) -> list[ServiceEntry]:
    """Extract all 23 UDS service records (17 primary + 6 extra)."""
    if cf is None:
        cf = CODEFLASH_PATH.read_bytes()
    entries = []
    for i in range(SERVICE_TABLE_COUNT):
        offset = SERVICE_TABLE_BASE + i * SERVICE_RECORD.size
        row = SERVICE_RECORD.unpack_from(cf, offset)
        entries.append(ServiceEntry(
            session_list_ptr=row[0], subfunc_table_ptr=row[1], sid=row[2],
            session_count=row[3], security_count=row[4], reserved=row[5],
            callback=row[7], table_index=i,
        ))
    for i in range(EXTRA_SERVICE_COUNT):
        offset = EXTRA_SERVICE_TABLE_BASE + i * SERVICE_RECORD.size
        row = SERVICE_RECORD.unpack_from(cf, offset)
        entries.append(ServiceEntry(
            session_list_ptr=row[0], subfunc_table_ptr=row[1], sid=row[2],
            session_count=row[3], security_count=row[4], reserved=row[5],
            callback=row[7], table_index=SERVICE_TABLE_COUNT + i,
        ))
    return entries


def extract_routines(cf: bytes | None = None) -> list[RoutineEntry]:
    """Extract all 32 routine/control-ID records."""
    if cf is None:
        cf = CODEFLASH_PATH.read_bytes()
    entries = []
    for i in range(ROUTINE_ID_TABLE_COUNT):
        offset = ROUTINE_ID_TABLE_BASE + i * ROUTINE_RECORD.size
        rid, flags, start_cb, result_cb = ROUTINE_RECORD.unpack_from(cf, offset)
        entries.append(RoutineEntry(
            identifier=rid, flags=flags, start_callback=start_cb,
            result_callback=result_cb, table_index=i,
        ))
    return entries


def extract_write_dids(cf: bytes | None = None) -> list[WriteDidEntry]:
    """Extract all 19 write-DID descriptors."""
    if cf is None:
        cf = CODEFLASH_PATH.read_bytes()
    entries = []
    for i in range(WRITE_DID_TABLE_COUNT):
        offset = WRITE_DID_TABLE_BASE + i * WRITE_DID_RECORD.size
        did, _pad, enable, extra = WRITE_DID_RECORD.unpack_from(cf, offset)
        entries.append(WriteDidEntry(
            identifier=did, enable=enable, extra=extra, table_index=i,
        ))
    return entries


def extract_all(cf: bytes | None = None) -> FirmwareTables:
    """Extract all diagnostic tables from the firmware."""
    return FirmwareTables(
        dids=extract_dids(cf),
        services=extract_services(cf),
        routines=extract_routines(cf),
        write_dids=extract_write_dids(cf),
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    tables = extract_all()

    print(f"DID table: {len(tables.dids)} entries")
    readable = sum(1 for d in tables.dids if d.is_readable)
    writable = sum(1 for d in tables.dids if d.is_writable)
    with_cb = sum(1 for d in tables.dids if d.has_callback)
    print(f"  readable: {readable}, writable: {writable}, with callback: {with_cb}")

    print(f"\nService table: {len(tables.services)} entries")
    for s in tables.services:
        cb = f"0x{s.callback:05X}" if s.callback else "—"
        print(f"  SID 0x{s.sid:02X}  callback={cb}")

    print(f"\nRoutine table: {len(tables.routines)} entries")
    unique_rids = set(r.identifier for r in tables.routines)
    print(f"  unique IDs: {len(unique_rids)}")

    print(f"\nWrite-DID table: {len(tables.write_dids)} entries")


if __name__ == "__main__":
    main()
