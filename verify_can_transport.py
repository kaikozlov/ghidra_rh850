#!/usr/bin/env python3
"""Independent raw-CodeFlash checks for CAN_TRANSPORT_ANALYSIS.md.

No Ghidra project is opened. Static tables/instructions are checked directly,
then correlated with the local public extraction tooling and shellcode.
"""
from pathlib import Path
import struct
import sys

HERE = Path(__file__).resolve().parent
REPOS = HERE.parent
CF = (HERE / "RH850_P1M-E_CodeFlash.bin").read_bytes()

passed = 0
failed = 0

def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        mark = "PASS"
    else:
        failed += 1
        mark = "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"[{mark}] {name}{suffix}")

def u16(off): return struct.unpack_from("<H", CF, off)[0]
def u32(off): return struct.unpack_from("<I", CF, off)[0]

print("== small-data base and CAN configuration roots ==")
TP = 0x869C
check("reset loads tp=0x869C", CF[0x1F8:0x1FE] == bytes.fromhex("25069c860000"))
check("CanIf Rx table root is 0x8920", u32(TP + 0x29C) == 0x8920)
check("CanIf Tx table root is 0x8948", u32(TP + 0x2A0) == 0x8948)
check("CanIf HRH route root is 0x898C", u32(TP + 0x2A4) == 0x898C)
check("CanIf has one Tx PDU", u16(TP + 0x2A8) == 1)
check("RSCFD channel config root is 0x8978", u32(TP + 0x2D0) == 0x8978)
check("RSCFD object config root is 0x8B0C", u32(TP + 0x2D4) == 0x8B0C)
check("RSCFD rule pointer root is 0x8918", u32(TP + 0x2D8) == 0x8918)

print("\n== 0x7A1 / 0x777 receive and 0x7A9 transmit addressing ==")
rx = u32(TP + 0x29C)
rx_rows = [struct.unpack_from("<IIB3x", CF, rx + i * 12) for i in range(2)]
check("Rx config 0 maps CAN 0x7A1 to upper PDU 0", rx_rows[0] == (0, 0x7A1, 0), repr(rx_rows[0]))
check("Rx config 1 maps CAN 0x777 to upper PDU 1", rx_rows[1] == (1, 0x777, 0), repr(rx_rows[1]))
check("both request IDs are standard, not extended", all(r[2] == 0 for r in rx_rows))
tx = u32(TP + 0x2A0)
tx_pdu, tx_id = struct.unpack_from("<II", CF, tx)
tx_ide = CF[tx + 8]
tx_hth = u16(tx + 10)
check("sole Tx config uses upper PDU 0", tx_pdu == 0)
check("sole Tx config uses CAN 0x7A9", tx_id == 0x7A9, hex(tx_id))
check("0x7A9 is a standard ID", tx_ide == 0)
check("diagnostic Tx HTH is 0x13", tx_hth == 0x13, hex(tx_hth))

channels = [CF[0x8978 + i * 6:0x8978 + (i + 1) * 6] for i in range(3)]
enabled = [i for i, row in enumerate(channels) if row[1] & 0x80]
check("only RSCFD channel 1 is enabled", enabled == [1], repr(enabled))
rule_ptrs = [u32(0x8918), u32(0x891C)]
check("driver rule pointers are 0x8954/0x8960", rule_ptrs == [0x8954, 0x8960], repr(rule_ptrs))
check("driver rule 0 contains 0x7A1", u32(rule_ptrs[0]) == 0x7A1)
check("driver rule 1 contains 0x777", u32(rule_ptrs[1]) == 0x777)
check("both driver rules carry route word 0x800",
      u32(rule_ptrs[0] + 8) == u32(rule_ptrs[1] + 8) == 0x800)

print("\n== HRH/HTH callback routing ==")
hrh = u32(TP + 0x2A4)
def route(index):
    off = hrh + index * 8
    return u32(off), u16(off + 4), CF[off + 6]
check("HRH 0x10 selects Rx callback and config 0", route(0x10) == (0x88F8, 0, 1), repr(route(0x10)))
check("HRH 0x11 selects Rx callback and config 1", route(0x11) == (0x88F8, 1, 1), repr(route(0x11)))
check("HTH 0x13 selects Tx callback and config 0", route(0x13) == (0x88F0, 0, 1), repr(route(0x13)))
check("Rx descriptor callback is 0x1EEE", u32(0x88F8 + 4) == 0x1EEE)
check("Tx descriptor callback is 0x1F0C", u32(0x88F0 + 4) == 0x1F0C)
check("Rx adapter calls CanTp_RxIndication 0x2B8A",
      CF[0x1F04:0x1F08] == bytes.fromhex("80ff860c"))
check("Tx adapter calls CanTp_TxConfirmation 0x2F1C",
      CF[0x1F1C:0x1F20] == bytes.fromhex("80ff0010"))

print("\n== RSCFD receive and transmit register use ==")
peripheral_words = [u32(0x23000 + i * 4) for i in range(24)]
for address, name in [
    (0xFFD20178, "CFSTS base"), (0xFFD201D8, "CFPCTR base"),
    (0xFFD20250, "CFDTMC base"), (0xFFD202D0, "CFDTMSTS base"),
    (0xFFD23400, "common-FIFO message base"),
    (0xFFD24000, "Tx message-buffer base"),
]:
    check(f"peripheral table contains {name} {address:#x}", address in peripheral_words)
check("firmware directly loads CFDTMC base at 0x373C",
      CF[0x373C:0x3742] == bytes.fromhex("21065002d2ff"))
check("firmware sets CFDTMC bit 0 via helper at 0x3744",
      CF[0x3744:0x3748] == bytes.fromhex("bfffcae5"))
check("Tx primitive checks CFDTMSTS array",
      CF[0x36EE:0x36F4] == bytes.fromhex("a607050d05a4"))
check("Tx primitive writes TMID", CF[0x3718:0x371E] == bytes.fromhex("81070f4080a4"))
check("Tx primitive writes TMPTR/DLC", CF[0x3720:0x3726] == bytes.fromhex("81074f9880a4"))
check("Tx primitive clears TMFDCTR", CF[0x3736:0x373C] == bytes.fromhex("81078f0080a4"))
channel = (tx_hth & 0x7F) >> 4
obj = tx_hth & 0x0F
n = channel * 16 + obj - 3
check("HTH 0x13 decodes to channel 1", channel == 1)
check("HTH 0x13 normalizes to Tx buffer index 16", n == 16, str(n))
check("diagnostic Tx message RAM is 0xFFD24200", 0xFFD24000 + 0x20 * n == 0xFFD24200)
check("diagnostic Tx command byte is 0xFFD20260", 0xFFD20250 + n == 0xFFD20260)
check("RSCFD Rx wrapper calls common-FIFO reader",
      CF[0x4030:0x4034] == bytes.fromhex("bfff66ff"))
check("RSCFD Rx wrapper calls CanIf_RxIndication",
      CF[0x4040:0x4044] == bytes.fromhex("80ff3806"))
check("common-FIFO status access uses CFSTS displacement",
      CF[0x3F6A:0x3F70] == bytes.fromhex("8707895702a4"))
check("common-FIFO data path reads CFID window",
      CF[0x3FC2:0x3FC8] == bytes.fromhex("8107099068a4"))
check("common-FIFO pop writes 0xFF to CFPCTR window",
      CF[0x3FFA:0x4004] == bytes.fromhex("200eff009d078f0d03a4"))

print("\n== ISO-TP configuration and PCI dispatch ==")
rx0 = CF[TP + 0x6B4:TP + 0x6B4 + 0x18]
rx1 = CF[TP + 0x6B4 + 0x18:TP + 0x6B4 + 0x30]
check("CanTp Rx channel IDs are 0 and 1", u16(TP + 0x6B4) == 0 and u16(TP + 0x6CC) == 1)
check("physical/functional channel type bytes are 1/2", (rx0[2], rx1[2]) == (1, 2), repr((rx0[2], rx1[2])))
check("both CanTp channels use normal addressing", rx0[3] == rx1[3] == 3)
check("physical channel maps to upper PDU 0", u16(TP + 0x6B4 + 0x16) == 0)
check("functional channel maps to upper PDU 1", u16(TP + 0x6B4 + 0x18 + 0x16) == 1)
txcfg = TP + 0x6E4
check("CanTp Tx uses normal addressing", CF[txcfg] == 3)
check("CanTp Tx zero-pads frames", CF[txcfg + 2] == 0)
check("CanTp Tx routes to CanIf PDU 0", u16(txcfg + 0x0E) == 0)
check("CanTp Rx dispatcher calls SF handler 0x242A",
      CF[0x2BFA:0x2BFE] == bytes.fromhex("bfff30f8"))
check("CanTp Rx dispatcher calls FF handler 0x27D8",
      CF[0x2C04:0x2C08] == bytes.fromhex("bfffd4fb"))
check("CanTp Rx dispatcher calls CF handler 0x2946",
      CF[0x2C0E:0x2C12] == bytes.fromhex("bfff38fd"))
check("CanTp Rx dispatcher calls FC handler 0x2AE4",
      CF[0x2BF0:0x2BF4] == bytes.fromhex("bffff4fe"))
check("CanTp_Transmit chooses First Frame path",
      CF[0x2E24:0x2E28] == bytes.fromhex("bffff2fd"))
check("CanTp_Transmit chooses Single Frame path",
      CF[0x2E2A:0x2E2E] == bytes.fromhex("bfffaafe"))
check("Consecutive Frame builder contains PCI base 0x20",
      bytes.fromhex("1b9e2000") in CF[0x20E4:0x2140])
check("FC sender contains CTS PCI 0x30",
      bytes.fromhex("208e3000") in CF[0x1F98:0x2046])
check("FC WAIT sender contains PCI 0x31",
      bytes.fromhex("208e3100") in CF[0x24D0:0x2594])
check("FC OVERFLOW sender contains PCI 0x32",
      bytes.fromhex("208e3200") in CF[0x2636:0x26D2])
check("CanIf_Transmit compares DLC against 8 and rejects greater values",
      CF[0x460E:0x4614] == bytes.fromhex("01ea689a8b35"))
check("CanTp transport maximum is the 12-bit 0x0FFF limit",
      CF[0x2DA0:0x2DAA] == bytes.fromhex("130effff010601f0b145"))

print("\n== Dcm/UDS integration and addressing masks ==")
dcm0 = CF[0x8F04:0x8F0C]
dcm1 = CF[0x8F0C:0x8F14]
check("Dcm PDU 0 records CAN 0x7A1", u32(0x8F04) == 0x7A1)
check("Dcm PDU 1 records CAN 0x777", u32(0x8F0C) == 0x777)
check("Dcm addressing classes are physical=1, functional=0",
      (dcm0[5], dcm1[5]) == (1, 0), repr((dcm0[5], dcm1[5])))
SERVICE = struct.Struct("<BBHI")
services = [SERVICE.unpack_from(CF, 0x8E54 + i * 8) for i in range(20)]
by_sid = {sid:(mask, handler) for sid,mask,_reserved,handler in services}
check("service table has 20 entries", len(services) == 20)
check("SID 0x27 is physical-only mask 0x02", by_sid[0x27] == (2, 0x5516), repr(by_sid[0x27]))
check("SID 0x10 allows both addressing classes", by_sid[0x10][0] == 3)
check("SID 0x28 is functional-only mask 0x01", by_sid[0x28][0] == 1)
check("dispatcher resolves table as tp+0x7B8",
      CF[0x5230:0x5234] == bytes.fromhex("259eb807"))
check("dispatcher loops over exactly 20 entries",
      CF[0x5258:0x525C] == bytes.fromhex("0106ecff"))
check("dispatcher invokes handler indirectly",
      CF[0x5250:0x5254] == bytes.fromhex("fdc760f9"))
check("successful Dcm Rx completion calls dispatcher",
      CF[0x64FC:0x6500] == bytes.fromhex("bfff26ed"))
check("Dcm response path calls CanTp_Transmit",
      CF[0x6784:0x6788] == bytes.fromhex("bfff04c6"))
check("CanTp sends through CanIf wrapper",
      CF[0x2CA2:0x2CA6] == bytes.fromhex("bfff1ef2"))
check("CanTp wrapper calls CanIf_Transmit",
      CF[0x1ED6:0x1EDA] == bytes.fromhex("80ff3027"))
check("CanIf_Transmit calls Can_Write",
      CF[0x4668:0x466C] == bytes.fromhex("bfffe6f0"))
check("Can_Write calls RSCFD Tx primitive",
      CF[0x37A6:0x37AA] == bytes.fromhex("bfff38ff"))

print("\n== local tooling/shellcode corroboration ==")
extract = (REPOS / "secoc" / "extract_keys.py").read_text(encoding="utf-8").lower()
dump_step = (REPOS / "tsk_extraction_by_can_log" / "steps" / "step_dump_dataflash.py").read_text(encoding="utf-8").lower()
shellcode = (REPOS / "secoc" / "shellcode" / "main.c").read_text(encoding="utf-8").lower()
check("Willem extractor transmits to 0x7A1", "addr = 0x7a1" in extract)
check("DataFlash tool uses TX 0x7A1", "tx_addr = 0x7a1" in dump_step)
check("DataFlash tool expects RX 0x7A9", "rx_addr = 0x7a9" in dump_step)
check("dump shellcode transmits CAN 0x7A9", "= 0x7a9;" in shellcode)
for address in ("0xffd20250", "0xffd202d0", "0xffd24000", "0xffd24004", "0xffd24008", "0xffd2400c", "0xffd24010"):
    check(f"dump shellcode independently uses RSCFD {address}", address in shellcode)
check("no local extraction tool currently names functional 0x777",
      "0x777" not in extract and "0x777" not in dump_step and "0x777" not in shellcode)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
