#!/usr/bin/env bash
#
# tools/finalize_project.sh — orchestrate the full "end of session" lifecycle.
#
# This is the deliberate promotion path: it stops the interactive daemon cleanly,
# waits for it to exit, runs working-project verification, invokes the existing
# snapshot path, and prints the staged project diff summary.
#
# It does NOT run automatically on `tools/g stop`. The distinction:
#   tools/g stop             persist working-copy edits only
#   make finalize-project    verify and deliberately promote the working copy
#
# Usage: tools/finalize_project.sh [--dry-run]
#
# Exit codes:
#   0  finalization succeeded
#   1  operational error (daemon won't stop, verification fails, etc.)
set -euo pipefail

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi
if (($#)); then
  echo "usage: $0 [--dry-run]" >&2
  exit 1
fi

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROJECT_DIR="${PROJECT_DIR:-$ROOT/build/project}"
SNAPSHOT_DIR="$ROOT/project"
PROJECT_NAME="rh850_p1me_mapped"
PROGRAM_NAME="RH850_P1M-E_CodeFlash.bin"
DAEMON_RE='AnalyzeHeadless.*rh850_p1me_mapped'

PROJECT_DIR=$(python3 - "$PROJECT_DIR" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
)

echo "=== finalize-project: lifecycle orchestration ==="
echo

if ((DRY_RUN)); then
  echo "Dry run: explicit promotion would stop the project daemon, verify exact parity, and snapshot:"
  echo "  $PROJECT_DIR"
  echo "No daemon, project, or Git state was changed."
  exit 0
fi

# --- Step 1: Stop the interactive daemon --------------------------------------

daemon_pids=$(pgrep -f "$DAEMON_RE" || true)
if [[ -n "$daemon_pids" ]]; then
  echo "==> [1/5] Stopping interactive daemon..."
  GHIDRA_PROJECT="$PROJECT_DIR" "$ROOT/tools/g" stop || true
else
  echo "==> [1/5] No daemon running."
fi

# --- Step 2: Wait for the daemon to fully exit --------------------------------

echo "==> [2/5] Waiting for daemon exit..."
max_wait=15
waited=0
while ((waited < max_wait)); do
  any_alive=0
  for pid in $daemon_pids; do
    if kill -0 "$pid" 2>/dev/null; then
      any_alive=1
      break
    fi
  done
  if ((any_alive == 0)); then
    break
  fi
  sleep 1
  waited=$((waited + 1))
done

for pid in $daemon_pids; do
  if kill -0 "$pid" 2>/dev/null; then
    echo "ERROR: daemon PID $pid did not exit after ${max_wait}s" >&2
    ps -p "$pid" -o pid=,command= >&2 || true
    exit 1
  fi
done
if [[ -n "$daemon_pids" ]]; then
  echo "    Daemon exited cleanly after stop."
else
  echo "    No daemon needed stopping."
fi

# --- Step 3: Verify the working project ---------------------------------------

echo "==> [3/5] Verifying working project..."
if [[ ! -d "$PROJECT_DIR/$PROJECT_NAME.rep" ]]; then
  echo "ERROR: working project not found: $PROJECT_DIR" >&2
  exit 1
fi
echo "    Working project present."

# --- Step 4: Snapshot (the existing promotion path) ---------------------------

echo "==> [4/5] Promoting working project -> committed snapshot..."
echo "    (floors + fingerprint + exact inventory + snapshot packing + stage)"
"$ROOT/tools/snapshot_project.sh" \
  --project-dir "$PROJECT_DIR" \
  --snapshot-dir "$SNAPSHOT_DIR"

# --- Step 5: Print staged diff summary ----------------------------------------

echo "==> [5/5] Staged project diff summary:"
echo
git -C "$ROOT" diff --cached --stat -- "$SNAPSHOT_DIR/"
echo

staged_count=$(git -C "$ROOT" diff --cached --name-only -- "$SNAPSHOT_DIR/" | wc -l | tr -d ' ')
echo "$staged_count file(s) staged in $SNAPSHOT_DIR/"
echo
echo "Finalization complete. Review and commit:"
echo "  git status --short project/"
echo "  git diff --cached --stat"
echo
echo "If this was wrong, unstage with:"
echo "  git restore --staged project/"
