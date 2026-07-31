use thiserror::Error;

#[derive(Error, Debug)]
pub enum GhidraError {
    #[error("Ghidra installation not found. Set GHIDRA_INSTALL_DIR or run 'ghidra init'")]
    GhidraNotFound,

    #[error("Failed to parse filter: {0}")]
    FilterParseError(String),

    #[error("Invalid filter expression: {0}")]
    InvalidFilter(String),

    #[error("Invalid format: {0}")]
    InvalidFormat(String),

    #[allow(dead_code)]
    #[error("Invalid data type: {0}")]
    InvalidDataType(String),

    #[error("Configuration error: {0}")]
    ConfigError(String),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("JSON error: {0}")]
    JsonError(#[from] serde_json::Error),

    #[error("YAML error: {0}")]
    YamlError(#[from] serde_yaml::Error),
}

pub type Result<T> = std::result::Result<T, GhidraError>;
