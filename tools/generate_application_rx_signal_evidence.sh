#!/usr/bin/env bash
# Export data/application_rx_signal_evidence.csv from the working Ghidra project
# at build/project/. Read-only: never opens committed project/, never analyzes,
# never commits daemon state.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROJECT_DIR="${PROJECT_DIR:-$ROOT/build/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
OUT="${1:-$ROOT/data/application_rx_signal_evidence.csv}"
SCRIPT_PATH="$ROOT/ghidra/scripts/verify;$ROOT/ghidra/scripts/investigate;$ROOT/ghidra/scripts/import;$ROOT/ghidra/scripts/annotate;$ROOT/ghidra/scripts/seed"

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
    echo "use build/project via make work-project" >&2
    exit 1
    ;;
esac

"$ROOT/tools/install_v850_extension.sh" >/dev/null
# shellcheck disable=SC1091
source "$ROOT/build/ghidra-processor.env"

ANALYZE="$GHIDRA_HOME/support/analyzeHeadless"
[[ -x "$ANALYZE" ]] || { echo "missing analyzeHeadless: $ANALYZE" >&2; exit 1; }

mkdir -p "$(dirname "$OUT")" "$ROOT/build"
LOG="$ROOT/build/generate-application-rx-signal-evidence.log"

echo "Exporting Rx signal evidence from $PROJECT_DIR"
echo "CSV: $OUT"

set +e
"$ANALYZE" "$PROJECT_DIR" "$PROJECT_NAME" \
  -process "$PROGRAM_NAME" \
  -noanalysis \
  -readOnly \
  -scriptPath "$SCRIPT_PATH" \
  -postScript ExportApplicationRxSignalEvidence.java "$OUT" \
  >"$LOG" 2>&1
rc=$?
set -e

if ((rc != 0)) || rg -q 'REPORT SCRIPT ERROR|IllegalStateException' "$LOG"; then
  echo "Rx signal evidence export failed (rc=$rc) — see $LOG" >&2
  rg -n 'SCRIPT ERROR|IllegalStateException|ExportApplicationRx|ERROR' "$LOG" | tail -40 >&2 || true
  exit 1
fi
rg -q 'ExportApplicationRxSignalEvidence: wrote' "$LOG" || {
  echo "exporter did not report success — see $LOG" >&2
  exit 1
}
echo "Wrote evidence: $OUT"
echo "Log: $LOG"
