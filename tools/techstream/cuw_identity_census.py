#!/usr/bin/env python3
"""Byte-level identity census across Toyota CUW containers and recoverable CPU images."""
from __future__ import annotations

import hashlib
import io
import re
import sqlite3
from pathlib import Path
from typing import Any

from inspect_cuw_vforest import decode_ascii_hex_payload, parse_zv_lzf_stream
from parse_cuw_container import parse as parse_cuw_container


def _byte_forms(text: str) -> list[tuple[str, bytes]]:
    ascii_bytes = text.encode("ascii")
    base = [
        ("ascii", ascii_bytes),
        ("ascii_lower", ascii_bytes.lower()),
        ("utf16le", text.encode("utf-16-le")),
        ("utf16be", text.encode("utf-16-be")),
        ("inverted_ascii", bytes(0xFF - value for value in ascii_bytes)),
    ]
    out = list(base)
    for name, value in base:
        out.append((f"hex_{name}_upper", value.hex().upper().encode("ascii")))
        out.append((f"hex_{name}_lower", value.hex().lower().encode("ascii")))
    return out


def _patterns(identities: dict[str, str]) -> tuple[re.Pattern[bytes], dict[bytes, tuple[str, str]], int]:
    by_bytes: dict[bytes, tuple[str, str]] = {}
    for label, text in identities.items():
        for encoding, value in _byte_forms(text):
            by_bytes.setdefault(value, (label, encoding))
    ordered = sorted(by_bytes, key=len, reverse=True)
    return re.compile(b"|".join(re.escape(value) for value in ordered)), by_bytes, max(map(len, ordered))


def _scan_bytes(data: bytes, pattern: re.Pattern[bytes], lookup: dict[bytes, tuple[str, str]], *, base: int = 0) -> list[dict[str, Any]]:
    return [
        {"identity": lookup[match.group()][0], "encoding": lookup[match.group()][1], "offset": base + match.start()}
        for match in pattern.finditer(data)
    ]


def _scan_srecords(
    blob: bytes,
    pattern: re.Pattern[bytes],
    lookup: dict[bytes, tuple[str, str]],
    max_pattern: int,
) -> tuple[int, int, list[dict[str, Any]]]:
    """Stream correctly framed S1/S2/S3 payload bytes with cross-chunk carry.

    An S-record line is ``Sx || count || address || data || checksum``.  The
    count byte is *not* part of the address.  Payload hex is accumulated and
    converted in large chunks so multi-megabyte Toyota images do not pay a
    ``bytes.fromhex`` cost for every individual S-record.
    """
    total = records = 0
    carry = b""
    hits: list[dict[str, Any]] = []
    keep = max_pattern - 1
    hex_buffer = bytearray()

    def flush() -> None:
        nonlocal total, carry
        if not hex_buffer:
            return
        try:
            decoded = bytes.fromhex(hex_buffer.decode("ascii"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError(f"invalid S-record payload hex: {exc}") from exc
        window = carry + decoded
        base = total - len(carry)
        for match in pattern.finditer(window):
            # Anything ending at/before ``total`` was wholly inside the carry
            # and was already emitted by the previous chunk.
            if base + match.end() <= total:
                continue
            identity, encoding = lookup[match.group()]
            hits.append({
                "identity": identity,
                "encoding": encoding,
                "offset": base + match.start(),
            })
        total += len(decoded)
        carry = window[-keep:] if keep else b""
        hex_buffer.clear()

    for raw_line in io.BytesIO(blob):
        record = raw_line.strip()
        kind = record[:2]
        if kind not in (b"S1", b"S2", b"S3"):
            continue
        address_hex_length = {b"S1": 4, b"S2": 6, b"S3": 8}[kind]
        if len(record) < 4 + address_hex_length + 2:
            raise ValueError("truncated S-record")
        try:
            declared_count = int(record[2:4], 16)
        except ValueError as exc:
            raise ValueError("invalid S-record count") from exc
        encoded_after_count = record[4:]
        if len(encoded_after_count) % 2 or len(encoded_after_count) // 2 != declared_count:
            raise ValueError("S-record count/line-length mismatch")
        # Strip ``Sx``, count, address and trailing checksum; concatenate only
        # logical data bytes.
        hex_buffer.extend(record[4 + address_hex_length:-2])
        records += 1
        if len(hex_buffer) >= 1 << 20:
            flush()
    flush()
    return records, total, hits


def _members(data: bytes, parsed: dict[str, Any]) -> list[tuple[str, bytes]]:
    out: list[tuple[str, bytes]] = []
    for row in parsed.get("format4_archives") or []:
        start, length = int(row["payload_offset"]), int(row["payload_length"])
        out.append((f"format4[{row['index']}]:{row['name']}", data[start:start + length]))
    for row in parsed.get("format67_members") or []:
        start, length = int(row["payload_offset"]), int(row["payload_length"])
        out.append((f"format67[{row['index']}]:{row['name']}", data[start:start + length]))
    return out


def scan_cuw_corpus(corpus_root: Path, identities: dict[str, str], *, family_prefix: bytes | None = None) -> dict[str, Any]:
    pattern, lookup, max_pattern = _patterns(identities)
    exact_hits: list[dict[str, Any]] = []
    prefix_hits: list[dict[str, Any]] = []
    srecord_bytes = zv_bytes = 0
    srecord_records = zv_records = 0
    decoded_members = 0
    package_rows: list[dict[str, Any]] = []

    paths = sorted(corpus_root.glob("*.cuw"), key=lambda path: path.name)
    for path in paths:
        data = path.read_bytes()
        parsed = parse_cuw_container(data)
        if parsed["errors"]:
            raise ValueError(f"{path.name}: CUW container errors: {parsed['errors']}")
        raw_hits = _scan_bytes(data, pattern, lookup)
        exact_hits.extend({"filename": path.name, "surface": "raw_cuw", **hit} for hit in raw_hits)
        if family_prefix:
            start = 0
            while True:
                offset = data.find(family_prefix, start)
                if offset < 0:
                    break
                prefix_hits.append({"filename": path.name, "package_offset": offset})
                start = offset + 1

        decoded_for_package = 0
        for member_name, blob in _members(data, parsed):
            if blob[:2] in (b"S0", b"S1", b"S2", b"S3"):
                records, count, hits = _scan_srecords(blob, pattern, lookup, max_pattern)
                if records:
                    decoded_members += 1
                    decoded_for_package += 1
                    srecord_records += records
                    srecord_bytes += count
                    exact_hits.extend(
                        {"filename": path.name, "surface": "srecord_decoded", "member": member_name, **hit}
                        for hit in hits
                    )
                continue
            # Known legacy Format-4 archives are ASCII-hex ZV streams. Decode only
            # when that parser accepts the complete member; opaque tails remain raw-only.
            try:
                raw = decode_ascii_hex_payload(blob)
                records, image = parse_zv_lzf_stream(raw)
            except Exception:  # bounded: unknown member representations are still scanned raw above
                continue
            decoded_members += 1
            decoded_for_package += 1
            zv_records += len(records)
            zv_bytes += len(image)
            exact_hits.extend(
                {"filename": path.name, "surface": "zv_decoded", "member": member_name, **hit}
                for hit in _scan_bytes(image, pattern, lookup)
            )
        package_rows.append({
            "filename": path.name,
            "format_type": int(parsed["format_type"]),
            "decoded_member_count": decoded_for_package,
        })

    return {
        "package_count": len(paths),
        "identities": identities,
        "exact_identity_hits": exact_hits,
        "raw_family_prefix_hits": prefix_hits,
        "decoded_member_count": decoded_members,
        "srecord_decoded_record_count": srecord_records,
        "srecord_decoded_bytes": srecord_bytes,
        "zv_decoded_record_count": zv_records,
        "zv_decoded_bytes": zv_bytes,
        "packages": package_rows,
        "scope": (
            "Every CUW is scanned byte-for-byte in direct, UTF-16, inverted and textual-hex representations. "
            "Recognized S-record CPU members are additionally streamed as decoded binary with cross-record carry; "
            "recognized ASCII-hex ZV/LZF members are decompressed and scanned as logical image bytes. Unknown/opaque "
            "tail representations remain raw-byte covered only."
        ),
    }


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_retained_gtsplus_state(root: Path) -> dict[str, Any]:
    """Census retained package/session state in one pinned GTS+ distribution tree.

    The result deliberately records only non-sensitive structural state: updater
    component names/versions, package-name references, row counts, filenames and
    source hashes.  It does not copy diagnostic/session contents.
    """
    service_log = root / "AgentLite/logs/AgentLite_Service.log"
    message_log = root / "AgentLite/logs/AgentLite_Message.log"
    datasync_db = root / "GTSPlusDataSyncDb/GTSPlusDataSync.db"
    download_root = root / "AgentLite/DOWNLOAD"
    autosave_root = root / "GTSPlus/UserData/AutoSave"
    required = (service_log, message_log, datasync_db)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ValueError(f"missing retained GTS+ state: {missing}")

    service_text = service_log.read_text(encoding="utf-8", errors="replace")
    completed_components: list[dict[str, str]] = []
    for line in service_text.splitlines():
        if "DL完了" not in line:
            continue
        match = re.search(r"CP名\[([^]]+)\],CP_Ver\[([^]]+)\]", line)
        if match:
            completed_components.append({"component": match.group(1), "version": match.group(2)})

    package_refs: set[str] = set()
    package_re = re.compile(rb"T-[0-9]{4}-[0-9]{2}")
    for log in (service_log, message_log):
        package_refs.update(match.group().decode("ascii") for match in package_re.finditer(log.read_bytes()))

    with sqlite3.connect(datasync_db) as connection:
        db_rows = {
            table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in ("hash_info", "logging_history", "process_info")
        }

    def relative_files(base: Path) -> list[str]:
        if not base.is_dir():
            return []
        return sorted(str(path.relative_to(base)) for path in base.rglob("*") if path.is_file())

    package_suffixes = {".tse", ".gtse", ".vdas", ".cuw", ".cal", ".xxz"}
    session_or_package_files = sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and path.suffix.casefold() in package_suffixes
    )

    return {
        "completed_updater_components": completed_components,
        "calibration_package_references": sorted(package_refs),
        "datasync_db_rows": db_rows,
        "download_cache_files": relative_files(download_root),
        "autosave_files": relative_files(autosave_root),
        "session_or_package_files": session_or_package_files,
        "searched_suffixes": sorted(package_suffixes),
        "source_identity": {
            str(path.relative_to(root)): {"size": path.stat().st_size, "sha256": _sha256_file(path)}
            for path in required
        },
        "boundary": (
            "This is retained local GTS+ runtime/updater state only. Empty caches and zero package-name references "
            "do not prove Toyota/TIS lacks the exact calibration; they prove the pinned local distribution did not "
            "retain a reusable vehicle package/session specimen in these surfaces."
        ),
    }
