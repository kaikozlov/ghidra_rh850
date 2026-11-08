# GTS+ query CLI

`tools/gts` is the read-only discovery surface for Toyota GTS+/Techstream evidence.
It exposes structured OEM records and their implementation routes. Start by
selecting the diagnostic or recorder namespace below; use string/PE searches
for remaining gaps, then return to target firmware bytes or captures for proof.

The command deliberately does **not** replace the deterministic Techstream/GTS+
extractors and verification suites. Those encode subsystem-specific evidence
boundaries. `tools/gts` only centralizes the already-shared mechanics needed for
interactive discovery.

## Schema-first workflow

GTS has two distinct field-definition paths. A hexadecimal identifier alone
does not select one:

| Starting point | First query | What it resolves |
|---|---|---|
| ECU / database | `tools/gts ecu FRC_P5` | Section types, record classes and sizes |
| Data List or ordinary snapshot DID | `tools/gts did FRC_P5 0x1B06 --json` | Monitor row, primary/alternate DID, bit range, scaling and enum references |
| PCS TSS3 recorder ID / field name | `tools/gts recorder 0x5A08 --json` | Recovered viewer field definitions and source identities |
| PCS ADU recorder ID / field name | `tools/gts recorder 0x1F06 --schema adu --json` | The separate ADU field schema |
| ECU implementation route | `tools/gts category FRC_P5` | Category and plugin-role bindings; follow a role with `command` |

An empty `did` result means **no matching Data List/alternate snapshot row in
that ECU database**. Check the
recorder namespace when investigating a recorder ID. Neither command silently
borrows records or enum meanings from the other namespace.

### Follow references

- **DDB path:** `Toyota.ddb` category/plugin routing → ECU monitor tables
  `62/157` → physical-data table `13` → unit table `15`, plus pattern-display
  table `14` and language strings. `did` displays table aliases, monitor key,
  bit range, physical key and pattern key; `--json` includes the enum labels.
  It matches both the primary Data List DID and the alternate snapshot DID.
  See the [DDB pipeline](techstream-ddb-pipeline.md#ecu-databases) and the
  canonical decoder, `tools/techstream/ddb_semantics.py`.
- **Recorder path:** recovered PCS viewer static constructors → TSS3
  `DetailBitAssignInfo` or ADU `P6DetailBitAssignInfo` → record ID and
  byte/bit geometry, type, scale, support bits and invalid values.
  `recorder` reads the complete tracked schemas, independently of live-tool
  focus lists. The [shared Operation-FFD decoder](pcs-data-viewer-tss3-dictionary.md#shared-operation-ffd-decoder),
  `tools/techstream/tss3_operation_ffd.py`, owns TSS3 payload decoding for both
  acquisition and offline commands; the schema query itself does not decode bytes.

For example, `1B06`'s responsiveness row supplies its own enum labels, while
recorder `5A07` supplies a three-bit response-priority field. Similar names do
not establish identical enum values. Recorder `5A08` also has a support bitmap:
for its `SupportDID=1` fields, the preceding byte supplies the support bit.
Keep “unsupported” separate from a numeric zero.

Both paths describe **diagnostic/recorder payload positions**.
Inspect the reader to determine which raw records acquisition includes.

### Recorder lookup contract

```bash
tools/gts recorder 5A08
tools/gts recorder 'response priority'
tools/gts recorder 1F06 --schema adu --json
```

IDs match exactly, accepting four hex digits or a `0x` prefix. Other queries
match field names case-insensitively. Omitting the query lists record fields;
viewer metadata entries without a record ID are excluded. `--limit` caps
displayed fields; JSON includes `matched_fields` before truncation.

The command needs no external GTS installation. It reads the pinned
`pcs_data_viewer_tss3_managed_semantics.json` or
`pcs_data_viewer_adu_semantics.json` under `data/generated/gtsplus_2026/`.
`--gtsplus-root` selects only the DDB-query release. Output identifies
the artifact and JSON includes its source hashes. All recovered field attributes
are retained, including `Point` where present; byte positions are 1-based and
bit position 7 is MSB. This command inspects the recovered schema.
Legacy DDR schemas remain in the
[recorder guide](pcs-data-viewer-tss3-dictionary.md), outside these two selections.

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
labels describe only the recovered shared-runtime edge:
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

## Implementation boundaries

The public command runs `tools.techstream.gts.cli`. Within
`tools/techstream/gts/`, `cli.py` owns argument parsing and dispatch; `render.py`
owns text/JSON presentation. Domain modules build the results: `ddb.py` and
`master.py` resolve OEM data, `query.py` provides DDB and recorder-schema queries,
`cuw.py` provides CUW searches,
`active_tests.py` and `commands.py` assemble recovered plans, and `registry.py`
and `bundle.py` export diagnostic descriptions. Shared support selection and
execution-model loading live in `support.py` and `execution_model.py`.

Consumers import the relevant domain module, never the CLI. Inputs are resolved
by the existing Techstream path helpers, and explicit relative file arguments
remain relative to the caller's working directory.


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

#### Database-name matching

Check the returned database name when using `search --ecu`: the filter can
match a longer name. For example, `--ecu CentralGW_P5` also matches the
distinct `CentralGW_P5FHI.ddb` Subaru dictionary. Its lost-communication
codes are not Toyota `CentralGW_P5.ddb` records.

The Toyota dictionary has one DTC, `B102004`, and a Data List covering
power, odometer, type information, Ethernet-1, DTC count and clock.
It contains no steering/lateral/CAN-ID monitor. Inspect the selected database
with `tools/gts ecu CentralGW_P5` and check each query's source identity.

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

The displayed Toyota `Bus N` name identifies a Central-Gateway network.
Panda bus numbers and connector pins require separate physical harness mapping with vehicle evidence.
For the exact 2026 Camry join, see the [Camry baseline §19](../variants/camry-2026-live-baseline.md#19-current-gts-establishes-logical-bus-4-membership-not-physical-transparency).

### Master DB execution model

`active-test`, `command`, `role`, `commset`, `timer`, `category`, and `frame` expose the native diagnostic execution model. **Raw catalog rows and the active native index are different views.** `--raw` preserves source, table, ordinal, bytes and duplicate occurrences. Selected queries report their native context; an initial offline context is not an observed vehicle session.

The native default index includes only the leading handling-ID-zero prefix. Ordered handling events delete the first comparator-equal row or replace/insert a row. Master category queries skip Spe; other admitted master queries concatenate Gen then Spe. Category names resolve from their own source's string table. Catalog inspection uses detached ECU contexts and does not mutate the supplied session history.

Use `--native-context initial` for the initial index. Use `--native-context unknown` when the session history is unavailable. A selected command then emits unresolved JSON and exits with status2.

`--native-history FILE` replays an ordered JSON event array. For example, `[{"kind":"reflection","ecu_id":0,"handling_id":136}]` changes `tools/gts frame 1 0x66 --json` from `0100` to `2100`. The output retains the event and its source-qualified status.

`command` joins category+role to the selected plugin, every selected frame, CommSet, timers and recovered control flow. A category miss falls back to the **first active row for that role**, not a category-zero lookup. Plugin semantics are SHA-256-bound; an unknown identity reports `plugin_semantics_unrecovered_for_identity`. Deployed filenames resolve within the selected directory, preserving its actual spelling.

`frame` evaluates every selected type18 row. Each supplies its own frame key, but current `GetCommFrmInfo` uses the **first selector row's CommSet key for all emitted frames**. The frame consumer uses its first returned type17 record; the CommSet consumer requires exactly one type29 record. Handler136 changes the initial selector-`0x66` program from `0100` to `2100`, making event history material to the result.

`timer` uses type25's key at `+0x04`, category at `+0x06`, handling ID at `+0x08`, flag at `+0x0A`, and delay at `+0x00`. `commset` exposes the native timeout, retry and exception-handler fields. Unknown history remains unresolved rather than silently becoming the initial index.

```sh
# Selected plugin/control flow and raw metadata
tools/gts command HV_P5 0x19
tools/gts command EMPS_P5 0x52
tools/gts category HV_P5
tools/gts frame 397 0x1
tools/gts commset 1
tools/gts timer HV_P5 1

# Selected Active Test, initialization, presentation and monitor membership
tools/gts active-test HV_P5 0x1
tools/gts active-test FRC_P5 0xA429
tools/gts command HV_P5 0x08 --item 0x1
tools/gts command HV_P5 0x70 --item 0x1
tools/gts command HV_P5 0xAD
tools/gts command Engine_P5 0x63 --item 0x4C
```

These commands are offline planners. The Hybrid example obtains four-byte prefixes `2F280103` and `2F280100`, plus the independent `222801 -> 62` length probe. For its mode1 encoding, START includes N value bytes **and N mask bytes**; STOP includes N mask bytes. With the explicit example assumption `N=2`, ON is `2F28010300010001` and return-control is `2F2801000001`.

`active-test` is the preferred selected-test planner when you do not already know Toyota's internal command role. It auto-detects a unique current type-68 direct versus 72-byte type-71 routine row (or accepts `--kind` for an ambiguous key), resolves the current master templates, and never opens a transport. For current routine rows, type71 `+0x28/+0x2A/+0x2C/+0x2E` are respectively routine-command, routine-stop, output-value-mask, and output-button-mask variable references; `+0x30` is the type72 routine-status key. A `fixed=1` result means all four payload sources are zero, as for FRC `0xA429`, so the displayed `31 01/02/03 + RID` requests have no hidden setpoint bytes. Current GTS+ uses standard UDS `31/71` here; the older pinned V18 `21 E2/61 E2` routine executor remains version-specific.

Role `0x63` handles **multi-control Active Test initialization**. `--item` selects the type-33 group ID. The current generic P5 plugin reads 12-byte `CDbMultiDidIdTable` rows keyed by u16 `+0x00`, takes member Active Test ID from `+0x02`, and sorts on u32 `+0x06`. The current DataMonitor runtime additionally consumes the low u16 at `+0x06` as input slot 1/2, materializes each member through the ordinary type68 direct executor, and OR-composes complete start/stop frames. All member DID bytes must match; mixed-DID groups fail closed. The generated catalog therefore exports input slots plus `materializable`/`blocked` composer status. Categories may bind role `0x63` without having type-33 groups; the planner reports an empty census instead of manufacturing groups.

Role `0xAD` is category-wide rather than selected-test-specific. The current `GetDatMonListP5ForActTest_DT.dll` reuses the normal role-`0x05` P5 support/table/MultiPID/conversion pipeline, but uses monitor flag bit `0x40` as the Active-Test membership bit. If flag bit4 is set, bit `0x40` is the direct include/exclude decision; if bit4 is clear, the plugin still calls `CheckSupportPid` and applies the `0x40` membership test afterward. `tools/gts command ... 0xAD` therefore reports both static membership and which rows still require runtime support evaluation. It does **not** take `--item`: the plugin does not join this list to one selected Active Test ID.

For role `0x70`, the same `--item` selects the direct type-68 Active Test but no wire transaction is attached. The exact current `GetATSignalInfoP5_DT.dll` consumes that selected ID and joins type-12 Active-Test pattern, type-13 physical conversion, type-14 display values, and type-15 unit metadata into `CCmdActTstSignalInfoItem`. This makes `0x70` the read-only presentation/conversion companion to role `0x08`.

For role `0x08`, `--item` selects the category's type68 Active Test. Initial-read mode0 substitutes DID `+0x34` into selector `0xCA`; mode1 skips that initialization read. The planner also follows the linked-monitor DID/bit-range lookup. Direct execution takes its encoding mode from the first matching type67 row and uses selectors `0x9D/0x64` for START/STOP. N comes separately from `CheckSupportDid`: a successful `22 <DID>` response longer than the three-byte `62 <DID>` echo contributes `received_length - 3` to the per-ECU length cache. The `runtime_length_probe` is therefore retained even when initialization-read mode1 skips its transaction. Minimum-length examples assume N from static bit geometry; actual support, runtime N and menu exposure remain caller-supplied state. Unknown test IDs fail closed.

Current GTS+ namespaces base-variable references above `0x2710`; the CLI follows
`CDbVariableTable::GetVariable` and subtracts `0x2710` before the unchanged
1-based offset/length lookup. Thus current IDs such as `0x2743` and `0x28F7`
resolve to logical variables `0x33` and `0x1E7` rather than being mistaken for
out-of-range table indices. CommSet dword `+0x00` is intentionally exposed as
`send_parameter`: it reaches `SendInt` argument 4, but the common CAN `SendProc`
does not consume that argument, so the CLI does not invent a timeout/unit label.
The current type-19 DLL-role layout uses `u16 +0x54`.
V18 uses `u8 +0x56`.

OEM display names can legitimately be ambiguous across diagnostic generations
(e.g. multiple P3/P4/P5 categories named `Hybrid Control`); the CLI refuses such
a query instead of silently choosing one. Use category `397` or database key
`HV_P5` when the generation matters.

### CUW -> current writer route

`tools/gts cuw FILE.cuw` reads only the small outer header + first `attach.att`
member by default, so even 250+ MiB packages resolve immediately without
streaming the flash payload. It summarizes vehicle/contact type, diagnostic
IDs, logical-block calibration IDs, and target calibration IDs. Current native
selection uses `KindOfECU`, `ContactType`, CPU and node fields to derive exact
INI filenames and select:

```text
CID getter -> prepare writer -> flash writer
```

Ordinary entry selectors first probe their own INI; if it is unreadable, the
first exact master row selects the legacy or current engine. Exact
`P5-Unified`, `Phase6` and `Ethernet` contacts take the current-engine branch
directly. CID, prepare and flash selectors are separate: classic prepare uses
CPU0's DLL while address and flash selection use the current CPU; node-based
routes use their required-specification/protocol fields. Missing CPU or node
state remains an explicit native precondition, not a synthetic CPU0 or node.

The result retains selector inputs, selected files, role bindings and native
failure branches. Add `--validate` for full outer-container CRC/size validation;
that reads the entire package and is separate from descriptor/route discovery.

### DLL / EXE inspection

`tools/gts pe` resolves binaries from the selected GTS+ `bin` directory and its
installed `CUWPlus` sibling, or an explicit `--cuwplus-root`. It exposes native
PE imports, exports, and ASCII/UTF-16 strings. An optional query filters all
three surfaces in one command.

Use this for fast implementation lookup (class names, exported methods, DLL
edges, protocol strings), then use Ghidra/decompilation and the deterministic
Techstream generators when a claim needs to be promoted to evidence.


### Derived Comma diagnostic registry

`tools/gts registry` is the shipping bridge between the proprietary analysis corpus and
runtime Toyota tooling. It compiles current GTS+ vocabulary/command plans together with
vehicle-bound live evidence into a clean JSON registry; the consumer does **not** need
Techstream, GTS+, DDBs, or Toyota DLLs installed.

For the maintainer Camry:

```bash
tools/gts registry camry-2026-f33 \
  --out data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json.gz

tools/gts registry camry-2026-f33 --compact > /tmp/toyota_diag_registry.json
```

The tracked Camry fixture uses deterministic gzip (level 6, zero modification
time, no embedded filename). It retains the complete schema-v8 JSON, including
all repeated native query/context evidence, raw source identities, record order,
and selection histories; compression is not a reduced catalog or a new schema.
The original 174,740,779 JSON bytes occupy 5,378,395 tracked gzip bytes.
`--compact` only removes JSON whitespace and is independent of gzip output.
An output name ending in `.gz` selects gzip; other output paths and stdout
remain ordinary JSON for exports.

Offline readers use
`tools.techstream.gts.registry.load_toyota_diag_registry(Path(...))`; no
proprietary corpus or external build cache is needed. For a plain JSON copy:

```bash
uv run python -c 'import gzip; from pathlib import Path; p = Path("data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json.gz"); Path("/tmp/toyota_diag_registry.json").write_bytes(gzip.decompress(p.read_bytes()))'
```

The `camry-2026-f33` profile pins the relay-correct Panda bus-0 diagnostic topology,
the exact 17-address live DTC sweep, the EPS F181 guard `8965F3307000`, and the
validated functional `0x7DF` Mode-04 responder set `7E8/7EA/7EB/7ED/7EE`. It then
joins the eight resolved current-P5 categories (Engine, Motor Generator, Hybrid, HV
Battery, EMPS, Brake/EPB, Air Conditioner, and Front Recognition Camera 2) to compact
DID signal metadata, DTC names/failure types, and static Active-Test plans.

Registry schema v2 also carries the recovered ordinary-P5 Data Monitor decoder as
`p5-linear-msb0-v1`. Current `DatMonCommon.dll::CPacketConvertor` proves that signal
bit numbering is MSB-first within each byte (`bit 0 = byte 0 bit 7`) and multi-byte
fields are assembled big-endian. `CommandDataLib.dll::CComDataConvert` then applies
unsigned or two's-complement interpretation at the declared bit width followed by
`trunc_toward_zero(raw * Mul / Div) + Offset`; the DDB decimal count renders that
integer as `value / 10^decimal_point_count`, and pattern-display lookup compares the
converted integer before decimal rendering. The role-`0x41` signal-info plugin joins
exactly those type-13 physical fields into `CCmdConversionTbl`; that table calls the
basic conversion overload. Unrelated time/chassis/illuminance-style display paths
use a separate special-format overload. Each exported DID signal explicitly names
its decoder kind so future non-P5 formats can fail closed instead of inheriting this
contract implicitly.

`tools/gts registry toyota-current` regenerates the canonical universal bundle at
`data/generated/gtsplus_2026/toyota_diag_bundle_current/`; `--out DIRECTORY`
selects another destination. This is a directory of deterministic gzip-compressed
members, not a tracked distribution ZIP. Its ordered `manifest.json` records every
original member name, uncompressed size, and SHA-256. All 686 original members are
retained byte-for-byte, including the existing compact native metadata and P6
representations; source identities, query ordering, and JSON schemas are unchanged.
The canonical directory occupies 106,938,056 bytes; its largest file is
`index.json.gz` at 13,413,545 bytes. The replaced ZIP occupied 118,655,949 bytes
and contained 4,972,122,569 uncompressed bytes.

Offline access needs only the tracked canonical directory, Python dependencies,
and this repository—no Toyota distributions, DLLs, or extraction cache:

```bash
tools/toyota gts bundle list
tools/toyota gts bundle read catalogs/NA/372.json --path category
tools/toyota gts bundle verify
tools/toyota gts bundle export
# Default portable output: build/out/toyota_diag_bundle_current.zip (not tracked).
tools/gts bundle sqlite
# Indexed runtime projection: build/out/toyota_diag.sqlite (not tracked).
# Byte-for-byte migration proof against a preserved original archive:
tools/toyota gts bundle verify --compare-zip /path/to/original.zip
```

Use `bundle --bundle DIRECTORY` to select a different canonical directory,
`bundle read MEMBER` to stream the exact member bytes, and `bundle export --out
FILE.zip` to select a portable export path. Python consumers use
`tools.techstream.diag_bundle.DiagnosticBundle` (`open`, `read`, `json`, `namelist`).
Reads inflate only the selected member; verification and ZIP export stream all
members rather than allocating the 844 MiB uncompressed index. `bundle sqlite` verifies
the canonical bundle first, then writes the compact indexed vehicle/ECU/search projection
used by `toyota-diagnostics`; the canonical gzip members remain the evidence source.

Bundle schema **`toyota-diagnostics-bundle-v4`** keeps Toyota's resolver layers independent: all regional vehicle/type-41/type-59 tables, install sets, physical category occurrences and native-selected categories, class-`0x10D` category/route-selector keys, per-category D1/D2/DD frames, selected support plugins, family-local `support_mode`, Toyota transport-controller selection, and lazy decoded catalogs. Route/VIN/type-41 rows expose `route_selector`, install rows `connection_route_selector`, and Customize rows `target_route_selector`. ECU generation remains a separate input. Catalog availability does not decide whether a category exists or is routable.

Current support-family selection comes directly from Toyota's DLL table (`p3/p4/p5/p6`). The ordinary Toyota P5 mode reproduces `22 01 01` plus MSB-first group/member expansion while retaining advertised `xx00` IDs and skipping Toyota's `F300`/`FD00` group queries; Subaru/Suzuki/Mazda/Hino modes remain distinct. Standard P6 support discovery exports DID `22 A1 00 -> A1nn -> nn00..nnFF` with `A1FD/A1FE` retained but unexpanded, and RID `31 01 D1 00 -> D1nn -> nn00..nnFF` with the inclusive range `D1F0..D1FE` retained but unexpanded. Route selectors `0x18`/`0x38` use Toyota's `CCommCtrlISO15765_29BitCan` normal-fixed construction (`0x18DA<target>F1` request / `0x18DAF1<target>` response). Other controllers remain explicitly typed. P3/P4 carry their `Spe/Toyota.ddb` live probe programs and semantic type-41 criteria; a VIN hit requiring that second stage is non-final. VIN10 low5 `5..19` rejection is recorded together with Toyota's separate legacy `SelectCarType.dll` / `SelectCarTypeVin.dll` role bindings, whose binaries are absent from the current corpus.

The bundle contains no Panda logical-bus default: the caller supplies harness state. `tests/techstream/verify_toyota_diag_bundle.py` regenerates the canonical gzip members byte-for-byte, checks exact portable ZIP member restoration and deterministic export, and checks these boundaries plus Camry and 4Runner install/route resolution. The Camry gzip-compressed JSON is a target-specific evidence fixture.

Registry schema v8 also carries the current Camry-HV GTS CAN Bus Check topology and
tracked module identities needed by the legacy Camry fixture. Toyota master vehicle type
`12704` (**Camry HV**) resolves `CANBusCarID=0x00A7D910`; all 18 option rows collapse to
one placement variant. The exact placements put **Front Camera Module** on GTS **Bus 1**
and **Power Steering (EPS)** plus **Skid Control (ABS/VSC/TRAC)** on GTS **Bus 4**, all
behind **Central Gateway**. These Toyota vehicle-network domain names use a
separate namespace from Panda buses. The active post-repin profile remains Panda bus0. The registry separately
retains the tracked 2026-08-26 **pre-repin** identity observations without rewriting that
history: EPS F181 `8965F3307000` + `8A3113303100` / F18C
`8965033K9011J2740743`; FRC F181 `8646F3315000`, part `8646C06091`, F18C
`TN69400026030404235J`; Brake F181 `F152633K0000`, part `8954147040`, F18C
`8954147040CFC1800985`. Each identity row records Panda bus1 + ELM327 param1 as the
observation route and explicitly points to current post-repin Panda bus0 diagnostics.

The current registry contains 428 Active-Test candidates. **41** routine tests are
`executable` in the narrow sense that their fixed request geometry is complete
(all four type-71 payload sources zero, so start/stop/result requests are fully
materialized); **361** remain `plan_only` because a runtime parameter (typically the
direct-executor DataIdLengthList payload length) or an explicit type-71 variable is
required, and **26** remain `unresolved_static_plan` because their current database
rows are ambiguous — the exporter does not pick a row heuristically. Representative
witnesses are Hybrid Active Test `0x0001` (`0x2F`, DID `0x2801`, start prefix
`2F280103`, return-control prefix `2F280100`, initial read `222801` via selector
`0xCA`) and FRC `0xA429` **LTA Steering Vibration** (RID `0x1588`, fixed requests
`31011588` / `31021588` / `31031588`).

The legacy Camry registry schema **v6** predates the universal bundle and remains an evidence/compatibility fixture. It added Toyota vehicle/mounted-ECU/capability metadata and category routes to the older execution-model surface. Its historical generation/session fields are retained as evidence but are not permission inputs in the universal runtime. Earlier catalog sections remain preserved in shape:

- `profile.vehicle_resolution` — clean structured Toyota resolver metadata from
  `CSelectCarTypeVin10` / `GetMntEcuLstNoCf_DT.dll` / `GetSupportP5_DT`. The current
  Camry witness resolves vehicle type `12704` = **Camry HV**, four install sets
  (`8119`, `8120`, `8121`, `27706`), and **34 Toyota logical ECU categories**. Each
  candidate preserves its install-set/category identity and connection metadata:
  frame `0`, CommSet `9`, and encoded route selector `0x12` or `0x22`.
  Current `DV000004` uses role121 mode0: it publishes candidates with connection
  state `-1`, then selectively probes coexisting combined/individual aliases.
  The separate `DV000005` can select a cache-only branch. Connection frame0 has
  empty send/mask/check payloads. Each candidate's `transport_route` resolves
  through Toyota class `0x10D` `CDbProtInfoTable`, with the same
  `(category, route_selector)` key consumed by
  `CCommFrameCtrl::GetEcuAddr`: u16 `+0x08` is the request address and byte `+0x0A`
  is the current P5 logical address extension. Thus all 34 Camry candidates have a
  Toyota-derived route; no maintained-profile endpoint allowlist participates. This
  includes direct routes absent from the old 17-address sweep (`0x7C0`, `0x780`) and
  multiple logical categories sharing `0x750` with distinct extensions such as
  `0x2A`, `0x29`, `0x7B`, and `0x96`. The same section carries
  the P5 PID/DID/RID support resolver contract (`optionId` 1/2/3), including DID
  selector `0xC8`, root request `22 01 01`, and the two-level MSB-first bitmap.
- `profile.session_control` — the runtime current-P5 session contract from TMS-077:
  `generation: current-p5`, default session `1` / extended `3`, enter sequence
  `["1001","1003"]`, `return_default: "1001"`, and the keepalive poll
  `{kind: session_did_poll, did: 0xF186, request 22f186, positive_prefix 62f186,
  interval_s 2.0}`. The narrow session-judgment exception (`CCommFrameCtrl +0x398`
  one-shot no-wire D1/D2) is retained as documentation metadata with
  `runtime_default: false`, never as a runtime default. The former local
  `wire_proven_categories` gate is intentionally absent. The legacy v6 artifact
  records the Camry categories' generation-low5/session behavior, but the universal
  bundle does **not** use those low5 values as a P5-family classifier: Toyota's
  `GetSupportP5_DT.dll` binding supplies that boundary directly, and D1/D2/DD are
  resolved independently for each selected category.
- `catalogs.<id>.plugins` — every category role/plugin binding with a
  `semantic_kind` only where the exact plugin SHA-256 matches a recovered profile
  (for example 0x19 `dtc_clear`, 0x52 `generic_cid`, 0x08 `p5_active_test_init`);
  everything else stays `null`/`plugin_semantics_unrecovered_for_identity`.
- `catalogs.<id>.commands` — wire-request plans for the recovered command roles:
  DTC clear primary/fallback selector paths with per-request CommSet timeout/retry
  and a `session_requirement` derived from the recovered first-byte session
  classifier (`04` → default, `14ffffff`/`22`/`2F`/`31` → extended), the EMPS
  `0x52` CID response model (payload offset 4, 16-byte records), and the role-0x08
  initial-read template.
- `catalogs.<id>.selectors` — every resolved `(category, selector)` frame as exact
  send / receive-mask / receive-check bytes with its CommSet reference, plus
  top-level `commsets` rows for the CommSets actually referenced.
- `catalogs.<id>.functions` — the master type-26/type-27 supported-function
  hierarchy (function/sort/detail keys) via `GetEcuFuncList` classes `0x11A/0x11B`;
  these categories carry string index 0, so OEM function names are explicitly not
  recovered (`function_names` states this).
- `catalogs.<id>.data_list` — Data List display order from the consumer-pinned
  type-62/157 sort key, deduplicated by signal identity; DID signal rows also gain
  `data_range`/`graph_range` display metadata.
- `catalogs.<id>.active_test_groups` — type-33 multi-control group geometry
- generation-22/P6 catalog shards export the recovered Active-Test surface plus exact P6 DID/RID support-gate metadata; P6 Data List/FFD/RoB presentation remains intentionally unprojected from P5
  (presently only Engine 372: 5 groups / 10 memberships).
- `utilities` — a deliberately compact runtime `utility list/plan` surface: only the
  recovered generic category-0 families (TestPresent start/stop, check-mode
  get/confirm, set-default-session, move-session-CGWDK, and the four routine
  Active-Test wrappers), the RoutineControl `31 01/02/03 FF FF` and IOControl
  `2F FF FF 03/00` templates with their substitution grammar, and pointers to the
  per-category function menus. Unrecovered generic roles are omitted.

The registry provides metadata. Authorization remains a runtime requirement.
`execution: executable` certifies complete fixed request geometry. Live support
state and outer session/authentication requirements remain runtime questions.
The generated artifact records SHA-256 identities for every
consumed GTS+/derived input so a changed corpus cannot silently reuse old plans. Source keys
are logical and checkout-independent: GTS inputs use `gtsplus/<region>/DB/<family>/...`
while tracked evidence remains repository-relative, so an isolated worktree cannot
change registry bytes merely because the corpus is mounted at a different path.

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
Writer-route lookup selects the installed `CUWPlus` sibling of that normalized
GTS+ directory, including its `Ini/` directory and product-level DLLs. The current
installed corpus contains 505 INIs, 500 factory declarations and 16 additional
master-only selectors: a 516-selector union. A missing sibling remains missing;
the CLI does not substitute an ancestor sample or another release.
Explicit `GTSPLUS_CUW_ROOT`/`--cuwplus-root` values remain authoritative and may
select either a product directory with `Ini/` or a flat INI corpus. Use an
explicit root for intentional cross-release comparisons or recovered PE bodies.

Command and registry DLL lookup compares filenames case-insensitively within
the selected product's immediate binary directory. Results retain the registered
spelling separately from the actual filename, source path and whole-file hash.
Case-equivalent duplicate files are ambiguous; a missing main-product DLL does
not resolve to a same-named DS-4 or older-release DLL.

## Evidence boundary

A `tools/gts` result provides **external-source discovery**.
Toyota names and database membership can constrain interpretation.
