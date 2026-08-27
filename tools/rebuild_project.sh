#!/usr/bin/env bash
# Rebuild the complete annotated Ghidra project in staged durable headless commits.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
mkdir -p "$BUILD_CACHE" "$BUILD_WORK" "$BUILD_OUT" "$BUILD_LOGS" "$BUILD_TMP"
PROJECT_DIR="$BUILD_WORK/project"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
PROCESSOR="v850e3:LE:32:default"
FORCE=0
REFRESH_DIAGNOSTIC_VOCABULARY=0

usage() {
  cat <<'EOF'
Usage: tools/rebuild_project.sh [options]

Options:
  --project-dir DIR   Output directory (default: build/work/project)
  --ghidra-home DIR  Ghidra installation root (or set GHIDRA_HOME)
  --force            Remove an existing output project first
  --refresh-diagnostic-vocabulary
                     Regenerate the tracked vocabulary from local Techstream
  -h, --help         Show this help

The output must resolve to a dedicated directory below build/work/. Committed
project/, cache/output namespaces, and arbitrary external paths are never rebuild destinations.
EOF
}

while (($#)); do
  case "$1" in
    --project-dir)
      PROJECT_DIR=${2:?missing argument for --project-dir}
      shift 2
      ;;
    --ghidra-home)
      GHIDRA_HOME=${2:?missing argument for --ghidra-home}
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --refresh-diagnostic-vocabulary)
      REFRESH_DIAGNOSTIC_VOCABULARY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

PROJECT_DIR=$(python3 - "$PROJECT_DIR" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1]).expanduser().resolve()
if any(part.startswith(".") for part in path.parts if part not in (".", "..")):
    raise SystemExit(f"Ghidra rejects dot-prefixed path components: {path}")
print(path)
PY
)

case "$PROJECT_DIR" in
  "$BUILD_WORK"|"$BUILD_WORK/")
    echo "refusing to use the work root itself as a rebuild destination" >&2
    exit 1
    ;;
  "$BUILD_WORK/"*) ;;
  *)
    echo "refusing rebuild destination outside $BUILD_WORK: $PROJECT_DIR" >&2
    exit 1
    ;;
esac

command -v cargo >/dev/null 2>&1 || { echo "cargo is required (to build vendored ghidra-cli)" >&2; exit 1; }
# Prefer the vendored ghidra-cli build; build it if missing.
if [[ ! -x "$BUILD_CACHE/ghidra-cli/ghidra" ]]; then
  "$ROOT/tools/build_ghidra_cli.sh"
fi

# --- Shared environment setup -------------------------------------------------
# This resolves GHIDRA_HOME (honoring --ghidra-home), validates version 12.1.3,
# installs the isolated processor extension, sources the env file, and validates
# the processor fingerprint.
# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" full

# --- Vendored GhidraFindcrypt analysis extension (isolated) ------------------
# Prebuilt Ghidra extension that labels crypto constants during auto-analysis.
# Same isolated-user-home pattern as the v850 processor module.
"$ROOT/tools/install_findcrypt_extension.sh"

if pgrep -f 'AnalyzeHeadless.*rh850_p1me_mapped' >/dev/null 2>&1; then
  echo "an RH850 AnalyzeHeadless process is already running; stop it before rebuilding" >&2
  pgrep -af 'AnalyzeHeadless.*rh850_p1me_mapped' >&2 || true
  exit 1
fi

if [[ -e "$PROJECT_DIR/$PROJECT_NAME.gpr" || -e "$PROJECT_DIR/$PROJECT_NAME.rep" ]]; then
  if ((FORCE == 0)); then
    echo "output project already exists: $PROJECT_DIR (use --force to replace it)" >&2
    exit 1
  fi
  rm -rf "$PROJECT_DIR"
fi
mkdir -p "$PROJECT_DIR"
cat >"$PROJECT_DIR/.gitignore" <<'EOF'
# Ghidra project transient files — created when a daemon has the project open.
# Never commit these; they are regenerated on open and are machine-specific.
*.lock
*.lock~
**/tmp*
**/~journal*
EOF

CODEFLASH="$ROOT/firmware/RH850_P1M-E_CodeFlash.bin"
DATAFLASH="$ROOT/firmware/RH850_P1M-E_DataFlash.bin"
run_headless() {
  local stage=$1
  shift
  local project_dir=$1
  local project_name=$2
  shift 2
  local log="$BUILD_LOGS/rebuild-${stage}.log"
  "$ROOT/tools/run_headless" \
    --project-dir "$project_dir" \
    --project "$project_name" \
    --label "rebuild-$stage" \
    --log "$log" \
    --quiet \
    -- "$@"
  if [[ "$stage" == "annotate" || "$stage" == "finalize-conventions" ]]; then
    rg -n 'ApplyCallingConventions:|RecoverSwitchTables:|RecoverVectorHandlers:' "$log" || true
  fi
}

echo "Rebuilding $PROJECT_NAME in $PROJECT_DIR"
echo "Ghidra: $GHIDRA_HOME"
echo "Isolated v850 plugin: $V850_EXT_DIR"
echo "Processor manifest: $PROCESSOR_MANIFEST"

# Fail before any expensive analysis if the tracked mechanical-annotation recipe
# is malformed or missing. Stage 4 consumes this exact validated path.
ANNOTATION_LEDGER="$ROOT/data/annotations/annotation_ledger.jsonl"
"$ROOT/tools/annotations" --ledger "$ANNOTATION_LEDGER" validate >/dev/null

# Analysis is intentionally staged. Ghidra discovers a different graph if all
# seeds are injected before its first pass; these four durable analysis commits
# reproduce the checked-in project's exact function/instruction/symbol counts.
# A separate -noanalysis convention finalizer follows (not a fifth analysis stage).
# Note: the default analyzers (incl. Address Tables, Non-Returning Functions) are
# left enabled deliberately. See docs/tooling/processor-module-audit.md "Why auto-analysis options
# are left on defaults" for the measured rationale.
echo "[1/4] Import mapped images without analysis"
run_headless "import" "$PROJECT_DIR" "$PROJECT_NAME" \
  -import "$CODEFLASH" \
  -processor "$PROCESSOR" \
  -noanalysis \
  -postScript AddDataFlash.java "$DATAFLASH" \
  -postScript ApplyP1MDeviceProfile.java "$ROOT/data/p1m_sfr_labels.csv" \
  -postScript ApplyP1MSfrTypes.java \
  -postScript ApplyRamTypes.java "$ROOT/data/checkpoint_payload_map.csv" \
  -commit "Import mapped CodeFlash and DataFlash"

echo "[2/4] Seed report entries and run base analysis"
run_headless "seed-entries" "$PROJECT_DIR" "$PROJECT_NAME" \
  -process "$PROGRAM_NAME" \
  -preScript SeedEntries.java \
  -commit "Seed report entries and run base analysis"

echo "[3/4] Seed the UDS table and re-run analysis"
run_headless "seed-uds" "$PROJECT_DIR" "$PROJECT_NAME" \
  -process "$PROGRAM_NAME" \
  -preScript SeedUdsServiceTable.java \
  -commit "Seed UDS service table and handlers"

echo "[4/4] Seed missed functions, analyze, and apply every annotation"

# Generate the Techstream diagnostic vocabulary before annotation so that
# ApplyDiagnosticVocabulary.java can consume it during this stage.
VOCAB_PATH=""
FW_SHA=$(shasum -a 256 "$ROOT/firmware/RH850_P1M-E_CodeFlash.bin" | cut -d' ' -f1)
TRACKED_VOCAB="$ROOT/data/generated/${FW_SHA:0:16}/diagnostic_vocabulary.json"
TECHSTREAM_SENTINEL="$ROOT/software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB/EPS_P4DK3.ddb"
if ((REFRESH_DIAGNOSTIC_VOCABULARY)); then
  [[ -f "$TECHSTREAM_SENTINEL" ]] || {
    echo "--refresh-diagnostic-vocabulary requires the local Techstream source tree" >&2
    exit 1
  }
  echo "  Generating Techstream diagnostic vocabulary..."
  ( cd "$ROOT/tools/techstream" && python3 extract_catalog.py )
  ( cd "$ROOT/tools/diagnostics" && python3 correlate_vocabulary.py )
  VOCAB_PATH="$TRACKED_VOCAB"
elif [ -f "$TRACKED_VOCAB" ]; then
  echo "  Using tracked diagnostic vocabulary artifact."
  VOCAB_PATH="$TRACKED_VOCAB"
else
  echo "  No tracked diagnostic vocabulary; skipping optional vocabulary annotation."
fi

VOCAB_SCRIPT_ARGS=()
if [ -n "$VOCAB_PATH" ]; then
  VOCAB_SCRIPT_ARGS=(
    -postScript ApplyDiagnosticVocabulary.java "$VOCAB_PATH"
    -postScript AssertDiagnosticVocabulary.java
  )
fi

run_headless "annotate" "$PROJECT_DIR" "$PROJECT_NAME" \
  -process "$PROGRAM_NAME" \
  -preScript SeedCanTransportFunctions.java \
  -preScript SeedPayloadVerificationFunctions.java \
  -preScript SeedSecocNvmFunctions.java \
  -preScript SeedSecocApplicationFunctions.java \
  -preScript SeedDataFlashSemanticsFunctions.java \
  -preScript SeedApplicationDiagnosticFunctions.java \
  -preScript SeedDidCallbacks.java \
  -preScript SeedBootloaderDiagnosticFunctions.java \
  -preScript SeedArchitectureFunctions.java \
  -preScript SeedApplicationTransmitFunctions.java \
  -preScript SeedApplicationReceiveFunctions.java \
  -preScript SeedRecoveredCallbackTables.java \
  -preScript SeedDispatchProvenFunctionTables.java \
  -preScript SeedBoundedPointerWrappers.java \
  -preScript SeedDirectCallTargets.java \
  -postScript AnnotateBootloaderSecrets.java \
  -postScript AnnotatePayloadGate.java \
  -postScript AnnotateSecocNvmCorrection.java \
  -postScript AnnotateSecocApplication.java \
  -postScript AnnotateDataFlashLayout.java \
  -postScript AnnotateDidModel.java \
  -postScript AnnotateCanTransport.java \
  -postScript AnnotateApplicationDiagnostics.java \
  "${VOCAB_SCRIPT_ARGS[@]}" \
  -postScript AnnotateControlPartition.java \
  -postScript AnnotateBootloaderDiagnostics.java \
  -postScript RecoverVectorHandlers.java \
  -postScript RecoverSwitchTables.java \
  -postScript AnnotateArchitecture.java \
  -postScript AnnotateApplicationTransmit.java \
  -postScript AnnotateApplicationReceive.java \
  -postScript AnnotateLargeFunctions.java \
  -postScript SeedDirectCallTargets.java \
  -postScript ApplyCallingConventions.java \
  -postScript ApplyAnnotationLedger.java "$ANNOTATION_LEDGER" \
  -commit "Complete reproducible RH850 analysis"

# Convention finalizer (not an analysis stage): after the annotate-stage commit,
# a -noanalysis reopen consistently surfaces two additional non-ISR bodies at
# 0x3b0be and 0x6f0d0 that were absent from FunctionManager during stage-4
# ApplyCallingConventions (the iterator count can grow after stage-4 analysis).
# Without this pass newly surfaced bodies
# remain calling-convention "unknown" and fail AssertProjectInvariants /
# AssertDecompilerInvariants. The finalizer assigns conventions to every
# recovered body, including the explicitly seeded ICU-S/key-update family.
echo "[4b] Finalize calling conventions (no analysis)"
run_headless "finalize-conventions" "$PROJECT_DIR" "$PROJECT_NAME" \
  -process "$PROGRAM_NAME" \
  -noanalysis \
  -postScript ApplyCallingConventions.java \
  -commit "Finalize calling conventions"

CLI_ARGS=(
  --projects-dir "$PROJECT_DIR"
  --project "$PROJECT_NAME"
  --program "$PROGRAM_NAME"
)
BRIDGE_STARTED=0
cleanup() {
  if ((BRIDGE_STARTED)); then
    "$GHIDRA_CLI" "${CLI_ARGS[@]}" stop >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

BRIDGE_STARTED=1
STATS_OUTPUT=$("$BUILD_CACHE/ghidra-cli/ghidra" "${CLI_ARGS[@]}" stats)
printf '%s\n' "$STATS_OUTPUT"
"$BUILD_CACHE/ghidra-cli/ghidra" "${CLI_ARGS[@]}" stop
BRIDGE_STARTED=0
trap - EXIT INT TERM

printf '%s\n' "$STATS_OUTPUT" | python3 "$ROOT/tools/verify_ghidra_stats.py"

# Persist processor fingerprint beside the working project.
cp "$PROCESSOR_MANIFEST" "$PROJECT_DIR/processor_manifest.json"
echo "Wrote $PROJECT_DIR/processor_manifest.json"

echo "Durable project rebuild verified: $PROJECT_DIR/$PROJECT_NAME.gpr"
