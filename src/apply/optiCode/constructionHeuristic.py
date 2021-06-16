from apply.helpFunctions import centralityMeasure

def forwardNN(ttZone, zoneDictname, ttNormal, stopsData):
    centrality = centralityMeasure(ttZone, zoneDictname, ["depot"], start=True)
    firstZone = min(centrality, key=centrality.get)
    routeZone = ['depot', firstZone]
    currentZone = firstZone
    zoneList = []
    routeList = zoneDictname['depot']
    for _i in range(len(zoneDictname[currentZone])):
        currentStop = routeList[-1]
        cleanedList = list([key,ttNormal[currentStop][key]] for key in ttNormal.keys()if  key != currentStop and key not in routeList and stopsData[key]['ZoneID'] == currentZone)
        nextStop = min(cleanedList, key=lambda x: x[1])[0]
        routeList.append(nextStop) 
    for _j in range(1, len(zoneDictname)-1):
        zoneList.append(len(zoneDictname[currentZone])) 
        centrality = centralityMeasure(ttZone, zoneDictname, routeZone, start=False)
        cleanedList = list([key, ttZone[currentZone][key] + 1*centrality[key]] for key in ttZone.keys() if key != currentZone and key not in routeZone)
        currentZone = min(cleanedList, key=lambda x: x[1])[0]
        routeZone.append(currentZone) 
        for _k in range(len(zoneDictname[currentZone])):
            currentStop = routeList[-1]
            cleanedList = list([key,ttNormal[currentStop][key]] for key in ttNormal.keys()if  key != currentStop and key not in routeList and stopsData[key]['ZoneID'] == currentZone)
            nextStop = min(cleanedList, key=lambda x: x[1])[0]
            routeList.append(nextStop) 
    zoneList.append(len(zoneDictname[currentZone]))
    return routeList, zoneList