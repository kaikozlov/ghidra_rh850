#!/usr/bin/env python3
"""Parse Toyota Techstream ``ptshim32`` SaveLog output.

The V18 distribution carries two relevant shim formats:

* v04.04: PTWriteMsgs and no per-message handle;
* v05.00: PTQueueMsgs and a decimal handle in each message header.

Both formats are line-oriented.  This parser deliberately preserves the raw
API arguments and unparsed lines while normalizing the fields needed for
diagnostic-traffic analysis.  It accepts the CRT UTF-8 output as well as
UTF-16LE ring dumps encountered when logs are recovered before text-mode CRT
conversion.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


API_RE = re.compile(
    r"^(?P<elapsed>\d+(?:\.\d+)?)s\s+"
    r"(?P<marker><<|>>|\+\+)\s+"
    r"PT(?P<api>[A-Za-z0-9_]+)\((?P<args>.*)\)\s*$"
)
TX_RE = re.compile(
    r"^\s*(?P<label>.+?)\[\s*(?P<index>\d+)\]\s+"
    r"(?P<protocol>[^.]+)\.\s+"
    r"(?:(?P<handle>\d+)\s+Handle,\s+)?"
    r"(?P<size>\d+)\s+bytes\.\s+TxF=0x(?P<flags>[0-9A-Fa-f]+)\s*$"
)
RX_RE = re.compile(
    r"^\s*(?P<label>.+?)\[\s*(?P<index>\d+)\]\s+"
    r"(?P<timestamp>\d+(?:\.\d+)?)s\.\s+"
    r"(?P<protocol>[^.]+)\.\s+"
    r"(?:(?P<handle>\d+)\s+Handle,\s+)?"
    r"Actual data\s+(?P<actual>\d+)\s+of\s+(?P<size>\d+)\s+bytes\.\s+"
    r"RxS=0x(?P<flags>[0-9A-Fa-f]+)\s*$"
)
SUMMARY_RE = re.compile(
    r"^\s*(?P<verb>read|sent|queued)\s+"
    r"(?P<count>\d+)\s+of\s+(?P<requested>\d+)\s+messages\s*$",
    re.IGNORECASE,
)
STATUS_RE = re.compile(
    r"^\s*(?P<elapsed>\d+(?:\.\d+)?)s\s+(?P<status>\S.*)\s*$"
)
HEX_PAIR_RE = re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{2}(?![0-9a-f])")


def decode_log(data: bytes) -> tuple[str, str]:
    """Decode a saved log and return ``(text, detected_encoding)``."""

    if data.startswith(b"\xff\xfe"):
        return data.decode("utf-16"), "utf-16-le-bom"
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig"), "utf-8-bom"

    sample = data[: min(len(data), 4096)]
    odd_nuls = sample[1::2].count(0)
    pairs = max(1, len(sample) // 2)
    if odd_nuls / pairs > 0.35:
        return data.decode("utf-16-le"), "utf-16-le"
    return data.decode("utf-8"), "utf-8"


def _split_args(arguments: str) -> list[str]:
    # The logged J2534 calls use scalar/pointer arguments and do not contain
    # commas inside nested expressions.
    return [part.strip() for part in arguments.split(",")] if arguments else []


def _channel_id(api: str, args: list[str]) -> int | None:
    if api not in {"ReadMsgs", "WriteMsgs", "QueueMsgs"} or not args:
        return None
    try:
        return int(args[0], 0)
    except ValueError:
        return None


def _new_message(match: re.Match[str], direction: str) -> dict[str, Any]:
    values = match.groupdict()
    protocol = values["protocol"].strip()
    result: dict[str, Any] = {
        "direction": direction,
        "label": values["label"].strip(),
        "index": int(values["index"]),
        "protocol": protocol,
        "handle": int(values["handle"]) if values.get("handle") else None,
        "message_timestamp_seconds": (
            float(values["timestamp"]) if values.get("timestamp") else None
        ),
        "data_size": int(values["size"]),
        "actual_data_size": (
            int(values["actual"]) if values.get("actual") else int(values["size"])
        ),
        "flags": int(values["flags"], 16),
        "flag_names": [],
        "data_hex": None,
        "address_hex": None,
        "extra_data_hex": None,
    }
    return result


def _raw_bytes(line: str) -> bytes | None:
    if r"\__" not in line:
        return None
    raw = line.split(r"\__", 1)[1]
    # Some releases concatenate bytes; others separate them with spaces.
    compact = re.sub(r"[^0-9A-Fa-f]", "", raw)
    if compact and len(compact) % 2 == 0:
        return bytes.fromhex(compact)
    pairs = HEX_PAIR_RE.findall(raw)
    return bytes.fromhex("".join(pairs)) if pairs else b""


def parse_text(text: str, encoding: str = "text") -> dict[str, Any]:
    """Parse decoded log text into normalized API-call records."""

    calls: list[dict[str, Any]] = []
    preamble: list[str] = []
    current: dict[str, Any] | None = None
    pending_message: dict[str, Any] | None = None

    def finish_message() -> None:
        nonlocal pending_message
        if pending_message is not None and current is not None:
            current["messages"].append(pending_message)
        pending_message = None

    def finish_call() -> None:
        nonlocal current
        finish_message()
        if current is not None:
            calls.append(current)
        current = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\r")
        api_match = API_RE.match(line)
        if api_match:
            finish_call()
            args = _split_args(api_match["args"])
            current = {
                "api": api_match["api"],
                "api_marker": api_match["marker"],
                "call_elapsed_seconds": float(api_match["elapsed"]),
                "channel_id": _channel_id(api_match["api"], args),
                "arguments": args,
                "summary": None,
                "status": None,
                "status_elapsed_seconds": None,
                "messages": [],
                "unparsed_lines": [],
            }
            continue

        if current is None:
            if line:
                preamble.append(line)
            continue

        message_match = RX_RE.match(line)
        if message_match is not None:
            finish_message()
            pending_message = _new_message(message_match, "rx")
            continue
        message_match = TX_RE.match(line)
        if message_match is not None:
            finish_message()
            pending_message = _new_message(message_match, "tx")
            continue

        if pending_message is not None:
            data = _raw_bytes(line)
            if data is not None:
                pending_message["data_hex"] = data.hex()
                actual = min(pending_message["actual_data_size"], len(data))
                pending_message["extra_data_hex"] = data[actual:].hex()
                if pending_message["protocol"].upper() in {"CAN", "ISO15765"}:
                    pending_message["address_hex"] = data[:4].hex() if len(data) >= 4 else None
                finish_message()
                continue
            stripped = line.strip()
            if stripped.startswith(("RxStatus:", "TxFlags:", "Flags:")):
                _, _, names = stripped.partition(":")
                pending_message["flag_names"] = [
                    name.strip() for name in re.split(r"[,|]", names) if name.strip()
                ]
                continue

        summary_match = SUMMARY_RE.match(line)
        if summary_match:
            current["summary"] = {
                "verb": summary_match["verb"].lower(),
                "count": int(summary_match["count"]),
                "requested": int(summary_match["requested"]),
            }
            continue

        status_match = STATUS_RE.match(line)
        if status_match:
            current["status_elapsed_seconds"] = float(status_match["elapsed"])
            current["status"] = status_match["status"]
            continue

        if line:
            current["unparsed_lines"].append(line)

    finish_call()
    return {"encoding": encoding, "record_delimiter": "newline", "preamble": preamble, "calls": calls}


def parse_bytes(data: bytes) -> dict[str, Any]:
    text, encoding = decode_log(data)
    return parse_text(text, encoding)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path, help="ptshim SaveLog file")
    parser.add_argument("-o", "--output", type=Path, help="write JSON here")
    args = parser.parse_args()

    result = parse_bytes(args.log.read_bytes())
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
