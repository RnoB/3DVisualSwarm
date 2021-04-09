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
import bmesh
import mathutils
import math
import numpy
import os
import numpy as np

def projectedSine(size):
    sizeR = [size+1,np.int(size/2)+1]


    theta = np.linspace(-np.pi/2,np.pi/2,sizeR[1])
    phi = np.linspace(-np.pi,np.pi,sizeR[0])
    phi2d = np.array([phi,]*sizeR[1])
    theta2d = np.array([theta,]*sizeR[0]).transpose()
    #sinThetaIm = np.sin(theta2d)
    #cosThetaCosPhiIm = np.cos(theta2d) * np.cos(phi2d)
    #cosThetaSinPhiIm = np.cos(theta2d) * np.sin(phi2d)
    
    dTheta =  [[np.pi/sizeR[1],]*sizeR[0],]*sizeR[1]
    dPhi = np.cos(theta2d)*[[2*np.pi/sizeR[0],]*sizeR[0],]*sizeR[1]

    sinTheta = np.matrix.flatten(np.sin(theta2d))
    cosThetaCosPhi = np.matrix.flatten(np.cos(theta2d) * np.cos(phi2d))
    cosThetaSinPhi = np.matrix.flatten(np.cos(theta2d) * np.sin(phi2d))
