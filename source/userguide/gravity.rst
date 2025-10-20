Gravity
=======

Gravity in Dyablo can be solved in multiple ways. Essentially, when dealing with hydrodynamics variables (density :math:`\rho`, velocity :math:`\mathbf{u}` and energy :math:`E` in particular), gravity is included to the equations as 

.. math::

  \dfrac{\partial \rho\mathbf{u}}{\partial t} &= \rho \mathbf{g} \\
  \dfrac{\partial E}{\partial t} &= \rho\mathbf{u}\cdot\mathbf{g}

where :math:`\mathbf{g}` is the gravitational acceleration.

Gravitational acceleration can either be provided directly or derived from a potential.

Constant and static gravity
---------------------------

The simplest form of gravity is to apply a constant gravity over the whole domain by setting the value of :math:`\mathbf{g}` as a constant. This is done by setting the following parameters in your ``.ini`` file:

.. code-block :: ini

  [gravity]
  
  gravity_type=constant
  gx=...
  gy=...
  gz=...


Dynamic gravity
---------------

For problems requiring more advanced gravity, you can define a gravity solver that will calculate and store the gravitational acceleration as a field. In that case you will need to provide a solver in the ``solver`` parameter of the ``[gravity]`` section.

Available solvers are: 

.. doxygenpage:: gravity_solver_plugins
  :content-only:

Updating the hydrodynamics variables
-------------------------------------

The previous sections treat the way to calculate the gravitational acceleration :math:`\mathbf{g}`. Once the actual acceleration is computed, its effect needs to be integrated to the hydrodynamics variables. This is the role of the ``update`` variable in the ``[gravity]`` section. The update plugin will depend on your hyperbolic policy (see :doc:`equations`). Available gravity update plugins are: 

.. doxygenpage:: gravity_update_plugins
  :content-only: