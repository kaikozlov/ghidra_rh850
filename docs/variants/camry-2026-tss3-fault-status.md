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

**Simultaneous-class precedence.** After startup and invalid-input selection,
`512E4` chooses `02 > 04 > 10 > (20/F0/status22) > 40 > 0F > 08`.
Classes `0F/08` select rows14/13 only when operational helper `510E0`
returns0; otherwise they select16. Class80 inhibits the deepest normal path,
but special row15 takes precedence over that inhibit. Retained A5 bits only
decorate rows6/8 versus7/9; A5 alone cannot select a fault row.
Counts are sampled before aging, flag banks afterward. Status22 detection
`51266` runs after aging: its rising edge selects row11 immediately, while
its new activity is consumed on the following invocation. Decisive branches
are `513A6..51480`.

**Event ownership.** `51C66` reports failure only once per current-event
transition; repeated failure reports do not add class references.
`51D5E` releases a reference only when the old current bit was set.
Healthy-observation API `51E2C` updates a separate bitmap and does not release
the fault. Direct accumulator `50FC8` increments unsigned16 with wrap;
release `514BC` saturates at zero and preserves latched flags.

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

## 5. Exact-F33 classifier ages, request gate and capture eligibility

The seven unsigned words at **`0x30E40`** are
`[200, 200, 600, 22170, 200, 200, 1000]`, with distinct consumers:

| ROM word | Owner | State / comparison |
|---|---|---|
| `0x30E40=200` | `0x5110A`, called by `0x511B6` | primary flags `FEBE82A3`, activity `FEBE82A6`, age `FEBE82CA`; clear when age **>200** and request gate permits |
| `0x30E42=200` | `0x5110A`, called by `0x511B6` | aggregate flags `FEBE82A4`, activity `FEBE82A7`, age `FEBE82CC`; same clear rule |
| `0x30E44=600` | `0x5116C`, called by `0x511B6` | retained class-02/04 flags `FEBE82A5`, activity `FEBE82A8`, age `FEBE82CE`; clear when age **>600** |
| `0x30E46=22170` | `0x5110A` | unsigned owner-4 request snapshot **`FEBEE8B0 >= 22170`**, enabling A3/A4 clear |
| `0x30E48=200` | `0x512E4` | startup A: `FEBE82B6 >200` |
| `0x30E4A=200` | `0x512E4` | startup B: `FEBE82B8 >=200` |
| `0x30E4C=1000` | `0x52DA4` | separate diagnostic-capture eligibility counter `FEBE6166` |

**Bank aging.** `0x511B6` calls the helpers only for nonzero flag banks;
zero banks freeze both age and pending activity. Activity exactly `0x5A` is
consumed and resets age before increment, producing age **1**. The helpers
increment only while age is at or below its threshold, then clear the entire
flag byte only when the resulting age is strictly above it. Thus 199→200 and
599→600 retain flags; 200→201 and 600→601 can clear them. A3/A4 also require
the request gate; A5 does not. A blocked gate holds a normally advancing age
at 201; supplied already-over-threshold ages, including 65535, hold unchanged.
Cleared banks freeze on subsequent calls. Decisive comparisons are
`0x5113E..0x51154` and `0x5119A..0x511A6`.

The request is published by `0xBF3AA` (`0xBF5CC..0xBF5D0` copies owner-4
request `FEBEBCC2` to `FEBEE8B0`), after `0xBACA8` updates owner 4 through
`0xBB736`. **22170 is a request-level threshold.**
`0x50FC8` asserts class flags/activity and increments active class reference
counts; `0x514BC` releases those counts without clearing the latched banks.
Count increments are unsigned16; releases hold at zero. `0x51266` adds the
status-22 edge contribution after bank aging, for consumption on the next call.

**Startup and reset.** `0x512E4` runs injection, aging and input predicates
before startup selection. With both startup flags `FEBE82A1/A2=5A`, it
increments B6 and publishes row 1, then clears A1 only above 200. With A2=5A
and A1 clear, it increments B8 and publishes row 2, then clears A2 at 200.
From zero these take 201 and 200 eligible calls; each crossing call still
publishes its startup row. Ordinary selection begins on the following call.
Inactive phase counters hold; synthetic 65535 increments wrap to zero.
`0x51592` clears class counts/banks and loads ages 200/200/600, preserving
activity and startup state. `0x50FAE` only reloads those ages on mode entry.
`0x515D4` separately rearms startup flags/counters. `0x515E6` invokes both
initializations, additionally clears `82A9` and sets `82B0=5A`
(`51602: 8903`, `51606: 900B`).

The class-02 source helper `0x510B6` injects only when `FEBE82AF !=5A`
and source `FEBE6764` bit15 is high. Once set, **82AF stays 5A for either
high or low input** (`0x510BA..0x510D8`); it does not refresh activity.
Application-work-state initializer `0x59448` clears it at `0x59EB6`.
Neither `0x51592` nor startup rearm `0x515D4` clears it.

**Capture eligibility.** `0x52DA4` reads 1000 at `0x52DC0`. With latch
`FEBE615A=0`, age below 1000 increments; age at or above 1000 resets to zero
and sets the latch to 5A. Thus 999→1000 leaves the latch zero until the next
call. Any nonzero latch freezes both fields. `capture_diagnostic_event`
at `0x52E18` uses latch 5A and a distinct nonzero DTC to admit a second
non-qualified capture; accepted slot-2/3 paths clear the latch at `0x52EF4`
without resetting age. Qualified captures bypass this eligibility check;
the first non-qualified slot can be written before it. Capture initialization
paths including `0x52F32` and `0x53092` set latch 5A/age zero.

**Scheduling and evidence.** The EIC136-polled foreground chain is
`0x66062 -> 0x667E6 -> 0x58B5E -> (0x5F464 | 0x5F91C)`.
Mode >=`0x102` dispatches capture aging every foreground generation and
classifier aging only with generation-mask bit1, selected every other completed
generation. The loop polls a pending request, so delayed work can coalesce
timer requests. These are invocation counts, without elapsed-time guarantees.

The 20 retained **`camry_f33_recovery_`** scenarios in
`decomp/camry-8965F3307000/oracles.jsonl` reproduce bank/gate boundaries,
capture eligibility, startup crossing and next-row behavior, sticky input
interruption and reset scope. All executed as `verified-local-execution`:
**2106 original instructions**, with no overlays or stubs. Inputs are synthetic,
explicitly bounded owner state, external predicates and a 256-byte stack;
no clocks or blanket-RAM initialization are supplied.

### Event clearing and command-gate independence

Count reset `51592` preserves DEM current-event bits. A repeated failure
after that reset is still deduplicated and does not reacquire its class.
RAM-generation clear `516DC -> 5255A` instead clears current, first-history
and healthy-observation bitmaps, retaining second history; a later failure
can reacquire the class. In service mode `E856=11`, `516DC` preserves the six
ROM-listed events `0E,51,BE,FF,20,120`. Their classes are01 or00, so restoring
them does not reassert supported classifier counts.

Classifier output and command inhibition have separate owners. Every
projected classifier cell `82A0/82AA..82AE` has only `4C24A` as its
non-initialization direct reader, for Tx projection. The command gates instead
follow `5737A(owner,request) -> 572E6 -> 8B28 -> FCC00 -> EEF90 -> BCAA6`.
`BCAA6` derives `AC29=(EEF90&70017001)!=70017001` and
`AC2A=(EEF90&40004)!=0`; `D042C` zeros `CC66` when `AC29==0` or `AC2A!=0`.
`D047C` subsequently selects the final command as described in
[live baseline §66.3](camry-2026-live-baseline.md#663-four-independent-post-b6-gates-can-erase-or-replace-a-valid-cooperative-command).

A continuous original-byte sequence exercises the classifier, request
aggregation, snapshots and `D042C`: row6 can coexist with `CC66=1200`;
recovered row0 can coexist with `CC66=0` under a retained output request.
Removing that request through original `5737A` restores the command.
Classifier aging is therefore not a command-recovery timer.

All thirteen standalone `camry_f33_fault_lifecycle_*.json` scenarios passed
exact-image execution across `build/out/firmware-question-campaign/`
`fault-lifecycle-wave1`, `wave2` and `wave3`. They cover simultaneous priority,
real event fail/pass/healthy reporting, 201/601-call aging, request thresholds,
startup, edge/latch retention, count wrap, both clear modes and the independent
command gate. Initial inputs are explicitly synthetic and bounded; retained
histories evolve through original firmware calls without CodeFlash overlays.

## 6. `0x351` force-status boundary

The canonical [EPS Tx §5](camry-f33-eps-tx.md#5-0x351-base-status-and-qualified-action-override)
owns the recovered qualification, snapshot, ancillary router, override and hold behavior.
`FEBE6764` snapshots qualified action-class word `FEBE71EC`.
Qualification bit15 is separate from bit15 of the selected records' fourth, ancillary aggregate.
The latter recomputes `FEBE8143` as `5A` or zero.

F33 DID `0x1156` is a separate object: callback `0x4E4CE` reads `GP-0x5074`
(`FEBE678C`), not the qualification snapshot at `GP-0x509C` (`FEBE6764`).

## 7. Openpilot mapping

The [vehicle-state review](camry-2026-port-evidence-review.md#fault-projections)
owns the CarState fault mapping and its evidence.
The [capability matrix](camry-2026-capability-matrix.md) owns port status.
