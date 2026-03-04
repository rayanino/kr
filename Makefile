# خزانة ريان (KR) — Development Makefile

VENV    := .venv
PYTHON  := $(VENV)/bin/python
PIP     := $(VENV)/bin/pip

.PHONY: install test test-verbose clean help

help:          ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

install:       ## Create venv and install all dependencies
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip --quiet
	$(PIP) install -r requirements.txt --quiet
	@echo "✓ venv ready at $(VENV)/"
	@echo "  Activate: source $(VENV)/bin/activate"

test:          ## Run the full test suite
	$(PYTHON) -m pytest engines/*/tests/ shared/*/tests/ -q --tb=short

test-verbose:  ## Run tests with full output
	$(PYTHON) -m pytest engines/*/tests/ shared/*/tests/ -v

clean:         ## Remove venv and Python artifacts
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache
	@echo "✓ cleaned"
