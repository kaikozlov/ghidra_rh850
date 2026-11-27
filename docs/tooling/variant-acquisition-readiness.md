# Variant acquisition readiness checker

> **Scope:** offline firmware triage and RH850/P1M-E acquisition readiness
>
> **Tool:** `tools/variants/check_variant_acquisition.py`
>
> **Verification:** `tests/variants/verify_variant_acquisition_readiness.py`
> (`tools/test variant_acquisition_readiness`)

## Purpose

Run the checker before importing an acquired image:

```sh
uv run --locked python -m tools.variants.check_variant_acquisition DUMP \
  -o build/out/target-evidence/acquisition-readiness.json
```

For readable inputs and valid sidecars, the checker emits a report even when
the acquisition gate fails. It neither modifies the image nor opens Ghidra
or contacts hardware. Use `--run-json` to bind an acquisition record,
`--manifest` to check a manifest against the image hash, and `--notes` to
record provenance.

Regenerate the registered comparison catalog with:

```sh
uv run --locked python -m tools.variants.check_variant_acquisition \
  --registered-targets -o data/generated/variant_acquisition_readiness.json
```

## Triage method

The checks describe the selected CodeFlash region at the estimated load base
where applicable:

| Field | Evidence |
|---|---|
| `architecture` | Erased and high-entropy input; ARM Thumb, PowerPC, and V850/RH850 vector signatures. RH850 confidence also uses decoded `INTBP` writes and direct `gp`/`tp` initialization. |
| `container_triage` | Bare vectors or a `0x8000`-byte DataFlash prefix; entropy, erased fraction, and non-erased bounds by region. |
| `load_address_vote` | Reset target and candidate mappings from an initialized `INTBP` to an in-range interrupt pointer table. |
| `vector_entries` | 16-byte reset-vector slots decoded from the vendored SLEIGH encodings, with branch, pointer, and unsupported entries distinguished. |
| `uds_table_candidates` | Candidate resident and application service tables and supporting compare instructions. |
| `ccp_xcp_candidates` | Candidate route constants and selector/handler tables. |
| `crc_table_constants` | Addresses of matching CRC-32, reflected `0xA001`, and CRC-16/CCITT table prefixes. |

`structure_triage` summarizes the
[P1M-E structural scanner](rh850-codeflash-structure-scanner.md) when the
selected CodeFlash region is exactly 1 MiB. Candidate matches do not enter
the acquisition or resolver-readiness verdict.

## Output contract

`variant-acquisition-readiness-v1` reports triage fields at the top level:

- `acquisition` records the input's size and SHA-256 and checks for exactly
  1 MiB of bare CodeFlash. An optional acquisition record must report a
  complete capture and have the same SHA-256. Peeling a DataFlash prefix
  for triage does not change the acquisition verdict.
- `ready` is the acquisition verdict, not a resolver verdict. On a
  single-image report the command exits `0` when `ready` is true and `1`
  otherwise.
- `resolver_readiness` checks the same acquisition conditions and, if
  supplied, the manifest hash. It reports readiness without running the
  resolver.

`--registered-targets` emits one report per registry entry in the
[`variant-acquisition-readiness-catalog-v1` catalog](../../data/generated/variant_acquisition_readiness.json).

## External-tool evaluation

The external checks did not replace the native checks on the seven
registered images:

- **cpu_rec** found V850 as the largest chunk in every registered image and
  in a synthetic DataFlash-prefixed image. It returned no whole-file
  architecture for six registered images and reported ARC32eb for Venza.
  It provided neither container nor load-base evidence.
- **Binbloom** inferred little endian and base zero only for the RAV4 Prime
  meter. With those settings supplied, its UDS candidate fell inside the
  known application table on all five EPS images, but it missed the tables
  on Venza and the meter. Treat its addresses as candidates, not table bounds.
