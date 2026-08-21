# Lochuan `8965B4512000-FW-PATCH` refresh — 2026-08-20

## Purpose

Refresh the existing checkout of `lochuan/8965B4512000-FW-PATCH`, determine what changed after the previously pinned public-release commit, compare the changes against the canonical Sienna/Corolla reconstruction in this repository, and retain the resulting evidence even where it only corroborates existing work.

## Checkout refresh

Existing checkout:

```text
/Users/kai/dev/inspect/repos/8965B4512000-FW-PATCH
```

Previous pinned HEAD:

```text
e7c1f17d1090470b18f7f3315abd99b64e5e4619
chore: prepare repository for public release
```

Refreshed with a fast-forward-only pull to:

```text
9eed2b4ac871b1944e686769cc3e0a43fd7198c3
docs: rewrite README with slop-free prose and add CUW flash-parity section
```

The four new commits are:

| Commit | Date | Subject | Disposition |
|---|---|---|---|
| `2188d5a235d4ac1bf8c616266b8f6b472a047fdb` | 2026-08-18 | `chore: update source, payload and tests` | **Material:** replaces the old wrong `0x664E6` target with the corrected Gate-2 target already independently recovered here |
| `dc2abd7199f49b50b5f120c8d8852337f7e8ba5d` | 2026-08-18 | `docs: note verified vehicles (RAV4 Prime 2024, Sienna 2026 PRC)` | New vehicle claims; Sienna is now image-bound to the canonical `8965B4512000` donor, RAV4 remains artifact-unbound |
| `390ddb730ca24265c7935989e251f45545909d65` | 2026-08-20 | `fix: correct FACI poll bit, error mask and register names per manufacturer shellcode` | **Material:** exposes a correctness gap in our inherited FACI backend |
| `9eed2b4ac871b1944e686769cc3e0a43fd7198c3` | 2026-08-20 | `docs: rewrite README with slop-free prose and add CUW flash-parity section` | Documents claimed Toyota CUW shellcode parity and the corrected FACI model |

The refreshed upstream test suite passes with:

```text
PYTHONPATH=. uv run --python 3.12 --extra test pytest -q
504 passed
```

## 1. The current Lochuan patch now agrees with our Gate-2 patch

The most important semantic change is a correction by upstream, not a new bypass.

The old public manifest at `e7c1f17...` targeted:

```text
0x664E4  20 e6 31 00
             31 -> 10 at 0x664E6
```

This repository already proved that target is an ordinary checkpoint/NvM failure-status fail-open and not a SecOC acceptance predicate. That historical analysis remains valid for old commits and old field incidents.

Commit `2188d5a...` changes the current upstream manifest to:

```text
instruction context: 1d 30 e0 d1 -> 1d 30 e0 01
changed byte:         0x8E6C7 d1 -> 01
instruction:          0x8E6C6 e0 d1 -> e0 01
semantic effect:      cmp r0,r26 -> cmp r0,r0
```

It also carries:

```text
patched prefix CRC: 0xBE36F00D
terminal fixup:     0x41C90FF2
final residue:      0xFFFFFFFF
```

Those values exactly match the independently recovered local Sienna Gate-2 result in SECOC-043/045. This is useful independent convergence, but it does not advance the local proof frontier: our firmware-static resolver, branch-polarity proof, exact patch bytes, and CRC reconstruction already establish the result without trusting the external repository.

The refreshed README additionally says the corrected patch point, sector digests, and adjustment word were captured from an actual bench vehicle and validated through a complete `probe → patch → verify` run. That bench target is no longer identity-ambiguous. The current manifest is hard-locked to application F181 `01 8965B4512000 00000000`, and its original `0x88000..0x8FFFF` sector SHA-256 is `281a0ef918a1bd8e709bb579a7f19163d3e908eedb5bdf79ad7348c701177b01`. That digest exactly equals both the sector in Lochuan's pinned `RH850_P1M-E_Firmware.bin` and the canonical CodeFlash analyzed in this repository. Lochuan's original report identifies that donor as the Sienna CN EPS `8965B4512000`; operator provenance further identifies it as the PRC Sienna donor used for this analysis. The refreshed public patch repository still does not retain the newer run directory, raw protocol transcript, or CAN evidence, so the **execution transcript** remains external-source, but the bench ECU/image identity is bound to our source calibration rather than unknown.

The correct temporal interpretation is therefore:

- **historical Lochuan patch:** `0x664E6 31->10`, disproved as a SecOC bypass;
- **current Lochuan patch:** corrected Gate-2 compare neutralization, independently corroborating this repository.

## 2. Vehicle-verification claims are new but weakly bound

The current README adds:

```text
Verified working on a 2024 Toyota RAV4 Prime and a 2026 Toyota Sienna (PRC made).
```

The same README still explicitly warns that Flash-level `PASS` does not by itself prove that EPS RX SecOC has been functionally bypassed.

The two vehicle statements do not have equal evidence. The **Sienna** side is bound to the exact `8965B4512000` source image as described above: current manifest identity plus original-sector SHA-256 match our canonical Lochuan donor. The exact model-year label (`2026 PRC made`) and the newer bench-run transcript remain author/operator provenance rather than a retained public CAN/run artifact. The **2024 RAV4 Prime** claim remains only an external-source field claim because no matching F181, CodeFlash image, retained run transcript, or MAC28-only causal experiment is shipped for it.

The RAV4 Prime model/year overlaps the yc field report already captured in SECOC-049. The available public artifacts do not establish whether Lochuan's statement refers to the same vehicle/experiment or an independent one. Neither vehicle statement replaces the controlled MAC28 experiment needed to prove higher-level RX SecOC behavior.

## 3. FACI correction exposed a real local implementation gap

This is the materially new item we were missing.

Our `exploit/patcher/flash_backend.c` descended from the same older blurbdust-style primitive and previously used:

```text
ready:             FFA10080 bit 15
program pacing:    FFA10080 bit 21 (0x00200000)
completion error:  FFA10010 bit 4 only
```

Upstream commit `390ddb7...` corrects the manufacturer register identities and behavior to:

```text
FASTAT      = 0xFFA10010
FAREASELC   = 0xFFA10020
FSADDR      = 0xFFA10030
FSTATR      = 0xFFA10080
FENTRYR     = 0xFFA10084
FPROTR      = 0xFFA10088
FPSADDR     = 0xFFA100E0
FHVE15      = 0xFFF8A430
FHVE3       = 0xFFF82410

FSTATR ready              = 0x00008000
FSTATR program pace       = 0x00000800
FSTATR error mask         = 0x00007040
FASTAT command lock       = 0x10
Forced Stop command       = 0xB3
Status Clear command      = 0x50
```

Upstream says the old bit-21 poll was reserved/always zero and therefore did not provide the intended write pacing. It attributes the corrected values to a register-by-register Ghidra comparison against Toyota Calibration Update Wizard `8965F3... *_erase.pt.bin` manufacturer shellcode.

### Evidence boundary

The referenced manufacturer `*_erase.pt.bin` is not present in our retained local Techstream/CUW corpus. We therefore do **not** promote the exact CUW parity claim to local verified status.

The Sienna firmware does independently show that our old abstraction was incomplete:

- `FUN_00077B6A` reads `0xFFA10080` and uses bit 15 as ready;
- `FUN_00077BA0` observes low FSTATR status and emits Status Clear `0x50`;
- `FUN_00077C56` emits Forced Stop `0xB3` and waits for ready;
- `FUN_00077D9A` checks FSTATR bit `0x400` while feeding program data;
- `FUN_00077F96` checks FSTATR mask `0x24068`.

Those stock routines do not independently prove the exact external `0x7040` CUW mask or bit-11 interpretation, but they do prove that the previous local command-lock-only result model omitted meaningful FSTATR state.

### Local correction made during this refresh

`exploit/patcher/flash_backend.c` was updated to:

1. use the corrected FACI register identities;
2. replace the bit-21 loop with a bounded bit-11 pacing wait;
3. check FSTATR `0x7040` plus FASTAT command-lock;
4. issue Forced Stop/Status Clear recovery as required;
5. keep P/E exit checked even when entry only partially succeeds;
6. retain watchdog service and phase-coded fail-closed errors.

`tests/verify_secoc_manifest_patcher.py` now rejects the old bit-21 poll and pins the corrected source-level invariants. CORR-086 records the correction.

The corrected source was also compiled with the pinned Docker V850 toolchain rather than checked only as C text. The raw `.text` is exactly `0xF70` (3952) bytes, which is exactly the fixed runtime-config offset; the 96-byte config then produces a `0xFD0` (4048)-byte plaintext template. There is **no code-size headroom** before the config slot, so every future backend change must rerun the real V850 build instead of relying on source-level tests alone. The verified build hashes for this refresh were:

```text
raw .text SHA-256: c09b6419f4209da72e6b2b23265696b6714039b7a2576d689454f165d33b9d71
template SHA-256:  cc75e6aaa85157fdd2e08828916844c6144e756233947cf754da40ee0cd19767
```

## 4. CUW parity claim: source package identified, bytes still missing

The rewritten upstream README says its FACI writer is byte-identical to Toyota CUW erase/program shellcode from `8965F3...` update packages, except for stricter cleanup in the public patcher. We can now identify a concrete public source package and extraction path for that payload family, although Lochuan does not explicitly bind his private copy to one exact CUW filename.

The pinned optskug timeline records Willem Melching's July 2025 Tundra EPS work: Toyota bulletin **T-SB-0069-22** exposes calibration package **`T-0035-22.cuw`**, and he specifically called the flash driver uploaded before programming the most interesting artifact. The official bulletin retained by NHTSA (`MC-10220230-9999.pdf`, SHA-256 `618be3738b7c985a6c04df3b7d9fb4414659a0994ccb19c99054d9bc656ad370`) contains page-3 link annotations for:

```text
/t3Portal/calibration/8965F3401200
/t3Portal/calibration/8965F3402200
/t3Portal/calibration/8965F3403200
/t3Portal/calibration/8965F3404200
```

The first pair is the dual-CPU `8965F3401200/8965F3402200` family already named by the community patch tooling. As of this refresh, the first two exact endpoints remain live under `https://techinfo.toyota.com` but redirect an anonymous request to Toyota TechInfo login rather than returning calibration bytes.

The retained community tool `community/blurbdust_secoc_flash_patcher/decrypt.T-0035-22.py` closes the format chain. It parses the CUW's per-CPU S-record streams, derives the section key from the CUW `SeedKey`/DID-`0x0201` data, decrypts each region, distinguishes `CPUImageN` from `EraseRoutineN`, and writes plaintext files named `{NewCID}_body.pt.bin` and `{NewCID}_erase.pt.bin`. In April 2026, the pinned community timeline also records blurbdust describing exactly such a script for extracting the flash driver from a Techinfo `.cuw` package and computing `0x201`/`0x202` for decryption.

A concrete, independently documented community acquisition chain is therefore:

```text
Toyota T-SB-0069-22
  -> TechInfo calibration link for 8965F3401200/2200
  -> T-0035-22.cuw
  -> CUW decryption/extraction
  -> 8965F3..._erase.pt.bin
```

The retained `decrypt.T-0035-22.py` implements that extraction shape. Lochuan then independently states that he disassembled an `8965F3... *_erase.pt.bin` and compared it with his writer. It is highly plausible that these refer to the same Tundra CUW lineage, but the surviving evidence does **not** prove that Lochuan's exact input file was `T-0035-22.cuw` or that he used this exact script.

What remains unknown is **how Lochuan personally obtained his copy**: his repository says only that he extracted the payload from `8965F3...` update packages. It does not say whether he downloaded a package directly with TIS access or received a CUW/plaintext payload from Willem, blurbdust, or another participant.

A bounded search of local files and Git object histories, GitHub code/forks/releases, the I-CAN-hack Tundra branch, Internet Archive exact/prefix captures, archive.org item search, Common Crawl 2024/2025/2026 indexes, and exact web queries found no public mirror of `T-0035-22.cuw` or an `8965F3... *_erase.pt.bin`. Thus exact CUW byte parity still cannot be reproduced locally today. The best concrete acquisition target is **`T-0035-22.cuw`** (or a plaintext erase payload derived from it): hash-pin it, run/verify the retained decryptor, and independently disassemble the result.

## 5. Repository changes made from this refresh

- advanced `external-references.lock.json` from `e7c1f17...` to `9eed2b4...`;
- added hashes for refreshed `README.md`, `eps_patch/manifest.py`, and `payload/faci_dual.h`;
- updated `tests/verify_external_corroboration.py` to distinguish the historical wrong target from the current corrected target and pin the FACI refresh/vehicle claims;
- corrected `exploit/patcher/flash_backend.c` and strengthened its deterministic regression checks;
- updated the SecOC canonical report, findings ledger, corrections ledger, patcher README, and community provenance page.

## 6. Verification

Completed during the refresh:

```text
upstream: PYTHONPATH=. uv run --python 3.12 --extra test pytest -q
          504 passed

local:    uv run --locked python exploit/patcher/build_shellcode_template.py \
            --docker build/patcher-template-lochuan-refresh.bin
          raw .text = 0xF70 bytes; template = 0xFD0 bytes

local:    make verify-one SUITE=secoc_manifest_patcher
          2 suites passed

local:    make verify-one SUITE=exploit_surface
          1 suite passed

local:    make verify-external
          376 checks passed, 0 failed

local:    make verify-changed
          115 suites passed, 0 failed

local:    make verify
          181 core suites passed, 0 failed
```

A direct live Ghidra-bridge xref attempt was also made first for the FACI registers, per repository policy, but the local bridge could not start because the runtime reported `Language not found for 'v850e3:LE:32:default'`. The existing read-only pseudocode corpus and raw firmware references were then used for the bounded local cross-check above. No committed Ghidra project was modified.

## Bottom line

The refresh does **not** reveal a better SecOC bypass than the one already recovered here. Instead, it supplies strong independent convergence: Lochuan corrected his target to our exact Gate-2 patch and CRC fixup.

The genuinely new actionable finding is lower-level: his CUW-correlated FACI correction exposed a flaw in our persistent flash backend's program pacing and status checking. That local defect is now corrected and regression-tested. The PRC-Sienna bench target is now explicitly bound to the canonical `8965B4512000` donor image; only its newer execution transcript/model-year wording remains external provenance. The RAV4 Prime statement remains an artifact-unbound portability lead. The CUW source package is also no longer generic: the acquisition target is Toyota Tundra `T-0035-22.cuw` from TSB `T-SB-0069-22`, although the actual package bytes have not been found in a public mirror.
