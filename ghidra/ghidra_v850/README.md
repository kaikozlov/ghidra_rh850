# Renesas v850 / RH850 processor module (vendored fork)

This is a Ghidra processor module for the Renesas v850/RH850 family. It is
the source of truth for the `v850e3:LE:32:default` language used by this repo's
RH850/P1M-E analysis.

It has diverged from upstream and is edited freely to serve this project's
firmware analysis. There is no intent to keep patches upstreamable; exact
RH850G3M/P1M-E behavior takes priority. The Venza target reuses the core
instruction decoder, but its exact RH850 subtype and peripheral map remain
unestablished and do not inherit P1M-E system-register or SFR claims.

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
make rebuild-project    # full annotated rebuild into build/work/project/
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

See the git history of this repo for the changes made on top of the fork
point. Notable areas under active modification for the P1M-E target:

- `data/languages/v850.cspec` — RH850/G3 calling-convention model.
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
- `data/languages/v850.dwarf` — GCC DWARF register mapping.
- `data/patterns/` — Ghidra function-start patterns for PREPARE/ADDI prologues
  following architectural returns.
- Language versions `0.7` (V850E2M and RH850G3M), with extension metadata
  pinned to Ghidra `12.1.4` (see `PROVENANCE.json`). `MADDF`/`MSUBF`/`NMADDF`/
  `NMSUBF` remain supported in V850E2M, gated out of the G3M language.
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
quiet NaN `0x7fc00000`, not a silicon-specific payload. Other floating-point
arithmetic/conversion instructions still use Ghidra's ordinary floating
primitives and do not gain a complete exception model from this change.
