# V850/RH850 processor and automatic-analysis audit

> **Scope:** vendored V850/RH850 plugin, including broader family functionality; firmware results remain target-specific
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades.
>
> **Canonical artifacts:** `data/semantic_coverage_ledger.csv`
>
> **Verification:** `make verify-processor`
>
> **Related:** [WORKFLOW](../WORKFLOW.md), [firmware-architecture](../architecture/firmware-architecture.md)

This owns architectural and automatic-analysis evidence for
`ghidra/ghidra_v850`. Earlier firmware counts, addresses and conclusions below
are **legacy Sienna `8965B4512000` checkpoints**, unless another target is named.
They are not the plugin's support boundary. Decode coverage and p-code semantic
correctness remain separate; the checks are layered:

| Layer | What it proves | How to run |
|---|---|---|
| SLEIGH compile | All four ISA profiles compile | `make verify-sleigh` |
| Synthetic fixtures | Selected encodings plus executed register/memory/flag vectors | `make verify-processor` |
| Function-body decode | No undefined bytes inside recovered functions | `AssertNoUndefinedInFunctions` |
| System-register naming | Every `ldsr`/`stsr` operand is named | `AssertSystemRegisterNames` |
| Project invariants | Critical labels/functions/memory/context | `AssertProjectInvariants` |
| Decompiler invariants | Landmark ABI/decompiler properties + no unset conventions | `AssertDecompilerInvariants` |
| Device profile | RAM/SFR map + SFR labels/types + boot/application GP/TP context | `ApplyP1MDeviceProfile`, `ApplyP1MSfrTypes` |
| LocalRAM overlays | Typed payload/SecOC/DID/checkpoint roots on LocalRAM | `ApplyRamTypes` |
| Vector recovery | INTBP/EBASE handlers + `__interrupt` | `RecoverVectorHandlers` |
| Calling conventions | Explicit `__stdcall` on non-ISR functions | `ApplyCallingConventions` |
| Switch tables | Automatic native/direct-jump/loaded-relative/loaded-absolute recovery; target annotations remain available | `V850SwitchAnalyzer` / `AssertV850SwitchAnalysis` |

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

[GNU DWARF numbering](../../ghidra/ghidra_v850/data/languages/v850.dwarf) is
shared across language profiles. Slots 0–31 name the GPRs (including SP at
3); 32–35 map to EIPC/EIPSW/FEPC/FEPSW, 37 to PSW, 48/49/52 to
CTPC/CTPSW/CTBP, and 64 to PC. This mapping is registered in the language
definitions and participates in the processor fingerprint.

Reserved register-number slots remain unnamed. G4 guest, virtualization,
thread-context, TLB, and hypervisor instructions were removed from the G3M
language rather than left as plausible decodes. The synthetic processor
fixture includes `MCFG0`, `PMR`, `MCC`, and `CDBCR` transfers and asserts the
decoded operand register, so a future name/selection regression fails before
project analysis.

G3M cache-control reads are not ordinary register round trips. **CDBCR.CDBCLR**
bit 1 is write-only/read-as-zero (R01US0123EJ0140 Table 3-64, p.110): `STSR`
masks that bit without discarding `LDSR` command writes. **ICCTRL.ICHCLR** bit 8
instead reads one until hardware completes clearing (Table 3-60, p.106).
Both registers use native `register_data` volatility: ICCTRL observations must
remain hardware-dependent, and CDBCR command/control writes must remain
externally observable. This is not a complete reserved-bit, cache-content or
completion-timing model. G4MH is not assigned this G3M protocol: E2x-FCC2
Table 3.79 (p.345) specifies that its ICHCLR reads zero.

The processor fixture embeds the exact 136 bytes of Camry `8965F3307000`
function `0x3614`. It exercises both modes with an explicit environment-supplied
completion event, checks the shared return separately from opaque `SYNCI`, and
requires reachable high-IR command writes, nonconstant ICCTRL polls and return.

**PMR** also uses native `register_data` volatility: its writes change the
interrupt-priority ceiling even when no subsequent software read consumes the
value (R01US0123EJ0140 Table 3-33, p.75). Previously the decompiler could discard
those writes from Camry's `0x701C4`/`0x701EA` helpers. The processor fixture now
embeds their exact 68 bytes, executes eighteen lower/equal/higher-mask,
signed-comparison and unconditional-restore cases across both incoming ID states,
and checks reachable high-IR PMR writes, old-mask-dependent branching and return.
The execution cases seed `FPEC=0`. Fresh Camry decompilations retain the
conditional-enter and unconditional-restore PMR writes.

`EIC136`/`EIC292`/`EIC293` remain memory-mapped peripheral registers at
`0xFFFFB110` / `0xFFFFB248` / `0xFFFFB24A`, accessed via `ld.w`/`st.w`.
They belong to the device profile and are excluded from the `ldsr`/`stsr`
system-register table.

## Instruction-decode coverage

Renesas manuals define the ISA and operand forms. The G3M instruction help
index uses Appendix D of R01US0123EJ0140 Rev. 1.40. Comparison revisions for
Ghidra, Rizin, radare2 and IDA live in
[`PROVENANCE.json`](../../ghidra/ghidra_v850/PROVENANCE.json).
All 184 Rizin ISA mnemonic IDs have counterparts after spelling normalization
(e.g. `stasub` → `satsub`); the radare2 table contains 403 CPU-masked forms
and 324 spellings. The G3M manual census found no missing G3M mnemonic.
Profile acceptance also depends on register and encoding constraints.

The exact G3M profile excludes later or other-family forms such as `SATS`,
`ROUNDF.*`, `DST`/`EST`, `DB*` trace/debug, `HVCALL`/`HVTRAP`, TLB,
DSP accumulators, `BINSL` and `DIVN`. It dispatches exceptions through
RBASE/EBASE. V850E2M separately accepts `MADDF.S`, `MSUBF.S`, `NMADDF.S` and
`NMSUBF.S` with split `reg4` (R01US0001EJ0100 pp. 374, 380, 386, 388).

`AssertV850LanguageProfiles` checks Format XIV forms on E2M and RH850 and
their absence on E1F. For `LD.HU`, bit 4 in the second halfword is fixed at
zero and the signed displacement is even (`a6 07 67 44 00 00` loads at
`+0x46`; `a6 07 e7 47 ff ff` loads at `-2`). `SST.B/H/W` print the source
before the EP-relative destination (R01US0123EJ0140 pp. 249–250, 307–309).

Script: `ghidra/scripts/investigate/FindUndefinedInFunctions.java`
(asserting companion: `ghidra/scripts/verify/AssertNoUndefinedInFunctions.java`).

The recorded legacy-Sienna checkpoint had **zero undefined bytes** inside its
7,090 recovered functions. This establishes in-body decode for that checkpoint.
Semantic fixtures under `tests/fixtures/processor/` and the asserting scripts
cover:

- signed `sld.b` / `sld.h` sign-extend. `TST` derives S/Z from the bitwise
  AND: disjoint nonzero operands set Z;
- saturating arithmetic derives S/Z from the clamped result and CY/OV from
  the unclamped calculation. `SATADD(INT_MAX,1)` clears S and sets sticky SAT
  (R01US0123EJ0140 pp. 284–288, 332).
- `ld.w` `disp16` scaling (`field × 2`) is checked by an executed memory load;
- `prepare`/`dispose` stack/register effects and direct/indirect
  `jarl`/`jmp [lp]` flow types are checked on fixtures;
- inventory-driven risky ops used by this image: `switch` table walk +
  `BRANCHIND`, `callt` CTBP-relative `CALLIND`, `bins` bitfield insert,
  `set1`/`clr1`/`tst1` bit-memory side effects and Z semantics, `cmovne`
  taken/not-taken, signed `mulhi`, and arithmetic `sar`;
- `PUSHSP`/`POPSP` handle the full 32-register range; reversed ranges leave SP
  unchanged. The word accesses align down and SP retains its low bits. A
  push of SP stores its pre-instruction value; a pop through SP consumes the
  saved word without restoring it (R01US0123EJ0140 pp. 273–274, 278);
- `CAXI` captures both inputs before returning the old word, including when
  its compare and exchange registers alias. E2M aligns both the load and
  store to the same word (R01US0123EJ0140 pp. 210–211;
  R01US0001EJ0100 pp. 81–82).

Further G3M fixture coverage follows R01US0123EJ0140:

- Decode fixtures pin `DIVQ`, the floating-point spellings `CVTF.DW`,
  `CVTF.LD`, `CVTF.ULD`, `DIVF.D` and `FLOORF.SW`, compare condition 8 (`SF`),
  and both true/false operand selections of `CMOVF.S`.
- `LDL.W` sets the reservation for `STC.W`. `CLL`, exception entry and
  `EIRET`/`FERET` clear it; `CTRET` preserves it. A conditional store to a
  different address fails. Local writes invalidate within the same 32-byte unit
  (Table 5-3), including scalar, short, extended, bit-update, `CAXI`,
  `PREPARE` and `PUSHSP` stores.
- Two-operand `DIVH` is signed. Divide on zero sets OV and preserves the
  undefined result registers without invoking host division. Register shifts
  and indexed bit operations take the low five and three bits respectively.
  `ROTL` takes CY from result bit 0, including zero rotation (p. 280).
- Bit searches return a one-based position or zero on no match. CY marks
  result 32; Z marks no match; OV/S clear. `BSH`/`HSH` take Z from the lower
  halfword. `LOOP` stores its decremented count and flags before branching,
  and indirect `JARL` preserves an aliased target before writing the link.
- `CALLT`/`CTRET` save and restore only PSW(4:0).
  `FETRAP`, `TRAP`, `RIE` and `SYSCALL` save the G3M cause registers, clear
  `PSW.UM`, set the exception-state bits and select masked `RBASE`/`EBASE`
  through `PSW.EBV`.

Landmark decompiler checks (secrets at `0xBFD8`/`0xBFE8`, ISR calling
convention, session-control decompilation, SecurityAccess expected-key,
ICU dispatch callee, boot reset) live in
`AssertDecompilerInvariants.java`; it checks recovered calling conventions,
parameter widths, secret-address references and successful decompilation.
It does not pin the spelling or whole-text hash of decompiled C.
Every non-thunk function must carry an explicit `__stdcall` or `__interrupt`
prototype — Ghidra's anonymous `unknown`/`default` is treated as a failure.

## Device profile and interrupt recovery

P1M-E, P1x-C main CPUs and D1L/D1M share one G3M decoder. Their processor
specifications mark CPU-side I/O volatile independently of the memory blocks,
SFR labels and types applied by device scripts:

| G3M profile | I/O volatility and authority |
|---|---|
| P1M-E (`v850e3:LE:32:default`) | H-Bus on-chip I/O at `0x10000000..0x1FFFFFFF`, plus the P-Bus and LPB windows (R01UH0585EJ0120 Table 4.1) |
| P1x-C (`v850e3:LE:32:P1xC`) | Main CPU P-Bus and LPB self windows; the H-Bus aperture can contain external memory (R01UH0517EJ0130 Fig. 4.1) |
| D1L/D1M (`v850e3:LE:32:D1LD1M`) | CPU PBUS windows at `0xFF400000..0xFFFDFFFF` and `0xFFFEE000..0xFFFFFFFF`; XC1 and DataFlash retain ordinary memory semantics (R01UH0451EJ0220 Fig. 5.1) |

P1M-E leaves flash, including configuration/OTP, and reserved gaps outside
the volatile ranges. `0xFFFF0000` is reserved on P1M-E and P1x-C, but in
the upper PBUS window on D1L/D1M. The Venza and
[R4P meter](../variants/yc-r4p-2024-meter.md#normalization-and-analysis-model)
use family-compatible profiles; their exact device parts are unidentified.
Both profiles were exercised on Ghidra 12.2 imports of the original images.

Raw imports use the language in the
[target registry](../../data/analysis_targets.json). ELF uses machine
and architecture flags: `EM_V800` selects E2M or broad RH850 under the
default ABI, and `EM_V850`/legacy `EM_CYGNUS_V850` select those ISA profiles
under the old-GCC ABI. `AssertV850LanguageProfiles` covers supported flag
combinations, unassigned combinations, and device volatility boundaries.
The IAR scalar register list lives in radare2's analysis database.

Restored snapshots retain their import-time language. To select the
current registered profile, rebuild into a fresh directory:
`make rebuild-project TARGET=<target> PROJECT_DIR=<fresh build/work directory>`.

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

The P1M-E script includes `SFR_EIC0_31` at `0xFFFEEA00` (0x40 bytes,
R01UH0585EJ0120 §6.2.2). CSV coverage is checked by
`tests/firmware/verify_p1m_device_profile.py`; project invariants require
these windows, landmark labels and the structured overlays.

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

## Compiler / ABI fingerprint: volatile `ep`

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
It is local research input. Portable repository builds do not depend on it.

Reference compilation also explains why compiler identification from instruction
shape alone was misleading. CC-RH V2.08 naturally emits the RH850 `switch`
opcode with a compact halfword branch table and a `cmp`/range-branch prefix,
which closely matches the Toyota tables below. That shape therefore does **not**
prove CC-RH. Conversely, the repository's V850 GCC 13.2 toolchain exposes
`-mghs`/`-mrh850-abi` as its default RH850 ABI mode, and the runtime builders
add `-mno-app-regs`; this is compatible with the firmware's fixed `gp`/`tp` and
volatile `ep` model. Compatibility is not compiler provenance: no compiler ID
string or byte-identical runtime-library match has been recovered, so the exact
Toyota compiler vendor/version remains **bounded and unidentified**.

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
and the reset target is a terminal no-argument path. This strongly validates
GCC 13.2 for **standalone RH850 payloads**.

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

### Measured basis for the prefix-bound trigger

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

### `AssertSwitchTables` verifies full coverage

`AssertSwitchTables.java` (run by `make verify-processor`) scans **every**
decoded `switch`, independently recomputes which ones are prefix-bound with a
valid table, and asserts that set **exactly equals** the recovered set. This
proves three things each run:

- **completeness** — every prefix-bound switch has a sized `short[N]` table and
  complete `COMPUTED_JUMP` case coverage (real switches are never missed);
- **soundness** — no switch without a prefix bound is recovered (no data
  mislabelled as a switch table);
- **the boundary itself** — measurement identifies the 227 unrecovered `switch`
  opcodes as collisions: none carries the range check a real compiler switch
  requires.

`make verify-processor` reruns this measurement read-only into `build/out/` and
compares it with the committed `data/switch_table_inventory.csv` baseline.

## Accepted unimplemented ops

Opaque `callother` operations are tracked in `data/processor_unimpl_allowlist.txt`.
Interrupt-controller and synchronization effects remain explicit intrinsics.
`CACHE`/`PREF` accept the operation values defined by R01US0123EJ0140
Tables 7-7/7-8: `chbii`, `cibii`, `cfali`, `cisti`, `cildi`, `prefi` and
cacheop `1111110`, the CLL alias. The named variants use matching user-ops;
the alias clears the reservation. Reserved values remain undecoded.
These forms are exercised by the synthetic fixture; they do not occur in the
legacy Sienna instruction inventory. `NOP` has no user-op.

## Isolated install and processor fingerprint

The module is copied to `build/cache/processor-extension-src/`, compiled there, and
installed into `build/cache/ghidra-home/.../Extensions/Renesas_v850/` (via
`-Duser.home`). Vendored sources and `$GHIDRA_HOME/Ghidra/Extensions` are never
mutated. A conflicting install-tree copy causes an actionable failure, and a
clean `analyzeHeadless` subprocess proves that the isolated language resolves.

`tools/project/fingerprint_processor.py` hashes language specifications,
DWARF mappings, manual indexes, pattern XML, extension metadata, compiled
artifacts, and Ghidra versions. Rebuilds write `processor_manifest.json`
beside `build/work/project/`.
`make work-project` performs a Ghidra-free source check. Processor audits and
`make snapshot-project` require source files, compiled SLA hash, Ghidra version,
and CLI version all to match the project manifest. The committed full baseline is
`data/processor_manifest.baseline.json`; `make verify-processor` compares it with
the freshly built processor manifest before running project audits.

Instruction inventory for this firmware is committed as
`data/instruction_inventory.csv`. `make verify-processor` emits a temporary fresh
inventory under `build/out/` with `InventoryUsedInstructions.java` and compares it
byte-for-byte with the committed baseline instead of mutating tracked evidence.

### Ghidra 12.2 compatibility

The repository is pinned to Ghidra **12.2** and JDK **25+**. The CLI bridge
uses the current single-type removal API; Findcrypt's tracked patch updates
its two cancellation checks to `TaskMonitor.checkCancelled()`.

The compiler-helper analyzer marks instruction-proven GCC/GHS save-helper
`jmp [r10]` exits as returns before native inlining. Ghidra 12.2 otherwise
turns those indirect branches into tail calls and loses the caller's continuation
and stack effects. Mutated helper bodies remain indirect jumps. The fixture
checks the original machine execution and exact escaped-SP deltas; its p-code
resolver also handles constant-index `PTRADD`.

The current source and compiled-artifact identities are recorded in
`data/processor_manifest.baseline.json`. Each project snapshot retains the
processor identity that actually produced it.

The Camry computed-store resolver handles low-word `SUBPIECE` values emitted
for combined GP/TP temporaries. Its refreshed censuses and bound checks pass;
destination-writer matching uses the current named SFRs with address provenance.

## Exact project parity

The legacy Sienna normalized project inventory has **7,090 functions, 197,726
instructions, and 11,249 symbols**. Aggregate floors remain useful as a fast
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
  (read-only, executable-hash-bound, against disposable `build/work/` projects).
- Generator: `make generate-semantic-coverage TARGET=... PROJECT_DIR=...`;
  commands and lifecycle are owned by [WORKFLOW](../WORKFLOW.md#verification).
- Artifact/review paths: `data/analysis_targets.json` fields
  `semantic_coverage_ledger`, `semantic_coverage_summary`, and `semantic_reviews`.
  Legacy Sienna retains its top-level paths; Camry uses its target directory.
- Gate: `tests/tooling/verify_semantic_coverage.py` checks all registered coverage
  targets, including equality with each canonical function-entry inventory.

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
program facts; otherwise empty or zero. `codeflash_data_ref_count` counts every
DATA reference into CodeFlash outside function entries, including scalars and tables.

Review counts are generated in each target's registered summary. Curated
conclusions are separate inputs; automatic decompilation-only entries are not
counted as reviews. Camry's reconstruction evidence and remaining boundaries are
owned by [the reconstruction tree](../../decomp/camry-8965F3307000/README.md#source-and-evidence-ownership).

This in-function inventory is not an executable denominator. For **Sienna**,
after importing the upstream function-start patterns, the outside-function exporter
records 900 conservative candidate runs containing 7,186 decoded instructions
in 18,138 bytes: 281 orphan decoded runs and 619 pointer-referenced runs, all
unresolved. Two independent four-stage rebuilds converge at 7,090 functions /
197,726 instructions, exactly +714 functions / +14,486 instructions over the
prior 6,376 / 183,240 graph. The 60 targets referenced by `0x27C88..0x27D77`
are exact functions now, while their missing dispatch consumer remains a
separate bounded negative.

## Target function-start evidence

[`v850_patterns.xml`](../../ghidra/ghidra_v850/data/patterns/v850_patterns.xml)
recognizes PREPARE/ADDI prologues after architectural return boundaries.
Independent four-stage rebuilds compare normalized inventories for parity.

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

The Venza profile marks the capture's `0x180000..0x2FFFFF` fill partition
non-executable and typed as data; this prevents a direct call from creating
a function in erased space.

## Exact binary32 multiply-add execution

V850E2M `MADDF.S`/`MSUBF.S`/`NMADDF.S`/`NMSUBF.S` and RH850G3M
`FMAF.S`/`FMSF.S`/`FNMAF.S`/`FNMSF.S` use an integer-p-code fused core.
The product retains its full 48 significant bits; alignment uses guard/sticky
information and there is one final rounding decision. Operands are captured
before writing the destination, including aliased and architectural `r0`
operands.

Authorities are R01US0123EJ0140 Rev.1.40 §§6.1.6–6.1.11 and pp. 402–409,
and R01US0001EJ0100 Rev.1.00 Part 4 §§2.2, 5.3 and pp. 374–389.
The architecture-specific differences are intentional:

- G3M implements RN/RZ/RP/RM, signed-zero flushing, FN flush-to-nearest
  including its quarter-minimum cancellation exception, and mandatory
  unimplemented-operation exceptions for subnormal inputs/results with FS=0.
- V850E2M's legal configuration is RN with FS=1; other RM settings and FS=0
  are prohibited by its manual. Its multiply-add supplements additionally
  detect multiplication overflow before the addition, even when a finite
  addend would otherwise cancel that overflow.
- Enabled exceptions preserve the destination, update XC/FPEPC, and enter
  the precise handler or report a pending imprecise exception. Disabled
  exceptions accumulate XP without replacing the previous enabled cause.
  G3M input-flush state is sticky. FPST/FPCC/FPCFG are views of FPSR.
- Pending FPI uses PSW masking and G3M FPIPR/PMR/ISPR priority, supports
  cancellation through FPEC, and is released through the ordinary LDSR,
  SYNCE, EI, EIRET and FERET paths. ICSR.PMFP reports PMR-masked FPI,
  including priority 16's shared PM15 bit, and clears on cancellation or
  release without changing PMEI. Floating-point instructions other than
  TRFSR do not update their destinations while FPIVD is pending.

**Verified in Ghidra's actual p-code emulator:** 3,922 numerical vectors
against an independent arbitrary-width signed-integer/quotient-remainder
oracle, plus 32 exception/control sequences. Coverage includes deep
cancellation, rounding ties and directed rounding, intermediate overflow,
flush boundaries, infinities, signaling/quiet NaNs, destination aliases,
`r0`, precise/imprecise delivery, register views, priority masking and
interrupt returns.

The NaN class is modeled, but the manuals do not define payload/sign selection:
canonical quiet NaN `0x7fc00000` is a documented model convention.
Imprecise delivery is modeled at instruction boundaries.

## Broader plugin implementation

Architectural profiles are independent of analysis and compiler selection.
The [module README](../../ghidra/ghidra_v850/README.md) lists the language IDs;
[WORKFLOW](../WORKFLOW.md#compiler-and-register-analysis-policy) owns options and
rebuild commands. Exact G3M decoding remains available alongside the broader
profile; a current firmware census does not exclude other family functionality.

- **Register/ABI analysis:** fixed EP/CTBP/GP/TP values are optional settings.
  Callee-save policy for EP/GP/TP/r2 selects
  native compiler-spec variants, so it affects unresolved indirect calls as
  well as direct calls. GHS MULTI is the default compiler; old-GCC and CC-RH
  retain their distinct scalar/aggregate alignment and hidden-return contracts.
- **CALLT:** CTBP values are collected across flowed paths before recovery.
  A call site resolves only when every observation agrees and no path is
  unknown. Initialized table entries produce data/xrefs, executable targets
  produce computed calls and functions, and zero offsets remain valid.
  Writable-memory trust is respected by both custom and generic propagation.
  Ordinary LDSR selectors are decoded separately from FPU selectors: symbolic
  propagation no longer explores an impossible FPU branch that discards a known
  CTBP value. Runtime vectors cover changing, zero, agreeing, conflicting and
  unknown incoming CTBP values.
- **DISPOSE:** the two-operand form falls through; `[lp]` returns; any other target is a computed jump.
  `[sp]` uses SP before frame writeback on G3M/G4MH (R01US0123EJ0140 p. 220;
  R01US0209EJ0220 p. 59) and after writeback on E2M (R01US0001EJ0100 p. 89).
- **Switches:** the analyzer recognizes native, direct-jump, loaded-relative
  and loaded-absolute tables from instruction/dataflow structure. An intervening
  write to the PSW byte containing CY/Z invalidates the range check: in
  `cmp 2,r18; cmp 0,r7; bh default; switch r18`, the branch tests `r7`.
  Bounds and targets are checked before defining a table.
- **Compiler helpers:** stripped GHS/GCC save/restore and arithmetic routines
  are recognized from code structure or compiler-generated byte templates.
  Call-fixups carry stack/register and numerical effects;
  unknown caller-clobbered values remain independent opaque results.
  In matched `___ghssv5*` save helpers, `stsr ctpc,r10` supplies the return
  address for `jmp [r10]`; marking that exit as a return preserves the caller's stack frame.
  Epilogue bytes, including orphan decoded epilogues and conditional local exits,
  do not establish a new helper entry. Existing functions, calls and direct
  unconditional tail jumps from other functions do. This prevents false function
  splits and the resulting no-return/caller truncation.
  The old-GCC aggregate-return analyzer examines the formal return type, avoiding
  an indirect-pointer/aggregate signature oscillation on repeated analysis.
- **Broader architecture:** DSP/SIMD operands and aliasing, FX status/control
  views, indexed MPU descriptors and Host/Guest register transfers have explicit
  p-code dataflow. Fused SIMD and ROUNDF conversion models implement status and
  destination-suppression transitions.
  Scalar and paired `r0` reads supply zero; pair destinations discard the low word
  without changing `r1`'s high-word result. Native execution checks source,
  destination and aliased MAC/FP pairs and MODADD.
- **Trace/debug:** DBPUSH traces a register range rather than changing SP;
  DBCP/DBTAG preserve their event inputs. In broad RH850, the legacy
  DBTRAP/DBRET model uses a synthetic debug bank and toggles its DM bit
  (U14559EJ3V0UM pp. 66–67). E1F uses DBPC/DBPSW for the saved context;
  DBTRAP takes vector `0x60` (PHO3 R01UH0128ED0730 §4.7.2).
- **E1F decode and flow:** the profile accepts the E1 `BSW`/`BSH`/`HSW`
  swaps and excludes E2 search opcodes. Its explicit transfers and saved
  return addresses wrap at 26 bits (PHO3 §3.1.2); implicit Ghidra
  fallthrough uses the flat address space at 64 MiB. E1F `CALLT`/`CTRET`
  save and restore the full PSW (U14559EJ3V1UM pp. 61, 65).
  The original V850 has a 24-bit PC; radare2's `e0` decoder is a legacy
  approximation.

Undocumented legacy private-context/TLB/DSP compound effects remain typed
intrinsics with their known inputs and outputs. They are not aliased to unrelated
G4MH Host/Guest registers or replaced with invented arithmetic. V850E1F has
numeric dataflow and recovered EFG/ECT masks; exact vendor EFG retention,
TRFF flag mapping and exceptional result rules require the unavailable
`U16374EJ1V0UM00` instruction manual. Explicit operations preserve those
boundaries.

Selected verification under `make verify-processor`:

| Fixture | Exercised behavior |
|---|---|
| `AssertProcessorFixtureSemantics` | Core machine cases plus fused numerical and exception/control vectors |
| `AssertV850LanguageProfiles` | Format XIV, short-store operand order, CAXI, ELF selection, DWARF mappings, device volatility and manual prefixes |
| `AssertV850ExtendedIsa` | 156 decode vectors plus executed DSP/SIMD, conversion, pair-alias, burst-memory and debug transitions |
| `AssertV850ExtendedRegisters` | 14 register-access fixtures |
| `AssertV850Virtualization` | Indexed MPU, Host/Guest state and exception transitions |
| `AssertV850E1f` | Legacy decode, debug and PC transitions, and E1F floating-point behavior |
| `AssertV850RegisterAnalysis` | Context options, direct/indirect ABI policy and CTBP flow joins |
| `AssertV850SwitchAnalysis` | All four table idioms, recovered control flow and rejection boundaries |
| `AssertV850CompilerHelpers` | Stripped recognition, numerical decompilation, independent clobbers, escaping stack effects and execution of real save/remainder bodies |

Venza's dynamic CTBP path was checked against instructions and references:
`LDSR r11,CTBP` at `0x17038` installs `0x17060`; CALLT sites
`0x17092`, `0x17096` and `0x1709a` reference the corresponding halfword entries
and trampolines. `LDSR r28,CTBP` at `0x170a6` restores the saved runtime value.
Those table references already existed before this change and are not claimed
as new discoveries. The regenerated `0x17092` pseudocode additionally retains
the FPEC/FPIPR/PMR/ISPR guard and EBASE exception-vector dispatch, with the same
function body. The indirect switch at `0x170b8` remains unresolved.

Residual data-as-code is not hidden by the rebuild comparison. In Crown,
`45 00` at `0x1a4dc` decodes as `switch tp`, not CALLT; the surrounding repeated
halfword table is reached through a data load in `0xc9cea`, and its computed
reference to `0x25212` does not establish a real call. Venza's `0xc974` still
has bad-instruction pseudocode despite shedding decoded table bytes; its
`callt 0x19` at `0xc99a` remains unresolved.

## 2026-10-11 IDA 9.5 processor/decompiler prior-art audit

IDA Professional `9.5.261001.a12ef234` was audited independently at both
layers: the installed arm64 `nec850.dylib` processor module and
`hexv850.dylib` decompiler backend. The MIT-licensed IDA SDK `nec850` source
provides the readable processor implementation. For the build pinned in
[`PROVENANCE.json`](../../ghidra/ghidra_v850/PROVENANCE.json), `nec850` checks
for LP on `DISPOSE` at `0x7d0c`; `hexv850` lowers CTRET to an indirect jump
through CTPC at `0x6210`.

The bundle inventory also contains `rh850.xml` / `rh850-core.xml` debugger
register descriptions, `necv850.cmt` instruction comments, and
`cfg/ghidra_patterns/V850`. No V850 signature library or type library was
present. The debugger XML has no decoder semantics. The shipped Ghidra
function pattern is byte-identical to current upstream Ghidra's file.

The processor-module comparison covered:

- the V850, V850E/E1/E2M, and broad RH850 decoder variants;
- direct and computed flow/xref generation, the CTBP halfword call table, and
  fixed CTBP/GP/TP/EP register options;
- register-value propagation, stack aliases, `PREPARE`, stack stores, and
  GCC/Green Hills save/restore helper thunks;
- four switch families: native `switch`, direct `jmp` tables, and loaded
  relative/absolute target tables;
- the old-GCC and CC-RH argument allocators, including r6-r9, register/stack
  splitting, aggregates, varargs, and r10:r11 returns.

The Hex-Rays backend consumes the processor's saved-register/frame metadata,
link-register and CTPC offsets, and instruction flags. It lowers architectural
system-register accesses and non-C operations to helpers, recognizes named
Green Hills 64-bit arithmetic helpers, and performs its ordinary microcode
optimizations. That explains some IDA quality without revealing a second
instruction decoder: the processor module owns decode, xrefs, stack recovery,
switches, and ABI allocation. In this fork those responsibilities are split
between SLEIGH p-code, the compiler spec, Ghidra analyzers, and the existing
target scripts.

`hexv850.dylib` arm64 addresses for build `9.5.261001.a12ef234`:

| Address | Recovered behavior | Ghidra-side owner |
|---|---|---|
| `0x5658` | Instruction-to-microcode dispatch with CPU-capability checks and a helper-call table | SLEIGH profile selection and instruction p-code |
| `0x1280` | Architectural helper-call generation, including system-register/selector arguments and PSW access | Named system-register dataflow in `v850_special.sinc` |
| `0x555C` → `0x5124` | Prologue-analysis callback and saved-register metadata transfer; the latter records LP/CTPC offsets and flags | Compiler specs, PREPARE/DISPOSE p-code and compiler-helper analysis |
| `0x53A0` / `0x547C` | Serialization/loading of `psi`, `lroff`, `ctpcoff`, `iflags` | No direct file-format equivalent; relevant machine state is modeled in p-code |
| `0x4B5C`, table `0x3F5850` | Name recognition for 44 GHS/COM 64-bit arithmetic-helper entries | Existing `V850CompilerHelperAnalyzer` contracts and call-fixups cover the table |

The prologue callback is at vtable slot `0x3F56D0`; the two preceding slots
are destructors. Decompilation of the saved-register transfer and serializer
establishes the metadata path.

Some backend differences favor retaining the existing Ghidra model: Hex-Rays
uses opaque helpers for saturating arithmetic, clipping and several bit
manipulations for which the fork already emits numerical p-code and flags.
Its compiler/`eabi32` varargs-collector gate at `0x11F94C` does not establish a
`va_list` ABI for these firmware targets. Ghidra compiler specs alone do not
express all IDA variadic-float promotion behavior; no speculative ABI change
was made without a demonstrated consumer.


The vendored function pattern had accidentally shortened only the
`jmp [lp]`-followed `PREPARE ..., simm16/imm16` alternatives to five bytes.
Both instructions are six bytes. The patterns now exactly match installed
IDA's Ghidra-pattern copy and current upstream Ghidra, preventing a
truncated instruction tail from satisfying that function-start pattern.

The clean rebuild also disproved a prior CALLT interpretation rather than
turning it into a processor feature: Sienna `22 02 @ 0x1d5c` and H/F
`22 02 @ 0x1d40` are interior halfwords of four-byte `mulu` instructions, not
instruction boundaries. The [keyless execution assessment](../security/keyless-exec-surface-assessment.md)
details the security consequence. Raw halfword mnemonics and permissive
overlapping-code recovery are not accepted as target evidence.

### Live differential check and indexed-store width correction

An isolated ELF wrapper around the synthetic processor fixture used at that
checkpoint was decoded by installed IDA 9.5 with the RH850 processor selected.
All instruction lengths matched. There were 93 exact mnemonic-prefix matches;
one difference was presentation (`cmovne` versus `cmov nz`), and four were
substantive decode disagreements:

| Bytes | Vendored decode | Installed IDA decode |
|---|---|---|
| `e7 17 76 53` | `st.h r10,[r7]+` | `stc.h r10,[r7]` |
| `e7 27 76 53` | `st.h r10,[r7]-` | `stc.h r10,[r7]` |
| `e7 17 7a 53` | `st.w r10,[r7]+` | `stc.w r10,[r7]` |
| `e7 27 7a 53` | `st.w r10,[r7]-` | `stc.w r10,[r7]` |

The IDA instructions have no post-index operand flags for these four encodings.
The readable SDK explains the result: `ana.cpp` cases `0x376` and `0x37A`
do not discriminate the first halfword's `r2` field, unlike byte-store case
`0x372`. The G3M manual (R01US0123EJ0140 pp. 35–36) describes post-index
addressing, while its load/store entries list only displacement forms.

For post-indexed stores, the fork writes only the access width. Post-indexed
loads with a shared base and destination also update from the original
address; base writeback wins (R01US0209EJ0220, post-indexed `LD` cautions).

With `r10=0x12345678`, zeroed destination memory and no valid load-link,
the actual p-code emulator produced:

| Indexed store, both directions | Four destination bytes |
|---|---|
| `ST.B` | `78 00 00 00` |
| `ST.H` | `78 56 00 00` |
| `ST.W` | `78 56 34 12` |

`AssertProcessorFixtureSemantics` checks these values, neighboring-byte
sentinels, source preservation and address updates for all six store forms
in the G3M and broad RH850 profiles.

### SDK-derived switch recovery gaps

The second comparison found real gaps in the existing analyzer's supported
switch families. IDA's `regfinder.cpp` folds
`MOVHI`; `switch.cpp` accepts immediate/register base additions and both
`MOVEA` and two-operand immediate `ADD` low-case normalization.

`V850SwitchAnalyzer` now follows:

- a `MOVHI` high half composed with a signed `MOVEA` low half;
- immediate `ADD`/`ADDI` table or element bases;
- either operand of a register addition as the proven constant base;
- `add -min, index` normalization, following the index register backward
  even when the dispatch uses a different destination register.

Unknown register writers still terminate constant recovery. Normalization
also stops at an intervening write instead of borrowing an older unrelated
offset. No extra trust policy or target-address special case was added.

New real-analyzer fixtures reproduced missing computed targets, missing
function-body case arms and wrong case labels before the change. The complete
`AssertV850SwitchAnalysis` run passes afterward, including an unknown-base
negative. A separate stripped-binary smoke, with generic decompiler switch
analysis disabled, recovered all three computed edges and decompiled the
MOVHI/MOVEA plus reversed-add dispatch into cases **5, 6 and 7**, returning
**1, 2 and 3**, with default **15**. The temporary smoke inputs/scripts were
removed. Existing checks pinned to warning prose were removed; structural
switch, reference, body and case-value checks remain.

## Remaining implementation gaps

- Zero undefined bytes inside the current functions proves in-body decode
  coverage.
- Some scalar floating-point arithmetic/conversion forms still use Ghidra's
  ordinary primitives without a complete FPSR exception model. Fused and
  ROUNDF status semantics, and the broader SIMD models, do not make the entire
  FPU silicon-exact; documented double-rounding/pipeline limits remain.
  Cache/prefetch userops do not emulate cache contents; load-link invalidation
  by external agents is outside instruction-level emulation.
- Exact function/instruction counts are smoke signals; prefer the asserting
  invariant scripts and the generated semantic coverage ledger for coverage
  floors.

## Historical legacy-Sienna auto-analysis defaults

The recorded legacy-Sienna rebuild (`tools/project/rebuild_project.sh`) ran
Ghidra's default analyzers without disabling "Address Tables" or
"Non-Returning Functions". Observations for that image/checkpoint:

- **Address Tables:** the over-eager-disassembly symptom it warns about *is*
  present — 227 decoded `switch` opcodes are unreachable data misread as code
  (see "Switch jump-table recovery" above). Most arise when the general
  disassembly pass follows word-aligned operands into data.
  Disabling this one analyzer alone would therefore leave them. The real
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
