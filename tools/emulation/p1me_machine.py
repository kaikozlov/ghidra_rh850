#!/usr/bin/env python3
"""Resolve exact targets and execute strict P1M-E machine scenarios in Ghidra."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import struct
import subprocess
import tempfile
from collections.abc import Iterable, Iterator, Sequence
from itertools import chain, pairwise
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.project.analysis_target import target as resolve_target

ROOT = REPO_ROOT
SCRIPT = ROOT / "ghidra" / "scripts" / "emulate" / "RunP1MEMachine.java"
MODEL = ROOT / "data/generated/p1me_machine.json"
SCENARIO_SCHEMA = "rh850-p1me-machine-scenario-v2"
CONTRACT_SCHEMA = "rh850-p1me-machine-run-v2"
MODEL_SCHEMA = "rh850-p1me-machine-v2"
GPR_NAMES = (
    "r1", "r2", "sp", "gp", "tp",
    *(f"r{index}" for index in range(6, 30)),
    "ep", "lp",
)


class P1MEMachineError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _absolute_input(path: Path, *, base: Path | None = None) -> Path:
    if path.is_absolute():
        return path.resolve()
    return ((base if base is not None else Path.cwd()) / path).resolve()


def _require_keys(
    value: dict[str, Any], *, allowed: set[str], required: set[str], context: str,
) -> None:
    unknown = sorted(set(value) - allowed)
    missing = sorted(required - set(value))
    if unknown:
        raise P1MEMachineError(f"{context}: unsupported fields: {', '.join(unknown)}")
    if missing:
        raise P1MEMachineError(f"{context}: missing fields: {', '.join(missing)}")


def _require_list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise P1MEMachineError(f"{context}: expected a list")
    return value


def _validate_entry(entry: Any, context: str) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise P1MEMachineError(f"{context}: expected an object")
    scope = entry.get("scope")
    if scope == "resolved-address":
        _require_keys(
            entry,
            allowed={"role", "scope", "address"},
            required={"role", "scope", "address"},
            context=context,
        )
        try:
            address = int(entry["address"], 0)
        except (TypeError, ValueError) as exc:
            raise P1MEMachineError(
                f"{context}.address: expected an integer string",
            ) from exc
        if not 0 <= address <= 0xFFFFFFFF:
            raise P1MEMachineError(f"{context}.address: outside 32-bit address space")
        return entry

    allowed = {
        "role", "scope", "shape_sha256", "instruction_count", "body_size",
        "offset", "requirements",
    }
    required = {"role", "scope", "shape_sha256", "instruction_count", "body_size"}
    _require_keys(entry, allowed=allowed, required=required, context=context)
    if scope not in {"function", "instructions"}:
        raise P1MEMachineError(
            f"{context}.scope: expected function, instructions, or resolved-address",
        )
    digest = entry["shape_sha256"]
    if not isinstance(digest, str) or len(digest) != 64:
        raise P1MEMachineError(f"{context}.shape_sha256: expected 64 hex characters")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise P1MEMachineError(f"{context}.shape_sha256: expected hexadecimal") from exc
    if not isinstance(entry["instruction_count"], int) or entry["instruction_count"] <= 0:
        raise P1MEMachineError(f"{context}.instruction_count: expected a positive integer")
    if not isinstance(entry["body_size"], int) or entry["body_size"] <= 0:
        raise P1MEMachineError(f"{context}.body_size: expected a positive integer")
    requirements = _require_list(entry.get("requirements", []), f"{context}.requirements")
    normalized_requirements: list[dict[str, Any]] = []
    for index, requirement in enumerate(requirements):
        item_context = f"{context}.requirements[{index}]"
        if not isinstance(requirement, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        _require_keys(
            requirement,
            allowed={"index", "mnemonic", "operand", "scalar"},
            required={"index", "mnemonic"},
            context=item_context,
        )
        if not isinstance(requirement["index"], int) or requirement["index"] < 0:
            raise P1MEMachineError(f"{item_context}.index: expected a non-negative integer")
        if "scalar" in requirement and "operand" not in requirement:
            raise P1MEMachineError(f"{item_context}: scalar requires operand")
        normalized_requirements.append(requirement)
    return {
        **entry,
        "offset": entry.get("offset", 0),
        "requirements": normalized_requirements,
    }


def _validate_memory_rows(rows: Any, context: str) -> list[dict[str, Any]]:
    normalized = _require_list(rows, context)
    for index, row in enumerate(normalized):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        _require_keys(
            row,
            allowed={"address", "size", "hex", "fill", "evidence"},
            required={"address", "evidence"},
            context=item_context,
        )
        if ("hex" in row) == ("fill" in row):
            raise P1MEMachineError(f"{item_context}: specify exactly one of hex or fill")
        if "fill" in row and "size" not in row:
            raise P1MEMachineError(f"{item_context}: fill requires size")
    return normalized


def _validate_artifacts(rows: Any, context: str, base: Path) -> list[dict[str, Any]]:
    normalized = _require_list(rows, context)
    out: list[dict[str, Any]] = []
    for index, row in enumerate(normalized):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        _require_keys(
            row,
            allowed={"address", "path", "sha256", "executable", "evidence"},
            required={"address", "path", "sha256", "executable", "evidence"},
            context=item_context,
        )
        out.append({**row, "path": str(_absolute_input(Path(row["path"]), base=base))})
    return out


def _validate_checks(rows: Any, context: str) -> list[dict[str, Any]]:
    normalized = _require_list(rows, context)
    for index, row in enumerate(normalized):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        _require_keys(
            row,
            allowed={"name", "kind", "register", "address", "source_address", "size", "operation", "equals", "equals_hex"},
            required={"name", "kind"},
            context=item_context,
        )
        if row["kind"] not in {"register", "memory", "memory-equal", "sync-count", "event-count"}:
            raise P1MEMachineError(f"{item_context}.kind: unsupported check kind")
    return normalized


def _validate_events(rows: Any, context: str, *, expand: bool = True) -> list[dict[str, Any]]:
    events = _require_list(rows, context)
    normalized: list[dict[str, Any]] = []
    fields = {
        "clock": {"p_bus_cycles"},
        "can-rx": {"fifo", "can_id", "data_hex", "extended", "fd", "boundary", "label", "timestamp"},
        "csih-word": {"unit", "value", "after_transmit_words", "delay_instructions"},
        "adc-sample": {"unit", "channel", "value", "boundary"},
        "rsent-frame": {"unit", "pulse_samples", "after_spc_triggers", "delay_hsb_cycles"},
        "interrupt": {"channel", "firmware_control"},
        "can-tx-complete": {"buffer", "firmware_control", "tolerate_no_pending"},
        "memory-write": {"address", "data_hex"},
        "register-input": {"register", "value"},
        "ecm-pin-drive": {"pin", "drive"},
        "peripheral-reset": {"reset_class"},
        "reset-assert": {"reset_class"},
    }
    serial_boundaries: set[tuple[int, int]] = set()
    rsent_boundaries: set[tuple[int, int]] = set()
    for index, row in enumerate(events):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict) or row.get("kind") not in fields:
            raise P1MEMachineError(f"{item_context}: unsupported external event")
        kind = row["kind"]
        required = {
            "clock": {"p_bus_cycles"},
            "can-rx": {"fifo", "can_id", "data_hex", "boundary"},
            "csih-word": {"unit"},
            "adc-sample": {"unit", "channel", "value", "boundary"},
            "rsent-frame": {"unit", "pulse_samples"},
            "interrupt": {"channel"},
            "can-tx-complete": {"buffer"},
            "memory-write": {"address", "data_hex"},
            "register-input": {"register", "value"},
            "ecm-pin-drive": {"pin", "drive"},
            "peripheral-reset": {"reset_class"},
            "reset-assert": {"reset_class"},
        }[kind]
        relative_serial = kind == "csih-word" and "after_transmit_words" in row
        relative_spc = kind == "rsent-frame" and "after_spc_triggers" in row
        relative_reset = "after_reset_instructions" in row
        if relative_serial:
            boundary = {"after_transmit_words", "delay_instructions"}
        elif relative_spc:
            boundary = {"after_spc_triggers", "delay_hsb_cycles"}
        elif relative_reset:
            boundary = {"after_reset_instructions"}
        else:
            boundary = {"after_instructions"}
        _require_keys(
            row,
            allowed={"kind", "after_instructions", "after_reset_instructions", "evidence"}
            | fields[kind] | ({"repeat", "stride_words", "repeat_forever"} if relative_serial else set()),
            required={"kind", "evidence"} | boundary | required,
            context=item_context,
        )
        if relative_serial or relative_spc:
            if "after_instructions" in row or relative_reset:
                raise P1MEMachineError(
                    f"{item_context}: choose one instruction, reset, or controller-relative boundary",
                )
            ordinal_name, delay_name = (
                ("after_transmit_words", "delay_instructions")
                if relative_serial else ("after_spc_triggers", "delay_hsb_cycles")
            )
            for name, minimum in ((ordinal_name, 1), (delay_name, 1 if relative_serial else 0)):
                if type(row[name]) is not int or not minimum <= row[name] <= 0x7FFFFFFFFFFFFFFF:
                    raise P1MEMachineError(f"{item_context}: {name} must be a signed-64 integer >= {minimum}")
            if relative_serial:
                repeat = row.get("repeat", 1)
                stride_words = row.get("stride_words", 1)
                repeat_forever = row.get("repeat_forever", False)
                for name, value in (("repeat", repeat), ("stride_words", stride_words)):
                    if type(value) is not int or not 1 <= value <= 0x7FFFFFFFFFFFFFFF:
                        raise P1MEMachineError(f"{item_context}: {name} must be a positive signed-64 integer")
                if type(repeat_forever) is not bool:
                    raise P1MEMachineError(f"{item_context}: repeat_forever must be boolean")
                if repeat_forever and "repeat" in row:
                    raise P1MEMachineError(f"{item_context}: repeat and repeat_forever are exclusive")
                if not repeat_forever and row["after_transmit_words"] + (repeat - 1) * stride_words > 0x7FFFFFFFFFFFFFFF:
                    raise P1MEMachineError(f"{item_context}: expanded CSIH transmitted word exceeds signed-64 range")
        else:
            if "delay_instructions" in row or "delay_hsb_cycles" in row:
                raise P1MEMachineError(f"{item_context}: delay requires a controller-relative boundary")
            if relative_reset and "after_instructions" in row:
                raise P1MEMachineError(
                    f"{item_context}: choose an absolute or reset-relative boundary, not both",
                )
            tick_name = "after_reset_instructions" if relative_reset else "after_instructions"
            tick = row[tick_name]
            if type(tick) is not int or not 0 <= tick <= 0x7FFFFFFFFFFFFFFF:
                raise P1MEMachineError(
                    f"{item_context}: {tick_name} must be a nonnegative signed-64 integer",
                )
        if kind == "clock":
            if type(row["p_bus_cycles"]) is not int or not 0 < row["p_bus_cycles"] <= 0x7FFFFFFFFFFFFFFF:
                raise P1MEMachineError(f"{item_context}: p_bus_cycles must be a positive signed-64 integer")
        elif kind == "csih-word":
            if type(row["unit"]) is not int or not 0 <= row["unit"] <= 3:
                raise P1MEMachineError(f"{item_context}: invalid CSIH unit")
            if "value" in row:
                try:
                    value = int(row["value"], 0)
                except (ValueError, TypeError) as exc:
                    raise P1MEMachineError(f"{item_context}: CSIH wire value must be an integer string") from exc
                if not 0 <= value <= 0xFFFF:
                    raise P1MEMachineError(f"{item_context}: CSIH wire value exceeds 16 bits")
                row["value"] = hex(value)
        elif kind == "rsent-frame":
            if type(row["unit"]) is not int or row["unit"] not in (0, 1):
                raise P1MEMachineError(f"{item_context}: RSENT unit must be 0 or 1")
            pulses = row["pulse_samples"]
            if not isinstance(pulses, list) or not 4 <= len(pulses) <= 9 or any(
                type(sample) is not int or not 1 <= sample <= 131071 for sample in pulses
            ):
                raise P1MEMachineError(f"{item_context}: expected 4..9 pulse intervals of 1..131071 sample clocks")
            if not isinstance(row["evidence"], str) or not row["evidence"].strip():
                raise P1MEMachineError(f"{item_context}: RSENT pulse source evidence is required")
            if relative_spc:
                rsent_boundary = (row["unit"], row["after_spc_triggers"])
                if rsent_boundary in rsent_boundaries:
                    raise P1MEMachineError(f"{item_context}: duplicate response for this RSENT SPC trigger")
                rsent_boundaries.add(rsent_boundary)
        elif kind == "adc-sample":
            if type(row["unit"]) is not int or row["unit"] not in (0, 1):
                raise P1MEMachineError(f"{item_context}: ADC unit must be 0 or 1")
            channel = row["channel"]
            if type(channel) is not int or not (
                0 <= channel < 12 or (row["unit"] == 1 and channel == 12)
            ):
                raise P1MEMachineError(f"{item_context}: invalid ADC physical channel")
            if not isinstance(row["boundary"], str) or row["boundary"] not in {
                "normal", "pull-down", "pull-up", "mode1"
            }:
                raise P1MEMachineError(f"{item_context}: unsupported ADC sample boundary")
            if channel == 12 and row["boundary"] != "normal":
                raise P1MEMachineError(f"{item_context}: temperature input cannot select pin pulls")
            try:
                value = int(row["value"], 0)
            except (ValueError, TypeError) as exc:
                raise P1MEMachineError(f"{item_context}: ADC code must be an integer string") from exc
            if not 0 <= value <= 4095:
                raise P1MEMachineError(f"{item_context}: ADC sample must fit 12 bits")
            row["value"] = hex(value)
        elif kind in {"interrupt", "can-tx-complete"}:
            if kind == "interrupt":
                if type(row["channel"]) is not int or not 0 <= row["channel"] < 512:
                    raise P1MEMachineError(f"{item_context}: invalid interrupt channel")
            elif type(row["buffer"]) is not int or not 0 <= row["buffer"] < 48:
                raise P1MEMachineError(f"{item_context}: invalid RSCFD transmit buffer")
            if "tolerate_no_pending" in row and type(row["tolerate_no_pending"]) is not bool:
                raise P1MEMachineError(
                    f"{item_context}: tolerate_no_pending must be boolean",
                )
            if "firmware_control" in row:
                try:
                    control = int(row["firmware_control"], 0)
                except (ValueError, TypeError) as exc:
                    raise P1MEMachineError(
                        f"{item_context}: firmware-derived EIC control must be an integer string"
                    ) from exc
                if not 0 <= control <= 0xFFFF:
                    raise P1MEMachineError(
                        f"{item_context}: firmware-derived EIC control exceeds 16 bits"
                    )
                row["firmware_control"] = hex(control)
        elif kind == "ecm-pin-drive":
            if not isinstance(row["pin"], str) or row["pin"] not in {"ERROROUT", "ERROROUT_C"}:
                raise P1MEMachineError(f"{item_context}: unsupported ECM pin")
            if not isinstance(row["drive"], str) or row["drive"] not in {"released", "low"}:
                raise P1MEMachineError(f"{item_context}: ECM drive must be released or low")
        elif kind in {"peripheral-reset", "reset-assert"}:
            if not isinstance(row["reset_class"], str) or row["reset_class"] not in {
                "power-on", "system-1-cvm", "system-1-pin", "system-2", "application-1"
            }:
                raise P1MEMachineError(f"{item_context}: unsupported reset class")
        elif kind == "register-input":
            if not isinstance(row["register"], str) or not row["register"]:
                raise P1MEMachineError(f"{item_context}: register name must be a nonempty string")
            try:
                value = int(row["value"], 0)
            except (ValueError, TypeError) as exc:
                raise P1MEMachineError(f"{item_context}: invalid register input value") from exc
            if not 0 <= value <= 0xFFFFFFFF:
                raise P1MEMachineError(f"{item_context}: register input exceeds 32-bit range")
            row["value"] = hex(value)
        elif kind == "memory-write":
            try:
                address = int(row["address"], 0)
                payload = bytes.fromhex(row["data_hex"])
            except (ValueError, TypeError) as exc:
                raise P1MEMachineError(f"{item_context}: invalid memory address or data") from exc
            if not payload:
                raise P1MEMachineError(f"{item_context}: memory write cannot be empty")
            if not 0 <= address <= 0xFFFFFFFF or address + len(payload) - 1 > 0xFFFFFFFF:
                raise P1MEMachineError(f"{item_context}: memory write exceeds 32-bit address space")
            row["address"] = hex(address)
            row["data_hex"] = payload.hex()
        else:
            if row["boundary"] != "post-filter":
                raise P1MEMachineError(f"{item_context}: only the explicit post-filter receive boundary is supported")
            if type(row["fifo"]) is not int or not 0 <= row["fifo"] < 9:
                raise P1MEMachineError(f"{item_context}: invalid common receive FIFO")
            for field, maximum in (("label", 0xFFF), ("timestamp", 0xFFFF)):
                if field in row and (type(row[field]) is not int or not 0 <= row[field] <= maximum):
                    raise P1MEMachineError(f"{item_context}: invalid receive {field}")
            for flag in ("extended", "fd"):
                if flag in row and type(row[flag]) is not bool:
                    raise P1MEMachineError(f"{item_context}: {flag} must be boolean")
            try:
                identifier = int(row["can_id"], 0)
                payload = bytes.fromhex(row["data_hex"])
            except (ValueError, TypeError) as exc:
                raise P1MEMachineError(f"{item_context}: invalid CAN identifier or data") from exc
            if not 0 <= identifier <= (0x1FFFFFFF if row.get("extended") else 0x7FF):
                raise P1MEMachineError(f"{item_context}: CAN identifier exceeds frame format")
            lengths = {0, 1, 2, 3, 4, 5, 6, 7, 8}
            if row.get("fd"):
                lengths |= {12, 16, 20, 24, 32, 48, 64}
            if len(payload) not in lengths:
                raise P1MEMachineError(f"{item_context}: invalid CAN payload length")
            row["can_id"] = hex(identifier)
            row["data_hex"] = payload.hex()
        explicit = {key: value for key, value in row.items() if key not in {"repeat", "stride_words"}}
        if relative_serial:
            # Expand in place: source order and lifetime transmit ordinals survive
            # controller reset/abort events, just as for explicit completions.
            if repeat_forever:
                normalized.append(row)
            else:
                for repetition in range(repeat):
                    ordinal = row["after_transmit_words"] + repetition * stride_words
                    serial_boundary = (row["unit"], ordinal)
                    if serial_boundary in serial_boundaries:
                        raise P1MEMachineError(f"{item_context}: duplicate completion for this CSIH transmitted word")
                    serial_boundaries.add(serial_boundary)
                    if expand:
                        normalized.append({**explicit, "after_transmit_words": ordinal})
                if not expand:
                    normalized.append(row)
        else:
            normalized.append(row)
    return normalized


def _validate_dataflash_cells(rows: Any, context: str) -> list[dict[str, Any]]:
    normalized = _require_list(rows, context)
    intervals: list[tuple[int, int]] = []
    for index, row in enumerate(normalized):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        _require_keys(
            row, allowed={"address", "size", "state", "evidence"},
            required={"address", "size", "state", "evidence"}, context=item_context,
        )
        try:
            address = int(row["address"], 0)
        except (ValueError, TypeError) as exc:
            raise P1MEMachineError(f"{item_context}: address must be an integer string") from exc
        size = row["size"]
        if (
            type(size) is not int or size <= 0 or size % 4
            or not 0 <= address <= 0xFFFFFFFF or address % 4
            or address + size > 0x100000000
        ):
            raise P1MEMachineError(f"{item_context}: cells require a nonempty aligned 32-bit address range")
        if row["state"] not in ("erased", "programmed"):
            raise P1MEMachineError(f"{item_context}: state must be erased or programmed")
        if not isinstance(row["evidence"], str) or not row["evidence"].strip():
            raise P1MEMachineError(f"{item_context}: flash-cell state evidence is required")
        intervals.append((address, address + size))
        row["address"] = hex(address)
    intervals.sort()
    if any(left[1] > right[0] for left, right in pairwise(intervals)):
        raise P1MEMachineError(f"{context}: flash-cell ranges overlap")
    return normalized


def _validate_icus_startup_stub(value: Any, context: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise P1MEMachineError(f"{context}: expected an object")
    _require_keys(
        value, allowed={"evidence", "responses"},
        required={"evidence", "responses"}, context=context,
    )
    if not isinstance(value["evidence"], str) or not value["evidence"].strip():
        raise P1MEMachineError(f"{context}: explicit startup-stub evidence or assumption is required")
    responses = _require_list(value["responses"], f"{context}.responses")
    if not responses:
        raise P1MEMachineError(f"{context}: at least one diagnostic response is required")
    for index, response in enumerate(responses):
        item_context = f"{context}.responses[{index}]"
        if not isinstance(response, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        fields = {"command", "error_bits", "completion_hsb_cycles"}
        _require_keys(response, allowed=fields, required=fields, context=item_context)
        try:
            command = int(response["command"], 0)
            error_bits = int(response["error_bits"], 0)
        except (ValueError, TypeError) as exc:
            raise P1MEMachineError(f"{item_context}: command and error_bits require integer strings") from exc
        if command not in (0x7000, 0x7100):
            raise P1MEMachineError(f"{item_context}: only selector-free diagnostic commands 0x7000/0x7100 are supported")
        if not 0 <= error_bits <= 0xFFF:
            raise P1MEMachineError(f"{item_context}: error_bits exceeds the recovered low-twelve-bit field")
        cycles = response["completion_hsb_cycles"]
        if type(cycles) is not int or not 0 < cycles <= 0x7FFFFFFFFFFFFFFF:
            raise P1MEMachineError(f"{item_context}: completion_hsb_cycles must be a positive signed-64 integer")
        response["command"] = hex(command)
        response["error_bits"] = hex(error_bits)
    return value


def _validate_steps(rows: Any, context: str, *, expand: bool = True) -> list[dict[str, Any]]:
    steps = _require_list(rows, context)
    checkpoints: set[str] = set()
    trial_names: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(steps):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        kind = row.get("kind")
        if kind == "checkpoint":
            _require_keys(
                row,
                allowed={"kind", "name", "after_instructions"},
                required={"kind", "name"},
                context=item_context,
            )
            name = row["name"]
            after = row.get("after_instructions")
            if not isinstance(name, str) or not name or name in checkpoints:
                raise P1MEMachineError(f"{item_context}: checkpoint name must be unique")
            if after is not None and (type(after) is not int or after < 0):
                raise P1MEMachineError(
                    f"{item_context}: after_instructions must be a nonnegative integer",
                )
            checkpoints.add(name)
            normalized.append(row)
        elif kind == "restore":
            _require_keys(
                row,
                allowed={"kind", "checkpoint"},
                required={"kind", "checkpoint"},
                context=item_context,
            )
            if row["checkpoint"] not in checkpoints:
                raise P1MEMachineError(f"{item_context}: restore names an unknown checkpoint")
            normalized.append(row)
        elif kind == "trial":
            _require_keys(
                row,
                allowed={
                    "kind", "name", "max_instructions", "stop_addresses",
                    "stop_after_arrivals", "events", "checks", "capture_rows",
                    "capture_event_kinds",
                },
                required={
                    "kind", "name", "max_instructions", "stop_addresses",
                    "events", "checks",
                },
                context=item_context,
            )
            name = row["name"]
            if not checkpoints:
                raise P1MEMachineError(f"{item_context}: trial requires a prior checkpoint")
            if not isinstance(name, str) or not name or name in trial_names:
                raise P1MEMachineError(f"{item_context}: trial name must be unique")
            if type(row["max_instructions"]) is not int or row["max_instructions"] <= 0:
                raise P1MEMachineError(f"{item_context}: max_instructions must be positive")
            if "capture_rows" in row and type(row["capture_rows"]) is not bool:
                raise P1MEMachineError(f"{item_context}: capture_rows must be boolean")
            if "capture_event_kinds" in row:
                if "capture_rows" in row:
                    raise P1MEMachineError(
                        f"{item_context}: capture_event_kinds and capture_rows are mutually exclusive",
                    )
                event_kinds = _require_list(
                    row["capture_event_kinds"], f"{item_context}.capture_event_kinds",
                )
                if (
                    any(not isinstance(value, str) or not value for value in event_kinds)
                    or len(event_kinds) != len(set(event_kinds))
                ):
                    raise P1MEMachineError(
                        f"{item_context}: capture_event_kinds must contain unique nonempty strings",
                    )
            stops = _require_list(row["stop_addresses"], f"{item_context}.stop_addresses")
            if any(not isinstance(value, str) for value in stops):
                raise P1MEMachineError(f"{item_context}: stop addresses must be strings")
            arrivals = _require_list(
                row.get("stop_after_arrivals", []),
                f"{item_context}.stop_after_arrivals",
            )
            for arrival_index, arrival in enumerate(arrivals):
                arrival_context = f"{item_context}.stop_after_arrivals[{arrival_index}]"
                if not isinstance(arrival, dict):
                    raise P1MEMachineError(f"{arrival_context}: expected an object")
                _require_keys(
                    arrival,
                    allowed={"address", "count"},
                    required={"address", "count"},
                    context=arrival_context,
                )
                try:
                    address = int(arrival["address"], 0)
                except (TypeError, ValueError) as exc:
                    raise P1MEMachineError(
                        f"{arrival_context}: address must be an integer string",
                    ) from exc
                if not isinstance(arrival["address"], str) or not 0 <= address <= 0xFFFFFFFF:
                    raise P1MEMachineError(
                        f"{arrival_context}: address must be a 32-bit integer string",
                    )
                if type(arrival["count"]) is not int or arrival["count"] <= 0:
                    raise P1MEMachineError(
                        f"{arrival_context}: count must be positive",
                    )
                arrival["address"] = hex(address)
            trial_names.add(name)
            normalized.append({
                **row,
                "stop_after_arrivals": arrivals,
                "events": _validate_events(row["events"], f"{item_context}.events", expand=expand),
                "checks": _validate_checks(row["checks"], f"{item_context}.checks"),
            })
        else:
            raise P1MEMachineError(f"{item_context}: unsupported step kind")
    if steps and (not checkpoints or not trial_names):
        raise P1MEMachineError(f"{context}: steps require a checkpoint and a trial")
    return normalized

def _validate_event_socket(value: Any, context: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise P1MEMachineError(f"{context}: expected an object")
    _require_keys(
        value,
        allowed={"host", "port", "ready_address", "ready_after_arrivals", "hold_when_ready"},
        required={"host", "port"},
        context=context,
    )
    if value["host"] not in {"127.0.0.1", "::1", "localhost"}:
        raise P1MEMachineError(f"{context}: host must be loopback")
    if type(value["port"]) is not int or not 0 < value["port"] <= 65535:
        raise P1MEMachineError(f"{context}: port must be in 1..65535")
    if "hold_when_ready" in value and type(value["hold_when_ready"]) is not bool:
        raise P1MEMachineError(f"{context}: hold_when_ready must be boolean")
    if "ready_address" in value:
        try:
            ready_address = int(value["ready_address"], 0)
        except (TypeError, ValueError) as exc:
            raise P1MEMachineError(
                f"{context}: ready_address must be a 32-bit integer string",
            ) from exc
        if not isinstance(value["ready_address"], str) or not 0 <= ready_address <= 0xFFFFFFFF:
            raise P1MEMachineError(
                f"{context}: ready_address must be a 32-bit integer string",
            )
    if "ready_after_arrivals" in value:
        if "ready_address" in value:
            raise P1MEMachineError(
                f"{context}: ready_address and ready_after_arrivals are mutually exclusive",
            )
        arrival = value["ready_after_arrivals"]
        if not isinstance(arrival, dict):
            raise P1MEMachineError(f"{context}.ready_after_arrivals: expected an object")
        _require_keys(
            arrival, allowed={"address", "count"}, required={"address", "count"},
            context=f"{context}.ready_after_arrivals",
        )
        try:
            arrival_address = int(arrival["address"], 0)
        except (TypeError, ValueError) as exc:
            raise P1MEMachineError(
                f"{context}.ready_after_arrivals.address must be a 32-bit integer string",
            ) from exc
        if (
            not isinstance(arrival["address"], str)
            or not 0 <= arrival_address <= 0xFFFFFFFF
            or type(arrival["count"]) is not int
            or arrival["count"] <= 0
        ):
            raise P1MEMachineError(
                f"{context}.ready_after_arrivals requires a 32-bit address and positive count",
            )
    return value


def _validate_reset_replay(
    value: Any, scenario_path: Path, *, expand: bool = True,
) -> dict[str, Any] | None:
    if value is None:
        return None
    context = f"{scenario_path}.reset_replay"
    if not isinstance(value, dict):
        raise P1MEMachineError(f"{context}: expected an object")
    _require_keys(value, allowed={"scenario"}, required={"scenario"}, context=context)
    source = value["scenario"]
    if not isinstance(source, str) or not source:
        raise P1MEMachineError(f"{context}.scenario: expected a nonempty path")
    fragment_path = (scenario_path.parent / source).resolve()
    fragment = _load_scenario(fragment_path, expand=expand)
    if fragment.get("reset_replay") is not None:
        raise P1MEMachineError(f"{context}: nested reset replay is unsupported")
    return {
        "scenario": str(fragment_path),
        "memory": fragment["memory"],
        "events": fragment["events"],
        "hsb_cycles_per_instruction": fragment["hsb_cycles_per_instruction"],
        "dataflash_cells": fragment["dataflash_cells"],
        "icus_startup_stub": fragment["icus_startup_stub"],
        "dma_master_rewrite_assumption": fragment["dma_master_rewrite_assumption"],
    }


def _validate_snapshot_outputs(
    rows: Any, context: str, base: Path,
) -> list[dict[str, Any]]:
    normalized = _require_list(rows, context)
    result: list[dict[str, Any]] = []
    for index, row in enumerate(normalized):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        _require_keys(
            row,
            allowed={"path", "address", "size", "evidence"},
            required={"path", "address", "size", "evidence"},
            context=item_context,
        )
        try:
            address = int(row["address"], 0)
        except (TypeError, ValueError) as exc:
            raise P1MEMachineError(f"{item_context}: address must be an integer string") from exc
        size = row["size"]
        if (
            not isinstance(row["address"], str)
            or type(size) is not int or size <= 0
            or not 0 <= address <= 0xFFFFFFFF
            or address + size > 0x100000000
        ):
            raise P1MEMachineError(f"{item_context}: snapshot range is outside 32-bit memory")
        if not isinstance(row["path"], str) or not row["path"]:
            raise P1MEMachineError(f"{item_context}: path must be a nonempty string")
        if not isinstance(row["evidence"], str) or not row["evidence"].strip():
            raise P1MEMachineError(f"{item_context}: evidence is required")
        result.append({
            **row,
            "address": hex(address),
            "path": str(_absolute_input(Path(row["path"]), base=base)),
        })
    return result


def load_scenario(path: Path) -> dict[str, Any]:
    return _load_scenario(path, expand=True)


def _load_scenario(path: Path, *, expand: bool) -> dict[str, Any]:
    scenario_path = _absolute_input(path)
    try:
        raw = json.loads(scenario_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise P1MEMachineError(f"cannot load scenario {scenario_path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise P1MEMachineError(f"{scenario_path}: scenario root must be an object")
    allowed = {
        "schema", "name", "source", "entry", "max_instructions", "reset",
        "stop_addresses", "gpr_fill", "registers", "memory", "pre_reset_memory",
        "artifacts", "checks", "expected_fault", "expected_termination", "events",
        "peripheral_file", "bounded_entries", "bounded_edges",
        "hsb_cycles_per_instruction", "dataflash_cells", "icus_startup_stub",
        "dma_master_rewrite_assumption", "steps", "compare_operands",
        "input_derived_table_indices", "reset_replay", "event_socket",
        "snapshot_outputs", "engine", "instruction_trace_start_step",
        "capture_rows", "capture_event_kinds",
    }
    required = {"schema", "name", "entry", "max_instructions", "stop_addresses", "checks"}
    _require_keys(raw, allowed=allowed, required=required, context=str(scenario_path))
    if raw["schema"] != SCENARIO_SCHEMA:
        raise P1MEMachineError(f"{scenario_path}: scenario schema drift")
    engine = raw.get("engine", os.environ.get("P1ME_MACHINE_ENGINE", "jit"))
    if engine not in ("plain", "jit"):
        raise P1MEMachineError(f"{scenario_path}: engine must be plain or jit")
    source = raw.get("source")
    if "source" in raw and not isinstance(source, dict):
        raise P1MEMachineError(f"{scenario_path}: source must be an object")
    if not isinstance(raw["max_instructions"], int) or raw["max_instructions"] <= 0:
        raise P1MEMachineError(f"{scenario_path}: max_instructions must be positive")
    registers = raw.get("registers", {})
    if not isinstance(registers, dict):
        raise P1MEMachineError(f"{scenario_path}: registers must be an object")
    if "gpr_fill" in raw:
        fill = raw["gpr_fill"]
        if not isinstance(fill, str):
            raise P1MEMachineError(f"{scenario_path}: gpr_fill must be an integer string")
        registers = {**dict.fromkeys(GPR_NAMES, fill), **registers}
    peripheral_file = raw.get("peripheral_file", False)
    if not isinstance(peripheral_file, bool):
        raise P1MEMachineError(f"{scenario_path}: peripheral_file must be a boolean")
    bounded_entries = raw.get("bounded_entries", [])
    if not isinstance(bounded_entries, list) or any(not isinstance(item, str) for item in bounded_entries):
        raise P1MEMachineError(f"{scenario_path}: bounded_entries must be a list of addresses")
    bounded_edges = raw.get("bounded_edges", [])
    if not isinstance(bounded_edges, list):
        raise P1MEMachineError(f"{scenario_path}: bounded_edges must be a list")
    for edge in bounded_edges:
        if (
            not isinstance(edge, dict)
            or set(edge) != {"pc", "target", "entry"}
            or any(not isinstance(edge[key], str) for key in ("pc", "target", "entry"))
        ):
            raise P1MEMachineError(f"{scenario_path}: bounded edge must name pc, target, and entry")
    expected_fault = raw.get("expected_fault")
    if expected_fault is not None:
        if not isinstance(expected_fault, dict):
            raise P1MEMachineError(f"{scenario_path}: expected_fault must be an object or null")
        _require_keys(
            expected_fault,
            allowed={"kind", "address", "access"},
            required=set(),
            context=f"{scenario_path}.expected_fault",
        )
    expected_termination = raw.get("expected_termination")
    if expected_termination is not None:
        if expected_termination not in ("halt", "stop-address", "instruction-budget"):
            raise P1MEMachineError(f"{scenario_path}: invalid expected_termination")
        if expected_fault is not None:
            raise P1MEMachineError(f"{scenario_path}: expected_fault and expected_termination are exclusive")
    hsb_quantum = raw.get("hsb_cycles_per_instruction")
    if hsb_quantum is not None and (
        type(hsb_quantum) is not int or not 0 < hsb_quantum <= 0x7FFFFFFFFFFFFFFF
    ):
        raise P1MEMachineError(
            f"{scenario_path}: hsb_cycles_per_instruction must be a positive signed-64 integer",
        )
    dma_rewrite = raw.get("dma_master_rewrite_assumption")
    if dma_rewrite is not None and (not isinstance(dma_rewrite, str) or not dma_rewrite.strip()):
        raise P1MEMachineError(
            f"{scenario_path}: dma_master_rewrite_assumption must be a nonempty evidence string",
        )
    for option in ("compare_operands", "input_derived_table_indices"):
        if option in raw and type(raw[option]) is not bool:
            raise P1MEMachineError(f"{scenario_path}: {option} must be boolean")
    if "capture_rows" in raw and type(raw["capture_rows"]) is not bool:
        raise P1MEMachineError(f"{scenario_path}: capture_rows must be boolean")
    if "capture_event_kinds" in raw:
        if "capture_rows" in raw:
            raise P1MEMachineError(
                f"{scenario_path}: capture_event_kinds and capture_rows are mutually exclusive",
            )
        kinds = _require_list(
            raw["capture_event_kinds"], f"{scenario_path}.capture_event_kinds",
        )
        if (
            any(not isinstance(kind, str) or not kind.strip() for kind in kinds)
            or len(set(kinds)) != len(kinds)
        ):
            raise P1MEMachineError(
                f"{scenario_path}: capture_event_kinds must contain unique nonempty strings",
            )
    steps = _validate_steps(
        raw.get("steps", []), f"{scenario_path}.steps", expand=expand,
    )
    trace_start_step = raw.get("instruction_trace_start_step")
    if "instruction_trace_start_step" in raw:
        if not isinstance(trace_start_step, str) or not trace_start_step.strip():
            raise P1MEMachineError(
                f"{scenario_path}: instruction_trace_start_step must be a nonempty step name",
            )
        matches = sum(
            step.get("kind") in ("checkpoint", "trial")
            and step.get("name") == trace_start_step
            for step in steps
        )
        if matches != 1:
            raise P1MEMachineError(
                f"{scenario_path}: instruction_trace_start_step must name exactly one "
                "checkpoint or trial step",
            )
    normalized = {
        "schema": raw["schema"],
        "name": raw["name"],
        "source": source,
        "engine": engine,
        "entry": _validate_entry(raw["entry"], f"{scenario_path}.entry"),
        "max_instructions": raw["max_instructions"],
        "reset": raw.get("reset", "none"),
        "stop_addresses": _require_list(raw["stop_addresses"], f"{scenario_path}.stop_addresses"),
        "registers": registers,
        "memory": _validate_memory_rows(raw.get("memory", []), f"{scenario_path}.memory"),
        "pre_reset_memory": _validate_memory_rows(
            raw.get("pre_reset_memory", []), f"{scenario_path}.pre_reset_memory",
        ),
        "artifacts": _validate_artifacts(
            raw.get("artifacts", []), f"{scenario_path}.artifacts", scenario_path.parent,
        ),
        "checks": _validate_checks(raw["checks"], f"{scenario_path}.checks"),
        "expected_fault": expected_fault,
        "expected_termination": expected_termination,
        "hsb_cycles_per_instruction": hsb_quantum,
        "dataflash_cells": _validate_dataflash_cells(
            raw.get("dataflash_cells", []), f"{scenario_path}.dataflash_cells",
        ),
        "icus_startup_stub": _validate_icus_startup_stub(
            raw.get("icus_startup_stub"), f"{scenario_path}.icus_startup_stub",
        ),
        "dma_master_rewrite_assumption": dma_rewrite,
        "events": _validate_events(raw.get("events", []), f"{scenario_path}.events", expand=expand),
        "steps": steps,
        "compare_operands": raw.get("compare_operands", False),
        "input_derived_table_indices": raw.get(
            "input_derived_table_indices", False,
        ),
        "reset_replay": _validate_reset_replay(raw.get("reset_replay"), scenario_path, expand=expand),
        "event_socket": _validate_event_socket(
            raw.get("event_socket"), f"{scenario_path}.event_socket",
        ),
        "snapshot_outputs": _validate_snapshot_outputs(
            raw.get("snapshot_outputs", []),
            f"{scenario_path}.snapshot_outputs",
            scenario_path.parent,
        ),
    }
    if "capture_rows" in raw:
        normalized["capture_rows"] = raw["capture_rows"]
    if "capture_event_kinds" in raw:
        normalized["capture_event_kinds"] = list(raw["capture_event_kinds"])
    if source is None:
        normalized.pop("source")
    if peripheral_file:
        normalized["peripheral_file"] = True
    if bounded_entries:
        normalized["bounded_entries"] = bounded_entries
    if bounded_edges:
        normalized["bounded_edges"] = bounded_edges
    if trace_start_step is not None:
        normalized["instruction_trace_start_step"] = trace_start_step
    return normalized


def _hex_base(value: int | str) -> str:
    return f"0x{(int(value, 0) if isinstance(value, str) else value):08X}"


def _target_contract(target_name: str) -> dict[str, Any]:
    resolved_name, target = resolve_target(target_name)
    codeflash = ROOT / target["codeflash"]
    if not codeflash.is_file():
        raise P1MEMachineError(f"registered CodeFlash is missing: {codeflash}")
    result: dict[str, Any] = {
        "name": resolved_name,
        "mcu": target["mcu"],
        "processor": target["processor"],
        "codeflash": {
            "path": str(codeflash),
            "sha256": target["codeflash_sha256"],
            "size": target["codeflash_size"],
            "base": _hex_base(target["codeflash_base"]),
        },
        "dataflash": None,
    }
    if target.get("dataflash"):
        dataflash = ROOT / target["dataflash"]
        if not dataflash.is_file():
            raise P1MEMachineError(f"registered DataFlash is missing: {dataflash}")
        result["dataflash"] = {
            "path": str(dataflash),
            "sha256": target["dataflash_sha256"],
            "size": target["dataflash_size"],
            "base": _hex_base(target["dataflash_base"]),
        }
    return result


def _load_model() -> tuple[dict[str, Any], str]:
    try:
        model = json.loads(MODEL.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise P1MEMachineError(f"cannot load generated machine model: {exc}") from exc
    if model.get("schema") != MODEL_SCHEMA:
        raise P1MEMachineError("generated machine model schema drift")
    return model, _sha256(MODEL)

def _write_drcov(
    report: dict[str, Any],
    target: dict[str, Any],
    output_path: Path,
) -> None:
    """Write unique entered instructions as DynamoRIO text basic blocks."""
    trace = report.get("instruction_trace")
    if not isinstance(trace, list):
        trials = report.get("checkpointing", {}).get("trials", [])
        trace = chain.from_iterable(trial.get("instruction_trace", []) for trial in trials)
    _write_drcov_instructions(_report_instructions(trace), target, output_path)


def _report_instructions(trace: Iterable[Any]) -> Iterator[tuple[int, int]]:
    for index, row in enumerate(trace):
        try:
            pc, size = int(row["pc"], 0), int(row["size"])
        except (KeyError, TypeError, ValueError) as exc:
            raise P1MEMachineError(
                f"instruction_trace[{index}]: expected pc and size",
            ) from exc
        yield pc, size


def _spooled_instructions(path: Path) -> Iterator[tuple[int, int]]:
    """Read the Java writer's big-endian uint32 PC and uint8 size records."""
    if path.is_file():
        pair = struct.Struct(">IB")
        with path.open("rb") as stream:
            while chunk := stream.read(pair.size * 16384):
                yield from pair.iter_unpack(chunk)


def _write_drcov_instructions(
    trace: Iterable[tuple[int, int]], target: dict[str, Any], output_path: Path,
) -> None:
    module = target["codeflash"]
    base = int(module["base"], 0)
    end = base + module["size"]
    module_path = Path(module["path"]).resolve()
    module_name = module_path.relative_to(ROOT)
    seen: dict[int, int] = {}
    for index, (pc, size) in enumerate(trace):
        if not base <= pc or pc + size > end:
            raise P1MEMachineError(
                f"instruction_trace[{index}]: instruction outside registered CodeFlash",
            )
        if not 0 < size <= 0xFFFF:
            raise P1MEMachineError(
                f"instruction_trace[{index}]: size outside drcov uint16 range",
            )
        prior_size = seen.setdefault(pc, size)
        if prior_size != size:
            raise P1MEMachineError(
                f"instruction_trace[{index}]: conflicting size at {pc:#x}",
            )
    if not seen:
        raise P1MEMachineError("instruction trace requested but absent from machine report")

    lines = [
        "DRCOV VERSION: 3",
        "DRCOV FLAVOR: drcov",
        "Module Table: version 5, count 1",
        "Columns: id, containing_id, start, end, entry, offset, preferred_base, path",
        (
            f"{0:3d}, {0:3d}, 0x{base:016x}, 0x{end:016x}, "
            f"0x{0:016x}, 0x{0:016x}, 0x{base:016x},  {module_name}"
        ),
        f"BB Table: {len(seen)} bbs",
        "module id, start, size:",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output:
        output.write("\n".join(lines) + "\n")
        output.writelines(
            f"module[{0:3d}]: 0x{pc - base:016x}, {size:3d}\n" for pc, size in seen.items()
        )


def _failure_summary(report: dict[str, Any]) -> str:
    scenario = report.get("scenario", "<unknown>")
    pieces = [f"{scenario}: {report.get('termination_reason', 'failed')}"]
    if error := report.get("error"):
        pieces.append(f"{error.get('type')}: {error.get('detail')}")
    if fault := report.get("fault"):
        pieces.append(
            f"fault={fault.get('kind')} pc={fault.get('pc')} address={fault.get('address')}"
        )
    failed_check = next(
        (row for row in report.get("checks", []) if not row.get("passed")), None,
    )
    if failed_check:
        pieces.append(
            f"check={failed_check.get('name')} expected={failed_check.get('expected')} "
            f"actual={failed_check.get('actual')}"
        )
    if recent := report.get("recent_pcs"):
        pieces.append("recent_pcs=" + ",".join(recent))
    return "; ".join(pieces)


def _machine_command(target: str, contract_path: Path, batch_report: Path) -> list[str]:
    return [
        str(ROOT / "tools" / "gtarget"), target,
        "script", "run", str(SCRIPT), "--",
        str(contract_path),
        str(batch_report),
    ]


def _execute(
    target_name: str,
    scenario_paths: Sequence[Path],
    *,
    instruction_trace: bool = False,
    report_outputs: Sequence[dict[str, str]] | None = None,
) -> dict[str, Any]:
    if not scenario_paths:
        raise P1MEMachineError("at least one scenario is required")
    target = _target_contract(target_name)
    model, model_sha = _load_model()
    products = {row["product_id"] for row in model["products"]}
    if target["mcu"] not in products:
        raise P1MEMachineError(f"machine model does not describe MCU {target['mcu']}")
    scenarios = [_load_scenario(path, expand=False) for path in scenario_paths]
    names = [scenario["name"] for scenario in scenarios]
    if len(names) != len(set(names)):
        raise P1MEMachineError("scenario names must be unique within one batch")
    contract = {
        "schema": CONTRACT_SCHEMA,
        "target": target,
        "model_path": str(MODEL),
        "model_sha256": model_sha,
        "scenarios": scenarios,
    }
    with tempfile.TemporaryDirectory(prefix="p1me-machine-", dir=ROOT / "build" / "tmp") as tmp:
        tmp_path = Path(tmp)
        contract_path = tmp_path / "run-contract.json"
        batch_report_path = tmp_path / "batch-report.json"
        contract_path.write_text(json.dumps(contract, separators=(",", ":")), encoding="utf-8")
        command = _machine_command(target_name, contract_path, batch_report_path)
        environment = os.environ.copy()
        environment.setdefault("GHIDRA_CLI_READ_TIMEOUT", "0")
        if any(scenario["engine"] == "jit" for scenario in scenarios):
            # Extra HotSpot compiler threads for the Java-side paths (interpreted p-code,
            # row capture, device scheduling); explicit caller settings stay last so they
            # still take precedence.
            options = environment.get("GHIDRA_HEADLESS_JAVA_OPTIONS", "")
            environment["GHIDRA_HEADLESS_JAVA_OPTIONS"] = (
                f"-XX:CICompilerCount=4 {options}".rstrip()
            )
        if instruction_trace:
            command.append("--instruction-trace")
        if report_outputs is not None:
            outputs_path = tmp_path / "report-outputs.json"
            outputs_path.write_text(json.dumps(report_outputs), encoding="utf-8")
            command.extend(["--report-outputs", str(outputs_path)])
        proc = subprocess.run(
            command, cwd=ROOT, env=environment, text=True, capture_output=True, check=False,
        )
        if not batch_report_path.is_file():
            message = f"P1M-E machine runner failed before reporting (exit {proc.returncode})."
            if "script_compile_failed" in proc.stdout or "script_compile_failed" in proc.stderr:
                check = shlex.join([
                    str(ROOT / "tools" / "gtarget"), target_name, "script", "check", str(SCRIPT),
                ])
                message += (
                    "\nGhidra could not compile or load the machine script; no scenario ran."
                    "\nCheck the bridge's access to the script sources and OSGi cache, then run "
                    f"this compile-only diagnostic: {check}"
                )
            raise P1MEMachineError(
                f"{message}\n--- Ghidra stdout ---\n{proc.stdout}"
                f"\n--- Ghidra stderr ---\n{proc.stderr}"
            )
        with batch_report_path.open(encoding="utf-8") as stream:
            batch = json.load(stream)
    expected_schema = (
        "rh850-p1me-machine-report-manifest-v1"
        if report_outputs is not None else "rh850-p1me-machine-batch-report-v1"
    )
    if batch.get("schema") != expected_schema:
        raise P1MEMachineError("P1M-E machine batch report schema drift")
    return batch


def _spool_reports(
    target: str,
    scenarios: Sequence[Path],
    output_dir: Path,
    *,
    instruction_trace: bool = False,
) -> list[tuple[Path, dict[str, Any]]]:
    output_dir = _absolute_input(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [_absolute_input(path) for path in scenarios]
    names = [path.stem for path in paths]
    if len(names) != len(set(names)):
        raise P1MEMachineError("scenario filenames must have unique stems")
    report_paths = [output_dir / f"{name}.report.json" for name in names]
    target_contract = _target_contract(target) if instruction_trace else None
    trace_paths = [output_dir / f".{name}.instructions.bin" for name in names]
    drcov_paths = [output_dir / f"{name}.drcov" for name in names]
    outputs: list[dict[str, str]] = []
    for index, report_path in enumerate(report_paths):
        report_path.unlink(missing_ok=True)
        row = {"report": str(report_path)}
        if instruction_trace:
            trace_paths[index].unlink(missing_ok=True)
            drcov_paths[index].unlink(missing_ok=True)
            row["instruction_spool"] = str(trace_paths[index])
            row["drcov_path"] = str(drcov_paths[index])
        outputs.append(row)

    try:
        manifest = _execute(
            target,
            paths,
            instruction_trace=instruction_trace,
            report_outputs=outputs,
        )
        verdicts = manifest.get("reports")
        if not isinstance(verdicts, list) or len(verdicts) != len(paths):
            raise P1MEMachineError("machine report manifest does not match requested scenarios")

        completed = []
        for index, (report_path, verdict) in enumerate(
            zip(report_paths, verdicts, strict=True),
        ):
            if not report_path.is_file():
                raise P1MEMachineError(
                    f"machine did not spool completed trial report: {report_path}",
                )
            if not isinstance(verdict, dict) or not isinstance(verdict.get("passed"), bool):
                raise P1MEMachineError(f"invalid machine verdict: {report_path}")
            if instruction_trace:
                assert target_contract is not None
                _write_drcov_instructions(
                    _spooled_instructions(trace_paths[index]),
                    target_contract,
                    drcov_paths[index],
                )
            completed.append((report_path, verdict))
        return completed
    finally:
        for trace_path in trace_paths:
            trace_path.unlink(missing_ok=True)


def capture_many(
    target: str,
    scenarios: Sequence[Path],
    output_dir: Path,
    *,
    instruction_trace: bool = False,
) -> list[dict[str, Any]]:
    reports = []
    for path, verdict in _spool_reports(target, scenarios, output_dir, instruction_trace=instruction_trace):
        with path.open(encoding="utf-8") as stream:
            report = json.load(stream)
        if report.get("passed") != verdict["passed"]:
            raise P1MEMachineError(f"machine verdict disagrees with trial report: {path}")
        report["report_path"] = str(path)
        reports.append(report)
    return reports


def run_many(
    target_name: str,
    scenario_paths: Sequence[Path],
    output_dir: Path,
    *,
    instruction_trace: bool = False,
) -> list[dict[str, Any]]:
    reports = capture_many(
        target_name,
        scenario_paths,
        output_dir,
        instruction_trace=instruction_trace,
    )
    failures = [report for report in reports if not report.get("passed")]
    if failures:
        raise P1MEMachineError("; ".join(_failure_summary(report) for report in failures))
    return reports


def run(
    target_name: str,
    scenario_path: Path,
    report_path: Path,
    *,
    instruction_trace: bool = False,
) -> dict[str, Any]:
    batch = _execute(
        target_name, [scenario_path],
        instruction_trace=instruction_trace,
    )
    report = batch["reports"][0]
    report_path = _absolute_input(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if instruction_trace:
        drcov_path = report_path.with_name(f"{Path(scenario_path).stem}.drcov")
        _write_drcov(report, _target_contract(target_name), drcov_path)
        report["drcov_path"] = str(drcov_path)
    with report_path.open("w", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
        output.write("\n")
    report["report_path"] = str(report_path)
    if not report.get("passed"):
        raise P1MEMachineError(_failure_summary(report))
    return report


def _run_cli(
    target: str,
    scenarios: Sequence[Path],
    output_dir: Path,
    *,
    instruction_trace: bool = False,
) -> list[Path]:
    completed = _spool_reports(target, scenarios, output_dir, instruction_trace=instruction_trace)
    failures = [f"{path}: {_failure_summary(verdict)}" for path, verdict in completed if not verdict["passed"]]
    if failures:
        raise P1MEMachineError("; ".join(failures))
    return [path for path, _ in completed]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target")
    parser.add_argument("scenarios", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--instruction-trace",
        action="store_true",
        help="include every entered (pc, size) instruction and write one drcov file per scenario",
    )
    args = parser.parse_args()
    try:
        reports = _run_cli(
            args.target,
            args.scenarios,
            args.output_dir,
            instruction_trace=args.instruction_trace,
        )
    except P1MEMachineError as exc:
        parser.error(str(exc))
    print(json.dumps({"reports": [str(path) for path in reports]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
