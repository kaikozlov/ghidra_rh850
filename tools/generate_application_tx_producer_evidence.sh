#!/usr/bin/env bash
# Regenerate data/application_tx_producer_evidence.csv from the working Ghidra
# project. Read-only: never opens committed project/ and never analyzes.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
PROJECT_DIR="${PROJECT_DIR:-$BUILD_WORK/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
OUT="${1:-$ROOT/data/application_tx_producer_evidence.csv}"
RAW_REFS="$BUILD_OUT/application_tx_producer_refs.csv"

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
  echo "missing working project: $PROJECT_DIR/$PROJECT_NAME.rep" >&2
  echo "materialize it with: make work-project" >&2
  exit 1
fi
case "$PROJECT_DIR" in
  "$ROOT/project"|"$ROOT/project/"*)
    echo "refusing to open committed project/: $PROJECT_DIR" >&2
    exit 1
    ;;
esac

# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" none
mkdir -p "$BUILD_OUT" "$BUILD_LOGS" "$(dirname "$OUT")"
LOG="$BUILD_LOGS/generate-application-tx-producer-evidence.log"

"$ROOT/tools/run_headless" \
  --project-dir "$PROJECT_DIR" \
  --project "$PROJECT_NAME" \
  --label application-tx-producer-evidence \
  --log "$LOG" \
  --quiet \
  -- \
  -process "$PROGRAM_NAME" \
  -noanalysis \
  -readOnly \
  -postScript ExportApplicationTxProducerRefs.java "$RAW_REFS"

rg -q 'ExportApplicationTxProducerRefs: sources=' "$LOG" || {
  echo "Tx producer-ref exporter did not report success — see $LOG" >&2
  exit 1
}

uv run --locked python "$ROOT/tools/generate_application_tx_producer_evidence.py" \
  --refs "$RAW_REFS" \
  --output "$OUT"

echo "Wrote evidence: $OUT"
echo "Log: $LOG"
