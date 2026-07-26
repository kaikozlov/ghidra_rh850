UV ?= uv
PYTHON ?= $(UV) run --locked python
EXTERNAL_REPOS_DIR ?= $(abspath ..)
PROJECT_DIR ?= $(CURDIR)/build/project
SNAPSHOT_DIR ?= $(CURDIR)/project

VERIFY_SUITES := \
	tests/verify_findings.py \
	tests/verify_payload_gate.py \
	tests/verify_secoc_nvm.py \
	tests/verify_secoc_application.py \
	tests/verify_dataflash_layout.py \
	tests/verify_dataflash_semantics.py \
	tests/verify_did_model.py \
	tests/verify_application_diagnostics.py \
	tests/verify_bootloader_diagnostics.py \
	tests/verify_can_transport.py \
	tests/verify_architecture.py \
	tests/verify_application_transmit.py

.PHONY: sync verify verify-core verify-external generate-dataflash rebuild-project work-project snapshot-project

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
	$(PYTHON) tools/generate_checkpoint_payload_map.py

rebuild-project:
	tools/rebuild_project.sh --project-dir "$(PROJECT_DIR)"

# Materialize the gitignored working project (build/project) from the committed
# snapshot (project/) if it does not already exist. Fast local copy (~2s). All
# interactive `ghidra` CLI work targets build/project/ so the committed snapshot
# is never daemon-opened (any open compacts its DB and churns the tree).
work-project:
	@if [ -d "$(PROJECT_DIR)/rh850_p1me_mapped.rep" ]; then \
		echo "Working project already exists: $(PROJECT_DIR)"; \
	else \
		echo "Materializing working project from committed snapshot..."; \
		mkdir -p "$(PROJECT_DIR)"; \
		cp -R "$(SNAPSHOT_DIR)/." "$(PROJECT_DIR)/"; \
		echo "Ready: $(PROJECT_DIR)"; \
	fi

# Push the working project (build/project) into the committed snapshot
# (project/) and stage it. The ONLY path that mutates the committed project/.
# Verifies exact stats first and refuses if a daemon is still running.
snapshot-project:
	tools/snapshot_project.sh --project-dir "$(PROJECT_DIR)" --snapshot-dir "$(SNAPSHOT_DIR)"
