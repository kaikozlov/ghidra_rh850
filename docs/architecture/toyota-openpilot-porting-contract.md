# Toyota openpilot porting contract

Use the normal upstream openpilot, opendbc and Panda division of responsibility.
Deviate only when target-native evidence requires it. Unknown semantics stay
unmapped; do not add guards, timers or state machines merely to compensate for
uncertainty.

This document owns integration rules, not vehicle status. The
[Camry capability matrix](../variants/camry-2026-capability-matrix.md) owns the
maintained port; [target reports](../variants/README.md) own other specimens.

## Software ownership

| Layer | Responsibility |
|---|---|
| openpilot | Engagement, driver interaction, planning and lateral/longitudinal control |
| opendbc interface | Vehicle identification, platform configuration and CarParams |
| CarState / RadarInterface | Decode vehicle observations into the standard interfaces |
| CarController | Translate CarControl into vehicle requests with the normal limiting helpers |
| Authentication transport | Deliver authenticated requests without taking over driving policy |
| opendbc safety / Panda | Independently enforce the permitted command surface and forwarding policy |
| Development/bringup tools | Prepare and inspect the environment; remain separate from engagement policy |

Reuse the owner that already exists. A signer is not another controller; a
bringup status flag is not another engagement state machine. Keep transport
availability and vehicle-control semantics distinct.

## Generation and authentication are separate

TSS/TSS2/TSS3 describes the ADAS/control generation: request vocabulary,
feedback, source ownership, radar and UI. SecOC/TSK describes message
protection and security architecture. Neither determines the other.

Do not assign an ADAS generation from the presence of SecOC, or add the
`SECOC` platform flag merely because a vehicle is TSS3. The curated
[variant matrix](../../data/toyota_eps_variant_matrix.csv) records these axes
separately.

The same numeric CAN ID is not proof of the same interface. Verify message
length, fields, integrity, producer and consumer on the target. Corolla's
64-byte `0x183`, for example, is not the older Toyota 8-byte ACC command.

## Enter Toyota's request pipeline

The Camry interface separates:

1. application requests (`0x08A`);
2. arbitration result/status (`0x081`); and
3. downstream controller instructions and actuator behavior.

Use the application-request side while retaining Toyota's arbitration and
actuator controllers. The detailed evidence belongs in the
[vehicle-movement report](toyota-tss3-vehicle-movement-arbitration.md) and
[longitudinal report](../variants/camry-2026-longitudinal-evidence.md).
Authentication makes a protected request deliverable.

## Source replacement and timing

Identify the native publisher, physical route and interception boundary for
each replaced message. Keep capture bus labels tied to their harness
configuration; they do not select runtime topology.

For each command family, specify:

- which source is forwarded or replaced;
- which component owns application data and authentication state;
- request cadence and receiver supervision;
- behavior on release, invalid commands and transport loss; and
- coexistence with native interventions and driver inputs.

Do not race a stock source or use freshness collisions as arbitration.
The [runtime contract](toyota-tss3-minimal-runtime.md) owns the maintained
TSS3 topology and signer boundary; do not duplicate them in per-checkpoint
roadmaps.

## Decode observations without inventing semantics

Vehicle speed, steering angle/rate, physical driver torque, cruise state,
pedals, gear, readiness and faults must reach the normal CarState fields.
Use target evidence for their scale, validity and transitions.

A temporary/permanent fault classification requires evidence for that
distinction. A lossy aggregate cannot identify its underlying cause or prove
that restart is required. Diagnostic names and recorder offsets are leads,
not automatic CAN-field mappings.

The same rule applies to radar validity, track identity, UI state and
longitudinal policy fields. Retain unknown fields as unknown rather than
inventing OEM names, confidence percentages or behavioral rules.

## Evidence provenance

Record how each finding is known:

- **Source inspection:** what the identified software implements.
- **Firmware analysis:** what the exact target bytes and dataflow establish.
- **Capture analysis:** what happened in the named vehicle/configuration.
- **Maintainer or contributor report:** attributed behavior.
- **Software/model tests:** the behavior or invariant actually exercised.

Record vehicle observations with their software, harness and runtime identities.
Preserve useful observations and source provenance; delete obsolete implementation
descriptions.

## Upstream prior art

The reproducible upstream Toyota comparison is
[`toyota_porting_contract.json`](../../data/external/opendbc/toyota_porting_contract.json),
pinned to commaai/opendbc `c9b31d21bc396e8958891e271936bdbdf1a6ca93`.
It records older Toyota command builders, platform flags, CarState, radar,
SecOC and safety ownership.

Useful transferable patterns are standard CarControl/CarState integration,
source replacement in safety, generation-specific DBCs, independent command
limits and separate authentication. Old wire IDs, scaling and fault enums
are not transferable without target evidence.

## Evidence owners

- [Camry port](../variants/camry-2026-tss3-opendbc-port.md): integration and
  request/state observations.
- [Camry longitudinal evidence](../variants/camry-2026-longitudinal-evidence.md):
  acceleration bounds, result quantities and unnamed policy fields.
- [Camry fault/status](../variants/camry-2026-tss3-fault-status.md): exact-EPS
  fault behavior and projection limits.
- [Corolla H/F state bridge](../variants/corolla-h-f-openpilot-state-bridge.md):
  target-specific state and capture joins.
- [TSS3 runtime](toyota-tss3-minimal-runtime.md): signer and host ownership.
