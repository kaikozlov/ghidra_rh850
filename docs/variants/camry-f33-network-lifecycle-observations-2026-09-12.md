# F33 network recovery: original installer record and normal exit-path evidence

2026-09-12. Network-only research; no connector access, vehicle commands,
ECU reset, uploaded payload, or flash operation was performed. No working EPS
repair is established. This note records distinct evidence without rewriting
parallel edits in the larger recovery reports.

## 1. Original installer stdout is available without the comma

The Mac retains the original tool results in the project-scoped session
`~/.codex/sessions/2026/09/10/rollout-2026-09-10T23-31-27-01a08ebc-1cb8-7881-9f68-4ea81dd22b95.jsonl`.
The selected records are tool outputs, not assistant explanations. A filtered
observation is retained at
`targets/camry-2026/raw-20260912/eps-recovery/installer-tool-observation.json`.
It excludes security material, device-location data and model reasoning.
It is a selected-field copy of stdout, not the complete original telemetry file.

| Original tool-result timestamp (UTC, September 11) | Source line | Operation/result |
|---|---:|---|
| 04:47:45.941 | 455 | Resident preflight: SUCCESS/DONE stages and no reported errors. |
| 04:50:08.921 | 605 | Resident apply: APPLY_TARGET, VERIFY_FINAL, SUCCESS/DONE and no reported errors. |
| 04:50:34.279 | 626 | Hook preflight: `apply_ready=true`, no reported mismatches, 35 telemetry events. |
| 04:51:02.464 | 647 | Hook apply: `payload-complete`, `handler_done=true`, `timed_out=false`, 65 events, no reported errors. |

The hook-apply result itself was created at **04:51:01 UTC**. It records the
initial application F181, then the boot identity before running the writer.
Its configuration is explicitly a **four-byte** patch at `7A272`, original
`80FFEE1C`, replacement `FF02925B`; its expected fixup is `4AED0259` and expected
residue is `FFFFFFFF`. This is the original bad-package run, not a transcript
from the corrected package.

Three retained local artifacts independently match the original run's reported
identities:

- Input stage-6 image: `818338cc3e3dc23f1cf466c72f497699adc9ff33767e67b81fb65bccfab09010`.
- Configured RAM writer: `fe2c46b16096260fa6d438a43d0fc662f444648815058fbe60ee7ea0d12c893a`.
- Expected post-write image: `aba6867f244dda42b754d6f455f25a226ee95025dee6a2d98b07b3ac550f2d74`.

These matches bind the archived run to the frozen binaries already analyzed.
They do **not** turn an expected post-write SHA into a measured flash SHA.
The telemetry file referenced by the original result is
`/data/camry-f33-car-kit-state/hook-install/telemetry.ndjson`, SHA-256
`8439209debceec8e4402b62092ea9cdbb34736d1238114d6fcb0bfd753acc2f4`;
that complete raw file has not been recovered in this pass.

The report semantics were checked in `exploit/patcher/deploy.py`:
`payload_success` requires the SUCCESS and DONE stages with no error event;
`write_crc_sequence_complete` copies that result, whereas the post-image hash,
fixup and residue in `apply` are calculated by `simulate_apply`. Therefore the
original stdout supports a completed, acknowledged write sequence. It is not
an independent whole-flash readback or proof of the subsequent CPU state.
In particular, `health_after_reappearance` is nested inside the **pre-upload
programming handoff**, not a post-write proof that the EPS rebooted normally.

The previously stated need to reconnect the comma before inspecting any original
installer evidence was too broad. The remaining unavailable evidence is the
complete raw telemetry and a synchronized post-install reset/execution capture,
not this original completion record.

## 2. Normal Unified completion has a functional default-session phase

Fresh native inspection used the current recovered CUWPlus bodies. Their
protected stubs, `.dll._` sidecars and recovered outputs match the source
identities already retained in `gateway-preparation-observation.json`.
This did not use an unrelated older generic flash writer as the Unified flow.

`TCUWCanUnifiedFlashWriter.dll!10001000` constructs three ordinary functional
return-to-default-session requests. The following details are static packet
construction evidence, **not a proposed live sender or abort procedure**:

| Native stores / send call | Constructed transport family |
|---|---|
| `1000105D / 10001083` | CAN `777`, service bytes `10 81`. |
| `100010A4..100010C9 / 100010DB` | CAN `77F`, address extension `FE`, service bytes `10 81`, ISO address-extension flag. |
| `100010F0..1000112E / 10001138` | Phase-6 exported address `18 DB EF E0`, service bytes `10 81`, extended-CAN-ID flag. |

The second identifier follows from the actual little-endian store: it is
**77F**, not 7FF. The Phase-6 address comes from the UnifiedUtils export at
`100081A8`, not an assumption about this Camry's bus.

The helper's only direct call in the executable sections is **10001893**.
Its normal path first requires the target-reset exchange at **10001857**,
stops synchronization messages at **10001864**, waits, and then invokes this
functional cleanup. No executable literal-pointer alternative to this helper
was found in that PE; the one literal-pattern occurrence is in the PE header.
That is a bounded native callsite survey, not a proof against every computed
call.

This timing matters: the cleanup exists, but it is found in **successful
completion after target reset**, not a verified stand-alone abort path for an
unresponsive target. It cannot automatically fill the P5 preparation-abort
proof gap. Nor does the name “default session” imply any change to CodeFlash.

The separate SMC follow-up remains distinctly addressed. At
`10001961..100019B8` the caller matches the package string `0751`, reads its
programming-control state via `751/761`, and conditionally calls its type-4
stop operation. Its expected reply address is not this Camry's `758/5F`.
This confirms the family restriction already documented in the current
network-gateway evaluation rather than creating a new Camry command.

An additional suggestive export,
`TCUWJ2534DeviceIF.dll!SetLastCommunicationMessage @ 10004600`, only copies
message metadata/payload into an enabled host record. The reviewed body has no
network send. It is not a deferred target-reset or recovery executor.

## 3. Correct the premise about the brake ECU's downstream CAN leg

Exact **2025 Camry LE / 2.5L VIN A, 04/2024-onward** Toyota service pages were
acquired and their images examined. They are model-family service evidence,
not confirmation of every terminal on the owner's exact 2026 VIN.

The brake terminal table explicitly calls A30-34/35 `DC1H/DC1L` a **daisy-chain
communication line** and A30-36/37 `CA1H/CA1L` CAN communication line 1. The CAN
terminal table places both pairs under **Bus 4 main lines**. The overall
network diagram shows EPS at the termination of the main line through BRK1;
its legend marks gateway-equipped units with an asterisk, and BRK1 has no such
mark on the drawing. The current GTS topology lists Central Gateway, not an
additional brake gateway, in the EPS gateway path.

Measuring approximately 120 ohms on each disconnected leg does **not** prove
that the brake ECU implements two separately controlled buses. Splitting a
single normally joined bus between its two terminating resistors produces the
same result. Thus the earlier inference “two connector pairs plus these
resistances proves a software bridge” is unsupported.

This does not prove the exact internal copper connection or exclude every
filtering component inside BRK1. It means a network command to open or program
an alleged brake gateway cannot be justified from those resistance readings
and connector names alone. No physical disconnection is proposed here.

Toyota source reproductions and original figures:

- CAN system diagram: https://lemon-manuals.la/Toyota/2025/Camry%20LE%2C%202.5L%20Eng%20VIN%20A/Repair%20and%20Diagnosis/Accessories%20%26%20Equipment/Communication%20Devices/Can%20Communication%20System%20-%20Diagnostics%20-%20Introduction/Can%20Communication%20System/System%20Diagram%20%5B04%2F2024%20-%20%5D/System%20Diagram%20%5B04%2F2024%20-%20%5D/
- Brake terminals: https://lemon-manuals.la/Toyota/2025/Camry%20LE%2C%202.5L%20Eng%20VIN%20A/Repair%20and%20Diagnosis/Brakes/Mechanical%20-%20Hydraulic/Electronically%20Controlled%20Brake%20System%20-%20Diagnostics%20-%20Introduction/Electronically%20Controlled%20Brake%20System/Terminals%20Of%20Ecu%20%5B04%2F2024%20-%20%5D/Terminals%20Of%20Ecu%20%5B04%2F2024%20-%20%5D/
- Overall topology: https://lemon-manuals.la/images25/GTY1267625/
- EPS branch: https://lemon-manuals.la/images25/GTY1267483/

## 4. What remains a distinct network-only experiment

The supported gateway-preparation condition in
[the network-gateway evaluation](camry-f33-network-gateway-evaluation.md)
remains different from repeating EPS session requests. The initial identity
read in the normal Unified preparer is optional: its timeout can be caught
before gateway preparation, while the mandatory target programming exchange
is later. Correctly preparing the actual `750/758`, extension-`5F` gateway is
therefore an untested condition rather than something already ruled out by
ordinary EPS silence. The precise family must be selected from its validated
response, with its supported manufacturer authorization and exit handling.
A reply from the gateway alone is not evidence that the EPS executes.

This pass did not complete that experiment. A read-only SSH attempt to the
configured comma failed before any device command ran; the router's existing
lease still assigns the same address to that named device. No existing comma
cloud API credential was available, so no cloud request was made. The missing
live response is not replaced by guessing a family, borrowing another ECU's
calibration, or omitting authorization.

No network-only recovery sequence has yet been shown to restore the EPS.
The newly recovered installer evidence, normal-exit inspection and topology
qualification narrow the next decision; they are not a claim of a repair.
