# ghidra-cli Navigation Index

See @AGENTS.md for agent-specific instructions.

## Key Files

| What | When |
|------|------|
| `src/main.rs` | Modifying CLI entry point, bridge lifecycle, or output format detection |
| `src/main.rs` `verify_bridge()` | Changing bridge ping verification after connecting to an existing bridge |
| `src/main.rs` `extract_program_from_command()` | Adding new command variants that support `--program` switching |
| `src/cli.rs` | Adding/modifying CLI arguments and subcommands |
| `src/ghidra/scripts/GhidraCliBridge.java` `resolveDataType()` | Resolving type names to DataType (path, name scan, pointer syntax) |
| `src/format/mod.rs` | Implementing new output formats or changing format detection logic |
| `src/ghidra/bridge.rs` | Bridge process management (start/stop/status/connect via TCP) |
| `src/ghidra/scripts/GhidraCliBridge.java` | Java bridge server (TCP, command handlers, Ghidra API) |
| `src/ipc/client.rs` | BridgeClient (TCP connection, command methods) |
| `src/ipc/protocol.rs` | BridgeRequest/BridgeResponse wire format |
| `PLAN-java-plugin.md` | Architecture decisions and migration rationale |
| `README.md` | Understanding project architecture or user-facing command documentation |

## Modules

| What | When |
|------|------|
| `src/ghidra/` | Bridge management, Ghidra setup/installation, Java bridge script |
| `src/ipc/` | TCP client, protocol definitions, transport helpers |
| `src/format/` | Handling output format conversion (Table, Compact, JSON, CSV, etc.) |
| `tests/` | Writing integration or unit tests |

## Documentation

| What | When |
|------|------|
| `CHANGELOG.md` | Reviewing version history and release notes |
| `.claude/skills/ghidra-cli/SKILL.md` | Full command reference for AI agents (all commands, query options, workflows) |
| `src/ghidra/README.md` | Understanding bridge lifecycle, PID file sequence, TOCTOU elimination, BridgeClient adoption |
| `src/ipc/README.md` | Understanding TCP wire format, BridgeClient API, single implementation rationale |
| `tests/README.md` | Understanding test structure and conventions |
