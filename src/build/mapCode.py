import folium
import os
import webbrowser
import numpy as np
import requests
import polyline
import constants
from folium.features import DivIcon
import re
import time



class Map:
    def __init__(self, markers, zoom_start=None):
        self.zoom_start = zoom_start
        self.markers = markers
        # Set center to markers center if markers exist
        nrows = len(markers)
        self.center = (2)*[0] # avgs per column
        nelem = float(nrows-1)
        self.coordinates = {}
        for stop in markers:
            if markers[stop]["StopType"] == "dropoff":
                self.center[0] += markers[stop]["lat"]
                self.center[1] += markers[stop]["lng"]
            self.coordinates[stop] = {"lat": markers[stop]["lat"],
                                      "lng": markers[stop]["lng"]}
        self.center[0] /= nelem
        self.center[1] /= nelem
        
        #Create the map
        self.my_map = folium.Map(location = self.center, zoom_start = self.zoom_start, tiles='Stamen Terrain', attr="None")

    def addMarkers(self):
        markers = self.markers
        # Add markers to map
        for stop in markers:
            if markers[stop]["StopType"] == "depot":
                folium.Marker(  [markers[stop]['lat'],markers[stop]['lng']],
                                popup = markers[stop]['StopName'],
                                icon=folium.Icon(icon='home', color='orange')).add_to(self.my_map)
            else:
                m = markers[stop]
                folium.Marker([m['lat'],m['lng']],
                             popup =" <div>{name}<br>TWS: {TWS}<br>TWE: {TWE}<br>#oP {NoPack}<br>zoneID {zoneID}</div>".format(name=m["StopName"],
                                                                                                                                TWS=m["TimeWindowStart"],
                                                                                                                                TWE=m["TimeWindowEnd"],
                                                                                                                                NoPack=m["NumberOfPackages"],
                                                                                                                                zoneID=m["ZoneID"]),
                    color='blue',
                    icon=DivIcon(html='<div style="font-size: 18pt; color : black">{stopN}</div>'.format(stopN=m["sequenceSpot"]))).add_to(self.my_map)

    
    def addDirections(self, sequence):
        success = True
        totalDuration = 0
        total_left = 0
        total_right = 0
        new_seq = [sequence[i:i+50] for i in range(0, len(sequence), 50-1)]
        for ls in new_seq:
            coord = []
            for i in ls:
                el = [self.coordinates[i]['lat'], self.coordinates[i]['lng']]   
                el.reverse()
                coord.append(el)
            body = {"coordinates":coord}
            headers = {
                'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
                'Authorization': constants.ORS_KEY,
                'Content-Type': 'application/json; charset=utf-8',
                #'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36',
            }
            r = requests.post('https://api.openrouteservice.org/v2/directions/driving-car', json=body, headers=headers)
            time.sleep(1.5)
            contentType = r.status_code
            if contentType != 200:
                print("Request from Open Source denied")
                success = False
            else:
                r = r.json()  
                total_left += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape('Turn left'), str(r['routes'][0]['segments'])))
                total_left += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape('Turn slight left'), str(r['routes'][0]['segments'])))
                total_right += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape('Turn slight right'), str(r['routes'][0]['segments'])))
                total_right += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape('Turn right'), str(r['routes'][0]['segments'])))
                totalDuration += r['routes'][0]['summary']['duration']
                geojson = r['routes'][0]['geometry']
                folium.PolyLine(locations=polyline.decode(geojson)).add_to(self.my_map)

        return totalDuration, total_left, total_right, success
    
    def addDirectionsStraight(self, sequence):
        success = True
        totalDuration = 0
        total_left = 0
        total_right = 0
        new_seq = [sequence[i:i+50] for i in range(0, len(sequence), 50-1)]
        for ls in new_seq:
            coord = []
            for i in ls:
                el = [self.coordinates[i]['lat'], self.coordinates[i]['lng']]   
                el.reverse()
                coord.append(el)
            body = {"coordinates":coord,
                    "continue_straight": True,
                    "optimized": False}
            headers = {
                'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
                'Authorization': constants.ORS_KEY,
                'Content-Type': 'application/json; charset=utf-8',
                #'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36',
            }
            r = requests.post('https://api.openrouteservice.org/v2/directions/driving-car', json=body, headers=headers)
            time.sleep(1.5)
            contentType = r.status_code
            if contentType != 200:
                print("Request from Open Source denied")
                success = False
            else:
                r = r.json()  
                total_left += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape('Turn left'), str(r['routes'][0]['segments'])))
                total_left += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape('Turn slight left'), str(r['routes'][0]['segments'])))
                total_right += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape('Turn slight right'), str(r['routes'][0]['segments'])))
                total_right += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape('Turn right'), str(r['routes'][0]['segments'])))
                totalDuration += r['routes'][0]['summary']['duration']

        return totalDuration, total_left, total_right, success

    def showMap(self):
        #Display the map
        if __name__ == '__main__':
            self.my_map.save("map.html")
            webbrowser.open("map.html")
        else:
            self.my_map.save("src/build/map.html")
            webbrowser.open(os.path.join('src/build/map.html'))