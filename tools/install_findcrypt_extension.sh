#!/usr/bin/env bash
# Install the vendored GhidraFindcrypt extension into the isolated Ghidra
# user-home Extensions directory. Never mutates $GHIDRA_HOME/Ghidra/Extensions.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
GHIDRA_HOME="$("$ROOT/tools/resolve_ghidra_home.sh")"
VENDOR="$ROOT/ghidra/ghidra-findcrypt"
USER_HOME="${GHIDRA_ISOLATED_HOME:-$BUILD_CACHE/ghidra-home}"
SETTINGS_DIR="$USER_HOME/Library/ghidra/ghidra_12.1.3_PUBLIC"
EXT_DIR="$SETTINGS_DIR/Extensions/GhidraFindcrypt"
ZIP_FILE="$VENDOR/ghidra_12.1.3_PUBLIC_20260822_GhidraFindcrypt.zip"

GHIDRA_VERSION=$(awk -F= '$1 == "application.version" { print $2 }' "$GHIDRA_HOME/Ghidra/application.properties")
[[ "$GHIDRA_VERSION" == "12.1.3" ]] || {
  echo "Ghidra 12.1.3 is required (found ${GHIDRA_VERSION:-unknown})" >&2
  exit 1
}

[[ -f "$ZIP_FILE" ]] || {
  echo "findcrypt extension zip not found: $ZIP_FILE" >&2
  exit 1
}

INSTALL_TREE_EXT="$GHIDRA_HOME/Ghidra/Extensions/GhidraFindcrypt"
if [[ -e "$INSTALL_TREE_EXT" ]]; then
  echo "ERROR: conflicting install-tree extension exists at:" >&2
  echo "  $INSTALL_TREE_EXT" >&2
  echo "Remove it explicitly; this isolated installer will never modify GHIDRA_HOME." >&2
  exit 1
fi

mkdir -p "$SETTINGS_DIR/Extensions"

echo "Installing GhidraFindcrypt -> $EXT_DIR"
rm -rf "$EXT_DIR"
unzip -q -o "$ZIP_FILE" -d "$SETTINGS_DIR/Extensions/"

[[ -f "$EXT_DIR/lib/GhidraFindcrypt.jar" ]] || {
  echo "GhidraFindcrypt.jar not found after extraction" >&2
  exit 1
}

echo "Installed extension: $EXT_DIR"
