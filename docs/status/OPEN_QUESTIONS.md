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
  request/angle command, while observing d/q-reference/current/PWM state. For
  tracked Corolla `8965H1202000`, do **not** synthesize those absent Sienna
  profiles. TMS-021 now statically proves the general internal `1C02 Command
  Value Torque` contribution reaches Techstream-visible base Q command `1152`
  and then compensated-command/error/PI state in the closed-loop Q-current path.
  VAR-036/VAR-037/CORR-078 separately close the retained LTA branch as
  direct-write inactive, rule out recovered hidden D7/B6 group/full-PDU commands,
  and classify the only shared command-sized CAN025 fields as steering-angle/rate
  sensor state. The remaining Corolla experiment is therefore genuinely
  external-provenance work:
  during a known stock-LTA interval, capture all real incoming CAN-FD traffic and
  read the H precursor/mode/contributor cells to find a state that moves before
  the autonomous component of the general torque command. If none does, acquire
  the camera/gateway/other steering-controller firmware. Static broad searching
  of this H EPS should not be repeated without a new concrete lead.
  Canonical: [../architecture/control-partition.md](../architecture/control-partition.md) §9.3 ·
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md) §§7.34–7.35.

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
  canary through the complete bench-gated `live_installer.py` workflow. The
  installer now rechecks application F181 and requires SID-`0x23` heartbeat
  progression itself; use a hardware reset plus the existing read-only probe only
  when proving reset-to-stock behavior. Next prove
  one-shot queue capture, then enable COM delivery on an isolated bench. Do not
  resume generic callback/xref searching unless dynamic behavior falsifies a
  specific static assumption. Canonical:
  [../security/ephemeral-secoc-bypass.md](../security/ephemeral-secoc-bypass.md);
  `exploit/ephemeral_runtime/`.
- **Cross-calibration semantic patch resolver validation.** SECOC-045
  rediscovers the Sienna authenticated-delivery gate from a fresh unannotated
  CodeFlash-only import with no target/MAC-result/CRC addresses embedded in the
  resolver, and Span `8965F1208000` has now independently reproduced the same
  semantic resolution against its own persisted image. The next high-value
  validation artifacts are blurbdust-supported `8965F3`/`8965F4` CodeFlash images.
  For F3 the acquisition target is now concrete: Toyota Tundra package
  `T-0035-22.cuw` from TSB `T-SB-0069-22` contains the `8965F3401200/2200`
  images plus the CUW erase routine; the retained community decryptor can emit
  the body/erase plaintext once the package is acquired. Run
  `tools/resolve_secoc_patch_image.sh` unchanged on the recovered CodeFlash and compare its unique semantic
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
  facility — SECOC-023, CORR-017), so under standard SHE a MAC-usage slot 4
  *permits* command-5 generation and would *reject* command 1/3 enc/dec. Renesas
  public P1M material also lists CMAC generation/verification, but SHE-adjacent
  vendor extensions are possible (Vector documents an additional verification-only
  `CMAC USAGE` flag). The remaining open question is therefore target-specific:
  what policy/lifecycle does this provisioned P1M-E slot enforce? Bench-test
  command 7 good/bad controls then command 5 after normal application
  initialization; characterize mode-0 command 1 only with a separate
  `FEBE519A` output observer because the DTC cannot distinguish rejection from
  compare mismatch; record status, output, latency, jitter, and debug-attached
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
- **Application command-5 signing capability — only hardware permission/timing remain dynamic.**
  Stock RoutineControl `31 01 10 0F` still supplies a fixed-16 diagnostic test,
  but SECOC-070 closes the alternate-caller problem: a 546-byte RAM-only runtime
  now invokes serialized dispatcher `0x88350` through clean driver record 0 with
  fixed selector 4 and caller-chosen `0..80` byte length. Its `FEBFFB80..FEBFFBFF`
  mailbox is reachable through the existing no-application-SA XCP read/write
  path; record-0 completion publishes the generated result without the stock
  diagnostic 16-byte comparer. Installation still requires the already-solved
  authenticated bootloader-RAM/MEM-SAFE-001 foothold, but no persistent CodeFlash
  hook or per-request application SecurityAccess is needed. The remaining
  command-5 questions are therefore genuinely dynamic: does live provisioned
  slot 4 accept command 5, what latency/jitter does it have under real command-7
  verification load, and do 7/12/36-byte results match independently known
  CMACs? The runtime retries shared-driver busy rather than aborting command 7.
  Sender freshness remains a separate protocol-state requirement. The older
  stock-bank stimulus remains useful as a low-risk permission/control experiment,
  while `command5/ram_proxy.py` is the variable-length planner / guarded live
  client after the RAM runtime is installed. Production Tx integration still
  requires a new audited route because stock CanIf has no `0x2E4/0x131` Tx entry.
  See
  [../security/secoc/command5-oracle-assessment.md](../security/secoc/command5-oracle-assessment.md) and
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
- **Corolla `8965F1208000`.** Acquisition and broad static comparison are
  closed against the tracked 2026-08-21 Span corpus. F181, all three static
  security roots, normal-Rx/SecOC topology, Sienna transfer, non-CodeFlash
  memory, and the `0xA000` active unit-calibration family are now pinned from
  actual bytes. The low delta is exactly partitioned as 863 changed A000-family
  bytes + 1,311 changed bytes in the structured `0x10000..0x17DEF` shadow source
  + the 16-byte region-0 AES-CMAC tag at `0x17DF0`. The semantic closure is now
  complete (VAR-048/CORR-100): the `0xB022C` seven-pair selector picks the
  low/vehicle bank in every retained capture (high `0x18000..0x1FDEF` = compiled
  fallback/default), Bank B runs live vehicle-speed interpolation over
  conditioned SP1, `0x13E46` feeds the dual-channel plausibility center with
  runtime-confirmed `B33C`, record 8 is the DID `0x010B` torque-sensor
  diagnostic object, and the region-0 CMAC KDF/message are fully recovered.
  Remaining questions are the real vehicle-level lateral-command provenance;
  exact OEM naming where no Techstream join exists (Bank-B map-output
  labels/units, the `0x13E46` coefficient's physical label/unit, the record-8
  inner-u32 subfield); the historical factory/package DID `0x201/0x202` inputs
  of the region-0 CMAC tag (a matching Corolla CUW/calibration package or
  reflash transcript would supply them); per-channel Techstream naming of A000
  records (class corroborated, offsets not mapped); H/Span-specific
  retained-RAM execution geometry if a runtime is built; and live ICU-S policy
  only where hardware evidence is needed. Records 0/2/3 are persistent
  calibration state admitted only after successful reads over byte-identical
  all-zero staging seeds — not differing compiled model-year constants; factory
  vs service origin is not distinguished. See
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
  The retained five-run H FF20-range corpus also adds a storage-quality boundary.
  Official Renesas P1M-E documentation identifies `R7F701383` as a DPS 1-MiB
  device with **32 KiB DataFlash at `FF200000..FF207FFF`**; the upper half of
  Calvin's 64-KiB host profile is outside the specified DataFlash array and must
  not be treated as DataFlash. Across the actual first 32 KiB, the five reads
  differ by 23.5077%-25.6470% pairwise while object validity still repeats
  exactly (0/2/5 valid, object 15 invalid). The same Renesas documentation maps
  both the `FEBE` PE1-local and `FEDE` self-local 128-KiB views while specifying
  only 128 KiB total local RAM, so `FEDE` is an architectural self view rather
  than an additional bank. A direct H `local_ram_self` read would reproduce
  dynamic access behavior, but is no longer required to resolve memory extent.
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
  closed as a complete target-native surface as well. The canonical 1,113-name
  denominator is now **zero genuinely unresolved** after closing the generated
  monitor/adaptor surfaces, application command/async tables, transport/interrupt
  ownership, the clean direct-call provenance graph, and the final 34-name residue.
  The former 96 `structural-candidate-only` rows now all have target-native H
  operand/dataflow inspection evidence, leaving **zero structural-only rows** as
  well. Further H-static work should therefore be driven by concrete semantic,
  exploit, runtime-reachability, or target-architecture questions rather than
  denominator completion;
  generic DAQ/XCP callbacks remain optional unless such a hypothesis needs them. If revisited
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

- **Boot SecurityAccess lifecycle measurement.** The bad-key backoff itself is
  statically closed at **10 seconds**: the second bad `27 02` arms
  `200000000` TAUJ1CNT0 ticks and `27 01` returns NRC `0x37`; TAUJ1CNT0 runs at
  20 MHz from the recovered P1M-E timer configuration. Separately, the ordinary
  application→PROGRAMMING retained replay explicitly clears the initializer
  delay before synthetic boot `10 02`, explaining Calvin's roughly one-second
  successful unlocks. Remaining dynamic value is lifecycle confirmation after
  hard reset / actual bad-key lockout, not the nominal duration. Host tooling
  should request SecurityAccess normally after PROGRAMMING and respect NRC
  `0x37` only when the backoff is actually active.

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
  A 2026-08-21 multi-agent audit adds three cheap pre-capture steps: extract
  the concrete serial mode-entry pattern/baud tuple from the shipped driver
  implementations (`Driver_COM::RunModeEntry`, `Driver_E1E2::RunModeEntry` in
  `libRFP.dylib`, explicitly left un-analyzed by RFP-001..008); fingerprint a
  bench target read-only first (`GetDeviceType 0x38`, `Inquiry 0x00`,
  `GetIDAuth 0x2C`, then protection/option reads `0x21/0x23/0x27/0x2E/0x49`)
  before anything mutating; and, **only as a target-transfer hypothesis**, try
  `CheckIDAuth 0x30` with an all-FF ID as the first authentication probe. The
  shipped RFP docs/configuration contain generic all-FF ID examples/conventions,
  but there is no R7F701381/P1M-E device record proving that blank-ID state for
  this target. Treat acceptance/rejection as an observation, not a prior fact.
  Defer `ValidateICU_S 0x70` and `DisableSerialProgramming 0x29` until their
  silicon effect on P1M-E is observed. See CORR-092.
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
  capture, TMS-027's Sienna observer card should be polled directly:
  `1C02`, `1152`, `1151`, `1156`, companion `1065`, `1154`, `1153`, `1185`,
  and `1155`, with `1185` paired against the separate `0102` speed acquisition.
  Exact scaling, callback provenance, alternate P5 Data IDs, and invalid markers
  are already static facts; the remaining purpose is correlation/support/timing,
  especially the unresolved external-`0x2E4` contribution to the general
  `1C02` command. Also retain `Cooperation Control State` (60) and `Control State
  Information` (403) as lower-confidence vocabulary probes: 60 has the binary
  cooperation-control display while 403 remains 16-bit/unitless. Then compare
  SA seed/key exchange, DID reads,
  session transitions, and programming handoff against SEC-BOOT-003,
  SEC-APP-001, and DIAG-APP-001/003. Preserve raw logs
  privately and commit only reviewed/redacted derivatives or hashes. See
  [../tooling/techstream-capture-procedure.md](../tooling/techstream-capture-procedure.md).
- **Sienna EPS exact CUW row and calibration material.** TMS-029/TMS-032 close
  the complete V18 static route census and both surviving Unified routes at
  body level (RequestDownload grammar incl. hex-decoded `SecurityProperty2`
  bit 3, per-CPU-image/area sequencing, `MakeSendData` verbatim copy, negative
  import census, 17-record wrap-key table with records 1–16 present but not
  proven reachable): 194/196 factory rows have an exact target mismatch and
  only two remain, both pairing `TCUWCanUnifiedPrepareWriter` with either
  `TCUWCanUnifiedFlashWriter` or `TCUWCanUnifiedFlashWriterEachArea`. What is
  still missing is the actual `.cuw`/`.cal` metadata proving which of those
  two Unified rows Toyota selected and supplying `ServiceAuthKey`,
  `ECUAuthKey`, `SeedKey`, `Nonce`, `OffsetAddress`, download ranges,
  per-area choice, and actual target-integrity/header values. Do not promote
  byte compatibility into an exact transcript without that artifact.
- **CUW retry/recovery live attribution.** TMS-030/TMS-031 close the V18 static
  timing tables, retry/reconnect controller, recovery-file schema, and useful
  P5 power-cycle observers. A live session is still needed to identify the
  selected target row and measure its actual SecurityAccess spacing,
  reset/disconnect/reconnect timing, IG OFF/ON behavior, and recovery-state
  transitions. Preserve `Save/RecoveryInfo.ini`, its saved calibration payload,
  raw J2534 timestamps, selected factory/contact/CPU metadata, and Data IDs
  `0016..0019`, `0033/0034/0036`, `0421/0422`, `07D1/07D2`, and
  `26AC/26AD/26C1/26C3`. This is now a capture task, not a static-RE blocker.
- **Matching modern calibration package and target-specific integrity values.**
  TMS-026/TMS-034/TMS-037/TMS-038 close two real legacy specimen families.
  `T-0087-17.cuw` validates the recovered outer CRC/member framing, Format-4
  archive grammar, S-record route, and legacy software-password consumer.
  `T-0011-21 - 04C21.cuw` independently validates a P5-CAN integrated VFOREST
  route and fully closes its `.xxz` transport layer as ASCII-hex `ZV00/ZV01`
  LZF framing, reconstructing the exact 2-MiB logical image. Neither specimen is
  a tracked modern EPS package: the former is SH72544R ENG&ECT; the latter is
  Tacoma ENG&ECT `VFOREST_2_0M` / Denso Gen2-newGen family. What remains still
  needs a **matching modern EPS CUW**: choose between the two byte-compatible
  Unified rows and recover its `ServiceAuthKey`, `ECUAuthKey`, `SeedKey`,
  `Nonce`, `OffsetAddress`, download ranges, area choice, required-spec branch,
  and actual integrity/header values. Other CUW format-tail variants remain
  specimen-bound. The remaining encoded-image questions in the two legacy
  packages concern final ECU/native representation semantics, not ability to
  parse or extract their CUW payload bytes. `DigitalSignature` remains unrelated
  to TIS/RKS `Signature` absent a real dataflow edge.
- **RKS exact target/region policy (Layer A).** TMS-028/TMS-033 close the static
  client completely: state machine, request-field provenance (incl. shipped
  `Ini/RKS.ini` `[ReproKeyRequest]` values), online/offline/import convergence,
  fixed token format, the `IsStored` flag, and the full SeedValue producer
  chain (CentralGW P5-CAN `27 21` seed → callback → ReproKeyRequest; portal
  token returned to the ECU as `27 22 || token[256]`). The shipped client
  explicitly supports continuing without Signature Request when the repair
  manual says it is unnecessary, and no calibration-schema or flash-writer edge
  makes RKS universal. What remains is external policy evidence: determine
  whether a particular EPS calibration/region requires RKS during a legitimate
  GTS+/TIS session, plus the live gateway seed value and the server-side
  signing algorithm/private key — both external to the shipped client, which
  never reaches the ECU security boundary or any firmware secret.
  See [../tooling/techstream.md](../tooling/techstream.md) §5.3.
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
  are bounded negatives or duplicates. The 2026-08-22 static re-audit also
  closed the three formerly `open` rows (`0x00058404`, `0x000539a8`,
  `0x0007c7c2`) with direct firmware bounds, so the reviewed ledger currently
  has zero `open` rows. **That is a ledger statement, not a global coverage
  statement**: ranked functions and cross-function compositions outside the
  manually consumed cohorts remain valid review input and are not absence
  claims (CORR-101).
- **Cross-calibration structural triage of future P1M-E images.** The offline
  structural fingerprint scanner (`tools/analyze_rh850_codeflash_structure.py`)
  now flags boot-CRC geometry, RAM-exec/MEM-SAFE-001 package anchors, and XCP
  `0x7F7/0x7F8` route/command-map constants in arbitrary images. Every match is
  a triage candidate only; whether each mechanism transfers must be verified
  against the new firmware bytes before anything is recorded beyond
  `docs/variants/` hypothesis.
