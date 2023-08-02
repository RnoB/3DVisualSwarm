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


import math
import numpy
import os
import numpy as np
import random


path = '~/tmp/'

def pather(path,expId):
    if not os.path.exists(path):
        os.makedirs(path)
    path = path  + expId+ '/'
    if not os.path.exists(path):
        os.makedirs(path)
    print(path)
    return path

def pathFile(path,name="positions.csv"):
    filepath = os.path.join(path, name)
    fd = open(filepath,'wb')
    fd.close()
    return filepath


class Simulator:


    # def writeCsv(X,N,U,name,path,writeMode = 0):
    #     filepath = os.path.join(path, name)
    #     if writeMode == 0:
    #         fd = open(filepath,'wb')
    #     elif writeMode == 1:
    #         checkFile = True
    #         while checkFile:
    #             try:
    #                 fd = open(filepath,'ab')
    #                 checkFile = False
    #             except Exception as e:
    #                 traceback.print_exc()
    #                 print()
    #     nId=np.zeros((10,1))
    #     nId = np.arange(0,N)
    #     wri = np.c_[nId,X]
    #     wri = np.c_[wri,U]
        
    #     np.savetxt(fd,np.c_[nId,X,U],delimiter=',',fmt= '%5.5f')

    #     fd.close()


    def integrator(self):
        self.vIntegral[:,0] = np.sum(self.proj.allVisualField*self.proj.sine.cosThetaCosPhiAllD,axis = (0,1))
        self.vIntegral[:,1] = np.sum(self.proj.allVisualField*self.proj.sine.cosThetaSinPhiAllD,axis = (0,1))
        self.vIntegral[:,2] = np.sum(self.proj.allVisualField*self.proj.sine.sinThetaAllD,axis = (0,1))

        self.vIntegral[:,3] = np.sum(self.proj.allVisualFieldContour*self.proj.sine.cosThetaCosPhiAll,axis = (0,1))
        self.vIntegral[:,4] = np.sum(self.proj.allVisualFieldContour*self.proj.sine.cosThetaSinPhiAll,axis = (0,1))
        self.vIntegral[:,5] = np.sum(self.proj.allVisualFieldContour*self.proj.sine.sinThetaAll,axis = (0,1))



    def computeVelocity(self):


        self.du[:,0] = (self.drag * (self.u0 - self.u[:,0] ) + self.parametersV[0,0] * ( self.parametersV[0,1] * self.vIntegral[:,0] + self.parametersV[0,2] * self.vIntegral[:,3] ) )
        self.du[:,1] =  self.parametersV[1,0] * (( self.parametersV[1,1] * self.vIntegral[:,1] + self.parametersV[1,2] * self.vIntegral[:,4] ))
        self.du[:,2] =  ( -self.drag * self.u[:,2] + self.parametersV[2,0] * ( self.parametersV[2,1] * self.vIntegral[:,2] + self.parametersV[2,2] * self.vIntegral[:,5] ))

        self.u += self.du*self.dt

        self.dx = self.u*self.dt
        self.dx[:,1] = self.du[:,1] * self.dt


    def updatePositions(self):
        positions = np.zeros((self.N,3))
        for k in range(0,self.N):
            obj = self.proj.listObjects[k]
            self.proj.rotateObject(obj,dz=self.dx[k,1])
            self.proj.moveObject(obj,x=self.dx[k,0],z=self.dx[k,2])
            positions = [k,obj.location.x,obj.location.y,obj.location.z,
                            obj.rotation_euler.x,obj.rotation_euler.y,obj.rotation_euler.z]
            self.positionWrite.append(positions)


    def writePositions(self):
        fd = open(self.filePath,'ab')
        np.savetxt(fd,np.array(self.positionWrite),delimiter=',',fmt= '%5.5f')

        fd.close()
        self.positionWrite = []

    def startSimulation(self,tMax = 0):
        if tMax > 0:
            self.tMax = tMax
        for t in range(0,int(self.tMax/self.dt)):
            self.proj.computeAllVisualField()
            self.proj.derivateAllVisualField()
            self.integrator()
            self.computeVelocity()
            self.updatePositions()
            if len(self.positionWrite)>100:
                self.writePositions()


    def initializeSwarm(self,R = 20,dim = 3):

        for k in range(0,self.N):
            x = R*random.random()-R/2
            y = R*random.random()-R/2
            if self.dim == 3:
                z = 0#R*random.random()-R/2
            else:
                z = 0
            phi = 2*np.pi*random.random()-np.pi
            print(x,y,z)
            print(phi)
            self.proj.addObject(x,y,z)
            self.proj.rotateObject(self.proj.listObjects[-1],0,0,phi)
            obj = self.proj.listObjects[k]
            if engine == "panda":
                location = obj.getPos()
                rotation = obj.getHpr()
            else:
                location = obj.location
                rotation = obj.rotation_euler
            positions = [k,location.x,location.y,location.z,
                            rotation.x,rotation.y,rotation.z]
            self.positionWrite.append(positions)



    def __init__(self,engine = "blender",size = 200, N = 2, dim = 3,dt = 0.1,tMax = 100,u0 = 1,drag = 1,path ="./",expId = "test",parametersV =np.array([[0,0,0],[0,0,0],[0,0,0]])):
        
        self.engine = engine
        if engine == "panda":
            from visualProjector import panda as vp
        else:
            from visualProjector import blender as vp
        self.N = N
        self.dim = dim
        self.dt = dt
        self.tMax = tMax
        self.drag = drag
        self.vIntegral = np.zeros((3,2))
        self.u = np.zeros((N,3))
        self.du = np.zeros((N,3))
        self.dx = np.zeros((N,3))
        self.vIntegral = np.zeros((N,6))
        self.u0 = u0
        self.u[:,0] = u0
        self.parametersV = np.array(parametersV)

        self.positionWrite = []

        self.path = pather(path,expId)
        self.filePath = pathFile(self.path)
        self.proj = vp.Projector(size = size,dim = dim)
        self.initializeSwarm(dim = dim)