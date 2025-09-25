Building and running on supercomputers
======================================

This document centralizes all the configuration/batchscripts used for building and running Dyablo on supercomputers.

Jean-Zay
--------

H100 partition (**Last update: 25/09/2025**)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Configuration:** 

.. code-block :: bash
  
  module purge
  module load arch/h100
  module load cmake gcc/12.2.0 cuda/12.1.0 openmpi/4.1.5-cuda hdf5/1.12.0-mpi-cuda
  cmake -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH="HOPPER90" ..

.. danger :: As of november 2024, compilation fails on frontal nodes because of h100 modules incompatible with gcc/cmake. 
  ATo build dyablo, the code should be compiled on a h100 node via a slurm job or an interactive job.
  
  To start an interactive job use the following command ``srun --pty -A PROJECTID@h100 -C h100 --partition=gpu_p6 --nodes=1 --ntasks-per-node=1 --cpus-per-task=24 --gres=gpu:1 --hint=nomultithread bash``

**Example job script for a single node run with 4 gpus:**

.. code-block :: slurm

  #!/bin/bash

  #SBATCH --job-name=<job-name-here>
  #SBATCH -C h100
  #SBATCH --nodes=1
  #SBATCH --ntasks-per-node=4 # Up to 4 h100 GPU per node
  #SBATCH --gres=gpu:4
  #SBATCH --cpus-per-task=24 # 96/ngpu (h100)
  #SBATCH --hint=nomultithread
  #SBATCH --time=20:00:00
  #SBATCH --output=log.out
  #SBATCH --error=log.out
  #SBATCH -A <projectid>@h100

  module purge
  module load arch/h100
  module load cmake gcc/12.2.0 cuda/12.1.0 openmpi/4.1.5-cuda hdf5/1.12.0-mpi-cuda

  srun ./dyablo <your-ini-file>.ini


A100 partition (**Last update: 25/09/2025**)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Configuration:**

.. code-block :: bash
  
  module purge
  module load arch/a100
  module load cmake gcc/12.2.0 cuda/12.1.0 openmpi/4.1.5-cuda hdf5/1.12.0-mpi-cuda
  cmake -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH="AMPERE80" ..


**Example job script for a single node run with 8 gpus:**

.. code-block :: slurm

  #!/bin/bash

  #SBATCH --job-name=<job-name-here>
  #SBATCH -C a100
  #SBATCH --nodes=1
  #SBATCH --ntasks-per-node=8 # Up to 8 a100 GPU per node
  #SBATCH --gres=gpu:4
  #SBATCH --cpus-per-task=8 # 64/ngpu (a100)
  #SBATCH --hint=nomultithread
  #SBATCH --time=20:00:00
  #SBATCH --output=log.out
  #SBATCH --error=log.out
  #SBATCH -A <projectid>@a100

  module purge
  module load arch/a100
  module load cmake gcc/12.2.0 cuda/12.1.0 openmpi/4.1.5-cuda hdf5/1.12.0-mpi-cuda

  srun ./dyablo <your-ini-file>.ini

Ad-Astra
--------

Genoa (CPU) partition (**Last update 25/09/2025**)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block :: bash

  module purge
  module load cpe/24.07
  module load craype-x86-genoa
  module load PrgEnv-cray
  module load cray-hdf5-parallel
  CC=cc CXX=CC cmake -DCMAKE_BUILD_TYPE=Release -DKokkos_ARCH=ZEN4 ..

**Example jobscript:**

.. code-block :: slurm
  
  #!/bin/bash

  #SBATCH --account=<your-account>
  #SBATCH --job-name=blast_3D
  #SBATCH --constraint=GENOA
  #SBATCH --nodes=1
  #SBATCH --ntasks-per-node=8
  #SBATCH --cpus-per-task=12
  #SBATCH --threads-per-core=1
  #SBATCH --exclusive
  #SBATCH --time=24:00:00
  #SBATCH --output=log.out
  #SBATCH --error=log.out

  module purge

  module load cpe/24.07
  module load craype-x86-genoa
  module load PrgEnv-cray
  module load cray-hdf5-parallel

  srun  ./dyablo <your-ini-file.ini>

MI250 partition (**Last update 25/09/2025**)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**Configuration:**

.. code-block :: bash

  module purge
  module load PrgEnv-amd
  module load amd/6.3.3 
  module load cray-mpich 
  module load cray-hdf5-parallel
  CC=hipcc CXX=hipcc cmake -DDYABLO_USE_MPI_CUDA_AWARE_ENFORCED=ON -DDYABLO_CMAKE_ARGS="-DCMAKE_CXX_FLAGS=-ffp-model=precise;-DCMAKE_EXE_LINKER_FLAGS='-L${CRAY_MPICH_ROOTDIR}/gtl/lib -lmpi_gtl_hsa'" -DHDF5_C_COMPILER_EXECUTABLE=h5pcc -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_HIP=ON -DKokkos_ARCH=VEGA90A ..


.. danger :: Using cray wrappers to compile HIP instead of hipcc directly results in catastrophic performance (time x2.5)

.. note :: Additional info on the configuration command:
  
  - To use GPU direct MPI : ``-L${CRAY_MPICH_ROOTDIR}/gtl/lib -lmpi_gtl_hsa must be linked``.
  - Dyablo generates nans with default hipcc configuration, ``-ffp-model=precise`` must be added to yield correct results
  - Don't forget to use ``MPICH_GPU_SUPPORT_ENABLED=1`` at execution time

**Example jobscript:**

.. code-block :: slurm

  #!/bin/bash

  #SBATCH --account=<your-account>
  #SBATCH --job-name=<job-name>
  #SBATCH --constraint=MI250
  #SBATCH --nodes=1
  #SBATCH --ntasks-per-node=8
  #SBATCH --cpus-per-task=8
  #SBATCH --threads-per-core=1
  #SBATCH --gpus-per-task=1
  #SBATCH --gpu-bind=closest
  #SBATCH --exclusive
  #SBATCH --time=1:00:00
  #SBATCH --output=log.out
  #SBATCH --error=log.out

  module purge

  module load PrgEnv-amd
  module load amd/6.3.3 
  module load cray-mpich 
  module load cray-hdf5-parallel

  export MPICH_GPU_SUPPORT_ENABLED=1
    
  srun ./dyablo <your-ini-file.ini>


MI300 partition (**Last update 25/09/2025**)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**Configuration:**

.. code-block :: bash

  module purge
  module load PrgEnv-amd
  module load amd/6.3.3 
  module load cray-mpich 
  module load cray-hdf5-parallel
  CC=hipcc CXX=hipcc cmake -DDYABLO_USE_MPI_CUDA_AWARE_ENFORCED=ON -DDYABLO_CMAKE_ARGS="-DCMAKE_CXX_FLAGS=-ffp-model=precise;-DCMAKE_EXE_LINKER_FLAGS='-L${CRAY_MPICH_ROOTDIR}/gtl/lib -lmpi_gtl_hsa'" -DHDF5_C_COMPILER_EXECUTABLE=h5pcc -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_HIP=ON -DKokkos_ARCH=AMD_GFX942 ..

.. note :: Additional info on the configuration command:
  
  - To use GPU direct MPI : ``-L${CRAY_MPICH_ROOTDIR}/gtl/lib -lmpi_gtl_hsa must be linked``.
  - Dyablo generates nans with default hipcc configuration, ``-ffp-model=precise`` must be added to yield correct results
  - Don't forget to use ``MPICH_GPU_SUPPORT_ENABLED=1`` at execution time


**Example jobscript:**

.. code-block :: slurm

  #!/bin/bash

  #SBATCH --account=<your-account>
  #SBATCH --job-name=<job-name>
  #SBATCH --constraint=MI300
  #SBATCH --nodes=1
  #SBATCH --ntasks-per-node=4
  #SBATCH --cpus-per-task=24
  #SBATCH --threads-per-core=1
  #SBATCH --gpus-per-task=1
  #SBATCH --gpu-bind=closest
  #SBATCH --exclusive
  #SBATCH --time=1:00:00
  #SBATCH --output=log.out
  #SBATCH --error=log.out

  module purge

  module load PrgEnv-amd
  module load amd/6.3.3 
  module load cray-mpich 
  module load cray-hdf5-parallel

  export MPICH_GPU_SUPPORT_ENABLED=1
    
  srun ./dyablo <your-ini-file>.ini
