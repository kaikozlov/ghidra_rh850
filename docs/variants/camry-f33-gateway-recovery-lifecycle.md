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


## 9. The surrounding phase wrapper distinguishes retry policy from restoration

The native caller outside the preparer was also followed, so its failure branch
is not assumed to be the same as successful flash completion. In current
`TCUWControlCommPhase`, the P5-Unified selection at `1000B43C..1000B477` reaches
`1000B720`; its preparation dispatch at `1000B72E` calls the thunk to `10009370`.
That wrapper invokes the dynamically resolved `StartPrepareWrite` at `10009B4E`.
On failure it calls the shared error handler (`10009B8C -> 10003B90`) rather than
claiming success and proceeding directly to the flash phase. Only the successful
branch changes the phase byte to 2 at `10009BD5`.

The separately named `ProcessBeforeIGOffOnAtRetry` callback is not an uncovered
P5 recovery operation in this wrapper. The comparison at `10009ADE..10009B15`
selects it specifically for the Phase-6 contact type; the callback invocation
at `10009BC5` is additionally guarded by that equality after a failure. Its
existence in the shared module cannot be projected onto P5-Unified.

The shipped **P5-Unified** and **P5-Unified10** route settings are
`IGOffRetriableFlag=1` and `PrepareRetryFlag=0`. Those are distinct policies:
absence of a writer retry export is not proof that the OEM host has no
ignition-cycle retry interaction. The shared error handler reads the former
from its literal at `10014A08`, and reads the latter at `10003DFD..10003E15`
before the optional writer retry call at `10003EF8`. This host-policy evidence
does not prove that ignition alone cold-resets the EPS, normalizes every gateway
mode, or creates an EPS boot listener.

Finally, the normal common phase tail (`1000B74A -> 10004BE0`) calls the
J2534 and calibration objects' `ExportData` methods. It preserves host state;
it does not issue a newly recovered P5 abort/reset packet. GUI callbacks and
provider-internal behavior retain their separate scope. Together with sections
2 and 8, these inspected wrapper paths provide no basis for presenting a
prepare-then-unrelated-writer sequence as already complete.


## 10. Native restoration coverage and saved-image verification

This additional pass checks the **restoration half** of the network candidate.
It does not establish the missing live EPS entry, acquire a matching OEM flash
package, or execute any writer. Undoing the incident and returning every byte to
factory state are distinct goals; the archived stage-7 inverse remains an
incident rollback even though it preserves the previous stage-6 modifications.

### All reconstructed changes fall within the normal upper-region erase domain

Fresh exact-F33 decompilation of `3402`, `3474`, `34A8`, `40E0`, `41E0`,
`42F6`, `4332`, `43BE`, and `4428` was checked against the factory binary.
The routine dispatcher has its ordinary erase call at `58B4 -> 41E0`.
`41E0` selects sector boundaries using `40E0 -> 3474`, selects the region's
metadata location through `3402`, and queues the normal erase worker. This
analysis concerns an already executing, authorized programming service; erase
is not a way to contact an unresponsive target.

The fixed upper-region descriptor at `8E1C` has data bounds
`18000..FFDFF`. The native sector boundary table at `86EC` contains 38 sectors;
the final one is `F8000..FFFFF`. Therefore a completed **full upper-region**
erase covers `18000..FFFFF`, including the trailer beyond the ordinary data
range. It is not limited to the bytes included in the application CRC.

Independent comparisons of the complete retained images give:

| Saved image versus factory | Different bytes | Inside CRC inputs | Outside CRC inputs |
|---|---:|---:|---:|
| Stage 6 (the archived inverse's result) | 488 | 12 | 476 |
| Complete incident reconstruction | 492 | 16 | 476 |

Every difference in both comparisons is inside that upper-region erase extent.
The lower boot bytes are unchanged. The incident-to-stage-6 comparison differs
at eight bytes, consistent with the archived inverse already checked in section
3. These are **saved-image** comparisons, not present-ECU flash measurements.

**Positive result:** normal full upper-region restoration has the necessary
address coverage to remove the damaged call, previous application patches, and
resident tail together. A hypothesis that the normal erase necessarily leaves
the tail untouched is not supported by these tables. This does not prove that
an as-yet unacquired F33 package selects the full range, that its driver runs,
or that programming succeeds on this rack. It does not call for erasing the
boot region or vehicle-specific DataFlash to undo these known CodeFlash changes.

### A native erase changes metadata; CRC success alone is not factory equality

The same descriptor selects `FFF00` as the upper-region counter word; the lower
region selects `17F00`. `3402` obtains the descriptor's fifth word. `41E0`
stores it in the flash-operation state. When that address lies in the sector
being erased, `42F6` saves its previous value plus one and fills the rest of the
256-byte staging page with `FF`. `4332` calls the installed normal flash driver
for erase and then for the counter-page rewrite. `43BE` avoids overwriting that
same metadata page through the ordinary data-writing branch. These are native
firmware semantics, not a newly constructed RAM writer.

Thus a successfully reprogrammed image need not have the factory dump's **whole
CodeFlash hash**: the programming counter is expected to change according to the
actual erase history. Conversely, exempting that whole page would hide resident
bytes. Only the separate four-byte words are identified as counter fields here;
their values still need transaction history to interpret.

The 476 differing bytes outside the CRC inputs are not counter changes. In the
factory image, the upper trailer after the validity marker is erased except for
the four-byte counter. A CRC-only comparison cannot establish that resident
trailer content was removed. Counter changes and a CRC pass therefore must not
silently become a general "stock restored" result.

### An offline comparison is not a live dump mechanism

The exact boot SID table's ReadMemoryByAddress record at `8E8C` names `69B0`.
The handler at `69B0..69D1` builds a fixed negative reply rather than a flash
read. Its bytes match both the factory and incident images. Consequently,
ordinary boot-service availability does not also establish availability of a
one-megabyte standard-service readback. A live bytewise audit needs a separately
established read mechanism; do not append a nonexistent dump command to the OEM
flow or replace normal programming-integrity checks with a simulated image hash.

The new read-only saved-image comparator is:

```sh
uv run python tools/targets/camry/analysis/analyze_camry_f33_recovery_image.py SAVED_CODEFLASH.bin
uv run python tests/verify_camry_f33_recovery_image.py
```

It reads files only, trusts geometry solely from the exact hash-checked factory
reference, reports every differing range, and distinguishes counter-word
changes from all other differences. Exit zero requires **exact** equality;
counter-only differences still exit one and remain explicitly visible. It
neither obtains a live dump nor generates/writes a replacement image.
The 11 portable tests cover trailer residue with unchanged CRC inputs, adjacent
counter-page bytes, validity markers, truncated images, an altered reference,
modified candidate descriptors, and conservative CLI exit behavior. All pass;
Ruff checks and formatting pass. The tests do not execute the ECU or native
flash driver.

The raw instruction ranges used for counter selection, erase setup, counter
update/rewrite, normal data writes, the erase callsite and negative readback
handler were independently matched byte-for-byte against both factory and
retained incident images (490 bytes total). The disposable observations are
`build/work/f33-native-restore-coverage/image-comparisons.json` and
`raw-byte-checks.json`; portable tests require neither file nor any other
`build/` artifact.

`tools/gts cuw 8965F3307 --json` still returns no local package match. Toyota's
public reprogramming index directs matched-calibration acquisition to TIS and
applicable service bulletins, but the public search in this pass supplied no
exact F33 package or independent recovery-entry procedure:
https://techinfo.toyota.com/techInfoPortal/appmanager/t3/ti?_nfpb=true&_pageLabel=ti_tdt_reprog
This is an acquisition gap for the OEM-package branch, not proof that no such
package exists or that the archived incident inverse lacks the correct bytes.

**Remaining composition gap:** no prepared-state EPS response was observed;
no compatible native restoration was executed; the repaired application has
not reappeared. A read-only SSH retry returned "Host is down" before any device
command ran. The restoration coverage is more tightly established, but this
is still not a completed network-only recovery route.


## 11. Normal host phases are not an independent network entry

Returning to the previously working pre-incident image is a valid **unbricking**
goal. Factory-exact restoration is optional, not an extra prerequisite. The
archived inverse's 488 remaining factory differences do not themselves
invalidate its incident rollback; its missing live entry and terminal-halt
completion are the separate concerns identified above.

Fresh instruction inspection of the current `TCUWCanUnifiedFlashWriter.dll`
matched the following direct-call opcodes and relative destinations to the
hash-pinned recovered PE. The protected input and its sidecar were also freshly
matched to the recovery manifest before inspection.

| Callsite | Callee | Normal host stage |
|---|---|---|
| `1000158D` | `10002AD0` | Install package-defined fields |
| `10001609` / `10001621` | `10002510` / `10002060` | Transfer and verify phase 0 |
| `10001651` | `10002060` | Phase-1 erase operation |
| `100017D7` / `100017EF` | `10002510` / `10002060` | Transfer and verify phase 2 |
| `10001813` / `1000182B` | `10002510` / `10002060` | Transfer and verify phase 3 |
| `10001857` | `100012B0` | Target reset after the final CPU image |
| `10001893` | `10001000` | Functional completion after periodic-stop/wait |

Numeric phases are the actual caller arguments. Their work is driven by the
package's area records; an empty phase does not imply an unconditional write.
The transfer helper calls the ordinary download/data/transfer-exit helpers at
`10001BE0`, `10002980`, and `10001F70`. The routine helper checks corresponding
positive replies. These functions do not invoke the archived custom writer
which stops in a terminal halt.

On the exact F33 target, the ordinary erase/program worker invokes an installed
RAM flash driver through `FEBF0FD0` (`4332`, `43BE`, `4428`). Thus the presence of
normal programming services does not mean the entire writer is resident in
untouched boot code. Compatible driver/package material and normal authorization
are still required for that branch; the raw factory dump alone is not a complete
OEM programming package. The retained Tundra package's shared protocol and
flash-controller behavior do not prove full F33 package compatibility.

Fresh `5A04` decompilation also confirms that normal verification completion can
resolve the validity-marker destination through `33CC`, call `5286`, and wait for
the marker-write worker result before returning success. `5286` queues the native
validity value using `4188` and `4276`. This fills in the connection between
ordinary verification and the marker discussed in section 10; it does not supply
a pre-application entry into those services.

The ten direct-call checks and the independent saved-image count check passed.
The latter again found 16 incident differences in the application data range,
476 in the footer, and none below `18000`. The existing saved-image comparator's
11 portable tests also passed. These checks are offline observations, not ECU
execution, complete flash-driver emulation, or evidence of successful recovery.
The disposable numeric record is
`build/work/f33-oem-writer-composition/observations.json`; no portable check
requires it. No new transport, writer payload, key material, or vehicle command
was introduced.


## 10. Generic session, flow-control and power-hold helpers are different operations

The remaining cleanup candidates were followed through their actual call targets
and destination construction. This was offline; no diagnostic transaction,
authorization attempt, ECU reset or flash write was made. All five relevant
current protected inputs, sidecars and recovered images matched the existing
CUW recovery manifest before these checks.

**`SetBStoECU` is a provider configuration operation in the reviewed body.**
`TCUWCanDiagCommUtils!10002140..10002176` builds a one-entry configuration list
with parameter `1E` and the supplied byte value, then calls J2534 object vtable
slot `+0C` with operation `2`. The actual `CJ2534IF` vtable at `100071DC` resolves
that slot to `10001D80`; this wrapper calls object member `+1C0`. Its loader
at `10003577..10003581` binds that member from the literal **PassThruIoctl**
at `10007344`. Thus the preparer's cleanup call at `1000245D` does not reveal
an EPS boot request or gateway-normal-state request. Provider-internal traffic
remains a separate implementation boundary; a name containing “ECU” was not
used to infer a transmitted diagnostic service.

**The generic default-session helper is real, but its recovered caller is the
local-bus controller flow.** `TCUWUnifiedUtils!10003230` builds normal `10 01`,
checks `50 01`, and uses its two supplied address objects. The current Unified
CID getter's call at `10002514` is guarded by local-bus flow value `1` and follows
`RoutineControlForChargeLocalBus` at `100024F0`. Its address objects are the
same ones populated by `GetChargeLocalBusPowerOnControllingEcuDiagID` at
`10001F56` and used for that controller's extended session at `1000206A`.
They are not automatically the Camry central-gateway `750/758, extension 5F`
objects. This additional normal-session implementation therefore does not fill
the separate P5 gateway-abort proof gap. It also does not prove that a standard
default-session request would fail on the real gateway; that behavior is still
unmeasured.

**Automatic ignition-off cancellation is a third endpoint and must not be
misread as a reverse-state switch.** The current
`CancelAutomaticIGOFFForP4CanAndP5Can` body starts at `10001630`; its literals
at `100082A4/100082B0` select **750/758 with extension E9**, not `5F`. It reads
its configured power-management data, and the supported write branch sets a
bit using `OR 40` at `1000189E`. The boolean argument changes compatibility/
error-path handling; the reviewed write branch does not use false to clear
that bit. Its legacy fallback is another operation on the same E9 endpoint.
Neither calling a function named “Cancel” nor changing that boolean establishes
an inverse operation for the 5F gateway's programming routines. The ECU-side
persistence and release conditions were not measured and must not be inferred
from host cleanup alone.

These distinctions prevent composing an incorrect recovery lifecycle from
similarly named helpers. They do not require a special inverse packet to exist:
a supported ignition-cycle procedure or ECU-side timeout could be the intended
release mechanism, but its exact gateway behavior needs its own evidence.
The P5 host's ignition-retry policy in section 9 is retained separately from
such a live state-restoration observation.

Primary inputs: current **TCUWCanDiagCommUtils.dll**, **TCUWJ2534DeviceIF.dll**,
**TCUWUnifiedUtils.dll**, **TCUWCanUnifiedCIDGetter.dll**, and
**TCUWCanUnifiedPrepareWriter.dll**. The relevant native bodies and address
literals were read from their recovered PE images; disposable disassemblies
are under `build/work/f33-network-return-20260912/`. No new recovery sender,
authentication bypass or claimed vehicle repair is implied.


## 11. The surviving 7A2 response is a camera-side control, not a second EPS

The existing Camry mount resolution maps plain request **7A2** to category
**5005 / RC_P5.ddb / Rear Camera**. Fresh `tools/gts category RC_P5 --json`
confirms the OEM category, and `tools/gts canbus 12984 --json` places
`Parking Assist Monitor System / Rear Camera` on **Toyota Bus 1**, whereas
`Power Steering (EPS)` is on **Toyota Bus 4**. Those Toyota bus labels are not
Panda bus indices.

The previously captured 7A2 fault **561854** independently agrees with this
mapping: current RC_P5 table 65, record 1, resolves it to **C161854, Optical
Axis Alignment / Missing Calibration**. The prior F181 **867BF0601001**
observation therefore must not be treated as a central-gateway identity or an
alternate EPS programming CPU merely because it is adjacent to 7A1. The join
is an OEM install-set/observed-fault identification, not a newly captured
hardware label or an authenticated sender measurement.

Both current camera category 5005 and gateway category 443 use selector DC,
frame 2B54, for normal F181 reading. Their identical request service does not
make them the same endpoint. The gateway's separate **750/758, extension 5F**
route remains the relevant route for the prepared-network hypothesis. A camera
reply demonstrates communication with that camera path, not that the gateway's
EPS route is in its programming state.

## 12. The incident reconstruction also passes the native regional CRC inputs

The claim that the retained incident passes startup integrity was checked
against **the actual boot descriptors**, not merely a whole-file CRC. Fresh
exact-target decompilation of `3438`, `344C`, `47EA` and `481A`, together with
boot TP **869C** (raw handoff setup `9F50`), resolves the selected descriptor
records at **8DD0** and **8DE0**:

| Profile | CRC input, end exclusive | Descriptor-reference words |
|---|---|---|
| 0 | 10000..17DF0 | FFDD0 / FFDD4 |
| 1 | 18000..FFDF0 | FFDE0 / FFDE4 |

In both the retained factory image and complete incident reconstruction
`aba6867f...50f2d74`, the referenced start/length words match the boot table;
each range's CRC32 is **FFFFFFFF**, and validity markers **17E00 / FFE00**
are both **5AA5A55A**. Thus an unnoticed difference between whole-file CRC and
native regional CRC does not, in the retained reconstruction, put the ECU in
the validity-failure boot path. The resident tail beyond these CRC ranges must
still be included in a complete image comparison. This checks saved bytes;
it neither measures live flash ECC nor converts the reconstruction into a
post-incident ECU readback.


## Native frontend admission and the last-message record: additional closure

The earlier distinction between the optional F181 read **inside preparation**
and admission **before preparation** was followed into current `CUW.dll`, not
left at its managed wrapper. This is a bounded native-code result, not a live
run of GTS and not proof of a complete recovery procedure.

### No received CID is a real native condition, not an automatic blank target

`_JudgeFlashable@16` at `10061B70` reaches the worker at `1005F800` through its
normal or alternate loaded-package paths. In the reviewed worker:

- `1005F927..1005F9B2` reduces the selected node's per-entry bitmap. This pass
  calls it a bitmap, not a proven EPS fault or hardware-blank indicator.
- If that bitmap condition is not satisfied, `1005F9EF..1005FA28` checks a
  package-filename exception containing the literal **`.vbf`** at `10078D50`.
- Outside that exception, `1005FA33..1005FA52` branches to the **`BBE`** return
  at `1005FA6F` when the current received-CID vector has zero entries. Its endpoints are `1008C1D8/1008C1DC`,
  with 24-byte elements. `_GetNumberOfReceivedCID@4` at `1005F000` independently
  uses those same endpoints on its corresponding normal-source branch.
- The separate target-blank-only configuration byte at `1008C460` is populated
  by `_ConfigureCUWDLL@32` (`10064849`) and read later in the matching logic.
  It does not bypass this earlier empty-CID return merely by being set.

There are real bitmap, file-family and alternate-package cases, so this does
**not** establish that every zero-CID call is rejected, nor that every F33
package would select this branch. It establishes why a zero-count managed call,
`BlankECU` wording, or the optional later F181 exception handler cannot stand in
for a successful native admission result. None of the missing input state was
fabricated and no compatibility check was patched or disabled.

The absolute byte at `1008CA1C` must also not be named as an ECU recovery-mode
flag just from its presence in this decision. Its native writer `10045880`
sets it while unpacking a host archive whose `Setting.ini` names
`DeltaReproCalFile` and `WholeReproCalFile` members. That observed host-package
state is not evidence that the ECU has entered a recoverable boot state.

### The saved last message is consumed as failure-report data

The previous observation that `SetLastCommunicationMessage` only copies data
was extended to its CUW consumers. At `10030F8D..10030F92`, CUW supplies the
host record `1008CA88` to the J2534 object's setter. In `1004A940`, the saved
address/header and payload are converted to printable hexadecimal strings;
a negative response's NRC is extracted for the error classification. There is
no replay of that stored byte array into a diagnostic sender in the reviewed
consumer. `_InformResultOfQueryRetry@8` at `1005E180` clears the entire `1028`-
byte record at `1005E21D..1005E227` before signaling the retry decision. Thus
this record does not fill the missing P5 abort/normalization operation.

### Source and recovery-state boundaries

The protected inputs, sidecars and recovered copies of `CUW.dll` and
`TCUWJ2534DeviceIF.dll` matched the existing CUW recovery manifest. The existing
working x86 Ghidra project's memory was compared with the current recovered
CUW PE over `1004A850..1004AD4F`, `1005E180..1005E2CF`,
`1005F000..1005F14F`, `1005F800..10062597`, and `10064800..1006488F`,
bounding use of its decompiler output. The work neither relies on a different-version
host graph nor changes the ECU image. Working disassemblies and comparison
metadata are under `build/work/f33-native-admission-20260912/` and are disposable;
the current PE and exact source spans are the evidence inputs.

A fresh file-only comparison reproduces **488** factory differences in stage6
and **492** in the incident reconstruction, all within the native upper-region
erase extent. Returning to the prior working stage6 image remains a legitimate
unbricking objective; factory-exact restoration is not imposed as a separate
requirement. Canonical F33 decompilation of `4332/43BE` confirms that ordinary
programming still calls the installed RAM driver through `FEBF0FD0`.
Consequently neither the correct rollback bytes nor a raw factory image alone
is a runnable, target-independent native restoration method.

No prepared-state EPS response, native flash operation, or repaired application
startup was observed. The configured comma still timed out before the read-only
SSH command ran. These results close additional **host-side composition**
questions; they do not turn the gateway reachability hypothesis into a complete
end-to-end network repair.
