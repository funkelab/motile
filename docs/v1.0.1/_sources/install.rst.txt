.. _sec_install:

Installation
============

.. automodule:: motile
   :noindex:

.. code-block:: bash

  pip install motile

This will install ``motile`` with all required dependencies, including the
`SCIP Optimizer <https://www.scipopt.org/>`_, a free and open source discrete
optimizer (via `ilpy <https://github.com/funkelab/ilpy>`_).

Gurobi (optional)
------------------

``motile`` also supports the `Gurobi Optimizer <https://www.gurobi.com/>`_, a
commercial solver that requires a valid license. Academic licenses are provided
for free, see `here
<https://www.gurobi.com/academia/academic-program-and-licenses/>`_ for how to
obtain one.

To install with Gurobi support:

.. code-block:: bash

  pip install motile[gurobi]

If ``motile`` finds a valid Gurobi license at runtime, it will use Gurobi;
otherwise it will fall back to SCIP.

Developers
----------

Developers can use `uv` for dependency management. See CONTRIBUTING.md for more
information.
