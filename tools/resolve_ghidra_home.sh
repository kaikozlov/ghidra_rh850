#!/usr/bin/env bash
# Resolve GHIDRA_HOME for this repo's pinned Ghidra 12.1.3 install.
set -euo pipefail

if [[ -n ${GHIDRA_HOME:-} ]]; then
  :
elif command -v brew >/dev/null 2>&1 && brew --prefix ghidra >/dev/null 2>&1; then
  GHIDRA_HOME="$(brew --prefix ghidra)/libexec"
else
  GHIDRA_HOME="/opt/homebrew/opt/ghidra/libexec"
fi

GHIDRA_HOME=$(cd "$GHIDRA_HOME" 2>/dev/null && pwd) || {
  echo "Ghidra home does not exist: ${GHIDRA_HOME:-<unset>}" >&2
  exit 1
}

echo "$GHIDRA_HOME"
