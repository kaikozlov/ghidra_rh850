#!/usr/bin/env bash
# Processor semantic gate: SLEIGH compile, synthetic fixture checks, and
# (when a working project exists) full-program audits via analyzeHeadless so
# the isolated extension is used without mutating GHIDRA_HOME.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROJECT_DIR="${PROJECT_DIR:-$ROOT/build/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
FIXTURE_DIR="$ROOT/tests/fixtures/processor"
FIXTURE_PROJECT_DIR="$ROOT/build/processor-fixture-project"
mkdir -p "$ROOT/build"

"$ROOT/tools/install_v850_extension.sh"
# shellcheck disable=SC1091
source "$ROOT/build/ghidra-processor.env"

python3 "$ROOT/tools/build_processor_fixture.py" --out-dir "$FIXTURE_DIR"
MANIFEST="$FIXTURE_DIR/manifest.json"
BINARY="$FIXTURE_DIR/rh850_semantic_fixture.bin"
ANALYZE="$GHIDRA_HOME/support/analyzeHeadless"
SCRIPT_PATH="$ROOT/ghidra/scripts/verify;$ROOT/ghidra/scripts/investigate;$ROOT/ghidra/scripts/import;$ROOT/ghidra/scripts/annotate"

fail_if_script_error() {
  local log=$1
  local label=$2
  if grep -E 'REPORT SCRIPT ERROR|IllegalStateException' "$log" >/dev/null; then
    echo "$label failed — see $log" >&2
    exit 1
  fi
}

echo "==> Synthetic fixture project"
rm -rf "$FIXTURE_PROJECT_DIR"
mkdir -p "$FIXTURE_PROJECT_DIR"
FIXTURE_LOG="$ROOT/build/verify-processor-fixture.log"
"$ANALYZE" "$FIXTURE_PROJECT_DIR" rh850_fixture \
  -import "$BINARY" \
  -processor v850e3:LE:32:default \
  -loader BinaryLoader \
  -loader-baseAddr 0x0 \
  -noanalysis \
  -scriptPath "$SCRIPT_PATH" \
  -postScript AssertProcessorFixtureSemantics.java "$MANIFEST" \
  -deleteProject \
  2>&1 | tee "$FIXTURE_LOG"
fail_if_script_error "$FIXTURE_LOG" "synthetic fixture verification"
grep -q 'ASSERT processor-fixture: all .* cases passed' "$FIXTURE_LOG" || {
  echo "synthetic fixture did not report success" >&2
  exit 1
}

echo "==> Working-project audits (if present)"
if [[ -d "$PROJECT_DIR/$PROJECT_NAME.rep" ]]; then
  if [[ -f "$PROJECT_DIR/processor_manifest.json" ]]; then
    python3 "$ROOT/tools/fingerprint_processor.py" \
      --expect "$PROJECT_DIR/processor_manifest.json" \
      --ghidra-version "$GHIDRA_VERSION" \
      --cli-version "$GHIDRA_CLI_VERSION" \
      --sla "$V850_EXT_DIR/data/languages/v850e3.sla"
  else
    echo "NOTE: no processor_manifest.json beside working project yet"
  fi

  INV_OUT="$ROOT/data/instruction_inventory.csv"
  DECOMPILER_REPORT="$ROOT/build/decompiler-signatures.txt"
  mkdir -p "$(dirname "$INV_OUT")"
  PROJECT_LOG="$ROOT/build/verify-processor-project.log"

  # Use durable headless -process so GHIDRA_JAVA_OPTIONS/-Duser.home applies.
  "$ANALYZE" "$PROJECT_DIR" "$PROJECT_NAME" \
    -process "$PROGRAM_NAME" \
    -noanalysis \
    -readOnly \
    -scriptPath "$SCRIPT_PATH" \
    -postScript AssertNoUndefinedInFunctions.java \
    -postScript AssertSystemRegisterNames.java \
    -postScript AssertProjectInvariants.java \
    -postScript AssertSwitchTables.java \
    -postScript AssertDecompilerInvariants.java "$DECOMPILER_REPORT" \
    -postScript InventoryUsedInstructions.java "$INV_OUT" "$ROOT/data/processor_unimpl_allowlist.txt" \
    2>&1 | tee "$PROJECT_LOG"
  fail_if_script_error "$PROJECT_LOG" "processor project audits"
  if ! cmp -s "$ROOT/data/decompiler_signatures.baseline.csv" "$DECOMPILER_REPORT"; then
    echo "decompiler signature baseline mismatch:" >&2
    diff -u "$ROOT/data/decompiler_signatures.baseline.csv" "$DECOMPILER_REPORT" >&2 || true
    exit 1
  fi

  echo "Wrote instruction inventory: $INV_OUT"
else
  echo "NOTE: $PROJECT_DIR missing; skipped full-program processor audits"
  echo "      run 'make work-project' or 'make rebuild-project' first"
fi

echo "verify-processor passed"
