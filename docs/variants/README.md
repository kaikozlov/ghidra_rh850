# Variants

Sienna is the analyzed calibration. The Corolla and the wider TSS 3.0 EPS
family are related variants — findings transfer as **hypotheses to check**,
not facts.

| Variant | Firmware | Status | Report |
|---|---|---|---|
| Sienna (China) | `8965B4512000` | Fully analyzed (this repo) | [sienna-8965B4512000.md](sienna-8965B4512000.md) |
| Corolla | `8965F1208000` | Firmware not yet in hand; template hypotheses only | [corolla-8965F1208000.md](corolla-8965F1208000.md) |
| TSS 3.0 family | various | Partial comparison matrix | [tss3-family-comparison.md](tss3-family-comparison.md) |

## The transfer rule

Matching application DID/service tables in a related EPS are strong
software-family evidence. They do **not** prove the related MCU, byte-identical
bootloader contents, retained secrets/payload routines, or that a PROGRAMMING
timeout must be external to the EPS. Every transferred claim starts at grade
**hypothesis** until checked against the variant's own bytes.

The machine-readable comparison data lives in
`data/tss3_eps_variant_matrix.csv`.
