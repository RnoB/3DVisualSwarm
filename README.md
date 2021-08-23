# 3DVisualSwarm
An accurate 3D visual field projection rasterizer to perform behavioral simulation


## The projector

Starts by importing the visual projector
```python
import visualProjector as vp
```
then creates an empty scene with the pixel size of the projection of the visual field 
```python
size = 512
scene = vp.Scene(size)
```
Once this is done, new objects can be added to the scene. Only spherical objects with size bodySize are taken into account. The rotation accounts for the direction of the object
```python
position = (0,0,0)
rotation = (0,0,0)
bodySize = 1
scene.addObject(position,rotation,bodySize)
```
Each new object should be added with the same code. The index of each object is then iterated for each new object. To compute the visual of the first object added, one just needs to type
```python
idx = 0
scene.computeVisualField(idx)
```

## The simulator

untested