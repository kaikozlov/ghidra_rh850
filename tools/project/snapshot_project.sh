#!/usr/bin/env bash
# Push the legacy Sienna working project into its committed packed snapshot
# under projects/sienna-8965B4512000/ and stage it for commit.
#
# Why this exists: any `ghidra` daemon open of the committed project compacts
# its DB (db.N.gbf -> db.N+1) and rewrites the change buffers on clean stop,
# producing tree churn even when no analysis edit was made. The committed
# projects/ namespace is therefore snapshot-only; interactive work stays under build/work/.
# mirrors a finished, verified build back into the snapshot.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
TARGET="sienna-8965B4512000"
field(){ python3 "$ROOT/tools/project/analysis_target.py" "$TARGET" --field "$1"; }
PROJECT_DIR="$ROOT/$(field work_dir)"
REGISTERED_SNAPSHOT_DIR="$ROOT/$(field snapshot_dir)"
SNAPSHOT_DIR="$REGISTERED_SNAPSHOT_DIR"
PROJECT_NAME=$(field project_name)
PROGRAM_NAME=$(field program_name)

usage() {
  cat <<'EOF'
Usage: tools/project/snapshot_project.sh [options]

Options:
  --project-dir DIR    Working project to snapshot from (default: registered Sienna work_dir)
  --snapshot-dir DIR   Committed Sienna snapshot to write; must match the registered snapshot_dir
  -h, --help           Show this help
EOF
}

while (($#)); do
  case "$1" in
    --project-dir)  PROJECT_DIR=${2:?missing argument for --project-dir};  shift 2 ;;
    --snapshot-dir) SNAPSHOT_DIR=${2:?missing argument for --snapshot-dir}; shift 2 ;;
    -h|--help)      usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ ! -L "$ROOT/projects" ]] || {
  echo "REFUSING: committed projects root must not be a symlink: $ROOT/projects" >&2
  exit 2
}
[[ ! -L "$SNAPSHOT_DIR" ]] || {
  echo "REFUSING: committed snapshot must not be a symlink: $SNAPSHOT_DIR" >&2
  exit 2
}

EXPECTED_SNAPSHOT_DIR=$(python3 - "$REGISTERED_SNAPSHOT_DIR" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).resolve(strict=False))
PY
)
SNAPSHOT_DIR=$(python3 - "$SNAPSHOT_DIR" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).resolve(strict=False))
PY
)
if [[ "$SNAPSHOT_DIR" != "$EXPECTED_SNAPSHOT_DIR" ]]; then
  echo "REFUSING: snapshot destination must be the committed repository snapshot: $EXPECTED_SNAPSHOT_DIR" >&2
  exit 2
fi

[[ -d "$PROJECT_DIR/$PROJECT_NAME.rep" ]] || {
  echo "working project not found: $PROJECT_DIR" >&2
  echo "run 'make rebuild-project' (fresh build) or 'make work-project' (copy from snapshot) first" >&2
  exit 1
}
command -v cargo >/dev/null 2>&1 || { echo "cargo is required (to build vendored ghidra-cli)" >&2; exit 1; }
if [[ ! -x "$BUILD_CACHE/ghidra-cli/ghidra" ]]; then
  "$ROOT/tools/project/build_ghidra_cli.sh"
fi
GHIDRA_CLI="$BUILD_CACHE/ghidra-cli/ghidra"
command -v rsync >/dev/null 2>&1 || { echo "rsync is required" >&2; exit 1; }
[[ -d "$SNAPSHOT_DIR" ]] || { echo "snapshot dir does not exist: $SNAPSHOT_DIR" >&2; exit 1; }

# Shared environment setup: resolve Ghidra, install processor extension,
# source env file, validate fingerprint. This replaces the old manual
# install + source dance.
# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" full

PROJECT_DIR=$(python3 - "$PROJECT_DIR" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
)
DAEMON_RE="AnalyzeHeadless.*${PROJECT_DIR}.*${PROJECT_NAME}"
if pgrep -f "$DAEMON_RE" >/dev/null 2>&1; then
  echo "an RH850 daemon is still running; stop it before snapshotting" >&2
  pgrep -af "$DAEMON_RE" >&2 || true
  exit 1
fi

# Resolve absolute paths for Ghidra (rejects dot-prefixed components).
SNAPSHOT_DIR=$(cd "$SNAPSHOT_DIR" && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/project_marker.sh"
MUTATION_MARKER=$(project_mutation_marker "$ROOT" "$PROJECT_DIR")
CLI_ARGS=(--projects-dir "$PROJECT_DIR" --project "$PROJECT_NAME" --program "$PROGRAM_NAME")

STOP_REQUIRED=0
stop_cli_daemon() {
  ((STOP_REQUIRED)) || return 0
  "$GHIDRA_CLI" "${CLI_ARGS[@]}" stop >/dev/null 2>&1 || true
  for _ in 1 2 3 4 5; do
    pgrep -f "$DAEMON_RE" >/dev/null 2>&1 || break
    sleep 1
  done
  if pgrep -f "$DAEMON_RE" >/dev/null 2>&1; then
    echo "daemon did not stop cleanly; aborting snapshot" >&2
    return 1
  fi
  STOP_REQUIRED=0
}

echo "Verifying working project stats before snapshot..."
trap stop_cli_daemon EXIT
STOP_REQUIRED=1
STATS_OUTPUT=$("$GHIDRA_CLI" "${CLI_ARGS[@]}" stats)
stop_cli_daemon
trap - EXIT
printf '%s\n' "$STATS_OUTPUT" | python3 "$ROOT/tools/testing/processor/verify_ghidra_stats.py"

# Processor fingerprint must match the sources that built this working copy.
if [[ -f "$PROJECT_DIR/processor_manifest.json" ]]; then
  python3 "$ROOT/tools/project/fingerprint_processor.py" \
    --expect "$PROJECT_DIR/processor_manifest.json" \
    --ghidra-version "$GHIDRA_VERSION" \
    --cli-version "$GHIDRA_CLI_VERSION" \
    --sla "$V850_EXT_DIR/data/languages/v850e3.sla"
else
  echo "ERROR: working project missing processor_manifest.json; rebuild first" >&2
  exit 1
fi

echo "Verifying exact normalized project parity before snapshot..."
GHIDRA_ANALYSIS_TARGET="$TARGET" PROJECT_DIR="$PROJECT_DIR" \
  "$ROOT/tools/project/export_ghidra_project.sh" project-inventory "$BUILD_OUT/ghidra_project_inventory.snapshot.jsonl"
python3 "$ROOT/tools/project/project_inventory.py" compare \
  "$ROOT/data/ghidra_project_inventory.baseline.jsonl" \
  "$BUILD_OUT/ghidra_project_inventory.snapshot.jsonl"

PACKED_DIR=$(mktemp -d "$BUILD_WORK/project-snapshot-pack.XXXXXX")
cleanup_packed() { rm -rf "$PACKED_DIR"; }
trap cleanup_packed EXIT

echo "Packing live project under non-openable snapshot names..."
python3 "$ROOT/tools/project/project_layout.py" pack \
  --project-dir "$PROJECT_DIR" \
  --snapshot-dir "$PACKED_DIR" \
  --project-name "$PROJECT_NAME"

echo "Syncing packed snapshot -> $SNAPSHOT_DIR (committed snapshot)"
# --delete removes stale DB versions and the former live .gpr/.rep names.
rsync -a --delete "$PACKED_DIR/" "$SNAPSHOT_DIR/"
python3 "$ROOT/tools/project/project_layout.py" validate-snapshot \
  --snapshot-dir "$SNAPSHOT_DIR" \
  --project-name "$PROJECT_NAME"

echo "Staging $SNAPSHOT_DIR"
git -C "$ROOT" add "$SNAPSHOT_DIR/"

# Clear only this working project's mutation marker. Markers for other
# disposable projects must survive an unrelated promotion.
rm -f "$MUTATION_MARKER"
trap - EXIT
cleanup_packed

echo
echo "Snapshot staged. Review and commit, e.g.:"
echo "  git status --short $SNAPSHOT_DIR"
echo "  git diff --cached --stat"
