#!/usr/bin/env python3
"""Parse Techstream .ddb diagnostic database files.

Two file types share the "DiagTool DataCtrl" magic:

1. **ECU databases** (EPS_P4DK3.ddb, EPS_CAN_P4DK.ddb, ...) — per-ECU
   diagnostic tables: DTCs, DIDs, data monitors, active tests, routines.
   Stored as sequential sections, each with a 10-byte TABLE_DATA_HEAD header.
   Sections are uncompressed (compression_flag = 0).

2. **String databases** (V_English.ddb, V_Spanish.ddb, ...) — the global OEM
   string table referenced by all ECU databases via string indices.
   Stored as one LZSS-compressed block (compression_flag = 1).

Format details recovered by decompiling DataCompress_DT.DLL!_DataDecode@12
(LZSS algorithm) and KgpDataCtrl.dll!CDbTableRead::CreateTable (file format).

LZSS algorithm (DataCompress_DT.DLL vtable[1] @ 0x10001bd0):
  - 0x1000-byte sliding window, initial write position 0xfee
  - Flag-byte-driven: read flag byte, process 8 bits (LSB first)
  - bit 1 = literal: copy 1 byte to output and window
  - bit 0 = match: read 2 bytes (b1, b2), copy (b2 & 0xf + 3) bytes from
    window position (b1 | (b2 & 0xf0) << 4) & 0xfff

Usage::

    from parse_ddb import DDBParser
    parser = DDBParser()
    eps = parser.parse_ecu_db("path/to/EPS_P4DK3.ddb")
    strings = parser.load_string_db("path/to/V_English.ddb")
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO

MAGIC = b"\x40\x00\x0c\x16\x0c\x08\x00\x39"
SIGNATURE = b"DiagTool DataCtrl\x00"


# ── LZSS decompression ────────────────────────────────────────────────────────

def lzss_decompress(data: bytes) -> bytes:
    """Decompress an LZSS-compressed block from DataCompress_DT.DLL.

    Block format: [u32 decompressed_size][u8 checksum][LZSS stream].
    Returns the decompressed payload.
    """
    if len(data) < 5:
        raise ValueError("LZSS block too short")
    decompressed_size = struct.unpack_from("<I", data, 0)[0]
    stream = data[5:]

    window = bytearray(0x1000)
    win_pos = 0xfee
    out = bytearray()
    pos = 0
    flag = 0

    while pos < len(stream) and len(out) < decompressed_size:
        flag >>= 1
        if (flag & 0x100) == 0:
            if pos >= len(stream):
                break
            flag = stream[pos] | 0xFF00
            pos += 1
        if pos >= len(stream):
            break
        if flag & 1:  # literal
            out.append(stream[pos])
            window[win_pos] = stream[pos]
            win_pos = (win_pos + 1) & 0xFFF
            pos += 1
        else:  # match
            if pos + 1 >= len(stream):
                break
            b1 = stream[pos]
            b2 = stream[pos + 1]
            pos += 2
            match_pos = (b1 | ((b2 & 0xF0) << 4)) & 0xFFF
            match_len = (b2 & 0xF) + 3
            for i in range(match_len):
                bv = window[(match_pos + i) & 0xFFF]
                out.append(bv)
                window[win_pos] = bv
                win_pos = (win_pos + 1) & 0xFFF

    return bytes(out[:decompressed_size])


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class TableDataHead:
    """Per-section header preceding each table in a .ddb file (10 bytes on disk)."""
    table_type: int       # u8 — section type ID
    compression: int      # u8 — 0=uncompressed, 1=LZSS
    record_count: int     # u32 — number of records (or decompressed size for string DBs)
    payload_size: int     # u32 — byte size of the payload that follows

    HEADER_SIZE = 10

    @classmethod
    def read(cls, data: bytes, offset: int) -> "TableDataHead":
        table_type = data[offset]
        compression = data[offset + 1]
        record_count = struct.unpack_from("<I", data, offset + 2)[0]
        payload_size = struct.unpack_from("<I", data, offset + 6)[0]
        return cls(table_type, compression, record_count, payload_size)


@dataclass
class Section:
    """A parsed section from an ECU .ddb file."""
    header: TableDataHead
    data_offset: int      # offset of payload in the file
    raw_data: bytes       # the payload bytes

    @property
    def record_size(self) -> float:
        if self.header.record_count == 0:
            return 0
        return self.header.payload_size / self.header.record_count


@dataclass
class DTCEntry:
    """A DTC record from section type 5 (28 bytes)."""
    code: str             # e.g. "C1511"
    string_index: int     # index into the OEM string table
    dtc_identifier: int   # encoded DTC number (e.g. 0x5511)
    raw: bytes = b""


@dataclass
class ECUDataBase:
    """Parsed ECU diagnostic database (.ddb file)."""
    path: Path
    format_version: int   # byte 8 of the file (0x02 for EPS, 0x05 for string DBs)
    sections: dict[int, Section] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.path.stem


@dataclass
class StringDataBase:
    """Parsed OEM string database (V_English.ddb etc.)."""
    path: Path
    entry_count: int
    decompressed: bytes
    pool_offset: int      # byte offset where string data begins (after offset table)

    def get_string(self, index: int) -> str | None:
        """Resolve a 1-based string index to text.

        Algorithm recovered from CDbVariableTable::GetVariable (KgpDataCtrl.dll
        @ 0x10050383): indices are 1-based (0 = null).  Each 6-byte entry in the
        offset table is ``[u32 offset_in_pool][u16 byte_length]``.  The string
        lives at ``pool_offset + entry.offset``, encoded UTF-16LE.
        """
        if index == 0 or index > self.entry_count:
            return None
        entry_off = (index - 1) * 6
        if entry_off + 6 > len(self.decompressed):
            return None
        rel_offset = struct.unpack_from("<I", self.decompressed, entry_off)[0]
        str_length = struct.unpack_from("<H", self.decompressed, entry_off + 4)[0]
        if str_length == 0:
            return None
        str_abs = self.pool_offset + rel_offset
        if str_abs + str_length > len(self.decompressed):
            return None
        return self.decompressed[str_abs : str_abs + str_length].decode(
            "utf-16-le", errors="replace"
        ).rstrip("\x00")

    def search(self, term: str, limit: int = 20) -> list[tuple[int, str]]:
        """Full-text search for a term in the string pool (case-insensitive)."""
        target = term.lower()
        results = []
        idx = 0
        pool = self.decompressed[self.pool_offset:]
        while len(results) < limit:
            pos = pool.lower().find(target.encode("utf-16-le").lower(), idx)
            if pos < 0:
                break
            # Find string boundaries
            start = pos
            while start > 0 and struct.unpack_from("<H", pool, start - 2)[0] != 0:
                start -= 2
            end = pos
            while end + 1 < len(pool) and struct.unpack_from("<H", pool, end)[0] != 0:
                end += 2
            text = pool[start:end].decode("utf-16-le", errors="replace")
            results.append((self.pool_offset + start, text))
            idx = end + 2
        return results


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_utf16le(data: bytes, offset: int, max_len: int = 500) -> str:
    end = offset
    while end + 1 < len(data) and end - offset < max_len:
        if struct.unpack_from("<H", data, end)[0] == 0:
            break
        end += 2
    return data[offset:end].decode("utf-16-le", errors="replace")


# ── Parser ────────────────────────────────────────────────────────────────────

class DDBParser:
    """Parse Techstream .ddb diagnostic database files."""

    def parse_ecu_db(self, path: str | Path) -> ECUDataBase:
        """Parse an ECU .ddb file (uncompressed sections)."""
        path = Path(path)
        data = path.read_bytes()
        self._validate_header(data)

        format_version = data[8]
        db = ECUDataBase(path=path, format_version=format_version)

        # Section directory: u32 offsets starting at file offset 0x24.
        # Zero entries are gaps; valid offsets point to TABLE_DATA_HEAD headers.
        for i in range(0x24, min(0x68, len(data)), 4):
            offset = struct.unpack_from("<I", data, i)[0]
            if 0 < offset < len(data):
                header = TableDataHead.read(data, offset)
                data_start = offset + TableDataHead.HEADER_SIZE
                raw = data[data_start : data_start + header.payload_size]
                db.sections[header.table_type] = Section(
                    header=header, data_offset=data_start, raw_data=raw,
                )
        return db

    def load_string_db(self, path: str | Path) -> StringDataBase:
        """Load and decompress an OEM string database (V_English.ddb)."""
        path = Path(path)
        data = path.read_bytes()
        self._validate_header(data)

        # String DBs have a single LZSS-compressed section.
        # Section header at 0x28: type=0, compression=1.
        header = TableDataHead.read(data, 0x28)
        assert header.compression == 1, f"expected LZSS, got compression={header.compression}"

        # The _DataDecode block starts right after the 10-byte section header.
        block_offset = 0x28 + TableDataHead.HEADER_SIZE
        compressed = data[block_offset : block_offset + header.payload_size]
        decompressed = lzss_decompress(compressed)

        entry_count = header.record_count
        pool_offset = entry_count * 6

        return StringDataBase(
            path=path,
            entry_count=entry_count,
            decompressed=decompressed,
            pool_offset=pool_offset,
        )

    @staticmethod
    def _validate_header(data: bytes) -> None:
        if len(data) < 0x30:
            raise ValueError("file too short for .ddb header")
        if data[0:8] != MAGIC:
            raise ValueError(f"bad magic: {data[0:8].hex()}")
        sig_end = data.find(b"\x00", 0x0A)
        sig = data[0x0A:sig_end]
        if sig != b"DiagTool DataCtrl":
            raise ValueError(f"bad signature: {sig!r}")

    # ── Section-type decoders ─────────────────────────────────────────────────

    @staticmethod
    def extract_dtcs(section: Section) -> list[DTCEntry]:
        """Extract DTC records from section type 5 (28-byte records)."""
        dtcs = []
        rec_size = 28
        for i in range(section.header.record_count):
            off = i * rec_size
            raw = section.raw_data[off : off + rec_size]
            if len(raw) < rec_size:
                break
            code = raw[0:12].decode("utf-16-le", errors="replace").rstrip("\x00")
            string_index = struct.unpack_from("<I", raw, 12)[0]
            dtc_identifier = struct.unpack_from("<H", raw, 20)[0]
            dtcs.append(DTCEntry(
                code=code,
                string_index=string_index,
                dtc_identifier=dtc_identifier,
                raw=raw,
            ))
        return dtcs

    @staticmethod
    def extract_dids(section: Section) -> list[int]:
        """Extract DID identifiers from section type 3 (8-byte records).

        Returns the DID values (e.g. 0x0100, 0x0120, 0x0140, 0x01E0).
        """
        dids = []
        rec_size = 8
        for i in range(section.header.record_count):
            off = i * rec_size
            raw = section.raw_data[off : off + rec_size]
            if len(raw) < rec_size:
                break
            did = struct.unpack_from("<H", raw, 4)[0]
            dids.append(did)
        return dids
