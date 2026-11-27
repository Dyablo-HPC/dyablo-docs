Full cosmological volume simulation
===================================

Preamble
--------

.. note :: This tutorial is loosely adapted from the `RAMSES tutorials <https://ramses-tutorials.readthedocs.io/en/latest/Cosmological-Volume/tutorial.html>`_ written by Jérémy Blaizot and Clément Stahl. This version reproduces the main steps of the tutorial. 

In this tutorial we will see how to create initial conditions for a full cosmological volume simulation, and how to run this simulation with Dyablo. This tutorial assume that you have already compiled and run Dyablo before. If not, please refer to the :doc:`/getting_started` section.

The objective of this tutorial is to run a full cosmological box with only dark matter. We will see how to generate initial conditions using Music2, how to run the cosmological run with Dyablo and finally how to analyze the results using ``yt``.

.. danger :: Dyablo is a code initially developed for fluid dynamics. As such it is clearly not the best suited option for pure Nbody simulations. This is only an example so that the tutorial can be run quickly on a laptop with a medium GPU.

Installing the dependencies
---------------------------

MUSIC2
^^^^^^

This tutorial will be using the `MUSIC2 <https://github.com/cosmo-sims/MUSIC2>`_ code to generate initial conditions. Start by cloning the code in a folder of your choice, and build it: 

.. code-block:: bash

  git clone https://github.com/cosmo-sims/MUSIC2
  mkdir MUSIC2/build
  cd MUSIC2/build
  cmake --fresh ..
  make -j 4
  export MUSICPATH=`pwd`

If MUSIC is already built somewhere, export the path to the correct folder manually.


``yt`` and colossus
^^^^^^^^^^^^^^^

Most of the analysis will be done using the `yt <https://yt-project.org/>` package. We will also need the colossus package for the dark matter halo mass analysis.

Granted that you have a working python installation, you can use pip (or your preferred package manager) to install the required dependencies for the tutorial:

.. code-block:: bash

  pip install -v git+https://github.com/cphyc/yt_dyablo.git colossus ipykernel f90nml git+https://github.com/cphyc/yt_astro_analysis.git@fix-halo-objects ipykernel

Building the tutorial version of Dyablo
---------------------------------------

This tutorial relies on a specific version of Dyablo with the correct plugins enabled. If you don't already have a version of Dyablo on your computer, start by cloning the git repository on your computer:

.. code-block:: bash
  
  git clone --recurse-submodules https://github.com/Dyablo-HPC/Dyablo.git

This should create a ``dyablo`` folder. Go in the folder, and switch to the ``cosmo-tutorial`` branch: 

.. code-block:: bash
  
  cd dyablo
  git fetch cosmo-tutorial
  git checkout cosmo-tutorial

Finally build the code. If you want to build for a Nvidia GPU for instance do: 

.. code-block:: bash

  mkdir build
  cd build
  cmake -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_CUDA=ON ..
  make -j 4

If you want to build for CPU, the ``cmake`` command will be slightly different:

.. code-block:: bash

  mkdir build
  cd build
  cmake -DCMAKE_BUILD_TYPE=Release ..
  make -j 4

Once the code is built, you should have a ``dyablo`` executable in your ``dyablo/bin`` subfolder (inside ``build``). Go there and create an environment variable for your dyablo executable:

.. code-block:: bash

  cd dyablo/bin
  export DYABLOPATH=`pwd`

Generating initial conditions
-----------------------------

Now that we have a ``dyablo`` and a ``MUSIC`` executable built, the next step is to generate initial conditions for our run. For this, we will be using a pre-made MUSIC configuration file that you can download at `this link`_. 

.. _`this link`: ini_files/music_DM.conf

The important parameters are the following: 

[TODO]

Create a new folder where the simulations of this tutorial will be run. Download and copy the ``music.conf`` file there, then start MUSIC to generate the initial conditions set:

.. code-block:: bash

  $MUSICPATH/MUSIC music.conf

The MUSIC run should last for a few seconds to a minute and generate three new files and a folder: ``input_powerspec.txt``, ``level_007``, ``music_conf.log`` and ``wnoise_0007.bin``.

Only the folder ``level_007`` will be relevant for our simulation. The rest of the files will not be used by Dyablo.

Running the simulation
----------------------

Now that the initial conditions are ready, we can run the simulation with Dyablo. For that, we need an initial conditions file. You can use the one provided `here`_. 

.. _`here`: ini_files/cosmo_DM.ini

Let's first take a peek at this file. Open it with a text/code editor. If you are not familiar with ``.ini`` files in Dyablo, we refer you to the 

Download and copy this file to the folder where your ``music.conf`` file lives. Make a copy of the ``dyablo`` binary there as well. Finally run the simulation: 

.. code-block:: bash

  $DYABLOPATH/dyablo cosmo_DM.ini

The code should take a few minutes to run on GPU and a lot longer on CPU. At the end, you should get a report on the timers. If everything went correctly, you should have spent most of your time in the multigrid solver which solves the Poisson equation for the gravitational potential.

The run should have generated a few pairs of ``.h5/.xmf`` files. First you have the fields on the grid, stored in the ``cosmo_iterXXXXXXX.h5/.xmf`` files. Then, you have the particles stored in the ``cosmo_particles_particles_iterXXXXXXX.h5/.xmf`` files. You have three iterations stored corresponding to the expansion factors we filled in the ``.ini`` file with expansion factors of 0, 0.5 and 1.0.

Analyzing the results
---------------------

We will now switch to Python for the analysis. The bulk of the analysis will be using the ``yt`` python package. 

Loading and exploring the data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We start by importing yt, numpy and matplotlib and load the last snapshot in yt:

.. code-block:: python

  import yt_dyablo
  import yt
  import matplotlib.pyplot as plt
  import numpy as np

  filename = "cosmo_iter0000964.h5"
  ds = yt.load(
    filename,
    units_override=dict(time_unit=(1, "Gyr"), 
                        length_unit=(1, "Mpc"), 
                        mass_unit=(1, "mp/m**3 * Mpc**3")),
  )

Make sure to replace the value of ``filename`` by the last iteration you have in your run. ``yt`` should print a few messages about the information stored in the snapshot:

.. code-block::

  yt : [INFO     ] 2026-11-26 15:26:56,880 Inferred block size: [4 4 4], number of blocks: [32 32 32]
  yt : [WARNING  ] 2026-11-26 15:26:56,881 Overriding code units: Use this option only if you know that the dataset doesn't define the units correctly or at all.
  yt : [INFO     ] 2026-11-26 15:26:56,881 Overriding length_unit: 1 Mpc.
  yt : [INFO     ] 2026-11-26 15:26:56,881 Overriding time_unit: 1 Gyr.
  yt : [INFO     ] 2026-11-26 15:26:56,881 Overriding mass_unit: 1 Mpc**3*mp/m**3.
  yt : [INFO     ] 2026-11-26 15:26:56,919 Parameters: current_time              = -1.2691390419141899e-06
  yt : [INFO     ] 2026-11-26 15:26:56,919 Parameters: domain_dimensions         = [128 128 128]
  yt : [INFO     ] 2026-11-26 15:26:56,919 Parameters: domain_left_edge          = [0. 0. 0.]
  yt : [INFO     ] 2026-11-26 15:26:56,919 Parameters: domain_right_edge         = [591.19122314 591.19122314 591.19122314]
  yt : [INFO     ] 2026-11-26 15:26:56,919 Parameters: cosmological_simulation   = True
  yt : [INFO     ] 2026-11-26 15:26:56,919 Parameters: current_redshift          = -1.000000082740371e-10
  yt : [INFO     ] 2026-11-26 15:26:56,919 Parameters: omega_lambda              = 0.6889
  yt : [INFO     ] 2026-11-26 15:26:56,919 Parameters: omega_matter              = 0.3111
  yt : [INFO     ] 2026-11-26 15:26:56,919 Parameters: omega_radiation           = 0.0
  yt : [INFO     ] 2026-11-26 15:26:56,919 Parameters: hubble_constant           = 0.6766

We can query the ``ds`` structure to get more information on the snapshot. For instance, the metadata stored in the snapshot:

.. code-block:: python

  ds.parameters

.. code-block::

  {'aexp': np.float64(1.0000000001),
  'dt': np.float64(0.004709000191861687),
  'iter': np.int32(964),
  'time': np.float64(-1.2691390419141899e-06),
  'time_physical': np.float64(1.4461455853703462e-09),
  'name': 'cosmo'}


You can see here a list of metadata, including the current expansion factor (``aexp``), the current iteration (``iter``), or the name of the run. 

** Faire ici un display de l'histogramme des niveaux**

Maps of the simulation data
^^^^^^^^^^^^^^^^^^^^^^^^^^^

We can use ``yt`` to calculate and display projections or slices of our data. Let's start by projecting the dark matter particle mass on a plane:

.. code-block:: python

  p = yt.ParticlePlot(ds,'particle_position_x','particle_position_y','particle_mass',density=True)
  p.set_figure_size((5,5))
  p.set_buff_size(512)
  p.set_unit('particle_mass', "Msun/kpc**2")
  p.save()

In this example, we project the particle masses on the xy-plane to make a density map.  For this we use the `ParticlePlot <https://yt-project.org/doc/visualizing/plots.html#particle-plots>` method. This creates a plot on the disk ``cosmo_iterXXXXXXX.h5_particles_particles_mass.png`` that should resemble this:

.. figure :: ../figs/tuto_cosmo_dm_proj.png
  :align: center

Dark matter halos
^^^^^^^^^^^^^^^^^
Blabla we need to add particle ids that we don't have.

.. code-block:: python

  def _ind(data):
    return np.arange(len(data["nbody", "particle_ones"]))
  
  ds.add_field(("all", "particle_index"), function=_ind, units="", sampling_type="particle")

We run FOF on the dataset to build a catalogue

.. code-block:: python

  hc = HaloCatalog(data_ds=ds, finder_method='fof', output_dir='./')
  hc.create()



Playing with paraview
---------------------


