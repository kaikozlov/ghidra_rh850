//! Library exports for ghidra-cli testing infrastructure.
//!
//! This module exposes internal components needed for integration tests.

#[path = "error.rs"]
pub mod error;

#[path = "config.rs"]
pub mod config;

#[path = "ipc/mod.rs"]
pub mod ipc;

/// Re-export bridge module for integration tests.
#[path = "ghidra"]
pub mod ghidra {
    pub mod bridge;
    pub mod java;
}

/// Batch file parsing.
///
/// Shared between `main.rs` (the batch command handler) and unit/integration
/// tests so the JSON/plain-text parsing logic can be exercised without a
/// running Ghidra bridge. The key invariant — that JSON input preserves token
/// boundaries exactly (no shell re-splitting) — is covered by tests in
/// `src/batch.rs` and `tests/batch_tests.rs`.
#[path = "batch.rs"]
pub mod batch;
