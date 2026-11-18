# Renesas v850 / RH850 processor module (vendored fork)

Use the language ID from `tools/gtarget show TARGET` when importing a registered
raw image. The three G3M languages share a decoder and have different CPU I/O
volatility maps.

| Language ID | Architectural profile |
|---|---|
| `v850:LE:32:default` | V850E2M |
| `v850e3:LE:32:default` | RH850G3M, P1M-E EPS devices |
| `v850e3:LE:32:P1xC` | RH850G3M, P1x-C main CPU (Venza) |
| `v850e3:LE:32:D1LD1M` | RH850G3M, D1L/D1M-compatible combination meter |
| `v850e3x:LE:32:default` | Broad RH850: DSP, SIMD, virtualization, context transfers, trace and debug |
| `v850e1f:LE:32:default` | Legacy V850E1F, including general-register floating-point instructions |

The [processor audit](../../docs/tooling/processor-module-audit.md) owns
instruction semantics, device evidence and known limits. [PROVENANCE.json](PROVENANCE.json)
records the upstream fork, comparison revisions and Renesas manual editions.

## How it is built and installed

Build from the repository root with Ghidra 12.2 and JDK 25:

```bash
make verify-sleigh      # compile + clean-process language resolution
make verify-processor   # fixtures + project audits
make rebuild-project    # selected target's staged rebuild into its build/work/ path
```

`make verify-processor` checks the committed instruction fixture without
rewriting it. After editing its generator, run `make generate-processor-fixture`.

The installer compiles `data/languages/*.slaspec` in `build/cache/` and installs
the extension into the isolated Ghidra user home. G3M and E2M instruction help
uses `data/manuals/*.idx` and the matching PDFs when available under `REFERENCE/`.

Select GHS MULTI (default), old-GCC or CC-RH on import. Compiler and analyzer
options are documented in [WORKFLOW](../../docs/WORKFLOW.md#compiler-and-register-analysis-policy).
