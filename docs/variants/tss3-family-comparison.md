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

| Property | Sienna `8965B4512000` | Sienna `8965B4514000` | Corolla `8965F1208000` | Confidence |
|---|---|---|---|---|
| MCU family | RH850/P1M-E `R7F701381` (confirmed) | unknown | unknown | high for `4512000` only |
| Application SA levels | level 2 (`03/04`) functional; level 1 stub | unknown | suspected same template | `4512000` verified; other variants unknown/hypothesis |
| Application SA secret | recovered at CodeFlash `0x20840` | unknown | unknown | `4512000` verified |
| Bootloader payload format | confirmed (AES-CBC + CRC32 + CMAC gate) | external dump tooling exists; CodeFlash unavailable | unknown | `4512000` verified; no `4514000` firmware conclusion |
| Application service table | 17 SIDs (incl. proprietary `0xAB`/`0xBA`) | unknown | 13 SIDs answering (subset); `0xAB`/`0xBA` present | `4512000` verified; Corolla field-confirmed |
| `0xAB` semantics | event-record service (3 subfns, checkpoint-backed) | unknown | present (field), semantics inferred from `4512000` | `4512000` verified; Corolla hypothesis |
| `0xBA` semantics | inert echo (null callback, no-op) | unknown | present (field), semantics inferred from `4512000` | `4512000` verified; Corolla hypothesis |
| `0x34` application behavior | no-op echo (real handler bootloader-only) | unknown | silent (field), consistent with application mode | `4512000` verified; Corolla hypothesis |
| Diagnostic endpoints | `0x7A1` physical, `0x777` functional, `0x7A0` limited secondary | external report: bus 0, `0x7A1`/`0x7A9` physical | partially observed in field behavior | per-cell |
| DDB vocabulary template | NA `EPS_CAN_P4DK` (30 DTCs, 75 freeze-data monitors) | unknown | JP `EPS_P4DK4` has 13 extra seq-derived candidate DID bridges (JP-market features) | `4512000` verified; P4DK4 is JP-market variant, not newer generation; not a `CDbDidTable` join |
| Object 15 | 32-byte triplicate object; all copies invalid in captured dump | reported CMAC-validating candidate at same structural second-field address `0xFF206E14`; raw artifact unavailable | unknown | `4512000` verified; `4514000` external observation/structural alignment |
| SecOC profile | six RX PDUs; command-7 verify selects slot 4; `0x344` absent | same key reportedly validates sync plus `0x131`/`0x2E4`/`0x344`; EPS directions and runtime crypto unknown | external field IDs include `0x131`/`0x2E4`/`0x344`; firmware unknown | `4512000` firmware-static; other rows external/inference |

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
