motile: Multi-Object Tracker using Integer Linear Equations
===========================================================

`motile` tracks multiple objects by solving a global optimization problem.

Installation
------------

`motile` requires [`pylp`](https://github.com/funkey/pylp) to create and solve
an Integer Linear Program. The recommended way of installing `motile` is thus
through `conda`:

```bash
conda create -n motile -c funkey pylp
conda activate motile
git clone https://github.com/funkelab/motile
cd motile
pip install .
```
