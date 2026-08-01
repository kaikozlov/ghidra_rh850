# TSS 3.0 EPS family comparison

> **Document type:** variant comparison
>
> **Status:** partial
>
> **Evidence grade:** mixed (per-cell; see the CSV)

The machine-readable canonical matrix is
`data/tss3_eps_variant_matrix.csv`. This page is the narrative orientation;
the CSV holds the populated rows.

## Comparison matrix (summary)

| Property | Sienna `8965B4512000` | Corolla `8965F1208000` | Confidence |
|---|---|---|---|
| MCU family | RH850/P1M-E `R7F701381` (confirmed) | unknown | high for Sienna only |
| Application SA levels | level 2 (`03/04`) functional; level 1 stub | suspected same template | Sienna verified; Corolla hypothesis |
| Application SA secret | recovered at CodeFlash `0x20840` | unknown | Sienna verified |
| Bootloader payload format | confirmed (AES-CBC + CRC32 + CMAC gate) | unknown | Sienna verified |
| Application service table | 17 SIDs (incl. proprietary `0xAB`/`0xBA`) | 13 SIDs answering (subset); `0xAB`/`0xBA` present | Sienna verified; Corolla field-confirmed |
| `0xAB` semantics | event-record service (3 subfns, checkpoint-backed) | present (field), semantics inferred from Sienna | Sienna verified; Corolla hypothesis |
| `0xBA` semantics | inert echo (null callback, no-op) | present (field), semantics inferred from Sienna | Sienna verified; Corolla hypothesis |
| `0x34` application behavior | no-op echo (real handler bootloader-only) | silent (field), consistent with application mode | Sienna verified; Corolla hypothesis |
| Diagnostic endpoints | `0x7A1` physical, `0x777` functional, `0x7A0` limited secondary | partially observed in field behavior | Sienna verified |
| DDB vocabulary template | NA `EPS_CAN_P4DK` (30 DTCs, 75 monitors) | JP `EPS_P4DK4` has 13 extra bridged DIDs (JP-market features) | Sienna verified; P4DK4 is JP-market variant, not newer generation |
| SecOC profile | six RX PDUs; command-7 verify selects slot 4; live key state unknown | unknown | Sienna firmware path verified; slot contents unobserved |

Unobserved fields are recorded as `unknown` in the CSV, never fabricated.

## What "same software family" does and does not mean

Matching application DID/service tables in a related EPS are strong Denso
software-continuity evidence. They do **not** prove:

- the related MCU;
- byte-identical bootloader contents;
- retained secrets or payload routines;
- that a PROGRAMMING timeout must be external to the EPS.

## Adding a variant

1. Add a row to `data/tss3_eps_variant_matrix.csv` (evidence-graded fields;
   `unknown` for unobserved).
2. If the firmware is in hand, create a `variants/<name>-<partnumber>.md`
   using the Corolla page as the template.
3. Update this page's summary matrix.
