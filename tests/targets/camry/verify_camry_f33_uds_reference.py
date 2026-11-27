#!/usr/bin/env python3
"""Verify the pure Camry F33 UDS response classifier contract."""
from __future__ import annotations

from tools.targets.camry.research.compare_camry_f33_uds_reference import (
    classify_response,
    matrix_cases,
)


def main() -> None:
    wrong_nrc = classify_response(
        bytes.fromhex("7f2212"), bytes.fromhex("7f2213"), bytes.fromhex("22ffff")
    )
    nrc_against_positive = classify_response(
        bytes.fromhex("7f2231"), bytes.fromhex("622030"), bytes.fromhex("222030")
    )
    assert wrong_nrc == "b"
    assert nrc_against_positive == "c"
    assert classify_response(
        bytes.fromhex("7f2213"), bytes.fromhex("7f2213"), bytes.fromhex("2220")
    ) == "a"
    assert classify_response(
        bytes.fromhex("622030aabb"), bytes.fromhex("6220300000"), bytes.fromhex("222030")
    ) == "a"
    assert classify_response(
        bytes.fromhex("622030"), bytes.fromhex("62203000"), bytes.fromhex("222030")
    ) == "d"
    assert classify_response(None, bytes.fromhex("622030"), bytes.fromhex("222030")) == "e"

    cases = matrix_cases()
    assert len(cases) == 69
    assert len({(row.session, row.security, row.service) for row in cases}) == 23
    assert {row.service for row in cases} == {
        0x10, 0x14, 0x19, 0x22, 0x23, 0x27, 0x28, 0x2E, 0x31, 0x3E, 0x85,
    }
    assert all({row.variant for row in cases if row.service == sid} == {
        "valid", "truncated", "invalid",
    } for sid in {row.service for row in cases})
    print("camry F33 UDS reference classifier: 23 cells, 69 requests; b/c seeds pass")


if __name__ == "__main__":
    main()
