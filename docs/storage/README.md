# Storage

Persistent storage: the 32 KiB DataFlash and the NvM object model.

| Report | Scope |
|---|---|
| [dataflash.md](dataflash.md) | Complete 32 KiB map: 122 physical records, triplicate bank, checkpoint ring, SecOC object bank, access gates |

## Machine-readable canonical maps

- `data/dataflash_nvm_records.csv` — all 122 physical records with logical
  owners (regenerate with `make generate-dataflash`);
- `data/checkpoint_payload_map.csv` — all 32 checkpoint descriptors, direct
  writers, structural layouts, evidence limits.

## Important notes

- Pages 0–255 are outside both configured persistent-object classes; erased
  DataFlash readback is undefined, so their prior use is indeterminable.
- Pages 432–479 are the full 16-object SecOC triplicate bank.
- `application_dataflash_range_allowed` (`0x4EAD8`) rejects accesses
  overlapping pages 480–511 and optional-object pages 432–443.
- DIDs `0x201/0x202/0x203` are volatile bootloader inputs, **not**
  DataFlash-backed.
