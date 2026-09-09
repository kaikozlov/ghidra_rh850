# Application asynchronous operation queue

The application has one shared four-slot asynchronous-operation queue centered on
`FEBE828C` (active operation), `FEBE828E/828F` (queue indices), and
`FEBE8290[4]` (pending operations). It is shared across Dcm services and internal
application recovery logic; it is not owned by one diagnostic SID.

The firmware contains **five real operation numbers: `1`, `2`, `4`, `5`, and
`6`**. There is no operation `3` in this calibration. The five starter bodies
write those exact literal values while idle, and replay dispatcher `0x50996`
recognizes exactly the same set. No function writes queue value `3`.

Canonical machine-readable ownership is in
`data/application_async_operation_queue.csv`.

## Operation ownership

| Operation | Starter | Active | External owner | Initializer | Completion |
|---:|---:|---:|---|---|---|
| `1` | `0x50698` | `0x81` | SID `0x14` ClearDiagnosticInformation (`0x4C9DA`) | `0x50660` | selector `0x11` through `0x4C430` |
| `2` | `0x50760` | `0x82` | RoutineControl RID `0x1108` (`0x4F4CA`) | `0x5070C` | selector `10` through `0x4C430` |
| `4` | `0x507EA` | `0x84` | internal CAN/RTE recovery helper `0x35658` | `0x50660` | no selector; falls through to replay |
| `5` | `0x50864` | `0x85` | RoutineControl RID `0x1004` (`0x4F17E`) | `0x50858 -> 0x5449E` | selector `3` through `0x4C430` |
| `6` | `0x50922` | `0x86` | WDBI DID `0x0204` completion (`0x4EC0A`) | `0x508E6` | `0x4C474`, which resolves pending selectors `3` and/or `10` |

Every starter also has exactly one replay-dispatch caller in `0x50996`. The
non-replay owner is therefore explicit for all five operations.

### Operation 1: ClearDiagnosticInformation

SID `0x14` state worker `0x4C9C6` starts operation 1 and stores shared Dcm word
`FEBE816A = 0x1410`. Low byte `0x10` is the pending marker. Queue monitor
`0x50A1C` waits until the shared maintenance status bytes leave `0xAA/0xA5`, then
reports success/failure through **selector `0x11`**, not compact selector `1`.

That distinction is important. `0x4C430` sends selectors below `0x10` to the
compact RoutineControl-style selector bank, but selector `0x11` takes the shared
Dcm path. If the current shared word's low byte is `0x10`, `0x4C430` replaces it
with result `0` or `0x20`, producing `0x1400` or `0x1420`. Re-entered
`0x4C9C6` then clears the word and returns success or failure instead of response
pending.

This closes a temporary analysis false positive: ClearDiagnosticInformation is
**not** statically stuck pending. The apparent mismatch came from initially
reading the queue selector as `1`; the firmware encodes `0x11`.

Operation 1 and internal operation 4 share initializer `0x50660`, which resets
maintenance/history working groups including status bytes `FEBE5F5D` and
`FEBE6128`. That shared implementation does not make operation 4 diagnostic.

### Operations 2, 5, and 6

These are the persistent diagnostic workflows recovered separately:

- operation `2`: RoutineControl `0x1108`, repeatable no-speed checkpoint reset;
- operation `5`: RoutineControl `0x1004`, repeatable no-speed event-log/history
  persistence rewrite;
- operation `6`: WDBI `0x0204` post-response maintenance/reset workflow.

Operations 2/6 and 5/6 intentionally coalesce. Operation 6 completion uses
`0x4C474`, which updates compact selector 10 and/or selector 3 when those
RoutineControl requests are pending.

### Operation 4: internal selector-less maintenance

Operation 4 has no diagnostic owner. Its only non-replay starter call is
`0x3568C` in helper `0x35658`; the exact callers of that helper are in the
CAN/RTE application paths at `0x5E1B8`, `0x5E1DE`, and `0x5E7D0`. The helper
contains no reference to the compact diagnostic selector bytes or shared Dcm
word `FEBE816A`.

Operation 4 shares initializer `0x50660` with operation 1 and becomes active
state `0x84`. Monitor `0x50A1C` has terminal branches for `0x81`, `0x82`,
`0x85`, and `0x86`, but deliberately no `0x84` selector branch. Once the shared
maintenance status bytes are no longer pending, execution simply reaches replay
`0x50996`; replay clears `FEBE828C` before examining the pending ring and
advancing the queue. Operation 4 is therefore a **finite, selector-less internal
maintenance action**, not a latched queue defect and not a hidden diagnostic
service.

## Verification boundary

- `tests/verify_application_async_operation_queue.py` pins queue function hashes,
  literal operation numbers, absence of operation 3, replay cases, external
  ownership, the SID-`0x14` selector-`0x11` completion bridge, and selector-less
  operation-4 completion.
- `tests/verify_application_async_operation_queue_live.py` runs
  `AssertApplicationAsyncOperationQueue.java` against the accepted project and
  pins exact starter/helper/queue-state xref topology.

The census is architectural rather than a new actuation primitive. It closes the
shared async ownership boundary and prevents the diagnostic operations 2/5/6 or
internal operation 4 from being mistaken for unrelated queue numbers or service
owners.
