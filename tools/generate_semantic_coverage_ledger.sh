#!/usr/bin/env bash
# Generate data/semantic_coverage_ledger.csv (+ summary JSON) from the working
# Ghidra project at build/project/. Read-only: never opens committed project/,
# never analyzes, never commits daemon state.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROJECT_DIR="${PROJECT_DIR:-$ROOT/build/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
CSV_OUT="${CSV_OUT:-$ROOT/data/semantic_coverage_ledger.csv}"
SUMMARY_OUT="${SUMMARY_OUT:-$ROOT/data/semantic_coverage_summary.json}"
SCRIPT_PATH="$ROOT/ghidra/scripts/investigate;$ROOT/ghidra/scripts/verify"

PROJECT_DIR=$(python3 - "$PROJECT_DIR" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1]).expanduser().resolve()
if any(part.startswith(".") for part in path.parts if part not in (".", "..")):
    raise SystemExit(f"Ghidra rejects dot-prefixed path components: {path}")
print(path)
PY
)
CSV_OUT=$(python3 -c 'import sys; from pathlib import Path; print(Path(sys.argv[1]).expanduser().resolve())' "$CSV_OUT")
SUMMARY_OUT=$(python3 -c 'import sys; from pathlib import Path; print(Path(sys.argv[1]).expanduser().resolve())' "$SUMMARY_OUT")

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

"$ROOT/tools/install_v850_extension.sh"
# shellcheck disable=SC1091
source "$ROOT/build/ghidra-processor.env"

ANALYZE="$GHIDRA_HOME/support/analyzeHeadless"
[[ -x "$ANALYZE" ]] || { echo "missing analyzeHeadless: $ANALYZE" >&2; exit 1; }

mkdir -p "$(dirname "$CSV_OUT")" "$(dirname "$SUMMARY_OUT")" "$ROOT/build"
LOG="$ROOT/build/generate-semantic-coverage.log"

echo "Exporting semantic coverage ledger from $PROJECT_DIR"
echo "CSV: $CSV_OUT"

set +e
"$ANALYZE" "$PROJECT_DIR" "$PROJECT_NAME" \
  -process "$PROGRAM_NAME" \
  -noanalysis \
  -readOnly \
  -scriptPath "$SCRIPT_PATH" \
  -postScript ExportSemanticCoverageLedger.java "$CSV_OUT" \
  >"$LOG" 2>&1
rc=$?
set -e

if ((rc != 0)) || rg -q 'REPORT SCRIPT ERROR|IllegalStateException' "$LOG"; then
  echo "semantic coverage export failed (rc=$rc) — see $LOG" >&2
  rg -n 'SCRIPT ERROR|IllegalStateException|ExportSemantic|ERROR' "$LOG" | tail -40 >&2 || true
  exit 1
fi
rg -q 'ExportSemanticCoverageLedger: wrote ' "$LOG" || {
  echo "exporter did not report success — see $LOG" >&2
  exit 1
}

python3 - "$CSV_OUT" "$SUMMARY_OUT" <<'PY'
import csv
import json
import sys
from collections import Counter
from pathlib import Path

csv_path = Path(sys.argv[1])
summary_path = Path(sys.argv[2])
expected = [
    "entry_addr",
    "body_bytes",
    "name",
    "name_source",
    "is_thunk",
    "calling_convention",
    "caller_count",
    "callee_count",
    "root_kind",
    "ram_ref_count",
    "mmio_ref_count",
    "codeflash_data_ref_count",
    "string_ref_count",
    "subsystem",
    "evidence_grade",
]
with csv_path.open(newline="") as fh:
    reader = csv.DictReader(fh)
    if reader.fieldnames != expected:
        raise SystemExit(f"unexpected CSV header: {reader.fieldnames}")
    rows = list(reader)

grades = Counter(r["evidence_grade"] for r in rows)
sources = Counter(r["name_source"] for r in rows)
conventions = Counter(r["calling_convention"] for r in rows)
subsystems = Counter(r["subsystem"] for r in rows if r["subsystem"])
roots = Counter(r["root_kind"] for r in rows if r["root_kind"])
summary = {
    "schema_version": 1,
    "function_count": len(rows),
    "evidence_grade_counts": dict(sorted(grades.items())),
    "name_source_counts": dict(sorted(sources.items())),
    "calling_convention_counts": dict(sorted(conventions.items())),
    "subsystem_counts": dict(sorted(subsystems.items())),
    "root_kind_counts": dict(sorted(roots.items())),
    "csv": str(csv_path.name),
}
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(f"Wrote summary ({len(rows)} functions) to {summary_path}")
for grade, count in sorted(grades.items()):
    print(f"  evidence_grade {grade}: {count}")
PY

echo "Wrote ledger: $CSV_OUT"
echo "Log: $LOG"
