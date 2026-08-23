#!/usr/bin/env bash
# Export a deterministic normalized inventory from build/work/project.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
mkdir -p "$BUILD_CACHE" "$BUILD_WORK" "$BUILD_OUT" "$BUILD_LOGS" "$BUILD_TMP"
PROJECT_DIR="${PROJECT_DIR:-$BUILD_WORK/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
OUT="${1:-$BUILD_OUT/ghidra_project_inventory.jsonl}"
LOG="$BUILD_LOGS/generate-project-inventory.log"

[[ -d "$PROJECT_DIR/$PROJECT_NAME.rep" ]] || {
  echo "missing working project: $PROJECT_DIR/$PROJECT_NAME.rep" >&2
  echo "run 'make work-project' or 'make rebuild-project' first" >&2
  exit 1
}

case "$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$PROJECT_DIR")" in
  "$ROOT/project"|"$ROOT/project/"*)
    echo "refusing to open committed project/: $PROJECT_DIR" >&2
    exit 1
    ;;
esac

OUT=$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$OUT")
case "$OUT" in
  "$BUILD_OUT/"*) ;;
  *)
    echo "refusing inventory output outside $BUILD_OUT: $OUT" >&2
    exit 1
    ;;
esac
rm -f "$OUT"
mkdir -p "$(dirname "$OUT")"

# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" none

"$ROOT/tools/run_headless" \
  --project-dir "$PROJECT_DIR" \
  --project "$PROJECT_NAME" \
  --label project-inventory \
  --log "$LOG" \
  --quiet \
  -- \
  -process "$PROGRAM_NAME" \
  -noanalysis \
  -readOnly \
  -postScript ExportProjectInventory.java "$OUT"

grep -q 'ExportProjectInventory: wrote ' "$LOG" || {
  echo "inventory exporter did not report success — see $LOG" >&2
  exit 1
}
python3 "$ROOT/tools/project_inventory.py" validate "$OUT"
echo "Wrote canonical project inventory: $OUT"
echo "Log: $LOG"
