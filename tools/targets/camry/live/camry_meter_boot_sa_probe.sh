#!/usr/bin/env bash
set -euo pipefail

HERE="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)"
PY="${CAMRY_METER_PYTHON:-/usr/local/venv/bin/python}"
TOOL="${CAMRY_METER_PROBE:-$HERE/camry_meter_boot_sa_probe.py}"
LEASE_LIB="${CAMRY_METER_LEASE_LIB:-/data/tss3-oracle/runtime/tsk/ram_runtime/tss3_panda_lease.sh}"

die() { printf 'camry-meter-probe: %s\n' "$*" >&2; exit 2; }

[[ -x "$PY" ]] || die "python unavailable: $PY"
[[ -f "$TOOL" ]] || die "probe missing: $TOOL"
[[ -f "$LEASE_LIB" ]] || die "Panda lease helper missing: $LEASE_LIB"

# shellcheck source=/dev/null
source "$LEASE_LIB"
quiesce_panda_owner

cd /data/openpilot
"$PY" "$TOOL" "$@"
