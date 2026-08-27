# 2026 Camry TSS3 passive openpilot/opendbc port

**Target:** maintainer 2026 Toyota Camry Hybrid, EPS application F181
`8965F3307000 / 8A3113303100`.

**Evidence boundary:** this report closes the exact-F33 generated-COM transmit geometry
needed by the passive software port and records the implementation state. It does **not**
authorize steering transmission. The retained Camry route has not yet observed stock B6,
`0x351`, `0x394`, or `0x4A3` under the relay-correct stock-LTA transition required to
promote their live policy semantics.

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

### 1.3 `0x4A3`

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

A target-specific semantic boundary matters here. F33 DID `0x1151` **Motor Actual
Current (Q Axis)** reads `GP-0x50F2`, while the `0x4A3` producer reads `GP-0x50E8`.
The opendbc field is therefore structurally named `MOTOR_CURRENT_ALT`; this report does
not claim that the two sources are equivalent merely because the H/F homolog joins to
Q-axis current.

## 2. VAR-056 bounded-census correction

VAR-056 reported four direct/fixed-GP references to the F33 physical driver-torque source
`GP-0x5158` in the then-recovered whole-function corpus:

`0x35A06, 0x4DB70, 0x54244, 0x564CE`.

Forcing/recovering the exact F33 `0x4A3` source producer adds a fifth:

`0x4C000`.

The corrected recovered set is therefore:

`0x35A06, 0x4C000, 0x4DB70, 0x54244, 0x564CE`.

This does **not** overturn VAR-056's safety-relevant negative. `0x4C000` is a generated
telemetry Tx producer outside the cooperative `C8xxx-D1xxx` target-to-motor control
cone. The bounded statement remains: no direct/fixed-GP driver-torque or DID1151
Q-current source reference was recovered in that cooperative cone; computed aliases,
DMA, and unrecovered functions remain outside the negative proof.

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

### 3.4 Controller and Panda remain mechanically non-enabling

The TSS3 controller computes a shadow B6 application and a shadow F33 safety decision for
unit/replay inspection, but returns **zero CAN frames** on every control request.

The candidate F33 C limits are compiled only with `ALLOW_DEBUG`; the helper is not called
from `toyota_tx_hook`. `0x0B6` is absent from every Toyota TX whitelist and the platform's
CarParams remains `SafetyModel.noOutput`. Dedicated tests assert that actual no-output
safety rejects B6.

The complete nested opendbc gate passed after this implementation: 4,075 executed unit
tests passed with 719 skipped, and Ruff, type checking, codespell, cpplint, and MISRA all
passed.

## 4. What remains before lateral output can be enabled

This port intentionally stops before actuation. The remaining production gates are live:

1. capture stock B6 off→active→off on a relay-correct, exact-F181 Camry and close cadence,
   full 28-byte template behavior, sequence start/restart, and freshness behavior;
2. prove exclusive relay/source suppression behavior for the production topology;
3. prove application-context slot-4 command-5 generation permission plus latency/jitter
   under normal EPS load;
4. choose and dynamically validate conservative driver-override and motor-current-response
   policy rather than converting representation limits into safety thresholds;
5. observe `0x351/0x394/0x4A3` on the relevant route and correlate normal, inhibit, asserted
   fault, and recovery transitions before public fault-policy mapping.

**Production output remains disabled.**

## 5. Deterministic evidence

- `data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json`
- `data/generated/camry_8965F3307000_tss3_opendbc_port.json`
- `tests/verify_camry_8965F3307000_tss3_opendbc_port.py`

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [VAR-058](../reference/index.md#finding-var-058)
- Corrections with this document as canonical home: [CORR-120](../reference/index.md#correction-corr-120)
<!-- knowledge-cross-references:end -->
