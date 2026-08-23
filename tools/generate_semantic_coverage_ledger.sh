#!/usr/bin/env bash
# Generate data/semantic_coverage_ledger.csv (+ summary JSON) from the working
# Ghidra project at build/work/project/. Read-only: never opens committed project/,
# never analyzes, never commits daemon state.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
PROJECT_DIR="${PROJECT_DIR:-$BUILD_WORK/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
CSV_OUT="${CSV_OUT:-$ROOT/data/semantic_coverage_ledger.csv}"
SUMMARY_OUT="${SUMMARY_OUT:-$ROOT/data/semantic_coverage_summary.json}"

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
    echo "use build/work/project via make work-project" >&2
    exit 1
    ;;
esac

# Shared environment setup: resolve Ghidra, install processor extension,
# source env file.
# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" none

mkdir -p "$(dirname "$CSV_OUT")" "$(dirname "$SUMMARY_OUT")" "$BUILD_LOGS"
LOG="$BUILD_LOGS/generate-semantic-coverage.log"

echo "Exporting semantic coverage ledger from $PROJECT_DIR"
echo "CSV: $CSV_OUT"

"$ROOT/tools/run_headless" \
  --project-dir "$PROJECT_DIR" \
  --project "$PROJECT_NAME" \
  --label semantic-coverage \
  --log "$LOG" \
  --quiet \
  -- \
  -process "$PROGRAM_NAME" \
  -noanalysis \
  -readOnly \
  -postScript ExportSemanticCoverageLedger.java "$CSV_OUT"
rg -q 'ExportSemanticCoverageLedger: wrote ' "$LOG" || {
  echo "exporter did not report success — see $LOG" >&2
  exit 1
}

python3 "$ROOT/tools/apply_semantic_review_status.py" \
  --ledger "$CSV_OUT" \
  --reviews "$ROOT/data/semantic_review_status.csv"

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
    "discovery_source",
    "discovery_provenance",
    "name_source",
    "is_thunk",
    "calling_convention",
    "caller_count",
    "callee_count",
    "indirect_reference_count",
    "root_kind",
    "ram_ref_count",
    "ram_read_ref_count",
    "ram_write_ref_count",
    "mmio_ref_count",
    "codeflash_data_ref_count",
    "string_ref_count",
    "subsystem",
    "review_state",
    "evidence_grade",
    "verification_source",
    "oracle_class",
    "execution_status",
    "review_date",
    "review_result",
]
with csv_path.open(newline="") as fh:
    reader = csv.DictReader(fh)
    if reader.fieldnames != expected:
        raise SystemExit(f"unexpected CSV header: {reader.fieldnames}")
    rows = list(reader)

grades = Counter(r["evidence_grade"] for r in rows)
grades.pop("", None)
discovery = Counter(r["discovery_source"] for r in rows)
review_states = Counter(r["review_state"] for r in rows)
oracles = Counter(r["oracle_class"] for r in rows if r["oracle_class"])
execution = Counter(r["execution_status"] for r in rows if r["execution_status"])
sources = Counter(r["name_source"] for r in rows)
conventions = Counter(r["calling_convention"] for r in rows)
subsystems = Counter(r["subsystem"] for r in rows if r["subsystem"])
roots = Counter(r["root_kind"] for r in rows if r["root_kind"])
summary = {
    "schema_version": 2,
    "function_count": len(rows),
    "discovered_function_count": len(rows),
    "reviewed_function_count": sum(
        count for state, count in review_states.items() if state != "unreviewed"
    ),
    "bounded_semantics_count": sum(
        count for state, count in review_states.items()
        if state in {"structurally_bounded", "semantically_identified"}
    ),
    "deterministically_verified_count": sum(
        1 for row in rows
        if row["evidence_grade"] == "verified" and row["execution_status"] == "passed"
    ),
    "discovery_source_counts": dict(sorted(discovery.items())),
    "review_state_counts": dict(sorted(review_states.items())),
    "evidence_grade_counts": dict(sorted(grades.items())),
    "oracle_class_counts": dict(sorted(oracles.items())),
    "execution_status_counts": dict(sorted(execution.items())),
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
