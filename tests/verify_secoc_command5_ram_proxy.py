#!/usr/bin/env python3
"""Verify the RAM-only variable-length command-5 proxy from firmware bytes and artifacts."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.command5.ram_proxy import (  # noqa: E402
    INPUT,
    MAILBOX,
    MAILBOX_MAGIC,
    MAILBOX_SIZE,
    OUTPUT,
    PRODUCTION_LENGTHS,
    build_request_plan,
)
from exploit.followups.xcp_shadow_write_plan import SHADOW_END, SHADOW_START  # noqa: E402

CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
MANIFEST = json.loads((REPO / "data/generated/ephemeral_runtime_target_manifest_4512000.json").read_text())
AUDIT = json.loads((REPO / "exploit/ephemeral_runtime/audited_command5_proxy_build.json").read_text())
SOURCE = REPO / "exploit/ephemeral_runtime/command5_proxy.c"
BUILDER = REPO / "exploit/ephemeral_runtime/build_command5_proxy.py"
HOST = REPO / "exploit/command5/ram_proxy.py"
CORPUS = REPO / "data/generated/decompilations.jsonl"
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def sha(a: int, n: int) -> str:
    return hashlib.sha256(CF[a:a+n]).hexdigest()


print("== lower command-5 record-0 path ==")
check("serialized command-5 dispatcher body pinned",
      sha(0x88350, 150) == "dca5252efba4bfee3cc2a509050d088b280771ce58b1d4134d3ead290545d4e4")
check("variable-length command-5 prepare body pinned",
      sha(0x87A94, 178) == "db56dcbbc3be5852d9baa94784b80ddcd26cc9aa704aa4537fb58850a32bcb23")
check("command-5 result-copy body pinned",
      sha(0x87B46, 116) == "c62fc5e48366ad9f56eb73694bfa1481eaba9045f09d36dc751fc264e54f4be2")
check("command-5 adapter body pinned",
      sha(0x87CCC, 260) == "2a5c7f1c4bed7543f8143a21e3d78319c8c3f1298f96ca2b87a5b7a244e9b729")
check("command-5 async completion worker pinned",
      sha(0x87DD0, 186) == "ed65ceae78ed91987a3b27847dffaba9118143e0f94734ffc9aedca5fc9c45f9")

record0 = CF[0x27F78:0x27F98]
record1 = CF[0x27F98:0x27FB8]
check("driver record 0 exact bytes pinned",
      record0 == bytes.fromhex("0000ffff5c8b0800000000000000000000000000cc7c0800d07d0800747f0200"))
check("driver record 1 exact bytes pinned",
      record1 == bytes.fromhex("0100ffff6a920600000000000000000000000000cc7c0800d07d0800757f0200"))
check("record 0 id is zero and uses clean completion callback 0x88B5C",
      struct.unpack_from("<H", record0, 0)[0] == 0 and struct.unpack_from("<I", record0, 4)[0] == 0x88B5C)
check("record 0 and record 1 both use command-5 adapter 0x87CCC",
      struct.unpack_from("<I", record0, 0x14)[0] == struct.unpack_from("<I", record1, 0x14)[0] == 0x87CCC)
check("record 0 and record 1 both use async completion worker 0x87DD0",
      struct.unpack_from("<I", record0, 0x18)[0] == struct.unpack_from("<I", record1, 0x18)[0] == 0x87DD0)
check("record-0 completion callback only publishes status then done",
      CF[0x88B5C:0x88B6A] == bytes.fromhex("4437bd5b010a440fbc5b00527f00"))
check("record-0 completion body pinned",
      sha(0x88B5C, 14) == "ad851b94e1d4e5d1addd4211a68fdc70401832071161bd779b00f957001085f6")
completion_refs = []
for line in CORPUS.open():
    row = json.loads(line)
    for ref in row.get("data_references", []):
        if ref.get("to_addr") in ("0xfebf13bc", "0xfebf13bd"):
            completion_refs.append((row.get("entry_addr"), ref.get("from_addr"), ref.get("ref_type"), ref.get("to_addr")))
check("stock record-0 done/status cells are orphaned except completion writes",
      completion_refs == [
          ("0x00088b5c", "0x00088b5c", "WRITE", "0xfebf13bd"),
          ("0x00088b5c", "0x00088b62", "WRITE", "0xfebf13bc"),
      ], repr(completion_refs))
check("generic prepare admits byte lengths below 0x51",
      CF[0x87ABA:0x87AC0] == bytes.fromhex("0806afffa10d"))
check("generic prepare converts byte length to bit length",
      CF[0x87B1E:0x87B26] == bytes.fromhex("24f6085ac3ea1e0e"))
check("result copy executes before record completion callback dispatch",
      CF[0x87B90:0x87B9E] == bytes.fromhex("243e745a80ffaa121d3080ff5208"))

print("\n== SHA-bound RAM proxy contract ==")
geometry = MANIFEST["ram_execution_geometry"]
check("manifest is exact Sienna CodeFlash SHA",
      MANIFEST["image"]["sha256"] == "21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde")
check("manifest binds dispatcher 0x88350 record 0 selector 4",
      geometry["command5_dispatch_address"] == "0x88350" and geometry["command5_driver_record"] == 0 and geometry["command5_key_selector"] == 4)
check("manifest binds record-0 completion flags",
      geometry["command5_done_flag"] == "0xFEBF13BC" and geometry["command5_status_flag"] == "0xFEBF13BD")
check("manifest binds 128-byte XCP mailbox",
      geometry["command5_mailbox_address"] == "0xFEBFFB80" and geometry["command5_mailbox_size"] == "0x80")
check("mailbox is fully inside no-SA XCP write window",
      SHADOW_START <= MAILBOX and MAILBOX + MAILBOX_SIZE - 1 <= SHADOW_END)
check("mailbox begins above startup CodeFlash shadow-copy end",
      MAILBOX > 0xFEBFF9EF)

mailbox_refs = []
for line in CORPUS.open():
    row = json.loads(line)
    for ref in row.get("data_references", []):
        try:
            addr = int(ref["to_addr"], 16)
        except (KeyError, TypeError, ValueError):
            continue
        if MAILBOX <= addr < MAILBOX + MAILBOX_SIZE:
            mailbox_refs.append((row.get("entry_addr"), ref.get("from_addr"), ref.get("ref_type"), ref.get("to_addr")))
check("canonical application corpus has zero direct references into mailbox", mailbox_refs == [], repr(mailbox_refs))
check("mailbox layout reserves 80 input and 16 output bytes",
      INPUT == MAILBOX + 0x20 and OUTPUT == MAILBOX + 0x70 and OUTPUT + 16 == MAILBOX + MAILBOX_SIZE)

print("\n== deterministic resident build ==")
check("audited build is not bench-validated", AUDIT["review_status"] == "audited-static-not-bench-validated")
check("audited proxy fits retained 0x308-byte executable pocket",
      AUDIT["shellcode"]["size"] == 546 and AUDIT["shellcode"]["headroom"] == 230 and AUDIT["compile_contract"]["retained_limit"] == 776)
check("audited proxy has entry zero and no relocations",
      AUDIT["shellcode"]["entry_offset"] == 0 and AUDIT["compile_contract"]["relocations"] == 0)
check("audited proxy binary identity pinned",
      AUDIT["shellcode"]["sha256"] == "273202dc591810b2f587ab8fac044599b57b4e07a24ff61d36b7131b97c00660")
bindings = {row["path"]: row["sha256"] for row in AUDIT["sources"]}
check("audited proxy source hash matches",
      bindings["exploit/ephemeral_runtime/command5_proxy.c"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest())
check("audited proxy builder hash matches",
      bindings["exploit/ephemeral_runtime/build_command5_proxy.py"] == hashlib.sha256(BUILDER.read_bytes()).hexdigest())
check("audited target manifest hash matches",
      AUDIT["compile_contract"]["target_manifest_sha256"] == hashlib.sha256((REPO / "data/generated/ephemeral_runtime_target_manifest_4512000.json").read_bytes()).hexdigest())
check("security boundary retains initial authenticated RAM foothold",
      AUDIT["security_boundary"]["initial_bootloader_authenticated_ram_foothold_required"] is True and
      AUDIT["security_boundary"]["application_security_access_required"] is False and
      AUDIT["security_boundary"]["persistent_codeflash_mutation_required"] is False)

source = SOURCE.read_text().lower()
check("runtime calls manifest-selected command-5 dispatcher record and slot",
      "target_command5_dispatch" in source and "target_command5_driver_record" in source and "target_command5_key_selector" in source)
check("runtime retries shared-driver busy instead of aborting it",
      "rc != 2" in source and "shared-driver busy" in source and "retry" in source)
check("runtime waits for record-0 done flag and publishes response sequence",
      "target_command5_done_flag" in source and "target_command5_status_flag" in source and "mailbox->response_seq = pending_seq" in source)
check("runtime does not call a command-5 abort primitive", "abort" not in source)

print("\n== XCP mailbox host protocol ==")
msg12 = bytes(range(12))
plan = build_request_plan(msg12, request_seq=0x12345678)
check("host defaults cover configured SecOC lengths 7/12/36", PRODUCTION_LENGTHS == (7, 12, 36))
check("12-byte SecOC request plans fixed record 0 / selector 4",
      plan["command5"]["driver_record"] == 0 and plan["command5"]["key_selector"] == 4 and plan["command5"]["input_length"] == 12)
ops = plan["operations"]
commit_indices = [i for i, row in enumerate(ops) if row.get("operation") == "set_mta" and row.get("address") == f"0x{MAILBOX + 4:08X}"]
body_indices = [i for i, row in enumerate(ops) if row.get("operation") == "set_mta" and row.get("address") == f"0x{MAILBOX + 0x10:08X}"]
check("request sequence commit is written after complete length/input body", len(commit_indices) == len(body_indices) == 1 and commit_indices[0] > body_indices[0])
check("host plans response-sequence poll before status/output reads",
      next(i for i,row in enumerate(ops) if row["operation"] == "poll_response_seq") < next(i for i,row in enumerate(ops) if row["operation"] == "read_output"))
check("host checks live mailbox magic CMD5",
      next(row for row in ops if row["operation"] == "read_magic")["expected"] == MAILBOX_MAGIC.hex())
host_source = HOST.read_text().lower()
check("live host tool is bench gated", "--bench-isolated" in host_source and "--execute requires --bench-isolated" in host_source)
check("host records initial foothold boundary", "initial_bootloader_authenticated_ram_foothold_required" in host_source)

print(f"\nSummary: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
