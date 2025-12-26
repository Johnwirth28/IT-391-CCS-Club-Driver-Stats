from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

import logging

logger = logging.getLogger(__name__)



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
    def parsePaxDataPageContent(cls,page_content):
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

        event_page_dict = {'events':None}
        events = []

        key_table_item = soup.find("strong",string="Event",recursive=True)
        
        if key_table_item is None:
            logger.error('Failed to find first event')
            raise ValueError('Failed to find first event')
        
        event_rows = key_table_item.find_parent().find_parent().find_next_siblings()
        
        
        for item in event_rows:
            events.append(cls.__parseEventTableRow(item))
        
        event_page_dict['events']=events
        
        return event_page_dict
    
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
        session_links = [*map(lambda x : x.get('href'),children[4].find_all('a'))]
        columns["session_data_links"] = session_links
        


        return columns
        

#Provides methods for extracting html content from CCSCC raw data pages
#Used for 2025 raw data pages
#Returns list with raw data rows, or none
class RawDataPageParser(RawDataPageParserBase):

    @classmethod
    def parseRawDataPageContent(cls,page_content):

        logger.debug('Starting raw data page parse')
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

        date_text= re.search('\\d\\d-\\d\\d-\\d\\d\\d\\d',main_header_text).group(0)
        new_date = datetime.strptime(date_text,'%m-%d-%Y').strftime('%Y-%m-%d')

        rawPageData['date'] = new_date

        logger.debug(f'Found date: {rawPageData['date']}')

        
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

            logger.debug(f'Found entry: {entry}')

            #Add entry to page entry list
            rawPageData['entries'].append(entry)

        return rawPageData
        
        
        

#Provides methods for extracting html content from CCSCC pax data pages
#Used for 2025 pax data pages
class PaxDataPageParser(PaxDataPageParserBase):
   
    @classmethod
    def parsePaxDataPageContent(cls,page_content):
        logger.debug('Starting PAX data page parse')
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

        date_text= re.search('\\d\\d-\\d\\d-\\d\\d\\d\\d',main_header_text).group(0)
        new_date = datetime.strptime(date_text,'%m-%d-%Y').strftime('%Y-%m-%d')

        paxPageData['date'] = new_date

        logger.debug(f'Found date: {paxPageData['date']}')

        
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

            logger.debug(f'Found entry: {entry}')

            #Add entry to page entry list
            paxPageData['entries'].append(entry)

        return paxPageData
    
#Provides methods for extracting html content from CCSCC final data pages
#Used for 2025 final pax data pages
class FinalDataPageParser(FinalDataPageParserBase):
    
    @classmethod
    def parseFinalDataPageContent(cls,page_content):
        logger.debug('Starting final data page parse')
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
            #                        'num_penalties': bool,
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

        date_text= re.search('\\d\\d-\\d\\d-\\d\\d\\d\\d',main_header_text).group(0)
        new_date = datetime.strptime(date_text,'%m-%d-%Y').strftime('%Y-%m-%d')

        if new_date:
            finalPageData['date'] = new_date

        logger.debug(f'Found date: {finalPageData['date']}')


        #Process rows


        class_entries = []

        class_entry = {}

        max_run_num = len(main_content_rows[0].find_all('th',string=re.compile(r"^.*Run.*$")))

        for row in main_content_rows:

            children = row.find_all_next()
            is_header = children[0].name == 'th'

            if is_header:
                if class_entry:
                    class_entries.append(class_entry)
                    class_entry = {}

                header_info = children[0].get_text()
                logger.debug(f'Found header {header_info}')
                extracted_items = re.compile(r"^\s(\w*).*'(.+)'").match(header_info)
                class_entry['race_class_abrv'] = extracted_items.group(1)
                class_entry['race_class_name'] = extracted_items.group(2)
                class_entry['entries'] = []
                logger.debug(class_entry)

            else:

                race_entry = {}
                race_entry['runs'] = []
                for index, column in enumerate(children):
                    text = column.get_text()
                    match index:

                        case 0:
                            race_entry['has_trophy'] = True if re.search(r"T",text) else False
                        case 1:
                            race_entry['class_abrv'] = text
                        case 2:
                            race_entry['car_num'] = text
                        case 3:
                            race_entry['driver_name'] = text
                        case 4:
                            race_entry['car_model'] = text
                        case 5:
                            race_entry['car_color'] = text
                        case _:
                            run = {}
                            if text and index < max_run_num + 6:
                                logger.debug(f'Examing run text: \'{text}\'')
                                match = re.search(r"^.(?P<time>\d*.\d*)(\+((?P<dnf>DNF)|(?P<pen>\d)))?",text)
                                run['time'] = match.group('time')
                                run['isDNF'] = True if match.group('dnf') else False
                                penalties = match.group('pen')
                                run['num_penalties'] = penalties if penalties else 0
                                race_entry['runs'].append(run)
                                run = {}
                            else:
                                class_entry['entries'].append(race_entry)
                                race_entry = {}
                                race_entry['runs'] = []
                                break
                                
        finalPageData['class_entries'] = class_entries
        
                           
                

        return finalPageData
    
    