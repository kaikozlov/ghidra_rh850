#!/usr/bin/env bash
# Build the vendored ghidra-cli into an isolated output directory.
# Never installs into ~/.cargo/bin or mutates PATH.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
VENDOR="$ROOT/ghidra/ghidra-cli"
OUT_DIR="$BUILD_CACHE/ghidra-cli"
CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$BUILD_CACHE/ghidra-cli-target}"
REQUIRED_VERSION="0.2.1"
export CARGO_TARGET_DIR

command -v cargo >/dev/null 2>&1 || {
  echo "cargo is required to build the vendored ghidra-cli" >&2
  exit 1
}

mkdir -p "$OUT_DIR"

echo "Building vendored ghidra-cli (release)..."
cargo build --locked --release --manifest-path "$VENDOR/Cargo.toml"

# Keep Cargo intermediates under the canonical ignored cache namespace too.
# The vendored source tree must remain source-only.
BIN_SRC="$CARGO_TARGET_DIR/release/ghidra"
[[ -x "$BIN_SRC" ]] || {
  echo "expected binary not found: $BIN_SRC" >&2
  exit 1
}
cp "$BIN_SRC" "$OUT_DIR/ghidra"

BUILT_VERSION=$("$OUT_DIR/ghidra" --version | awk 'NR == 1 { print $2 }')
[[ "$BUILT_VERSION" == "$REQUIRED_VERSION" ]] || {
  echo "built ghidra-cli version mismatch: expected $REQUIRED_VERSION, got ${BUILT_VERSION:-unknown}" >&2
  exit 1
}

# Emit a small env file callers can source.
ENV_FILE="$BUILD_CACHE/ghidra-cli.env"
cat >"$ENV_FILE" <<EOF
export VENDORED_GHIDRA_CLI="$OUT_DIR/ghidra"
export GHIDRA_CLI_VERSION="$BUILT_VERSION"
EOF

echo "Built: $OUT_DIR/ghidra (v$BUILT_VERSION)"
echo "Env helper: $ENV_FILE"
