#!/usr/bin/env bash
# Regenerate data/application_rx_consumer_audit.csv from build/work/project.
# Read-only; never opens committed project/ and never runs analysis.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
PROJECT_DIR="${PROJECT_DIR:-$BUILD_WORK/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
MAP="${MAP:-$ROOT/data/application_rx_map.csv}"
OUT="${1:-$ROOT/data/application_rx_consumer_audit.csv}"

PROJECT_DIR=$(python3 - "$PROJECT_DIR" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1]).expanduser().resolve()
if any(part.startswith('.') for part in path.parts if part not in ('.', '..')):
    raise SystemExit(f"Ghidra rejects dot-prefixed path components: {path}")
print(path)
PY
)
MAP=$(python3 -c 'import sys; from pathlib import Path; print(Path(sys.argv[1]).expanduser().resolve())' "$MAP")
OUT=$(python3 -c 'import sys; from pathlib import Path; print(Path(sys.argv[1]).expanduser().resolve())' "$OUT")

if [[ ! -d "$PROJECT_DIR/$PROJECT_NAME.rep" ]]; then
  echo "missing working project: $PROJECT_DIR/$PROJECT_NAME.rep" >&2
  exit 1
fi
case "$PROJECT_DIR" in
  "$ROOT/project"|"$ROOT/project/"*) echo "refusing committed project/: $PROJECT_DIR" >&2; exit 1 ;;
esac

# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" none
mkdir -p "$(dirname "$OUT")" "$BUILD_LOGS"
LOG="$BUILD_LOGS/generate-application-rx-consumer-audit.log"

"$ROOT/tools/run_headless" \
  --project-dir "$PROJECT_DIR" \
  --project "$PROJECT_NAME" \
  --label application-rx-consumer-audit \
  --log "$LOG" \
  --quiet \
  -- \
  -process "$PROGRAM_NAME" \
  -noanalysis \
  -readOnly \
  -postScript ExportApplicationRxConsumerAudit.java "$MAP" "$OUT"

rg -q 'ExportApplicationRxConsumerAudit: rows=' "$LOG" || {
  echo "consumer-audit exporter did not report success — see $LOG" >&2
  exit 1
}
echo "Wrote audit: $OUT"
echo "Log: $LOG"
