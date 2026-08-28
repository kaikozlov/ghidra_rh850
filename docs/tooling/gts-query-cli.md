# GTS+ query CLI

`tools/gts` is the read-only discovery surface for Toyota GTS+/Techstream evidence.
It exists to make the OEM corpus usable as a Rosetta stone during firmware RE:
start from an unknown DID/DTC/CUW/contact type or a Toyota phrase, resolve the
OEM vocabulary and implementation route immediately, then return to target
firmware bytes for proof.

The command deliberately does **not** replace the deterministic Techstream/GTS+
extractors and verification suites. Those encode subsystem-specific evidence
boundaries. `tools/gts` only centralizes the already-shared mechanics needed for
interactive discovery.

## Command surface

```bash
tools/gts status

tools/gts search 'Advanced Drive Target Steering Angle'
tools/gts search 'Missing Message' --ecu EMPS_P5 --kind dtc
tools/gts search 0x1CEE --ecu EMPS_P5 --kind did

tools/gts ecu EMPS_P5
tools/gts role
tools/gts role 0x05
tools/gts role 0x19
tools/gts command HV_P5 0x19
tools/gts command EMPS_P5 0x52
tools/gts commset
tools/gts commset 1
tools/gts timer HV_P5 1
tools/gts category HV_P5
tools/gts canbus 12704
tools/gts canbus 'Camry HV' --json
tools/gts frame 397 0x01
tools/gts frame HV_P5 0x102
tools/gts did EMPS_P5 steering
tools/gts did EMPS_P5 0x1CEE
tools/gts dtc EMPS_P5 U012987

tools/gts route P5-Unified04
tools/gts cuw T-0051-26.cuw
tools/gts cuw 8A2810602100
tools/gts cuw list

tools/gts pe KgpDataCtrl.dll CDbDatamonitor
tools/gts pe TCUWCanReproStdFlashWriter.unpack.dll StartFlashWrite
```

`tools/gts role` also reports a binding-weighted `surfaces=` breakdown. Its
labels describe the recovered shared-runtime edge, not blanket vehicle I/O:
`direct_transport` means the plugin imports frame/send primitives itself;
`delegated_transport_v18_proven` means a stable current support-helper import has
an executable V18 path to frame/send; `support_cache_v18_proven` consumes cached
support response bytes; and the `unclosed`/`no_recovered` classes remain bounded
unknowns. For example, role `0x05` exposes the P4 cached-support versus P5
delegated-support evolution, while role `0x19` is direct transport for all 536
bindings.

All commands bootstrap the repository's locked `uv` environment themselves.
No venv activation or direct Python invocation is required. `--json` is
available on every subcommand for scripting. M/V OEM string decompression is
cached automatically under ignored `build/cache/gts/`, keyed by the source
DDB bytes plus the DDB parser implementation; a new GTS+ artifact or parser
change invalidates the cache. The first lookup pays the decode cost, subsequent
invocations reuse the decoded bytes. Up to four same-database generations are
kept so side-by-side GTS+ releases stay warm without unbounded cache growth.

## What the queries resolve

### DDB / OEM vocabulary

The default database is the current GTS+ `NA/DB/Gen` tree. `search`, `did`, and
`dtc` reuse `tools/techstream/parse_ddb.py` and `M_English.ddb` to resolve:

- P5/P6 Data List rows to primary/alternate DIDs and Toyota names;
- P5 DTC rows to Toyota DTC descriptions and failure types;
- behavior-code records to OEM names/comments;
- otherwise-unjoined OEM strings from current `M_English` by default. Add
  `--all-string-dbs` when the slower `V_English`/`U_English` UI contexts are
  relevant (the runtime selects among those string-table contexts).

Overlapping current table aliases (for example table 62 and 157 copies of the
same Data List entry) are deduplicated for interactive output. `did` also joins
the current role-`0x41` signal-info metadata when type-13/14/15 tables are
present: physical `Mul/Div/Offset`, signedness, decimal-point count, bit width,
default unit, raw/graph ranges, and the type-14 value→display dictionary. For
example current `EMPS_P5` DID `0x1037 Steering Angle` reports `15/1`, offset 0,
one decimal, signed 16-bit, `deg`; `0x106A Cooperation Control State` reports
its exact `0=Cooperation Control`, `1=Other than Cooperation Control` dictionary.

### CAN Bus Check topology

`canbus` exposes Toyota's current master CAN Bus Check model directly. It resolves a
vehicle-type ID or OEM vehicle-name substring through `CDbCanBusCarIdTable`, expands every
`CDbCanBusOptionTable` variant, joins component membership through
`CDbCanBusComponentTable` + `CDbSubBusConfirmationCGWTable`, and names each network through
`CDbCanBusNameTable` / `CDbCanBusListTable`. If multiple option rows collapse to the same
component placement, the CLI reports one placement variant rather than duplicating it.

```text
$ tools/gts canbus 12704
vehicle=12704 name=Camry HV can_bus_car_id=0x00A7D910 options=18 placement_variants=1
  Bus 1 index=29 gateway=Central Gateway
    ...
    0x6D Front Camera Module
  Bus 4 index=32 gateway=Central Gateway
    0x28 Brake Booster ...
    0x29 Skid Control (ABS/VSC/TRAC) ...
    0x32 Power Steering (EPS) ...
    0xF0 Spiral cable (Steering Angle Sensor) ...
```

The displayed Toyota `Bus N` name is a Central-Gateway network identity, **not** a Panda
bus number or connector pin. Physical harness mapping still requires vehicle evidence.
For the exact 2026 Camry join, see the [Camry baseline §19](../variants/camry-2026-live-baseline.md#19-current-gts-can-topology-closes-the-b6-bus-question).

### Master DB execution model

`command`, `role`, `commset`, `timer`, `category`, and `frame` expose the means-based diagnostic execution model recovered
from Techstream/GTS+ rather than another endpoint-specific lookup. The current
master contains **6,194 category/plugin bindings but only 191 logical DLL roles**.
`command` is the normal joined view: it resolves one category+role to the exact
current plugin identity, operation surface, category-local frames/CommSets,
timers, and any recovered executable parser/control-flow semantics. Semantic
profiles are keyed by SHA-256; if a selected plugin changes bytes, the command
fails closed to `plugin_semantics_unrecovered_for_identity` and does not inherit
selectors or parser behavior by filename/role alone. `role` aggregates the
vocabulary globally so one command family can be studied
across every ECU generation that uses it. For example, role `0x19` has 536
bindings and is dominated by `DelDiagCodeP4.dll` (424) plus the P6 equivalent
(106). `category`
resolves a master ECU category by numeric ID or an unambiguous database/name key
and shows its `CDbDllTable` plugin-role bindings plus function IDs. `frame`
resolves `CDbFuncCommFrameTable` selector operands through `CDbCommFrameTable`
and `CDbVariableTable` to the exact current GTS+ send / receive-mask /
receive-check bytes. `timer` decodes master type-25 `CDbTimerTable` by Toyota ECU category and timer ID; the recovered first dword is the command delay passed directly to `Sleep`. `commset` decodes master type-29 `CDbComSetTable`, including
the proven receive-timeout and retry fields used by the shared runtime:

```text
$ tools/gts command HV_P5 0x19
command  category=397  Hybrid Control  role=0x19  plugin=DelDiagCodeP4.dll  surface=direct_transport  semantics=exact_plugin_identity_and_primary_frame
primary  selector=0x1  send=04  expect=44  commset=1  timeout=1020  retries=1
fallback selector=0x102  send=14ffffff  expect=54  commset=1  timeout=1020  retries=1
timer    id=1  delay_ms=0
flow     primary=0x1  fallback=0x102  fallback_errors=10

$ tools/gts command EMPS_P5 0x52
command  category=405  EMPS  role=0x52  plugin=GetCID_SID22_DT.dll  surface=direct_transport  semantics=exact_plugin_identity_and_category_frame
request  selector=0xDC  send=22f181  expect=62f181  commset=1  timeout=1020  retries=1
response payload_offset=4  record_size=16  names=CID1...  conversion=CP_ACP

$ tools/gts command HV_P5 0x06
command  category=397  Hybrid Control  role=0x6  plugin=GetActTstListP5_DT.dll  surface=delegated_transport_v18_proven  semantics=exact_plugin_identity_and_category_active_test_partition
active-tests  direct=29  routine=10  multi_did=0  did_helper=CheckSupportDid  rid_helper=CheckSupportRid

$ tools/gts command HV_P5 0x08 --item 0x1
command  category=397  Hybrid Control  role=0x8  plugin=GetActTstInitP5_DT.dll  surface=direct_transport  semantics=exact_plugin_identity_and_selected_active_test_plan
active-test-init  id=0x1  name=Activate the Inverter Water Pump  did=0x2801  bits=15..15  init_mode=0  monitor_link_mode=0
initial-read      selector=0xCA  send=222801  expect=62  bits=15..15
linked-monitor    key=30  resolution=unique DID/bit-range match from plugin scan  name=Inverter Water Pump

$ tools/gts command EMPS_P5 0x05
command  category=405  EMPS  role=0x5  plugin=GetDatMonListP5_DT.dll  surface=delegated_transport_v18_proven  semantics=exact_plugin_identity_and_category_candidate_partition
list     table=62  candidates=230  direct_include=0  direct_exclude=0  runtime_probe=230  builder=CreateEnableDataIdList

$ tools/gts command EMPS_P5 0x41
command  category=405  EMPS  role=0x41  plugin=GetDatMonSignalInfoP5_DT.dll  surface=no_recovered_shared_transport_edge  semantics=exact_plugin_identity_metadata_only
metadata physical=table13  unit=table15  patterns=table14  fields=10

$ tools/gts did EMPS_P5 0x1037
did      EMPS_P5.ddb  0x1037 alt=0x3037  Steering Angle  conv=15/1 offset=0 dec=1 signed=1 bits=16 unit=deg

$ tools/gts category HV_P5
category  397  Hybrid Control  db=HV_P5.ddb  generation=20
...
0x19      DelDiagCodeP4.dll

$ tools/gts commset 1
commset  1  send_parameter=1000  receive_timeout=1020  retries=1  exception_id=0  exception_flag=0  unknown_0c=0

$ tools/gts timer HV_P5 1
timer  category=397  id=1  delay_ms=0  unknown_08=0

$ tools/gts frame 397 0x1
frame  category=397  selector=0x1  comm_set=1  frame=0x279E  rcv_timeout=1020  retries=1  send=04  mask=  check=44
```

For role `0x08`, `--item` is the direct Active Test ID from the selected category's type-68 `CDbActTestP5Table`. The planner joins that exact row to the current plugin's initialization state machine: when `initial_read_mode == 0`, selector `0xCA` supplies a base `22FFFF` request and the plugin substitutes the row's `+0x34` DID into request bytes 1/2 before send. It also reproduces the plugin's linked-Data-Monitor lookup by DID and bit range. This remains a **read-only plan**: it does not execute the Active Test or assert that role `0x06` would expose the test on a live ECU. Unknown direct-test IDs fail closed.

Current GTS+ namespaces base-variable references above `0x2710`; the CLI follows
`CDbVariableTable::GetVariable` and subtracts `0x2710` before the unchanged
1-based offset/length lookup. Thus current IDs such as `0x2743` and `0x28F7`
resolve to logical variables `0x33` and `0x1E7` rather than being mistaken for
out-of-range table indices. CommSet dword `+0x00` is intentionally exposed as
`send_parameter`: it reaches `SendInt` argument 4, but the common CAN `SendProc`
does not consume that argument, so the CLI does not invent a timeout/unit label.
The current type-19 DLL-role layout is likewise
version-aware (`u16 +0x54`, not V18's `u8 +0x56`).

OEM display names can legitimately be ambiguous across diagnostic generations
(e.g. multiple P3/P4/P5 categories named `Hybrid Control`); the CLI refuses such
a query instead of silently choosing one. Use category `397` or database key
`HV_P5` when the generation matters.

### CUW -> current writer route

`tools/gts cuw FILE.cuw` reads only the small outer header + first `attach.att`
member by default, so even 250+ MiB packages resolve immediately without
streaming the flash payload. It summarizes vehicle/contact type, diagnostic
IDs, logical-block calibration IDs, and target calibration IDs, then decodes the
current GTS+ CUWPlus route INIs and joins `Vehicle/ContactType` to the current:

```text
CID getter -> prepare writer -> flash writer
```

This makes a CUW immediately actionable without first remembering which of the
older corpus inspectors or writer generators owns the relevant mechanics.
Those proof tools remain separate. Add `--validate` when full outer-container
CRC/size validation is actually required; that deliberately reads the entire
package and is not part of the normal discovery path.

### DLL / EXE inspection

`tools/gts pe` resolves binaries from the current GTS+ `bin` directory and the
tracked CUWPlus reconstruction tree, then exposes native PE imports, exports,
and ASCII/UTF-16 strings. An optional query filters all three surfaces in one
command.

Use this for fast implementation lookup (class names, exported methods, DLL
edges, protocol strings), then use Ghidra/decompilation and the deterministic
Techstream generators when a claim needs to be promoted to evidence.

## Source selection

Defaults are repository-pinned paths. They can be overridden without changing
scripts:

- `GTSPLUS_ROOT` or `--gtsplus-root`
- `GTSPLUS_CUW_ROOT` or `--cuwplus-root`
- `TOYOTA_CUW_CORPUS_ROOT` or `--cuw-root`
- `--region` (default `NA`)
- `--family` (default `Gen`)

`GTSPLUS_ROOT` may point either at the repository's external-artifact root or
directly at `.../Toyota Diagnostics/GTSPlus`; the CLI normalizes both shapes.
When an alternate GTS+ tree is selected, writer-route lookup uses only an
adjacent CUWPlus tree (or an explicit `GTSPLUS_CUW_ROOT`/`--cuwplus-root`) and
never silently borrows the repository pin's route tables.
When an alternate GTS+ tree is selected, route lookup prefers a `cuwplus/CUWPlus`
tree adjacent to that artifact before falling back to the repository default, so
DDBs and writer tables are not silently mixed across releases. Use
`--cuwplus-root` when an intentional cross-release comparison is desired.

## Evidence boundary

A `tools/gts` result is **external-source discovery**, not target-firmware
proof. Toyota names and database membership can constrain interpretation, but
they do not prove that the Camry/Sienna/Corolla firmware uses a field the same
way, nor do they prove CAN producer ownership, SecOC key/freshness semantics,
or runtime reachability. Promote useful correlations through the existing
image-bound extractors/tests before recording them as firmware findings.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [TMS-064](../reference/index.md#finding-tms-064)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
