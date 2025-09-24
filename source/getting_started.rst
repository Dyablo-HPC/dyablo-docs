Getting Started
===============

Cloning the repository
----------------------

Dyablo can be cloned from the Github repository:

.. code-block :: console
  
  git clone --recurse-submodules https://github.com/Dyablo-HPC/Dyablo.git

In case you have cloned the repository **without** adding the ``--recurse-submodules`` option, you can clone the submodules separately. In the ``dyablo`` folder, type:`

.. code-block :: console

  git submodule init
  git submodule update


Dependencies
------------


Dyablo relies on CMake for building. The superbuild system should automatically find dependencies and warn you if any dependency is missing. 
CMake version > 3.16 is needed to compile Kokkos.

You will need a recent C++ compiler compatible with C++17 and capable of compiling Kokkos. Recommended compiler versions for Dyablo are :

  * ``g++`` 12+
  * ``icc`` 19.0.5+
  * ``clang`` 11+
  * ``nvcc`` 12+
  
You will also require ``hdf5`` (1.10+), ``MPI`` and ``libxml2``.


Building for CPU
-----------------

To make a first build of Dyablo, create a ``build`` subfolder and configure the CMake project:

.. code-block :: console

  mkdir build_openmp; cd build_openmp
  cmake -DCMAKE_BUILD_TYPE=Release ..

By default, if no other argument is provided to the CMake command, Dyablo will build using the OpenMP backend of Kokkos, effectively compiling for multi-threaded CPUs.

Once the configuration step finished, the last three lines should look like the following:

.. code-block :: 

  -- Configuring done (1.9s)
  -- Generating done (0.0s)
  -- Build files have been written to: <path_to_your_build_folder>

You can then compile the project using ``make``:

.. code-block :: console

  make -j 8

The code should take a little while to compile, but will eventually end-up with the following statement: 

.. code-block :: console

  [100%] Completed 'dyablo'
  [100%] Built target dyablo

Building for GPU
-----------------

Alternatively, you can configure Dyablo to compile for a GPU target. For a Nvidia GPU with cuda, the configuration line will become : 

.. code-block ::
  
  cmake -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_CUDA=ON ..

while for an AMD GPU the configuration will use HIP : 

.. code-block ::

  cmake -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_HIP=ON ..

For these two configurations, Kokkos should be able to automatically detect the architecture used by your GPU.


Running a first example
-----------------------

The executable of ``dyablo`` will be located in the subfolder ``dyablo/bin`` along with a couple of examples to run and visualize. 

Go on and give a try to the 2D Sedov blast:

.. code-block :: console

  cd dyablo/bin
  ./dyablo test_blast_2D_block.ini

After a few seconds the run should be finished. The output log of Dyablo is generally made of four major section : 
  
  1. Kokkos' initialization step
  2. Dyablo initialization step
  3. Run information
  4. Final reporting

Let's go over these one by one.

Kokkos' initialization
^^^^^^^^^^^^^^^^^^^^^^

The first elements logged by Dyablo are the information given by Kokkos. Here is an example of reporting done by Kokkos :

.. code-block :: 

  ##########################
  KOKKOS CONFIG             
  ##########################
  Kokkos configuration
    Kokkos Version: 4.4.0
  Compiler:
    KOKKOS_COMPILER_GNU: 1330
  Architecture:
    CPU architecture: none
    Default Device: N6Kokkos6OpenMPE
    GPU architecture: none
    platform: 64bit
  Atomics:
  Vectorization:
    KOKKOS_ENABLE_PRAGMA_IVDEP: no
    KOKKOS_ENABLE_PRAGMA_LOOPCOUNT: no
    KOKKOS_ENABLE_PRAGMA_UNROLL: no
    KOKKOS_ENABLE_PRAGMA_VECTOR: no
  Memory:
  Options:
    KOKKOS_ENABLE_ASM: yes
    KOKKOS_ENABLE_CXX17: yes
    KOKKOS_ENABLE_CXX20: no
    KOKKOS_ENABLE_CXX23: no
    KOKKOS_ENABLE_CXX26: no
    KOKKOS_ENABLE_DEBUG_BOUNDS_CHECK: no
    KOKKOS_ENABLE_HWLOC: no
    KOKKOS_ENABLE_LIBDL: yes
  Host Parallel Execution Space:
    KOKKOS_ENABLE_OPENMP: yes

  OpenMP Runtime Configuration:
  Kokkos::OpenMP thread_pool_topology[ 1 x 20 x 1 ]

Here Kokkos tells us that the code is using C++17, that Dyablo has been compiled for the OpenMP backend, 
and that it will be running using 20 threads on a single NUMA node with no hyperthreading.

Dyablo's initialization
^^^^^^^^^^^^^^^^^^^^^^^

The next phase is the information given by Dyablo about the run: 

.. code-block ::

  ##########################
  Godunov updater    : HydroUpdate_hancock
  IO Manager         : IOManager_hdf5
  Gravity solver     : none
  Initial conditions : `blast` 
  Refine condition   : RefineCondition_pseudo_gradient
  Compute dt         : `Compute_dt_hydro` 
  Source Terms : 
  ##########################

This tells us all the information taken from the ``.ini`` file concernign the plugins used by Dyablo to make the computation. So we know the following:

  * The hydrodynamics part is solved using a Muscl Hancock scheme
  * All outputs will be written as ``.xmf``/``.h5`` pairs.
  * No gravity will be applied to the run
  * We setup the run to be a Sedov Blast
  * We use a pseudo-gradient refinement condition, using the difference between neighboring cells to decide if an octant must be refined.
  * Time-step calculation uses standard Hydro CFL limitations 
  * No source terms are applied

Run information
^^^^^^^^^^^^^^^

Then Dyablo will output a sequence of lines looking like these : 

.. code-block ::

  Output: scalar_data : iter=0 aexp=1 time=0 
  scalar_data : iter=0 aexp=1 dt=0.00153124 time=0 
  Mesh - rank 0 octs : 124 (0)

Let's go over these one by one: 

  * The first line indicates that an output is being written to the disk. The current iteration number, and time information (physical time, and cosmological expansion factor) are provided as well.
  * The second line reports an iteration. By default, every 10 iterations are reported. This lines indicate the current iteration, time, and time-step size.
  * The final line occurs when the AMR cycle is being called. The reporting indicates for each MPI rank, the size of the mesh (here 124 octants) and the number of MPI ghosts held by this process (here 0 since we are in a mono-process run) 

Other lines can be logged, but these are the most important ones to know.

Final reporting
^^^^^^^^^^^^^^^

**Finish this part**

Building tests
--------------

Dyablo comes with a suite of unit-tests that can be run to check your code is up to standards. You can activate the building of unit-tests in the CMake configuration stage by setting the flag ``-DDYABLO_ENABLE_UNIT_TESTING=ON``.

After configuring and compiling the code, the unit tests should be available in the folder ``build/dyablo/unit_tests``. After compilation, the folder should hold a series of executable programs that will individually test features in Dyablo.

The tests can be run one by one by executing the relevant executable, or all executed in a batch as they would run in the CI pipeline on git by running the command ``make test`` in the ``unit_tests`` folder. Each test will be executed for single process and MPI runs and should report success or failure upon execution.