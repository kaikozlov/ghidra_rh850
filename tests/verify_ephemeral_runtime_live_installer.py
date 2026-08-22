#!/usr/bin/env python3
"""Verify the complete ephemeral-runtime installer choreography offline."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.ephemeral_runtime.live_installer import (  # noqa: E402
    AUTHENTICATED_FIXTURE_SHA256,
    FF00_REQUEST_OLD,
    FF00_REQUEST_NEW,
    ff00_request,
    _attest_canary_once,
    _bootstrap_and_substitute,
    build_install_plan,
    load_install_spec,
    validate_target_f181,
)
from exploit.common.ram_exec import explicit_route  # noqa: E402

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


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

    class ROUTINE_CONTROL_TYPE:
        START = 1

    class DATA_IDENTIFIER_TYPE:
        APPLICATION_SOFTWARE_IDENTIFICATION = 0xF181


class FakeClient:
    def __init__(self, f181_payload: bytes | None = None) -> None:
        self.events: list[tuple] = []
        self.f181_payload = f181_payload or bytes.fromhex("0138393635423435313230303000000000")

    def diagnostic_session_control(self, value):
        self.events.append(("session", value))

    def security_access(self, access, data=None, data_record=None):
        payload = data_record if data_record is not None else data
        self.events.append(("security", access, bytes(payload or b"")))
        if access == FakeUds.ACCESS_TYPE.REQUEST_SEED:
            return bytes.fromhex("00112233445566778899aabbccddeeff")
        return b""

    def write_data_by_identifier(self, did, data):
        self.events.append(("wdbi", did, bytes(data)))

    def _uds_request(self, service, data):
        self.events.append(("request", service, bytes(data)))
        return b""

    def transfer_data(self, block_counter, data):
        self.events.append(("transfer", block_counter, bytes(data)))
        return b""

    def request_transfer_exit(self):
        self.events.append(("exit",))
        return b""

    def routine_control(self, control, rid, data=b""):
        self.events.append(("routine", control, rid, bytes(data)))
        return b""

    def read_data_by_identifier(self, did):
        self.events.append(("rdbi", did))
        return self.f181_payload


print("== artifact identity and offline plan ==")
spec = load_install_spec("command5-proxy")
plan = build_install_plan(spec, uds_variant="old", cpu_index=0)
check("pinned encrypted fixture identity", spec.fixture_sha256 == AUTHENTICATED_FIXTURE_SHA256)
check("command5 runtime identity", spec.runtime_sha256 == "273202dc591810b2f587ab8fac044599b57b4e07a24ff61d36b7131b97c00660")
check("command5 runtime size", len(spec.runtime) == 546)
check("runtime installs in 37 <=15-byte substitutions", plan["runtime"]["raw_chunks"] == 37 and plan["runtime"]["max_raw_chunk"] == 15)
check("callback is FEBF0FD0 -> FEBF0000 and written last", plan["callback"] == {
    "cell": "0xFEBF0FD0", "value": "0xFEBF0000", "little_endian": "0000bffe", "raw_chunks": 1, "written_last": True,
})
check("bootstrap explicitly requires boot SA", plan["bootstrap"]["boot_security_access_required"] is True)
check("bootstrap explicitly needs no payload-build secret", plan["bootstrap"]["payload_build_secret_required"] is False)
check("target manifest F181 accepts exact Sienna application identity", validate_target_f181("0138393635423435313230303000000000", spec) == bytes.fromhex("0138393635423435313230303000000000"))
try:
    validate_target_f181("0138393635483132303230303000000000", spec)
except Exception as exc:
    wrong_target_rejected = "does not contain any software ID" in str(exc)
else:
    wrong_target_rejected = False
check("target manifest F181 rejects operator-blessed wrong ECU", wrong_target_rejected)
check("old FF00 request is exact", plan["execution_trigger"] == FF00_REQUEST_OLD.hex())
new_plan = build_install_plan(spec, uds_variant="new", cpu_index=0)
check("new FF00 request uses 45 01 magic", new_plan["execution_trigger"] == FF00_REQUEST_NEW.hex() and ff00_request("new")[4:6] == b"\x45\x01")
canary_spec = load_install_spec("canary")
canary_plan = build_install_plan(canary_spec, uds_variant="old", cpu_index=0)
check("canary plan requires automatic heartbeat attestation", canary_plan["canary_attestation"] == {
    "required": True,
    "method": "application F181 + extended-session SID 0x23 heartbeat progression",
    "heartbeat_address": "0xFEBFFBF0",
})

print("\n== canary post-FF00 attestation ==")
canary_client = FakeClient()
heartbeat_reads = iter((bytes.fromhex("50485045"), bytes.fromhex("51485045")))
canary_attestation = _attest_canary_once(
    canary_client,
    FakeUds,
    canary_spec,
    "0138393635423435313230303000000000",
    heartbeat_interval=0.01,
    read_memory_fn=lambda client, uds, mem_id, address, size: next(heartbeat_reads),
    sleep_fn=lambda delay: None,
)
check("canary attestation rechecks application F181", canary_attestation["f181_hex"] == "0138393635423435313230303000000000")
check("canary attestation enters application extended session", ("session", FakeUds.SESSION_TYPE.EXTENDED_DIAGNOSTIC) in canary_client.events)
check("canary attestation uses manifest heartbeat cell", canary_attestation["heartbeat_address"] == "0xFEBFFBF0")
check("canary attestation requires heartbeat progression", canary_attestation["heartbeat_first_le"] + 1 == canary_attestation["heartbeat_second_le"] and canary_attestation["heartbeat_advanced"] is True)
try:
    _attest_canary_once(
        FakeClient(), FakeUds, canary_spec, "0138393635423435313230303000000000",
        heartbeat_interval=0.01,
        read_memory_fn=lambda client, uds, mem_id, address, size: bytes.fromhex("50485045"),
        sleep_fn=lambda delay: None,
    )
except Exception as exc:
    static_heartbeat_rejected = "did not advance" in str(exc)
else:
    static_heartbeat_rejected = False
check("static heartbeat is not accepted as canary success", static_heartbeat_rejected)

print("\n== mocked live choreography ==")
client = FakeClient()
isotp_events: list[tuple] = []
route = explicit_route(bus=1, elm327_param=1, uds_variant="old", cpu_index=0)
secret = bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044")
stats = _bootstrap_and_substitute(
    object(),
    client,
    FakeUds,
    route,
    spec,
    secret,
    isotp_send_fn=lambda panda, data, addr, *, bus: isotp_events.append((bytes(data), addr, bus)),
)
e = client.events
check("old-stack session choreography repeats 01->03->02", e[:6] == [
    ("session", 1), ("session", 3), ("session", 2),
    ("session", 1), ("session", 3), ("session", 2),
], repr(e[:6]))
check("SecurityAccess request is zero data-record", e[6] == ("security", 1, bytes(16)))
check("SecurityAccess send-key is 16 bytes", e[7][0:2] == ("security", 2) and len(e[7][2]) == 16)
check("DID setup is 0203 -> 0201 -> 0202", e[8:11] == [
    ("wdbi", 0x203, b"\x01\x00\x00\x00\x00"),
    ("wdbi", 0x201, bytes(16)),
    ("wdbi", 0x202, bytes(16)),
])
check("authenticated RequestDownload is exact FEBF0000/1000 record", e[11] == (
    "request", 0x34, bytes.fromhex("01460100febf000000001000")
), e[11][2].hex())
check("fixture transfers as four 0x400 blocks", [row[1] for row in e[12:16]] == [1,2,3,4] and all(row[0] == "transfer" and len(row[2]) == 0x400 for row in e[12:16]))
check("authenticated fixture exits before 10F0", e[16] == ("exit",) and e[17][0:3] == ("routine", 1, 0x10F0))
check("10F0 record targets FEBF0000/1000", e[17][3] == bytes.fromhex("4500febf000000001000"), e[17][3].hex())

# Every post-auth chunk is exactly RequestDownload -> block-1 TransferData -> TransferExit.
post = e[18:]
triples = [post[i:i+3] for i in range(0, len(post), 3)]
check("post-auth sequence has 38 substitutions", len(triples) == 38, str(len(triples)))
check("every raw substitution is RD -> block1 TD -> exit", all(
    len(t) == 3 and t[0][0] == "request" and t[0][1] == 0x34 and
    t[1][0:2] == ("transfer", 1) and 1 <= len(t[1][2]) <= 15 and t[2] == ("exit",)
    for t in triples
))
check("first 37 raw substitutions exactly reconstruct runtime", b"".join(t[1][2] for t in triples[:-1]) == spec.runtime)
check("callback substitution is last and writes FEBF0000 pointer", triples[-1][0][2] == bytes.fromhex("01460100febf0fd000000004") and triples[-1][1][2] == bytes.fromhex("0000bffe"))
check("FF00 is sent only after callback substitution", isotp_events == [(FF00_REQUEST_OLD, 0x7A1, 1)])
check("installer reports exact operation counts", stats["fixture_transfer_blocks"] == 4 and len(stats["runtime_substitutions"]) == 37 and len(stats["callback_substitutions"]) == 1 and stats["ff00_sent"] is True)

client_new = FakeClient()
isotp_new: list[tuple] = []
route_new = explicit_route(bus=1, elm327_param=1, uds_variant="new", cpu_index=0)
_bootstrap_and_substitute(
    object(), client_new, FakeUds, route_new, spec, secret,
    isotp_send_fn=lambda panda, data, addr, *, bus: isotp_new.append((bytes(data), addr, bus)),
)
check("new-stack live trigger uses 45 01 magic", isotp_new == [(FF00_REQUEST_NEW, 0x7A1, 1)])
check("new-stack 10F0 and FF00 magic agree", client_new.events[14][3][:2] == b"\x45\x01" and FF00_REQUEST_NEW[4:6] == b"\x45\x01")

source = (REPO / "exploit/ephemeral_runtime/live_installer.py").read_text(encoding="utf-8")
check("live installer never loads payload-build secret", "load_payload_secret" not in source)
check("live execution is explicitly bench gated", "--bench-isolated" in source and "--execute requires --bench-isolated" in source)
check("live F181 is independently bound to manifest software IDs", "validate_target_f181(f181_hex, spec)" in source and "target_software_ids" in source)
check("command5 message is validated before live installation", source.index("_validate_message(command5_message") < source.index("panda, route, live = install_live"))
check("canary live path performs built-in post-FF00 attestation", "canary_attestation" in source and "_wait_for_canary(" in source)
check("command5 proxy phase also pins Panda blocked-Tx telemetry", "proxy_panda_safety_tx_blocked_delta" in source and "Panda blocked at least one command-5 proxy XCP request" in source)
check("command5 proxy failures are folded into fail-closed installer errors", "command-5 proxy phase failed" in source)
check("live secret is not hard-coded in installer source", "f05f36b7d78c03e24ab4faef2a57d044" not in source.lower())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
