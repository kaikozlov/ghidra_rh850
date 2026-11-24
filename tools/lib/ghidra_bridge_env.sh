# Sourced by repository Ghidra CLI callers. Like uv, resolve a relative
# UV_PROJECT_ENVIRONMENT from the project root, not the caller's directory.
case "${UV_PROJECT_ENVIRONMENT:-.venv}" in
  /*) GHIDRA_CLI_PYGHIDRA_PYTHON="$UV_PROJECT_ENVIRONMENT/bin/python" ;;
  *)  GHIDRA_CLI_PYGHIDRA_PYTHON="$ROOT/${UV_PROJECT_ENVIRONMENT:-.venv}/bin/python" ;;
esac
export GHIDRA_CLI_PYGHIDRA_PYTHON
