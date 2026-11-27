#!/usr/bin/env python3
"""Check D5 stack-watermark arithmetic on a synthetic traced adjustment."""
from tools.targets.camry.research.audit_camry_f33_definedness_boundaries import stack_watermark


def main() -> int:
    image = bytes.fromhex("031ec0ff031e4000")
    trace = [
        {"pc": "0x0", "size": 4, "instruction": 0},
        {"pc": "0x4", "size": 4, "instruction": 1},
    ]
    row = stack_watermark(trace, image, 0xFEBE2000)
    assert row.lowest_sp == 0xFEBE1FC0
    assert row.widest_use == 64
    assert row.margin_to_lower_edge == 0x7C0
    assert not row.finding
    print("camry F33 stack-watermark oracle check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
