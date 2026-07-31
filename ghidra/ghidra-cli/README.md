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
make ghidra-cli    # cargo build --release into build/ghidra-cli/
```

`tools/build_ghidra_cli.sh` runs the isolated release build and emits
`build/ghidra-cli.env`, which the repo's tool scripts source to find the
binary. When the vendored build is present, it is preferred over any `ghidra`
on `PATH`; otherwise the PATH binary is used with a version check.

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
