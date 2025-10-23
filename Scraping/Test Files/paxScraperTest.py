#File for testing pax scraper

import os
from Parser import PaxDataPageParser



def main():

    content = ''
    with open('Scraping/2025Pages/SamplePax.htm','r',encoding='utf-8') as file:
        content = file.read()

    PaxDataPageParser.scrapeRawDataPageContent(content)

    return 1




if __name__ == '__main__':
    main()