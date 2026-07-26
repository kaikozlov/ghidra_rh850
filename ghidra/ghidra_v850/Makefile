# Local Makefile for the vendored processor module.
# Prefer the repo-level targets:
#   make verify-sleigh
#   make verify-processor
#   make rebuild-project
#
# This file remains as a thin wrapper around the isolated installer.

ROOT := $(abspath ../..)
.PHONY: all clean install

all install:
	$(ROOT)/tools/install_v850_extension.sh

clean:
	rm -f data/languages/*.sla
