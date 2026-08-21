# Community exploit tooling — provenance and status

This directory holds analysis code received from the comma community
that independently corroborates or extends this repository's findings. Unlike
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

### Cross-validation value

These tools confirm — with independent authorship — the following
repository findings:

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
