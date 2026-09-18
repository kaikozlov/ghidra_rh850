#!/usr/bin/env python3
"""Verify exact-F33 high-rate 0x08A selector-4 oracle transport."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import (
    build_camry_f33_08a_oracle_stream as build,
)
from exploit.ephemeral_runtime import (
    camry_f33_08a_oracle_stream as oracle,
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    print("== deterministic build ==")
    with tempfile.TemporaryDirectory(prefix="verify-f33-08a-oracle-") as td:
        out = Path(td)
        run = subprocess.run(
            [sys.executable, str(build.BUILDER), "--output-dir", str(out)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert run.returncode == 0, run.stderr[-1200:]
        meta = json.loads((out / "camry_f33_08a_oracle_stream.json").read_text())
        resident = (out / meta["resident"]["path"]).read_bytes()
        helper = (out / meta["helper"]["path"]).read_bytes()
        stage = (out / meta["staging"]["path"]).read_bytes()
        payload = (out / meta["authenticated_payload"]["path"]).read_bytes()

    audited_stage = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_08a_oracle_stream.bin"
    audited_meta = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_08a_oracle_stream_build.json"
    assert audited_stage.read_bytes() == stage
    assert json.loads(audited_meta.read_text()) == meta

    assert meta["schema"] == "camry-f33-08a-oracle-stream-build-v1"
    assert meta["target"] == {"software_id": "8965F3307000", "codeflash_sha256": build.IMAGE_SHA256}
    assert (len(resident), sha(resident)) == (oracle.RESIDENT_SIZE, oracle.EXPECTED_RESIDENT_SHA256)
    assert (len(helper), sha(helper)) == (oracle.HELPER_SIZE, oracle.EXPECTED_HELPER_SHA256)
    assert sha(stage) == oracle.EXPECTED_STAGING_SHA256 and len(stage) == 1136
    assert sha(payload) == oracle.EXPECTED_PAYLOAD_SHA256 and len(payload) == 0x1000
    assert meta["resident"]["headroom"] == 112
    assert meta["helper"]["headroom"] == 684 and meta["helper"]["word_count"] == 85 and meta["helper"]["execution"] == "direct-from-GlobalRAM" and meta["helper"]["base"] == "0xFEF07C00"
    assert meta["staging"]["resident_offset"] == 0x180 and meta["staging"]["helper_offset"] == 0x31C

    print("== firmware-pinned transport ==")
    assert meta["request"] == {
        "can_id": "0x7A1", "bus": 1, "transport": "stock classic ISO-TP / CanTp reassembly",
        "dcm_buffer": "0xFEBE5651", "dcm_capacity": 0x100, "nsdu_length": 40,
        "layout": "C9 C9 seq || 00 8A || application[28] || freshness[6] || (seq XOR FF)",
        "authenticated_domain_offset": 3, "authenticated_domain_length": 36,
    }
    assert meta["response"] == {
        "can_id": "0x7A9", "bus": 1,
        "transport": "one classic 8-byte lower-driver frame shaped as ISO-TP SF",
        "lower_object": 53, "lower_node": 1, "lower_mailbox": 6,
        "pending_handle": "0xFEBE5036", "software_handle": "0x00F0",
        "layout": "07 C9 seq status cmac[0:4]",
        "status": {"0": "success", "1": "command5 error", "2": "transient busy/timeout", "3": "bad DataID"},
    }
    assert meta["command5"] == {
        "wrapper": "0x00089BC2", "record": 0, "config_type": 1, "selector": 4,
        "input_length": 36, "output_length": 16,
    }
    image = build.IMAGE.read_bytes()
    assert int.from_bytes(image[0x21FA0:0x21FA4], "little") == 0x7A1
    assert int.from_bytes(image[0x21F80:0x21F84], "little") == 0x7A9
    assert int.from_bytes(image[0x25E94:0x25E98], "little") == 0xFEBE5651
    assert int.from_bytes(image[0x25E98:0x25E9C], "little") == 0x100
    helper_source = build.HELPER_SOURCE.read_text()
    assert "ld.bu -0x61ae[gp]" in helper_source  # durable physical DCM B1 tag
    assert "ld.hu -0x61af[gp]" not in helper_source  # B0 SID is not durable
    assert helper_source.count("jarl32 command5_sync, lp") == 1
    assert helper_source.count("jarl32 lower_can_write, lp") == 1
    assert "movea 53, r0, r6" in helper_source and "movea 0x00f0, r0, r6" in helper_source
    for forbidden in ("0x0b6", "0x4000008a", "ICUSCMD"):
        assert forbidden not in helper_source
    boundary = meta["mutation_boundary"]
    assert boundary["persistent_flash_write"] is False
    assert boundary["host_08a_transmit"] is False and boundary["eps_08a_transmit"] is False
    assert boundary["b6_transmit"] is False and boundary["secoc_bypass"] is False
    assert boundary["accepted_data_id"] == "0x008A only" and boundary["forged_cantp_confirmation"] is False

    print("== request/trailer framing ==")
    request = oracle.build_request(0x12, oracle.KNOWN_DOMAIN)
    assert len(request) == 40
    assert request[:3] == bytes.fromhex("c9c912")
    assert request[3:39] == oracle.KNOWN_DOMAIN
    assert request[39] == 0xED
    try:
        oracle.build_request(1, b"\x00\xb6" + bytes(34))
    except oracle.OracleStreamError:
        pass
    else:
        raise AssertionError("oracle accepted non-0x008A DataID")
    # First seven CMAC nibbles are the transmitted MAC28. The low nibble of the
    # fourth byte is intentionally irrelevant to the trailer.
    assert oracle.trailer_from_cmac4(oracle.KNOWN_DOMAIN, bytes.fromhex("d64e2a50")).hex() == "1d64e2a5"

    print("== state decoder ==")
    raw = bytearray(oracle.STATE_SIZE)
    raw[0:4] = oracle.STATE_MAGIC.to_bytes(4, "little")
    raw[4:8] = bytes((1, 1, 0x12, 0))
    raw[8:12] = (3).to_bytes(4, "little")
    raw[12:16] = (2).to_bytes(4, "little")
    raw[16:20] = (3).to_bytes(4, "little")
    raw[20:24] = bytes((0, 1, 0, 16))
    raw[24:28] = bytes.fromhex("d64e2a50")
    raw[28] = 0
    state = oracle.decode_state(bytes(raw))
    assert state["magic_ok"] and state["version_ok"] and state["initialized"]
    assert state["last_seq"] == 0x12 and state["request_count"] == 3
    assert state["success_count"] == 2 and state["response_count"] == 3
    assert state["last_cmac_first4_hex"] == "d64e2a50" and state["last_response_tx_rc"] == 0

    print("== classic ISO-TP request / private response ==")
    class FakePanda:
        def __init__(self):
            self.rx: list[list[tuple[int, bytes, int]]] = []
            self.tx: list[tuple[int, bytes, int]] = []
            self.cf_count = 0

        def can_recv(self):
            return self.rx.pop(0) if self.rx else []

        def can_send_many(self, arr, **_kwargs):
            for addr, dat, bus in arr:
                self.can_send(addr, dat, bus, **_kwargs)

        def can_send(self, addr, dat, bus, **_kwargs):
            frame = bytes(dat)
            self.tx.append((int(addr), frame, int(bus)))
            if frame[0] >> 4 == 1:  # First Frame -> CTS, BS=0, STmin=0.
                self.rx.append([(oracle.RESPONSE_ADDR, bytes.fromhex("3000000000000000"), oracle.BUS)])
            elif frame[0] >> 4 == 2:
                self.cf_count += 1
                if self.cf_count == 5:
                    # Stock unsupported-SID NRC may coexist; private response must still bind by seq.
                    self.rx.append([
                        (oracle.RESPONSE_ADDR, bytes.fromhex("037fc91100000000"), oracle.BUS),
                        (oracle.RESPONSE_ADDR, bytes.fromhex("07c91200d64e2a50"), oracle.BUS),
                    ])

    fake = FakePanda()
    result = oracle.send_oracle_request(fake, seq=0x12, domain=oracle.KNOWN_DOMAIN)  # type: ignore[arg-type]
    assert result["status"] == 0 and result["mac28_hex"] == oracle.KNOWN_MAC28
    assert result["trailer_hex"] == "1d64e2a5"
    assert result["stock_responses"] == ["037fc91100000000"]
    assert fake.tx[0] == (
        oracle.REQUEST_ADDR,
        bytes((0x10, 40)) + request[:6],
        oracle.BUS,
    )
    assert len(fake.tx) == 6  # one FF + five CF
    assert [row[1][0] for row in fake.tx[1:]] == [0x21, 0x22, 0x23, 0x24, 0x25]
    assembled = fake.tx[0][1][2:]
    for _, frame, _ in fake.tx[1:]:
        assembled += frame[1:]
    assert assembled[:40] == request
    assert result["advertised_stmin_ms"] == 0.0
    assert result["effective_cf_gap_ms"] == 0.0
    assert result["stmin_override_used"] is False

    class FakePanda40(FakePanda):
        def can_send(self, addr, dat, bus, **_kwargs):
            frame = bytes(dat)
            self.tx.append((int(addr), frame, int(bus)))
            if frame[0] >> 4 == 1:
                self.rx.append([(oracle.RESPONSE_ADDR, bytes.fromhex("3000280000000000"), oracle.BUS)])
            elif frame[0] >> 4 == 2:
                self.cf_count += 1
                if self.cf_count == 5:
                    self.rx.append([(oracle.RESPONSE_ADDR, bytes.fromhex("07c91300d64e2a50"), oracle.BUS)])

    fake40 = FakePanda40()
    fast = oracle.send_oracle_request(fake40, seq=0x13, domain=oracle.KNOWN_DOMAIN, cf_gap_ms=0.0)  # type: ignore[arg-type]
    assert fast["advertised_stmin_ms"] == 40.0
    assert fast["effective_cf_gap_ms"] == 0.0
    assert fast["stmin_override_used"] is True and fast["stmin_violated"] is True
    assert fast["cf_batch_used"] is True
    assert "ff_send_to_fc_ms" in fast and "cf_submit_ms" in fast

    fake_no_fc = FakePanda40()
    no_fc = oracle.send_oracle_request(
        fake_no_fc, seq=0x13, domain=oracle.KNOWN_DOMAIN, cf_gap_ms=0.0, skip_flow_control=True,
    )  # type: ignore[arg-type]
    assert no_fc["status"] == 0 and no_fc["mac28_hex"] == oracle.KNOWN_MAC28
    assert no_fc["flow_control_waited"] is False
    assert no_fc["request_batch_included_ff"] is True
    assert no_fc["cf_batch_used"] is True
    assert no_fc["flow_control_frames"] == ["3000280000000000"]
    assert no_fc["advertised_stmin_ms"] == 40.0 and no_fc["stmin_violated"] is True

    class RawBatch:
        def __init__(self):
            self.calls = []
        def can_send_many(self, arr):
            self.calls.append(list(arr))
    class TapBatch:
        def __init__(self):
            import threading
            self._panda = RawBatch()
            self._send_lock = threading.Lock()
        def can_send_many(self, _arr):
            raise AssertionError("fallback path should not be used")
    tap = TapBatch()
    sample_batch = [(oracle.REQUEST_ADDR, bytes.fromhex("2100000000000000"), oracle.BUS)]
    oracle._send_many_batched(tap, sample_batch)  # type: ignore[arg-type]
    assert tap._panda.calls == [sample_batch]

    print("== fast benchmark contract ==")
    class FakeSession:
        def __init__(self):
            self.state = {"last_seq": 7}
            self.calls = []
        def read_state(self):
            return dict(self.state)
        def sign(self, domain, *, seq, cf_gap_ms=None):
            self.calls.append((domain, seq, cf_gap_ms))
            self.state["last_seq"] = seq
            return {
                "seq": seq, "status": 0, "mac28_hex": oracle.KNOWN_MAC28,
                "request_start_to_response_ms": 19.0,
                "final_cf_to_response_ms": 4.0,
            }
    fs = FakeSession()
    bench = oracle.benchmark(fs, count=3, period_ms=25.0, cf_gap_ms=0.0)  # type: ignore[arg-type]
    assert bench["success_count"] == 3 and bench["within_25ms_all_successes"] is True
    assert bench["cf_gap_ms"] == 0.0 and bench["stmin_override_used"] is True
    assert [x[1:] for x in fs.calls] == [(8, 0.0), (9, 0.0), (10, 0.0)]
    assert all("scheduled_start_lateness_ms" in row for row in bench["rows"])

    print("== launcher contract ==")
    launcher = (ROOT / "exploit/ephemeral_runtime/camry_f33_08a_oracle_stream_launcher.sh").read_text()
    assert oracle.EXPECTED_PAYLOAD_SHA256 in launcher
    assert "./f33-08a-oracle known-answer [OUTPUT_JSON]" in launcher
    assert "./f33-08a-oracle transport-probe CF_GAP_MS [OUTPUT_JSON]" in launcher
    assert "./f33-08a-oracle transport-probe-no-fc [OUTPUT_JSON]" in launcher
    assert "./f33-08a-oracle benchmark [COUNT] [OUTPUT_JSON]" in launcher
    assert "./f33-08a-oracle benchmark-fast [COUNT] [OUTPUT_JSON]" in launcher
    assert 'benchmark-fast --count "$count" --period-ms 25 --cf-gap-ms 0' in launcher
    assert "--period-ms 25" in launcher
    plan = oracle.plan(None)
    assert plan["transport"]["target_period_ms"] == 25
    assert plan["boundaries"]["transmitted_08a"] is False
    assert plan["boundaries"]["accepted_data_id"] == "0x008A only"

    print("PASS: exact-F33 high-rate 0x08A oracle stream")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
