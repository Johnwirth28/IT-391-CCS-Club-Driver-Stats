from datetime import datetime
import sys
import logging
from Requestor import Requestor,WeatherRequestor
from EventPageScraper import EventPageScraper
import json
import emojis


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



#Config

NEW_CALL = False

#Workspace

def main():


    origin_url = 'https://ccsportscarclub.org/autocross/schedule/'
    WAPI_KEY = '4fe622efc66879c6e0c78c0b4e647fe3'

    requestor = Requestor(None,interval_ms=2500,padding_factor=4)
    weather_requestor = WeatherRequestor(WAPI_KEY)
    
    scraper = EventPageScraper(requestor)

    result_json = scraper.scrapeEventsAndData(origin_url)

    weather_jsons = {}

    for event in result_json:
        for date,content in event['sessions'].items():
            if date not in weather_jsons.keys():
                new_date = datetime.strptime(date,'%m-%d-%Y').strftime('%Y-%m-%d')
                weather_jsons[date] = weather_requestor.getWeatherJsonFromDate(new_date,delay=100)
            for data in content:
                data['weather'] = json.loads(weather_jsons[date])
                

                
    logger.info(json.dumps(result_json,indent=5,sort_keys=True))
    






    



if __name__ == '__main__':
    main()
    

        
        


    


        



    









