# 2026 Camry TSS3 passive + historical-development openpilot/opendbc port

**Target:** maintainer 2026 Toyota Camry Hybrid, EPS application F181
`8965F3307000 / 8A3113303100`.

**Evidence boundary:** this report closes the exact-F33 generated-COM transmit geometry, the default-passive software integration, and the current development-only B6 sender/safety envelope. It does **not** authorize steering transmission. CORR-129/VAR-081 identify **73.303384 s of retained `0x08A` ID11 LTA/LCA request state with zero B6**; this is not a direct winner/grant oracle. CORR-134 recovers B21 as Target Lateral ID and B18:B19 as the signed request-angle quantity; CORR-135 rejects a presumed `0x08A -> B6` transform. Exact F33 neither accepts `0x08A` nor transmits it, while its B6-inactive internal path reaches physical steering; that makes zero B6 architecturally possible but does not prove the retained request was granted. VAR-091/CORR-136/CORR-149 place authenticated `0x08A` on captured Bus 4, observed E2E-only camera/radar PDUs on Bus 1, and exclude the FRC from the TSK signing role; batched rlog timestamps still cannot identify the downstream physical transmitter/proxy signer. VAR-094 proves consecutive `5282` is absent from native Bus-1 CAN; CORR-138 retracts the former standing-echo interpretation of `0x160[22]`. VAR-101 plus CORR-149 exclude FRC from the TSK key-holder/signing role and bound the always-on downstream proxy signer to Brake/Skid or Central Gateway without identifying which one.

The integration and stock-architecture questions are deliberately separate.
OQ-054 still tracks the private FRC request handoff and exact Bus-4 `0x08A`
signer. That attribution is **not** a prerequisite for exercising B6 as an
independent external EPS angle ingress. Exact-F33 Gate-2 compare neutralization
is homologous to the field-proven Sienna result bypass, but the cumulative F33
stage-5 patch plus zero-MAC B6 did not update the application snapshot. Static
review now closes the configured Corolla/Camry B6 path and the downstream F33
ID11/health selector; it does not claim live receiver acceptance. The current
`kai-openpilot` fork carries the exact-F181 B6 development path: exact-F33 output
is enabled on its `kai` development branch through the ordinary Toyota safety
model (§3.4); upstream comma opendbc has no Camry TSS3 platform at all.

**Current execution blocker:** establish the first live B6 boundary with the
countered non-bypassing RAM observer. It distinguishes a valid scheduler window
through native protected-D7 queue activity, then requires a phase-local B6 queue
count and exact current-phase wire signature. Only proven B6 queue ingress
authorizes the deduplicating RAM route44 bridge. A further persistent
SecOC-result patch or nonzero target is unjustified before that split. The
sender's explicit-zero 28-byte base remains non-stock; application semantics,
sign/scale, driver override, motor response, timeout/release, source coexistence
or suppression, and fault recovery remain unmeasured.

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

### 3.4 Current fork state: exact-F33 output is enabled, not passively gated

The original passive implementation remains useful history, but it no longer describes the
code that produced the 2026-09-04 road logs. The current fork moved through three relevant
opendbc revisions:

- `78d03ddf` keeps Toyota `0x08A` passive/read-only and forwarded from the camera side;
- `91834530` restores exact-F33 B6 lateral output through the ordinary Toyota safety model;
- `c7a62eaf` reanchors the local B6 message counter whenever live `0x00F RESET_CNT` changes.

The corresponding parent `kai-openpilot` revisions are `75779fcdb`, `eda738486`, and
`d1914bbe7`. For `TOYOTA_CAMRY_TSS3`, current `CarInterface` selects Toyota safety with
`STOCK_LONGITUDINAL|TSS3`, sets `dashcamOnly=False`, advertises angle control down to zero
speed, and does **not** require the former `ToyotaEphemeralSecOCBridge` /
`ToyotaTss3DevLateral` attestation parameters. Panda forwards stock `0x08A`, blocks a
camera-side stock `0x0B6` replacement source, and permits the controller's bus-0 B6.

The former state-decoding holdover is resolved: fork opendbc `e37bab6c` (2026-09-04)
replaces the hardcoded `steeringPressed=False` with the normal driver-state contract — physical
`0x030` torque above a provisional 1.2 N.m exact-F33 threshold (route-3d-derived; sign and
final value still need dynamic validation). §4.4 records why the placeholder was not harmless.

## 4. Current exact-F33 Gate-2 development plumbing (VAR-102)

The first conservative sender was staged in opendbc `dde0fcf0` / parent `15f355036`, then
removed after the stock-template premise was disproved. Later development revisions rebuilt
the B6 candidate without claiming a stock template. The code exercised on 2026-09-04 is the
newer ordinary-path implementation at opendbc `78d03ddf -> 91834530 -> c7a62eaf`: stock
`0x08A` remains passive, B6 lateral is enabled for exact F33, and local freshness progression
is reanchored on each live reset epoch. This supersedes the former debug-only gating described
in older history.

### 4.1 Current sender contract

For exact F33, the current controller:

- sends one `0x0B6`, DLC-32 frame every other 100-Hz control frame (nominal 50 Hz) on
  Panda bus 0;
- reads live `0x00F` trip/reset state, resets the local message counter to zero whenever
  `RESET_CNT` changes, and owns the independent modulo-64 application sequence locally;
- sends Target Lateral ID 11 while `CC.latActive` and ID0 otherwise;
- applies the normal Toyota angle-control shaping, including the recovered ±1745-raw
  (~100-deg) absolute envelope and speed-dependent angle-rate limits;
- reports the actual slew-limited transmitted angle to controls;
- preserves the computed FV4 nibble while deliberately transmitting zero MAC28 for the
  patched exact-F33 receiver experiment.

The 28-byte base is explicitly `stock_validated=false`: no stock B6 exists in the
retained factory-LTA intervals. Recovered command fields are packed exactly.
Current active companion fields set additive-term suppression to 0 and both
percentage contributions to 100, matching the recovered F33 selector shape;
inactive fields remain zero. This is a development candidate to validate
against an observed/bridged receiver, not a claim about Toyota stock bytes.

### 4.2 Receiver observation and conditional bridge

The historical cumulative CodeFlash stage-5 image remains a development
artifact, not proof of receiver acceptance: zero-MAC B6 left the application
snapshot stale. The current sequence is RAM-only:

1. **Countered observer:** the audited v2 resident samples without bypassing. It
   counts B6 and native protected-D7 queue samples, preserves the exact last B6
   signature, and records profile-2 pre/post state. D7 activity validates that
   the observer ran across a healthy native SecOC scheduler window.
2. **Deduplicating route44 bridge:** only after an exact queue-phase match, save
   the queued zero-MAC B6 before the stock aggregate; afterward call recovered
   route44 `0x7D72C` only if the raw COM window does not already equal that exact
   frame.

Neither resident recovers or exposes the protected slot-class TSK key. The key
remains in protected ICU-S storage. The bridge is a causal receive-path
experiment, not production architecture.

### 4.3 Current Panda safety boundary

Current TSS3 Panda safety is no longer the earlier `ALLOW_DEBUG`/`TSS3_DEV_LATERAL`
sequence-and-timeout experiment. With the ordinary Toyota `TSS3` flag selected, bus-0
`0x0B6`/DLC-32 is whitelisted and checked as an **angle-steering command**. The B6 hook:

- allows only Target Lateral ID 0 (inactive) or 11 (LTA/LCA active);
- interprets B4:B5 as signed target steering angle;
- enforces ±1745 raw (~100 deg); and
- applies the standard Toyota speed-dependent angle-rate checks against measured `0x025`
  steering angle.

There is no B6 torque-command limit in this branch. The legacy Toyota
`MAX_LTA_DRIVER_TORQUE_ALLOWANCE` path is below the TSS3 controller's early return and is not
what constrains these B6 frames. `safetyTxBlocked` and Panda reject-return evidence therefore
provide a direct way to distinguish a Panda angle-safety rejection from an EPS that simply
does not act on a successfully transmitted command.

### 4.4 2026-09-04 highway evidence: B6 non-response and lane-change state failure (VAR-124/125)

Three long same-day routes were retained under
`/Users/kai/dev/inspect/logs/camry-2026/2026-09-04/`: `0000003b--62262eb7a1`
(110 segments), `0000003c--97b9e7a69a` (81), and `0000003d--0e812cecba` (62). Together
they contain **751,664** openpilot B6 `sendcan` frames. The CAN returns contain **751,628**
Panda returned/TX-loopback B6 frames and only **33** `src=192` rejected B6 frames; the
Panda `safetyTxBlocked` counter rises by only **19** over roughly 252 minutes. This rules out
Panda steering limits as the explanation for the repeated long-duration non-response.

The failure is visible directly in angle space. During route `3d`'s first right-lane-change
warning, openpilot and its post-controller B6 output command roughly **+6.2 deg** while
measured steering remains near **-2.5 deg** for long enough to saturate. Route `3c` contains
an even larger window: B6 commands roughly **+15..+17 deg** while measured steering remains
near **-9.4 deg**. These are not marginal rate-limit clips. `LatControlAngle` declares
`saturated` when desired and measured steering differ by more than 2.5 deg for the configured
0.8-s `steerLimitTimer`; `selfdrived` then emits `steerSaturated` / “Turn Exceeds Steering
Limit”. The alert is therefore an **angle tracking failure**, not a report that a steering
torque allowance was too small.

Stock Toyota lateral state remains present at the same time. Native camera-side `0x08A` is
forwarded, and ID11 is frequent throughout all three routes; in route `3d` alone there are
226,470 sampled >5-m/s overlaps where openpilot B6 is active ID11 and stock `0x08A` is also
ID11. Because the two requested angles usually co-vary during straight highway driving, the
rlog alone cannot prove that Toyota is the *sole* actuator in every straight segment. The
large-divergence windows do prove the narrower and more important fact: successfully
transmitted openpilot B6 can fail to produce the commanded wheel motion while the stock
request plane remains live. A clean non-blinker route-`3c` interval strengthens that
interpretation: at ~25.7 m/s with only ~0.45 N.m driver torque, measured steering remains
near **3.2 deg** for ~1.25 s while stock `0x08A` is ~**3.1 deg** and openpilot/B6 is
~**6.36 deg**. This is directly consistent with the stock request/authority path continuing
to determine the wheel while B6 is ineffective in that window. It still does not prove sole
stock ownership when the two targets co-vary. Exact EPS B6 ingress/freshness/acceptance
therefore remains the primary actuation blocker; raising an openpilot/Panda steering limit is
not supported.

The lane-change warning had a second, independent software cause. The exact-F33
`CarState` that produced these routes decoded physical steering-wheel torque but set
`steeringPressed=False` on every sample.
Openpilot's `DesireHelper` requires `steeringPressed` plus torque in the indicated
direction to leave `preLaneChange` and enter `laneChangeStarting`. Across the three routes
there are thousands of `preLaneChangeLeft/Right` event samples and **zero `laneChange` event
samples**. The driver can therefore physically steer across the lane boundary while
openpilot continues requesting the old-lane path; the resulting desired/measured-angle gap
then triggers the same `steerSaturated` alert. Route `3d` torque distributions also show why
a threshold should not be guessed from one drive: absolute torque during `preLaneChange` has
median ~1.30 N.m and p90 ~2.15 N.m, while >10-m/s no-blinker samples still reach median
~0.37 N.m, p90 ~1.14 N.m, with substantial overlap. Resolved 2026-09-04 by fork opendbc
`e37bab6c`: `steeringPressed` now thresholds physical torque at a provisional 1.2 N.m — just
above the no-blinker p90 and below the preLaneChange median. On-vehicle validation of the
threshold and the `0x030` torque sign convention remains required.

Finally, the Sept-3 freshness change is demonstrably active on the wire but not yet proven
accepted by F33. Live `0x00F RESET_CNT` advances roughly every 300 ms rather than only at
ignition; the current sender reanchors its local message counter at each such epoch, and the
observed B28-high FV4 progression matches that implementation. Exact firmware still verifies
freshness before the patched Gate-2 MAC-result path and can return drop/retry/adopt verdicts.
Nothing in these rlogs proves which verdict B6 received. The corrected non-bypassing queue /
freshness observer remains the right discriminator; the wire-consistent FV4 trace is not a
substitute for receiver acceptance.

### 4.5 2026-09-04 wire-geometry, authority-attribution, and transport audit (VAR-126)

A full-corpus decode of the same three routes closes the three remaining observational
questions around §4.4: what the sender actually put on the wire, whether the wheel
tracks the stock or the openpilot request when they diverge, and whether any
transport-level event could explain the non-response.

**Sender envelope is internally exact.** All 751,664 B6 `sendcan` frames decompose into
exactly two application shapes: inactive `Target Lateral ID 0` with companion byte
`B6=0x04` and `B8=B9=0`, and active `ID 11` with `B6=0x00` and `B8=B9=100` (0x64).
MAC28 is zero on every frame, every other application byte (`B0..B2`, `B10..B27`) is
zero on every frame, the modulo-64 sequence advances exactly +1 on every consecutive
pair (the only non-+1 differences are the 253 intra-route segment boundaries), the
message counter's low2 jumps only at epoch reanchors, and the transmitted reset low2
equals the current `0x00F RESET_CNT` epoch low2 on 100% of frames that had an observed
sync (751,664 − 603 segment-start frames). Cadence is a clean 50 Hz: per-segment median
inter-frame gap 19.84–20.01 ms, worst observed gap 34.6 ms. The sender did not
misbehave.

**One systematic wire difference from the stock protected sender.** The native protected
`0x0D7` stream on the same bus shares the FV4+MAC28 trailer and is the only available
reference for what an accepted protected sender looks like. Its first frame in each
freshness epoch carries message-low2 = **1** in 95.1–95.5% of epochs (second mode 3,
4.0–4.2%, race frames), and its reset low2 lags the observed `0x00F` epoch by one on
~0.2–0.3% of frames. Our reanchoring sender instead emits first-in-epoch message-low2 =
**0** in 99.6–99.8% of epochs. The stock sender therefore keeps a one-count phase
difference at every epoch boundary that our sender does not reproduce. VAR-123's
recovered verifier compares `frame_mc_low2 <= tracked_low2` against offset candidates
`{0,-1,+1,-2,+2}`, so this phase difference is not proven fatal — but it is the only
observable wire-geometry divergence from a known-accepted protected sender and is a
cheap A/B variable (`message_counter` initial phase) for the next stationary observer
run.

**The wheel tracks the stock request, corpus-level.** Restricting to samples where both
requests are active ID11 and fresh (≤50 ms), speed > 15 m/s, no blinker, |driver torque|
< 0.7 N.m, and the two requested angles diverge by ≥ 2.5 deg (181 samples across the
three routes): median |measured − stock| = **0.79 deg** versus median |measured − B6| =
**2.02 deg**; the stock request is closer in 134 samples versus 47, and there are 30
samples where stock tracks within 1 deg while B6 is off by more than 3 deg, against 2 in
the reverse direction. This generalizes §4.4's single route-`3c` interval to the whole
corpus. (In the unseparated bulk the B6 error is smaller — median 0.26 deg versus 0.69 —
but that is the openpilot controller closing the loop on the measured, stock-driven
plant and is not authority evidence; only the separated subset discriminates.)

**Transport is exonerated during driving.** All of route `3d`'s 56 bus-off events, its
single CAN core reset, and its receive-error accumulation (REC endpoint 127) fall inside
the final 100 ms of the route — power-down noise — and `canfdEnabled=false` intervals
exist only in the first/last ~0.1 s of each route. The four B6 sends in `3d`'s shutdown
window are the only non-rejected sends without a Panda return. During every driving
window `canfdEnabled=true`, `busOffCnt=0`, and `transmitErrorCnt=0`, while native
traffic (`0x00F` at 10 Hz, `0x0D7` at 50 Hz) and stock LTA functioned on the same bus.
Panda-level transport cannot explain the non-response. (Per CORR-159, Panda TX returns
still do not prove physical ACK; the same-bus native traffic bounds that residual.)

**The EPS raised no observable objection.** In the `0x030` telemetry nibble
(`EPS_STATUS_B6_BIT3 / STEERING_FAULT_INHIBIT_STATUS / EPS_STATUS_B6_BIT1 /
DRIVER_TORQUE_INVALID`), `STEERING_FAULT_INHIBIT_STATUS` and `DRIVER_TORQUE_INVALID`
(alone) are never asserted; `EPS_STATUS_B6_BIT1` appears in 0.3–1.1% of frames and
`EPS_STATUS_B6_BIT3` in 269 frames of each of routes `3c`/`3d` (none in `3b`; 72–73 of
them together with `DRIVER_TORQUE_INVALID`), all transient with the dominant state
zero. No fault latch, no inhibit, no status transition correlates with the B6 phases.
Combined with §4.4 this separates the failure cleanly: the receiver neither acts on nor
visibly rejects three-quarters of a million well-formed frames — silent non-admission
upstream of any observable application reaction, consistent with the unresolved
ingress/freshness/first-rejecting-stage boundary, while the lane-change alert was fully
explained by the former `steeringPressed=False` integration bug (VAR-125; fixed by fork
opendbc `e37bab6c`).

## 5. What remains before B6 steering authority is established

The 2026-09-04 road logs show why further limit tuning is not the next step. The shortest
bounded execution path is independent of Toyota's unresolved stock FRC pipeline:

1. **Return B6 diagnosis to the stationary boundary.** The road corpus already proves that
   openpilot can request large angles without getting the expected wheel motion; another road
   drive cannot localize the receiver failure and adds no useful discriminator.
2. **Observe B6 ingress without bypass.** Install/heartbeat-attest observer v2 in NRTD,
   transition directly NRTD→READY without OFF, and run the stationary exact-signature probe.
   `D7 delta=0` invalidates the window.
3. **Separate transport from EPS acceptance when B6 remains zero.** With D7 advancing, use an
   independent physical bus receiver; Panda TX returns and REC/TEC endpoints alone do not
   prove wire acknowledgement.
4. **Bridge only after exact queue ingress.** Install the deduplicating route44 resident and
   repeat ID0/current-angle phases. Do not request a nonzero offset before the host classifier
   reports `ADMITTED`.
5. **Validate the B6 application candidate stationary.** With the wheels unloaded, test ID0
   inactive, ID11 zero angle, then one small bounded nonzero step. Establish sign, scale,
   application companions, motor response, and absence of an EPS fault latch.
6. **Validate the driver-state mapping on-vehicle.** Fork opendbc `e37bab6c` feeds
   `steeringPressed` from physical `0x030` torque at a provisional 1.2 N.m; confirm the
   threshold and torque sign/direction dynamically, and keep the fault mapping neutral
   until same-car asserted/recovery transitions are proved.
7. **Only after receiver acceptance and driver-state policy are closed, validate safety
   transitions and tune.** Prove slew/rate limits, inactive release, source coexistence or
   suppression, inhibit, fault, recovery, and driver override before another on-road B6 test.

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

- Findings with this document as canonical home: [VAR-058](../reference/index.md#finding-var-058), [VAR-061](../reference/index.md#finding-var-061), [VAR-062](../reference/index.md#finding-var-062), [VAR-071](../reference/index.md#finding-var-071), [VAR-102](../reference/index.md#finding-var-102), [VAR-124](../reference/index.md#finding-var-124), [VAR-125](../reference/index.md#finding-var-125), [VAR-126](../reference/index.md#finding-var-126)
- Corrections with this document as canonical home: [CORR-120](../reference/index.md#correction-corr-120), [CORR-122](../reference/index.md#correction-corr-122), [CORR-139](../reference/index.md#correction-corr-139), [CORR-140](../reference/index.md#correction-corr-140)
<!-- knowledge-cross-references:end -->
