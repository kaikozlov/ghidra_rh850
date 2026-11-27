#!/usr/bin/env bash
set -euo pipefail

source_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/windowgraph" && pwd)
cache_root=${1:?Usage: build_windowgraph_runner.sh CACHE_DIR}

case $(uname -s) in
    Darwin) platform=darwin; suffix=dylib; shared=-dynamiclib ;;
    Linux) platform=linux; suffix=so; shared=-shared ;;
    *) printf 'Native window graph is unsupported on this host; Java remains available.\n' >&2; exit 1 ;;
esac
arch=$(uname -m)
case $arch in
    arm64|aarch64) arch=aarch64 ;;
    amd64|x86_64) arch=x86_64 ;;
esac

cache=$cache_root/$platform-$arch
compiler=${P1ME_WINDOWGRAPH_CC:-${CC:-cc}}
umask 077
mkdir -p "$cache"
tmp=$(mktemp -d "$cache/.runner.XXXXXXXX")
trap 'rm -rf -- "$tmp"' EXIT
cp "$source_dir/windowgraph-abi.h" "$source_dir/windowgraph-runner.c" "$tmp/"
# The Java loader checks the same header-then-runner source digest.
runner_id=$(python3 - "$tmp" <<'PY'
from hashlib import sha256
from pathlib import Path
from sys import argv

source = Path(argv[1])
digest = sha256()
for name in ('windowgraph-abi.h', 'windowgraph-runner.c'):
    digest.update((source / name).read_bytes())
print(digest.hexdigest())
PY
)
runner=$cache/runner-$runner_id.$suffix
if [[ ! -f "$runner" ]]; then
    "$compiler" -std=c11 -O3 -fPIC "$shared" "-DWINDOWGRAPH_ABI=wg_abi_$runner_id" \
        -o "$tmp/runner.$suffix" "$tmp/windowgraph-runner.c" >&2
    mv -f -- "$tmp/runner.$suffix" "$runner"
fi
printf '%s\n' "$runner"
