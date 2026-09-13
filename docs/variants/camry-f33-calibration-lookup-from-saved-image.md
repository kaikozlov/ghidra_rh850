# F33: exact calibration lookup inputs from the retained ECU image

2026-09-12. Offline recovery research using the existing firmware and GTS+
artifacts. No vehicle request, reset, flash write, authentication bypass or
new executable payload was performed. A working network repair is not established.

## A silent EPS need not prevent identifying the package to request

The archived image contains the backing data for the actual assembly-number
read. This is stronger than stripping a part-number-looking prefix from F18C
or trusting a used-parts listing. The exact retained lookup tuple is:

| Manufacturer search field | Retained value | Evidence |
|---|---|---|
| ECU assembly number / `ecuAssyNo` | `8965033K90` | Exact DID 0105 backing object, valid checksum and marker. |
| First `baseSwNo` | `8965F3307000` | Normal F181 producer's first fixed-width record. |
| Second `baseSwNo` | `8A3113303100` | Normal F181 producer's second fixed-width record. |
| VIN | Use the owner's actual VIN in the authorized lookup. | Not derived from the EPS part number and not published here. |

These are original-image lookup inputs, **not fabricated current diagnostic
responses**. They can identify a part-specific inquiry or supported calibration
search without first making the silent EPS answer. This does not prove that
Toyota offers a matching restore package, that the frontend supports importing
these fields, or that a programmer is currently reachable.

## Exact firmware source chain

The source is the complete retained `8965F3307000` factory CodeFlash image,
SHA-256 `42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`.
Fresh exact-target Ghidra and raw instructions establish:

1. RDBI record `292BC` selects DID `0105`, length 12 and callback `4D93C`.
   That callback calls `66DFC` with object `0204`; its failure reply is ten
   question marks plus two NUL bytes, not a fallback part-number string.
2. `66DFC` selects ROM-object family `0200`, index 4. `67208` checks it through
   `67090 -> 67060`, then copies from the descriptor's ROM source pointer via
   `66E2E`. It does not copy from the adjacent RAM-mirror pointer.
3. Descriptor `2AFBC` is a 16-byte object with RAM mirror `FEBEF670` and ROM
   source `A0A0`. The stored marker is `A55A5AA5`; the ten data bytes are
   `8965033K90`. CRC over the object and its checkword is `FFFFFFFF`.
4. `4D93C` requires the validated object's marker, copies precisely those ten
   bytes and appends two NUL bytes. This establishes the actual DID-value
   origin, rather than a string-search association.
5. The independent serial object `0207` is also checksum-valid and its saved
   serial agrees with the retained original F18C response. The whole
   manufacturing-data span `A000..FFFF` is unchanged in the complete saved
   incident reconstruction. This is archive agreement, not a new flash dump.
6. Normal F181 producer `4FA26` reads 16-byte fields at `20860` and `17DC0`.
   Its separate compatibility-failure placeholder branch remains distinct;
   the two actual identifiers above match the retained preincident F181.

The object lives outside the application's CRC input and outside the normal
upper-region erase. Thus upper application restoration does not require
rewriting this known assembly/serial data. A corrupted candidate's part text
must not be allowed to redefine which trusted baseline the audit uses.

## Same-release GTS+ uses those same two diagnostic inputs

The current installed `GetPartNumber_DT.dll` was inspected directly, not
inferred from its V18 counterpart. Its input SHA-256 is
`ae05a7f705a2eebf78514b935b50cf1162fec0cb449198224b4f5ff133ca17b3`.

The plugin initially obtains selector `66` at `10001403`. In current EMPS
metadata this is a `3E00` initializer, **not the final part-number request**:
the plugin replaces its send/mask/check lists with its own literals.
The optional assembly branch uses `220105 / FFFFFF / 620105` at
`100051BC/100051C0/100051C4`, then sends at `100015A5` and parses one
12-byte record after the three-byte response header.

The software branch uses `22F181 / FFFFFF / 62F181` at
`100051C8/100051CC/100051D0`, sends at `100017BF`, and consumes the count at
response byte 3 followed by 16-byte records from offset 4 at `100017E9..1000180B`.
The assembly and software strings populate separate output members.

The already-recovered Toyota/TIS acquisition flow maps these separate values to
`ecuAssyNo` and `baseSwNoLst`. It submits the actual VIN and receives candidate
software IDs, filenames and package URLs from the service. That recovered host
flow does not authorize guessing a download URL from a current software ID,
faking a healthy ECU reply, or skipping normal manufacturer authorization.
See the existing acquisition evidence in `docs/tooling/techstream.md`, TMS-049
and TMS-050, for the request/result ownership distinctions. Toyota bulletin
T-SB-0021-25 separately describes model/ECU-specific calibration packages and
the required Security Signature for GTS+ reprogramming.

## Reproduction and result

The existing saved-image comparator now reports
`retained_factory_calibration_lookup`, explicitly sourced from its hash-checked
factory reference and never from candidate-supplied descriptors or text:

```sh
uv run python tools/targets/camry/analysis/analyze_camry_f33_recovery_image.py SAVED_CODEFLASH.bin
uv run python tests/verify_camry_f33_recovery_image.py
```

The fourteen portable tests pass. New cases pin the DID callback/object pointer,
checkword and reference-source semantics, and prevent altered candidate text
from becoming trusted lookup identity. Original comparisons reproduce unchanged:
stage 6 differs by 488 bytes, incident by 492, with 476 outside CRC inputs in
both cases; all these differences remain in the native upper erase domain.
The tool obtains no live image, evaluates no calibration package, generates no
replacement bytes and changes no authorization or programming behavior.

## What this closes, and what it does not

This removes an avoidable dependency on a fresh assembly-number read for the
**package inquiry**. It does not close the network-entry problem. The retained
archive plus the native programming code support a conditional route through
matching authorized firmware restoration, native verification and the normal
bootloader reset; the custom archived writer's DONE/halt is not that lifecycle.

The exact F33 package search in the retained CUW corpus remains empty. Public
exact-identity searches in this pass supplied no matched package or independent
network recovery procedure. No authenticated Toyota lookup result was obtained,
no prepared-state EPS response was observed and no restoration was run. A
checksum-valid retained identity is not evidence that the live ECU executes.


## Separate cold-versus-warm transport check

A different possible cause of silence was checked: could the normal live
programming handoff and cold invalid-image fallback use the same CAN-register
values but a different input clock? The common boot initializer is
`1398 -> 1338 -> 3B3C` for both entries. Its `396C` global write selects
`DCS=0`; `3978` uses the same nominal/data timing values. Renesas
R01UH0585EJ0120 Table 12.2 (p.469) and Tables 17.6/17.7 (p.791), rendered and
visually checked in this pass, identify `clkc=CLK_LSB` as **40 MHz fixed**.
The reconstructed modes therefore do not establish an overlooked 250-kbit/s or
1-Mbit/s cold recovery listener. This is configured behavior, not a live clock
measurement or proof against an electrical clock fault.

The cold handoff value `FF` is not simply a disabled-protocol flag:
`69D2` enables the boot protocol for either `0` or `FF`, and `6A22` initializes
its protocol state in both cases. The `0` path additionally performs the
synthetic programming-session handoff through `6504`; the `FF` path does not.
Thus cold and warm session state must still be distinguished, but the cold
configuration is not evidence of a second hidden address family or magic
network enable operation. None of this makes the boot runtime execute when the
cold selector has already entered the CRC-valid damaged application.
