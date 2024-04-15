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
import json


pathData = "/data"

def getUUID():
    return uuid.uuid4().hex

def getUUIDPath(uu):
    return [uu[0:2],uu[2:4],uu[4:6],uu[6:8],uu[8:]]

def pather(path,params = []):
    for param in params:
        path = path + '/' + str(param)
    return path

def lDToDL(LD):
    #https://stackoverflow.com/questions/5558418/list-of-dicts-to-from-dict-of-lists
    DL = {}
    common_keys0 = set.intersection(*map(set, LD))
    for key0 in common_keys0:
        DL[key0] = {}
        for key1 in LD[0][key0].keys():
            values = []
            
            for d in LD:
                values.append(d[key0][key1])
            values = np.array(values)

            if key1 == "polarization":
                rang = '[0,1]'
                cmap = "div"
            elif key1 == "dphi":
                rang = '[-0.001,0.001]'
                cmap = "div"
            elif key1 == "v":
                rang = '[.5,1.5]'
                cmap = "div"
            else:
                rang = '['+str(np.min(values[:,2]))+','+str(np.max(values[:,2]))+']' 
                cmap = "seq"
            
            DL[key0][key1] = {"values" : arrayToString(values),"range" : rang,"cmap" : cmap}

    return DL

def arrayToString(x):
    x = np.array(x)
    return np.array2string(x, separator=', ')

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

    def getSortingKeys(self,exp):
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
        context = {'experiment': experiment,'project':project,"backward":"../"}
        #exp = experiments.objects.filter(project=project).filter(experiment=experiment)
        exp = experiments.objects.filter(project=project).filter(experiment=experiment)

        if "p0" in self.kwargs:
            fieldName = self.kwargs.get("p0", None)
            fieldValue = self.kwargs.get("value0", None)
            exp = exp.filter(**{fieldName: fieldValue}) 
            #print("fieldName : "+str(fieldName) + " fieldValue : "+str(fieldValue))
            context["p0"] = fieldName
            context["value0"] = fieldValue
            context["backward"] += "../"


        sortedKeys = self.getSortingKeys(exp)
        keys = list(sortedKeys.keys())

        if len(sortedKeys) == 2:
            context["display"] = True
            context["xname"] = keys[1]
            context["yname"] = keys[0]
            context["x"] = sortedKeys[keys[1]]
            context["y"] = sortedKeys[keys[0]]
            context["xTab"] = len(context["x"])
            context["yTab"] = len(context["y"])
            exp2 = exp.order_by(context["yname"],context["xname"],'?').values_list("repId", flat=True)
            yn = exp.order_by(context["yname"],context["xname"],'?').values_list(context["yname"], flat=True)
            xn = exp.order_by(context["yname"],context["xname"],'?').values_list(context["xname"], flat=True)
            videos = []
            globalData = []
            print(len(exp2))
            print(context)

            for y0 in context["y"]:
                for x0 in context["x"]:

                    fil = {context["xname"] : x0,context["yname"] : y0}
                    repIds = exp.filter(**fil).values_list("repId", flat=True)
                    vid = ""
                    datas = []
                    for repId in repIds:
                        pathID = getUUIDPath(repId)
                        path = pather("",[project])
                        path = pather(path,pathID)
                        path += "/"
                        if os.path.exists(pathData+"/"+path+repId+".mp4"):
                            vid = path+repId
                        if os.path.exists(pathData+"/"+path+"globalData.json"):
                            with open(pathData+"/"+path+"globalData.json") as f:
                                d = json.load(f)
                                datas.append(d)
                        else:
                            print("no")
                    print(len(repIds))
                    print(datas)
                    print(lDToDL(datas))

                    videos.append(vid)

            for k in range(0,len(exp2)):
                repId = exp2[k]
                pathID = getUUIDPath(repId)
                path = pather("",[project])
                path = pather(path,pathID)
                path += "/"
                #print(pathData+"/"+path+".mp4")
                if os.path.exists(pathData+"/"+path+repId+".mp4"):
                    #videos.append(path+repId)
                    #print(path)
                    if os.path.exists(pathData+"/"+path+"globalData.json"):
                        with open(pathData+"/"+path+"globalData.json") as f:
                            exp = exp.filter(**{"repId": repId})
                            
                            d = json.load(f)
                            for k0 in d.keys():
                                for k1 in d[k0].keys():
                                    d[k0][k1] = [xn[k],yn[k],d[k0][k1]]
                            globalData.append(d)

            print(len(globalData))                
            gData = lDToDL(globalData)
            
            context["videos"] = videos
            context["map"] = gData
            context["maps"] = {"x" : arrayToString(context["x"]),"y" : arrayToString(np.flip(context["y"]))}

        elif len(sortedKeys)>2:
            context["display"] = False
            context["keys"] = sortedKeys.items()
            
        else:
            context["display"] = False
        #print(context)
        
        return context

