use super::{CompareOp, ExistenceCheck, Filter, FilterExpr, LogicalOp, StringOp, Value};
use crate::error::{GhidraError, Result};
use pest::Parser;
use pest_derive::Parser;

#[derive(Parser)]
#[grammar = "filter.pest"]
struct FilterParser;

pub fn parse_filter(input: &str) -> Result<Filter> {
    let pairs = FilterParser::parse(Rule::expr, input)
        .map_err(|e| GhidraError::FilterParseError(format!("{}", e)))?;

    let mut expr = None;
    for pair in pairs {
        if pair.as_rule() == Rule::expr {
            for inner in pair.into_inner() {
                if inner.as_rule() == Rule::logical_expr {
                    expr = Some(parse_logical_expr(inner)?);
                }
            }
        }
    }

    expr.map(|e| Filter { expr: e })
        .ok_or_else(|| GhidraError::FilterParseError("Empty expression".to_string()))
}

fn parse_logical_expr(pair: pest::iterators::Pair<Rule>) -> Result<FilterExpr> {
    let mut terms = Vec::new();
    let mut ops = Vec::new();

    for inner in pair.into_inner() {
        match inner.as_rule() {
            Rule::logical_term => {
                terms.push(parse_logical_term(inner)?);
            }
            Rule::logical_op => {
                let op_str = inner.as_str();
                let op = match op_str {
                    "AND" | "&&" => LogicalOp::And,
                    "OR" | "||" => LogicalOp::Or,
                    _ => {
                        return Err(GhidraError::FilterParseError(format!(
                            "Unknown operator: {}",
                            op_str
                        )))
                    }
                };
                ops.push(op);
            }
            _ => {}
        }
    }

    if terms.is_empty() {
        return Err(GhidraError::FilterParseError(
            "No terms in logical expression".to_string(),
        ));
    }

    if terms.len() == 1 {
        return Ok(terms.into_iter().next().unwrap());
    }

    // Build expression tree respecting precedence (AND before OR)
    // For simplicity, we'll evaluate left-to-right for now
    // TODO: Proper precedence handling
    let mut result = terms[0].clone();
    for (i, op) in ops.iter().enumerate() {
        result = FilterExpr::Logical {
            op: *op,
            exprs: vec![result, terms[i + 1].clone()],
        };
    }

    Ok(result)
}

fn parse_logical_term(pair: pest::iterators::Pair<Rule>) -> Result<FilterExpr> {
    for inner in pair.into_inner() {
        match inner.as_rule() {
            Rule::logical_not => {
                return parse_logical_not(inner);
            }
            Rule::logical_expr => {
                return parse_logical_expr(inner);
            }
            Rule::comparison => {
                return parse_comparison(inner);
            }
            _ => {}
        }
    }
    Err(GhidraError::FilterParseError(
        "Invalid logical term".to_string(),
    ))
}

fn parse_logical_not(pair: pest::iterators::Pair<Rule>) -> Result<FilterExpr> {
    for inner in pair.into_inner() {
        if inner.as_rule() == Rule::logical_term {
            let term = parse_logical_term(inner)?;
            return Ok(FilterExpr::Not(Box::new(term)));
        }
    }
    Err(GhidraError::FilterParseError(
        "Invalid NOT expression".to_string(),
    ))
}

fn parse_comparison(pair: pest::iterators::Pair<Rule>) -> Result<FilterExpr> {
    let mut field = None;
    let mut op = None;
    let mut value = None;
    let mut string_op = None;
    let mut existence = None;
    let mut negate_existence = false;
    let mut in_values = None;

    for inner in pair.into_inner() {
        match inner.as_rule() {
            Rule::field => {
                field = Some(inner.as_str().to_string());
            }
            Rule::compare_op => {
                let op_str = inner.as_str();
                op = Some(match op_str {
                    "=" => CompareOp::Equal,
                    "!=" => CompareOp::NotEqual,
                    ">" => CompareOp::Greater,
                    ">=" => CompareOp::GreaterEqual,
                    "<" => CompareOp::Less,
                    "<=" => CompareOp::LessEqual,
                    _ => {
                        return Err(GhidraError::FilterParseError(format!(
                            "Unknown compare op: {}",
                            op_str
                        )))
                    }
                });
            }
            Rule::string_op => {
                let op_str = inner.as_str();
                string_op = Some(match op_str {
                    "~" => StringOp::Contains,
                    "^" => StringOp::StartsWith,
                    "$" => StringOp::EndsWith,
                    "=~" => StringOp::Regex,
                    _ => {
                        return Err(GhidraError::FilterParseError(format!(
                            "Unknown string op: {}",
                            op_str
                        )))
                    }
                });
            }
            Rule::value => {
                value = Some(parse_value(inner)?);
            }
            Rule::string_value => {
                value = Some(parse_value(inner)?);
            }
            Rule::existence_check => {
                for part in inner.into_inner() {
                    match part.as_rule() {
                        Rule::existence_not => negate_existence = true,
                        Rule::existence_op => {
                            existence = Some(match part.as_str() {
                                "EXISTS" => ExistenceCheck::Exists,
                                "EMPTY" => ExistenceCheck::Empty,
                                "NULL" => ExistenceCheck::Null,
                                unknown => {
                                    return Err(GhidraError::FilterParseError(format!(
                                        "Unknown existence check: {unknown}"
                                    )))
                                }
                            });
                        }
                        _ => {}
                    }
                }
            }
            Rule::value_list => {
                let mut values = Vec::new();
                for val_pair in inner.into_inner() {
                    if val_pair.as_rule() == Rule::value {
                        values.push(parse_value(val_pair)?);
                    }
                }
                in_values = Some(values);
            }
            _ => {}
        }
    }

    let field = field.ok_or_else(|| GhidraError::FilterParseError("Missing field".to_string()))?;

    if let Some(check) = existence {
        let expr = FilterExpr::Exists { field, check };
        return Ok(if negate_existence {
            FilterExpr::Not(Box::new(expr))
        } else {
            expr
        });
    }

    if let Some(values) = in_values {
        return Ok(FilterExpr::In { field, values });
    }

    if let Some(str_op) = string_op {
        let val =
            value.ok_or_else(|| GhidraError::FilterParseError("Missing value".to_string()))?;
        let val_str = match val {
            Value::String(s) => s,
            _ => {
                return Err(GhidraError::FilterParseError(
                    "String operation requires string value".to_string(),
                ))
            }
        };
        return Ok(FilterExpr::StringOp {
            field,
            op: str_op,
            value: val_str,
        });
    }

    if let Some(cmp_op) = op {
        let val =
            value.ok_or_else(|| GhidraError::FilterParseError("Missing value".to_string()))?;
        return Ok(FilterExpr::Compare {
            field,
            op: cmp_op,
            value: val,
        });
    }

    Err(GhidraError::FilterParseError(
        "Invalid comparison".to_string(),
    ))
}

fn parse_value(pair: pest::iterators::Pair<Rule>) -> Result<Value> {
    for inner in pair.into_inner() {
        match inner.as_rule() {
            Rule::number => {
                let num_str = inner.as_str();
                if num_str.contains('.') {
                    let num = num_str.parse::<f64>().map_err(|_| {
                        GhidraError::FilterParseError(format!("Invalid number: {}", num_str))
                    })?;
                    return Ok(Value::Number(num));
                } else {
                    let num = num_str.parse::<i64>().map_err(|_| {
                        GhidraError::FilterParseError(format!("Invalid integer: {}", num_str))
                    })?;
                    return Ok(Value::Integer(num));
                }
            }
            Rule::hex_number => {
                let hex_str = inner.as_str().trim_start_matches("0x");
                let num = u64::from_str_radix(hex_str, 16).map_err(|_| {
                    GhidraError::FilterParseError(format!("Invalid hex number: {}", inner.as_str()))
                })?;
                return Ok(Value::Hex(num));
            }
            Rule::boolean => {
                let bool_str = inner.as_str().to_lowercase();
                return Ok(Value::Boolean(bool_str == "true"));
            }
            Rule::quoted_string => {
                let s = inner.as_str();
                let s = s.trim_matches(|c| c == '"' || c == '\'');
                return Ok(Value::String(s.to_string()));
            }
            Rule::identifier => {
                return Ok(Value::String(inner.as_str().to_string()));
            }
            _ => {}
        }
    }
    Err(GhidraError::FilterParseError("Invalid value".to_string()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple() {
        let filter = parse_filter("name=test").unwrap();
        assert!(matches!(filter.expr, FilterExpr::Compare { .. }));
    }

    #[test]
    fn test_parse_and() {
        let filter = parse_filter("name=test AND size>100").unwrap();
        assert!(matches!(filter.expr, FilterExpr::Logical { .. }));
    }

    #[test]
    fn test_existence_checks() {
        let data = serde_json::json!({
            "name": "alpha", "empty": "", "nil": null, "values": [],
            "number": 0, "function": {"name": "callee"},
        });
        for (input, expected) in [
            ("name EXISTS", true),
            ("missing EXISTS", false),
            ("nil EXISTS", true),
            ("NOT missing EXISTS", true),
            ("missing NOT EXISTS", true),
            ("name NOT \t EXISTS", false),
            ("NOT (name EXISTS)", false),
            ("empty EMPTY", true),
            ("values EMPTY", true),
            ("missing EMPTY", true),
            ("number EMPTY", false),
            ("nil NULL", true),
            ("missing NULL", true),
            ("name NULL", false),
            ("function.name EXISTS", true),
            ("name EXISTS AND nil NULL", true),
        ] {
            let filter = parse_filter(input).unwrap_or_else(|err| panic!("{input}: {err}"));
            assert_eq!(filter.evaluate(&data).unwrap(), expected, "{input}");
        }
    }

    #[test]
    fn test_in_checks() {
        let data = serde_json::json!({"name": "Beta", "size": 32, "enabled": true});
        for (input, expected) in [
            ("size IN [16,0x20,64]", true),
            ("size IN [16,64]", false),
            ("size IN [16,32.0]", true),
            ("name IN [alpha,'beta',\"gamma delta\"]", true),
            ("name IN [alpha,gamma]", false),
            ("enabled IN [false,true]", true),
            ("enabled IN [false]", false),
            ("missing IN [true,1,name]", false),
            ("NOT size IN [16,64]", true),
            ("(size IN [0x20]) AND NOT (name IN [missing])", true),
        ] {
            let filter = parse_filter(input).unwrap_or_else(|err| panic!("{input}: {err}"));
            assert_eq!(filter.evaluate(&data).unwrap(), expected, "{input}");
        }
    }

    #[test]
    fn test_rejects_malformed_existence_and_membership() {
        for input in [
            "name NOT",
            "name NOT EXISTS trailing",
            "name EXISTS AND",
            "name IN []",
            "name IN [a,]",
            "name IN [a",
            "name IN [a] trailing",
        ] {
            assert!(
                parse_filter(input).is_err(),
                "accepted malformed filter: {input}"
            );
        }
    }

    #[test]
    fn test_rejects_trailing_syntax() {
        for input in [
            "name=test junk",
            "name=test AND",
            "name=test OR size>",
            "name=test &&",
            "name=test)",
            "name=test\nsize>100",
            "size>=10garbage",
            "address=0x1234junk",
            "name='test' 'ignored'",
            "(name=test OR size>100) unexpected",
        ] {
            assert!(
                parse_filter(input).is_err(),
                "accepted trailing input: {input}"
            );
        }
    }

    #[test]
    fn test_nested_expression_with_surrounding_whitespace() {
        let filter =
            parse_filter(" \t(name=test OR size>100) AND NOT (size=0 OR name=ignored)\r\n")
                .unwrap();
        assert!(filter
            .evaluate(&serde_json::json!({"name": "test", "size": 1}))
            .unwrap());
        assert!(!filter
            .evaluate(&serde_json::json!({"name": "test", "size": 0}))
            .unwrap());
        assert!(!filter
            .evaluate(&serde_json::json!({"name": "ignored", "size": 101}))
            .unwrap());
    }

    #[test]
    fn test_parse_hex() {
        let filter = parse_filter("address=0x401000").unwrap();
        if let FilterExpr::Compare { value, .. } = filter.expr {
            assert!(matches!(value, Value::Hex(0x401000)));
        } else {
            panic!("Expected Compare expression");
        }
    }
}
