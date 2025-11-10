default:
	uv sync --no-dev

install-dev:
	uv sync

.PHONY: tests
tests:
	uv run pytest -v --cov=motile --cov-report=term-missing
	uv run pre-commit run --all-files

.PHONY: docs
docs:
	uv run make -C docs html

.PHONY: docs-watch
docs-watch:
	uv run sphinx-autobuild docs/source docs/_build/html --watch motile --watch docs/source --open-browser
