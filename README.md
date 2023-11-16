# ~~Project abandonned for now~~

~~Finally, Ray casting does not seem to be a good solution to compute fastly and reliably multiple points of view, a different version is in progress. I keep the project as a reference.~~

# Back in business!!

There are still no good solutions to compute multiple spherical point of view with complex objects. So I am throwing a general simulator with different methods to compute the visual field. This repository is experimental and is not ready for production, so you should better contact me before attempting to use it.  

# 3DVisualSwarm
An accurate 3D visual field projection extraction using Blender Cycles to make collective behavior simulation. The cycles renderer offers panoramic equirectangular projection. This provides a direct way to compute the projection of the visual field in every direction.

This simulator should be considered the preferred version for computations and simulations related to the 3d projected visual field. There are many compromises to take into account (rasterisation, computation time, complexity of the scene...). It is going to be slow! 

Panda3D raycaster has been implemented with the bullet engine and it is very slow. It is not clear why it is so much slower than Unity3D. I keep as a flex because the engine behind the simulator can be changed transparently to the user.

There is also a rasterizer engine in 2D but it only works with ellipses. If you can implement that in 3D I am interested.

 <font size=”7”>SLOW SLOW SLOW</font>

# Writer Server

I am implementing a full stack that will include a multiplayer Virtual Reality server. As for now, the writer server is required if you want to write data.

https://github.com/RnoB/WriterServer

## Blender Python Modules

The software should run directly inside Blender, but for automation purpose it is useful to use Blender bpy as a python module. The option to build Blender as a Python module is not officially supported. The module needs to be build directly on the machine. Also, to avoid writing each frame to the HDD, a viewer node is used (https://ammous88.wordpress.com/2015/01/16/blender-access-render-results-pixels-directly-from-python-2/). However rendering to the viewer node is disabled in background mode and the code should be modified before compilation (https://blender.stackexchange.com/questions/69230/python-render-script-different-outcome-when-run-in-background/81240#81240). This has been tested with Windows 10, blender 2.93 and python 3.9. This has failed with Ubuntu Server 22.02.3, Blender 3.6 and Python 3.10. For Linux, I advise now to prepare a Virtual Machine with [Rocky 8](https://rockylinux.org/) as it is the preffered way to compile release versions of Blender. Be sure to read all those sections before you start. And be sure to checkout a released version of Blender to avoid bugs
```console
git checkout v3.6.0
```

### Rocky 8 Release Build Environment
https://wiki.blender.org/wiki/Building_Blender/Other/Rocky8ReleaseEnvironment

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

### Removing Blender Verbosity
Blender is printing a lot of stuff like that.
```console
Fra:1 Mem:9.41M (Peak 9.59M) | Time:00:00.00 | Mem:0.00M, Peak:0.00M | Scene, ViewLayer | Updating Scene
```
It's a mess when doing simulations and a source of slowdown. Let's get rid of it too.

So in source/blender/render/intern/pipeline.cc lines ~204 to ~215 should be commented
```C
  fprintf(stdout,
          TIP_("Fra:%d Mem:%.2fM (Peak %.2fM) "),
          rs->cfra,
          megs_used_memory,
          megs_peak_memory);

  fprintf(stdout, TIP_("| Time:%s | "), info_time_str);

  fprintf(stdout, "%s", rs->infostr);

  /* Flush stdout to be sure python callbacks are printing stuff after blender. */
  fflush(stdout);
```
and lines ~221 and ~222
```C
  fputc('\n', stdout);
  fflush(stdout);
```
