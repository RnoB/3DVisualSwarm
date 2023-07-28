# MIT License

# Copyright (c) 2021 Renaud Bastien

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import bpy
import bpy_extras
import bmesh
import mathutils
import math
import numpy
import os
import numpy as np

radTodDeg = 180/np.pi 


class Camera:

    def positionUpdate(self,*args):
        if len(args) == 1:
            bpy.data.objects['Camera'].location = mathutils.Vector(args[0])
        if len(args) == 3:
            bpy.data.objects['Camera'].location = mathutils.Vector((args[0],args[1],args[2]))

        self.position = bpy.data.objects['Camera'].location

    def rotationUpdate(self,*args):
        if len(args) == 1:
            self.camera.rotation_euler = mathutils.Vector(args[0])+self.rotationOffset
        if len(args) == 3:
            self.camera.rotation_euler = mathutils.Vector((args[0],args[1],args[2]))+self.rotationOffset

        self.rotation = self.camera.rotation_euler 

    def rotate(self,*args):
        if len(args) == 1:
            self.camera.rotation_euler += mathutils.Vector(args[0])
        if len(args) == 3:
            self.camera.rotation_euler = mathutils.Vector((self.rotation.x+args[0],\
                                                            self.rotation.y+args[1],\
                                                            self.rotation.z+args[2]))

        self.rotation = self.camera.rotation_euler 


    def Translate(self,*args):
        if len(args) == 1:
            bpy.data.objects['Camera'].location += mathutils.Vector(args[0])
        if len(args) == 3:
            bpy.data.objects['Camera'].location += mathutils.Vector((args[0],args[1],args[2]))
        self.position = bpy.data.objects['Camera'].location

    def camera2d(self):
        proj.camera.camera.data.cycles.latitude_max = 0
        proj.camera.camera.data.cycles.latitude_min = 0

    def __init__(self,x=0,y=0,z=0,dim = 3):
        self.rotationOffset = mathutils.Vector((math.pi/2.0,0,-math.pi/2.0))
        camera_data = bpy.data.cameras.new(name='Camera')
        self.camera = bpy.data.objects.new('Camera', camera_data)
        bpy.context.scene.collection.objects.link(self.camera)
        bpy.context.scene.camera = self.camera
        self.camera.data.type = 'PANO'
        self.camera.data.cycles.panorama_type = 'EQUIRECTANGULAR'
        self.camera.rotation_euler = (math.pi/2.0,0,-math.pi/2.0)
        self.rotation = self.camera.rotation_euler
        bpy.data.objects['Camera'].location = mathutils.Vector((x,y,z))
        self.position = bpy.data.objects['Camera'].location
        if dim == 2:
            camera2d()
   

class Mesh:

    def position(self,*args):
        if len(args) == 1:
            bpy.data.objects['Camera'].location = mathutils.Vector(args[0])
        if len(args) == 3:
            bpy.data.objects['Camera'].location = mathutils.Vector((args[0],args[1],args[2]))

        self.position = bpy.data.objects['Camera'].location

    def Translate(self,*args):
        if len(args) == 1:
            bpy.data.objects['Camera'].location += mathutils.Vector(args[0])
        if len(args) == 3:
            bpy.data.objects['Camera'].location += mathutils.Vector((args[0],args[1],args[2]))
        self.position = bpy.data.objects['Camera'].location



    def __init__(self):
        camera_data = bpy.data.cameras.new(name='Camera')
        self.camera = bpy.data.objects.new('Camera', self.camera)
        bpy.context.scene.collection.objects.link(camera_object)
        bpy.context.scene.camera = self.camera
        self.camera.data.type = 'PANO'
        self.camera.data.cycles.panorama_type = 'EQUIRECTANGULAR'
        self.camera.rotation_euler = (-math.pi/2.0,0,math.pi/2.0)
        bpy.data.objects['Camera'].location = mathutils.Vector((x,y,z))
        self.position = bpy.data.objects['Camera'].location

class ProjectedSine:



    def equirectangularToDirection(self,u,v):
        rang = [-2*np.pi, np.pi, -np.pi, np.pi/2.0]
        phi = rang[0] * u + rang[1];
        theta = - (rang[2] * v + rang[3]);
        return phi,theta


    def stack(self,N):
        self.dPhiAll = np.array([self.dPhiIm]*N).transpose((1,2,0))
        self.dThetaAll = np.array([self.dThetaIm]*N).transpose((1,2,0))

        self.sinThetaAll = np.array([self.sinThetaIm]*N).transpose((1,2,0))
        self.cosThetaCosPhiAll = np.array([self.cosThetaCosPhiIm]*N).transpose((1,2,0))
        self.cosThetaSinPhiAll = np.array([self.cosThetaSinPhiIm]*N).transpose((1,2,0))


 

    def __init__(self,size):
        

        u = np.linspace(0,1,size[0])
        v = np.linspace(0,1,size[1])
        self.phi,self.theta = self.equirectangularToDirection(u,v)
        
        
        self.phi2d = np.array([self.phi,]*size[1])
        self.theta2d = np.array([self.theta,]*size[0]).transpose()

        self.dThetaIm =  np.array([[np.pi/size[1],]*size[0],]*size[1])
        self.dPhiIm = np.cos(self.theta2d)*np.array([[2*np.pi/size[0],]*size[0],]*size[1])



        self.dThetadPhiIm = self.dThetaIm*self.dPhiIm

        self.sinThetaIm = np.sin(self.theta2d) * self.dThetadPhiIm
        self.cosThetaCosPhiIm = np.cos(self.theta2d) * np.cos(self.phi2d) * self.dThetadPhiIm 
        self.cosThetaSinPhiIm = np.cos(self.theta2d) * np.sin(self.phi2d) * self.dThetadPhiIm
        

        self.dTheta = np.matrix.flatten(self.dThetaIm)
        self.dPhi = np.matrix.flatten(self.dPhiIm)

        self.sinTheta = np.matrix.flatten(self.sinThetaIm)
        self.cosThetaCosPhi = np.matrix.flatten(self.cosThetaCosPhiIm)
        self.cosThetaSinPhi = np.matrix.flatten(self.cosThetaSinPhiIm)




class Projector:

    def setupRender(self,samples = 1):
        bpy.context.scene.render.engine = 'CYCLES'


        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.use_nodes = True
        bpy.context.scene.render.image_settings.color_mode = 'BW'
        tree = bpy.context.scene.node_tree
        links = tree.links

        for n in tree.nodes:
            tree.nodes.remove(n)
        nodeLayer = tree.nodes.new('CompositorNodeRLayers')  
        nodeViewer = tree.nodes.new('CompositorNodeViewer')  
        nodeViewer.use_alpha = False

        links.new(nodeLayer.outputs[0], nodeViewer.inputs[0])



        bpy.context.scene.render.resolution_x = self.size[0]
        ìf self.dim == 3:
            bpy.context.scene.render.resolution_y = self.size[1]
        else:
            bpy.context.scene.render.resolution_y = 1
        bpy.context.scene.cycles.samples = samples
        bpy.context.scene.cycles.preview_samples = 0

        bpy.context.scene.cycles.max_bounces = 0
        bpy.context.scene.cycles.diffuse_bounces = 0
        bpy.context.scene.cycles.glossy_bounces = 0
        bpy.context.scene.cycles.transparent_max_bounces = 0
        bpy.context.scene.cycles.transmission_bounces = 0
        bpy.context.scene.cycles.volume_bounces = 0


        bpy.context.scene.cycles.max_subdivisions = 1
        bpy.context.scene.cycles.sample_all_lights_indirect = 0
        bpy.context.scene.cycles.sample_all_lights_direct = 0

        bpy.context.scene.cycles.caustics_reflective = False
        bpy.context.scene.cycles.caustics_refractive = False

        bpy.context.scene.cycles.sample_clamp_indirect = 0
        bpy.context.scene.cycles.sample_clamp_direct = 0

        bpy.context.scene.cycles.min_light_bounces = 0
        bpy.context.scene.cycles.min_transparent_bounces = 0
        bpy.context.scene.cycles.light_sampling_threshold = 0

        bpy.context.scene.cycles.use_adaptive_sampling = True
        bpy.context.scene.cycles.use_denoising = False
        bpy.context.scene.cycles.blur_glossy = 0

        bpy.context.scene.cycles.volume_step_rate = 100
        bpy.context.scene.cycles.volume_max_steps = 10
        bpy.context.scene.render.use_simplify = False


        bpy.context.scene.render.use_motion_blur = False

        bpy.context.scene.cycles.pixel_filter_type = 'BOX'

        bpy.context.scene.render.threads_mode = 'FIXED'
        bpy.context.scene.render.threads = 1

        #bpy.context.scene.render.tile_x = 64
        #bpy.context.scene.render.tile_y = 64

        #bpy.context.object.data.clip_start = 0.1
        #bpy.context.object.data.clip_end = 10000

        bpy.context.scene.world.cycles_visibility.scatter = False
        bpy.context.scene.world.cycles_visibility.transmission = False
        bpy.context.scene.world.cycles_visibility.glossy = False
        bpy.context.scene.world.cycles_visibility.diffuse = False
        bpy.context.scene.world.cycles_visibility.camera = False

        bpy.context.scene.world.cycles.sampling_method = 'NONE'

        bpy.context.scene.world.cycles.volume_sampling = 'MULTIPLE_IMPORTANCE'





        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0



        world = bpy.data.worlds['World']
        world.use_nodes = True

        # changing these values does affect the render.
        bg = world.node_tree.nodes['Background']
        bg.inputs[0].default_value[:3] = (0, 0, 0)
        bg.inputs[1].default_value = 1.0


    def defaultMaterial(self):

        self.material0 = bpy.data.materials.new(name="white")
        self.material0.use_nodes = True
        self.material0.node_tree.nodes.remove(self.material0.node_tree.nodes.get('Principled BSDF'))
        material_output = self.material0.node_tree.nodes.get('Material Output')
        emission = self.material0.node_tree.nodes.new('ShaderNodeEmission')
        emission.inputs[0].default_value = (1, 1, 1, 1)
        #material.use_transparent_shadow = False
        #material.sample_as_light = False
        self.material0.node_tree.links.new(material_output.inputs[0], emission.outputs[0])

    def addObject(self,x=0,y=0,z=0,name = "agent"):
        mesh = bpy.data.meshes.new(name)
        basic_sphere = bpy.data.objects.new(name, mesh)

        # Add the object into the scene.
        bpy.context.collection.objects.link(basic_sphere)

        # Select the newly created object
        bpy.context.view_layer.objects.active = basic_sphere
        basic_sphere.select_set(True)

        #bpy.context.view_layer.objects.active = obj
        # go edit mode

        # Construct the bmesh sphere and assign it to the blender mesh.
        bm = bmesh.new()
        #bmesh.ops.create_icosphere(bm, subdivisions=16,  diameter=1)
        bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=20, radius=.5)
        bm.to_mesh(mesh)
        bm.free()

        basic_sphere.select_set(True)
        basic_sphere.active_material = self.material0
        basic_sphere.location = mathutils.Vector((x,y,z))        
        basic_sphere.select_set(False)
        self.listObjects.append(basic_sphere)
        self.allVisualField = np.zeros((self.size[1],self.size[0],len(self.listObjects)))
        self.sine.stack(len(self.listObjects))

    def computeVisualField(self,agent):
        self.camera.positionUpdate(agent.location)
        self.camera.rotationUpdate(agent.rotation_euler)
        agent.hide_render = True
        self.render()
        agent.hide_render = False
        

    def computeAllVisualField(self):
        
        for k in range(0,len(self.listObjects)):
            self.computeVisualField(self.listObjects[k])
            self.allVisualField[:,:,k] = self.image()

    def derivateAllVisualField(self):
        self.allVisualFieldDPhi =\
         (np.roll(self.allVisualField[:,:,:],1,1)-np.roll(self.allVisualField[:,:,:],-1,1))
        self.allVisualFieldDTheta =\
         np.pad((self.allVisualField[:-2,:,:]-self.allVisualField[2:,:,:]),((1,1),(0,0),(0,0)),'constant', constant_values=0)
        self.allVisualFieldContour = (self.allVisualFieldDTheta!=0) + (self.allVisualFieldDPhi!=0)

    def moveCamera(self,*args):
        camera.translate(args)

    def moveObject(self,basic_sphere,x=0,y=0,z=0):
        phi = basic_sphere.rotation_euler.z
        dx = x*np.cos(phi) - y*np.sin(phi)
        dy = x*np.sin(phi) + y*np.cos(phi)
        dz = z
        basic_sphere.location += mathutils.Vector((dx,dy,dz)) 

    def rotateObject(self,basic_sphere,dx=0,dy=0,dz=0):
        x = basic_sphere.rotation_euler.x
        y = basic_sphere.rotation_euler.y
        z = basic_sphere.rotation_euler.z
        basic_sphere.rotation_euler = mathutils.Euler((x+dx*radTodDeg,y+dy*radTodDeg,z+dz*radTodDeg),"XYZ") 

    def image(self):
        return np.reshape(self.pixels,(self.size[1],self.size[0]))

    def visualFieldImage(self,idx):
        return np.reshape(self.allVisualField[:,idx],(self.size[1],self.size[0]))

    def render(self,write = False,kFrame = 0):
        bpy.context.scene.render.filepath = os.path.join("c:/tmp/", ("render%06d.jpg" % kFrame))
        bpy.ops.render.render(write_still = write)
        self.pixels = np.array(bpy.data.images['Viewer Node'].pixels)[::4]#[self.mask]


    def listCollection(self):
        for collection in bpy.data.collections:
           print(collection.name)
           for obj in collection.all_objects:
              print("obj: ", obj.name)

    def cleanScene(self):
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        for obj in bpy.context.scene.objects:
            obj.select_set(True)
            bpy.ops.object.delete()

    def __init__(self, size=512,dim = 3):
        self.cleanScene()
        self.dim = dim
        if size%2 == 0:
            size += 1
        size2 = int(size/2)
        if size2%2 == 0:
            size2 += 1
        self.size = [size,size2]

        self.setupRender()
        self.defaultMaterial()
        self.camera = Camera(dim = dim)
        self.sine = ProjectedSine(self.size)
        #self.mask = np.ones((self.size[0]*self.size[1]), dtype=bool)
        #self.mask[self.size[0]-1::self.size[0]] = False
        self.listObjects = []




