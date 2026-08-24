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
vehicle-network effect of those routines. The ADS_Eth_P5 target-angle order
rows (406/407, rad/s and rad via
the PhyData→Unit chain) are recorded-snapshot evidence, and a 402-file corpus
scan proves the `0x1CEE/0x1CEF` steering-observer **type-62 primary Data-ID
declarations** occur only in `EMPS_P5`/`EMPS2_P5` — exact Corolla H
implements neither.

**Next software-analysis target:** acquire and analyze **`FRC_P5` camera
firmware** (Front Recognition Camera 2) for a true-TSS 3 vehicle and recover
its lateral-control producer contract: which in-vehicle message(s) carry the
LTA target state, and whether/where they join the EMPS/EMPS2 steering
observer domain. TMS-042 makes the same acquisition the highest-value
reprogramming target too: modern GTS+ proves the FRC `ReproMethod=07` path
uploads the package routine with DFI `0x01` / `10F5`, then the compact
`DeltaReproData` with DFI `0x21` / `10F6`, while the host treats `.datx` as
opaque bytes. A matching FRC boot/programming image is therefore the missing
consumer that can explain both the routine/blob transform and the delta
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

The community `NEW_MSG_8A_LAT_CONTROL` heatmap is a high-value lead because it
independently names torque/target-angle/confidence-like fields, and the
Reference screenshot corpus (REFERENCE/CorollaExp_Screenshots.md) records
`0x18A` as one of 22 CAN-FD 64-byte IDs observed on buses 0 and 2 — nothing
more is pinned by that artifact. No bit/name/producer/authentication join to
`FRC_P5` is proven. Do not encode it in a DBC from the screenshot alone;
treat it as the candidate wire hypothesis the FRC firmware pass must confirm
or refute.

Canonical: [../tooling/techstream.md](../tooling/techstream.md) §6.2.2 ·
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) ·
[../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md) §7.35.

## P0 — highest information gain

### 1. Live slot-4 command-5 permission

**Question:** does provisioned ICU-S slot 4 actually permit command 5 MAC
generation in initialized application context?

Why this matters: SECOC-070 removes the remaining software-call problem. A
546-byte RAM-only application runtime now invokes serialized command-5 driver
record 0 with fixed selector 4 and caller-chosen `0..80` byte input, including
the exact 7/12/36-byte SecOC domains. It needs no persistent CodeFlash hook or
per-request application SecurityAccess; only the already-solved authenticated
bootloader-RAM foothold is required to install it. A positive hardware result
would therefore validate the final cryptographic permission assumption for the
resident signer.

Ready now:

- low-risk fixed-16 stock permission experiment under `exploit/command5/`;
- deterministic 546-byte RAM proxy under `exploit/ephemeral_runtime/`;
- variable-length XCP mailbox planner / guarded live client in
  `exploit/command5/ram_proxy.py`;
- clean driver record 0 completion path, fixed slot 4, and busy/defer arbitration;
- exact 7/12/36-byte inputs once the RAM proxy and XCP route are live.

Stage-1 positive criterion: current-run generated output changes from the
pre-stimulus baseline under selector 4 / mode 1. A DTC-only negative does not
separate command failure from expected-result mismatch. On a separate fresh
boot, selector 4 / mode 0 is the expected-negative raw-AES policy control, but
it needs its own result-source observer (`FEBE519A`; the command-5 observer points
at `FEBE51AA`) or equivalent status instrumentation; the DTC alone is ambiguous.
Only after stage 1 succeeds, the preferred exact-domain test is the RAM proxy
with a known 12-byte classic authenticated input; compare its first 28 generated
bits against an independently known classic SecOC tag. The older `0x68B8A`
`16→12` CodeFlash adaptation remains a fallback experiment, not the preferred
path.

Canonical:
[../security/secoc/command5-oracle-assessment.md](../security/secoc/command5-oracle-assessment.md) ·
[../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md) ·
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

The remaining H question is **external autonomous-lateral provenance**, not
ordinary EPS torque provenance. The dedicated static census now closes the
EPS-local escape hatches: the retained Sienna-homolog LTA magnitude cells and
mode source are direct-write zero/inactive; D7's only 16-bit scalar is
Techstream `CAN Vehicle Speed (SP1)`; B6's sole 16-bit scalar is staged-only and
its nonscalar rows have no recovered block/group/full-PDU/direct-literal
consumer; and the only shared supervisor-reaching >=12-bit fields on CAN `0x025`
are target-natively proved steering angle/rate sensor state. `1C02` is a general
internal torque-command observable with local assist contributors, so watching
it alone cannot identify stock LTA.

The next H evidence must therefore be same-vehicle dynamic correlation: capture a
known stock-LTA steering interval on **all genuine incoming buses** while reading
`1C02`, `1152`, and the retained/H-native upstream mode/contributor cells with
read-only XCP/DAQ if reachable. Look for a state transition that precedes the
increment attributable to autonomous steering. If no EPS-local precursor moves,
the next firmware target is the camera/gateway/other steering controller rather
than another generic pass over this EPS image. For a Sienna-style applicable EPS,
separately retain the existing valid signed `0x2E4/0x131` command experiment.

Canonical:
[../architecture/control-partition.md](../architecture/control-partition.md) ·
[../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md) §§7.34–7.35.

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
while `110B` becomes a new active lifecycle. The obvious FD replacement-command
hypothesis is now bounded negative: `025` is a shared pre-existing FD interface;
B6's only signed16 scalar is staged-only under the complete direct-reference
census; active B6 fields are supervisor gate/mode/sequence/scaling state; and the
retained Sienna-shaped clamp input is zero-fed while `AE20` is an internal
plausibility/status branch. The two remaining high-value H gaps identified there
are now also closed at the
firmware-static boundary. A complete generated-COM→snapshot→`0xCEDAE` ingress
census finds no H-only/wire-changed scalar ≥12 bits and no changed shared-CAN
field in the mapped supervisor cone; all changed surviving fields are sub-12-bit
`0x0B6` supervisor state. Separately, all `00F/D7/B6` SecOC profiles use config
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
