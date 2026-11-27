#!/usr/bin/env bash
# Measure two auto-analysis options using four disposable Camry projects.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
TARGET=camry-8965F3307000
OUTPUT_ROOT=${1:-}
if [[ -z "$OUTPUT_ROOT" ]]; then
  echo "Usage: tools/project/measure_analyzer_choices.sh NEW_BUILD_WORK_DIRECTORY" >&2
  exit 2
fi
OUTPUT_ROOT=$(uv run --locked python - "$OUTPUT_ROOT" "$ROOT/build/work" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1]).expanduser().resolve(strict=False)
work = Path(sys.argv[2]).resolve()
if path == work or work not in path.parents:
    raise SystemExit(f"output must be a new directory below {work}: {path}")
if path.exists():
    raise SystemExit(f"output already exists: {path}")
print(path)
PY
)
mkdir -p "$OUTPUT_ROOT"

field() {
  uv run --locked python -m tools.project.analysis_target "$TARGET" --field "$1"
}
PROJECT_NAME=$(field project_name)
PROGRAM_NAME=$(field program_name)
CODEFLASH="$ROOT/$(field codeflash)"
DATAFLASH="$ROOT/$(field dataflash)"
PROCESSOR=$(field processor)
SEEDS="$ROOT/$(field function_seeds)"
DECOMP_ROOT="$ROOT/$(field decomp_root)"
DEVICE_PROFILE_SCRIPT=$(field device_profile_script)
ENTRY_SEED_SCRIPT=$(field entry_seed_script)
DIAGNOSTIC_SEED_SCRIPT=$(field diagnostic_seed_script)
RECOVERED_SEED_SCRIPT=$(field recovered_seed_script)

[[ "$(shasum -a 256 "$CODEFLASH" | cut -d' ' -f1)" == "$(field codeflash_sha256)" ]] || {
  echo "CodeFlash identity drift" >&2; exit 1;
}
[[ "$(shasum -a 256 "$DATAFLASH" | cut -d' ' -f1)" == "$(field dataflash_sha256)" ]] || {
  echo "DataFlash identity drift" >&2; exit 1;
}

# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_env.sh" full
"$ROOT/tools/project/install_findcrypt_extension.sh" >/dev/null

run_mode() {
  local mode=$1 address_tables=$2 no_return=$3
  local mode_root="$OUTPUT_ROOT/$mode"
  local project_dir="$mode_root/project"
  local logs="$mode_root/logs"
  local source_root="$DECOMP_ROOT"
  local started ended missing_curated
  local import_config=()
  local analysis_config=()
  if [[ "$address_tables" != unchanged || "$no_return" != unchanged ]]; then
    import_config=(-postScript MeasureAnalyzerChoices.java configure "$address_tables" "$no_return")
    analysis_config=(-preScript MeasureAnalyzerChoices.java configure "$address_tables" "$no_return")
  fi
  mkdir -p "$project_dir" "$logs"
  cat > "$project_dir/.gitignore" <<'EOF'
*.lock
*.lock~
**/tmp*
**/~journal*
EOF
  runh() {
    local stage=$1; shift
    "$ROOT/tools/project/run_headless" \
      --project-dir "$project_dir" --project "$PROJECT_NAME" \
      --label "analyzer-choice-$mode-$stage" --log "$logs/$stage.log" --quiet -- "$@"
  }

  started=$(date +%s)
  echo "[$mode 1/4] import registered Camry images and target-native context"
  runh import -import "$CODEFLASH" -processor "$PROCESSOR" -noanalysis \
    -postScript AddDataFlash.java "$DATAFLASH" "$(field dataflash_base)" \
      "$(printf '0x%X' "$(field dataflash_size)")" \
    -postScript ApplyP1MDeviceProfile.java "$ROOT/data/p1m_sfr_labels.csv" \
    -postScript ApplyP1MSfrTypes.java \
    -postScript "$DEVICE_PROFILE_SCRIPT" \
    "${import_config[@]}" \
    -commit "Import Camry analyzer-choice measurement"

  echo "[$mode 2/4] seed registered application roots and analyze"
  runh entries -process "$PROGRAM_NAME" \
    "${analysis_config[@]}" \
    -preScript "$ENTRY_SEED_SCRIPT" \
    -commit "Analyzer-choice application roots"

  echo "[$mode 3/4] seed registered diagnostic callbacks and analyze"
  runh diagnostics -process "$PROGRAM_NAME" \
    "${analysis_config[@]}" \
    -preScript "$DIAGNOSTIC_SEED_SCRIPT" \
    -commit "Analyzer-choice diagnostic callbacks"

  # Replay curated annotations only for discovered or explicitly seeded functions.
  runh discovered -process "$PROGRAM_NAME" -noanalysis -readOnly \
    -postScript MeasureAnalyzerChoices.java export-functions "$mode_root/discovered.txt"
  if [[ "$mode" != default ]]; then
    source_root="$mode_root/decomp-filtered"
    mkdir -p "$source_root"
    uv run --locked python - "$DECOMP_ROOT" "$source_root" "$mode_root/discovered.txt" \
        "$SEEDS" "$mode_root/missing-curated.txt" <<'PY'
import csv
import json
import shutil
import sys
from pathlib import Path
source, output, discovered_path, seed_path, missing_path = map(Path, sys.argv[1:])
discovered = {int(line) for line in discovered_path.read_text().splitlines()}
with seed_path.open() as stream:
    seeded = {int(row["address"], 0) for row in csv.DictReader(stream)}
rows = [json.loads(line) for line in (source / "symbols.jsonl").read_text().splitlines()]
allowed = discovered | seeded | {int(row["addr"], 0) for row in rows if int(row["addr"], 0) > 0xfffff}
kept = [row for row in rows if int(row["addr"], 0) in allowed]
(output / "symbols.jsonl").write_text(
    "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in kept)
)
shutil.copy2(source / "data.jsonl", output / "data.jsonl")
shutil.copy2(source / "struct_layouts.json", output / "struct_layouts.json")
missing = sorted(set(int(row["addr"], 0) for row in rows) - allowed)
missing_path.write_text("".join(f"0x{entry:x}\n" for entry in missing))
PY
  else
    : > "$mode_root/missing-curated.txt"
  fi
  missing_curated=$(wc -l < "$mode_root/missing-curated.txt" | tr -d ' ')

  echo "[$mode 4/4] seed promoted recovered functions and analyze"
  runh recovered -process "$PROGRAM_NAME" \
    "${analysis_config[@]}" \
    -preScript "$RECOVERED_SEED_SCRIPT" "$SEEDS" "$source_root" \
    -commit "Analyzer-choice recovered functions"

  echo "[$mode 4b] finalize structural repairs and calling conventions"
  runh conventions -process "$PROGRAM_NAME" -noanalysis \
    -postScript "$RECOVERED_SEED_SCRIPT" "$SEEDS" "$source_root" \
    -postScript ApplyCallingConventions.java \
    -commit "Analyzer-choice calling conventions"

  runh measure -process "$PROGRAM_NAME" -noanalysis -readOnly \
    -postScript MeasureAnalyzerChoices.java measure "$mode" "$mode_root/raw.json"
  "$ROOT/tools/project/run_headless" --with-investigate \
    --project-dir "$project_dir" --project "$PROJECT_NAME" \
    --label "analyzer-choice-$mode-switches" --log "$logs/switches.log" --quiet -- \
    -process "$PROGRAM_NAME" -noanalysis -readOnly \
    -postScript InventorySwitchTables.java "$mode_root/switches.csv"

  ended=$(date +%s)
  uv run --locked python - "$mode_root/raw.json" "$mode_root/switches.csv" \
      "$mode_root/result.json" "$((ended - started))" "$missing_curated" <<'PY'
import csv
import json
import sys
from pathlib import Path
raw_path, switches_path, output_path, elapsed, missing_curated = sys.argv[1:]
result = json.loads(Path(raw_path).read_text())
rows = list(csv.DictReader(Path(switches_path).open()))
result["verified_switch_tables"] = sum(
    row["in_function"] == "Y" and row["validate_ok"] == "Y" for row in rows
)
result["spurious_decoded_switches"] = (
    result["decoded_switches"] - result["verified_switch_tables"]
)
result["curated_functions_missing"] = int(missing_curated)
result["duration_seconds"] = int(elapsed)
Path(output_path).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
PY
  echo "[$mode] $((ended - started)) seconds -> $mode_root/result.json"
}

run_mode default unchanged unchanged
run_mode no-address-tables false unchanged
run_mode no-non-return unchanged false
run_mode neither false false

uv run --locked python - "$OUTPUT_ROOT" <<'PY'
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
modes = ["default", "no-address-tables", "no-non-return", "neither"]
results = [json.loads((root / mode / "result.json").read_text()) for mode in modes]
(root / "summary.json").write_text(json.dumps({"target": "camry-8965F3307000", "results": results}, indent=2) + "\n")
print(root / "summary.json")
PY
