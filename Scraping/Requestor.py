import requests
from abc import ABC,abstractmethod
import logging
import datetime
import time
from random import randint

#Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


#Method for making requests
class RequestorBase(ABC):
    
    @abstractmethod
    def __init__(self,session, allowed_requests,interval,padding_factor):
        raise NotImplementedError
    
    #Makes requests to links and returns list of response dicts: 
    # [{'link': link, 'status_code':status_code, 'content': content},...]
    @abstractmethod
    def makeRequests(cls,links):
        raise NotImplementedError
    
    #Makes requests to links and returns list of response dict: 
    #Delay (ms) is used for delays if making multiple requests
    # {'link': link, 'status_code':status_code, 'content': content}
    @abstractmethod
    def makeRequest(cls,link,delay):
        raise NotImplementedError
    
#------------------Implementation Classes------------------------------------------#


#Method for making requests
class Requestor(RequestorBase):
    
    
    def __init__(self,session=None, allowed_requests=1000,interval_ms=2500,padding_factor=5):
        self.__allowed_requests = allowed_requests
        self.__interval_ms = interval_ms
        self.__padding_factor= padding_factor
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
                
                rand_delay = self.__getRandDelayInSeconds(self.__interval_ms,self.__padding_factor)
                time.sleep(rand_delay)
            
            self.__allowed_requests -= 1
            index+=1
    
        return response_list
    
    def makeRequest(self,link,delay=0):
        logger.info(f'Request to {link}')

        if(delay > 0):
            
            rand_delay = self.__getRandDelayInSeconds(delay,self.__padding_factor)
            time.sleep(rand_delay)

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
    
    def __getRandDelayInSeconds(self,duration_ms,padding_factor):
        padding_ms = round(duration_ms/padding_factor)
        return (duration_ms + randint(-1*padding_ms, padding_ms))/1000
    
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