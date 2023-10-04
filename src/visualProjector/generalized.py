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


import numpy as np
import scipy.spatial as sc

radToDeg = 180.0/np.pi 
degToRad = np.pi/180.0 

def round(x, base=1):
    return base * np.round(x/base)

def roundInt(x):
    return np.round(x).astype(int)


def computeAllDistance(X):
    return sc.distance.pdist(X)

def computeAllDistanceInPlane(X):
    return sc.distance.pdist(X[:,0:2])

def getDistance(D,k,j):
    if k<j:
        l = len(X) * k + j - ((k + 2) * (k + 1)) // 2
    if k>j:
        l = len(X) * j + k - ((j + 2) * (j + 1)) // 2
    return D[l]

def getAllDistance(D,k,L):
    j1 = np.arange(0,k)
    j2 = np.arange(k+1,L)
    l1 = L * j1 + k - ((j1 + 2) * (j1 + 1)) // 2
    l2 = L * k + j2 - ((k + 2) * (k + 1)) // 2
    l = np.hstack((l1,l2))
    return(D[l])


def cartesianToSpherical(X,rp = None,rs = None):
    Xs = np.zeros(X.shape)
    if rp == None:
        rp = X[:,0]**2 + X[:,1]**2
    if rs == None:
        rs = np.sqrt(rp + X[:,2]**2)
    Xs[:,0] = rs
    #ptsnew[:,4] = np.arctan2(np.sqrt(xy), xyz[:,2]) # for elevation angle defined from Z-axis down
    Xs[:,2] = np.arctan2(X[:,2], np.sqrt(rp)) # for elevation angle defined from XY-plane up
    Xs[:,1] = np.arctan2(X[:,1], X[:,0])
    return Xs

def angleDiff(A1, A2):
    A1 = (A1 + np.pi) % (2 * np.pi) - np.pi
    A2 = (A2 + np.pi) % (2 * np.pi) - np.pi
    A = A1 - A2
    A = (A + np.pi) % (2 * np.pi) - np.pi
    return A

class ProjectedSine:
    
    def stack(self,N):
        dim = N-1
        if N-1<1:
            dim = 1
        self.dPhiAll = np.zeros((1,dim,N))
        self.dThetaAll = np.zeros((1,dim,N))

        self.sinThetaAll = np.zeros((1,dim,N))
        self.cosThetaCosPhiAll = np.zeros((1,dim,N))
        self.cosThetaSinPhiAll = np.zeros((1,dim,N))

        self.sinThetaAllD = np.zeros((1,dim,N))
        self.cosThetaCosPhiAllD = np.zeros((1,dim,N))
        self.cosThetaSinPhiAllD = np.zeros((1,dim,N))


    def __init__(self):
        self.dPhiAll = [0]
        self.dThetaAll = [0]

        self.sinThetaAll = [0]
        self.cosThetaCosPhiAll = [0]
        self.cosThetaSinPhiAll = [0]

        self.sinThetaAllD = [0]
        self.cosThetaCosPhiAllD = [0]
        self.cosThetaSinPhiAllD = [0]
        





class Projector:








    def rotateReferential(self,k,X):
        rotZ = self.rotation[k][2]
        x = np.cos(rotZ)*X[:,0] + np.sin(rotZ)*X[:,1]
        y = -np.sin(rotZ)*X[:,0] + np.cos(rotZ)*X[:,1]
        X[:,0] = x
        X[:,1] = y
        return X
   
    def addObject(self,x=0,y=0,z=0,radius = .5,name = "agent"):
        self.position = np.vstack((self.position,np.array((x,y,z))))
        self.positionOld = np.vstack((self.positionOld,np.array((x,y,z))))
        self.rotation = np.vstack((self.rotation,np.array((0,0,0))))
        self.scale = np.vstack((self.scale,np.array((2*radius,2*radius,2*radius))))
        N = len(self.listObjects)
        dim = N-1
        if N-1<1:
            dim = 1
        self.allVisualField = np.zeros((1,dim,N))
        self.allVisualFieldOld = np.zeros((1,dim,N))
        self.listObjects.append(len(self.listObjects))
        

    def interactionFunction(self,r,attractive = True):
        if attractive:
            f = (2/np.pi) * np.arctan(r)
        else:
            f = 1 - (2/np.pi) * np.arctan(r) 
        return f

    def computeVisualField(self,agent):
        k = agent
        X = np.delete(self.position - self.position[k,:],k,0)
        sca = np.delete(self.scale,k,0)
        rot = np.delete(self.rotation,k,0)
        #X = self.position - self.position[k,:]
        X = self.rotateReferential(k,X)
        Xs = cartesianToSpherical(X)
        N = len(Xs[:,0])
        V = np.zeros((N,5))
        for j in range(0,N):
            V[j,0] = self.interactionFunction(Xs[j,0],True)
            V[j,1] = self.interactionFunction(Xs[j,0],False)
            V[j,2] = np.cos[Xs[j,2]] * np.cos[Xs[j,1]]
            V[j,3] = np.cos[Xs[j,2]] * np.sin[Xs[j,1]]
            V[j,4] = np.sin[Xs[j,2]] 
        return np.arrayV
        



    def computeAllVisualField(self):
        
        for k in range(0,len(self.listObjects)):
            V = self.computeVisualField(self.listObjects[k])
            self.allVisualField[1,:,k] = np.copy(V[:,0])
            self.allVisualFieldContour[1,:,k] = np.copy(V[:,1])
            self.cosThetaCosPhiIm[1,:,k] = np.copy(V[:,2])
            self.cosThetaSinPhiIm[1,:,k] = np.copy(V[:,3])
            self.sinThetaIm[1,:,k] = np.copy(V[:,4])
            self.cosThetaCosPhiImD[1,:,k] = np.copy(V[:,2])
            self.cosThetaSinPhiImD[1,:,k] = np.copy(V[:,3])
            self.sinThetaImD[1,:,k] = np.copy(V[:,4])

    def derivateAllVisualField(self):
        pass


    def moveObject(self,basic_sphere,x=0,y=0,z=0):
        phi = self.rotation[basic_sphere,2]
        dx = x*np.cos(phi) - y*np.sin(phi)
        dy = x*np.sin(phi) + y*np.cos(phi)
        dz = z
        self.positionOld[basic_sphere] = np.copy(self.position[basic_sphere])
        self.position[basic_sphere]+=np.array((dx,dy,dz))  


    def setPosition(self,basic_sphere,x=0,y=0,z=0):
        self.position[basic_sphere]=np.array((x,y,z))

    def getPosition(self,basic_sphere):
        return self.position[basic_sphere]

    def setRotation(self,basic_sphere,x=0,y=0,z=0):
        self.rotation[basic_sphere]=np.array((x,y,z)) 

    def getRotation(self,basic_sphere):
        return self.rotation[basic_sphere]


    def setScale(self,basic_sphere,x=0,y=0,z=0):
        self.scale[basic_sphere] = np.array((x,y,z))

    def rotateObject(self,basic_sphere,dx=0,dy=0,dz=0):
        self.rotation[basic_sphere]+=np.array((dx,dy,dz))

    def getObjects(self,idx = 0):
        return self.listObjects[idx]

    def cleanScene(self):
        pass

    def __init__(self, size=512,dim = 3,texture = False,colors = False,tanApprox = False,insideInvisible = True):

   
        self.sine = ProjectedSine()
        self.position = np.zeros((0,3))
        self.positionOld = np.zeros((0,3))
        self.velocity = np.zeros((0,3))
        self.rotation = np.zeros((0,3))
        self.scale = np.zeros((0,3))
        self.listObjects = []









