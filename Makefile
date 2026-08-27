UV ?= uv
PYTHON ?= $(UV) run --locked python
EXTERNAL_REPOS_DIR ?= $(abspath ..)
BUILD_ROOT ?= $(CURDIR)/build
BUILD_CACHE ?= $(BUILD_ROOT)/cache
BUILD_WORK ?= $(BUILD_ROOT)/work
BUILD_OUT ?= $(BUILD_ROOT)/out
BUILD_LOGS ?= $(BUILD_ROOT)/logs
BUILD_TMP ?= $(BUILD_ROOT)/tmp
export BUILD_ROOT BUILD_CACHE BUILD_WORK BUILD_OUT BUILD_LOGS BUILD_TMP
TARGET ?= sienna-8965B4512000
DEFAULT_TARGET := sienna-8965B4512000
ifeq ($(TARGET),$(DEFAULT_TARGET))
PROJECT_DIR ?= $(BUILD_WORK)/project
SNAPSHOT_DIR ?= $(CURDIR)/project
PROJECT_NAME := rh850_p1me_mapped
PROGRAM_NAME := RH850_P1M-E_CodeFlash.bin
# Canonical parity paths are not command-line overrides: allowing the current
# output to alias the tracked baseline would turn verification into self-compare.
override PROJECT_INVENTORY := $(BUILD_OUT)/ghidra_project_inventory.jsonl
override PROJECT_INVENTORY_BASELINE := $(CURDIR)/data/ghidra_project_inventory.baseline.jsonl
else
TARGET_WORK_DIR := $(shell python3 tools/analysis_target.py "$(TARGET)" --field work_dir)
TARGET_SNAPSHOT_DIR := $(shell python3 tools/analysis_target.py "$(TARGET)" --field snapshot_dir)
TARGET_INVENTORY_BASELINE := $(shell python3 tools/analysis_target.py "$(TARGET)" --field inventory_baseline)
TARGET_DECOMPILER_CORPUS := $(shell python3 tools/analysis_target.py "$(TARGET)" --field decompiler_corpus)
PROJECT_NAME := $(shell python3 tools/analysis_target.py "$(TARGET)" --field project_name)
PROGRAM_NAME := $(shell python3 tools/analysis_target.py "$(TARGET)" --field program_name)
PROJECT_DIR ?= $(CURDIR)/$(TARGET_WORK_DIR)
SNAPSHOT_DIR ?= $(CURDIR)/$(TARGET_SNAPSHOT_DIR)
override PROJECT_INVENTORY := $(BUILD_OUT)/targets/$(TARGET)/project_inventory.jsonl
override PROJECT_INVENTORY_BASELINE := $(CURDIR)/$(TARGET_INVENTORY_BASELINE)
endif

.PHONY: sync knowledge-index verify verify-core verify-full verify-local verify-one verify-changed verify-agent verify-exploit verify-required-external verify-external verify-corroboration verify-rfp verify-sleigh verify-processor verify-semantic-coverage-live verify-ghidra \
	ghidra-cli test-ghidra-cli \
	generate-dataflash generate-application-diagnostics generate-diagnostic-vocabulary generate-techstream-corpus \
	generate-application-receive-evidence generate-application-receive generate-application-transmit \
	generate-processor-fixture generate-function-discovery generate-semantic-coverage generate-project-inventory \
	generate-semantic-sweep generate-decompiler-corpus pseudocode \
	verify-project-parity update-project-baseline \
	rebuild-project work-project snapshot-project finalize-project build-init build-status clean-build

sync:
	$(UV) sync --locked

knowledge-index:
	$(PYTHON) tools/build_knowledge_index.py

build-init:
	$(PYTHON) tools/build_layout.py init

build-status:
	$(PYTHON) tools/build_layout.py status

# Safe default cleanup: transient logs and tmp only. Work/cache require an
# explicit tools/build_layout.py clean ... --force invocation.
clean-build:
	$(PYTHON) tools/build_layout.py clean logs tmp

# Build the vendored ghidra-cli (ghidra/ghidra-cli) into build/cache/ghidra-cli/.
ghidra-cli:
	tools/build_ghidra_cli.sh

# Complete portable verification for the vendored CLI. `--no-run` compile-checks
# every integration target; the remaining commands execute all Ghidra-free tests,
# including src/main.rs parser/safety tests that `--lib` alone would miss.
test-ghidra-cli:
	cargo test --locked --manifest-path ghidra/ghidra-cli/Cargo.toml --no-run
	cargo test --locked --manifest-path ghidra/ghidra-cli/Cargo.toml --lib
	cargo test --locked --manifest-path ghidra/ghidra-cli/Cargo.toml --bin ghidra
	cargo test --locked --manifest-path ghidra/ghidra-cli/Cargo.toml --test batch_tests

verify: verify-core

verify-core:
	$(PYTHON) tools/fast_verify.py --core

# Exhaustive portable gate: all tracked repository evidence, no ignored/external corpora.
verify-full:
	$(PYTHON) tools/fast_verify.py --full

# Local superset: portable full + available proprietary/external + live-project suites.
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
	$(PYTHON) tools/fast_verify.py --suite ephemeral_runtime_live_installer
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

verify-ghidra: verify-full verify-sleigh verify-processor verify-semantic-coverage-live verify-project-parity

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
	tools/export_ghidra_project.sh application-rx-signals

generate-application-receive: generate-application-receive-evidence
	$(PYTHON) tools/generate_application_rx_map.py

generate-application-transmit:
	$(PYTHON) tools/generate_application_tx_map.py

generate-processor-fixture:
	$(PYTHON) tools/build_processor_fixture.py

generate-function-discovery:
	tools/export_ghidra_project.sh outside-functions

generate-semantic-coverage:
	tools/export_ghidra_project.sh semantic-coverage

generate-semantic-sweep:
	$(PYTHON) tools/generate_semantic_sweep.py --project-dir "$(PROJECT_DIR)"

generate-decompiler-corpus:
ifeq ($(TARGET),$(DEFAULT_TARGET))
	$(PYTHON) tools/generate_decompiler_corpus.py --project-dir "$(PROJECT_DIR)"
else
	$(PYTHON) tools/generate_target_decompiler_corpus.py --target "$(TARGET)" --project-dir "$(PROJECT_DIR)" --output "$(CURDIR)/$(TARGET_DECOMPILER_CORPUS)"
endif

pseudocode:
	$(PYTHON) tools/pseudo --materialize

generate-project-inventory:
ifeq ($(TARGET),$(DEFAULT_TARGET))
	tools/export_ghidra_project.sh project-inventory "$(PROJECT_INVENTORY)"
else
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" PROJECT_DIR="$(PROJECT_DIR)" tools/export_ghidra_project.sh project-inventory "$(PROJECT_INVENTORY)"
endif

# Exact normalized parity: aggregate floors remain the fast collapse detector;
# this catches substitutions and metadata drift that equal totals cannot.
verify-project-parity:
ifeq ($(TARGET),$(DEFAULT_TARGET))
	tools/export_ghidra_project.sh project-inventory "$(PROJECT_INVENTORY)"
else
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" PROJECT_DIR="$(PROJECT_DIR)" tools/export_ghidra_project.sh project-inventory "$(PROJECT_INVENTORY)"
endif
	$(PYTHON) tools/project_inventory.py compare \
		"$(PROJECT_INVENTORY_BASELINE)" "$(PROJECT_INVENTORY)"

# Deliberately separate from ordinary verification. The baseline can only move
# when two independently rebuilt projects export byte-identical inventories.
update-project-baseline:
	@if [ -z "$(PROJECT_DIR_A)" ] || [ -z "$(PROJECT_DIR_B)" ]; then \
		echo "Usage: make update-project-baseline TARGET=$(TARGET) PROJECT_DIR_A=/abs/rebuild-a PROJECT_DIR_B=/abs/rebuild-b" >&2; \
		exit 2; \
	fi
	@if [ "$$($(PYTHON) -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$(PROJECT_DIR_A)")" = \
	      "$$($(PYTHON) -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$(PROJECT_DIR_B)")" ]; then \
		echo "PROJECT_DIR_A and PROJECT_DIR_B must be independent rebuilds" >&2; \
		exit 2; \
	fi
ifeq ($(TARGET),$(DEFAULT_TARGET))
	PROJECT_DIR="$(PROJECT_DIR_A)" tools/export_ghidra_project.sh project-inventory \
		"$(BUILD_OUT)/ghidra_project_inventory.rebuild-a.jsonl"
	PROJECT_DIR="$(PROJECT_DIR_B)" tools/export_ghidra_project.sh project-inventory \
		"$(BUILD_OUT)/ghidra_project_inventory.rebuild-b.jsonl"
	$(PYTHON) tools/project_inventory.py update \
		"$(BUILD_OUT)/ghidra_project_inventory.rebuild-a.jsonl" \
		"$(BUILD_OUT)/ghidra_project_inventory.rebuild-b.jsonl" \
		"$(PROJECT_INVENTORY_BASELINE)"
else
	@mkdir -p "$(BUILD_OUT)/targets/$(TARGET)"
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" PROJECT_DIR="$(PROJECT_DIR_A)" tools/export_ghidra_project.sh project-inventory \
		"$(BUILD_OUT)/targets/$(TARGET)/project_inventory.rebuild-a.jsonl"
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" PROJECT_DIR="$(PROJECT_DIR_B)" tools/export_ghidra_project.sh project-inventory \
		"$(BUILD_OUT)/targets/$(TARGET)/project_inventory.rebuild-b.jsonl"
	$(PYTHON) tools/project_inventory.py update \
		"$(BUILD_OUT)/targets/$(TARGET)/project_inventory.rebuild-a.jsonl" \
		"$(BUILD_OUT)/targets/$(TARGET)/project_inventory.rebuild-b.jsonl" \
		"$(PROJECT_INVENTORY_BASELINE)"
endif
	@echo "Updated $(PROJECT_INVENTORY_BASELINE); review before committing."

rebuild-project:
ifeq ($(TARGET),$(DEFAULT_TARGET))
	tools/rebuild_project.sh --project-dir "$(PROJECT_DIR)"
else
	tools/rebuild_target_project.sh --target "$(TARGET)" --project-dir "$(PROJECT_DIR)"
endif

# Materialize a gitignored working project from the registered committed snapshot.
# TARGET defaults to the canonical Sienna; non-default first-class targets resolve
# project/snapshot names through data/analysis_targets.json.
work-project:
	@if [ -d "$(PROJECT_DIR)/$(PROJECT_NAME).rep" ]; then \
		echo "Working project already exists: $(PROJECT_DIR)"; \
	else \
		echo "Materializing $(TARGET) working project from committed snapshot..."; \
		$(PYTHON) tools/project_layout.py materialize \
			--snapshot-dir "$(SNAPSHOT_DIR)" \
			--project-dir "$(PROJECT_DIR)" \
			--project-name "$(PROJECT_NAME)"; \
		echo "Ready: $(PROJECT_DIR)"; \
	fi
	@if [ -f "$(PROJECT_DIR)/processor_manifest.json" ]; then \
		$(PYTHON) tools/fingerprint_processor.py --source-only --expect "$(PROJECT_DIR)/processor_manifest.json"; \
	elif [ -f "$(SNAPSHOT_DIR)/processor_manifest.json" ]; then \
		$(PYTHON) tools/fingerprint_processor.py --source-only --expect "$(SNAPSHOT_DIR)/processor_manifest.json"; \
	else \
		echo "NOTE: no processor_manifest.json yet; run rebuild-project to create one"; \
	fi

snapshot-project:
ifeq ($(TARGET),$(DEFAULT_TARGET))
	tools/snapshot_project.sh --project-dir "$(PROJECT_DIR)" --snapshot-dir "$(SNAPSHOT_DIR)"
else
	tools/snapshot_target_project.sh --target "$(TARGET)" --project-dir "$(PROJECT_DIR)" $(if $(PARITY_PROJECT_DIR),--parity-project-dir "$(PARITY_PROJECT_DIR)",)
endif

# Deliberate end-of-session promotion. The default Sienna preserves the mature
# orchestration path; registered non-default targets stop their own daemon and
# then run target parity/corpus/snapshot promotion.
finalize-project:
ifeq ($(TARGET),$(DEFAULT_TARGET))
	tools/finalize_project.sh
else
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" GHIDRA_PROJECT="$(PROJECT_DIR)" tools/g stop || true
	tools/snapshot_target_project.sh --target "$(TARGET)" --project-dir "$(PROJECT_DIR)" $(if $(PARITY_PROJECT_DIR),--parity-project-dir "$(PARITY_PROJECT_DIR)",)
endif
