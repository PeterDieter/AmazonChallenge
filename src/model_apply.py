from os import path
from apply.main import predict_new_routes
import sys, json, time

# Get Directory
BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))

# Read input data
print('Reading Input Data')
# Model Build output
# model_path=path.join(BASE_DIR, 'data/model_build_outputs/model.json')
# with open(model_path, newline='') as in_file:
#     model_build_out = json.load(in_file)
# Prediction Routes (Model Apply input)
prediction_routes_path = path.join(BASE_DIR, 'data/model_apply_inputs/new_route_data.json')
prediction_ttMatrix_path = path.join(BASE_DIR, 'data/model_apply_inputs/new_travel_times.json')
prediction_packageData_path = path.join(BASE_DIR, 'data/model_apply_inputs/new_package_data.json')
with open(prediction_routes_path, newline='') as in_file:
  prediction_routes = json.load(in_file)
with open(prediction_ttMatrix_path, newline='') as in_file:
  prediction_travelTimes = json.load(in_file)
with open(prediction_packageData_path, newline='') as in_file:
  prediction_packages = json.load(in_file)



def sort_by_key(stops, sort_by):
    """
    Takes in the `prediction_routes[route_id]['stops']` dictionary
    Returns a dictionary of the stops with their sorted order always placing the depot first

    EG:

    Input:
    ```
    stops={
      "Depot": {
        "lat": 42.139891,
        "lng": -71.494346,
        "type": "depot",
        "zone_id": null
      },
      "StopID_001": {
        "lat": 43.139891,
        "lng": -71.494346,
        "type": "delivery",
        "zone_id": "A-2.2A"
      },
      "StopID_002": {
        "lat": 42.139891,
        "lng": -71.494346,
        "type": "delivery",
        "zone_id": "P-13.1B"
      }
    }

    print (sort_by_key(stops, 'lat'))
    ```

    Output:
    ```
    {
        "Depot":1,
        "StopID_001":3,
        "StopID_002":2
    }
    ```

    """
    # Serialize keys as id into each dictionary value and make the dict a list
    stops_list=[{**value, **{'id':key}} for key, value in stops.items()]

    # Sort the stops list by the key specified when calling the sort_by_key func
    ordered_stop_list=sorted(stops_list, key=lambda x: x[sort_by])

    # Keep only sorted list of ids
    ordered_stop_list_ids=[i['id'] for i in ordered_stop_list]

    # Serialize back to dictionary format with output order as the values
    return {i:ordered_stop_list_ids.index(i) for i in ordered_stop_list_ids}

def propose_all_routes(prediction_routes, sort_by):
    """
    Applies `sort_by_key` to each route's set of stops and returns them in a dictionary under `output[route_id]['proposed']`

    EG:

    Input:
    ```
    prediction_routes = {
      "RouteID_001": {
        ...
        "stops": {
          "Depot": {
            "lat": 42.139891,
            "lng": -71.494346,
            "type": "depot",
            "zone_id": null
          },
          ...
        }
      },
      ...
    }

    print(propose_all_routes(prediction_routes, 'lat'))
    ```

    Output:
    ```
    {
      "RouteID_001": {
        "proposed": {
          "Depot": 0,
          "StopID_001": 1,
          "StopID_002": 2
        }
      },
      ...
    }
    ```
    """
    return {key:{'proposed':sort_by_key(stops=value['stops'], sort_by=sort_by)} for key, value in prediction_routes.items()}

print('\nApplying answer with real model...')
predicted_routes = predict_new_routes(prediction_routes, prediction_travelTimes)
#print('Sorting data by the key: {}'.format(sort_by))
output=propose_all_routes(prediction_routes=predicted_routes, sort_by='position')
print('Data sorted!')

# Write output data
output_path=path.join(BASE_DIR, 'data/model_apply_outputs/proposed_sequences.json')
with open(output_path, 'w') as out_file:
    json.dump(output, out_file)
    print("Success: The '{}' file has been saved".format(output_path))

print('Done!')
