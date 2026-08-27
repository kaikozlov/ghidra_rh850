#!/usr/bin/env bash
# Verify two-build parity (on first promotion), generate canonical corpus, and snapshot a registered target.
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
TARGET=""; PROJECT_DIR=""; PARITY_DIR=""
usage(){ echo "Usage: tools/snapshot_target_project.sh --target TARGET --project-dir DIR [--parity-project-dir DIR]"; }
while (($#)); do case "$1" in
  --target) TARGET=${2:?missing target}; shift 2;;
  --project-dir) PROJECT_DIR=${2:?missing project dir}; shift 2;;
  --parity-project-dir) PARITY_DIR=${2:?missing parity project dir}; shift 2;;
  -h|--help) usage; exit 0;;
  *) echo "unknown argument: $1" >&2; exit 2;;
esac; done
[[ -n "$TARGET" && -n "$PROJECT_DIR" ]] || { usage >&2; exit 2; }
field(){ python3 "$ROOT/tools/analysis_target.py" "$TARGET" --field "$1"; }
[[ "$(field rebuild_profile)" == "camry_f33_v1" ]] || { echo "unsupported target profile" >&2; exit 2; }
PN=$(field project_name); PROG=$(field program_name); SNAP="$ROOT/$(field snapshot_dir)"; BASE="$ROOT/$(field inventory_baseline)"; CORPUS="$ROOT/$(field decompiler_corpus)"
canon_work(){ python3 - "$1" "$BUILD_WORK" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]).expanduser().resolve(strict=False); w=Path(sys.argv[2]).resolve(strict=False)
if p==w or w not in p.parents: raise SystemExit(f"refusing project outside build/work descendant: {p}")
print(p)
PY
}
PROJECT_DIR=$(canon_work "$PROJECT_DIR"); [[ -d "$PROJECT_DIR/$PN.rep" ]] || { echo "missing target project $PROJECT_DIR/$PN.rep" >&2; exit 1; }
if [[ -n "$PARITY_DIR" ]]; then PARITY_DIR=$(canon_work "$PARITY_DIR"); [[ -d "$PARITY_DIR/$PN.rep" ]] || { echo "missing parity target project" >&2; exit 1; }; fi
if pgrep -f "AnalyzeHeadless.*${PN}" >/dev/null 2>&1; then echo "target daemon still active" >&2; exit 1; fi
# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" full
for d in "$PROJECT_DIR" ${PARITY_DIR:+"$PARITY_DIR"}; do
  [[ -f "$d/processor_manifest.json" ]] || { echo "missing processor manifest: $d" >&2; exit 1; }
  python3 "$ROOT/tools/fingerprint_processor.py" --expect "$d/processor_manifest.json" --ghidra-version "$GHIDRA_VERSION" --cli-version "$GHIDRA_CLI_VERSION" --sla "$V850_EXT_DIR/data/languages/v850e3.sla" >/dev/null
done
TMP=$(mktemp -d "$BUILD_TMP/target-finalize.XXXXXX"); trap 'rm -rf "$TMP"' EXIT
export_inventory(){ GHIDRA_ANALYSIS_TARGET="$TARGET" PROJECT_DIR="$1" "$ROOT/tools/export_ghidra_project.sh" project-inventory "$2" >/dev/null; }
export_inventory "$PROJECT_DIR" "$TMP/a.jsonl"
if [[ -f "$BASE" ]]; then
  python3 "$ROOT/tools/project_inventory.py" compare "$BASE" "$TMP/a.jsonl"
else
  [[ -n "$PARITY_DIR" ]] || { echo "first target promotion requires --parity-project-dir" >&2; exit 1; }
  export_inventory "$PARITY_DIR" "$TMP/b.jsonl"
  cmp -s "$TMP/a.jsonl" "$TMP/b.jsonl" || { echo "independent target rebuild inventories differ" >&2; python3 "$ROOT/tools/project_inventory.py" compare "$TMP/a.jsonl" "$TMP/b.jsonl" || true; exit 1; }
  mkdir -p "$(dirname "$BASE")"; cp "$TMP/a.jsonl" "$BASE"
  echo "Initialized byte-identical two-build inventory baseline: $BASE"
fi
# Canonical corpus generation independently re-checks live inventory against BASE.
python3 "$ROOT/tools/generate_target_decompiler_corpus.py" --target "$TARGET" --project-dir "$PROJECT_DIR" --output "$CORPUS"
# Pack this verified work project under non-openable snapshot names.
PACK="$TMP/packed"; mkdir -p "$PACK"
python3 "$ROOT/tools/project_layout.py" pack --project-dir "$PROJECT_DIR" --snapshot-dir "$PACK" --project-name "$PN"
rm -rf "$SNAP"; mkdir -p "$SNAP"; rsync -a --delete "$PACK/" "$SNAP/"
python3 "$ROOT/tools/project_layout.py" validate-snapshot --snapshot-dir "$SNAP" --project-name "$PN"
git -C "$ROOT" add "$SNAP" "$BASE" "$CORPUS"
echo "Promoted first-class target snapshot: $SNAP"
echo "Promoted canonical corpus: $CORPUS"
