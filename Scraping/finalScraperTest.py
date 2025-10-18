#File for testing final data scraper

import os
from Parser import FinalDataPageParser




def main():

    content = ''
    with open('Scraping/2025Pages/SampleFinal.htm','r',encoding='utf-8') as file:
        content = file.read()

    FinalDataPageParser.parseFinalDataPageContent(content)

    return 1














if __name__ == '__main__':
    main()