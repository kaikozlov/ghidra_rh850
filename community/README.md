# Community exploit tooling — provenance and status

This directory holds exploit/analysis code received from the comma community
that independently corroborates or extends this repository's findings. Unlike
the git-pinned repositories in `external-references.lock.json` (I-CAN-hack,
Bk2ol, calvinpark), these artifacts were distributed via Discord and have no
canonical git source. They are committed in-tree with SHA-256 hashes and
provenance metadata in `../external-references.lock.json` under
`community_artifacts`.

## `blurbdust_secoc_flash_patcher/`

**Author:** blurbdust (`@yc`)
**Channel:** comma Discord, EPS/SecOC discussion, 2026-08-01
**Status per author:** "largely untested so don't go out and flash everyone's
cars" — verification checks forced to always return true, which also accepts
malformed packets.

| File | Purpose |
|---|---|
| `flash_patcher.py` | SecOC flash patcher host tool. Implements the authenticated-RAM-exec bootstrap (SA → WDBI 0x203/0x201/0x202 → RequestDownload 0xFEBF0000 → RoutineControl 0x10F0/0xFF00), uploads shellcode, triggers via `0xE0000` routine, and decodes progress frames over CAN 0x7A9. |
| `main.c` | Egg-hunter shellcode (C source). Runs from the boot-context callback, scans CodeFlash for an 8-byte egg marker, patches the SecOC MAC verification to always-pass (`0x007f5201`), fixes the bootloader CRC32, and returns over CAN. |
| `decrypt.T-0035-22.py` | CUW (Calibration Update Wizard) decryption tool. Documents the per-byte SeedKey/Nonce obfuscation (`out[i] = raw[i] - i mod 256` → ASCII hex → 16 bytes) and the `AES_ECB(BL_KEY, DID_201)` derivation matching SEC-BOOT-003. |

### Cross-validation value

These tools confirm — with independent authorship — the following
repository findings:

- **SEC-BOOT-002/003/005/006/007** — SA secret, algorithm, DID sequence,
  download address, execution trigger all match exactly.
- **SECOC-024** — the authenticated-RAM-exec bootstrap is a solved,
  reusable toolchain across the 8965B4x family.
- The CUW deobfuscation scheme fills a gap in `docs/tooling/techstream.md`.

### New directions not yet in repository findings

- **Persistent CodeFlash patching via FCU** — the shellcode uses Flash
  Control Unit registers (FACI at 0xFFA1xxxx) to erase/reprogram CodeFlash
  blocks. The CRC repair geometry (range `0x18000..0xFFDF0`, adjustment word
  at `0xFFDEC`, marker at `0xFFE00`) matches the Sienna boot layout exactly.
  However, the 8-byte egg marker is a **false positive** on `8965B4512000`:
  it matches a 5-byte `memcmp` helper in the `0xAB` event-record dispatch
  path (`FUN_0003485A` at VA `0x3485A`), not the SecOC verify function
  (`secoc_rx_verify_worker` at `0x8E4BA`). The egg was designed for the
  `8965F3`/`8965F4` family; it does not transfer to this calibration.
  See SECOC-028 and `verify_community_tooling.py` §6–7.
- **Extended version family** — targets 8965F3401200 (dual-CPU),
  8965F4207000, 8965F4201000, 8965B4209000, 8965B4233100, 8965B4509100.
  The 8965F3 dual-CPU part is a new family.
- **Steering angle sensor pivot** — yc's strategic suggestion to target the
  SAS instead of the EPS, since it uses the same RH850 and is less
  safety-critical.

These are unverified (author notes "largely untested") and are committed for
reference and cross-validation, not as proven tooling.
