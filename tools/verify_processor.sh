#!/usr/bin/env bash
# Processor semantic gate: SLEIGH compile, synthetic fixture checks, and
# (when a working project exists) full-program audits via tools/run_headless so
# the isolated extension is used without mutating GHIDRA_HOME.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROJECT_DIR="${PROJECT_DIR:-$ROOT/build/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
FIXTURE_DIR="$ROOT/tests/fixtures/processor"
FIXTURE_PROJECT_DIR="$ROOT/build/processor-fixture-project"
mkdir -p "$ROOT/build"

# Shared environment setup: resolve Ghidra, install processor extension,
# source env file, validate fingerprint.
# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" full

python3 "$ROOT/tools/build_processor_fixture.py" --out-dir "$FIXTURE_DIR"
MANIFEST="$FIXTURE_DIR/manifest.json"
BINARY="$FIXTURE_DIR/rh850_semantic_fixture.bin"

echo "==> Synthetic fixture project"
rm -rf "$FIXTURE_PROJECT_DIR"
mkdir -p "$FIXTURE_PROJECT_DIR"
FIXTURE_LOG="$ROOT/build/verify-processor-fixture.log"
"$ROOT/tools/run_headless" \
  --project-dir "$FIXTURE_PROJECT_DIR" \
  --project rh850_fixture \
  --label processor-fixture \
  --log "$FIXTURE_LOG" \
  --quiet \
  -- \
  -import "$BINARY" \
  -processor v850e3:LE:32:default \
  -loader BinaryLoader \
  -loader-baseAddr 0x0 \
  -noanalysis \
  -postScript AssertProcessorFixtureSemantics.java "$MANIFEST" \
  -deleteProject
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
  "$ROOT/tools/run_headless" \
    --project-dir "$PROJECT_DIR" \
    --project "$PROJECT_NAME" \
    --label processor-project-audits \
    --log "$PROJECT_LOG" \
    --quiet \
    -- \
    -process "$PROGRAM_NAME" \
    -noanalysis \
    -readOnly \
    -postScript AssertNoUndefinedInFunctions.java \
    -postScript AssertSystemRegisterNames.java \
    -postScript AssertProjectInvariants.java "$ROOT/data/checkpoint_payload_map.csv" \
    -postScript AssertApplicationReceiveMap.java "$ROOT/data/application_rx_map.csv" \
    -postScript AssertSecocRxControlSurface.java \
    -postScript AssertApplicationTransmitSemantics.java \
    -postScript AssertApplicationInterfaceStateJoins.java \
    -postScript AssertRecoveredCallbackTables.java \
    -postScript AssertFunctionDiscoveryFloor.java --mutation-self-test \
    -postScript AssertReviewedPointerClusters.java \
    -postScript AssertMemorySafetyPaths.java \
    -postScript AssertMotorActuationBoundary.java \
    -postScript AssertIcusStage7Static.java \
    -postScript AssertSwitchTables.java \
    -postScript AssertDecompilerInvariants.java "$DECOMPILER_REPORT" \
    -postScript InventoryUsedInstructions.java "$INV_OUT" "$ROOT/data/processor_unimpl_allowlist.txt"
  if ! cmp -s "$ROOT/data/decompiler_signatures.baseline.csv" "$DECOMPILER_REPORT"; then
    echo "decompiler signature baseline mismatch:" >&2
    diff -u "$ROOT/data/decompiler_signatures.baseline.csv" "$DECOMPILER_REPORT" >&2 || true
    exit 1
  fi

  echo "Wrote instruction inventory: $INV_OUT"
  grep -E 'ASSERT (processor-fixture|undefined-in-functions|system-register-ops|project-invariants|application-rx-map|secoc-rx-surface|application-tx-semantics|application-interface-joins|function-discovery-floor|reviewed-pointer-clusters|memory-safety-paths|motor-actuation-boundary|icus-stage7|switch-tables|decompiler-invariants|processor-userops)|AssertRecoveredCallbackTables: PASS' \
    "$FIXTURE_LOG" "$PROJECT_LOG" || true
else
  echo "NOTE: $PROJECT_DIR missing; skipped full-program processor audits"
  echo "      run 'make work-project' or 'make rebuild-project' first"
fi

echo "verify-processor passed"
