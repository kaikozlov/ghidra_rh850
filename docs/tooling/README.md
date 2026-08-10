# Tooling

The analysis toolchain: processor module, scripts, verification.

| Report | Scope |
|---|---|
| [processor-module-audit.md](processor-module-audit.md) | Audit of the vendored `ghidra_v850` processor module: SLEIGH semantics, semantic coverage ledger, calling-convention model |
| [renesas-rfp-rv40f.md](renesas-rfp-rv40f.md) | External-source recovery of the Renesas Flash Programmer RV40F serial protocol and its bounded ICU-S configuration interface |
| [techstream.md](techstream.md) | External-source recovery of Toyota Techstream V18.00.003 (installer 18.00.008): J2534 diagnostic architecture, SecurityAccess implementations, CUW reflash flow, and the ptshim32 CAN traffic logger |
| [techstream-ddb-pipeline.md](techstream-ddb-pipeline.md) | `.ddb` binary format reverse-engineering: LZSS decompression, section parsing, OEM string resolution, and the generated diagnostic catalog pipeline |
| [community-dataflash-secoc.md](community-dataflash-secoc.md) | Static audit of the pinned community DataFlash/SecOC extractor, its Sienna-specific bus/ID assumptions, and the repository-local generic Toyota classic-SecOC oracle |
| [community-patch-target-analysis.md](community-patch-target-analysis.md) | Fail-closed raw/Ghidra workflow for classifying the blurbdust/yc persistent patch target on future F3/F4 firmware |
| [panda-toyota-routing.md](panda-toyota-routing.md) | Static Panda ELM327/harness routing model and non-destructive Toyota EPS bus-discovery helper |

## Operating manual

For the day-to-day Ghidra workflow (durability trap, working copy vs.
committed snapshot, rebuild procedure), see [../WORKFLOW.md](../WORKFLOW.md).

## Vendored processor module

The RH850 language `v850e3:LE:32:default` is the **vendored in-tree fork** at
`ghidra/ghidra_v850/` (forked from `esaulenka/ghidra_v850` at commit
`14c1b5be32b8ec741ee626c8bca9885c58f7a473`; see
`ghidra/ghidra_v850/PROVENANCE.json`). Install path and fingerprint checks are
in [../WORKFLOW.md](../WORKFLOW.md).
