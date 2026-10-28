#!/usr/bin/env python3
"""Reproduce the bounded disposition of malformed-CMAC and command-8 leads."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"


class ClosureError(RuntimeError):
    pass


@dataclass(frozen=True)
class CmacWalk:
    length: int
    endpoint_offset_u32: int
    terminates: bool
    first_oob_block_offset: int | None


def model_cmac_walk(length: int) -> CmacWalk:
    if not 1 <= length <= 0x1000:
        raise ClosureError("modeled authenticated length must be within the 4 KiB RAM window")
    endpoint = (length - 16) & 0xFFFFFFFF
    terminates = length >= 16 and length % 16 == 0
    first_oob = None if terminates else (length // 16) * 16
    return CmacWalk(length, endpoint, terminates, first_oob)


def command8_failure_clear_length(output_capacity: int) -> int:
    if output_capacity < 48 or output_capacity > 0xFFFFFFFF:
        raise ClosureError("command-8 prepare accepts only capacities >=48 in uint32")
    return output_capacity


def _exact(image: bytes, address: int, value: str) -> bool:
    expected = bytes.fromhex(value)
    return image[address : address + len(expected)] == expected


def firmware_closure(image: bytes) -> dict:
    if len(image) != 0x100000:
        raise ClosureError("closure requires an exact 1 MiB CodeFlash image")
    cmac = {
        "endpoint_arithmetic": _exact(image, 0x715C, "64e7b198dce950ea0ad864efa998"),
        "increment_16": _exact(image, 0x717E, "06e61000"),
        "endpoint_equality_only": _exact(image, 0x7182, "e131f205e1e1ea05"),
        "sole_direct_callee_is_cmac": (
            image[0x7170:0x71EE].count(bytes.fromhex("80ff5c0c")) == 1
            and image[0x7170:0x71EE].count(bytes.fromhex("80ff")) == 1
        ),
    }
    command8 = {
        "prepare_requires_64_input_and_capacity_48": (
            _exact(image, 0x86E78, "0706c0ffb205")
            and _exact(image, 0x86E82, "23f71100000d0106d0ffe30712db")
        ),
        "failure_uses_original_capacity_for_zero_fill": (
            _exact(image, 0x86EF8, "02ed00dd")
            and _exact(image, 0x86F20, "1d30e0e1ea15")
            and _exact(image, 0x86F50, "3b3f010080fff020")
        ),
        "configured_caller_fixes_48_output_64_input": (
            _exact(image, 0x6825C, "200e30001d38640f5998")
            and _exact(image, 0x6827A, "204640000648")
            and _exact(image, 0x68284, "240e5898030d82ffac06")
        ),
        "driver_dispatch_call_is_unique": (
            image.count(bytes.fromhex("82ffac06")) == 1
            and _exact(image, 0x6828A, "82ffac06")
        ),
    }
    if not all(cmac.values()) or not all(command8.values()):
        raise ClosureError("image does not satisfy the Sienna static closure propositions")
    walks = [model_cmac_walk(length) for length in range(1, 0x1001)]
    return {
        "schema": "sienna-static-followup-closure-v1",
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "malformed_cmac": {
            "firmware_propositions": cmac,
            "length_census_1_to_0x1000": {
                "terminating": sum(item.terminates for item in walks),
                "nonterminating_oob": sum(not item.terminates for item in walks),
            },
            "boundary_models": [asdict(model_cmac_walk(length)) for length in (1, 15, 16, 17, 0x1000)],
            "disposition": "availability-only-bounded-negative",
            "live_probe": "not_implemented",
            "reason": (
                "the malformed walk never reaches tag comparison, the exact step body has no "
                "response-buffer consumer, and a live probe adds hang/reset risk without an "
                "exfiltration or code-execution predicate"
            ),
            "reopen_on": "a concrete fault/timing side channel or new direct/indirect data consumer",
        },
        "command8": {
            "firmware_propositions": command8,
            "configured_output_capacity": 48,
            "configured_failure_clear_length": command8_failure_clear_length(48),
            "disposition": "latent-not-remotely-controllable-in-this-graph",
            "live_probe": "not_implemented",
            "reason": (
                "the sole configured dispatch fixes both pointer ownership and capacity 48; "
                "diagnostic input controls neither failure-clear argument"
            ),
            "reopen_on": (
                "a variant caller with capacity >48, or independent evidence of pointer/length "
                "corruption reaching the command-8 prepare API"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = firmware_closure(args.image.read_bytes())
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered)
        print(rendered, end="")
        return 0
    except (OSError, ClosureError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
