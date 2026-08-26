#!/usr/bin/env python3
"""Verify the telescope-informed H/F direct-canary package and choreography."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.common.ram_exec import explicit_route  # noqa: E402
from exploit.ephemeral_runtime.corolla_hf_direct_canary import (  # noqa: E402
    ALBINO_APP_F181,
    BOOT_F181,
    CANARY_SHA256,
    DIRECT_PAYLOAD_SHA256,
    DID_201,
    DID_202,
    DID_203,
    FF00_REQUEST,
    HEARTBEAT_ADDR,
    HEARTBEAT_MAGIC,
    REQUEST_DOWNLOAD,
    VERIFY_10F0,
    _attest_once,
    _upload_and_trigger,
    build_payload,
    build_plan,
)

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][dynamic_trace] {name}{suffix}")


class FakeUds:
    class SESSION_TYPE:
        DEFAULT = 1
        EXTENDED_DIAGNOSTIC = 3
        PROGRAMMING = 2

    class ACCESS_TYPE:
        REQUEST_SEED = 1
        SEND_KEY = 2

    class SERVICE_TYPE:
        REQUEST_DOWNLOAD = 0x34
        READ_MEMORY_BY_ADDRESS = 0x23

    class ROUTINE_CONTROL_TYPE:
        START = 1

    class DATA_IDENTIFIER_TYPE:
        APPLICATION_SOFTWARE_IDENTIFICATION = 0xF181


class FakeClient:
    def __init__(self, f181: bytes = BOOT_F181) -> None:
        self.events: list[tuple] = []
        self.f181 = f181

    def diagnostic_session_control(self, session):
        self.events.append(("session", session))
        return b""

    def read_data_by_identifier(self, did):
        self.events.append(("rdbi", did))
        return self.f181

    def security_access(self, access, data_record=None, security_key=None):
        data = data_record if data_record is not None else security_key
        self.events.append(("security", access, bytes(data or b"")))
        if access == FakeUds.ACCESS_TYPE.REQUEST_SEED:
            return bytes.fromhex("ef309a63a0572b7a147b7062aa1073a3")
        return b""

    def write_data_by_identifier(self, did, data):
        self.events.append(("wdbi", did, bytes(data)))
        return b""

    def _uds_request(self, service, data):
        self.events.append(("request", service, bytes(data)))
        return b"\x20\x04\x02" if service == FakeUds.SERVICE_TYPE.REQUEST_DOWNLOAD else b""

    def transfer_data(self, block, data):
        self.events.append(("transfer", block, bytes(data)))
        return b""

    def request_transfer_exit(self):
        self.events.append(("exit",))
        return b""

    def routine_control(self, control, rid, data=b""):
        self.events.append(("routine", control, rid, bytes(data)))
        return b""


print("== deterministic direct package ==")
payload, meta = build_payload()
plan = build_plan()
canary_source = ROOT / "exploit/ephemeral_runtime/corolla_hf_canary.c"
canary_audit = json.loads((ROOT / "exploit/ephemeral_runtime/audited_corolla_hf_canary_build.json").read_text())
canary_source_bytes = canary_source.read_bytes()
check("heartbeat semantics are source/audit bound", canary_audit["source"]["path"] == "exploit/ephemeral_runtime/corolla_hf_canary.c" and canary_audit["source"]["sha256"] == hashlib.sha256(canary_source_bytes).hexdigest() and canary_audit["runtime_contract"]["canary_heartbeat"] == f"0x{HEARTBEAT_ADDR:08X}" and b"0x45504843u" in canary_source_bytes)
check("audited canary identity", meta["shellcode_size"] == 332 and meta["shellcode_sha256"] == CANARY_SHA256)
check("direct package identity", len(payload) == 0x1000 and meta["payload_sha256"] == DIRECT_PAYLOAD_SHA256)
check("package callback and descriptor are FEBF0000", meta["callback_address"] == "0xFEBF0000" and meta["crc_descriptor_address"] == "0xFEBF0000")
check("package authenticates and has terminal CRC residue", meta["cmac_valid"] is True and meta["crc_residue"] == "0xFFFFFFFF")
check("plan reproduces telescope zero DID setup", plan["field_proven_bootstrap"]["did_0203"] == DID_203.hex() and plan["field_proven_bootstrap"]["did_0201"] == DID_201.hex() and plan["field_proven_bootstrap"]["did_0202"] == DID_202.hex())
check("plan reproduces exact RequestDownload", plan["field_proven_bootstrap"]["request_download"] == REQUEST_DOWNLOAD.hex() == "01460100febf000000001000")
check("plan reproduces exact 10F0 option", plan["field_proven_bootstrap"]["verify_option"] == VERIFY_10F0.hex() == "4500febf000000001000")
check("plan reproduces exact old-stack FF00 request", plan["field_proven_bootstrap"]["ff00_request"] == FF00_REQUEST.hex() == "3101ff004500000e000000008000")
check("direct package eliminates post-auth substitution", plan["field_proven_bootstrap"]["post_10f0_ram_substitution_required"] is False)
check("command5 remains gated off", plan["success_gate"]["command5_proxy_authorized_by_this_plan"] is False)
check("exact application identity is pinned", plan["target"]["required_application_f181_hex"] == ALBINO_APP_F181.hex())
check("exact boot placeholder identity is pinned", plan["target"]["required_boot_f181_hex"] == BOOT_F181.hex())

print("\n== mocked field-proven upload choreography ==")
client = FakeClient()
route = explicit_route(bus=0, elm327_param=0, uds_variant="old", cpu_index=0)
sent: list[tuple] = []
sleeps: list[float] = []
stats = _upload_and_trigger(
    object(),
    client,
    FakeUds,
    route,
    payload=payload,
    security_secret=bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044"),
    isotp_send_fn=lambda panda, data, addr, *, bus: sent.append((bytes(data), addr, bus)),
    sleep_fn=lambda seconds: sleeps.append(seconds),
)
e = client.events
check("one old-stack identity ladder is explicit", e[:3] == [
    ("session", 1), ("session", 3), ("session", 2),
], repr(e[:3]))
check("session settle timing mirrors telescope", sleeps == [0.5, 0.7, 1.0], repr(sleeps))
check("boot F181 is verified before SA", e[3] == ("rdbi", 0xF181))
check("SecurityAccess requests zero data record", e[4] == ("security", 1, bytes(16)))
check("SecurityAccess sends a 16-byte response", e[5][0:2] == ("security", 2) and len(e[5][2]) == 16)
check("DID writes exactly reproduce telescope 0203/0201/0202", e[6:9] == [
    ("wdbi", 0x203, bytes(5)),
    ("wdbi", 0x201, bytes(16)),
    ("wdbi", 0x202, bytes(16)),
])
check("RequestDownload record is exact", e[9] == ("request", 0x34, REQUEST_DOWNLOAD))
check("payload transfers in four exact 0x400 blocks", [row[1] for row in e[10:14]] == [1, 2, 3, 4] and all(row[0] == "transfer" and len(row[2]) == 0x400 for row in e[10:14]))
check("TransferExit precedes 10F0", e[14] == ("exit",) and e[15] == ("routine", 1, 0x10F0, VERIFY_10F0))
check("FF00 sent only after successful 10F0 call", sent == [(FF00_REQUEST, 0x7A1, 0)])
check("install stats retain boot identity and successful gates", stats["boot_f181_hex"] == BOOT_F181.hex() and stats["rid_10f0_accepted"] and stats["ff00_sent"])

empty_download = FakeClient()
empty_download._uds_request = lambda service, data: (empty_download.events.append(("request", service, bytes(data))) or b"")
try:
    _upload_and_trigger(
        object(), empty_download, FakeUds, route, payload=payload,
        security_secret=bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044"),
        isotp_send_fn=lambda *args, **kwargs: None, sleep_fn=lambda _: None,
    )
except Exception as exc:
    empty_download_rejected = "RequestDownload returned an empty" in str(exc)
else:
    empty_download_rejected = False
check("empty RequestDownload positive payload fails closed before transfer", empty_download_rejected and not any(row[0] == "transfer" for row in empty_download.events))

try:
    _upload_and_trigger(
        object(), FakeClient(), FakeUds,
        explicit_route(bus=0, elm327_param=0, uds_variant="new", cpu_index=0),
        payload=payload, security_secret=bytes(16),
        isotp_send_fn=lambda *args, **kwargs: None, sleep_fn=lambda _: None,
    )
except Exception as exc:
    new_stack_rejected = "old-stack" in str(exc)
else:
    new_stack_rejected = False
check("unobserved new-stack variant fails closed", new_stack_rejected)

bad = FakeClient(f181=b"bad")
try:
    _upload_and_trigger(
        object(), bad, FakeUds, route, payload=payload, security_secret=bytes(16),
        isotp_send_fn=lambda *args, **kwargs: None, sleep_fn=lambda _: None,
    )
except Exception as exc:
    boot_identity_rejected = "boot F181 mismatch" in str(exc)
else:
    boot_identity_rejected = False
check("wrong boot identity fails before SecurityAccess/upload", boot_identity_rejected and not any(row[0] == "security" for row in bad.events))

print("\n== application-context canary attestation ==")
app = FakeClient(f181=ALBINO_APP_F181)
reads = iter((bytes.fromhex("50485045"), bytes.fromhex("51485045")))
attest = _attest_once(
    app,
    FakeUds,
    heartbeat_interval=0.05,
    read_memory_fn=lambda client, uds, mem, addr, size: next(reads),
    sleep_fn=lambda _: None,
)
check("post-FF00 application F181 must reappear", attest["application_f181_hex"] == ALBINO_APP_F181.hex())
check("attestation enters extended session", ("session", 3) in app.events)
check("attestation reads target-native heartbeat address", attest["heartbeat_address"] == f"0x{HEARTBEAT_ADDR:08X}")
check("heartbeat signature and progression are required", attest["heartbeat_magic_le"] == HEARTBEAT_MAGIC and attest["heartbeat_start_delta"] == 13 and attest["heartbeat_step"] == 1 and attest["heartbeat_advanced"] is True)

try:
    _attest_once(
        FakeClient(f181=ALBINO_APP_F181), FakeUds, heartbeat_interval=0.05,
        read_memory_fn=lambda client, uds, mem, addr, size: bytes.fromhex("50485045"),
        sleep_fn=lambda _: None,
    )
except Exception as exc:
    static_rejected = "progression is implausible" in str(exc)
else:
    static_rejected = False
check("static heartbeat cannot pass", static_rejected)

foreign_reads = iter((bytes.fromhex("01020304"), bytes.fromhex("02020304")))
try:
    _attest_once(
        FakeClient(f181=ALBINO_APP_F181), FakeUds, heartbeat_interval=0.05,
        read_memory_fn=lambda client, uds, mem, addr, size: next(foreign_reads),
        sleep_fn=lambda _: None,
    )
except Exception as exc:
    foreign_rejected = "canary signature" in str(exc)
else:
    foreign_rejected = False
check("unrelated changing RAM cannot masquerade as canary heartbeat", foreign_rejected)

try:
    _attest_once(
        FakeClient(f181=b"wrong"), FakeUds, heartbeat_interval=0.05,
        read_memory_fn=lambda *args: bytes(4), sleep_fn=lambda _: None,
    )
except Exception as exc:
    wrong_app_rejected = "application F181 mismatch" in str(exc)
else:
    wrong_app_rejected = False
check("wrong application identity cannot pass", wrong_app_rejected)

source = (ROOT / "exploit/ephemeral_runtime/corolla_hf_direct_canary.py").read_text(encoding="utf-8")
check("live mode is double-gated", "--execute requires --bench-isolated" in source)
check("tool cannot expose command5 proxy", "corolla_hf_command5_proxy.bin" not in source and "command5_proxy_authorized_by_this_plan" in source)
check("no flash write primitive is imported", all(token not in source for token in ("flash_erase", "flash_program", "erase_codeflash", "write_codeflash", "exploit.patcher")))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
