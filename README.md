# motile: Multi-Object Tracker using Integer Linear Equations

`motile` tracks multiple objects by solving a global optimization problem.

Read all about it in the [documentation](https://funkelab.github.io/motile/).

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
