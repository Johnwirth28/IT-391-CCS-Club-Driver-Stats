

import pickle

from datetime import datetime
import sys
import logging
from Requestor import Requestor
from Parser import EventPageParser,RawDataPageParser,PaxDataPageParser, FinalDataPageParser

#Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename=datetime.now().strftime('logs/scraper%m.%d.%Y.%H.%M.%S.log'))


#Config

NEW_CALL = False



#-----------------Helper Funcs--------------#

def printEvents(events):
    for item in events:
        print("Event {}:".format(events.index(item)))
        for key,value in item.items():
            if type(value) == list:
                print('{}:'.format(key))
                if len(value) != 0:
                    for i in value:
                        print('\t{}'.format(i))
                else:
                    print('No links found')
            else:
                print("{}: {}".format(key,value))
        print()

    


#Workspace

def main():


    origin_url = 'https://ccsportscarclub.org/autocross/schedule/'
    
    
    requestor = Requestor(None,interval_ms=10000)
    
    origin_data = requestor.makeRequest(origin_url)

    if origin_data['status_code'] != 200:
        print('Origin url request failed.\nExiting...')
        exit(1)
        
    origin_events = EventPageParser.scrapeEventsPageContent(origin_data['contents'])

    for event in origin_events:
        for link_bundle in event['session_data_links']:
            response = requestor.makeRequest(link_bundle[0])
            if response['status_code'] == 200:
                link_bundle[1] = response['content']
                
    
    return 1
    



if __name__ == '__main__':
    main()
    

        
        


    


        



    









