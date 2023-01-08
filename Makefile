default:
	pip install -r requirements.txt
	pip install .

install-dev:
	pip install -r requirements_dev.txt
	pip install -e .[full]

.PHONY: tests
tests:
	PY_MAJOR_VERSION=py`python -c 'import sys; print(sys.version_info[0])'` pytest -v --cov=motile --cov-config=.coveragerc tests
	flake8 motile
