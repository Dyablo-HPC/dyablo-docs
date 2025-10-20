Lexicon
=======

This page defines technical terms that are used throughout this documentation.

#
-

**2:1 balance**: property of the mesh stating that you cannot have more that one level of difference between two neighboring octants. [:doc:`userguide/amr`]

B
-

**Block**: a regular cartesian subgrid holding the cells of the domain. [:doc:`userguide/amr`]

C
-

**Cell**: the base grid element of the mesh that stores the fields and the data. [:doc:`userguide/amr`]

**Checkpoint**: output made to restart the simulation after failing or stopping. [:doc:`userguide/ios`]

**Coarsening**: merges 4(2D) or 8(3D) octants at level :math:`\ell` into a single octant at level :math:`\ell-1` [:doc:`userguide/amr`]

**Coarse resolution**: resolution of the mesh at :math:`\ell_{min}`. [:doc:`userguide/amr`]

G
-

**Ghost cell**: Ghost cells can have two specific meaning depending on the context:
  
  * When dealing with MPI processes and communication, each MPI process has a certain domain that it is responsible for. The cells that are neighboring that domain are called ghost-cells because their value is used in the computation, but the current process is not responsible for updating them.
  * When dealing with the domain as a whole, and with non-periodic boundary conditions, ghost-cells refer to a layer of virtual cells that are added around the physical domain to simulate the boundary conditions.

M
-

**Marking**: process where the octants of the mesh are flagged for refinement or coarsening. [:doc:`userguide/amr`]

O
-

**Octant**: a leaf of the AMR tree. Each octant holds a block of cells. [:doc:`userguide/amr`]


P
-

**Plugin**: a plugin in Dyablo is a piece of modular code that can be replaced at runtime. Plugins affect all major parts of the code.

R
-

**Refinement**: subdivides an octant at level :math:`\ell` into 4(2D) or 8(3D) octants at level :math:`\ell+1` [:doc:`userguide/amr`]

S
-

**Snapshot**: output made for visualization/analysis. [:doc:`userguide/ios`]

U
-

**User data**: the union of all the fields defined by the user that have to be stored on the grid.

