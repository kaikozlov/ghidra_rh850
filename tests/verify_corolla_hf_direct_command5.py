#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "exploit/ephemeral_runtime/corolla_hf_direct_command5.py"
PROXY = ROOT / "exploit/ephemeral_runtime/audited/corolla_hf_command5_proxy.bin"
SOURCE = ROOT / "exploit/ephemeral_runtime/corolla_hf_command5_proxy.c"

spec = importlib.util.spec_from_file_location("hf_cmd5", TOOL)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

passed = failed = 0

def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"[PASS][dynamic_trace] {name}")
    else:
        failed += 1
        print(f"[FAIL][dynamic_trace] {name}{': ' + detail if detail else ''}")

plan = mod.build_plan()
check("schema exact", plan["schema"] == "corolla-hf-direct-command5-v1")
check("audited proxy identity exact", PROXY.stat().st_size == 462 and plan["package"]["shellcode_sha256"] == "3bb96eefae06005c99a0ac52b7f0c64cc5d52e2b0b1fcbb73e0b4ec69609f8d3")
check("direct proxy package identity exact", plan["package"]["payload_sha256"] == "a94979704010758dd09acc0e137977c8eed5003822eababa39eb8a7e5e9d5a58" and plan["package"]["payload_size"] == 4096)
check("package validates CRC and CMAC", plan["package"]["crc_residue"] == "0xFFFFFFFF" and plan["package"]["cmac_valid"] is True)
check("field-proven zero-DID old-stack path retained", plan["field_proven_bootstrap"]["did_0203"] == "0000000000" and plan["field_proven_bootstrap"]["did_0201"] == "00"*16 and plan["field_proven_bootstrap"]["did_0202"] == "00"*16 and plan["field_proven_bootstrap"]["post_10f0_ram_substitution_required"] is False)
probe = plan["probe"]
check("fixed selector4 B6-sized contract", probe["command5"]["driver_record"] == 0 and probe["command5"]["key_selector"] == 4 and probe["command5"]["input_length"] == 36 and probe["command5"]["expected_output_length"] == 16)
check("mailbox contract exact", probe["mailbox"] == {"address":"0xFEBFFB80","size":60,"request_state_offset":0,"result_status_offset":1,"output_length_offset":4,"input_offset":8,"output_offset":44})
check("host uses sentinels and commits request state last", probe["host_commit_order"][-1] == "write request_state=1 last" and "0xFE" in probe["host_commit_order"][2] and "a5" in probe["host_commit_order"][1])
check("live stage requires canary plus reset confirmation", plan["live_guards"]["successful_canary_result_required"] and plan["live_guards"]["reset_to_stock_confirmation_required"] and plan["live_guards"]["execute_and_bench_isolated_required"])
check("no flash/steering transmission is part of probe", plan["live_guards"]["flash_write_used"] is False and plan["live_guards"]["steering_can_transmit_used"] is False)
check("proxy source self-initializes before interrupts", "m->request_state = 0u;\n  __asm__ volatile(\"ei\");" in SOURCE.read_text())
check("proxy mirrors completion status into mailbox", "m->result_status = (unsigned char)(completion_state >> 8);" in SOURCE.read_text() and "m->result_status = (unsigned char)rc;" in SOURCE.read_text())
check("proxy samples adjacent completion bytes as halfword", "volatile unsigned short *completion" in SOURCE.read_text() and "*completion = 0xff00u;" in SOURCE.read_text())

# Successful retained canary is an explicit capability token, not a filename-only gate.
with tempfile.TemporaryDirectory() as td:
    good = Path(td) / "good.json"
    good.write_text(json.dumps({
        "schema": "corolla-hf-direct-canary-v1", "mode": "live", "created_at": "test",
        "live": {
            "attestation": {"attested": True, "heartbeat_advanced": True, "application_f181_hex": mod.ALBINO_APP_F181.hex(), "heartbeat_first_hex":"43485045", "heartbeat_second_hex":"44485045"},
            "panda_safety_tx_blocked_delta": 0,
            "package": {"payload_sha256":"313d1bb70fe6147c179e4b5a35e4556e536f062a80d53d85af3d4292b0b29d84"},
            "reset_to_stock_checked": False,
        },
    }))
    gate = mod.validate_canary_result(good)
    check("successful exact canary result is accepted", gate["application_f181_hex"] == mod.ALBINO_APP_F181.hex() and gate["panda_safety_tx_blocked_delta"] == 0)
    bad = Path(td) / "bad.json"
    bad.write_text(json.dumps({"schema":"corolla-hf-direct-canary-v1","mode":"live","live":{"attestation":{"attested":False}}}))
    try:
        mod.validate_canary_result(bad)
        bad_rejected = False
    except mod.DirectCommand5Error:
        bad_rejected = True
    check("failed canary result is rejected", bad_rejected)

# Model the host-visible state machine: idle -> queued -> completed, with result/output sentinels.
originals = (mod._exchange, mod.parse_positive_response, mod._read_xcp, mod._write_xcp, mod.time.sleep)
try:
    mem = bytearray(60)
    phases = {"poll": 0}
    writes = []
    output = bytes.fromhex("00112233445566778899aabbccddeeff")
    def fake_exchange(*args, **kwargs): return b"\xff"
    def fake_positive(*args, **kwargs): return None
    def fake_write(_panda, *, bus, timeout, address, data):
        off = address - mod.MAILBOX
        mem[off:off+len(data)] = data
        writes.append((address, bytes(data)))
        return 1
    def fake_read(_panda, *, bus, timeout, address, length):
        off = address - mod.MAILBOX
        if address == mod.MAILBOX and length == 2 and mem[0] == 1:
            phases["poll"] += 1
            if phases["poll"] == 1:
                return bytes((2, mod.RESULT_SENTINEL))
            mem[0] = 0; mem[1] = 0; mem[4:8] = (16).to_bytes(4,"little"); mem[44:60] = output
        return bytes(mem[off:off+length])
    mod._exchange, mod.parse_positive_response = fake_exchange, fake_positive
    mod._write_xcp, mod._read_xcp, mod.time.sleep = fake_write, fake_read, lambda _x: None
    observed, meta = mod._execute_probe(object(), bus=1, timeout=.1, completion_timeout=1, message=mod.DEFAULT_VECTOR)
    check("host state machine accepts queued then status-zero completion", observed == output and meta["result_status"] == 0 and meta["queued_state_observed"] and meta["state_transitions_observed"] == [2,0])
    check("request_state commit is final host write", writes[-1] == (mod.MAILBOX, b"\x01"))
    check("output sentinel is replaced before success", observed != mod.OUTPUT_SENTINEL)
finally:
    mod._exchange, mod.parse_positive_response, mod._read_xcp, mod._write_xcp, mod.time.sleep = originals

proc = subprocess.run([sys.executable, str(TOOL)], cwd=ROOT, capture_output=True, text=True)
check("plan-only CLI succeeds without hardware", proc.returncode == 0)
if proc.returncode == 0:
    cli = json.loads(proc.stdout)
    check("plan-only CLI cannot claim live result", cli["mode"] == "plan" and cli["live"] is None)

proc = subprocess.run([sys.executable, str(TOOL), "--execute", "--bench-isolated", "--reset-to-stock-confirmed"], cwd=ROOT, capture_output=True, text=True)
check("live CLI refuses missing canary result before hardware", proc.returncode != 0 and "--canary-result" in proc.stderr)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
