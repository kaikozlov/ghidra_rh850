#!/usr/bin/env bash
# Export deterministic artifacts from the disposable working Ghidra project.
#
# This is the shared profile runner for read-only project exports.  The hard
# project-path/environment/headless safety policy lives in tools/run_headless;
# this file owns only artifact profiles and their deterministic postprocessing.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

usage() {
  cat <<'EOF'
Usage: tools/export_ghidra_project.sh list
       tools/export_ghidra_project.sh PROFILE [OUTPUT [SUMMARY_OUTPUT]]

Profiles:
  application-rx-signals       Export application Rx signal evidence CSV
  application-rx-consumers     Export application Rx consumer audit CSV
  application-tx-producers     Export Tx refs and build producer evidence CSV
  outside-functions            Export/adjudicate outside-function census + summary
  semantic-coverage            Export/review semantic coverage ledger + summary
  project-inventory            Export normalized project inventory (build/out or build/tmp only)

PROJECT_DIR defaults to build/work/project. Profile-specific environment
variables (MAP, CSV_OUT, SUMMARY_OUT) remain supported where they existed.
EOF
}

PROFILE=${1:-}
case "$PROFILE" in
  -h|--help|"") usage; exit 0 ;;
  list)
    printf '%s\n' \
      application-rx-signals \
      application-rx-consumers \
      application-tx-producers \
      outside-functions \
      semantic-coverage \
      project-inventory
    exit 0
    ;;
esac
shift

# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
mkdir -p "$BUILD_CACHE" "$BUILD_WORK" "$BUILD_OUT" "$BUILD_LOGS" "$BUILD_TMP"
PROJECT_DIR="${PROJECT_DIR:-$BUILD_WORK/project}"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"

resolve_path() {
  python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$1"
}

# Compare canonical paths to canonical paths. BUILD_ROOT may itself be reached
# through a symlink (for example macOS /tmp -> /private/tmp), while output paths
# are always resolved below.
BUILD_OUT_CANON=$(resolve_path "$BUILD_OUT")
BUILD_TMP_CANON=$(resolve_path "$BUILD_TMP")
PROJECT_DIR=$(resolve_path "$PROJECT_DIR")
if [[ ! -d "$PROJECT_DIR/$PROJECT_NAME.rep" ]]; then
  cat >&2 <<EOF
missing working project: $PROJECT_DIR/$PROJECT_NAME.rep
materialize it first with 'make work-project' or 'make rebuild-project'
EOF
  exit 1
fi

LABEL=""
LOG_NAME=""
SUCCESS_MARKER=""
POST_SCRIPT=""
POST_ARGS=()
PRIMARY_OUT=""
SECONDARY_OUT=""

case "$PROFILE" in
  application-rx-signals)
    (($# <= 1)) || { usage >&2; exit 2; }
    PRIMARY_OUT=$(resolve_path "${1:-$ROOT/data/application_rx_signal_evidence.csv}")
    LABEL="application-rx-signal-evidence"
    LOG_NAME="generate-application-rx-signal-evidence.log"
    SUCCESS_MARKER="ExportApplicationRxSignalEvidence: wrote"
    POST_SCRIPT="ExportApplicationRxSignalEvidence.java"
    POST_ARGS=("$PRIMARY_OUT")
    ;;
  application-rx-consumers)
    (($# <= 1)) || { usage >&2; exit 2; }
    PRIMARY_OUT=$(resolve_path "${1:-$ROOT/data/application_rx_consumer_audit.csv}")
    MAP=$(resolve_path "${MAP:-$ROOT/data/application_rx_map.csv}")
    LABEL="application-rx-consumer-audit"
    LOG_NAME="generate-application-rx-consumer-audit.log"
    SUCCESS_MARKER="ExportApplicationRxConsumerAudit: rows="
    POST_SCRIPT="ExportApplicationRxConsumerAudit.java"
    POST_ARGS=("$MAP" "$PRIMARY_OUT")
    ;;
  application-tx-producers)
    (($# <= 1)) || { usage >&2; exit 2; }
    PRIMARY_OUT=$(resolve_path "${1:-$ROOT/data/application_tx_producer_evidence.csv}")
    RAW_REFS="$BUILD_OUT/application_tx_producer_refs.csv"
    LABEL="application-tx-producer-evidence"
    LOG_NAME="generate-application-tx-producer-evidence.log"
    SUCCESS_MARKER="ExportApplicationTxProducerRefs: sources="
    POST_SCRIPT="ExportApplicationTxProducerRefs.java"
    POST_ARGS=("$RAW_REFS")
    ;;
  outside-functions)
    (($# <= 2)) || { usage >&2; exit 2; }
    PRIMARY_OUT=$(resolve_path "${1:-${CSV_OUT:-$ROOT/data/outside_function_candidates.csv}}")
    SECONDARY_OUT=$(resolve_path "${2:-${SUMMARY_OUT:-$ROOT/data/outside_function_summary.json}}")
    LABEL="outside-function-candidates"
    LOG_NAME="generate-outside-function-candidates.log"
    SUCCESS_MARKER="ExportOutsideFunctionCandidates: wrote "
    POST_SCRIPT="ExportOutsideFunctionCandidates.java"
    POST_ARGS=("$PRIMARY_OUT")
    ;;
  semantic-coverage)
    (($# <= 2)) || { usage >&2; exit 2; }
    PRIMARY_OUT=$(resolve_path "${1:-${CSV_OUT:-$ROOT/data/semantic_coverage_ledger.csv}}")
    SECONDARY_OUT=$(resolve_path "${2:-${SUMMARY_OUT:-$ROOT/data/semantic_coverage_summary.json}}")
    LABEL="semantic-coverage"
    LOG_NAME="generate-semantic-coverage.log"
    SUCCESS_MARKER="ExportSemanticCoverageLedger: wrote "
    POST_SCRIPT="ExportSemanticCoverageLedger.java"
    POST_ARGS=("$PRIMARY_OUT")
    ;;
  project-inventory)
    (($# <= 1)) || { usage >&2; exit 2; }
    PRIMARY_OUT=$(resolve_path "${1:-$BUILD_OUT/ghidra_project_inventory.jsonl}")
    case "$PRIMARY_OUT" in
      "$BUILD_OUT_CANON/"*|"$BUILD_TMP_CANON/"*) ;;
      *)
        echo "refusing inventory output outside $BUILD_OUT_CANON or $BUILD_TMP_CANON: $PRIMARY_OUT" >&2
        exit 1
        ;;
    esac
    # ExportProjectInventory opens the destination with a truncating writer, so
    # no pre-delete is needed. Keeping an existing artifact intact until the
    # headless safety gate succeeds makes failed/unsafe invocations non-destructive.
    LABEL="project-inventory"
    LOG_NAME="generate-project-inventory.log"
    SUCCESS_MARKER="ExportProjectInventory: wrote "
    POST_SCRIPT="ExportProjectInventory.java"
    POST_ARGS=("$PRIMARY_OUT")
    ;;
  *)
    echo "unknown export profile: $PROFILE" >&2
    usage >&2
    exit 2
    ;;
esac

mkdir -p "$(dirname "$PRIMARY_OUT")" "$BUILD_LOGS"
[[ -z "$SECONDARY_OUT" ]] || mkdir -p "$(dirname "$SECONDARY_OUT")"
LOG="$BUILD_LOGS/$LOG_NAME"

"$ROOT/tools/run_headless" \
  --project-dir "$PROJECT_DIR" \
  --project "$PROJECT_NAME" \
  --label "$LABEL" \
  --log "$LOG" \
  --quiet \
  -- \
  -process "$PROGRAM_NAME" \
  -noanalysis \
  -readOnly \
  -postScript "$POST_SCRIPT" "${POST_ARGS[@]}"

grep -Fq "$SUCCESS_MARKER" "$LOG" || {
  echo "$PROFILE exporter did not report success — see $LOG" >&2
  exit 1
}

case "$PROFILE" in
  application-tx-producers)
    uv run --locked python "$ROOT/tools/generate_application_tx_producer_evidence.py" \
      --refs "$RAW_REFS" \
      --output "$PRIMARY_OUT"
    ;;
  outside-functions)
    python3 "$ROOT/tools/apply_function_discovery_adjudications.py" \
      --candidates "$PRIMARY_OUT" \
      --reviews "$ROOT/data/function_discovery_reviewed_clusters.csv" \
      --firmware "$ROOT/firmware/RH850_P1M-E_CodeFlash.bin"
    python3 - "$PRIMARY_OUT" "$SECONDARY_OUT" <<'PY'
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
    ;;
  semantic-coverage)
    python3 "$ROOT/tools/apply_semantic_review_status.py" \
      --ledger "$PRIMARY_OUT" \
      --reviews "$ROOT/data/semantic_review_status.csv"
    python3 - "$PRIMARY_OUT" "$SECONDARY_OUT" <<'PY'
import csv
import json
import sys
from collections import Counter
from pathlib import Path

csv_path = Path(sys.argv[1])
summary_path = Path(sys.argv[2])
expected = [
    "entry_addr", "body_bytes", "name", "discovery_source", "discovery_provenance",
    "name_source", "is_thunk", "calling_convention", "caller_count", "callee_count",
    "indirect_reference_count", "root_kind", "ram_ref_count", "ram_read_ref_count",
    "ram_write_ref_count", "mmio_ref_count", "codeflash_data_ref_count", "string_ref_count",
    "subsystem", "review_state", "evidence_grade", "verification_source", "oracle_class",
    "execution_status", "review_date", "review_result",
]
with csv_path.open(newline="") as fh:
    reader = csv.DictReader(fh)
    if reader.fieldnames != expected:
        raise SystemExit(f"unexpected CSV header: {reader.fieldnames}")
    rows = list(reader)
grades = Counter(r["evidence_grade"] for r in rows); grades.pop("", None)
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
    "reviewed_function_count": sum(count for state, count in review_states.items() if state != "unreviewed"),
    "bounded_semantics_count": sum(count for state, count in review_states.items() if state in {"structurally_bounded", "semantically_identified"}),
    "deterministically_verified_count": sum(1 for row in rows if row["evidence_grade"] == "verified" and row["execution_status"] == "passed"),
    "discovery_source_counts": dict(sorted(discovery.items())),
    "review_state_counts": dict(sorted(review_states.items())),
    "evidence_grade_counts": dict(sorted(grades.items())),
    "oracle_class_counts": dict(sorted(oracles.items())),
    "execution_status_counts": dict(sorted(execution.items())),
    "name_source_counts": dict(sorted(sources.items())),
    "calling_convention_counts": dict(sorted(conventions.items())),
    "subsystem_counts": dict(sorted(subsystems.items())),
    "root_kind_counts": dict(sorted(roots.items())),
    "csv": csv_path.name,
}
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(f"Wrote summary ({len(rows)} functions) to {summary_path}")
for grade, count in sorted(grades.items()):
    print(f"  evidence_grade {grade}: {count}")
PY
    ;;
  project-inventory)
    python3 "$ROOT/tools/project_inventory.py" validate "$PRIMARY_OUT"
    ;;
esac

echo "Wrote: $PRIMARY_OUT"
[[ -z "$SECONDARY_OUT" ]] || echo "Wrote: $SECONDARY_OUT"
echo "Log: $LOG"
