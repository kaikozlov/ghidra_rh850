# Plan: Replace Python Bridge with Java GhidraScript Socket Server

## Overview

Replace the current three-layer architecture (Rust CLI → Rust Daemon → Python bridge inside Ghidra JVM) with a two-layer architecture (Rust CLI → Java GhidraScript socket server inside Ghidra JVM). The Java GhidraScript runs via `analyzeHeadless -postScript`, starts a TCP socket server that keeps the JVM alive, and handles all 49 commands directly via the Ghidra Java API. The Rust side collapses: the persistent daemon process is eliminated, replaced by a thin "launcher" that starts `analyzeHeadless` if not running, writes a port+PID file, and then the CLI connects directly to the Java bridge's TCP socket.

**Chosen approach**: Single `.java` GhidraScript file (auto-compiled by `analyzeHeadless`), TCP localhost with dynamic port + port/PID file, collapsed single-layer IPC (no Rust daemon process), clean break migration.

## Planning Context

### Decision Log

| Decision | Reasoning Chain |
|----------|----------------|
| GhidraScript .java over Extension .zip | Extension requires Gradle build infra + versioned distribution packaging → adds build complexity for no runtime benefit → GhidraScript is auto-compiled by `analyzeHeadless` at startup → matches current Python pattern where scripts are written to disk and referenced via `-postScript` → simpler maintenance |
| Collapse to single IPC layer | Current flow: CLI → UDS → Daemon → TCP:18700 → Python bridge. Daemon exists to: (a) manage bridge process lifecycle, (b) provide lock files, (c) lazy-start bridge. With Java bridge: (a) `analyzeHeadless` IS the daemon process, (b) lock files move to port/PID file, (c) CLI launcher starts `analyzeHeadless` if port file missing → Rust daemon process becomes pure passthrough with no logic → eliminate it |
| TCP localhost + port/PID file over Unix domain socket | Java 16+ supports `UnixDomainSocketAddress` but: Ghidra bundles its own JDK and not all Ghidra distributions include JDK 16+ → TCP `ServerSocket(0)` on localhost is universally supported → dynamic port avoids fixed-port conflicts → port written to `~/.local/share/ghidra-cli/bridge-{hash}.port` → PID written to `bridge-{hash}.pid` for killing hung bridges → same security model (localhost only) |
| Single .java file with inner classes | Multiple .java files risk classpath issues with `analyzeHeadless` script compilation → single file with static inner classes keeps all handler code together → file is ~2000-3000 lines which is manageable → `analyzeHeadless` compiles single script files reliably |
| Clean break over dual-mode | Maintaining both Python and Java bridges doubles test surface → Python bridge is the source of complexity we're eliminating → feature branch with all E2E tests passing before merge provides safety → CHANGELOG documents breaking change |
| Sequential command processing (no threading) | Ghidra headless is single-threaded for program access → concurrent writes to Program cause data corruption → Python bridge was already single-connection sequential → Java bridge processes one command at a time on accept loop → analysis queue handles concurrent import requests by queuing |
| Embed .java in binary via include_str! | Current pattern: 13 Python scripts embedded via `include_str!()` in `bridge.rs`, written to `~/.config/ghidra-cli/scripts/` at runtime → same pattern for single Java file → no separate installation step beyond `ghidra-cli` binary itself |
| Port file as liveness indicator | fslock-based locking was complex and had edge cases → port file + PID file is simpler: if port file exists AND PID is alive AND TCP connect succeeds → bridge is running → if any check fails, clean up stale files and start fresh |
| 300s read timeout for analysis ops | Current bridge uses 300s read timeout (bridge.rs:240) → analysis operations (especially initial auto-analysis) can take minutes → keep same timeout → individual query commands complete in <1s but timeout provides safety net |

### Rejected Alternatives

| Alternative | Why Rejected |
|-------------|-------------|
| Ghidra Extension (.zip) packaging | Requires Gradle build infrastructure, module.manifest, extension.properties → adds build system complexity for distribution → GhidraScript auto-compilation achieves same result with zero build tooling |
| Unix domain sockets in Java | Requires Java 16+ `UnixDomainSocketAddress` → Ghidra may bundle older JDK → TCP localhost is universally supported and equally secure for loopback-only binding |
| Keep Rust daemon as process manager | With Java bridge handling its own lifecycle, Rust daemon becomes a passthrough that adds latency and complexity → thin launcher function in CLI achieves same lifecycle management |
| ghidra_bridge (existing library) | External dependency on Jython RPC library → still has Python layer → less control over protocol and error handling → custom Java bridge is simpler and eliminates Python entirely |
| PyGhidra JPype embedding | Requires Python + JPype installation → adds Python dependency back → ghidra-cli's goal is minimal deps (just Ghidra + Java) |
| Dual mode with --bridge flag | Doubles test matrix → Python bridge is what we're removing → clean break is simpler to reason about |
| Fixed port per project (hash-based) | Port collisions between projects with similar hashes → dynamic port with port file is collision-free → slight complexity of reading port file is worth guaranteed uniqueness |

### Constraints & Assumptions

- **Ghidra 10.0+**: Minimum supported version (same as current). `AutoImporter`, `DecompInterface`, `FunctionManager` APIs stable across 10.x-12.x.
- **Java 17+**: Required by Ghidra itself. `ServerSocket`, `Gson` (bundled by Ghidra) available.
- **analyzeHeadless**: Compiles `.java` GhidraScript files automatically. Script receives `currentProgram`, `state`, `monitor` as instance fields.
- **Gson bundled**: Ghidra includes `com.google.gson` in classpath. No external JSON library needed.
- **Single-threaded program access**: Ghidra `Program` objects are not thread-safe for writes. All command handling is sequential (same as current Python bridge).
- **Existing E2E tests validate migration**: If Java bridge produces identical JSON responses to Python bridge, all existing E2E test files pass unchanged. The Rust-side IPC protocol changes (direct TCP instead of UDS→TCP) but the test harness connects via CLI binary which handles this transparently.
- **`GhidraScript.getScriptArgs()`**: Returns command-line arguments passed after script name. Used to pass port file path.

### Known Risks

| Risk | Mitigation | Anchor |
|------|-----------|--------|
| Ghidra API differences across versions (10.x vs 11.x vs 12.x) | `AutoImporter.importByUsingBestGuess()` signature changed in 12.x → Java bridge uses try/catch with reflection fallback for import, same pattern as Python bridge | `src/ghidra/scripts/bridge.py:880-888` uses 6-arg variant |
| `analyzeHeadless` compiles .java with errors | Java compilation errors surface in stderr → bridge.rs already captures stderr for diagnostics → keep this pattern → add specific "Java compilation failed" error detection |
| TCP port exhaustion on systems with many projects | Dynamic port from `ServerSocket(0)` draws from ephemeral range (49152-65535) → 16K+ ports available → stale port files cleaned on next launch attempt |
| Ghidra JVM heap exhaustion with large binaries | Same risk as current Python bridge → not a new risk → Ghidra's default heap settings apply |
| `analyzeHeadless` calls `System.exit()` after script | GhidraScript `run()` method blocks in accept loop → `analyzeHeadless` waits for script completion → `System.exit()` only called after `run()` returns (on shutdown command) |

## Invisible Knowledge

### Architecture

```
BEFORE (3 layers):
  ghidra-cli (Rust) --[UDS]--> daemon (Rust/tokio) --[TCP:18700]--> bridge.py (Python in Ghidra JVM)

AFTER (2 layers):
  ghidra-cli (Rust) --[TCP:dynamic]--> GhidraCliBridge.java (Java in Ghidra JVM via analyzeHeadless)

Lifecycle:
  1. CLI reads port file (~/.local/share/ghidra-cli/bridge-{hash}.port)
  2. If missing or stale: launch analyzeHeadless + GhidraCliBridge.java
  3. GhidraCliBridge writes port file, enters accept loop
  4. CLI connects via TCP, sends JSON command, reads JSON response
  5. On shutdown: GhidraCliBridge deletes port/PID files, run() returns, analyzeHeadless exits
```

### Data Flow

```
CLI Command (e.g., `ghidra functions --limit 10`)
  │
  ├─ Parse CLI args → Command enum
  ├─ Read port file → TCP port (or launch bridge if missing)
  ├─ Connect TCP localhost:port
  ├─ Send: {"command":"list_functions","args":{"limit":10}}\n
  ├─ Recv: {"status":"success","data":{"functions":[...],"count":N}}\n
  ├─ Format output (table/json/csv)
  └─ Display

Bridge Lifecycle:
  analyzeHeadless project_dir project_name -import binary -postScript GhidraCliBridge.java /path/to/portfile
    │
    ├─ GhidraCliBridge.run() called by analyzeHeadless
    ├─ Opens ServerSocket(0), writes port to file, writes PID to file
    ├─ Prints ready signal to stdout
    ├─ Accept loop: read command JSON → dispatch to handler → write response JSON
    ├─ "shutdown" command → break accept loop
    ├─ Cleanup: delete port/PID files
    └─ run() returns → analyzeHeadless exits normally
```

### Why This Structure

- **Single .java file**: `analyzeHeadless` compiles GhidraScript files individually. Multi-file compilation requires extension packaging. Single file with inner classes avoids this while keeping code organized.
- **Port file + PID file**: Replaces the fslock + info file + UDS socket triple. Simpler liveness detection: read PID, check `kill -0`, verify TCP connect.
- **No Rust daemon process**: The Java bridge IS the daemon. `analyzeHeadless` is the process manager. Rust CLI is a thin client that launches the bridge if needed.

### Invariants

1. **One bridge per project**: Port file path includes project hash → only one bridge instance per project directory.
2. **Sequential command processing**: Single accept loop, one connection at a time. Ghidra `Program` objects are not thread-safe for mutation.
3. **Import queuing**: If a program is being analyzed, import commands queue the new binary and return immediately with "queued" status. Analysis proceeds in order.
4. **Port file lifecycle**: Created AFTER ServerSocket.bind() succeeds, deleted BEFORE run() returns. Stale files detected via PID liveness check.
5. **Protocol compatibility**: JSON wire format `{"command":"...","args":{...}}` → `{"status":"success|error","data":{...},"message":"..."}` is identical to current Python bridge.

### Tradeoffs

- **Single large .java file vs extension with multiple classes**: Chose single file for zero-build-tooling simplicity at cost of a large source file (~2500 lines).
- **TCP vs UDS**: Chose TCP for Java cross-platform compatibility at cost of port file management overhead.
- **Clean break vs gradual migration**: Chose clean break for code simplicity at cost of no fallback path.

## Milestones

### Milestone 1: Java GhidraScript Bridge — Core Server + Basic Commands

**Files**:
- `src/ghidra/scripts/GhidraCliBridge.java` (NEW)

**Flags**: `needs-rationale`, `complex-algorithm`

**Requirements**:
- GhidraScript that extends `ghidra.app.script.GhidraScript`
- `run()` method: parse script args for port file path, bind `ServerSocket(0)` on localhost, write port + PID files, print ready signal to stdout, enter accept loop
- Accept loop: read newline-delimited JSON commands from socket, dispatch to handler, write JSON response, handle client disconnect gracefully
- Shutdown command: break accept loop, delete port/PID files, return from `run()`
- Core command handlers (direct ports from bridge.py):
  - `ping` — health check
  - `shutdown` — stop server
  - `program_info` — program metadata (name, format, language, image base, address range)
  - `list_functions` — enumerate functions with limit/filter support
  - `decompile` — decompile function at address or by name
  - `list_strings` — enumerate string data
  - `list_imports` — enumerate external symbols
  - `list_exports` — enumerate export entry points
  - `memory_map` — enumerate memory blocks with permissions
  - `xrefs_to` / `xrefs_from` — cross-reference queries
  - `import` — import binary via `AutoImporter.importByUsingBestGuess()`
  - `analyze` — trigger `AutoAnalysisManager` re-analysis
  - `list_programs` — enumerate project domain files
  - `open_program` — switch active program
  - `program_close` — close current program
  - `program_delete` — delete program from project
  - `program_export` — export program info as JSON
- Address resolution helper: parse hex address or resolve function name
- JSON serialization via Gson (bundled by Ghidra)
- Error handling: all handlers return `{"status":"error","message":"..."}` on failure
- `currentProgram` null checks on all program-dependent handlers

**Acceptance Criteria**:
- `analyzeHeadless /tmp/test TestProject -import /bin/ls -scriptPath . -postScript GhidraCliBridge.java /tmp/test.port` starts server
- Port file contains valid integer port
- PID file contains process PID
- `echo '{"command":"ping"}' | nc localhost $(cat /tmp/test.port)` returns `{"status":"success","data":{"message":"pong"}}`
- `echo '{"command":"list_functions","args":{"limit":5}}' | nc ...` returns JSON with functions array
- `echo '{"command":"shutdown"}' | nc ...` causes clean exit, port+PID files deleted

**Tests**:
- **Test files**: Manual validation with `analyzeHeadless` + `nc`/`curl` during development; formal E2E tests run in Milestone 4
- **Test type**: Manual integration
- **Backing**: Bootstrap — Java bridge must work standalone before Rust integration
- **Scenarios**:
  - Normal: start server, send commands, get correct JSON responses
  - Edge: send malformed JSON, send unknown command, send command with no program loaded
  - Error: binary not found on import, function not found on decompile

**Code Intent**:

- New file `src/ghidra/scripts/GhidraCliBridge.java`: Single GhidraScript class extending `ghidra.app.script.GhidraScript`
- `run()` method: get port file path from `getScriptArgs()[0]`, create `ServerSocket(0, 1, InetAddress.getByName("127.0.0.1"))`, write port to file, write PID to file via `ProcessHandle.current().pid()`, print ready signal `---GHIDRA_CLI_START---` / JSON / `---GHIDRA_CLI_END---` to stdout, enter accept loop
- `handleRequest(String line)` method: parse JSON with Gson, extract "command" and "args", dispatch to handler method, return JSON response string
- `resolveAddress(String addrStr)` helper: try `currentProgram.getAddressFactory().getAddress()`, fall back to function name lookup
- Handler methods: `handlePing()`, `handleProgramInfo()`, `handleListFunctions(JsonObject args)`, `handleDecompile(JsonObject args)`, `handleListStrings(JsonObject args)`, `handleListImports()`, `handleListExports()`, `handleMemoryMap()`, `handleXrefsTo(JsonObject args)`, `handleXrefsFrom(JsonObject args)`, `handleImport(JsonObject args)`, `handleAnalyze(JsonObject args)`, `handleListPrograms()`, `handleOpenProgram(JsonObject args)`, `handleProgramClose()`, `handleProgramDelete(JsonObject args)`, `handleProgramExport(JsonObject args)`
- Each handler follows same pattern as Python equivalent: null-check currentProgram, call Ghidra Java API, build Gson JsonObject response

**Code Changes**: _To be filled by Developer_

---

### Milestone 2: Java Bridge — Extended Command Handlers

**Files**:
- `src/ghidra/scripts/GhidraCliBridge.java` (MODIFY — add remaining handlers)

**Flags**: `conformance`

**Requirements**:
- Port all remaining Python command handlers to Java methods in GhidraCliBridge:
  - **Find**: `find_string`, `find_bytes`, `find_function`, `find_calls`, `find_crypto`, `find_interesting` (from `find.py`)
  - **Symbols**: `symbol_list`, `symbol_get`, `symbol_create`, `symbol_delete`, `symbol_rename` (from `symbols.py`)
  - **Types**: `type_list`, `type_get`, `type_create`, `type_apply` (from `types.py`)
  - **Comments**: `comment_list`, `comment_get`, `comment_set`, `comment_delete` (from `comments.py`)
  - **Graph**: `graph_calls`, `graph_callers`, `graph_callees`, `graph_export` (from `graph.py`)
  - **Diff**: `diff_programs`, `diff_functions` (from `diff.py`)
  - **Patch**: `patch_bytes`, `patch_nop`, `patch_export` (from `patch.py`)
  - **Disasm**: `disasm` (from `disasm.py`)
  - **Stats**: `stats` (from `stats.py`)
  - **Script**: `script_run`, `script_python`, `script_java`, `script_list` (from `script_runner.py`)
  - **Batch**: `batch` (from `batch.py`)
- All handlers produce identical JSON output structure to their Python equivalents
- Transaction management: handlers that modify program state (symbol_create, comment_set, patch_bytes, etc.) must use `currentProgram.startTransaction()` / `endTransaction()`

**Acceptance Criteria**:
- Each handler returns same JSON structure as corresponding Python handler
- Write operations (symbol create, comment set, patch) wrapped in transactions
- `find_bytes` correctly handles hex pattern search across memory blocks
- `graph_callers`/`graph_callees` correctly traverse call graph to specified depth
- `decompile` timeout set to 30 seconds (matching Python: `decompiler.decompileFunction(func, 30, monitor)`)

**Tests**:
- **Test files**: Manual validation during development; formal E2E tests in Milestone 4
- **Test type**: Manual integration
- **Backing**: Behavioral parity with Python bridge
- **Scenarios**:
  - Normal: each handler returns expected data for sample binary
  - Edge: symbol operations on non-existent symbols, patch at invalid address
  - Error: find with empty pattern, graph on function with no calls

**Code Intent**:

- Add command dispatch entries to `handleRequest()` for all new commands
- Find handlers: `handleFindString(args)` — iterate defined data matching pattern; `handleFindBytes(args)` — use `Memory.findBytes()` with hex pattern; `handleFindFunction(args)` — iterate functions matching name pattern; `handleFindCalls(args)` — get xrefs to named function; `handleFindCrypto()` — scan for known crypto constants (AES S-box, SHA constants); `handleFindInteresting()` — heuristic scan for security-relevant functions
- Symbol handlers: use `currentProgram.getSymbolTable()` API — `getSymbols()`, `createLabel()`, `removeSymbolSpecial()`, `getSymbol()`
- Type handlers: use `currentProgram.getDataTypeManager()` — `getAllDataTypes()`, `getDataType()`, `addDataType()`, `apply()` via `DataUtilities.createData()`
- Comment handlers: use `currentProgram.getListing().getCodeUnitAt()` — `getComment()`, `setComment()` with `CodeUnit.EOL_COMMENT` etc.
- Graph handlers: recursive traversal of `function.getCalledFunctions()` / `function.getCallingFunctions()` with depth limit
- Diff handlers: compare two programs' function lists by name/size/signature
- Patch handlers: use `currentProgram.getMemory().setBytes()` within transaction; NOP uses language-specific NOP byte(s)
- Disasm handler: use `currentProgram.getListing().getInstructionAt()` and iterate
- Stats handler: aggregate counts (functions, strings, imports, exports, memory blocks, defined data)
- Script handlers: `script_run` — use `GhidraScriptUtil` to find and run scripts; `script_list` — enumerate script directories
- All write operations wrapped in `int txId = currentProgram.startTransaction("description"); try { ... } finally { currentProgram.endTransaction(txId, true); }`

**Code Changes**: _To be filled by Developer_

---

### Milestone 3: Rust Side — Replace Daemon with Direct Bridge Connection

**Files**:
- `src/ghidra/bridge.rs` (REWRITE — replace Python bridge management with Java bridge management)
- `src/daemon/mod.rs` (REWRITE — eliminate daemon process, replace with launcher logic)
- `src/daemon/handler.rs` (DELETE or REWRITE — direct TCP replaces IPC→bridge delegation)
- `src/daemon/ipc_server.rs` (DELETE — no more UDS IPC server)
- `src/daemon/process.rs` (REWRITE — replace fslock/info file with port/PID file management)
- `src/daemon/state.rs` (DELETE — no daemon state needed)
- `src/daemon/cache.rs` (DELETE or keep if result caching desired)
- `src/daemon/queue.rs` (DELETE — analysis queuing moves to Java side)
- `src/daemon/handlers/*.rs` (DELETE — all handler delegation removed)
- `src/ipc/client.rs` (REWRITE — connect via TCP to Java bridge instead of UDS to daemon)
- `src/ipc/protocol.rs` (MODIFY — simplify to match Java bridge JSON protocol)
- `src/ipc/transport.rs` (SIMPLIFY — TCP only, remove UDS/named pipe abstraction)
- `src/ghidra/bridge.rs` (REWRITE — replace Python bridge management with Java bridge TCP client)
- `src/ghidra/scripts.rs` (MODIFY — embed GhidraCliBridge.java instead of Python scripts)
- `src/lib.rs` (MODIFY — update module structure)
- `src/main.rs` (MODIFY — remove daemon foreground mode, update command routing)
- `src/cli.rs` (MODIFY — remove `daemon start/stop` subcommands, simplify)
- `Cargo.toml` (MODIFY — remove `interprocess`, `fslock` deps; may remove `tokio` if fully sync)

**Flags**: `error-handling`, `needs-rationale`

**Requirements**:
- `bridge.rs` rewrite:
  - `ensure_bridge_running(project_path)`: check port file, verify PID alive, verify TCP connect. If any fail, start new bridge.
  - `start_bridge(project_path, mode)`: spawn `analyzeHeadless` with `-postScript GhidraCliBridge.java`, wait for ready signal on stdout, verify port file created
  - `send_command(port, command, args)`: TCP connect, send JSON, read JSON response, disconnect
  - `kill_bridge(project_path)`: read PID file, send shutdown command (graceful), fall back to kill PID (forced)
  - Port/PID file management: `~/.local/share/ghidra-cli/bridge-{md5_hash}.port`, `bridge-{md5_hash}.pid`
- CLI command flow:
  - `ghidra import <binary>` → ensure_bridge_running → send "import" command
  - `ghidra functions` → ensure_bridge_running → send "list_functions" command
  - `ghidra daemon stop` → read PID/port → send "shutdown" command → verify exit
  - `ghidra daemon status` → check port file + PID + TCP connect → report status
- Remove Python-specific code:
  - Remove `find_headless_script()` pyghidraRun preference logic
  - Remove `install_pyghidra()` from setup
  - Remove all `include_str!("scripts/*.py")` embeds
- Add Java-specific code:
  - `include_str!("scripts/GhidraCliBridge.java")` for embedding
  - Write `.java` file to `~/.config/ghidra-cli/scripts/` on bridge start
  - Always use `analyzeHeadless` (no pyghidraRun)

**Acceptance Criteria**:
- `ghidra import tests/fixtures/sample_binary --project test` starts bridge if needed, imports binary, returns success
- `ghidra functions --project test --program sample_binary` connects to running bridge, returns function list
- `ghidra daemon status` reports bridge running/stopped
- `ghidra daemon stop` gracefully stops the Java bridge
- No `tokio` runtime needed if all I/O is synchronous TCP
- Port file created on bridge start, deleted on bridge stop
- PID file allows `ghidra daemon stop` to kill hung bridges

**Tests**:
- **Test files**: `tests/daemon_tests.rs`, `tests/command_tests.rs` (existing, should pass)
- **Test type**: E2E integration
- **Backing**: Existing test suite validates behavioral parity
- **Scenarios**:
  - Normal: full command lifecycle (import → analyze → query → shutdown)
  - Edge: bridge already running (reuse), bridge crashed (restart), stale port file (cleanup)
  - Error: Ghidra not installed, binary not found, invalid project path

**Code Intent**:

- Rewrite `src/ghidra/bridge.rs`:
  - Remove `GhidraBridge` struct with `Child`, `TcpStream`, `AtomicBool`
  - New functions: `ensure_bridge_running(project_path) -> Result<u16>` (returns port), `start_bridge(project_path, ghidra_dir, mode) -> Result<u16>`, `send_command(port, command, args) -> Result<Value>`, `stop_bridge(project_path) -> Result<()>`
  - `start_bridge()`: write embedded Java script to disk, build `analyzeHeadless` command, spawn process, read stdout for ready signal, return port from port file
  - `send_command()`: `TcpStream::connect(("127.0.0.1", port))`, write JSON line, read JSON line, parse response
  - Port file path: `get_data_dir()?.join(format!("bridge-{}.port", md5_hash(project_path)))`
  - PID file path: same pattern with `.pid` extension
- Rewrite `src/daemon/mod.rs`: remove `DaemonState`, `DaemonConfig`, `run()` async function. Replace with `ensure_bridge(project_path, ghidra_dir)` that calls `bridge::ensure_bridge_running()`
- Rewrite `src/daemon/process.rs`: remove `acquire_daemon_lock()`, `DaemonInfo`. New functions: `read_port_file()`, `write_port_file()`, `read_pid_file()`, `write_pid_file()`, `is_pid_alive()`, `cleanup_stale_files()`
- Delete: `src/daemon/ipc_server.rs`, `src/daemon/state.rs`, `src/daemon/queue.rs`, `src/daemon/handlers/` directory
- Rewrite `src/ipc/client.rs`: remove `DaemonClient` with async reader/writer. New `BridgeClient` with sync `TcpStream`
- Simplify `src/ipc/transport.rs`: remove UDS/named pipe abstractions, keep only TCP helper functions
- Simplify `src/ipc/protocol.rs`: protocol now matches Java bridge JSON format directly: `{"command":"...", "args":{...}}` → `{"status":"...", "data":{...}, "message":"..."}`
- Modify `src/main.rs`: remove `--foreground` daemon mode, update command dispatch to use `bridge::ensure_bridge_running()` + `bridge::send_command()`
- Modify `src/cli.rs`: keep `daemon start/stop/status` as convenience commands but implement via bridge management (not separate process)
- Modify `Cargo.toml`: remove `interprocess`, `fslock` dependencies. Evaluate removing `tokio` if all bridge I/O is synchronous.

**Code Changes**: _To be filled by Developer_

---

### Milestone 4: Setup/Doctor Commands + Python Removal

**Files**:
- `src/ghidra/setup.rs` (MODIFY — remove `install_pyghidra()`, simplify setup)
- `src/main.rs` (MODIFY — update `handle_doctor()`, `handle_setup()`)
- `src/ghidra/scripts/bridge.py` (DELETE)
- `src/ghidra/scripts/find.py` (DELETE)
- `src/ghidra/scripts/symbols.py` (DELETE)
- `src/ghidra/scripts/types.py` (DELETE)
- `src/ghidra/scripts/comments.py` (DELETE)
- `src/ghidra/scripts/graph.py` (DELETE)
- `src/ghidra/scripts/diff.py` (DELETE)
- `src/ghidra/scripts/patch.py` (DELETE)
- `src/ghidra/scripts/disasm.py` (DELETE)
- `src/ghidra/scripts/stats.py` (DELETE)
- `src/ghidra/scripts/script_runner.py` (DELETE)
- `src/ghidra/scripts/batch.py` (DELETE)
- `src/ghidra/scripts/program.py` (DELETE)
- `src/ghidra/scripts.rs` (MODIFY — remove Python script embeds, add Java script embed)

**Flags**: `needs-rationale`

**Requirements**:
- `ghidra setup`:
  1. Check Java 17+ (keep existing `check_java_requirement()`)
  2. Download + extract Ghidra (keep existing `install_ghidra()`)
  3. Remove PyGhidra installation step entirely
  4. Verify `analyzeHeadless` script exists and is executable
  5. Write GhidraCliBridge.java to scripts directory (verify Java compilation by doing a dry-run compile if possible)
- `ghidra doctor`:
  1. Check Java version (keep)
  2. Check Ghidra installation (keep)
  3. Remove PyGhidra check
  4. Add: verify GhidraCliBridge.java can be found/written
  5. Add: verify no stale port/PID files
- Delete all 13 Python scripts from `src/ghidra/scripts/`
- Update `src/ghidra/scripts.rs` to embed only `GhidraCliBridge.java`

**Acceptance Criteria**:
- `ghidra setup` installs Ghidra without any Python/PyGhidra steps
- `ghidra doctor` reports Java, Ghidra, and bridge script status (no Python checks)
- All Python `.py` files removed from source tree
- `cargo build` succeeds with no references to deleted Python files

**Tests**:
- **Test files**: `tests/command_tests.rs` (existing doctor/setup tests)
- **Test type**: E2E integration
- **Backing**: Existing tests validate doctor/setup commands
- **Scenarios**:
  - Normal: setup with valid Ghidra, doctor reports all green
  - Edge: Ghidra not installed (doctor reports error), stale files present (doctor warns)
  - Error: Java not installed, wrong Java version

**Code Intent**:

- Modify `src/ghidra/setup.rs`: delete `install_pyghidra()` function entirely (lines 244-345). Remove all references to Python venv, pip, PyGhidra wheel.
- Modify `src/main.rs` `handle_setup()`: remove PyGhidra installation call. Add step to verify `analyzeHeadless` exists in Ghidra install.
- Modify `src/main.rs` `handle_doctor()`: remove PyGhidra version check. Add bridge script presence check. Add stale port/PID file detection.
- Modify `src/ghidra/bridge.rs`: replace all `include_str!("scripts/*.py")` embeds (lines ~391-403) with single `include_str!("scripts/GhidraCliBridge.java")`. Update script writing logic to write only the Java file.
- Modify `src/ghidra/scripts.rs` if it references Python scripts: update or remove as needed.
- Delete all 13 `.py` files from `src/ghidra/scripts/`

**Code Changes**: _To be filled by Developer_

---

### Milestone 5: E2E Test Validation + CI

**Files**:
- `tests/common/mod.rs` (MODIFY — update `DaemonTestHarness` for new bridge architecture)
- `tests/common/helpers.rs` (MODIFY — update helper functions if needed)
- `tests/daemon_tests.rs` (MODIFY — adapt daemon lifecycle tests)
- `tests/e2e.rs` (MODIFY — verify smoke tests pass)
- `tests/batch_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/command_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/comment_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/diff_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/disasm_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/find_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/graph_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/output_format_integration.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/patch_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/program_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/query_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/script_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/stats_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/symbol_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/type_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `tests/unimplemented_tests.rs` (MODIFY — if DaemonTestHarness interface changes)
- `.github/workflows/test.yml` (MODIFY — remove Python/PyGhidra CI setup if present)

**Requirements**:
- Update `DaemonTestHarness` to work with new bridge architecture:
  - Instead of starting a Rust daemon process, start `analyzeHeadless` with Java bridge
  - Or: use `ghidra import` which now auto-starts the bridge
  - Socket path environment variable replaced with port file path
- All existing E2E test files must pass
- CI workflow removes any Python setup steps

**Acceptance Criteria**:
- `cargo test` passes all existing tests (with Ghidra installed)
- `cargo test --test daemon_tests` validates bridge start/stop/restart
- `cargo test --test query_tests` validates all data query commands
- `cargo test --test command_tests` validates doctor/setup/version
- CI workflow runs without Python dependencies

**Tests**:
- **Test files**: All existing test files in `tests/`
- **Test type**: E2E integration
- **Backing**: Existing test suite is the validation gate
- **Scenarios**:
  - Full regression: every existing test passes
  - New: bridge restart recovery, stale port file cleanup

**Code Intent**:

- Modify `tests/common/mod.rs` `DaemonTestHarness`:
  - `new()`: instead of spawning `ghidra daemon start --foreground`, use `ghidra import` to start bridge, or spawn `analyzeHeadless` directly
  - Replace `socket_path` field with `port` field (read from port file)
  - Update `GHIDRA_CLI_SOCKET` env var to `GHIDRA_CLI_PORT` or equivalent
  - `Drop` impl: send shutdown command via TCP, verify process exit, cleanup port/PID files
- Verify `tests/common/helpers.rs` `ghidra()` builder works with new bridge connection
- Update `tests/daemon_tests.rs`: adapt tests that reference daemon-specific concepts (daemon start/stop → bridge start/stop)
- Update `.github/workflows/test.yml`: remove any `pip install pyghidra` or Python venv setup steps

**Code Changes**: _To be filled by Developer_

---

### Milestone 6: Documentation

**Delegated to**: @agent-technical-writer (mode: post-implementation)

**Source**: `## Invisible Knowledge` section of this plan

**Files**:
- `CLAUDE.md` (MODIFY — update navigation index for new architecture)
- `AGENTS.md` (MODIFY — update architecture description)
- `src/daemon/README.md` (REWRITE — document new bridge-based architecture)
- `CHANGELOG.md` (MODIFY — document breaking change)

**Requirements**:
- CLAUDE.md: update file references (remove Python script references, add Java bridge)
- AGENTS.md: update architecture section to reflect single-layer IPC
- src/daemon/README.md: document new bridge lifecycle, port/PID file management, command protocol
- CHANGELOG.md: document breaking change — Python bridge removed, Java bridge replaces it, setup no longer installs PyGhidra

**Acceptance Criteria**:
- CLAUDE.md is tabular index only
- src/daemon/README.md describes new architecture with ASCII diagram
- CHANGELOG.md has breaking change entry
- No references to Python bridge in documentation

## Milestone Dependencies

```
M1 (Core Java Bridge) ──→ M2 (Extended Handlers) ──→ M3 (Rust Rewrite) ──→ M4 (Setup + Python Removal) ──→ M5 (E2E Tests)
                                                                                                              │
                                                                                                              v
                                                                                                          M6 (Docs)
```

- M1 and M2 are sequential (M2 extends M1's file)
- M3 depends on M1+M2 (Rust side needs Java bridge to exist)
- M4 depends on M3 (can't delete Python until Rust no longer references it)
- M5 depends on M3+M4 (tests validate the complete migration)
- M6 depends on M5 (document after validation)

**Parallelization note**: M1 and early M3 exploration can overlap — Rust-side design can be planned while Java handlers are being written. But M3 implementation depends on M1+M2 being complete for integration testing.
