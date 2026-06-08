Adaptive Mesh Refinement
========================

.. important ::
   
   This section is aimed at advanced developers who wish to understand how the AMR backend is implemented.

.. attention::

   This section needs reworking


The AMR interface in Dyablo
---------------------------

In Dyablo, the implementation of the AMR algorithms is written using Kokkos to run on GPUs, but the interfaces used to interact with the AMR mesh are still very similar to that of the PABLO_ library. This interface separates user data from the AMR mesh topology and allows us to use Kokkos to execute our compute-intensive kernels on all Kokkos-supported hardware independently of the AMR backend used. Dyablo is modular and the AMR can still be offloaded to external libraries.

.. _PABLO: https://optimad.github.io/bitpit/modules/index.html#PABLO


The interface exposes the following manipulations of the AMR mesh:

* **Access mesh connectivity information**: the function ``findNeighbors()`` retrieves the neighborhood of a given octant. This is used inside stencil-like kernels to access values of neighboring cells.
* **Coarsen/refine AMR cells**: the function ``adapt()`` coarsens or refines the mesh according to markers computed from user-defined refinement criteria. The mesh modification is performed in multiple steps:
   
   1. The **2:1 balance** modifies the refinement criterion markers to ensure that every cell only has neighbors with at most 1 level of difference;
   2. Apply the refinement criteria to modify the AMR tree;
   3. Remap the user data to fit the new mesh by various interpolation schemes.

* **MPI Data distribution**: The AMR cells are distributed and load-balanced across multiple MPI processes. This includes MPI communications to distribute and re-distribute user data.

* **MPI communication**: The ``GhostCommunicator`` interface integrates with the AMR mesh to communicate ghost cells with a simple ``communicate_ghosts()`` call.


Accessing the AMR mesh in kernels
---------------------------------

Because some AMR algorithms can be offloaded to external libraries (that may not be compatible with GPUs), Dyablo implements data-structures to represent the AMR mesh on GPU that are used to access the meta-data and the neighborhood of AMR octants. In Dyablo, the device-compatible ``LightOctree`` interface has been added to allow access to the AMR tree inside Kokkos kernels.

Mesh meta-data
^^^^^^^^^^^^^^

In Dyablo, the information (meta-data) concerning the leaves of the octree can be accessed using the ``LightOctree`` interface. Each leaf-octant is numbered according to the Morton space-filling curve (`Z-curve`_), and the index related to this ordering (``iOct``) is used to access octant data :

.. _`Z-curve`: https://en.wikipedia.org/wiki/Z-order_curve

* **Position**: logical in the unit cube (or morton index), or physical position. ex: ``mesh.getCenter(iOct)``
* **AMR level**: logical level or physical cell size. ex: ``mesh.getSize(iOct)``.

To use this information inside Kokkos kernels on the  device, the mesh meta-data must be extracted from the AMR backend to a Kokkos::View and transferred to the device. This can be done by extracting data through the ``AMRMesh`` interface for generic AMR backends. The custom Dyablo AMR backend allows optimized creation of the ``LightOctree`` because they share the same mesh representation.

The ``LightOctree`` interface uses a similar access pattern. Therefore, Dyablo only supports a cube topology (actually a rectangular cuboid for the Dyablo backend). 

Neighborhood
""""""""""""

Information related to the neighborhood of an octant can be retrieved using the ``lmesh.findNeighbors(iOct, neighbor_pos, [...])`` method in the ``LightOctree`` interface. This is used in stencil-like algorithms to access neighbor cells.
This method can be implemented in multiple ways depending on the AMR backend and the hardware architecture used:

* Encode and store the results of the AMR backend's ``findNeighbors()`` for each octant into a ``Kokkos:View``.
* Compute the neighborhood inside the Kokkos kernel using already stored meta-data from before.

Dyablo's LightOctree_hashmap implementation uses a hashmap (Kokkos::UnorderedMap) and the data copied from section "Mesh meta-data" (``Kokkos::View``) to translate and reverse-translate logical position + level <-> octant index. To get the neighborhood of an octant from it's index :

1. translate index to logical position using the ``Kokkos::View`` of positions
2. add neighbor offset to logical coordinates
3. convert logical coordinates back to octant index using the hashmap

This method recomputes the neighborhood at each call during the kernels, but we can imagine storing the result of this neighborhood search to avoid accessing the hashmap too often. (A LightOctree_hashmap_precompute has been implemented, it is not necessarily interesting performance-wise on GPUs)

Coarsen-Refine
^^^^^^^^^^^^^^

The Coarsen/Refine algorithm is performed in a black-box manner by the AMR backend, but computing the Markers and remapping the user data after the AMR cycle needs to be performed in GPU kernels.

Markers
"""""""

The coarsen refine process in Dyablo uses markers to flag octants for coarsening / refining. Markers represent the number of levels to add/remove for each octant and are computed outside of the AMR backend according to a user-defined refinement criterion. Markers are computed in a Kokkos kernel that can be executed on device : this means the user data required for this computation does not need to be copied back to the host (main memory, CPU). Only the markers are copied back to allow teh AMR backend to process them. Furthermore, only non-zero markers need to be copied and transmitted to the backend.

To transmit markers to the backend the ``mesh.setMarker(iOct,marker)`` interface need to be used. This is a CPU-only method and must be called for each non-zero marker in the list computed on device and copied back to the host memory. An OpenMP Kokkos kernel is used for maximum performance. An optimization is available for the Dyablo internal backend to avoid copying the markers to CPU.

Remapping
"""""""""

After the AMR mesh topology has been modified by the coarsening / refining process in the ARM backend, user-data has to be copied and interpolated :

* Newly refined cells need to take the value of their parent octant
* Newly coarsened cells have their values interpolated from the values of the child octants
* Unchanged cells have to be copied to their new location in the array

The AMR backend exposes the ``AMR_Remapper`` abstract interface to determine whether an octant in the new mesh is newly coarsened / refined and which old octant(s) correspond to which new octant. This interface if created by the AMR backend during the refinement process.

The ``AMR_Remapper`` abstract interface is a generic and GPU-compatible interface to get the old/new correspondence inside Kokkos kernels. The second method uses the hashmap to get old octant index from the logical position of new octant, searching on multiple levels to find an existing octant in, the new mesh.

A new user-data ``Kokkos::View`` is allocated, and the octants are copied from the old view to the new in a Kokkos kernel according to the ``AMR_Remapper`` info. The new and old views are swapped and the old view is then unallocated. The kernel used for adaptation can be adapted on the user side, for example if a specific interpolation/extrapolation is needed.

MPI distribution
^^^^^^^^^^^^^^^^

The AMR mesh is distributed across multiple MPI process. Each process can access local octants with the interface detailed in section "Accessing mesh information". Additionally, it is possible to access ghost octants : they are the octants that share a face with a local octant. Some information, like the neighborhood, can only be accessed for local octants.

The load-balancing is computed in a black-box manner by the AMR backend.

MPI communication of user-data
""""""""""""""""""""""""""""""

Dyablo implements the ``GhostCommunicator`` abstraction that can be configured by the AMR backend and offers a simple way to communicate ghost cells between MPI process. The ``communicate_ghosts()`` fills ghosts cells with values from remote processes. The ``reduce_ghosts()`` reduces the values from all the ghosts in remote processes to the local cell.

This interface is compatible with GPU-Aware communications but can also use CPU-only communications with a GPU-CPU transfer if the MPI implementation is not compatible.

Custom AMR algorithms for GPU
-----------------------------

A new backend replacing PABLO has been added to Dyablo for the AMR algorithms. The ``AMRmesh`` common interface for both implementation allows using any backend without changing the rest of the code. Whilst the PABLO-specific implementations for ``LightOctree`` or ``GhostCommunicator`` can only be used with the PABLO AMR backend, other implementations can be used by both ``AMRmesh`` implementations.

Domain decomposition and storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Storage
"""""""

The only necessary data needed to describe the entire AMR tree are the logical coordinates and the level at which each octant resides. The same information is also needed for ghost octants.

Two ``Kokkos::View<uint16_t[4]*>`` are used to store ``{px,py,pz,level}`` for each octant and for each ghost octant. Octants are stored according to the Z-curve.

Load-balancing
""""""""""""""

Domain decomposition is based on morton intervals : each process :math:`P_i` is assigned a morton interval :math:`[Mmin_i,Mmin_{i+1}[` and each octant with a morton index (at the deepest level) within this interval is local to the process.

During load balancing an optimal morton interval is determined for each MPI process, and meta-data as well as user-data are exchanged using the ``GhostCommunicator`` interface mentioned previously to construct a new local AMR mesh with up-to-date user-data.

The optimal Morton interval for each process is computed using a distributed k-selection. With :math:`N` the total number of octants and :math:`p` the number of MPI processes, the :math:`(Ni)/p`-th global octant (using the Morton order) is selected as the pivot :math:`Mmin_i` this ensures that each process has the same number of local octants. As the octants are sorted in each process, the owning process and the local index of the pivot octant can be easily found.

Morton intervals can be shifted to avoid splitting families of octants of the same subtree by truncating the last bits of the pivot Morton indexes :math:`Mmin_i`. The resulting distribution is not perfectly distributed, but it reduces de complexity of the ghost zones and reduces the number of ghost octants. This can also be used to ensure that more parent octants are on the same process as their children for multi-grid and hierarchical algorithms.

Ghost octants discovery
"""""""""""""""""""""""

Octants to send to other MPI processes as ghost octants are discovered by computing the Morton index of the neighbor cells and comparing against the Morton intervals determined during the load-balancing phase.

For each local octant :math:`i_{Oct}`, an offset in every direction is applied to the logical coordinates and the Morton index of the neighbor is computed. A binary search upon the Morton intervals is then performed to search which MPI process :math:`P_i` owns the neighbor cell. :math:`i_{Oct}` is then added to the list of octants to send to :math:`P_i` as ghosts.

When the neighbor octant is subdivided in smaller octants (which the local process have no way of knowing), the Morton intervals may split it across multiple process. This has to be taken into account and :math:`i_{Oct}` may be added to the list for multiple process when neighboring cells are scattered across multiple process.

Coarsen-Refine
^^^^^^^^^^^^^^

During the coarsen / refine step, markers are applied to subdivide or merge octants according to the markers computed beforehand. This algorithm also ensures the 2:1 balance condition of every octant : every octant is only surrounded by octants with at most 1 AMR level difference.

2:1 balance
"""""""""""

2:1 balance is the most expensive algorithm of the AMR cycle. Because Refining an octant can trigger a cascade of refinements to keep the 2:1 balance. One refinement can affect octants quite far from the initially refined octant and can cross process boundaries. 2:1 balance is an iterative process and may require MPI communications to spread successive refinements.

In this implementation, markers are modified to ensure 2:1 balance before they are applied to the mesh. For a valid mesh that verifies the 2:1 criterion, markers can only be increased : under refined octants can lead to numerical errors, whereas over-refined octants only cause a performance penalty. Before starting, the markers are cleaned : for instance an octant can be coarsened only if all it's sibling are marked for coarsening.

At the beginning of the algorithm, each process knows it's initial octants (+ ghosts) and the local requested markers.

1. Ghost markers are exchanged using GhostCommunicator, and the same list of octants to exchange as for the communication of ghost user-data.
2. The 2:1 criterion is checked for every octant. If the current octant has a neighbor that is too small (size < /2 in each direction), the marker for the current octant is increased. LightOctree is used to find neighbors.
3. Repeat 2 as long as at least one local marker has been modified
4. Repeat 1,2,3 as long as at least one global marker has been modified since the last ghost markers communication.

This algorithm is a naive version of the 2:1 balance algorithm :

* 2,3 can be done using task-based kokkos parallelism to avoid unnecessary octant checks: only neighbors of recently modified markers need to be checked
* The volume of MPI communications can be greatly reduced by exchanging only markers that have been modified since the last exchange
* The number of ghost communication cycles can be reduced by using a wider ghost zone for markers

Applying markers
""""""""""""""""

Newly refined octants have to be inserted into the octant list and newly coarsened octants have to be removed. ``Kokkos::parallel_scan`` is used to copy old octants to a new view, and to add/remove all refined/coarsened octants.

Ghost octants are then discovered as described in 'Ghost octants discovery', and metadata for ghost octants are exchanged.