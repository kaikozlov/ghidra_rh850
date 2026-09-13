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
every gateway or power-management state. The post-programming callback owner is
now resolved, not left as an opaque indirect call:

- The manager constructs its real 0xC84-byte active job through `10058780` and
  stores it at manager `+24` (`1003C39C`), corresponding to global `1008BFD4`.
- Its loader at `10058E70` loads **TCUWControlCommPhase.dll**, resolves
  `IsSendingSyncPeriodicMsgToECU` into job `+28` at `10059133`, and resolves
  `DisconnectJ2534Connection` into job `+2C` at `1005913C`.
- `CUW!ProcessAfterReprogramming @ 10064D10` tests the former and calls the
  latter only when periodic traffic is active. It does not choose a P5
  gateway-normalization operation.
- The predicate thunk `TCUWControlCommPhase!10001181 -> 1000B850` calls
  `CJ2534IF::IsSendingSyncPeriodicMsg @ 10002CA0`, which tests the host thread
  handle at `+38`. Disconnect thunk `100010CD -> 1000B3D0` calls
  `CJ2534IF::Disconnect @ 10001E70`.
- That final disconnect stops the host periodic thread, invokes ordinary
  `PassThruDisconnect`, `PassThruClose`, and `PassThruUnloadLibrary`, and joins
  remaining host threads. The dynamic API slots were independently resolved
  in `CJ2534IF::LoadDLL` (`10003491/100034CD/10003614`). It contains no newly
  recovered ECU reset or P5 recovery/normalization packet.

The ordinary flash completion contains a P4-specific gateway-default branch;
it must not be projected onto P5 abort handling. Disconnecting the tester and
proving that a gateway has returned to its normal state are distinct results.

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
placeholder, not a unique match to `8965F3307000`. **It is not even exclusive
to the bootloader:** exact application producer `4FA26` emits the same
`02 || 32*21` response when its compatibility-status getter `62E18` is nonzero.
The complete application producer, its status getter, and the boot RDBI table
are unchanged in the retained incident reconstruction. Normal compatibility
bytes match in that reconstruction, so this is a required interpretation
qualification, not evidence that the current application actually takes its
fallback branch.

An independent, ordinary read-only distinction is available if the target
answers: the application implements **F186** through `4FA7C -> 91AF4 -> 924FC`,
which copies its current-session byte from `FEBE595C`. The exact boot handler
`5FB8` checks four 12-byte descriptors at `8F14`; only F181 is readable. In a
supported boot session a well-formed F186 read therefore gets the explicit
unknown-DID negative response, not the application's positive session value.
A placeholder plus that explicit negative is boot-compatible under these exact
tables; a positive F186 identifies the application service implementation.
A timeout, unrelated negative reply, incomplete FirstFrame, or response from
another source does not decide the issue. Correlation requires one outstanding
request to the same EPS endpoint; negative RDBI responses do not echo the DID.

The portable `camry_f33_recovery_identity` verifier pins the machine-level
producer branches, table bound/access bits, negative-response branch, and
current-session store. It does not emulate or observe the live ECU. F181/F186
observations still cannot replace trusted route/target binding or appropriate
image/live-preimage checks, and they do not authorize a write. Nothing in this
admission logic makes an unresponsive CPU start processing requests.

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
against `build/out/cuwplus-unprotected/manifest.json` for all eight native/managed
inputs used here. Recovered SHA-256 identities:

| Input | Recovered SHA-256 |
|---|---|
| `CUW.dll` | `0e9ba6fd54b8301948309b5fb0571c0b99b40276dec3f0d229a44b7890cda603` |
| `CuwBackendService.dll` | `eb0177bf3a4f608b216541e1a4c088d69ef1037f486110ffa958407735c29ca5` |
| `TCUWCanUnifiedCIDGetter.dll` | `2956d2cef7333305e77589bbc38b507efef6c7ba6f43927c65c5d83d1a8c4f4a` |
| `TCUWCanUnifiedPrepareWriter.dll` | `797b15b8ae8049717c1f5ec2692b923dcea9abb52bd2add6415cf295281db1dc` |
| `TCUWCanUnifiedFlashWriter.dll` | `97cdba7f5cc57a555df27893479141632e48a41276e73c54f9c36de3e6e16647` |
| `TCUWUnifiedUtils.dll` | `fed628ec4c9ca0d6905c96c68e3bdfd574f9c64d2fd76b50de6eba4206579672` |
| `TCUWControlCommPhase.dll` | `684a60c95121d29991669c3e48e4efc8410aa4604bcb56d88cbdd702d80aecec` |
| `TCUWJ2534DeviceIF.dll` | `f95dafd49a5fdff6c7a35b21f20529eb739386c299fcb298fa541f3e254908a3` |

Target claims use `firmware/camry-8965F3307000/CodeFlash.bin`, target-native
Ghidra for the defined functions and raw RH850 instructions for the unseeded
`614A` wrapper. No committed Ghidra project was opened or modified. Temporary
PE disassembly and IL outputs live under `build/work/f33-gateway-end-to-end/`.

## 6. Exact Camry gateway identity acquisition is an ordinary read

The retained current Camry install set resolves Central Gateway to category
443 `CentralGW_P5`, request/response `750/758` with addressing extension `5F`.
That is catalog resolution, not a live gateway identity or a verified current
Panda-bus assignment. Its role-82 plugin is the specially named
`GetCID_SID22_GearShiftControl_DT.dll`; the name must not be treated as proof
that identification needs a different protocol.

Its primary path at `100013F0` loads selector **DC** with `GetCommFrmInfo`
at `1000149E/100014A9`, and sends it through `CommFrameSendReceiveExt` at
`10001520`. Current category-443 DC resolves to **22 F1 81**, with response
mask `FF FF FF` and check `62 F1 81`. The response parser checks the DID bytes,
skips the three-byte response header plus count byte, and iterates 16-byte
software-ID fields. `Execute @ 100027D0` then calls two optional related-unit
branches, each guarded by `CheckEcuFunc` metadata before connecting; those
branches are not prerequisites for that first identity read.

Thus an initial gateway-identification observation can use the existing
standard read operation with correct extended addressing, without guessing
another service, starting a programming session, or treating the plugin's
special name as an access requirement. This does not replace the separate
live gateway-family determination used by the CUW preparer. Plugin input
SHA-256: `aaaea5ac9e323b527ae3ae3bd29e2b659900f4eb097dfa806b8c889132600728`.
Reproduce the table side with `tools/gts frame 443 0xDC --json`.

The two retained partial `.live.zst` files were also compared record-for-record
with their completed `d4` files, using event kind, monotonic timestamp, source,
ID, and payload. All 89,484 recovered records of `rlog-1.live.zst` and all
103,207 records of `rlog-6.live.zst` occur in their completed counterparts.
The first partial file reports corrupted events; neither supplies an additional
record or an independent gateway-preparation attempt. The comparison does not
extend capture coverage beyond the spans already reviewed.


## 7. Normal bootloader completion has a network-requested reset, unlike the halted writer

The remaining return-to-application question was checked against both the current
native programmer and the exact F33 receiver, not just an exported “reset” name.
This is an ordinary authorized programming-service path. No service was sent,
no RAM writer was modified, and no target memory was written.

`TCUWCanUnifiedFlashWriter!100012B0..1000138F` constructs the ordinary hard-reset
request, expects its corresponding positive reply, and calls the P5
request/response helper at `10001379`. The successful normal flash path calls
this helper at `10001857`, before stopping periodic messages, waiting for the
configured wake-up interval, and entering its functional default-session phase.
The functional phase's existing evidence and its success-only callsite are in
[the original-installer/exit note](camry-f33-network-lifecycle-observations-2026-09-12.md).
It is not an independently validated preparation-abort path.

The exact F33 boot receiver supplies the other half:

The ordinary service dispatcher `5222` consumes the table at `TP+7B8 = 8E54`;
its SID-11 record at `8E5C` directly names the `60C2` callback. The reset
table, handler, response builder, scheduling/confirmation code, and terminal
sequence are byte-identical in stock and the retained incident reconstruction.

- Reset handler `60C2..6133` copies two request bytes, requires the configured
  programming session and authorization state, validates hard reset, and
  schedules it through `67DA` before constructing the positive reply at `6098`.
  Startup's TP load at `1F8` sets `TP=869C`; the actual session-policy byte at
  `TP+858 = 8EF4` is `02`. This is not borrowed from another ECU's annotations.
- `67DA..67F5` enters `159E` directly when the transport is idle or records a
  pending reset while the response is in progress. The confirmation callback
  `66BE..66F9` calls `159E` at `66E6` only on the successful pending-response
  branch; a failed confirmation clears the pending flag.
- Fresh Ghidra decompilation of `159E`, `1550`, and `1560` shows the reset
  shutdown: interrupts are disabled, the low boot state becomes 3, the clock
  output divider is stopped when enabled, and Port 4 bit 5 is driven low in
  GPIO output mode before a nonreturning wait. The previously recovered
  EXTCLK1O/supervisor relationship explains the intended hardware reset.
  The external supervisor's actual reaction and subsequent boot were **not**
  observed during this offline pass.

The unseeded handler/confirmation slices were independently byte-matched,
instruction by instruction, to `firmware/camry-8965F3307000/CodeFlash.bin`:
114 request-handler bytes, 42 response-builder bytes, 28 scheduling bytes,
and 78 bytes spanning the confirmation context. The decoding source was the
retained low-region disassembly, not a decompilation of a different target.
The defined reset functions were additionally read from the target-native
Ghidra project. Current UnifiedFlashWriter protected input, sidecar, and
recovered body were hash-matched to the existing recovery manifest.

**Positive result:** a surviving, authorized normal bootloader can be asked over
the network to perform its normal reset shutdown after compatible restoration.
There is no architectural requirement to finish an OEM programming transaction
with the custom RAM writer's halt-only terminal state.

**Composition boundary:** this normal reset handler is not executing inside the
archived writer after its DONE/halt. Appending an ECUReset request after that
halt does not make the handler available. Likewise, the reset request cannot
unbrick a CPU that is not processing diagnostics in the first place. A completed
network-only route still needs demonstrated entry to the normal programming
service, a compatible authorized restoration flow that preserves that service,
and actual repaired-application reappearance.

## 8. Post-programming disconnect does not send a hidden final recovery packet

Section 2's callback resolution was independently reproduced through the actual
`GetProcAddress` assignments and the ControlCommPhase export thunks. The final
thread behavior was checked as well: `CJ2534IF::StopSyncPeriodicMsg` sets the
host stop flag and joins the periodic thread. `SendSyncPeriodicMsg`, at
`100043D0..1000450D`, exits its send loop when that flag is set; it does not
append a special P5 inverse or target reset on exit. An in-flight ordinary
periodic batch can finish, so this is not a claim that no byte can still be
transmitted during a stop.

The subsequent `Disconnect` body calls the provider APIs whose names were
resolved from their actual loader strings: `PassThruDisconnect`, `PassThruClose`,
and `PassThruUnloadLibrary`. These are host/interface lifecycle operations.
No gateway-normal-state reply or target-reset acknowledgement is checked here.
Provider-specific internal behavior is outside this bounded host analysis.
Thus the unresolved P5 reverse-state question cannot be filled merely by calling
`ProcessAfterReprogramming` or releasing a Python/VCI handle.

Working disassemblies from this independent check are under
`build/work/f33-network-return-20260912/`; they are disposable outputs, not new
inputs required by portable verification. No additional vehicle observation,
recovery sender, exploit primitive, or completed repair is implied.
