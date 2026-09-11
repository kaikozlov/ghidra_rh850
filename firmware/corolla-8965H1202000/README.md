# Corolla EPS `8965H1202000` analysis image

Canonical physical analysis inputs for the contributor-reported 2023 Corolla
EPS. `8965H1202000` is the retained historical image label from auxiliary DID
`0x2032`; direct application F181 reports `8965F1208000/8A3111202000`.

- `CodeFlash.bin`: exact retained normalized 1 MiB CodeFlash, SHA-256
  `0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f`
- `DataFlash.bin`: exact retained physical 32 KiB DataFlash, SHA-256
  `8ac2a6beecb4ca2e6caf695eebffe440478171b4e093a1b2a36ab4e4ff313299`

The deterministic producer and source identities live in
`tools/targets/corolla/builders/promote_corolla_analysis_inputs.py`.
