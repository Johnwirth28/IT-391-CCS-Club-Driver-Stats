from Requestor import WeatherRequestor
import logging
from datetime import datetime
import sys
import json



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(datetime.now().strftime('logs/scraper%m.%d.%Y.%H.%M.%S.log'))
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG,handlers=[file_handler,stream_handler])


def main():
    
    dates = ['2020-03-04','2020-03-05','2020-03-06']

    WAPI_KEY = '4fe622efc66879c6e0c78c0b4e647fe3'

    rq = WeatherRequestor(WAPI_KEY)

    responses = {}

    for date in dates:
        responses[date] = rq.getWeatherJsonFromDate(date)
    
    for a,v in responses.items():
        logger.debug(json.dumps((json.loads(v)),indent=4))




if __name__ == '__main__':
    main()