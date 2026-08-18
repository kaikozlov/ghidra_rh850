#!/usr/bin/env bash
# Resolve the callback-free ephemeral runtime contract from an arbitrary bare
# RH850/P1M-E CodeFlash image using one disposable, unannotated Ghidra import.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

usage() {
  cat <<'EOF'
Usage: tools/resolve_ephemeral_runtime_image.sh CODEFLASH.bin [manifest.json] [variant-id]

Imports CODEFLASH.bin into a disposable Ghidra project, runs the existing
calibration-independent Gate-2 resolver plus the callback-free runtime semantic
resolver, scans the raw SecOC record table, joins image-bound RAM execution /
retention geometry, and emits a target manifest. The input image is never
modified.

A semantic match without verified image-bound RAM geometry is emitted as
"semantic-resolved-geometry-unresolved" and is NOT runtime-build-ready. This is
intentional fail-closed behavior for new Toyota EPS images.

CODEFLASH.bin must be the bare 1 MiB (0x100000) CodeFlash image.
EOF
}

if [[ $# -lt 1 || $# -gt 3 ]]; then
  usage >&2
  exit 2
fi

IMAGE=$(python3 - "$1" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]).expanduser().resolve()
if not p.is_file(): raise SystemExit(f"not a file: {p}")
print(p)
PY
)
OUT="${2:-$ROOT/build/ephemeral_runtime_target_manifest.json}"
OUT=$(python3 - "$OUT" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
)
VARIANT_ID="${3:-}"
mkdir -p "$(dirname "$OUT")"

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
WORK="$ROOT/build/ephemeral-runtime-targets/$SHORT"
PROJECT_DIR="$WORK/project"
PROJECT_NAME="ephemeral_runtime_$SHORT"
GATE="$WORK/gate-resolution.json"
SEMANTIC="$WORK/runtime-semantic.json"
LOG="$WORK/ghidra-import.log"

case "$PROJECT_DIR" in
  "$ROOT/build/ephemeral-runtime-targets/"*) rm -rf "$WORK" ;;
  *) echo "refusing unexpected resolver workspace: $PROJECT_DIR" >&2; exit 1 ;;
esac
mkdir -p "$PROJECT_DIR"

"$ROOT/tools/run_headless" \
  --with-investigate \
  --project-dir "$PROJECT_DIR" \
  --project "$PROJECT_NAME" \
  --label "ephemeral-runtime-$SHORT" \
  --log "$LOG" \
  --quiet \
  -- \
  -import "$IMAGE" \
  -processor v850e3:LE:32:default \
  -postScript ResolveSecocAcceptanceGate.java "$GATE" \
  -postScript ResolveEphemeralRuntime.java "$GATE" "$SEMANTIC" \
  -commit "Disposable ephemeral runtime semantic analysis"

if [[ ! -s "$GATE" || ! -s "$SEMANTIC" ]]; then
  echo "runtime semantic resolver did not emit results; see $LOG" >&2
  rg -n 'SECOC_GATE_RESOLVER|EPHEMERAL_RUNTIME_RESOLUTION|FAIL_CLOSED|ERROR' "$LOG" >&2 || true
  exit 1
fi

ARGS=(
  --image "$IMAGE"
  --gate "$GATE"
  --semantic "$SEMANTIC"
  --out "$OUT"
)
if [[ -n "$VARIANT_ID" ]]; then
  ARGS+=(--variant-id "$VARIANT_ID")
fi
uv run --locked python "$ROOT/tools/build_ephemeral_runtime_manifest.py" "${ARGS[@]}"
cat "$OUT"
