#!/usr/bin/env bash
# Resolve a SecOC authenticated-delivery patch from an arbitrary RH850/P1M-E
# CodeFlash image using a disposable, unannotated Ghidra project.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
cd "$ROOT"

usage() {
  cat <<'EOF'
Usage: tools/resolve_secoc_patch_image.sh CODEFLASH.bin [manifest.json]

Imports CODEFLASH.bin into a disposable Ghidra project under build/work/secoc-targets,
runs the calibration-independent semantic gate resolver, verifies the resolver
SHA-256 against the exact input image, discovers boot-CRC geometry, and emits a
patch manifest. The input image is never modified.

CODEFLASH.bin must be exactly the bare 1 MiB (0x100000) CodeFlash image. A
0x108000 DataFlash+CodeFlash concatenated dump, a truncated image, or an
oversized image is rejected before import with an explicit diagnosis.

This is the RH850/P1M-E backend. Zero/multiple semantic candidates or ambiguous
CRC geometry fail closed.
EOF
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage >&2
  exit 2
fi

IMAGE=$(python3 - "$1" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1]).expanduser().resolve()
if not p.is_file():
    raise SystemExit(f"not a file: {p}")
print(p)
PY
)
OUT="${2:-$BUILD_OUT/secoc_patch_manifest.json}"
OUT=$(python3 - "$OUT" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
)
mkdir -p "$(dirname "$OUT")"

# Fail-closed geometry gate BEFORE the disposable Ghidra import. The resolver is
# defined only for a bare 1 MiB CodeFlash image; a DataFlash+CodeFlash
# concatenation (0x108000) or a truncated/oversized image must be rejected with
# an explicit diagnosis instead of burning an analysis pass or mis-resolving.
uv run --locked python -c '
import sys
from pathlib import Path

from tools.build_secoc_patch_manifest import validate_codeflash_geometry

try:
    validate_codeflash_geometry(Path(sys.argv[1]).stat().st_size)
except ValueError as exc:
    print(f"rejecting image: {exc}", file=sys.stderr)
    raise SystemExit(1)
' "$IMAGE"

SHA=$(shasum -a 256 "$IMAGE" | awk '{print $1}')
SHORT=${SHA:0:16}
WORK="$BUILD_WORK/secoc-targets/$SHORT"
PROJECT_DIR="$WORK/project"
PROJECT_NAME="secoc_target_$SHORT"
RESOLUTION="$WORK/semantic-resolution.json"
LOG="$WORK/ghidra-import.log"

# Always rebuild the disposable import so resolver behavior follows the current
# processor module/script rather than a stale cached analysis database.
case "$PROJECT_DIR" in
  "$BUILD_WORK/secoc-targets/"*) rm -rf "$WORK" ;;
  *) echo "refusing unexpected resolver workspace: $PROJECT_DIR" >&2; exit 1 ;;
esac
mkdir -p "$PROJECT_DIR"

"$ROOT/tools/run_headless" \
  --with-investigate \
  --project-dir "$PROJECT_DIR" \
  --project "$PROJECT_NAME" \
  --label "secoc-target-$SHORT" \
  --log "$LOG" \
  --quiet \
  -- \
  -import "$IMAGE" \
  -processor v850e3:LE:32:default \
  -postScript SeedSecocAcceptanceGateCandidates.java \
  -postScript ResolveSecocAcceptanceGate.java "$RESOLUTION" \
  -commit "Disposable SecOC semantic target analysis"

if [[ ! -s "$RESOLUTION" ]]; then
  echo "semantic resolver did not emit a unique result; see $LOG" >&2
  rg -n 'SECOC_GATE_RESOLVER|FAIL_CLOSED|ERROR' "$LOG" >&2 || true
  exit 1
fi

uv run --locked python "$ROOT/tools/build_secoc_patch_manifest.py" \
  "$RESOLUTION" "$IMAGE" -o "$OUT"

cat "$OUT"
