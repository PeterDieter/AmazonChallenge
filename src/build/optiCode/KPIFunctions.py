import datetime
from math import nan
import geopy.distance

def getObjectiveValue(ttMatrix, sequenceWithNames):
    totalCosts = 0
    for idx, val in enumerate(sequenceWithNames):
        if idx == 0:
            continue
        else:
            lastStop = sequenceWithNames[idx-1]
            totalCosts += ttMatrix[lastStop][val]
    return totalCosts + ttMatrix[sequenceWithNames[idx]][sequenceWithNames[0]]

def getArrivalTimes(ttMatrix, startTime, startDate, sequenceWithNames, stopsData):
    startTime = startDate + ' ' + startTime
    startTime = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
    for idx, val in enumerate(sequenceWithNames):
        if idx == 0:
            stopsData[val]["arrivalTime"]  = (startTime-datetime.datetime(1970,1,1)).total_seconds()
            stopsData[val]["slackBeginningTW"] = nan
            stopsData[val]["slackEndTW"] = nan
        else:
            lastStop = sequenceWithNames[idx-1]
            stopsData[val]["arrivalTime"] = int(stopsData[lastStop]["arrivalTime"] + ttMatrix[lastStop][val] + stopsData[lastStop]["ServiceTime"])
            slackBeginningTW = stopsData[val]["arrivalTime"] - stopsData[val]["TimeWindowStart"]
            slackEndTW = stopsData[val]["TimeWindowEnd"] - stopsData[val]["arrivalTime"]
            stopsData[val]["slackBeginningTW"] = slackBeginningTW
            stopsData[val]["slackEndTW"] = slackEndTW
        
    
    return stopsData


def neighborNextDeviation(ttMatrix, sequenceWithNames):
    # This function calculates how the nearest neighbor deviates (distance wise) with the actual next stop
    route = [sequenceWithNames[0]]
    dev = []
    for i in range(len(sequenceWithNames)-1):
        cleanedList = list([key,value] for key, value in ttMatrix[sequenceWithNames[i]].items() if  key != sequenceWithNames[i] and key not in route)
        nextDist = min(cleanedList, key=lambda x: x[1])[1]
        actualDistance = ttMatrix[sequenceWithNames[i]][sequenceWithNames[i+1]]
        dev.append((actualDistance - nextDist))
        route.append(sequenceWithNames[i+1])
    return dev

def nextNeighbor(ttMatrix, sequenceWithNames):
    # This function calculates which neighbor the next stop is: 0 = nearest neighbor, 1 = second nearest neighbor etc.
    route = [sequenceWithNames[0]]
    dev = []
    for i in range(len(sequenceWithNames)-1):
        cleanedList = list([key,value] for key, value in ttMatrix[sequenceWithNames[i]].items() if key != sequenceWithNames[i] and key not in route)
        cleanedList.sort(key=lambda x: x[1])
        index = [j for j in range(len(cleanedList)) if cleanedList[j][0] == sequenceWithNames[i+1]]
        dev.append(index[0])
        route.append(sequenceWithNames[i+1])
    return dev

def firstLastDistance(ttMatrix, sequenceWithNames):
    # This function calculates the distance between the first and the last stop of the route
    route = [sequenceWithNames[0]]
    firstStop = sequenceWithNames[1]
    lastStop = sequenceWithNames[len(sequenceWithNames)-1]
    cleanedList = list([key,value] for key, value in ttMatrix[firstStop].items() if key != firstStop and key not in route)
    cleanedList.sort(key=lambda x: x[1])
    index = [j for j in range(len(cleanedList)) if cleanedList[j][0] == lastStop]
    return index[0]/len(sequenceWithNames)



def zoneNearestNeighbor(ttMatrix, sequenceWithNames, stopsData, nn):
    # This function calculates how many of the unvisited neighbors are part of a different zone.
    route = [sequenceWithNames[0]]
    dev = []
    allZones = []
    for i in range(1,len(sequenceWithNames)-1):
        currentStop = sequenceWithNames[i]
        currentZone = stopsData[currentStop]["ZoneID"]
        allZones.append(currentZone)
        cleanedList = list([key,value] for key, value in ttMatrix[currentStop].items() if key != currentStop and key not in route)
        cleanedList.sort(key=lambda x: x[1])
        cleanedList = cleanedList[0:nn]
        numberInZone = 0
        for j in cleanedList:
            if stopsData[j[0]]["ZoneID"] == currentZone:
                numberInZone += 1
        dev.append(numberInZone)
        route.append(sequenceWithNames[i+1])
    y = (len(sequenceWithNames)-1) / len(set(allZones))
    dev = [x / y for x in dev]
    return dev

def zoneViolations(ttMatrix, sequenceWithNames, stopsData):
    # This function calculates how many of the unvisited neighbors are part of a different zone.
    allZones = []
    violations = 0
    for i in range(1,len(sequenceWithNames)):
        currentStop = sequenceWithNames[i]
        currentZone = stopsData[currentStop]["ZoneID"]
        if i > 2:
            for j in range(i-2, -1, -1):
                if allZones[j] != currentZone:
                    if currentZone in allZones[:j]:
                        violations += 1
                        break
                    else:
                        continue
                    continue
                else:
                    break
        allZones.append(currentZone)
    #y = (len(sequenceWithNames)-1) / len(set(allZones))
    return violations,  len(set(allZones))


def airDistance(stopsData):
    distMat = {}
    for _from in stopsData:
        distMat[_from] = {}
        for _to in stopsData:
            distMat[_from][_to] = geopy.distance.distance((stopsData[_from]["lat"],stopsData[_from]["lng"]), (stopsData[_to]["lat"],stopsData[_to]["lng"])).m
    return distMat
            
