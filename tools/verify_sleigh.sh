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
  --ghidra-version "$GHIDRA_VERSION" \
  --cli-version "$GHIDRA_CLI_VERSION" \
  --sla "$V850_EXT_DIR/data/languages/v850e3.sla" >/dev/null

if compgen -G "$ROOT/ghidra/ghidra_v850/data/languages/*.sla" >/dev/null; then
  echo "vendored source tree was polluted by generated .sla files" >&2
  exit 1
fi

# Resolve the language in a clean Ghidra subprocess. File existence alone does
# not prove the isolated user-home extension is discoverable.
RESOLVE_PROJECT="$ROOT/build/sleigh-resolution-project"
RESOLVE_LOG="$ROOT/build/sleigh-logs/language-resolution.log"
rm -rf "$RESOLVE_PROJECT"
mkdir -p "$RESOLVE_PROJECT"
"$GHIDRA_HOME/support/analyzeHeadless" "$RESOLVE_PROJECT" resolve_v850 \
  -import "$ROOT/tests/fixtures/processor/rh850_semantic_fixture.bin" \
  -processor v850e3:LE:32:default \
  -loader BinaryLoader \
  -loader-baseAddr 0x0 \
  -noanalysis \
  -deleteProject >"$RESOLVE_LOG" 2>&1
grep -Eq 'Language.*v850e3:LE:32:default|v850e3:LE:32:default' "$RESOLVE_LOG" || {
  echo "isolated language resolution did not report v850e3:LE:32:default" >&2
  cat "$RESOLVE_LOG" >&2
  exit 1
}

echo "verify-sleigh passed (clean subprocess resolved isolated extension)"
