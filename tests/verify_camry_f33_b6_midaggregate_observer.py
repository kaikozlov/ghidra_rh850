#!/usr/bin/env python3
"""Verify deterministic exact-F33 mid-aggregate ingress observer and statistics contract."""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exploit.ephemeral_runtime import camry_f33_b6_midaggregate_observer as host
from exploit.ephemeral_runtime import build_camry_f33_b6_midaggregate_observer as build

OUT = ROOT / "build/out/ephemeral-runtime/camry-f33-b6-midaggregate-observer"
AUDIT = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_b6_midaggregate_observer_build.json"
AUDITED_STAGE = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_midaggregate_observer.bin"
subprocess.run([sys.executable, str(build.BUILDER)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
meta = json.loads((OUT / "build.json").read_text())
resident = (OUT / meta["resident"]["path"]).read_bytes()
staging = (OUT / meta["staging"]["path"]).read_bytes()
payload = (OUT / meta["authenticated_payload"]["path"]).read_bytes()
image = build.IMAGE.read_bytes()


def sha(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()


def check(name: str, cond: object) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"PASS {name}")


check("exact target and payload hashes", meta["target"]["software_id"] == "8965F3307000" and
      sha(resident) == host.EXPECTED_RESIDENT_SHA256 == meta["resident"]["sha256"] and
      sha(staging) == host.EXPECTED_STAGING_SHA256 == meta["staging"]["sha256"] and
      sha(payload) == host.EXPECTED_PAYLOAD_SHA256 == meta["authenticated_payload"]["sha256"])
check("audited promotion is byte/metadata exact",
      json.loads(AUDIT.read_text()) == meta and AUDITED_STAGE.read_bytes() == staging)
check("resident fits live-qualified high tail", len(resident) == host.RESIDENT_SIZE == 498 and
      meta["resident"]["limit"] == 524 and meta["resident"]["headroom"] == 26 and meta["resident"]["relocations"] == 0)
check("tail jumps preserve untouched stock suffixes", meta["resident"]["external_tail_jumps"] == ["0x000667F2","0x0007A272"] and
      image[0x66802:0x66806] == bytes.fromhex("40063f00") and image[0x7A2C4:0x7A2C8] == bytes.fromhex("40063f00"))
check("exact queue geometry and observation boundary pinned", meta["static_pins"]["d7_queue_record"] == "0xFEBE5472" and
      meta["static_pins"]["b6_queue_record"] == "0xFEBE547A" and meta["static_pins"]["b6_secured_buffer"] == "0xFEBE54D4" and
      "before" in meta["static_pins"]["observation_boundary"] and "0x6A410" in meta["static_pins"]["observation_boundary"])
check("normal controller callback0 is exact CanIf receive", meta["static_pins"]["normal_rx_callbacks"][0] == "0x000810F2")
check("observer writes only mailbox by declared contract", meta["mutation_boundary"] == {
    "added_write_regions": ["FEBF0000..FEBF0027 observer mailbox"],
    "codeflash_write": False, "resident_b6_transmit": False, "route44_publish": False,
    "secoc_bypass": False, "source_memory_write": False, "steering_can_transmit": False,
})

# Function-boundary-independent caller census from the exact decompilation corpus.
callers: dict[int, set[int]] = {}
rx = re.compile(r"FUN_([0-9A-Fa-f]{8})\s*\(")
for line in (ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl").read_text().splitlines():
    d = json.loads(line)
    if not d.get("entry_addr"):
        continue
    src = int(d["entry_addr"],16)
    for t in rx.findall(d.get("decompiled_c", "")):
        target=int(t,16)
        if target != src:
            callers.setdefault(target,set()).add(src)
check("79EDE uniquely owns 809FE foreground receive-ring drain", callers.get(0x809FE) == {0x79EDE})
check("809FE uniquely owns 808D6 queue drain", callers.get(0x808D6) == {0x809FE})
check("808D6 uniquely owns 80884 configured callback dispatch", callers.get(0x80884) == {0x808D6})

# Exact callback table and normal-control bytes close the indirect edge to CanIf 810F2.
callbacks = [int.from_bytes(image[0x21A24+i:0x21A28+i],"little") for i in range(0,24,4)]
check("normal receive callback table exact", callbacks == [0x810F2,0x81072,0x81200,0x81072,0x81072,0x81072] and
      set(image[0x219DC:0x219DC+43]) == {1})

# Mailbox decoder and wrap-safe statistics.
raw = bytearray(host.MAILBOX_SIZE)
raw[0:4] = host.MAILBOX_MAGIC.to_bytes(4,"little"); raw[4]=host.MAILBOX_VERSION
for off,val in ((0x08,101),(0x0C,22),(0x10,7),(0x14,3)):
    raw[off:off+4]=val.to_bytes(4,"little")
sig = bytes.fromhex("0000003f0011223300000000d1234567")
raw[0x18:0x28]=sig
d=host.decode_mailbox(bytes(raw))
check("mailbox decodes exact ID63 compact identity", d["magic_ok"] and d["version_ok"] and d["id63_marker_count"]==3 and
      d["last_id63_target_lateral_id"]==63 and d["last_id63_signature_hex"]==sig.hex() and d["last_id63_trailer_hex"]=="d1234567")
check("u32 counters are wrap safe", host.delta_u32(2,0xFFFFFFFE)==4)

base_delta={"observation_count":400,"d7_queue32_count":90,"b6_queue32_count":12,"id63_marker_count":1}
verdict,match=host.classify_marker_delta(base_delta,transmitted_signatures=["aa",sig.hex(),"bb"],stored_signature=sig.hex(),accepted_returns=3,rejected_returns=0)
check("exact resident signature is decisive success", verdict=="exact_id63_b6_seen_after_canif_before_secoc" and match==[1])
nohit={**base_delta,"id63_marker_count":0}
verdict,_=host.classify_marker_delta(nohit,transmitted_signatures=["aa"],stored_signature=None,accepted_returns=1,rejected_returns=0)
check("D7-positive no-marker is bounded midaggregate negative", verdict=="id63_not_seen_at_midaggregate_boundary")
noctrl={**nohit,"d7_queue32_count":0}
verdict,_=host.classify_marker_delta(noctrl,transmitted_signatures=["aa"],stored_signature=None,accepted_returns=1,rejected_returns=0)
check("no positive control stays inconclusive", verdict=="same_scheduler_d7_positive_control_not_seen")

# Statistics contract: no diagnostic read inside either treatment loop and marker cadence is not 5-ms phase locked.
host_src = Path(host.__file__).read_text()
tree=ast.parse(host_src)
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for name in ("run_idle_selfcheck","run_id63_marker"):
    text=ast.get_source_segment(host_src,funcs[name]) or ""
    check(f"{name} has exactly pre/post mailbox reads", text.count("session.read_state()") == 2)
check("jitter intervals avoid 5-ms phase lock", all(ms % 5 for ms in host.JITTER_MS) and len(set(ms % 5 for ms in host.JITTER_MS)) >= 3)
check("metadata forbids SID23 treatment polling", meta["statistics_contract"]["no_sid23_during_treatment"] is True and
      "0x0D7" in meta["statistics_contract"]["same_scheduler_positive_control"])
check("NRTD attestation does not require receive-gated observation progress",
      'state["magic_ok"] and state["version_ok"]' in host_src and
      'state["observation_count"] > 0' not in ast.get_source_segment(host_src, funcs["install"]))
asm_src = build.SOURCE.read_text()
check("mailbox initialization preserves arbitrary counter baselines",
      "Counters are deliberately not zeroed" in asm_src and ".L_clear_mailbox" not in asm_src)

print("PASS camry F33 mid-aggregate observer")
