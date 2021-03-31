import optiCode.ngbhStruc as nbh
from helpFunctions import createMLdata
import score
import collections
import random
import time
import math
import multiprocessing
import textdistance
from joblib import dump, load

class SAZone:
    def __init__(self, startSequence, travelTimeMatrix, stopsData, zoneList, origSequenceWithNames, startTime, startDate):
        self.sequence = startSequence
        self.zoneList = zoneList
        self.tt = travelTimeMatrix
        self.stopsData = stopsData
        self.origSequenceWithNames = origSequenceWithNames
        self.startTime, self.startDate = startTime, startDate
        # Create list with neighborhodds that we then choose from
        self.neighborhoods = [nbh.zoneInsertion, nbh.zoneSwap, nbh.randomSwapInZone, nbh.zoneNodeInsertion, nbh.inZoneTwoOptChange]
    
    def checkValidity(self, sequence):
        valid = True
        return valid    
    
    def getObjectiveValue(self, sequenceWithNames):
        totalCosts = 0
        for idx, val in enumerate(sequenceWithNames):
            if idx == 0:
                continue
            else:
                lastStop = sequenceWithNames[idx-1]
                totalCosts += self.tt[lastStop][val]
        return totalCosts + self.tt[sequenceWithNames[idx]][sequenceWithNames[0]]

    def iterate(self, maxTime):
        seq = self.sequence
        zoneList = self.zoneList
        temp = 1 # Set starting temperature
        bestObjValue = self.getObjectiveValue(seq)
        tabuList = collections.deque([0])
        bestSeq = seq.copy()
        tempCounter = 0
        notImprovedCounter = 0
        t0 = time.time()
        # Start iterations
        while time.time() - t0 < maxTime:
            temp = math.exp(-0.005*tempCounter)
            oldObjVal = self.getObjectiveValue(seq)
            temporarySeq, temporaryZoneList = random.choices(self.neighborhoods, weights=[0, 0.0,0.4, 0.4, 0.4])[0](seq.copy(), zoneList.copy())
            newObjVal = self.getObjectiveValue(temporarySeq)
            if newObjVal not in tabuList:
                if newObjVal <= oldObjVal: # Always accept better solutions
                    tabuList.appendleft(newObjVal)
                    tabuList.pop()
                    seq = temporarySeq.copy()
                    zoneList = temporaryZoneList.copy()
                    notImprovedCounter = 0
                    # Now we store the best solution
                    if newObjVal < bestObjValue:
                        bestObjValue = newObjVal
                        bestSeq = temporarySeq.copy()
                        #print('new Best value', bestObjValue)
                else: # Sometimes accept worse solutions
                    notImprovedCounter +=1
                    if random.random() < temp:
                        tabuList.appendleft(newObjVal)
                        tabuList.pop()
                        seq = temporarySeq.copy()
                        zoneList = temporaryZoneList.copy()

            tempCounter += 1
            if notImprovedCounter >= 6000:
                break
        return bestSeq, bestObjValue
    
    def multiprocessSA(self, noIterations):
        # multiprocessing stuff here
        args = [noIterations] * (multiprocessing.cpu_count())
        p = multiprocessing.Pool(multiprocessing.cpu_count())
        result = p.map(self.iterate, args)
        for r in result:
            print(score.score(self.origSequenceWithNames + [r[0][0]],r[0] + [r[0][0]],self.tt), r[1])
        res = min(result, key=lambda x: x[1])[0]
        return res



class SA:
    def __init__(self, startSequence, travelTimeMatrix, stopsData):
        self.sequence = startSequence
        self.tt = travelTimeMatrix
        self.stopsData = stopsData
        # Create list with neighborhodds that we then choose from
        self.neighborhoods = [nbh.randomSwap, nbh.twoOptChange, nbh.nodeInsertion]
    
    def checkValidity(self, sequence):
        valid = True
        return valid    
    
    def getObjectiveValue(self, sequenceWithNames):
        totalCosts = 0
        for idx, val in enumerate(sequenceWithNames):
            if idx == 0:
                continue
            else:
                lastStop = sequenceWithNames[idx-1]
                totalCosts += self.tt[lastStop][val]
        return totalCosts

    def iterate(self, noIterations):
        seq = self.sequence
        temp = 1 # Set starting temperature
        notValidCounter = 0 # Counter used to check how often an unvalid route has been found 
        bestObjValue = self.getObjectiveValue(seq)
        bestSeq = seq.copy()
        tempCounter = 0
        notImprovedCounter = 0
        # Start iterations
        for _i in range(noIterations):
            temp = math.exp(-0.0003*tempCounter)
            oldObjVal = self.getObjectiveValue(seq)
            temporarySeq = random.choice(self.neighborhoods)(seq.copy())
            newObjVal = self.getObjectiveValue(temporarySeq)
            if newObjVal <= oldObjVal: # Always accept better solutions
                seq = temporarySeq.copy()
                notImprovedCounter = 0
                # Now we store the best solution
                if newObjVal < bestObjValue:
                    bestObjValue = newObjVal
                    bestSeq = temporarySeq.copy()
                    #print('new Best value', bestObjValue)
            else: # Sometimes accept worse solutions
                notImprovedCounter +=1
                if random.random() < temp:
                    seq = temporarySeq.copy()
            tempCounter += 1
            if notImprovedCounter >= 8000:
                break
        return bestSeq, bestObjValue
    
    def multiprocessSA(self, noIterations):
        # multiprocessing stuff here
        args = [noIterations] * (multiprocessing.cpu_count()-1)
        p = multiprocessing.Pool(multiprocessing.cpu_count()-1)
        result = p.map(self.iterate, args)
        res = min(result, key=lambda x: x[1])[0]
        return res

