//! Batch file parsing.
//!
//! Shared between `main.rs` (the batch command handler) and unit/integration
//! tests so the JSON/plain-text parsing logic can be exercised without a
//! running Ghidra bridge.
//!
//! The key invariant — that JSON input preserves token boundaries exactly
//! (no shell re-splitting) — is the whole reason this module exists. A filter
//! like `name ~ 'crypt'` must survive as a single argv element when it comes
//! in as a JSON string value, even though it contains a space and quotes.

use anyhow::{Context, Result};

/// A single parsed batch entry.
///
/// `display` is a human-readable reconstruction used for reporting in batch
/// result output; `argv` is the exact argument vector passed to
/// `Cli::try_parse_from`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BatchCommand {
    /// Human-readable reconstruction of the command (for result reporting).
    pub display: String,
    /// Exact argv vector — passed to the clap parser without re-splitting.
    pub argv: Vec<String>,
}

/// Parse batch file content into a list of commands.
///
/// Two modes, selected by content inspection:
///
/// - **JSON mode**: if the content (after trimming leading whitespace) starts
///   with `[`, it is parsed as a JSON array of `{"command": "...", "args":
///   [...]}` objects. Token boundaries are **exact** — each JSON string value
///   becomes one argv element with no shell splitting. This is critical for
///   filters containing spaces or quotes, e.g. `"name ~ 'crypt'"` must stay
///   intact.
///
/// - **Plain-text mode**: one command per non-empty, non-comment line. Each
///   line is split with `shlex` to preserve shell-style quoting. Lines
///   starting with `#` (after trimming) and blank lines are skipped.
pub fn parse_batch(content: &str) -> Result<Vec<BatchCommand>> {
    if content.trim_start().starts_with('[') {
        parse_json_batch(content)
    } else {
        parse_text_batch(content)
    }
}

/// Parse a JSON array of `{"command":"...","args":[...]}` entries.
///
/// Token boundaries are preserved exactly — each string in the `args` array
/// becomes one argv element, with no shell re-splitting.
fn parse_json_batch(content: &str) -> Result<Vec<BatchCommand>> {
    let entries: Vec<serde_json::Value> =
        serde_json::from_str(content).context("Failed to parse batch file as JSON")?;

    entries
        .iter()
        .map(|entry| {
            let cmd = entry
                .get("command")
                .and_then(|v| v.as_str())
                .context("Each JSON entry needs a \"command\" string")?;

            let mut argv = vec![cmd.to_string()];
            if let Some(extra) = entry.get("args").and_then(|v| v.as_array()) {
                for a in extra {
                    match a.as_str() {
                        Some(s) => argv.push(s.to_string()),
                        None => anyhow::bail!(
                            "Non-string argument in JSON batch entry: {:?}",
                            a
                        ),
                    }
                }
            }

            let display = argv.join(" ");
            Ok(BatchCommand { display, argv })
        })
        .collect()
}

/// Parse plain-text batch content: one shlex-split command per non-comment line.
fn parse_text_batch(content: &str) -> Result<Vec<BatchCommand>> {
    content
        .lines()
        .filter(|l| !l.trim().is_empty() && !l.trim().starts_with('#'))
        .map(|l| {
            let trimmed = l.trim();
            let argv = shlex::split(trimmed).unwrap_or_else(Vec::new);
            if argv.is_empty() {
                anyhow::bail!("Could not parse command line: {:?}", trimmed);
            }
            Ok(BatchCommand {
                display: trimmed.to_string(),
                argv,
            })
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    // ---- JSON mode: token boundaries preserved exactly ----

    #[test]
    fn json_preserves_quoted_filter_as_single_token() {
        // The bug this guards against: the filter "name ~ 'crypt'" must NOT be
        // re-split into ["name", "~", "'crypt'"]. It is a single JSON string
        // value, so it must become exactly one argv element.
        let content = r#"[
            {"command": "query", "args": ["functions", "--filter", "name ~ 'crypt'"]}
        ]"#;
        let cmds = parse_batch(content).unwrap();
        assert_eq!(cmds.len(), 1);
        assert_eq!(
            cmds[0].argv,
            vec!["query", "functions", "--filter", "name ~ 'crypt'"]
        );
    }

    #[test]
    fn json_preserves_spaces_in_args() {
        let content = r#"[
            {"command": "comment", "args": ["set", "--text", "hello world from test"]}
        ]"#;
        let cmds = parse_batch(content).unwrap();
        assert_eq!(
            cmds[0].argv,
            vec!["comment", "set", "--text", "hello world from test"]
        );
        // The text with spaces must be exactly ONE argv element.
        assert_eq!(cmds[0].argv.len(), 4);
    }

    #[test]
    fn json_preserves_special_chars() {
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
    fn json_command_only() {
        let content = r#"[{"command": "stats"}]"#;
        let cmds = parse_batch(content).unwrap();
        assert_eq!(cmds.len(), 1);
        assert_eq!(cmds[0].argv, vec!["stats"]);
    }

    #[test]
    fn json_multiple_entries() {
        let content = r#"[
            {"command": "query", "args": ["functions"]},
            {"command": "stats"}
        ]"#;
        let cmds = parse_batch(content).unwrap();
        assert_eq!(cmds.len(), 2);
        assert_eq!(cmds[0].argv, vec!["query", "functions"]);
        assert_eq!(cmds[1].argv, vec!["stats"]);
    }

    #[test]
    fn json_display_string() {
        let content = r#"[{"command": "query", "args": ["functions", "--limit", "5"]}]"#;
        let cmds = parse_batch(content).unwrap();
        assert_eq!(cmds[0].display, "query functions --limit 5");
    }

    #[test]
    fn json_rejects_missing_command() {
        let content = r#"[{"args": ["x"]}]"#;
        assert!(parse_batch(content).is_err());
    }

    #[test]
    fn json_rejects_non_string_arg() {
        let content = r#"[{"command": "query", "args": ["ok", 42]}]"#;
        assert!(parse_batch(content).is_err());
    }

    #[test]
    fn json_rejects_malformed_json() {
        let content = "[not valid json";
        assert!(parse_batch(content).is_err());
    }

    #[test]
    fn json_tolerates_leading_whitespace() {
        let content = "  \n  [{\"command\": \"stats\"}]";
        let cmds = parse_batch(content).unwrap();
        assert_eq!(cmds.len(), 1);
    }

    // ---- Plain-text mode: shlex splitting ----

    #[test]
    fn text_basic_split() {
        let content = "query functions --limit 5";
        let cmds = parse_batch(content).unwrap();
        assert_eq!(
            cmds[0].argv,
            vec!["query", "functions", "--limit", "5"]
        );
    }

    #[test]
    fn text_shlex_preserves_quoted_filter() {
        // In plain-text mode, the filter is shell-quoted; shlex should split
        // it into [command, subcommand, --filter, <filter-value>].
        let content = r#"query functions --filter "name ~ 'crypt'""#;
        let cmds = parse_batch(content).unwrap();
        assert_eq!(
            cmds[0].argv,
            vec!["query", "functions", "--filter", "name ~ 'crypt'"]
        );
        assert_eq!(cmds[0].argv.len(), 4);
    }

    #[test]
    fn text_skips_comments_and_blanks() {
        let content = "\
# This is a comment
query functions

# Another comment
stats
";
        let cmds = parse_batch(content).unwrap();
        assert_eq!(cmds.len(), 2);
        assert_eq!(cmds[0].argv, vec!["query", "functions"]);
        assert_eq!(cmds[1].argv, vec!["stats"]);
    }

    #[test]
    fn text_multiple_lines() {
        let content = "stats\nquery functions\nquery types";
        let cmds = parse_batch(content).unwrap();
        assert_eq!(cmds.len(), 3);
        assert_eq!(cmds[0].argv, vec!["stats"]);
        assert_eq!(cmds[1].argv, vec!["query", "functions"]);
        assert_eq!(cmds[2].argv, vec!["query", "types"]);
    }

    #[test]
    fn text_rejects_unparseable_line() {
        // An unterminated quote is invalid shlex → empty argv → error.
        let content = "query functions --filter 'unterminated";
        assert!(parse_batch(content).is_err());
    }

    #[test]
    fn text_preserves_equals_in_args() {
        let content = "query functions --filter=name~crypt";
        let cmds = parse_batch(content).unwrap();
        assert_eq!(cmds[0].argv, vec!["query", "functions", "--filter=name~crypt"]);
    }

    // ---- Mode selection ----

    #[test]
    fn detects_json_vs_text_by_leading_bracket() {
        let json = r#"[{"command": "stats"}]"#;
        let text = "stats";
        // Both should parse successfully; the dispatch is internal.
        assert!(parse_batch(json).unwrap().len() == 1);
        assert!(parse_batch(text).unwrap().len() == 1);
    }

    #[test]
    fn empty_json_array() {
        let cmds = parse_batch("[]").unwrap();
        assert!(cmds.is_empty());
    }

    #[test]
    fn empty_text() {
        let cmds = parse_batch("").unwrap();
        assert!(cmds.is_empty());
    }
}
