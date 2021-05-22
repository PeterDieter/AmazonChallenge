import numpy as np
from itertools import chain
from build.helpFunctions import centralityMeasure

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

def find_in_list_of_list(mylist, char):
    for sub_list in mylist:
        if char in sub_list:
            return (mylist.index(sub_list), sub_list.index(char))
    raise ValueError("'{char}' is not in list".format(char = char))

def backWardsNN(ttZone, zoneDictname, lastZone):
    currentZone = lastZone
    routeZone = [lastZone]
    zoneList = []
    newList = []
    routeList = zoneDictname[lastZone]
    for _i in range(1, len(zoneDictname)):
        zoneList.insert(0,len(zoneDictname[currentZone])) 
        ### Change ttZone[currentZone] to ttZone[variable][currentZone]
        masterList = []
        if _i < (len(zoneDictname)-1):
            for _j in zoneDictname:
                if _j not in routeZone and _j != 'depot':
                    cleanedList = list([key,value] for key, value in ttZone[_j].items() if key != _j) #and key not in newList)
                    cleanedList.sort(key = lambda x: x[1])
                    idx, two = find_in_list_of_list(cleanedList, currentZone)
                    masterList.append([_j, idx])
            newList.append(currentZone)
            ls = [i for i, x in enumerate(masterList) if x[1] == min(masterList, key=lambda x: x[1])[1]]   
            currentLowestDist = 100000000000000
            for _k in ls:
                if ttZone[masterList[_k][0]][currentZone] < currentLowestDist:
                    currentLowestDist = ttZone[masterList[_k][0]][currentZone]
                    nextZone = masterList[_k][0]
            currentZone = nextZone

        else:
            cleanedList = list([key, ttZone[key][currentZone]] for key in ttZone.keys() if key != currentZone and key not in routeZone)
            currentZone = min(cleanedList, key=lambda x: x[1])[0]
        routeZone.insert(0,currentZone) 
        routeList = zoneDictname[currentZone] + routeList
    return routeList, zoneList

def forwardNN(ttZone, zoneDictname):
    centrality = centralityMeasure(ttZone, zoneDictname, ['depot'])
    firstZone = min(centrality, key=centrality.get)
    routeZone = ['depot', firstZone]
    routeList = zoneDictname['depot']
    currentZone = firstZone
    zoneList = []
    routeList = zoneDictname['depot'] + zoneDictname[firstZone]
    for _i in range(1, len(zoneDictname)-1):
        zoneList.append(len(zoneDictname[currentZone])) 
        centrality = centralityMeasure(ttZone, zoneDictname,routeZone)
        #cleanedList = list([key,value+0.05*centrality[key]] for key, value in ttZone[currentZone].items() if  key != ttZone and key not in routeZone)
        cleanedList = list([key, ttZone[key][currentZone] + 0.05*centrality[key]] for key in ttZone.keys() if key != currentZone and key not in routeZone)
        currentZone = min(cleanedList, key=lambda x: x[1])[0]
        routeZone.append(currentZone) 
        routeList = routeList + zoneDictname[currentZone]
    zoneList.append(len(zoneDictname[currentZone]))
    routeList[1:len(routeList)] = routeList[1:len(routeList)][::-1]
    zoneList = zoneList[::-1]
    return routeList, zoneList
