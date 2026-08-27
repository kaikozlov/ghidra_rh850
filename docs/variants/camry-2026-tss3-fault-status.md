# 2026 Camry TSS3 exact-F33 fault/status contract

This report closes the **static, target-native** meaning of the 2026 Camry
`8965F3307000` EPS `0x394` status carrier far enough to expose its OEM internal
classifier state safely in a passive openpilot port. It does **not** define
openpilot `steerFaultTemporary` / `steerFaultPermanent`, and it does not enable
CAN output.

Canonical machine-readable evidence:

- `data/generated/camry_8965F3307000_fault_status_decompiler_evidence.json`
- `data/generated/camry_8965F3307000_fault_status.json`
- `tests/verify_camry_8965F3307000.py`

The normalized target remains exact `8965F3307000`, SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`.

## 1. Target-native 17-state classifier

F33 function `0x512E4` is the exact target classifier feeding `0x394`. It calls
F33's own class accumulator and latch helpers, then indexes a 17×5 table at
**`0x2A19C`**. The five-byte rows are:

| State | c0 | c1 | c2 | c3 | c4 | Recovered role |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 0 | 0 | 0 | 0 | 0 | deepest clear/normal classifier path |
| 1 | 4 | 3 | 0 | 0 | 0 | startup/settling hold A |
| 2 | 4 | 7 | 0 | 0 | 0 | startup/settling hold B |
| 3 | 5 | 3 | 0 | 0 | 0 | internal input invalid/unavailable predicate |
| 4 | 4 | 3 | 0 | 0 | 0 | retained row; no direct selector recovered |
| 5 | 1 | 1 | 0 | 0 | 0 | retained row; no direct selector recovered |
| 6 | 3 | 3 | 2 | 1 | 2 | class `0x02`, secondary latch set |
| 7 | 3 | 3 | 2 | 1 | 0 | class `0x02`, secondary latch cleared |
| 8 | 6 | 3 | 3 | 0 | 2 | class `0x04`, secondary latch set |
| 9 | 6 | 3 | 3 | 0 | 0 | class `0x04`, secondary latch cleared |
| 10 | 3 | 7 | 1 | 1 | 1 | class `0x10` family |
| 11 | 3 | 7 | 4 | 1 | 1 | class `0x20` / `0xF0`-compatible aggregate plus independent source |
| 12 | 6 | 7 | 7 | 0 | 1 | class `0x40` branch |
| 13 | 6 | 7 | 6 | 0 | 1 | class `0x08` branch under operational helper |
| 14 | 6 | 7 | 5 | 0 | 1 | class `0x0F` branch under operational helper |
| 15 | 2 | 2 | 0 | 0 | 0 | distinct special operating state |
| 16 | 4 | 7 | 0 | 0 | 0 | fallback/not-normal operational inhibit branch |

The table bytes happen to equal the H-family table, but the conclusion above is
not transferred from H: `0x512E4` itself uses **F33 `0x2A19C`**, and the selected
functions are body-hash-bound to the exact F33 image.

The important F33 functions are:

- `0x50FC8`: DEM class accumulator;
- `0x510B6`: additional class-`0x02` injection from one internal status bit;
- `0x510E0`: operational helper;
- `0x5110A`, `0x5116C`, `0x511B6`: latch aging;
- `0x51208`: invalid/unavailable predicate;
- `0x51266`: additional state-11 source;
- `0x512E4`: 17-state classifier/table projection;
- `0x51592`: initialization.

## 2. Exact `0x394` wire projection is lossy

The previously recovered F33 Tx path is `0x4C24A -> 0x4CE08`. `0x394` carries
four of the state-table columns in this order:

`(column4, column1, column2, column3)`.

That produces the following target-native candidate map:

| `0x394` projected tuple | Candidate internal state(s) |
|---|---|
| `(0,0,0,0)` | **`0` only** |
| `(0,1,0,0)` | `5` |
| `(0,2,0,0)` | `15` |
| `(0,3,0,0)` | `1,3,4` |
| `(0,3,2,1)` | `7` |
| `(0,3,3,0)` | `9` |
| `(0,7,0,0)` | `2,16` |
| `(1,7,1,1)` | `10` |
| `(1,7,4,1)` | `11` |
| `(1,7,5,0)` | `14` |
| `(1,7,6,0)` | `13` |
| `(1,7,7,0)` | `12` |
| `(2,3,2,1)` | `6` |
| `(2,3,3,0)` | `8` |

So an all-zero `0x394` projection uniquely identifies F33's **internal state 0**.
That is useful telemetry, but it is not independently the same thing as DID
`0x1033 Ready Status`, nor is it authorization to steer. The two ambiguous tuples
must remain candidate sets; inventing a single state would discard information
that the wire format genuinely does not carry.

The passive opendbc implementation therefore exposes an internal state candidate
set and a unique state only when the tuple is unambiguous. Public
`steerFaultTemporary` and `steerFaultPermanent` remain unchanged/false. This is
implemented in nested opendbc commit
`0d5773bd393bbf3d4109728171d2390b60fcde16` and parent `kai-openpilot` commit
`191aeb43df3fb72f3264209be1aad57b9ca42e2d`. The complete nested gate passes
**4,077 tests / 719 skipped**, plus Ruff, ty, codespell, cpplint, and MISRA.

## 3. F33 DEM class accumulator

`0x50FC8` target-natively accumulates the fault-class families used by
`0x512E4`: `0x02`, `0x04`, `0x08`, `0x0F`, `0x10`, `0x20`, `0x40`, `0x80`, and
supported class `0xF0`. Class `0x01` exists in the event catalog but is not a
recovered classifier input.

The exact F33 DEM event table is **`0x2FC50`**, 384 records × 8 bytes. The class
byte is record `+1`, and the DTC index is record `+2`. Its populated class census
is:

| Class | F33 events |
|---|---:|
| `0x01` | 8 |
| `0x02` | 34 |
| `0x04` | 1 |
| `0x08` | 1 |
| `0x0F` | 1 |
| `0x10` | **171** |
| `0x20` | 16 |
| `0x40` | 1 |
| `0x80` | 7 |

That is **240 classified events**. H has 242 because its class-`0x10` population
is 173.

Across all 384 records, F33 differs from H in only 31 records. Twenty-nine of
those differences are an unrelated record flag byte. The only class changes are:

- event `0x0085`: class `0x10 -> 0`;
- event `0x0088`: class `0x10 -> 0`.

The exact corresponding DTC records remain present and byte-identical, so the
pinned Toyota `EMPS_P5` vocabulary joins them unambiguously:

- `0x0085`: **C10051C — Control Module Internal Temperature Sensor "B" —
  Circuit Voltage Out of Range**;
- `0x0088`: **C10001C — Control Module Internal Temperature Sensor "A" —
  Circuit Voltage Out of Range**.

Those two thermal events therefore no longer drive F33's `0x394` class-`0x10`
state even though the named DTC records themselves remain available.

The only DTC-index change in the event table is `0x00AC`, which changes from H
index 120 to F33 index 0. The corresponding DTC record itself changes from
`8710d10001000000` to `8710d10000000000`, disabling it on F33.

## 4. Exact F33 DTC table and Toyota-name join

The exact F33 DTC table relocates to **`0x30850`**. F33 references 80 DTC indexes,
with maximum index 133. Every one of those 80 referenced 8-byte records is
byte-identical to the corresponding H record.

That matters for evidence grading: Toyota `EMPS_P5` DTC descriptions are not
being copied because the vehicle family looks similar. They are joined through
identical packed-DTC bytes already pinned in the Techstream corpus. The only H/F
record difference in the referenced union is the disabled index 120 described
above, and F33 no longer references it.

## 5. F33 latch/aging constants are not H constants

The classifier calibration words at exact F33 **`0x30E40`** are:

`[200, 200, 600, 22170, 200, 200, 1000]`.

Target-native use establishes:

- primary class-latch age: `200`;
- aggregate class-latch age: `200`;
- class-`0x02`/`0x04` secondary-latch age: `600`;
- primary-clear enable age: **`22,170`**;
- two startup/settling holds: `200` and `200`.

The following `1000` word remains unnamed here. Most importantly, the F33
primary-clear threshold is **22,170**, whereas the H calibration used **17,736**.
The H number must not be transferred to Camry.

These are classifier counter thresholds. Without an independently proved counter
period/context they are not promoted to a wall-clock temporary/permanent-fault
policy.

## 6. `0x351` force-status boundary

The neighboring F33 `0x351` path is also more closed than the first passive-port
artifact, but not enough to assign every source an OEM display name.

Target-native F33 `0x3C008` walks 24 records and ORs several verified ushort
fields. Its fourth aggregate flows to `0x3C6A8`; **aggregate bit15** causes
`0x3C6A8 -> 0x4C5E8` to write `0x5A` into `GP-0x36BD`. F33 `0x4C216` then forces
`0x351` status code **7** and sets its companion flag iff:

`(GP-0x509C & 3) != 0 && GP-0x36BD != 0`.

Thus the force-7 topology is target-native and independent of the base status
producer. What remains unnamed is the broad 16-bit status object at
`GP-0x509C`: exact F33 references test bits 0, 1, and 15, but current evidence
does not recover unique Toyota names for bits0/1. It is also **not** F33 DID
`0x1156`; target DID1156 callback `0x4E4CE` reads `GP-0x5074` instead. No
diagnostic name is transplanted onto `GP-0x509C`.

This is enough to treat `0x351` code7/flag as a distinct forced/special status
input if the carrier is observed, but not enough to map it to openpilot's
permanent/temporary split.

## 7. Openpilot consequence

The static work now supports three conservative statements:

1. `0x394` can expose exact F33 internal classifier state candidates, including a
   unique state0 all-clear projection.
2. `0x394` DEM class families, target-specific aging constants, and exact Toyota
   DTC joins are known without Corolla transfer.
3. None of that alone defines `steerFaultTemporary` or `steerFaultPermanent`.

A relay-correct live capture that exercises asserted and recovery transitions is
still the correct policy discriminator. Driver-override and motor-current
response limits remain separate policy work; acquisition/representation clamps
must not be repurposed as safety thresholds.

**Production output remains disabled.** `SafetyModel.noOutput`, zero controller
CAN output, the absent production `0x0B6` whitelist, and the shadow-only safety
path are unchanged.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [VAR-059](../reference/index.md#finding-var-059)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
