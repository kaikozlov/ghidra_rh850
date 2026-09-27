# Tool layout

`tools/` is a **command surface**, not a dumping ground for every analysis script.
The files directly in this directory are the small set of commands worth remembering:

- `g`, `gtarget`, `pe`, `pseudo` — Ghidra/project access.
- `gts` — Toyota GTS+/Techstream discovery.
- `toyota` — Toyota platform capabilities and target workflow discovery.
- `artifact` — generated-artifact producer discovery/regeneration.
- `know` — repository research lookup.
- `annotations` — persistent Ghidra annotation ledger.
- `test` — explicit verification runner.
- `rh850` — target toolchain and instruction-simulation commands.

`uv sync --locked` installs the checkout as an editable Python package. Packaged
commands use `tools.*` imports and `tools.REPO_ROOT`, not `sys.path` bootstraps.
Ghidra's pre-environment bootstrap helpers remain stdlib-only.
For direct invocation, use module syntax, for example
`uv run --locked python -m tools.project.analysis_target --list`.

Implementation is grouped by the capability it serves:

- `targets/<family>/` — calibration-specific analysis and artifact producers. Input captures stay at the paths registered in `data/analysis_targets.json`.
- `toyota_support/` — reusable Toyota protocol libraries behind `tools/toyota`.
  `passive_capture.py` owns retained JSON/JSONL/gzip readers and streaming digests;
  `toyota_route_opendbc_common.py` owns shared route decoding.
  Calibration-specific scaling and time/bus selection stay with their analyses.
- `techstream/` — GTS+/Techstream parsers and extractors behind `tools/gts` / `tools/toyota gts`.
  Its `gts/cli.py` owns argument parsing/dispatch, `gts/render.py` owns presentation,
  and the other `gts/` modules own DDB, master-data, CUW, query, and registry/bundle
  computation. Standalone extractors reuse those modules rather than importing a CLI.
- `project/` — Ghidra project lifecycle, corpus generation, and processor mechanics.
- `firmware/` — generic firmware-derived artifact producers.
- `security/` — generic SecOC/payload/memory-safety analysis mechanics.
- `variants/` — cross-calibration comparison/extraction.
- `toolchains/` — implementation of `tools/rh850` and the pinned GNU toolchain build inputs (`v850-gcc/` Dockerfile and patches).
- `catalog/` — implementation of `tools/artifact` and `tools/know`.
- `testing/` — implementation of `tools/test`; verification machinery is deliberately not presented as general tooling.
- `diagnostics/`, `lib/` — shared diagnostic and shell-library internals.

The existing target registry joins each calibration's firmware/capture inputs,
working/snapshot projects, inventory, and decompiler corpus. Generic consumers
resolve those paths through `tools.project.analysis_target`; family-specific code
keeps calibration constants local. Historical byte inputs are not relocated to
make the implementation tree symmetrical.

Do not add a new root-level implementation script. Put it in the narrowest reusable
namespace. If it creates a tracked artifact, let `tools/artifact` discover it. If it
adds a reusable Toyota or target capability, make it visible through `tools/toyota`
(or `tools/gts` for GTS+/Techstream) so a later session can discover that capability
without remembering the implementation filename.
