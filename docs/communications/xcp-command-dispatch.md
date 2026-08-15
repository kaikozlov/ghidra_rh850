# Application calibration-command dispatch

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence source:** firmware-static
>
> **Confidence:** verified disclosure + direct RAM-write primitives; bounded
> downstream write impact
>
> **Canonical artifact:** `data/recovered_callback_tables.csv`
>
> **Verification:** `tests/verify_function_discovery.py`,
> `tests/verify_xcp_security.py`, `tests/verify_xcp_shadow_write_live.py`,
> `tests/verify_exploit_followups.py`, `AssertXcpShadowWriteBoundary.java`,
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

The same firmware path exposes an unauthenticated memory disclosure on the
paired CAN `0x7F7` request / `0x7F8` response route. The configured generic
command map has no GET_SEED (`0xF8`) or UNLOCK (`0xF7`) callback. After CONNECT
(`0xFF`), SET_MTA (`0xF6`) accepts a tester-supplied 32-bit address without an
authorization check and the custom UPLOAD command (`0xF5`) returns one to seven
bytes from permitted LocalRAM. The `0xE4` page-copy command first makes
CodeFlash `0x10000..0x17DEF` readable by copying it to permitted LocalRAM
`0xFEBF7C00..0xFEBFF9EF`. Repeated uploads therefore recover 32,240 CodeFlash
bytes exactly.

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

## Security path

All request frames are eight bytes. This is the minimal firmware-static proof
sequence; the final request is repeated, using a shorter length for the last
fragment.

| Operation | Request bytes | Effect |
|---|---|---|
| CONNECT | `FF 00 00 00 00 00 00 00` | sets the protocol connected state |
| copy page | `E4 00 00 00 01 00 00 00` | copies CodeFlash `0x10000..0x17DEF` to RAM |
| SET_MTA | `F6 00 00 00 00 7C BF FE` | selects RAM `0xFEBF7C00` (little-endian) |
| UPLOAD | `F5 07 00 00 00 00 00 00` | returns seven bytes and advances the MTA |

The `0xF5` range checker permits LocalRAM `0xFEBE0000..0xFEBFFFFF` except five
inclusive intervals encoded at `0x293F4`:

- `0xFEBE0000..0xFEBE37FF`
- `0xFEBE5030..0xFEBE529B`
- `0xFEBF0288..0xFEBF13CB`
- `0xFEBF4958..0xFEBF4B33`
- `0xFEBF6C00..0xFEBF78DF`

That leaves 107,924 readable RAM bytes. The checker rejects requests crossing
an exclusion and rejects address wraparound. The page-copy destination lies
outside every exclusion.

The copied interval does not contain the bootloader secrets at `0xBFD8` and
`0xBFE8` or the application SecurityAccess secret at `0x20840`; this finding
does not claim direct key disclosure.

### Generic write commands are real direct RAM writes

The same unauthenticated generic command map contains standard XCP-shaped
`DOWNLOAD` (`0xF0`, callback `0x80F12`) and `MODIFY_BITS` (`0xEC`, callback
`0x80FD8`). These are not merely configuration records for a hypothetical
calibration writer.

`DOWNLOAD` obtains the current MTA from `FEBE4FF4`, accepts 1–6 tester bytes in
an eight-byte CTO, validates the complete interval against both LocalRAM
`0xFEBE0000..0xFEBFFFFF` and the narrower write window
`0xFEBF7C00..0xFEBFFBFF`, then directly stores each tester byte to `MTA+i`.
After success it advances MTA to `end+1`. Repeated six-byte-or-smaller requests
therefore cover any contiguous portion of the entire 32 KiB window, including
the complete window from start through `0xFEBFFBFF`.

`MODIFY_BITS` uses the same MTA and write-window validation, requires word
alignment, and performs an in-place 32-bit masked read-modify-write. Neither
command has a GET_SEED/UNLOCK prerequisite because those command slots are not
configured in this image.

That is a firmware-static **unauthenticated arbitrary 32 KiB LocalRAM write
primitive**, with two important impact bounds. First, the containing LocalRAM
memory block is read/write but non-executable. Second, an exhaustive live-project
census over all defined function instructions finds exactly three direct
references into `0xFEBF7C00..0xFEBFFBFF`, all `WRITE` references to the base
`FEBF7C00` (`0x142E`, `0x62652`, `0x976E4`). It finds zero function-owned direct
`READ`, `PARAM`, call/jump, or other references and zero function entries inside
the window. The current static graph therefore does **not** establish a callback
pointer, executable alias, persistent-flash consumer, or motor-control consumer
for attacker-written bytes. Runtime-only aliasing or computed consumers remain
a bounded unknown; the absence of direct xrefs is not a universal non-use proof.

The security conclusion is therefore stronger than the earlier
"calibration-shadow write configuration" description but still bounded:
**write capability is verified; downstream control/RCE/persistence impact is not.**

Firmware-static evidence proves CAN1 acceptance and response construction, not
that an external vehicle gateway or diagnostic connector forwards CAN
`0x7F7/0x7F8`. Any live confirmation belongs on an isolated bench and should
exercise only the read chain. The default-plan/simulation tool
[`../../exploit/followups/xcp_read_probe.py`](../../exploit/followups/xcp_read_probe.py)
operationalizes that bounded proof, requires an F181-bound isolated bench for
live mode, and implements no generic write command.

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
