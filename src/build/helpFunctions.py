import numpy as np
import os 
import json
import mpu


def findZoneClosestStop(stop, ttMatrix, route):
    cleanedList = list([key,value] for key, value in ttMatrix[stop].items() if key != stop and isinstance(route["stops"][key]["zone_id"], str))
    cleanedList.sort(key=lambda x: x[1])
    closestStop = cleanedList[0][0]
    return closestStop

def centralityMeasure(zoneTT, zoneListName, neglectZones):
    centrality, distToDepot, zoneList, TWList = [], [], [], []
    for fromZone in zoneListName:
        if fromZone not in neglectZones:
            value = 0
            for toZone in zoneListName:
                if toZone not in neglectZones:
                #if toZone != 'depot':
                    #value += zoneTT[fromZone][toZone]
                    value += zoneTT[toZone][fromZone]
            zoneList.append(fromZone)
            distToDepot.append(zoneTT['depot'][fromZone])
            centrality.append(value)
    
    newList = -np.array(centrality) + np.array(distToDepot) 

    centrality = {}
    for idx, zone in enumerate(zoneList):
        centrality[zone] = newList[idx]
    return centrality

def zoneDistanceMatrix(ttMatrix, stopsData, zoneListName):
    distMat = {}
    for _fromZone in zoneListName:
        distMat[_fromZone] = {}
        for _toZone in zoneListName:
            if _fromZone == _toZone:
                distMat[_fromZone][_toZone] = 0
            else:
                totalDist = 0
                stopsFromZone = [v["StopName"] for v in stopsData.values() if _fromZone in v.values()]
                stopsToZone = [v["StopName"] for v in stopsData.values() if _toZone in v.values()]
                for fromStop in stopsFromZone:
                    for toStop in stopsToZone:
                        totalDist += ttMatrix[fromStop][toStop]
                distMat[_fromZone][_toZone] = totalDist/(len(stopsFromZone)*len(stopsToZone))
            
    return distMat


def zoneDistanceMatrixMinMin(ttMatrix, stopsData, zoneListName):
    distMat = {}
    for _fromZone in zoneListName:
        distMat[_fromZone] = {}
        for _toZone in zoneListName:
            if _fromZone == _toZone:
                distMat[_fromZone][_toZone] = 0
            else:
                stopsFromZone = [v["StopName"] for v in stopsData.values() if _fromZone in v.values()]
                stopsToZone = [v["StopName"] for v in stopsData.values() if _toZone in v.values()]
                dist = 10000000000000000
                for fromStop in stopsFromZone:
                    for toStop in stopsToZone:
                        if ttMatrix[fromStop][toStop] < dist:
                            dist = ttMatrix[fromStop][toStop]
                distMat[_fromZone][_toZone] = int(dist)
            
    return distMat

def geoDistance(stopsData):
    geoTT = {}
    for _from in stopsData:
        geoTT[_from] = {}
        for _to in stopsData:
           geoTT[_from][_to] = mpu.haversine_distance((stopsData[_from]["lat"],stopsData[_from]["lng"]), (stopsData[_to]["lat"],stopsData[_to]["lng"]))
    return geoTT


def saveRouteAsJson(route, routeID):
    submission = {}
    submission[routeID] = {}
    submission[routeID]["proposed"] = {}
    for i in range(len(route)):
        submission[routeID]["proposed"][route[i]] = i
    with open(os.path.join('data/model_build_inputs/proposed_sequences.json'), 'w') as fp:
        json.dump(submission, fp)
    
    return submission