# Community exploit tooling — provenance and status

This directory holds analysis code received from the comma community
that corroborates or extends this repository's findings. Unlike
the git-pinned repositories in `external-references.lock.json` (I-CAN-hack,
Bk2ol, calvinpark), they are committed in-tree with SHA-256 hashes and
provenance metadata in `../external-references.lock.json` under `community_artifacts`.

## `blurbdust_secoc_flash_patcher/`

**Author:** blurbdust 
**Channel:** comma Discord, EPS/SecOC discussion, 2026-08-01
**Status per author:** "largely untested so don't go out and flash everyone's
cars" — verification checks forced to always return true, which also accepts
malformed packets.

| File | Purpose |
|---|---|
| `flash_patcher.py` | SecOC flash patcher host tool. Implements the authenticated-RAM-exec bootstrap (SA → WDBI 0x203/0x201/0x202 → RequestDownload 0xFEBF0000 → RoutineControl 0x10F0/0xFF00), uploads shellcode, triggers via `0xE0000` routine, and decodes progress frames over CAN 0x7A9. |
| `main.c` | Egg-hunter shellcode (C source). Runs from the boot-context callback, scans CodeFlash for an 8-byte egg marker, forces the matched predicate to return success (`0x007f5201`), re-signs the boot CRC from live CodeFlash, and returns over CAN. On `8965B4512000` the egg target does not transfer, but the FCU RMW and CRC-resigning mechanism does. |
| `decrypt.T-0035-22.py` | CUW (Calibration Update Wizard) decryption tool. Documents the per-byte SeedKey/Nonce obfuscation (`out[i] = raw[i] - i mod 256` → ASCII hex → 16 bytes) and the `AES_ECB(BL_KEY, DID_201)` derivation matching SEC-BOOT-003. |

### Provenance bridge: the Discord bundle and public Git are one lineage

The August Discord import was originally recorded as having no canonical Git
source. That is wrong for two of the three files. Public GitHub metadata shows
`blurbdust/secoc` was created on **2026-04-28** as a fork of
`I-CAN-hack/secoc`, and blurbdust added the flash patcher in three commits:

- `dbfd991bc817deca0c5c94e2fb5171d1142682c1` — 2026-04-28, `adding first pass at patching flash`;
- `846866d4a9b8a81327f1cd1e54114931ae60a39a` — 2026-04-28, second pass;
- `47d282428d2ad504e79120c35d492d1211142da6` — 2026-04-29, third pass and the pinned public tip.

There is an older public precursor that matters for attribution. Willem's
`I-CAN-hack/secoc` **`tundra` branch** at
`b80d9104a14bdf59d236a6a0de2a4a5c929a9d76` (2025-07-13, `make it work for
the tundra`) already contains the exact 72-byte `8965F3401200/8965F3402200`
application-version record, CPU0 DID-`0x0203` value `01 00 00 00 00`, and the
`45 01` new-UDS routine grammar. Blurbdust's host tool generalizes those ideas
to two CPUs; it does **not** byte-copy the Tundra RequestDownload prefix. Thus
the F340 identity/new-UDS plumbing are pre-existing I-CAN-hack lineage, not
independent evidence that blurbdust learned them from CUW extraction.

The retained `main.c` is **byte-identical** to public
`shellcode/main_flash_patch.c` at `47d2824` (SHA-256
`5fa6ef897e928e3f9cacc13a5eac59a5708791a0ae1a32f17a6cf2a7781f505a`).
The retained `flash_patcher.py` is the same public host tool except for exactly
two progress-frame decode format strings: the Discord copy uses little-endian
`struct.unpack("<I", ...)`, while public Git uses `">I"`. The flash/deployment
logic is otherwise identical. `decrypt.T-0035-22.py` still has no public Git
source.

The CUW chronology is unusually tight. The optskug timeline preserves
blurbdust's Discord message `1496150355224952995`, whose Discord snowflake
resolves to **2026-04-21 14:07:21 UTC**. In that message blurbdust says he has a
script that extracts the flash driver from the TechInfo `.cuw` package and
computes `0x201` and `0x202`. Seven days later, `dbfd991` adds the persistent FACI flash writer. Its host
wrapper still targets `8965F3401200/8965F3402200`, but that exact target record
and part of the new-UDS plumbing already existed on Willem's 2025 `tundra`
branch, so target identity itself is **not** evidence of CUW-derived authorship.
The retained decryptor is
specifically named `decrypt.T-0035-22.py`, parses `CPUImageN` and
`EraseRoutineN`, derives those two DIDs, and writes `{NewCID}_erase.pt.bin`.
This is strong evidence that the retained decryptor is the same private tool or
a direct descendant of the tool described on April 21, but no April attachment
hash survives, so byte identity is not proved.

The flash writer also has a distinctive OEM-shaped FACI sequence from its
**first** public commit. Its symbolic register names are wrong, but the MMIO
operations already line up closely with the manufacturer-corrected sequence
later documented by Lochuan:

| Operation | blurbdust first pass | Manufacturer-corrected interpretation |
|---|---|---|
| ready | `0xFFA10080 & 0x8000` | `FSTATR.FRDY`, correct |
| command lock | `0xFFA10010 & 0x10` | `FASTAT.CMDLK`, correct |
| P/E unlock | `0xFFA10084 = 0xAA01`, poll `==1` | `FENTRYR`, correct operation/address |
| HV/protection entry | `FFF8A430=1`, `FFF82410=1`, `FFA10020=3B00`, `FFA10088=5501` | `FHVE15/FHVE3/FAREASELC/FPROTR`, same operations |
| erase | `FFA100E0=1`, `FSADDR`, `20,D0` | `FPSADDR`, `FSADDR`, erase + execute, same sequence |
| program | `FSADDR`, `E8,80`, 128 halfwords, `D0` | same page-program sequence |
| halfword pacing | polls bit 21 | **wrong**; Toyota CUW uses FSTATR bit 11 / `0x800` (`SUSRDY`) |
| status/recovery | ready + command-lock only; `B3` cleanup | **incomplete**; Toyota path also uses FSTATR `0x7040`, Status Clear `0x50`, and bounded Forced Stop |

That pattern matters: the writer had the right raw register addresses, magic
values, and command sequence while several register *names* were shifted and
two status semantics were wrong. This is consistent with behavior reconstructed
from disassembly without a correct symbolic register map. Together with the
April-21 extractor statement, it makes CUW-informed FACI reconstruction
**plausible and worth investigating**; the inherited F340 target identity adds
context, not independent provenance evidence. It does not prove that
`main_flash_patch.c` was translated from Toyota's erase payload line-for-line.
The actual `T-0035-22.cuw`/plaintext `*_erase.pt.bin` remains necessary for that
comparison.

There is also a useful parser-layer boundary that our later Techstream work makes
explicit. `decrypt.T-0035-22.py` is a **payload-oriented extractor**: it scans
the supplied bytes for INI sections and S-record streams and knows how to turn
`CPUImageN`/`EraseRoutineN` ciphertext into plaintext. It does not validate the
outer CUW container magic, package CRC, declared size, or first-member CRC. Our
independently recovered V18 parser `tools/techstream/parse_cuw_container.py`
does exactly that outer validation for the `\0CALIBRATION\0` framing and
extracts the first `attach.att` member while preserving the format-specific tail.
Without a real `T-0035-22.cuw` specimen we cannot prove which supported format
type/tail layout that 2022 package uses, or whether blurbdust's script was meant
to consume the raw package or an already exposed package layer. The capture-safe
workflow is therefore: **preserve/hash raw CUW -> validate outer container ->
preserve/extract `attach.att` + tail -> run the T-0035 extractor against the
package layer it actually recognizes -> CMAC-check every plaintext output**.
This is another reason acquiring the real file remains valuable: it validates
both independently recovered parser layers, not just the FACI disassembly.

### Cross-validation value

These tools corroborate the following repository findings, but the public Git
lineage proves they are **not an independent source** for the inherited
I-CAN-hack authenticated-RAM-exec bootstrap. Blurbdust's independent additions
are the persistent flash writer/patch host and the separately shared CUW
decryptor:

- **SEC-BOOT-002/003/005/006/007** — SA secret, algorithm, DID sequence,
  download address, execution trigger all match exactly.
- **SECOC-024** — the authenticated-RAM-exec bootstrap is a solved,
  reusable toolchain across the 8965B4x family.
- The CUW deobfuscation scheme fills a gap in `docs/tooling/techstream.md`.

### Additional community-derived directions

- **Persistent CodeFlash patching via FCU + CRC resigning** — the shellcode uses
  Flash Control Unit registers (FACI at `0xFFA1xxxx`) to erase/reprogram
  CodeFlash blocks, then recomputes the CRC from the **live** flash prefix and
  writes its complement at `0xFFDEC`. The geometry (range
  `0x18000..0xFFDF0`, adjustment word `0xFFDEC`, marker `0xFFE00`) matches the
  Sienna boot layout exactly. Stock region 0 independently validates the same
  CRC-32/Ethernet terminal-fixup formula (`CRC(prefix)=0xEC0CD6CF`, stored
  complement `0x13F32930`, final residue `0xFFFFFFFF`). The published
  `8965B4512000` region-1 artifact itself has a one-bit anomaly at `0xBB1C4`:
  `0xA2→0x82` is the **unique** single-bit change that makes its existing
  `0x0962887F` fixup validate, and also repairs an anomalous `sst.b 0x22,ep,r1`
  into `sst.b 0x2,ep,r1`, completing a six-byte destination permutation
  `0..5`. This strongly indicates a one-bit acquisition error in the public
  dump, not a CRC-algorithm mismatch. The 8-byte egg marker is independently a
  **false positive as a SecOC signature** on this calibration: it matches the
  shared 5-byte token comparator (`FUN_0003485A` at VA `0x3485A`) used by the
  application SID `0xBA` proprietary operation table, not the SecOC Gate-2
  control flow. Forcing that comparator true removes BA token comparisons, but
  F7/`BAENA` still has an independent application SecurityAccess-level-2 check
  at `0x34D96`; the patch therefore does not create the persistent BA
  authorization state without SA2. See SECOC-028/035/043/044, SEC-APP-007, and
  `verify_community_tooling.py` §6–7.
- **Extended version family** — targets 8965F3401200 (dual-CPU),
  8965F4207000, 8965F4201000, 8965B4209000, 8965B4233100, 8965B4509100.
  The 8965F3 dual-CPU part is a new family.
- **Steering angle sensor pivot** — yc's strategic suggestion to target the
  SAS instead of the EPS, since it uses the same RH850 and is less
  safety-critical.

The author notes the complete patcher is "largely untested" on its target
calibrations. Repository analysis independently verifies the bootstrap,
CodeFlash/CRC mechanism, and the `4512000` dump anomaly; the `4512000` egg target is now semantically closed as
SID-`0xBA` token-comparison logic rather than SecOC acceptance logic. Future
F3/F4 egg matches still require calibration-specific semantic validation.

For comparison with yc's corrected Gate-2 patch, the independently published
Lochuan/3b1b `8965B4512000-FW-PATCH` repository is pinned in
`../external-references.lock.json`. Its **historical pre-2026-08-18**
`0x664E6: 0x31→0x10` target is a generic checkpoint/NvM failure-status fail-open,
not another Gate-2 encoding; see
[`docs/security/secoc/application-chain.md` §9.7](../docs/security/secoc/application-chain.md#97-yc-compare-neutralization-versus-lochuan3b1b-0x664e6-patch).
Commit `2188d5a...` subsequently removed that target and the current public tool
now independently matches the corrected Gate-2 compare neutralization at
`0x8E6C6 e0d1→e001` plus CRC fixup `0x41C90FF2`. Commit `390ddb7...` also
corrected the FACI program-pacing/status model; that refresh exposed and prompted
CORR-086 in our own persistent patcher. The older pinned `lochuan/RH850_P1m-E`
report is retained alongside the current checkout because its historical
misidentification of the checkpoint cone as SecOC MAC scheduling is a plausible
conceptual origin for the bad target. No surviving source explicitly states that
this misclassification caused the original `0x664E6` selection, so that final
provenance link remains an inference.

## `albinoelephant/`

**Contributor:** albinoelephant, comma Discord, 2026-08-12

**Vehicle attribution:** reported 2023 US Corolla. The later tracked CodeFlash
identifies the firmware artifact as `8965H1202000` / `8A3111202000` on
`R7F701383`; a direct UDS F181 transcript is still not retained.

This directory preserves the contributor's complete 2026-08-18 memory corpus
under `albinoelephant/raw-20260818/` (CodeFlash, DataFlash, global/local RAM,
and the earlier TSKM oracle), plus a compact CAN-only oracle derived from the
already-pinned public route. The contributor-supplied `MANIFEST.txt` pins every
raw file hash and acquisition note; the artifacts are immutable evidence inputs
rather than tooling.

The CodeFlash range dump normalizes to a one-megabyte image with SHA-256
`0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f`.
It independently transfers all three Sienna cryptographic roots, the semantic
Gate-2/CRC-resigning machinery, and the checkpoint semantics behind the old
Lochuan patch. Its Gate-2 queue is nevertheless variant-specific: exactly
`0x00F/0x0D7/0x0B6`, with no `0x2E4/0x131` steering profiles. This foreign
image exposed and now regression-tests the resolver's former Sienna-specific
queue/table assumptions.

The contributor's TSKM oracle contains synchronization `0x00F` only, explaining
the original matcher failure. The derived public-route oracle adds the genuine
bus-1 `0x116` and `0x24D` protected-family traffic already established in the
variant report. `tools/analyze_toyota_dataflash.py` can therefore test the
actual dump against all three observed domains offline. See
[`albinoelephant/README.md`](albinoelephant/README.md) and
[`docs/variants/corolla-2023-us-public-route.md`](../docs/variants/corolla-2023-us-public-route.md).
