Equations
=========

General considerations
----------------------

Dyablo has originally been written to simulate astrophysical plasmas with the finite-volume method. This Eulerian approach solves equations for fields discretized on a grid. The most basic system of equations solved by Dyablo are conservative equations of the form: 

.. math::

  \dfrac{\partial\mathbf{U}}{\partial t} + \nabla \cdot \mathbf{F}(\mathbf{U}) = \mathbf{S}(\mathbf{U})

where :math:`\mathbf{U}` is a vector of conserved variables, :math:`\mathbf{F}` a conservative flux depending on the conserved variables vector and :math:`\mathbf{S}` a source term.

The code separates the resolution of this equation in three parts: 

1. The hyperbolic part: :math:`\dfrac{\partial\mathbf{U}}{\partial t} + \nabla \cdot \mathbf{F}(\mathbf{U}) = 0`.
2. The cell-centered source terms: :math:`\dfrac{\partial\mathbf{U}}{\partial t} = \mathbf{S}_{cell}(\mathbf{U})`
3. The parabolic source terms that are not cell-centered: :math:`\dfrac{\partial\mathbf{U}}{\partial t} = \mathbf{S}_{parabolic}(\mathbf{U})`

For gravity runs, the Poisson equation is also included: 

.. math::

  \Delta \phi = 4\pi G \rho

with :math:`\rho` the density, :math:`\phi` the gravitational potential and :math:`G` the gravitational constant. See :doc:`gravity` for more info.

The combination of all the terms above is done using operator splitting. Each term is resolved in a separate plugin to allow for more modularity of the code.

Hyperbolic terms
----------------

The hyperbolic terms are solved using a godunov-like method. The resolution of the hyperbolic terms combine two aspects: 

* a **policy** which describes the equations: a conservative state, a primitive state, an equation of state, a flux solver, boundary conditions, etc.
* a **scheme** which will update the equations in an explicit discrete form.

For instance, the most basic policy in Dyablo is the **hydrodynamics** policy which solves the Euler equations : 

.. math ::

  \mathbf{U} = \begin{bmatrix}
        \rho \\
        \rho\mathbf{u} \\
        E
        \end{bmatrix}
  \hspace{0.5cm}
  \mathbf{F}(\mathbf{U}) = 
  \begin{bmatrix}
      \rho \mathbf{u} \\
      \rho \mathbf{u}\otimes\bm{u} + \mathbb{I}P \\
      (E+P)\mathbf{u}
  \end{bmatrix}

The policy includes the flux calculation, which, in this precise case, is done using the `HLLC`_ solver. Boundary conditions, by default include *absorbing*, *periodic* and *reflecting* conditions. The policy also defined the closure of the equations, and in the hydrodynamics case, uses an ideal gas equation of state to link the internal energy density to the pressure.

.. _HLLC: https://link.springer.com/article/10.1007/s00193-019-00912-4

The scheme in itself is what will evolve the status of the variables at an iteration (:math:`n`) to the next (:math:`n+1`). For instance, by default in Dyablo, you can use the Euler method: 

.. math ::

  \mathbf{U}^{n+1} = \mathbf{U}^n + \Delta t^n\mathcal{L}(\mathbf{U}^n)

for a time-step at current iteration :math:`\Delta t^n`, and an evolution operator :math:`\mathcal{L}` depending on the conserved state at the current iteration.

Likewise, you could use the `2nd order strong-stability preserving Runge-Kutta`_ scheme, which would then evolve the variables as the following: 

.. _2nd order strong-stability preserving Runge-Kutta: https://www.ams.org/journals/mcom/1998-67-221/S0025-5718-98-00913-2/S0025-5718-98-00913-2.pdf

.. math ::

  \mathbf{U}^* &= \mathbf{U}^n + \Delta t^n\mathcal{L}(\mathbf{U}^n) \\
  \mathbf{U}^{**} &= \mathbf{U}^* + \Delta t^n\mathcal{L}(\mathbf{U}^*) \\
  \mathbf{U}^{n+1} &= \dfrac{1}{2}(\mathbf{U}^n + \mathbf{U}^{**})


``.ini`` file parameters:
^^^^^^^^^^^^^^^^^^^^^^^^^

The hyperbolic solver is declared in the ``[hydro]`` section and paired with the ``update`` key. Every hyperbolic solver is going to have their own parameters that will be read from the ``.ini`` file so please refer to the documentation of each policy and scheme.

.. doxygenpage:: hyperbolic_update_plugins
  :content-only:



Parabolic terms
---------------

.. warning::
  The parabolic source term will be refactored into source-terms later in the development of Dyablo. 

Parabolic source terms can also be applied. Parabolic terms include viscosity and thermal conduction. They are splitted from the hyperbolic and source updates, and are applied a first order in time explicit operator. The parabolic plugins do not create fields for Dyablo so their usage is conditioned to specific hyperbolic policies.

Viscosity
^^^^^^^^^

The viscosity operator acts on two variables: the momentum (:math:`\rho\mathbf{u}`) and the total energy (:math:`E`). The plugin applies the following treatment to the variables:

.. math ::

  \dfrac{\partial \rho\mathbf{u}}{\partial t} &= -\nabla\cdot(\mathbf{\tau}) \\
  \dfrac{\partial E}{\partial t} &= -\nabla\cdot(\mathbf{\tau}\cdot\mathbf{u})

with :math:`\mathbf{\tau}` the viscosity stress tensor whose components are defined as 

.. math ::

  \tau_{ij} = \mu \left(\dfrac{\partial u_i}{\partial x_j} + \dfrac{\partial u_j}{\partial x_i} - \dfrac{2}{3}(\delta_i^j \nabla\cdot\mathbf{u})\right)

where :math:`\mu` is the bulk viscosity diffusion coefficient and :math:`\delta_i^j` the Kroenecker delta operator.

``.ini`` parameters:
####################


.. warning :: 

  This section is incomplete yet.



Thermal conduction
^^^^^^^^^^^^^^^^^^


.. warning :: 

  This section is incomplete yet.

Other source terms
------------------

The rest of the source terms are splitted and applied in turn. 

``.ini`` parameters:
####################

Each source term has its own set of parameters. Multiple source terms can be applied in the order they are declared in the ``.ini`` file:

.. code-block :: ini

  [source_terms]
  updates=SourcePlugin1,SourcePlugin2,SourcePlugin3

The source plugins the can be used are the following: 

.. doxygenpage:: source_plugins
  :content-only: