#File for testing event page scraper
import os
from Parser import EventPageParser

def main():

	print(os.getcwd())
	content = ''
	with open('Scraping/2025Pages/EventSchedule.html','r',encoding='utf-8') as file:
		content = file.read()
		
	print(EventPageParser.scrapeEventsPageContent(content))


	return 1







if __name__ == '__main__':
    main()