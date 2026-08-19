# Open questions

Exhaustive unresolved-question ledger. **This is not the execution queue**; for
what to work on next, start with [PRIORITIES.md](PRIORITIES.md).

Once resolved, a question leaves this file, the result moves to
[FINDINGS.md](FINDINGS.md) (with its evidence grade), and any superseded prior
claim moves to [CORRECTIONS.md](CORRECTIONS.md).

## Bootloader

- **Bootloader DID `0203` semantics.** It ignores its five bytes and only arms
  state 0 → 1. Whether any field ever carried meaning in other calibrations is
  unknown.

## Application

- **`0xAB` event-record naming.** The configured graph is closed and its
  list/per-ID/detail structure is recovered, but the OEM service name and exact
  meanings of the event catalogue's encoded upper ID bits and record-kind
  values remain unknown.
- **Live confirmation of the RDBI stale-response disclosure.** Firmware-static
  analysis proves that DIDs `1CF4..1CFF` and `1D01..1D03` return 45 bytes that
  their success-stub producers never write, sourced from persistent Dcm buffer
  `FEBE59F8`. On an isolated Sienna `8965B4512000` bench, run the default-safe
  `exploit/followups/application_rdbi_stale_probe.py`: its discriminator seeds
  the buffer with a 47-byte SID-`0x23` read and requires `22 1C F4` to equal
  `62 1C F4 ‖ seed[2:47]`. Preserve F181, route, and raw request/response bytes.
- **XCP physical reachability; dynamic-only write consumers.** COM-005 proves
  both the unauthenticated `0x7F7/0x7F8` disclosure chain and a direct 32 KiB
  LocalRAM write primitive (`F0 DOWNLOAD` plus `EC MODIFY_BITS`). COM-007 now
  closes the adjacent DAQ direction: `E1 WRITE_DAQ` configures 112 one-byte
  LocalRAM source pointers, but the periodic engine only loads through those
  pointers into DTO staging and transmits through `0x7F8`; no reverse
  store-through-pointer path is recovered. The known d/q references
  `FEBE6D28/6D2A` and TSG3 compare state `FEBE38A2/38A4/38A6` are DAQ-readable,
  so a reachable channel would provide a non-invasive observer for the dynamic
  actuation discriminator. The separate shadow write window remains RW and
  direct-consumer-negative. Its Ghidra `execute=false` attribute is analysis
  metadata; the hardware MPU grants supervisor execute on that region
  (CORR-060), so the open question is a runtime-computed control-transfer
  consumer, not executability. What is still unobserved is whether a vehicle
  gateway or diagnostic connector forwards CAN `0x7F7/0x7F8`.
  `exploit/followups/xcp_read_probe.py` remains read-only for isolated-bench
  reachability confirmation. `exploit/followups/xcp_daq_probe.py` now adds the
  exact volatile DAQ configuration/capture path, including named actuation and
  diagnostic-state profiles, without implementing the generic F0/EC memory
  writers. Do not exercise generic write commands on a vehicle. Canonical:
  [../communications/xcp-command-dispatch.md](../communications/xcp-command-dispatch.md).
- **Dynamic authenticated-command actuation discriminator.** If COM-007's
  `0x7F7/0x7F8` route is physically reachable on the bench,
  `exploit/followups/xcp_daq_probe.py --profile actuation-discriminator` can
  stream the already-pinned d/q-reference and TSG3-compare RAM directly during
  this experiment without modifying the motor loop. The full-corpus
  extension closes the static join search more broadly than Stage 6. Protected
  `0x2E4` torque control (`BFA2`) and protected `0x131` LTA angle control
  (`AE60 -> ... -> C0D6`) are now proved to converge at `C144`; the common cone
  has been exhausted through `C170/C1B8/C1BC/C1D4 -> B788 -> B87E` and its
  monitor/adaptation consumers. Together with the complete `FEBE6D00..6DFF`
  writer/xref census, producer cone, absolute-pointer scan, generic-memcpy
  census, and RTE-copy audit, no static transfer into `FEBE6D28/6D2A` is
  recovered. This does not prove physical independence. A provisioned isolated
  bench should test the two command modes separately: a valid signed `0x2E4`
  torque request and, where the target supports it, a valid signed `0x131` LTA
  request/angle command, while observing d/q-reference/current/PWM state. Static
  broad searching should not be repeated without a new concrete lead.
  Canonical: [../architecture/control-partition.md](../architecture/control-partition.md) §9.3.

## SecOC

- **Cross-calibration ephemeral runtime transfer.** The Sienna fresh-import
  resolver is now deterministic and the RH850 runtime sources are target-driven.
  What remains is external evidence: run `tools/resolve_ephemeral_runtime_image.sh`
  unchanged on the first foreign CodeFlash. A `semantic-resolved-geometry-unresolved`
  result is useful and must remain non-buildable until that image's authenticated
  download/callback/retention MPU geometry is proven. A build-ready foreign
  manifest then still needs its own inert-canary observation cell. Authenticated
  bootstrap-family evidence is already available for several B4/F3/F4 EPS IDs;
  a target outside those rows needs new bootstrap evidence, while a known-family
  target may still need an explicitly target-accepted encrypted fixture if exact
  byte identity is not pinned. Canonical:
  [../tooling/ephemeral-runtime-semantic-resolver.md](../tooling/ephemeral-runtime-semantic-resolver.md).

- **Ephemeral scheduler-bridge hardware validation.** ARCH-013/014 and
  SECOC-060/061 now close the static architecture without a post-init stock
  callback: the audited 704-byte runtime performs the stock boot/context/startup
  sequence, remains foreground scheduler owner, snapshots marked pre-verification
  `0x2E4/0x131`, runs stock SecOC, and conditionally re-delivers through stock
  `application_com_rx_indication` before the normal COM/system-mode/control
  task. The initial Sienna payload artifact is no longer open: the pinned public
  encrypted RAM-dump fixture already satisfies this exact gate with zero
  DID-0201/0202 inputs. What remains is dynamic: use the audited 332-byte inert
  canary, offline MEM-SAFE substitution plan, and read-only SID-`0x23` heartbeat
  probe to prove scheduler ownership and reset-to-stock behavior; next prove
  one-shot queue capture, then enable COM delivery on an isolated bench. Do not
  resume generic callback/xref searching unless dynamic behavior falsifies a
  specific static assumption. Canonical:
  [../security/ephemeral-secoc-bypass.md](../security/ephemeral-secoc-bypass.md);
  `exploit/ephemeral_runtime/`.
- **Cross-calibration semantic patch resolver validation.** SECOC-045 now
  rediscovers the Sienna authenticated-delivery gate from a fresh unannotated
  CodeFlash-only import with no target/MAC-result/CRC addresses embedded in the
  resolver. The highest-value next artifact is any blurbdust-supported
  `8965F3`/`8965F4` CodeFlash (or the missing Corolla `8965F1208000` image): run
  `tools/resolve_secoc_patch_image.sh` unchanged and compare its unique semantic
  target, if any, with the community egg location. Zero candidates means the
  Level-1 machine shape must be lifted to p-code/CFG data-flow; multiple
  candidates require stronger crypto-result provenance. Do **not** add a
  software-ID offset table as the fallback. Canonical:
  [../tooling/secoc-semantic-patch-resolver.md](../tooling/secoc-semantic-patch-resolver.md).
- **First live run of the generic read-only CodeFlash acquisition path.** The
  addressed-word protocol/reassembler and 424-byte RH850 payload are locally
  complete and pinned-toolchain verified, including authenticated 4 KiB payload
  packaging, address-zero CodeFlash load retention, partial-dump preservation,
  SHA/provenance, boot-CRC sanity, and automatic semantic-resolver handoff. What
  remains is hardware-only: run it on a provisioned EPS over the explicitly
  recorded Panda bus/ELM/UDS route, preserve `F181`, obtain all 262,144 addressed
  words, and compare the resulting SHA/CRC descriptors with any independently
  acquired image. This read-only acquisition should precede every live APPLY and
  supplies the exact recovery source image. Canonical:
  `exploit/dumper/README.md`; [historical exploit-engineering journal](../history/2026-08/EXPLOIT_ENGINEERING_2026-08-12.md).
- **Live Gate-2 MAC28 causal proof.** The local hardware-proof harness and the
  exact one-off openpilot ablation are complete. yc's 2026-08-16 external field
  report corroborates the corrected `cmp r0,r26 -> cmp r0,r0` direction on a
  2024 RAV4 Prime, but its forced older profile changes a broader message set and
  is not this causal experiment. What remains is hardware-only: on the same
  EPS/F181 and bus topology, preserve a
  healthy stock baseline, demonstrate that the exact MAC28-only ablation is
  rejected on the identical stock firmware image, then apply the semantically
  resolved Gate-2 patch and demonstrate acceptance with the same ablation
  commit. Preserve SHA-bound raw CAN, EPS DTC, and steering-state evidence for
  all three phases. `validate_trial.py` intentionally rejects flash/reboot
  success as proof. Canonical: `exploit/behavioral_proof/README.md` and
  [../security/secoc/application-chain.md](../security/secoc/application-chain.md).
- **RR versus RL ordering inside protected CAN-FD `0x090`.** Techstream
  `EMPS2_P5` plus the firmware consumer shapes now identify signals 270/273 as
  the protected rear-wheel-speed RR/RL pair and signal 276 as `CAN Steering
  Angle Speed (SSAV)`. The static artifacts do **not** bind signal 270 versus
  273 individually to right versus left. Preserve the pair-level semantic until
  a CAN trace, exact DBC, or independently labeled diagnostic correlation fixes
  the ordering. Canonical: [../communications/application-rx.md](../communications/application-rx.md) §5.4; `secoc_fd_sensor_correlations.json`.
- **Live slot-4 operation permissions.** Static CodeFlash proves slot-4
  verification (command 7). The AUTOSAR SHE spec governs usage by a single
  binary `KEY_USAGE` flag (enc/dec ⊕ MAC-generate+verify; no verify-only
  facility — SECOC-023, CORR-017), so under SHE a MAC-usage slot 4 *permits*
  command-5 generation and would *reject* command 1/3 enc/dec. The remaining
  open question is therefore narrower: does the Renesas ICU-S deviate from SHE
  (a non-standard verify-only restriction, or debug/lifecycle gating)? Bench-test
  command 7 good/bad controls then command 5 after normal application
  initialization; record status, output, latency, jitter, and debug-attached
  behavior. See
  [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md) §1.3.
- **Command 13 vendor semantics.** The SHE spec disproves the normal
  slot-4→`RAM_KEY`→export extraction route (SECOC-025): `CMD_EXPORT_RAM_KEY` is
  `RAM_KEY`-only/plain-only and no nonvolatile KEY has an export or copy command.
  Command-13 opcode identity is therefore moot for standard SHE extraction. Its
  remaining value is narrow: determine whether Renesas implements an undocumented
  deviation in opcode/selector/lifecycle behavior. This is lower priority than
  the live command-5 permission test. See
  [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md).
- **`8965B4514000` runtime object-15 key path.** Vance's external field report
  places a CMAC-validating candidate in the structural object-15 second field
  at `0xFF206E14`, but no `4514000` CodeFlash or runtime trace is public in the
  bounded Stage-8 acquisition corpus. Exact identifier/path/extension searches,
  source/fork/release scans, and the separate Vance English tree still yielded
  no target image. Obtain that image or instrument initialization to distinguish
  direct software CMAC, object-15-to-ICU-S provisioning followed by
  selector/command-7 use, independent hardware-slot provisioning, or mixed use.
  See [../variants/sienna-8965B4514000.md](../variants/sienna-8965B4514000.md)
  and [historical external-reference refresh](../history/2026-08/EXTERNAL_REFERENCE_REFRESH_2026-08-10.md).
- **Same-vehicle `0x344` producer and key storage.** The same `4514000` partner
  key reportedly validates `PRE_COLLISION_2` (`0x344`) `112/113`, while
  `4512000` EPS has no `0x344` receive profile. Identify the physical producer
  by multi-segment capture, candidate-ECU isolation/reset, or candidate firmware
  analysis, then test it as a peer key-recovery target. OpenDBC's inherited
  `DS1`/`DSU` logical node is not physical-source proof; a gateway mirror must
  be excluded.
- **SecOC key uniqueness across vehicles/calibrations.** Collect hash-only
  records with vehicle/sample pseudonym, software ID, region/build, validated
  CAN IDs, match counts, and source. One `4514000` partner observation cannot
  distinguish a per-vehicle key from calibration-, model-, region-, or
  fleet-shared provisioning.
- **Command-7 power/EM leakage.** FD IDs `0x090`/`0x0D7` provide 14 chosen bytes
  in CMAC's first AES block. Run fixed-vs-random leakage detection, establish a
  stable trigger, attempt CPA for key bytes 2..15, and complete the two fixed
  Data-ID-aligned bytes by `2^16` search against multiple stock tags. ICU-S
  masking, byte order, trace count, and attainable SNR are unobserved.
- **Physical power topology.** Confirm the chip marking and measure the actual
  core rail before power analysis or glitching. Renesas lists `R7F701381` as a
  DPS part with VDD pins 11/66/98, while a public same-part-number report
  describes VCL/eVR pins 11/66.
- **Protected-tail serial read.** Determine whether a faulted serial read of
  `0x1007800..0x1007FFF` bypasses only a mask-ROM range check or also exposes
  nonblank ICU-S storage. The current CPU-visible dump contains only `00/FF`;
  public P1M-E fault injection proves ordinary flash readout, not key-array
  access.
- **Bank-0 command-8 production role and safe dynamic confirmation (SECOC-047/048).** Static firmware closes the CAN `0x13..0x1A` assembly and completion-misattribution mechanics. What remains useful is dynamic provenance, not random stimulation: determine whether RID `0x100E`/those CAN IDs occur during legitimate provisioning, whether any external monitor exposes bank-0 terminal state, and whether dealer tooling treats RID `0x1010` status `02` with zero proof as success. Reproduce the race only on a disposable/matching unit with a legitimately captured authenticated update package and complete recovery plan; preserve F181, route, M1–M5 hashes, timing, DTCs, and post-run key state. Do not synthesize command-8 packages on the only original ECU.
- **Application command-5 signing capability — dynamic discriminator only.**
  Stock RoutineControl `31 01 10 0F` now supplies bank-1 activation, and stock
  `0x68B42 -> 0x88350 -> 0x87CCC` supplies selector-4 command-5 plumbing; the
  minimal bench experiment therefore needs no activation hook. SECOC-046 now
  supplies a stock no-SA DTC observation of the terminal negative state
  (`0x00D317`), but that state conflates command failure with full-result mismatch
  and does not expose `FEBE51AA`; direct byte observation remains bounded. For a production-resident signing proxy,
  `0x65750` remains a foreground non-CH0 hook slot; command-7 contention is
  handled by deferring on the shared serialized driver; sender freshness and a
  controlled `0x7F8` bench egress are specified. Remaining questions are
  dynamic: does live slot 4 actually permit command 5, what latency/jitter does
  it have under real command-7 load, and does a provisioned isolated bench
  produce CMACs matching independently known frames? The stimulus harness now
  records per-observation monotonic/wall timestamps and request RTT
  (`command5/stimulus.py`, schema `sienna-command5-app-live-result-v4`), so the
  slot-4 latency/jitter question can be answered from evidence without any new
  mutator. The same harness now records read-only `19 02 FF` snapshots before and
  after stimulation. A second dynamic question is whether a tester can deliberately
  trigger the recovered runtime re-arm chain `0x4F93C -> FEBE508D=0xA5 -> 0x68C0C
  -> 0x67FCE`; static analysis proves the reset path exists but not external control
  of the prerequisite application transition. Production Tx integration
  also requires a new audited route because stock CanIf has no `0x2E4/0x131` Tx
  entry. See
  [../security/secoc/sender-implementation.md](../security/secoc/sender-implementation.md) §5.
- **Object-15 producer.** No static producer exists in this calibration.
  Where a provisioned unit writes object 15 from is unknown (dealer tool path
  hypothesis only).
- **Reset-window replay.** Receiver freshness is zeroed at SecOC initialization,
  so a captured positive synchronization value is structurally forward after
  reset. `exploit/followups/secoc_freshness_trials.py reset-replay` now validates
  the captured sync/protected frames and emits the exact offline phase artifact;
  a cold-boot bench run must still determine sync cadence, whether the old
  authenticated sync can win the startup race, which early ordinary frames can
  then replay, and how quickly legitimate sync closes the window.
- **Tag-guess and saturation rate.** The static profile exposes 28 CMAC bits,
  does not advance freshness on failure, and has no recovered authentication
  failure lockout. `secoc_freshness_trials.py tag-guesses` now creates bounded
  offline candidate sets while preserving payload and transmitted freshness;
  live work still needs command-7 throughput, queue replacement, `0xE07`
  polling latency, watchdog load, legitimate-frame loss, and whether bus error
  behavior makes online guessing or only denial of service practical.
- **Future-sync recovery.** A valid sync can jump arbitrarily forward.
  `secoc_freshness_trials.py future-sync` now rejects non-forward candidates and
  records the already-authenticated candidate/current epochs; verify on a bench
  whether a far-future signed sync blocks lower legitimate epochs until receiver
  reset, whether any external freshness manager repairs it, and which
  diagnostic/status signals expose the desynchronization.
- **FD ignored-suffix behavior.** CAN-FD DLC 48/64 is accepted then clamped to 32.
  `secoc_freshness_trials.py fd-suffix-alias` now constructs exact 48/64-byte
  aliases with an unchanged first 32-byte EPS authenticated view. Confirm whether
  gateways or peer ECUs preserve/interpret the suffix differently; the Sienna
  EPS itself does not pass it to SecOC/COM.

## Variants

- **Sienna `8965B4514000`.** Acquire CodeFlash and completed partner
  dump/capture outputs. Stage 8 re-ran exact public/local acquisition searches
  and found neither, so this remains missing-artifact blocked rather than
  quietly unblocked. The object-15 field and CMAC counts are pinned external
  observations, but runtime crypto architecture, `0x344` EPS direction/owner,
  mismatch clustering, and key uniqueness remain open. See
  [../variants/sienna-8965B4514000.md](../variants/sienna-8965B4514000.md).
- **Corolla `8965F1208000`.** Firmware-static confirmation remains blocked:
  Stage 8 found no public CodeFlash artifact under the exact identifier or
  firmware-shaped path variants. MCU identity, SA implementation/secret
  location, bootloader payload gate, bootloader secrets, and SecOC
  implementation must therefore still be checked against the actual CodeFlash.
  Direct field probing has already established the software IDs, physical
  diagnostic endpoint, responding SIDs, level-`0x03` seed behavior, and
  observed SecOC traffic; do not describe those as unknown. See
  [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md).
- **Separate 2023 US Corolla / tracked `8965H1202000` specimen.** The complete
  memory corpus is now retained. CodeFlash internally identifies
  `8965H1202000/8A3111202000`, `R7F701383`, and serial
  `8965012N50A05G310920`; all three Sienna crypto roots transfer byte-for-byte,
  Gate-2/CRC resolution transfers, and the target's actual queue is exactly
  `00F/D7/B6` with no `2E4/131`. The Toyota-B pin-swap's **physical function is
  also closed statically**: official comma hardware makes CAN0/CAN2 the
  intercept-relay pair, while the affected field pinout put the relevant network
  on unsplit CAN1. Exact H firmware rules out an EPS app→boot controller/ID
  migration and reproduces the asynchronous programming-reset handoff. The
  direct stock-wire diagnostic candidate is therefore `ELM param 1 + bus 1`; it
  is not relay-topology equivalent to the physical repin. Two dynamic boundaries
  remain. First, the exact reason the **indirect OBD route** does not reliably
  survive/observe `10 02` is still gateway/timing/ACK/wakeup territory and cannot
  be selected without gateway firmware or a dual-segment capture. Second, the
  **epoch/key boundary** remains: no raw DataFlash window matches the local
  `0x00F` oracle, CAN capture and dumping are separate jobs, and the older
  public-route `0x116/0x24D` oracle is a different freshness epoch (`TRIP 0xCE9`
  versus local `0xD0D`). The major H-native static transfer questions exposed by
  the first whole-image census are now substantially closed rather than left as
  offset hypotheses. XCP target-native decomp proves the same unauthenticated
  LocalRAM read / shadow-write / E4 CodeFlash-copy architecture with H-specific
  exclusion ranges. SecOC target-native decomp proves the same verification
  algorithm over a different `00F/D7/B6` profile set. Motor-control recovery
  reaches the d/q-to-duty and TSG3 hardware path; the high-level steering pipeline
  is anchored at H `0xCEDAE` and is larger than Sienna's. The corrected H GP/TP
  context and generated COM tables now prove that classic `2E4/131` are absent
  from normal Rx as well as SecOC, that the old `2E4` request staging cell is
  periodically forced to zero, and that FD `0B6` is the new secured control/status
  PDU feeding several stages in `0xCEDAE`; Tx likewise replaces `260/262` with FD
  `030`. The application-diagnostic generation is now independently re-censused as
  well: 17 outer SIDs retain their policy shape, RDBI is 226 DIDs with a distinct
  32-selector stale-response set, and RoutineControl keeps the same 19 policy rows
  while `110A/C/D` become no-op and `110B` becomes an H-only active lifecycle.
  The FD field pass now closes the obvious replacement-command candidates:
  `025` is shared with Sienna and retains the `025 -> 4A3` telemetry join; B6's
  signed16 scalar is staged-only under the complete direct-reference census;
  active B6 fields are gate/mode/sequence/scaling/validity state; and the retained
  Sienna-shaped clamp branch reads zero-fed `AE12`, while internal `AE20` is a
  plausibility/status path. The H-only/reordered `0xCEDAE` stage ledger is now
  complete, and the mapped generated-COM ingress has no H-only/wire-changed scalar
  ≥12 bits; the only changed surviving fields are sub-12-bit B6 supervisory inputs.
  SecOC provenance is also closed at the CPU↔ICU-S boundary: `00F/D7/B6` share
  config/job 0 and protected slot 4, with no raw key in the mapped command-7 CPU
  descriptor and authenticated command 8 as the recovered refresh interface.
  The eight changed high-level `scheduler_system` roles are also now target-native
  recovered (mode-event policy, per-tick wiring, startup/init, reset continuation),
  reducing the genuinely-unresolved matrix residue to 454. The nine changed CAN/COM
  roles are now also target-native recovered. The three changed storage/NvM roles
  are likewise closed: H preserves object-15 exclusion/restore geometry but the
  supplied object-15 copies are invalid. The four changed XCP handlers are also
  target-native closed, preserving the custom selector set and application-side F5
  read semantics with H-specific exclusions. The five changed motor-control roles
  are target-native closed, and the remaining 42 named SecOC/ICU-S roles are now
  closed as a complete target-native surface as well. The current residue is
  **228**, with zero unresolved `scheduler_system`, `can_com`, `storage_nvm`,
  `xcp`, `motor_control`, `secoc_icus`, `crypto`, `steering`, or `diagnostics` entries. All remaining named residue is untagged; the complete 88-function deadline-monitor family is also closed by target-table recensus. Remaining H-static work is the explicit
  residue outside those closed surfaces; generic DAQ/XCP
  callbacks remain optional unless an exploit hypothesis needs them. If revisited
  dynamically, record
  direct F181 plus full-bus and Panda health on both normal-CAN1 and OBD routes
  immediately around the programming transition, then repeat the memory/capture
  epoch join. Route metadata remains forced `TOYOTA_COROLLA_TSS2` with no `carFw`,
  so the route-to-image/model-year join remains contributor attribution. See
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
  and [../tooling/panda-toyota-routing.md](../tooling/panda-toyota-routing.md).
- **TSS 3.0 family breadth.** Which Sienna findings generalize across the
  family (Camry, RAV4, etc.) is unmapped. See
  [../variants/tss3-family-comparison.md](../variants/tss3-family-comparison.md).

## Tooling

- **Semantic coverage.** The current graph has 6,376 structurally discovered
  functions. A reproducible ranked sweep decompiled 100 entries, including all
  mandatory callback/dispatcher families, but 87 selected entries remain
  `reviewed_unknown`; across the whole ledger 6,257 functions remain
  unreviewed and only 32 carry a semantic grade. This is an open semantic
  denominator, not evidence of hidden subsystems. New work should remain
  lead-driven and record an explicit disposition without upgrading successful
  decompilation into semantic confidence. The selection artifact and current
  boundary are in
  [historical corrected-graph re-audit](../history/2026-08/CORRECTED_GRAPH_REAUDIT_2026-08-11.md).
- **RFP/P1M-E serial-protocol transfer.** The generic RV40F **host-side static
  work is closed** (RFP-001..008): all 52 ordinary command IDs are censused,
  both connection/setup variants are recovered, the 8-byte `GetDeviceType`
  capability word and key `0x1106` are decoded, legacy `SetICUM` is bounded to
  its exact 20-byte structural option record, and `CheckICUMode`/payload-free
  `ValidateICU_S` host sequencing is pinned. The remaining question is target
  transfer only: obtain a legitimate R7F701381/P1M-E serial-boot capture (or
  query a bench target) to learn which commands/capabilities its mask ROM
  actually advertises, what target-side transition `ValidateICU_S` causes, and
  whether any manufacturing-only provisioning path exists outside the standard
  RFP distribution. The four `SetICUM` integer fields and three flags lack
  retained human-readable enum names, but further generic host archaeology is
  not justified without a target observation that makes those labels material.
  See [../tooling/renesas-rfp-rv40f.md](../tooling/renesas-rfp-rv40f.md).
- **DID `0x1010` production use and slot-4 package.** Static firmware now
  recovers a SHE-compatible command-8 key-update service behind RoutineControl RID
  `0x1010`; selector `01` starts the 64-byte M1–M3 update and selector `03`
  reads status `01/02/FF` plus M4/M5 on success. Capture a legitimate
  provisioning/rekey session and process it with
  `tools/decode_icus_key_update_trace.py` to determine whether Toyota/Denso
  actually invokes this DID, whether M1 targets slot 4, observed polling
  cadence/deadlines, and which lifecycle preconditions exist beyond the
  recovered extended-session/no-Dcm-SA policy. Techstream V18 MACKey
  Registration is no longer a candidate exact static join: it reads a separate
  16-byte identity from DID `0x1010`, but writes M1–M3 through Routine
  `0x3002`. RFP's `ValidateICU_S` is likewise a separate
  lifecycle-validation operation.
- **MACKey `SafekeyNumber` physical meaning.** Techstream forwards the raw
  16-byte payload of `22 10 10` unchanged and uses it to associate returned
  exchange records with master/slave ECUs. Stage 8 now pins an external official
  rekey observation that Toyota requires both an **MCU ID and VIN** and rejects
  VIN-only requests (TMS-016), independently proving that an MCU identity is a
  required input somewhere in the rekey flow. The Techstream binaries still
  contain no `MCUID` naming/derivation edge and no retained transcript labels
  DID `0x1010` as that value. Resolve the final identity join only from target
  ECU firmware or a labeled legitimate vehicle transcript; do not equate the
  two fields from naming similarity alone.
- **Techstream live-session capture.** `ptshim32.dll`/`ptshim32_0500.dll`
  (TMS-005) can capture a complete Techstream↔EPS J2534 transcript, and the log
  format is no longer a blocker. Both shipped text formats, performance-counter
  timestamps, address/data lines, save modes, and `J2534Ctrl.dll`'s timestamped
  `Techstream\\ErrorReport\\j2534_....log` save path/event handshake are
  statically recovered; `tools/techstream/parse_ptshim_log.py` normalizes both.
  The remaining question is purely dynamic. Capture health check, data list,
  active-test/customization, MACKey Registration, CUW preparation, and reflash
  authorization/programming as six separate labeled operations. In the Data List
  capture, explicitly record `Command Value Torque` (monitor 402),
  `Cooperation Control State` (60), and `Control State Information` (403): the
  static P5 metadata now proves 402 is 16-bit/`Nm`, 60 has the binary
  cooperation-control display, and 403 is 16-bit/unitless, but a live transcript
  is needed to identify their UDS data IDs and compare values/timing against the
  recovered CAN/application states. Then compare SA seed/key exchange, DID reads,
  session transitions, and programming handoff against SEC-BOOT-003,
  SEC-APP-001, and DIAG-APP-001/003. Preserve raw logs
  privately and commit only reviewed/redacted derivatives or hashes. See
  [../tooling/techstream-capture-procedure.md](../tooling/techstream-capture-procedure.md).
- **Sienna EPS CUW route and calibration material.** TMS-004/TMS-007 recover the
  V18 controller's decoded parameter-row factory and the standard/unified
  command builders, but the installation contains no `.cuw` or `.cal` payload.
  Obtain the matching `8965B4512000` payload or a labeled transcript to select
  the exact factory identifier and recover its `ServiceAuthKey`, `ECUAuthKey`,
  `SeedKey`, `Nonce`, `OffsetAddress`, download ranges, data-format fields, and
  routine choices. Firmware support for the same UDS SIDs/DIDs is only a
  bounded compatibility join, not proof of which host builder was selected.
- **RKS authorization vs. EPS reflash (Layer A).** The TIS portal RKS flow
  (TMS-009) is a CUW-side VIN+license permission gate, distinct from the
  cal-file crypto key (Layer B). Open: whether it is *mandatory* for every EPS
  reflash or optional/regional/offline-bypassable. `SeedValue` itself is now
  statically bounded: `CUWAccessRKSWrapper` reads native buffer `+0x78`, and
  `Cuw.exe` serializes a pre-existing **16-byte** native input into 32 uppercase
  hex characters plus NUL with no RNG/time transform in the request-building
  edge. Only the producer of those 16 bytes one indirect controller edge
  upstream remains unknown; resolving it is low priority because Layer A never
  reaches the ECU or any of the three firmware secrets. See
  [../tooling/techstream.md](../tooling/techstream.md) §5.3.
- **MEM-SAFE-001 transfer to newer SecOC/TSK targets.** The partial-AES-block
  raw-write primitive (MEM-SAFE-001) upgrades a prior authenticated payload into
  arbitrary RAM-code execution without repeating CMAC. The exact bounded host
  transactions are now implemented and tested under `exploit/followups/`; the
  remaining question is only whether the same
  bootloader gate structure (4 KiB download window, callback pointer at
  `0xFEBF0FD0`, `payload_decrypt_transfer_task` floor-division block count,
  authorization persistence) exists in a newer target's CodeFlash is the
  decisive check. If it transfers, the primitive provides a repeatable
  code-execution foothold for application-context ICU-S command-5 signing-oracle
  experiments. If the target uses different download window sizes, callback
  offsets, or alignment requirements, the primitive may not apply. See
  [../security/memory-safety-audit.md](../security/memory-safety-audit.md).
- **MEM-SAFE-003 equality-oracle reachability for variant identification.** The
  `0x10F3` byte-compare oracle can read application CodeFlash at
  its two configured ranges without dumping the full image. The re-arm loop,
  range gates, request budget, simulator, and explicit live mode are now
  implemented under `exploit/followups/`. It could be used on a newer
  target to check whether the same crypto routines, SecOC profiles, or callback
  structures are present before attempting a full exploit. The remaining
  unknown is a live timing/reachability measurement; the 256-request worst case
  makes only small known signatures rational. See
  [../security/memory-safety-audit.md](../security/memory-safety-audit.md).
- **Newer-TSK exact target bundle.** No exact target identity currently exists.
  Acquire the part/calibration number plus `F181`, complete CodeFlash and
  DataFlash, matching Techstream/regional DDB set, exact `.cuw`, and the six
  synchronized labeled captures above. Use the redacted manifest schema in
  [../variants/newer-tsk-target-evidence.md](../variants/newer-tsk-target-evidence.md);
  until then every Sienna→newer-TSK transfer remains hypothesis.
- **RoutineControl `1004` hardware-visible event-history rewrite consequence.**
  Static recovery is closed: default-session `31 01 10 04 FF FF` has no recovered
  vehicle-speed gate and repeatably drives operation 5, which waits on persistent
  rewrites of event-log/history objects 17/18/19/20/21/23. No direct
  conditioned-command/d/q/PWM join is recovered. Do not label the routine
  “ClearDTC” without external/dynamic evidence. Dynamic characterization is not
  packaged as a normal probe because it deliberately modifies persistent event
  history; use only a disposable/matching ECU with NVM backup/restore.
- **RoutineControl `1108` hardware-visible persistent-reset consequence.**
  Static recovery is closed: unauthenticated default-session `31 01 11 08` has
  no recovered vehicle-speed gate and repeatedly starts/coalesces queue operation
  2, which resets/reinitializes runtime state and persists checkpoint objects
  9/11/12/14/15 before selector-10 completion. Exact static/live closure has no
  direct conditioned-command/d/q/PWM join. Dynamic characterization is
  deliberately not packaged as a normal probe because the routine modifies
  persistent state; use only a disposable/matching ECU with complete NVM
  backup/restore and recovery procedure.
- **Application WDBI `0204` hardware-visible maintenance/reset consequence.**
  Static recovery is closed: the write transitions/persists checkpoint object 7,
  and one branch then starts queue operation 6, which resets/reinitializes state
  and persists checkpoint objects 9/11/12/14/15 after WDBI completion. No direct
  conditioned-command/d/q/PWM join is recovered. Dynamic characterization is
  deliberately not packaged as a normal bench probe because it modifies
  persistent state; use only a disposable/matching bench with complete NVM
  backup/restore and recovery procedure if the physical effect becomes important.
- **Application WDBI `2012` hardware-visible lifecycle-inhibit consequence.**
  Static recovery now closes the software cone: after the scaled-supply snapshot
  reaches `0x0900`, `2012` suppresses the mode-specific transition block that
  normally performs task-signal clearing / NvM default-reset actions, and it
  also clears an alternate rotor-observer calibration selector. The remaining
  unknown is what observable EPS behavior this inhibit produces on an isolated
  matching bench and how it recovers across session exit/reset. Static closure
  has no direct d/q/PWM join, so do not describe it as steering-current control.
- **Application WDBI `2013/2014` hardware-visible consequence.** Their static
  cones are now closed. Both retain the vehicle-speed plus two-state-flag start
  gate. `2013` reaches motor-worker fields `FEBE6DCA/6DCC` but dead-ends in
  write-only task/RTE mirrors; `2014` changes threshold/mode eligibility and
  participates in RoutineControl `110A/110C` start gating. Neither has a
  recovered direct d/q/PI/PWM join. The remaining question is what observable
  EPS behavior either write produces on an isolated matching bench and how the
  state recovers across diagnostic session exit/reset.
- **Application CommunicationControl live effect.** Static recovery proves that
  extended-session SID `0x28` reaches real communication-mode updates without a
  configured SecurityAccess policy or recovered speed gate. The isolated-bench
  probe is now ready under `exploit/followups/`; run it to determine which
  baseline-active EPS application Tx IDs are suppressed by `28 01 01` and prove
  all recover after `28 00 01`. This is an availability characterization, not a
  candidate steering interface.
- **Exploit-interest cohort consumption (SWEEP-008).** The ranking pipeline
  produces anchored candidate cohorts (`pre_sa_write`, `computed_store`,
  `selector_dispatch`, ...). The first serious cohort and the 2026-08-15
  second batch (highest-ranked unresolved candidates after excluding the
  XCP/RDBI/RMBA/SA/boot-RC families and parallel command-8 work) are
  dispositioned in `data/exploit_interest_reviewed_candidates.csv`; the
  verification gate requires every ingress-reachable top-15 cohort member to
  carry a disposition there. Rank-3 `0x00068368` is now promoted to
  SECOC-047/048 by the parallel bank-0 audit; the other fresh batch-2 reviews
  are bounded negatives or duplicates. Remaining `open` ledger rows: `0x00058404`/`0x0007c7c2`
  (no recovered ingress root) and `0x000539a8` (event-log cluster adjacency
  unverified). Beyond the ledger, the remaining ranked candidates are review
  input, not absence claims.
- **Cross-calibration structural triage of future P1M-E images.** The offline
  structural fingerprint scanner (`tools/analyze_rh850_codeflash_structure.py`)
  now flags boot-CRC geometry, RAM-exec/MEM-SAFE-001 package anchors, and XCP
  `0x7F7/0x7F8` route/command-map constants in arbitrary images. Every match is
  a triage candidate only; whether each mechanism transfers must be verified
  against the new firmware bytes before anything is recorded beyond
  `docs/variants/` hypothesis.
