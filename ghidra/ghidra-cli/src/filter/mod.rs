pub mod evaluator;
pub mod parser;

use crate::error::Result;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum FilterExpr {
    Compare {
        field: String,
        op: CompareOp,
        value: Value,
    },
    StringOp {
        field: String,
        op: StringOp,
        value: String,
    },
    Logical {
        op: LogicalOp,
        exprs: Vec<FilterExpr>,
    },
    Not(Box<FilterExpr>),
    Exists {
        field: String,
        check: ExistenceCheck,
    },
    In {
        field: String,
        values: Vec<Value>,
    },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CompareOp {
    Equal,
    NotEqual,
    Greater,
    GreaterEqual,
    Less,
    LessEqual,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum StringOp {
    Contains,   // ~
    StartsWith, // ^
    EndsWith,   // $
    Regex,      // =~
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum LogicalOp {
    And,
    Or,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ExistenceCheck {
    Exists,
    Empty,
    Null,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Value {
    String(String),
    Number(f64),
    Integer(i64),
    Boolean(bool),
    Hex(u64),
}

impl Value {
    pub fn as_f64(&self) -> Option<f64> {
        match self {
            Value::Number(n) => Some(*n),
            Value::Integer(i) => Some(*i as f64),
            Value::Hex(h) => Some(*h as f64),
            _ => None,
        }
    }
}

pub struct Filter {
    pub expr: FilterExpr,
}

impl Filter {
    pub fn parse(input: &str) -> Result<Self> {
        parser::parse_filter(input)
    }

    pub fn evaluate(&self, data: &serde_json::Value) -> Result<bool> {
        evaluator::evaluate(&self.expr, data)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple_filter() {
        let filter = Filter::parse("name=test").unwrap();
        assert!(matches!(filter.expr, FilterExpr::Compare { .. }));
    }

    #[test]
    fn test_parse_logical_filter() {
        let filter = Filter::parse("name=test AND size>100").unwrap();
        assert!(matches!(filter.expr, FilterExpr::Logical { .. }));
    }
}
