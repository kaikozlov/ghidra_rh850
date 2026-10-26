# Toyota TSS3 runtime ownership and signer integration

The maintained runtime is the request signer exposed by `tools/toyota ram`.
For the current Camry port and inspected software pins, see the
[capability matrix](../variants/camry-2026-capability-matrix.md).

## Current shared request-signer contract

Openpilot owns the complete `0x08A` application request and its publication.
The EPS-resident signer supplies authentication. It is not a lateral controller,
longitudinal controller, planner, or second engagement policy.

| Owner | Responsibility |
|---|---|
| openpilot | Engagement, planning, lateral/longitudinal control and driver interaction |
| opendbc Toyota interface and CarState | Vehicle identity, observations and standard CarParams/CarState |
| Toyota CarController | Convert CarControl to the request application, using ordinary controller limits |
| SignerTransport | Exchange requests and signed responses; manage transport availability |
| Toyota safety | Independently check requests and control replacement/forwarding |
| Bringup tooling | Prepare the resident signer and report installation status, outside driving policy |

The host transport uses four Classical CAN request fragments. Openpilot receives
the authentication trailer and publishes the completed request; it does not
reconstruct freshness from native request generations. Stock-longitudinal mode
preserves the FRC's longitudinal fields; openpilot-longitudinal mode supplies
the controller's acceleration request. Both modes use the same signer.

The maintained repinned topology is chassis/state bus 0, FRC/source bus 2 and
auxiliary/radar bus 1. Panda suppresses the replaced FRC request while host
ownership is active and restores native forwarding on release or timeout.
The source implements PCS handoff separately; see the
[port report](../variants/camry-2026-tss3-opendbc-port.md#pcs-observation-and-implementation).

The runtime is volatile. Build and package ownership lives in the existing
[workflow](../WORKFLOW.md#ram-resident-tss3-build-and-kit-workflow), not in a
second set of installation instructions here. A change to opendbc safety also
requires the corresponding Panda firmware build and deployment; changing host
source alone does not update a deployed safety implementation.

## Host integration

The port's manual and automatic bringup consumers share
`openpilot/selfdrive/car/toyota_tss3_oracle_status.py`; kit compatibility is
owned by `toyota_tss3_oracle_kit.py`. Those interfaces report backend/process
results rather than infer vehicle readiness from a UI message.

Source locations in the inspected sibling checkout:
`opendbc/car/toyota/tss3.py`, `carcontroller.py`, and
`opendbc/safety/modes/toyota.h`; the checkout identities are recorded only in
the [capability matrix](../variants/camry-2026-capability-matrix.md).

## Target-specific evidence

The following retained audit records the firmware and machine-model basis for
cross-target runtime compatibility. Its target identities and modeled/hardware
boundaries do not establish whole-vehicle support on another car.

## Cross-variant resident control ingress

Exact Camry F33, Corolla H, Corolla F, and Crown F30 expose the same physical
request contract: four classic standard-`0x777` records accepted by the stock
functional CAN rule. The helper reads those records through a private cursor
over the software RX ring; it does not depend on or modify the stock consumer.
Header nibbles `8..B` are intentionally invalid ISO-TP PCI types, so no CanTp
reassembly, PduR copying, DCM buffer, service lookup, or diagnostic response
state is part of the recurring request path.

The resident executes the target's stock foreground calls unchanged. It may
service pending private-ring records in a timer-bounded idle window; the outer
post-foreground call remains the fallback.
### Shared P1M-E RAM-execution invariant

This runtime does not depend on a Camry-only processor feature. Camry F33 and
Crown F30 use the 1-MiB `R7F701381`; Corolla H/F use the 1-MiB `R7F701383`.
Both are RH850/P1M-E DPS variants with the same 160-MHz core, 16 MPU channels,
128 KiB PE1 Local RAM, and 64 KiB Global RAM.

The manual's architectural instruction-fetch map names the self Local-RAM view
`FEDE0000..FEDFFFFF` and Global RAM. Exact firmware control flow and retained
live payloads independently prove instruction fetch through Toyota's PE1 view
`FEBE0000..FEBFFFFF`; the Ghidra profile therefore maps the self view as a byte
alias of the PE1 backing and marks both views executable. Execution permission
still depends on the active MPU region: the recovered payload regions use
`MPAT=0xB8` for supervisor read/write/execute or `0xA8` for supervisor
read/execute.

Publishing newly written RAM code requires the G3M ordering from the CPU
manual: complete the stores, perform a dummy read from the written region,
execute `SYNCP`, execute `SYNCI`, then branch to it. The processor can
speculatively fetch up to 48 bytes beyond the code body, so that trailing range
must also be initialized and access-permitted. The universal request-signer
builder rejects missing publication sequences and makes a 48-byte zero guard
part of both copied executable artifacts; their metadata separates code and
guard sizes. Global-RAM data writes are hardware-coherent/write-through on
P1M-E, but that does not replace instruction-cache publication.

RAM clearing is reset-class-specific. `STAC_LM0` controls local-RAM
initialization for the reset classes listed by the device manual; it is not a
blanket promise that every reset clears every local-RAM view. Target builders
must continue to prove the exact boot/reset path and startup write survival
from firmware.

What differs per firmware is a small signer/I/O ABI: RX ring and producer,
authenticated trip/reset cells, state/scratch placement, freshness encoder,
command-5 wrapper/globals, lower CAN writer and transmit handle. These values,
the startup span, and the foreground calls are no longer a vehicle-named code
table. The builder resolves them from unique machine structures in the supplied
CodeFlash and rejects a missing or ambiguous structure. The registered exact
CodeFlash hashes bind the resulting profiles; an unregistered dump is bound by
the hash in its onboarding report. Panda logical-bus routing remains external
registry metadata because it is not encoded by these CodeFlash structures.

The audited binary contains three runtime configs for four targets;
Corolla H/F resolve to the same application software ID and ABI. The registry's
bus metadata below is separate from the maintained host topology above:

| exact target | Registry bus metadata | RX ring / producer | resident state | response lower handle | signer scratch | command-5 globals |
|---|---:|---|---|---:|---|---|
| Camry `8965F3307000` | 0 | `FEBE4038` / `FEBE48F8` | `FEBF025C` | 53 | `FEBF0280` | `FEBF13A0` |
| Crown `8965F3012000` | 1 | `FEBE3E98` / `FEBE475A` | `FEBF025C` | 50 | `FEBF0280` | `FEBF13A0` |
| Corolla `8965H1202000` | 1 | `FEBE3F4C` / `FEBE480C` | `FEBFF9F0` | 50 | `FEF07F98` | `FEBF1264` |
| Corolla `8965F1208000` | 1 | `FEBE3F4C` / `FEBE480C` | `FEBFF9F0` | 50 | `FEF07F98` | `FEBF1264` |

The response handle is derived from the exact generated CanIf diagnostic class.
In all four images, class 2 contains primary/functional `0x7A9` on local HTH0 and secondary `0x7A8`
on local HTH1; the class-route base is 2, so `0x7A9` resolves to global HTH2.
That is resource 6 / lower handle 53 on Camry and resource 6 / lower handle 50
on Crown and Corolla. The former four-resource heuristic incorrectly selected
Crown HTH3 / handle 51 / resource 7, which is the secondary `0x7A8` route. The
machine verification now executes both the exact lower wrapper and the complete
compiled C helper against the selected primary route on every registered image.

All four default to the same four-message classic standard-`0x777` request
codec, standard-`0x7A9` response, and 36-byte command-5 authentication domain.
Headers `8s`, `9S`, `As`, and `BS` encode ordered fragments 0..3 while
repeating the low/high nibbles of the complete 8-bit transaction sequence. Each
message contributes seven consecutive bytes, so the helper reconstructs all 28
application bytes verbatim.

## Cross-variant request-signer audit (2026-10-12)

The October-12 audit binds runtime assumptions to each exact image and
separates machine-model results from hardware/key observations.

| surface | Camry | Crown | Corolla H/F | audit result |
|---|---|---|---|---|
| application context | `715B4` | `709E4` | `6A8C4` | exact per-image context loader |
| software RX ring / producer | `FEBE4038 / FEBE48F8` | `FEBE3E98 / FEBE475A` | `FEBE3F4C / FEBE480C` | exact producer/ring tables; machine receive scenario passes |
| `0x777` acceptance | rule label 53 | label 50 | label 50 | exact rule routes all three to diagnostic CFIFO5; exact IRQ187/ring path passes |
| authenticated trip/reset | `FEBE55C0/55C4` | `FEBE50EC/50F0` | `FEBE54AC/54B0` | target freshness code; Crown old signer and Corolla `0x00F` evidence independently corroborate |
| freshness encoder | `90566` | `8E006` | `89876` | target-native body/signature plus exact execution scenario |
| command-5 wrapper/globals | `89BC2 / FEBF13A0` | `87662 / FEBF13A0` | `82ED2 / FEBF1264` | target-native wrapper/global addresses; exact submit/input/output scenarios pass |
| lower CAN writer | `85112` | `812A2` | `7E422` | target-native lower wrapper; complete helper emits both timeout and modeled-completion responses |
| primary `0x7A9` lower route | handle 53 / resource 6 | **handle 50 / resource 6** | handle 50 / resource 6 | exact CanIf diagnostic HTH + class-route + lower route map |
| software confirmation | `85240 -> 8043C -> 8152E` | `813D0 -> 7DAA8 -> 7EB4A` | `7E550 -> 7974C -> 7A83E` | exact lower completion maps controller/resource back to pending `00F0`; dispatcher sends the `F0` class to a one-instruction `jmp [lp]` no-op |

The lower completion entries above are the transmit-interrupt path. The similarly
shaped cancellation wrappers are at `lower_can_write + 0xDC`. Exact
completion-table recovery binds the selected resource back to the pending
software-handle cell (`FEBE5036`, `FEBE4AE6`, or `FEBE4F22` respectively), and
the machine scenario consumes `00F0` from that cell through the target's
dispatcher.

Corolla F `8965F1208000` and H `8965H1202000` have different exact
CodeFlash identities and F181 responses but the same recovered signer-facing
machine contract. Their five-row transmit-resource table maps primary `0x7A9`
to local HTH0 -> global HTH2 -> handle 50/controller 1/resource 6, secondary
`0x7A8` to handle 51/resource 7, and the fifth object to handle 52/resource 8.
The old five-row heuristic already selected row 2, so neither Corolla profile
received the Crown alternate-mailbox selection. The shared runtime selector
`8965F1208000` is bounded by byte-identical boot calls/runtime configuration;
the host manifest still binds the complete target-specific application F181.

Deeper recovery of `812A2 -> 8153A -> 8148E` shows that the request signer calls
the `Can_Write`-shaped lower API beneath that upper association. Handles 50 and
51 map to controller 1 transmit buffers 6 and 7 respectively, but the supplied
`Can_PduType.id` is written into the selected buffer's `TMID` register on every
call. No lower gate compares handle 51 with `0x7A8`. Focused exact execution
therefore sends the same supplied `0x7A9` through either handle: resource 6
becomes global buffer 22 and resource 7 becomes global buffer 23. The `00F0`
software-confirmation value is also consumed through the resource-7 completion
path and reaches the same no-op.

The real behavioral difference is mailbox state. For ordinary transmit buffers,
`8153A` returns 2 without writing a frame when `TMSTS & 0x1E` is nonzero:
pending transmit request, completed/aborted result awaiting clear, or abort
request (P1M-E manual sections 17.3.10.1–2). A focused resource-7-busy scenario
exercises that exact rejection. The machine's successful resource-7 case starts
idle and therefore cannot establish the field value of `TMSTS7`.

The stock primary association is handle 50/resource 6. Successful modeled
transmission through resource 7 does not establish that mailbox's state in a
field run. The retained no-response logs contain neither resident counters nor
mailbox status and cannot distinguish those causes.

The complete-helper status-0 scenario schedules recovered ICU-S
done/status/length and supplied output bytes only after exact command-five
submission. It proves that each target's wrapper, helper checks, success counter,
response packing, lower route, and modeled RSCFD transmit compose. It does not
model provisioned-key cryptography, interrupt timing, or silicon.

The common memory placement was also checked rather than inferred from Camry.
All four startup schedules call the same 36-byte copy loop: CodeFlash
`00010000..00017DEF` is copied to LocalRAM `FEBF7C00..FEBFF9EF`, ending exactly
one byte before the resident at `FEBFF9F0`. The resolver now requires that
exact call and boundary. A generated P1M-E scenario executes the real loop,
checks its first and final copied words, and proves that a nonzero sentinel at
the resident boundary is unchanged on Camry, Crown, Corolla F, and Corolla H.
The GNU lifecycle run likewise leaves that call unstubbed and byte-compares the
post-startup resident, runtime config, and GlobalRAM helper with the built
artifacts.

The application GlobalRAM initializers are bounded far below the helper.
Camry/Crown clear and initialize `FEEF80A0..FEEF9157`; Corolla H/F use
`FEEF8000..FEEF972F`. The complete recovered corpora have no exact application
data reference into `FEF07C00..FEF07FFF`, and the raw images have no aligned
pointer literal into that final 1 KiB. The helper pocket is supervisor R/W/X in
both recovered application MPU contexts. Retained Camry, 2023 Corolla, and 2025
Corolla captures independently show the final 1 KiB all-zero after ordinary
application use.

Camry has live proof for `FEBFF9F0..FEBFFBFB`; Crown's earlier B6 resident ran
from the same retained tail on hardware. Camry/Crown keep state
`FEBF025C..FEBF027F` immediately before scratch `FEBF0280..FEBF02E7`; the state
remains below the SID23 exclusion and scratch ends before the object-15 mirror.
Corolla initializes its state over the already-executed first 36 resident bytes
only after all startup calls return, and uses `FEF07F98..FEF07FFF` for scratch.
The complete helper artifact ends at `FEF07F6C`, leaving 44 bytes before that
scratch. This is strong placement/lifetime evidence, but current-helper
execution from GlobalRAM is hardware-live only on Camry; Crown/Corolla still
benefit from resident-state readback when a field probe fails.

The builder and lifecycle checks cover publication/coherency, guarded bounds,
zero relocations, compare-immediate encoding, exact startup-copy survival and
unchanged stock foreground execution. These are implementation invariants,
not proof of silicon behavior.

The shared `0x08A` freshness policy is no longer a Camry-only assumption.
Re-reading the retained 2025 Span and 2023 public Corolla road logs against the
latest preceding `0x00F` shows that every post-sync `0x08A` trailer carries the
current reset-low2. Every observed new reset epoch begins at SecOC
message-low2=1, then normal adjacent requests advance message-low2 by one.
`0x08A` B26 also advances, but its phase differs between the two captures
(Span: message-low2 = B26-low2+1; public 2023: +2), proving B26 is not the SecOC
message counter. This directly supports the helper's private reset-local message
counter. Canonical counts and the one public-route logging gap are retained in
`data/generated/corolla_hf_secoc_00f_freshness_bridge.json`.

Camry's retained native-`0x08A` equality oracle matches EPS slot 4 in 3/3 samples.
Crown's earlier B6 signer exercised EPS slot-4 command five.
