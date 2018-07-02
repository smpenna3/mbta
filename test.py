import requests
import json
import math
from geopy.distance import vincenty
import traceback
import logging

# Setup logging
logger = logging.getLogger('mainlog')
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
logger.addHandler(stream)

url = 'https://api-v3.mbta.com'

headers = {'api_key':'k9rojBi20kesV8k_yW1WOA'}

lat = 42.3438654
lon = -71.0880786
radius = 0.00000005

call = '/predictions?filter[latitude]='+str(lat)+'&filter[longitude]='+str(lon)+'&filter[radius]='+str(radius)+'&include=stop,route,trip'

r = requests.get(url+call, headers=headers)

print('code: ' + str(r.status_code))
#print(json.dumps(r.text, indent=4))
j = json.loads(r.text)
#print(json.dumps(j['included'][0], indent=4))
#print(json.dumps(j['included'][1], indent=4))
#print(json.dumps(j['included'][2], indent=4))
#print(json.dumps(j['included'][3], indent=4))
#print(json.dumps(j['included'][0], indent=4))
#print(json.dumps(j['included'][31], indent=4))

#print('vince: ' + str(vincenty((lat, lon), (42.347779, -71.085476))))


print(len(j['data']))
print(len(j['included']))

for i in range(0, 50):
    print(str(i) + ' ' + str(j['included'][i].keys()))

with open('j.txt', 'w') as f:
    pass
    #f.write(j['included'])
    
    
    
