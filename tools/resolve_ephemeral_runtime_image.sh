#!/usr/bin/env bash
# Resolve the callback-free ephemeral runtime contract from an arbitrary
# RH850/P1M-E CodeFlash image/range dump using one disposable Ghidra import.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
cd "$ROOT"

usage() {
  cat <<'EOF'
Usage: tools/resolve_ephemeral_runtime_image.sh CODEFLASH.bin [manifest.json] [variant-id]

Imports CODEFLASH.bin into a disposable Ghidra project, recovers and applies the
target's own boot/application GP+TP context, runs the existing calibration-
independent Gate-2 resolver plus the callback-free runtime semantic resolver,
scans the raw SecOC record table, joins image-bound RAM execution / retention
geometry, and emits a target manifest. The input image is never modified.

A semantic match without verified image-bound RAM geometry is emitted as
"semantic-resolved-geometry-unresolved" and is NOT runtime-build-ready. A target
whose Gate-2 queue lacks the classic 0x2E4/0x131 steering records is emitted as
"semantic-resolved-steering-unsupported". Both are intentional fail-closed
results rather than resolver errors.

CODEFLASH.bin may be either the bare 1 MiB (0x100000) CodeFlash image or a 2 MiB
range-dumper artifact whose upper 1 MiB is entirely 0xFF. The latter is
normalized to its first 1 MiB for analysis while the manifest preserves the
source artifact hash/size.
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
OUT="${2:-$BUILD_OUT/ephemeral_runtime_target_manifest.json}"
OUT=$(python3 - "$OUT" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
)
VARIANT_ID="${3:-}"
mkdir -p "$(dirname "$OUT")"

mapfile -t IMAGE_INFO < <(uv run --locked python - "$IMAGE" <<'PY'
from pathlib import Path
import sys
from tools.build_ephemeral_runtime_manifest import load_codeflash, sha256
try:
    image, source = load_codeflash(Path(sys.argv[1]))
except Exception as exc:
    print(f"rejecting image: {exc}", file=sys.stderr)
    raise SystemExit(1)
print(sha256(image))
print(source["normalization"])
PY
)
SHA=${IMAGE_INFO[0]}
NORMALIZATION=${IMAGE_INFO[1]}
SHORT=${SHA:0:16}
WORK="$BUILD_WORK/ephemeral-runtime-targets/$SHORT"
PROJECT_DIR="$WORK/project"
PROJECT_NAME="ephemeral_runtime_$SHORT"
GATE="$WORK/gate-resolution.json"
SEMANTIC="$WORK/runtime-semantic.json"
LOG="$WORK/ghidra-import.log"

case "$PROJECT_DIR" in
  "$BUILD_WORK/ephemeral-runtime-targets/"*) rm -rf "$WORK" ;;
  *) echo "refusing unexpected resolver workspace: $PROJECT_DIR" >&2; exit 1 ;;
esac
mkdir -p "$PROJECT_DIR"

IMPORT_IMAGE="$IMAGE"
if [[ "$NORMALIZATION" != "bare-codeflash" ]]; then
  IMPORT_IMAGE="$WORK/normalized-CodeFlash.bin"
  uv run --locked python - "$IMAGE" "$IMPORT_IMAGE" <<'PY'
from pathlib import Path
import sys
from tools.build_ephemeral_runtime_manifest import load_codeflash
image, _ = load_codeflash(Path(sys.argv[1]))
Path(sys.argv[2]).write_bytes(image)
PY
fi

"$ROOT/tools/run_headless" \
  --with-investigate \
  --project-dir "$PROJECT_DIR" \
  --project "$PROJECT_NAME" \
  --label "ephemeral-runtime-$SHORT" \
  --log "$LOG" \
  --quiet \
  -- \
  -import "$IMPORT_IMAGE" \
  -processor v850e3:LE:32:default \
  -postScript ApplyRecoveredGpTpContext.java \
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
