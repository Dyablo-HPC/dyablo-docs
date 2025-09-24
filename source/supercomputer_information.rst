Building and running on supercomputers
======================================

This document centralizes all the configuration/batchscripts used for building and running Dyablo on supercomputers

Jean-Zay:
---------

H100 partition
^^^^^^^^^^^^^^

**Last update: 12/11/2024**

.. code-block :: console
  
  module purge
  module load arch/h100
  module load cmake gcc/12.2.0 cuda/12.1.0 openmpi/4.1.5-cuda hdf5/1.12.0-mpi-cuda
  cmake -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH="HOPPER90" ..

.. danger :: Compilation fails on frontal nodes because of h100 modules incompatible with gcc/cmake. 
  To build dyablo, the code should be compiled on a h100 node via a slurm job or an interactive job.
  
  To start an interactive job use the following command ``srun --pty -A PROJECTID@h100 -C h100 --partition=gpu_p6 --nodes=1 --ntasks-per-node=1 --cpus-per-task=24 --gres=gpu:1 --hint=nomultithread bash``


A100 partition
^^^^^^^^^^^^^^

**Last update: 12/11/2024**

.. code-block :: console
  
  module purge
  module load arch/a100
  module load cmake gcc/12.2.0 cuda/12.1.0 openmpi/4.1.5-cuda hdf5/1.12.0-mpi-cuda
  cmake -DCMAKE_BUILD_TYPE=Release -DKokkos_ENABLE_CUDA=ON -DKokkos_ARCH="AMPERE80" ..

