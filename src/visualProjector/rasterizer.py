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

    def equirectangularToDirection(self,u,v):
        rang = [-2*np.pi, np.pi, -np.pi, np.pi/2.0]
        phi = rang[0] * u + rang[1];
        theta = - (rang[2] * v + rang[3]);
        return phi[:-1],theta

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
        

        u = np.linspace(0,1,size[0]+1)
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

    def drawSphere(self,Xs,scale,size):

        R = scale[0]/2.0
        dPhi = 2*np.pi/(size[0])
        dTheta = np.pi/(size[1]-1)
        theta0 = Xs[2]
        phi0 = -((np.pi+Xs[1])%(2*np.pi)-np.pi)
        if self.tanApprox:
            thetaApp = np.arctan2(R,Xs[0])
        else:
            thetaApp = np.arcsin(R/Xs[0])
            
        thetaMin = round(theta0-thetaApp,dTheta)
        thetaMax = round(theta0+thetaApp,dTheta)
        thetaN = 1+roundInt((thetaMax-thetaMin)/dTheta)

        if thetaN == 1:
            thetaIdx = np.floor(size[1]/2) + np.round(((theta0/dTheta)))

            phiIdx = (np.floor(size[0]/2) + round(phi0 / dPhi))%size[0]
            vIdx = np.array([phiIdx,thetaIdx], dtype='int')
        else:
            #theta = np.linspace(thetaMin,thetaMax,thetaN)
            theta = thetaMin+(thetaMax-thetaMin)*(self.phiIdxList[0:thetaN]/(thetaN-1))

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
            idx2 = []

            for thetaIdx,phiIdxMin,phiIdxMax in zip(thetaIdx,phiMin,phiMax):

                if phiIdxMax-phiIdxMin >size[0] or phiIdxMax == -2147483648:
                    idxLine = np.empty((size[0],2), dtype='int')
                    idxLine[:,1].fill(thetaIdx)
                    idxLine[:,0] = self.phiIdxList[0:size[0]]


                else:
                    #phiIdx = np.arange(phiIdxMin,phiIdxMax+1)
                    #phiIdx = phiIdx%size[0]
                    idx0 = int(phiIdxMin+size[0])
                    idx1 = int(phiIdxMax+1+size[0])
                    idxLine = np.empty((idx1-idx0,2), dtype='int')
                    idxLine[:,1].fill(thetaIdx)
                    
                    idxLine[:,0] = self.phiIdxList[idx0:idx1]




                
                #idxLine = np.empty((len(phiIdx),2))
                #idxLine[:,1].fill(thetaIdx)
                #idxLine[:,0] = phiIdx

                idx.append(idxLine)
            try:    
                vIdx = np.concatenate(idx)
            except:
                VIdx = []
        return vIdx

    def drawDisk(self,Xs,dPhi,scale = [1,1,1],rotation = [0,0,0]):
        #print(scale)
        if scale[1] == scale[0]:
            R = scale[0]/2.0
            idxPhi = int(round(-(np.pi+Xs[1])/dPhi  ))
            if self.tanApprox:
                dP = int(round(np.arctan2(R,Xs[0])/dPhi   ))
            else:
                if Xs[0]>R:
                    dP = int(round(np.arcsin(R/Xs[0])/dPhi   ))
                else:
                    dP = int(round(np.pi/dPhi   ))
            vIdx = np.arange(idxPhi-dP,idxPhi+dP+1)
            vIdx[vIdx<0]=self.size[0]+vIdx[vIdx<0]
            vIdx=vIdx%self.size[0]
        else:
            try:
                y = -Xs[0]*np.sin(Xs[1])
                x = Xs[0]*np.cos(Xs[1])
                r0 = scale[0]/2.0
                r1 = scale[1]/2.0
                psi0 = rotation[2]


                
                uc = (x * np.cos(psi0) - y * np.sin(psi0))/r0
                us = (x * np.sin(psi0) + y * np.cos(psi0))/r1            
                
                delta = np.sqrt(us**2-(1-uc**2))
                theta1 = 2*np.arctan((-delta+us)/(1-uc)) 
                theta2 = 2*np.arctan((delta+us)/(1-uc))
                
                ex1 = r0 * np.cos(theta1)
                ey1 = r1 * np.sin(theta1)
                ex2 = r0 * np.cos(theta2)
                ey2 = r1 * np.sin(theta2)


                psi0 = -psi0
                x1 = x + ex1 * np.cos(psi0) + ey1 * np.sin(psi0)
                y1 = y + ex1 * np.sin(psi0) - ey1 * np.cos(psi0)
                x2 = x + ex2 * np.cos(psi0) + ey2 * np.sin(psi0)
                y2 = y + ex2 * np.sin(psi0) - ey2 * np.cos(psi0)
                

                dPsi1 = int(self.size[0] * (np.pi+np.arctan2(y1,x1))/(2*np.pi))
                dPsi2 = int(self.size[0] * (np.pi+np.arctan2(y2,x2))/(2*np.pi))
                vIdx = np.arange(dPsi1,dPsi2,1).astype(int)
                
                vIdx[vIdx<0]=self.size[0]+vIdx[vIdx<0]
                vIdx=vIdx%self.size[0]
            except:
                if self.insideInvisible:
                    vIdx = []
                else:
                    vIdx = np.arange(0,self.size[0],1).astype(int)

        return vIdx



    def vision2d(self,X,Xs,scale,rotation):
        dPhi = 2*np.pi/(self.size[0])
        V = np.zeros(self.size[0])                
        #loop through all individuals
        sort = Xs[:, 0].argsort()[::-1]
        scale = scale[sort]
        rotation = rotation[sort]
        Xs = Xs[sort]

        vIdx2 = []
        for j in range(0,np.shape(X)[0]):
            if Xs[j,0]>0:
                vIdxTmp = self.drawDisk(Xs[j,:],dPhi,scale[j],rotation[j])
                vIdx2.append(vIdxTmp)

        vIdx = np.hstack(vIdx2).astype(int)
        V[vIdx] = 1
        return V  

    def vision3d(self,X,Xs):
        vIdx2 = []
        for j in range(0,np.shape(X)[0]):
            vIdxTmp = self.drawSphere(Xs[j,:],self.scale[j],self.size)

            vIdx2.append(vIdxTmp)
        vIdx = np.vstack(vIdx2)
        V = np.zeros([self.size[1],self.size[0]])
        try:
            V[vIdx[:,1],vIdx[:,0]] = 1
        except:
            V[vIdx[1],vIdx[0]] = 1
        return V


    def rotateReferential(self,k,X):
        rotZ = self.rotation[k][2]
        x = np.cos(rotZ)*X[:,0] + np.sin(rotZ)*X[:,1]
        y = -np.sin(rotZ)*X[:,0] + np.cos(rotZ)*X[:,1]
        X[:,0] = x
        X[:,1] = y
        return X
   
    def addObject(self,x=0,y=0,z=0,radius = .5,name = "agent"):
        self.position = np.vstack((self.position,np.array((x,y,z))))
        self.rotation = np.vstack((self.rotation,np.array((0,0,0))))
        self.scale = np.vstack((self.scale,np.array((2*radius,2*radius,2*radius))))
        self.allVisualField = np.zeros((self.size[1],self.size[0],len(self.position)))
        self.sine.stack(len(self.position))
        self.listObjects.append(len(self.listObjects))
        


    def computeVisualField(self,agent):
        k = agent
        X = np.delete(self.position - self.position[k,:],k,0)
        sca = np.delete(self.scale,k,0)
        rot = np.delete(self.rotation,k,0)
        #X = self.position - self.position[k,:]
        X = self.rotateReferential(k,X)
        Xs = cartesianToSpherical(X)
        if self.dim == 2:
            V = self.vision2d(X,Xs,sca,rot) 
        else:
            V = self.vision3d(X,Xs)

        return V
        
    def updatePhysics(self):
        self.world.doPhysics(1)


    def computeAllVisualField(self):
        
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
        phi = self.rotation[basic_sphere,2]
        dx = x*np.cos(phi) - y*np.sin(phi)
        dy = x*np.sin(phi) + y*np.cos(phi)
        dz = z
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
        self.dim = dim
        if size%2 == 1:
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
   
        self.sine = ProjectedSine(self.size,self.dim)
        self.tanApprox = tanApprox
        self.position = np.zeros((0,3))
        self.rotation = np.zeros((0,3))
        self.scale = np.zeros((0,3))

        self.phiIdxList = np.tile(np.arange(0,self.size[0], dtype='int'),3)
        self.listObjects = []
        self.insideInvisible = insideInvisible








