# 2026 Camry openpilot capability matrix

**Current port:** the maintainer's 2026 Camry Hybrid uses **`0x08A` for both
lateral and longitudinal control**, integrated with the EPS-resident request
signer.

## Evidence and implementation identity

- **Maintainer report, 2026-10-26:** both axes have been in use with the signer
  setup for approximately a month.
- **Source inspected, 2026-11-17:** sibling `../kai-openpilot`, branch
  `tss3-camry-port`, commit `469e8a0163ed5294cf2079a93616f6a4e431c4ad`;
  its pinned `opendbc_repo` is `8e1dd8e66d263876d8291b50b3ad160ace9b8c33`
  (`tss3-refine`). Both checkouts were clean and matched their remote heads.
  The controller, interface, signer transport and Toyota safety code establish
  the implementation described below.
- **Capture inspected, 2026-11-17:** route
  `5211e3c6c7b088d3/0000013e--27d453251c` records clean openpilot
  `433eb007b8bbf014677557b08af83d7854f09778`, whose tree and opendbc pin
  equal the inspected checkout. It uses non-PCM openpilot longitudinal.
  The [port report](camry-2026-tss3-opendbc-port.md) owns its measured
  steering-reference and request-tracking results.

The target is EPS `8965F3307000 / 8A3113303100`. Linked capture reports retain
their software and vehicle identities.

## Current capabilities

| Area | Maintained implementation | Evidence owner |
|---|---|---|
| Lateral | Standard openpilot angle control is encoded in `CONTROL_REQUEST` (`0x08A`) and passed through the signer | [Port report](camry-2026-tss3-opendbc-port.md) |
| Longitudinal | TSS3 advertises Alpha Long. With the toggle enabled, `openpilotLongitudinalControl` is true and the controller supplies acceleration through the same `0x08A` request. With it disabled, the transport preserves stock longitudinal fields | [Port report](camry-2026-tss3-opendbc-port.md) |
| Topology and ownership | Repinned Toyota-B: chassis/state on bus 0, FRC on bus 2, auxiliary/radar on bus 1. Panda controls forwarding of the replaced FRC request | [Runtime contract](../architecture/toyota-tss3-minimal-runtime.md) |
| Authentication | EPS-resident request signer; openpilot owns the application request and publication. Bringup tooling is separate from driving control | [Runtime contract](../architecture/toyota-tss3-minimal-runtime.md) |
| Vehicle state and faults | TSS3 CarState decodes vehicle, cruise and steering state; fault interpretation follows the recovered signal | [EPS transmit surface](camry-f33-eps-tx.md), [fault/status report](camry-2026-tss3-fault-status.md), [evidence review](camry-2026-port-evidence-review.md) |
| Radar | TSS3 RadarInterface assembles object tracks; unit and lifecycle measurements have independent retained fixtures | [Evidence review](camry-2026-port-evidence-review.md#radar-units-and-lifecycle) |
| Cancel and HUD | The controller implements cancel output and HUD replacement | [Port report](camry-2026-tss3-opendbc-port.md), [cancel evidence](camry-2026-port-evidence-review.md#cancellation-evidence) |
| PCS handling | The current controller and safety code recognize the native PCS request flag and return request ownership to the FRC | [PCS observation and implementation](camry-2026-tss3-opendbc-port.md#pcs-observation-and-implementation) |

## Evidence navigation

- [Longitudinal request/result evidence](camry-2026-longitudinal-evidence.md)
  owns the wire interpretation and remaining unnamed fields. `0x160` is not
  the port's longitudinal command.
- [Field witnesses](toyota-tss3-openpilot-bounty-evidence.md) retain measured
  steering/coexistence results for their named configurations.
- [Vehicle-movement architecture](../architecture/toyota-tss3-vehicle-movement-arbitration.md)
  owns the request/arbitration/controller distinction and remaining
  FRC/Brake implementation questions.
- [Porting contract](../architecture/toyota-openpilot-porting-contract.md)
  owns software responsibilities and evidence requirements.
