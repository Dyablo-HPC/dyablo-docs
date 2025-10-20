Timestep control
================

Every plugin related to computation might be subject to timestep control. Timestepping is controlled via the ``[dt]`` section in the ``.ini`` file. Each plugin takes at least a ``cfl`` parameter that corresponds to a limiting factor to maximize stability. The plugins to control the timestep can be declared using the ``dt_kernel`` parameter. 

.. warning :: 

  This section is incomplete yet.