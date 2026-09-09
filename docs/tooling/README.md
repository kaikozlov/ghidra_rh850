# Tooling

The analysis toolchain: processor module, scripts, verification.

| Report | Scope |
|---|---|
| [processor-module-audit.md](processor-module-audit.md) | Audit of the vendored `ghidra_v850` processor module: SLEIGH semantics, semantic coverage ledger, calling-convention model |
| [renesas-rfp-rv40f.md](renesas-rfp-rv40f.md) | External-source recovery of the Renesas Flash Programmer RV40F serial protocol and its bounded ICU-S configuration interface |
| [techstream.md](techstream.md) | External-source recovery of Toyota Techstream V18.00.003 (installer 18.00.008): J2534 diagnostic architecture, SecurityAccess implementations, CUW reflash flow, and the ptshim32 CAN traffic logger |
| [techstream-capture-procedure.md](techstream-capture-procedure.md) | Isolated-bench capture, hashing, normalization, redaction, and evidence labeling for official J2534 traces |
| [techstream-ddb-pipeline.md](techstream-ddb-pipeline.md) | `.ddb` binary format reverse-engineering: LZSS decompression, section parsing, OEM string resolution, and the generated diagnostic catalog pipeline |
| [gts-query-cli.md](gts-query-cli.md) | `tools/gts`: unified read-only discovery across current GTS+ DDB semantics, CUW descriptors/writer routes, and DLL/EXE metadata/strings |
| [gtsplus-tss3-fleet-map.md](gtsplus-tss3-fleet-map.md) | Current-GTS+ cross-vehicle TSS3 architecture/topology census: per-region category-498 install-set architectures, v18 ECU_Setting diagnostic addresses, and CAN Bus Check gateway topology (Toyota bus identity, explicitly not panda buses) |
| [pcs-data-viewer-tss3-dictionary.md](pcs-data-viewer-tss3-dictionary.md) | PCS Data Viewer TSS3 Operation/Image FFD dictionary: 1,131 recorder fields, trigger names, control/arbitration semantics, and the AB/EB recorder-model join |
| [gtsplus-tse-gtse-saved-session.md](gtsplus-tse-gtse-saved-session.md) | GTS+ TSE/GTSE saved-session grammar: FAT/sections, ring-buffer signal metadata, PCS Operation/Image FFD persistence, and converter skip boundary |
| [gtsplus-p5-adas-p6-migration.md](gtsplus-p5-adas-p6-migration.md) | Cross-generation ADAS semantic map from distributed P5 PCS/radar/lane databases into generation-22 ADCU_P6, including recorder and diagnostic-role continuity |
| [community-dataflash-secoc.md](community-dataflash-secoc.md) | Static audit of the pinned community DataFlash/SecOC extractor, its Sienna-specific bus/ID assumptions, and the repository-local generic Toyota classic-SecOC oracle |
| [community-patch-target-analysis.md](community-patch-target-analysis.md) | Fail-closed raw/Ghidra workflow for classifying the blurbdust/yc persistent patch target on future F3/F4 firmware |
| [secoc-semantic-patch-resolver.md](secoc-semantic-patch-resolver.md) | Calibration-independent host-side resolver for the SecOC authenticated-delivery branch plus dynamic boot-CRC geometry and patch-manifest generation |
| [exploit-predicate-semantics.md](exploit-predicate-semantics.md) | Cross-workstream firmware audit of exploit-critical result/status polarity, branch direction, and opposite-direction regression coverage |
| [panda-toyota-routing.md](panda-toyota-routing.md) | Static Panda ELM327/harness routing model and non-destructive Toyota EPS bus-discovery helper |
| [exploit-interest-ranking.md](exploit-interest-ranking.md) | Whole-image exploit-interest ranking pipeline: ingress/pre-SA distance, attacker-controlled-selection proxies, sink families, anchored cohorts |
| [rh850-codeflash-structure-scanner.md](rh850-codeflash-structure-scanner.md) | Offline cross-calibration structural fingerprint scanner (boot-CRC geometry, RAM-exec/MEM-SAFE-001 anchors, XCP 0x7F7/0x7F8 route constants) for triage of future P1M-E images |
| [variant-acquisition-readiness.md](variant-acquisition-readiness.md) | One-command offline evidence-chain check binding an acquired CodeFlash image to geometry/SHA/run-record provenance, structural triage summary, and semantic-resolver readiness |
| [annotation-ledger.md](annotation-ledger.md) | Declarative, fully preflighted replay of simple persistent Ghidra function names, data labels, and listing comments |
| [toyota-dataflash-analysis.md](toyota-dataflash-analysis.md) | Offline all-window DataFlash analyzer: physical NvM validity, raw/XOR55/XORAA consensus, object-15 geometry, and independent SecOC key-domain classification |

## Operating manual

For the day-to-day Ghidra workflow (durability trap, working copy vs.
committed snapshot, rebuild procedure), see [../WORKFLOW.md](../WORKFLOW.md).

## Task-oriented entry points

Prefer a task-oriented entry point when several analyses share the same
mechanics. Do not add another one-file wrapper merely to bake in a different
address list.

The small command surface to remember is:

| Task | Entry point |
|---|---|
| Edit-loop tests | `tools/test` |
| Discover / preview | `tools/test list [word]`, `tools/test plan` |
| Ghidra / pseudocode | `tools/g`, `tools/pseudo` |
| GTS+ / Toyota vocabulary / CUW routes | `tools/gts` |
| Toyota platform capabilities / target workflows | `tools/toyota capabilities`, `tools/toyota target list camry` |
| Repository knowledge / findings / corrections / open questions | `tools/know QUERY` |
| Generated artifacts / producers | `tools/artifact list`, `show`, `regen` |
| Broad gates | `tools/test core` / `full` / `local` |
| Discover/query configured targets | `tools/gtarget list`, `tools/gtarget show TARGET`, `tools/gtarget TARGET ...` |
| Discover Corolla target workflows | `tools/toyota target list corolla` |
| Discover cross-variant evidence modes | `tools/toyota variant list` |
| Discover working-project export profiles | `tools/project/export_ghidra_project.sh list` |

Generated artifacts are discoverable without remembering their implementation filenames:

```bash
tools/artifact list camry
tools/artifact show camry_8965F3307000_fault_status.json
tools/artifact regen camry_8965F3307000_fault_status.json
```

The catalog is derived from tracked artifact paths and source references; it is not another manually maintained builder registry. `regen` exposes the selected producer before execution and requires an explicit `--producer` when discovery is ambiguous.

Repository memory has the same task-shaped surface:

```bash
tools/know COM-017
tools/know "Target Lateral ID" --kind finding --kind open
tools/know fault_status --kind artifact --kind suite
tools/know TMS-060 --json
```

`tools/know` reads the authoritative findings/corrections/open-question ledgers, the derived artifact catalog, `verification.toml`, and tracked docs directly. It is navigation, not an evidence oracle: use the returned canonical report/test to continue, and return to firmware/Ghidra for primary proof.

Configured firmware targets likewise have one registry-backed discovery surface:

```bash
tools/gtarget list
tools/gtarget show camry-8965F3307000
tools/gtarget camry-8965F3307000 stats
```

Generic rebuild/snapshot tooling resolves target-specific seed tables and Ghidra stage scripts from `data/analysis_targets.json`; adding a target must not require editing the generic shell scripts.

Family modules (`tests/verify_application_wdbi.py`, `tests/verify_corolla_h.py`,
and so on) group related proofs. Exact F33 proofs use
`tests/verify_camry_8965F3307000.py` with per-suite `--section` dispatch. Tests
are selected explicitly; Git changes do not route into suites. Prefix discovery
remains available with `tools/test list application` / `corolla` /
`camry_8965f3307000` / `techstream`. Generated-artifact producer discovery is
handled directly by `tools/artifact` and is independent of verification suites.

The repeated Corolla-H corpus-compaction scripts are consolidated behind one
profile-driven command:

```bash
tools/toyota target run corolla extract/h-evidence list
tools/toyota target run corolla extract/h-evidence extract can-com
tools/toyota target run corolla extract/h-evidence extract xcp
```

`list` is the discovery surface: it reports each profile's purpose, tracked
output, input corpora, and function count. The profiles cover only the common
operation of selecting known target-native functions from disposable JSONL
corpora and binding their decompilation to CodeFlash bytes. Extractors that do
dynamic discovery, whole-corpus censuses, call-graph construction, or semantic
joins remain separate tools because those are different operations, not
variants of the same one.

Likewise, the `build_corolla_h_*` programs remain separate semantic builders.
Their envelopes look similar, but the proof logic they encode (routing tables,
selector policies, supervisor alignment, diagnostic joins, and so on) is
subsystem-specific. Consolidation should expose shared mechanics without hiding
those distinctions.

Cross-variant image-bound evidence extraction uses one subcommand runner:

```bash
tools/toyota variant list
tools/toyota variant structural --image ... --fingerprints ... \
  --software-id 8965H1202000 --address 0xCEDAE ... --out data/generated/...json
tools/toyota variant function --image ... --corpus ... \
  --software-id 8965H1202000 --address 0xB6 ... --out data/generated/...json
tools/toyota variant application-diagnostics --image ... \
  --corpus ... --did-table 0x... --did-count 180 --routine-callback-table 0x... \
  --software-id 8965H1202000 --out data/generated/...json
tools/toyota variant reference-census --image ... \
  --corpus ... --software-id 8965H1202000 --term B6=... --out data/generated/...json
```

The four modes share exactly one abstraction — select function records from a
disposable JSONL corpus and bind them to raw CodeFlash bytes with SHA-256 — and
differ only in selection strategy (explicit addresses, image-resolved callback
tables, or whole-corpus substring census). Unlike the Corolla-H profile runner,
these stay argument-driven rather than profile-driven because each invocation
names its own image, corpus, and output path: the same mode serves both the
Sienna and Corolla calibrations, so baking per-artifact profiles here would just
duplicate the generated-artifacts table.

## Internal implementation boundaries

The public surface is consolidated even when the underlying proof logic is not.
A target-specific extractor or builder may remain a separate implementation when
it genuinely encodes a different analysis, but it lives under the target/domain
namespace and is discoverable through `tools/toyota target list ...` or
`tools/artifact`. Do not promote those implementation filenames back into the
root command surface.

The same rule applies to Techstream: parsers/extractors remain separate where
the formats or evidence boundaries differ, while `tools/gts` / `tools/toyota gts`
is the capability surface. Shared parsing, routing, crypto, or container mechanics
belong in reusable modules and should be consumed by every implementation that
needs them.

Resolver and live-experiment code can keep distinct fail-closed contracts when
those contracts are materially different. Consolidation means one place to
*discover and invoke* what we know how to do, plus shared mechanics underneath;
it does not mean forcing unrelated analyses through one giant function.

## Vendored processor module

The RH850 language `v850e3:LE:32:default` is the **vendored in-tree fork** at
`ghidra/ghidra_v850/` (forked from `esaulenka/ghidra_v850` at commit
`14c1b5be32b8ec741ee626c8bca9885c58f7a473`; see
`ghidra/ghidra_v850/PROVENANCE.json`). Install path and fingerprint checks are
in [../WORKFLOW.md](../WORKFLOW.md).

- [Ephemeral runtime semantic resolver](ephemeral-runtime-semantic-resolver.md) — fresh-image fail-closed resolver and SHA-bound target manifest for the RAM scheduler/SecOC-COM bridge.
