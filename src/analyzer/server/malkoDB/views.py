from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from decimal import Decimal
from .models import experiments
from malkoDB.plotTab import plotTab

import numpy as np


class IndexView(generic.ListView):
  model = experiments
  template_name = 'malkoDB/index.html'
  context_object_name = 'experiments_list'
  
  def get_queryset(self):
    project = experiments.objects.order_by("project").values_list("project", flat=True).distinct()
    return {'exp':project}


class ProjectView(generic.ListView):
  model = experiments
  template_name = 'malkoDB/indexProject.html'
  context_object_name = 'experiments_list'
  def get_queryset(self):
    
    project = self.kwargs.get("project", None)
    print(project)
    exp = experiments.objects.order_by("experiment").values_list("experiment", flat=True).distinct()
    print(exp)
    context = {'exp': exp,'project':project}
    return context

class ExperimentView(generic.ListView):
  model = experiments
  template_name = 'malkoDB/indexExperiment.html'
  context_object_name = 'experiments_list'
  def get_queryset(self):
    
    project = self.kwargs.get("project", None)
    print(project)
    exp = experiments.objects.order_by("experiment").values_list("experiment", flat=True).distinct()
    print(exp)
    context = {'exp': exp,'project':project}
    return context


class IndexdVuView(generic.ListView):
  model = experiments
  template_name = 'malkoDB/index2.html'
  context_object_name = 'experiments_list'
  
  def get_queryset(self):
    project = self.kwargs.get("project", None)
    experiment = self.kwargs.get("experiment", None)
    exp = experiments.objects.order_by("N").values_list("N", flat=True).distinct()
    return {'exp':exp,'project':N}





class VisNView(generic.ListView):
  model = experiments
  template_name = 'malkoDB/VisN.html'
  context_object_name = 'experiments_list'

  def get_queryset(self):
    dVu = self.kwargs.get("dVu", None) 
    N = self.kwargs.get("N", None)
    project = self.kwargs.get("project", None)
    
    if project =='Vuu':
      Vu = 'Vuu'
      Vp = 'dtVp'
      exp2 = experiments.objects.filter(Vpp=0.1).filter(N=N).order_by(Vu,Vp,'?')
    elif project=='Vpp':
      Vu = 'Vpp'
      Vp = 'dtVp'
      exp2 = experiments.objects.filter(Vuu=0.5).filter(N=N).order_by(Vu,Vp,'?')
    
    rep = np.array(exp2.values_list('youtube', flat=True))
    repVu = np.array(exp2.values_list(Vu, flat=True))
    repVp = np.array(exp2.values_list(Vp, flat=True))
    sim = exp2.values_list('expId', flat=True)
    simIdx = np.sort(np.unique(sim,return_index=True)[1])

    repVideo = np.vstack((repVu[simIdx],repVp[simIdx]))
    tmp,uniqueIdx = np.unique(repVideo, axis=1,return_index=True)
    print(len(uniqueIdx))
    if project == "Vppx":
      repVp = repVp[uniqueIdx]
      idx = np.where(repVp == 0.01)
      print(idx)
      uniqueIdx = np.delete(uniqueIdx,idx[0])
      repVp = repVp[uniqueIdx]      
      idx = np.where(repVp == 0.02)
      uniqueIdx = np.delete(uniqueIdx,idx[0])    
    exp = rep[simIdx[uniqueIdx]]
    Vuu = np.unique(np.array(exp2.values_list(Vu, flat=True)))
    Vpp = np.unique(np.array(exp2.values_list(Vp, flat=True)))

    xTab = len(Vuu)
    yTab = len(Vpp)

    if len(exp)>0:
      L = True
    else:
      L=False

    print(L)
    context = {'L' : L,
               'exp': exp,
               'project': project,
               'N':N,
               'xTab':xTab,
               'yTab':yTab,
               'Vuu':Vuu,
               'Vpp':Vpp
               }
    return context
