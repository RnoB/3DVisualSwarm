#MIT License

#Copyright (c) 2024 Renaud Bastien

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
###########


import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import sys
import os
from analyzer.dbFiller import dbFiller
import scipy.spatial as sc
import json

def angleDifference(A1, A2):
    A = A1 - A2
    A = (A + np.pi) % (2 * np.pi) - np.pi
    return A

def polarization(X):
    phi = ((X[:,7,:]+np.pi)%2*np.pi)-np.pi
    nx = np.shape(phi)[0]
    P = []
    for k in range(0,nx):
        phi0 = phi[k,:]
        N = len(phi0)
        D = angleDifference(phi0[:,None],phi0[None,:])
        D = np.cos(D)
        P.append((D.sum()-np.trace(D))/(N*(N-1)))
    return P

def centerOfMass(X):
    return np.mean(X[:,2:5,:],axis = 2)
    
def centerOfMassSpeed(X,step = 10):
    center = centerOfMass(X)
    du = center[step:,:]-center[:-step,:]
    dt = X[step:,1,0]-X[:-step,1,0]
    v = np.linalg.norm(du,axis = 1)/dt
    phi  = np.arctan2(center[:,1],center[:,0])
    dphi = (phi[step:]-phi[:-step])/dt 

    return {"center":center,"phi":phi,"v":v,"dphi":dphi}

def computeAllDistance(X):
    D = sc.distance.pdist(X)
    D = sc.distance.squareform(D)
    np.fill_diagonal(D, np.nan)
    return D

def getAllDistance(X):
    dMean = []
    dMin = []
    dMax = []
    dMinMean = []
    dMaxMean = []
    for k in range(0,len(X[:,0,0])):
        D = computeAllDistance(X[k,2:5,:].T)
        dMean.append(np.nanmean(D))
        dMinMean.append(np.mean(np.nanmin(D,axis = 1)))
        dMaxMean.append(np.mean(np.nanmax(D,axis = 1)))
        dMin.append(np.nanmin(D))
        dMax.append(np.nanmax(D))
    distance = {"mean" : np.array(dMean),"min" : np.array(dMin),"max" : np.array(dMax),"minMean" : np.array(dMinMean),"maxMean" : np.array(dMaxMean)}
    return distance


class Analyzer:


    def start(self):
        for project in self.projects:
            self.experiments = self.anal.getExperiments(project)
            for exp in self.experiments:
                sortingKeys,sortedKeys = self.anal.getExperimentSortingKeys(project,exp)
                for key in sortedKeys:
                    
                    simId = self.anal.getSimIds(key)
                    
                    if len(simId)>0:
                        simId = simId[0][0]
                        repIds = self.anal.getRepIds(simId)
                        for repId in repIds:
                            repId = repId[0]
                            parameters = self.anal.getParameters(simId,project,exp)
                            X = self.anal.getDataSet(repId)
                            path = self.anal.getDataPath(repId)
                            N = parameters["N"]
                            mode = parameters["mode"]
                            center = centerOfMassSpeed(X,step = self.step)
                            distance = getAllDistance(X)
                            pol = polarization(X)
                            dataDistance = {"mean" : np.mean(distance["mean"][-1000:]),
                                            "min" : np.mean(distance["min"][-1000:]),
                                            "max" : np.mean(distance["max"][-1000:]),
                                            "minMean" : np.mean(distance["minMean"][-1000:]),
                                            "maxMean" : np.mean(distance["maxMean"][-1000:])}
                            dataCenter = {"v" : np.mean(center["v"][-1000:]),
                                          "dphi" : np.mean(center["dphi"][-1000:])}
                            group = {"polarization" : np.mean(pol[-1000:])}
                            data = {"distance" : dataDistance,"center" : dataCenter,"group" : group}
                            with open(path+"/globalData.json","w") as f:
                                json.dump(data,f)

    def __init__(self,step = 10):
        self.step = step
        self.anal = dbFiller.Analyzer()
        self.projects = self.anal.projects
