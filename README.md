# motile: Multi-Object Tracker using Integer Linear Equations

[![License](https://img.shields.io/pypi/l/motile.svg)](https://github.com/funkelab/motile/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/motile.svg)](https://pypi.org/project/motile)
[![CI](https://github.com/funkelab/motile/actions/workflows/ci.yaml/badge.svg)](https://github.com/funkelab/motile/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/funkelab/motile/branch/main/graph/badge.svg)](https://codecov.io/gh/funkelab/motile)

`motile` tracks multiple objects by solving a global optimization problem.

Read all about it in the [documentation](https://funkelab.github.io/motile/).

## Installation

Motile depends on [`ilpy`](https://github.com/funkelab/ilpy), which is currently only available via
conda on the `funkelab` channel.  `ilpy` in turn requires
gurobi which is only available via the `gurobi` channel.

So, to create a new environment with motile:

```bash
conda create -n my_env -c conda-forge -c funkelab -c gurobi ilpy
conda activate my_env
pip install motile
```

or, to install into an existing environment:

```bash
conda install -c conda-forge -c funkelab -c gurobi ilpy
pip install motile
```

## Development

```sh
git clone https://github.com/funkelab/motile  # or your fork
cd motile

# currently required to build ilpy dependency wheel
conda install scip

pip install -e .[dev]
```

### Testing

```sh
pytest
```

### Deployment

> note for developers

To deploy a new version, first make sure to bump the version string in
`motile/__init__.py`.  Then create an **annotated** tag, and push it to github.
This will trigger the `deploy.yaml` workflow to upload to PyPI

```bash
git tag -a vX.Y.Z -m vX.Y.Z
git push upstream --follow-tags
```

### Building Documentation

```sh
pip install -e .[docs]
make docs && open docs/_build/html/index.html

# or to start a live-reloading server
make docs-watch
```
