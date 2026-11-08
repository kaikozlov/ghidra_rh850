use crate::error::{GhidraError, Result};
use comfy_table::{presets::UTF8_FULL, Table};
use serde::Serialize;
use serde_json::Value as JsonValue;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OutputFormat {
    Full,
    Compact,
    Minimal,
    Json,
    JsonCompact,
    JsonStream,
    Csv,
    Tsv,
    Table,
    Ids,
    Count,
    Hex,
    Asm,
    C,
}

impl OutputFormat {
    pub fn from_str(s: &str) -> Result<Self> {
        match s.to_lowercase().as_str() {
            "full" => Ok(Self::Full),
            "compact" => Ok(Self::Compact),
            "minimal" => Ok(Self::Minimal),
            "json" => Ok(Self::Json),
            "json-compact" => Ok(Self::JsonCompact),
            "json-stream" | "ndjson" => Ok(Self::JsonStream),
            "csv" => Ok(Self::Csv),
            "tsv" => Ok(Self::Tsv),
            "table" => Ok(Self::Table),
            "ids" => Ok(Self::Ids),
            "count" => Ok(Self::Count),
            "tree" => Err(GhidraError::InvalidFormat(
                "tree is not supported; use compact for graph reports or graph export dot".into(),
            )),
            "hex" => Ok(Self::Hex),
            "asm" => Ok(Self::Asm),
            "c" => Ok(Self::C),
            _ => Err(GhidraError::InvalidFormat(format!("Unknown format: {}", s))),
        }
    }
}

pub trait Formatter {
    fn format<T: Serialize>(&self, data: &[T], format: OutputFormat) -> Result<String>;
}

pub struct DefaultFormatter;

impl Formatter for DefaultFormatter {
    fn format<T: Serialize>(&self, data: &[T], format: OutputFormat) -> Result<String> {
        match format {
            OutputFormat::Json => serde_json::to_string_pretty(data).map_err(|e| e.into()),
            OutputFormat::JsonCompact => serde_json::to_string(data).map_err(|e| e.into()),
            OutputFormat::JsonStream => {
                let mut result = String::new();
                for item in data {
                    let json = serde_json::to_string(item)?;
                    result.push_str(&json);
                    result.push('\n');
                }
                Ok(result)
            }
            OutputFormat::Count => Ok(format!("{}", data.len())),
            OutputFormat::Table => format_table(data),
            OutputFormat::Csv => format_csv(data, ','),
            OutputFormat::Tsv => format_csv(data, '\t'),
            OutputFormat::Compact => format_compact(data),
            OutputFormat::Full => format_full(data),
            OutputFormat::Minimal | OutputFormat::Ids => format_minimal(data),
            OutputFormat::C | OutputFormat::Asm | OutputFormat::Hex => format_source(data, format),
        }
    }
}

fn table_columns(data: &[JsonValue]) -> Vec<String> {
    let mut columns = std::collections::BTreeSet::new();
    for item in data {
        if let JsonValue::Object(map) = item {
            columns.extend(map.keys().cloned());
        } else {
            columns.insert("value".into());
        }
    }
    columns.into_iter().collect()
}

fn table_cell(item: &JsonValue, key: &str) -> String {
    let value = if let JsonValue::Object(map) = item {
        map.get(key)
    } else if key == "value" {
        Some(item)
    } else {
        None
    };
    match value {
        Some(JsonValue::String(text)) => text.clone(),
        Some(value) => value.to_string(),
        None => String::new(),
    }
}

fn format_table<T: Serialize>(data: &[T]) -> Result<String> {
    if data.is_empty() {
        return Ok("No results".to_string());
    }
    let rows: Vec<JsonValue> = data
        .iter()
        .map(serde_json::to_value)
        .collect::<std::result::Result<_, _>>()?;
    let columns = table_columns(&rows);
    let mut table = Table::new();
    table.load_preset(UTF8_FULL);
    table.set_header(&columns);
    for row in &rows {
        table.add_row(columns.iter().map(|key| table_cell(row, key)));
    }
    Ok(table.to_string())
}

fn format_csv<T: Serialize>(data: &[T], delimiter: char) -> Result<String> {
    if data.is_empty() {
        return Ok(String::new());
    }
    let rows: Vec<JsonValue> = data
        .iter()
        .map(serde_json::to_value)
        .collect::<std::result::Result<_, _>>()?;
    let columns = table_columns(&rows);
    let mut writer = csv::WriterBuilder::new()
        .delimiter(delimiter as u8)
        .from_writer(Vec::new());
    let csv_error = |error| GhidraError::IoError(std::io::Error::other(error));
    writer.write_record(&columns).map_err(csv_error)?;
    for row in &rows {
        writer
            .write_record(columns.iter().map(|key| table_cell(row, key)))
            .map_err(csv_error)?;
    }
    let bytes = writer
        .into_inner()
        .map_err(|error| GhidraError::IoError(error.into_error()))?;
    String::from_utf8(bytes).map_err(|error| GhidraError::InvalidFormat(error.to_string()))
}

fn format_source<T: Serialize>(data: &[T], format: OutputFormat) -> Result<String> {
    let mut out = String::new();
    for item in data {
        let value = serde_json::to_value(item)?;
        let map = value.as_object().ok_or_else(|| {
            GhidraError::InvalidFormat(format!("{format:?} requires structured source data"))
        })?;
        match format {
            OutputFormat::C if entity_kind(map) == Some("decompile") => {
                render_decompile(map, false, &mut out);
            }
            OutputFormat::Asm if entity_kind(map) == Some("instruction") => {
                render_instruction(map, &mut out);
            }
            OutputFormat::Hex if entity_kind(map) == Some("memory") => {
                render_memory(map, &mut out);
            }
            _ => {
                let command = match format {
                    OutputFormat::C => "decompile",
                    OutputFormat::Asm => "disasm",
                    OutputFormat::Hex => "memory read",
                    _ => unreachable!(),
                };
                return Err(GhidraError::InvalidFormat(format!(
                    "{format:?} requires {command} results; use compact or json for this command"
                )));
            }
        }
    }
    Ok(out)
}

/// Compact human/agent format: one line per item, layout chosen by the
/// item's field signature (see docs/output-format.md).
fn format_compact<T: Serialize>(data: &[T]) -> Result<String> {
    let json_data: Vec<JsonValue> = data
        .iter()
        .map(serde_json::to_value)
        .collect::<std::result::Result<Vec<_>, _>>()?;

    if json_data.is_empty() {
        return Ok("No results".to_string());
    }

    let mut out = String::new();

    // A lone stats wrapper is presentation noise; render its payload directly.
    if json_data.len() == 1 {
        if let JsonValue::Object(map) = &json_data[0] {
            if map.len() == 1 {
                if let Some(JsonValue::Object(stats)) = map.get("stats") {
                    render_kv_block(stats, &mut out);
                    return Ok(out.trim_end().to_string());
                }
            }

            // Reference tracing deliberately carries a global xref envelope plus
            // per-source reference sites. Render the latter once, grouped by type,
            // instead of repeating the same references twice.
            if map.contains_key("target")
                && map.contains_key("references")
                && map.contains_key("source_functions")
            {
                render_trace_report(map, &mut out);
                return Ok(out.trim_end().to_string());
            }

            // Detailed type objects carry components/members in addition to the
            // list-row fields. Preserve those details instead of collapsing the
            // whole object to a one-line type row.
            if entity_kind(map) == Some("data_type") && has_type_details(map) {
                render_data_type_detail(map, &mut out);
                return Ok(out.trim_end().to_string());
            }

            // A single function detail deserves its signature; multi-row function
            // lists stay one line per item.
            if entity_kind(map) == Some("function") && map.contains_key("signature") {
                render_function_detail(map, &mut out);
                return Ok(out.trim_end().to_string());
            }

            if map.len() == 2 && map.contains_key("inspection") && map.contains_key("target") {
                render_compact_item(map, &mut out);
                return Ok(out.trim_end().to_string());
            }

            if entity_kind(map).is_none() {
                let section_like = map.values().any(|v| v.is_object() || v.is_array());
                if section_like {
                    render_sections(map, &mut out);
                } else {
                    render_kv_block(map, &mut out);
                }
                return Ok(out.trim_end().to_string());
            }
        }
    }

    for item in &json_data {
        match item {
            JsonValue::Object(map) => render_compact_item(map, &mut out),
            other => {
                out.push_str(&format_json_value(other));
                out.push('\n');
            }
        }
    }

    Ok(out)
}

/// Field-signature classification for compact rendering.
fn entity_kind(map: &serde_json::Map<String, JsonValue>) -> Option<&'static str> {
    if map.contains_key("status") || map.contains_key("error") {
        None
    } else if get_str(map, "code").is_some()
        && !map.contains_key("message")
        && !map.contains_key("diagnostics")
    {
        Some("decompile")
    } else if get_str(map, "format") == Some("dot") && get_str(map, "output").is_some() {
        Some("graph_source")
    } else if map.contains_key("mnemonic") {
        Some("instruction")
    } else if map.contains_key("from") && map.contains_key("to") && map.contains_key("ref_type") {
        Some("xref")
    } else if map.contains_key("from") && map.contains_key("to") && map.contains_key("type") {
        Some("graph_edge")
    } else if map.contains_key("hex") && map.contains_key("size") && map.contains_key("address") {
        Some("memory")
    } else if map.contains_key("address") && map.contains_key("value") && map.contains_key("length")
    {
        Some("string")
    } else if map.contains_key("address")
        && map.contains_key("name")
        && map.contains_key("reasons")
        && map.contains_key("xrefs")
    {
        Some("interesting_function")
    } else if map.contains_key("address") && map.contains_key("caller") && map.contains_key("type")
    {
        Some("call_hit")
    } else if map.contains_key("address") && map.contains_key("name") && map.contains_key("library")
    {
        Some("import")
    } else if map.len() == 2 && map.contains_key("address") && map.contains_key("name") {
        Some("named_address")
    } else if map.contains_key("name")
        && map.contains_key("address")
        && map.get("size").is_some_and(|v| v.is_u64())
    {
        Some("function")
    } else if map.contains_key("entry") && map.contains_key("reference_sites") {
        Some("source_function")
    } else if map.contains_key("address")
        && map.contains_key("name")
        && map.contains_key("call_site")
    {
        Some("call_relation")
    } else if map.contains_key("id") && map.contains_key("address") && map.contains_key("name") {
        Some("graph_node")
    } else if map.contains_key("kind") && map.contains_key("path") && map.contains_key("name") {
        Some("data_type")
    } else if map.contains_key("offset") && map.contains_key("type") && map.contains_key("name") {
        Some("type_component")
    } else if map.len() == 2 && map.contains_key("name") && map.contains_key("value") {
        Some("enum_member")
    } else if map.contains_key("pattern_length")
        && map.contains_key("address")
        && map.contains_key("type")
    {
        Some("crypto_hit")
    } else if map.contains_key("current") && map.contains_key("name") && map.contains_key("path") {
        Some("program")
    } else if map.contains_key("start")
        && map.contains_key("end")
        && map.contains_key("permissions")
    {
        Some("section")
    } else if map.contains_key("text") && (map.contains_key("address") || map.contains_key("type"))
    {
        Some("comment")
    } else if map.len() == 1 && map.contains_key("address") {
        Some("address")
    } else if map.contains_key("address")
        && map.contains_key("source")
        && map.contains_key("type")
        && map.contains_key("name")
    {
        Some("symbol")
    } else if map.contains_key("storage") && map.contains_key("type") && map.contains_key("name") {
        Some("variable")
    } else {
        None
    }
}

fn render_compact_item(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    // Multi-target inspection wrapper: exactly {"inspection": {...}, "target": "..."}
    if map.len() == 2
        && map.contains_key("inspection")
        && map.get("inspection").is_some_and(|v| v.is_object())
    {
        if let Some(inner) = map.get("inspection").and_then(|v| v.as_object()) {
            if let Some(target) = get_str(map, "target") {
                out.push_str(&format!("# {}\n", target));
            }
            render_sections(inner, out);
            return;
        }
    }
    match entity_kind(map) {
        Some("comment") => {
            let prefix = get_str(map, "address")
                .map(|address| format!("{:<10}  ", norm_addr(address)))
                .unwrap_or_default();
            let typ = get_str(map, "type").unwrap_or("");
            let text = get_str(map, "text").unwrap_or("");
            let prefix = format!("{}{:6} ", prefix, typ);
            let continuation = format!("\n{}", " ".repeat(prefix.len()));
            out.push_str(&format!(
                "{}{}\n",
                prefix,
                text.replace('\n', &continuation)
            ));
        }
        Some("graph_source") => {
            let text = get_str(map, "output").unwrap_or("");
            out.push_str(text);
            if !text.ends_with('\n') {
                out.push('\n');
            }
        }
        Some("address") => {
            out.push_str(&norm_addr(get_str(map, "address").unwrap_or("")));
            out.push('\n');
        }
        Some("source_function") => {
            let entry = norm_addr(get_str(map, "entry").unwrap_or(""));
            let name = get_str(map, "name").unwrap_or("");
            out.push_str(&format!("{:<10}  {}\n", entry, name));
            if let Some(JsonValue::Array(sites)) = map.get("reference_sites") {
                render_reference_sites(sites, "  ", out);
            }
            if let Some(inner) = map.get("inspection").and_then(|v| v.as_object()) {
                render_sections(inner, out);
            }
        }
        Some("section") => {
            let start = norm_addr(get_str(map, "start").unwrap_or(""));
            let end = norm_addr(get_str(map, "end").unwrap_or(""));
            let perms = get_str(map, "permissions").unwrap_or("");
            let size = map.get("size").and_then(|v| v.as_u64()).unwrap_or(0);
            let name = get_str(map, "name").unwrap_or("");
            out.push_str(&format!(
                "{:<10}-{:<10} {:<5} {:<8} {}",
                start, end, perms, size, name
            ));
            for (key, label) in [
                ("is_initialized", "uninitialized"),
                ("is_loaded", "unloaded"),
            ] {
                if map.get(key).and_then(JsonValue::as_bool) == Some(false) {
                    out.push_str(&format!("  {}", label));
                }
            }
            out.push('\n');
        }
        Some("decompile") => render_decompile(map, true, out),
        Some("instruction") => render_instruction(map, out),
        Some("xref") => render_xref(map, out),
        Some("graph_edge") => render_graph_edge(map, out),
        Some("graph_node") => render_graph_node(map, out),
        Some("call_relation") => render_call_relation(map, out),
        Some("data_type") => render_data_type(map, out),
        Some("type_component") => render_type_component(map, out),
        Some("enum_member") => render_enum_member(map, out),
        Some("crypto_hit") => render_crypto_hit(map, out),
        Some("program") => render_program(map, out),
        Some("memory") => render_memory(map, out),
        Some("string") => render_string(map, out),
        Some("interesting_function") => render_interesting_function(map, out),
        Some("call_hit") => render_call_hit(map, out),
        Some("import") => render_import(map, out),
        Some("named_address") => render_named_address(map, out),
        Some("function") => render_function(map, out),
        Some("symbol") => render_symbol(map, out),
        Some("variable") => render_variable(map, out),
        _ => {
            // Compound report (e.g. inspect): sections of entities.
            if map.values().any(|v| v.is_object() || v.is_array()) {
                render_sections(map, out);
            } else {
                render_kv_line(map, out);
            }
        }
    }
}

/// Normalize an address string to a `0x`-prefixed form, keeping emitted width.
fn norm_addr(s: &str) -> String {
    if s.starts_with("0x")
        || s.starts_with("0X")
        || s.is_empty()
        || !s.chars().all(|c| c.is_ascii_hexdigit())
    {
        s.to_string()
    } else {
        format!("0x{}", s)
    }
}

fn get_str<'a>(map: &'a serde_json::Map<String, JsonValue>, key: &str) -> Option<&'a str> {
    map.get(key).and_then(|v| v.as_str())
}

fn render_decompile(
    map: &serde_json::Map<String, JsonValue>,
    with_details: bool,
    out: &mut String,
) {
    let code = get_str(map, "code").unwrap_or("");
    out.push_str(code);
    if !code.ends_with('\n') {
        out.push('\n');
    }
    if with_details {
        for key in ["params", "variables"] {
            if let Some(JsonValue::Array(items)) = map.get(key) {
                if !items.is_empty() {
                    out.push_str(&format!("## {}\n", key));
                    render_array(items, out);
                }
            }
        }
    }
}

fn render_variable(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let storage = get_str(map, "storage").unwrap_or("");
    let typ = get_str(map, "type").unwrap_or("");
    let name = get_str(map, "name").unwrap_or("");
    out.push_str(&format!("{:<16} {:<20} {}\n", storage, typ, name));
}

fn render_instruction(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let bytes = get_str(map, "bytes").unwrap_or("");
    let mnemonic = get_str(map, "mnemonic").unwrap_or("");
    let operands = match map.get("operands") {
        Some(JsonValue::Array(ops)) => ops
            .iter()
            .map(format_json_value)
            .collect::<Vec<_>>()
            .join(", "),
        _ => String::new(),
    };
    let text = if operands.is_empty() {
        mnemonic.to_string()
    } else {
        format!("{} {}", mnemonic, operands)
    };
    out.push_str(&format!("{:<10}  {:<12} {}\n", addr, bytes, text));
}

fn render_xref(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let from = norm_addr(get_str(map, "from").unwrap_or(""));
    let from_fn = get_str(map, "from_function").unwrap_or("");
    let ref_type = get_str(map, "ref_type").unwrap_or("");
    let to = norm_addr(get_str(map, "to").unwrap_or(""));
    let to_fn = get_str(map, "to_function").unwrap_or("");
    let mut line = format!("{:<10}  {:<28} {:<14} → {}", from, from_fn, ref_type, to);
    if !to_fn.is_empty() {
        line.push_str(&format!("  {}", to_fn));
    }
    out.push_str(&line);
    out.push('\n');
}

fn render_string(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let len = map.get("length").and_then(|v| v.as_u64()).unwrap_or(0);
    let value = get_str(map, "value").unwrap_or("");
    out.push_str(&format!(
        "{:<10}  {:<4} {}\n",
        addr,
        len,
        escape_string(value, 60)
    ));
}

/// Preserve Unicode, escape controls and delimiters, and mark clipped previews.
fn escape_string(s: &str, max_chars: usize) -> String {
    let mut escaped = String::new();
    let mut width = 0;
    for ch in s.chars() {
        let part = match ch {
            '"' => "\\\"".to_string(),
            '\\' => "\\\\".to_string(),
            '\n' => "\\n".to_string(),
            '\r' => "\\r".to_string(),
            '\t' => "\\t".to_string(),
            ch if ch.is_ascii_control() => format!("\\x{:02x}", ch as u32),
            ch if ch.is_control() => format!("\\u{{{:x}}}", ch as u32),
            ch => ch.to_string(),
        };
        let part_width = part.chars().count();
        if width + part_width > max_chars {
            escaped.push('…');
            break;
        }
        escaped.push_str(&part);
        width += part_width;
    }
    format!("\"{}\"", escaped)
}

fn render_interesting_function(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let size = map.get("size").and_then(|v| v.as_u64()).unwrap_or(0);
    let name = get_str(map, "name").unwrap_or("");
    let xrefs = map.get("xrefs").and_then(|v| v.as_u64()).unwrap_or(0);
    let reasons = map
        .get("reasons")
        .and_then(|v| v.as_array())
        .map(|items| {
            items
                .iter()
                .map(format_json_value)
                .collect::<Vec<_>>()
                .join("; ")
        })
        .unwrap_or_default();

    out.push_str(&format!("{:<10}  {:<6} {}", addr, size, name));
    if xrefs > 0 {
        out.push_str(&format!("  xrefs={}", xrefs));
    }
    if !reasons.is_empty() {
        out.push_str(&format!("  # {}", reasons));
    }
    out.push('\n');
}

fn render_call_hit(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let caller = get_str(map, "caller").unwrap_or("");
    let typ = get_str(map, "type").unwrap_or("");
    out.push_str(&format!("{:<10}  {:<28} {}\n", addr, caller, typ));
}

fn render_import(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let name = get_str(map, "name").unwrap_or("");
    let library = get_str(map, "library").unwrap_or("");
    out.push_str(&format!("{:<10}  {}", addr, name));
    if !library.is_empty() {
        out.push_str(&format!("  [{}]", library));
    }
    out.push('\n');
}

fn render_named_address(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let name = get_str(map, "name").unwrap_or("");
    out.push_str(&format!("{:<10}  {}\n", addr, name));
}

fn render_function(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let size = map.get("size").and_then(|v| v.as_u64()).unwrap_or(0);
    let name = get_str(map, "name").unwrap_or("");
    out.push_str(&format!("{:<10}  {:<6} {}", addr, size, name));
    if let Some(comment) = get_str(map, "comment") {
        if !comment.is_empty() {
            out.push_str(&format!("  # {}", comment));
        }
    }
    out.push('\n');
}

fn render_function_detail(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    render_function(map, out);
    if let Some(sig) = get_str(map, "signature") {
        out.push_str("  ");
        out.push_str(sig);
        out.push('\n');
    }
    if let Some(cc) = get_str(map, "calling_convention") {
        if !matches!(cc, "" | "unknown" | "default" | "Unknown")
            && !get_str(map, "signature").is_some_and(|signature| signature.contains(cc))
        {
            out.push_str(&format!("  calling convention: {}\n", cc));
        }
    }
}

fn render_graph_edge(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let from = norm_addr(get_str(map, "from").unwrap_or(""));
    let to = norm_addr(get_str(map, "to").unwrap_or(""));
    let typ = get_str(map, "type").unwrap_or("");
    out.push_str(&format!(
        "{} → {}{}\n",
        from,
        to,
        if typ.is_empty() {
            String::new()
        } else {
            format!("  {}", typ)
        }
    ));
}

fn render_graph_node(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let name = get_str(map, "name").unwrap_or("");
    out.push_str(&format!("{:<10}  {}\n", addr, name));
}

fn render_call_relation(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let name = get_str(map, "name").unwrap_or("");
    let site = norm_addr(get_str(map, "call_site").unwrap_or(""));
    let depth = map.get("depth").and_then(|v| v.as_u64()).unwrap_or(0);
    out.push_str(&format!("{:<10}  {:<28} @ {}", addr, name, site));
    if depth > 0 {
        out.push_str(&format!("  depth={}", depth));
    }
    out.push('\n');
}

fn render_data_type(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let size = map.get("size").map(format_json_value).unwrap_or_default();
    let kind = get_str(map, "kind").unwrap_or("");
    let path = get_str(map, "path")
        .or_else(|| get_str(map, "name"))
        .unwrap_or("");
    out.push_str(&format!("{:<6} {:<10} {}\n", size, kind, path));
}

fn has_type_details(map: &serde_json::Map<String, JsonValue>) -> bool {
    [
        "components",
        "members",
        "description",
        "base_type",
        "base_type_path",
    ]
    .iter()
    .any(|key| map.contains_key(*key))
}

fn render_data_type_detail(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    render_data_type(map, out);

    if let Some(description) = get_str(map, "description") {
        if !description.is_empty() {
            out.push_str(&format!("  {}\n", description));
        }
    }
    if let Some(base) = get_str(map, "base_type_path").or_else(|| get_str(map, "base_type")) {
        out.push_str(&format!("  base: {}\n", base));
    }

    for key in ["components", "members"] {
        let Some(JsonValue::Array(items)) = map.get(key) else {
            continue;
        };
        if items.is_empty() {
            continue;
        }
        out.push_str(&format!("## {}\n", key));
        for item in items {
            if let JsonValue::Object(inner) = item {
                render_compact_item(inner, out);
            }
        }
    }
}

fn render_type_component(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let offset = map.get("offset").and_then(|v| v.as_u64()).unwrap_or(0);
    let size = map.get("size").and_then(|v| v.as_u64()).unwrap_or(0);
    let typ = get_str(map, "type").unwrap_or("");
    let name = get_str(map, "name").unwrap_or("");
    out.push_str(&format!(
        "+0x{:04x}  {:<5} {:<20} {}\n",
        offset, size, typ, name
    ));
}

fn render_enum_member(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let name = get_str(map, "name").unwrap_or("");
    let value = map.get("value").map(format_json_value).unwrap_or_default();
    out.push_str(&format!("{:<12} {}\n", value, name));
}

fn render_crypto_hit(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let typ = get_str(map, "type").unwrap_or("");
    let len = map
        .get("pattern_length")
        .and_then(|v| v.as_u64())
        .unwrap_or(0);
    out.push_str(&format!("{:<10}  {:<5} {}\n", addr, len, typ));
}

fn render_program(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let path = get_str(map, "path")
        .or_else(|| get_str(map, "name"))
        .unwrap_or("");
    let current = map
        .get("current")
        .and_then(|v| v.as_bool())
        .unwrap_or(false);
    out.push_str(&format!("{}{}", if current { "*" } else { " " }, path));
    if let Some(functions) = map.get("function_count").and_then(|v| v.as_u64()) {
        out.push_str(&format!("  {} functions", functions));
    }
    if map.get("analyzed").and_then(|v| v.as_bool()) == Some(true) {
        out.push_str("  analyzed");
    }
    if let Some(format) = get_str(map, "executable_format") {
        out.push_str(&format!("  [{}]", format));
    }
    out.push('\n');
}

fn render_symbol(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let addr = norm_addr(get_str(map, "address").unwrap_or(""));
    let name = get_str(map, "name").unwrap_or("");
    let sym_type = get_str(map, "type").unwrap_or("");
    let user_defined = get_str(map, "source") == Some("USER_DEFINED");
    out.push_str(&format!(
        "{:<10}  {}{}{}{}\n",
        addr,
        if user_defined { "*" } else { "" },
        name,
        if sym_type.is_empty() || sym_type == "Label" {
            String::new()
        } else {
            format!(" ({})", sym_type)
        },
        if map.get("is_primary").and_then(JsonValue::as_bool) == Some(false) {
            " (secondary)"
        } else {
            ""
        }
    ));
}

fn render_memory(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let base = get_str(map, "address").unwrap_or("");
    let hex = get_str(map, "hex").unwrap_or("");
    let (space, digits) = base
        .rsplit_once(':')
        .map_or(("", base), |(space, digits)| (space, digits));
    let digits = digits
        .strip_prefix("0x")
        .or_else(|| digits.strip_prefix("0X"))
        .unwrap_or(digits);
    let Ok(base_val) = u64::from_str_radix(digits, 16) else {
        render_kv_block(map, out);
        return;
    };
    if hex.len() % 2 != 0
        || !hex.bytes().all(|byte| byte.is_ascii_hexdigit())
        || base_val
            .checked_add((hex.len() / 2).saturating_sub(1) as u64)
            .is_none()
    {
        render_kv_block(map, out);
        return;
    }

    let bytes: Vec<u8> = hex
        .as_bytes()
        .chunks_exact(2)
        .map(|pair| {
            let high = (pair[0] as char).to_digit(16).unwrap();
            let low = (pair[1] as char).to_digit(16).unwrap();
            ((high << 4) | low) as u8
        })
        .collect();
    let prefix = if space.is_empty() {
        String::new()
    } else {
        format!("{}:", space)
    };
    for (row, chunk) in bytes.chunks(16).enumerate() {
        let addr = format!(
            "{}0x{:0width$x}",
            prefix,
            base_val + (row * 16) as u64,
            width = digits.len()
        );
        let hex_part: Vec<String> = chunk.iter().map(|byte| format!("{:02x}", byte)).collect();
        let ascii: String = chunk
            .iter()
            .map(|&byte| {
                if (0x20..0x7f).contains(&byte) {
                    byte as char
                } else {
                    '.'
                }
            })
            .collect();
        out.push_str(&format!(
            "{:<10}  {:<49}|{}|\n",
            addr,
            hex_part.join(" "),
            ascii
        ));
    }
    if bytes.is_empty() {
        out.push_str(&format!("{}  0 bytes\n", norm_addr(base)));
    }
}

fn render_trace_report(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let target = norm_addr(get_str(map, "target").unwrap_or(""));
    let reference_count = map
        .get("references")
        .and_then(|v| v.as_object())
        .and_then(|refs| refs.get("count"))
        .and_then(|v| v.as_u64())
        .unwrap_or(0);
    let source_count = map
        .get("source_function_count")
        .and_then(|v| v.as_u64())
        .unwrap_or_else(|| {
            map.get("source_functions")
                .and_then(|v| v.as_array())
                .map(|rows| rows.len() as u64)
                .unwrap_or(0)
        });
    let unowned_count = map
        .get("unowned_reference_sites")
        .and_then(|v| v.as_array())
        .map(|rows| rows.len())
        .unwrap_or(0);

    out.push_str(&format!(
        "{}  {} refs  {} source functions",
        target, reference_count, source_count
    ));
    if unowned_count > 0 {
        out.push_str(&format!("  {} unowned", unowned_count));
    }
    out.push('\n');

    if let Some(JsonValue::Array(sources)) = map.get("source_functions") {
        if !sources.is_empty() {
            out.push_str("## source_functions\n");
            for source in sources {
                if let JsonValue::Object(source) = source {
                    render_compact_item(source, out);
                }
            }
        }
    }

    if let Some(JsonValue::Array(sites)) = map.get("unowned_reference_sites") {
        if !sites.is_empty() {
            out.push_str("## unowned_reference_sites\n");
            render_reference_sites(sites, "", out);
        }
    }
}

fn render_reference_sites(sites: &[JsonValue], indent: &str, out: &mut String) {
    let mut by_type: std::collections::BTreeMap<String, Vec<String>> =
        std::collections::BTreeMap::new();
    for site in sites {
        let JsonValue::Object(site) = site else {
            continue;
        };
        let from = norm_addr(get_str(site, "from").unwrap_or(""));
        let ref_type = get_str(site, "ref_type").unwrap_or("ref").to_string();
        by_type.entry(ref_type).or_default().push(from);
    }

    for (ref_type, addresses) in by_type {
        out.push_str(&format!(
            "{}{} ({}): {}\n",
            indent,
            ref_type,
            addresses.len(),
            addresses.join(", ")
        ));
    }
}

fn render_array(items: &[JsonValue], out: &mut String) {
    if items.is_empty() {
        out.push_str("No results\n");
    }
    for item in items {
        match item {
            JsonValue::Object(map) => render_compact_item(map, out),
            JsonValue::Array(items) => render_array(items, out),
            value => {
                out.push_str(&format_json_value(value));
                out.push('\n');
            }
        }
    }
}

fn section_collection(map: &serde_json::Map<String, JsonValue>) -> Option<&[JsonValue]> {
    let mut collection = None;
    for (key, value) in map {
        if let JsonValue::Array(items) = value {
            if collection.is_some() {
                return None;
            }
            collection = Some(items.as_slice());
        } else if !matches!(key.as_str(), "count" | "function" | "target" | "truncated") {
            return None;
        }
    }
    collection
}

/// Compound reports retain every requested section, including empty results.
fn render_sections(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    for (key, value) in map {
        if !value.is_object()
            && !value.is_array()
            && !is_noise_value(value)
            && !is_default_field(key, value)
        {
            out.push_str(&format!("{}: {}\n", key, format_json_value(value)));
        }
    }

    let mut sections: Vec<_> = map
        .iter()
        .filter(|(_, value)| value.is_object() || value.is_array())
        .collect();
    sections.sort_by_key(|(key, _)| match key.as_str() {
        "function" => 0,
        "decompilation" => 1,
        "disassembly" => 2,
        "callers" => 3,
        "callees" => 4,
        "xrefs_to" => 5,
        "xrefs_from" => 6,
        _ => 7,
    });
    let has_code = map
        .get("decompilation")
        .and_then(|value| value.get("code"))
        .is_some_and(|value| value.is_string());

    for (key, value) in sections {
        let mut body = String::new();
        match value {
            JsonValue::Array(items) => render_array(items, &mut body),
            JsonValue::Object(inner) => match entity_kind(inner) {
                Some("decompile") => render_decompile(inner, key != "decompilation", &mut body),
                Some("function") if inner.contains_key("signature") && !has_code => {
                    render_function_detail(inner, &mut body);
                }
                Some("data_type") if has_type_details(inner) => {
                    render_data_type_detail(inner, &mut body);
                }
                Some(_) => render_compact_item(inner, &mut body),
                None => {
                    if let Some(items) = section_collection(inner) {
                        for (name, value) in inner {
                            if value.is_array()
                                || is_noise_value(value)
                                || is_default_field(name, value)
                                || name == "count" && value.as_u64() == Some(items.len() as u64)
                            {
                                continue;
                            }
                            body.push_str(&format!("{}: {}\n", name, format_json_value(value)));
                        }
                        render_array(items, &mut body);
                    } else if inner
                        .values()
                        .any(|value| value.is_object() || value.is_array())
                    {
                        render_sections(inner, &mut body);
                    } else {
                        render_kv_block(inner, &mut body);
                    }
                }
            },
            _ => unreachable!(),
        }
        if !body.trim_end().is_empty() {
            out.push_str(&format!("## {}\n{}\n", key, body.trim_end()));
        }
    }
}

/// `key: value` block for a lone non-entity object, one nesting level flattened.
fn render_kv_block(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let width = map.keys().map(|k| k.len()).max().unwrap_or(0);
    for (key, value) in map {
        match value {
            JsonValue::Object(inner) => {
                out.push_str(&format!("{}:\n", key));
                let inner_width = inner.keys().map(|k| k.len()).max().unwrap_or(0);
                for (k, v) in inner {
                    if is_noise_value(v) || is_default_field(k, v) {
                        continue;
                    }
                    out.push_str(&format!(
                        "  {:<width$} {}\n",
                        format!("{}:", k),
                        format_json_value(v),
                        width = inner_width + 1
                    ));
                }
            }
            v if is_noise_value(v) || is_default_field(key, v) => continue,
            v => out.push_str(&format!(
                "{:<width$} {}\n",
                format!("{}:", key),
                format_json_value(v),
                width = width + 1
            )),
        }
    }
}

/// Single-line `key=value` fallback with null/empty/default values omitted.
fn render_kv_line(map: &serde_json::Map<String, JsonValue>, out: &mut String) {
    let kv: Vec<String> = map
        .iter()
        .filter(|(k, v)| !is_noise_value(v) && !is_default_field(k, v))
        .map(|(k, v)| format!("{}={}", k, format_json_value(v)))
        .collect();
    if kv.is_empty() {
        return;
    }
    out.push_str(&kv.join("  "));
    out.push('\n');
}

fn is_noise_value(v: &JsonValue) -> bool {
    matches!(v, JsonValue::Null)
        || v.as_str().map(|s| s.is_empty()).unwrap_or(false)
        || matches!(v, JsonValue::Array(a) if a.is_empty())
}

/// Fields that carry no information at their default value.
fn is_default_field(key: &str, v: &JsonValue) -> bool {
    match key {
        "calling_convention" => matches!(
            v.as_str(),
            Some("unknown") | Some("default") | Some("Unknown")
        ),
        "is_primary" => v.as_bool() == Some(true),
        "truncated" => true, // surfaced once on stderr by the output pipeline
        _ => false,
    }
}

/// Full human-readable format: multi-line labeled blocks per item.
fn format_full<T: Serialize>(data: &[T]) -> Result<String> {
    let json_data: Vec<JsonValue> = data
        .iter()
        .map(serde_json::to_value)
        .collect::<std::result::Result<Vec<_>, _>>()?;

    if json_data.is_empty() {
        return Ok("No results".to_string());
    }

    let mut result = String::new();

    for (i, item) in json_data.iter().enumerate() {
        if i > 0 {
            result.push_str("---\n");
        }

        match item {
            JsonValue::Object(map) => {
                // Special case: decompile response
                if let Some(code) = map.get("code").and_then(|v| v.as_str()) {
                    if let Some(sig) = map.get("signature").and_then(|v| v.as_str()) {
                        result.push_str(&format!("Signature: {}\n", sig));
                    }
                    if let Some(name) = map.get("name").and_then(|v| v.as_str()) {
                        result.push_str(&format!("Function:  {}\n", name));
                    }
                    result.push('\n');
                    result.push_str(code);
                    if !code.ends_with('\n') {
                        result.push('\n');
                    }
                    if let Some(JsonValue::Array(params)) = map.get("params") {
                        if !params.is_empty() {
                            result.push_str("\nParameters:\n");
                            for p in params {
                                if let JsonValue::Object(obj) = p {
                                    let name =
                                        obj.get("name").and_then(|v| v.as_str()).unwrap_or("?");
                                    let typ =
                                        obj.get("type").and_then(|v| v.as_str()).unwrap_or("?");
                                    let storage =
                                        obj.get("storage").and_then(|v| v.as_str()).unwrap_or("?");
                                    result.push_str(&format!("  {} {} ({})\n", typ, name, storage));
                                }
                            }
                        }
                    }
                    if let Some(JsonValue::Array(vars)) = map.get("variables") {
                        if !vars.is_empty() {
                            result.push_str("\nVariables:\n");
                            for v in vars {
                                if let JsonValue::Object(obj) = v {
                                    let name =
                                        obj.get("name").and_then(|v| v.as_str()).unwrap_or("?");
                                    let typ =
                                        obj.get("type").and_then(|v| v.as_str()).unwrap_or("?");
                                    let storage =
                                        obj.get("storage").and_then(|v| v.as_str()).unwrap_or("?");
                                    result.push_str(&format!("  {} {} ({})\n", typ, name, storage));
                                }
                            }
                        }
                    }
                    continue;
                }

                // Calculate max key width for alignment
                let max_key = map.keys().map(|k| k.len()).max().unwrap_or(0);

                for (key, val) in map {
                    let formatted = format_json_value(val);
                    result.push_str(&format!(
                        "{:width$}  {}\n",
                        format!("{}:", key),
                        formatted,
                        width = max_key + 1
                    ));
                }
            }
            _ => {
                result.push_str(&format_json_value(item));
                result.push('\n');
            }
        }
    }

    Ok(result)
}

fn format_minimal<T: Serialize>(data: &[T]) -> Result<String> {
    let json_data: Vec<JsonValue> = data
        .iter()
        .map(serde_json::to_value)
        .collect::<std::result::Result<Vec<_>, _>>()?;

    let mut result = String::new();

    for item in &json_data {
        if let JsonValue::Object(map) = item {
            // Try to get address or name or first field
            let value = map
                .get("address")
                .or_else(|| map.get("name"))
                .or_else(|| map.get("id"))
                .or_else(|| map.values().next())
                .map(format_json_value)
                .unwrap_or_else(|| "".to_string());

            result.push_str(&value);
            result.push('\n');
        } else {
            result.push_str(&format_json_value(item));
            result.push('\n');
        }
    }

    Ok(result)
}

fn format_json_value(value: &JsonValue) -> String {
    match value {
        JsonValue::Null => "null".to_string(),
        JsonValue::Bool(b) => b.to_string(),
        JsonValue::Number(n) => n.to_string(),
        JsonValue::String(s) => s.clone(),
        JsonValue::Array(arr) => {
            format!(
                "[{}]",
                arr.iter()
                    .map(format_json_value)
                    .collect::<Vec<_>>()
                    .join(", ")
            )
        }
        JsonValue::Object(_) => serde_json::to_string(value).unwrap_or_else(|_| "{}".to_string()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_format_json() {
        let data = vec![json!({"name": "test", "value": 123})];
        let formatter = DefaultFormatter;
        let result = formatter.format(&data, OutputFormat::Json).unwrap();
        assert!(result.contains("test"));
    }

    #[test]
    fn test_format_count() {
        let data = vec![json!({"name": "test1"}), json!({"name": "test2"})];
        let formatter = DefaultFormatter;
        let result = formatter.format(&data, OutputFormat::Count).unwrap();
        assert_eq!(result, "2");
    }

    #[test]
    fn test_compact_function() {
        let data = vec![json!({
            "address": "000001b0",
            "name": "reset_context_and_startup",
            "size": 782,
            "signature": "void reset_context_and_startup(void)",
            "calling_convention": "__stdcall",
            "comment": null,
            "entry_point": "000001b0"
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(
            out,
            "0x000001b0  782    reset_context_and_startup\n  void reset_context_and_startup(void)\n  calling convention: __stdcall"
        );
    }

    #[test]
    fn test_compact_function_comment() {
        let data = vec![json!({
            "address": "0x00008ef4",
            "name": "aes_init",
            "size": 40,
            "comment": "master key schedule"
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(out, "0x00008ef4  40     aes_init  # master key schedule\n");
    }

    #[test]
    fn test_compact_instruction() {
        let data = vec![json!({
            "address": "000001b4",
            "bytes": "0008",
            "mnemonic": "mov",
            "operands": ["r0", "r1"]
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(out, "0x000001b4  0008         mov r0, r1\n");
    }

    #[test]
    fn test_compact_xref() {
        let data = vec![json!({
            "from": "00000002",
            "from_function": "reset_vector",
            "ref_type": "COMPUTED_JUMP",
            "to": "000001b0",
            "to_function": "reset_context_and_startup"
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(out.contains("0x00000002"), "{}", out);
        assert!(out.contains("reset_vector"), "{}", out);
        assert!(out.contains("COMPUTED_JUMP  → 0x000001b0"), "{}", out);
    }

    #[test]
    fn test_compact_string_escapes_control_bytes() {
        let data = vec![json!({
            "address": "00008ef4",
            "length": 3,
            "value": "a\u{2}b"
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(out, "0x00008ef4  3    \"a\\x02b\"\n");
    }

    #[test]
    fn test_compact_symbol() {
        let data = vec![json!({
            "address": "00008ff1",
            "name": "AES_Encryption_SBox",
            "type": "Label",
            "source": "USER_DEFINED",
            "is_primary": true
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(out, "0x00008ff1  *AES_Encryption_SBox\n");
    }

    #[test]
    fn test_compact_memory_hexdump() {
        let data = vec![json!({
            "address": "0x000001b0",
            "size": 4,
            "hex": "e0076001"
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(
            out,
            "0x000001b0  e0 07 60 01                                      |..`.|\n"
        );
    }

    #[test]
    fn test_compact_summary_kv_block() {
        let data = vec![json!({
            "name": "CodeFlash.bin",
            "function_count": 7336,
            "compiler": null
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(out.contains("name:"), "{}", out);
        assert!(!out.contains("compiler"), "{}", out);
    }

    #[test]
    fn test_compact_decompile_raw_code() {
        let data = vec![json!({
            "address": "000001b0",
            "signature": "void f(void)",
            "code": "void f(void)\n{\n  int x = 1;\n}\n"
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(out, "void f(void)\n{\n  int x = 1;\n}\n");
        assert_eq!(out.matches("void f(void)").count(), 1);
    }

    #[test]
    fn test_compact_comment() {
        let data = vec![json!({
            "address": "00008ff1",
            "type": "EOL",
            "text": "Crypt constant AES_Encryption_SBox - 256 bytes"
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(
            out,
            "0x00008ff1  EOL    Crypt constant AES_Encryption_SBox - 256 bytes\n"
        );
    }

    #[test]
    fn test_compact_bare_address() {
        let data = vec![
            json!({"address": "0000013a"}),
            json!({"address": "000001b0"}),
        ];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(out, "0x0000013a\n0x000001b0\n");
    }

    #[test]
    fn test_compact_type_rows_drop_redundant_fields() {
        let data = vec![json!({
            "category": "/CamryF33",
            "kind": "struct",
            "name": "F33AcquisitionGroupPair",
            "path": "/CamryF33/F33AcquisitionGroupPair",
            "size": 24
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(out, "24     struct     /CamryF33/F33AcquisitionGroupPair\n");
    }

    #[test]
    fn test_compact_type_detail_preserves_components() {
        let data = vec![json!({
            "category": "/CamryF33",
            "description": "",
            "kind": "struct",
            "name": "F33AcquisitionGroupPair",
            "path": "/CamryF33/F33AcquisitionGroupPair",
            "size": 24,
            "components": [
                {"name": "group0", "offset": 0, "size": 12, "type": "ushort[6]"},
                {"name": "group8", "offset": 12, "size": 12, "type": "ushort[6]"}
            ]
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(out.contains("## components"), "{out}");
        assert!(out.contains("+0x0000  12    ushort[6]"), "{out}");
        assert!(out.contains("group8"), "{out}");
    }

    #[test]
    fn test_compact_interesting_function_preserves_reasons() {
        let data = vec![json!({
            "address": "00085a5c",
            "name": "aes128_encrypt_context_block_in_place_85a5c",
            "size": 2372,
            "xrefs": 3,
            "reasons": ["large function (2372 bytes)", "suspicious name"]
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(out.contains("xrefs=3"), "{out}");
        assert!(
            out.contains("large function (2372 bytes); suspicious name"),
            "{out}"
        );
    }

    #[test]
    fn test_compact_call_hit_is_one_line() {
        let data = vec![json!({
            "address": "00000130",
            "caller": "boot_eiint_context",
            "type": "UNCONDITIONAL_CALL"
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert_eq!(out.lines().count(), 1, "{out}");
        assert!(out.contains("boot_eiint_context"), "{out}");
    }

    #[test]
    fn test_nested_decompilation_keeps_code_when_metadata_has_arrays() {
        let data = vec![json!({
            "decompilation": {
                "address": "00000100",
                "code": "void f(void)\n{\n  return;\n}\n",
                "name": "f",
                "params": [{"name": "unused", "type": "int", "size": 4, "storage": "r6:4"}],
                "signature": "void f(void)",
                "variables": []
            }
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(out.contains("void f(void)\n{\n  return;\n}"), "{out}");
        assert!(!out.contains("name=unused"), "{out}");
    }

    #[test]
    fn test_nested_collection_preserves_all_bridge_trimmed_rows() {
        let data = vec![json!({
            "callers": {
                "count": 2,
                "truncated": true,
                "callers": [
                    {"address": "00000100", "name": "a", "call_site": "00000110", "depth": 0},
                    {"address": "00000200", "name": "b", "call_site": "00000210", "depth": 0}
                ]
            }
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(out.contains("0x00000100"), "{out}");
        assert!(out.contains("0x00000200"), "{out}");
        assert!(!out.contains("showing first"), "{out}");
    }

    #[test]
    fn test_trace_report_groups_reference_sites_without_duplicate_global_xrefs() {
        let data = vec![json!({
            "target": "00008ff1",
            "references": {
                "count": 3,
                "xrefs": [
                    {"from": "00001010", "to": "00008ff1", "ref_type": "DATA"},
                    {"from": "00001020", "to": "00008ff1", "ref_type": "DATA"},
                    {"from": "00002010", "to": "00008ff1", "ref_type": "READ"}
                ]
            },
            "source_function_count": 1,
            "source_functions": [{
                "entry": "00001000",
                "name": "uses_table",
                "reference_sites": [
                    {"from": "00001010", "ref_type": "DATA"},
                    {"from": "00001020", "ref_type": "DATA"}
                ],
                "inspection": {
                    "decompilation": {
                        "address": "00001000",
                        "code": "void uses_table(void)\n{\n  return;\n}\n",
                        "name": "uses_table",
                        "params": [],
                        "signature": "void uses_table(void)",
                        "variables": []
                    },
                    "function": {
                        "address": "00001000",
                        "name": "uses_table",
                        "size": 16,
                        "signature": "void uses_table(void)"
                    }
                }
            }],
            "unowned_reference_sites": [{"from": "00002010", "ref_type": "READ"}]
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(
            out.contains("0x00008ff1  3 refs  1 source functions  1 unowned"),
            "{out}"
        );
        assert!(out.contains("DATA (2): 0x00001010, 0x00001020"), "{out}");
        assert!(out.contains("READ (1): 0x00002010"), "{out}");
        assert_eq!(out.matches("0x00001010").count(), 1, "{out}");
        assert!(
            out.contains("void uses_table(void)\n{\n  return;\n}"),
            "{out}"
        );
    }

    #[test]
    fn test_compact_mutations_keep_status_and_function_identity() {
        for response in [
            json!({"status":"signature_set", "function":"updated", "address":"0010", "signature":"int updated(int x)"}),
            json!({"status":"return_type_set", "function":"updated", "return_type":"long", "signature":"long updated(int x)"}),
            json!({"status":"calling_convention_set", "function":"updated", "calling_convention":"__stdcall", "signature":"int updated(int x)"}),
        ] {
            let out = DefaultFormatter
                .format(&[response.clone()], OutputFormat::Compact)
                .unwrap();
            assert!(out.contains(response["status"].as_str().unwrap()), "{out}");
            assert!(out.contains("updated"), "{out}");
            assert!(
                out.contains(response["signature"].as_str().unwrap()),
                "{out}"
            );
            assert!(!out.contains("  0 "), "{out}");
        }
        let error = json!({"code":"SCRIPT_COMPILE_FAILED", "message":"Cannot compile", "diagnostics":"missing symbol"});
        let out = DefaultFormatter
            .format(&[error], OutputFormat::Compact)
            .unwrap();
        assert!(
            out.contains("Cannot compile") && out.contains("missing symbol"),
            "{out}"
        );
    }

    #[test]
    fn test_compact_typedef_preserves_underlying_type_and_unknown_size() {
        let data = [json!({
            "name":"sample_t", "kind":"typedef", "path":"/sample_t",
            "size":-1, "base_type":"string", "base_type_path":"/builtin/string"
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(out.contains("-1") && out.contains("/sample_t"), "{out}");
        assert!(out.contains("base: /builtin/string"), "{out}");
    }

    #[test]
    fn test_compact_nested_report_preserves_scalars_all_arrays_and_empty_sections() {
        let data = [json!({
            "report": {
                "name": "comparison",
                "memory_size": 128,
                "warnings": ["first warning", "second warning"],
                "blocks": [{"name":"text", "start":"0010", "end":"001f", "size":16, "permissions":"r-x"}],
                "details": {"values":[3, 7], "label":"details retained"},
                "missing":[]
            }
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        for expected in [
            "comparison",
            "128",
            "first warning",
            "second warning",
            "0x0010",
            "text",
            "details retained",
            "3\n7",
            "## missing\nNo results",
        ] {
            assert!(out.contains(expected), "missing {expected:?}: {out}");
        }
        assert!(!out.contains("{\""), "{out}");
    }

    #[test]
    fn test_explicit_decompile_details_and_inspect_code_are_distinct() {
        let decompile = json!({
            "address":"0010", "name":"f", "signature":"int f(int x)",
            "code":"int f(int x)\n{\n  return x;\n}\n",
            "params":[{"name":"x", "type":"int", "size":4, "storage":"r6:4"}],
            "variables":[{"name":"local", "type":"int", "size":4, "storage":"Stack[-4]:4"}]
        });
        let explicit = DefaultFormatter
            .format(&[decompile.clone()], OutputFormat::Compact)
            .unwrap();
        for expected in ["## params", "r6:4", "## variables", "Stack[-4]:4"] {
            assert!(explicit.contains(expected), "{explicit}");
        }
        let inspection = json!({
            "function": {"address":"0010", "name":"f", "size":12, "signature":"int f(int x)"},
            "decompilation":decompile,
            "callers":{"count":0, "callers":[]}
        });
        let nested = DefaultFormatter
            .format(&[inspection], OutputFormat::Compact)
            .unwrap();
        assert!(nested.starts_with("## function\n"), "{nested}");
        assert_eq!(nested.matches("int f(int x)").count(), 1, "{nested}");
        assert!(
            !nested.contains("r6:4") && !nested.contains("Stack[-4]:4"),
            "{nested}"
        );
        assert!(nested.contains("## callers\nNo results"), "{nested}");
    }

    #[test]
    fn test_string_previews_preserve_unicode_and_escape_delimiters() {
        assert_eq!(escape_string("日本語 café", 60), "\"日本語 café\"");
        assert_eq!(escape_string("a\"b\\c\n\t", 60), "\"a\\\"b\\\\c\\n\\t\"");
        assert_eq!(
            escape_string(&"x".repeat(60), 60),
            format!("\"{}\"", "x".repeat(60))
        );
        assert_eq!(
            escape_string(&"x".repeat(61), 60),
            format!("\"{}…\"", "x".repeat(60))
        );
        assert_eq!(escape_string("日本語", 2), "\"日本…\"");
    }

    #[test]
    fn test_memory_formatting_never_invents_bytes_or_address_zero() {
        for (address, hex) in [
            ("invalid", "0102"),
            ("0x0010", "1"),
            ("0x0010", "é1"),
            ("0x0010", "zz"),
            ("0xffffffffffffffff", "0102"),
        ] {
            let row = json!({"address":address, "hex":hex, "size":2});
            let out = DefaultFormatter
                .format(&[row], OutputFormat::Compact)
                .unwrap();
            assert!(out.contains(address) && out.contains(hex), "{out}");
            assert!(!out.contains("0x00000000"), "{out}");
        }
        let out = DefaultFormatter
            .format(
                &[json!({"address":"0X00000010", "hex":"4142", "size":2})],
                OutputFormat::Compact,
            )
            .unwrap();
        assert!(
            out.starts_with("0x00000010") && out.contains("|AB|"),
            "{out}"
        );
    }

    #[test]
    fn test_delimited_formats_round_trip_optional_fields_and_embedded_delimiters() {
        let data = [
            json!({"name":"first", "text":"comma, quote\" newline\n tab\t", "values":["a,b","c"]}),
            json!({"name":"second", "late":"present only later", "text":"next"}),
        ];
        for (format, delimiter) in [(OutputFormat::Csv, b','), (OutputFormat::Tsv, b'\t')] {
            let out = DefaultFormatter.format(&data, format).unwrap();
            let mut reader = csv::ReaderBuilder::new()
                .delimiter(delimiter)
                .from_reader(out.as_bytes());
            let columns = reader.headers().unwrap().clone();
            let rows: Vec<_> = reader.records().map(|row| row.unwrap()).collect();
            let position = |key| columns.iter().position(|column| column == key).unwrap();
            assert_eq!(
                &rows[0][position("text")],
                data[0]["text"].as_str().unwrap()
            );
            assert_eq!(&rows[1][position("late")], "present only later");
            assert_eq!(&rows[0][position("late")], "");
            assert_eq!(
                serde_json::from_str::<JsonValue>(&rows[0][position("values")]).unwrap(),
                data[0]["values"]
            );
        }
        let table = DefaultFormatter.format(&data, OutputFormat::Table).unwrap();
        assert!(
            table.contains("late") && table.contains("present only later"),
            "{table}"
        );
    }

    #[test]
    fn test_table_and_csv_preserve_scalar_rows() {
        let data = [json!("alpha"), json!(42)];
        for format in [OutputFormat::Table, OutputFormat::Csv] {
            let out = DefaultFormatter.format(&data, format).unwrap();
            assert!(out.contains("alpha") && out.contains("42"), "{out}");
        }
    }

    #[test]
    fn test_program_row_preserves_path_without_fabricated_counts() {
        let data = [
            json!({"name":"sample", "path":"/nested/sample", "current":false, "type":"Program", "version":1}),
        ];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(out.contains("/nested/sample"), "{out}");
        assert!(!out.contains("0 functions"), "{out}");
    }

    #[test]
    fn test_source_formats_render_their_content_and_reject_wrong_shapes() {
        let code = "int f(void)\n{\n  return 1;\n}\n";
        let decompile =
            json!({"name":"f", "code":code, "params":[{"name":"x", "storage":"r6", "type":"int"}]});
        assert_eq!(
            DefaultFormatter
                .format(&[decompile], OutputFormat::C)
                .unwrap(),
            code
        );
        let asm = DefaultFormatter
            .format(
                &[json!({"address":"0010", "bytes":"00", "mnemonic":"nop", "operands":[]})],
                OutputFormat::Asm,
            )
            .unwrap();
        assert!(asm.contains("0x0010") && asm.contains("nop"), "{asm}");
        let hex = DefaultFormatter
            .format(
                &[json!({"address":"0010", "hex":"4142", "size":2})],
                OutputFormat::Hex,
            )
            .unwrap();
        assert!(hex.contains("41 42") && hex.contains("|AB|"), "{hex}");
        for format in [OutputFormat::C, OutputFormat::Asm, OutputFormat::Hex] {
            assert!(DefaultFormatter
                .format(&[json!({"status":"saved"})], format)
                .is_err());
        }
        assert!(OutputFormat::from_str("tree").is_err());
    }

    #[test]
    fn test_compact_dot_export_is_redirectable_source() {
        let dot = "digraph calls {\n  a -> b;\n}\n";
        let data = [json!({"format":"dot", "output":dot})];
        assert_eq!(
            DefaultFormatter
                .format(&data, OutputFormat::Compact)
                .unwrap(),
            dot
        );
    }

    #[test]
    fn test_compact_comment_get_keeps_type_and_multiline_text() {
        let data = [
            json!({"address":"0010", "comments":[{"type":"PRE", "text":"first line\nsecond line"}]}),
        ];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(
            out.contains("PRE") && out.contains("first line") && out.contains("second line"),
            "{out}"
        );
        assert!(!out.contains("text="), "{out}");
    }

    #[test]
    fn test_compact_rows_surface_nondefault_symbol_and_memory_state() {
        let symbol = json!({"address":"0010", "name":"alias", "type":"Label", "source":"USER_DEFINED", "is_primary":false});
        let out = DefaultFormatter
            .format(&[symbol], OutputFormat::Compact)
            .unwrap();
        assert!(out.contains("(secondary)"), "{out}");
        let block = json!({"name":"bss", "start":"0010", "end":"001f", "size":16, "permissions":"rw-", "is_initialized":false, "is_loaded":false});
        let out = DefaultFormatter
            .format(&[block], OutputFormat::Compact)
            .unwrap();
        assert!(
            out.contains("uninitialized") && out.contains("unloaded"),
            "{out}"
        );
    }

    #[test]
    fn test_json_modes_preserve_all_metadata_and_text() {
        let data = [
            json!({"status":"saved", "code":"metadata", "null":null, "empty":[], "text":"日本語\n", "truncated":false}),
        ];
        for format in [
            OutputFormat::Json,
            OutputFormat::JsonCompact,
            OutputFormat::JsonStream,
        ] {
            let out = DefaultFormatter.format(&data, format).unwrap();
            let value: JsonValue = serde_json::from_str(&out).unwrap();
            let expected = if format == OutputFormat::JsonStream {
                data[0].clone()
            } else {
                json!(data)
            };
            assert_eq!(value, expected);
        }
    }

    #[test]
    fn test_compact_graph_report_hides_truncation_bookkeeping() {
        let data = vec![json!({
            "node_count": 2,
            "edge_count": 1,
            "truncated": true,
            "nodes": [
                {"id": "00000100", "address": "00000100", "name": "a"},
                {"id": "00000200", "address": "00000200", "name": "b"}
            ],
            "edges": [{"from": "00000100", "to": "00000200", "type": "call"}]
        })];
        let out = DefaultFormatter
            .format(&data, OutputFormat::Compact)
            .unwrap();
        assert!(!out.contains("truncated"), "{out}");
        assert!(out.contains("0x00000100 → 0x00000200  call"), "{out}");
        assert!(out.contains("0x00000100  a"), "{out}");
    }
}
