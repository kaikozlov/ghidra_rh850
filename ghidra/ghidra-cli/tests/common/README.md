# Common Test Utilities

Shared infrastructure for E2E tests.

## DaemonTestHarness

Manages bridge lifecycle for test suites requiring Ghidra bridge interaction.

### Usage

```rust
use common::{DaemonTestHarness, ensure_test_project};

const TEST_PROJECT: &str = "my-test";
const TEST_PROGRAM: &str = "sample_binary";

#[test]
#[serial]
fn test_with_bridge() {
    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);

    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
        .expect("Failed to start bridge");

    Command::cargo_bin("ghidra")
        .unwrap()
        .arg("--project")
        .arg(TEST_PROJECT)
        .arg("my-command")
        .arg("--program")
        .arg(TEST_PROGRAM)
        .assert()
        .success();

    // Bridge automatically shuts down when harness drops
}
```

### Port File Discovery

Each harness discovers the bridge via port file:
```
~/.local/share/ghidra-cli/bridge-{md5_hash}.port
```

Where `{md5_hash}` is derived from the canonical project path. The harness reads the port number from this file and connects via TCP.

### Cleanup Guarantees

Drop implementation ensures best-effort cleanup:
1. Send shutdown command via TCP (ignores errors)
2. Bridge deletes its own port/PID files on clean shutdown
3. Kill process via PID if still running

## Fixtures

### fixture_binary()

Returns path to compiled sample_binary fixture.

```rust
let binary = fixture_binary();
assert!(binary.exists());
```

Binary must be compiled before tests:
```bash
rustc --edition 2021 -o tests/fixtures/sample_binary tests/fixtures/sample_binary.rs
```

### ensure_test_project()

Idempotent project setup using `Once::call_once`. Imports and analyzes sample_binary if needed.

```rust
ensure_test_project("my-project", "sample_binary");
// Second call does nothing - project already exists
```

Handles "already exists" errors gracefully. Safe to call from multiple tests.

## require_ghidra! Macro

Tests should call this macro to assert Ghidra availability up front:

```rust
#[test]
fn test_something() {
    require_ghidra!();

    // Test code runs only if ghidra doctor succeeds
}
```

Runs `ghidra doctor` and fails the test if Ghidra is unavailable, including doctor output.

## GhidraCommand Builder (helpers.rs)

Fluent builder for constructing CLI commands in tests:

```rust
use common::helpers::{ghidra, GhidraCommand};

let result = ghidra(&harness)
    .arg("function")
    .arg("list")
    .run();

result.assert_success();
```

The `ghidra(&harness)` helper pre-configures `--project` args from the harness. Additional helpers include `with_project()`, `json_format()`, and `timeout()`.

## Design Decisions

### Exponential Backoff Parameters

`wait_for_port()` uses backoff to wait for the bridge port file to appear after launching `analyzeHeadless`. Typical fast start exits in <5s.

### Why 5s Shutdown Timeout

Most bridges shut down in <1s. 5s allows graceful cleanup without blocking tests indefinitely. If bridge hangs, hard kill via PID prevents test suite deadlock.
