//! Test helper utilities for CLI testing.
//!
//! Provides a fluent API for running CLI commands with proper assertions.

#![allow(dead_code)]

use serde::de::DeserializeOwned;
use std::path::PathBuf;

use super::schemas::{Function, Validate};
use super::DaemonTestHarness;

/// Result of running a ghidra CLI command.
///
/// Provides fluent assertion methods for verifying command behavior.
#[derive(Debug)]
pub struct GhidraResult {
    pub exit_code: i32,
    pub stdout: String,
    pub stderr: String,
}

impl GhidraResult {
    /// Assert the command succeeded (exit code 0).
    pub fn assert_success(&self) -> &Self {
        assert_eq!(
            self.exit_code, 0,
            "Expected success but command failed.\nstderr: {}\nstdout: {}",
            self.stderr, self.stdout
        );
        self
    }

    /// Assert the command failed (non-zero exit code).
    pub fn assert_failure(&self) -> &Self {
        assert_ne!(
            self.exit_code, 0,
            "Expected failure but command succeeded.\nstdout: {}",
            self.stdout
        );
        self
    }

    /// Assert stdout contains the given string.
    pub fn assert_stdout_contains(&self, expected: &str) -> &Self {
        assert!(
            self.stdout.contains(expected),
            "Expected stdout to contain '{}'.\nActual stdout:\n{}",
            expected,
            self.stdout
        );
        self
    }

    /// Assert stdout does NOT contain the given string.
    pub fn assert_stdout_not_contains(&self, unexpected: &str) -> &Self {
        assert!(
            !self.stdout.contains(unexpected),
            "Expected stdout to NOT contain '{}'.\nActual stdout:\n{}",
            unexpected,
            self.stdout
        );
        self
    }

    /// Assert stderr contains the given string.
    pub fn assert_stderr_contains(&self, expected: &str) -> &Self {
        assert!(
            self.stderr.contains(expected),
            "Expected stderr to contain '{}'.\nActual stderr:\n{}",
            expected,
            self.stderr
        );
        self
    }

    /// Parse stdout as JSON into the specified type.
    /// Panics with helpful message if parsing fails.
    pub fn json<T: DeserializeOwned>(&self) -> T {
        serde_json::from_str(&self.stdout).unwrap_or_else(|e| {
            panic!(
                "Failed to parse stdout as JSON.\nError: {}\nstdout:\n{}",
                e, self.stdout
            )
        })
    }

    /// Parse stdout as JSON and validate against schema.
    pub fn json_validated<T: DeserializeOwned + Validate>(&self) -> T {
        let result: T = self.json();
        result.assert_valid();
        result
    }

    /// Try to parse stdout as JSON, returning None if it fails.
    pub fn try_json<T: DeserializeOwned>(&self) -> Option<T> {
        serde_json::from_str(&self.stdout).ok()
    }

    /// Get stdout lines as a vector.
    pub fn lines(&self) -> Vec<&str> {
        self.stdout.lines().collect()
    }

    /// Assert stdout has at least N lines.
    pub fn assert_min_lines(&self, n: usize) -> &Self {
        let count = self.stdout.lines().count();
        assert!(
            count >= n,
            "Expected at least {} lines, got {}.\nstdout:\n{}",
            n,
            count,
            self.stdout
        );
        self
    }

    /// Assert stdout has exactly N lines.
    pub fn assert_line_count(&self, n: usize) -> &Self {
        let count = self.stdout.lines().count();
        assert_eq!(
            count, n,
            "Expected {} lines, got {}.\nstdout:\n{}",
            n, count, self.stdout
        );
        self
    }
}

/// Builder for running ghidra CLI commands with proper configuration.
pub struct GhidraCommand {
    args: Vec<String>,
    project: Option<String>,
    program: Option<String>,
    env_vars: Vec<(String, String)>,
    timeout_secs: u64,
}

impl GhidraCommand {
    /// Create a new command builder.
    pub fn new() -> Self {
        Self {
            args: Vec::new(),
            project: None,
            program: None,
            env_vars: Vec::new(),
            timeout_secs: 120,
        }
    }

    /// Add an argument.
    pub fn arg(mut self, arg: impl Into<String>) -> Self {
        self.args.push(arg.into());
        self
    }

    /// Add multiple arguments.
    pub fn args<I, S>(mut self, args: I) -> Self
    where
        I: IntoIterator<Item = S>,
        S: Into<String>,
    {
        for arg in args {
            self.args.push(arg.into());
        }
        self
    }

    /// Set an environment variable.
    pub fn env(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.env_vars.push((key.into(), value.into()));
        self
    }

    /// Configure for bridge connection.
    pub fn with_daemon(mut self, harness: &DaemonTestHarness) -> Self {
        self.project = Some(harness.project().to_string());
        self
    }

    /// Set project and program arguments.
    pub fn with_project(mut self, project: &str, program: &str) -> Self {
        self.project = Some(project.to_string());
        self.program = Some(program.to_string());
        self
    }

    /// Request JSON output format.
    pub fn json_format(self) -> Self {
        self.arg("--format").arg("json")
    }

    /// Set timeout in seconds.
    pub fn timeout(mut self, secs: u64) -> Self {
        self.timeout_secs = secs;
        self
    }

    /// Run the command and return result.
    pub fn run(self) -> GhidraResult {
        let mut cmd = assert_cmd::cargo::cargo_bin_cmd!("ghidra");

        for (key, value) in &self.env_vars {
            cmd.env(key, value);
        }

        for arg in &self.args {
            cmd.arg(arg);
        }

        // Add --project and --program after the subcommand and its args
        if let Some(ref project) = self.project {
            cmd.arg("--project").arg(project);
        }
        if let Some(ref program) = self.program {
            cmd.arg("--program").arg(program);
        }

        cmd.timeout(std::time::Duration::from_secs(self.timeout_secs));

        let output = cmd.output().expect("Failed to run ghidra command");

        GhidraResult {
            exit_code: output.status.code().unwrap_or(-1),
            stdout: String::from_utf8_lossy(&output.stdout).to_string(),
            stderr: String::from_utf8_lossy(&output.stderr).to_string(),
        }
    }
}

impl Default for GhidraCommand {
    fn default() -> Self {
        Self::new()
    }
}

/// Helper to run a ghidra command with common setup.
pub fn ghidra(harness: &DaemonTestHarness) -> GhidraCommand {
    GhidraCommand::new().with_daemon(harness)
}

/// Get the address of a function by name from the test binary.
///
/// Dynamically resolves addresses instead of using hardcoded magic values.
pub fn get_function_address(
    harness: &DaemonTestHarness,
    project: &str,
    program: &str,
    name: &str,
) -> String {
    let result = ghidra(harness)
        .arg("function")
        .arg("list")
        .with_project(project, program)
        .json_format()
        .run();

    result.assert_success();

    let functions: Vec<Function> = result.json();

    functions
        .iter()
        .find(|f| f.name == name || f.name.contains(name))
        .unwrap_or_else(|| {
            let available: Vec<_> = functions.iter().map(|f| f.name.as_str()).collect();
            panic!(
                "Function '{}' not found in program.\nAvailable functions: {:?}",
                name, available
            )
        })
        .address
        .clone()
}

/// Get the first N function addresses from the test binary.
pub fn get_function_addresses(
    harness: &DaemonTestHarness,
    project: &str,
    program: &str,
    count: usize,
) -> Vec<String> {
    let result = ghidra(harness)
        .arg("function")
        .arg("list")
        .with_project(project, program)
        .json_format()
        .arg("--limit")
        .arg(count.to_string())
        .run();

    result.assert_success();

    let functions: Vec<Function> = result.json();
    functions.into_iter().map(|f| f.address).collect()
}

/// Normalize output for snapshot comparison.
///
/// Replaces non-deterministic values (addresses, timestamps, UUIDs) with placeholders.
pub fn normalize_output(output: &str) -> String {
    use regex::Regex;

    // Build patterns without triggering hex literal parsing
    let hex_pattern = ["0", "x", "[0-9a-fA-F]{4,16}"].concat();
    let timestamp_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}";
    let uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}";
    let tmp_path_pattern = r#"/tmp/[^\s"]+"#;

    let hex_addr = Regex::new(&hex_pattern).unwrap();
    let timestamp = Regex::new(timestamp_pattern).unwrap();
    let uuid = Regex::new(uuid_pattern).unwrap();
    let tmp_path = Regex::new(tmp_path_pattern).unwrap();

    let output = hex_addr.replace_all(output, "[ADDR]");
    let output = timestamp.replace_all(&output, "[TIMESTAMP]");
    let output = uuid.replace_all(&output, "[UUID]");
    let output = tmp_path.replace_all(&output, "[TMP_PATH]");

    output.to_string()
}

/// Normalize JSON output for snapshot comparison.
///
/// Parses as JSON, normalizes fields, and re-serializes with consistent formatting.
pub fn normalize_json(output: &str) -> String {
    if let Ok(mut value) = serde_json::from_str::<serde_json::Value>(output) {
        normalize_json_value(&mut value);
        serde_json::to_string_pretty(&value).unwrap_or_else(|_| output.to_string())
    } else {
        output.to_string()
    }
}

fn looks_like_hex_address(s: &str) -> bool {
    let bytes = s.as_bytes();
    bytes.len() > 2
        && bytes[0] == b'0'
        && (bytes[1] == b'x' || bytes[1] == b'X')
        && bytes[2..].iter().all(|&b| b.is_ascii_hexdigit())
}

fn normalize_json_value(value: &mut serde_json::Value) {
    match value {
        serde_json::Value::String(s) => {
            if looks_like_hex_address(s) {
                *s = "[ADDR]".to_string();
            } else if s.starts_with("/tmp/") || s.starts_with("/var/") {
                *s = "[PATH]".to_string();
            }
        }
        serde_json::Value::Array(arr) => {
            for item in arr {
                normalize_json_value(item);
            }
        }
        serde_json::Value::Object(map) => {
            for (key, val) in map {
                // Normalize address fields specifically
                if key == "address" || key == "entry_point" || key == "start" || key == "end" {
                    if let serde_json::Value::String(s) = val {
                        if looks_like_hex_address(s) {
                            *s = "[ADDR]".to_string();
                        }
                    }
                }
                normalize_json_value(val);
            }
        }
        _ => {}
    }
}

/// Fixture paths helper.
pub fn fixture_path(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join(name)
}

/// Check if a function name matches an expected name, accounting for
/// platform differences (macOS adds underscore prefix to C symbols).
pub fn matches_function_name(actual: &str, expected: &str) -> bool {
    actual == expected || actual == format!("_{}", expected)
}
