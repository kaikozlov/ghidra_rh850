# Plugin verification: v850e3 SLEIGH against the P1M-E firmware

> **Scope:** RH850G3M/P1M-E targets; Venza core decode only where explicitly bounded
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades; see FINDINGS ARCH-006
>
> **Canonical artifacts:** `data/semantic_coverage_ledger.csv`
>
> **Verification:** `make verify-processor`
>
> **Related:** [WORKFLOW](../WORKFLOW.md), [firmware-architecture](../architecture/firmware-architecture.md)

This records audits of the vendored `ghidra/ghidra_v850` processor module
against the RH850/P1M-E CodeFlash. **Decode coverage is not the same as p-code
semantic correctness.** The checks below are layered:

| Layer | What it proves | How to run |
|---|---|---|
| SLEIGH compile | Sources parse and produce `v850e3.sla` | `make verify-sleigh` |
| Synthetic fixtures | Selected encodings plus executed register/memory/flag vectors | `make verify-processor` |
| Function-body decode | No undefined bytes inside recovered functions | `AssertNoUndefinedInFunctions` |
| System-register naming | Every `ldsr`/`stsr` operand is named | `AssertSystemRegisterNames` |
| Project invariants | Critical labels/functions/memory/context | `AssertProjectInvariants` |
| Decompiler invariants | Landmark ABI/decompiler properties + no unset conventions | `AssertDecompilerInvariants` |
| Device profile | RAM/SFR map + SFR labels/types + boot/application GP/TP context | `ApplyP1MDeviceProfile`, `ApplyP1MSfrTypes` |
| LocalRAM overlays | Typed payload/SecOC/DID/checkpoint roots on LocalRAM | `ApplyRamTypes` |
| Vector recovery | INTBP/EBASE handlers + `__interrupt` | `RecoverVectorHandlers` |
| Calling conventions | Explicit `__stdcall` on non-ISR functions | `ApplyCallingConventions` |
| Switch tables | In-function `switch` jump tables + xrefs | `RecoverSwitchTables` / `AssertSwitchTables` |

Automated gate:

```bash
make verify            # core repository mechanics, no Ghidra or firmware research suites
make verify-sleigh     # compile + isolated install
make verify-processor  # fixtures (+ working-project audits if present)
make verify-ghidra     # full portable sweep + SLEIGH + fixtures + live semantic coverage + project parity
```

Working-project audits require a materialized copy:

```bash
make work-project
make verify-processor
```

## System-register coverage (`ldsr` / `stsr`)

Primary ISA source: *RH850G3M User's Manual: Software*,
R01US0123EJ0140, chapter 3. Script:
`ghidra/scripts/investigate/FindSystemRegisterOps.java`; asserting companion:
`ghidra/scripts/verify/AssertSystemRegisterNames.java`.

The former `v850e3.sinc` table mixed G3M with later G4 register names and
instructions. It mislabeled three register IDs exercised by this firmware:
`PID` as `SPID`, `PMR` as `IMSR`, and `CDBCR` as `RDBCR`. In particular,
selection ID 2, register 11 is **PMR** on G3M; the previous claim that `IMSR`
was correct for P1M-E was false. Persisted decompiler output made with that
table must be regenerated rather than treated as evidence.

The implemented G3M selection-ID table is now:

- **selID 0** (common, `v850_common.sinc`): `PSW`, `EIPC`, `EIPSW`, `FEPC`,
  `FEPSW`, `CTPC`, `CTPSW`, `EIIC`, `FEIC`, `EIWR`, `FEWR`, `CTBP`, `BSEL`,
  plus the FPU registers.
- **selID 1**: `MCFG0`, `RBASE`, `EBASE`, `INTBP`, `MCTL`, `PID`, `FPIPR`,
  `SCCFG`, `SCBP`.
- **selID 2**: `HTCFG0`, `MEA`, `ASID`, `MEI`, `ISPR`, `PMR`, `ICSR`,
  `INTCFG`.
- **selID 4**: instruction-cache registers `ICTAGL/H`, `ICDATL/H`, `ICCTRL`,
  `ICCFG`, `ICERR`.
- **selID 5**: `MPM`, `MPRC`, `MPBRGN`, `MPTRGN`, `MCA`, `MCS`, `MCC`,
  `MCR`.
- **selID 6/7**: `MPLA0–15`, `MPUA0–15`, `MPAT0–15`.
- **selID 13**: `CDBCR`.

Reserved register-number slots remain unnamed. G4 guest, virtualization,
thread-context, TLB, and hypervisor instructions were removed from the G3M
language rather than left as plausible decodes. The synthetic processor
fixture includes `MCFG0`, `PMR`, `MCC`, and `CDBCR` transfers and asserts the
decoded operand register, so a future name/selection regression fails before
project analysis.

`EIC136`/`EIC292`/`EIC293` remain memory-mapped peripheral registers at
`0xFFFFB110` / `0xFFFFB248` / `0xFFFFB24A`, accessed via `ld.w`/`st.w`, not
`ldsr`/`stsr`. They belong to the device profile and are not system-register
table entries.

## Instruction-decode coverage

Script: `ghidra/scripts/investigate/FindUndefinedInFunctions.java`
(asserting companion: `ghidra/scripts/verify/AssertNoUndefinedInFunctions.java`).

The current function bodies disassemble completely: **zero** undefined bytes
occur inside any of the 7,090 functions. A SLEIGH decode failure would leave a
hole inside a function; none exists, so the module decodes every instruction
listed inside those current bodies. This does not establish that every
executable body or compiler-emitted instruction has been discovered.

That alone does **not** prove every decoded instruction has correct p-code.
Semantic fixtures under `tests/fixtures/processor/` and the asserting scripts
close the highest-impact gaps for this firmware:

- signed `sld.b` / `sld.h` use `sext` (not `zext`);
- two-operand `divh` uses signed division (`s/`) and sets `OV` without executing
  an undefined host divide on a zero divisor;
- saturating arithmetic updates `PSW.SAT` from signed overflow (`OV`), verified
  with both positive-overflow and carry-without-overflow execution vectors;
- `ld.w` `disp16` scaling (`field × 2`) is checked by an executed memory load;
- `prepare`/`dispose` stack/register effects and direct/indirect
  `jarl`/`jmp [lp]` flow types are checked on fixtures;
- inventory-driven risky ops used by this image: `switch` table walk +
  `BRANCHIND`, `callt` CTBP-relative `CALLIND`, `bins` bitfield insert,
  `set1`/`clr1`/`tst1` bit-memory side effects and Z semantics, `cmovne`
  taken/not-taken, signed `mulhi`, and arithmetic `sar`.

Landmark decompiler checks (secrets at `0xBFD8`/`0xBFE8`, ISR calling
convention, session-control decompilation, SecurityAccess expected-key,
ICU dispatch callee, boot reset) live in
`AssertDecompilerInvariants.java`; the gate writes deterministic normalized-C
hashes to `build/out/decompiler-signatures.txt`, compares them with
`data/decompiler_signatures.baseline.csv`, and uploads the report in CI.
Every non-thunk function must carry an explicit `__stdcall` or `__interrupt`
prototype — Ghidra's anonymous `unknown`/`default` is treated as a failure.

## Device profile and interrupt recovery

`ApplyP1MDeviceProfile.java` maps LocalRAM and verified peripheral windows
(`SFR_EIC`, `SFR_RSCFD`, `SFR_ICUS`), labels observed SFRs from
`data/p1m_sfr_labels.csv`, and seeds boot/application `GP`/`TP` register
context. `ApplyP1MSfrTypes.java` then overlays structured types:

| Type | Applied at | Fields named from evidence |
|---|---|---|
| `EIC_Register` | EIC8/133–136/187/188/292/293/379 | `EIP`, `EITB`, `EIMK`, `EIRF`, `EICT` |
| `ICUS_Command` | `ICUSCMD` `0xFFC5D000` | `CMD`, `KEY_SLOT` |
| `ICUS_Status` | `ICUSSTS` `0xFFC5D00C` | `BUSY` (bit 0) |
| `RSCFD_CFSTS` | CFSTS / CFSTS_CH1 | `status_b3` (FIFO poll bit) |
| `RSCFD_CFDTMC` | `CFDTMC16` | `TMTR` |
| `RSCFD_CommonFifoFrame` | CFID / CFID_CH1 | CFID/CFPTR/CFFDCSTS/CFDF0/CFDF1 |
| `RSCFD_TxMessageBuffer` | CFDTMID / CFDTMID16 | CFDTMID/PTR/FDCTR/DF0/DF1 |

The full `0xFF600000..0xFFFFFFFF` range stays volatile in `v850.pspec` without
being mapped as one block (that caused false CodeFlash-as-SFR pointer creation).
CSV coverage is checked by `tests/firmware/verify_p1m_device_profile.py`; project
invariants require the windows, a landmark label subset, and the structured
overlays above.

`ApplyRamTypes.java` then overlays evidence-backed LocalRAM types at absolute
addresses (GP/TP register context is already seeded above). Inventory and
GP-displacement checks live in `data/ram_overlay_map.csv` /
`tests/runtime/verify_ram_overlays.py`. Enabled checkpoint mirrors are sized from
`data/checkpoint_payload_map.csv` without inventing OEM field names.

| Type | Applied at | Notes |
|---|---|---|
| `PayloadFlashCallback` | `0xFEBF0FD0` | Flash-driver callback slot |
| `PayloadCrcTrailer` | `0xFEBF0FE0` | Embedded CRC addr/length/patch |
| `PayloadCmacTag` | `0xFEBF0FF0` | 16-byte AES-CMAC tag |
| `SecocNvmObject15` | `0xFEBF02E8` | 32-byte mirror; key field at `+0x10` |
| `SecocNvmWorkbufRoot` | `0xFEBF0B08` | 4×(raw/XOR55/XORAA)×32; app `GP+0x5308` |
| `PayloadDid0201KeyMaterial` / `PayloadDid0202Iv` | `0xFEBF2D08` / `0xFEBF2CF8` | Volatile DID buffers |
| `Checkpoint_*` | enabled ring mirrors | Opaque `u8[N]` from checkpoint CSV |
| scalars | DID/UDS/handoff landmarks | Session, phase, speed, supply, latches |

| Region | GP | TP |
|---|---:|---:|
| Boot CodeFlash `0x0..0x1FFFF` | `0xFEBF9800` | `0x869C` |
| Application CodeFlash `0x20000..` | `0xFEBEB800` | `0x23EE4` |

`RecoverVectorHandlers.java` walks the boot EIIC dispatch table, application
EBASE vectors, and the 384-entry INTBP table, creates missing handler
functions, and applies the `__interrupt` prototype to true ISR wrappers
(not their normal callees such as `0x87610`/`0x87636`). It also creates explicit
vector-to-handler references; project invariants require the expected 382
CodeFlash INTBP references and all known wrapper conventions.

`ApplyCallingConventions.java` then pins the RH850/G3 ABI prototype
(`__stdcall` from `v850.cspec`) on every remaining non-thunk function. Newly
created Ghidra functions otherwise stay on anonymous `unknown` even though the
cspec default_proto is correct; explicit assignment is what makes landmark
decompiler signatures and project invariants report `__stdcall` instead of
`unknown`. The script is idempotent and preserves `__interrupt`.

## Compiler / ABI fingerprint: `ep` is volatile, not CC-RH callee-save

The calling-convention model is now based on a direct machine-code discriminator
rather than a generic RH850 compiler assumption. Exact Sienna `8965B4512000` and
exact Camry `8965F3307000` contain the same normally called leaf at `0x1478`;
call sites include `0x1498` and `0x1522`. Its complete 22-byte body begins and
ends as follows:

```asm
00001478  mov    r6,ep
0000147a  cmp    r0,r8
0000147c  ble    0x148c
0000147e  sld.w  0[ep],r1
...
00001488  loop   r8,0x147e
0000148c  jmp    [lp]
```

There is no save or restore of the incoming `r30/ep`. A caller therefore cannot
assume that `ep` survives an ordinary call. `tests/firmware/verify_rh850_compiler_abi.py`
binds this witness to both exact firmware images and also pins the corresponding
`v850.cspec` model. This is sufficient to establish **volatile `ep`** for the
firmware ABI; a broader read-only census finds the same pattern throughout both
images, but the single reachable leaf is already a decisive counterexample to a
callee-save rule.

The supplied Renesas CC-RH V2.08.00 reference package gives the contrasting
compiler contract. Its V2.08 user manual (Rev.1.13, June 2026), section 9.1.1,
lists `r20..r31` including `r30/ep` as callee-save; the `-Xep` option says that
when omitted the value of `ep` is guaranteed before/after a call, and the
supported modes are `callee` (preserved) or `fix` (globally fixed). The local
package used for this comparison is
`software/Renesas/cc-rh-compiler/cc-rh_v20800_for_linux_amd64-doc.zip`
(SHA-256 `d72b7754cdfde84130ec585185300b447fdb73fdbf12221f070a6f7c64c2ab25`).
It is research input, not a portable repository dependency.

Reference compilation also explains why compiler identification from instruction
shape alone was misleading. CC-RH V2.08 naturally emits the RH850 `switch`
opcode with a compact halfword branch table and a `cmp`/range-branch prefix,
which closely matches the Toyota tables below. That shape therefore does **not**
prove CC-RH. Conversely, the repository's V850 GCC 13.2 toolchain exposes
`-mghs`/`-mrh850-abi` as its default RH850 ABI mode, and the runtime builders
add `-mno-app-regs`; this is compatible with the firmware's fixed `gp`/`tp` and
volatile `ep` model. Compatibility is not compiler provenance: no compiler ID
string or byte-identical runtime-library match has been recovered, so the exact
Toyota compiler vendor/version remains **bounded**, not identified.

A **known-working public GCC payload** independently validates our payload
compiler family without changing that provenance boundary. Pinned
`I-CAN-hack/secoc @ 4ce19cc31ff5` builds its RH850 key-dumper with Ubuntu 22.04,
binutils `2_41-release`, GCC `13.2.0`, target `v850-elf`, and
`v850-elf-gcc -fPIC -ffreestanding -c main.c`. The current
`v850-gcc-scratch` image history is the same recipe and GCC configure command;
GCC reports `-mghs`/`-mrh850-abi` enabled and `-mgcc-abi` disabled by default.
The published encrypted payload is already pinned as
`tests/fixtures/payloads/ram_dump_payload.bin` (SHA-256 `d972d4bf…b2`). After
normal Toyota payload decryption it contains a 438-byte executable prefix,
SHA-256 `8b3f55e3950ca59e5175f6356df9ab96a34cb4515df11c6fd8c73f8f17bfc5eb`,
followed by zeros to the callback slot. Recompiling Willem's pinned
`shellcode/main.c` with that source-equivalent image and his exact build command
reproduces those **438 bytes byte-for-byte**.

That public payload also shows why a working GCC shellcode is not evidence that
ordinary C calls can replay arbitrary Toyota internals. Willem's dump loop is
self-contained RSCFD MMIO. Its only stock call occurs after extraction, when it
invokes boot reset `0x157E`; GCC materializes that constant in `r10` and emits a
small indirect veneer before `jmp [r10]`. It therefore never creates the
`r6=target_address` state that broke our later `call0(address)` startup replay,
and the reset target is a terminal no-argument path. This is strong validation
of GCC 13.2 for **standalone RH850 payloads**, not of C as an exact stock-call
replay abstraction and not of Toyota's original compiler vendor.

Practical consequence: do not switch target-native payloads to CC-RH merely
because its switch/prologue output looks Toyota-like. More importantly, this ABI
result does not make a C trampoline such as `call0(address)` equivalent to a
stock direct `jarl`: passing `address` still materializes argument state in `r6`,
whereas exact replay must preserve the original call-site register state.

## Switch jump-table recovery

`RecoverSwitchTables.java` recovers the RH850 `switch reg` idiom. The table size
is taken **only** from the compiler's range-check prefix (`cmp IMM` +
`bh`/`bnh` → `IMM+1`, or `addi -N,rX,r0` + `bc`/`bnc` → `N`). For each site it
then:

1. defines a `short[N]` array immediately after the instruction, labels it
   `switch_table_<addr>`, and comments the switch with the table address/size;
2. adds `COMPUTED_JUMP` references from the switch to every case target and
   `DATA` references from each table halfword to its target; disassembles case
   entries when needed.

### Why the prefix bound is the only trusted trigger (measured, not asserted)

`InventorySwitchTables.java` runs the recovery's bound+validation logic against
**all 247** decoded `switch` opcodes in this image (not just the in-function
ones) and emits `data/switch_table_inventory.csv`. The result:

| Class | Count | Bound | Verdict |
|---|---:|---|---|
| Real switches | **20** | `cmp+bh` (17) / `addi+bc` (3) | recovered; all in-function |
| Packed-case0 hits | 4 | packed-case0 (no prefix bound) | **false positives** — unreachable data misread as code (e.g. repeated `switch r12`/`nop` pairs in data at `0xd38xx`; offsets like `+25600`, `+32767`, repeated `+0`) |
| Other decoded `switch` | 223 | none | no plausible table (`no-bound` / `nested-switch`) |

Every real switch carries the compiler range check; the packed-case0 fallback
matched **only** data (4/4 false positives), so it was removed as a recovery
trigger. Requiring the prefix bound recovers the same 20 tables with zero false
positives.

### `AssertSwitchTables` is a full-coverage verifier, not a count assert

`AssertSwitchTables.java` (run by `make verify-processor`) scans **every**
decoded `switch`, independently recomputes which ones are prefix-bound with a
valid table, and asserts that set **exactly equals** the recovered set. This
proves three things each run:

- **completeness** — every prefix-bound switch has a sized `short[N]` table and
  complete `COMPUTED_JUMP` case coverage (real switches are never missed);
- **soundness** — no switch without a prefix bound is recovered (no data
  mislabelled as a switch table);
- **the boundary itself** — the 227 unrecovered `switch` opcodes are measured
  collisions, not an assumption: none carries the range check a real compiler
  switch requires.

`make verify-processor` reruns this measurement read-only into `build/out/` and
compares it with the committed `data/switch_table_inventory.csv` baseline.

## Accepted unimplemented ops

Instructions that decode but intentionally use opaque `callother` p-code are
listed by user-op name in `data/processor_unimpl_allowlist.txt`. The inventory
resolves CALLOTHER indexes to `__cache`, `__prefetch`, `__disable_irq`,
`__enable_irq`, `__nop`, and `__synchronize`; verification fails for either an
unapproved used op or a stale allowlist entry.

## Isolated install and processor fingerprint

The module is copied to `build/cache/processor-extension-src/`, compiled there, and
installed into `build/cache/ghidra-home/.../Extensions/Renesas_v850/` (via
`-Duser.home`). Vendored sources and `$GHIDRA_HOME/Ghidra/Extensions` are never
mutated. A conflicting install-tree copy causes an actionable failure, and a
clean `analyzeHeadless` subprocess proves that the isolated language resolves.

`tools/project/fingerprint_processor.py` hashes language specifications,
DWARF mappings, pattern XML, extension metadata, the compiled SLA, and Ghidra
versions.
Rebuilds write `processor_manifest.json` beside `build/work/project/`.
`make work-project` performs a Ghidra-free source check. Processor audits and
`make snapshot-project` require source files, compiled SLA hash, Ghidra version,
and CLI version all to match the project manifest. The committed full baseline is
`data/processor_manifest.baseline.json`; `make verify-processor` compares it with
the freshly built processor manifest before running project audits.

Instruction inventory for this firmware is committed as
`data/instruction_inventory.csv`. `make verify-processor` emits a temporary fresh
inventory under `build/out/` with `InventoryUsedInstructions.java` and compares it
byte-for-byte with the committed baseline instead of mutating tracked evidence.

### Ghidra 12.1.4 migration

The repository is pinned to Ghidra **12.1.4**. The 12.1.3→12.1.4 migration
itself changed only inventory-version metadata; the compiled language and
semantic project rows were unchanged at that milestone. This later P1M-E
hardware-spec correction intentionally changes the processor language and
persisted semantics. The current source fingerprint is
`219148ff9a4c095219d5fc1f46a7bf1f5c517094e5c0da0a2dc79e9115e4c357`;
its compiled SLA is
`a7560830060d2bbe28708aec5e35cd5ec495d1bf8d1f9009803548def5532f4a`.
Two independent clean rebuilds of every registered target agree under that
compiled language. See
[the migration journal](../history/2026-09/GHIDRA_12_1_4_MIGRATION_2026-09-21.md)
for the earlier version-only migration evidence.

## Exact project parity

The current normalized project inventory has **7,090 functions, 197,726
instructions, and 8,813 symbols**. Aggregate floors remain useful as a fast
collapse detector, but they cannot detect equal-count substitutions. The deterministic
`ExportProjectInventory.java` exporter therefore records path-free Ghidra and
program identity, every memory mapping, function entry/body/signature/parameter
storage, user-defined symbol, listing/function comment, bookmark, and aggregate
map in `data/ghidra_project_inventory.baseline.jsonl`.

`make verify-project-parity` exports the working project and compares every
normalized row. `make update-project-baseline PROJECT_DIR_A=... PROJECT_DIR_B=...`
is the explicit update path and requires two independent rebuilds to agree;
ordinary verification never mutates the baseline. The parity gate caught both
a stale 5,913-function snapshot and a Ghidra script-path hazard that added 194
spurious functions when `ghidra/scripts/investigate` was present.

## Semantic coverage ledger

Whole-image structural function inventory (not full semantic understanding):

- Exporter: `ghidra/scripts/verify/ExportSemanticCoverageLedger.java`
  (read-only headless against `build/work/project/` only).
- Generator: `make generate-semantic-coverage` /
  `tools/project/export_ghidra_project.sh semantic-coverage`
- Artifacts: `data/semantic_coverage_ledger.csv` and
  `data/semantic_coverage_summary.json`
- Gate: `tests/tooling/verify_semantic_coverage.py` (runs in the
  `tools/test full` / `local` sweeps, not core)

Each CSV row is one discovered function, sorted by entry address, with Ghidra
discovery and name provenance, calling convention, caller/callee counts,
structural reference metrics, curated review state, semantic evidence grade,
verification source, oracle class, and execution status. These dimensions are
independent:

| Review state | Meaning |
|---|---|
| `unreviewed` | structurally discovered; no semantic review recorded |
| `reviewed_unknown` | decompiled/reviewed, but exact semantics remain unknown |
| `structurally_bounded` | structure constrained without an exact semantic identity |
| `semantically_identified` | a concrete role is supported by the cited evidence |

Evidence grade is blank unless a curated review supports `bounded`,
`recovered`, or `verified`. A user-defined name, body hash, generated
self-check, or successful decompilation does not create a semantic grade.
Optional structural columns (`root_kind`, RAM/MMIO/`codeflash_data`/string reference
counts, coarse `boot`/`application` subsystem) are filled only from reliable
program facts; otherwise empty or zero. `codeflash_data_ref_count` is every
DATA reference into CodeFlash that is not a function entry (scalars included),
not a table-only classifier. The ledger deliberately does **not** claim that
every function is behaviorally understood.

Current review counts are generated in `data/semantic_coverage_summary.json`.
The curated conclusions live in `data/semantic_review_status.csv`; automatic
decompilation-only entries are not counted as reviews. The earlier selected
sweep and corrected-graph re-audit remain in the
[historical report](../history/2026-08/CORRECTED_GRAPH_REAUDIT_2026-08-11.md).

This in-function inventory is not an executable denominator. After importing
the upstream function-start patterns, the separate outside-function exporter
records 900 conservative candidate runs containing 7,186 decoded instructions
in 18,138 bytes: 281 orphan decoded runs and 619 pointer-referenced runs, all
unresolved. Two independent four-stage rebuilds converge at 7,090 functions /
197,726 instructions, exactly +714 functions / +14,486 instructions over the
prior 6,376 / 183,240 graph. The 60 targets referenced by `0x27C88..0x27D77`
are exact functions now, while their missing dispatch consumer remains a
separate bounded negative.

## 2026-10-08 cross-implementation and G3M-manual audit

The vendored language was compared instruction-by-instruction with Ghidra
`c7bc89dd29ee7f56b753b29a8bbabcb36ad3cae7`, Rizin
`0ed7bdfdaf186a26ff24eee62f41b10c154b5a99`, and radare2
`391dc446b5f12000c9588bff162a45689463eff6`. The RH850G3M software manual
R01US0123EJ0140 Rev.1.40 remains authoritative when those implementations
disagree. Their broad G3K/G4/debug/hypervisor opcode sets were not copied into
the exact G3M language.

Useful upstream Ghidra assets are now retained locally:

- `data/languages/v850.dwarf` maps the GCC DWARF register numbers, including
  `sp`, `gp`, `tp`, `ep`, and `lp`;
- `data/patterns/v850_patterns.xml` recognizes PREPARE/ADDI function prologues
  after architectural return boundaries;
- both assets participate in `processor_manifest.json` source fingerprints.

The graph effect is reproducible rather than a one-project analyzer accident.
Every registered target has byte-identical normalized inventories from two
independent four-stage rebuilds:

The “before” columns are the tracked normalized inventories immediately before
the processor refresh. Camry's separately recovered 6,065-real-function
checkpoint had not yet been promoted as that baseline; the current 7,178 count
is +1,113 relative to that byte-audited checkpoint.

| Target | Functions before | Functions after | Δ | Instructions before | Instructions after | Δ |
|---|---:|---:|---:|---:|---:|---:|
| Sienna `8965B4512000` | 6,376 | 7,090 | +714 | 183,240 | 197,726 | +14,486 |
| Camry `8965F3307000` | 6,056 | 7,178 | +1,122 | 187,475 | 205,829 | +18,354 |
| Crown `8965F3012000` | 5,864 | 6,972 | +1,108 | 184,505 | 198,930 | +14,425 |
| Corolla `8965F1208000` | 5,811 | 6,934 | +1,123 | 178,237 | 199,413 | +21,176 |
| Corolla `8965H1202000` | 5,811 | 6,934 | +1,123 | 178,222 | 199,403 | +21,181 |
| Venza airbag `8917048E30` | 4,006 | 10,391 | +6,385 | 154,859 | 297,293 | +142,434 |

In Sienna, the recovered functions expose previously hidden, byte-verified
readers at `0xC7376`, `0xC746C`, `0xC78E6`, and `0xC7F58`; the SecOC and
motor-boundary reference assertions now include those reads instead of
preserving stale negative censuses.

Camry is the clearest quality check because the larger recovered graph was
re-audited against target bytes rather than accepted by count. Marking exact
CodeFlash `0x10000..0x17FFF` as non-executable calibration/metadata removed
three pattern-created phantom starts (`0xB21CA`, `0xB1406`, `0xC11D2`) and their
fabricated callers. The retained graph newly resolves the callback-table
targets `0x3B400/0x3B434` and `0x3B4A8/0x3B4DC` into the shared state machine
at `0x6AE7C`, plus previously missing reads of B6 application-state snapshots.
Those data references refine command-magnitude supervision and sibling-state
readiness; they do not add an external ingress or an output-authority path.

The stronger graph also improves the exploit negative without turning coverage
into proof by count. The target-native recensus covers every function-owned
indirect transfer, reduces all directly referenced RAM call sources to five
fixed cells below the application XCP write floor, finds no static or raw
CodeFlash pointer into the retained high-tail carrier, and keeps all recovered
DMAC endpoints outside that window. Fifty parameter-vector call sites in ten
unreferenced library routines remain an explicit static-analysis boundary.
Exact counts, addresses, and the resulting bounded negative are owned by the
[Camry report](../variants/camry-2026-live-baseline.md#135-control-transfer-audit-the-missing-primitive).

The corrected G3M register map changes decompiler names and system-state
interpretation, not firmware bytes. No current vehicle or exploit conclusion
depended on the former `SPID`/`IMSR`/`RDBCR` labels; persisted projects and
corpora were nevertheless rebuilt so future register dataflow starts from
`PID`/`PMR`/`CDBCR` rather than carrying the stale aliases forward.

The language-semantics change increments the V850E2M registration to
version `0.4` and the RH850G3M registration to `0.5`; stale compiled languages
therefore cannot silently satisfy a project fingerprint.

The external opcode tables exposed six inherited mnemonic defects:
`DIVQ`, `CVTF.DW`, `CVTF.LD`, `CVTF.ULD`, `DIVF.D`, and `FLOORF.SW` decoded as
other instructions. The G3M manual additionally established `SF` (not `SD`) as
floating compare condition 8 and the `CMOVF` true/false operand order. Fixtures
now cover every corrected spelling and execute both `CMOVF.S` outcomes.

The same manual audit corrected machine semantics rather than only display:

- `CLL`, `LDL.W`, and `STC.W` carry an explicit load-link address/valid state.
  A conditional store fails after `CLL`, an address mismatch, exception entry,
  or `EIRET`/`FERET`. `CTRET` preserves the link. Local writes invalidate links
  in the same 32-byte unit (G3M Table 5-3), including scalar, short, extended,
  bit-update, `CAXI`, `PREPARE`, and `PUSHSP` stores; adjacent units do not;
- all divide forms avoid host division on a zero divisor, preserve the
  architecturally undefined result registers in that case, and set `OV`;
- register shifts and register-indexed bit operations use the specified low
  five and three bits; `ROTL` updates `CY` from result bit 0 even for a zero
  rotation;
- bit searches return the architectural one-based position, return zero on no
  match, set `CY` only for a match at the final searched bit (result 32), set
  `Z` only for no match, and clear `OV/S`; `BSH`/`HSH` derive `Z` from the lower
  halfword;
- `LOOP` always writes the decremented counter and flags before its branch
  decision, and indirect `JARL` preserves an aliased source before writing the
  link register;
- `CALLT`/`CTRET` save and restore only `PSW(4:0)`;
- `FETRAP`, `TRAP`, `RIE`, and `SYSCALL` save the G3M cause registers, clear
  `PSW.UM`, set the specified exception-state bits, and select masked
  `RBASE`/`EBASE` through `PSW.EBV`;
- `CACHE` and `PREF` now emit named `__cache`/`__prefetch` userops instead of
  undefined p-code.

Selection-ID 0 no longer gives reserved G3M slots names imported from other
RH850 variants. The Venza image is bounded to the P1x-C family, whose persisted
hardware manual specifies RH850G3M cores, so it shares the core decoder and
system-register semantics. Its exact device remains unknown: no P1M-E
peripheral-register labels, memory capacities, or SFR claims transfer to it.

Venza additionally required its exact capture boundary in the target profile:
the `0x180000..0x2FFFFF` fill partition is non-executable and typed as data.
That removes one direct-call-created function in erased space. Its larger
pattern-recovery gain is deterministic discovery of previously disconnected
entry-shaped code, not evidence for an exact device part or peripheral map.

The post-commit review found and corrected three gaps in the initial refresh:
the load-link lifetime above was incomplete, the bit-search carry fixture
endorsed the wrong first-bit result, and the imported DWARF file was not
registered in either language definition. Both languages now declare
`DWARF.register.mapping.file`; an installed-Ghidra smoke resolved all 32
registers and the stack register for each. The processor fixture now contains
96 instruction cases and executes reservation-lifetime sequences for each local
write encoding and modeled exception transition, plus first/last/no-match search
boundaries. A separate instruction-sequence smoke confirms that
`LDL.W → EIRET → STC.W` fails without writing and that
`SCH0R(0xFFFFFFFE)` returns 1 with `CY=0`.

## What these audits do *not* claim

- Zero undefined bytes inside the current functions proves in-body decode
  coverage, not discovery of every executable body and not every
  p-code edge case (FP rounding, hypervisor ops, unexercised arithmetic forms, …).
- Floating-point p-code uses Ghidra's round-to-nearest primitives and does not
  deliver enabled IEEE-754 exceptions from `FPSR`; cache/prefetch userops do not
  emulate cache contents; load-link invalidation by external agents is outside
  instruction-level emulation.
- Exact function/instruction counts are smoke signals; prefer the asserting
  invariant scripts and the generated semantic coverage ledger for coverage
  floors.
- A provisioned SecOC key or live ICU-S behavior cannot be proven from this
  dump alone; see the firmware evidence docs for dynamic caveats.

## Why auto-analysis options are left on defaults

The rebuild (`tools/project/rebuild_project.sh`) runs Ghidra's default analyzers and does
not disable "Address Tables" or "Non-Returning Functions" (a recommendation
sometimes given for raw automotive images). This is deliberate for this image:

- **Address Tables:** the over-eager-disassembly symptom it warns about *is*
  present — 227 decoded `switch` opcodes are unreachable data misread as code
  (see "Switch jump-table recovery" above). However most of those come from the
  general disassembly pass following word-aligned operands into data, not from
  this one analyzer, so disabling it alone would not remove them. The real
  defense here is seeding all known functions before the first analysis pass
  (`SeedEntries`, `SeedUdsServiceTable`, …, run as preScripts), which gives the
  code finder real anchors. The residual noise is then filtered soundly and
  completely by `RecoverSwitchTables` / `AssertSwitchTables` (20 real tables,
  zero false positives). The final annotated project is clean.
- **Non-Returning Functions:** no false positives have been observed in this
  image — no truncated control flow or unreachable code after a call is flagged
  by the invariant audits. Disabling it would instead add cost: the genuine
  noreturn functions (boot failure loop `0x1398`, foreground cyclic loop,
  bootloader reset path) would have to be marked `setNoReturn` by hand to keep
  their call sites' decompilation clean.

Net: leaving the defaults is a net win here. Revisit only if a future rebuild
surfaces no-return false positives (truncated control flow) or a large new crop
of data-as-code switches that the prefix-bound recovery cannot audit out.
