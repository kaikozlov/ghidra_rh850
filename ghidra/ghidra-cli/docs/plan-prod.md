# Ghidra-CLI Open Source Release Plan (Daemon-Only Architecture)

> Historical planning document: this does not reflect the current implementation.
> Current architecture is direct CLI-to-Java bridge (`GhidraCliBridge.java`) as documented in `README.md` and `AGENTS.md`.

## Overview

Prepare ghidra-cli for open source release with a **daemon-only architecture**. Binary analysis is slow enough that a persistent Ghidra process (via daemon) is always preferable to spawning new processes per command.

**Key architectural change**: Remove HeadlessExecutor as an execution path. All query operations MUST go through the daemon, which maintains a persistent GhidraBridge connection to Ghidra.

## Planning Context

### Decision Log

| Decision | Reasoning Chain |
|----------|-----------------|
| Daemon-only for queries | Binary analysis takes 5-30+ seconds cold start -> persistent daemon amortizes this -> always faster for real workflows -> user confirmed this approach |
| Remove HeadlessExecutor fallback | Fallback creates confusion about which path is used -> daemon is always better -> remove fallback, require daemon explicitly |
| Use IPC layer over legacy RPC | IPC uses local sockets (faster, no port conflicts) -> cross-platform (Unix sockets + Windows named pipes) -> already implemented in src/ipc/ |
| Wire CommandQueue to GhidraBridge | Queue already exists with caching -> handler.rs already routes to bridge -> just need to connect the pieces |
| Keep standalone commands local | Config, setup, doctor, version don't need Ghidra -> run locally without daemon |

### Rejected Alternatives

| Alternative | Why Rejected |
|-------------|--------------|
| Keep HeadlessExecutor as fallback | Creates two code paths to maintain -> daemon is always better -> simpler to require daemon |
| Auto-start daemon | Adds complexity -> explicit start is clearer -> user knows daemon is running |
| Remove daemon RPC entirely | Some users may have scripts using RPC -> deprecate but keep for now |

### Constraints & Assumptions

- **User-specified**: Daemon-only architecture for query operations
- **Technical**: GhidraBridge and bridge.py already functional
- **Technical**: IPC protocol and transport already implemented
- **Pattern**: handler.rs already translates IPC Commands to bridge calls

## Current State Analysis

### What Already Works

```
✓ GhidraBridge (src/ghidra/bridge.rs) - persistent TCP to Ghidra
✓ bridge.py - Python server inside Ghidra with command handlers
✓ IPC protocol (src/ipc/protocol.rs) - typed Command enum
✓ IPC transport (src/ipc/transport.rs) - cross-platform sockets
✓ IPC client (src/ipc/client.rs) - high-level client API
✓ IPC server (src/daemon/ipc_server.rs) - accepts connections
✓ Handler (src/daemon/handler.rs) - routes commands to bridge
✓ Daemon lifecycle (start/stop/status/ping)
```

### What Needs Wiring

```
✗ CommandQueue.execute_command() is stubbed (returns TODO message)
✗ main.rs uses daemon_rpc (legacy) not ipc (new)
✗ Fallback to HeadlessExecutor still exists
✗ Query operations bypass daemon entirely
```

## Milestones

> All file paths are relative to repository root

### Milestone 1: Fix Cargo.toml Repository URL

**Files**: `Cargo.toml`

**Requirements**:
- Update repository URL from localhost to GitHub

**Acceptance Criteria**:
- URL matches `https://github.com/akiselev/ghidra-cli`

**Code Changes**:
```diff
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -5,7 +5,7 @@ edition = "2021"
 authors = ["Alexander Kiselev"]
 description = "Rust CLI to run Ghidra headless for reverse engineering with Claude Code and other agents"
 license = "GPL-3.0"
-repository = "http://127.0.0.1:62915/git/akiselev/ghidra-cli"
+repository = "https://github.com/akiselev/ghidra-cli"
```

---

### Milestone 2: Wire IPC Client in main.rs

**Files**: `src/main.rs`

**Requirements**:
- Replace `daemon_rpc::DaemonClient` with `ipc::client::DaemonClient`
- Route query commands through IPC when daemon is running
- Return error (not fallback) when daemon required but not running

**Acceptance Criteria**:
- `ghidra query functions` uses IPC when daemon running
- `ghidra query functions` errors with "start daemon" message when daemon not running
- No fallback to HeadlessExecutor

**Code Intent**:
- In `run_with_daemon_check()`: Replace `daemon_rpc::DaemonClient::connect(port)` with `ipc::client::DaemonClient::connect(socket_path)`
- Add match on command type: query-based commands REQUIRE daemon, others can run standalone
- Remove the `else { run(cli) }` fallback for query commands
- Add helpful error message: "This command requires the daemon. Start with: ghidra daemon start --project <name>"

---

### Milestone 3: Implement CommandQueue Execute

**Files**: `src/daemon/queue.rs`

**Requirements**:
- Implement `execute_command()` to actually execute commands via GhidraBridge
- Replace the TODO stub with real execution

**Acceptance Criteria**:
- Commands submitted to queue are executed via bridge
- Results are cached and returned

**Code Intent**:
- Change `execute_command()` to take a reference to `GhidraBridge`
- Translate `Commands` enum to bridge operations
- Call `bridge.send_command()` for each operation type
- Parse JSON response and return formatted result

---

### Milestone 4: Add XRefs Support to Handler

**Files**: `src/daemon/handler.rs`, `src/ipc/protocol.rs`

**Requirements**:
- Ensure XRefs commands are handled in the daemon
- Handler routes XRefsTo/XRefsFrom to bridge

**Acceptance Criteria**:
- `ghidra query xrefs --to main` works via daemon
- Returns JSON array of cross-references

**Code Intent**:
- Verify `Command::XRefsTo` and `Command::XRefsFrom` exist in protocol.rs
- Add handling in `handler.rs` for these commands
- Call `bridge.xrefs_to()` / `bridge.xrefs_from()`

---

### Milestone 5: Add --to Parameter for XRefs Query

**Files**: `src/cli.rs`, `src/main.rs`

**Requirements**:
- Add `--to` parameter to query subcommand
- Pass target to daemon when querying xrefs

**Acceptance Criteria**:
- `ghidra query xrefs --to main --project x --program y` parses correctly
- Target is sent to daemon in IPC request

**Code Intent**:
- Add `to: Option<String>` to QueryArgs in cli.rs
- In main.rs query handling, include target in IPC command

---

### Milestone 6: Deprecate HeadlessExecutor

**Files**: `src/ghidra/headless.rs`, `src/ghidra/mod.rs`

**Requirements**:
- Mark HeadlessExecutor as deprecated
- Remove direct calls from main.rs
- Keep module for potential future use (import/analyze operations)

**Acceptance Criteria**:
- No query operations use HeadlessExecutor
- Compile succeeds with deprecation warnings only

**Code Intent**:
- Add `#[deprecated(note = "Use daemon for query operations")]` to HeadlessExecutor
- Remove/comment out direct HeadlessExecutor usage in main.rs handle_* functions
- Route through daemon instead

---

### Milestone 7: Fix Compiler Warnings

**Files**: Multiple (same as original plan)

**Requirements**:
- Remove unused imports
- Handle dead code appropriately

**Acceptance Criteria**:
- `cargo build` produces no warnings (or only deprecation warnings for HeadlessExecutor)

**Code Intent**:
- Remove unused imports from handler.rs, queue.rs, etc.
- Keep IPC layer code (now actually used!)
- Remove truly dead methods

---

### Milestone 8: Add E2E Tests for Daemon Queries

**Files**: `tests/e2e.rs`

**Requirements**:
- Test query operations through daemon
- Test XRefs query

**Acceptance Criteria**:
- Tests start daemon, run queries, stop daemon
- All tests pass

**Code Intent**:
- Add test helper to start/stop daemon
- Add `test_daemon_query_functions()`
- Add `test_daemon_query_xrefs()`
- Add `test_daemon_required_error()` - verify error when daemon not running

---

### Milestone 9: Expand README.md

**Files**: `README.md`

**Requirements**:
- Document daemon-first architecture
- Explain why daemon is required for queries
- Quick start with daemon workflow

**Acceptance Criteria**:
- README explains daemon requirement
- Includes daemon workflow example

**Code Intent**:
- Expand README with:
  - Overview explaining persistent Ghidra benefit
  - Quick start: `ghidra daemon start`, then queries
  - Architecture section explaining daemon design
  - All 9 sections from original plan

---

## Milestone Dependencies

```
M1 (Cargo.toml) ----+
                    |
M2 (IPC Client) ----+----> M4 (XRefs Handler) ----> M5 (--to param)
                    |
M3 (Queue Execute) -+----> M6 (Deprecate Headless)
                    |
                    +----> M7 (Warnings) ----> M8 (Tests) ----> M9 (README)
```

## Architecture After Changes

```
CLI Command
    ↓
[Command Type?]
    ├─ Daemon Control (start/stop) → Handle locally
    ├─ Config/Setup/Doctor → Handle locally
    └─ Query/Decompile/etc → REQUIRES DAEMON
                                ↓
                         [Daemon Running?]
                         ├─ NO → Error: "Start daemon first"
                         └─ YES → IPC Client
                                    ↓
                              Send Command (local socket)
                                    ↓
                              IPC Server receives
                                    ↓
                              handler.rs routes
                                    ↓
                              GhidraBridge.send_command()
                                    ↓
                              bridge.py in Ghidra
                                    ↓
                              Response back
                                    ↓
                              Format & display
```

## Key Benefits

1. **Faster queries**: Ghidra stays loaded, no 5-30s startup per command
2. **Simpler code**: One execution path, not two
3. **Better UX**: Consistent behavior, clear daemon requirement
4. **Easier debugging**: All queries go through same path
