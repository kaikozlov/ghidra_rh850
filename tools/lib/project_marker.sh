#!/usr/bin/env bash
# Project-affine mutation marker helpers shared by tools/g and snapshotting.

project_mutation_marker() {
  local repository_root=${1:?repository root required}
  local project_dir=${2:?project directory required}
  python3 - "$repository_root" "$project_dir" <<'PY'
from hashlib import sha256
from pathlib import Path
import os, sys

root = Path(sys.argv[1]).resolve()
project = Path(sys.argv[2]).expanduser().resolve(strict=False)
key = sha256(str(project).encode()).hexdigest()
work = Path(os.environ.get("BUILD_WORK", root / "build" / "work")).expanduser().resolve(strict=False)
print(work / "ghidra-session-dirty" / f"{key}.marker")
PY
}

write_project_mutation_marker() {
  local marker=${1:?marker path required}
  local project_dir=${2:?project directory required}
  mkdir -p "$(dirname "$marker")"
  {
    printf 'project=%s\n' "$project_dir"
    printf 'timestamp=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$marker"
}
