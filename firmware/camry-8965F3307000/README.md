# 2026 Camry EPS `8965F3307000`

Canonical first-class firmware inputs for the maintainer-operated 2026 Camry EPS.

- `CodeFlash.bin`: 1,048,576 bytes, SHA-256
  `42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`
- `DataFlash.bin`: 32,768 bytes, SHA-256
  `231fbdde4ef317931d8f1ff20ff131650f7d773c124a179b0ae3dc98bf8e4432`

Acquisition/provenance is retained under `targets/camry-2026/raw-20260826/`.
`CodeFlash.bin` is the exact lower 1 MiB of the complete acquired transport dump;
`DataFlash.bin` is byte-identical to the retained `FF200000..FF208000` acquisition.
Analysis-target metadata is pinned in `data/analysis_targets.json`.
