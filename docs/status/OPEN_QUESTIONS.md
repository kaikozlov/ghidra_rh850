# Open questions

Exhaustive unresolved-question ledger. **This is not the execution queue**; for
what to work on next, start with [PRIORITIES.md](PRIORITIES.md).

Each question carries a stable address (e.g. `OQ-004`). Use it when linking a
lead from findings, reports, PRIORITIES, or commit messages; the generated
[../reference/index.md](../reference/index.md) resolves every OQ to its related
findings/corrections and owning gate suites. IDs are stable: resolved questions
leave this file (their result moves to
[FINDINGS.md](FINDINGS.md)), and new questions take the next free number.

Once resolved, a question leaves this file, the result moves to
[FINDINGS.md](FINDINGS.md) (with its evidence grade), and any superseded prior
claim moves to [CORRECTIONS.md](CORRECTIONS.md).

## Bootloader

- **OQ-001 — Bootloader DID `0203` semantics.** It ignores its five bytes and only arms
  state 0 → 1. Whether any field ever carried meaning in other calibrations is
  unknown.

## Application

- **OQ-002 — `0xAB` event-record naming.** The configured graph is closed and its
  list/per-ID/detail structure is recovered, but the OEM service name and exact
  meanings of the event catalogue's encoded upper ID bits and record-kind
  values remain unknown.
- **OQ-003 — Live confirmation of the RDBI stale-response disclosure.** Firmware-static
  analysis proves that DIDs `1CF4..1CFF` and `1D01..1D03` return 45 bytes that
  their success-stub producers never write, sourced from persistent Dcm buffer
  `FEBE59F8`. On an isolated Sienna `8965B4512000` bench, run the default-safe
  `exploit/followups/application_rdbi_stale_probe.py`: its discriminator seeds
  the buffer with a 47-byte SID-`0x23` read and requires `22 1C F4` to equal
  `62 1C F4 ‖ seed[2:47]`. Preserve F181, route, and raw request/response bytes.
- **OQ-004 — XCP physical reachability; dynamic-only write consumers.** COM-005 proves
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
- **OQ-005 — Dynamic authenticated-command actuation discriminator.** If COM-007's
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
  VAR-014/VAR-017/VAR-036/CORR-107 now close the receiver-side Corolla command
  model positively. GP-relative `B8EEC` copies B6 signal255 staging
  `FEBEF1CC -> FEBEAE82`; `C9DB0/C9E54` form target state; `CBD7E/CB096`
  independently reconstruct measured angle from FD `0x025`; and `CA138` applies
  the same gain before forming target-minus-measured error. The result reaches
  `C2A8`, general `1C02 Command Value Torque`, and the Q-current command under
  recovered gates. B6 signal254 is the companion 6-bit mode/control ID and
  signals262/263 percentage-modulate internal contributors. D7/B6 group/full-PDU
  alternatives remain closed and the shared large CAN025 fields remain sensor
  state. The physical scale is now closed statically as well: H carries FD025
  signal184 unchanged into DID `0x1037 Steering Angle`; Techstream physical key 3
  makes it 1.5 deg/count, signed4 signal185 supplies a 0.1-deg fraction, and the
  matched H controller makes B6 signal255 `1024/17870 deg/count`
  (`~1.000121519 mrad/count`) controller-equivalent. Receiver-side request/loss/
  sequence semantics are now closed too: Techstream's `Target Lateral ID` defines
  `0=No Request` and labels active signal254 IDs `1/4/10/11/19` as
  `PCS/LDA/Hands Off LTA/LTA-LCA/PDA`; PDU42 reloads to **7 TAUJ0-CH3 foreground
  ticks** and first expiry disables cooperative selection through slot18/`ADB9`;
  signal261 is a modulo-64 sequence counter with effective-gap cap `8`. TMS-053 now
  closes the timer domain too: H starts CH3 with `(400000+8000)-1` for a one-time
  **5.1 ms** first interval and then reloads `400000-1` for a steady **5.0 ms**
  foreground tick, making the primary B6 loss cutoff nominally **35 ms**. Span's
  moving `0x030` traffic independently corroborates two ticks at 10.000012 ms mean.
  The receiver-side 32-byte envelope is now
  separately exhausted: B0..B27 are authenticated application data, B28..B31 are
  exact FV4+CMAC28, full freshness is `trip16||reset20||message8||reset_low2||00b`,
  and the CMAC input is `00 B6 || B0..B27 || freshness[6]` through ICU-S slot 4.
  The bounded application census finds recovered semantics only in selected B3..B10
  bits. SECOC-071 now also closes the receiver-side SecOC policy behind that envelope:
  B6 is normal freshness slot1; reset candidates are tried `current,-1,+1,-2,+2` with
  the one same-PDU retry resolving the `±2` modulo-4 ambiguity; same-epoch message8
  reconstruction accepts the next congruent forward value (+1..+4); `0x24` still
  proceeds to CMAC; authenticated trip wrap clears linked B6 state; command7 result0
  commits pending freshness before normal verified PDU42 delivery; and application
  signal261 is a separate modulo-64 counter. CORR-111 adds the bounded exception:
  verification failure never commits freshness, but hard-freshness failure or
  retry-exhausted CMAC mismatch can still be forwarded to COM while `FEBE5408 < 204`
  or a separate global D2 override is active. SECOC-072 now
  closes the Sienna-transfer boundary too: Sienna and H/F share the same generated
  `00F` sync/wrap algorithm, ordinary FV46/FV4 arithmetic, MAC28 domain/trailer
  construction, stage-before-CMAC/commit-after-match discipline, and ICU-S command7
  slot-selector machinery. What does **not** transfer by number is equally important:
  shared D7 moves from Sienna freshness ID6/ordinary slot4 to H/F ID1/slot0, and B6 is
  H/F ID2/slot1; RAM addresses/profile counts are regenerated, and the same slot-4
  selector does not prove the same provisioned secret. SECOC-073 now closes the global
  sender freshness state visible on the wire: `0x00F` is exactly trip16/reset20 + MAC28,
  reset advances at a nominal 300 ms state cadence, and exact-H reset/message arithmetic
  replays every retained D7 frame including the `current-1` rollover overlap. A strictly
  newer authenticated sync epoch can therefore re-anchor a replacement B6 message8
  without knowing its previous high bits; D7's own message8 remains independent.
  TMS-053 closes the replacement-side state machine from that point: an exclusive
  replacement sender can own B6 message8 locally, advance normally inside the +1..+4
  receiver window, keep application signal261 separate, and after sender restart wait
  for the next authenticated `0x00F` epoch instead of guessing or persisting Toyota's
  prior B6 message8. The remaining Corolla work is therefore **stock** sender wall-clock
  cadence/secondary-field template, the slot-4 secret value or an available approved
  MAC operation, stock-source suppression, and the upstream payload/SecOC producer
  contract. Static broad searching
  of this H EPS should not be repeated without a new concrete lead.
  TMS-040/041 close the `FRC_P5` diagnostic domain and fixed-routine probe surface;
  TMS-043 now closes the **module-dependency topology**: Corolla P5 installs
  category 498 `FRC_P5`, category 435 **`ABS_P5` = Brake/EPB**, and category 405
  `EMPS_P5`; FRC records X216E `Front Recognition Camera => BRK Communication
  Invalid`, ABS monitors EPS communication, and exact H maps protected-B6 loss
  to U012987 Brake System Control Module. `ABS_P5` also exposes DID `0x107E ADS
  Control EPS Pinion Angle2` at signed 0.00025 rad/count, a conversion shared by
  the brake-family P5 diagnostic databases. This does **not** close payload
  forwarding: FRC also has a direct EPS missing-message dependency and both FRC
  and ABS reference an Automated Driving System Interface module. The unresolved
  task is firmware/dynamic: acquire decoded `FRC_P5` plus category-435 `ABS_P5`
  firmware or synchronized stock-LTA traffic and join planner state to B6 bytes,
  **stock** sender cadence/secondary-field behavior, signing ownership, and stock-source
  suppression. Replacement message8 re-anchoring/progression is already closed and
  does not require producer-policy recovery. Global `00F` trip/reset ownership is now externally observable and no
  longer part of this blocker. Receiver freshness/trailer reconstruction, candidate-window/retry
  policy, command7 result handling, commit timing, authenticated trip-wrap behavior,
  signal261 separation, and ICU-S slot selection are no longer open; the slot-4 key
  value remains unknown. The read-only `AB/EB`
  Operation FFD surface plus fixed routine
  `0x1588` remain capture references. Wire arbitration ID for the FRC/Brake leg,
  exact producer/forwarder identity, and any relation to community
  `NEW_MSG_8A_LAT_CONTROL` (`0x18A`) remain unproved. TMS-051 now exhausts the
  current-corpus sender-attribution branch: exact H U012987 plus the shared D7/B6
  Brake source label, Corolla category-435 `ABS_P5 = Brake/EPB`, and common H
  SecOC config0/ICU-S slot4 across `00F/D7/B6` identify the **immediate
  authenticated B6 source family** as Brake System Control / category-435
  Brake/EPB. They do not identify the unique upstream target originator or prove
  that category 435 executes CMAC/freshness generation. The six local `0792` FRC
  CUWs are opaque/high-entropy ReproMethod07 stored images and there is still no
  `07B0` Brake application, so Tx-descriptor/SecOC-call literal searches cannot be
  performed against decoded producer code. FRC/ABS expose no named producer-side
  Target-Lateral/Target-Steering monitor; the exact request-ID dictionary remains
  on the EMPS observer side. ADS DDR target-angle/angle-speed snapshots are signed
  32-bit rad/rad-s values with unity numeric conversion, while Brake DID `107E` is
  a separate `0.00025 rad/count` observer; neither has a proved B6 dataflow join.
  TMS-052 narrows that acquisition: raw `T-0058-23`/`T-0060-23` already match
  Toyota 23TC01's 2023-Corolla `8646F1204300/4400→8646F1204500` FRC family,
  while Toyota 24TC01 publishes the candidate Brake/EPB family
  `F152612A5100/5200/5300→F152612A5400`; none of those Brake CIDs and no `07B0`
  package is present locally. The next static evidence is therefore specifically
  a decoded/exact-target `07B0` Brake application plus a decoder/exact identity
  join for the already-owned `0792` family (or synchronized stock-LTA traffic),
  not another broad FRC-package search.
  TMS-044 also closes the category-435 Techstream Active-Test catalog as a
  normal steering-writer lead: 20 direct tests and four routines are brake-actuator-
  only, and every routine has zero variable command/mask/button payloads. Those tests
  remain useful as actuator probes, but they are not the missing B6 setpoint writer.
  TMS-045 makes the firmware acquisition blocker exact: the category-435 P5 VDS
  request address is `7B0` in NA/EU/JP, legacy SUW independently maps VSC/ABS/ECB
  to `7B0`, and modern Unified routing takes CAN IDs from the package CAN-ID table.
  The complete current 26-package `software/Techstream/cuw` inventory has six `0792` FRC
  and three `07A1` EPS packages but no `07B0` package. Obtain a true-TSS3 CUW
  whose `Node01/DiagID=07B0`; local absence does not imply Toyota/TIS absence.
  TMS-046 closes the second VDS token as Toyota's exact `FuncAddress=7E5`; TMS-047
  then closes the category-435 diagnostic CID reader itself. Brake/EPB role 82
  `GetCID_SID22_SAS_DT.dll` resolves selector `0xDC` to `22 F1 81`, mask `FF FF FF`,
  expected `62 F1 81`, and parses the post-prefix response into 16-byte `CID1`,
  `CID2`, … entries. The remaining acquisition unknown is therefore only the
  **actual category-435 current software/calibration identity value and package**:
  read F181 at physical `7B0` on the target, preserve the `22 01 05` ECU-part
  number and VIN, then run/record the Toyota ECU Supply Change lookup. TMS-048
  proves `SearchCal.dll` is local-only; TMS-049 closes the real remote handoff and
  proves the uploaded search XML uses F181's 16-byte records as `baseSwNo` values
  while `0105` supplies `ecuAssyNo`. TMS-050 closes the returned-result client
  policy: Techstream parses `systemAssyInfo` and per-ECU `selectSwInfo`, resolves
  selected software to server `swId`/`fileName`, filters targets already present
  as local `*.cuw`, then emits the missing subset as get-cal
  `swNo`/`fileName`/`swType` before URL polling and managed download. In that
  path `swNo` is the selected server `swId`, not `systemAssyNo`. The unresolved
  external facts are the **actual Brake F181/0105 values, the live `resData`, and
  whether Toyota's service returns the desired `07B0` package for that VIN**.
  The FRC-only `1FFF` SWIN path remains unrelated.
  Canonical: [../architecture/control-partition.md](../architecture/control-partition.md) §9.3 ·
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md) §§7.34–7.35.

## SecOC

- **OQ-006 — Cross-calibration ephemeral runtime transfer.** The Sienna fresh-import
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

- **OQ-007 — Ephemeral scheduler-bridge hardware validation.** ARCH-013/014 and
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
- **OQ-008 — Cross-calibration semantic patch resolver validation.** SECOC-045
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
- **OQ-009 — First live run of the generic read-only CodeFlash acquisition path.** The
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
- **OQ-010 — Live Gate-2 MAC28 causal proof.** The local hardware-proof harness and the
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
- **OQ-011 — RR versus RL ordering inside protected CAN-FD `0x090`.** Techstream
  `EMPS2_P5` plus the firmware consumer shapes now identify signals 270/273 as
  the protected rear-wheel-speed RR/RL pair and signal 276 as `CAN Steering
  Angle Speed (SSAV)`. The static artifacts do **not** bind signal 270 versus
  273 individually to right versus left. Preserve the pair-level semantic until
  a CAN trace, exact DBC, or independently labeled diagnostic correlation fixes
  the ordering. Canonical: [../communications/application-rx.md](../communications/application-rx.md) §5.4; `secoc_fd_sensor_correlations.json`.
- **OQ-012 — Live slot-4 operation permissions.** Static CodeFlash proves slot-4
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
- **OQ-013 — Command 13 vendor semantics.** The SHE spec disproves the normal
  slot-4→`RAM_KEY`→export extraction route (SECOC-025): `CMD_EXPORT_RAM_KEY` is
  `RAM_KEY`-only/plain-only and no nonvolatile KEY has an export or copy command.
  Command-13 opcode identity is therefore moot for standard SHE extraction. Its
  remaining value is narrow: determine whether Renesas implements an undocumented
  deviation in opcode/selector/lifecycle behavior. This is lower priority than
  the live command-5 permission test. See
  [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md).
- **OQ-014 — `8965B4514000` runtime object-15 key path.** Vance's external field report
  places a CMAC-validating candidate in the structural object-15 second field
  at `0xFF206E14`, but no `4514000` CodeFlash or runtime trace is public in the
  bounded Stage-8 acquisition corpus. Exact identifier/path/extension searches,
  source/fork/release scans, and the separate Vance English tree still yielded
  no target image. Obtain that image or instrument initialization to distinguish
  direct software CMAC, object-15-to-ICU-S provisioning followed by
  selector/command-7 use, independent hardware-slot provisioning, or mixed use.
  See [../variants/sienna-8965B4514000.md](../variants/sienna-8965B4514000.md)
  and [historical external-reference refresh](../history/2026-08/EXTERNAL_REFERENCE_REFRESH_2026-08-10.md).
- **OQ-015 — Same-vehicle `0x344` producer and key storage.** The same `4514000` partner
  key reportedly validates `PRE_COLLISION_2` (`0x344`) `112/113`, while
  `4512000` EPS has no `0x344` receive profile. Identify the physical producer
  by multi-segment capture, candidate-ECU isolation/reset, or candidate firmware
  analysis, then test it as a peer key-recovery target. OpenDBC's inherited
  `DS1`/`DSU` logical node is not physical-source proof; a gateway mirror must
  be excluded.
- **OQ-016 — SecOC key uniqueness across vehicles/calibrations.** Collect hash-only
  records with vehicle/sample pseudonym, software ID, region/build, validated
  CAN IDs, match counts, and source. One `4514000` partner observation cannot
  distinguish a per-vehicle key from calibration-, model-, region-, or
  fleet-shared provisioning.
- **OQ-017 — Command-7 power/EM leakage.** FD IDs `0x090`/`0x0D7` provide 14 chosen bytes
  in CMAC's first AES block. Run fixed-vs-random leakage detection, establish a
  stable trigger, attempt CPA for key bytes 2..15, and complete the two fixed
  Data-ID-aligned bytes by `2^16` search against multiple stock tags. ICU-S
  masking, byte order, trace count, and attainable SNR are unobserved.
- **OQ-018 — Physical power topology.** Confirm the chip marking and measure the actual
  core rail before power analysis or glitching. Renesas lists `R7F701381` as a
  DPS part with VDD pins 11/66/98, while a public same-part-number report
  describes VCL/eVR pins 11/66.
- **OQ-019 — Protected-tail serial read.** Determine whether a faulted serial read of
  `0x1007800..0x1007FFF` bypasses only a mask-ROM range check or also exposes
  nonblank ICU-S storage. The current CPU-visible dump contains only `00/FF`;
  public P1M-E fault injection proves ordinary flash readout, not key-array
  access.
- **OQ-020 — Bank-0 command-8 production role and safe dynamic confirmation (SECOC-047/048).** Static firmware closes the CAN `0x13..0x1A` assembly and completion-misattribution mechanics. What remains useful is dynamic provenance, not random stimulation: determine whether RID `0x100E`/those CAN IDs occur during legitimate provisioning, whether any external monitor exposes bank-0 terminal state, and whether dealer tooling treats RID `0x1010` status `02` with zero proof as success. Reproduce the race only on a disposable/matching unit with a legitimately captured authenticated update package and complete recovery plan; preserve F181, route, M1–M5 hashes, timing, DTCs, and post-run key state. Do not synthesize command-8 packages on the only original ECU.
- **OQ-021 — Application command-5 signing capability — static H/F carrier candidate closed; live retention/permission/timing remain dynamic.**
  Stock RoutineControl `31 01 10 0F` still supplies a fixed-16 diagnostic test,
  and SECOC-070 closes the generic alternate-caller problem on Sienna with the
  546-byte variable-length proxy. TMS-053 then proved that exact H/F record0 /
  dispatcher / prepare / lower-engine software accepts the 36-byte B6 domain but
  that Sienna's full retained-page geometry cannot be copied. TMS-054 now closes
  the next static step: exact H has a **464-byte** candidate carrier at
  `FEBF0000..FEBF01CF`, the first recovered normalized direct/simple-GP reference
  is exactly `FEBF01D0`, and MPU region 5 (`FEBEF400..FEBF33FC`) assigns
  supervisor R/W/X `0xB8` in both recovered application contexts. The relevant
  startup/MPU/command-5 ranges are byte-identical on F. A separate
  `FEBFFB80..FEBFFBBB` 60-byte mailbox/observation window has zero recovered
  normalized direct references and begins above the startup shadow-copy end.

  Two target-native executables are now audited: a **332-byte** inert canary and
  a **462-byte** fixed-36-byte command-5 proxy, both entry-zero and relocation-
  free. The proxy leaves **2 bytes** of carrier headroom, uses H/F dispatcher
  `0x82750`, record 0, selector 4, and completion cells `FEBF1280/FEBF1281`, and
  retries shared-driver busy without aborting command 7. The current audited proxy
  also self-initializes `request_state=0` after stock final init/before `ei`, samples
  the adjacent done/status cells as one halfword, and mirrors terminal status into
  host-readable mailbox byte `FEBFFB81`; the host therefore no longer depends on
  preserving a preinitialized mailbox across the programming transition. The canary
  never invokes command 5 and exposes heartbeat at `FEBFFB80`.

  Albino's August-18 range-dump acquisition already demonstrated that the H/F
  authenticated boot-RAM architecture works on this physical specimen. VAR-049
  adds a cleaner same-car replay with direct F181 binding and exact zero-0201/0202
  state: boot SecurityAccess succeeds, `0x10F0` authenticates a `FEBF0000` envelope,
  and read-only shellcode returns a valid stream. Optional reconstruction of the
  pinned telescope payload also matches live `DCRA1CIN` and the live CMAC tag.
  None of that proves the candidate `FEBF0000..FEBF01CF` bytes survive the
  boot-to-application transition, because telescope resets after its own payload.

  The remaining questions are now strictly dynamic. First prove **live retention**
  and scheduler health with the inert canary, including heartbeat progression and
  reset-to-stock behavior. Only then use the guarded
  `corolla_hf_direct_command5.py` second stage (successful canary result + explicit
  reset confirmation required) to test whether provisioned slot 4 accepts command 5;
  the tool performs no steering-CAN transmission and requires status-zero plus a
  16-byte non-sentinel mailbox result. Then establish whether outputs agree with
  independent CMAC vectors,
  and what completion latency/jitter looks like under ordinary command-7
  verification load. `data/variant_ram_exec_requirements.json` deliberately still
  has no verified H/F row because the static reference census cannot exclude
  arbitrary computed aliases, DMA/hardware writers, or live lifetime conflicts.
  The existing Sienna `live_installer.py` is therefore not silently generalized
  to H/F. Production H/F B6 Tx still requires those dynamic results or another
  approved MAC path, plus the separately tracked stock-sender/suppression work.
  See
  [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md) and
  [../security/secoc/sender-implementation.md](../security/secoc/sender-implementation.md) §5.
- **OQ-022 — Object-15 producer.** No static producer exists in this calibration.
  Where a provisioned unit writes object 15 from is unknown (dealer tool path
  hypothesis only).
- **OQ-023 — Reset-window replay.** Receiver freshness is zeroed at SecOC initialization,
  so a captured positive synchronization value is structurally forward after
  reset. `exploit/followups/secoc_freshness_trials.py reset-replay` now validates
  the captured sync/protected frames and emits the exact offline phase artifact;
  a cold-boot bench run must still determine sync cadence, whether the old
  authenticated sync can win the startup race, which early ordinary frames can
  then replay, and how quickly legitimate sync closes the window.
- **OQ-024 — Tag-guess and saturation rate.** The static profile exposes 28 CMAC bits,
  does not advance freshness on failure, and has no recovered authentication
  failure lockout. `secoc_freshness_trials.py tag-guesses` now creates bounded
  offline candidate sets while preserving payload and transmitted freshness;
  live work still needs command-7 throughput, queue replacement, `0xE07`
  polling latency, watchdog load, legitimate-frame loss, and whether bus error
  behavior makes online guessing or only denial of service practical.
- **OQ-025 — Future-sync recovery.** A valid sync can jump arbitrarily forward.
  `secoc_freshness_trials.py future-sync` now rejects non-forward candidates and
  records the already-authenticated candidate/current epochs; verify on a bench
  whether a far-future signed sync blocks lower legitimate epochs until receiver
  reset, whether any external freshness manager repairs it, and which
  diagnostic/status signals expose the desynchronization.
- **OQ-026 — FD ignored-suffix behavior.** CAN-FD DLC 48/64 is accepted then clamped to 32.
  `secoc_freshness_trials.py fd-suffix-alias` now constructs exact 48/64-byte
  aliases with an unchanged first 32-byte EPS authenticated view. Confirm whether
  gateways or peer ECUs preserve/interpret the suffix differently; the Sienna
  EPS itself does not pass it to SecOC/COM.

## Variants

- **OQ-027 — Sienna `8965B4514000`.** Acquire CodeFlash and completed partner
  dump/capture outputs. Stage 8 re-ran exact public/local acquisition searches
  and found neither, so this remains missing-artifact blocked rather than
  quietly unblocked. The object-15 field and CMAC counts are pinned external
  observations, but runtime crypto architecture, `0x344` EPS direction/owner,
  mismatch clustering, and key uniqueness remain open. See
  [../variants/sienna-8965B4514000.md](../variants/sienna-8965B4514000.md).
- **OQ-028 — Corolla `8965F1208000`.** Acquisition and broad static comparison are
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
- **OQ-029 — Separate 2023 US Corolla / historical-`8965H1202000` corpus.** The complete
  memory corpus and same-car telescope probe are now retained. Direct application
  F181 is `8965F1208000/8A3111202000`; `8965H1202000 @0x17D80` is the
  separate one-record DID `0x2032` identity retained in historical corpus naming.
  Live PRDNAME is `R7F701383`, the retained unit serial is
  `8965012N50A05G310920`, and all three Sienna crypto roots transfer byte-for-byte,
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
  The corrected FD/fixed-map pass now closes the replacement-command question
  positively: `025` is shared measured-angle/rate state, while protected B6
  signal255 is signed16 target steering angle via `7D94 -> F1CC -> AE82`, and
  signal254 is the 6-bit cooperative mode/control ID via `7D96 -> F127 -> ADB0`.
  The H-only/reordered `0xCEDAE` stage ledger is complete, and the corrected
  generated-COM ingress census finds signal255 as the sole H-only/wire-changed
  field ≥12 bits in the mapped command cone. The separate retained Sienna-shaped
  torque-clamp branch still reads zero-fed `AE12`, while internal `AE20` remains
  a plausibility/status path; those facts do not contradict the distinct B6
  target-angle controller.
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
  generic DAQ/XCP callbacks remain optional unless such a hypothesis needs them. The
  direct F181 is now closed by VAR-049; boot-RAM execution was already established by
  the earlier range-dump acquisition and is now independently replayed/payload-bound by VAR-049. If revisited
  dynamically, record full-bus and Panda health on both normal-CAN1 and OBD routes
  immediately around the programming transition, then repeat the memory/capture
  epoch join. Route metadata remains forced `TOYOTA_COROLLA_TSS2` with no `carFw`,
  so the route-to-image/model-year join remains contributor attribution. See
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
  and [../tooling/panda-toyota-routing.md](../tooling/panda-toyota-routing.md).
- **OQ-030 — TSS 3.0 family breadth and generation control contract.** TSS
  generation and SecOC/TSK remain explicitly separate axes (CORR-108). TMS-079 now
  closes the **host-side fleet architecture breadth** that used to be repeatedly
  re-derived: current GTS+ category-498 `FRC_P5` spans 256/460/213 NA/EU/JP install
  rows, 51/93/70 model names, and 5/9/9 selected architecture patterns. Category
  499 `Steering Actuator` is present in only 4/256, 9/460, and 12/213 of those rows,
  so it is not intrinsic to the TSS3/FRC_P5 generation. That does not collapse the
  target-native work: each architecture still needs its own command/feedback,
  producer/route, suppression, limits/faults, UI and authentication proof. COM-013
  now combines three vehicle-level oracles with exact H/F firmware. The public
  2023 route preserves substantial old-state structure but lacks `carFw`; Span's
  July-29 driving rlog independently exercises motion, brake/gas/steering and
  restores `0x127/8` as a strong carrier reuse candidate (3,662/3,662 valid Toyota
  checksums, raw value `3`, prior-art-compatible with D) while its embedded
  `carParams=MOCK` provides no independent gear-state oracle and its different dongle
  prevents an exact `8965F1208000` identity join. All 599 Span Panda-state
  samples are `ELM327 param=1`; that is direct observation of the normal unsplit
  harness CAN1 path. Span had not physically repinned Toyota-B CAN0/CAN1, so the
  capture cannot establish relay-side producer ownership or stock suppression,
  but the lack of repin does not itself make CAN1 traffic invisible. B6 remains
  absent in this no-stock-LTA-transition segment and is therefore only a bounded
  negative. The public route, old Span static capture, and moving Span rlog all
  preserve the same 22-ID/DLC ADAS-FD geometry. COM-014 now closes the **candidate
  H/F Panda numeric envelope** independently of a new capture: ID11-only candidate
  active control, ±1745 raw (~100 deg) target, strict candidate +1 modulo64 sequence
  with <=78-raw (~4.47 deg) target step, 7-foreground-tick EPS loss cutoff, and raw
  `0x025` steering-rate cutout 100. COM-015 further closes the firmware/calibration
  limit families: selected-bank LTA slew is 7 doubled-domain units per steering task
  (high/default 4), the hard ±1745 ceiling has no recovered speed-dependent reduction,
  and the runtime-selected `CBFCE` compensation maps are zero-valued at every real
  point. The physical driver-torque path's ~±8.238 N.m acquisition clamp and ±10 N.m
  telemetry saturation are explicitly **not** override thresholds. TMS-053 expands
  the physical torque census beyond the earlier exact-symbol pass: 13 direct
  named/fixed-GP source/snapshot references are recovered and **zero** occur in the
  C8xxx–CExxx target-to-motor control cone. Under that explicit static boundary,
  there is no Toyota physical driver-torque comparator left to recover; the numeric
  driver-override threshold is a conservative Panda/openpilot policy to choose and
  validate dynamically. Measured `0x4A3` Q-current is observable, but no
  cooperative-supervisor measured-Q comparator is recovered; any actuator-response
  limit is likewise a future Panda/sender policy rather than an OEM threshold still
  waiting to be copied. TMS-058 now closes the extended **static** `0x394`
  mapping: 242 populated-class DEM events are exhaustively partitioned into the
  native class/state families, named Toyota DTC families are joined where present,
  and the class-2/class-4 paired states have exact 200/600-count aging structure.
  TMS-059 additionally closes `0x030 B6[1]` to a Q-axis-current-derived detector
  (calibration-disabled on exact H) and the `0x351` force-7 source topology. What
  remains is operational policy: Ready=0 plus recoverable/latched fault transitions
  are still required before assigning openpilot temporary/permanent classes.
  COM-016 now closes **receiver-side competing-B6 arbitration**: there is no recovered
  sender identity or Target-Lateral-ID priority; one pending SecOC slot coalesces
  arrivals, in-flight arrivals are ignored, one shared freshness state rejects replay
  but can be advanced by any future-valid slot4-capable sender, and signal261 delta0 is
  tolerated rather than used as a duplicate filter. CORR-111 further closes a bounded
  generated fail-open mode: B6 verification failures can still reach COM without
  freshness commit while `FEBE5408 < 204` or a separate global D2 override is active.
  Deterministic lateral authority therefore requires exclusive B6 control. TMS-053
  additionally closes the exact H steady TAUJ0-CH3 period at **5.0 ms** (one initial
  5.1-ms interval), so the seven-tick primary loss cutoff is nominally **35 ms**;
  Span `0x030` timing corroborates the same period. It also closes the replacement
  sender's freshness restart/progression recipe: re-anchor only on a newer
  authenticated `0x00F` epoch, own B6 message8 locally, keep signal261 independent,
  and wait for the next epoch after restart instead of guessing/persisting Toyota's
  message8. The remaining suppression question is physical/deployment-specific:
  identify the producer side and validate the relay-side isolation point; do not use
  freshness racing as coexistence. **Stock** sender template/cadence, slot4 MAC
  capability/key policy or an audited H/F signer route, and that physical suppression
  implementation remain deployment blockers. COM-017 independently narrows the **non-steering engagement
  state**: exact H receives `0x51E B0[7]` as the source of DID `0x1033 Ready Status`,
  both retained operational routes show Ready=1, and Span observes checksum-valid `0x127`
  raw `3`, compatible with the retained prior-art D enum but not independently gear-oracled;
  target-native D semantics and P/R/N/B remain transition-gated. `0x176 B0[3]` strongly
  tracks accelerator/brake context and is therefore not justified as a cruise-main/engaged
  replacement from these captures; without an independent cruise oracle it is not
  categorically disproved as every possible cruise-related meaning. FRC_P5 Data IDs
  `1905/1906/1914/1901/1912` provide exact OEM
  permission/main/operation/set-speed/interval correlation oracles. Current GTS+ now
  proves direct `22 19 05/06/14/01/12` RDBI requests; require the matching `62 19 xx`
  prefix in independent tooling. The outer diagnostic-session prerequisite remains
  bounded. The next decisive
  Corolla discriminator is therefore a **firmware-identified H/F-family capture with the
  target network physically repinned onto the CAN0/CAN2 relay pair and stock LTA
  exercised off→active→off**, with `carFw`/F181 preserved; also exercise cruise and
  P/R/N/D so the remaining state contract can close. Family
  breadth beyond Corolla (Camry, RAV4, etc.) still must close command,
  feedback/readiness, producer/route, stock suppression, limits/faults, UI and
  authentication independently. Canonical machine-readable state:
  `data/generated/corolla_tss3_opendbc_readiness.json`; firmware steering-limit ledger:
  `data/generated/corolla_hf_steering_limits.json`; candidate safety contract:
  `data/generated/corolla_hf_panda_lateral_safety_contract.json`; bounded non-steering
  engagement contract: `data/generated/corolla_hf_nonsteering_engagement_state.json`. See
  [../architecture/toyota-openpilot-porting-contract.md](../architecture/toyota-openpilot-porting-contract.md)
  and [../variants/toyota-eps-variant-comparison.md](../variants/toyota-eps-variant-comparison.md).

- **OQ-031 — Boot SecurityAccess lifecycle measurement.** The bad-key backoff itself is
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

- **OQ-032 — Semantic coverage.** The current graph has 6,376 structurally discovered
  functions. A reproducible ranked sweep decompiled 100 entries, including all
  mandatory callback/dispatcher families, but 87 selected entries remain
  `reviewed_unknown`; across the whole ledger 6,257 functions remain
  unreviewed and only 32 carry a semantic grade. This is an open semantic
  denominator, not evidence of hidden subsystems. New work should remain
  lead-driven and record an explicit disposition without upgrading successful
  decompilation into semantic confidence. The selection artifact and current
  boundary are in
  [historical corrected-graph re-audit](../history/2026-08/CORRECTED_GRAPH_REAUDIT_2026-08-11.md).
- **OQ-033 — RFP/P1M-E serial-protocol transfer.** The generic RV40F **host-side static
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
- **OQ-034 — DID `0x1010` production use and slot-4 package.** Static firmware now
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
- **OQ-035 — MACKey `SafekeyNumber` physical meaning.** Techstream forwards the raw
  16-byte payload of `22 10 10` unchanged and uses it to associate returned
  exchange records with master/slave ECUs. Stage 8 now pins an external official
  rekey observation that Toyota requires both an **MCU ID and VIN** and rejects
  VIN-only requests (TMS-016), independently proving that an MCU identity is a
  required input somewhere in the rekey flow. The Techstream binaries still
  contain no `MCUID` naming/derivation edge and no retained transcript labels
  DID `0x1010` as that value. Resolve the final identity join only from target
  ECU firmware or a labeled legitimate vehicle transcript; do not equate the
  two fields from naming similarity alone.
- **OQ-036 — Techstream live-session capture.** `ptshim32.dll`/`ptshim32_0500.dll`
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
- **OQ-037 — Sienna EPS exact CUW row and calibration material.** TMS-029/TMS-032 close
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
- **OQ-038 — CUW retry/recovery live attribution.** TMS-030/TMS-031 close the V18 static
  timing tables, retry/reconnect controller, recovery-file schema, and useful
  P5 power-cycle observers. A live session is still needed to identify the
  selected target row and measure its actual SecurityAccess spacing,
  reset/disconnect/reconnect timing, IG OFF/ON behavior, and recovery-state
  transitions. Preserve `Save/RecoveryInfo.ini`, its saved calibration payload,
  raw J2534 timestamps, selected factory/contact/CPU metadata, and Data IDs
  `0016..0019`, `0033/0034/0036`, `0421/0422`, `07D1/07D2`, and
  `26AC/26AD/26C1/26C3`. This is now a capture task, not a static-RE blocker.
- **OQ-039 — Matching modern calibration package and target-specific integrity values.**
  TMS-026/TMS-034/TMS-037/TMS-038/TMS-039 now close two real legacy package
  families plus an 11-package Tacoma comparative corpus. `T-0087-17.cuw`
  validates the recovered outer CRC/member framing, Format-4 archive grammar,
  S-record route, and legacy software-password consumer. The Tacoma corpus
  validates integrated P5-CAN VFOREST across CPUType86/87/89 and fully closes
  all 16 `.xxz` members as ASCII-hex `ZV00/ZV01` + LZF, including dual-CPU
  member ordering, password chains, image geometry, and stable logical
  header/footer/fill structure. Those expanded images are demonstrably
  structured rather than whole-image ciphertext, although exact native MCU
  interpretation / any Denso storage transform remains bounded. None of these
  artifacts is a tracked modern EPS package. What remains still needs a
  **matching modern EPS CUW**: choose between the two byte-compatible Unified
  rows and recover its `ServiceAuthKey`, `ECUAuthKey`, `SeedKey`, `Nonce`,
  `OffsetAddress`, download ranges, area choice, required-spec branch, and
  actual integrity/header values. Other CUW format-tail variants remain
  specimen-bound. `DigitalSignature` remains unrelated to TIS/RKS `Signature`
  absent a real dataflow edge. TMS-042 now closes the format-`0x67` tail
  grammar, the `ReproMethod=07` delta descriptor/route (ReproStd writers,
  DFI `0x21`), and the modern unpacked GTS+ host anchors on a real six-package
  FRC corpus — but that is a Corolla **front camera**, not EPS: its
  `ServiceAuthKey`/`Nonce`/ranges do not transfer, and the EPS Unified-row
  choice/credentials above remain open.
- **OQ-040 — RKS exact target/region policy (Layer A).** TMS-028/TMS-033 close the static
  client completely: state machine, request-field provenance (incl. shipped
  `Ini/RKS.ini` `[ReproKeyRequest]` values), online/offline/import convergence,
  fixed token format, the `IsStored` flag, and the full SeedValue producer
  chain (CentralGW P5-CAN `27 21` seed → callback → ReproKeyRequest; portal
  token returned to the ECU as `27 22 || token[256]`, byte-pinned in the
  modern GTS+ CUW.dll by TMS-042). The shipped client
  explicitly supports continuing without Signature Request when the repair
  manual says it is unnecessary, and no calibration-schema or flash-writer edge
  makes RKS universal — modern-host selection is the runtime
  `JudgeReproGWNodeForP4AndP5` probe result, **not** the
  `IsControlledBySCC` descriptor bit (which parses `VehicleForNA`/
  `VehicleForEUOT`). TMS-042 additionally closes the host side of the delta
  transfer itself: `.datx` is read raw+CRC-gated and passed verbatim
  (`CDeltaReproArchiveCtrlr` is orchestration-only; no crypto/compression
  imports on the writer path), with the routine-area (`10 F5`, DFI `0x01`)
  then delta-data (`10 F6`, DFI `0x21`) RoutineControl framing — so any
  `.datx` grammar, the routine blob format, and `10F5/10F6` ECU semantics
  now require **FRC bootloader/programming-decoder firmware or an executable camera
  dump** — the 23TC01 Corolla update package itself is already local per TMS-052 — not more host RE, and explicitly not the tracked Sienna/H EPS
  (TMS-029 already proves standard ReproStd `10F5`/`10F6` are absent/rejected
  there). Bind the acquisition with the camera-special direct
  `0x792→0x79A` DID-`1FFF` SWIN response recovered from `GetSWINForFCM`, plus
  generic F181/F18C and the package/current CID; `GetSWINForFCM` is a distinct
  path from generic F181. What remains is external policy evidence: determine
  whether a particular EPS calibration/region requires RKS during a legitimate
  GTS+/TIS session, plus the live gateway seed value and the server-side
  signing algorithm/private key — both external to the shipped client, which
  never reaches the ECU security boundary or any firmware secret.
  See [../tooling/techstream.md](../tooling/techstream.md) §5.3.
- **OQ-041 — MEM-SAFE-001 transfer to newer SecOC/TSK targets.** The partial-AES-block
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
- **OQ-042 — MEM-SAFE-003 equality-oracle reachability for variant identification.** The
  `0x10F3` byte-compare oracle can read application CodeFlash at
  its two configured ranges without dumping the full image. The re-arm loop,
  range gates, request budget, simulator, and explicit live mode are now
  implemented under `exploit/followups/`. It could be used on a newer
  target to check whether the same crypto routines, SecOC profiles, or callback
  structures are present before attempting a full exploit. The remaining
  unknown is a live timing/reachability measurement; the 256-request worst case
  makes only small known signatures rational. See
  [../security/memory-safety-audit.md](../security/memory-safety-audit.md).
- **OQ-043 — Newer-TSK exact target bundle.** No exact target identity currently exists.
  Acquire the part/calibration number plus `F181`, complete CodeFlash and
  DataFlash, matching Techstream/regional DDB set, exact `.cuw`, and the six
  synchronized labeled captures above. Use the redacted manifest schema in
  [../variants/newer-tsk-target-evidence.md](../variants/newer-tsk-target-evidence.md);
  until then every Sienna→newer-TSK transfer remains hypothesis.
- **OQ-044 — RoutineControl `1004` hardware-visible event-history rewrite consequence.**
  Static recovery is closed: default-session `31 01 10 04 FF FF` has no recovered
  vehicle-speed gate and repeatably drives operation 5, which waits on persistent
  rewrites of event-log/history objects 17/18/19/20/21/23. No direct
  conditioned-command/d/q/PWM join is recovered. Do not label the routine
  “ClearDTC” without external/dynamic evidence. Dynamic characterization is not
  packaged as a normal probe because it deliberately modifies persistent event
  history; use only a disposable/matching ECU with NVM backup/restore.
- **OQ-045 — RoutineControl `1108` hardware-visible persistent-reset consequence.**
  Static recovery is closed: unauthenticated default-session `31 01 11 08` has
  no recovered vehicle-speed gate and repeatedly starts/coalesces queue operation
  2, which resets/reinitializes runtime state and persists checkpoint objects
  9/11/12/14/15 before selector-10 completion. Exact static/live closure has no
  direct conditioned-command/d/q/PWM join. Dynamic characterization is
  deliberately not packaged as a normal probe because the routine modifies
  persistent state; use only a disposable/matching ECU with complete NVM
  backup/restore and recovery procedure.
- **OQ-046 — Application WDBI `0204` hardware-visible maintenance/reset consequence.**
  Static recovery is closed: the write transitions/persists checkpoint object 7,
  and one branch then starts queue operation 6, which resets/reinitializes state
  and persists checkpoint objects 9/11/12/14/15 after WDBI completion. No direct
  conditioned-command/d/q/PWM join is recovered. Dynamic characterization is
  deliberately not packaged as a normal bench probe because it modifies
  persistent state; use only a disposable/matching bench with complete NVM
  backup/restore and recovery procedure if the physical effect becomes important.
- **OQ-047 — Application WDBI `2012` hardware-visible lifecycle-inhibit consequence.**
  Static recovery now closes the software cone: after the scaled-supply snapshot
  reaches `0x0900`, `2012` suppresses the mode-specific transition block that
  normally performs task-signal clearing / NvM default-reset actions, and it
  also clears an alternate rotor-observer calibration selector. The remaining
  unknown is what observable EPS behavior this inhibit produces on an isolated
  matching bench and how it recovers across session exit/reset. Static closure
  has no direct d/q/PWM join, so do not describe it as steering-current control.
- **OQ-048 — Application WDBI `2013/2014` hardware-visible consequence.** Their static
  cones are now closed. Both retain the vehicle-speed plus two-state-flag start
  gate. `2013` reaches motor-worker fields `FEBE6DCA/6DCC` but dead-ends in
  write-only task/RTE mirrors; `2014` changes threshold/mode eligibility and
  participates in RoutineControl `110A/110C` start gating. Neither has a
  recovered direct d/q/PI/PWM join. The remaining question is what observable
  EPS behavior either write produces on an isolated matching bench and how the
  state recovers across diagnostic session exit/reset.
- **OQ-049 — Application CommunicationControl live effect.** Static recovery proves that
  extended-session SID `0x28` reaches real communication-mode updates without a
  configured SecurityAccess policy or recovered speed gate. The isolated-bench
  probe is now ready under `exploit/followups/`; run it to determine which
  baseline-active EPS application Tx IDs are suppressed by `28 01 01` and prove
  all recover after `28 00 01`. This is an availability characterization, not a
  candidate steering interface.
- **OQ-050 — Exploit-interest cohort consumption (SWEEP-008).** The ranking pipeline
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
- **OQ-051 — Cross-calibration structural triage of future P1M-E images.** The offline
  structural fingerprint scanner (`tools/analyze_rh850_codeflash_structure.py`)
  now flags boot-CRC geometry, RAM-exec/MEM-SAFE-001 package anchors, and XCP
  `0x7F7/0x7F8` route/command-map constants in arbitrary images. Every match is
  a triage candidate only; whether each mechanism transfers must be verified
  against the new firmware bytes before anything is recorded beyond
  `docs/variants/` hypothesis.
- **OQ-052 — True-TSS3 longitudinal producer/control contract.** TMS-079 adds an
  important search boundary: current category-498 install rows have zero selected
  co-occurrence in NA/EU/JP with `PCS1_P5` 427, `DSSystem_P5` 428,
  `Fr_RadSen_P5` 429, `RoadSign_P5` 431, or `PCS2_P5` 432. Do not pick one of
  those databases as the TSS3 longitudinal owner merely because it is P5 or has a
  promising name. TMS-080/082 instead close a concrete cross-vehicle GTS+ recorder
  source to join to an exact target: the same-release native FRC Operation/Image FFD
  acquisition path is now recovered (`AB11/12/13 -> EB11/12/13`; Image-FFD
  `22 11 03 -> 22 11 01 -> 27 03/04 -> 22 20 81`), TSE persists PCS FFD sections,
  and PCS Data Viewer names the longitudinal/lateral request and arbitration model.
  TMS-084 now closes the former managed-table gap too: 1,130 exact bit/scaling rows
  across 623 recorder DIDs, 47 RoB definitions, and the current FCM TSS3 image decode
  (`AB31/EB31`, `AB33/EB33`, exact byte-9 variable-length block grammar, `6002..6017`
  split reassembly to `6001`, then `622081` value `01` unencrypted or
  `reverse_bits8(cipher_byte) XOR 0xAA`).
  The remaining host-side validation item is a representative Toyota-generated TSS3 TSE
  specimen; the substantive open problem is recorder-ID -> vehicle-network producer/frame/
  SecOC ownership and arbitration execution on an exact target. Join that evidence to an exact
  target's installed modules and live/firmware evidence. Older Toyota prior
  art makes longitudinal ownership a separate generation-specific architecture:
  ordinary TSS2 treats the camera as the ACC command source, `RADAR_ACC` moves
  ownership to the radar, and some SecOC-protected profiles split acceleration
  across classic `0x343` plus authenticated `0x183`. That SecOC fact is orthogonal
  to TSS generation. The pinned 2023 Corolla route has **no `0x343`** and its
  `0x183` is a 64-byte ~20-Hz CAN-FD member of the wider `0x180..0x18B` family;
  the retained 2025 Span capture reproduces the same ID/DLC family. This proves the
  old `0x183/8` ACC_CONTROL_2 wire contract does not transfer and makes the numeric
  ID alone non-semantic. For one exact TSS3 target, identify the real ACC producer
  (FRC, radar/ADS, gateway, brake/ACC controller, or other), command/feedback fields
  and cadence, lead/distance/standstill state, AEB/brake arbitration,
  integrity/authentication, and the safe stock-source suppression/fallback point.
  Do not add a TSS3 longitudinal builder or Panda whitelist until that ownership
  contract is target-native. Canonical:
  [../architecture/toyota-openpilot-porting-contract.md](../architecture/toyota-openpilot-porting-contract.md) §4.1/§5D and
  `data/generated/corolla_tss3_opendbc_readiness.json`.

- **OQ-053 — F33 non-disruptive application-mode RAM execution pivot.** **Production-only ordering note:** VAR-060 now closes an exact persistent F33 Gate-2 development patch and deterministic restore, so this question no longer blocks first development lateral. It remains open because the production goal is still a non-persistent signer/control path. Exact
  `8965F3307000` has the desired volatile carrier and the placement half of the
  production loader: live evidence proves `FEBFF9F0..FEBFFBFB` (524 bytes)
  survives the real stock application startup byte-for-byte and executes, while
  the former `FEBF0000` carrier is disproved by that same startup. Target-native
  XCP `SET_MTA 0x82C62` + `DOWNLOAD 0x81FFE` can statically write arbitrary tester
  bytes throughout `FEBF7C00..FEBFFBFF`; GET_SEED/UNLOCK are unconfigured. The
  packed `0x7F7/0x7F8` endpoint is present in CodeFlash. CORR-124 now closes its
  physical route target-natively: RX rule46 at `0x23398` and TX handle `0x37`
  independently resolve to RSCFD controller 1, the same EPS channel exposed as
  Panda bus1 on the identity-bound normal harness. The retained CONNECT timeout is
  therefore a correct-route/no-response runtime observation, not route falsification.
  The remaining architectural blocker is a safe already-running-application control
  transfer into the tail.

  The **recovered stock pivot surface is now statically exhausted**, rather than
  merely missing an obvious callback. CORR-123 refreshes that conclusion against
  the current first-class 6,065-function graph: **496 decoded indirect transfers**
  exist in total (403 `jarl` / 93 `jmp`), **487 in application CodeFlash**
  (395 / 92). The function-owned classifier covers 495 total and **all 487
  application sites**; among its direct target-definition references, 152 resolve
  to CodeFlash/data, 9 to concrete lower-RAM cells, and **zero to the
  `FEBF7C00..FEBFFBFF` XCP window**. Those lower-RAM call sources reduce to
  `FEBF0FD0/FEBF6B04/FEBF117C/FEBF1194/FEBE5628`, all below the XCP floor and
  closed to boot-only, fixed-CodeFlash, guarded-callback, or fixed service-table
  semantics. The calibration-page shadow is data-only;
  the four locally unresolved computed calls resolve to guarded lower-RAM fixed-
  CodeFlash callbacks; eight exception-return paths save PCs on lower `FEBE`
  stacks; seven fixed DMAC families cover 22 records / 88 endpoint fields with
  zero XCP-window endpoints and `0x60A6A` as the only recovered application channel
  programmer; the whole-image CTBP census finds only reset's `ldsr r0,CTBP @ 0x25E`;
  application context setup writes fixed `INTBP=0x20200` and `EBASE=0x20000`;
  and full configured XCP DAQ is measurement/readback-only (`WRITE_DAQ 0x82510`
  supplies a read source consumed by `0x82368`, not a write/call target).

  The diagnostic/factory-test classes are closed target-natively too. SID `0x11`
  ECUReset is session-2-only with null callback and no subfunctions. WDBI resolves
  exactly 13 DIDs (`0204, 2001, 2002, 2005, 2006, 2007, 2008, 2009, 200D, 2010,
  2012, 2013, 2014`) to fixed CodeFlash maintenance setters. All 19 RoutineControl
  rows use fixed CodeFlash callbacks (RID `0x1010` is null/null; `0x100F` remains
  only the fixed-16/private-result command-5 oracle). SID `0xBA` has ten fixed
  operation records / 20 fixed start-finish callbacks, and SID `0xAB` has three
  fixed selectors plus a 51-populated-entry event-ID/type catalogue; neither
  interprets request bytes as an executable address.

  Therefore more broad static searching of known stock services has diminishing
  value. The remaining bounded classes are synthesized/computed aliases not present
  in recovered references, a memory-safety bug outside the recovered CFG/dataflow,
  a separate undiscovered DMA/hardware mutation mechanism, or undiscovered code.
  The next live work should remain non-executing. First use the new read-only
  `xcp_runtime_state_probe.py` on the proven normal-harness bus1/controller-1 route
  to snapshot the exact admission chain (`FEBE3DF2/3DE5`, `FEBE4914..493A`,
  `FEBE4EE6`, `FEBE4FAE`); only then repeat CONNECT. If it responds, close placement
  with bounded high-tail DOWNLOAD+SHORT_UPLOAD readback. For the **execution** blocker, collect a targeted
  runtime RAM/control-flow discriminator (for example before/after lower-RAM state
  plus registration/control-flow trace around benign stock diagnostic/task activity)
  to identify a concrete mutable continuation/callback/task object or unrecovered
  trigger. Do not guess an arbitrary PC write. Canonical:
  [../variants/camry-2026-live-baseline.md](../variants/camry-2026-live-baseline.md) §13.


- **OQ-054 — exact-F33 stock-LTA authority into the shared `CC50/CC62` actuation funnel.**
  This is the current steering-command blocker and should not be reopened as a broad CAN
  search. VAR-081 strongly identifies **73.303384 s** of retained factory LTA/LCA-active
  operation on the relay-correct Toyota Bus-4 Brake/EPS network with **zero B6**; the
  operator directly observed factory LTA physically steering. VAR-082 then scans every
  sufficiently periodic Bus-4 ID/DLC field family and finds zero external field that
  reproducibly leads the EPS motor/steering response. VAR-083 closes the downstream exact
  F33 current-control convergence instead of leaving it hypothetical:
  `CC50 -> D042C/CC62 -> D042C/CC66 -> D047C/CC64 -> AC54/EE40C -> 6AF4 ->
  6E0A -> 6DEC -> 6DC8/6DD6 -> 38162`. `AC56/EE40A/6772/1C02` is the diagnostic
  mirror of pre-slew `CC62`; it is not the motor-driving sibling. No second additive
  lateral command is recovered downstream of `CC50`.

  The contradiction is therefore upstream: **what state/value gives `CC50/CC62` stock-LTA
  lane authority while B6 is absent, and how would a B6 request arbitrate with it?** The
  B6-inactive `D0218` value terms are already semantically bounded to torque/speed/angle
  feedback, ROM/internal aggregation, and return/dither families; the ordinary `C28FC/
  C2B64` selector is ineffective for the retained route because zero sig160 can reach only
  equivalent selector 0/2 banks. Do not re-derive those branches unless new evidence
  falsifies their pinned tests.

  VAR-084 attacks the main static false-negative classes and finds no concrete alternate
  producer: no stored CodeFlash/live-RAM pointer into the widened command/motor ROI, nine
  non-default unrecovered ISR entries delegate into recovered timer/serial/acquisition code
  without a transitive ROI writer, fixed DMAC descriptors route to known GlobalRAM rings
  rather than LocalRAM, fixed callback cells install CodeFlash targets, and the exact 47
  RSCFD rules contain no hidden normal-CAN route. Two static escape hatches remain and are
  the next falsifiers: **E1**, resolve every register-arithmetic `st.{b,h,w}` effective
  address that canonical data references leave computed and report any path capable of
  landing in the command/motor ROI; **E2**, census every runtime writer of the DMAC
  destination-address SFRs and prove the values derive only from the fixed descriptor
  tables. If E1/E2 are clean, continue upstream from `CC50` through its remaining
  selectors/gates/value producers with the physical factory-LTA observation held fixed;
  do not resolve the contradiction by relabeling the observed steering as generic assist.
  Canonical: [../variants/camry-2026-live-baseline.md](../variants/camry-2026-live-baseline.md)
  §§20,33–35; VAR-081/082/083/084; CORR-129/130.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: —
- Corrections with this document as canonical home: [CORR-092](../reference/index.md#correction-corr-092)
<!-- knowledge-cross-references:end -->
