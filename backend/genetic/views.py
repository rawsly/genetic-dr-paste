from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json

import numpy as np
import math
import time
import random
import itertools
import queue
import pandas as pd
import seaborn as sns

def createRandomPop(Npop, numberOfJobs):
    pop = []
    for i in range(Npop):
        p = list(np.random.permutation(numberOfJobs))
        while p in pop:
            p = list(np.random.permutation(numberOfJobs))
        pop.append(p)
    
    return pop

def initialization(Npop, numberOfJobs):
    return createRandomPop(Npop, numberOfJobs)

def findFirstNotBusyMachine(machines):
    for index, machine in enumerate(machines):
        if machine == False:
            return index
    
    return -1

def calculateObj(sol, numberOfStages, cost, numberOfMachinesInStage):
    numberOfJobs = len(cost)
    qTime = queue.PriorityQueue() # (time, stage, machine, job)
    machineTracker = list()
    
    qStages = list(list())
    for i in range(numberOfStages):
        for j in numberOfMachinesInStage:
            qMachines = []
            for k in range(j):
                qMachines.append(queue.Queue())
            
            qStages.append(qMachines)
    
    # qStages = [[queue1], [queue2, queue3, queue4], [queue5, queue6, queue7]]
    # putting jobs inside first machine queue
    for i in range(numberOfJobs):
        qStages[0][0].put(sol[i])
        
    # creating busyMachines list to track busy machines.
    # this is actually [stage][machine]
    # [[False], [False, False, False], [False, False, False]]
    # at first no machine is busy.
    busyMachines = []
    for i in range(numberOfStages):
        busyMachines.append([])
        for j in range(len(qStages[i])):
            busyMachines[i].append(False)
    
    # initial state.
    # time = 0, job is the first element in qStages[0][0] which is queue1
    # TODO: job ve machine sayısına göre loop'ta dönmeliyiz
    loopRange = numberOfMachinesInStage[0] if numberOfMachinesInStage[0] < numberOfJobs else numberOfJobs
    for i in range(loopRange):
        time = 0
        job = qStages[0][0].get()
        initQTime = [int(0), int(time + cost[job][0]), int(0), int(i), int(job)]
        qTime.put(initQTime)
        machineTracker.append(initQTime)
        busyMachines[0][i] = True
            
    while True:
        startTime, time, stage, machine, job = qTime.get()
        # loop through all jobs and stages - ending condition
        if job == sol[numberOfJobs-1] and stage == numberOfStages-1:
            break
        
        busyMachines[stage][machine] = False
        # if there is a job waiting to be proccessed
        if not qStages[stage][machine].empty():
            j = qStages[stage][machine].get()
            procTime = int(time + cost[j][stage])
            
            qTimeObj = [int(time), procTime, int(stage), int(machine), int(j)]
            qTime.put(qTimeObj)
            machineTracker.append(qTimeObj)
            
            busyMachines[stage][machine] = True


        if stage < numberOfStages - 1:
            nextStage = stage + 1
            notBusyMachine = findFirstNotBusyMachine(busyMachines[nextStage])
            if notBusyMachine != -1:
                procTime = int(time + cost[job][nextStage]) # stage or stage + 1 ?
                
                qTimeObj = [int(time), procTime, int(nextStage), int(notBusyMachine), int(job)]
                qTime.put(qTimeObj)
                machineTracker.append(qTimeObj)
                
                busyMachines[nextStage][notBusyMachine] = True
            else:
                qStages[nextStage][notBusyMachine].put(job)
     
    return time, stage, machine, job, machineTracker

def selection(pop, numberOfStages, cost, numberOfMachinesInStage):
    popObj = []
    for i in range(len(pop)):
        popObj.append([calculateObj(pop[i], numberOfStages, cost, numberOfMachinesInStage)[0], i])
    
    popObj.sort()
    
    probabilityDistribution = []
    probabilityDistributionIndex = []
    
    for i in range(len(pop)):
        probabilityDistributionIndex.append(popObj[i][1])
        prob = (2*(i+1)) / (len(pop) * (len(pop)+1))
        probabilityDistribution.append(prob)
    
    parents = []
    for i in range(len(pop)):
        parents.append(list(np.random.choice(probabilityDistributionIndex, 2, p=probabilityDistribution)))
    
    return parents

def crossover(parents, numberOfJobs):
    # crossover points
    cp = list(np.random.permutation(np.arange(numberOfJobs-1)+1)[:2])
    
    # ordering crossover points in asc
    if cp[0] > cp[1]:
        t = cp[0]
        cp[0] = cp[1]
        cp[1] = t
    
    child = list(parents[0])
    
    # loop between crossover points
    for i in range(cp[0], cp[1]):
        child[i] = -1
    
    p = -1
    for i in range(cp[0], cp[1]):
        while True:
            p = p + 1
            if parents[1][p] not in child:
                child[i] = parents[1][p]
                break
    
    return child

def mutation(sol, numberOfJobs):
    # mutation points
    mp = list(np.random.permutation(np.arange(numberOfJobs))[:2])
    # 3, 6
    
    # sorting
    if mp[0] > mp[1]:
        t = mp[0]
        mp[0] = mp[1]
        mp[1] = t
    
    remJob = sol[mp[1]]
    
    for i in range(mp[1], mp[0], -1):
        # probability distribution = 1
        sol[i] = sol[i-1]
        
    sol[mp[0]] = remJob
    
    return sol

def elitistUpdate(oldPop, newPop, numberOfStages, cost, numberOfMachinesInStage):
    bestSolInd = 0
    bestSol = calculateObj(oldPop[0], numberOfStages, cost, numberOfMachinesInStage)[0]
    
    for i in range(1, len(oldPop)):
        tempObj = calculateObj(oldPop[i], numberOfStages, cost, numberOfMachinesInStage)[0]
        if tempObj < bestSol:
            bestSol = tempObj
            bestSolInd = i
            
    rndInd = random.randint(0,len(newPop)-1)    
    newPop[rndInd] = oldPop[bestSolInd]

    
    return newPop

# Returns best solution's index number, best solution's objective value and average objective value of the given population.
def findBestSolution(pop, numberOfStages, cost, numberOfMachinesInStage):
    bestObj, stage, machine, job, machineTracker = calculateObj(pop[0], numberOfStages, cost, numberOfMachinesInStage)
    avgObj = bestObj
    bestInd = 0
    bestMachineTacker = machineTracker
    
    for i in range(1, len(pop)):
        tempObj, tempStage, tempMachine, tempJob, tempMachineTracker = calculateObj(pop[i], numberOfStages, cost, numberOfMachinesInStage)
        avgObj = avgObj + tempObj
        if tempObj < bestObj:
            bestMachineTacker = tempMachineTracker
            bestObj = tempObj
            bestInd = i
            
    return bestInd, bestObj, avgObj/len(pop), bestMachineTacker

def genetic(Npop, Pc, Pm, stopGen, numberOfStages, cost, numberOfMachinesInStage):
    t1 = time.time()
    population = initialization(Npop, len(cost))
    for i in range(stopGen):
        parents = selection(population, numberOfStages, cost, numberOfMachinesInStage)
        childs = []

        for p in parents:
            r = random.random()
            if r < Pc:
                childs.append(crossover([population[p[0]], population[p[1]]], len(cost)))
            else:
                if r < 0.5:
                    childs.append(population[p[0]])
                else:
                    childs.append(population[p[1]])
        for c in childs:
            r = random.random()
            if r < Pm:
                c = mutation(c, len(cost))

        population = elitistUpdate(population, childs, numberOfStages, cost, numberOfMachinesInStage)
    
    bestSol, bestObj, avgObj, bestMachineTacker = findBestSolution(population, numberOfStages, cost, numberOfMachinesInStage)
    t2 = time.time()
    runningTime = t2 - t1
    
    return population[bestSol], bestObj, avgObj, runningTime, bestMachineTacker

def startParameterTuning(Npop, Pc, Pm, stopGen, numberOfStages, cost, numberOfMachinesInStage):
    isFirst = True
    bestResult = {}
    results = []
    for n in Npop:
        for pc in Pc:
            for pm in Pm:
                for gen in stopGen: 
                    params = {
                        "Npop": n,
                        "Pc": pc,
                        "Pm": pm,
                        "stopGen": gen
                    }
                    result = genetic(n, pc, pm, gen, numberOfStages, cost, numberOfMachinesInStage)
                    results.append({"result": result, "params": params})
                    print(result, params)
                    if isFirst:
                        bestResult = {
                            "result": result,
                            "params": params
                        }
                    else:
                        oldBestObj = bestResult['result'][1]
                        newBestObj = result[1]
                        if newBestObj <= oldBestObj:
                            bestResult = {
                                "result": result,
                                "params": params
                            }
                            
                    isFirst = False
                    
    return bestResult, results

# Create your views here.
def index(request):
   
    requestData = json.loads(request.body.decode('utf-8'))
    Npop = requestData['population']
    Pc = requestData['crossover']
    Pm = requestData['mutation']
    gen = requestData['generation']
    numberOfStages = requestData['stages']
    cost = requestData['data']
    numberOfMachinesInStage = requestData['numberOfMachinesInStage']
    result = genetic(Npop, Pc, Pm, gen, numberOfStages, cost, numberOfMachinesInStage)
    solution = [int(i) for i in result[0]]
    data = {
        "bestSol": solution,
        "cMax": result[1],
        "average": result[2],
        "runningTime": result[3],
        "machineTracker": result[4]
    }
    print(data)
    return JsonResponse(data)