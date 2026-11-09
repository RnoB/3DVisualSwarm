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

from visualswarm import visualSwarm as vs
from analyzer.dbFiller import dbFiller
from analyzer import analyzer
import threading
from writerserver import writer
import sys


import os
import json
import datetime
import sqlite3
import traceback
import numpy as np
import random
import time







    
def main():
    
    try:
        jsonFile = sys.argv[1]
    except:
        jsonFile = "./ms.json"
    if not os.path.isfile(jsonFile):
        print('----  you need a file called ms.json  ----')
        print('---- or to give the path to this file ----')
        print('---- i am nice so i just made you one ----')
        jsonFaker = '{\n\t"dbSimulations":"./analyzer/db/simulations.db",\n\t"dbReplicates":"./analyzer/db/replicates.db",\n\t"dbAnalyzed":"./analyzer/db/analyzed.db",\n\t"replicates":1,\n\t"nThreads":30,\n\t"writerIP":"XXX.XXX.XXX.XXX",\n\t"writerPort":"YYYY"\n\t"writerPath":""\n\t"step:10"\n,"project":"","experiment":""}'
        with open('ms.json', 'w') as f:
            f.write(jsonFaker)
        print(jsonFaker)
    else:
        f = open(jsonFile)
        config = json.load(f)
        f.close()
        
        try:
            if len(config["writerPath"])>0:
                writerServer = writer.Server(path = config["writerPath"],ip = config["writerIP"], port = config["writerPort"])
                writerServer.start() 
        except Exception as e:

            traceback.print_exc() 
                
        dbSimulations =config["dbSimulations"]
        dbReplicates = config["dbReplicates"]
        dbAnalyzed = config["dbReplicates"]
        step = config["step"]
        project = config["project"]
        experiment = [config["experiment"]]
        nThreads = [config["nThreads"]]

        analyzer.start(step = step,nThreads = nThreads,dbSimulations = dbSimulations,dbReplicates = dbReplicates,dbAnalyzed = dbAnalyzed,project = project,experiment = experiment)

if __name__ == "__main__":
    main()