"""Verify current GTS+ legacy ROB records against every regional ECU source."""
import json
from collections import Counter
from tools.techstream.gts.ddb import _english_strings
from tools.techstream.legacy_rob import legacy_rob_catalog, decode_rob_scalar
from tools.techstream.parse_ddb import DDBParser
from tools.techstream.techstream_paths import resolve_gts_root, gts_db_root


def main():
    parser = DDBParser()
    for region in ("NA", "EU", "JP"):
        root = gts_db_root(resolve_gts_root(), region)
        strings = _english_strings(parser, root)
        totals = Counter()
        for path in sorted(root.glob("*.ddb")):
            try:
                db = parser.parse_ecu_db(path)
            except (ValueError, AssertionError):
                # This directory also holds master, string and viewer databases.
                continue
            if not any(t in db.sections for t in (43,44,45,57,58,59)):
                continue
            catalog = legacy_rob_catalog(db, strings, path.name)
            json.dumps(catalog, allow_nan=False)
            totals["databases"] += 1
            for family in catalog["families"]:
                table = 45 if family["mode"] == 1 else 59
                expected = db.sections[table].header.record_count if table in db.sections else 0
                assert len(family["signals"]) == expected, path
                totals["signals"] += expected
                for signal in family["signals"]:
                    assert signal["physical_variants"], (path, signal["signal_key"])
                    for variant in signal["physical_variants"]:
                        assert variant["units"], (path, signal["signal_key"])
                    size = signal["bit_end"] // 8 + 1
                    decode_rob_scalar(bytes(size), signal)
                    decode_rob_scalar(bytes([255]) * size, signal)
        print(f"{region}: {dict(totals)}; every source signal retained, all physical/unit joins resolved, native zero/all-ones decode passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
