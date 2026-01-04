.DEFAULT_GOAL := help

PYTHON := python
UV := uv
PRE_COMMIT := pre-commit

SRC := backend

# =========================
# INSTALLATION
# =========================

install:
	$(UV) pip install --system -r requirements.txt

install-dev:
	$(UV) pip install --system -r requirements.txt -r requirements-dev.txt
	$(PRE_COMMIT) install

# =========================
# QUALITÉ DE CODE
# =========================

lint:
	$(PRE_COMMIT) run --all-files

format:
	black $(SRC)
	isort $(SRC)

# =========================
# TESTS
# =========================

test:
	pytest $(SRC) -v -s

test-fast:
	pytest $(SRC) -q

# =========================
# CI
# =========================

ci:
	make install
	make test

ci-full:
	make install-dev
	make lint
	make test

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make install       Install production dependencies"
	@echo "  make install-dev   Install dev dependencies"
	@echo "  make lint          Run linters (pre-commit)"
	@echo "  make format        Format code (black + isort)"
	@echo "  make test          Run test suite"
	@echo "  make ci            CI pipeline (fast)"
	@echo "  make ci-full       CI pipeline (full checks)"
