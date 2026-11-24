"""Compare Cereal schema declarations with the event types in one local rlog."""
from __future__ import annotations

import argparse
import json
from collections import Counter

import zstandard

from tools.toyota_support.route_log import KjException, load_logreader


def _type_name(schema_type) -> str:
    kind = schema_type.which()
    if kind == "list":
        return f"list({_type_name(schema_type.list.elementType)})"
    return kind


def _field_type(field) -> str:
    proto = field.proto
    return "group" if proto.which() == "group" else _type_name(proto.slot.type)


def _fields(field) -> dict:
    proto = field.proto
    if proto.which() == "group":
        return field.schema.fields
    schema_type = proto.slot.type
    list_depth = 0
    while schema_type.which() == "list":
        schema_type = schema_type.list.elementType
        list_depth += 1
    if schema_type.which() != "struct":
        return {}
    schema = field.schema
    for _ in range(list_depth):
        schema = schema.elementType
    return schema.fields


def _inspect(args: argparse.Namespace) -> dict[str, object]:
    if args.field is not None and args.event is None:
        raise ValueError("--field requires --event")
    reader = load_logreader(args.openpilot_root)
    schema = reader.event_schema
    report: dict[str, object] = {"schema_event_types": sorted(schema.union_fields)}
    event_report: dict[str, object] | None = None
    if args.event is not None:
        if args.event not in schema.union_fields:
            raise ValueError(f"undefined Cereal event: {args.event!r}")
        event_field = schema.fields[args.event]
        event_report = {
            "name": args.event,
            "schema_type": _field_type(event_field),
            "schema_fields": {name: _field_type(field) for name, field in _fields(event_field).items()},
        }
        if args.field is not None:
            field = event_field
            for name in args.field.split("."):
                field = _fields(field).get(name)
                if field is None:
                    raise ValueError(f"undefined Cereal field: {args.event}.{args.field}")
            report["field"] = {"path": args.field, "schema_type": _field_type(field)}

    counts: Counter[str] = Counter()
    unrecognized = 0
    for event in reader(args.rlog):
        try:
            kind = event.which()
        except KjException:
            unrecognized += 1
        else:
            counts[kind] += 1
    report["observed_event_types"] = dict(counts)
    report["unrecognized_event_count"] = unrecognized
    if event_report is not None:
        event_report["observed_event_count"] = counts[args.event]
        report["event"] = event_report
    return report


def inspect_command(args: argparse.Namespace) -> int:
    try:
        report = _inspect(args)
    except (OSError, ValueError, KjException, zstandard.ZstdError) as exc:
        raise SystemExit(f"toyota route inspect: {exc}") from None
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0
