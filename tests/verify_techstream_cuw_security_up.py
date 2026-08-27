#!/usr/bin/env python3
"""Verify the recovered CUW SecurityUp AES construction against pinned V18 PEs."""
from __future__ import annotations

import sys
from pathlib import Path

import pefile
from Crypto.Cipher import AES

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard"
sys.path.insert(0, str(REPO / "tools/techstream"))
from cuw_security_up import (  # noqa: E402
    SECURITY_UP_WRAP_KEY,
    calculate_security_up_response,
    decode_cuw_block,
    firmware_security_access_working_key,
    unwrap_service_auth_key,
)

passed = failed = 0
oracle = "raw_bytes"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


if not ROOT.is_dir():
    print("[SKIP] pinned Techstream V18 tree is unavailable")
    raise SystemExit(77)

common_path = ROOT / "TCUWCanCommonPrepareWriter.dll"
unified_flash_path = ROOT / "TCUWCanUnifiedFlashWriter.dll"
cuw_path = ROOT / "Cuw.exe"
common = common_path.read_bytes()
unified_flash = unified_flash_path.read_bytes()
cuw = cuw_path.read_bytes()
common_pe = pefile.PE(data=common)
unified_flash_pe = pefile.PE(data=unified_flash)
cuw_pe = pefile.PE(data=cuw)


def rva_bytes(pe: pefile.PE, data: bytes, rva: int, size: int) -> bytes:
    return data[pe.get_offset_from_rva(rva):][:size]


print("== selector-0 SecurityUp wrapper key ==")
wrap_text = rva_bytes(common_pe, common, 0x31D8, 33)
check("selector-0 table entry is the recovered AES wrapper key",
      wrap_text == b"B45B26D6344FD60E80BC01D63C7584A0\x00")
check("wrapper key decoder agrees with raw table", bytes.fromhex(wrap_text[:-1].decode()) == SECURITY_UP_WRAP_KEY)
check("selector-0 discriminator is zero", rva_bytes(common_pe, common, 0x33DC, 4) == b"\x00\x00\x00\x00")

print("\n== CalcSeedKeyForSecurityUp callback order ==")
calc = rva_bytes(common_pe, common, 0x1310, 0xE5)
# The function pushes selector 0 before calling its key-table helper, invokes
# callback +0x58 first, formats its 16-byte result with %02X, then invokes
# callback +0x54.  Cuw.exe initializes +0x58 as decrypt and +0x54 as encrypt.
selector_push = calc.find(b"\x6a\x00")
selector_lookup = calc.find(bytes.fromhex("e8befcffff"))
check("SecurityUp requests key-table selector 0",
      0 <= selector_push < selector_lookup and selector_lookup - selector_push < 0x20)
first_decrypt = calc.find(bytes.fromhex("8b4958"))
second_encrypt = calc.find(bytes.fromhex("8b4b54"))
check("SecurityUp invokes callback +0x58 before +0x54", 0 <= first_decrypt < second_encrypt)
check("SecurityUp hex-formats the 16-byte stage-1 key", b"%02X\x00" in common)

print("\n== Cuw.exe callback bindings and CryptoAPI AES mode ==")
# The callback wrappers are short rel32-call shims.  Pin the complete call
# chain rather than trusting decompiler-assigned names:
#   +0x54 -> 0x487374 -> 0x489748 -> CAES::GetEncryptedData @ 0x566dd8
#   +0x58 -> 0x487390 -> 0x48983c -> CAES::GetDecryptedData @ 0x5674c4

def rel32_targets(body: bytes, base_va: int) -> set[int]:
    targets: set[int] = set()
    for index in range(len(body) - 4):
        if body[index] != 0xE8:
            continue
        displacement = int.from_bytes(body[index + 1:index + 5], "little", signed=True)
        targets.add(base_va + index + 5 + displacement)
    return targets


enc_cb = rva_bytes(cuw_pe, cuw, 0x87374, 0x1C)
dec_cb = rva_bytes(cuw_pe, cuw, 0x87390, 0x1C)
enc_wrapper = rva_bytes(cuw_pe, cuw, 0x89748, 0x80)
dec_wrapper = rva_bytes(cuw_pe, cuw, 0x8983C, 0x80)
check("callback +0x54 wrapper reaches encrypt adapter",
      0x00489748 in rel32_targets(enc_cb, 0x00487374))
check("callback +0x58 wrapper reaches decrypt adapter",
      0x0048983C in rel32_targets(dec_cb, 0x00487390))
check("encrypt adapter reaches CAES::GetEncryptedData",
      0x00566DD8 in rel32_targets(enc_wrapper, 0x00489748))
check("decrypt adapter reaches CAES::GetDecryptedData",
      0x005674C4 in rel32_targets(dec_wrapper, 0x0048983C))
imports = {symbol.name.decode("latin1") for lib in cuw_pe.DIRECTORY_ENTRY_IMPORT
           for symbol in lib.imports if symbol.name}
check("Cuw.exe imports CryptEncrypt/CryptDecrypt/CryptImportKey/CryptSetKeyParam",
      {"CryptEncrypt", "CryptDecrypt", "CryptImportKey", "CryptSetKeyParam"} <= imports)
# ImportKey writes CALG_AES_128 (0x660e) into the PLAINTEXTKEYBLOB; mode setup
# passes KP_MODE=4 with CRYPT_MODE_ECB=2 to CryptSetKeyParam.
import_key = rva_bytes(cuw_pe, cuw, 0x16703C, 0x180)
set_mode = rva_bytes(cuw_pe, cuw, 0x1671C0, 0x90)
check("CAES ImportKey selects CALG_AES_128", (0x660E).to_bytes(4, "little") in import_key)
check("CAES SetEncryptionMode carries ECB mode value 2", b"\x02\x00\x00\x00" in set_mode)
check("CAES SetEncryptionMode passes KP_MODE parameter 4", b"\x6a\x04" in set_mode)

print("\n== CUW hex-field parsing width ==")
# CBytes(string) divides strlen by two and parses pairs as base-16; the auth
# parser copies exactly 0x10 bytes from those CBytes into fixed fields.
cbytes_ctor = rva_bytes(cuw_pe, cuw, 0x199F8, 0x140)
check("CBytes(string) contains base-16 conversion", b"\x6a\x10" in cbytes_ctor)
check("auth parser names ECUAuthKey and ServiceAuthKey", b"ECUAuthKey\x00" in cuw and b"ServiceAuthKey\x00" in cuw)
check("ECUAuthKey parser performs a fixed 16-byte copy",
      rva_bytes(cuw_pe, cuw, 0x551A, 2) == b"\x6a\x10")
check("ServiceAuthKey parser performs a fixed 16-byte copy",
      rva_bytes(cuw_pe, cuw, 0x5661, 2) == b"\x6a\x10")
check("SeedKey parser performs a fixed 16-byte copy",
      rva_bytes(cuw_pe, cuw, 0x6F9C, 2) == b"\x6a\x10")
check("Nonce parser performs a fixed 16-byte copy",
      rva_bytes(cuw_pe, cuw, 0x7116, 2) == b"\x6a\x10")

print("\n== SecurityProperty2 separation ==")
def imported_names(pe: pefile.PE) -> set[str]:
    return {symbol.name.decode("latin1") for lib in pe.DIRECTORY_ENTRY_IMPORT
            for symbol in lib.imports if symbol.name}


common_imports = imported_names(common_pe)
unified_flash_imports = imported_names(unified_flash_pe)
check("SecurityProperty2 is not an input to the common SecurityUp prepare DLL",
      not any("GetSecurityProperty2" in name for name in common_imports))
check("SecurityProperty2 is consumed by the unified flash writer",
      any("GetSecurityProperty2" in name for name in unified_flash_imports))
check("unified flash writer has no CryptoAPI AES operations",
      not ({"CryptEncrypt", "CryptDecrypt", "CryptImportKey"} & unified_flash_imports))

print("\n== executable formula regression ==")
# Publicly observed CUW example from calibration 8966312R1100.  V18 consumes
# only the first 16 decoded bytes of each fixed-size field.
service_text = "4247354845484A394D40414D4E505040544749494757475C505C515351635152"
ecu_auth_text = "3146324645493E39383941514F3D524842425843565648485A5F52505551614F"
seed_key_text = "34453938383E39384D4C3F3D3C4E545441494A555A4858474C505B504F565462"
nonce_text = "413945473C35494D3C404E4F42413F5555554B49455B4E4F5B5A5E5E625F5F63"
service = decode_cuw_block(service_text)
ecu_auth = decode_cuw_block(ecu_auth_text)
seed_key = decode_cuw_block(seed_key_text)
nonce = decode_cuw_block(nonce_text)
check("32-byte ServiceAuthKey text truncates to first 16 bytes", service.hex() == "4247354845484a394d40414d4e505040")
check("32-byte ECUAuthKey text truncates to first 16 bytes", ecu_auth.hex() == "3146324645493e39383941514f3d5248")
check("32-byte SeedKey text truncates to first 16 bytes", seed_key.hex() == "34453938383e39384d4c3f3d3c4e5454")
check("32-byte Nonce text truncates to first 16 bytes", nonce.hex() == "413945473c35494d3c404e4f42413f55")
working = unwrap_service_auth_key(service)
check("sample ServiceAuthKey unwrap vector", working.hex() == "140ff15b66e1f32564bc64c927c3334f")

# Algebraic bridge check: construct a credential pair that wraps the same
# working key on the host and ECU sides.  This does not claim that a particular
# CUW matches the Sienna; it proves the recovered constructions coincide when
# their provisioned working keys coincide.
family_secret = bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044")
synthetic_working = bytes.fromhex("00112233445566778899aabbccddeeff")
synthetic_service = AES.new(SECURITY_UP_WRAP_KEY, AES.MODE_ECB).encrypt(synthetic_working)
synthetic_ecu_auth = AES.new(family_secret, AES.MODE_ECB).encrypt(synthetic_working)
seed = bytes.fromhex("ffeeddccbbaa99887766554433221100")
check("host unwrap recovers provisioned working key", unwrap_service_auth_key(synthetic_service) == synthetic_working)
check("firmware DEC(root, ECUAuthKey) recovers same working key",
      firmware_security_access_working_key(family_secret, synthetic_ecu_auth) == synthetic_working)
check("host response matches firmware-side AES-ENC(working, seed)",
      calculate_security_up_response(seed, synthetic_service)
      == AES.new(synthetic_working, AES.MODE_ECB).encrypt(seed))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
