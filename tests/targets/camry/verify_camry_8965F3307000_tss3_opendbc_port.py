#!/usr/bin/env python3
"""Verify exact-F33 Tx/status evidence for the passive Camry TSS3 opendbc port.

Standalone section of the exact-F33 portable family; assertions are carried over verbatim.
"""
from __future__ import annotations

from tools import REPO_ROOT
def section_tss3_opendbc_port() -> int:
    """Verify exact-F33 Tx/status evidence for the passive Camry TSS3 opendbc port."""

    import hashlib
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    ROOT = REPO_ROOT
    IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
    EVID = ROOT / "data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json"
    ART = ROOT / "data/generated/camry_8965F3307000_tss3_opendbc_port.json"
    BUILD = ROOT / "tools/targets/camry/builders/build_camry_8965F3307000_tss3_opendbc_port.py"

    p = f = 0


    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()


    def body_bytes(image: bytes, row: dict) -> bytes:
        ranges=row.get("body_ranges") or []
        if not ranges:
            e=int(row["entry"],16); return image[e:e+int(row["body_size"])]
        out=bytearray()
        for r in ranges:
            lo=int(r["min"],16); hi=int(r["max"],16); out.extend(image[lo:hi+1])
        return bytes(out)


    def check(name: str, ok: object) -> None:
        nonlocal p, f
        yes = bool(ok)
        p += int(yes)
        f += int(not yes)
        print(f"[{'PASS' if yes else 'FAIL'}] {name}")


    img = IMAGE.read_bytes()
    evid = json.loads(EVID.read_text(encoding="utf-8"))
    art = json.loads(ART.read_text(encoding="utf-8"))
    funcs = {int(row["entry"], 16): row for row in evid["functions"]}

    print("== target/evidence identity ==")
    check("exact image hash", sha(img) == evid["image"]["sha256"] == art["target"]["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7")
    for entry, row in sorted(funcs.items()):
        check(f"0x{entry:08X} body hash", sha(body_bytes(img,row)) == row["body_sha256"])
    with tempfile.TemporaryDirectory(prefix="camry-f33-tss3-port-") as td:
        out = Path(td) / "port.json"
        r = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
        check("builder exits cleanly", r.returncode == 0)
        check("builder reproduces artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

    print("\n== exact F33 generated-COM Tx geometry ==")
    tx = art["generated_com_tx"]
    check("Tx table exact address", tx["tx_table"] == "0x00021F58")
    check("first five Tx IDs exact", [(x["can_id"], x["can_fd"]) for x in tx["first_five"]] == [("0x030", True), ("0x351", False), ("0x394", False), ("0x4A3", False), ("0x4C8", False)])
    check("signal/PDU tables exact", tx["signal_to_pdu_table"] == "0x00022488" and tx["pdu_table"] == "0x000226C0" and tx["signal_count"] == 284)
    check("PDU slice-offset table pinned", tx["pdu_slice_offset_table"] == "0x00022840" and tx["pdu_slice_offsets"] == [0, 32, 36, 39, 47])
    check("PDU descriptors exact", tx["pdu_descriptors"] == {
        "0": [2, 0, 0, 32, 0, 3], "1": [200, 0, 0, 4, 0, 3], "2": [60, 0, 0, 3, 0, 3],
        "3": [100, 0, 0, 8, 0, 3], "4": [196, 0, 0, 8, 0, 3],
    })
    check("0x351 signal allocation exact", tx["signal_allocations"]["1"] == [38, 39])
    check("0x394 signal allocation exact", tx["signal_allocations"]["2"] == [40, 41, 42, 43])
    check("0x4A3 signal allocation exact", tx["signal_allocations"]["3"] == list(range(44, 52)))
    check("generic scalar packer target-native", "&DAT_00022488 + (param_1 & 0xffff) * 2" in funcs[0x7D1DC]["decompiled_c"])

    print("\n== exact F33 status carrier packers ==")
    s = art["status_carriers"]
    check("351 exact functions", s["0x351"]["producer"] == "0x0004C216" and s["0x351"]["debounce"] == "0x0004C1C0" and s["0x351"]["packer"] == "0x0004CED0")
    check("351 exact packing", "FUN_0007d1dc(0x26,0x22,3,5" in funcs[0x4CED0]["decompiled_c"] and "FUN_0007d1dc(0x27,0x22,1,4" in funcs[0x4CED0]["decompiled_c"])
    check("394 exact functions", s["0x394"]["projection"] == "0x0004C24A" and s["0x394"]["packer"] == "0x0004CE08")
    check("394 exact packing", all(tok in funcs[0x4CE08]["decompiled_c"] for tok in (
        "FUN_0007d1dc(0x28,0x25,2,6", "FUN_0007d1dc(0x29,0x25,3,3", "FUN_0007d1dc(0x2a,0x26,3,1", "FUN_0007d1dc(0x2b,0x26,1,0")))
    check("4A3 exact functions", s["0x4A3"]["source_preparation"] == "0x0004C000" and s["0x4A3"]["staging"] == "0x0004C14E" and s["0x4A3"]["packer"] == "0x0004C7AA")
    check("4A3 packs signals44..51", "FUN_0007d31e(0x2c,0x27,8,0" in funcs[0x4C7AA]["decompiled_c"] and "FUN_0007d31e(0x33,0x2e,8,0" in funcs[0x4C7AA]["decompiled_c"])
    check("4A3 signed12 angle staging exact", all(tok in funcs[0x4C14E]["decompiled_c"] for tok in ("DAT_febe8048", ">> 8) & 0xf", "DAT_febe7d46", "0x7ff", "0xfffff800")))
    check("4A3 torque staging exact", "DAT_febe66a8" in funcs[0x4C000]["decompiled_c"] and "* 100) / 0x100" in funcs[0x4C000]["decompiled_c"] and "puVar1 + -0x36ae" in funcs[0x4C14E]["decompiled_c"])
    check("4A3 alternate current source exact", "DAT_febe6718" in funcs[0x4C000]["decompiled_c"] and "* -100) / 0x80" in funcs[0x4C000]["decompiled_c"])

    print("\n== 0x030 mapped motor-feedback closure ==")
    m = s["0x030"]["mapped_motor_feedback"]
    check("0x030 carrier exact", s["0x030"]["pdu"] == 0 and s["0x030"]["length"] == 32 and s["0x030"]["source_preparation"] == "0x0004C490" and s["0x030"]["packer"] == "0x0004C97A")
    check("B22:B23 mapped feedback wire exact", m["wire"] == "B22:B23" and m["signal_id"] == 33 and m["pdu_slice_offset_table"] == "0x00022840")
    check("driver torque wire fields exact", [f["wire"] for f in s["0x030"]["driver_torque_fields"]][:2] == ["B8", "B17[3:0]"])
    check("aggregate packs the mapped chain", all(tok in funcs[0x37E48]["decompiled_c"] for tok in ("DAT_febe6e28", "DAT_febe6d78 = iVar2 + iVar4", "DAT_febe6d72 = (short)iVar5")))
    check("map is nonlinear lookup interpolation", all(tok in funcs[0x38678]["decompiled_c"] for tok in ("DAT_00031d44", "(&PTR_DAT_000210f4)", "if ((int)param_1 < 1)")))
    check("publish maps extended Q sum conditioned by sibling axis", all(tok in funcs[0x3879E]["decompiled_c"] for tok in ("DAT_febe6d78", "DAT_febe6d70", "FUN_00038678")))
    tx030 = funcs[0x4C490]["decompiled_c"]
    check("0x030 staging formula exact",
          all(tok in tx030 for tok in ("-0x50e8", "-0x3694", "/ 0x100) * 100", "/ 0x2000"))
          and m["staging_formula"] == "signed16(((((int)(-signed16(FEBE6718)) * unsigned16(FEBEE8D8)) / 0x100) * 100) / 0x2000)")
    check("signal33 packs signed BE16 at B22", "FUN_0007d31e(0x21,0x16,0x10,0" in funcs[0x4C97A]["decompiled_c"] and "DAT_febe8c2e = DAT_febe816c" in funcs[0x4C97A]["decompiled_c"])
    check("mapped-feedback census exact", [x["entry"] for x in evid["fixed_gp_census"]["mapped_current_feedback_gp_minus_0x4a00"]] == ["0x0003879E", "0x00057FD2", "0x00059448", "0x0005D12C"])
    check("extended Q-sum census exact", [x["entry"] for x in evid["fixed_gp_census"]["did1151_q_current_upstream_gp_minus_0x4a8e"]] == ["0x00037E48", "0x00037F92", "0x00059448", "0x0005C7B6", "0x0005CA3A", "0x0005D12C"])
    check("0x030 scale census exact", [x["entry"] for x in evid["fixed_gp_census"]["tx030_current_scale_gp_plus_0x30d8"]] == ["0x0004C490", "0x000BF3AA", "0x000BF97A"])

    print("\n== VAR-056 bounded-census correction ==")
    c = art["census_correction"]
    check("canonical torque census supersedes scratch 4->5 count", c["old_recovered_count"] == 5 and c["new_recovered_count"] == 9 and c["new_read_count"] == 7 and c["new_write_count"] == 2 and c["new_entry"] == "0x0004C490")
    check("updated torque entries exact", c["driver_torque_direct_fixed_gp_entries"] == ["0x00035A06", "0x0004C000", "0x0004C490", "0x0004DB70", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D5E0"])
    check("alternate-current census distinct", [x["entry"] for x in evid["fixed_gp_census"]["alternate_4a3_current_source_gp_minus_0x50e8"]] == ["0x0004C000", "0x0004C490", "0x00059448", "0x0005D12C"])
    check("DID1151 source census remains distinct", [x["entry"] for x in evid["fixed_gp_census"]["did1151_q_current_source_gp_minus_0x50f2"]] == ["0x0004E394", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D12C"])

    print(f"\nResults: {p} passed, {f} failed")
    return 1 if f else 0


if __name__ == "__main__":
    raise SystemExit(section_tss3_opendbc_port())
