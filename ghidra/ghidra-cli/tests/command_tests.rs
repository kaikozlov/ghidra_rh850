//! Tests for basic CLI commands that don't require daemon.

use predicates::prelude::*;

#[macro_use]
mod common;

#[test]
fn test_version() {
    require_ghidra!();

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("version")
        .assert()
        .success()
        .stdout(predicate::str::contains("ghidra-cli"));
}

#[test]
fn test_doctor() {
    require_ghidra!();

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("doctor")
        .assert()
        .success()
        .stdout(predicate::str::contains("Ghidra CLI Doctor"));
}

#[test]
fn test_config_list() {
    require_ghidra!();

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("config")
        .arg("list")
        .assert()
        .success()
        .stdout(predicate::str::contains("ghidra_install_dir"));
}

#[test]
fn test_config_get() {
    require_ghidra!();

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("config")
        .arg("get")
        .arg("ghidra_install_dir")
        .assert()
        .success();
}

#[test]
fn test_config_set() {
    require_ghidra!();

    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .arg("config")
        .arg("set")
        .arg("default_output_format")
        .arg("json")
        .assert()
        .success();
}

#[test]
fn test_legacy_config_timeout_is_rejected_with_replacements() {
    require_ghidra!();

    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .arg("config")
        .arg("set")
        .arg("timeout")
        .arg("1800")
        .assert()
        .failure()
        .stderr(predicate::str::contains("GHIDRA_CLI_READ_TIMEOUT"));
}

#[test]
fn test_config_set_launch_timeout() {
    require_ghidra!();

    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .arg("config")
        .arg("set")
        .arg("launch_timeout_secs")
        .arg("240")
        .assert()
        .success();

    let config = std::fs::read_to_string(config_path).unwrap();
    assert!(config.contains("launch_timeout_secs: 240"), "{config}");
}

#[test]
fn portable_invalid_resource_overrides_leave_saved_config_unchanged() {
    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");
    for (key, value) in [("max_heap", "1536m"), ("cpu_workers", "3")] {
        assert_cmd::cargo::cargo_bin_cmd!("ghidra")
            .env("GHIDRA_CLI_CONFIG", &config_path)
            .args(["config", "set", key, value])
            .assert()
            .success();
    }
    let saved = std::fs::read(&config_path).unwrap();
    for (key, value) in [
        ("max_heap", ""),
        ("max_heap", "0G"),
        ("max_heap", "1.5G"),
        ("max_heap", "4GB"),
        ("max_heap", "2G -Xmx64G"),
        ("cpu_workers", "0"),
        ("cpu_workers", "-1"),
        ("cpu_workers", "2147483648"),
        ("cpu_workers", "many"),
    ] {
        assert_cmd::cargo::cargo_bin_cmd!("ghidra")
            .env("GHIDRA_CLI_CONFIG", &config_path)
            .args(["config", "set", key, value])
            .assert()
            .failure();
        assert_eq!(std::fs::read(&config_path).unwrap(), saved, "{key}={value}");
    }
}

#[test]
fn portable_output_options_fail_before_bridge_work() {
    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");
    for (option, value, message) in [
        ("--format", "unknown", "Unknown format"),
        (
            "--filter",
            "name=test garbage",
            "invalid --filter expression",
        ),
    ] {
        assert_cmd::cargo::cargo_bin_cmd!("ghidra")
            .env("GHIDRA_CLI_CONFIG", &config_path)
            .env_remove("GHIDRA_CLI_DEFAULT_LIMIT")
            .args(["function", "list", option, value])
            .assert()
            .failure()
            .stdout(predicate::str::is_empty())
            .stderr(predicate::str::contains(message))
            .stderr(predicate::str::contains("Starting Ghidra").not());
    }
    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .args(["function", "delete", "main", "-o", "c"])
        .assert()
        .failure()
        .stdout(predicate::str::is_empty())
        .stderr(predicate::str::contains("format 'c' requires decompile"))
        .stderr(predicate::str::contains("Starting Ghidra").not());
    assert!(!config_path.exists());
}

#[test]
fn portable_configured_limit_defaults_and_environment_overrides() {
    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");
    let mut config = serde_yaml::to_value(ghidra_cli::config::Config::default()).unwrap();
    config
        .as_mapping_mut()
        .unwrap()
        .remove(serde_yaml::Value::from("default_limit"));
    std::fs::write(&config_path, serde_yaml::to_string(&config).unwrap()).unwrap();

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .env_remove("GHIDRA_CLI_DEFAULT_LIMIT")
        .args(["config", "get", "default_limit"])
        .assert()
        .success()
        .stdout("50\n\n");
    for value in ["0", "7"] {
        assert_cmd::cargo::cargo_bin_cmd!("ghidra")
            .env("GHIDRA_CLI_CONFIG", &config_path)
            .env("GHIDRA_CLI_DEFAULT_LIMIT", value)
            .args(["config", "get", "default_limit"])
            .assert()
            .success()
            .stdout(format!("{value}\n\n"));
    }
    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .env("GHIDRA_CLI_DEFAULT_LIMIT", "invalid")
        .args(["config", "get", "default_limit"])
        .assert()
        .failure()
        .stderr(predicate::str::contains("must be a non-negative integer"));
}

#[test]
fn portable_invalid_output_format_does_not_change_saved_config() {
    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");
    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .args(["config", "set", "default_output_format", "json"])
        .assert()
        .success();
    let original = std::fs::read(&config_path).unwrap();
    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .args(["config", "set", "default_output_format", "nonsense"])
        .assert()
        .failure();
    assert_eq!(std::fs::read(config_path).unwrap(), original);
}

#[test]
fn test_config_reset() {
    require_ghidra!();

    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .arg("config")
        .arg("reset")
        .assert()
        .success();
}

#[test]
fn test_init() {
    require_ghidra!();

    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .arg("init")
        .assert()
        .success();

    assert!(config_path.exists());
}

#[test]
fn test_set_default_program() {
    require_ghidra!();

    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .arg("set-default")
        .arg("program")
        .arg("sample_binary")
        .assert()
        .success()
        .stdout(predicate::str::contains("Default program set"));
}

#[test]
fn test_set_default_project() {
    require_ghidra!();

    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .env("GHIDRA_CLI_CONFIG", &config_path)
        .arg("set-default")
        .arg("project")
        .arg("test-project")
        .assert()
        .success()
        .stdout(predicate::str::contains("Default project set"));
}
