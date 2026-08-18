# Community persistent SecOC patch — pre-acquisition target analysis

> **Scope:** blurbdust/yc persistent CodeFlash patch signature and future
> `8965F3`/`8965F4` CodeFlash images
>
> **Status:** tooling complete; target semantics artifact-blocked until an
> F3/F4 image is acquired
>
> **Verification:** `tests/verify_community_patch_target_analyzer.py` and
> `tests/verify_community_tooling.py`

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
Lochuan/3b1b `8965B4512000-FW-PATCH` repository. That repository is pinned as
`lochuan_b4512000_fw_patch` in
[`external-references.lock.json`](../../external-references.lock.json) at
`e7c1f17d1090470b18f7f3315abd99b64e5e4619` and fixes a different target,
`0x664E6: 0x31→0x10`. Firmware analysis now closes that byte as an ordinary
checkpoint/NvM failure-status fail-open, not a second SecOC Gate-2 encoding. The
full yc-versus-Lochuan comparison, including why the older Lochuan analysis
selected that byte and why it can be flaky, is canonical in
[the SecOC application chain §9.7](../security/secoc/application-chain.md#97-yc-compare-neutralization-versus-lochuan3b1b-0x664e6-patch).

The crucial research rule is that the egg identifies a **location candidate**,
not a semantic function. `8965B4512000` already proves why: the marker occurs
exactly once at `0x3485A`; the containing function is the shared 5-byte token
comparator for the proprietary SID `0xBA` operation table. Its two direct call
references are `FUN_00034882` and the historically named
`application_proprietary_ab_f1_start` (now semantically BA F1/`JTEKM`); it has
no direct ICU-S reference. Forcing its return true removes BA token comparisons,
but F7 still independently requires application SA level 2 at `0x34D96`. The
actual SecOC receive-verify worker is at `0x8E4BA`.

## 1. Raw-byte triage

`tools/analyze_secoc_patch_target.py` is the first pass for any future image:

```bash
uv run --locked python tools/analyze_secoc_patch_target.py \
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

## 4. What is already closed and what remains blocked

Closed now:

- exact signature and replacement semantics;
- robust raw-location triage;
- instruction-aware semantic-report workflow;
- known `4512000` false-positive reference result;
- rule preventing raw-callsite or prologue overinterpretation;
- a separate calibration-independent Level-1 semantic resolver that ignores the
  blurbdust egg entirely and rediscovers the Sienna authenticated-delivery gate
  from machine/CFG/data-flow structure; see
  [secoc-semantic-patch-resolver.md](secoc-semantic-patch-resolver.md).

Still blocked on an F3/F4 CodeFlash artifact:

- containing function for `8965F3401200`, `8965F4207000`, or `8965F4201000`;
- its callers and SecOC/ICU relationship;
- whether the unchanged semantic resolver finds the same acceptance gate on
  those images;
- whether that resolved gate is the same semantic object as the blurbdust egg
  target, or whether the successful live patch forced a broader/different
  predicate true.

A post-patch dump is sufficient if the surrounding image is intact: the
original first four bytes are known from the egg, so the target can be restored
for static analysis without requiring a separate pre-patch dump.
