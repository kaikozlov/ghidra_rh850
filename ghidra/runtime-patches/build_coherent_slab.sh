#!/usr/bin/env bash
# Build the Ghidra 12.2 coherent storage overlay without modifying Ghidra.
set -euo pipefail
PATCH_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck disable=SC1091
source "$PATCH_ROOT/../../tools/lib/ghidra_p1me_runtime.sh"
if [[ $# -lt 2 || $# -gt 3 || ( $# -eq 3 && $3 != --proof ) ]]; then
  echo "Usage: $0 GHIDRA_HOME OUTPUT_DIR [--proof]" >&2
  exit 2
fi
GHIDRA_HOME=$(cd "$1" && pwd -P)
OUTPUT_DIR=$(cd "$2" && pwd -P)
VERSION=$(awk -F= '$1 == "application.version" { print $2 }' "$GHIDRA_HOME/Ghidra/application.properties")
if [[ "$VERSION" != 12.2 ]]; then
  echo "The coherent slab overlay requires Ghidra 12.2 (found ${VERSION:-unknown})" >&2
  exit 1
fi
ARCHIVE="$GHIDRA_HOME/Ghidra/Framework/Emulation/lib/Emulation-src.zip"
if [[ ! -f "$ARCHIVE" ]]; then
  echo "Ghidra 12.2's Emulation source archive is required: $ARCHIVE" >&2
  exit 1
fi
if [[ "$OUTPUT_DIR/" == "$GHIDRA_HOME/"* ]]; then
  echo 'Refusing to write an overlay into GHIDRA_HOME' >&2
  exit 1
fi

WORK=$(mktemp -d "$OUTPUT_DIR/.coherent-slab.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
mkdir "$WORK/src" "$WORK/classes"
PATCH="$PATCH_ROOT/ghidra-12.2-coherent-slab.patch"
SOURCES=()
while IFS= read -r path; do
  source="$WORK/src/$path"
  mkdir -p "$(dirname "$source")"
  case "$path" in
    ghidra/app/plugin/processors/sleigh/*) archive="$GHIDRA_HOME/Ghidra/Framework/SoftwareModeling/lib/SoftwareModeling-src.zip" ;;
    *) archive="$ARCHIVE" ;;
  esac
  unzip -p "$archive" "$path" > "$source"
  [[ -s "$source" ]] || {
    echo "Ghidra 12.2 source archive lacks $source" >&2
    exit 1
  }
  SOURCES+=("$source")
done < <(awk '/^--- a\// { print substr($0, 7) }' "$PATCH")
# Every hunk must apply exactly to the versioned upstream source.
(cd "$WORK/src" && patch -f -F 0 -p1 < "$PATCH" >&2)

CLASSPATH=$(_ghidra_p1me_installed_classpath "$GHIDRA_HOME")
javac --release 25 -encoding UTF-8 -cp "$CLASSPATH" -d "$WORK/classes" "${SOURCES[@]}"

if [[ ${3:-} == --proof ]]; then
  mkdir "$WORK/proof"
  javac --release 25 -encoding UTF-8 -cp "$WORK/classes:$CLASSPATH" \
    -d "$WORK/proof" "$PATCH_ROOT/proof/coherentslab/proof/CoherentSlabProof.java"
  # Load the overlay before the installed jars, as Ghidra does at launch.
  java -Djava.awt.headless=true -Duser.home="$WORK" \
    -cp "$WORK/proof:$WORK/classes:$CLASSPATH" \
    coherentslab.proof.CoherentSlabProof "$GHIDRA_HOME" >&2
fi

# A running Ghidra can retain the module path, so publish each build at a new path.
MODULE="$WORK/EmulationCoherentSlab"
mkdir -p "$MODULE/bin"
: > "$MODULE/Module.manifest"
mv "$WORK/classes" "$MODULE/bin/main"
PUBLISHED=$(mktemp -d "$OUTPUT_DIR/coherent-slab.XXXXXX")
mv "$MODULE" "$PUBLISHED/"
printf '%s\n' "$PUBLISHED/EmulationCoherentSlab"
