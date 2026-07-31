//! Integration tests for output format
//! Tests require real Ghidra installation

/// Helper to verify Ghidra is installed before running tests
fn require_ghidra() {
    let output = assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("doctor")
        .output()
        .expect("Failed to run ghidra doctor");

    if !output.status.success() {
        panic!("Ghidra is not installed. Tests require Ghidra installation per AGENTS.md");
    }
}

#[test]
fn test_format_detection_tty() {
    require_ghidra();

    // Test that --help shows both --json and --pretty flags
    let mut cmd = assert_cmd::cargo::cargo_bin_cmd!("ghidra");
    cmd.arg("--help");
    cmd.assert().success();

    let output = cmd.output().unwrap();
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("--json"), "Help should show --json flag");
    assert!(
        stdout.contains("--pretty"),
        "Help should show --pretty flag"
    );
}

#[test]
fn test_json_flag() {
    require_ghidra();

    // Test --json flag is recognized
    let mut cmd = assert_cmd::cargo::cargo_bin_cmd!("ghidra");
    cmd.arg("--json").arg("--help");
    cmd.assert().success();
}

#[test]
fn test_pretty_flag() {
    require_ghidra();

    // Test --pretty flag is recognized
    let mut cmd = assert_cmd::cargo::cargo_bin_cmd!("ghidra");
    cmd.arg("--pretty").arg("--help");
    cmd.assert().success();
}
