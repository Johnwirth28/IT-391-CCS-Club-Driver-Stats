from  classes.Requestor import Requestor
from classes.Parser import EventPageParser,RawDataPageParser,PaxDataPageParser, FinalDataPageParser
from abc import ABC,abstractmethod
import re
import json
import logging

logger = logging.getLogger(__name__)



class BaseEventPageScraper(ABC):

    @abstractmethod
    def __init__(self,**kwargs):
        pass
    
    @abstractmethod
    def scrapeEventsAndData(self,events_page_url) ->list:
        pass



class EventPageScraper(BaseEventPageScraper):

 
    def __init__(self,requestorObj:Requestor):
        self.__requestor = requestorObj
        self.__failed_links = []
 
    def scrapeEventsAndData(self,events_page_url):

        logger.info(f'Making request to origin site at {events_page_url}')
        origin_data = self.__requestor.makeRequest(events_page_url)

        if origin_data['status_code'] != 200:
            raise ConnectionRefusedError('Origin url request failed.\nExiting...')
        
        logger.info(f'Successful request')
            
        parsed_content = EventPageParser.parseEventsPageContent(origin_data['content'])
        origin_events =[]
        if parsed_content['events']:
            origin_events = parsed_content['events']
        
        for event in origin_events:
            
            logger.info(f'Gathering links to send from event \'{event['name']}\'')
            response_bundles = self.__processResultsLinks(event['session_data_links'])
            event['sessions'] = {}

            for response in response_bundles:

                url = response['link']

                if response['status_code'] != 200:
                    self.__failed_links.append({'event_name':event['name'], 'response':response})
                    logger.debug(f'Link failed with status code {response['status_code']} : {url}')
                    continue
                    
                

                sheet_type = ''
                
                match = re.search(r'.*((fin)|(raw)|(pax)).*',url)
                if match:
                    sheet_type = match.group(1)
                else:
                    logger.warning(f'Found link with improper format: {url}')
                    continue
                

                result_dict = {'sheet_type':sheet_type,'data':None}

                if sheet_type == 'raw':
                    result_dict['data'] = RawDataPageParser().parseRawDataPageContent(response['content'])
                elif sheet_type == 'pax':
                    result_dict['data'] = PaxDataPageParser().parsePaxDataPageContent(response['content'])
                elif sheet_type == 'fin':
                    result_dict['data'] = FinalDataPageParser().parseFinalDataPageContent(response['content'])
                else:
                    logger.debug('Improper point in file reached. File format incorrect')
                    raise NameError('Data type of URL could not be determined')
                
                result_page_date = result_dict['data']['date']

                if result_page_date in event['sessions'].keys():
                    event['sessions'][result_page_date].append(result_dict)
                else:
                    event['sessions'][result_page_date] = [result_dict]
                
        return origin_events
            
            


    def __processResultsLinks(self, links):
        num_links = len(links)
        responses = []
        logger.info(f'Processing {num_links} links.')
        for index,link in enumerate(links):
            logger.info(f'Request [{index+1},{num_links}],  {link}')
            response = self.__requestor.makeRequest(link,1000)

            if response['status_code'] == 200:
                logger.info(f'Successful request')
            else:
                logger.info(f'Failed Request')
            responses.append(response)
        return responses
            
                
