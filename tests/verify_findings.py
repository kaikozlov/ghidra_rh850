#!/usr/bin/env python3
"""Independent verification of the base firmware findings.

Reads only the committed split images, reconstructing the original combined
layout in memory. No Ghidra project or sibling repository is required.
"""
import hashlib, struct, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPLIT_CF = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
SPLIT_DF = REPO / "firmware" / "RH850_P1M-E_DataFlash.bin"

# Known family secrets (from report / cross-tooling).
PAYLOAD_BUILD_SECRET = bytes.fromhex("ba052435f8843f985fd1329d2b6117b0")
SEED_KEY_SECRET      = bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044")

# Reference AES tables.
AES_SBOX = bytes.fromhex(
    "637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0"
    "b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275"
    "09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cf"
    "d0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2"
    "cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb"
    "e0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08"
    "ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9e"
    "e1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16")
AES_RCON = bytes([0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36])

ok = 0
bad = 0
def check(name, cond, detail=""):
    global ok, bad
    status = "PASS" if cond else "FAIL"
    if cond: ok += 1
    else: bad += 1
    print(f"[{status}] {name}" + (f"  ({detail})" if detail else ""))

df = SPLIT_DF.read_bytes()
cf = SPLIT_CF.read_bytes()
fw = df + cf

# ---- 1. Layout & split SHA-256 ----
print("\n== 1. file layout & split hashes ==")
check("reconstructed combined size == 0x108000", len(fw) == 0x108000, f"{len(fw):#x}")
check("DataFlash size == 0x8000", len(df) == 0x8000)
check("CodeFlash size == 0x100000", len(cf) == 0x100000)
h_combined = hashlib.sha256(fw).hexdigest()
h_df = hashlib.sha256(df).hexdigest()
h_cf = hashlib.sha256(cf).hexdigest()
check("combined sha256 matches pinned original",
      h_combined == "0bba74d0e443f9dd3da33e3a28c3511ec31e35e8303acef7e0117fbdc91d5a86", h_combined[:16])
check("DataFlash sha256 matches README",
      h_df == "81d87b678784bb2a07b1fdcb3d43dd40767d4f5ca1b56867b6575cd652a9ecb8", h_df[:16])
check("CodeFlash sha256 matches README",
      h_cf == "21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde", h_cf[:16])

# ---- 2. Reset handler gp setup at VA 0x1F2 (file 0x81F2) ----
print("\n== 2. reset handler @ VA 0x1F2 ==")
def va_file(va):  # CodeFlash VA -> file offset
    return va + 0x8000
rh = fw[va_file(0x1F2):va_file(0x1F2)+16]
check("reset handler first instr is movhi gp setup", rh[0:4] == bytes.fromhex("24060098"),
      f"raw={rh[:8].hex()}")
# movhi hi16,r0,r6 ; movea lo16,r6,gp  -> gp = 0xFEBF9800
hi = struct.unpack("<H", rh[0:2])[0]          # 0x0024 -> wait, reconstruct properly
# RH850: movea imm16, reg1, reg2. Decode gp value from the documented pair.
gp = struct.unpack("<I", rh[4:8])[0] & 0xFFFFFFFF
# The two-instruction sequence loads 0xFEBF9800; verify the literal appears right after.
gp_literal = struct.unpack("<I", fw[va_file(0x1F2)+4:va_file(0x1F2)+8])[0]
# search the immediate words for 0xFEBF9800
found_gp = (0xFEBF9800).to_bytes(4,"little") in fw[va_file(0x1F2):va_file(0x1F2)+16]
check("gp literal 0xFEBF9800 present in reset prologue", found_gp, f"raw={rh.hex()}")

# ---- 3. Secret bytes & VA mapping ----
print("\n== 3. secrets ==")
def find_once(needle):
    import re
    offs = [m.start() for m in re.finditer(re.escape(needle), fw)]
    return offs
p_offs = find_once(PAYLOAD_BUILD_SECRET)
s_offs = find_once(SEED_KEY_SECRET)
check("PAYLOAD_BUILD_SECRET occurs exactly once in file", len(p_offs)==1, [hex(o) for o in p_offs])
check("SEED_KEY_SECRET occurs exactly once in file", len(s_offs)==1, [hex(o) for o in s_offs])
if len(p_offs)==1:
    check("PAYLOAD file offset == 0x13FD8", p_offs[0]==0x13FD8, hex(p_offs[0]))
    check("PAYLOAD VA == 0xBFD8 (file-0x8000)", p_offs[0]-0x8000==0xBFD8, hex(p_offs[0]-0x8000))
if len(s_offs)==1:
    check("SEED file offset == 0x13FE8", s_offs[0]==0x13FE8, hex(s_offs[0]))
    check("SEED VA == 0xBFE8 (file-0x8000)", s_offs[0]-0x8000==0xBFE8, hex(s_offs[0]-0x8000))

# ---- 4. xref instruction immediates ----
print("\n== 4. xref immediates ==")
# ori imm16, r0, r6  encodes imm16 little-endian in bytes 2-3; word0 = 0x36?? with 0x80 ext.
def decode_ori_imm16(va):
    f = va_file(va)
    w0 = struct.unpack("<H", fw[f:f+2])[0]
    imm = struct.unpack("<H", fw[f+2:f+4])[0]
    return w0, imm
for va, expect, name in [(0x6FF8,0xBFE8,"SEED_KEY ref"),(0x7070,0xBFD8,"PAYLOAD ref")]:
    w0, imm = decode_ori_imm16(va)
    check(f"{name}: {name.split()[0]}@VA {va:#x} encodes imm {expect:#x}",
          imm==expect, f"word0={w0:#06x} imm={imm:#06x}")

# ---- 5. UDS service table @ VA 0x8E54 ----
print("\n== 5. UDS service table @ 0x8E54 ==")
TABLE = 0x8E54
N = 20
entries = []
sid27_handler = None
for i in range(N):
    base = va_file(TABLE) + i*8
    sid, mask, rsv, handler = struct.unpack("<BBHI", fw[base:base+8])
    entries.append((sid, mask, handler))
    if sid == 0x27:
        sid27_handler = handler
sids = sorted({e[0] for e in entries})
check("SID 0x27 handler == 0x5516", sid27_handler==0x5516, hex(sid27_handler) if sid27_handler else None)
print(f"    decoded SIDs: {[hex(s) for s in sids]}")

# ---- 6. AES S-box & Rcon ----
print("\n== 6. AES S-box @ 0x8FF1, Rcon @ 0x8FE1 ==")
sbox = fw[va_file(0x8FF1):va_file(0x8FF1)+256]
rcon = fw[va_file(0x8FE1):va_file(0x8FE1)+len(AES_RCON)]
check("256-byte AES S-box matches at VA 0x8FF1", sbox==AES_SBOX, sbox[:8].hex())
check("AES Rcon matches at VA 0x8FE1", rcon==AES_RCON, rcon.hex())

# ---- 7. Crypto test vectors ----
print("\n== 7. crypto vectors ==")
from Crypto.Cipher import AES
# SecurityAccess: derived=DEC(SEED_KEY,data_record); key=ENC(derived,ecu_seed)
data_record = bytes(16)
ecu_seed = bytes.fromhex("e8c0f91e28faee7b1fc04d49e707fd3e")
derived = AES.new(SEED_KEY_SECRET, AES.MODE_ECB).decrypt(data_record)
key = AES.new(derived, AES.MODE_ECB).encrypt(ecu_seed)
check("SecurityAccess computed key == Willem sample ad250d24...",
      key.hex()=="ad250d24bf843f8d831eaa8bb78e7839", key.hex())
# Payload: derived=ENC(PAYLOAD,zeros)
pderived = AES.new(PAYLOAD_BUILD_SECRET, AES.MODE_ECB).encrypt(bytes(16))
check("payload derived key == 80d221a0...", pderived.hex()=="80d221a05622b4f9d4f287922e6c78d1", pderived.hex())

# ---- 8. SecOC RX retry budgets + callback routing (SECOC-068 / CORR-090) ----
print("\n== 8. SecOC retry budgets + callback routing ==")
recs = [0x25970 + 0x50 * i for i in range(6)]
macs = [struct.unpack_from("<H", fw, va_file(b) + 2)[0] for b in recs]
check("all six SecOC RX records carry MAC length 28", macs == [28] * 6, str(macs))
lim10 = [fw[va_file(b) + 0x10] for b in recs]
check("current-PDU verify retry budget +0x10: sync 0, five ordinary 1",
      lim10 == [0, 1, 1, 1, 1, 1], str(lim10))
lim2e = [fw[va_file(b) + 0x2E] for b in recs]
check("CryptoIf-submit retry budget +0x2E: sync 0, five ordinary 2",
      lim2e == [0, 2, 2, 2, 2, 2], str(lim2e))
# FUN_0008E166 owns fresh-PDU admission. The raw writes at 0x8E1A0/0x8E1A2
# zero FEBE550C/FEBE550E in the D2 admission arm; pin the complete function so
# the retry budgets cannot again be misread as persistent cross-frame counters.
check("fresh-PDU admission helper exact body pins per-frame retry reset",
      hashlib.sha256(fw[va_file(0x8E166):va_file(0x8E166) + 66]).hexdigest()
      == "36a81b38ac5106dee1068526e91b7c33aff0fd8e6df4540868229a0bb2b58dfc")
check("fresh-PDU admission zeroes both retry counters at 0x8E1A0/0x8E1A2",
      fw[va_file(0x8E19C):va_file(0x8E1A8)] == bytes.fromhex("24f60c9d8004810440067f00"))
# The +0x10 and +0x2E limits are consumed by different helpers.
check("wrong-MAC/current-PDU helper exact body is 0x8E382",
      hashlib.sha256(fw[va_file(0x8E382):va_file(0x8E382) + 104]).hexdigest()
      == "6d1250c3a12079c7de2ca965822e7c091c84ad0ba74db083bc3d918478d7ade2")
check("CryptoIf-submit retry helper exact body is 0x8E426",
      hashlib.sha256(fw[va_file(0x8E426):va_file(0x8E426) + 92]).hexdigest()
      == "3562b9de405f3ae6069011d43fcef0349dbe072c62e7bce653fcb26c3e489046")
# Global callbacks are three distinct slots; all records also carry the same
# per-profile +0x4C callback. 0x8E36C is the separate freshness-result-0x24
# dispatcher through slot 0x25944, while 0x8E30A is the generic failure path.
hooks = struct.unpack_from("<3I", fw, va_file(0x25940))
check("global status-hook slots == 6911C/69116/691EA",
      list(hooks) == [0x6911C, 0x69116, 0x691EA], " ".join(f"{h:x}" for h in hooks))
profile_hooks = [struct.unpack_from("<I", fw, va_file(b) + 0x4C)[0] for b in recs]
check("all per-profile +0x4C callbacks are 0x69182", profile_hooks == [0x69182] * 6,
      " ".join(f"{h:x}" for h in profile_hooks))
check("freshness-result callback dispatcher 0x8E36C body is pinned separately",
      hashlib.sha256(fw[va_file(0x8E36C):va_file(0x8E36C) + 22]).hexdigest()
      == "7a616930f2da5d88e211e6a1b4810ab71d19e77e2f04927b4f340a8646ae43b0")
check("generic failure callback dispatcher 0x8E30A body is pinned separately",
      hashlib.sha256(fw[va_file(0x8E30A):va_file(0x8E30A) + 98]).hexdigest()
      == "6f0ab67025d52b235d475bcc11fc33f2ddb54f36690e3b778670a3bfcb08b8bc")
# KAT config word0 must be 1: icus_cmac_verify_prepare (0x87ED0) rejects *config != 1,
# and the stored config passes, so the sole KAT kill switch remains gate byte
# 0x30EF3 == 0x00 (SECOC-004). Guards against future "doubly dead KAT" misreads.
_kat0 = struct.unpack_from("<I", fw, va_file(0x21604))[0]
check("KAT config word0 == 1 (passes prepare validation)", _kat0 == 1, hex(_kat0))

print(f"\n== RESULT: {ok} passed, {bad} failed ==")
sys.exit(1 if bad else 0)
