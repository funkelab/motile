default:
	pip install .

install-dev:
	pip install -e .[full]

.PHONY: tests
tests:
	PY_MAJOR_VERSION=py`python -c 'import sys; print(sys.version_info[0])'` pytest -v --cov=motile --cov-config=.coveragerc tests
	flake8 motile

.PHONY: publish
publish:
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -rf build/ dist/ motile.egg-info/
