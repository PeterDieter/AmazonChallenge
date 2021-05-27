import random
import time
import math
import multiprocessing
import build.optiCode.ngbhStruc as nbh

class SA:
    def __init__(self, startSequence, travelTimeMatrix, zoneList):
        self.sequence = startSequence
        self.zoneList = zoneList
        self.tt = travelTimeMatrix
        # Create list with neighborhodds that we then choose from
        self.neighborhoods = [nbh.randomSwapInZone, nbh.zoneNodeInsertion, nbh.inZoneTwoOptChange] 
    
    def getObjectiveValue(self, sequenceWithNames):
        totalCosts = 0
        for idx, val in enumerate(sequenceWithNames):
            if idx == 0:
                continue
            else:
                lastStop = sequenceWithNames[idx-1]
                totalCosts += self.tt[lastStop][val]
        return totalCosts 

    def iterate(self, inp):
        maxTime, temperature = inp[0], inp[1]
        seq = self.sequence
        zoneList = self.zoneList
        temp = 1 # Set starting temperature
        bestObjValue = self.getObjectiveValue(seq)
        bestSeq = seq.copy()
        tempCounter = 0
        t0 = time.time()
        # Start iterations
        while time.time() - t0 < maxTime:
            temp = math.exp(temperature*tempCounter)
            oldObjVal = self.getObjectiveValue(seq)
            temporarySeq, temporaryZoneList = random.choices(self.neighborhoods, weights=[0.2, 0.8, 2.4])[0](seq.copy(), zoneList.copy())
            newObjVal = self.getObjectiveValue(temporarySeq)
            if newObjVal <= oldObjVal: # Always accept better solutions
                seq = temporarySeq.copy()
                zoneList = temporaryZoneList.copy()
                # Now we store the best solution
                if newObjVal < bestObjValue:
                    bestObjValue = newObjVal
                    bestSeq = temporarySeq.copy()
            else: # Sometimes accept worse solutions
                if random.random() < temp:
                    seq = temporarySeq.copy()
                    zoneList = temporaryZoneList.copy()
            tempCounter += 1
        return bestSeq, bestObjValue
    
    def multiprocessSA(self, noIterations):
        # multiprocessing stuff here
        args = [noIterations] * (5)
        p = multiprocessing.Pool(5)
        result = p.map(self.iterate, args)
        res = min(result, key=lambda x: x[1])[0]
        return res

