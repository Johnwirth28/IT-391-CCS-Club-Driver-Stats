from datetime import datetime
import sys
import logging
from Requestor import Requestor
from EventPageScraper import EventPageScraper
import json

#Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(datetime.now().strftime('logs/scraper%m.%d.%Y.%H.%M.%S.log'))
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG,handlers=[file_handler,stream_handler])

sys.stderr = open(datetime.now().strftime('logs/err%m.%d.%Y.%H.%M.%S.log'),'w')


#Config

NEW_CALL = False

#Workspace

def main():


    origin_url = 'https://ccsportscarclub.org/autocross/schedule/'
    
    
    requestor = Requestor(None,interval_ms=2500,padding_factor=4)
    
    scraper = EventPageScraper(requestor)

    result_json = scraper.scrapeEventsAndData(origin_url)
                
    logger.info(json.dumps(result_json,indent=5,sort_keys=True))
    return 1
    



if __name__ == '__main__':
    main()
    

        
        


    


        



    









