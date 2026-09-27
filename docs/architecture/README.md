# Architecture

Boot flow, execution architecture, and the control/safety partition.

**Target grounding:** the firmware-static reports below are grounded in the
legacy Sienna EPS `8965B4512000` image — each report header declares its exact
scope. The `toyota-*` reports combine external-source design analysis and
dated TSS3 implementation checkpoints; `openpilot-port-quality-benchmarks.md`
is a pinned upstream survey. These are not Sienna firmware facts or an
evergreen description of deployed software. Cross-calibration evidence lives
in [the variant index](../variants/README.md).

| Report | Scope |
|---|---|
| [firmware-architecture.md](firmware-architecture.md) | Application vector/executable base, EIINT table, foreground loop, CAN1 routing, module census |
| [boot-validity-and-flash-lifecycle.md](boot-validity-and-flash-lifecycle.md) | Boot validity gate, CRC descriptors, validity markers, flash program/erase lifecycle |
| [control-partition.md](control-partition.md) | Control/safety partition: torque path, safety monitors, mode cluster boundaries |
| [openpilot-port-quality-benchmarks.md](openpilot-port-quality-benchmarks.md) | Upstream openpilot/opendbc port-quality bar (2026-09-13 snapshot) used to grade the TSS3 integration |
| [toyota-openpilot-porting-contract.md](toyota-openpilot-porting-contract.md) | Pinned comma Toyota prior art translated into the TSS3 command/state/ownership/safety roadmap |
| [toyota-tss3-minimal-runtime.md](toyota-tss3-minimal-runtime.md) | Runtime architecture checkpoints, including the request-plane supersession of the earlier C7/B6 design |
| [toyota-tss3-vehicle-movement-arbitration.md](toyota-tss3-vehicle-movement-arbitration.md) | Toyota vehicle-movement-manager request/arbitration/result/target architecture joined to TSS3 `0x08A` / `0x081` / B6 |
| [toyota-request-invalidation-us20230166772.md](toyota-request-invalidation-us20230166772.md) | Close read of US20230166772A1: selective client invalidation/priority, latched handoff, and rejection feedback joined to TSS3/P6 evidence |
| [toyota-selected-id-direct-request-arbitration.md](toyota-selected-id-direct-request-arbitration.md) | Close read of US20200070873A1: Toyota's selected-application-ID + direct-request latency optimization and its exact-F33 boundary |
| [toyota-tss3-era-patent-landscape.md](toyota-tss3-era-patent-landscape.md) | 2019-2026 Toyota/Toyota-affiliated patent families for VMM arbitration, fail classes, source rejection, gateway topology, SecOC, steering, and attention tracking |
| [toyota-driver-monitoring-us20220001874.md](toyota-driver-monitoring-us20220001874.md) | Deep review of Toyota US20220001874A1: steering touch, driver-monitor attention, hands-off timers, and exact-F33 transfer boundaries |
| [system-mode-cluster.md](system-mode-cluster.md) | System-mode cluster: shutdown/reset mode machinery and handoff paths |

The Sienna reports describe *how that firmware runs*. For what the firmware
*stores*, see [../storage/README.md](../storage/README.md); for how it talks on
CAN, see [../communications/README.md](../communications/README.md).

## Machine-readable canonical map

- `data/control_partition.csv` — the control/safety cyclic-partition map
  (see [control-partition.md](control-partition.md)).
