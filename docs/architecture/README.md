# Architecture

Boot flow, execution architecture, and the control/safety partition.

| Report | Scope |
|---|---|
| [firmware-architecture.md](firmware-architecture.md) | Application vector/executable base, EIINT table, foreground loop, CAN1 routing, module census |
| [boot-validity-and-flash-lifecycle.md](boot-validity-and-flash-lifecycle.md) | Boot validity gate, CRC descriptors, validity markers, flash program/erase lifecycle |
| [control-partition.md](control-partition.md) | Control/safety partition: torque path, safety monitors, mode cluster boundaries |
| [system-mode-cluster.md](system-mode-cluster.md) | System-mode cluster: shutdown/reset mode machinery and handoff paths |

These reports describe *how the firmware runs*. For what the firmware *stores*,
see [../storage/README.md](../storage/README.md); for how it talks on CAN, see
[../communications/README.md](../communications/README.md).
