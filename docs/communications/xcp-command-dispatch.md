# Application calibration-command dispatch

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence source:** firmware-static
>
> **Confidence:** verified dispatch structure; recovered handler roles
>
> **Canonical artifact:** `data/recovered_callback_tables.csv`
>
> **Verification:** `tests/verify_function_discovery.py`,
> `AssertRecoveredCallbackTables.java`, `AssertFunctionDiscoveryFloor.java`

## Result

The application contains a seven-entry command table at CodeFlash `0x2B3F0`.
`FUN_00097160` walks exactly seven eight-byte records, compares the request
selector with byte zero, loads the little-endian callback from record offset
four, and invokes it through the computed `jarl r29,lp` at `0x971A2`. The
handler bodies and their shared response builder match an XCP-shaped
calibration command family. That protocol identification is recovered from the
firmware behavior; no OEM symbol or external specification is used as naming
evidence.

| Selector | Pointer field | Handler | Body bytes | Structural role |
|---:|---:|---:|---:|---|
| `0xFB` | `0x2B3F4` | `0x9729A` | 74 | response builder |
| `0xFA` | `0x2B3FC` | `0x972FA` | 96 | indexed-identifier response |
| `0xF5` | `0x2B404` | `0x97432` | 100 | bounded upload response |
| `0xF3` | `0x2B40C` | `0x97546` | 168 | bounded checksum response |
| `0xEB` | `0x2B414` | `0x975EE` | 122 | page-state writer |
| `0xEA` | `0x2B41C` | `0x97668` | 104 | page-state reader |
| `0xE4` | `0x2B424` | `0x976F4` | 106 | guarded page-copy operation |

Every target begins at an independently decoded function boundary, has a
bounded return, is not an alternate entry into another function, and is pinned
by exact body size and SHA-256 in the canonical CSV. The handlers converge on
the response helper at `0x9724E`, which builds an eight-byte response in RAM at
`0xFEBE5E94`.

## Reproducibility and remaining boundary

`SeedRecoveredCallbackTables.java` validates the table bytes, selector order,
dispatcher instructions, target hashes, and boundaries before creating the
seven functions and `USER_DEFINED` pointer references. A clean four-stage
rebuild therefore recovers them without interactive edits. The asserting floor
also covers the other firmware-proven indirect tables and rejects any literal
call whose destination lacks an exact function entry.

The nearby 60-pointer array at `0x27C88..0x27D77`, including the wrapper-shaped
targets referenced by `0x27D08..0x27D54`, is intentionally not seeded. Its
bytes are valid CodeFlash pointers to entry-shaped runs, but this image has no
referenced executable walker or computed-call consumer. It remains
`unresolved-reviewed` in `data/outside_function_candidates.csv`; prologue shape
and pointer shape alone do not prove dispatch.
