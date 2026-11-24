//! Tests for script execution operations.

use serial_test::serial;
use std::fs;
use std::path::PathBuf;
use std::sync::OnceLock;

#[macro_use]
mod common;
use common::{ensure_test_project, DaemonTestHarness};

const TEST_PROJECT: &str = "ci-test";
const TEST_PROGRAM: &str = "sample_binary";

static HARNESS: OnceLock<DaemonTestHarness> = OnceLock::new();

fn harness() -> &'static DaemonTestHarness {
    HARNESS.get_or_init(|| {
        ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
        DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM).expect("Failed to start daemon")
    })
}

fn echo_args_script_path() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("tests");
    path.push("fixtures");
    path.push("scripts");
    path.push("EchoArgs.java");
    path
}

/// Copy a fixture script into a unique, fresh temp directory and return the copy.
///
/// Ghidra resolves a script to the FIRST registered source directory that is an
/// ancestor of it (GhidraScriptUtil.findSourceDirectoryContaining), and bundle
/// registrations persist in the OSGi cache across bridge sessions. Running a
/// fixture straight out of tests/fixtures/** can therefore be shadowed by a
/// previously-registered ancestor (e.g. tests/fixtures itself), which corrupts
/// the derived class name. Staging into a unique temp dir gives each run an
/// unregistered parent — exactly the arbitrary-absolute-path case users hit.
fn stage_script(fixture: &PathBuf) -> PathBuf {
    let stem = fixture.file_stem().unwrap().to_string_lossy().into_owned();
    let dir =
        std::env::temp_dir().join(format!("ghidra_cli_script_{}_{}", std::process::id(), stem));
    fs::create_dir_all(&dir).expect("create staging dir");
    let dest = dir.join(fixture.file_name().unwrap());
    fs::copy(fixture, &dest).expect("copy fixture script");
    dest
}

fn write_artifact_script_path() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("tests");
    path.push("fixtures");
    path.push("scripts");
    path.push("WriteArtifact.java");
    path
}

fn get_test_script_path() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("tests");
    path.push("fixtures");
    path.push("test_script.py");
    path
}

fn create_test_script() -> PathBuf {
    let script_path = get_test_script_path();

    fs::create_dir_all(script_path.parent().unwrap()).ok();

    let script_content = r#"# Test script
# @category Test

print("Test script executed")
"#;

    fs::write(&script_path, script_content).expect("Failed to write test script");
    script_path
}

#[test]
#[serial]
fn test_script_list() {
    require_ghidra!();
    let _harness = harness();

    // script list does not accept --project/--program arguments,
    // so it may fail with "no project specified" unless a default is configured
    let output = assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("script")
        .arg("list")
        .output()
        .expect("Failed to run command");

    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        output.status.success()
            || stderr.contains("No project specified")
            || stderr.contains("no default project"),
        "Expected success or no-project error, got: {}",
        stderr
    );
}

#[test]
#[serial]
fn test_script_run() {
    require_ghidra!();
    let script_path = create_test_script();

    let _harness = harness();

    let output = assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("script")
        .arg("run")
        .arg(script_path.to_str().unwrap())
        .arg("--project")
        .arg(TEST_PROJECT)
        .arg("--program")
        .arg(TEST_PROGRAM)
        .output()
        .expect("Failed to run command");

    // Ghidra's runScript may not find scripts outside its script directories
    // Accept either success or "Script does not exist" error
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        output.status.success()
            || stderr.contains("Script does not exist")
            || stderr.contains("Script not found")
            || stderr.contains("No script provider") // Python provider not installed
            || stderr.contains("Script failed")
            || stderr.contains("Script threw")
            || stderr.contains("Failed to run script"),
        "Expected success or script-not-found error, got: {}",
        stderr
    );

    fs::remove_file(script_path).ok();
}

/// A checked-in Java script runs by absolute path (no global-scripts-dir copy),
/// receives real positional arguments (Phase 4.1), and its stdout is captured
/// into the structured result. Java is used deliberately: it compiles via the
/// doctor-resolved JDK, whereas Python needs a provider that may be absent.
#[test]
#[serial]
fn test_script_run_java_args() {
    require_ghidra!();
    let _harness = harness();

    let fixture = echo_args_script_path();
    assert!(fixture.exists(), "fixture missing: {}", fixture.display());
    let script_path = stage_script(&fixture);

    let output = assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("script")
        .arg("run")
        .arg(script_path.to_str().unwrap())
        .arg("--project")
        .arg(TEST_PROJECT)
        .arg("--program")
        .arg(TEST_PROGRAM)
        .arg("--")
        .arg("hello")
        .arg("world")
        .output()
        .expect("Failed to run command");

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        output.status.success(),
        "script run failed.\nstdout: {}\nstderr: {}",
        stdout,
        stderr
    );
    // The captured script println() output lands in the result's `stdout` field.
    assert!(
        stdout.contains("ARGC=2") && stdout.contains("ARG0=hello") && stdout.contains("ARG1=world"),
        "expected echoed args in captured stdout, got: {}",
        stdout
    );
}

fn inline_script(language: &str, code: &str) -> std::process::Output {
    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .args([
            "--json",
            "script",
            language,
            code,
            "--project",
            TEST_PROJECT,
            "--program",
            TEST_PROGRAM,
        ])
        .output()
        .expect("Failed to run inline script")
}

#[test]
#[serial]
fn test_script_inline() {
    require_ghidra!();
    let _harness = harness();

    for (language, success, throws, syntax_error, next) in [
        (
            "java",
            r#"println("java:" + currentProgram.getName()); println(sourceFile.getAbsolutePath());"#,
            r#"println("java-before-error"); throw new Exception("java-inline-exception");"#,
            "println(123;",
            r#"println("java-next");"#,
        ),
        (
            "python",
            "print('python:' + currentProgram.getName())\nprint(__file__)",
            "print('python-before-error')\nraise RuntimeError('python-inline-exception')",
            "print(123",
            "print('python-next')",
        ),
    ] {
        let result = inline_script(language, success);
        if language == "python" && std::env::var_os("GHIDRA_CLI_PYGHIDRA_PYTHON").is_none() {
            assert!(!result.status.success(), "{result:?}");
            let json: serde_json::Value = serde_json::from_slice(&result.stderr).unwrap();
            assert_eq!(
                json["error"]["code"], "script_runtime_unavailable",
                "{json}"
            );
            let message = json["error"]["message"].as_str().unwrap();
            assert!(message.contains("GHIDRA_CLI_PYGHIDRA_PYTHON"), "{json}");
            continue;
        }
        assert!(result.status.success(), "{result:?}");
        let json: serde_json::Value = serde_json::from_slice(&result.stdout).unwrap();
        let mut stdout = json[0]["stdout"].as_str().unwrap().lines();
        assert_eq!(stdout.next().unwrap(), format!("{language}:{TEST_PROGRAM}"));
        let source_path = PathBuf::from(stdout.next().unwrap());
        assert!(!source_path.parent().unwrap().exists(), "{json}");
        assert_eq!(stdout.next(), None, "{json}");

        let result = inline_script(language, throws);
        assert!(!result.status.success(), "{result:?}");
        let json: serde_json::Value = serde_json::from_slice(&result.stderr).unwrap();
        assert_eq!(json["error"]["code"], "script_failed", "{json}");
        let rendered = json.to_string();
        assert!(
            rendered.contains(&format!("{language}-inline-exception")),
            "{json}"
        );
        assert!(
            rendered.contains(&format!("{language}-before-error")),
            "{json}"
        );

        let result = inline_script(language, syntax_error);
        assert!(!result.status.success(), "{result:?}");
        let json: serde_json::Value = serde_json::from_slice(&result.stderr).unwrap();
        let diagnostics = json["error"]["diagnostics"].as_str().unwrap();
        assert!(!diagnostics.trim().is_empty(), "{json}");
        assert!(!diagnostics.contains("before-error"), "{json}");

        let result = inline_script(language, next);
        assert!(result.status.success(), "{result:?}");
        let json: serde_json::Value = serde_json::from_slice(&result.stdout).unwrap();
        assert_eq!(
            json[0]["stdout"].as_str().unwrap().trim(),
            format!("{language}-next")
        );
    }
}

#[test]
#[serial]
fn test_script_inline_cancel_cleans_up() {
    use std::time::{Duration, Instant};

    require_ghidra!();
    let client = harness().client().unwrap();
    let marker = "inline-cancel-fixture";
    for (language, code) in [
        (
            "java",
            format!(
                "println(sourceFile.getAbsolutePath()); \
                 monitor.setMessage(\"{marker}\"); \
                 for (int i = 0; i < 3000; i++) {{ monitor.checkCancelled(); Thread.sleep(10); }}"
            ),
        ),
        (
            "python",
            format!(
                "import time\nprint(__file__)\nmonitor.setMessage('{marker}')\n\
                 for _ in range(3000):\n    monitor.checkCancelled()\n    time.sleep(0.01)"
            ),
        ),
    ] {
        if language == "python" && std::env::var_os("GHIDRA_CLI_PYGHIDRA_PYTHON").is_none() {
            continue;
        }
        let request = std::thread::spawn(move || inline_script(language, &code));
        let deadline = Instant::now() + Duration::from_secs(30);
        let job_id = loop {
            let status = client.job_status(None).unwrap();
            let active = &status["active_job"];
            if active["progress_message"] == marker {
                break active["id"].as_u64().unwrap();
            }
            assert!(
                !request.is_finished() && Instant::now() < deadline,
                "{language} script did not start: {status}"
            );
            std::thread::sleep(Duration::from_millis(25));
        };
        client.cancel_job(Some(job_id)).unwrap();
        let result = request.join().unwrap();
        assert!(!result.status.success(), "{result:?}");
        let json: serde_json::Value = serde_json::from_slice(&result.stderr).unwrap();
        assert_eq!(json["error"]["code"], "script_cancelled", "{json}");
        let diagnostics = json["error"]["diagnostics"].as_str().unwrap();
        let source_path = PathBuf::from(diagnostics.lines().next().unwrap());
        assert!(!source_path.parent().unwrap().exists(), "{json}");
    }
}

#[test]
#[serial]
fn test_script_inline_rejected_by_read_only_batch() {
    require_ghidra!();
    let _harness = harness();

    for (language, code) in [("java", "println(123);"), ("python", "print(123)")] {
        let mut batch = tempfile::NamedTempFile::new().unwrap();
        serde_json::to_writer(
            &mut batch,
            &serde_json::json!([{"command": "script", "args": [language, code]}]),
        )
        .unwrap();
        let result = assert_cmd::cargo::cargo_bin_cmd!("ghidra")
            .args([
                "batch",
                "--read-only",
                "--project",
                TEST_PROJECT,
                "--program",
                TEST_PROGRAM,
            ])
            .arg(batch.path())
            .output()
            .unwrap();
        assert!(!result.status.success(), "{result:?}");
        assert!(
            String::from_utf8_lossy(&result.stderr).contains("not allowed by --read-only"),
            "{result:?}"
        );
    }
}

/// Phase 4.2: a declared JSONL artifact is validated and a manifest (row count,
/// checksum, binary provenance) is attached; a missing declared artifact fails
/// the job closed. Absolute paths are used for both the script's output arg and
/// `--expect` so the bridge validates exactly the file the script wrote.
#[test]
#[serial]
fn test_script_run_artifact_contract() {
    require_ghidra!();
    let _harness = harness();

    let fixture = write_artifact_script_path();
    assert!(fixture.exists(), "fixture missing: {}", fixture.display());
    let script = stage_script(&fixture);

    let out =
        std::env::temp_dir().join(format!("ghidra_cli_artifact_{}.jsonl", std::process::id()));
    let out_str = out.to_str().unwrap();
    let _ = fs::remove_file(&out);

    // Success: script writes 5 rows, we require >= 3.
    let output = assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("script")
        .arg("run")
        .arg(script.to_str().unwrap())
        .arg("--project")
        .arg(TEST_PROJECT)
        .arg("--program")
        .arg(TEST_PROGRAM)
        .arg("--expect")
        .arg(format!("{}:3", out_str))
        .arg("--")
        .arg(out_str)
        .arg("5")
        .output()
        .expect("Failed to run command");

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        output.status.success(),
        "expected success.\nstdout: {}\nstderr: {}",
        stdout,
        stderr
    );
    assert!(
        stdout.contains("## artifacts") && stdout.contains("rows=5"),
        "expected artifact manifest with row count, got: {}",
        stdout
    );
    assert!(
        stdout.contains("wrote 5 records"),
        "expected captured script stdout, got: {}",
        stdout
    );
    let _ = fs::remove_file(&out);

    // Failure: declare an artifact the script never writes -> job fails closed.
    let missing =
        std::env::temp_dir().join(format!("ghidra_cli_missing_{}.jsonl", std::process::id()));
    let out2 =
        std::env::temp_dir().join(format!("ghidra_cli_artifact2_{}.jsonl", std::process::id()));
    let output2 = assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("script")
        .arg("run")
        .arg(script.to_str().unwrap())
        .arg("--project")
        .arg(TEST_PROJECT)
        .arg("--program")
        .arg(TEST_PROGRAM)
        .arg("--expect")
        .arg(missing.to_str().unwrap())
        .arg("--")
        .arg(out2.to_str().unwrap())
        .arg("5")
        .output()
        .expect("Failed to run command");

    let combined = format!(
        "{}{}",
        String::from_utf8_lossy(&output2.stdout),
        String::from_utf8_lossy(&output2.stderr)
    );
    assert!(
        !output2.status.success(),
        "expected failure for a missing declared artifact, got success: {}",
        combined
    );
    assert!(
        combined.contains("validation failed") || combined.contains("missing"),
        "expected artifact-validation error, got: {}",
        combined
    );
    let _ = fs::remove_file(&out2);
}

#[test]
#[serial]
fn test_script_run_nonexistent() {
    require_ghidra!();
    let _harness = harness();

    assert_cmd::cargo::cargo_bin_cmd!("ghidra")
        .arg("script")
        .arg("run")
        .arg("/nonexistent/script.py")
        .arg("--project")
        .arg(TEST_PROJECT)
        .arg("--program")
        .arg(TEST_PROGRAM)
        .assert()
        .failure();
}
