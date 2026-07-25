UV ?= uv
PYTHON ?= $(UV) run --locked python
EXTERNAL_REPOS_DIR ?= $(abspath ..)
PROJECT_DIR ?= $(CURDIR)/build/project

VERIFY_SUITES := \
	tests/verify_findings.py \
	tests/verify_payload_gate.py \
	tests/verify_secoc_nvm.py \
	tests/verify_dataflash_layout.py \
	tests/verify_did_model.py \
	tests/verify_application_diagnostics.py \
	tests/verify_can_transport.py

.PHONY: sync verify verify-core verify-external generate-dataflash rebuild-project

sync:
	$(UV) sync --locked

verify: verify-core

verify-core:
	@set -e; for suite in $(VERIFY_SUITES); do \
		echo "==> $$suite"; \
		$(PYTHON) "$$suite"; \
		echo; \
	done

verify-external:
	$(PYTHON) tests/verify_external_corroboration.py --repos-dir "$(EXTERNAL_REPOS_DIR)"

generate-dataflash:
	$(PYTHON) tools/generate_dataflash_layout.py

rebuild-project:
	tools/rebuild_project.sh --project-dir "$(PROJECT_DIR)"
