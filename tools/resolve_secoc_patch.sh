#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: tools/resolve_secoc_patch.sh CODEFLASH.bin [manifest.json]" >&2
  echo "The current tools/g working project must be the Ghidra import of CODEFLASH.bin." >&2
  exit 2
fi

IMAGE="$1"
OUT="${2:-build/secoc_patch_manifest.json}"
RESOLUTION="${OUT%.json}.semantic.json"
mkdir -p "$(dirname "$OUT")"

# The Java resolver scans the current Ghidra program without calibration-specific
# target addresses. It emits the program SHA-256, which the manifest builder then
# requires to equal IMAGE's SHA-256. This makes cross-calibration/project mixups
# fail closed.
tools/g script run ghidra/scripts/investigate/ResolveSecocAcceptanceGate.java -- "$RESOLUTION" >/dev/null
uv run --locked python tools/build_secoc_patch_manifest.py "$RESOLUTION" "$IMAGE" -o "$OUT"
cat "$OUT"
