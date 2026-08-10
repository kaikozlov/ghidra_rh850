#!/usr/bin/env bash
# Compile-only SLEIGH smoke check with isolated extension install.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

# Shared environment setup: resolve Ghidra, install processor extension,
# source env file, validate fingerprint.
# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" full

# Isolation proof: confirm the install-tree copy is absent and the isolated
# extension provides a compiled v850e3.sla matching the fingerprint.
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
"$ROOT/tools/run_headless" \
  --project-dir "$RESOLVE_PROJECT" \
  --project resolve_v850 \
  --label language-resolution \
  --log "$RESOLVE_LOG" \
  --quiet \
  -- \
  -import "$ROOT/tests/fixtures/processor/rh850_semantic_fixture.bin" \
  -processor v850e3:LE:32:default \
  -loader BinaryLoader \
  -loader-baseAddr 0x0 \
  -noanalysis \
  -deleteProject
grep -Eq 'Language.*v850e3:LE:32:default|v850e3:LE:32:default' "$RESOLVE_LOG" || {
  echo "isolated language resolution did not report v850e3:LE:32:default" >&2
  cat "$RESOLVE_LOG" >&2
  exit 1
}

# Physical snapshot hardening: the committed database is stored under names
# Ghidra cannot recognize. This deliberately bypasses tools/run_headless to
# prove a raw/subagent analyzeHeadless invocation cannot open project/.
python3 "$ROOT/tools/project_layout.py" validate-snapshot \
  --snapshot-dir "$ROOT/project" --project-name rh850_p1me_mapped
RAW_OPEN_LOG="$ROOT/build/sleigh-logs/committed-snapshot-raw-open.log"
set +e
"$GHIDRA_HOME/support/analyzeHeadless" "$ROOT/project" rh850_p1me_mapped \
  -process RH850_P1M-E_CodeFlash.bin -noanalysis -readOnly \
  >"$RAW_OPEN_LOG" 2>&1
raw_open_rc=$?
set -e
if ((raw_open_rc == 0)) || ! grep -q 'Could not find project' "$RAW_OPEN_LOG"; then
  echo "committed project/ was unexpectedly openable by raw analyzeHeadless" >&2
  cat "$RAW_OPEN_LOG" >&2
  exit 1
fi

echo "verify-sleigh passed (isolated extension resolved; committed snapshot non-openable)"
