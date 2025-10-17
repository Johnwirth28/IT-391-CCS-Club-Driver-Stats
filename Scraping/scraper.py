import requests
from bs4 import BeautifulSoup
import pickle
from abc import ABC,abstractmethod
from random import randint
import time
from datetime import datetime
import sys
import logging

#Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename=datetime.now().strftime('logs/scraper%m.%d.%Y.%H.%M.%S.log'))

#Config

NEW_CALL = False



#-----------------Helper Funcs--------------#

#Saving soup
def saveSoup(soup, filename):
    with open(filename,'wb') as file:
        pickle.dump(soup,file)

#Loading soup        
def loadSoup(filename) -> BeautifulSoup:
    with open(filename,'rb') as file:
       return pickle.load(file)

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
    
    
    
#------------------Abstract Classes------------------------------------------#

#Provides methods for extracting html content from CCSCC events page
class eventPageParser(ABC):
    
    #Returns dictionary with event session pages or None
    @classmethod
    @abstractmethod
    def scrapeEventsPageContent(cls,soup:BeautifulSoup):
        raise NotImplementedError
    
    # Returns dictionary with event data or None
    @classmethod
    @abstractmethod
    def __scrapeEventTableRow(cls,soup:BeautifulSoup):
        raise NotImplementedError
   
   
#Provides methods for extracting html content from CCSCC raw data pages
class rawDataPageParser(ABC):
    
    @classmethod
    @abstractmethod
    def scrapeRawDataPageContent(cls,soup:BeautifulSoup):
        raise NotImplementedError

#Provides methods for extracting html content from CCSCC pax data pages
class paxDataPageParser(ABC):

    @classmethod
    @abstractmethod
    def scrapeRawDataPageContent(cls,soup:BeautifulSoup):
        raise NotImplementedError
    
#Provides methods for extracting html content from CCSCC final data pages
class finalDataPageParser(ABC):
    
    @classmethod
    @abstractmethod
    def scrapeFinalDataPageContent(cls,soup:BeautifulSoup):
        raise NotImplementedError
    
#Method for making requests
class Requestor(ABC):
    
    @abstractmethod
    def __init__(self,session, allowed_requests,interval,padding_factor):
        raise NotImplementedError
    
    #Makes requests to links and downloads html files to dir
    @abstractmethod
    def makeRequests(cls,links):
        raise NotImplementedError
    
#------------------Implementation Classes------------------------------------------#


#Method for making requests
class baseRequestor(Requestor):
    
    
    def __init__(self,session=None, allowed_requests=1000,interval_ms=1000,padding_factor=5):
        self.__allowed_requests = allowed_requests
        self.__interval_ms = interval_ms
        self.__padding_ms = round(interval_ms/padding_factor)
        self.__session = session
        self.__default_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
        } 
        
        if self.__session is None:
            self.__session = requests.sessions.Session()
            self.__session.headers.update(self.__default_headers)
            
        
        
    #Requests pages and returns list of dicts with link, status, and content
    #Uses set interval with padding factor in form of interval/padfactor for delaying commands
    #Returns list of dicts in form {'link':link, 'status_code':status_code,'content':content}
    def makeRequests(self,links):
        
        response_list = []

        num_links = len(links)
    
        index = 0

        while(index < num_links and self.__allowed_requests > 0):
            
            logger.info(f'link[{index}] request to {links[index]}')

            content = self.__getPage(links[index])
            
            logger.info(f'Response code: {content['status_code']}')

            response_list.append(content)
        
            if index != num_links-1:
                rand_padding = randint(-1*self.__padding_ms, self.__padding_ms)
                
                time.sleep((self.__interval_ms + rand_padding)/1000)
            
            self.__allowed_requests -= 1
            index+=1
    
        return response_list
    
    def makeRequest(self,link,delay=0):
        logger.info(f'Request to {link}')

        if(delay > 0):
            time.sleep(delay/1000)
            
        content = self.__getPage(link)
            
        logger.info(f'Response code: {content['status_code']}')

        self.__allowed_requests -= 1
        return content
    #Returns html page or None
    def __getPage(self,link):
        req = self.__session.get(link)
        dict = {}
        dict['link'] = link
        dict['status_code'] = req.status_code
        dict['content'] = req.text
        return dict
    
    def setSession(self,session):
        self.__session = session
    
    def getSession(self):
        return self.__session
        
    def setAllowedRequests(self,allowed_requests):
        self.__allowed_requests = allowed_requests
    
    def getAllowedRequests(self):
        return self.__allowed_requests
    
    def setInterval(self,interval_ms):
        self.__interval_ms = interval_ms
    
    def getInterval(self):
        return self.__interval_ms
    
    def setPadding(self,padding_factor):
        self.__padding = padding_factor
    
    def getPadding(self):
        return self.__padding
    

    

class sessionSoupRequestor(baseRequestor):
    
    def makeRequests(self, links):
        return super().makeRequests(links)
    
    
#Parser used for 2025 events schedule page
class baseEventPageParser(eventPageParser):

    #Returns dictionary with event session html
    @classmethod
    def scrapeEventsPageContent(cls,soup:BeautifulSoup):
        events = []
        
        key_table_item = soup.find("strong",string="Event",recursive=True)
        
        if key_table_item is None:
            print("Failed to find first event")
            exit(1)
        
        event_rows = key_table_item.find_parent().find_parent().find_next_siblings()
        
        
        for item in event_rows:
            events.append(cls.__scrapeEventTableRow(item))
        
        return events
    
    # Returns dictionary with event data
    @classmethod
    def __scrapeEventTableRow(cls,soup:BeautifulSoup):
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
class baseRawDataPageParser(rawDataPageParser):
   
    @classmethod
    def scrapeRawDataPageContent(cls,soup:BeautifulSoup):
        
        #Gets all rows
        rows = soup.find_all('tr')
        
        #Removes the heading row
        rows.pop(0)
        
        return rows.find_all('td')
        
        
        

#Provides methods for extracting html content from CCSCC pax data pages
#Used for 2025 pax data pages
class basePaxDataPageParser(ABC):
   
    @classmethod
    def scrapeRawDataPageContent(cls,soup:BeautifulSoup):
        pass
    
#Provides methods for extracting html content from CCSCC final data pages
#Used for 2025 final pax data pages
class baseFinalDataPageParser(ABC):
    
    @classmethod
    def scrapeFinalDataPageContent(cls,soup:BeautifulSoup):
        pass
    
    
    
    
    
    


#Workspace

def main():


    origin_url = 'https://ccsportscarclub.org/autocross/schedule/'
    
    
    requestor = baseRequestor(None,interval_ms=10000)
    
    origin_data = requestor.makeRequests([origin_url])

    if origin_data[0]['status_code'] != 200:
        print('Origin url request failed.\nExiting...')
        exit(1)

    origin_soup = BeautifulSoup(origin_data[0]['content'],'html.parser')
        
    origin_events = baseEventPageParser.scrapeEventsPageContent(origin_soup)

    for event in origin_events:
        for link_bundle in event['session_data_links']:
            response = requestor.makeRequest(link_bundle[0])
            if response['status_code'] == 200:
                link_bundle[1] = response['content']

    printEvents(origin_events)
    
    return 1
    



if __name__ == '__main__':
    main()
    

        
        


    


        



    









