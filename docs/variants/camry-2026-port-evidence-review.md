# 2026 Camry port: adversarial evidence review

This September 15 review audits the preceding integration checkpoint, rather
than accepting the earlier “essentially complete” summary as evidence. All
work is offline; no vehicle commands or persistent firmware writes are run.

## Confirmed corrections

### Tire stiffness is a baseline times a learned multiplier

`VehicleModel.update_params()` multiplies `CP.tireStiffnessFront/Rear` by
`vehicleParameters.stiffnessFactor`. `paramsd.VehicleParamsLearner` likewise
initializes its model globals from those same CP stiffnesses. A learned value
near 1.0 therefore supports preserving the configured baseline; it does not
justify replacing `CP.tireStiffnessFactor=0.7933` with 1.0. The PlotJuggler
label used in the previous pass is not authoritative over executable code.

The erroneous 1.0 override has been removed. The 15.3 steering-ratio default
is a separate absolute learned quantity and is not reverted with stiffness.
The 0.18 s actuator delay is left unchanged, but identical cached lagd values
on consecutive routes must not be described as independent fresh estimates.

### Radar integration requires more than plausible field distributions

The initial radar parser inherited Panda bus 1 from pre-repin Toyota code,
whereas this branch uses stock Toyota-B: ADAS/camera on the 0/2 relay and
EPS/Brake on unsplit bus 1. Its synthetic test fed the same wrong bus and did
not exercise that topology mismatch.

The first joined-object analyzer also indexed by segment and a repeating
B2:B3 value, overwriting earlier bursts after wrap. A streaming, time-bounded
join is required. Full-corpus reconstruction still supports the recovered
relative-speed field, but cycle identity, validity, track lifetime, lateral
sign/scale, and vision correspondence are being independently reviewed before
calling the RadarPoint path qualified.

### Continuous signer loses host-command liveness

The archived continuous helper replaces every distinct native B6 while the
last C7 sequence is nonzero. Its branch-to-NOP change removes one-shot
consumption without introducing command expiry. Native B6 arrivals can
therefore keep a stale host target active after host updates cease. The
historical steering witness does not establish host-loss behavior. This is an
adapter lifecycle defect, not a reason to add another engagement policy to
CarController or Panda.

## Completed independent radar-unit review

`data/generated/camry_2026_radar_anchors.json` and its raw-object-byte fixture
retain 17 original rlog identities and independent vision/gyro observations.
They supersede the prior direct FFD-to-CAN scale transfer:

| Quantity | Corrected observed wire interpretation | Independent anchor |
|---|---|---|
| Range | unsigned B0:B1 × 0.005 m | 1,953 vision-associated observations: r=0.998518, slope=1.029071, median absolute error 0.799 m |
| Lateral | signed12 B2:B3[7:4] × 0.04 m, left-positive | 240 off-center vision observations: slope=0.982563; 27,602 continuity-qualified gyro pairs: r=0.843106 and inferred LSB=0.038909 m/count |
| Relative speed | signed low14 B1:B2 × 0.025 m/s; B1[7:6] excluded | vision-speed slope=0.992347; signed12 wraps 113 retained high-closing-speed observations |

The previous range/range-rate correlation could not determine their common
scale: both were doubled. Signed13 and signed14 velocity interpretations agree
on the retained data; the wider field boundary is not independently resolved.
Object validity/confidence and silent same-slot reassignment are also not
resolved. The corrected parser remains available for offline/replay inspection;
normal CarParams retains the model-only radar-unavailable path until object
validity/lifecycle is established.

The corrected full August reconstruction consumes each time-bounded occurrence
rather than overwriting repeated counter values: 30,532 / 35,994 complete
four-record bank bursts. Its kinematic agreement is corroboration, not a
substitute for the independent unit anchors above.

## Completed diagnostic recovery review

FRC_P5 monitor 199 defines control modes 1/2/4 as distance control and mode 3
as conventional constant-speed cruise. Recovery now requires a distance-control
mode as well as the permission flag and a clear ACC-not-available flag. Truncated
DID1903/1905/1906 values are errors, never implicit false/no-fault booleans.
ISO-TP response-pending no longer terminates a transaction, malformed single
frames are rejected, and sequence errors cannot produce partial success.

The pre-clear snapshot is written atomically **before** the first clearing
request. A later timeout preserves that snapshot, completed clear responses,
and the failure instead of discarding the diagnostic evidence. Six offline
regression tests cover these cases, including an injected mid-clear failure
and final Panda ownership cleanup. Same-cycle physical DRCC restoration is
still a vehicle observation, not established by these tests.
