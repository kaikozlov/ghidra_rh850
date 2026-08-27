#!/usr/bin/env bash
# Resolve/build the ghidra CLI binary for this repo.
#
# Usage:
#   tools/resolve_ghidra_cli.sh                    # existing resolver behavior
#   tools/resolve_ghidra_cli.sh --ensure-vendored # rebuild missing/stale vendored CLI; no system fallback
#   tools/resolve_ghidra_cli.sh --ensure-vendored --allow-system
#
# The vendored source freshness policy lives here so tools/g, tools/pe, and any
# future wrapper cannot silently disagree about which ghidra-cli build is current.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
VENDOR_SRC="$ROOT/ghidra/ghidra-cli/src"
VENDORED_BIN="$BUILD_CACHE/ghidra-cli/ghidra"
ENV_FILE="$BUILD_CACHE/ghidra-cli.env"
ENSURE_VENDORED=0
ALLOW_SYSTEM=1

for arg in "$@"; do
  case "$arg" in
    --ensure-vendored) ENSURE_VENDORED=1; ALLOW_SYSTEM=0 ;;
    --allow-system) ALLOW_SYSTEM=1 ;;
    *) echo "unknown resolve_ghidra_cli option: $arg" >&2; exit 2 ;;
  esac
done

if [[ -z "${VENDORED_GHIDRA_CLI:-}" && -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

# The env file is advisory; the canonical repo cache path owns freshness.
NEED_BUILD=0
if ((ENSURE_VENDORED)); then
  if [[ ! -x "$VENDORED_BIN" ]]; then
    NEED_BUILD=1
  elif [[ -d "$VENDOR_SRC" ]] && find "$VENDOR_SRC" -type f \( -name '*.rs' -o -name '*.java' \) \
       -newer "$VENDORED_BIN" -print -quit 2>/dev/null | grep -q .; then
    NEED_BUILD=1
  fi
  if ((NEED_BUILD)); then
    if [[ -x "$ROOT/tools/build_ghidra_cli.sh" ]] && command -v cargo >/dev/null 2>&1; then
      echo "Vendored ghidra CLI is missing or stale — rebuilding..." >&2
      "$ROOT/tools/build_ghidra_cli.sh" >&2
    elif ((ALLOW_SYSTEM == 0)); then
      echo "ghidra CLI not found/current and vendored rebuild is unavailable. Run 'make ghidra-cli'." >&2
      exit 1
    fi
  fi
fi

if [[ -x "$VENDORED_BIN" ]]; then
  echo "$VENDORED_BIN"
  exit 0
fi
if [[ -n "${VENDORED_GHIDRA_CLI:-}" && -x "$VENDORED_GHIDRA_CLI" && $ENSURE_VENDORED -eq 0 ]]; then
  echo "$VENDORED_GHIDRA_CLI"
  exit 0
fi
if ((ALLOW_SYSTEM)) && command -v ghidra >/dev/null 2>&1; then
  command -v ghidra
  exit 0
fi

echo "ghidra CLI not found. Run 'make ghidra-cli' to build the vendored copy." >&2
if ((ALLOW_SYSTEM == 0)); then
  echo "System fallback is disabled for this caller." >&2
else
  echo "or install ghidra-cli 0.2.1 on PATH." >&2
fi
exit 1
