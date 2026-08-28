# Current priorities

Short execution queue only. This page answers **what should we do next?** It is
not a historical roadmap and should not become one. Detailed unresolved state
belongs in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md); completed work belongs in
[FINDINGS.md](FINDINGS.md) and the canonical subsystem reports.

## Pre-GTS static-only queue: closed

The eight-item V18/firmware static-closure pass is complete to the evidence
available without a matching calibration package or live GTS+/CUW session.
TMS-025/TMS-029 close writer-family census/target scoring; TMS-024/TMS-026 close
the target-integrity/calibration-schema boundary; TMS-027 closes the Sienna
motor/control observer card; TMS-028/TMS-033 close the RKS client incl. the
full SeedValue producer chain; TMS-030/TMS-031 close CUW timing/recovery plus
the targeted DDB/legacy-EPS comparative pass; TMS-032 closes both surviving
Unified routes at body level; and TMS-034 recovers the outer `.cuw` container
framing (synthetic-fixture validated, specimen validation pending).

Do not start another undirected V18 or firmware sweep to continue that queue.
The remaining high-value blockers now require genuinely new evidence: a matching
modern-EPS `.cuw`/`.cal` package (the six-package FRC delta corpus closed by
TMS-042 is front-camera ReproStd, not EPS Unified), a retained labeled
GTS+/J2534 session, newer GTS+/CUW+ host material beyond the unpacked CUWPlus
subset already pinned, gateway/camera/other steering-controller firmware, or
missing target CodeFlash.
The concrete live capture requirements are in
[../tooling/techstream-capture-procedure.md](../tooling/techstream-capture-procedure.md),
and unresolved static/dynamic boundaries remain in
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

## Directed static exception — true-TSS3 FRC_P5 producer contract

The previous pre-GTS static queue is still closed; do **not** reopen an
undirected Techstream or Corolla-H firmware sweep. TMS-040 closed the
software-ownership question that justified the exception: the true-TSS3
lateral-control **diagnostic-domain holder** is generation-20 category **498
`FRC_P5` = Front Recognition Camera 2** (distinct from `Fr_Camera_P5` 430 and
`ADS_Eth_P5` 476; holder means exactly that — physical control-path ownership
is not asserted), it holds dedicated master plugin roles 233/234
(`GetTSS3ImageFFDP5_DT.dll` / `GetTSS3OperationFFDP5_DT.dll`), it pins the
LTA/LDA/LCA installation/customize/control/hands-off DID surface, and its
read-only `AB/EB` Operation FFD capture path is byte-anchored. Category 498
also binds an **Active-Test surface**. TMS-041 closes the steering-relevant
part of that surface as fixed type-71 routine control, not a parameterized
lateral writer: `FRC_P5` has no type-68 direct P5 Active-Test table, and LDA/
LTA/LCA Steering Vibration are fixed routines `0x1508/0x1588/0x15C8` with no
command/output-mask/button payload variables. `SingleRoutineActTstP5_DT.dll`
uses a `D5 -> D7 -> D6` `21 E2 <RID BE16>` sequence; the vibration status
pattern is byte `02`. The remaining unknown is the camera's downstream
vehicle-network effect of those routines. TMS-043 now closes the **module-level
upstream topology** without claiming payload forwarding: Corolla P5 sets pair
`FRC_P5` 498 and `EMPS_P5` 405 with category **435 `ABS_P5` = Brake/EPB**;
`FRC_P5` carries X216E `Front Recognition Camera => BRK Communication Invalid`
plus brake/EPS/ADS-interface missing-message DTCs; `ABS_P5` monitors EPS
communication and exposes `0x107E ADS Control EPS Pinion Angle2` at a verified
0.00025 rad/count. The same `0x107E` engineering conversion is shared by the
Brake-Booster and EPB P5 diagnostic databases. Exact H independently maps B6
loss to U012987 Brake System Control Module. Because FRC also monitors EPS
directly and both FRC/ABS reference an Automated Driving System Interface
module, this is not proof of an FRC→ABS→B6 byte-forwarding chain. The ADS_Eth_P5
target-angle order rows remain recorded-snapshot evidence, and `0x1CEE/0x1CEF`
remain steering-observer DIDs absent from exact H.

TMS-044 additionally closes the category-435 Techstream Active-Test avenue: its
20 direct tests and four routines are brake-actuator-only, with no steering/EPS/ADS/
lateral/pinion named catalog row; all four routines have zero variable-backed
command/mask/button payloads. Do not spend another static pass looking for the normal
B6 producer in that Active-Test catalog.

TMS-045 closes the acquisition search key. Raw NA/EU/JP P5 VDS
`ECU_Setting_Table` independently maps category 435 to request address **`7B0`**;
legacy SUW independently maps VSC/ABS/ECB to `CANID1=7B0`, while modern
`P5-Unified04` obtains CID/prepare/flash CAN IDs from `GetCanIDsFromCANIDTable`
rather than a hard-coded FRC address. The complete current 26-package CUW
reference inventory has six `0792` FRC and three `07A1` EPS positive controls
but **no `07B0` package**. This is only a local-corpus absence. TMS-046
additionally closes the VDS pair as **`Address=7B0`, `FuncAddress=7E5`** from
Techstream's own SQL schema and the exact `7E0..7E7` phase-5 family. V18 Unified
CID retrieval calls generic `ReadSoftwareID` (`22 F1 81` / `62 F1 81`) before
mode dispatch; the alternate `1FFF` SWIN reader is uniquely gated to `0792` FRC.
TMS-047 now independently proves the category-435 **diagnostic** reader itself:
master role 82 is `GetCID_SID22_SAS_DT.dll`; `(435, 0xDC)` resolves through
ComSet 1 / CommFrame `0x444` to exact `22 F1 81` / mask `FF FF FF` / expected
`62 F1 81`. The parser skips the first four response bytes and groups the rest
into 16-byte `CID1`, `CID2`, … values. Therefore a read-only F181 at physical
`7B0` is the exact Techstream path to acquire the current Brake/EPB CID; what is
still missing is the **value**, not the DID/protocol.

TMS-048 eliminates `SearchCal.dll` as a hidden offline catalog path: the V18
helper enumerates local `\*.cuw` files, parses their Vehicle/CPU/CID/target
calibration profile fields, and opens a selected local result. It has no network,
database, or XML client and Techstream invokes its sole export with an initially
empty C-string rather than a CID/catalog object. Thus once `7B0/F181` supplies the
current Brake CID, **SearchCal can only match a CUW already downloaded locally**.
TMS-049 closes that missing handoff. `tiswebapi.dll` owns the remote
SendSearchInfo → GetSearchInfo → DownloadCalFile → GetCalFileURL sequence, and
the managed utility downloads the returned ZIP, expands nested ZIPs, and copies
the calibration files into Techstream's local store. More importantly, the
server search input is now joined to the vehicle: `GetPartNumber_DT.dll` uses
`22 01 05` for `ecuAssyNo` and **`22 F1 81` for the `baseSwNo` array**, reading
byte 3 as a count and 16-byte records from byte 4. `SaveEcuSupplyChangeSendXmlFile`
serializes those records under `baseSwNoLst`; the web API's separate
`strSoftwareId` is `CTISCommon::GetPecID` client identity, not ECU F181.

TMS-050 closes the client-side result-selection step that remained between search
and download. Techstream parses `resData/systemAssyInfo`, applies its wired/update
policy to the improvement records, parses per-ECU `selectSwInfo` records, and
normalizes selected software into 0x64-byte targets. For the supply-candidate
path, server `swId` becomes get-cal `swNo`, `fileName` is preserved, and `swType`
is derived client-side; `systemAssyNo` is a separate assembly/policy identifier.
`FindCalFile` then removes targets already available in the local `*.cuw` store,
and only the missing subset is serialized into the get-cal request. The next step
is therefore operational rather than another host-static search: read Brake
`7B0/F181` plus `0105` and VIN on the target, run/record the normal Toyota ECU
Supply Change lookup, preserve the returned `resData`, and retain the `07B0`
package if the service offers one.

**Next software-analysis target:** TMS-051 closes what can be learned about B6
sender attribution from the current decoded corpus; TMS-052 now narrows the
acquisition blocker. Raw `T-0058-23.cuw` and `T-0060-23.cuw` exactly match Toyota
23TC01's published 2023-Corolla FRC transitions `8646F1204300/4400 →
8646F1204500`, so a generation/model-matched `0792` FRC family is **already
owned**. Its runtime representation remains opaque. Toyota 24TC01 independently
publishes the 2023-Corolla Brake/EPB family `F152612A5100/5200/5300 →
F152612A5400`, while our 26-CUW corpus contains zero `07B0` packages and none of
those Brake CIDs. Do **not** spend another pass searching for an unspecified 2023
Corolla FRC package or literal-searching the encoded FRC bodies. Acquire/decode the
category-435 **`Node01/DiagID=07B0`** Brake application—starting with live
`7B0/F181`, `0105`, VIN and the 24TC01 CID family as search handles—and either
decode/exactly identify the already-owned `0792` FRC family or capture synchronized
stock-LTA traffic. Then recover the remaining **producer-side** contract: target
originator/forwarder, 32-byte B6 Tx builder, wall-clock cadence, CMAC/freshness
ownership, authenticated-but-EPS-unconsumed bytes, and stock-source suppression.
SECOC-071 now closes the EPS-side verification algorithm itself:
B6 freshness ID2/slot1 state, `00F`-anchored reset/message candidate window, retry
scopes, `0x24` boundary behavior, trip-wrap reset, 36-byte CMAC input, ICU-S slot-4
selection, result polarity, commit-before-delivery ordering, and separation from
application signal261. SECOC-072 then closes the structural transfer question against
Sienna `8965B4512000`: H/F uses the same generated SecOC receiver framework, including
`00F` synchronization/wrap arithmetic, FV46/FV4 codecs, DataID+payload+freshness
CMAC28 construction, staged/commit-after-auth freshness handling, and ICU-S command7
selector4 machinery. B6 is a new Corolla PDU instantiated from the same 32-byte
ordinary-FD SecOC class already used by Sienna `090/D7`. Do **not** copy Sienna's
freshness IDs, ordinary-slot numbers, RAM addresses, or assume its slot-4 secret is the
same: those are target-generated/provisioned state, and shared D7 itself moves from
Sienna freshness ID6/slot4 to H/F ID1/slot0. SECOC-073 now closes the live `0x00F`
bridge too: the wire directly exposes global trip16/reset20, reset state advances at a
nominal 300 ms cadence, and H's exact reset/message reconstruction replays all retained
D7 traffic including the `current-1` rollover overlap. TMS-053 closes the replacement
sender state machine from a strictly newer authenticated `00F` epoch: no previous B6
message8 is required; own message8 locally, advance normally inside the receiver's
+1..+4 same-epoch window, keep application signal261 independent, and after sender
restart wait for the next authenticated sync epoch rather than guessing or persisting
Toyota's prior message8. D7's message counter remains independent and must not be
reused. Do not spend another pass rediscovering receiver freshness, global sync state,
MAC28 logic, or Toyota B6 counter-start policy for the replacement sender. The remaining
SecOC problem is slot-4 key/approved-MAC use (or live command-5 capability after
validating the already-built H/F-native application carrier), **stock** sender cadence/secondary-field template, stock
suppression, and producer topology.
TMS-042 makes the same acquisition the highest-value reprogramming target too: modern GTS+ proves the FRC `ReproMethod=07` path
uploads the package routine with DFI `0x01` / `10F5`, then the compact
`DeltaReproData` with DFI `0x21` / `10F6`, while the host treats `.datx` as
opaque bytes. TMS-052 proves the 23TC01 Corolla **package** is already local, so the
missing consumer is now specifically FRC bootloader/programming-decoder firmware
or an executable camera dump that can explain the routine/blob transform and delta
representation; do not look for those handlers in the tracked Sienna/H EPS,
where TMS-029 already closes standard ReproStd `10F5/10F6` as absent/rejected.
The V18 Unified CID path now gives a concrete identity checklist for that
acquisition: preserve generic F181, F18C, the package/current CID, and especially
the camera-special direct `0x792→0x79A` `22 1F FF` / `62 1F FF` SWIN response
(`GetSWINForFCM`; distinct from F181). The read-only Operation FFD surface
(`AB 11/12/13` → `EB …`, parser at 0x10001A70) is one reference capture protocol
once live probes are justified; fixed FRC routine `0x1588` (LTA Steering
Vibration) is a second, higher-specificity trigger for isolating the
camera-to-steering output. The repository deliberately ships no live writer
for either proprietary path. A
newer EMPS/EMPS2 image that implements `0x1CEE/0x1CEF` remains the
complementary steering-side acquisition.

The pinned comma Toyota implementation is now captured as a role-level porting
contract in [../architecture/toyota-openpilot-porting-contract.md](../architecture/toyota-openpilot-porting-contract.md).
Use that contract as the acceptance checklist for this FRC pass: recover not
only the lateral payload, but its feedback/readiness state, physical producer
and route, stock-source suppression point, fault/driver-override envelope, UI
coexistence, and authentication requirements. Older IDs are search vocabulary,
not TSS3 wire facts. Lateral acquisition is the immediate software target; the
separate TSS3 longitudinal ownership/command problem is tracked explicitly as
[OQ-052](OPEN_QUESTIONS.md) and must be closed before production longitudinal
support.

The community `NEW_MSG_8A_LAT_CONTROL` heatmap remains a useful naming lead, but
COM-013 now gives it a stronger negative boundary. The exact pinned 2023 public
route and the retained 2025 Span capture share the **same 22-ID/DLC CAN-FD
baseline**, and `0x18A` is simply one 64-byte ~20-Hz member of the broader
`0x180..0x18B` family. Span's capture is probably NRtD despite its filename, so
this is topology/geometry evidence only. No bit/name/producer/authentication join
to `FRC_P5` is proved. Do not encode `0x18A` in a DBC from the heatmap/screenshot;
treat it as one candidate member the matched FRC/Brake firmware or a synchronized
stock-LTA capture must confirm or refute.

Canonical: [../tooling/techstream.md](../tooling/techstream.md) §6.2.2 ·
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) ·
[../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md) §7.35.

## Parallel integration target — firmware-identified, relay-correct TSS3 capture

**Current exact live target (VAR-051/052/053/054/055/056/057):** the maintainer's 2026 Camry now has both identity-bound live evidence and exact target-native EPS firmware. EPS F181 is `8965F3307000 / 8A3113303100` on normal-harness `(bus1,param1)`; FRC is `0x792→0x79A / 8646F3315000`; Brake/EPB is `0x7B0→0x7B8 / F152633K0000`. VAR-053 closes `0x51E` Ready plus **P=0, R=1, N=2, D=3, B=4**; VAR-054/056 close the target-native B6 receiver, timing, limits, feedback and runtime anchors. VAR-057 supersedes the old low-RAM carrier assumption: the real stock startup overwrites `FEBF0000`, while **`FEBFF9F0..FEBFFBFB` (524 bytes) is live-proven retained and executable** with stock application return and zero Panda TX-block delta. Exact F33 application XCP provides the placement half of the desired production loader: packed `0x7F7/0x7F8` descriptors exist, `SET_MTA 0x82C62` + `DOWNLOAD 0x81FFE` can write arbitrary bytes throughout `FEBF7C00..FEBFFBFF`, and GET_SEED/UNLOCK are unconfigured. A target-native 22-record / 88-endpoint fixed-DMAC census has zero endpoints in the XCP window, closing the obvious recovered DMA shortcut. **CORR-124 now proves the old normal bus1/ELM1 XCP probe used the correct physical route:** RX rule46 and TX handle `0x37` independently bind `0x7F7/0x7F8` to exact F33 RSCFD controller 1, so its timeout is a live admission/response negative rather than route falsification. The **remaining production architecture blocker is now a safe already-running-application PC pivot into the high tail**, not carrier retention or a RAM writer. OQ-053's recovered stock pivot classes are now **statically exhausted**: computed-call/callback cells, exception returns, fixed DMAC, CTBP/INTBP/EBASE, XCP DAQ, ECUReset, RoutineControl, WDBI, BA and AB dispatch were all closed target-natively without a writable control-transfer object into the retained tail. Do not repeat broad callback/service mining as if it were still the next static discriminator. Highest-value bounded next evidence is the read-only exact-state preflight on the proven bus1/controller-1 route, then CONNECT and non-executing high-tail DOWNLOAD/readback if admitted, plus a runtime-specific volatile-pivot discriminator; do not use the PROGRAMMING handoff as a normal startup design and do not guess arbitrary PC writes. Slot-4 command-5 permission/latency and stock-LTA sender/suppression characterization remain separate live gates. Production output remains disabled. Canonical baseline: [../variants/camry-2026-live-baseline.md](../variants/camry-2026-live-baseline.md) §§12–13.

**Development-path update (VAR-060/SECOC-074):** exact F33 persistent Gate-2 patch construction is now closed offline from a fresh bare import, not transferred from Sienna/H/F: `0x8F952 e0d1→e001`, exact image SHA `42dce8ef…d9b0e7`, stock-valid high CRC region, repaired fixup `0xD9AF33AF`, and deterministic byte-exact restore. The flash backend is also now independently pinned by exact F33 boot code plus locally retained/CMAC-validated Toyota `T-0035-22.cuw`; both prove post-halfword FSTATR **DBFULL `0x400`** pacing, correcting the prior external `0x800/SUSRDY` interpretation. This means the §13 application-mode signer pivot no longer blocks **first development lateral**. The next development gates are a zero-write live patch preflight, restore-gated APPLY + invalid-MAC causal proof, then stock-B6 off→active→off capture/source suppression and conservative first actuation. The volatile signer pivot remains the preferred production architecture and OQ-053 remains open for that purpose. Canonical: [../variants/camry-2026-live-baseline.md](../variants/camry-2026-live-baseline.md) §14.

### Exact-F33 openpilot port — passive default + fail-closed development path (VAR-058/062)

The passive baseline remains pinned at nested opendbc commit
`ab60fd95d8a7b566e10ed1cf59738292f3498932` (parent `kai-openpilot`
`d7d7dfd7e49961e9d35eb7a7681e8756ceee8d04`). It binds the Camry by byte-exact
EPS F181 on the relay-correct Toyota bus-0 UDS F181 query, retains the 179-ID
normal-harness census separately because Corolla's 147-ID TSS3 fingerprint is a
strict subset, replays same-car `0x025/0x030/0x127/0x51E` state, and constructs the
known B6/FV46/FV4/CMAC28 candidate in shadow. Ordinary TSS3 CarParams still remains
`SafetyModel.noOutput`; without the explicit development config, controller output is zero CAN.

The remaining **static first-development-lateral software work is now staged** in
`opendbc@dde0fcf0fbaf875750c54a072b0dcb3857f8829b` /
`kai-openpilot@15f3550365e2eee54ca5645ae9c24d9d41ae4f31`. `ToyotaTSS3DevLateral` is
development-only and rejected on release branches. Its JSON config must supply exact
`8965F3307000`, a stock-captured 28-byte B6 template, measured cadence, and explicit
completed Gate-2 + exclusive-authority live attestations; the Toyota interface also rejects
the unsplit bus-1 topology. Only then can an `ALLOW_DEBUG` Panda mode whitelist bus-0
`0x0B6/32`, with exact-F33 ID11/±1745/+78/+1/steering-rate-100/35-ms checks. The
development sender deliberately emits a real FV4 with zero MAC28 for the already-validated
Gate-2 experiment, and disarms on inactivity rather than inventing OEM restart semantics.
**Production output remains disabled.**

Static F33 Tx closure also removes the need to transfer `0x351/0x394/0x4A3` wire
geometry from H/F. **VAR-059 now also closes the F33 `0x394` classifier statically:**
`0x512E4`, state table `0x2A19C`, DEM table `0x2FC50`, DTC table `0x30850`,
240 classified events, target-specific 200/200/600/22,170 aging, and the exact lossy
wire→state-candidate map are all target-native. Do not redo that static sweep or copy H's
17,736 clear age. The remaining `0x394` work is relay-correct **asserted/recovery**
correlation to choose openpilot `steerFaultTemporary`/`steerFaultPermanent`; state0 is an
OEM internal clear/normal classifier state, not independently a Ready authorization bit. Highest-value remaining work is live: stock B6 off→active→off
cadence/template/freshness on a relay-correct exact-F181 car, exclusive source
suppression, slot-4 command-5 generation permission plus latency/contention, and
normal/asserted/recovery correlations for the F33 status carriers. Driver override
and current-response thresholds remain policy choices requiring conservative dynamic
validation, not values to infer from representation clamps. Canonical port report:
[../variants/camry-2026-tss3-opendbc-port.md](../variants/camry-2026-tss3-opendbc-port.md).

COM-013 closes much more of the whole-vehicle side than the earlier EPS-only
roadmap. TSS generation and SecOC/TSK are **orthogonal** (CORR-108). The public
2023 route already proved partial state continuity; Span's newly retained July-29
driving rlog now independently proves real motion plus dynamic brake/gas/steering,
6,000/6,000 exact-H/F `0x030` rule matches, and `0x127 GEAR_PACKET_HYBRID` carrier/
checksum/`D` compatibility. The old Span `ready_capture.ndjson` remains useful as
structural corroboration, but it is no longer our only 2025-attributed CAN sample.

Do not overread the new log's wiring. All 599 Panda-state samples are
`ELM327 param=1`, `harnessStatus=flipped`, controls disallowed. The maintainer
reports Span had **not physically swapped the Toyota-B CAN0/CAN1 pairs**.
`harnessStatus=flipped` is only Panda harness orientation; ELM327 param1 keeps
logical bus 1/FDCAN2 on the normal harness CAN1 wires, so passive observation of
that unsplit network is valid. What the missing physical repin prevents is normal
comma **interception**: the target network is not moved onto the CAN0/CAN2 relay
pair, so the capture cannot identify camera-side versus car-side producer
ownership or prove stock-source suppression behavior.

Span's moving capture still has `00F/D7` but no B6 and only `030` from the exact
H/F Tx set. That rules out treating the earlier absence as merely an NRtD/static
artifact, but it does **not** prove B6 is absent from the vehicle: there is no
stock-LTA off→active→off transition and no exact F181 join. Treat it as a bounded
segment-level negative.

**Highest-value dynamic artifact now:** on a firmware-identified H/F-family target,
physically repin Toyota-B CAN0/CAN1 so the target network lands on the CAN0/CAN2
relay pair, preserve `carFw`/F181, and log all buses while safely exercising:

1. stock LTA off → active → off plus ordinary driver steering;
2. cruise main, engage/cancel and standstill where safe while directly polling FRC P5
   Data IDs `0x1905` (Cruise Control Permission), `0x1906` (Main Switch Recognition /
   Set-Cancel / not-available icon), `0x1914` (ACC Control in Operation), `0x1901`
   (Current/Memory Vehicle Speed), and `0x1912` (Set Vehicle Interval Time) with the
   recovered `22 19 xx` RDBI requests and matching `62 19 xx` response-prefix checks;
3. brake and gas transitions;
4. stationary P/R/N/D transitions with an independent gear-state oracle (`0x127` raw 3 is only prior-art-compatible with D today); and
5. lane/LTA UI state changes and one recoverable message-loss/fault condition if
   a safe diagnostic trigger exists.

This capture should close B6 visibility/**stock** cadence and producer side, exact physical
relay path and the concrete stock-source suppression/isolation point, the remaining
conservative Panda/openpilot driver-override policy calibration/validation, a deliberately chosen/validated `0x4A3` Q-current actuator-response policy,
`0x351/0x394` fault transitions plus the now-wire-closed `0x51E B0[7] -> DID 0x1033`
Ready Status transition, remaining gear enums, the CAN fields that correspond to the
now-exact FRC cruise diagnostic oracles, and the correct Panda parser/safety bus. The **core H/F Panda
command envelope itself is now statically derived** (COM-014/COM-015): ID11-only
candidate active control, ±1745 raw (~100 deg) target, strict candidate +1 sequence /
<=78-raw target step, 7-tick EPS loss cutoff, raw steering-rate cutout 100, and
selected-bank per-task LTA slew. Static recovery also finds no measured-Q-current
comparator in the cooperative supervisor and no speed-dependent reduction of the hard
±1745 B6 ceiling. Do not spend another pass copying old Toyota angle/current limits;
focus the live capture on still-parameterized driver/fault/response policy and
deployment topology. **COM-016 now closes the receiver-side suppression question:**
B6 has one source-agnostic SecOC queue/freshness/COM state, pending arrivals coalesce,
in-flight arrivals are ignored, signal261 is not a duplicate filter, and Target
Lateral ID has no priority arbiter. CORR-111 additionally proves a bounded generated
failure-forwarding mode: while `FEBE5408 < 204` (or the separate global D2 override
is active), freshness-hard-failed or retry-exhausted CMAC-failed B6 can still reach
COM without committing freshness. Deterministic production control therefore
requires exclusive B6 authority; the live capture is needed to locate/validate the
physical stock suppression point, not to decide whether racing two streams is
acceptable. Current Toyota safety assumes checked state on logical bus 0; direct
diagnostic/passive observation on bus 1 is not itself the production relay topology.

Machine-readable checklist: `data/generated/corolla_tss3_opendbc_readiness.json`.
This target runs in parallel with static `07B0` Brake + `0792` FRC acquisition;
neither replaces the other.

**Read-only opendbc scaffold is complete.** The initial passive TSS3 platform/DBC/CarState
landed in opendbc `6b124c546381350b8c7285980ffed3f14aef8f53` and kai-openpilot
`263b339480eabf8be242b486bd76f1df835241b2`. Follow-up opendbc
`fa1847d7ee66a221f2960ec5cf7a840e737ca521` adds exact-H `0x51E B0[7]` Ready Status for
read-only observation, and kai-openpilot `ddc6e532ecb8640d5771234b0017d84839e28ae2`
advances that submodule revision. The platform remains `dashcamOnly` + Panda `noOutput`;
the TSS3 controller emits no CAN and Ready has no fault/engagement policy. The tracked Span
rlog replays through that parser with 5,900/5,900 post-startup samples CAN-valid. Therefore **do not spend the next pass rebuilding basic state parsing**.
Use the implementation as the dynamic measurement harness and focus the next evidence on:
exact target/F181 binding, physical relay-correct stock-LTA transitions, **stock** B6 cadence
and active-LTA secondary-field template, slot4 MAC/key or live command-5 capability plus a target-native signer route,
the physical producer side plus suppression/isolation implementation, conservative driver-override policy calibration for the now-live `0x030`
torque, a deliberately chosen/validated `0x4A3` Q-current response policy, and
`0x351/0x394` fault transitions plus a `0x51E B0[7]` Ready `1->0->1` transition.
Ready's incoming wire source is no longer open; cruise availability/main/enabled/set-speed
is narrowed to the exact FRC P5 Data-ID oracle set above but still lacks a CAN-wire join.
Static firmware recovery has
already bounded the ~±8.238 N.m torque acquisition clamp and ±10 N.m telemetry
saturation as representation limits—not override thresholds—and found no measured-Q
comparator in the cooperative supervisor. The firmware limit ledger is tracked in
`data/generated/corolla_hf_steering_limits.json`; the numeric candidate Panda envelope
is `data/generated/corolla_hf_panda_lateral_safety_contract.json`. Keep it disabled
until those policy/deployment blockers close. Gear values other than the observed `D` and
cruise engagement remain deliberately neutral in the implementation until transition
captures justify them. Static/non-active engagement closure is machine-readable at
`data/generated/corolla_hf_nonsteering_engagement_state.json`; do not redo the basic
`0x51E`/`0x127`/inactive-`0x176` census.

## P0 — highest information gain

### 1. Inert H/F carrier canary, then live slot-4 command-5 permission

**Question:** does the exact-H/F target-native carrier actually survive the
boot-to-application transition and normal foreground scheduling, and only after
that, does provisioned ICU-S slot 4 permit command-5 MAC generation with usable
latency?

Why this matters: TMS-054 closes the remaining **static carrier-construction**
problem without pretending it is a live result. Exact H has a 464-byte candidate
pocket at `FEBF0000..FEBF01CF`: the first recovered normalized direct/simple-GP
reference is exactly `FEBF01D0`, MPU region 5 covers the pocket with supervisor
R/W/X (`0xB8`) in both recovered application contexts, and all listed
startup/MPU/command-5 prerequisites transfer byte-for-byte to F. A fixed B6-only
command-5 runtime links to **462 bytes** with entry zero / zero relocations, leaving
**2 bytes** headroom. A separate **332-byte** inert scheduler canary uses
`FEBFFB80` as an observation heartbeat and never calls command 5. The corresponding
60-byte signer mailbox `FEBFFB80..FEBFFBBB` is above H's startup shadow-copy end
and has zero recovered normalized direct references under the same bounded census.
Computed aliases, DMA/hardware ownership, and runtime lifetime remain outside that
static proof, so `data/variant_ram_exec_requirements.json` intentionally still has
no verified H/F entry. The August-18 range-dump acquisition had already established
working authenticated boot-RAM execution on Albino's car. VAR-049 adds a clean
same-car replay with direct F181 binding, exact zero-0201/0202 state, and terminal
CRC/CMAC state that reconstructs against pinned eps-telescope. Telescope still resets
from boot context afterward, so it does not answer the application-retention question
the canary is designed to test.

The live order is therefore fixed. First run the **inert H/F carrier canary** on
an isolated, firmware-identified H/F target and require `FEBFFB80` canary-signature/heartbeat
progression plus application F181 reappearance; then separately verify reset-to-stock
and ordinary application health before treating the carrier as usable.
Do not expose the signer if the canary fails or its observation cell is unstable.
Second, on a fresh isolated run, use
`exploit/ephemeral_runtime/corolla_hf_direct_command5.py`: it accepts live mode only
after a retained successful direct-canary result plus explicit reset-to-stock
confirmation, then installs the audited 462-byte fixed-36-byte proxy and tests
selector-4 command-5 permission against a known input without vehicle actuation.
The proxy self-initializes its request byte after stock startup/before `ei` and
mirrors the stock completion status into mailbox byte `+1`, eliminating the prior
installer-preinitialization/status-observability gap. Third, require independent MAC agreement. Fourth, measure completion latency/jitter while normal
command-7 verification traffic is present and show that the resulting sender
schedule fits the B6 timing contract. None of these stages authorizes vehicle
actuation.

Ready now:

- audited H/F inert canary:
  `exploit/ephemeral_runtime/audited/corolla_hf_runtime_canary.bin`
  (332 bytes, SHA-256 `a32baf46...97424f4`);
- audited H/F fixed-B6 signer:
  `exploit/ephemeral_runtime/audited/corolla_hf_command5_proxy.bin`
  (462 bytes, SHA-256 `3bb96eef...609f8d3`);
- deterministic target-native builder with compiler-equivalence protection:
  `exploit/ephemeral_runtime/build_corolla_hf_command5_carrier.py`;
- static geometry/build contract:
  `data/generated/corolla_hf_command5_runtime_carrier.json`;
- same-car authenticated boot-RAM execution was already implied by the retained
  August-18 range-dump acquisition; `community/albinoelephant/telescope/probe.json` /
  VAR-049 independently replays it with exact F181 and terminal payload-state joins;
- the first inert live test is now operationalized by
  `exploit/ephemeral_runtime/corolla_hf_direct_canary.py` / VAR-050. It builds the
  exact audited 4-KiB canary envelope (SHA-256 `313d1bb7...b0b29d84`), reproduces
  the telescope-observed old-stack bootstrap without post-auth substitution, and
  refuses to expose command 5;
- the second-stage slot-4 probe is now operationalized but remains hardware-gated:
  `exploit/ephemeral_runtime/corolla_hf_direct_command5.py` packages the hardened
  proxy into exact envelope SHA-256 `a9497970...e9d5a58`, requires the successful
  canary-result token plus reset-to-stock confirmation, commits mailbox state last,
  and requires mirrored status 0 / 16-byte non-sentinel output; it does not send B6;
- low-risk fixed-16 stock permission experiment under `exploit/command5/` remains
  useful as an independent policy control.

A DTC-only negative still does not separate command failure from expected-result
mismatch. On a separate fresh boot, selector 4 / mode 0 is the expected-negative
raw-AES policy control, but it needs its own result-source observer (`FEBE519A`;
the command-5 observer points at `FEBE51AA`) or equivalent status instrumentation.
The preferred positive exact-domain check is now the target-native proxy with a
known 36-byte B6-domain input after canary success; 7/12-byte cross-checks remain
useful for independently known SecOC vectors.

Canonical:
[../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md) ·
[../security/secoc/command5-oracle-assessment.md](../security/secoc/command5-oracle-assessment.md) ·
[../security/secoc/sender-implementation.md](../security/secoc/sender-implementation.md).

### 2. XCP physical reachability

**Question:** does the real bench/vehicle route deliver `0x7F7` to the EPS and
return `0x7F8`?

Why this matters: COM-005/007 already establish a powerful unauthenticated
application surface. If reachable, XCP immediately becomes the preferred
non-invasive dynamic observer for steering/SecOC experiments.

Ready now:

- CONNECT-only `exploit/followups/xcp_reachability.py`;
- bounded read probe;
- read-only DAQ profiles for actuation and diagnostic state.

First live step must remain CONNECT/read-only. Do not start by exercising the
F0/EC memory writers on a valuable ECU.

Canonical:
[../communications/xcp-command-dispatch.md](../communications/xcp-command-dispatch.md).

### 3. Acquire a foreign CodeFlash with steering SecOC profiles

The generic-transfer milestone is no longer artifact-blocked: tracked Corolla
`8965H1202000` independently resolves Gate-2, startup/scheduler, COM, and its
actual three-record SecOC queue. That image correctly reports the current
`0x2E4/0x131` steering bridge as unsupported, so the next acquisition should be
chosen for **applicability**, not merely foreignness.

The first command for any acquired EPS image remains:

```bash
tools/resolve_ephemeral_runtime_image.sh path/to/CodeFlash.bin \
  build/out/target-ephemeral-runtime.json
```

This one result tests Gate-2 transfer, callback-free startup/scheduler transfer,
SecOC queue/COM geometry, and whether exact image-bound RAM retention evidence
exists. Do not add a software-ID offset row to make a foreign image pass.

Span's persisted `8965F1208000` corpus is now closed through the unchanged
semantic/runtime resolvers, target-native SA/SecOC/steering comparison, and the
low-CodeFlash unit-calibration audit. Its remaining static question is narrow:
identify a semantic consumer for the structured `0x10000..0x17DEF` shadow bank
only if independent evidence supports one. The highest-value still-missing
images are `8965B4514000` or a blurbdust-supported F3/F4 calibration with an
independently observed steering profile. `8965H1202000` remains the
negative-capability regression and should not be counted again as an unresolved
transfer target.

Why this matters: the H image has already proved the semantic Gate-2/runtime
resolver can transfer without Sienna offsets. The next image can answer the
remaining higher-value question: whether the current steering bridge and its
retained-RAM geometry generalize to a second **applicable** EPS. It can also
advance MEM-SAFE-001, XCP, diagnostic-policy, command-5/8, boot-SA, and
provisioning comparisons.

Ready now:

- read-only dumper under `exploit/dumper/`;
- `tools/check_variant_acquisition.py` for geometry/SHA/provenance/readiness;
- structural scanner and semantic patch resolver.

Canonical:
[../tooling/variant-acquisition-readiness.md](../tooling/variant-acquisition-readiness.md) ·
[../variants/README.md](../variants/README.md).

## P1 — decisive hardware proofs

### 4. Gate-2 MAC28 causal proof

The corrected compare-neutralization patch and evidence pipeline are locally
complete. yc's 2026-08-16 RAV4 Prime field report strongly corroborates the
correct Gate-2 direction, but because it forced the older profile and used a
dummy key it does not isolate MAC28. The missing decisive result is still the
three-phase behavioral experiment on matching hardware:

1. stock baseline works;
2. MAC28-only ablation is rejected on the same stock firmware;
3. the same ablation is accepted after the semantically resolved Gate-2 patch.

Write/reboot success by itself is **not** proof.

Ready now: `exploit/behavioral_proof/` and the manifest patch/restore tooling.

### 5. Corolla H external/LTA command-provenance discriminator

Techstream has now closed the downstream H actuation question statically.
`EMPS_P5` monitor 402 `Command Value Torque` resolves to DID `0x1C02`, and the
same target-specific semantic join proves that state reaches DID `0x1152`
`Command Value Current (Q Axis)` through the real H current-reference pipeline.
Actual Q/D current and the selected Q-current limit are independently named and
mapped as `0x1151/0x1153/0x1156`. Another generic command→motor xref sweep is no
longer useful.

The pre-TSS3 Corolla comparison makes the generation break explicit rather than
treating older Toyota IDs as a loose search list. Both supported older Corolla
generations actively steer with 5-byte `0x2E4`; TSS2 `0x191` is only a neutral
coexistence frame. In H/F, `0x2E4` is gone while `0x025` survives as a 32-byte
FD steering-sensor interface. Albino H and Span F are byte-identical over the
full application region, so the split is common to both dumps.

The deeper state recovery now closes the most important current-route state hole.
Live `0x030` carries exact physical **Steering Wheel Torque** through signals10+31
(`0.1 N.m` coarse + signed `0.01 N.m` remainder), with 536 values from -8.23 to
+2.85 N.m in Span's 6,000-frame moving capture. Its B6[2] selected steering fault/inhibit status (not an exhaustive EPS-fault
state) and B6[0] torque-invalid gates are nominal-clear in all 6,000 frames. A GP-relative
writer correction also removes eleven false `default-init-only` classifications.
`0x4A3` is now the alternate torque/Q-current bridge (0.1 N.m/count and -0.01
A/count respectively). TMS-059 closes `0x030 B6[1]` to a Q-axis-current threshold/
debounce chain whose exact-H detector is calibration-disabled, and closes `0x351`'s
separate force-7 override to status-bitmap bits0/1 AND bit15 of a 24-record aggregate.
TMS-058 closes `0x394` substantially farther: all 242 populated-class DEM events are
partitioned into exact class/state families, named Toyota DTC families are joined where
present, and states 6/7 and 8/9 have exact 200/600-count latch-aging structure. State 0
remains the deepest clear/normal path, not a Ready boolean. Ready itself is now closed
on the **incoming** side: exact H `0x51E B0[7] -> FEBE7D1B -> FEBEF052 -> FEBEB5A8 ->
FEBEE811 -> DID 0x1033 Ready Status`, corroborated as value1 in both operational
routes. No EPS-Tx Ready duplicate is required for observation. Do not redo driver-torque
producer/scale, Ready-wire recovery, broad `0x394` class mapping, `0x030 B6[1]` source
tracing, or `0x351` force-7 source tracing. The remaining fault work is live policy
validation, not another static sweep.

COM-013 adds the whole-vehicle half that was previously missing. The public TSS3
Corolla route preserves useful old-state structure in `0x0AA/0x101/0x116/0x176`
and the exact-H-proved `0x025` fields. Span's moving rlog further restores `0x127`
as a checksum-valid gear reuse candidate and independently exercises those retained
state fields, while `0x1D3/0x260/0x262/0x343/0x399` remain unresolved. The surviving
`0x176/0x24D` cruise carriers are inactive in both routes, and exact FRC P5 diagnostic
oracles now define permission/main/operation/memory-speed/follow-distance semantics
without yet locating their CAN fields. Because neither vehicle-level route has an exact
F181 join and Span's harness was not physically repinned onto the relay pair, the
state-side priority is now a **firmware-identified, relay-correct H/F capture with stock
LTA and cruise transitions**, not another static EPS sweep: observe `0x4A3/0x351/0x394`,
exercise `0x51E Ready Status` through value0, synchronize the FRC P5 cruise **Data IDs** with
CAN, choose and validate a conservative Panda/openpilot driver-override policy from the
already closed `0x030` torque signal (TMS-053 finds no physical torque comparator in the
recovered target-to-motor control cone), and obtain an independent gear-state oracle plus P/R/N/B transitions. See
`data/generated/corolla_tss3_opendbc_readiness.json`,
[../variants/corolla-pre-tss3-openpilot-message-comparison.md](../variants/corolla-pre-tss3-openpilot-message-comparison.md),
and [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md).

The EPS receiver-side command question is now **closed positively**. The corrected
fixed-map/RTE audit resolves protected B6 signal255 from
`FEBE7D94 -> FEBEF1CC -> FEBEAE82`; `C9DB0/C9E54` build target state,
`CBD7E/CB096` independently reconstruct measured steering angle from FD `0x025`,
and `CA138` applies the same gain before forming target-minus-measured error. The
result reaches the cooperative steering controller, `C2A8`, general
`1C02 Command Value Torque`, and, under the recovered output gates, `1152 Command
Value Current (Q Axis)`. Companion B6 signal254 follows `7D96 -> F127 -> ADB0` and
selects mode families for values `1/4/10/11/19`; signals262/263 remain percentage-
like contributor modifiers. D7's command-sized field remains vehicle speed and the
B6 nonscalar/group/full-PDU alternatives remain negative.

The next H evidence is therefore **security/upstream-producer and production-limit
recovery**, not another request/validity/loss search inside the EPS. The physical
controller relation is closed: FD `0x025` signal184 is 1.5 deg/count, signal185 is a
signed 0.1-deg fraction, and B6 signal255 is `1024/17870 deg/count`
(`~1.000121519 mrad/count`) controller-equivalent. Techstream's `Target Lateral ID`
dictionary defines `0=No Request` and closes H's active signal254 IDs as
`PCS/LDA/Hands Off LTA/LTA-LCA/PDA`; H-special IDs `25/27` are `AP/Remote Parking`.
The dedicated receiver contract now also proves PDU42 reload/expiry at **7 TAUJ0-CH3
foreground ticks**, immediate cooperative cutout through slot18→`FEBEADB9`→`C26D`,
and B6 signal261 as a modulo-64 sequence counter with effective-gap cap `8`. TMS-053
closes CH3 at a steady **5.0 ms** after one 5.1-ms startup interval, so the primary B6
loss cutoff is nominally **35 ms**; Span's two-tick `0x030` cadence corroborates the
same timer. The full
receiver envelope is now exhausted too: B0..B27 are all authenticated, recovered EPS
application semantics occupy only 51 bits concentrated in B3..B10, another six bits
are extracted without a recovered downstream consumer, and the remaining 167
authenticated application bits have no recovered consumer under the bounded generic
COM/direct-reference census. B28..B31 are exactly FV4+CMAC28; full freshness is
`trip16||reset20||message8||reset_low2||00b`; the CMAC input is
`00 B6 || B0..B27 || freshness[6]`; and config/job0 selects ICU-S slot4. SECOC-071
now closes the remaining receiver policy too: reset trials are `current,-1,+1,-2,+2`,
B6's one same-PDU retry resolves the `±2` low-two-bit ambiguity, same-epoch message8
advances to the next congruent value by 1..4, `0x24` still proceeds to CMAC, authenticated
trip wrap clears linked B6 freshness state, and only command7 result0 commits pending
freshness before normal verified PDU42 delivery. Signal261 is a separate application
modulo-64 counter. CORR-111 retains the bounded failure-forwarding exception without
freshness commit. TMS-053 also closes the exclusive replacement-sender restart/progression
recipe: re-anchor on a newer authenticated `0x00F`, own B6 message8 locally, and wait for
the next epoch after sender restart; Toyota's B6-local counter-start policy is not needed.

Capture protected `0x0B6` during stock steering to validate **stock** sender wall-clock
cadence, secondary-field dynamics where needed, and normal target/rate bounds—not to
rediscover the receiver envelope, replacement freshness state machine, or verification
logic. In parallel, recover signing ownership and the slot-4 key value or live-validate
the audited TMS-054 H/F carrier path: 332-byte inert canary first, then the 462-byte
fixed-B6 command-5 proxy for selector-4 permission and latency. The Sienna resident
RAM geometry still does not transfer, and the H/F static pocket is not yet a verified
`variant_ram_exec_requirements` entry; receiver freshness extraction/window/retry/commit,
replacement message8 state, and key-slot selection are now closed. A category-435 CUW with
`Node01/DiagID=07B0` plus the matched `FRC_P5` image is now the primary software
target for the **remaining payload transform, sender cadence,
and routing/authentication ownership**, not for discovering the EPS setpoint/request/
loss contract; TMS-043 has already closed the module-level topology. For a Sienna-style
applicable EPS, separately retain the existing valid signed `0x2E4/0x131` command
experiment.

Canonical:
[../architecture/control-partition.md](../architecture/control-partition.md) ·
[../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md) §§7.34–7.36.

### 6. Passive command-8 / provisioning provenance

SECOC-047/048 statically close the second CAN-fed command-8 client and the
cross-bank completion-attribution bug. What is missing is production context:

- does RID `0x100E` / CAN `0x13..0x1A` appear during legitimate provisioning?
- how does dealer tooling interpret RID `0x1010` status `02` with zero proof?
- is any bank-0 terminal state externally observable?

Prefer passive capture of a legitimate flow. Do not synthesize random command-8
packages on the only original ECU.

### 7. Ephemeral SecOC scheduler bridge

The static architecture is now complete enough to stop searching for a stock
post-init callback. On `8965B4512000`, the pinned public encrypted RAM-dump
fixture already satisfies the exact authenticated 4 KiB payload gate with zero
DID-0201/0202 inputs; after its one successful `0x10F0`, MEM-SAFE-001 gives
boot-context RAM code. `FEBF0000..FEBF0307` is retained application-RWX, and the
pinned callback-free runtime fits there at 704 bytes with 72 bytes headroom.
The runtime reproduces stock startup, owns the TAUJ0-CH3 foreground schedule,
and bridges only marked zero-MAC `0x2E4/0x131` through stock
`application_com_rx_indication` after stock SecOC processing but before the
normal COM/system-mode/control task.

Highest-value next evidence, in order:

1. on an isolated bench, use `exploit/ephemeral_runtime/live_installer.py
   --variant canary --execute --bench-isolated` with an exact F181-bound route;
   it performs boot SecurityAccess, pinned-fixture `0x10F0`, MEM-SAFE
   substitutions, callback-last installation, FF00, application F181
   reappearance, and SID-`0x23` heartbeat-progression attestation in one command.
   If reset-to-stock is the property under test, then hard-reset and use the
   read-only heartbeat probe to prove the runtime disappeared;
2. prove one-shot marked-frame queue capture with no COM delivery;
3. enable stock-COM delivery and run the existing three-phase behavioral proof.

For another EPS calibration, first join its software ID against
`data/variant_bootstrap_profiles.json`: bootstrap reuse is already established
for multiple B4/F3/F4 targets, and tracked `8965H1202000` now provides a direct
field-observed foreign execution case. Keep that evidence separate from exact
encrypted-fixture identity, from per-image retained-RWX/scheduler geometry, and
from whether the resolved queue actually contains `0x2E4/0x131`.

Do not spend more static effort on generic callback hunting unless one of those
dynamic steps falsifies a concrete invariant. Canonical:
[../security/ephemeral-secoc-bypass.md](../security/ephemeral-secoc-bypass.md) ·
`exploit/ephemeral_runtime/`.

## P2 — useful when a specific dependency appears

- **Toyota-B direct-route confirmation:** the static root cause is now bounded.
  If an affected car is available, compare stock-pin `ELM param 1 + bus 1`
  against the OBD route while recording Panda CAN health and post-`10 02`
  endpoint reappearance. This is useful to distinguish gateway/timing from
  ACK/bus-off behavior; do not physically repin merely to answer the diagnostic
  question. The test does not replace the CAN0/CAN2 relay topology needed for
  normal openpilot interception.
- **Reset-window replay / future-sync poisoning / tag-guess throughput / FD
  suffix behavior:** host trial constructors exist; run on an isolated bench
  when SecOC behavior itself is the active question.
- **Live stale-RDBI confirmation:** easy and bounded, but lower strategic value
  than the P0/P1 discriminators.
- **CommunicationControl availability experiment:** reversible and ready; useful
  for availability characterization, not a steering primitive.
- **Command 13 characterization:** only interesting as a possible Renesas SHE
  deviation; standard SHE already closes the old nonvolatile-key-export idea.
- **Power/EM / fault injection:** fallback paths after software/vehicle-side
  options are exhausted and physical topology is confirmed.

## Static work that remains worthwhile

Use the exploit-interest cohorts selectively. The reviewed-candidate ledger
`data/exploit_interest_reviewed_candidates.csv` prevents already-audited
functions from resurfacing as unexplained hits. New static work should have a
specific exploit hypothesis, externally reachable sink, or variant-transfer
question.

Tracked Corolla `8965H1202000` now has both a whole-image exact-body census and
an address-independent structural transfer pass, so its remaining static work is
**target-native**, not another Sienna-offset sweep. The first H-specific gaps are
already closed: XCP read/write/E4 semantics were re-proved in H decompilation;
the SecOC verify algorithm was recovered over H's different `00F/D7/B6`
profile set; and the motor-control chain is anchored from H scheduler through
d/q/phase processing to the TSG3 hardware boundary, with the larger steering
pipeline at `0xCEDAE` calling the recovered clamp/rate stages. Target-native
startup/COM recovery also closes the old classic-CAN assumption: app GP remains
`FEBEB800` but TP is `23D6C`; normal Rx drops `2E4/131` and adds secured FD
`0B6`; the old `2E4` request cell is periodically forced to zero; and Tx replaces
`260/262` with a 32-byte FD `030`. The application diagnostic surface is now
re-censused target-natively too: H has 226 readable DIDs / 32 exact-stub stale
selectors and the same 19 RoutineControl policy rows, but `110A/C/D` become no-op
while `110B` becomes a new active lifecycle. The former FD replacement-command negative is now corrected by the fixed-map/RTE
audit: `025` remains shared sensor state, but B6 signal255 is a live signed16 target-
steering-angle command that the direct-reference census missed because
`B8EEC` copies `FEBEF1CC -> FEBEAE82` through GP-relative addressing. Signal254
similarly reaches `ADB0` as the cooperative mode/control ID. The complete corrected
COM→snapshot→`0xCEDAE` census therefore has exactly one H-only/wire-changed field
at least 12 bits in the command cone — B6 signal255 — while the shared large fields
remain `0x025` angle/rate sensor state and no second nonscalar/group/full-PDU command
surface is recovered. The separate retained Sienna `0x2E4` clamp input remains
zero-fed; that does not describe the B6 target-angle controller. Separately, all `00F/D7/B6` SecOC profiles use config
ID/job 0 and select one protected ICU-S **slot 4**; the raw key is opaque to the
mapped CPU command-7 path, while authenticated command 8 is the recovered refresh
interface. The remaining H-static work should therefore be driven by the named
coverage denominator. The first large residue is now closed: all eight changed
`scheduler_system` roles are target-native mapped, reducing the global genuinely
unresolved denominator from 462 to 454. The nine changed CAN/COM transport roles
are now also target-native closed, reducing the residue again to **445** and
leaving zero genuinely-unresolved functions under both `scheduler_system` and
`can_com`. The three changed storage/NvM roles are now also closed, including the
object-15 protected geometry and invalid supplied object-15 snapshot, reducing the
global residue again to 442 and `storage_nvm` unresolved to zero. The four XCP
command-handler gaps are now also closed—including H-specific F5 exclusion ranges
and surviving EB/EA state—reducing the residue to 438 with `xcp` unresolved
zero. The five remaining motor-control roles are target-native closed, and the full
42-function SecOC/ICU-S residue is now closed as well, including the lower
command5/7/8 adapters, freshness graph, Rx ingress, ICU ISRs, crypto-test callbacks,
and regenerated D7 unpacker. `secoc_icus` unresolved is zero, overlapping
`crypto`, `steering`, and `diagnostics` unresolved are now **zero**. The canonical
1,113-function named denominator is now also **zero genuinely unresolved**. The former 96 structural-only rows are now all target-native inspected as well,
so no shape-only coverage residue remains. New static work should be initiated only
by a concrete target-native semantic, externally reachable, runtime, or exploit
question; do not restart a broad Sienna-offset sweep. Generic XCP DAQ callbacks
remain optional unless a concrete exploit question needs them. For
`8965H1202000` specifically, undirected comparative CodeFlash analysis is now a
closed task: remaining variant questions require runtime, ICU-S-internal,
route-identity, or foreign-firmware evidence.

The remaining explicitly open cohort rows without a recovered ingress root are
not reason enough for another broad sweep by themselves.

## Do not repeat without new evidence

These directions have reached diminishing returns or have already been closed:

- another generic whole-image decompilation/semantic sweep;
- generic authenticated-command → d/q xref searching without a new concrete
  bridge;
- direct-reference searches for an XCP-window execution consumer using the same
  existing graph;
- interpreting the compiled-out `FF*16` KAT as the live slot-4 key;
- treating object 15 as proof of the current live ICU-S key;
- treating command 13 as a standard SHE nonvolatile-key export route;
- building software-ID → patch-offset lookup tables instead of improving the
  semantic resolver.

## When this page changes

Update this file only when the **execution order** changes. If an item is
resolved, move the result to the appropriate subsystem report / `FINDINGS.md`
and remove it here instead of appending a completion diary.
