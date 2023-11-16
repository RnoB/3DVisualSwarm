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

def getUUID():
    return uuid.uuid4().hex

def recursive(r,n,values,allValues):

    for k in r[n]["range"]:
        values[r[n]["k"]] = k
        if n<len(r)-1:
            recursive(r,n+1,values,allValues)
        else:
            allValues.append(np.copy(values))


class Filler:

    def generator(self):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        parameters = """("""
        for key in self.dbConfig.keys():
            parameters+= key+" "+self.dbConfig[key]["type"]+","
        parameters= parameters[:-1]+""")"""      
        c.execute("""CREATE TABLE parameters """+parameters)
        parameters = """(simId text,repId text,date text)"""
        c.execute("""CREATE TABLE simulations """+parameters)
        conn.commit()
        conn.close()

    def printValues(self):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        c.execute("""PRAGMA table_info(parameters) """)
        columns = c.fetchall()
        print(columns)
        conn.close()

    def fillParameters(self):
        conn = sqlite3.connect(self.dbName)
        c = conn.cursor()
        values = []
        valuesRange = []
        for key in self.dbConfig.keys():
            values.append(self.dbConfig[key]["default"])
            if "range" in self.dbConfig[key]:
                valuesRange.append({"k":len(values)-1,"range":self.dbConfig[key]["range"]})
        nValues = "?,"*len(values)
        
        allValues = []
        recursive(valuesRange,0,values,allValues)

        for value in allValues: 
            value[0] = getUUID()  
            c.execute("INSERT INTO parameters VALUES ("+nValues[:-1]+")",value)
        conn.commit()
        conn.close()

    def __init__(self,dbName = 'VisualSimulation.db',jsonFile = "db.json"):
        self.dbName = dbName
        f = open(jsonFile)
        self.dbConfig = json.load(f)
        f.close()

