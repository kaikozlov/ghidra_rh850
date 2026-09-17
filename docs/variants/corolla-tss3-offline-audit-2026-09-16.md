# Corolla TSS3 offline confidence audit — 2026-09-16

## Conclusion

The retained Corolla CAN shapes decode successfully with the current port, and
its selected Toyota/firmware-fingerprint/safety unit suites pass. This is not an
all-clear for a completed or road-qualified port. There are identifiable software
and evidence gaps, not only pending vehicle testing. Earlier statements that
nothing remained except physical qualification were too strong.

This audit changes documentation only. It does not change controller, Panda,
resident, or installer behavior; it performs no vehicle access or transmission.

## Revisions and scope

Reviewed analysis `4d8006d8`, kai-openpilot `53b95d0dd` on `tss3`, and its opendbc
revision `7dce3659`. Primary integration checks use current source in the latter
checkout and the retained raw CAN inputs, rather than treating readiness prose
or a passing fixture as proof of physical behavior.

The audit covers identification/subtype selection, passive CarState decoding,
existing Toyota safety tests, the stock-cruise cancellation call path, and the
limits of the previously reported tester-kit qualification. It does not claim
exhaustive verification of every firmware execution path or a new live signer
qualification.

## Checks completed

The command below was run in `kai-openpilot/opendbc_repo`:

```sh
uv run --locked pytest -q opendbc/car/toyota/tests \
  opendbc/car/tests/test_fw_fingerprint.py \
  opendbc/safety/tests/test_toyota.py
```

Observed result: **324 passed, 262 skipped, 8,106 subtests passed**. Skipped tests
are not additional coverage. These suites include the two retained exact EPS
identity matches, Corolla powertrain selection, and the stock-longitudinal
configuration; they do not establish operation on a real Corolla.

### Raw-log decoder replay

Each input was hash-checked. The platform was explicitly selected as
`TOYOTA_COROLLA_TSS3`, while the powertrain flag came from a full-segment incoming
CAN census with no supplied diagnostic ECU records. Only incoming source buses
0–7 were retained; returned/rejected records were excluded. Original CAN batch
timestamps were replayed into `CarInterface.update()` at 10 ms intervals, with
empty timestamped updates between batches. The first five seconds were excluded
from the reported validity totals. `CarInterface.apply()` was never called.

| Input | Duration | Selected gear carrier | First valid decoder state | Valid cycles after warmup | Timeout/sensor-invalid cycles after warmup |
|---|---:|---|---:|---:|---:|
| Retained public 2023 Corolla segment 0 | 61.099784 s | `0x3BF` | 0.95 s | 5,610 / 5,610 | 0 / 0 |
| Retained Span-attributed 2025 segment | 59.990073 s | `0x127` | 0.92 s | 5,500 / 5,500 | 0 / 0 |

Input identities:

- `REFERENCE/public_route_corolla_2023_segment0_rlog.zst`, SHA-256
  `d246a55988889253c8d155f04b132b1bb443fdd74f1e6bad68eef8879a5c477b`.
- `community/spanconstant/span_67fd5b833889fedf_00000010--17084916da--3--rlog.zst`,
  SHA-256 `f1ae7c40ad8e9ff8c462a3f5367d914873e93575d902ccb82f2c74984acd439f`.

No required message was invalid after warmup. The public route decoded
Park/Reverse/Drive; the Span segment decoded Drive. The public route had no
reported ACC engagement during the counted interval. The Span replay had 92
engaged decoder cycles (0.92 s); neither replay exercised ACC standstill hold.
These are samples of the decoded state, not independent observations of the
physical dashboard or proof of controller authority.

This is a stronger nominal parser check than repeating representative frames at
100 Hz, but it is **not** an automatic-fingerprinting replay or a physical car
qualification. The public route contains no usable firmware identity join, and
the Span log is MOCK-attributed vehicle evidence rather than an exact
firmware-to-route join. See the identity boundaries in the existing
`corolla_2023_public_route_opendbc_evidence.json` and
`corolla_2025_span_discord_rlog_opendbc_evidence.json` artifacts.

## Findings that prevent an all-clear

### 1. Corolla steering-fault reporting is unfinished

At opendbc `7dce3659`, `opendbc/car/toyota/carstate.py:188–197` decodes driver-torque
validity but unconditionally sets both `steerFaultTemporary` and
`steerFaultPermanent` false. The DBC also exposes `EPS_FAULT_INHIBIT`; the Corolla
CarState path does not consume that field.

An offline synthetic check changed only the fault/inhibit field in the existing
Corolla telemetry fixture, preserving the additive-byte relationship. In both
cases the decoder remained CAN-valid and sensor-valid. With the decoded
`EPS_FAULT_INHIBIT` changed from 0 to 1, both steering-fault outputs remained
false. Thus nominal route replay cannot establish the fault-handling contract.

The existing exact-H evidence distinguishes a selected fault/inhibit aggregate
from an exhaustive EPS fault classification. A justified fault/inhibit mapping
is still needed; this finding does not authorize guessing Toyota's full
permanent/temporary fault classification. It is not accurate to describe this
as only a cosmetic future improvement.

### 2. Software-requested stock ACC cancellation was unimplemented at the audited revision

`kai-openpilot/openpilot/selfdrive/controls/controlsd.py:161–163` requests cruise
cancellation when stock cruise is enabled and openpilot is not enabled. The TSS3
branch in `opendbc/car/toyota/carcontroller.py:80–113` returns before the ordinary
Toyota cancellation handling beginning at line 118. That branch has no stock
ACC cancel sender.

Consequently the audited implementation had no mechanism to honor that request
by cancelling Toyota longitudinal control. Releasing lateral control is not
stock ACC cancellation. This is distinct from the driver's physical brake or
cancel action, and the audit makes no claim that those physical controls are
disabled. This finding is superseded by the same-day implementation follow-up
below; Corolla receiver acceptance remains a live qualification item.

### 3. The claimed hybrid gear fallback is not implemented

The successful observed configurations remain:

- bus shape with `0x127` selects the hybrid gear parser;
- bus shape without it and without hybrid diagnostic evidence selects `0x3BF`.

However, `carstate.py:33–38,375–395` chooses a single gear parser from the HYBRID
flag. It does not fall back to `0x3BF` on a hybrid when `0x127` is absent.

A separate synthetic check supplied a Hybrid Control ECU diagnostic record,
omitted `0x127`, and supplied the one-hot `0x3BF` Drive fixture for six seconds.
The port selected `GEAR_PACKET_HYBRID`, did not parse `0x3BF`, and remained
`canValid=False`. The gear field defaulted to Park, but the invalid CAN state
must not be mistaken for a qualified Park observation.

This is **not a failure demonstrated on Span's retained log**: that input has
3,662 `0x127` frames and works. It is a mismatch between the claimed general
fallback and implemented behavior, plus an untested configuration boundary.
Supporting a new fallback would require an evidence-backed selection decision;
this audit does not change that decision.

Likewise, `values.py:560–572` resolves OEM VIN identities to a platform set, not
to CarParams powertrain metadata. Separating the ten GTS vehicle IDs and fixing
the dynamic-enum membership bug did not add direct propagation of the GTS
powertrain classification. Present runtime subtype detection still uses
positive diagnostic/CAN evidence.

### 4. Cruise-state and tuning evidence remain bounded

`carstate.py:199–215` uses nonzero longitudinal request ID B as Corolla cruise
availability, the contributor engagement field as enabled, a selected request
ID/allocation combination as standstill hold, and an mph display interpretation.
Both replays report cruise availability throughout; they do not discriminate
cruise-main OFF from ON. They also do not qualify hold/resume transitions or
metric display behavior. A request-ID presence rule is not, by itself, an
independent cruise-main oracle.

GTS diagnostic enum labels corroborate shift meanings but are not a direct CAN
wire mapping. The retained public route exercises `0x3BF` P/R/D, while its N
value and the unexercised Corolla hybrid gear values retain the previously
stated evidence boundaries. Vehicle mass, steering ratio, actuator delay, and
dynamic tuning are also not physically validated by these decoder tests.

## Tester-kit boundary

The prior exact-target kit build and `doctor` result establish packaging/import
checks, not the complete installed lifecycle on the recipient's ECU. This audit
adds no new vehicle evidence for runtime survival, native-message replacement,
fault recovery, driver override, stock-system coexistence, or physical steering
response. A successful stationary signing/replacement check would still not
establish all of those properties.

The kit should not be described as making the port road-ready once two commands
pass. Current upstream also separates software-in-the-loop, hardware-in-the-loop,
and in-vehicle testing: [openpilot safety documentation](https://docs.comma.ai/concepts/safety/).

## Disposition

Keep the positive identification and passive-decoding results. Keep longitudinal
stock-owned. Do not revive `0x160` as an actuator path. Close or explicitly
resolve the fault-reporting and automatic-cancellation gaps, correct the gear
fallback/subtype claims, and retain physical qualification as a separate
requirement. This audit does not implement or validate those remaining items.


## Same-day implementation follow-up

The immediate steering-fault gap is now partially closed in the justified
openpilot shape: exact H/F `EPS_FAULT_INHIBIT` reports
`steerFaultTemporary=True`, while no permanent class is invented. The unified
signer tester's post-startup attestation, live sensor freshness/validity, Corolla
Park enforcement, NRTD preflight ordering, failure-path release, and failure
recording defects are also fixed and covered by the unified signer regression.

The software gap in automatic stock-ACC cancellation is now closed in the normal
openpilot ownership shape. Opendbc `37d6021e` snapshots Corolla's live bus-1
`0x101` Brake Module state, and when `controlsd` sets `CC.cruiseControl.cancel`
CarController clones that stock frame, asserts only `BRAKE_PRESSED`, and lets the
DBC recompute Toyota's checksum. Panda permits only bus-1 `0x101` with the cancel
bit asserted and a valid Toyota checksum; it adds no speed, cruise-state, timer,
or separate permission policy. Both retained ICE/hybrid Corolla routes carry the
same checksum-valid ordinary `0x101` family, while exact Camry evidence proves
the homologous `0x101 B0[3]` assertion causes the protected cruise request to
drop. Corolla receiver acceptance is still a live qualification item, not an
offline-proven fact.

The hybrid `0x3BF` item is retained as a coverage boundary rather than a known
Span-car failure: Span's retained hybrid supplies 3,662 valid `0x127` frames.
Likewise the cruise-main availability rule remains bounded pending an OFF/ON
capture. The corrected status is therefore: nominal identification/CarState/C7
software is strong and a bounded stationary signer qualification is warranted,
but road qualification still needs live confirmation of the implemented cancel
carrier plus the usual live actuation/coexistence work.
