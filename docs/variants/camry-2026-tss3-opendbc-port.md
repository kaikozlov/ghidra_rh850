# 2026 Camry TSS3 passive + historical-development openpilot/opendbc port

**Target:** maintainer 2026 Toyota Camry Hybrid, EPS application F181
`8965F3307000 / 8A3113303100`.

**Evidence boundary:** this report closes the exact-F33 generated-COM transmit geometry, the default-passive software integration, and the current development-only B6 sender/safety envelope. It does **not** authorize steering transmission. CORR-129/VAR-081 identify **73.303384 s of retained `0x08A` ID11 LTA/LCA request state with zero B6**; this is not a direct winner/grant oracle. CORR-134 recovers B21 as Target Lateral ID and B18:B19 as the signed request-angle quantity; CORR-135 rejects a presumed `0x08A -> B6` transform. Exact F33 neither accepts `0x08A` nor transmits it, while its B6-inactive internal path reaches physical steering; that makes zero B6 architecturally possible but does not prove the retained request was granted. VAR-091/CORR-136/CORR-149 place authenticated `0x08A` on captured Bus 4, observed E2E-only camera/radar PDUs on Bus 1, and exclude the FRC from the TSK signing role; batched rlog timestamps still cannot identify the downstream physical transmitter/proxy signer. VAR-094 proves consecutive `5282` is absent from native Bus-1 CAN; CORR-138 retracts the former standing-echo interpretation of `0x160[22]`. VAR-101 plus CORR-149 exclude FRC from the TSK key-holder/signing role and bound the always-on downstream proxy signer to Brake/Skid or Central Gateway without identifying which one.

The integration and stock-architecture questions are deliberately separate. OQ-054 still tracks the private FRC request handoff and exact Bus-4 `0x08A` signer. That attribution is **not** a prerequisite for exercising B6 as an independent external EPS angle ingress. Exact-F33 Gate-2 compare neutralization plus CRC repair can admit deliberately zero-MAC28 B6, and VAR-089 supplies the audited reset-to-stock RAM re-admission candidate. The current local forks reintroduce an exact-F181, non-release B6 development path (`opendbc@c98872c6`, parent `kai-openpilot@5fee63cfc`) and harden it with cruise/`controls_allowed` safety plus runtime fixes (`opendbc@8da4bb9b`, parent `kai-openpilot@6dd58cf5e`). Default/release behavior remains `dashcamOnly` / `SafetyModel.noOutput`.

**Current execution blocker:** install and positively verify one receiver-acceptance option—persistent Gate-2 CodeFlash patch or reset-to-stock RAM bridge—then run bounded stationary inactive/zero/small-angle validation. The sender currently uses an explicit-zero, non-stock 28-byte base plus recovered companion defaults; application semantics, sign/scale, driver override, motor response, timeout/release, source coexistence or suppression, and fault recovery must be measured before leaving the development boundary. For the RAM option, `card.py` consumes exact-F181 bridge-attestation parameters but does not deploy the resident or verify an EPS heartbeat.

**Physical routing decision (CORR-139):** the present Toyota-B repin is correct.
Current GTS+ places Brake/Skid/SAS/EPS together on Toyota Bus 4; exact F33 has one
application CAN controller carrying both its B6 rule and diagnostic rules; the
relay-correct capture observes exact-F33 `0x030` and EPS UDS on the repinned
steering family. Therefore the candidate external-control route is `0x0B6`,
DLC 32, on **Panda bus 0 across the current CAN0/CAN2 relay pair**. Panda bus 1
remains the native FRC/camera-radar plane. Do not send `0x08A` to EPS, do not infer
an `0x08A -> B6` transform, and do not repin again in search of an EBU-private EPS
stub: the telemetry/carrier absences in VAR-099 are not a routing discriminator.
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

### 3.4 Passive default and development-only output remain mechanically separate

The ordinary TSS3 path computes a shadow B6 application/safety decision while returning
**zero CAN frames**. The platform remains `dashcamOnly` / `SafetyModel.noOutput` unless
all exact-F181, non-release development gates below are satisfied. Ordinary Toyota safety
modes do not whitelist `0x0B6`.

The current development path is real but dormant by default. Parent `card.py` requires
`ToyotaEphemeralSecOCBridge`, exact `ToyotaEphemeralSecOCBridgeF181=8965F3307000`,
`ToyotaTss3DevLateral`, a byte-match against the current EPS firmware inventory, no preferred
`SecOCKey`, stock longitudinal control, TSS3 identity, and a non-release build. Only then does
it clear `dashcamOnly`, select Toyota safety with `TSS3_DEV_LATERAL`, and arm the controller's
zero-MAC28 B6 sender. `card.py` treats those parameters as external bridge attestation: it does
not deploy the RAM resident or verify an EPS heartbeat.

## 4. Current exact-F33 Gate-2 development plumbing (VAR-102)

The first conservative sender was staged in opendbc `dde0fcf0` / parent `15f355036`, then
removed in `b9e86924` / `abf3ca70a` after the stock-template premise was disproved. The
current path was deliberately reintroduced without that premise in opendbc `c98872c6` and
parent `5fee63cfc`; opendbc `8da4bb9b` adds the cruise/`controls_allowed` gate and accurate
slew-limited output reporting, while parent `6dd58cf5e` fixes controller availability and
registers `ToyotaTss3DevLateral`. Default/release output remains disabled.

### 4.1 Current sender contract

Once externally attested and armed, the controller:

- sends one `0x0B6`, DLC-32 frame per control cycle on Panda bus 0;
- reads live `0x00F` trip/reset epoch and owns message8 plus application sequence locally;
- sends Target Lateral ID 11 while active and ID0 after ramping the target to zero;
- clamps target angle to ±1745 raw and each transmitted step to ±78 raw;
- reports the actual slew-limited transmitted angle to controls;
- preserves the FV4 nibble while deliberately transmitting zero MAC28.

The 28-byte base is explicitly `stock_validated=false`: no stock B6 exists in the retained
factory-LTA intervals. Recovered command fields are packed exactly. Current bounded companion
defaults set additive-term suppression to 1 and both percentage contributions to 0; the
remaining unresolved fields are zero. This is a development candidate to validate against
the patched/bridged receiver, not a claim about Toyota stock bytes.

### 4.2 Receiver-acceptance options

Two exact-F33 development options are tracked:

1. **Persistent CodeFlash:** Gate-2 compare neutralization plus deterministic CRC repair.
   This is frictionless after installation but carries flash-write and persistent-image risk.
2. **Reset-to-stock RAM bridge:** VAR-089's audited resident re-admits only rejected B6 frames
   carrying the zero-MAC28 marker. It avoids persistent flash modification, but a reliable
   application-mode deployment/execution/heartbeat path is not implemented.

Neither option recovers or exposes the protected slot-class TSK key. The key remains in
protected ICU-S storage.

### 4.3 Development Panda safety boundary

`ToyotaSafetyFlags.TSS3_DEV_LATERAL` remains behind Panda `ALLOW_DEBUG`. When selected by the
exact development gate, it installs a dedicated bus-0 `0x0B6`/DLC-32-only TX whitelist. It
requires prior `0x025` steering-rate and `0x00F` synchronization observations, consumes
`0x08A B3[3]` as the same-car cruise operating latch, and requires `controls_allowed` for an
active ID11 request. Inactive release remains allowed. The hook enforces:

- active Target Lateral ID exactly 11;
- absolute target ≤1745 raw;
- absolute steering-rate raw ≤100;
- modulo-64 sequence exactly +1;
- target step ≤78 raw;
- active inter-command timeout ≤35 ms.

Ordinary Toyota modes still reject B6. The development implementation is test-verified, not
vehicle-authorized.

## 5. What remains before lateral output can actually be exercised

The shortest execution path is independent of Toyota's unresolved stock FRC pipeline:

1. **Install and positively verify receiver acceptance.** Choose the persistent Gate-2 patch
   or complete RAM deployment/execution/heartbeat. A parameter saying the bridge is installed
   is not proof that it is running.
2. **Validate the B6 application candidate stationary.** With the wheels unloaded, test ID0
   inactive, ID11 zero angle, then one small bounded nonzero step. Establish sign, scale,
   application companion behavior, motor response, and absence of an EPS fault latch.
3. **Validate safety transitions.** Prove driver override, slew/rate limits, ramp-to-zero,
   sender timeout, inactive release, source coexistence or relay suppression, inhibit, fault,
   and recovery behavior.
4. **Only then tune and leave the stationary boundary.** Production transmission remains
   unauthorized.

OQ-054 remains valuable for an elegant stock-compatible architecture: synchronized FRC
Operation FFD `5282/5631/5285/57DE/5265/560D`, matched FRC/Brake firmware, or source-identifying
capture must still reveal the request handoff/encoding and the exact Brake/Skid/CGW signer.
Native Bus 1 has 22 frequent periodic camera/radar streams; `0x180..0x182` carry recovered
perception-object slots, but per-ID FRC-versus-radar ownership is not named. The 28-byte `0x08A`
application and consecutive `5282` layout are absent. VAR-113/CORR-153 bound direct
single-field linear/monotonic carriers within declared sweeps but leave transformed,
multi-field, multiplexed, sparse/event, and genuinely private/non-CAN handoffs open. We
therefore know what FRC computes, not the transport/encoding that carries those semantics to
the downstream proxy. That attribution does **not** block the independent B6 development
probe above.

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

- Findings with this document as canonical home: [VAR-058](../reference/index.md#finding-var-058), [VAR-061](../reference/index.md#finding-var-061), [VAR-062](../reference/index.md#finding-var-062), [VAR-071](../reference/index.md#finding-var-071), [VAR-102](../reference/index.md#finding-var-102)
- Corrections with this document as canonical home: [CORR-120](../reference/index.md#correction-corr-120), [CORR-122](../reference/index.md#correction-corr-122), [CORR-139](../reference/index.md#correction-corr-139), [CORR-140](../reference/index.md#correction-corr-140)
<!-- knowledge-cross-references:end -->
