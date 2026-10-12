# Renesas v850 / RH850 processor module (vendored fork)

Vendored Ghidra processor module for the Renesas V850/RH850 family. Architectural
profiles select the appropriate instruction set; automatic register, switch,
compiler-helper and ABI analysis is not restricted to the repository's firmware.

| Language ID | Architectural profile |
|---|---|
| `v850:LE:32:default` | V850E2M |
| `v850e3:LE:32:default` | RH850G3M; registered P1M-E and Venza core analysis |
| `v850e3x:LE:32:default` | Broad RH850: DSP, SIMD, virtualization, context transfers, trace and debug |
| `v850e1f:LE:32:default` | Legacy V850E1F, including general-register floating-point instructions |

The broad profile does not assign a P1M-E peripheral map to another processor.
Use the registered target's architectural profile for exact-target work and the
broad profile for additional family functionality. Unknown vendor-specific
effects remain explicit typed intrinsics, not invented register or memory effects.

Machine-readable provenance lives in [`PROVENANCE.json`](PROVENANCE.json).
Processor-module audits against this firmware are recorded in
[`docs/tooling/processor-module-audit.md`](../../docs/tooling/processor-module-audit.md).

## How it is built and installed

The compiled `.sla` files are **not** committed (see `.gitignore`); they are
regenerated from the `.slaspec` / `.sinc` sources by `make verify-sleigh` and
by every project rebuild. Prefer the repo Make targets:

```bash
make verify-sleigh      # compile + clean-process language resolution
make verify-processor   # fixtures + project audits
make rebuild-project    # selected target's staged rebuild into its build/work/ path
```

`tools/project/install_v850_extension.sh` copies the module to
`build/cache/processor-extension-src/`, compiles each `*.slaspec` there with Ghidra's
`sleigh` compiler, and installs the result into an isolated user home. It never
generates `.sla` files in this directory or mutates Ghidra's installation tree.
A conflicting install-tree copy is reported for explicit user removal. No
manual install step is otherwise required.

## Original upstream basis (for reference)

1. V850E2 version based on **User's Manual: V850E2M Architecture**
   ([link](https://www.renesas.com/us/en/doc/products/mpumcu/doc/v850/r01us0001ej0100_v850e2m.pdf))
2. V850E3 version based on gcc `objdump` and `gdb` sources, CubeSuite IDE
   [manual](https://www.renesas.com/sg/en/doc/products/tool/doc/003/r20ut2584ej0101_qscdrh850.pdf)
   and **RH850G3KH User's Manual: Software**
   ([link](https://www.renesas.com/us/en/document/mas/rh850g3kh-users-manual-software),
   R01US0165EJ0120).

> **Core identity (G3M, not G3KH).** The R7F701381 target core is **RH850G3M**:
> the P1M-E datasheet (R01DS0505ED0100) states the device "contains two
> RH850G3Ms" in a lockstep master/checker arrangement, and the `.sinc` sources
> cite the G3M software manual as the authoritative ISA reference. The G3KH
> manual above is the upstream's original comparative reference, retained for
> history — it is not the target's core.

## Local modifications

Implementation owners:

- `data/languages/v850_ghs.cspec`, `v850_gcc.cspec`, `v850_ccrh.cspec` — GHS MULTI
  (default), old-GCC and CC-RH calling conventions; native callee-save policy
  variants are generated during installation.
- `data/languages/v850.pspec` — processor volatility (P1M-E peripheral windows).
- `data/languages/v850e3.sinc` — RH850G3M instructions, atomics, named
  `CACHE`/`PREF` operations, and system-register maps.
- `data/languages/v850_load_store.sinc` / `v850_arithmetic.sinc` — verified
  load/store, divide, and saturating-arithmetic p-code semantics.
- `data/languages/v850_float.sinc` — floating-point mnemonics, operand order,
  conversion dataflow, and V850E2M-only four-register multiply-add forms.
- `data/languages/v850_fused.sinc` — integer binary32 fused multiply-add,
  single rounding, special values, and architecture-specific flush behavior.
- `data/languages/v850_special.sinc` — shared FPU register views, exception
  entry, pending-exception cancellation, and interrupt-mask/return handling.
- `data/languages/v850_ext.sinc`, `v850_dsp.sinc`, `v850_simd.sinc`,
  `v850_virtual.sinc`, `v850_e1f.sinc` — broader architectural families,
  including FXU/MPU register views, Host/Guest transitions and legacy debug state.
- `src/main/java/.../analysis/` — configurable register context and CALLT
  dataflow, four switch idioms, stripped compiler-helper recognition, and
  GCC aggregate-return analysis. Configuration and rebuild commands belong in
  [WORKFLOW](../../docs/WORKFLOW.md); evidence and limitations in the
  [processor audit](../../docs/tooling/processor-module-audit.md).
- `data/languages/v850.dwarf` — GCC DWARF register mapping.
- `data/patterns/` — Ghidra function-start patterns for PREPARE/ADDI prologues
  following architectural returns.
- Language versions `0.8` (V850E2M), `0.9` (RH850G3M), `1.1` (broad RH850)
  and `1.0` (V850E1F), with extension metadata pinned to Ghidra `12.1.4`.
  `MADDF`/`MSUBF`/`NMADDF`/`NMSUBF` use the V850E2M architectural contract;
  G3M has its separate fused forms.
  `CACHE`/`PREF` use the G3M manual's named operations (Table 7-7/7-8).

The four V850E2M multiply-add forms and four G3M fused forms execute through
integer p-code, not separately rounded `FLOAT_MULT`/`FLOAT_ADD` operations.
G3M supports all four rounding modes and flush-to-nearest; V850E2M's legal
settings require nearest-even rounding and subnormal flushing. The E2M
manual additionally requires multiplication-overflow detection before the
fused addition. Enabled exceptions suppress the destination and update the
architectural FPU state; pending imprecise exceptions invalidate subsequent
floating-point instructions.

These are instruction-boundary semantics, not FPU pipeline timing. The manuals
do not specify a NaN payload/sign selection rule; the model emits canonical
quiet NaN `0x7fc00000`, not a silicon-specific payload. Some remaining scalar
arithmetic/conversion forms still use Ghidra's ordinary floating primitives.
The broader SIMD and ROUNDF status models do not establish pipeline timing or
silicon-exact behavior for every floating-point corner; see the processor audit.
