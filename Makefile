# ESBMC-Python verification for GoogleChrome/related-website-sets.
#
# Usage:
#   make verify              # both phases on every target
#   make phase1              # functional contracts only
#   make verify-only T=<name>
#
# Override ESBMC binary: make verify ESBMC=/path/to/esbmc

ESBMC  ?= esbmc
PYTHON ?= python3

.PHONY: verify phase1 phase2 verify-only check-esbmc

verify: check-esbmc
	$(PYTHON) verify.py --phase all

phase1: check-esbmc
	$(PYTHON) verify.py --phase 1

phase2: check-esbmc
	$(PYTHON) verify.py --phase 2

verify-only: check-esbmc
	@test -n "$(T)" || (echo "usage: make verify-only T=<target>" && exit 2)
	$(PYTHON) verify.py --only $(T)

check-esbmc:
	@command -v $(ESBMC) >/dev/null || { \
	  echo "ESBMC not found (set ESBMC=/path/to/esbmc)"; exit 1; }
