# ghidra-cli (vendored fork)

This is a Rust CLI wrapper for Ghidra's headless API. It is the tool used by
this repo's `tools/*.sh` scripts and the interactive `ghidra` commands in
[docs/WORKFLOW.md](../../docs/WORKFLOW.md).

It has been vendored in-tree from Kai's fork so the exact CLI version is
maintained alongside the rest of the RH850 analysis work rather than depending
on a separate installed binary. There is no intent to keep patches upstreamable;
the fork is edited freely to serve this project.

Machine-readable provenance lives in [`PROVENANCE.json`](PROVENANCE.json).

## How it is built

The compiled binary (`ghidra`) is **not** committed (see `.gitignore`); it is
built from the vendored `src/` by `make ghidra-cli`:

```bash
make ghidra-cli    # cargo build --release into build/cache/ghidra-cli/
```

`tools/project/build_ghidra_cli.sh` runs the isolated release build. The wrappers
rebuild missing or stale vendored binaries automatically. `tools/g` permits a
system `ghidra` fallback only when `GHIDRA_ALLOW_SYSTEM_CLI=1` is set.

Repository-facing ergonomic extensions are exposed through `tools/g`:

```bash
tools/g inspect TARGET [TARGET ...]
tools/g x-ref trace-to ADDRESS [--max-functions N]
tools/g find function '*aes*' --limit 20
tools/g memory search deadbeef
printf 'stats\nquery functions --count\n' | tools/g batch --read-only -
```

A one-target `inspect` retains the original response shape. Multi-target
inspection and reference tracing execute as one queued bridge job, resolve and
bound their full scope before expensive work, and return errors rather than
partial aggregates. Batch input accepts `-` for stdin, preflights every command
before execution, defaults to 100 commands, and offers a conservative
`--read-only` allowlist for scripted investigation.

Output defaults to compact text for terminals and pipes. Use `--json` for
machine-readable results or `--pretty` for indented JSON. The built-in page size
is 50; saved `default_limit` values are preserved, `GHIDRA_CLI_DEFAULT_LIMIT`
overrides the saved value, and command `--limit` takes precedence. `--limit 0`
returns all rows. See [Output and query options](docs/output-format.md) for
filtering, projection, pagination, source/table formats, and batch behavior.

## Inline Ghidra scripts

Use inline scripts only with code you trust. Like `script run`, an inline
script runs inside the local bridge with access to the live `currentProgram`
and the normal Ghidra script API. It can change the open program. Changes
follow the normal bridge persistence rules; `batch --read-only` rejects both
inline commands.

```bash
tools/g script java 'println(currentProgram.getName());'
tools/g script python 'print(currentProgram.getName())'
```

Java accepts statements for a `GhidraScript.run()` body and needs the full
JDK that `ghidra doctor` reports. Python accepts a Python 3 script and needs a
bridge launched with a CPython interpreter that has the Ghidra installation's
matching PyGhidra package. The CLI stages each snippet in a private temporary
directory and sends its path to the existing script runner. Script output
appears in `stdout` with `--json`; compile and runtime failures return a nonzero
exit status and include any captured diagnostics.

After `uv sync --locked`, `tools/g`, `tools/gtarget`, and `tools/pe` start
bridges with the repository's `.venv/bin/python`. They honor uv's
`UV_PROJECT_ENVIRONMENT` if configured. No activation or export is needed.
If the project's bridge is already running Java-only, stop it cleanly once
with the same wrapper (`tools/g stop` or `tools/pe stop`).

When invoking the Rust binary directly instead of a repository wrapper,
`GHIDRA_CLI_PYGHIDRA_PYTHON` selects its interpreter at bridge startup.
Without it the standalone CLI starts a Java-only bridge.

Inline requests wait for the script to return. From a second terminal, use
`ghidra --project PROJECT jobs` and `ghidra --project PROJECT cancel JOB_ID`.
Cancellation is cooperative: long scripts should call `monitor.checkCancelled()`
or use Ghidra operations that poll their monitor.

To test the standalone CLI with the same interpreter and its synthetic fixture:

```bash
GHIDRA_CLI_PYGHIDRA_PYTHON="$PWD/.venv/bin/python" \
  cargo test --manifest-path ghidra/ghidra-cli/Cargo.toml --locked \
  --test script_tests test_script_inline -- --nocapture
```

## Headless resource configuration

Defaults live in `src/config.rs`: `max_heap` is `8G`; `cpu_workers` is available
CPUs plus one, capped at ten.

Machine-local overrides via configuration commands:

```bash
build/cache/ghidra-cli/ghidra config set max_heap 4G
build/cache/ghidra-cli/ghidra config set cpu_workers 8
build/cache/ghidra-cli/ghidra config list
```

## What's here

Everything in this directory is the fork's source tree as of the baseline
commit in `PROVENANCE.json`. The upstream `.github/` (CI) and `.claude/`
(Agent configs) directories are stripped — this repo has its own CI and
tooling. The upstream `tests/fixtures/sample_binary` (a 3.8 MB ELF) is kept
because the CLI's own test suite needs it.

## Prerequisites

- Rust toolchain (stable, `cargo` on PATH).

## Upstream

- Fork: <https://github.com/kaikozlov/ghidra-cli>
- Original: <https://github.com/akiselev/ghidra-cli>
