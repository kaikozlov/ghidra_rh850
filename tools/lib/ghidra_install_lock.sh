#!/usr/bin/env bash
# Serialize processor installation per build cache. Keep the lock file in place;
# the kernel releases the advisory lock when the last descriptor closes.

_ghidra_lock_open_file() {
  # Bash 3 (macOS) has no dynamic file descriptors, and macOS has no flock(1).
  # Python locks the open file description shared with this shell on fd 9.
  python3 -c 'import fcntl, os, sys
if not os.path.samestat(os.fstat(9), os.stat(sys.argv[1])):
    raise SystemExit("Ghidra install lock descriptor does not match the build cache")
fcntl.flock(9, fcntl.LOCK_EX)' "$BUILD_CACHE/ghidra-processor.lock"
}

_ghidra_install_lock_is_inherited() {
  [[ "$BUILD_CACHE/ghidra-processor.lock" -ef "${_GHIDRA_INSTALL_LOCK_FILE:-}" ]] &&
    _ghidra_lock_open_file 2>/dev/null
}

_ghidra_run_locked() {
  local _GHIDRA_INSTALL_LOCK_FILE="$BUILD_CACHE/ghidra-processor.lock"
  _ghidra_lock_open_file || return 1
  export _GHIDRA_INSTALL_LOCK_FILE
  "$@"
}

_ghidra_with_install_lock() {
  if _ghidra_install_lock_is_inherited; then
    "$@"
  else
    mkdir -p "$BUILD_CACHE" || return 1
    _ghidra_run_locked "$@" 9>>"$BUILD_CACHE/ghidra-processor.lock"
  fi
}
