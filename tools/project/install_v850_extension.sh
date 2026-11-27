#!/usr/bin/env bash
# Compile vendored SLEIGH and processor analyzers, then install into an isolated
# Ghidra user-home. Never mutates $GHIDRA_HOME/Ghidra/Extensions.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/tools/lib/build_paths.sh"
# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_install_lock.sh"
# shellcheck disable=SC1091
source "$ROOT/tools/lib/ghidra_p1me_runtime.sh"
if ! _ghidra_install_lock_is_inherited; then
  # Direct invocations take the same lock as bootstrap before writing anything.
  _ghidra_with_install_lock exec "$BASH" "$0" "$@"
fi
mkdir -p "$BUILD_CACHE" "$BUILD_WORK" "$BUILD_OUT" "$BUILD_LOGS" "$BUILD_TMP"
GHIDRA_HOME="$("$ROOT/tools/project/resolve_ghidra_home.sh")"
VENDOR="$ROOT/ghidra/ghidra_v850"
BUILD_EXT="$BUILD_CACHE/processor-extension-src/Renesas_v850"
LANG="$BUILD_EXT/data/languages"
USER_HOME="${GHIDRA_ISOLATED_HOME:-$BUILD_CACHE/ghidra-home}"
SETTINGS_DIR="$USER_HOME/Library/ghidra/ghidra_12.2_PUBLIC"
EXT_DIR="${V850_EXT_DIR:-$SETTINGS_DIR/Extensions/Renesas_v850}"
LOG_DIR="$BUILD_LOGS/sleigh"
MANIFEST="${PROCESSOR_MANIFEST:-$BUILD_OUT/processor_manifest.json}"
ENV_FILE="${GHIDRA_PROCESSOR_ENV_FILE:-$BUILD_CACHE/ghidra-processor.env}"
PATCH_ROOT="$ROOT/ghidra/runtime-patches"
PATCH_BUILD="$BUILD_CACHE/ghidra-runtime-patches"
PATCH_MODULE="$PATCH_BUILD/EmulationSymbolsCache"
PATCH_CLASS="$PATCH_MODULE/bin/main/ghidra/pcode/exec/SymbolsCache.class"
PATCH_SOURCE_SHA256=$(shasum -a 256 \
  "$PATCH_ROOT/src/ghidra/pcode/exec/SymbolsCache.java" | awk '{print $1}')
RUNTIME_SOURCE_SHA256=$(_ghidra_p1me_runtime_source_sha "$ROOT")
WINDOWGRAPH_CACHE="$BUILD_CACHE/p1me-windowgraph"

GHIDRA_VERSION=$(awk -F= '$1 == "application.version" { print $2 }' "$GHIDRA_HOME/Ghidra/application.properties")
[[ "$GHIDRA_VERSION" == "12.2" ]] || {
  echo "Ghidra 12.2 is required (found ${GHIDRA_VERSION:-unknown})" >&2
  exit 1
}
if [[ ${1:-} == --coherent-slab ]]; then
  shift
  mkdir -p "$PATCH_BUILD"
  exec bash "$PATCH_ROOT/build_coherent_slab.sh" "$GHIDRA_HOME" "$PATCH_BUILD" "$@"
fi
CLI_VERSION="missing"
GHIDRA_CLI_BIN=""
if [[ -x "$BUILD_CACHE/ghidra-cli/ghidra" ]]; then
  GHIDRA_CLI_BIN="$BUILD_CACHE/ghidra-cli/ghidra"
  CLI_VERSION=$("$GHIDRA_CLI_BIN" --version | awk 'NR == 1 { print $2 }')
  [[ "$CLI_VERSION" == "0.2.1" ]] || {
    echo "vendored ghidra CLI version mismatch (found $CLI_VERSION)" >&2
    exit 1
  }
elif command -v ghidra >/dev/null 2>&1; then
  GHIDRA_CLI_BIN=$(command -v ghidra)
  CLI_VERSION=$(ghidra --version | awk 'NR == 1 { print $2 }')
  [[ "$CLI_VERSION" == "0.2.1" ]] || {
    echo "ghidra CLI 0.2.1 is required when present (found $CLI_VERSION)" >&2
    exit 1
  }
else
  echo "NOTE: ghidra CLI not built or on PATH; SLEIGH compile will still proceed" >&2
fi

command -v rsync >/dev/null 2>&1 || { echo "rsync is required" >&2; exit 1; }
mkdir -p "$LOG_DIR" "$SETTINGS_DIR/Extensions" "$(dirname "$BUILD_EXT")"

INSTALL_TREE_EXT="$GHIDRA_HOME/Ghidra/Extensions/Renesas_v850"
if [[ -e "$INSTALL_TREE_EXT" ]]; then
  echo "ERROR: conflicting install-tree extension exists at:" >&2
  echo "  $INSTALL_TREE_EXT" >&2
  echo "Remove it explicitly; this isolated installer will never modify GHIDRA_HOME." >&2
  exit 1
fi

mkdir -p "$PATCH_BUILD"
SLAB_MODULE=$(bash "$PATCH_ROOT/build_coherent_slab.sh" "$GHIDRA_HOME" "$PATCH_BUILD")
SLAB_CLASS="$SLAB_MODULE/bin/main/ghidra/generic/util/datastruct/SemisparseByteArray.class"
SLAB_SHA256=$(shasum -a 256 "$SLAB_CLASS" | awk '{print $1}')

# Build from a disposable copy so generated .sla files never touch vendored
# sources. Exclude any stale local outputs that may predate this installer.
rm -rf "$BUILD_EXT"
mkdir -p "$BUILD_EXT"
rsync -a --delete --exclude '.git' --exclude '*.sla' "$VENDOR/" "$BUILD_EXT/"
for manual in r01us0001ej0100_v850e2m.pdf r01us0123ej0140-rh850g3m.pdf; do
  if [[ -f "$ROOT/REFERENCE/$manual" ]]; then
    ln -s "$ROOT/REFERENCE/$manual" "$BUILD_EXT/data/manuals/$manual"
  fi
done
python3 "$ROOT/tools/project/build_compiler_policy_specs.py" "$LANG"

echo "Compiling vendored SLEIGH sources under $LANG"
(
  cd "$LANG"
  for spec in *.slaspec; do
    log="$LOG_DIR/${spec%.slaspec}.log"
    if ! JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -Duser.home=$USER_HOME" \
      "$GHIDRA_HOME/support/sleigh" "$spec" >"$log" 2>&1; then
      echo "sleigh failed for $spec; see $log" >&2
      cat "$log" >&2
      exit 1
    fi
    if grep -E '\bERROR\b|Exception' "$log" >/dev/null 2>&1; then
      echo "unexpected sleigh diagnostics in $log" >&2
      cat "$log" >&2
      exit 1
    fi
    unexpected_warnings=$(grep -E '\bWARN(ING)?\b' "$log" \
      | grep -Ev 'WARN  [0-9]+ NOP constructors found|WARN  Use -n switch to list each individually' \
      || true)
    if [[ -n "$unexpected_warnings" ]]; then
      echo "unexpected sleigh warnings in $log" >&2
      printf '%s\n' "$unexpected_warnings" >&2
      exit 1
    fi
  done
)
[[ -f "$LANG/v850e3.sla" ]] || { echo "sleigh did not produce v850e3.sla" >&2; exit 1; }

# Both the processor extension and the symbols overlay compile against the installed API.
CLASSPATH=$(_ghidra_p1me_installed_classpath "$GHIDRA_HOME")

# Processor analyzers are ordinary extension classes, discovered by Ghidra's
# class search. Build them alongside the languages, never in the source tree.
JAVA_SOURCES=()
while IFS= read -r source; do
  JAVA_SOURCES+=("$source")
done < <(find "$BUILD_EXT/src/main/java" -name '*.java' -type f | sort)
if [[ ${#JAVA_SOURCES[@]} -gt 0 ]]; then
  CLASSES="$BUILD_EXT/build/classes"
  mkdir -p "$CLASSES" "$BUILD_EXT/lib"
  javac --release 25 -encoding UTF-8 -cp "$CLASSPATH" \
    -d "$CLASSES" "${JAVA_SOURCES[@]}"
  jar --create --file "$BUILD_EXT/lib/Renesas_v850.jar" \
    --date=2000-01-01T00:00:00Z -C "$CLASSES" .
  rm -rf "$BUILD_EXT/build"
fi

mkdir -p "$(dirname "$PATCH_CLASS")"
: >"$PATCH_MODULE/Module.manifest"
PATCH_TMP=$(mktemp -d "$PATCH_MODULE/.classes.XXXXXX")
trap 'rm -rf "$PATCH_TMP"' EXIT
javac --release 25 -encoding UTF-8 -cp "$CLASSPATH" -d "$PATCH_TMP" \
  "$PATCH_ROOT/src/ghidra/pcode/exec/SymbolsCache.java"
mv -f "$PATCH_TMP/ghidra/pcode/exec/SymbolsCache.class" "$PATCH_CLASS"
rm -rf "$PATCH_TMP"
trap - EXIT
PATCH_SHA256=$(shasum -a 256 "$PATCH_CLASS" | awk '{print $1}')

if WINDOWGRAPH_RUNNER=$(bash "$PATCH_ROOT/build_windowgraph_runner.sh" "$WINDOWGRAPH_CACHE"); then
  echo "Native window graph runner: $WINDOWGRAPH_RUNNER"
else
  WINDOWGRAPH_RUNNER=""
  echo "Native graph runner unavailable; using the Java instruction path." >&2
fi
RUNTIME_ID=$(printf '%s\n' "$RUNTIME_SOURCE_SHA256" "$SLAB_SHA256" "$PATCH_SHA256" "$WINDOWGRAPH_RUNNER" |
  shasum -a 256 | awk '{print $1}')

echo "Installing Renesas_v850 -> $EXT_DIR"
mkdir -p "$(dirname "$EXT_DIR")"
# Do not advertise a ready cache while replacing the installed extension.
rm -f "$ENV_FILE"
rsync -a --delete "$BUILD_EXT/" "$EXT_DIR/"

python3 "$ROOT/tools/project/fingerprint_processor.py" \
  --ghidra-version "$GHIDRA_VERSION" \
  --cli-version "$CLI_VERSION" \
  --sla "$LANG/v850e3.sla" \
  --write "$MANIFEST"

# Publish the completed environment in one step for lock-free readers.
ENV_TMP="$(mktemp "${ENV_FILE}.XXXXXX")"
trap 'rm -f "$ENV_TMP"' EXIT
cat >"$ENV_TMP" <<EOF
export GHIDRA_HOME="$GHIDRA_HOME"
export GHIDRA_ISOLATED_HOME="$USER_HOME"
export V850_EXT_DIR="$EXT_DIR"
export V850_BUILD_DIR="$BUILD_EXT"
export PROCESSOR_MANIFEST="$MANIFEST"
export GHIDRA_VERSION="$GHIDRA_VERSION"
export GHIDRA_CLI_VERSION="$CLI_VERSION"
export GHIDRA_EMULATION_PATCH="$PATCH_MODULE"
export GHIDRA_EMULATION_PATCH_SHA256="$PATCH_SHA256"
export GHIDRA_EMULATION_PATCH_SOURCE_SHA256="$PATCH_SOURCE_SHA256"
export GHIDRA_P1ME_SLAB_MODULE="$SLAB_MODULE"
export GHIDRA_P1ME_SLAB_CLASS_SHA256="$SLAB_SHA256"
export GHIDRA_P1ME_RUNTIME_SOURCE_SHA256="$RUNTIME_SOURCE_SHA256"
export GHIDRA_P1ME_WINDOWGRAPH_RUNNER="$WINDOWGRAPH_RUNNER"
_p1me_modules="$SLAB_MODULE"
export GHIDRA_P1ME_RUNTIME_ID="$RUNTIME_ID"
if [[ "\${GHIDRA_DISABLE_EMULATION_PATCH:-0}" != "1" ]]; then
  _p1me_modules="$PATCH_MODULE:\$_p1me_modules"
else
  GHIDRA_P1ME_RUNTIME_ID="\$GHIDRA_P1ME_RUNTIME_ID-no-symbols"
fi
export GHIDRA_JAVA_OPTIONS="\${GHIDRA_JAVA_OPTIONS:-} -Dghidra.external.modules=\$_p1me_modules -Dghidra.cli.runtime.id=\$GHIDRA_P1ME_RUNTIME_ID -Duser.home=$USER_HOME"
unset _p1me_modules
if [[ -n "\$GHIDRA_P1ME_WINDOWGRAPH_RUNNER" ]]; then
  export P1ME_WINDOWGRAPH_SOURCE="$PATCH_ROOT/windowgraph"
  export P1ME_WINDOWGRAPH_RUNNER_CACHE="$WINDOWGRAPH_CACHE"
  export P1ME_WINDOWGRAPH_CACHE="\${P1ME_WINDOWGRAPH_CACHE:-$WINDOWGRAPH_CACHE}"
  export P1ME_WINDOWGRAPH_CC="\${P1ME_WINDOWGRAPH_CC:-\${CC:-cc}}"
  export GHIDRA_JAVA_OPTIONS="\$GHIDRA_JAVA_OPTIONS --enable-native-access=ALL-UNNAMED"
else
  unset P1ME_WINDOWGRAPH_SOURCE P1ME_WINDOWGRAPH_RUNNER_CACHE
fi
export GHIDRA_HEADLESS_JAVA_OPTIONS="\${GHIDRA_HEADLESS_JAVA_OPTIONS:-} -Duser.home=$USER_HOME"
EOF
mv -f "$ENV_TMP" "$ENV_FILE"
trap - EXIT

echo "Installed extension: $EXT_DIR"
echo "Processor manifest: $MANIFEST"
echo "Emulation patch: $PATCH_MODULE"
echo "Coherent emulation backing module: $SLAB_MODULE"
echo "Env helper: $ENV_FILE"
