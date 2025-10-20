IOs
===

Dyablo has two types of outputs:

* **Snapshots** which are outputs meant for visualization and analysis
* **Restarts** which are meant for restarting the code after stopping or failing.

Snapshots
---------

Snapshots are the main outputs of Dyablo. They are to be used for visualization and analysis. Every time a snapshot has to be written to the disk, Dyablo writes two files, an ``.h5`` file that holds the data and an ``.xmf`` file that holds the structure. These two files represent the fields stored on the grid. Additional couples of files are written per particle family. So if your run has two particle families, each snapshot will be six files (three ``.xmf`` and three ``.h5`` files).

The fields available will depend on the plugins activated for the run. But any permanently stored field is available for outputs. On top of the physical fields, a few annex fields are available : 

* ``ioct`` the id of the octant for each cell
* ``rank`` the MPI rank holding the cell
* ``level`` the AMR level of the cell (ie of the octant holding the cell)

The ``.xmf`` file can be read by most scientific visualization software such as Paraview_ [the recommended choice] or VisIt_. Additionally, you can use Pyablo_ to read the snapshots and analyze them with Python.

.. _Paraview: https://www.paraview.org/

.. _VisIt: https://visit-dav.github.io/visit-website/index.html

.. _Pyablo: https://github.com/Dyablo-HPC/Pyablo

While writing the snapshots to the disk, Dyablo also maintains a ``_main`` file that stores the time series of all the snapshots in the run, allowing you to visualize the simulation as a whole.

``.ini`` file parameters
^^^^^^^^^^^^^^^^^^^^^^^^

The parameters for writing snapshots are distributed in two sections in the ``.ini`` file: 

.. code-block :: ini

  [run]
  # This should be on by default
  enable_outputs=on

  # How many iterations between each snapshot
  output_frequency=1

  # Alternatively, you can give a simulation time between two snapshots
  output_timeslice=0.1

  [output]
  # Precision of the outputs, can be float or double
  output_real_type     = float

  # Filenames and directories
  outputdir            = ./                  
  outputprefix         = prefix_to_be_added_to_output_filenames 

  # The list of fields/particles to write to the file
  write_variables          = field1,field2,field3,...
  write_particle_variables = family1/var1,family1/var2,family2/var1, ... 

Derived fields
^^^^^^^^^^^^^^

On top of the field variables that are stored on the grid, Dyablo exposes *Derived fields*, ie fields that are not variables of the problem per-se, but can be computed right before the outputs and stored to the disk. For example, a derived field can be the divergence of the magnetic-field, or the Mach number. Both are not variables of the problem but are important quantities.

Derived fields are given to the ``.ini`` file in the ``[output]`` section : 

.. code-block ::
  
  [output]
  derived_fields=DerivedFieldPlugin1,DerivedFieldPlugin2

The fields created by the plugins will be automatically added to the ``.xmf`` and ``.h5`` files.

The available DerivedFields plugins are the following: 

.. doxygenpage:: derived_fields_plugins
  :content-only:

Restarts
--------

The other type of outputs written by Dyablo are restarts/checkpoints. They are meant to save the state of the simulation at a given point to allow the code to restart from that point, with a change of parameter if necessary. Each restart is made of two files: a ``.h5`` file that stores the raw data of the simulation and a ``.ini`` file that stores the parameters of the simulation as well as information to restart from that point.  

.. warning ::

  The ``.h5`` data-format of restarts is not the same as the one for snapshots. Thus, you will not be able to open these with a visualization software even if you make an ad-hoc ``.xmf`` file.



``.ini`` file parameters
^^^^^^^^^^^^^^^^^^^^^^^^

As for snapshots, the restarts can be parametrized in the ``.ini`` file:

.. code-block :: ini
  
  [run]
  # This should be on by default
  enable_checkpoint = on

  # How many iterations between each checkpoint
  checkpoint_frequency = -1

  # Alternatively, you can give a simulation time between two checkpoints
  checkpoint_timeslice = -1


Changing parameters after restart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As the restart ``.ini`` files are the same format as the rest of the configuration files for Dyablo, it is possible to open them to modify the parameters of the run. It is thus possible to modify every parameter of the run **within reason**. 

.. note ::

  It is possible to change the number of MPI processes at restart. This is completely transparent and should not be specified anywhere in the ``.ini`` file.

We highlight two standard use cases: changing the resolution of a run, and adding new-physics after a first run.

Changing the resolution
#######################

Changing the resolution of a run after a restart is possible but must follow very strict rules:

* It is possible to increase the maximum level of the simulation
* It is **not** possible to change the minimum level of the simulation
* It is **not** possible to change the block size.

To change the resolution, simply edit the ``level_max`` value in the restart file to make it effective as soon as the restart is launched. 


Adding physics
##############

It is also possible to change solvers (for instance the :doc:`hyperbolic policy <equations>`) to add new physics after a first run using restarts. To do so, one need to be careful. Changing the solver will treat new physics, but might also work on fields that are nowhere to be found in the restart file. 

As an example, let's imagine you have a run solely evolving hydrodynamics variables. After reaching a certain state in your simulation, you wish to restart the simulation, including magnetic fields. You can switch to a MHD solver, however, no magnetic field will be found in the restart file, which will lead to a crash.

The correct way to do this is to include an additional initial condition that will initialize the magnetic field without touching the hydro variables. Initial conditions, for a restart are, by default ``initial_conditions=restart``, but you can change them, given you have the correct plugin to do so. For instance, in our case, the proper initialisation would become something along the lines of ``initial_conditions=restart,magnetic_field_seed``.