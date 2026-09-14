#!/usr/bin/env python3
"""Verify the yc Venza airbag reprogramming/extended-user-area invariants."""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BOOT = REPO / "community/yc/venza/boot.bin"
CFLASH = REPO / "community/yc/venza/cflash.bin"
EPS_CFLASH = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"

BOOT_SHA = "943934abc9a5c676eff46f51f008baa39e4f533e66650ffcce54d7bfb6e6e6e2"
CFLASH_SHA = "2dfaf7ce21cb04af1126192f574103f63802352f8717fa0f03986d5a11d067f9"
PAYLOAD_BUILD_ROOT = bytes.fromhex("8af2c4708cd9cdec494da7acdaa9a8f7")
BOOT_SECURITY_ACCESS_ROOT = bytes.fromhex("8f69e6dc2a4b80b45054b4827a5ab622")
EPS_ROOTS = (
    bytes.fromhex("ba052435f8843f985fd1329d2b6117b0"),
    bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044"),
    bytes.fromhex("893e08418c741ffa2a9c044bffa55813"),
)
COPY = struct.Struct("<III")
SERVICE = struct.Struct("<IIIIBBBBB3x")
SUBFUNCTION = struct.Struct("<IIIHH")

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


boot = BOOT.read_bytes()
cf = CFLASH.read_bytes()
eps_cf = EPS_CFLASH.read_bytes()

print("== immutable contributor artifacts ==")
check("boot.bin is the exact 32-KiB artifact", len(boot) == 0x8000 and sha256(boot) == BOOT_SHA)
check("cflash.bin is the exact 3-MiB artifact", len(cf) == 0x300000 and sha256(cf) == CFLASH_SHA)
check("RPRG build tag is at the extended-user tail", boot[0x7FD0:0x7FE2] == b"AUBIST_RPRG_201902")
check("raw airbag identity 8917048E30 is retained", cf[0x17FFC6:0x17FFD0] == b"8917048E30")
check("raw airbag identity 8917F48692 is retained", cf[0x17FFD0:0x17FFDA] == b"8917F48692")

print("\n== extended-user image is a split RAM-loaded RPRG segment ==")
check("first relocation group header is exact", struct.unpack_from("<II", cf, 0x1914) == (3, 0x1954))
check("second relocation group header is exact", struct.unpack_from("<II", cf, 0x191C) == (3, 0x1978))
first_group = [COPY.unpack_from(cf, 0x1954 + i * COPY.size) for i in range(3)]
second_group = [COPY.unpack_from(cf, 0x1978 + i * COPY.size) for i in range(3)]
check("CodeFlash runtime segment ends at logical 0xA304", first_group[0] == (0xFEBEA7B0, 0x4190, 0xA304))
check("extended user 0x01000000..0x01007588 copies to FEBF0924", first_group[1] == (0xFEBF0924, 0x01000000, 0x01007588))
check("extended user 0x01007588..0x01007BD0 copies to FEBFBF90", second_group[1] == (0xFEBFBF90, 0x01007588, 0x01007BD0))
check("relocated CodeFlash seam is contiguous with RPRG destination", first_group[0][0] + (first_group[0][2] - first_group[0][1]) == first_group[1][0])
check("logical call at 0x83E0 retains the A304 split-image target encoding", cf[0x83E0:0x83E6] == bytes.fromhex("ff02241f0000"))

print("\n== DiagnosticSessionControl programming route ==")
svc10 = SERVICE.unpack_from(cf, 0x23C18)
check("service group has SID 0x10 with five subfunctions", svc10 == (0, 0, 0, 0x237D0, 0x10, 1, 0, 0, 5))
programming = SUBFUNCTION.unpack_from(cf, 0x237E0)
check("SID 0x10 subfunction 0x02 dispatches to C190C", programming == (0xC190C, 0, 0x2356A, 0x02, 3))
check("programming subfunction permits current sessions 1/3/2", cf[0x2356A:0x2356D] == bytes([1, 3, 2]))
check("C190C wrapper is exact", cf[0xC190C:0xC191C] == bytes.fromhex("800721008600024280ffc41940063f00"))

print("\n== retained programming handoff ==")
check(
    "handoff writer targets FEF0FFD0 and embeds 5AA5A55A",
    cf[0xC76C6:0xC7728]
    == bytes.fromhex(
        "3e06d0fff0fe020a800b81038203079a839b209e8000849b8503860387038803"
        "209e1000899b019a8a9b8b0b8c038d038e038f03900391039203930394039503"
        "96039703980399039a039b039c039d039e039f0321065aa5a55a405ef1fe6b0f"
        "f1ff"
    ),
)
check(
    "session event 6 performs the two 0x200 hardware writes then halt path",
    cf[0xC780E:0xC7838]
    == bytes.fromhex(
        "86006632ea0d200e000280078f0e0ef080078f0e10f0e0076001e00720018505"
        "00527f0000527f00405e"
    ),
)
check(
    "startup magic test is exact",
    cf[0x17BC:0x17D2] == bytes.fromhex("409ef1fe339ff1ff21065aa5a55ae199ea5700007f00"),
)
check("startup immediately has a dedicated magic-clear helper", cf[0x17D2:0x17DC] == bytes.fromhex("405ef1fe6b07f1ff7f00"))

print("\n== reprogramming SecurityAccess and payload-build roots ==")
check("payload-build root is the unique 16-byte block at C3AC", cf[0xC3AC:0xC3BC] == PAYLOAD_BUILD_ROOT and cf.count(PAYLOAD_BUILD_ROOT) == 1)
check("boot SecurityAccess root is the adjacent unique block at C3BC", cf[0xC3BC:0xC3CC] == BOOT_SECURITY_ACCESS_ROOT and cf.count(BOOT_SECURITY_ACCESS_ROOT) == 1)
check("yc roots are distinct from all three tracked EPS roots", all(root not in cf and root not in boot for root in EPS_ROOTS))
common_crypto_copy = second_group[0]
check("common crypto/data segment relocates BBAC..C3CC to FEBFB770", common_crypto_copy == (0xFEBFB770, 0xBBAC, 0xC3CC))
payload_root_runtime = common_crypto_copy[0] + (0xC3AC - common_crypto_copy[1])
boot_sa_root_runtime = common_crypto_copy[0] + (0xC3BC - common_crypto_copy[1])
check("payload-build root relocates to FEBFBF70", payload_root_runtime == 0xFEBFBF70)
check("boot-SA root relocates to FEBFBF80", boot_sa_root_runtime == 0xFEBFBF80)
check("payload-root indirection at source C100 points to relocated FEBFBF70", struct.unpack_from("<I", cf, 0xC100)[0] == payload_root_runtime)
check("boot-SA indirection at source C1CC points to relocated FEBFBF80", struct.unpack_from("<I", cf, 0xC1CC)[0] == boot_sa_root_runtime)
check("runtime TP geometry selects C100 payload-root pointer via TP-735C", 0xFEC03020 - 0x735C == common_crypto_copy[0] + (0xC100 - common_crypto_copy[1]))
check("runtime TP geometry selects C1CC boot-SA pointer via TP-7290", 0xFEC03020 - 0x7290 == common_crypto_copy[0] + (0xC1CC - common_crypto_copy[1]))

print("\n== payload key derivation inputs and RequestDownload hook ==")
check("WDBI dispatcher 0201/0202/0203 body is exact", sha256(cf[0x654A:0x65CA]) == "e0f663505921b223617bac3e489758ad86e6e4336d47ea8749085f6e8db9a68e")
check("DID 0201 16-byte writer body is exact", sha256(cf[0x64DE:0x6514]) == "957f8a809e1b815c5fcf761ecde5abebe93883886870e54c07bec3fb143d9e10")
check("DID 0202 16-byte writer body is exact", sha256(cf[0x6514:0x654A]) == "54313cd1942d52d8b20616075f0b3502c61de546290f93a4d687c463ffb891a0")
check("payload AES root/KDF body is exact", sha256(cf[0x62A6:0x630A]) == "61f9ad9ee0d57b8213ca2cae8148f48567df49fb08d29620c2065a4af5edffa3")
check("derived-key plus DID0202 IV context body is exact", sha256(cf[0x630A:0x635C]) == "794f64e77c83e66bd422fc7c1faa3dbd591e26bbd07214053e666985a5ee343e")
check("RequestDownload normal-path branch containing relocated 7A4C KDF call is exact", sha256(boot[0x3F14:0x3FD6]) == "839753a894a67316be5bb67cf10ecb154c3a7921353f764ada56b3e03cf93282")

print("\n== boot SecurityAccess AES construction ==")
check("boot-SA root transform body is exact", sha256(cf[0x77B4:0x77EC]) == "8fca2937edca82d96acd22e43004724024afd4c133dccea2ff6403a1efc8be53")
check("boot-SA expected-key transform body is exact", sha256(cf[0x77EC:0x7820]) == "b8ef89653e0a785943ba84cdfb6791ed4b346f21e7bb42c0189fcbe2e790bc5b")
check("boot-SA 16-byte key compare body is exact", sha256(cf[0x7820:0x78DC]) == "174830b17c7830fc69f2f441af464687ba32d208757b3444449186007f817f9d")

print("\n== application SecOC secure-service boundary ==")
# Application startup fixes TP=0x24050. SecOC init then passes TP-0x69A8 =
# 0x1D6A8 into the single supported crypto-config setter. This 20-byte object is
# byte-identical to the tracked EPS type-1 / logical-selector-4 config object.
check("application startup fixes TP at 0x24050", cf[0x108E8:0x108EE] == bytes.fromhex("250650400200"))
secoc_key_config = cf[0x1D6A8:0x1D6BC]
check(
    "SecOC crypto config is exact type-1 / logical selector 4",
    secoc_key_config == bytes.fromhex("0100000004000000000000000000000000000000"),
)
check(
    "airbag SecOC selector-4 config is byte-identical to the canonical EPS config",
    secoc_key_config == eps_cf[0x25950:0x25964],
)
check("SecOC init body is exact", sha256(cf[0xDD6F4:0xDD736]) == "b1a2e3c511c1d8b4f182049afc545967aa48ac65c5787f0949895761c2398f19")
check("SecOC crypto-config setter body is exact", sha256(cf[0xDDC0A:0xDDC5C]) == "7eeaf66074689b8671d134add37f08e205bb40192747d0b1e49e9875abc84190")
check("SecOC crypto-config getter body is exact", sha256(cf[0xDDC5C:0xDDC92]) == "e8538aa55c58103e324b4b05793ab6d0545cf7a8e094e9e955e6816745464155")
check("SecOC route-set descriptor body is exact", sha256(cf[0xDD23A:0xDD27A]) == "466bf18016d6a5224dbf3dd206818cd1040d6933ae5c3faf654657761763d31f")
check("route set 0 declares two entries", cf[0xDD256:0xDD258] == bytes.fromhex("020a"))
check("route set 1 declares four entries", cf[0xDD272:0xDD274] == bytes.fromhex("040a"))
check("TX scheduler selects route set 0 and reaches TX worker", sha256(cf[0xDEB58:0xDEBBE]) == "f02334a94abaa68b9e3632ebfc99b8f95c4eca695f7cebc819a2aec0f70d600c")
check("RX scheduler selects route set 1 and reaches RX worker", sha256(cf[0xDE27A:0xDE2F4]) == "60d7163904933b90ba2862ed37abf8161f1bbeb8d5b56ea3641f3750c8cdb2eb")

secoc_rx_profiles = (
    (0x1D6C8, 0x00F, 8, "ed0d2d403d752d0bad2c7c922fff53fd6e110d2bd521ceb674fed77ab86a1270"),
    (0x1D718, 0x090, 32, "aa57b49a9975bd312800c5bf5f99ad8608e93be460453b778d26189babbdaa6b"),
    (0x1D768, 0x0D7, 32, "ed1146f6d5e88ce5f2faec28fb15bd0e1276b308daf70c87b0cc8c16d58c3077"),
    (0x1D7B8, 0x024, 32, "b749a52a24ee7d05d9394940614113b2383b42b8b0bbc44e9c65ac0020077e12"),
)
for off, data_id, configured_len, digest in secoc_rx_profiles:
    check(f"SecOC receive record {off:#x} is byte-pinned", sha256(cf[off:off + 0x50]) == digest)
    check(f"SecOC receive record {off:#x} carries DataID {data_id:#x}", struct.unpack_from("<H", cf, off + 0x0A)[0] == data_id)
    check(f"SecOC receive record {off:#x} carries configured PDU/buffer length {configured_len}", struct.unpack_from("<I", cf, off + 0x24)[0] == configured_len)
    check(f"SecOC receive record {off:#x} selects crypto config 0", struct.unpack_from("<H", cf, off + 0x16)[0] == 0)

# TX uses a distinct generated descriptor type with a 0x44-byte stride. The TX
# worker places the u16 at +0x0C into the authenticated material as the DataID.
secoc_tx_profiles = (
    (0x1D808, 0x0326, "e3e7cfa8602a668580e761f49316517c10fe542020b6e53e44f725b88980e003"),
    (0x1D84C, 0x0024, "587b5a86f2c76750ff85534a57427c89d3cbef5cba9ab34b39aee50f02e06f7a"),
)
for off, data_id, digest in secoc_tx_profiles:
    check(f"SecOC transmit record {off:#x} is exact 0x44-byte profile", sha256(cf[off:off + 0x44]) == digest)
    check(f"SecOC transmit record {off:#x} carries authenticated DataID {data_id:#x}", struct.unpack_from("<H", cf, off + 0x0C)[0] == data_id)
    check(f"SecOC transmit record {off:#x} selects crypto config 0", struct.unpack_from("<H", cf, off + 0x16)[0] == 0)

check("SecOC RX verification worker body is exact", sha256(cf[0xDE09E:0xDE240]) == "71897f7543e1dce29971da1967929fc6c0fca6994ab734d0f8c0ea68b50d140a")
check("SecOC TX generation worker body is exact", sha256(cf[0xDE9F0:0xDEB58]) == "ea373a29ee2eb29c004b1f344a5ce5c76480bda45b79efd18ce78a51c0f0aeaa")
check("SecOC TX secure-service adapter body is exact", sha256(cf[0xBDC7A:0xBDD72]) == "13a19535fb14336b33285b3f3f1dedfb2a637e8914157560de7131049b327d8b")
check("SecOC RX secure-service adapter body is exact", sha256(cf[0xBDE88:0xBDFC6]) == "a44d62e63363a6c6170adc1ec126093ee7cd87b043cb27ffc958dd8fac759d98")
check("secure request enqueue wrapper is exact", sha256(cf[0x8A18A:0x8A1F0]) == "0de122986c51d93ab0dcf75e2134fc5f51ea9a1f70bec49b158cf53b359a62a3")
check("secure shared-RAM queue body is exact", sha256(cf[0x89E60:0x89ED0]) == "bb0541973644e0ab89b5a66a8534a04a3960464fa3aaf6fe53ebae2333d463c8")
check("secure service trigger body is exact", sha256(cf[0x89F6E:0x89FC4]) == "8675acdb3e9932632c7f6bc321ec318e3b4fdbc7302bd607d27612ce49a4f11f")

print("\n== authenticated ECU Security Key update: RoutineControl RID 0x1010 ==")
check("application RoutineControl table has 19 entries", struct.unpack_from("<H", cf, 0x2506C)[0] == 19)
rid_table = cf[0x255E4:0x255E4 + 19 * 8]
check("19-entry RoutineControl table is byte-pinned", sha256(rid_table) == "37a6786788f944c737ddb73daec9d24ba98edc899119289a08bbd2b491414474")
check("RoutineControl table index 9 is RID 0x1010", struct.unpack_from("<H", rid_table, 9 * 8)[0] == 0x1010)
check("RID 0x1010 start staging body is exact", sha256(cf[0x7B306:0x7B370]) == "135a3d6da6241665554bad3a84615bb34e8c6566cc2403b4ecde2fc0dcccd063")
check("RID 0x1010 result body is exact", sha256(cf[0x7B3A6:0x7B414]) == "7030ff37050ff7c7be38ef982b21613a65c5d00f43abcc703050eb8bca445a77")
check("RID 0x1010 key-update worker is exact", sha256(cf[0xB76D4:0xB77B8]) == "87a24689ed7d1960839fde41739860af629898b3ef59c395e72fd4ad12554327")
check("authenticated key-update dispatcher is exact", sha256(cf[0xBD2EC:0xBD37C]) == "1e174b5310cb2c445fe5a010b40bdd5d991c7442dfe9d7ace56cb9252a337550")
check("authenticated 64-byte/48-byte lower adapter is exact", sha256(cf[0xBE0CC:0xBE1DA]) == "adea5483aa15706e8fcae2ee368143584e92037f3e7b2c01d5893fa3e219ca27")
check("RoutineControl application dispatcher body is exact", sha256(cf[0xC6672:0xC6776]) == "e7dbd1793c2df4dc30efd47dcea3f51e67b29043053ed7085531aa4839b49212")

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
