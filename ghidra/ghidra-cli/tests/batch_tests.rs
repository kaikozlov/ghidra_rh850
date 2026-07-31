//! Integration tests for batch file parsing.
//!
//! These tests exercise `ghidra_cli::batch::parse_batch` — the shared parsing
//! logic extracted from the batch command handler — WITHOUT requiring a running
//! Ghidra bridge. They run in CI on ubuntu-latest with only the Rust toolchain.
//!
//! The central invariant under test: **JSON input preserves token boundaries
//! exactly**. A filter value like `name ~ 'crypt'` arriving as a single JSON
//! string must become a single argv element, never re-split on whitespace.

use ghidra_cli::batch::{parse_batch, BatchCommand};

// =========================================================================
// JSON mode — token boundaries preserved exactly (no shell re-splitting)
// =========================================================================

#[test]
fn json_batch_preserves_filter_with_spaces_as_single_token() {
    // The primary regression this guards: the filter "name ~ 'crypt'" must NOT
    // be split into ["name", "~", "'crypt'"]. It's one JSON string value → one
    // argv element.
    let content = r#"[
        {"command": "query", "args": ["functions", "--filter", "name ~ 'crypt'"]}
    ]"#;
    let cmds = parse_batch(content).expect("valid JSON should parse");
    assert_eq!(cmds.len(), 1);
    assert_eq!(
        cmds[0].argv,
        vec!["query", "functions", "--filter", "name ~ 'crypt'"]
    );
    // The filter is exactly ONE argv element, not split.
    assert_eq!(cmds[0].argv.len(), 4);
}

#[test]
fn json_batch_preserves_text_with_spaces() {
    let content = r#"[
        {"command": "comment", "args": ["set", "--text", "hello world from test"]}
    ]"#;
    let cmds = parse_batch(content).unwrap();
    assert_eq!(
        cmds[0].argv,
        vec!["comment", "set", "--text", "hello world from test"]
    );
    assert_eq!(cmds[0].argv.len(), 4, "the comment text is one element");
}

#[test]
fn json_batch_preserves_regex_filter() {
    let content = r#"[
        {"command": "query", "args": ["functions", "--filter", "name ~= /encrypt|decrypt/i"]}
    ]"#;
    let cmds = parse_batch(content).unwrap();
    assert_eq!(
        cmds[0].argv,
        vec!["query", "functions", "--filter", "name ~= /encrypt|decrypt/i"]
    );
}

#[test]
fn json_batch_command_with_no_args() {
    let content = r#"[{"command": "stats"}]"#;
    let cmds = parse_batch(content).unwrap();
    assert_eq!(cmds.len(), 1);
    assert_eq!(cmds[0].argv, vec!["stats"]);
}

#[test]
fn json_batch_multiple_entries_preserve_order() {
    let content = r#"[
        {"command": "query", "args": ["functions"]},
        {"command": "stats"},
        {"command": "query", "args": ["types", "--limit", "10"]}
    ]"#;
    let cmds = parse_batch(content).unwrap();
    assert_eq!(cmds.len(), 3);
    assert_eq!(cmds[0].argv, vec!["query", "functions"]);
    assert_eq!(cmds[1].argv, vec!["stats"]);
    assert_eq!(
        cmds[2].argv,
        vec!["query", "types", "--limit", "10"]
    );
}

#[test]
fn json_batch_display_string_reconstructed() {
    let content = r#"[{"command": "query", "args": ["functions", "--limit", "5"]}]"#;
    let cmds = parse_batch(content).unwrap();
    assert_eq!(cmds[0].display, "query functions --limit 5");
}

#[test]
fn json_batch_rejects_missing_command() {
    let content = r#"[{"args": ["x"]}]"#;
    assert!(parse_batch(content).is_err());
}

#[test]
fn json_batch_rejects_non_string_arg() {
    let content = r#"[{"command": "query", "args": ["ok", 42]}]"#;
    assert!(parse_batch(content).is_err());
}

#[test]
fn json_batch_rejects_malformed_json() {
    let content = "[not valid json";
    assert!(parse_batch(content).is_err());
}

// =========================================================================
// Plain-text mode — shlex splitting with comment/blank skipping
// =========================================================================

#[test]
fn text_batch_basic_split() {
    let content = "query functions --limit 5";
    let cmds = parse_batch(content).unwrap();
    assert_eq!(cmds[0].argv, vec!["query", "functions", "--limit", "5"]);
}

#[test]
fn text_batch_shlex_preserves_quoted_filter() {
    // In plain-text mode the filter is shell-quoted; shlex strips the quotes
    // and yields the filter as a single token.
    let content = r#"query functions --filter "name ~ 'crypt'""#;
    let cmds = parse_batch(content).unwrap();
    assert_eq!(
        cmds[0].argv,
        vec!["query", "functions", "--filter", "name ~ 'crypt'"]
    );
    assert_eq!(cmds[0].argv.len(), 4);
}

#[test]
fn text_batch_skips_comments_and_blanks() {
    let content = "\
# comment line
query functions

# another comment
stats
";
    let cmds = parse_batch(content).unwrap();
    assert_eq!(cmds.len(), 2);
    assert_eq!(cmds[0].argv, vec!["query", "functions"]);
    assert_eq!(cmds[1].argv, vec!["stats"]);
}

#[test]
fn text_batch_multiple_lines() {
    let content = "stats\nquery functions\nquery types";
    let cmds = parse_batch(content).unwrap();
    assert_eq!(cmds.len(), 3);
    assert_eq!(cmds[0].argv, vec!["stats"]);
    assert_eq!(cmds[1].argv, vec!["query", "functions"]);
    assert_eq!(cmds[2].argv, vec!["query", "types"]);
}

#[test]
fn text_batch_rejects_unparseable_line() {
    // Unterminated quote → shlex returns None → error.
    let content = "query functions --filter 'unterminated";
    assert!(parse_batch(content).is_err());
}

// =========================================================================
// Mode selection & edge cases
// =========================================================================

#[test]
fn detects_json_vs_text_by_leading_bracket() {
    let json = r#"[{"command": "stats"}]"#;
    let text = "stats";
    assert_eq!(parse_batch(json).unwrap().len(), 1);
    assert_eq!(parse_batch(text).unwrap().len(), 1);
}

#[test]
fn empty_json_array_produces_no_commands() {
    let cmds = parse_batch("[]").unwrap();
    assert!(cmds.is_empty());
}

#[test]
fn empty_text_produces_no_commands() {
    let cmds = parse_batch("").unwrap();
    assert!(cmds.is_empty());
}

#[test]
fn json_tolerates_leading_whitespace_before_bracket() {
    let content = "  \n  [{\"command\": \"stats\"}]";
    let cmds = parse_batch(content).unwrap();
    assert_eq!(cmds.len(), 1);
}

#[test]
fn batch_command_struct_has_display_and_argv() {
    let cmd = BatchCommand {
        display: "query functions".to_string(),
        argv: vec!["query".to_string(), "functions".to_string()],
    };
    assert_eq!(cmd.display, "query functions");
    assert_eq!(cmd.argv.len(), 2);
}
