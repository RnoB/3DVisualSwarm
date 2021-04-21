# 3DVisualSwarm
An accurate 3D visual field projection extraction using Blender Cycles to make collective behavior simulation. The cycles renderer offers panoramic equirectangular projection. This provides a direct way to compute the projection of the visual field in very direction.

This simulator should be considered the preferred version for computations and simulations related to the 3d projected visual field. There are many compromises to take into account (rasterisation, computation time, complexity of the scene...). Unless better algorithms are coming to compute multiple point of views in a given scene, Blender cycles is


## Blender Python Modules

The software should run directly inside Blender, but for automation purpose it is useful to use Blender bpy as a python module. The option to build Blender as a Python module is not officially supported. The module needs to be build directly on the machine. Also, to avoid writing each frame to the HDD, a viewer node is used (https://ammous88.wordpress.com/2015/01/16/blender-access-render-results-pixels-directly-from-python-2/). However rendering to the viewer node is disabled in background mode and the code should be modified before compilation (https://blender.stackexchange.com/questions/69230/python-render-script-different-outcome-when-run-in-background/81240#81240). This has been tested with Windows 10, blender 2.93 and python 3.9. 

### Building Blender as a Python Module
https://wiki.blender.org/wiki/Building_Blender/Other/BlenderAsPyModule

### Building Blender
https://wiki.blender.org/wiki/Building_Blender

### Modifying the code (after make update, before make)

Taken directly from https://blender.stackexchange.com/questions/69230/python-render-script-different-outcome-when-run-in-background/81240#81240

---

In the file source/blender/compositor/operations/COM_ViewerOperation.h, line ~58:
```C
bool isOutputOperation(bool /*rendering*/) const { if (G.background) return false; return isActiveViewerOutput();
```
should be changed to
```C
bool isOutputOperation(bool /*rendering*/) const {return isActiveViewerOutput(); }
```
and in file source/blender/compositor/operations/COM_PreviewOperation.h, line ~48:
```C
bool isOutputOperation(bool /*rendering*/) const { return !G.background; }
```
should be changed to
```C
bool isOutputOperation(bool /*rendering*/) const { return true; }
```
After these changes, the pixels array gets properly updated in background mode.

---

