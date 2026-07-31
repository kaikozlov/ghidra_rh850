# Agent Instructions

## Critical Rules

1. **NEVER SKIP TESTS!** If Ghidra is not installed, the tests MUST fail. `require_ghidra!()` panics when `ghidra doctor` fails.
2. **DEFAULT OUTPUT FORMAT** should be human and agent readable, NOT JSON. Use `--json` and `--pretty` for JSON output. Exception: when stdout is not a TTY (piped/scripted), the default auto-detects to `JsonCompact` for machine consumption — this is standard Unix pipe convention.

## Architecture

ghidra-cli uses a **direct bridge architecture**:
- CLI connects directly to a Java bridge running inside Ghidra's JVM via TCP
- The bridge is a GhidraScript (`GhidraCliBridge.java`) started via `analyzeHeadless -postScript`
- Bridge binds `ServerSocket(0)` on localhost, writes port/PID files for discovery
- One bridge per project, identified by `~/.local/share/ghidra-cli/bridge-{md5}.port`
- Import/Analyze commands auto-start the bridge if not running
- No separate Rust daemon process — the Java bridge IS the persistent server
