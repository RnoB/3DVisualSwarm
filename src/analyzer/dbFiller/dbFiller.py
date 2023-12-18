#MIT License

#Copyright (c) 2023 Renaud Bastien

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
import sqlite3
import json
import uuid
import os.path
import datetime
import random
import itertools
import pandas as pd
from writerserver import writer



def getUUID():
    return uuid.uuid4().hex

def recursive(r,n,values,allValues):
    for k in r[n]["range"]:
        values[r[n]["k"]] = k
        if n<len(r)-1:
            recursive(r,n+1,values,allValues)
        else:
            allValues.append(np.copy(values))

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def separateData(data):
    ids = np.unique(data[:,0])
    N = len(ids)
    nx = int(np.shape(data)[0]/N)
    ny = np.shape(data)[1]
    X = np.zeros((nx,ny,N))
    for k in range(0,N):
        mask = data[:,0] == k
        X[:,:,k] = data[mask,:] 
    return X
    
def dictListsToListDict(DL):
    keys, values = zip(*DL.items())
    permutations_dicts = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return permutations_dicts



class Filler:

    def getTypes(self):
        conn = sqlite3.connect(self.dbSimulations)
        c = conn.cursor()
        c.execute("""PRAGMA table_info(parameters) """)
        columns = c.fetchall()
        tmp,keys,types,tmp,tmp,tmp =  zip(*columns)
        self.types = dict(zip(keys, types))
        conn.close()

    def generator(self):
        conn = sqlite3.connect(self.dbSimulations)
        c = conn.cursor()
        parameters = """(simId text,"""
        for key in self.dbConfig.keys():
            parameters+= key+" "+self.dbConfig[key]["type"]+","
        parameters= parameters[:-1]+""")"""      
        c.execute("""CREATE TABLE parameters """+parameters)
        conn.commit()
        conn.close()

    def generatorReplicates(self):
        conn = sqlite3.connect(self.dbReplicates)
        c = conn.cursor()
        parameters = """(simId text,repId text,date text)"""
        c.execute("""CREATE TABLE simulations """+parameters)
        conn.commit()
        conn.close()

    def generatorAnalyzed(self):
        conn = sqlite3.connect(self.dbAnalyzed)
        c = conn.cursor()
        parameters = """(repId text,date text)"""
        c.execute("""CREATE TABLE simulations """+parameters)
        conn.commit()
        conn.close()


    def printValues(self):
        conn = sqlite3.connect(self.dbSimulations)
        c = conn.cursor()
        c.execute("""PRAGMA table_info(parameters) """)
        columns = c.fetchall()
        print(columns)
        conn.close()

    def reloadJSON(self,jsonFile = "db/db.json"):
        f = open(jsonFile)
        self.dbConfig = json.load(f)
        f.close()



    def getSimIds(self,parameters):
        line = "select simId from parameters where"
        values = ()
        for key in parameters.keys():
            line+=" "+key+" = ? and"
            if self.types[key] == 'INTEGER':
                values = values+(int(parameters[key]),)
            else:
                values = values+(parameters[key],)
        conn = sqlite3.connect(self.dbSimulations, check_same_thread=False)
        c = conn.cursor()
        c.execute(line[:-4],values)
        simIds = c.fetchall()[0]
        conn.close()
        return simId

    def checkExists(self,parameters):
        line = "select simId from parameters where"
        lineProject = ""
        values = ()
        valuesProject = ()

        keys = list(self.dbConfig.keys())
        for k in range(0,len(keys)):
            key = keys[k]
            if key != "project" and key != "experiment":
                line+=" "+key+" = ? and"
                if self.types[key] == 'INTEGER':
                    values = values+(int(parameters[k]),)
                else:
                    values = values+(parameters[k],)
            else:
                lineProject+=" "+key+" = ? and"
                if self.types[key] == 'INTEGER':
                    valuesProject = valuesProject+(int(parameters[k]),)
                else:
                    valuesProject = valuesProject+(parameters[k],)

        conn = sqlite3.connect(self.dbSimulations, check_same_thread=False)
        c = conn.cursor()
        c.execute(line+lineProject[:-4],values+valuesProject)
        simIds = c.fetchall()
        if len(simIds)>0:
            simId = -1
        else:
            c.execute(line[:-4],values)
            simIds = c.fetchall()
            if len(simIds)>0:
                simId = simIds[0]
            else:
                simId = getUUID() 
        conn.close()
        return simId
        

    def fillParameters(self):
        conn = sqlite3.connect(self.dbSimulations)
        c = conn.cursor()
        values = []
        valuesRange = []
        for key in self.dbConfig.keys():
            values.append(self.dbConfig[key]["default"])
            if "range" in self.dbConfig[key]:
                valuesRange.append({"k":len(values)-1,"range":self.dbConfig[key]["range"]})
        nValues = "?,"*(len(values)+1)
        
        allValues = []
        recursive(valuesRange,0,values,allValues)

        for value in allValues:
            simId = self.checkExists(value)
            if simId !=-1:
                value = np.insert(value,0,[simId])   
                c.execute("INSERT INTO parameters VALUES ("+nValues[:-1]+")",value)
        conn.commit()
        conn.close()

    def checkReplicates(self, replicates = 1):
        conn = sqlite3.connect(self.dbSimulations, check_same_thread=False)
        conn.row_factory = dict_factory
        res = conn.execute("Select * from parameters")

        simIds = res.fetchall()
        conn.close()

        conn = sqlite3.connect(self.dbReplicates, check_same_thread=False)
        c = conn.cursor()
        repIds = []
        for simId in simIds:
            c.execute("Select * from simulations where simId = ?",(simId["simId"],))
            n = len(c.fetchall())
            for k in range(0,replicates-n):
                simId["repId"] = getUUID()
                repIds.append(simId)
        conn.close()


        print('simulations type : '+str(len(simIds)))
        print('simulations left : '+str(len(repIds)))

        return repIds

    def addReplicate(self,repId):
        values = [repId["simId"],repId["repId"],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        while self.lockDB:
            time.sleep(random.random())
        self.lockDB = True
        conn = sqlite3.connect(self.dbReplicates, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO simulations VALUES (?,?,?)",values)
        conn.commit()
        conn.close()
        self.lockDB = False

    def __init__(self,dbSimulations = 'db/simulations.db',jsonFile = "db/db.json",dbReplicates = "db/replicates.db",dbAnalyzed = "db/analyzed.db"):
        self.lockDB = False
        self.dbSimulations = dbSimulations
        self.dbReplicates = dbReplicates
        self.dbAnalyzed = dbAnalyzed
        try:
            f = open(jsonFile)
            self.dbConfig = json.load(f)
            f.close()
            if not os.path.isfile(dbSimulations):
                self.generator()
            self.getTypes()
        except:
            print(" - - -   there is not database configuration file  - - - ")
            print(" - - - databases can be accessed but not generated - - - ")
            #print('---- i am nice so i just made you one ----')
            #jsonFaker = '{\n\t"project":"test",\n\t"experiment":"ex",\n\t"replicates":1,\n\t"nThreads":30,\n\t"writerIP":"XXX.XXX.XXX.XXX",\n\t"writerPort":YYYY\n}'
        
        if not os.path.isfile(dbReplicates):
            self.generatorReplicates()




class Analyzer:

    def getTypes(self):
        conn = sqlite3.connect(self.dbSimulations)
        c = conn.cursor()
        c.execute("""PRAGMA table_info(parameters) """)
        columns = c.fetchall()
        tmp,keys,types,tmp,tmp,tmp =  zip(*columns)
        self.types = dict(zip(keys, types))
        conn.close()

    def getProjects(self):
        conn = sqlite3.connect(self.dbSimulations, check_same_thread=False)
        c = conn.cursor()
        c.execute("Select project from parameters")
        projects = np.unique(c.fetchall())
        conn.close()    
        return projects

    def getExperiments(self,project = "project"):
        conn = sqlite3.connect(self.dbSimulations, check_same_thread=False)
        c = conn.cursor()
        c.execute("Select experiment from parameters where project = ?",(project,))
        experiments = np.unique(c.fetchall())
        conn.close()    
        return experiments

    def getParameters(self,simId):
        conn = sqlite3.connect(self.dbSimulations, check_same_thread=False)
        conn.row_factory = dict_factory
        res = conn.execute("Select * from parameters where simId = ?",(simId,))
        parameters = res.fetchall()
        conn.close()
        return parameters[0]


    def getExperimentSortingKeys(self,project = "project",experiment = "experiment"):
        conn = sqlite3.connect(self.dbSimulations, check_same_thread=False)
        conn.row_factory = dict_factory
        res = conn.execute("Select * from parameters where project = ? and experiment = ?",(project,experiment))
        experiments = res.fetchall()
        conn.close() 
        sortingKeys = {"project":[project],"experiment":[experiment]}
        for key in experiments[0].keys():
            if key != "simId":
                x = []
                for exp in experiments:
                    x.append(exp[key])
                x = np.array(x)

                if len(set(x))>1:
                    sortingKeys[key] = np.sort(np.unique(x))
                    if self.types[key] == 'INTEGER':
                        sortingKeys[key] = sortingKeys[key].astype(int)
        sortedKeys = dictListsToListDict(sortingKeys)
        del sortingKeys["project"]
        del sortingKeys["experiment"]
        return sortingKeys,sortedKeys

    def getSimIds(self,parameters):
        line = "select simId from parameters where"
        values = ()
        for key in parameters.keys():
            line+=" "+key+" = ? and"
            if self.types[key] == 'INTEGER':
                values = values+(int(parameters[key]),)
            else:
                values = values+(parameters[key],)
        conn = sqlite3.connect(self.dbSimulations, check_same_thread=False)
        c = conn.cursor()
        c.execute(line[:-4],values)
        print(parameters)
        simId = c.fetchall()
        conn.close()
        return simId





    def getRepIds(self,simId):
        conn = sqlite3.connect(self.dbReplicates, check_same_thread=False)
        c = conn.cursor()
        c.execute("Select repId from simulations where simId = ?",(simId,))
        repIds = c.fetchall()
        conn.close()
        return repIds

    def getDate(self,repId):
        conn = sqlite3.connect(self.dbReplicates, check_same_thread=False)
        c = conn.cursor()
        c.execute("Select date from simulations where repId = ?",(repId,))
        dates = c.fetchall()
        conn.close()
        return dates[0][0]

    def getAllRepIds(self):
        conn = sqlite3.connect(self.dbReplicates, check_same_thread=False)
        c = conn.cursor()
        c.execute("Select repId from simulations")
        repIds = c.fetchall()
        conn.close()
        return repIds


    def getDataPath(self,repId):
        conn = sqlite3.connect(self.dbReplicates, check_same_thread=False)
        c = conn.cursor()
        c.execute("Select simId from simulations where repId = ?",(repId,))
        simId = c.fetchall()[0][0]
        conn.close()
        
        conn = sqlite3.connect(self.dbSimulations, check_same_thread=False)
        c = conn.cursor()
        c.execute("Select project from parameters where simId = ?",(simId,))
        project = c.fetchall()[0][0]
        conn.close()
        pathProject = writer.pather(self.path,[project])
        return writer.pather(pathProject,writer.getUUIDPath(repId))


    def getDataSet(self,repId):
        pathData = self.getDataPath(repId) + "/position.csv"
        #rawData = np.genfromtxt(pathData, delimiter=",")
        rawData = pd.read_csv(pathData, header=None, delimiter=",").values
        data = separateData(rawData)
        return data

    def __init__(self,dbSimulations = 'db/simulations.db',dbReplicates = "db/replicates.db",dbAnalyzed = "db/analyzed.db",path = "/data"):
        self.lockDB = False
        self.dbSimulations = dbSimulations
        self.dbReplicates = dbReplicates
        self.dbAnalyzed = dbAnalyzed
        self.path = path
        self.getTypes()
        self.projects = self.getProjects()


class serverFiller:
    def getTypes(self):
        conn = sqlite3.connect(self.expDB)
        c = conn.cursor()
        c.execute("""PRAGMA table_info(malkoDB_experiments) """)
        columns = c.fetchall()
        tmp,keys,types,tmp,tmp,tmp =  zip(*columns)
        self.types = dict(zip(keys, types))
        c.execute("Select * from malkoDB_experiments ")
        self.id0 = len(c.fetchall())
        conn.close()

        
        
    
    def defineModels(self):
        self.anal.getTypes()
        text = 'from django.db import models\nfrom django.utils import timezone\n\nclass experiments(models.Model):\n\t'
        text += 'repId = models.CharField(max_length=200)\n\t'
        text += 'date = models.CharField(max_length=200)\n\t'

        for typ in self.anal.types:
            text += typ+' = models.'
            if self.anal.types[typ] == "TEXT":
                text += 'CharField(max_length=200)'
            elif self.anal.types[typ] == "INTEGER":
                text += 'IntegerField()'
            elif self.anal.types[typ] == "REAL":
                text += 'FloatField()'
            text += '\n\t'

        with open(self.models, 'w') as f:
            f.write(text)

    def writeLines(self,parameters):
        conn = sqlite3.connect(self.expDB)
        c = conn.cursor()
        c.execute("Select * from malkoDB_experiments where repId = ?",(parameters["repId"],))
        ids = c.fetchall()
        values = ()
        if len(ids) == 0:
            for typ in self.types:
                values += (parameters[typ],)
            nValues = "?,"*(len(values))
            c.execute("INSERT INTO malkoDB_experiments VALUES ("+nValues[:-1]+")",values)
        conn.commit()
            
        conn.close()
        self.id0 += 1



    def fillDB(self):        
        self.projects = self.anal.getProjects()
        for project in self.projects:
            experiments = self.anal.getExperiments(project)
            for exp in experiments:
                simIds = self.anal.getSimIds({"project":project,"experiment":exp}) # here i need something different
                for simId in simIds:
                    repIds = self.anal.getRepIds(simId[0])
                    for repId in repIds:
                        parameters = self.anal.getParameters(simId[0])
                        parameters["project"] = project
                        parameters["experiment"] = exp
                        parameters["repId"] = repId[0]
                        parameters["date"] = self.anal.getDate(repId[0])
                        parameters["id"] = self.id0
                        self.writeLines(parameters)
        print("done")

    def __init__(self,models = './server/malkoDB/models.py',expDB = './server/exp.db',
                      dbSimulations = 'db/simulations.db',dbReplicates = "db/replicates.db",dbAnalyzed = "db/analyzed.db",path = "/data"):
        self.anal = Analyzer(dbSimulations,dbReplicates,dbAnalyzed)
        self.models = models
        self.expDB = expDB
        if not os.path.isfile(self.models):
            self.defineModels()
        if not os.path.isfile(self.expDB):
            print('please run\n\t python server/manage.py makemigrations\n then\n\t python server/manage.py migrate')
        else:
            self.getTypes()
