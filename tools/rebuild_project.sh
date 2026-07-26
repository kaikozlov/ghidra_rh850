#!/usr/bin/env bash
# Rebuild the complete annotated Ghidra project in staged durable headless commits.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROJECT_DIR="$ROOT/build/project"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
PROCESSOR="v850e3:LE:32:default"
FORCE=0

usage() {
  cat <<'EOF'
Usage: tools/rebuild_project.sh [options]

Options:
  --project-dir DIR   Output directory (default: build/project)
  --ghidra-home DIR  Ghidra installation root (or set GHIDRA_HOME)
  --force            Remove an existing output project first
  -h, --help         Show this help

The output path must be absolute after resolution and may not contain a
component beginning with '.'. The committed project/ directory is never
replaced unless explicitly selected with --project-dir and --force.
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

if [[ -z ${GHIDRA_HOME:-} ]]; then
  if command -v brew >/dev/null 2>&1 && brew --prefix ghidra >/dev/null 2>&1; then
    GHIDRA_HOME="$(brew --prefix ghidra)/libexec"
  else
    GHIDRA_HOME="/opt/homebrew/opt/ghidra/libexec"
  fi
fi
GHIDRA_HOME=$(cd "$GHIDRA_HOME" 2>/dev/null && pwd) || {
  echo "Ghidra home does not exist: ${GHIDRA_HOME:-<unset>}" >&2
  exit 1
}
ANALYZE_HEADLESS="$GHIDRA_HOME/support/analyzeHeadless"
[[ -x "$ANALYZE_HEADLESS" ]] || { echo "missing analyzeHeadless: $ANALYZE_HEADLESS" >&2; exit 1; }
command -v ghidra >/dev/null 2>&1 || { echo "ghidra CLI is required" >&2; exit 1; }
GHIDRA_VERSION=$(awk -F= '$1 == "application.version" { print $2 }' "$GHIDRA_HOME/Ghidra/application.properties")
[[ "$GHIDRA_VERSION" == "12.1.2" ]] || {
  echo "Ghidra 12.1.2 is required (found ${GHIDRA_VERSION:-unknown})" >&2
  exit 1
}
GHIDRA_CLI_VERSION=$(ghidra --version | awk 'NR == 1 { print $2 }')
[[ "$GHIDRA_CLI_VERSION" == "0.2.1" ]] || {
  echo "ghidra CLI 0.2.1 is required (found ${GHIDRA_CLI_VERSION:-unknown})" >&2
  exit 1
}

# --- Vendored Renesas_v850 processor extension -------------------------------
# Source of truth is the in-repo vendored fork at ghidra/ghidra_v850 (forked
# from esaulenka/ghidra_v850). Compile its SLEIGH and install the extension
# into Ghidra's discovered extensions dir so both analyzeHeadless and the
# `ghidra` CLI load our locally-edited processor model.
VENDOR_V850="$ROOT/ghidra/ghidra_v850"
V850_LANG_DIR="$VENDOR_V850/data/languages"
V850_EXT_DIR="$GHIDRA_HOME/Ghidra/Extensions/Renesas_v850"
[[ -f "$V850_LANG_DIR/v850e3.slaspec" ]] || {
  echo "missing vendored v850e3.slaspec: $V850_LANG_DIR/v850e3.slaspec" >&2
  exit 1
}
command -v rsync >/dev/null 2>&1 || { echo "rsync is required to install the vendored extension" >&2; exit 1; }
echo "Compiling vendored SLEIGH sources (*.slaspec)"
( cd "$V850_LANG_DIR" && for spec in *.slaspec; do "$GHIDRA_HOME/support/sleigh" "$spec" >/dev/null; done )
[[ -f "$V850_LANG_DIR/v850e3.sla" ]] || { echo "sleigh did not produce v850e3.sla" >&2; exit 1; }
echo "Installing vendored Renesas_v850 -> $V850_EXT_DIR"
mkdir -p "$V850_EXT_DIR"
rsync -a --delete --exclude '.git' "$VENDOR_V850/" "$V850_EXT_DIR/"

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
  case "$PROJECT_DIR" in
    /|"$ROOT") echo "refusing to remove unsafe path: $PROJECT_DIR" >&2; exit 1 ;;
  esac
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
SCRIPT_PATH="$ROOT/ghidra/scripts/import;$ROOT/ghidra/scripts/seed;$ROOT/ghidra/scripts/annotate"

COMMON_ARGS=(
  -scriptPath "$SCRIPT_PATH"
  -analysisTimeoutPerFile "${GHIDRA_ANALYSIS_TIMEOUT:-1800}"
  -max-cpu "${GHIDRA_MAX_CPU:-4}"
)

echo "Rebuilding $PROJECT_NAME in $PROJECT_DIR"
echo "Ghidra: $GHIDRA_HOME"
echo "Vendored v850 plugin: $VENDOR_V850 (installed -> $V850_EXT_DIR)"

# Analysis is intentionally staged. Ghidra discovers a different graph if all
# seeds are injected before its first pass; these four durable commits reproduce
# the checked-in project's exact function/instruction/symbol counts.
echo "[1/4] Import mapped images without analysis"
"$ANALYZE_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
  -import "$CODEFLASH" \
  -processor "$PROCESSOR" \
  -noanalysis \
  "${COMMON_ARGS[@]}" \
  -postScript AddDataFlash.java "$DATAFLASH" \
  -commit "Import mapped CodeFlash and DataFlash"

echo "[2/4] Seed report entries and run base analysis"
"$ANALYZE_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
  -process "$PROGRAM_NAME" \
  "${COMMON_ARGS[@]}" \
  -preScript SeedEntries.java \
  -commit "Seed report entries and run base analysis"

echo "[3/4] Seed the UDS table and re-run analysis"
"$ANALYZE_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
  -process "$PROGRAM_NAME" \
  "${COMMON_ARGS[@]}" \
  -preScript SeedUdsServiceTable.java \
  -commit "Seed UDS service table and handlers"

echo "[4/4] Seed missed functions, analyze, and apply every annotation"
"$ANALYZE_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
  -process "$PROGRAM_NAME" \
  "${COMMON_ARGS[@]}" \
  -preScript SeedCanTransportFunctions.java \
  -preScript SeedPayloadVerificationFunctions.java \
  -preScript SeedSecocNvmFunctions.java \
  -preScript SeedSecocApplicationFunctions.java \
  -preScript SeedDataFlashSemanticsFunctions.java \
  -preScript SeedApplicationDiagnosticFunctions.java \
  -preScript SeedBootloaderDiagnosticFunctions.java \
  -preScript SeedArchitectureFunctions.java \
  -preScript SeedApplicationTransmitFunctions.java \
  -postScript AnnotateBootloaderSecrets.java \
  -postScript AnnotatePayloadGate.java \
  -postScript AnnotateSecocNvmCorrection.java \
  -postScript AnnotateSecocApplication.java \
  -postScript AnnotateDataFlashLayout.java \
  -postScript AnnotateDidModel.java \
  -postScript AnnotateCanTransport.java \
  -postScript AnnotateApplicationDiagnostics.java \
  -postScript AnnotateBootloaderDiagnostics.java \
  -postScript AnnotateArchitecture.java \
  -postScript AnnotateApplicationTransmit.java \
  -commit "Complete reproducible RH850 analysis"

CLI_ARGS=(
  --projects-dir "$PROJECT_DIR"
  --project "$PROJECT_NAME"
  --program "$PROGRAM_NAME"
)
BRIDGE_STARTED=0
cleanup() {
  if ((BRIDGE_STARTED)); then
    ghidra "${CLI_ARGS[@]}" stop >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

BRIDGE_STARTED=1
STATS_OUTPUT=$(ghidra "${CLI_ARGS[@]}" stats)
printf '%s\n' "$STATS_OUTPUT"
ghidra "${CLI_ARGS[@]}" stop
BRIDGE_STARTED=0
trap - EXIT INT TERM

printf '%s\n' "$STATS_OUTPUT" | python3 "$ROOT/tools/verify_ghidra_stats.py"

echo "Durable project rebuild verified: $PROJECT_DIR/$PROJECT_NAME.gpr"
