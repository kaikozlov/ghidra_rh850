# 2026 Camry TSS3 exact-F33 fault/status contract

This report owns the exact `8965F3307000` EPS fault classifier, `0x394`
projection and DTC-table analysis. The
[vehicle-state review](camry-2026-port-evidence-review.md#fault-projections)
owns the CarState fault mapping.

Canonical machine-readable evidence:

- `data/generated/camry_8965F3307000_fault_status_decompiler_evidence.json`
- `data/generated/camry_8965F3307000_fault_status.json`
- `tools/test camry_8965f3307000_fault_status`

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

Decode ambiguous tuples as candidate sets. The
[CarState fault mapping](camry-2026-port-evidence-review.md#fault-projections)
uses a separate current fault/inhibit projection.

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

### Family diagnostic vocabulary

The GTS+ family dictionaries contain the following communication labels.
Query them with `tools/gts dtc DATABASE CODE`; exact-F33 support is determined
by the event/table join above.

| Database | Code | Reported peer |
|---|---|---|
| `EMPS_P5` | `U012987`, `U012687`, `U023A87` | Brake, steering-angle sensor, image-processing module A |
| `EMPS_P5` | `U110487`, `U118487` | Driving Support ECU, Advanced Drive controller |
| `FRC_P5` | `U013187`, `U012987`, `U012687`, `U023587` | EPS, Brake, steering-angle sensor, front radar |
| `ABS_P5`, `Brk_Bst_P5` | `U013187`, `U11B187` | EPS and EPS channel 2 |

`U013187` belongs to `EMPS2_P5`, not `EMPS_P5`. The latter contains
`U013087` (Steering Effort Control Module) and `U118F87` (Steering Actuator
Control Module). Both steering dictionaries expose `0x1CEF` **Target
Lateral ID (System 2)**; Camry install set `0x1FB8` contains no category
499 EMPS2. Brake/booster DID `0x102F` bit 74 is **EPS/Steering Control
Actuator ECU Communication Open**, with 0=Normal and 1=Under intermittent
when byte8 mask `0x20` advertises support (zero-based); byte9 mask `0x20`
is the value. In the retained Camry `f700fd007c00a9000000` response that
support bit is clear, so this monitor is unavailable. See the
[GTS length/support contract](../tooling/techstream.md#brake-monitor-response-length-and-field-support).

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

If observed, `0x351` code7/flag identifies a distinct forced/special status input.

## 7. Openpilot mapping

The [vehicle-state review](camry-2026-port-evidence-review.md#fault-projections)
owns the CarState fault mapping and its evidence.
The [capability matrix](camry-2026-capability-matrix.md) owns port status.
