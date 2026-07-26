# Plugin verification: v850e3 SLEIGH against the P1M-E firmware

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
| Vector recovery | INTBP/EBASE handlers + `__interrupt` | `RecoverVectorHandlers` |
| Calling conventions | Explicit `__stdcall` on non-ISR functions | `ApplyCallingConventions` |
| Switch tables | In-function `switch` jump tables + xrefs | `RecoverSwitchTables` / `AssertSwitchTables` |

Automated gate:

```bash
make verify            # firmware-only, no Ghidra
make verify-sleigh     # compile + isolated install
make verify-processor  # fixtures (+ working-project audits if present)
make verify-ghidra     # all of the above
```

Working-project audits require a materialized copy:

```bash
make work-project
make verify-processor
```

## System-register coverage (ldsr / stsr)

Script: `ghidra/scripts/investigate/FindSystemRegisterOps.java`
(asserting companion: `ghidra/scripts/verify/AssertSystemRegisterNames.java`).

Every system-register transfer in the firmware decodes with a correct register
name; there is nothing to add to the `selID` tables in `v850e3.sinc`. Across the
whole CodeFlash the firmware uses **324** such instructions (**242 `ldsr`** +
**82 `stsr`**) and **zero** `ldtc`/`sttc`/`ldvc`/`stvc` (the thread-/virtual-
context transfers are absent, consistent with the P1M-E having no hypervisor or
virtualization extension). No operand decodes to a blank or raw token.

The distinct registers referenced, all named correctly:

- **selID 0** (common, `v850_common.sinc`): `PSW`, `EIPC`, `EIPSW`, `FEPC`,
  `FEPSW`, `CTPC`, `CTPSW`, `EIIC`, `FEIC`, `EIWR`, `FEWR`, `CTBP`, `BSEL`.
- **selID 1**: `EBASE`, `INTBP`, `MCTL`, `SCCFG`, `SCBP`, `SPID`, `FPIPR`.
- **selID 2**: `MEA`, `MEI`, `ASID`, `IMSR`, `INTCFG`.
- **selID 4** (cache): `ICTAGL`, `ICTAGH`, `ICDATL`, `ICDATH`, `ICCTRL`, `ICERR`.
- **selID 5/6/7** (MPU): `MPM`, `MPRC`, `MCA`, `MCS`, `MCR`, `MPAT0–15`,
  `MPLA0–15`, `MPUA0–15`.
- **selID 13**: `RDBCR`.
- FPU: `FPSR`, `FPEC`, `FPEPC`.

Two points worth recording:

- `IMSR` (the subject of upstream issue #40, "decoded where it should be PMR")
  is **correct** for the P1M-E. The firmware uses it for the standard
  interrupt-mask critical section (`stsr IMSR,rN` / `ldsr rN,IMSR` around
  protected regions). Issue #40 concerns a newer multicore ICU, not this core.
- `EIC136`/`EIC292`/`EIC293` are **memory-mapped** peripheral registers at
  `0xFFFFB110` / `0xFFFFB248` / `0xFFFFB24A`, accessed via `ld.w`/`st.w`, not
  `ldsr`/`stsr`. They are therefore out of scope for the `selID` tables and are
  named through the device profile / project labels, not the processor module.

## Instruction-decode coverage

Script: `ghidra/scripts/investigate/FindUndefinedInFunctions.java`
(asserting companion: `ghidra/scripts/verify/AssertNoUndefinedInFunctions.java`).

The firmware disassembles completely: **zero** undefined bytes occur inside
any of the 5560 function bodies. A SLEIGH decode failure would leave a hole
inside a function; none exists, so the module decodes every instruction the
compiler emitted.

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
  `jarl`/`jmp [lp]` flow types are checked on fixtures.

Landmark decompiler checks (secrets at `0xBFD8`/`0xBFE8`, ISR calling
convention, session-control decompilation, SecurityAccess expected-key,
ICU dispatch callee, boot reset) live in
`AssertDecompilerInvariants.java`; the gate writes deterministic normalized-C
hashes to `build/decompiler-signatures.txt`, compares them with
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
CSV coverage is checked by `tests/verify_p1m_device_profile.py`; project
invariants require the windows, a landmark label subset, and the structured
overlays above.

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
**all 251** decoded `switch` opcodes in this image (not just the in-function
ones) and emits `data/switch_table_inventory.csv`. The result:

| Class | Count | Bound | Verdict |
|---|---:|---|---|
| Real switches | **19** | `cmp+bh` (16) / `addi+bc` (3) | recovered; all in-function |
| Packed-case0 hits | 5 | packed-case0 (no prefix bound) | **false positives** — unreachable data misread as code (e.g. six `switch r12`/`nop` pairs in a row at `0xd38xx`; offsets like `+25600`, `+32767`, repeated `+0`) |
| Other decoded `switch` | 227 | none | no plausible table (`no-bound` / `nested-switch`) |

Every real switch carries the compiler range check; the packed-case0 fallback
matched **only** data (5/5 false positives), so it was removed as a recovery
trigger. Requiring the prefix bound recovers the same 19 tables with zero false
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
- **the boundary itself** — the ~232 unrecovered `switch` opcodes are measured
  collisions, not an assumption: none carries the range check a real compiler
  switch requires.

Re-run the measurement anytime with
`ghidra ... -postScript InventorySwitchTables.java <out.csv>` (read-only).

## Accepted unimplemented ops

Instructions that decode but intentionally use opaque `callother` p-code are
listed by user-op name in `data/processor_unimpl_allowlist.txt`. The inventory
resolves CALLOTHER indexes to `__disable_irq`, `__enable_irq`, `__nop`, and
`__synchronize`; verification fails for either an unapproved used op or a stale
allowlist entry.

## Isolated install and processor fingerprint

The module is copied to `build/processor-extension-src/`, compiled there, and
installed into `build/ghidra-home/.../Extensions/Renesas_v850/` (via
`-Duser.home`). Vendored sources and `$GHIDRA_HOME/Ghidra/Extensions` are never
mutated. A conflicting install-tree copy causes an actionable failure, and a
clean `analyzeHeadless` subprocess proves that the isolated language resolves.

`tools/fingerprint_processor.py` hashes every `.slaspec` / `.sinc` / `.cspec` /
`.pspec` / `.ldefs` / metadata file plus the compiled SLA and Ghidra versions.
Rebuilds write `processor_manifest.json` beside `build/project/`.
`make work-project` performs a Ghidra-free source check. Processor audits and
`make snapshot-project` require source files, compiled SLA hash, Ghidra version,
and CLI version all to match the project manifest. A committed full baseline lives at
`data/processor_manifest.baseline.json`.

Instruction inventory for this firmware is committed as
`data/instruction_inventory.csv` (regenerate via
`InventoryUsedInstructions.java` after a rebuild if coverage changes).

## What these audits do *not* claim

- Zero undefined bytes inside functions proves decode coverage, not every
  p-code edge case (FP rounding, hypervisor ops, unexercised arithmetic forms, …).
- Exact function/instruction counts are smoke signals; prefer the asserting
  invariant scripts for semantic gates.
- A provisioned SecOC key or live ICU-S behavior cannot be proven from this
  dump alone; see the firmware evidence docs for dynamic caveats.
