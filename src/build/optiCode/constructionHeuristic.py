import numpy as np

def nearestNeighbor(tt, stopsData):
    route = []
    for stop in stopsData.values():
        if stop['StopType'] == "depot":
            route.append(stop["StopName"])
    
    for i in range(len(stopsData)-1):
        cleanedList = list([key,value] for key, value in tt[route[i]].items() if  key != route[i] and key not in route)
        nextStop = min(cleanedList, key=lambda x: x[1])[0]
        route.append(nextStop)
    return route


def randomZone(tt, stopsData):
    z = list(stopsData.items())
    z.sort(key=lambda x: (x[1]['StopType'], x[1]['ZoneID']))
    route = [i[0] for i in z]
    zoneList = []
    counter = 0
    for i in range(1, len(z)-1):
        if z[i][1]['ZoneID'] != z[i+1][1]['ZoneID']:
            zoneList.append(counter+1)
            counter = 0
        else:
            counter += 1
        
        if i == (len(z)-2):
            zoneList.append(counter+1)
    
    return route, zoneList

def nnZone(ttZone, zoneDictname):
    currentZone = 'depot'
    routeZone = ['depot']
    zoneList = []
    routeList = zoneDictname['depot']
    for _i in range(1, len(zoneDictname)):
        cleanedList = list([key,value] for key, value in ttZone[currentZone].items() if  key != ttZone and key not in routeZone)
        if _i == 1:
            currentZone = min(cleanedList, key=lambda x: x[1])[0]
        else:
            currentZone = min(cleanedList, key=lambda x: x[1])[0]
        routeZone.append(currentZone)
        zoneList.append(len(zoneDictname[currentZone]))
        routeList = routeList + zoneDictname[currentZone]
    
    return routeList, zoneList