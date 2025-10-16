import requests
from bs4 import BeautifulSoup
import pickle
import re
import os
from abc import ABC,abstractmethod
from random import randint
import time


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

def printEvents(events, output_file):
    for item in events:
        print("Event {}:".format(events.index(item)),file=output_file)
        for key,value in item.items():
            if type(value) == list:
                print('{}:'.format(key),file=output_file)
                if len(value) != 0:
                    for i in value:
                        print('\t{}'.format(i),file=output_file)
                else:
                    print('No links found',file=output_file)
            else:
                print("{}: {}".format(key,value),file=output_file)
        print(file=output_file)
    
    
    
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
    
    
    def __init__(self,session=None, allowed_requests=100,interval=1,padding_factor=5):
        self.__allowed_requests = allowed_requests
        self.__interval = interval
        self.__padding = interval/padding_factor
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
    def makeRequests(self,links):
        
        response_list = []
    
        index = 0

        while(index < len(links) and self.__allowed_requests > 0):
            
            print(f'Making index:{index} request to {links[index]}')
            
            response_list.append(self.__getPage(links[index]))
            
            interval_ms = (self.__interval/1000)
            padding = interval_ms/self.__padding
            
            rand_padding = (padding*(-1),padding)
            
            time.sleep(interval_ms + padding)
            
            self.__allowed_requests -= 1
            index+=1
    
        return response_list
    
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
    
    def setInterval(self,interval):
        self.__interval = interval
    
    def getInterval(self):
        return self.__interval
    
    def setPadding(self,padding_factor):
        self.__padding = padding_factor
    
    def getPadding(self):
        return self.__padding
    

    

class sessionSoupRequestor(baseRequestor):
    
    def makeRequests(self, links):
        return super().makeRequests(links)
    
    
#Parser used for 2025 events schedule page
class baseEventPageParser(eventPageParser):

    #Returns dictionary with event session pages or None
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
    
    # Returns dictionary with event data or None
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
        session_links = [*map(lambda x :x.get('href') ,children[4].find_all('a'))]
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
        
        return rows
        
        
        

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
    os.chdir('CCC Autocross App')

    spfilename = 'sp.pkl'

    site_url = 'https://ccsportscarclub.org/autocross/schedule/'

    output_file = open('output_print.txt','w',encoding='utf-8')

    links_text = 'http://ccsportscarclub.org/files/2025/04/april-cross-saturday-04-26-2025_raw.htm,http://ccsportscarclub.org/files/2025/04/april-cross-saturday-04-26-2025_pax.htm,http://ccsportscarclub.org/files/2025/04/april-cross-saturday-04-26-2025_fin.htm,http://ccsportscarclub.org/files/2025/04/april-cross-sunday-04-27-2025_raw.htm,http://ccsportscarclub.org/files/2025/04/april-cross-sunday-04-27-2025_pax.htm,http://ccsportscarclub.org/files/2025/04/april-cross-sunday-04-27-2025_fin.htm'

    links = links_text.split(',')
        
    requestor = baseRequestor(None,interval=1000)
    
    responses = requestor.makeRequests(links)
    
    print('starting requests ')
    for item in responses:
        # for key,value in item.items():
        #     print(f'{key}: {value}')
        # print()
        print(item['status_code'])
        
    #Close output file
    output_file.close()
    
    return 1
    


if __name__ == '__main__':
    main()
    

        
        


    


        



    









