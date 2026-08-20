#!/usr/bin/env python3
"""Conservative outer-container parser for Toyota CUW calibration packages.

The framing implemented here is *statically recovered* from Techstream V18
`Cuw.exe` (SHA-256 97f7b9302a6090e2715ca6c9713aecc73404d6c0f75aede2dd52f09bd201074b):

  magic     13 bytes  00 43 41 4C 49 42 52 41 54 49 4F 4E 00   (const @ 0x5D453C,
              installed by the 0x412CE0 initializer, PUSH 0xD = 13, and
              compared by the container parser 0x413BF0 at 0x413C43)
  type      1 byte    membership-checked against the 11-entry table at
              0x5D5284 (count 11 @ 0x5D5290): {01,03,04,05,06,07,08,09,65,66,67}.
              Values {01,03,04} additionally equal TCUWCalibrationFile.dll
              `gbytFORMAT_VERSIONS` @ 0x100063A4.  Semantics of the other
              members are NOT claimed - only membership enforcement
              (raiser 0x414124 "This version of calibration file is not
              supported by this program.").
  crc32     u32-BE    stored CRC, parsed at 0x413CF8..0x413D57 -> object +0x14
  total     u32-BE    declared total file size measured from file offset 0,
              parsed at 0x413D5E..0x413DE0 -> object +0x18
  member    u16-BE name length || name || u32-BE payload length ||
              u32-BE payload CRC32 || payload           (reader 0x412F9C,
              whose consumed-bytes return value is name_len + 8 + payload_len;
              the payload CRC is verified against the 0x412C98 zlib CRC32,
              raiser 0x4131B0 "File is corrupt (CRC Error)")
  tail      format-specific CPU-image remainder, deliberately opaque here

Outer checks performed by 0x413BF0 at its tail (0x41403B..0x41407A):

  * CRC32 is computed over [18, declared_total) - i.e. from immediately after
    the stored-CRC field (beginning at the total-size field) through the
    declared end - and compared with the stored CRC (compare @ 0x41405B,
    CRC computed by 0x412C98 with zlib semantics: table @ 0x5D454C,
    init/final 0xFFFFFFFF).
  * Bytes consumed by parsing must equal the declared total
    (compare @ 0x41406B, raiser 0x4142E0 "File sizes don't match").

This module validates everything above that does not require interpreting the
format-specific tail, extracts the first named member (the embedded
`attach.att` descriptor), verifies both CRCs and the size bounds, and
preserves all remaining bytes as an opaque tail.  No semantic mapping of the
tail or of individual format-type values is attempted.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
import zlib
from pathlib import Path
from typing import Any

MAGIC = bytes.fromhex("0043414c4942524154494f4e00")  # "\x00CALIBRATION\x00", 13 bytes
MAGIC_OFFSET = 0
TYPE_OFFSET = 13
STORED_CRC_OFFSET = 14
DECLARED_TOTAL_OFFSET = 18
FIRST_MEMBER_OFFSET = 22

# Membership table @ Cuw.exe 0x5D5284 (count 11 @ 0x5D5290).
# {01,03,04} are additionally TCUWCalibrationFile.dll gbytFORMAT_VERSIONS
# @ 0x100063A4; no per-value semantics are claimed for the others.
KNOWN_FORMAT_TYPES = frozenset({0x01, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x65, 0x66, 0x67})
FORMAT_VERSIONS = frozenset({0x01, 0x03, 0x04})


def parse(data: bytes) -> dict[str, Any]:
    """Validate the statically recovered outer framing of a .cuw package.

    Returns a result dictionary.  `errors` is non-empty exactly when a
    statically-enforced check fails; `tail` always preserves every byte after
    the first member record without interpretation.
    """
    res: dict[str, Any] = {
        "file_size": len(data),
        "magic_hex": data[:13].hex(),
        "format_type": None,
        "format_type_known_version": None,
        "stored_crc32": None,
        "declared_total_size": None,
        "name": None,
        "name_length": None,
        "payload_length": None,
        "payload_crc32": None,
        "payload_sha256": None,
        "computed_outer_crc32": None,
        "outer_crc_region": None,
        "first_member_end": None,
        "tail_length": None,
        "tail_sha256": None,
        "notes": [],
        "errors": [],
    }
    err = res["errors"].append

    if len(data) < TYPE_OFFSET:
        err(f"truncated before magic: {len(data)} bytes < 13")
        return res
    if data[MAGIC_OFFSET:TYPE_OFFSET] != MAGIC:
        err(f"bad magic {data[MAGIC_OFFSET:TYPE_OFFSET].hex()} != {MAGIC.hex()}")

    if len(data) < STORED_CRC_OFFSET:
        err(f"truncated before format type at offset {TYPE_OFFSET}")
        return res
    fmt = data[TYPE_OFFSET]
    res["format_type"] = fmt
    if fmt not in KNOWN_FORMAT_TYPES:
        err(f"format type 0x{fmt:02x} not in statically recovered membership table")
    res["format_type_known_version"] = fmt in FORMAT_VERSIONS or None

    if len(data) < FIRST_MEMBER_OFFSET:
        err(f"truncated before crc/size fields at offset {STORED_CRC_OFFSET}")
        return res
    res["stored_crc32"] = struct.unpack_from(">I", data, STORED_CRC_OFFSET)[0]
    declared = struct.unpack_from(">I", data, DECLARED_TOTAL_OFFSET)[0]
    res["declared_total_size"] = declared
    if declared < FIRST_MEMBER_OFFSET:
        err(f"declared total size {declared} smaller than first member offset {FIRST_MEMBER_OFFSET}")
        return res
    if declared > len(data):
        err(f"declared total size {declared} exceeds file size {len(data)} (truncated package)")
        return res
    if declared != len(data):
        res["notes"].append(
            f"file carries {len(data) - declared} byte(s) beyond the declared total; "
            "0x413BF0 requires its own consumed-bytes count to equal the declared total, "
            "which this conservative parser cannot fully re-verify without tail semantics"
        )

    # ---- first member record: u16be name len || name || u32be len || u32be crc || payload
    off = FIRST_MEMBER_OFFSET
    if off + 2 > len(data):
        err(f"truncated before first member name length at offset {off}")
        return res
    (name_len,) = struct.unpack_from(">H", data, off)
    off += 2
    res["name_length"] = name_len
    if off + name_len > len(data):
        err(f"truncated inside first member name at offset {off} (need {name_len} bytes)")
        return res
    name = data[off:off + name_len]
    off += name_len
    try:
        res["name"] = name.decode("ascii")
    except UnicodeDecodeError:
        res["name"] = name.hex()

    if off + 8 > len(data):
        err(f"truncated before first member payload length/CRC at offset {off}")
        return res
    payload_len, payload_crc = struct.unpack_from(">II", data, off)
    off += 8
    res["payload_length"] = payload_len
    res["payload_crc32"] = payload_crc
    if off + payload_len > len(data):
        err(f"truncated inside first member payload at offset {off} (need {payload_len} bytes)")
        return res
    if FIRST_MEMBER_OFFSET + 2 + name_len + 8 + payload_len > declared:
        err("first member record extends beyond the declared total size")
    payload = data[off:off + payload_len]
    off += payload_len
    res["payload_sha256"] = _sha256(payload)
    res["first_member_end"] = off
    computed_payload_crc = zlib.crc32(payload) & 0xFFFFFFFF
    if computed_payload_crc != payload_crc:
        err(f"first member payload CRC mismatch: computed 0x{computed_payload_crc:08x} != stored 0x{payload_crc:08x}")

    # ---- outer CRC over [18, declared_total): from immediately after the
    # stored-CRC field (beginning at the total-size field) through declared end.
    computed_outer = zlib.crc32(data[DECLARED_TOTAL_OFFSET:declared]) & 0xFFFFFFFF
    res["computed_outer_crc32"] = computed_outer
    res["outer_crc_region"] = [DECLARED_TOTAL_OFFSET, declared]
    if computed_outer != res["stored_crc32"]:
        err(f"outer CRC mismatch over [{DECLARED_TOTAL_OFFSET}, {declared}): "
            f"computed 0x{computed_outer:08x} != stored 0x{res['stored_crc32']:08x}")

    tail = data[off:]
    res["tail_length"] = len(tail)
    res["tail_sha256"] = _sha256(tail)
    return res


def build_synthetic(payload: bytes, name: bytes = b"attach.att", fmt: int = 0x03,
                    tail: bytes = b"\x00" * 8) -> bytes:
    """Assemble a container byte-exactly per the statically recovered grammar.

    Used to fixture-test the parser; the reference test builds its fixture
    independently from the documented grammar rather than via this helper.
    """
    total = FIRST_MEMBER_OFFSET + 2 + len(name) + 8 + len(payload) + len(tail)
    body = bytearray()
    body += MAGIC
    body.append(fmt)
    body += struct.pack(">I", 0)  # stored CRC placeholder
    body += struct.pack(">I", total)
    body += struct.pack(">H", len(name)) + name
    body += struct.pack(">I", len(payload))
    body += struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
    body += payload
    body += tail
    stored = zlib.crc32(bytes(body[DECLARED_TOTAL_OFFSET:total])) & 0xFFFFFFFF
    body[STORED_CRC_OFFSET:STORED_CRC_OFFSET + 4] = struct.pack(">I", stored)
    return bytes(body)


def _sha256(b: bytes) -> str:
    import hashlib
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", type=Path, help="raw .cuw/.cal package file")
    ap.add_argument("--output", type=Path, help="write the JSON result here")
    ap.add_argument("--payload-out", type=Path, help="write the first member payload here")
    args = ap.parse_args()

    data = args.input.read_bytes()
    res = parse(data)
    ok = not res["errors"]
    res["ok"] = ok
    if args.payload_out is not None and res["first_member_end"] is not None:
        end = res["first_member_end"]
        args.payload_out.write_bytes(data[end - res["payload_length"]:end])
        res["payload_written"] = str(args.payload_out)

    text = json.dumps(res, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    if not ok:
        for e in res["errors"]:
            print(f"error: {e}", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
