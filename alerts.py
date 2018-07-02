import requests
import json
import traceback
import logging
import sys
import datetime as dt

#############################################
################ PARAMETERS #################
relevant = ['Red', 'Orange', 'Green-D', 'Green-B', 'Green-C', 'Green-E']

#############################################


# Setup logging
logger = logging.getLogger('mainlog')
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
logger.addHandler(stream)

# URL and headers (API-key)
url = 'https://api-v3.mbta.com'
headers = {'api_key':'k9rojBi20kesV8k_yW1WOA'}
call = '/alerts/'

try:
    # Get the current data and parse in JSON format
    response = requests.get(url+call, headers=headers)
    response_status = str(response.status_code)
    # Check that the status code is okay (200)
    if(str(response_status) != '200'):
        raise RuntimeError('Status code: ' + response_status)
    response_json = json.loads(response.text)
    data = response_json['data']
    logger.info('Got ' + str(len(data)) + ' alerts.')
except:
    logger.error('Could not get data from MBTA')
    logger.error(traceback.print_exc())
    
# response_json now holds a list of alerts
# First we need to check that the alerts are relevant
# This can be checked in response_json['attributes']['informed_entity']
relevant_data = []
for alert in data:
    try:
        route = alert['attributes']['informed_entity'][0]['route']
        if(route in relevant):
            relevant_data.append(alert)
    except:
        pass
    
logger.info('Found ' + str(len(relevant_data)) + ' revelant alerts.')

# Then we need to check that they are from the current day
# This can be checked in response_json['attributes']['active_period']
final_data = []
now = dt.datetime.now()
for alert in relevant_data:
    times = alert['attributes']['active_period']
    flagData = False
    for time in times:
        try:
            # Get the start and end time in datetime format
            startTMP = time['start']
            stopTMP = time['end']
            start = dt.datetime.strptime(startTMP[0:-6], '%Y-%m-%dT%H:%M:%S')
            stop = dt.datetime.strptime(stopTMP[0:-6], '%Y-%m-%dT%H:%M:%S')
            
            # Check that time falls within current period
            if((stop-now).days >= 0 and (start-now).days <= 0):
                flagData = True
            
        except:
            pass
        
    if(flagData):
        final_data.append(alert)
    
logger.info('Found ' + str(len(final_data)) + ' current relevant alerts.')



# Now we have the relevant and current alerts stored in final_data