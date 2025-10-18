#File for testing raw scraper

from Parser import RawDataPageParser



def main():

    content = ''
    with open('Scraping/2025Pages/SampleRaw.htm','r',encoding='utf-8') as file:
        content = file.read()


    data = RawDataPageParser.scrapeRawDataPageContent(content)


    return 1














if __name__ == '__main__':
    main()