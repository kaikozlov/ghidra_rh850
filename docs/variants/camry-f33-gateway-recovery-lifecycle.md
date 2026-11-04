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
  path requires real target responses.
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
successful target response. The exact F33 CUW remains unacquired.
The separately archived inverse is available below.

## 2. Preparation completion comes after target execution

The complete current Unified preparer establishes this P5 order:

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
DH gateway branches remain distinct. Select them from actual topology and
responses.

Stopping periodic transmissions and receive filters appears in the preparation
error/cleanup path. These operations provide **host transport cleanup**.
The post-programming callback owner is now resolved:

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
referenced config, shellcode and payload. These retained local incident artifacts
must be acquired separately from a clean checkout. The disposable
result is `build/work/f33-gateway-end-to-end/archived-rollback-audit.json`.

This proves the **byte-image inverse**.

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
placeholder shared with the application. Exact application producer `4FA26`
emits the same `02 || 32*21` response when its compatibility-status getter
`62E18` is nonzero.
The complete application producer, its status getter, and the boot RDBI table
are unchanged in the retained incident reconstruction. Normal compatibility
bytes match in that reconstruction.

An independent, ordinary read-only distinction is available if the target
answers: the application implements **F186** through `4FA7C -> 91AF4 -> 924FC`,
which copies its current-session byte from `FEBE595C`. The exact boot handler
`5FB8` checks four 12-byte descriptors at `8F14`; only F181 is readable. In a
supported boot session a well-formed F186 read therefore gets the explicit
unknown-DID negative response.
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
None of those live observations was produced in this pass.

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
Its role-82 plugin is `GetCID_SID22_GearShiftControl_DT.dll`.

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
native programmer and the exact F33 receiver.
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
and 78 bytes spanning the confirmation context. Decoding used the retained
low-region disassembly of this target.
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
`build/work/f33-network-return-20260912/`. These disposable outputs are optional
for portable verification.


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
Undoing the incident and returning every byte to factory state are distinct goals;
the archived stage-7 inverse remains an incident rollback even though it preserves
the previous stage-6 modifications.

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
3. These comparisons cover **saved images**.

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
same metadata page through the ordinary data-writing branch. These semantics
come from the native firmware.

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
uv run --locked python -m tools.targets.camry.analysis.analyze_camry_f33_recovery_image SAVED_CODEFLASH.bin
tools/test camry_f33_recovery_image
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
The OEM-package branch still needs acquisition of an exact package.

**Remaining composition gap:** no prepared-state EPS response was observed;
no compatible native restoration was executed; the repaired application has
not reappeared. A read-only SSH retry returned "Host is down" before any device
command ran. The restoration coverage is more tightly established, but this
is still not a completed network-only recovery route.


## 11. Normal host phases are not an independent network entry

Returning to the previously working pre-incident image is a valid **unbricking**
goal. Factory-exact restoration is optional. The
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
11 portable tests also passed.
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
at `100082A4/100082B0` select **750/758 with extension E9**. It reads
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


## 11. The surviving 7A2 response is a camera-side control

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
alternate EPS programming CPU merely because it is adjacent to 7A1. This
identification joins OEM install-set data with the observed fault.

Both current camera category 5005 and gateway category 443 use selector DC,
frame 2B54, for normal F181 reading. Their identical request service does not
make them the same endpoint. The gateway's separate **750/758, extension 5F**
route remains the relevant route for the prepared-network hypothesis.

## 12. The incident reconstruction also passes the native regional CRC inputs

The retained incident's startup integrity was checked against **the actual boot
descriptors**. Fresh exact-target decompilation of `3438`, `344C`, `47EA` and
`481A`, together with
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
and admission **before preparation** was followed into native current `CUW.dll`.

### Native handling of an absent CID

`_JudgeFlashable@16` at `10061B70` reaches the worker at `1005F800` through its
normal or alternate loaded-package paths. In the reviewed worker:

- `1005F927..1005F9B2` reduces the selected node's per-entry bitmap.
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


## Read-only gateway selection and native cancellation: caller-level follow-up

2026-09-12. Offline investigation of the actual OEM route, with no vehicle
request, mode change, reset, upload or write.

### The actual Unified caller enables the legacy query first

Current `TCUWCanUnifiedPrepareWriter.dll!10001DA8` pushes **0**, then calls
`CCanCommonPrepareWriter::JudgeReproGWNode` at `10001DAE`. In the current common
helper, `10001930..10001934` skips its one-byte query only when that argument
is **1**. The selected caller therefore does not skip it. The helper first
constructs bare `3E`, requiring positive prefix `7E`, and assigns enum2 after
success; only its permitted fallback path tries `3E 00` / `7E 00` and assigns
enum1. Vehicle year and a P5 database label do not substitute for that exchange.

The existing standalone CLI can express both non-programming requests through
11-bit `750/758`, address extension `5F`. New end-to-end tests exercise the
real CLI and ISO-TP implementation with only the Panda replaced by a fake:

- Bare `3E` and `3E 00` remain different payloads; exactly one host CAN
  submission occurs for each test exchange.
- A returned-TX echo and unrelated `0F`/`6D` logical-node responses cannot
  stand in for the gateway's response.
- A negative `7F 3E 13` remains negative. Raw CLI exit code zero confirms only
  transport-exchange completion. Gateway-family selection needs its own valid response.
- Both the current default registry and the older test fixture work with
  an explicit numeric endpoint, without triggering VIN/vehicle discovery.
- Explicit OBD multiplexing selects Panda bus 1 / ELM327 parameter 0.
  The EPS normal-harness path retains its separate bus assignment.

The committed tests are
`toyota-diagnostics/tests/test_gateway_raw_cli.py` (`08539fe`, `b3cb8b8`);
that file plus `tests/test_transport.py` passes **15 tests**. No production
runtime was changed in this pass and no extra raw probe framework was created.

The literal `5000` passed by the legacy-query caller is not proved to be its
initial response timeout. `TCUWCanDiagCommUtils!10001586` obtains the existing
J2534 timeout; `100016DF..100016E4` applies the caller's final argument in its
response-pending branch. Do not turn that literal into a guessed initial wait
or claim that the raw CLI's timeout behavior reproduces the full OEM helper.

### Searching for historical gateway identification

A separate local sweep examined **559** earlier saved rlogs (5,608,876,389
compressed bytes) and found no `750/758` extension-`5F` record. Another sweep
checked cached `carParams.carFw` in **598** saved rlogs: **703** CarParams
records containing **1,134** firmware entries, with no entry identified as
the gateway or as `750/5F`. This also checks identification cached before logging
began.

The observed `761` frames are sixteen `sendcan` requests, their sixteen
returned-TX records and sixteen forwarded copies, all carrying `3E 00`. They
are not responses from the alternative OEM gateway family. Archives can duplicate
time spans, and one earlier file reports corrupted events. These numbers measure
file/cached-record coverage, which may include overlapping spans. The maintainer-local
inputs are under `/Users/kai/dev/inspect/logs/camry-2026`;
disposable sweep code/results are in `build/work/f33-historical-gateway-baseline`.
No historical positive was recovered to replace the missing live family witness.

### ClearStatus cancellation is not a newly found reverse gateway operation

The exported `CUW.dll!ClearStatusOfReprogramming` reaches `1003FE00`. Its
worker sets the active job's stop byte at **+14** (`1003FE55`) and waits for
that host job. Constructor `10058780` installs vtable `1007C738`; slot +4 is
job worker `10059ED0`. If stop is observed in its initial state, it returns
through `1005A76B`. In the reviewed active phase, `1005A5E2..1005A5F4` selects
the job's +3C cancellation callback when the phase and stop conditions match.

The manager explicitly installs **1003D490** into that +3C slot at `1003C3D6`.
That callback only loads the host object at `1008AE4C`, sets its byte +258 to
one, and returns. It does not send a gateway-normalization packet.

Likewise, current managed `CuwModel::SuppressSleepMode` and
`CancelingSleepMode` set/clear the host static `IsSuppressSleep`. The native/managed
input PEs, sidecars and recovered outputs were matched against their existing manifests.

**Recovery consequence:** completing the appropriate OEM gateway preparation
remains an untested network delivery condition. A gateway reply alone, the
read-only CLI tests, a cached lookup, or setting a host cancellation flag does
not supply the target-side programming executor. In the reconstructed terminal
EPS fault, changing routing cannot repair the bad instruction. An actual EPS
response after a changed network condition is required to overturn that premise;
none was observed in this pass.

## Native software handoff and timed fallback

2026-11-03. Exact stock target `camry-8965F3307000`, immutable CodeFlash
SHA-256 `42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`.
Reconstructed C was checked against original instructions at `56CF0..56D74`,
`58B5E..58C80`, `5F5F4..5F60C`, `5F9BC..5F9CA`, `65F5E..65F86`,
`9F00..9F62`, `1478..149C`, `1338`, `16F2/169C`, and `5086/55AA`.
This subsection owns the native handoff result; the
[exception follow-up](camry-f33-recovery-exception-followup.md#2-a-receive-callback-can-run-without-executing-its-diagnostic-request)
owns foreground ordering relative to the malformed call.

### Readiness wins before the timeout comparison

`56CF6` snapshots the u16 at `FEBE8AC4` into `r29` **before** calling intact
`66F1E`. Return value exactly **1** calls nonreturning `65F5E`; this happens
before the threshold comparison, even with counter `FFFF`. The original
readiness contract is recorded in
[the NvM subsection](camry-f33-eps-recovery-2026-09-11.md#exact-f33-nvm-readiness-and-recovery-state).

ROM `30D5E` contains `14 05`, threshold **0514 = 1300**. On a busy return,
snapshot `<0514` increments once. Equality and every greater u16 take the
fallback and finally store zero. These are invocation counts, not proved time
units. A call starting at `0513` stores `0514`; the next busy invocation takes
the fallback. A ready handoff never reaches that final counter store.

The fallback's actual call sequence is:

```text
98898 diagnostic initialization
91B50 default-session restoration when phase<2 and no slot is receiving
917A4(0) communication-mode update
8E62A application diagnostic/security/admission initialization
FDFFC -> B15AC(0E) indexed request publication
8B114 -> 8B134 programming-admission reset
7FEF8(0800, {data, length=8}) -> software CAN transmit queue
FEBE8AC4 = 0
```

No call in this chain is replaced by a successful return. `98898` itself runs
the DCM timer, event-ring, callback, service, session and receive initializers.
Its immutable condition word `26AE4` is zero. Response initialization uses the
previous current-slot selector **before** receive initialization resets it;
fixtures explicitly provide valid current slot 0. Session notification also
reads sixteen routine-result bytes at `FEBE819B`; their synthetic values are
named inputs, and original `5088A` preserves running result 1.

The negative response is built by original stores as
`03 7F 10 10 00 00 00 00`. ROM `2199C -> 21F80` selects raw CAN ID `7A9`,
controller 0, route class 2. `218E4 -> 21ACC`, descriptor index 2, selects
software queue 2 with seven-word capacity; `21A5C` selects `FEBE3E48`.
The expected five-word record is
`08008408, F7FF7BF7, 000007A9, 10107F03, 00000000`.
Only the software controller signature, enable/mode fields and an empty queue
are preloaded; no peripheral transmit completion is supplied.

### Mode entry, steady state and integrity fallback differ

Real `58B5E` first checks restart/status redundancy, then `58B1A` executes its
six original snapshot-copy bodies. With an intact previous-mode complement,
a changed current mode takes the redundant mode vote and the entry-dispatch
chain ending at `5F464`. An unchanged mode takes the steady chain ending at
`5F91C`. A bad previous-mode complement instead republishes the current mode
and its complement and takes the **steady** chain, even when the old raw mode
differs. A valid restart request `A55A` with valid triplicate status selects
reinitialization at `5886C`; unrecoverable restart redundancy clears the request.

Both diagnostic dispatchers select `56CF6` for unsigned mode **>=0900**;
`08FF` does not select it. Only entry `5F464` additionally calls `56CF0`
to clear the counter when the previous mode was `<0900`. A transition already
inside that band preserves the count. `5F91C` never performs the entry reset.

The full-generation fixtures enter **58B5E**, execute acquisition, and stop at
the selected monitor dispatcher `5EC24` or `5F610`, before its body. Their
558 sparse source fields each cite the exact original copy-function load PC.
Separate post-acquisition fixtures start at `58BFA`; terminal diagnostic-band
fixtures start at `5F5F4` or `5F9BC`, execute the actual comparison/reset/caller,
and stop before output publication at `58074`. These checkpoints isolate the
mode gates; they do not claim one continuous execution of all intervening
monitor, thermal, control and diagnostic-service bodies.

### Live transfer sanitizes CPU context before boot diagnostics initialize

`65F5E` raises PMR and writes zero separately to the four backup registers
`FFC0A000/4/8/C`, reads the last word back, synchronizes, and calls
`9F00(31788)`. The model accepts each **four-byte BRAMDATn register**, not a
single sixteen-byte preload. R01UH0585EJ0120 section 36.3.2 specifies retention
across reset and leaves initial backup data unspecified; four distinct synthetic
pre-handoff words expose every clear.

At `9F00`, the backup words are already zero but application SP/GP/TP have not
yet changed. At `148E`, original code has established PMR `FFFF`, PSW `18020`,
SP `FEBE8000`, GP `FEBF9800`, TP `869C`, EBASE 1, INTBP 0 and MPM 0.
`r6=31788` still identifies the original ROM record. `148E ->1478` copies its
nine words into `FEBF2908..FEBF292B`:
`0,7A1,0,0,2,0,0,0,0`. At `1398`, SP is `FEBE7FFC`; the record copy is
complete and diagnostic initialization has **not** run. PSW is now `18029`:
the final `LOOP r8` at `1488` adds `FFFFFFFF` to 1, setting CY and Z and clearing
S and OV (RH850G3M R01US0123EJ0140 p.256). This arithmetic-flag change does not
undo the context sanitization.

`1398 ->1338` sets `FEBF2904=1`, clears `FEBF2900`, then enters the real CSIH1
exchange at `16F2`, before CAN/boot-diagnostic initialization. The exact receive
and record contract is below. Central execution of the complete ready handoff
with no serial input reaches **17C2**. The native-handoff scenarios supply no
serial reply. The separate boot-reply matrix supplies explicitly synthetic
completed words to characterize conditional software acceptance.

The separately labeled software-reset closures enter original `5086`, or
sequence intact `69D2 ->6A22` after an explicit handoff-record checkpoint.
They exercise the master enable gate, default session, cleared diagnostic
privileges, and original security-material initialization. The continuation
stops at `152A` before relocated flash-driver preparation. It is a later-entry
software closure, not evidence that the preceding serial/CAN hardware
initialization completed. In particular, CPU context reset at `9F00`, record
copy at `1398`, and diagnostic session/security reset at `5086/55AA` are
different boundaries.

### Boot CSIH1 reply acceptance contract

Static evidence is the retained Camry source (`tools/toyota decomp source`
`16F2`, `169C`, `15C0`, `167C`, `1626`, `1338`) and exact target disassembly.
This subsection applies to CodeFlash SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`.

**Transaction order.** `16F2` zeros its eight-byte receive record, disables
CSIH1, configures master/dual-buffer operation, clears pointers and selected
status flags, enables transmit/receive, then waits `7208(50)`. The outgoing
halfwords are `8C00,0000,F000,1F11`; `167C ->15C0` computes the low check byte
before `1626` submits them on CS0. The first three TX words carry control
`20FE0000`, the fourth `00FE0000`; `MCTL2=80040000` starts four words.
After another `7208(50)`, it attempts the same submission again, waits
`7208(50)`, and starts receiving. Both submission return values are ignored.
A busy first exchange can therefore suppress the second submission; there is
no transaction identifier tying the received record to the second attempt.
A completed first response is normally superseded when the second submission
clears the receive pointer.

**Receive gate (`169C`).** These are literal register tests, not a decoded
peripheral error taxonomy:

| Condition | Return | Destination effect |
| --- | --- | --- |
| `STR0(FFD82004).bit7 != 0` | `5AA5` | No write |
| `(MCTL2(FFD83004) & 7F) != 4` | `5AA5` | No write |
| `((MRWP0(FFD83018) >> 16) & 7F) != 0` | `A55A` | No write |
| All three gates pass | `0` | Four successive halfword reads of `FFD83014` fill offsets `0,2,4,6` |

`MCTL2 & 7F` is the buffer start pointer, not a receive FIFO count; the
`MRWP0` test is the read pointer. Other bits, including `MCTL2`'s high count
field and STR0 communication-error flags outside bit7, are not inspected here.
The exact instructions are `SHR 8; BC` at `16A4/16A6`,
`ANDI 7F; CMP 4; BNE` at `16AE..16B4`, and
`SHL 9; SHR 19; BNE` at `16BC..16C0` (shift operands hexadecimal).
The model independently requires actual supplied receive-buffer entries before
allowing any data read.

**Only record validation.** `15C0` seeds DCRA0 with `FF`, `CTL=22`, and feeds
`w0.high,w0.low,w1.high,w1.low,w2.high,w2.low,w3.high`, in that order.
Its final XOR `FF` cancels the hardware read XOR, leaving the raw
MSB-first polynomial-`1D` CRC8 remainder. `17BA..17C0` compares that result
with **`w3.low` only** (`LD.BU 6[sp]; CMP r10,r1; BE 17C4`).
There are no reply-opcode, payload, reserved-bit, status-field or request-echo
checks. For example, synthetic `0000,0000,0000,00F5` and
`6400,0001,F000,0038` both meet this software contract. These are conditional
records, not observed boot-peripheral responses.

**Timeout/failure.** Each poll, including a successful one, is followed by
`7208(1)` before the byte counter increments. Return `0` ends polling;
both `5AA5` and `A55A` retry identically, up to **201 calls**. After poll201,
even a completion during its trailing delay is not read again.
`7208(n)` executes 155 inner decrements per unit; its instruction count for
positive `n` is `313*n+5`, not a measured elapsed-time bound. The loop does
not explicitly reject timeout: it always validates the local record.
Unsuccessful polls leave its initial zeros intact, whose required check is
`F5` rather than the retained low byte `00`, so they reach the original
`BR 17C2` (`85 05`). A bad received check reaches the same permanent loop,
without cleanup or a diagnostic error publication.

**Downstream consumers.** The received record remains local to `16F2`;
`1338` ignores its returned CRC. Acceptance permits `121A` to write/read
`FFFF8000=1`, then ECM setup `1228`, interrupt setup `17C8`, CAN configuration
`3B3C`, driver initialization `35BC`, queue/constant/region-CRC initialization,
timers `1CA0`, and diagnostics `770`, in that order. Parent execution of the
initial downstream scenario stopped during ECM setup with
`missing post-reset input for ECMMESSTR2`, before reaching CAN initialization.
The exact boundary is `132C` (`05 0D`, `SST.W r1,8[ep]`), the third protected
write committing `ECMESSTC2(FFD6203C)=7FFFFFFF`. The model reads both status
banks before clearing either, preserving their external pin bit31.
`ECMMESSTR2` and `ECMCESSTR2` have reset mask `7FFFFFFF`; bit31 represents
ERROROUT/ERROROUT_C feedback, not a reset-zero constant
(R01UH0585EJ0120 section32.4.6, Table32.20). The revised downstream fixture
stops immediately **before** `132C`, after the synchronized gate, ECM masks
and earlier status clears; it supplies no pin feedback. `ECMPEM` is initially
written `3` at `1230`, then explicitly restored to `0` at `12F6` and read back
at `12FC`, before any status-clear sequence. Its expected value at `132C` is
therefore `0`, while `ECMEMK0..2` retain `FFFFFFE1,FFFFFFFF,3FFFFFFF`.

After that prerequisite, the later static boundary `3B3C ->3818` waits for
`GSTS(FFD2008C).bit3` (CAN RAM initialization) to clear. The device definition
resets GSTS to `0D`; the inspected machine implements no completion transition
for that bit. Later still, `35BC ->3584` sends the distinct `8800` record until
`FFA10000.bit7` permits progress. These are subsequent prerequisites, not
boundaries reached by the retained downstream fixture.

#### Retained conditional boot-reply scenarios

All sixteen standalone `camry_f33_boot_reply_*.json` fixtures passed exact-image
execution: fifteen reply-only cases in `boot-reply-wave2`, including both
final-poll timing cases, and the downstream `132C` checkpoint in
`boot-reply-wave3`, under `build/out/firmware-question-campaign/`.
They call only original firmware, with bounded stack preloads and finite
explicit `csih-word` inputs, using the serial event
contract in [the harness documentation](../tooling/rh850-build-and-sim.md#original-reset-without-supplied-serial-completions).
Suffixes below share that prefix:

| Fixture suffix | Consumer-visible boundary to check |
| --- | --- |
| `valid_zero_payload`, `valid_arbitrary_payload` | CRC-only acceptance at `17C4`; distinct first reply is superseded |
| `invalid_check_byte`, `invalid_payload_with_stale_check` | Single-byte check/payload changes reach `17C2` |
| `partial_second_record_0_words`, `_1_words`, `_3_words` | Pending/partial second exchange never publishes a record; 201 polls then failure |
| `last_poll_accepts_completed_record` | Explicit final-word latency lands before poll201; record accepted with counter201 |
| `completion_after_last_poll_is_not_repolled` | Final word completes during poll201's trailing delay; zero local record still fails |
| `late_first_record_satisfies_poll` | Busy first exchange suppresses second submission; its late valid record is accepted |
| `receiver_busy`, `receiver_short_start_pointer`, `receiver_long_start_pointer` | Direct original receiver returns `5AA5`, preserving caller record |
| `receiver_read_pointer_bit16`, `receiver_read_pointer_bit22` | Low/high ends of the seven-bit read-pointer gate return `A55A`, preserving caller record |
| `accepted_reply_before_ecm_status_clear` | Original `1398 ->1338` passes reply validation and the synchronized gate, programs ECM masks, and stops at `132C` before the clear that requires external ECM pin feedback |

The status-only fixtures explicitly preload synthetic register snapshots and
never claim an actual received word. The timed fixtures use 128-instruction
functional word latency except their named late completion; the two final-poll
cases declare final-word delays 91550 and 91800 from its actual launch.
Their expected poll counts were statically derived and confirmed by parent execution.
The existing `camry_f33_handoff_boot_first_serial_exchange_no_synthetic_reply`
covers entirely absent input; existing `csih-partial-wire-completion-keeps-frame-pending`
and `csih-original-frame-complete-and-poll` cover shared controller behavior and
the separate application driver. They are reused, not copied.

```sh
tools/rh850 test firmware camry-8965F3307000 \
  tests/fixtures/rh850/machine/camry-8965F3307000/camry_f33_boot_reply_*.json
```

No boot CSIH1 response capture was found in the tracked serial documentation,
fixture inventory or capture references inspected for this closure. Existing
synthetic application/reset serial inputs are not boot-peer observations.
Physical closure requires a time-correlated CSIH1 CS0/SCK/MOSI/MISO capture
of the original `8C00` exchange on this ECU, including both attempted frames,
actual reply words and timing, plus the later `8800` exchange and
`FPMON.FWE`/FLMD0 transition if continuing through `3584`. CAN readiness and
diagnostic startup require their own subsequent observed inputs. The retained
conditional cases do not establish completed hardware startup.


### Executable evidence

Standalone `camry_f33_handoff_*.json` scenarios live in
[`tests/fixtures/rh850/machine/camry-8965F3307000/`](../../tests/fixtures/rh850/machine/camry-8965F3307000/).
All **40/40** handoff scenarios passed central original-byte execution with
status `verified-local-execution`. Coverage includes readiness versus busy,
threshold-minus-one and two-invocation threshold crossing, at/over-threshold
fallback initialization, session/admission/security reset, request `0E`, the
queued negative response, all four backup clears, CPU context replacement,
record copying, full acquisition-mode selection, restart/integrity
discrimination, both terminal mode-band gates, and the no-reply terminal at
`17C2`. The separately entered boot reset runs through `69D2 ->6A22`.
Fallback also executes `6A156`, publishing abort request `5A` for an explicitly
active crypto-direct lifecycle. Every synthetic entry-state contract is explicit.

Two-call fixtures use only the fourteen-byte RAM sequencer
`MOV 798,lp; MOV original_function,r1; JMP [r1]`; no firmware state changes occur
between the two original calls. The `56CF6` encoding is
`3F 06 98 07 00 00 21 06 F6 6C 05 00 61 00`; the `6A22` variant substitutes
`22 6A 00 00` for the target immediate. No CodeFlash overlays, callback stubs,
blanket RAM initialization, fabricated hardware authentication or external ECU
traffic are used.

```sh
tools/rh850 test firmware camry-8965F3307000 \
  tests/fixtures/rh850/machine/camry-8965F3307000/camry_f33_handoff_*.json
```

The fixtures are automatically discovered by `tools/test rh850_firmware`.
These software transitions establish no working physical network-recovery path.
