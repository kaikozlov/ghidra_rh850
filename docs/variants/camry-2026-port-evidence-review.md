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
