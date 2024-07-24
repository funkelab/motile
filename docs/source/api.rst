.. _sec_api:

API Reference
=============

.. automodule:: motile
   :noindex:

.. admonition:: A note on ``NodeId`` and ``EdgeId`` types
  :class: note, dropdown

   The following types are used throughout the docs

   - All objects in a graph (both ``Nodes`` and ``Edges``) are represented as
     dictionaries mapping string attribute names to value. For example, a node
     might be ``{ "id": 1, "x": 0.5, "y": 0.5, "t": 0 }``

     ``GraphObject: TypeAlias = Mapping[str, Any]``

   - Node IDs may be integers, or a "meta-node" as a tuple of integers.

    ``NodeId: TypeAlias = Union[int, tuple[int, ...]]``

   - Edges IDs are tuples of ``NodeId``.

    ``EdgeId: TypeAlias = tuple[NodeId, ...]``

    - ``(0, 1)`` is an edge from node 0 to node 1.
    - ``((0,), (1, 2))`` is a hyperedge from node 0 to nodes 1 and 2 (i.e. a split).
    - ``((0, 1), 2)`` is a not a valid edge.



Track Graph
-----------

.. autoclass:: TrackGraph
  :members:

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

  .. autoclass:: Cost
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

Features
--------

  .. autoclass:: Features
    :members:


Weights
-------

Weight
^^^^^^

  .. autoclass:: Weight
     :members:

Weights
^^^^^^^

  .. autoclass:: Weights
    :members:

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
     :show-inheritance:

MaxParents
^^^^^^^^^^
  .. autoclass:: MaxParents
     :show-inheritance:

ExpressionConstraint
^^^^^^^^^^^^^^^^^^^^
  .. autoclass:: ExpressionConstraint
     :show-inheritance:

Pin
^^^
  .. autoclass:: Pin
     :show-inheritance:
