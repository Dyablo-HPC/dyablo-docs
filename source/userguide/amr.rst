Adaptive Mesh Refinement
========================

This page describes the adaptive mesh refinement used in Dyablo.

Block-Based AMR
---------------

The Adaptive mesh refinement data structure in Dyablo is called **block-structured AMR**. It means the mesh structure is *virtually* organized as a tree. Each leaf of the tree is called an **octant**. Block-structured AMR adds on top of that another layer where each octant holds a regular sub-grid: a **block**.

.. figure :: ../figs/amr_types.png
  :align: center
  
  **Left**: A *cell-based* AMR tree. The octants in green are the cells of the mesh. **Right**: A *block-based* AMR tree. The leaves of the tree in orange are not the cells of the computational domain. Instead, each octant contains a regular cartesian sub-grid, with the actual cells (in green).


Levels, block-sizes and resolution
----------------------------------

Refinement level
^^^^^^^^^^^^^^^^

The AMR tree exists is always confined between two **refinement levels**: a minimum level (``level_min``) and a maximum level (``level_max``). The tree is always fully refined at ``level_min`` and *can* go up to ``level_max`` included.

Every time an octant is refined, it is subdivided in two along each direction: 4 new octants in 2D and 8 in 3D.

.. figure :: ../figs/amr_levels.png
  :align: center

  Example of an AMR tree. The tree is refined between ``level_min = 2`` and ``level_max = 5``. The octants denoted in green are the blocks holding the actual cells in memory. In yellow, a cell has been marked for refinement. After the AMR cycle, this cell will be refined into two smaller octants (dashed circles below).

The operation of going from one level :math:`\ell` to the next :math:`\ell + 1` is called **refinement** while the inverse operation is called **coarsening**.

.. attention::

  An important concept to keep in mind when dealing with AMR in Dyablo is the **2:1 balance**. It is a property of the mesh that states that you *cannot* have more than one level of difference between two neighboring octants.

Block-sizes
^^^^^^^^^^^

Octants are then subdivided in blocks. The size of a block is given as a set of three parameters to the simulation, one along each direction: :math:`b_x`, :math:`b_y` and :math:`b_z`. Thus, each octant has a :math:`b_x \times b_y \times b_z` regular grid of cells. Note that in 2D, :math:`b_z` is automatically set to zero.

.. figure :: ../figs/octants_blocks.png
  :align: center

  AMR grid in two dimensions. We see cells and octants at two different levels. Each block has :math:`b_x=b_y=4`. Octant are colored differently. A block is highlighted in pink. 

Logical resolution
^^^^^^^^^^^^^^^^^^

The actual resolution obtained with block-structured AMR can be sometimes tricky to calculate. Let's consider a fixed grid case as an example, where the minimum level (:math:`\ell_{min}`) and maximum level (:math:`\ell_{max}`) are equal. Blocks in a simulation are given a size, ie the number of cells along each direction they have. These sizes are constant through the whole simulation, and are noted :math:`b_x`, :math:`b_y`, and :math:`b_z`.

We define the **logical resolution** as the number of cells in each direction at maximum level. In the case of a fixed grid run, it is the actual number of cells in the simulation. In the case of an AMR run, it is the maximum potential cells in the domain.

For our example, let us take :math:`\ell_{min} = \ell_{max} = 6`. Likewise, we take the same block size, along each direction: :math:`b_x = b_y = b_z = 4`. 

We start by calculating the number of octants along each direction. Since the grid is fully refined, the number of octants :math:`N_{oct, dir}` is given by the number of levels : 

.. math ::

  N_{oct, dir} = 2^{\ell_{max}}

Then we simply multiply by the block size to get the resolution. In our case :math:`N_{oct, dir} = 2^6 = 64`, and since the block size is 4, that means the simulation has a resolution of :math:`256^3`.

Now if we were to take :math:`b_x = 4`, :math:`b_y = 6` and :math:`b_z = 12`, we would have a total resolution of :math:`256\times 384 \times 768`.

Physical resolution
^^^^^^^^^^^^^^^^^^^

The **physical resolution** is the actual physical size of the cells. The size of a cell will depend on its level, on the size of a block, but also on the physical size of the domain. Initially, the whole domain is one huge cell of dimensions :math:`[x_{min}, x_{max}] \times [y_{min}, y_{max}] \times [z_{min}, z_{max}]`. The physical size of a cell :math:`(\Delta h)_{h=x,y,z}` is given by the level :math:`\ell` of the octant to which the cell belongs, the block size :math:`b_h` as well as the physical size of the domain. The general formula to get the physical size of a cell is thus:

.. math ::

  \Delta h = \dfrac{h_{max} - h_{min}}{2^\ell \times b_h}

The **maximum physical resolution** is thus given by taking this formula and applying it to the maximum level of the simulation : 

.. math ::

  \Delta h = \dfrac{h_{max} - h_{min}}{2^{\ell_{max}} \times b_h}

If we continue with the previous example, and say the physical domain is :math:`[0,1]\times[0,2]\times[0,3]` then, the maximum physical resolution is:

.. math ::

  \Delta x &= \dfrac{1}{2^6 \times 4}  = 0.00390625 \\
  \Delta y &= \dfrac{2}{2^6 \times 6}  \approx 0.00520833 \\
  \Delta z &= \dfrac{3}{2^6 \times 12} = 0.00390625

Slabs
-----

Sometimes, the domain you want to simulate might not be a cube. Changing the physical size of the mesh might be sufficient, but it also might distort the size of the cells stretching one direction extremely thin. 

For instance, having a circular feature in a domain extending over :math:`[0.00, 0.25]\times[0.00, 1.00]\times[0.00, 0.25]` with levels between 4 and 8 and a block size of 4 might yield the following mesh: 

.. figure :: ../figs/slab_incorrect.png
  :align: center

  Example of a slab with the same logical resolution along each direction. Since the domain is stretched along the y-axis, all cells look squashed. This can have negative numerical impacts, for instance on time step limitations.

A solution to avoid the squashing of the cells is to lower both :math:`\ell_{min}` and :math:`\ell_{max}` and change the block size to fit the aspect ratio. This has the inconvenient of often increasing the granularity of refinement, and adding too many cells in un-necessary places. In our example, if we go to :math:`\ell_{min}=2`, :math:`\ell_{max}=6` and :math:`bx,by,bz=4,16,14` we get the following result: 

.. figure :: ../figs/slab_incorrect2.png
  :align: center

  Example of the same slab where the aspect ratio of cells has been corrected using the block-size. This increases the granularity of the refinement, and adds a lot of cells far from the circular feature due to the size of the blocks.

The correct solution is to use the **coarse-resolution** feature that allows you to cut the coarse mesh, ie, the mesh fully refined at :math:`\ell_{min}`. For this Dyablo exposes the parameters ``coarse_oct_resolution_{x|y|z}`` that allows you to select how many **octants** the coarse mesh has in each direction. To circle back on our example, we have :math:`\ell_{min}=4` so we have 16 octants along each direction. The ratio to our physical size is :math:`(1/4, 1, 1/4)` so we can set: 

.. code-block ::

  coarse_oct_resolution_x = 4
  coarse_oct_resolution_y = 16
  coarse_oct_resolution_z = 4

That way, the mesh will have the right amount of cells in each direction to keep a block size of :math:`4^3` and still have a perfect aspect ratio: 


.. figure :: ../figs/slab.png
  :align: center

  The slab has been cut at :math:`\ell_{min}` only keeping the correct amount of cells. AMR granularity is optimal and cells have the right aspect ratio.

AMR Cycle and Load-balancing
----------------------------

The AMR cycle is the process of marking the cells, adapting the mesh, and doing the 2:1 balance. This process can be very expensive, so the user has the choice to parametrize how often it is applied by the parameter ``cycle_frequency``.

Similarly, the operation of load-balancing, ie distribution the total load of the mesh between all the MPI processes to make sure all process does roughly the same amount of work, is very expensive because it involves communicating a lot of data. Dyablo allows the user to parametrize how often the load balancing is done using the ``load_balancing_frequency`` parameter.

Refinement criterion and remapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The actual marking of the cells is done by the `RefinementCondition` plugin. Similarly, when a cell is refined or coarsen, the definition of the new values is done using the `MapUserData` plugin (**remapping**).

Coherent-levels
^^^^^^^^^^^^^^^

By default, the data is organized in memory following a space filling curve: the Morton Z-curve_. The most simple way to do load-balancing is to cut the curve in equal pieces and distribute these to every-process. Doing that can imply cutting on very fine levels, which will tend to increase unnecessarily the number of ghost cells to communicate. To avoid that, Dyablo allows the user to set **coherent levels** which are a number of levels below the maximum level of refinement that are not going to be cut by the load balancing if possible.  

.. _`Z-curve`: https://en.wikipedia.org/wiki/Z-order_curve

.. figure :: ../figs/coherent_levels.png
  :align: center

  The figure shows a two occurrences of the same run, woomed on a specific region. The run uses 13 MPI processes and different coherence levels. The colors indicate the MPI process and the mesh is displayed in blue. On the **left** we set ``loadbalance_coherent_levels=0``. We can see the MPI process cutting is very irregular and cuts through smaller levels. On the **right** ``loadbalance_coherent_levels=3`` and the balancing is much more coarse. 


``.ini`` file parameters
------------------------

The most important parameters are the following. Additional parameters depend on the marking and remapping plugins. See their individual documentation.

.. code-block:: ini

  [amr]
  
  # AMR levels
  level_min = 2
  level_max = 8

  # Number of cells in a block
  bx = 4                    
  by = 4                   
  bz = 4                    

  # Coarse octant cutting for slabs  
  coarse_oct_resolution_x = 4
  coarse_oct_resolution_y = 4
  coarse_oct_resolution_z = 4

  # AMR-cycle and Load-balancing
  cycle_frequency = 5                           
  load_balancing_frequency = 10                  
  loadbalance_coherent_levels = 3   

  markers_kernel = RefineCondition_pseudo_gradient
  remap          = MapUserData_mean