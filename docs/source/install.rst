.. _sec_install:

Installation
============

.. automodule:: motile
   :noindex:

.. code-block:: bash

  conda create -n motile -c conda-forge -c gurobi -c funkelab ilpy
  conda activate motile
  pip install motile

This will install ``motile`` with all required dependencies, including binaries
for two discrete optimizers:

1. The `Gurobi Optimizer <https://www.gurobi.com/>`_. This is a comercial
   solver, which requires a valid license. Academic licenses are provided for
   free, see `here
   <https://www.gurobi.com/academia/academic-program-and-licenses/>`_ for how
   to obtain one.

2. The `SCIP Optimizer <https://www.scipopt.org/>`_, a free and open source
   solver. If ``motile`` does not find a valid Gurobi license, it will fall
   back to using SCIP.

Do I have to use ``conda``?
---------------------------

Kinda. ``motile`` uses `ilpy <https://github.com/funkelab/ilpy>`_ to solve the
optimization problem. Conda packages for ``ilpy`` are available for all major
platforms, linking against the conda packages for SCIP and Gurobi.

It is possible to not use ``conda``: If you have SCIP or Gurobi installed
otherwise, you can compile ``ilpy`` yourself from the PyPI repository (``pip
install ilpy``).
