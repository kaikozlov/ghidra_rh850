//! Test schema definitions and validation.
//!
//! Defines data structures matching the CLI's JSON output format.
//! These are used for type-safe parsing and validation in tests.

#![allow(dead_code)]

use serde::Deserialize;

/// Function information from `ghidra function list`.
#[derive(Debug, Clone, Deserialize)]
pub struct Function {
    pub name: String,
    pub address: String,
    pub size: u64,
    #[serde(default)]
    pub signature: Option<String>,
    pub entry_point: String,
    #[serde(default)]
    pub calling_convention: Option<String>,
    #[serde(default)]
    pub parameters: Vec<Parameter>,
    #[serde(default)]
    pub local_variables: Vec<LocalVariable>,
    #[serde(default)]
    pub calls: Vec<String>,
    #[serde(default)]
    pub called_by: Vec<String>,
    #[serde(default)]
    pub decompiled: Option<String>,
    #[serde(default)]
    pub comment: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Parameter {
    pub name: String,
    pub data_type: String,
    pub ordinal: u32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct LocalVariable {
    pub name: String,
    pub data_type: String,
    #[serde(default)]
    pub stack_offset: Option<i32>,
}

/// String data from `ghidra strings list`.
#[derive(Debug, Clone, Deserialize)]
pub struct StringData {
    pub address: String,
    pub value: String,
    pub length: usize,
    #[serde(default)]
    pub encoding: Option<String>,
    #[serde(default)]
    pub references: Vec<String>,
}

/// Symbol from `ghidra symbol list`.
#[derive(Debug, Clone, Deserialize)]
pub struct Symbol {
    pub name: String,
    pub address: String,
    pub symbol_type: String,
    #[serde(default)]
    pub namespace: Option<String>,
    #[serde(default)]
    pub source: Option<String>,
}

/// Memory block from `ghidra memory map`.
#[derive(Debug, Clone, Deserialize)]
pub struct MemoryBlock {
    pub name: String,
    pub start: String,
    pub end: String,
    pub size: u64,
    pub permissions: String,
    #[serde(default)]
    pub is_initialized: bool,
    #[serde(default)]
    pub is_loaded: bool,
}

/// Instruction from disassembly output.
#[derive(Debug, Clone, Deserialize)]
pub struct Instruction {
    pub address: String,
    pub mnemonic: String,
    #[serde(default)]
    pub operands: Option<String>,
    #[serde(default)]
    pub bytes: Option<String>,
    #[serde(default)]
    pub length: Option<u32>,
    #[serde(default)]
    pub flow_type: Option<String>,
}

/// Comment from `ghidra comment` commands.
#[derive(Debug, Clone, Deserialize)]
pub struct Comment {
    pub address: String,
    pub comment_type: String,
    pub text: String,
}

/// Data type from `ghidra type` commands.
#[derive(Debug, Clone, Deserialize)]
pub struct DataType {
    pub name: String,
    #[serde(default)]
    pub category: Option<String>,
    #[serde(default)]
    pub size: Option<u64>,
    #[serde(default)]
    pub description: Option<String>,
}

/// Cross-reference from `ghidra xref` commands.
#[derive(Debug, Clone, Deserialize)]
pub struct XRef {
    pub from: String,
    pub to: String,
    pub ref_type: String,
    #[serde(default)]
    pub from_function: Option<String>,
    #[serde(default)]
    pub to_function: Option<String>,
    #[serde(default)]
    pub direction: Option<String>,
}

/// Wrapper for lists of items with optional metadata.
#[derive(Debug, Deserialize)]
pub struct ResultWrapper<T> {
    pub results: Vec<T>,
    #[serde(default)]
    pub count: Option<usize>,
    #[serde(default)]
    pub truncated: Option<bool>,
}

/// Disassembly result from `ghidra disasm` command.
#[derive(Debug, Deserialize)]
pub struct DisasmResult {
    pub results: Vec<Instruction>,
    #[serde(default)]
    pub start_address: Option<String>,
    #[serde(default)]
    pub end_address: Option<String>,
}

/// Patch operation result.
#[derive(Debug, Deserialize)]
pub struct PatchResult {
    pub status: String,
    #[serde(default)]
    pub address: Option<String>,
    #[serde(default)]
    pub bytes_written: Option<usize>,
    #[serde(default)]
    pub original_bytes: Option<String>,
}

/// Export result from `ghidra patch export`.
#[derive(Debug, Deserialize)]
pub struct ExportResult {
    pub status: String,
    #[serde(default)]
    pub path: Option<String>,
    #[serde(default)]
    pub size: Option<u64>,
}

/// Stats result from `ghidra stats`.
#[derive(Debug, Deserialize)]
pub struct StatsResult {
    #[serde(default)]
    pub functions: Option<usize>,
    #[serde(default)]
    pub instructions: Option<usize>,
    #[serde(default)]
    pub strings: Option<usize>,
    #[serde(default)]
    pub symbols: Option<usize>,
    #[serde(default)]
    pub imports: Option<usize>,
    #[serde(default)]
    pub exports: Option<usize>,
    #[serde(default)]
    pub memory_blocks: Option<usize>,
}

/// Graph result for call graph operations.
#[derive(Debug, Deserialize)]
pub struct GraphResult {
    pub nodes: Vec<GraphNode>,
    pub edges: Vec<GraphEdge>,
}

#[derive(Debug, Deserialize)]
pub struct GraphNode {
    pub id: String,
    #[serde(default)]
    pub label: Option<String>,
    #[serde(default)]
    pub address: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct GraphEdge {
    pub from: String,
    pub to: String,
    #[serde(default)]
    pub edge_type: Option<String>,
}

// ============================================================================
// Validation trait and implementations
// ============================================================================

/// Validation trait for schema types.
pub trait Validate {
    /// Perform validation and return any errors.
    fn validate(&self) -> Vec<String>;

    /// Check if valid (no errors).
    fn is_valid(&self) -> bool {
        self.validate().is_empty()
    }

    /// Assert validity, panicking with all errors if invalid.
    fn assert_valid(&self) {
        let errors = self.validate();
        if !errors.is_empty() {
            panic!("Validation failed:\n  - {}", errors.join("\n  - "));
        }
    }
}

/// Check if a string is a valid memory address.
/// Accepts both plain hex ("001174b0") and overlay format (".comment::00000000").
fn is_memory_address(s: &str) -> bool {
    if is_hex_address(s) {
        return true;
    }
    // Ghidra overlay sections use "section_name::hex_addr" format
    if let Some((_section, addr)) = s.rsplit_once("::") {
        return is_hex_address(addr);
    }
    false
}

fn is_hex_address(s: &str) -> bool {
    let s = s.trim();
    if s.is_empty() {
        return false;
    }
    // Accept both "0x001174b0" and "001174b0" formats
    // Ghidra returns addresses without 0x prefix
    let hex_part = s
        .strip_prefix("0x")
        .or_else(|| s.strip_prefix("0X"))
        .unwrap_or(s);
    !hex_part.is_empty() && hex_part.bytes().all(|b| b.is_ascii_hexdigit())
}

impl Validate for Function {
    fn validate(&self) -> Vec<String> {
        let mut errors = Vec::new();

        if self.name.is_empty() {
            errors.push("Function name is empty".to_string());
        }

        if !is_hex_address(&self.address) {
            errors.push(format!(
                "Function address '{}' should be hex format (0x...)",
                self.address
            ));
        }

        if !is_hex_address(&self.entry_point) {
            errors.push(format!(
                "Function entry_point '{}' should be hex format",
                self.entry_point
            ));
        }

        errors
    }
}

impl Validate for Instruction {
    fn validate(&self) -> Vec<String> {
        let mut errors = Vec::new();

        if !is_hex_address(&self.address) {
            errors.push(format!(
                "Instruction address '{}' should be hex format",
                self.address
            ));
        }

        if self.mnemonic.is_empty() {
            errors.push("Instruction mnemonic is empty".to_string());
        }

        // Bytes should be hex string if present
        if let Some(ref bytes) = self.bytes {
            if !bytes.chars().all(|c| c.is_ascii_hexdigit()) {
                errors.push(format!(
                    "Instruction bytes '{}' should be hex characters only",
                    bytes
                ));
            }
        }

        errors
    }
}

impl Validate for StringData {
    fn validate(&self) -> Vec<String> {
        let mut errors = Vec::new();

        if !is_hex_address(&self.address) {
            errors.push(format!(
                "String address '{}' should be hex format",
                self.address
            ));
        }

        if self.length == 0 && !self.value.is_empty() {
            errors.push("String length is 0 but value is not empty".to_string());
        }

        errors
    }
}

impl Validate for Symbol {
    fn validate(&self) -> Vec<String> {
        let mut errors = Vec::new();

        if self.name.is_empty() {
            errors.push("Symbol name is empty".to_string());
        }

        if !is_hex_address(&self.address) {
            errors.push(format!(
                "Symbol address '{}' should be hex format",
                self.address
            ));
        }

        if self.symbol_type.is_empty() {
            errors.push("Symbol type is empty".to_string());
        }

        errors
    }
}

impl Validate for MemoryBlock {
    fn validate(&self) -> Vec<String> {
        let mut errors = Vec::new();

        if self.name.is_empty() {
            errors.push("MemoryBlock name is empty".to_string());
        }

        // Ghidra may return addresses as "section::hex" for overlay blocks
        if !is_memory_address(&self.start) {
            errors.push(format!(
                "MemoryBlock start '{}' should be hex or overlay format",
                self.start
            ));
        }

        if !is_memory_address(&self.end) {
            errors.push(format!(
                "MemoryBlock end '{}' should be hex or overlay format",
                self.end
            ));
        }

        // Permissions may be empty for non-loaded/overlay sections
        if self.permissions.is_empty() && self.is_loaded {
            errors.push("Loaded MemoryBlock permissions is empty".to_string());
        }

        errors
    }
}

impl Validate for Comment {
    fn validate(&self) -> Vec<String> {
        let mut errors = Vec::new();

        if !is_hex_address(&self.address) {
            errors.push(format!(
                "Comment address '{}' should be hex format",
                self.address
            ));
        }

        if self.comment_type.is_empty() {
            errors.push("Comment type is empty".to_string());
        }

        errors
    }
}

impl<T: Validate> Validate for Vec<T> {
    fn validate(&self) -> Vec<String> {
        self.iter()
            .enumerate()
            .flat_map(|(i, item)| {
                item.validate()
                    .into_iter()
                    .map(move |e| format!("[{}] {}", i, e))
            })
            .collect()
    }
}

impl Validate for DisasmResult {
    fn validate(&self) -> Vec<String> {
        let mut errors = self.results.validate();

        if let Some(ref addr) = self.start_address {
            if !is_hex_address(addr) {
                errors.push(format!("start_address '{}' should be hex format", addr));
            }
        }

        errors
    }
}
