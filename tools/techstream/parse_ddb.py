#!/usr/bin/env python3
"""Parse Techstream .ddb diagnostic database files.

The supported modern layouts carry the "DiagTool DataCtrl" signature:

1. **Type-2 ECU databases** (EPS_P4DK3.ddb, EPS_CAN_P4DK.ddb, ...) — per-ECU
   diagnostic tables. A type-indexed pointer directory references sections,
   each with a 10-byte TABLE_DATA_HEAD header. Sections are uncompressed.

2. **Modern type-4/5/6 string databases** (M/V/U language files) — global OEM
   strings referenced by ECU records. M/V carry one LZSS-compressed section;
   U carries strings plus a parallel compressed resource-metadata section.

Type-1 Toyota master, type-3 Viewer, and legacy type-4 layouts are distinct and
intentionally rejected by these APIs rather than silently misparsed.

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

# First 6 bytes are constant across all regions. Bytes 6-7 vary by region
# (NA: 00 39, JP: 01 1b, EU: 00 14) — they carry a region/version tag or
# checksum, not a format identifier.
MAGIC_PREFIX = bytes.fromhex("40 00 0c 16 0c 08")
U_MAGIC_PREFIX = bytes.fromhex("39 00 0c 16 0b 15 0f")
U_LANGUAGE_TAGS = frozenset(range(0x16, 0x1B))
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

    if len(out) != decompressed_size:
        raise ValueError(
            f"truncated LZSS stream: expected {decompressed_size} bytes, "
            f"decoded {len(out)}"
        )
    return bytes(out)


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
        if offset < 0 or offset + cls.HEADER_SIZE > len(data):
            raise ValueError(
                f"section header at 0x{offset:X} extends past file size "
                f"0x{len(data):X}"
            )
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
    def record_size(self) -> int:
        if self.header.record_count == 0:
            return 0
        size, remainder = divmod(
            self.header.payload_size, self.header.record_count
        )
        if remainder:
            raise ValueError(
                f"section {self.header.table_type} payload size "
                f"{self.header.payload_size} is not divisible by record count "
                f"{self.header.record_count}"
            )
        return size


@dataclass
class DTCEntry:
    """A DTC record from section type 5 (28 bytes)."""
    code: str             # e.g. "C1511"
    string_index: int     # index into the OEM string table
    dtc_identifier: int   # encoded DTC number (e.g. 0x5511)
    raw: bytes = b""


@dataclass
class DTCFailureEntry:
    """A P5 DTC/failure-type record from section type 65 (68 bytes).

    The recovered fields are deliberately narrower than the full record:
    UTF-16 code at 0x00, packed 24-bit DTC+failure byte at 0x2C, base DTC
    description string index at 0x30, failure-type description string index at
    0x34, and the enable word at 0x40. Bytes 0x38..0x3F remain uninterpreted.
    """
    code: str
    packed_dtc: int
    description_string_index: int
    failure_string_index: int
    enabled: int
    raw: bytes = b""

    @property
    def failure_type(self) -> int:
        return self.packed_dtc & 0xFF

    @property
    def base_dtc(self) -> int:
        return (self.packed_dtc >> 8) & 0xFFFF


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
class StringMetadataEntry:
    """One U_English type-1 identifier record, aligned by string index."""

    identifier: str
    auxiliary_value: int


@dataclass
class StringDataBase:
    """Parsed OEM string database (V_English.ddb etc.)."""
    path: Path
    entry_count: int
    decompressed: bytes
    pool_offset: int      # byte offset where string data begins (after offset table)
    metadata: list[StringMetadataEntry] | None = None

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

    def get_metadata(self, index: int) -> StringMetadataEntry | None:
        """Return the U_English identifier record for a 1-based string index."""
        if self.metadata is None or index == 0 or index > len(self.metadata):
            return None
        return self.metadata[index - 1]

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
        if format_version != 0x02:
            raise ValueError(
                f"expected ECU database format 0x02, got 0x{format_version:02X}"
            )
        db = ECUDataBase(path=path, format_version=format_version)

        # Section directory: u32 offsets starting at file offset 0x24.
        # The slot index is the section type. The directory extends to the
        # first section payload (0x280 in V18), not merely through type 16;
        # newer schemas use types as high as 91.
        directory_end = None
        for i in range(0x24, len(data) - 3, 4):
            offset = struct.unpack_from("<I", data, i)[0]
            if offset:
                directory_end = offset
                break
        if directory_end is None:
            raise ValueError(f"no section offsets in {path.name}")
        if directory_end <= 0x24 or directory_end > len(data):
            raise ValueError(
                f"invalid section-directory boundary in {path.name}: "
                f"0x{directory_end:X}"
            )

        for i in range(0x24, directory_end, 4):
            offset = struct.unpack_from("<I", data, i)[0]
            if offset == 0:
                continue
            if offset + TableDataHead.HEADER_SIZE > len(data):
                raise ValueError(
                    f"section directory entry at 0x{i:X} points outside "
                    f"{path.name}: 0x{offset:X}"
                )
            header = TableDataHead.read(data, offset)
            expected_type = (i - 0x24) // 4
            if header.table_type != expected_type:
                raise ValueError(
                    f"directory slot {expected_type} in {path.name} points to "
                    f"section type {header.table_type}"
                )
            data_start = offset + TableDataHead.HEADER_SIZE
            data_end = data_start + header.payload_size
            if data_end > len(data):
                raise ValueError(
                    f"section {header.table_type} payload in {path.name} ends at "
                    f"0x{data_end:X}, past file size 0x{len(data):X}"
                )
            if header.table_type in db.sections:
                raise ValueError(
                    f"duplicate section type {header.table_type} in {path.name}"
                )
            raw = data[data_start:data_end]
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
        # Format 0x04/0x05 (M/V English): section header at 0x28.
        # Format 0x06 (U_English): different header layout, section at 0x34.
        format_version = data[8]
        if format_version not in (0x04, 0x05, 0x06):
            raise ValueError(
                f"expected string database format 0x04/0x05/0x06, got "
                f"0x{format_version:02X}"
            )
        section_offset = 0x34 if format_version == 0x06 else 0x28

        header = TableDataHead.read(data, section_offset)
        if header.compression != 1:
            raise ValueError(
                f"expected LZSS string section, got compression={header.compression}"
            )

        # The _DataDecode block starts right after the 10-byte section header.
        block_offset = section_offset + TableDataHead.HEADER_SIZE
        if block_offset + header.payload_size > len(data):
            raise ValueError(
                f"compressed string block in {path.name} extends past EOF"
            )
        compressed = data[block_offset : block_offset + header.payload_size]
        decompressed = lzss_decompress(compressed)

        entry_count = header.record_count
        pool_offset = entry_count * 6
        if pool_offset > len(decompressed):
            raise ValueError(
                f"string offset table in {path.name} is larger than decoded data"
            )

        metadata = None
        if format_version == 0x06:
            metadata_offset = struct.unpack_from("<I", data, 0x28)[0]
            if metadata_offset == 0:
                raise ValueError(f"missing U_English metadata section in {path.name}")
            metadata_header = TableDataHead.read(data, metadata_offset)
            if (
                metadata_header.table_type != 1
                or metadata_header.compression != 1
                or metadata_header.record_count != entry_count
            ):
                raise ValueError(
                    f"invalid U_English metadata header in {path.name}: "
                    f"{metadata_header}"
                )
            metadata_block = metadata_offset + TableDataHead.HEADER_SIZE
            metadata_end = metadata_block + metadata_header.payload_size
            if metadata_end > len(data):
                raise ValueError(
                    f"U_English metadata block in {path.name} extends past EOF"
                )
            metadata_data = lzss_decompress(data[metadata_block:metadata_end])
            record_size, remainder = divmod(len(metadata_data), entry_count)
            if remainder or record_size != 164:
                raise ValueError(
                    f"unexpected U_English metadata shape in {path.name}: "
                    f"{len(metadata_data)} bytes / {entry_count} records"
                )
            metadata = []
            for index in range(entry_count):
                record = metadata_data[index * record_size : (index + 1) * record_size]
                identifier = record[:160].decode(
                    "utf-16-le", errors="strict"
                ).split("\x00", 1)[0]
                metadata.append(
                    StringMetadataEntry(
                        identifier=identifier,
                        auxiliary_value=struct.unpack_from("<I", record, 160)[0],
                    )
                )

        return StringDataBase(
            path=path,
            entry_count=entry_count,
            decompressed=decompressed,
            pool_offset=pool_offset,
            metadata=metadata,
        )

    @staticmethod
    def _validate_header(data: bytes) -> None:
        if len(data) < 0x30:
            raise ValueError("file too short for .ddb header")
        # Format 0x06 has a distinct seven-byte prefix followed by a language
        # tag (0x16 English through 0x1A Turkish in the pinned corpus).
        # Standard files share six prefix bytes while bytes 6-7 vary by region.
        if data[8] == 0x06:
            valid_magic = (
                data[0:7] == U_MAGIC_PREFIX and data[7] in U_LANGUAGE_TAGS
            )
        else:
            valid_magic = data[0:6] == MAGIC_PREFIX
        if not valid_magic:
            raise ValueError(f"bad magic prefix: {data[0:8].hex()}")
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
    def extract_dtc_failure_entries(section: Section) -> list[DTCFailureEntry]:
        """Extract P5 DTC failure-type records from section type 65.

        Pinned V18 P5 databases use 68-byte records. The first 44 bytes hold a
        UTF-16LE code such as ``U023A87``. The packed value at 0x2C is the same
        code as ``base_dtc << 8 | failure_type``; 0x30 and 0x34 are 1-based
        indices into M_English for the base description and failure-type text.
        """
        if section.header.table_type != 65 or section.record_size != 68:
            raise ValueError(
                f"expected section 65 with 68-byte records, got type "
                f"{section.header.table_type} size {section.record_size}"
            )
        entries = []
        for i in range(section.header.record_count):
            off = i * 68
            raw = section.raw_data[off : off + 68]
            if len(raw) < 68:
                break
            code = raw[0:44].decode("utf-16-le", errors="replace").rstrip("\x00")
            entries.append(DTCFailureEntry(
                code=code,
                packed_dtc=struct.unpack_from("<I", raw, 44)[0],
                description_string_index=struct.unpack_from("<I", raw, 48)[0],
                failure_string_index=struct.unpack_from("<I", raw, 52)[0],
                enabled=struct.unpack_from("<I", raw, 64)[0],
                raw=raw,
            ))
        return entries

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
