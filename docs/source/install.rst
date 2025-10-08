.. _sec_install:

Installation
============

.. automodule:: motile
   :noindex:

.. code-block:: bash
   
  pip install motile

This will install ``motile`` with all required dependencies, including
two discrete optimizers:

1. The `Gurobi Optimizer <https://www.gurobi.com/>`_. This is a comercial
   solver, which requires a valid license. Academic licenses are provided for
   free, see `here
   <https://www.gurobi.com/academia/academic-program-and-licenses/>`_ for how
   to obtain one.

2. The `SCIP Optimizer <https://www.scipopt.org/>`_, a free and open source
   solver. If ``motile`` does not find a valid Gurobi license it will fall
   back to using SCIP.

Developers can use `uv` for dependency management. See CONTRIBUTING.md for more
information.