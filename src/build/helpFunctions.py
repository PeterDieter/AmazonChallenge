import numpy as np
import os 
import json
from optiCode.KPIFunctions import getArrivalTimes
from optiCode.KPIFunctions import neighborNextDeviation


def findZoneClosestStop(stop, ttMatrix, route):
    cleanedList = list([key,value] for key, value in ttMatrix[stop].items() if key != stop and isinstance(route["stops"][key]["zone_id"], str))
    cleanedList.sort(key=lambda x: x[1])
    closestStop = cleanedList[0][0]
    return closestStop

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
                distMat[_fromZone][_toZone] = int(totalDist/(len(stopsFromZone)*len(stopsToZone)))
            
    return distMat

def zoneDistanceMatrixMinMin(ttMatrix, stopsData, zoneListName):
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
                dist = 10000000000000000
                for fromStop in stopsFromZone:
                    for toStop in stopsToZone:
                        if ttMatrix[fromStop][toStop] < dist:
                            dist = ttMatrix[fromStop][toStop]
                distMat[_fromZone][_toZone] = int(dist)
            
    return distMat

def geoAttributes(stopsData):
    minlng = min(stopsData.values(), key=lambda v:v['lng'] if v['StopType'] != 'depot' else float('inf'))['lng']
    maxlng = max(stopsData.values(), key=lambda v:v['lng'] if v['StopType'] != 'depot' else float('-inf'))['lng']
    minlat = min(stopsData.values(), key=lambda v:v['lat'] if v['StopType'] != 'depot' else float('inf'))['lat']
    maxlat = max(stopsData.values(), key=lambda v:v['lat'] if v['StopType'] != 'depot' else float('-inf'))['lat']
    return ((maxlng-minlng) * (maxlat - minlat))
        
def createMLdata(route,stopsData, tt, startTime, startDate, zoneList):
    stopsData = getArrivalTimes(tt, startTime, startDate, route, stopsData)
    deviations = np.array(neighborNextDeviation(tt, route))
    slackBeginningTW = np.array(list(d['slackBeginningTW'] for d in stopsData.values()))
    slackEndTW = np.array(list(d['slackEndTW'] for d in stopsData.values()))  
    res = [
        len(stopsData),
        #(total_duration_SAZone - total_duration_StartSeq) / total_duration_StartSeq,
        np.nanmin(slackBeginningTW),
        np.nanmedian(slackBeginningTW),
        np.nanquantile(slackBeginningTW, 0.75),
        np.nanquantile(slackBeginningTW, 0.25),
        np.nanmean(slackBeginningTW),
        (slackBeginningTW<0).sum()/len(stopsData),
        np.nanmin(slackEndTW),
        np.nanmean(slackEndTW),
        np.nanquantile(slackEndTW, 0.75),
        np.nanquantile(slackEndTW, 0.25),
        np.nanmedian(slackEndTW),
        len(zoneList),
        np.max(deviations)/len(stopsData),
        np.mean(deviations),
        np.median(deviations),
        np.quantile(deviations, 0.75),
        np.std(deviations),
    ]
    return np.array(res).reshape(1, -1)

def saveRouteAsJson(route, routeID):
    submission = {}
    submission[routeID] = {}
    submission[routeID]["proposed"] = {}
    for i in range(len(route)):
        submission[routeID]["proposed"][route[i]] = i
    with open(os.path.join('data/model_build_inputs/proposed_sequences.json'), 'w') as fp:
        json.dump(submission, fp)
    
    return submission