#!/usr/bin/env bash
# Compile-only SLEIGH smoke check with isolated extension install.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
"$ROOT/tools/install_v850_extension.sh"

# Isolation proof: confirm the install-tree copy is absent and the isolated
# extension provides a compiled v850e3.sla matching the fingerprint.
# shellcheck disable=SC1091
source "$ROOT/build/ghidra-processor.env"
INSTALL_TREE_EXT="$GHIDRA_HOME/Ghidra/Extensions/Renesas_v850"
if [[ -e "$INSTALL_TREE_EXT" ]]; then
  echo "ERROR: install-tree extension still present at $INSTALL_TREE_EXT" >&2
  exit 1
fi
[[ -f "$V850_EXT_DIR/data/languages/v850e3.sla" ]] || {
  echo "isolated extension missing v850e3.sla" >&2
  exit 1
}
python3 "$ROOT/tools/fingerprint_processor.py" \
  --expect "$PROCESSOR_MANIFEST" \
  --sla "$V850_EXT_DIR/data/languages/v850e3.sla" >/dev/null

echo "verify-sleigh passed (isolated extension resolves without install-tree copy)"
