#!/usr/bin/env python3
"""Validate, compare, and deliberately update canonical Ghidra JSONL inventories."""
from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

RECORD_ORDER = {
    "meta": 0,
    "memory_block": 1,
    "function": 2,
    "user_symbol": 3,
    "listing_comment": 4,
    "function_comment": 5,
    "bookmark": 6,
    "totals": 7,
}
REQUIRED_KEYS = {
    "meta": (
        "record", "schema_version", "ghidra_version", "program_name",
        "executable_sha256", "executable_format", "language_id", "compiler_spec_id",
    ),
    "memory_block": (
        "record", "name", "start", "end", "size", "block_type", "initialized",
        "overlay", "loaded", "read", "write", "execute", "volatile", "artificial",
        "source_infos",
    ),
    "function": (
        "record", "entry", "body_ranges", "body_address_count", "is_thunk",
        "thunk_target", "is_inline", "is_external", "user_name", "name_source",
        "signature_source", "calling_convention", "return", "parameters", "varargs",
        "no_return", "custom_storage", "stack_purge_size",
    ),
    "user_symbol": ("record", "address", "symbol_type", "qualified_name", "primary"),
    "listing_comment": ("record", "address", "comment_type", "text"),
    "function_comment": ("record", "entry", "comment_type", "text"),
    "bookmark": ("record", "address", "type", "category", "comment"),
    "totals": (
        "record", "functions", "instructions", "symbols", "memory_blocks",
        "body_ranges", "body_addresses", "user_function_names", "user_symbols",
        "listing_comments", "function_comments", "bookmarks", "name_sources",
        "calling_conventions", "signature_sources",
    ),
}
ADDRESS_KEYS = ("space", "offset")
DATA_TYPE_KEYS = ("path", "length")
RETURN_KEYS = ("source", "formal_type", "data_type", "storage")
PARAMETER_KEYS = (
    "ordinal", "source", "formal_type", "data_type", "auto", "forced_indirect", "storage",
)
SOURCE_INFO_KEYS = (
    "destination_min", "destination_max", "length", "mapped_range", "byte_mapping",
    "file_bytes",
)
BYTE_MAPPING_KEYS = ("mapped_byte_count", "mapped_source_byte_count")
FILE_BYTES_KEYS = ("filename", "file_offset", "size", "source_offset")


def address_key(value: Any) -> tuple[str, int]:
    if not isinstance(value, dict):
        return ("", -1)
    offset = value.get("offset")
    return (str(value.get("space", "")), -1 if offset is None else int(str(offset), 16))


def range_key(value: dict[str, Any]) -> tuple[tuple[str, int], tuple[str, int]]:
    return (address_key(value["min"]), address_key(value["max"]))


def address_span(minimum: dict[str, Any], maximum: dict[str, Any], label: str) -> int:
    if minimum["space"] != maximum["space"] or minimum["offset"] is None or maximum["offset"] is None:
        raise ValueError(f"{label} must stay within one concrete address space")
    start = int(minimum["offset"], 16)
    end = int(maximum["offset"], 16)
    if end < start:
        raise ValueError(f"{label} has an inverted address range")
    return end - start + 1


def record_sort_key(record: dict[str, Any]) -> tuple[Any, ...]:
    kind = str(record["record"])
    if kind == "memory_block":
        return (address_key(record["start"]), record["name"])
    if kind == "function":
        return (address_key(record["entry"]),)
    if kind == "user_symbol":
        return (
            address_key(record["address"]),
            record["qualified_name"],
            record["symbol_type"],
        )
    if kind == "listing_comment":
        return (address_key(record["address"]), record["comment_type"])
    if kind == "function_comment":
        return (address_key(record["entry"]), record["comment_type"])
    if kind == "bookmark":
        return (
            address_key(record["address"]),
            record["type"],
            record["category"],
            record["comment"],
        )
    return ()


def fail_keys(label: str, value: dict[str, Any], expected: tuple[str, ...]) -> None:
    if tuple(value) != expected:
        expected_set = set(expected)
        raise ValueError(
            f"{label} schema/order mismatch: missing={sorted(expected_set - set(value))} "
            f"extra={sorted(set(value) - expected_set)} actual_order={list(value)!r}"
        )


def validate_address(label: str, value: object) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an address object")
    fail_keys(label, value, ADDRESS_KEYS)
    if not isinstance(value["space"], str):
        raise ValueError(f"{label}.space must be a string")
    offset = value["offset"]
    if value["space"] == "NO_ADDRESS":
        if offset is not None:
            raise ValueError(f"{label} NO_ADDRESS offset must be null")
    elif (
        not isinstance(offset, str) or len(offset) < 8 or len(offset) % 2 != 0 or
        any(c not in "0123456789abcdef" for c in offset)
    ):
        raise ValueError(f"{label}.offset must be fixed-width lowercase hex")


def validate_data_type(label: str, value: object) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a datatype object")
    fail_keys(label, value, DATA_TYPE_KEYS)
    if (
        not isinstance(value["path"], str) or isinstance(value["length"], bool) or
        not isinstance(value["length"], int)
    ):
        raise ValueError(f"{label} has invalid datatype fields")


def validate_record(record: dict[str, Any], line_number: int) -> str:
    kind = record.get("record")
    if not isinstance(kind, str) or kind not in RECORD_ORDER:
        raise ValueError(f"line {line_number}: unknown record type {kind!r}")
    fail_keys(f"line {line_number} {kind}", record, REQUIRED_KEYS[kind])

    boolean_fields = {
        "memory_block": {
            "initialized", "overlay", "loaded", "read", "write", "execute",
            "volatile", "artificial",
        },
        "function": {
            "is_thunk", "is_inline", "is_external", "varargs", "no_return",
            "custom_storage",
        },
        "user_symbol": {"primary"},
    }.get(kind, set())
    for key in boolean_fields:
        if not isinstance(record[key], bool):
            raise ValueError(f"line {line_number}.{key} must be a boolean")

    string_fields = {
        "meta": {
            "ghidra_version", "program_name", "executable_sha256", "executable_format",
            "language_id", "compiler_spec_id",
        },
        "memory_block": {"name", "block_type"},
        "function": {"name_source", "signature_source", "calling_convention"},
        "user_symbol": {"symbol_type", "qualified_name"},
        "listing_comment": {"comment_type", "text"},
        "function_comment": {"comment_type", "text"},
        "bookmark": {"type", "category", "comment"},
    }.get(kind, set())
    for key in string_fields:
        if not isinstance(record[key], str):
            raise ValueError(f"line {line_number}.{key} must be a string")

    for key in ("address", "entry", "start", "end", "thunk_target"):
        if key in record:
            validate_address(f"line {line_number}.{key}", record[key])
    if kind == "memory_block":
        size = record["size"]
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ValueError(f"line {line_number}.size must be a nonnegative integer")
        if size != address_span(record["start"], record["end"], f"line {line_number} memory block"):
            raise ValueError(f"line {line_number}.size does not match start/end")
        source_infos = record["source_infos"]
        if not isinstance(source_infos, list):
            raise ValueError(f"line {line_number}.source_infos must be a list")
        for index, item in enumerate(source_infos):
            if not isinstance(item, dict):
                raise ValueError(f"line {line_number}.source_infos[{index}] must be an object")
            fail_keys(f"line {line_number}.source_infos[{index}]", item, SOURCE_INFO_KEYS)
            if isinstance(item["length"], bool) or not isinstance(item["length"], int) or item["length"] < 0:
                raise ValueError(f"line {line_number}.source_infos[{index}].length is invalid")
            validate_address(
                f"line {line_number}.source_infos[{index}].destination_min",
                item["destination_min"],
            )
            validate_address(
                f"line {line_number}.source_infos[{index}].destination_max",
                item["destination_max"],
            )
            if item["length"] != address_span(
                item["destination_min"], item["destination_max"],
                f"line {line_number}.source_infos[{index}]",
            ):
                raise ValueError(f"line {line_number}.source_infos[{index}].length is inconsistent")
            mapped = item["mapped_range"]
            if mapped is not None:
                if not isinstance(mapped, dict) or tuple(mapped) != ("min", "max"):
                    raise ValueError(
                        f"line {line_number}.source_infos[{index}].mapped_range is invalid"
                    )
                validate_address(
                    f"line {line_number}.source_infos[{index}].mapped_range.min", mapped["min"]
                )
                validate_address(
                    f"line {line_number}.source_infos[{index}].mapped_range.max", mapped["max"]
                )
            mapping = item["byte_mapping"]
            if mapping is not None:
                if not isinstance(mapping, dict):
                    raise ValueError(
                        f"line {line_number}.source_infos[{index}].byte_mapping is invalid"
                    )
                fail_keys(
                    f"line {line_number}.source_infos[{index}].byte_mapping",
                    mapping,
                    BYTE_MAPPING_KEYS,
                )
                if any(
                    isinstance(value, bool) or not isinstance(value, int) or value < 0
                    for value in mapping.values()
                ):
                    raise ValueError(
                        f"line {line_number}.source_infos[{index}].byte_mapping has invalid counts"
                    )
            file_bytes = item["file_bytes"]
            if file_bytes is not None:
                if not isinstance(file_bytes, dict):
                    raise ValueError(f"line {line_number}.source_infos[{index}].file_bytes is invalid")
                fail_keys(
                    f"line {line_number}.source_infos[{index}].file_bytes",
                    file_bytes,
                    FILE_BYTES_KEYS,
                )
                if not isinstance(file_bytes["filename"], str) or any(
                    isinstance(file_bytes[key], bool) or not isinstance(file_bytes[key], int) or
                    file_bytes[key] < 0
                    for key in ("file_offset", "size", "source_offset")
                ):
                    raise ValueError(f"line {line_number}.source_infos[{index}].file_bytes is invalid")
        source_keys = []
        for item in source_infos:
            mapped = item["mapped_range"]
            file_bytes = item["file_bytes"]
            source_keys.append((
                address_key(item["destination_min"]),
                address_key(item["destination_max"]),
                () if mapped is None else range_key(mapped),
                () if item["byte_mapping"] is None else (
                    item["byte_mapping"]["mapped_byte_count"],
                    item["byte_mapping"]["mapped_source_byte_count"],
                ),
                () if file_bytes is None else (
                    file_bytes["filename"], file_bytes["file_offset"],
                    file_bytes["size"], file_bytes["source_offset"],
                ),
            ))
        if source_keys != sorted(source_keys):
            raise ValueError(f"line {line_number}.source_infos are not canonically ordered")
        if sum(item["length"] for item in source_infos) != size:
            raise ValueError(f"line {line_number}.source_infos do not cover the memory block")
    if kind == "function":
        ranges = record["body_ranges"]
        if not isinstance(ranges, list):
            raise ValueError(f"line {line_number}.body_ranges must be a list")
        for index, item in enumerate(ranges):
            if not isinstance(item, dict) or tuple(item) != ("min", "max"):
                raise ValueError(f"line {line_number}.body_ranges[{index}] is invalid")
            validate_address(f"line {line_number}.body_ranges[{index}].min", item["min"])
            validate_address(f"line {line_number}.body_ranges[{index}].max", item["max"])
        if [range_key(item) for item in ranges] != sorted(range_key(item) for item in ranges):
            raise ValueError(f"line {line_number}.body_ranges are not canonically ordered")
        derived_body_count = sum(
            address_span(item["min"], item["max"], f"line {line_number}.body_ranges")
            for item in ranges
        )
        if record["body_address_count"] != derived_body_count:
            raise ValueError(f"line {line_number}.body_address_count does not match body_ranges")
        for key in ("body_address_count", "stack_purge_size"):
            if isinstance(record[key], bool) or not isinstance(record[key], int):
                raise ValueError(f"line {line_number}.{key} must be an integer")
        user_name = record["user_name"]
        if user_name is not None and not isinstance(user_name, str):
            raise ValueError(f"line {line_number}.user_name must be a string or null")
        if (user_name is not None) != (record["name_source"] == "USER_DEFINED"):
            raise ValueError(f"line {line_number}.user_name contradicts name_source")
        has_thunk_target = record["thunk_target"]["space"] != "NO_ADDRESS"
        if record["is_thunk"] != has_thunk_target:
            raise ValueError(f"line {line_number}.thunk_target contradicts is_thunk")
        returned = record["return"]
        if not isinstance(returned, dict):
            raise ValueError(f"line {line_number}.return must be an object")
        fail_keys(f"line {line_number}.return", returned, RETURN_KEYS)
        validate_data_type(f"line {line_number}.return.formal_type", returned["formal_type"])
        validate_data_type(f"line {line_number}.return.data_type", returned["data_type"])
        if not isinstance(returned["source"], str) or not isinstance(returned["storage"], str):
            raise ValueError(f"line {line_number}.return has invalid scalar fields")
        parameters = record["parameters"]
        if not isinstance(parameters, list):
            raise ValueError(f"line {line_number}.parameters must be a list")
        for index, parameter in enumerate(parameters):
            if not isinstance(parameter, dict):
                raise ValueError(f"line {line_number}.parameters[{index}] must be an object")
            fail_keys(f"line {line_number}.parameters[{index}]", parameter, PARAMETER_KEYS)
            validate_data_type(f"line {line_number}.parameters[{index}].formal_type", parameter["formal_type"])
            validate_data_type(f"line {line_number}.parameters[{index}].data_type", parameter["data_type"])
            if (
                isinstance(parameter["ordinal"], bool) or not isinstance(parameter["ordinal"], int) or
                not isinstance(parameter["source"], str) or not isinstance(parameter["storage"], str) or
                not isinstance(parameter["auto"], bool) or
                not isinstance(parameter["forced_indirect"], bool)
            ):
                raise ValueError(f"line {line_number}.parameters[{index}] has invalid scalar fields")
    if kind == "meta":
        if isinstance(record["schema_version"], bool) or record["schema_version"] != 1:
            raise ValueError(f"line {line_number}: unsupported schema {record['schema_version']}")
        digest = record["executable_sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError(f"line {line_number}: invalid executable_sha256")
    if kind == "totals":
        maps = {"calling_conventions", "name_sources", "signature_sources"}
        for key in set(REQUIRED_KEYS["totals"]) - maps - {"record"}:
            value = record[key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"line {line_number}.{key} must be a nonnegative integer")
        for key in maps:
            value = record[key]
            if not isinstance(value, dict) or list(value) != sorted(value):
                raise ValueError(f"line {line_number}.{key} must be a key-sorted object")
            if any(
                not isinstance(name, str) or isinstance(count, bool) or
                not isinstance(count, int) or count < 0
                for name, count in value.items()
            ):
                raise ValueError(f"line {line_number}.{key} has invalid counts")
    return kind


def validate(path: Path, raw: bytes | None = None) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"inventory file not found: {path}")
    if raw is None:
        raw = path.read_bytes()
    if not raw.endswith(b"\n") or b"\r" in raw:
        raise ValueError("inventory must use UTF-8 LF lines and end with newline")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"inventory is not UTF-8: {error}") from error

    records: list[dict[str, Any]] = []
    previous_order = -1
    previous_sort_key: dict[str, tuple[Any, ...]] = {}
    counts = {kind: 0 for kind in RECORD_ORDER}
    for line_number, line in enumerate(text.splitlines(), 1):
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"line {line_number}: invalid JSON: {error}") from error
        if not isinstance(parsed, dict):
            raise ValueError(f"line {line_number}: record must be an object")
        canonical = json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))
        if line != canonical:
            raise ValueError(f"line {line_number}: JSON is not canonical compact form")
        kind = validate_record(parsed, line_number)
        order = RECORD_ORDER[kind]
        if order < previous_order:
            raise ValueError(f"line {line_number}: {kind} record is out of order")
        previous_order = order
        sort_key = record_sort_key(parsed)
        if kind in previous_sort_key:
            if sort_key < previous_sort_key[kind]:
                raise ValueError(f"line {line_number}: {kind} records are not canonically ordered")
            if sort_key == previous_sort_key[kind] and kind not in {"meta", "totals"}:
                raise ValueError(f"line {line_number}: duplicate {kind} semantic identity")
        previous_sort_key[kind] = sort_key
        counts[kind] += 1
        records.append(parsed)

    if not records or records[0]["record"] != "meta" or records[-1]["record"] != "totals":
        raise ValueError("inventory must start with meta and end with totals")
    if counts["meta"] != 1 or counts["totals"] != 1:
        raise ValueError("inventory must contain exactly one meta and one totals record")

    address_widths: dict[str, set[int]] = {}

    def collect_address_widths(value: Any) -> None:
        if isinstance(value, dict):
            if tuple(value) == ADDRESS_KEYS and value["space"] != "NO_ADDRESS":
                address_widths.setdefault(value["space"], set()).add(len(value["offset"]))
            for nested in value.values():
                collect_address_widths(nested)
        elif isinstance(value, list):
            for nested in value:
                collect_address_widths(nested)

    for record in records:
        collect_address_widths(record)
    inconsistent_widths = {
        space: sorted(widths) for space, widths in address_widths.items() if len(widths) != 1
    }
    if inconsistent_widths:
        raise ValueError(f"address offsets are not fixed-width by space: {inconsistent_widths}")

    totals = records[-1]
    functions = [record for record in records if record["record"] == "function"]
    expected_totals: dict[str, Any] = {
        "functions": len(functions),
        "memory_blocks": counts["memory_block"],
        "body_ranges": sum(len(record["body_ranges"]) for record in functions),
        "body_addresses": sum(record["body_address_count"] for record in functions),
        "user_function_names": sum(record["user_name"] is not None for record in functions),
        "user_symbols": counts["user_symbol"],
        "listing_comments": counts["listing_comment"],
        "function_comments": counts["function_comment"],
        "bookmarks": counts["bookmark"],
    }
    calling_conventions: dict[str, int] = {}
    name_sources: dict[str, int] = {}
    signature_sources: dict[str, int] = {}
    for function in functions:
        convention = function["calling_convention"]
        name_source = function["name_source"]
        signature = function["signature_source"]
        calling_conventions[convention] = calling_conventions.get(convention, 0) + 1
        name_sources[name_source] = name_sources.get(name_source, 0) + 1
        signature_sources[signature] = signature_sources.get(signature, 0) + 1
    expected_totals["calling_conventions"] = dict(sorted(calling_conventions.items()))
    expected_totals["name_sources"] = dict(sorted(name_sources.items()))
    expected_totals["signature_sources"] = dict(sorted(signature_sources.items()))
    for key, expected in expected_totals.items():
        if totals[key] != expected:
            raise ValueError(
                f"totals.{key} mismatch: recorded={totals[key]!r} computed={expected!r}"
            )
    return records


def compare(baseline: Path, current: Path) -> bool:
    baseline = baseline.resolve(strict=False)
    current = current.resolve(strict=False)
    if baseline == current or (
        baseline.exists() and current.exists() and os.path.samefile(baseline, current)
    ):
        raise ValueError("parity comparison requires two distinct inventory artifacts")
    expected_bytes = baseline.read_bytes()
    actual_bytes = current.read_bytes()
    validate(baseline, expected_bytes)
    validate(current, actual_bytes)
    if expected_bytes == actual_bytes:
        return True
    expected = expected_bytes.decode("utf-8").splitlines(keepends=True)
    actual = actual_bytes.decode("utf-8").splitlines(keepends=True)
    sys.stdout.writelines(
        difflib.unified_diff(
            expected,
            actual,
            fromfile=f"baseline/{baseline.name}",
            tofile=f"current/{current.name}",
        )
    )
    return False


def update(first: Path, second: Path, destination: Path) -> None:
    first = first.resolve(strict=False)
    second = second.resolve(strict=False)
    destination = destination.resolve(strict=False)
    if first == second:
        raise ValueError("rebuild inventory inputs must resolve to distinct files")
    if first.exists() and second.exists() and os.path.samefile(first, second):
        raise ValueError("rebuild inventory inputs must not alias the same file")
    if destination in {first, second}:
        raise ValueError("baseline destination must be distinct from both rebuild inputs")
    if destination.exists() and any(
        source.exists() and os.path.samefile(destination, source)
        for source in (first, second)
    ):
        raise ValueError("baseline destination must not alias a rebuild input")
    first_bytes = first.read_bytes()
    second_bytes = second.read_bytes()
    validate(first, first_bytes)
    validate(second, second_bytes)
    if first_bytes != second_bytes:
        raise ValueError("independent rebuild inventories disagree; refusing baseline update")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.update.", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(first_bytes)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
        directory_fd = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("inventory", type=Path)
    compare_parser = sub.add_parser("compare")
    compare_parser.add_argument("baseline", type=Path)
    compare_parser.add_argument("current", type=Path)
    update_parser = sub.add_parser("update")
    update_parser.add_argument("first_rebuild", type=Path)
    update_parser.add_argument("second_rebuild", type=Path)
    update_parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    try:
        if args.command == "validate":
            validate(args.inventory)
        elif args.command == "compare":
            if not compare(args.baseline, args.current):
                print("ERROR: normalized project inventory mismatch", file=sys.stderr)
                return 1
        else:
            update(args.first_rebuild, args.second_rebuild, args.destination)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())