#!/usr/bin/env python3
"""Native P3/P4 framing and compact-byte expansion regression vectors."""
from tools.techstream.gts.legacy_pid import expand_p4_pid, legacy_pid_request, decode_legacy_pid_response

assert expand_p4_pid(bytes.fromhex("1234"), bytes.fromhex("ff0001")) == bytes.fromhex("120034")
assert expand_p4_pid(bytes.fromhex("1234"), bytes.fromhex("0001ff")) == bytes.fromhex("001234")
# Native ignores trailing received bytes when the support cache consumes fewer.
assert expand_p4_pid(bytes.fromhex("1234"), bytes.fromhex("0100")) == bytes.fromhex("1200")
for compact, support in [(b"", b"\xff"), (b"\x01\x02", b"\xff"), (b"\x01", b"\xff\xff")]:
    try:
        expand_p4_pid(compact, support)
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe compact payload accepted")
row = {"pid": 5, "bit_start": 8, "bit_end": 15, "data_type": 1,
       "physical_records": [{"bit_width": 8, "sign_mode": 0, "mul": 1, "div": 1,
                            "offset": -40, "decimal_point_count": 0, "patterns": []}]}
request = legacy_pid_request(row, bytes.fromhex("2100"))
assert request == bytes.fromhex("2105")
p3 = decode_legacy_pid_response(row, bytes.fromhex("61050064"), request, protocol="p3")
assert p3["raw"] == 100 and p3["converted_integer"] == 60
p4 = decode_legacy_pid_response(row, bytes.fromhex("610564"), request, protocol="p4", support=bytes.fromhex("00ff"))
assert p4["raw"] == 100 and p4["converted_integer"] == 60
assert p4["payload"] == "0064"
for kwargs in [
    {"protocol": "p4"}, {"protocol": "p3", "support": b"\xff"},
    {"protocol": "uds"}, {"protocol": "p4", "support": b"\xff"},
]:
    try:
        decode_legacy_pid_response(row, bytes.fromhex("610564"), request, **kwargs)
    except ValueError:
        pass
    else:
        raise AssertionError("incompatible response geometry accepted")
print("[PASS] native PID frame patching, P3 payload offset, P4 byte expansion and scalar conversion")
