# 2026 Camry TSS3 passive + gated-development openpilot/opendbc port

**Target:** maintainer 2026 Toyota Camry Hybrid, EPS application F181
`8965F3307000 / 8A3113303100`.

**Evidence boundary:** this report closes the exact-F33 generated-COM transmit geometry
needed by the software port and records both the passive default and a fail-closed
Gate-2 development-output path. It does **not** authorize steering transmission. The
development path cannot arm until live evidence supplies a stock B6 template/cadence,
proves the exact-F33 Gate-2 consequence, and proves exclusive relay/source authority.
The retained Camry route has not yet observed stock B6, `0x351`, `0x394`, or `0x4A3`
under the relay-correct stock-LTA transition required to promote their live semantics.

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

The distinct `0x4A3` alternate-current source `GP-0x50E8 = FEBE6718` has four
direct references: readers `0x4C000/0x4C490` and writers `0x59448/0x5D12C`. This
continues to justify keeping the packed field structurally distinct from DID1151.

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
normal CarParams remains `SafetyModel.noOutput`; ordinary Toyota safety modes still do
not whitelist `0x0B6`. This is the state whenever the explicit development configuration
is absent, invalid, running on a release branch, bound to the wrong F181, or still on the
normal-harness bus-1 topology.

## 4. Default-off exact-F33 Gate-2 development plumbing (VAR-062)

The remaining *static software* work for the first-development-lateral path is now staged
in nested opendbc commit
`dde0fcf0fbaf875750c54a072b0dcb3857f8829b` (`toyota: harden F33 development freshness`)
and parent `kai-openpilot` commit
`15f3550365e2eee54ca5645ae9c24d9d41ae4f31` (`toyota: harden F33 development gating`).
This does not weaken the passive default. It adds a second path that is impossible to arm
from inferred constants alone.

### 4.1 Runtime configuration refuses guessed live facts

`ToyotaTSS3DevLateral` is a development-only master switch. The companion JSON param
`ToyotaTSS3DevLateralConfig` must provide all of the following, or the car card leaves the
platform passive:

- exact `f181 = 8965F3307000`; the Toyota interface independently requires the current
  EPS CarFw entry to contain that F181 and rejects any other platform;
- a **28-byte `b6_template_hex` obtained from the relay-correct stock-LTA capture**;
- the measured stock `cadence_frames` (1–3 control frames, ≤30 ms, with no guessed default);
- `gate2_bypass_validated=true` only after the live exact-F33 invalid-MAC causal proof;
- `exclusive_b6_authority_validated=true` only after relay/source-suppression proof.

The interface additionally rejects `TSS3_PT_BUS1`: development output requires the
relay-correct bus-0 topology. Release branches reject the development master switch.

### 4.2 Development sender is deliberately not a production signer

After all gates above are supplied, the controller uses the existing exact-F33
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

### 4.3 Panda development mode is B6-only and fail-closed

`ToyotaSafetyFlags.TSS3_DEV_LATERAL` exists only behind Panda `ALLOW_DEBUG`. Selecting it
installs a dedicated TX whitelist containing exactly bus-0 `0x0B6`, DLC 32, with relay
checking. The hook requires prior bus-0 `0x025` steering-rate and `0x00F` sync observations
and enforces the statically recovered F33 envelope:

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

The remaining first-actuation gates are now live, not unfinished static implementation:

1. resolve VAR-063/065's live discriminator: two independent moving routes totaling
   3,574,703 incoming frames / 19 segments still have zero B6 while protected `00F/D7`
   remain healthy, and the exact-F33 controller-1 rule span is fully exhausted with no
   hidden direct-CAN ID outside the normal COM table; that inverse audit also finds no
   observed ordinary generated-COM steering-command alternative (`0x115` is Engine Revolution; `0x0D5` is monitor/
   plausibility; `0x025` is feedback; command-sized `0x1C5/0x64F` and group `0x013..0x01F`
   are absent). Synchronize FRC P5 DID `0x1601` (`LTA Control Condition`) with relay-
   correct CAN. If active LTA is proved while B6 remains absent, move to FRC/Brake
   transformation or a non-COM/internal EPS path rather than guessing another EPS ID;
2. prove exclusive relay/source suppression behavior for whichever command path that
   synchronized factory-LTA observation identifies;
3. complete the zero-write Gate-2 preflight, restore-gated APPLY, and an exact causal
   SecOC experiment before setting `gate2_bypass_validated`;
4. perform the bounded first steering-response experiment.

Production still additionally requires an application-context authenticated signer (or an
equivalent non-persistent architecture), conservative dynamic driver-override/current
policy, and asserted/recovery fault-state mapping. Those values remain deliberately absent
from the static safety model because the current corpus does not prove them.

**Production output remains disabled.**

## 6. Deterministic evidence

- `data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json`
- `data/generated/camry_8965F3307000_tss3_opendbc_port.json`
- `data/generated/camry_8965F3307000_external_lateral_ingress.json`
- `tests/verify_camry_8965F3307000.py`

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [VAR-058](../reference/index.md#finding-var-058), [VAR-061](../reference/index.md#finding-var-061), [VAR-062](../reference/index.md#finding-var-062)
- Corrections with this document as canonical home: [CORR-120](../reference/index.md#correction-corr-120), [CORR-122](../reference/index.md#correction-corr-122)
<!-- knowledge-cross-references:end -->
