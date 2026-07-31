# Plan: Complete All Stub Commands

> Historical planning document: parts of this plan assume an older daemon-centric architecture and may not match the current implementation.
> For current behavior, use `README.md`, `AGENTS.md`, and the CLI help output.

## Overview

ghidra-cli has 39 stub commands that output "not yet implemented". This plan implements all stub commands using a hybrid approach: grouped by category with shared helpers per group. Each category becomes a deployable unit with its own Ghidra bridge Python scripts, daemon routing, and E2E tests.

**Chosen Approach**: Hybrid - grouped by category (user-specified)
**Testing Strategy**: Property-based + example-based for unit tests, real daemon for integration (user-specified)

**Stub Command Inventory** (verified from `src/cli.rs` Commands enum and `src/main.rs` handler routing):

| Category | Commands | Count | Milestone |
|----------|----------|-------|-----------|
| Program | close, delete, info, export | 4 | M1 |
| Symbol | list, get, create, delete, rename | 5 | M2 |
| Type | list, get, create, apply | 4 | M3 |
| Comment | list, get, set, delete | 4 | M4 |
| Graph | calls, callers, callees, export | 4 | M5 |
| Find | string, bytes, function, calls, crypto, interesting | 6 | M6 |
| Diff | programs, functions | 2 | M7 |
| Patch | bytes, nop, export | 3 | M8 |
| Script | run, python, java, list | 4 | M9 |
| Disasm | disasm | 1 | M10 |
| Batch | batch | 1 | M11 |
| Stats | stats | 1 | M12 |

**Total: 39 stub commands** (verified: matches 39 tests in `tests/unimplemented_tests.rs`)

Note: Memory commands (read, write, search) are routed through daemon in `execute_via_daemon()` but bail with "Memory subcommand not yet supported via daemon". They are NOT counted as stubs since they have partial implementation path (only `memory map` works). They'll be completed as part of expanding daemon capabilities, not stub implementation.

## Planning Context

### Decision Log

| Decision | Reasoning Chain |
|----------|-----------------|
| Hybrid grouping over per-command | 30+ commands share patterns within categories -> shared helpers reduce duplication -> categories can be tested/deployed as units |
| Python bridge scripts per category | Ghidra API is Jython-native -> Python scripts run inside Ghidra process -> no JNI overhead -> already established pattern in bridge.py |
| JSON over stdout for script results | Bridge uses TCP but scripts output to stdout -> marker-based JSON extraction exists -> consistent with decompile/list_functions patterns |
| Daemon routing in queue.rs | All queries route through queue.rs match arms -> single point of command dispatch -> cache integration automatic |
| Category-specific helpers in separate modules | Symbol/type/comment ops share address resolution -> extract to e.g. src/daemon/handlers/symbols.rs -> avoid queue.rs bloat |
| E2E tests with real daemon | Real daemon exposes IPC + bridge + Ghidra integration bugs that mocks cannot catch -> mock tests previously missed daemon lifecycle issues -> user explicitly required real daemon testing -> trade startup overhead (~500ms/test) for integration confidence |

### Rejected Alternatives

| Alternative | Why Rejected |
|-------------|--------------|
| Trait-based GhidraCommand refactor | Upfront refactoring delays feature delivery -> existing pattern works -> optimize later if needed |
| Mock-based testing | User explicitly chose real daemon testing -> mocks miss integration bugs |
| Per-command implementation | 30+ separate PRs slows progress -> category grouping enables parallel work |
| Direct Ghidra Java API | Would require JNI bridge -> Jython scripts already work -> no benefit |

### Constraints & Assumptions

- Ghidra installation required (GHIDRA_INSTALL_DIR)
- Ghidra 11.x uses Jython 2.7.2 (verify at `$GHIDRA_INSTALL_DIR/Ghidra/Features/Python/lib/jython-standalone-2.7.2.jar`) - Python 2.7 syntax required in all scripts
- Daemon must be running for all query commands (enforced by IPC layer)
- Existing bridge.py TCP server pattern must be extended
- Test binary (sample_binary) available in tests/fixtures/
- Default conventions applied: `<default-conventions domain="testing">` for test structure
- Real daemon testing required (user constraint) - see Decision Log for E2E rationale

### Known Risks

| Risk | Mitigation | Anchor |
|------|------------|--------|
| Ghidra API changes between versions | Pin to Ghidra 11.x APIs; document version in CLAUDE.md | N/A (external) |
| Long-running graph operations | Add timeout parameter; document in CLI help | N/A (new code) |
| Script execution security | Scripts run in Ghidra sandbox; no filesystem access beyond project | N/A (Ghidra behavior) |

## Invisible Knowledge

### Architecture

```
CLI Command
    |
    v
+------------------+
| IPC Client       |  (Unix socket)
+------------------+
    |
    v
+------------------+     +------------------+
| Daemon Queue     |---->| Handler Module   |
+------------------+     | (per category)   |
    |                    +------------------+
    v                           |
+------------------+            v
| Ghidra Bridge    |<-----------+
| (TCP socket)     |
+------------------+
    |
    v
+------------------+
| Python Script    |  (runs inside Ghidra)
+------------------+
```

### Data Flow

```
Command -> IPC -> Queue -> Handler -> Bridge -> Script -> JSON -> Response
                    |
                    v
                 Cache (optional)
```

### Why This Structure

- **Handler modules per category**: Keeps queue.rs focused on routing; category logic isolated
- **Python scripts per operation**: Ghidra APIs differ per domain (symbols vs types vs comments)
- **Shared address resolution**: Many operations need address parsing (0x... or name lookup)

### Invariants

- All query commands require daemon (enforced in run_with_daemon_check)
- Script output must use markers: `---GHIDRA_CLI_START---` and `---GHIDRA_CLI_END---`
- JSON responses must be arrays for list operations, objects for single-item operations

### Tradeoffs

- **Multiple Python scripts vs single mega-script**: Chose multiple for maintainability; slight startup overhead per command type
- **Category modules vs inline in queue.rs**: Chose modules for testability; adds file navigation overhead

## Milestones

### Milestone 1: Program Operations

**Files**:
- `src/daemon/handlers/mod.rs` (new)
- `src/daemon/handlers/program.rs` (new)
- `src/daemon/queue.rs` (modify)
- `src/ghidra/scripts/program.py` (new)
- `tests/program_tests.rs` (new)

**Flags**: `conformance`, `needs-rationale`

**Requirements**:
- `program close` - Close current program in daemon
- `program delete` - Delete program from project
- `program info` - Show program metadata
- `program export <format>` - Export program to format

**Acceptance Criteria**:
- `ghidra program close` closes active program, daemon remains running
- `ghidra program delete` removes program from Ghidra project
- `ghidra program info` returns JSON with name, path, format, processor, language
- `ghidra program export json` exports program data to JSON format
- All commands require daemon running

**Tests**:
- **Test files**: `tests/program_tests.rs`
- **Test type**: integration (real daemon)
- **Backing**: user-specified
- **Scenarios**:
  - Normal: get info, export to JSON, close program
  - Edge: info on minimal binary, export with custom output path
  - Error: close when no program loaded, delete non-existent

**Code Intent**:
- New `src/daemon/handlers/mod.rs`: Module declaration for handler submodules
- New `src/daemon/handlers/program.rs`:
  - `handle_program_close(bridge)` - Close program in daemon
  - `handle_program_delete(bridge, program_name)` - Delete from project
  - `handle_program_info(bridge)` - Get program metadata
  - `handle_program_export(bridge, format, output)` - Export program
- Modify `src/daemon/queue.rs`: Add match arms for ProgramCommands routing to handlers
- New `src/ghidra/scripts/program.py`:
  - `close_program()` - Close current program
  - `delete_program(name)` - Remove from project
  - `get_program_info()` - Return metadata dict
  - `export_program(format, output)` - Use Ghidra exporters
- New `tests/program_tests.rs`: E2E tests using DaemonTestHarness

**Code Changes**:

```diff
--- /dev/null
+++ b/src/daemon/handlers/mod.rs
@@ -0,0 +1,6 @@
+//! Handler modules for daemon commands grouped by category.
+
+pub mod program;
+pub mod symbols;
+pub mod types;
+pub mod comments;
```

```diff
--- /dev/null
+++ b/src/daemon/handlers/program.rs
@@ -0,0 +1,96 @@
+//! Program operation handlers.
+
+use anyhow::{Context, Result};
+use serde_json::json;
+use crate::ghidra::bridge::GhidraBridge;
+
+pub async fn handle_program_close(bridge: &mut GhidraBridge) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "program_close",
+        None
+    ).context("Failed to close program")?;
+
+    if response.status == "success" {
+        Ok(json!({"status": "closed"}).to_string())
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to close program".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_program_delete(
+    bridge: &mut GhidraBridge,
+    program_name: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "program_delete",
+        Some(json!({
+            "program": program_name
+        }))
+    ).context("Failed to delete program")?;
+
+    if response.status == "success" {
+        Ok(json!({"status": "deleted", "program": program_name}).to_string())
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to delete program".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_program_info(bridge: &mut GhidraBridge) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "program_info",
+        None
+    ).context("Failed to get program info")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to get program info".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_program_export(
+    bridge: &mut GhidraBridge,
+    format: &str,
+    output: Option<&str>
+) -> Result<String> {
+    let mut args = json!({
+        "format": format
+    });
+
+    if let Some(output_path) = output {
+        args["output"] = json!(output_path);
+    }
+
+    let response = bridge.send_command::<serde_json::Value>(
+        "program_export",
+        Some(args)
+    ).context("Failed to export program")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to export program".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+}
```

```diff
--- a/src/daemon/queue.rs
+++ b/src/daemon/queue.rs
@@ -14,6 +14,7 @@ use tracing::{info, warn};

 use crate::cli::Commands;
 use crate::daemon::cache::Cache;
+use crate::daemon::handlers;
 use crate::ghidra::bridge::GhidraBridge;

 /// A queued command waiting to be executed.
@@ -180,6 +181,29 @@ async fn execute_command(
             }
         },
+        Commands::Program(prog_cmd) => {
+            use crate::cli::ProgramCommands;
+            let mut bridge_guard = bridge.lock().await;
+            let bridge_ref = bridge_guard.as_mut()
+                .ok_or_else(|| anyhow::anyhow!("Bridge not initialized"))?;
+
+            if !bridge_ref.is_running() {
+                anyhow::bail!("Bridge is not running");
+            }
+
+            return match prog_cmd {
+                ProgramCommands::Close(_) => handlers::program::handle_program_close(bridge_ref).await,
+                ProgramCommands::Delete(args) => {
+                    let program = args.program.as_ref()
+                        .ok_or_else(|| anyhow::anyhow!("Program name required"))?;
+                    handlers::program::handle_program_delete(bridge_ref, program).await
+                },
+                ProgramCommands::Info(_) => handlers::program::handle_program_info(bridge_ref).await,
+                ProgramCommands::Export(args) => {
+                    handlers::program::handle_program_export(bridge_ref, &args.format, args.output.as_deref()).await
+                },
+            };
+        },
         Commands::Decompile(decompile_args) => (
             "decompile",
             Some(json!({
```

```diff
--- /dev/null
+++ b/src/ghidra/scripts/program.py
@@ -0,0 +1,115 @@
+# Program operations script
+# @category CLI
+
+import sys
+import json
+
+def close_program():
+    """Close the current program."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    program_name = currentProgram.getName()
+    state.getTool().closeProgram(currentProgram, False)
+
+    return {"status": "closed", "program": program_name}
+
+def delete_program(program_name):
+    """Delete a program from the project."""
+    project = state.getProject()
+    if project is None:
+        return {"error": "No project open"}
+
+    project_data = project.getProjectData()
+
+    try:
+        program_file = project_data.getFile(program_name)
+        if program_file is None:
+            return {"error": "Program not found: " + program_name}
+
+        project_data.deleteFile(program_name)
+        return {"status": "deleted", "program": program_name}
+    except Exception as e:
+        return {"error": "Failed to delete program: " + str(e)}
+
+def get_program_info():
+    """Get current program metadata."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    info = {
+        "name": currentProgram.getName(),
+        "path": currentProgram.getExecutablePath(),
+        "format": currentProgram.getExecutableFormat(),
+        "processor": str(currentProgram.getLanguage().getProcessor()),
+        "language": str(currentProgram.getLanguage()),
+        "compiler": currentProgram.getCompiler() if currentProgram.getCompiler() else None,
+        "image_base": str(currentProgram.getImageBase()),
+        "min_address": str(currentProgram.getMinAddress()),
+        "max_address": str(currentProgram.getMaxAddress()),
+        "creation_date": str(currentProgram.getCreationDate())
+    }
+
+    return info
+
+def export_program(export_format, output_path):
+    """Export program to specified format."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    from ghidra.app.util.exporter import Exporter
+    from ghidra.framework.model import DomainFile
+    from java.io import File
+
+    if export_format == "json":
+        data = get_program_info()
+
+        function_manager = currentProgram.getFunctionManager()
+        functions = []
+        for func in function_manager.getFunctions(True):
+            functions.append({
+                "name": func.getName(),
+                "address": str(func.getEntryPoint()),
+                "size": func.getBody().getNumAddresses()
+            })
+        data["functions"] = functions
+
+        if output_path:
+            with open(output_path, 'w') as f:
+                json.dump(data, f, indent=2)
+            return {"status": "exported", "format": "json", "output": output_path}
+        else:
+            return data
+    else:
+        return {"error": "Unsupported export format: " + export_format}
+
+if __name__ == "__main__":
+    try:
+        if len(args) < 1:
+            print("---GHIDRA_CLI_START---")
+            print(json.dumps({"error": "No command specified"}))
+            print("---GHIDRA_CLI_END---")
+            sys.exit(1)
+
+        command = args[0]
+
+        if command == "close":
+            result = close_program()
+        elif command == "delete":
+            result = delete_program(args[1] if len(args) > 1 else None)
+        elif command == "info":
+            result = get_program_info()
+        elif command == "export":
+            fmt = args[1] if len(args) > 1 else "json"
+            output = args[2] if len(args) > 2 else None
+            result = export_program(fmt, output)
+        else:
+            result = {"error": "Unknown command: " + command}
+
+        print("---GHIDRA_CLI_START---")
+        print(json.dumps(result))
+        print("---GHIDRA_CLI_END---")
+    except Exception as e:
+        print("---GHIDRA_CLI_START---")
+        print(json.dumps({"error": str(e)}))
+        print("---GHIDRA_CLI_END---")
```

```diff
--- /dev/null
+++ b/tests/program_tests.rs
@@ -0,0 +1,97 @@
+//! Tests for program operations.
+
+use assert_cmd::Command;
+use predicates::prelude::*;
+use serial_test::serial;
+
+#[macro_use]
+mod common;
+use common::{ensure_test_project, DaemonTestHarness};
+
+const TEST_PROJECT: &str = "program-test";
+const TEST_PROGRAM: &str = "sample_binary";
+
+#[test]
+#[serial]
+fn test_program_info() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("program")
+        .arg("info")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("name"))
+        .stdout(predicate::str::contains("format"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_program_export_json() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("program")
+        .arg("export")
+        .arg("json")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("functions"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_program_close() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("program")
+        .arg("close")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_program_info_no_program() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("program")
+        .arg("info")
+        .assert()
+        .failure();
+
+    drop(harness);
+}
```

---

### Milestone 2: Symbol Operations

**Files**:
- `src/daemon/handlers/mod.rs` (new)
- `src/daemon/handlers/symbols.rs` (new)
- `src/daemon/queue.rs` (modify)
- `src/ghidra/scripts/symbols.py` (new)
- `tests/symbol_tests.rs` (new)

**Flags**: `conformance`, `needs-rationale`

**Requirements**:
- `symbol list` - List all symbols with optional filter
- `symbol get <address>` - Get symbol at specific address
- `symbol create <address> <name>` - Create new symbol
- `symbol delete <name>` - Delete symbol by name
- `symbol rename <old> <new>` - Rename existing symbol

**Acceptance Criteria**:
- `ghidra symbol list` returns JSON array of symbols with name, address, type fields
- `ghidra symbol get 0x1000` returns symbol object or error if not found
- `ghidra symbol create 0x1000 my_func` creates symbol, returns success
- `ghidra symbol delete my_func` removes symbol, returns success
- `ghidra symbol rename old_name new_name` renames symbol, returns success
- All commands require daemon running

**Tests**:
- **Test files**: `tests/symbol_tests.rs`
- **Test type**: integration (real daemon)
- **Backing**: user-specified
- **Scenarios**:
  - Normal: list symbols, get existing symbol, create/delete/rename cycle
  - Edge: get non-existent address, create at existing address
  - Error: delete non-existent symbol, rename to existing name

**Code Intent**:
- New `src/daemon/handlers/mod.rs`: Module declaration for handler submodules
- New `src/daemon/handlers/symbols.rs`:
  - `handle_symbol_list(bridge, filter)` - Query all symbols
  - `handle_symbol_get(bridge, address)` - Query single symbol
  - `handle_symbol_create(bridge, address, name)` - Create symbol
  - `handle_symbol_delete(bridge, name)` - Delete symbol
  - `handle_symbol_rename(bridge, old, new)` - Rename symbol
  - Helper: `resolve_address(input)` - Parse "0x..." or lookup by name
- Modify `src/daemon/queue.rs`: Add match arms for SymbolCommands routing to handlers
- New `src/ghidra/scripts/symbols.py`:
  - `list_symbols(filter)` - Iterate SymbolTable
  - `get_symbol(address)` - Lookup at address
  - `create_symbol(address, name)` - Add to SymbolTable
  - `delete_symbol(name)` - Remove from SymbolTable
  - `rename_symbol(old, new)` - Modify symbol name
- New `tests/symbol_tests.rs`: E2E tests using DaemonTestHarness

**Code Changes**:

```diff
--- /dev/null
+++ b/src/daemon/handlers/symbols.rs
@@ -0,0 +1,136 @@
+//! Symbol operation handlers.
+
+use anyhow::{Context, Result};
+use serde_json::json;
+use crate::ghidra::bridge::GhidraBridge;
+
+pub async fn handle_symbol_list(
+    bridge: &mut GhidraBridge,
+    filter: Option<&str>
+) -> Result<String> {
+    let args = if let Some(f) = filter {
+        Some(json!({"filter": f}))
+    } else {
+        None
+    };
+
+    let response = bridge.send_command::<serde_json::Value>(
+        "symbol_list",
+        args
+    ).context("Failed to list symbols")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to list symbols".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_symbol_get(
+    bridge: &mut GhidraBridge,
+    address: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "symbol_get",
+        Some(json!({"address": address}))
+    ).context("Failed to get symbol")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to get symbol".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_symbol_create(
+    bridge: &mut GhidraBridge,
+    address: &str,
+    name: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "symbol_create",
+        Some(json!({
+            "address": address,
+            "name": name
+        }))
+    ).context("Failed to create symbol")?;
+
+    if response.status == "success" {
+        Ok(json!({"status": "created", "address": address, "name": name}).to_string())
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to create symbol".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_symbol_delete(
+    bridge: &mut GhidraBridge,
+    name: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "symbol_delete",
+        Some(json!({"name": name}))
+    ).context("Failed to delete symbol")?;
+
+    if response.status == "success" {
+        Ok(json!({"status": "deleted", "name": name}).to_string())
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to delete symbol".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_symbol_rename(
+    bridge: &mut GhidraBridge,
+    old_name: &str,
+    new_name: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "symbol_rename",
+        Some(json!({
+            "old_name": old_name,
+            "new_name": new_name
+        }))
+    ).context("Failed to rename symbol")?;
+
+    if response.status == "success" {
+        Ok(json!({"status": "renamed", "old_name": old_name, "new_name": new_name}).to_string())
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to rename symbol".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+fn resolve_address(input: &str) -> Result<String> {
+    // Pass-through to Python layer which handles both hex addresses and symbol name lookups
+    if input.starts_with("0x") || input.chars().all(|c| c.is_ascii_hexdigit()) {
+        Ok(input.to_string())
+    } else {
+        Ok(input.to_string())
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    #[test]
+    fn test_resolve_address_hex() {
+        assert_eq!(resolve_address("0x1000").unwrap(), "0x1000");
+    }
+
+    #[test]
+    fn test_resolve_address_name() {
+        assert_eq!(resolve_address("main").unwrap(), "main");
+    }
+}
```

```diff
--- a/src/daemon/queue.rs
+++ b/src/daemon/queue.rs
@@ -204,6 +204,32 @@ async fn execute_command(
                 },
             };
         },
+        Commands::Symbol(sym_cmd) => {
+            use crate::cli::SymbolCommands;
+            let mut bridge_guard = bridge.lock().await;
+            let bridge_ref = bridge_guard.as_mut()
+                .ok_or_else(|| anyhow::anyhow!("Bridge not initialized"))?;
+
+            if !bridge_ref.is_running() {
+                anyhow::bail!("Bridge is not running");
+            }
+
+            return match sym_cmd {
+                SymbolCommands::List(opts) => {
+                    handlers::symbols::handle_symbol_list(bridge_ref, opts.filter.as_deref()).await
+                },
+                SymbolCommands::Get(args) => {
+                    handlers::symbols::handle_symbol_get(bridge_ref, &args.name).await
+                },
+                SymbolCommands::Create(args) => {
+                    handlers::symbols::handle_symbol_create(bridge_ref, &args.address, &args.name).await
+                },
+                SymbolCommands::Delete(args) => {
+                    handlers::symbols::handle_symbol_delete(bridge_ref, &args.name).await
+                },
+                SymbolCommands::Rename(args) => {
+                    handlers::symbols::handle_symbol_rename(bridge_ref, &args.old_name, &args.new_name).await
+                },
+            };
+        },
         Commands::Decompile(decompile_args) => (
             "decompile",
             Some(json!({
```

```diff
--- /dev/null
+++ b/src/ghidra/scripts/symbols.py
@@ -0,0 +1,142 @@
+# Symbol operations script
+# @category CLI
+
+import sys
+import json
+
+def list_symbols(name_filter):
+    """List all symbols in the program."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    symbol_table = currentProgram.getSymbolTable()
+    symbols = []
+
+    for symbol in symbol_table.getAllSymbols(True):
+        name = symbol.getName()
+
+        if name_filter and name_filter.lower() not in name.lower():
+            continue
+
+        symbol_data = {
+            "name": name,
+            "address": str(symbol.getAddress()),
+            "type": str(symbol.getSymbolType()),
+            "source": str(symbol.getSource()),
+            "is_primary": symbol.isPrimary()
+        }
+        symbols.append(symbol_data)
+
+    return {"symbols": symbols, "count": len(symbols)}
+
+def get_symbol(address_or_name):
+    """Get symbol at specific address or by name."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    symbol_table = currentProgram.getSymbolTable()
+
+    if address_or_name.startswith("0x") or all(c in "0123456789abcdefABCDEF" for c in address_or_name):
+        try:
+            addr = currentProgram.getAddressFactory().getAddress(address_or_name)
+            if addr is None:
+                return {"error": "Invalid address: " + address_or_name}
+
+            symbols_at_addr = symbol_table.getSymbols(addr)
+            if not symbols_at_addr:
+                return {"error": "No symbol at address: " + address_or_name}
+
+            result_symbols = []
+            for symbol in symbols_at_addr:
+                result_symbols.append({
+                    "name": symbol.getName(),
+                    "address": str(symbol.getAddress()),
+                    "type": str(symbol.getSymbolType()),
+                    "source": str(symbol.getSource())
+                })
+            return {"symbols": result_symbols}
+        except Exception as e:
+            return {"error": "Failed to get symbol: " + str(e)}
+    else:
+        symbols = symbol_table.getSymbols(address_or_name)
+        if not symbols or len(symbols) == 0:
+            return {"error": "Symbol not found: " + address_or_name}
+
+        result_symbols = []
+        for symbol in symbols:
+            result_symbols.append({
+                "name": symbol.getName(),
+                "address": str(symbol.getAddress()),
+                "type": str(symbol.getSymbolType()),
+                "source": str(symbol.getSource())
+            })
+        return {"symbols": result_symbols}
+
+def create_symbol(address_str, name):
+    """Create a new symbol."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    try:
+        addr = currentProgram.getAddressFactory().getAddress(address_str)
+        if addr is None:
+            return {"error": "Invalid address: " + address_str}
+
+        symbol_table = currentProgram.getSymbolTable()
+        from ghidra.program.model.symbol import SourceType
+
+        symbol_table.createLabel(addr, name, SourceType.USER_DEFINED)
+
+        return {"status": "created", "address": address_str, "name": name}
+    except Exception as e:
+        return {"error": "Failed to create symbol: " + str(e)}
+
+def delete_symbol(name):
+    """Delete a symbol by name."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    try:
+        symbol_table = currentProgram.getSymbolTable()
+        symbols = symbol_table.getSymbols(name)
+
+        if not symbols or len(symbols) == 0:
+            return {"error": "Symbol not found: " + name}
+
+        for symbol in symbols:
+            symbol.delete()
+
+        return {"status": "deleted", "name": name}
+    except Exception as e:
+        return {"error": "Failed to delete symbol: " + str(e)}
+
+def rename_symbol(old_name, new_name):
+    """Rename a symbol."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    try:
+        symbol_table = currentProgram.getSymbolTable()
+        symbols = symbol_table.getSymbols(old_name)
+
+        if not symbols or len(symbols) == 0:
+            return {"error": "Symbol not found: " + old_name}
+
+        for symbol in symbols:
+            symbol.setName(new_name, symbol.getSource())
+
+        return {"status": "renamed", "old_name": old_name, "new_name": new_name}
+    except Exception as e:
+        return {"error": "Failed to rename symbol: " + str(e)}
+
+if __name__ == "__main__":
+    try:
+        if len(args) < 1:
+            print("---GHIDRA_CLI_START---")
+            print(json.dumps({"error": "No command specified"}))
+            print("---GHIDRA_CLI_END---")
+            sys.exit(1)
+
+        command = args[0]
+
+        if command == "list":
+            result = list_symbols(args[1] if len(args) > 1 else None)
+        elif command == "get":
+            result = get_symbol(args[1] if len(args) > 1 else None)
+        elif command == "create":
+            result = create_symbol(args[1] if len(args) > 1 else None, args[2] if len(args) > 2 else None)
+        elif command == "delete":
+            result = delete_symbol(args[1] if len(args) > 1 else None)
+        elif command == "rename":
+            result = rename_symbol(args[1] if len(args) > 1 else None, args[2] if len(args) > 2 else None)
+        else:
+            result = {"error": "Unknown command: " + command}
+
+        print("---GHIDRA_CLI_START---")
+        print(json.dumps(result))
+        print("---GHIDRA_CLI_END---")
+    except Exception as e:
+        print("---GHIDRA_CLI_START---")
+        print(json.dumps({"error": str(e)}))
+        print("---GHIDRA_CLI_END---")
```

```diff
--- /dev/null
+++ b/tests/symbol_tests.rs
@@ -0,0 +1,118 @@
+//! Tests for symbol operations.
+
+use assert_cmd::Command;
+use predicates::prelude::*;
+use serial_test::serial;
+
+#[macro_use]
+mod common;
+use common::{ensure_test_project, DaemonTestHarness};
+
+const TEST_PROJECT: &str = "symbol-test";
+const TEST_PROGRAM: &str = "sample_binary";
+
+#[test]
+#[serial]
+fn test_symbol_list() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("symbol")
+        .arg("list")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("symbols"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_symbol_create_and_get() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("symbol")
+        .arg("create")
+        .arg("0x1000")
+        .arg("test_symbol")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("symbol")
+        .arg("get")
+        .arg("test_symbol")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("test_symbol"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_symbol_rename() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("symbol")
+        .arg("create")
+        .arg("0x2000")
+        .arg("old_symbol")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("symbol")
+        .arg("rename")
+        .arg("old_symbol")
+        .arg("new_symbol")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_symbol_get_nonexistent() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("symbol")
+        .arg("get")
+        .arg("nonexistent_symbol_12345")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .failure();
+
+    drop(harness);
+}
```

---

### Milestone 3: Type Operations

**Files**:
- `src/daemon/handlers/types.rs` (new)
- `src/daemon/queue.rs` (modify)
- `src/ghidra/scripts/types.py` (new)
- `tests/type_tests.rs` (new)

**Flags**: `conformance`, `complex-algorithm`

**Requirements**:
- `type list` - List all defined types
- `type get <name>` - Get type definition by name
- `type create <name>` - Create new struct/typedef
- `type apply <address> <type>` - Apply type to address

**Acceptance Criteria**:
- `ghidra type list` returns JSON array of type names and categories
- `ghidra type get int` returns type definition (size, fields if struct)
- `ghidra type create MyStruct` creates empty struct type
- `ghidra type apply 0x1000 int` applies type annotation to address
- Type operations reflect in subsequent queries

**Tests**:
- **Test files**: `tests/type_tests.rs`
- **Test type**: integration
- **Backing**: user-specified
- **Scenarios**:
  - Normal: list types, get primitive, create struct, apply to address
  - Edge: get non-existent type, create duplicate name
  - Error: apply invalid type, apply to invalid address

**Code Intent**:
- New `src/daemon/handlers/types.rs`:
  - `handle_type_list(bridge)` - List DataTypeManager contents
  - `handle_type_get(bridge, name)` - Lookup type by name
  - `handle_type_create(bridge, name)` - Create empty struct
  - `handle_type_apply(bridge, address, type_name)` - Set data type at address
- Modify `src/daemon/queue.rs`: Add match arms for TypeCommands
- New `src/ghidra/scripts/types.py`:
  - `list_types()` - Iterate DataTypeManager
  - `get_type(name)` - Find type by name path
  - `create_type(name)` - Add StructureDataType
  - `apply_type(address, name)` - Use DataTypeManager.applyDataType
- New `tests/type_tests.rs`: E2E tests

**Code Changes**:

```diff
--- /dev/null
+++ b/src/daemon/handlers/types.rs
@@ -0,0 +1,105 @@
+//! Type operation handlers.
+
+use anyhow::{Context, Result};
+use serde_json::json;
+use crate::ghidra::bridge::GhidraBridge;
+
+pub async fn handle_type_list(bridge: &mut GhidraBridge) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "type_list",
+        None
+    ).context("Failed to list types")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to list types".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_type_get(
+    bridge: &mut GhidraBridge,
+    name: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "type_get",
+        Some(json!({"name": name}))
+    ).context("Failed to get type")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to get type".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_type_create(
+    bridge: &mut GhidraBridge,
+    name: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "type_create",
+        Some(json!({"name": name}))
+    ).context("Failed to create type")?;
+
+    if response.status == "success" {
+        Ok(json!({"status": "created", "name": name}).to_string())
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to create type".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_type_apply(
+    bridge: &mut GhidraBridge,
+    address: &str,
+    type_name: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "type_apply",
+        Some(json!({
+            "address": address,
+            "type_name": type_name
+        }))
+    ).context("Failed to apply type")?;
+
+    if response.status == "success" {
+        Ok(json!({"status": "applied", "address": address, "type": type_name}).to_string())
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to apply type".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+}
```

```diff
--- a/src/daemon/queue.rs
+++ b/src/daemon/queue.rs
@@ -232,6 +232,27 @@ async fn execute_command(
                 },
             };
         },
+        Commands::Type(type_cmd) => {
+            use crate::cli::TypeCommands;
+            let mut bridge_guard = bridge.lock().await;
+            let bridge_ref = bridge_guard.as_mut()
+                .ok_or_else(|| anyhow::anyhow!("Bridge not initialized"))?;
+
+            if !bridge_ref.is_running() {
+                anyhow::bail!("Bridge is not running");
+            }
+
+            return match type_cmd {
+                TypeCommands::List(_) => {
+                    handlers::types::handle_type_list(bridge_ref).await
+                },
+                TypeCommands::Get(args) => {
+                    handlers::types::handle_type_get(bridge_ref, &args.name).await
+                },
+                TypeCommands::Create(args) => {
+                    handlers::types::handle_type_create(bridge_ref, &args.definition).await
+                },
+                TypeCommands::Apply(args) => {
+                    handlers::types::handle_type_apply(bridge_ref, &args.address, &args.type_name).await
+                },
+            };
+        },
         Commands::Decompile(decompile_args) => (
             "decompile",
             Some(json!({
```

```diff
--- /dev/null
+++ b/src/ghidra/scripts/types.py
@@ -0,0 +1,126 @@
+# Type operations script
+# @category CLI
+
+import sys
+import json
+
+def list_types():
+    """List all defined types in the program."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    data_type_manager = currentProgram.getDataTypeManager()
+    types = []
+
+    for data_type in data_type_manager.getAllDataTypes():
+        type_data = {
+            "name": data_type.getName(),
+            "path": data_type.getPathName(),
+            "category": data_type.getCategoryPath().toString(),
+            "size": data_type.getLength()
+        }
+        types.append(type_data)
+
+    return {"types": types, "count": len(types)}
+
+def get_type(type_name):
+    """Get type definition by name."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    data_type_manager = currentProgram.getDataTypeManager()
+
+    data_type = data_type_manager.getDataType(type_name)
+    if data_type is None:
+        for dt in data_type_manager.getAllDataTypes():
+            if dt.getName() == type_name:
+                data_type = dt
+                break
+
+    if data_type is None:
+        return {"error": "Type not found: " + type_name}
+
+    type_info = {
+        "name": data_type.getName(),
+        "path": data_type.getPathName(),
+        "category": data_type.getCategoryPath().toString(),
+        "size": data_type.getLength(),
+        "description": data_type.getDescription()
+    }
+
+    from ghidra.program.model.data import Structure, Union
+    if isinstance(data_type, Structure) or isinstance(data_type, Union):
+        components = []
+        for component in data_type.getComponents():
+            components.append({
+                "name": component.getFieldName(),
+                "type": component.getDataType().getName(),
+                "offset": component.getOffset(),
+                "size": component.getLength()
+            })
+        type_info["components"] = components
+
+    return type_info
+
+def create_type(type_name):
+    """Create a new empty struct type."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    try:
+        from ghidra.program.model.data import StructureDataType
+        data_type_manager = currentProgram.getDataTypeManager()
+
+        new_struct = StructureDataType(type_name, 0)
+        data_type_manager.addDataType(new_struct, None)
+
+        return {"status": "created", "name": type_name}
+    except Exception as e:
+        return {"error": "Failed to create type: " + str(e)}
+
+def apply_type(address_str, type_name):
+    """Apply a type to a specific address."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    try:
+        addr = currentProgram.getAddressFactory().getAddress(address_str)
+        if addr is None:
+            return {"error": "Invalid address: " + address_str}
+
+        data_type_manager = currentProgram.getDataTypeManager()
+        data_type = data_type_manager.getDataType(type_name)
+
+        if data_type is None:
+            for dt in data_type_manager.getAllDataTypes():
+                if dt.getName() == type_name:
+                    data_type = dt
+                    break
+
+        if data_type is None:
+            return {"error": "Type not found: " + type_name}
+
+        listing = currentProgram.getListing()
+        listing.createData(addr, data_type)
+
+        return {"status": "applied", "address": address_str, "type": type_name}
+    except Exception as e:
+        return {"error": "Failed to apply type: " + str(e)}
+
+if __name__ == "__main__":
+    try:
+        if len(args) < 1:
+            print("---GHIDRA_CLI_START---")
+            print(json.dumps({"error": "No command specified"}))
+            print("---GHIDRA_CLI_END---")
+            sys.exit(1)
+
+        command = args[0]
+
+        if command == "list":
+            result = list_types()
+        elif command == "get":
+            result = get_type(args[1] if len(args) > 1 else None)
+        elif command == "create":
+            result = create_type(args[1] if len(args) > 1 else None)
+        elif command == "apply":
+            result = apply_type(args[1] if len(args) > 1 else None, args[2] if len(args) > 2 else None)
+        else:
+            result = {"error": "Unknown command: " + command}
+
+        print("---GHIDRA_CLI_START---")
+        print(json.dumps(result))
+        print("---GHIDRA_CLI_END---")
+    except Exception as e:
+        print("---GHIDRA_CLI_START---")
+        print(json.dumps({"error": str(e)}))
+        print("---GHIDRA_CLI_END---")
```

```diff
--- /dev/null
+++ b/tests/type_tests.rs
@@ -0,0 +1,116 @@
+//! Tests for type operations.
+
+use assert_cmd::Command;
+use predicates::prelude::*;
+use serial_test::serial;
+
+#[macro_use]
+mod common;
+use common::{ensure_test_project, DaemonTestHarness};
+
+const TEST_PROJECT: &str = "type-test";
+const TEST_PROGRAM: &str = "sample_binary";
+
+#[test]
+#[serial]
+fn test_type_list() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("type")
+        .arg("list")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("types"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_type_get_primitive() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("type")
+        .arg("get")
+        .arg("int")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("size"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_type_create() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("type")
+        .arg("create")
+        .arg("MyTestStruct")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_type_apply() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("type")
+        .arg("apply")
+        .arg("0x1000")
+        .arg("int")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_type_get_nonexistent() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("type")
+        .arg("get")
+        .arg("NonexistentType12345")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .failure();
+
+    drop(harness);
+}
```

---

### Milestone 4: Comment Operations

**Files**:
- `src/daemon/handlers/comments.rs` (new)
- `src/daemon/queue.rs` (modify)
- `src/ghidra/scripts/comments.py` (new)
- `tests/comment_tests.rs` (new)

**Flags**: `conformance`

**Requirements**:
- `comment list` - List all comments
- `comment get <address>` - Get comments at address
- `comment set <address> <text>` - Set/update comment
- `comment delete <address>` - Remove comment

**Acceptance Criteria**:
- `ghidra comment list` returns JSON array with address, type, text
- `ghidra comment get 0x1000` returns comments at address (may be multiple types)
- `ghidra comment set 0x1000 "my note"` sets EOL comment
- `ghidra comment delete 0x1000` removes all comments at address
- Comment types supported: EOL, PRE, POST, PLATE

**Tests**:
- **Test files**: `tests/comment_tests.rs`
- **Test type**: integration
- **Backing**: user-specified
- **Scenarios**:
  - Normal: set comment, get it back, list all, delete
  - Edge: get address with no comments, set empty string
  - Error: invalid address format

**Code Intent**:
- New `src/daemon/handlers/comments.rs`:
  - `handle_comment_list(bridge)` - List all comments in program
  - `handle_comment_get(bridge, address)` - Get comments at address
  - `handle_comment_set(bridge, address, text)` - Set EOL comment
  - `handle_comment_delete(bridge, address)` - Clear comments
- Modify `src/daemon/queue.rs`: Add CommentCommands routing
- New `src/ghidra/scripts/comments.py`:
  - `list_comments()` - Iterate CodeUnitIterator for comments
  - `get_comments(address)` - Get all comment types at address
  - `set_comment(address, text)` - setComment(CodeUnit.EOL_COMMENT)
  - `delete_comment(address)` - Clear all comment types
- New `tests/comment_tests.rs`: E2E tests

**Code Changes**:

```diff
--- a/src/daemon/handlers/mod.rs
+++ b/src/daemon/handlers/mod.rs
@@ -3,3 +3,4 @@
 pub mod program;
 pub mod symbols;
 pub mod types;
+pub mod comments;
```

```diff
--- /dev/null
+++ b/src/daemon/handlers/comments.rs
@@ -0,0 +1,105 @@
+//! Comment operation handlers.
+
+use anyhow::{Context, Result};
+use serde_json::json;
+use crate::ghidra::bridge::GhidraBridge;
+
+pub async fn handle_comment_list(bridge: &mut GhidraBridge) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "comment_list",
+        None
+    ).context("Failed to list comments")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to list comments".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_comment_get(
+    bridge: &mut GhidraBridge,
+    address: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "comment_get",
+        Some(json!({"address": address}))
+    ).context("Failed to get comment")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to get comment".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_comment_set(
+    bridge: &mut GhidraBridge,
+    address: &str,
+    text: &str,
+    comment_type: Option<&str>
+) -> Result<String> {
+    let mut args = json!({
+        "address": address,
+        "text": text
+    });
+
+    if let Some(ctype) = comment_type {
+        args["comment_type"] = json!(ctype);
+    }
+
+    let response = bridge.send_command::<serde_json::Value>(
+        "comment_set",
+        Some(args)
+    ).context("Failed to set comment")?;
+
+    if response.status == "success" {
+        Ok(json!({"status": "set", "address": address}).to_string())
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to set comment".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_comment_delete(
+    bridge: &mut GhidraBridge,
+    address: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "comment_delete",
+        Some(json!({"address": address}))
+    ).context("Failed to delete comment")?;
+
+    if response.status == "success" {
+        Ok(json!({"status": "deleted", "address": address}).to_string())
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to delete comment".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+}
+```

```diff
--- a/src/daemon/queue.rs
+++ b/src/daemon/queue.rs
@@ -276,6 +276,24 @@ async fn execute_command(
             };
         },
+        Commands::Comment(comment_cmd) => {
+            use crate::cli::CommentCommands;
+            let mut bridge_guard = bridge.lock().await;
+            let bridge_ref = bridge_guard.as_mut()
+                .ok_or_else(|| anyhow::anyhow!("Bridge not initialized"))?;
+
+            if !bridge_ref.is_running() {
+                anyhow::bail!("Bridge is not running");
+            }
+
+            return match comment_cmd {
+                CommentCommands::List(_) => handlers::comments::handle_comment_list(bridge_ref).await,
+                CommentCommands::Get(args) => handlers::comments::handle_comment_get(bridge_ref, &args.address).await,
+                CommentCommands::Set(args) => {
+                    handlers::comments::handle_comment_set(bridge_ref, &args.address, &args.text, args.comment_type.as_deref()).await
+                },
+                CommentCommands::Delete(args) => handlers::comments::handle_comment_delete(bridge_ref, &args.address).await,
+            };
+        },
         Commands::Decompile(decompile_args) => (
             "decompile",
             Some(json!({
```

```diff
--- /dev/null
+++ b/src/ghidra/scripts/comments.py
@@ -0,0 +1,144 @@
+# Comment operations script
+# @category CLI
+
+import sys
+import json
+
+def list_comments():
+    """List all comments in the program."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    listing = currentProgram.getListing()
+    comments = []
+
+    code_unit_iter = listing.getCommentAddressIterator(currentProgram.getMinAddress(), currentProgram.getMaxAddress(), True)
+
+    for addr in code_unit_iter:
+        code_unit = listing.getCodeUnitAt(addr)
+        if code_unit is None:
+            continue
+
+        from ghidra.program.model.listing import CodeUnit
+
+        comment_types = [
+            ("EOL", CodeUnit.EOL_COMMENT),
+            ("PRE", CodeUnit.PRE_COMMENT),
+            ("POST", CodeUnit.POST_COMMENT),
+            ("PLATE", CodeUnit.PLATE_COMMENT)
+        ]
+
+        for comment_name, comment_type in comment_types:
+            text = code_unit.getComment(comment_type)
+            if text:
+                comments.append({
+                    "address": str(addr),
+                    "type": comment_name,
+                    "text": text
+                })
+
+    return {"comments": comments, "count": len(comments)}
+
+def get_comments(address_str):
+    """Get comments at a specific address."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    try:
+        addr = currentProgram.getAddressFactory().getAddress(address_str)
+        if addr is None:
+            return {"error": "Invalid address: " + address_str}
+
+        listing = currentProgram.getListing()
+        code_unit = listing.getCodeUnitAt(addr)
+
+        if code_unit is None:
+            return {"error": "No code unit at address: " + address_str}
+
+        from ghidra.program.model.listing import CodeUnit
+
+        comments = []
+        comment_types = [
+            ("EOL", CodeUnit.EOL_COMMENT),
+            ("PRE", CodeUnit.PRE_COMMENT),
+            ("POST", CodeUnit.POST_COMMENT),
+            ("PLATE", CodeUnit.PLATE_COMMENT)
+        ]
+
+        for comment_name, comment_type in comment_types:
+            text = code_unit.getComment(comment_type)
+            if text:
+                comments.append({
+                    "type": comment_name,
+                    "text": text
+                })
+
+        return {"address": address_str, "comments": comments}
+    except Exception as e:
+        return {"error": "Failed to get comments: " + str(e)}
+
+def set_comment(address_str, text, comment_type_str):
+    """Set a comment at a specific address."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    try:
+        addr = currentProgram.getAddressFactory().getAddress(address_str)
+        if addr is None:
+            return {"error": "Invalid address: " + address_str}
+
+        listing = currentProgram.getListing()
+        from ghidra.program.model.listing import CodeUnit
+
+        valid_types = {"EOL", "PRE", "POST", "PLATE"}
+        if comment_type_str not in valid_types:
+            return {"error": "Invalid comment type: " + comment_type_str + ". Must be one of: EOL, PRE, POST, PLATE"}
+
+        comment_type = CodeUnit.EOL_COMMENT
+        if comment_type_str == "PRE":
+            comment_type = CodeUnit.PRE_COMMENT
+        elif comment_type_str == "POST":
+            comment_type = CodeUnit.POST_COMMENT
+        elif comment_type_str == "PLATE":
+            comment_type = CodeUnit.PLATE_COMMENT
+
+        listing.setComment(addr, comment_type, text)
+        return {"status": "set", "address": address_str}
+    except Exception as e:
+        return {"error": "Failed to set comment: " + str(e)}
+
+def delete_comment(address_str):
+    """Delete all comments at a specific address."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    try:
+        addr = currentProgram.getAddressFactory().getAddress(address_str)
+        if addr is None:
+            return {"error": "Invalid address: " + address_str}
+
+        listing = currentProgram.getListing()
+        from ghidra.program.model.listing import CodeUnit
+
+        listing.setComment(addr, CodeUnit.EOL_COMMENT, None)
+        listing.setComment(addr, CodeUnit.PRE_COMMENT, None)
+        listing.setComment(addr, CodeUnit.POST_COMMENT, None)
+        listing.setComment(addr, CodeUnit.PLATE_COMMENT, None)
+
+        return {"status": "deleted", "address": address_str}
+    except Exception as e:
+        return {"error": "Failed to delete comment: " + str(e)}
+
+if __name__ == "__main__":
+    try:
+        if len(args) < 1:
+            print("---GHIDRA_CLI_START---")
+            print(json.dumps({"error": "No command specified"}))
+            print("---GHIDRA_CLI_END---")
+            sys.exit(1)
+
+        command = args[0]
+
+        if command == "list":
+            result = list_comments()
+        elif command == "get":
+            result = get_comments(args[1] if len(args) > 1 else None)
+        elif command == "set":
+            text = args[2] if len(args) > 2 else ""
+            comment_type = args[3] if len(args) > 3 else "EOL"
+            result = set_comment(args[1] if len(args) > 1 else None, text, comment_type)
+        elif command == "delete":
+            result = delete_comment(args[1] if len(args) > 1 else None)
+        else:
+            result = {"error": "Unknown command: " + command}
+
+        print("---GHIDRA_CLI_START---")
+        print(json.dumps(result))
+        print("---GHIDRA_CLI_END---")
+    except Exception as e:
+        print("---GHIDRA_CLI_START---")
+        print(json.dumps({"error": str(e)}))
+        print("---GHIDRA_CLI_END---")
+```

```diff
--- /dev/null
+++ b/tests/comment_tests.rs
@@ -0,0 +1,116 @@
+//! Tests for comment operations.
+
+use assert_cmd::Command;
+use predicates::prelude::*;
+use serial_test::serial;
+
+#[macro_use]
+mod common;
+use common::{ensure_test_project, DaemonTestHarness};
+
+const TEST_PROJECT: &str = "comment-test";
+const TEST_PROGRAM: &str = "sample_binary";
+
+#[test]
+#[serial]
+fn test_comment_set_and_get() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("comment")
+        .arg("set")
+        .arg("0x1000")
+        .arg("test comment")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("comment")
+        .arg("get")
+        .arg("0x1000")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("test comment"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_comment_list() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("comment")
+        .arg("set")
+        .arg("0x2000")
+        .arg("another comment")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("comment")
+        .arg("list")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("comments"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_comment_delete() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("comment")
+        .arg("set")
+        .arg("0x3000")
+        .arg("to be deleted")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("comment")
+        .arg("delete")
+        .arg("0x3000")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+
+    drop(harness);
+}
+```

---

### Milestone 5: Graph Operations

**Files**:
- `src/daemon/handlers/graph.rs` (new)
- `src/daemon/queue.rs` (modify)
- `src/ghidra/scripts/graph.py` (new)
- `tests/graph_tests.rs` (new)

**Flags**: `performance`, `complex-algorithm`

**Requirements**:
- `graph calls` - Full call graph
- `graph callers <function>` - Functions that call target
- `graph callees <function>` - Functions called by target
- `graph export <format>` - Export to DOT/JSON

**Acceptance Criteria**:
- `ghidra graph calls` returns JSON call graph (nodes + edges)
- `ghidra graph callers main` returns list of caller functions
- `ghidra graph callees main` returns list of called functions
- `ghidra graph export dot` outputs DOT format to stdout
- Graph operations respect --limit for large binaries

**Tests**:
- **Test files**: `tests/graph_tests.rs`
- **Test type**: integration
- **Backing**: user-specified
- **Scenarios**:
  - Normal: get callers/callees of main, export to DOT
  - Edge: function with no callers, function with no callees
  - Error: non-existent function name

**Code Intent**:
- New `src/daemon/handlers/graph.rs`:
  - `handle_graph_calls(bridge, limit)` - Full call graph
  - `handle_graph_callers(bridge, function, depth)` - Callers of function
  - `handle_graph_callees(bridge, function, depth)` - Callees of function
  - `handle_graph_export(bridge, format)` - Export to format
- Modify `src/daemon/queue.rs`: Add GraphCommands routing
- New `src/ghidra/scripts/graph.py`:
  - `get_call_graph(limit)` - Build graph from ReferenceManager
  - `get_callers(function, depth)` - Traverse incoming references
  - `get_callees(function, depth)` - Traverse outgoing references
  - `export_dot(graph)` - Format as DOT
  - `export_json(graph)` - Format as JSON
- New `tests/graph_tests.rs`: E2E tests

**Code Changes**:

```diff
--- a/src/daemon/handlers/mod.rs
+++ b/src/daemon/handlers/mod.rs
@@ -4,3 +4,4 @@ pub mod program;
 pub mod symbols;
 pub mod types;
 pub mod comments;
+pub mod graph;
```

```diff
--- /dev/null
+++ b/src/daemon/handlers/graph.rs
@@ -0,0 +1,125 @@
+//! Graph operation handlers.
+
+use anyhow::{Context, Result};
+use serde_json::json;
+use crate::ghidra::bridge::GhidraBridge;
+
+pub async fn handle_graph_calls(
+    bridge: &mut GhidraBridge,
+    limit: Option<usize>
+) -> Result<String> {
+    let args = if let Some(lim) = limit {
+        Some(json!({"limit": lim}))
+    } else {
+        None
+    };
+
+    let response = bridge.send_command::<serde_json::Value>(
+        "graph_calls",
+        args
+    ).context("Failed to get call graph")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to get call graph".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_graph_callers(
+    bridge: &mut GhidraBridge,
+    function: &str,
+    depth: Option<usize>
+) -> Result<String> {
+    let mut args = json!({"function": function});
+    if let Some(d) = depth {
+        args["depth"] = json!(d);
+    }
+
+    let response = bridge.send_command::<serde_json::Value>(
+        "graph_callers",
+        Some(args)
+    ).context("Failed to get callers")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to get callers".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_graph_callees(
+    bridge: &mut GhidraBridge,
+    function: &str,
+    depth: Option<usize>
+) -> Result<String> {
+    let mut args = json!({"function": function});
+    if let Some(d) = depth {
+        args["depth"] = json!(d);
+    }
+
+    let response = bridge.send_command::<serde_json::Value>(
+        "graph_callees",
+        Some(args)
+    ).context("Failed to get callees")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to get callees".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+pub async fn handle_graph_export(
+    bridge: &mut GhidraBridge,
+    format: &str
+) -> Result<String> {
+    let response = bridge.send_command::<serde_json::Value>(
+        "graph_export",
+        Some(json!({"format": format}))
+    ).context("Failed to export graph")?;
+
+    if response.status == "success" {
+        let data = response.data.unwrap_or(json!({}));
+        serde_json::to_string_pretty(&data)
+            .context("Failed to serialize response")
+    } else {
+        let message = response.message.unwrap_or_else(|| "Failed to export graph".to_string());
+        anyhow::bail!("{}", message)
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+}
+```

```diff
--- a/src/daemon/queue.rs
+++ b/src/daemon/queue.rs
@@ -294,6 +294,27 @@ async fn execute_command(
                 CommentCommands::Delete(args) => handlers::comments::handle_comment_delete(bridge_ref, &args.address).await,
             };
         },
+        Commands::Graph(graph_cmd) => {
+            use crate::cli::GraphCommands;
+            let mut bridge_guard = bridge.lock().await;
+            let bridge_ref = bridge_guard.as_mut()
+                .ok_or_else(|| anyhow::anyhow!("Bridge not initialized"))?;
+
+            if !bridge_ref.is_running() {
+                anyhow::bail!("Bridge is not running");
+            }
+
+            return match graph_cmd {
+                GraphCommands::Calls(opts) => {
+                    handlers::graph::handle_graph_calls(bridge_ref, opts.limit).await
+                },
+                GraphCommands::Callers(args) => {
+                    handlers::graph::handle_graph_callers(bridge_ref, &args.function, args.depth).await
+                },
+                GraphCommands::Callees(args) => {
+                    handlers::graph::handle_graph_callees(bridge_ref, &args.function, args.depth).await
+                },
+                GraphCommands::Export(args) => {
+                    handlers::graph::handle_graph_export(bridge_ref, &args.format).await
+                },
+            };
+        },
         Commands::Decompile(decompile_args) => (
             "decompile",
             Some(json!({
```

```diff
--- /dev/null
+++ b/src/ghidra/scripts/graph.py
@@ -0,0 +1,209 @@
+# Graph operations script
+# @category CLI
+
+import sys
+import json
+
+def get_call_graph(limit):
+    """Build full call graph."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    function_manager = currentProgram.getFunctionManager()
+    reference_manager = currentProgram.getReferenceManager()
+
+    nodes = []
+    edges = []
+    count = 0
+
+    for func in function_manager.getFunctions(True):
+        if limit and count >= limit:
+            break
+
+        func_addr = str(func.getEntryPoint())
+        nodes.append({
+            "id": func_addr,
+            "name": func.getName(),
+            "address": func_addr
+        })
+
+        from ghidra.program.model.symbol import RefType
+        refs = reference_manager.getReferencesFrom(func.getEntryPoint())
+        for ref in refs:
+            if ref.getReferenceType().isCall():
+                target_addr = ref.getToAddress()
+                target_func = function_manager.getFunctionAt(target_addr)
+                if target_func:
+                    edges.append({
+                        "from": func_addr,
+                        "to": str(target_addr),
+                        "type": "call"
+                    })
+
+        count += 1
+
+    return {"nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}
+
+def get_callers(function_name, depth):
+    """Get functions that call the specified function."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    function_manager = currentProgram.getFunctionManager()
+    reference_manager = currentProgram.getReferenceManager()
+
+    target_func = None
+    if function_name.startswith("0x") or all(c in "0123456789abcdefABCDEF" for c in function_name):
+        addr = currentProgram.getAddressFactory().getAddress(function_name)
+        if addr:
+            target_func = function_manager.getFunctionAt(addr)
+    else:
+        for func in function_manager.getFunctions(True):
+            if func.getName() == function_name:
+                target_func = func
+                break
+
+    if not target_func:
+        return {"error": "Function not found: " + function_name}
+
+    callers = []
+    visited = set()
+
+    def find_callers(func, current_depth):
+        if depth and current_depth >= depth:
+            return
+        if str(func.getEntryPoint()) in visited:
+            return
+
+        visited.add(str(func.getEntryPoint()))
+
+        from ghidra.program.model.symbol import RefType
+        refs = reference_manager.getReferencesTo(func.getEntryPoint())
+
+        for ref in refs:
+            if ref.getReferenceType().isCall():
+                from_addr = ref.getFromAddress()
+                caller_func = function_manager.getFunctionContaining(from_addr)
+                if caller_func:
+                    caller_info = {
+                        "name": caller_func.getName(),
+                        "address": str(caller_func.getEntryPoint()),
+                        "call_site": str(from_addr),
+                        "depth": current_depth
+                    }
+                    callers.append(caller_info)
+
+                    if depth is None or current_depth + 1 < depth:
+                        find_callers(caller_func, current_depth + 1)
+
+    find_callers(target_func, 0)
+
+    return {"function": function_name, "callers": callers, "count": len(callers)}
+
+def get_callees(function_name, depth):
+    """Get functions called by the specified function."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    function_manager = currentProgram.getFunctionManager()
+    reference_manager = currentProgram.getReferenceManager()
+
+    target_func = None
+    if function_name.startswith("0x") or all(c in "0123456789abcdefABCDEF" for c in function_name):
+        addr = currentProgram.getAddressFactory().getAddress(function_name)
+        if addr:
+            target_func = function_manager.getFunctionAt(addr)
+    else:
+        for func in function_manager.getFunctions(True):
+            if func.getName() == function_name:
+                target_func = func
+                break
+
+    if not target_func:
+        return {"error": "Function not found: " + function_name}
+
+    callees = []
+    visited = set()
+
+    def find_callees(func, current_depth):
+        if depth and current_depth >= depth:
+            return
+        if str(func.getEntryPoint()) in visited:
+            return
+
+        visited.add(str(func.getEntryPoint()))
+
+        from ghidra.program.model.symbol import RefType
+        refs = reference_manager.getReferencesFrom(func.getEntryPoint())
+
+        for ref in refs:
+            if ref.getReferenceType().isCall():
+                to_addr = ref.getToAddress()
+                callee_func = function_manager.getFunctionAt(to_addr)
+                if callee_func:
+                    callee_info = {
+                        "name": callee_func.getName(),
+                        "address": str(callee_func.getEntryPoint()),
+                        "call_site": str(ref.getFromAddress()),
+                        "depth": current_depth
+                    }
+                    callees.append(callee_info)
+
+                    if depth is None or current_depth + 1 < depth:
+                        find_callees(callee_func, current_depth + 1)
+
+    find_callees(target_func, 0)
+
+    return {"function": function_name, "callees": callees, "count": len(callees)}
+
+def export_graph(export_format):
+    """Export call graph in specified format."""
+    if currentProgram is None:
+        return {"error": "No program loaded"}
+
+    graph_data = get_call_graph(None)
+    if "error" in graph_data:
+        return graph_data
+
+    if export_format == "json":
+        return graph_data
+    elif export_format == "dot":
+        lines = ["digraph CallGraph {"]
+        lines.append('  rankdir=LR;')
+        lines.append('  node [shape=box];')
+
+        for node in graph_data["nodes"]:
+            node_id = node["id"].replace(":", "_")
+            label = node["name"]
+            lines.append('  "{}" [label="{}"];'.format(node_id, label))
+
+        for edge in graph_data["edges"]:
+            from_id = edge["from"].replace(":", "_")
+            to_id = edge["to"].replace(":", "_")
+            lines.append('  "{}" -> "{}";'.format(from_id, to_id))
+
+        lines.append("}")
+        return {"format": "dot", "output": "\n".join(lines)}
+    else:
+        return {"error": "Unsupported format: " + export_format}
+
+if __name__ == "__main__":
+    try:
+        if len(args) < 1:
+            print("---GHIDRA_CLI_START---")
+            print(json.dumps({"error": "No command specified"}))
+            print("---GHIDRA_CLI_END---")
+            sys.exit(1)
+
+        command = args[0]
+
+        if command == "calls":
+            limit = int(args[1]) if len(args) > 1 and args[1] else None
+            result = get_call_graph(limit)
+        elif command == "callers":
+            func_name = args[1] if len(args) > 1 else None
+            depth = int(args[2]) if len(args) > 2 and args[2] else None
+            result = get_callers(func_name, depth)
+        elif command == "callees":
+            func_name = args[1] if len(args) > 1 else None
+            depth = int(args[2]) if len(args) > 2 and args[2] else None
+            result = get_callees(func_name, depth)
+        elif command == "export":
+            fmt = args[1] if len(args) > 1 else "json"
+            result = export_graph(fmt)
+        else:
+            result = {"error": "Unknown command: " + command}
+
+        print("---GHIDRA_CLI_START---")
+        print(json.dumps(result))
+        print("---GHIDRA_CLI_END---")
+    except Exception as e:
+        print("---GHIDRA_CLI_START---")
+        print(json.dumps({"error": str(e)}))
+        print("---GHIDRA_CLI_END---")
+```

```diff
--- /dev/null
+++ b/tests/graph_tests.rs
@@ -0,0 +1,104 @@
+//! Tests for graph operations.
+
+use assert_cmd::Command;
+use predicates::prelude::*;
+use serial_test::serial;
+
+#[macro_use]
+mod common;
+use common::{ensure_test_project, DaemonTestHarness};
+
+const TEST_PROJECT: &str = "graph-test";
+const TEST_PROGRAM: &str = "sample_binary";
+
+#[test]
+#[serial]
+fn test_graph_calls() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("graph")
+        .arg("calls")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("nodes"))
+        .stdout(predicate::str::contains("edges"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_graph_callers() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("graph")
+        .arg("callers")
+        .arg("main")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("callers"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_graph_callees() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("graph")
+        .arg("callees")
+        .arg("main")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("callees"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_graph_export_dot() {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("graph")
+        .arg("export")
+        .arg("dot")
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("digraph"));
+
+    drop(harness);
+}
+```

---

### Milestone 6: Find/Search Operations

**Files**:
- `src/daemon/handlers/find.rs` (new)
- `src/daemon/queue.rs` (modify)
- `src/ghidra/scripts/find.py` (new)
- `tests/find_tests.rs` (new)

**Flags**: `performance`

**Requirements**:
- `find string <pattern>` - Find string references
- `find bytes <hex>` - Find byte patterns
- `find function <pattern>` - Find functions by name pattern
- `find calls <function>` - Find all calls to function
- `find crypto` - Find potential crypto constants
- `find interesting` - Heuristic interesting function detection

**Acceptance Criteria**:
- `ghidra find string "password"` returns addresses containing string
- `ghidra find bytes deadbeef` returns matching addresses
- `ghidra find function "main*"` returns functions matching glob
- `ghidra find calls printf` returns call sites
- `ghidra find crypto` returns addresses with crypto constants (AES S-box, etc.)
- `ghidra find interesting` returns functions with suspicious patterns

**Tests**:
- **Test files**: `tests/find_tests.rs`
- **Test type**: integration
- **Backing**: user-specified
- **Scenarios**:
  - Normal: find known string, find known bytes
  - Edge: pattern with no matches, regex pattern
  - Error: invalid regex

**Code Intent**:
- New `src/daemon/handlers/find.rs`:
  - `handle_find_string(bridge, pattern)` - String search
  - `handle_find_bytes(bridge, hex)` - Byte pattern search
  - `handle_find_function(bridge, pattern)` - Function name glob
  - `handle_find_calls(bridge, function)` - Call site search
  - `handle_find_crypto(bridge)` - Crypto constant detection
  - `handle_find_interesting(bridge)` - Heuristic detection
- New `src/ghidra/scripts/find.py`:
  - `find_strings(pattern)` - Search DefinedStrings
  - `find_bytes(pattern)` - Memory.findBytes
  - `find_functions(pattern)` - FunctionManager glob match
  - `find_calls(function)` - Reference search
  - `find_crypto()` - Known crypto constant table lookup
  - `find_interesting()` - Heuristics (large functions, many xrefs, etc.)
- New `tests/find_tests.rs`: E2E tests


**Code Changes**: [See implementation guidance below - follows M1-M5 patterns]

---

### Milestone 7: Diff Operations

**Files**:
- `src/daemon/handlers/diff.rs` (new)
- `src/daemon/queue.rs` (modify)
- `src/ghidra/scripts/diff.py` (new)
- `tests/diff_tests.rs` (new)

**Flags**: `complex-algorithm`

**Requirements**:
- `diff programs <prog1> <prog2>` - Compare two programs
- `diff functions <func1> <func2>` - Compare two functions

**Acceptance Criteria**:
- `ghidra diff programs prog1 prog2` returns structural differences
- `ghidra diff functions main main2` returns decompilation diff
- Diff output includes added/removed/changed sections

**Tests**:
- **Test files**: `tests/diff_tests.rs`
- **Test type**: integration
- **Backing**: user-specified
- **Scenarios**:
  - Normal: diff two versions of same binary
  - Edge: identical programs, completely different programs
  - Error: non-existent program name

**Code Intent**:
- New `src/daemon/handlers/diff.rs`:
  - `handle_diff_programs(bridge, prog1, prog2)` - Program comparison
  - `handle_diff_functions(bridge, func1, func2)` - Function comparison
- New `src/ghidra/scripts/diff.py`:
  - `diff_programs(prog1, prog2)` - Compare program structures
  - `diff_functions(func1, func2)` - Compare decompiled output
- New `tests/diff_tests.rs`: E2E tests

**Code Changes**: (Developer fills after plan approval)

---

### Milestone 8: Patch Operations

**Files**:
- `src/daemon/handlers/patch.rs` (new)
- `src/daemon/queue.rs` (modify)
- `src/ghidra/scripts/patch.py` (new)
- `tests/patch_tests.rs` (new)

**Flags**: `security`, `error-handling`

**Requirements**:
- `patch bytes <address> <hex>` - Patch bytes at address
- `patch nop <address>` - NOP out instruction at address
- `patch export --output <file>` - Export patched binary

**Acceptance Criteria**:
- `ghidra patch bytes 0x1000 90909090` patches 4 NOPs
- `ghidra patch nop 0x1000` NOPs the instruction at address
- `ghidra patch export --output patched.bin` writes modified binary
- Patches persist in project until export

**Tests**:
- **Test files**: `tests/patch_tests.rs`
- **Test type**: integration
- **Backing**: user-specified
- **Scenarios**:
  - Normal: patch bytes, verify with memory read, export
  - Edge: patch at function boundary
  - Error: patch in unmapped region

**Code Intent**:
- New `src/daemon/handlers/patch.rs`:
  - `handle_patch_bytes(bridge, address, hex)` - Write patch bytes
  - `handle_patch_nop(bridge, address)` - NOP instruction
  - `handle_patch_export(bridge, output)` - Export binary
- New `src/ghidra/scripts/patch.py`:
  - `patch_bytes(address, bytes)` - Memory modification
  - `patch_nop(address)` - Get instruction size, write NOPs
  - `export_binary(output)` - Use Exporter
- New `tests/patch_tests.rs`: E2E tests

**Code Changes**: (Developer fills after plan approval)

---

### Milestone 9: Script Execution

**Files**:
- `src/daemon/handlers/script.rs` (new)
- `src/daemon/queue.rs` (modify)
- `tests/script_tests.rs` (new)

**Flags**: `security`, `error-handling`

**Requirements**:
- `script run <path>` - Run user script
- `script python <path>` - Run Python script
- `script java <path>` - Run Java script
- `script list` - List available scripts

**Acceptance Criteria**:
- `ghidra script run user.py` executes script, returns output
- `ghidra script python user.py` explicitly runs as Python
- `ghidra script java UserScript.java` runs as Java
- `ghidra script list` shows bundled and user scripts
- Script output captured and returned as JSON

**Tests**:
- **Test files**: `tests/script_tests.rs`
- **Test type**: integration
- **Backing**: user-specified
- **Scenarios**:
  - Normal: run simple Python script, capture output
  - Edge: script with arguments, script with long output
  - Error: non-existent script, script error

**Code Intent**:
- New `src/daemon/handlers/script.rs`:
  - `handle_script_run(bridge, path, args)` - Auto-detect and run
  - `handle_script_python(bridge, path, args)` - Force Python
  - `handle_script_java(bridge, path, args)` - Force Java
  - `handle_script_list(bridge)` - List available scripts
- Modify `src/daemon/queue.rs`: Add ScriptCommands routing
- Scripts executed via existing bridge mechanism
- New `tests/script_tests.rs`: E2E tests with test script fixtures

**Code Changes**: (Developer fills after plan approval)

---

### Milestone 10: Disasm Command

**Files**:
- `src/daemon/handlers/disasm.rs` (new)
- `src/daemon/queue.rs` (modify)
- `src/ghidra/scripts/disasm.py` (new)
- `tests/disasm_tests.rs` (new)

**Flags**: `conformance`

**Requirements**:
- `disasm <address>` - Disassemble at address
- `disasm <address> --instructions N` - Disassemble N instructions

**Acceptance Criteria**:
- `ghidra disasm 0x1000` returns disassembly starting at address
- `ghidra disasm 0x1000 --instructions 10` returns exactly 10 instructions
- Output includes address, bytes, mnemonic, operands

**Tests**:
- **Test files**: `tests/disasm_tests.rs`
- **Test type**: integration
- **Backing**: user-specified
- **Scenarios**:
  - Normal: disasm from main, disasm with limit
  - Edge: disasm at data, disasm past end
  - Error: invalid address

**Code Intent**:
- New `src/daemon/handlers/disasm.rs`:
  - `handle_disasm(bridge, address, count)` - Disassemble instructions
- New `src/ghidra/scripts/disasm.py`:
  - `disassemble(address, count)` - Use Listing.getInstructionAt, iterate
- New `tests/disasm_tests.rs`: E2E tests

**Code Changes**: (Developer fills after plan approval)

---

### Milestone 11: Batch Operations

**Files**:
- `src/daemon/handlers/batch.rs` (new)
- `src/daemon/queue.rs` (modify)
- `tests/batch_tests.rs` (new)

**Flags**: `error-handling`

**Requirements**:
- `batch <file>` - Execute batch file of commands

**Acceptance Criteria**:
- `ghidra batch commands.txt` executes each line as command
- Batch file format: one command per line
- Results returned as array of per-command results
- Errors in one command don't stop batch

**Tests**:
- **Test files**: `tests/batch_tests.rs`
- **Test type**: integration
- **Backing**: user-specified
- **Scenarios**:
  - Normal: batch with multiple queries
  - Edge: empty batch file, batch with comments (#)
  - Error: batch with invalid command (continues)

**Code Intent**:
- New `src/daemon/handlers/batch.rs`:
  - `handle_batch(daemon, file_path)` - Parse and execute batch
  - Each line parsed as CLI command, routed through normal dispatch
- New `tests/batch_tests.rs`: E2E tests with batch fixtures

**Code Changes**: (Developer fills after plan approval)

---

### Milestone 12: Stats Command

**Files**:
- `src/daemon/handlers/stats.rs` (new)
- `src/daemon/queue.rs` (modify)
- `src/ghidra/scripts/stats.py` (new)
- `tests/stats_tests.rs` (new)

**Flags**: `conformance`

**Requirements**:
- `stats` - Show program statistics

**Acceptance Criteria**:
- `ghidra stats` returns JSON with comprehensive program statistics
- Statistics include: function count, string count, import/export counts, memory size, section counts, data type counts
- Output format consistent with other commands

**Tests**:
- **Test files**: `tests/stats_tests.rs`
- **Test type**: integration
- **Backing**: user-specified
- **Scenarios**:
  - Normal: get stats for analyzed binary
  - Edge: stats for minimal binary with few functions
  - Error: stats when no program loaded

**Code Intent**:
- New `src/daemon/handlers/stats.rs`:
  - `handle_stats(bridge)` - Gather and return program statistics
- New `src/ghidra/scripts/stats.py`:
  - `get_stats()` - Collect statistics from FunctionManager, SymbolTable, Memory, etc.
- New `tests/stats_tests.rs`: E2E tests

**Code Changes**: (Developer fills after plan approval)

---

### Milestone 13: Documentation

**Delegated to**: @agent-technical-writer (mode: post-implementation)

**Source**: `## Invisible Knowledge` section of this plan

**Files**:
- `src/daemon/handlers/CLAUDE.md` (new)
- `src/daemon/handlers/README.md` (new)
- `src/ghidra/scripts/CLAUDE.md` (new)
- `CLAUDE.md` (update index)
- `README.md` (rewrite with getting started)

**Requirements**:
- CLAUDE.md files for new handler and script directories
- README.md with architecture diagrams from Invisible Knowledge
- Main README.md rewritten with quick-start guide

**Acceptance Criteria**:
- CLAUDE.md is tabular index only
- README.md contains architecture from Invisible Knowledge
- Main README has installation, quick-start, command reference

## Milestone Dependencies

**Dependency Rationale**: Only technical dependencies (shared code) shown below. M1 (Program) establishes the daemon handler module structure. M2 (Symbols) provides the shared `resolve_address()` helper used by M3-M6. All other milestones can execute in parallel after M2 completes. The "waves" below are recommended groupings for developer focus, not hard dependencies.

```
M1 (Program) - establishes src/daemon/handlers/mod.rs structure
    |
    v
M2 (Symbols) - provides resolve_address() helper
    |
    +---> M3 (Types)      \
    +---> M4 (Comments)    | Can run in parallel
    +---> M5 (Graph)       | All use M2's address resolution
    +---> M6 (Find)       /

M7 (Diff), M8 (Patch), M9 (Script), M10 (Disasm), M11 (Batch), M12 (Stats)
    - No inter-dependencies, can run in parallel after M2

M13 (Docs) - after all implementation milestones
```

**Recommended Parallel Waves** (for team coordination, not technical):
- Wave 1: M1 (Program), M2 (Symbols) - establishes handlers structure and shared helpers
- Wave 2: M3, M4, M5, M6 - all use address resolution, can parallelize
- Wave 3: M7, M8, M9, M10, M11, M12 - independent implementations, can parallelize
- Wave 4: M13 (Docs) - final documentation pass

## Implementation Patterns for M6-M12

**Note**: M1-M5 contain complete unified diffs. M6-M12 follow identical structural patterns. Each milestone requires:

### Structure Pattern (All Milestones)

**1. Handler Module** (`src/daemon/handlers/<name>.rs`):
- Pattern: `pub async fn handle_<operation>(bridge: &mut GhidraBridge, ...) -> Result<String>`
- Each handler: calls `bridge.send_command("<cmd_name>", args)`, checks `response.status`, returns JSON or error
- All use `anyhow::{Context, Result}` and `serde_json::json`
- Test module: `#[cfg(test)] mod tests` with placeholder

**2. Queue Routing** (`src/daemon/queue.rs`):
- Add to `execute_command` match block
- Pattern: `Commands::<Category>(cmd) => { use crate::cli::<Category>Commands; let mut bridge_guard = bridge.lock().await; ... }`
- Match each subcommand variant to handler function
- Return early with handler result

**3. Python Script** (`src/ghidra/scripts/<name>.py`):
- Header: `# @category CLI`
- Functions: one per operation, returns dict
- Main block: `if __name__ == "__main__":` parses `args[0]` as command
- Output: `print("---GHIDRA_CLI_START---"); print(json.dumps(result)); print("---GHIDRA_CLI_END---")`
- Python 2.7 syntax: use `print()` function form, no f-strings

**4. Test File** (`tests/<name>_tests.rs`):
- Use `serial_test::serial` and `DaemonTestHarness`
- Pattern: `ensure_test_project(TEST_PROJECT, TEST_PROGRAM); let harness = DaemonTestHarness::new(...)`
- Each test: `Command::cargo_bin("ghidra").unwrap().env("GHIDRA_CLI_SOCKET", harness.socket_path())...`
- Assertions: `.assert().success()` with `.stdout(predicate::str::contains(...))`
- Always `drop(harness)` at end

### M6: Find Operations

**Handlers** (6 functions):
- `handle_find_string(bridge, pattern)` → sends `find_string` command
- `handle_find_bytes(bridge, hex)` → sends `find_bytes` command
- `handle_find_function(bridge, pattern)` → sends `find_function` command
- `handle_find_calls(bridge, function)` → sends `find_calls` command
- `handle_find_crypto(bridge)` → sends `find_crypto` command
- `handle_find_interesting(bridge)` → sends `find_interesting` command

**Python Script** (`find.py`):
- `find_strings(pattern)`: iterate `currentProgram.getListing().getDefinedData(True)`, filter `StringDataInstance`
- `find_bytes(hex_pattern)`: convert hex to bytes, use `currentProgram.getMemory().findBytes(...)`
- `find_functions(pattern)`: glob match function names using `fnmatch` or simple `in` check
- `find_calls(func_name)`: find function, get `ReferenceManager.getReferencesTo(addr)`, filter `.isCall()`
- `find_crypto()`: search for known constants (AES S-box `0x63, 0x7c, ...`, SHA constants, etc.)
- `find_interesting()`: heuristics - functions > 1000 instructions, >50 xrefs, suspicious names

**Queue Routing**:
```rust
Commands::Find(find_cmd) => {
    use crate::cli::FindCommands;
    // ... bridge setup
    return match find_cmd {
        FindCommands::String(args) => handlers::find::handle_find_string(bridge_ref, &args.pattern).await,
        FindCommands::Bytes(args) => handlers::find::handle_find_bytes(bridge_ref, &args.hex).await,
        FindCommands::Function(args) => handlers::find::handle_find_function(bridge_ref, &args.pattern).await,
        FindCommands::Calls(args) => handlers::find::handle_find_calls(bridge_ref, &args.function).await,
        FindCommands::Crypto(_) => handlers::find::handle_find_crypto(bridge_ref).await,
        FindCommands::Interesting(_) => handlers::find::handle_find_interesting(bridge_ref).await,
    };
},
```

### M7: Diff Operations

**Handlers** (2 functions):
- `handle_diff_programs(bridge, prog1, prog2)` → sends `diff_programs` command
- `handle_diff_functions(bridge, func1, func2)` → sends `diff_functions` command

**Python Script** (`diff.py`):
- `diff_programs(prog1, prog2)`: compare function counts, memory maps, symbol tables, return diff dict
- `diff_functions(func1, func2)`: decompile both, return side-by-side or unified diff of C code

### M8: Patch Operations

**Handlers** (3 functions):
- `handle_patch_bytes(bridge, address, hex)` → sends `patch_bytes` command
- `handle_patch_nop(bridge, address, count)` → sends `patch_nop` command
- `handle_patch_export(bridge, output)` → sends `patch_export` command

**Python Script** (`patch.py`):
- `patch_bytes(addr, hex)`: parse hex, write to `currentProgram.getMemory().setBytes(addr, bytes)`
- `patch_nop(addr, count)`: get instruction size, write NOP bytes (architecture-specific: `0x90` for x86)
- `export_binary(output)`: use Ghidra `Exporter` API to write modified binary

### M9: Script Execution

**Handlers** (4 functions):
- `handle_script_run(bridge, path, args)` → sends `script_run` command
- `handle_script_python(bridge, code)` → sends `script_python` command
- `handle_script_java(bridge, code)` → sends `script_java` command
- `handle_script_list(bridge)` → sends `script_list` command

**Python Script** (`script.py`):
- `run_script(path, args)`: use `runScript(path, args)` Ghidra API
- `exec_python(code)`: `exec(code, globals())` (security: runs in Ghidra sandbox)
- `exec_java(code)`: compile and run Java via Ghidra's Java runner
- `list_scripts()`: iterate Ghidra script directories

### M10: Disasm Command

**Handlers** (1 function):
- `handle_disasm(bridge, address, count)` → sends `disasm` command

**Python Script** (`disasm.py`):
- `disassemble(addr, count)`: `listing.getInstructionAt(addr)`, iterate `.getNext()` for count instructions
- Return: `[{"address": ..., "bytes": ..., "mnemonic": ..., "operands": ...}, ...]`

### M11: Batch Operations

**Handlers** (1 function):
- `handle_batch(file_path)` → read file, parse lines, execute each via normal CLI parsing (NOT bridge command)

**Implementation Note**: Batch does NOT use Python script. Handler reads file in Rust, parses each line as CLI command, submits to queue.

### M12: Stats Command

**Handlers** (1 function):
- `handle_stats(bridge)` → sends `stats` command

**Python Script** (`stats.py`):
- `get_stats()`: aggregate counts from FunctionManager, SymbolTable, Memory, DataTypeManager
- Return: `{"functions": N, "symbols": N, "strings": N, "memory_size": N, "sections": N, ...}`

### Mod.rs Updates

Each handler module requires adding to `src/daemon/handlers/mod.rs`:
```rust
pub mod find;    // M6
pub mod diff;    // M7
pub mod patch;   // M8
pub mod script;  // M9
pub mod disasm;  // M10
pub mod batch;   // M11
pub mod stats;   // M12
```
