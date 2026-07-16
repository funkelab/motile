.. _sec_api:

API Reference
=============

.. automodule:: motile
   :noindex:

.. admonition:: A note on ``Node`` and ``Edge`` types
  :class: note, dropdown

   The following types are used throughout the docs

   - Nodes are integers

    ``Node: TypeAlias = int``

   - Edges are 2-tuples of ``Node``.

    ``Edge: TypeAlias = tuple[Node, Node]``

    Example: ``(0, 1)`` is an edge from node 0 to node 1.

   - All attributes in a graph (for both ``Node``\ s and ``Edge``\ s) are
     dictionaries mapping string attribute names to values. For example, a
     node's attributes might be ``{ "x": 0.5, "y": 0.5, "t": 0 }``

     ``Attributes: TypeAlias = Mapping[str, Any]``



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

Node Variables
^^^^^^^^^^^^^^

.. autoclass:: NodeSelected

.. autoclass:: NodeSplit

.. autoclass:: NodeMerge

.. autoclass:: NodeAppear

.. autoclass:: NodeDisappear

Edge Variables
^^^^^^^^^^^^^^

.. autoclass:: EdgeSelected

.. autoclass:: EdgeContinuation

.. autoclass:: EdgeSplit

.. autoclass:: EdgeMerge

Edge Pair Variables
^^^^^^^^^^^^^^^^^^^

.. autoclass:: EdgeSplitPair

.. autoclass:: EdgeMergePair

Costs
-----

All costs inherit from the following base class:

.. automodule:: motile.costs

  .. autoclass:: Cost
    :members:

The following lists all costs that are already implemented in ``motile``.

Node Costs
^^^^^^^^^^

.. autoclass:: NodeSelectedCost

.. autoclass:: NodeSplitCost

.. autoclass:: NodeMergeCost

.. autoclass:: NodeAppearCost

.. autoclass:: NodeDisappearCost

Edge Costs
^^^^^^^^^^

.. autoclass:: EdgeSelectedCost

.. autoclass:: EdgeDistanceCost

.. autoclass:: EdgeSplitCost

.. autoclass:: EdgeMergeCost

Edge Pair Costs
^^^^^^^^^^^^^^^

.. autoclass:: SymmetricSplitCost

.. autoclass:: SymmetricMergeCost

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
