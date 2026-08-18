UV ?= uv
PYTHON ?= $(UV) run --locked python
EXTERNAL_REPOS_DIR ?= $(abspath ..)
PROJECT_DIR ?= $(CURDIR)/build/project
SNAPSHOT_DIR ?= $(CURDIR)/project
# Canonical parity paths are not command-line overrides: allowing the current
# output to alias the tracked baseline would turn verification into self-compare.
override PROJECT_INVENTORY := $(CURDIR)/build/ghidra_project_inventory.jsonl
override PROJECT_INVENTORY_BASELINE := $(CURDIR)/data/ghidra_project_inventory.baseline.jsonl

.PHONY: sync verify verify-core verify-local verify-one verify-changed verify-agent verify-exploit verify-required-external verify-external verify-corroboration verify-rfp verify-sleigh verify-processor verify-semantic-coverage-live verify-ghidra \
	ghidra-cli \
	generate-dataflash generate-application-diagnostics generate-diagnostic-vocabulary generate-techstream-corpus \
	generate-application-receive-evidence generate-application-receive generate-application-transmit \
	generate-processor-fixture generate-function-discovery generate-semantic-coverage generate-project-inventory \
	generate-semantic-sweep generate-decompiler-corpus pseudocode \
	verify-project-parity update-project-baseline \
	rebuild-project work-project snapshot-project finalize-project

sync:
	$(UV) sync --locked

# Build the vendored ghidra-cli (ghidra/ghidra-cli) into build/ghidra-cli/.
ghidra-cli:
	tools/build_ghidra_cli.sh

verify: verify-core

verify-core:
	$(PYTHON) tools/fast_verify.py --core

verify-local:
	$(PYTHON) tools/fast_verify.py --local

# Fast verification targets (see verification.toml for ownership map).
verify-one:
	@if [ -z "$(SUITE)" ]; then echo "Usage: make verify-one SUITE=<name>" >&2; exit 2; fi
	$(PYTHON) tools/fast_verify.py --suite "$(SUITE)"

verify-changed:
	$(PYTHON) tools/fast_verify.py --changed

verify-agent:
	$(PYTHON) tools/fast_verify.py --agent

verify-exploit:
	$(PYTHON) tools/fast_verify.py --suite exploit_surface
	$(PYTHON) tools/fast_verify.py --suite exploit_predicate_semantics
	$(PYTHON) tools/fast_verify.py --suite secoc_manifest_patcher
	$(PYTHON) tools/fast_verify.py --suite codeflash_dumper
	$(PYTHON) tools/fast_verify.py --suite ephemeral_runtime
	$(PYTHON) tools/fast_verify.py --suite ephemeral_runtime_resolver
	$(PYTHON) tools/fast_verify.py --suite secoc_command5_experiment
	$(PYTHON) tools/fast_verify.py --suite secoc_mac28_behavioral_proof
	$(PYTHON) tools/fast_verify.py --suite exploit_followups
	$(PYTHON) tools/fast_verify.py --suite variant_acquisition_readiness

verify-required-external:
	$(PYTHON) tools/fast_verify.py --required-external

verify-external verify-corroboration:
	$(PYTHON) tests/verify_external_corroboration.py --repos-dir "$(EXTERNAL_REPOS_DIR)"

verify-rfp:
	$(PYTHON) tests/verify_renesas_rfp.py --require-package

verify-sleigh:
	tools/verify_sleigh.sh

verify-processor:
	tools/verify_processor.sh

# Full local gate: firmware suites + SLEIGH + processor audits + exact parity.
verify-semantic-coverage-live:
	$(PYTHON) tests/verify_semantic_coverage_live.py --project-dir "$(PROJECT_DIR)"

verify-ghidra: verify-core verify-sleigh verify-processor verify-semantic-coverage-live verify-project-parity

generate-dataflash:
	$(PYTHON) tools/generate_dataflash_layout.py
	$(PYTHON) tools/generate_checkpoint_payload_map.py

generate-application-diagnostics:
	$(PYTHON) tools/generate_application_diagnostic_map.py
	$(PYTHON) tools/generate_application_wdbi_surface.py

generate-techstream-corpus:
	cd tools/techstream && $(PYTHON) extract_steering_corpus.py
	cd tools/techstream && $(PYTHON) extract_p4dk4_catalog.py
	$(PYTHON) tools/techstream/extract_factory_table_map.py
	$(PYTHON) tools/techstream/extract_toyota_master_routes.py
	$(PYTHON) tools/techstream/extract_priority_ddb_semantics.py
	$(PYTHON) tools/techstream/generate_dtc_failure_types.py

generate-diagnostic-vocabulary: generate-techstream-corpus
	cd tools/techstream && $(PYTHON) extract_catalog.py
	cd tools/diagnostics && $(PYTHON) correlate_vocabulary.py

generate-application-receive-evidence:
	tools/generate_application_rx_signal_evidence.sh

generate-application-receive: generate-application-receive-evidence
	$(PYTHON) tools/generate_application_rx_map.py

generate-application-transmit:
	$(PYTHON) tools/generate_application_tx_map.py

generate-processor-fixture:
	$(PYTHON) tools/build_processor_fixture.py

generate-function-discovery:
	tools/generate_outside_function_candidates.sh

generate-semantic-coverage:
	tools/generate_semantic_coverage_ledger.sh

generate-semantic-sweep:
	$(PYTHON) tools/generate_semantic_sweep.py --project-dir "$(PROJECT_DIR)"

generate-decompiler-corpus:
	$(PYTHON) tools/generate_decompiler_corpus.py --project-dir "$(PROJECT_DIR)"

pseudocode:
	$(PYTHON) tools/pseudo --materialize

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
