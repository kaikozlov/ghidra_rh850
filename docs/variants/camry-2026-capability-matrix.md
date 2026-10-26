# 2026 Camry openpilot capability matrix

**Current port:** the maintainer's 2026 Camry Hybrid uses **`0x08A` for both
lateral and longitudinal control**, integrated with the EPS-resident request
signer. This is the maintained port, not a proposed successor to a lateral-only
runtime.

## Evidence and implementation identity

- **Maintainer report, 2026-10-26:** both axes have been in use with the signer
  setup for approximately a month.
- **Source inspected, 2026-10-26:** sibling `../kai-openpilot`, branch
  `tss3-camry-port`, commit `f9d6e3883ec5d54a55d63e9b6e2d24b39c7f426f`;
  its pinned `opendbc_repo` is `90aeb85b7cf68a2eb7103b2bd645ed41ff3598bd`.
  The controller, interface, signer transport and Toyota safety code establish
  the implementation described below.
- **Local build supplied by the maintainer:** `build/out/tss3-oracle/`.
  This is local workspace, not a tracked deployment record or a substitute for
  source/capture provenance.

The target is EPS `8965F3307000 / 8A3113303100`. Source inspection establishes
software behavior; the maintainer report establishes reported use. Capture
measurements retain their own software and vehicle identities in the linked
reports. Neither an old route nor a passing software check assigns a blanket
qualification grade to a different build.

## Current capabilities

| Area | Maintained implementation | Evidence owner |
|---|---|---|
| Lateral | Standard openpilot angle control is encoded in `CONTROL_REQUEST` (`0x08A`) and passed through the signer | [Port report](camry-2026-tss3-opendbc-port.md) |
| Longitudinal | TSS3 advertises Alpha Long. With the toggle enabled, `openpilotLongitudinalControl` is true and the controller supplies acceleration through the same `0x08A` request. With it disabled, the transport preserves stock longitudinal fields | [Port report](camry-2026-tss3-opendbc-port.md) |
| Topology and ownership | Repinned Toyota-B: chassis/state on bus 0, FRC on bus 2, auxiliary/radar on bus 1. Panda controls forwarding of the replaced FRC request | [Runtime contract](../architecture/toyota-tss3-minimal-runtime.md) |
| Authentication | EPS-resident request signer; openpilot owns the application request and publication. Bringup tooling is separate from driving control | [Runtime contract](../architecture/toyota-tss3-minimal-runtime.md) |
| Vehicle state and faults | TSS3 CarState decodes vehicle, cruise and steering state; fault interpretation remains tied to the recovered signal rather than an invented OEM fault class | [EPS transmit surface](camry-f33-eps-tx.md), [fault/status report](camry-2026-tss3-fault-status.md), [evidence review](camry-2026-port-evidence-review.md) |
| Radar | TSS3 RadarInterface assembles object tracks; unit and lifecycle measurements have independent retained fixtures | [Evidence review](camry-2026-port-evidence-review.md#radar-units-and-lifecycle) |
| Cancel and HUD | The controller implements cancel output and HUD replacement. Implementation is distinct from what any particular older cancel capture demonstrates | [Port report](camry-2026-tss3-opendbc-port.md), [cancel evidence](camry-2026-port-evidence-review.md#cancellation-evidence) |
| PCS handling | The current controller and safety code recognize the native PCS request flag and return request ownership to the FRC | [PCS observation and implementation](camry-2026-tss3-opendbc-port.md#pcs-observation-and-implementation) |

## Evidence navigation

- [Longitudinal request/result evidence](camry-2026-longitudinal-evidence.md)
  owns the wire interpretation and remaining unnamed fields. `0x160` is not
  the port's longitudinal command.
- [Field witnesses](toyota-tss3-openpilot-bounty-evidence.md) retain measured
  steering/coexistence results for their named configurations; they are not
  the current implementation specification.
- [Vehicle-movement architecture](../architecture/toyota-tss3-vehicle-movement-arbitration.md)
  owns the request/arbitration/controller distinction. Unresolved native
  FRC/Brake internals do not mean the implemented request-plane port is blocked.
- [Porting contract](../architecture/toyota-openpilot-porting-contract.md)
  owns software responsibilities and evidence requirements.

Do not summarize this port as “lateral road-qualified, longitudinal blocked.”
Use the capability and evidence source relevant to the question instead.
