# Variants

Sienna `8965B4512000` is the analyzed calibration. Sienna `8965B4514000`, the
Corolla, and the wider TSS 3.0 EPS family are related variants — findings
transfer as **hypotheses to check**, not facts.

| Variant | Firmware | Status | Report |
|---|---|---|---|
| Sienna (China) | `8965B4512000` | Fully analyzed (this repo) | [sienna-8965B4512000.md](sienna-8965B4512000.md) |
| Sienna (Vance partner) | `8965B4514000` | External field report pinned; firmware/raw outputs unavailable | [sienna-8965B4514000.md](sienna-8965B4514000.md) |
| Corolla | `8965F1208000` | Field probes done; firmware not yet in hand | [corolla-8965F1208000.md](corolla-8965F1208000.md) |
| RAV4 Prime (2024 field experiment) | exact F181 pending | Live persistent-patch/openpilot experiment reported; static forced-profile interpretation only | [rav4-prime-forced-secoc-profile.md](rav4-prime-forced-secoc-profile.md) |
| TSS 3.0 family | various | Partial comparison matrix | [tss3-family-comparison.md](tss3-family-comparison.md) |

## The transfer rule

Matching application DID/service tables in a related EPS are strong
software-family evidence. They do **not** prove the related MCU, byte-identical
bootloader contents, retained secrets/payload routines, or that a PROGRAMMING
timeout must be external to the EPS. Every transferred claim starts at grade
**hypothesis** until checked against the variant's own bytes.

The machine-readable comparison data lives in
`data/tss3_eps_variant_matrix.csv`.
