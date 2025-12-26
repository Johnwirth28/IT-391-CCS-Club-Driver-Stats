from flask import Blueprint, jsonify, request
from classes.EventPageScraper import EventPageScraper
from classes.MySQLRepository import *
import logging
from classes.Requestor import WeatherRequestor
import json
import os
import re


#logger obj
logger = logging.getLogger(__name__)



api_scrape = Blueprint('api_scrape', __name__)



def init_scrape_routes(weather_requestor:WeatherRequestor, event_page_scraper:EventPageScraper, event_chair_repo:MySQLEventChairRepo,location_repo:MySQLLocationRepo,event_repo:MySQLEventRepo,event_session_repo:MySQLEventSessionRepo,weather_repo:MySQLWeatherDataRepo,car_repo:MySQLCarRepo,session_raw_repo:MySQLSessionRawRepo,session_pax_repo:MySQLSessionPAXRepo,session_final_repo:MySQLSessionFinalRepo,run_repo:MySQLRunRepo):

    @api_scrape.route('/api/scrape', methods=['GET'])
    def scrapeEventSchedulePage():

        link=request.args.get('origin_url')
        if not link:
            return {'error':'Origin url must be provided'}, 400
        
        new_request_param = request.args.get('new_request')

        new_request_flag = False

        if new_request_param and new_request_param == 'True':
            new_request_flag = True

        
        response_json = None

        # file_name = link.strip('/:')
        # dir = '/scrapeditems/'
        

        # if os.path.isfile(file_name) and new_request_flag == False:
        #     with open(file_name, 'r') as file:
        #         response_json = json.loads(file.read())
        # else:
        try:
            response_json = event_page_scraper.scrapeEventsAndData(link)
        except Exception as err:
            return {'error':err}, 400

        
        
        
        weather_jsons = {}

        for event in response_json:
            for date,content in event['sessions'].items():
                if date not in weather_jsons.keys():
                    weather_jsons[date] = weather_requestor.getWeatherJsonFromDate(date,delay=100)
                for data in content:
                    data['weather'] = json.loads(weather_jsons[date])
        

        for event in response_json:

            event_id = event_repo.create_event(event['name'],event.get('link'))

            if event_id == 0:
                    logger.warning('event create failed')
                    continue

            for date,sessions in event['sessions'].items():

                event_session_id = event_session_repo.create_event_session(date,event_id)

                if event_session_id == 0:
                    logger.warning('event session create failed')
                    continue

                for session_data in sessions:

                    sheet_type = session_data.get('sheet_type')

                    if not sheet_type:
                        logger.warning(f'Sheet type cannot be found for session in date :{date}, event_id: {event_id}')
                        continue
                


                    match sheet_type:
                        case 'raw':
                            for entry in session_data['data']['entries']:

                                
                                car_info_expanded = re.search(r'((?P<year>\d{4})[ \t]+)?(?P<make>\w+)[ \t]+(?P<model>.*)',entry['car_model'])

                                if not car_info_expanded :
                                    logger.error(f'Bad match for car info: {entry['car_model']}')
                                    continue
                                
                                car_year= None
                                if car_info_expanded.group('year'):
                                    car_year = int (car_info_expanded.group('year'))

                                list_of_cars = car_repo.get_cars_by_params(car_info_expanded.group('make'),car_info_expanded.group('model'),car_year ,entry['driver_name'])

                                car_id = None
                                if list_of_cars:
                                    car_id = list_of_cars[0]['car_id']
                                else:
                                    car_id = car_repo.create_car(entry['driver_name'],car_info_expanded.group('make'),car_info_expanded.group('model'), car_year )

                                if car_id == 0:
                                    logger.warning('Car create failed')
                                    continue
                                
                                entry_id = session_raw_repo.create_session_raw(entry['class_abrv'],entry['car_num'],entry['raw_time'],car_id,event_session_id)

                                if entry_id == 0:
                                    logger.warning('Entry create failed')
                                    continue


                        case 'pax':
                            for entry in session_data['data']['entries']:

                                car_info_expanded = re.search(r'((?P<year>\d{4})[ \t]+)?(?P<make>\w+)[ \t]+(?P<model>.*)',entry['car_model'])

                                if not car_info_expanded :
                                    logger.error(f'Bad match for car info: {entry['car_model']}')
                                    continue
                                
                                car_year= None
                                if car_info_expanded.group('year'):
                                    car_year = int (car_info_expanded.group('year'))

                            
                                list_of_cars = car_repo.get_cars_by_params(car_info_expanded.group('make'),car_info_expanded.group('model'),car_year ,entry['driver_name'])
                               

                                car_id = None
                                if list_of_cars:
                                    car_id = list_of_cars[0]['car_id']
                                else:
                                    car_id = car_repo.create_car(entry['driver_name'],car_info_expanded.group('make'),car_info_expanded.group('model'), car_year )

                                if car_id == 0:
                                    logger.warning('Car create failed')
                                    continue
                                
                                sp_raw_time = entry['pax_time']/entry['pax_factor']

                                entry_id = session_pax_repo.create_session_pax(entry['class_abrv'],entry['car_num'],sp_raw_time,entry['pax_factor'],entry['pax_time'],car_id,event_session_id)

                                if entry_id == 0:
                                    logger.warning('Entry create failed')
                                    continue

                        case 'fin':

                            

                            for c_entry in session_data['data']['class_entries']:
                                race_class_name = c_entry['race_class_name']
                                race_class_abrv = c_entry['race_class_abrv']
                                for entry in c_entry:

                                    car_info_expanded = re.search(r'((?P<year>\d{4})[ \t]+)?(?P<make>\w+)[ \t]+(?P<model>.*)',entry['car_model'])

                                    if not car_info_expanded :
                                        logger.error(f'Bad match for car info: {entry['car_model']}')
                                        continue
                                    
                                    car_year= None
                                    if car_info_expanded.group('year'):
                                        car_year = int (car_info_expanded.group('year'))

                                    list_of_cars = car_repo.get_cars_by_params(car_info_expanded.group('make'),car_info_expanded.group('model'),car_year ,entry['driver_name'])

                                    car_id = None
                                    if list_of_cars:
                                        car_id = list_of_cars[0]['car_id']
                                    else:
                                        car_id = car_repo.create_car(entry['driver_name'],car_info_expanded.group('make'),car_info_expanded.group('model'), car_year )

                                    if car_id == 0:
                                        logger.warning('Car create failed')
                                        continue

                                    entry_id = session_final_repo.create_session_final(entry['class_abrv'],race_class_name,entry['car_num'],entry['has_trophy'],entry['car_color'],car_id,event_session_id)

                                    if entry_id == 0:
                                        logger.warning('Entry create failed')
                                        continue

                                    for run in entry['runs']:
                                        run_repo.create_run(run['time'],run['isDNF'],run['num_penalties'],entry_id)

                                    if entry_id == 0:
                                        logger.warning('Entry create failed')
                                        continue
                            
                        
                        case _:
                            logger.warning(f'Invalid sheet identifier {sheet_type} for session in date :{date}, event_id: {event_id}')
                            continue

                    weather_data = session_data.get('weather')
                    if weather_data:
                        daily = weather_data['daily']
                        usa_pressure = daily['pressure_msl_mean'] * 0.02953
                        weather_repo.create_weather(-1,-1,daily['precipitation_sum'],daily['temperature_2m_max'],daily['temperature_2m_min'],usa_pressure,daily['wind_speed_10m_mean'],daily['wind_direction_10m_dominant'],event_session_id)


        return response_json,200
                            




        



        



