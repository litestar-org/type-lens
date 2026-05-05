.DEFAULT_GOAL := help

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: install
install:												## Run tests
	uv sync --all-groups

.PHONY: test
test:												## Run tests
	uv run --group test pytest tests

.PHONY: test-all
test-all:											## Run all tests including examples
	uv run --group test pytest tests docs/examples

.PHONY: format
format:												## Format code with ruff
	uv run --group lint ruff format .
	uv run --group lint ruff check --fix .

.PHONY: lint
lint:												## Run all linting
	uv run --group lint ruff check .
	uv run --group lint ruff format --check .
	uv run --group lint mypy
	uv run --group lint pyright
	uv run --group lint slotscheck type_lens

##@ Docs

.PHONY: docs
docs:												## Build docs
	uv run --group docs sphinx-build -M html docs docs/_build/ -E -a -j auto -W --keep-going

.PHONY: docs-serve
docs-serve:											## Serve docs locally
	uv run --group docs sphinx-autobuild docs docs/_build/ -j auto --watch type_lens --watch docs --watch tests --watch CONTRIBUTING.rst --port 8002
