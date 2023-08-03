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


from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
import panda3d.core as pc
import panda3d.bullet as bullet
import math
import numpy
import os
import numpy as np

radToDeg = 180.0/np.pi 
degToRad = np.pi/180.0 


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

        self.sinThetaAllD = np.array([self.sinThetaImD]*N).transpose((1,2,0))
        self.cosThetaCosPhiAllD = np.array([self.cosThetaCosPhiImD]*N).transpose((1,2,0))
        self.cosThetaSinPhiAllD = np.array([self.cosThetaSinPhiImD]*N).transpose((1,2,0))

    def __init__(self,size,dim = 3):
        

        u = np.linspace(0,1,size[0])
        v = np.linspace(0,1,size[1])
        self.phi,self.theta = self.equirectangularToDirection(u,v)
        if dim == 2:
            self.theta[0] = 0
        
        self.phi2d = np.array([self.phi,]*size[1])
        self.theta2d = np.array([self.theta,]*size[0]).transpose()

        if dim == 2:
            self.dThetaIm =  np.array([[1,]*size[0],]*size[1])
        else:
            self.dThetaIm =  np.array([[np.pi/size[1],]*size[0],]*size[1])
        self.dPhiIm = np.cos(self.theta2d)*np.array([[2*np.pi/size[0],]*size[0],]*size[1])



        self.dThetadPhiIm = self.dThetaIm*self.dPhiIm

        self.sinThetaIm = np.sin(self.theta2d) 
        self.cosThetaCosPhiIm = np.cos(self.theta2d) * np.cos(self.phi2d)  
        self.cosThetaSinPhiIm = np.cos(self.theta2d) * np.sin(self.phi2d) 
        
        self.sinThetaImD = np.sin(self.theta2d) * self.dThetadPhiIm
        self.cosThetaCosPhiImD = np.cos(self.theta2d) * np.cos(self.phi2d) * self.dThetadPhiIm 
        self.cosThetaSinPhiImD = np.cos(self.theta2d) * np.sin(self.phi2d) * self.dThetadPhiIm
        

        self.dTheta = np.matrix.flatten(self.dThetaIm)
        self.dPhi = np.matrix.flatten(self.dPhiIm)

        self.sinTheta = np.matrix.flatten(self.sinThetaIm)
        self.cosThetaCosPhi = np.matrix.flatten(self.cosThetaCosPhiIm)
        self.cosThetaSinPhi = np.matrix.flatten(self.cosThetaSinPhiIm)




class Projector:

    def setupRender(self):
        loadPrcFileData("", "window-type none" ) # Make sure we don't need a graphics engine (Will also prevent X errors / Display errors when starting on linux without X server)
        loadPrcFileData("", "audio-library-name null" ) # Prevent ALSA errors
        base = ShowBase()
        self.world = bullet.BulletWorld()
   
    def addObject(self,x=0,y=0,z=0,radius = .5,name = "agent"):
        shape = bullet.BulletSphereShape(radius)

        node = bullet.BulletRigidBodyNode(name)
        node.addShape(shape)
        node.setMass(0.0)
        node.setKinematic(True)

        sphere = render.attachNewNode(node)
        sphere.setPos(x, y, z)

        self.world.attachRigidBody(node)
        self.listObjects.append(sphere)
        self.allVisualField = np.zeros((self.size[1],self.size[0],len(self.listObjects)))
        self.sine.stack(len(self.listObjects))
        self.updatePhysics()

    def computeVisualField(self,agent):
        V = self.render(agent)
        return V
        
    def updatePhysics(self):
        self.world.doPhysics(1)


    def computeAllVisualField(self):
        self.updatePhysics()
        for k in range(0,len(self.listObjects)):
            V = self.computeVisualField(self.listObjects[k])
            self.allVisualField[:,:,k] = np.copy(V)

    def derivateAllVisualField(self):
        self.allVisualFieldDPhi =\
         (np.roll(self.allVisualField[:,:,:],1,1)-np.roll(self.allVisualField[:,:,:],-1,1))
        self.allVisualFieldDTheta =\
         np.pad((self.allVisualField[:-2,:,:]-self.allVisualField[2:,:,:]),((1,1),(0,0),(0,0)),'constant', constant_values=0)
        self.allVisualFieldContour = (self.allVisualFieldDTheta!=0) + (self.allVisualFieldDPhi!=0)


    def moveObject(self,basic_sphere,x=0,y=0,z=0):
        phi = basic_sphere.getHpr().z
        dx = x*np.cos(phi) - y*np.sin(phi)
        dy = x*np.sin(phi) + y*np.cos(phi)
        dz = z
        basic_sphere.setPos(basic_sphere,pc.Vec3(dx,dy,dz))  


    def setPosition(self,basic_sphere,x=0,y=0,z=0):
        basic_sphere.setPos(x,y,z) 

    def getPosition(self,basic_sphere):
        return np.array(basic_sphere.getPos()) 

    def setRotation(self,basic_sphere,x=0,y=0,z=0):
        basic_sphere.setHpr(x,y,z) 

    def getRotation(self,basic_sphere):
        return np.array(basic_sphere.getHpr()) 


    def setScale(self,basic_sphere,x=0,y=0,z=0):
        basic_sphere.setScale(pc.Vec3(x,y,z)) 

    def rotateObject(self,basic_sphere,dx=0,dy=0,dz=0):
        a = basic_sphere.getHpr()
        #dx *= radTodDeg
        #dy *= radTodDeg
        #dz *= radTodDeg
        basic_sphere.setHpr(basic_sphere,pc.Vec3(dx,dy,dz)) 

    def render(self,agent):
        V = np.zeros((self.size[1],self.size[0]))
        pos = agent.getPos()
        rot = agent.getHpr()
        phi = self.sine.phi + rot.z

        
        for k in range(0,self.size[0]):
            for j in range(0,self.size[1]):
                x = pos.x+10000*np.cos(self.sine.theta[j])*np.cos(phi[k])
                y = pos.y+10000*np.cos(self.sine.theta[j])*np.sin(phi[k])
                z = pos.z+10000*np.sin(self.sine.theta[j])
                result = self.world.rayTestClosest(pos,pc.Point3(x,y,z))
                if result.hasHit():
                    V[j,k] = 1
        
        return V

    def cleanScene(self):
        pass

    def __init__(self, size=512,dim = 3,texture = False,colors = False):
        self.cleanScene()
        self.dim = dim
        if size%2 == 0:
            size += 1
        if dim == 2:
            self.size = [size,1]
        else:
            size2 = int(size/2)
            if size2%2 == 0:
                size2 += 1
            self.size = [size,size2]
        self.texture = texture
        self.colors = colors
        self.setupRender()
        self.sine = ProjectedSine(self.size,self.dim)
        #self.mask = np.ones((self.size[0]*self.size[1]), dtype=bool)
        #self.mask[self.size[0]-1::self.size[0]] = False
        self.listObjects = []




