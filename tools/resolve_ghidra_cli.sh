#!/usr/bin/env bash
# Resolve the ghidra CLI binary for this repo.
#
# Preference order:
#   1. $VENDORED_GHIDRA_CLI (set by build/ghidra-cli.env after make ghidra-cli)
#   2. build/ghidra-cli/ghidra (auto-detected vendored build)
#   3. ghidra on PATH (fallback, version-checked by callers)
#
# Prints the binary path to stdout. Exits 1 if none found.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
VENDORED_BIN="$ROOT/build/ghidra-cli/ghidra"
ENV_FILE="$ROOT/build/ghidra-cli.env"

# If the env file exists, source it to pick up VENDORED_GHIDRA_CLI.
if [[ -z "${VENDORED_GHIDRA_CLI:-}" && -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

if [[ -n "${VENDORED_GHIDRA_CLI:-}" && -x "$VENDORED_GHIDRA_CLI" ]]; then
  echo "$VENDORED_GHIDRA_CLI"
  exit 0
fi

if [[ -x "$VENDORED_BIN" ]]; then
  echo "$VENDORED_BIN"
  exit 0
fi

if command -v ghidra >/dev/null 2>&1; then
  command -v ghidra
  exit 0
fi

echo "ghidra CLI not found. Run 'make ghidra-cli' to build the vendored copy," >&2
echo "or install ghidra-cli 0.2.1 on PATH." >&2
exit 1
