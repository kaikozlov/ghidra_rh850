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
| `dc2abd7199f49b50b5f120c8d8852337f7e8ba5d` | 2026-08-18 | `docs: note verified vehicles (RAV4 Prime 2024, Sienna 2026 PRC)` | New external field claims; artifact binding remains absent |
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

The refreshed README additionally says the corrected patch point, sector digests, and adjustment word were captured from an actual bench vehicle and validated through a complete `probe → patch → verify` run. That is stronger than the prior public history, which only retained a successful write/readback of the **wrong** target followed by a failed CRC-sector step. However, the refreshed repository does not retain the corresponding run directory, F181/CodeFlash identity, raw protocol transcript, or CAN evidence for this newer claimed successful run. It is therefore useful external deployment evidence, not a locally reproducible or independently auditable hardware record.

The correct temporal interpretation is therefore:

- **historical Lochuan patch:** `0x664E6 31->10`, disproved as a SecOC bypass;
- **current Lochuan patch:** corrected Gate-2 compare neutralization, independently corroborating this repository.

## 2. Vehicle-verification claims are new but weakly bound

The current README adds:

```text
Verified working on a 2024 Toyota RAV4 Prime and a 2026 Toyota Sienna (PRC made).
```

The same README still explicitly warns that Flash-level `PASS` does not by itself prove that EPS RX SecOC has been functionally bypassed.

No exact F181 value, CodeFlash image, retained run transcript, or MAC28-only causal experiment tied to those two named vehicles is present in the refreshed repository. The generic README statement about a successful bench `probe → patch → verify` run is likewise not artifact-bound to either named vehicle in the public tree. The vehicle claims are therefore recorded as **external-source/bounded field claims**, not as firmware-static portability proof.

The 2024 RAV4 Prime model/year overlaps the yc field report already captured in SECOC-049. The available public artifacts do not establish whether Lochuan's statement refers to the same vehicle/experiment or an independent one. The 2026 PRC-made Sienna statement is a new model/year/region claim, but remains similarly unbound.

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

## 4. CUW parity claim: useful lead, not locally reproduced

The rewritten upstream README says its FACI writer is byte-identical to Toyota CUW erase/program shellcode from `8965F3...` update packages, except for stricter cleanup in the public patcher.

This is potentially valuable because our local Techstream V18 work has recovered the host-side CUW route, security, container, timing, and writer state machines, but we still do not possess a matching manufacturer calibration package containing the cited target-resident `*_erase.pt.bin` payload. The upstream claim therefore identifies a concrete artifact worth obtaining later:

```text
8965F3... Toyota CUW package containing *_erase.pt.bin
```

If obtained, it should be hash-pinned and independently disassembled before promoting register/bit-name equivalence beyond external-source status.

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

The genuinely new actionable finding is lower-level: his CUW-correlated FACI correction exposed a flaw in our persistent flash backend's program pacing and status checking. That local defect is now corrected and regression-tested. The new RAV4 Prime and PRC-Sienna statements are worth retaining as portability leads, but they remain artifact-unbound external claims.
