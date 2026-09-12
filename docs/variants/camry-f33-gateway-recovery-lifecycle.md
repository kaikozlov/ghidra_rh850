# F33 network recovery: gateway-to-rollback lifecycle audit

2026-09-12. Offline analysis only. No vehicle connection, diagnostic request,
session change, upload, flash operation, or target reboot was performed.
**A complete working network recovery path is not established.**

This note extends the gateway candidate in
[the exception follow-up](camry-f33-recovery-exception-followup.md) beyond the
preparation routine to the caller, target identification, archived inverse, and
completion state. It does not prescribe a guessed gateway reset or create a new
upload payload.

## 1. A permissive preparation read is not proof of frontend admission

The current `TCUWCanUnifiedPrepareWriter.dll` can continue after its preliminary
F181 read fails. That remains useful for the routing-hidden-listener hypothesis.
The **separate CID-getter phase**, however, has a different error contract:

- `TCUWCanUnifiedCIDGetter!100019D0` calls `ReadSoftwareID` at `10001B78` and
  preserves failures. Its conditional fallback at `10002680` can inspect newly
  returned placeholder CIDs or use `CheckSupportRID` and `ReadRoB`; the latter
  path needs real target responses, not just the absence of F181.
- `TCUWUnifiedUtils!CheckSupportRID` at `100022A0` builds RoutineControl for
  RID `1000`; `ReadRoB` at `100046F0` builds its ordinary `AB` request and
  requires the corresponding `EB` response. The fallback examines returned
  `F021`/`F022` code values. No EPS-specific meaning is assigned to those codes
  here without an OEM label. It is not an independent flash executor.
- At `100020FF`, the getter retrieves **`RequestCANIDAllowingTimeout`** (literal
  at `10005278`). Its error handler can tolerate selected timeout failures for
  that configured request address. The decoded current P5-Unified-family rows
  examined here leave this value empty; that observation does not exclude
  unacquired package/parameter overrides.
- The per-target worker rethrows preserved failures at `10001D52` when its
  optional fallback does not succeed. The outer phase has a distinct
  no-new-CID error at `1000264A` and a rethrow at `1000266D`.

`CuwBackendService!CuwCoreModel.JudgeFlashable` calls the native eligibility
operation and requires a positive resulting CPU/calibration count. Its initial
received-CID-count conversion accepts zero, so the managed wrapper alone is
**not** proof that every zero-CID recovery workflow is rejected. Native recovery
and blank-target configuration must not be inferred from that wrapper.

**Consequence:** the catch-all inside `StartPrepareWrite` does not establish
that ordinary CUW frontend discovery/eligibility will reach it on this silent
EPS. Neither fabricate target identity nor treat a host-side exception as a
successful target response. The exact F33 CUW remains unacquired; that limits
claims about the manufacturer-package frontend, not the existence of our
separately archived inverse below.

## 2. Preparation completion comes after target execution

The complete current Unified preparer, not the earlier truncated assembly
slice, establishes this P5 order:

| Native location | Operation |
|---|---|
| `10001F80..10001FA3` | Normal gateway authorization, routine `1011` start, 1500-ms wait, result check. |
| `10002070..100021D3` | Network-message preparation, diagnostic masking, periodic traffic and target receive filter. |
| `10002211` | Preliminary target identity read whose exception may be ignored. |
| `10002288..1000229E` | Routine `1012` start, 1500-ms wait, result check. |
| `10002363 -> 10002550` | Mandatory EPS programming-session exchange. |
| `100023AA` | Subsequent target authorization phase. |
| `100023AF` | Only then is the preparer's successful-completion flag set. |

The two routine-result helpers require their returned completion value; a
start response or response-pending frame is not their completed result. P4 and
DH gateway branches remain distinct and must be selected from actual topology
and responses, not assumed from model year.

Stopping periodic transmissions and receive filters appears in the preparation
error/cleanup path. Those are **host transport cleanup**, not proof of restoring
every gateway or power-management state. `CUW!ProcessAfterReprogramming` at
`10064D10` dispatches through configured callbacks at object offsets `28/2C`;
the reviewed managed wrapper calls it and logs the return. These indirections
are not a recovered universal P5 reverse-transition packet. The ordinary flash
completion contains a P4-specific gateway-default branch; it must not be
projected onto P5 abort handling.

Thus separately running preparation and then an unrelated loader is not yet a
verified composed lifecycle: gateway mode/authorization, keepalive ownership,
transport handoff and the failure exit must remain accounted for.

## 3. The archived inverse restores the full reconstructed preincident image

The original incident package has a matching inverse; the corrected future
package is not needed to reconstruct it. I read the **archived**
`stage7-restore/restore_config.bin` and compared its hash, payload-file hash and
shellcode-file hash with its original `restore.json`. I then applied its inverse
**only to an in-memory copy** of the complete retained incident reconstruction
with `PatchConfigV1.from_bytes` and `simulate_apply`. No payload was run and no
authentication exchange or secret derivation was performed.

| Check | Result |
|---|---|
| Incident source SHA-256 | `aba6867f244dda42b754d6f455f25a226ee95025dee6a2d98b07b3ac550f2d74` |
| Original archived inverse-config SHA-256 | `b4aed9dc791a83797e5f3238b946a9ffdad13e249ea21a1de5274dc5f563b95d` |
| Reconstructed restored SHA-256 | `818338cc3e3dc23f1cf466c72f497699adc9ff33767e67b81fb65bccfab09010` |
| Complete byte comparison to retained stage 6 | Equal, across all 1,048,576 bytes. |
| Changed bytes | Eight: four at the damaged call and four at its CRC fixup. |
| Final application CRC residue | `FFFFFFFF` |
| Lower boot region | Unchanged. |
| Factory-stock equivalence | **No**: stage 6 retains 488 differing bytes from the original stock image. |

Inputs are the original files under
`build/out/f33-persistent-b6-signer-tail/`: `CodeFlash.stage7-persistent-signer.bin`,
`CodeFlash.stage6-resident.bin`, and `stage7-restore/restore.json` plus its
referenced config, shellcode and payload. These are retained local incident
artifacts, not inputs implicitly available in a clean checkout. The disposable
result is `build/work/f33-gateway-end-to-end/archived-rollback-audit.json`.

This proves the **byte-image inverse**, not current EPS flash contents, live
preimage checking, executable-payload correctness, or successful vehicle repair.
It also distinguishes undoing the bricking change from restoring all factory
firmware or certifying roadworthiness.

## 4. A surviving boot listener can be admitted; it is not created by admission

The existing restore wrapper has a direct-boot branch; it does not require an
application handoff after an independently observed matching boot response.
The initial default-session request was specifically checked as a possible
composition hazard. Exact F33 `614A..6203` queues default session normally;
`6244 -> 51D8 -> 55FC` updates session/security bookkeeping, followed by the
`6204` response. This reviewed path does not itself call the hardware-reset
routine. The default request therefore is **not established as a route-destroying
boot exit** in this image.

The F33 boot F181 value of two exclamation-filled identifiers is a family
placeholder, not a unique match to `8965F3307000`. It cannot replace a trusted
route/target binding and the appropriate image and live-preimage checks.
Nothing in this admission logic makes an unresponsive CPU start processing
requests.

## 5. DONE is not a completed recovery lifecycle

The archived restore shellcode has exactly the same executable bytes as its
retained generic template before the configuration slot. Its terminal helper
ends in the previously decoded nonreturning loop after DONE telemetry, matching
`runtime_halt`. The wrapper likewise records that a post-restore power cycle is
required. Host success does not mean the application resumed, and ignition OFF
alone has not been proven to remove both EPS supplies.

A completed recovery therefore needs four separate observations: a working
prepared-state target service; successful, correct-image restoration with
readback; an actual return/reset into the repaired application; and renewed EPS
identity/normal output with the diagnostic and vehicle-state checks completed.
None of those live observations was produced in this pass. The result is a
more complete **audit of the candidate**, not an end-to-end demonstrated route.

## Sources and reproduction boundary

Current protected inputs, sidecars, and recovered outputs were freshly checked
against `build/out/cuwplus-unprotected/manifest.json` for all six native/managed
inputs used here. Recovered SHA-256 identities:

| Input | Recovered SHA-256 |
|---|---|
| `CUW.dll` | `0e9ba6fd54b8301948309b5fb0571c0b99b40276dec3f0d229a44b7890cda603` |
| `CuwBackendService.dll` | `eb0177bf3a4f608b216541e1a4c088d69ef1037f486110ffa958407735c29ca5` |
| `TCUWCanUnifiedCIDGetter.dll` | `2956d2cef7333305e77589bbc38b507efef6c7ba6f43927c65c5d83d1a8c4f4a` |
| `TCUWCanUnifiedPrepareWriter.dll` | `797b15b8ae8049717c1f5ec2692b923dcea9abb52bd2add6415cf295281db1dc` |
| `TCUWCanUnifiedFlashWriter.dll` | `97cdba7f5cc57a555df27893479141632e48a41276e73c54f9c36de3e6e16647` |
| `TCUWUnifiedUtils.dll` | `fed628ec4c9ca0d6905c96c68e3bdfd574f9c64d2fd76b50de6eba4206579672` |

Target claims use `firmware/camry-8965F3307000/CodeFlash.bin`, target-native
Ghidra for the defined functions and raw RH850 instructions for the unseeded
`614A` wrapper. No committed Ghidra project was opened or modified. Temporary
PE disassembly and IL outputs live under `build/work/f33-gateway-end-to-end/`.
