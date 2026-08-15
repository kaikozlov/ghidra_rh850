# Tooling

The analysis toolchain: processor module, scripts, verification.

| Report | Scope |
|---|---|
| [processor-module-audit.md](processor-module-audit.md) | Audit of the vendored `ghidra_v850` processor module: SLEIGH semantics, semantic coverage ledger, calling-convention model |
| [renesas-rfp-rv40f.md](renesas-rfp-rv40f.md) | External-source recovery of the Renesas Flash Programmer RV40F serial protocol and its bounded ICU-S configuration interface |
| [techstream.md](techstream.md) | External-source recovery of Toyota Techstream V18.00.003 (installer 18.00.008): J2534 diagnostic architecture, SecurityAccess implementations, CUW reflash flow, and the ptshim32 CAN traffic logger |
| [techstream-capture-procedure.md](techstream-capture-procedure.md) | Isolated-bench capture, hashing, normalization, redaction, and evidence labeling for official J2534 traces |
| [techstream-ddb-pipeline.md](techstream-ddb-pipeline.md) | `.ddb` binary format reverse-engineering: LZSS decompression, section parsing, OEM string resolution, and the generated diagnostic catalog pipeline |
| [community-dataflash-secoc.md](community-dataflash-secoc.md) | Static audit of the pinned community DataFlash/SecOC extractor, its Sienna-specific bus/ID assumptions, and the repository-local generic Toyota classic-SecOC oracle |
| [community-patch-target-analysis.md](community-patch-target-analysis.md) | Fail-closed raw/Ghidra workflow for classifying the blurbdust/yc persistent patch target on future F3/F4 firmware |
| [secoc-semantic-patch-resolver.md](secoc-semantic-patch-resolver.md) | Calibration-independent host-side resolver for the SecOC authenticated-delivery branch plus dynamic boot-CRC geometry and patch-manifest generation |
| [panda-toyota-routing.md](panda-toyota-routing.md) | Static Panda ELM327/harness routing model and non-destructive Toyota EPS bus-discovery helper |
| [exploit-interest-ranking.md](exploit-interest-ranking.md) | Whole-image exploit-interest ranking pipeline: ingress/pre-SA distance, attacker-controlled-selection proxies, sink families, anchored cohorts |
| [rh850-codeflash-structure-scanner.md](rh850-codeflash-structure-scanner.md) | Offline cross-calibration structural fingerprint scanner (boot-CRC geometry, RAM-exec/MEM-SAFE-001 anchors, XCP 0x7F7/0x7F8 route constants) for triage of future P1M-E images |
| [variant-acquisition-readiness.md](variant-acquisition-readiness.md) | One-command offline evidence-chain check binding an acquired CodeFlash image to geometry/SHA/run-record provenance, structural triage summary, and semantic-resolver readiness |
| [toyota-dataflash-analysis.md](toyota-dataflash-analysis.md) | Offline all-window DataFlash analyzer: physical NvM validity, raw/XOR55/XORAA consensus, object-15 geometry, and independent SecOC key-domain classification |

## Operating manual

For the day-to-day Ghidra workflow (durability trap, working copy vs.
committed snapshot, rebuild procedure), see [../WORKFLOW.md](../WORKFLOW.md).

## Vendored processor module

The RH850 language `v850e3:LE:32:default` is the **vendored in-tree fork** at
`ghidra/ghidra_v850/` (forked from `esaulenka/ghidra_v850` at commit
`14c1b5be32b8ec741ee626c8bca9885c58f7a473`; see
`ghidra/ghidra_v850/PROVENANCE.json`). Install path and fingerprint checks are
in [../WORKFLOW.md](../WORKFLOW.md).
