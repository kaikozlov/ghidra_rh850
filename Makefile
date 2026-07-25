PYTHON ?= python3

VERIFY_SUITES := \
	tests/verify_findings.py \
	tests/verify_payload_gate.py \
	tests/verify_secoc_nvm.py \
	tests/verify_dataflash_layout.py \
	tests/verify_did_model.py \
	tests/verify_can_transport.py

.PHONY: verify generate-dataflash

verify:
	@set -e; for suite in $(VERIFY_SUITES); do \
		echo "==> $$suite"; \
		$(PYTHON) "$$suite"; \
		echo; \
	done

generate-dataflash:
	$(PYTHON) tools/generate_dataflash_layout.py
