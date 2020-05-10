
import numpy as np
import math
import time
import random
import itertools
import queue
import pandas as pd
import seaborn as sns

colors = {
    'WHITE': 30,
    'SKIN': 35,
    'BABY_PINK': 35,
    'BABY_BLUE': 35,
    'BLUE': 35,
    'GREEN': 35,
    'SILVER': 35,
    'YELLOW': 35,
    'ORANGE': 40,
    'PINK': 40,
    'RED': 40,
    'DARK_BLUE': 40,
    'GREY': 40,
    'GOLD': 40,
    'PURPLE': 40,
    'BROWN': 40,
    'BLACK': 50
}
sizes = { 'XS': 30, 'S': 20, 'M': 15, 'L': 5 }

def calculateProcTime(color=None, size=None):
    if size == None and color == None:
        print("Size and color is not set.")
        return 0
    if color != None and size == None:
        return colors[color]
    if size != None and color == None:
        return sizes[size]

    return colors[color] + sizes[size]

def createData(weight, color, size, capacity, machines):
    numberOfJobs = math.ceil(weight / capacity)
    jobs = list(list())
    for i in range(numberOfJobs):
        # procTimes = [calculateProcTime(color=color), calculateProcTime(size=size)]
        procTimes = [random.randint(5, 30), random.randint(5, 30)]
        jobs.append(procTimes)

    return jobs, len(jobs), len(procTimes), machines

cost, numberOfJobs, numberOfStages, numberOfMachinesInStage = createData(1000, 'RED', 'S', 65, [12, 4])

def createRandomPop(Npop):
    pop = []
    for i in range(Npop):
        p = list(np.random.permutation(numberOfJobs))
        while p in pop:
            p = list(np.random.permutation(numberOfJobs))
        pop.append(p)
    
    return pop

def initialization(Npop):
    return createRandomPop(Npop)

def findFirstNotBusyMachine(machines):
    for index, machine in enumerate(machines):
        if machine == False:
            return index
    
    return -1         

def calculateObj(sol):
    qTime = queue.PriorityQueue() # (time, stage, machine, job)
    machineTracker = list()
    
    # creating stages which has machine queues inside
    
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
    for i in range(numberOfMachinesInStage[0]):
        time = 0
        job = qStages[0][0].get()
        initQTime = (time + cost[job][0], 0, i, job)
        qTime.put(initQTime)
        machineTracker.append(initQTime)
        busyMachines[0][i] = True
            
    while True:
        time, stage, machine, job = qTime.get()
        # loop through all jobs and stages - ending condition
        if job == sol[numberOfJobs-1] and stage == numberOfStages-1:
            break
        
        busyMachines[stage][machine] = False
        # if there is a job waiting to be proccessed
        if not qStages[stage][machine].empty():
            j = qStages[stage][machine].get()
            procTime = time + cost[j][stage]
            
            qTimeObj = (procTime, stage, machine, j)
            qTime.put(qTimeObj)
            machineTracker.append(qTimeObj)
            
            busyMachines[stage][machine] = True


        if stage < numberOfStages - 1:
            nextStage = stage + 1
            notBusyMachine = findFirstNotBusyMachine(busyMachines[nextStage])
            if notBusyMachine != -1:
                procTime = time + cost[job][nextStage] # stage or stage + 1 ?
                
                qTimeObj = (procTime, nextStage, notBusyMachine, job)
                qTime.put(qTimeObj)
                machineTracker.append(qTimeObj)
                
                busyMachines[nextStage][notBusyMachine] = True
            else:
                qStages[nextStage][notBusyMachine].put(job)
     
    return time, stage, machine, job

def selection(pop):
    popObj = []
    for i in range(len(pop)):
        popObj.append([calculateObj(pop[i])[0], i])
    
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

def crossover(parents):
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

def mutation(sol):
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

def elitistUpdate(oldPop, newPop):
    bestSolInd = 0
    bestSol = calculateObj(oldPop[0])[0]
    
    for i in range(1, len(oldPop)):
        tempObj = calculateObj(oldPop[i])[0]
        if tempObj < bestSol:
            bestSol = tempObj
            bestSolInd = i
            
    rndInd = random.randint(0,len(newPop)-1)    
    newPop[rndInd] = oldPop[bestSolInd]

    
    return newPop

# Returns best solution's index number, best solution's objective value and average objective value of the given population.
def findBestSolution(pop):
    bestObj, stage, machine, job = calculateObj(pop[0])
    avgObj = bestObj
    bestInd = 0
    
    for i in range(1, len(pop)):
        tempObj = calculateObj(pop[i])[0]
        avgObj = avgObj + tempObj
        if tempObj < bestObj:
            bestObj = tempObj
            bestInd = i
            
    return bestInd, bestObj, avgObj/len(pop)

# Number of population
Npop = [10, 20, 30, 40, 50]
# Probability of crossover
Pc = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
# Probability of mutation
Pm = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
# Stopping number for generation
stopGeneration = [100, 1000]

# 5 * 6 * 10 * 2 = 600
# we are going to have 600 results and we will find the best one.

def genetic(Npop, Pc, Pm, stopGen):
    t1 = time.clock()
    population = initialization(Npop)
    for i in range(stopGen):
        parents = selection(population)
        childs = []

        for p in parents:
            r = random.random()
            if r < Pc:
                childs.append(crossover([population[p[0]], population[p[1]]]))
            else:
                if r < 0.5:
                    childs.append(population[p[0]])
                else:
                    childs.append(population[p[1]])
        for c in childs:
            r = random.random()
            if r < Pm:
                c = mutation(c)

        population = elitistUpdate(population, childs)
    
    bestSol, bestObj, avgObj = findBestSolution(population)
    t2 = time.clock()
    runningTime = t2 - t1
    
    return bestSol, bestObj, avgObj, runningTime

def startParameterTuning(Npop, Pc, Pm, stopGen):
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
                    result = genetic(n, pc, pm, gen)
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