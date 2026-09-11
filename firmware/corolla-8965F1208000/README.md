# Corolla EPS `8965F1208000` analysis image

Canonical physical analysis inputs from the retained Span 2025 Corolla
acquisition. The MCU is an R7F701383: only the lower 1 MiB CodeFlash and lower
32 KiB DataFlash are physical arrays. The discarded CodeFlash suffix is all
`0xFF`; the upper half of the 64 KiB host DataFlash range is not DataFlash.

- `CodeFlash.bin`: normalized 1 MiB CodeFlash, SHA-256
  `fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6`
- `DataFlash.bin`: physical 32 KiB prefix of the first retained read, SHA-256
  `7d339a531b911b97a1d3d0bbeb45938aa996dcc856a0951f6c74ed42c67c1d58`

The deterministic producer and source identities live in
`tools/targets/corolla/builders/promote_corolla_analysis_inputs.py`.
