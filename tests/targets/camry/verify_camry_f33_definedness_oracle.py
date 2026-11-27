#!/usr/bin/env python3
"""Check that the D5 definedness collector preserves the first fault exactly."""
from collections import Counter

from tools.targets.camry.research.audit_camry_f33_definedness_boundaries import (
    _completed_isotp_messages,
    _trial_fault,
    ingress_cases,
    ingress_events,
)


def main() -> int:
    expected = {
        "kind": "uninitialized-read", "pc": "0x0004F9C6",
        "address": "0xFEBE5A23", "size": 1, "access": "read",
    }
    observed = _trial_fault({"fault": expected, "event_rows": []})
    assert observed == expected
    fallback = _trial_fault({"event_rows": [expected]})
    assert fallback == expected
    assert _trial_fault({"event_rows": []}) is None
    cases = ingress_cases()
    assert Counter(case.category for case in cases) == {
        "rdbi": 242,
        "wdbi": 26,
        "routine": 57,
        "transport-shape": 7,
    }
    shapes = Counter(f"{case.category}/{case.shape}" for case in cases)
    assert shapes == {
        "rdbi/valid": 242,
        "wdbi/valid": 13,
        "wdbi/overlong": 13,
        "routine/valid": 38,
        "routine/overlong": 19,
        "transport-shape/transport": 7,
    }
    by_name = {case.name: case for case in cases}
    assert len(by_name["shape-response-block-size-0"].response_flow_control) == 1
    assert len(by_name["shape-response-block-size-1"].response_flow_control) == 5
    assert len(by_name["shape-response-block-size-2"].response_flow_control) == 3
    assert by_name["wdbi-2012-valid"].frames == (bytes.fromhex("042e201201000000"),)
    assert by_name["wdbi-0204-valid"].frames == (bytes.fromhex("052e020400000000"),)
    assert by_name["routine-1004-start"].frames == (bytes.fromhex("0631011004ffff00"),)
    assert len(by_name["routine-1010-start"].frames) == 10
    assert by_name["routine-110a-results"].frames == (bytes.fromhex("043102110a000000"),)
    assert "routine-100e-stop" not in by_name
    extended_events = ingress_events(by_name["wdbi-0204-long"])
    assert any(
        row["kind"] == "can-rx"
        and row["after_instructions"] == 1_850_000
        for row in extended_events
    )
    messages = _completed_isotp_messages([
        {"kind": "can-tx", "can_id": "0x7a9", "data_hex": "100b62f181010203"},
        {"kind": "can-tx", "can_id": "0x7a9", "data_hex": "2104050607080000"},
    ])
    assert messages == [{
        "complete": True,
        "declared_length": 11,
        "payload_hex": "62f1810102030405060708",
        "frames": ["100b62f181010203", "2104050607080000"],
    }]
    print("camry F33 definedness oracle check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
