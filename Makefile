UV ?= uv
PYTHON ?= $(UV) run --locked python
EXTERNAL_REPOS_DIR ?= $(abspath ..)
PROJECT_DIR ?= $(CURDIR)/build/project
SNAPSHOT_DIR ?= $(CURDIR)/project
# Canonical parity paths are not command-line overrides: allowing the current
# output to alias the tracked baseline would turn verification into self-compare.
override PROJECT_INVENTORY := $(CURDIR)/build/ghidra_project_inventory.jsonl
override PROJECT_INVENTORY_BASELINE := $(CURDIR)/data/ghidra_project_inventory.baseline.jsonl

VERIFY_SUITES := \
	tests/verify_findings.py \
	tests/verify_payload_gate.py \
	tests/verify_candidate_f05_payload.py \
	tests/verify_security_gate.py \
	tests/verify_secoc_nvm.py \
	tests/verify_secoc_application.py \
	tests/verify_secoc_security_properties.py \
	tests/verify_toyota_secoc_signer.py \
	tests/verify_toyota_secoc_oracle.py \
	tests/verify_toyota_eps_bus_probe.py \
	tests/verify_icus_key_recovery_surface.py \
	tests/verify_icus_software_paths.py \
	tests/verify_icus_key_update.py \
	tests/verify_icus_trace_decoder.py \
	tests/verify_dataflash_layout.py \
	tests/verify_dataflash_semantics.py \
	tests/verify_did_model.py \
	tests/verify_application_diagnostics.py \
	tests/verify_bootloader_diagnostics.py \
	tests/verify_boot_trust.py \
	tests/verify_can_transport.py \
	tests/verify_architecture.py \
	tests/verify_application_transmit.py \
	tests/verify_application_receive.py \
	tests/verify_p1m_device_profile.py \
	tests/verify_ram_overlays.py \
	tests/verify_scheduler_timing.py \
	tests/verify_semantic_coverage.py \
	tests/verify_control_partition.py \
	tests/verify_motor_actuation_boundary.py \
	tests/verify_tss3_variant_matrix.py \
	tests/verify_security_consumers.py \
	tests/verify_application_ab_service.py \
	tests/verify_application_routine_id_callbacks.py \
	tests/verify_diagnostic_vocabulary.py \
	tests/verify_techstream_mackey.py \
	tests/verify_memory_safety.py \
	tests/verify_community_tooling.py \
	tests/verify_community_patch_target_analyzer.py \
	tests/verify_corolla_2023_public_route_summary.py \
	tests/verify_toyota_secoc_session.py \
	tests/verify_rav4_prime_forced_profile_matrix.py \
	tests/verify_techstream_dtc_failure_types.py \
	tests/verify_u023a87_monitor_map.py \
	tests/verify_secoc_acceptance_gate.py \
	tests/verify_renesas_rfp.py \
	tests/verify_lifecycle.py \
	tests/verify_project_layout.py \
	tests/verify_headless_runner.py \
	tests/verify_ghidra_env.py \
	tests/verify_project_inventory.py \
	tests/verify_doc_links.py

.PHONY: sync verify verify-core verify-one verify-changed verify-agent verify-external verify-rfp verify-sleigh verify-processor verify-ghidra \
	ghidra-cli \
	generate-dataflash generate-application-diagnostics generate-diagnostic-vocabulary generate-techstream-corpus \
	generate-application-receive-evidence generate-application-receive \
	generate-processor-fixture generate-semantic-coverage generate-project-inventory \
	verify-project-parity update-project-baseline \
	rebuild-project work-project snapshot-project finalize-project

sync:
	$(UV) sync --locked

# Build the vendored ghidra-cli (ghidra/ghidra-cli) into build/ghidra-cli/.
ghidra-cli:
	tools/build_ghidra_cli.sh

verify: verify-core

verify-core:
	@set -e; for suite in $(VERIFY_SUITES); do \
		echo "==> $$suite"; \
		$(PYTHON) "$$suite"; \
		echo; \
	done

# Fast verification targets (see verification.toml for ownership map).
verify-one:
	@if [ -z "$(SUITE)" ]; then echo "Usage: make verify-one SUITE=<name>" >&2; exit 2; fi
	$(PYTHON) tools/fast_verify.py --suite "$(SUITE)"

verify-changed:
	$(PYTHON) tools/fast_verify.py --changed

verify-agent:
	$(PYTHON) tools/fast_verify.py --agent

verify-external:
	$(PYTHON) tests/verify_external_corroboration.py --repos-dir "$(EXTERNAL_REPOS_DIR)"

verify-rfp:
	$(PYTHON) tests/verify_renesas_rfp.py --require-package

verify-sleigh:
	tools/verify_sleigh.sh

verify-processor:
	tools/verify_processor.sh

# Full local gate: firmware suites + SLEIGH + processor audits + exact parity.
verify-ghidra: verify-core verify-sleigh verify-processor verify-project-parity

generate-dataflash:
	$(PYTHON) tools/generate_dataflash_layout.py
	$(PYTHON) tools/generate_checkpoint_payload_map.py

generate-application-diagnostics:
	$(PYTHON) tools/generate_application_diagnostic_map.py

generate-techstream-corpus:
	cd tools/techstream && $(PYTHON) extract_steering_corpus.py
	cd tools/techstream && $(PYTHON) extract_p4dk4_catalog.py

generate-diagnostic-vocabulary: generate-techstream-corpus
	cd tools/techstream && $(PYTHON) extract_catalog.py
	cd tools/diagnostics && $(PYTHON) correlate_vocabulary.py

generate-application-receive-evidence:
	tools/generate_application_rx_signal_evidence.sh

generate-application-receive: generate-application-receive-evidence
	$(PYTHON) tools/generate_application_rx_map.py

generate-processor-fixture:
	$(PYTHON) tools/build_processor_fixture.py

generate-semantic-coverage:
	tools/generate_semantic_coverage_ledger.sh

generate-project-inventory:
	tools/generate_project_inventory.sh "$(PROJECT_INVENTORY)"

# Exact normalized parity: aggregate floors remain the fast collapse detector;
# this catches substitutions and metadata drift that equal totals cannot.
verify-project-parity:
	tools/generate_project_inventory.sh "$(PROJECT_INVENTORY)"
	$(PYTHON) tools/project_inventory.py compare \
		"$(PROJECT_INVENTORY_BASELINE)" "$(PROJECT_INVENTORY)"

# Deliberately separate from ordinary verification. The baseline can only move
# when two independently rebuilt projects export byte-identical inventories.
update-project-baseline:
	@if [ -z "$(PROJECT_DIR_A)" ] || [ -z "$(PROJECT_DIR_B)" ]; then \
		echo "Usage: make update-project-baseline PROJECT_DIR_A=/abs/rebuild-a PROJECT_DIR_B=/abs/rebuild-b" >&2; \
		exit 2; \
	fi
	@if [ "$$($(PYTHON) -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$(PROJECT_DIR_A)")" = \
	      "$$($(PYTHON) -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$(PROJECT_DIR_B)")" ]; then \
		echo "PROJECT_DIR_A and PROJECT_DIR_B must be independent rebuilds" >&2; \
		exit 2; \
	fi
	PROJECT_DIR="$(PROJECT_DIR_A)" tools/generate_project_inventory.sh \
		"$(CURDIR)/build/ghidra_project_inventory.rebuild-a.jsonl"
	PROJECT_DIR="$(PROJECT_DIR_B)" tools/generate_project_inventory.sh \
		"$(CURDIR)/build/ghidra_project_inventory.rebuild-b.jsonl"
	$(PYTHON) tools/project_inventory.py update \
		"$(CURDIR)/build/ghidra_project_inventory.rebuild-a.jsonl" \
		"$(CURDIR)/build/ghidra_project_inventory.rebuild-b.jsonl" \
		"$(PROJECT_INVENTORY_BASELINE)"
	@echo "Updated $(PROJECT_INVENTORY_BASELINE); review with:"
	@echo "  git diff -- data/ghidra_project_inventory.baseline.jsonl"

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
		$(PYTHON) tools/project_layout.py materialize \
			--snapshot-dir "$(SNAPSHOT_DIR)" \
			--project-dir "$(PROJECT_DIR)" \
			--project-name rh850_p1me_mapped; \
		echo "Ready: $(PROJECT_DIR)"; \
	fi
	@if [ -f "$(PROJECT_DIR)/processor_manifest.json" ]; then \
		$(PYTHON) tools/fingerprint_processor.py --source-only --expect "$(PROJECT_DIR)/processor_manifest.json"; \
	elif [ -f "$(SNAPSHOT_DIR)/processor_manifest.json" ]; then \
		$(PYTHON) tools/fingerprint_processor.py --source-only --expect "$(SNAPSHOT_DIR)/processor_manifest.json"; \
	else \
		echo "NOTE: no processor_manifest.json yet; run rebuild-project to create one"; \
	fi

# Push the working project (build/project) into the committed snapshot
# (project/) and stage it. The ONLY path that mutates the committed project/.
# Verifies exact stats first and refuses if a daemon is still running.
snapshot-project:
	tools/snapshot_project.sh --project-dir "$(PROJECT_DIR)" --snapshot-dir "$(SNAPSHOT_DIR)"

# Deliberate end-of-session promotion: stops the daemon, waits for exit,
# verifies the working project, invokes the snapshot path, and prints the
# staged diff. Distinct from `tools/g stop` (which only persists working-copy
# edits) and from `snapshot-project` (which promotes without orchestrating an
# existing interactive daemon lifecycle).
finalize-project:
	tools/finalize_project.sh
