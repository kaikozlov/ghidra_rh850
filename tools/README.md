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

Implementation is grouped by the capability it serves:

- `targets/camry/`, `targets/corolla/`, `targets/sienna/` — calibration/vehicle-specific analyses, captures, and artifact producers.
- `toyota_support/` — reusable Toyota protocol libraries behind `tools/toyota`.
- `techstream/` — GTS+/Techstream parsers and extractors behind `tools/gts` / `tools/toyota gts`.
- `project/` — Ghidra project lifecycle, corpus generation, and processor mechanics.
- `firmware/` — generic firmware-derived artifact producers.
- `security/` — generic SecOC/payload/memory-safety analysis mechanics.
- `variants/` — cross-calibration comparison/extraction.
- `catalog/` — implementation of `tools/artifact`.
- `testing/` — implementation of `tools/test`; verification machinery is deliberately not presented as general tooling.
- `diagnostics/`, `lib/` — shared diagnostic and shell-library internals.

Do not add a new root-level implementation script. Put it in the narrowest reusable
namespace. If it creates a tracked artifact, let `tools/artifact` discover it. If it
adds a reusable Toyota or target capability, make it visible through `tools/toyota`
(or `tools/gts` for GTS+/Techstream) so a later session can discover that capability
without remembering the implementation filename.
