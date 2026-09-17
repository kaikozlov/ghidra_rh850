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
DEFAULT_TARGET := $(shell python3 -c 'import json; print(json.load(open("data/analysis_targets.json"))["default_target"])')
TARGET ?= $(DEFAULT_TARGET)
LEGACY_SIENNA_TARGET := sienna-8965B4512000
LEGACY_SIENNA_WORK_DIR := $(shell python3 tools/project/analysis_target.py "$(LEGACY_SIENNA_TARGET)" --field work_dir)
LEGACY_SIENNA_PROJECT_DIR := $(CURDIR)/$(LEGACY_SIENNA_WORK_DIR)
TARGET_WORK_DIR := $(shell python3 tools/project/analysis_target.py "$(TARGET)" --field work_dir)
TARGET_SNAPSHOT_DIR := $(shell python3 tools/project/analysis_target.py "$(TARGET)" --field snapshot_dir)
TARGET_INVENTORY_BASELINE := $(shell python3 tools/project/analysis_target.py "$(TARGET)" --field inventory_baseline)
TARGET_DECOMPILER_CORPUS := $(shell python3 tools/project/analysis_target.py "$(TARGET)" --field decompiler_corpus)
PROJECT_NAME := $(shell python3 tools/project/analysis_target.py "$(TARGET)" --field project_name)
PROGRAM_NAME := $(shell python3 tools/project/analysis_target.py "$(TARGET)" --field program_name)
TARGET_WORK_SUFFIX := $(patsubst build/work/%,%,$(TARGET_WORK_DIR))
PROJECT_DIR ?= $(BUILD_WORK)/$(TARGET_WORK_SUFFIX)
SNAPSHOT_DIR ?= $(CURDIR)/$(TARGET_SNAPSHOT_DIR)
# Canonical parity paths are not command-line overrides: allowing the current
# output to alias the tracked baseline would turn verification into self-compare.
override PROJECT_INVENTORY_BASELINE := $(CURDIR)/$(TARGET_INVENTORY_BASELINE)
ifeq ($(TARGET),$(LEGACY_SIENNA_TARGET))
override PROJECT_INVENTORY := $(BUILD_OUT)/ghidra_project_inventory.jsonl
else
override PROJECT_INVENTORY := $(BUILD_OUT)/targets/$(TARGET)/project_inventory.jsonl
endif

.PHONY: sync verify verify-core verify-full verify-local verify-agent verify-required-external verify-external verify-corroboration verify-rfp verify-sleigh verify-processor verify-semantic-coverage-live verify-ghidra \
	ghidra-cli test-ghidra-cli \
	generate-dataflash generate-application-diagnostics generate-diagnostic-vocabulary generate-techstream-corpus \
	generate-application-receive-evidence generate-application-receive generate-application-transmit \
	generate-processor-fixture generate-function-discovery generate-semantic-coverage generate-project-inventory \
	generate-semantic-sweep generate-decompiler-corpus pseudocode \
	verify-project-parity update-project-baseline \
	rebuild-project work-project snapshot-project finalize-project build-init build-status clean-build

sync:
	$(UV) sync --locked

build-init:
	$(PYTHON) tools/project/build_layout.py init

build-status:
	$(PYTHON) tools/project/build_layout.py status

# Safe default cleanup: transient logs and tmp only. Work/cache require an
# explicit tools/project/build_layout.py clean ... --force invocation.
clean-build:
	$(PYTHON) tools/project/build_layout.py clean logs tmp

# Build the vendored ghidra-cli (ghidra/ghidra-cli) into build/cache/ghidra-cli/.
ghidra-cli:
	tools/project/build_ghidra_cli.sh

# Complete portable verification for the vendored CLI. `--no-run` compile-checks
# every integration target; the remaining commands execute all Ghidra-free tests,
# including src/main.rs parser/safety tests that `--lib` alone would miss.
test-ghidra-cli:
	cargo test --locked --manifest-path ghidra/ghidra-cli/Cargo.toml --no-run
	cargo test --locked --manifest-path ghidra/ghidra-cli/Cargo.toml --lib
	cargo test --locked --manifest-path ghidra/ghidra-cli/Cargo.toml --bin ghidra
	cargo test --locked --manifest-path ghidra/ghidra-cli/Cargo.toml --test batch_tests

verify:
	tools/test core

verify-core:
	tools/test core

# Exhaustive portable gate: all tracked repository evidence, no ignored/external corpora.
verify-full:
	tools/test full

# Local superset: portable full + available proprietary/external + live-project suites.
verify-local:
	tools/test local

verify-agent:
	tools/test --agent

verify-required-external:
	tools/test --required-external

verify-external verify-corroboration:
	$(PYTHON) tests/verify_external_corroboration.py --repos-dir "$(EXTERNAL_REPOS_DIR)"

verify-rfp:
	$(PYTHON) tests/verify_renesas_rfp.py --require-package

verify-sleigh:
	tools/testing/processor/verify_sleigh.sh

verify-processor:
	tools/testing/processor/verify_processor.sh

# Full local gate: firmware suites + SLEIGH + processor audits + exact parity.
verify-semantic-coverage-live:
	$(PYTHON) tests/verify_semantic_coverage_live.py --project-dir "$(PROJECT_DIR)"

verify-ghidra: verify-full verify-sleigh verify-processor verify-semantic-coverage-live verify-project-parity

generate-dataflash:
	$(PYTHON) tools/firmware/generate_dataflash_layout.py
	$(PYTHON) tools/firmware/generate_checkpoint_payload_map.py

generate-application-diagnostics:
	$(PYTHON) tools/firmware/generate_application_diagnostic_map.py

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

# These global artifacts predate the target registry and are Sienna-owned. Keep
# them explicitly pinned so changing the registry default cannot retarget them.
generate-application-receive-evidence:
	GHIDRA_ANALYSIS_TARGET="$(LEGACY_SIENNA_TARGET)" PROJECT_DIR="$(LEGACY_SIENNA_PROJECT_DIR)" tools/project/export_ghidra_project.sh application-rx-signals

generate-application-receive: generate-application-receive-evidence
	$(PYTHON) tools/firmware/generate_application_rx_map.py

generate-application-transmit:
	$(PYTHON) tools/firmware/generate_application_tx_map.py

generate-processor-fixture:
	$(PYTHON) tools/testing/processor/build_processor_fixture.py

generate-function-discovery:
	GHIDRA_ANALYSIS_TARGET="$(LEGACY_SIENNA_TARGET)" PROJECT_DIR="$(LEGACY_SIENNA_PROJECT_DIR)" tools/project/export_ghidra_project.sh outside-functions

generate-semantic-coverage:
	GHIDRA_ANALYSIS_TARGET="$(LEGACY_SIENNA_TARGET)" PROJECT_DIR="$(LEGACY_SIENNA_PROJECT_DIR)" tools/project/export_ghidra_project.sh semantic-coverage

generate-semantic-sweep:
	$(PYTHON) tools/project/generate_semantic_sweep.py --project-dir "$(LEGACY_SIENNA_PROJECT_DIR)"

generate-decompiler-corpus:
ifeq ($(TARGET),$(LEGACY_SIENNA_TARGET))
	$(PYTHON) tools/project/generate_decompiler_corpus.py --project-dir "$(PROJECT_DIR)"
else
	$(PYTHON) tools/project/generate_target_decompiler_corpus.py --target "$(TARGET)" --project-dir "$(PROJECT_DIR)" --output "$(CURDIR)/$(TARGET_DECOMPILER_CORPUS)"
endif

pseudocode:
	$(PYTHON) tools/pseudo --target "$(TARGET)" --materialize

generate-project-inventory:
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" PROJECT_DIR="$(PROJECT_DIR)" tools/project/export_ghidra_project.sh project-inventory "$(PROJECT_INVENTORY)"

# Exact normalized parity: aggregate floors remain the fast collapse detector;
# this catches substitutions and metadata drift that equal totals cannot.
verify-project-parity:
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" PROJECT_DIR="$(PROJECT_DIR)" tools/project/export_ghidra_project.sh project-inventory "$(PROJECT_INVENTORY)"
	$(PYTHON) tools/project/project_inventory.py compare \
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
ifeq ($(TARGET),$(LEGACY_SIENNA_TARGET))
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" PROJECT_DIR="$(PROJECT_DIR_A)" tools/project/export_ghidra_project.sh project-inventory \
		"$(BUILD_OUT)/ghidra_project_inventory.rebuild-a.jsonl"
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" PROJECT_DIR="$(PROJECT_DIR_B)" tools/project/export_ghidra_project.sh project-inventory \
		"$(BUILD_OUT)/ghidra_project_inventory.rebuild-b.jsonl"
	$(PYTHON) tools/project/project_inventory.py update \
		"$(BUILD_OUT)/ghidra_project_inventory.rebuild-a.jsonl" \
		"$(BUILD_OUT)/ghidra_project_inventory.rebuild-b.jsonl" \
		"$(PROJECT_INVENTORY_BASELINE)"
else
	@mkdir -p "$(BUILD_OUT)/targets/$(TARGET)"
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" PROJECT_DIR="$(PROJECT_DIR_A)" tools/project/export_ghidra_project.sh project-inventory \
		"$(BUILD_OUT)/targets/$(TARGET)/project_inventory.rebuild-a.jsonl"
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" PROJECT_DIR="$(PROJECT_DIR_B)" tools/project/export_ghidra_project.sh project-inventory \
		"$(BUILD_OUT)/targets/$(TARGET)/project_inventory.rebuild-b.jsonl"
	$(PYTHON) tools/project/project_inventory.py update \
		"$(BUILD_OUT)/targets/$(TARGET)/project_inventory.rebuild-a.jsonl" \
		"$(BUILD_OUT)/targets/$(TARGET)/project_inventory.rebuild-b.jsonl" \
		"$(PROJECT_INVENTORY_BASELINE)"
endif
	@echo "Updated $(PROJECT_INVENTORY_BASELINE); review before committing."

rebuild-project:
ifeq ($(TARGET),$(LEGACY_SIENNA_TARGET))
	tools/project/rebuild_project.sh --project-dir "$(PROJECT_DIR)"
else
	tools/project/rebuild_target_project.sh --target "$(TARGET)" --project-dir "$(PROJECT_DIR)"
endif

# Materialize a gitignored working project from the registered committed snapshot.
# TARGET defaults to the registry primary (Camry); every target resolves
# project/snapshot names through data/analysis_targets.json.
work-project:
	@if [ -d "$(PROJECT_DIR)/$(PROJECT_NAME).rep" ]; then \
		echo "Working project already exists: $(PROJECT_DIR)"; \
	else \
		echo "Materializing $(TARGET) working project from committed snapshot..."; \
		$(PYTHON) tools/project/project_layout.py materialize \
			--snapshot-dir "$(SNAPSHOT_DIR)" \
			--project-dir "$(PROJECT_DIR)" \
			--project-name "$(PROJECT_NAME)"; \
		echo "Ready: $(PROJECT_DIR)"; \
	fi
	@if [ -f "$(PROJECT_DIR)/processor_manifest.json" ]; then \
		$(PYTHON) tools/project/fingerprint_processor.py --source-only --expect "$(PROJECT_DIR)/processor_manifest.json"; \
	elif [ -f "$(SNAPSHOT_DIR)/processor_manifest.json" ]; then \
		$(PYTHON) tools/project/fingerprint_processor.py --source-only --expect "$(SNAPSHOT_DIR)/processor_manifest.json"; \
	else \
		echo "NOTE: no processor_manifest.json yet; run rebuild-project to create one"; \
	fi

snapshot-project:
ifeq ($(TARGET),$(LEGACY_SIENNA_TARGET))
	tools/project/snapshot_project.sh --project-dir "$(PROJECT_DIR)" --snapshot-dir "$(SNAPSHOT_DIR)"
else
	tools/project/snapshot_target_project.sh --target "$(TARGET)" --project-dir "$(PROJECT_DIR)" $(if $(PARITY_PROJECT_DIR),--parity-project-dir "$(PARITY_PROJECT_DIR)",)
endif

# Deliberate end-of-session promotion. Legacy Sienna preserves its mature
# orchestration path; staged targets stop their own daemon and then run
# target parity/corpus/snapshot promotion.
finalize-project:
ifeq ($(TARGET),$(LEGACY_SIENNA_TARGET))
	tools/project/finalize_project.sh
else
	GHIDRA_ANALYSIS_TARGET="$(TARGET)" GHIDRA_PROJECT="$(PROJECT_DIR)" tools/g stop || true
	tools/project/snapshot_target_project.sh --target "$(TARGET)" --project-dir "$(PROJECT_DIR)" $(if $(PARITY_PROJECT_DIR),--parity-project-dir "$(PARITY_PROJECT_DIR)",)
endif
