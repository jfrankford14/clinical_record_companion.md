.PHONY: test typecheck smoke-local-parse smoke-local-reconcile

SHELL := /bin/bash

test:
	pytest -q

typecheck:
	python -m compileall v2

smoke-local-parse:
	@if [ -z "$(INPUT)" ]; then echo "INPUT variable required" >&2; exit 1; fi
	@if [ -n "$(OUTPUT)" ]; then \
		scripts/local_parse.sh "$(INPUT)" "$(OUTPUT)"; \
	else \
		scripts/local_parse.sh "$(INPUT)"; \
	fi

smoke-local-reconcile:
	@if [ -z "$(A)" ] || [ -z "$(B)" ]; then echo "A and B variables required" >&2; exit 1; fi
	scripts/local_reconcile.sh "$(A)" "$(B)"
