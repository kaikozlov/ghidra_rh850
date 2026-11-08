"""Regression: native non-P6 runtime selection must not omit table164 source.

These seven catalogs previously lost every table164 record because source
projection was gated by runtime family. Validate against their actual selected
source, not a guessed Gen path, including byte-for-byte record provenance.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from tools.techstream.diag_bundle import DiagnosticBundle
from tools.techstream.parse_ddb import DDBParser
from tools.techstream.ddb_semantics import records

REGRESSIONS = (("NA",930),("NA",6020),("EU",930),("EU",6020),
               ("JP",930),("JP",6020),("JP",6066))

def verify(bundle, gts_root):
    parser = DDBParser()
    total = 0
    for region, category in REGRESSIONS:
        name = f"catalogs/{region}/{category}.json"
        catalog = bundle.json(name)
        db = parser.parse_ecu_db(gts_root / catalog["source_identity"]["database"]["path"])
        expected = list(records(db.sections[164]))
        actual = catalog["p6_rob_source"]["signals"]
        assert expected, name
        assert [row["record"] for row in actual] == list(range(len(expected))), name
        assert all(row["table"] == 164 for row in actual), name
        assert [bytes.fromhex(row["raw"]) for row in actual] == expected, name
        assert all("did" in row and "physical_data_key" in row for row in actual), name
        total += len(actual)
    return total

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle",type=Path)
    parser.add_argument("--gts-root",type=Path,required=True)
    args = parser.parse_args()
    total = verify(DiagnosticBundle(args.bundle),args.gts_root)
    print(f"PASS: all 7 formerly omitted selected catalogs retain {total} table164 source rows")

if __name__ == "__main__":
    main()
