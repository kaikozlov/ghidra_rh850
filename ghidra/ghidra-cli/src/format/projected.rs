use serde_json::Value;
use std::fmt::Write;

/// Rows have already been projected by the query. Render the requested schema,
/// not the entity their remaining keys happen to resemble.
pub(crate) fn rows(data: &[Value], include: Option<&[String]>) -> String {
    if data.is_empty() {
        return "No results".into();
    }
    let inferred;
    let columns = match include {
        Some(columns) => columns,
        None => {
            inferred = super::table_columns(data);
            &inferred
        }
    };
    if columns.is_empty() {
        return format!("No fields ({} rows)", data.len());
    }

    let mut out = String::new();
    if columns.len() > 1 {
        for (i, column) in columns.iter().enumerate() {
            if i != 0 {
                out.push('\t');
            }
            out.push_str(column);
        }
        out.push('\n');
    }
    for row in data {
        for (i, column) in columns.iter().enumerate() {
            if i != 0 {
                out.push('\t');
            }
            match row.get(column) {
                None => out.push('—'),
                Some(Value::String(s)) if s.is_empty() || s.chars().any(char::is_control) => {
                    write!(out, "{s:?}").unwrap();
                }
                Some(Value::String(s)) => out.push_str(s),
                Some(value) => write!(out, "{value}").unwrap(),
            }
        }
        out.push('\n');
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn sparse_columns_keep_their_positions_and_physical_rows() {
        let data = [json!({"a": "two\nlines", "b": null}), json!({"b": 0})];
        let columns = ["b".into(), "a".into()];
        assert_eq!(
            rows(&data, Some(&columns)),
            "b\ta\nnull\t\"two\\nlines\"\n0\t—\n"
        );
        assert_eq!(rows(&data[..1], Some(&columns[1..])), "\"two\\nlines\"\n");
    }
}
