#File for testing final data scraper

import os
from Parser import FinalDataPageParser
import json

SPECIAL_FILE = 'FinalPageUnusual.htm'
NORMAL_FILE = 'SampleFinal.htm'

DIR = 'Scraping/2025Pages/'

def main():

    content = ''
    with open(DIR + NORMAL_FILE,'r',encoding='utf-8') as file:
        content = file.read()

    result = FinalDataPageParser.parseFinalDataPageContent(content)

    print(json.dumps(result,indent=4,sort_keys=True))
    
    return 1














if __name__ == '__main__':
    main()