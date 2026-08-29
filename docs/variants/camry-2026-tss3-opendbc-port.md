# 2026 Camry TSS3 passive + historical-development openpilot/opendbc port

**Target:** maintainer 2026 Toyota Camry Hybrid, EPS application F181
`8965F3307000 / 8A3113303100`.

**Evidence boundary:** this report closes the exact-F33 generated-COM transmit geometry needed by the software port, records the passive implementation, and preserves the former Gate-2 development path as historical/test-only engineering context. It does **not** authorize steering transmission. CORR-129/VAR-081 identify **73.303384 s of retained factory LTA/LCA-active operation with zero B6**; CORR-134 recovers observed Bus-4 `0x08A` B21 as Target Lateral ID and B18:B19 as the signed target-angle quantity, and CORR-135 adds a strong ordinary-P5 SecOC trailer match while correcting the former next-hop assumption. Exact F33 neither accepts `0x08A` as normal Rx nor lists it among its five generated-COM Tx IDs, but its B6-inactive `D0218 -> CC48 -> CC60 -> CC50 -> CC62/CC66 -> CC64` path reaches physical steering. Factory LTA therefore does **not** require an `0x08A -> B6` transform. Every retained `0x08A` is on the Bus-4 capture and its producer/security profile is unknown, so it must not be labeled a Bus-1 camera message.

The remaining integration problem is split deliberately. OQ-054 tracks (1) `0x08A` producer/SecOC/arbitration ownership and (2) the exact external/local state that selects or modulates F33's B6-independent stock-LTA assist path. Protected B6 remains a real external cooperative-control ingress and may later be chosen as the openpilot actuation interface, but that choice requires a separate valid signing/freshness/suppression contract and must not be inferred from stock LTA. The old stock-template B6 runtime sender was removed in `opendbc@b9e86924` and `kai-openpilot@abf3ca70a`; current opendbc `525ee987` retains only passive observation and analysis/test-only B6 receiver/freshness/safety helpers.

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

Those params and the CarInterface/CarController sender hook no longer exist. VAR-081 proves
that no stock B6 template/cadence appears during the retained factory LTA/LCA intervals,
so the old admission contract is historical evidence only and must not be revived by
inventing a template or weakening its gates. OQ-054 now owns the real integration
boundary: the observed Bus-4 `0x08A` producer, authentication/integrity, transformation
into protected B6, signer/freshness ownership, and authority/arbitration.

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

The critical remaining work is **not** a presumed `0x08A -> B6` producer chain. CORR-135 separates the stock architecture from the possible external actuation interface:

1. **Identify who produces and security-protects observed Bus-4 `0x08A`.** Exact F33 does not normally receive or generated-COM-transmit it. Recover the actual producer, SecOC profile/key-slot/freshness ownership, consumers, and arbitration. Its B28..B31 trailer strongly matches Toyota ordinary-P5 `FV4 || MAC28`, but the exact sender implementation is not yet recovered.
2. **Recover the exact F33 stock-LTA authority selector/modulator.** Start at the proven B6-inactive `D0218 -> CC48 -> CC60 -> CC50` path and trace its snapshot leaves backward while conditioning the retained logs on Target Lateral ID `0/11/18`. The missing discriminator may be a mode/gain/authority state rather than another angle-shaped CAN signal.
3. **Choose the openpilot actuation interface only after those roles are understood.** Protected B6 is a genuine F33 external cooperative-control ingress, so it remains a plausible interface; it is simply not proved to be Toyota's stock-LTA next hop. If B6 is selected, recover its valid signer/freshness/suppression/arbitration contract separately from the stock-LTA path. Do not wait for or fabricate a stock B6 template.
4. **Close dynamic safety policy before actuation.** Validate driver override, motor-current response, normal/inhibit/fault/recovery behavior, and any signer latency/jitter required by the chosen interface. Ordinary Camry operation stays `noOutput` until that contract is closed.

The historical `TSS3_DEV_LATERAL` B6 sender/safety work remains useful only as a bounded receiver/envelope experiment. It is not evidence that stock Camry LTA uses B6 and is not a reason to revive the removed runtime hook.

## 6. Deterministic evidence

- `data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json`
- `data/generated/camry_8965F3307000_tss3_opendbc_port.json`
- `data/generated/camry_8965F3307000_external_lateral_ingress.json`
- `data/generated/camry_2026_motor_feedback_correlation.json`
- `data/generated/camry_2026_lta_state_reconciliation.json`
- `tests/verify_camry_8965F3307000.py`
- `tests/verify_camry_2026_lta_state_reconciliation.py`

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [VAR-058](../reference/index.md#finding-var-058), [VAR-061](../reference/index.md#finding-var-061), [VAR-062](../reference/index.md#finding-var-062), [VAR-071](../reference/index.md#finding-var-071)
- Corrections with this document as canonical home: [CORR-120](../reference/index.md#correction-corr-120), [CORR-122](../reference/index.md#correction-corr-122)
<!-- knowledge-cross-references:end -->
