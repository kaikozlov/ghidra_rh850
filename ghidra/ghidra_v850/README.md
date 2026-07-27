# Renesas v850 / RH850 processor module (vendored fork)

This is a Ghidra processor module for the Renesas v850/RH850 family. It is
the source of truth for the `v850e3:LE:32:default` language used by this repo's
RH850/P1M-E analysis.

It has diverged from upstream and is edited freely to serve this project's
firmware analysis. There is no intent to keep patches upstreamable; correctness
for the RH850/P1M-E (`R7F701381`) target takes priority.

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
make rebuild-project    # full annotated rebuild into build/project/
```

`tools/install_v850_extension.sh` copies the module to
`build/processor-extension-src/`, compiles each `*.slaspec` there with Ghidra's
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

## Local modifications

See the git history of this repo for the changes made on top of the fork
point. Notable areas under active modification for the P1M-E target:

- `data/languages/v850.cspec` — RH850/G3 calling-convention model.
- `data/languages/v850.pspec` — processor volatility (P1M-E peripheral windows).
- `data/languages/v850e3.sinc` — RH850 instructions and system-register maps.
- `data/languages/v850_load_store.sinc` / `v850_arithmetic.sinc` — verified
  load/store and arithmetic p-code semantics (`sld.b`/`sld.h` sext, signed
  `divh`, saturating `PSW.SAT`/`OV`).
- `data/languages/v850_float.sinc` — `ceilf.suw` constructor correction.
- Language version `0.2` / extension metadata `12.1.2` (see `PROVENANCE.json`).
