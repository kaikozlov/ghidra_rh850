# Tooling

The analysis toolchain: processor module, scripts, verification.

| Report | Scope |
|---|---|
| [processor-module-audit.md](processor-module-audit.md) | Audit of the vendored `ghidra_v850` processor module: SLEIGH semantics, semantic coverage ledger, calling-convention model |
| [rh850-build-and-sim.md](rh850-build-and-sim.md) | Unified `tools/rh850` workflow for the pinned toolchain, payload tests, CodeFlash tests, exact-firmware scenarios, and generated P1M-E model |
| [renesas-rfp-rv40f.md](renesas-rfp-rv40f.md) | External-source recovery of the Renesas Flash Programmer RV40F serial protocol and its bounded ICU-S configuration interface |
| [techstream.md](techstream.md) | External-source recovery of Toyota Techstream V18.00.003 (installer 18.00.008): J2534 diagnostic architecture, SecurityAccess implementations, CUW reflash flow, and the ptshim32 CAN traffic logger |
| [cuw-t0087-17.md](cuw-t0087-17.md) | T0087-17 CUW package analysis and decoded payload evidence |
| [cuw-t0011-21-04c21.md](cuw-t0011-21-04c21.md) | T0011-21 / 04C21 VFOREST CUW package analysis |
| [cuw-tacoma-vforest-corpus.md](cuw-tacoma-vforest-corpus.md) | Comparative analysis of the Tacoma VFOREST CUW corpus |
| [techstream-capture-procedure.md](techstream-capture-procedure.md) | Isolated-bench capture, hashing, normalization, redaction, and evidence labeling for official J2534 traces |
| [techstream-ddb-pipeline.md](techstream-ddb-pipeline.md) | `.ddb` binary format reverse-engineering: LZSS decompression, section parsing, OEM string resolution, and the generated diagnostic catalog pipeline |
| [gts-query-cli.md](gts-query-cli.md) | `tools/gts`: unified read-only discovery across current GTS+ DDB semantics, CUW descriptors/writer routes, and DLL/EXE metadata/strings |
| [gtsplus-body-recovery.md](gtsplus-body-recovery.md) | Offline recovery of the current CP-protected GTS+ executable bodies into clean analysis PEs |
| [cuwplus-body-recovery.md](cuwplus-body-recovery.md) | Offline reconstruction of the CP-protected CUWPlus/GTS+ auxiliary corpus (stub + sidecar pairs) in a constrained emulator |
| [gtsplus-tss3-fleet-map.md](gtsplus-tss3-fleet-map.md) | Current-GTS+ cross-vehicle TSS3 architecture/topology census: per-region category-498 install-set architectures, v18 ECU_Setting diagnostic addresses, and CAN Bus Check gateway topology (Toyota bus identity, explicitly not panda buses) |
| [pcs-data-viewer-tss3-dictionary.md](pcs-data-viewer-tss3-dictionary.md) | PCS Data Viewer TSS3 Operation/Image FFD dictionary: 1,131 recorder fields, trigger names, control/arbitration semantics, and the AB/EB recorder-model join |
| [gtsplus-vdas-pcs-data.md](gtsplus-vdas-pcs-data.md) | GTS+ PCS Vehicle Data Analysis `.vdas` persistence: TSS3 FFD model fields and the recovered managed-body container contract |
| [gtsplus-tse-gtse-saved-session.md](gtsplus-tse-gtse-saved-session.md) | GTS+ TSE/GTSE saved-session grammar: FAT/sections, ring-buffer signal metadata, PCS Operation/Image FFD persistence, and converter skip boundary |
| [gtsplus-p5-adas-p6-migration.md](gtsplus-p5-adas-p6-migration.md) | Cross-generation ADAS semantic map from distributed P5 PCS/radar/lane databases into generation-22 ADCU_P6, including recorder and diagnostic-role continuity |
| [community-dataflash-secoc.md](community-dataflash-secoc.md) | Static audit of the pinned community DataFlash/SecOC extractor, its Sienna-specific bus/ID assumptions, and the repository-local generic Toyota classic-SecOC oracle |
| [community-patch-target-analysis.md](community-patch-target-analysis.md) | Fail-closed raw/Ghidra workflow for classifying the blurbdust/yc persistent patch target on future F3/F4 firmware |
| [secoc-semantic-patch-resolver.md](secoc-semantic-patch-resolver.md) | Calibration-independent host-side resolver for the SecOC authenticated-delivery branch plus dynamic boot-CRC geometry and patch-manifest generation |
| [ephemeral-runtime-semantic-resolver.md](ephemeral-runtime-semantic-resolver.md) | Fresh-image fail-closed resolver and SHA-bound target manifest for the RAM scheduler/SecOC-COM bridge, avoiding inherited Sienna offsets |
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
| Edit-loop tests | `tools/test <suite-or-prefix>` — run the smallest relevant suite |
| Discover / preview | `tools/test list [query]`, `tools/test plan <selector> [...]` |
| Ghidra / pseudocode | `tools/g`, `tools/pseudo` |
| Read memory / disassemble instructions | `tools/g memory read ADDR 0x20`, `tools/g disasm ADDR -n 16` (`--count` alone reports a count) |
| Linear listing of a whole registered CodeFlash image | `tools/rh850 toolchain listing TARGET` — prints a cached objdump file path; use Ghidra for function boundaries |
| Run P1M-E firmware scenarios or select an engine | `tools/rh850 test firmware TARGET SCENARIO…` — [P-code execution engines](rh850-build-and-sim.md#p-code-execution-engines) |
| Search a reference PDF | `rg -n 'pattern' "$(tools/manual-text MANUAL.pdf)"` — reuses layout-preserving text with page breaks |
| GTS+ / Toyota vocabulary / CUW routes | `tools/gts` |
| Toyota platform capabilities / target workflows | `tools/toyota capabilities`, `tools/toyota target list camry` |
| Offline rlog events and schema fields | `tools/toyota route inspect RLOG --openpilot-root CHECKOUT` |
| Maintained reports, artifacts, and verification suites | `tools/know QUERY` |
| Generated artifacts / producers | `tools/artifact list`, `show`, `regen` |
| Broad gates | `tools/test core` / `full` / `local` |
| Discover/query configured targets | `tools/gtarget list`, `tools/gtarget show TARGET`, `tools/gtarget TARGET ...` |
| Discover Corolla target workflows | `tools/toyota target list corolla` |
| Camry reconstruction | `tools/toyota decomp --help` |
| Camry F33 DCM UDS reference comparison | [Gallia replay command and conformance matrix](../security/fuzz-oracle-methodology.md#gallia-reference-comparison) |
| Camry F33 nonvolatile reset lifecycle | `tools/test camry_f33_nvm_lifecycle` |
| Locate reconstructed Camry C | `tools/toyota decomp source QUERY [QUERY ...]` — exact names, entries, or interior PCs; [source ownership](../../decomp/camry-8965F3307000/README.md#source-and-evidence-ownership) |
| Discover cross-variant evidence modes | `tools/toyota variant list` |
| Discover working-project export profiles | `tools/project/export_ghidra_project.sh list` |

Generated artifacts are discoverable without remembering their implementation filenames:

```bash
tools/artifact list camry
tools/artifact show camry_8965F3307000_fault_status.json
tools/artifact regen camry_8965F3307000_fault_status.json
```

`regen --dry-run` previews the selected invocation. Only declared outputs and registered corpora can be regenerated; `--producer` chooses among declared owners. References from other tools appear as consumers.

Repository memory has the same task-shaped surface:

```bash
tools/know "CAN receive"
tools/know "Target Lateral ID" --kind doc
tools/know fault_status --kind artifact --kind suite
tools/know "Panda routing" --json
```

`tools/know` searches maintained reports first, then the derived artifact catalog and `verification.toml`. Follow the returned report or test to its evidence.

Configured firmware targets likewise have one registry-backed discovery surface:

```bash
tools/gtarget list
tools/gtarget show camry-8965F3307000
tools/gtarget camry-8965F3307000 stats
tools/gtarget show corolla-8965H1202000
tools/gtarget show corolla-8965F1208000
```

Generic rebuild/snapshot tooling resolves target-specific seed tables and Ghidra stage scripts from `data/analysis_targets.json`; adding a target must not require editing the generic shell scripts.

Tests are grouped under `tests/tooling/`, `tests/techstream/`, `tests/toyota/`,
`tests/diagnostics/`, `tests/firmware/`, `tests/targets/`, `tests/variants/`,
and `tests/runtime/`. Larger target suites
are split by behavioral domain; `verification.toml` retains their public suite
names and maps them to the relevant scripts. Use `tools/test list application`,
`corolla`, `camry_8965f3307000`, or `techstream` for discovery. Git changes do not
select suites. Artifact producer discovery remains the separate `tools/artifact`
command.

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
joins remain separate tools because each performs a distinct operation.

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
namespace and is discoverable through `tools/toyota capabilities`,
`tools/toyota target list ...`, or `tools/artifact`. Do not promote implementation filenames into the
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

## Tool support and limits

### Request-byte dataflow

Reconstructed C and exact disassembly identified all 18 decision groups and 10
sink groups in the F33 SecurityAccess, WriteDataByIdentifier, and RoutineControl
handlers. Ghidra 12.2 `TaintPlugin` requires an external CTADL engine, and its
source exporter fails without a UI tool. angr 10.0.7 with pypcode 4.0.1 lifted
the handler entries with the vendored SLEIGH language, but its symbolic runs
stopped on temporary-width or statement-offset errors. Neither produced a
service map. The KARONTE keyword-propagation candidate was not runnable.

### Machine ingress coverage

Two bounded F33 runs exercised firmware transport, DCM receive-buffer, and timer
writes. The flood and forced-edge cases covered 820 and 819 edges, respectively,
without a typed fault, uninitialized read, or object-boundary crossing. Neither
run reached the application handlers under test. The forced-edge policy did not
activate because execution did not enter its target routine. The respective
stack watermarks were 748 and 652 bytes. An unmodeled SP write prevents either
figure from establishing a maximum.
See the [typed-event P1M-E campaign](../security/fuzz-oracle-methodology.md#typed-event-p1m-e-campaign)
for the simulator and coverage model.

### Bench transport

[`I-CAN-hack/automotive` 0.7.0a1](https://github.com/I-CAN-hack/automotive/tree/d29d252cc9829af74079e3d791bda6e993af8a48)
matched the EPS probe's F181 ISO-TP request and flow-control bytes with zero
padding on a virtual bus. It also matched the response reassembly and NRC
decoding. Its Panda adapter does not implement the bench probe's Toyota
routing, NOOUTPUT state, heartbeat lease, or health counters. It does not
model Toyota application messages.

### Function comparison

[`ghidriff` 1.0.0](https://github.com/clearbluejar/ghidriff) recovered 24 of
326 verified named pairs, missed 302, and made three wrong pairings.
The inputs were the Sienna `8965B4512000` and Corolla `8965H1202000` EPS
images, not two calibrations of one part. Its JSON contains decompiler-text
diffs but no instruction-level diff. Use the exact matcher and verify
instruction changes as described in the
[update comparison record](../variants/toyota-eps-variant-comparison.md#update-comparison-record).

The comparison used Ghidra 12.2 on macOS arm64 and these host package versions:

```sh
uv venv --python 3.11 build/tmp/ghidriff-eval/venv
uv pip install --python build/tmp/ghidriff-eval/venv/bin/python 'ghidriff==1.0.0' 'pyghidra==3.2.0' 'jpype1==1.7.1'
```

Stock `ghidriff` 1.0.0 cannot select a raw-image language on the command
line. The scratch install imported both images at base zero with
`GhidraProject.importProgram`, the vendored `v850e3:LE:32:default` language,
and its default compiler. Its `VersionTrackingDiff` run used
`TaskMonitor.DUMMY`, the isolated Ghidra user home, and a working directory
outside the repository's `ghidra/` namespace.
