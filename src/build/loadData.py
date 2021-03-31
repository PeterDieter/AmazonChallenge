import json

def loadData():
    with open("data/model_build_inputs/route_data.json") as f:
        routeData = json.load(f)
        for key, value in routeData.items():
            if routeData[key]["route_score"] == "High":
                print (key)

    with open("data/model_build_inputs/actual_sequences.json") as f:
        routeSequences = json.load(f)

    with open("data/model_build_inputs/package_data.json") as f:
        packageData = json.load(f)

    # Load travel time
    with open('data/model_build_inputs/travel_times.json') as infile:
        travelTimes = json.load(infile)
    

    return routeData, routeSequences, packageData, travelTimes