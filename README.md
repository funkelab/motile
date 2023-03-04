# motile: Multi-Object Tracker using Integer Linear Equations

[![codecov](https://codecov.io/gh/funkelab/motile/branch/main/graph/badge.svg)](https://codecov.io/gh/funkelab/motile)

`motile` tracks multiple objects by solving a global optimization problem.

Read all about it in the [documentation](https://funkelab.github.io/motile/).

## Installation

Motile depends on `ilpy`, which is currently only available via
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
