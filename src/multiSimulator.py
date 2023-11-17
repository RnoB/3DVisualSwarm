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

import visualSwarm as vs
from dbFiller import dbFiller
import sys
import multiprocessing 
import os
import json
import datetime
import sqlite3
import traceback
import numpy as np

lockDB = False
config = {}

def addReplicate(repId):
    global lockDB
    values = [repId["simId"],repId["repId"],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    while lockDB:
        time.sleep(random.random())
    lockDB = True
    conn = sqlite3.connect(config["dbReplicates"], check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO simulations VALUES (?,?,?)",values)
    conn.commit()
    conn.close()
    lockDB = False

def startSimulation(repId):
    global lockDB

    try:

        parametersV = np.array([[repId["a0"],repId["a00"],repId["a1"]],
                                [repId["b0"],repId["b00"],repId["b1"]],
                                [repId["c0"],repId["c00"],repId["c1"]]])
        N = repId["N"]
        sim = vs.Simulator(engine = repId["engine"],size = repId["nPhi"], N = repId["N"], dim = repId["dim"],
                      dt = repId["dt"],tMax = repId["tMax"],u0 = repId["u0"],drag = repId["drag"],
                      parametersV = parametersV,
                      bufferSize = 1000,ip = config["writerIP"] , port = config["writerPort"],project = repId["project"])
        if repId["mode"] == 0:
            sim.setScale(repId["sx"],repId["sy"],repId["sz"])
        elif repId["mode"] == 1:
            sim.setScale(repId["sx"],repId["sx"],repId["sx"],0)
        repId['repId'] = sim.getName()
        print("** * starting simulations : " + str(repId["simId"]) + " replicates : " +str(repId['repId']))
        sim.start()
        sim.stop()
        addReplicate(repId)
        print("** * **  done simulations : " + str(repId["simId"]) + " replicates : " +str(repId['repId']))
    except Exception as e:

        traceback.print_exc()
        print()

def main():
    global config
    try:
        jsonFile = sys.argv[1]
    except:
        jsonFile = "ms.json"
    if not os.path.isfile(jsonFile):
        print('----  you need a file called ms.json  ----')
        print('---- or to give the path to this file ----')
        print('---- i am nice so i just made you one ----')
        jsonFaker = '{\n\t"dbSimulations":"./db/simulations.db",\n\t"dbReplicates":"./db/replicates.db",\n\t"replicates":1,\n\t"nThreads":30,\n\t"writerIP":"XXX.XXX.XXX.XXX",\n\t"writerPort":YYYY\n}'
        with open('ms.json', 'w') as f:
            f.write(jsonFaker)
        print(jsonFaker)
    else:
        f = open(jsonFile)
        config = json.load(f)
        f.close()
        db = dbFiller.Filler(dbSimulations = config["dbSimulations"],dbReplicates = config["dbReplicates"])
        repIds = db.checkReplicates(config["replicates"])

        pool = multiprocessing.Pool(processes=config["nThreads"])
        pool.map_async(startSimulation, repIds)
        pool.close()
        pool.join()

if __name__ == "__main__":
    main()
