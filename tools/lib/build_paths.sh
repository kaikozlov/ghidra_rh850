#!/usr/bin/env bash
# Canonical ignored-workspace layout. Caller must define ROOT first.
: "${ROOT:?caller must define ROOT before sourcing build_paths.sh}"
BUILD_ROOT="${BUILD_ROOT:-$ROOT/build}"
BUILD_CACHE="${BUILD_CACHE:-$BUILD_ROOT/cache}"
BUILD_WORK="${BUILD_WORK:-$BUILD_ROOT/work}"
BUILD_OUT="${BUILD_OUT:-$BUILD_ROOT/out}"
BUILD_LOGS="${BUILD_LOGS:-$BUILD_ROOT/logs}"
BUILD_TMP="${BUILD_TMP:-$BUILD_ROOT/tmp}"
export BUILD_ROOT BUILD_CACHE BUILD_WORK BUILD_OUT BUILD_LOGS BUILD_TMP
