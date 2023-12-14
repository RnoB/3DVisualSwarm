from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from decimal import Decimal
from .models import experiments
from malkoDB.plotTab import plotTab
from django.db.models import CharField
import uuid
import numpy as np
import os
pathData = "/data"

def getUUID():
    return uuid.uuid4().hex

def getUUIDPath(uu):
    return [uu[0:2],uu[2:4],uu[4:6],uu[6:8],uu[8:]]

def pather(path,params = []):
    for param in params:
        path = path + '/' + str(param)
    return path



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
        exp = experiments.objects.order_by("experiment").values_list("experiment", flat=True).distinct()
        context = {'exp': exp,'project':project}
        return context

class ExperimentView(generic.ListView):
    model = experiments
    template_name = 'malkoDB/indexExperiment.html'
    context_object_name = 'experiments_list'

    def getSortingKeys(self,project,experiment):
        exp = experiments.objects.filter(project=project).filter(experiment=experiment)
        #print(exp)
        sortedKeys = {}
        for key in experiments._meta.get_fields():
            if not isinstance(key,CharField) and key.name != 'id' and key.name != "mode":
                var = exp.order_by(key.name).values_list(key.name, flat=True).distinct()
                if len(var)>1:
                    sortedKeys[key.name] = np.sort(np.array(var))
        return sortedKeys
            
            

    def get_queryset(self):
        
        project = self.kwargs.get("project", None)
        experiment = self.kwargs.get("experiment", None)
        context = {'experiment': experiment,'project':project}
        sortedKeys = self.getSortingKeys(project,experiment)
        keys = list(sortedKeys.keys())
        exp = experiments.objects.filter(project=project).filter(experiment=experiment)
        
        if len(sortedKeys) == 2:
            context["display"] = True
            context["xname"] = keys[0]
            context["yname"] = keys[1]
            context["x"] = sortedKeys[keys[0]]
            context["y"] = sortedKeys[keys[1]]
            exp2 = exp.order_by(keys[0],keys[1],'?').values_list("repId", flat=True)
            videos = []
            for repId in exp2:
                pathID = getUUIDPath(repId)
                path = pather("",[project])
                path = pather(path,pathID)
                path += "/"+repId
                #print(pathData+"/"+path+".mp4")
                if os.path.exists(pathData+"/"+path+".mp4"):
                    videos.append(path)
                    #print(path)
            
            context["videos"] = videos

        else:
            context["display"] = False
        #print(context)
        
        return context

