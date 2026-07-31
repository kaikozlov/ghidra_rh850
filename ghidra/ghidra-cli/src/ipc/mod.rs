//! IPC module for CLI-to-bridge communication.
//!
//! Provides direct TCP communication to the Java GhidraCliBridge.
//! No intermediate daemon process is needed.

pub mod client;
pub mod protocol;
