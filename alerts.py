import requests
import json
import traceback
import logging
import sys
import datetime as dt
import tkinter as tk

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
call = '/alerts?filter[route_type]=0,1'

def getAlerts(log=True):
##############################################
# Get Data and find relevant info
    try:
        # Get the current data and parse in JSON format
        logger.info('Getting info....')
        response = requests.get(url+call, headers=headers)
        response_status = str(response.status_code)
        # Check that the status code is okay (200)
        if(str(response_status) != '200'):
            raise RuntimeError('Status code: ' + response_status)
        response_json = json.loads(response.text)
        data = response_json['data']
        if(log):
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

    if(log):
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
                start = dt.datetime.strptime(startTMP[0:-6], '%Y-%m-%dT%H:%M:%S')
                endTMP = time['end']

                if((start-now).days <= 0 and endTMP is None):
                    # If the end date is not defined
                    pass
                    #flagData = True        
                else:
                    end = dt.datetime.strptime(endTMP[0:-6], '%Y-%m-%dT%H:%M:%S')

                    # Check that time falls within current period
                    if((end-now).days >= 0 and (start-now).days <= 0):
                        flagData = True

                    else:
                        pass
                        #logger.debug(str('\n' + str(startTMP) + ' - ' + #str(endTMP)))


            except:
                logger.error(traceback.print_exec())
                pass

        if(flagData):
            final_data.append(alert)
        else:
            pass

    if(log):
        logger.info('\nFound ' + str(len(final_data)) + ' current relevant alerts.\n')
        
    return final_data

        

def printAlerts(alertList):
    ##############################################
    # Print the relevant alerts which were found
    # MUST be called after get Alerts
    # Now we have the relevant and current alerts stored in final_data
    for alert in alertList:
        logger.info('\n-------------------------------------') #  Break
        logger.info(alert['attributes']['effect']) # Print effect (Station closure, delay, etc.)
        logger.info(alert['attributes']['short_header']) # Print short description
        #logger.info(alert['attributes']['active_period']) # Print times effected

        

##############################################
# Main function
def main():
    alertList = getAlerts()
    printAlerts(alertList)
    
    
class alertWindow:
    pass

# Run main
main()