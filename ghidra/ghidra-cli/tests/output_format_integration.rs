//! Exercise the public output contract against real bridge responses.

#[macro_use]
mod common;

use common::{ensure_test_project, ghidra, DaemonTestHarness, GhidraResult};
use ghidra_cli::config::Config;
use serde_json::Value;

const TEST_PROJECT: &str = "ci-test";
const TEST_PROGRAM: &str = "sample_binary";

#[test]
fn output_contract_with_live_bridge() {
    require_ghidra!();
    ensure_test_project(TEST_PROJECT, TEST_PROGRAM);
    let harness = DaemonTestHarness::new(TEST_PROJECT, TEST_PROGRAM)
        .expect("Failed to start output-contract bridge");

    let temp = tempfile::tempdir().unwrap();
    let config_path = temp.path().join("config.yaml");
    let mut config = Config::load().unwrap();
    config.default_output_format = Some("auto".into());
    config.default_limit = Some(3);
    config.ghidra_project_dir = Some(Config::default_project_dir().unwrap());
    std::fs::write(&config_path, serde_yaml::to_string(&config).unwrap()).unwrap();

    let run = |args: &[&str]| -> GhidraResult {
        let result = ghidra(&harness)
            .with_project(TEST_PROJECT, TEST_PROGRAM)
            .env("GHIDRA_CLI_CONFIG", config_path.to_string_lossy())
            .env("GHIDRA_CLI_DEFAULT_LIMIT", "3")
            .env(
                "GHIDRA_PROJECT_DIR",
                Config::default_project_dir().unwrap().to_string_lossy(),
            )
            .args(args.iter().copied())
            .run();
        result.assert_success();
        result
    };

    let all_result = run(&["--json", "function", "list", "--limit", "0"]);
    let all: Vec<Value> = all_result.json();
    assert!(all.len() > 5, "Fixture needs multiple pages of functions");
    assert!(
        !all_result.stderr.contains("showing"),
        "{}",
        all_result.stderr
    );

    let compact = run(&["function", "list"]);
    assert_eq!(
        compact
            .stdout
            .lines()
            .filter(|line| line.starts_with("0x"))
            .count(),
        3
    );
    assert!(
        serde_json::from_str::<Value>(&compact.stdout).is_err(),
        "{}",
        compact.stdout
    );
    assert!(!compact.stdout.contains("showing"), "{}", compact.stdout);
    assert!(compact.stderr.contains("showing"), "{}", compact.stderr);

    let json = run(&["--json", "function", "list"]);
    assert_eq!(json.json::<Vec<Value>>(), all[..3]);
    assert_eq!(json.stdout.trim().lines().count(), 1);
    let pretty = run(&["--pretty", "function", "list"]);
    assert_eq!(pretty.json::<Vec<Value>>(), all[..3]);
    assert!(pretty.stdout.trim().lines().count() > 1);
    let explicit = run(&["--json", "function", "list", "-o", "compact"]);
    assert_eq!(explicit.stdout, compact.stdout);
    let explicit_json = run(&["function", "list", "-o", "json"]);
    assert_eq!(explicit_json.json::<Vec<Value>>(), all[..3]);

    let exact_limit = all.len().to_string();
    let exact = run(&["--json", "function", "list", "--limit", &exact_limit]);
    assert_eq!(exact.json::<Vec<Value>>(), all);
    assert!(!exact.stderr.contains("showing"), "{}", exact.stderr);

    let offset = run(&[
        "--json", "function", "list", "--offset", "3", "--limit", "2",
    ]);
    assert_eq!(offset.json::<Vec<Value>>(), all[3..5]);
    assert!(offset.stderr.contains("showing"), "{}", offset.stderr);
    let final_offset = (all.len() - 2).to_string();
    let final_page = run(&[
        "--json",
        "function",
        "list",
        "--offset",
        &final_offset,
        "--limit",
        "2",
    ]);
    assert_eq!(final_page.json::<Vec<Value>>(), all[all.len() - 2..]);
    assert!(
        !final_page.stderr.contains("showing"),
        "{}",
        final_page.stderr
    );

    let count = run(&["function", "list", "--count", "--limit", "0"]);
    assert_eq!(count.stdout.trim(), all.len().to_string());
    assert!(!count.stderr.contains("showing"), "{}", count.stderr);
    let page_count = run(&[
        "function", "list", "--count", "--offset", "3", "--limit", "2",
    ]);
    assert_eq!(page_count.stdout.trim(), "2");

    let filtered = run(&[
        "--json",
        "function",
        "list",
        "--filter",
        "name~add_numbers",
        "--limit",
        "0",
    ]);
    let functions: Vec<Value> = filtered.json();
    assert!(!functions.is_empty(), "Fixture must contain add_numbers");
    assert!(functions
        .iter()
        .all(|row| row["name"].as_str().unwrap().contains("add_numbers")));
    let address = functions[0]["address"].as_str().unwrap();

    let selected = run(&[
        "--json",
        "function",
        "list",
        "--fields",
        "address,name",
        "--limit",
        "2",
    ]);
    let fields: Vec<Value> = selected.json();
    assert!(fields.iter().all(|row| row.as_object().unwrap().len() == 2));
    let csv = run(&[
        "function",
        "list",
        "--fields",
        "address,name",
        "--limit",
        "2",
        "-o",
        "csv",
    ]);
    let mut csv_reader = csv::Reader::from_reader(csv.stdout.as_bytes());
    assert_eq!(
        csv_reader.headers().unwrap().iter().collect::<Vec<_>>(),
        vec!["address", "name"]
    );
    assert_eq!(csv_reader.records().count(), 2);

    let decompile_json = run(&["--json", "decompile", address]);
    let decompilation: Vec<Value> = decompile_json.json();
    let code = decompilation[0]["code"].as_str().unwrap();
    let decompile = run(&["decompile", address]);
    assert_eq!(decompile.stdout.trim_end(), code.trim_end());
    let source = run(&["decompile", address, "--with-params", "-o", "c"]);
    assert_eq!(source.stdout.trim_end(), code.trim_end());
    let params_json = run(&["--json", "decompile", address, "--with-params"]);
    let with_params: Vec<Value> = params_json.json();
    let params = with_params[0]["params"].as_array().unwrap();
    assert!(
        !params.is_empty(),
        "add_numbers should have decompiler parameters"
    );
    let params_text = run(&["decompile", address, "--with-params"]);
    assert!(
        params_text.stdout.contains("## params"),
        "{}",
        params_text.stdout
    );
    for param in params {
        assert!(
            params_text
                .stdout
                .contains(param["storage"].as_str().unwrap()),
            "{}",
            params_text.stdout
        );
    }

    let asm_json = run(&["--json", "disasm", address, "--instructions", "2"]);
    let instructions: Vec<Value> = asm_json.json();
    assert_eq!(instructions.len(), 2);
    let asm = run(&["disasm", address, "--instructions", "2"]);
    let explicit_asm = run(&["disasm", address, "--instructions", "2", "-o", "asm"]);
    assert_eq!(asm.stdout, explicit_asm.stdout);
    assert_eq!(asm.stdout.lines().count(), 2);
    for instruction in &instructions {
        assert!(
            asm.stdout
                .contains(instruction["address"].as_str().unwrap()),
            "{}",
            asm.stdout
        );
        assert!(
            asm.stdout
                .contains(instruction["mnemonic"].as_str().unwrap()),
            "{}",
            asm.stdout
        );
    }

    let memory = run(&["memory", "read", address, "16"]);
    let explicit_hex = run(&["memory", "read", address, "16", "-o", "hex"]);
    assert_eq!(memory.stdout, explicit_hex.stdout);
    assert!(
        memory.stdout.starts_with("0x") && memory.stdout.contains('|'),
        "{}",
        memory.stdout
    );

    let inspect_args = [
        "inspect",
        address,
        "--decompile",
        "--disasm",
        "3",
        "--callers",
        "--callees",
        "--xrefs",
        "--limit",
        "2",
    ];
    let mut json_inspect_args = vec!["--json"];
    json_inspect_args.extend(inspect_args);
    let inspect_json = run(&json_inspect_args);
    let inspection: Vec<Value> = inspect_json.json();
    let inspection = &inspection[0];
    let inspect = run(&inspect_args);
    assert!(
        inspect.stdout.starts_with("## function\n"),
        "{}",
        inspect.stdout
    );
    for section in [
        "function",
        "decompilation",
        "disassembly",
        "callers",
        "callees",
        "xrefs_to",
        "xrefs_from",
    ] {
        assert!(inspection.get(section).is_some(), "{inspection}");
        assert!(
            inspect.stdout.contains(&format!("## {section}\n")),
            "{}",
            inspect.stdout
        );
    }
    assert!(
        inspection["decompilation"].get("params").is_some(),
        "{inspection}"
    );
    assert!(
        inspect
            .stdout
            .contains(inspection["decompilation"]["code"].as_str().unwrap().trim()),
        "{}",
        inspect.stdout
    );
    assert!(
        !inspect.stdout.contains("## params") && !inspect.stdout.contains("## variables"),
        "{}",
        inspect.stdout
    );
    assert!(!inspect.stdout.contains("showing"), "{}", inspect.stdout);
    let any_section_truncated = inspection
        .as_object()
        .unwrap()
        .values()
        .any(|section| section.get("truncated").and_then(Value::as_bool) == Some(true));
    if any_section_truncated {
        assert!(inspect.stderr.contains("showing"), "{}", inspect.stderr);
    }

    let graph_json = run(&["--json", "graph", "calls", "--limit", "2"]);
    let graphs: Vec<Value> = graph_json.json();
    let graph = &graphs[0];
    assert_eq!(graph["nodes"].as_array().unwrap().len(), 2);
    assert_eq!(graph["node_count"], 2);
    let graph_text = run(&["graph", "calls", "--limit", "2"]);
    assert!(
        graph_text.stdout.contains("## nodes\n"),
        "{}",
        graph_text.stdout
    );
    for node in graph["nodes"].as_array().unwrap() {
        assert!(
            graph_text
                .stdout
                .contains(node["address"].as_str().unwrap()),
            "{}",
            graph_text.stdout
        );
        assert!(
            graph_text.stdout.contains(node["name"].as_str().unwrap()),
            "{}",
            graph_text.stdout
        );
    }
    assert!(
        !graph_text.stdout.contains("showing"),
        "{}",
        graph_text.stdout
    );
    assert!(
        graph_text.stderr.contains("showing"),
        "{}",
        graph_text.stderr
    );
}
