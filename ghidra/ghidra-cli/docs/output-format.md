# Output and query options

Analysis commands default to compact text on terminals and through pipes. Use
`--json` for scripts that parse results, or `--pretty` for indented JSON.

```bash
tools/g decompile 0x4e848
tools/g function list --filter 'name~secoc' --sort=-size --fields address,name --limit 20
tools/g function list --json --limit 50 --offset 50
tools/g query functions --count
```

## Formats

Where a command accepts `-o` / `--format`, that option takes precedence over
`--pretty`, then `--json`, then saved `default_output_format`. The configured
value `auto`, or a missing value, selects `compact`. For example,
`tools/g config set default_output_format compact` saves the text preference.

| Option | Result |
|---|---|
| `-o compact` | Address-first rows and sectioned reports |
| `--json`, `-o json-compact` | Compact JSON |
| `--pretty`, `-o json` | Indented JSON |
| `-o ndjson` / `-o json-stream` | One JSON value per line |
| `-o csv`, `-o tsv`, `-o table` | Columns covering all returned fields |
| `-o ids` / `-o minimal` | One address, ID, or name per row |
| `-o full` | Labeled detail blocks |
| `-o c`, `-o asm`, `-o hex` | C from `decompile`, assembly from `disasm`, or a hexdump from `memory read` |
| `--count` | A bare integer; skips the default page limit |
| `-o count` | Number of rows in the selected page |

CSV and TSV quote embedded delimiters, quotes, and newlines. Source formats
require the corresponding command; incompatible combinations fail before execution. `tree` is unsupported; use compact graph
reports or `graph export dot`, which prints redirectable DOT source.

Compact decompilation prints Ghidra's C once. Add `--with-params` or
`--with-vars` for parameter/local storage details. Compound `inspect` reports
show code with its callers, callees, references, and disassembly in separate
sections; their automatically collected parameter/local metadata remains
available in JSON. Requested empty sections say `No results`.

String previews preserve Unicode, escape control characters, and mark clipped
text with an ellipsis. JSON preserves full string values and parameter/local
metadata. Function records use `address`; absent `comment` and `signature`
fields are omitted.

## Limits, filters, and projection

The built-in page size is **50**. Precedence is:

1. Command `--limit N` (`0` means unlimited).
2. `GHIDRA_CLI_DEFAULT_LIMIT`.
3. Saved `default_limit` configuration.
4. The built-in default when the saved value is missing or null.

Existing configured values are preserved. Both wrappers use the CLI's setting.
Set a persistent preference with `tools/g config set default_limit 50`, or use
`GHIDRA_CLI_DEFAULT_LIMIT=20 tools/g function list` for one invocation.

`--filter`, `--sort`, `--offset`, and `--limit` select rows before `--fields`
projects their columns, so a sort key can be omitted from the displayed fields.
Filters require a field and operator, such as `name~secoc`, `size>100`, or
`name=~"^SecOc"`. Use `AND`, `OR`, and `NOT`, with parentheses to group mixed
conditions.
`--count` counts matching rows without the default cap; explicit `--limit` and
`--offset` still apply.

Simple lists and searches return at most the requested page size. The bridge
checks for another match to distinguish an exact-size result from a truncated
one. Client-side filters, sorting, counts, and offsets fetch the complete source
set before selecting the result. Truncation notices go to **stderr**; stdout
contains only the selected output format.

Standalone `disasm -n N` uses the requested instruction count in place of the
default page size. An explicit `--limit` still applies. In `inspect`, `--limit`
caps the nested reference and call lists; `--disasm N` sets the instruction count.
`x-ref trace-to`
retains its complete reference/owner census; `--max-functions` bounds the owner
set and `--limit` caps lists inside each owner's inspection. `graph calls`
applies query options to nodes and retains their outgoing edges.

## Batch and wrapper commands

`batch` always retains its JSON envelope (`commands_parsed`, `results`). Each
subcommand applies its own filter, sort, limit, offset, fields, and count options.

```bash
printf 'function list --limit 5\nquery functions --count\n' | tools/g batch --read-only -
```

Bridge lifecycle commands (`start`, `stop`, `restart`, `status`, `ping`, `jobs`,
and `cancel`) honor JSON flags and saved JSON preferences. `restart` returns one
final JSON result.

`tools/g session-status` and `tools/pe import FILE` also accept `--json` and
`--pretty` before or after the command. `GHIDRA_AGENT=1` remains a wrapper
shorthand for `--json`. PE import runs full headless analysis in each format;
put extra headless/script arguments after `--`.
