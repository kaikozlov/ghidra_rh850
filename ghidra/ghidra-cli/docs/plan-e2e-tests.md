# E2E Test Coverage Plan

> Historical planning document: this plan captures prior design decisions and may not match current test architecture exactly.
> For current test behavior and commands, see `tests/README.md`.

## Overview

This plan addresses the critical E2E test coverage gap in ghidra-cli. Currently only 4 of 60+ CLI commands have active tests. The plan implements a modular test structure with daemon lifecycle management, enabling comprehensive testing of all CLI functionality including the 51+ untested commands.

**Key decisions**:
- Modular test organization (separate files per command category)
- Per-suite daemon lifecycle (start once, stop after suite)
- Unix socket paths with UUID for uniqueness (not TCP ports)
- Test unimplemented commands for graceful error messages
- Use existing fixture binary with additional fixtures as needed

## Planning Context

### Decision Log

| Decision | Reasoning Chain |
|----------|-----------------|
| Modular test structure | 60+ tests in one file is unmaintainable -> separate files by category enables independent runs -> also allows per-suite daemon lifecycle -> cleaner organization |
| Per-suite daemon lifecycle | Per-test would add 5-30s startup per test -> 60 tests = 5-30 minutes overhead -> per-suite amortizes startup -> faster CI while maintaining isolation between suites |
| Unix socket with UUID path | IPC uses Unix domain sockets (verified in src/ipc/transport.rs) -> need unique path per test suite -> PID can wrap on long-running CI -> UUID guarantees uniqueness -> tempdir + UUID provides safe isolation |
| 120s daemon startup timeout | User-specified -> Ghidra cold start can be slow on constrained CI -> 120s covers worst case without causing flaky tests -> exponential backoff makes fast starts responsive |
| Exponential backoff parameters | Initial delay 100ms, multiplier 2x, max attempts 12 -> covers 100ms to ~200s range -> total max wait ~409s but typical fast start exits in <5s -> balances responsiveness with reliability |
| Test unimplemented commands | User-specified: test with graceful errors -> 25+ commands are stubs -> users need helpful error messages -> testing ensures graceful failures -> also documents which commands need implementation |
| Fixture-based test data | User-specified preference -> existing sample_binary has 9 functions (add, multiply, factorial, fibonacci, process_string, xor_encrypt, simple_hash, init_data, main) -> sufficient for most tests |
| UUID for test project names | User-specified -> PID can wrap on long-running systems -> collision risk in parallel CI -> UUID guarantees uniqueness -> test isolation preserved |
| Drop-based cleanup | User-specified -> best effort cleanup in destructor -> handles most cases -> simpler than explicit finally blocks -> accepts minor leak risk on panic-during-panic |
| Serial test execution scope | #[serial] applies per-file (same test binary) -> prevents daemon state races within suite -> allows parallelism between different test files -> balance of isolation and speed |
| Lazy daemon initialization | Use once_cell::sync::Lazy for per-suite harness -> ensures single initialization even with parallel test discovery -> thread-safe -> daemon starts on first test access |
| Async test support | Verified: daemon client is async (src/ipc/client.rs uses tokio) -> #[tokio::test] required for daemon-dependent tests -> assert_cmd works with sync commands |
| Unimplemented error format | Exit code 1 with message "Command not yet implemented" or "not yet implemented" -> consistent with existing stub pattern in main.rs -> no panic or crash |

### Rejected Alternatives

| Alternative | Why Rejected |
|-------------|--------------|
| Single e2e.rs file | Would grow to 2000+ lines -> hard to navigate -> can't run subsets easily |
| Per-test daemon | 5-30s startup overhead per test -> 60 tests would take 5-30 minutes -> unacceptable CI time |
| Shared global daemon | State leakage between suites -> flaky tests -> debugging nightmare |
| Fixed test port | Parallel CI runs would conflict -> random port more robust |
| Mock daemon responses | Wouldn't test real integration -> defeats purpose of E2E tests |

### Constraints & Assumptions

- **Technical**: Daemon requires Ghidra installation and Java runtime
- **Technical**: IPC uses Unix domain sockets (verified: src/ipc/transport.rs uses interprocess::local_socket)
- **Pattern**: Use assert_cmd and predicates crates (verified: Cargo.toml dev-dependencies)
- **Pattern**: Use serial_test for tests sharing daemon state (verified: Cargo.toml dev-dependencies)
- **Pattern**: Daemon client is async (verified: src/ipc/client.rs uses tokio async/await)
- **CI**: Tests may run on machines without Ghidra installed (need skip mechanism)
- **Fixture**: sample_binary exists with functions: add, multiply, factorial, fibonacci, process_string, xor_encrypt, simple_hash, init_data, main

### Known Risks

| Risk | Mitigation | Anchor |
|------|------------|--------|
| Ghidra not installed on CI | Skip tests with clear message if `ghidra doctor` fails | tests/e2e.rs:73-78 (doctor test pattern) |
| Socket path conflicts | UUID-based socket path in tempdir -> guaranteed unique per test suite | N/A - new code |
| Daemon startup timeout | 120s timeout (user-specified) with exponential backoff ping | N/A - new code |
| Test pollution between suites | Each suite starts fresh daemon with unique socket path | N/A - new code |
| Cleanup on panic | Drop impl sends shutdown, but may leak on panic-during-panic | Accepted: rare edge case, CI cleanup handles residual |

## Invisible Knowledge

### Architecture

```
tests/
├── common/
│   └── mod.rs           # DaemonTestHarness, fixtures, helpers
├── daemon_tests.rs      # Daemon lifecycle: start/stop/restart/status/ping
├── project_tests.rs     # Project: create/list/delete/info
├── query_tests.rs       # Function/strings/memory/xref/dump queries
├── command_tests.rs     # Basic commands: version/doctor/config/init
└── unimplemented_tests.rs  # Graceful error tests for stub commands
```

### Data Flow

```
Test Suite Start
      |
      v
DaemonTestHarness::new()
      |
      +---> Start daemon process
      +---> Wait for IPC socket
      +---> Verify with ping
      |
      v
Run tests (serial within suite)
      |
      v
DaemonTestHarness::drop()
      |
      +---> Send shutdown command
      +---> Wait for process exit
      +---> Cleanup socket file
```

### Why This Structure

- **common/mod.rs**: Shared across all test suites, avoids duplication
- **Per-category files**: Run `cargo test daemon_tests` for focused testing
- **Separation of daemon vs non-daemon tests**: Non-daemon tests run fast without setup

### Invariants

- Daemon must be fully started before any query test runs
- Each test suite gets its own daemon instance (no sharing)
- Socket files must be cleaned up even on test failure (Drop impl)
- Tests must not assume specific function addresses (use name-based lookups)

### Tradeoffs

- **Per-suite vs per-test daemon**: Chose speed over maximum isolation
- **Random vs fixed port**: Chose reliability over simplicity
- **Test unimplemented commands**: Adds maintenance burden but documents gaps

## Milestones

### Milestone 1: Test Infrastructure - DaemonTestHarness

**Files**: `tests/common/mod.rs`, `Cargo.toml`

**Flags**: `error-handling`

**Requirements**:
- Create DaemonTestHarness struct with daemon process management
- Implement start_daemon() with configurable project path
- Implement wait_for_ready() with exponential backoff ping
- Implement graceful shutdown in Drop
- Random port allocation via ephemeral port binding
- Unique socket path per test suite instance

**Acceptance Criteria**:
- DaemonTestHarness::new() starts daemon and waits for ready
- DaemonTestHarness::drop() cleanly shuts down daemon
- Daemon responds to ping within 120s timeout (user-specified)
- Socket file is cleaned up after tests

**Tests**:
- **Test files**: `tests/harness_tests.rs`
- **Test type**: integration
- **Backing**: default-derived
- **Scenarios**:
  - Normal: harness starts and stops daemon successfully
  - Edge: daemon already running (should error)
  - Error: daemon fails to start (timeout with clear message)

**Code Intent**:
- New file `tests/common/mod.rs`
- Struct `DaemonTestHarness` with fields: child process handle (Child), socket path (PathBuf), project path (PathBuf), runtime (tokio::runtime::Runtime)
- Runtime field prevents panic-during-panic in Drop and avoids repeated Runtime creation overhead
- Method `new(project: &str, program: &str) -> Result<Self>`:
  - Generate unique socket path via `get_unique_socket_path()`
  - Set GHIDRA_CLI_SOCKET env var for daemon
  - Spawn `ghidra daemon start --foreground --project <project>`
  - Create tokio Runtime (reused across all async operations)
  - Call `wait_for_ready(Duration::from_secs(120))`
- Method `wait_for_ready(&self, timeout: Duration) -> Result<()>`:
  - Exponential backoff: initial 100ms, multiplier 2x, max 12 attempts
  - Each attempt tries IPC ping using self.runtime.block_on
  - Explicitly handles connection errors on final attempt
  - Returns Ok on success, Err with timeout/connection error message on exhaustion
- Method `client(&self) -> Result<DaemonClient>`: uses self.runtime.block_on to connect to socket, returns async IPC client
- Impl `Drop for DaemonTestHarness`:
  - Try to send shutdown via client using self.runtime.block_on (ignore errors)
  - No Runtime creation in Drop (prevents panic-during-panic)
  - Wait up to 5s for process exit
  - Kill process if still running
  - Remove socket file
- Helper `get_unique_socket_path() -> PathBuf`: `std::env::temp_dir().join(format!("ghidra-test-{}.sock", uuid::Uuid::new_v4()))`
- Re-export fixture helpers from fixtures.rs

**Code Changes**:
```diff
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -90,6 +90,8 @@ predicates = "3.0"
 tempfile = "3.8"
 serial_test = "3.0"
+uuid = { version = "1.6", features = ["v4"] }
+once_cell = "1.19"

 [[bin]]
 name = "ghidra"
```

```diff
--- /dev/null
+++ b/tests/common/mod.rs
@@ -0,0 +1,118 @@
+//! Common test utilities for E2E tests.
+
+use anyhow::{Context, Result};
+use std::path::PathBuf;
+use std::process::{Child, Command};
+use std::time::Duration;
+
+pub mod fixtures;
+pub use fixtures::*;
+
+/// Test harness that manages daemon lifecycle for a test suite.
+pub struct DaemonTestHarness {
+    child: Child,
+    socket_path: PathBuf,
+    project: String,
+    // Runtime field prevents panic-during-panic in Drop (cannot create Runtime during panic unwinding)
+    // and amortizes Runtime creation overhead across all async operations in this harness.
+    runtime: tokio::runtime::Runtime,
+}
+
+impl DaemonTestHarness {
+    /// Start daemon for testing. Blocks until daemon is ready or timeout.
+    pub fn new(project: &str, program: &str) -> Result<Self> {
+        let socket_path = get_unique_socket_path();
+
+        let mut cmd = Command::new(env!("CARGO_BIN_EXE_ghidra"));
+        cmd.env("GHIDRA_CLI_SOCKET", &socket_path)
+            .arg("daemon")
+            .arg("start")
+            .arg("--foreground")
+            .arg("--project")
+            .arg(project);
+
+        let child = cmd.spawn().context("Failed to spawn daemon")?;
+
+        // ChildGuard ensures daemon process is killed if wait_for_ready() returns early due to error.
+        // Without this, failed initialization would leak daemon processes.
+        struct ChildGuard(Option<Child>);
+        impl Drop for ChildGuard {
+            fn drop(&mut self) {
+                if let Some(mut child) = self.0.take() {
+                    let _ = child.kill();
+                }
+            }
+        }
+        let mut guard = ChildGuard(Some(child));
+
+        let runtime = tokio::runtime::Runtime::new()
+            .context("Failed to create tokio runtime")?;
+
+        let mut harness = Self {
+            child: guard.0.take().unwrap(),
+            socket_path,
+            project: project.to_string(),
+            runtime,
+        };
+
+        // 120s timeout: Ghidra cold start can be slow on constrained CI environments.
+        // Covers worst case without causing flaky tests.
+        harness.wait_for_ready(Duration::from_secs(120))?;
+
+        Ok(harness)
+    }
+
+    /// Wait for daemon to be ready using exponential backoff.
+    fn wait_for_ready(&mut self, timeout: Duration) -> Result<()> {
+        let start = std::time::Instant::now();
+        // Exponential backoff: 100ms initial (responsive for fast starts), 2x multiplier, 12 max attempts.
+        // Covers 100ms to ~200s range; total max wait ~409s but typical fast start exits in <5s.
+        let mut delay = Duration::from_millis(100);
+        let max_attempts = 12;
+
+        for attempt in 0..max_attempts {
+            if start.elapsed() > timeout {
+                anyhow::bail!("Daemon failed to start within {}s timeout", timeout.as_secs());
+            }
+
+            std::thread::sleep(delay);
+
+            if let Ok(mut client) = self.client() {
+                match self.runtime.block_on(client.ping()) {
+                    Ok(true) => return Ok(()),
+                    Ok(false) => {},
+                    Err(e) => {
+                        if attempt == max_attempts - 1 {
+                            anyhow::bail!("Connection error during ping: {}", e);
+                        }
+                    }
+                }
+            }
+
+            delay = delay.saturating_mul(2);
+        }
+
+        anyhow::bail!("Daemon failed to respond after {} attempts", max_attempts)
+    }
+
+    /// Get async IPC client connected to daemon.
+    pub fn client(&self) -> Result<ghidra_cli::ipc::client::DaemonClient> {
+        self.runtime.block_on(async {
+            ghidra_cli::ipc::client::DaemonClient::connect().await
+        })
+    }
+
+    /// Get socket path for this daemon instance.
+    pub fn socket_path(&self) -> &PathBuf {
+        &self.socket_path
+    }
+
+    /// Get project name.
+    pub fn project(&self) -> &str {
+        &self.project
+    }
+}
+
+impl Drop for DaemonTestHarness {
+    fn drop(&mut self) {
+        if let Ok(mut client) = self.client() {
+            let _ = self.runtime.block_on(client.shutdown());
+        }
+
+        // 5s wait before kill: allows graceful shutdown to complete.
+        // Most daemons shut down in <1s; 5s handles slow cleanup without blocking tests indefinitely.
+        let timeout = Duration::from_secs(5);
+        let start = std::time::Instant::now();
+
+        while start.elapsed() < timeout {
+            if let Ok(Some(_)) = self.child.try_wait() {
+                break;
+            }
+            std::thread::sleep(Duration::from_millis(100));
+        }
+
+        let _ = self.child.kill();
+        let _ = std::fs::remove_file(&self.socket_path);
+    }
+}
+
+/// Generate unique socket path for test isolation.
+///
+/// UUID guarantees uniqueness across parallel test suites and long-running CI (PID can wrap).
+fn get_unique_socket_path() -> PathBuf {
+    std::env::temp_dir().join(format!("ghidra-test-{}.sock", uuid::Uuid::new_v4()))
+}
+```


---

### Milestone 2: Test Infrastructure - Fixtures and Helpers

**Files**: `tests/common/mod.rs` (extend), `tests/common/fixtures.rs`

**Requirements**:
- Extract fixture helpers from e2e.rs to common module
- Add helper for creating test projects
- Add helper for verifying daemon responses
- Add skip_if_no_ghidra() macro

**Acceptance Criteria**:
- `fixture_binary()` returns path to sample_binary
- `ensure_test_project()` creates and analyzes a test project
- `skip_if_no_ghidra!()` skips test with message if Ghidra not available
- All helpers work with DaemonTestHarness

**Tests**:
- **Test files**: `tests/harness_tests.rs` (extend with fixture tests)
- **Test type**: integration
- **Backing**: default-derived
- **Scenarios**:
  - Normal: fixture binary exists and is valid
  - Edge: fixture not compiled (clear build instructions)

**Code Intent**:
- New file `tests/common/fixtures.rs`
- Move `fixture_binary() -> PathBuf` from e2e.rs (returns tests/fixtures/sample_binary path)
- Move `ensure_project_setup()` from e2e.rs, rename to `ensure_test_project(project: &str, program: &str)`
  - Uses Once::call_once pattern for idempotent setup
  - Imports and analyzes sample_binary if needed
- Add `skip_if_no_ghidra!()` macro that runs `ghidra doctor` and skips if fails
- Add `verify_json_response(output: &str, expected_fields: &[&str])` helper
- Update `tests/common/mod.rs` to re-export from fixtures.rs

**Code Changes**:
```diff
--- /dev/null
+++ b/tests/common/fixtures.rs
@@ -0,0 +1,69 @@
+//! Test fixture helpers.
+
+use assert_cmd::Command;
+use std::path::PathBuf;
+use std::sync::Once;
+
+/// Get path to the sample_binary test fixture.
+pub fn fixture_binary() -> PathBuf {
+    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
+        .join("tests")
+        .join("fixtures")
+        .join("sample_binary")
+}
+
+/// Ensure test project exists with analyzed sample binary.
+///
+/// Uses Once::call_once for idempotent setup across multiple tests in same process.
+pub fn ensure_test_project(project: &str, program: &str) {
+    static SETUP: Once = Once::new();
+    SETUP.call_once(|| {
+        let binary = fixture_binary();
+        if !binary.exists() {
+            panic!(
+                "Test fixture not found: {:?}\nRun: rustc --edition 2021 -o tests/fixtures/sample_binary tests/fixtures/sample_binary.rs",
+                binary
+            );
+        }
+
+        eprintln!("=== Setting up test project (import + analyze) ===");
+
+        let mut cmd = Command::cargo_bin("ghidra").expect("Failed to find ghidra binary");
+        let result = cmd
+            .arg("import")
+            .arg(binary.to_str().unwrap())
+            .arg("--project")
+            .arg(project)
+            .arg("--program")
+            .arg(program)
+            .timeout(std::time::Duration::from_secs(300))
+            .output()
+            .expect("Failed to run import command");
+
+        if !result.status.success() {
+            let stderr = String::from_utf8_lossy(&result.stderr);
+            let stdout = String::from_utf8_lossy(&result.stdout);
+            eprintln!("Import stdout: {}", stdout);
+            eprintln!("Import stderr: {}", stderr);
+            if !stderr.contains("already exists") && !stdout.contains("already exists") {
+                eprintln!("Warning: Import may have failed, but continuing...");
+            }
+        } else {
+            eprintln!("Binary imported successfully");
+        }
+
+        eprintln!("=== Test project setup complete ===");
+    });
+}
+
+/// Skip test if Ghidra is not available.
+#[macro_export]
+macro_rules! skip_if_no_ghidra {
+    () => {
+        use assert_cmd::Command;
+        let doctor = Command::cargo_bin("ghidra").unwrap().arg("doctor").output();
+        if doctor.is_err() || !doctor.unwrap().status.success() {
+            eprintln!("Skipping test: Ghidra not available");
+            return;
+        }
+    };
+}
+```


---

### Milestone 3: Basic Command Tests

**Files**: `tests/command_tests.rs`

**Requirements**:
- Test all standalone commands that don't need daemon
- Cover: version, doctor, init, config (list/get/set/reset), set-default

**Acceptance Criteria**:
- `ghidra version` returns version string
- `ghidra doctor` checks installation status
- `ghidra init` creates config file
- `ghidra config list` shows all config keys
- `ghidra config get <key>` returns value
- `ghidra config set <key> <value>` updates config
- `ghidra config reset` resets to defaults
- `ghidra set-default program <name>` sets default
- `ghidra set-default project <name>` sets default

**Tests**:
- **Test files**: `tests/command_tests.rs`
- **Test type**: integration
- **Backing**: default-derived (standard integration test pattern)
- **Scenarios**:
  - Normal: each command with valid inputs
  - Edge: config get for non-existent key
  - Error: invalid command arguments

**Code Intent**:
- New file `tests/command_tests.rs`
- 9 test functions: test_version, test_doctor, test_init, test_config_list, test_config_get, test_config_set, test_config_reset, test_set_default_program, test_set_default_project
- Each test uses `Command::cargo_bin("ghidra")` pattern
- No daemon required for these tests
- Use `skip_if_no_ghidra!()` at start of each test

**Code Changes**:
```diff
--- /dev/null
+++ b/tests/command_tests.rs
@@ -0,0 +1,106 @@
+//! Tests for basic CLI commands that don't require daemon.
+
+use assert_cmd::Command;
+use predicates::prelude::*;
+
+#[macro_use]
+mod common;
+
+#[test]
+fn test_version() {
+    skip_if_no_ghidra!();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("version")
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("ghidra-cli"));
+}
+
+#[test]
+fn test_doctor() {
+    skip_if_no_ghidra!();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("doctor")
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("Ghidra CLI Doctor"));
+}
+
+#[test]
+fn test_init() {
+    skip_if_no_ghidra!();
+
+    let temp = tempfile::tempdir().unwrap();
+    let config_path = temp.path().join("config.yaml");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_CONFIG", &config_path)
+        .arg("init")
+        .assert()
+        .success();
+
+    assert!(config_path.exists());
+}
+
+#[test]
+fn test_config_list() {
+    skip_if_no_ghidra!();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("config")
+        .arg("list")
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("ghidra_install_dir"));
+}
+
+#[test]
+fn test_config_get() {
+    skip_if_no_ghidra!();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("config")
+        .arg("get")
+        .arg("ghidra_install_dir")
+        .assert()
+        .success();
+}
+
+#[test]
+fn test_config_set() {
+    skip_if_no_ghidra!();
+
+    let temp = tempfile::tempdir().unwrap();
+    let config_path = temp.path().join("config.yaml");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_CONFIG", &config_path)
+        .arg("config")
+        .arg("set")
+        .arg("default_project")
+        .arg("test-project")
+        .assert()
+        .success();
+}
+
+#[test]
+fn test_config_reset() {
+    skip_if_no_ghidra!();
+
+    let temp = tempfile::tempdir().unwrap();
+    let config_path = temp.path().join("config.yaml");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_CONFIG", &config_path)
+        .arg("config")
+        .arg("reset")
+        .assert()
+        .success();
+}
+```


---

### Milestone 4: Project Management Tests

**Files**: `tests/project_tests.rs`

**Requirements**:
- Test project lifecycle commands
- Cover: project create, project list, project delete, project info

**Acceptance Criteria**:
- `ghidra project create <name>` creates new project
- `ghidra project list` shows all projects
- `ghidra project info <name>` shows project details
- `ghidra project delete <name>` removes project
- Error on delete non-existent project

**Tests**:
- **Test files**: `tests/project_tests.rs`
- **Test type**: integration
- **Backing**: default-derived
- **Scenarios**:
  - Normal: create -> list -> info -> delete lifecycle
  - Edge: create project that already exists
  - Error: delete non-existent project

**Code Intent**:
- New file `tests/project_tests.rs`
- 5 test functions: test_project_create, test_project_list, test_project_info, test_project_delete, test_project_lifecycle
- test_project_lifecycle does full create->list->info->delete sequence
- Use unique project names per test: `format!("test-{}-{}", test_name, uuid::Uuid::new_v4())` (Decision: UUID for uniqueness)
- Cleanup projects in test teardown via `ghidra project delete`

**Code Changes**:
```diff
--- /dev/null
+++ b/tests/project_tests.rs
@@ -0,0 +1,103 @@
+//! Tests for project management commands.
+
+use assert_cmd::Command;
+use predicates::prelude::*;
+
+#[macro_use]
+mod common;
+
+/// Generate unique project name for test isolation.
+///
+/// UUID prevents collisions in parallel CI runs (PID can wrap on long-running systems).
+fn unique_project_name(prefix: &str) -> String {
+    format!("test-{}-{}", prefix, uuid::Uuid::new_v4())
+}
+
+#[test]
+fn test_project_create() {
+    skip_if_no_ghidra!();
+
+    let project = unique_project_name("create");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("create")
+        .arg(&project)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("Created project"));
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("delete")
+        .arg(&project)
+        .assert()
+        .success();
+}
+
+#[test]
+fn test_project_list() {
+    skip_if_no_ghidra!();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("list")
+        .assert()
+        .success();
+}
+
+#[test]
+fn test_project_info() {
+    skip_if_no_ghidra!();
+
+    let project = unique_project_name("info");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("create")
+        .arg(&project)
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("info")
+        .arg(&project)
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("delete")
+        .arg(&project)
+        .assert()
+        .success();
+}
+
+#[test]
+fn test_project_lifecycle() {
+    skip_if_no_ghidra!();
+
+    let project = unique_project_name("lifecycle");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("create")
+        .arg(&project)
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("list")
+        .assert()
+        .success()
+        .stdout(predicate::str::contains(&project));
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("delete")
+        .arg(&project)
+        .assert()
+        .success();
+}
+```


---

### Milestone 5: Daemon Lifecycle Tests

**Files**: `tests/daemon_tests.rs`

**Requirements**:
- Test daemon start/stop/restart/status/ping/clear-cache
- Use DaemonTestHarness infrastructure

**Acceptance Criteria**:
- `ghidra daemon start --project <name>` starts daemon
- `ghidra daemon status` shows running daemon info
- `ghidra daemon ping` verifies daemon is responsive
- `ghidra daemon stop` shuts down daemon gracefully
- `ghidra daemon restart` stops and restarts daemon
- `ghidra daemon clear-cache` clears query cache
- Error when starting daemon for non-existent project

**Tests**:
- **Test files**: `tests/daemon_tests.rs`
- **Test type**: integration
- **Backing**: default-derived
- **Scenarios**:
  - Normal: each lifecycle command
  - Edge: start when already running
  - Error: start with invalid project

**Code Intent**:
- New file `tests/daemon_tests.rs`
- Import DaemonTestHarness from common
- 7 test functions: test_daemon_start, test_daemon_stop, test_daemon_status, test_daemon_ping, test_daemon_restart, test_daemon_clear_cache, test_daemon_lifecycle
- test_daemon_lifecycle is serial integration test of full lifecycle
- Each test marked `#[serial]` to avoid port conflicts
- Ensure test project exists before daemon tests

**Code Changes**:
```diff
--- /dev/null
+++ b/tests/daemon_tests.rs
@@ -0,0 +1,129 @@
+//! Tests for daemon lifecycle commands.
+
+use assert_cmd::Command;
+use predicates::prelude::*;
+use serial_test::serial;
+
+#[macro_use]
+mod common;
+use common::{ensure_test_project, DaemonTestHarness};
+
+const TEST_PROJECT: &str = "daemon-test";
+const TEST_PROGRAM: &str = "sample_binary";
+
+#[test]
+#[serial]
+fn test_daemon_start() {
+    skip_if_no_ghidra!();
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("daemon")
+        .arg("status")
+        .assert()
+        .success();
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_daemon_status() {
+    skip_if_no_ghidra!();
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("daemon")
+        .arg("status")
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("running"));
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_daemon_ping() {
+    skip_if_no_ghidra!();
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("daemon")
+        .arg("ping")
+        .assert()
+        .success();
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_daemon_clear_cache() {
+    skip_if_no_ghidra!();
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("daemon")
+        .arg("clear-cache")
+        .assert()
+        .success();
+
+    drop(harness);
+}
+
+#[test]
+#[serial]
+fn test_daemon_lifecycle() {
+    skip_if_no_ghidra!();
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+
+    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
+        .expect("Failed to start daemon");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("daemon")
+        .arg("status")
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("running"));
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("daemon")
+        .arg("ping")
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("daemon")
+        .arg("stop")
+        .assert()
+        .success();
+}
+```


---

### Milestone 6: Query Command Tests (Function/Strings/Memory)

**Files**: `tests/query_tests.rs`

**Flags**: `conformance`

**Requirements**:
- Test query commands that require daemon
- Cover: function list, strings list, memory map, summary
- Use DaemonTestHarness for daemon lifecycle

**Acceptance Criteria**:
- `ghidra function list` returns JSON array of functions
- `ghidra function list --limit N` respects limit
- `ghidra function list --filter <expr>` filters results
- `ghidra strings list` returns string data
- `ghidra memory map` returns memory regions
- `ghidra summary` returns program info
- All commands return valid JSON

**Tests**:
- **Test files**: `tests/query_tests.rs`
- **Test type**: integration
- **Backing**: default-derived
- **Scenarios**:
  - Normal: list functions finds main, fibonacci, factorial
  - Normal: memory map shows .text section
  - Edge: empty filter returns all
  - Edge: limit 0 returns empty

**Code Intent**:
- New file `tests/query_tests.rs`
- Use `once_cell::sync::Lazy<DaemonTestHarness>` for per-suite daemon (Decision: Lazy daemon initialization)
- Static HARNESS: Lazy<DaemonTestHarness> initialized on first test access
- 8 test functions: test_function_list, test_function_list_limit, test_function_list_filter, test_strings_list, test_memory_map, test_summary, test_query_json_format, test_query_table_format
- Each test uses shared daemon via `&*HARNESS`
- Mark all tests `#[serial]` for shared daemon safety (Decision: Serial test execution scope)
- Verify JSON structure of responses using serde_json::from_str

**Code Changes**:
```diff
--- /dev/null
+++ b/tests/query_tests.rs
@@ -0,0 +1,158 @@
+//! Tests for query commands that require daemon.
+
+use assert_cmd::Command;
+use once_cell::sync::Lazy;
+use predicates::prelude::*;
+use serial_test::serial;
+
+#[macro_use]
+mod common;
+use common::{ensure_test_project, DaemonTestHarness};
+
+const TEST_PROJECT: &str = "query-test";
+const TEST_PROGRAM: &str = "sample_binary";
+
+// Lazy initialization: starts daemon on first test access, ensures single initialization
+// even with parallel test discovery. Thread-safe per-suite daemon amortizes 5-30s startup
+// overhead across all tests in this file (per-test daemon would add minutes to CI time).
+static HARNESS: Lazy<DaemonTestHarness> = Lazy::new(|| {
+    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
+    DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM).expect("Failed to start daemon")
+});
+
+#[test]
+#[serial]
+fn test_function_list() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    let output = Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("function")
+        .arg("list")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .get_output()
+        .stdout
+        .clone();
+
+    let stdout = String::from_utf8_lossy(&output);
+    assert!(stdout.contains("main"));
+    assert!(stdout.contains("fibonacci") || stdout.contains("factorial"));
+}
+
+#[test]
+#[serial]
+fn test_function_list_limit() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("function")
+        .arg("list")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .arg("--limit")
+        .arg("5")
+        .assert()
+        .success();
+}
+
+#[test]
+#[serial]
+fn test_function_list_filter() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("function")
+        .arg("list")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .arg("--filter")
+        .arg("main")
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("main"));
+}
+
+#[test]
+#[serial]
+fn test_strings_list() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("strings")
+        .arg("list")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .arg("--limit")
+        .arg("100")
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("address"));
+}
+
+#[test]
+#[serial]
+fn test_memory_map() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("memory")
+        .arg("map")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains(".text").or(predicate::str::contains("r")));
+}
+
+#[test]
+#[serial]
+fn test_summary() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("summary")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("Program Summary"));
+}
+```


---

### Milestone 7: Decompile and XRef Tests

**Files**: `tests/query_tests.rs` (extend)

**Requirements**:
- Test decompile command
- Test xref to/from commands
- Both require daemon

**Acceptance Criteria**:
- `ghidra decompile main` returns C code
- `ghidra decompile 0x<addr>` works with address
- `ghidra xref to <addr>` returns references to address
- `ghidra xref from <addr>` returns references from address
- Invalid address returns helpful error

**Tests**:
- **Test files**: `tests/query_tests.rs`
- **Test type**: integration
- **Backing**: default-derived
- **Scenarios**:
  - Normal: decompile main function
  - Normal: xrefs to/from known address
  - Edge: decompile by address
  - Error: non-existent function name

**Code Intent**:
- Extend `tests/query_tests.rs`
- 6 additional test functions: test_decompile_by_name, test_decompile_by_address, test_xref_to, test_xref_from, test_xref_nonexistent, test_decompile_error
- Get address of main from function list for address-based tests
- Verify decompiled code contains function signature

**Code Changes**:
```diff
--- a/tests/query_tests.rs
+++ b/tests/query_tests.rs
@@ -155,3 +155,78 @@ fn test_summary() {
         .success()
         .stdout(predicate::str::contains("Program Summary"));
 }
+
+#[test]
+#[serial]
+fn test_decompile_by_name() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("decompile")
+        .arg("main")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("void").or(predicate::str::contains("int")));
+}
+
+#[test]
+#[serial]
+fn test_decompile_by_address() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    let output = Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("function")
+        .arg("list")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .arg("--format")
+        .arg("json")
+        .assert()
+        .success()
+        .get_output()
+        .stdout
+        .clone();
+
+    let stdout = String::from_utf8_lossy(&output);
+    let functions: serde_json::Value = serde_json::from_str(&stdout).unwrap();
+    let main_addr = functions
+        .as_array()
+        .and_then(|arr| arr.iter().find(|f| f["name"].as_str() == Some("main")))
+        .and_then(|f| f["address"].as_str())
+        .expect("Could not find main function address");
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("decompile")
+        .arg(main_addr)
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+}
+
+#[test]
+#[serial]
+fn test_decompile_error() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("decompile")
+        .arg("nonexistent_function")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .failure();
+}
+```


---

### Milestone 8: Dump Command Tests

**Files**: `tests/query_tests.rs` (extend)

**Requirements**:
- Test dump subcommands: imports, exports, functions, strings
- All require daemon

**Acceptance Criteria**:
- `ghidra dump imports` returns import list
- `ghidra dump exports` returns export list
- `ghidra dump functions` returns function list
- `ghidra dump strings` returns string list
- All support --limit and --format options

**Tests**:
- **Test files**: `tests/query_tests.rs`
- **Test type**: integration
- **Backing**: default-derived
- **Scenarios**:
  - Normal: each dump command returns expected data
  - Edge: dump with limit
  - Edge: dump with JSON format

**Code Intent**:
- Extend `tests/query_tests.rs`
- 4 additional test functions: test_dump_imports, test_dump_exports, test_dump_functions, test_dump_strings
- Verify structure matches function list output for dump functions
- Use same daemon harness as other query tests

**Code Changes**:
```diff
--- a/tests/query_tests.rs
+++ b/tests/query_tests.rs
@@ -230,3 +230,68 @@ fn test_decompile_error() {
         .assert()
         .failure();
 }
+
+#[test]
+#[serial]
+fn test_dump_imports() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("dump")
+        .arg("imports")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+}
+
+#[test]
+#[serial]
+fn test_dump_exports() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("dump")
+        .arg("exports")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+}
+
+#[test]
+#[serial]
+fn test_dump_functions() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("dump")
+        .arg("functions")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+}
+
+#[test]
+#[serial]
+fn test_dump_strings() {
+    skip_if_no_ghidra!();
+
+    let harness = &*HARNESS;
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .env("GHIDRA_CLI_SOCKET", harness.socket_path())
+        .arg("dump")
+        .arg("strings")
+        .arg("--project")
+        .arg(TEST_PROJECT)
+        .arg("--program")
+        .arg(TEST_PROGRAM)
+        .assert()
+        .success();
+}
+```


---

### Milestone 9: Import and Analyze Tests

**Files**: `tests/project_tests.rs` (extend)

**Requirements**:
- Test binary import command
- Test analyze command
- Test quick analysis command

**Acceptance Criteria**:
- `ghidra import <binary> --project <name>` imports binary
- `ghidra analyze --project <name> --program <prog>` runs analysis
- `ghidra quick <binary>` imports and analyzes in one step
- Import with existing program name prompts or errors
- Analysis shows progress or completes silently

**Tests**:
- **Test files**: `tests/project_tests.rs`
- **Test type**: integration
- **Backing**: default-derived
- **Scenarios**:
  - Normal: import sample_binary
  - Normal: analyze imported binary
  - Normal: quick analysis workflow
  - Edge: import to existing project

**Code Intent**:
- Extend `tests/project_tests.rs`
- 4 additional test functions: test_import_binary, test_analyze, test_quick, test_import_existing
- Use unique project names per test
- Cleanup imported projects after tests
- These don't require daemon (use HeadlessExecutor)

**Code Changes**:
```diff
--- a/tests/project_tests.rs
+++ b/tests/project_tests.rs
@@ -101,3 +101,75 @@ fn test_project_lifecycle() {
         .assert()
         .success();
 }
+
+#[test]
+fn test_import_binary() {
+    skip_if_no_ghidra!();
+
+    let project = unique_project_name("import");
+    let binary = common::fixture_binary();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("import")
+        .arg(binary.to_str().unwrap())
+        .arg("--project")
+        .arg(&project)
+        .arg("--program")
+        .arg("sample_binary")
+        .timeout(std::time::Duration::from_secs(300))
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("Successfully imported"));
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("delete")
+        .arg(&project)
+        .assert()
+        .success();
+}
+
+#[test]
+fn test_analyze() {
+    skip_if_no_ghidra!();
+
+    let project = unique_project_name("analyze");
+    let binary = common::fixture_binary();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("import")
+        .arg(binary.to_str().unwrap())
+        .arg("--project")
+        .arg(&project)
+        .arg("--program")
+        .arg("sample_binary")
+        .timeout(std::time::Duration::from_secs(300))
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("analyze")
+        .arg("--project")
+        .arg(&project)
+        .arg("--program")
+        .arg("sample_binary")
+        .timeout(std::time::Duration::from_secs(300))
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("project")
+        .arg("delete")
+        .arg(&project)
+        .assert()
+        .success();
+}
+
+#[test]
+fn test_quick() {
+    skip_if_no_ghidra!();
+
+    let binary = common::fixture_binary();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("quick")
+        .arg(binary.to_str().unwrap())
+        .timeout(std::time::Duration::from_secs(300))
+        .assert()
+        .success();
+}
+```


---

### Milestone 10: Unimplemented Command Tests

**Files**: `tests/unimplemented_tests.rs`

**Flags**: `needs-rationale`

**Requirements**:
- Test all stub/unimplemented commands for graceful errors
- Document which commands are not yet implemented
- Verify helpful error messages

**Acceptance Criteria**:
- Each unimplemented command returns "not yet implemented" message
- Error message suggests alternative or next steps
- Exit code is non-zero
- No panic or crash

**Commands to test** (25+):
- Program: close, delete, info, export
- Symbol: list, get, create, delete, rename
- Type: list, get, create, apply
- Comment: list, get, set, delete
- Find: string, bytes, function, calls, crypto, interesting
- Graph: calls, callers, callees, export
- Diff: programs, functions
- Patch: bytes, nop, export
- Script: run, python, java, list
- Batch
- Stats
- Disasm

**Tests**:
- **Test files**: `tests/unimplemented_tests.rs`
- **Test type**: integration
- **Backing**: user-specified (test graceful errors per user request)
- **Scenarios**:
  - Normal: each command returns helpful error
  - Normal: exit code is non-zero

**Code Intent**:
- New file `tests/unimplemented_tests.rs`
- Macro `test_unimplemented!(name, args...)` to reduce boilerplate:
  ```rust
  macro_rules! test_unimplemented {
      ($name:ident, $($arg:expr),*) => {
          #[test]
          fn $name() {
              Command::cargo_bin("ghidra").unwrap()
                  $(.arg($arg))*
                  .assert()
                  .failure()
                  .stderr(predicate::str::contains("not yet implemented")
                      .or(predicate::str::contains("Command not yet implemented")));
          }
      };
  }
  ```
- Generate test for each unimplemented command using macro
- Verify output contains "not yet implemented" or "Command not yet implemented" (Decision: Unimplemented error format)
- Verify exit code is non-zero via `.failure()`
- Group tests by category with comments (Program, Symbol, Type, etc.)

**Code Changes**:
```diff
--- /dev/null
+++ b/tests/unimplemented_tests.rs
@@ -0,0 +1,102 @@
+//! Tests for unimplemented commands to ensure graceful error messages.
+
+use assert_cmd::Command;
+use predicates::prelude::*;
+
+// Macro reduces boilerplate for 25+ unimplemented command tests.
+// Consistent pattern enforces graceful error format across all stub commands.
+macro_rules! test_unimplemented {
+    ($name:ident, $($arg:expr),*) => {
+        #[test]
+        fn $name() {
+            Command::cargo_bin("ghidra").unwrap()
+                $(.arg($arg))*
+                .assert()
+                .failure()
+                .stderr(predicate::str::contains("not yet implemented")
+                    .or(predicate::str::contains("Command not yet implemented")));
+        }
+    };
+}
+
+test_unimplemented!(test_program_close, "program", "close", "test");
+test_unimplemented!(test_program_delete, "program", "delete", "test");
+test_unimplemented!(test_program_info, "program", "info", "test");
+test_unimplemented!(test_program_export, "program", "export", "test");
+
+test_unimplemented!(test_symbol_list, "symbol", "list");
+test_unimplemented!(test_symbol_get, "symbol", "get", "test");
+test_unimplemented!(test_symbol_create, "symbol", "create", "test");
+test_unimplemented!(test_symbol_delete, "symbol", "delete", "test");
+test_unimplemented!(test_symbol_rename, "symbol", "rename", "test", "new");
+
+test_unimplemented!(test_type_list, "type", "list");
+test_unimplemented!(test_type_get, "type", "get", "test");
+test_unimplemented!(test_type_create, "type", "create", "test");
+test_unimplemented!(test_type_apply, "type", "apply", "test");
+
+test_unimplemented!(test_comment_list, "comment", "list");
+test_unimplemented!(test_comment_get, "comment", "get", "0x1000");
+test_unimplemented!(test_comment_set, "comment", "set", "0x1000", "test");
+test_unimplemented!(test_comment_delete, "comment", "delete", "0x1000");
+
+test_unimplemented!(test_find_string, "find", "string", "test");
+test_unimplemented!(test_find_bytes, "find", "bytes", "deadbeef");
+test_unimplemented!(test_find_function, "find", "function", "test");
+test_unimplemented!(test_find_calls, "find", "calls", "test");
+test_unimplemented!(test_find_crypto, "find", "crypto");
+test_unimplemented!(test_find_interesting, "find", "interesting");
+
+test_unimplemented!(test_graph_calls, "graph", "calls");
+test_unimplemented!(test_graph_callers, "graph", "callers", "main");
+test_unimplemented!(test_graph_callees, "graph", "callees", "main");
+test_unimplemented!(test_graph_export, "graph", "export", "test.dot");
+
+test_unimplemented!(test_diff_programs, "diff", "programs", "p1", "p2");
+test_unimplemented!(test_diff_functions, "diff", "functions", "f1", "f2");
+
+test_unimplemented!(test_patch_bytes, "patch", "bytes", "0x1000", "deadbeef");
+test_unimplemented!(test_patch_nop, "patch", "nop", "0x1000");
+test_unimplemented!(test_patch_export, "patch", "export", "test.bin");
+
+test_unimplemented!(test_script_run, "script", "run", "test.py");
+test_unimplemented!(test_script_python, "script", "python", "test.py");
+test_unimplemented!(test_script_java, "script", "java", "test.java");
+test_unimplemented!(test_script_list, "script", "list");
+
+test_unimplemented!(test_batch, "batch", "test.txt");
+test_unimplemented!(test_stats, "stats");
+test_unimplemented!(test_disasm, "disasm", "0x1000");
+```


---

### Milestone 11: Refactor Existing E2E Tests

**Files**: `tests/e2e.rs`

**Requirements**:
- Remove tests migrated to new files
- Keep e2e.rs as integration smoke test
- Update to use common module

**Acceptance Criteria**:
- e2e.rs imports from common module
- Duplicate tests removed
- Remaining tests still pass
- No ignored tests (handled by other files now)

**Tests**:
- **Test files**: `tests/e2e.rs`
- **Test type**: integration
- **Backing**: existing tests
- **Scenarios**:
  - Normal: smoke test of basic workflow

**Code Intent**:
- Update `tests/e2e.rs`
- Remove test_function_list, test_decompile, test_strings, test_memory_map, test_summary (now in query_tests.rs)
- Remove test_doctor, test_version, test_config_list (now in command_tests.rs)
- Remove test_import_binary (now in project_tests.rs)
- Keep ensure_project_setup() call but delegate to common module
- Add single test_smoke() that does quick workflow verification:
  - Check ghidra version works
  - Check ghidra doctor works
  - Verify config can be listed
  - Total runtime target: <30s without daemon
- Import common::{fixture_binary, ensure_test_project, skip_if_no_ghidra}

**Code Changes**:
```diff
--- a/tests/e2e.rs
+++ b/tests/e2e.rs
@@ -5,242 +5,25 @@

 use assert_cmd::Command;
 use predicates::prelude::*;
-use serial_test::serial;
-use std::path::PathBuf;
-use std::sync::Once;

-static SETUP: Once = Once::new();
-static PROJECT_NAME: &str = "e2e-test";
-static PROGRAM_NAME: &str = "sample_binary";
-
-/// Get the path to the test fixture binary
-fn fixture_binary() -> PathBuf {
-    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
-        .join("tests")
-        .join("fixtures")
-        .join("sample_binary")
-}
-
-/// Ensure the test project is set up (import + analyze the sample binary).
-/// This runs only once per test run, regardless of how many tests call it.
-fn ensure_project_setup() {
-    SETUP.call_once(|| {
-        let binary = fixture_binary();
-        if !binary.exists() {
-            panic!(
-                "Test fixture not found: {:?}\nRun: rustc --edition 2021 -o tests/fixtures/sample_binary tests/fixtures/sample_binary.rs",
-                binary
-            );
-        }
-
-        eprintln!("=== Setting up E2E test project (import + analyze) ===");
-
-        // Import the binary
-        let mut cmd = Command::cargo_bin("ghidra").expect("Failed to find ghidra binary");
-        let result = cmd
-            .arg("import")
-            .arg(binary.to_str().unwrap())
-            .arg("--project")
-            .arg(PROJECT_NAME)
-            .arg("--program")
-            .arg(PROGRAM_NAME)
-            .timeout(std::time::Duration::from_secs(300))
-            .output()
-            .expect("Failed to run import command");
-
-        if !result.status.success() {
-            let stderr = String::from_utf8_lossy(&result.stderr);
-            let stdout = String::from_utf8_lossy(&result.stdout);
-            eprintln!("Import stdout: {}", stdout);
-            eprintln!("Import stderr: {}", stderr);
-            // Don't panic - project might already exist
-            if !stderr.contains("already exists") && !stdout.contains("already exists") {
-                eprintln!("Warning: Import may have failed, but continuing...");
-            }
-        } else {
-            eprintln!("Binary imported successfully");
-        }
-
-        eprintln!("=== E2E test project setup complete ===");
-    });
-}
-
-mod e2e_tests {
-    use super::*;
-
-    /// Test that doctor command works
-    #[test]
-    fn test_doctor() {
-        let mut cmd = Command::cargo_bin("ghidra").unwrap();
-        cmd.arg("doctor")
-            .assert()
-            .success()
-            .stdout(predicate::str::contains("Ghidra CLI Doctor"));
-    }
-
-    /// Test version command
-    #[test]
-    fn test_version() {
-        let mut cmd = Command::cargo_bin("ghidra").unwrap();
-        cmd.arg("version")
-            .assert()
-            .success()
-            .stdout(predicate::str::contains("ghidra-cli"));
-    }
-
-    /// Test config list command
-    #[test]
-    fn test_config_list() {
-        let mut cmd = Command::cargo_bin("ghidra").unwrap();
-        cmd.arg("config")
-            .arg("list")
-            .assert()
-            .success()
-            .stdout(predicate::str::contains("ghidra_install_dir"));
-    }
-
-    /// Test import command with sample binary
-    #[test]
-    #[serial]
-    fn test_import_binary() {
-        let binary = fixture_binary();
-        if !binary.exists() {
-            panic!(
-                "Test fixture not found. Run: rustc --edition 2021 -o tests/fixtures/sample_binary tests/fixtures/sample_binary.rs"
-            );
-        }
-
-        // Use a unique project name for this test
-        let project = format!("e2e-import-{}", std::process::id());
-
-        let mut cmd = Command::cargo_bin("ghidra").unwrap();
-        cmd.arg("import")
-            .arg(binary.to_str().unwrap())
-            .arg("--project")
-            .arg(&project)
-            .arg("--program")
-            .arg("sample_binary")
-            .timeout(std::time::Duration::from_secs(300))
-            .assert()
-            .success()
-            .stdout(predicate::str::contains("Successfully imported"));
-    }
-
-    /// Test function list command on pre-analyzed binary
-    /// NOTE: This test requires the daemon to be running. Skipped pending daemon E2E test infrastructure.
-    #[test]
-    #[serial]
-    #[ignore = "Requires daemon to be running. Run with --ignored to include daemon tests."]
-    fn test_function_list() {
-        ensure_project_setup();
-
-        let mut cmd = Command::cargo_bin("ghidra").unwrap();
-        cmd.arg("function")
-            .arg("list")
-            .arg("--project")
-            .arg(PROJECT_NAME)
-            .arg("--program")
-            .arg(PROGRAM_NAME)
-            .arg("--limit")
-            .arg("100")
-            .timeout(std::time::Duration::from_secs(300))
-            .assert()
-            .success()
-            // Check for our known exported functions
-            .stdout(predicate::str::contains("main"))
-            .stdout(
-                predicate::str::contains("fibonacci").or(predicate::str::contains("factorial")),
-            );
-    }
-
-    /// Test decompile command
-    /// NOTE: This test requires the daemon to be running.
-    #[test]
-    #[serial]
-    #[ignore = "Requires daemon to be running. Run with --ignored to include daemon tests."]
-    fn test_decompile() {
-        ensure_project_setup();
-
-        let mut cmd = Command::cargo_bin("ghidra").unwrap();
-        cmd.arg("decompile")
-            .arg("main") // Decompile main function
-            .arg("--project")
-            .arg(PROJECT_NAME)
-            .arg("--program")
-            .arg(PROGRAM_NAME)
-            .timeout(std::time::Duration::from_secs(300))
-            .assert()
-            .success()
-            // Should contain decompiled C code
-            .stdout(predicate::str::contains("void").or(predicate::str::contains("int")));
-    }
-
-    /// Test strings command
-    /// NOTE: This test requires the daemon to be running.
-    #[test]
-    #[serial]
-    #[ignore = "Requires daemon to be running. Run with --ignored to include daemon tests."]
-    fn test_strings() {
-        ensure_project_setup();
-
-        let mut cmd = Command::cargo_bin("ghidra").unwrap();
-        cmd.arg("strings")
-            .arg("list")
-            .arg("--project")
-            .arg(PROJECT_NAME)
-            .arg("--program")
-            .arg(PROGRAM_NAME)
-            .arg("--limit")
-            .arg("100") // Increase limit to find our test strings
-            .timeout(std::time::Duration::from_secs(300))
-            .assert()
-            .success()
-            // Check for strings that exist in a typical ELF binary
-            // (libc symbols are reliably present)
-            .stdout(predicate::str::contains("address"))
-            .stdout(predicate::str::contains("value"));
-    }
-
-    /// Test memory map command
-    /// NOTE: This test requires the daemon to be running.
-    #[test]
-    #[serial]
-    #[ignore = "Requires daemon to be running. Run with --ignored to include daemon tests."]
-    fn test_memory_map() {
-        ensure_project_setup();
-
-        let mut cmd = Command::cargo_bin("ghidra").unwrap();
-        cmd.arg("memory")
-            .arg("map")
-            .arg("--project")
-            .arg(PROJECT_NAME)
-            .arg("--program")
-            .arg(PROGRAM_NAME)
-            .timeout(std::time::Duration::from_secs(300))
-            .assert()
-            .success()
-            // Should show memory sections
-            .stdout(predicate::str::contains(".text").or(predicate::str::contains("r")));
-    }
+#[macro_use]
+mod common;

-    /// Test summary command
-    /// NOTE: This test requires the daemon to be running.
-    #[test]
-    #[serial]
-    #[ignore = "Requires daemon to be running. Run with --ignored to include daemon tests."]
-    fn test_summary() {
-        ensure_project_setup();
+#[test]
+fn test_smoke() {
+    skip_if_no_ghidra!();

-        let mut cmd = Command::cargo_bin("ghidra").unwrap();
-        cmd.arg("summary")
-            .arg("--project")
-            .arg(PROJECT_NAME)
-            .arg("--program")
-            .arg(PROGRAM_NAME)
-            .timeout(std::time::Duration::from_secs(300))
-            .assert()
-            .success()
-            .stdout(predicate::str::contains("Program Summary"));
-    }
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("version")
+        .assert()
+        .success()
+        .stdout(predicate::str::contains("ghidra-cli"));
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("doctor")
+        .assert()
+        .success();
+
+    Command::cargo_bin("ghidra")
+        .unwrap()
+        .arg("config")
+        .arg("list")
+        .assert()
+        .success();
 }
```


---

### Milestone 12: Documentation

**Delegated to**: @agent-technical-writer (mode: post-implementation)

**Source**: `## Invisible Knowledge` section of this plan

**Files**:
- `tests/README.md`
- `tests/common/README.md`

**Requirements**:
- Document test organization
- Document how to run tests
- Document DaemonTestHarness usage
- Document fixture requirements

**Acceptance Criteria**:
- README.md explains test structure
- Instructions for running specific test suites
- Instructions for adding new tests
- Troubleshooting section for common issues

## Milestone Dependencies

```
M1 (DaemonTestHarness) ---+---> M5 (Daemon Tests)
                          |           |
M2 (Fixtures) ------------+---> M6 (Query Tests) ---> M7 (Decompile/XRef)
                          |           |                      |
                          |           +---> M8 (Dump Tests) -+
                          |                                  |
M3 (Basic Commands) ------+                                  v
                          |                           M11 (Refactor e2e.rs)
M4 (Project Tests) -------+---> M9 (Import/Analyze)         |
                          |                                  v
M10 (Unimplemented) ------+                           M12 (Documentation)
```

**Parallel Wave Analysis**:
- Wave 1: M1, M2 (infrastructure, no dependencies)
- Wave 2: M3, M4, M10 (basic tests and unimplemented tests, depend on M2 only)
- Wave 3: M5, M6, M9 (daemon tests and import, depend on M1+M2)
- Wave 4: M7, M8 (extend M6, depend on Wave 3)
- Wave 5: M11 (refactor, after all other tests exist)
- Wave 6: M12 (documentation, after all code complete)

Note: M10 (unimplemented tests) moved to Wave 2 as it only needs fixtures from M2, not daemon infrastructure.
