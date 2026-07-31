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

    // ---- CommandError::from_response() ----

    #[test]
    fn test_command_error_from_structured_response() {
        // New format: error object should populate code/message/diagnostics.
        let json = r#"{
            "status":"error",
            "error":{
                "code":"script_compile_failed",
                "message":"Script failed to compile",
                "diagnostics":"Foo.java:3: error: ';' expected"
            }
        }"#;
        let response: BridgeResponse = serde_json::from_str(json).unwrap();
        let err = CommandError::from_response(&response);
        assert_eq!(err.code.as_deref(), Some("script_compile_failed"));
        assert_eq!(err.message, "Script failed to compile");
        assert_eq!(
            err.diagnostics.as_deref(),
            Some("Foo.java:3: error: ';' expected")
        );
    }

    #[test]
    fn test_command_error_from_legacy_response() {
        // Old format: flat message only — code and diagnostics must be None.
        let json = r#"{"status":"error","message":"Something went wrong"}"#;
        let response: BridgeResponse = serde_json::from_str(json).unwrap();
        let err = CommandError::from_response(&response);
        assert!(err.code.is_none());
        assert_eq!(err.message, "Something went wrong");
        assert!(err.diagnostics.is_none());
    }

    #[test]
    fn test_command_error_falls_back_to_top_level_message() {
        // Edge case: error object present but message missing inside it —
        // should fall back to the top-level message field.
        let json = r#"{
            "status":"error",
            "message":"top level fallback",
            "error":{"code":"no_inner_message"}
        }"#;
        let response: BridgeResponse = serde_json::from_str(json).unwrap();
        let err = CommandError::from_response(&response);
        assert_eq!(err.code.as_deref(), Some("no_inner_message"));
        assert_eq!(err.message, "top level fallback");
    }

    #[test]
    fn test_command_error_no_message_anywhere() {
        // Neither error.message nor top-level message present.
        let json = r#"{"status":"error","error":{"code":"bare"}}"#;
        let response: BridgeResponse = serde_json::from_str(json).unwrap();
        let err = CommandError::from_response(&response);
        assert_eq!(err.code.as_deref(), Some("bare"));
        assert_eq!(err.message, "Unknown error");
    }

    // ---- CommandError::to_json() ----

    #[test]
    fn test_command_error_to_json_full() {
        let err = CommandError {
            code: Some("script_compile_failed".to_string()),
            message: "Script failed to compile".to_string(),
            diagnostics: Some("Foo.java:3: error".to_string()),
        };
        let json = err.to_json();
        assert_eq!(json["status"], "error");
        assert_eq!(json["error"]["code"], "script_compile_failed");
        assert_eq!(json["error"]["message"], "Script failed to compile");
        assert_eq!(json["error"]["diagnostics"], "Foo.java:3: error");
    }

    #[test]
    fn test_command_error_to_json_no_code_no_diagnostics() {
        // Legacy-format error: only message present.
        let err = CommandError {
            code: None,
            message: "Something went wrong".to_string(),
            diagnostics: None,
        };
        let json = err.to_json();
        assert_eq!(json["status"], "error");
        assert_eq!(json["error"]["message"], "Something went wrong");
        // code and diagnostics should be absent from the object.
        assert!(json["error"].get("code").is_none());
        assert!(json["error"].get("diagnostics").is_none());
    }

    #[test]
    fn test_command_error_to_json_roundtrip_shape() {
        // The to_json() output must have exactly {"status":"error","error":{...}}.
        let err = CommandError {
            code: Some("e1".to_string()),
            message: "m".to_string(),
            diagnostics: None,
        };
        let json = err.to_json();
        let obj = json.as_object().expect("to_json returns an object");
        assert_eq!(obj.len(), 2, "exactly status + error keys");
        assert!(obj.contains_key("status"));
        assert!(obj.contains_key("error"));
        let error_obj = json["error"].as_object().unwrap();
        assert_eq!(error_obj.len(), 2, "code + message, no diagnostics");
    }

    // ---- CommandError Display ----

    #[test]
    fn test_command_error_display_with_code() {
        let err = CommandError {
            code: Some("e1".to_string()),
            message: "boom".to_string(),
            diagnostics: None,
        };
        assert_eq!(format!("{}", err), "[e1] boom");
    }

    #[test]
    fn test_command_error_display_without_code() {
        let err = CommandError {
            code: None,
            message: "boom".to_string(),
            diagnostics: None,
        };
        assert_eq!(format!("{}", err), "boom");
    }

    #[test]
    fn test_command_error_display_with_diagnostics() {
        let err = CommandError {
            code: Some("e1".to_string()),
            message: "boom".to_string(),
            diagnostics: Some("line 5: broken".to_string()),
        };
        let rendered = format!("{}", err);
        assert!(rendered.contains("[e1] boom"));
        assert!(rendered.contains("line 5: broken"));
    }
}
