import numpy as np
import os 
import json
import mpu


def findZoneClosestStop(stop, ttMatrix, route):
    cleanedList = list([key,value] for key, value in ttMatrix[stop].items() if key != stop and isinstance(route["stops"][key]["zone_id"], str))
    cleanedList.sort(key=lambda x: x[1])
    closestStop = cleanedList[0][0]
    return closestStop

def centralityMeasure(zoneTT, zoneListName, neglectZones, start=False):
    centrality, distToDepot, zoneList, TWList = [], [], [], []
    for fromZone in zoneListName:
        if fromZone not in neglectZones:
            value = 0
            counter = 0
            for toZone in zoneListName:
                if toZone not in neglectZones:
                #if toZone != 'depot':
                    #value += zoneTT[fromZone][toZone]
                    value += zoneTT[toZone][fromZone]
                    counter += 1
            zoneList.append(fromZone)
            distToDepot.append(zoneTT['depot'][fromZone])
            centrality.append(value/counter)
    
    if start:
        newList = -np.array(centrality) + 0.05*np.array(distToDepot)
    else:
        newList = -np.array(centrality) - 0.05*np.array(distToDepot)

    centrality = np.argsort(np.argsort(-np.array(centrality)))
    distToDepot = np.argsort(np.argsort(np.array(distToDepot))) 

    

    combined = centrality + distToDepot 
    ranking = np.argsort(np.argsort(np.array(combined))) 
    centrality = {}
    rank = {}
    for idx, zone in enumerate(zoneList):
        rank[zone] = ranking[idx]
        centrality[zone] = newList[idx]

    #centrality.sort(key = lambda x: x[1], reverse=True)
    return centrality, rank

def zoneDistanceMatrix(ttMatrix, stopsData, zoneListName):
    distMat = {}
    for _fromZone in zoneListName:
        distMat[_fromZone] = {}
        for _toZone in zoneListName:
            if _fromZone == _toZone:
                distMat[_fromZone][_toZone] = 0
            else:
                totalDist = 0
                distarray = []
                stopsFromZone = [v["StopName"] for v in stopsData.values() if _fromZone in v.values()]
                stopsToZone = [v["StopName"] for v in stopsData.values() if _toZone in v.values()]
                for fromStop in stopsFromZone:
                    for toStop in stopsToZone:
                        totalDist += ttMatrix[fromStop][toStop]
                        distarray.append(ttMatrix[fromStop][toStop])
                distMat[_fromZone][_toZone] = np.mean(np.array(distarray)) #totalDist/(len(stopsFromZone)*len(stopsToZone))
            
    return distMat



def geoDistance(stopsData):
    geoTT = {}
    for _from in stopsData:
        geoTT[_from] = {}
        for _to in stopsData:
           geoTT[_from][_to] = mpu.haversine_distance((stopsData[_from]["lat"],stopsData[_from]["lng"]), (stopsData[_to]["lat"],stopsData[_to]["lng"]))
    return geoTT
