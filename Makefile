default:
	pip install .

install-dev:
	pip install -e .[dev]

.PHONY: tests
tests:
	uv run pytest -v --cov=motile --cov-config=.coveragerc tests
	uv run pre-commit run --all-files

.PHONY: publish
publish:
	python -m build
	twine upload dist/*
	rm -rf build/ dist/ motile.egg-info/

.PHONY: docs
docs:
	uv run make -C docs html

.PHONY: docs-watch
docs-watch:
	uv run sphinx-autobuild docs/source docs/_build/html --watch motile --watch docs/source --open-browser
