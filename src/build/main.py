import datetime
import numpy as np
import time
import math
import score
import copy
from loadData import loadData
from optiCode.constructionHeuristic import nnZone, backWardsNN, forwardNN
from optiCode.simulatedAnnealing import SA
from helpFunctions import centralityMeasure, zoneDistanceMatrix, geoDistance, findZoneClosestStop, zoneDistanceMatrixMinMin

# Load Data in
routeData, routeSequences, allPackageData, travelTimes = loadData()
counter = 0
for key, value in routeData.items():
    if routeData[key]["route_score"] == "High":
        counter += 1
        print(counter)
        if counter < 1000:
            continue
        if counter > 1250:
            break
        # Define route ID
        routeID = key

        # Access the data for the ID
        origtt = travelTimes[routeID]
        routeSequence = routeSequences[routeID]["actual"]
        route = routeData[routeID]
        packageData = allPackageData[routeID]
        stops = route["stops"]

        # Summarize data
        stopsData = {}
        zoneDict = {}
        for stop in stops:
            if len(packageData[stop]) == 0:
                zone = 'depot'
                StopType = 'depot'
                depotlat = route["stops"][stop]["lat"],
                depotlng = route["stops"][stop]["lng"],
            else:
                StopType = 'dropoff'
                if isinstance(route["stops"][stop]["zone_id"], str):
                    zone = route["stops"][stop]["zone_id"]
                else:
                    closestNeighbor = findZoneClosestStop(stop, origtt, route)
                    zone = route["stops"][closestNeighbor]["zone_id"]

            if zone not in zoneDict: 
                zoneDict[zone] = [stop]
            else:
                zoneDict[zone].append(stop)

            # Now we add all relevant information to a dict
            stopsData[stop] = { "StopName": stop,
                                "StopType": StopType,
                                "sequenceSpot": routeSequence[stop],
                                "lat":   route["stops"][stop]["lat"],
                                "lng":   route["stops"][stop]["lng"],
                                "ZoneID":  zone}   
  
        # Derive sequences of the route 
        geott = geoDistance(stopsData)
        newtt = {}
        for key in origtt:
           newtt[key] = {}
           for key2 in origtt[key]:
               newtt[key][key2] = 105*geott[key][key2] + 1*origtt[key][key2] 
    
       
        ttZone = zoneDistanceMatrix(origtt, stopsData, zoneDict)
        ttZoneminmin = zoneDistanceMatrixMinMin(origtt, stopsData, zoneDict)
        #ttZoneGeo = zoneDistanceMatrixMaxMax(geott, stopsData, zoneDict)
        ttSpecial = zoneDistanceMatrix(newtt, stopsData, zoneDict)
        mzlist = stopsData.keys()
        origSequenceWithNames = sorted(mzlist, key=lambda x: (stopsData[x]['sequenceSpot']))
        

        zoneRoute, zoneList = backWardsNN(ttSpecial,zoneDict, centralityMeasure(ttSpecial, zoneDict))
        instance = SA(zoneRoute, origtt, zoneList)
        SAsequenceZone2 = instance.multiprocessSA((4, -0.0002, False))
        scoreRes2 = score.score(origSequenceWithNames + [origSequenceWithNames[0]],SAsequenceZone2 + [origSequenceWithNames[0]],copy.deepcopy(origtt))
        print(scoreRes2)