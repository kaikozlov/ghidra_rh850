#!/usr/bin/env bash
# Compile vendored SLEIGH and install into an isolated Ghidra user-home
# Extensions directory. Never mutates $GHIDRA_HOME/Ghidra/Extensions.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
GHIDRA_HOME="$("$ROOT/tools/resolve_ghidra_home.sh")"
VENDOR="$ROOT/ghidra/ghidra_v850"
BUILD_EXT="$ROOT/build/processor-extension-src/Renesas_v850"
LANG="$BUILD_EXT/data/languages"
USER_HOME="${GHIDRA_ISOLATED_HOME:-$ROOT/build/ghidra-home}"
SETTINGS_DIR="$USER_HOME/Library/ghidra/ghidra_12.1.2_PUBLIC"
EXT_DIR="${V850_EXT_DIR:-$SETTINGS_DIR/Extensions/Renesas_v850}"
LOG_DIR="$ROOT/build/sleigh-logs"
MANIFEST="${PROCESSOR_MANIFEST:-$ROOT/build/processor_manifest.json}"

GHIDRA_VERSION=$(awk -F= '$1 == "application.version" { print $2 }' "$GHIDRA_HOME/Ghidra/application.properties")
[[ "$GHIDRA_VERSION" == "12.1.2" ]] || {
  echo "Ghidra 12.1.2 is required (found ${GHIDRA_VERSION:-unknown})" >&2
  exit 1
}
CLI_VERSION="missing"
GHIDRA_CLI_BIN=""
if [[ -x "$ROOT/build/ghidra-cli/ghidra" ]]; then
  GHIDRA_CLI_BIN="$ROOT/build/ghidra-cli/ghidra"
  CLI_VERSION=$("$GHIDRA_CLI_BIN" --version | awk 'NR == 1 { print $2 }')
  [[ "$CLI_VERSION" == "0.2.1" ]] || {
    echo "vendored ghidra CLI version mismatch (found $CLI_VERSION)" >&2
    exit 1
  }
elif command -v ghidra >/dev/null 2>&1; then
  GHIDRA_CLI_BIN=$(command -v ghidra)
  CLI_VERSION=$(ghidra --version | awk 'NR == 1 { print $2 }')
  [[ "$CLI_VERSION" == "0.2.1" ]] || {
    echo "ghidra CLI 0.2.1 is required when present (found $CLI_VERSION)" >&2
    exit 1
  }
else
  echo "NOTE: ghidra CLI not built or on PATH; SLEIGH compile will still proceed" >&2
fi

command -v rsync >/dev/null 2>&1 || { echo "rsync is required" >&2; exit 1; }
mkdir -p "$LOG_DIR" "$SETTINGS_DIR/Extensions" "$(dirname "$BUILD_EXT")"

INSTALL_TREE_EXT="$GHIDRA_HOME/Ghidra/Extensions/Renesas_v850"
if [[ -e "$INSTALL_TREE_EXT" ]]; then
  echo "ERROR: conflicting install-tree extension exists at:" >&2
  echo "  $INSTALL_TREE_EXT" >&2
  echo "Remove it explicitly; this isolated installer will never modify GHIDRA_HOME." >&2
  exit 1
fi

# Build from a disposable copy so generated .sla files never touch vendored
# sources. Exclude any stale local outputs that may predate this installer.
rm -rf "$BUILD_EXT"
mkdir -p "$BUILD_EXT"
rsync -a --delete --exclude '.git' --exclude '*.sla' "$VENDOR/" "$BUILD_EXT/"

echo "Compiling vendored SLEIGH sources under $LANG"
(
  cd "$LANG"
  for spec in *.slaspec; do
    log="$LOG_DIR/${spec%.slaspec}.log"
    if ! JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -Duser.home=$USER_HOME" \
      "$GHIDRA_HOME/support/sleigh" "$spec" >"$log" 2>&1; then
      echo "sleigh failed for $spec; see $log" >&2
      cat "$log" >&2
      exit 1
    fi
    if grep -E '\bERROR\b|Exception' "$log" >/dev/null 2>&1; then
      echo "unexpected sleigh diagnostics in $log" >&2
      cat "$log" >&2
      exit 1
    fi
    unexpected_warnings=$(grep -E '\bWARN(ING)?\b' "$log" \
      | grep -Ev 'WARN  (24|26) NOP constructors found|WARN  Use -n switch to list each individually' \
      || true)
    if [[ -n "$unexpected_warnings" ]]; then
      echo "unexpected sleigh warnings in $log" >&2
      printf '%s\n' "$unexpected_warnings" >&2
      exit 1
    fi
  done
)
[[ -f "$LANG/v850e3.sla" ]] || { echo "sleigh did not produce v850e3.sla" >&2; exit 1; }

echo "Installing Renesas_v850 -> $EXT_DIR"
mkdir -p "$(dirname "$EXT_DIR")"
rsync -a --delete "$BUILD_EXT/" "$EXT_DIR/"

python3 "$ROOT/tools/fingerprint_processor.py" \
  --ghidra-version "$GHIDRA_VERSION" \
  --cli-version "$CLI_VERSION" \
  --sla "$LANG/v850e3.sla" \
  --write "$MANIFEST"

# Emit a small env file callers can source.
ENV_FILE="$ROOT/build/ghidra-processor.env"
cat >"$ENV_FILE" <<EOF
export GHIDRA_HOME="$GHIDRA_HOME"
export GHIDRA_ISOLATED_HOME="$USER_HOME"
export V850_EXT_DIR="$EXT_DIR"
export V850_BUILD_DIR="$BUILD_EXT"
export PROCESSOR_MANIFEST="$MANIFEST"
export GHIDRA_VERSION="$GHIDRA_VERSION"
export GHIDRA_CLI_VERSION="$CLI_VERSION"
export GHIDRA_JAVA_OPTIONS="\${GHIDRA_JAVA_OPTIONS:-} -Duser.home=$USER_HOME"
export GHIDRA_HEADLESS_JAVA_OPTIONS="\${GHIDRA_HEADLESS_JAVA_OPTIONS:-} -Duser.home=$USER_HOME"
EOF

echo "Installed extension: $EXT_DIR"
echo "Processor manifest: $MANIFEST"
echo "Env helper: $ENV_FILE"
