#!/usr/bin/env python3
"""Check D5 store/extent boundary arithmetic."""
from tools.targets.camry.research.audit_camry_f33_definedness_boundaries import (
    Extent,
    Store,
    crossing_stores,
)


def main() -> int:
    extent = Extent(0x1000, 0x10, "seeded_object", "synthetic")
    in_bounds = Store(0x200, 0x100C, 4)
    assert crossing_stores([in_bounds], [extent]) == []
    end_rows = crossing_stores([Store(0x204, 0x100F, 2)], [extent])
    assert len(end_rows) == 1 and end_rows[0]["crossed_edge"] == "end"
    start_rows = crossing_stores([Store(0x202, 0x0FFF, 2)], [extent])
    assert len(start_rows) == 1 and start_rows[0]["crossed_edge"] == "start"
    # A store beginning at an object's end may belong to an adjacent object;
    # without pointer provenance it is not a crossing of this extent.
    assert crossing_stores([Store(0x206, 0x1010, 1)], [extent]) == []
    print("camry F33 object-boundary oracle check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
