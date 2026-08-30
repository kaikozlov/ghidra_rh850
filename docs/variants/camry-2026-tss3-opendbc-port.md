# 2026 Camry TSS3 passive + historical-development openpilot/opendbc port

**Target:** maintainer 2026 Toyota Camry Hybrid, EPS application F181
`8965F3307000 / 8A3113303100`.

**Evidence boundary:** this report closes the exact-F33 generated-COM transmit geometry needed by the software port, records the passive implementation, and preserves the former Gate-2 development path as historical/test-only engineering context. It does **not** authorize steering transmission. CORR-129/VAR-081 identify **73.303384 s of retained `0x08A` ID11 LTA/LCA request state with zero B6**; this is not a direct winner/grant oracle. CORR-134 recovers B21 as Target Lateral ID and B18:B19 as the signed request-angle quantity; CORR-135 rejects a presumed `0x08A -> B6` transform. Exact F33 neither accepts `0x08A` nor transmits it, while its B6-inactive internal path reaches physical steering; that makes zero B6 architecturally possible but does not prove the retained request was granted. VAR-091/CORR-136 place authenticated `0x08A` on captured Bus 4 and observed plaintext camera PDUs on Bus 1, but batched rlog timestamps cannot identify the physical transmitter and Bus-1 trailer absence cannot identify the signer or FRC HSM capability. VAR-094 proves only that consecutive `5282` is absent from native Bus-1 CAN; CORR-138 retracts the former standing-echo interpretation of `0x160[22]`.

The remaining integration problem is split deliberately. OQ-054 tracks physical `0x08A` transmission, private transport, and SecOC computation ownership; current evidence permits FRC pre-authentication or CGW/Skid/Brake assembly/signing. Synchronized FRC Operation FFD `5282/5285/57DE/5265` separately determines request versus winner/grant. VAR-092 closes default-bank `D0218` as not an F33 COM copy of the published milliradian. Protected B6 remains a real external cooperative-control ingress and a separate candidate openpilot interface. Production use still needs a signing/freshness contract, but that is not a prerequisite for the development path: VAR-060 already supplies a deterministic exact-F33 Gate-2 compare-neutralization plus CRC repair, so a patched/bridged EPS can accept deliberately zero-MAC28 B6 frames. The old stock-template B6 runtime sender was removed in `opendbc@b9e86924` and `kai-openpilot@abf3ca70a`; the development task is to deploy/arm the acceptance bypass and correctly enable the fork sender, Panda safety, suppression/relay, and bounded live-test path rather than infer anything from stock LTA.

**Physical routing decision (CORR-139):** the present Toyota-B repin is correct.
Current GTS+ places Brake/Skid/SAS/EPS together on Toyota Bus 4; exact F33 has one
application CAN controller carrying both its B6 rule and diagnostic rules; the
relay-correct capture observes exact-F33 `0x030` and EPS UDS on the repinned
steering family. Therefore the candidate external-control route is `0x0B6`,
DLC 32, on **Panda bus 0 across the current CAN0/CAN2 relay pair**. Panda bus 1
remains the native FRC/camera-radar plane. Do not send `0x08A` to EPS, do not infer
an `0x08A -> B6` transform, and do not repin again in search of an EBU-private EPS
stub: the telemetry/carrier absences in VAR-099 are not a routing discriminator.
The next integration gate is not discovery of B6 receiver authentication: VAR-060's
exact-F33 Gate-2 patch and deterministic CRC repair already make deliberately
zero-MAC28 development frames admissible on a patched/bridged EPS. What remains
is deployment/arming, correct fork sender and Panda-safety enablement, required
source-suppression/relay behavior, and bounded live-response validation.
Production transmission remains unauthorized.

Working session notes for the GTS+ vehicle-type → install-set → family-`.ddb` → GetSupport funnel (not a claim ledger): [../history/2026-08/CAMRY_GTS_LATERAL_FUNNEL_2026-08-29.md](../history/2026-08/CAMRY_GTS_LATERAL_FUNNEL_2026-08-29.md).

## 1. Exact F33 generated-COM Tx carriers

The exact normalized `8965F3307000` CodeFlash (SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`) closes the
first five application generated-COM Tx descriptors at `0x21F58`:

| PDU | CAN ID | FD | PDU descriptor | Signals |
|---:|---:|:---:|---|---|
| 0 | `0x030` | yes | `(2,0,0,32,0,3)` | `0..37`, `283` |
| 1 | `0x351` | no | `(200,0,0,4,0,3)` | `38,39` |
| 2 | `0x394` | no | `(60,0,0,3,0,3)` | `40..43` |
| 3 | `0x4A3` | no | `(100,0,0,8,0,3)` | `44..51` |
| 4 | `0x4C8` | no | `(196,0,0,8,0,3)` | `52..55` |

The target signal-to-PDU table is `0x22488`, the PDU table is `0x226C0`, and the target
has 284 configured signal IDs. Target-native generic Tx scalar packer `0x7D1DC` indexes
that same signal map through `TP-0x1974`.

### 1.1 `0x351`

The target-native chain is:

- debounce/state preparation `0x4C1C0`;
- force/status producer `0x4C216`;
- packer `0x4CED0`.

`0x4CED0` packs signal 38 to `B2[7:5]` and signal 39 to `B2[4]`, then submits PDU1.
This closes the F33 wire projection, but not an openpilot temporary/permanent fault
classification. In particular, the force-7 path is not renamed as an old `LKA_STATE`.

### 1.2 `0x394`

The target-native projection/packer pair is `0x4C24A -> 0x4CE08`. PDU2 carries four
lossy state-table columns:

- `B1[7:6]`: column 4;
- `B1[5:3]`: column 1;
- `B2[3:1]`: column 2;
- `B2[0]`: column 3.

The exact H/F work already established the analogous 17-state classifier semantics, but
this F33 closure deliberately does not equate the deepest clear state with Ready or map
any numeric class to openpilot `steerFaultTemporary`/`steerFaultPermanent` without a
same-car asserted/recovery transition.

### 1.3 `0x030`

The target-native chain is `0x4C490 -> 0x4C97A` (PDU0, 32 bytes, CAN FD). Wire
geometry is derived from the pinned per-PDU slice-offset table at `0x22840`
(`FUN_0007d05c` copies each PDU out of the shared pack buffer at `FEBE4A48`;
`FUN_0007d31e`'s second argument is an absolute buffer byte offset, so wire bytes =
buffer offset - slice offset; PDU0 slice offset is 0):

- `B8` (signal 11): coarse signed steering-wheel torque, 0.1 N.m/count;
- `B17[3:0]` (signal 30): signed decimal digit, 0.01 N.m/count;
- combined: `signed8(B8)*0.1 + signed4(B17[3:0])*0.01` N.m;
- `B22:B23` (signal 33): **signed big-endian 16-bit mapped motor-feedback proxy**.

The `B22:B23` source chain is now target-natively closed: `0x37E48` forms dual-channel
feedback sums into `FEBE6D70` plus an extended Q-axis sum `FEBE6D78` (whose saturated
i16 `FEBE6D72` is the DID `0x1151` upstream source); `0x38678` maps
`abs(FEBE6D78)` through a lookup table conditioned by the sibling axis `FEBE6D70`;
`0x3879E` publishes the mapped result to `FEBE6E00`; `0x59448`/`0x5D12C` mirror it to
`FEBE6718` (GP-0x50E8, the same cell `0x4A3 B6:B7` reads); `0x4C490` stages
`signed16(((-FEBE6718 * FEBEE8D8) / 0x100) * 100 / 0x2000)` into `FEBE816C`; and
`0x4C97A` packs it at `B22:B23`. It is therefore a **motor-current-family feedback
proxy sharing DID1151's pre-clamp Q-axis aggregate**, but not DID1151 in wire units:
the sibling-axis-conditioned lookup and the runtime scale (`FEBEE8D8`, written at
runtime by `0xBF3AA`/`0xBF97A`) intervene. A second staging-cell writer `0x58C9A`
also writes `FEBE816C`; it is bounded with no semantic claim. Treat `B22:B23` as a
signed motor-feedback/assist proxy — never as amperes, commanded torque, or lateral
authority: driver EPS assist also creates current. The two-drive bounded correlation
of this field lives in the live-baseline report §24 (VAR-072).

### 1.4 `0x4A3`

The exact F33 chain is `0x4C000 -> 0x4C14E -> 0x4C7AA` and is materially better evidence
than transferring the H/F packer by shape.

`0x4C000` prepares the physical sources. `0x4C14E` stages the eight wire bytes, and
`0x4C7AA` packs global signal IDs 44 through 51 and submits PDU3. The recovered wire
geometry is:

- `B0[5]`: marker/status bit;
- `B0[0]`: selected steering fault/inhibit status;
- `B1[3:0]:B2`: signed12 coarse steering-angle source, 1.5 deg/count;
- `B3[3:0]:B4`: signed12 filtered/voted steering-angle quantity, 1.5 deg/count;
- `B5`: steering-wheel-torque telemetry at 0.1 N.m/count after F33 source staging;
- `B6:B7`: signed16 alternate motor-current telemetry from
  `(GP-0x50E8 * -100) / 0x80`.

The distinct `0x4A3` alternate-current source `GP-0x50E8 = FEBE6718` has four
direct references: readers `0x4C000/0x4C490` and writers `0x59448/0x5D12C`. The
`0x030 B22:B23` field reads this same cell, and its upstream is now closed (§1.3,
§2): `GP-0x50E8` is a nonlinear sibling-axis-conditioned map of the same extended
Q-axis sum that saturates into the DID1151 source. The packed fields therefore remain
structurally named (`MOTOR_CURRENT_ALT`, mapped motor-feedback proxy) — not because
the source relationship is unknown, but because the lookup and runtime scale mean the
wire values are not DID1151 units, amperes, or commanded torque.

## 2. Canonical first-class source-reference census

The earlier scratch-project census evolved in two steps: VAR-056 initially found four
direct/fixed-GP driver-torque users, and CORR-120 added `0x4C000` as a fifth after
recovering the `0x4A3` telemetry producer. Both counts are now historical. The
first-class F33 project seeds the target-native GP from `0x715B4` and exports the
canonical Ghidra data-reference graph across **6,065 recovered functions**, so the
source census no longer depends on textual `unaff_gp` spelling.

For driver torque `GP-0x5158 = FEBE66A8`, the exact direct-reference set is **nine**:

- readers: `0x35A06`, `0x4C000`, `0x4C490`, `0x4DB70`, `0x52CA0`, `0x54244`, `0x564CE`;
- writers: `0x59448`, `0x5D5E0`.

For DID1151 Q-current `GP-0x50F2 = FEBE670E`, the exact direct-reference set is
**six**:

- readers: `0x4E394`, `0x52CA0`, `0x54244`, `0x564CE`;
- writers: `0x59448`, `0x5D12C`.

The distinct `0x4A3`/`0x030` mapped-current source `GP-0x50E8 = FEBE6718` has four
direct references: readers `0x4C000/0x4C490` and writers `0x59448/0x5D12C`.

The `0x030 B22:B23` upstream is now census-closed as well: the mapped feedback
`FEBE6E00` (GP-0x4A00) is written only by `0x3879E` and read by `0x57FD2`,
`0x59448`, `0x5D12C`; the extended Q-axis sum `FEBE6D78` (GP-0x4A8E) is written by
`0x37E48` and read by `0x375C2`-family consumers including the `0x38678` map input;
the DID1151 pre-clamp cell `FEBE6D72` is written by `0x37E48` and read by `0x37F92`,
`0x59448`, `0x5C7B6`, `0x5CA3A`, `0x5D12C`; and the `0x030` runtime scale
`FEBEE8D8` is read by `0x4C490` and written at runtime by `0xBF3AA`/`0xBF97A`.

The safety-relevant negative is unchanged and is now stronger: **none** of the direct
references to `FEBE66A8` or `FEBE670E` lies in the cooperative `C8xxx-D1xxx`
target-to-motor control cone. Computed aliases without a Ghidra data reference, DMA,
hardware mutation, and unrecovered code remain outside that bounded negative.
CORR-122 records why the old textual 4→5 census was incomplete.

## 3. Passive software implementation

The corresponding implementation is retained in:

- nested opendbc commit
  `ab60fd95d8a7b566e10ed1cf59738292f3498932` (`toyota: add passive Camry TSS3 lateral stack`);
- parent `kai-openpilot` commit
  `d7d7dfd7e49961e9d35eb7a7681e8756ceee8d04` (`toyota: advance passive Camry TSS3 port`).

### 3.1 Exact platform identity without an ambiguous legacy CAN fingerprint

The port adds `TOYOTA_CAMRY_TSS3` and a byte-exact EPS F181 discriminator for
`02 || 8965F3307000[16] || 8A3113303100[16]`. Known FRC and Brake identities are
corroborating constraints: if present, they must not conflict.

The retained same-car normal-harness CAN census contains a **179-ID** census. It is deliberately
*not* registered as a legacy CAN fingerprint because the current Corolla TSS3 fingerprint
is a **147-ID** set and is a strict subset of the Camry census. Registering both would
make Corolla identification order-dependent/ambiguous. The Camry census remains available
for topology and replay evidence while F181 performs the target binding.

### 3.2 Same-car CarState replay

The dedicated Camry tests replay source-real retained payloads for:

- `0x025` steering angle/rate;
- `0x030` driver-torque/status telemetry;
- complete `0x127` selector transitions: `P=0, R=1, N=2, D=3, B=4`;
- `0x51E B0[7]` Ready 0/1.

`0x4A3`, `0x351`, and `0x394` are parsed as static/presence-bounded internal inputs.
Their absence is distinguished from a real all-zero packet. They are not required for
CAN-alive checking and are not yet mapped to public openpilot fault policy.

VAR-088 completes the `0x08A` `TSS3_LATERAL_REQUEST` DBC entry with the full
census-bounded field set — cruise latch/sub-state mirrors, the byte-identical
duplicated signed16 request word, set speed, `0x7FFF` sentinel slots, the
cooperative substate flag, the 0/50/100 request level, and the `FV4+MAC28`
trailer geometry — plus the full 19-value Target Lateral ID dictionary on both
`0x08A` and B6 (live-baseline §39). These remain passive observables; the
producer/security and stock-LTA authority questions of OQ-054 are unchanged.

### 3.3 B6 candidate construction and freshness/signing interfaces

The passive stack now has deterministic code for the exact known B6 contract:

- explicit 28-byte application template preserving unresolved bytes/bits;
- Target Lateral ID, signed target angle, secondary recovered scalar fields, and
  modulo-64 application sequence;
- FV46 construction and FV4 projection;
- full CMAC128 signer interface with transmitted MSB28 trailer;
- signer status/latency instrumentation;
- replacement freshness state that accepts the first authenticated `0x00F` only as a
  baseline and arms only after a **strictly newer authenticated sync epoch**.

The default application template is intentionally marked `stock_validated=false`.
No zero-filled candidate is represented as Toyota stock behavior.

### 3.4 Passive default remains mechanically non-enabling

The ordinary TSS3 controller path still computes a shadow B6 application and F33 safety
decision for unit/replay inspection while returning **zero CAN frames**. The platform's
CarParams remains `SafetyModel.noOutput`; ordinary Toyota safety modes do not whitelist
`0x0B6`. The former interface/card development configuration path has been removed, so no
current CarInterface/CarController runtime switch can arm B6 output.

## 4. Historical exact-F33 Gate-2 development plumbing (VAR-062; runtime path removed)

The original fail-closed experiment was staged in opendbc
`dde0fcf0fbaf875750c54a072b0dcb3857f8829b` and parent kai-openpilot
`15f3550365e2eee54ca5645ae9c24d9d41ae4f31`. After VAR-081/CORR-134 disproved the
stock-template integration shape, the runtime hook was removed in `opendbc@b9e86924`
and `kai-openpilot@abf3ca70a`; current opendbc `525ee987` keeps the lower-level receiver,
freshness, packer, and debug-safety helpers only for deterministic analysis/tests.

### 4.1 Historical admission contract

For provenance, the removed runtime path required `ToyotaTSS3DevLateral` plus
`ToyotaTSS3DevLateralConfig` to provide all of the following:

- exact `f181 = 8965F3307000`;
- a **28-byte `b6_template_hex` claimed to come from relay-correct stock LTA**;
- measured `cadence_frames` in the 1–3 control-frame range;
- `gate2_bypass_validated=true` after an exact-F33 invalid-MAC causal proof;
- `exclusive_b6_authority_validated=true` after relay/source-suppression proof.

Those params and the CarInterface/CarController sender hook no longer exist. No stock B6
template/cadence appears during the retained ID11 request intervals, so the old admission
contract is historical evidence only and must not be revived by inventing a template or
weakening its gates. OQ-054's `0x08A` transmitter/signer question is separate from B6:
resolving the request publisher does not establish a transform into protected B6 or select
the openpilot actuation interface.

### 4.2 Historical development sender is deliberately not a production signer

Under its original experimental contract, after all gates above are supplied, the controller uses the existing exact-F33
replacement-freshness machinery. The first observed stock `0x00F` is baseline only; a
**strictly newer** epoch arms message counter 1 / application sequence 0. Active output is
Target Lateral ID 11 only. Target angle is clamped to ±1745 raw and each emitted command
is clamped to ±78 raw from the prior command. The 28-byte stock template is preserved
outside recovered fields. The four-byte trailer carries the correct FV4 nibble but an
**intentionally zero MAC28**, because this path exists only for the already-live-validated
Gate-2 bypass experiment.

On active→inactive, the controller emits **no invented OEM inactive packet**. It stops B6,
disarms replacement freshness, and requires a newer stock sync epoch before another
activation. That intentionally leaves exact disengage/restart packet semantics to the live
stock capture rather than encoding a guess.

### 4.3 Historical/debug Panda B6 safety mode is test-only and fail-closed

`ToyotaSafetyFlags.TSS3_DEV_LATERAL` still exists behind Panda `ALLOW_DEBUG` so the
recovered B6 envelope can be regression-tested, but no current Camry CarParams,
CarInterface, or CarController runtime path selects it. If explicitly selected by a debug
test, it installs a dedicated TX whitelist containing exactly bus-0 `0x0B6`, DLC 32, with
relay checking. The hook requires prior bus-0 `0x025` steering-rate and `0x00F` sync
observations and enforces the statically recovered F33 envelope:

- active Target Lateral ID exactly 11;
- absolute target ≤1745 raw;
- absolute steering-rate raw ≤100;
- modulo-64 sequence exactly +1 after the first accepted command;
- target step ≤78 raw;
- active inter-command timeout ≤35 ms.

Only a **strictly newer** stock `0x00F` epoch resets Panda's command-history
baseline; stale or backward epochs do not. No legacy Toyota TX message is admitted by
this development safety mode. Targeted regression coverage
includes the existing passive/no-output path plus actual Panda hook tests; the Toyota
safety module currently passes 283 tests with 34 skips in the local targeted gate.

## 5. What remains before lateral output can actually be exercised

The critical remaining work is **not** a presumed `0x08A -> B6` producer chain:

1. **Discriminate request from grant.** Capture FRC Operation FFD `5282/5285/57DE/5265` synchronized with `0x08A`, `0x025`, `0x030`, and the B6 count. Current logs prove ID11 request state, not an autonomous winner/grant.
2. **Resolve `0x08A` ownership with source-capable evidence.** Exact F33 is excluded and consecutive `5282` is absent from native Bus-1 CAN. Batched rlog cadence and plaintext Bus-1 trailers cannot choose FRC pre-authentication versus CGW/Skid/Brake assembly/signing. Use exact candidate firmware, private-link dataflow, or source-identifying physical capture. Do not send `0x08A` to EPS.
3. **Choose and validate the openpilot ingress separately.** Protected B6 is a genuine exact-F33 external angle ingress; the audited zero-MAC28 receive bridge is a static candidate, not live authorization. Validate stationary zero-angle acceptance, driver override, motor-current response, source suppression/fallback, and normal/inhibit/fault/recovery before leaving `noOutput`.

The historical `TSS3_DEV_LATERAL` B6 sender/safety work remains useful only as a bounded receiver/envelope experiment. It is not evidence that stock Camry LTA uses B6 and is not a reason to revive the removed runtime hook.

## 6. Deterministic evidence

- `data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json`
- `data/generated/camry_8965F3307000_tss3_opendbc_port.json`
- `data/generated/camry_8965F3307000_external_lateral_ingress.json`
- `data/generated/camry_2026_motor_feedback_correlation.json`
- `data/generated/camry_2026_lta_state_reconciliation.json`
- `data/generated/camry_2026_08a_producer_bounds.json`
- `tests/verify_camry_8965F3307000.py`
- `tests/verify_camry_2026_lta_state_reconciliation.py`
- `tests/verify_camry_2026_08a_producer_bounds.py`
- `tools/decode_camry_tss3_operation_ffd.py`
- `tests/verify_camry_tss3_operation_ffd_decoder.py`

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [VAR-058](../reference/index.md#finding-var-058), [VAR-061](../reference/index.md#finding-var-061), [VAR-062](../reference/index.md#finding-var-062), [VAR-071](../reference/index.md#finding-var-071)
- Corrections with this document as canonical home: [CORR-120](../reference/index.md#correction-corr-120), [CORR-122](../reference/index.md#correction-corr-122), [CORR-139](../reference/index.md#correction-corr-139)
<!-- knowledge-cross-references:end -->
