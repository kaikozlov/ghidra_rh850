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
| Broad gates | `tools/test core` / `full` / `branch` |
| Query another configured target | `tools/gtarget` (or a target wrapper such as `tools/gcamry`) |
| Discover Corolla-H evidence-compaction profiles | `uv run --locked python tools/extract_corolla_h_evidence.py list` |
| Discover cross-variant evidence modes | `uv run --locked python tools/extract_variant_evidence.py list` |
| Discover working-project export profiles | `tools/export_ghidra_project.sh list` |

Family modules (`tests/verify_application_wdbi.py`, `tests/verify_corolla_h.py`,
and so on) group same-mode same-family portable proofs. Prefix queries are the
memory: `tools/test list application` / `corolla` / `techstream`. Keep live,
external, and distinct safety pipelines as separate files.

The repeated Corolla-H corpus-compaction scripts are consolidated behind one
profile-driven command:

```bash
uv run --locked python tools/extract_corolla_h_evidence.py list
uv run --locked python tools/extract_corolla_h_evidence.py extract can-com
uv run --locked python tools/extract_corolla_h_evidence.py extract xcp
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
uv run --locked python tools/extract_variant_evidence.py list
uv run --locked python tools/extract_variant_evidence.py structural --image ... --fingerprints ... \
  --software-id 8965H1202000 --address 0xCEDAE ... --out data/generated/...json
uv run --locked python tools/extract_variant_evidence.py function --image ... --corpus ... \
  --software-id 8965H1202000 --address 0xB6 ... --out data/generated/...json
uv run --locked python tools/extract_variant_evidence.py application-diagnostics --image ... \
  --corpus ... --did-table 0x... --did-count 180 --routine-callback-table 0x... \
  --software-id 8965H1202000 --out data/generated/...json
uv run --locked python tools/extract_variant_evidence.py reference-census --image ... \
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

## Deliberate non-consolidations

Several tool families *look* consolidatable but are not, because they only share
incidental boilerplate, not one operation. Each of these carries distinct proof
logic, fail-closed boundaries, or safety contracts that a shared runner would
hide:

- **Techstream CUW inspectors and writer generators.** `parse_cuw_container.py`
  already packages the shared container parser; `inspect_cuw_legacy.py` exports
  the shared legacy attach/parameter decoders used by the other inspectors, and
  `generate_cuw_writer_inventory.py` exports the shared parameter-INI decoder
  and factory-route table consumed by the writer-analysis tools. The remaining
  per-tool code encodes distinct evidence boundaries and proof outputs
  (whole-repro vs delta corpus invariants, per-family route verdicts, timing
  recovery, calibration schema), each pinned by its own deterministic test
  suite. Merging them would bury fail-closed boundary contracts, and their
  shared mechanics are already factored where genuinely common.
- **Corolla-H semantic extractors and builders.** The remaining
  `extract_corolla_h_*_evidence.py` tools each embed distinct discovery logic:
  whole-corpus literal-call closure (`direct_call_surface`), image-resolved
  callback tables (`deadline_monitor_surface`, `diagnostic_residue`),
  artifact-derived cohort joins (`structural_residue`), a seven-corpus
  reference-pair join with fragmented-body pinning (`secoc_surface`), and a
  dual-image Sienna/H fingerprint join (`final_named_residue`). The
  `build_corolla_h_*` semantic builders likewise encode subsystem-specific
  proof logic (routing tables, selector policies, supervisor alignment,
  diagnostic joins). These are different operations, not variants of one.
- **Arbitrary-image resolver wrappers.** `resolve_secoc_patch_image.sh` and
  `resolve_ephemeral_runtime_image.sh` both import a disposable Ghidra project,
  but their input contracts (bare 1 MiB only vs 2 MiB range-dumper
  normalization), fail-closed gates (CRC-geometry ambiguity vs
  geometry-unresolved/steering-unsupported outcomes), resolvers, and output
  manifests are distinct safety pipelines. A merged CLI would hide which
  fail-closed contract is being enforced; they stay separate. The
  working-project variant `resolve_secoc_patch.sh` is lifecycle-adjacent
  (drives `tools/g`) and is likewise untouched.

Do not add a helper that merely centralizes `sha256`/`load_jsonl` boilerplate
across these families: that moves code without strengthening any invariant. The
consolidation test (`tests/verify_tooling_consolidation.py`) pins this taxonomy
in both directions — retired files must stay gone, and the deliberately
separate tools must stay present.

Read-only exports from `build/work/project` use a second shared profile runner:

```bash
tools/export_ghidra_project.sh list
tools/export_ghidra_project.sh application-rx-signals
tools/export_ghidra_project.sh application-rx-consumers
tools/export_ghidra_project.sh application-tx-producers
tools/export_ghidra_project.sh outside-functions
tools/export_ghidra_project.sh semantic-coverage
tools/export_ghidra_project.sh project-inventory
```

This replaces the former one-shell-wrapper-per-export pattern. The profile
runner owns artifact defaults and deterministic postprocessing; the existing
`tools/run_headless` remains the single owner of committed-project rejection,
Ghidra environment bootstrap, controlled script paths, logging, and headless
failure detection. Keep new read-only project exports in this profile runner
unless their lifecycle or safety semantics are genuinely different.

## Vendored processor module

The RH850 language `v850e3:LE:32:default` is the **vendored in-tree fork** at
`ghidra/ghidra_v850/` (forked from `esaulenka/ghidra_v850` at commit
`14c1b5be32b8ec741ee626c8bca9885c58f7a473`; see
`ghidra/ghidra_v850/PROVENANCE.json`). Install path and fingerprint checks are
in [../WORKFLOW.md](../WORKFLOW.md).

- [Ephemeral runtime semantic resolver](ephemeral-runtime-semantic-resolver.md) — fresh-image fail-closed resolver and SHA-bound target manifest for the RAM scheduler/SecOC-COM bridge.
