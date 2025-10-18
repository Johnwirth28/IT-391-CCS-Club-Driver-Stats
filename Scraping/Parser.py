from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from datetime import datetime
import re

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename=datetime.now().strftime(f'logs/{__name__}%m.%d.%Y.%H.%M.%S.log'))


#Provides methods for extracting html content from CCSCC events page
class EventPageParserBase(ABC):
    
    #Returns dictionary with event session pages or None
    @classmethod
    @abstractmethod
    def parseEventsPageContent(cls,page_content):
        raise NotImplementedError
    
    # Returns dictionary with event data or None
    @classmethod
    @abstractmethod
    def __parseEventTableRow(cls,page_content):
        raise NotImplementedError
   
   
#Provides methods for extracting html content from CCSCC raw data pages
class RawDataPageParserBase(ABC):
    
    @classmethod
    @abstractmethod
    def parseRawDataPageContent(cls,page_content):
        raise NotImplementedError

#Provides methods for extracting html content from CCSCC pax data pages
class PaxDataPageParserBase(ABC):

    @classmethod
    @abstractmethod
    def parseRawDataPageContent(cls,page_content):
        raise NotImplementedError
    
#Provides methods for extracting html content from CCSCC final data pages
class FinalDataPageParserBase(ABC):
    
    @classmethod
    @abstractmethod
    def parseFinalDataPageContent(cls,page_content):
        raise NotImplementedError
    

    
    
    
#Parser used for 2025 events schedule page
class EventPageParser(EventPageParserBase):

    #Returns dictionary with event session html
    @classmethod
    def parseEventsPageContent(cls,page_content):
        soup = BeautifulSoup(page_content,'html.parser')

        events = []

        key_table_item = soup.find("strong",string="Event",recursive=True)
        
        if key_table_item is None:
            print("Failed to find first event")
            exit(1)
        
        event_rows = key_table_item.find_parent().find_parent().find_next_siblings()
        
        
        for item in event_rows:
            events.append(cls.__parseEventTableRow(item))
        
        return events
    
    # Returns dictionary with event data
    @classmethod
    def __parseEventTableRow(cls,soup):


        columns = {}
        
        children = soup.find_all('td',recursive=False)
        
        # Get link
        
        a_tag = children[0].find('a')
        if a_tag:
            columns["link"] = a_tag.get('href')
        else:
            columns["link"] = None

        
        # Get chairs
        columns["chairs"] = children[3].get_text(";",False).split(';')
        
        
        # Get title
        columns["name"] = children[4].contents[0]
        
        # Get event sessions
        session_links = [*map(lambda x :[x.get('href'),None] ,children[4].find_all('a'))]
        columns["session_data_links"] = session_links
        


        return columns
        

#Provides methods for extracting html content from CCSCC raw data pages
#Used for 2025 raw data pages
#Returns list with raw data rows, or none
class RawDataPageParser(RawDataPageParserBase):

    @classmethod
    def parseRawDataPageContent(cls,page_content):

        logger.info('Starting raw data page parse')
        rawPageData={
            'date':None,
            'entries': [
            #      {
            #       'class_abrv': str,
            #       'car_num': str,
            #       'driver_name': str,
            #       'car_model': str,
            #       'raw_time': str,
            #       },...
            ]
            }

        soup = BeautifulSoup(page_content,'html.parser')

        #Gets both tables
        tables = soup.find_all('tbody')

        page_headers = tables[0]
        entry_table = tables[1]

        #Get date
        main_header_text = page_headers.find_all('tr')[1].find('th').get_text()
        
        rawPageData['date'] = re.search('\\d\\d-\\d\\d-\\d\\d\\d\\d',main_header_text).group(0)

        logger.info(f'Found date: {rawPageData['date']}')

        
        entry_rows = entry_table.find_all('tr')

        #Pop row that has labels
        entry_rows.pop(0)

        for row in entry_rows:
            entry = {}

            entry_columns = row.find_all('td')

            columns = [*map(lambda x: x.get_text(), entry_columns)]

            entry['class_abrv'] = columns[2]
            entry['car_num'] = columns[3]
            entry['driver_name'] = columns[4]
            entry['car_model'] = columns[5]
            entry['raw_time'] = columns[6]

            logger.info(f'Found entry: {entry}')

            #Add entry to page entry list
            rawPageData['entries'].append(entry)

        return rawPageData
        
        
        

#Provides methods for extracting html content from CCSCC pax data pages
#Used for 2025 pax data pages
class PaxDataPageParser(PaxDataPageParserBase):
   
    @classmethod
    def parseRawDataPageContent(cls,page_content):
        logger.info('Starting PAX data page parse')
        paxPageData={
            'date':None,
            'entries': [
            #      {
            #       'class_abrv': str,
            #       'car_num': str,
            #       'driver_name': str,
            #       'car_model': str,
            #       'pax_factor': str,
            #       'pax_time' : str
            #       },...
            ]
            }

        soup = BeautifulSoup(page_content,'html.parser')

        #Gets both tables
        tables = soup.find_all('tbody')

        page_headers = tables[0]
        entry_table = tables[1]

        #Get date
        main_header_text = page_headers.find_all('tr')[1].find('th').get_text()
        
        paxPageData['date'] = re.search('\\d\\d-\\d\\d-\\d\\d\\d\\d',main_header_text).group(0)

        logger.info(f'Found date: {paxPageData['date']}')

        
        entry_rows = entry_table.find_all('tr')

        #Pop row that has labels
        entry_rows.pop(0)

        for row in entry_rows:
            entry = {}
            entry_columns = row.find_all('td')

            #Convert all columns to text
            columns = [*map(lambda x: x.get_text(), entry_columns)]

            entry['class_abrv'] = columns[2]
            entry['car_num'] = columns[3]
            entry['driver_name'] = columns[4]
            entry['car_model'] = columns[5]
            entry['pax_factor'] = columns[7][1:]
            entry['pax_time'] = columns[8]

            logger.info(f'Found entry: {entry}')

            #Add entry to page entry list
            paxPageData['entries'].append(entry)

        return paxPageData
    
#Provides methods for extracting html content from CCSCC final data pages
#Used for 2025 final pax data pages
class FinalDataPageParser(FinalDataPageParserBase):
    
    @classmethod
    def parseFinalDataPageContent(cls,page_content):
        logger.info('Starting final data page parse')
        finalPageData={
            'date':None,
        #   'class_entries': [
            #       {
            #       'race_class_abrv': str,
            #       'race_class_name': str,
            #       'entries: [
            #            {
            #             'class_abrv': str,
            #             'car_num': str,
            #             'driver_name': str,
            #             'car_model': str,
            #             'car_color': str,
            #             'has_trophy': bool,
            #             'runs': [
            #                       {
            #                        'time': str,
            #                        'isDNF':bool,
            #                        'numPenalties': bool,
            #                        }
            #                     ]
            #             },...
            #       },...
            #       ]
            #   ]
            }

        soup = BeautifulSoup(page_content,'html.parser')

        #Gets header and main table
        body = soup.find('body')

        page_headers = body.find('table',recursive=False).find('tbody',recursive=False)

        main_content_rows = body.find('a',recursive=False)   \
                            .find_all('table',recursive=False)[1]   \
                            .find('tbody',recursive=False)  \
                            .find_all('tr',recursive=False)


        #Get date
        main_header_text = page_headers.find_all('tr')[1].find('th').get_text()
        
        finalPageData['date'] = re.search('\\d\\d-\\d\\d-\\d\\d\\d\\d',main_header_text).group(0)

        logger.info(f'Found date: {finalPageData['date']}')


        #Process rows

        class_entries = {''}
        for row in main_content_rows:
            columns = row.find_all('th',recursive=False)
            for column in columns:
                logger.info(column.get_text())


        






        # for row in entry_rows:
        #     entry = {}
        #     entry_rows = row.find_all('td')

        #     columns = [*map(lambda x: x.get_text(), entry_rows)]

        #     entry['class_abrv'] = columns[2]
        #     entry['car_num'] = columns[3]
        #     entry['driver_name'] = columns[4]
        #     entry['car_model'] = columns[5]
        #     entry['pax_factor'] = columns[7][1:]
        #     entry['pax_time'] = columns[8]

        #     logger.info(f'Found entry: {entry}')

        #     #Add entry to page entry list
        #     paxPageData['entries'].append(entry)

        return finalPageData
    
    