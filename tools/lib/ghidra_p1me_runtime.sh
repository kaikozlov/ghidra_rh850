# Shared runtime inputs and build settings for the installer, launcher, and overlay builder.
_ghidra_p1me_runtime_source_sha() {
  local dir="$1/ghidra/runtime-patches"
  (
    set -o pipefail
    cat "$dir/build_coherent_slab.sh" "$dir/ghidra-12.2-coherent-slab.patch" \
      "$dir/build_windowgraph_runner.sh" "$dir/windowgraph/windowgraph-abi.h" \
      "$dir/windowgraph/windowgraph-runner.c" "$1/tools/lib/ghidra_p1me_runtime.sh" |
      shasum -a 256 | awk '{print $1}'
  )
}

_ghidra_p1me_installed_classpath() {
  local dependency classpath=
  for dependency in "$1"/Ghidra/{Framework,Features,Processors}/*/lib/*.jar; do
    [[ -f "$dependency" ]] || continue
    classpath="${classpath:+$classpath:}$dependency"
  done
  printf '%s\n' "$classpath"
}
