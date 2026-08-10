#!/usr/bin/env bash
# Shared, cached, fail-closed isolated Ghidra environment setup.
# Source as: source tools/lib/ghidra_env.sh [none|source|full] [manifest]

_GHIDRA_ENV_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
_GHIDRA_ENV_FILE="${GHIDRA_PROCESSOR_ENV_FILE:-$_GHIDRA_ENV_ROOT/build/ghidra-processor.env}"
_GHIDRA_INSTALL="${GHIDRA_INSTALL_SCRIPT:-$_GHIDRA_ENV_ROOT/tools/install_v850_extension.sh}"
_GHIDRA_FINGERPRINT="${GHIDRA_FINGERPRINT_TOOL:-$_GHIDRA_ENV_ROOT/tools/fingerprint_processor.py}"
_GHIDRA_FINGERPRINT_MODE="${1:-none}"
_GHIDRA_REQUESTED_MANIFEST="${2:-}"

case "$_GHIDRA_FINGERPRINT_MODE" in
  none|source|full) ;;
  *)
    echo "ERROR: unknown fingerprint mode: $_GHIDRA_FINGERPRINT_MODE" >&2
    echo "Usage: source ghidra_env.sh [none|source|full] [manifest-path]" >&2
    exit 1
    ;;
esac

_source_processor_env() {
  [[ -f "$_GHIDRA_ENV_FILE" ]] || return 1
  # shellcheck disable=SC1090
  source "$_GHIDRA_ENV_FILE"
}

_cached_env_is_current() {
  _source_processor_env || return 1
  [[ "${GHIDRA_VERSION:-}" == "12.1.2" ]] || return 1
  [[ "${GHIDRA_CLI_VERSION:-}" == "0.2.1" ]] || return 1
  [[ -d "${GHIDRA_HOME:-}" ]] || return 1
  [[ -f "$GHIDRA_HOME/Ghidra/application.properties" ]] || return 1
  [[ "$(awk -F= '$1 == "application.version" { print $2 }' "$GHIDRA_HOME/Ghidra/application.properties")" == "12.1.2" ]] || return 1
  [[ -f "${V850_EXT_DIR:-}/data/languages/v850e3.sla" ]] || return 1
  [[ -f "${PROCESSOR_MANIFEST:-}" ]] || return 1
  python3 "$_GHIDRA_FINGERPRINT" \
    --source-only --expect "$PROCESSOR_MANIFEST" >/dev/null 2>&1
}

if [[ "${GHIDRA_ENV_FORCE_REBUILD:-0}" == "1" ]] || ! _cached_env_is_current; then
  [[ -x "$_GHIDRA_INSTALL" ]] || {
    echo "ERROR: processor installer is not executable: $_GHIDRA_INSTALL" >&2
    exit 1
  }
  "$_GHIDRA_INSTALL" >&2
  _source_processor_env || {
    echo "ERROR: processor installer did not write env file: $_GHIDRA_ENV_FILE" >&2
    exit 1
  }
fi

# Re-validate after install. A successful installer exit is not enough.
_cached_env_is_current || {
  echo "ERROR: isolated Ghidra processor environment is missing or stale after install" >&2
  exit 1
}

ROOT="$_GHIDRA_ENV_ROOT"
export ROOT GHIDRA_HOME GHIDRA_ISOLATED_HOME V850_EXT_DIR V850_BUILD_DIR
export PROCESSOR_MANIFEST GHIDRA_VERSION GHIDRA_CLI_VERSION
export GHIDRA_JAVA_OPTIONS GHIDRA_HEADLESS_JAVA_OPTIONS
export GHIDRA_ENV_READY=1

_GHIDRA_MANIFEST="${_GHIDRA_REQUESTED_MANIFEST:-$PROCESSOR_MANIFEST}"
case "$_GHIDRA_FINGERPRINT_MODE" in
  none)
    ;;
  source)
    [[ -f "$_GHIDRA_MANIFEST" ]] || {
      echo "ERROR: manifest not found for source fingerprint: $_GHIDRA_MANIFEST" >&2
      exit 1
    }
    python3 "$_GHIDRA_FINGERPRINT" \
      --source-only --expect "$_GHIDRA_MANIFEST" >&2
    ;;
  full)
    [[ -f "$_GHIDRA_MANIFEST" ]] || {
      echo "ERROR: manifest not found for full fingerprint: $_GHIDRA_MANIFEST" >&2
      exit 1
    }
    python3 "$_GHIDRA_FINGERPRINT" \
      --expect "$_GHIDRA_MANIFEST" \
      --ghidra-version "$GHIDRA_VERSION" \
      --cli-version "$GHIDRA_CLI_VERSION" \
      --sla "$V850_EXT_DIR/data/languages/v850e3.sla" >&2
    ;;
esac
