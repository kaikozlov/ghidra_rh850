#!/usr/bin/env bash
# Push the working project (build/project) into the committed snapshot
# (project/) and stage it for commit. This is the ONLY path that mutates the
# committed project/ directory.
#
# Why this exists: any `ghidra` daemon open of the committed project compacts
# its DB (db.N.gbf -> db.N+1) and rewrites the change buffers on clean stop,
# producing tree churn even when no analysis edit was made. So the committed
# project/ is treated as a pure snapshot that is never daemon-opened; all
# interactive work happens in the gitignored build/project/, and this script
# mirrors a finished, verified build back into the snapshot.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROJECT_DIR="$ROOT/build/project"
SNAPSHOT_DIR="$ROOT/project"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"

usage() {
  cat <<'EOF'
Usage: tools/snapshot_project.sh [options]

Options:
  --project-dir DIR    Working project to snapshot from (default: build/project)
  --snapshot-dir DIR   Committed snapshot to write (default: project)
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

[[ -d "$PROJECT_DIR/$PROJECT_NAME.rep" ]] || {
  echo "working project not found: $PROJECT_DIR" >&2
  echo "run 'make rebuild-project' (fresh build) or 'make work-project' (copy from snapshot) first" >&2
  exit 1
}
command -v ghidra >/dev/null 2>&1 || { echo "ghidra CLI is required" >&2; exit 1; }
command -v rsync >/dev/null 2>&1 || { echo "rsync is required" >&2; exit 1; }
[[ -d "$SNAPSHOT_DIR" ]] || { echo "snapshot dir does not exist: $SNAPSHOT_DIR" >&2; exit 1; }

DAEMON_RE='AnalyzeHeadless.*rh850_p1me_mapped'
if pgrep -f "$DAEMON_RE" >/dev/null 2>&1; then
  echo "an RH850 daemon is still running; stop it before snapshotting" >&2
  pgrep -af "$DAEMON_RE" >&2 || true
  exit 1
fi

# Resolve absolute paths for Ghidra (rejects dot-prefixed components).
PROJECT_DIR=$(cd "$PROJECT_DIR" && pwd)
SNAPSHOT_DIR=$(cd "$SNAPSHOT_DIR" && pwd)
CLI_ARGS=(--projects-dir "$PROJECT_DIR" --project "$PROJECT_NAME" --program "$PROGRAM_NAME")

echo "Verifying working project stats before snapshot..."
STATS_OUTPUT=$(ghidra "${CLI_ARGS[@]}" stats)
ghidra "${CLI_ARGS[@]}" stop >/dev/null 2>&1 || true
# Wait for the daemon to fully exit before touching any files.
for _ in 1 2 3 4 5; do
  pgrep -f "$DAEMON_RE" >/dev/null 2>&1 || break
  sleep 1
done
if pgrep -f "$DAEMON_RE" >/dev/null 2>&1; then
  echo "daemon did not stop cleanly; aborting snapshot" >&2
  exit 1
fi
printf '%s\n' "$STATS_OUTPUT" | python3 "$ROOT/tools/verify_ghidra_stats.py"

# Processor fingerprint must match the sources that built this working copy.
if [[ -f "$PROJECT_DIR/processor_manifest.json" ]]; then
  python3 "$ROOT/tools/fingerprint_processor.py" --expect "$PROJECT_DIR/processor_manifest.json"
else
  echo "ERROR: working project missing processor_manifest.json; rebuild first" >&2
  exit 1
fi

echo "Syncing $PROJECT_DIR -> $SNAPSHOT_DIR (committed snapshot)"
# --delete removes stale db versions from the previous snapshot. Exclude
# transient Ghidra files and any nested .git so the snapshot stays clean.
rsync -a --delete \
  --exclude '.git' \
  --exclude '*.lock' --exclude '*.lock~' \
  --exclude 'tmp*' --exclude '*~journal*' \
  "$PROJECT_DIR/" "$SNAPSHOT_DIR/"

echo "Staging $SNAPSHOT_DIR"
git -C "$ROOT" add "$SNAPSHOT_DIR/"

echo
echo "Snapshot staged. Review and commit, e.g.:"
echo "  git status --short project/"
echo "  git diff --cached --stat"
