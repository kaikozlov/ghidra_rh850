#!/usr/bin/env bash
# Export data/application_rx_signal_evidence.csv from the working Ghidra project
# at build/work/project/. Read-only: never opens committed project/, never analyzes,
# never commits daemon state.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
PROJECT_DIR="${PROJECT_DIR:-$BUILD_WORK/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
OUT="${1:-$ROOT/data/application_rx_signal_evidence.csv}"

PROJECT_DIR=$(python3 - "$PROJECT_DIR" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1]).expanduser().resolve()
if any(part.startswith(".") for part in path.parts if part not in (".", "..")):
    raise SystemExit(f"Ghidra rejects dot-prefixed path components: {path}")
print(path)
PY
)
OUT=$(python3 -c 'import sys; from pathlib import Path; print(Path(sys.argv[1]).expanduser().resolve())' "$OUT")

if [[ ! -d "$PROJECT_DIR/$PROJECT_NAME.rep" ]]; then
  cat >&2 <<EOF
missing working project: $PROJECT_DIR/$PROJECT_NAME.rep
materialize it first (does not open committed project/):
  make work-project
  # or: make rebuild-project
EOF
  exit 1
fi

case "$PROJECT_DIR" in
  "$ROOT/project"|"$ROOT/project/"*)
    echo "refusing to open committed project/: $PROJECT_DIR" >&2
    echo "use build/work/project via make work-project" >&2
    exit 1
    ;;
esac

# Shared environment setup: resolve Ghidra, install processor extension,
# source env file.
# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" none

mkdir -p "$(dirname "$OUT")" "$BUILD_LOGS"
LOG="$BUILD_LOGS/generate-application-rx-signal-evidence.log"

echo "Exporting Rx signal evidence from $PROJECT_DIR"
echo "CSV: $OUT"

"$ROOT/tools/run_headless" \
  --project-dir "$PROJECT_DIR" \
  --project "$PROJECT_NAME" \
  --label application-rx-signal-evidence \
  --log "$LOG" \
  --quiet \
  -- \
  -process "$PROGRAM_NAME" \
  -noanalysis \
  -readOnly \
  -postScript ExportApplicationRxSignalEvidence.java "$OUT"
rg -q 'ExportApplicationRxSignalEvidence: wrote' "$LOG" || {
  echo "exporter did not report success — see $LOG" >&2
  exit 1
}
echo "Wrote evidence: $OUT"
echo "Log: $LOG"
