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
from numba import jit

radTodDeg = 180/np.pi 


def round(x, base=1):
    return base * np.round(x/base)

def roundInt(x):
    return np.round(x).astype(np.int)


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


class ProjectedSine:





    def stack(self,N):
        self.dPhiAll = np.array([self.dPhiIm]*N).transpose((1,2,0))
        self.dThetaAll = np.array([self.dThetaIm]*N).transpose((1,2,0))

        self.sinThetaAll = np.array([self.sinThetaIm]*N).transpose((1,2,0))
        self.cosThetaCosPhiAll = np.array([self.cosThetaCosPhiIm]*N).transpose((1,2,0))
        self.cosThetaSinPhiAll = np.array([self.cosThetaSinPhiIm]*N).transpose((1,2,0))


 

    def __init__(self,size):
        
        dPhi = 2*np.pi/(size[0])
        dTheta = np.pi/(size[1]-1)
        
        self.phi = np.linspace(-np.pi+dPhi,np.pi,size[0])
        self.theta = np.linspace(-np.pi/2,np.pi/2,size[1])
        
        
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




class Scene:



    def drawSphere(self,Xs,R,size):
        dPhi = 2*np.pi/(size[0])
        dTheta = np.pi/(size[1]-1)
        theta0 = Xs[2]
        phi0 = Xs[1]
        
        #i don't know what approximation to use
        #thetaApp = np.arcsin(R/Xs[0])
        thetaApp = np.arctan2(R,Xs[0])
        thetaMin = round(theta0-thetaApp,dTheta)
        thetaMax = round(theta0+thetaApp,dTheta)
        thetaN = 1+roundInt((thetaMax-thetaMin)/dTheta)

        if thetaN == 1:
            thetaIdx = np.floor(size[1]/2) + np.round(((theta0/dTheta)))

            phiIdx = (np.floor(size[0]/2) + round(phi0 / dPhi))%size[0]
            vIdx = np.array([phiIdx,thetaIdx])
        else:
            theta = np.linspace(thetaMin,thetaMax,thetaN)
            
            thetaSpace = theta - round(theta0,dTheta)

            theta[theta > np.pi/2.0] = np.pi - theta[theta > np.pi/2.0]
            theta[theta < -np.pi/2.0] = - np.pi - theta[theta < -np.pi/2.0]

            thetaIdx = np.floor(size[1]/2) + np.round(((theta/dTheta)))

            ## no idea where this 2 or the 4 is coming from
            phiLim = np.sqrt((thetaApp**2 - thetaSpace**2) / (np.cos(theta)**2))

            thetaIdx = thetaIdx[~np.isnan(phiLim)]

            phiLim = phiLim[~np.isnan(phiLim)]
            phiMax =  (np.floor(size[0]/2) + round((phi0 + phiLim) / dPhi))
            phiMin =  (np.floor(size[0]/2) + round((phi0 - phiLim) / dPhi))

            idx = []

            for thetaIdx,phiIdxMin,phiIdxMax in zip(thetaIdx,phiMin,phiMax):

                if phiIdxMax-phiIdxMin >size[0] or phiIdxMax == -2147483648:
                    phiIdx = np.arange(0,size[0])%size[0]


                else:
                    phiIdx = np.arange(phiIdxMin,phiIdxMax+1)%size[0]
                idxLine = np.empty((len(phiIdx),2))
                idxLine[:,1].fill(thetaIdx)
                idxLine[:,0] = phiIdx
                idx.append(idxLine)
            vIdx = np.concatenate(idx)
        return roundInt(vIdx)


    def rotateReferential(self,k,X):
        rotZ = self.rotation[k][2]
        x = np.cos(rotZ)*X[:,0] + np.sin(rotZ)*X[:,1]
        y = -np.sin(rotZ)*X[:,0] + np.cos(rotZ)*X[:,1]
        X[:,0] = x
        X[:,1] = y
        return X

    def computeVisualField(self,k):
        X = np.delete(self.position - self.position[k,:],k,0)
        X = self.rotateReferential(k,X)
        Xs = cartesianToSpherical(X)
        vIdx2 = []
        for k in range(0,np.shape(X)[0]):
            try:
                vIdxTmp = self.drawSphere(Xs[k,:],1,self.size)
            except:
                pass
            try:
                vIdx2.append(vIdxTmp)
                #vIdx = np.vstack([vIdx,vIdxTmp])
            except:
                #vIdx = vIdxTmp
                pass
        vIdx = np.vstack(vIdx2)
        V = np.zeros([self.size[1],self.size[0]])
        try:
            V[vIdx[:,1],vIdx[:,0]] = 1
        except:
            V[vIdx[1],vIdx[0]] = 1
            
        return V


    def computeAllVisualField(self):
        
        for k in range(0,len(self.position)):
            
            self.allVisualField[:,:,k] = self.computeVisualField(k)

    def derivateAllVisualField(self):
        self.allVisualFieldDPhi =\
         (np.roll(self.allVisualField[:,:,:],1,1)-np.roll(self.allVisualField[:,:,:],-1,1))
        self.allVisualFieldDTheta =\
         np.pad((self.allVisualField[:-2,:,:]-self.allVisualField[2:,:,:]),((1,1),(0,0),(0,0)),'constant', constant_values=0)
        self.allVisualFieldContour = (self.allVisualFieldDTheta!=0) + (self.allVisualFieldDPhi!=0)




    def getLength(self):
        return len(self.position)


    def addObject(self,position = (0,0,0),rotation = (0,0,0),bodySize = 1):
        self.position = np.vstack((self.position,position))
        self.rotation = np.vstack((self.rotation,rotation))
        np.append(self.bodySize,bodySize)
        self.allVisualField = np.zeros((self.size[1],self.size[0],len(self.position)))
        self.sine.stack(len(self.position))
        return self.getLength()-1

    def rotateObject(self,idx,rotation = (0,0,0)):
        self.rotation[idx] += rotation

    def rotationObject(self,idx,rotation = (0,0,0)):
        self.rotation[idx] = rotation

    def rotatePhiObject(self,idx,rotation = 0):
        self.rotation[idx][2] += rotation


    def translateObject(self,idx,translation = (0,0,0)):
        self.position[idx] += translation

    def translateLinearObject(self,idx,X = 0,Z = 0):
        phi = self.rotation[idx][2]
        self.position[idx] += [X * np.cos(phi),X * np.sin(phi),Z]

    def positionObject(self,idx,translation = (0,0,0)):
        self.position[idx] = translation




    def __init__(self, size=512):
        if size%2 == 1:
            size += 1
        size2 = np.int(size/2)
        if size2%2 == 0:
            size2 += 1
        self.size = [size,size2]

        self.sine = ProjectedSine(self.size)


        self.position = np.zeros((0,3))
        self.rotation = np.zeros((0,3))
        self.bodySize = np.zeros((0))




