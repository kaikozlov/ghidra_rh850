#!/usr/bin/env python3
"""Parse Techstream .ddb diagnostic database files.

The supported modern layouts carry the "DiagTool DataCtrl" signature:

1. **Type-1 Toyota master database** (Toyota.ddb) — global routing and ECU
   enumeration tables.  It uses the same section directory/header grammar,
   but a different factory/table-class namespace.

2. **Type-2 ECU databases** (EPS_P4DK3.ddb, EPS_CAN_P4DK.ddb, ...) — per-ECU
   diagnostic tables. A type-indexed pointer directory references sections,
   each with a 10-byte TABLE_DATA_HEAD header. Sections are uncompressed.

3. **Modern type-4/5/6 string databases** (M/V/U language files) — global OEM
   strings referenced by ECU records. M/V carry one LZSS-compressed section;
   U carries strings plus a parallel compressed resource-metadata section.

Type-3 Viewer and legacy type-4 layouts are distinct and intentionally rejected
by these APIs rather than silently misparsed.

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

# Header families observed in the pinned Techstream V18 and GTS+ corpora.
# The date/build bytes changed between the 2022 Techstream generation and the
# 2026 GTS+ generation; region/language bytes remain outside these family keys.
STANDARD_HEADER_PREFIXES = frozenset({
    bytes.fromhex("40 00 0c 16 0c 08"),  # Techstream V18 regional DBs
    bytes.fromhex("40 00 0c 1a 06 10"),  # GTS+ Gen regional DBs
    bytes.fromhex("49 00 0c 1a 03 11"),  # GTS+ Spe regional DBs
    bytes.fromhex("01 02 0a 1a 06 10"),  # GTS+ Gen P6/P6F ECU DBs
})
U_HEADER_FAMILIES = {
    bytes.fromhex("39 00 0c 16 0b 15 0f"): frozenset(range(0x16, 0x1B)),
    bytes.fromhex("48 00 0c 1a 05 12 0b"): frozenset(range(0x09, 0x0E)),
}
SIGNATURE = b"DiagTool DataCtrl\x00"

# Table identities recovered from the two KgpDataCtrl.dll factories selected
# by CDbTableRead::MakeTable (0x100228D1).  These names are not heuristic:
# FUN_1001C9D0 constructs format-1 tables and FUN_1001ECCB constructs format-2
# tables.  The subset below covers every table used by the steering/security
# audit plus the high-value Toyota master routing/identity tables.
ECU_TABLE_CLASS_NAMES = {
    0: "CDbSignalGroupTable",
    1: "CDbSignalCheckTable",
    2: "CDbSupFreezeTable",
    3: "CDbSupPidTable",
    4: "CDbSupDidTable",
    5: "CDbDiagCodeTable",
    6: "CDbPidTable",
    7: "CDbDidTable",
    10: "CDbFreezeTable",
    11: "CDbActTestTable",
    12: "CDbActTestPatternTable",
    13: "CDbPhyDataTable",
    14: "CDbPatDispTable",
    15: "CDbUnitTable",
    16: "CDbTriggerListTable",
    18: "CDbStandardInfoTable",
    19: "CDbTriggerAnalyzeRetrievalTable",
    32: "CDbDTCGroupRetrieveTable",
    35: "CDbWorkFactorSignalListTable",
    36: "CDbWorkFactorItemTable",
    37: "CDbWorkFactorPatternTable",
    38: "CDbCommEcuDataTable",
    43: "CDbBdidTable",
    44: "CDbSupBdidTable",
    45: "CDbBehaviorDataRecordTable",
    46: "CDbBehaviorSignalCheckTable",
    55: "CDbPidAdditionFrameTable",
    57: "CDbBdidTable",
    58: "CDbSupBdidTable",
    59: "CDbBehaviorDataRecordTable",
    61: "CDbDataIdForDmTable",
    62: "CDbDatamonitorP5Table",
    63: "CDbDataIdBitForDmTable",
    65: "CDbDiagCodeP5Table",
    66: "CDbDTCStatusMaskTable",
    80: "CDbDataIdBitForFfdTable",
    87: "CDbBehaviorCodeTable",
    88: "CDbBehaviorDataRecordP5Table",
    90: "CDbDataIdForRobTable",
    91: "CDbBehaviorSignalCheckTable",
    # Current GTS+ format-2 factory aliases/extensions, recovered from the
    # KgpDataCtrl.dll MakeTable jump table. Several intentionally mirror older
    # table classes at new IDs for the current Gen/P6 database families.
    151: "CDbDataIdForRobTable",
    152: "CDbBehaviorSignalCheckTable",
    153: "CDbBehaviorDataRecordP5Table",
    154: "CDbSignalGroupTable",
    155: "CDbSignalCheckTable",
    156: "CDbDataIdForDmTable",
    157: "CDbDatamonitorP5Table",
    158: "CDbTableBase",
    159: "CDbTableBase",
    160: "CDbMonitorStatus_J1979_2_3_Table",
    161: "CDbMonitorResultCan_J1979_2_3_Table",
    162: "CDbDetailLink_J1979_2_3_Table",
    163: "CDbRoBDiagCodeTable",
    164: "CDbRoBFreezeFrameTable",
    165: "CDbDDRDiagCodeTable",
    166: "CDbDataIdForDdrTable",
    167: "CDbDDRFreezeFrameTable",
    168: "CDbDDRInvalidConditionTable",
    169: "CDbTableBase",
    170: "CDbScaling_J1979_2_3_Table",
    171: "CDbPreFFDVehicleTypePIDIDTable",
}

MASTER_TABLE_CLASS_NAMES = {
    0: "CDbVariableTable",
    2: "CDbProtJudgeTable",
    3: "CDbExceptionFindIdTable",
    4: "CDbExceptionProcessIdTable",
    5: "CDbEcuGroupTable",
    13: "CDbProtInfoTable",
    14: "CDbCommInfoCanTable",
    15: "CDbCommInfoIsoTable",
    16: "CDbEcuCategoryTable",
    17: "CDbCommFrameTable",
    18: "CDbFuncCommFrameTable",
    19: "CDbDllTable",
    23: "CDbSubSystemTable",
    24: "CDbUtilityListTable",
    26: "CDbEcuFuncInfoTable",
    27: "CDbEcuFuncDetailsTable",
    28: "CDbEcuAddInfoTable",
    29: "CDbComSetTable",
    41: "CDbVehicleDecisionTable",
    43: "CDbVehicleNameTable",
    44: "CDbInstallingEcuListTable",
    56: "CDbEcuDescriptionTable",
    59: "CDbVinVehicleDecisionTable",
    62: "CDbCommDidDataTable",
    75: "CDbCanBusCarIdTable",
    77: "CDbCanBusOptionTable",
    78: "CDbCanBusComponentTable",
    79: "CDbCanBusNameTable",
    82: "CDbVehicleSetTable",
    85: "CDbCommInfoEthernetTable",
    86: "CDbCommInfoSwEcuTable",
    88: "CDbCommRidDataTable",
}


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
    def decoded_data(self) -> bytes:
        """Return the logical table bytes, decompressing a type-1 payload."""
        return lzss_decompress(self.raw_data) if self.header.compression else self.raw_data

    @property
    def record_size(self) -> int:
        if self.header.compression != 0:
            raise ValueError(
                f"section {self.header.table_type} is compressed; record size "
                "is unavailable for its on-disk payload"
            )
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

    @property
    def decoded_record_size(self) -> int:
        """Record size after decompression, with integral-shape validation."""
        if self.header.record_count == 0:
            return 0
        size, remainder = divmod(len(self.decoded_data), self.header.record_count)
        if remainder:
            raise ValueError(
                f"decoded section {self.header.table_type} size "
                f"{len(self.decoded_data)} is not divisible by record count "
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
    tail_word: int
    raw: bytes = b""

    @property
    def failure_type(self) -> int:
        return self.packed_dtc & 0xFF

    @property
    def base_dtc(self) -> int:
        return (self.packed_dtc >> 8) & 0xFFFF


@dataclass
class MasterEcuCategoryEntry:
    database_name: str
    ecu_short_name: str
    ecu_name_string_index: int
    category_id: int
    generation: int
    raw: bytes


@dataclass
class MasterDllEntry:
    dll_name: str
    category_id: int
    dll_role_id: int
    raw: bytes


@dataclass
class MasterFunctionEntry:
    name_string_index: int
    description_string_index: int
    category_id: int
    function_id: int
    sort_key: int
    raw: bytes


@dataclass
class MasterFunctionDetailEntry:
    name_string_index: int
    category_id: int
    function_id: int
    detail_id: int
    raw: bytes


@dataclass
class MasterCommSetEntry:
    """Consumer-proven subset of master type-29 ``CDbComSetTable``.

    ``send_parameter`` is deliberately not named as a timeout. The ordinary
    CAN ``SetCommSet(1)`` path copies it into ``CCommFrameData+0x18`` and passes
    it as ``CCommFrameCtrl::SendInt`` argument 4, but the shared CAN
    ``SendProc`` implementation does not read that argument. The second dword
    is independently consumed as receive-timeout input, while byte ``+0x0E``
    bounds the retry loop.
    """

    send_parameter: int
    receive_timeout: int
    exception_handler_id: int
    comm_set_id: int
    unknown_word_0c: int
    retry_count: int
    exception_handler_flag: int
    raw: bytes


@dataclass
class PriorityRecord:
    """Field-proven subset of a priority ECU-table record.

    ``fields`` contains only offsets used by an exported KgpDataCtrl consumer.
    ``raw`` intentionally retains every byte whose semantics remain unknown.
    """

    table_type: int
    fields: dict[str, int | str]
    raw: bytes


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


def _fixed_utf16le(data: bytes) -> str:
    """Decode a fixed-width UTF-16LE field through its first NUL."""
    return data.decode("utf-16-le", errors="strict").split("\x00", 1)[0]


def _records(section: Section, expected_type: int, expected_size: int) -> list[bytes]:
    if section.header.table_type != expected_type:
        raise ValueError(
            f"expected section {expected_type}, got {section.header.table_type}"
        )
    data = section.decoded_data
    if section.decoded_record_size != expected_size:
        raise ValueError(
            f"section {expected_type} decoded record size is "
            f"{section.decoded_record_size}, expected {expected_size}"
        )
    return [
        data[index * expected_size : (index + 1) * expected_size]
        for index in range(section.header.record_count)
    ]


# ── Parser ────────────────────────────────────────────────────────────────────

class DDBParser:
    """Parse Techstream .ddb diagnostic database files."""

    def parse_ecu_db(self, path: str | Path) -> ECUDataBase:
        """Parse an ECU .ddb file (uncompressed sections)."""
        return self._parse_sectioned_db(path, expected_format=0x02, label="ECU")

    def parse_master_db(self, path: str | Path) -> ECUDataBase:
        """Parse the structural section directory of type-1 ``Toyota.ddb``.

        Compressed payloads remain in their on-disk form; this API establishes
        complete table coverage and factory identities without pretending that
        every master-table record layout has been decoded.
        """
        return self._parse_sectioned_db(path, expected_format=0x01, label="master")

    def _parse_sectioned_db(
        self, path: str | Path, expected_format: int, label: str
    ) -> ECUDataBase:
        path = Path(path)
        data = path.read_bytes()
        self._validate_header(data)

        format_version = data[8]
        if format_version != expected_format:
            raise ValueError(
                f"expected {label} database format 0x{expected_format:02X}, "
                f"got 0x{format_version:02X}"
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
        if data[8] == 0x06:
            tags = U_HEADER_FAMILIES.get(data[0:7])
            valid_magic = tags is not None and data[7] in tags
        else:
            valid_magic = data[0:6] in STANDARD_HEADER_PREFIXES
        if not valid_magic:
            raise ValueError(f"bad magic prefix: {data[0:8].hex()}")
        sig_end = data.find(b"\x00", 0x0A)
        if sig_end < 0:
            raise ValueError("unterminated .ddb signature")
        sig = data[0x0A:sig_end]
        if sig != SIGNATURE[:-1]:
            raise ValueError(f"bad signature: {sig!r}")

    # ── Section-type decoders ─────────────────────────────────────────────────

    @staticmethod
    def extract_master_ecu_categories(section: Section) -> list[MasterEcuCategoryEntry]:
        """Decode format-1 type 16 fields used by CDbEcuCategory consumers."""
        return [
            MasterEcuCategoryEntry(
                database_name=_fixed_utf16le(raw[0:40]),
                ecu_short_name=_fixed_utf16le(raw[40:60]),
                ecu_name_string_index=struct.unpack_from("<I", raw, 60)[0],
                category_id=struct.unpack_from("<H", raw, 68)[0],
                generation=struct.unpack_from("<I", raw, 72)[0],
                raw=raw,
            )
            for raw in _records(section, 16, 76)
        ]

    @staticmethod
    def extract_master_dlls(section: Section) -> list[MasterDllEntry]:
        """Decode type-19 plugin filename/category/role across V18 and GTS+.

        The record remains 88 bytes, but Toyota moved the role key between the
        two pinned generations.  V18 ``CDbDllTable::FindDbItem1`` consumes a
        u8 at +0x56 and every V18 type-19 row has u16(+0x54)==0.  Current GTS+
        consumes a u16 at +0x54; its +0x56 byte is a separate field/flag and is
        nonzero on a small subset.  Detect the table generation from the whole
        section rather than interpreting the GTS+ flag as a role.
        """
        rows = _records(section, 19, 88)
        role_at_54 = any(struct.unpack_from("<H", raw, 0x54)[0] != 0 for raw in rows)
        return [
            MasterDllEntry(
                dll_name=_fixed_utf16le(raw[0:80]),
                category_id=struct.unpack_from("<H", raw, 80)[0],
                dll_role_id=(
                    struct.unpack_from("<H", raw, 0x54)[0]
                    if role_at_54
                    else raw[0x56]
                ),
                raw=raw,
            )
            for raw in rows
        ]

    @staticmethod
    def extract_master_functions(section: Section) -> list[MasterFunctionEntry]:
        """Decode type 26 string references, category/function keys, and sort key."""
        return [
            MasterFunctionEntry(
                name_string_index=struct.unpack_from("<I", raw, 0)[0],
                description_string_index=struct.unpack_from("<I", raw, 4)[0],
                category_id=struct.unpack_from("<H", raw, 8)[0],
                function_id=struct.unpack_from("<H", raw, 10)[0],
                sort_key=struct.unpack_from("<H", raw, 20)[0],
                raw=raw,
            )
            for raw in _records(section, 26, 24)
        ]

    @staticmethod
    def extract_master_function_details(
        section: Section,
    ) -> list[MasterFunctionDetailEntry]:
        """Decode the three-part type 27 lookup key and its name string index."""
        return [
            MasterFunctionDetailEntry(
                name_string_index=struct.unpack_from("<I", raw, 0)[0],
                category_id=struct.unpack_from("<H", raw, 4)[0],
                function_id=struct.unpack_from("<H", raw, 6)[0],
                detail_id=struct.unpack_from("<H", raw, 8)[0],
                raw=raw,
            )
            for raw in _records(section, 27, 24)
        ]

    @staticmethod
    def extract_master_comm_sets(section: Section) -> list[MasterCommSetEntry]:
        """Decode master type-29 fields used by CDbComSetTable/CommandCommon."""
        return [
            MasterCommSetEntry(
                send_parameter=struct.unpack_from("<I", raw, 0x00)[0],
                receive_timeout=struct.unpack_from("<I", raw, 0x04)[0],
                exception_handler_id=struct.unpack_from("<H", raw, 0x08)[0],
                comm_set_id=struct.unpack_from("<H", raw, 0x0A)[0],
                unknown_word_0c=struct.unpack_from("<H", raw, 0x0C)[0],
                retry_count=raw[0x0E],
                exception_handler_flag=raw[0x0F],
                raw=raw,
            )
            for raw in _records(section, 29, 16)
        ]

    @staticmethod
    def extract_priority_records(section: Section) -> list[PriorityRecord]:
        """Decode only consumer-proven fields of priority steering sections.

        Field provenance is pinned in ``extract_priority_ddb_semantics.py``.
        Unknown/reserved bytes are never discarded because every result carries
        the complete immutable record in ``raw``.
        """
        layouts = {
            6: (8, lambda r: {"pid_key_u8": r[2]}),
            11: (
                92,
                lambda r: {
                    "active_test_name_string_index": struct.unpack_from("<I", r, 32)[0],
                    "secondary_key_u16": struct.unpack_from("<H", r, 56)[0],
                    "primary_key_u8": r[82],
                },
            ),
            12: (24, lambda r: {"pattern_key_u16": struct.unpack_from("<H", r, 0)[0]}),
            61: (8, lambda r: {"data_id_u16": struct.unpack_from("<H", r, 2)[0]}),
            62: (
                64,
                lambda r: {
                    "name_string_index": struct.unpack_from("<I", r, 24)[0],
                    "monitor_key_u16": struct.unpack_from("<H", r, 36)[0],
                    "sort_key_u16": struct.unpack_from("<H", r, 48)[0],
                },
            ),
            63: (
                16,
                lambda r: {
                    "lookup_key_u16": struct.unpack_from("<H", r, 0)[0],
                    "variable_index_u16": struct.unpack_from("<H", r, 2)[0],
                },
            ),
            80: (
                12,
                lambda r: {
                    "lookup_key_u16": struct.unpack_from("<H", r, 0)[0],
                    "variable_index_u16": struct.unpack_from("<H", r, 2)[0],
                },
            ),
            87: (
                28,
                lambda r: {
                    "behavior_signature": _fixed_utf16le(r[0:12]),
                    "name_string_index": struct.unpack_from("<I", r, 12)[0],
                    "comment_string_index": struct.unpack_from("<I", r, 16)[0],
                },
            ),
            88: (
                60,
                lambda r: {
                    "name_string_index": struct.unpack_from("<I", r, 24)[0],
                    "behavior_key_u16": struct.unpack_from("<H", r, 36)[0],
                    "sort_key_u16": struct.unpack_from("<H", r, 46)[0],
                },
            ),
            90: (8, lambda r: {"data_id_u16": struct.unpack_from("<H", r, 2)[0]}),
            91: (12, lambda r: {"behavior_key_u16": struct.unpack_from("<H", r, 0)[0]}),
        }
        try:
            record_size, decoder = layouts[section.header.table_type]
        except KeyError as exc:
            raise ValueError(
                f"section {section.header.table_type} is not a priority decoded layout"
            ) from exc
        return [
            PriorityRecord(section.header.table_type, decoder(raw), raw)
            for raw in _records(section, section.header.table_type, record_size)
        ]

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
                tail_word=struct.unpack_from("<I", raw, 64)[0],
                raw=raw,
            ))
        return entries

    @staticmethod
    def extract_dids(section: Section) -> list[int]:
        """Extract bounded DID record keys from type-7 ``CDbDidTable`` rows.

        This helper must only be passed section 7.  Section 3 is
        ``CDbSupPidTable`` and must never be promoted as DID evidence.
        """
        if section.header.table_type != 7:
            raise ValueError(
                f"expected CDbDidTable section 7, got {section.header.table_type}"
            )
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

    @staticmethod
    def extract_supported_pid_records(section: Section) -> list[bytes]:
        """Return raw type-3 ``CDbSupPidTable`` records.

        The two bytes at offsets 4–5 were formerly mislabeled as a little-
        endian DID.  Preserve the complete record until its support-mask field
        semantics are independently recovered.
        """
        if section.header.table_type != 3:
            raise ValueError(
                f"expected CDbSupPidTable section 3, got {section.header.table_type}"
            )
        if section.record_size != 8:
            raise ValueError(
                f"CDbSupPidTable record size is {section.record_size}, expected 8"
            )
        return [
            section.raw_data[index * 8 : (index + 1) * 8]
            for index in range(section.header.record_count)
        ]
