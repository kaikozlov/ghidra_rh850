# Community persistent SecOC patch target analysis

> **Scope:** community persistent CodeFlash patch signatures across analyzed EPS applications
>
> **Status:** active; Tundra `8965F3401200/2200` semantics resolved from the Toyota CUW applications
>
> **Verification:** `tests/tooling/verify_community_patch_target_analyzer.py` and
> `tests/tooling/verify_community_tooling.py`

The community persistent patcher searches CodeFlash for one exact 8-byte marker:

```text
88 00 01 52 00 0A E5 0D
```

and overwrites the first four bytes with:

```text
01 52 7F 00
```

which is the RH850 immediate-success return used by the patcher:

```text
mov 1, r10
jmp [lp]
```

This blurbdust/yc egg-based patch is also distinct from the separately published
Lochuan/3b1b `8965B4512000-FW-PATCH` repository. Its historical patch changed
`0x664E6: 0x31→0x10`. Firmware analysis now identifies that byte as an ordinary
checkpoint/NvM failure-status fail-open. The
full yc-versus-Lochuan comparison, including why the older Lochuan analysis
selected that byte and why it can be flaky, is canonical in
[the SecOC application chain §9.7](../security/secoc/application-chain.md#97-yc-compare-neutralization-versus-lochuan3b1b-0x664e6-patch).

The crucial research rule is that the egg identifies a **location candidate**.
`8965B4512000` already proves why: the marker occurs
exactly once at `0x3485A`; the containing function is the shared 5-byte token
comparator for the proprietary SID `0xBA` operation table. Its two direct call
references are `FUN_00034882` and the historically named
`application_proprietary_ab_f1_start` (now semantically BA F1/`JTEKM`); it has
no direct ICU-S reference. Forcing its return true removes BA token comparisons,
but F7 still independently requires application SA level 2 at `0x34D96`. The
actual SecOC receive-verify worker is at `0x8E4BA`.

## 1. Raw-byte triage

`tools/security/analyze_secoc_patch_target.py` is the first pass for any future image:

```bash
uv run --locked python tools/security/analyze_secoc_patch_target.py \
  /path/to/CodeFlash.bin \
  --output patch-target.json
```

It reports:

- image SHA-256 and size;
- every raw egg occurrence;
- file offset and virtual address;
- bounded context bytes;
- exact replacement bytes and known replacement semantics;
- an explicit warning that no semantic ownership follows from an egg match.

It intentionally does **not** infer callers from raw halfwords. A preliminary
implementation attempted that and produced 11 apparent Sienna JARL candidates,
while Ghidra's instruction-aware reference manager proves only two actual call
references. Code/data ownership and instruction boundaries therefore remain a
Ghidra responsibility.

The committed reference output for the analyzed Sienna is:

`data/generated/community_patch_target_4512000.json`

## 2. Instruction-aware semantic triage

After importing a future F3/F4 CodeFlash image into Ghidra, run:

```text
AnalyzeCommunityPatchTarget.java <egg-virtual-address>
```

Tracked script:

`ghidra/scripts/investigate/AnalyzeCommunityPatchTarget.java`

The script is read-only and reports:

1. containing function and whether the egg is its entry point;
2. instruction-aware incoming references/callers;
3. direct callees;
4. direct references from the containing function into the known
   `0xFFC5D000..0xFFC5D0FF` ICU-S register window;
5. decompiled C for semantic classification;
6. a fail-closed reminder that an egg match alone is not a SecOC identity.

Against `8965B4512000`, it deterministically reports:

```text
PATCH_TARGET 0003485a
CONTAINING_FUNCTION FUN_0003485a entry=0003485a size=40
TARGET_IS_ENTRY true
CALLER application_proprietary_ab_f1_start site=00034b80
CALLER FUN_00034882 site=00034898
CALLER_COUNT 2
CALLEE_COUNT 0
DIRECT_ICUS_REF_COUNT 0
```

and decompiles the known byte-comparison loop that returns 1 only when all
requested bytes match. The emitted caller name reflects the accepted project's
historical symbol; service ownership is established separately from the corrected
Dcm object and BA descriptor table.

## 3. Classification procedure for an F3/F4 image

Do not classify the patch target from its machine-code prologue. Use this order:

1. **Raw uniqueness:** how many egg matches exist?
2. **Function ownership:** is the match at a function entry, inside a function,
   or data accidentally decoded as code?
3. **Callers:** which subsystem invokes the target?
4. **Return-value consumers:** what branch/state changes when the target returns
   0 versus 1?
5. **Direct/nearby ICU-S flow:** does the function, its immediate callers, or
   adjacent worker graph touch command-7 result state or `0xFFC5Dxxx`?
6. **SecOC acceptance graph:** does forcing the return value actually dominate
   protected-PDU delivery?
7. **Other callers:** is the function generic and shared with unrelated
   diagnostics/string/state comparisons?

Only after these checks should the target be described as one of:

- cryptographic MAC verifier;
- MAC-result predicate;
- freshness/format aggregate predicate;
- downstream SecOC acceptance predicate;
- generic helper used by SecOC and unrelated paths;
- unrelated false positive.

## 4. Tundra F340: the two community signatures select different functions

Toyota `T-0035-22.cuw` supplies CMAC-valid application images for both Tundra
processors. They close the F340 target question directly.

The blurbdust immediate-success egg `88 00 01 52 00 0A E5 0D` occurs once in
each image:

| CPU | Egg address | Containing function | Direct callers | Semantics |
|---|---:|---:|---:|---|
| `8965F3401200` | `0x30C22` | `0x30C22` | 11 | generic byte-array equality comparator |
| `8965F3402200` | `0x2F8E2` | `0x2F8E2` | 11 | generic byte-array equality comparator |

Both functions are the same 40-byte loop: compare `param3 & 0xFF` bytes and
return 1 only when every byte matches. Replacing their entry with unconditional
success therefore changes a shared comparison primitive; it is not the Tundra
SecOC acceptance predicate.

The later RAV4 Prime field patch uses a different signature and operation:

```text
E0 D1 9A 0D 1A 38 BF FF  ->  E0 01 9A 0D 1A 38 BF FF
cmp r0,r26                    cmp r0,r0
```

That exact eight-byte context also occurs once in each Tundra application:

| CPU | Compare | Worker | Result-zero path |
|---|---:|---:|---|
| `8965F3401200` | `0x88406` | `0x883BA` | status notification then secured-payload delivery |
| `8965F3402200` | `0x809E4` | `0x80998` | status notification then secured-payload delivery |

Both workers are 134 bytes and preserve the same control-flow structure as the
named Camry `finish_secoc_receive_verification_8f906`: the result is compared
against zero; zero takes the normal delivery arm and nonzero takes the
retry/failure arm. The compare-neutralization patch is therefore the transferred
Gate-2 operation on both Tundra CPUs.

This distinction matters when reconstructing historical Tundra experiments:
the blurbdust egg patch and the R4P/Camry Gate-2 compare patch are different
patches against different functions.

## 5. Remaining boundary

The Tundra application findings are closed for `8965F3401200/2200`. The exact
`8965F4207000` and `8965F4201000` targets still require their own firmware
images before assigning either signature a semantic role.

A post-patch Tundra dump remains valuable for a different reason: it can identify
which historical patch was actually applied and whether the containing erase
block suffered collateral changes. The stock CPU1 `0x88000..0x8FFFF` block is
especially diagnostic because it contains both Gate 2 and application diagnostic
session code; see the Tundra target report.
