#!/usr/bin/env python3
"""Verify the recovered ptshim32 log formats and parser."""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools/techstream"))
from parse_ptshim_log import parse_bytes  # noqa: E402

FIXTURES = REPO / "tests/fixtures/techstream"
BIN = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/bin"
J2534_CTRL = BIN / "J2534Ctrl.dll"

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


print("== synthetic cross-version parser fixtures ==")
v4 = parse_bytes((FIXTURES / "ptshim_v0404_sample.log").read_bytes())
check("v04 fixture detected as UTF-8", v4["encoding"] == "utf-8")
check("v04 parser recovers two API calls", len(v4["calls"]) == 2)
v4_tx, v4_rx = v4["calls"]
check("v04 PTWriteMsgs channel and direction",
      v4_tx["api"] == "WriteMsgs" and v4_tx["channel_id"] == 7
      and v4_tx["messages"][0]["direction"] == "tx")
check("v04 transmit address and flags",
      v4_tx["messages"][0]["address_hex"] == "000007e0"
      and v4_tx["messages"][0]["flags"] == 0x40
      and v4_tx["messages"][0]["flag_names"] == ["ISO15765_FRAME_PAD"])
check("v04 receive timestamp, actual length, and extra byte",
      v4_rx["messages"][0]["message_timestamp_seconds"] == 12.345678
      and v4_rx["messages"][0]["actual_data_size"] == 7
      and v4_rx["messages"][0]["extra_data_hex"] == "ff")
check("v04 status and read summary",
      v4_rx["status"] == "ERR_TIMEOUT"
      and v4_rx["summary"] == {"verb": "read", "count": 1, "requested": 1})

v5_bytes = (FIXTURES / "ptshim_v0500_sample.log").read_bytes()
v5 = parse_bytes(b"\xff\xfe" + v5_bytes.decode().encode("utf-16-le"))
check("v05 fixture detected as BOM UTF-16LE", v5["encoding"] == "utf-16-le-bom")
check("v05 PTQueueMsgs and ChannelID recovered",
      v5["calls"][0]["api"] == "QueueMsgs" and v5["calls"][0]["channel_id"] == 11)
check("v05 per-message handle recovered",
      all(call["messages"][0]["handle"] == 42 for call in v5["calls"]))
check("v05 CAN/ISO15765 address bytes recovered",
      [call["messages"][0]["address_hex"] for call in v5["calls"]]
      == ["000007df", "000007e8"])
check("v05 receive extra data boundary recovered",
      v5["calls"][1]["messages"][0]["extra_data_hex"] == "0200")


print("\n== pinned shim binaries ==")
v4_path = BIN / "ptshim32.dll"
v5_path = BIN / "ptshim32_0500.dll"
if os.environ.get("RH850_VERIFY_EXTERNAL") != "1":
    print("SKIP: optional ignored Techstream binary checks are disabled for portable verification")
elif not v4_path.exists() or not v5_path.exists() or not J2534_CTRL.exists():
    print("SKIP: ignored Techstream tree is not present; parser fixtures still verified")
else:
    expected_files = {
        v4_path: "c8d960e84981d761981706e85004ab31dc8263cea740c9afd5bc47dfdadafb8a",
        v5_path: "e6e56a20763e03eddaf7f868537738cf314705e3f27742244a6456fbc73f5202",
        J2534_CTRL: "aa371b09b28eeb9aca5c7d948829f94475c7606e70ef34852c77fbea547a8a7a",
    }
    for path, expected in expected_files.items():
        check(f"{path.name} SHA-256", sha256(path.read_bytes()) == expected)

    body_pins = {
        v4_path: {
            (0x10005A80, 989): "55dd800acf31cf1518758d8b8e7e38d2e9387c6eca994482b2a599259d425f7b",
            (0x10008E10, 377): "8edaf039a856ca30e821edd943b042b62fab002b8557df688dcf97445e785004",
            (0x1000B050, 115): "3e800b85fac114d4d93c8713d243c73138b5734eeb184b41a7f131f233d60bd9",
            (0x1000B2E0, 271): "ee987d7a38f713465248d57ebfe94b706316740f1a59c27b942dbc31a84c80f6",
            (0x1000B3F0, 157): "b192ef8ab8108fee3a02cc0f7a7582862372e40672b8fccfdb9e1ae57dcf09b2",
        },
        v5_path: {
            (0x10009970, 825): "b46288f015d7351e19bd2f00d3ec626d35aef174cb80e5987333172893bfd99d",
            (0x1000C210, 338): "a0c28f58b85e16192c05969e1fe2331a81a765e0adbcd04caf079e78832dbba4",
            (0x1000EF90, 144): "ea24f10c8f3cb48625eeed615123ce05eac5fd8cf7b9849fceb854377f43a625",
            (0x1000FFC0, 142): "54bd4ac1890d34c11f5d927d497ff96ca9a93bce2e6aeaf0507c5368cf6c964a",
        },
        J2534_CTRL: {
            (0x10008B9B, 168): "5a71bcc3687551d74d8e801768bf0194a05f66828a3eb72961356af59000595f",
            (0x10008C50, 105): "8b2c22af39b1f0710ff88c1b9a610f15437839219a71d02b1bd78609d5f17ab7",
        },
    }
    for path, functions in body_pins.items():
        pe = pefile.PE(str(path), fast_load=True)
        image_base = pe.OPTIONAL_HEADER.ImageBase
        for (address, size), expected in functions.items():
            body = pe.get_data(address - image_base, size)
            check(f"{path.name} body {address:#x}/{size}", sha256(body) == expected)

    v4_data = v4_path.read_bytes()
    v5_data = v5_path.read_bytes()
    def u16(value: str) -> bytes:
        return value.encode("utf-16-le")

    check("v04 SaveLog opens append UTF-8 mode", u16("a, ccs=UTF-8") in v4_data)
    check("v05 SaveLog opens overwrite UTF-8 mode", u16("w, ccs=UTF-8") in v5_data)
    check("v04 formatter has handle-free Tx/Rx headers",
          u16("  %s[%2ld] %s. %lu bytes. TxF=0x%08lx\n") in v4_data
          and u16("Actual data %lu of %lu bytes. RxS=0x%08lx") in v4_data)
    check("v05 formatter adds decimal Handle fields",
          u16("%lu Handle, %lu bytes. TxF=0x%08lx") in v5_data
          and u16("%lu Handle, Actual data %lu of %lu bytes. RxS=0x%08lx") in v5_data)
    check("v04 exposes PTWriteMsgs while v05 exposes PTQueueMsgs",
          u16("PTWriteMsgs") in v4_data and u16("PTQueueMsgs") in v5_data)
    check("both versions retain the raw-byte line marker",
          u16(r"  \__") in v4_data and u16(r"  \__") in v5_data)
    check("both versions use performance-counter elapsed timestamps",
          b"QueryPerformanceCounter" in v4_data
          and b"QueryPerformanceFrequency" in v4_data
          and b"QueryPerformanceCounter" in v5_data
          and b"QueryPerformanceFrequency" in v5_data)

    ctrl_data = J2534_CTRL.read_bytes()
    check("J2534Ctrl generates timestamped ErrorReport log names",
          b"%s\\Techstream\\ErrorReport\\j2534_%02d%02d%04d%02d%02d%02d.log"
          in ctrl_data)
    check("J2534Ctrl exposes save/finish synchronization events",
          b"SAVE_J2534_LOG_FILE_EVENT" in ctrl_data
          and b"FINISH_J2534_LOG_FILE_EVENT" in ctrl_data)
    check("J2534Ctrl path builder uses local wall-clock time",
          b"GetLocalTime" in ctrl_data and b"SHGetSpecialFolderPathA" in ctrl_data)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
