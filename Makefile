.DEFAUTL_GOAL := help
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
	$(PRE_COMMIT) run isort --all-files
	$(PRE_COMMIT) run yapf --all-files

# =========================
# TESTS
# =========================

test:
	pytest $(SRC) -v

# =========================
# CI (entrypoint unique)
# =========================

ci:
	make install-dev
	make lint
	make test


help:
	@echo "Available commands:"
	@echo "  make install       Install prod deps"
	@echo "  make install-dev   Install dev deps"
	@echo "  make lint          Run linters"
	@echo "  make test          Run tests"
	@echo "  make ci            Run CI pipeline"
