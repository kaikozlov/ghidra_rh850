# Communications

CAN and ISO-TP transport, and the application receive/transmit maps.

| Report | Scope |
|---|---|
| [diagnostic-transport.md](diagnostic-transport.md) | Bootloader CAN/ISO-TP diagnostic transport path |
| [application-rx.md](application-rx.md) | Application receive map: 47 normal Rx I-PDUs, 242 COM signals, acceptance rules |
| [application-tx.md](application-tx.md) | Application transmit map: 11 active CanIf routes, 6 COM I-PDUs, 58 COM signals |

## Machine-readable canonical maps

The CSVs in `data/` are canonical for exact rows; the reports teach how to
read them:

- `data/application_rx_signal_evidence.csv` — RX signal evidence (drives
  `tools/generate_application_rx_map.py`);
- `data/application_diagnostic_map.csv` — per-SID diagnostic routing, session
  policy, callbacks;
- `data/control_partition.csv` — control-partition map.

CAN `0x344` is **absent** from this firmware's acceptance table, descriptors,
and the RX CSV — do not project related-variant expectations onto it.
