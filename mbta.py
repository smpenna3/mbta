import requests
import json
from geopy.distance import vincenty
from geopy.geocoders import Nominatim
import traceback
import logging
import sys

# Setup logging
logger = logging.getLogger('mainlog')
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
logger.addHandler(stream)

# Setup up geolocator
geolocator = Nominatim(user_agent='smpmbtsa')

address = '1 Main Street Cambridge MA' # Address to find predictions around
location = geolocator.geocode(address) # Find the GPS coordinates of the address
radius = 100.5 #km # Set the radius to find within
#types = ['Rapid Transit', 'Commuter Rail', 'Local Bus', 'Key Bus Route (Frequent Service)']
types = ['Rapid Transit'] # Select the types of service to include

# URL and headers (API-key)
url = 'https://api-v3.mbta.com'
headers = {'api_key':'k9rojBi20kesV8k_yW1WOA'}


# Get data
call = '/predictions?filter[latitude]='+str(location.latitude)+'&filter[longitude]='+str(location.longitude)+'&filter[radius]='+str(radius)+'&include=stop,route,trip'


try:
	# Get the current data and parse in JSON format
	response = requests.get(url+call, headers=headers)
	response_status = str(response.status_code)
	# Check that the status code is okay (200)
	if(str(response_status) != '200'):
		raise RuntimeError('Status code: ' + response_status)
	response_json = json.loads(response.text)
except:
	logger.error('Could not get data from MBTA')
	logger.error(traceback.print_exc())
	sys.exit()

# Sort the included data into the categories defined
# The 'type' key holds the required sorting info

# Define empty array
stops = {}
trips = {}
routes = {}
# Fill arrays with data
for item in response_json['included']:
	if(item['type'] == 'stop'):
		print(item['attributes']['name'])
		# If the item is a stop, append the ID, name, and location
		stop_id = item['id']
		stop_name = item['attributes']['name']
		stop_lat = item['attributes']['latitude']
		stop_lon = item['attributes']['longitude']
		stops[stop_id] = [stop_name, stop_lat, stop_lon]
		
	elif(item['type'] == 'trip'):
		# If the item is a trip, append the ID, name, headsign name, and direction
		trip_id = item['id']
		trip_name = item['attributes']['name']
		if(trip_name == ''):
			trip_name = 'none'
		trip_headsign = item['attributes']['headsign']
		trip_direction = item['attributes']['direction_id']
		
		trips[trip_id] = [trip_name, trip_headsign, trip_direction]
		
	elif(item['type'] == 'route'):
		# If the item is a route, append the ID, name, directions list, and description (type ex bus)
		route_id = item['id']
		route_name = item['attributes']['long_name']
		if(route_name == ''):
			route_name = 'none'
		route_directions = item['attributes']['direction_names']
		route_description = item['attributes']['description']
		
		routes[route_id] = [route_name, route_directions, route_description]
		
	else:
		raise KeyError('Invalid key: ' + item['type'])
		
	
# Fill array with the prediction data
predictions = []
for item in response_json['data']:
	# Append the array with a JSON holding all relevant data
	p_route_id = item['relationships']['route']['data']['id']
	p_route_name = routes[p_route_id][0]
	p_route_directions = routes[p_route_id][1]
	p_route_description = routes[p_route_id][2]
	
	p_stop_id = item['relationships']['stop']['data']['id']
	p_stop_name = stops[p_stop_id][0]
	p_stop_lat = stops[p_stop_id][1]
	p_stop_lon = stops[p_stop_id][2]
	
	p_trip_id = item['relationships']['trip']['data']['id']
	p_trip_name = trips[p_trip_id][0]
	p_trip_headsign = trips[p_trip_id][1]
	p_trip_direction  = trips[p_trip_id][2]
	
	p_time = item['attributes']['departure_time']
	p_status = item['attributes']['status']

	'''
	# If the description is a bus line, the name of the route will be the ID so add that
	'''
	
	p_route_json = {}
	p_route_json['id'] = p_route_id
	p_route_json['name'] = p_route_name
	p_route_json['directions'] = p_route_directions
	p_route_json['description'] = p_route_description
	
	p_stop_json = {}
	p_stop_json['id'] = p_stop_id
	p_stop_json['name'] = p_stop_name
	p_stop_json['latitude'] = p_stop_lat
	p_stop_json['longitude'] = p_stop_lon
	
	p_trip_json = {}
	p_trip_json['id'] = p_trip_id
	p_trip_json['name'] = p_trip_name
	p_trip_json['headsign'] = p_trip_headsign
	p_trip_json['direction'] = p_trip_direction
	
	p_json = {}
	p_json['route'] = p_route_json
	p_json['stop'] = p_stop_json
	p_json['trip'] = p_trip_json
	p_json['time'] = p_time
	p_json['status'] = p_status
	
	predictions.append(p_json)
	

# Keep only predictions which include a stop in the given radius and with given description
predictions_nearby = [prediction for prediction in predictions if ((vincenty((location.latitude, location.longitude), (prediction['stop']['latitude'],prediction['stop']['longitude'])) < radius) and (prediction['route']['description'] in types))]
# This list will be formatted with each item being a json with a corresponding departure time.  The time json includes all stop, route, and trip information

print('%35s - %15s - %10s - %20s' % ('Stop', 'Line', 'Direction', 'Time'))
for item in predictions_nearby:
	print('%15s - %15s - %10s - %20s' % (item['stop']['name'], item['route']['name'], item['route']['directions'][item['trip']['direction']], item['time']))

'''
print(predictions_nearby)
for item in predictions_nearby:
	print item['stop']['name']
'''
