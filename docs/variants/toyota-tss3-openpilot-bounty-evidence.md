# Toyota TSS3 openpilot bounty evidence

**Issue:** [commaai/opendbc#3695 — Toyota TSS3 car port](https://github.com/commaai/opendbc/issues/3695)

**Status:** bounty-level control evidence assembled; upstream cleanup and review packaging remain.

**Evidence sources:** direct same-car rlog (`firmware-static` is used only for the
target-specific F33 wire/security boundary) plus an independent Corolla field
report (`external-source`).

This report is the compact review entry point for the Toyota TSS3 work. It
separates the control result from the development mechanism used to obtain it:

- the maintainer's 2026 Camry demonstrates openpilot lateral control while
  Toyota LTA is off;
- the maintainer's Camry work had already discovered the unprotected `0x160`
  request plane and produced a verified offline generator; albinoelephant's
  later 2023 Corolla TSS3 field run independently validates it under live
  openpilot longitudinal control on the stock Toyota-B network;
- SecOC is not a TSS3-generation requirement. The Camry's RAM-resident B6 signer
  is an exact-EPS development adapter, not architecture that should be imposed
  on every TSS3 platform.

## 1. Camry lateral: direct route evidence

### Result

Route `00000093--4066e7ae51`, segment 3 contains a continuous 17.92-second
openpilot lateral-active interval at 10.61..10.94 m/s. The controller sent 893
fresh active C7 angle commands at nominal 50 Hz. All 893 have successful Panda
TX returns and none is returned as rejected. Measured steering follows the
command from negative angle through a sustained positive-angle turn with no EPS
temporary or permanent fault.

This is not an inference from the operator's impression alone. The same interval
contains the following independent witnesses:

| Witness | Direct segment-3 result |
|---|---:|
| `carControl.latActive` samples | 1,787 |
| Active C7 `sendcan` frames | 893 |
| Active C7 successful Panda returns | 893 |
| Active C7 rejected returns | 0 |
| C7 target-angle range | -3.954..20.228 deg |
| Measured steering-angle range | -4.0..17.8 deg |
| Target/measured Pearson correlation | 0.997 at 400 ms tested lag |
| Target/measured mean absolute error | 0.994 deg at that lag |
| `carState` samples in interval | 1,784 |
| Driver `steeringPressed` samples | 11 (0.62%) |
| Absolute driver torque | 0.23 N.m median; 0.47 N.m p95; 0.67 N.m max |
| EPS temporary/permanent fault samples | 0 / 0 |

The two-second means show the target leading a physical steering response rather
than a single coincident endpoint:

| Seconds from activation | Mean C7 target | Mean measured angle |
|---:|---:|---:|
| 0 | -1.90 deg | -2.66 deg |
| 2 | 0.05 deg | -0.80 deg |
| 4 | 4.71 deg | 2.95 deg |
| 6 | 8.31 deg | 7.03 deg |
| 8 | 10.58 deg | 8.81 deg |
| 10 | 16.77 deg | 14.34 deg |
| 12 | 18.83 deg | 16.87 deg |
| 14 | 17.32 deg | 16.33 deg |
| 16 | 16.60 deg | 15.97 deg |

The operator independently reported that openpilot steering was physically
apparent. The direct route response, low driver torque, clean EPS state, command
lead, and inactive Toyota request plane make this **observed openpilot lateral
control**, not merely a successful transmit test.

### Toyota LTA was off

The active interval contains 717 native bus-2 `0x08A` request frames and 597
native bus-0 `0x081` result/reference frames. Every `0x08A` and every `0x081`
has Target Lateral ID `0`, which Toyota's recovered dictionary defines as **No
Request (Manual Operation)**. There are no native ID11 LTA/LCA requests or
results during the openpilot steering interval.

This matters because the wheel response cannot be assigned to simultaneous
factory LTA. Openpilot was engaged from normal non-adaptive cruise after EPS
programming had made stock TSS/DRCC unavailable for that ignition cycle.

### Source integrity and scope

The active interval is wholly inside segment 3, SHA-256
`65bc4e824580628cb8409d92b72e15e0626b92e1a2553b304d3e81db209ca2ad`,
which matches the contemporaneously recorded inventory byte-for-byte. The local
copy is intentionally outside git under
`/Users/kai/dev/inspect/logs/camry-2026/2026-09-10/00000093--4066e7ae51/`.

Segments 0..5 pulled from the comma on 2026-09-11 match the retained hashes.
The comma's current segment 6 is a valid Zstandard stream but has SHA-256
`78f96db6bdc11d73c63e09c43f3c4cfde7033d579a215b9111a3eb5658aa9c84`,
not the contemporaneously inventoried `4a0646ae...`. Full-route totals from the
original reduction must therefore not be silently mixed with a new seven-file
reduction. This discrepancy does not affect the lateral claim because all of
its inputs and witnesses are in byte-identical segment 3.

The route records openpilot parent `ddd1f6fac47e636c6b5ec470849350587ee04272`,
branch `kai`, version `0.11.2`, and `dirty=true`. The dirty state is material:
the working C7 opendbc delta was not part of base commit
`baec01c15ac3fdf7361f862a483ad3a06e1f985a`.

## 2. Exact Camry development mechanism

The successful Camry drive did not transmit a host-built B6. Its ordinary
openpilot control path was:

```text
controlsd / CC.latActive
  -> Toyota CarController angle limits
  -> 00 C7 sequence 00 target_hi target_lo 00 00
     on extended 0x1FDC0002, Panda bus 0
  -> ephemeral exact-F33 EPS resident
  -> replace B6 B3..B9 in one already-admitted native B6
  -> EPS ICU-S command 5, selector 4
  -> valid replacement trailer before stock SecOC consumption
  -> normal F33 angle-control path
```

Sequence zero is neutral and leaves the native B6 untouched. While
`CC.latActive`, the controller advances 1..255 and the resident consumes each
fresh value at most once. Panda applies its normal Toyota angle-command checks
to the requested angle and rejects malformed C7 frames.

The exact reproduction identity is:

- installed cumulative stage-5 image:
  `669cedf8c8465ebfd02318cb7708b897b817bc3b40925c89743b64ce49aa01af`;
- authenticated 4-KiB RAM payload:
  `01ce993425e910a6ea37473580adb6e641bdff56a3568492d4c9e0388e02fc6c`;
- retained high-tail resident:
  `31b1b2c31007f130d6b4679a0c99f5903a58f748daf11978f9c52f504aea3a3a`;
- padded post-startup helper:
  `4719c4f27563180359445724eaefd594e3051ea545f75d69efb9bbede8f1965a`;
- exact five-file working opendbc delta:
  `kai-opendbc-c7-working-tree.patch`, SHA-256
  `3f798940f439f329ebade4e342325f951e1b0725dba801565708df9bbc610081`.

The required volatile lifecycle was full EPS OFF, NRTD/Park/stationary
`./f33-secoc install`, direct NRTD-to-READY without OFF, then
`./f33-secoc load-arm`. The last step required byte-exact helper readback and
equality between one untouched Toyota B6 trailer and the locally generated
command-5 trailer. Panda ownership was then returned to exactly one normal
openpilot manager/pandad tree. Full EPS OFF removed the resident and required
repeating the install/arm sequence.

The retained [session summary](../../targets/camry-2026/raw-20260910/working-steering/summary.json),
[exact working delta](../../targets/camry-2026/raw-20260910/working-steering/kai-opendbc-c7-working-tree.patch),
and [field runbook](../../exploit/ephemeral_runtime/camry_f33_runtime_monitor_runbook.md#known-working-openpilot-steering-fallback)
are the reproduction sources.

## 3. Corolla TSS3 longitudinal proof of concept

### Chronology and attribution

The unprotected request-plane discovery and message-generation PoC predate the
Corolla field report. Git author dates provide the repository record:

| Date (America/Chicago) | Repository result |
|---|---|
| 2026-08-31 12:12 | `6d02fc4` documented the Camry plaintext/protected longitudinal join and identified native Bus-1 `0x160 B12` as the high-value non-SecOC request candidate. |
| 2026-08-31 14:28 | `4bd9ccb` recovered the Bus-1 E2E framing. |
| 2026-08-31 14:48 | `d73baf5` added the offline Camry FRC `0x160` request generator and deterministic verifier. |
| 2026-08-31 15:13 | `1661e5c` recovered the exact AUTOSAR E2E Profile-5 CRC/counter/Data-ID contract and upgraded the generator. |
| 2026-09-05 14:28 | `198d8da` documented the native openpilot longitudinal integration path. |
| 2026-09-10 | albinoelephant reported the independent live Corolla controller result. |

Thus the Camry work established the non-SecOC `0x160` path and proof-of-concept
message generation ten days before the reported Corolla run. The Corolla
result's distinct contribution is independent live closed-loop validation and
a working opendbc/sunnypilot integration on another TSS3 target.

On 2026-09-10, contributor albinoelephant reported a live openpilot-longitudinal
run on the 2023 Corolla TSS3 target. The contributor's local opendbc + sunnypilot
implementation uses the ordinary, non-SecOC FRC `0x160` command on the stock
Toyota-B network; it does not require the Camry lateral repin or an EPS RAM
signer.

The field report records three independent software/log witnesses:

1. Panda `safetyModel` remained `toyota` for the drive; a shadow/no-output run
   would report `noOutput`.
2. The controller transmitted 23,683 `0x160` frames at 40 Hz; shadow mode would
   transmit zero.
3. About 80% of those frames carried real acceleration commands, with clean
   frame rate and counter behavior.

The contributor reported that the car followed a truck and controlled speed.
The first live pass completed without the earlier system-malfunction behavior.
On a later pass, a mismatch at complete standstill triggered a Toyota System
Malfunction, which is itself consistent with openpilot owning the command and
exercising a still-incomplete stock/openpilot standstill handoff. The mode was
then explicitly reverted to `TSS3LongMode.OFF` while parked.

This is sufficient as the issue's **longitudinal proof of concept**: the native
command is implemented, transmitted under Toyota safety rather than shadowing,
and produces reported closed-loop lead following. The known standstill handoff
defect is follow-up engineering, not evidence that the longitudinal controller
was absent.

Evidence boundary: this is an attributed external field report supplied as a
Discord screenshot. The contributor explicitly described the result as new and
requested that it initially be taken with caution. The raw rlog, exact route ID,
and local-fork revision are not yet in this repository, so exact counts are
**observed/external-source**, not repository-verified. When supplied, retain the
route inventory and reduce `safetyModel`, `sendcan 0x160`, counter continuity,
requested acceleration, lead distance, speed response, and the standstill fault
transition without inventing a second longitudinal permission system.

Before that field report, this repository already contained the bare offline
message generator:
[`camry_frc_request_poc.py`](../../tools/targets/camry/live/camry_frc_request_poc.py)
constructs the observed Camry-family 32-byte `0x160` request by changing B2/B12
and recomputing its exact Profile-5 CRC. Its verifier reconstructs fixed wire
witnesses and more than 20,000 retained counter/request pairs byte-for-byte.
That is repository-verified prior proof of message generation, not proof of the
later Corolla road result or a license to transfer Camry B12 scaling to
Corolla.

## 4. What is universal and what is target-specific

The cleanup should preserve ordinary openpilot ownership and make vehicle
capabilities explicit:

| Layer | Reusable TSS3 port shape | Exact-target detail |
|---|---|---|
| Engagement | `controlsd` owns `CC.latActive` and `CC.longActive` | None |
| Vehicle description | `CarInterface`/`CarParams` select angle control, buses, limits, and longitudinal capability | Firmware identity and per-platform flags |
| State | `CarState` decodes steering, torque, faults, cruise, gear, and readiness | Message layout and native bus |
| Control | `CarController` encodes angle and acceleration from ordinary actuator requests | B6 application fields; Corolla `0x160` command |
| Safety | Panda uses ordinary Toyota angle/acceleration limits and an explicit TX whitelist | Exact address, length, bus, checksum and counter |
| Authentication | Optional transport/signing provider for a platform that actually requires it | Camry F33 C7/RAM/ICU-S adapter; user-provided key on a native SecOC sender |
| Harness | Use the stock Toyota-B topology whenever the native command is already exposed there | Camry C7 lateral on unsplit Panda bus 1; Corolla longitudinal needs no repin |

For the combined Camry cleanup, “stock Toyota-B” means undoing the temporary
lateral-development CAN0/CAN1 repin: Toyota Bus-1/`0x160` returns to the
CAN0/CAN2 relay pair for normal stock suppression/replacement, while the F33 C7
signer sideband moves to unsplit Panda bus 1 to reach Bus-4/EPS. The successful
lateral route proves the old post-repin assignment. The stock-topology software
assignment is now implemented; it still requires parked transport validation
and is not yet a road-proven fact.

The following must not become global TSS3 policy: F181
`8965F3307000/8A3113303100`, extended `0x1FDC0002`, C7, ICU-S selector 4, the
stage-5 receiver patch, NRTD lifecycle, the Camry physical repin, or any
controller-side permission veto. They are one development transport for one EPS.

Likewise, TSS3 does not imply SecOC. The Corolla longitudinal path demonstrates
the unprotected/checksummed case. A platform with a key should use the same
semantic controller and normal safety model with the appropriate authenticated
wire wrapper; a platform without that requirement should not acquire signing
machinery merely because it is TSS3.

## 5. Bounty claim and remaining packaging

The evidence now covers both control requirements named by issue #3695:

- **full lateral control:** same-car Camry road actuation with Toyota LTA off,
  ordinary `CC.latActive`, normal Panda Toyota angle checks, a commanded angle
  sweep, measured lagged response, negligible driver intervention, and no EPS
  faults;
- **longitudinal proof of concept:** independent TSS3 Corolla road control over
  unprotected `0x160` on stock Toyota-B, with Toyota safety active, 40-Hz command
  transmission, real acceleration requests, and reported lead following.

What remains is reviewability rather than discovery: promote the existing
offline `0x160` primitive through the normal controller/safety boundaries,
keep the Camry signer behind an exact platform boundary, import or link
albinoelephant's longitudinal revision and rlog reduction, and submit the
smallest upstream-shaped opendbc change. The standstill transition is a known
longitudinal follow-up and should remain an
ordinary controller/state issue, not become a speculative global safety gate.

### Issue-ready progress summary

> We now have road-tested TSS3 control in both axes. On a 2026 Camry, openpilot
> lateral produced a 17.92-second active steering interval with 893/893 active
> commands returned by Panda, commanded/measured angle correlation of 0.997,
> low driver torque, no EPS faults, and Toyota `0x08A`/`0x081` remaining ID0
> (LTA off) for the entire interval. The Camry used an exact-EPS RAM-resident
> signer, while controlsd, CarController, and Panda retained normal ownership.
> Independently and later, a 2023 Corolla TSS3 openpilot-longitudinal run transmitted
> 23,683 unprotected `0x160` commands at 40 Hz under `safetyModel=toyota`, with
> real acceleration requests in about 80% of frames and reported closed-loop
> lead following. We are now cleaning the implementation into a reusable TSS3
> port while keeping the Camry signer/repin and Corolla wire details strictly
> platform-specific.
