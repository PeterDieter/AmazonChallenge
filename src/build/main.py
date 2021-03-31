import mapCode
import datetime
import numpy as np
import time
import math
import textdistance
from loadData import loadData
from optiCode.KPIFunctions import getObjectiveValue, getArrivalTimes, neighborNextDeviation, nextNeighbor, firstLastDistance, zoneNearestNeighbor, zoneViolations
from optiCode.constructionHeuristic import nearestNeighbor, randomZone, nnZone
from optiCode.simulatedAnnealing import SA, SAZone
from helpFunctions import findZoneClosestStop, zoneDistanceMatrix, zoneDistanceMatrixMinMin, geoAttributes, saveRouteAsJson
import score

# Load Data in
routeData, routeSequences, allPackageData, travelTimes = loadData()

# Define route ID
routeID = "RouteID_e4bf9524-79c1-462c-a1ee-ce530d288ade"

# Access the data for the ID
tt = travelTimes[routeID]
routeSequence = routeSequences[routeID]["actual"]
route = routeData[routeID]
packageData = allPackageData[routeID]
stops = route["stops"]


# Summarize data
stopsData = {}
zoneListName = {}
counter = 0
for stop in stops:
    if len(packageData[stop]) == 0:
        zone = 'depot'
        latestStart = None
        earliestClosing = None
        StopType = 'depot'
        serviceTime = 0
    else:
        # First we extract the time windows for the packages
        tws = {}
        for package in packageData[stop]:
            if type(packageData[stop][package]["time_window"]['start_time_utc']) != float:
                x = datetime.datetime.strptime(packageData[stop][package]["time_window"]['start_time_utc'], '%Y-%m-%d %H:%M:%S')
                packageData[stop][package]["time_window"]['start_time_utc'] = (x-datetime.datetime(1970,1,1)).total_seconds()
            if type(packageData[stop][package]["time_window"]['end_time_utc']) != float:
                x = datetime.datetime.strptime(packageData[stop][package]["time_window"]['end_time_utc'], '%Y-%m-%d %H:%M:%S')
                packageData[stop][package]["time_window"]['end_time_utc'] = (x-datetime.datetime(1970,1,1)).total_seconds()
            tws[package] = {"TimeWindow": packageData[stop][package]["time_window"]}       
        latestStart = max(d['TimeWindow']['start_time_utc'] for d in tws.values())
        if not math.isnan(latestStart):
            counter += 1
        earliestClosing = min(d['TimeWindow']['end_time_utc'] for d in tws.values())
        serviceTime = packageData[stop][package]['planned_service_time_seconds']
        StopType = 'dropoff'

        if isinstance(route["stops"][stop]["zone_id"], str):
            zone = route["stops"][stop]["zone_id"]
        else:
            closestNeighbor = findZoneClosestStop(stop, tt, route)
            zone = route["stops"][closestNeighbor]["zone_id"]

    if zone not in zoneListName: 
        zoneListName[zone] = [stop]
    else:
        zoneListName[zone].append(stop)

    # Now we add all relevant information to a dict
    stopsData[stop] = { "StopName": stop,
                        "StopType": StopType,
                        "sequenceSpot": routeSequence[stop],
                        "lat":   route["stops"][stop]["lat"],
                        "lng":   route["stops"][stop]["lng"],
                        "NumberOfPackages":   len(packageData[stop]),
                        "TimeWindowStart":   latestStart,
                        "TimeWindowEnd":  earliestClosing,
                        "ZoneID":  zone,
                        "ServiceTime":   serviceTime}   

# Derive sequences of the route 
mzlist = stopsData.keys()
origSequenceWithNames = sorted(mzlist, key=lambda x: (stopsData[x]['sequenceSpot']))
print(counter)
ttZone = zoneDistanceMatrixMinMin(tt, stopsData, zoneListName)
startTime = route['departure_time_utc']
startDate = route['date_YYYY_MM_DD']

start_time = time.time()
zoneRoute, zoneList = nnZone(ttZone, zoneListName)
instance = SAZone(zoneRoute, tt, stopsData, zoneList, origSequenceWithNames,startTime, startDate)
SAsequenceZone = instance.multiprocessSA(6)
subJson = saveRouteAsJson(SAsequenceZone, routeID)
print("--- %s seconds ---" % (time.time() - start_time))

start_time = time.time()
startSequence = nearestNeighbor(tt, stopsData)
instance = SA(zoneRoute, tt, stopsData)
SAsequence = instance.multiprocessSA(70000)
print("--- %s seconds ---" % (time.time() - start_time))

print(score.score(origSequenceWithNames + [SAsequence[0]],SAsequenceZone + [SAsequence[0]],tt))
print(score.score(origSequenceWithNames + [SAsequence[0]],SAsequence + [SAsequence[0]],tt))
print(score.score(origSequenceWithNames + [SAsequence[0]],startSequence + [SAsequence[0]],tt))

# Calculate arrival times
stopsData = getArrivalTimes(tt, startTime, startDate, origSequenceWithNames, stopsData)
slackBeginningTW = np.array(list(d['slackBeginningTW'] for d in stopsData.values()))
slackEndTW = np.array(list(d['slackEndTW'] for d in stopsData.values()))

deviations = neighborNextDeviation(tt, origSequenceWithNames)
nextNeighbors = np.array(nextNeighbor(tt, origSequenceWithNames))
zoneNeighbors = np.array(zoneNearestNeighbor(tt, origSequenceWithNames, stopsData, 3))
zoneViolations = zoneViolations(tt, origSequenceWithNames, stopsData)
print(zoneViolations)

# Calculate Objective value
total_duration_AMZ = getObjectiveValue(tt, origSequenceWithNames)
total_duration_SA = getObjectiveValue(tt, SAsequence)
total_duration_SAZone = getObjectiveValue(tt, SAsequenceZone)
total_duration_StartSeq = getObjectiveValue(tt, startSequence)
print("Levensthein distance", textdistance.levenshtein.distance(zoneRoute,origSequenceWithNames)/len(stopsData))
print("Levensthein distance", textdistance.levenshtein.distance(startSequence,origSequenceWithNames)/len(stopsData))
print("Levensthein distance", textdistance.levenshtein.distance(SAsequence,origSequenceWithNames)/len(stopsData))
print("Levensthein distance", textdistance.levenshtein.distance(SAsequenceZone,origSequenceWithNames)/len(stopsData))

# Plot map and get data from OpenRoute
map = mapCode.Map(zoom_start=15, markers=stopsData)
total_duration_curve, total_left_curve, total_right_curve, success_curve = map.addDirections(origSequenceWithNames)
map.addMarkers()
map.showMap()


for i in range(len(SAsequenceZone)):
    stopsData[SAsequenceZone[i]]["sequenceSpot"] = i

map = mapCode.Map(zoom_start=15, markers=stopsData)
total_duration_curve, total_left_curve, total_right_curve, success_curve = map.addDirections(SAsequenceZone)
map.addMarkers()
map.showMap()
#total_duration_straight, total_left_straight, total_right_straight, success_straight = map.addDirectionsStraight(origSequenceWithNames)
if success_curve:
    # Print results
    print("Duration of curves", total_duration_curve)
    #print("Duration straight", total_duration_straight)
    #print("Straight vs Curves", (total_duration_straight-total_duration_curve)/total_duration_curve)
    print("Duration AMZ", total_duration_AMZ)
    print("Duration ORS_curve", total_duration_curve)
    print("Duration NN", total_duration_StartSeq)
    print("Duration SA", total_duration_SA)
    print("Change of ORS as AMZ base",(total_duration_curve-total_duration_AMZ)/total_duration_AMZ)
    print("Change of Start Sequence as AMZ base",(total_duration_StartSeq-total_duration_AMZ)/total_duration_AMZ)
    print("Change of SA as AMZ base",(total_duration_SA-total_duration_AMZ)/total_duration_AMZ)
    print("Change of SAZone as AMZ base",(total_duration_SAZone-total_duration_AMZ)/total_duration_AMZ)
    print("Minimum Slack Beginning TW", np.nanmin(slackBeginningTW))
    print("Average Slack Beginning TW", np.nanmean(slackBeginningTW))
    print("Violated Time Window Beginnings", (slackBeginningTW<0).sum()/len(stopsData))
    print("Almost violated Time Window Beginnings", (slackBeginningTW<600).sum()/len(stopsData))
    print("Minimum Slack End TW", np.nanmin(slackEndTW))
    print("Average Slack End TW", np.nanmean(slackEndTW))
    print("Violated Time Window Ends", (slackEndTW<0).sum()/len(stopsData))
    print("Almost violated Time Window Ends", (slackEndTW<600).sum()/len(stopsData))
    print("Max deviation from NN", np.max(deviations)/len(stopsData))
    print("Mean deviation from NN", np.mean(deviations))
    print("Median deviation from NN", np.median(deviations))
    print("75% Quantile deviation from NN", np.quantile(deviations, 0.75))
    print("STDV deviation from NN", np.std(deviations))
    print("Max Different from NN", np.max(nextNeighbors)/len(stopsData))
    print("Mean Different from NN", np.mean(nextNeighbors))
    print("Median Different from NN", np.median(nextNeighbors))
    print("75% Quantile Different from NN", np.quantile(nextNeighbors, 0.75))
    print("STDV Different from NN", np.std(nextNeighbors))
    print("Occurences of not going to one of the 5 closest neighbors", (nextNeighbors>5).sum()/len(stopsData))
    print("First last relative distance", firstLastDistance(tt, origSequenceWithNames))
    print("Levensthein distance", textdistance.levenshtein.distance(startSequence,origSequenceWithNames)/len(stopsData))
    print(route["route_score"])



    

