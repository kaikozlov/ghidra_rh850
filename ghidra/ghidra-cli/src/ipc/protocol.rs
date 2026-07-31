//! IPC protocol types for bridge communication.
//!
//! Defines the request/response format for CLI ↔ Java bridge communication.
//! Uses simple JSON: {"command":"...", "args":{...}} → {"status":"...", "data":{...}}

use serde::{Deserialize, Serialize};
use std::fmt;

/// Request to the Java bridge.
#[derive(Debug, Serialize)]
pub struct BridgeRequest {
    pub command: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub args: Option<serde_json::Value>,
}

/// Response from the Java bridge.
#[derive(Debug, Deserialize)]
pub struct BridgeResponse<T = serde_json::Value> {
    pub status: String,
    pub data: Option<T>,
    #[serde(default)]
    pub message: Option<String>,
    /// Structured error payload (new format). Old bridges only populate
    /// `message`; newer ones add this object with machine-readable details.
    #[serde(default)]
    pub error: Option<BridgeError>,
}

/// Structured error returned by the bridge in the new error format.
///
/// Serialized as `{"code":"...", "message":"...", "diagnostics":"..."}` inside
/// [`BridgeResponse::error`]. All fields are optional so partial payloads
/// remain deserializable.
#[derive(Debug, Deserialize)]
pub struct BridgeError {
    /// Machine-readable error code, e.g. `script_compile_failed`.
    #[serde(default)]
    pub code: Option<String>,
    /// Human-readable error summary.
    #[serde(default)]
    pub message: Option<String>,
    /// Optional diagnostics payload (e.g. compiler output).
    #[serde(default)]
    pub diagnostics: Option<String>,
}

/// A structured error returned by the bridge, normalized from either the new
/// `{error:{code,message,diagnostics}}` format or the legacy `{message:"..."}`
/// format.
///
/// This type implements [`std::error::Error`] so it flows through `anyhow::Error`
/// (via `?`), but callers can downcast to recover the structured fields —
/// essential for rendering machine-readable JSON errors in `--json` mode.
#[derive(Debug, Clone)]
pub struct CommandError {
    /// Machine-readable error code, when the bridge provided one.
    pub code: Option<String>,
    /// Human-readable error summary.
    pub message: String,
    /// Optional diagnostics (e.g. javac compiler output).
    pub diagnostics: Option<String>,
}

impl CommandError {
    /// Build a `CommandError` from a parsed bridge response, preferring the
    /// structured `error` object and falling back to the top-level `message`.
    pub fn from_response(response: &BridgeResponse) -> Self {
        if let Some(err) = &response.error {
            // New structured format: prefer error.message, but fall back to
            // the top-level message if the nested one is absent.
            let message = err
                .message
                .clone()
                .or_else(|| response.message.clone())
                .unwrap_or_else(|| "Unknown error".to_string());
            Self {
                code: err.code.clone(),
                message,
                diagnostics: err.diagnostics.clone(),
            }
        } else {
            // Legacy format: flat message only.
            Self {
                code: None,
                message: response
                    .message
                    .clone()
                    .unwrap_or_else(|| "Unknown error".to_string()),
                diagnostics: None,
            }
        }
    }

    /// Serialize this error as the structured JSON object that should be
    /// printed to stderr in `--json` mode:
    /// `{"status":"error","error":{...}}`.
    pub fn to_json(&self) -> serde_json::Value {
        let mut error_obj = serde_json::Map::new();
        if let Some(code) = &self.code {
            error_obj.insert("code".to_string(), serde_json::Value::String(code.clone()));
        }
        error_obj.insert(
            "message".to_string(),
            serde_json::Value::String(self.message.clone()),
        );
        if let Some(diagnostics) = &self.diagnostics {
            error_obj.insert(
                "diagnostics".to_string(),
                serde_json::Value::String(diagnostics.clone()),
            );
        }
        serde_json::json!({
            "status": "error",
            "error": serde_json::Value::Object(error_obj),
        })
    }
}

impl fmt::Display for CommandError {
    /// Render a human-readable string containing all available info. When a
    /// code or diagnostics are present they are included so the message is
    /// useful even without JSON formatting.
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match &self.code {
            Some(code) => write!(f, "[{}] {}", code, self.message)?,
            None => write!(f, "{}", self.message)?,
        }
        if let Some(diagnostics) = &self.diagnostics {
            if !diagnostics.is_empty() {
                write!(f, "\n{}", diagnostics)?;
            }
        }
        Ok(())
    }
}

impl std::error::Error for CommandError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_request_serialization() {
        let request = BridgeRequest {
            command: "ping".to_string(),
            args: None,
        };
        let json = serde_json::to_string(&request).unwrap();
        assert!(json.contains("ping"));
        assert!(!json.contains("args"));
    }

    #[test]
    fn test_request_with_args() {
        let request = BridgeRequest {
            command: "list_functions".to_string(),
            args: Some(serde_json::json!({"limit": 100})),
        };
        let json = serde_json::to_string(&request).unwrap();
        assert!(json.contains("list_functions"));
        assert!(json.contains("100"));
    }

    #[test]
    fn test_response_deserialization() {
        let json = r#"{"status":"success","data":{"count":42}}"#;
        let response: BridgeResponse = serde_json::from_str(json).unwrap();
        assert_eq!(response.status, "success");
        assert!(response.data.is_some());
    }

    #[test]
    fn test_error_response() {
        // Old format: flat message at top level.
        let json = r#"{"status":"error","message":"Something went wrong"}"#;
        let response: BridgeResponse = serde_json::from_str(json).unwrap();
        assert_eq!(response.status, "error");
        assert_eq!(response.message.as_ref().unwrap(), "Something went wrong");
        assert!(response.error.is_none());
    }

    #[test]
    fn test_structured_error_response() {
        // New format: nested error object with code, message, diagnostics.
        let json = r#"{
            "status":"error",
            "error":{
                "code":"script_compile_failed",
                "message":"Script failed to compile",
                "diagnostics":"Foo.java:3: error: ';' expected"
            }
        }"#;
        let response: BridgeResponse = serde_json::from_str(json).unwrap();
        assert_eq!(response.status, "error");
        let err = response.error.expect("error object present");
        assert_eq!(err.code.as_deref(), Some("script_compile_failed"));
        assert_eq!(err.message.as_deref(), Some("Script failed to compile"));
        assert!(err.diagnostics.as_deref().unwrap().contains("Foo.java"));
        // message at top level is optional even in the new format.
        assert!(response.message.is_none());
    }

    #[test]
    fn test_structured_error_partial_fields() {
        // New format with only code (message/diagnostics absent).
        let json = r#"{"status":"error","error":{"code":"not_found"}}"#;
        let response: BridgeResponse = serde_json::from_str(json).unwrap();
        let err = response.error.expect("error object present");
        assert_eq!(err.code.as_deref(), Some("not_found"));
        assert!(err.message.is_none());
        assert!(err.diagnostics.is_none());
    }
}
