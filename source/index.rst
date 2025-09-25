.. Dyablo documentation master file, created by
   sphinx-quickstart on Fri Sep 19 09:15:36 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dyablo documentation
====================

What is Dyablo
--------------

**Dyablo** is a framework to develop Computational Fluid Dynamics (CFD) simulations using Adaptive Mesh Refinement (AMR) on large scale supercomputers.

It is an attempt to modernize de software stack, initially for numerical simulations for astrophysics. 
Dyablo is written in C++ with performance portability in mind and uses an MPI+Kokkos hybrid approach to parallelism.

The MPI Library is used for distributed parallelism and compute kernels using shared-memory parallelism use the Kokkos performance portability library. 
MPI is used to distribute the AMR mesh across multiple compute nodes, while Kokkos allows us to write a single code that can be executed on multithreaded
CPUs, GPUs and other parallel architectures supported by Kokkos.

Dyablo is also build with modularity and ease of use in mind to allow physicists to easily add new kernels written with abstract interfaces to access and modify the AMR mesh.

Modularity is also key to use state-of-the-art libraries interchangeably, reuse existing work and allow compatibility with external tools for vizualization or post-processing for instance. Originally Dyablo used the PABLO external library for AMR but now uses a custom implementation written in Kokkos. This modularity enables us to plug in other external libraries to manage the AMR mesh or to perform IO, vizualization or post-processing operations. For now vizualisation outputs are handled by the HDF5 library but other backends can be integrated to Dyablo through plug-ins.


.. note::
   This project is under active development.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   supercomputer_information
   general_organization
   user_guide
   developer_guide
   reference

