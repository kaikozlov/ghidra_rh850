#!/usr/bin/env bash
# Generate the outside-function candidate census from a safe working project.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROJECT_DIR="${PROJECT_DIR:-$ROOT/build/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
CSV_OUT="${CSV_OUT:-$ROOT/data/outside_function_candidates.csv}"
SUMMARY_OUT="${SUMMARY_OUT:-$ROOT/data/outside_function_summary.json}"

PROJECT_DIR=$(python3 - "$PROJECT_DIR" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve())
PY
)
CSV_OUT=$(python3 -c 'import sys; from pathlib import Path; print(Path(sys.argv[1]).expanduser().resolve())' "$CSV_OUT")
SUMMARY_OUT=$(python3 -c 'import sys; from pathlib import Path; print(Path(sys.argv[1]).expanduser().resolve())' "$SUMMARY_OUT")

case "$PROJECT_DIR" in
  "$ROOT/project"|"$ROOT/project/"*)
    echo "refusing to open committed project/: $PROJECT_DIR" >&2
    exit 1
    ;;
esac
if [[ ! -d "$PROJECT_DIR/$PROJECT_NAME.rep" ]]; then
  echo "missing working project: $PROJECT_DIR/$PROJECT_NAME.rep" >&2
  exit 1
fi

# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" none
mkdir -p "$(dirname "$CSV_OUT")" "$(dirname "$SUMMARY_OUT")" "$ROOT/build"
LOG="$ROOT/build/generate-outside-function-candidates.log"

"$ROOT/tools/run_headless" \
  --project-dir "$PROJECT_DIR" \
  --project "$PROJECT_NAME" \
  --label outside-function-candidates \
  --log "$LOG" \
  --quiet \
  -- \
  -process "$PROGRAM_NAME" \
  -noanalysis \
  -readOnly \
  -postScript ExportOutsideFunctionCandidates.java "$CSV_OUT"

rg -q 'ExportOutsideFunctionCandidates: wrote ' "$LOG" || {
  echo "outside-function exporter did not report success; see $LOG" >&2
  exit 1
}

python3 "$ROOT/tools/apply_function_discovery_adjudications.py" \
  --candidates "$CSV_OUT" \
  --reviews "$ROOT/data/function_discovery_reviewed_clusters.csv" \
  --firmware "$ROOT/firmware/RH850_P1M-E_CodeFlash.bin"

python3 - "$CSV_OUT" "$SUMMARY_OUT" <<'PY'
import csv
import json
import sys
from collections import Counter
from pathlib import Path

csv_path = Path(sys.argv[1])
summary_path = Path(sys.argv[2])
with csv_path.open(newline="") as handle:
    rows = list(csv.DictReader(handle))

classes = Counter(row["candidate_class"] for row in rows)
states = Counter(row["adjudication_state"] for row in rows)
summary = {
    "schema_version": 1,
    "candidate_count": len(rows),
    "candidate_class_counts": dict(sorted(classes.items())),
    "adjudication_state_counts": dict(sorted(states.items())),
    "decoded_instruction_count": sum(int(row["decoded_instruction_count"]) for row in rows),
    "decoded_byte_count": sum(int(row["decoded_byte_count"]) for row in rows),
    "csv": csv_path.name,
}
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, sort_keys=True))
PY

echo "Wrote $CSV_OUT"
echo "Wrote $SUMMARY_OUT"
echo "Log: $LOG"
