# Minimal persistent write+exec patch — Camry F33 `8965F3307000`

> **Scope:** exact Camry EPS `8965F3307000` application CodeFlash, with a
> transfer audit of the other three registered EPS images
>
> **Question:** what is the smallest persistent CodeFlash change that gives a
> universal, payload-agnostic write-and-execute primitive in RAM while the
> stock application keeps running — no `10 02` programming transition, no
> reset, repeatable every ignition cycle?
>
> **Status:** design verified firmware-static and simulator-proven; not yet
> exercised on hardware.
>
> **Verification:** `tests/targets/camry/verify_camry_f33_minimal_write_exec_patch.py`
> (selector `camry_8965f3307000_minimal_write_exec_patch`); stub executed in
> the pinned simulator with window placement and postcondition asserts.
>
> **Related:** [keyless-exec-surface-assessment](keyless-exec-surface-assessment.md)
> (no-patch alternative), [live baseline §13](../variants/camry-2026-live-baseline.md#13-non-persistent-application-mode-signer-installation)
> (placement/control-transfer split), [boot validity](../architecture/boot-validity-and-flash-lifecycle.md),
> [TSS3 runtime](../architecture/toyota-tss3-minimal-runtime.md)

## Result

Two patch sites spanning 29 bytes, plus the 4-byte region-1 CRC fixup the
boot validity gate requires (31 bytes differ from stock; two stub bytes
coincide with the original handler's). Everything else — boot, application,
UDS, SecOC — is stock bytes.

| # | Site | Stock | Patched | Purpose |
|---|---|---|---|---|
| 1 | `0x30D68` | `5A` | `00` | open the stock XCP command ingress gate |
| 2 | `0x99266..0x99281` | `validate_cursor_crc_request_and_build_reply_99266` entry (168 B) | 28-byte universal exec stub | selector `0xF3` becomes "call payload at `*(u32 *)0xFEBF7C00`" |
| 3 | `0xFFDEC..0xFFDEF` | `EB 76 C3 D8` | `F0 6E 82 D1` | region-1 CRC fixup for the bytes above |

Patches 1–2 re-use two complete stock mechanisms that this calibration carries
but disables or never consumes:

- **Placement already exists.** F33 contains the full XCP command stack —
  standard map at `0x22B24` (count byte `0x22AF1`, callback table `0x22B50`),
  custom calibration family at `0x2B250`. `SET_MTA 0x82C62` accepts an
  arbitrary 32-bit cursor; `DOWNLOAD 0x81FFE` stores 1–6 tester bytes per
  8-byte CTO under an interrupt guard after two range checks
  (LocalRAM `FEBE0000..FEBFFFFF` via cells `0x22AAC`/`0x22AA8`, then the write
  window `FEBF7C00..FEBFFBFF` via `PTR_DAT_0002b21c/0x2b220` in
  `reject_memory_span_outside_configured_window_98f2c`). `GET_SEED`/`UNLOCK`
  are unconfigured, so the write path has no authentication. The only thing
  that keeps it dead is one config byte: `dispatch_eight_byte_command_reply_98e80`
  reads `DAT_00030d68` at `0x98E88` and, when nonzero, returns "handled"
  before any opcode lookup — so `wrapper_predispatch_session_command_hook_830c0`
  (called by the standard dispatcher `0x821D6` before CONNECT processing)
  suppresses everything. `0x30D68` has exactly one reader in the 7,336-function
  corpus and no writer. Setting it to zero restores the stock Sienna-family
  behavior: custom selectors dispatch through `0x98E80`'s 7-entry table,
  everything else falls through to the standard XCP dispatcher.
- **Execution has no stock consumer** (the live-baseline §13 boundary). The
  patch supplies the missing consumer by replacing one dead-in-practice
  callback: `0xF3` `BUILD_CHECKSUM` is EOL calibration tooling, its table row
  (`0x2B268`, callback field `0x2B26C`) is its only reference, and its
  168-byte body (`0x99266..0x9930D`, next selector `EB` at `0x9930E`) is
  entirely free for the stub.

The window the primitive writes and executes is supervisor-executable.
MPU region bounds words at `0x31690/0x31694` are exactly
`FEBF7C00..FEBFFBFC` — one region covering the whole window — with the
`0xB8`/`0xA8` attribute words behind it matching the family's
context-0-RWX/context-1-RX mapping. The load-bearing evidence is stronger
than that transferred attribute indexing: the retained tail `FEBFF9F0..`
inside this single region has live on-hardware execution evidence, and the
stock write validators admit the same range. The frame path itself was
live-proven reachable: the `0x1FDC0002` extended-CAN route reaches the XCP
staging cell (live-baseline §13.1 marker probe).

## The stub

```asm
/* 0x99266 — entered via `jarl r29,lp` at 0x98EC2; r6 = frame ptr, r7 = len */
1fa0        mov    lp, r20             /* keep dispatcher return address   */
40ae bffe   movhi  0xFEBF, r0, r21     /* r21 = 0xFEBF0000                 */
35b7 017c   ld.w   0x7C00[r21], r22    /* r22 = *(0xFEBF7C00) entry mailbox*/
96bf 0100   ld.bu  0[r22], r23         /* dummy read: publish the writes   */
1f00        syncp
1c00        synci
f6c7 60f9   jarl   [r22], lp           /* call payload; lp resumes below   */
2056 5a00   movea 0x5A, r0, r10        /* deterministic completion value   */
7400        jmp    [r20]               /* return into dispatcher 0x98EC6   */
```

Properties:

- **Payload-agnostic.** The stub knows nothing about the payload; the sender
  chooses the entry address by writing the mailbox word at the window base
  (`0xFEBF7C00`, also a natural payload load address). Any executable address
  works, not only the window.
- **Self-contained publication.** The G3M ordering (stores → dummy read →
  `SYNCP` → `SYNCI` → branch) is in the stub, so the sender's `DOWNLOAD`s are
  automatically instruction-coherent before the call.
- **Deterministic completion.** The custom dispatcher compares the callback
  return register `r10` against `0x5A` (`addi -0x5a,r10,r0` at `0x98ED0`) and
  on equality transmits the fixed 8-byte reply from `FEBE5EBC` on
  `0x1FE00002`. The stub forces `r10 = 0x5A` after the payload returns, so a
  reply means "payload returned"; silence (timeout) means it did not.
- **Register discipline.** `r20`–`r25` are caller-saved; the dispatcher's live
  registers `r26`–`r29` are protected by its `prepare` and untouched. The
  payload is entered as an ordinary subroutine with `lp` set, so
  payload-side `jmp [lp]` returns through the stub.

Simulator proof: harness + payload linked into the window + these exact 28
bytes run under `tools/rh850 test payload` (region `0xFEBF0000,0x10000`,
payload at `0xFEBF7000`, marker at `0xFEBF6000`, stop at the caller's
`done_marker`, asserts on marker and `r10`) — payload executes from the XCP
window, `r10 == 0x5A`, and control resumes at the caller. PASS.

## Sender protocol (8-byte frames on `0x1FDC0002` → `0x1FE00002`)

```text
FF 00 00 00 00 00 00 00        CONNECT   (sets FEBE5005=1, channel FEBE5004)
F6 00 00 00 <addr32 LE>        SET_MTA   (payload destination, any window addr)
F0 <n> <n bytes>               DOWNLOAD  (repeat, ≤6 bytes/frame; MTA advances)
F6 00 00 00 00 7C BF FE        SET_MTA   → 0xFEBF7C00
F0 04 <entry32 LE>             DOWNLOAD  mailbox = payload entry, written last
F3 00 00 00 00 00 00 00        TRIGGER   → payload runs; reply = ACK, timeout = no return
```

Custom selectors require the prior CONNECT on the same channel
(`session_id_not_active_83570`). ~5.5 k frames move the full 32 KiB window.

Payload-author notes: follow the existing resident-payload rules — 48-byte
speculative-fetch guard, timer-bounded work in the communication-task context,
preserve `r26`–`r29`. Hand-written assembly must avoid `movea`/`ld.w`
displacements ≥ `0x8000` from a `0xFEBF0000` base (sign-extended imm16; the
stub's `0x7C00` displacement is deliberately sign-safe).

## Boot validity and brick boundary

`boot_select_application_or_resident 0x13B0` runs
`boot_validate_application_images 0x119E`: per-region CRC (descriptors at
`0x8DD0`/`0x8DE0`, embedded address/length at `0xFFDD0`/`0xFFDE0`) plus the
`0x5AA5A55A` markers at `0x17E00`/`0xFFE00`. CRC32 with residue `0xFFFFFFFF`
covers `0x10000..0x17DEF` and `0x18000..0xFFDEF` inclusive of the terminal
fixup words (`0x17DEC`, `0xFFDEC`). There is **no boot-time CMAC** — the
region CMAC machinery (`boot_region_authentication_submit`, trailer fields in
the region table at `0x8E00`) belongs to the programming-time download
validation, and region 1's trailer slot `0xFFDF0..0xFFDFF` is `0x400040`
filler in the stock image.

Both patch sites sit inside region 1, so the patched image needs only the
region-1 fixup: `zlib.crc32(patched[0x18000:0xFFDF0]) == 0xFFFFFFFF` with the
solver word at `0xFFDEC` (the same solver reproduces the stock fixup
`EB 76 C3 D8` from the stock prefix, and the stage7 restore used the same
CRC convention on hardware). Region 0 and both markers are untouched. The
verifier asserts residues `FFFFFFFF`/`FFFFFFFF`, marker words, and the exact
31-byte change set.

Failure containment: the boot region `< 0x10000` is untouched, so the
bootloader itself cannot be damaged by this patch. If the CRC fixup were
wrong, the gate fails into `boot_resident_main` — the DCM-armed programming
runtime (default session, boot-SA-gated reflash) that the F33 recovery
already exercised on hardware. That is a recoverable state, not a brick.

## Install and rollback (one-time)

Flash the patched image once by the proven raw-write route — boot
SecurityAccess + authenticated RAM execution + FCL block writes (the stage
5/6/7 pattern from the F33 recovery), rewriting the three affected 0x8000
blocks (`0x30000`, `0x98000`, `0xF8000`) from the current image. The stock
UDS 0x34/0x36 path would instead require rebuilding region CMAC trailers with
the `0xBFD8`-derived key; unnecessary when raw writes are available.
Rollback is the exact inverse: restore 29 bytes, re-fix the CRC.

## Collateral and risk

- **The whole stock XCP surface re-opens**, unauthenticated, for anyone who
  can send on `0x1FDC0002`: LocalRAM reads (`F4`/`F5`/DAQ minus the compiled
  exclusions) and writes to the 32 KiB window. The window includes the
  retained resident state tail `FEBFF9F0..` used by the maintained signer —
  a second writer on that route can clobber it. On a Panda-gated bus this is
  the same trust boundary as the rest of the diag surface; on a shared bus it
  is a real regression versus stock.
- **No execution without the trigger.** Writes alone still have no consumer;
  only selector `0xF3` (the stub) transfers control.
- **`BUILD_CHECKSUM` (`0xF3`) is gone** — EOL/calibration tooling only.
- **Detectable and revertible.** Image CRCs differ from stock; any dealer
  reflash overwrites the patch (and the payload window below `FEBFF9EF` is
  re-copied from CodeFlash `0x10000..0x17DEF` at every startup, so payloads
  are per-ignition-cycle by design; only the `FEBFF9F0..` tail survives soft
  resets).
- **Open boundaries.** No hardware exercise of the patched image yet; the
  dispatch context is the communication task (payloads must be timer-bounded
  like the existing residents); the ACK reply content is whatever the custom
  family last built into `FEBE5EBC` (`FF`-success-shaped), not a stub-chosen
  value.

## Why this shape

The alternatives are strictly worse on byte count or universality: repointing
the table field instead of overwriting in place splits the patch across two
blocks; a UDS-side hook cannot work because application UDS has no
pre-authenticated arbitrary-write (no SID `0x3D`; `0x2E` is DID-table-bound —
live-baseline §13.4); and re-hosting placement in the stub would duplicate a
transport the image already ships.

## Cross-target transfer

The XCP command family is present in Sienna, both Corollas and Camry, with
the same stock-closed one-byte gate, including Sienna's 2021 image. Crown
omits the module; the four Tundra application images have matching absence
signatures. The two Corollas accept the same 28 stub bytes and mailbox
protocol as Camry, with target-local patch addresses and CRC fixups.

| fact | Sienna `8965B4512000` | Corolla H `8965H1202000` / F `8965F1208000` | Camry `8965F3307000` | Crown `8965F3012000` |
|---|---|---|---|---|
| XCP command family | present, gated | present, gated | present, gated | **absent** |
| ingress gate byte | `0x30EF4` = `5A` | `0x2CAA0` = `5A` (both) | `0x30D68` = `5A` | n/a |
| gate reader | `0x97168` (sole) | `0x92198` (sole, both) | `0x98E88` (sole) | n/a |
| custom table | `0x2B3F0` | `0x2AE38` (both) | `0x2B250` | none |
| `0xF3` handler (stub site, 168 B) | `0x97546..0x975ED` | `0x92576..0x9261D` (both) | `0x99266..0x9930D` | none |
| standard map / SET_MTA / DOWNLOAD | map present; `DOWNLOAD 0x80F12` | `0x22A48` / `0x7BF72` / `0x7B30E` | `0x22B24` / `0x82C62` / `0x81FFE` | none |
| wire route | standard `0x7F7`/`0x7F8` | extended `0x1FDC0002`/`0x1FE00002` (IDE-marked descriptors `0x21EF4/0x21EFC`) | extended `0x1FDC0002`/`0x1FE00002`, live-proven reachable | family-5 transport configured out; no rule, no route record |
| write window cells | `0x2B3BC/0x2B3C0` | `0x2AE04/0x2AE08` (both) | `0x2B21C/0x2B220` | none |
| MPU window bounds | `0x3181C/0x31820` | `0x2D1EC/0x2D1F0` (both) | `0x31690/0x31694` | `0x31338/0x3133C` |
| boot region table / markers | `0x8E00` / `0x17E00`,`0xFFE00` | `0x8DE0` / same markers | `0x8E00` / same markers | `0x8E00` / same markers |
| region-1 fixup (patched) | n/a — glitch dump, not constructed | `AA 61 8D B6` (both) | `F0 6E 82 D1` | n/a |

Sienna facts are read from the tracked glitch-dumped image (normalized after
the fact); its per-byte facts — gate, table, callbacks, window and MPU cells —
match the family exactly, which is what the uniform-gate conclusion rests on.
No patched Sienna image is constructed against that dump. The uniform gate
also corrects the framing of
[the Sienna XCP report](../communications/xcp-command-dispatch.md): its
handler semantics are real compiled-in code, but stock dispatch was already
closed there in 2021, exactly as on F33.

Corolla evidence is the existing target-native H closure
([corolla-2023 §7.19-class](../variants/corolla-2023-us-public-route.md)):
the 41-entry opcode map, `SET_MTA`/`DOWNLOAD`/`MODIFY_BITS` handlers for
`FEBF7C00..FEBFFBFF`, and extended `0x1FDC0002`/`0x1FE00002` descriptors are
pinned there; this audit adds the gate byte (`0x2CAA0`, sole reader
`0x92198`, stock `0x5A`, same suppress-when-nonzero semantics in the
relocated dispatcher `0x92190`, reply buffer `FEBE5DA8`) and the patched-image
construction (31-byte change set, both CRC residues `FFFFFFFF`). H and F
differ only in identity strings; their patches are byte-identical. The
Corolla sender protocol uses the same extended-ID pair and frame sequence; the
five read-exclusion intervals are H/F-specific and affect reads only, not the
write window.

Crown boundary: `FEBF7C00` occurs at exactly three Crown sites — the
zero-trip startup clear (`0x1428`), the MPU bounds pair (`0x31338`), and the
calibration shadow copy loop (`0x62AD6`). There is no custom selector table,
no write-window pointer cell, no LocalRAM bound pair, and no XCP handler
code; the Crown-vs-Camry comparison already established the transport family
is configured out with no acceptance rule and no route record.

The two committed Tundra application images (`8965F3401200/2200`) and the
two application images extracted from `T-0036-22` (`8965F3403200/4200`)
have no matching seven-selector table or aligned `FEBFFBFF` word.

The matched communication-stack comparison, actual route encoding and
post-reset writer-frame correction are maintained in
[the EPS variant comparison](../variants/toyota-eps-variant-comparison.md#xcp-and-communication-stack-split).
The Sep-10 C7 helper proves stock mailbox reachability, not an OEM C7
protocol consumer.

Consequence for Crown: nothing to re-enable and nowhere to repoint — a Crown
equivalent would be a different design: one self-contained stub hosting its
own ingress (the stock functional-`0x777` software RX ring is the natural
carrier; it is live-proven on the family and Crown's ring/producer are
already resolved) plus the same exec core and CRC procedure, roughly a
hundred bytes rather than twenty-nine. The window, MPU region, retained
tail, boot gate, and fixup machinery all transfer to Crown unchanged, so
that future variant keeps this report's brick boundary and install route.
