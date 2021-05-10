import datetime
import time
import math
import copy
from build.optiCode.constructionHeuristic import backWardsNN, nnZone
from build.optiCode.simulatedAnnealing import SA
from build.helpFunctions import centralityMeasure, zoneDistanceMatrix, geoDistance, findZoneClosestStop, zoneDistanceMatrixMinMin


def predict_new_routes(routeData, travelTimes):
    prediction_routes = {}
    counter = 0
    for key, value in routeData.items():
        print(counter, key)
        counter += 1
        # Define route ID
        routeID = key

        # Access the data for the ID
        origtt = travelTimes[routeID]
        route = routeData[routeID]
        stops = route["stops"]

        # Summarize data
        stopsData = {}
        zoneDict = {}
        for stop in stops:
            if route["stops"][stop]['type'] == 'Station':
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
                                "lat":   route["stops"][stop]["lat"],
                                "lng":   route["stops"][stop]["lng"],
                                "ZoneID":  zone}   

        # Derive sequences of the route     
        geott = geoDistance(stopsData)
        newtt = {}
        for key in origtt:
            newtt[key] = {}
            for key2 in origtt[key]:
                newtt[key][key2] = 135*geott[key][key2] + 0*origtt[key][key2] 

        
        #ttZone = zoneDistanceMatrix(origtt, stopsData, zoneDict)
        #ttZoneminmin = zoneDistanceMatrixMinMin(origtt, stopsData, zoneDict)
        #ttZoneGeo = zoneDistanceMatrixMaxMax(geott, stopsData, zoneDict)
        ttSpecial = zoneDistanceMatrix(newtt, stopsData, zoneDict)
        zoneRoute, zoneList = backWardsNN(ttSpecial,zoneDict, centralityMeasure(ttSpecial, zoneDict))
        instance = SA(zoneRoute, newtt, zoneList)
        SAsequenceZone = instance.multiprocessSA((6, -0.0002, False))

        prediction_routes[routeID] = {} 
        prediction_routes[routeID]['stops'] = {}
        for idx, stop in enumerate(SAsequenceZone):
            stopsData[stop]['position'] = idx
            prediction_routes[routeID]['stops'][stop] = stopsData[stop]
        
    return prediction_routes