.. _sec_api:

API Reference
=============

.. automodule:: motile
   :noindex:

Track Graph
-----------

.. autoclass:: TrackGraph
  :members: get_frames, nodes_by_frame

Solver
------

.. autoclass:: Solver
  :members:

Variables
---------

Solver variables are introduced by inheriting from the following abstract base class:

.. automodule:: motile.variables

  .. autoclass:: Variable
    :members:

The following lists all variables that are already implemented in ``motile``.

NodeSelected
^^^^^^^^^^^^
  .. autoclass:: NodeSelected

EdgeSelected
^^^^^^^^^^^^
  .. autoclass:: EdgeSelected

NodeAppear
^^^^^^^^^^
  .. autoclass:: NodeAppear

NodeSplit
^^^^^^^^^
  .. autoclass:: NodeSplit

Costs
-----

All costs inherit from the following base class:

.. automodule:: motile.costs

  .. autoclass:: Costs
    :members:

The following lists all costs that are already implemented in ``motile``.

Appear
^^^^^^
  .. autoclass:: Appear

EdgeSelection
^^^^^^^^^^^^^
  .. autoclass:: EdgeSelection

NodeSelection
^^^^^^^^^^^^^
  .. autoclass:: NodeSelection

Split
^^^^^
  .. autoclass:: Split

EdgeDistance
^^^^^^^^^^^^
  .. autoclass:: EdgeDistance

Constraints
-----------

All constraints inherit from the following base class:

.. automodule:: motile.constraints

  .. autoclass:: Constraint
    :members:

The following lists all constraints that are already implemented in ``motile``.

MaxChildren
^^^^^^^^^^^
  .. autoclass:: MaxChildren

MaxParents
^^^^^^^^^^
  .. autoclass:: MaxParents

Pin
^^^
  .. autoclass:: Pin

SelectEdgeNodes (internal use)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  .. autoclass:: SelectEdgeNodes
