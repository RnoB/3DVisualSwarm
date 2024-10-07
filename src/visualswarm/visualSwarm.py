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
try:
    from writerserver import writer
except:
    writer = False



class Simulator:

    def integrator(self):
        self.vIntegral[:,0] = np.sum(self.proj.allVisualField*self.proj.sine.cosThetaCosPhiAllD,axis = (0,1))
        self.vIntegral[:,1] = np.sum(self.proj.allVisualField*self.proj.sine.cosThetaSinPhiAllD,axis = (0,1))
        self.vIntegral[:,2] = np.sum(self.proj.allVisualField*self.proj.sine.sinThetaAllD,axis = (0,1))

        self.vIntegral[:,3] = np.sum(self.proj.allVisualFieldContour*self.proj.sine.cosThetaCosPhiAll,axis = (0,1))
        self.vIntegral[:,4] = np.sum(self.proj.allVisualFieldContour*self.proj.sine.cosThetaSinPhiAll,axis = (0,1))
        self.vIntegral[:,5] = np.sum(self.proj.allVisualFieldContour*self.proj.sine.sinThetaAll,axis = (0,1))

        flow = self.parametersV[3,0] * self.proj.allVisualFieldDt 
        flowD = self.parametersV[3,1] * self.proj.allVisualFieldContourDt
        flowO = self.parametersV[3,2] * self.proj.allVisualFieldDt * self.proj.allVisualFieldContour
        
        self.vIntegral[:,6] = np.sum(flowO * self.proj.sine.cosThetaSinPhiAll+flowD * self.proj.sine.cosThetaCosPhiAll+flow * self.proj.sine.cosThetaCosPhiAllD,axis = (0,1))
        self.vIntegral[:,7] = np.sum(flowO * self.proj.sine.cosThetaCosPhiAll+flowD * self.proj.sine.cosThetaSinPhiAll+flow * self.proj.sine.cosThetaSinPhiAllD,axis = (0,1))
        self.vIntegral[:,8] = np.sum((flowO+flowD) * self.proj.sine.sinThetaAll+flow * self.proj.sine.sinThetaAllD,axis = (0,1))


    def computeVelocity(self):
        self.du[:,0] = (self.drag * (self.u0 - self.u[:,0] ) + self.parametersV[0,0] * ( self.parametersV[0,1] * self.vIntegral[:,0] + self.parametersV[0,2] * self.vIntegral[:,3]  + self.parametersV[0,3] * self.vIntegral[:,6] ) )
        self.du[:,1] =  self.parametersV[1,0] * (( self.parametersV[1,1] * self.vIntegral[:,1] + self.parametersV[1,2] * self.vIntegral[:,4]  + self.parametersV[1,3] * self.vIntegral[:,7] ))
        self.du[:,2] =  ( -self.drag * self.u[:,2] + self.parametersV[2,0] * ( self.parametersV[2,1] * self.vIntegral[:,2] + self.parametersV[2,2] * self.vIntegral[:,5] + self.parametersV[2,3] * self.vIntegral[:,8] ))

        self.u += self.du*self.dt

        self.dx = self.u*self.dt
        self.dx[:,1] = self.du[:,1] * self.dt

    def updatePositions(self):
        for k in range(0,self.N):
            obj = self.proj.listObjects[k]
            self.proj.rotateObject(obj,dz=self.dx[k,1])
            self.proj.moveObject(obj,x=self.dx[k,0],z=self.dx[k,2])
            
            location = self.proj.getPosition(obj)
            rotation = self.proj.getRotation(obj)
            
            positions = [k,self.t,location[0],location[1],location[2],
                           rotation[0],rotation[1],rotation[2],
                           self.u[k,0],self.u[k,0],self.u[k,0],
                           self.du[k,0],self.du[k,0],self.du[k,0]]
            if self.write:
                self.positionWrite.append(positions)
                

    def writePositions(self):
        if len(self.positionWrite)>0:
            toWrite = np.concatenate(self.positionWrite)
            self.client.write(toWrite)
            self.positionWrite = []

    def start(self,tMax = 0):
        if tMax > 0:
            self.tMax = tMax
        for k in range(0,int(self.tMax/self.dt)):
            self.t += self.dt
            self.proj.computeAllVisualField()
            self.proj.derivateAllVisualField()
            self.integrator()
            self.computeVelocity()
            self.updatePositions()
            if len(self.positionWrite)>self.bufferSize:
                self.writePositions()
        self.writePositions()

    def stop(self):
        self.client.stop()

    def initializeSwarm(self,R = 20,dim = 3):
        self.proj.addObject(0,0,0,nObjects = self.N)
        for k in range(0,self.N):
            x = R*random.random()-R/2
            y = R*random.random()-R/2
            if self.dim == 3:
                z = R*random.random()-R/2
            else:
                z = 0
            phi = 2*np.pi*random.random()-np.pi
            
            self.proj.moveObjects(self.proj.listObjects[k],x,y,z)
            self.proj.rotateObject(self.proj.listObjects[k],0,0,phi)
            obj = self.proj.listObjects[k]

            location = self.proj.getPosition(obj)
            rotation = self.proj.getRotation(obj)

            positions = [k,0,location[0],location[1],location[2],
                           rotation[0],rotation[1],rotation[2],
                           self.u[k,0],self.u[k,0],self.u[k,0],
                           self.du[k,0],self.du[k,0],self.du[k,0]]
            self.positionWrite.append(positions)

    def getName(self):
        return self.name

    def setScale(self,sx,sy,sz,k = -1):
        if k == -1:
            for j in range(0,self.N):
                self.proj.setScale(j,sx,sy,sz)
        else:
            self.proj.setScale(k,sx,sy,sz)

    def __init__(self,engine = "rasterizer",size = 200, N = 2, dim = 3,
                      dt = 0.1,tMax = 100,u0 = 1,drag = .1,
                      parametersV = np.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]),
                      bufferSize = 100,ip = "localhost" , port = 1234,project = "project",write = True):
        
        self.engine = engine
        if engine == "panda":
            from visualswarm.visualProjector import panda as vp
        elif engine == "blender":
            from visualswarm.visualProjector import blender as vp
        elif engine == "generalized":
            from visualswarm.visualProjector import generalized as vp
        else:
            from visualswarm.visualProjector import rasterizer as vp
        if bufferSize>N:
            self.bufferSize = bufferSize
        else:
            self.bufferSize = N-1

        self.N = N
        self.dim = dim
        self.dt = dt
        self.t = 0 
        self.tMax = tMax
        self.drag = drag
        self.vIntegral = np.zeros((3,2))
        self.u = np.zeros((N,3))
        self.du = np.zeros((N,3))
        self.dx = np.zeros((N,3))
        self.vIntegral = np.zeros((N,9))
        self.u0 = u0
        self.u[:,0] = u0
        self.parametersV = np.array(parametersV)

        self.positionWrite = []

        self.proj = vp.Projector(size = size,dim = dim)
        self.initializeSwarm(dim = dim)
        self.write = write
        if writer and self.write:
            self.client = writer.Client(N = 14,ip = ip,port = port,project = project)
            self.client.start()
            self.name = self.client.getName()
        else:
            self.write = False
            self.name = "test"
